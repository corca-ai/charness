# Session Retro
Date: 2026-08-14

## Context

This session took the release-runner visibility owner the previous retro named
as its `capability` next-improvement, and shipped it. The unit under review is
one slice: a shared child-process primitive with an explicit quiet-probe versus
monitored-phase caller choice, plus its two converted callers.

Evidence trustworthy for this retro is strong and local: two measured
process-tree runs, three bounded reviewer reports, the standing gate, and the
closeout telemetry stream. Everything about the unpushed publication remains
weak — it was inspected, not exercised.

The session also surfaced three findings the slice did not own. They were filed
rather than absorbed, which is the decision most worth reviewing below.

## Window

The two commits `dac792e2a` and `1b448f9f4`, their two bounded review rounds, and
the ambient scan that produced #619 and #620. Publication, issue closure, and
installed-host proof are outside it.

## Evidence Summary

- Direct measurement, twice: a 1.0s budget against `bash -c 'sleep 25 & sleep 25'`
  returned after 25.0s before the process-group kill and 1.0s after. A third run
  with the group kill reverted returned at 6.2s — the number that proved a timing
  assertion alone could not pin the repair. (strong)
- Three bounded reviewer reports; the round reading the REPAIRS found two blockers
  the first round could not have seen. (strong)
- `python3 scripts/run_standing_pytest.py --repo-root . --mode full
  --include-release-only` at HEAD: 3 failed, 9012 passed, 21 errors — the evidence
  behind #619. (strong)
- `inspect.getsource(subprocess.Popen.__exit__ / run / send_signal)` on this host
  confirmed all three CPython claims a reviewer flagged as memory-based, including
  the bpo-38630 pid-recycling guard. (strong)
- `mine_closeout_telemetry.py` over 1,704 records: the single most-recurring gate
  is `pytest -q -m 'not release_only' ...`, 16 occurrences, 475s peak. (strong)
- [Current quality record](../quality/latest.md) owns the full receipt.

## Waste

**The largest waste was avoided, not paid, and naming how matters.** The previous
retro's improvement said "give long-running child execution one reusable
`monitored_phase` path". Read literally that is an instruction to build a new
primitive, and the first draft did exactly that — a new
`skills/shared/scripts/monitored_run.py` whose `atomic_capture` was a
near-duplicate of an existing function. One `rg` for the timeout message found
`scripts/subprocess_guard.run_process` already owning that half. The file was
deleted and the missing shape went into the existing owner instead. Cost: about
one file's worth of writing. Cost had it shipped: two competing owners for "how
this repo spawns a child", which is the exact concept-integrity failure the
quality lens exists to catch. (strong)

**Two rounds of review were not ceremony.** Round 1 found three blockers. The
repairs for those blockers introduced two more — a timeout branch that relabelled
a child which had already exited, and a group kill that dropped the reaped-pid
guard CPython carries for bpo-38630. Round 2 read the repairs and caught both.
Every measured slice in this repo that shipped a fix carrying the class it fixed
is the reason the second round is mandatory on proof surfaces; this slice is
another data point, not a counterexample. (strong)

**Real waste: the retro artifact and the quality artifact both fought their own
size and path contracts.** The quality artifact needed six trimming passes to
reach a 140-line budget the validator only reports after the whole artifact is
written, and each pass initially reworded without deleting. That is a slow loop
the scaffold could shorten by reporting the budget against a draft.

**Real waste: the probe drift message names surfaces #596 already superseded.**
Adding one quality artifact reds a pinned probe, and the failure message
instructs updating `2026-08-01-inventory-marker-rule.json` and `docs/deferred-decisions.md`
D47. D47's own text says corpus growth must not rewrite it, and the marker pin
moved to an immutable dated snapshot. Following the message literally would have
edited two surfaces that should not move. (strong)

## Critical Decisions

1. **Extend the existing owner instead of adding a primitive.** Chosen after an
   existing-convention grep. Skipped: a new shared module reachable from skill
   packages via `parents[3]`. Constrained later work usefully — the release
   scripts reach `scripts.subprocess_guard` through a precedent that already
   existed in the same directory, so no new bootstrap block was duplicated.
2. **File three ambient findings rather than fix them.** `charness init` is broken
   at HEAD and that is arguably higher priority than this slice. Fixing it would
   have mixed an unrelated format-contract decision into a reviewed commit and
   demanded its own proof lane. Filed as #619/#620 and put first in the handoff
   trigger instead. This is the decision most open to challenge; the counter-case
   is that a broken install path outranks slice hygiene.
3. **Preserve isolated bodies rather than tee the child's stream.** The prescribed
   transformation said so explicitly, and teeing is a genuinely distinct third
   caller choice. Recorded as a disclosed non-goal in the module header rather
   than silently deferred — so the quality runner still surfaces only through the
   parent's heartbeat until it exits.
4. **SIGTERM before SIGKILL.** Round 2 pointed out that a bash EXIT trap runs on
   the first and never on the second, and `run-quality.sh` uses one to remove its
   temp dir. Cost: a 0.5s grace per kill. Bought: the child's own cleanup, which
   the repo names as its operator recovery channel.

## Trends vs Last Retro

The previous 2026-08-14 retro's `capability` improvement is now closed by this
slice. Its `closeout-diagnostic-visibility` recurrence class appeared three times
in that retro's improvements; this session reduced it to one open instance (the
remaining release-lane `run_shell` consumers, deliberately unconverted pending
measurement). The `proof-surface-review-binding` lesson — run the broad gate
before minting the final review binding — was followed: the broad gate ran
before both rounds and again after each repair set.

New this session and not in the prior trend: a gate whose *message* has drifted
from the surfaces it names.

## North Star Alignment

The north star says brief a capable judge and keep teeth only where a wrong
answer escapes. This slice added no gate. It moved teeth into the one place a
wrong answer escapes unobserved — the child-process boundary — and left the
heartbeat interval, the drain bound, and the grace period as parameters a caller
briefs rather than a floor a validator enforces. At the irreversible boundary
(a publish that can abort on a false timeout), the confirmation came through a
different observer and a different evidence channel: bounded reviewers reading
the code, and direct process-tree measurement contradicting the code's own
docstring.

## Expert Counterfactuals

**Engelbart (system-improving-itself; the planner's briefed lens).** Treat the
human, the language, and the tooling as one unit. This session improved T (the
primitive) and LAM (the "quiet probe versus monitored phase" vocabulary) together
— that part is on the nose. Where Engelbart would have pushed harder: the LAM
improvement is currently carried only by a module docstring. A caller choosing
between the two shapes has no tool that answers "which should this call site
use?". The measured inventory that started this work — 230 capture markers, 17
declaring a 60s-plus timeout — was produced once, by hand, and is now stale. He
would have shipped that inventory as a repeatable command alongside the
primitive, so the vocabulary can be applied to the remaining call sites without
re-deriving the census.

**Charity Majors (does it fail early and emit what a maintainer can use under
pressure?).** She would have forced one question earlier than it was asked:
*what does an operator actually see during those 1800 seconds?* Asking it first
would have surfaced immediately that the child already streams its own lifecycle
and the parent buffers it — which reframes the fix from "add a heartbeat" to
"stop swallowing a stream that already exists". The heartbeat is the right
bounded answer, but the reframing is what produced the honest non-goal in the
module header instead of an unstated limitation. She would also downgrade one
confident story: the claim that the repo "has no shared monitored-capture
primitive" was in a durable quality record and was half wrong — the atomic half
existed. A remedy named in a durable record is a hypothesis, and this one cost a
file before a single grep falsified it.

## Sibling Search

- same layer: the remaining `run_shell` consumers in the release lane
  (`run_post_publish_install_refresh`, the distinct-channel probes) | decision:
  valid follow-up outside the slice | proof: read each call site; none has a
  measured runtime justifying conversion, and converting blind repeats the
  anti-need this slice avoided | follow-up: deferred [handoff Next Session item 4](../../docs/handoff.md)
- abstraction up: other long-running orchestrators the prior inventory ranked —
  skill A/B, JS mutation, mutant restore, eval fan-out, worktree prepare,
  skill-surface preflight | decision: valid follow-up outside the slice | proof:
  the ranking exists in the prior quality record but the census was hand-produced
  and is now stale; a re-run is the precondition, not the conversion |
  follow-up: deferred [quality record Recommended Next Quality Moves](../quality/latest.md)
- specialization down: `scripts/subprocess_guard.run_processes_in_order`, the
  parallel sibling of `run_process` | decision: intentional boundary | proof: it
  is the atomic shape fanned out; a monitored variant of it would need the
  interleaving story `run-quality.sh` already solves in shell, and no caller asks
  for one
- mental-model siblings: gates whose failure MESSAGE names surfaces that later
  moved — the probe drift message still instructs a D47 edit and a
  `2026-08-01-inventory-marker-rule.json` update that #596 superseded | decision:
  valid follow-up outside the slice | proof: read D47, which states in its own
  text that corpus growth does not rewrite it; the instruction was not followed
  and the reason is recorded in the probe's own `synchronized_reason` |
  follow-up: https://github.com/corca-ai/charness/issues/624

## Portable Candidate

Abstract pattern: a runner that spawns one long child owes that child a streamed
lifecycle, and the choice between quiet capture and monitored phase should be a
named parameter at the call site rather than an accident of which helper was
nearest. Triggering evidence: an observable child buffered by a silent parent for
up to 1800 seconds. Intended consumer shape: any repo whose CI/release tooling
shells out to its own test runner. Destination: `not portable — the pattern
already belongs to the public `quality` operability lens, and the primitive's
correct API shape is still repo-local until a second codebase demonstrates the
same need. The reusable artifact here is the *lens question*, not the module.

## Lesson Evaluation

Lesson evaluation: {"reason":"missing-start","score_event_count":0,"session_id":"none","status":"not-evaluated"}

This slice opened no declared lesson session. The earlier sessions' lessons are
not backfilled from this retro.

## Next Improvements

- **capability**: ship the capture/monitored-phase census as a repeatable command
  next to the primitive, so the remaining call sites can be classified without
  re-deriving the 230-marker inventory by hand.
  (recurrence-class: closeout-diagnostic-visibility)
- **workflow**: when a durable record names a missing capability, grep for the
  half that may already exist before building — this slice's first draft
  duplicated `run_process` because the record said "no shared primitive" and only
  the monitored half was actually missing.
  (recurrence-class: premise-not-checked-against-source)
- **capability**: have the quality artifact scaffold report its line budget
  against a draft rather than only after a complete artifact, so the trim loop
  costs one pass instead of six.
  (recurrence-class: artifact-contract-late-feedback)
- **workflow**: when a gate's failure message instructs edits, verify each named
  surface still owns what the message claims before editing — two of the four
  named here were superseded by #596.
  (recurrence-class: proof-surface-message-drift)
- **memory**: a second review round on a proof surface is not a formality; the
  round that read the REPAIRS found two blockers the first round could not have
  seen, both in code written to fix the first round's findings.
  (recurrence-class: proof-surface-review-binding)

## Packet Consumed

Packet Consumed: n/a (no packet prepared for this window; the prior
2026-08-14 packet covers the earlier current-contract slice, not this one)

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-14-monitored-execution-retro.md
