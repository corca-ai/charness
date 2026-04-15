# Operator Acceptance

This document translates the remaining roadmap into operator-owned acceptance
runs.

Use it when you want to take over one roadmap item directly instead of asking
an agent to discover the whole repo state again.

## Shared Start

Run these first at the repo root:

```bash
git status --short
sed -n '1,220p' docs/handoff.md
sed -n '1,260p' docs/roadmap.md 2>/dev/null || true
./scripts/run-quality.sh
```

If the work touches evaluator, integrations, or packaging, also read:

```bash
sed -n '1,220p' docs/control-plane.md
sed -n '1,220p' docs/public-skill-validation.md
```

## Remaining Items

### 1. Close Deferred Decisions

Why this exists:

- A deferred product-boundary backlog existed in `docs/handoff.md` `Discuss`.
- It is now closed in [docs/deferred-decisions.md](deferred-decisions.md) (2026-04-10 batch), and should only be reopened by explicit triggers.

Read first:

- [docs/handoff.md](handoff.md)
- [docs/deferred-decisions.md](deferred-decisions.md)
- [docs/host-packaging.md](host-packaging.md)
- [docs/control-plane.md](control-plane.md)

Suggested agent prompt:

```text
Read docs/deferred-decisions.md and adjacent current planning docs. If any
reopen trigger is active, propose and record the minimum decision update
needed; otherwise confirm closure and continue to cautilus integration work.
```

Acceptance:

- `docs/deferred-decisions.md` stays in sync with current product-boundary choices.
- `docs/handoff.md` `Discuss` is either empty or scoped to explicit reopen triggers only.
- Any reopened decision records its new choice and impacted docs.
- `./scripts/run-quality.sh` passes after the doc updates.

### 2. Wire `cautilus` Into `charness`

Why this exists:

- `public-skill-validation.md` already says which public skills are
  `evaluator-required`.
- The upstream evaluator contract is now connected at the integration-manifest
  layer, but maintained scenario usage still needs to become real.

Read first:

- [docs/public-skill-validation.md](public-skill-validation.md)
- [docs/control-plane.md](control-plane.md)
- [docs/handoff.md](handoff.md)
- [.agents/cautilus-adapter.yaml](../.agents/cautilus-adapter.yaml)

Useful local commands:

```bash
python3 scripts/doctor.py --repo-root . --json
python3 scripts/validate-integrations.py --repo-root .
python3 scripts/run-evals.py --repo-root .
```

If `~/cautilus` is available, also inspect its current contract surface before
editing `charness`.

Suggested agent prompt:

```text
Use the existing validation-tier policy and wire the real cautilus contract into
charness. Add the integration manifest, update control-plane/docs/tests, and
connect evaluator-required skills to honest scenario validation without
placeholder claims.
```

Acceptance:

- `cautilus` has a real integration surface in `charness`.
- `docs/public-skill-validation.md` is confirmed or minimally adjusted against
  the actual upstream contract.
- Repo-owned tests/evals/docs reflect the new evaluator path and any added
  maintained scenario wiring honestly.
- `./scripts/run-quality.sh` passes.

### 3. Run Managed CLI Install Experiments

Why this exists:

- a checked-in plugin install surface now exists under `plugins/charness`
- the repo now claims one thin-CLI-managed install/update path across hosts
- initial install/bootstrap is largely proven; the remaining real-host question is whether `charness update` propagates upstream skill/plugin changes into the actually installed host-visible copy

Read first:

- [INSTALL.md](../INSTALL.md)
- [UNINSTALL.md](../UNINSTALL.md)
- [README.md](../README.md)
- [docs/host-packaging.md](host-packaging.md)
- [packaging/charness.json](../packaging/charness.json)

Useful local commands:

```bash
python3 scripts/validate-packaging.py --repo-root .
python3 scripts/sync_root_plugin_manifests.py --repo-root .
charness doctor
charness tool doctor cautilus
charness tool install cautilus
charness tool update agent-browser
```

Suggested operator runs:

- bootstrap or reuse the managed checkout under `~/.agents/src/charness` with
  `charness init`; use `./init.sh` only when the binary is not already
  available on PATH
- treat initial install/enable as pre-proven unless the host reports otherwise
- make an explicit upstream payload change that should be visible in a loaded
  skill or plugin manifest
- run `charness update`
- verify Claude by checking that the changed payload is reflected in the
  installed host copy after the documented restart/reload step
- Codex update propagation is already operator-proven; keep any future rerun as
  an on-demand regression check rather than a standing acceptance blocker
- if you need to rerun the update-propagation experiment locally, prefer
  `pytest -q tests/charness_cli/test_update_propagation.py` plus a human host
  spot-check instead of turning it back into a default every-session task
- if you want the full local install/update regression suite before or after
  host testing, run `./scripts/self-validate-install-update.sh`

Acceptance:

- install works from the documented managed local install surface rooted at `~/.agents/src/charness`
- explicit operator clone is not required when a standalone `charness` binary
  is already available and can bootstrap that managed checkout internally
- non-managed `--repo-root` runs stay proof/development-only and do not become the installed CLI source
- `charness init` deterministically creates the Codex source plugin root and
  personal marketplace entry
- `charness doctor` distinguishes “surface prepared” from “host install/enable
  still required”
- `charness tool install/update/doctor` leave machine-readable lock state for
  external dependencies and any remaining manual steps
- `charness update` refreshes the installed CLI itself before judging downstream
  host behavior
- an upstream skill/plugin payload change is actually observable in the
  installed Claude or Codex host copy after the required refresh step
- any required doc or manifest tweaks are committed back here

### 4. Raise `create-skill` / `spec` Workflow Gates

Why this exists:

- those skills still lean more on contract-marker checks than on workflow smoke

Read first:

- [skills/public/create-skill/SKILL.md](../skills/public/create-skill/SKILL.md)
- [skills/public/spec/SKILL.md](../skills/public/spec/SKILL.md)
- [scripts/check-skill-contracts.py](../scripts/check-skill-contracts.py)
- [scripts/run-evals.py](../scripts/run-evals.py)

Suggested agent prompt:

```text
Take create-skill and spec from marker-level contract checks to stronger
repo-owned workflow smoke without introducing fake guarantees or host-specific
assumptions.
```

Acceptance:

- at least one stronger deterministic workflow check exists for each targeted
  skill
- docs and tests describe the stronger proof honestly
- `./scripts/run-quality.sh` passes

### 5. Decide Adapter Requirements Per Public Skill

Why this exists:

- some public skills still have no checked-in adapter contract
- the repo has now seen that “probably fine without adapter” can be wrong

Read first:

- [skills/public/impl/SKILL.md](../skills/public/impl/SKILL.md)
- [skills/public/quality/SKILL.md](../skills/public/quality/SKILL.md)
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)

Useful local commands:

```bash
for d in skills/public/*; do [ -f "$d/adapter.example.yaml" ] && echo "adapter $d" || echo "no-adapter $d"; done
python3 scripts/validate-adapters.py --repo-root .
```

Suggested agent prompt:

```text
Classify which public skills truly require checked-in adapters and which can
stay adapter-free honestly. Then turn that classification into a deterministic
repo-owned gate.
```

Acceptance:

- the classification is recorded in canonical docs or validator logic
- obviously adapter-dependent skills fail closed if their adapter contract is
  missing
- `./scripts/run-quality.sh` passes

## Closeout Rule

For any accepted item:

1. update the canonical doc(s)
2. run the strongest honest local validation
3. commit the work
4. update [docs/handoff.md](handoff.md) if the next
   operator's first move changed
