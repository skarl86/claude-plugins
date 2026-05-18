---
name: assemble-team
description: |
  Convert a user plan into a safely spawned Claude Code agent team via a 5-layer
  harness (L1 Entry → L2 Routing → L3 Enrichment → L4 Verification → L5 Handoff).
  Lead reads the plan, classifies its intent and complexity, fills gaps via
  grilling, gets user approval, then spawns the team with role bodies and
  domain guards injected.

  Trigger when the user says:
  - "이 plan으로 팀 만들어줘" / "팀 에이전트로 돌려" / "team agents on this"
  - "assemble a team for this plan"
  - "use the assemble-team skill on this plan"
  - pastes a plan body and asks to parallelize

  Do NOT use this skill for:
  - single-task work (use a normal subagent)
  - strongly sequential work (no parallel benefit)
  - tasks where multiple workers would edit the same file (conflict)

  Note: detached-tmux-session delegation is intentionally out of scope for
  this release. A future companion plugin may add that capability.
---

# assemble-team

A 5-layer harness for converting a plan into a Claude Code agent team. The harness ensures the lead does not skip ambiguity resolution, mapping justification, or user approval before spawning teammates.

The 5 layers, in order:

1. **L1 Entry** — accept or block the invocation; coerce ambiguous execution requests into plan mode.
2. **L2 Routing** — classify the plan (intent × complexity) and select which tools the lead will use to fill gaps.
3. **L3 Enrichment** — fill the gaps via ambiguity scoring + grilling + codebase exploration; produce a plan complete enough to spawn against.
4. **L4 Verification** — present the team mapping and ambiguity summary to the user; obtain explicit approval. Skip is not allowed.
5. **L5 Handoff** — call `TeamCreate` with role bodies and domain guards injected; monitor; report.

## L1 · Entry Layer

The entry layer decides whether to enter the harness at all and, if so, with what plan body.

### Triggers

- Natural language: "이 plan으로 팀 만들어줘", "팀 에이전트로 돌려", "team agents on this plan", "assemble a team", "use the assemble-team skill on this plan"
- Pasted plan body + "process this in parallel" / "이거 병렬로 처리해"
- (Slash-command invocation and a sibling `delegate-team` skill for detached tmux sessions are intentionally out of scope for this release.)

### Plan loading

1. If the user provided a file path, `Read` it.
2. If the user pasted the plan body inline, use it directly.
3. If the body is a single URL (GitHub issue / PR / external page):
   - Parse the URL into `owner`, `repo`, and `number`. For `https://github.com/<owner>/<repo>/issues/<num>` or `.../pull/<num>`, extract all three explicitly. Do not assume the current working directory's repo.
   - Fetch with the appropriate tool, passing `--repo <owner>/<repo>` so `gh` does not fall back to the current repo:
     - GitHub issue: `gh issue view <num> --repo <owner>/<repo> --json title,body,comments`
     - GitHub PR: `gh pr view <num> --repo <owner>/<repo> --json title,body,comments`
     - Generic URL: `WebFetch`
   - Expand into the plan body under a `## (original URL)` header.
   - Re-score ambiguity after expansion.
   - On fetch failure, fall back to grilling (ask the user for Goal / Scope / Tasks directly).
4. If the body contains both prose and URLs, treat the prose as authoritative and URLs as references the lead may fetch on demand.

### Pre-gate (block invalid invocations)

- No plan + no slash arg + no pasted body → respond with `PLAN_TEMPLATE.md` excerpt and ask the user to provide a plan.
- Plan body shorter than ~40 characters or no nouns → treat as invalid; ask user to expand.

### Detached-tmux-session delegation (out of scope)

If the user explicitly asks to isolate the new lead in a separate tmux session (so the working window is not split), explain that this release does not package that capability. Recommend running this skill in a dedicated terminal window instead. A future companion plugin may add the detached-session flow.

## L2 · Routing Layer

The routing layer classifies the plan and decides what tools the lead will use in L3. Classification is mandatory — every plan is classified before enrichment.

### Axis 1 — Intent (signal-based heuristic)

Read `ROLES.md` for the canonical role catalog. Classify the plan's primary intent using the keyword signals in `ROLES.md`. Categories:

- **Trivial** — single-file change, obvious fix
- **Refactor** — restructure existing code, preserve behavior
- **Build** — net-new code or feature
- **Mid-sized** — bounded feature with explicit deliverables
- **Collaborative** — user wants dialogue / iteration
- **Architecture** — system design, infrastructure choice
- **Research** — investigation with unclear path

### Axis 2 — Complexity (file count + impact heuristic)

- **Trivial** — single file, < 10 LoC, no dependency impact
- **Simple** — 1-2 files, scoped, < 30 min equivalent
- **Complex** — 3+ files OR architectural impact

### Routing decisions

Use the (Intent × Complexity) tuple to set:

| Decision | Default by tuple |
|---|---|
| Pre-L4 exploration done by the lead itself | Trivial → none; Build / Architecture → the lead runs `Glob` / `Read` / `Grep` to map existing patterns and cite paths in the L4 mapping; Research → the lead does local read-only scans with distinct exit criteria per probe and includes findings in the L4 ambiguity summary |
| Grilling depth | Trivial → only forced-block items; Simple → only failing dimensions; Complex → full ambiguity walkthrough |
| Required role in the L4 team mapping | Architecture → include an `architect` teammate card so it surfaces dependency / ordering issues during execution; when sanity review is critical also include a `reviewer` card. Research-heavy plans → include `researcher` teammate card(s). All such roles enter the team only after the user approves the L4 mapping. |
| Interview tone | Trivial → "I see X, also do Y?" / Architecture → "what lifespan, what scale?" |

**Spawn discipline (core safety guarantee).** The lead MUST NOT call `TeamCreate` or otherwise spawn any teammate before L4 user approval. All exploration before approval is local, read-only, and performed by the lead itself using `Glob` / `Read` / `Grep`. Any `researcher` / `architect` / `reviewer` work that requires a teammate is scheduled into the L4 mapping and executed only after approval in L5.

All role names referenced in this table MUST be present in the `ROLES.md` catalog. Do NOT invent role names or refer to external subagents (such as `explore`, `critic`) that the package does not bundle.

The mapping is a natural-language rulebook in `ROLES.md`, not a hardcoded function. The lead reads the rulebook each invocation.

## L3 · Enrichment Layer

Fill the gaps until the plan is concrete enough to spawn against. Read `GRILL_PLAN.md` for the procedure and dependency order.

### Order of operations

1. Score ambiguity across 5 dimensions (Goal / Scope / Tasks / Constraints / DoD).
2. If `Ambiguity ≤ 0.30` and no forced-block trigger, skip grilling; proceed to L4.
3. Otherwise enter grilling: one question at a time, recommendation provided, dependency order Why → Scope → Tasks → Constraints → DoD → Out-of-scope → Risks.
4. Prefer codebase exploration (`Glob` / `Read` / `Grep`) over asking the user when the answer is discoverable.
5. Attach a source tag (`[from-user]` / `[from-code: path:line]` / `[guess]`) to every filled field.

### Forced-block heuristics (binary — block even with passing score)

- `Goal` missing
- `Tasks` count == 0
- `Constraints` missing AND plan contains destructive signals (migration / drop / force-push)

### Output of L3

A "complete plan summary" markdown block with source-tagged fields for each dimension. Any `[guess]` field is flagged for explicit user check in L4.

## L4 · Verification Layer

Present the team mapping and obtain user approval. Skip is not allowed.

### Mapping derivation

Using the plan and the `ROLES.md` heuristic table, derive teammate cards. Each card includes:

- name (single word, predictable: `frontend`, `backend`, `qa`, ...)
- role (one entry from the `ROLES.md` catalog)
- task (one paragraph extracted from the plan)
- owned files (directory / glob list)
- source justification (`[from-user]` / `[from-code: path:line]` / `[guess]`) per decision
- model (role default unless plan overrides)
- permission (role default; e.g. reviewer is read-only)
- plan-approval mode (ON for code/DB/destructive tasks)

### Team size

3 to 5 teammates. If two are needed for the same role, suffix with `-a` / `-b`.

### Dialectic rhythm guard

If the lead has made 3 consecutive decisions without user input during L2 + L3 + L4 (role inference, file ownership, model default, worktree on/off, team size), inject an `AskUserQuestion` to confirm the next decision before continuing. Counter resets on any user input. Counter scope is per-invocation.

### User approval prompt

Show the ambiguity score breakdown, the team cards with source tags, worktree decision, permission summary, applied domain guards, and any `automation:` flags. Ask: "이대로 spawn 할까요?" / "Spawn this team?" — proceed only on explicit yes / 진행 / go.

## L5 · Handoff Layer

Spawn the team and monitor.

### TeamCreate call

Team name format: `team-<short-purpose>-<YYYYMMDD-HHMM>`. Each teammate spawn prompt receives, in order:

1. The teammate's role body — inline-injected from `ROLES.md` (do NOT reference `subagent_type` for external subagents that restrict tools like `SendMessage` — that has been observed to break team collaboration)
2. The common domain guards from `ROLES.md`
3. The plan body (shared context)
4. The teammate's own task paragraph (from the L4 card)
5. Owned files / glob list
6. worktree path + branch (only when isolation is on)
7. Collaboration rules (other teammate names + when to `SendMessage` to whom)
8. Definition of Done — both task-specific and common (commit per convention + report one paragraph to lead)

### Worktree isolation

Default OFF. Switch ON when:
- The plan explicitly requests isolation.
- Two or more teammates would edit overlapping directories.
- The plan contains destructive operations.

When ON, the lead must `git worktree add` and pass the path + branch into the spawn prompt. On completion, the lead does NOT auto-merge.

### Monitoring + automation gate

- Idle teammates notify the lead automatically.
- Stuck teammates: report to the user and ask how to proceed (extra instruction / replace / shutdown).
- All-idle synthesis: produce a one-paragraph summary for the user.

When the plan's Constraints include `automation: pr-create`, run the PR gate:

0. Confirm the `automation: pr-create` flag is set explicitly by the user — either present in the original plan body, OR chosen by the user during L3 grilling (explicit yes to the "Add `automation: pr-create`" option, captured as a `[from-user]` source tag on the Constraints field). Lead-inferred natural-language signals ("create a PR for me", "올려줘") do NOT count and must NOT trigger automation.
1. qa verdict must be all green. Otherwise block and report.
   Exception: when the plan also sets `automation: skip-qa` (and the user confirmed once during L3 grilling that PR creation without qa verification is intended), bypass the qa gate. Record the bypass in the L5 summary so the human knows the PR did not go through qa.
2. reviewer verdict — block on any `❌`; force a reviewer-summary banner at the top of the PR body if 1-2 `⚠️`; block on 3+ `⚠️`.
3. Discover the repository's default branch dynamically — do NOT hardcode `main`. Use `DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)` and fall back to `$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')` if `gh` is unavailable.

3a. Reconcile with the no-auto-push guard. `gh pr create` needs a remote head, but the common guards forbid auto-push. Resolution:

   - **If the plan explicitly authorizes a push** (the plan body contains `automation: pr-create` AND either `automation: allow-push` OR the user gave explicit yes to a "Push the branch and create the PR?" prompt during L3 grilling): the lead may run `git push -u origin "$(git rev-parse --abbrev-ref HEAD)"` immediately before `gh pr create`. Report the push and PR URLs to the user.
   - **Otherwise**: do NOT push. Stop and ask the user once: "Branch `<name>` has not been pushed. Push and create the draft PR? (yes / no)" — proceed only on explicit yes; otherwise instruct the user to push manually and re-run the skill.

3b. With worktree isolation OFF and the push reconciled per step 3a, build the PR title and body non-interactively before calling `gh`. Synthesize:

   - `PR_TITLE` — the plan's `Why` first line (or a one-line slug of the plan title); single line, ≤ 70 chars.
   - `PR_BODY_FILE` — a temporary file (e.g. `$(mktemp)`) containing the full synthesized body: plan `Why` + per-teammate one-line report + qa verdict table + reviewer summary banner (when applicable).

   Then run:

   ```bash
   gh pr create \
     --draft \
     --base "$DEFAULT_BRANCH" \
     --head "$(git rev-parse --abbrev-ref HEAD)" \
     --title "$PR_TITLE" \
     --body-file "$PR_BODY_FILE"
   ```

   Both `--title` and `--body-file` MUST be present so `gh` does not drop into an interactive editor and hang the agent run. Capture the returned PR URL and report it to the user.

   With isolation ON, do NOT auto-merge — instead instruct the user to combine the worktree branches manually, then push the combined branch and run `gh pr create` themselves with `--title` and `--body-file` (or `--body`) explicitly set.
4. Never run `gh pr merge` automatically — that is always a human action.

### Cleanup

When the user says "cleanup" / "팀 정리", call `TeamDelete`. Live teammates must be shut down before deletion to preserve state consistency.

## Safety defaults

| Item | Default |
|---|---|
| Execution location | Current session (current window splits into panes). To keep the working window intact, the user can run the skill from a dedicated terminal window. Detached-tmux delegation is out of scope for this release. |
| User confirm before spawn | ON. Skip is not allowed. |
| Teammate model | `sonnet` |
| Team size | 3-5 based on plan signals |
| Worktree isolation | OFF (ON when plan signals destructive ops or overlap) |
| Plan-approval mode | ON for risky tasks |
| Permission | Inherited from lead. Reviewer and read-only roles are adjusted post-spawn. |

## Known limits (Claude Code platform)

- `/resume` does not restore in-process teammates. The lead may try to message a teammate that no longer exists — respawn.
- Teammate task-status lag — the lead may need to refresh manually.
- Shutdown waits for the current turn to finish.
- One team per session.
- Nested teams are not supported.
- The lead role is bound to the session that created the team.

## When NOT to use

- Single task or strongly sequential work (use a single session or one subagent).
- Multiple workers would edit the same file (conflict).
- "Just give me an answer" research (a single subagent is more efficient).
