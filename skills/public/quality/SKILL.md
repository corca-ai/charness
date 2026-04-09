---
name: quality
description: "Use when the goal is to understand and improve the repo's current quality bar. Detect existing gates, run the available ones, inspect concept integrity, test confidence, and security posture, then propose concrete next gates instead of only complaining about what is missing."
---

# Quality

Use this when the task is overall quality posture, not only one narrow bug or
one isolated test.

`quality` is one public concept. It absorbs:

- concept integrity review
- test confidence improvement
- security and supply-chain posture review

The job is not to invent one universal checklist. The job is to understand the
repo's current quality surface, run the meaningful gates that already exist,
and propose the missing ones concretely.

## Bootstrap

Resolve the adapter first, then inspect the current quality surface.

Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

By default, `quality` writes its durable artifact to
`skill-outputs/quality/quality.md`. Repos can override the directory with
`.agents/quality-adapter.yaml`.

If the adapter is missing and the repo would benefit from explicit command
groups, scaffold one:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root . --preset-id portable-defaults
```

```bash
# 1. current quality artifact and adjacent contracts
sed -n '1,220p' <resolved-quality-artifact> 2>/dev/null || true
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
rg --files docs skills

# 2. repo signals for existing gates and contracts
rg -n "eslint|ruff|mypy|pyright|tsc|pytest|vitest|jest|coverage|deptry|knip|audit|sast|owasp|threat|architecture|concept" .

# 3. current repo state
git status --short
```

If the adapter is missing, use inferred defaults and continue. The purpose of
`quality` is to give first-use value before a repo has a perfect quality setup.
Scaffold the adapter when the repo already has stable gate commands worth
recording.

## Workflow

1. Restate the current quality question.
   - what the user wants checked or improved
   - whether the scope is repo-wide, one seam, or one proposed change
2. Detect the current gate surface.
   - local executable gates already present
   - current concept or architecture sources of truth
   - security and supply-chain signals already configured
   - obvious blind spots where the repo has no gate at all
3. Run the meaningful gates that already exist.
   - prefer repo-native commands over hypothetical recommendations
   - keep the run bounded to the current scope when the task is not repo-wide
4. Inspect four quality lenses.
   - `concept`: does the repo still match its claimed architecture and
     ownership model
   - `behavior`: do tests and checks say something falsifiable about real
     behavior
   - `security`: are there meaningful code, secret, or supply-chain risks
   - `operability`: are setup, CI, and maintenance surfaces honest enough to
     sustain the quality bar
5. Classify gaps.
   - `healthy`: already enforced and useful
   - `weak`: present but low-signal or easy to game
   - `missing`: should exist but does not
   - `defer`: useful later, but not the next highest-leverage gate
6. Propose the next quality moves concretely.
   - for missing or weak gates, name the exact setup or command family to add
   - prefer the smallest gate that materially improves confidence
   - do not force one stack's tooling when the repo does not use that stack
7. End with a quality posture summary.
   - what was actually run
   - what the current bar proves
   - what it still does not prove
   - the next best gate or cleanup to add

## Output Shape

The result should usually include:

- `Scope`
- `Current Gates`
- `Healthy`
- `Weak`
- `Missing`
- `Deferred`
- `Commands Run`
- `Recommended Next Gates`

## Guardrails

- Do not reduce quality to one aggregate score.
- Do not recommend gates the repo cannot realistically run without saying why.
- Do not confuse gate presence with gate usefulness.
- Do not propose generic "add more tests" or "improve security" without naming
  the actual seam and the next concrete setup.
- If a gate already exists, prefer tightening or reusing it before adding a new
  parallel tool.
- If a stronger check would require an external tool, support skill, or
  permission, say so explicitly.

## References

- `references/adapter-contract.md`
- `references/quality-lenses.md`
- `references/proposal-flow.md`
- `references/gate-classification.md`
- `references/sample-presets.md`
