# Achieve Goal: Make deliberate absence representable, starting with the adapter bootstrap that destroys it

Status: active
Created: 2026-08-05
Activation: `/goal @charness-artifacts/goals/2026-08-05-make-deliberate-absence-representable.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: E (closeout). A, B+C, and D are complete and logged.
- Current slice intent: prove and close. The reviewable-intent unit is "make a
  deliberate absence representable in the quality adapter and honor it in the
  bootstrap writer" — one intent spanning A through D, so critique does not
  re-fire per commit within it. Round 1 of the mandated bounded review is done
  (7 findings, 6 repaired in-slice, 1 filed as #485); round 2 reading the
  repairs is owed because this slice changed verdict logic on a proof surface.
- Next action: bounded review round 2 over the repairs, then the closeout
  aggregate, commit, push, and #481's closeout floor.
- Non-claim to carry into closeout: the fix is proven against a fixture
  RECONSTRUCTED from #481's posted before/after. That is evidence about the
  report, not about the reporter's tree, which this session cannot see.
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

**The operator hit this from outside, in a real repo, and it is data loss.**
[#481](https://github.com/corca-ai/charness/issues/481): running `quality` in a
repo whose adapter had already been customized silently reverted it toward the
preset. 14 comment lines to 0, and deleted preset keys resurrected pointing at
`lefthook.yml`, `.github/workflows/*.yml`, and a coverage-exemption file that do
not exist in that repo. `SKILL.md` calls the bootstrap as standard procedure, so
a customized repo pays this on EVERY run.

The deleted comment had predicted the failure in its own words: *"declaring gates
that do not exist sends the next session hunting for them."*

**The class, read from the code rather than from the report.**
`bootstrap_quality_adapter` does merge — `gate_commands` survived — so this is not a
blind overwrite. It fails two other ways, and they compound:

1. **Deliberate absence is not representable.** `existing.get(field) or <default>`
   cannot distinguish "absent because never set" from "absent because the operator
   deliberately removed it". Every deletion is read as the first and refilled.
2. **The only record of the intent is destroyed in the same pass.** The adapter is
   re-serialized rather than round-tripped, so the comments explaining WHY a field
   was cut die — which is also the only thing that could have told the merge, or a
   later reader, that the absence was deliberate.

Measured population, 2026-08-03: **5 helpers in this repo write a
generated/bootstrapped surface over a hand-authorable one; 0 of the 5 preserve
comments.** `bootstrap_adapter.py` already HAS an existence guard and a
`--dry-run`, and the loss happened anyway — which is the finding: the guard
protects the FILE, and what was lost was the operator's INTENT inside it.

The outcome is that a repo can say "this gate deliberately does not exist here"
in a way a generator will not undo, and that a generator which cannot honor that
says so instead of silently reverting.

## Non-Goals

- **Not redesigning the adapter schema.** Adding the ONE field that makes a
  deliberate absence representable is in scope (decided 2026-08-03); changing what
  the other fields mean is not.
- **Not adding `ruamel.yaml`.** Decided: the rationale moves into data instead, so
  comment round-tripping stops being the property the fix depends on.
- **Not converting every generated surface to round-trip YAML.** Measure which of
  the 5 writers actually face hand-authored input first; a generator whose output
  nobody edits does not need comment preservation.
- **Not the unreachable-file residue.** #482/#483/#484 are filed with their
  rulers and are a separate goal; only pick one up if this goal finishes early.
- **Not #468's deferred-remedy pattern**, though it is adjacent: the destroyed
  comment WAS a durable record of a decision. Recorded as a connection, not scope.
- Not the E-cluster, not D41—D49.

## Boundaries

- **External side-effect scope.** Issue CREATION is standing per `AGENTS.md`.
  `git push` is standing CONDITIONAL ON THE GATES — a refusing gate withdraws it,
  and never weaken one to reach a green push. Closing #481 is standing CONDITIONAL
  ON THE CLOSEOUT FLOOR; it is the operator's own report, so the behavioural
  verdict should reach THEIR repo, not only this one.
- In scope: `quality_bootstrap_lib.py`'s merge and serialization, the 4 sibling
  writers, the adapter's own vocabulary for expressing a deliberate absence, and
  the `plugins/` mirror of anything touched.
- Stop conditions: (1) if honoring deletion requires a schema migration that
  invalidates existing consumer adapters, stop and treat it as a design decision
  for the operator; (2) if the data-field approach turns out to need `ruamel.yaml` after all, STOP and
  re-ask — the operator rejected that dependency, so discovering it is
  unavoidable is a design change rather than an implementation detail; (3) if the fix
  starts changing what the adapter MEANS rather than how it is written, stop.
- **Cut order if short: D, then C.** A and B are the report; without them nothing
  is fixed for the person who filed it.

## User Acceptance

- **The reported loss cannot recur**, proven by replaying the operator's
  reproduction STEPS on a fixture RECONSTRUCTED from the before/after they
  posted: a customized adapter with comments and deleted preset keys, run through
  the bootstrap, compared before/after.
  **Ruler correction, 2026-08-05 (resolution critique F1).** An earlier wording of
  this line said "the operator's EXACT reproduction" and "the 14-to-0 comment
  loss". Both overstate what was run. Their tree measured 47 -> 62 lines and
  14 -> 0 comments; the reconstruction measured **24 -> 56 lines and 12 -> 0
  comments — 1 fixture, 2026-08-05**. It reproduces the same two MECHANISMS and
  the same 3 named nonexistent-path keys, which is what the fix is proven
  against; it is not the same file and its figures are not the reporter's. The
  observables are therefore: comment loss (any nonzero -> 0) and the 3 resurrected
  keys `exemption_list_path` / `lefthook_path` / `ci_workflow_glob`.
- **A deliberate absence is expressible as DATA**, and an adapter written before
  the field existed keeps working unchanged — back-compat is a criterion, not a
  hope, because every consumer adapter in the wild predates it.
- **The rationale survives a regeneration**, proven by running the bootstrap twice
  over an adapter carrying the field and diffing.
- **A generator that cannot honor an existing customization SAYS SO** rather than
  reverting silently. Refusing is an acceptable answer; refusing quietly is not.
- **The other 4 writers carry a decision**, each either fixed or recorded with a
  reason a reader can tell from an omission.
- **Every figure carries `<value> — <source>`**, with its denominator and date.
- **Non-claim in writing**: a fix verified in THIS repo's fixtures is not verified
  in the operator's repo. Name which channel reached which tree.

## Agent Verification Plan

### Low-Cost Checks

- **Replay the operator's reproduction FIRST**, before designing: their commands
  are in #481 and they confirmed it reproduces twice. A fix designed before the
  observation is a fix for the report, not for the behaviour.
- **Separate the two mechanisms.** Comment loss and key resurrection have
  different causes and could be fixed independently; a single test that only
  proves "the file did not change" would hide one of them.
- Re-measure the 5-writer population with the ruler stated; the first grep in this
  design said 52 and was wrong because most of those never write.
- Sync `plugins/` mirrors before validators; obey the dup-ratchet edit advisory.

### High-Confidence Checks

- **TWO bounded rounds for any slice that changes verdict or merge logic**, round 2
  reading the repairs. Measured seven times now; in the previous goal the round-2
  repairs themselves carried the class twice.
- **A new or changed rule must be proven to BITE** by reintroducing the real
  defect — here, the operator's own before/after adapter.
- `reviewer_boundary_fingerprint.py snapshot` around each review, `verify` the
  moment the reviewer returns, before any parent write.
- A closeout-claims review by a distinct observer before the completion flip.

### External Or Live Proof

- `git push` to `main` and its CI — standing, conditional on the gates. Remote CI
  confirmed by a different observer AND a different channel than the push exit
  code; the combined-status API reads `pending`/`total_count: 0` here because this
  repo publishes check-runs, which is not a pending check.
- **The behavioural verdict for #481 should reach the operator's repo**, since
  that is where the loss was observed. If it cannot, record the disposition rather
  than substituting this repo's fixtures for it.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Replay #481's reproduction and separate the two mechanisms | A fix designed before the observation is a fix for the report; and the two causes could each be fixed while the other still bites | A before/after diff reproducing 14->0 comments and the 3 resurrected keys, with each attributed to its mechanism | pending |
| B | Make a deliberate absence representable, and make the merge honor it | `existing.get(f) or default` cannot see a deletion; until it can, every other fix is cosmetic | The operator's deleted keys stay deleted across a bootstrap run, proven on their fixture | pending |
| C | Move the rationale into the same data field, and keep an older adapter loading | The comment was the only record of WHY a field was cut, and it lives in the one place a re-serializer cannot keep; data survives, and no dependency is added | Rationale survives a double bootstrap run; an adapter WITHOUT the new field loads and behaves exactly as before | pending |
| D | Decide the other 4 writers | One fixed instance and three unexamined siblings is how a class comes back | Each of the 4 fixed or recorded with a reason | pending |
| E | Closeout: bundle gate, claims review by a distinct observer, retro, #481 closeout floor, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest number; `check_goal_artifact.py` green; #481 closed through its floor or explicitly deferred | pending |

## Operator Decision Queue
Both activation decisions were RESOLVED by the operator on 2026-08-03 and are
folded into `## Interview Decisions`; what remains here is the one obligation
that outlives this goal.

- Decision: re-run #481's reproduction in the operator's own repo and confirm
  the loss is gone
- Owner: operator
- Why deferred: this session cannot see that tree. The close is carried by a
  fixture RECONSTRUCTED from the before/after posted on #481, which is evidence
  about the report and not about the reporter's repo — the closeout must say so
  in those words rather than letting a reconstruction read as a live verdict.
- Unblock action: after the fix ships, run the three commands from #481 in that
  repo and compare; a clean diff closes this, a dirty one reopens #481
- Revisit trigger: the next `quality` run in that repo. Recorded in TWO places on
  purpose — here and as a comment on #481 at close time — because a deferred
  confirmation kept in one place has evaporated more than once in this repo.

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  boundary, and record the route it returns. At completion, recorded
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

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

- Discuss before activation: RESOLVED at design time. No release surface, no
  live/prod proof, no broad scope. The two consequential calls are recorded as
  Interview Decisions 2 (a possible `ruamel.yaml` dependency — default is to
  refuse rather than add it) and 3 (the behavioural verdict cannot reach the
  operator's repo from here, so it is a reconstruction and says so). Closing #481
  is standing conditional on the closeout floor. The proof-level non-claim is in
  `## User Acceptance`.
- **This goal is ready to run.**

## Slice Log

### Slice 1: A — Replay #481 and separate the two mechanisms

- Objective: Reproduce the operator's reported loss from a fixture reconstructed from #481's before/after, and attribute each observable to its own mechanism before designing anything.
- Why this approach: A fix designed before the observation is a fix for the report. The two observables (14->0 comments, 3 resurrected nonexistent-path keys) have different causes and could each be fixed while the other still bites.
- Commits:
- What changed: No repo change. Fixture built at /tmp/i481 (Svelte+TS package.json, tsconfig.json, README.md, charness-artifacts/quality/latest.md) with a 24-line adapter carrying 12 comment lines, gate_commands: [npm run gate], preset_lineage: [typescript-quality], and coverage_floor_policy / coverage_fragile_margin_pp / recommendation_defaults_version / public_spec_section_exemptions / preflight_commands / security_commands deliberately deleted.
- Alternatives rejected: Rejected reading the operator's tree (not visible from this session) and rejected designing from the issue text alone (would not have found the trigger below).
- Targeted verification: REPRODUCED — 12 comment lines -> 0, and the operator's exact three nonexistent-path keys returned (exemption_list_path: scripts/coverage-floor-exemptions.txt, lefthook_path: lefthook.yml, ci_workflow_glob: .github/workflows/*.yml), adapter_status: updated, 24 -> 56 lines. Denominator: 1 reconstructed fixture, 2026-08-05; this is evidence about the REPORT, not about the reporter's tree.

Mechanism separation, three controlled runs:
- M1a (comments present, adapter data-converged, nothing else to change): adapter_status unchanged, comments 2 -> 2. Comments survive when no write happens.
- M1b (comments present, ZERO deleted keys, one benign concept_paths augmentation): adapter_status updated, comments 2 -> 0, data diff exactly one line. COMMENT DESTRUCTION is collateral of any write and is independent of key resurrection — cause: render_bootstrap_adapter re-serializes from the data dict, where comments have no representation.
- M2 (deleted keys, ZERO comments): adapter_status updated, all defaulted keys resurrected. KEY RESURRECTION is independent of comment loss — cause: 'field in explicit_fields' is the only absence signal in _add_adapter_policy_fields / _add_prompt_and_runtime_fields, and absent unconditionally means refill-with-default.
- Test duplication pressure:
- Critique: n/a — observation slice, no verdict-logic change yet.
- Off-goal findings:
- Lessons carried forward: Third mechanism found that the issue did not name, and it changes the fix's shape: diff_is_defaulted_only() is the de-facto protection for operator intent today, and it FAILS OPEN. It suppresses the write only when the ENTIRE diff is defaulted-only; any single unrelated legitimate merge unblocks the full rewrite and drags every defaulted key in with it. In the operator's repo the unblocking change is created BY THE QUALITY RUN ITSELF — charness-artifacts/quality/latest.md is a detect_concept_paths candidate, so the first quality run after customization writes the artifact that makes the next bootstrap overwrite the adapter. This is why the goal's 'the guard protects the FILE, not the INTENT' framing is right, and why a fix that only tightens the write-suppression heuristic would be the wrong repair: suppression is not representation.
- Metrics:

### Slice 2: B+C — Make deliberate absence representable as data, and honor it

- Objective: Add the one adapter field that makes a deliberate absence expressible (B), carry the rationale in the same field so it survives re-serialization (C), and make the generator announce what it cannot preserve.
- Why this approach: B and C are one change, not two: the merge needs a field to LOOK AT before it can see a deletion, and that same field is where the rationale has to live, because the comment that used to hold it is destroyed by the very rewrite it was explaining. Splitting them would have shipped a signal with no reason attached.
- Commits:
- What changed: NEW scripts/quality_bootstrap_absence.py (validation, unrecognized-name warning, intent-loss reporting). scripts/quality_bootstrap_lib.py: load/honor deliberately_absent, set field_statuses, filter deferred_setup, report. scripts/quality_bootstrap_render.py: emit the block, filter declared-absent keys from output. scripts/adapter_lib.py: _string_round_trips_bare (quote a string that would reload as a bool/int), _strip_inline_comment, {} mapping parse. scripts/quality_adapter_lib.py: _apply_deliberate_absence pass-through + gap warning. skills/public/quality/scripts/bootstrap_adapter.py: stderr WARN. Docs: bootstrap-posture.md (status vocabulary + full field rules + scope limit), adapter-contract.md (field listing). NEW tests/quality_gates/test_quality_bootstrap_absence.py (16 tests). plugins/ mirror synced.
- Alternatives rejected: Rejected ruamel.yaml round-tripping (operator rejected the dependency; and round-trip MERGE has its own unresolved question about where a comment on a nested node should follow). Rejected refusing to rewrite (operator does not hand-edit adapters, so refusal pushes the merge onto the caller — the tool's own job). Rejected tightening diff_is_defaulted_only: suppression is not representation, and it already fails open.
- Targeted verification: Operator fixture (/tmp/i481-fix, reconstructed from #481): declaring the 6 cut fields absent -> 0 of the 3 nonexistent-path keys resurrect, adapter_status unchanged on re-run, rationale intact. Double bootstrap: run2 byte-identical to run1. Back-compat: an adapter without the field renders no deliberately_absent key and keeps every prior status. 16 targeted tests pass. Warning quality: the refill list on the undeclared fixture dropped 28 -> 11 fields, and all 11 are genuinely written to the file.
- Test duplication pressure: Dup-ratchet edit advisory fired on 3 files (quality_bootstrap_absence.py +105, adapter_lib.py +33, quality_adapter_lib.py +31); to be settled at the closeout aggregate.
- Critique: Bounded fresh-eye round 1 (typed bounded-reviewer, unnamed, read-only; reviewer_boundary_fingerprint verify = clean). 7 findings, ALL confirmed by direct reproduction before repair, 6 repaired in-slice:
- F1 (highest) deliberately_absent is honored by the WRITER but not by adapter RESOLUTION — quality_adapter_lib re-defaults on absence exactly as the bootstrap used to, so a declared-absent coverage_floor_policy still resolves to the preset default naming lefthook.yml. Partially repaired (declaration now survives resolution + a warning names every field where the default still wins); the deeper per-consumer honoring hits this goal's stop condition (1) and is FILED as issue #485.
- F2 (high) inline comments were swallowed into the value: `coverage_fragile_margin_pp: 2.0  # widened` parsed as a STRING, the type check dropped it, the default won, and the report still said `preserved` — a false verdict, same class as #481. REPAIRED in the parser; comments_dropped now counts trailing comments too.
- F3 the loss warning named ~25 never-customized, mostly never-written fields, burying the real ones. REPAIRED (intersect with keys actually written).
- F4 DEAD branch: adapter_status `written` could never produce an intent-loss entry. REPAIRED.
- F5 the new operator-facing field was documented nowhere an operator reads. REPAIRED in both quality references.
- F6 a typo'd declaration was honored as a silent no-op, reproducing the confusion the field exists to end. REPAIRED as a warning (an unknown/consumer-owned name must stay legal).
- F7 an empty `deliberately_absent: {}` block hard-failed with a misleading message. REPAIRED in the parser.
Reviewer confirmed clean: no _unknown_fields double-emit, no non-convergent write loop, no status-vocabulary consumer breakage, and _yaml_scalar back-compat verified against this repo's real adapter (byte-identical).
- Off-goal findings: issue #485 (resolution-layer half of F1).
- Lessons carried forward: The review's F1 is the finding that matters beyond this fix: the goal framed the class as 'a generator destroys intent', and the same conflation of never-set with deliberately-removed lives in the RESOLVER too. Fixing the writer alone would have let the file tell the truth while the resolved adapter kept lying. Also: 6 of 7 findings were in code written THIS slice, which is the measured argument for the round-2 obligation on verdict-logic surfaces.
- Metrics:

### Slice 3: D — Decide the other sibling writers

- Objective: Re-measure the render-and-write population with the ruler stated, then fix or record a reason for each sibling, so one fixed instance does not leave unexamined siblings.
- Why this approach: One fixed instance and unexamined siblings is exactly how a class returns.
- Commits:
- What changed: No code change. Decisions recorded here.
- Alternatives rejected: Rejected a blanket refactor of every writer before one was understood; rejected accepting the design-time count without re-measuring.
- Targeted verification: RE-MEASURED 2026-08-05. Ruler: a helper that calls render_yaml_mapping() or write_adapter_scaffold() AND writes the result to disk, counted over scripts/ + skills/ excluding mutants/. Result: 4 distinct render-and-write helpers, not the 5 recorded at design time on 2026-08-03. The difference is a counting rule, not a change in the code: 14 skill-level init_adapter.py entrypoints all delegate to the single scripts/adapter_init_lib.py helper, so counting entrypoints gives 17 and counting distinct helpers gives 4.

The load-bearing figure is different from the one the goal anticipated: 1 of 4 could silently revert a hand-authored surface, and it is the one that was reported. The other 3 all already refuse-or-warn. 0 of 4 preserve comments (unchanged from the design-time measurement) — but comment preservation only matters where the writer overwrites, which narrows the class sharply.

Per-writer decision:

1. scripts/quality_bootstrap_render.py + quality_bootstrap_lib.py — faces hand-authored input (the adapter is the documented operator customization surface and SKILL.md calls the bootstrap every run); MERGES rather than refusing, so it could silently revert. This was the defect. FIXED this goal.

2. scripts/adapter_init_lib.py (14 skill init_adapter.py entrypoints) — faces the same adapter family, so it does face hand-authored input. Cannot silently revert: write_adapter_scaffold (scripts/adapter_lib.py) raises SystemExit when the target exists unless --force. NO FIX. Reason a reader can tell from an omission: its contract is REFUSAL, not merge, so there is no absence-vs-deletion question to answer — it never reads an existing file at all.

3. scripts/markdown_preview_bootstrap_lib.py — faces hand-authored input (a repo-owned preview config). Cannot silently revert: returns status existing-config / config_status preserved on any existing config, and at the write path emits config_status preserved-existing plus a warning naming the rerun-with---force remedy; it overwrites only under explicit --force. NO FIX. Reason: it ALREADY has the property this goal wants — it announces rather than reverting.

4. skills/public/hitl/scripts/bootstrap_review.py — writes .charness/hitl/runtime/<session_id>/state.yaml. NOT a hand-authorable surface: machine session state, keyed by session id, regenerated per run, under .charness/. NO FIX. Reason: nobody hand-authors it, so there is no operator intent for a rewrite to destroy.

Note: all 4 share scripts/adapter_lib.py, so the two parser/serializer repairs made this slice (inline-comment stripping, scalar-shaped-string quoting) reach every one of them, including the 3 that needed no writer change.
- Test duplication pressure:
- Critique: Covered by the bounded review rounds recorded on slice B+C and the round-2 review.
- Off-goal findings: None beyond issue #485 already filed.
- Lessons carried forward: The goal's design-time framing ('5 writers, 0 preserve comments') implied a wide class. Measured, the class is 1 wide: the differentiator is not comment preservation but whether the writer MERGES into an existing file or refuses it. A writer that refuses cannot destroy intent, so it never needs a vocabulary for deliberate absence. That reframes the remedy: representability is owed by mergers, not by every generator.
- Metrics:

### Slice 4: B+C round 2 — bounded review of the repairs

- Objective: Run the mandated second bounded round reading the REPAIRS from round 1, since this slice changes verdict logic on a proof surface.
- Why this approach: This repo's measured experience is that a repair carries the class it fixes. That held again, decisively: the two highest findings are the ORIGINAL #481 class living inside the round-1 repairs.
- Commits:
- What changed: scripts/adapter_lib.py: strip_inline_comment made public and moved BEFORE the _mapping_value dispatch. scripts/quality_bootstrap_absence.py: _line_has_comment now defers to the parser instead of re-deriving the rule. scripts/quality_bootstrap_lib.py: KNOWN_ADAPTER_FIELDS (defaults + fields rendered without defaults), would_do computed before the dry_run branch. scripts/quality_adapter_lib.py: resolver warns instead of silently discarding malformed declarations; structural fields excluded from the still-defaulted list. bootstrap-posture.md: quote-your-reason rule. 6 new tests (22 total).
- Alternatives rejected: Rejected leaving D2 as a parser edge case: it silently drops a whole nested block while reporting the field preserved, which is strictly worse than the bug this goal was filed for.
- Targeted verification: All findings REPRODUCED before repair, then re-run after:
- D1: count_comment_lines("repo: it's-a-repo  # renamed") returned 0 (comment destroyed, loss reported as none). Now >= 1.
- D2: load_yaml("deliberately_absent: {}  # none") -> the STRING "{}"; load_yaml("coverage_floor_policy:  # tightened\n  fail_below_pct: 90.0") -> {"coverage_floor_policy": ""} with the nested block DROPPED; load_yaml("gate_commands: []  # none yet") -> the STRING "[]". All three now parse correctly.
- D3: declaring public_spec_section_exemptions absent produced a false "this bootstrap does not generate" warning. Now silent.
- D5: --dry-run on a commented but data-converged adapter claimed comment loss a real run would not cause. Now reports would_do: unchanged and warns nothing.
22 targeted tests pass; reviewer_boundary_fingerprint verify = clean around both rounds.
- Test duplication pressure: Dup-ratchet edit advisory fired again on quality_bootstrap_lib.py (+37); settled at the closeout aggregate.
- Critique: Bounded fresh-eye round 2 (typed bounded-reviewer, unnamed, read-only). 6 findings + 1 doc gap; all repaired:
- D1 (HIGH) _line_has_comment, the round-1 repair for comment loss, MISSED a real trailing comment when the value contained an apostrophe, so the rewrite destroyed an annotation and reported losing nothing. The original class, inside its own repair. Root cause named by the reviewer: two implementations of "where does the comment start". REPAIRED by deleting the second one.
- D2 (HIGH) the round-1 inline-comment strip was added only to the plain-scalar branch, so `{}`, `[]`, block-scalar headers, and "value on the following lines" still swallowed the comment. Worst case: `coverage_floor_policy:  # note` + nested block silently dropped the ENTIRE nested block while field_statuses still said `preserved`. This also un-did round 1's own F7 fix. REPAIRED by stripping before the dispatch.
- D3 (MED-HIGH) the round-1 typo warning used _infer_defaults as the known-field set, but 5 fields are rendered without inferred defaults, so 5 CORRECT declarations were reported as probable typos. REPAIRED.
- D4 (MED) the resolver silently discarded malformed declarations, giving the bootstrap and the resolver opposite verdicts on the same file, with the silent one wired into validate_adapters. REPAIRED as warnings.
- D5 (MED-LOW) --dry-run could not distinguish a would-be rewrite from a would-be no-op, so it warned about losses a real run would not cause. REPAIRED by computing would_do first.
- D6 (LOW) _line_has_comment over-counts block-scalar body text containing ` #`. ACCEPTED: it over-warns, never under-warns, and the renderer never emits block scalars into a quality adapter.
- Doc gap: a reason containing ` #` is truncated by YAML. REPAIRED in bootstrap-posture.md.
Reviewer independently confirmed clean: no legitimate value in any checked-in adapter is truncated by the strip (repo-wide grep, 4 hits, all genuine comments); the signature change is fully propagated to both trees; adding deliberately_absent to resolved data breaks no strict/schema/consumer path.
- Off-goal findings: None new.
- Lessons carried forward: The round-2 obligation earned its cost outright this run: round 1's repairs contained two HIGH defects of the very class they repaired, one of which silently dropped MORE operator data than the original bug. The transferable rule the reviewer named is sharper than 'review twice': D1 and D2 both came from re-deriving a rule that already existed somewhere else (a second comment-start implementation; a strip applied at one of two dispatch layers). A repair that DUPLICATES a rule rather than moving it is the shape to look for.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [issue #481](https://github.com/corca-ai/charness/issues/481) — the operator's
   own report from an external repo, with the reproduction, the before/after
   table, and the deleted comment that predicted the failure. Read this first.
2. [quality_bootstrap_lib.py](../../scripts/quality_bootstrap_lib.py) — the merge
   is real (`preserved`/`augmented` statuses); the two failures are the
   `or <default>` refill and the re-serialization. Read the code before the fix.
3. [design-north-star.md](../../docs/design-north-star.md) — P4 governs this: a
   generator's success is a claim, and "the file was written" is not "the operator's
   intent survived".
4. [the closed #479](https://github.com/corca-ai/charness/issues/479) and its
   [resolution critique](../critique/2026-08-03-issue-479-resolution-critique.md)
   — the denominator discipline, and the worked example of a critique refusing a
   close because the record misstated its own ruler.
5. [recent-lessons.md](../retro/recent-lessons.md) — repeat traps that should
   change the next move.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

1. **What is the unit of the fix — the quality adapter, or the class?** Family
   considered: {fix #481 only; fix the 5 writers; fix the concept of a generated
   surface}. **Chosen: fix #481 fully, then DECIDE the other 4 with a recorded
   reason.** One fixed instance and three unexamined siblings is exactly how a
   class returns; but a blanket refactor of 5 writers before one is understood
   inverts the order. Anti-anchoring: `axis: a class is found by fixing one
   instance carefully, not by touching five quickly`.
2. **Comment preservation, or refusal?** Family considered: {round-trip YAML via
   `ruamel.yaml`; refuse to rewrite an existing adapter; move the rationale into a
   DATA field; write a sidecar; accept the loss}. **Chosen by the operator
   2026-08-03: move the rationale into a data field (`deliberately_absent`), and
   add no dependency.**

   Two observations settled it and neither was in the original framing. First,
   **the operator does not hand-edit adapters** — so "refuse and print the diff"
   pushes the merge onto whoever called the tool, which is the tool's own job.
   Their words: *"refusing means the repo has to work it out itself, right?"*
   Second, **the lost comment reads as agent-authored** (*"the bootstrap applied
   the typescript-quality preset, but this repo uses neither..."* is written by
   whoever watched the bootstrap run), so the adapter is a record agents write and
   agents read — and a rationale agents write need not be a COMMENT at all.

   Moving it into data resolves three things at once: the merge can finally SEE a
   deletion (there is a field to look at), the rationale survives
   re-serialization, and no dependency is added. Comments still vanish, but they
   stop being load-bearing — losing one no longer produces a false signal.
   Rejected `ruamel.yaml`: a supply-chain addition in a repo that gates on supply
   chain, for a formatting property the data field makes non-essential; and
   round-trip MERGE carries its own unresolved question about where a comment
   attached to a nested node should follow. Anti-anchoring: `axis: if the only
   reader is a machine, the rationale does not belong in the one place machines
   cannot read`.
3. **Should the verdict reach the operator's repo?** Family considered: {this
   repo's fixtures only; block the close on an operator re-run; reconstruct from
   the posted before/after; reconstruct now and re-run later}. **Chosen by the
   operator 2026-08-03: reconstruct from the posted before/after and close, with
   the re-run recorded as a revisit.** The loss was observed in a tree this
   session cannot see, so the reconstruction is evidence about the REPORT and not
   about the reporter's tree, and the closeout must say exactly that. Because
   "confirm it later" has evaporated more than once here, the revisit is recorded
   in TWO durable places — a comment on #481 at close time AND this goal's
   Operator Decision Queue — rather than in prose. Anti-anchoring: `axis: a
   deferred confirmation that lives in one place is one that will be lost`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

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
