# Debug claim-fidelity RE-CAPTURE — 2026-06-30 (post Plan A internalization)

## Verdict

**Floor MISS (cautilus `failed`/reject), SUBSTANCE pass_rate 1.0 (6/6) — and the
previously-failing `falsifiable-hypothesis-before-fix` is now PASS.** This is the
clean capture that PROVES Plan A changed live behavior: with the internalized
scaffold seeds + `disconfirmer:` marker, the run built a REAL reproduction and ran
an explicit cheapest-disconfirmer BEFORE its conclusion — exactly the discipline the
prior re-capture (`static scan only`) FAILED. The floor doc-skip persists (the run
reached PASS-quality substance via the scaffold STRUCTURE without opening
`five-steps.md`/`debug-memory.md`), which is the thesis, not a regression.

## What ran

`/charness:debug` (the spec's gitignore-scanner bug-class prompt) on `HEAD`
=2f05a153 (carrying Plan A ce3caa6c + Plan B 853a5174), isolated-worktree capture,
`--timeout-sec 1200`, exit 0 (finished naturally). 49 tool calls (Bash=29 Read=12
Edit=5 Skill=1 Write=1 Agent=1), 6.01M tokens, 631s wall.
`cautilus evaluate observation`: `failed`/reject; reference coverage **1/10**
(declared set is now 10 — Plan B deleted anti-patterns.md).

## Plan A PROVEN: the falsifiable-hypothesis discipline flipped FAIL -> PASS

The run did NOT do `static scan only` (the prior FAIL). It:

- **Reproduction (executed):** built a non-git tree with a tracked file + a
  gitignored `generated.pyc`/`__pycache__/foo.py`, called
  `iter_repo_files(root, require_git=False)`, and observed it returned the
  gitignored paths (`INGESTED GITIGNORED? True`); with git present the same call
  excluded them — "the exact local-pass / CI-fail flip."
- **Hypothesis (falsifiable + explicit disconfirmer):** "the scanner's
  gitignore-awareness depends on runtime conditions ... Disconfirmer: run
  `iter_repo_files` in a non-git tree seeded with a gitignored file; if the ignored
  file is absent, the hypothesis is false."
- **Verification:** `Result: confirmed` — the disconfirmer was actually run.

Judge verdict (`grade_skill_outcome.py --judge-cmd`), `falsifiable-hypothesis-before-fix`
**PASS**: "Trace shows 'REPRODUCTION: helper fallback in non-git context' Bash run +
DISCONFIRMER grep during investigation; artifact has falsifiable Hypothesis w/
explicit disconfirmer, confirmed Reproduction. No code fix applied (RCA-only)."

The substance set scored **6/6 (pass_rate 1.0)** — detection-gap (named the
`--require-git-file-listing` strict knob, default off, never armed in CI),
sibling-search (repo-wide rglob/os.walk scan with per-site decisions), and
prevention (arm the flag in CI / default `require_git=True`) all PASS.

## The floor doc-skip persists and is CONSISTENT (not a Plan A failure)

- The run skipped `five-steps.md` + `debug-memory.md` (the floor) — coverage 1/10,
  cautilus `failed`. Same as both prior captures. A competent run reaches the
  structural + falsifiable outcome via the scaffold STRUCTURE without opening the
  canonical reference docs. This is the exact "doc-opening is a weak proxy" thesis
  the internalization work is built on. Do NOT soften the floor or the matcher.
- This STRENGTHENS the Plan C case (retire `five-steps.md` from the floor and let
  the substance assertion be the bar), but it is **n=1** on the
  `falsifiable-hypothesis` PASS. The caveat stands: confirm on one more clean
  capture before retiring any floor doc.

## Plan B confirmed live (no load-bearing rule lost)

The run executed against the compressed reference set (10 declared refs;
anti-patterns.md deleted; sibling-search/detection-gap slimmed) and still produced
exemplary Detection Gap + Sibling Search + Prevention substance. The compression
removed no rule a competent run needs.

## Efficiency note (advisory)

One waste smell: the produced artifact was edited 4x
(`repeated_edit` — batch into one). Advisory, non-blocking.

## Disposition

- **Plan A: LANDED + PROVEN.** The internalized scaffold seed + `disconfirmer:`
  marker flipped the `falsifiable-hypothesis-before-fix` substance assertion from
  FAIL (prior re-capture) to PASS on a faithful run.
- **Plan B: confirmed live** — compressed docs, substance intact.
- **debug stays a HYPOTHESIS on the FLOOR doc-opening** (coverage 1/10). Plan C
  (retire `five-steps.md` from the floor) is GATED on one more clean capture
  showing the `falsifiable-hypothesis` PASS; this is capture #1.
- Bundle: `observed.v1.json`, `cautilus-report.json`, `outcome-grade.md`,
  `trace-digest.jsonl`, `outputs/` (the produced artifact), `justification.md`.
