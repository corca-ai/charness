# Debug claim-fidelity capture #2 — 2026-06-30 (Plan C n=2 gate)

## Verdict

**Floor MISS (cautilus `failed`/reject, coverage 5/10), SUBSTANCE pass_rate 1.0
(6/6) — `falsifiable-hypothesis-before-fix` PASS again. This is the SECOND
confirming clean capture: n=2 on the falsifiable-hypothesis PASS.** Capture #1
(`debug-claim-fidelity-2026-06-30-plan-a-recapture/`) flipped that assertion
FAIL→PASS at n=1; this independent run, on the same spec prompt at the same HEAD,
reproduces the PASS. **The Plan C gate (retire `five-steps.md` from the floor and
let the substance assertion be the bar) is now MET.** The floor doc-skip persists
(the run reached PASS-quality substance via the scaffold STRUCTURE without opening
`five-steps.md`/`debug-memory.md`), which is the thesis, not a regression.

## What ran

`/charness:debug` (the spec's gitignore-scanner bug-class prompt, verbatim from
`evals/cautilus/debug-claim-fidelity/spec.json`) on `HEAD`=2a6c35de (carrying
Plan A ce3caa6c + Plan B 853a5174), isolated-worktree capture, `--timeout-sec
1200`, exit **124** (hit the cap, like the 2026-06-29 quality captures — the
partial tree is usable; the run wrote its debug artifact at ~8min and the cap fell
during closeout/sibling-search). 110 tool calls (Bash=57 Edit=36 Read=12 Write=3
Skill=1 Agent=1), 21.0M tokens, 1197s wall. `cautilus evaluate observation`
(0.17.1): `failed`/reject; reference coverage **5/10** (declared set 10).

## Plan A re-confirmed: the falsifiable-hypothesis discipline is PASS at n=2

The run did NOT do `static scan only` (the original FAIL). It:

- **Reproduction (executed):** created a gitignored `skills/support/generated/
  demo_pkg/probe.py`, confirmed `git check-ignore`, ran the real
  `validate_attention_state_visibility.py` → **exit 1**, then `rm -rf` → green
  again. A real reproduction of the local-pass / CI-fail flip.
- **Hypothesis (falsifiable + explicit disconfirmer):** "a gitignored file under a
  scanned root enters the raw set and makes the scanner exit non-zero, while `git
  ls-files --cached --others --exclude-standard` excludes it. | disconfirmer:
  compare `git ls-files` vs `rglob` on a synthetic gitignored `*.py`, then run the
  real scanner against one."
- **Verification:** `Result: confirmed` — TWO falsifiers actually run (synthetic
  throwaway repo: `git ls-files` vs `rglob` diverge on the gitignored path; real
  scanner: exit 1 on the gitignored probe). Honest non-claims: the CI producer +
  Pattern B git-failure path are reasoned mechanisms, not observed at runtime. No
  source fix applied (RCA-only).

Judge verdict (`grade_skill_outcome.py --judge-cmd`, grader self-test PASSED
good=1.0/bad=0.0 first), `falsifiable-hypothesis-before-fix` **PASS**: "Trace
shows FALSIFIER 1/2 Bash checks run before any edit; artifact has falsifiable
Hypothesis + Verification (real-scanner repro, exit 1) confirming cause; no source
fix applied (debug-only)."

The substance set scored **6/6 (pass_rate 1.0)**: detection-gap (named
`inventory_gitignore_scan_hygiene.py` `DEFAULT_PATH_GLOBS` + `_is_repo_wide_glob`,
WHY each didn't fire, verified `--json` findings `[]`), sibling-search (mental
model + per-sibling decisions), and prevention (broaden the gate glob to
`scripts/*.py`; flag any `rglob`/`os.walk` outside a git-aware context) all PASS.

## The floor doc-skip persists and is CONSISTENT (not a Plan A failure)

- Coverage 5/10 this time (capture #1 was 1/10): the run consulted MORE references,
  but still skipped the two FLOOR docs (`five-steps.md` + `debug-memory.md`), so
  the floor matcher still reports both missing → cautilus `failed`/reject. A
  competent run reaches the structural + falsifiable outcome via the scaffold
  STRUCTURE without opening the canonical floor docs. This is the exact
  "doc-opening is a weak proxy" thesis. Do NOT soften the floor or the matcher.
- This is now **n=2** on the `falsifiable-hypothesis` PASS. The handoff/spec gate
  ("confirm on 1-2 more captures before retiring any floor doc") is satisfied.

## Plan C gate: MET — APPLIED this session (operator-confirmed)

- Per `charness-artifacts/spec/2026-06-30-debug-doc-internalization-and-compression.md`
  Plan C + Caveats: retire `five-steps.md` from `requiredCommandFragments` once the
  "scaffold elicits substance" pattern holds at n≥2. It now does (capture #1 + #2
  both PASS `falsifiable-hypothesis`). **`five-steps.md`'s load-bearing rules
  (smallest reproduction; falsifiable hypothesis) are internalized in the scaffold
  + substance-asserted; requiring its doc be OPENED tests the wrong thing.**
- Scope guard (from the spec caveat): retire **`five-steps.md` only**.
  `debug-memory.md` STAYS on the floor — its consume-prior-incident-memory behavior
  is a SEPARATE, not-yet-internalized, not-yet-substance-asserted gap. Both captures
  also skipped `debug-memory.md`, so dropping it would lose a real signal.
- **APPLIED this session (operator-confirmed scope):** `requiredCommandFragments`
  in `evals/cautilus/debug-claim-fidelity/spec.json` is now `["debug-memory.md"]`
  (five-steps.md retired). five-steps.md stays in `declaredReferences` +
  `engage-always` (the planner still routes it; `plan_debug_run.py` /
  `tests/test_debug_plan.py` unchanged). No plugin mirror exists for the eval spec;
  no test pinned the floor contents (`test_claim_fidelity_specs.py` validates the
  RCF-must-be-engage-always rule structurally — `["debug-memory.md"]` satisfies it).
  The re-pin is documented in the spec `_comment` + the five-steps.md engagement
  rationale.

## Efficiency note (advisory)

Waste smells (6, advisory/non-blocking): the produced artifact was edited **38x**
(`repeated_edit` — far above capture #1's 4x; the run iterated the artifact in many
small Edits — batch into fewer writes); `validate_attention_state_visibility.py`
read 3x and `inventory_gitignore_scan_hygiene.py` read 2x (`duplicate_read`); a
`wc -l` Bash run repeated 5x/4x. None affect the substance verdict; flagged for the
efficiency lens.

## Disposition

- **n=2 PROVEN.** `falsifiable-hypothesis-before-fix` PASS on two independent clean
  captures post Plan A. Plan C gate MET.
- **debug stays a HYPOTHESIS on the FLOOR doc-opening** (coverage 5/10, both floor
  docs skipped) — consistent across all three captures.
- `latest.md` (cautilus current pointer) unchanged: it records the last PASSING
  cautilus proof (quality 2026-06-29); a floor-miss/substance-pass capture stays a
  standalone dated finding (same as capture #1).
- Bundle: `observed.v1.json`, `cautilus-report.json`, `outcome-grade.md`,
  `trace-digest.jsonl`, `outputs/charness-artifacts/debug/` (the produced
  artifact), `justification.md`, `observation.stderr`.
