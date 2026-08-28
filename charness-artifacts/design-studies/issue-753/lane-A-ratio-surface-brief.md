# Lane brief: 753-ratio-surface (fix the ratio gate's denominator)

Governing context:
`charness-artifacts/design-studies/issue-753/2026-08-28-jtbd-audit-quality-gates.md`
section "Why the ratio reads 1.18" (normative motivation): the gate's
`**/*.py`-only denominator omits the extensionless root `charness` CLI
(6,081 lines of Python), canonical shell, and the Rust core — measured
against the full executable surface the ratio is ~1.01-1.04. The JTBD
audit found the test corpus 96.5% legitimate, so the honest move is to
fix the metric, not prune healthy tests. Do not spawn descendant
agents.

## Outcome

1. `scripts/check_test_production_ratio.py` counts the full EXECUTABLE
   production surface in the denominator (splitlines engine):
   - canonical Python as today (`**/*.py` outside the ignored dirs);
   - tracked extension-less files whose first line is a Python shebang,
     outside ignored dirs (this captures the root `charness` CLI
     without hardcoding one filename);
   - tracked `*.sh` and `.githooks/*` outside ignored dirs;
   - Rust production sources `native/*/src/**/*.rs` (and build.rs if
     present);
   - EXCLUDED from the denominator: `native/*/fixtures/**` entirely
     (test fixtures are not production — this also removes the
     currently miscounted `native/repograph/fixtures/*.py`), and
     declarative YAML/JSON/TOML config (documented decision: policy
     data, not executed code).
2. The NUMERATOR gains Rust crate tests `native/*/tests/**/*.rs`
   alongside today's `tests/` corpus (a test line is a test line
   regardless of language).
3. Payload stays schema-compatible: keep every existing key
   (`engine`, `source_lines`, `test_lines`, `ratio`, `max_ratio`,
   `status`/advisory) and ADD an additive `surface_breakdown` object
   with per-bucket line counts (python, python-shebang, shell, rust,
   rust-tests, tests-python) so the definition is auditable from the
   output. Threshold stays `1.0` and the gate stays ADVISORY — do not
   change enforcement posture (that is a later #753 decision).
4. The `tokei` engine either gains the same surface (tokei supports
   Sh/Rust types) or, if fidelity is not achievable cheaply, is updated
   to report a typed
   `engine_note: "tokei engine measures Python only"` so the two
   engines cannot silently disagree about what they measure — pick one,
   document it in the module docstring.
5. `tests/quality_gates/test_test_production_ratio.py` updated:
   behavioral fixtures for the new buckets (a fixture tree with a
   shebang script, a `.sh`, rust `src/` + `tests/` + `fixtures/`
   files proving each lands in the right bucket or is excluded), and
   the schema-additivity of `surface_breakdown` pinned
   additive-key-tolerantly (do not pin the exact whole payload — that
   is the change-detector-pin class #753 is retiring).
6. Run the gate on the real repo and report the new measured ratio and
   the full breakdown verbatim in your final message.

## Boundaries

Scope (must match the task-run `--scope` list exactly):
`scripts/check_test_production_ratio.py`,
`tests/quality_gates/test_test_production_ratio.py`.
Out of scope: `scripts/run-quality.sh` (label line unchanged),
`tests/quality_gates/support.py`, all other tests, `native/**`,
`plugins/**` (parent syncs), `.agents/**`. A concurrent lane is
refactoring other files under `tests/quality_gates/` — touch ONLY your
two scoped files.

## Verification

- `python3 -m pytest tests/quality_gates/test_test_production_ratio.py -q`;
- `python3 scripts/check_test_production_ratio.py --repo-root .
  --require-git-file-listing --advisory` (real run, report verbatim);
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`;
- `./scripts/check-python-lint.sh`.
The parent runs the FULL battery after integration.

## Stop condition and result shape

One coherent commit, prefix `quality(753):`. Final message: what
changed, the real-repo ratio + breakdown, commands run with observed
results, deviations with reasons.
