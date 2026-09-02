# Operator Acceptance

> Status: conditional (operator takeover path)
> Source of truth: functional checks, the active Goal Run parent/cursor, and the active plan
> Last verified: 2026-09-02

This document translates active work into operator-owned acceptance runs. The
current plan of record is the active [Goal Run parent issue #765](https://github.com/corca-ai/charness/issues/765).
Use this page when you want to take over one item directly instead of asking an
agent to rediscover the whole repo state. A consumer may add an optional
roadmap surface when active ordered work requires it.
Each item names the ownership seam, read-first surfaces, and acceptance bar. Restate that material in your own prompt instead of copying another embedded prompt block into chat.

## Shared Start

Run these first at the repo root:

```bash
git status --short
./scripts/run-quality.sh
```

If the work touches integrations or packaging, also read:

```bash
sed -n '1,220p' docs/control-plane.md
sed -n '1,220p' docs/public-skill-validation.md
```

## Progressive Operator Path

See [docs/operator-progressive-path.md](./operator-progressive-path.md) for the per-horizon operator capability map (Day 1, Week 8, Month 6).

## Remaining Items

### 1. Close Deferred Decisions

Focus: keep deferred product-boundary decisions closed unless a real reopen trigger is active.

Read first:

- [docs/goal-lifecycle.md](./goal-lifecycle.md) — current Goal Run parent/cursor and continuation contract.
- [docs/deferred-decisions.md](./deferred-decisions.md) — closed product-boundary decisions, record shape, and reopen triggers.
- [docs/host-packaging.md](./host-packaging.md) — export contract for host plugin layouts and its source-of-truth surfaces.
- [docs/control-plane.md](./control-plane.md) — external tool manifests, support capability metadata, and lock state rules.

Acceptance:

- [`docs/deferred-decisions.md`](./deferred-decisions.md) stays in sync with current product-boundary choices.
- The active Goal Run parent/cursor is current and has no stale next-child claim.
- Any reopened decision records its new choice and impacted docs.
- [`./scripts/run-quality.sh`](../scripts/run-quality.sh) passes after the doc updates.

### 2. Run Managed CLI Install Experiments

Focus: confirm that the managed install/update path changes the host-visible payload, not only the source checkout.

Read first:

- [README.md](../README.md) — product framing, managed install quick start, and everyday CLI commands.
- [docs/host-packaging.md](./host-packaging.md) — export contract for host plugin layouts and its source-of-truth surfaces.
- [packaging/charness.json](../packaging/charness.json) — shared packaging manifest: identity, version, bundle inputs, host export paths.

Useful local commands:

```bash
python3 scripts/validate_packaging.py --repo-root .
python3 scripts/sync_root_plugin_manifests.py --repo-root .
charness doctor
charness update all
charness tool update agent-browser
```

Suggested operator runs:

- bootstrap or reuse the managed checkout under `~/.agents/src/charness` with
  `charness init`; use [`./init.sh`](../init.sh) only when the binary is not already
  available on PATH
- treat initial install/enable as pre-proven unless the host reports otherwise
- make an explicit upstream payload change that should be visible in a loaded
  skill or plugin manifest
- run `charness update`
- run `charness update all` when the acceptance run also needs tracked external
  binaries and bundled support skill surfaces refreshed
- verify Claude by checking that the changed payload is reflected in the
  installed host copy after the documented restart/reload step
- Codex update propagation is already operator-proven; keep any future rerun as
  an on-demand regression check rather than a standing acceptance blocker
- if you need to rerun the update-propagation experiment locally, prefer
  `pytest -q tests/charness_cli/test_update_propagation.py` plus a human host
  spot-check instead of turning it back into a default every-session task
- if you want the full local install/update regression suite before or after
  host testing, run [`./scripts/self-validate-install-update.sh`](../scripts/self-validate-install-update.sh)

Acceptance:

- install works from the documented managed local install surface rooted at `~/.agents/src/charness`
- explicit operator clone is not required when a standalone `charness` binary
  is already available and can bootstrap that managed checkout internally
- non-managed `--repo-root` runs stay proof/development-only and do not become the installed CLI source
- `charness init` deterministically creates the Codex source plugin root and
  personal marketplace entry
- `charness doctor` distinguishes “surface prepared” from “host install/enable
  still required”
- `charness init` and `charness update` return nonzero for an explicit failed
  host-install/cache-readback status; optional `skipped` or `unavailable`
  host states remain typed in YAML rather than being treated as failures
- `charness tool install/update/doctor` leave machine-readable lock state for
  external dependencies and any remaining manual steps
- `charness update` refreshes the installed CLI itself before judging downstream
  host behavior
- `charness update all` keeps the same self-update contract and also runs the
  tracked external tool update/support-refresh flow in one command
- an upstream skill/plugin payload change is actually observable in the
  installed Claude or Codex host copy after the required refresh step
- any required doc or manifest tweaks are committed back here

### 3. Raise `create-skill` / `spec` Workflow Gates

Focus: move `create-skill` and `spec` from marker-level checks to stronger workflow smoke.

Read first:

- [skills/public/create-skill/SKILL.md](../skills/public/create-skill/SKILL.md) — the portable skill authoring workflow and its bootstrap reads.
- [skills/public/spec/SKILL.md](../skills/public/spec/SKILL.md) — the implementation-contract workflow and its bootstrap reads.
- [docs/public-skill-dogfood.md](./public-skill-dogfood.md) — human-readable contract for the reviewed consumer-prompt registry.
- [tools/check_skill_contracts.py](../tools/check_skill_contracts.py) — pinned SKILL.md contract phrases and the pin-deletion discipline.
- [tools/run_evals.py](../tools/run_evals.py) — runner for the repo-owned deterministic skill and adapter scenarios.
- [tools/validate_public_skill_dogfood.py](../tools/validate_public_skill_dogfood.py) — validator entrypoint for the dogfood registry JSON.

Acceptance:

- at least one stronger deterministic workflow check exists for each targeted
  skill
- docs and tests describe the stronger proof honestly
- [`./scripts/run-quality.sh`](../scripts/run-quality.sh) passes

### 4. Decide Adapter Requirements Per Public Skill

Focus: classify which public skills must fail closed on missing adapters and turn that into a deterministic rule.

Read first:

- [skills/public/impl/SKILL.md](../skills/public/impl/SKILL.md) — the slice implementation workflow and its conditional evidence route to `prove`.
- [skills/public/quality/SKILL.md](../skills/public/quality/SKILL.md) — the quality posture workflow, adapter bootstrap, and gate planning.
- [docs/public-skill-validation.md](./public-skill-validation.md) — validation tiers plus per-skill adapter and missing-adapter rules.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md) — the latest quality review: scope, gates, weak and missing areas.

Useful local commands:

```bash
for d in skills/public/*; do [ -f "$d/adapter.example.yaml" ] && echo "adapter $d" || echo "no-adapter $d"; done
python3 scripts/validate_adapters.py --repo-root .
```

Acceptance:

- the classification is recorded in canonical docs and machine-readable policy
- missing-adapter behavior is explicit per public skill: `allow`, `visible`,
  or `block`
- high-leverage repo-truth, review-state, or release skills do not silently
  fall back when their adapter contract is missing
- [`./scripts/run-quality.sh`](../scripts/run-quality.sh) passes

## Closeout Rule

For any accepted item:

1. update the canonical doc(s)
2. run the strongest honest local validation
3. commit the work
4. update the active Goal Run parent cursor if the next operator's first move changed
