# SLOC Inventory
Date: 2026-05-04

## Scope
Repo-wide SLOC inventory plus dual-engine measurement for the
test-production ratio gate. Output of:

- `python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --json`
- `python3 scripts/check_test_production_ratio.py --engine={splitlines,tokei} --json`

Tool: tokei 14.0.0 (linuxbrew, arm64).

## Test-Production Ratio: splitlines vs tokei

| engine | source_lines | source_files | test_lines | test_files | ratio |
|---|---:|---:|---:|---:|---:|
| splitlines | 83,632 | 606 | 20,378 | 117 | 0.244 |
| tokei (Python only) | 31,017 | 225 | 18,058 | 117 | 0.582 |

Both pass the current `DEFAULT_MAX_RATIO=1.0`.

## Why The Engines Disagree
- `splitlines` walks `Path.rglob('*.py')` and only filters by `IGNORED_DIRS`
  membership. Generated trees that are git-ignored — most notably
  `.artifacts/cautilus-experiments/premortem-ab-compare/{baseline,candidate}/`
  — still get counted, inflating the source denominator by ~380 files and
  ~52,000 lines.
- `tokei` honors `.gitignore` automatically, so it sees only the source we
  actually maintain. It also separates code from blank and comment lines, which
  trims another ~10–15% per file.
- The denominator gap drives most of the ratio shift: tokei's 0.582 is the
  honest test-production proportion for `charness`-owned Python.

## Repo-Wide SLOC (tokei, .gitignore honored)

| language | code | comments | blanks | files |
|---|---:|---:|---:|---:|
| Python | 75,492 | 8,604 | 11,876 | 564 |
| JSON | 17,504 | 0 | 0 | 65 |
| JavaScript | 2,264 | 84 | 286 | 10 |
| Shell | 1,058 | 196 | 153 | 19 |
| YAML | 430 | 27 | 12 | 24 |
| TOML | 18 | 1 | 4 | 1 |
| Markdown | 0 | 24,307 | 10,261 | 520 |
| Plain Text | 0 | 0 | 0 | 7 |

Totals: 96,766 code / 33,219 comments / 22,592 blanks across 1,210 files.

Raw payload: [latest.json](./latest.json).

## Decision Surface
- Splitlines stays the default for `check_test_production_ratio.py` because it
  has zero external dependencies and the gate already passes.
- Tokei is the honest measurement when the question is "what is our real
  source-vs-test mix"; promote it to default only after the repo accepts a
  Rust binary as a hard prerequisite for the gate.
- Either way, the splitlines `IGNORED_DIRS` set should grow to include
  `.artifacts` so the zero-dep engine stops crediting `cautilus-experiments`
  to source. Filed as a follow-up below.

## Follow-ups
- Add `.artifacts` to `IGNORED_DIRS` in `scripts/check_test_production_ratio.py`
  and update `tests/quality_gates/test_test_production_ratio.py` expectations.
- Re-run this inventory after the IGNORED_DIRS fix to confirm splitlines
  ratio rises from 0.244 toward the tokei value of 0.582.
- Decide whether to promote `inventory_sloc.py` from helper to a standing
  advisory step in `quality` Bootstrap or `scripts/run-quality.sh`.

## Refresh
Regenerate with:

```bash
python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --json \
  > charness-artifacts/quality/sloc-inventory/latest.json
python3 scripts/check_test_production_ratio.py --engine splitlines --json
python3 scripts/check_test_production_ratio.py --engine tokei --json
```
