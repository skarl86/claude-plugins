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
/plugin install ralph-bootstrap
/plugin install markdown-to-slides
/plugin install assemble-team
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

### [ralph-bootstrap](plugins/ralph-bootstrap)

Bootstrap a [Ralph loop](https://ghuntley.com/ralph/) scaffold from a one-sentence goal. Creates `specs/` (overview / architecture / constraints), priority-ordered `TODO.md`, fixed-prompt `PROMPT.md`, plus append-only `decisions.md` / `progress.md` — the seven state files needed to run Claude in a `while`-loop until `ALL DONE`.

**Use when:** you have a vague but non-trivial goal and want Claude to grind on it autonomously across many iterations, instead of micromanaging each step. Ambiguity becomes `[ASSUMPTION]` markers in the specs (greppable), not interview questions.

`PROMPT.md` declares **two activation modes** — wrapper script (fresh Claude per iteration) and in-session (current Claude becomes the loop body) — and explicitly forbids phase-boundary check-ins like "P0 done, continue with P1?", so the loop doesn't stall at natural seams.

### [markdown-to-slides](plugins/markdown-to-slides)

Turn a markdown file into a 1920×1080 presentation deck — single stacked HTML plus per-slide Retina PNGs (3840×2160) — via Playwright. Splits on `---` horizontal rules first, then `##`/`#` headings, with table- and diagram-aware layouts and a light theme tuned for conference-room projectors.

**Use when:** you've written something in markdown and want to present or share it without round-tripping through Keynote/PowerPoint, or you need static slide images for a blog post / async share.

Output drops into `<input-stem>-slides/` next to the source — `index.html` (full deck stacked vertically) plus `slide-01.png … slide-NN.png`. No PowerPoint required; PNG-on-projector is more reliable than `.pptx` font fallbacks anyway.

### [assemble-team](plugins/assemble-team)

5-layer harness (Entry → Routing → Enrichment → Verification → Handoff) that converts a user-provided plan into a safely spawned Claude Code agent team. Universal — works with any monorepo.

**Use when:** you have a plan with multiple parallelizable tasks across different scopes and you want to spawn a coordinated agent team with explicit ambiguity-resolution, role-mapping justification, and user approval before any teammate is created.

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
