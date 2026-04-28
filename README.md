# skills

skarl86's personal collection of [Claude Code](https://claude.com/claude-code) skills, packaged as a plugin.

## Install

Add this repo as a marketplace, then install the plugin:

```
/plugin marketplace add skarl86/skills
/plugin install skills
```

After installing, the bundled skills become available to Claude Code in your sessions.

## Skills

### [github-direnv](skills/github-direnv/SKILL.md)

Folder-scoped GitHub authentication via direnv. When you `cd` into a configured directory, `GH_TOKEN` is auto-populated for a specific `gh` account, so `gh` and `git push/pull` use that account — without globally switching the active gh account or affecting other terminals/IDEs.

**Use when:** you have multiple `gh auth` accounts (personal/work/org) and keep hitting `Repository not found` errors after pushing from the wrong folder.

### [claude-session-to-md](skills/claude-session-to-md/README.md)

Convert Claude Code session jsonl logs (`~/.claude/projects/`, `~/.claude-envs/*/projects/`) into readable per-session markdown files. Includes subagent (Task tool) child conversations, idempotent re-runs, and noise filtering.

**Use when:** you want to accumulate Claude Code history in an Obsidian vault, back up sessions before clearing, or sync conversations across machines.

Benchmarked against Claude rolling its own converter from scratch (3-eval suite — single source, multi-source labels, subagent grouping):

| Metric | with skill | baseline | delta |
|---|---:|---:|---:|
| Pass rate | **94.4%** | 72.2% | **+22.2 pp** |
| Time | **28 s** | 123 s | **4.4× faster** |
| Tokens | **17.6 k** | 33.1 k | **−47%** |

Wins on every axis: the baseline writes its own header format instead of YAML frontmatter (breaks dataview / parsers), and flattens subagents next to parents with `__` filename joins (loses navigability).

---

More skills will be added over time.

## Layout

```
.
├── .claude-plugin/
│   ├── plugin.json        # plugin manifest
│   └── marketplace.json   # marketplace listing
└── skills/
    └── <skill-name>/
        ├── SKILL.md       # what Claude reads
        ├── README.md      # human-facing docs (some skills)
        └── scripts/       # bundled helpers (some skills)
```

## License

MIT
