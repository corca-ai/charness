# Prescribed Skill Closeout Contract

This document is the implementation contract for the
[#230 + #229](https://github.com/corca-ai/charness/issues/230) self-substitution
pattern fix. It owns the cross-cutting design that
[the achieve goal artifact](../charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md)
points at, before any of the three sibling closeout surfaces (`achieve` /
`issue` / `release`) drift on their own.

The companion read-side contract is
[skills/shared/references/prescribed-path-self-test.md](../skills/shared/references/prescribed-path-self-test.md);
that owns "a self-test must exercise the next agent's prescribed path". This
doc owns the closeout-side counterpart: "a closeout must execute the prescribed
sub-skill, not paraphrase it".

## Problem

The #226 run measured the pattern at scale: the After-phase prescribed
`retro` invocation and host-log probe were inline-paraphrased instead of run,
and the goal was flipped to `complete` anyway. The same prose-only reliance
exists in `issue` resolution closeout (resolution critique) and `release`
closeout (standalone critique). The Before-phase has the design-anchoring half
(#229): a user-confirmed single value gets treated as a closed design space.

Both halves share one shape — substitute a lighter self-authored version for a
prescribed/fuller thing. Convention alone has now demonstrably failed twice;
the next move is gates, not exhortation.

## Scope

This contract changes:

- `skills/public/achieve/` — After-phase guard, Before-phase anti-anchoring
  probe step, Before-phase portability self-test, and the
  [goal artifact library](../skills/public/achieve/scripts/goal_artifact_lib.py)
  required-sections list.
- `skills/public/issue/` — closeout guard before `issue_tool.py verify-closeout`
  (no duplication of the existing ledger verification).
- `skills/public/release/` — closeout guard before publish closeout.
- `skills/public/critique/` — one new angle reference
  (`confirmed-input over-anchoring`) callable from any Before-phase critique.
- `<repo-root>/scripts/check_prescribed_skill_executed.py` — new repo-owned, portable
  helper that the three sibling skills reuse.

This contract does not change the `/goal` host runtime, the broad pre-push
quality gate's correctness guarantees, or the markdown hook / push-gate router
(those are slices 6 and 7, scoped here only for stop-condition consistency).

## Shared Closeout Guard

### Design

A single repo-owned helper script enforces "the prescribed sub-skill ran or was
explicitly skipped with a reason". Each sibling skill wraps it with its own
required-evidence list; no skill embeds the policy in prose alone.

Helper path: `<repo-root>/scripts/check_prescribed_skill_executed.py`.

Why repo-owned (not under one skill's `scripts/`): three public skills share
it. Placing it under one skill couples the other two to that skill's directory
layout; placing it under the repo's `scripts/` keeps each calling skill
standalone (no `achieve`-only branch in `issue` or `release`).

### Helper Surface

```text
check_prescribed_skill_executed.py
  --repo-root <path>
  --closeout-kind <achieve|issue-resolution|release>
  --evidence <name>:<path-or-glob>     # repeatable
  --skip <name>:<reason-text>          # repeatable
  --json
```

For each `--evidence` the helper requires the path to exist and to be
non-empty; a `--skip` for the same name is the only honest substitute. A
closeout that names neither for a required evidence kind fails with exit
code 1 and lists the missing names.

The helper does not know which kinds are required for which closeout — that
list lives in each calling skill's wrapper. The helper is the gate; the
wrapper supplies the contract.

### Per-Skill Required Evidence

| Closeout kind | Required evidence | Skip allowed? |
| --- | --- | --- |
| `achieve` After | `retro_artifact` (a checked-in `charness-artifacts/retro/<date>-<slug>.md` newer than goal `active` flip), `host_log_probe` (`probe_host_logs.py` output recorded in the goal artifact or a sibling JSON) | yes, with `skip: <reason>` (e.g., host log not exposed) |
| `issue-resolution` | `resolution_critique` (one line of the carrier body starting with `Critique:` followed by either an artifact path under `charness-artifacts/critique/` matching `*<issue-number>*.md` or the literal phrase `blocked <host-signal>`) | yes, with `skip: <reason>` only when host blocks subagents |
| `release` closeout | `standalone_critique` (artifact reference or `Critique: blocked <host-signal>`) | yes, with `skip: <reason>` only when host blocks subagents |

The helper validates that a `skip` reason is non-empty and not in the
placeholder set (`{tbd, todo, n/a, missing}`). A skip without a substantive
reason is not honest substitution.

### Integration Points

- `achieve`: `check_goal_artifact.py` invokes the helper when the requested
  status flip is `complete`. The helper failure returns exit 1 and the status
  flip refuses.
- `issue`: `issue_tool.py verify-closeout` invokes the helper before its
  existing ledger verification when the resolved classification is `bug`,
  `feature`, or `deferred-work`. The existing ledger checks
  (`missing_close_keywords`, `missing_fields`, `state_mismatches`,
  `manual_comment_missing`) are unchanged, and
  [`_classification_requirements`](../skills/public/issue/scripts/issue_verify_closeout.py)
  is **not** extended — the new helper reads its own carrier-body header
  (`Critique:` line), independent of the existing per-classification field
  set, so there is one body source of truth per check and no field-list
  overlap.
- `release`: `publish_release.py` (and the manual `release` workflow path)
  invokes the helper before tag push or publish.

### Portability Decision

The helper is repo-owned shell-callable Python under `scripts/`, with no
host-specific assumption. Each calling skill passes the evidence list as
arguments. This satisfies the boundaries stop condition (no `achieve`-only
branches in `issue` or `release`) and the standalone-usefulness rule (each
skill can call the helper directly without depending on `achieve`'s lifecycle
state).

The portability fallback (slice 1 stop condition) does **not** fire:
infeasibility would require the helper to depend on one skill's internal
state. The evidence list pattern keeps it portable.

## Before-Phase Anti-Anchoring Probe

### Probe Contract

Add an explicit Before-phase step to `achieve` (between interview and goal
artifact save):

> For each value confirmed by the user or inherited from issue framing, test
> whether it is one of a known system axis (host, provider, environment,
> profile, locale) before locking the design. Record the axis as
> `axis: <name>` or as `single-point: <reason>` per value in the goal
> artifact's `Interview Decisions` section.

The probe runs before the goal is saved at status `draft`. A confirmed value
without an axis or single-point record refuses save.

### New Critique Angle

`<repo-root>/skills/public/critique/references/confirmed-input-over-anchoring.md`
— a short angle reference (≤80 lines) that any Before-phase critique can cite.
It asks:

- Does any decision treat a user-confirmed or issue-inherited value as
  closing a design space that the system varies on elsewhere?
- For each anchor, is the axis (host / provider / environment / profile)
  named, or is single-point intent recorded explicitly?
- Are there `AskUserQuestion` options that present a host/provider-specific
  value as a global confirm/defer binary when the repo runs on multiple
  hosts?

This angle is one of the angles `critique` may pick during a Before-phase
review; it is not always required.

The new angle file is listed in `critique/SKILL.md` `## References` (the
[`validate_skills`](../scripts/validate_skills.py) gate requires every
`references/` file to be listed), but **`critique/SKILL.md` net line count
must not grow** past the 200-line ceiling. Adding the reference listing
forces compressing one existing guardrail by one wrapped line. The
recent-lessons Repeat Trap #1 (the 200-line gate biting twice) is exactly
this trade-off; record it explicitly in the slice log so the next session
inherits the constraint.

### AskUserQuestion Guidance

The `achieve` lifecycle reference grows a one-sentence rule: when the repo is
known to run on multiple hosts/providers, do not offer a confirm-value-X /
defer-to-host binary. Offer the family shape instead, or ask the axis
question first.

## Before-Phase Portability Self-Test

### Required Sections

[The goal artifact library](../skills/public/achieve/scripts/goal_artifact_lib.py)
adds three required sections that must be present **before the goal can be
saved at status `draft`** for any non-trivial goal (defined below):

- `Context Sources` — durable references this goal was shaped from; a fresh
  session can reconstruct the originating context by following them in order.
- `Interview Decisions` — for each Before-phase question: family of options
  considered, chosen value, and rejected-alternatives reason. Applies #229's
  anti-anchoring lesson to the artifact itself.
- `Plan Critique Findings` — blockers folded, over-worry raised but not
  folded, and reviewer provenance. Preserves reasoning so a fresh session
  re-verifies folded revisions without re-running critique.

These sections are required for any goal whose Slice Plan has two or more
slices. Single-slice goals (rare) may use a one-line "Single-slice goal:
no portability sections required" note in place.

### Self-Test

A new test fixture (`<repo-root>/tests/skills/test_goal_artifact_portability.py`)
loads a synthetic two-slice goal artifact missing one of the three sections and
asserts that [check_goal_artifact.py](../skills/public/achieve/scripts/check_goal_artifact.py)
fails. A second fixture with all three sections present passes. The test fails
if the required-sections check is removed.

The `check_goal_artifact.py` output gains a `portability_missing_sections`
field so the failure is legible without re-grepping.

### Trivial Goal Exemption

`goal_artifact_lib.py` counts **data rows in the `## Slice Plan` markdown
table** (lines starting with `|` that are not the header row or the
separator row); one or fewer rows is `trivial` and exempts the three new
sections. Two or more is `non-trivial` and requires them.

Counting `### Slice N:` headings would misfire on the dominant
representation: the
[goal-artifact template](../skills/public/achieve/scripts/goal_artifact_lib.py)
ships an empty `## Slice Plan` table and no `### Slice` headings (those
appear only in `## Slice Log` once the run starts). The slice-2 portability
fixture must cover both the table form (planning intent) and the heading
form (execution log) so the discriminator stays honest if a goal author
chooses heading-only Slice Plan style.

## Stop Conditions

All stop conditions from the
[goal artifact Boundaries](../charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md#boundaries)
remain authoritative; this spec narrows them to concrete files:

- Portability fallback: see decision above; this spec records that fallback
  did **not** fire and explains why. If slice 3 or 4 discovers the helper
  must embed `achieve`-specific state to be useful, downgrade to three
  standalone wrappers and re-run plan critique on the revised slice plan.
- Slice 6 markdown-hook stop: any change to
  [scripts/check-markdown.sh](../scripts/check-markdown.sh)
  that removes failing-file names from stdout fails the slice; verify
  against a known-failing fixture before commit.
- Slice 7 push-gate stop: any router change that skips the broad gate when
  the pushed diff touches `plugins/`, `.claude-plugin/`, or
  `.agents/plugins/` is rejected unconditionally.

## Test Plan

Per slice 1 (this spec): plan critique on this doc and on the revised slice
plan before slice 2 begins.

Per slices 2–5: unit tests under `tests/skills/` for each guard wrapper plus
the shared helper. Each wrapper test fails when the prescribed sub-skill is
not run and there is no skip record.

Per slice 8 (closeout): real-host smoke of the achieve After-phase guard
against a small dummy goal closeout. Recorded as "host: Claude Code" with
Codex coverage deferred unless trivially available.

## Non-Claims

This spec does not redesign `retro`, `critique`, the GitHub-backed issue
verification path, or the publish pipeline. It introduces one shared gate
helper and three thin wrappers plus a Before-phase probe + portability
self-test, all additive.

## References

- [Goal artifact](../charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md)
- [Source retro](../charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md)
- [achieve lifecycle](../skills/public/achieve/references/lifecycle.md)
- [achieve goal artifact reference](../skills/public/achieve/references/goal-artifact.md)
- [issue closeout discipline](../skills/shared/references/closeout-discipline.md)
- [issue verify-closeout helper](../skills/public/issue/scripts/issue_verify_closeout.py)
- [release SKILL.md](../skills/public/release/SKILL.md)
- [critique SKILL.md](../skills/public/critique/SKILL.md)
- [prescribed-path self-test (read-side counterpart)](../skills/shared/references/prescribed-path-self-test.md)
- [implementation discipline](./conventions/implementation-discipline.md)
- [operating contract](./conventions/operating-contract.md)
