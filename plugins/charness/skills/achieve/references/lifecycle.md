# Achieve Lifecycle

`achieve` runs one goal as three phases: **before** (shape and save), **during**
(slice and record), **after** (prove and reflect). The goal artifact is the
single durable surface across all three so a compacted or interrupted run can be
audited from one file.

## Before

Start from prose, not from an already perfect goal. Shaping happens here, in the
Before-phase (invoked via `/achieve`), never at `/goal` activation. Interview
only until the work has enough shape to save a reviewable goal artifact.
Establish:

- desired outcome
- non-goals and boundaries
- user-visible acceptance proof
- low-cost agent verification
- high-confidence or high-cost verification
- per-slice expected proof cost and expected test-duplication pressure, so a
  slice that adds or expands tests states up front whether it is likely to push
  a broad duplicate/length/pressure gate toward its threshold
- slice sequence
- critique plan
- when the goal resolves a tracked issue: the `debug` root-cause step for a
  bug-class issue (planned *before* the fix slice) and the closeout
  close-via-`issue` step (`Close #N` on the fix/closeout commit) — see
  `references/coordination.md` *Resolving A Tracked Issue*
- stop conditions
- reporting expectations

Ask a small number of high-leverage questions. Do not interrogate the user for
detail that a strong default or the request wording already settles.

### Mode disambiguation (#239)

One mode question is high-leverage often enough to call out: is this an
**artifact-only** goal draft (shape and save, then stop) or an
**implementation-continuation** run (the user expects slices to execute once
activated)? When the selector or prose is genuinely ambiguous between the two,
ask at least one question to resolve it before saving — a wrong assumption here
either strands a draft the user wanted executed or starts executing a draft the
user wanted only reviewed. When a strong default settles it (the prose names the
mode), state the assumed mode in the artifact and the response instead of
asking. The mode is a shaping-time intent question only; it never licenses
auto-execution, because `/goal` (pursue) and `/achieve` (shape) are separate
operator actions (#247). This is the
[#239](https://github.com/corca-ai/charness/issues/239) before-phase
question-discipline contract.

### Anti-anchoring probe

For each value confirmed by the user, inherited from issue framing, or
pulled from prior session memory, test whether the value is one of a known
system axis (host, provider, environment, profile, locale, runtime, tier)
before locking the design. Record the result on each value:

- `axis: <name>` when the system already varies on that axis somewhere
  else (adapter, preset, profile, integration manifest), or
- `single-point: <reason>` when the value really is a singleton.

A confirmed value with neither record is over-anchored. This is the
[#229](https://github.com/corca-ai/charness/issues/229) lesson — one
confirmed model name was treated as a global default when the repo runs
on multiple hosts.

When the repo is known to vary on a host/provider/environment axis, do
**not** offer an `AskUserQuestion` that frames the value as a global
`confirm <value-X>` vs `defer to host` binary. Offer the family shape
instead (one option per axis instance), or ask the axis question first.

A `critique` Before-phase pass may pick the
[`confirmed-input over-anchoring`](../../critique/references/confirmed-input-over-anchoring.md)
angle to verify the probe ran honestly.

### Portability self-test

A goal artifact must be readable by a fresh session without the saving
session's working memory. Before saving the artifact at status `draft`,
the Before-phase records three durable sections inline (already present
in the template):

- `## Context Sources` — retros, prior goal artifacts, issue numbers,
  recent-lessons surfaces; what a fresh session follows first.
- `## Interview Decisions` — for each user question: the family
  considered, the chosen value, and the rejected-alternatives reason.
  This applies the anti-anchoring lesson to the artifact itself.
- `## Plan Critique Findings` — blockers folded into Boundaries /
  Verification / Slice Plan, over-worry raised but not folded, and
  reviewer provenance. Preserves the reasoning so a fresh session does
  not have to re-run critique to verify the folded revisions.

`check_goal_artifact.py` enforces these on every goal regardless of
size. A goal that genuinely has nothing for a section keeps the heading
and writes `N/A — <reason>`. (#255 removed the old size/marker exemption:
its full-text `Single-slice goal:` scan was poisoned by prose merely
describing the marker, and the template already seeds all three headings,
so the exemption was both unsafe and redundant.)

When shaping an auto-drafted skeleton, overwrite its
`To be filled by the achieve Before-phase` placeholder lines with the real
content — a leftover marker leaves the goal reading as unshaped to the
pursue-readiness check, which would make `/goal` fail-fast on an
actually-shaped goal (#247).

Save the artifact with `upsert_goal.py` at status `draft`. Tell the user the
file is inert until they run the activation command. The skill does **not** start
executing slices on its own — activation is the user's explicit decision.

### Activation-closeout clarity (#239)

The before-phase response must make activation impossible to miss. Close it with
an explicit checklist the operator can act on without rereading:

- `Goal file:` — the saved artifact path under `charness-artifacts/goals/`.
- `Activation:` — the exact `/goal @<path>` line to run.
- the inert-until-`/goal` status stated in one sentence (nothing runs until
  the user activates).

`check_goal_artifact.py` already fails closed when the artifact body is missing
its `Activation:` line; this closeout checklist is the response-side counterpart
so the operator-facing handoff is as clear as the artifact contract.

### Activation = pursue only (#247)

`/goal @<artifact>` is **pure pursue**: it runs the During loop on the goal as
given and never shapes. Shaping is the Before-phase's job (invoked via
`/achieve`); whoever runs `/goal` is responsible for handing it a shaped goal.

Before pursuing, confirm the goal is shaped with
`check_goal_artifact.py --pursue-ready --goal-path <artifact>`. If it is
**unshaped** (the Before-phase placeholder marker is still present — e.g. a raw
handoff-chunker auto-draft that was never `/achieve`'d), **fail-fast**: refuse to
pursue and route the operator to the Before-phase (`/achieve @<artifact>`). Do
**not** shape the goal inside `/goal` — that would put shaping back into the
pursue path, the exact responsibility blur #247 removes.

## During

The goal artifact becomes the working scratchpad for the active run. Do not use
`handoff` as the mid-goal memory surface while a goal is active.

Activation runs only after the pursue-readiness check passes (see
*Activation = pursue only*). When the run begins (the user has activated the
goal), flip the status to `active` with `upsert_goal.py --status active`; move
it to `blocked` or `complete` as the run state changes.

After each slice, append a slice report with `append_slice_log.py`:

- objective and why this slice was chosen now
- commits or files changed
- alternatives rejected
- targeted verification (cheap, deterministic)
- test-duplication pressure: when the slice adds or expands tests, a cheap
  duplicate-pressure sample (the repo's duplicate/length gate run in sample or
  report mode), so accumulated suite debt stays visible at the slice boundary
  instead of surfacing only at final closeout
- critique findings
- off-goal findings filed through `issue`
- lessons to carry into the next slice
- a token / time / tool-call snapshot when available

Each slice uses targeted deterministic checks. Broad quality gates and expensive
proof belong at bundle boundaries or the final stage, not after every commit.
Subagent critique is slice-level by default, not commit-level. The cheap
duplicate-pressure sample is the exception that stays slice-local: it is a
sample, not the full broad gate, and it carries the test-debt signal forward in
the goal artifact so a compacted or resumed session does not rediscover the same
late blocker.

`run_slice_closeout.py` auto-surfaces two recurring-trap signals so they are
workflow affordances, not agent memory: a **length-headroom advisory** for any
changed gated file already near its limit (`limit − current`; #256 — choose a new
module over appending before the hard gate fires), and — via the
`check_staged_mirror_drift.py` pre-commit gate — a **hard block** when exported
source is staged without its regenerated `plugins/` mirror (#257). Both are
owned by `<repo-root>/docs/conventions/implementation-discipline.md`.

Stop and ask the user when an unexpected blocker, an evidence conflict, or a
policy/product decision appears that cannot be resolved autonomously. Flip the
status to `blocked`, record the blocker and the paths already attempted, and
hand the decision back rather than guessing. When test-duplication pressure is
the blocker or relevant context, cite the latest `Test duplication pressure`
sample in the blocked record so the user and any resumed session inherit it
instead of rediscovering it.

## After

At completion the goal artifact should contain:

- final self-verification against the original goal
- final quality gate results, including the full broad duplicate/length/pressure
  gate when the run added or expanded tests; if that gate fails, classify the
  failure as new-slice-local (introduced by this run's slices) or
  accumulated-suite debt (pre-existing pressure the run pushed past threshold),
  and name the smallest next structural cleanup rather than only reporting the
  failing percentage
- high-confidence or high-cost verification results, or an explicit statement
  that they were not run
- residual risks and non-claims
- concrete user verification instructions
- when the goal resolved a tracked issue: its close is *staged* through `issue`
  — the default-branch commit/PR body carries `Close #N` so the maintainer's
  push auto-closes it (it is still OPEN at `achieve` closeout); `achieve` does
  not push or close out-of-band (see `references/coordination.md` *Resolving A
  Tracked Issue*)
- an automatic retro focused on reducing time, tokens, and waste next time
- a closeout narration that surfaces the retro's `## Waste`,
  `## Critical Decisions`, `## Next Improvements`, and `## Sibling Search`
  (when present) sections inline in the user-facing response — the retro
  file is the durable copy, the user-facing message is the transport.
  "Persisted at `<path>`" alone is the [#233](https://github.com/corca-ai/charness/issues/233)
  F2 recurrence pattern (three observed occurrences as of 2026-05-28:
  the #226 origin run, the #230+#229 closeout that filed #233, and the
  handoff-chunked-routing closeout that inherited #233 as an Off-Goal
  note and still hit it). As of #233 the After-phase evidence gate now
  surfaces a `narration_required_sections` list naming exactly which of
  these sections the cited retro contains — narrate each one inline.
  Narration itself stays a prose contract (a hard transcript gate would
  over-fire); the list is the affordance, not a blocker.

Run `check_goal_artifact.py` before declaring completion so the required
sections, status, and activation line are all present. Flip the status to
`complete` only after the final report separates what was proven from what
remains the user's responsibility to verify.

### Improvement disposition

The retro's value is realized only if its improvements change something. The
loop has three rungs — capture (the retro artifact + `recent-lessons.md`
digest), surface (the digest is a pull surface other sessions are told to
read), and apply — and only the first two are automatic. Application does not
happen on its own: a prose `Next Improvement` left in the retro decays out of
the digest (recency half-life + slot limits) and is, in practice, lost unless a
later session both reads it and chooses to act.

So the After-phase must **close the loop, not widen it**. At closeout, give
every improvement the retro or the run surfaced an explicit disposition — one
of exactly two:

- **applied-in-session**: converted to *teeth* this run — a gate, hook,
  validator, test, or code/contract change — and committed. Teeth self-apply on
  the next run; prose does not. Prefer this when the improvement is small enough
  to land now or names a recurrence a future session would otherwise repeat.
- **filed-as-issue**: a tracked `issue` (via the `issue` skill / adapter
  backend) so the next session picks it up from the live backlog the handoff
  chunker reasons over. Prefer this when the improvement is real but larger than
  the current goal's scope, or needs its own design.

Which of the two — apply now vs file for next session — is the **agent's
judgment**, weighing the improvement's size against the current goal's scope.
What is **not** optional: leaving an improvement as prose-only retro memory is
not a valid disposition. Record each improvement's outcome in the Auto-Retro
section as `applied: <what landed>` or `issue #N`, so a fresh session can audit
that the loop was closed. (This rule is itself the applied form of the lesson
that `achieve` captured improvements but never closed the apply rung.)

The two forms above are **per-improvement**: each improvement that exists is
applied or filed. A goal may instead assert, once, that *no actionable
improvement exists to disposition* — an explicit
`Retro dispositions: none — <reason>` line inside `## Auto-Retro` (≥30 chars,
mirroring the skip discipline). This is a **per-goal** assertion at a different
scope, not a third escape box: it is a factual claim the fresh-eye reviewer can
**falsify** (it reads the retro and contradicts a false "none"). Use it only
when the retro genuinely surfaced nothing to act on.

### Disposition gate — two rungs (#253)

The disposition rule above earns teeth from two complementary rungs, each doing
only what it is good at (the gate-and-intelligence split). A deterministic
false-positive is worse than a false-negative — it trains token-theater — so the
deterministic teeth stay narrow and ungameable, and the substantive judgment is
made by an agent and recorded for a human, never by a regex.

- **Rung 1 — deterministic floor** (in `goal_artifact_disposition.py`, run by the
  After-phase evidence gate). Two ungameable, offline, clone-safe checks:
  - *block-the-blank*: refuse the `complete` flip when the cited retro lists
    actionable `## Next Improvements` but the goal's `## Auto-Retro` is blank and
    no opt-out is recorded. Emptiness only — it never classifies prose.
  - *review-ran evidence*: require a bound `Disposition review:` line (below).
    This is **presence/binding-only by design**: it proves a fresh-eye review
    *ran* and binds to this goal; it never inspects the review's content. A
    future maintainer must not tighten it into a content classifier — that
    re-imports the prose word-list trap one level up.
- **Rung 2 — the fresh-eye disposition review** (the intelligence). The
  After-phase already mandates a bounded fresh-eye closeout review; this gives
  that reviewer an added mandate: read the cited retro's `## Next Improvements`
  and the goal's `## Auto-Retro`, and record a **per-improvement verdict** —
  for each improvement, dispositioned (`applied:` / `issue #N` / explicit-none)
  or undispositioned — into a review artifact the `Disposition review:` line
  binds. This is the substantive call a regex cannot make (polarity, "filed" vs
  "not filed", narration-vs-action). It is **non-deterministic by nature** — made
  visible and auditable for a human, not a hidden pass — and near-zero marginal
  cost because it scopes an already-required review rather than adding an agent.

**Honest limit.** The deterministic floor proves the *process* ran (a review
exists and binds) and catches the unambiguous *blank*; it never scores whether a
non-empty Auto-Retro genuinely disposed each improvement. That substantive
judgment is rung 2's and the human's. A fully-deterministic *substantive* check
is infeasible — a prose word-list over-fires or passes pure narration (proven on
the live corpus) — so #253's literal "deterministic check" is satisfied as a
deterministic floor **plus** a recorded intelligent review, named honestly, not
as a quiet scope-narrowing. Narration stays a non-blocking affordance while
review-*existence* is blocking, for one principled reason: you can ungameably
check "is there a bound `Disposition review:` line" (offline, clone-safe), but a
hard transcript gate on whether the agent narrated substance would over-fire.

### After-phase evidence gate

`upsert_goal.py --status complete` now refuses the flip unless the goal
artifact body carries two evidence lines (anywhere; the parser scans the
whole body):

- `Retro: <path>` — a checked-in retro artifact under
  `charness-artifacts/retro/` produced by running the `retro` skill this
  run, **or** `Retro: skipped: <enum>: <detail>` with the enum from
  `host-blocked-subagent`, `host-log-not-exposed`, `evaluator-unavailable`
  and ≥40 chars total (free-text "host limit" is rejected).
- `Host log probe: <path>` — a JSON file containing
  `probe_host_logs.py` output (e.g.,
  `charness-artifacts/probe/<date>-<slug>.json`), **or**
  `Host log probe: skipped: <enum>: <detail>`.
- `Disposition review: <path>` — **for in-scope goals only** (#253; see
  grandfather rule below) — the fresh-eye disposition-review artifact (rung 2),
  e.g. under `charness-artifacts/critique/`, **or**
  `Disposition review: skipped: host-blocked-subagent: <detail>` on a host that
  cannot spawn the reviewer (graceful degradation to rung 1 only). A
  `host-blocked-subagent` skip on a host that demonstrably *can* spawn is itself
  an audit-flag for the human reader, not a clean pass.

The `## Auto-Retro` blank check (rung 1a) and the `Disposition review:`
requirement (rung 1b) fire only for goals **`Created:` on or after the rule
landing date `2026-05-30` (inclusive)**. A goal shaped before the rule existed
had no chance to plan its Auto-Retro/review around it, so keying on `Created`
(not completion date) grandfathers exactly the in-flight goals; a
missing/malformed `Created:` fails **closed** (the gate applies) so a goal cannot
dodge both rungs by corrupting one line. Grandfathering is clone-safe (in-file
content, not mtime).

`check_goal_artifact.py` runs the same check post-flip when the goal's
status is already `complete`, so the gate stays visible from both
directions. (A goal closed before the rule but `Created` on/after the landing
date — e.g. `2026-05-30-issue-251`, closed ~80 min before the rule commit — is
in-scope and shows a rung-1b diagnostic on re-check, but is never *re-refused*:
the flip-guard only fires on a non-`complete` → `complete` transition.) The
contract lives at
`<repo-root>/docs/prescribed-skill-closeout-contract.md`.

A cited evidence file must also **bind** to this goal (#233 F1): file
presence is necessary but not sufficient, so each evidence path's
basename or content must reference the goal's identity (its slug or the
issue numbers parsed from the `Activation:` line). A closeout that points
`Retro:` at an unrelated pre-existing artifact is refused with a
`binding_failures` entry. Binding is clone-safe (basename/content tokens,
not mtime — a fresh checkout resets every file's mtime).

## Honest Proof Discipline

Borrow W. Edwards Deming's Plan-Do-Study-Act emphasis on the *study* step:
measure the result against the original prediction before claiming the goal is
met. A run that skips the comparison has done activity, not achievement.

Never claim provider, live, or release proof when only local deterministic
checks ran. If a proof level was skipped, the final report must say so.
