# setup (normalization) claim-fidelity capture — 2026-07-01 (reference-compaction Slice 7)

## Verdict

**RCF HYPOTHESIS REFUTED — like gather (#411), setup does NOT fit the mechanical
RCF→RSF doc-routing model, and #410's "default-surfaces.md STAYS pinned" guardrail
is refuted.** The first live in-repo normalization capture scores **outcome=FAILED,
coverage 0/9**: the run opened **zero** reference docs, including all 3 RCF floors
(`normalization-flow.md`, `agent-docs-policy.md`, `default-surfaces.md`).

## What ran

`/charness:setup` full normalization of a mature repo (charness itself → mode
`NORMALIZE`). Capture at `HEAD`=92d7f2aa, exit 0, **571604ms**, 5.2M tokens, tool
profile Bash=23 Read=14 Edit=2 Skill=1 Agent=1 Write=1. The run did a faithful
normalization: detected `NORMALIZE` mode, read the four target surfaces, found one
genuine AGENTS.md drift, fixed it, and committed with a clean tree — all WITHOUT
opening any setup reference doc.

## The refutation (0/9 coverage)

setup has NO planner; its RCF was derived from SKILL.md workflow analysis (a
HYPOTHESIS). The run's 14 Reads were all TARGET SURFACES — `README.md`, `AGENTS.md`,
`docs/operator-acceptance.md`, `docs/conventions/operating-contract.md`,
`charness-artifacts/retro/recent-lessons.md`, `docs/handoff.md`, the adapters — and
NONE were `setup/references/*.md` (verified across the parent stream + the spawned
subagent's jsonl). So the normalization discipline is driven by the SKILL.md
workflow + the real surfaces, not the reference docs.

## Why #410's default-surfaces.md guardrail is refuted

#410 flagged `default-surfaces.md` to STAY RCF-pinned as "a faithful multi-surface
proxy." The capture shows the run engages the REAL surfaces (README/AGENTS/
operator-acceptance/roadmap) DIRECTLY, so the proxy doc-open is never forced — the
proxy reasoning was a hypothesis the live run refutes.

## Recommendation (needs an operator decision — same class as #411)

setup is a SKILL-driven skill whose representative normalization run has no honest
deterministic doc-routing floor. Its central claim (normalize the operating
surfaces) is best proven by a **durable-artifact / substance instrument** (did the
run touch + honestly normalize the real surfaces), not a doc-open. setup has no
`outcome-assertions.json`. This is a floor REDESIGN, out of scope for a mechanical
RCF→RSF slice — filed as a follow-up. RCF is KEPT as-is (a known-refuted
hypothesis); do NOT pin a trivial token to force a green.

Note: only `normalization.spec.json` was captured (in-repo). `greenfield.spec.json`
stays untested (needs a fresh-sandbox capture, not in-repo capturable — #410 already
defers it).

## Bundle

- `observed.current-spec-FAILED.v1.json` — the failing grade (0/9).
- `transcript.txt` — the faithful normalization closeout.
