# Spec: #325 Provenance-Placement Policy + Portable Check

Canonical contract for #325 (the `2026-06-07-325-provenance-policy-handoff3-gate-capability`
goal, slices S1–S3 and S6). handoff-3's mutation-gate capability keeps its own
contract in [mutation-changed-line-premerge-gate.md](./mutation-changed-line-premerge-gate.md);
this spec is the policy + standing-doc check half of the merged goal.

## Problem

Charness standing/contract docs (the timeless rule docs linked from
`AGENTS.md`/`CLAUDE.md` — not record artifacts like `*/latest.md`, `retro/*`,
`debug/*`) weave GitHub issue numbers and ISO dates directly into rule prose. A
reader opening a *contract* to learn the current rule wades through incident
history; dates age and issue numbers couple the standing rule to mutable tracker
state. This is good provenance culture with drifted placement, not random
clutter — the originating issue/RCA belongs in the record layer with at most one
link from the standing doc.

The fix must be **portable** (inheritable by charness-consuming repos through a
`quality` capability, not a charness-local doc sweep) and must **distinguish
standing-rule docs from tracking docs** (issue refs in tracking ledgers are
load-bearing). Shipping this charness-local would repeat the portability-miss
trap (`charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`) —
the same root cause as handoff-3.

## Current Slice

S1: decide the policy + the enforcement-surface home (this doc). S2 implements
the portable check; S3 sweeps the charness census docs; S6 broadens the
closeout checkpoint that let this almost ship repo-local.

## Fixed Decisions

1. **Provenance-placement rule (the timeless policy).** A standing/contract doc
   states the *timeless rule*. Originating provenance is:
   - a terse trailing `(#NNN)` **only when load-bearing** — i.e. the ref points
     the reader at the actual mechanism / test / record the issue introduced and
     they would need it to act on the rule; **at most one** ref per rule line;
   - **else a single link** to the owning record artifact (`retro/*`, the RCA
     ledger, `debug/*`);
   - **never stacked dates / incident-names** in the rule body — that diary noise
     moves to the record layer plus one link.
2. **Policy doc home: `docs/conventions/provenance-placement.md`** — a new
   standing doc that states the rule, the standing-vs-tracking distinction, and
   the record-layer pointer. Referenced from
   `docs/conventions/operating-contract.md` and
   `docs/conventions/implementation-discipline.md`.
3. **Enforcement surface: a `quality` capability** (`axis: enforcement-surface`
   resolved here). The check lives under `skills/public/quality/scripts/` and is
   config-driven through the **quality adapter** (`.agents/quality-adapter.yaml`)
   — the seam consuming repos already inherit when they install the public
   `quality` skill. Rejected: a repo-root `scripts/*.py` linter (charness-local —
   exactly the portability-miss this issue names) and folding into
   `authoring-preflight` / `check_skill_surface_preflight.py` (those scope to
   skill *package* authoring; standing-rule contract docs are broader). This
   **generalizes** the existing skill-package precedent
   (`skill_text_quality_lib.py`: `ISSUE_ANCHOR_RE`, `DATED_INCIDENT_RE`,
   `is_allowed_issue_anchor_context`) to standing *docs* with a
   standing-vs-tracking allowlist; it does not reinvent it (the lib's regexes are
   reused, not re-derived).
4. **Standing-vs-tracking discriminator is explicit + allowlisted, config-driven.**
   The adapter block `standing_doc_provenance` carries:
   - `standing_docs`: explicit globs of the rule docs to scan;
   - `tracking_allowlist`: globs excluded even if a `standing_docs` glob would
     match them (tracking ledgers whose refs are load-bearing);
   - the record layer (`retro/*`, `debug/*`, `*/latest.md`, `charness-artifacts/*`)
     is never a default scan target.
   **Opt-in by default:** empty `standing_docs` → the check is inert
   (stack-neutral, like the `mutation_testing` slots). A consuming repo opts in by
   listing its rule docs; charness fills it as the dogfood instance.
5. **Flag rule (per scanned line of a standing doc).** Flag when the line carries
   (a) an ISO date `20\d{2}-\d{2}-\d{2}`, OR (b) **two or more** issue refs
   (`ISSUE_ANCHOR_RE` matches ≥2), OR (c) a dated-incident phrase
   (`DATED_INCIDENT_RE`). Do **not** flag a line with exactly one issue ref and no
   date (the load-bearing trailing `(#NNN)`). Skip fenced code blocks and lines
   carrying an explicit inline-allow marker.
6. **charness census classification** (drives S3):
   - **Standing-rule → scan + sweep:** `operating-contract.md`,
     `implementation-discipline.md`, `authoring-preflight.md`,
     `prescribed-skill-closeout-contract.md` (plus
     `handoff-chunked-routing.md`, `ai-ml-engineering-patterns.md` pending S3
     per-doc confirmation).
   - **Tracking → allowlist:** `support-tool-followup.md`,
     `deferred-decisions.md`, `product-success-metrics.md`, `artifact-policy.md`.

## Probe Questions (resolved at S3)

- `handoff-chunked-routing.md` and `ai-ml-engineering-patterns.md` — **RESOLVED:
  neither is a standing-rule contract**, so both stay out of `standing_docs`.
  `handoff-chunked-routing.md` is a per-goal *implementation spec* (it opens "the
  implementation contract for the handoff auto-chunking goal"); its refs/dates are
  load-bearing pointers to trigger cases, slices, and a fixture snapshot.
  `ai-ml-engineering-patterns.md` is a dated #185 *disposition record* whose refs
  to #184/#185/#188/#243 are load-bearing. Both are record/spec layer, not the
  timeless rule layer — out of scope by the same standing-vs-tracking discriminator.
- The check refinement (masking inline-code, markdown link targets, and raw path
  tokens) is what keeps the sanctioned placements — record-layer links and
  code-literal examples — from over-firing; the load-bearing grandfather cutoff
  dates in `prescribed-skill-closeout-contract.md` are kept as backticked literals
  (consistent with the prose section that already backticks them). The
  inline-allow marker remains the visible escape hatch for any free-prose
  load-bearing date.

## Deferred Decisions

- Wiring the check into `run_slice_closeout.py` as a hard gate vs. leaving it an
  advisory `quality` inventory probe — decide after the sweep proves the
  false-positive rate. Default: advisory first (matches the ergonomics gate's
  opt-in posture).
- Auto-fix / rewrite mode (move diary noise to the record layer automatically) —
  out of scope; the check reports, the human sweeps.

## Non-Goals

- Blanket-stripping issue refs / dates — the policy keeps load-bearing terse
  `(#NNN)` and allowlists tracking docs.
- A charness-repo-local doc sweep only — portability is mandatory.
- Re-deriving the skill-package anchor gate — reuse `skill_text_quality_lib.py`.
- Rewriting tracking docs.
- Becoming a generic linter framework — scope is the provenance-placement rule +
  the standing-vs-tracking allowlist + the dogfood sweep.

## Deliberately Not Doing

- Not scanning all of `docs/**` (architecture/generated/release docs carry
  legitimate dates/refs) — the scan target is the explicit `standing_docs` set.
- Not making the check a blocking gate in this slice — advisory first.

## Constraints

- `mutate → sync → verify → publish` hard phase barriers; sync generated /
  plugin / export surfaces before validators.
- The check must be portable: config-driven via the quality adapter, with a
  stack-neutral (inert) default and a documented adapter block.
- Reuse `skill_text_quality_lib.ISSUE_ANCHOR_RE` / `DATED_INCIDENT_RE` rather
  than new regexes that could drift from the skill-package gate.

## Success Criteria

1. A provenance-placement policy doc exists stating the timeless rule, the
   standing-vs-tracking distinction, and the record-layer pointer.
2. A portable `quality` check flags a standing-doc rule line carrying a date or
   ≥2 issue refs, stays silent on an allowlisted tracking doc, and stays silent
   on a single load-bearing trailing `(#NNN)`.
3. The charness census standing docs are swept against the policy (diary noise →
   record layer + one link; load-bearing refs kept terse). `Close #325` staged;
   `gh issue view 325` still OPEN.
4. The closeout checkpoint in `implementation-discipline.md` is broadened to
   cover improvement/issue/policy portability, not only new code mechanisms (S6).

## Acceptance Checks

- **AC1 (flag):** the check, pointed at a fixture standing doc with a dated /
  multi-ref rule line, reports that line. Covered by pytest.
- **AC2 (allowlist):** the same check stays silent on a fixture tracking doc in
  `tracking_allowlist`. Covered by pytest.
- **AC3 (load-bearing):** the check stays silent on a rule line with exactly one
  trailing `(#NNN)` and no date. Covered by pytest.
- **AC4 (inert default):** empty `standing_docs` → no findings (stack-neutral).
  Covered by pytest.
- **AC5 (dogfood sweep):** running the check over the charness `standing_docs`
  config after the S3 sweep returns no findings (or only inline-allowed lines).
- **AC6 (deterministic closeout):** `run_slice_closeout.py` aggregate stays
  green across the new files.

## Critique

Bounded fresh-eye `critique` runs at the S2/S3 bundle boundary (per the goal's
verification cadence), focused on: does the standing-vs-tracking allowlist
over/under-fire, and is the check genuinely inheritable (config-driven via the
adapter) or still charness-local? No forced debug interrupt
(`plan_risk_interrupt` — policy/portability design work, not a behavior defect).

## Canonical Artifact

This file during S1–S3 + S6; the policy doc
`docs/conventions/provenance-placement.md` is the durable rule home after S1.

## First Implementation Slice

S2: implement `standing_doc_provenance_lib.py` +
`check_standing_doc_provenance.py` under `skills/public/quality/scripts/`,
reusing `skill_text_quality_lib` regexes; add the `standing_doc_provenance`
adapter block (inert default in `adapter.example.yaml`, charness census filled in
`.agents/quality-adapter.yaml`); add the adapter validator + contract-doc entry;
write the AC1–AC4 pytest. Then S1's policy doc, then S3 sweep.
