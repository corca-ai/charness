# Gather Extracted Content Persistence Subagent Critique

- Date: 2026-05-17
- Target: v0.5.31 opt-in extracted content persistence follow-up
- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: `charness-artifacts/critique/2026-05-17-042429-packet.md`

## Change

Re-review the just-released public URL gather opt-in content persistence path
after v0.5.31. The intended contract is that default gather stores no body
content, and opt-in persistence stores readable extracted text/markdown only,
not raw HTML or API responses.

## Angles

- Broad implementation and release review.
- Code and data-contract correctness review.
- Release, install, and operator-surface review.
- Counterweight triage for surfaced concerns.

## Findings

### Act Before Ship

- JSON/API responses could be persisted as selected content. The support
  acquire helper used HTML tag stripping for every non-markdown response, which
  left JSON essentially raw. This violated the explicit extracted-content
  boundary.

Resolution: JSON-looking responses that parse successfully are no longer
eligible for `selected_content`. Public gather reports opt-in persistence as
`unavailable` when there is no readable extracted text to store.

### Bundle Anyway

- `content_persistence` could differ between stdout and the artifact when a
  selected content object existed but carried empty text.
- Non-positive content caps were accepted, making `0` produce an unavailable
  artifact and negative values bypass most of the cap through Python slicing.

Resolution: gather now computes persistence from the same nonblank extracted
text predicate used by the artifact, and both public/support CLIs reject
non-positive content limits.

### Over-Worry

- The release artifact says public release verification was not checked by the
  helper, while live GitHub verification later confirmed v0.5.31 exists. This
  is helper-scoped wording, not a release defect.

### Valid But Defer

- Make future GitHub release notes self-contained for new user-facing flags.
  This can improve release ergonomics, but it does not change the correctness
  of the code fix.

## Proof

- `pytest -q tests/test_web_fetch_support.py tests/test_web_fetch_content_persistence.py`: 35 passed.
- `ruff check skills/public/gather/scripts/gather_public_url.py skills/support/web-fetch/scripts/acquire_public_url.py skills/support/web-fetch/scripts/classify_fetch_response.py tests/test_web_fetch_support.py tests/test_web_fetch_content_persistence.py`: passed.
- `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`: passed.

## Scenario Review

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json` returned
  `next_action: none` and `scenario_registry_review_required: true`; no
  evaluator run was required without an explicit log-backed proof request.
- The maintained gather scenario in `evals/cautilus/scenarios.json` is
  `gather-adapter-bootstrap`, which maps to `scenario_gather_adapter_bootstrap`
  in `scripts/run_evals.py` and only checks adapter bootstrap/artifact path
  behavior. This slice changes public URL persistence internals, not first-skill
  routing or adapter bootstrap, so no scenario registry mutation is needed.
- The consumer contract was frozen in `docs/public-skill-dogfood.json` with the
  JSON/API raw-body boundary.

## Next Move

Commit the follow-up fix with synced plugin exports, then publish a patch
release so the installed plugin surface receives the correction.
