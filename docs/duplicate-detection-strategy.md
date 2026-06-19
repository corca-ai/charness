# Duplicate Detection Strategy

This note records the intended duplicate-detection posture for Charness and for
repos that consume the `quality` skill.

## Layers

### 1. `nose` Markdown engine: Document Near-Duplicate Review

Document near-duplicate review is owned by nose's Markdown duplication engine
(same-language char-n-gram MinHash + line-level witnesses, nose >= 0.13.0),
surfaced as the advisory
[`inventory_doc_duplicates.py`](../skills/public/quality/scripts/inventory_doc_duplicates.py)
quality phase (`doc-duplicates`). It replaced the bespoke difflib whole-file
guard, which only caught ~0.98 whole-file similarity and missed per-line drift
that nose's tiered families and span witnesses surface.

- Scope: checked-in Markdown, skill, reference, and README surfaces. It scans the
  repo root and excludes the `plugins/` export mirror (every source doc would
  otherwise pair 1:1 with its copy), `charness-artifacts/`, and `mutants/`; nose
  also honors `.gitignore`.
- Posture: advisory. Findings are review candidates — which families are
  intentional shared template versus single-sourceable duplication — not standing
  failures. The phase fails closed only when nose is missing or older than 0.13.0,
  so an absent or pre-Markdown scanner is never a silent all-clear.
- Drift baseline: nose's native `--baseline` filters only the code-clone view, not
  the top-level `markdown` array, so the advisory keeps its own signature baseline
  ([`charness-artifacts/quality/doc-nose-baseline.json`](../charness-artifacts/quality/doc-nose-baseline.json),
  sorted member `path#heading` tuples — line-number stable) and reports only
  new/changed families. Re-baseline with `--write-baseline`; never treat the
  accepted count as a reduction target without a reviewed-candidate classification.

nose is a REQUIRED install (see
[`integrations/tools/nose.json`](../integrations/tools/nose.json)): there is no
difflib fallback, so a healthy nose >= 0.13.0 must be present for doc
near-duplicate review to run, in Charness and in consumer repos alike.

### 2. `jscpd`: Syntax Copy-Paste Candidate (deferred)

`jscpd` is the right candidate for a broader literal/token copy-paste detector.
It can scan Python and Markdown, so it is not limited to JavaScript-only use.

Adoption is deferred. `jscpd` found real block-level code clones, but the current
tree contains enough bootstrap and adapter-shape debt that a hard raw `jscpd`
gate would be noisy before those families are refactored or explicitly baselined.
Revisit `jscpd` only after the `nose`-driven refactoring pass reduces the existing
code-clone backlog.

If adopted, `jscpd` should start as a separate validation support binary, not as
a replacement for either nose surface:

- add a `jscpd` manifest under [`integrations/tools/`](../integrations/tools/)
  with `quality` as the supported public skill and `validation` as the
  recommendation role
- expose install, update, doctor, and degradation through `charness tool`
- run an advisory or separately labelled quality phase first, because the current
  Charness tree already has many block-level clones that the document
  near-duplicate review intentionally ignores
- promote to a hard gate only after choosing a reviewed threshold/budget, an
  ignore-pattern policy for intentional bootstrap/export duplication, or a
  baseline-like adoption contract

Post-cleanup reassessment on 2026-06-04 used maintainer-local `npx --yes jscpd`
4.2.4 after the bootstrap, adapter, and document near-copy cleanup slices:

- Source-only Python scan (`scripts skills/public skills/support`,
  `--min-lines 18 --min-tokens 50`) still found 87 exact clones / 2110 duplicated
  lines (3.05%). Most of that is portable skill-runtime bootstrap and remaining
  adapter/import skeletons, with a few real refactoring candidates mixed in, so a
  raw hard gate would still be noisy.
- A higher-floor source scan (`--min-lines 40 --min-tokens 80`) found 3 exact
  clones / 188 duplicated lines: `check_init_repo_rename.py` vs
  `check_premortem_rename.py`, and `report_usage_episodes.py` vs
  `validate_usage_episodes.py`. These are meaningful refactoring candidates, but
  not enough to justify an unbaselined hard gate.

Recommendation: keep `jscpd` out of the standing gate for now. If adopted, wire it
through the external-tool/support-binary path first and start with a labelled
code-only advisory or baseline/no-increase wrapper.

### 3. `nose`: Advisory Code Clone Inventory

The same required `nose` binary that backs document near-duplicate review in
layer 1 also ranks semantic and near-structural code clone families as
refactoring proposals, surfaced as the advisory
[`inventory_nose_clones.py`](../skills/public/quality/scripts/inventory_nose_clones.py)
quality phase (`inventory-nose-clones`).

- Code clones (`nose scan`, advisory `inventory-nose-clones`) rank refactoring
  candidates with their own
  [`charness-artifacts/quality/nose-baseline.json`](../charness-artifacts/quality/nose-baseline.json)
  drift baseline.
- Document near-duplicates (`nose query` Markdown families, advisory
  `doc-duplicates`) own layer 1 above.
- `jscpd` (layer 2) remains a deferred syntax/token copy-paste candidate.

For Charness, the initial maintainer-local 2026-06-04 observation surfaced
meaningful refactoring candidates, especially repeated skill-runtime bootstrap
blocks and adapter resolver shapes. The standing code-clone scan:

```sh
nose scan scripts skills/public skills/support \
  --mode syntax,semantic,near --min-size 24 \
  --sort extractability --top 20
```

Use repeatable `--exclude <glob>` (for example, `--exclude '**/resolve_adapter.py'`)
or a structured `--ignore-file <file>` for focused follow-up scans after
classifying intentional boilerplate; do not treat filters as proof that the
excluded duplication was resolved.

## Test DSL And Testability Policy

Duplicate findings in tests must follow the existing testability policy:

- extract mechanical scaffolding, fixture builders, lifecycle wrappers, command
  runners, and shared assertion helpers when doing so keeps behavior intent
  visible at the test site
- do not hide behavioral assertions in helpers just to lower a duplicate score
- when a duplicated test pattern depends on subprocess-heavy setup, first ask
  whether the target behavior should be reachable through an in-process module,
  package, function, service, or adapter seam

The boundary-bypass ratchet is already a separate structural guard. A passing
ratchet proves no new boundary-bypass candidates beyond the baseline; it does not
prove the existing backlog or test duplication posture is healthy.
