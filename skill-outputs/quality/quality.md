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
- Python syntax compilation for every committed helper script under
  `skills/public/*/scripts/*.py`
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
- The top-level repo shape matches the documented skeleton in `README.md`.

## Weak

- Skill helper scripts are highly duplicated. `_stdlib_yaml.py` is effectively
  copied per skill, and the adapter resolver implementations are near-clones
  across `debug`, `gather`, `handoff`, and `quality`.
- `spec` still exposes explicit user-facing modes while the current
  `create-skill` authoring contract says to avoid modes/options unless they are
  truly necessary and unsafe to infer.
- `docs/handoff.md` still carries Ceal-specific branding and absolute local file
  references to other repos, which makes the committed handoff artifact less
  portable than the rest of the repo.

## Missing

- A duplicate-check gate for helper scripts
- A doc/link portability check for committed markdown
- Repo-owned smoke scenarios under `evals/` or `workbench` fixtures
- A checked-in quality adapter for this repo once stable commands exist

## Deferred

- Support integration validator once actual tool manifest instances land
- Full `workbench` + `hitl` validation after more public skills exist
- Collaboration-layer quality gates for `announcement` and `hitl`

## Findings

### 1. The repo promises self-validation deliverables but still ships only a partial set

`docs/master-plan.md` says Workstream 4 should provide a taxonomy validator,
support integration validator, bootstrap scenarios, profile/preset scenarios,
and intent-regression checks. The actual top-level `scripts/` and `evals/`
surface is no longer empty, but it still lacks repo-owned smoke scenarios,
duplicate checks, and integration validators.

Evidence:

- `docs/master-plan.md` lines 119-131
- current `scripts/` contents
- `evals/.gitkeep`

### 2. Committed handoff artifact was still partially Ceal-shaped before this pass

The committed handoff file had Ceal branding and foreign local filesystem
references. Those paths work only on one machine and should be rejected by a
repo-owned doc link check.

Evidence:

- previous Session 8 handoff state
- `scripts/check-doc-links.py`

### 3. Adapter helper implementation is drifting toward copy-paste maintenance

The minimal YAML loader is duplicated per skill, and the adapter resolvers for
`debug`, `gather`, `handoff`, and `quality` are all very high-similarity
variants. This is now a real duplicate hotspot and should be covered by a
repo-specific duplicate check before more skills copy the pattern again.

Evidence:

- `skills/public/debug/scripts/_stdlib_yaml.py` lines 1-67
- `skills/public/gather/scripts/_stdlib_yaml.py` lines 1-67
- `skills/public/quality/scripts/_stdlib_yaml.py` lines 1-67
- `skills/public/debug/scripts/resolve_adapter.py` lines 17-135
- `skills/public/gather/scripts/resolve_adapter.py` lines 17-135
- `skills/public/quality/scripts/resolve_adapter.py` lines 17-156

### 4. `spec` still violates the repo's newer option-minimalism rule

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
python3 -m py_compile skills/public/*/scripts/*.py
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
```

## Recommended Next Gates

1. `python3 scripts/validate-adapters.py`
   Run each committed `resolve_adapter.py --repo-root .`, assert `valid=true`,
   and verify the expected durable artifact filename and canonical search order.

2. `python3 scripts/check-duplicates.py`
   Detect very-high-similarity helper scripts under `skills/public/*/scripts/`
   so adapter boilerplate drift becomes visible before it spreads further.

3. `python3 -m py_compile skills/public/*/scripts/*.py`
   Keep this as a cheap syntax smoke test for the current Python helper layer.

4. Add repo-owned smoke scenarios under `evals/`
   At minimum:
   - one skill package shape scenario
   - one profile/schema scenario
   - one adapter resolution scenario
   - one handoff portability scenario
