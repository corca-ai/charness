# Release v8 Artifact Corpus Drift Debug
Date: 2026-08-30

## Problem

The first v8 publish execution stopped in `pytest-release`: the artifact
referent corpus gate returned nonzero and the inventory-consumption probe
reported live artifact count 158 versus recorded 156. The helper restored HEAD
`6b0266d3f` and `charness-artifacts/release/latest.md` before any release commit,
tag, push, or GitHub release mutation.

## Correct Behavior

Given identical tracked release-candidate bytes, the release-only suite must
produce the same verdict in a clean clone and a long-lived authoring clone. A
dated measurement remains historical evidence; the current corpus is judged by
live rule-sensitive invariants rather than exact equality to mutable counts.

## Observed Facts

- `pytest-release` ran 8,684 tests: 8,682 passed and the named corpus tests failed.
- The inventory failure is exact: `live["artifacts"] == 158`, recorded value 156.
- The artifact-referent failure tail lists grandfathered records, so the tail
  alone does not identify the new blocking referent.
- Release rollback reports `status: restored`, original HEAD, and empty remaining
  status.

## Reproduction

- Candidate clone `6b0266d3f`: both focused nodes fail. The referent checker
  names `d309412d6` at Goal Draft lines 196 and 199; the probe is 158/156.
- Parent `8d82b0608` in the shared-object Goal worktree: referents pass but the
  probe fails at the same 158/156 identity.
- In the candidate clone, `git cat-file -t d309412d6` and provider-ref search
  fail. The shared-object worktree sees the object through unrelated local
  history. Tracked Goal bytes are identical.

## Candidate Causes

- Disconfirmed A: the new release records are outside both scanners' configured
  corpus; parent reproduces the inventory drift.
- Confirmed B: commits `029b2c6e6` and `f449f4a07` added the missing top-level
  quality records after probe HEAD `143801359`; the rule-sensitive floor,
  lowered-citation set, label minimum, and floor-20 counterfactual are unchanged.
- Disconfirmed C: the helper restored its temporary release pointer; the focused
  failures reproduce without a prepared release file.
- Confirmed D: referent resolution equates local object presence with durable
  provider-history identity and has no exact declaration for intentional
  local-only context.

## Hypothesis

- Falsifiable claim: the inventory arm clears without refreshing the dated
  probe when live rule-sensitive fields remain safe; the referent arm becomes
  clone-stable only when durability uses HEAD reachability and the two intentional
  local-context sites have an exact, reasoned declaration. Disconfirmer: the
  focused nodes still disagree between a shared-object worktree and clean clone.

## Verification

- Result: resolved — 117 focused tests pass, including side-branch presence,
  absent/non-commit objects, shallow history, exact and malformed declarations,
  changed line context, untracked declaration bytes, each live safety negative
  control, and the two original corpus consumers. The full referent corpus is
  clean with two declared-local findings still visible. One ancestry snapshot
  reduced that check from about 60.5 seconds to 2.73 seconds.
- The first broad retry passed 8,698 tests and exposed one consequence: removing
  mutable probe equality left `probe_drift_message` with zero production callers.
  Its own caller-derived guard refused the dead owner. The inventory message,
  constants, and dedicated test matrix were deleted; the independently live
  evidence-residual diagnostic moved to its own support owner and 47 focused
  tests pass across that boundary.
- The next broad retry passed all 8,699 tests and 80 of 82 release gates. The
  remaining generated seam index was refreshed by its owner. Maintainer setup
  also exposed that `install-git-hooks.sh` chmodded every `.githooks` file,
  making the sourced `runtime-env.sh` executable and dirtying the clean clone.
  Installation now chmods only the three Git entrypoints; 14 hook tests include
  the non-executable helper negative control.

## Root Cause

Two independent stale assumptions met in the release-only suite.

1. A historical observation was promoted into a rolling contract: exact corpus
   volume and residual counts were compared even though valid corpus growth is
   expected and the safety rules derive from different fields.
2. `git_commit_exists` asked `cat-file`, which answered whether this clone had an
   object, not whether published HEAD supplies it. The Goal Draft intentionally
   records excluded local context, but the gate has no structured declaration
   for that distinction. A maintainer object database therefore supplies proof
   that a provider clone cannot reproduce.

The pattern-of-patterns is one authority error: ambient authoring observations
(a local object database and a dated payload) were treated as durable truth.
The repair therefore changes authority at both seams instead of updating the
two failing values.

A sibling pattern was also confirmed: retaining a richly tested helper after
its final consumer disappeared would preserve ceremony without a JTBD. The
helper's own caller guard made that structural deletion mandatory.

The hook failure was the same ownership error at a filesystem boundary:
directory membership was treated as executable-role authority. The installer
now classifies entrypoints explicitly instead of mutating every sibling.

## Invariant Proof

- Invariant: a release evidence commit is responsible only for corpus deltas it introduces.
- Producer Proof: the live measure reports 158 artifacts with unchanged floor 5,
  empty lowered citations, and label minimum 7; Git reports no `d309412d6` object
  or provider ref in the clean clone.
- Final-Consumer Proof: the exact release pytest nodes reproduce 158/156 at both
  revisions and the referent disagreement only across object databases.
- Interface-Shape Sibling Scan: probe equality and referent resolution are
  separate consumers with the same ambient-observation-as-authority failure.
- Non-Claims: no mutation-stage result and no public release result exists.

## Detection Gap

- Quality Core versus release pytest | the mutable corpus equality and clone-safe
  referent consumer were not exercised | keep release pytest as the detector and
  add focused clean-vs-side-branch fixtures at the referent owner.

## Sibling Search

- Mental model: local availability or a prior green is treated as durable current evidence.
- same layer: historical probe treated as rolling baseline | decision: same bug, fix now | proof: executable live invariants
- abstraction up: local object presence versus HEAD reachability | decision: same bug, fix now | proof: clean/shared-object differential
- specialization down: exact local-only Goal context needs a reasoned declaration | decision: same bug, fix now | proof: two blocking sites
- cross-file: `tests/quality_gates/test_artifact_referents.py` and `tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py`

## Seam Risk

- Interrupt ID: release-v8-artifact-corpus-drift-2026-08-30
- Risk Class: host-disproves-local, repeated-symptom
- Seam: published HEAD reachability versus authoring-object visibility, and dated measurement versus live corpus.
- Disproving Observation: shared-object parent green and clean-clone parent-equivalent bytes red.
- What Local Reasoning Cannot Prove: public install behavior.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-30-release-v8-clone-stable-proof-baselines.md

## Prevention

Keep the dated corpus probe unchanged and derive current safety live. Make
commit durability HEAD-reachable, and represent intentional local-only context
in an exact declaration bound to the candidate index, artifact line SHA-256,
token, and reason. Refuse stale, malformed, untracked, unstaged, and shallow
history states. The ancestry owner reads HEAD once; the corpus check fell from
about 60.5 seconds to 2.73 seconds while the 117 focused tests passed.
Delete diagnostic owners when their final live caller disappears; do not add a
fake caller merely to preserve their tests.
Install scripts must mutate only files whose role requires mutation; sourceable
helpers do not inherit executable ownership from their directory.
