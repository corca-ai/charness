# Debug Review
Date: 2026-09-04

## Problem

`./scripts/run-quality.sh --release --read-only` (the 8.2.0 publish lane) exited 1 in `release-changed-line-coverage` with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0` from `suggest_mutation_coverage_command._local_loader_ancestor_levels`, so the release produced no changed-line verdict and the publish helper rolled back.

## Correct Behavior

Given a release delta that touches the root-level `charness` file, when the changed-line gate builds its coverage recommendation, then it renders a verdict; a file it cannot decode is skipped like a file it cannot read, and a root-level changed path scans only its own directory.

## Observed Facts

- The traceback names `candidate.read_text(encoding="utf-8")` inside a `directory.rglob("*.py")` loop guarded by `except OSError` only.
- The only tracked file whose first byte is `0xff` is `native/repograph/fixtures/non_utf8.py` (landed 9d2ba2ff3, 2026-08-28, the #745 Rust parser spike; a deliberate fixture).
- The 8.1.0 lane passed on the same gate; its delta touched no root-level file.
- This delta changes `charness` (help text for `--scope`), whose `Path("charness").parent` is `.`, so the "same-directory" walk became a whole-repo `rglob`.
- The first repair (decode guard only) made the gate run; the second test I wrote asserted a loader relation in a grammar the matcher does not accept, failed, and was committed because `| tail -1` swallowed pytest's exit code in an `&&` chain.

## Reproduction

- `python3 scripts/mutation/release_changed_line_coverage.py --repo-root .` on 62446fd7e (delta includes `charness`): traceback above. Unit: `_local_loader_ancestor_levels(root, "tool.py")` with `deep/fixtures/non_utf8.py` present.

## Candidate Causes

- A file in this delta is not UTF-8 (disconfirmed: every changed file decodes).
- The gate reads a fixture it should never reach because its walk is unbounded for a root-level path (confirmed).
- The runtime root or mirror state was stale (disconfirmed: the crash reproduces on a fresh export).

## Hypothesis

- If the walk is bounded to the flat directory for a root-level path, the fixture is never read and the gate renders a verdict; the decode guard alone also stops the crash but leaves an O(repo) walk. | disconfirmer: run the unit scan on a tmp tree with a nested `non_utf8.py` and a nested loader; the nested loader must not be found for the root file.

## Verification

- confirmed — the unit test `test_loader_scan_for_a_root_level_path_stays_flat` finds only `root_loader.py`; the direct gate run on the committed tree renders a verdict (recorded in the commit).

## Root Cause

`_local_loader_ancestor_levels` promised same-directory loaders but walked recursively; at the repo root that is the whole tree, which holds an adversarial fixture the walk was never meant to read, and the read guard covered `OSError` only.

## Invariant Proof

- Invariant: n/a - not a workflow-boundary propagation bug
- Producer Proof: n/a
- Final-Consumer Proof: n/a
- Interface-Shape Sibling Scan: n/a
- Non-Claims: n/a

## Detection Gap

- release lane | fired, at the last step before tag, after a 183 s lane | the same gate in the full read-only lane the pre-push hook runs; it did not fire there because the gate is release-only, and I ran the full lane instead of the release lane before publishing. Smallest change: run `--release --read-only` locally before invoking the publish helper when the delta touches a root-level file.

## Sibling Search

- Mental model: a "same-directory" scan implemented as `rglob` is bounded only by where it starts; the repo root is the one start that reaches everything, including files kept precisely to break scanners.
- same layer: `scripts/mutation/suggest_mutation_coverage_command.py:225` | decision: same bug, fix now | proof: bounded walk plus decode guard, two unit tests
- abstraction up: every `rglob("*.py")` in `scripts/` and `tools/` | decision: intentional boundary | proof: all start at `tests/`, `scripts/`, an export or package root, or `skills|support|shared` subtrees (`helper_provenance_lib.py:202,272`); none can reach `native/`; `check_prose_pin.py:132` already guards decoding
- specialization down: the decode guard in isolation | decision: same class, diagnostic-only for this slice | proof: kept as backstop; the bound is the fix
- cross-file: `scripts/gates/check_prose_pin.py:132` is the guarded precedent, not a defect
- mental-model siblings: verification output piped through `tail -1` inside an `&&` chain | decision: same waste, fix now | proof: the failing-test commit 67e28cb05; this record's Prevention names the rule

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: none
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Bound the walk (done) and keep the decode guard (done). For the process: a verification command's exit code is the claim; never pipe it through `tail`/`grep` inside an `&&` chain that commits — capture to a file and grep the file. Run the release lane, not only the full lane, before the publish helper when the delta touches a root-level file.
