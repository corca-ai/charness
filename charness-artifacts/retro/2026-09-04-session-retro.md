# Session Retro
Date: 2026-09-04

## Context

The 8.2.0 release session: README rewritten as the user guide; `impl` gained a
route into `debug` and a six-signal waste scan; `debug` gained "the verifier
that did fire"; `charness task run` fixed #790 and #791; the changed-line gate's
loader scan was bounded. Two user corrections mid-session exposed misses in how
I worked, and this retro is bounded to those two.

## Window

From the README history question through `v8.2.0` published, #790 and #791
closed, and the claims packet committed (`187649cb1`).

## Evidence Summary

- 20 commits on `main` since `v8.1.0` (`git log v8.1.0..HEAD`), 19 non-artifact
  paths changed (measured for the claims narrative).
- Gate failures met after the fact, in order: `test_packaging_validation`
  (bare README link), `check-docs-length` (1118 > 1000 words), ruff `I001`,
  ruff `PLR0915` (85 > 80), `release-changed-line-coverage` crash
  (`UnicodeDecodeError`), my own new test's wrong expectation, then
  `validate-skills` (debug body 205 > 200 lines) and a stale seam-risk index.
  Eight, not six as I said in chat.
- Commit `67e28cb05` landed with a failing test: the command was
  `run_standing_pytest ... | tail -1 && ruff ... && git commit`; the pipe's
  exit code is `tail`'s.
- Fresh-eye reviews: six on the skill surfaces, one code critique and one
  repair verification on the task-run change, one claims round; three
  reviewers returned `block` on first drafts. All packets are tracked under
  `charness-artifacts/critique/`.
- Debug record: `charness-artifacts/debug/2026-09-04-debug-review.md`.
- Two bounded README reviewers found three wrong install-path claims
  (marketplace file, wrapper path, PATH) and two omissions (Grok copy, state
  dir) in a README I had written from the CLI's own docstrings.
- Retro packet: rework issues since 2026-08-05 name `achieve` (2), `issue`
  (1), `retro` (1); none names `impl` or `debug`.
- No metrics commands are configured; efficiency claims here are narrative.

## Waste

- **Eight gate failures handled one at a time, each as its own surprise.** I
  wrote, ran a narrow check, committed, and let the next lane tell me the next
  thing. The class was visible by the third: I was not running the gate that
  would judge the change before making the change. The fix that ended it was
  running the exact release lane locally before the publish helper.
  (recurrence-class: gate-failures-patched-serially)
- **A verification exit code swallowed by a shell pipe.** `pytest | tail -1`
  inside an `&&` chain reports `tail`'s success, so a failing test committed.
  The habit that produced it — trimming tool output for my own context — is
  reasonable; putting the trim *inside* the chain that decides to commit is
  not. Nothing in the repo holds this rule.
  (recurrence-class: verification-exit-masked-by-pipe)
- **A red gate read as a red subject.** The coverage gate crashed on a fixture
  and I fixed the read, then patched the test I wrote for it, before asking
  whether the gate's walk was right in scope. It was not: a root-level changed
  path turned "same-directory" into a whole-repo `rglob`. The user had to say
  "the verifier is suspect too" before that question was asked.
  (recurrence-class: red-gate-is-a-candidate-cause)
- **A prepared release superseded mid-flight.** The 8.1.1 prepared commit and
  its claims record were dropped by rebase when #790/#791 joined the release.
  Not waste in outcome (nothing was pushed) but two reviewer rounds and one
  claims round were spent on a record that never shipped.

## Critical Decisions

- Route the repeated-failure rule into `impl` (read every slice) rather than a
  host hook or the goal body — chosen after finding the retired `find-skills`
  path and the line this repo drew between deterministic advisories and
  inferred ones.
- Put "the verifier that did fire" in `references/detection-gap.md` because
  the debug body was already at its 200-line cap; the cap is P2's signal that
  `debug` carries more than one concept, and that is recorded, not shaved.
- Bump 8.2.0 minor, not 8.1.1 patch, once the task-run receipt fields joined.
- Close #790/#791 by comment rather than the helper's closeout ledger; stated
  in the comments.

## North Star Alignment

- **P1 held** in the design: the debug route is a principle with an observable
  test (a cause that predicts a disproving observation), not a counter or a
  hook, after two reviewers showed the first draft would fire on ordinary loops.
- **P3 was inverted, then corrected.** The first draft justified its list by
  arguing against P3 inside the skill body; the operator's observed non-recall
  is the exception P3 names, and the list stayed while the argument left.
- **P4 mis-applied by me on my own work.** A release lane is a claim; I read
  the first `exit 0` of the full read-only lane as clearance for the release
  lane, which runs a different gate set. The exact lane, run locally before the
  helper, was the distinct channel I skipped twice.
- **Named signature: terminal trust at a proxy.** `| tail -1` made a pipe's
  exit code the verdict, and I committed on it. The Diagnosis section's failure
  is a green treated as proof; this was a green that was not even the gate's.
- **Documentation as code held:** every rule change landed in the surface an
  agent reads (`impl`, `debug`, `detection-gap.md`, `agent-task-runs.md`), and
  `README` claims were checked against `init.sh` and the CLI by observers other
  than the author.

## Trends vs Last Retro

- Last retro (goal #784 closeout) reported 0 push refusals in-session; this
  session had 0 push refusals but 2 publish-helper refusals before the tag
  (critique binding, then the lane crash), and one denied command.
- Last retro's improvements were capability-first (a budget bound); this one
  is workflow-first: the misses were in how I verified, not in the tools.
- Active lesson classes: 63 in the index; this retro tags 3 new ones.

## Expert Counterfactuals

- **Engelbart (system-improving-itself):** the two corrections changed the
  method (LAM) — impl's route, debug's verifier rule — but only one changed a
  tool (T): the gate's bounded walk. The pipe-masking miss has a method note
  and no tool. The system-improving move is to make the runner the only thing
  that reports a verification verdict: `run_standing_pytest.py` already writes
  a run record (`--print-last-run`); a session that reads that record, never
  the pipe, cannot be fooled by `tail`. That is a habit until the record is
  what the commit hook asks for.
- **Gary Klein (premortem, decision quality):** before the first publish
  attempt the question "if the release lane fails, what in this delta is
  unusual?" had one obvious answer — a root-level file changed — and the
  release-only gate that walks from a changed path's parent would have been
  named before it crashed. The premortem costs one sentence; the crash cost a
  lane, a debug record, and two commits.

## Next Improvements

- workflow: run the exact lane the boundary will run (`--release --read-only`
  before the publish helper), and never place a verification command behind a
  pipe inside the chain that commits — capture to a file, check the exit,
  then read the file. Structural pattern: a proxy's exit code standing in for
  the verifier's. Triggering instance(s): commit `67e28cb05`; the
  8.2.0 first publish attempt. Destination: repo-local guard candidate — a
  runner-owned verdict record read by the commit hook — filed only if the
  class recurs. (recurrence-class: verification-exit-masked-by-pipe)
- capability: applied — `impl` routes a repeated unexplained failure to
  `debug`; `debug/references/detection-gap.md` owns "the verifier that did
  fire" with the `scope-too-broad | verifier-defect | subject-defect`
  vocabulary; the changed-line gate's walk is bounded at the root.
  (recurrence-class: red-gate-is-a-candidate-cause)
- memory: this record, so the three classes reach the next session's
  selection preview; `gate-failures-patched-serially` is the class the impl
  route exists to end, and the next retro should say whether it fired.
  (recurrence-class: gate-failures-patched-serially)

## Sibling Search

- Mental model: a verdict read from something other than the verifier — a
  pipe's exit, a different lane's green, a gate's own crash log.
- same layer: every `&&` chain in this session that ended in `git commit` |
  decision: same waste, fix now | proof: the later commits captured to a file
  and echoed `$?` before committing
- abstraction up: the full read-only lane standing in for the release lane |
  decision: same waste, fix now | proof: the release lane run standalone
  before the second publish attempt (88 passed)
- specialization down: `run_standing_pytest.py --print-last-run` as the
  verdict source instead of stdout | decision: valid follow-up outside the
  slice | proof: the record exists and was not read this session |
  follow-up: deferred docs/development.md#verification-and-export (the
  mechanisms table row this rule would need)
- mental-model siblings: `scripts/gates/check_prose_pin.py:132` guards
  decoding where the coverage scan did not | decision: intentional boundary |
  proof: no other `rglob("*.py")` in `scripts/`/`tools/` starts at a root
  that can reach `native/`

## Persisted

Persisted: yes: charness-artifacts/retro/2026-09-04-session-retro.md
Seeding: 3 class(es) seeded

## Packet Consumed

Packet Consumed: charness-artifacts/retro/2026-09-04-003829-packet.md
