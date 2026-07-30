# Resolution Critique — issue 465 (subprocess-coverage advisory on the changed-line BLOCK)

Date: 2026-07-30
Scope: resolution critique for GitHub issue #465, `corca-ai/charness`.
Classification: `feature` (an advisory added to an existing blocking gate's payload;
no spec/behavior divergence, so not `bug`).

## What the issue asked for

On a changed-line BLOCK, say when a blocked file's tests exercise it somewhere the
coverage data never reached, instead of letting the reader re-derive that diagnosis
once per occurrence (it happened four times in one session). Explicitly not a new
gate and not a blocking condition.

## Carrier lineage

The advisory code landed earlier in commit `8ebe3284` **without** its issue
closeout — that commit's own non-claims say so. This critique is therefore written
from scratch against the shipped surface, and it changed the surface substantially.

## Round 1 — three bounded reviewers over the shipped surface (HEAD `7f383516`)

Reviewer boundary: snapshot/verify around every spawn, window
`w-20260730T073045Z-1920560`, verdict `clean`, drift `[]`.

All three independently returned **NOT closable**, converging on one finding and
requesting the same experiment:

- **The advisory was honest but INERT.** It fired on 1 of 61 recorded baseline
  pairs and on **none** of the four files that motivated the issue. Three of those
  four have no entry in `scripts/boundary-bypass-baseline.json` at all — it is a
  no-increase RATCHET, not a current inventory — and the fourth's test passes no
  `env=`.
- **The one pair that did fire was a misfire.** `test_quality_runner.py` →
  `scripts/record_quality_runtime.py` runs a seeded STUB recorder; the real script
  is never executed by that test.
- **The central premise was asserted from code reading and contradicted by the
  session record.** All three asked for the same measurement.
- `_replaces_environment` answered `{**name, ...}` as *replacing*, breaking the
  module's own stated invariant ("anything unreadable is treated as inheriting,
  because silence is the safe direction") in the unsafe direction.
- No crash guard at the call site: an exception outside the enumerated
  `OSError`/`ValueError`/`SyntaxError` would turn a CLEAN run's exit 0 into exit 1
  — a false BLOCK produced entirely by the advisory.
- Advisory silence carried no reason, so "nothing recorded", "pruned by the
  re-check", and "baseline unreadable" were one indistinguishable empty dict —
  the very class the issue named, recurring on the fix.

### The experiment all three asked for, run

Two measurements with the repo's own producer (`mutation_sampling_lib`):

1. A script whose ONLY exercise is `subprocess.run([sys.executable, <in-repo
   path>])` with an **inherited** environment — no import, no in-process call, no
   copy — **had its executed lines attributed**, with its unexercised branch
   correctly reported missing. The premise HOLDS: a subprocess test is not by
   itself a reason to doubt a BLOCK.
2. A test that `shutil.copy2`s the script into `tmp_path` and spawns the COPY with
   a fully inherited environment attributed **0** lines. The rcfile sets
   `source = <repo_root>`, so the executed file is filtered out.

So the load-bearing mechanism was never the process boundary — it is the
out-of-tree copy (and the env-replacing spawn). The shipped advisory modelled only
the second, which is why it was silent on the reporter's own first instance.

## Round 2 — two bounded reviewers over the REPAIRED surface

Reviewer boundary: window `w-20260730T081023Z-2084173`, snapshot taken before the
spawns. Round 2 again returned **NOT closable**, and caught two blockers the
repair itself introduced — the pattern this repo's Critique Discipline predicts.

- **BLOCKER: the repair shipped the class it fixed.** `_copies_script_out_of_tree`
  matched the copy's **parent directory name** as a quoted literal. Every mutation
  pool script's parent is literally `scripts`, so any test copying *anything* out
  of a `scripts/` directory was reported as copying whichever script it happened to
  mention. Confirmed against real files: `scripts/check_supply_chain.py` and
  `scripts/check_github_actions.py` — both exercised **only** by inherited-env
  spawns at their real in-repo path, i.e. measured — returned
  `['env-replaces', 'out-of-tree-copy']`. False reassurance printed onto a true
  block, which is exactly what round 1 had just repaired.
- **BLOCKER: my own premise measurement was CONFOUNDED.** I measured 143 attributed
  lines from `test_release_narrative_audit.py` and called it a subprocess-only
  control. That file also loads the module in-process via
  `tests/script_loader.load_script_module` (11 sites). The number proved nothing
  about the child. Re-measured with a purpose-built control that has no in-process
  arm; the premise survived, and the confounded figure is gone from the code.
- The unconditional guarantee in the operator text ("a spawn that inherits the
  environment ... **is never named here**") was false under the file-level bound —
  and it was the most reassuring sentence in the text.
- `out-of-tree-copy` asserted a DESTINATION the detector never inspected.
- `scope` made silence legible only in JSON; the human-facing BLOCK narration was
  byte-identical to the pre-#465 gate.
- The advisory keyed on `blocking_targets`, so a file that blocks **without** proof
  targets — whose own `blocking_detail` reads "file not tracked by the test suite
  (subprocess-only or untested)", i.e. the likeliest candidate for this diagnosis —
  was examined zero times.
- A third live surface still asserted the old over-general claim
  (`skills/public/quality/references/mutation-testing.md`), and the corrected DSL
  doc left an unmeasured sibling claim as the sole support for its thesis.
- Round 2 also verified round 1's misfire argument, and confirmed the
  `{**name, ...}` reversal is correct even though it silences two genuine
  PATH-only scrubs in the same file (safe direction, disclosed).

### Round-2 repairs applied

Both mechanisms are now **bound to the call**, reusing
`inventory_boundary_bypass_lib`'s existing spawn recognisers: `env-replaces`
requires the spawn whose COMMAND names this script; the copy mechanism was renamed
`copies-this-script` (naming only what is checked) and matches on a path boundary,
with the parent-directory branch deleted. Verified after the repair: the two false
positives return `[]`, the two true positives still fire
(`validate_maintainer_setup.py` via `copies-this-script`,
`check_python_lengths.py` via `env-replaces`), and the measured in-repo
inherited-env control stays silent. Scope is now narrated to the operator, the
advisory examines `blocking ∪ blocking_targets`, and the confounded figure and the
false guarantee are gone.

Per the two-round cap, these round-2 repairs are recorded as
**accepted-unreviewed**.

## Counterweight — what is NOT a blocker

- The advisory still cannot see a spawn whose command is built from a variable, an
  `env=` passed as a bare name (including the PATH-only dicts
  `tests/quality_gates/support.py` hands to dozens of callers), or a helper that
  `copytree`s a whole seeded repo from another module. All three are silence in the
  safe direction, and all three are now disclosed in `silence_means` and the module
  docstring. Resolving them needs cross-file value tracking, which would trade a
  disclosed false negative for undisclosed false positives on a blocking gate.
- The hardcoded measurement figure is gone; the remaining reference points at the
  docstring rather than at an unpinned integer.
- Cost: `tests_referencing_paths` runs only when something blocked (`if blocked`),
  so clean runs pay one small JSON read.

## Remaining honest gaps (not closed by this resolution)

- The reporter's stated diagnosis for at least one of the four instances was
  **wrong**: `audit_public_release_narrative.py` IS measured from its in-repo
  spawn, so that BLOCK was a true block on a genuinely unexercised branch. The
  four-cycle waste had two causes, not one, and this advisory addresses the two
  detectable ones.
- No claim that the advisory is exhaustive over the ~61-pair baseline or the
  reference map; `scope` states what was examined per run rather than asserting
  coverage of the space.
- `docs/testability-dsl-initiative.md`'s type/mutation claim is now marked
  unverified rather than re-measured.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/subprocess_only_coverage_advisory.py | action: fix | note: round 1 — advisory inert: fired on 1 of 61 baseline pairs and none of the four motivating files; fixed by unioning the test-reference map as a second candidate source
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/subprocess_only_coverage_advisory.py | action: fix | note: round 1 — the load-bearing mechanism (out-of-tree copy) was not modelled at all; measured 0 attributed lines for a copy-spawn vs attributed lines for an in-repo inherited-env spawn
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/subprocess_only_coverage_advisory.py | action: fix | note: round 1 — `{**name, ...}` answered "replaces", breaking the module's own safe-direction invariant and risking false reassurance on a true block
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/subprocess_only_coverage_advisory.py | action: fix | note: round 2 — the copy detector matched the copy's PARENT DIRECTORY name, so any test copying anything out of `scripts/` implicated whichever script it mentioned; confirmed on check_supply_chain.py and check_github_actions.py, both measured
- F5 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-07-30-issue-465-resolution.md | action: fix | note: round 2 — my own premise measurement was confounded (the cited test also loads the module in-process); re-measured with a purpose-built control, premise survived, confounded figure removed from operator text
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/changed_line_run_trust.py | action: fix | note: round 2 — advisory silence was legible only in JSON, so a BLOCK narrated byte-identically to the pre-fix gate; scope is now narrated in the operator's channel
- F7 | bin: bundle-anyway | evidence: moderate | ref: skills/public/quality/references/mutation-testing.md | action: document | note: a third live surface still asserted the over-general "cannot see across the process boundary" claim; corrected alongside the two round-1 surfaces
- F8 | bin: valid-but-defer | evidence: moderate | ref: scripts/subprocess_only_coverage_advisory.py | action: defer | note: cross-module resolution (helper-returned PATH-only env dicts, seeded-repo copytree, variable-built spawn commands) stays unresolved and disclosed; closing it needs value tracking that would trade disclosed false negatives for undisclosed false positives on a blocking gate
- F9 | bin: over-worry | evidence: weak | ref: scripts/suggest_mutation_coverage_command.py | action: defer | note: reference-map cost on a blocking run was raised; the `if blocked` guard keeps clean runs free and the mapper's own prefilter is already the load-bearing guard

## Reviewer Tier Evidence

- Requested tier: high-leverage (issue-resolution closeout review, two rounds).
- Requested spawn fields: n/a — this is a Claude Code host, where the repo's
  per-host subagent split calls for the host's own typed-agent control rather than
  a requested model/effort pair; spawned as the read-only `bounded-reviewer` type
  with session-model inheritance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: five `bounded-reviewer` spawns accepted and
  returned findings inline (round 1 agent ids a1b1d221619ffef3f,
  a334f374c36b4a77f, a5ef85cf19a946bdd; round 2 ae4a24959a6849fec,
  a6fe78294c8cbf3b6).
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepared packet was consumed; each reviewer was given a scoped prompt over
the working-tree surface, and round 2 was explicitly pointed at the repaired
version rather than HEAD. -->

## Boundary Ownership

- Producer: the changed-line gate's coverage producer and blocking payload
  (`scripts/mutation_sampling_lib.py`, `scripts/check_changed_line_mutation_coverage.py`).
- Consumer: the operator reading a changed-line BLOCK, plus JSON consumers of the
  gate report (`scripts/mutation_coverage_producer.py`, the pre-push lane).
- Owning surface: repo-owned quality gate scripts in this repo.
- Verdict: owned-correctly

The baseline, the test-reference map, and the gate payload are all repo-owned
surfaces here, so the fact and its consumer live in the same repo. The advisory
consumes the mapper and the spawn recognisers in
`scripts/inventory_boundary_bypass_lib.py` rather than re-implementing either, and
it added no obligation to any portable skill package. One portable surface was
touched — `skills/public/quality/references/mutation-testing.md` — only to correct
a claim it already made about this repo's producer, with the issue anchor kept out
of the package per the repo's skill-anchor rule.

## Behavior verdict channel

Distinct from `CLOSED` state and the carrier body: direct execution of
`unmeasured_spawn_mechanisms` against real repo file pairs (two false-positive
controls returning `[]`, two true positives firing with named mechanisms, one
measured-in-repo control staying silent), plus the two coverage-attribution
measurements above run through `mutation_sampling_lib.run_test_coverage`.
