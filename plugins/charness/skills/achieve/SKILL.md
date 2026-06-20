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

# 3. scaffold or locate first, then validate post-scaffold (helpers preserve manual content)
python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . --slug <slug> --title "<title>"
python3 "$SKILL_DIR/scripts/check_goal_artifact.py" --repo-root . --slug <slug> --date <yyyy-mm-dd>
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
     stop conditions, reporting expectations, and timebox fields (`Timebox:`, `Activation time:`, `Closeout reserve:`, `Done-early policy: continue_next_improvement`)
   - replace all `To be filled by the achieve Before-phase` placeholders; any
     leftover marker leaves the goal unshaped to `--pursue-ready`
   - for consequential defaults (live/prod proof, issue close/split, broad scope,
     irreversible side effects, or proof-level non-claims) in Non-Goals,
     Boundaries, verification, interview decisions, or critique findings, add a
     non-empty `Discuss before activation:` summary and resolve or explicitly ask
     before activation; `--pursue-ready` fails unless that summary is resolved
   - save with `upsert_goal.py` at status `draft`; artifact-only — it must not
     consume the host active-goal slot while drafting (only `/goal` pursuit does)
   - close with `Goal file:`, exact `Activation:` line, and the
     inert-until-`/goal` status; do not execute slices yourself
2. During — slice and record.
   - activation (`/goal`) is pure pursue: check
     `check_goal_artifact.py --pursue-ready --goal-path <artifact>` and fail
     fast to the Before-phase (`/achieve @...`) if unshaped, missing a required
     activation-discussion summary, or carrying unresolved consequential
     activation discussion
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
   - external-side-effect approval (publish/push/remote-CI/apply) is scoped to
     the phase or bundle that requested it and does not carry forward; after an
     approved lane, done-early test-only continuation is local by default unless
     the operator explicitly asks or a runtime-affecting slice needs it earlier
   - keep critique slice-level, not commit-level
   - file off-goal findings through `issue`; record only the reference and
     reason in the artifact
   - before `blocked`, render the `## Remaining Boundary Matrix` classifying every external/live proof lane (lifecycle.md; `upsert_goal.py` refuses the flip if a lane is runnable); on blocker or `No safe next slice:` closeout, record reason and report artifacts
3. After — prove and reflect.
   - **closeout preflight (describe-first):** before drafting closeout evidence,
     run `describe_goal_closeout_shape.py --goal-path <artifact>` for this goal's
     conditional missing-line set in one pass, then verify once (not flip-serially)
   - run the final quality gate or documented substitute; if a broad
     duplicate/pressure gate fails, classify new-slice-local versus accumulated
     suite debt and name the smallest structural cleanup
   - record high-confidence / live proof, or state explicitly that it was not run
   - write final self-verification, residual risks, non-claims, and user
     verification instructions
   - if a timeboxed goal stops early, follow `references/lifecycle.md`
   - run `retro` for the automatic efficiency review
   - for a long goal with host timing data, record the goal window and render the
     provider-safe metrics block per `references/goal-artifact.md`, not by hand
   - when host evidence exists, summarize measured vs proxy efficiency signals
     separately; cached input alone is not waste (see `references/goal-artifact.md`)
   - disposition every surfaced improvement in Auto-Retro: either
     `applied: <what>` (a gate, hook, validator, test, or code change committed
     this run) or `tracked issue`; prose-only memory is invalid. If there is nothing
     actionable, record one per-goal `Retro dispositions: none — <reason>` line.
   - when a disposition routes to a tracked issue, it carries the generalized
     `Structural pattern:`+`Triggering instance(s):` and a resolved `Destination:`
     per `../../shared/references/retro-issue-destination-split.md`.
   - **disposition gate, for goals created after the rule landed:** block blank
     Auto-Retro; require a bound `Disposition review:` line; and when a retro
     names transferable waste, require a `Structural follow-up:` destination.
     Presence/binding-only, never a content classifier; pre-rule grandfathered.
   - **coordination floors:** for in-scope goals, recorded phase work needs
     `Routing:`; external sources need `Gather:`; release surfaces need
     `Release:`; tracked issue closeout needs `Issue closeout:`.
     Presence-only, grandfathered.
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

- a goal artifact under `charness-artifacts/goals/<yyyy-mm-dd-slug>.md` with
  `## Active Operating Frame` plus the audit sections in
  `references/goal-artifact.md`
- a `## Operator Decision Queue` section for deferrable operator-only decisions
- `Status` is one of draft / active / blocked / complete
- an explicit `/goal @...` activation line
- at completion, a final report that separates self-verification, user
  verification, residual risk, non-claims, and the operator decision queue
- at completion, an explicit disposition for each surfaced improvement
  (`applied: <what>` or `tracked issue`) — never prose-only memory
- a `## Coordination Cues` section that defers phase routing to `find-skills`
  (never an inline phase→skill map) and, at completion, `Routing:` / `Gather:`
  / `Release:` / `Issue closeout:` evidence (or an `n/a — <reason>` opt-out)
  whenever the matching closeout floor is triggered

## Guardrails

- `achieve` is a goal operator, not a generic task runner or execution engine: it
  does not start executing before activation, and not every short prompt needs to
  become a goal. The Workflow steps and `references/lifecycle.md` own the positive
  form of each phase rule the guardrails would otherwise restate — `/goal` shapes
  nothing (pursue-only), slice/quality cadence, named proof levels (no provider/live
  claim from local checks), `handoff`-is-not-the-scratchpad, frame-over-slice-log,
  cached-input-is-not-waste, the inline-and-persisted `retro`, the
  presence-only disposition floor, and `find-skills`-deferred coordination routing.
- Do not fabricate token, time, or tool-call metrics the host log does not expose.

## References

- `references/index.md`
