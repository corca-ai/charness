# Achieve Goal: Next queue — #N-anchor edit-time guard, #338 gather X/Twitter exact-source, charness-update release-closeout

Status: draft
Created: 2026-06-09
Activation: `/goal @charness-artifacts/goals/2026-06-09-nanchor-guard-338-gather-release-update.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-09-nanchor-guard-338-gather-release-update.md`.
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

## Slice Log

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

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <change>` / `issue #N (recurs:|novel:)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
