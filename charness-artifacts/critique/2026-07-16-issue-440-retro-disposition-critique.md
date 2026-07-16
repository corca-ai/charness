# Critique Review
Date: 2026-07-16

## Decision Under Review

Issue #440 resolution: disposition the two remaining round-5 retro
improvements by (a) adding the root-CLI host-mutation seam (`charness`,
`scripts/install_machine_local.py`) to `real_host_required_path_globs` in
`.agents/release-adapter.yaml`, and (b) adding a durable independent-observer
probe-artifact convention to the release skill's
`references/publication-boundary.md` with a matching ownership-overlap
allowlist entry.

## Failure Angles

- The glob closing only the literal v1.0.4 file while a sibling host-mutation
  seam stays untriggered (same escape class, different file).
- Trigger-rate dishonesty: the adapter comment overclaiming safety, or the
  checklist containing destructive machine mutation that a ~50% firing rate
  makes costly.
- The publication-boundary paragraph drifting into a terminal-green
  declaration or a new blocking floor (P4/P5 violation).
- Portability/ownership: naming `charness-artifacts/probe/` inside a portable
  public-skill reference without a declared cross-namespace boundary.
- The resolution failing the issue's actual JTBD (retro items still silent
  debt).

## Counterweight Pass

- Real pre-ship items: the plugin mirror of `publication-boundary.md` was
  unsynced (fixed in this closeout by the mirror sync), and the brief's
  operator pause on the glob decision needed a durable consent record — the
  operator confirmed "add the glob" in-session and the brief now records it.
- Acted on: the sibling seam finding — root `charness` delegates managed
  install / Codex marketplace / legacy-root cleanup to
  `scripts/install_machine_local.py`, which was untriggered; bundled into the
  same glob addition as cheap in-scope prevention instead of leaving it as
  retro-only debt (the exact anti-pattern the issue names).
- Over-worry: checklist destructiveness (items are additive
  update/doctor/dry-run; the only rmtree fires on a differing legacy plugin
  root), the P4/P5 concern (the paragraph is a record obligation with no
  validator and no completion claim), and the portability concern
  (`achieve` already cites `charness-artifacts/probe/` under an allowlist
  entry; the new `release:artifact:probe` line follows that precedent).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: plugins/charness/skills/release/references/publication-boundary.md | action: fix | note: plugin mirror lacked the new probe paragraph; mirror sync run before validators/commit (done in this closeout)
- F2 | bin: act-before-ship | evidence: strong | ref: .agents/release-adapter.yaml:39 | action: fix | note: sibling seam scripts/install_machine_local.py (actual install/rmtree/Codex marketplace) was untriggered; added to the same glob list
- F3 | bin: act-before-ship | evidence: contested | ref: charness-artifacts/issue/2026-07-16-issue-440-brief.md | action: document | note: item-(a) operator ceremony-cost consent confirmed in-session and recorded in the brief's Operator decision section
- F4 | bin: over-worry | evidence: strong | ref: skills/public/release/references/publication-boundary.md:34 | action: document | note: probe-artifact paragraph is a durability record obligation, no new blocking floor, P4/P5-consistent

## Reviewer Tier Evidence

- Requested tier: high-leverage (issue-closeout review class).
- Requested spawn fields: repo standing request `gpt-5.6-terra` + `medium`
  effort is not exposed by this host's Agent tool (model enum is
  sonnet/opus/haiku/fable); spawned typed `bounded-reviewer` with no model
  override.
- Host exposure state: host-defaulted
- Application state: reviewer reported the read-only envelope bound
  (Read/Grep/Glob only; no Bash/Edit/Write/Agent), and the parent-side
  boundary fingerprint verify returned drift: [] after the review.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: `.agents/release-adapter.yaml` (repo-local trigger config) and the
  release skill's `publication-boundary.md` (portable boundary doctrine).
- Consumer: the release-time agent running `check_real_host_proof.py` and the
  later disposition reviewer auditing observer evidence.
- Owning surface: release skill adapter + publication-boundary reference;
  probe-artifact namespace ownership stays with `probe` via the allowlist.
- Verdict: owned-correctly
