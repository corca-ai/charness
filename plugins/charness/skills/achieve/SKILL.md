---
name: achieve
description: "Use when operating a long-running autonomous objective as an auditable goal lifecycle: interview prose intent into a reviewable goal artifact under charness-artifacts/goals/, keep slice progress and verification visible during the run, and prove the goal with honest non-claims at the end. Coordinates ideation/spec/impl/quality/issue/critique/retro around one goal artifact instead of replacing them, and stays a goal operator rather than a task execution engine."
---

# Achieve

Use this when the user wants to prepare, strengthen, run, or audit a
long-running autonomous objective — including prose like `$achieve <outcome>` or
a request for a reviewable `/goal @file` activation artifact.

The core problem is not long autonomous work. It is *unstructured* long
autonomous work: weak goal contracts, invisible progress, repeated closeout
ritual, broad gates run too often, and no final confidence story. `achieve`
turns prose intent into one auditable goal artifact and coordinates the existing
workflow skills around it. It does not execute the run loop itself.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`. Every
invocation starts here.

```bash
# 1. current repo and workflow context
sed -n '1,200p' docs/handoff.md 2>/dev/null || true
git status --short --branch
git log --oneline -10

# 2. any active goal already on disk
ls charness-artifacts/goals/ 2>/dev/null || true

# 3. inspect or scaffold the goal artifact (helpers preserve manual content)
python3 "$SKILL_DIR/scripts/check_goal_artifact.py" --repo-root . --slug <slug> --date <yyyy-mm-dd>
python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . --slug <slug> --title "<title>"
```

If a goal artifact for this work already exists, read it first and continue its
lifecycle instead of starting a new one.

## Workflow

`achieve` runs one goal as three phases. See `references/lifecycle.md` for the
full per-phase contract and `references/goal-artifact.md` for the artifact shape
and helper usage.

1. Before — shape and save.
   - interview from prose with a small number of high-leverage questions; stop
     when the work has enough shape to save a reviewable artifact
   - when the request is genuinely ambiguous between an artifact-only goal draft
     and an implementation-continuation run, ask at least one high-leverage
     question to resolve which one before saving; if a strong default settles
     it, state the assumed interpretation explicitly instead of asking (#239)
   - establish outcome, non-goals, boundaries, user acceptance, verification
     plan (low-cost / high-confidence / external-or-live, plus expected proof
     cost and expected test-duplication pressure per slice), slice sequence,
     critique plan, stop conditions, and reporting expectations
   - when shaping an auto-drafted skeleton, overwrite its
     `To be filled by the achieve Before-phase` placeholder lines with the real
     content; a leftover marker leaves the goal reading as unshaped to
     `--pursue-ready` (#247)
   - save with `upsert_goal.py` at status `draft`
   - tell the user the file is inert until they run `/goal @...`; do not start
     executing slices yourself
   - close the before-phase response with the `Goal file:` path and the exact
     `Activation:` line, and state the inert-until-`/goal` status, so the
     operator cannot miss how to activate (#239)
2. During — slice and record.
   - activation (`/goal`) is pure pursue: it runs the goal as given and never
     shapes. Before pursuing, confirm shape with
     `check_goal_artifact.py --pursue-ready --goal-path <artifact>`; if the goal
     is unshaped, fail-fast
     — refuse and route the user to the Before-phase (`/achieve @...`), do not
     shape inside `/goal` (#247)
   - treat the active goal artifact as the slice memory surface, not `handoff`
   - before a substantial slice, state its objective and expected evidence
   - after each slice, append a report with `append_slice_log.py`; when the
     slice adds or expands tests, record a cheap duplicate-pressure sample via
     `--test-pressure` so accumulated test debt stays visible at the boundary
   - use targeted deterministic checks per slice; reserve broad gates and
     expensive proof for bundle boundaries or the final stage
   - keep critique slice-level, not commit-level
   - file off-goal findings through `issue`; record only the reference and
     reason in the artifact
   - on an unresolvable blocker, flip status to `blocked`, record the blocker
     and attempted paths, and ask the user
3. After — prove and reflect.
   - run the final quality gate or its documented local substitute; if a broad
     duplicate/pressure gate fails, classify it as new-slice-local or
     accumulated-suite debt and name the smallest next structural cleanup
   - record high-confidence / live proof results, or state explicitly that they
     were not run
   - write final self-verification, residual risks, non-claims, and concrete
     user verification instructions
   - run `retro` for the automatic efficiency review
   - **disposition every improvement** the retro or the run surfaced: each one
     is either *applied in-session* (converted to teeth — a gate, hook,
     validator, test, or code change committed this run) or *filed as a tracked
     `issue`* for the next session to pick up. Whether to apply now or file is
     the agent's judgment; leaving an improvement as prose-only retro memory is
     **not** a valid disposition — decaying, unread lessons are the exact gap
     this closes. Record each improvement's disposition (`applied: <what>` or
     `issue #N`) in the goal artifact's Auto-Retro section. These two forms are
     **per-improvement**; a goal with nothing to act on may instead record one
     **per-goal** `Retro dispositions: none — <reason>` line (a falsifiable
     claim, not a third escape) — different scope, no conflict with "exactly two".
   - **disposition gate (#253), for goals Created ≥ 2026-05-30:** a deterministic
     floor refuses the flip when the cited retro lists improvements but
     `## Auto-Retro` is blank (block-the-blank) and requires a bound
     `Disposition review:` line (or a `host-blocked-subagent` skip) proving a
     fresh-eye review *ran* — presence/binding-only, never a content classifier.
     That fresh-eye reviewer (rung 2) records the per-improvement verdict a regex
     cannot judge; the substantive call is agent-backed and human-audited, not
     deterministic. Pre-rule goals are grandfathered.
   - **coordination floors (gather + release), for goals Created ≥ 2026-05-31:**
     when `## Context Sources` names an external source the flip needs a
     `Gather:` step (or `Gather: n/a — <reason>`); when the run touched a release
     surface it needs a `Release:` step (or `Release: n/a — <reason>`).
     Presence-only, scoped to `## Coordination Cues`, grandfathered by `Created`.
   - run `check_goal_artifact.py`, then flip status to `complete`

## Coordination

`achieve` reuses existing skills and must keep each useful standalone. See
`references/coordination.md` for the per-skill roles and the `handoff` boundary.

- `ideation`/`spec` upstream; `impl` for slices; `debug` for a bug-class goal's
  root cause before the fix; `quality` for verification cadence; `issue` for
  off-goal findings *and* staging the originating tracked issue's close at
  closeout (`Close #N` on the default-branch commit/PR body; `achieve` does not
  push); `critique`
  for plan/slice/final review; `retro` for the after-action review.
- Do not absorb their work or add `achieve`-only branches to them.

## Output Shape

- a goal artifact under `charness-artifacts/goals/<yyyy-mm-dd-slug>.md` with the
  required sections (Goal, Non-Goals, Boundaries, User Acceptance, Agent
  Verification Plan, Slice Plan, Slice Log, Off-Goal Findings, Final
  Verification, User Verification Instructions, Auto-Retro)
- `Status` is one of draft / active / blocked / complete
- an explicit `/goal @...` activation line
- at completion, a final report that separates self-verification, user
  verification, residual risk, and non-claims
- at completion, an explicit disposition for each surfaced improvement
  (`applied: <what>` or `issue #N`) — never prose-only memory
- a `## Coordination Cues` section that defers phase routing to `find-skills`
  (never an inline phase→skill map) and, at completion, a `Gather:` / `Release:`
  step (or an `n/a — <reason>` opt-out) whenever the gather / release closeout
  floor is triggered

## Guardrails

- Do not make `achieve` a generic task runner; it is a goal operator, and it
  does not implement a new execution engine.
- Do not start executing the goal before the user activates it.
- Do not shape a goal at `/goal` activation; `/goal` pursues only and
  fail-fasts on an unshaped goal, routing the operator to `/achieve` (#247).
- Do not require every short prompt to become a goal.
- Do not run broad quality gates after every small commit.
- Do not make `handoff` the normal running scratchpad while a goal is active.
- Do not claim provider, live, or release proof when only local deterministic
  checks ran; name skipped proof levels in the final report.
- Do not fabricate token, time, or tool-call metrics the host log does not
  expose; record `when available` instead.
- Do not collapse `retro` into a path reference at closeout; narrate the
  retro's substantive findings inline as well as persisting the file
  (the #233 F2 pattern is the recurrence history this guards against;
  see `references/lifecycle.md` After section).
- Do not leave a surfaced improvement as prose-only retro memory at closeout.
  Every improvement is dispositioned per-improvement as applied-in-session
  (teeth) or a filed `issue` (next-session pickup) — or the run records one
  per-goal `Retro dispositions: none — <reason>` line when nothing is actionable
  (a claim the fresh-eye reviewer can falsify, not a silent skip). The now-vs-next
  choice is agent judgment, but the disposition itself is mandatory.
  Capture-and-hope is the loop the goal operator must close, not widen.
- Do not tighten the deterministic disposition floor (#253) into a content
  classifier. It blocks the blank and proves a review ran; judging whether each
  improvement was *genuinely* disposed is the fresh-eye reviewer's and the
  human's job — a prose word-list over-fires or passes narration.
- Do not bake a phase→skill map into the `## Coordination Cues` carrier; defer
  *which* skill answers a boundary to `find-skills`. The two presence-only floors
  are the only teeth: `gather` when `## Context Sources` names an external source,
  `release` when the run touches a release surface — record the step or an
  explicit `n/a — <reason>` opt-out, never prose-only intent. Both are
  grandfathered by `Created` date and stay presence/binding-only, never a
  prose-quality classifier.

## References

- `references/lifecycle.md`
- `references/goal-artifact.md`
- `references/coordination.md`
- `../../shared/references/bootstrap-resolution.md`
