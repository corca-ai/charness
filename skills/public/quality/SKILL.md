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
- skill package and maintenance drift review
- documentation drift and duplication review

The job is not to invent one universal checklist. The job is to understand the
repo's current quality surface, run the meaningful gates that already exist,
and propose the missing ones concretely.

When the next quality move is repo-local, deterministic, and low-risk, `quality`
should prefer implementing that gate in the same turn instead of stopping at a
recommendation. Review-only output is appropriate when the user asked for it,
when the tradeoff is genuinely product-defining, or when the gate cannot be
owned honestly by a repo-local script, test, hook, or config change.

Deterministic gates should define pass/fail authority wherever possible. If a
quality concern can be enforced by a linter, validator, test, hook, or script,
`quality` should prefer promoting it into that gate instead of leaving it as
repeated prose advice.

Maintainer-local setup counts when the repo depends on it. If a checked-in hook
or similar repo-owned developer control exists, `quality` should prefer a
deterministic validator that proves the current clone actually uses it.

`quality` and concept review are adjacent but not identical. Use `quality` for
repo posture, enforceable drift, duplicated surfaces, weak gates, and the next
concrete validation move. Use concept-review-style reasoning when the main
question is whether concepts, boundaries, ownership, or source-of-truth design
are still the right ones even without near-duplicate text or an obvious gate.

## Bootstrap

Resolve the adapter first, then inspect the current quality surface.

Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

By default, `quality` writes its durable artifact to
`skill-outputs/quality/quality.md`. Repos can override the directory with
`.agents/quality-adapter.yaml`.

Keep the current artifact short and current. When older review detail starts to
bury today's posture, move that detail into sibling `history/*.md` archives and
leave `quality.md` as the current snapshot plus links back to history.

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
rg -n "eslint|ruff|mypy|pyright|tsc|pytest|vitest|jest|coverage|deptry|knip|audit|sast|owasp|threat|architecture|concept|markdownlint|secretlint|shellcheck|lychee|gitleaks|trufflehog" .

# 3. current repo state
git status --short
```

If the adapter is missing, use inferred defaults and continue. The purpose of
`quality` is to give first-use value before a repo has a perfect quality
setup. Scaffold the adapter when the repo already has stable gate commands
worth recording.

## Workflow

1. Restate the current quality question.
   - what the user wants checked or improved
   - whether the scope is repo-wide, one seam, or one proposed change
2. Detect the current gate surface.
   - local executable gates already present
   - current concept or architecture sources of truth
   - security and supply-chain signals already configured
   - executable-spec frameworks, adapter depth, and overlap controls when the
     repo keeps acceptance checks in specs
   - obvious blind spots where the repo has no gate at all
3. Run the meaningful gates that already exist.
   - prefer repo-native commands over hypothetical recommendations
   - keep the run bounded to the current scope when the task is not repo-wide
   - if the repo has executable-spec overlap or cost guards, run those before
     proposing more spec coverage
   - for timing, logs, and retention signals, use
     `references/operability-signals.md`
4. Inspect four quality lenses.
   - `concept`: does the repo still match its claimed architecture and
     ownership model
   - `behavior`: do tests and checks say something falsifiable about real
     behavior
   - `security`: are there meaningful code, secret, or supply-chain risks
   - `operability`: are setup, CI, and maintenance surfaces honest enough to
     sustain the quality bar
   - when the repo authors skills, include skill package quality, portable
     bootstrap seams, and shared-helper drift in these lenses
   - when docs are part of the operating surface, include duplicated guidance,
     conflicting copies, source-of-truth drift, and clickable repo-doc links in
     prose
   - treat external URL health separately from repo-local markdown-link
     discipline
   - when executable specs exist, inspect whether they stay boundary-focused,
     duplicate lower-level tests, or rely on shell wrappers where direct
     adapters would be clearer and faster
5. Classify each issue by enforcement tier first.
   - `AUTO_EXISTING`: already enforced by a meaningful deterministic gate
   - `AUTO_CANDIDATE`: should be promoted into a linter, validator, test, hook,
     or script
   - `NON_AUTOMATABLE`: still requires judgment, tradeoff analysis, or human
     review
6. Classify gaps.
   - `healthy`: already enforced and useful
   - `weak`: present but low-signal or easy to game
   - `missing`: should exist but does not
   - `defer`: useful later, but not the next highest-leverage gate
7. Propose the next quality moves concretely.
   - for missing or weak gates, name the exact setup or command family to add
   - prefer the smallest gate that materially improves confidence
   - do not force one stack's tooling when the repo does not use that stack
   - when the problem is automatable, prefer a deterministic gate proposal over
     more prose
   - when the automatable move is already clear and repo-owned, implement it in
     the same turn unless the user asked to stay review-only
   - when executable specs are slow or overlapping, prefer deleting duplicate
     coverage, moving detail into unit/source-level checks, or introducing a
     direct adapter before widening the standing spec bar
8. End with a quality posture summary.
   - what was actually run
   - what runtime or diagnostic signals were captured
   - what the current bar proves
   - what it still does not prove
   - the next best gate or cleanup to add

## Output Shape

The result should usually include:

- `Scope`
- `Current Gates`
- `Runtime Signals`
- `Enforcement Triage`
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
- Do not ignore runtime drift just because a gate still passes functionally.
- Do not treat slow or broad executable specs as automatically strong quality when they mostly duplicate cheaper deterministic coverage.
- Do not recommend verbose or permanent logs without naming who will read them and how they stay bounded.
- Do not leave an automatable quality rule as prose-only guidance when a
  linter, validator, test, hook, or script could own it.
- If you stop short of an obvious repo-owned deterministic gate, name that as
  an unresolved enforcement gap explicitly.
- Do not propose generic "add more tests" or "improve security" without naming the actual seam and the next concrete setup.
- If a gate already exists, prefer tightening or reusing it before adding a new parallel tool.
- If a stronger check would require an external tool, support skill, or permission, say so explicitly.
- If a missing binary or local setup step would materially improve confidence, recommend installing it with the reason and exact command or package family.
- Keep repo-local markdown-link discipline separate from external URL health when the repo needs both.
- Do not pretend a conceptual boundary problem is solved just because duplicate text was linted away; semantic boundary questions still need concept review.

## References

- `references/adapter-contract.md`
- `references/quality-lenses.md`
- `references/skill-quality.md`
- `references/proposal-flow.md`
- `references/gate-classification.md`
- `references/automation-promotion.md`
- `references/operability-signals.md`
- `references/executable-spec-economics.md`
- `references/sample-presets.md`
