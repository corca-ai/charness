# Three Release Residues, and Two Caches Nobody Bounded

Date: 2026-08-13
Scope: session

## Context

The handoff's Next Session named four items: resolve #613, then #610 and #611,
leave #584 held, and act on the `skipped-is-not-passed` lesson. All four are done
and pushed. This is the THIRD retro dated 2026-08-13; `2026-08-13-session-retro.md`
and `2026-08-13-proof-surface-repair-retro.md` cover different sessions and neither
is superseded.

What matters next is that the push took five attempts, and only the last failure
was a real gate finding about this diff — the other four were environment and
operator error that presented as flaky tests.

## Window

Start: the `docs/handoff.md` pickup naming #613/#610/#611.
End: `bfbc8f4d` pushed with remote CI green on both jobs, three issues verified
`CLOSED` through `verify-closeout` and reconciled against an independent
`gh issue list` (15 open). Commits: `29751f0d`, `abf207fc`, `503545d7`, `2eaa887b`,
`e455c338`, `ceae9e48`, `d315d989`, `9278c333`, `bfbc8f4d`.

## Evidence Summary

- Two-round critique
  `../critique/2026-08-13-release-claims-path-record-and-notes-two-round-critique.md`;
  six bounded reviewers over two windows, both `reviewer_boundary_fingerprint.py`
  verifies `clean` at exit 0 with empty `parent_declared`, run before any fold.
- `run_standing_pytest.py` 8959 passed; the release/pointer/narrative/mirror/
  packaging sweep 773 passed; `prepush_focused_changed_line_coverage.py` `clean`
  on the committed tree; pre-push gate 91 passed 0 failed on the successful push.
- Per-issue behavioral verdicts driven against the EXPORTED plugin copies under
  `plugins/charness/skills/release/scripts/`, a channel distinct from the
  source-tree fix, the test suite, and `CLOSED`.
- Direct git probes for three claims the reviewers could not run: `git show HEAD:a//b`
  exits 128, `git diff --quiet -- <nonmatching>` exits 0, `git add -- <absent> <present>`
  exits 128.
- Measured cache sizes: `test-seeds` 1850 entries / 1.1 TB; `pytest-tmp` 181 keys /
  5.5 GB; `/home` 97% before, 34% after.

## Waste

- **Four failed pushes, ~45 minutes of gate time, from two causes that both
  masquerade as flaky tests.** Run 1 was the seed cache filling the disk; runs 2–4
  were my own `git -c core.hooksPath=.githooks` leaking `GIT_CONFIG_PARAMETERS`
  into every descendant, so each fixture's temp repo inherited a relative
  `.githooks` that does not exist there. Both produce a DIFFERENT failing set each
  run, and both pass when the named files are re-run in isolation — the exact
  signature that sends you hunting a flaky test.
- **I misattributed run 2 to disk pressure and told the user so.** Run 3 refuted it
  (34% disk, same file failing). The disk finding was real but it was not the cause
  of runs 2–4, and I stated the attribution before I had a second observation to
  separate them.
- **The `-c core.hooksPath=.githooks` flag was redundant from the first commit.**
  `git config --local core.hooksPath` already returns `.githooks`. I carried a
  flag I never checked was needed, and it was the thing breaking the gate.
- **Three validator round-trips on the carrier bodies**, one of them the exact
  line-anchored ledger-field trap the LAST retro recorded as a memory lesson:
  `Decision:` at the start of a wrapped line terminated the `Siblings:` field. I
  had read that lesson this session and still hit it.
- **`main` went red after the push, on the same job as last session.** The local
  focused changed-line lane reported `clean`; CI's broad mirror blocked on five lines
  in the classifier module. An independent `coverage json` read agreed with CI, so the
  LOCAL verdict was the wrong one — and that lane's own docstring says it "can never
  report an uncovered line as covered". Filed as #615; the five lines are covered and
  `bfbc8f4d` is green.
- **My first fix for those lines passed its assertions while testing the wrong arm.**
  An older `rev-list` branch in the test stub shadowed the new parent listing, so
  `claims_evidence_child` returned `""` and the scenario fell through to a later arm
  that produces an identical observable result. `24 passed` did not catch it;
  line-level coverage showing 131 executed and 132-134 not is what did.
- Not waste: the six reviewer spawns. Round 2 found a defect inside a round-1
  repair on all three surfaces — including a gate that committed the file it was
  about to refuse.

## Critical Decisions

- **Replace the mitigation instead of deleting it (#613).** Round 1 established
  that removing `assert_record_path_matches_adapter` with nothing in its place
  turns every derivation failure back into a silent miss. The replacement asks
  positively — is the record readable at the derived path — which covers a strictly
  wider trigger set than the value comparison it replaces, including the case the
  old check could never see: an adapter edited between prepare and resume.
- **Do not normalize `output_dir` on the floor side.** Round 2 caught that my
  `.strip()` was itself the two-derivations class. Normalization applied on one side
  only is how the floor and the writer come to name different files, so the value is
  now passed through unchanged and `""` derives the repo root exactly as the writer
  does.
- **Fix the cache cause before deleting 1.1 TB**, at the user's direction. I had
  proposed deleting first; the user was right that the cause had to go first, and
  `SEED_CACHE_KEEP = 3` turned out to match the original intent for that cache.
- **Leave three round-2 findings unfixed and say so.** The legacy marker-free lane,
  the adapter-declared review-unavailability patterns, and the notes-file naming
  heuristic are all recorded in the critique's Counterweight Pass rather than
  repaired at the round-2 cap.

## Trends vs Last Retro

The last retro's headline was *round 2 finds a defect inside every round-1 repair*.
That held again, 3 for 3, and the class was the same shape one level in: a repair
that carries the class it fixes (the strip), and a guard placed where firing it
creates the state it refuses.

Its `skipped-is-not-passed` lesson also paid for itself twice — a broad pytest run
that died on an unrecognized flag and still reported exit 0, and the changed-line
gate reporting `unestablished` over uncommitted files. Both would have been read as
green. The lesson was in the index but ranked 11th and never reached
recent-lessons' four slots, which is why it moved to the operating contract.

The new trend is different in kind: most of this session's waste was in the
ENVIRONMENT — an unbounded cache and a leaked git flag — which no gate the repo owns
can see. But the tail repeated last session's exact shape: local green, CI red, same
job. Last session the local lane had SKIPPED the check; this time it RAN it and
answered `clean` when the answer was `blocked`. That is worse, and it is why #615
exists rather than another entry in the skipped-is-not-passed class.

## North Star Alignment

P4/P5 held at each irreversible boundary. Three issue closes each carry a
behavioral verdict through the exported plugin copy — distinct from the fix, the
tests, and `CLOSED` — plus a `verify-closeout` readback reconciled against an
independent `gh issue list`. The push was granted per phase, and the release
boundary stayed untouched.

The place the north star was nearly bent is my run-2 attribution: I named a cause
from one observation, which is the same "confident verdict on evidence that cannot
discriminate" shape the repo's proof-surface rules exist to stop. The correction
came from a second observation, not from noticing the gap first.

## Expert Counterfactuals

**Douglas Engelbart — design Tool, Language, and Method together.** The seed cache
is a Tool with a Method nobody wrote: it was built to make the suite fast and the
question "when does an entry stop being worth keeping" was never asked, so the
answer defaulted to never. The repo already KNOWS the rule — `slice_closeout_broad_gate.py`
caps its records at `[-19:]` — so this is not missing knowledge, it is knowledge
that lives in one file instead of in the language of the system. The
system-improving move is not "bound this cache"; it is that any code writing under a
cache root should have to state its retention, the way any new proof surface has to
state its fresh-eye pass. `pytest-tmp` is the proof that fixing one instance is not
the same as fixing the class.

**Falsification-first operator lens.** Both push blockers were diagnosable by one
question I did not ask: *what is different between the run that passes and the run
that fails?* The named files passed in isolation and failed under the gate — that
differential IS the finding, and it points at the environment, not the tests. I
instead reached for the most recently discovered cause (the disk) and applied it to
a second, unrelated failure. The next move is to treat "passes in isolation, fails
in the harness" as a signal about the harness by default, and to require a second
discriminating observation before naming a cause out loud.

## Next Improvements

- **workflow**: when a failure passes in isolation but fails under the full gate,
  diff the ENVIRONMENT first — inherited git config (`GIT_CONFIG_PARAMETERS` from
  any `git -c`), HOME, cwd, disk — before reading the test. Both of this session's
  push blockers were environment, and both read as flaky tests.
  (recurrence-class: harness-differential-not-test)
- **workflow**: do not carry a flag you have not confirmed is needed.
  `git -c core.hooksPath=.githooks` was redundant against the local config from the
  first commit and was the thing breaking the gate for three runs.
  (recurrence-class: unchecked-redundant-flag)
- **capability**: anything that writes under a cache root states its retention.
  Two of the repo's caches had none and one reached 1.1 TB; a third
  (`slice_closeout_broad_gate`) shows the rule is already understood here. Tracked
  as #614.
  (recurrence-class: unbounded-cache)
- **memory**: state a cause only after a second observation that discriminates it.
  I named disk pressure for run 2 from one data point; run 3 refuted it at 34% disk.
  (recurrence-class: cause-named-from-one-observation)
- **workflow**: when adding tests to satisfy a coverage gate, verify by MEASURING the
  named lines, not by the test passing. Both attempts here passed; only the coverage
  read distinguished the one that exercised the intended branch from the one that
  silently matched a different arm with an identical result.
  (recurrence-class: green-test-is-not-covered-line)

## Sibling Search

- same layer: `~/.cache/charness/pytest-tmp` | decision: same waste, not fixed here
  | proof: `run_standing_pytest.py:355` rmtree's the basetemp only when
  `returncode == 0`, so failing runs retain theirs — deliberately, for inspection —
  and nothing evicts old repo-path keys; 181 keys, 5.5 GB, 1/11/109/60 per month
  May→August. Recorded on #614 with the direction that differs from the seed cache
  (keep the most recent N failed basetemps rather than clean up on failure).
- abstraction up: `reports/mutation` 2.2 GB and `.charness/reviewer-boundary` 12 MB
  / `.charness/usage-episodes` 8.7 MB | decision: same class, currently small |
  proof: gitignored and no eviction found by grep; named on #614 rather than
  repaired.
- specialization down: `slice_closeout_broad_gate.py:255` `records[-19:]` |
  decision: intentional boundary and the counter-example | proof: an explicit cap
  already exists in this repo, which is why #614 is framed as a rule that was not
  applied rather than a rule nobody knew.
- mental-model siblings: the `GIT_CONFIG_PARAMETERS` leak | decision: operator
  error, not a repo defect, but a cheap repo-side guard exists | proof: proven
  directly — a hook run under `git -c core.hooksPath=X` sees
  `GIT_CONFIG_PARAMETERS='core.hooksPath=X'` and it applies inside an unrelated
  repo. A pre-push hook could scrub it before running tests. Not filed; raised for
  the user's decision.

- mental-model siblings: the focused changed-line lane's `clean` verdict | decision:
  same class as the caches — a surface asserting a property it does not hold —
  escalated rather than repaired | proof: its docstring promises it can never report
  an uncovered line as covered, and an independent `coverage json` read showed it did;
  filed as #615 with the deterministic reproduction, because the cause (stale reuse vs
  `include_paths` narrowing vs xdist worker coverage) is not established.

Structural-follow-up destination: applied: the seed cache is bounded with seven
tests and the live cache pruned 1848 entries; tracked issues: #614 for `pytest-tmp`,
`reports/mutation`, and the retention rule as a class; #615 for the focused
changed-line lane's false `clean`.

## Portable Candidate

not portable — the seed-cache bound is specific to this repo's test fixtures, and
the `GIT_CONFIG_PARAMETERS` lesson is an operator habit rather than a capability a
consuming repo would install.

## Packet Consumed

none — continued from `docs/handoff.md` Next Session, not a prepared packet.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-13-release-residues-and-unbounded-caches-retro.md
