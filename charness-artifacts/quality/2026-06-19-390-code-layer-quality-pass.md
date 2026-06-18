# #390 code-layer quality pass — one-pass record (2026-06-19)

Re-scoped #390 (overhaul COMPLETE → lane discipline; see
`charness-artifacts/issue-drafts/2026-06-18-ceal-code-layer-quality.md`) then ran
the single closeable pass interactively at operator direction. In-scope:
`scripts/`, `skills/**/scripts/`, gate/validator code. Out of scope (other
tracks' lane): all prose surfaces.

## Leg 1 — duplication (nose 0.10.0, routed through `quality`)

- Scan: `inventory_nose_clones.py` over `scripts`, `skills/public`,
  `skills/support` (mode `syntax,semantic,near`, min-size 24): **560 families,
  2530 dup-lines in the top-20**.
- **Finding:** after applying the advisory-interpretation discipline, the top-20
  extractability families collapse into two *intentional, do-not-extract*
  classes:
  1. **Portability bootstrap boilerplate** — `resolve_adapter.py`,
     `init_adapter.py`, `_load_skill_runtime_bootstrap()`, `_RESOLVER_DIR`
     patterns. Deliberately copied so each skill package ships standalone;
     identity is already machine-governed by `validate_adapters.py`. Extracting
     breaks portability.
  2. **Idiomatic CLI entrypoint guards** — `if __name__ == "__main__": try:
     sys.exit(main()) except XError`. Different exception class each; extracting
     obscures the idiom and adds a "which helper" indirection.
- **Genuinely extractable, non-bootstrap candidates** (filed, not landed) — all
  in `charness-artifacts/issue-drafts/2026-06-19-code-layer-dup-followups.md`:
  - `#16` subprocess-timeout wrapper — a **cross-directory** family (7 sites:
    `release/scripts/{check_fresh_checkout_probes,check_requested_review_gate,publish_release_helpers,bump_version}.py`
    plus `scripts/check_supply_chain_online.py` and
    `quality/scripts/run_dead_code_advisory.py`). **Deferred for
    release-sequencing**: it touches the release machinery this session uses to
    cut the release; refactoring the tool right before relying on it is avoidable
    risk. NB: the baseline plumbing landed here (`nose_report_lib.run_nose`,
    `nose_baseline_lib.run_write_baseline`) **adds two more instances** of this
    same pattern — honest debt added to the same filed family, kept visible.
  - `#19` `scaffold_*_artifact.py`, `#14`, `#9` `*_adapter_lib` — cross-package;
    need a shared-seam / portability decision, not a one-pass mechanical refactor.
- **The held-visible set is a best-effort heuristic, not a complete
  classification.** It was derived from the top-20 extractability review and
  pulled by member-file signature; it can miss genuine debt below the top-20 and
  is internally inexact (e.g. small `*_adapter_lib` families are held visible
  while larger adapter families that also include `init_adapter` bootstrap stay
  baselined under the bootstrap guard). The `#9` adapter-lib intentional-vs-debt
  call is explicitly deferred to the follow-up issue.
- **Landed instead (test-first):** the **machine-owned-consistency** structural
  response the contract prescribes for intentional duplication — a nose
  **baseline**. Added `--baseline` / `--write-baseline` plumbing to
  `inventory_nose_clones.py` (3 new tests) and wrote the canonical
  `charness-artifacts/quality/nose-baseline.json`. Chosen over a hard `--exclude`
  because exclude blinds the advisory to copy-to-copy drift; baseline preserves
  it (proven: dropping one baselined family re-surfaces it).
  - **Length signal heeded with a real split, not gamed.** The plumbing pushed
    `inventory_nose_clones.py` over its length cap. Per implementation-discipline
    ("near-limit is a refactoring signal: cohesive unit or over-accumulation?"),
    the advisory was split by concern into three cohesive modules —
    `nose_baseline_lib.py` (baseline accept/write) and `nose_report_lib.py` (run
    nose + parse the versioned JSON report) beside the orchestrating
    `inventory_nose_clones.py` (now 240/360, signal cleared). An earlier
    squeak-under-by-trimming-help-text is no longer load-bearing — the split, not
    text compression, provides the 120 lines of headroom.
  - **The baseline accepts only the intentional/incidental drift-floor, NOT
    fixable debt.** A blanket `--write-baseline` first accepted all 561 current
    families — which would bury the genuine extractable candidates too. So the
    14 families matching the identified fixable candidates (#16 timeout-wrapper
    ×1 spanning 7 sites; #19 scaffold-artifact ×several; #9 adapter-libs ×3) were
    **pulled back out** of the baseline (final: **547 accepted**). They stay
    **visible** in the advisory as a short actionable list (14 families, 606
    dup-lines) instead of being silently accepted.
  - **Re-baseline caveat:** a future `--write-baseline` re-accepts whatever is
    currently a family, including these 14. Re-baseline only **after** the
    surfaced candidates are fixed (then they are no longer families) — not
    blindly — else fixable debt gets re-buried.
  - The ~547 accepted families are lower-extractability (nose's own ranking =
    lower fix-value) and are the standard "adopt existing clones, gate new"
    drift-floor; they were not individually classified in this one pass.

## Public-skill-validation review (`quality`, hitl-recommended)

The baseline plumbing is a **semantic change to the `quality` skill's nose-clone
advisory** (it now reads `nose-baseline.json` by default and reports only drift),
so the closeout required a public-skill-validation review. Decision, recorded:
the change is **internal advisory de-noising** — the `quality` skill's
consumer-facing contract (route to `quality`, run existing gates before proposing
new ones, refresh `charness-artifacts/quality/latest.md`, one realistic consumer
prompt) is **unchanged**; `validate_public_skill_dogfood` stays green (20/20). The
change was reviewed by a fresh-eye bounded critique (different agent context; ran
the structural sweep + 2181 quality-gate tests + executed both dev-tree and
exported-plugin copies). Cautilus is `next_action: none` (ask-before-run; no
evaluator scenario requested). Acked via `--ack-cautilus-skill-review`.

## Leg 2 — latent-defect sweep (`debug`)

Rigorous AST sweep across all **492** in-scope files over four classes:

- broad-except fail-open / silent-swallow → 5 hits, **all intentional** (best-
  effort optional reads with safe fallback; a session-start hook with
  `# pragma: no cover - never propagate hook errors`; JSON-shape predicates).
- mutable default args → **0**.
- `subprocess.run` without `timeout=` → 102 hits, but almost all local `git`;
  every network op (fetch/push/ls-remote) without a timeout is in `release/`
  (deferred by sequencing). The gather fetch chain is timeout-bounded downstream
  (`acquire_public_url.py --timeout`, default 20s).
- doc↔code drift (Leg 3).

**No concrete defect** in the swept classes; exception handling in the
gate/validator layer is disciplined and documented. No manufactured fix.

## Leg 3 — script-level doc↔code consistency

`docs/generated/cli-reference.md` regenerated → **in sync**;
`check_public_doc_coupling.py` clean; `check_command_docs.py` validated 31
command surfaces. Clean.

## Honest closeout

The in-scope code layer is in good shape — the recent overhaul + prior nose/
quality goals kept it disciplined. This pass's value is the **baseline** (de-
noises the standing advisory so future passes surface only genuine debt) plus
the filed `#16`. The dominant "duplication" is the intentional
portability-vs-local-duplication trade the architecture makes on purpose; the
baseline now encodes that decision as data instead of re-litigating it each run.
Per #390's "Done (landed **or** filed)", the pass is closeable: safest landing
shipped test-first, genuine remainder filed.
