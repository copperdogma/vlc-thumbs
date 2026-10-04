#!/usr/bin/env node
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';
import { buildGraph } from './methodology-graph.mjs';

const root = process.cwd();
const fail = message => { throw new Error(message); };
const read = path => readFileSync(join(root, path), 'utf8');
const graph = JSON.parse(buildGraph());
const required = ['AGENTS.md', 'README.md', 'docs/idea-intake.md', 'docs/plan.md',
  'docs/setup-checklist.md', 'docs/methodology-ideal-spec-compromise.md',
  'docs/runbooks/setup-methodology.md', 'docs/runbooks/skills.md',
  'docs/runbooks/triage.md', 'docs/runbooks/build-story.md', 'docs/decisions/README.md',
  'docs/evals/README.md', 'docs/evals/attempt-template.md',
  'tests/fixtures/golden/README.md', 'docs/research/scout.md'];
for (const path of required) if (!existsSync(join(root, path)) || !read(path).trim()) fail(`Missing/empty ${path}`);
const manifest = JSON.parse(read('docs/evidence/workflow-skill-sources.json'));
const actualSkills = readdirSync(join(root, '.agents/skills')).filter(name => existsSync(join(root, '.agents/skills', name, 'SKILL.md'))).sort();
const recordedSkills = manifest.skills.map(skill => skill.name).sort();
if (JSON.stringify(actualSkills) !== JSON.stringify(recordedSkills)) fail('Skill inventory differs from manifest');
for (const entry of [...manifest.skills.flatMap(skill => skill.files), ...manifest.tooling]) {
  const path = join(root, entry.path);
  if (!existsSync(path)) fail(`Missing imported file ${entry.path}`);
  const hash = createHash('sha256').update(readFileSync(path)).digest('hex');
  if (hash !== entry.sha256) fail(`Imported source drift: ${entry.path}; review and update provenance for deliberate edits`);
}
for (const entry of graph.evals) {
  const registry = read('docs/evals/registry.yaml');
  const block = registry.split(/\n(?=- id: )/).find(text => text.startsWith(`- id: ${entry.id}\n`));
  const contract = block?.match(/^  contract: (.+)$/m)?.[1];
  if (!contract || !existsSync(join(root, contract))) fail(`Missing eval contract: ${entry.id}`);
  if (entry.status === 'deferred' && (!/^  defer_reason: .+/m.test(block) || !/^  trigger: .+/m.test(block))) fail(`Deferred eval needs reason/trigger: ${entry.id}`);
}
for (const [name, lane] of Object.entries(graph.state.lanes)) {
  if (lane.status === 'deferred' && (!lane.reason || !lane.trigger)) fail(`Deferred lane needs reason/trigger: ${name}`);
}
if (graph.project !== 'vlc-thumbs') fail('Wrong project identity');
if (resolve(execFileSync('git', ['rev-parse', '--show-toplevel'], { cwd: root, encoding: 'utf8' }).trim()) !== resolve(root)) fail('Independent local Git repository or worktree missing');
console.log(`scaffold-check: OK (${actualSkills.length} sourced skills; contracts and deferred lanes valid)`);
