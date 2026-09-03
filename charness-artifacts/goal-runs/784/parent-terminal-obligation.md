# Goal Run #784 Parent Terminal Obligation

The parent is the Goal Run for `charness-artifacts/goals/2026-09-03-lesson-review-and-775-followups.md`
(frozen draft sha256 `878f74409e4c271d07a87c4bb34108376d10878cfdc476249311ec3671a8a151`,
binding sha256 `9e4650f0f731add79de7a0b68cc3b918ed087e71d7e28f43cb74c0973ddafd82`).
It receives no child cursor of its own and closes only through
`issue_tool.py goal-run-close` after exact readback.

Before the parent closes, all of the following hold and are cited in the
final proof:

1. Every one of the six linked children (783, 785, 786, 787, 788, 789) is
   provider `CLOSED`, carries an issue-owned closeout comment whose URL is the
   evidence identity in the close proof, and has a `verify-closeout` =
   `verified` readback against its closeout commit.
2. The exact expected graph (`expected-final-graph.json`: the six
   operator-approved initial children, #783 reused, no amendments) equals the
   live graph read by `goal-run-read`.
3. The three lanes (`run_standing_pytest.py`, `run-quality.sh --full
   --read-only`, `run-quality.sh --release`) are green in a clean clone with
   their not-run list read and recorded.
4. The most recent scheduled `mutation-tests.yml` run is read from GitHub and
   #764's state is consistent with its outcome: closed through the
   recovery-observer path only if the sampler's coverage baseline ran and the
   run was green; otherwise the failing set is recorded on #764 as the next
   work and #764 stays open.
5. `/goal #784` pickup returned `ok: true`, `selected`, naming #789 at the
   start of the closing session, and after #789 closed returns the typed
   refusal `cursor-child-closed`: nothing is left to select.

Push, tag, and installed-host mutation on operator machines stay separately
authorised. Release 8.0.3 was published inside #788 under the operator's
pre-approval of 2026-09-03 and is not re-claimed by the close. No mutation
score is claimed; the sampler's seed rotates per run.
