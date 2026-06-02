# #274 + #261 Mutation Workflow Recovery Carrier

Date: 2026-06-02
Repo: corca-ai/charness
Goal:
`charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`

## Carrier Scope

Close:

- #274 mutation test regression on main

Leave open intentionally:

- #261 mutation-standard policy for equivalent or low-value coordination-cues
  survivors

## Evidence

- Focused implementation commit:
  `ff5591eb Install mutation workflow length gate dependency`
- Closeout hardening: final carrier commit also records critique evidence,
  validates the closeout draft, and pins that `tokei --version` runs before
  mutation sampling.
- #274 latest scheduled failure run:
  `https://github.com/corca-ai/charness/actions/runs/26799230370`
- Latest #274 failure symptom: `StrykerJS JSON report missing` and no mutation
  sample manifest on `4c3dcbe11c92c7ce7c3a24953d3e7fddc677f07d`
- Root-cause proof: run `26799230370` failed in `Select mutation sample`
  because `scripts/check_python_lengths.py` could not find `tokei`; `Run
  mutation` was skipped, so StrykerJS never executed in that run.
- Fix: `.github/workflows/mutation-tests.yml` installs `tokei` and prints
  `tokei --version` before `Select mutation sample`.
- Regression pin:
  `test_checked_in_mutation_workflow_installs_length_gate_binary_before_sampling`
  asserts the workflow installs `tokei` before sampling.
- Local validation: `run_slice_closeout.py --skip-broad-pytest` passed after
  focused pytest, GitHub Actions validation, debug artifact validation, seam-risk
  index validation, documentation checks, packaging checks, ruff, length checks,
  attention-state visibility, and duplicate-pressure checks.
- #261 survivor disposition: prior scoped proof remains 514/514 executed, 467
  killed, 47 survived, 90.9% reachable score; current #274 evidence did not
  touch the coordination-cues survivor surface and does not convert that policy
  residue into a #274 workflow fix.

## Close Comment

Resolved in the #274 + #261 mutation workflow recovery carrier.

JTBD: restore the scheduled mutation gate's ability to select and run its full
mutation sample on `main`, while keeping #261's survivor-policy boundary
explicit.

Classification: bug for #274; #261 is decision-needed after prior mechanical
survivor hardening and remains open.

Root cause: the scheduled mutation workflow ran a sampled pytest coverage probe
that requires `tokei`, but the GitHub runner did not install `tokei` before
`Select mutation sample`. The job failed before producing a sample manifest and
before `Run mutation`; the reported missing StrykerJS JSON file was a downstream
symptom of skipped JS execution, not evidence that StrykerJS itself was
misconfigured.

Debug artifact:
`charness-artifacts/debug/2026-06-02-274-mutation-workflow-tokei-dependency.md`

Siblings: workflow steps and CI-only gates that call repo validators with
external binary assumptions. Decision: bundle the `tokei` install because it is
the concrete missing dependency for the current scheduled mutation sample; defer
the summary wording issue unless the dependency fix fails to recover #274 or
continues to produce misleading downstream report-missing comments. Proof: the
workflow now installs `tokei` before sampling, and focused tests pin the ordering.

Prevention: keep validation binaries explicit in the scheduled workflow before
adapter/sample phases instead of relying on local operator machines or package
requirements to imply non-Python tool availability.

Critique: charness-artifacts/critique/2026-06-02-274-261-mutation-workflow-recovery-resolution.md

Close #274.

Evidence:

- Goal artifact:
  `charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`
- Carrier artifact:
  `charness-artifacts/issue/2026-06-02-274-261-mutation-workflow-recovery.md`
- Implementation commit:
  `ff5591eb Install mutation workflow length gate dependency`

Scope note:

- #261 remains open for the equivalent/low-value survivor policy boundary.
- Remote GitHub Actions proof is not claimed until a fresh post-fix run is
  observed after publication.

## Leave-Open Comment

For #261:

```text
Leaving this open intentionally after the #274 mutation workflow recovery
carrier.

The mechanical survivor-hardening path is already present through `765f5d4`
and the prior scoped proof remains 514/514 executed, 467 killed, 47 survived,
90.9% reachable score. This run fixed #274's current workflow failure by
installing the `tokei` validation binary before mutation sampling; it did not
change the coordination-cues survivor surface and does not resolve the remaining
equivalent/low-value mutation-standard policy question.

Relevant evidence:
- Goal artifact: charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md
- Carrier artifact: charness-artifacts/issue/2026-06-02-274-261-mutation-workflow-recovery.md
- Prior critique: charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md
```

## Non-Claims

- No release is part of this carrier.
- Remote CI or a fresh scheduled mutation run is not claimed until observed
  after push.
- #261 is not closed by this carrier.
