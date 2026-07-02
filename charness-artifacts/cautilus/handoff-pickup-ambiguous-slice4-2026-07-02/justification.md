# Operator-authorized ask-before-run capture — handoff AMBIGUOUS pickup (Slice 4)

Authorization: operator approved ("모호한 픽업은 가치있어 보임. 승인.", 2026-07-02)
in the achieve goal 2026-07-02-issue-410-411-412-413-...slice-7 (Slice 4).

Purpose: VERIFY the OTHER arm of the conditionalized handoff planner (#412 / commit
c1a66f4d) — an AMBIGUOUS pickup (generic resume + a task directive to bypass the
chunker, no pinned task, >=2 plausible pickups) must OPEN continuation-sequence.md
to order the plausible pickups. Falsifiable: a run that skips it fails the ambiguous
floor. Ref: HEAD (c1a66f4d, conditional planner). Prompt is the pickup-ambiguous fixture.
