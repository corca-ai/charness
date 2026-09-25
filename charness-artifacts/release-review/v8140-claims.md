# Claims Review: charness 8.14.0 (prepared commit 1c5e38d)

Scope: record fidelity only, not code correctness. Record under review is
`charness-artifacts/release/latest.md` as committed in
`1c5e38dd8e2cdec8da572eae935d0873d7178385` ("Release charness 8.14.0").
Shipped delta: `8885601c3..5c1a1b06e` (issues 870-874, umbrellas 843/859).
Line cites below (`rec:<n>`) refer to that committed record.

## Verdict: PASS (with 3 non-blocking advisories)

No false version, quantitative, or verification claim was found. The record's
notable honesty points — it disclaims a durable quality receipt, disclaims
publication, and labels the adapter preflight a recorded absence — check out
against the evidence. Publication must still wait for the record's own stated
gates (pre-push receipt, branch/tag push); this PASS does not clear those.

## 1. Version claimed vs version bumped — PASS

- Record claims previous `8.12.0`, target `8.14.0` (rec:11-12), bump
  `8.12.0 -> 8.14.0` via `set-version` (rec:89).
- `packaging/charness.json` at `1c5e38d`: top-level `version` = `8.14.0`,
  `codex.manifest.version` = `8.14.0`, `claude.manifest.version` = `8.14.0`;
  the `1c5e38d` diff shows each changed `8.12.0` -> `8.14.0`. No drift.
- `.claude-plugin/marketplace.json` at `1c5e38d`: `metadata.version` =
  `8.14.0`, `plugins[0].version` = `8.14.0`; diff shows `8.12.0` -> `8.14.0`.
- No `.codex-plugin/plugin.json` / `.claude-plugin/plugin.json` paths exist in
  the `1c5e38d` tree; the record's "4 versioned surface(s), with 1
  presence-only surface(s) not version-checked" (rec:20) is consistent with
  this layout (embedded manifests version-checked, on-disk plugin paths
  presence-only). Every versioned surface observed reads `8.14.0`.

## 2. Quantitative figures vs sources — PASS (no overclaim)

- The record makes NO "89 passed / 0 failed" claim. It states the helper's
  `./scripts/run-quality.sh --release --read-only` exited 0 in 155.8s and in
  the same sentence flags "quality unestablished: pytest-release pending final
  resume" (rec:18), then explicitly records "pre-push quality receipt: NOT
  recorded ... cites no durable receipt" (rec:19).
- External battery evidence is self-consistent and UNCITED by the record (good):
  `/tmp/quality-run13.log` tail summary reads "89 passed, 0 failed, 4 not run
  (... opt-in unmet), total 850.6s"; `/tmp/quality-receipt13.json` has
  `status: pass`, `effective_exit_code: 0`,
  `details: {passed: 89, failed: 0, elapsed: 850.6s, execution_mode: read-only,
  release: true}`, with matching 4-entry `not_run` opt-in list. Log and
  receipt agree with each other; neither is falsely bound to the record.
- Advisory A1 (non-blocking): rec:18 holds "exited 0" and "quality
  unestablished" in one sentence without saying what scope exited 0. A reader
  could mistake exit 0 for a full gate pass. The disclaimers present ("pending
  final resume", rec:19) contain the damage, but a scope label for the 155.8s
  run would remove the ambiguity. Note the 155.8s helper measurement (rec:18,
  rec:67 `quality_command: 155.756s`) is a different run/scope from the 850.6s
  battery in `/tmp/quality-run13.log`; the record does not conflate them.

## 3. "Verified" sentences vs evidence — PASS with one advisory

- `current_release.py` no-drift (rec:20): corroborated — all versioned
  surfaces observed at `1c5e38d` read `8.14.0` (see section 1).
- Validated tree (rec:21): commit `c42aa39...` is the parent of `1c5e38d`
  (`git rev-parse 1c5e38d^` = `c42aa39...`), and the cited tree
  `6c2a5685...` equals `git rev-parse c42aa39^{tree}`. Binding is accurate.
  Advisory A2 (non-blocking): the cited tree is the pre-bump committed tree;
  the version bumps themselves landed in `1c5e38d`. The record discloses timing
  ("post-bump, pre-commit", rec:18/rec:20), so the working-tree drift check is
  the actual bump coverage — but a strict tree-pinner should note the cited
  hash does not itself contain the `8.14.0` bytes.
- Fresh-checkout probes "passed" (rec:72-75) with runtime 8.088s (rec:68):
  helper-measured, low-risk; no durable log cited, none claimed.
- Requested-review gate `ok` / `advisory_only` / 0 commands (rec:54-57):
  vacuous pass, honestly labeled. No inflation.
- Review proof (rec:46): `charness-artifacts/critique/v8140-critique.md`
  exists as a blob in `1c5e38d`. Referent resolves.
- Adapter preflight `not_required`, execution `not_run`, "recorded absence,
  not a passing preflight" (rec:37-42): exemplary non-claim. Delta stat shows
  no release-adapter file among the 92 changed files, consistent with the
  stated reason (rec:38).
- Publication/install-refresh (rec:27-28, rec:33, rec:61): all "pending", "not
  verified yet". No premature verification claimed.

## 4. Bump rationale — PASS (present and sourced)

- Present at rec:89-90: minor (not patch) via 870/871/872 capabilities; not
  major (no invocation breaks or renames); `8.14.0` (not `8.13.0`) because
  that tag already exists on origin for the #866-869 batch.
- Issue-to-diff mapping checks out against `8885601c3..5c1a1b06e` (92 files):
  870 train metrics (`scripts/task_run/task_run_train_stats.py`,
  `tests/.../test_train_stats_870.py`), 871 goal re-inject hook
  (`scripts/host_goal_reinject_hook.py`,
  `scripts/hooks/host_hook_goal_reinject_install.py`,
  `tests/test_goal_reinject_hook_871.py`), 872 status report
  (`scripts/task_run/task_run_status_report.py`,
  `tests/.../test_task_status_report_872.py`).
- `v8.13.0` exists on origin (`8cd3cbd5`, peeled `8885601c3` — i.e. the
  #866-869 batch tip), so skipping to `8.14.0` is correctly justified.
  Advisory A3 (non-blocking): the record does not enumerate the full shipped
  delta (873/874, umbrellas 843/859, 825 staying open) anywhere except via the
  rationale's 870/871/872; that is acceptable for a surface-check record but a
  one-line delta pointer would aid the publisher.

## Gates restated (not findings — the record already gates on these)

1. Pre-push quality receipt absent by the record's own statement (rec:19).
2. Branch/tag push, GitHub release creation, and public surface verification
   all recorded pending (rec:26-28, rec:33, rec:61).
3. Claims review was the pending item (rec:50); this file is that review.
