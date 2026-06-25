issue: summarize created issue body in closeout

Closes #403.

Jtbd: After `issue new` creates a GitHub issue, the requester sees the created
issue title and a short summary of the filed body instead of only a link.

Boundary: This resolves the upstream issue skill contract and helper payload for
issue creation closeout; it does not add an automatic prose renderer or run a
live issue-create dogfood write.

Resolution Brief: inline (no pause)

Implementation: `issue_create.py` now emits a bounded `body_preview` beside
`body_verified`; the issue skill and closeout-discipline references require the
verified ledger plus title/body summary and an unverified-body warning; backend
docs and public-skill dogfood evidence were updated; plugin mirrors were synced.

Prevention: Focused tests pin hostile-body preservation, preview truncation, and
the closeout contract template requiring title, `body_preview` summary, and
verification warning.

Critique: charness-artifacts/critique/2026-06-25-issue-403-create-closeout-summary.md

Behavior: verified through local focused tests
`tests/quality_gates/test_issue_create.py` and
`tests/quality_gates/test_issue_closeout_discipline.py`, plus deterministic
skill/package/dogfood validators; no live GitHub issue-create write was run.

AI-provenance: Codex agent authored the implementation, tests, docs, and carrier.
