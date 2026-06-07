# Critique — handoff-3 Changed-Line Coverage Gate as a `quality` Capability

Standalone bounded critique for handoff-3 (internal; no GitHub issue): promoting
the charness changed-line mutation pre-merge gate to a reusable, inheritable
`quality` capability + adapter contract. Classification: feature (a new portable
capability, not a behavior defect — `debug: n/a — capability design`).

## Reviewer Provenance

Bounded fresh-eye `critique` subagent (general-purpose, read-only) run this
session against the staged slice (`git diff HEAD`, plus a bare /tmp fixture repo
with no `cosmic-ray.toml` to prove portability — no charness-repo mutation). The
reviewer probed inheritability, the `**`-aware glob matcher (18 edge cases),
skip/fail polarity, adapter validation, the content-fingerprint across the commit
boundary, and drift vs the active charness gate.

## Verdict

**Ship.** No blockers. Two nits found and fixed before commit.

## Inheritability (the seeded concern) — confirmed

The portable capability is genuinely inheritable: the three reused libs
(`mutation_changed_files_lib`, `mutation_sampling_lib`, `quality_adapter_lib`,
plus the transitive `mutation_line_coverage_lib`) are exported byte-identical to
`plugins/charness/scripts/`, so a consuming repo that installs the charness
plugin gets them. The two consumed functions (`classify_changed_line_scope_gap`,
`load_file_statement_lines`) are tool-neutral (git diff + coverage.py JSON only);
the sole cosmic-ray import in `mutation_sampling_lib` is lazy and never reached.
The eligible set is glob-driven, inert when unconfigured. Verified by running the
full producer→consumer cycle in a bare /tmp repo with no `cosmic-ray.toml`.

## Blockers

None.

## Nits (found and FIXED before commit)

- **Marker-path collision footgun (low severity).** Both gates derive the
  freshness marker as `<coverage_json>.fingerprint` but compute different
  fingerprints (different prefix + pool source). If a consuming repo points the
  portable gate at the same `coverage_json` a separate fingerprint-stamping flow
  uses, each reads the other's marker as stale → silent non-blocking skip (never
  a false fail — polarity safe). Fixed: `mutation-testing.md` now warns to give
  the gate its own `coverage_json` when another flow stamps the same report.
  (charness today is safe — the portable gate is dogfood-only and never run with
  `--stamp-marker`.)
- **Two-dot-vs-worktree clarity.** `changed_eligible` uses `base..head` (the
  change-set) while `changed_pool_vs_base` uses `base→worktree` (the fingerprint
  pool). Intentional (mirrors the active gate) but easy to misread; added a
  one-line comment.

## Over-Worry (raised, probed, ruled non-blocking)

- **Glob matcher.** 18 edge cases (recursive `**`, segment-bounded `*`,
  `**/tests/**` exclusion, `?` not crossing `/`, `\Z` anchoring) all correct.
- **Skip/fail polarity.** Invalid adapter → exit 1 (fails closed); every other
  non-clean state (inert / no base / no coverage / no eligible change / stale) →
  exit 0 non-blocking. Matches the active gate + the 6 tests.
- **Drift vs the active gate.** Both call the SAME classifier + coverage reader,
  so the blocking verdict is structurally identical; only the eligible-set source
  and fingerprint pool differ (intended).
- **False-green-HEAD warning + fingerprint stability** verified live on fixtures.
