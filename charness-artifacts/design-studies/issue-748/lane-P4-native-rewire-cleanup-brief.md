# Lane brief: 748-native-rewire-cleanup (lane P4)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-748-migration-plan.md`
(rev 2), decisions D5 (Python deletion side), D6 (rewire/deletion —
including the TWO NAMED doc references), D9 (fake-binary seam), D10
(catalog consequences), and the LANDED native commands: `repograph
plugin-refs` and `repograph what-reads` (read their `ABI.md` sections;
plugin-refs SCANS inline code — the parent corrected an earlier
masking defect; verdicts on this repo: plugin-refs exit 0, 65
references, 0 findings). The shim is `scripts/native_gate_lib.py`
(landed; consume, don't modify). Sibling lanes run concurrently
touching ONLY `scripts/check_standalone_imports.py`,
`tests/quality_gates/test_standalone_imports.py`,
`skills/public/release/**`, and
`tests/quality_gates/test_release_real_host.py` — stay off those
files. Do not spawn descendant agents.

## Outcome

1. Delete `scripts/check_plugin_dir_references.py`. Rewire:
   - `scripts/run-quality.sh` label `check-plugin-dir-references`
     (currently `queue_selected "check-plugin-dir-references" python3
     scripts/check_plugin_dir_references.py --repo-root "$REPO_ROOT"`)
     → `python3 scripts/native_gate_lib.py --repo-root "$REPO_ROOT"
     plugin-refs --repo-root "$REPO_ROOT"`; add the label to
     `NATIVE_GATE_LABELS` so the existing preflight covers it. Label
     name unchanged; stays OFF `UNESTABLISHED_CAPABLE_LABELS` (native
     exit 3 blocks; exit 1 findings block).
   - `.github/workflows/quality-core.yml` step "Validate plugin-dir
     references" (direct `python3 scripts/check_plugin_dir_references.py`)
     → the same shim invocation (the provisioning build step already
     precedes it).
   - `tests/quality_gates/support.py` stub tuple
     `("check-plugin-dir-references", "check_plugin_dir_references.py")`
     → `("check-plugin-dir-references", "native_gate_lib.py")`.
2. Contract deltas to respect, not fight: native reports ALL findings
   (Python raised on first), exit 1 findings / 3 unestablished, and
   preserves `<plugin-dir>/...` ellipsis targets as `templated` where
   Python silently dropped them (recorded delta). The
   no-plugins-package exit-0 typed note is preserved by the native
   command.
3. Rewrite `tests/quality_gates/test_plugin_dir_references.py` as
   wrapper-level tests: fake binary via `CHARNESS_NATIVE_CORE` emitting
   canned `repograph.plugin_refs.v1` documents (findings → exit 1
   propagates; unestablished → 3; clean → 0), IN-PROCESS `main()`
   drives (the boundary-bypass ratchet counts new test→script
   subprocess boundaries — run
   `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`
   before finishing). Behavior/classification tests die with the
   algorithm (crate fixtures own them).
4. Delete `scripts/what_reads_this.py`,
   `scripts/what_reads_this_fallback.py`,
   `tests/test_what_reads_this.py`, and the what-reads portions of
   `tests/coverage_debt/test_batch1.py` (the file's other portions
   stay; if the remainder is trivially empty, delete the file and say
   so). No Python wrapper replaces them: the owner is
   `repograph what-reads --path` (path-target only; symbol/config-key
   retired by plan D5 — do NOT re-create them).
5. Reference sweep (the exact scope-omission class the retro paid
   for):
   - `skills/shared/references/bootstrap-resolution.md:133` — the
     `<plugin-dir>/scripts/check_plugin_dir_references.py` reference:
     update the sentence to name the native gate route (the exported
     tree no longer carries the deleted script; after export sync this
     reference would otherwise become a `missing` FINDING in the very
     gate this lane rewires).
   - `docs/deferred-decisions.md:704` — same treatment for its
     `<authoring-repo>/scripts/check_plugin_dir_references.py` text.
   - `skills/public/quality/references/consumer-validator-catalog.yaml`
     — remove the `scripts/check_plugin_dir_references.py` entry
     (decision: exclude; no consumer contract change).
   - `skills/public/quality/references/attention-state-visibility.json`
     — it keys `"scripts/check_plugin_dir_references.py"`; read that
     file's contract (and any validator over it) and update the entry
     to whatever the schema requires for a retired path — do not
     hand-wave; if the right disposition is unclear, report it as a
     deviation instead of guessing.
   - grep the canonical tree (`docs/`, `skills/`, `scripts/`,
     `.agents/`) for remaining `what_reads_this` /
     `check_plugin_dir_references` mentions and update or report each
     (docs/validator-timing-layers.md:110 describes the
     check-plugin-dir-references gate — update its command description
     to the native route, keep its policy prose).
6. Do NOT touch `plugins/**` (the parent runs the canonical export
   sync afterward — the exported run-quality.sh and mirror deletions
   flow from there).

## Boundaries

Scope (must match the task-run `--scope` list exactly):
`scripts/check_plugin_dir_references.py`, `scripts/what_reads_this.py`,
`scripts/what_reads_this_fallback.py`, `scripts/run-quality.sh`,
`.github/workflows/quality-core.yml`,
`tests/quality_gates/test_plugin_dir_references.py`,
`tests/quality_gates/support.py`, `tests/test_what_reads_this.py`,
`tests/coverage_debt/test_batch1.py`,
`skills/shared/references/bootstrap-resolution.md`,
`docs/deferred-decisions.md`, `docs/validator-timing-layers.md`,
`skills/public/quality/references/consumer-validator-catalog.yaml`,
`skills/public/quality/references/attention-state-visibility.json`.
Out of scope: `native/**` (build-only), `plugins/**`,
`scripts/native_gate_lib.py`, the sibling-lane files listed above,
`.agents/**`.

## Verification

- `cargo build --release` in `native/repograph` (read-only) so the
  real binary exists;
- `CHARNESS_QUALITY_LABELS=check-plugin-dir-references
  ./scripts/run-quality.sh` (real end-to-end label run);
- `python3 -m pytest tests/quality_gates/test_plugin_dir_references.py
  tests/coverage_debt -q`;
- `python3 scripts/check_github_actions.py --repo-root .`;
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`;
- `./scripts/check-python-lint.sh`; `./scripts/check-markdown.sh`;
- `python3 scripts/check_doc_links.py --repo-root .`.
The parent runs the FULL battery + export sync after integration.

## Stop condition and result shape

One coherent commit, prefix `migrate(748):`. Final message: what was
built/deleted, commands run with observed results, deviations with
reasons.
