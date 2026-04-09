# Quality Review

Date: 2026-04-09

## Scope

Repo-wide dogfood review of `charness` itself, with emphasis on:

- public skill package structure
- YAML frontmatter and adapter example integrity
- concept and metadata synchronization
- current executable quality gates
- repo-specific next lint/test/duplicate-check proposals

## Current Gates

What was actually runnable today:

- YAML frontmatter presence and parse sanity for every existing `skills/public/*/SKILL.md`
- adapter example parse sanity for skills that ship `adapter.example.yaml`
- `resolve_adapter.py --repo-root .` smoke runs for `debug`, `gather`,
  `handoff`, `quality`, and `retro`
- `scripts/validate-skills.py`, `scripts/validate-profiles.py`,
  `scripts/validate-adapters.py`, `scripts/validate-packaging.py`, and
  `scripts/check-doc-links.py`
- Python syntax compilation for every committed helper script under
  `skills/public/*/scripts/*.py`
- `ruff check scripts tests skills/public/*/scripts`
- `pytest -q`
- `scripts/run-quality.sh` as the repo-owned quality entrypoint
- checked-in `.agents/quality-adapter.yaml` resolve for the current repo
- `scripts/check-duplicates.py --fail-on-match` as a fail-closed duplicate gate
- `scripts/check-markdown.sh` via `markdownlint-cli2`
- `scripts/check-secrets.sh` via `secretlint`
- `scripts/check-shell.sh` as an optional `shellcheck` wrapper
- `scripts/check-links-external.sh` as an optional `lychee` wrapper
- JSON Schema validation for `profiles/constitutional.json` against
  `profiles/profile.schema.json`
- manual concept review against `README.md`, `docs/master-plan.md`,
  `docs/handoff.md`, and actual repo contents

## Healthy

- Existing public skills all have YAML frontmatter with `name` and
  `description`.
- Every shipped `adapter.example.yaml` parsed successfully with the local
  stdlib-based YAML loader.
- Every committed helper script under `skills/public/*/scripts/*.py` compiled.
- Existing adapter resolvers returned valid JSON and usable inferred defaults.
- `profiles/constitutional.json` validates against the current Draft 7 schema.
- `scripts/validate-skills.py` now validates public skill package shape and
  YAML-safe frontmatter.
- `scripts/validate-profiles.py` now validates shipped profile instances against
  actual repo artifacts.
- `scripts/validate-adapters.py` now validates resolver output shape and artifact
  naming.
- `scripts/check-doc-links.py` now catches broken local links and foreign
  absolute workspace paths.
- `ruff` and `pytest` now run successfully against the repo-owned Python helper
  layer.
- `markdownlint-cli2` and `secretlint` now run as repo-local dependencies.
- shell and external-link checks now have dedicated wrappers and degrade
  honestly when `shellcheck` or `lychee` are unavailable.
- `scripts/run-quality.sh` now provides one canonical repo-owned quality
  entrypoint.
- adapter bootstrap helpers now share repo-level utilities instead of shipping
  per-skill YAML loader copies.
- `quality` now explicitly treats skill packages and helper drift as a quality
  surface, not only code/tests/security in the narrow sense.
- repo-owned smoke scenarios now exist under `evals/`, with
  `scripts/run-evals.py` covering package validation, profile validation, doc
  link validity, adapter bootstrap, checked-in quality adapter resolution,
  handoff-style absolute-link portability, and representative `find-skills`
  discovery behavior.
- `profiles/engineering-quality.json` now provides an explicit quality overlay
  profile instead of leaving that taxonomy slot empty.
- `.agents/quality-adapter.yaml` is now checked in with the canonical
  `./scripts/run-quality.sh` gate command and repo concept paths.
- `sync-support` now has a stable v1 recommendation of `reference`, and actual
  generated reference artifacts exist for `agent-browser` and `crill` under
  `skills/support/generated/`.
- control-plane locks now have one schema-backed per-tool shape with `support`,
  `doctor`, and `update` sections instead of each command overwriting a
  different ad-hoc payload.
- `profiles/meta-builder.json` now fills the remaining documented profile slot
  for maintainer-facing authoring/discovery/quality work.
- `scripts/check-skill-contracts.py` now gives the repo a deterministic
  representative intent gate for `handoff`, `gather`, `create-skill`, and
  `spec`, and `run-evals.py` includes that scenario in the smoke layer.
- `packaging/charness.json` and `scripts/validate-packaging.py` now give the
  repo a shared packaging contract for Claude/Codex host exports before any
  generated plugin tree exists.
- `scripts/export-plugin.py` now proves that the shared packaging contract can
  materialize temporary Claude/Codex layouts without checking generated plugin
  trees into the repo.
- `handoff` and `gather` now have scenario-level bootstrap checks rather than
  only static contract-marker coverage.
- profile validation metadata now stays synchronized with the eval registry
  instead of allowing arbitrary `smoke_scenarios` strings to drift silently.
- `doctor` now detects broken support-sync drift when a previously materialized
  generated wrapper or reference artifact disappears.
- `validate-skills.py` now guards the actual `References` contract instead of
  only checking that mentioned paths happen to exist.
- profile and packaging validators now run JSON Schema validation before custom
  cross-artifact checks, which closes remaining shape-drift gaps.
- The top-level repo shape matches the documented skeleton in `README.md`.

## Weak

- `spec` still exposes explicit user-facing modes while the current
  `create-skill` authoring contract says to avoid modes/options unless they are
  truly necessary and unsafe to infer.
- `shellcheck` and `lychee` still depend on optional local binaries, so shell
  and external-link posture is honest but not fully enforced everywhere.

## Missing

- no immediate missing gate surfaced in this pass beyond the deferred items

## Deferred

- actual human review decisions for the `HITL recommended` tier; a durable
  queue now exists at `skill-outputs/hitl/hitl.md`
- scenario-based evaluator paths for the `evaluator-required` tier once
  `cautilus` exposes a real upstream contract
- collaboration-layer tightening beyond the current representative `announcement`
  and `hitl` policy surface
- broader representative intent checks for `create-skill` and `spec` beyond the
  current contract-marker baseline
- generated Claude/Codex host layouts and drift checks beyond the current
  shared manifest validation
- richer published-plugin metadata and optional host-specific `commands/agents`
  generation beyond the current minimal export scope

## Findings

### 1. The repo now has a usable self-validation baseline, but deeper validation is intentionally split by tier

`docs/public-skill-validation.md` fixes which skills need future evaluator
coverage and which ones remain human-review-first. That makes the remaining
validation gap narrower and more honest: the missing piece is no longer a vague
"more evals" bucket, but specifically `cautilus`-backed scenarios for the
`evaluator-required` set plus real human review for the `HITL recommended`
set.

Evidence:

- `docs/public-skill-validation.md`
- `scripts/run-evals.py`
- `skill-outputs/hitl/hitl.md`

### 2. Skill quality and helper drift now need to stay under deterministic ownership

This repo now has repo-owned validators for skill packages and a fail-closed
duplicate gate for substantive helper scripts. That is the right direction, but
the important policy point is broader: skill package quality should keep being
promoted into validators and shared helpers rather than drifting back into
copy-paste local wrappers.

Evidence:

- `scripts/validate-skills.py`
- `scripts/check-duplicates.py`
- `scripts/adapter_lib.py`
- `scripts/adapter_init_lib.py`
- `skills/public/quality/references/skill-quality.md`

### 3. `spec` mode drift has been reduced, but the lighter contract-shaping surface still needs follow-through review

The public `spec` body no longer exposes a named mode menu. That resolves the
most obvious conflict with `create-skill`'s option-minimalism rule. The
remaining question is whether the lighter heuristic wording is enough in
practice, or whether more of the old branching logic should move into
references and examples.

Evidence:

- `skills/public/create-skill/SKILL.md`
- `skills/public/spec/SKILL.md`
- `skills/public/spec/references/contract-modes.md`

### 4. Host packaging now has a single canonical contract, but export materialization is still the next boundary

The repo now has a shared packaging manifest and validator that pin the neutral
bundle inputs plus the required Claude/Codex manifest paths. That closes the
policy gap which mattered most before generation work starts. The next step is
not another doc pass, but an export path that materializes plugin manifests and
repo-marketplace fixtures from this shared source.

Evidence:

- `packaging/charness.json`
- `packaging/plugin.schema.json`
- `scripts/validate-packaging.py`
- `docs/host-packaging.md`

### 5. The first export path exists, so the remaining packaging work is now about breadth rather than basic feasibility

`scripts/export-plugin.py` now materializes both Claude and Codex layouts from
the shared manifest, including a Codex repo-marketplace file. That closes the
basic feasibility question. The remaining packaging work is about how much
published metadata and host-specific surface area should be generated, not
whether one neutral source can drive both hosts.

Evidence:

- `scripts/export-plugin.py`
- `scripts/run-evals.py`
- `docs/host-packaging.md`

### 6. Representative skill validation has started moving from text markers to workflow smoke

`handoff` and `gather` now prove their adapter bootstrap path in `run-evals.py`
by creating clean temp repos, initializing adapters, and resolving the durable
artifact location. That is a better maintenance boundary than treating these
skills as prose-only contracts. The remaining gap in this area is now mostly
`create-skill` and `spec`.

Evidence:

- `skills/public/handoff/scripts/init_adapter.py`
- `skills/public/handoff/scripts/resolve_adapter.py`
- `skills/public/gather/scripts/init_adapter.py`
- `skills/public/gather/scripts/resolve_adapter.py`
- `scripts/run-evals.py`

### 7. Profile metadata now has a tighter contract with actual repo-owned validation surfaces

Profile files can now declare `smoke_scenarios` only when those scenario ids
actually exist in the eval registry, and `required_integrations` now has the
same artifact-integrity bar as bundle integrations. This matters because the
profile layer is starting to carry real operational meaning, not just labels.

Evidence:

- `scripts/eval_registry.py`
- `scripts/validate-profiles.py`
- `profiles/meta-builder.json`
- `profiles/engineering-quality.json`

### 8. Control-plane doctor now distinguishes broken support sync from first-run state

`doctor` now checks previously recorded `materialized_paths` from the support
lock and reports `support-missing` if those generated artifacts disappear. That
closes a real gap in the documented control-plane contract without making
first-run repos fail only because they have not run `sync-support` yet.

Evidence:

- `scripts/control_plane_lib.py`
- `scripts/doctor.py`
- `tests/test_control_plane.py`
- `docs/control-plane.md`

### 9. Public skill bodies now have a stronger structural guard against reference drift

`validate-skills.py` now requires every public skill to keep a real
`## References` section, list at least one reference artifact, and keep all
checked-in reference files represented there. That moves more of the
`create-skill` contract into deterministic enforcement instead of relying on
maintainer memory.

Evidence:

- `scripts/validate-skills.py`
- `tests/test_quality_gates.py`
- `skills/public/create-skill/SKILL.md`

### 10. Schema files now participate in actual validator execution instead of only documenting intent

`validate-profiles.py` and `validate-packaging.py` now use the checked-in JSON
Schemas before running repo-specific integrity checks. That means
`additionalProperties`, enum drift, and other shape regressions fail at the
validator boundary rather than relying on human review or indirect tests.

Evidence:

- `profiles/profile.schema.json`
- `packaging/plugin.schema.json`
- `scripts/validate-profiles.py`
- `scripts/validate-packaging.py`

## Commands Run

```bash
find . -maxdepth 2 \( -name 'package.json' -o -name 'pyproject.toml' -o -name 'requirements*.txt' -o -name 'Makefile' -o -name '.github' -o -name 'justfile' -o -name 'pytest.ini' -o -name 'tox.ini' -o -name 'mypy.ini' -o -name '.pre-commit-config.yaml' -o -name 'ruff.toml' \) | sort
python3 skills/public/debug/scripts/resolve_adapter.py --repo-root .
python3 skills/public/gather/scripts/resolve_adapter.py --repo-root .
python3 skills/public/handoff/scripts/resolve_adapter.py --repo-root .
python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .
python3 skills/public/retro/scripts/resolve_adapter.py --repo-root .
python3 scripts/validate-adapters.py
python3 -m py_compile skills/public/*/scripts/*.py
ruff check scripts tests skills/public/*/scripts
pytest -q
./scripts/run-quality.sh
python3 scripts/validate-skills.py
python3 scripts/validate-profiles.py
python3 - <<'PY'
import json
from pathlib import Path
import jsonschema
schema = json.loads(Path('profiles/profile.schema.json').read_text())
instance = json.loads(Path('profiles/constitutional.json').read_text())
jsonschema.Draft7Validator(schema).validate(instance)
print('ok')
PY
python3 scripts/check-doc-links.py
python3 scripts/check-duplicates.py --fail-on-match
python3 scripts/run-evals.py
./scripts/check-markdown.sh
./scripts/check-secrets.sh
./scripts/check-shell.sh
./scripts/check-links-external.sh
```

## Recommended Next Gates

1. Keep `./scripts/run-quality.sh` as the canonical local quality entrypoint and
   wire it into future collaboration-layer or CI flows.

2. Decide whether `shellcheck` and `lychee` should become required local setup
   for `charness`, or remain optional-but-recommended quality escalations.
