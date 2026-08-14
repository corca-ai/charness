# Closeout 618 628 Release Prep Retro
Date: 2026-08-14

## Context

A pickup that read "run the `issue` closeout floor on two landed cohorts" and
ended as: ten issues carrying published closeout evidence and still open, two
defects repaired inside the fixes being closed out, a release probe pair made
honest, a 20-commit push, and a prepared release blocked on a scope decision the
owner made mid-session. Seven bounded reviewers ran across three rounds plus a
pre-release critique.

## Evidence Summary

- Ten issues read through the backend, eleven comments published and read back;
  all remain OPEN by decision (`skills/public/issue/SKILL.md:102` refuses a close
  before the carrier is published).
- Three review rounds on the closeout slice, two blockers found in round 2 and
  two more in round 3; one round-3 blocker was a regression this session had
  introduced while repairing the same class.
- Pre-release critique returned DO-NOT-PUBLISH with four false claims, every one
  in the release notes rather than in the code.
- Four push attempts, each refused for a different real reason; `origin/main` is
  `0a1a53405`, verified by `git ls-remote` rather than by hook output.
- 35 changed lines had no test; closing them took two delegated agents and two
  self-authored passes.

## Waste

The largest single cost was trusting a description instead of reading the
source, and it recurred in three shapes. #608 was carried as the release blocker
by the handoff and by an open issue; it had been fixed on 2026-08-13 and only
needed closing, which a subagent found in its first minutes. The `--json`
survivor count was accepted from a reviewer's string grep and published without
checking whether the matches were flag declarations or `gh --json` call sites.
A 2026-04-22 spec line blessing `--json` was cited as live policy when the
owner's standing decision had superseded it.

Second cost: briefing a worktree-isolated agent against a vocabulary its tree
did not contain. `isolation: worktree` branches from `origin/main`, and this
session's work was 18 unpushed commits ahead, so the brief described contracts
that did not exist there. The agent reported the mismatch rather than forcing
the brief, which is the only reason it landed coherent.

Third: a test written to prevent recurrence would have passed on the very defect
it was named after, because its path check was cwd-relative. A round-2 review
caught it.

## Critical Decisions

- Not closing the ten issues. Every gate would have gone green on a
  `manual-fallback` close, and the repo's own precedent from one day earlier said
  an issue stays open until its carrier is pushed. The decision to run the floor
  and publish evidence WITHOUT closing is what made the rest of the session
  honest.
- Reverting the empty-key acceptance instead of keeping it. It made a broad-gate
  failure go away, its justification was false, and it converted a loud exit 3
  into exit 0 for a config an author had plainly declared.
- Not using `--no-verify` on any of four refused pushes. The contract revokes the
  release grant for it, and the refusals were all real.

## North Star Alignment

P4 held and was load-bearing: a passing gate is a claim, not a conclusion. It
fired most sharply where the gates were green and the claims were false — four
published sentences, an exemption rationale, and a module docstring, none of
which any automated check could see. The facet that did NOT hold on its own is
the same one: nothing in the toolchain distinguishes a true sentence from a
plausible one, so every instance was caught by a reader, and three of the seven
readers were needed to catch what the first two missed.

## Expert Counterfactuals

- Feynman ("the first principle is that you must not fool yourself"): the
  cheapest correction available all session was `git show` and `sed -n` on the
  file under discussion. Every false claim died to one of those two commands.
  A rule of "read the line before describing it" would have removed three of the
  four published errors at zero review cost.
- A release manager's lens: the pre-release critique found no code defect and
  four record defects. That ratio argues the release record deserves the same
  adversarial treatment as the code, which this repo currently gives it only at
  the claims round.

## Sibling Search

- axis: generator produces a shape its own gate cannot see | location:
  `scripts/check_docs_graph.py` | decision: valid follow-up outside the slice |
  proof: `awiki lint -root docs` exits 1 with `link_only_lines=196` while the gate
  reads only `orphans`/`islands` and discards the exit code, and the handoff
  scaffold teaches the bare-link shape that consumers then get linted on |
  follow-up: deferred to #629 and to the handoff's Next Session item 3, which
  names both halves because fixing only the generator lets the count regress
  silently

## Lesson Evaluation

Lesson evaluation: {"score_event_count":1,"session_id":"2026-08-14-closeout-618-628","status":"effect-recorded"}

One score, and the reason the count is not four. `premise-not-checked-against-source`
is scored `-2`: it was presented before the work, read, and still missed three
times. Three others measurably changed an action — `artifact-contract-late-feedback`
(the enforced shapes were rendered before authoring, not discovered by a refusal),
`bar-recorded-as-prose` (cited by name when the worktree ignore line got a test),
and `proof-surface-review-binding` (the broad lane ran before every review
binding, and caught a regression the focused suites missed). None could be
recorded: `lesson_ledger_lib.py:375` accepts a score only when the citing retro
carries a recurrence tag for that lesson, so scoring a lesson that WORKED requires
declaring it as a recurrence. Rather than write three false recurrences
to make a count go up, they are named here and left unscored — which is the
ledger's own `no_score_is_valid` rule, reached for a reason it does not yet cover.

## Next Improvements

- **workflow** (recurrence-class: premise-not-checked-against-source): before
  describing any surface in a published artifact — release notes, issue comment,
  exemption rationale, docstring — open the file and read the line. Three of this
  session's four false published claims were one `sed -n` away from never existing.
- **capability** (recurrence-class: isolated-agent-base-mismatch): a
  worktree-isolated subagent branches from the default branch, not from the
  parent's HEAD. Brief it against that base, hand it the diff, or do not isolate
  it. Name the base ref in every isolated brief.
- **capability** (recurrence-class: positive-effect-cannot-be-cited): the ledger
  can record that a lesson failed but not that one worked, because a score's
  citation requires the citing retro to tag that lesson as recurring. That biases
  the corpus toward negatives and leaves "this lesson is doing its job" invisible
  to the lifecycle review that decides what to graduate.
- **memory** (recurrence-class: superseded-line-stays-quotable): a retired
  convention stays quotable until its line is deleted. When a decision supersedes
  a spec sentence, retire the sentence in the same slice —
  `cli-command-flag-conventions.md:27` outlived its decision and misled a session
  that cited it in good faith.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-14-closeout-618-628-release-prep.md
