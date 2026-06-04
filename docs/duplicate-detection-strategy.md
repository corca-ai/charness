# Duplicate Detection Strategy

This note records the intended three-layer duplicate-detection posture for
Charness and for repos that consume the `quality` skill.

## Layers

### 1. `check_duplicates.py`: Near-Copy Guard, Markdown Target

[`scripts/check_duplicates.py`](../scripts/check_duplicates.py) is the current
repo-local hard guard for whole-file near similarity. It currently still scans
the helper-script globs in its `DEFAULT_PATTERNS`; the intended long-term scope
is checked-in Markdown, skill, reference, and README surfaces. It filters out
files below 18 non-empty lines, respects the git file listing when
`--require-git-file-listing` is used, and fails on whole-file text similarity at
`0.98` or higher.

This guard is intentionally narrow:

- it catches nearly identical checked-in Markdown, `SKILL.md`, reference, and
  README files
- it currently also scans helper-script globs, which should be preserved or
  narrowed only after the `nose` cleanup makes the coverage tradeoff explicit
- it is wired into [`scripts/run-quality.sh`](../scripts/run-quality.sh) as
  `check-duplicates`
- it also runs in the docs-only pre-push subset, so doc-only pushes still get a
  cheap copy-paste guard; this does not mean `charness-artifacts/` are scanned
  by the duplicate checker

The guard is not a block-level clone detector and should not be treated as a
complete refactoring inventory. Python and other code duplicate cleanup should
move out of this guard instead of widening its role.

### 2. `jscpd`: Syntax Copy-Paste Candidate

`jscpd` is the right candidate for a broader literal/token copy-paste detector.
It can scan Python and Markdown, so it is not limited to JavaScript-only use.

Adoption is now deferred. `jscpd` found real block-level code clones, but the
current tree contains enough bootstrap and adapter-shape debt that a hard raw
`jscpd` gate would be noisy before those families are refactored or explicitly
baselined. Revisit `jscpd` only after the `nose`-driven refactoring pass reduces
the existing code-clone backlog.

Adoption should start as a separate validation support binary, not as an
immediate replacement for [`scripts/check_duplicates.py`](../scripts/check_duplicates.py):

- add a `jscpd` manifest under
  [`integrations/tools/`](../integrations/tools/) with `quality` as the
  supported public skill and `validation` as the recommendation role
- expose install, update, doctor, and degradation through `charness tool`
- run an advisory or separately labelled quality phase first, because the
  current Charness tree already has many block-level clones that the existing
  whole-file guard intentionally ignores
- promote to a hard gate only after choosing one of:
  - a reviewed threshold/budget
  - an ignore-pattern policy for intentional bootstrap/export duplication
  - a baseline-like adoption contract if upstream support is sufficient

Parity status as of 2026-06-04:

- `jscpd` catches the existing
  [`check_duplicates.py`](../scripts/check_duplicates.py) fixture shape with
  repeated exact Markdown lines and respects `.gitignore` in that fixture.
- `jscpd` does not exactly replace the whole-file near-similarity behavior:
  highly similar Markdown files with per-line token differences can trip
  [`check_duplicates.py`](../scripts/check_duplicates.py) while producing no
  exact `jscpd` clone.
- With the current [`check_duplicates.py`](../scripts/check_duplicates.py) file
  list and a large token floor, `jscpd` reports existing Charness
  bootstrap/script clones instead of passing cleanly. That is useful signal, but
  not drop-in parity.

Conclusion: do not introduce `jscpd` yet. After the `nose` refactoring pass,
rerun the comparison and decide whether a code-only `jscpd` wrapper still adds
useful hard-gate signal. Whole-file Markdown near-similarity remains owned by
[`check_duplicates.py`](../scripts/check_duplicates.py) either way.

### 3. `nose`: Advisory Refactoring Inventory

`nose` should be a validation support binary for `quality`, not a public skill
and not a sibling-checkout assumption. It should be installed, updated, and
doctored through the external-tool manifest path so `charness update all` and
consumer repos can use it on arbitrary machines.

Recommended integration shape:

- add a `nose` manifest under [`integrations/tools/`](../integrations/tools/)
- stage `nose` in
  [`integrations/tools/dependencies.json`](../integrations/tools/dependencies.json)
  when Charness itself depends on it
- detect with `nose --version`
- health-check with a stable help or scan surface such as `nose scan --help`
- allow `NOSE_BIN` only as a maintainer-local override for development
- consume it from `quality` as an advisory inventory phase, for example
  `inventory-nose-clones`

`nose` should not replace [`check_duplicates.py`](../scripts/check_duplicates.py)
or `jscpd`:

- [`check_duplicates.py`](../scripts/check_duplicates.py) protects
  near-identical whole documents and skill files
- `jscpd` is the syntax/token copy-paste gate candidate
- `nose` ranks semantic and near-structural clone families as refactoring
  proposals

For Charness, the initial maintainer-local 2026-06-04 `nose 0.4.0` observation
surfaced meaningful refactoring candidates, especially repeated skill-runtime
bootstrap blocks and adapter resolver shapes. A durable baseline report belongs
to the first activated refactoring slice:

```sh
nose scan scripts skills/public skills/support \
  --mode syntax,semantic,near --threshold 0.70 \
  --min-lines 18 --min-tokens 24 --sort extractability --top 20
```

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
ratchet proves no new boundary-bypass candidates beyond the baseline; it does
not prove the existing backlog or test duplication posture is healthy.

## Dogfood Note

During this review, `impl` bootstrap created
[`.agents/impl-adapter.yaml`](../.agents/impl-adapter.yaml) because the Charness
checkout did not track one. Existing repo records mention the
`impl-adapter-bootstrap` eval and default fields, but the adapter file itself was
absent. Treat this as a first-use dogfood signal for the recent adapter
normalization effort, not as part of duplicate detection.
