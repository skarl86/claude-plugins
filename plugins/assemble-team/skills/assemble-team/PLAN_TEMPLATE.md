# Plan template (assemble-team friendly)

Writing your plan in this shape lets the lead derive a team accurately. Of the sections below, **Why / Scope / Tasks / DoD / Out of scope** are recommended for any non-trivial plan.

## Recommended sections

### Why (required)
One paragraph: why this work is needed, what triggered it, and any prior context. The lead uses this to score the Goal dimension and to write commit / PR messages.

### Scope (strongly recommended)
List the directories / services that this plan touches. One line per scope. Examples:
- `apps/<app-name>` (frontend)
- `services/<service-name>` (backend)
- `packages/<shared-lib>`
- `infra/`, `.github/workflows/` (devops scope)

The lead maps these to roles using `ROLES.md`.

### Constraints (close to required)
- read-only / write
- token / time budget
- explicit do-not-touch items (e.g. no push, no infra changes)
- worktree isolation (`worktree=on` / `worktree=off`)
- permissions (`permissions=skip` / `permissions=ask` / `permissions=accept-edits`)
- automation flags (optional):
  - `automation: pr-create` — when all qa tasks are `✅` and worktree isolation is OFF, the lead runs `gh pr create --draft --base <default-branch>`. Merge is never automatic.
  - `automation: skip-qa` — suppress the default-added qa task (use for read-only investigative plans).

### Tasks (required)
One line per task. Optional `[role:X]` hint at the end:
- `- [ ] [role:frontend] update the RefundDialog copy`
- `- [ ] [role:backend] add a new field to the refund response schema`
- `- [ ] [role:reviewer] cross-review the changes above`

If `[role:X]` is omitted, the lead infers the role from `ROLES.md` heuristics.

### Definition of Done (required)
Per task, a verifiable outcome:
- changed files committed (Conventional Commits)
- relevant tests pass (`pytest` / `vitest` / etc.)
- one-paragraph summary `SendMessage` to lead
- (optional) post-deploy / runtime verification

### Out of scope (strongly recommended)
Items deliberately deferred to a human or later iteration:
- PR creation / push / merge / deploy
- adjacent refactors at the same call sites
- dependency upgrades
- external system changes (schema, infra env vars)

## Optional sections

### Risks
- regression risk (e.g. "external API schema change → parser mismatch")
- data risk (e.g. "DB migration with no easy rollback")

### Token budget
- estimated tokens overall and per teammate

### Time budget
- target wall-clock

---

## Example plan (universal)

```markdown
# Plan: refund policy refresh across surfaces

## Why
Q2 introduces a new refund policy. The UI copy, the refund API response, and any
user-facing messaging must agree. Inconsistent wording across surfaces has been
flagged by support as a recurring complaint source.

## Scope
- apps/web/src/components/RefundDialog.tsx
- services/payments/handlers/refund.py
- packages/messaging/templates/refund.md

## Constraints
- worktree=off (the three scopes live in distinct, non-overlapping directories — file ownership separation is sufficient)
- permissions=skip
- Conventional Commits
- push / merge / deploy → human only
- automation: pr-create  (lead creates a draft PR when all qa is `✅` AND worktree isolation is OFF; ready and merge remain human)

## Tasks
- [ ] [role:frontend] update RefundDialog copy to match the new policy
- [ ] [role:backend] add `refund_eligibility_reason` to the refund response schema
- [ ] [role:backend] update the refund message template under `packages/messaging/` (a second backend teammate; the lead names it `backend-b` in the L4 mapping because it owns a different scope, but the role hint stays `backend` — the `-b` suffix is a teammate name, not a role)
- [ ] [role:reviewer] cross-review the three changes for wording, secrets, boolean defaults
- [ ] [role:qa] (default-added) integration e2e on top of per-surface tests — the verdict gates the automation: pr-create flow

## Definition of Done
- All three surfaces committed on a branch from the default branch (Conventional Commits)
- Per-surface tests pass (`pnpm test`, `pytest`)
- reviewer: `✅` / `⚠️` / `❌` table delivered
- qa: final verdict `전체 ✅` or English equivalent — gates the PR auto-creation
- automation: pr-create runs → draft PR opened; ready and merge remain human

## Out of scope
- payment gateway changes
- refund backend job changes
- promoting the draft PR to ready or merging it (human only)

## Risks
- wording drift between UI / API / messaging — reviewer must catch
- a single qa `❌` blocks the automation: pr-create flow — fix and rerun
```

When you invoke the assemble-team skill against this body (paste the plan and ask "assemble a team for this plan"), the lead will:
1. Map the three scopes — RefundDialog → `frontend`, refund API handler → `backend`, messaging template → `backend-b` (a second backend instance for the non-overlapping scope)
2. Add `[role:reviewer]` and the default `[role:qa]` to reach a 5-teammate team
3. Show the team mapping + ambiguity summary + `automation: pr-create` notice for approval
4. Spawn with `worktree=off` (file ownership separation), `permissions=skip`, role bodies inline-injected
5. After all teammates idle, check the qa verdict. If `✅` AND worktree isolation is OFF (which it is in this example), the lead:
   a. discovers the default branch — `DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)`;
   b. reconciles the no-auto-push guard — if `automation: pr-create` is set without `automation: allow-push` AND no explicit grilling consent was recorded, the lead asks the user once "Push the branch and create the draft PR? (yes / no)" and proceeds only on yes; otherwise it pushes via `git push -u origin "$(git rev-parse --abbrev-ref HEAD)"`;
   c. synthesizes `PR_TITLE` (one line, ≤ 70 chars, derived from the plan's `Why`) and `PR_BODY_FILE` (`$(mktemp)` containing the full body — plan `Why` + per-teammate report + qa verdict + reviewer summary banner when applicable);
   d. runs the noninteractive command exactly as L5 instructs:
```bash
gh pr create --draft \
  --base "$DEFAULT_BRANCH" \
  --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "$PR_TITLE" \
  --body-file "$PR_BODY_FILE"
```
   Both `--title` and `--body-file` MUST be present so `gh` never falls into an interactive editor and hangs the agent run.

   If qa is not green or any precondition fails, the lead reports the failure to the user and stops without creating a PR.
