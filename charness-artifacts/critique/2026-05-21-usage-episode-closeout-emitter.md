# Usage Episode Closeout Emitter Critique

## Execution

Fresh-eye critique ran through parent-delegated bounded subagents:

- code correctness and validation semantics
- privacy and operability
- counterweight triage

Packet consumed:
[2026-05-21-120328 packet](./2026-05-21-120328-packet.md).

## Change

Implement the first opt-in usage-episode emitter path for #188. The chosen
workflow is `slice_closeout`: after `run_slice_closeout.py` completes
successfully, it appends one privacy-safe `usage_episode` JSONL record only
when the usage-episodes adapter is enabled.

## Act Before Ship

- Avoid making disabled closeout fragile in bootstrap runtimes. Done by adding
  `PyYAML` to `packaging/bootstrap-requirements.txt`; the existing validator
  already imports YAML.
- Add failure-semantics coverage for invalid adapter/config. Done with a
  closeout CLI test that proves an invalid enabled adapter fails after verify.
- Rotation was advertised by the adapter but initially not enforced by the
  emitter. Done with size-triggered local JSONL rotation before append.

## Bundle Anyway

- Assert top-level closeout status in the enabled-emission test. Done.
- Keep error payloads bounded rather than echoing raw schema/YAML exception
  content. Done.
- Update stale docs and adapter comments so they say capture remains disabled
  until maintainer opt-in, not until emitter work lands. Done.

## Over-Worry

- Blocking on aggregation or quality summaries is out of scope for #188. This
  slice ships one emitter path, not analytics.
- Blocking on richer episode semantics such as `feedback_signal`, issue ids, or
  artifact paths is unnecessary. The schema makes those optional or
  product-owned, and the emitted record stays privacy-safe.

## Valid But Defer

- A future summary command can aggregate usage episodes by `selected_job`,
  `core_action`, `outcome_status`, `feedback_signal`, and `t_status` after real
  records exist.
- Timestamp format checking inside the emitter can stay delegated to the
  existing validator because the emitter controls the timestamp.

## Verification Notes

- Focused tests passed for enabled emission, disabled skip, invalid adapter
  failure, rotation, valid JSONL validation, and malformed JSONL rejection.
- `ruff check scripts/run_slice_closeout.py
  plugins/charness/scripts/run_slice_closeout.py
  tests/quality_gates/test_surface_obligations.py` passed.

## Post-Commit Repair Critique

Pre-push found two valid quality-contract misses: `no_adapter` was an
undeclared closeout attention state, and the implementation made
`run_slice_closeout.py` too long. The repair keeps the validators intact:
usage-episode emission moved to `scripts/slice_closeout_usage_episode.py`, the
new helper declares its `disabled` and `no_adapter` states, and usage-episode
tests moved out of the broad surface-obligation module. This is the right
direction because it reduces orchestration weight while preserving the privacy
and operability behavior reviewed above.
