# Issue 176 Closeout Verifier Critique

- Date: 2026-05-19
- Target: `issue_tool.py verify-closeout` for GitHub issue-resolution final handoff
- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: n/a (issue, debug substrate, implemented diff, and slice closeout output)

## Change

Add an executable issue-resolution closeout verifier so Charness does not rely
on public-skill prose alone for GitHub auto-close carriers. The verifier checks
direct commit bodies, PR bodies, and manual fallback comments for selected issue
numbers, classification-specific closeout ledger fields, and final GitHub issue
state when `--expect-state CLOSED` is supplied.

## Design Critique

### Act Before Ship

- Split `carrier_verified` from final `status: verified`; final handoff cannot
  be text-only.
- Require explicit `--classification` so ledger checks match the issue class.
- Use the selected issue backend's `view` command, including `{json_fields}`.
- Require manual fallback to use a structured reason.
- Require bug sibling closeout fields to carry decision and proof language, not
  empty headings.

### Bundle Anyway

- Treat PR body verification as a pre-merge carrier audit unless paired with
  final GitHub state verification.
- Document the release helper as the already-covered sibling; do not rework it
  in this slice.

### Over-Worry

- Full GitHub lifecycle causality proof is beyond this helper; final issue state
  is the closeout boundary for this slice.

### Valid But Defer

- A central `issue resolve` runner that makes the verifier impossible to skip.
- Rich merge/squash body archaeology after PR merge.

## Implementation Critique

### Act Before Ship

- The first implementation accepted repo-qualified close keywords for the wrong
  repository. It now accepts unqualified `#N` or a qualifier matching `--repo`;
  wrong-repo qualifiers are covered by tests.
- The first implementation checked final state but not returned issue identity.
  It now fails when backend `view` returns a different issue number.
- The first implementation could verify a local manual fallback body without
  proving it was posted. Manual fallback final verification now requests
  `number,state,url,comments` and requires an exact comment-body match.

### Bundle Anyway

- Added direct tests for PR-body carriers, wrong returned issue numbers, open
  final state, and unposted manual fallback comments.

### Over-Worry

- Requiring `close-with-comment` itself to prove exact posted comment before
  this verifier ships. The documented final gate is `verify-closeout`.

### Valid But Defer

- Enforce verifier invocation from a central issue-resolution runner.
- Prove that a carrier commit or merge body is reachable from the default
  branch, not only that the issue is closed.
- Require the manual fallback body reason text to semantically match the CLI
  enum.

## Proof

- Causal review: parent-delegated; root cause was prose-only closeout policy
  without an executable issue-resolution finalization verifier.
- Design critique: parent-delegated; counterweight found no need for broader
  GitHub lifecycle redesign.
- Implementation critique: parent-delegated; counterweight found no remaining
  blocker after wrong-repo, wrong-number, and unposted-comment fixes.
- `python3 -m pytest -q tests/quality_gates/test_issue_skill.py tests/quality_gates/test_issue_closeout_verifier.py`: focused issue tests passed.
- `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`: passed.

## Next Move

Commit the verifier, tests, synced plugin export, debug/dogfood artifacts, and
this critique artifact together, then push and release with issue #176 carried
through the release helper closeout path.
