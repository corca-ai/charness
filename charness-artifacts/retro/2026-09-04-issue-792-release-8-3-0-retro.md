# Session Retro: #792 dependency reuse and the 8.3.0 release

Date: 2026-09-04

## Context

One work unit: issue #792 (every `task run` lane paid a full `npm ci`) was
designed, implemented, reviewed, released as charness 8.3.0, and closed in a
single session, with a source-of-truth audit of the worktree subsystem folded
in at the operator's request. What matters next is the cost shape of that
session: the feature took about an hour; the proof took the other two.

## Window

From reading #792 (00:41 UTC) through `v8.3.0` public, #792 closed, #793 and
#794 filed, and the claims packet pushed (03:35 UTC).

## Evidence Summary

- 21 commits on `main` since `e191e89d4`; 8 of them are critique or claims
  records rather than code (`git log e191e89d4..HEAD`).
- Session probe (`probe_host_logs.py`, this session's JSONL): 253 tool calls,
  479 assistant messages, 518k output tokens over 2h54m. Turn pairing is
  heuristic; token and call counts are measured.
- Nine file-backed code reviews plus one surface review and two claims rounds,
  all tracked under `charness-artifacts/critique/`; every round's verdict and
  findings identity are in
  `charness-artifacts/critique/2026-09-04-worktree-dependency-reuse-792-release-8-3-0-critique.md`.
- Release lane failures met in order: `test_subprocess_form_gate`,
  `check-python-lengths` (two files), `validate-skill-ergonomics`,
  `validate-attention-state-visibility` (twice: undeclared term, then a
  declaration that did not move with the code), `release-changed-line-coverage`,
  and the two critique-artifact validators on the unfinished record. Seven
  distinct gate stops, each met after the change that tripped it.
- Live proof: `worktree create --prepare` on this ext4 host links the parent in
  164 to 389 ms across five runs; the pre-declaration run took the full install.
- Retro packet consumed: `charness-artifacts/retro/2026-09-04-033546-packet.md`
  (rework issues since 2026-08-05 name `achieve` 2, `issue` 1, `retro` 1; none
  names `impl`, `critique`, or `release`).
- No metrics commands are configured beyond the host-log probe; efficiency
  claims below are measured counts plus narrative, not a cost model.

## Waste

- **Seven gate stops met one at a time, again.** The last retro's first lesson
  was exactly this class, and I read it in the ledger preview at session
  start. I still ran the full release lane only after the first reviewer round
  instead of before the first commit, and then kept editing after each green.
  The lane costs 3 to 6 minutes; I ran it six times. The fix that would have
  ended it is the one the lesson already named: run the exact release lane
  before the first commit of a slice, and treat every later edit as a new
  slice that owes the lane again. (recurrence-class: gate-failures-patched-serially)
- **Nine code-review rounds where a design would have been one.** Rounds 3
  through 8 each moved the cache key's identity one notch: digest and
  directory, then platform and architecture, then tool and node versions, then
  fail-closed on unknown, then one observation per operation, then observed in
  the worktree. Each reviewer found the next notch on content the previous one
  had passed. The identity of a cache entry ("what must be equal for two trees
  to be interchangeable") was never written down before code; the reviewers
  wrote it for me, one clause per round, at five minutes and one commit each.
  (recurrence-class: boundary-identity-unbound)
- **A review packet that named its range as `HEAD`.** `run_review.py --range
  e191e89d4..HEAD` stored the symbolic range; the artifact validator re-resolves
  it at validation time, so the record went stale the moment its own commit
  landed. One full reviewer round (round 8) existed only to re-read identical
  content on a pinned range, and it happened to find a real defect, which
  masks the waste rather than excusing it.
  (recurrence-class: review-packet-range-not-pinned)
- **The unfinished record sat in the tree the reviewer read.** Reviewer 5
  blocked partly on the critique record's own TODOs, and the lane's two
  artifact validators failed twice on it. Holding the record out of the tree
  during rounds 6 to 9 was a manual `mv` each time.
  (recurrence-class: unfinished-record-in-reviewed-tree)
- **A bounded subagent spent 19 minutes idle before reporting.** The SoT audit
  agent went idle without a report; I repeated the audit in the parent, and its
  report arrived afterwards with four findings beyond mine. Not waste in
  outcome, but the host note that such spawns are not budgetable proof held
  again, and I had no way to ask it for its result.

## Critical Decisions

- Own the reuse in worktree preparation, not in `task run`: prepare links, the
  manifest opts in, `task run` only names the shared cache root. Every reviewer
  round stayed inside one module because of this.
- Reset the prepared release commit to fix one false sentence in the critique
  record rather than amend or comment around it. Cost: one 6-minute re-prepare.
  Benefit: the claims record binds to a record with no known-false sentence.
- File the SoT drift (#793) and the hooks-path defect (#794) instead of widening
  the release; fix only the false sentence the release itself had touched.
- Fail closed on unknown runtime identity for the cache, accepting that a repo
  whose install tool cannot answer `--version` gets no cache, rather than a
  cache that can lie.

## Trends vs Last Retro

- The last retro (this morning, 8.2.0) named `gate-failures-patched-serially`
  with eight instances; this session produced seven. The lesson was read and
  not applied. Its proposed guard (a runner-owned verdict record the commit
  hook reads) was deferred "until the class recurs"; it has recurred within
  the same day.
- The last retro's `red-gate-is-a-candidate-cause` did not recur: every gate
  stop this session was a subject defect, and I checked each one against its
  log before editing.
- `harness-differential-not-test` did not fire; no environment divergence.
- `verification-exit-masked-by-pipe` did not recur: every commit chain checked
  the runner's exit, and the lanes wrote their verdict to a file I read.

## North Star Alignment

- **P4 held at the release boundary.** The claims round had a distinct
  observer, it found a false sentence four code rounds and a docs gate had
  missed, and publication waited on the corrected bytes.
- **P5 held.** The prepared record was the stop; the tag moved only after the
  claims record was committed as its child.
- **P2 held under pressure.** Two files crossed the 480-line cap; the split
  (prepare out of doctor) followed the concept boundary rather than shaving
  lines. The docs page was trimmed to its ratchet by displacing prose, not by
  cutting the new contract.
- **P1 was over-applied to the reviewer loop.** I treated each `block` as a
  reversible edit and re-reviewed, nine times, instead of stopping after round
  3 to write the identity contract the reviewers were converging on. The
  failure signature is "count is not the metric": nine rounds read as
  thoroughness, but the same escape would have closed in two with the design
  written first.
- **Named signature walked into: terminal trust at a green lane.** After the
  first full green I kept committing on focused tests, which is exactly the
  proxy the last retro warned about.

## Expert Counterfactuals

- **Douglas Engelbart (system-improving-itself).** Two of this session's four
  waste classes are properties of the tool (T), not the method: a packet that
  stores `HEAD` instead of the resolved sha, and a reviewer that can see the
  record being written about it. Both were paid manually (a ninth round; a
  `mv` per round). The system-improving move is to change T: `run_review.py`
  resolves `--range` to shas before it writes the packet, and offers a
  hold-out for artifacts the review will produce. Designing T alongside the
  method turns two recurring manual steps into none.
- **John Ousterhout (design it twice, define the interface first).** The cache
  entry is an interface between lanes across time; its identity is the whole
  design. Writing "two trees are interchangeable when lockfile, directory,
  platform, architecture, install-tool version, node ABI, and the observing
  cwd agree" as one sentence before the first commit would have made rounds 3
  to 8 a single review of that sentence. The counterfactual next move is a
  ten-line identity note in the spec artifact before code for any cache,
  fingerprint, or key.

## Sibling Search

- same layer: `skills/public/critique/scripts/run_review.py` `--range` and
  `--commit` both store the operator's ref text | decision: valid follow-up
  outside the slice | proof: `release-8-3-0-code-7-packet.json` carries
  `changed_ref: e191e89d4..HEAD` beside a resolved sha pair the validator
  ignores | follow-up: https://github.com/corca-ai/charness/issues/795
- abstraction up: every packet-bound artifact validator that re-derives a
  reviewed set from a stored ref (`scripts/review/reviewed_input_identity.py`)
  | decision: same waste, fix now candidate is the same issue; the validator
  could prefer `resolved_changed_ref` | proof: the mismatch message names the
  re-derived set | follow-up: https://github.com/corca-ai/charness/issues/795
- specialization down: the release claims round uses working-tree mode with
  explicit paths and does not carry a ref | decision: intentional boundary |
  proof: `release-8-3-0-claims-2-packet.json` has `changed_ref: null`
- mental-model siblings: the release critique record must cite a worker report
  with `approval_eligible: true`, so the final reviewer can never have read
  the final record; the record-after-review ordering is inherent, and the
  hold-out is the mechanism the tool lacks | decision: valid follow-up outside
  the slice | proof: rounds 6 to 9 each moved the record aside by hand |
  follow-up: https://github.com/corca-ai/charness/issues/795

## Next Improvements

- workflow: before the first commit of a slice, run the exact release lane
  (`./scripts/run-quality.sh --full --release --read-only`), and after every
  reviewer-driven edit treat the slice as reopened and owe the lane again
  before the next review; the focused suite is a proxy. Structural pattern: a
  green from a narrower lane standing in for the boundary's lane. Triggering
  instance(s): seven gate stops this session; eight in the 8.2.0 session.
  Destination: repo-local guard — the last retro's runner-owned verdict record
  read by the commit hook, now filed as
  https://github.com/corca-ai/charness/issues/796 (recurs:).
  (recurrence-class: gate-failures-patched-serially)
- workflow: for any cache, key, or fingerprint, write the identity sentence
  ("two X are interchangeable when ...") in the spec artifact before code, and
  ask the first reviewer to attack that sentence rather than the code.
  Destination: none — a habit, held by the `boundary-identity-unbound` lesson.
  (recurrence-class: boundary-identity-unbound)
- capability: `run_review.py` resolves a symbolic `--range`/`--commit` to shas
  before writing the packet, and accepts a `--hold-out <path>` that moves a
  named artifact aside for the reviewer's run and restores it after.
  Destination: https://github.com/corca-ai/charness/issues/795 (novel:).
  (recurrence-class: review-packet-range-not-pinned)
  (recurrence-class: unfinished-record-in-reviewed-tree)
- memory: this artifact; the ledger seeds the two new classes and re-scores the
  two recurring ones.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-09-04-issue-792-release-8-3-0-retro.md
Seeding: 2 class(es) seeded
