# Achieve Goal: Next queue — #N-anchor edit-time guard, #338 gather X/Twitter exact-source, charness-update release-closeout

Status: complete
Created: 2026-06-09
Activation: `/goal @charness-artifacts/goals/2026-06-09-nanchor-guard-338-gather-release-update.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 1 committed (7204940d); Slice 2 committed (40e492ed, Closes #338); Slice 3 COMPLETE (verification — the standing `charness update` step already shipped v0.29.0→v0.30.1; stale handoff corrected), awaiting its own commit + light fresh-eye verify.
- Next action: commit Slice 3, then final goal closeout (broad gate over the bundle, retro, handoff, complete).
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Clear the next operator-selected queue in three independent, per-slice-closed-out
slices: (1) **#N-anchor edit-time guard** — flag a `#<number>` issue anchor in a
skill-package file (`skills/public/**`, `skills/support/**`) at edit/preflight
time, before the commit-time `validate_skill_ergonomics` sweep, ending the
recurring authoring trap this session (and 3× last session) hit; (2) **#338** —
make `gather` acquire an exact X/Twitter source through a reliable fallback OR
stop honestly with "exact source unavailable" (never substitute a merely-similar
public source as if it were the original), with source-identity proof recorded in
the acquisition trace; (3) **charness-update release-closeout** — make
`charness update` on the dev machine a standing release-closeout step so the
installed plugin surface stays == repo (killing the scaffold/gate version-skew
class), subsuming the open v0.27.0 real-host smoke + nose checklist. Skill-script
changes are mirror byte-synced; each slice closes out independently.

## Non-Goals

- Do NOT bundle the three slices' closeouts into one commit — per-slice closeout
  (each slice commits with its own fresh-eye critique). Queue-clearing goal, not a
  cross-theme proof bundle.
- Do NOT remove or weaken the commit-time `validate_skill_ergonomics`
  `portable_package_issue_anchor` backstop — slice 1 is ADDITIVE author/preflight-
  time surfacing of the same rule, not a replacement (the commit sweep stays).
- Do NOT build a full X/Twitter scraper or vendor `fivetaku/insane-search`
  wholesale — slice 2 is the exact-source fallback + honest-stop + identity-proof
  contract scoped to #338's acceptance criteria; live X fetching is mocked by
  default.
- Do NOT take on #184 (product metrics — needs `ideation`/`spec`, operator left it
  out) or re-do #340 (closed this cycle).
- Do NOT cut a real release/push by default; a release is cut only when the
  operator explicitly authorizes it (slice 3 may define the closeout step without
  cutting a release in the same run).

## Boundaries

- **#N-anchor guard (slice 1).** Additive author-time/preflight surface that flags
  `#<number>` anchors in skill-package files BEFORE commit; reuse
  `skill_text_quality_lib.is_allowed_issue_anchor_context` so allowed contexts
  (generic issue-workflow placeholders, version fields, fenced code, single
  load-bearing trailing `(#NNN)` per standing-doc-provenance) do NOT false-positive.
  Classify the right home (quality author-time surface vs `.githooks` pre-commit-
  staged vs an edit-time preflight) before wiring. Mirror byte-sync if a skill
  script changes; a test covers a skill-package file with a disallowed `#N` anchor
  flagged at the new surface; behavior-preserving for the commit-time sweep.
- **#338 gather (slice 2).** `gather`-provider-ownership contract; a mocked test
  for an `x.com` status URL whose direct fetch returns captcha/bot-block; implement
  a working exact-source fallback OR mark the route unsupported so the agent stops
  honestly; require source-identity proof before treating a fallback result as the
  original; record skipped/failed fallback attempts visibly in the acquisition
  trace; the answer path can distinguish exact-fetched / exact-blocked /
  similar-source. Behavior-preserving for other gather sources. No live X fetch in
  tests (mocked).
- **charness-update release-closeout (slice 3).** `release`-contract change making
  `charness update` a standing release-closeout step (installed surface == repo);
  subsumes the v0.27.0 real-host smoke + nose checklist. The actual `charness
  update` run on this machine is operator/host-dependent — record it as the named
  external proof lane, not an autonomous claim.
- **Public-skill + generated-surface scope.** Any skill-script change mirror-synced
  (`plugins/charness/...`), deterministic gates own closeout, **no `#N` anchors in
  skill-package files** (the very trap slice 1 guards — apply it to this goal's own
  edits).
- Discuss before activation: RESOLVED — this goal intends to close **#338**
  (`issue_close_or_split` activation-discussion trigger fires legitimately). The
  consequential decisions, operator-selected (themes 1+2+4, #184 dropped) and
  resolved: (a) the goal targets the #N-anchor guard + #338 closeout + the
  charness-update release-closeout step; (b) one queue-clearing goal with per-slice
  closeout (re-splittable into three goals if a reviewer prefers); (c) slice 2's
  exact-source mechanism (a real syndication/oEmbed-style route vs an honest
  "unsupported → stop") is a probe resolved DURING slice 2 — either outcome
  satisfies #338's acceptance (no source-substitution). Live X fetching and any
  real release/`charness update` are operator-authorized external lanes, not
  autonomous defaults. Safe to activate; re-open if a reviewer disagrees.
- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication. Slice 3's `charness
  update` + any release is the named external lane.

## User Acceptance

What the user can do to verify completion directly.

- #N-anchor: editing a `skills/public/**` file that contains a disallowed
  `#<number>` issue anchor is flagged at the new author/preflight surface BEFORE
  the commit sweep; allowed contexts (version fields, generic placeholders) are not
  flagged.
- #338: `gather` on a captcha/bot-blocked `x.com` status URL either acquires the
  exact source or returns a clear "exact source unavailable" result (no
  source-substitution); the acquisition trace records the fallback attempts and the
  answer path distinguishes exact-fetched / exact-blocked / similar-source; #338
  closes.
- charness-update: the release-closeout contract documents/runs `charness update`
  so the installed plugin surface == repo.
- Each slice: the touched test surface passes, mirror byte-synced, and the
  per-slice fresh-eye critique attests correctness.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths --headroom` on every touched file.
- The touched test modules; `check_export_safe_imports` + `check_plugin_import_smoke`
  + mirror byte-sync for any skill-script change; `validate_skill_ergonomics` for
  slice 1; `issue_tool.py validate-closeout-draft` for #338.

### High-Confidence Checks

- The full quality / gather / release / find-skills test surface green; broad gate
  (`run-quality.sh --read-only`) at the bundle boundary (run the changed-line
  producer FIRST and cover new branches in the introducing slice). Fresh-eye
  `critique` at each slice boundary.

### External Or Live Proof

- #338: gather's X/Twitter route is **mocked** by default (no live X fetch); a live
  acquisition is an operator-authorized lane only.
- charness-update / release: the actual `charness update` run + any release/push is
  operator/host-dependent — recorded as the named external proof lane (record
  `Release:` scope), not an autonomous claim.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | #N-anchor edit-time guard: flag `#<number>` anchors in skill-package files at author/preflight time (reuse `is_allowed_issue_anchor_context`); commit-sweep stays the backstop | recurring authoring trap (3× last session + 1× this session); session retro structural follow-up; bounded | new author/preflight surface flags a disallowed `#N` anchor; allowed contexts pass; test; mirror synced; `validate_skill_ergonomics` green | planned |
| 2 | #338: exact X/Twitter source fallback OR honest "exact source unavailable" stop + source-identity proof + visible fallback trace | open issue with clear acceptance criteria + a real wrong-outcome cost (source substitution) | mocked `x.com` captcha test; fallback-or-honest-stop; identity proof; trace records skipped/failed; answer path distinguishes exact/blocked/similar; #338 closeout draft validates | planned |
| 3 | charness-update standing release-closeout step (installed == repo); subsumes v0.27.0 real-host smoke + nose checklist | handoff operator-requested; kills the scaffold/gate version-skew class | release contract documents the `charness update` closeout step; the version-skew motivation captured; release proof recorded when a release is cut | planned |

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

### Recorded routes

- Routing: impl — find-skills task-recommendation routed implementation work to the
  matched durable work skill (impl); achieve operates the goal while find-skills owns
  which skill answers each boundary. Slice 1 extended the quality skill-surface
  preflight; slice 2 the gather/web-fetch provider surface; each slice critique routed
  to critique (three fresh-eye SHIP verdicts).
- Routing: quality — find-skills capability map routed validation and closeout to
  quality (validate_skill_ergonomics, the skill-surface preflight, run_slice_closeout,
  and the changed-line mutation producer).
- Routing: issue — find-skills routed the #338 resolution and closeout to issue
  (issue_tool.py validate-closeout-draft, direct-commit carrier).
- Gather: n/a — #338 is the gather provider being BUILT, not an external source to
  acquire into a knowledge asset; X/Twitter acquisition is mocked (no live fetch).
- Release: n/a (no release cut this run — non-goal) — the standing `charness update`
  release-closeout step ALREADY shipped (v0.29.0 manual → v0.30.1 auto-run): adapter
  `post_publish_install_refresh: charness update` + `publish_release.py` auto-run +
  `install-surface.md`. External lane (operator/host): the actual `charness update` +
  `nose` install at the next release. Verified read-only this run: installed plugin
  `0.33.0` == released `v0.33.0`; `test_release_publish_resilience.py` green (20);
  nose doctor `managed_checkout: true` + upstream installer route.
- Issue closeout: #338 — carrier `direct-commit` (`Closes #338` in the slice-2
  commit; closes on the operator's push to main). Proof: `issue_tool.py
  validate-closeout-draft` → `draft_verified` (ok: true); resolution critique
  `charness-artifacts/critique/2026-06-09-issue-338-gather-exact-source.md`.

## Slice Log

### Slice 1: Slice 1 — #N-anchor edit-time guard

- Objective: Additive fast edit-time scan flagging disallowed #NNN/issue anchors in a skill-package file BEFORE the commit-time validate_skill_ergonomics sweep; commit sweep stays the backstop.
- Why this approach: Recurring authoring trap (3x last session + 1x this) is the edit->closeout->blocked->fix round-trip. A sub-second per-file scan the author runs right after editing removes it. Home: extend the canonical authoring preflight (check_skill_surface_preflight.py), delegating to a new cohesive module to keep the preflight under its length limit (it was at 391/480; inline would have hit 471/480 NEAR-LIMIT, so extracted per the start-a-new-module-near-limit contract).
- Commits:
- What changed: skill_text_quality_lib.py +issue_anchor_findings_for_file (reuses ISSUE_ANCHOR_RE + is_allowed_issue_anchor_context, with __pycache__ parity); NEW scripts/skill_issue_anchor_scan.py (self-contained per-file scan); check_skill_surface_preflight.py +--scan-issue-anchors CLI delegating to it; docs/conventions/authoring-preflight.md +Edit-time issue-anchor scan subsection; NEW tests/quality_gates/test_skill_issue_anchor_scan.py (16 tests). Mirror byte-synced (plugins/charness/...).
- Alternatives rejected: (a) .githooks pre-commit staged check — rejected: the sweep already blocks at pre-commit/closeout, so the marginal value is edit-time, not commit-time. (b) inline in the preflight — rejected: pushed it to 471/480 NEAR-LIMIT. (c) enhance the closeout advisory — rejected: redundant (gated behind the already-blocking sweep).
- Targeted verification: 16 new tests pass; existing preflight (47) + ergonomics/text-quality (78) green; py_compile/ruff/lengths clean (preflight 408/480, new module 79/480, lib 187/360); validate_skill_ergonomics green (behavior-preserving); mirror drift none; CLI dogfood: clean->ok/exit0, anchor->BLOCK/exit1, bad path->exit2.
- Test duplication pressure: Low. New module reuses a generic _write tmp-file helper; distinct concern (anchor scan) from the existing preflight test's headroom focus; no assertion/fixture duplication that should be shared.
- Critique: Fresh-eye bounded reviewer (general-purpose, read-only): SHIP. Verified all 5 invariants incl. a 452/452 real-file differential (per-file verdict == commit-sweep verdict, zero mismatch). One non-blocking nit (pycache parity) applied as a 1-line hardening + test.
- Off-goal findings:
- Lessons carried forward: Covered every new branch (incl. the pycache exclusion and outside-repo error) in this slice so the bundle-boundary mutation producer confirms rather than discovers.
- Metrics:

### Slice 2: Slice 2 — #338 gather X/Twitter exact-source

- Objective: Acquire the EXACT X/Twitter post via identity-keyed fallback OR stop honestly with 'exact source unavailable' — never substitute a similar source. Source-identity proof, visible failed-attempt trace, answer-path distinction.
- Why this approach: The web-fetch twitter-syndication route already classified x.com/twitter.com but its domain-specific-route stage was a literal not-implemented skip (the exact gap #338 names). Implemented that stage: parse status URL, identity-keyed endpoints (syndication CDN by status id, then oEmbed), verify returned id == requested id before accepting as original. Probe resolved to a REAL exact-source route (criterion #2 option 1) with honest-stop fallback when blocked. Live fetch injected/operator-gated (no autonomous live X).
- Commits: (staged this slice; carrier direct-commit, Closes #338)
- What changed: NEW skills/support/web-fetch/scripts/twitter_exact_source.py (parse/endpoints/identity-verify/classify_source_identity/make_fetcher); acquire_public_url.py runs the stage for twitter-syndication + emits source_identity + --domain-route-response-file/--live-domain-route; gather_public_url.py surfaces source_identity + passthrough (extracted _build_acquire_cmd); routing-table.md + gather-provider-ownership.md contract; NEW tests/test_twitter_exact_source.py (19). Mirror byte-synced.
- Alternatives rejected: (a) full X scraper / vendor fivetaku/insane-search — rejected (non-goal, over-build). (b) honest 'unsupported' stop only — viable per #338 option 2, but the syndication/oEmbed identity-keyed route is reliable and adds real value, so implemented it WITH honest-stop as the fallback. (c) autonomous live fetch default — rejected: live X is operator-gated per goal.
- Targeted verification: 19 new tests (unit + subprocess integration, all mocked/seeded — no live X); 56 existing web-fetch/gather tests green; ruff/py_compile/lengths clean; validate_skill_ergonomics green; slice-1 anchor scan green on the edited skill-package files (dogfood); doc links + markdown green; #338 closeout draft draft_verified (ok:True).
- Test duplication pressure: Low-moderate. New test module is self-contained; the _fetcher mock + seeded subprocess helpers are local to the X concern; no shared-fixture duplication that should be hoisted.
- Critique: Fresh-eye bounded reviewer (general-purpose, read-only): SHIP, all 6 invariants verified live (mismatch->invalid-proof->non-success; non-twitter omits source_identity; no network primitives). One bundle-anyway finding (oEmbed URL-echo proves requested-id match not existence) folded this slice: require a rendered body + covering test. Recorded: charness-artifacts/critique/2026-06-09-issue-338-gather-exact-source.md.
- Off-goal findings:
- Lessons carried forward: Reused the existing acquisition-trace machinery (AcquisitionAttempt/classify/disposition) rather than a parallel trace; kept acquire wiring thin and the X logic in a new module to respect length limits.
- Metrics:

### Slice 3: Slice 3 — charness-update release-closeout step

- Objective: Make charness update a standing release-closeout step (installed surface == repo), subsuming the v0.27.0 real-host smoke + nose checklist; the actual run is the operator/host lane.
- Why this approach: Investigation finding: the in-repo deliverable ALREADY SHIPPED (v0.29.0 manual closeout step -> v0.30.1 auto-run). The release adapter declares post_publish_install_refresh: charness update; publish_release.py auto-runs it after a verified publish and records install_refresh (refreshed/failed/not_configured) as a closeout risk; install-surface.md documents the step + the version-skew motivation + that it subsumes the v0.27.0/v0.28.0 smoke; real_host_checklist carries the nose smoke. A NEW deterministic 'installed == repo packaging version' check would be WRONG (the repo is normally ahead of the last released/installed version between releases -> noisy); the correct invariant is installed == latest RELEASED, which the auto-refresh ensures. So slice 3 is verification + stale-handoff correction, not new code.
- Commits: (staged this slice)
- What changed: docs/handoff.md — corrected the stale 'Make charness update a standing release-closeout step' Next-Session to-do to reflect it SHIPPED (v0.29.0->v0.30.1), with the verified state. No code change: the release-contract deliverable pre-existed and a new installed-vs-repo check would be noisy/wrong.
- Alternatives rejected: (a) add a deterministic installed==repo check — rejected: repo HEAD is normally ahead of the last release between releases, so it would noisily report 'skew' on normal state; the right check is installed==latest-released, already ensured by the auto-refresh. (b) automate the real-host smoke — rejected: install-surface.md intentionally keeps it as release-time HUMAN proof, not standing CI. (c) cut a release to exercise the auto-refresh — rejected: non-goal (no release by default).
- Targeted verification: tests/quality_gates/test_release_publish_resilience.py green (20); adapter post_publish_install_refresh + publish_release auto-run wiring confirmed; install-surface.md contract + version-skew motivation present; read-only standing real-host checklist parts pass on this machine (installed plugin 0.33.0 == released v0.33.0; nose doctor managed_checkout=true + upstream nose-cli-installer.sh route; nose install --dry-run points at the upstream release path).
- Test duplication pressure:
- Critique: Fresh-eye bounded reviewer (general-purpose, read-only): SHIP. Independently verified all 4 claims against the repo (adapter+helper auto-run wiring; install-surface.md contract; the "installed==repo would be redundant not a missed gap" reasoning; handoff edit accuracy + version triple-check). Specifically hunted for a missed non-noisy check (an `install_refresh != failed` closeout gate) and ruled it out — blocking on it would contradict the deliberate non-blocking design. No code warranted.
- Off-goal findings: The handoff 'Next Session' charness-update item was STALE — it requested building a step that already shipped (v0.29.0->v0.30.1), predating this goal. Corrected in docs/handoff.md this slice. Root: the handoff to-do was carried forward across sessions without reconciling against the v0.29.0/v0.30.1 implementation.
- Lessons carried forward: Before building a handoff-sourced 'next step', verify it isn't already shipped — reconcile the handoff to-do against the actual repo/release state first.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **#N-anchor guard (session retro structural follow-up):**
   `charness-artifacts/retro/2026-06-09-deferred-queue-341-340-activation-preflight.md`
   (the `none — accepted-risk` disposition recommending an edit-time guard) and the
   commit-time backstop `skills/public/quality/scripts/skill_text_quality_lib.py`
   (`issue_anchor_package_findings` / `is_allowed_issue_anchor_context`, heuristic
   `portable_package_issue_anchor`) reached via `validate_skill_ergonomics`.
2. **#338 (gather X/Twitter exact-source):** `gh issue view 338` — exact `x.com`
   acquisition failed and a similar public source was substituted; acceptance
   criteria in the issue body. Surface: `docs/gather-provider-ownership.md` +
   `skills/public/gather`. Reference (not vendored): `fivetaku/insane-search`.
3. **charness-update release-closeout:** `docs/handoff.md` "Next Session"
   (operator-requested standing step; version-skew motivation) +
   `charness-artifacts/release/latest.md` (the open v0.27.0 real-host smoke + nose
   checklist this subsumes). Owner: `release` contract.
4. **Recent-lessons:** `charness-artifacts/retro/recent-lessons.md` — the #N-anchor
   accepted-risk recurrence and the coverage-producer in-slice-branch guardrail
   (apply the latter when adding new functions this goal).
5. **Tracked-but-out-of-scope (NOT this goal):** #184 (product metrics — needs
   `ideation`/`spec`).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Which next work (operator-selected).** Family offered: {#N-anchor edit-time
  guard; #338 gather X/Twitter; #184 product metrics (ideation); charness-update
  release-closeout}. Chosen: **#N-anchor guard + #338 + charness-update** (operator
  picked 1+2+4). Rejected: #184 (product-level, needs `ideation`/`spec`, not a code
  slice). `axis: theme` — each tracked independently.
- **Single multi-slice goal vs three separate goals.** Chosen: **one
  queue-clearing goal with per-slice closeout** (operator pattern from the prior
  goal). Re-splittable if a reviewer prefers.
- **Slice 1 home (probe, not fixed).** Family: {new quality author-time preflight
  surface; `.githooks` staged pre-commit edit-time check; extend an existing
  authoring preflight}. Deferred to slice 1 — classify before wiring; the
  commit-sweep stays the backstop regardless.
- **Slice 2 mechanism (probe, not fixed).** Family: {real syndication/oEmbed-style
  exact route; honest "unsupported → stop"}. Either satisfies #338's
  no-source-substitution acceptance; resolved during slice 2.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. (Shaping-phase self-critique; a fresh-eye
plan critique is part of activation.)

- **Slice 1 false positives could block legitimate edits.** Folded: reuse the
  existing `is_allowed_issue_anchor_context` allow-list so the new surface mirrors
  the commit-sweep verdict exactly; behavior-preserving boundary + a test for an
  allowed context.
- **Slice 2 over-build (full scraper / vendor the reference repo).** Folded:
  Non-Goals scope slice 2 to the acceptance criteria (fallback-or-honest-stop +
  identity proof + trace), live fetch mocked.
- **Slice 3 leans on an operator/host action (`charness update`).** Folded: the
  actual run is the named external lane; the slice's in-repo deliverable is the
  release-contract step + version-skew motivation, not the host run.
- **Over-worry (raised, not folded):** that the #N-anchor guard duplicates the
  commit sweep with no new value — kept visible for the activation critique;
  counter: the recurrence cost is edit→commit→fix round-trips, which an edit-time
  surface removes.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- **Stale handoff to-do (resolved this run).** Slice 3's goal — "make `charness
  update` a standing release-closeout step" — had ALREADY shipped (v0.29.0 manual
  → v0.30.1 auto-run): adapter `post_publish_install_refresh` + `publish_release.py`
  auto-run + `install-surface.md`. The handoff "Next Session" to-do was carried
  across sessions without reconciling against that implementation. Corrected in
  `docs/handoff.md` this run (slice 3).
- **Transferable sibling (recommend to operator, not auto-filed).** The GitHub-issue
  closeout-draft (`issue_tool.py validate-closeout-draft`) has no author-time shape
  preflight, unlike the 7 artifact surfaces `check_artifact_surface_preflight`
  covers — the same authoring-preflight class as #284→#334. It cost 4 discovery
  round-trips this run (resolution_critique, `tool signal:`, carrier-body source,
  feature ledger fields). Recorded in the retro `## Sibling Search` + recent-lessons
  + handoff for an operator decision; out of this goal's non-goal scope to file.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-09-nanchor-guard-338-gather-release-closeout.md
Host log probe: skipped: host-log-not-exposed: the goal set no Host metric window line, so no scoped host-log audit applies; efficiency was reviewed via proxy gate round-trips in the retro instead of measured token/time.
Disposition review: charness-artifacts/critique/2026-06-09-nanchor-guard-338-gather-release-disposition-review.md

## User Verification Instructions

- **#N-anchor:** edit a `skills/public/**` or `skills/support/**` file to add a
  disallowed anchor and scan it:
  `python3 scripts/check_skill_surface_preflight.py --scan-issue-anchors <file>` —
  a `#NNN`/`owner/repo#N`/`issues/N` anchor exits 1 (BLOCK) with file:line; an
  allowed context (version field, placeholder issue URL) exits 0. The commit-time
  `validate_skill_ergonomics` sweep is unchanged (still green).
- **#338:** seed a captcha direct fetch + an exact-source response and acquire an
  `x.com` status URL:
  `python3 skills/support/web-fetch/scripts/acquire_public_url.py --url
  https://x.com/<h>/status/<id> --direct-response-file <captcha> --domain-route-response-file <seed>`
  — `source_identity` reads `exact-fetched` on an id match, `exact-blocked` on a
  block/mismatch, `exact-unavailable` with no seed; a mismatched id is `invalid-proof`
  and never substituted. `gather_public_url.py` surfaces `source_identity` in the
  record. `gh issue view 338` shows the `Closes #338` carrier (closes on push).
- **charness-update:** `python3 -m pytest tests/quality_gates/test_release_publish_resilience.py`
  (20 green); `install-surface.md` "Maintainer Dev-Machine Install Refresh"
  documents the auto-run step; installed plugin `0.33.0` == released `v0.33.0`.

## Auto-Retro

Retro dispositions: applied: the three surfaced improvements are each shipped this run (the #N-anchor edit-time surface, in-slice branch coverage confirmed by the bundle producer, and the stale-handoff correction); no improvement is laundered to a narrow issue. Per-improvement:

- applied: `scripts/skill_issue_anchor_scan.py` + `check_skill_surface_preflight.py --scan-issue-anchors` (slice 1, commit 7204940d) — the #N-anchor recurring authoring trap now has the edit-time surface its prior `none — accepted-risk` disposition recommended; recent-lessons upgraded accepted-risk to applied.
- applied: changed-line coverage closed for the bundle (commit a2046a95) — the rung-2 disposition review caught that the first producer pass left `twitter_exact_source.py:27` (the guarded `sys.path` bootstrap, never hit under test) as an uncovered changed line and the earlier `ok:True` was the stale-fingerprint SKIP, not a confirmation; a focused bootstrap test now covers it and the re-run producer confirms genuinely (`ok:True`, fresh fingerprint, `blocking:[]`, 0 uncovered changed lines over `81f2e1ab..HEAD`). This is the same #335/#341 "discovered not confirmed" class the goal's own lessons name.
- applied: `docs/handoff.md` corrected (slice 3, commit 5c20547f) — the stale `charness update` standing-step to-do no longer misdirects the next session.

Structural follow-up: none — the transferable sibling (author-time issue-closeout-draft preflight, the #284 to #334 class) is an outward-facing capability recommendation; recorded in the retro `## Sibling Search` + recent-lessons + handoff for an operator decision, not auto-filed per this goal's non-goal (do not take on other tracked issues this run).
