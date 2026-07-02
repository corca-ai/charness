# spec H0 capture — no reference/critique lever; one Bootstrap-scan candidate open (2026-07-03)

Serves [intent.md](./intent.md): the north is a SMARTER agent; the sole test is
"그게 정말 최선인가?" (no proxy). This is the capture-then-diagnose (H0) pass on
`spec`, the skill the handoff routed to after the quality prune+brief pilot.

## Headline

**Unlike quality, spec has no reference-read or critique-cost lever** — its
dominant costs are load-bearing (a fresh-eye critique that caught real defects;
repo-truth ingest), not churn or forced reference reads. Spec's real compaction
already shipped in **Slice 3** (8 pure-DUP deletes, `1306b1c8`) and **Slice 6**
(acceptance-check enum → `## Closeout Vocabulary`, `f9003594`), and the capture
**empirically confirms** the current reference classification is correct.
**One NAMED candidate lever survives, not yet proven:** the Bootstrap block's
blanket scans, which the capable agent executed 0× (see "Candidate lever" below)
— routed forward for a lower-context second capture, not manufactured into a trim
here. (Fresh-eye review SOUND-WITH-DEFECTS; this section incorporates its catch
that the skipped Bootstrap scans are a live candidate, not vindication.)

## Capture (H0) — empirical, not predicted

Real `/charness:spec` on HEAD via the ungated capture harness
(`capture-skill-run.sh` + `build-skill-execution-observation.mjs`; only
`cautilus evaluate` scoring is ask-before-run, and it was NOT run). Invocation:
the verbatim `spec-claim-fidelity/spec.json` fixture prompt (purpose-built to
force both RCF floors, repo-honest, ungameable). Result: **outcome passed**
(both RCF floors genuinely opened), a strong 285-line contract produced, the
run's own fresh-eye critique caught 2 real misreads.

| metric | spec H0 | quality H0 (pilot baseline) |
|---|---|---|
| output tokens (parent+subagent) | ~88k (69k + 19k) | ~168k |
| cache-read | ~4.2M | ~18.9M |
| tool calls | 39 | 103 |
| wall | 11.2 min | 19.5 min |
| dominant cost | **earned critique + ingest** | **closeout CHURN (fixed)** |

spec runs at roughly half quality's output, a quarter the tools, a fifth the
cache — and its single biggest discrete bucket is load-bearing, not waste.

## Diagnosis — where the cost actually went

Tool profile: `Bash=21 Read=8 Edit=7 Write=1 Skill=1 Agent=1`. Ranked:

1. **Fresh-eye `critique` subagent (SKILL.md workflow step 7 → trace step 14) —
   ~19k output / 33 assistant msgs / 1.34M cache. LOAD-BEARING, not overhead.**
   It rendered "SOUND IN SHAPE — with 2 medium factual misreads" and caught a
   real, line-numbered defect the parent would have shipped: the draft
   misattributed `base-commit.txt` to `build-skill-execution-observation.mjs`,
   when that script has no diff-base param and the only consumer is
   `run_skill_efficiency_ab.py:300-303`. It verified 4/6 claims against exact
   repo lines. Its own verification work is trace **steps 24-39 (track `sub`)** —
   e.g. reading `build-observation.mjs` in full to confirm the missing param —
   which is *why* it caught the misread. Cutting this makes the agent DUMBER.
   (Mirrors the quality pilot KEEPING its substance judge.)
2. **Repo-truth ingest via targeted Bash (parent steps 1-12) + the parent applying
   the critique (step 15 re-verify + edits 16-22).** Targeted `rg`/`sed`/`cat`
   grounding the contract in the actual capture harness it specs, then the parent
   re-checking `base-commit.txt` ownership and revising section-by-section. The
   mature draft→critique→verify→finalize loop, not ritual. (Corrected from an
   earlier draft that mislabeled the subagent's steps 24-39 as parent work.)
3. **Reference reads are NOT the dominant cost (3rd confirmation of the H0
   lesson).** Only the 2 RCF floors were opened — `design-lenses.md` and
   `evidence-durability.md` — both genuinely `cat`-read in one Bash at trace step
   10 (honest, not name-mention gaming). `evidence-durability.md` carries the
   real non-briefable weight (the full doc-only proof contract SKILL.md gists in
   one line); `design-lenses.md` (760B of generic Beck/Ousterhout bullets) is
   closer to inlinable — its "keep as ref" case is organizational, not
   capability-stranding. Either way, "teeth→brief" buys nothing for spec.

## The capture confirms the existing classification (a positive finding)

The 4 DEPTH/on-demand refs (`acceptance-checks`, `executable-spec-cost`,
`public-executable-contracts`, `taxonomy-axis-checkpoint`) were **not opened**,
and the run still produced an excellent contract. Per the intent's method, a run
that does the task well WITHOUT opening ref X *is* the "without X" arm — so this
capture is direct evidence that the current fixture (only 2 RCF floors; the rest
DEPTH/on-demand/INLINE) is correctly shaped. No reference lever exists.

## Candidate lever (NAMED, not yet proven) — Bootstrap blanket scans

The SKILL.md Bootstrap block prescribes three broad scans — `rg --files . | sed
-n '1,200p'` (`SKILL.md:21`) and two full-repo `rg -n` mega-scans (`:28`, `:32`).
The representative run executed **all three 0 times**: the capable agent replaced
them with targeted `rg -l`/`sed`/`cat` (parent Bash steps 2-15). Per the intent
(§3-5: does this instruction earn its place? gate→brief), a Bootstrap step the
representative run discards is a live prune/brief candidate **and** a ritual-
training surface — so it is dispositioned here, not waved away as "the agent used
judgment." It is **not a proven lever**, though: this capture ran in-repo on the
harness it was speccing, so it cannot clear the intent's missing-scenario guard
("not opened ≠ never useful" — a cold-start spec in an unfamiliar repo might lean
on the broad scan). **Disposition:** a lower-context second spec capture (an
unfamiliar repo) would settle whether the blanket scans are globally dead weight
or just redundant-when-you-already-know-the-repo; routed to the next session as a
named hypothesis (handoff Next Session option 3), not trimmed blind.

## Secondary finding (tooling, NOT acted on — scope discipline)

The efficiency waste lens flagged `repeated_edit` (spec artifact edited 8×). For
a document-authoring skill this is **benign section-by-section drafting**, not the
gate-churn the smell targets (spec has no validator loop to short-circuit, unlike
quality's 6× validator re-run). This is a false-positive tendency of the lens on
authoring skills — a note about the diagnostic tool, not a spec defect. Left
unactioned to avoid scope creep.

## Method lesson for the remaining sweep

Capture-then-diagnose can legitimately conclude **"no lever in the buckets I
scoped"** — that is the anti-Goodhart guardrail, not a null result. But the
fresh-eye review's catch sharpens the lesson: **"no lever" must be scoped
honestly.** The diagnosis cleared reference reads and critique cost, but a
capable run also silently *routes around* prescribed steps (the Bootstrap
scans) — and a skipped instruction is itself a finding, not vindication. Name it
as a candidate and route it; do not fold it into "no lever." spec's proven
compaction was the DUP-delete + enum-lift (Slices 3/6); its residual scoped cost
is the skill doing its job well; its one open candidate is the Bootstrap prune.

## Held open (not dropped)

Whether a *lighter* critique could find the same 2 defects at less than 33 msgs
is a fair question, but proving it needs a with/without apparatus the intent
explicitly warns against pre-building — and the critique demonstrably earned its
cost here. Left as an open question, not a change.
