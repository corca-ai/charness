# Achieve Goal: Next queue — author-time closeout-draft/goal-closeout preflight + scaffold repo-validator citation verify

Status: complete
Created: 2026-06-09
Activation: `/goal @charness-artifacts/goals/2026-06-09-closeout-preflight-and-scaffold-validator-citation.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: **CLOSEOUT — both slices DONE.** Slice 1 (author-time closeout
  preflight: new `closeout-draft` surface + enriched `goal-closeout` via a
  `shape_command` source, committed `bebdaa2d`) and Slice 2 (verify-first scaffold
  citation audit: CONFIRMED already-shipped in v0.29.0, no residual gap, stale
  handoff Discuss item resolved) are both complete with fresh-eye critiques
  attesting correctness — see `## Slice Log`.
- Next action: After-phase closeout — bundle-boundary broad gate
  (`run-quality.sh --read-only`) + changed-line producer over the bundle range,
  retro, fill `## Final Verification`, flip `Status: complete`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Close the recurring **authoring-preflight-skip** class (#284→#334) for the two
surfaces it still does not cover, in two independent per-slice-closed-out slices:
(1) **author-time closeout preflight** — surface, BEFORE the validator fails, the
required shape of the GitHub-issue **closeout-draft** (`issue_tool.py
validate-closeout-draft`: the `resolution_critique` evidence + its critique
artifact's `tool signal:`, the carrier-body source = commit message for
`direct-commit`, the classification ledger fields, the close keyword) AND the
**goal-closeout** complete gate (`check_goal_artifact`: the `Routing:` line form
naming `find-skills` + the routed skill, the `host_log_probe` allowed skip-reason
enum, the disposition form, the evidence-line bare-path + goal-slug binding), the
sibling of `check_artifact_surface_preflight` for these two surfaces; (2)
**scaffold repo-validator citation verify** — confirm whether `debug`/`critique`/
etc. scaffolds emit the *installed* plugin validator command versus the repo-local
`scripts/<validator>.py` (the handoff Discuss item), VERIFY-FIRST against the
v0.29.0 "scaffolds cite the repo-local validator" claim before changing anything,
and close only a genuine residual gap. Slice 1 is ADDITIVE author-time surfacing
of the same validator verdicts; skill-script changes mirror byte-synced; each
slice closes out independently.

## Non-Goals

- Do NOT take on **#184** (product success metrics — product-level, needs
  `ideation`/`spec`, operator left it out this round) or **push/tag CI** (the
  handoff Discuss "No push/tag CI" item — operator deferred it this round).
- Do NOT weaken or change any closeout/complete validator's verdict — slice 1 is
  ADDITIVE author-time surfacing of the EXISTING shape (the dispatcher reads the
  required shape from the owning validator/scaffold, never re-declares it), exactly
  like the existing 7-surface `check_artifact_surface_preflight`.
- Do NOT re-implement already-shipped scaffold work — slice 2 is VERIFY-FIRST; the
  v0.29.0 release claimed "scaffolds cite the repo-local validator", so the first
  step is a read-only check that reconciles the handoff Discuss item against the
  shipped state (the slice-3 stale-handoff trap from the prior goal, avoided).
- Do NOT auto-file new GitHub issues or cut a real release/push by default; a
  release is cut only when the operator explicitly authorizes it.

## Boundaries

- **Closeout preflight (slice 1).** Classify the home (extend
  `check_artifact_surface_preflight` with new `--type` surfaces vs a dedicated
  closeout preflight) BEFORE wiring. The preflight emits the required shape read
  from the owning validator/scaffold (never re-declared), `--emit-stub` for a
  starter, `--path` for a current-verdict; a test covers an author surfacing the
  closeout-draft + goal-closeout required fields; behavior-preserving for
  `validate-closeout-draft` and `check_goal_artifact` (same verdicts). Mirror
  byte-sync if a skill script changes; apply slice-1-of-the-prior-goal's
  `--scan-issue-anchors` edit-time scan to this goal's skill-package edits.
- **Scaffold citation verify (slice 2).** Read-only verify FIRST: which scaffolds
  (`debug`/`critique`/`retro`/`quality`/`handoff`/`ideation`) emit a validator
  command, and whether it points at the installed plugin copy or the repo-local
  `scripts/<validator>.py` when the working repo owns one. Reconcile against the
  v0.29.0 claim. If already shipped → record honestly + done (no make-work). If a
  genuine gap remains → repo-local-first citation, behavior-preserving for consumer
  repos that ship no validator of their own.
- **Public-skill + generated-surface scope.** Any skill-script change mirror-synced
  (`plugins/charness/...`), deterministic gates own closeout, **no `#N` anchors in
  skill-package files** (dogfood the prior goal's edit-time guard on this goal's
  edits).
- Discuss before activation: RESOLVED — the activation-discussion triggers
  (`production_or_live_proof`, `broad_bundle_scope`) fire on keyword matches in the
  verification-cadence prose, not on real consequential decisions. The resolved
  decisions: (a) NO live/prod proof and NO release is cut by default — both slices
  are local deterministic author-time surfaces and a release stays an
  operator-authorized lane; (b) the broad gate + changed-line producer named in the
  plan are the STANDARD bundle-boundary verification cadence (cover-new-branches-in-
  the-introducing-slice), not a broad-scope behavior change or a new hard gate; (c)
  NO tracked issue is closed by this goal (#184 and #338 are context/out-of-scope).
  Safe to activate; re-open if a reviewer disagrees.
- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

What the user can do to verify completion directly.

- **Closeout preflight:** before committing a closeout, an author runs the
  preflight for the closeout-draft / goal-closeout surface and learns the required
  fields up front (e.g. `check_artifact_surface_preflight.py --type closeout-draft`
  / `--type goal-closeout`), instead of discovering them by failing
  `validate-closeout-draft` / `check_goal_artifact` N times; the underlying
  validator verdicts are unchanged.
- **Scaffold citation:** a read-only check shows whether each scaffold cites the
  installed-plugin or the repo-local validator; if a gap existed it is closed
  (repo-local-first), and if v0.29.0 already shipped it the goal records that
  honestly rather than re-implementing.
- Each slice: the touched test surface passes, mirror byte-synced, and the
  per-slice fresh-eye critique attests correctness.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths --headroom` on every touched file;
  the prior goal's `check_skill_surface_preflight.py --scan-issue-anchors` on any
  edited skill-package file.
- The touched test modules; mirror byte-sync + `validate_skill_ergonomics` for any
  skill-script change; a round-trip-reproduction test that the new preflight emits
  the same required fields the validators enforce (drift guard).

### High-Confidence Checks

- The full quality / issue / achieve test surface green; broad gate
  (`run-quality.sh --read-only`) + changed-line mutation producer at the bundle
  boundary (cover new branches in the introducing slice). Fresh-eye `critique` at
  each slice boundary.

### External Or Live Proof

- None required — both slices are local deterministic author-time surfaces. No
  live/prod/release proof; a release is an operator-authorized lane only.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Author-time closeout preflight for the closeout-draft + goal-closeout surfaces (extend `check_artifact_surface_preflight` or a sibling); shape read from the owning validator, verdict-preserving | this session paid 4 (closeout-draft) + ~5 (goal-closeout) discovery round-trips — the #284→#334 authoring-preflight class on the two surfaces it does not yet cover | new `--type` surface(s) emit required shape + `--emit-stub`; drift test pins shape == validator; test; mirror synced; validators' verdicts unchanged | planned |
| 2 | Scaffold repo-validator citation: VERIFY-FIRST whether scaffolds cite installed vs repo-local validator; close only a genuine residual gap | handoff Discuss open item + this session's version-skew lesson; guards the slice-3 stale-handoff trap (verify before building) | read-only citation audit reconciled against v0.29.0; honest record if shipped, or a repo-local-first fix + test if a gap remains | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Recorded route for this run:

- Routing: find-skills routed this run to `impl` for the impl-phase work, `quality` for the verification-phase work, and `critique` for the per-slice fresh-eye boundaries; `achieve` owns the goal lifecycle.
- Gather: n/a — no external (URL/Slack/Notion/Docs/Drive) source; all context is
  in-repo (validators, scaffolds, retro/handoff artifacts).
- Release: n/a — no release surface touched (no version bump, no install-manifest
  edit; only generated plugin-mirror sync of the changed sources).
- Issue closeout: n/a — this goal closes no tracked GitHub issue (#184 and #338
  are context/out-of-scope per Non-Goals).

## Slice Log

### Slice 1: Slice 1 — author-time closeout preflight (closeout-draft + goal-closeout)

- Objective: Surface, at author time, the enforced shape of the GitHub-issue closeout-draft (validate-closeout-draft) and the goal-closeout complete gate (check_goal_artifact), so an author no longer discovers fields by failing the validator N times. Verdict-preserving.
- Why this approach: Extend the existing check_artifact_surface_preflight dispatcher (the named sibling that already owns the artifact-authoring family) via a new shape_command source: a NEW closeout-draft surface + ENRICH the existing goal-closeout surface. Shape rendered LIVE from the owning validators' constants by two describe-shape sibling scripts, never re-declared. Rejected: a standalone closeout-preflight script (fragments the family); adding to issue_tool.py (NEAR-LIMIT) or goal_artifact_closeout_evidence.py (load-order-sensitive).
- Commits:
- What changed: scripts/check_artifact_surface_preflight.py (+shape_command field, _run_shape_command, accumulate in _shape_text/emit_stub, closeout-draft surface, enriched goal-closeout); NEW skills/public/issue/scripts/describe_closeout_draft_shape.py + skills/public/achieve/scripts/describe_goal_closeout_shape.py; skills/public/quality/references/attention-state-visibility.json (declared the achieve script's surfaced 'skipped:' author-syntax token); docs/conventions/authoring-preflight.md; tests/quality_gates/test_check_artifact_surface_preflight.py; plugins/charness/** byte-identical mirror.
- Alternatives rejected:
- Targeted verification: py_compile, ruff, check_python_lengths, validate_attention_state_visibility, validate_skill_ergonomics, check_doc_links, check_prose_pin, check_skill_surface_preflight --scan-issue-anchors all green; 50 dispatcher tests + 232 issue/achieve verdict-preservation tests pass; 100% line coverage on the 3 new/changed source files; round-trip: a closeout body built from the SURFACED headers satisfies the validator's own _missing_ledger_fields/_missing_close_keywords for every classification; drift tests pin the surfaced shape == live enforced constants (classifications/carriers/ledger fields/manual-fallback enum; skip-reason enum + VALID_FORM_SUMMARY + DESTINATION_FORM_SUMMARY + min-length floors).
- Test duplication pressure: New tests cover genuinely new surfaces (closeout-draft surface, enriched goal-closeout shape_command, _run_shape_command, accumulate arms, loader fail-closed) — no duplication of existing dispatcher tests; the loader fail-closed + spec-None pattern mirrors the established repo convention rather than re-asserting it.
- Critique: Fresh-eye subagent (bounded slice packet): REVISE -> all folded. B1: goal-closeout disposition form conflated Retro-dispositions (VALID_FORM_SUMMARY) with Structural-follow-up destination (DESTINATION_FORM_SUMMARY) -> would mis-direct an author into a REJECTED 'repo-local guard:' Retro-dispositions line; FIXED by rendering both forms live from disposition_form.py. B2: drift hole (forms were prose, unpinned) -> FIXED with a drift test pinning both summaries. N1: direct-commit draft body source is --commit-message-file (git show is post-close verify) -> reworded. N2: 'tool signal:' is enforced by validate_critique_artifacts, not the closeout path -> reattributed. N3: Routing form over-specified -> marked example + stated the real requirement.
- Off-goal findings:
- Lessons carried forward: Carried forward to slice 2: VERIFY-FIRST against the live validator constants, and a fresh-eye reviewer catches form/gate-attribution conflations that self-review misses (the disposition-form-vs-destination-form distinction).
- Metrics:

### Slice 2: Slice 2 — verify-first scaffold repo-validator citation audit

- Objective: Read-only verify FIRST whether the debug/critique/retro/quality/handoff/ideation scaffolds cite the installed-plugin validator or the repo-local scripts/<validator>.py, reconciled against the v0.29.0 'scaffolds cite the repo-local validator' claim; close only a genuine residual gap.
- Why this approach: VERIFY-FIRST by design to avoid the prior goal's slice-3 stale-handoff trap (building already-shipped work). No code change is the correct outcome when the audit shows it already shipped.
- Commits:
- What changed: docs/handoff.md only — resolved the now-stale Discuss item ('Scaffold should cite the repo validator') with the verified-shipped finding + the covering test reference. No scaffold/validator code change (already shipped).
- Alternatives rejected:
- Targeted verification: FINDING: already shipped in v0.29.0, NO residual gap. (1) All six scaffolds implement an identical repo-local-first validator_command (prefer repo-root scripts/<validator>.py when present; installed-plugin absolute-path fallback only for consumer repos). (2) v0.29.0 release note (.agents/release-adapter.yaml) explicitly claims it; git provenance commit 2b30d7e4 'fix(scaffolds): cite the repo-local scripts/ validator (Slice 2)'. (3) Behavioral: all six emit 'python3 scripts/validate_*.py' (repo-local) in this repo; a temp repo-root with no scripts/ falls back to the installed absolute path (behavior-preserving for consumers). (4) Both branches test-covered by tests/test_scaffold_inprocess_coverage.py::test_scaffold_validator_command_repo_local_fallback (parametrized, incl. the FileNotFoundError raise). validate_handoff_artifact + check_doc_links green after the stale-handoff fix.
- Test duplication pressure:
- Critique: Fresh-eye subagent (bounded verify-audit packet): **CONFIRMED-NO-GAP**.
  Independently re-read all six scaffold `validator_command` functions (cited
  file:line), ran them behaviorally (repo-local in this repo; absolute-path
  fallback in a temp repo), confirmed v0.29.0 provenance (commit 2b30d7e4 lands
  before release commit 4ddd9334) + behavior/verdict-preserving, and ran a broad
  missed-surface hunt (debug SKILL.md, achieve/issue closeout, install-surface
  narrative, grep for installed-plugin command patterns) → no other validator-
  citation surface. Informational nit folded: also cite the dedicated regression
  `tests/test_scaffold_repo_local_validator.py` in the handoff (more on-point than
  the in-process cover). No code change correct.
- Off-goal findings:
- Lessons carried forward: The goal's verify-first slice structure worked: it caught a stale handoff Discuss item (already-shipped v0.29.0 work) before any make-work, exactly as designed against the prior goal's slice-3 trap.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **Closeout-preflight waste (this session's retro + disposition review):**
   `charness-artifacts/retro/2026-06-09-nanchor-guard-338-gather-release-closeout.md`
   (`## Waste`: the closeout-draft 4-round-trip + goal-closeout ~5-round-trip
   discovery) and `charness-artifacts/critique/2026-06-09-nanchor-guard-338-gather-release-disposition-review.md`.
2. **Recent-lessons (the recommendation):** `charness-artifacts/retro/recent-lessons.md`
   "Next-Time Checklist" — the author-time issue-closeout-draft preflight, sibling of
   `check_artifact_surface_preflight`, same #284→#334 class.
3. **Scaffold citation:** `docs/handoff.md` "Discuss" ("Scaffold should cite the repo
   validator, not the installed plugin's") + the v0.29.0 release-note claim
   ("SCAFFOLDS CITE THE REPO-LOCAL VALIDATOR") in `.agents/release-adapter.yaml` to
   reconcile against. Owning surface: the artifact-authoring scaffolds + the
   `check_artifact_surface_preflight` dispatcher.
4. **Surface to extend:** `scripts/check_artifact_surface_preflight.py` (the existing
   7-surface author-time preflight) and `docs/conventions/authoring-preflight.md`.
5. **Tracked-but-out-of-scope (NOT this goal):** #184 (product metrics — needs
   `ideation`/`spec`); push/tag CI (handoff Discuss — operator deferred this round).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Which next work (operator-selected).** Family offered: {closeout-draft/goal-
  closeout preflight; push/tag CI; #184 product metrics; scaffold repo-validator
  citation verify}. Chosen: **closeout preflight + scaffold-validator-verify**
  (operator picked 1+4). Rejected: #184 (product-level, needs `ideation`/`spec`),
  push/tag CI (deferred). `axis: theme` — each tracked independently.
- **Slice 1 home (probe, not fixed).** Family: {extend
  `check_artifact_surface_preflight` with new `--type` surfaces; a dedicated
  closeout preflight script}. Deferred to slice 1 — classify before wiring; the
  validators' verdicts stay the source of truth regardless.
- **Slice 2 shape (verify-first, not fixed).** Family: {it already shipped in
  v0.29.0 → record honestly; a genuine residual gap remains → repo-local-first
  fix}. Resolved DURING slice 2 by a read-only audit — deliberately structured to
  avoid the prior goal's slice-3 stale-handoff trap (building already-done work).

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- **Slice 2 may re-implement already-shipped scaffold work (the exact slice-3 trap
  this session hit).** Folded: slice 2 is VERIFY-FIRST — a read-only citation audit
  reconciled against the v0.29.0 claim is the first step; record honestly if shipped.
- **Slice 1 preflight could drift from the validators it mirrors.** Folded: the
  dispatcher reads the required shape from the owning validator/scaffold and never
  re-declares it (the existing 7-surface contract), plus a drift test pinning
  shape == validator; behavior-preserving boundary.
- **Over-worry (raised, not folded):** that an author-time closeout preflight just
  duplicates the validators with no new value — counter: the recurrence cost is the
  validate→fix round-trips this session paid 9×, which an author-time shape surface
  removes; the validators stay the enforcement.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- **Cautilus scenario-registry decision (closeout machinery).** Slice 1 touched the
  `achieve` + `issue` public-skill packages (the two new `describe_*_shape.py` author-time
  scripts). `plan_cautilus_proof.py --json` reports `run_mode: ask`, `next_action: none`,
  `scenario_registry_review_required: false` → per the eval-only ask-before-run contract
  (CLAUDE.md), NO `cautilus evaluate` is invoked. Decision: the changes are ADDITIVE
  author-time shape-source scripts (new files), not behavioral/consumer-contract changes
  to either skill's invocation surface or its validators' verdicts — so neither
  `evals/cautilus/scenarios.json` nor `docs/public-skill-dogfood.json` needs a change.
  Acknowledged via `run_slice_closeout.py --ack-cautilus-skill-review`.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-09-closeout-preflight-and-scaffold-validator-citation.md
Host log probe: charness-artifacts/retro/2026-06-09-closeout-preflight-and-scaffold-validator-citation-host-log.md
Disposition review: charness-artifacts/critique/2026-06-09-closeout-preflight-and-scaffold-validator-citation-disposition-review.md

## User Verification Instructions

## Auto-Retro

Retro dispositions: applied: each of the retro's three surfaced improvements is dispositioned below; the capability one is an outward-facing operator recommendation (out-of-scope this run per the Non-Goal against auto-filing), not laundered to a narrow issue. Per-improvement:

- applied: render every ENUMERABLE enforced form from the owning validator's live constant + drift-test each (the disposition-form-conflation lesson) — shipped as the drift tests pinning the two form summaries in commit `bebdaa2d`.
- out-of-scope: the changed-line coverage producer's `--base`/origin-detect ergonomics (it no-ops post-commit, forcing `--paths` for the committed range) — an outward-facing operator capability recommendation, deferred this run per the Non-Goal against auto-filing new issues; recorded in the retro `## Next Improvements`.
- applied: persisted the per-improvement-disposition-floor vs structural-follow-up-destination-floor distinction (two distinct gates / valid-form summaries) to the retro + the recent-lessons summary refresh.

Structural follow-up: repo-local guard: tests/quality_gates/test_disposition_form_floor.py::test_goal_template_structural_followup_form_matches_live_constant — the fresh-eye disposition review falsified an earlier "none" here: the B1 waste class (an enforced form hand-copied as prose instead of rendered from the owning validator's live constant) had a LIVE sibling at the ORIGIN site B1 copied from — `goal_artifact_template.md`'s `Structural follow-up:` seed line, already drifted from `disposition_form.DESTINATION_FORM_SUMMARY`. Folded: fixed the template to quote the live form verbatim + added this drift-pin guard so the seed cannot drift again. The wider author-facing quoters (`retro-issue-destination-split.md` owner taxonomy, `lifecycle.md` already matching, `waste-sibling-scan.md`, `prescribed-skill-closeout-contract.md`) are context-specific prose definitions, not verbatim seeds — recorded, not force-pinned (a repo-wide verbatim pin would flatten intentional prose).
