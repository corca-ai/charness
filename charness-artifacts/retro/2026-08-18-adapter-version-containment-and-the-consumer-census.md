# Retro: adapter version containment and the consumer census

Date: 2026-08-18

## Context

A handoff pickup that started as one named residual and became a contract change across
every adapter resolver, a consumer census gate, and an issue-closeout pass. What matters
next is that three of this session's own measurements were refuted by reviewers who could
not run anything — that is the reusable finding, not the adapter work.

## Window

`7f0d23541..fae45d9c1` — ten commits, 86 files, +3625/-237. Pushed with all broad gates
green and no `--no-verify`; three issues closed, one deliberately left open.

## Evidence Summary

- Ten commits and their stored messages; `git diff --stat` over the range.
- Behavioral probes run against temp repos for every claim: the retro/debug/quality/handoff
  gates, the gather and retro writers, the release review gate, four scaffold families,
  and the quality adapter's dotted-absence path.
- Four bounded read-only reviewer rounds (`Tools: Read, Grep, Glob`) plus one 15-agent
  workflow censusing 100 consumer files and triaging 25 open issues.
- [The closes critique](./../critique/2026-08-18-closing-four-verified-resolved-issues.md) —
  the record of what the closeout round refuted.
- Two expert counterfactual sub-agents, briefed on distinct lenses.

## Waste

- **Three of my own measurements were wrong, and all three share one generator**: the
  probe's stimulus came from my model of the mechanism rather than from the source that
  defines the claim. `#528` was probed with `deliberately_absent` as a YAML list when the
  vocabulary is a mapping, so it measured the unfixed baseline and I reported "half the
  issue is still open" to the user as a fact. `#628` was probed with `--title "a different
  cohort"` when the reported case is the scaffold run with no arguments; under the reported
  conditions one family is still broken. Round 2 found I had guarded one of two entrypoints
  causing a harm my own guard comment described in words.
- The cost was not rework — each was caught. The cost was that I told the user "verified"
  twice before a distinct observer had read anything, and one of those reports was wrong.
- Four broad-lane and standing-lane reruns paid for a flaky test that is not mine, and two
  gate registrations (timing-layer table, runner fixture stub) were discovered by failure
  rather than by reading the surface I was joining.

## Critical Decisions

- **Reversing the handoff item instead of implementing it.** The item asserted a repo fact
  that was the inverse of the truth. Measuring all 18 resolver sites rather than the two it
  named is what surfaced that, and everything else followed.
- **Building a gate instead of patching 35 files.** The census found roughly four in five
  consumers acting with no check. Patching today's list would have left tomorrow's consumer
  exactly as unclassified.
- **Not closing `#628`.** The re-measurement under the reported conditions showed one
  family still failing. Closing on my first probe would have been an irreversible wrong.

## Trends vs Last Retro

The previous retro's first improvement was recurrence-class: foreign-helper-command-in-hook
— check whether a hook-printed helper command is the target repo's own copy before running
it. That class recurred today: I ran `issue_tool.py` from the installed copy. The prose
lesson did not stop it; the provenance guard did, with an exact remedy line. One data point,
in the direction the north star already argues: the executable seam held where the sentence
did not.

## North Star Alignment

- **P4 held, and sharpened.** Every refutation this session came from an observer with
  `Read, Grep, Glob` and no execution. The north star's back-test says the operative
  variable is the CHANNEL; this session's evidence adds that the channel and the observer
  buy different things — the channel buys independence of proxy, the observer buys
  independence of PREMISE. Both refutations were premise refutations, from a reviewer that
  could not re-run my probe even if it wanted to. A Bash-equipped reviewer would likely have
  re-run my command, inherited my wrong input, and confirmed the wrong answer green.
- **P5 held.** The census gate forces a question and declares no completion; its
  `accepted-risk-unguarded` count is reported, never asserted at a value.
- **The proof-surface clause bit exactly as written.** "Authoring or changing a proof
  surface" is irreversible, and the two-round obligation found defects in the repair on both
  slices it covered — including a false rationale inside my own comment.
- **Taste, mis-applied once and caught.** The census's one-verdict-per-file shape read as a
  tie against a per-call-site shape. It is not: see Sibling Search.

## Expert Counterfactuals

**Engelbart (system improving itself)** — the tool that would have prevented this session's
expensive defect was BUILT BY it. `consumer_files()` in the census gate computes exactly the
enumeration whose absence caused rounds 1 and 2; run at step 2, before inverting the
sibling-honoring contract, it would have listed the ~100 files that read a resolved payload
and forced the question the reviewers had to discover on real CLIs. The only difference
between the preventing version and the shipped version is WHEN it is invoked. Second: the
handoff's `## Next Session` bullets assert checkable repo facts with nothing binding them —
the repo already owns the countermeasure one directory away, where an exempt row must name a
`path::function` that mechanically resolves.

**Klein / Kahneman (decision quality)** — the generator of both probe errors is that the
probe's output was read as a verdict without anything establishing that the run entered the
path under judgment. "The fix is absent" and "the fixed branch was never entered" render
identically. The repo already enforces the countermeasure on its TEST surface — a polarity
control, a mutation that must be killed — and does not enforce it on the PROBE surface,
which is what closes issues. The pre-commitment that predicts both failures: every probe
states where its stimulus came from, verbatim, and runs on the pre-fix baseline before HEAD;
if base and HEAD agree, the honest report is "this probe measured nothing".

## Sibling Search

Transferable pattern: **a probe renders a verdict without establishing it entered the path
under judgment**, and its siblings are every surface that renders a behavioral verdict.

- `quality` behavior-testing — COVERED: it carries mutation kinds, so a probe that kills no
  mutant is visibly worthless.
- `issue` closeout — NOT COVERED: the floor is presence/form and says so; nothing inspects a
  probe's INPUT. This session's instance.
- `release` publication boundary — NOT COVERED: same behavioral-verdict vocabulary, same
  absence of any stimulus-provenance requirement, on a boundary that publishes.
- `hotl` proof packets — NOT SURVEYED.

Second, narrower sibling, confirmed by reading: my own census manifest mis-classifies
`build_retro_lesson_selection_index.py` as `accepted-risk-unguarded`. It is both that AND
`no-version-validation` — `_load_yamlish_retro_paths` hand-parses `.agents/retro-adapter.yaml`
and never reconciles a version. One verdict per file cannot express it, so the row will be
paid down under the wrong remedy. The gate's own docstring names this blind class; I did not
apply it when seeding.

## Next Improvements

- workflow: every probe that will support a close, a release, or a handoff claim states its
  stimulus verbatim with provenance, and runs on the pre-fix baseline before HEAD; when base
  and HEAD agree, report "this probe measured nothing" rather than its output.
  recurrence-class: probe-stimulus-from-model-not-source
- capability: add `--impact <loader-symbol>` to the consumer census so it answers "who reads
  this producer" BEFORE a shared output contract changes, and move
  `mutate -> sync -> verify -> publish` to `enumerate-consumers -> mutate -> sync -> verify
  -> publish` for shared-producer changes.
- capability: give the census a `no-increase` seam — it prints the accepted-risk count and
  compares it to nothing, so a 38th accepted row lands green, and four of its five verdicts
  are editable by the party reporting them.
- memory: the census must express more than one defect class per file, or seed rows that
  carry two classes will be repaid wrongly. Destination: folded into the goal below.

## Lesson Evaluation

Session `2026-08-18-9ce16d03-ac24-4658-b9d4-be137caec8e6`, frozen bundle of ten lessons
presented by the session-start hook before the work.

Answering the harmful question first: **none of the ten pushed me toward a wrong action**,
and none cost a read that returned nothing. The honest negative finding is an ABSENCE — no
lesson in the list covers "probe the reported case, not a case you find convenient", which
is the class that bit three times. That gap is why this retro's first Next Improvement
carries a `recurrence-class` rather than citing an existing lesson id.

Lesson evaluation: {"score_event_count":5,"session_id":"2026-08-18-9ce16d03-ac24-4658-b9d4-be137caec8e6","status":"effect-recorded"}

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-18-adapter-version-containment-and-the-consumer-census.md
