<!-- charness-work-item-key: backlog-634 -->
# Existing Work Item #634 — Export-only dependency self-sufficiency

## Purpose and premise

Close the repaired dependency-contract arm and census the remaining exported
instruction/data-reader paths from an export-only checkout.

## Owned change and acceptance

Audit cwd-relative commands, shell entrypoints, data readers, and bare imports
through the existing export checker; split any independently owned live defect
instead of hiding it under this child. A clean export-only checkout is required.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_export_self_sufficiency.py`, then changed-line proof. Source checkout success is not installed-layout proof.

## Accepted boundary and successor split

The bootstrap dependency-contract arm is complete: the exported installer ships
`packaging/bootstrap-python.json` and `packaging/bootstrap-requirements.txt`,
and the documented-entrypoint availability gate passes against the checked-in
export. The broader export self-sufficiency inventory is not being claimed as
repaired here.

The remaining consumer-boundary residue is transferred to successor issue
`#735`: consumer-facing `python3 scripts/<name>.py` instructions, the three
unrooted exported shell gates, and exported validators that read unshipped
consumer data files. The remaining bare third-party imports stay an explicit
inventory/non-claim until their documented-entrypoint scope is independently
owned.

## Verification boundary

The exact export self-sufficiency target passed `45` tests, including the real
checked-in export and hand-built consumer fixtures. This proves the repaired
dependency arm and detector behavior only; it does not prove installed-host
adoption, remote CI, or the #735 successor residue.
