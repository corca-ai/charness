# Goal 798 Consumer Journey Comparison

> Date: 2026-09-06
> Protocol: frozen revision 3 in `protocol.md`
> Status: parent-delegated read-only judgment; not configured-review approval

## Outcome

All four producer arms completed without prompt intervention. Journey A baseline
and candidate pass the frozen 4-check oracle; Journey B baseline and candidate
pass the frozen 8-check oracle. Both A handoffs preserve exact spec ancestry and
both B arms implement in the first context without a continuation.

| Arm/phase | Output commit | Duplicates | Tokens | Exec seconds |
| --- | --- | ---: | ---: | ---: |
| A baseline spec | `47907e7f4404fb869bbd6265af3007158ff5ec2f` | 3 | 140,810 | 657.014 |
| A baseline impl | `36008e55fff4c03bef0794539954d92be91bc3d4` | 0 | 77,118 | 196.831 |
| A candidate spec | `032b7d84474fe0524f97ea036d586b3b17116f66` | 0 | 114,453 | 415.150 |
| A candidate impl | `2f1f885deb89bb916d7dfd3e76faaa0e3300a6de` | 5 | 74,300 | 228.729 |
| B baseline | `5cf9b39fb50ef0a77c245a569c4bcf92bbb95f4f` | 11 | 126,035 | 610.259 |
| B candidate | `9eafbc46ae865d383902ca293f18c4ac5251357f` | 9 | 124,385 | 451.080 |

A baseline totals 3 duplicates, 217,928 tokens, and 853.845 execution
seconds; candidate A totals 5, 188,753, and 643.879. B moves from 11 to 9
duplicates and from 610.259 to 451.080 seconds, while tokens move from 126,035
to 124,385. These are two single paired observations: candidate runs were
faster here, but A repeated work increased and B reference repetition did not
improve. The evidence does **not** support a generalized speedup or causal claim.

## Strict duplicate adjudication

The unit is one repeated file-read/check operation on unchanged input after
usable evidence. First reads, zero-output recovery, changed-input tests,
independent acceptance, direct smoke, and final diff/status hygiene are excluded.

### Journey A baseline: 3

```sh
# Initial usable content: trace 983-993.
sed -n '1,360p' "$PLUGIN/shared/references/fresh-eye-subagent-review.md"
sed -n '1,360p' "$PLUGIN/shared/references/source-bound-records.md"
# Repeats: 2601 and 3618.
sed -n '1,240p' "$PLUGIN/shared/references/fresh-eye-subagent-review.md"
sed -n '1,180p' "$PLUGIN/shared/references/source-bound-records.md"
# Unchanged src/tests: first 1741, repeated 8648.
python3 -m unittest discover -s tests -v
```

Spec contributes 3; impl contributes 0. Impl's broad command at 967 emitted no
usable content, so bounded reads at 1004, 1471, and 1995 are recovery.

### Journey A candidate: 5

```sh
# Four impl refs first read visibly at 224-225, then re-read at 2192-2223:
sed -n '1,260p' "$PLUGIN/skills/impl/references/adapter-contract.md" >/dev/null
sed -n '1,260p' "$PLUGIN/skills/impl/references/contract-consumption.md" >/dev/null
sed -n '1,260p' "$PLUGIN/skills/impl/references/design-lenses.md" >/dev/null
sed -n '1,260p' "$PLUGIN/skills/impl/references/sequence-discipline.md" >/dev/null
# Same code/test revision: first 905, repeated 2333.
python3 -m unittest discover -s tests -v
```

Spec contributes 0; impl contributes 5. `git diff --check` at 1032 and 2333 is
reported as a repeated unchanged-input hygiene check but excluded consistently
with the baseline closeout-hygiene rule. The suite at 2803 follows the code/test
patch at 2575 and is not a duplicate.

### Journey B baseline: 11

```sh
# All create-cli refs read at 521; four repeated at 696:
sed -n '1,280p' "$PLUGIN/skills/create-cli/references/intent-first-grammar.md"
sed -n '1,220p' "$PLUGIN/skills/create-cli/references/machine-readable-state.md"
sed -n '1,320p' "$PLUGIN/skills/create-cli/references/install-update.md"
sed -n '1,320p' "$PLUGIN/skills/create-cli/references/quality-gates.md"
# Third install/update read at 8918:
sed -n '100,280p' "$PLUGIN/skills/create-cli/references/install-update.md"
# Four shared refs read in the 8911 sweep and repeated at 11442:
sed -n '1,260p' "$PLUGIN/shared/references/{binary-preflight,external-capability-proof-ladder,prescribed-path-self-test,source-bound-records}.md"
# After green 13213 and README-only patch 13685, repeated at 14591:
python3 -m unittest discover -s tests -v
python3 -c 'compile(open("repoctl").read(), "repoctl", "exec")'
```

The 20-file shared sweep is broad waste, but first-time reads are not added to
the strict count. Final diff/status/summary remain hygiene evidence.

### Journey B candidate: 9

```sh
# All content first visible at 469-1920; four repeats at 1921:
sed -n '1,260p' "$PLUGIN/skills/create-cli/references/{intent-first-grammar,machine-readable-state,quality-gates,version-provenance}.md"
# Five repeats at 2283:
sed -n '1,220p' "$PLUGIN/skills/create-cli/references/install-update.md"
sed -n '1,180p' "$PLUGIN/skills/impl/references/adapter-contract.md"
sed -n '1,140p' "$PLUGIN/skills/impl/references/contract-consumption.md"
sed -n '1,140p' "$PLUGIN/skills/impl/references/design-lenses.md"
sed -n '1,180p' "$PLUGIN/skills/impl/references/external-api-contract.md"
```

Reference duplicates remain 9 versus baseline 9. Executable duplicates are 0
versus baseline 2: the final 10-test run follows a test-file change.

## Semantic handoff and source disposition

- A baseline: spec `47907e7` is the exact impl base and ancestor of `36008e5`;
  SC-1 through SC-7 map to 11 tests. Only source/tests change after handoff.
- A candidate: spec `032b7d8` is the exact impl base and ancestor of `2f1f885`;
  SC-1 through SC-10 map one-to-one to 10 tests. The malformed-input probe ran;
  fixed/deferred choices and readiness remain explicit; the spec is unchanged.
- No post-handoff relaxation is visible in either A implementation.
- Every producer actually reads its primary skill and manifest from the intended
  external baseline or candidate export, not the Charness checkout or installed
  plugin. Candidate A impl abbreviates the final reported paths as `.../plugins`;
  trace identity is correct, but literal consumed-path self-reporting is partial.

## Recoveries and protocol deviation

Cold/path recoveries, excluded from duplicate and intervention counts: A
baseline spec has one wrong shared path; A baseline impl has one zero-output
read recovery; A candidate spec has one wrong `skills/shared` root; A candidate
impl has missing consumer `docs/index.md` and one wrong `skills/shared` root; B
baseline has an outside-worktree patch rejection, a rejected destructive-cleanup
probe, one test-guided repair, and wrong shared paths; B candidate has one wrong
shared inventory path and one lane-root patch target. The local durable-capture
rerun also had one misspelled environment variable before the successful oracle
run; it never loaded the fixture and is not an arm intervention.

Frozen protocol says 1800-second Codex timeout. All six task receipts record
`timeout_seconds: 3600`, a +1800-second per-run deviation. Both paired arms used
the same actual setting, so within-pair settings remain equal, but strict
protocol conformance is false and the deviation must accompany comparisons.

## Release-equivalence boundary

The candidate traces do not content-read or execute the subsequently modified
`quality/SKILL.md`, `critique/scripts/run_review.py`, or
`critique/scripts/run_review_packet.py`. Candidate A impl trace line 2001 only
lists `quality/SKILL.md` during a `find`; it does not read it. Release equivalence
therefore binds the actually consumed spec/impl/create-cli skill files, usable
reference content, manifests, and invoked shared scripts—not false whole-package
byte equality across these unrelated deltas.

## Trace SHA256

```text
A baseline spec  2575bcbf55e8230e489c0b55851b64dac2206ea3f8967811eb2a64db3d9f6cb1
A baseline impl  167b2f4d46d395f142ec492cc288c3f9e92e8d90196cb0454b3f787b6dc92d87
A candidate spec bef3c8186fde4ec445565dc44690680181ed077a8fe4bca2ab6e33380983ec9c
A candidate impl df988afefaf2ba271d4000e4d69637ca5e0953bb8a15842ad92f788ac394a97d
B baseline       b933b9e79c8794adbc0e29cd821de2bb2e1c7379292e4945f0190de5a144d539
B candidate      a54540699525595217b4db732aed23b932add1b0ca2adb07c89d1cb415ccc5d4
```
