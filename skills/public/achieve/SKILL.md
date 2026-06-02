---
name: achieve
description: "Use when operating a long-running autonomous objective as an auditable goal lifecycle: interview prose intent into a reviewable goal artifact under charness-artifacts/goals/, keep slice progress and verification visible during the run, and prove the goal with honest non-claims at the end. Coordinates ideation/spec/impl/quality/issue/critique/retro around one goal artifact instead of replacing them, and stays a goal operator rather than a task execution engine."
---

# Achieve

Use this when the user wants to prepare, strengthen, run, or audit a
long-running autonomous objective — including prose like `$achieve <outcome>` or
a request for a reviewable `/goal @file` activation artifact.

`achieve` turns prose intent into one auditable goal artifact, coordinates the
existing workflow skills around it, and keeps progress, proof, and non-claims
visible. It does not execute a separate run loop.

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

`achieve` runs one goal as three phases. See `references/lifecycle.md` and
`references/goal-artifact.md` for the full contract.

1. Before — shape and save.
   - interview from prose with a few high-leverage questions; if the request is
     ambiguous between artifact-only and implementation-continuation paths,
     ask at least one question before saving, or state the assumed interpretation
     when a strong default settles it
   - establish outcome, non-goals, boundaries, user acceptance, verification
     plan, proof cost, test-duplication pressure, slice sequence, critique plan,
     stop conditions, and reporting expectations
   - replace all `To be filled by the achieve Before-phase` placeholders; any
     leftover marker leaves the goal unshaped to `--pursue-ready`
   - for consequential defaults in Non-Goals, Boundaries, verification,
     interview decisions, or critique findings (live/prod proof,
     issue close/split, broad bundled scope, irreversible side effects, or
     proof-level non-claims), add a non-empty `Discuss before activation:`
     summary and resolve or explicitly ask about those items in the transcript
     before reporting the goal ready to enter or offering activation; otherwise
     `--pursue-ready` fails, and a present summary is still not proof that the
     discussion is resolved
   - save with `upsert_goal.py` at status `draft`
   - close with `Goal file:`, exact `Activation:` line, and the
     inert-until-`/goal` status; do not execute slices yourself
2. During — slice and record.
   - activation (`/goal`) is pure pursue: check
     `check_goal_artifact.py --pursue-ready --goal-path <artifact>` and fail
     fast to the Before-phase (`/achieve @...`) if unshaped or missing a required
     activation-discussion summary
   - treat the active goal artifact as the slice memory surface, not `handoff`
   - keep `## Active Operating Frame` current as the short control panel; let
     `## Slice Log` remain the archive
   - before a substantial slice, state its objective and expected evidence
   - for fresh-eye slice critique, hand the reviewer a bounded slice packet:
     intent, changed files and owning/generated surfaces, expected invariants,
     tests/proof, non-claims, out-of-scope lines, and questions
   - append slice reports with `append_slice_log.py`; when tests are added or
     expanded, include a cheap duplicate-pressure sample via `--test-pressure`
   - use cheap deterministic checks at commit boundaries; use higher-cost proof
     at slice boundaries; reserve broad/live proof for bundle boundaries or the
     final stage
   - keep critique slice-level, not commit-level
   - file off-goal findings through `issue`; record only the reference and
     reason in the artifact
   - on an unresolvable blocker, flip status to `blocked`, record the blocker
     and attempted paths, and ask the user
3. After — prove and reflect.
   - run the final quality gate or documented substitute; if a broad
     duplicate/pressure gate fails, classify new-slice-local versus accumulated
     suite debt and name the smallest structural cleanup
   - record high-confidence / live proof, or state explicitly that it was not run
   - write final self-verification, residual risks, non-claims, and user
     verification instructions
   - run `retro` for the automatic efficiency review
   - when host evidence exists, summarize measured efficiency signals and proxy
     pressure separately: tokens/time, compactions, tool-call counts, repeated
     VCS/check commands, polling, and subagent count. Cached input alone is not
     waste.
   - disposition every surfaced improvement in Auto-Retro: either
     `applied: <what>` (a gate, hook, validator, test, or code change committed
     this run) or `issue #N`; prose-only memory is invalid. If there is nothing
     actionable, record one per-goal `Retro dispositions: none — <reason>` line.
   - **disposition gate, for goals created after the rule landed:** a deterministic
     block blank Auto-Retro when cited retro lists improvements and require a
     bound `Disposition review:` line (or `host-blocked-subagent` skip). This is
     presence/binding-only, never a content classifier; pre-rule goals are
     grandfathered.
   - **coordination floors (gather + release + issue closeout), for goals
     created after the rules landed:** an external source in
     `## Context Sources` needs a `Gather:` step (or `n/a — <reason>`); a touched
     release surface needs a `Release:` step; tracked issue sources or closeout
     work need an `Issue closeout:` step. Presence-only, grandfathered.
   - run `check_goal_artifact.py`, then flip status to `complete`
   - if the artifact names `current HEAD`/`HEAD is` with an immutable SHA, make
     the SHA match the live `git rev-parse HEAD` result or mark it historical
   - before any host-level goal completion/status tool call, prove the checked-in
     goal artifact is already `Status: complete` and passes
     `check_goal_artifact.py`; never let a host green signal substitute for the
     artifact evidence floor

## Coordination

`achieve` reuses existing skills and must keep each useful standalone. See
`references/coordination.md` for the per-skill roles and the `handoff` boundary.

- `ideation`/`spec` upstream; `impl` for slices; `debug` before bug fixes;
  `quality` for verification cadence; `issue` for off-goal findings and staging
  the originating tracked issue's closeout; `critique` for plan/slice/final
  review; `retro` for the after-action review. `achieve` itself does not push.
- Do not absorb their work or add `achieve`-only branches to them.

## Output Shape

- a goal artifact under `charness-artifacts/goals/<yyyy-mm-dd-slug>.md` with a
  top-level `## Active Operating Frame` plus the required audit sections (Goal,
  Non-Goals, Boundaries, User Acceptance, Agent Verification Plan, Slice Plan,
  Slice Log, Context Sources, Interview Decisions, Plan Critique Findings,
  Off-Goal Findings, Final Verification, User Verification Instructions,
  Auto-Retro)
- `Status` is one of draft / active / blocked / complete
- an explicit `/goal @...` activation line
- at completion, a final report that separates self-verification, user
  verification, residual risk, and non-claims
- at completion, an explicit disposition for each surfaced improvement
  (`applied: <what>` or `issue #N`) — never prose-only memory
- a `## Coordination Cues` section that defers phase routing to `find-skills`
  (never an inline phase→skill map) and, at completion, a `Gather:` /
  `Release:` / `Issue closeout:` step (or an `n/a — <reason>` opt-out) whenever
  the matching closeout floor is triggered

## Guardrails

- Do not make `achieve` a generic task runner; it is a goal operator, and it
  does not implement a new execution engine.
- Do not start executing the goal before the user activates it.
- Do not shape a goal at `/goal` activation; `/goal` pursues only and
  fail-fasts on an unshaped goal, routing the operator to `/achieve`.
- Do not require every short prompt to become a goal.
- Do not run broad quality gates after every small commit.
- Do not make `handoff` the normal running scratchpad while a goal is active.
- Do not treat the historical slice log as the normal active prompt surface;
  refresh the active operating frame and archive completed detail below it.
- Do not claim provider, live, or release proof when only local deterministic
  checks ran; name skipped proof levels in the final report.
- Do not fabricate token, time, or tool-call metrics the host log does not expose.
- Do not treat cached input volume alone as waste.
- Do not collapse `retro` into a path reference; include its substantive findings
  inline and persist the file (see `references/lifecycle.md`).
- Do not leave surfaced improvements as prose-only retro memory; disposition
  each one, or record the falsifiable per-goal `none` line.
- Do not tighten the deterministic disposition floor into a content
  classifier; it proves a review ran, and the reviewer/human judges substance.
- Do not bake a phase→skill map into `## Coordination Cues`; defer routing to
  `find-skills` and record only the `gather` / `release` presence floors or
  explicit `n/a — <reason>` opt-outs.

## References

- `references/lifecycle.md`
- `references/goal-artifact.md`
- `references/coordination.md`
- `../../shared/references/bootstrap-resolution.md`
