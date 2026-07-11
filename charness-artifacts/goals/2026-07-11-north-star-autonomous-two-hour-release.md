# Achieve Goal: North-Star Autonomous Two-Hour Release

Status: active
Created: 2026-07-11
Activation: `/goal @charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release.md`
Timebox: 2h
Activation time: 2026-07-11T20:05:59+09:00
Closeout reserve: 20m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: shape and critique the two-hour autonomous improvement plan.
- Current slice intent: fix the two evidence-backed follow-ups first, continue
  through additional safe north-star slices until the closeout reserve, then
  publish one reviewed patch release.
- Next action: complete plan critique, pass pursue readiness, and start Slice A.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Improve Charness autonomously for two hours from diverse perspectives, starting
with the two concrete handoff defects, and publish one verified patch release
whose public behavior is checked through a distinct evidence channel.

## Non-Goals

- Do not close #433 or any other issue; the user authorized push and release,
  not issue close.
- Do not manufacture work to fill time, optimize lexical counts, or add a new
  blocking gate without recurrence evidence and floor-addition review.
- Do not introduce a generic host abstraction without a demonstrated consumer.
- Do not claim provider/live behavior from local deterministic tests.

## Boundaries

- Reversible local mutation is authorized throughout the timebox.
- Push, tag, GitHub release creation, and maintainer install refresh are
  authorized only for the final reviewed bundle. No per-slice push.
- The release carrier is the complete `merge-base(origin/main, HEAD)..HEAD`
  range: twenty pre-existing local commits plus this run. Preserve history; do
  not squash, rebase, or cherry-pick the carrier.
- Release target is only a patch candidate (`0.66.2`). After mutation closes,
  inventory every consumer-visible surface in the full carrier and choose the
  lightest honest version before release mutation.
- GitHub release visibility is provisional until a distinct observer reads the
  public surface through a channel different from the release backend readback.
- Issue close is explicitly outside the authorized external lane.
- Publication is conditional on behavioral acceptance, full-carrier version and
  release-note classification, a valid verification lock, release dry-run,
  fresh checkout proof, and fresh-eye release approval. Authorization is not a
  success oracle; a failed precondition leaves the reviewed bundle local.
- At T+100m stop all new feature mutation. At T+110m publish may begin only if
  mutation is closed, generated surfaces are synced, the expected diff is
  committed, verification is bound to HEAD, release critique is complete, the
  tree is clean, and dry-run/version checks pass. At T+120m perform only an
  already-started publication's required readback/evidence capture.
- Any changed path or commit after verification lock invalidates downstream
  proof and returns the run to sync and verification.
- After external mutation, never delete or repoint a public tag as automatic
  rollback. Record partial state and use the repo helper's resume path when safe;
  otherwise report `published, verification incomplete` as an open risk.

## User Acceptance

- `main` and the release tag are visible on origin at the reported SHA.
- GitHub shows the new patch release and its notes describe the delivered value.
- For a non-default quality scaffold `--title`, the emitted first line remains
  exactly `# Quality Review`, the custom title survives as non-H1 metadata, and
  the real validator accepts source and exported-plugin output without repair.
- Coverage Slice B starts with a reproduction recording producer/consumer
  commands, resolved bases, changed pools, and fingerprints. If a supported
  explicit anchor is required, broad and focused producers share it, the
  matching consumer reuses the marker without another producer run, mismatch
  still rejects, and the default `origin/main` pre-push path is unchanged.
- After public verification, `charness update` reports the new version; an
  independent `charness --version` and readiness/doctor check confirm it. Fresh
  install remains a non-claim unless actually executed.
- Release notes account for every user/operator-visible change in the full
  carrier; internal-only omissions are classified, and update, migration or
  rollback disposition, known risks, and non-claims are explicit.
- A fresh observer that did not publish fetches the unauthenticated public
  release through HTTPS and records URL, timestamp, HTTP status, visible tag,
  title, notes/value verdict, and assets. HTTP 200 alone is insufficient.
- #433 remains open.

## Agent Verification Plan

### Low-Cost Checks

- Focused pytest for each changed helper and its importer/registry consumers.
- Ruff, pycompile, mirror parity, artifact validators, and doc preflights.
- Cheap closeout rehearsal before each substantial slice commit.

### High-Confidence Checks

- Fresh-eye slice critique with rail-1 worktree/index fingerprints.
- One final verification-lock closeout with changed-line coverage for eligible
  Python changes and release dry-run before external mutation.
- Fresh-checkout probes declared by the release adapter.

### External Or Live Proof

- Push branch and tag only through the repo-owned release helper.
- Pre-publish, prove the helper invocation has no issue-close option and final
  carrier text has no close keyword targeting #433; record an OPEN readback.
- Post-publish, a different observer reads the public HTTPS surface and signs a
  content-bearing verdict; the publishing agent's backend readback cannot
  satisfy this item.
- Run post-publish install refresh and version/readiness checks.
- Re-read #433 OPEN after publication and after any final artifact push. Any
  unexpected closure is an escaped external-state failure, not success.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Repair quality scaffold custom-title/H1 contract | Concrete repeat trap and first active handoff slice | focused scaffold + validator tests | planned |
| B | Diagnose coverage producer/consumer anchor mismatch; fix only if reproduced | Avoids changing an intentional pre-push default from an ambiguous symptom | reproduction packet, then focused freshness/closeout tests or explicit not-reproduced disposition | planned |
| C | Admit only evidence-backed safe improvement(s) | Continue without manufacturing work | captured failure/repeat-waste owner, bounded proof, commit before T+100m | planned |
| D | Bundle critique, quality lock, release prep | Locks the final mutation set before publication | critique artifact, closeout, dry-run | planned |
| E | Push and publish patch release | User-authorized irreversible boundary | public release URL, distinct-channel readback, install refresh | planned |

## Operator Decision Queue

- none — final push and patch release are explicitly authorized; issue close is
  explicitly excluded.

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

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the find-skills-recommended skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: find-skills -> <skill> — <why this phase needs it>`

- Routing: find-skills -> release — release is the confirmed external-boundary owner; the higher-ranked issue match came only from the explicit issue-close exclusion.
- Gather: n/a — no external source is input to the local improvement slices.
- Issue closeout: n/a — #433 is context only and must remain open.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: approved — the user explicitly authorized a final push and patch release after the two-hour autonomous run; issue close remains excluded, and public release success requires distinct-channel evidence.

## Slice Log

### Slice 1: Slice A — canonical quality scaffold H1

- Objective: Repair custom-title scaffolding so every emitted quality artifact satisfies the validator-owned H1 invariant while preserving the caller title.
- Why this approach: Fix the producer at the ownership boundary; keep the validator strict and preserve custom input as additive metadata.
- Commits: `b6c2b7fe` (`Keep quality scaffold titles validator-safe`)
- What changed: Canonical # Quality Review H1; Title metadata; direct, CLI, and exported-plugin real-validator tests; regenerated plugin mirror.
- Alternatives rejected: Rejected weakening the validator, dropping custom titles, adding a new title schema, or adding a mirror-only duplicate test.
- Targeted verification: 24 focused tests passed; real validator executed across direct/CLI/exported paths; source/plugin cmp and ergonomics/anchor scans passed.
- Test duplication pressure: One existing exported-plugin test was extended; two focused source/CLI branches added without a new fixture family.
- Critique: Full fresh-eye critique at charness-artifacts/critique/2026-07-11-quality-scaffold-h1.md; initial packet-scope finding cleared after working-tree packet regeneration; rail-1 zero drift.
- Off-goal findings: Coverage anchor mismatch remained separate Slice B; no Cautilus run because the repo contract is ask-before-run and deterministic/runtime proof is sufficient.
- Lessons carried forward: Prepare critique packets without --changed-ref when the target is an uncommitted slice; a HEAD packet inventories the carrier rather than the worktree.
- Metrics: 24 focused tests; 3 behavior paths; 0 remaining act-before-ship findings.

### Slice 2: Slice B — one campaign anchor for coverage proof

- Objective: Prevent a closeout campaign with an explicit base from producing a freshness marker over a different range or paying for a second full producer run.
- Why this approach: Resolve the explicit ref once in closeout orchestration, reuse that SHA for committed-range collection and broad/focused producers, and leave omitted/auto behavior on origin/main.
- Commits: `9deca0ca` (`Keep coverage proof on one campaign anchor`)
- What changed: Optional base_sha propagation; resolved-SHA changed-path helper; CLI help correction; root/plugin sync; causal explicit/default/auto and producer-consumer tests.
- Alternatives rejected: Rejected a new CLI option, campaign-anchor object, double ref resolution, weakening freshness checks, and a broad closeout-module split.
- Targeted verification: 78 focused tests passed; explicit main path proves one resolution and one SHA across range/broad/focused; omitted/auto prove None fallback; real marker accepted then rejected after pool drift; mirrors byte-identical.
- Test duplication pressure: Extended existing closeout and mutation producer modules; replaced a weak hash comparison with consumer-contract proof.
- Critique: Full fresh-eye critique at charness-artifacts/critique/2026-07-11-coverage-anchor.md; F1/F2/F2R cleared over two revisions; three rail-1 verifies reported zero drift.
- Off-goal findings: run_slice_closeout remains at 478/480 code-line advisory headroom; broader decomposition is valid but not admitted into this bounded slice.
- Lessons carried forward: A moving ref is state, not a string: resolve it once at the owner and pass the immutable value to all consumers. Test orchestration, not only helpers.
- Metrics: 78 focused tests; 1 resolved SHA; 3 consumers; 0 remaining act-before-ship findings.

### Slice 3: Slice C — delete one superseded regex, retain intentional markers

- Objective: Remove confirmed internal dead code without laundering low-confidence advisory findings into broad cleanup.
- Why this approach: Inspect static references, dynamic registries, history, and tests; delete only the regex replaced by AST detection and keep five intentional/deferred candidates.
- Commits: pending this slice checkpoint
- What changed: Removed MODULE_RELEASE_ONLY_RE from canonical quality helper and regenerated plugin mirror; no behavior or API change.
- Alternatives rejected: Rejected deleting gate markers, public vocabulary constants, dynamic helpers, adding a dead-code floor, or changing the live AST implementation.
- Targeted verification: 17 standing-test economics tests passed; ruff, AST parse, attention-state validator, mirror cmp, and diff check passed.
- Test duplication pressure: No new tests; existing behavior suite already exercises the live AST replacement.
- Critique: Fresh-eye candidate classification and post-change confirmation at charness-artifacts/critique/2026-07-11-superseded-release-regex.md; rail-1 zero drift.
- Off-goal findings: Five advisory candidates retained with explicit dynamic/intentional/deferred dispositions.
- Lessons carried forward: Low-confidence dead-code output is a review queue, not a deletion list; history can prove a constant is a marker rather than executable data.
- Metrics: 6 candidates reviewed; 1 safe deletion; 5 retained; 8 derived lines removed; 0 remaining act-before-ship findings.

## Context Sources

- `docs/handoff.md` — ordered active defects and irreversible boundaries.
- `charness-artifacts/retro/2026-07-11-truthful-standing-delegation-retro.md`
  — measured scaffold and coverage-anchor waste.
- `docs/design-north-star.md` — judgment on reversible work, distinct-channel
  proof at release.
- `charness-artifacts/release/latest.md` and release planner output — current
  `0.66.1` surface and publish contract.

## Interview Decisions

- Mode family: artifact-only vs implementation-continuation; chosen
  implementation-continuation because the user said to proceed for two hours
  and release afterward; artifact-only rejected because it would strand work.
- Version axis: patch/minor/major; chosen patch candidate `0.66.2`; minor and
  major rejected because the planned fixes preserve public invocation shape.
- External boundary family: push+release vs issue close; chosen final bundle
  push+release only; issue close rejected by explicit user scope.
- Proof axis: backend readback vs distinct channel; chosen both, because release
  backend green is provisional under the north star.
- Host/provider axis: single-point GitHub because this repo's release adapter
  owns GitHub publication; no global provider default is introduced.

## Plan Critique Findings

- Packet consumed: `charness-artifacts/critique/2026-07-11-110741-packet.md`.
- Fresh-Eye Satisfaction: parent-delegated; Jackson, Weinberg, and Gawande
  angles plus a separate counterweight completed with zero rail-1 drift.
- Act before ship, folded: release scope is the full unpushed carrier; behavioral
  acceptance now names both defects; coverage is probe-first; release is
  conditional; T+100/T+110/T+120 cutoffs protect closeout; a fresh observer and
  content-bearing HTTPS verdict own public confirmation; partial publication is
  resumed or reported unresolved; #433 gets pre/post OPEN proof.
- Bundle anyway, folded: no history rewrite, no manufactured Slice C work,
  update and fresh-install claims stay separate, and release notes classify the
  whole carrier rather than narrating every commit.
- Over-worry, rejected: no per-commit release checklist, generic recovery
  framework, generic coverage-anchor abstraction, or validator weakening.
- Valid but defer: if the coverage mismatch does not reproduce as a supported
  explicit-anchor defect, make no anchor change and wait for new evidence.

## Off-Goal Findings

- none yet — off-goal findings route through `issue` but issue creation is not
  implied by this goal.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

- Pending final release URL, SHA, tag, update command, and #433 open-state readback.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
