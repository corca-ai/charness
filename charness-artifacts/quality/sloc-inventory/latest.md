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
| splitlines | 32,459 | 224 | 20,484 | 116 | 0.631 |
| tokei (Python only) | 31,132 | 225 | 18,147 | 116 | 0.583 |

Both pass the current `DEFAULT_MAX_RATIO=1.0`.

## Why The Engines Now Agree
- `IGNORED_DIRS` in `scripts/check_test_production_ratio.py` now excludes
  `.artifacts`, so generated `cautilus-experiments` copies no longer count as
  source. File counts are within one of each other (224 vs 225); tokei's
  remaining ~1,300-line lead on source is consistent with `.gitignore`-honoring
  selection plus blank/comment trimming.
- The 0.05 ratio gap between engines reflects how tokei drops blank and comment
  lines from the test side too. Either engine answers the same first-order
  question now: charness is a roughly 0.6-ratio test-production codebase.

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
- Splitlines stays the default for `check_test_production_ratio.py`. With
  `.artifacts` excluded the zero-dep engine matches tokei within ~5 ratio
  points, so the Rust dependency is not required to keep the gate honest.
- Tokei stays available through `--engine tokei` for repos that want the
  multi-language SLOC view or stricter blank/comment exclusion.
- `DEFAULT_MAX_RATIO=1.0` continues to pass for both engines; no recalibration
  is needed.

## Follow-ups
- None outstanding. Tokei is wired into `run-quality.sh` as the
  `inventory-sloc` advisory phase and refreshes this artifact's
  `latest.json` every quality run; this `latest.md` is updated by hand
  when the framing changes.

## Refresh
Regenerate with:

```bash
python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --json \
  > charness-artifacts/quality/sloc-inventory/latest.json
python3 scripts/check_test_production_ratio.py --engine splitlines --json
python3 scripts/check_test_production_ratio.py --engine tokei --json
```
