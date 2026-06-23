Resolved #398 by giving diagnostic Cautilus findings a canonical artifact path
that stays separate from the passing-proof `latest.md` contract.

JTBD: A valid negative or diagnostic Cautilus verdict should be preserved,
validated, and linkable from issue work without being laundered into a passing
regression proof.

Boundary: This does not relax `charness-artifacts/cautilus/latest.md`. That
artifact remains the preserve/improve proof carrier for passing closeout. The
new path covers run bundles under `charness-artifacts/cautilus/<run-slug>/`
that contain a `finding.md` plus machine evidence.

Resolution Brief: Added `scripts/validate_cautilus_diagnostics.py` as the
minimal diagnostic-bundle validator. It validates changed bundles by default and
can validate all existing bundles with `--all`.

Implementation: The validator requires a finding title, execution-source
section, verdict section, diagnosis/non-claim/follow-up context, and at least
one parseable machine evidence file (`observed.v1.json`, `summary.v1.json`, or
`report.json`). It is wired into `run-quality.sh`, `.agents/surfaces.json`, the
plugin mirror, tests, timing-layer classification, and artifact policy docs.

Prevention: Future diagnostic Cautilus findings now fail the standing gate if
they are only prose or only raw logs with no machine evidence. The passing-proof
validator remains separate, so negative verdicts cannot satisfy release or
prompt-change proof by accident.

Behavior: confirmed through the new validator against the existing diagnostic
bundle corpus: `python3 scripts/validate_cautilus_diagnostics.py --repo-root .
--all` returned `validated 3 cautilus diagnostic bundle(s)`.

Quality note: pre-push surfaced a dup-ratchet baseline mismatch under the local
nose 0.15.0 family-id set; the gate baseline was refreshed and
`check_dup_ratchet.py --repo-root . --json` returned `ok: true`.

Critique: charness-artifacts/critique/2026-06-23-issue-398-cautilus-diagnostics.md

AI-provenance: agent-drafted via charness issue resolve; human-auditable through
the linked code, validator tests, run-quality wiring, and resolution critique.
