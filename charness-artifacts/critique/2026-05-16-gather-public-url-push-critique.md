# Gather Public URL Push Critique

- Date: 2026-05-16
- Target: push-readiness critique for `origin/main..HEAD` gather/web-fetch repair work
- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: `charness-artifacts/critique/2026-05-16-031652-packet.md`
- Prepared For: `gather-public-url-push-critique`

## Change

The reviewed branch repairs gather public URL acquisition trace/proof behavior,
adds the public `gather_public_url.py` helper, syncs plugin export surfaces, and
records the support `web-fetch` route, attempts, selected attempt, and final
disposition in durable gather assets when acquisition succeeds.

## Angles

- Michael Jackson / problem framing: checked that the slice solves truthful
  gather acquisition trace and does not overclaim raw content persistence.
- Gerald Weinberg / diagnostic: checked proof/error precedence and plan-vs-trace
  consistency.
- Atul Gawande / operational checklist: checked public helper exit/write
  behavior, top-level operator signals, and packaging/export readiness.
- Counterweight: reviewed the focused fixes and separated remaining blockers
  from deferrable polish.

## Counterweight Triage

### Act Before Ship

None remaining after the focused push-critique fixes.

Resolved during this pass:

1. Invalid proof could be hidden by transport failure and become degraded.
   - Fix: `invalid-proof` now outranks transport errors in acquisition attempts.
   - Proof: `test_acquire_public_url_invalid_regex_outranks_transport_error`.

2. Planned but unexecuted fallback stages could disappear from `attempts`.
   - Fix: payload emission appends unvisited acquisition-plan stages as skipped,
     not-implemented, or terminally recorded attempts.
   - Proof: `test_acquire_public_url_records_all_planned_stages_as_attempts`.

3. Public gather could write/refresh `latest.md` for blocked or degraded
   acquisitions.
   - Fix: `gather_public_url.py` writes only when acquisition disposition is
     `success`; non-success results return non-zero JSON with top-level
     acquisition state and `write_record: null`.
   - Proof:
     `test_gather_public_url_does_not_write_blocked_acquisition` and
     `test_gather_public_url_does_not_write_degraded_acquisition`.

### Bundle Anyway

- Include the prepare packet files in the same commit as this critique record.
- Keep top-level `acquisition_disposition`, `final_status`, `final_confidence`,
  and `record_status` fields in the public helper response so callers do not
  have to parse nested trace JSON for the common branch decision.

### Valid But Defer

- Raw acquired-content persistence remains a separate gather artifact/content
  policy slice.
- Live `defuddle` dogfood remains blocked by the missing local binary.
- Archive/cache acquisition remains planned but not implemented.
- Skipped reason taxonomy can be refined later; the current values are enough
  to avoid trace omission and are regression-tested.

### Over-Worry

- Writing degraded trace artifacts anyway would reintroduce the `latest.md`
  freshness hazard this pass fixed. Returning explicit JSON without a durable
  current-pointer update is the cleaner contract for this slice.
- Expanding this into a generalized acquisition-state model before push would
  add surface area without addressing a current failing branch.

## Proof

- `pytest -q tests/test_web_fetch_support.py`: 28 passed.
- `ruff check skills/support/web-fetch/scripts/acquire_public_url.py skills/public/gather/scripts/gather_public_url.py tests/test_web_fetch_support.py`: passed.
- Counterweight reviewer also ran packaging, committed-packaging, skill
  validation, and py-compile spot checks with no push blocker found.
- Post-critique pre-push repair: extracted acquisition trace helpers and proof
  preparation helpers to satisfy `check-python-lengths` without changing
  behavior.
- `python3 scripts/check_python_lengths.py --repo-root .`: passed after the
  extraction.

## Next Move

Run the repo surface closeout for the changed files, commit the code, tests,
plugin exports, packet, contract, handoff, and this critique artifact, then
push `main`.
