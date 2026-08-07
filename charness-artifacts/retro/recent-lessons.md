# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- This retro covers the shaped goal's five slices: selecting the evidence-carrying control for #499/#491, building the semantic reviewer question, assigning the #502 receipt owner, repairing the #500/#501/#497 producer/export boundaries, and staging the final closeout carrier. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)

## Repeat Traps

- **A green suite proved a feature's LOGIC and nothing about its REACHABILITY, and the dead code nearly shipped into a hard-arm gate.** Built #534's suggested fix (exempt a dup-ratchet family whose members are unchanged but whose id rotated on a module move). Seven new tests passed, the dup gate exited 0, the slice closeout completed — and the classifier could not fire on any well-formed input, because the gate fingerprint is `sha16` of the SORTED member-hash list, so equal members implies equal id and "equal members, different id" is contradictory. Every test had hand-built a baseline/live pair the algorithm makes impossible. A carve-out that never fires breaks nothing, so no gate could catch it; a delegated resolution critique did. **When a fix ADDS an exemption, prove the exemption fires on a real input before trusting a green suite.** (source: `charness-artifacts/goals/2026-08-07-close-every-open-issue-declaration-to-verdict.md` Slice 8; sources: 1)
- **Three of four issues attempted in one goal had a named remedy whose premise did not hold.** #530's proposed shared known-key sweep is scoped to a loader that is not the only reader of the file it loads; #534's stated cause stopped being true at an earlier re-key; #526's "stale means the code no longer has it" was false for one of the two entries. In each case the issue body read as a complete diagnosis. **Verify the premise at design time, before shaping a slice around a remedy some durable record already names** — the repo's Work Phase Map already says this; the measured rate says it is the common case, not the exception. (source: `charness-artifacts/goals/2026-08-07-close-every-open-issue-declaration-to-verdict.md`; sources: 3)
- Evidence identity was frozen after a reviewed ledger change, causing packet regeneration and an extra bookkeeping cycle. The repair preserved safety, but the dependency should have invalidated the packet immediately. (source: `charness-artifacts/retro/2026-08-07-session-retro.md`; sources: 3)
- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- The broad verification, fresh-eye rounds, and carrier checks were necessary safety work at proof and issue boundaries, not waste. No host metric evidence supports a per-goal runtime or token comparison. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)

## Next-Time Checklist

- **when a change ADDS an exemption, a carve-out, or a skip path, construct the input that triggers it and show it triggering.** A green gate cannot distinguish "the exemption is correct" from "the exemption is unreachable". (source: `charness-artifacts/goals/2026-08-07-close-every-open-issue-declaration-to-verdict.md`)
- **memory** — This retro plus the recent-lessons digest. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`; sources: 2)
- carry the semantic reviewer question and the worked #499/#491 application in the critique packet and its source/plugin mirrors. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)
- freeze quality artifacts and host probes before broad verification so the proof record and the implementation surface share one identity. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)
- keep rolling telemetry separate from a per-run receipt until a named consumer, retention, and stale-state contract exists. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md`
- `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`
- `charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md`
- `charness-artifacts/retro/2026-08-07-session-retro.md`
- `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`
