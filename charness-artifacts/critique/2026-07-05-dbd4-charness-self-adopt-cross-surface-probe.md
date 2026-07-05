# DBD-4 — charness self-adopts its own cross-surface probe
Date: 2026-07-05

## Decision Under Review

Boundary-ownership checkpoint DBD-4 (spec 2026-07-05-boundary-ownership-checkpoint.md):
make the #408 "5b tooth" (critique validator rejecting a bare `single-surface`
boundary verdict when the changed set touches a shared surface) fire in charness's
OWN CI, not just unit fixtures. Shipped: `boundary_cross_surface_globs:
[scripts/*_lib.py, skills/shared/**]` in `.agents/critique-adapter.yaml` (8% of the
last 60 commits), `--changed-ref "${base}..HEAD"` wired into `run-quality.sh`'s
validate-critique-artifacts gate, three regression guards, and the DBD-4 resolution
recorded in the spec. Unblocks closing #408 on charness's live dogfood + fixtures.

## Failure Angles

- **False measurement (caught, corrected).** The first pass claimed broad globs were
  ~100% false-positive and recommended probe-off. That was a methodology bug —
  `git log -n 60 -- <path>` returns the 60 most-recent commits *touching* the path,
  capped, not a rate. The resolution-critique subagent caught it. Corrected with the
  probe's own matcher over the actual last 60 commits: `scripts/*_lib.py`=5%,
  `skills/shared/**`=5% (union 8%), `skills/public/**`=33%. A narrow set is viable.
- **Mis-targeted wiring (caught, fixed).** The first wiring passed a BARE merge-base
  sha; `surfaces_lib.collect_changed_paths_for_ref` routes a ref without `..` to
  `git diff-tree <ref>` = that one fork-point commit's own diff, not the range — so
  the tooth silently evaluated the wrong file set (false negatives on real work). The
  impl-critique subagent caught it; fixed to `${base}..HEAD` and verified end-to-end
  (range rejects, bare sha mis-targets).
- **Under-strong guard (caught, fixed).** The first wiring test only asserted
  `--changed-ref` present — it greenlit the broken bare-sha form. Strengthened to
  require the `..HEAD` range form plus an end-to-end git-range test.
- **Sync-before-verify miss (caught, fixed).** I edited `scripts/run-quality.sh`
  (source) without syncing `plugins/charness/scripts/run-quality.sh` (mirror), so the
  packaging + managed-install tests failed on export drift. Re-ran
  `scripts/sync_root_plugin_manifests.py`. The recurring "mutate → sync → verify" trap.
- **Self-inflicted CI failure.** With the probe live, would run-quality fail on this
  very change? No — the DBD-4 files (`.agents/critique-adapter.yaml`, `run-quality.sh`)
  match neither glob, so cross_surface_hit is False for the unpushed range.

## Counterweight Pass

- Real work folded now: charness now dogfoods the #408 tooth in its own CI (fixture →
  live), at 8% friction; two independent fresh-eye reviews caught a false measurement
  and a mis-targeted wiring that would each have shipped a hollow gate.
- Over-worry separated out: `skills/shared/**` covering prose `.md` was considered
  noise but kept — shared references are genuinely cross-consumed and a hit only
  rejects a *bare* `single-surface`, still allowing `owned-correctly` with a reason.
- Deliberately NOT done: broader globs (`skills/public/**`=33%) or a surface-id set —
  the narrow glob set is the smallest thing that closes charness's recurrence gap.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: .agents/critique-adapter.yaml | action: fix | note: adopt narrow boundary_cross_surface_globs (scripts/*_lib.py + skills/shared/**, 8% measured); replaces the false-measurement "keep probe-off" decision
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: --changed-ref must be a RANGE (${base}..HEAD); a bare sha resolves the fork-point diff and silently mis-targets the tooth (impl-critique BLOCKER, fixed + verified)
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_critique_boundary_ownership_presence.py | action: fix | note: three guards — globs configured, run-quality wires the range form, and an end-to-end base..HEAD git-range rejection; the wiring test now fails on the bare-sha regression
- F4 | bin: act-before-ship | evidence: strong | ref: plugins/charness/scripts/run-quality.sh | action: fix | note: synced the plugin mirror after the source edit (mutate->sync->verify); packaging/managed-install drift resolved
- F5 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/spec/2026-07-05-boundary-ownership-checkpoint.md | action: document | note: corrected the DBD-4 resolution note (real hit-rates, adoption not probe-off, scripts/*.py label fix); the content-guards-cover-taxonomy overclaim removed

Fresh-eye satisfaction: parent-delegated — two bounded fresh-eye subagents
(general-purpose) reviewed this slice: id aa4a04ab70af60e8e (resolution critique)
caught the false 100%-false-positive measurement, and id a32162bea0254817d (impl
critique) caught the bare-sha wiring BLOCKER and the under-strong guard. Both
findings were incorporated before this closeout; both ran to completion and returned
their findings.

## Reviewer Tier Evidence

- Requested tier: two bounded fresh-eye subagents in a different agent context, adversarial (refute-oriented), read-only in the shared parent worktree
- Requested spawn fields: the #408 asks + proof mapping (resolution critique); the working-tree DBD-4 diff + the wiring/measurement/guard failure modes to refute (impl critique)
- Host exposure state: applied
- Application state: host-confirmed: subagents aa4a04ab70af60e8e and a32162bea0254817d ran to completion and returned findings that changed this slice (measurement correction + wiring fix)

## Boundary Ownership

- Producer: charness owns its own critique adapter (`.agents/critique-adapter.yaml`) and quality gate (`scripts/run-quality.sh`)
- Consumer: charness CI (the validate-critique-artifacts gate) and future charness critiques
- Owning surface: charness's own repo-wide quality contract — a self-configuration, not a portable-skill change
- Verdict: owned-correctly
