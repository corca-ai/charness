# Achieve Goal: Cut the next Charness release without carrying its own failures

Status: active
Created: 2026-08-20
Activation: `/goal @charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: active Slice 0 qualification complete; the activation
  snapshot, planner receipts, ledger, and clean changed-line proof are locked.
- Current slice: Slice 0 — issue-source snapshot, current reproductions, ledger,
  and ledger-validator proof. No writer lane is admitted before this lock.
- Current slice intent: freeze one honest release backlog, distinguish blockers
  from independently shippable repairs and premise-refuted reports, then launch
  disjoint work lanes without weakening the release floor.
- Next action: prepare isolated writer lanes from the admitted package path
  table, starting with the release-blocker lane.
- Target version: undecided until the Slice 0 qualified set and the integrated
  Slice 4 surface are read by the release planner. `6.3.0` is the shaping
  forecast because likely lanes add public discovery/evidence capability; use
  the lightest honest bump and record the rationale in the release record.
- Intake lock: Slice 0 owns the activation-time open-issue snapshot. After its
  ledger commit, newly opened issues join this train only when they reproduce
  against the release candidate and block build, install, update, or a claimed
  public workflow. Everything else is successor backlog.
- Verification cadence: reproduce before design; focused proof in each lane;
  commit each semantic repair before changed-line proof; serialize integration,
  export sync, broad quality, version mutation, and publication in the parent
  checkout.
- Gate cadence: lane commits use focused checks plus
  `run_slice_closeout.py --skip-broad-pytest`; the integrated pre-release tree
  runs changed-line proof before standing/release/broad gates; the frozen
  semantic candidate receives the pre-bump critique; version/export/release-
  record mutation creates a distinct release candidate which must be committed
  and re-proven before publication dry-run or external probes.
- Slice review packet: include the frozen issue ledger, causal claim, changed
  source/export surfaces, acceptance mapping, focused and mutation proof,
  known blind class, non-claims, and the question whether the repair reproduces
  the failure class it is meant to remove.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`, and
  `## Auto-Retro`.

## Goal

Cut the next Charness release after repairing every activation-time open issue
that is both live and acceptance-ready, with release-path failures first and
with no issue counted as fixed merely because it was grouped into the train.

The capability being delivered is a trustworthy release train, not a quota of
closed tickets. At activation, every open issue receives one evidence-backed
disposition: **release blocker**, **qualified repair**, **premise refuted or
already satisfied**, **operator decision required**, or **deferred with a named
missing input**. Every release blocker must be resolved or disproved. Every
qualified repair must be implemented and independently proven. The final
release may leave issues open only when their ledger row explains why shipping
does not make a claim about them.

The shaping snapshot contains 29 open issues through `#680`. It already shows
four kinds of work that should not be forced through one implementation seam:
consumer bootstrap and portability, release/quality determinism, evidence
lifecycle, and semantic inspection. Those become isolated authoring lanes with
separate causal reviews and tests. The parent checkout alone integrates lane
commits, regenerates the plugin export, runs global gates, mutates version
surfaces, and publishes.

Known first priorities are the reproducible `#679` installed-consumer bootstrap
false-red and the pending live release probes for `#612`, `#668`, and `#669`.
The latter become blockers only when Slice 0 reproduces a current supported-path
failure with release impact; historical CI comments alone do not qualify them.
Priority does not imply a predetermined fix. The active run must reproduce each
claim and may refute or narrow it. `#680`, for example, is not currently a
release blocker: zero packet sections are independent of reviewed-input
identity, and the observed packet binds six explicit paths by content hash.
Its original causal claim is therefore premise-refuted at the shaping HEAD;
only a separately proven reader-visibility defect may qualify. This refutation
is scoped to shaping HEAD `38775dfeb` and the observed Ceal packet's six explicit
reviewed paths/content hashes; it is not a universal critique-packet verdict.

## Non-Goals

- No promise to close all open issues. Broad umbrellas, product choices,
  historical reports without a live reproducer, and reports whose premise is
  refuted receive durable dispositions rather than speculative code.
- No single universal scanner for `#599`, `#672`, `#676`, `#677`, and `#678`
  unless Slice 0 proves a shared input model, predicate, result schema, and
  false-positive policy. Similar vocabulary is not a reusable contract.
- No weakening or skipping of CI, mutation, changed-line, release-only,
  publication, or fresh-eye proof to make the release fit the session.
- No concurrent edits to plugin exports, version surfaces, `.charness` state,
  baselines, the Git index, or the release record. These are parent-owned
  single-writer surfaces.
- No Cautilus evaluation. It remains eval-only and ask-before-run; this release
  grant does not authorize it.
- No unrelated roadmap or product redesign for `#527`, and no invented
  acceptance criteria for an operator-owned choice.
- No claim that local export tests prove an installed cache, hosted tag, GitHub
  release, or maintainer update until the corresponding external readback runs.

## Boundaries

- **Snapshot boundary.** Recount all open issues with bodies and comments at
  activation into
  `charness-artifacts/issues/2026-08-20-next-release-ledger.json`. Freeze it
  after Slice 0, subject only to the release-blocker intake exception in the
  Active Operating Frame. GitHub remains source of truth; the ledger is a bound
  snapshot, not a replacement tracker.
- **Qualification boundary.** A repair lane needs a current reproducer or
  executable failing contract, a causal claim, user-visible acceptance, an
  owning test surface, and a closeout carrier. Missing any one means the issue
  remains deferred or decision-required rather than silently entering code.
- **Bug boundary.** Every bug-class issue routes through `charness:debug`
  before design and `charness:issue` before tracker close. A moved or disproved
  premise is a legitimate outcome.
- **Parallel boundary.** Read-only qualification may fan out. Every writer gets
  an isolated worktree and a disjoint path budget. A writer may not start until
  the parent records every allowed path, shared dependency, generated/export
  owner, and forbidden parent-only path. Any overlap returns to parent
  serialization before authoring; “coordinate later” is not an allowed state.
  Default `scripts/*_lib.py`, `skills/shared/**`, plugin exports, generated
  manifests, version files, release records, `.charness/**`, and any test shared
  by two packages to parent-only/serialized until the path table explicitly
  reassigns one. Reassignment must still leave exports/version/index parent-owned.
- **Proof-surface boundary.** Any change to code that renders a verdict about
  other code or artifacts receives a bounded fresh-eye review. If round 1
  causes repairs, round 2 reads the repaired surface; the cap is two rounds.
- **Release boundary.** No version mutation until all claimed lanes are
  integrated, the issue ledger is reconciled, and pre-release gates are green.
  No tag/push/publish until dry-run, critique, release record, and required
  external probes are bound to the unchanged release commit.
- **External grant.** The user's 2026-08-20 instruction to fix as much as
  possible and cut the release is the phase-scoped grant for the final bundled
  version bump, tag, push, and release publication. It applies only to the
  unchanged **post-bump release candidate** whose SHA is locked after Slice 6
  checks and dry-run. It is revoked by `--no-verify`, a weakened floor, narrowed
  proof, or material post-proof mutation.
- **Issue closure boundary.** Closing a qualifying issue is standing-approved
  only after its issue closeout floor: fresh source-of-truth read, acceptance-
  to-proof map, resolution critique, durable carrier, behavior verdict, and
  post-close readback. A release does not mass-close unresolved issues.
- **Locked-row amendment boundary.** A qualified row may leave or change the
  candidate only through an appended ledger amendment naming the new source or
  reproducer, old and new disposition, owner, missing/failed proof, successor
  destination, and release-scope impact. `cannot-ship` is an explicit result;
  an incomplete lane never silently disappears from the maximum-work claim.
  If `cannot-ship` follows a writer commit, exclude/revert that package before
  Slice 4; a half-proven commit cannot remain in the semantic candidate.
- **Stop boundary.** Stop and ask the operator only for a genuinely product-
  defining choice. Missing historical evidence, a refuted premise, or a lane
  that cannot clear its own proof becomes a typed disposition and does not
  indefinitely hold the release, unless it blocks the release path itself.
- **Failure states.** A failed or downgraded required changed-line, mutation,
  broad, release-only, fresh-checkout, or real-host check forbids version/tag/
  push until repaired and re-locked. Any post-lock mutation invalidates the lock.
  An ambiguous push switches only to the release resume/ambiguous workflow—do
  not run ordinary publish again. A post-publication readback failure means
  `published, external proof incomplete`; do not close dependent issues or mark
  the goal complete.

## Execution Runbook

This section is deliberately prescriptive because the activation session may
run a lower-capacity model. Do not replace an explicit branch below with a broad
refactor. When current evidence disagrees, record a ledger amendment and follow
the stop/requalification rule instead of guessing.

### Slice 0 commands and ledger contract

1. Load `charness:achieve`, `charness:issue`, `charness:quality`, and
   `charness:release`; open the repo lesson session before any reviewer spawn.
2. Run `python3 skills/public/issue/scripts/issue_tool.py plan --repo-root .
   --intent resolve`, then read every selected issue through `issue_tool.py read
   --repo corca-ai/charness --number <N> --repo-root .`. The script output, not
   this shaping prose, supplies current `updatedAt`, body, and comments.
3. Run `python3 skills/public/release/scripts/plan_release_run.py --repo-root .
   --detail` and `python3 skills/public/quality/scripts/plan_quality_run.py
   --repo-root . --detail`. Persist their unedited outputs under
   `charness-artifacts/release/` and `charness-artifacts/quality/`; do not infer
   commands or blocker semantics that the planners did not declare.
4. Write `charness-artifacts/issues/2026-08-20-next-release-ledger.json` with
   top-level `schema_version`, `repo`, `captured_at`, `head_sha`, `issue_count`,
   `list_truncated`, `release_planner_receipt`, `quality_planner_receipt`, and
   `issues` plus `work_packages` (multiple packages may reference one issue,
   such as the two independent `#669` reports). Each issue row must contain:
   `number`, `url`, `title`, `state`, `updated_at`, normalized body/comments
   SHA-256, `premise` (`verdict`, exact command, exit, evidence path),
   `classification`, `release_impact`, `acceptance_owner`, acceptance assertions,
   `lane_id`, allowed paths, dependencies, proof commands, release-content
   carrier, close disposition, and append-only `amendments`. `classification`
   is closed to `release-blocker`, `qualified-repair`, `premise-refuted`,
   `already-satisfied`, `decision-required`, `deferred`,
   `partial-child-shipped`, or `cannot-ship`; `close_disposition` defaults to
   `leave-open`. A qualified package's `release_content_evidence_path` is
   repository-relative, while `post_publication_closeout_path` stays null until
   post-release evidence exists.
5. Add `scripts/check_release_issue_ledger.py` plus focused tests **in the parent
   checkout**. It refuses a
   truncated snapshot, duplicate/missing activation issue, unknown enum, a
   qualified row missing reproducer/owner/acceptance/proof/path budget, a blocker
   without release impact, overwritten amendment history, and an exception row
   without a reproduced post-lock release blocker. This validator checks shape
   and internal coverage only; it must say that GitHub freshness is re-read.
   This is a verdict/proof surface: bind a packet to source, tests, fixtures, and
   ledger; obtain bounded fresh-eye review before the intake-lock commit; if
   round 1 causes repairs, round 2 reads the repaired surface.
6. Preserve each planner receipt as raw output plus command, HEAD SHA, timestamp,
   and exit code; the ledger points to these immutable files rather than a prose
   summary. Commit the goal, ledger, planner receipts, and reviewed validator as
   the intake lock.
   No writer worktree starts before that commit and the Slice 1 path table.

Before an issue is closed, re-read it and compare `updatedAt` plus normalized
body/comments identity to the locked row. Any difference requires requalification
and an amendment even when the new comment appears supportive.

### Admission decision table

| Observed state | Ledger disposition | Next action |
| --- | --- | --- |
| Current supported path fails, impact reaches this release, acceptance/test owner exists, path budget is disjoint | `release-blocker` or `qualified-repair` | Assign one writer package below |
| Reproducer passes or cited behavior is already prevented | `premise-refuted` / `already-satisfied` | Record command/output and do not edit code |
| Historical evidence exists but the current behavior cannot be reproduced | `deferred` with `defer_reason: missing-current-reproducer` | Preserve evidence and successor trigger; do not keep retrying |
| Public semantics or compatibility policy must be chosen by the operator | `decision-required` | Block only if release-critical; otherwise successor disposition |
| Focused implementation invalidates the causal claim or cannot clear required proof | `cannot-ship` amendment | Revert/exclude the lane commit, name failed proof and successor; never erase row |
| Issue is umbrella/duplicate but a bounded child ships | `partial-child-shipped` | Link child carrier; keep umbrella open unless its own acceptance is met |

### Work packages and fixed decision branches

Each bullet is a separate sub-lane until Slice 1 proves identical allowed paths.
The issue clusters in the Slice Plan are scheduling queues, not permission to
invent a common engine.

- **P0 — `#679`, impl bootstrap.** Read `skills/public/impl/SKILL.md`, its
  exported mirror, `scripts/adapter_init_lib.py`, and existing adapter-init tests.
  First reproduce three temporary-consumer states and record exact exit/output
  plus byte/stat baselines: missing adapter, valid customized adapter, invalid
  adapter. Then add `tests/quality_gates/test_impl_bootstrap_contract.py`
  encoding that baseline. Prefer a state-aware documented path: resolver `found:false` permits
  init then resolve; `found:true,valid:true` skips init; invalid refuses without
  mutation. Change shared init semantics only if the full consumer inventory
  proves that is smaller. Byte- and stat-compare the valid adapter; never make
  `--force` a normal next action. Sync and run the exported path too.
- **P1 — `#669a`, signal orphaning.** For orphan reaping, start at `scripts/subprocess_guard.py`,
  `scripts/standing_pytest_run_record.py`, and
  `tests/quality_gates/test_standing_pytest_run_execution.py`. The preferred
  branch records termination in the signal handler and lets the monitored phase
  reap after `Popen` binds its pid; do not raise from an arbitrary C-call window.
  The regression must repeatedly deliver SIGTERM around spawn and prove the
  grandchild marker/process group disappears.
- **P1 conditional — `#669b`, planner timeout attribution.** This is a separate
  work-package row referencing the newest `#669` comment and qualifies only if
  Slice 0 reproduces it independently from the signal race. Start at
  `skills/public/release/scripts/plan_release_run.py` and
  `tests/quality_gates/test_public_skill_yaml_output_contract.py`: preserve a
  typed nonzero timeout verdict and make the contract test report timeout rather
  than “malformed YAML.” Do not merely raise 10 seconds without planner evidence.
- **P1 — `#668`, runtime budget semantics.** Start at
  `.agents/quality-adapter.yaml`, `skills/public/quality/scripts/check_runtime_budget.py`,
  runtime-budget helpers, and `tests/quality_gates/test_runtime_budget_gate.py` /
  `test_runtime_budget_unenforceable.py`. Do not relevel the wall-time number.
  First prove isolated versus contended wall time on the same commit. Then select
  the smallest honest contract: correctness/release lanes treat wall time as
  advisory; a blocking performance regression needs a subject-controlled metric
  such as CPU work and its own calibrated evidence. This changes gate verdict
  semantics and therefore owes the conditional second review round.
- **P1 — `#612`, mutation regression watch.** Re-read the newest workflow comment
  and reproduce the current sampler/baseline through the quality-planner command.
  Historical uncovered files or stale baseline failures are not a current code
  todo. If current HEAD is green, record hosted current evidence and classify
  already-satisfied/monitoring; if red, fix only the named current baseline,
  changed-line, abnormal-worker, or surviving-mutant cause and rerun the same
  sample. Never suppress the summary's blocking signal to close the issue.
- **P1 — `#667`, cross-repo specialized release state.** Qualify only when a
  local fixture can represent the specialized lane and the generic planner's
  false `not releasable` verdict. Keep external repo policy out of Charness; the
  Charness carrier is a planner/adapter contract test or the row defers.
- **P2 — `#635`, lesson citation producer.** Select the producer repair, not a
  weaker retro reader: `achieve` must write the opened lesson `session_id` and
  frozen `bundle_path` into the goal's Context Sources/active record. Update the
  public skill/reference/template and exported mirror through normal sync; add a
  goal lifecycle test proving retro can recover the cited bundle without newest-
  file guessing. Do not duplicate the mutable bundle contents into the goal.
- **P2 — `#638`, durable critique rounds.** Add one per-round artifact under
  `charness-artifacts/critique/rounds/<date>-<window-id>.md` immediately when
  findings return. Required fields: packet path/SHA and reviewed-input identity,
  reviewer/delegation tier exposure, boundary window id, fingerprint verdict,
  findings verbatim enough to preserve categories, parent dispositions, repair
  commit, and next-round input. The next round must consume the prior record;
  closeout cites it rather than recreating it. Extend critique validation and
  tests. Serialize with `#637` if their registry/validator paths overlap.
- **P2 — `#639`, lesson-session ownership timing.** Start at
  `scripts/session_start_lesson_context.py`, session-start routing, and
  `tests/test_session_start_lesson_context.py`. Surface every unclaimed session
  at session start with session id, bundle path, opener evidence if known, and
  honest claim/disposition command; keep push-time continuity as a backstop.
  Do not auto-score a stranger's session. Also refuse reserved id `none` in the
  suggestion path. Warning versus blocking remains planner/adapter-owned; no
  new start blocker without operator policy.
- **P3 — `#672`, reader classification.** In `scripts/what_reads_this.py`, add an
  assertion/value-constraint classification before generic string literal and
  port lookup recognition for `.get("k")`/`["k"]` where symbol/config-key modes
  currently diverge. Extend `tests/test_what_reads_this.py` so
  `scripts/eval_setup.py:220` and the fixture assertion at the current test lines
  cannot share the same kind. State AST-scanned literals and aliased/getattr
  loaders as blind classes unless separately implemented.
- **P3 — `#678`, adapter reader versus refuser.** In
  `scripts/adapter_key_registry.py`, classify structural value reads separately
  from membership/refusal checks. Populate the three retired prose-budget keys
  only after tests show a key whose only sites refuse resolves `retired`, a real
  value read resolves `reader`, mixed sites are reported honestly, and
  `audit_registry` agrees. Extend
  `tests/quality_gates/test_adapter_key_registry.py`; do not treat literal
  presence as semantic use. The separate `validate_adapters.py` coverage gap is
  another row/amendment, not an untested fold.
- **P3 conditional — `#676`.** Before design, reconstruct the corpus from repair
  commits `a12ba86f5`, `9e88ebbcd`, and `0e9b52e64` plus the predecessor goal and
  resolution critiques; bind each of the six issue-table instances to exact diff
  hunks/symbols. If any instance lacks an exact semantic anchor, defer. If the
  corpus holds, build a slice-closeout advisory over added refusal/detector code,
  with one positive per instance and negative controls for ordinary validation,
  generation, exception cleanup, and multi-hop call graphs. It is advisory first;
  no blocker promotion in this release.
- **P3 conditional — `#677`.** Keep separate from `#676`. Parse citations only in
  durable Markdown under declared artifact roots; check path existence, line
  range, and nearby identifier token. Explicitly report semantic truth/counts as
  out of reach. Run path-scoped at slice closeout, grandfather historical corpus,
  and require fixtures for moved lines, nonexistent paths, prose numbers/URLs,
  code fences, and a real-but-semantically-false citation.
- **P4 — `#637`, installed critique preflight.** Start at
  `scripts/check_artifact_surface_preflight.py` and
  `tests/quality_gates/test_check_artifact_surface_preflight.py`. Resolve scaffold
  and validator from the same declared installed/package owner. An unavailable
  renderer is a typed non-pass/unproven state, never a PASS accompanied by an
  unqualified warning. Prove repo and installed export layouts.
- **P4 — `#670`, consumer-facing validator discovery.** Introduce a canonical,
  exported catalog that distinguishes consumer-facing validators from internal
  self-checks and supplies stable id, packaged path, purpose/artifact type,
  invocation, and adoption policy. Add a catalog self-check that every declared
  path ships. Expose the catalog in the documented doctor/inventory surface and
  support a consumer declaration with exactly one of `wired` or non-empty
  `opt_out_reason`; a newly declared consumer validator missing from both is the
  regression. Do not report all ~125 `check_*`/`validate_*` scripts as consumer
  obligations. This additive public capability is the main minor-bump trigger.
- **P4 — `#671`, goal path portability.** Extend goal artifact validation and
  `tests/quality_gates/test_goal_artifact_portability.py`. Portable executable
  roots use repo-relative/logical names. When an absolute POSIX/Windows path is
  present, require a `## Path Portability` row classifying it as evidence-only or
  an explicit machine-bound root with host mapping/existence proof; pursue-ready
  refuses undeclared host-specific paths and names each occurrence. Include two
  host-root fixtures and avoid rejecting URLs or illustrative placeholders.
- **P4 conditional — `#634`.** Re-run `check_export_self_sufficiency.py` and its
  tests, then enumerate the still-live four blind families from the latest issue
  comment: cwd-relative Markdown/YAML instructions, shell gates, docs JSON
  readers, and third-party imports. Qualify/fix each family as a separate row and
  test arm. Do not convert the existing advisory path-literal arm to blocking
  until fixtures distinguish “reads its own export tree” from “scans the caller's
  supplied root.” Preserve the already-shipped dependency-contract repair.

### Explicit non-work packages

- `#680`: refuted for the observed explicit-path packet. Add only a Markdown
  reviewed-path visibility test if a current user-path reproducer establishes
  that narrower defect; never make zero sections itself fail closed.
- `#546/#586/#605/#587`: no implementation without the current reproducer named
  in the ledger. `#605`'s newest inventory is 199 wired calls and zero trims;
  `#586` is explicitly deferred; `#546` has synthetic-only missing samples.
- `#527/#550/#582/#583/#584/#599/#601/#628`: extract a bounded child only when
  Slice 0 supplies current acceptance and a disjoint carrier. Do not close the
  umbrella from a child or spend the release inventing product policy.

## User Acceptance

1. **The whole backlog is accounted for.** The activation-time issue ledger
   lists every open issue exactly once and passes
   `python3 scripts/check_release_issue_ledger.py --repo-root . --ledger
   charness-artifacts/issues/2026-08-20-next-release-ledger.json`. New blocker
   exceptions are separately marked; no row is overwritten by an amendment.
2. **Release-path failures cannot hide behind unrelated green tests.** `#679`
   and every still-live build/install/update/release blocker are reproduced
   from their supported entrypoint, fixed without destructive routine advice,
   and proven through the source and shipped/exported surface where applicable.
3. **All acceptance-ready work ships.** Every issue marked `qualified repair`
   at the Slice 0 lock has a causal note, focused regression, mutation or
   counterfactual proof, changed-line verdict, fresh-eye result where required,
   and an issue-specific release-content carrier in the tagged commit. After
   publication, issue closure uses a separate closeout comment/record linking
   immutable release evidence, distinct behavior proof, and post-close readback;
   the tagged content commit contains no issue close keyword. It may carry a
   repository-local evidence draft, but the validated closeout carrier/comment
   is created only after publication, distinct-channel behavior proof, and
   install readback.
4. **Parallelism does not reduce evidence.** Lane work occurs only in verified
   isolated writer worktrees with disjoint ownership. The parent records the
   integration order, re-runs affected focused tests after each integration,
   and proves the combined tree rather than adding independent green receipts.
5. **The release candidate is coherent.** Source skills, exported plugin,
   generated manifests/docs, CLI references, version surfaces, and release
   notes agree on the same candidate. No dirty or untracked semantic change is
   omitted from the release record.
6. **The quality floor remains honest.** The checked-in quality/release planner
   receipts enumerate the exact required commands and blocking/advisory
   semantics for the semantic candidate and post-bump release candidate.
   Changed-line proof precedes broad quality; no planner-required blocking
   command is skipped or piped through output-truncating filters. A static list
   in this goal cannot override a newer planner receipt.
7. **Publication and behavior use distinct channels.** Hosted/public readback
   proves final commit, tag, release, and version visibility. A fresh checkout
   separately proves packaged install plus the documented `charness update` and
   doctor behavior. A probe sharing the release backend is flagged
   `same-proxy`, not counted as independent confirmation. Identifiers and
   outputs are recorded in Final Verification.
8. **Remaining issues tell the truth.** Every issue left open after the release
   has a final ledger disposition that says what is missing or refuted and why
   the selected release version makes no closure claim. Umbrellas are updated
   only when their shipped
   child evidence actually changes their state.
9. **The repair train does not carry its class.** The mandatory critique roster
   covers every changed verdict/proof surface, one repaired user path per writer
   lane, parent integration/export sync, version/release record, package install/
   update path, and one counterexample for each issue-specific predicate.
   Reviewers additionally sample for false-red startup, orphaned subprocesses,
   contention-sensitive verdicts, unbound evidence, reader/refuser confusion,
   and source/export drift. Anything outside the roster is recorded as residual
   risk rather than implied covered.

## Agent Verification Plan

### Low-Cost Checks

- Run `issue_tool.py` reads with comments and
  `recount_premise_state.py --with-bodies --limit 200`; reject a truncated or
  duplicate ledger.
- Run the release and quality planners before mutation and save their receipts;
  verify current version surfaces and latest tag before selecting the bump.
- For each qualified bug, record the exact failing command and exit/output
  baseline before editing, then run the focused regression after every edit.
- Run Ruff on changed Python/tests, source/export parity for changed skills, and
  the smallest owning validator in each lane.
- At every lane commit run
  `python3 scripts/run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`.
- Snapshot/verify reviewer boundaries around every bounded review. Quarantine a
  result if worktree, index, or HEAD integrity fails.

### High-Confidence Checks

- After each parent integration, run all focused tests from that lane plus any
  directly dependent lane; do not rely on the source worktree receipt alone.
- Sync generated/exported surfaces once the semantic integration set is fixed,
  inspect the diff, and exercise the exported public paths.
- After the integrated semantic commit, run
  `prepush_focused_changed_line_coverage.py --refuse-unestablished` before any
  broad lane and preserve its per-file verdicts.
- Run standing pytest, repository Ruff, release-only pytest, public-skill
  validation/dogfood, mutation checks selected by the quality planner, and the
  broad quality command without piping away failures.
- Run one bounded release-candidate critique across the committed issue ledger,
  repairs, exports, release notes, and non-claims. Apply the second-round rule
  separately to repaired verdict surfaces.
- Before version mutation, re-run the release planner against the integrated
  tree. Then run version sync/check, generated-manifest check, publication
  dry-run, packaging checks, and post-mutation gates required by the planner.

### External Or Live Proof

- Run planner-required fresh-checkout probes in temporary isolated checkouts;
  prove bootstrap/update/install behavior from the packaged candidate rather
  than the developer checkout.
- After the immutable candidate is green, publish under the scoped grant, then
  read back remote commit, tag, GitHub release, and public version metadata
  through a distinct hosted/public channel.
- Refresh the maintainer-installed plugin using the documented update path and
  record the installed version/readback. Do not treat checked-in export parity
  as this proof.
- For each closed issue, read back its final state and closing carrier. Record
  failures as incomplete external proof rather than a local success.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Recount/read every open issue; write and validate the canonical ledger; reproduce candidate blockers; persist release/quality planner receipts; commit the intake lock | “Maximum” needs an executable frozen set, not a ticket list | Exactly-once ledger and validator tests; version/tag/CI state; per-row current premise, acceptance owner, path budget, dependencies, proof, disposition; release candidates not assumed blockers | not started |
| 1 | Turn each qualified row into one work package; write the exact per-path owner table; split or serialize every overlap; create and doctor isolated writer worktrees | Scheduling labels are not code ownership, especially around critique, exports, and shared helpers | Approved path table including shared/generated/parent-only surfaces; worktree receipts; causal notes and focused commands per package | not started |
| 2 | Execute P0/P1 release-path packages first: `#679` and any live `#612/#668/#669/#667`; close focused proof and integrate each commit serially | A release train cannot compensate for a broken entrypoint or nondeterministic publication machinery | Supported-path, process-tree, timeout-attribution, runtime-semantic, and current mutation evidence; no unresolved reproduced blocker | not started |
| 3 | Execute every other qualified P2/P3/P4 package concurrently where path budgets are disjoint; integrate serially and run required proof-surface review rounds | This maximizes shipped repairs without pretending unlike issues share a design | Per-package regression/mutation/counterexample; lane closeout; generated impact; round records; parent integration proof | not started |
| 4 | Amend any disproved/cannot-ship rows; reconcile umbrellas/refutations; sync exports/generated docs; freeze and commit the integrated semantic candidate | Global proof needs a fixed semantic tree and truthful non-claims | Final ledger containing every frozen row exactly once plus separately identified blocker exceptions/amendments; source/export review; semantic candidate SHA | not started |
| 5 | Prove and critique the semantic candidate: changed-line first, then exact planner-required standing/release/broad gates; run the mandatory critique roster and conditional round 2 | Independent green packages do not prove composition; critique must read semantics before the bump obscures the diff | Gate logs/receipts; packet/fingerprints/round records; mutation proof; semantic verification lock. Any semantic repair returns to Slice 4 | not started |
| 6 | Re-run planner on the locked semantic candidate; select the bump; mutate version/export/release-record/note surfaces; commit the release candidate; run all planner-required post-bump checks, fresh-checkout/real-host probes, and publication dry-run on that exact commit | The release candidate is different from the pre-bump semantic candidate and owes its own proof | Version rationale/consistency; generated diff; release record; exact release-candidate SHA; post-bump lock; claims review; dry-run; tag target. Any semantic change returns to Slice 4 | not started |
| 7 | Publish only the locked release candidate; handle ambiguity through resume; perform hosted/public and separate install/update/doctor readback; then close only proven issues with post-release carriers; reconcile handoff and retro | The goal ends at externally verified release truth, not local green or tag creation | Remote/tag/release/install identifiers; same-proxy flags; issue comments/state readbacks; final ledger; handoff; Auto-Retro; complete closeout | not started |

## Backlog Recount

- Counted: 30 open issues from the non-truncated GitHub snapshot at
  `charness-artifacts/issues/2026-08-20-open-issues.raw.json`, captured at
  `2026-08-20T18:47:02+09:00` from HEAD
  `b9e89480904d16c586c3b1769f81cac3d3a7f214`. Every row has a read receipt with
  comments and normalized body/comment digests.
- Current classification: 1 `release-blocker` (`#679`); 9
  `qualified-repair` (`#635/#638/#639/#670/#671/#672/#676/#677/#678`); 3
  `already-satisfied` (`#634/#637/#681`); 1 `premise-refuted` (`#680`); 1
  `decision-required` (`#668`); and 15 `deferred` rows with a named missing
  reproducer or bounded child. The structured ledger and validator own these
  counts; this paragraph is only an index.
- Evidence: the ledger is
  `charness-artifacts/issues/2026-08-20-next-release-ledger.json` and passes
  `python3 scripts/check_release_issue_ledger.py --repo-root . --ledger
  charness-artifacts/issues/2026-08-20-next-release-ledger.json`; its focused
  refusal suite is `19 passed` in
  `tests/quality_gates/test_release_issue_ledger.py`.
- Claims: only the blocker and admitted work packages enter implementation.
  `#679` reproduces the valid-existing-adapter false red; `#668` remains an
  operator decision because the current runtime budget passes; `#612/#669` are
  deferred after current focused checks pass; and `#680` remains scoped to the
  shaping-head refutation. No row is a closure claim.
- The 10 admitted work packages are path-budgeted in the ledger. Their future
  implementation still owes causal notes, focused proof, changed-line proof,
  and the mandated fresh-eye review; admission is not completion.
- Intake lock: ready for commit after Slice 0 proof. Round-2 repairs are
  explicitly accepted-unreviewed under the bounded two-round cap; no third
  reviewer round is claimed.

## Operator Decision Queue

- No decision is required before activation. The operator chose the broad
  release-train shape and authorized the final release boundary.
- During execution, queue only choices that change public product semantics or
  accept a lasting compatibility tradeoff. Mechanism choices, premise
  refutations, lane drops for missing evidence, and ordinary implementation
  tradeoffs remain agent-owned and must be documented.
- If a release-critical issue requires an unresolved operator decision, pause
  before candidate freeze. A non-critical decision-owned issue receives a typed
  successor disposition and does not block the release.

## Coordination Cues

- Phases: qualify and lock -> parallel isolated authoring -> serial integration
  -> integrated proof -> version/release preparation -> publish/readback/close.
- Routing: `charness:achieve` owns the living goal; `charness:issue` and
  `charness:debug` own issue truth and causal review; relevant implementation
  skills own lanes; `charness:quality` plans the gate floor; `charness:prove`
  closes each slice; `charness:release` owns version/publication; `charness:retro`
  closes the work unit.
- Parallelism: parent may fan out read-only issue qualification. Writers use
  `charness worktree create ... --prepare` and
  `charness worktree doctor --require-isolation`; the parent alone touches
  exports, version state, index, integration commits, and release state.
- Gather: n/a for tracker reads handled by the issue backend. Any new public URL
  used as durable design evidence routes through `charness:gather` first.
- Release: target undecided; `6.3.0` is a forecast only. The final planner and
  version policy decide at Slice 6 from the actual shipped surface. Publication
  grant is scoped in `## Boundaries`.
- Issue closeout: close only rows proven in the final release commit and read
  each state back. Leave premise-refuted, umbrella, and decision-owned rows open
  unless their own closeout contract is independently satisfied.
- Successor goal: seeded only from the final ledger's explicit deferred rows;
  no automatic carry-over of a detector or umbrella.

## Discuss Before Activation

- Discuss before activation: resolved — on 2026-08-20 the operator rejected a
  narrowed `#679`-only draft and requested a large, properly designed next-
  session goal that fixes as much as safely possible and cuts a release.
- Consequential defaults fixed here: activation-time full backlog with a Slice
  0 intake lock; release blockers first; all acceptance-ready rows mandatory;
  isolated parallel writers and serialized integration; planner-selected honest
  bump (`6.3.0` only a forecast); final
  version/tag/push/publication grant limited to the unchanged proven candidate;
  no Cautilus.
- Proof non-claim: the shaping triage is not the Slice 0 ledger, the issue
  groupings are not closure claims, and the planned version is not final until
  the release planner reads the integrated surface.

## Slice Log

### Slice 0: activation qualification and intake ledger

- Objective: Qualify the activation-time open issue snapshot, preserve immutable planner and issue-read receipts, and validate an exactly-once ledger before writer lanes begin.
- Why this approach: The release train needs a structured admission boundary so current blockers, qualified repairs, premise refutations, decisions, and missing-input deferrals cannot be laundered through a ticket list or prose count.
- Commits: Intake lock committed as `911f730dd`; proof-repair commit `a7678ad3e` added the missing executable rejection-path coverage. Round 1 fresh-eye review returned seven false-pass classes and round 2 returned six more; both repair sets were recorded before the intake-lock commit, with round-2 repairs explicitly accepted-unreviewed under the two-round cap.
- What changed: Activated the goal; captured the 30-issue GitHub snapshot and all issue reads with comments; preserved issue, release, and quality planner receipts; recorded current reproductions; added the thin CLI `scripts/check_release_issue_ledger.py`, cohesive evidence and contract modules (`scripts/release_issue_ledger_evidence.py` and `scripts/release_issue_ledger_contract.py`), and focused tests; generated charness-artifacts/issues/2026-08-20-next-release-ledger.json; updated the live backlog recount; then bound raw snapshot hashes/order, source identity metadata, typed dispositions, post-lock exceptions, amendment roots, and issue/package path budgets. The length-gate failure exposed a monolith as a structural smell, so the validator was split by responsibility instead of suppressing the gate.
- Alternatives rejected: Rejected a #679-only train, a fixed ticket quota, and a prose-only backlog table. The ledger keeps all 30 rows while admitting only 10 path-budgeted work packages.
- Targeted verification: python3 scripts/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json -> pass (30 issues, 10 work packages); `pytest -q ./tests/quality_gates/test_release_issue_ledger.py` -> 25 passed; Python length and py_compile checks passed. Changed-line proof passed cleanly at `a7678ad3e` for `scripts/check_release_issue_ledger.py`, `scripts/release_issue_ledger_contract.py`, and `scripts/release_issue_ledger_evidence.py` (blocking: `[]`; consumer return code: `0`). The first run blocked on 3 files, the second exposed five residual paths while dirty, and the final run passed after structural coverage repair.
- Test duplication pressure: Focused tests cover truncated snapshots, raw snapshot substitution/digest drift, source receipt substitution, duplicate or missing issue coverage, enum refusal, typed admission floors, blocker impact, amendment-root overwrite, post-lock exceptions, freshness non-claims, and path overlap/parent-only violations. The validator's semantic truth and GitHub freshness blind classes remain explicit.
- Critique: Round 1 bounded reviewer returned and boundary verification was clean. It found snapshot/source identity, admission, exception, amendment-root, path-budget, and schema-binding gaps; all are repaired. Round 2 bounded reviewer returned cleanly at the boundary, found receipt-content, placeholder, timestamp, parent-path, boolean-number, and exception identity/time gaps; those repairs are locally verified and accepted-unreviewed under the two-round cap.
- Commit-gate smell and repair: the first commit attempt passed code gates but failed staged plugin-mirror drift because the new validator modules were absent from the generated install surface. Regenerated `plugins/charness` and both marketplace manifests, then included those derived surfaces in the same lock attempt.
- Off-goal findings: No implementation lane started. The #668 operator decision and deferred historical or umbrella rows remain open in the ledger.
- Lessons carried forward: Applied changed-line-proof-before-broad-quality, positive-effect-cannot-be-cited, detector-blind-class-unstated, goal-closeout-evidence-binding, prose-claim-without-a-reader, bar-recorded-as-prose, green-test-is-not-covered-line, global-probe-for-local-fact, proof-surface-message-drift, and the operator rule that every failure is a smell requiring a structural pattern or pattern-of-patterns repair.
- Metrics: Activation set: 30 rows; release blockers: 1; qualified repairs: 9; admitted packages: 10; already satisfied: 3; premise refuted: 1; decision required: 1; deferred: 15; focused ledger tests: 25 passed; fresh-eye round 1: repairs required and repaired; round 2: repairs required, locally verified, accepted-unreviewed; changed-line proof: clean across 3 mapped files.

### Slice 1: parallel-admitted-repairs

- Objective: Ship the first three independent post-lock repair lanes: #635, #638, and the release-blocking #679.
- Why this approach: These lanes had current evidence, disjoint budgets, and the release path or a repeated durable-evidence failure; isolated authoring and parent-owned integration preserved maximum parallelism without sharing writer state.
- Commits: #635 source/test lane 4c16bd05d was mirror-synced and integrated as 7427617c1; #638 source/test lane 082534276 was mirror-synced and integrated as 516678c4a; #679 test lock 10772a9a7 and shared implementation 1479811f1; changed-line repair for #638 7c060b5a1.
- What changed: #635 now carries the exact lesson-session session_id and frozen bundle_path into achieve's durable Context Sources. #638 records immutable reviewer round findings bound to window, snapshot digest, and findings digest, with a non-overwriting next-round carrier. #679 classifies valid existing adapter state through the resolver before the shared writer refusal, preserving missing scaffolding, invalid refusal, explicit force, and bytes/stat immutability; source and generated plugin mirrors were synchronized by the parent.
- Alternatives rejected: Rejected source-only commits blocked by mirror drift, --no-verify, routine --force, ignoring the false red, and an impl-only duplicated validity parser. The shared helper received an optional resolver-owned classification seam; sibling init consumers remain an explicit follow-up rather than hidden scope expansion.
- Targeted verification: Focused proofs: #635 1 passed; #638 5 passed after the first integrated changed-line run exposed 18 unmeasured exception paths; #679 4 passed plus 14 related adapter tests. Source/plugin valid-existing smoke both returned `unchanged`; missing returned 0; invalid returned 1 without overwrite; explicit --force overwrote in a temporary fixture. Integrated changed-line proof from b54f7850a is clean across scripts/adapter_init_lib.py, skills/public/critique/scripts/record_round_findings.py, and skills/public/impl/scripts/init_adapter.py; standing pytest passed with consumer returncode 0. Packaging and plugin-link checks passed.
- Test duplication pressure: The first green #638 focused suite was not enough: subprocess-only happy/error coverage left the shared recorder's refusal branches unmeasured. In-process tests now exercise malformed/missing snapshots, path/date/window validation, unreadable/empty/non-UTF-8 findings, write failures, round bounds, and renderer fallback. This records the pattern that an error contract must be measured at the producer, not merely observed through a subprocess.
- Critique: Two unnamed fresh-eye delivery attempts for #679 produced no findings within the allowed wait and were shut down; boundary verification was clean both times. Fresh-eye correctness review for #679 is therefore UNPROVEN and is not claimed as a pass. The prior Slice 0 validator review remains separate and complete; no same-agent substitute was used.
- Off-goal findings: #679's sibling init-idempotence family remains a named follow-up; installed-cache, external-host, hosted release, issue closeout, and release publication are not claimed. #668 and the deferred/refuted rows remain outside this slice.
- Lessons carried forward: Applied the standing rule that each failure is a smell: mirror drift became parent-owned integration, the shared existence-only decision became resolver-based classification, and changed-line blockage became executable in-process exception coverage. Also applied parallel isolated writers, commit-before-proof, and source/plugin parity as a single truth surface.
- Metrics: Three admitted lanes integrated; focused tests 1 + 5 + 4 (plus 14 related adapter tests); integrated changed-line mapped files 3, blocking []; standing pytest pass; source/plugin smoke pass; fresh-eye #679 delivery unproven; Cautilus not run.

### Slice 2: parallel-admitted-runtime-repairs

- Objective: Ship the next independent repair lanes #639, #670, and #671 while preserving the failure-as-smell rule and parent-owned integration boundaries.
- Why this approach: Three lanes had current evidence and disjoint worker budgets. Isolated worktrees let lesson-session routing, validator enumeration, and goal-path portability advance concurrently; parent serialization was reserved for generated mirrors and the missing #671 consumer wiring.
- Commits: #639 worker 20d09d732 integrated as 73cf9ce6a; #670 worker 6acd71ea0 integrated as 5c9192af1; #671 helper 2e752fddf integrated as 352ed2e7c, consumer wiring ee04dd391, coverage repair 449a32162.
- What changed: SessionStart now routes unclaimed lesson sessions through the canonical retro planner without claiming or silently treating routing failure as empty. Quality ships an explicit packaged consumer-validator catalog with a fixed scanner boundary. Achieve classifies absolute checkout-root paths, preserves intentional evidence, and shares one masked portability gate across check_goal and pursue_readiness.
- Alternatives rejected: Rejected --no-verify, source-only commits blocked by mirror drift, pure #671 helper completion without a live consumer, filesystem existence as portability proof, and mechanically shaving goal_artifact_lib below its hard limit. The #671 gate was split into a cohesive sibling after the length gate exposed responsibility accretion.
- Targeted verification: Focused: #639 22 passed plus ruff; #670 10 passed, 132 decisions and 13 consumer-facing validators; #671 7 helper tests, 48 initial integrated tests, then 21 portability plus 71 related achieve tests after coverage repair. Standing pytest passed with consumer returncode 0. Integrated changed-line proof from 73cf9ce6a first blocked gate/helper branches, then reran clean with blocking=[] and consumer_returncode=0. Ledger, plugin links, staged mirror, and pursue-ready checks passed.
- Test duplication pressure: The first integrated changed-line proof exposed four unmeasured paths: sibling-loader refusal, evidence-section classification, unusable standalone disposition, and executable-reference enumeration. Those tests were added at the producer/consumer boundary, converting a green functional suite into measured changed-line coverage. A nonexistent test path was also attempted once and recorded as a command-surface smell.
- Critique: Two unnamed fresh-eye attempts for the integrated #671 verdict surface did not deliver findings and were shut down after boundary verification showed no undeclared drift. This is a delivery failure, not approval; #671 fresh-eye remains UNPROVEN and no same-agent substitute was used. The source/plugin boundary stayed clean.
- Off-goal findings: #679 sibling init-idempotence remains a named follow-up; external host/install, hosted readback, issue closeout, release publication, and Cautilus are not claimed. #672, #676, #677, and #678 are admitted for the next parallel slice; their worktrees are prepared but not yet integrated.
- Lessons carried forward: Applied the standing structural rule: mirror drift became an explicit generated-surface integration step; validator under-enumeration became a fixed-scope catalog; portability helper-only work became a shared consumer gate; line-limit failure became a cohesive module split; changed-line failure became branch-specific tests; reviewer no-delivery stayed an explicit non-claim. Parallel isolated lanes remain the default.
- Metrics: Three lanes integrated; focused tests 22 + 10 + 7 initially and 21 + 71 after coverage repair; standing pytest pass; changed-line mapped files 3 with blocking []; plugin/source parity and ledger validation pass; #671 fresh-eye delivery unproven; Cautilus not run.

## Closeout Binding Plan

- Reviewed inputs: this goal, the frozen issue ledger and amendments, current
  issue reads, release/quality planner receipts, per-package causal notes/tests,
  source/export/generated diffs, and release-record claims. Critique/retro/lock
  records are terminal evidence, not semantic inputs.
- Frozen target: first commit and bind the integrated semantic candidate for
  critique; after the planner-selected version mutation, commit and separately
  bind the exact release candidate. Any semantic repair returns to Slice 4 and
  invalidates both downstream bindings.
- Fresh-eye: bounded read-only reviewers consume the packet and durable prior-
  round records. Reviewer code/artifact inspection is distinct from the parent's
  executable gates; fresh-checkout install/update and hosted readback are further
  distinct external channels. Same-proxy observations are flagged.
- Verification lock: use `python3 scripts/run_slice_closeout.py
  --verification-lock`; preserve named failure logs/receipts plus the exact
  planner command outputs. Any input, version, generated, or release-record edit
  after a lock requires the matching stage to re-bind and re-run.
- Complete flip: record semantic and release packet identities, reviewer round
  records/fingerprints, both verification locks, public/install readbacks,
  per-issue closeout readbacks, and Auto-Retro; only then change terminal status
  and bookkeeping outside the reviewed identity.

## Off-Goal Findings

- None during shaping. Record newly discovered work here unless it meets the
  post-lock release-blocker exception.

## Final Verification

- Not due. Slice 0 local intake proof is recorded in the ledger, planner
  receipts, issue-read/reproduction receipts, and Slice 0 log. Integrated
  semantic proof, release-candidate proof, external readback, and tracker
  closeout remain unrun.

## User Verification Instructions

- After publication, follow the release skill's maintainer install/update path,
  confirm the installed version, run the public bootstrap and discovery smoke
  paths selected in Slice 0, and compare their output with the release record.
  Exact commands remain Slice 6 output because the qualified public surface is
  not yet frozen.

## Auto-Retro

- Not started. Complete after release readback and before goal closeout; include
  lane/integration waste, findings that changed the candidate, and any workflow
  repair that should become a successor issue.

## Context Sources

1. [Design north star](../../docs/design-north-star.md) — wrong answers need a
   distinct observer and evidence channel at irreversible boundaries.
2. [Handoff](../../docs/handoff.md) — current repository state and the existing
   commit-then-changed-line-before-broad cadence.
3. [Operating contract](../../docs/conventions/operating-contract.md),
   [implementation discipline](../../docs/conventions/implementation-discipline.md),
   and [parallel execution](../../docs/conventions/parallel-execution.md) —
   issue, critique, worktree, integration, proof, and external-boundary rules.
4. Current GitHub source of truth for all 29 shaping-snapshot issues through
   `#680`, read with bodies and comments through the resolved `gh` issue backend
   on 2026-08-20.
5. Current source at shaping HEAD `38775dfeb`, including the `impl` bootstrap,
   release subprocess/runtime budget paths, critique packet identity, adapter
   registry, and relationship inspection code cited by the current issues.
6. The release planner at version `6.2.0` / latest tag `v6.2.0`, plus the
   release version, critique, publication, install-refresh, and real-host proof
   references loaded while shaping this draft.
7. The quality planner and its quality-lens, surface-contract, operability,
   public-skill, and ergonomics references. Slow/broad gates remain serialized;
   quality-contract changes route through report-first qualification.
8. The declared lesson bundle for shaping session
   `2026-08-20-01a01e68-fafb-7fc1-b27c-51a1bc88014b`, especially changed-line
   proof before broad quality, green tests not proving changed lines, premise
   truth over debt labels, and detector blind-class disclosure.
9. [Broad release-goal critique packet](../critique/2026-08-20-broad-release-goal-packet.md)
   — bound the pre-review broad draft. Packet SHA-256
   `40aa51c64150d200bb705fe7dbacad7f3a34965bf4833fea06b1adfc8d6b264a`;
   reviewed-input identity
   `7901708d62e714d9f2be5cc2f9ee4706a3887013cabee91b553dc43040c04191`.
   The final post-repair packet identity is appended after the execution-
   readiness pass.
10. Execution-readiness packets
    [round 1](../critique/2026-08-20-release-goal-execution-readiness-packet.md)
    (`packet 0bdb9f1d7d66a21a8f8363fd6a98f01a0ab0fbd774f2383723006bad10f87792`,
    `identity 4bcb8d6790dc6dcfa945b04638911bb79f5e50af9a5a1c37230e61e85b314165`)
    and [round 2](../critique/2026-08-20-release-goal-execution-readiness-r2-packet.md)
    (`packet 9b83e3e271d60161f8a327bc85903d147450cb42a9613315ad457b1165355250`,
    `identity 9b0c39187efb03c78b6e41937163325b46029b2d7598cc7425ed0c824680798f`)
    bind the lower-capacity execution runbook before and after its repairs.
11. [Handoff misunderstanding packet](../critique/2026-08-20-release-handoff-packet.md)
    bound this goal and `docs/handoff.md` together (`packet
    9afc2b1beb2216ed01fc528fc4231d29ec774f05cf45e1ea116e15508821eb26`,
    `identity 41a81f04b407a53957b24a7a654eb6a7743e610e8f4f15cbfbb33878f466e7f6`).

## Interview Decisions

**Mode:** artifact-only. Nothing executes until the activation command.

1. **Scope family.** Options: `#679` only; a fixed hand-selected batch; the
   activation-time backlog with qualification and intake lock. Chosen: full
   qualified backlog. `axis: premise/acceptance readiness` — broad scope is
   bounded by evidence, not ticket count.
2. **Priority family.** Options: issue number order; easy wins first; release
   path first, then all qualified independent lanes. Chosen: release path first.
   `single-point: ability to cut an honest release`.
3. **Execution family.** Options: one sequential mega-diff; concurrent shared
   checkout; isolated lane authoring with serial integration. Chosen: isolated
   lanes and parent integration. `axis: ownership/integration risk`.
4. **Release family.** Options: local fixes only; fixed patch/minor now;
   planner-selected honest bump. Chosen: planner-selected. `6.3.0` is a shaping
   forecast because candidate lanes include additive public discovery/evidence
   capability; a fix-only integrated surface selects patch instead.
5. **Closure family.** Options: mass-close at publish; close by issue evidence;
   never close. Chosen: per-issue closeout and readback. `axis: tracker truth`.
6. **Intake family.** Options: chase every new report indefinitely; freeze at
   activation; freeze with a release-blocker exception. Chosen: blocker
   exception. `axis: moving target versus knowingly broken release`.
7. **External effects.** The user's release-cut request grants final bundled
   version bump, tag, push, and publication, subject to the unchanged-candidate
   and proof floor. It does not grant Cautilus or unrelated external actions.
8. **Timebox.** No work budget was supplied. “Maximum” therefore means every
   Slice 0 qualified row, not an arbitrary count or a weakened end-of-session
   cutoff. `single-point: no budget supplied`.
9. **Executor capacity.** The operator said the active goal will be run by a
   lower-capacity model. Chosen response: pre-bind file/test entrypoints,
   preferred branches, prohibited shortcuts, ledger schema, failure states, and
   integration order in `## Execution Runbook`; current evidence may still
   override them only through the explicit amendment path.

## Plan Critique Findings

Target: spec critique. Execution: two contrasting bounded reviewers ran in
parallel over the broad release draft, followed by a separate counterweight
pass. Fresh-Eye Satisfaction: parent-delegated. Packet Consumed: item 9 under
`## Context Sources`. All three findings were received. The host exposes no
typed `bounded-reviewer` envelope, so parent-side boundary fingerprints were
used; the two parallel windows verified with only the parent's declared goal-
file edit, and the counterweight window verified clean.

**Act Before Activation (accepted).** Remove the premature fixed `6.3.0`; split
the pre-bump semantic candidate from the post-bump release candidate and reprove
the latter; make the issue ledger canonical and exactly-once validated; require
per-path ownership before writer start; make lane drops append-only amendments;
separate tagged release-content carriers from post-publication issue closeout;
let planner receipts own exact blocking commands; and spell out failed,
ambiguous-push, and external-readback-incomplete states.

**Bundle Anyway (accepted).** Treat lane names only as scheduling queues; scope
`#680` refutation to the observed HEAD and six explicit paths; distinguish
hosted visibility from fresh-checkout install/update behavior; re-read issue
`updatedAt` before close; and make the critique roster exact without creating a
cross-product of every generic defect against every lane.

**Over-Worry (rejected).** Do not force all 29 rows into code, create a universal
scanner/meta-validator, pull newly opened non-blockers into the locked train, or
mass-close umbrellas. Evidence qualification preserves the user's broad mandate
better than a ticket quota.

The operator then added that a lower-capacity model will execute the goal. The
post-critique `## Execution Runbook` is the accepted response: it fixes commands,
schemas, entry files/tests, decision branches, forbidden shortcuts, and package
ordering while preserving premise-driven amendments. Execution-readiness round 1
found six load-bearing ambiguities: reproduce-before-test ordering, fixed-version
residue, grant candidate identity, close-carrier timing, the two `#669` subclaims,
and proof-surface review for the new ledger validator. It also fixed closed enums,
raw planner receipts, parent-only defaults, and `cannot-ship` exclusion.

Round 2 confirmed those repairs and found one remaining executor-stop
contradiction: the table used compound classification
`deferred-missing-current-reproducer` outside the closed enum. The final repair
uses `classification: deferred` plus `defer_reason:
missing-current-reproducer`. That one-line round-2 repair is
`accepted-unreviewed`; no further design choice remains hidden in it.

The final handoff misunderstanding reviewer consumed Context Sources item 11
and returned clean: the first action is the repo-owned lesson-session command,
then this artifact's activation command, then Slice 0 only. It found no path to
the obsolete `#676`-only shape, pre-lock writers, a forced minor bump, Cautilus,
or premature publish/issue closure. Its boundary fingerprint verified clean.
