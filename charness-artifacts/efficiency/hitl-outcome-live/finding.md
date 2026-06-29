# Outcome Grader — first LIVE judge run (3-live PROVEN)

Date: 2026-06-29

The first end-to-end run of the OUTCOME layer with the real LLM judge (methodology
spec `2026-06-23-skill-claim-fidelity-doc-philosophy.md` § "Evaluation Ownership +
the Outcome Gap", part 3-live). One fresh `/charness:hitl` capture (n=1) at HEAD with
the new output+transcript preservation, then graded by `scripts/grade_skill_outcome.py`
with the reference `claude -p` judge adapter (`scripts/outcome_judge_cmd.py`).

## What ran

- 1 real isolated `claude -p` hitl capture via the A/B runner (`config.json`): 1.07M
  total tokens, 109.8s, 13 tool calls, `pass_rate 1.0` (claim matcher). See `report.md`
  / `results.json` (efficiency metrics) and `preserved/hitl__0/` (observed packet, trace
  digest, `transcript.txt`, `outputs/`).
- Live outcome grade over that bundle against
  `evals/cautilus/hitl-claim-fidelity/outcome-assertions.json`: 3 deterministic + 3
  judge-kind assertions; the judge ran `claude -p` once per judge-kind assertion. Full
  per-assertion verdict + cited evidence in `outcome-grade.md`.
- `check-secrets.sh` over the bundle: no leaks found.

## Verdict: the live judge graded the real work correctly (5/6, pass_rate 0.889)

The three judge-kind assertions each got an evidence-cited PASS from the live judge — it
quoted specific transcript strings, proving it read the actual produced work, not a proxy:

- **chunk-shape PASS** — cited the `Original Material:` excerpt + `Agent Assessment
  (against C1–C5)` + `Recommended Disposition (display-only, non-binding): revise`.
- **non-binding-disposition PASS** — cited `display-only, non-binding` and `No edits will
  be made now — Apply Phase happens only after ... explicit apply instruction`.
- **stop-for-approval PASS** — cited `Decision Needed` and `awaiting your decision on c1
  before advancing to c2`, with no auto-advance through c2–c7.

Deterministic layer: `ran-hitl` PASS, `opened-chunk-contract` PASS (matcher-verified
across tools — the run opened `chunk-contract.md`, "All declared claims met", coverage
1/5 including it).

This is the outcome layer the routing proxy cannot give: a verified judgment that the run
produced a faithful bounded human-in-the-loop chunk presentation, with cited evidence.

## Honest findings / non-claims

- **`materialized-queue` FAILED, and that is correct, not a grader defect.** hitl writes
  its resumable queue under `.charness/hitl/runtime/<sess>/queue.json`, which is gitignored
  (`.gitignore:20`). `preserve_outputs` uses `git ... --exclude-standard`, so gitignored
  runtime state is intentionally not preserved (keeps the committed bundle clean / secret-
  safe). So `outputs/` is empty here and `output_glob **/queue.json` honestly reports no
  match. **Lesson:** for a skill whose meaningful output is gitignored runtime state, the
  deterministic `output_*` checks do not apply — the TRANSCRIPT is the judge's evidence,
  which is exactly what carried this grade. A skill that produces tracked artifacts (docs,
  code) would populate `outputs/` and exercise `output_*` for real.
- **The judge is an LLM (non-deterministic).** These verdicts are well-cited and correct,
  but a re-run could vary in wording or a borderline call. That is why the outcome layer is
  ADVISORY and paired with the deterministic layer + the offline `--selftest` gate (which
  ran green before this grade); it is not a pass/fail commit gate.
- **n=1.** One capture; the grade describes this run, not a distribution.
- **Token cost:** the hitl capture (~1.07M tokens) dominates; the 3 judge calls are small.
  Ask-before-run was honored — this was an explicitly approved live run.
