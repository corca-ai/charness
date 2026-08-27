# P0–P2 backlog requalification — 2026-08-26

Status: current working ledger for goal `adversarial-priority-backlog-closeout`

## Truth boundary

- Capture time: 2026-08-26T04:08:29Z.
- Source revision for local probes: `9c32398c90b874bd624c9e5f89d7ddcfce04d4ab`.
- Tracker source: `gh issue list --repo corca-ai/charness --state open --limit 100`
  plus `python3 skills/public/issue/scripts/issue_tool.py read --repo
  corca-ai/charness --number <N>` for each claimed number.
- All 26 claimed reads returned `state: OPEN` and `comments_read: true` at
  requalification time. The GitHub state and final comments remain authoritative;
  this file is a decision ledger, not a replacement for tracker state.
- No row below claims a hosted, installed, public-release, or remote-CI result
  unless the row names that channel as an explicit proof obligation. Local source
  and command results establish premises and lane ownership only.

## Judgment vocabulary

- `premise-holds`: the reported arm is still visible in current source or in a
  current consumer-facing readback and receives a repair lane.
- `premise-refuted-clean`: the current producer and its first consumer establish
  that the reported defect is already satisfied; close as already satisfied with
  a typed behavior readback, without claiming this goal repaired it.
- `premise-refuted-with-residue`: the original arm is gone, but a narrower
  residue remains; keep only the narrowed lane or close with a typed non-verified
  disposition when the residue requires operator intent.
- `decision-bound`: the remaining question is an owner/intent boundary that the
  local implementation cannot decide honestly; close only with an explicit
  decision and non-verified behavior disposition, or keep the exact operator
  decision in the queue until its close carrier is ready.

## Current partition

| Issue | JTBD / current premise | Premise state | Classification | Owner | Proof diet | Lane / disposition |
| --- | --- | --- | --- | --- | --- | --- |
| #723 | Consumer quality planning must discover the adapter-declared skill paths and make the package's verification owner visible. The live comment identifies `plan_quality_run.py::_skill_paths()` hard-coding `skills/public`, `skills/support`, and `plugins/*/skills`, while Ceal's `.agents/quality-adapter.yaml` declares `skill_ergonomics_skill_paths` elsewhere. | premise-holds | feature | quality planner + catalog applicability | Exact planner output with a consumer-shaped adapter and first catalog/quality consumer; advisory heuristics remain advisory. | `consumer-selection`; repair |
| #722 | Setup/quality must produce an ownership-shaped normalization plan for oversized `AGENTS.md`/docs surfaces. The issue's current body still reports existence-only normalization and no bounded owner map. | premise-holds | feature | setup normalization + quality bootstrap | Dry-run output must name bounded owners and distinguish existence from shape; no bulk rewrite and no broad gate unless shared surfaces change. | `ownership-normalization`; repair |
| #721 | Debug artifact authoring must enforce the shape before broad indexing. The three artifacts named by the issue now validate individually through `validate_debug_artifact.py`. | premise-refuted-clean | bug | debug scaffold/validator | Re-run the three named validators and cite the existing artifacts; no new implementation. | `already-satisfied`; close candidate |
| #717 | Goal readiness proof code needs conceptual headroom, not line shaving. `check_python_lengths.py` currently reports `goal_artifact_lib.py` at 360 lines and `goal_artifact_pursue.py` at 335 in the [330,360] warning band. | premise-holds | deferred-work | achieve readiness proof surface | Changed-line proof plus focused goal-artifact tests and the readiness consumer; split concepts only where ownership becomes clearer. | `proof-surface`; repair |
| #715 | External workers must not silently select a stale installed implementation skill after a source repair. The current issue read still carries a concrete source/installed 6.4.0 mismatch and no admission preflight. | premise-holds | bug | impl resolver/install/update boundary | Consumer-shaped installed/source version and path readback; local source proof is not installed-adoption proof. | `consumer-installed`; repair / operator boundary |
| #710 | Dup-ratchet edit advisory must normalize adapter `scope_paths`; raw `.` does not match `scripts/x.py` under the current `posix == root or starts root/` predicate. | premise-holds | bug | `scripts/dup_ratchet_edit_advisory.py` | Minimal whole-tree and nested-root consumer cases plus advisory output; do not broaden ratchet policy. | `reporting-advisory`; repair |
| #708 | Python-length checking must report every over-limit file in one run. The current loop raises on the first `validate_file_length` exception. | premise-holds | bug | `scripts/check_python_lengths.py` | Two-invalid-file focused test and exact multi-file output; changed-line proof before broad quality. | `reporting-gate`; repair |
| #706 | Dup-ratchet summaries must not default found-counts/degraded fields to reassuring zeros when the scan did not judge. Current `summarize()` still supplies those defaults. | premise-holds | bug | `skills/public/quality/scripts/check_dup_ratchet.py` | Adapter-invalid, inert, and rebaseline fixtures with summary consumer readback; preserve withheld verdict fields. | `reporting-gate`; repair |
| #704 | `link_only_lines_slack` must have a stable numeric output type. Current annotation/behavior remains `int | str` with a sentinel sentence on an uncomputable path. | premise-holds | bug | `scripts/check_docs_graph.py` | Focused typed-output cases and the first YAML/JSON consumer; distinguish unavailable from a numeric zero. | `reporting-schema`; repair |
| #703 | Uncovered-set numbers must reach routine attention surfaces. Current source publishes overlap `uncovered`, dup-ratchet `SCOPE:`, and runtime-universe `unreachable_by_selected_profile`, but not all are shown in the ordinary broad-run path. | premise-refuted-with-residue | feature | quality attention/reporting consumers | Trace each field through its normal renderer; show only the missing attention path, never claim a gate ran because a payload exists. | `reporting-attention`; narrowed repair |
| #701 | Claims review needs a stable convergence boundary when the release bundle contains the artifacts describing the review. Current handoff records the 6.5.0 claims review as `unproven` after the independent worker timed out. | premise-holds | feature | release claims-review scope/bundle | Fixed-point or excluded-bundle fixture plus claims readback; no release publication grant is inferred. | `release-proof`; repair |
| #700 | A release-time grant must invalidate/re-read prose authored before the grant changes its claim boundary. Current release/goal records do not expose a complete re-read linkage. | premise-holds | bug | release grant and closeout narrative binding | Mutation/readback fixture around a grant transition; no claim about published history. | `release-proof`; repair |
| #699 | Release critique acceptance must bind to the candidate identity and verdict, not only reusable version tokens. Current `critique_acceptor()` calls closeout evidence with version-derived tokens and tracked/stub checks, without candidate identity binding. | premise-holds | bug | `plan_release_prepared_stop.py` / release preflight | Candidate A/B same-version fixture with a superseded HOLD artifact; publish planner must refuse the stale candidate. | `release-verdict`; repair |
| #698 | `superseded` must not silently bypass the Auto-Retro disposition floor. Current status handling checks only `Superseded by:` for this terminal state and skips the complete-state disposition obligations. | premise-holds | bug | achieve terminal-status lifecycle | New superseded artifact and flip tests covering surfaced improvements plus explicit handoff; verdict logic requires bounded review rounds. | `goal-lifecycle`; repair |
| #697 | Mutation sampling and changed-line coverage must not share one freshness-ambiguous report path. The three current producers all default to `reports/mutation/test-coverage.json` <!-- reproduction-source -->. | premise-holds | bug | mutation coverage producers | Distinct producer paths/markers and consumer readback; changed-line producer remains authoritative for changed-line proof. | `mutation-proof`; repair |
| #695 | Critique shape sources must emit the `Execution mode` field required by the closeout validator. The current draft-shape stub has no such line while typed-subagent observation requires it. | premise-holds | bug | issue/critique closeout shape producer | Render source/stub and validate a typed-subagent carrier; no prose-only shape claim. | `closeout-shape`; repair |
| #694 | Cadence floor must not treat a negated `--skip-broad-pytest` mention as a deferral. Current code uses clause-scoped structural handling and the issue comment records the fixed `applies:false ok:true` reproduction at `99c440aa7`. | premise-refuted-clean | bug | achieve cadence owner | Re-run the exact reproduction/focused test and cite current code; no new change. | `already-satisfied`; close candidate |
| #693 | Critique documentation claims same-context substitutes are refused, but current `skills/public/critique/scripts/record_round_findings.py` binds boundary/window/finding bytes without reviewer/execution identity. | premise-holds | bug | critique round writer + reviewer evidence | Same-context and distinct-context fixtures with explicit provenance; verdict logic needs bounded review. | `reviewer-provenance`; repair |
| #692 | Init-adapter idempotence must be wired across all 16 shipping public skills. Current census finds 16 `init_adapter.py` files but `existing_adapter_is_valid` only in `skills/public/impl/scripts/init_adapter.py`. | premise-holds | bug | public skill adapter bootstrap owners | Counted source census plus representative fresh/existing adapter runs; synchronize plugin mirror. | `adapter-bootstrap`; repair |
| #669 | Standing pytest must not orphan a child when SIGTERM interrupts `Popen` before the local handle is bound. Current `run_monitored_phase()` still enters `with subprocess.Popen(...) as process` directly at line 284; the handler race remains a live source arm. | premise-holds | bug | `scripts/subprocess_guard.py` | Deterministic constructor-interruption test and process-group readback; no claim about uninterruptible kernel sleep. | `process-runtime`; repair |
| #668 | The runtime-budget revisit trigger needs an owner decision about contention/profile policy, not another blind relevel. Current selected and universe budget checks pass with no missing samples/violations, while the universe explicitly declines to judge whether conditional labels ever run. | decision-bound | decision-needed | quality runtime-budget owner/operator | Record current pass plus the unresolved conditional/contended scope; do not call a clean budget check a performance proof. | `runtime-policy`; decision/close candidate |
| #667 | Generic release planning must route to a repository-specialized release lane when one exists. Current `next_action()` only chooses generic adapter/release/prepared-stop actions and has no specialized-lane discovery branch. | premise-holds | feature | release planner routing | Specialized-lane fixture and next-action output; no release mutation. | `release-routing`; repair |
| #637 | Critique preflight must render the scaffold at the installed/consumer layout it actually targets. Current registry still names `skills/public/critique/scripts/scaffold_critique_artifact.py`, which is absent in a flattened installed consumer where `skills/critique/scripts/...` is the working path. | premise-holds | bug | artifact-surface preflight + installed package layout | Consumer fixture with positive/negative scaffold paths and preflight output; no installed host claim. | `consumer-installed`; repair |
| #634 | The dependency-contract arm is fixed: current export contains `packaging/bootstrap-python.json` and `bootstrap-requirements.txt`, and `check_export_self_sufficiency.py --repo-root .` returns `status: pass` with `unguarded_entrypoint_imports: []`. The issue's own latest comment keeps the broader cwd-relative instruction sites, three shell gates, unexported data readers, and remaining bare imports open. | premise-refuted-with-residue | bug | packaging/export self-sufficiency | Close only the shipped contract arm if a new residual issue preserves the remaining scope; do not claim the broad inventory repaired. | `consumer-installed`; split/repair decision |
| #628 | Exact no-argument probes on 2026-08-26 now choose fresh dated records for both debug and quality (`write_artifact_effect: create_new_file`, `target_exists: false`), so the quality default overwrite arm reported on 2026-08-18 is no longer present. | premise-refuted-clean | bug | debug/quality scaffold producers | Re-run both no-argument scaffold probes and cite their typed payloads; do not claim #620 as a duplicate repair. | `already-satisfied`; close candidate |
| #546 | A budget label present in the runner but queued only conditionally still reads as enforceable unless operator intent declares the expectation. Current universe output has no unknown labels but explicitly says it does not judge whether a named label ever runs; the checker itself documents this remaining half. | decision-bound | decision-needed | runtime-budget adapter/operator contract | Record the clean membership result and the undecidable conditional-run boundary; no invented default for consumer intent. | `runtime-policy`; decision/close candidate |

## Immediate close candidates

The current evidence supports no-change closeout preparation for #721, #694,
and #628. #634 has a fixed dependency-contract sub-arm but remains an umbrella
for live residuals; it needs a split or a scoped repair decision before closure.
The three no-change close comments must use the issue closeout carrier, cite an
existing valid critique/debug artifact, distinguish tracker closure from
behavior proof, and receive an immediate GitHub CLOSED readback. No code change
is attributed to this goal unless a later repair lane actually changes it.

## Open implementation lanes

1. Consumer and authoring boundaries: #723, #722, #715, #692, #667, #637, and the residual #634 split/repair decision.
2. Proof/reporting surfaces: #717, #710, #708, #706, #704, #703, #695.
3. Release and lifecycle verdicts: #701, #700, #699, #698, #697, #693.
4. Process/runtime boundaries: #669.
5. Operator decision/typed disposition: #668, #546.

The lanes are disjoint at the file-owner level for the first implementation
pass. Shared generated mirrors are synchronized only by the integrating owner
of the slice that changes the source surface.

## Non-claims carried forward

- Local source checks do not prove the stale installed worker path in #715 or
  #637 is fixed until a consumer-shaped installed readback is run.
- Current release records and the handoff's `unproven` claims-review state do
  not prove a new release or public adoption.
- A passing runtime budget does not prove that conditional labels run, nor that
  in-gate contention has been solved.
- A GitHub CLOSED state will prove tracker closure only; each comment must carry
  its separate behavior or typed non-verified disposition.
