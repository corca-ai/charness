# Issue draft — code-layer duplication follow-ups (sub-issue of #390)

Status: **DRAFT** — file as a sub-issue of #390 at the push phase.
Parent: corca-ai/charness#390 (one-pass code-layer quality pass).

## Context

The #390 one-pass (record:
`charness-artifacts/quality/2026-06-19-390-code-layer-quality-pass.md`) baselined
the intentional/portability clone mass (`charness-artifacts/quality/nose-baseline.json`,
547 families) but deliberately **kept 14 genuine extractable families visible**
in the standing nose advisory rather than burying them. This issue tracks those
so they are not lost, and so a future `--write-baseline` is not run blindly while
they are open (which would re-accept them).

## Surfaced candidates (run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root .`)

1. **Release subprocess-timeout wrapper** (1 family, 7 sites) — `release/scripts/`
   `check_fresh_checkout_probes.py`, `check_requested_review_gate.py`,
   `publish_release_helpers.py`, `bump_version.py`, plus `check_supply_chain_online.py`,
   `run_dead_code_advisory.py`. Identical `subprocess.run(shell=True, /bin/bash,
   timeout) → CompletedProcess(124) on TimeoutExpired`. Extract one
   `run_bash(cmd, *, cwd, timeout) -> CompletedProcess` via the export-safe
   sibling-import pattern; callers keep their own post-processing.
   **Deferred from #390 for release-sequencing** (it touches the machinery used to
   cut the release in that same session) — do it on a non-release session.
2. **`scaffold_*_artifact.py` shared scaffolding** (several families) across
   `critique/`, `retro/`, `ideation/`, `debug/`, `handoff/`, `quality/`. Cross-
   package → needs a shared-seam / portability decision before extraction.
3. **`*_adapter_lib` / `_adapter_policy` shared logic** (3 families) —
   `critique_adapter_lib.py`, `proof_semantics_adapter_lib.py`,
   `achieve_adapter_policy.py`, `cautilus_adapter_lib.py`. Classify intentional-
   adapter-boilerplate vs genuinely shareable before acting.

## Baseline robustness gap (from the 0.52.5 release critique)

The written `nose-baseline.json` records **no scanner `tool_version`**, yet the
contract repeatedly says "re-baseline per scanner version." So a future `nose`
upgrade silently reads a stale baseline with no version-mismatch detection — the
exact trap the prose warns about, unenforced. Fix: have `--write-baseline` stamp
the `nose` version into the baseline (or a sidecar) and have the read path warn on
mismatch. Small, real robustness fix; deferred from the release as a follow-up.

## Discipline

Each is `mutate → sync → verify → publish`, test-first, fresh-eye critique at the
slice boundary. Some scaffold families are tiny (4–6 dup-lines) and may be
**won't-fix**; decide per family rather than chasing the count. After any of
these land, re-baseline (`--write-baseline`) so the fixed family drops out.
