# Session Retro

Date: 2026-08-15

## Context

S6 of the 6.0.0 release scope — worktree isolation for write-capable subagents,
the monitored standing runner, the exported `link_only_lines` bar default, and
[#633](https://github.com/corca-ai/charness/issues/633) — landed in one commit
after two review rounds. The session also surfaced a defect class from a
different machine and filed it. What matters next is S6b, then S7 publishes.

## Window

`e12b41b52..54654b032` — a single commit, its four review reports across windows
`s6-operating-contract-r1` and `-r2`, and the
[#634](https://github.com/corca-ai/charness/issues/634) report that arrived
mid-slice from a consuming machine.

## Evidence Summary

- Six bounded read-only reviewers (four in round 1, two in round 2); both
  `reviewer_boundary_fingerprint verify` runs returned `verdict: clean`.
- `python3 scripts/run_standing_pytest.py` at closeout: 9448 passed in 86s.
  `ruff check --no-cache .`, `check_python_lengths.py`, and the dup ratchet all
  clean.
- Two claims proven by DIRECT PROBE rather than by reading, both of which
  changed the outcome: reverting the #633 guard in an isolated copy showed the
  pre-repair assertions still passed (so the test did not discriminate), and
  running the standing runner under a real SIGTERM with and without the signal
  handler showed the grandchild orphaned in one case and reaped in the other.
- [SC10 probe](../probe/2026-08-15-sc10-write-capable-worktree-isolation.json) —
  what this host actually does with agent worktrees, and six explicit non-claims.
- `mine_closeout_telemetry.py`: 1704 records, the same `gate_runtime` findings
  S5 recorded, still stamped `disposition: file-issue`.
- Lesson session `2026-08-15-s6`, 10 lessons presented before work
  ([receipt](./lesson-session-receipts/2026-08-15-s6.md)).

## Waste

**The dominant waste was a rule this repo had already written down and I did not
run.** Round 2's first blocker existed because a scripted string replace did not
match and failed SILENTLY, so half an edit landed and the half that carried the
assertions did not. The operating contract's Claim Fidelity clause says exactly
this: *"After a non-interactive string edit (a scripted replace, a sed), assert
the SUPERSEDED text is absent."* I ran eleven such replaces this session and
verified none of them until a reviewer found the one that silently no-op'd.
Auditing all eleven afterwards took under a minute and found the other ten had
landed — so the check was cheap, available, mandatory, and skipped.

**Second, and the near-miss worth more than the miss:** the end-to-end test I
wrote to prove the SIGTERM repair could not have failed. Its grandchild wrote
its marker after 20s and the assertion ran at 3s, so it passed whether or not
the process tree died. I found it only because I probed the test itself rather
than trusting a green run — and the probe took two minutes. A test written to
close a blocker, asserting nothing, would have shipped inside the commit whose
message claims the blocker is closed.

Third, small and mine: I told both round-2 reviewers they would have Bash. The
`bounded-reviewer` type carries Read/Grep/Glob only, so both spent part of their
report explaining what they could not verify and asking me to fetch it. The
capability is declared in `.claude/agents/bounded-reviewer.md`; I asserted the
opposite from memory.

Not waste, recorded because it looks like it: six reviewers and two rounds cost
real wall clock and produced four blockers, two of which inverted their item's
intent. The premise check likewise — it rescoped SC11 from "build the monitored
path" to "wire the one that already ships", which is the largest single
correction in the slice.

## Critical Decisions

1. **Running the premise check against source before any code moved.** The plan
   read SC11 as work to be built; `run_monitored_phase` already had three
   production callers, and the 2026-08-14 retro records that a previous attempt
   at it was a near-duplicate module, deleted. Building it again would have
   re-created exactly that duplicate.
2. **Refusing the naive conversion.** Swapping `subprocess.run` for
   `run_monitored_phase` would have silenced a multi-minute suite, because the
   monitored shape pipes its child. Writing the acceptance envelope first is what
   made `capture=False` a requirement rather than a discovery — and the module's
   own docstring had already named that mode as the third caller choice it
   deliberately had not solved.
3. **Taking a duplicate-ratchet family seriously instead of classifying it.**
   One of the four new families was `_rev_parse` versus `git_config_value`;
   folding them onto one runner revealed that `git_config_value` never received
   the git-discovery env scrub its sibling had. Classifying it as intentional —
   the cheaper move, and one I made for eleven other families — would have left
   that gap in place.
4. **Enforcing ratchet monotonicity in the gate rather than only in the test**,
   which exceeds the literal owner ruling and was confirmed by the owner. Round 1
   showed the change as first built made the ratchet WEAKER for consumers: the
   rule lived only in a file the export does not ship.

## Trends vs Last Retro

The [S5 retro](./2026-08-15-session-retro-s5.md) named its dominant waste as *a
detector that ran, named the class, assigned an action, and emitted into a
channel with no obligation attached*. S6's dominant waste is the same shape one
layer up: **a rule that is written, correct, mandatory, and attached to nothing
executable.** S5's was a telemetry disposition nobody was obliged to file; S6's
is a Claim Fidelity clause nobody is obliged to run.

The three export instances behind [#634](https://github.com/corca-ai/charness/issues/634)
are the same shape a third time, at the artifact level: charness keeps building
correct mechanisms whose ENFORCEMENT does not travel with them — a bar without
its ratchet, a budget without its runner, an installer without its contract.
Three sessions, three levels, one pattern. That is now a trend line and not an
anecdote.

## North Star Alignment

P4 — confirm through a different observer and evidence channel — is what earned
this slice. Every one of the four blockers came from an observer that was not
me, and the two I verified myself I verified by PROBE rather than by re-reading,
which is the different-channel half. The clause the north star states as "teeth
only where a wrong answer escapes" is also what the trend above indicts: this
repo is good at writing the rule and weak at giving it teeth, and a rule with no
teeth is the wrong answer escaping quietly.

## Expert Counterfactuals

**Engelbart, `system-improving-itself` — treat (H + LAM + T) as one unit.** The
briefed lens lands directly on the trend. Every improvement this session and the
last produced a correct LAM (the method: check superseded text, file the
recurring disposition, ship the ratchet with its record) and NO T (the tool that
makes skipping it visible). Engelbart's objection would not be "you skipped the
check" — it would be that a method whose only carrier is prose in a contract
file is not part of the system at all; it is a hope about the human. What he
would have done differently, concretely: when S5 recorded the "detector with no
obligation" waste, the improvement should have been a `T` — a closeout gate that
refuses a slice whose telemetry carries an unfiled `disposition: file-issue`, or
in this slice's case a pre-commit check that greps for text a scripted edit
claimed to remove. Instead both retros wrote a better sentence. The next
improvement below is deliberately a `capability`, not a `memory`, for that
reason.

**A second, divergent lens — Gary Klein, pre-mortem on the proof itself.** Klein
would not ask "is the fix right"; he would ask "assume this test passes and the
bug is still live — how did that happen?" Run against my own work that question
finds the 20-second marker in under a minute, because the only way a
process-kill test passes vacuously is a timing window. I got there by probing,
but by luck of habit rather than by a step in the workflow. The transferable
move is cheap and general: **for any test written to close a blocker, break the
fix and watch the test fail before believing it.** I did that for #633 and did
not do it for the SIGTERM test until after writing it; doing it for both, by
rule, is one command each.

## Next Improvements

- **capability** — add a repo gate that refuses a commit whose diff removes no
  occurrence of text a scripted edit claimed to supersede. Cheaper first cut:
  a `check_claimed_replacements.py` that reads a slice's declared
  superseded-string list and greps for it. This is the `T` the Engelbart lens
  says both retros owed and neither delivered.
- **workflow** — a test written to close a blocker is not accepted until the fix
  has been broken and the test observed FAILING. Applied twice this session, once
  by habit and once only after a near-miss; make it the rule, not the habit.
- **memory** — the export-completeness class is filed as
  [#634](https://github.com/corca-ai/charness/issues/634) with its three measured
  instances, so instance four is a lookup rather than a rediscovery.
- **workflow** — read `.claude/agents/<type>.md` before writing a spawn prompt
  that promises the agent a capability; two reviewers spent report space on a
  tool I told them they had and they did not.

## Sibling Search

The transferable pattern: **a correct rule, detector, or mechanism exists, and
nothing obliges or enables its use at the moment it applies.** Four axes scanned.

- **Same-file siblings** — the operating contract's Claim Fidelity clause has
  three sub-rules (assert superseded text absent; grep the OLD value when a
  number replaces a number; state the unit before the value). None has an
  executable carrier. All three are the same shape as the one that failed here.
  **Decision: fold into the `capability` improvement above** — one gate can cover
  the first two.
- **Adjacent surfaces** — `mine_closeout_telemetry.py` stamps
  `disposition: file-issue` and nothing consumes it (S5's finding, still true and
  re-measured this session at 1704 records). **Decision: already filed by S5; not
  re-filing, and noted here as the same class rather than a new one.**
- **Exported surfaces** — the three instances behind #634. **Decision: filed.**
- **Review surfaces** — the two-round critique floor IS carried by an executable
  fingerprint check and a recorded window, which is why it worked twice this
  session. **Decision: no gap; recorded as the counter-example that shows the
  pattern is fixable.**

## Portable Candidate

not portable — the specific gate is charness-internal (it keys on this repo's
closeout ledger and contract clauses). The underlying idea, "every prose rule in
an operating contract needs either a carrier or an explicit note that it has
none", is a `create-skill` candidate only after the local gate exists and has
caught something; proposing it before that would ship a rule about rules with no
carrier, which is the defect it describes.

## Lesson Evaluation

Lesson evaluation: {"score_event_count":1,"session_id":"2026-08-15-s6","status":"effect-recorded"}

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-15-session-retro-s6.md
