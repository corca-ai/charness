# Quality Review
Date: 2026-06-25

## Scope

Target boundary: `critique` public skill quality, especially prepare-packet
ownership, progressive disclosure, fresh-eye review contract, and consumer
dogfood.

Ambient repo findings: the broad doc-duplicate advisory between `hitl` and
`narrative` is not a `critique` target finding. Python length-band warnings from
the broad gate are also ambient.

## Current Gates

- `./scripts/run-quality.sh --read-only` passed 79/79 before the target fix.
- Focused package gates passed after the fix: skill validation, skill ergonomics,
  critique quality-gate tests, critique packet tests, doc links, and markdown.
- Target-only ergonomics inventory scanned `critique` with
  `core_nonempty_lines=144`, `reference_file_count=12`, `unlisted_reference_files=[]`,
  no issue anchors, no dated incidents, and 12 host-surface reference hits.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile
  `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median, budget
  90.0s; `pytest` 24.9s latest / 25.8s median, budget 140.0s; `check-coverage`
  19.1s latest / 19.5s median, budget 55.0s; `check-duplicates` 10.0s latest /
  11.9s median, unbudgeted.
- coverage gate: broad read-only quality passed.
- evaluator depth: deterministic gates plus bounded fresh-eye review only;
  Cautilus was not triggered because no log-backed behavior source was in scope.

## Healthy

- `critique` has a coherent trigger boundary: before-the-fact review for
  non-trivial design, code, release, rename, deletion, spec, and workflow
  lock-in.
- `SKILL.md` owns target selection and sequencing; target references own deeper
  angle distribution, counterweight details, and target-specific output shape.
- The helper-owned prepare-packet seam is real and adapter-backed:
  `.agents/critique-adapter.yaml` declares two sections, `prepare_packet.py`
  builds the packet, and `critique_packet_lib.py` owns the envelope.
- Consumer dogfood pressures real behavior: a pending-decision prompt routes to
  `critique`, expects `charness-artifacts/critique`, and requires an adapter.

## Weak

- The target had a packet-production ownership fork: `SKILL.md` told agents to
  run `prepare_packet.py`, while `prepare-packet.md` said critique did not run
  it automatically and expected upstream production.
- The bootstrap fence hid packet-helper failures with `2>/dev/null || true`,
  which could let a failing adapter section disappear before fresh-eye review.
- Host-surface reference hits are intentional reviewer-tier and compatibility
  examples, but they remain a portability advisory rather than proof of health.

## Missing

- No missing helper remains after this slice. The packet helper, adapter
  contract, artifact validator, and focused tests already exist.

## Deferred

- Do not add another blocking floor for packet ownership now; the focused test
  added here is enough for this specific drift.
- Do not run Cautilus for this review without a concrete behavior log or
  evaluator fixture source.

## Advisory

- structural review result: target finding fixed. Command:
  `plan_quality_run.py --target-skill critique`. Packet ownership is now
  single-sourced enough for standalone `critique`: the bootstrap runs the helper
  when needed, the reference allows a parent-produced packet for changed-ref
  specificity, and helper failures are visible.
- prose review result: `critique` is structurally healthy after the packet
  correction; the core owns selection/sequencing and references deepen the path.
  Command: `inventory_skill_ergonomics.py --skill-path skills/public/critique/SKILL.md`.
- command: `inventory_skill_ergonomics.py --skill-path skills/public/critique/SKILL.md`;
  skill ergonomics interpretation: `prose_review_status=required` was satisfied
  by the prose review above, and the 12 host-surface hits are intentional
  adapter/reviewer-tier examples, not immediate portability debt, but they should
  stay visible in future quality reviews.
- command: `./scripts/run-quality.sh --read-only`; broad-gate interpretation:
  the HITL/narrative doc duplicate advisory is
  ambient and should not be charged to the `critique` target.

## Delegated Review

- Delegated Review: executed — bounded fresh-eye reviewer
  `019efd09-9834-73d0-9049-048c602c7e16` independently found the packet
  ownership fork and classified the broad duplicate advisory as ambient.
- Slow-gate lenses: fixture-economics, parallel-critical-path, duplicated-proof
  not re-delegated because this slice did not redesign slow gates; runtime data
  is reported as existing evidence only.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --target-skill critique --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --skill-path skills/public/critique/SKILL.md --json`
- `python3 skills/public/quality/scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id critique`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `./scripts/run-quality.sh --read-only`
- `python3 scripts/check_skill_surface_preflight.py --repo-root . --path skills/public/critique/SKILL.md --preview-delta 0`
- `python3 scripts/check_skill_surface_preflight.py --repo-root . --path skills/public/critique/references/prepare-packet.md --preview-delta 0`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_skill_ergonomics.py --repo-root .`
- focused critique pytest: 42/42 for `tests/quality_gates/test_critique_skill.py`
  and `tests/test_critique_prepare_packet.py`
- `python3 scripts/check_doc_links.py --repo-root .`
- `./scripts/check-markdown.sh`

## Recommended Next Gates

- active for #401 next targets: run the same target-vs-ambient structural review
  on `spec` and `impl`, and treat any missed target contract fork as quality
  evidence about the review process.
- passive because the current target fix is covered: consider a future
  structure-aware validator only if packet ownership drifts again across another
  skill.

## History

- [retro skill quality review](history/2026-06-25-retro-skill-quality-review.md)
