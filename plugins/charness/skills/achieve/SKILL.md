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

# 3. scaffold first, then validate. To LOCATE an existing goal, drop --fields-file:
#    a body that no longer matches the edited artifact is refused, not ignored.
python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . --slug <slug> --fields-file <fields.json>
python3 "$SKILL_DIR/scripts/check_goal_artifact.py" --repo-root . --slug <slug> --date <yyyy-mm-dd>
```

If a goal artifact for this work already exists, read it first and continue its
lifecycle instead of starting a new one.

## Workflow

`achieve` runs one goal as three phases. `check_goal_artifact.py` emits a
`phase_brief` naming the current-phase file plus `references/goal-artifact.md`
depth; read that file, not the full contract, and follow its `closeout_handoff` note.

1. Before — shape and save.
   - interview from prose with a few high-leverage questions; if the request is
     ambiguous between artifact-only and implementation-continuation paths,
     ask at least one question before saving, or state the assumed interpretation
     when a strong default settles it
   - establish the `## Backlog Recount`, outcome, non-goals, boundaries, user
     acceptance, verification plan, outcome/failed capability, proof cost,
     test-duplication pressure, slice sequence, critique plan, stop conditions,
     reporting expectations, closeout binding plan (minimum fields: semantic
     inputs, fixed target/SHA, fresh-eye channel, lock evidence, terminal-record
     rule), and timebox fields (`Timebox:`, `Activation time:`, `Closeout reserve:`, `Done-early policy: continue_next_improvement`)
   - replace all `To be filled by the achieve Before-phase` placeholders; any
     leftover marker leaves the goal unshaped to `--pursue-ready`, and so does a
     MISSING required/portability heading (an artifact whose sections were never
     written carries no marker either, so marker-absence is not shaping-presence)
   - for consequential defaults (live/prod proof, issue close/split, broad scope,
     irreversible side effects, or proof-level non-claims) in Non-Goals,
     Boundaries, verification, interview decisions, or critique findings, add a
     non-empty `Discuss before activation:` summary and resolve or explicitly ask
     before activation; `--pursue-ready` fails unless that summary is resolved
   - save with `upsert_goal.py --fields-file <json>` at status `draft` (see the
     no-shell prose rule under During); artifact-only — it must not
     consume the host active-goal slot while drafting (only `/goal` pursuit does)
   - close with `Goal file:`, exact `Activation:` line, and the
     inert-until-`/goal` status; do not execute slices yourself
2. During — slice and record.
   - activation (`/goal`) is pure pursue: check
     `check_goal_artifact.py --pursue-ready --goal-path <artifact>` and
     fail-fast to the Before-phase (`/achieve @...`) if unshaped, missing a
     required activation-discussion summary, or carrying unresolved consequential
     activation discussion (`/goal` shapes nothing)
   - treat the active goal artifact as the slice memory surface, not `handoff`
   - keep `## Active Operating Frame` current as the short control panel; let
     `## Slice Log` remain the archive
   - before a substantial slice, state its objective and expected evidence
   - for fresh-eye slice critique, hand the reviewer a bounded slice packet:
     intent, changed files and owning/generated surfaces, expected invariants,
     tests/proof, non-claims, out-of-scope lines, and questions
   - append slice reports with `append_slice_log.py`. It and `upsert_goal.py`
     both take their prose through `--fields-file <json>`, never per-field
     flags: goal and slice prose cites identifiers, so it carries backticks, and
     a shell expands those BEFORE the helper starts — the artifact is written
     with words missing and the run still reports success. Nothing inside the
     helper can detect that. (A caller that builds `argv` itself, with no shell,
     is equally safe.) When tests are added or expanded, include a cheap
     duplicate-pressure sample via `test-pressure`
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
   - before `blocked`, render the `## Remaining Boundary Matrix` classifying every external/live proof lane (`references/goal-artifact.md` owns the line form; `upsert_goal.py` refuses the flip if a lane is runnable); on blocker or `No safe next slice:` closeout, record reason and report artifacts
3. After — prove and reflect.
   - **closeout preflight (describe-first):** before drafting closeout evidence,
     run `describe_goal_closeout_shape.py --goal-path <artifact>` for this goal's
     conditional missing-line set in one pass, then verify once (not flip-serially)
   - bind closeout in order: freeze semantic inputs -> packet at fixed SHA -> fresh-eye -> verification lock -> terminal record
   - run the final quality gate or documented substitute; if a broad
     duplicate/pressure gate fails, classify new-slice-local versus accumulated
     suite debt and name the smallest structural cleanup
   - record high-confidence / live proof, or state explicitly that it was not run
   - write final self-verification, residual risks, non-claims, and user
     verification instructions
   - if a timeboxed goal stops early, follow `references/lifecycle-after.md`
   - run `retro` for the automatic efficiency review; for this goal's closeout persistence, pass `--goal-path <canonical goal artifact>` and include exactly one matching top-level `Goal:` field
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
   - the closeout-shape script's missing-line set is the contract for every
     conditional floor (disposition, coordination, timebox, and the rest):
     `describe_goal_closeout_shape.py --goal-path <artifact>` renders each one
     live from the validator, so nothing here is re-derived or restated
   - **design the successor goal from what this run LEARNED, not what is left
     over, and record `Successor goal: <path>` in `## Coordination Cues`** — the
     last closeout act, required at every completion
   - run `check_goal_artifact.py`, then flip status to `complete` or `superseded`
   - if the artifact names `current HEAD`/`HEAD is` with an immutable SHA, make
     the SHA match the live `git rev-parse HEAD` result or mark it historical
   - before any host-level goal completion/status tool call, prove the checked-in
     goal artifact is already `Status: complete` and passes
     `check_goal_artifact.py`; never let a host green signal substitute for the
     artifact evidence floor

## Coordination

`achieve` reuses existing skills and must keep each useful standalone; see `references/coordination.md` for per-skill roles and the `handoff` boundary.

- `ideation`/`spec` upstream; `impl` for slices; `debug` before bug fixes;
  `quality` for verification cadence; `issue` for off-goal findings and staging
  the originating tracked issue's closeout; `critique` for plan/slice/final
  review; `retro` for the after-action review. `achieve` itself does not push.
- Do not absorb their work or add `achieve`-only branches to them.

## Output Shape

- a goal artifact under `charness-artifacts/goals/<yyyy-mm-dd-slug>.md` with `## Active Operating Frame` plus audit sections in `references/goal-artifact.md`
- a `## Operator Decision Queue` section for deferrable operator-only decisions
- `Status` is one of draft / active / blocked / complete / superseded
- an explicit `/goal @...` activation line
- at completion, a final report that separates self-verification, user
  verification, residual risk, non-claims, and the operator decision queue
- at completion, an explicit disposition for each surfaced improvement
  (`applied: <what>` or `tracked issue`) — never prose-only memory
- a `## Coordination Cues` section that records routing from installed skill
  metadata/model judgment (never an inline phase→skill map; use the catalog only
  for hidden availability facts) and, at completion, `Routing:` / `Gather:`
  / `Release:` / `Issue closeout:` evidence (or an `n/a — <reason>` opt-out)
  whenever the matching closeout floor is triggered, plus a `Successor goal:`
  line at EVERY completion
- a `## Closeout Binding Plan` with minimum fields shaped before activation; semantic values and final identity remain closeout proof

## Guardrails

- `achieve` is a goal operator, not a generic task runner or execution engine: it
  does not start executing before activation, and not every short prompt needs to
  become a goal. The Workflow steps and `references/lifecycle.md` own the positive
  form of each phase rule the guardrails would otherwise restate — `/goal` shapes
  nothing (pursue-only), slice/quality cadence, named proof levels (no provider/live
  claim from local checks), `handoff`-is-not-the-scratchpad, frame-over-slice-log,
  cached-input-is-not-waste, the inline-and-persisted `retro`, the
  presence-only disposition floor, and metadata/model-judgment coordination routing.
- Do not fabricate token, time, or tool-call metrics the host log does not expose.

## References

- `references/index.md`
