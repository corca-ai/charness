# Achieve Goal: YouTube gather support and adapter renderer hygiene

Status: complete
Created: 2026-06-11
Activation: `/goal @charness-artifacts/goals/2026-06-11-youtube-gather-and-adapter-renderer-hygiene.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: complete — bundle closeout, critique, issue closeout draft,
  retro, disposition review, and final quality proof are recorded.
- Next action: commit the local direct-commit carrier; push/remote issue CLOSED
  verification remains out of this activation scope.
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
| 1 | Shape #352 YouTube gather contract from current gather/provider code and issue source context. | Avoid implementing a URL handler that cannot state transcript vs metadata-only proof honestly. | Source/context read; chosen artifact schema/status semantics; focused tests or spec notes named. | completed |
| 2 | Implement #352 YouTube URL handling and downstream confidence visibility. | Converts the recurring YouTube summary request into a durable gather path. | Focused gather tests for caption-available and blocked/unavailable cases, plus artifact fields proving source identity and partial status. | completed |
| 3 | Debug #353 adapter renderer failure modes before fixing. | #353 is bug-class work; root cause must precede patching. | Minimal reproductions for newline scalar, unsupported construct rewrite, and falsy-explicit handling. | completed |
| 4 | Fix #353 renderer hygiene and consumer status reporting. | Removes the latent config-corruption trap after the failure modes are pinned. | Focused adapter/quality-bootstrap tests; no silent lossy rewrite; falsy-explicit behavior matches status. | completed |
| 5 | Bundle closeout, critique, issue closeout draft, and final quality proof. | The slices are independent but share one operator-selected goal closeout. | Slice closeout proof, final goal artifact gate, retro/disposition, issue-closeout validation for #352/#353 when applicable. | completed |

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

Routing: find-skills routed gather for #352 source-ingestion, debug for #353 RCA, quality for validation, issue for #352/#353 closeout, and impl for code/test slices; achieve remained the lifecycle wrapper.
- Gather: `charness-artifacts/gather/2026-06-11-youtube-hak1koqwm18-unavailable-details.md`
  captures the issue #352 source URL through the new YouTube gather path in this
  unauthenticated runtime: direct fetch hit captcha/bot signals, `yt-dlp` was
  missing, and the artifact records `Source Identity: youtube-unavailable`.
- Release: n/a — no version bump or release surface is in the activation scope.
- Issue closeout: #352/#353 close-intended via direct-commit carrier
  `charness-artifacts/issue/2026-06-11-issues-352-353-closeout-commit-message.md`;
  `issue_tool.py validate-closeout-draft` returned `ok: true` for #352 as
  `feature` and #353 as `bug`. `verify-closeout --expect-state CLOSED` is
  deferred until the direct-commit carrier is pushed, per Non-Goals.

Discuss before activation: resolved for draft shaping — operator explicitly
selected chunks 2 + 3 as one goal, despite the chunker finding no shared merge
boundary. Activation assumes local-only implementation, no authenticated
YouTube/browser proof, no push/release, and issue closure only after the
standard issue-closeout path is prepared.

## Slice Log

- 2026-06-11 11:29 KST — Slices 1-2 (#352) implemented explicit YouTube
  handling under support/web-fetch's `yt-dlp-metadata` domain route and
  gather's durable public-URL record. New tests cover transcript-backed
  acquisition from seeded subtitle data, metadata-only acquisition, blocked
  bot-verification acquisition, and missing-`yt-dlp` unavailable acquisition.
  Live/local proof on `https://youtu.be/haK1KoQWm18` produced
  `charness-artifacts/gather/2026-06-11-youtube-hak1koqwm18-unavailable-details.md`
  with no transcript claim. Focused proof: `python3 -m pytest -q
  tests/test_youtube_source.py tests/test_twitter_exact_source.py
  tests/test_web_fetch_support.py tests/test_web_fetch_content_persistence.py`
  passed (65 tests) before bundle validation.
- 2026-06-11 11:29 KST — Slices 3-4 (#353) reproduced and fixed the
  adapter-lib renderer bugs. RCA captured in
  `charness-artifacts/debug/latest.md`; seam-risk index regenerated. Fixes:
  newline/carriage-return scalar escaping and decoding; limited block-scalar
  parsing so workflow `run: |` bodies are preserved rather than dropped;
  anchors/tags refused loudly; quality-bootstrap renders explicit falsy fields
  when status says `preserved`. Focused proof: `python3 -m pytest -q
  tests/quality_gates/test_adapter_lib_yaml.py
  tests/quality_gates/test_quality_bootstrap.py::test_quality_bootstrap_rewrite_preserves_explicit_falsy_fields
  tests/quality_gates/test_quality_bootstrap.py::test_quality_bootstrap_adapter_preserves_existing_explicit_commands`
  passed after the fix; broad proof later passed with 2769 passed, 4 skipped,
  26 deselected.
- 2026-06-11 11:48 KST — Slice 5 closeout completed: final critique
  `charness-artifacts/critique/2026-06-11-youtube-gather-and-adapter-renderer-closeout-critique.md`
  folded all Act Before Ship findings; direct-commit closeout draft validated
  for #352 and #353; retro and host-log probe artifacts were written; final
  broad proof passed with 2771 passed, 4 skipped, 26 deselected.

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

Retro: charness-artifacts/retro/2026-06-11-youtube-gather-adapter-closeout.md
Host log probe: charness-artifacts/retro/2026-06-11-youtube-gather-adapter-host-log.md
Disposition review: charness-artifacts/critique/2026-06-11-youtube-gather-adapter-disposition-review.md

### Focused And Live Proof

- `python3 -m pytest -q tests/test_youtube_source.py tests/test_twitter_exact_source.py tests/test_web_fetch_support.py tests/test_web_fetch_content_persistence.py`
  — passed, 65 tests.
- `python3 -m pytest -q tests/test_youtube_source.py tests/quality_gates/test_adapter_lib_yaml.py tests/quality_gates/test_quality_bootstrap.py::test_quality_bootstrap_adapter_preserves_existing_explicit_commands tests/quality_gates/test_inventory_ci_local_gate_parity.py`
  — passed, 40 tests.
- `python3 skills/public/gather/scripts/gather_public_url.py --repo-root . --url https://youtu.be/haK1KoQWm18 --browser-mode off --slug youtube-hak1koqwm18-unavailable-details --date 2026-06-11 --execute`
  — wrote
  `charness-artifacts/gather/2026-06-11-youtube-hak1koqwm18-unavailable-details.md`
  with `Source Identity: youtube-unavailable`, `Video Id: haK1KoQWm18`, and
  `Reason: missing-tool`; no transcript-backed claim.

### Changed-Surface Proof

- `python3 scripts/check_changed_surfaces.py --repo-root .` — passed and mapped
  checked-in plugin export, repo markdown, skill packages, public skill policy
  and dogfood, adapters, critique artifacts, debug seam-risk index,
  integrations/control plane, repo Python, and Python scan hygiene.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and
  `python3 scripts/build_debug_seam_risk_index.py --repo-root . --write` —
  completed before verification.
- `python3 scripts/validate_packaging.py --repo-root .` —
  passed.
- `python3 scripts/validate_packaging_committed.py --repo-root .` —
  passed.
- `python3 scripts/check_doc_links.py --repo-root .` — passed.
- `python3 scripts/check_command_docs.py --repo-root .` — passed.
- `./scripts/check-markdown.sh` — passed.
- `./scripts/check-secrets.sh` — passed.
- `python3 scripts/validate_skills.py --repo-root .` — passed.
- `python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py`
  — passed.
- `python3 scripts/check_skill_ownership_overlap.py --repo-root .` — passed.
- `python3 scripts/validate_skill_ergonomics.py --repo-root .` — passed.
- `python3 scripts/validate_public_skill_validation.py --repo-root .` —
  passed.
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .` — passed.
- `python3 scripts/validate_adapters.py --repo-root .` — passed.
- `python3 scripts/validate_critique_artifacts.py --repo-root . --all` —
  passed.
- `python3 scripts/validate_critique_packet.py charness-artifacts/critique/2026-06-11-023045-packet.json`
  — passed.
- `python3 scripts/validate_debug_artifact.py --repo-root .` — passed.
- `python3 scripts/build_debug_seam_risk_index.py --repo-root . --check` —
  passed.
- `python3 scripts/validate_integrations.py --repo-root .` — passed.
- `python3 scripts/sync_support.py --repo-root . --json` — passed as dry-run.
- `python3 scripts/update_tools.py --repo-root . --json` — passed as dry-run;
  reported current manual/missing tool readiness without mutating.
- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`
  — passed.
- `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing`
  — passed with advisory warn-band notes only, including touched
  `scripts/quality_bootstrap_lib.py` and
  `skills/support/web-fetch/scripts/acquire_public_url.py`.
- `python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support`
  — passed.
- `python3 scripts/check_test_repo_copy_invariants.py --repo-root .` — passed.
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .` — passed.
- `python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing`
  — passed.
- `pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py`
  — passed, 2771 passed, 4 skipped, 26 deselected.

### Issue Closeout Proof

- `python3 skills/public/issue/scripts/issue_tool.py validate-closeout-draft --repo corca-ai/charness --number 352 --classification feature --carrier direct-commit --commit-message-file charness-artifacts/issue/2026-06-11-issues-352-353-closeout-commit-message.md --repo-root .`
  — `ok: true`, `status: draft_verified`.
- `python3 skills/public/issue/scripts/issue_tool.py validate-closeout-draft --repo corca-ai/charness --number 353 --classification bug --carrier direct-commit --commit-message-file charness-artifacts/issue/2026-06-11-issues-352-353-closeout-commit-message.md --repo-root .`
  — `ok: true`, `status: draft_verified`.
- Final GitHub state verification is intentionally not claimed: this activation
  is local-only and no push is in scope.

## User Verification Instructions

- Activate only if the local-only proof and two-independent-slice bundle are
  acceptable: `/goal @charness-artifacts/goals/2026-06-11-youtube-gather-and-adapter-renderer-hygiene.md`.
- After completion, inspect the gathered YouTube artifact and the adapter
  renderer tests named in `## Final Verification`.

## Auto-Retro

Retro dispositions: applied: all surfaced retro improvements are dispositioned
below.

- applied: issue-closeout draft shape now comes from the live
  `describe_closeout_draft_shape.py` helper and the exact direct-commit carrier
  was validated separately for #352 as `feature` and #353 as `bug` before
  commit.
- applied: support/export surface closeout followed sync-before-verify
  ordering: `sync_root_plugin_manifests.py` and seam-risk index write first;
  changed-surface validators and broad pytest next; artifact-only closeout
  edits last, followed by narrow artifact validators before commit.
- applied: `charness-artifacts/retro/recent-lessons.md` now records the
  `proof:`-style continuation trap and the mixed-class closeout validation
  habit.

Structural follow-up: applied: the transferable field-shaped-continuation
pattern was corrected in
`charness-artifacts/issue/2026-06-11-issues-352-353-closeout-commit-message.md`
and guarded by both successful `validate-closeout-draft` runs; durable memory is
the refreshed `charness-artifacts/retro/recent-lessons.md`; no new issue is
needed.
