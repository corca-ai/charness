# Quality skill claim-fidelity capture — 2026-06-29

**Verdict: correctness floor PROVEN; runtime budget DEGRADED.** A real
`/charness:quality` run honors its central routing claim — it opens
`references/quality-lenses.md` and engages the planner's required primers. Two
independent live captures confirm it (via two different read mechanisms). The
first capture also surfaced — and this slice fixed — a **matcher false-negative**
on the for-loop batch-read idiom. Both captures exceeded the provisional duration
budget, dominated by a genuine red `dup-ratchet` gate investigation plus
capture-sandbox git-hook friction, so `max_duration_ms` is NOT re-derived.

## What ran

`/charness:quality` on `HEAD`=7d40044a, captured as a real user would
(`scripts/agent-runtime/capture-skill-run.sh`, isolated `CLAUDE_CONFIG_DIR`
resolving the slash command to a throwaway worktree, hooks pinned, full tools).
No shared install clone mutated (#258 hazard avoided).

- Capture 1 (`--timeout-sec 900`): exit 124 (hit cap). Tools `Bash=62 Skill=1
  Read=1 Agent=1`, 9.66M tokens. Read all 9 planner primers via ONE for-loop.
- Capture 2 / re-capture (`--timeout-sec 1200`): exit 124 (hit cap). Tools
  `Bash=62 Read=20 Skill=1 Edit=1 Agent=1`, 14.4M tokens. Read
  `quality-lenses.md` via the Read tool.

## The first capture surfaced a matcher FALSE NEGATIVE (now fixed)

Capture 1 consulted the canonical planner (`plan_quality_run.py`) and batch-read
EXACTLY its 9 `required_reads` with one command:

```bash
for f in quality-lenses inventory-dispatch automation-promotion gate-classification \
        proposal-flow maintainer-local-enforcement operability-signals skill-quality skill-ergonomics; do
  echo "########## references/$f.md ##########"; cat "references/$f.md"; done
```

The tool result is **27,552 bytes** beginning `# Quality Lenses` — the file was
genuinely read. But the matcher scored it `failed`: the floor
`requiredCommandFragments: ["quality-lenses.md"]` substring-matches the command
log, and the literal `quality-lenses.md` never appears contiguously — the token
`quality-lenses` (no `.md`) lives in the `for` list and the path `references/$f.md`
in the `cat` operand; the path only assembles at shell-expansion time, which the
static command log never captures. Coverage was 1/39 (only `dup-ratchet.md`, read
via a literal `cat`). That is the next instance of the class the 2026-06-29 item-1
matcher fix targeted ("count file reads, not just Read tool-calls") — item 1
handled literal `cat file.md`, not loop-variable reads.

**Fix (this slice):** `expandForLoopReadCommands` in
`scripts/agent-runtime/build-skill-execution-observation.mjs` expands a
literal-list `for VAR in TOK...; do <read> "...$VAR..."; done` into the concrete
read commands each iteration ran, wired into the floor (`collectCommandLog`) and
coverage (`collectOpenedBasenames`). It expands ONLY literal lists (no globs /
`$(...)` / seq) and emits ONLY read-command bodies, so it mirrors a deterministic
shell expansion and never invents a read. Re-scoring Capture 1's SAME session tree
with the fixed matcher flips it `failed → passed`, coverage `1/39 → 10/39` (the 9
primers + `dup-ratchet.md`). This is false-negative correction (the file was
demonstrably read), not softening — independently verified SOUND by a fresh-eye
review and a 3-angle + counterweight critique
(`charness-artifacts/critique/2026-06-29-matcher-for-loop-expansion-critique.md`).

## Capture 2 independently confirms the floor via a different mechanism

The re-capture read `quality-lenses.md` via the Read tool (matcher-visible with or
without the fix) and also scored `outcome=passed`, coverage 10/39. So the floor is
honored regardless of read idiom; n=2.

## Runtime budget: DEGRADED, and NOT a clean baseline

`cautilus evaluate observation` (0.17.1) on the canonical (fixed) packet:
`status: degraded` (passed=0, failed=0, degraded=1). The correctness dimension
(`skill_task_fidelity`) PASSES; the degrade is `runtime_budget_respect` —
`duration_ms` 899315 > threshold 600000.

Both captures hit the timeout cap (cut off, never naturally completed), and the
overrun is dominated by NON-routing work: Capture 2's 62 Bash calls were ~18
`dup-ratchet` investigation (the gate is genuinely red — 8 new fixable families,
per the 2026-06-22 finding) + ~9 git-hook-environment probes (the run fought the
capture sandbox's pinned `core.hooksPath`) + pytest/run-quality. The
`quality-claim-fidelity-2026-06-23-planner-capture` completed in 154968ms, so the
budget IS achievable when a run does not rabbit-hole on a red gate. Therefore:

- `max_duration_ms` is NOT re-derived. The captures provide no natural completion
  time; deriving from a cut-off, rabbit-holed run would be dishonest, and raising
  the bar to fit it would mask a real efficiency signal. The provisional 600000
  stays.
- Per the methodology split, runtime budget is an advisory/degrade dimension, not
  the correctness floor; this degrade does not block the correctness claim.

## Verdict

- **quality correctness floor: PROVEN** (n=2 live captures; `quality-lenses.md`
  opened via for-loop and via Read). Quality is the 3rd correctness-proven skill
  (after retro, hitl).
- The proof required and landed a measurement-instrument fix (the for-loop
  false-negative). This is NOT a skill change and NOT softening — the planner
  already routes correctly and the runs honored it; the matcher under-measured.
- Runtime budget stays a known degrade for quality (red-gate + sandbox-friction
  dominated); `max_duration_ms` unchanged at the provisional 600000.

## Follow-ups

- n=2 caveat: both captures were cut off; a future natural-completion capture
  (e.g. against a tree where `dup-ratchet` is green, or with longer headroom)
  would let `max_duration_ms` be re-derived honestly. Deferred, not blocking the
  correctness proof.
- Capture-sandbox git-hook friction (the run probing pinned `core.hooksPath`)
  recurred in both captures; a quieter hooks posture in `capture-skill-run.sh`
  could reduce non-skill time. Deferred efficiency follow-up.
- Stale `run_js_mutation.py` mutant-budget weight for this .mjs (breaks no gate);
  fold into the next mutation-budget refresh.
