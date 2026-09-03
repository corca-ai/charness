goal-run: prove the #775 composition in a clean clone and rewrite the last clock-raced test (#782)

Closes #782

The three lanes are green in a clean clone with their not-run lists read
(standing 8750 passed; full read-only 82 passed, 5 not run; release 87 passed,
4 not run). The most recent scheduled mutation run on a tree after #779
(33701977188) failed its coverage baseline on exactly one test whose deadline
arrived through an env knob instead of a time.* call; both probe-boundary
escapee tests now run in-process on a controlled clock plus FIFO, so the
budget is spent by an observation. #764 stays open until a scheduled run
reads that tree. verification-shape-mismatch is scored changed-an-action and
graduated into docs/development.md; the session retro's persistence seeded
the nine tagged classes (47 of 50 active after the graduation).

Classification: feature
Jtbd: the maintainer can read one composed truth about the tree: three lanes green in a clean clone, the hosted baseline's remaining failure named and fixed, the ledger's escape-path lesson retired into the page that owns it, and the parent ready to close through its guarded path.
Boundary: tests/quality_gates/test_cli_skill_surface_probe_boundary.py (two tests rewritten, holder helper gains a release mode), docs/development.md (one paragraph beside the standing-runner block), the lesson ledger (one score, one graduate event, nine seed transitions from retro persistence), charness-artifacts/retro/2026-09-03-goal-775-closeout-retro.md, and the goal-run record (clean-clone lanes, closeout bodies, expected final graph, parent obligation, session record). No production script changed. #764 is not claimed.
Resolution Brief: charness-artifacts/goals/2026-09-03-verification-shape-alignment.md slice 7 and the #782 Work Item body.
Implementation: lanes run by the parent in a fresh clone; the drain-test rewrite by an opus subagent who found the old green rested on the holder's own five-second self-deadline releasing the pipe inside the drain window, and split the two claims (partial output survives a completed drain; the drain bound is the only exit when the pipe never closes); ledger events applied by the parent after the retro was persisted.
Prevention: the two rewritten tests fail under a mutated discard and hang under a removed drain bound; the retro's Next Improvements name the census extension to timeout-bound claims and the changed-line gate as part of every subagent's definition of done.
Behavior: verified — check_lesson_ledger.py 61 lessons, 47 active, 14 lifecycle events; check-docs PASS; the two form gates at zero; 91 focused tests across the touched families; STANDING_RESULT; CLC_RESULT.
Review disposition: critique not required; test and record change proven by the mutation probes above and the clean-clone lanes.
AI-provenance: executed by an AI agent (Claude Code) with one subagent, under the operator's decisions to close today with #764 open and to accept retro-persistence seeding.
Goal lineage: Goal Run corca-ai/charness#775; draft sha256 6f2f63ecd8264a4502f7feeb9884a2e2cbb5e3f288be22536fd93a2eed010898; binding sha256 ea389dd26293eb3deff01bf502073c6d242dd84bb3a1df42b245fcac729d46b0; Work Item integrated-closeout (#782).
