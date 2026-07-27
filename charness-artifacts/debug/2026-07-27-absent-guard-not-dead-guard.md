# Foreign-Copy Publish Debug: an absent guard, not a dead guard
Date: 2026-07-27

## Problem

Two `v2.11.2` publish attempts run from an installed charness copy died at
`validate-retro-lesson-index` after bump, manifest sync, and the full quality
suite, and rolled back. `require_repo_local_helper` — a guard added for exactly
this failure — never refused, and nothing explained its silence. A maintainer
could not tell which copy of charness they were running, and the gate that did
fire named a remediation (`run --write`) that cannot terminate.

## Correct Behavior

Given an installed charness copy whose libraries have drifted from the target
source tree, when it is invoked with `--repo-root <that source tree>`, then the
run refuses before mutation and names the repo-local command that works.

## Observed Facts

- `~/.agents/src/charness` is a full git checkout (not a flat plugin install);
  `charness update` fast-forwards it.
- `git reflog` there: HEAD sat at `199017ca` (2026-07-26 16:38) until
  `eb90fa08` (2026-07-27 13:32, during the successful publish). `199017ca` is
  therefore the copy that ran both failed attempts.
- `199017ca` vs the pre-release HEAD `4df0393c`:
  `scripts/recent_lessons_lib.py` +123 lines, `scripts/retro_persistence_lib.py`
  +6. The installed copy carried the pre-`independent_source_count` index schema.
- `publish_release_execute.py:37` bumps, `:42-48` runs the retro closeout with
  `execute=True`, `:59` runs quality. The closeout writes before quality.
- `scripts/retro_persistence_lib.py:9` imports `recent_lessons_lib` at module
  scope, so the anchor scan would have seen it at the `:69` guard call.
- `CHARNESS_ALLOW_FOREIGN_HELPER` was unset; no override warning in the run log.

## Reproduction

Minimal, no writes to the real repo — `git archive` both commits to temp trees,
then drive the exact load path:

```text
installed = 199017ca, target = 4df0393c
rt = runpy.run_path(installed/plugins/charness/skill_runtime_bootstrap.py)
mod = rt["load_repo_module_from_skill_script"](<installed publish_release_retro.py>,
                                               "scripts.retro_persistence_lib")
mod.persist_retro_artifact(repo_root=target, ...)
-> RESULT: WRITE PROCEEDED   (guard did not refuse)
```

Module resolution was correct — both libs loaded from the installed plugin tree.

## Candidate Causes

- Control flow: the retro closeout never runs before quality in execute mode.
- Environment: `CHARNESS_ALLOW_FOREIGN_HELPER` set, silently allowing the write.
- State: module shadowing binds `scripts.*` to the target repo, so the guard sees `same-tree`.
- Logic: `is_relative_to` containment escape (`helper_provenance_lib.py:228`) classifies the copy as `same-tree`.
- Absence: the guard is not present in the copy that ran.

## Hypothesis

(5). If the installed copy predates the commit that introduced the guard, then
`scripts/helper_provenance_lib.py` does not exist there and
`retro_persistence_lib` contains no guard call — so nothing refuses, with no
error and no override.

disconfirmer: `git cat-file -e 199017ca:scripts/helper_provenance_lib.py` — one
command, run before any fix; the hypothesis dies if the file exists, or if that
revision's `retro_persistence_lib.py` calls `require_repo_local_helper`.

## Verification

```text
git cat-file -e 199017ca:scripts/helper_provenance_lib.py -> ABSENT
git log --diff-filter=A -- scripts/helper_provenance_lib.py -> a6f6e8fc
git show 199017ca:scripts/retro_persistence_lib.py | grep -c require_repo_local_helper -> 0
git show 4df0393c:scripts/retro_persistence_lib.py | grep -c require_repo_local_helper -> 2
```

Causes 1-4 are refuted by the Observed Facts above; each was checked before this
one was tested.

**Cause 4 is refuted as the mechanism HERE, not as a defect.** The branch was
unreachable twice over: the guard was absent from the copy that ran, and that
copy also lived outside the target root. That branch is still a live escape —
reproduced 2026-07-27, audit id A1 in the
[bug hunt](../audit/2026-07-27-evidence-surface-bug-hunt.md): a copy *inside* the
target root is exempted as `same-tree` with zero files compared, and this repo's
packaging manifest declares the checked-in plugin tree as an install source. Same
failure, different caller. "Refuted" here does not mean fixed.

## Root Cause

The guard did not fail — it was **absent**. `a6f6e8fc` introduced
`helper_provenance_lib.py` in the session immediately before this one, and that
commit was still unpushed when the installed checkout last pulled. The copy that
ran predated the guard by one session.

Five whys: publish failed -> old-schema index written -> installed lib wrote it
-> guard did not refuse -> guard absent from that copy -> **a guard that lives in
the copy being invoked cannot constrain a copy old enough to predate it.**

## Invariant Proof

- Invariant: every artifact written into the target repo is written by code that matches that repo.
- Producer Proof: none available — the producer is the untrusted party, and the producer that failed here carried no enforcement code at all.
- Final-Consumer Proof: the target repo's `validate-retro-lesson-index` rejected the old-schema artifact and the publish rolled back; reproduced twice.
- Interface-Shape Sibling Scan: the other four `require_repo_local_helper` sites share the producer-side placement and therefore the same limit.
- Non-Claims: no claim that other installed copies are drifted, nor that target-side validation catches every foreign write — only this artifact class is covered.

Producer: whichever charness tree supplies the running modules. Final consumer:
the target repo's checked-in artifacts. The invariant — "artifacts are written by
code matching the target repo" — cannot be enforced producer-side, because the
producer is the untrusted party and an old producer carries no enforcement at
all. It held here only because the **consumer** side checked:
`validate-retro-lesson-index` rejected the old-schema artifact and the publish
rolled back. Target-side detection worked and failed closed.

## Detection Gap

`validate-retro-lesson-index` fired correctly; the gap is diagnostic, not
detective. Its message says to run
`build_retro_lesson_selection_index.py --write`, which cannot terminate — the
next run through the same stale copy overwrites the fix, the exact
non-terminating remediation `helper_provenance_lib`'s own docstring was written
to kill. Smallest change that would have shortened this investigation: have that
validator report which tree wrote the artifact, or note that a foreign helper is
a possible cause.

## Sibling Search

Wrong mental model: *"the guard is in the repo, therefore the guard runs."*
Enforcement placed in the invoked copy is unenforceable against a stale copy —
the population that needs it most is exactly the population that lacks it.

- same layer: the four other `require_repo_local_helper` write sites | decision: same waste, diagnostic-only | proof: all live in the invoked copy, so all share the absent-in-stale-copy limit; none is individually wrong
- same guard, different escape: the containment branch that classifies a copy inside the target root as `same-tree` | decision: valid follow-up outside the slice | proof: reproduced 2026-07-27 — a stale checked-in plugin mirror wrote a wrong-schema lesson index with no refusal and zero files compared, and that tree is a packaging-declared install source | follow-up: audit id A1, [bug hunt record](../audit/2026-07-27-evidence-surface-bug-hunt.md)
- abstraction up: the entrypoint guard drafted this session (`publish_release.py`, `issue_tool.py`) | decision: same waste, fix now | proof: it lives in the invoked copy too, so it inherits the same limit; its claim must be reduced from "closes this class" to "defense in depth once installed"
- specialization down: `validate-retro-lesson-index`'s non-terminating remediation string | decision: valid follow-up outside the slice | proof: observed — it sent this investigation to the quality suite first and cost a full gate cycle | follow-up: https://github.com/corca-ai/charness/issues/462
- mental-model siblings: any target-side gate whose message assumes the operator's tooling matches the repo | decision: diagnostic-only | proof: not enumerated; named so the next occurrence is recognized rather than re-derived
- cross-file: `recent_lessons_lib.py`, `retro_persistence_lib.py`, `build_debug_seam_risk_index.py`, `persist_retro_artifact.py` — the other four guard sites, none in the subject file

## Seam Risk

- Interrupt ID: absent-guard-not-dead-guard
- Risk Class: external-seam
- Seam: the installed-copy lifecycle (`charness update` pull cadence), host-managed rather than repo-managed
- Disproving Observation: the guard was checked in and passing every repo gate, yet the copy that ran did not contain it.
- What Local Reasoning Cannot Prove: which revision any given installed copy is at when it is invoked.
- Generalization Pressure: factor-now

Every charness helper that enforces anything from inside the invoked copy
shares this limit, not just this one.

External seam: the installed-copy lifecycle is host-managed (`charness update`
pull cadence), not repo-managed. Local reasoning about "the guard is checked in"
does not predict host state. Any further work here goes to `spec`, not straight
to `impl`, because the enforceable side is the target repo, not the caller.

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-07-27-foreign-copy-write-enforcement.md

Diagnosis complete. The repair question is a design decision, not a bug fix.

## Prevention

- The entrypoint guard is defense in depth, effective one `charness update` after
  it ships — not a closure of this class.
- Enforceable side is the consumer. A target-side check ("which tree wrote this
  artifact") is the only form that constrains a copy that predates the guard.
- Fix the misleading `validate-retro-lesson-index` remediation (issue #462).

## Related Prior Incidents

`helper_provenance_lib.py:5-8` records four earlier publishes lost to this same
shape; this is the fifth and sixth, and the first where the guard existed in the
repo but not in the running copy.
