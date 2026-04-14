---
name: quality
description: "Use when the goal is to understand and improve the repo's current quality bar. Detect existing gates, run the available ones, inspect concept integrity, test confidence, and security posture, then propose concrete next gates instead of only complaining about what is missing."
---

# Quality

Use this when the task is overall quality posture, not only one narrow bug or
one isolated test.

`quality` is one public concept. It absorbs concept integrity review, test confidence improvement, security and supply-chain posture review, skill package and maintenance drift review, and documentation drift review.

The job is to understand the repo's current quality surface, run the meaningful gates that already exist, and propose the missing ones concretely.

`quality` may also install or refresh the repo-local quality posture when the next move is deterministic setup work instead of only review. Keep this inside the same public concept: review posture and bootstrap posture are different execution states of `quality`, not separate skills.

When the next quality move is repo-local, deterministic, and low-risk, prefer implementing that gate in the same turn. Stay review-only when the user asks or the tradeoff is genuinely product-defining.

Deterministic gates should define pass/fail authority wherever possible. If a quality concern can be enforced by a linter, validator, test, hook, or script, `quality` should prefer promoting it into that gate instead of leaving it as repeated prose advice.

Maintainer-local enforcement counts when the repo depends on it. When the repo has an obvious final stop-before-finish gate with no checked-in hook, repo-owned hook installer, or documented no-hook policy, `quality` must name that as a missing enforcement gap rather than treating the passing command as healthy posture. See `references/maintainer-local-enforcement.md`.

`quality` and concept review are adjacent. Use `quality` for repo posture, drift, duplicated surfaces, weak gates, and the next concrete validation move. Use concept review when boundaries, ownership, or source-of-truth design stay unresolved without duplicate text or an obvious gate. Use named-expert lenses only when they sharpen the next gate choice. See `references/quality-lenses.md`.

## Bootstrap

Resolve the adapter first, then inspect the current quality surface.

Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

If the repo already has repo-owned quality commands or needs a first-pass installed posture, bootstrap the adapter and capture deferred setup in a machine-readable report:

```bash
python3 "$SKILL_DIR/scripts/bootstrap_adapter.py" --repo-root .
```

When stronger local proof depends on a missing validation tool, reuse the shared recommendation/install payload instead of inventing prose-only install advice:

```bash
python3 "$SKILL_DIR/scripts/list_tool_recommendations.py" --repo-root .
```

Keep `quality.md` short and current; move older review detail into sibling `history/*.md` archives when today's posture starts getting buried.

If the adapter is missing and the repo only needs a blank scaffold instead of detected bootstrap, scaffold one directly:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root . --preset-id portable-defaults
```

The prior `quality.md` is history, not the authoritative universe. Re-derive the current source, spec, and gate surface before trusting what the last artifact happened to mention.

```bash
# Required Tools: rg
# Missing-binary protocol: create-skill/references/binary-preflight.md
# 1. fresh inventory before the prior artifact can anchor scope
rg --files .

# 2. current quality artifact and adjacent contracts
sed -n '1,220p' <resolved-quality-artifact> 2>/dev/null || true
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
rg --files docs skills

# 3. repo signals and maintainer-local enforcement surface
rg -n "eslint|ruff|mypy|pyright|tsc|pytest|vitest|jest|coverage|deptry|knip|audit|sast|owasp|threat|architecture|concept|markdownlint|secretlint|shellcheck|lychee|gitleaks|trufflehog|pre-push|prepush|githook|husky|simple-git-hooks|lefthook|core\.hooksPath|actions/checkout|actions/setup-node|actions/setup-go|actions/setup-python|actions/cache|actions/github-script|check-github-actions" .
git config --get core.hooksPath || true
find .git/hooks -maxdepth 1 -type f 2>/dev/null | sort

# 4. current repo state
git status --short
```

If the adapter is missing, use inferred defaults and continue; scaffold one when the repo already has stable gate commands worth recording. Prefer `bootstrap_adapter.py` when the adapter should record installed command groups, inferred concept paths, preset lineage, or deferred setup in one pass.

## Workflow

1. Restate the current quality question.
   - what the user wants checked or improved
   - whether the scope is repo-wide, one seam, or one proposed change
2. Detect the current gate surface.
   - independently enumerate the current source, spec, and gate inventory before letting the previous quality artifact define scope
   - local executable gates already present
   - current concept or architecture sources of truth
   - security and supply-chain signals already configured
   - if the repo ships an installable CLI, bootstrap command, or operator-facing command surface, inspect whether help, command discovery, binary health, install/readiness, and local discoverability are separated honestly
   - inspect README / INSTALL / operator docs for drift against install, update, doctor, reset, or uninstall behavior when those commands exist
   - executable-spec frameworks, adapter depth, and overlap controls when the repo keeps acceptance checks in specs
   - if the repo keeps standing coverage floors, tag seams within `coverage_fragile_margin_pp` as `FRAGILE` instead of burying near-miss risk in prose
   - for blind-spot prevention, apply `references/coverage-floor-policy.md`: adapter-owned `coverage_floor_policy`, real unfloored-file inventory, and `Covered by pytest:` reference validation when those notes exist
   - maintainer-local enforcement for the final stop-before-finish gate: a checked-in hook, installer, or explicit no-hook policy
   - obvious blind spots where the repo has no gate at all
   - whether the next move is review-only or a bounded bootstrap/install pass
3. Run the meaningful gates that already exist.
   - prefer repo-native commands over hypothetical recommendations
   - keep the run bounded to the current scope when the task is not repo-wide
   - if the repo has executable-spec overlap or cost guards, run those before proposing more spec coverage
   - for timing/logs/retention signals, workflow-runtime drift, and retention signals, see `references/operability-signals.md`
   - surface the current runtime hot spots from available timing or CI signals
4. Inspect four quality lenses.
   - `concept`: does the repo still match its claimed architecture and ownership model
   - `behavior`: do tests, evals, checks, and command-surface probes say something falsifiable about real behavior, and does the repo-owned test code stay maintainable
   - when the same confidence gap could be closed either by shrinking production branches/interfaces or by adding more tests, prefer the smaller production surface first if behavior and signal both improve
   - when executable specs exist, classify smoke vs behavior using the adapter's `specdown_smoke_patterns`, report the ratio, and flag pytest-delegation or duplicate-assertion overlap candidates directly
   - treat bounded test-ratio posture as a named positive pattern when the repo constrains both under-testing and test-surface inflation
   - `security`: are there meaningful code, secret, or supply-chain risks
   - `operability`: are setup, CI, install/update docs, and maintenance surfaces honest enough to sustain the quality bar
   - treat checked-in hook config, a repo-owned hook installer/checker, and repo-owned install paths for extra gate binaries as a first-class positive pattern, not only the absence of a missing gap
   - when the repo authors skills, include skill package quality, portable bootstrap seams, and shared-helper drift in these lenses
   - make `behavior` explicit about whether coverage is standing-gated, informally sampled, or absent
   - make evaluator depth explicit: smoke only, maintained evaluator-backed, or still smoke plus HITL
   - if stronger local proof depends on an external binary or support tool, state whether it is currently installed and healthy, then surface the exact install and post-install verification path instead of vague prose
   - prefer the shared recommendation payload when a validation tool is missing instead of hand-writing install guidance from scratch
5. Classify each issue by enforcement tier first.
   - `AUTO_EXISTING`: already enforced by a meaningful deterministic gate
   - `AUTO_CANDIDATE`: should be promoted into a linter, validator, test, hook, or script
   - `NON_AUTOMATABLE`: still requires judgment, tradeoff analysis, or human review
6. Classify gaps.
   - `healthy`: already enforced and useful
   - `weak`: present but low-signal or easy to game
   - `missing`: should exist but does not
   - `defer`: useful later, but not the next highest-leverage gate
7. Propose the next quality moves concretely.
   - for missing or weak gates, name the exact setup or command family to add
   - tag every recommended next gate as `active` or `passive`; passive entries require an explicit reason such as future-tool dependency, broader product decision, or runtime budget tradeoff
   - prefer the smallest gate that materially improves confidence
   - do not force one stack's tooling when the repo does not use that stack
   - when the problem is automatable, prefer a deterministic gate over prose
   - when the automatable move is already clear and repo-owned, implement it in
     the same turn unless the user asked to stay review-only
   - when the next deterministic move is to install or refresh the repo-local quality surface itself, prefer the bootstrap posture and leave a machine-readable deferred-setup report
   - if executable specs are slow or overlapping, delete duplicates, move detail into unit-level checks, or add a direct adapter before widening the spec bar
8. Run one fresh-eye premortem on the drafted report.
   - use `references/fresh-eye-premortem.md`; if subagents are available and explicitly allowed, a fresh-eye subagent is ideal, otherwise do the challenge pass yourself without rereading the draft first
9. End with a quality posture summary.
   - what was actually run
   - what runtime or diagnostic signals were captured
   - which runtime hot spots dominate the current bar
   - whether coverage is standing-gated, indirect, or absent
   - whether evaluator-backed depth exists, or whether the deeper bar is still smoke plus HITL
   - what the current bar proves
   - what it still does not prove
   - the next best gate or cleanup to add

- `Scope`, `Current Gates`, `Runtime Signals`, `Coverage and Eval Depth`, `Maintainer-Local Enforcement`, `Enforcement Triage`, `Healthy`, `Weak`, `Missing`, `Deferred`, `Commands Run`, `Recommended Next Gates`

- Do not reduce quality to one aggregate score.
- Do not split quality bootstrap into a second public concept when the work is still bounded repo-local quality setup.
- Do not recommend gates the repo cannot realistically run without saying why.
- Do not confuse gate presence with gate usefulness.
- Do not ignore runtime drift just because a gate still passes functionally.
- Do not wait for operator follow-up before stating current runtime hot spots, coverage-gate presence or absence, and evaluator-depth status when the repo signals are available.
- Do not treat slow or broad executable specs as automatically strong quality when they mostly duplicate cheaper deterministic coverage.
- Do not recommend verbose or permanent logs without naming who will read them and how they stay bounded.
- Do not leave an automatable quality rule as prose-only guidance when a linter, validator, test, hook, or script could own it.
- If you stop short of an obvious repo-owned deterministic gate, name that as an unresolved enforcement gap explicitly.
- Do not treat a passing final local gate as sufficient posture when clones have no repo-owned way to run it before push and no documented no-hook waiver.
- Do not propose generic "add more tests" or "improve security" without naming the actual seam, the next concrete setup, or whether the test surface now needs a maintainability gate.
- If a gate already exists, prefer tightening or reusing it before adding a new parallel tool.
- If a stronger check would require an external tool, support skill, or permission, say so explicitly.
- If a missing binary or local setup step would materially improve confidence, recommend installing it with the reason and exact command or package family.
- Do not let whole-worktree scans fail on gitignored runtime artifacts unless the gate explicitly exists to validate that machine-local state.
- Do not collapse help, command discovery, healthcheck, readiness, and local discoverability into one generic "doctor passed" claim when the repo ships an installable CLI or plugin surface.
- Do not treat support-skill materialization or host-visible plugin discovery as the same seam as generic binary health.
- Do not hide a missing evaluator or support binary behind "deeper validation recommended"; say whether the deeper bar is currently unavailable locally and how to enable it.
- Keep repo-local markdown-link discipline separate from external URL health when the repo needs both.
- Do not pretend a conceptual boundary problem is solved just because duplicate text was linted away; semantic boundary questions still need concept review.
- If the repo is shipping a CLI or bootstrap command surface, inspect whether install/update/doctor/reset behavior follows `create-cli`-level quality expectations instead of treating the entrypoint as ordinary helper glue.
- For anti-anchoring, unfloored-file inventory, glob-vs-operational drift, and `Covered by pytest:` honesty limits, follow `references/coverage-floor-policy.md` and `references/fresh-eye-premortem.md` instead of improvising.
- If a seam refactor improves maintainability but a focused gate regresses, rule out stale gate wiring before calling it product risk.

## References

- `references/adapter-contract.md`
- `references/coverage-floor-exemptions.txt`
- `references/coverage-floor-inventory.py`
- `references/coverage-floor-policy.md`
- `references/fresh-eye-premortem.md`
- `references/maintainer-local-enforcement.md`
- `references/quality-lenses.md`
- `references/skill-quality.md`
- `references/installable-cli-probes.md`
- `references/proposal-flow.md`
- `references/gate-classification.md`
- `references/automation-promotion.md`
- `references/bootstrap-posture.md`
- `references/operability-signals.md`
- `references/executable-spec-economics.md`
- `references/sample-presets.md`
- `references/security-overview.md`
- `references/security-npm.md`
- `references/security-pnpm.md`
- `references/security-uv.md`
- `references/validate-spec-pytest-references.py`
