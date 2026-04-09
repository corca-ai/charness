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
  `scripts/validate-adapters.py`, and `scripts/check-doc-links.py`
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
- broader representative intent checks for `handoff`, `gather`,
  `create-skill`, and `spec` beyond the current contract-marker baseline

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

### 3. `spec` still violates the repo's newer option-minimalism rule

The authoring contract now says not to introduce user-facing modes/options
unless the behavior is meaningfully distinct and unsafe to infer. `spec` still
has an explicit `Mode Selection` section with three named modes. That may be
defensible, but it is now a concept drift that should be resolved explicitly
rather than left implicit.

Evidence:

- `skills/public/create-skill/SKILL.md` lines 79-83
- `skills/public/spec/SKILL.md` lines 39-53

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
