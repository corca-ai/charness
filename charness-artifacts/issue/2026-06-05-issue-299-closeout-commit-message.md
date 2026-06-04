Report release-only sentinel coverage

Close #299.

Classification: feature.
Issue closeout carrier: direct-commit.
Issue: #299 Report release-only sentinel coverage for expensive pytest files.
JTBD: maintainers need to see whether expensive pytest files with
release-only boundary tests still retain cheaper standing sentinels before
moving more tests out of standing pytest.
Boundary: advisory quality/test-economics inventory only; no release marker
changes, no new blocking gate, and no release/publication work.
Resolution brief: feature-class issue with no open decisions; implement the
smallest advisory inventory under the quality skill and keep it selected-file
oriented via repeatable `--path`.
Implementation: Added `inventory_release_only_sentinels.py` under the quality
skill to report release-only test counts, standing test counts, standing
sentinel names, and advisory findings for selected pytest files; added focused
unit tests, inventory-dispatch discoverability, plugin mirror sync, and quality
dogfood evidence.
Prevention: Quality review now has a deterministic advisory signal to inspect
standing sentinel coverage before moving more expensive release boundary tests
into `release_only`; dispatch wording says to use `--path` for selected
slow/release-only files because the default scan is broad and advisory-noisy.
Selected proof: `tests/quality_gates/test_release_publish.py` plus
`tests/quality_gates/test_release_publish_real_host_delta.py` report
`release_only=19`, `standing=8`, `standing sentinels=8`, and no findings.
Tests: `pytest -q tests/quality_gates/test_release_only_sentinel_inventory.py`
passed; selected-file inventory output was inspected; slice closeout rehearsal
passed with deterministic validation.
Cautilus: planner reported `required=false`, `next_action=none`,
`must_ask_before_running=true`; no live Cautilus proof is claimed.
Critique: charness-artifacts/critique/2026-06-05-issue-299-release-only-sentinel-inventory.md
