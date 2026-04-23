# Session Retro: Bootstrap Runtime Repair
Date: 2026-04-23

## Mode

session

## Context

This session repaired an install bootstrap failure where another machine reported that the managed checkout bootstrap runtime was still missing `jsonschema` and `packaging`.

## Evidence Summary

Evidence came from the reported error text, `scripts/bootstrap_runtime.py`, `tests/charness_cli/test_bootstrap_runtime.py`, the new debug artifact, and `run_slice_closeout.py` output.

## Waste

The first hypothesis over-focused on dependency installation and launcher shell syntax. The sharper failure branch was stale machine-local launcher state combined with a current base Python that already satisfied the module contract.

## Critical Decisions

The fix repairs an existing failing runtime launcher before deciding whether `pip --target` is needed. That keeps fresh install, valid reuse, and stale managed-checkout recovery on the same bootstrap path.

## Expert Counterfactuals

- Gary Klein: replay the failure as a recognition-primed incident first; stale partially initialized state should have been an explicit candidate before shell syntax details.
- Daniel Kahneman: slow down at the first plausible cause and require a test double for the exact branch where base Python and runtime launcher disagree.

## Next Improvements

- workflow: for install/update symptoms, enumerate fresh, valid-reuse, and stale-partial-state branches before patching.
- capability: keep stale launcher repair covered in `test_bootstrap_runtime.py` so future install refactors preserve this recovery path.
- memory: the durable debug artifact now records this as an operator-visible recovery seam.

## Persisted

yes: `charness-artifacts/retro/2026-04-23-bootstrap-runtime-repair.md`
