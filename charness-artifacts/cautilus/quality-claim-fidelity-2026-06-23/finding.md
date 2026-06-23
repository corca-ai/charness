# Quality skill claim-fidelity re-capture — 2026-06-23

Post-remediation deterministic observation on one real `/charness:quality` run:
**failed**. The Slice 4 quality primer edit did not move the primary #397
predicate.

## What ran

`/charness:quality` on `ea46da85`, captured with
`scripts/agent-runtime/capture-skill-run.sh --ref HEAD --invocation
"/charness:quality"` into `/tmp/quality-claim-fidelity-ea46da85`.

The capture completed before the 1200s wrapper timeout. No Cautilus rollup was
run: `python3 scripts/plan_cautilus_proof.py --repo-root . --json` returned
`next_action: "none"` on the clean tree, and the primary deterministic
coverage predicate already failed.

## Deterministic Observed Packet

`node scripts/agent-runtime/build-skill-execution-observation.mjs` emitted
`observed.v1.json` from the full session tree.

- outcome: `failed`
- reference coverage: `0/39`
- required command fragment missing: `quality-lenses.md`
- duration: `881138ms` (threshold `600000ms`)
- tokens: `9267413`
- tool profile: Bash=42, Read=8, Edit=4, Skill=1, Agent=1, Write=1

This means #397 is **not closable** from the Slice 4 remediation. The captured
run still did not open `quality-lenses.md`.

## Transcript Shape

The quality skill was loaded, but the run still did not consult the
engage-always primer references:

- `session.parent.jsonl` line 6: `/charness:quality` loaded the quality skill
  instructions, including the new primer text.
- lines 12-15: the session-start hook required and launched
  `charness:find-skills`.
- line 25: `find-skills` confirmed `quality` as the right route and said it was
  driving into the quality workflow bootstrap.
- line 51 onward: execution ran the repo gate path and then fixed a discovered
  temp-repo hook issue in the throwaway worktree.
- line 192: the final answer explicitly said the active goal's Slice 5 runtime
  capture remained deferred, even though this run was the Slice 5 capture.

No transcript line records a read/open of `quality-lenses.md` or any declared
quality reference.

## Diagnosis

The quality prompt edit was necessary but not sufficient. The run loaded the
quality skill and intentionally satisfied the session-start `find-skills`
requirement, then proceeded into gate execution without opening the
engage-always references classified in Slice 2.

Do not treat this capture as proof of a `find-skills` defect by itself. The next
analysis should compare the transcript against the three-way reference
classification: which engage-always refs should have been consulted before
broad gates, which on-demand refs were not triggered, and which gate-sufficient
refs were legitimately covered by deterministic checks.

Follow-on remediation selected from that analysis: add a small `quality` run
planner that reports `skills_in_scope`, `required_primer_refs`, `gate_plan:
report_first`, and `next_action: read_primer_refs` before broad gates. This
keeps skill-specific references conditional on repos that actually author skill
packages and turns the three-way classification into an execution order instead
of another prose reminder.

## Evidence In This Bundle

- `observed.v1.json`: deterministic observed packet.
- `session.parent.jsonl`: parent session log.
- `session.subagent.jsonl`: bounded reviewer subagent log from the throwaway
  run.
