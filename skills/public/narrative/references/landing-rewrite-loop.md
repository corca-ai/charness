# Landing Rewrite Loop

Use this loop when `narrative` is rewriting a first-touch surface such as a
README, project overview, homepage copy, or durable product story.

## Audience Context

State the primary reader before writing. Examples:

- internal promotion shared as a repo link
- OSS landing page
- maintainer handoff
- contributor onboarding

This is not audience-specific delivery copy. If the user wants channel, tone,
language, or campaign adaptation, finish durable alignment first and hand off to
`announcement`.

## Comparables

Run a bounded comparables pass before editing when the surface is externally
read or high-leverage. Partition concerns instead of asking for generic README
advice.

Each return should use this shape:

- 3 patterns to steal, each tied to a source
- 1 pattern to avoid
- 2 immediate apply suggestions

Do not accept broad summaries as the artifact. The value is the reusable
pattern and why it applies.

## Tension And Decision Logs

Before editing, list conflicting research or source-truth tensions, resolve
each with reasoning, and keep those decisions stable during the rewrite.

Persist decisions in two places when the work is substantial:

- current narrative artifact for session pickup
- checked-in research or decision note when future rewrites would otherwise
  rediscover the same comparables

## Compression Metric

Record before/after line counts for the main prose surface, excluding code
fences and tables when practical.

- greater than 3x line drop plus structural section changes: likely real
  restructure
- less than 10 percent line delta on a claimed restructure: ask whether this
  was only a repackage

## Rendered Preview

When the target is a landing page, README, durable spec prose, or another
first-touch Markdown surface, inspect rendered output before calling the
rewrite done.

- use the repo-local markdown preview seam when it exists
- if the preferred renderer is missing, surface the exact install/verify path
  before treating degraded artifacts as sufficient:
  `python3 skills/public/narrative/scripts/list_tool_recommendations.py --repo-root .`
- if no preview config exists yet, bootstrap one and leave the exact command
  plus artifact path instead of pretending raw source review was enough
- keep width-specific preview artifacts so the next session can inspect the
  rendered shape directly

## Claim Audit

Before stopping, map landing claims to evidence:

- claim
- durable source
- human acceptance check
- executable spec or test when available
- gap and next artifact when not covered

The loop is narrative -> operator acceptance -> executable spec -> implementation
when a new claim is not yet machine-verifiable. Acceptance and executable specs
are separate artifacts; do not collapse them.

## Self-Premortem

Run a short fresh-eye premortem before finalizing:

- Do any two sections assert contradictory requirements?
- For each claim, is scope fixed while implementation remains open where it
  should?
- For each example, fixture, or path, is there one canonical source of truth?
