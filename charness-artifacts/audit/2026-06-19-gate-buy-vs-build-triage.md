# Gate buy-vs-build triage (handoff item B, 2026-06-19)

Operator-requested ("buy-vs-build 전수 triage 먼저"). Lens: north-star P1 (gates on
**reversible** in-session work bear the burden → DROP/advisory candidates) + P5
(teeth legitimate only at **irreversible** boundaries → KEEP) + craken-agents'
"buy the gate, write thin config; build only the irreducibly repo-unique"
(`gather/2026-06-19-craken-agents-gate-bootstrap-study.md`). **Count is not a
metric** — the goal is removing *judgment-displacing bespoke teeth on reversible
work*, not minimizing lines.

Named-gate surface measured: **18,261 lines** (`scripts/check_*|validate_*` +
skills-nested); ~70 blocking phases in `run-quality.sh`. Two read-only triage
subagents classified each gate; findings vetted against the north-star traps.

## Already "bought" (off-the-shelf, in use)

ruff (E/F/I/C90 + mccabe complexity 15), vulture (dead code), markdownlint-cli2,
tokei, jsonschema (in validate_packaging/profiles), the sibling `nose` clone
tool, cosmic-ray (mutation), coverage.py. So charness already buys the
lint/format/dead-code/clone/mutation/coverage layers — the bespoke surface is
mostly *repo-unique contracts*, which is the correct place to build.

## BUY candidates (bespoke re-implements an available tool)

| gate | lines | tool | note |
|---|---|---|---|
| `check_doc_near_duplicates.py` | 123 | **nose** (in-repo) or jscpd | difflib near-dup re-implements clone detection; nose is the in-repo precedent |
| `check_doc_links.py` (link core only) | 396 | markdownlint-cli2 / lychee | only the broken-relative-link core is buyable; adapter-canonical-surface + placeholder logic stays bespoke (partial BUY) |
| `check_python_lengths.py` **function** cap | (of 423) | ruff **PLR0915** | statements-per-function ≈ the intent; tolerance shifts (statements≠lines). **File-line cap is NOT buyable** (no ruff rule) and stays the KEEP core |
| `validate_critique_packet.py` | 179 | **jsonschema** (already a dep) | hand-rolled key/enum validator for a versioned JSON envelope; not wired into any hook → free to convert/drop from standing |

## DROP / demote-to-advisory candidates (P1 reversible, blocking today)

Ranked by judgment-displacement (strongest first):

1. **`check_test_production_ratio.py`** (175, BLOCKING `run-quality.sh:477`) — a hard
   test/prod **LOC-ratio ≤ 1.0** cap is the clearest "count is a metric"
   violation on reversible test growth; forces awkward splits. **Strongest DROP.**
2. **`check_title_slug_drift.py`** (137, BLOCKING `--strict` `:430`) — heuristic
   word-overlap of H1 vs filename on editable docs; false-positive-prone → drop
   `--strict` to advisory.
3. **`check_skill_contracts.py`** (289, BLOCKING `:418`) — exact `\n`-anchored prose
   snapshots pinned in named SKILL.md cores; brittle, reversible doc content →
   advisory (this is review/test territory, and it bit us in the S5/S6 retro).
4. **`validate_skill_ergonomics.py`** (324, BLOCKING `:382`) — mostly opt-in
   heuristic prose rules; **keep only the `portable_package_*` arm** (issue-anchor
   / host-surface leak into *exported* packages = a real export boundary), demote
   the rest.
5. **`validate_critique_artifacts.py`** (375, BLOCKING `:409`) — **keep the
   reviewer-tier honesty field-presence check** (don't claim a tier you didn't
   request), demote the structured-bin / forbidden-phrase matching.

Already non-blocking (confirm they stay advisory; no action): `check_doc_authoring_preflight`,
`check_symbol_residue`, `check_prose_pin`, `check_seed_fixture_budget`.

## KEEP / traps (P5 irreversible — do NOT drop)

- **`check_issue_closeout_commit_msg.py`** — GitHub issue close (canonical P5).
- **`check_staged_reversion.py`** — silent base-reversion re-commit with green gates.
- **`check_staged_mirror_drift.py` + `validate_packaging[_install_surface].py`** —
  plugin export / install manifest ships to operators.
- **`validate_current_pointer_freshness.py` + `check_current_pointer_writes.py`** —
  operator-facing rolling pointers / single-writer invariant.
- **`check_mutation_run_proof.py` + `check_changed_line_mutation_coverage.py`** —
  false-proof citation into closeout/issue/release; pre-merge teeth.
- **`validate_adapters / integrations / profiles / presets`**,
  **`validate_inference_interpretation` + `validate_attention_state_visibility`**
  (silent-green prevention), **supply-chain**, **`check_bootstrap_shim_consistency`**.

## The length floor (operator decision: "keep hard floor, move cap to tool rule")

Honest feasibility — the move is clean for one cap, partial for one, impossible
for one:

- **Complexity cap** → already a ruff rule (`C90`/mccabe), already bought.
- **Python file-line cap** (`check_python_lengths.py`, 480/360/800 via tokei) →
  **no ruff/markdownlint rule exists** (PLC0302 unimplemented; biome's
  `noExcessiveLinesPerFile` is JS-only). Options: add pylint `C0302`, a tiny
  generic `max-file-lines` hook, or keep bespoke.
- **SKILL.md cap** (200 total `validate_skills.py:351`; core-headroom ratchet
  160/buffer-4 `check_skill_surface_preflight.py`) → **no off-the-shelf rule
  anywhere** (markdownlint MD013 is per-line only). The 200 total-line check is
  ~3 lines; the core-headroom ratchet (strip frontmatter + pressure-exempt
  sections, regression-grandfathered) is **irreducibly bespoke**.
- **Achievable "tool rule" = config-driven constants (Option 2):** lift the magic
  numbers (200/160/4 and 480/360/800) into the quality adapter
  (`.agents/quality-adapter.yaml`); `validate_skill_ergonomics` already reads its
  core budget from the adapter. Policy becomes configured/declarative even though
  the enforcement mechanism stays bespoke Python. This is the honest version of
  the operator's instruction — the cap **cannot** become a pure off-the-shelf
  tool rule like craken's biome line.

## Corrections / flags

- **`check_upstream_support_drift.py`** (200) — KEEP-class logic but **orphaned**:
  not referenced by `run-quality.sh`, `.githooks/*`, or any CI workflow; its
  docstring claims a "CI nightly / update doctor" home that does not exist.
  Flag for wiring or explicit acceptance, not drop.
- **`check_coverage_lib.py` / `check_coverage_extra_lib.py`** are pure libraries
  (no `main`), not independent gates — classify with `check_coverage.py`.

## Next decision (for the operator)

Each DROP softens/removes a **blocking** gate = a quality-contract change needing
its own sign-off + fresh-eye review (route through `quality`). Recommended order:
**DROP #1 (test-production-ratio) → #2 (title-slug --strict) → length-floor
Option-2 config-ification → #4/#5 partial demotions → BUY consolidations**. None
landed yet — triage only, per "triage 먼저".
