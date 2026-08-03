# Issue Resolution Critique — #494, #493, #492

Date: 2026-08-07
Goal: [2026-08-07-finish-the-sweeps-this-run-left.md](../goals/2026-08-07-finish-the-sweeps-this-run-left.md)
Observer: delegated bounded reviewer (`bounded-reviewer`), distinct agent context,
run BEFORE any close call.
Reviewer boundary window: `w-20260803T144557Z-156359`, `verify` → `clean`.

The prior critique in this family
([2026-08-06](2026-08-06-issue-487-488-489-490-resolution-critique.md)) REFUSED two
of four closes and produced two of the three issues under review here. Refusal was
an expected outcome, and the reviewer was told so.

## Verdicts

**#494 — CLOSE.** Classification `bug` (a real MISS). Both halves of the acceptance
hold: `test_upsert_goal_input_channel.py` drives a REAL shell twice as a controlled
pair — the reproduction asserts the loss still happens under exit 0 and `"created"`,
the repair asserts the same prose arrives intact through the same shell — and
`references/goal-artifact.md` no longer demonstrates the form it forbids. The
reviewer verified the miss is a miss: the 2026-08-06 critique names `upsert_goal.py`
as in-scope-and-unswept, and nothing in that goal records it as an accepted deferral.

**#493 — CLOSE.** Classification `deferred-work`. The issue's own reproduction is
the test, the false-positive control varies VALUE and not merely presence (the axis
the buggy predicate read), and the whole-block arm is separately pinned. The
deferral record predates this run: 2026-08-06 goal non-claim 5, with its direction
stated. The variation from the issue's non-binding candidate direction — a
wholly-refilled block keeps its block name rather than naming every leaf — is
recorded in the function's docstring with the measured-wrong alternative named.

**#492 — CLOSE.** Classification `deferred-work`. The reviewer's key finding: the
reconstruction is an HONEST discharge of "from git", not a weakened acceptance
dressed up. `_reconstruct_the_cycle` derives the hoisted names from the live source
and fails loudly if the function-level imports are gone, so it is pinned to the real
module rather than to a fossil; and the reconstruction is proven to emit the issue's
exact error text before any assertion about the gate. "From git" was impossible —
the pre-fix module was never committed — and that limitation is stated in the test's
own docstring. The reviewer judged the resulting acceptance *stronger* than the
literal one.

## Pre-close conditions the reviewer set, and their disposition

1. **Two wrong pattern counts in the goal artifact** — "three of nine" and, worse,
   "outside its five patterns" inside `## Non-claims`. `SCAN_PATTERNS` ships eight.
   The reviewer's framing is the right one: a wrong denominator in the scope-
   limitation sentence, for a gate whose whole thesis is that a verdict must state
   what it measured, on a run whose disposition review had just corrected eight
   false figures. **Both corrected before this artifact was written.**
2. **An unrecorded trigger gap, and it is instance SIX of this run's own class.**
   `staged_commit_gate_plan.py` scoped the new gate to changed `.py` under
   `scripts/` or `skills/`, excluding repo-ROOT modules — `runtime_bootstrap.py` and
   `skill_runtime_bootstrap.py`, imported by 135 scripts, the exact family
   `SCAN_PATTERNS`'s first entry was added for and the one the inversion test found
   because nobody listing families thought of it. The enumeration had been repaired;
   the trigger one layer up still carried the original blind spot. The reviewer
   called this "the single item most likely to become next run's #494".
   **Repaired rather than filed** — it is this run's own wiring bug, the fix is one
   condition, and it is now pinned. Recorded in the goal's residual-risk list as the
   sharpest evidence for #499.
3. **The behavioural verdict channel gates all three closes.** The fix channel was
   local pytest plus the slice gate, and every artifact-side proof is also local
   pytest, so none of it can serve as the distinct channel. The only adequate
   distinct observer AND channel is the remote CI check-runs API read on the pushed
   HEAD carrying all three commits. **No close was made before that read landed**;
   the verdict is recorded per issue in the closeout commit message.

## What the reviewer independently swept, so the closes can assert it

- **The sibling class for #494 is genuinely swept**: no other skill helper takes
  free prose on argv into an artifact — `issue_create.py`, `issue_tool.py close`,
  `publish_release_cli.py` and `audit_public_release_narrative.py` all use
  `--body-file`/`--notes-file`. `issue_create --title` sits in the same
  short-identifier carve-out as `upsert_goal --slug/--date/--status`.
- **`draft_goal_from_chunk.py` is the second goal-artifact writer** and it has no
  argv-prose channel (it takes a ChunkCandidate JSON), but it does NOT route through
  `upsert_goal`, so the new value guards reach one writer of two. Filed as #495. A
  close body claiming the goal-artifact writers are guarded, plural, would be the
  same overclaim #487 was narrowed for — so the close says one of two.
- **#492's enumeration genuinely covers the issue's stated scope**, not just the
  common case: `scripts/` has no subdirectories and skills have no deeper script
  nesting, both verified. The exclusions are decisions on the record enforced by an
  inversion test, and `plugins/` is a delegation to its own mirror inversion rather
  than a hole.

## Residue this run created, all filed before closing

#495 (slice A's second writer), #496 (slice B's hollow refills — residue this fix
introduced), #497 (found by slice C's gate on day one), #498 (the template splice),
#499 (the structural guard-boundary class). The reviewer confirmed nothing else was
left unfiled once the trigger gap was repaired.

## Bar comparison

The 2026-08-06 critique refused a close because a sibling named in the goal's own
Boundaries was unswept AND unrecorded. Applying the same bar: #494's sibling is
recorded (#495), #493's residue is recorded (#496), #492's mirror failure is
recorded (#497). The one instance of the 2026-08-06 pattern still live at review
time — #492's trigger gap, unswept and unrecorded — is why the reviewer made it a
pre-close condition rather than a note, and it is now repaired.

## Close Sequence

1. Correct the two pattern counts. **Done.**
2. Repair the commit-gate trigger gap for repo-root modules. **Done and pinned.**
3. Push the closeout commit; read remote CI through the check-runs API — a different
   observer AND a different channel than the push exit code.
4. Only then write each `Behavior #N:` verdict citing that read, and close through
   `issue_tool.py` with `validate-closeout-draft` reporting `draft_verified` and
   `verify-closeout --expect-state CLOSED` reading the state back.

## Reviewer Tier Evidence

- Requested tier: this host's typed `bounded-reviewer` subagent (read-only Read/Grep/Glob).
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing or team name (per the repo spawn-shape rule), session-model inheritance.
- Host exposure state: applied
- Application state: host-confirmed: the Agent tool was exposed, the spawn returned findings inline, and the reviewer self-reported `envelope-bound` (no Bash/Edit/Write/Agent), which is the intended envelope. Per the per-host subagent split the Codex model/effort request does not apply on a Claude Code host, so its absence is contract-conformant.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepared packet was consumed; the reviewer was given an inline packet naming the artifacts and questions, and read the repo directly. -->

## Boundary Ownership

- Producer: the three issue resolutions in commits 25a8e265, 86be2df5, 70e32238
- Consumer: the GitHub issue record each close writes, and any session reading it later
- Owning surface: each issue's own owning surface (achieve helper input, quality policy report, repo gate)
- Verdict: single-surface

The one cross-owner question raised — that `draft_goal_from_chunk.py` is a SECOND goal-artifact writer the new guards do not reach — was escalated to issue #495 rather than folded in, and the close body says "one of two writers" rather than claiming the class. The trigger-gap finding was in-surface (this run's own wiring) and repaired here.
