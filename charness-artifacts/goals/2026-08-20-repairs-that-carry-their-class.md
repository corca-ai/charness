# Achieve Goal: Cut the next Charness release without carrying its own failures

Status: active
Created: 2026-08-20
Activation: `/goal @charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: historical Slices 0–5 are locally proven and archived;
  the broader release goal remains active at its version, publication,
  external-readback, issue-closeout, current-open-issue qualification, and
  fresh-eye delivery edges. Issue #687 remains a release-cut exception with a
  Charness-owned prevention child and an explicitly unproven host-side
  dependency.
- Current slice: R2 — portable review-worker and delivery-state reliability;
  the file-backed default, consumer approval boundary, YAML CLI channel, and
  process-group timeout repair are committed. The installed/fresh-eye/release
  boundary remains open.
- Current slice intent: turn every observed wrong path, fail-open inventory,
  race, and dirty-proof result into an owning boundary with executable
  detection, while preserving source/export parity and refusing public-release
  claims from local proof.
- Next action: commit the semantic worker/delivery repair, regenerate the packet
  over the complete verdict-owning surface, rerun exact-target changed-line
  proof, then obtain the required round-2 fresh-eye read of the repaired
  verdict surfaces. Reproduce P0 #679 and run disjoint #682/#683/#685/#686
  lanes only after that repair boundary is clean; no version mutation yet.
  Round-1 worker delivery is proven, but its three verdicts are `block` and
  approval remains withheld.
- Large-slice rule: completed issue-level history remains auditable, but future
  work is scheduled by capability boundary rather than ticket count. Each macro
  slice owns one user-visible outcome and its shared contract; independent
  issue lanes run concurrently inside it, while the parent serializes ledger,
  exports, proof, version, and release truth surfaces.
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

The original shaping snapshot contains 30 open issues through `#681`. It already shows
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
| 0 | Recount/read every open issue; write and validate the canonical ledger; reproduce candidate blockers; persist release/quality planner receipts; commit the intake lock | “Maximum” needs an executable frozen set, not a ticket list | Exactly-once ledger and validator tests; version/tag/CI state; per-row current premise, acceptance owner, path budget, dependencies, proof, disposition; release candidates not assumed blockers | completed |
| 1 | Turn each qualified row into one work package; write the exact per-path owner table; split or serialize every overlap; create and doctor isolated writer worktrees | Scheduling labels are not code ownership, especially around critique, exports, and shared helpers | Approved path table including shared/generated/parent-only surfaces; worktree receipts; causal notes and focused commands per package | completed |
| 2 | Execute P0/P1 release-path packages first: `#679` and any live `#612/#668/#669/#667`; close focused proof and integrate each commit serially | A release train cannot compensate for a broken entrypoint or nondeterministic publication machinery | Supported-path, process-tree, timeout-attribution, runtime-semantic, and current mutation evidence; no unresolved reproduced blocker | completed |
| 3 | Execute every other qualified P2/P3/P4 package concurrently where path budgets are disjoint; integrate serially and run required proof-surface review rounds | This maximizes shipped repairs without pretending unlike issues share a design | Per-package regression/mutation/counterexample; lane closeout; generated impact; round records; parent integration proof | completed |
| 4 | Amend any disproved/cannot-ship rows; reconcile umbrellas/refutations; sync exports/generated docs; freeze and commit the integrated semantic candidate | Global proof needs a fixed semantic tree and truthful non-claims | Final ledger containing every frozen row exactly once plus separately identified blocker exceptions/amendments; source/export review; semantic candidate SHA | completed |
| 5 | Prove and critique the semantic candidate: changed-line first, then exact planner-required standing/release/broad gates; run the mandatory critique roster and conditional round 2 | Independent green packages do not prove composition; critique must read semantics before the bump obscures the diff | Gate logs/receipts; packet/fingerprints/round records; mutation proof; semantic verification lock. Any semantic repair returns to Slice 4 | completed with fresh-eye round 2 unproven |
| 6 | Re-run planner on the locked semantic candidate; select the bump; mutate version/export/release-record/note surfaces; commit the release candidate; run all planner-required post-bump checks, fresh-checkout/real-host probes, and publication dry-run on that exact commit | The release candidate is different from the pre-bump semantic candidate and owes its own proof | Version rationale/consistency; generated diff; release record; exact release-candidate SHA; post-bump lock; claims review; dry-run; tag target. Any semantic change returns to Slice 4 | not started |
| 7 | Publish only the locked release candidate; handle ambiguity through resume; perform hosted/public and separate install/update/doctor readback; then close only proven issues with post-release carriers; reconcile handoff and retro | The goal ends at externally verified release truth, not local green or tag creation | Remote/tag/release/install identifiers; same-proxy flags; issue comments/state readbacks; final ledger; handoff; Auto-Retro; complete closeout | not started |

## Replanned Release-Cut Macro Slices

The historical Slice 0–5 records remain the evidence ledger for work already
completed. This macro plan replaces the fine-grained pending Slice 6/7 schedule;
it is intentionally larger so parallel work advances a complete capability
boundary at once while parent-only truth surfaces remain serialized.

| Macro slice | Outcome | Parallel lanes | Parent-owned closeout | Status |
| --- | --- | --- | --- | --- |
| R1 — current-open qualification and contract freeze | Every live issue is freshly read and assigned an evidence-backed route; #687 has a durable Charness/host ownership split and a critique-ready implementation contract | #681 current requalification; #682 evidence-continuity; #683 reviewer-handoff; #685 persistence contract; #686 installed-path; #687 delivery boundary | Current-open manifest, ledger amendment(s), debug/spec artifacts, issue readback, path table, critique packet, and honest critique-delivery disposition | completed |
| R2 — evidence and delivery reliability | The release candidate carries the shared prevention pattern for wrong paths, lost delivery, commit-boundary evidence, and contradictory operator signals | Track A: delivery/evidence continuity (#682/#683/#687); Track B: CLI/installed-path contracts (#685/#686); #681 only after current requalification. Fake-host and installed-layout fixtures run concurrently after admission. | Parent integrates source/plugin exports, ledger carriers, generated docs, changed-line proof, and bounded fresh-eye rounds; any proof-surface repair triggers round 2 | in progress |
| R3 — candidate freeze, external truth, and issue closeout | One unchanged release candidate is selected, versioned, proven locally, installed/read back, published, and reconciled issue-by-issue | Planner/quality/release read-only probes and final issue reads fan out only after the candidate SHA is locked; publication, version surfaces, install/update, hosted readback, and closeout remain serialized | Candidate lock/post-bump proof; distinct install and hosted readback; per-issue behavioral carriers; post-close reads; handoff, retro, and final goal audit | pending |

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
  historical intake-lock refusal suite was `19 passed`; the current repaired
  focused suite is `24 passed` in
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
- Targeted verification: Focused: #639 22 passed plus ruff; #670's later catalog repair reports 133 decisions and 14 consumer-facing validators; #671 7 helper tests, 48 initial integrated tests, then 21 portability plus 71 related achieve tests after coverage repair. Standing pytest passed with consumer returncode 0. Integrated changed-line proof from 73cf9ce6a first blocked gate/helper branches, then reran clean with blocking=[] and consumer_returncode=0. Ledger, plugin links, staged mirror, and pursue-ready checks passed.
- Test duplication pressure: The first integrated changed-line proof exposed four unmeasured paths: sibling-loader refusal, evidence-section classification, unusable standalone disposition, and executable-reference enumeration. Those tests were added at the producer/consumer boundary, converting a green functional suite into measured changed-line coverage. A nonexistent test path was also attempted once and recorded as a command-surface smell.
- Critique: Two unnamed fresh-eye attempts for the integrated #671 verdict surface did not deliver findings and were shut down after boundary verification showed no undeclared drift. This is a delivery failure, not approval; #671 fresh-eye remains UNPROVEN and no same-agent substitute was used. The source/plugin boundary stayed clean.
- Off-goal findings: #679 sibling init-idempotence remains a named follow-up; external host/install, hosted readback, issue closeout, release publication, and Cautilus are not claimed. #672, #676, #677, and #678 moved into Slice 3; their worker worktrees are retained as receipts, while parent integration is serialized here.
- Lessons carried forward: Applied the standing structural rule: mirror drift became an explicit generated-surface integration step; validator under-enumeration became a fixed-scope catalog; portability helper-only work became a shared consumer gate; line-limit failure became a cohesive module split; changed-line failure became branch-specific tests; reviewer no-delivery stayed an explicit non-claim. Parallel isolated lanes remain the default.
- Metrics: Three lanes integrated; focused tests 22 + 10 + 7 initially and 21 + 71 after coverage repair; standing pytest pass; changed-line mapped files 3 with blocking []; plugin/source parity and ledger validation pass; #671 fresh-eye delivery unproven; Cautilus not run.

### Slice 3: parallel-proof-and-consumer-repairs

- Objective: Integrate the four disjoint P2/P3 lanes #672, #676, #677, and #678 while ensuring each detector distinguishes its named failure class and every helper has a real consumer.
- Why this approach: The lanes had independent path budgets and could be authored concurrently, but generated mirrors, ledger amendments, and closeout wiring belong to the parent. The parent therefore serialized only integration and truth-surface updates after parallel worker proof.
- Commits: worker results remain distinct from parent integration: #672 worker `2e840dc89` -> parent `c4b9c48c4`; #676 worker `df3c5a456` -> parent `f82dc7967`; #677 helper `d88c42595` -> parent `53cf7d618`, then consumer/ledger integration `d0e10a28b`; #678 worker `5820b7654` -> parent `d7973bc0a`. Later parent truth-surface repairs are `ef10a94ea`, `beecb5769`, `f6c4ed340`, `c8d4eefe1`, `0407e1338`, `e7fc1e6d8`, and semantic repair commit `b2f9a6407`; fallback coverage commits are `ff192f63a`, `63c3996c9`, and `9dbda5097`.
- What changed: #672 now uses parseable Python structure to distinguish value constraints and lookups from inert mentions. #676 exposes refusal/detector input classes through a non-blocking closeout advisory and negative controls. #677 syntactically checks changed durable-artifact citations, reports semantic blind spots, and is wired into slice closeout as reporting-only; a helper-only intermediate was explicitly amended to `partial-child-shipped` before being promoted after consumer readback. #678 separates adapter value readers from refusal-only/retired-key mentions through one AST usage classification.
- Alternatives rejected: Rejected source-only commits blocked by mirror drift, `--no-verify`, mechanically shaving files under the length bar, treating #677's unconsumed helper as complete, blocking historical artifact rewrites, and merging the distinct citation/class-detection engines without a shared false-positive policy.
- Structural failures and repairs: #676's first class-hint test included the mapping key `reason`; the classifier boundary was corrected. The length gate then exposed responsibility overload in both #676 and #678, so parity and AST usage were split into cohesive modules. The second fresh-eye round found a shared base-propagation gap, silent/crashing parity failure states, an ImportFrom alias false positive, five adapter/reference classifier blind classes, ledger premise/receipt drift, and issue/package proof drift; these were repaired at the shared consumer, parser, and validator boundaries. #672/#677/#678 worker commits initially hit the expected staged-mirror refusal; the parent regenerated and staged the derived plugin copies. A closeout plan first reported no scope without a committed-base selector, then `--paths` readback established the selected goal with `status=checked`, `issues=[]`, and `semantic_scope=syntactic-only`. The first integrated changed-line producer exposed a pre-existing standing JSON-stdout violation in the Slice 0 ledger CLI; the CLI now uses the shared YAML renderer, while the critique writer's intentional standalone JSON-as-YAML fallback is explicitly registered. Final changed-line retries then exposed an uncovered standalone import branch, an unbound fallback module in the test map, and four malformed-input fallback branches; each became a direct consumer/counterexample test before the clean proof.
- Targeted verification: #672 focused `24 passed`; #676 focused `12 passed` plus its secondary consumer suite `33 passed`; #677 focused `16 passed` with the supported-entrypoint proof still bound to the explicit campaign base; #678 focused `43 passed`. The pre-fallback focused/consumer bundle measured `201 passed`; the final reader-focused suite measured `26 passed`. Ledger validation, ruff, compile, and source/plugin sync passed. Final changed-line receipt (`/tmp/charness-s3-changed-line-final8.log`) is `status: clean`, explicit base `988f068f6`, `analyzed=10/changed=10`, `blocking=[]`, consumer return code `0`, resolved against code truth `1ee53a795`; standing pytest passed. Final release-only receipt (`/tmp/charness-slice-3-release-final2.log`) is `103 passed, 10749 deselected`.
- Test duplication pressure: The workers' green tests were not accepted as composition proof. Parent integration added a closeout consumer test, recorded the helper-only gap as an amendment, and preserved the distinction between syntactic citation presence and semantic truth/count claims. Length warnings remain visible as structural smells rather than being hidden by whitespace changes.
- Critique/non-claims: Round 1 code, consumer/export, and goal-claim findings are durably recorded and repaired. Round 2 code, consumer/export, and goal/ledger findings were delivered, recorded, and repaired; their repair set is accepted-unreviewed under the two-round cap, not a third-round approval. Boundary results are parent-attributed because the parent changed the shared checkout after the reviewer snapshots. Cautilus, hosted release, install/update readback, issue closure, and publication remain unrun. The #671 fresh-eye delivery failure remains explicitly unproven from Slice 2.
- Metrics: Four lanes integrated; lane proof is `24 + 12 + 16 + 43`, with #676 secondary consumer proof `33`; the pre-fallback combined focused/consumer bundle was `201 passed`, final reader-focused proof `26 passed`, changed-line is clean across all 10 mapped files, standing pytest passed, and release-only is `103 passed` with `10749 deselected`; #677/#678 premise commands match their receipts; package proof/path propagation is validator-enforced; generated source/plugin parity passes. External release, install/update, hosted readback, issue closeout, and publication remain open.

### Slice 4: slice-3-closeout-and-slice-4-entry

- Objective: Close the integrated Slice 3 repair lanes with durable proof, then move the active frame to the semantic-candidate freeze boundary.
- Why this approach: Slice 3 had focused, changed-line, standing, release-only, ledger, mirror, and pre-commit evidence; the next planned boundary is the fixed semantic tree required before version mutation.
- Commits: Semantic repair b2f9a6407; fallback coverage ff192f63a, 63c3996c9, 9dbda5097; proof-bound goal records 1ee53a795 and 7eb9b05bf. Lesson session 2026-08-20-goal-continuation is recorded in the repo-owned lesson ledger and receipt files.
- What changed: Promoted Slice 3 from locally proven to archived in the active frame; recorded the continuation lesson bundle; no new source mutation in this transition.
- Alternatives rejected: Rejected treating release-only green as a public release claim, skipping the lesson receipt because it dirtied the tree, or moving to version mutation before semantic candidate critique and fresh-checkout evidence.
- Targeted verification: check_goal_artifact.py --pursue-ready passed; check_release_issue_ledger.py passed for 30 issues and 10 packages; final changed-line receipt was clean across 10/10 files with standing pytest passing; release-only was 103 passed, 10749 deselected; final pre-commit and worktree checks passed.
- Test duplication pressure: No production tests were added in this transition. The prior Slice 3 fallback coverage repair is recorded as direct consumer and malformed-branch coverage; the lesson session itself is a durable evidence write and must be committed before release planning.
- Critique: Round-2 Slice 3 findings remain durably recorded and accepted-unreviewed under the two-round cap. The next critique target is the semantic candidate as a release boundary, with distinct source, gate, and fresh-eye channels.
- Off-goal findings: None. External publication, hosted/readback, install refresh, and issue closeout remain explicitly unclaimed.
- Lessons carried forward: Changed-line proof must follow the commit and precede broad/release work; a lesson-session write is part of the provenance surface, not incidental dirt; release planner freshness must be re-read after every source or evidence-surface mutation.
- Metrics: Current code truth before this transition: 1ee53a795; current documentation binding before this transition: 7eb9b05bf; current release surface remains 6.2.0; ledger 30 issues / 10 packages; worktree dirty only from the required lesson-session receipt.

### Slice 4 continuation: failure-smell and proof-surface repairs

- Objective: Repair the newly observed release-proof timeout class, close the
  integrated changed-line coverage gaps, and classify or remove duplicate seams
  before the semantic candidate is frozen.
- Why this approach: The failures were coupled at boundaries rather than being
  isolated red tests. The release wrapper owned a shorter timeout than its
  bounded children; two CLI entry paths duplicated the same child-process
  setup; and changed-line proof exposed unmeasured entry branches. The repairs
  therefore moved to the producer contract, shared runner seam, and direct
  consumer tests instead of weakening gates or merely recording exceptions.
- Commits: timeout repair `345ec2a7b`; consumer coverage `e00898cf9`; validator
  and lesson-hook entry coverage `69c1a3ec7`; shared child runner extraction
  `2ff21b39e`; reviewed duplicate-family classifications `b44d6df16`; closed
  timeout RCA and ledger event `e29735316`; parallel coverage-runtime
  isolation `d6381e3d5`; canonical lesson-routing test binding `933ac9f32`.
- What changed: The fresh-checkout producer explicitly opts out of the shared
  10-second alarm while retaining 120/300-second owned subprocess bounds, and
  its regression pins that policy. Session child execution now has one shared
  environment/process/timeout seam. Consumer tests exercise CLI guards,
  routing failures, fallback branches, and entrypoint paths. Twenty-six
  remaining intentional duplicate families are recorded with rationale; the
  one duplicated subprocess seam was structurally removed.
- Targeted verification: release focused tests passed; the exact default
  fresh-checkout proof returned `status: passed` with five probes and zero
  return codes; source/plugin mirror and spec/debug artifact validators passed;
  duplicate ratchet returned `new_code_families: []`, `hard_block: false`, and
  `status: clean`; real-host trigger evaluation over the full changed range
  returned `required: false`, `evaluation_scope: evaluated`, and no hits.
  Immutable changed-line proof at frozen source HEAD
  `2ff21b39e10a1ee1b2aaceae3b6d58263a792a5b` passed with 10,766 tests,
  `analyzed=20/changed=20`, and `blocking=[]`.
- Integrated quality exposed a parallel producer race: broad and focused
  coverage producers shared hidden runtime files. `d6381e3d5` namespaces those
  files by report stem and extends retention ownership; `933ac9f32` makes the
  focused mapper bind the canonical lesson-routing module. Focused mutation and
  retention suites passed, and the post-fix focused changed-line proof at
  `933ac9f32` passed 22/22 files with `blocking=[]`.
- RCA conversion: `charness-artifacts/debug/2026-08-20-fresh-checkout-probe-timeout.md`
  is resolved and `charness-artifacts/metrics/rca-ledger.jsonl` records the
  converted class `release-fresh-checkout-aggregate-timeout-boundary` with a
  gate and regression carrier.
- Critique/non-claims: Two unnamed bounded-reviewer spawn attempts were
  blocked by the host because no Agent/spawn/ceal capability was available;
  no fresh-eye approval is claimed and no same-agent pass substitutes for it.
  No version bump, tag, push, publication, hosted/install readback, issue
  closure, or Cautilus evaluation is claimed. The current code truth is
  `933ac9f32`; the release surface remains `6.2.0`.
- Lessons carried forward: A generic timeout applied across unlike producer
  workflows is a shared-contract smell; a green focused suite without changed
  lines is an evidence-measurement smell; and a ratchet exception without a
  family-specific rationale is a memory smell. Each now has a producer seam,
  direct coverage, or durable classification rather than a silent waiver.
- Continuity closeout: the two receipted lesson sessions are separately bound
  by `charness-artifacts/retro/2026-08-21-session-retro.md` and
  `charness-artifacts/retro/2026-08-21-goal-continuation-retro.md`; the
  continuity reconciler reports zero violations. The final release Auto-Retro
  remains pending until external release/readback work, so this does not flip
  the goal terminal status.

### Slice 4 continuation: integrated quality and critique boundary

- Objective: run the full integrated quality floor, refresh release-time probes,
  and bind the semantic-candidate critique before any version or publication
  mutation.
- Targeted verification: `run-quality.sh --read-only` passed `96 passed, 0
  failed` in 168.8 seconds; the changed-line producer passed concurrently after
  the report-stem runtime namespace repair. Fresh-checkout probes passed 5/5;
  duplicate ratchet remained clean with `new_code_families: []` and
  `hard_block: false`; real-host trigger evaluation over the full 234-path
  range returned `required: false`, `evaluation_scope: evaluated`, and no hits.
- Release planner: current version remains `6.2.0` and blockers are empty. Its
  planner-only fresh-checkout field is intentionally `not_established`; the
  direct five-probe packet above is the executed proof, not the planner listing.
- Critique boundary: packet
  `charness-artifacts/critique/2026-08-21-semantic-candidate-packet.json` is
  bound by SHA `5d2075b58d4742336f59bbf30c6eec6ea415d37b24af43d59c0cdbceeefdfb6e`
  and identity SHA
  `4d0d947e003c1a9d0621aebbb54c7308d12e14c9d20e4389bd09c4b799292858`.
  The durable critique record
  `charness-artifacts/critique/2026-08-21-semantic-candidate-release-critique.md`
  records the parent-delegated Codex retry and its Gawande/Minto/Raskin plus
  counterweight findings. The command-plan repair is separately bound to
  rounds 1 and 2, with round 2 reading the repaired surface and finding no
  blocker. No same-agent substitute or Cautilus evaluation is claimed.
- Public-skill scenario review: deterministic dogfood, conditional-read,
  scenario-registry, call-provenance, and proof validators passed; the five
  changed public skills remain mapped to their existing review/evaluator
  posture. The maintained `impl-adapter-bootstrap` scenario was inspected and
  no registry mutation was justified for this release/quality/evidence slice.
  Live Cautilus was not run because its policy remains ask-before-run and no
  log-backed evaluator proof was requested.
- Closeout advisories are dispositioned in the critique record: the moved
  `_added_diff_lines` helper has live import/test coverage; eleven added
  proof-surface candidates have explicit skipped/non-surface decisions because
  the host cannot provide fresh-eye review; and Floor-Addition Restraint keeps
  only the three recurring release-boundary floors (artifact citations,
  consumer-validator catalog, and issue ledger). No fourth blocking floor is
  being added.
- Command-surface failure is also treated as a smell: guessed validator/test/
  release paths, an unsupported release-reader flag, and an abbreviated ref
  all failed before their intended subject ran. The executable repair in
  `scripts/command_plan_preflight.py` resolves targets via `rg --files`,
  verifies refs with `git rev-parse --verify`, probes the resolved CLI owner
  with `--help`, checks long and short flags, and stops later probes after the
  first target/ref/owner/flag failure. The corrected five-target/full-ref
  preflight passed. Its first fresh-eye round found the continuation and short
  flag gaps; round 2 read the repaired verdict surface with no blocker, and the
  final two test additions are accepted-unreviewed under the two-round cap. The
  initial out-of-repo snapshot handoff refusal is preserved as a path-contract
  smell and was repaired with a repo-owned snapshot. The closeout's `177.71s`
  standing pytest runtime over the `120s` advisory budget is retained as a
  typed #668 runtime advisory, not re-leveled or claimed clean.
- Non-claims: no semantic-candidate lock, version bump, tag, push, publication,
  hosted/install readback, issue closure, or Cautilus evaluation.

### Slice 4 continuation: command-plan failure-smell repair

- Objective: make wrong path, ref, owner, and flag invocations fail before a
  parallel fan-out can escape, including the pattern where a failed preflight
  continues probing later commands.
- What changed: `scripts/command_plan_preflight.py`, its twenty-five focused regression
  tests, the parent parallel-execution contract, and the durable plan at
  `charness-artifacts/critique/command-plans/2026-08-21-goal-fanout.json`.
- Targeted verification: focused tests passed `25`; ruff, Python length, doc
  links, documented-command flags, critique-all, diff check, and the actual
  five-target/full-ref preflight passed. Round 1 found two structural gaps;
  the repaired surface was read in round 2 with clean boundary verification
  and no remaining blocker. The first owner-binding fresh-eye finding added a
  second structural repair round: `owner_target` now binds `argv` and
  `help_argv`, malformed commands refuse structurally, and relative plans
  resolve from `--repo-root`. The follow-up changed-line run is clean across
  `23/23` mapped files with `blocking=[]` at current proof HEAD
  `19e62aea8`; the new nested-token and expansion-error tests also discharge
  the changed-line blocking targets. The round-2 test additions are
  accepted-unreviewed under the repository's two-round cap. The exact line-274
  targeted-mutant result is preserved in
  `charness-artifacts/quality/2026-08-21-command-plan-targeted-mutant-proof.md`.
- Non-claims: the preflight does not run planned commands or prove runtime,
  installed, hosted, external, issue-closeout, publication, or Cautilus truth.

### Slice 4 integrated verification after command-plan repairs

- Current source truth: `19e62aea829e4d40b1ede2d1e2273ea067963dd1`.
- Changed-line proof: the serialized current-head receipt at
  `charness-artifacts/quality/2026-08-21-command-plan-changed-line-proof.md`
  is `clean`, with `23/23` changed-pool files covered, `blocking=[]`, and
  consumer return code `0` at the exact current HEAD.
- Broad quality: the durable receipt at
  `charness-artifacts/quality/2026-08-21-command-plan-broad-quality-proof.md`
  records `./scripts/run-quality.sh --read-only` passing `96` checks with
  `0` failures in `166.9s` at the same HEAD. Runtime remains advisory under
  #668; the result is not a claim that the budget is clean.
- Focused command-plan proof: the durable receipt at
  `charness-artifacts/quality/2026-08-21-command-plan-focused-proof.md`
  records `25 passed in 2.01s` at the same endpoint, with raw log SHA-256
  `7f9d2ecd409e3385f77b15ba55bc4fad2e689455be43610c3f7c46c9928aa0a4`.
- Verification lock: the durable receipt at
  `charness-artifacts/quality/2026-08-21-semantic-candidate-verification-lock.md`
  records the exact committed-range closeout at target HEAD `0784bb041` as
  `status: completed`, with `53` executed commands, `10,792 passed in 92.65s`,
  and broad proof fingerprint
  `dbcf626dd2ec1b8fae22730f508712ab9a4939efc1ace1e6b5b7ea10a0c5865c`.
- Fresh checkout: the corrected owner command
  `python3 skills/public/release/scripts/check_fresh_checkout_probes.py
  --repo-root . --run-probes --detail` passed all five declared probes.
- Execution-smell repair: an attempted concurrent changed-line/broad run
  produced a no-verdict coverage race because both producers share mutation
  state. The broad run was then rerun alone and the changed-line proof was rerun
  alone before it at the exact current HEAD; the final receipts above are
  serialized, not the raced run.
- Verification-smell repair: the first post-critique closeout refused a stale
  cached broad proof because the locked-diff fingerprint changed after commit
  `0784bb041`; the final mutation set was then refreshed explicitly. A separate
  `xargs` plan also put `--plan-only` after greedy `--paths`, and argparse
  refused it before execution. The corrected plan puts all flags before
  `--paths` and excludes untracked intermediate packets from the lock.

### Slice 5: consumer-validator-and-quality-boundary-repairs

- Objective: Carry the #670 catalog contract through source, exported package,
  consumer inventory, adoption decisions, closeout ownership, and proof timing;
  repair every wrong-path, cache/TMPDIR race, and false-green smell observed
  while integrating the slice.
- Structural repairs: the checker now resolves source versus installed layout
  through one helper, validates exact `python3 <plugin-root>/...` invocations,
  stable consumer IDs and metadata, catalog completeness, and exactly one
  `wired: true` or `opt_out_reason` decision. The capability CLI requires the
  adoption contract and returns nonzero for a blocked inventory. The staged
  gate requires the declaration in the index. The quality runner resolves
  relative TMPDIR from launch cwd, creates and canonicalizes an absolute base,
  and refuses repo-local temp state. Seed-cache pruning now owns a root lock
  across prune and entry-lock acquisition, with a cross-hash multiprocess
  regression. A dedicated `.agents/surfaces.json` surface owns the new
  declaration and its verifier; duplicate layout branches were collapsed and
  independent CLI families were explicitly classified.
- Wrong-call smells repaired: nonexistent critique packet and debug scaffold
  paths were corrected; the mirror checker name was corrected; a wrong spec
  patch anchor was abandoned for the debug artifact owner; source-layout and
  doubled-plugin paths passed to installed/source checkers were identified as
  refusals; and the nonexistent attention-state validator path explored by the
  reviewer was not treated as proof. A positional debug-artifact path passed to
  the `--paths` validator CLI was also rejected, then rerun with the declared
  flag. Focused repair authoring also corrected an undefined `ROOT` and an
  export-marker newline assumption. A guessed `current_release.py --detail`
  flag was also rejected by argparse; the planner's declared no-detail form is
  the valid call. A no-scope `check_real_host_proof.py --detail` call returned
  an empty evaluation scope and was rerun with the goal path, establishing
  `required: false` on an evaluated scope rather than misreading the empty
  result as proof. These are durable failure evidence, not incidental command
  noise.
- Focused proof: catalog/capability/CLI/packaging/staged tests and ruff passed;
  the latest combined focused catalog/capability/CLI/packaging/staged run was
  `161 passed`. Direct source and exported checker readback passed with `133`
  packaged validators, `133` decisions, `14` consumer-facing entries, `119`
  excluded, `13` declared wired, and `1` opt-out. Retry boundary fingerprint
  verified `clean` with `drift: []`.
- Integrated proof: the repaired `TMPDIR=/tmp ./scripts/run-quality.sh
  --read-only` completed `97 passed, 0 failed` in `278.7s`. Standing pytest
  passed in `139.4s`; changed-line mutation passed in `253.9s` with `32/32`
  changed pool files analyzed and no blocking lines; the debug seam index and
  inventory declaration checks passed. Focused repair coverage was `101 passed`.
- Fresh-checkout proof: the planner-required
  `check_fresh_checkout_probes.py --run-probes --detail` completed with
  `status: passed`, five declared probes, five `returncode: 0` results, and no
  blockers. This is local temporary-checkout evidence only; it does not
  establish managed install/update or hosted/public readback.
- Critique and delivery: round 1 fresh-eye returned BLOCK and its repair set
  is recorded at `charness-artifacts/critique/rounds/2026-08-21-consumer-validator-round-1.md`.
  The first round-2 reviewer and one unnamed retry failed to deliver a final
  report; the retry boundary was clean, but round 2 remains unproven rather
  than PASS or BLOCK. The delivery failures and host-only temp-path errors are
  recorded in the round-2 record. No same-agent substitute was used.
- Non-claims: no version bump, release-candidate commit, tag, push, public
  publication, managed install/update readback, hosted readback, issue closure,
  Cautilus evaluation, or runtime proof that every `wired` declaration is
  actually called is claimed. The semantic candidate must be re-bound after
  commit and after a delivered fresh-eye result.
- Metrics: 133 packaged decisions / 14 consumer-facing / 13 wired / 1 opted
  out; catalog focused `161 passed`; repair focused `101 passed`; integrated
  quality `97/97`; mutation `32/32` clean; dup-ratchet clean; source/export
  checker readback pass; fresh-eye round 2 delivery unproven.

### Slice 6: R2 continuation — portable reviewer worker consumer boundary

- Objective: Make the consumer unable to confuse a result medium, process success, or recovered transcript with delivered reviewer approval, while keeping the default review path file-backed and bounded.
- Why this approach: The first file-backed worker experiment reproduced two structural smells: the consumer had to reject a timed-out typed receipt without laundering it through a findings ledger, and a backend timeout needed to settle its descendant process tree rather than only the wrapper. The repair belongs at the worker, adapter, skill, and consumer boundaries together.
- Commits: The file-backed default and adapter/skill consumer contract are committed in `9b4ee5d40`; the follow-up worker output, process-group timeout, consumer tests, mirror, and RCA ledger repair are committed in `8a1bb8d89`. The slice proof base is the parent of `495af8a20`.
- What changed: The reviewer worker and delivery/report CLIs emit YAML on stdout while durable receipts, results, and ledgers remain JSON. A shared reviewer process module hard-kills and reaps the backend process group on timeout. The consumer report requires the typed worker schema, terminal succeeded status, fresh output hash/size, matching provenance, and findings-received approval state. Source and plugin mirrors stay synchronized.
- Alternatives rejected: Rejected typed-subagent waiting as the default consumer path and rejected treating a successful process, non-empty file, transcript recovery, or same-context critique as fresh-eye approval.
- Targeted verification: The original thirteen focused worker/consumer tests,
  the critique/prove consumer contract suites, and the adapter/packet/release
  ledger suites passed. The first exact-base changed-line run correctly blocked
  on five uncovered malformed/fallback branches; one counterexample was added
  per target, and the same producer now reports `status: clean`, six changed
  pool files, zero blocking targets, and standing pytest passed. A wrong test
  path, wrong source-layout path, and absent guessed gate-config path were
  recorded as command-surface smells rather than used as evidence. The broad
  pytest run was interrupted after 5,971 passes and had three failures, two
  stale closeout-packet failures and one worker JSON-stdout contract failure
  that this slice repaired; a complete broad rerun remains pending.
- Test duplication pressure: Direct counterexamples cover stale output, schema failure, finite timeout, child-process survival, success receipt without findings, timed-out receipt with findings, provenance mismatch, and matching typed approval. The worker/reporter integration remains separate from the consumer verdict logic.
- Critique: Round 1 fresh-eye findings were repaired. The round-2 file-backed worker attempt timed out before producing a bounded typed review; boundary verification was clean and the consumer report correctly returned approval_eligible=false. A separate bounded `claude -p` handoff review found ambiguous #679 ordering, unscoped changed-line proof, and missing semantic-rebind/version-hold steps; those baton defects were repaired. No fresh-eye code approval or same-agent substitute is claimed.
- Off-goal findings: No version bump, release candidate, tag, push, publication,
  hosted/install readback, issue closure, Cautilus evaluation, or external host
  runtime attribution is claimed. The changed-line receipt is now clean for the
  stated base and current resolved HEAD; it does not bind the semantic candidate
  or prove fresh-eye approval.
- Lessons carried forward: A consumer needs an explicit semantic approval gate, not merely a durable artifact carrier. A timeout contract must own the whole backend process group. Wrong default execution paths and wrong output channels are recurrence classes and belong in adapter/skill contracts plus executable tests.
- Metrics: Focused worker/consumer tests: 13 passed; critique/prove contract
  suites: 56 + 32 + 33 + 50; changed-line repair suites: 45 + 26; exact-base
  changed-line: clean across 6/6 files with blocking=[]; standing pytest passed.
  Staged closeout: 18 commands passed. Handoff review: typed PASS with the
  three baton defects repaired. Fresh-eye code delivery: unproven due typed
  worker timeout; approval correctly withheld. Handoff and goal refresh are
  pending commit.

### Slice 6 continuation: semantic approval-chain repair

- Objective: close the identity and mode seams found by the first delivered
  semantic fresh-eye round, so explicit subagent/worker contracts cannot be
  satisfied by a stale packet, foreign receipt, unbound result hash, or
  same-context substitution.
- Fresh-eye result: contract, delivery, and counterweight workers each returned
  schema-valid `codex_exec` reports through the typed receipt/ledger/report
  path. All three independently returned `verdict: block`; the reports are
  delivered evidence, not candidate approval. Durable round record:
  `charness-artifacts/critique/rounds/2026-08-21-r2-semantic-candidate-round-1.md`.
- Structural repairs committed in `0c76ff41c` (with the load-bearing critique
  contract wording retained in `7b5607fba`): receipt-to-attempt joins now carry packet,
  reviewed-input, mode/backend, prompt/schema, exit, and result identities;
  delivery CLI output is `delivery_complete` rather than approval; delivery
  history is replay-validated; result/receipt path aliases refuse; interruption
  cleanup covers the whole backend; the repo-owned runner/schema explicitly
  refuses the typed-subagent cross-over; and `worker-delivered` artifacts need
  a combined report carrier with packet/result identities.
- Targeted verification: 67 focused worker/delivery/validator tests pass;
  ruff, the repo-owned result schema check, and the full pre-commit closeout
  pass. The first post-repair exact-base attempt had no verdict because a
  load-bearing `rail-1 snapshot/verify` contract pin had been compressed away;
  after restoring it, the next attempt passed standing pytest but exposed three
  uncovered worker-delivery evidence branches. Counterexamples are now added;
  the same exact-base producer now returns `status: clean` for 7/7 changed pool
  files with `blocking: []`, resolved HEAD `7d15f1aef1dabd948ed1f71806294050348219e9`,
  and standing pytest passed in 52.4s. Receipt:
  `charness-artifacts/quality/2026-08-21-r2-semantic-repair-changed-line-proof-final.md`.
  The exact changed-line proof is now candidate-bindable; a new packet and
  round-2 fresh-eye review remain required before approval or release claims.
- Failure-smell memory: provider-invalid response schema, guessed delivery
  subcommands/flags, wrong ledger filenames, and mismatched round snapshot ids
  were all recorded as command-boundary failures and corrected through help,
  inventory, or schema validation. They are not omitted as operator typos.
- Round-2 fan-out exposed a second provider-schema class: Codex rejected the
  checked-in schema's nested `additionalProperties: true` objects before any
  reviewer response. The schema is now closed recursively in source and plugin
  mirrors, with a focused provider-strictness regression; this invalidates the
  prior packet binding and requires a new exact candidate proof and packet.
- Non-claims: no release/publication, install or hosted readback, typed host
  application, issue closure, version mutation, or fresh-eye approval of the
  repaired surface is claimed.

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

- `#687` — [Fresh-eye review delivery has no terminal path for interrupted
  subagents](https://github.com/corca-ai/charness/issues/687), filed before any
  Charness code change. The established unnamed one-shot request is a
  Charness-side mitigation for named mailbox routing. The Codex `Interrupted`
  path is recorded as a pinned source-level host hypothesis, not as runtime
  proof of every episode. R1 carries the Charness prevention child into this
  release and keeps the host fix open/non-claimed.
- `#681`–`#686` current-open refresh: the live set is captured in
  `charness-artifacts/issues/2026-08-21-current-open-surface.md`; #684 was
  re-read as closed and excluded. These rows enter R1/R2 only after their
  current reproducer, owner, path budget, proof, and release carrier are
  appended to the locked ledger rather than being silently folded into prose.
  #682/#683/#685/#686 are now bound as post-lock release-blocker exceptions;
  #681 remains the original `already-satisfied` row pending fresh consumer
  requalification.
- The R1 writer join barrier is
  `charness-artifacts/issues/2026-08-21-post-lock-path-table.md`. It keeps
  shared review-boundary files parent-serialized while allowing the retro
  persistence and installed-planner lanes to proceed in disjoint worktrees.
- `charness-artifacts/debug/2026-08-21-fresh-eye-interrupted-delivery.md` and
  `charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md` are the
  durable RCA/contract handoff for #687. The current debug interrupt is
  `handoff-recorded` only for the stated artifact paths; it does not discharge
  the missing delivered fresh-eye result.
- The R1 spec-critique attempt is recorded at
  `charness-artifacts/critique/rounds/2026-08-21-fresh-eye-delivery-spec-attempt.md`.
  Earlier angle findings consumed a stale packet identity, and the replacement
  spawn was rejected with `agent thread limit reached`; this is unproven
  delivery, not critique approval. The spec now includes explicit transition,
  provenance, late-result, R1/R2/R3 gate, and exact-test-path requirements, but
  the current packet delivered a BLOCK whose findings are recorded as repair
  input; its approval is quarantined because the parent wrote during the review
  window. A clean second round remains required.
- R2 now owns a portable Charness worker envelope and delivery ledger. It does
  not import or depend on CEAL: CEAL's workbench runner is only an external
  reference for failure classes, while Charness owns its own stale-artifact,
  schema, timeout, cwd, atomic-publish, and typed-receipt contract.

## Final Verification

- Slice 3 local proof is complete at code truth `1ee53a795`: semantic repair
  commit `b2f9a6407`, fallback import coverage `ff192f63a`, direct fallback
  mapping `63c3996c9`, and malformed-branch coverage `9dbda5097`. The final
  explicit-base changed-line receipt is clean across all 10 mapped files with
  standing pytest passing; release-only is `103 passed, 10749 deselected`.
- The final commit after that receipt is documentation-only: it binds this
  receipt and does not alter the source mutation pool.
- Slice 0 local intake proof remains recorded in the ledger, planner receipts,
  issue-read/reproduction receipts, and Slice 0 log. Integrated semantic
  candidate critique and verification lock are complete at the target commit;
  version/release-candidate proof, external readback, and tracker closeout
  remain unrun, so this goal is still active.
- Historical Slice 4 integrated proof remains recorded at code truth
  `5a170113d`, with the command-plan implementation repairs at `7b277c3d0`,
  coverage completion at `c29d338d8`, and diagnostic repair at `3cc29d5ea`.
  The latest exact-HEAD verification is now recorded at
  `19e62aea829e4d40b1ede2d1e2273ea067963dd1`: default fresh-checkout probes
  passed (5/5), the changed-line receipt is clean across `23/23` files, and
  the durable broad receipt records `96 passed, 0 failed`; the focused
  command-plan receipt records `25 passed`. The v9 replacement packet and
  final fresh-eye round read this synchronized candidate evidence. The parent
  boundary fingerprint was clean (`ok: true`, `verdict: clean`, `drift: []`),
  and the exact post-critique verification lock completed at target HEAD
  `0784bb041` with `10,792 passed`. The semantic candidate is locally locked;
  version mutation, publication, external readback, issue closure, and
  Cautilus remain unrun.

## User Verification Instructions

- After publication, follow the release skill's maintainer install/update path,
  confirm the installed version, run the public bootstrap and discovery smoke
  paths selected in Slice 0, and compare their output with the release record.
  Exact commands remain R3 output because the qualified public surface and
  current-open amendments are not yet frozen.

## Auto-Retro

- Slice 4 session retros are persisted and goal-bound at
  `charness-artifacts/retro/2026-08-21-session-retro.md` and
  `charness-artifacts/retro/2026-08-21-goal-continuation-retro.md`.
  Complete the final release retro after release readback and before goal
  closeout; include
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
4. Current GitHub source of truth for the original 30-issue shaping snapshot
   through `#681`, read with bodies and comments through the resolved `gh`
   issue backend on 2026-08-20; the live refresh is
   `charness-artifacts/issues/2026-08-21-current-open-surface.md`.
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

12. Slice 3 bounded fresh-eye records and snapshots: round-1 code, consumer/export,
    and goal-claim records plus round-2 code, consumer/export, and goal/ledger
    records under `charness-artifacts/critique/rounds/`; round-2 repairs are
    explicitly accepted-unreviewed under the two-round cap.
13. Continuation lesson session `2026-08-20-goal-continuation`: frozen selection
   bundle and emission receipt at
   `charness-artifacts/retro/lesson-session-receipts/2026-08-20-goal-continuation.md`
   and `.json`; the repo-owned lesson ledger records its snapshot hash.
14. [#687](https://github.com/corca-ai/charness/issues/687), its issue-first
    body readback, the round-2 retry record, and the pinned adjacent Codex
    source inspection. These establish separate named-channel and interrupted-
    terminal hypotheses; they do not establish an episode-level host trace.
15. [Current open surface refresh](../issues/2026-08-21-current-open-surface.md)
    and [fresh-eye delivery debug](../debug/2026-08-21-fresh-eye-interrupted-delivery.md)
    — R1 intake and causal evidence.
16. [Fresh-eye delivery boundary spec](../spec/2026-08-21-fresh-eye-delivery-boundary.md)
    — R2 implementation contract, pending bounded critique.

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

**Over-Worry (rejected).** Do not force every open row into one universal code
bundle, create a universal scanner/meta-validator, pull newly opened
non-blockers into the locked train without qualification, or mass-close
umbrellas. Evidence qualification plus the R1/R2 macro slices preserves the
user's broad mandate better than a ticket quota.

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
