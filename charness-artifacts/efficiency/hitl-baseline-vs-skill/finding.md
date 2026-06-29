# Efficiency A/B — hitl baseline-vs-skill (first live matrix; found a contamination)

Date: 2026-06-29

The first real run of the efficiency A/B harness (`scripts/run_skill_efficiency_ab.py`),
2 arms × n=3 at HEAD `a6574f19`. Both arms ran the SAME bounded-review task on
`docs/operator-acceptance.md`; the only intended difference was the `/charness:hitl`
invocation (baseline = the same task as a plain prompt). The self-test gate passed
before any spend. See `report.md` (generated), `results.json`, `preserved/*/` (per-run
observed packet + trace digest), `run.log`.

## What ran

- baseline (plain prompt, n=3) vs skill (`/charness:hitl …`, n=3), `--out-dir` here.
- 6 real isolated `claude -p` captures via `capture-skill-run.sh`; ~90–126s each.
- No secrets in the bundle (`check-secrets.sh` clean).

## Verdict: the baseline is CONTAMINATED — both arms ran hitl

The headline is a methodology finding, not an efficiency number. The trace digests
(`preserved/baseline__*/trace-digest.jsonl`) show every baseline arm did:
`Skill charness:find-skills` → `Skill charness:hitl` → `bootstrap_review.py` /
`resolve_adapter.py` → wrote `state.yaml`/`queue.json`. The plain-prompt baseline
ran in the charness worktree, read the project CLAUDE.md ("call find-skills at
startup, route to the skill"), and **auto-invoked hitl**. The skill arms ran
`find-skills` first too. So both arms ran hitl — this is ponytail's
baseline-contamination bug, caught by the harness on its first real run.

Corroborating: `total_tokens` is near-equal (baseline 818.6k vs skill 848.8k, +3.7%,
ranges fully overlap) and `tool_count` is identical (9.3 both) — consistent with
both arms doing the same work.

## What the data actually compares (reframed)

Not "skill vs no-skill" but "hitl reached via find-skills routing" (baseline) vs
"hitl via direct slash command" (skill). Under that honest frame, at n=3:

- **Floor reliability:** direct invocation reached the `chunk-contract.md` floor
  2/3; the find-skills-routed path 0/3. The routed path spent steps on discovery and
  (headless) stalled at bootstrap before chunk presentation. (A second possible
  contributor, not isolated here: the baseline prompt lacks the `/charness:hitl`
  prefix that primes the skill flow — the gap may be routing-detour AND prompt
  priming, not routing alone.)
- **duration +23% (90.4s→111.2s, non-overlapping ranges); output_tokens +39%
  (13.3k→18.6k, but the ranges OVERLAP):** a plausible read is the direct arm is not
  more wasteful — it reached chunk presentation while the routed baseline stalled
  earlier (floor 2/3 vs 0/3). But tool_count is IDENTICAL (9.3 both) and the token
  ranges overlap, so at n=3 this is a HYPOTHESIS, not established: same step count,
  more time/output per step. The per-call trace digest is what surfaced the routing
  difference at all; the deterministic metrics alone ("skill +23% slower") would have
  misled — the value is the trace, not the verdict.
- **hitl variance is large:** total_tokens 613k–1037k (~1.7×), duration 85–126s.
  Confirms n=1 is unreliable; n>1 is essential.

## Non-Claims / Follow-ups

- **No clean baseline-vs-skill efficiency claim from this run** — the baseline ran
  the skill. Do not read the deltas as the skill's cost.
- **Methodology correction (durable):** baseline-vs-skill is invalid in this capture
  harness because project CLAUDE.md routing fires for both arms. The clean mode is
  **variant-A-vs-B** (same skill, two refs — routing is identical and cancels). A
  true no-skill baseline needs routing neutralization (ponytail's
  `--setting-sources project,local` + no plugin, or running outside the charness
  repo, or stripping the project CLAUDE.md) — a harness follow-up.
- **The harness itself worked end-to-end** (capture→observe→aggregate→report→preserve,
  self-test gate, per-run trace) — and earned its keep by surfacing its own
  methodology flaw on run one. That is the n>1 + honesty discipline paying off.
- waste_smell_count 0 across all 6 (the earlier n=1 queue.json-churn smell did not
  recur here); output_lines 0/0 (read-only task; hitl's runtime-state writes are not
  tracked vs the ref) — output_lines is uninformative for read-only skills.
- tooling note: the trace-digest `args` field truncates at 160 chars (`…`), so a
  naive grep over the digest for a long command undercounts (a `bootstrap_review.py`
  call shows as `boo…`). Analyze invocations via the `Skill` records (short args) or
  the observed packet, not grep-on-digest for long Bash commands.
