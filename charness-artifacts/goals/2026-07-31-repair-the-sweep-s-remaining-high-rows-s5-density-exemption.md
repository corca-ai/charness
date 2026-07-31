# Achieve Goal: Repair the sweep's remaining high rows so an absent or degenerate input stops rendering a green verdict: S5 density exemption, S7 unrecognized cautilus bundle, S21 empty/decision-free chunk, S22 disarmed brief contract — with S8 dispositioned rather than repaired.

Status: complete
Created: 2026-07-31
Activation: `/goal @charness-artifacts/goals/2026-07-31-repair-the-sweep-s-remaining-high-rows-s5-density-exemption.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: complete — four rows repaired, one refuted, all proof executed and committed; nothing pushed.
- Current slice: none — all six slices closed and committed (`4302aeaa`, `ec72c301`; HEAD `ec72c301`).
- Next action: none — the goal is complete. The two operator decisions in the queue are the only open threads, and neither blocks anything shipped.
- Verification cadence: per slice, the row's own reproduction test plus the
  owning surface's existing test module, run in-process. The full pre-push lane
  runs once at the bundle boundary before the commit, not per slice.
- Slice review packet: intent, the row id and its sweep line, changed files and
  their generated/mirror surfaces, the invariant the repair asserts, the
  reproduction test and what reverting the fix does to it, non-claims, the
  out-of-scope rows, and open questions. Slices 1-5 change verdict logic on a
  proof surface, so each owes a second bounded review round reading the repairs;
  slice 6 does not.
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

Repair the sweep's remaining high rows so an absent or degenerate input stops rendering a green verdict: S5 density exemption, S7 unrecognized cautilus bundle, S21 empty/decision-free chunk, S22 disarmed brief contract — with S8 dispositioned rather than repaired.

**Source handoff entry #1: The sweep's remaining high rows**

> Batch by shared root cause only where one exists:
>    **S5 is a density-exemption defect, not an evidence floor**; S7+S8 (cautilus) plausibly
>    share a helper; S21/S22 are separate skills, one repair each.

## Non-Goals

- Not a release: no plugin version bump expected, no publish, no push.
- Do not absorb adjacent handoff entries beyond the selected chunk. Handoff
  entries 2 (S11 second channel), 3 (E-cluster), 4 (un-dispositioned), and 5
  (retro anchors) stay out even where the defect shape rhymes.
- Not a re-audit: rows outside S5/S7/S8/S21/S22 are not re-read, and the sweep's
  other OPEN rows are not opportunistically fixed.
- Do not widen a repair into a redesign of the surface it lands in. Each row gets
  the smallest change that makes the degenerate input fail.
- No live cautilus run: S7 is repaired and proven against fixture bundles plus
  this repo's live corpus.
  `cautilus evaluate` stays eval-only and ask-before-run.

## Boundaries

- In scope, one surface per row (line numbers are the sweep's, as-of 2026-07-28
  — re-locate by symbol, not by line):
  - S5 `scripts/check_skill_surface_preflight.py` — `_remove_pressure_exempt_sections:102`
    exempts *every* section whose H2 is in `PRESSURE_EXEMPT_H2_SECTIONS:38` while
    the anti-abuse pass `closeout_vocabulary_findings:144` audits only the *first*
    `## Closeout Vocabulary` via `_section_body_lines:122`. The density read is
    `:117-119`. (The sweep's `:152` pointer is inside the anti-abuse function, not
    the exemption.)
  - S7 `scripts/validate_cautilus_diagnostics.py:58-110` — a directory carrying
    bundle-shaped evidence but neither `finding.md` nor a name in
    `MACHINE_EVIDENCE_NAMES:16` is not "a bundle", so both `--paths` and `--all`
    exit 0 without reaching the floors at `:179`.
  - S8 `scripts/validate_cautilus_proof.py:192-206` — **demoted to a disposition
    decision, not a repair.** See `## Operator Decision Queue`.
  - S21 `skills/public/hitl/scripts/check_chunk_contract.py:44` via
    `scripts/hitl_review_artifact_lib.py:164-175` — empty/whitespace-only input
    short-circuits to pass, and decision detection is too narrow (a chunk asking a
    human to decide without a `?` or the exact marker passes). Skipping a genuinely
    informational chunk is by design and stays.
  - S22 `skills/public/issue/scripts/audit_brief.py:79-84` — the classification is
    read at the mutation event, so an absent, post-mutation, or unrecognized
    classification value disarms the brief-before-mutation contract identically.
    `load_transcript:46-53` validates `kind` but never the classification value.
- Also in scope: the regression tests for each row, and any generated/mirror
  surface those files feed (sync mirrors before validators).
- Out of scope: `plugins/` copies as an editing target — mutate canonical source
  and sync.
- Portable per implementation-discipline: no host-specific assumption; skill-local
  checkers stay skill-local.
- **No repair may turn an ordinary run red.** Three of the five rows have
  checked-in tests pinning today's verdict
  (`tests/test_cautilus_proof_artifact.py:12`,
  `tests/test_cautilus_diagnostic_artifact.py:73`,
  `tests/quality_gates/test_hitl_chunk_contract.py:71`). A slice either keeps its
  pin green or consciously re-pins it and names the re-pinned assertion in its
  review packet — a silently weakened assertion is the escape
  `docs/conventions/operating-contract.md:89-92` names.
- Reproduction first: every row is `SUBAGENT-CONFIRMED`, which the sweep says is
  "not to be cited as proof without re-running". A slice that cannot reproduce its
  row does not get a fix — it gets a recorded disposition.
- Stop conditions: (1) a row's reproduction fails, so the row is re-dispositioned
  rather than fixed; (2) a repair would require changing a floor's meaning rather
  than its reachability — surface it as an operator decision instead; (3) the dup
  or changed-line ratchet blocks the bundle and the smallest structural cleanup is
  not obvious; (4) a bounded review round cannot be obtained.
- New tests go in-process unless the CLI boundary is the thing under test; the
  boundary-bypass ratchet is no-increase.

## User Acceptance

The operator can run each row's trigger command from the sweep table and see it
**fail** where it used to exit 0:

- S5: a `SKILL.md` with a second `## Closeout Vocabulary` block full of prose is
  reported by `check_skill_surface_preflight.py`, not exempted.
- S7: a directory carrying bundle-shaped evidence (e.g. `cautilus-report.json` +
  `justification.md`) but neither `finding.md` nor a recognized machine-evidence
  name is reported under both `--paths` and `--all`. A truly contentless directory
  still says "no changed cautilus diagnostic bundles", and a `held-out/` or
  `full-gate/` eval output dir does not turn the lane red.
- S8: **no behavior change expected.** Acceptance is a recorded disposition, not a
  failing command.
- S21: empty and whitespace-only input is rejected instead of `{"status": "pass"}`,
  and a chunk that asks a human to decide without a `?` or the exact marker is
  rejected. A purely informational chunk still passes.
- S22: a fix-unit transcript whose classification event is absent, recorded after
  the mutation, or outside the known set is reported instead of `audit ok`.

Plus: the sweep record's rows carry an updated status with the date — `CLOSED
(parent-reproduced 2026-07-31)` only where the parent actually reproduced the
wrong output — and the full pre-push lane is green on the final bundle.

## Agent Verification Plan

- Low-cost, per slice: (a) reproduce the row first, on a seeded temp repo, and
  capture the wrong output verbatim — name the fixture root in the slice report,
  because at least the S7 `--all` reproduction cannot have run against this repo
  (34 real bundles) and the S5 reproduction must be staged or driven through
  `build_report`/`--path`, since `_changed_skill_text:211` reads the staged index
  blob first; (b) enumerate the existing assertions that pin the behavior being
  changed, and decide keep-or-re-pin before writing anything; (c) write the
  regression test against the reproduction; (d) apply the repair; (e) re-run the
  row's test plus the owning surface's existing test module in-process; (f) revert
  the fix and confirm the test fails **naming the new invariant**, not on an
  unrelated ImportError, then restore.
- The revert-check runs patch-shaped, never index-shaped — this is a shared
  worktree (#258): `git diff -- <file> > /tmp/slice-N.patch && git apply -R
  /tmp/slice-N.patch && pytest -q <test>; git apply /tmp/slice-N.patch`. No
  `git stash` / `checkout` / `restore` for this step.
- Mirror sync is part of the slice, not the bundle: slices 1, 4, and 5 have
  `plugins/charness/` mirrors, and the mirrors sync before validators run.
- Mid-cost, per slice: the repo's own preflight/validator for the touched file
  family, and `python3 scripts/check_doc_authoring_preflight.py` for any doc or
  artifact edit.
- Bundle boundary, once before commit: the full pre-push gate lane, plus
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .
  --base-sha <sha before the first commit of this goal>` — the default merge-base
  is vacuous once the commits are pushed, and this goal's commits start from
  `0e8d9760`.
- Not run, and not claimed: no `cautilus evaluate`, no mutation-score lane, no CI
  dispatch, no push. S7/S8 are proven against fixture bundles only.
- Review: a bounded fresh-eye reviewer for slices 1-5, plus a second round reading
  the repairs, because those slices change verdict logic on a proof surface. One
  critique artifact per slice records both rounds. Slice 6 is sweep-row status
  text plus the lane and the commit — it decides nothing, so it carries no round-2
  obligation. The parent snapshots and verifies reviewer boundary integrity with
  `skills/shared/scripts/reviewer_boundary_fingerprint.py` around each review.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 (done) | S5: make the exemption and the anti-abuse audit symmetric — audit every block that is exempted, for every heading in `PRESSURE_EXEMPT_H2_SECTIONS`, not only the first `## Closeout Vocabulary` | Smallest and best-understood row, and the only one where "make it fail" is clean on the live corpus (4 SKILL.md files carry exactly one Closeout Vocabulary block; all 22 carry exactly one `## References`) | Staged/`--path` reproduction with a two-block `SKILL.md` showing `core_nonempty == 4` and zero findings, plus the cheaper `## References` prose variant; both reported after the fix; revert-fails-test check; `plugins/` mirror synced | done — audits every exempt block, fenced lines still charged |
| 2 (done) | S7: a directory carrying bundle-shaped evidence but no `finding.md` and no recognized machine-evidence name becomes a finding, on both `--paths` and `--all`; in the same slice, add the adapter's `held-out/` and `full-gate/` eval output dirs to the non-diagnostic prefixes | The narrow repair is visible in the corpus: 10 real bundles write `cautilus-report.json`, a near-miss for `report.json` in `MACHINE_EVIDENCE_NAMES:16`, so they are silently invisible today | Seeded-repo reproduction of both arms at exit 0, then both reported; `tests/test_cautilus_diagnostic_artifact.py:73` (contentless `raw.log`-only dir) deliberately still green; `--all` green on this repo's live corpus including a simulated eval output dir | done |
| 3 (done) | S8: **no repair.** Record the disposition (design posture, not a defect) in the sweep row and route the freshness residual to the Operator Decision Queue | The reviewer showed the "floors skipped" reading is wrong: those floors judge artifact shape, and there is no artifact under judgment when it did not change; the repo's posture is that deterministic validators own prompt-affecting diffs | The two citations that settle it (`skills/public/quality/references/cautilus-on-demand.md:21`, `tests/test_cautilus_proof_artifact.py:12`) recorded on the row; no code change, no test change | done |
| 4 (done) | S21: reject empty and whitespace-only input, and widen decision detection beyond `?`/the exact marker; keep informational chunks passing | Independent skill; the sweep row fuses two defects and only the degenerate-input half plus detection-widening is safe | Empty and `'   \n\n'` stdin rejected; a decision-asking chunk without `?` rejected; `tests/quality_gates/test_hitl_chunk_contract.py:71` (informational chunk passes) still green as written; `plugins/` mirror synced | done |
| 5 (done) | S22: arm the contract on absent, post-mutation, and unrecognized classification alike; create the surface's first test module | Independent skill, last because it is least entangled; a fix handling only `classification is None` would ship the class it fixes | All three transcript shapes reported instead of `audit ok`; the four checked-in fixtures still pass; new `tests/` module; `plugins/` mirror synced | done |
| 6 (done) | Bundle closeout: update the sweep rows, run the full pre-push lane and the changed-line gate with an explicit `--base-sha 0e8d9760`, commit | The bundle boundary is where broad proof is affordable and where the dup/changed-line ratchets are answered | Full gate lane green; rows carry `CLOSED (parent-reproduced 2026-07-31)` only where the parent actually reproduced, and S8 carries its disposition status instead | done |

## Operator Decision Queue

Operator-only decisions surfaced by this run and left for the repo owner. Each
blocks nothing that shipped.

Queue:

- Decision: the pressure-exempt walk exists in three places, and slice 1 repaired
  only the author-time preflight. `skills/public/quality/scripts/skill_ergonomics_lib.py`
  (portable, cannot import repo `scripts/`) and `scripts/validate_quality_artifact.py`
  keep the unbounded, unaudited version with a different exempt set. Port the
  bounded+audited contract into a portable surface, or accept the divergence?
  - Owner: repo owner.
  - Why deferred: crossing the skill-portability boundary is a scope increase
    beyond row S5, and the divergence is now documented rather than silent.
  - Unblock action: decide port-vs-accept; if port, it wants its own slice.
  - Revisit trigger: the next quality-artifact `core_nonempty_lines` mismatch, or
    the first skill that crosses an exempt budget.
  - **Answered 2026-07-31 by the repo owner: accept the divergence.** The
    bounded+audited contract stays author-time-preflight-only; the portable
    `skill_ergonomics_lib.py` and `scripts/validate_quality_artifact.py` copies keep
    their unbounded walks. This is an accepted, documented divergence
    (`docs/conventions/authoring-preflight.md`), not a closed defect — the revisit
    trigger above stands.
- Decision: is S8's freshness residual — an *existing* proof artifact going stale
  relative to a later prompt change — worth its own sweep row? (The demotion
  itself is settled; this is the leftover.)
  - Owner: repo owner.
  - Why deferred: it blocks nothing in this goal; it is a new-row question, not a
    repair question.
  - Unblock action: open a freshness-class row with its own trigger, or decline.
  - Revisit trigger: slice 6, when the sweep rows are written.
  - **Answered 2026-07-31 by the repo owner: open the row.** Recorded as S110 in
    the triage sweep's main findings table (freshness class, LEAD — not
    parent-reproduced). Opening the row is not a repair claim.
- Decision: should `audit_brief.py` ever be wired into the `issue` flow?
  (Settled for this goal: slice 5 stays a checker repair.)
  - Owner: repo owner.
  - Why deferred: wiring is a scope increase beyond this chunk.
  - Unblock action: file it as its own issue if the checker should enforce
    anything live.
  - Revisit trigger: next time the `issue` skill's brief contract is touched.

## Discuss before activation

Resolved 2026-07-31 — both consequential decisions below were put to the operator
during shaping and answered before this goal was offered for activation.

- **S8 is demoted from repair to disposition.** The plan critique showed the
  original reading was wrong and the naive repair would turn the pre-push lane red
  for every future SKILL.md commit. This changes what the goal title promises, so
  it is the operator's call, not the agent's. **Resolved 2026-07-31: the operator
  chose the demotion — S8 leaves the repair set and its row becomes
  `REFUTED (design posture, 2026-07-31)`. Slice 3 writes no code.**
- **S22 repairs a checker with no caller and no test module.** Resolved
  2026-07-31: the operator chose checker-repair-plus-non-claim over wiring it into
  the `issue` flow. Slice 5 does not touch the `issue` skill surface, and the
  closeout records that the repair fixes a checker, not an enforced boundary.
- **Proof-level non-claim:** no live cautilus run, no mutation lane, no CI
  dispatch, no push. S7's repair is proven against fixture bundles plus this
  repo's live corpus under `--all`; that is not a claim about other repos.
  **Resolved: accepted as the scope of this goal.**

## Slice Log

### Slice 1: Slice 1 — S5: the density exemption now audits what it exempts

- Objective: Make the SKILL.md core-density exemption bounded and audited across every block of every exempt heading, so 60 lines of prose under a second `## Closeout Vocabulary` (or the first `## References`) stop costing zero.
- Why this approach: Smallest, best-understood row, and the only one where 'make it fail' is clean on the live corpus. Reproduced both variants first (core_nonempty 6, findings 0) before touching code, per the sweep's SUBAGENT-CONFIRMED-is-not-proof rule.
- Commits: not yet committed; the bundle commits at slice 6
- What changed: NEW scripts/skill_core_density.py (the density accounting, split out because check_skill_surface_preflight.py was at its 480 code-line cap); NEW scripts/skill_gate_report_render.py + scripts/skill_issue_anchor_scan.py (extraction the dup ratchet's own triage called for); scripts/check_skill_surface_preflight.py (re-exports, closeout_vocabulary_findings -> pressure_exempt_findings, JSON key closeout_vocab -> exempt_findings, human label BLOCK closeout-vocab -> BLOCK exempt-section); tests/quality_gates/test_skill_surface_preflight.py; docs/conventions/authoring-preflight.md; skills/public/create-skill/references/portable-authoring.md; charness-artifacts/quality/dup-review.json (2 families classified intentional); plugins/ mirrors synced.
- Alternatives rejected: Rejected a prose-shape whitelist for exempt lines (25 false positives on the live corpus: wrapped list continuations). Rejected keeping the over-budget case as a blocking finding (its own message said it merely costs density — a verdict that contradicted itself). Rejected fixing the sibling copies in skill_ergonomics_lib.py / validate_quality_artifact.py: the first must stay skill-local-portable, and porting the contract there is a scope increase — recorded as a non-claim and a queued follow-up instead.
- Targeted verification: Reproduced both variants pre-fix; 35 targeted tests green; revert-check via git apply -R makes the behavioral test fail on its own assertion ('prose past the exempt budget must pay density') and restores cleanly; live-corpus scan: 0 of 22 SKILL.md files produce a finding, and no skill gains a density charge; run_slice_closeout.py --skip-broad-pytest completed (sync, packaging, ruff, lengths, markdown, secrets, doc links, dup ratchet, boundary-bypass); full pytest run pending at the bundle boundary.
- Test duplication pressure: The dup ratchet hard-blocked at 5 new code families. Resolved by extraction (skill_gate_report_render, which its own triage recommended) down to 2, then 2 intentional classifications: 76b34d112c417b21 (the exemption walk exists twice by portability boundary, and the two copies now differ in semantics) and 8a9078e2e55bf7ff (repo-script bootstrap header; surfaced as a membership rotation, no member in this diff). Four membership-reduction advisories remain unaccepted.
- Critique: Two bounded rounds, both load-bearing. Round 1 (8 findings): the over-budget verdict contradicted its own message; the sentence heuristic false-positives on ordered lists and abbreviations; the splitter was not fence-aware; Load-Bearing Anchors had a 32-line budget with zero corpus usage; the corpus test generated its fixture from the constant under test (vacuous); no test drove the commit-boundary path; docs described the old contract. Round 2 caught a BLOCKER in round 1's own repairs: the fence fix used strip_fenced_lines, which dropped fenced lines from the density count — re-opening the same free-line hatch one layer down (setup/SKILL.md would have lost ~17 lines of charge). Repaired by suppressing heading detection inside fences while still counting the lines, and pinned by a new test. Round-2 repairs are accepted-unreviewed per the two-round cap.
- Off-goal findings: Three copies of the pressure-exempt walk exist: this module, skills/public/quality/scripts/skill_ergonomics_lib.py, and scripts/validate_quality_artifact.py. The other two keep the unbounded, unaudited semantics and a different exempt set, so S5 is closed at the author-time preflight ONLY and the two numbers diverge today on setup/prove/handoff/spec. Documented in authoring-preflight.md; queued as an operator decision. Also: skill_markdown_lib.extract_h2_section_lines reads only the FIRST matching H2 — the same first-block reading S5 was about, on a different consumer.
- Lessons carried forward: A repair aimed at a narrow trigger reached for the nearest existing helper (strip_fenced_lines) and inherited a semantic it did not want. The round-2 rule earned its cost here: round 1 could not have caught it, because the defect did not exist yet.
- Metrics: not available: no host token/time log exposed in this session

### Slice 2: Slices 2-5 — S7 bundle shape, S8 disposition, S21 chunk contract, S22 brief contract

- Objective: Close the remaining three repairs (S7, S21, S22) and record S8's disposition, so an absent, empty, or unrecognized input stops rendering a green verdict on each surface.
- Why this approach: One bundle: the three repairs are independent one-file changes of the same class, and reviewing them together let one fresh-eye round read the class rather than three near-identical slices.
- Commits: not yet committed; the bundle commits at slice 6
- What changed: scripts/validate_cautilus_diagnostics.py (BUNDLE_SHAPE_MARKERS, _is_non_diagnostic_tail, held-out/ + full-gate/ prefixes); scripts/hitl_review_artifact_lib.py (empty-input rejection, two-tier decision detection, fence-stripped signal text); skills/public/issue/scripts/audit_brief.py (arm on absent/late/unrecognized classification, reject empty transcript and non-numeric issue); scripts/skill_core_density.py + scripts/skill_markdown_lib.py + scripts/skill_gate_report_render.py (round-2 folds); tests/test_cautilus_diagnostic_artifact.py, tests/quality_gates/test_hitl_chunk_contract.py, tests/quality_gates/test_skill_surface_preflight.py, NEW tests/quality_gates/test_issue_audit_brief.py; charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md (five rows + a new status token + closeout non-claims); docs/conventions/authoring-preflight.md; plugins/ mirrors synced.
- Alternatives rejected: Rejected repairing S8 (the plan critique showed the reading was wrong and the repair would have turned the pre-push lane red for every future SKILL.md commit; operator confirmed the demotion). Rejected wiring audit_brief.py into the issue flow (operator chose checker-repair-plus-non-claim). Rejected porting the bounded exemption into skill_ergonomics_lib.py: it must stay skill-local-portable, so that copy is a queued operator decision and an explicit non-claim, not a silent divergence.
- Targeted verification: Every row reproduced first on a seeded repo, wrong output captured verbatim; targeted tests green; revert-check via git apply -R fails each new test on its own assertion; live cautilus --all still validates 34 bundles; a simulated held-out/ eval output dir does not redden the lane; tests/quality_gates + tests/test_cautilus_diagnostic_artifact.py = 4207 passed, 1 xfailed; full tests/ run earlier = 6332 passed (its single failure was an un-synced mirror mid-run, green after sync).
- Test duplication pressure: No new dup families from this bundle (the ratchet ran clean in the slice closeout after the earlier extraction and two intentional classifications). New test module tests/quality_gates/test_issue_audit_brief.py is in-process; the two subprocess-shaped additions went into modules already baselined for the boundary-bypass ratchet.
- Critique: Two bounded rounds. Round 1 (9 findings): the new NON_DIAGNOSTIC prefixes were inert in the --all arm because it compares a bare directory tail against slash-terminated prefixes, so --paths and --all disagreed; the test that appeared to prove them passed with them reverted; the marker list missed live capture outputs; the decision regex false-positived on descriptive prose and fenced examples; audit_brief still certified an empty transcript and crashed outside its error path on a non-numeric issue; pressure_exempt_findings audited fenced examples as the author's own prose. Round 2 (no blockers, 9 should-fix/nits) read those repairs: the two-tier regex had SILENCED ordinary request shapes (mid-line 'please approve', task-list and blockquote markers, table cells); the new fence walk repeated the earlier fence-bug class on an unbalanced or mixed-token fence; the fence strip was applied to the regex but not to the '?' and section-marker signals; and excusing fenced lines from the audit without charging them created a window that was both uncharged and unread. All folded: fences now close on the matching token and fail toward detection, fenced exempt lines always pay density and never consume budget, and the marker/stdin/renderer test gaps are closed. Round-2 repairs are accepted-unreviewed per the two-round cap.
- Off-goal findings: skill_markdown_lib.extract_h2_section_lines still reads only the FIRST matching H2 — the same first-block reading S5 was about, on a different consumer. Not repaired: no caller depends on multi-block behavior today.
- Lessons carried forward: The fence question came back three times in one goal (density count, density audit, chunk detection) and each independent fix got it slightly wrong in a different direction. A shared fence walk that closes on its opening token and declares its failure direction should have been the first move, not the third.
- Metrics: not available: no host token/time log exposed in this session

## Context Sources

- Source: handoff entry #1 (The sweep's remaining high rows) — see [docs/handoff.md](../../docs/handoff.md).
- Row detail and status vocabulary: [2026-07-28 triage sweep](../audit/2026-07-28-evidence-surface-triage-sweep.md).
  Read its `## Status vocabulary` before citing any row: `SUBAGENT-CONFIRMED` is
  not proof, and `CLOSED` requires parent reproduction plus a revert-failing test.
- Sibling class: [2026-07-27 evidence-surface hunt](../audit/2026-07-27-evidence-surface-bug-hunt.md)
  (class (a), empty/degenerate input still PASSes) and
  [why the class stayed invisible](../audit/2026-07-28-why-the-hunt-class-stayed-invisible.md).
- Review contract: [fresh-eye subagent review](../../skills/shared/references/fresh-eye-subagent-review.md)
  and the Critique Discipline section of [operating contract](../../docs/conventions/operating-contract.md)
  (verdict-logic surfaces owe a second review round).
- Repeat traps: [recent lessons](../retro/recent-lessons.md).
- Repo state at shaping: `main` at `0e8d9760`, clean except this artifact.
  `docs/handoff.md` still says `e011f3ff`; the v3.0.0 release commits landed after
  that line was written, so trust `git log`, not the handoff line, for the base sha.

## Interview Decisions

- **Scope.** Family considered: all five rows / the cautilus pair only / S5 only.
  Chosen: all five. Rejected the narrower options because each row is an
  independent slice that closes cleanly on its own, so a mid-run stop still lands
  on a row boundary and the narrow options only defer the same work.
  `single-point: the row set is this chunk's definition, not a system axis.`
- **Proof cost.** Family considered: full pre-push lane per slice / targeted tests
  per slice with the full lane at the bundle boundary. Chosen: the latter.
  Rejected per-slice full lanes because the lane is 82 gates and the marginal
  regression signal per slice is small next to the wall-clock cost.
  `axis: local-vs-CI validation cost — the repo already varies here (pre-push lane
  vs dispatched CI runs), and this goal deliberately sits on the local side.`
- **Timebox.** Family considered: none / 2h / 4h. Chosen: none; the goal ends on
  scope. Rejected timeboxing because no external deadline exists and a timebox
  would add early-close ledger obligations for no gain.
  `single-point: no operator time budget was given.`
- **Mode.** Artifact-only versus implementation-continuation was not asked: the
  chunker draft plus the operator's "진행" settles it as
  implementation-continuation, and `/goal` remains a separate explicit action, so
  a wrong read here cannot start execution by itself.
  `single-point: mode is a shaping-time intent, not a host axis.`
- **Host/model for reviews.** Not asked. This is a Claude Code host, so bounded
  reviews use the host's typed `bounded-reviewer` agent with session-model
  inheritance. `axis: host family — the repo's subagent default is split per host
  (Codex requests gpt-5.6-terra/medium; Claude Code uses its own typed agents), so
  no model is pinned here.`

## Plan Critique Findings

Reviewer provenance: one bounded read-only fresh-eye reviewer (Claude Code typed
`bounded-reviewer`, Read/Grep/Glob only), plan-critique pass on the draft above.
Parent boundary check: `reviewer_boundary_fingerprint.py` snapshot before /
verify after → `clean`, window `w-20260731T090151Z`. The parent independently
re-read the three pinning tests, the cautilus posture line, and the
`audit_brief.py` caller search before folding.

Blockers folded:

- **S8 was not a defect.** `cautilus-on-demand.md:21` makes deterministic
  validators the owner of prompt-affecting diffs, `run-quality.sh:530` runs the
  validator over the live diff with no `--paths`, and two checked-in tests pin the
  exit-0 behavior. The original plan would have turned the lane red for every
  future commit touching a SKILL.md unless the author ran a cautilus run the repo
  forbids by default — and slice 3's own evidence column contradicted its
  objective. Folded: slice 3 became a disposition, Boundaries and Acceptance
  updated, freshness residual queued.
- **S21 fused two defects.** Rejecting decision-free chunks would flip
  `tests/quality_gates/test_hitl_chunk_contract.py:71`, which pins informational
  chunks as legitimately passing. Folded: slice 4 now repairs the degenerate-input
  half and widens detection, and explicitly preserves that test.
- **S7 as written would flip `tests/test_cautilus_diagnostic_artifact.py:73`** and
  arm a future lane failure: the adapter's `held-out/`/`full-gate/` eval dirs write
  `summary.json`, which is in neither `MACHINE_EVIDENCE_NAMES` nor
  `NON_DIAGNOSTIC_DIR_PREFIXES`. Folded: narrowed to bundle-shaped-evidence dirs,
  with the prefix extension in the same slice.
- **Three slices must touch a pinning test.** Folded as a Boundaries rule plus a
  keep-or-re-pin step in the verification plan.
- **S22's one-line reading was incomplete** (late and unrecognized classifications
  disarm it identically) and the surface has no caller and no test module. Folded
  into slice 5 and the non-claims.
- **The S7/S8 shared-helper premise was false** — the two validators share only
  `surfaces_lib` path helpers. Folded: the ordering rationale no longer rests on
  it, and the real coupling (plugin mirrors) moved into the slice evidence.
- **S5's exemption hatch is wider than the row.** `## References` and
  `## Load-Bearing Anchors` are exempted with no anti-abuse pass at all, so 60
  lines of prose evade the density count with no second block needed. Folded:
  slice 1 makes the exemption uniform rather than patching the reported instance.
- **The revert-check was under-specified** for a shared worktree, and the
  reproductions needed seeded-repo/staging notes. Folded into the verification plan.

Raised as over-worry, not folded:

- Round-2 review for slice 6 (it decides nothing) — dropped, and the
  one-artifact-per-slice reading of the critique contract recorded instead.
- The boundary-bypass ratchet worry for the cautilus proof surface:
  `scripts/boundary-bypass-baseline.json:56` already baselines it. The rule stays
  in Boundaries; it does not shape the slices.
- Stop condition (3) (dup/changed-line ratchet) is disproportionate for five small
  edits in five unrelated files. Kept as a stop condition, not as a design driver.

Reviewer non-claims: it had no shell, so it executed none of the five
reproductions and could not verify the `0e8d9760` base sha or a clean tree — the
parent confirmed both. Every behavioral finding above is read from source plus
checked-in tests, which is exactly the provenance the sweep calls not-proof; each
slice still reproduces its own row before repairing it.

## Proof-Surface Dispositions

- `Fresh-eye pass: scripts/skill_core_density.py — proof surface (its findings
  block the preflight; its count drives the commit-boundary ratchet). Two bounded
  rounds. Round 1: over-budget blocked while its own message said it only cost
  density; the sentence heuristic false-positived on ordered lists and
  abbreviations; the splitter was fence-blind; a 32-line budget for a heading with
  zero corpus usage; the corpus test generated its fixture from the constant under
  test. Round 2 caught a blocker in round 1's own repair — the fence fix dropped
  fenced lines from the density count — plus a fenced-example false positive and a
  budget/audit window. All folded.`
- `Fresh-eye pass: scripts/skill_gate_report_render.py — not a proof surface, it
  renders no verdict: both callers compute `status` themselves and pass it in.
  Reviewer nit folded anyway (an explicit `blocked` flag, so an unrecognized status
  string cannot silently drop the remediation paragraph).`
- `Fresh-eye pass: scripts/validate_cautilus_diagnostics.py — proof surface. Round
  1 found the new non-diagnostic prefixes inert in the `--all` arm (bare directory
  tail vs slash-terminated prefix), a non-binding test, and a marker list missing
  live capture outputs; round 2 confirmed the prefix fix and asked for per-marker
  coverage. Folded.`
- `Fresh-eye pass: scripts/hitl_review_artifact_lib.py — proof surface. Round 1
  found false positives on descriptive prose and fenced examples; round 2 found the
  repair had silenced ordinary request positions and repeated the fence-bug class.
  Folded.`
- `Fresh-eye pass: skills/public/issue/scripts/audit_brief.py — proof surface.
  Round 1 found the sibling degenerate case (an empty transcript still `audit ok`)
  and a crash outside the error path. Folded.`

## Public-Skill Validation Decision

Changed public-skill surfaces: `create-skill` (a reference doc describing what the
density gate now does) and `issue` (`audit_brief.py`, a checker with no caller in
the skill's flow). `plan_cautilus_proof.py --detail` reports `status:
not-required`, `run_mode: ask`, `must_ask_before_running: true`, and no
log-backed behavior-proof request exists — so deterministic validation owns this
closeout and no live cautilus run was made or claimed. Reviewed
`evals/cautilus/scenarios.json`: neither change alters `create-skill`'s trigger,
routing, or acceptance evidence, and `issue`'s scenario does not exercise
`audit_brief.py`, so maintained scenario coverage does not change. Recorded, then
`--ack-cautilus-skill-review` passed.

## Coordination Cues

- Routing: shaped by `achieve` Before-phase after `handoff` chunked routing
  selected chunk 1; slices execute through `impl` + `prove`, plan and slice review
  through `critique` with bounded fresh-eye reviewers, closeout proof through
  `quality`, retro through `retro`. Routed from installed skill metadata and model
  judgment, not from an inline phase→skill map.
- Gather: n/a — no external source; every input is checked into this repo.
- Release: n/a — this goal ships no release surface (see Non-Goals).
- Issue closeout: n/a — this goal resolves no tracked GitHub issue. The live
  open-issue backlog was queried during chunked routing and returned zero open
  issues.

## Off-Goal Findings

## Final Verification

Self-verification (executed this run):

- Every row reproduced first on a seeded temp repo, wrong output captured
  verbatim, before any edit. S8 was reproduced too — and the reproduction is what
  showed the row described intended behavior.
- Per repair: targeted tests, then a patch-shaped revert-check
  (`git diff > p; git apply -R p; pytest; git apply p`) confirming the new test
  fails on its own assertion, naming the invariant, not on an import error.
- `run_slice_closeout.py --repo-root . --skip-broad-pytest --ack-cautilus-skill-review`
  → `Closeout status: completed` (sync, packaging, ruff, lengths, markdown,
  secrets, doc links, dup ratchet, skill ergonomics, boundary-bypass, mirror drift).
- Full `pytest tests/` → **6361 passed, 1 xfailed**.
- `prepush_focused_changed_line_coverage.py --repo-root . --base-sha 0e8d9760`
  → `clean`. It first reported one uncovered changed line (the unbalanced-fence
  fallback); that branch now has a test, committed as `ec72c301`.
- Live corpus checks: `validate_cautilus_diagnostics.py --all` validates 34
  bundles; a simulated `held-out/` eval output dir does not redden the lane; 0 of
  22 `SKILL.md` files produce an exempt-section finding.
- Commits: `4302aeaa` (the bundle), `ec72c301` (the coverage fix). Nothing pushed.

Retro: charness-artifacts/retro/2026-07-31-session-retro.md
Host log probe: skipped: host-log-not-exposed: the Claude host exposes per-message token snapshots and function-call counts thread-wide, but no per-goal window was set on this artifact, so no goal-scoped total exists to cite.
Disposition review: charness-artifacts/retro/2026-07-31-session-retro.md

Residual risks:

- S5 is repaired at the author-time preflight only; the portable
  `skill_ergonomics_lib.py` copy and `validate_quality_artifact.py` keep the
  unbounded, unaudited, fence-blind walk, so the two `core_nonempty` numbers
  diverge on any skill with a `## Closeout Vocabulary` block. Documented, queued.
- S21's widened detection is a floor, not a detector: a decision request phrased
  outside the known phrases and positions still passes silently.
- Round-2 repairs are accepted-unreviewed (the two-round cap).

Non-claims:

- No live cautilus run, no mutation-score lane, no CI dispatch, no push.
- S7 is proven against fixture bundles plus this repo's live corpus; that is not
  a claim about other repos.
- S22 repairs a checker with no caller in the `issue` workflow — a verdict fixed,
  not an enforced boundary.
- The reviewer-boundary fingerprint verified `parent-attributed` with no
  unattributed drift, but the path declarations are the parent's own: git proves
  the tree changed, never who changed it.


## User Verification Instructions

Run each row's trigger and see it fail where it used to exit 0:

```bash
# S21 — all three used to print {"status": "pass"}, exit 0
printf '' | python3 skills/public/hitl/scripts/check_chunk_contract.py
python3 skills/public/hitl/scripts/check_chunk_contract.py --chunk-text "Please approve or reject this rename before I continue."
# still passes, by design:
python3 skills/public/hitl/scripts/check_chunk_contract.py --chunk-text "Status update: still gathering evidence; no decision yet."

# S22 — used to print `audit ok: 1 fix-unit(s) checked`
printf '{"events":[{"kind":"mutation","issue":143,"tool":"Edit"},{"kind":"close","issue":143}]}' > /tmp/t.json
python3 skills/public/issue/scripts/audit_brief.py --transcript /tmp/t.json

# S5 / S7 — the reproductions live in the regression tests
python3 -m pytest tests/quality_gates/test_skill_surface_preflight.py tests/test_cautilus_diagnostic_artifact.py -q
```

Then confirm nothing ordinary broke: `python3 scripts/validate_cautilus_diagnostics.py --repo-root . --all`
(34 bundles) and `python3 scripts/run-quality.sh` for the full lane.


## Auto-Retro

Retro: charness-artifacts/retro/2026-07-31-session-retro.md

- Retro dispositions: applied: consolidated the three ad hoc fence walks into `skill_markdown_lib.split_fenced_lines` (token-matched close plus an explicit `unbalanced` flag), both consumers switched over, committed in `4302aeaa`
- Retro dispositions: applied: wrote the "S5 is closed at the preflight only" non-claim into `docs/conventions/authoring-preflight.md` and the sweep record's closeout section, so the next reader of either `core_nonempty` number sees the divergence
- Retro dispositions: accepted-risk: the "unify a structural walk on its second occurrence" lesson stays prose in the retro — it is a judgment habit rather than something a gate can express, and the duplicate ratchet already catches the mechanical half
- Retro dispositions: out-of-scope: teaching the changed-line gate to report subprocess-only coverage (carried from the 2026-07-30 retro) changes a blocking gate's payload and owes its own two-round review; this goal's scope was the sweep rows

Structural follow-up: applied: `scripts/skill_markdown_lib.py::split_fenced_lines` — one fence walk with a declared failure direction, replacing the three ad hoc walks this run kept re-deriving.

