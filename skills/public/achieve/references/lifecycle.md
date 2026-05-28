# Achieve Lifecycle

`achieve` runs one goal as three phases: **before** (shape and save), **during**
(slice and record), **after** (prove and reflect). The goal artifact is the
single durable surface across all three so a compacted or interrupted run can be
audited from one file.

## Before

Start from prose, not from an already perfect `/goal` command. Interview only
until the work has enough shape to save a reviewable goal artifact. Establish:

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
- stop conditions
- reporting expectations

Ask a small number of high-leverage questions. Do not interrogate the user for
detail that a strong default or the request wording already settles.

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

`check_goal_artifact.py` enforces these on any non-trivial goal (Slice
Plan with 2+ data rows, or Slice Log with 2+ `### Slice` headings). A
one-shot research-only goal may use a `Single-slice goal: <reason>`
marker inside the Slice Plan section to opt out.

Save the artifact with `upsert_goal.py` at status `draft`. Tell the user the
file is inert until they run the activation command. The skill does **not** start
executing slices on its own — activation is the user's explicit decision.

## During

The goal artifact becomes the working scratchpad for the active run. Do not use
`handoff` as the mid-goal memory surface while a goal is active.

When the run begins (the user has activated the goal), flip the status to
`active` with `upsert_goal.py --status active`; move it to `blocked` or
`complete` as the run state changes.

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

`check_goal_artifact.py` runs the same check post-flip when the goal's
status is already `complete`, so the gate stays visible from both
directions. The contract lives at
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
