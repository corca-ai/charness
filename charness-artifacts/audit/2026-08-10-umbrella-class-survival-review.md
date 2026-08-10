# Umbrella class-survival review — #582, #583, #584, #585

Date: 2026-08-10. Method: four bounded read-only fresh-eye reviewers, one per umbrella,
each given the umbrella's claimed shared gap and its members, each asked the same
question — **did fixing the instances remove the CLASS, or only the instances?** — and
each instructed to be adversarial toward closing. Reviewers had `Read`/`Grep`/`Glob`
only, so every verdict below is a claim about the current tree, never about history.

Reviewer boundary: snapshot/verify around the window returned `clean`.

## Verdict: CLASS REMAINS, 4 of 4

And the framing that produced this review was itself wrong. All ten members read
`CLOSED` / `NOT_PLANNED` through the backend — that is the `consolidated` disposition,
which by contract **claims nothing about the defect**. The umbrellas are not four
tickets awaiting a ruling on whether a fix generalized. They are the only durable home
of ten defects, most of which were never repaired.

`charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md:287`
already said so: "fifteen are only MOVED. The umbrella issues carry the actual work
forward and this goal does not do it." Closing the four umbrellas would complete exactly
the laundering path the consolidated-close rule was written to block.

## Per member

**#582 — proof/evidence is prose, not schema.**

- `#524` NOT FIXED. The external-capability proof ladder
  (`skills/shared/references/external-capability-proof-ladder.md`) has **zero** machine
  readers: a repo-wide grep for its level names returns no `.py`/`.json`/`.yaml`/`.sh`
  hit. The repo does own a schema'd ladder (`scripts/proof_semantics_adapter_lib.py`)
  but it is a *different* ladder and charness ships no adapter for itself, which
  `docs/proof-semantics-adapter.md:54-58` states outright.
- `#525` PARTIALLY FIXED. `docs/readme-proof.md` IS now read by a failing gate
  (`specs/readme-proof.spec.md`, queued at `scripts/run-quality.sh:927`), so "nothing
  reads it" is false today. But that gate checks string presence and row shape only — it
  never opens an evidence path, so the silent evidence-path drift the issue named
  survives. Live proof: `docs/readme-proof.md:36-42` forbids claim discovery while
  `:80-82` still instructs to run it, and the gate passes either way.
- `#514` DECLINED, not fixed. `scripts/closeout_bundle.py` + `final_bundle_preflight.py`
  give one-command planned assembly over `.agents/surfaces.json`, but they shipped in
  v3.4.0 *before* the close, behavior channels are recorded rather than run
  (`docs/development.md:71-72`), and the evidence-boundary matrix the issue turns on was
  explicitly left unscheduled while its crosswalk instance was retired.
- `#535` INSTANCE FIXED, RULE NOT. `validate_issue_source_freeze.py refreeze` exists;
  nothing enumerates digest-binding surfaces and requires each to declare a re-bind.

**#583 — a verification surface can silently stop verifying.**

- `#568` NOT FIXED — discrimination *relocated*, not restored. Both eval specs are still
  registered (`evals/cautilus/claim-fidelity-registry.json:59-67`) and still collapsed.
  **CORRECTED 2026-08-11:** this section first said both arms had empty floors. Only
  `pickup.spec.json:10-11` does; `pickup-ambiguous.spec.json` carries
  `requiredCommandFragments: ["continuation-sequence.md"]` and is the ONLY `engage-always`
  forcer of that reference, so deleting it reds `validate-scenario-conditional-reads`
  (`scripts/run-quality.sh:747`). The collapse is real — both arms produce the same
  planner output — but it is the CLEAR arm that cannot fail on anything. Real
  discriminating tests were built elsewhere (`tests/test_handoff_plan.py:442-472`). No
  collapse detector exists. `pickup.spec.json:2` admits the collapse in its own text;
  `pickup-ambiguous.spec.json:2` still carries the *uncorrected* draft claim.
- `#569` EXAMPLES FIXED, RULE NOT BUILT. `scripts/check_quality_tool_fixtures.py:112-115`
  returns 0 on an EMPTY fixture set, is not in `run-quality.sh`, and fires only when a
  fixture file changes — so it can never catch the case the issue asked about (a
  belief-based test with no fixture at all). One fixture exists, not two.
- Class evidence: the repo has no mechanism that checks the PREMISE of a test. The
  handoff's own note is still true — the `Premise-residue:` seam has readers
  (`recount_residue_lib.py:68-71`) and no writers; exactly one marker exists in the
  tree, written by the goal that built the seam.

**#584 — a harness surface discards state and emits prose.**

- `#531` NOT FIXED, verbatim. `scripts/session_start_routing.py:42` still ships
  "skip this branch if the file doesn't exist"; `build_additional_context()` at `:58`
  takes **no arguments**, so it is structurally incapable of varying by repo; `cwd`
  reaches exactly one line, the debug log at `:111`. The plugin mirror carries it
  identically, so it is live in consumer sessions. `tests/test_session_start_routing.py:72-91`
  feeds a real `cwd` and asserts the constant — the defect is test-pinned, so a green
  gate is not evidence of repair. The design record that rejected the fix
  (`charness-artifacts/spec/session-start-hook-host-split.md:63-71,119-123`) says on its
  own line 3-5 that its required fresh-eye critique was never obtained.
- `#532` NOT FIXED. `skills/shared/scripts/run_plan_envelope.py:66-91` — `read()` still
  accepts no size or cost field, while `_validate_gate_packets:209-217` still mandates
  `cost_tier` and `_validate_reads:198-206` requires only `path`/`why`. No planner emits
  a size.

**#585 — a gate pins volatile identity.**

- `#534` INSTANCE NEUTRALIZED BY UNRELATED WORK. The pure-move false block cannot
  reproduce, because the slice-4/D30 re-key made the fingerprint offset- and
  path-independent (`nose_fingerprint_lib.py:20`) — `#534`'s own build was refuted as
  green-over-dead-code and reverted. Rotation detection still covers only membership
  SHRINK (`dup_ratchet_lib.py:110-131`); membership GROWTH and same-membership content
  rotation still hard-block a classified family, and
  `charness-artifacts/quality/dup-review.json` records that firing on 2026-08-08 (`:647`)
  and 2026-08-10 (`:1547`) — 57 rotation notes total. **A green dup-ratchet is not class
  removal; it is the record of keeping it green by re-recording rotated ids.**
- `#561` NOT FIXED. Both equality pins survive unchanged
  (`tests/test_inventory_marker_rule_measurement.py:153-171,189-195`;
  `tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py:370-381`). What
  shipped was a drift MESSAGE (`tests/probe_drift_support.py`), which that file itself
  says does not change the pins. **The operator decision is still open.**
  **CORRECTED 2026-08-11:** "no `docs/deferred-decisions.md` entry" was wrong. D47
  (`:636-703`) publishes the exact pinned figures, records a FOURTH and FIFTH refresh
  (`:710-726`), and `:711-714` assigns the standing pin tax to `#536` rather than
  absorbing it. The pins are therefore load-bearing for an OPEN operator decision, not
  free-standing measurement records.

## Class instances outside every member

These are the strongest evidence that the classes are structural, not two-issue accidents:

- `skills/public/setup/scripts/render_skill_routing.py:45-55` — takes `public_skill_ids`,
  never references it, hardcodes `listed_skill_ids = []`, and emits `docs/handoff.md` as
  the pickup surface while the caller already stats a sibling file. Resolved state in,
  static prose out — and it writes into a *consumer's* AGENTS.md. (#584's class)
- `scripts/boundary_bypass_ratchet_lib.py:137-139` — keys its ratchet on
  `"<test_file>::<target>"` path pairs beside its own working `no_increase` count
  property, so a test-file rename mints new keys and hard-blocks with zero new bypasses.
  This is the surface the dup ratchet cites as its own design template. (#585's class)
- `.agents/quality-adapter.yaml:123-652` — ~530 lines of hand-maintained prose sizing
  ~120 machine-checked numbers. The numbers are checked; the reasoning that sizes them
  is not. (#582's class)
- `skills/public/quality/scripts/plan_quality_run.py:327` — `next_action` is a constant
  over branches the same function already computed. (#584's class)

## What none of this establishes

No reviewer could run anything: no gate execution, no `git log`, no `gh`. Every
"predates" or "was reverted" claim above is read from in-repo records, not from history.
The parent separately confirmed through the backend that all ten members are
`CLOSED`/`NOT_PLANNED`, and confirmed `#531`'s and `#532`'s live defect text by reading
the two files directly. Nothing here re-verifies that the quality gate is green.

## What follows

The umbrellas are not closable today. The available moves are to re-split the live
defects into issues that say they are live, or to record an explicit declined ruling per
member — and for `#561`, to land its operator decision in `docs/deferred-decisions.md`
with a reopen trigger, since it currently exists only in a superseded goal's queue.
