# Session Retro
Date: 2026-08-09
Goal: charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md

## Context

One session that started from "design the next work" and ended having shipped it.
Four commits: shaped the successor goal, closed `#560` and `#567` through the
full closeout floor, and built slice 1 (`#565`'s mutation-sweep runner). Filed
`#570`. Ran a NO-OBSERVED-EFFECT census over the repo's own quality gates via a
Sonnet dynamic workflow with adversarial refutation.

What matters next: three closeout carriers are committed and unpushed, so
`#560`, `#565`, and `#567` all read OPEN on GitHub. One push converts them.

## Window

`81ead447..94f3d68c`, four commits, one working session. No push, no release, no
remote CI.

## Evidence Summary

- Commits: `81ead447` (goal + census), `9cab4c40` (`#560`), `ffa88c2c` (`#567`),
  `94f3d68c` (`#565` slice 1).
- `charness-artifacts/audit/2026-08-09-no-observed-effect-census.md` — 90 checks
  classified, 6 candidates, 4 refuted, 2 survivors. 11 Sonnet agents, 744K
  subagent tokens, 213 tool calls, ~5m wall clock.
- Three resolution critique artifacts (`#560`, `#565`, `#567`), each with two or
  one delegated bounded rounds and clean parent-side boundary fingerprints.
- `scripts/mutate_and_restore.py` + 26 tests; a dogfood sweep of the tool against
  its own repairs (4 killed of 5, 1 recorded unpinned).
- `mine_closeout_telemetry.py` over 1576 records: 4 recurring waste items, all
  `gate_runtime`, peak 475s for the standing pytest lane.
- Prior retro digest: `charness-artifacts/retro/recent-lessons.md`.

## Waste

**The dominant waste was rework inside my own repairs, and it was productive
rather than avoidable.** Seven blockers across two review rounds on `#565`, four
of them in the first draft and three inside the fixes for the first four. Each
round cost a full write-review-repair cycle. This is the measured cost of the
two-round rule, and it bought a tool that would otherwise have shipped reporting
false verdicts.

**Genuinely avoidable, three instances:**

- I asserted `#567`'s problem 2 was "UNVERIFIED and contradicted" and reported
  that to the operator, then measured it and found it fully implemented. One
  command (`check_doc_authoring_preflight.py --repo-root .`) would have settled
  it before I spoke. Cost: a wrong disposition in the handoff that a reviewer
  later had to catch as a blocker.
- I claimed a test "declares `bundle_ready_repo` but never uses it" from a grep
  window that stopped one line short of the use. Cost: small, self-caught by
  mutation, but it was stated to the operator first.
- A crude regex proxy produced "14 checks cannot fail" including `pytest` and
  `dup-ratchet`. Discarded before use, but it was run and reported before being
  sanity-checked.

All three are the same shape: **I spoke before measuring, on questions a command
could answer in seconds.** The repo already names this ("Settle by measuring, not
by debating, when a command can answer") and it still fired three times.

**Not waste, recorded so it is not mistaken for it:** the census's 744K subagent
tokens bought a decision on an open `question`-labelled issue that had been
unanswerable for days, and its adversarial pass prevented four wrong deletions.
The gate-runtime telemetry (peak 475s) is the standing suite doing its job; this
session ran targeted modules instead and paid it only at commit boundaries.

## Critical Decisions

1. **Verifying the handoff's premise before acting on it.** The named pickup was
   already complete and pushed. A bare pickup would have re-run a finished
   release. This single check reframed the whole session from "continue" to
   "design fresh".
2. **Asking "should this checker be code at all?" instead of repairing it.** The
   operator's question turned `#563` from a scope-widening slice into a deletion,
   after measurement showed the checker exits 0 everywhere, reports 0 findings,
   and has two lifetime commits.
3. **Making the census adversarial rather than single-pass.** 4 of 6 first-pass
   candidates were refuted. A single-pass census would have recommended deleting
   four working surfaces.
4. **Declining `#564`'s filed remedy.** Two durable records had already rejected
   it as rulebook growth; shaping a slice around it would have been the
   Change-Discipline trap. The question moved into the tool instead.
5. **Recording one repair as UNPINNED rather than writing a test that looks like
   coverage.** The `restore` verify-before-invalidate ordering has no
   distinguishing observable; a test asserting it would have been decoration.

## Trends vs Last Retro

`recent-lessons.md` carries "Three planned items were premises, not debt" from
`2026-07-27`. **It fired three more times this session** — the completed release,
`#567`'s problem 1, and `#564`'s remedy — which makes it the most durable repeat
trap in the digest and the one most worth converting from prose into a step.

It also carries "A finding repaired at one call site out of two" from
`2026-08-08`. The sibling this session is sharper: `#560`'s blocker was a repair
carrying a FALSE EXPLANATION rather than an incomplete one, and `#565`'s round-2
blockers were repairs applied to one of two symmetric verdicts. The pattern is
generalizing from "half the call sites" to "half the symmetric cases".

## North Star Alignment

**P4/P5 held and were load-bearing.** Every proof surface authored here got a
distinct observer, and every one of them found something the author could not
see. `#560`'s blocker, `#567`'s blocker (my own handoff contradicting my close),
and `#565`'s seven — none were visible to careful re-reading by the writer.

**P3 held twice, deliberately.** `#564`'s template rule was declined in favour of
tool behaviour, and `check_title_slug_drift.py`'s deletion keeps the
rename-residue ANGLE while dropping the enumerating tool.

**P1 was applied correctly and then overruled with evidence.** The title-slug
checker was advisory under P1; a year of no observed effect turned "keep the
signal visible" into "delete it", which is P1 reasoning followed to its end
rather than a violation of it.

**The failure signature I walked into: "a gate that checks gates."** The census
came within one design decision of becoming a meta-gate. It was kept as a table
plus a recommendation, and slice 4 explicitly forbids it from deleting anything.

**Where I violated the standard:** three times I rendered a verdict over a scope
I had not measured (see Waste). That is precisely the class this goal exists to
close, committed by the agent closing it.

## Expert Counterfactuals

**Douglas Engelbart — treat (H + LAM + T) as one unit; design the Tool alongside
the Language and Method.** The briefed lens for harness work, and it lands on the
sharpest miss of the session. I hand-rolled a mutation harness FIVE times —
fixture-parameter deletion, two drift-code deletions, the probe revert, and a
manual `cp` restore — across `#560` and `#567`, and only then built the tool that
does exactly that. The Method ("mutate the call site to prove the repair") was
already fluent; the Tool lagged by two issues. Engelbart's move: the moment the
same manual procedure appears twice in one session, that is the T-half signalling
it is missing — build it then, and let the rest of the session use it. Concretely
this session would have gone slice-1-first, and `#560`/`#567`'s repairs would
have been proven BY the runner rather than by five `cp`/`pytest` pairs. The
repo's own digest already predicted this ("a repo-owned mutate-and-restore
helper... three hand-rolled harnesses in one run is the trigger") — the trigger
fired at five and I still built it last.

**Direct lens — the falsification-first reviewer.** Every claim I got wrong this
session was one I could have falsified with a single command before stating it.
The counterfactual is not "review more"; it is a rule about SPEAKING: an
assertion about repo state that a command can settle does not get spoken until
the command has run. That would have caught all three Waste items and cost
seconds each. It differs from the Engelbart lens (which is about building the
tool) by being about the order of speech and measurement.

## Sibling Search

- axis: **the same premise-check gap in other skills' shaping phases** |
  location: `achieve`'s Before phase now has `## Backlog Recount`, but no
  equivalent "verify the remedy a durable record proposes" step; `issue`'s
  resolve flow reads the issue but not the records that may have superseded it |
  decision: valid follow-up outside the slice | proof: `#564`'s remedy was
  rejected in two durable records and I still shaped a slice around it; `#567`'s
  fix commit said "the repair for #567" and the issue sat open |
  follow-up: deferred — carried into the handoff as a next-session candidate
- axis: **hand-rolled harnesses elsewhere in the repo** | location: prior goal
  artifacts' slice logs record inline sweeps | decision: valid follow-up outside
  the slice | proof: the superseded draft goal explicitly cut a sweep over
  already-shipped repairs as unbounded | follow-up: deferred — this is the
  owning goal's own later-slice question, not a new one
- axis: **verdict surfaces with asymmetric guards** | location: `#565`'s runner
  had scope accounting on `KILLED` and not `SURVIVED`; the census's own
  classifier attacked only its 6 candidates and never its 84 clearances |
  decision: fixed in slice (the runner) + disclosed (the census) | proof: round 2
  found the runner's asymmetry; the census's `## Non-claims` records its own |
  follow-up: none — both dispositioned

## Next Improvements

- **workflow**: before stating a claim about repo state that a command can
  settle, run the command. This session's three avoidable errors were all
  spoken-then-measured. The rule is about the order of speech, not about doing
  more review.
- **capability**: `achieve`'s Before phase should ask, for each remedy a durable
  record proposes, whether that remedy's premise still holds — the same shape as
  `## Backlog Recount` but pointed at prior goals, audits, and issue comments
  rather than the tracker. `#564` is the measured instance: two records had
  already declined its filed remedy. Destination: issue.
- **memory**: this retro plus the recent-lessons digest, with the
  premises-not-debt trap promoted — it has now fired in three separate sessions
  and six measured instances.

## Portable Candidate

- Abstract pattern: **a mutation-sweep runner that refuses to report a kill it
  cannot evidence** — no kill without a passing baseline count, no kill from a
  bare exit code, unconditional restore, and refusals for ambiguous or absent
  edits.
- Triggering evidence: nine false kills in one measured sweep here; five
  hand-rolled harnesses in this session alone; and the runner's own first two
  drafts each reproduced the defect it exists to prevent.
- Intended consumer shape: any repo whose agents are asked to prove a repair by
  mutation — i.e. every repo that installs `charness`'s `prove`/`impl` flow.
- Destination: `create-skill` — but NOT yet. It is pytest-summary-shaped, and a
  portable version needs a declared runner contract first. Recorded as a
  candidate, not a commitment.
- First-prompt acceptance claim: "given a deliberately broken test command, the
  runner reports zero kills and names the broken baseline."

## Packet Consumed

n/a (no adapter sections)

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-09-session-retro.md
