# Consumer output errata

The independent final consumer reviewer identified a low-severity overstatement
in the captured candidate CLI README: it says repeated options are rejected,
but repeated `--help`/`-h` is accepted. The demonstrated rejection is for
duplicate `--json` and `--dry-run`, as required by the frozen oracle.

This is the corrected interpretation of the README. The captured original
remains byte-identical to the actual producer output; it has not been silently
edited into a stronger first-prompt result. No producer rescue or extra consumer
iteration is claimed. Frozen acceptance remains valid; blanket duplicate-option
rejection is not claimed.

Review: `charness-artifacts/critique/workers/goal798-final-consumer-release/worker-report.yaml`.
