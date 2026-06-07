# Achieve Goal: #325 provenance-placement policy + portable check + handoff-3 gate-as-quality-capability

Status: complete
Created: 2026-06-07
Activation: `/goal @charness-artifacts/goals/2026-06-07-325-provenance-policy-handoff3-gate-capability.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command. It was shaped by the
`2026-06-07-324-325-322-handoff-orchestrator` orchestrator (B3) as a child
`/achieve` goal; the orchestrator does not execute it.

## Active Operating Frame

- Current slice: COMPLETE — all six slices delivered in two commits
  (`7e931999` Close #325 staged, `0f97effb` handoff-3); retro + disposition
  review done.
- Next action: maintainer pushes `origin/main` (closes #325). No agent push/tag.
- Mode: spec-first — decide the provenance-placement policy and the
  enforcement-surface home, then implement the portable check, sweep the dogfood
  docs, and (handoff-3) build the mutation-gate `quality` capability + adapter.
- Time policy: until objective complete (no hard wall-clock cap — not
  timeboxed); re-pick the next slice at each boundary by dependency and risk.
- Activation time: (set at `/goal` activation)
- Closeout reserve: ~15% for final verification + bounded critique + retro.
- Done-early policy: continue_next_improvement
- Verification cadence: cheap deterministic checks (`run_slice_closeout.py`
  aggregate) at commit boundaries; targeted `pytest` for the new check + the new
  capability; broad `pytest` + one bounded fresh-eye `critique` at bundle
  boundaries.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve two objectives that share one root cause (a portable lesson almost
shipping repo-local — `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`):

1. **#325 — provenance-placement policy + portable check.** Define a
   provenance-placement policy: standing/contract docs state the *timeless rule*;
   originating provenance is a terse trailing `(#NNN)` only when load-bearing,
   else a link to the owning record artifact (`retro/*`, RCA ledger, `debug/*`) —
   never stacked dates/incident-names in rule body. Ship a **portable check**
   (the enforcement-surface home is decided at activation, not pre-picked) that
   flags standing-doc rule prose carrying dates / multiple issue refs, with a
   **standing-vs-tracking allowlist**, so charness-consuming repos inherit it.
   Then census + sweep the charness standing docs against the policy. Stage
   `Close #325`.
2. **handoff-3 — promote the changed-line mutation gate to a reusable `quality`
   capability + adapter contract** (operator decision: build it, not
   reference-only), AND carry the pattern + freshness-guard + producer-cost
   lesson into `skills/public/quality/references/mutation-testing.md`.

The two share the portability-classification-as-closeout-checkpoint root cause:
handoff-3 is the concrete instance #325's portable check would catch. Resolve
the policy once and apply it to both.

## Non-Goals

- **Blanket-stripping issue refs / dates** — the policy distinguishes
  standing-rule docs from tracking docs and keeps load-bearing provenance as a
  terse trailing `(#NNN)`.
- **A charness-repo-local doc sweep only** — portability is mandatory; the
  charness docs are the dogfood instance, not the whole scope.
- **Re-deriving the existing skill-package anchor gate** — `validate_skill_ergonomics`
  / `skill_text_quality_lib` already enforce issue-anchor / dated-incident
  prohibition for skill *packages* (`ISSUE_ANCHOR_RE`, `DATED_INCIDENT_RE`,
  `is_allowed_issue_anchor_context`); #325 GENERALIZES that precedent to standing
  *docs* with a standing-vs-tracking allowlist, it does not reinvent it.
- **Rewriting tracking docs** (`support-tool-followup`, `deferred-decisions`,
  `product-success-metrics`) — issue refs there are load-bearing; allowlist them.
- **Pushing/tagging or publishing** — `Close #325` is staged; the issue stays
  OPEN until the maintainer's push. handoff-3 is internal (no GitHub issue).
- **Becoming a generic linter framework** — scope is the provenance-placement
  rule + the standing-vs-tracking allowlist + the dogfood sweep.

## Boundaries

- **Portability is mandatory.** Both #325's check and handoff-3's capability must
  be inheritable surfaces (a `quality` capability / linter / `authoring-preflight`
  / `mutation-testing.md` reference / adapter contract), not charness-local
  fixes. Both carry the repeated portability-miss trap
  (`charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`).
- **`axis: enforcement-surface`** for the #325 portable check — quality
  capability vs. linter vs. `authoring-preflight`. **Do not pre-pick**; decide at
  activation by where consuming repos most naturally inherit it. The existing
  ergonomics gate lives under `skills/public/quality/scripts/` — reusing that
  surface (a `quality`-owned standing-doc check) is the leading candidate but is
  not locked.
- **Standing-vs-tracking discriminator must be explicit and allowlisted.**
  Standing-rule docs (operating-contract, implementation-discipline,
  authoring-preflight, prescribed-skill-closeout-contract): #refs/dates in rule
  prose = the smell. Tracking docs (support-tool-followup, deferred-decisions,
  product-success-metrics, artifact-policy): refs are load-bearing → allowlist.
- **Load-bearing provenance stays** as a terse trailing `(#NNN)`; only diary
  noise (stacked dates/incident-names) moves to the record layer + one link.
- **handoff-3 builds the capability** (operator decision). The mutation gate
  (`check_changed_line_mutation_coverage.py` + producer + freshness marker + the
  handoff-4 false-green warning) becomes a `quality` capability with an adapter
  contract so consuming repos inherit the gate, not just the prose.
- **Related closeout-checkpoint broadening (raised by #325):** the existing
  "Portability classification is a closeout checkpoint" in
  `implementation-discipline.md` only covers new code mechanisms, so it does not
  fire for improvements/issues/policies that should be portable. Broadening it to
  cover improvement/issue scoping is in-scope (it is the root-cause fix) but may
  split to a sub-issue if it grows.
- `mutate → sync → verify → publish` are hard phase barriers; sync generated /
  plugin / export surfaces before validators.
- Bounded fresh-eye reviewers run in the shared parent worktree, inspecting
  prior versions read-only (`git show <ref>:<path>`), never mutating the index.

## User Acceptance

What the user can do to verify completion directly:

- **#325 policy** — a provenance-placement policy doc exists (standing docs state
  the timeless rule; provenance is a terse trailing `(#NNN)` when load-bearing,
  else a link to the owning record artifact).
- **#325 check** — a portable check (quality capability / linter /
  `authoring-preflight`) flags a standing-doc rule line carrying a date or
  multiple issue refs, and stays silent on an allowlisted tracking doc and on a
  single load-bearing trailing `(#NNN)`. A test covers both the flag and the
  allowlist.
- **#325 sweep** — the charness standing docs in the issue census are swept
  against the policy (diary noise moved to the record layer + one link;
  load-bearing refs kept terse). `Close #325` staged; `gh issue view 325` still
  OPEN.
- **handoff-3 reference** — `skills/public/quality/references/mutation-testing.md`
  carries the changed-line pattern + the `.fingerprint` freshness-guard + the
  producer-cost lesson.
- **handoff-3 capability** — the changed-line mutation gate is exposed as a
  reusable `quality` capability with an adapter contract a consuming repo can
  wire; a test or dogfood proof shows the capability resolves and runs.

## Agent Verification Plan

### Low-Cost Checks

- At commit boundaries: `run_slice_closeout.py` deterministic aggregate (ruff,
  lengths, validate_skills, validate_skill_ergonomics, check-markdown,
  mirror-drift, doc-links, dogfood).
- Targeted `pytest` for the new standing-doc provenance check (flag case +
  allowlist case + load-bearing-trailing-ref case) and the new `quality`
  capability resolution.

### High-Confidence Checks

- Broad `pytest` at bundle boundaries.
- One bounded fresh-eye `critique` for the merged #325 + handoff-3
  policy/portability bundle (does the standing-vs-tracking allowlist over/under
  fire? is the capability genuinely inheritable or still charness-local?).
- Changed-line mutation-coverage gate where source changed (run the consumer
  over `base→worktree`, never `--head-sha HEAD`; the handoff-4 warning now
  surfaces that trap).
- A cheap test-duplication pressure sample whenever a slice adds/expands tests.

### External Or Live Proof

- **Skipped (named so closeout cannot silently claim them):** no push/tag/GitHub
  release by the agent (maintainer's); no cross-repo inheritance proof on a real
  consuming repo (the adapter contract is proven locally / by dogfood, not on a
  second repo unless the operator provides one).

## Slice Plan

Dynamic — re-pick at each boundary by dependency and risk.

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 policy spec | #325 | spec-first; the policy decides the check | provenance-placement policy doc: standing-vs-tracking classes, load-bearing-`(#NNN)` rule, record-layer link rule | done |
| S2 portable check + allowlist | #325 | the policy needs teeth | standing-doc provenance check (enforcement-surface decided here) + standing-vs-tracking allowlist + tests (flag / allowlist / load-bearing) | done |
| S3 dogfood sweep | #325 | prove the policy on the census docs | charness standing docs swept; `Close #325` staged | done |
| S4 mutation-testing.md reference | handoff-3 | cheap, independent | pattern + freshness-guard + producer-cost lesson recorded | done |
| S5 gate-as-quality-capability + adapter | handoff-3 | operator chose build | the changed-line gate exposed as a `quality` capability + adapter contract; resolution/dogfood proof | done |
| S6 closeout-checkpoint broadening | #325-related | root-cause fix | implementation-discipline portability checkpoint broadened to improvements/issues/policies (or split to a sub-issue) | done |

## Coordination Cues

Phase-appropriate routing is deferred to `find-skills`
(`--recommend-for-task` / `--recommendation-role --next-skill-id`). Expected
owners to confirm at runtime: `spec` (#325 policy), `quality` (portable check +
handoff-3 capability), `create-skill` (if the gate becomes a `quality` capability
surface), `impl` (the sweep + the checkpoint broadening), `issue` (#325 closeout
+ any split). `debug: n/a — #325 and handoff-3 are policy/portability design
work, not behavior defects.` Record actual routes at completion.

Recorded actual routes (anchored step lines for the closeout floors):

- Routing: find-skills routed each phase — spec (#325 policy) · impl (sweep + checkpoint broadening) · quality (portable checks + handoff-3 capability) · create-skill (gate capability surface) · issue (#325 closeout). debug n/a — policy/portability design, not a behavior defect.
- Gather: n/a — issue bodies via gh; no external web/Slack source.
- Release: n/a — no version bump; the gate capability changed no release surface.
- Issue closeout: #325 — carrier = direct commit 7e931999; close keyword `Close #325` staged (issue OPEN until maintainer push); proof = the commit-msg closeout gate (passed) + resolution critique charness-artifacts/critique/2026-06-07-issue-325-provenance-policy.md. handoff-3 is internal (no GitHub issue).

## Discuss Before Activation

Discuss before activation: RESOLVED via the orchestrator's mid-run stop-and-ask
this session. Consequential defaults and their resolutions:

- **handoff-3 scope** (build a new reusable capability + adapter — a new operator
  surface) — **RESOLVED**: the operator chose to build the `quality` capability +
  adapter contract (not reference-only).
- **#325 issue close / split** — **RESOLVED**: `Close #325` is staged (issue
  stays OPEN until maintainer push); split into a tracked sub-issue only if scope
  clearly grows (operator: "split if scope grows").
- **#325 portable-check enforcement surface** — **deferred to S2 by design**
  (`axis: enforcement-surface`); not a blocker to activation.

## Slice Log

- **S1 (policy spec) — done.** Spec
  `charness-artifacts/spec/issue-325-provenance-placement-policy.md` +
  policy doc `docs/conventions/provenance-placement.md`.
  `axis: enforcement-surface` **resolved → a `quality` capability** (config-driven
  via the quality adapter, the seam consuming repos already inherit; rejected
  repo-root linter = charness-local, and authoring-preflight = skill-package-only
  scope). Routing: `spec` (per coordination cues).
- **S2 (portable check + allowlist + tests) — done.**
  `skills/public/quality/scripts/standing_doc_provenance_lib.py` +
  `check_standing_doc_provenance.py` (reuse `skill_text_quality_lib`
  ISSUE_ANCHOR_RE/DATED_INCIDENT_RE + ISO-date + masking of inline-code / link
  targets / slash-paths so sanctioned placements don't over-fire). New
  `standing_doc_provenance` adapter block (`quality_policy_defaults.py` +
  `quality_adapter_lib.py`), inert default in `adapter.example.yaml`, contract
  doc, reference `standing-doc-provenance.md`, attention-state declaration.
  10 pytest cases (flag / allowlist / load-bearing / inert / sanctioned / stacked
  link-text / invalid-adapter). Routing: `quality`/`create-skill` surface.
- **S3 (dogfood sweep + stage Close #325) — done.** charness `standing_docs` =
  the 4 issue-named contract docs + `provenance-placement.md`; tracking
  allowlist = the 4 ledgers. Probe resolved: `handoff-chunked-routing.md`
  (per-goal spec) + `ai-ml-engineering-patterns.md` (dated disposition record)
  are NOT standing-rule → excluded. Swept 4 docs (diary noise → record-layer
  links / terse refs; load-bearing grandfather dates → backticked literals).
  Check now returns 0 on the 5 configured docs (AC5). Routing: `impl`.
- **S6 (closeout-checkpoint broadening) — done.** `implementation-discipline.md`
  portability checkpoint now fires for two scopes (new mechanism + improvement /
  issue / policy), not only code mechanisms; provenance moved to a retro link.
  No sub-issue split (contained single-bullet rewrite). Routing: `impl`.
- **#325 bundle verification — done.** Broad `run_slice_closeout.py
  --verification-lock` green (broad pytest + ruff + validate_skills +
  validate_skill_ergonomics + check-markdown + doc-links + mirror-drift +
  ownership-overlap + attention-state-visibility). Bounded fresh-eye `critique`:
  `charness-artifacts/critique/2026-06-07-issue-325-provenance-policy.md`
  (ship; one exit-code doc nit found + fixed; over/under-fire + inheritability
  seeds probed and cleared). Cautilus: `next_action: none` (ask-before-run,
  additive `quality` reference change) → deterministic validation owned closeout;
  no `cautilus evaluate` invoked per the on-demand contract.
- **S4 (mutation-testing.md reference) — done.** Added a "Changed-Line Coverage
  Gate (portable pattern)" section to
  `skills/public/quality/references/mutation-testing.md`: the reuse-a-coverage-
  report pattern, the content-fingerprint freshness guard (why content not SHA;
  base→worktree stability across the commit boundary), the producer-cost lesson
  (one instrumented run, drop dynamic_context), and the false-green `--head-sha
  HEAD` dry-run trap. Routing: `quality`.
- **S5 (gate-as-quality-capability + adapter) — done.** New portable capability
  `skills/public/quality/scripts/check_changed_line_coverage.py` +
  `changed_line_coverage_gate_lib.py` reading the new `changed_line_mutation_gate`
  adapter block (glob-driven eligible set, inert default), reusing the
  tool-neutral classifier + coverage.py reader (exported to the plugin → genuinely
  inheritable). 6 pytest cases + a charness dogfood run (resolved the adapter,
  listed changed eligible files, non-blocking stale-coverage skip + false-green
  warning, exit 0). charness keeps its cosmic-ray-coupled active gate; this is the
  portable sibling. Routing: `create-skill`/`quality`.
- **handoff-3 verification — done.** Broad `run_slice_closeout.py
  --verification-lock` green; bounded fresh-eye `critique`
  `charness-artifacts/critique/2026-06-07-handoff3-changed-line-gate-capability.md`
  (ship; inheritability seed confirmed in a bare /tmp repo; 2 nits — marker-
  collision doc warning + a clarity comment — found and fixed).

## Context Sources

A fresh session can reconstruct the originating context by following these in
order:

- **GitHub issue #325** (documentation/enhancement) — full body with the doc
  census table and the standing-vs-tracking distinction.
- **Retro:** `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`
  (the shared portability-classification-as-closeout-checkpoint root cause),
  `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md` (handoff-3
  producer-cost lesson).
- **Existing precedent to generalize:**
  `skills/public/quality/scripts/skill_text_quality_lib.py`
  (`ISSUE_ANCHOR_RE`, `DATED_INCIDENT_RE`, `is_allowed_issue_anchor_context`) and
  `skill_ergonomics_lib.py` (`issue_anchor_in_core`, `portable_package_issue_anchor`,
  `dated_incident_in_core`) — already enforce this for skill *packages*; #325
  generalizes to standing *docs* with a standing-vs-tracking allowlist.
- **handoff-3 targets:** `skills/public/quality/references/mutation-testing.md`,
  `scripts/check_changed_line_mutation_coverage.py` (now incl. the handoff-4
  `false_green_warning`), `scripts/mutation_coverage_producer.py`,
  `charness-artifacts/spec/mutation-changed-line-premerge-gate.md`.
- **Orchestrator parent:** `charness-artifacts/goals/2026-06-07-324-325-322-handoff-orchestrator.md` (B3).

## Interview Decisions

For each Before-phase question: family considered, chosen value, rejected
reason, and the anti-anchoring axis result.

1. **#325 + handoff-3 merged vs separate** — family: {merged one goal, two
   separate goals}. **Chosen:** merged. Rejected *separate* — both retros name the
   same root cause (portability-classification-as-closeout-checkpoint); handoff-3
   is the concrete instance #325's check would catch; merging avoids deriving the
   policy twice. `single-point: this goal's chosen bundling.`
2. **handoff-3 scope** — family: {reference-only, build the quality capability +
   adapter}. **Chosen:** build the capability + adapter (operator decision this
   session). Rejected *reference-only* — the operator chose the durable,
   inheritable surface so consuming repos inherit the gate, not just the prose.
   `axis: enforcement-surface — capability vs reference.`
3. **#325 portable-check home** — family: {quality capability, standalone linter,
   authoring-preflight}. **Deferred to S2** (do not pre-pick). `axis:
   enforcement-surface` — decide by where consuming repos most naturally inherit
   it; the existing ergonomics gate under `skills/public/quality/scripts/` is the
   leading candidate.

## Plan Critique Findings

Reviewer provenance: to be run as a bounded fresh-eye `critique` at the first
bundle boundary during pursuit (the orchestrator's plan critique covered the
parent; this child goal runs its own at S2/S3). Seeded concerns to fold:

- Over/under-firing risk of the standing-vs-tracking allowlist — bind tests for
  the flag case, the allowlist case, AND the single load-bearing trailing
  `(#NNN)` that must NOT flag.
- Capability-still-charness-local risk — the handoff-3 capability must expose an
  adapter contract a consuming repo can wire, proven by resolution/dogfood, not
  only a charness-local invocation.

## Off-Goal Findings

(None yet — file off-goal findings via `issue`, recording only the reference and
reason here. Per the operator decision, split #325 into a tracked sub-issue if
its scope clearly exceeds one coherent fix, e.g. the closeout-checkpoint
broadening growing large.)

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>` at the After-phase. The complete gate
rejects a literal `TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-07-325-h3-provenance-gate-capability.md
Host log probe: charness-artifacts/goals/2026-06-07-325-provenance-policy-handoff3-gate-capability-host-log-probe.json
Disposition review: charness-artifacts/critique/2026-06-07-325-h3-disposition-review.md

Host-log probe scope: thread-wide (no per-goal metric window configured) —
429 function calls, 139 patch applications, 4 subagent spawns.

## User Verification Instructions

Staged in two local commits on `main`, NOT pushed (`git log --oneline origin/main..HEAD`):
`7e931999` (#325 bundle, `Close #325` staged) and `0f97effb` (handoff-3).
`gh issue view 325` is still **OPEN** — it closes only on the maintainer's push.

Commands the user can run to verify:

- **#325 policy** — `sed -n '1,40p' docs/conventions/provenance-placement.md`.
- **#325 check (flag/allowlist/load-bearing/inert):**
  `python3 -m pytest tests/quality_gates/test_standing_doc_provenance.py -q`.
- **#325 dogfood sweep is clean:**
  `python3 skills/public/quality/scripts/check_standing_doc_provenance.py --repo-root .`
  → "OK: 5 standing doc(s) scanned; no drifted provenance."
- **#325 checkpoint broadening:** `sed -n '95,116p' docs/conventions/implementation-discipline.md`.
- **handoff-3 reference:** the "Changed-Line Coverage Gate (portable pattern)"
  section in `skills/public/quality/references/mutation-testing.md`.
- **handoff-3 capability resolves + runs:**
  `python3 -m pytest tests/quality_gates/test_changed_line_coverage_gate.py -q`, and the
  charness dogfood `python3 skills/public/quality/scripts/check_changed_line_coverage.py --repo-root . --base-sha $(git rev-parse origin/main) --head-sha HEAD --json`.

Proof levels the agent did NOT run (named so closeout cannot silently claim them):
no push/tag/GitHub release (maintainer's); no cross-repo inheritance proof on a
real second consuming repo (the adapter contract is proven by the fixture tests
+ charness dogfood, not on a second repo); broad mutation-score run stays CI-only.

## Auto-Retro

Retro: charness-artifacts/retro/2026-06-07-325-h3-provenance-gate-capability.md.
Disposition review (bound fresh-eye): `dispositions-sound` —
charness-artifacts/critique/2026-06-07-325-h3-disposition-review.md.

Retro dispositions:

- **workflow** (batch the portable-surface validators upfront for slices adding
  new skill-package files) → applied as a next-session workflow lesson +
  recorded in `charness-artifacts/retro/recent-lessons.md`. Disposition: memory.
- **capability** (extend `check_skill_surface_preflight.py` to run the
  portable-package gate set as one pre-author/pre-closeout tripwire) →
  **scope-extension comment posted to `issue #328`** recording the additional
  gates this session found (attention-state declaration, ownership-overlap,
  author-repo cite) so a future #328 build covers the whole set, not just the
  three originally enumerated:
  https://github.com/corca-ai/charness/issues/328#issuecomment-4641520695.
  Disposition: issue (#328), captured on the destination.
- **memory** (recurrence persisted) → done: retro + recent-lessons + lesson-
  selection-index refreshed and committed in the closeout commit.
- **Sibling Search** (serial-discovery-behind-a-gate is transferable) →
  recurrence of an existing tracked lesson; boost, no new issue. Disposition: memory.
