# Slices 2-3 critique — S9/S10/S12/S13, "a declaration is not its own corroboration"

Date: 2026-08-01
Goal: [close-the-sweeps-remaining-high-rows-by-class](../goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md)
Slices: batch B (S9, S10) and batch C (S12, S13), reviewed together because they
are one class in two files.

## Reviewer Tier Evidence

- Requested tier: bounded read-only reviewer (`bounded-reviewer` typed agent)
- Requested spawn fields: agent_type=bounded-reviewer, unnamed spawn, session-model
  inheritance. Claude Code host, so the Codex `gpt-5.6-terra` / `fork_turns` request
  does not apply under the per-host split; its absence is contract-conformant.
- Host exposure state: requested_fields_sent
- Application state: all four spawns were accepted and returned findings inline; the
  host does not separately expose applied model metadata.
- Delivery state: findings-received

## Reviewer Provenance

Fresh-eye satisfaction: parent-delegated

Four bounded `bounded-reviewer` subagents across two rounds, spawned unnamed in the
shared parent worktree with Read/Grep/Glob only. Round 1: correctness of the repaired
surfaces; blast radius and claim honesty. Round 2: does the fix reproduce the class it
fixes; is every claim true.

Worktree integrity: snapshots opened windows `slice2-round1` and `slice2-round2` at
HEAD `5f99e842`. **Non-claim:** the matching `verify` was not run for either window —
the parent edits in-tree between rounds by design, which `--parent-path` exists to
declare, and it was not used. Integrity rests on `git status --porcelain`.

## Round 1 — findings that changed the work

Ten blockers across two reviewers. The ones that changed the plan:

1. **S9's exploit survived on the path that matters most.** `git log -1 -- <path>` exits
   0 with EMPTY stdout for a file git has never seen, which the first repair collapsed
   into "git cannot answer" and exempted. That is the state of every freshly authored
   artifact when this gate runs before the commit. `commit_state` now separates
   `dated` / `uncommitted` / `dirty` / `unavailable`.
2. **The comment claiming "refuses a stub, not a lie" was false.** Three stub shapes
   passed: `"n/a"` scored exactly the floor because every character counted; `not
   applicable` scored 13 because the per-token vocabulary can never match a phrase; and
   a bare enumeration of three field names engaged all three because only the queried
   field was stripped. The repair reuses the repo's existing `_bound_residual_chars`
   rather than writing a third residual implementation.
3. **A length floor cannot fix ordinary-word fields.** `scope`, `ranking`, `excludes`,
   `notes` are engaged by incidental prose. Measured: 51 of 169 corpus mentions carry no
   value marker, every sampled one incidental. The marker rule was measured at 5 refused
   reviews and deferred as D47 rather than armed.
4. **The measurement never measured the label floors** — the half of S10 that actually
   changed — while a comment cited their corpus minimum. It also had no `--floor`, so
   the counterfactual it asserted was not re-runnable, and no test, which the 2026-08-01
   slice-5 critique had recorded one day earlier as "the withdrawn attempts' mistake one
   level up".

## Round 2 — the fixes that carried the class they fixed

Five blockers, all on round 1's own repairs, and both reviewers independently found the
first:

1. **The comment defending the floor asserted a measurement the slice's own probe and
   test refute** ("floor 20 still refuses zero"; the probe records 10 citations and 46
   label values). A declaration corroborating itself while the number says otherwise —
   this sweep's class, committed by the repair.
2. **A failed `git status` fell through to the log branch**, so an `index.lock` or a
   submodule pathspec turned a dirty artifact back into "Corroborated".
3. **"Corroborated by HEAD" was printed for bytes git has never seen.** Only the `dated`
   arm may say corroborated; the rest now say NOT CORROBORATED.
4. **The S13 refusal wrote its reason to a key no consumer reads**, so
   `check_goal_artifact` refused with an empty reason and
   `describe_goal_closeout_shape` rendered the refused floor as SATISFIED — and round
   1's test pinned that wrong channel, making it load-bearing.
5. **The S12 negation guard ran before the resolution forms**, so
   `skipped: blocked on an upstream outage` was refused for a word inside its own
   reason — S12's own token-for-sentence move, pointed the other way.

Plus: an em dash bypassed the stub-phrase check and landed exactly on the floor; the
`all_fields` defaults made the S10 fix silently droppable; an unparsable `Date:` shape
killed the validator with a traceback; and D47 misattributed the five refused reviews to
2026-06 when two are 2026-07.

## Round-2 repairs — ACCEPTED-UNREVIEWED

Everything in the round-2 list ships without a third review, under the two-round cap.

## Boundary Ownership

- Verdict: owned-correctly

The producer of the corroborating fact is git, and `commit_state` is the only place that
reads it; the consumers (`main`'s exemption arm, the measurement script) receive a typed
state rather than re-deriving dates. Where this slice DECLINED to move a boundary is
recorded rather than implied: the repo already single-sources a later-of-body-and-filename
`observed_date` in `critique_enforcement_scope`, and this repair forks a fourth date
channel instead of extending it, because the default artifact is a rolling pointer with
no filename date. The five floors consuming `goal_artifact_floor_grammar.parse_created_date`
with no corroboration at all are the same class and are out of this slice's scope; they
are carried to the handoff, not silently absorbed.

## What was raised and NOT folded

- Adding a `--require-value-marker` mode to the measurement so D47's two numbers become
  re-runnable. Declined for this slice and recorded instead: both are marked as one-off
  hand measurements in D47 and in the script docstring, and D47's reopen trigger is
  where to re-derive them.
- Counting non-ASCII alphanumerics in the residual. Real for a consumer repo writing
  observations in Korean; recorded as a stated limit rather than changed, because
  changing the shared `_bound_residual_chars` would move the S3 floor too.

## Non-claims

S9, S10 and S12 close as NARROWED with their residuals written into the sweep rows; only
S13 closes. S12's ROW is corrected, not just closed — two of its three stated triggers
never reproduced. No push, no CI dispatch, no live cautilus run.
