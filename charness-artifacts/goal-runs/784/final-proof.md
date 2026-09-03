# Goal Run #784 Final Proof

Date: 2026-09-04
Provider: `corca-ai/charness`
Frozen draft SHA-256: `878f74409e4c271d07a87c4bb34108376d10878cfdc476249311ec3671a8a151`
Binding SHA-256: `9e4650f0f731add79de7a0b68cc3b918ed087e71d7e28f43cb74c0973ddafd82`
Draft: `charness-artifacts/goals/2026-09-03-lesson-review-and-775-followups.md`

## Outcome and boundary

The Goal Run carried out the second joint lesson review under the graduation
rule and the four #775 follow-ups, in six Work Items, all operator-approved at
activation and none amended: 785 lane-changed-line-done, 786
timeout-bound-census, 783 lesson-review-783 (reused), 787
runtime-root-retention, 788 checkout-first-routing-and-8-0-3, 789
integrated-closeout. All six are provider `CLOSED`, each through a `Closes #N`
commit on `origin/main` whose body is the closeout carrier, each with
`verify-closeout` = `verified`, and each carrying an issue-owned closeout
comment whose URL is the evidence identity in `final-close-proof.json`.

Desired-outcome readback against the Goal Draft:

- A lane's definition of done includes the changed-line gate: `task run`
  completion runs `release_changed_line_coverage.py` against the lane base and
  the receipt carries the verdict (#785, `4057fcb09`); briefs name it.
- The wall-clock census sees timeout-bound verdicts: `check_timeout_bound_form.py`
  in the standing lane with four kept sites recorded (#786, `ede3ac7a9`).
- The second lesson review settled every active lesson with the operator: 15
  graduated, 8 archived, 25 active of 50; docs cut to current facts under a
  1,000-word page budget with a shrink-only record (#783, `a5c9bc1e3`).
- The runtime root reclaims itself: finished lanes drop their worktrees, keys
  never nest, dead keys are swept with salvage (#787, `170180934`).
- Skill scripts inside the authoring repo run from the checkout and refuse a
  drifted installed copy; release 8.0.3 published under the operator's
  pre-approval (#788, `ebfd777ed`).
- The composition proven once in a clean clone and the hosted run read (#789,
  `399276f7d`).

Not claimed: a mutation score (the seed rotates per run), #764's closure, any
release beyond 8.0.3, or installed-host mutation beyond the maintainer refresh
#788 recorded.

## Child closeouts

| child | key | carrier commit | issue-owned comment |
| --- | --- | --- | --- |
| #785 | lane-changed-line-done | `4057fcb09` | https://github.com/corca-ai/charness/issues/785#issuecomment-5532481669 |
| #786 | timeout-bound-census | `ede3ac7a9` | https://github.com/corca-ai/charness/issues/786#issuecomment-5532482287 |
| #783 | lesson-review-783 | `a5c9bc1e3` | https://github.com/corca-ai/charness/issues/783#issuecomment-5532484707 |
| #787 | runtime-root-retention | `170180934` | https://github.com/corca-ai/charness/issues/787#issuecomment-5532482913 |
| #788 | checkout-first-routing-and-8-0-3 | `ebfd777ed` | https://github.com/corca-ai/charness/issues/788#issuecomment-5532483884 |
| #789 | integrated-closeout | `399276f7d` | https://github.com/corca-ai/charness/issues/789#issuecomment-5532544516 |

## Whole-system evidence

- Clean-clone lanes: `789-clean-clone-lanes.md` (standing 8863 passed; full
  read-only 83 passed, 5 not run; release 88 passed, 4 not run; the not-run
  list is the skip list, read from the summary line).
- Hosted mutation: the most recent scheduled run is
  https://github.com/corca-ai/charness/actions/runs/33756376766 on `bce861e15`,
  after #782 and every #784 code child. `Select mutation sample` succeeded (the
  baseline #782 rewrote is green); `Run mutation` was cancelled by the job's
  180-minute budget at 8880 s of a 9000 s exec timeout. #764 is therefore NOT
  closed by this run; the budget is recorded on #764 as the next work
  (`764-recovery-observer-reading.md`).
- Pickup: `/goal #784` returned `ok: true`, `status: selected`,
  `script_origin: same-tree`, naming #789 at the start of the closing session;
  after #789 closed it returns `cursor-child-closed`
  (`observations/goal-784-final-pickup.yaml`), the terminal refusal.
- Exact graph: `observations/goal-784-final-read.yaml`, `verified-read`, six
  children all `CLOSED`, parent OPEN before the close.
- Lesson review: `783-lesson-dispositions.md`, `783-principle-fold-map.md`,
  and the session retro
  `charness-artifacts/retro/2026-09-04-goal-784-closeout-retro.md`.
- Session record: `2026-09-03-session-record.md` (four sessions, each push
  refusal and its repair named).
