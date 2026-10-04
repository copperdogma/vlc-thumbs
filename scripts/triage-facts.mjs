#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildGraph, sectionRecords, sectionScalars } from "./methodology-graph.mjs";

const EXPECTED_LANES = [
  "triage",
  "triage-stories",
  "triage-inbox",
  "triage-evals",
  "triage-architecture",
  "triage-health",
  "loop-verify",
  "codebase-improvement-scout",
];

export function collectFacts(root = process.cwd()) {
  let graph = readJson(root, "docs/methodology/graph.json", {});
  const methodology = { graph_exists: existsSync(join(root, "docs/methodology/graph.json")), current: false, error: null };
  if (root === process.cwd()) {
    try {
      const expected = buildGraph();
      methodology.current = readText(root, "docs/methodology/graph.json") === expected;
      graph = JSON.parse(expected);
    } catch (error) { methodology.error = error.message; }
  }
  const stateText = readText(root, "docs/methodology/state.yaml");
  const categories = parseStateCategories(stateText);
  const evalRegistry = readText(root, "docs/evals/registry.yaml");

  return {
    project: graph.project || "vlc-thumbs",
    methodology,
    planning_inputs: sectionRecords(stateText, "planning_inputs").map((input) => ({ ...input, exists: Boolean(input.path && existsSync(join(root, input.path))) })),
    next_step: { story_id: sectionScalars(stateText, "active_focus").story_id || null, summary: sectionScalars(stateText, "active_focus").summary || null, source: "docs/methodology/state.yaml active_focus", executed: false },
    git: gitFacts(root),
    stories: storyFacts(graph),
    evals: evalFacts(graph, evalRegistry),
    state: stateFacts(stateText, categories),
    inbox: inboxFacts(root),
    health: healthFacts(root, stateText),
    lanes: laneFacts(root),
    wrappers: wrapperFacts(root),
    churn: churnFacts(root),
  };
}

export function renderText(facts) {
  const lines = [
    "Triage Facts",
    `- methodology graph: ${facts.methodology.current ? "current" : "missing/stale or invalid"}${facts.methodology.error ? ` (${facts.methodology.error})` : ""}`,
    `- next step: Story ${facts.next_step.story_id || "unset"}: ${facts.next_step.summary || "unset"}`,
    `- branch: ${facts.git.branch} @ ${facts.git.head}`,
    `- dirty: ${facts.git.dirty ? "yes" : "no"}`,
    `- stories: ${JSON.stringify(facts.stories.by_status)}`,
    `- open stories: ${facts.stories.open_count}${formatList(facts.stories.open_ids)}`,
    `- evals: ${JSON.stringify(facts.evals.by_status)}`,
    `- planned evals: ${facts.evals.planned_count}${formatList(facts.evals.planned_ids)}`,
    `- state substrate: ${JSON.stringify(facts.state.substrate_statuses)}; climb partial/deferred categories: ${facts.state.climb_pressure_count}${formatList(facts.state.climb_pressure_ids)}`,
    `- active focus: ${facts.state.active_focus.summary || "none"}`,
    `- inbox untriaged: ${facts.inbox.untriaged_count}`,
    `- ui/client scout: ${facts.health.ui_scout.status || "unknown"}${facts.health.ui_scout.reason ? ` (${facts.health.ui_scout.reason})` : ""}`,
    `- architecture audits: ${facts.health.architecture_audits.status || "unknown"}${facts.health.architecture_audits.reason ? ` (${facts.health.architecture_audits.reason})` : ""}`,
    `- codebase improvement: ${facts.health.codebase_improvement.status}`,
    `- lane presence: ${facts.lanes.present.length} present, ${facts.lanes.absent.length} absent${formatList(facts.lanes.absent)}`,
    `- skill surface drift: ${facts.wrappers.drift_count}`,
    `- recent churn: ${facts.churn.changed_file_count} files in last 20 commits; top dirs: ${formatTopDirs(facts.churn.top_dirs)}`,
  ];
  return `${lines.join("\n")}\n`;
}

function readText(root, relativePath) {
  const path = join(root, relativePath);
  return existsSync(path) ? readFileSync(path, "utf8") : "";
}

function readJson(root, relativePath, fallback) {
  const text = readText(root, relativePath);
  if (!text) return fallback;
  try {
    return JSON.parse(text);
  } catch {
    return fallback;
  }
}

function run(root, command, args) {
  try {
    return execFileSync(command, args, {
      cwd: root,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {
    return "";
  }
}

function gitFacts(root) {
  const status = run(root, "git", ["status", "--short", "--", "."]);
  return {
    branch: run(root, "git", ["rev-parse", "--abbrev-ref", "HEAD"]) || "unknown",
    head: run(root, "git", ["rev-parse", "--short", "HEAD"]) || "unknown",
    dirty: Boolean(status),
  };
}

function storyFacts(graph) {
  const stories = Array.isArray(graph.stories) ? graph.stories : [];
  const byStatus = countBy(stories.map((story) => story.status || "Unknown"));
  const open = stories.filter((story) => story.status !== "Done");
  return {
    total: stories.length,
    by_status: byStatus,
    open_count: open.length,
    open_ids: open.map((story) => story.id),
  };
}

function evalFacts(graph, registryText) {
  const evals = Array.isArray(graph.evals) ? graph.evals : [];
  const byStatus = countBy(evals.map((item) => item.status || "unknown"));
  const planned = evals.filter((item) => item.status === "planned" || /command:\s*"not implemented"/.test(evalBlock(registryText, item.id)));
  const implemented = evals.filter((item) => item.status === "implemented");
  return {
    total: evals.length,
    by_status: byStatus,
    implemented_count: implemented.length,
    run_by_facts: false,
    results_claim: "Registry declarations only; this facts command does not execute evals or establish fidelity.",
    planned_count: planned.length,
    planned_ids: planned.map((item) => item.id),
  };
}

function evalBlock(registryText, id) {
  if (!id) return "";
  const blocks = registryText.split(/\n(?=- id: )/);
  return blocks.find((block) => block.includes(`id: ${id}`) || block.includes(`id: "${id}"`)) || "";
}

function parseStateCategories(stateText) {
  return sectionRecords(stateText, "categories");
}

function stateFacts(stateText, categories) {
  const activeFocus = sectionScalars(stateText, "active_focus");
  const substrateStatuses = countBy(categories.map((category) => category.substrate_status || "unknown"));
  const climbPressure = categories.filter((category) => (
    category.phase === "climb" &&
    ["partial", "missing", "deferred", "unplanned"].includes(category.substrate_status)
  ));
  return {
    active_focus: activeFocus,
    category_count: categories.length,
    substrate_statuses: substrateStatuses,
    climb_pressure_count: climbPressure.length,
    climb_pressure_ids: climbPressure.map((category) => category.id),
  };
}

function inboxFacts(root) {
  const text = readText(root, "docs/inbox.md");
  if (!text || /No live items\./.test(text)) {
    return { path: "docs/inbox.md", untriaged_count: 0, sample: [] };
  }
  const items = text.split("\n")
    .filter((line) => /^[-*]\s+\S/.test(line.trim()) || /^[-*]\s+\[[ xX]\]\s+\S/.test(line.trim()))
    .map((line) => line.replace(/^[-*]\s+/, "").trim());
  return { path: "docs/inbox.md", untriaged_count: items.length, sample: items.slice(0, 10) };
}

function healthFacts(root, stateText) {
  const reportsDir = join(root, "docs/reports/codebase-improvement");
  const reports = existsSync(reportsDir)
    ? readdirSync(reportsDir).filter((name) => name.endsWith(".md")).sort()
    : [];
  const latestReport = reports.at(-1) || null;

  return {
    runtime: sectionScalars(stateText, "runtime"),
    eval_harness: sectionScalars(stateText, "eval_harness"),
    ui_scout: sectionScalars(stateText, "ui_scout"),
    architecture_audits: sectionScalars(stateText, "architecture_audits"),
    codebase_improvement: {
      ...sectionScalars(stateText, "codebase_improvement"),
      status: latestReport ? "present" : sectionScalars(stateText, "codebase_improvement").status || "absent",
      latest_report: latestReport ? `docs/reports/codebase-improvement/${latestReport}` : null,
    },
  };
}

function laneFacts(root) {
  const present = [];
  const absent = [];
  for (const lane of EXPECTED_LANES) {
    const path = join(root, ".agents/skills", lane, "SKILL.md");
    if (existsSync(path)) present.push(lane);
    else absent.push(lane);
  }
  return { expected: EXPECTED_LANES, present, absent };
}

function wrapperFacts(root) {
  const output = run(root, "bash", ["scripts/sync-agent-skills.sh", "--check"]);
  return {
    status: output ? "ok" : "drift",
    drift_count: output ? 0 : 1,
  };
}

function churnFacts(root) {
  const output = run(root, "git", ["log", "--name-only", "--format=", "--max-count=20"]);
  const files = [...new Set(output.split("\n").map((line) => line.trim()).filter(Boolean))];
  const topDirs = Object.entries(countBy(files.map((file) => file.split("/")[0] || file)))
    .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
    .slice(0, 5)
    .map(([dir, count]) => ({ dir, count }));
  return { changed_file_count: files.length, top_dirs: topDirs };
}


function countBy(values) {
  return values.reduce((acc, value) => {
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

function formatList(values) {
  if (!values || values.length === 0) return "";
  const shown = values.slice(0, 5).join(", ");
  return ` (${shown}${values.length > 5 ? ", ..." : ""})`;
}

function formatTopDirs(entries) {
  if (!entries || entries.length === 0) return "none";
  return entries.map((entry) => `${entry.dir}:${entry.count}`).join(", ");
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const facts = collectFacts();
  if (!process.argv.includes("--text")) {
    process.stdout.write(`${JSON.stringify(facts, null, 2)}\n`);
  } else {
    process.stdout.write(renderText(facts));
  }
}
