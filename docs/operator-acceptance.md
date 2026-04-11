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
- It is now closed in [docs/deferred-decisions.md](/home/ubuntu/charness/docs/deferred-decisions.md) (2026-04-10 batch), and should only be reopened by explicit triggers.

Read first:

- [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md)
- [docs/deferred-decisions.md](/home/ubuntu/charness/docs/deferred-decisions.md)
- [docs/host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md)
- [docs/control-plane.md](/home/ubuntu/charness/docs/control-plane.md)

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
- Repo-owned tests/evals/docs reflect the new evaluator path and any added
  maintained scenario wiring honestly.
- `./scripts/run-quality.sh` passes.

### 3. Run Managed CLI Install Experiments

Why this exists:

- a checked-in plugin install surface now exists under `plugins/charness`
- the repo now claims one thin-CLI-managed install/update path across hosts
- public install/update behavior still needs real-host confirmation

Read first:

- [INSTALL.md](/home/ubuntu/charness/INSTALL.md)
- [UNINSTALL.md](/home/ubuntu/charness/UNINSTALL.md)
- [README.md](/home/ubuntu/charness/README.md)
- [docs/host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md)
- [packaging/charness.json](/home/ubuntu/charness/packaging/charness.json)

Useful local commands:

```bash
python3 scripts/validate-packaging.py --repo-root .
python3 scripts/sync_root_plugin_manifests.py --repo-root .
./charness doctor
```

Suggested operator runs:

- bootstrap or reuse the managed checkout, then run `./charness init`
- verify Claude with `claude-charness`
- verify Codex through `~/.agents/plugins/marketplace.json`
- run `charness update` and confirm both hosts stay aligned after refresh
- if the host output is ambiguous, record that ambiguity instead of claiming
  the install worked

Acceptance:

- install works from the documented managed local install surface
- update behavior matches the documented single-path model
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

## Closeout Rule

For any accepted item:

1. update the canonical doc(s)
2. run the strongest honest local validation
3. commit the work
4. update [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md) if the next
   operator's first move changed
