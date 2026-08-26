# Goal Run `backlog-634` boundary split

## Disposition

Complete only the shipped bootstrap dependency-contract arm. Split the remaining
consumer-boundary residue into successor issue `#735` rather than treating an
umbrella inventory as a complete export repair.

## Evidence

- Exact standing target through `run_standing_pytest.py`:
  `tests/quality_gates/test_export_self_sufficiency.py` — `45 passed`.
- The checked-in export contains `scripts/bootstrap_runtime.py`,
  `packaging/bootstrap-python.json`, and `packaging/bootstrap-requirements.txt`.
- The documented-entrypoint availability arm returns no unguarded imports;
  detector fixtures preserve the distinction between declaration and runtime
  availability.
- Existing closed neighbors #618, #670, and #679 were read before the split;
  #735 is the new owner for the distinct remaining instruction/shell/data-reader
  shapes.

## Non-claims

This is not a claim that every exported bare import, cwd-relative instruction,
shell gate, or repo-root data reader is repaired. It does not prove installed
consumer behavior, remote CI, release, push, tag, or fresh-eye review. The
successor issue #735 is OPEN and owns the remaining consumer-boundary work.
Forced handoff and micro-slice rituals are omitted by operator direction.

## External closeout readback

- Successor issue #735 was created with `body_verified: true` at
  `https://github.com/corca-ai/charness/issues/735`.
- The #634 close carrier read preflight state `OPEN`, posted the split-aware
  close comment, closed the issue with reason `completed`, and read back
  `state: CLOSED`.
- The independent `verify-closeout --expect-state CLOSED` returned
  `status: verified` through `issue_verify_closeout@gh`; the skipped fresh-eye
  critique remains an advisory and is not claimed as executed.
- No installed-host adoption, remote CI, push, release, or tag was performed.
