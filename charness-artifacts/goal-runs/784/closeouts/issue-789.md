goal-run: prove the #784 composition in a clean clone, comment every child, and read the hosted run for #764 (#789)

Closes #789

The three lanes are green in a clean clone with their not-run lists read
(standing 8863 passed; full read-only 83 passed, 5 not run; release 88 passed,
4 not run). Every closed child is verify-closeout verified and now carries an
issue-owned closeout comment whose body is its carrier commit message. The
most recent scheduled mutation run (33756376766, on a tree after every #784
code child) passed the sampler baseline the #782 rewrite was waiting on and
then lost Run mutation to the job's 180-minute budget at 8880 s of a 9000 s
exec timeout; #764 stays open with the budget recorded as its next work.

Classification: feature
Jtbd: the maintainer can read one composed truth about the tree before the parent closes: three lanes green in a clean clone, every child proven and commented, the hosted observer's latest reading recorded where its issue lives, and the close proof's inputs (expected graph, parent obligation, retro) in the tree.
Boundary: charness-artifacts/goal-runs/784/ (789-clean-clone-lanes.md, 764-recovery-observer-reading.md, closeouts/issue-783..789.md, expected-final-graph.json, parent-terminal-obligation.md, the session record), charness-artifacts/retro/2026-09-04-goal-784-closeout-retro.md with its prepare packet, and the lesson ledger (one seed transition). No script, docs page, or test changed. #764 is not closed; no mutation ceiling or job budget changed.
Resolution Brief: charness-artifacts/goals/2026-09-03-lesson-review-and-775-followups.md slice 6 and the #789 Work Item body.
Implementation: lanes run by the parent in a fresh clone from a script kept beside the log; verify-closeout and close-with-comment per child from the checkout's own issue_tool.py; the hosted run read through gh run view and its job log; the retro written by the parent and persisted through the retro skill's helper.
Prevention: the retro's Next Improvements name the exec-budget binding for the mutation job (destination: #764's thread) and moving the child comment to the moment the carrier lands; the seeded class makes a second budget-ordering miss visible to the next retro.
Behavior: verified — 789-clean-clone-lanes.md carries the three summary lines; five verify-closeout readbacks verified; five comment URLs on the issues; #764 comment posted; check_lesson_ledger.py 63 lessons, 26 active, 37 lifecycle events; check-docs PASS on the changed artifacts.
Review disposition: critique not required; evidence-only change proven by the lanes and the provider readbacks it records.
AI-provenance: executed by an AI agent (Claude Code) in the Goal Run #784 session, continuing the session record's recorded next steps; no operator decision was pending for this slice.
Goal lineage: Goal Run corca-ai/charness#784; draft sha256 878f74409e4c271d07a87c4bb34108376d10878cfdc476249311ec3671a8a151; binding sha256 9e4650f0f731add79de7a0b68cc3b918ed087e71d7e28f43cb74c0973ddafd82; Work Item integrated-closeout (#789).
