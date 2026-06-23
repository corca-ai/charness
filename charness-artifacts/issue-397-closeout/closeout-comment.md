Resolved #397's quality runtime-reference defect by changing `quality` from
gate-first execution into planner-backed, report-first execution that loads the
judgment primer before broad deterministic gates.

JTBD: A real `/charness:quality` invocation should not spend the whole run in
deterministic gates while bypassing its own quality reference corpus. It should
make the reference/judgment layer visible early enough that the skill's
mechanism claim is true, not merely its output claim.

Root Cause: The quality skill had a gate-driven completion path. A capable agent
could satisfy the apparent task by repeatedly running deterministic checks and
never create demand for the quality references. That produced the diagnostic
`0/39` reference coverage observed in the original Cautilus reject.

Debug Artifact: `charness-artifacts/cautilus/quality-claim-fidelity-2026-06-23/finding.md`
preserves the rejected diagnostic packet; `charness-artifacts/cautilus/quality-claim-fidelity-2026-06-23-planner-capture/finding.md`
preserves the neutral post-fix capture.

Siblings: Same-class risk remains for other public skills whose deterministic
workflow can outrun their judgment references; proof for this slice is limited
to `quality`. Decision: defer cross-skill rollout and Cautilus diagnostic
artifact-contract work instead of bundling them into #397. Proof: the post-fix
neutral fixture was `/charness:quality` only and observed `9/39` quality
references, not other skills.

Prevention: Commit `71147c82` added `skills/public/quality/scripts/plan_quality_run.py`,
wired `quality/SKILL.md` to run it before broad gates/fixes, and added focused
planner tests plus dogfood metadata. The planner explicitly returns
`next_action: read_primer_refs`, a `report_first` gate plan, and the required
primer references including `quality-lenses.md`.

Behavior: confirmed via neutral runtime capture, not the GitHub state or this
comment. The fixture only invoked `/charness:quality`; it did not name the
planner, primer references, or expected ordering. The resulting observation
passed `execution-quality-claim-fidelity` with `9/39` reference coverage,
`quality-lenses.md` observed, `duration_ms: 154968`, and `Read=13 Bash=8
Skill=1`. Evidence:
`charness-artifacts/cautilus/quality-claim-fidelity-2026-06-23-planner-capture/observed.v1.json`.

Follow-up: #398 tracks the separate diagnostic-proof-contract gap for valid
negative Cautilus verdicts. It is intentionally not kept inside #397 because the
quality runtime-reference defect has its own fix and proof.

Manual Fallback Reason: operator-directed-manual-close - auto-close was not used
because the fixing release and evidence work had already landed without a
close-keyword carrier for #397; this comment is the manual closeout carrier.

Critique: charness-artifacts/critique/2026-06-23-issue-397-closeout.md

AI-provenance: agent-drafted via charness issue resolve; human-auditable through
the linked artifacts, neutral capture, validation commands, and resolution
critique.
