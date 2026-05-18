# assemble-team

A Claude Code plugin that converts a user-provided plan into a safely spawned agent team via a 5-layer harness. Universal — works with any monorepo.

## Install

```
/plugin marketplace add skarl86/claude-plugins
/plugin install assemble-team
```

## What it does

`assemble-team` runs the lead Claude through five layers before any agent team is created:

| Layer | Responsibility |
|---|---|
| **L1 Entry** | Accept the invocation and resolve the plan body (file path, pasted body, or URL) |
| **L2 Routing** | Classify the plan along Intent × Complexity axes and select which tools to use in L3 |
| **L3 Enrichment** | Score ambiguity across 5 dimensions; grill the user in dependency order to fill gaps; prefer codebase exploration over user interrogation |
| **L4 Verification** | Present team mapping with source-tagged justifications; obtain explicit user approval (skip not allowed) |
| **L5 Handoff** | Call `TeamCreate` with role bodies and common guards inline-injected; monitor; optionally run a gated PR-create flow |

The intent classification, ambiguity scoring, and approval gate are adapted from patterns observed in `oh-my-openagent` (Prometheus) and `oh-my-claudecode` (plan / deep-interview / ralplan).

## When to use

- The user provides a plan with multiple parallelizable tasks across different scopes.
- The plan covers 3+ teammates' worth of work.
- The user explicitly asks to spawn an agent team.

## When NOT to use

- Single-task work — use a single subagent.
- Strongly sequential work — no parallel benefit.
- Multiple workers would edit the same file — conflict risk.

## Files

- `skills/assemble-team/SKILL.md` — main workflow (L1-L5)
- `skills/assemble-team/ROLES.md` — 6 mandatory + 2 optional generic roles + Plan→Role heuristic + common guards
- `skills/assemble-team/GRILL_PLAN.md` — ambiguity score + 7-step grilling
- `skills/assemble-team/PLAN_TEMPLATE.md` — universal plan template + example

## Requirements

- Claude Code v2.1.32+ with agent-teams capability enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
- `teammateMode: "tmux"` in `~/.claude/settings.json` for split-pane teammates
- `gh` CLI (only when using the optional `automation: pr-create` flow)

## License

MIT. See repository root.
