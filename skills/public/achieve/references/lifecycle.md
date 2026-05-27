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
- slice sequence
- critique plan
- stop conditions
- reporting expectations

Ask a small number of high-leverage questions. Do not interrogate the user for
detail that a strong default or the request wording already settles.

Save the artifact with `upsert_goal.py` at status `draft`. Tell the user the
file is inert until they run the activation command. The skill does **not** start
executing slices on its own — activation is the user's explicit decision.

## During

The goal artifact becomes the working scratchpad for the active run. Do not use
`handoff` as the mid-goal memory surface while a goal is active.

After each slice, append a slice report with `append_slice_log.py`:

- objective and why this slice was chosen now
- commits or files changed
- alternatives rejected
- targeted verification (cheap, deterministic)
- critique findings
- off-goal findings filed through `issue`
- lessons to carry into the next slice
- a token / time / tool-call snapshot when available

Each slice uses targeted deterministic checks. Broad quality gates and expensive
proof belong at bundle boundaries or the final stage, not after every commit.
Subagent critique is slice-level by default, not commit-level.

Stop and ask the user when an unexpected blocker, an evidence conflict, or a
policy/product decision appears that cannot be resolved autonomously. Flip the
status to `blocked`, record the blocker and the paths already attempted, and
hand the decision back rather than guessing.

## After

At completion the goal artifact should contain:

- final self-verification against the original goal
- final quality gate results
- high-confidence or high-cost verification results, or an explicit statement
  that they were not run
- residual risks and non-claims
- concrete user verification instructions
- an automatic retro focused on reducing time, tokens, and waste next time

Run `check_goal_artifact.py` before declaring completion so the required
sections, status, and activation line are all present. Flip the status to
`complete` only after the final report separates what was proven from what
remains the user's responsibility to verify.

## Honest Proof Discipline

Borrow W. Edwards Deming's Plan-Do-Study-Act emphasis on the *study* step:
measure the result against the original prediction before claiming the goal is
met. A run that skips the comparison has done activity, not achievement.

Never claim provider, live, or release proof when only local deterministic
checks ran. If a proof level was skipped, the final report must say so.
