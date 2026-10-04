.PHONY: methodology-compile methodology-check skills-sync skills-check scaffold-check triage-facts validate

methodology-compile:
	node scripts/methodology-graph.mjs compile

methodology-check:
	node scripts/methodology-graph.mjs check

skills-sync:
	bash scripts/sync-agent-skills.sh

skills-check:
	bash scripts/sync-agent-skills.sh --check

scaffold-check:
	node scripts/check-scaffold.mjs

triage-facts:
	@node scripts/triage-facts.mjs --json

validate: methodology-check skills-check scaffold-check
