# nose v0.13.0 markdown duplication — gather asset (2026-06-19)

## Source

- Canonical URL: https://github.com/corca-ai/nose/releases/tag/v0.13.0
- Primary source used: **local checkout** `/home/hwidong/codes/nose` @ `v0.13.0-4-g1732f08`
  (source-priority: local before external). Access mode: `direct-cli` /
  local-repo read.
- Freshness: local repo is at/just past the v0.13.0 tag (2026-06).

## Requested facts — markdown/prose duplication in nose

- **It exists and is first-class.** `nose query <path>` now reports
  **same-language near-duplicate prose** across Markdown as one of its domains,
  surfaced in the same dashboard/JSON as code clones (capabilities-over-features:
  one entry point `nose query`, not a separate command).
  (`nose/docs/markdown-duplication.md:1-30`, `nose/docs/usage.md:41`)
- **Separate engine from code clones**: character-n-gram (Latin q5 / CJK q3)
  MinHash-LSH + winnowing + containment → IDF-weighted cosine rank →
  Smith-Waterman line-level witness. Order-invariant, sub-quadratic, deterministic
  (byte-identical across runs). **Same-language only** (no cross-lingual /
  paraphrase — that needs an LLM). (`markdown-duplication.md:9-14,46-54`)
- **Output per family**: relation tier (`exact`/`near-high`/`near-med`/`near-low`/
  `partial`) + score, a **span witness** (exact duplicated line range per file),
  and orthogonal evidence fields you filter on: `commonness` (boilerplate signal),
  `removable` (lines saved if single-sourced), `files`, `members`.
  (`markdown-duplication.md:27-30`)
- **Honesty contract** (matches charness's advisory-interpretation discipline):
  nose detects + witnesses, never judges intentional/acceptable/"remove this" —
  that stays the maintainer's call. Quality: PR-AUC 0.995 single-genre / 0.944
  multi-domain, candidate-recall 1.0. (`markdown-duplication.md:32-63`)

## CLI invocation + baseline mechanism

```
nose query <path>                 # human dashboard incl. "markdown near-duplicates"
nose query <path> --format json   # versioned JSON; top-level "markdown" array of families
```

- Discovers `.md`/`.markdown` under `<path>`, respects `.gitignore` + `--exclude`
  gitignore-style globs (`markdown-duplication.md:23`, `usage.md:99`).
- **CI gate**: `--fail-on any` / `--fail-on new` (`usage.md:102`).
- **Baseline** (same model charness already uses for code clones): `--baseline FILE
  --write-baseline` to accept a drift floor; `since=FILE status=new --fail-on new`
  is the composable "only new/changed" gate (temporal lens, hides nothing unlike
  `--baseline`). (`usage.md:73,102`)
- Filter to prose families with `--format json` and read the `markdown` array
  (vs code-clone families).

## Use for charness — replace check_doc_near_duplicates.py

`scripts/check_doc_near_duplicates.py` (123 lines, difflib whole-file prose at
0.98 ratio, blocking `run-quality.sh:481 --fail-on-match`) → replace with
`nose query <doc-scope> --format json` filtered to the markdown array, mirroring
the existing `inventory_nose_clones` / `nose-baseline.json` integration so doc-dup
uses one consistent clone tool + baseline mechanism. nose is strictly richer
(tiered families + span witnesses + commonness/removable evidence vs a binary
0.98 whole-file match). Steelman/critique of the bespoke gate tracked alongside
the buy-vs-build triage.

## Captured vs human confirmation

- Captured from local repo docs + `nose query --help`. NOT yet run against
  charness's doc surface (no families inventoried here); the replacement slice
  will produce the first real doc-dup family report + baseline.

## Open gaps

- Exact doc scope to scan (docs/ only? + SKILL.md? + charness-artifacts/?) and the
  initial baseline content are decided when the replacement lands.
- Whether to gate `--fail-on new` (drift-only, matches the code-clone baseline
  posture) vs `--fail-on any`.
