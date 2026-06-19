# nose v0.13.0 output-vs-counts divergences (corca-ai/nose#463)

- **Source:** https://github.com/corca-ai/nose/issues/463
- **Canonical Asset:** `charness-artifacts/gather/2026-06-19-nose-463-v013-output-observations.md`
- **Freshness:** issue OPEN, created/updated 2026-06-19T02:04Z; fetched 2026-06-19.
- **Access Mode:** GitHub `direct-cli` (`gh issue view 463 --repo corca-ai/nose --comments`).
- **Author:** spilist (operator), filed after running nose 0.13.0 on the **ceal**
  monorepo (1,423 files: ts 863 / py 545 / js 15). Labeled `bug`,`documentation`.
  CodeRabbit flags possible duplicate of corca-ai/nose#365.

## Why this is repo working context

charness item 5 (boy-scout dup ratchet,
`charness-artifacts/spec/boy-scout-dup-ratchet.md`) is built directly on nose.
These are observations, not fix requests; the operator expects nose to improve
but wants item 5 designed to be **resilient to them**.

## Requested Facts — the six observations (all reproduced by the author)

1. **Dashboard `proven` wording overclaims.** The legend ("proven = same
   behavior, machine-verified") and header ("same behavior, not just similar
   shape") flatten the docs' `exact` (whole-unit proof) vs `shared-core` (shared
   sub-computation) distinction. The #1 extractability family `4e38e93152`
   (`validateSemanticMessageSegment`, 27 copies) shares only a **single guard
   line**; the 27 enclosing functions diverge after it (throw vs return false vs
   return null). `ANCHOR_MIN_WEIGHT=20` is IL node count, so a 1-source-line
   guard can earn "heavy [anchor]" next to "0/27 shared".
2. **Default `sort=extractability` ranks a ~0-removable family above ~110 /
   ~375 removable ones.** The top row is `0/27 shared, ~0 removable` (a
   cross-language TS+JS family that by construction shares no source text);
   ranking unit (IL node mass) diverges from the displayed unit (source lines).
3. **`--format json` top-level shape differs by query under the same
   `schema_version: 2`.** `nose query <path> --format json` → has
   `top_candidates` (5), **no `families`**. `nose query <path> all --format
   json` → has `families`, **no `top_candidates`**. The full family list needs
   the `all` term.
4. **Family count differs between summary and the `--fail-on` gate.** Same scan,
   same path: `summary.families` = **1068**; `nose query <path> --fail-on any` =
   **1163** clone families. A 95-family gap between reported count and gate count.
5. **`reinvented` can point production code at a helper defined in a test
   file** ("call `providerRetryWorkerRedaction`" which exists only in `*.test.ts`).
6. **`query` accepts only one path root** — `nose query packages scripts` errors
   (`scripts` parsed as a query term). Two sibling roots need separate runs.

### What worked (calibration)
`exact` true positives; copy-paste robust to line shift; legit `shared-core`
with context hints; exit codes (no-path→2, bad-path→1, empty→0, `--fail-on
any`→1); `stats`/`il`/`reinvented`/`base=origin/main`/`next:` hints all
functioned. Full scan ≈12.7s, ≈494 MB RSS.

## Implications for item 5 (to fold into the spec)

- **Obs 4 is the sharpest:** the ratchet's count source and its new/changed
  detection must come from **one consistent enumeration**. The spec's
  "code newness = nose native `--baseline --fail-on new`" is unsafe — the
  `--fail-on` count diverges from `families[]`. Switch code newness to **our own
  `family_id` set-diff over `families[]`**, symmetric with the doc gate's
  signature set-diff. Never mix the gate count with the families count.
- **Obs 3 + the deprecated-`scan` risk:** charness gates currently run the
  **deprecated** `nose scan --format json` (which *does* carry `families[]` +
  `family_id` — confirmed). The recommended `nose query` has a different shape
  (`top_candidates` vs `families`; needs `all`) and (Obs 6) one root per call.
  Item 5 must pin the command + shape behind one resolver and treat a
  scan→query migration as a known future change, not an ambient assumption.
- **Obs 1 + 2:** piece-1 classification must key on **structural fields**
  (`shared`/`removable`, members, files, same-vs-cross-language), NOT the
  dashboard `proven`/extractability labels. A cross-language 0-removable family
  must not auto-seed as `fixable`.
- **Obs 5:** if `quality` ever proposes an extraction target, exclude
  test-file-only helpers (don't point production at `*.test.*`).

## Captured vs Human Confirmation

Captured: full issue body + the one CodeRabbit auto-comment, verbatim, via gh.
Human-confirmed by the operator (issue author) that this reflects real ceal-repo
runs. No maintainer response yet (issue is hours old).

## Open Gaps

- No upstream fix/triage yet; revisit before item 5 slice 2 in case nose
  resolves Obs 3/4 (which would simplify the resolver).
- Raw JSON dumps not captured here (author offered them on request).
