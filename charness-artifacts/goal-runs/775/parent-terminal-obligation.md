# Goal Run #775 Parent Terminal Obligation

The parent is the Goal Run for `charness-artifacts/goals/2026-09-03-verification-shape-alignment.md`
(frozen draft sha256 `6f2f63ecd8264a4502f7feeb9884a2e2cbb5e3f288be22536fd93a2eed010898`,
binding sha256 `ea389dd26293eb3deff01bf502073c6d242dd84bb3a1df42b245fcac729d46b0`).
It receives no child cursor of its own and closes only through
`issue_tool.py goal-run-close` after exact readback.

Before the parent closes, all of the following hold and are cited in the
final proof:

1. Every one of the seven linked children (776, 777, 778, 779, 780, 781, 782)
   is provider `CLOSED`, carries an issue-owned closeout comment whose URL is
   the evidence identity in the close proof, and has a `verify-closeout` =
   `verified` readback against its closeout commit.
2. The exact expected graph (`expected-final-graph.json`: the seven
   operator-approved initial children, no amendments) equals the live graph
   read by `goal-run-read`.
3. The three lanes (`run_standing_pytest.py`, `run-quality.sh --full
   --read-only`, `run-quality.sh --release`) are green in a clean clone with
   their not-run list read and recorded.
4. The most recent scheduled `mutation-tests.yml` run on a tree at or after
   #779 is read from GitHub and #764's state is consistent with its outcome:
   closed through the recovery-observer path only if the sampler's coverage
   baseline ran and the run was green; otherwise the failing set is recorded
   as the next work and #764 stays open.
5. `/goal #775` pickup returns `ok: true` with the bounded ledger preview
   showing the three re-admitted classes.

Push, tag, release publish, and installed-host mutation on operator machines
stay separately authorised and are not claimed by the close. No mutation
score is claimed; the sampler's seed rotates per run.
