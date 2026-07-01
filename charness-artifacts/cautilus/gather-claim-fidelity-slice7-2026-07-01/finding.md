# gather claim-fidelity capture — 2026-07-01 (reference-compaction Slice 7)

## Verdict

**REFUTED HYPOTHESIS FLOOR — the gather RCF→RSF slice does NOT fit the mechanical
doc-routing model, and #410's "keep source-priority.md as a floor" assumption is
refuted by this first live capture.** A representative public-URL gather run
scores **outcome=FAILED, coverage 0/8** against the current spec: it opens **zero**
of the 8 declared reference docs — including BOTH current RCF floors
(`source-priority.md` AND `capability-contract.md`). This is a skill-shape signal
(re-classify), NOT a reason to soften the matcher.

## What ran

`/charness:gather https://docs.python.org/3/library/asyncio-task.html ...` at
`HEAD`=73e8ec14 (`base-commit.txt`), exit **0**, 238486ms, 2.09M tokens, tool
profile Bash=12 Read=3 Edit=2 Skill=1. The run produced a HIGH-QUALITY faithful
gather: fetched the primary source (canonical-link confirmed, no search widening),
distilled the requested asyncio facts, recorded `Access Mode / Route:
support/web-fetch public route, direct-public-fetch`, wrote the durable asset +
refreshed `latest.md`, and committed it (`074eb110` inside the worktree — a
committing run, like impl S5). A textbook gather — that opened no reference docs.

## The refutation (0/8 coverage, both RCF floors missing)

`build-skill-execution-observation.mjs --spec` over `stream.jsonl` →
`outcome=failed | coverage=0/8 | command log missing required fragment:
source-priority.md; ... capability-contract.md`. The run's only Read/Edit calls
were on gather ARTIFACTS (`charness-artifacts/gather/latest.md`, a prior gather
record, and the new asset it authored) — never a `references/*.md`. The
primary-source discipline `source-priority.md` owns is **inlined in SKILL.md**
steps 1-3 ("Prefer primary sources", "local files before external summaries", "if
the user named a source URL/path, do not widen into search"), and the acquisition
is **script-driven** (`gather_plan.py` + `gather_public_url.py` + `support/web-fetch`
own the route/tactics/verdict). So neither doc is a load-bearing doc-open for the
representative public-URL run.

## Why this is NOT a mechanical RCF→RSF slice (the decision)

The other Slice-7 skills move a doc-open floor to an emitted-token floor because
the run DOES the work and just needn't re-open a doc for a token already in core.
gather is different: the representative public-URL run opens NO docs at all, and
its only deterministically-checkable emitted tokens are the Output-Shape field
labels:

- `Access Mode: public` — but `public` is near-trivial for a public-URL gather
  (it appears 3x incidentally; a public fetch ALWAYS says "public"). Pinning
  `requiredSummaryFragments=[public]` would make the floor trivially green — that
  is **softening the matcher**, which the plan forbids. Rejected.
- `Canonical Asset` / `Access Mode` (Output-Shape labels) — trivially emitted by
  any run that follows the template; weak form signal.

So gather's default (public-URL) scenario has **no honest deterministic
doc-routing OR emitted-token floor** under the current model. Its central claim
("durable primary-source asset, not a transient answer") is best proven by a
**durable-artifact-existence floor** (the run wrote `charness-artifacts/gather/<dated>.md`)
or a **substance judge** (outcome-assertions.json grading the asset's
source-fidelity) — gather currently has NEITHER (no outcome-assertions.json). That
is a floor REDESIGN, out of scope for a mechanical RCF→RSF slice.

## Recommendation (needs an operator decision)

gather's checklist item in #410 assumed a doc-open floor that this capture
refutes. Options:

1. **Redesign gather's floor to an artifact/substance instrument** (file a
   follow-up): add an `outcome-assertions.json` with an `output_glob`
   `charness-artifacts/gather/**/*.md` durable-artifact floor + judge assertions
   for source-fidelity, and reclassify source-priority.md (INLINE, gist in
   SKILL.md) + capability-contract.md (DEPTH, on-demand for private-source depth).
   This is the honest fix but is its own design slice, not the mechanical sweep.
2. **Re-scope gather's representative scenario**: a public-URL gather is fully
   script-driven; a provider scenario (Slack/Notion/browser-mediated) MIGHT open
   capability-contract.md. Pin the default spec to a provider scenario where the
   doc-open is genuinely forced. (Higher capture cost; may still be script-driven.)
3. **Leave gather's floor as-is and mark it a known-refuted hypothesis** pending
   the redesign, and skip gather in the mechanical sweep.

Recommended: **Option 1 as a filed follow-up**, skip gather in the mechanical
sweep. Do NOT pin a trivial `public` token to force a green.

## Bundle

- `observed.current-spec-FAILED.v1.json` — the failing grade against the current
  spec (0/8, both RCF missing).
- `transcript.txt` — the faithful gather closeout (Access Mode: public route).
