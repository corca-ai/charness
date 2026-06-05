fix(release): make publish resumable, installed-cache-safe, and staleness-checked

Close #305.

Classification: bug.
Issue closeout carrier: direct-commit.
Issue: #305 release publish-flow resilience — not resumable, installed-cache
bootstrap failure, and stale update_instructions go undetected.
JTBD: a maintainer cutting a release must be able to recover a publish that
failed after the local commit+tag (without hand-running push/release/verify), run
the helper from the installed plugin cache, and be stopped before shipping a
release record whose operator update steps still describe the previous version.
Root cause: the helper committed+tagged before its last (push) gate with no
resume path and non-idempotent re-run; `publish_release_retro.py` hardcoded the
repo-layout import `skills.public.retro...` which does not exist in the exported
plugin cache (raising `ModuleNotFoundError: No module named 'skills.public'`); and
the only update_instructions check was the adapter-file-change-triggered
preflight, so stale instructions whose file was not touched were never flagged.
Debug artifact: charness-artifacts/debug/2026-06-05-issue-305-release-publish-resilience.md
Siblings: the sibling search covered the publish control flow (commit/tag/push),
both runtime-bootstrap cross-skill imports in the release scripts, and every
update_instructions consumer (adapter preflight plus the generated release
record); the decision was to add an explicit opt-in `--resume` flow (avoiding the
double-publish hazard) that validates the partial state and re-validates the
push-time gates, make the retro import layout-tolerant (`skills.public.<x>` then
`skills.<x>`, re-raising genuine dependency errors), and add an unconditional
previous-vs-target staleness check; the proof is the release suite plus
tests/quality_gates/test_release_publish_resilience.py (resume idempotent
continue, resume refusal with no partial state, resume requires --publish-current,
exported-layout import, staleness block) all green and the exported plugin-mirror
`publish_release.py --help` running without ModuleNotFoundError.
Prevention: each gap is locked by a regression test, and the public `release`
consumer-contract dogfood evidence freezes the unchanged routing/artifact/output
shape so a regression trips a test or the public-skill validation gate.
Tests: `pytest -q tests/quality_gates/test_release_publish_resilience.py` plus the
release suite (`test_release_publish.py`, `_tag_history`, `_critique_artifact`,
`_retro_trigger`, `_real_host_delta`, `_backend`, `_narrative_audit`) — 63 passed;
`run_slice_closeout.py` deterministic aggregate completed.
Critique: charness-artifacts/critique/2026-06-05-issue-305-release-publish-resilience.md
