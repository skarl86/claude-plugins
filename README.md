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

| Skill | What it does |
|---|---|
| [github-direnv](skills/github-direnv/SKILL.md) | Sets up direnv-based folder-scoped GitHub authentication so `gh` and `git` automatically use a specific GitHub account when working inside that directory |

More skills will be added over time.

## Layout

```
.
├── .claude-plugin/
│   ├── plugin.json        # plugin manifest
│   └── marketplace.json   # marketplace listing
└── skills/
    └── <skill-name>/
        └── SKILL.md
```

## License

MIT
