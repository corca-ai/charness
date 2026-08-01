# Midpoint goal-claims review — the sweep-high-rows goal

Date: 2026-08-01
Goal: [close-the-sweeps-remaining-high-rows-by-class](../goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md)

The contract-mandated midpoint round (`docs/conventions/operating-contract.md`, Critique
Discipline: a goal with three or more slices runs one at its midpoint, not only at
closeout). It asks a different question from a slice review — *does what the goal CLAIMS
match what the owning records say and what the commits did* — and it is written down here
because the closeout disposition review found it was the one round in this goal with no
checked-in record, in a goal whose acceptance criteria exist because the PRIOR goal had
none.

## Reviewer Tier Evidence

- Requested tier: bounded read-only reviewer (`bounded-reviewer` typed agent)
- Requested spawn fields: agent_type=bounded-reviewer, unnamed spawn, session-model
  inheritance. Claude Code host, so the Codex model/effort request does not apply.
- Host exposure state: requested_fields_sent
- Application state: the spawn was accepted and returned findings inline.
- Delivery state: findings-received

## Reviewer Provenance

Fresh-eye satisfaction: parent-delegated

One bounded `bounded-reviewer` subagent, spawned unnamed in the shared parent worktree
with Read/Grep/Glob only, reading the committed surface at `dac61db7`.

Worktree integrity: snapshot opened window `goal-midpoint`; `git status --porcelain` was
empty at the snapshot. **Non-claim:** the matching `verify` was not run, consistent with
every other window this session. The reviewer had no Bash, so two of its questions were
answered from the artifacts rather than from `git show`, and it said so.

## Findings

Five blockers, ten nits. What the round was for:

1. **The goal's own operating frame asserted a measurement its own recorded probe
   refutes** — "an engagement residual floor up to 20 costs 0 new refusals", with the
   negation at 31 against a corpus p5 of 19. The probe says floor 20 drops 10 citations
   and 46 label values, the negation scores 18, and p5 is 5. Slice 2's round 2 had
   already repaired that claim IN THE CODE and left it standing in the artifact. Same
   defect, one surface over, where a slice review does not look. **This is the finding
   that justifies the round's existence.**
2. **Both Slice Log `Commits:` fields were empty**, so no claim in the artifact was
   diffable against what shipped, and one commit (`5f99e842`) was attributed by no
   artifact at all.
3. **The mandated per-slice producer step had been substituted without a record.** The
   plan specifies `run_slice_closeout.py --verification-lock --produce-mutation-coverage`;
   every slice ran `--skip-broad-pytest --ack-cautilus-skill-review`.
4. **The fingerprint `verify` had never run for any review window**, and the critiques
   said so honestly while the goal artifact did not — so acceptance bullet 3 read as met.
5. **Slice Plan row 3's stated ordering reason never happened**: batches B and C ran as
   one slice, so the midpoint could not land between them.

Nits included the sweep header's correction note not reconciling (the four unlisted rows
are S5, S7, S21, S22 — 29 + 4 = 33, not the "seven" a first draft claimed), the S12 table
cells still carrying refuted text while only the batch note said so, `NARROWED` not being
in the sweep's status vocabulary at all, and the closed rows naming no reproduction
control or pinning test.

## What was folded

All five blockers and every nit that named a false or missing claim. The S12 cells are
annotated inline, `NARROWED` is defined in the vocabulary block, the correction note names
its four rows, and the closed rows now carry controls and pinned test node ids.

## What was NOT folded

The reviewer suggested treating the empty `## Off-Goal Findings` as a nit. The closeout
disposition review disagreed and called it a blocker; the section is now filled. Recorded
here because the two rounds reached different severities on the same gap, and the later
one was right.

## Boundary Ownership

- Verdict: owned-correctly

The midpoint round reads the goal artifact against the sweep and the commits; it does not
review code. Keeping that boundary is what let it see a defect four slice-level reviewers
had walked past — they were reading repairs, and the defect was in a claim. The slice
reviews own repair correctness; this round owns claim fidelity; the closeout disposition
review owns whether the goal is safe to close. Three questions, three packets.

## Non-claims

No code was reviewed or changed by this round. The reviewer could not run git and said
which two answers that limited. The fingerprint `verify` was not run.
