# Resolution Critique: #274 + #261 Mutation Workflow Recovery

Date: 2026-06-02
Target:
`charness-artifacts/issue/2026-06-02-274-261-mutation-workflow-recovery.md`
Fresh-Eye Satisfaction: parent-delegated
Packet Consumed: n/a (no adapter sections)

## Change

Close #274 through a local carrier after fixing the scheduled mutation workflow
dependency setup, and leave #261 open as the bounded mutation-standard policy
question. The fix installs `tokei` before mutation sampling and pins that
ordering in `tests/quality_gates/test_quality_mutation_testing.py`.

## Angles

- Causal review: Kepler (`019e8733-4375-73b0-9279-6f5632c70f64`)
- Closeout/proof integrity: Kuhn (`019e8735-9c30-71f3-8077-373c66412a32`)
- Workflow dependency and recurrence risk: James
  (`019e8735-b64f-7a30-b66e-0ff340277f62`)
- Counterweight: Pascal (`019e8735-d286-7322-82a1-272aee83c2d2`)

## Act Before Ship

- Create this critique artifact and keep the carrier's `Critique:` line as a
  same-line checked-in path so `validate-closeout-draft` can prove the
  resolution critique ran.
- Update the goal ledger before final closeout so Slice 3 and final
  verification do not remain `N/A`.

## Bundle Anyway

- Strengthen the workflow-ordering test so it asserts both `cargo install tokei`
  and `tokei --version` occur before `Select mutation sample`.
- Add `cargo --version` before `cargo install tokei` so a future runner-image
  drift is easier to diagnose from logs.
- Keep the #274 closeout text explicit that this is local/root-cause proof and
  that a post-fix GitHub Actions run has not been observed.

## Over-Worry

- Do not block this closeout on `yq`. The failing remote run reached `Select
  mutation sample`, so adapter parsing had already passed.
- Do not change StrykerJS config. The current failure skipped `Run mutation`,
  and local evidence shows StrykerJS writes the configured JSON report when it
  actually runs.
- Do not rerun the full coordination-cues survivor campaign before this carrier.
  #261 remains open for the equivalent/low-value policy boundary.
- Do not change generated stack-neutral mutation workflow templates in this
  slice; this repo's checked-in workflow carries its stack-specific setup.

## Valid But Defer

- The mutation summary can still report a missing JS JSON artifact after an
  upstream sample failure. Defer a diagnostic-reporting issue unless the next
  post-fix run still fails or keeps producing misleading comments.
- A broader pre-sample validation-binary setup hook for generated templates may
  be useful, but it is not required to resolve the current #274 failure.
- Remote GitHub Actions proof remains pending until the fix is published and a
  fresh scheduled or manual mutation run is observed.

## Next Move

Run focused workflow tests, issue draft validation, changed-surface checks, and
final slice closeout. Commit the carrier with `Close #274` in the direct-commit
body while leaving #261 open with the drafted comment.
