#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const mode = process.argv[2] || "build";
const root = process.cwd();

// Portable methodology tooling adapted for VLC timeline enhancements.

const paths = {
  ideal: join(root, "docs/ideal.md"),
  spec: join(root, "docs/spec.md"),
  state: join(root, "docs/methodology/state.yaml"),
  graph: join(root, "docs/methodology/graph.json"),
  storiesDir: join(root, "docs/stories"),
  storiesIndex: join(root, "docs/stories.md"),
  evalRegistry: join(root, "docs/evals/registry.yaml"),
};

function read(path) {
  return existsSync(path) ? readFileSync(path, "utf8") : "";
}

function ensureDir(path) {
  mkdirSync(path, { recursive: true });
}

function unique(values) {
  return [...new Set(values)].sort();
}

function extractRefs(text, prefix) {
  const re = new RegExp(`${prefix.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}:[a-z0-9.-]+`, "g");
  return unique(text.match(re) || []);
}

function idealRequirements() {
  const ideal = read(paths.ideal);
  const records = [];
  let current = null;
  for (const line of ideal.split("\n")) {
    const start = line.match(/^- \*\*(ideal:req:[a-z0-9-]+):\*\* (.+)$/);
    if (start) {
      current = { id: start[1], parts: [start[2]] };
      records.push(current);
      continue;
    }
    if (current && /^  \S/.test(line)) {
      current.parts.push(line.trim());
      continue;
    }
    if (current && (line.startsWith("## ") || line.trim() === "")) {
      current = null;
    }
  }
  return records.map((record) => ({
    id: record.id,
    text: record.parts.join(" ").replace(/\s+/g, " ").trim(),
  }));
}

function specCategories() {
  const spec = read(paths.spec);
  const matches = [...spec.matchAll(/^## (spec:\d+) - (.+)$/gm)];
  return matches.map((match, index) => {
    const start = match.index || 0;
    const end = index + 1 < matches.length ? matches[index + 1].index || spec.length : spec.length;
    const section = spec.slice(start, end);
    return {
      id: match[1],
      title: match[2].trim(),
      ideal_refs: extractRefs(section, "ideal:req"),
    };
  });
}

function parseFrontmatter(text) {
  if (!text.startsWith("---\n")) return {};
  const end = text.indexOf("\n---", 4);
  if (end === -1) return {};
  const fm = text.slice(4, end).split("\n");
  const out = {};
  let currentKey = null;
  for (const line of fm) {
    const keyVal = line.match(/^([a-zA-Z0-9_-]+):\s*(.*)$/);
    if (keyVal) {
      currentKey = keyVal[1];
      const raw = keyVal[2].trim();
      out[currentKey] = raw === "" ? [] : scalar(raw);
      continue;
    }
    const item = line.match(/^\s*-\s*"?([^"]+)"?\s*$/);
    if (item && currentKey) {
      if (!Array.isArray(out[currentKey])) out[currentKey] = [];
      out[currentKey].push(scalar(item[1]));
    }
  }
  return out;
}

function stories() {
  if (!existsSync(paths.storiesDir)) return [];
  return readdirSync(paths.storiesDir)
    .filter((name) => /^story-\d+-.+\.md$/.test(name))
    .sort()
    .map((name) => {
      const path = join(paths.storiesDir, name);
      const text = read(path);
      const fm = parseFrontmatter(text);
      const title = (text.match(/^# (.+)$/m) || [null, name])[1];
      return {
        id: String(fm.id || (name.match(/^story-(\d+)/) || [null, ""])[1]),
        title,
        status: String(fm.status || "Draft"),
        priority: String(fm.priority || "Medium"),
        path: `docs/stories/${name}`,
        ideal_refs: Array.isArray(fm.ideal_refs) ? fm.ideal_refs : [],
        spec_refs: Array.isArray(fm.spec_refs) ? fm.spec_refs : [],
        depends_on: Array.isArray(fm.depends_on) ? fm.depends_on : [],
        decision_refs: Array.isArray(fm.decision_refs) ? fm.decision_refs : [],
        eval_refs: Array.isArray(fm.eval_refs) ? fm.eval_refs : [],
      };
    });
}

function evals() {
  const registry = read(paths.evalRegistry);
  const blocks = registry.split(/\n(?=- id: )/).filter((block) => block.trim().startsWith("- id: "));
  return blocks.map((block) => ({
    id: (block.match(/^- id:\s*"?([^"\n]+)"?/m) || [null, ""])[1],
    name: (block.match(/^\s*name:\s*"?([^"\n]+)"?/m) || [null, ""])[1],
    type: (block.match(/^\s*type:\s*"?([^"\n]+)"?/m) || [null, ""])[1],
    status: (block.match(/^\s*status:\s*"?([^"\n]+)"?/m) || [null, ""])[1],
    spec_refs: extractRefs(block, "spec"),
    ideal_refs: extractRefs(block, "ideal:req"),
    command: (block.match(/^\s*command:\s*"?([^"\n]+)"?/m) || [null, ""])[1],
    parent_id: (block.match(/^\s*parent_id:\s*"?([^"\n]+)"?/m) || [null, ""])[1],
  }));
}

export function sectionScalars(state, name) {
  const lines = state.split("\n");
  const result = {};
  let active = false;
  for (const line of lines) {
    if (line === `${name}:`) { active = true; continue; }
    if (active && /^\S/.test(line) && !line.startsWith("#")) break;
    if (!active) continue;
    const match = line.match(/^  ([a-zA-Z0-9_]+):\s*(.*)$/);
    if (match) result[match[1]] = scalar(match[2]);
  }
  return result;
}

// Deliberately supports the portable package's scalar/inline-list YAML subset,
// not arbitrary YAML. Keep lists of IDs inline in state.yaml.
function scalar(value) {
  const clean = value.trim();
  if (clean.startsWith("[") && clean.endsWith("]")) return clean.slice(1, -1).split(",").map((item) => scalar(item)).filter(Boolean);
  return clean.replace(/^['"]|['"]$/g, "");
}

export function sectionRecords(state, name) {
  const records = [];
  let active = false;
  let current;
  for (const line of state.split("\n")) {
    if (line === `${name}:`) { active = true; continue; }
    if (active && /^\S/.test(line) && !line.startsWith("#")) break;
    if (!active) continue;
    const start = line.match(/^  - ([a-zA-Z0-9_]+):\s*(.*)$/);
    if (start) { current = { [start[1]]: scalar(start[2]) }; records.push(current); continue; }
    const field = line.match(/^    ([a-zA-Z0-9_]+):\s*(.*)$/);
    if (field && current) current[field[1]] = scalar(field[2]);
  }
  return records;
}

function stateSummary() {
  const state = read(paths.state);
  return {
    exists: Boolean(state),
    active_focus: sectionScalars(state, "active_focus"),
    categories: sectionRecords(state, "categories"),
    planning_inputs: sectionRecords(state, "planning_inputs"),
    lanes: Object.fromEntries(["runtime", "eval_harness", "ui_scout", "architecture_audits", "codebase_improvement"].map((name) => [name, sectionScalars(state, name)])),
  };
}

function renderStoriesIndex(storyRecords) {
  const rows = storyRecords.map((story) => (
    `| ${story.id} | ${story.title.replace(/^Story \d+ - /, "")} | ${story.status} | ${story.priority} | ${story.spec_refs.join(", ")} | ${story.depends_on.join(", ") || "-"} |`
  ));
  return [
    "# Stories",
    "",
    "> Generated by `make methodology-compile`. Edit files in `docs/stories/`, not this index.",
    "",
    "| ID | Title | Status | Priority | Spec refs | Depends on |",
    "|---|---|---|---|---|---|",
    ...rows,
    "",
  ].join("\n");
}

export function buildGraph() {
  const graph = {
    project: "vlc-thumbs",
    ideal_requirements: idealRequirements(),
    spec_categories: specCategories(),
    stories: stories(),
    evals: evals(),
    state: stateSummary(),
  };
  validateGraph(graph);
  return `${JSON.stringify(graph, null, 2)}\n`;
}

function validateGraph(graph) {
  const fail = (message) => { throw new Error(message); };
  for (const name of ["ideal", "spec", "state", "evalRegistry"]) {
    if (!read(paths[name]).trim()) fail(`Missing or empty required source: ${paths[name]}`);
  }
  if (!graph.ideal_requirements.length) fail("No labeled ideal:req requirements found");
  if (!graph.spec_categories.length) fail("No spec:N categories found");
  for (const [name, records] of Object.entries({ ideals: graph.ideal_requirements, specs: graph.spec_categories, stories: graph.stories, evals: graph.evals, categories: graph.state.categories })) {
    const ids = records.map((record) => record.id);
    if (ids.some((id) => !id) || new Set(ids).size !== ids.length) fail(`Missing or duplicate IDs in ${name}`);
  }
  const known = {
    ideal_refs: new Set(graph.ideal_requirements.map((record) => record.id)),
    spec_refs: new Set(graph.spec_categories.map((record) => record.id)),
    depends_on: new Set(graph.stories.map((record) => record.id)),
    story_refs: new Set(graph.stories.map((record) => record.id)),
    eval_refs: new Set(graph.evals.map((record) => record.id)),
  };
  for (const record of [...graph.spec_categories, ...graph.stories, ...graph.evals, ...graph.state.categories]) {
    for (const [field, ids] of Object.entries(known)) {
      for (const id of record[field] || []) if (!ids.has(id)) fail(`${record.id}: unknown ${field} reference ${id}`);
    }
  }
  for (const category of graph.state.categories) if (!known.spec_refs.has(category.id)) fail(`Unknown state category ${category.id}`);
  for (const spec of graph.spec_categories) if (!graph.state.categories.some((category) => category.id === spec.id)) fail(`Missing state category ${spec.id}`);
  const focus = graph.state.active_focus.story_id;
  if (focus && !known.story_refs.has(focus)) fail(`Unknown active-focus story ${focus}`);
  for (const evalRecord of graph.evals) {
    if (evalRecord.parent_id && !known.eval_refs.has(evalRecord.parent_id)) fail(`Unknown eval parent ${evalRecord.parent_id}`);
  }
  for (const input of graph.state.planning_inputs) {
    if (!input.path || !existsSync(join(root, input.path))) fail(`Missing planning input ${input.path || "path"}`);
  }
}

function build() {
  ensureDir(dirname(paths.graph));
  ensureDir(dirname(paths.storiesIndex));
  const graph = buildGraph();
  writeFileSync(paths.graph, graph);
  writeFileSync(paths.storiesIndex, renderStoriesIndex(stories()));
  console.log("methodology-compile: OK");
}

function check() {
  const expectedGraph = buildGraph();
  const actualGraph = read(paths.graph);
  if (actualGraph !== expectedGraph) {
    console.error("methodology-check: docs/methodology/graph.json is stale");
    process.exit(1);
  }
  const expectedStories = renderStoriesIndex(stories());
  const actualStories = read(paths.storiesIndex);
  if (actualStories !== expectedStories) {
    console.error("methodology-check: docs/stories.md is stale");
    process.exit(1);
  }
  console.log("methodology-check: OK");
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  try {
    if (mode === "build" || mode === "compile") build();
    else if (mode === "check") check();
    else throw new Error(`Unknown mode: ${mode}`);
  } catch (error) {
    console.error(`methodology-${mode}: ${error.message}`);
    process.exitCode = 1;
  }
}
