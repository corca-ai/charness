# Dup-Review Portability Falsification Audit — VERIFIED reclassification

Date: 2026-06-30. Method: per-family workflow (25 families x judge->adversarial-refute,
50 agents). Anchor = the fae23 precedent (a shared module the members ALREADY depend on
adds ZERO new coupling, so "would couple / keep skill-local-portable" is testable, not assumed).

## CRITICAL CORRECTION (post-audit fresh-eye review)

The workflow audit tested behavior-neutrality + zero-coupling but did **not** know a
standing architectural decision: **#390 / commit `a741e613` explicitly considered and
REJECTED "full consolidation to a shared import" of the per-skill resolver/bootstrap
scaffolding**, on three grounds — the *bare-shell invocation contract*, the
*no-cross-skill-import rule*, and the *planned `packages/` split* ("charness ships
standalone portable plugins, so the copy is correct"). `check_bootstrap_shim_consistency.py`
machine-governs 93 shim sites at byte-identity. So **per-skill resolver-scaffolding
duplication is a VERIFIED-intentional portability contract, not falsified debt.**

Therefore the resolver-scaffolding "fixable" verdicts below are **OVERRIDDEN to
intentional-per-#390**:

- `fe221bab` (resolve_adapter `main()` CLI tail, 6 skills) → **intentional (#390)**
- `54bc9db2` (resolve_adapter CLI driver, ~5 skills) → **intentional (#390)** (the refuter was right; my first-pass reconciliation that kept it fixable was WRONG)
- `3edc6552` (debug/gather resolver glue) → **intentional (#390)** (resolver scaffolding)
- `704b93d2` (find_adapter) → **#390-contested**: skill copies are #390-covered; only the repo-infra `*_adapter_lib.py` copies are outside the portable-plugin scope.

**Surviving genuinely-fixable set (NOT resolver scaffolding; adopt an already-imported
repo-root helper, so #390 does not apply):** `16fec8ed`, `878bffbe`, `c2c42ffe`,
`a664a431` (2/3 members are repo-infra), `13741926` (doc). `b8dbc45f` stays deferred —
adopting `subprocess_guard.run_process` changes the timeout message (`…while running cmd`),
not behavior-neutral.

## Headline (pre-correction workflow tally; see correction above)

- **11/25 families** the workflow flagged REDUCIBLE — but ~4 are resolver scaffolding the #390 contract keeps intentional, so the genuinely-actionable set is **~5–6 families** (the non-resolver adopt-existing-helper cases).
- **14/25 stay intentional** — but most need their NOTE reworded (the real reason is simplicity / repo-infra / north-star uniformity, NOT portability).
- **Two systematic findings the refuters surfaced:**
  1. The fae23 rule generalizes to *the home the members already depend on*. For adapter resolvers that is repo-root `scripts/`, NOT `skills/shared/` — picking the wrong home is what made several look intentional.
  2. **Several families are UN-MIGRATED re-implementations of helpers that ALREADY EXIST** in repo-root `scripts/` (`subprocess_guard.run_process`, `simple_skill_adapter_lib.load_simple_adapter`, `public_skill_dogfood_lib`). Pure adoption — zero new abstraction. (Verified to exist.)
- Irony: the single biggest raw family — **cd865345 (414 dl)** — is the one that is HONESTLY irreducible (bootstrap-of-bootstrap chicken-and-egg).

## REDUCIBLE / fixable (the audit's action set)

| family | dl | reduction home | refuter | note |
|---|---:|---|---|---|
| `5e1af1bc` | 574 | scripts/simple_skill_adapter_lib.py (load_simple_adapter — EXISTS) | refined | Reducible: the shared validate_adapter_data prologue (infer_defaults + version int-check +… |
| `b8dbc45f` | 119 | — | FLIP int->fix | Keep local on SIMPLICITY, not portability: the only common slice is a ~3-line TimeoutExpir… |
| `fe221bab` | 113 | scripts/simple_skill_adapter_lib.py (load_simple_adapter — EXISTS) | confirmed | argparse/main-guard CLI scaffolding, byte-identical across 6 resolve_adapter.py mains; the… |
| `16fec8ed` | 80 | scripts/scaffold_artifact_lib.py | confirmed | fixable: record-role payload_for dict is a meaningful extractable core into the already-lo… |
| `878bffbe` | 76 | scripts/public_skill_dogfood_lib.py (EXISTS) | confirmed | fixable: format_human + main are byte-identical pure CLI glue; the heavy build_matrix logi… |
| `a664a431` | 64 | scripts/adapter_lib.py | confirmed | Reducible but NOT for portability reasons: 2 of 3 members are top-level scripts/*_adapter_… |
| `54bc9db2` | 50 | skills/shared/scripts/ (e.g. a run_adapter_cli(* | refined | Adapter-resolution CLI driver (arm_cli_timeout + --repo-root argparse + sorted-keys JSON-t… |
| `c2c42ffe` | 42 | skills/shared/scripts/ — a helper e.g. emit_tool | confirmed | tool-recommendation CLI emit-core (build payload dict + recommendations_for_role/load_mani… |
| `704b93d2` | 30 | scripts/adapter_lib.py | confirmed | fixable: byte-identical find_adapter (md5 c1b01eab) is a coherent named helper, not a coin… |
| `13741926` | 28 | A single OPERATOR_QUEUE_SCAFFOLD constant owned  | confirmed | fixable: the Operator Decision Queue seed is byte-identical across achieve goal_artifact_t… |
| `3edc6552` | 20 | scripts/simple_skill_adapter_lib.py (load_simple_adapter — EXISTS) | FLIP int->fix | Keep-local on SIMPLICITY, not portability: this is coincidental per-skill adapter-wiring g… |

## Genuinely intentional (keep) — NOTE reframed to the real reason

| family | dl | real reason | note |
|---|---:|---|---|
| `cd865345` | 414 | verified-true | Bootstrap-of-the-bootstrap: this block IS the loader that resolves SKILL_RUNTIME, so it ca… |
| `322d067a` | 240 | not-portability-based | Intentional planner-uniformity: the identical ## Bootstrap header plus canonical "Resolve … |
| `fee3c32b` | 153 | not-portability-based | Keep-local on SIMPLICITY, not portability: the real reusable logic (base_adapter_items, ru… |
| `8ad80f4c` | 108 | not-portability-based | Keep local on SIMPLICITY grounds (coincidental idiom), not portability: this is the trivia… |
| `35bbd5df` | 101 | not-portability-based | Coincidental spec_from_file_location loader idiom (~10 lines, per-file error string), not … |
| `d772cd8f` | 90 | not-portability-based | Coincidental stdlib idiom (the canonical `if __name__=="__main__": try: sys.exit(main()) e… |
| `d54c2ed9` | 69 | not-portability-based | Keep local on SIMPLICITY, not portability: 4 of 5 members are top-level scripts/*.py repo … |
| `46e942ae` | 58 | not-portability-based | Keep-local on SIMPLICITY, not portability: the meaningful core is ALREADY single-sourced i… |
| `4dd7b07d` | 36 | not-portability-based | Coincidental call-site idiom, keep local on SIMPLICITY (not portability): the real shared … |
| `ac9c909a` | 26 | not-portability-based | Coincidental CLI-entrypoint idiom (__main__ guard + broken-config print/exit tail), not a … |
| `7dbc27a3` | 24 | not-portability-based | Coincidental sys.path bootstrap idiom across top-level scripts/ repo-infra (not skills/), … |
| `c4b45fc9` | 20 | not-portability-based | Coincidental idiom, keep local on SIMPLICITY grounds (not portability): the only overlap i… |
| `40a4e156` | 15 | not-portability-based | Intentional: the 2 matched lines are the validator-enforced goal-artifact `## Slice Plan` … |
| `aca9e00f` | 6 | not-portability-based | Intentional: identical `## Bootstrap` preamble (heading + one-line pointer to shared/refer… |

## Reconciliation of the 4 refuted=true verdicts

- **5e1af1bc (574)** — stays fixable, but refuter showed the clean-block story is wrong: member-specific validation is interleaved in a 21-31 line gap, and the named host helper is NOT actually consumed by members. Realizable win is smaller than 574; extract only the truly byte-identical sub-blocks.
- **54bc9db2 (50)** — refuter said intentional by fixating on a `skills/shared/` home (which WOULD add coupling). Correct home is repo-root `scripts/` (already depended) → stays **fixable**.
- **b8dbc45f (119)** — refuter FLIPPED intentional→fixable: `scripts/subprocess_guard.run_process` already implements the exact timeout idiom, already parameterized. Adopt it.
- **3edc6552 (20)** — refuter FLIPPED intentional→fixable: `scripts/simple_skill_adapter_lib.load_simple_adapter` exists and handoff/setup already use it; this span is an un-migrated re-impl.
