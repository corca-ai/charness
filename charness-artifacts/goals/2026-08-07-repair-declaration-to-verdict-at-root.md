# Achieve Goal: Repair the declaration-to-verdict boundary at its root, as a generative sequence

Status: active
Created: 2026-08-07
Activated: 2026-08-07
Activation: `/goal @charness-artifacts/goals/2026-08-07-repair-declaration-to-verdict-at-root.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 1 — make one declared field answerable: reconcile adapter
  `version` across all 17 resolver sites.
- Current slice intent: replace 17 hand-copied inline `version` blocks with ONE
  shared contract check in `scripts/adapter_lib.py`, so an adapter declaring an
  unsupported `version` is refused everywhere instead of echoed back as
  authoritative at 16 of 17 sites. This names the reviewable-intent unit in
  progress and the commits it spans; critique and broad proof do not re-fire
  within one unchanged intent (meaningful-slice-cadence).
- **2026-08-09 update — the premise was re-confirmed LIVE, by accident, on a
  different resolver.** While arming an unrelated quality gate, a new
  `regenerable_facts` key was added to `.agents/quality-adapter.yaml` and the
  quality resolver SILENTLY DROPPED it: `valid: true`, `errors: []`,
  `warnings: []`, and the key simply absent from `data`. The gate then ran on its
  defaults and reported findings for files the adapter had already exempted,
  which is the only reason anyone noticed. That is this goal's root defect on a
  resolver its slice plan had not yet reached, found by a consumer of the
  contract rather than by a gate — the exact asymmetry the goal names. The fix
  needed a hand-written `_apply_regenerable_facts` validator, which is the
  seventeenth hand-copied block the goal exists to remove.
- **Also 2026-08-09: `#530`'s sibling shape is now armed once.** The new
  validator REFUSES an exemption whose reason is blank, rather than accepting and
  echoing it. That is one site holding the contract the other sixteen do not, so
  the goal's slice-1 target moved from "one site is right" to "two are".
- Premise check (verdict BEFORE the build): **HOLDS, and is slightly worse than
  stated.** Measured at activation — 17 non-plugin sites carry a `version`
  check; 16 accept ANY integer and write it into `validated["version"]` as
  authoritative; exactly one
  (`skills/public/create-skill/scripts/resolve_adapter.py`) compares against a
  `SUPPORTED_VERSION`. All 17 import `scripts/adapter_lib.py` already, so the
  shared seam exists and needs no new plumbing. Blast radius is zero as claimed:
  all 17 `.agents/*.yaml` and all shipped `adapter.example.yaml` files declare
  `version: 1`. NEW fact the goal did not predict: `isinstance(version, int)` is
  True for `bool`, and this repo's own YAML loader coerces bare `true`/`false`
  to `bool` — so `version: true` is currently accepted as an integer version at
  ALL 17 sites, including the one that enforces a supported value.
- Round-1 review (2 bounded reviewers): found an 18th unrouted site
  (`scripts/validate_adapters.py`, which accepted `version: 9` AND `version: true`
  and is the only version verdict `.agents/cautilus-adapters/*.yaml` gets), a test
  row proving a two-line pass-through instead of the real quality resolver, a
  vacuous payload assertion, an import-time-bound `supported` default, a dead
  constant, and an under-covering blast-radius glob. All repaired.
- Round-2 review (1 bounded reviewer reading the REPAIRS): the round earned its
  keep exactly as the contract predicts — the round-1 fix CARRIED THE CLASS IT
  FIXED. Moving the AGENTS.md reader to per-host framing left the setup TEMPLATE
  still writing a baked model id, so charness would have shipped a template its
  own inspector flags: one reader/writer split traded for another. Also found the
  new required-version floor skipped `cautilus-adapter.yaml` and
  `critique-adapter.yaml` via early returns (14 of 16 covered while reading as
  16 of 16), and that requiredness had been re-hand-rolled beside the shared
  check. All repaired; round-2 repairs are accepted-unreviewed per the two-round
  cap.
- Proof: 7762 passed / 0 failed, including the pre-existing red this slice
  repaired. 11 mutants constructed against the new verdict paths, 11 killed, 0
  survived — counted from a re-run, not from memory. The one mutant that first
  SURVIVED (section-scoping of the AGENTS.md policy check) is why the count is
  reported rather than assumed.
- Slice 2 premise check (verdict BEFORE the build): **HOLDS, and the refutation
  is stronger than recorded.** `.agents/setup-adapter.yaml` declares
  `defaults_version`, `policy_sources`, `recommendation_sets`, and `surfaces`.
  None is known to the shared `simple_skill` loader — its `STRING_FIELDS` is
  `(repo, language, output_dir, preset_id, preset_version, customized_from)`.
  All four have real named readers, measured not assumed:
  `skills/public/setup/scripts/setup_adapter.py` reads all four;
  `scripts/setup_inspect_lib.py` reads three; `surfaces` alone has 13 distinct
  readers including `scripts/surfaces_lib.py` and `scripts/validate_surfaces.py`.
  So a loader-scoped known-key set would call four CORRECT declarations typos on
  day one, which is exactly what `#530`'s posted causal review predicted. The
  unit has to be "which reader owns this key", not "does the loader know it".
- Current slice: Slice 2 — the reader registry. **COMPLETE.** The key-scoping
  defect its own round-1 review found (`#553`) is repaired within the slice:
  resolution is now (file, key)-scoped, the registry is wired behind a reporting
  `survey()` CLI, and the measurement the Operator Decision Queue asked for is
  done across the full population.
- Slice 2 acceptance: MET, **verified by execution against the criterion text
  rather than asserted here.** Clause by clause: (a) every declared key across
  the 37-file population resolves either to a named reader or to a typed state —
  measured, zero keys that are neither; (b) `setup-adapter.yaml`'s four
  multi-reader keys all resolve `reader` with named readers, and a mutant
  reverting to the refuted design is killed by that fixture. DIVERGENCE STATED:
  the criterion enumerates `unknown`/`retired`/`extension`, and the
  implementation adds `reader-elsewhere` and `text-asserted`. That is a superset,
  not a substitution — every criterion state still exists and is reachable
  (proved by constructed inputs, since `retired`/`unknown` have no live subject
  in this repo). The two extra states exist because collapsing them into the
  enumerated ones is precisely what would have produced the false verdicts the
  slice was built to remove.
- Pre-push gate acceptance: MET at this slice boundary. `./scripts/run-quality.sh
  --read-only` exits 0 with 85 passed, 0 failed, and one honestly-reported
  UNPROVEN (`check-changed-line-mutation-coverage` ran and established part of
  its scope). It FAILED on first run and caught real defects this session would
  otherwise have shipped: dead code my own repair orphaned (`_references`), two
  unreachable branches, and three genuinely uncovered verdict paths. `pytest
  tests/ -q`: 7796 passed, 0 failed.
- Measured across 37 adapter files / 445 keys (after the round-2 narrowing):
  167 shared-core, 254 reader, 23 reader-elsewhere, 1 text-asserted, **0 unknown**.
  24 gaps across 4 files. Two are the `.agents/cautilus-adapters/*.yaml` pair with
  no parsing reader at all; two are under-association residue, kept visible
  because a false `reader-elsewhere` is a report an operator dismisses in one
  reading while a false `reader` is a false green. Association is bounded to
  under 10% of the repo per adapter by an executable test.
- `#553` closeout carrier is COMMITTED and `draft_verified` (delegated critique,
  `Behavior #553:` verdict on a distinct channel, full bug ledger). It carries
  `Closes #553`, which fires on PUSH — not granted, so the issue is still open
  and `verify-closeout --expect-state CLOSED` has not run. That readback is the
  only floor step outstanding.
- Next action: Slice 3 (`#518`) — reconcile every declared quality surface to a
  reader or a typed gap. It is now unblocked: slice 2's resolution is
  trustworthy and bounded, and `survey()` is the seam it consumes.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Repair the declaration-to-verdict boundary starting at its ROOT, in a sequence
where each slice builds the thing the next one needs.

The predecessor goal
(`charness-artifacts/goals/2026-08-07-close-every-open-issue-declaration-to-verdict.md`)
had the right diagnosis and the wrong shape. Its diagnosis -- "a declaration that
no executable reader ever reconciles" -- held up under every review this repo ran
against it. Its shape, "close all 19 open issues", did not: it closed 8 and the
open set GREW, because honest reviews surface real findings faster than closes
remove them. That goal is SUPERSEDED, not failed; its Slice Log is this goal's
evidence base and nothing it proved is rebuilt.

This goal is not measured in issues closed. It is measured by one question:
**can this repo refuse a declaration nobody reconciles?** Today it cannot, and
the reason is specific and located -- 16 of 17 adapter resolvers accept any
integer `version` and return it as authoritative, and no resolver can tell a
typo'd key from a deliberate one.

The sequence is generative: each slice exists to make the next one possible.

1. **Version reconciliation** makes ONE declared field answerable, and proves the
   pattern of "one shared contract check, applied consistently" on the smallest
   surface that has zero blast radius.
2. **The reader registry** answers the question version reconciliation cannot:
   which reader owns a key. The predecessor's causal review REFUTED the obvious
   move here -- a loader-scoped known-key set -- by showing `.agents` files have
   multiple readers (`setup-adapter.yaml` carries four correct keys the shared
   loader has never heard of). So the registry, not a key list, is the unit.
3. **Surface reconciliation** (#518) becomes possible only once a declared
   surface can be resolved to a reader, which is exactly what slice 2 builds.
4. **Absence** (#528) becomes expressible only once "declared", "defaulted", and
   "absent" are three distinguishable states rather than one.

Each of those is a slice the predecessor listed and could not start, because it
ordered them behind a root it never repaired.

## Non-Goals

- **Not "close every open issue."** That was the predecessor's shape and it is
  measurably not reachable by grinding: this repo's reviews find real defects
  faster than closes remove them. Issues close here only when a slice's own work
  genuinely finishes one.
- Do not build a repo-wide doc-to-helper key gate. Measured in the predecessor:
  a prototype fired 25 times for ~2 real defects, and even a correctly scoped
  version probes `--help`, which cannot see payload-key semantics — the half that
  actually caused harm.
- Do not derive a known-key set from `infer_defaults`. The repo already built
  that and recorded why it failed: it told operators a correct declaration was a
  typo, on the one surface whose job is to stop a false signal.
- Do not add a refusal whose answer to "what escape does this prevent?" is
  "malformed input that changes no verdict."
- No release, tag, version bump, PR, or Cautilus run.

## Boundaries

- **Premise check is a phase, not a step.** Every slice opens by verifying the
  premise of whatever remedy it is about to build, and records the verdict in the
  Slice Log even when the premise holds. Measured basis: across the predecessor
  and this session, 6 of 7 attempted issues had a named remedy or a stated
  severity that did not survive its own premise check — `#530` (loader-scoped key
  set is the wrong set), `#534` (built green over dead code), `#544` (four of five
  claims refuted), `#538` (severity understated, not overstated), `#526` (partly),
  against `#529` as the one that held.
- **A slice that changes verdict logic owes round-1 and round-2 bounded review.**
  Round 2 is not ceremony: in this session it caught a false proof count in a
  closeout carrier and a second opt-in the first repair had missed — both
  introduced BY round 1's repairs.
- **Presence is not polarity.** A test asserting a doc or payload CONTAINS the
  right tokens is satisfied by one that says the opposite. Slices that pin
  wording must pin direction and prove it by constructing the flipped input.
- **A fix may carry the class it fixes.** `#544`'s regime fix leaked ambient state
  into the test suite — the same defect one layer up. Check the fix against its
  own diagnosis before closing.
- Root before consumer: slice 2 precedes `#518`; slice 2 precedes `#528`.
- Bounded reviewers run read-only in the shared worktree, fingerprinted
  snapshot/verify around every review.

## User Acceptance

- An adapter declaring an unsupported `version` is refused or warned by every
  resolver, not silently accepted and echoed back as authoritative. The report
  names how many of the 17 sites are covered and which are exempt with a reason.
- A declared adapter key resolves to a NAMED READER, or to a typed
  unknown/retired/extension state. `setup-adapter.yaml`'s four multi-reader keys
  stay clean — that is the regression fixture for the refuted approach.
- Every quality surface the adapter declares resolves to an executable reader or
  a typed gap; no declared-but-unreached surface renders as `clean`.
- A repo can declare a sub-key ABSENT and the resolver honors it.
- Every slice is proven green at the cadence `## Active Operating Frame` states.
  This line names no command and no boundary frequency on purpose; the frame owns that.
- The Slice Log records, per slice, the premise-check verdict BEFORE the build —
  including the slices where the premise held.

## Agent Verification Plan

### Low-Cost Checks

- Per slice: `scripts/check_changed_surfaces.py` and the validators it names,
  root/plugin sync before validators, `check_python_lengths.py --headroom` before
  adding to a gated file, `check_dup_ratchet.py --summary` before writing the
  commit message, and `run_slice_closeout.py --skip-broad-pytest`.
- Do not pipe a gate through `tail`; redirect and grep. Gates name their failures
  in the last line and keep full output under `.charness/quality-failure-logs/`.

### High-Confidence Checks

- Slice 1: a fixture per resolver family proving an unsupported `version` is
  surfaced, plus the count of covered vs exempt sites with reasons. Blast radius
  is measured first: every `.agents/*.yaml` and every shipped
  `adapter.example.yaml` in this repo declares `version: 1`, so a repo-local
  regression here would be self-inflicted.
- Slice 2: `setup-adapter.yaml`'s `defaults_version` / `policy_sources` /
  `recommendation_sets` / `surfaces` must stay clean — they are correct keys the
  shared loader does not know, and warning on them is the exact failure the
  predecessor's causal review predicted. `test_retro_plan.py`'s retired-key
  fixture must stay clean too.
- Any slice adding a refusal answers, in its carrier, what escape it prevents,
  and constructs the input that triggers it rather than trusting a green suite.
- Mutation-check every new verdict path and report the count from a re-run, not
  from memory. A miscounted proof claim in a carrier is itself a defect this repo
  has now shipped once and caught in review.

### External Or Live Proof

- Remote CI is a non-claim unless separately observed; a push exit code is not a
  build verdict, and the confirming observer and channel must both differ.
- Consumer-repo product behavior remains a standing non-claim.

## Slice Plan

| Slice | Objective | Issues | Why HERE in the sequence | Status |
| --- | --- | --- | --- | --- |
| 1 | Make one declared field answerable: reconcile adapter `version` across all resolvers | part of #530 | The smallest true instance of the root, with measured zero blast radius (every adapter here is `version: 1`). Proves the "one shared contract check, applied consistently" pattern the later slices reuse | planned |
| 2 | Build the reader registry: a declared key resolves to a NAMED reader or a typed unknown/retired/extension state | rest of #530 | The refuted move was a loader-scoped key list; the real question is which reader owns a key. This is the seam slices 3 and 4 both consume | planned |
| 3 | Reconcile every declared quality surface to a reader or a typed gap | #518 | Only expressible once slice 2 can resolve a declaration to a reader | planned |
| 4 | Let a repo declare a sub-key ABSENT | #528 | Needs slice 2's declared/defaulted/absent distinction; deletions currently refill silently | planned |
| 5 | Bundle proof and goal closeout, including the successor goal | (none) | Composition can drop what each slice proved alone | planned |

## Operator Decision Queue

- Decision: whether slice 2's unknown-key state is a WARNING or a REFUSAL for
  consumer repos.
  Owner: operator.
  Why deferred: D46 already rules out arming a blocking refusal from a repo-local
  zero, because the population that matters is consumer adapters this repo has
  never seen and cannot enumerate. A warning is safe and honest; a refusal is
  stronger but can block a consumer's whole skill run on an extension key that is
  legal in their world.
  Unblock action: slice 2 delivers the typed states and the measured count of
  unknown keys across this repo plus every shipped example adapter; decide from
  that.
  Revisit trigger: if slice 2 finds ANY unknown key in this repo that is not a
  known second-reader key, that is evidence the warning tier is already earning
  its place and the refusal question gets easier.
  STATUS 2026-08-07: ANSWERABLE, and the data is in. `#553` is repaired, so the
  resolution is trustworthy, and the measurement now covers the full population
  the unblock action names (this repo PLUS every shipped example adapter): 37
  files, 445 keys, 0 unknown, 21 gaps ALL inside the two
  `.agents/cautilus-adapters/*.yaml` files. The gaps are one real, contiguous,
  explicable cluster rather than scattered noise, which is evidence a warning
  tier would fire on something true. Still the operator's call: `survey()`
  reports and does not refuse, and D46's reasoning about the unseen consumer
  population is unchanged by a repo-local measurement.
- Decision: whether `#521` (prompt-surface deletion policy) is still worth its
  instrument chain, now that "close every issue" is no longer the frame.
  Owner: operator.
  Why deferred: the predecessor ordered `#532`/`#519`/`#520` ahead of it purely to
  answer `#521`. Outside that frame the instruments may be worth building on their
  own merits, or not at all.
  Unblock action: operator says whether prompt-surface measurement is a goal of
  its own.
  Revisit trigger: any slice here needing a read-cost number it cannot get.

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.
- **Successor goal step** — required at EVERY completion, not conditionally. Add
  a `Successor goal:` line naming the next goal artifact this run's lessons
  designed, or write `Successor goal: n/a — <reason>` to say out loud that none
  is wanted. The closing goal is the only place that still holds what the session
  measured about this repo's real shape; a completion that does not spend it
  throws that away, and the next session re-derives it.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: achieve — goal lifecycle operator for the slice sequence, premise-check phase, and closeout binding`
- `Routing: impl + prove — slice 1 and 2 builds and their closeout ledgers`
- `Routing: critique — the bounded fresh-eye rounds; round 2 read the repairs and caught a fix carrying the class it fixed`
- `Routing: issue — #550/#551/#552 filed under the standing approval; #553 filed, repaired, and closed through its full floor`
- `Routing: quality — pre-push gate cadence; it failed first and named four real defects`
- `Routing: release — v3.5.0 publish under the operator's explicit grant`
- `Gather: n/a — no external source informed this run; every input was repo-local or a GitHub issue already tracked`
- `Release: v3.5.0 published; critique charness-artifacts/critique/2026-08-07-release-v3.5.0-critique.md; release https://github.com/corca-ai/charness/releases/tag/v3.5.0 confirmed non-draft via gh release view, a channel distinct from the publish script's exit code`
- `Issue closeout: #553 — carrier direct-commit 19189ff1; validate-closeout-draft draft_verified; verify-closeout --expect-state CLOSED returned CLOSED via backend-state-readback. #550/#551/#552 filed as findings, not closed by this run.`
- `Successor goal: charness-artifacts/goals/2026-08-08-finish-the-declaration-to-verdict-sequence.md — carries slices 3-5 plus the four boundaries this run measured (premise-check as a phase, two review rounds, upper bound on any widening, and the quality gate at every slice boundary rather than only at the end)`

## Discuss Before Activation

CONFIRMED at activation (2026-08-07) by two operator acts read together: the
checked-in [handoff](../../docs/handoff.md) `## Workflow Trigger` names
"activate the root-repair goal and run **Slice 1**" as the next pickup, and the
operator then ran the `/goal` activation on this exact artifact. Each item
below is resolved on that basis; nothing here is assumed silently.

- RESOLVED — the reframe stands: this goal is measured by whether the repo can
  refuse an unreconciled declaration, NOT by issues closed. The predecessor's
  remaining open issues stay in the tracker and are picked up when a slice's own
  work reaches them, or in a later goal. The handoff states this reframe in the
  operator's own checked-in words ("measured by one question ... not by issues
  closed"), which is the confirmation.
- RESOLVED — slice 2's warn-vs-refuse tier is the operator's call and does NOT
  block activation. It stays in `## Operator Decision Queue` with its unblock
  action (slice 2's measured unknown-key count) and is answered mid-goal.
  Slices 3 and 4 consume slice 2's typed states either way, so the deferral
  changes the teeth, not the seam.
- RESOLVED — `#521` and the `#532`/`#519`/`#520` instrument chain are OUT OF
  SCOPE here, not deferred inside. They were ordered into the predecessor only
  to answer `#521`; outside the close-everything frame they need their own
  justification, which is an `## Operator Decision Queue` entry.

Non-claim about this confirmation: it is an inference from two operator acts,
not a fresh per-item answer in this session's transcript. If any item was meant
differently, say so and the goal reshapes — the three resolutions above are the
only place activation depends on them.

## Slice Log

### Slice 1: Slice 1 — reconcile adapter `version` across all 17 resolver sites

- Objective: Make ONE declared adapter field answerable everywhere, and prove the "one shared contract check, applied consistently" pattern that slices 2-4 reuse, on the smallest surface with measured zero blast radius.
- Why this approach: VERDICT BEFORE THE BUILD: HOLDS, and understated. Measured 17 non-plugin sites carrying a `version` check. 16 accepted ANY integer and wrote it into the resolved payload as authoritative; exactly one (`skills/public/create-skill/scripts/resolve_adapter.py`) compared against a local `SUPPORTED_VERSION`. All 17 already import `scripts/adapter_lib.py`, so the shared seam existed and needed no new plumbing. Blast radius zero as predicted: all 17 `.agents/*.yaml` and all shipped `adapter.example.yaml` declare `version: 1`. NEW fact the goal did not predict: `isinstance(True, int)` is True and this repo's own YAML loader coerces a bare `true` to `True`, so `version: true` read as a valid integer version at ALL 17 sites -- including the one site that did enforce a supported value.
- Commits:
- What changed: Added `SUPPORTED_ADAPTER_VERSION` and `validate_adapter_version()` to `scripts/adapter_lib.py` and routed all 17 sites through it, deleting 17 hand-copied inline blocks. Absent stays legal; a bool, a non-integer, and an unsupported integer are each refused, and none of them writes `validated['version']` -- a version the reader cannot interpret no longer comes back out as authoritative. `create-skill`'s local `SUPPORTED_VERSION` became an alias of the shared constant rather than a second source of truth. Existing error wording preserved exactly (`version must be an integer`, `version must be 1`) so existing fixtures keep their meaning. `scripts/adapter_lib.py` was at 459/480 code lines and the shared check pushed it to exactly 480/480 -- passing, but leaving zero headroom for slices 2 and 3, which both need this module. Per the length gate's own prescribed response (separate a concept; do NOT shave lines to stay under the bar), the YAML EMITTER moved whole into `scripts/adapter_yaml_render_lib.py`, a clean data->text boundary against the parser and field validators that remain. `adapter_lib` deliberately does not re-export the moved names, because a re-exporting companion would dodge the cap rather than separate the concept. Result: 398/480, 82 lines of headroom.
- Alternatives rejected: Rejected: warning instead of refusing an unsupported version. The in-repo precedent (`create-skill`) already ERRORED, so warning everywhere would have resolved the 17-way disagreement by weakening the one site that was right. D46's consumer-population reasoning argues against arming refusals from a repo-local zero, but it governs uninterpreted LINES, not a version the reader provably cannot interpret: an unknown key may be a legal extension in a consumer's world, while an unsupported schema version cannot be honoured by definition. Rejected: shaving the new helper's docstring to fit `adapter_lib.py` under its cap. That is the evasion the length gate names by name, and it would have left slices 2-3 with zero headroom in the module they both need.
- Targeted verification: New `tests/quality_gates/test_adapter_version_reconciliation.py`: 70 passing cases, 17 of 17 sites covered, 0 exempt. Per site it CONSTRUCTS the refused declaration (version 9, version true, version "1") and asserts BOTH that the refusal fires AND that the bad value does not survive into the resolved payload -- a test asserting only that an error appeared would pass on a resolver refusing for an unrelated reason. A polarity control asserts `version: 1` stays clean at every site, so a check that refused the supported value could not hide behind the refusal tests. The blast-radius measurement is kept executable rather than recorded as prose: a test fails and names the file if any repo-local adapter stops declaring version 1. pytest tests/ -q: 7747 passed, 1 failed. The single failure (`test_setup_inspect_recognizes_live_charness_policy_with_inline_code`) is PRE-EXISTING on main -- reproduced at HEAD in a detached worktree before any of this slice's changes. validate_packaging / validate_packaging_committed / validate_adapters / validate_skills / check_skill_ownership_overlap / validate_public_skill_validation / validate_public_skill_dogfood / check_python_lengths / check_doc_links / validate_skill_ergonomics / check_boundary_bypass_ratchet / check_test_repo_copy_invariants / gitignore_scan_hygiene / check-python-lint: all pass. Root->plugin synced before validators. Fired with 18 new code families, and the cause is worth recording because it inverts the obvious reading. Collapsing the 6-line version block did not ADD duplication -- it REVEALED duplication that was always there. The block sat in the middle of each resolver's `validate_adapter_data` body and split an otherwise identical preamble/epilogue (`errors`/`warnings`/`infer_repo_defaults`/STRING_FIELDS loop/CHANGE_ME warning/return) into two sub-threshold runs. One line per family is mine. Verified by reading two members side by side rather than inferred. Disposition: 18 families scoped-accepted into the gate baseline (not classified `intentional`, because they ARE fixable) plus 5 membership-reduction rotations; the real repair is a shared resolver contract, which is slice 2/3 territory and is filed rather than bundled here. Two later families WERE classified `intentional` in dup-review.json: one is literally the shared `validate_adapter_version` call site (consistent use of a shared helper looks like a clone of every other use), the other an import preamble. Editing `skills/public/issue/scripts/resolve_adapter.py` correctly staled the checked-in #514/#515/#518 owner-inspection freeze, which binds that file's digest. Re-froze with the repo's own `validate_issue_source_freeze.py refreeze`, whose docstring names re-freezing as the routine response to exactly this. Safe because the locator was inspected for the `issue_source_capture` capability contract and this slice's diff to that file touches only version validation plus one import binding -- confirmed by reading the diff, not assumed.
- Test duplication pressure: The 4 new test functions are parametrized across one SITES table rather than written per resolver, so adding a resolver adds a row, not a test. Duplicate pressure checked with check_dup_ratchet: the new test file introduced no fixable family of its own.
- Critique: Round-1 bounded fresh-eye review pending; this slice changes verdict logic on a proof surface, so it owes round 1 and round 2.
- Off-goal findings: The unknown-KEY half of #530 (slice 2's reader registry) is untouched. The resolver-body duplication the ratchet revealed is recorded, not repaired. The pre-existing `codex_subagent_profile_complete` failure is diagnosed but repaired in a separate commit. FINDING (pre-existing, main is red at HEAD): `test_setup_inspect_recognizes_live_charness_policy_with_inline_code` fails on unmodified HEAD. Cause traced: commit `353fa4a5` deliberately removed the Codex model-id profile block from AGENTS.md (the contract now says a host-specific model id belongs in an adapter or preset, because naming one in the contract file goes stale silently), but `scripts/setup_agent_docs_lib.py` still REQUIRES the exact tokens `gpt-5.6-terra`, `medium reasoning effort`, and `fork_turns: "none"` in AGENTS.md. This is this goal's own root class one layer over: a validator whose declaration nobody reconciled against the surface it reads.
- Lessons carried forward: A shared check can make a gate fire by REVEALING duplication rather than adding it. The dup ratchet's 18 new families were pre-existing clones unmasked by removing the 6 lines that had been splitting them; reading two members side by side took a minute and inverted the disposition entirely. A gate result is evidence about the tree, not about the diff, and the difference is only visible if you read the members. The premise check paid for itself again, in the direction the goal predicted least: the premise HELD, and checking it still surfaced a defect the goal had not predicted (`version: true` accepted as an integer at all 17 sites, including the compliant one).
- Metrics: No remote CI claim, no push, no release, no Cautilus run, no issue closed. Mutation coverage of the new verdict path is NOT yet reported from a re-run and remains owed before slice closeout. Consumer-repo adapter behavior is unobserved: the blast-radius measurement covers THIS repo's adapters only, and a consumer declaring a version other than 1 will now be refused where it was previously accepted silently -- that is the intended behavior change, not an unmeasured side effect, but no consumer repo was read to confirm none does so.

### Slice 2: Slice 1 addendum — public-skill scenario-registry decision (Cautilus planner follow-ups)

- Objective: Record the decision the closeout gate requires before it will pass: whether this slice's public-skill edits change any skill's consumer contract or need new/changed evaluator scenario coverage.
- Why this approach: The gate flagged 9 public skills because their helper scripts changed. It is right to ask; the answer has to be reasoned, not waved through.
- Commits:
- What changed: DECISION: no dogfood re-freeze and no scenario-registry change. Every public-skill edit in this slice is the same mechanical substitution -- a 6-line inline `version` block replaced by one call to `validate_adapter_version`, plus one module-attribute binding line. Net -72/+24 lines across 12 files, and no skill gained, lost, or reworded a command, flag, payload key, artifact path, or operator-facing message. The one behavior change is the shared one under review: an adapter declaring an unsupported version is now refused instead of echoed back. That is a change to the ADAPTER CONTRACT, which `docs/public-skill-dogfood.json` does not model per skill, and it is already covered by 81 constructed-input cases across all 18 sites plus 11 killed mutants. A dogfood re-freeze here would re-record unchanged consumer contracts and make the next real change harder to see.
- Alternatives rejected: Rejected: running `cautilus evaluate` to settle it. It is a Non-Goal of this goal, needs a separate explicit operator grant, and could not answer the question anyway -- the scenarios exercise skill workflows, not adapter version validation.
- Targeted verification: Basis for the decision, not assertion: `git diff --stat skills/public/` shows 12 files at -72/+24 with no signature, CLI, or output change; the full suite is 7762 passed / 0 failed; and the version contract's own proof is the 81-case table with 0 exempt sites. Acknowledged with `--ack-cautilus-skill-review` after recording this.
- Test duplication pressure: n/a — no tests added by this addendum.
- Critique: Round 1 (2 reviewers) and round 2 (1 reviewer reading the repairs) both complete; this addendum records a gate decision, not new verdict logic.
- Off-goal findings: Two length WARNs surfaced and are recorded rather than acted on: scripts/setup_agent_docs_lib.py at 462/480 and skills/public/quality/scripts/adapter_validators.py at 332/360. Neither is over its cap. Splitting either is a separate concept-separation decision, and this slice already carried one such split.
- Lessons carried forward: The gate asked a question this slice could answer cheaply and precisely because the edit was uniform. A slice whose public-skill edits were heterogeneous could not have answered it in one paragraph -- which is an argument for keeping mechanical substitutions in their own slice.
- Metrics: Non-claim: no Cautilus run, no evaluator observation, no consumer-repo dogfood execution. This is a reasoned decision from the diff and the suite, not evaluator evidence.

### Slice 3: Slice 2 (partial) — the reader registry, and the defect its own review found in it

- Objective: Answer the question slice 1 could not: which reader owns a declared adapter key. Deliver typed states (`shared-core`/`reader`/`text-asserted`/`extension`/`retired`/`unknown`) plus the measured counts the Operator Decision Queue needs for the warn-vs-refuse call.
- Why this approach: PREMISE CHECK BEFORE THE BUILD -- HOLDS, and the refutation is stronger than recorded. `.agents/setup-adapter.yaml` declares `defaults_version`, `policy_sources`, `recommendation_sets`, `surfaces`; the shared `simple_skill` loader knows none of them (its STRING_FIELDS is six unrelated names), and all four are parsed by `skills/public/setup/scripts/setup_adapter.py`. A loader-scoped key set would call four CORRECT declarations typos on day one. So the unit is the reader, not the key list -- exactly as `#530`'s posted causal review predicted.
- Commits:
- What changed: New `scripts/adapter_key_registry.py`: reader lists are DISCOVERED from the repo's own Python (via `ast` string constants) rather than declared in a table, because a checked-in key->reader table would be a second declaration nobody reconciles -- this repo's defect rebuilt inside the tool meant to detect it. The small registry that remains (retired keys, dynamic readers) is itself audited against the tree by `audit_registry`. A `text-asserted` state separates 'a validator greps for the raw line `key:`' from 'a module parses the value', because those are different facts and collapsing them is the false green this goal targets.
- Alternatives rejected: Rejected: a loader-scoped known-key set (refuted before building, see premise). Rejected: a hand-maintained key->reader table (a declaration nobody reconciles). Rejected during the build: a quote-regex for literal extraction -- it alternates quote pairs, so on `("alpha", "beta")` it pairs one literal's closing quote with the next one's opening quote and loses both, UNDER-reporting readers and inventing gaps. Replaced with `ast`, which is exact and also faster.
- Targeted verification: 16 tests; 6 mutants constructed, 6 killed after repair. One mutant SURVIVED first -- deleting the plugin-mirror guard changed nothing, because `READER_ROOTS` already excluded it -- so the guard was unpinned dead code; it is now pinned directly. Performance: the first version cost ~40s (per-key full-tree regex), which is expensive enough that the check would eventually be moved out of the fast gates, which is how a check stops running. Extracting each module's string constants once brought it to ~3s.
- Test duplication pressure: Tests are parametrized over one fixture table; the repo-wide measurement asserts SHAPE (no unknown keys, every reader state naming a reader) rather than pinning counts, since pinned totals fail on any legitimate adapter edit and then get deleted.
- Critique: Round-1 bounded review returned two blockers and I confirmed both by measurement rather than accepting them. BLOCKER: resolution is KEY-scoped, not (FILE, KEY)-scoped -- it asks 'does any module parse a key of this name', not 'does a module that reads THIS file parse it'. `.agents/cautilus-adapters/chatbot-benchmark.yaml` has NO parsing reader (`scripts/cautilus_adapter_lib.py` pins the SINGULAR `.agents/cautilus-adapter.yaml`; its only mention of the `cautilus-adapters/*.yaml` glob is an unrelated prompt-pattern list), yet nine of its keys resolve to it on name collision alone. Its three `*_command_templates` siblings are declared together, read by nothing, and graded differently for that reason only. BLOCKER: the module's own headline claim -- `surfaces` is read by thirteen modules -- was false in the way it mattered; only three concern the setup adapter, and several 'readers' merely EMIT a dict with that key. Both are now corrected in the module text, and the test that pinned 'only one text-asserted key' was replaced: it asserted a name-collision artifact as though it were a property.
- Off-goal findings: Filed `#553` for the key-scoping redesign, with the measured instance and the hard part named (transitive association: `setup_inspect_lib.py` reads the setup adapter through an imported `load_adapter`, never by path, so a path-literal rule alone would invert the bias into false `unknown`s).
- Lessons carried forward: The instrument reproduced the defect it was built to detect, twice, and neither instance was visible from inside the build. Its own docstring quoted an adapter key, so the first run counted the module as that key's reader -- the tool manufacturing the evidence it then reported. Then bounded review found the deeper one: a `reader` verdict is a claim about the REPO ('some module parses this name') dressed as a claim about the ADAPTER ('this declaration is reconciled'). Measuring the specific instance, rather than accepting or dismissing the review, is what separated the sound states (`unknown`, `text-asserted`) from the overstated one (`reader`).
- Metrics: STATUS: PARTIAL, and deliberately NOT WIRED. Nothing calls this module, and that is the correct state given the key-scoping gap: arming a warning on these verdicts would flag operators on evidence the tool does not have. The goal's acceptance criterion for slice 2 is therefore NOT met -- the typed states and the mechanism exist and are proven, the reader-resolution is not yet trustworthy, and the Operator Decision Queue's warn-vs-refuse call must NOT be made from these counts. Measured today, with that caveat attached: 227 declared keys across 18 adapters -- 74 shared-core, 152 reader, 1 text-asserted, 0 unknown. `unknown` is sound; the `reader` count overstates. Also unmeasured: the shipped `adapter.example.yaml` population the Decision Queue explicitly asks for, and keys the YAML parser silently dropped (`load_yaml_file_report` exists for that and is not used here).

### Slice 4: Slice 2 (completed) — repair #553: resolution is now (file, key)-scoped

- Objective: Make the reader resolution trustworthy enough to wire and to decide from, which is what slices 3 and 4 were blocked on.
- Why this approach: PREMISE CHECK ON THE REMEDY ITSELF, before building it: the obvious fix -- credit only modules containing the adapter's path literal -- was verified against the tree FIRST and would have been wrong. `scripts/setup_inspect_lib.py` receives its adapter loader as an INJECTED CALLABLE and names neither the path nor its owner, and most skill resolvers never contain their adapter's path at all because the shared helper composes `.agents/{skill_id}-adapter.yaml` from the skill id. A path-literal rule alone would have reported correct declarations as unread -- inverting the bias into false typo reports, which is the exact wolf-crier this goal's Non-Goals forbid. So the remedy needed three seeds, not one.
- Commits:
- What changed: Ownership seeds from (1) exact path literals -- never globs, because `cautilus_adapter_lib.py` carries `.agents/cautilus-adapters/*.yaml` inside an unrelated `DEFAULT_PROMPT_AFFECTING_PATTERNS` list and a glob rule would re-admit the very module the repair excludes; (2) the repo's naming convention, verified by requiring the file to exist; (3) inheritance for shipped examples, since `skills/public/setup/adapter.example.yaml` is a template for `.agents/setup-adapter.yaml` and by construction shares its readers. Association then closes transitively over module references -- static imports AND the dotted-name string literals this repo's dynamic loaders take. A key parsed only by unassociated modules gets its own state, `reader-elsewhere`, rather than being collapsed into `unknown`: telling an operator a correct declaration looks like a typo on the strength of an import graph is a mistake this repo has already shipped once.
- Alternatives rejected: Rejected: glob-based ownership (re-admits the excluded module; pinned by a mutant). Rejected: collapsing `reader-elsewhere` into `unknown` (false typo reports). Rejected: leaving examples unassociated -- it made the SAME key resolve `reader` in `.agents/setup-adapter.yaml` and `reader-elsewhere` in its own example, a verdict contradicting itself on identical evidence, and it inflated the example-adapter gap count the operator decision depends on.
- Targeted verification: 23 tests. 6 mutants against the repair, 6 killed -- each one re-creates a specific wrong design (key-scoped, glob owners, no convention seed, no example inheritance, collapsed states, no transitive closure) rather than flipping an operator. Suite 7785 passed / 0 failed. Runtime held to ~9s by caching the import graph and the closure; the naive version cost ~24s, and a check that gets expensive gets moved out of the fast gates and then stops running.
- Test duplication pressure: The intermediate wrong answers are pinned as tests rather than deleted: a glob does not confer ownership, a path-building resolver still owns its adapter, an injected reader stays associated, an example agrees with what it exemplifies. Each of those was a real defect in an intermediate version of this slice, found by measuring rather than by review.
- Critique: Round-1 review's two blockers are both repaired and both pinned. The reviewer's diagnosis was correct and its suggested direction was incomplete in the way it predicted -- it named transitive association as the hard part, and measurement showed there were two further seeds it had not seen (convention-built paths and example inheritance), each of which produced false gaps on real adapters before being fixed.
- Off-goal findings: `#553` is resolved by this slice's own work. `comparison_command_templates` remains a genuine finding, now correctly typed rather than accidentally singled out.
- Lessons carried forward: Every intermediate version of this repair was wrong in a way review had not predicted and only measurement exposed: exact-literal ownership produced 9 false gaps on `release-adapter.yaml`, and example adapters disagreed with the adapters they exemplify on identical keys. Running the instrument against the whole population after each change -- not just the fixture -- is what caught all three. A fixture that stays green while the population goes wrong is the failure mode an instrument is most prone to, because the fixture is the part the author was thinking about.
- Metrics: MEASUREMENT, and it now answers the Operator Decision Queue's unblock action in full -- this repo PLUS every shipped example adapter, which the earlier partial measurement omitted. 37 adapter files, 445 declared keys: 167 shared-core, 257 reader, 20 reader-elsewhere, 1 text-asserted, 0 unknown. Every one of the 21 gaps sits in the two `.agents/cautilus-adapters/*.yaml` files, which the repo itself documents as having no per-skill resolver. Revisit-trigger reading: there are NO unknown keys and no scattered noise -- the gaps are one real, contiguous, explicable cluster. That is evidence a warning tier would fire on something true rather than cry wolf, and it is the operator's call to make from it; `survey()` reports and does not refuse, per D46. Non-claim: no consumer repo was read, and the consumer population remains the one this measurement cannot speak for.

## Context Sources

1. `charness-artifacts/goals/2026-08-07-close-every-open-issue-declaration-to-verdict.md`
   — SUPERSEDED predecessor. Its Slice Log is this goal's evidence base: Slice 0
   (baseline), Slice 1 (`#529`), Slice 8 (`#534`, built then refuted), Slice 544,
   Slice 538.
2. `#530`'s posted causal review (issue comment) — the refutation that shapes
   slice 2: a loader-scoped known-key set is a known-key set for the wrong
   question, because `.agents` files have multiple readers.
3. `skills/public/quality/scripts/quality_bootstrap_lib.py` — the repo's own
   record of the first attempt at this fix and why the smaller inferred set was
   wrong.
4. `docs/deferred-decisions.md` D46 — governs uninterpreted LINES, not unknown
   KEYS, but its consumer-population reasoning constrains slice 2's warn/refuse
   decision.
5. `docs/design-north-star.md` — teeth only where a wrong answer escapes.
6. `charness-artifacts/critique/2026-08-07-issue-544-resolution-critique.md` and
   `...-issue-538-resolution-critique.md` — the two reviews that produced this
   goal's premise-check and presence-vs-polarity boundaries.
7. Measured this session: every `.agents/*.yaml` (18) and every shipped
   `adapter.example.yaml` (16) declares `version: 1`; 17 files carry
   `version must be an integer` and exactly one also enforces a supported value.

## Interview Decisions

- Shape: a generative sequence anchored at the root, rather than a backlog sweep.
  Chosen because the predecessor measured the sweep shape failing — 8 closed and
  the open set still grew — while its own ordering claim (root before consumer)
  was never executed. Rejected: continuing "close every open issue", which the
  predecessor's own artifact now records as not reachable by grinding.
- Slice 1 is the version half of `#530`, split away from the key half. Chosen
  because the key half's named remedy is refuted and needs a design pass, while
  the version half is untouched by that refutation, has an in-repo precedent
  (`create-skill` already enforces it), and has measured zero blast radius here.
  Rejected: parking `#530` whole, which is what left the root unrepaired.
- Slice 2 builds a reader registry rather than a key list. Forced by the posted
  refutation: `setup-adapter.yaml` carries four correct keys the shared loader
  does not know, so a loader-scoped list warns on correct declarations on day one.
- `#521` and its instrument chain (`#532`/`#519`/`#520`) are NOT in this goal.
  They were ordered into the predecessor only to answer `#521`; outside the
  close-everything frame they need their own justification, which is now an
  Operator Decision Queue entry rather than an assumed dependency.
- Premise check promoted from a step to a phase boundary, on a measured 6-of-7
  rate rather than on preference.

## Plan Critique Findings

- Corrected while drafting: the first shape of this goal was "finish the
  predecessor's remaining 16 issues in a better order." That reproduces the shape
  the predecessor already measured as non-convergent, and it buries the root
  again. Reshaped around the root with issues as consequences rather than targets.
- Corrected while drafting: slice 2 was initially "sweep unknown adapter keys."
  That is the exact move `#530`'s posted causal review refutes. Rewritten as a
  reader registry, with `setup-adapter.yaml`'s four multi-reader keys named as
  the regression fixture.
- Open risk, not resolved: slice 2's warn-vs-refuse question is a real operator
  decision (D46's consumer-population reasoning cuts against arming a refusal),
  and slices 3 and 4 consume slice 2's output either way. Mitigation: slice 2
  delivers the typed states and the measured counts regardless of the tier, so
  the decision changes the teeth, not the seam.
- Open risk, not resolved: this goal has no issue-count target, which makes
  "done" less legible to an operator scanning the tracker. Mitigation: User
  Acceptance is written as observable repo behavior, not as closes.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: name semantic goal/issue/quality inputs; retro, packet, reviewer, and lock records are terminal evidence.
- Frozen target: commit the semantic baseline, then bind the packet to that exact commit SHA.
- Fresh-eye: name a distinct reviewer and a different observer/evidence channel.
- Verification lock: name the lock command and evidence location; semantic input edits require rebinding.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status/evidence bookkeeping outside the reviewed identity.

## Off-Goal Findings

- **`#549` — durable failure output is a HABIT, not a quality feature, and it is
  built in exactly one script.** `run-quality.sh` copies failing phase logs to a
  stable directory and names the failing check in its last line; no other script
  in the repo does. The consumer-facing contract
  (`setup/references/hook-failure-visibility.md`) has no executable reader — its
  tests assert the document is mirrored, never that a consumer's hook satisfies
  it. And the agent-facing rule ("do not pipe a gate through `tail`") lives only
  in this repo's `AGENTS.md`, so an installing repo gets the affordance without
  the habit.
  This is the SAME shape as the goal's root — a declaration nobody reconciles —
  one layer out, at the boundary between charness and the repos that install it.
  It is NOT a slice here yet: per this goal's premise-check boundary, first
  measure whether consumer hooks actually ignore the contract, because a floor
  that fires across every consumer repo is exactly the wolf-crier this goal's
  Non-Goals forbid. Decide to build only after that measurement.
- The predecessor's remaining open issues stay tracked and unclaimed by this
  goal. Recount rather than trusting any list written here.
- `#534` may not be worth building at all; its stated cause was refuted and the
  build was reverted. Any future attempt re-measures first.
- Anything surfaced while reading consumer repos is a separate owner and is
  filed, not fixed here.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
