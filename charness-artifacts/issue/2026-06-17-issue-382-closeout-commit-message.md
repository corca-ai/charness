fix(hotl): adjudicate stale proving surfaces before reproof

Close #382.

Issue #382 closeout:
- Classification: bug.
- JTBD: make HOTL proving-surface staleness a candidate signal requiring agent
  adjudication, with explicit dispositions, instead of teaching path-diff as
  automatic proof debt.
- Debug artifact: charness-artifacts/debug/2026-06-17-issue-382-hotl-staleness-adjudication.md.
- Root cause: HOTL collapsed stale-candidate detection and proof-debt disposition in
  the public contract, so a broad path diff could be reported as requiring
  reproof before semantic review.
- Siblings: decision: bundled the plugin mirror; proof: static scan plus mirror parity and final slice closeout
  (plugins/charness/skills/hotl/SKILL.md and
  plugins/charness/skills/hotl/references/ledger-and-dispositions.md);
  reviewed quality/release/HITL stale-signal siblings as intentional boundaries
  for this slice; deferred only future structured ledger-schema hardening.
- Prevention: public HOTL now surfaces `stale_candidate` /
  `needs_adjudication`, enumerates `reproof_required`, `covered_by_tests`,
  `covered_by_newer_proof`, `narrow_surface`, `ledger_outdated`,
  `accepted_risk`, and `deferred`, blocks unresolved adjudication in pre-live
  and completion audits, and avoids claiming a reproof plan as proof.
- Verification: `python3 scripts/run_slice_closeout.py --repo-root .
  --verification-lock --refresh-broad-pytest-proof
  --ack-cautilus-skill-review` completed, including broad pytest.

Critique: charness-artifacts/critique/2026-06-17-issue-382-hotl-staleness-adjudication.md
