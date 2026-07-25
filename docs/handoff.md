# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Continuation Capability

The only open issue is #453; every residual below names an owning artifact that
already holds its evidence.

## Current State

- **Released through v2.7.0** (#454, #455, #456 all resolved and shipped). The
  standing operator direction is bug fixes, friction/rework reduction, and
  test/code speed.
- **Documented commands now resolve.** `check_doc_links` was one syntax short, so
  a `python3 scripts/<name>.py` example outlived the script it named — measured,
  not assumed: all six tests in
  [test_authoring_preflight_reference.py](../tests/test_authoring_preflight_reference.py)
  passed with `check_prose_pin.py` deleted. The shared fence/HTML-comment walk now
  has one home, [markdown_doc_scan.py](../scripts/markdown_doc_scan.py), which
  fixed two bugs the three drifted copies hid (see the
  [critique](../charness-artifacts/critique/2026-07-25-documented-command-resolution-gate.md)).
- **#453 stays deliberately OPEN** for a human close; its fixes are pushed.

## Next Session

1. **Close #453** once the next **scheduled** mutation run is verified with
   `check_mutation_run_proof.py --claim changed-line --run-id <id>`. A dispatch
   re-run cannot prove it (no `base_sha`).
2. **Documented flags are still a proxy** (F8 in the critique above). Dropping
   `--run-checks` from its owning script leaves the drift guards green while the
   documented command exits 2. Needs argparse introspection, not another literal.
3. **D38** (retro lessons that never reach a durable contract) is a deliberate
   defer in [deferred-decisions.md](./deferred-decisions.md); trigger has not fired.
4. **Pinned, not fixed:** `REPO_ROOT.resolve() / "skills" / "public"` escapes the
   export-safety predicate ([decision point](../tests/quality_gates/test_export_safe_asset_paths.py)).
5. Unowned follow-ups with evidence in the artifacts below: critique packet tier
   mismatch, specdown preset duplication, and `recommended_commands` in
   `plan_cautilus_proof.py` (the sweep's one surfaced twin — the sweep itself is
   signed off, do not re-run it).
6. Budgets retuned for `local-linux-x86_64-36cpu` only; run the budget check on
   aarch64/unprofiled hardware.
7. Still deferred: inline `.rglob`/`ls-files` pathspec discovery,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory, D18,
   stale `charness-run-*` basetemp reaping, #451's two unacted siblings. #449 declined.

## Discuss

- Write the violation before writing the guard. This slice did it twice and both
  times the demonstration changed the design; hazards in
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- The dup ratchet's hard arm fired mid-slice and was right: the fix was extracting
  the shared walk, not baselining the family. Treat a block as a design signal
  before reaching for `--write-baseline`.
- Do not re-litigate the two refuted audit findings (removing the dup-ratchet hard
  arm or the boundary-bypass ratchet). #448 scoped-accept items wait for the next
  dup-ratchet slice.

## References

- [documented-command critique](../charness-artifacts/critique/2026-07-25-documented-command-resolution-gate.md) · [#454 debug artifact](../charness-artifacts/debug/2026-07-25-bounded-reviewer-result-delivery.md)
- [455/456 resolution critique](../charness-artifacts/critique/2026-07-25-issues-455-456-resolution-critique.md) · [session retro](../charness-artifacts/retro/2026-07-25-session-retro.md) · [unused-option sweep](../charness-artifacts/audit/2026-07-25-unused-mode-option-sweep.md)
- [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [release state](../charness-artifacts/release/latest.md) · [quality review](../charness-artifacts/quality/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
