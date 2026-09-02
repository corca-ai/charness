Closeout carrier: commit `b8a6c742168ab57d54f04a505afabb7b1776eb74` on `origin/main` (`Closes #773`), Goal Run corca-ai/charness#765; `issue_tool.py verify-closeout` = `verified` against that commit.

Classification: feature
Jtbd: a live Goal Run absorbs a corrected child sentence or an operator-approved new Work Item without re-bootstrapping, while a swapped draft path, foreign binding hash, unapproved child, or closed cursor is still refused by name.
Boundary: skills/public/issue goal-run scripts and issue-backend reference, skills/public/achieve binding, pickup, and lifecycle references, docs/goal-lifecycle.md, and the goal-run test families. The live binding file and historical operation files are unchanged; the first cut in dfbb02342 is the base.
Resolution Brief: charness-artifacts/goals/2026-09-02-north-star-realignment.md amendment #773 and the #773 Work Item section.
Implementation: written by a Codex lane at xhigh effort and integrated by the parent; 21 files. Lineage readers: none read the Work Item set, so amendments needed no change there (grep approved_work_items|amendments over scripts/task_run*, goal_lineage, retro persistence, prove).
Prevention: seeded tests load the live binding and all 21 historical operation files, amend a run, correct child prose, move the cursor, and assert typed refusals for a swapped draft path, an unapproved child key, and a closed cursor.
Behavior: verified — live probes on corca-ai/charness#765 after integration: /goal #765 pickup returns verified-read; a list-children operation file with no identity fields resolved the parent identity and read all 8 children (charness-artifacts/goal-runs/765/operations/list-children-773-identity-probe.out.yaml); the same file with a foreign binding_sha256 refused without mutation (list-children-773-identity-mismatch-probe.out.yaml).
Review disposition: critique not required; reversible local contract change proven by seeded tests and live read-only probes, no provider mutation.
AI-provenance: implemented by a Codex lane and integrated, probed, and verified by an AI agent (Claude Code) in the Goal Run #765 session.
Goal lineage: Goal Run corca-ai/charness#765; draft sha256 129f065a28ce2c6a6a7fd7dc5f6ff2b63349b75ddf1ab62411ea4879ff8d2501; binding sha256 20fdaf7e9a3e1489a308b11041555a9249b2e826d93d951f294a565b24d161cf; Work Item goal-run-binding-simplification (#773, amendment).
