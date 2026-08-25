# Prescribed Skill Closeout Contract

> Status: current
> Source of truth: this page and its linked executable surfaces

This document is the implementation contract for the
[self-substitution pattern fix](https://github.com/corca-ai/charness/issues/230)
(#230). It owns the cross-cutting design that
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
  --kind <achieve|issue-resolution|release>
  --require <name>                     # repeatable
  --evidence <name>:<path>             # repeatable
  --skip <name>:<reason-text>          # repeatable
  --context-token <token>              # repeatable; see Context Binding
```

Output is unconditionally YAML; there is no output-format flag.

For each `--evidence` the helper requires the path to exist and to be
non-empty; a `--skip` for the same name is the only honest substitute. A
closeout that names neither for a required evidence kind fails with exit
code 1 and lists the missing names.

The helper does not know which kinds are required for which closeout — that
list lives in each calling skill's wrapper. The helper is the gate; the
wrapper supplies the contract.

### Context Binding (#233 F1)

Presence is necessary but not sufficient: a closeout could cite any
pre-existing artifact in the repo and pass the presence check (the #233 F1
hole — demonstrated live by pointing `Retro:` at a pre-existing retro from an
unrelated goal). The helper exposes a reusable
`evidence_binds_to_context(path, *, tokens)` predicate: an evidence file
binds when its basename carries a distinctive context token, or its content
does. A BARE number in content must additionally be *cited* (`#27`, `issue 27`,
`issues/27`, `gh-27`) rather than merely present, and a date/time run in a
basename is masked before matching — without that, a critique of an unrelated
issue bound a #27 closeout through its own `Date: 2026-07-27` header (hunt B4). The
wrapper supplies the tokens (the achieve wrapper derives the goal slug + the
issue-number cluster from the goal artifact's `Activation:` line). Token
containment is clone-safe; an `mtime >= context-date` rule is deliberately
**not** used because a fresh `git clone` resets every file's mtime to checkout
time and would pass every stale file, silently reopening the hole.

Binding lives in `check()` itself, at the shared choke point. It did not always:
`evidence_binds_to_context` was defined and `check()` never called it, so binding
held exactly where `achieve` and `issue` had wired the predicate by hand and
nowhere else — the generic CLI and the release publish gate carried none at all,
and a real critique about an unrelated topic satisfied an `issue-resolution`
closeout (sweep S4, parent-reproduced). Callers pass `tokens=`; the generic CLI
takes `--context-token`. `release` now binds to the version being published
(both the dotted `2.12.0` and the hyphenated `2-12-0` the critique basenames
use), closing what this section previously recorded as a follow-up.

`tokens` empty still means presence-only — some callers genuinely cannot derive
an identity — but the report records that as `binding_checked: false` and
`binding: not-checked` per item, so a presence-only pass can no longer be read as
a bound one.

A dotted release version is boundary-matched like any other numeric cluster.
It was not: `_token_matches` fell through to plain substring containment for
anything that was not a hyphen/underscore cluster, so `2.12.0` bound a critique
that merely mentioned a dependency at `12.12.0`. A leading `v` is allowed on the
boundary, because `v2.12.0` / `v2-11-2-release-critique.md` is how this repo
names release artifacts and refusing it would reject the artifacts the gate
exists to accept.

**Closed, and not with a byte floor:** sweep row S3 observed that the only
content test was `st_size == 0`, so a stub satisfied the gate. Two byte floors
were written for it and both withdrawn — a basename-channel-only floor left the
*cheaper* content channel open (`printf '#466' > x.md` is four bytes and binds),
and a universal one was still defeated by filler while failing 34 existing
tests. That second withdrawal rested on a mis-measurement worth recording: the
34 were TEST FIXTURES, not evidence. The artifacts start at 427 bytes.

The rule that closed it is narrower than size: **evidence must say something
beyond the identity it cites.** After the citation tokens are removed, at least
`MIN_BOUND_RESIDUAL_CHARS` alphanumeric characters must remain. Measured before
it was written, and the measurement is a **checked-in script** rather than a
number in a comment — [`scripts/measure_evidence_residual.py`](../scripts/measure_evidence_residual.py),
whose recorded run is
[`charness-artifacts/probe/2026-08-01-evidence-residual-floor.json`](../charness-artifacts/probe/2026-08-01-evidence-residual-floor.json).
The stub's residual is 0; markdown artifacts floor at 337 over 2168 files, and
real JSON host-log probes at 530 over 83. The floor sits at 8, below every
measured minimum rather than between two of them.

It broke no existing **assertion**. It did break four degenerate **fixtures** —
12-byte shapes such as `{"goal":"g"}` — which were rewritten to be realistic with
their assertions untouched. That is recorded here rather than omitted, because
the previous withdrawal of this floor rested on the mirror-image elision: it
counted 34 failing fixtures as evidence about how this repo writes evidence.

It runs wherever an identity is available: the `tokens=` binding path, and
`residual_tokens=` for the two wrappers that must bind out-of-band
(`issue_resolution_critique` binds per issue NUMBER, `goal_artifact_closeout_evidence`
per entry). Wiring it through `tokens=` alone would have missed both: measured,
a four-byte `#466` file closed issue #466 with the floor already in the library.
A caller that can derive no identity at all still gets presence-only, and the
report says so through `residual_checked`.

**What stays open:** a few characters of filler still passes, exactly as any
floor here would — this refuses a stub, not a lie. The remaining distance is
per-kind SHAPE, and this library is deliberately policy-free and generic over
evidence names, so it remains the wrong layer for a kind-specific floor.
`validate_critique_artifacts.py` and `validate_retro_artifact.py` own shape, and
they run from the repo's quality gate rather than on this accept path.

The achieve After-phase wrapper wires binding for goal evidence. The
`issue-resolution` wrapper also binds resolution-critique evidence to each
selected issue number, and multi-issue carriers must use explicit `Critique #N:`
or `Critique #N #M:` lines.

### Per-Skill Required Evidence

| Closeout kind | Required evidence | Skip allowed? |
| --- | --- | --- |
| `achieve` After | `retro_artifact` (a checked-in `charness-artifacts/retro/<date>-<slug>.md` newer than goal `active` flip), `host_log_probe` (`probe_host_logs.py` output recorded in the goal artifact or a sibling JSON), and — **for goals `Created` ≥ `2026-05-30` only** — `disposition_review` (#253; a bound fresh-eye disposition-review artifact); plus the routing/gather/release/issue **coordination floors** (separate, presence-only — gather/release `Created` ≥ `2026-05-31`; issue `Created` ≥ `2026-06-02`; phase routing `Created` ≥ `2026-06-04`; see *Coordination Floors* below) | yes, with `skip: <reason>` (e.g., host log not exposed; `disposition_review` only with `host-blocked-subagent`); coordination floors via a `Routing:`/`Gather:`/`Release:`/`Issue closeout:` step or `n/a — <reason>` opt-out |
| `issue-resolution` | `resolution_critique` (one carrier-body line per issue, `Critique #N: <artifact-or-blocked>`, or an explicit bundle line such as `Critique #N #M: <artifact-or-blocked>`; the single-issue shorthand `Critique: <artifact-or-blocked>` is still accepted) | yes, with `skip: <reason>` only when host blocks subagents |
| `release` closeout | `standalone_critique` (artifact reference or `Critique: blocked <host-signal>`) | yes, with `skip: <reason>` only when host blocks subagents |

The helper validates a `skip` reason on two axes, both in
[check_prescribed_skill_executed_lib.py](../scripts/check_prescribed_skill_executed_lib.py):

1. it must **start with** one of the enum heads `host-blocked-subagent`,
   `host-log-not-exposed`, `evaluator-unavailable`, followed by `:` and a detail;
2. the whole reason must be at least `MIN_SKIP_LENGTH` (40) characters **and**
   the detail after the enum head at least `MIN_SKIP_DETAIL_LENGTH` (20).

The detail floor exists because several callers (`issue_resolution_critique`,
`publish_release_preflight`) prepend the enum head themselves from an author
shorthand. On those carriers the enum check validates a constant the caller
supplied, so the length floor is the only blocking tooth — and the head's own
characters were paying it down, which let a 17-character signal skip a mandatory
fresh-eye critique on a GitHub issue close. The floor now measures only author
text.

Length refuses terseness; it cannot refuse a fluent excuse, and it is not sold as
doing so. What distinguishes a skipped critique from an executed one is that the
skip is surfaced as a non-blocking `REVIEW:` advisory on every issue carrier. A
skip without a substantive reason is not honest substitution.

### Improvement-Disposition Gate (#253)

The After-phase requires every retro/run improvement to be dispositioned
(`applied:` / `issue #N`), not left as prose-only memory. That rule earns
deterministic teeth from two complementary rungs — the gate-and-intelligence
split — implemented in
[`goal_artifact_disposition.py`](../skills/public/achieve/scripts/goal_artifact_disposition.py)
and wired through the achieve After-phase evidence gate:

- **Rung 1 — deterministic floor** (offline, clone-safe, ungameable):
  - *block-the-blank* — refuse the `complete` flip when the cited (bound) retro
    lists actionable `## Next Improvements` but the goal's `## Auto-Retro` is
    blank and no `Retro dispositions: none — <reason>` opt-out is recorded
    (Auto-Retro-scoped; a full-text scan is poisoned by goal bodies that merely
    *describe* the marker). Emptiness only — it never classifies prose.
  - *review-ran evidence* — require the bound `disposition_review` line above.
    Presence/binding-only **by design**: it proves a fresh-eye review *ran* and
    binds to this goal; it never inspects the review's content. Tightening it
    into a content classifier re-imports the prose word-list trap one level up
    and is disallowed.
  - *structural-follow-up destination* (#337) — when the cited retro names a
    transferable waste item (a `## Sibling Search` trigger), `## Auto-Retro` must
    carry a `Structural follow-up:` line whose value is one of four destinations
    (`applied:` / `issue #N` / `repo-local guard: <path>` / `none — <reason>`), so
    "recorded in recent-lessons" cannot pass as a structural disposition.
    Presence/form-enum only; inert unless transferable waste is named; same
    grandfather-by-`Created`-date shape (≥ `2026-06-09`).
- **Rung 2 — fresh-eye disposition review** (the intelligence): the bounded
  closeout reviewer reads the retro's `## Next Improvements` + the goal's
  `## Auto-Retro` and records a **per-improvement verdict** (dispositioned vs
  undispositioned) into the artifact the `Disposition review:` line binds. This
  is the substantive, polarity-aware call a regex cannot make; it is
  **agent-backed / non-deterministic** and host-dependent, made auditable for a
  human, not a hidden pass.

Both rungs are **grandfathered by `Created` date** (≥ `2026-05-30` inclusive —
the rule landing date; missing/malformed `Created` fails closed). Keying on
`Created` (not completion date) grandfathers goals shaped before the rule existed
that had no chance to plan around it. The check fires at the `--status complete`
flip (`upsert_goal.py`) and post-flip (`check_goal_artifact.py`), so it is
visible from both directions; a goal already `complete` is diagnosed but never
re-refused.

**Honest limit.** #253 asked for a "deterministic check". A fully deterministic
*substantive* check is infeasible — a prose word-list over-fires or passes pure
narration (proven on the live goal corpus) — so the gate is a deterministic
*floor* (proves the review ran; catches the blank) **plus** a recorded
intelligent review (judges substance). Rung 1b is therefore weaker than #253's
literal ask, by design and named, not by quiet scope-narrowing.

### Coordination Floors (routing + gather + release + issue)

The achieve After-phase carries further presence-only floors, in
[`goal_artifact_coordination_floors.py`](../skills/public/achieve/scripts/goal_artifact_coordination_floors.py)
and
[`goal_artifact_phase_routing.py`](../skills/public/achieve/scripts/goal_artifact_phase_routing.py),
wired through the same evidence gate. They give *teeth* to
owner-skill routing boundaries the goal-artifact `## Coordination Cues` prose
cue under-serves (skipping them is silent and costly). Same deterministic-floor
philosophy as #253: presence/binding-only, clone-safe, block-the-blank, an
explicit opt-out valve, grandfathered by `Created`.

- **phase-routing floor** — trigger: recorded work sections show implementation
  (`What changed:` / `Commits:`), bug/RCA/debug cues, quality-gate cues, or
  issue-closeout cues. Satisfied by a `Routing:` line in `## Coordination Cues`
  that names the routed skill (`impl`, `debug`, `quality`, or `issue`) and its
  basis, or a `Routing: n/a — <reason>` opt-out (≥30 chars). This proves the
  owner-skill boundary was considered; it does not judge route prose quality.
- **gather floor** — trigger: `## Context Sources` names an external source (an
  `http(s)://` URL — Slack / Notion / Google-Docs / Drive links and bare web URLs
  all qualify). Satisfied by a `Gather: <ref>` step in `## Coordination Cues`, or
  a `Gather: n/a — <reason>` opt-out (≥30 chars). Mirrors `CLAUDE.md`'s
  external-source routing mandate.
- **release floor** — trigger: the run's *recorded work* names a release surface,
  detected by precise path/action tokens (`bump_version`, `publish_release`,
  `marketplace.json`, `charness-artifacts/release/`) — never the bare word
  "release", so a goal that merely references the release skill as context does
  not self-trip. Satisfied by a `Release: <ref>` step or a
  `Release: n/a — <reason>` opt-out.
- **issue-closeout floor** — trigger: `## Context Sources` names a
  tracked/GitHub issue, or recorded work sections (`## Slice Log` /
  `## Final Verification`) carry a close keyword such as `Close #N`.
  Satisfied by an `Issue closeout: <ref>` step or an
  `Issue closeout: n/a — <reason>` opt-out.

All detect trigger and step from the **artifact text** (not git diff), so the
signal is clone-safe — a fresh checkout reproduces the verdict. Reference + opt-out
detection is scoped to `## Coordination Cues` so a goal body that merely
*describes* a step line in prose cannot falsely satisfy a floor. Grandfather
dates are floor-specific: gather/release apply to goals Created ≥ `2026-05-31`,
issue closeout applies to goals Created ≥ `2026-06-02`, and phase routing
applies to goals Created ≥ `2026-06-04`. The gather/release floors landed
`2026-05-30`, but several same-day goals predate them, so the
`2026-05-31` cutoff grandfathers every in-flight goal;
missing/malformed `Created` fails closed. `achieve` owns the carrier + floors;
installed skill metadata and model judgment own *which* skill answers a
boundary (never an inline phase→skill map). The bidirectional surface where a standalone `/issue` or `/debug` reads the
active goal is explicitly **deferred** to its own effort.

### Closeout Delegation (orchestrator/sub-goal external proof, #318)

An *opt-in* orchestrated-closeout mode in
[`goal_artifact_closeout_delegation.py`](../skills/public/achieve/scripts/goal_artifact_closeout_delegation.py),
wired through the same After-phase evidence gate. It lets a sub-goal close at
`impl-local`/`carrier` while a *named* orchestrator goal owns the deferred
external proof, without weakening standalone goals: a goal with no
`## Closeout Delegation` section, or an explicit `Closeout mode: standalone`, is untouched (a present section with the mode line missing is `undeclared` and refused) —
the strict standalone default stays the hard default.

Closeout-state taxonomy (documentation vocabulary; the gate is
presence/resolution-based, not an exact-token match): `impl-local`, `carrier`,
`pushed-ci`, `instance-synced`, `live`, `issue-closed`.

- **orchestrated sub-goal** (`Closeout mode: orchestrated`) — must name an
  `Orchestrator goal:` and list ≥1 `Delegated proof:` item, so delegation is
  explicit (named owner + named levels), never silent omission.
- **orchestrator goal** (`Closeout mode: orchestrator`) — must carry a
  `Delegated proof checklist:` and resolve *every* item (`verified`,
  `skipped: <reason>`, or `issue #N`) before it can flip to `complete`; an
  unresolved item blocks the flip, so the orchestrator cannot silently forget a
  delegated proof.

Same deterministic-floor philosophy as the disposition/coordination floors:
presence/resolution-only, clone-safe (artifact text, not git diff), and it never
classifies whether the prose is "good enough". Opt-in *is* the grandfather: a
goal earns the gate only by declaring the section, so no pre-existing goal is
retroactively refused.

### Integration Points

- `achieve`: `check_goal_artifact.py` invokes the helper when the requested
  status flip is `complete`. The helper failure returns exit 1 and the status
  flip refuses.
- `issue`: `issue_tool.py verify-closeout` invokes the helper before its
  existing ledger verification when the resolved classification is `bug`,
  `feature`, or `deferred-work`. The existing ledger checks
  (`missing_close_keywords`, `missing_fields`, `state_mismatches`,
  `manual_comment_missing`) are unchanged, and
  [`_classification_requirements`](../skills/public/issue/scripts/issue_verify_closeout_body.py)
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
adds three required sections that must be present on **every** goal **before it
can be saved at status `draft`**:

- `Context Sources` — durable references this goal was shaped from; a fresh
  session can reconstruct the originating context by following them in order.
- `Interview Decisions` — for each Before-phase question: family of options
  considered, chosen value, and rejected-alternatives reason. Applies #229's
  anti-anchoring lesson to the artifact itself.
- `Plan Critique Findings` — blockers folded, over-worry raised but not
  folded, and reviewer provenance. Preserves reasoning so a fresh session
  re-verifies folded revisions without re-running critique.

These sections are required on **every** goal regardless of size. A goal that
genuinely has nothing for a section keeps the heading and writes
`N/A — <reason>`. (#255 removed the earlier size/marker exemption: its full-text
`Single-slice goal:` scan was poisoned by prose merely describing the marker,
and the goal-artifact template already seeds all three headings, so an exemption
was both unsafe and redundant.)

### Self-Test

[`tests/quality_gates/test_goal_artifact_lib.py`](../tests/quality_gates/test_goal_artifact_lib.py)
asserts that [check_goal_artifact.py](../skills/public/achieve/scripts/check_goal_artifact.py)
fails for a goal missing one of the three sections — including a 1-row Slice
Plan and a goal whose prose merely mentions "single-slice goal" — and passes
once all three headings are present. The test fails if the required-sections
check is removed.

The `check_goal_artifact.py` output carries a `portability_missing_sections`
field so the failure is legible without re-grepping.

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

- [Goal artifact](../charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md) — the achieve goal scratchpad, slice plan, and plan-critique findings behind this spec.
- [Source retro](../charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md) — measured waste from the achieve run that skipped its prescribed retro.
- [achieve lifecycle](../skills/public/achieve/references/lifecycle.md) — before/during/after phase split and honest-proof discipline.
- [achieve goal artifact reference](../skills/public/achieve/references/goal-artifact.md) — goal artifact location, section shape, and helper scripts.
- [issue closeout discipline](../skills/shared/references/closeout-discipline.md) — shared verified-ledger, target-durability, and external-source identity rules.
- [issue verify-closeout helper](../skills/public/issue/scripts/issue_verify_closeout.py) — checks closeout carrier body, ledger fields, and proof mismatch.
- [release SKILL.md](../skills/public/release/SKILL.md) — release workflow contract: planner bootstrap, invariants, publish output.
- [critique SKILL.md](../skills/public/critique/SKILL.md) — angle probes, counterweight pass, and bounded fresh-subagent rule.
- [prescribed-path self-test (read-side counterpart)](../skills/shared/references/prescribed-path-self-test.md) — when a self-test counts as evidence for a later agent.
- [implementation discipline](./implementation-discipline.md) — validation, change, repair, and generated-surface rules for maintenance.
- [operating contract](./operating-contract.md) — commit, external side-effect, critique, and session conventions.
