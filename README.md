# claude-plugins

skarl86's personal collection of [Claude Code](https://claude.com/claude-code) plugins.

Each plugin is independently installable, so you can pick only the ones you want instead of pulling everything in.

## Install

Add the marketplace once:

```
/plugin marketplace add skarl86/claude-plugins
```

Then install whichever plugin(s) you need:

```
/plugin install github-direnv
/plugin install claude-session-to-md
/plugin install blog-illustrate
```

## Plugins

### [github-direnv](plugins/github-direnv)

Folder-scoped GitHub authentication via direnv. When you `cd` into a configured directory, `GH_TOKEN` is auto-populated for a specific `gh` account, so `gh` and `git push/pull` use that account — without globally switching the active gh account or affecting other terminals/IDEs.

**Use when:** you have multiple `gh auth` accounts (personal/work/org) and keep hitting `Repository not found` errors after pushing from the wrong folder.

### [claude-session-to-md](plugins/claude-session-to-md)

Convert Claude Code session jsonl logs (`~/.claude/projects/`, `~/.claude-envs/*/projects/`) into readable per-session markdown files. Includes subagent (Task tool) child conversations, idempotent re-runs, and noise filtering.

**Use when:** you want to accumulate Claude Code history in an Obsidian vault, back up sessions before clearing, or sync conversations across machines.

Benchmarked against Claude rolling its own converter from scratch (3-eval suite — single source, multi-source labels, subagent grouping):

| Metric | with skill | baseline | delta |
|---|---:|---:|---:|
| Pass rate | **94.4%** | 72.2% | **+22.2 pp** |
| Time | **28 s** | 123 s | **4.4× faster** |
| Tokens | **17.6 k** | 33.1 k | **−47%** |

Wins on every axis: the baseline writes its own header format instead of YAML frontmatter (breaks dataview / parsers), and flattens subagents next to parents with `__` filename joins (loses navigability).

### [blog-illustrate](plugins/blog-illustrate)

Generate clean illustrations for blog posts when you don't have screenshots — or when the originals leak internal identifiers. HTML/CSS templates (terminal mockups, decision trees, comparison cards, mapping diagrams, layered defense) rendered to PNG via Playwright, uploaded to a blog MCP, and inserted into the post body as image references. All values stay as pseudonyms.

**Use when:** reviewing a text-only draft and wondering "where would a diagram help?", or when original screenshots have PII / internal paths that can't be published as-is.

Bundles 6 ready-to-edit templates with a unified Dracula-inspired dark theme + macOS terminal chrome, so a series of posts shares the same visual tone.

---

More plugins will be added over time.

## Layout

```
.
├── .claude-plugin/
│   └── marketplace.json        # marketplace listing — points at each plugin
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json     # plugin manifest
        └── skills/
            └── <skill-name>/
                ├── SKILL.md    # what Claude reads
                ├── README.md   # human-facing docs (some skills)
                └── scripts/    # bundled helpers (some skills)
```

## License

MIT
