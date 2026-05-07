# Bootstrap Escalations

Keep the public `SKILL.md` bootstrap on the frequent path. Use these paths only
when the current quality question or repo state needs them.

## Tool Recommendations

When stronger local proof depends on a missing validation or runtime tool, reuse
the structured recommendation payload instead of inventing prose-only install
advice:

```bash
python3 "$SKILL_DIR/scripts/list_tool_recommendations.py" --repo-root .
python3 "$SKILL_DIR/scripts/list_tool_recommendations.py" --repo-root . --recommendation-role runtime --next-skill-id quality
```

If an existing gate is blocked only by a missing validation binary, treat that
as setup work. Name the missing binary and verify command; install only when
the user already asked for installation or local closeout, then rerun the
blocked gate.

## Evaluator-Backed Behavior Proof

For evaluator-backed behavior closeout, prompt regression, baseline compare, or
operator reading tests, route through `quality` before downgrading to HITL or
manual review. Generic review, closeout, or "run quality" wording does not
require an evaluator. Start with deterministic gates and escalate only when
they cannot answer the behavior question.

If the repo-owned evaluator adapter is disabled, do not run the evaluator.
Record the disabled policy and let deterministic gates own closeout until the
adapter is re-enabled.

## Markdown Preview

When reader-facing Markdown needs rendered readability proof instead of
source-only review, bootstrap or execute the repo-local Markdown preview seam:

```bash
python3 "$SKILL_DIR/scripts/bootstrap_markdown_preview.py" --repo-root .
python3 "$SKILL_DIR/scripts/bootstrap_markdown_preview.py" --repo-root . --execute
```

Ordinary Markdown uses the markdown preview seam. Executable `*.spec.md` review
should use the rendered Specdown report when that is the authoritative
human-facing surface.

## Artifact Write Path

Keep `latest.md` short and current; move older review detail into sibling
`history/*.md` archives when today's posture starts getting buried.

Before editing the artifact, run:

```bash
python3 "$SKILL_DIR/scripts/resolve_quality_artifact.py" --repo-root . --intent current
```

Edit the returned `write_artifact_path`, not `latest.md` by habit. The prior
quality artifact is history, not the authoritative universe.

## Initial Signal Sweep

When a fresh repo-wide review needs a broad signal sweep, prefer this current
inventory after adapter resolution:

```bash
rg --files docs skills
rg -n "eslint|ruff|mypy|pyright|tsc|pytest|vitest|jest|coverage|deptry|knip|audit|sast|owasp|threat|architecture|concept|markdownlint|secretlint|shellcheck|lychee|gitleaks|trufflehog|pre-push|prepush|githook|husky|simple-git-hooks|lefthook|core\.hooksPath|actions/checkout|actions/setup-node|actions/setup-go|actions/setup-python|actions/cache|actions/github-script|check-github-actions" .
git config --get core.hooksPath || true
find .git/hooks -maxdepth 1 -type f 2>/dev/null | sort
```
