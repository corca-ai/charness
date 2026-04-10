# Operator Acceptance

This document translates the remaining roadmap into operator-owned acceptance
runs.

Use it when you want to take over one roadmap item directly instead of asking
an agent to discover the whole repo state again.

## Shared Start

Run these first in `/home/ubuntu/charness`:

```bash
git status --short
sed -n '1,220p' docs/handoff.md
sed -n '1,260p' docs/master-plan.md
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

- `docs/handoff.md` still has a `Discuss` backlog.
- The next planned session is to close those product-boundary decisions before
  `cautilus` integration.

Read first:

- [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md)
- [docs/master-plan.md](/home/ubuntu/charness/docs/master-plan.md)
- [docs/host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md)
- [docs/control-plane.md](/home/ubuntu/charness/docs/control-plane.md)

Suggested agent prompt:

```text
Read docs/handoff.md Discuss and docs/master-plan.md. Propose concrete decisions
for the still-open product-boundary items, challenge weak assumptions, then
update the docs to record the decisions we actually made.
```

Acceptance:

- `docs/handoff.md` `Discuss` list is materially smaller or explicitly
  narrowed.
- The chosen decisions are reflected in canonical docs, not only chat.
- `./scripts/run-quality.sh` passes after the doc updates.

### 2. Wire `cautilus` Into `charness`

Why this exists:

- `public-skill-validation.md` already says which public skills are
  `evaluator-required`.
- The upstream evaluator contract still needs to be connected.

Read first:

- [docs/public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md)
- [docs/control-plane.md](/home/ubuntu/charness/docs/control-plane.md)
- [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md)
- [.agents/cautilus-adapter.yaml](/home/ubuntu/charness/.agents/cautilus-adapter.yaml)

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
- Repo-owned tests/evals/docs reflect the new evaluator path.
- `./scripts/run-quality.sh` passes.

### 3. Run Claude/Codex Direct-Install Experiments

Why this exists:

- root plugin manifests are now checked in
- public install/update behavior still needs real-host confirmation

Read first:

- [README.md](/home/ubuntu/charness/README.md)
- [docs/host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md)
- [packaging/charness.json](/home/ubuntu/charness/packaging/charness.json)

Useful local commands:

```bash
python3 scripts/validate-packaging.py --repo-root .
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/plugin_preamble.py --repo-root .
```

Suggested operator runs:

- Claude Code:
  - try the shared marketplace path from `README.md`
  - try local `--plugin-dir /absolute/path/to/charness`
- Codex:
  - use the checked-in `.agents/plugins/marketplace.json`
  - reload Codex after updating the checkout

Acceptance:

- install works from the documented root artifacts
- update behavior matches the documented model
- any required doc or manifest tweaks are committed back here

### 4. Raise `create-skill` / `spec` Workflow Gates

Why this exists:

- those skills still lean more on contract-marker checks than on workflow smoke

Read first:

- [skills/public/create-skill/SKILL.md](/home/ubuntu/charness/skills/public/create-skill/SKILL.md)
- [skills/public/spec/SKILL.md](/home/ubuntu/charness/skills/public/spec/SKILL.md)
- [scripts/check-skill-contracts.py](/home/ubuntu/charness/scripts/check-skill-contracts.py)
- [scripts/run-evals.py](/home/ubuntu/charness/scripts/run-evals.py)

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

- [skills/public/impl/SKILL.md](/home/ubuntu/charness/skills/public/impl/SKILL.md)
- [skills/public/quality/SKILL.md](/home/ubuntu/charness/skills/public/quality/SKILL.md)
- [skill-outputs/quality/quality.md](/home/ubuntu/charness/skill-outputs/quality/quality.md)

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

## Ceal Repo Items

These are roadmap items, but they should be done in the Ceal repo, not here.

### 6. Apply Full `charness` In Ceal Maintainer Environment

Read first from this repo:

- [docs/ceal-consumption-model.md](/home/ubuntu/charness/docs/ceal-consumption-model.md)

Success looks like:

- Ceal maintainer workflows consume full `charness`
- Ceal does not maintain a fork-like local copy
- any local materialization is generated/pinned, not hand-edited

### 7. Build Ceal Organization Presets

Read first from this repo:

- [docs/ceal-consumption-model.md](/home/ubuntu/charness/docs/ceal-consumption-model.md)
- [presets/README.md](/home/ubuntu/charness/presets/README.md)

Success looks like:

- Ceal Slack app org installs expose Ceal-owned presets, not raw full-harness
  internals
- preset exposure contract is explicit

### 8. Run Ceal-Side Validation

Success looks like:

- Ceal seeded flows use the shared harness cleanly
- Ceal-specific prompt/preset behavior is validated in Ceal, not hidden in
  shared skill bodies

## Closeout Rule

For any accepted item:

1. update the canonical doc(s)
2. run the strongest honest local validation
3. commit the work
4. update [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md) if the next
   operator's first move changed
