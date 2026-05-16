# Gather Repair Implementation Critique

- Date: 2026-05-16
- Target: gather/web-fetch trace and proof correctness implementation
- Fresh-Eye Satisfaction: blocked
- Host Signal: active Codex tool contract only permits `spawn_agent` when the current task asks for subagent delegation; this slice records deterministic proof and residual risks instead.
- Contract: [charness-artifacts/spec/gather-acquisition-repair-contract.md](../spec/gather-acquisition-repair-contract.md)

## Change

The slice repaired public URL acquisition honesty for `gather` and
`support/web-fetch`:

- non-HTTP(S) URLs are rejected before acquisition tools run
- invalid regex proof is reported as invalid proof, not strong success
- blocker classifications outrank matching caller proof
- skipped domain routes and missing fallback tools remain visible in attempts
- browser network reconnaissance is diagnostic-only
- final status and confidence are derived from `selected_attempt`
- selector-proof wording was removed from the runtime contract
- `gather_public_url.py` writes durable gather records containing the
  `web-fetch` trace JSON

## Angles

- Boundary honesty: checked whether public `gather` can now reach the support
  helper without absorbing site-specific retrieval policy.
- Failure-mode proof: checked that the prior critique's Act Before Ship cases
  have executable regression coverage.
- Operator trace quality: checked that skipped stages and diagnostics cannot
  silently become success.
- Counterweight: separated local deterministic repair from live external
  `defuddle` proof and GitHub issue closure.

## Counterweight Triage

### Act Before Ship

None remaining for this local slice. The named trace/proof failure modes have
focused tests and closeout proof.

### Valid But Defer

1. Live `defuddle` dogfood remains deferred.
   - This machine still lacks the binary, and deterministic command-shape/stub
     tests are the honest local proof level.

2. Raw acquired-content persistence remains deferred.
   - The new public gather helper preserves trace and selected proof, not full
     fetched content bodies.

3. GitHub #169 should stay open remotely until the unpublished local commits
   are pushed or PR'd and accepted.

### Over-Worry

1. Adding a maintained Cautilus scenario for this exact public URL helper is
   not required in this slice.
   - `plan_cautilus_proof.py` reports `next_action: none`; the consumer
     contract is frozen in `docs/public-skill-dogfood.json`, and deterministic
     tests cover the new helper.

## Proof

- `pytest -q tests/test_web_fetch_support.py`: 21 passed.
- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`
- `pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`: 980 passed, 4 skipped.
- `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`: completed.
