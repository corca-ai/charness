# Achieve Goal: YouTube gather support and adapter renderer hygiene

Status: draft
Created: 2026-06-11
Activation: `/goal @charness-artifacts/goals/2026-06-11-youtube-gather-and-adapter-renderer-hygiene.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-11-youtube-gather-and-adapter-renderer-hygiene.md`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Implement the selected chunks from handoff pickup: #352 explicit YouTube gather-source support and #353 adapter_lib YAML renderer hygiene, keeping them as independent slices inside one auditable goal.

## Non-Goals

- Do not treat #352 and #353 as one shared implementation boundary. They are
  bundled only because the operator selected both chunks for one goal.
- Do not use authenticated browser profiles, private YouTube sessions, or
  policy-expanding hosted fetch paths unless a later operator explicitly
  approves that boundary.
- Do not push, release, or close issues as a side effect of activation. Issue
  closeout happens only through the repo issue-closeout carrier and proof path.
- Do not make `adapter_lib` a general YAML implementation. The renderer fix is
  limited to the current adapter seam's stated invariants and loud failure
  behavior.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- #352 is a gather/source-ingestion slice. It should preserve source identity,
  transcript freshness/source/language when available, and an honest
  metadata-only or blocked status when captions are unavailable.
- #353 is bug-class renderer hygiene. Run the debug/root-cause step before
  changing `scripts/adapter_lib.py` or its consumers, and prove newline,
  unsupported-construct, and falsy-explicit behavior with focused tests.
- When a change generalizes beyond the source repo, classify portability before
  closeout and sync exported/plugin surfaces before validation.

## User Acceptance

- For #352, a user can pass a YouTube URL through the supported gather path and
  inspect a durable gathered artifact that clearly distinguishes
  transcript-backed content from metadata-only or blocked acquisition.
- For #352, downstream summary or answer workflows can tell whether they are
  using a transcript or only metadata/chapters, so they do not imply stronger
  source proof than the gather artifact provides.
- For #353, newline-bearing scalar behavior no longer reparses incorrectly, and
  unsupported YAML constructs are refused or surfaced loudly instead of being
  silently normalized away.
- For #353, falsy-but-explicit known adapter fields are either preserved on
  render or honestly reported as not preserved; tests pin the chosen behavior.

## Agent Verification Plan

### Low-Cost Checks

- `python3 -m pytest` for focused tests covering the changed gather and adapter
  renderer modules.
- `python3 scripts/check_changed_surfaces.py --repo-root .` after the mutation
  shape is known, then run the required surface-specific checks it reports.
- `python3 scripts/sync_support.py --json` and
  `python3 scripts/update_tools.py --json` as dry-run sanity checks when public
  skill, support, export, or tool surfaces are touched.
- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.40.0/skills/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-11-youtube-gather-and-adapter-renderer-hygiene.md`
  after artifact edits.

### High-Confidence Checks

- Fresh-eye slice critique before locking each meaningful slice, with packet
  content scoped to the slice's changed files, invariants, tests, non-claims,
  and issue-closeout risk.
- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  before broad validation when a slice spans multiple validator families or
  generated/exported surfaces.
- Final `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock`
  once the mutation set is locked; add `--produce-mutation-coverage` if an
  eligible mutation-pool Python file is touched.
- `issue_tool.py validate-closeout-draft` and `verify-closeout` proof for #352
  and #353 if the final carrier intends to close the issues.

### External Or Live Proof

- Live YouTube/provider proof is optional and local-first. If unavailable or
  blocked by YouTube verification, record the blocked/partial artifact as the
  proof rather than claiming transcript-backed success.
- No authenticated/browser-profile proof is in scope without a new operator
  approval.
- Remote CI/push proof is not in scope for activation. If a later operator asks
  for push/issue closure, record the approval scope and proof path in this file.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Shape #352 YouTube gather contract from current gather/provider code and issue source context. | Avoid implementing a URL handler that cannot state transcript vs metadata-only proof honestly. | Source/context read; chosen artifact schema/status semantics; focused tests or spec notes named. | planned |
| 2 | Implement #352 YouTube URL handling and downstream confidence visibility. | Converts the recurring YouTube summary request into a durable gather path. | Focused gather tests for caption-available and blocked/unavailable cases, plus artifact fields proving source identity and partial status. | planned |
| 3 | Debug #353 adapter renderer failure modes before fixing. | #353 is bug-class work; root cause must precede patching. | Minimal reproductions for newline scalar, unsupported construct rewrite, and falsy-explicit handling. | planned |
| 4 | Fix #353 renderer hygiene and consumer status reporting. | Removes the latent config-corruption trap after the failure modes are pinned. | Focused adapter/quality-bootstrap tests; no silent lossy rewrite; falsy-explicit behavior matches status. | planned |
| 5 | Bundle closeout, critique, issue closeout draft, and final quality proof. | The slices are independent but share one operator-selected goal closeout. | Slice closeout proof, final goal artifact gate, retro/disposition, issue-closeout validation for #352/#353 when applicable. | planned |

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

- Routing: pending — use `find-skills` at each phase boundary; likely routes
  include gather/spec/impl/debug/quality/issue, but the current skill resolver
  owns the final choice.
- Gather: pending for #352 source context and YouTube source acquisition
  semantics.
- Release: n/a — no version bump or release surface is in the activation scope.
- Issue closeout: pending for #352 and #353; close only after carrier and
  validation proof exist.

Discuss before activation: resolved for draft shaping — operator explicitly
selected chunks 2 + 3 as one goal, despite the chunker finding no shared merge
boundary. Activation assumes local-only implementation, no authenticated
YouTube/browser proof, no push/release, and issue closure only after the
standard issue-closeout path is prepared.

## Slice Log

## Context Sources

- `docs/handoff.md` current pickup state on 2026-06-11.
- GitHub issue #352, "Support YouTube sources in gather skill"; source context
  includes YouTube URL `https://youtu.be/haK1KoQWm18` and Slack URL
  `https://corcaai.slack.com/archives/C09UJEA7S4R/p1781129246350739`.
- GitHub issue #353, "adapter_lib YAML renderer: unescaped newlines, lossy
  rewrite of unsupported constructs, falsy-explicit field drops".
- `charness-artifacts/retro/recent-lessons.md`, especially the current
  adapter_lib renderer hygiene follow-up.
- `docs/conventions/implementation-discipline.md` and
  `docs/conventions/operating-contract.md` for phase barriers, validation, and
  closeout discipline.

## Interview Decisions

- Mode: implementation-continuation once activated; rejected artifact-only
  because the operator said `achieve 2 + 3` after selecting concrete work
  chunks.
- Bundle shape: one goal with two independent slices; rejected pretending #352
  and #353 share an implementation boundary because the chunker found no merge
  basis and the source concerns differ.
- External proof: local-first unauthenticated YouTube handling; rejected
  browser-profile/authenticated access because it would expand policy and
  side-effect scope.
- Issue closure: prepare closure only after implementation, focused proof,
  critique, and issue-closeout validation; rejected closing on draft or on
  local implementation evidence alone.
- Push/release: out of activation scope; rejected bundling the existing
  branch-ahead push because the operator selected chunks 2 + 3, not `push`.

## Plan Critique Findings

- Act before activation: prevent over-merged execution by making #352 and #353
  separate slices with separate proof, even though they share one goal artifact.
  Folded into Boundaries and Slice Plan.
- Act before activation: make live/authenticated YouTube proof non-default, or
  the implementation could silently depend on credentials or a browser profile.
  Folded into Non-Goals and External Or Live Proof.
- Bundle anyway: one goal is acceptable because the operator explicitly selected
  both chunks and closeout can batch final proof without mixing implementation
  boundaries.
- Valid but defer: final fresh-eye critique and issue-closeout review belong at
  slice/final closeout, after the actual code and tests exist.
- Over-worry: requiring a full product-metrics ideation pass before #352 is not
  necessary for this selected goal; #184 remains outside scope.
- Fresh-Eye Satisfaction: n/a for draft shaping; required fresh-eye review is
  planned before slice/final closeout when concrete changes exist.

## Off-Goal Findings

N/A — draft shaping only; record issues or deferred findings discovered during
the active run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

- Activate only if the local-only proof and two-independent-slice bundle are
  acceptable: `/goal @charness-artifacts/goals/2026-06-11-youtube-gather-and-adapter-renderer-hygiene.md`.
- After completion, inspect the gathered YouTube artifact examples and the
  adapter renderer tests named in `## Final Verification`.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
