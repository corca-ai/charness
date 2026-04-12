---
name: quality
description: "Use when the goal is to understand and improve the repo's current quality bar. Detect existing gates, run the available ones, inspect concept integrity, test confidence, and security posture, then propose concrete next gates instead of only complaining about what is missing."
---

# Quality

Use this when the task is overall quality posture, not only one narrow bug or
one isolated test.

`quality` is one public concept. It absorbs concept integrity review, test
confidence improvement, security and supply-chain posture review, skill
package and maintenance drift review, and documentation drift review.

The job is to understand the repo's current quality surface, run the
meaningful gates that already exist, and propose the missing ones concretely.

When the next quality move is repo-local, deterministic, and low-risk, prefer
implementing that gate in the same turn. Stay review-only when the user asks
or the tradeoff is genuinely product-defining.

Deterministic gates should define pass/fail authority wherever possible. If a
quality concern can be enforced by a linter, validator, test, hook, or script,
`quality` should prefer promoting it into that gate instead of leaving it as
repeated prose advice.

Maintainer-local enforcement counts when the repo depends on it. When the
repo has an obvious final stop-before-finish gate with no checked-in hook,
repo-owned hook installer, or documented no-hook policy, `quality` must name
that as a missing enforcement gap rather than treating the passing command as
healthy posture. See `references/maintainer-local-enforcement.md`.

`quality` and concept review are adjacent. Use `quality` for repo posture,
drift, duplicated surfaces, weak gates, and the next concrete validation move.
Use concept review when boundaries, ownership, or source-of-truth design stay unresolved without duplicate text or an obvious gate. Use named-expert lenses only when they sharpen the next gate choice. See `references/quality-lenses.md`.

## Bootstrap

Resolve the adapter first, then inspect the current quality surface.

Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

Keep `quality.md` short and current; move older review detail into sibling
`history/*.md` archives when today's posture starts getting buried.

If the adapter is missing and the repo would benefit from explicit command
groups, scaffold one:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root . --preset-id portable-defaults
```

```bash
# Required Tools: rg
# Missing-binary protocol: create-skill/references/binary-preflight.md
# 1. current quality artifact and adjacent contracts
sed -n '1,220p' <resolved-quality-artifact> 2>/dev/null || true
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
rg --files docs skills

# 2. repo signals and maintainer-local enforcement surface
rg -n "eslint|ruff|mypy|pyright|tsc|pytest|vitest|jest|coverage|deptry|knip|audit|sast|owasp|threat|architecture|concept|markdownlint|secretlint|shellcheck|lychee|gitleaks|trufflehog|pre-push|prepush|githook|husky|simple-git-hooks|lefthook|core\.hooksPath" .
git config --get core.hooksPath || true
find .git/hooks -maxdepth 1 -type f 2>/dev/null | sort

# 3. current repo state
git status --short
```

If the adapter is missing, use inferred defaults and continue; scaffold one
when the repo already has stable gate commands worth recording.

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
   - maintainer-local enforcement for the final stop-before-finish gate: a
     checked-in hook, installer, or explicit no-hook policy
   - obvious blind spots where the repo has no gate at all
3. Run the meaningful gates that already exist.
   - prefer repo-native commands over hypothetical recommendations
   - keep the run bounded to the current scope when the task is not repo-wide
   - if the repo has executable-spec overlap or cost guards, run those before
     proposing more spec coverage
   - for timing/logs/retention signals, see `references/operability-signals.md`
   - surface the current runtime hot spots from available timing or CI signals
4. Inspect four quality lenses.
   - `concept`: does the repo still match its claimed architecture and
     ownership model
   - `behavior`: do tests, evals, and checks say something falsifiable about
     real behavior, and does the repo-owned test code stay maintainable
   - `security`: are there meaningful code, secret, or supply-chain risks
   - `operability`: are setup, CI, and maintenance surfaces honest enough to
     sustain the quality bar
   - when the repo authors skills, include skill package quality, portable
     bootstrap seams, and shared-helper drift in these lenses
   - make `behavior` explicit about whether coverage is standing-gated,
     informally sampled, or absent
   - make evaluator depth explicit: smoke only, maintained evaluator-backed,
     or still smoke plus HITL
   - for docs-as-operating-surface, flag duplicated guidance, conflicting
     copies, source-of-truth drift, and bare repo-doc links in prose
   - for repo-owned source gates, prefer tracked or explicitly unignored files
     over whole-worktree scans; inspect gitignored runtime state only when the check explicitly owns machine-local artifacts
   - treat external URL health separately from repo-local markdown-link
     discipline
   - for executable specs, inspect boundary focus, lower-level duplication, and shell-wrapper use where direct adapters would be clearer and faster
   - if one test module has accumulated many unrelated seams, prefer splitting it by validator or behavior seam before it becomes normal to skim only partially
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
   - when the problem is automatable, prefer a deterministic gate over prose
   - when the automatable move is already clear and repo-owned, implement it in
     the same turn unless the user asked to stay review-only
   - if executable specs are slow or overlapping, delete duplicates, move
     detail into unit-level checks, or add a direct adapter before widening
     the spec bar
8. End with a quality posture summary.
   - what was actually run
   - what runtime or diagnostic signals were captured
   - which runtime hot spots dominate the current bar
   - whether coverage is standing-gated, indirect, or absent
   - whether evaluator-backed depth exists, or whether the deeper bar is still smoke plus HITL
   - what the current bar proves
   - what it still does not prove
   - the next best gate or cleanup to add

- `Scope`, `Current Gates`, `Runtime Signals`, `Coverage and Eval Depth`
- `Maintainer-Local Enforcement`, `Enforcement Triage`
- `Healthy`, `Weak`, `Missing`, `Deferred`, `Commands Run`, `Recommended Next Gates`

- Do not reduce quality to one aggregate score.
- Do not recommend gates the repo cannot realistically run without saying why.
- Do not confuse gate presence with gate usefulness.
- Do not ignore runtime drift just because a gate still passes functionally.
- Do not wait for operator follow-up before stating current runtime hot spots,
  coverage-gate presence or absence, and evaluator-depth status when the repo
  signals are available.
- Do not treat slow or broad executable specs as automatically strong quality
  when they mostly duplicate cheaper deterministic coverage.
- Do not recommend verbose or permanent logs without naming who will read them and how they stay bounded.
- Do not leave an automatable quality rule as prose-only guidance when a linter, validator, test, hook, or script could own it.
- If you stop short of an obvious repo-owned deterministic gate, name that as
  an unresolved enforcement gap explicitly.
- Do not treat a passing final local gate as sufficient posture when clones
  have no repo-owned way to run it before push and no documented no-hook waiver.
- Do not propose generic "add more tests" or "improve security" without naming
  the actual seam, the next concrete setup, or whether the test surface now
  needs a maintainability gate.
- If a gate already exists, prefer tightening or reusing it before adding a new
  parallel tool.
- If a stronger check would require an external tool, support skill, or permission, say so explicitly.
- If a missing binary or local setup step would materially improve confidence, recommend installing it with the reason and exact command or package family.
- Do not let whole-worktree scans fail on gitignored runtime artifacts unless the gate explicitly exists to validate that machine-local state.
- Keep repo-local markdown-link discipline separate from external URL health when the repo needs both.
- Do not pretend a conceptual boundary problem is solved just because duplicate text was linted away; semantic boundary questions still need concept review.
- If the repo is shipping a CLI or bootstrap command surface, inspect whether
  install/update/doctor/reset behavior follows `create-cli`-level quality
  expectations instead of treating the entrypoint as ordinary helper glue.

## References

- `references/adapter-contract.md`
- `references/maintainer-local-enforcement.md`
- `references/quality-lenses.md`
- `references/skill-quality.md`
- `references/proposal-flow.md`
- `references/gate-classification.md`
- `references/automation-promotion.md`
- `references/operability-signals.md`
- `references/executable-spec-economics.md`
- `references/sample-presets.md`
- `references/security-overview.md`
- `references/security-npm.md`
- `references/security-pnpm.md`
- `references/security-uv.md`
