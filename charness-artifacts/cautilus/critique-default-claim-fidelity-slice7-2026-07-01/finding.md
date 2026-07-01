# critique claim-fidelity capture (both scenarios) — 2026-07-01 (reference-compaction Slice 7)

Companion evidence: `../critique-decision-claim-fidelity-slice7-2026-07-01/`.

## Verdict

**Both floors PROVEN; #410's "drop counterweight-triage.md from RCF" is REFUTED —
the autonomous scenario GENUINELY opens it.** No floor move, no SKILL.md change (so
the ~195-line ceiling #410 flagged is untouched).

## The two scenarios

| scenario | RCF | outcome | coverage | counterweight-triage.md engagement |
|---|---|---|---|---|
| default (bare `/charness:critique`, autonomous) | `[autonomous-trigger.md, counterweight-triage.md]` | passed | 4/12 | **GENUINELY OPENED** (Read + `cat` + `sed`) |
| decision (pinned premortem) | `[counterweight-triage.md, premortem-decision.md]` | passed | 1/12 | applied via subagent-prompt DELEGATION (name-mention, not a genuine open) |

- default: `HEAD`=36df7ae4, 621849ms, 7.07M tokens (Bash=76 Read=18 Agent=4
  ReportFindings=4). It self-activated into a full multi-angle (Jackson/Gawande/
  Weinberg) + counterweight review — and, notably, critiqued the Slice-7 sweep
  ITSELF (ReportFindings on `critique-claim-fidelity/spec.json` + the
  reference-compaction `plan.json`). It opened autonomous-trigger.md AND
  counterweight-triage.md and emitted the four-bin triage.
- decision: 457563ms, opened premortem-decision.md; delegated the triage to angle
  subagents with counterweight-triage.md named in the prompt (four-bin enum inlined
  at SKILL.md:37), emitting `Over-Worry`.

## Why #410's RCF-drop is refuted (keep the floor)

#410 wanted counterweight-triage.md dropped from RCF in BOTH specs and its enums
lifted to `## Closeout Vocabulary`. The captures refute the premise: the autonomous
critique GENUINELY opens counterweight-triage.md for its full triage rules (not just
the inlined four-bin), so it is a load-bearing doc-open, not a wasteful re-read.
And the four-bin enum (`Act Before Ship` / `Bundle Anyway` / `Over-Worry` / `Valid
but Defer`) is ALREADY inlined at SKILL.md:37, so there is nothing to lift and no
reason to pressure the 194-line SKILL.md against its ceiling. Both floors are KEPT
and now PROVEN (HYPOTHESIS→PROVEN).

## Recorded nuance (matcher, candidate follow-up — not a blocker)

In the decision scenario, counterweight-triage.md satisfied the RCF via a
command-log MENTION inside an angle-subagent PROMPT, not a genuine file open (the
run applied the inlined four-bin + delegated). The RCF matcher
(`build-skill-execution-observation.mjs` collectCommandLog) includes subagent
prompt text, so naming a reference filename in a spawned-agent prompt can satisfy a
doc-open floor without an open. This did not cause a false PASS of a bad run here
(the concept WAS applied), but it is a matcher-honesty nuance worth a future look —
recorded, not softened, and not blocking this slice (the default scenario's genuine
open carries the skill-wide verdict).

## Change landed

No RCF/RSF move (correctly). Both spec `_comment`s record the captures + the
#410-refutation; `thresholds.max_duration_ms` set from the passing baselines:
default 1244000 (621849ms), decision 915000 (457563ms). critique moves off the
HYPOTHESIS-floor list.
