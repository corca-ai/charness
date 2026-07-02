# hitl claim-fidelity capture — 2026-07-01 (reference-compaction Slice 7)

## Verdict

**RCF→RSF MOVE — the chunk-contract.md doc-open is a FLAKY proxy; fidelity moves to
the substance judge.** A fresh capture REFUTES hitl's own prior proof: coverage
0/5, the run did NOT open chunk-contract.md — yet it authored a faithful bounded
chunk. Since the 2026-06-29 capture DID open it, the doc-open is
non-deterministic. hitl uniquely has a substance judge, so this is the sweep's
third clean move (impl's form+substance twin) — not a softening.

## What ran

Fresh Slice-7 capture (`HEAD`=cf0edb5f, exit 0, 156085ms, 1.18M tokens) of
`/charness:hitl` reviewing `docs/operator-acceptance.md` in bounded chunks, graded
against `evals/cautilus/hitl-claim-fidelity/spec.json`. Behavior source in this
dir: `observed.v1.json` + `transcript.txt`. Full run shape is described under
"The two captures disagree" below.

## The two captures disagree (the flaky-floor signal)

| capture | opened chunk-contract.md? | coverage | floor |
|---|---|---|---|
| 2026-06-29 (prior PROVEN) | YES | 1/5 | passed |
| 2026-07-01 (this) | **NO** | 0/5 | failed on the doc-open |

This run (`HEAD`=cf0edb5f, 156085ms, 1.18M tokens) reviewed
`docs/operator-acceptance.md` in bounded chunks: it materialized the resumable
queue (queue.json / hitl runtime), authored a chunk with an original excerpt +
Agent Assessment + non-binding Recommended Disposition, emitted the disposition
enum (`accept`×17 / `revise` / `defer`), and paused for approval — WITHOUT opening
chunk-contract.md. The chunk-presentation shape is inlined in SKILL.md step 5 +
Output Shape, so a competent run authors faithful chunks from always-loaded core.
The doc-open is therefore not reliably forced — a flaky RCF proxy.

## The move (impl's form+substance split)

- **spec.json**: `requiredCommandFragments=[]` (drop the flaky chunk-contract.md
  doc-open) → `requiredSummaryFragments=["recommended disposition"]` (the
  chunk-contract presentation invariant, emittable from SKILL.md Output Shape).
  chunk-contract.md stays DECLARED classTag DEPTH (the rubric — good/bad-chunk,
  pseudo-tag, rewrite-review — is a depth read opened on-demand, not every run).
- **Honest-reading guard**: `recommended disposition` is ALSO named in the prompt,
  so it is a weak FORM token on its own. hitl is the one sweep skill with a
  SUBSTANCE JUDGE (outcome-assertions.json: `chunk-shape`, `non-binding-disposition`,
  `stop-for-approval`) + the deterministic `materialized-queue` (output_glob
  `**/queue.json`) — those grade fidelity directly and catch a hollow echo. The
  form RSF + substance judge is exactly impl's split, which is why #410 called hitl
  "impl's closest twin."
- **outcome-assertions.json**: removed the now-moot `opened-chunk-contract`
  deterministic assertion (it tested the retired doc-open proxy and would pass
  vacuously); the chunk-shape + non-binding-disposition judge assertions now carry
  "did the run apply the chunk-contract discipline" directly.

`thresholds.max_duration_ms=240000` retained (this capture 156085ms, within budget).

Honest caveat (fresh-eye NIT): on the free path (no ask-before-run `--judge-cmd`),
the substance judge assertions are SKIPPED, so deterministic OUTCOME coverage of
"chunk discipline applied" rests on `materialized-queue` + `ran-hitl` alone — the
real chunk-shape fidelity here is judge-gated, not free-deterministic. Not a
regression (the retired `opened-chunk-contract` was itself vacuous), but the honest
signal is: hitl's fidelity floor now depends on invoking the substance judge.

## Note

This move is BETTER than keeping the flaky floor: RCF=[chunk-contract.md] fails
~half the time (0/5 here, 1/5 in 2026-06-29) while faithful runs pass the judge
every time. Retiring the flaky proxy and leaning on the always-present substance
judge is the reliable, honest floor.

## Non-Claims

- n=1 fresh capture: combined with the 2026-06-29 capture it shows the doc-open is
  flaky (0/5 vs 1/5), not a stability proof of the new floor.
- Not a softening: the flaky doc-open proxy is replaced by the RSF form token PLUS
  the always-present substance judge + `materialized-queue`, not by a relaxed matcher.
- Honest limit (already recorded above): on the free path the substance judge is
  skipped, so deterministic fidelity coverage then rests on `materialized-queue` +
  `ran-hitl` alone — the chunk-shape fidelity floor is judge-gated, not free-deterministic.
