# S5 umbrella guards — measurement and remainder

Date: 2026-08-15. Owns SC9 of the
[6.0.0 release scope](../spec/2026-08-15-6-0-0-release-scope.md): *each umbrella has one
executable guard with a recorded measurement of what it catches on the current tree, and
a stated remainder.* Sequence and narrowing follow the `## Owner Rulings` entry
"S5 lands ONE executable guard per umbrella, and #582 is narrowed to a single member",
plus the ruling on #583's rule taken this session.

Every measurement below is a command that can be re-run. A guard whose catch is not
reproducible is a claim, not a measurement.

## Premise check, run before any code moved

The standing remedy from `## Next Session` item 1. It changed the slice materially, so
it is recorded rather than assumed.

| Issue | Scoped work | Found on the current tree |
| --- | --- | --- |
| #586 | vocabulary-parity check | **LIVE.** Five copies of the closeout classification vocabulary, none held. |
| #584 | #531, #532 | **Both members already FIXED** (`eae80f660`, `76a395446`), reproductions run. The CLASS had no guard, and the rollout that fixed them stopped at "representative" by its own docstring. |
| #582 → #525 | resolve evidence paths | **Already BUILT** (`28be0bf2a`). What was owed was the measurement and the rulings, not code. |
| #583 | rule undecided | **LIVE.** Both members closed, #597's fail-open repaired and queued; no premise-checking mechanism. |

Two of four umbrellas' scoped member work was already done. The guards below are
therefore CLASS guards, which is what SC9 asks for in any case.

## #586 — a check that passes its own direct-call test while never firing on the wired path

**Guard:** [check_closeout_classification_parity.py](../../scripts/check_closeout_classification_parity.py),
queued in [run-quality.sh](../../scripts/run-quality.sh) beside the floor-matrix gate.

No site is judged by parsing a source literal, because a test that reads the tuple passes
while the wired surface refuses the value — the issue's own shape. **Five of six** are
probed through the surface an operator reaches: argparse by parsing an argv, two regexes
by matching the production line, the resolve planner by building a plan, and the
classification ledger through `classification_requirements`, its production accessor.
Stated as five rather than six because an earlier version of this section (and of the
gate's own docstring) claimed all of them: `audit_brief.KNOWN_CLASSIFICATIONS` is read as
a module attribute, not exercised through `audit_brief`'s transcript check.

**Measurement.** Baseline is green, and a green parity gate is indistinguishable from a
gate that probes nothing. So the catch is measured by assuming a seventh disposition:

```
python3 scripts/check_closeout_classification_parity.py --repo-root . --assume-classification superseded
```

Five `exact` sites turn red, each naming its own surface and its own failure mode:
`audit_brief.KNOWN_CLASSIFICATIONS`, the commit-msg hook regex, the release closeout
message regex, `publish_release_cli --close-issue-classification`, and
`issue_plan.build_resolve_plan().classification_actions`. The run is labelled
`hypothetical` in its own payload so a transcript is never read as a verdict about the
tree. `tests/test_closeout_classification_parity.py` pins that measurement.

**Remainder.**

- Parity is agreement, not correctness. Six sites can agree on a wrong value.
- The `subset` site (`CLASSIFICATION_FIELDS`) now DECLARES the two absences its recorded
  decision covers, `question`/`decision-needed`, and any other missing classification
  fails. It still **cannot be judged for an ASSUMED value** — a hypothetical addition is
  exempt there by construction, since omission is legal — and the payload says so rather
  than counting it as covered.
- `.agents/closeout-floor-matrix.json` is delegated to `check_closeout_floor_matrix.py`
  and named in `not_judged` on every run, passing ones included.
- Only #586's instances 1 and 6 are covered. Instances 2-5 (a readback wired into one
  carrier and not the required one; a constant read by nobody; a `self_number` defaulted
  to `None`; a resolver whose only production caller passed no `repo_root`) are NOT the
  vocabulary shape and get no guard here.

## #584 — a harness surface discards state it already has and emits prose instead

**Guard:** the disclosure is now MANDATORY at the shared chokepoint.
[run_plan_envelope](../../skills/shared/scripts/run_plan_envelope.py) gains
`measure_read`/`measure_reads`, and `_validate_reads` refuses a read that discloses no
measurement — the branch that used to `continue` past one.

This is preventive, not detective, and it needs no enumeration of "which files are
planners": every planner already passes through `build_envelope`.

**Measurement.** Before the mandate, **five of eight** planner surfaces emitted unpriced
reads: `plan_debug_run`, `plan_release_run`, `gather_plan`, `plan_retro_run`, and
`issue_plan`. All five are now measured and disclose real sizes; `issue_plan`'s resolve
plan, for instance, reports `[3801, 16819, 22535]`. Re-run any planner to see it, or
delete a `measure_reads` call to see the refusal.

A false green is worth recording: `python3 skills/public/issue/scripts/issue_plan.py` exits
0 and prints nothing, because the module has no `main`. The first probe read that as
compliance. `build_resolve_plan` called directly is what showed it red.

**What made the class recur, and what changed.** Three planners had each hand-rolled a
near-identical resolver, so every new planner owed a fresh copy and the ones that skipped
it were silent. **An earlier version of this sentence said "those three now delegate to
the shared one" — that was false when written.** Two were collapsed into delegations
(handoff, quality); retro's was left in place and the shared resolver stacked ON TOP of
it, which double-disclosed and made the planner RAISE for any adapter naming an evidence
path outside the repo root. A bounded round-1 reviewer found it; the reproduction is a
retro adapter with `evidence_paths: ["../outside.md"]`, which exited 1 with
`mixes available and unavailable measurement`. Retro's resolver now contributes only
`available`/`path_kind` and the envelope is the sole measurer.

**Remainder.**

- An unmeasurable read is disclosed with a typed `unavailable_reason`, never blocked. So
  a planner that stats nothing still validates — the guard forces DISCLOSURE, not
  availability.
- `measure_read` accepts an `(anchor, containment_root)` base pair for the real case of a
  skill reading a sibling package (gather's `../../support/web-fetch/...`). That widens
  the containment check for that one base by design.
- The class is broader than reads. `render_skill_routing.py` still resolves
  `public_skills`/`support_skills` and emits a static block into a consumer's AGENTS.md;
  its own docstring records this as an open instance. No guard here touches it.
- Sizes are disclosed; nothing yet ACTS on them. #532's "shrink the unearned read set"
  half is not done.
- **`on_demand_reads` are still unpriced in every planner**, and `validate_envelope` does
  not inspect that key. Those paths are resolved by the same planner against the same
  bases, so the class is half-closed, not closed. Named by a round-1 reviewer.
- Gather's containment widening is per-PLANNER, not per-read: every gather read is now
  contained by the skills container rather than by the gather skill dir. A mistaken
  `../../public/quality/...` read would be priced as if legitimately in base.

## #583 — a verification surface can silently stop verifying what it claims to

**Rule decided this session** (the contract records that #583's rule must be decided
before its guard). Of three candidates — an eval-arm collapse detector, a captured-fixture
requirement, and retirement by ruling — the first was chosen because it is the only one
that is deterministic at low cost. The captured-fixture rule needs a heuristic enumeration
of "what counts as an external-tool assertion", which inside a release slice produces the
inert-or-unfalsifiable guard the contract already refused for release-note claims; and
#569's own disposition had declined it for cost.

**Guard:** `_validate_floor_move` in
[claim_fidelity_lib](../../scripts/claim_fidelity_lib.py), reached from
`validate_claim_fidelity_specs.py`, already queued in `run-quality.sh`.

The predicate is three JSON array-emptiness reads, so it has no false positives by
construction. The obligation resolves structurally: a spec whose deterministic floor is
empty must carry `deterministicFloorMovedTo.assertionIds`, and each id must exist in the
sibling `outcome-assertions.json` AND be `kind: judge`.

The pre-existing check required only that the sibling FILE exist, and said so in its own
docstring: "here we only require it exists so the spec still asserts SOMETHING." That is
satisfied by a file shared with every other spec in the directory, so it bound an emptied
floor to nothing in particular.

**Measurement.** Over the 26 registered specs, **exactly one** has all three floor
channels empty: `evals/cautilus/gather-claim-fidelity/spec.json`. It now declares its move
onto `primary-source-fidelity`, `honest-access-and-capture-accounting`, and
`no-search-widening-substitution` — derived from the spec's own `_comment`, which already
recorded the 2026-07-05 retirement under #411, not invented here.
`test_this_repo_has_exactly_one_emptied_floor_and_it_declares_its_move` pins the count.

**A wrong count was published inside this slice and is corrected here.** An earlier
measurement said TWO, naming `handoff-claim-fidelity/judge-intent.spec.json`. That came
from a two-field predicate that ignored `requiredOpenedReferences`, which judge-intent
carries. The wired validator refused only gather, which is what surfaced the miscount.
This is the release's own defect class — a quantity asserted before it was counted —
occurring in the slice that ships guards against it.

**Remainder, and it is large enough that the guard's name would overstate it.**

- This does NOT detect collapse. It forces a DECLARATION when a floor is emptied. #568's
  actual accident — an upstream planner change making two arms converge while both floors
  stay populated — is invisible to it. Catching that means running both arms and comparing
  outcomes, which is a Cautilus evaluation, ask-before-run, and out of S5's scope.
- It proves the pointer resolves to a real judge assertion. It does not prove that
  assertion covers the discrimination the floor lost.
- **The instrument the floor points to is not executed by any automated gate.** Gather's
  `outcome-assertions.json` says of itself "ADVISORY (grades nothing, does not block)",
  and its judge assertions need a live judge under ask-before-run Cautilus.
  `validate_outcome_assertions.py` checks schema, never execution. So on that spec, three
  deterministic channels are empty and the replacement runs in no automated lane. Under
  #583's own framing this is the more load-bearing remainder, and an earlier version of
  this section did not carry it.
- **On its one live subject the rule's discriminating power is near nil.** Gather's
  sibling file holds exactly three judge assertions and the spec names all three, so the
  satisfying set was forced — "name the judge assertions" and "a sibling file exists"
  pick out the same thing here. The rule has teeth for a directory with many judge
  assertions or a renamed id; it had none to show on this one. Both points from a
  round-1 reviewer.
- The sibling file is shared with `private-saas.spec.json` (resolution is per-directory),
  so the named instrument is not scenario-specific and cannot register a
  public-URL-arm-specific collapse — the arm discrimination #568 lost.
- The cheapest bypass found in review is now closed: a BLANK floor fragment
  (`"requiredSummaryFragments": [""]`) passed validation, counted as a populated channel
  so the move rule never ran, and matched every transcript at grade time. Blank entries
  are refused. A throwaway five-line judge assertion remains a possible bypass; it is
  more expensive and leaves a reviewable artifact.
- **The real uncovered surface is an UNREGISTERED spec.** `validate_registry` validates
  only what the registry lists, and its coverage check is skill-level, so a new
  `evals/cautilus/<skill>-claim-fidelity/<scenario>.spec.json` with all channels empty and
  no registry line is invisible to every gate while still runnable by hand via
  `run_skill_efficiency_ab.py --spec-path`. Pre-existing, and now the widest way around
  this rule. (An earlier version of this bullet named
  `evals/cautilus/skill-experiment/spec.json` instead. That was misleading: it is not a
  claim-fidelity spec at all — it is the skill-clone experiment input, with no floor
  concept in its schema — so "all three channels empty" was true only in the way it is
  true of any JSON object lacking those keys. Corrected after a round-1 reviewer read it.)
- #569's general rule (captured fixtures required for external-tool assertions) remains
  declined for cost. `check_quality_tool_fixtures.py` covers the fixtures that exist and
  is queued; nothing requires one to be created.

## #582 — proof and evidence infrastructure is prose, not schema

Narrowed by owner ruling to **#525 alone**. Every other member defers with its
measurement attached, which the
[class-survival review](./2026-08-10-umbrella-class-survival-review.md) already records
per member.

**Guard: already shipped in `28be0bf2a`**, before this slice. `_evidence_targets` in
[readme_proof_ledger_lib](../../scripts/readme_proof_ledger_lib.py) resolves every
Evidence cell to a repo-relative path and refuses one that does not exist; consumed by
[specs/readme-proof.spec.md](../../specs/readme-proof.spec.md). S5 owed the measurement
and the rulings, not code.

**Measurement.** 11 ledger rows are currently bound. Replacing one row's evidence link
with a deleted path is refused (`Evidence reference does not exist`), and replacing the
cell with free text is refused (`without free-text residue`) — the shape the old
string-presence gate passed.

**Reachability, proven rather than assumed**, because #586's shape is exactly a check
nobody reaches: `specs/index.spec.md` links the spec, `scripts/specdown_ephemeral_config.py`
builds the entry from it, and a real `specdown run` reports
`[2/8] PASS README Proof Ledger` and `[4/8] PASS README Proof Ledger > Proof Owners`.
`run-quality.sh` queues that lane.

**Remainder.**

- The gate proves each evidence path EXISTS. It never opens one to check the claim is
  supported. Same residual class as S4's `## References` descriptor rule.
- #524, #514, #535 are untouched here. Their dispositions (declined-for-cost,
  declined-by-operator, ignore-with-reopen-trigger) are recorded in the class-survival
  review, and #582's own body says it "retires by ruling, not by repair".
- The umbrella's self-described largest instance —
  `.agents/quality-adapter.yaml`'s ~530 lines of hand-maintained prose sizing ~120
  machine-checked numbers — is out of scope and gets no guard.

## Review record

Round 1: three bounded read-only fresh-eye reviewers, one per proof surface, all
`parent-delegated`, on window `s5-umbrella-guards-r1`. All three reported blockers, and
each blocker was reproduced by the parent before repair rather than taken on the report:

- **#584 — a regression this slice introduced.** Retro double-disclosure, reproduced as an
  exit-1 crash, repaired above.
- **#586 — four fail-open paths, each reproduced by mutation before and after repair.** A
  `subset` site had no lower bound, so deleting the ledger's `bug` row read as
  `absent_by_design` and passed; `arity` was unvalidated free text, so a one-character
  typo demoted an `exact` site to permissive; a single negative sentinel was defeated by a
  regex loosened to `[a-z][a-z-]*`, which accepts every canonical value and refuses an
  underscore-wrapped sentinel; and a non-`ProbeError` exception escaped `evaluate()`
  entirely, suppressing every other site's verdict including real failures. All four now
  produce fail or not-run, pinned as regression tests. Also repaired: an assumed value
  already in the vocabulary produced an exit-0 run wearing the `hypothetical` badge, and
  the module's exit-3 contract did not match `run-quality.sh`, which had no
  unestablished-capable label for it.
- **#583 — the blank-fragment bypass**, above.

Three of this artifact's own claims were falsified by that round and are corrected in
place rather than silently edited: the "three planners now delegate" sentence, the
skill-experiment bullet, and the absent "instrument is never executed" remainder. Two
tests were also found to prove less than their names: the site-roster test derived both
sides from the same source, and the queue test matched a substring a commented-out line
would satisfy.

Round 2 read the repairs on window `s5-umbrella-guards-r2`, and **earned its keep — it
found defects IN round 1's repairs**, which is the measured claim the two-round floor
rests on:

- **The #584 quality-planner repair shipped unverified.** Round 1's fix changed
  `{ref.get("base"): SKILL_ROOT}` to a literal `{None: SKILL_ROOT}`, but the existing
  assertion reached `unknown-base` through the PATH guard, not the base guard, so
  reverting the fix left every test green. Now pinned by a test that declares
  `base: repo`; reverting the map makes it fail.
- **The retro repair moved `available` from `is_file()` to `exists()`**, so a directory
  row now reads `available: true` beside `unavailable_reason: not-a-file`. Correct by
  design — the path is there to open and is not a file to size — but it was the one row
  with no measurement assertion, which is how the pre-repair double disclosure hid there.
  Now asserted.
- **The blank-entry refusal was in the optional-list helper only**, leaving the strict
  sibling `_validate_string_list` with the same hole and nothing recording why they
  differed. Hoisted into `_refuse_blank_entries`, which both call.
- Round 2 also walked `measure_read`'s rewritten branch case by case — zero-byte file,
  broken symlink, FIFO, TOCTOU delete, permission-denied parent — and found no divergence
  from the pre-repair ordering. A zero-byte file discloses `size_bytes: 0` because the
  sentinel is `size is not None`, not truthiness.

Carried, not fixed, with its reason:

- `tests/quality_gates/test_quality_run_read_measurement.py` asserts `stat-failed` for a
  symlink loop. That holds on this repo's Python (3.10.12, measured) because
  `Path.resolve()` raised `RuntimeError`; on 3.11+ `resolve()` returns the path instead
  and the disclosure becomes `missing`, so the assertion would fail there. Pre-existing
  and adjacent to this slice. Recorded rather than silently widened: relaxing an
  assertion in a surface this slice was not asked to change, without measuring on the
  version in question, is not a repair.
- `run_plan_envelope` discloses `unknown-base` when the PATH is missing or non-string,
  which names the wrong thing — the base was found, the path was malformed. It is also
  what let the F2 defect above look covered. Left as-is; a distinct reason would need the
  vocabulary widened, which is a contract change.

The parity gate's round-2 pass found more, including one defect the ROUND-1 REPAIR
created and one it unmasked:

- **BLOCKER: the new gate broke a different gate.** `check_timing_layer_completeness.py`
  requires every `queue_*` label to carry a row in
  [validator-timing-layers.md](../../docs/conventions/validator-timing-layers.md), and
  queueing the parity gate without one made that check exit 1 — a red gate on a surface
  the parity gate's own tests all reported green, which is #586's exact shape reproduced
  by the fix for #586. Reproduced (`1 run-quality validator(s) have NO timing verdict`),
  row added, now exit 0.
- **FAIL-OPEN that round 1's repair 7 unmasked.** Both liveness guards asked whether a
  site accepts `canonical[0]` — `bug`. A site that had merely DROPPED `bug` was therefore
  indistinguishable from a broken probe: it raised `ProbeError`, resolved to not-run, and
  once the label became unestablished-capable the whole quality run exited **0** on a real
  parity break. Measured before and after: dropping `bug` from the release CLI choices or
  from the commit-msg regex now reports `fail` (exit 1) where it reported `not-run`
  (exit 3). Liveness now means "observes anything", not "accepts bug". Repair 7 did not
  create this; it removed the accident that was masking it.
- `SystemExit` is `BaseException`, so it escaped the broad handler the docstring said
  caught everything — and a probed module growing an import-time `sys.exit` would have
  ended the process at exit 0 with no payload, the strongest fail-open available. Caught
  now; `KeyboardInterrupt` deliberately still is not.
- The ledger probe asked whether `classification_requirements` returned something other
  than `DEFAULT_FIELDS`. That proxy breaks the moment a classification is given an
  explicit row equal to the default: the gate reports it missing and prints a remedy that
  cannot be satisfied, because the row already exists. The ledger now exposes
  `has_classification_row` and the probe asks that.
- The `absent_by_design` staleness check was one-directional. A declared absence that is
  no longer absent had become a standing exemption licensing a later deletion; it is
  not-run now.
- The `fail` remedy was unconditional and wrong for the over-permissive failure mode
  ("add the missing classification" when nothing is missing). It branches on which mode
  fired.
- Repair 7 itself had **no test** — reverting the label was invisible. Pinned, along with
  the dropped-classification, stale-exemption, and row-membership behaviours above.

Also removed: dead scaffolding in a test (`_gate.evaluate.__wrapped__` and a vacuous
`assert result is None`) that would have silently run the real `evaluate` against live
`SITES` before the monkeypatch if `evaluate` were ever decorated.

Round-2 repairs are **accepted-unreviewed** at the two-round cap. That is a real
exposure here rather than a formality: this round changed verdict logic in
`_judge_site`, the liveness guards, and the ledger accessor, and nothing has read those
changes with fresh eyes.

## Non-claims

No push, tag, version bump, publish, hosted CI, installed-consumer readback, or issue
closure. No umbrella is closed by this slice: #586's instances 2-5, #584's non-read
surfaces, #583's collapse detection, and #582's other three members are all live. The
guards are queued in this repo's own quality run; no consuming repo was inspected.
