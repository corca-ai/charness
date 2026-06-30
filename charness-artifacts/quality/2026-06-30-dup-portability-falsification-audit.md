# Dup-Review Portability Falsification Audit — VERIFIED reclassification

Date: 2026-06-30. Method: per-family workflow (25 families x judge->adversarial-refute,
50 agents). Anchor = the fae23 precedent (a shared module the members ALREADY depend on
adds ZERO new coupling, so "would couple / keep skill-local-portable" is testable, not assumed).

## CORRECTION TRAIL (two passes — read this first)

**Pass 1 (fresh-eye, over-corrected):** a fresh-eye review flagged that #390 / commit
`a741e613` "REJECTED resolver-scaffolding consolidation," so I first flipped the
resolve_adapter "fixable" verdicts to intentional-per-#390. **That over-corrected.**

**Pass 2 (challenged + PROVEN — current truth):** re-reading the actual artifacts shows
#390's governance is **narrower** than the flip assumed:

- `check_bootstrap_shim_consistency.py` governs **only** the `_load_skill_runtime_bootstrap`
  *finder shim* (`SHIM_NAME` = that one function) — i.e. **`cd865345`**, the
  bootstrap-of-bootstrap that genuinely cannot be shared (chicken-and-egg). That stays
  verified-true intentional.
- #390's "reject full consolidation to a shared import / bare-shell invocation contract"
  is about that **finder** (it must be inline so the script can bootstrap itself), **not**
  the resolver `main()` CLI tail. The CLI tail runs *after* the finder and already calls
  `SKILL_RUNTIME.arm_cli_timeout` — an **already-shared** bootstrap function.
- So extracting the byte-identical CLI tail into `SKILL_RUNTIME.run_adapter_cli` (beside
  `arm_cli_timeout`, skill-specific `load_adapter`/label/help kept local) is the *same
  established mechanism*, adds zero new coupling, and is **proven behavior-neutral**:
  16/16 resolvers emit byte-identical `--json` + identical `--help` after the change.

**Resolver CLI tail = genuinely FIXABLE, and now DONE** (this session):

- `fe221bab` + `54bc9db2` (resolve_adapter/review_adapter `main()` tail, **16 skills**)
  → **EXTRACTED** into `SKILL_RUNTIME.run_adapter_cli` (commit follows). #390 does not block it.

Still genuinely intentional: `cd865345` (414, finder shim, governed). Still deferred:
`b8dbc45f` (adopting `subprocess_guard.run_process` changes the timeout message — not
behavior-neutral). Remaining fixable survivors queued: `16fec8ed`, `878bffbe`, `c2c42ffe`,
`a664a431`, `704b93d2`, `3edc6552`, `13741926`.

**Lesson (sharpened):** a "standing decision" override is only as broad as what the gate
*actually* governs — read the gate's scope (here: one finder function), don't infer a
blanket from the commit's headline. The duplication-is-harm default wins unless a real,
scoped contract says otherwise.

## Headline (original workflow tally)

- **11/25 families** the workflow flagged REDUCIBLE — confirmed for the resolver CLI tail
  (now extracted, behavior-neutral proven) and the non-resolver survivors; only `cd865345`
  (finder shim) is genuinely irreducible.
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
