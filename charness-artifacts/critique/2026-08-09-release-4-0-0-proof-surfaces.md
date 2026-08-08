# Critique Review

Date: 2026-08-09

## Decision Under Review

Publish a MAJOR release (`3.5.0` -> `4.0.0`) covering the unpushed range, then
push it, as slice 8 of
[the proof-surfaces goal](../goals/2026-08-09-make-proof-surfaces-report-what-they-observed.md).
The bump is MAJOR because three of the seven slices change what a surface
REFUSES, and all of it reaches consuming repos through `plugins/charness/`.

## Failure Angles

- **The push gate refuses, and the workaround forfeits the grant.**
  `.githooks/pre-push` forces the full battery for any `plugins/` change, and
  `check-changed-line-mutation-coverage` computes its changed set from
  `merge-base(origin/main, HEAD)` — the whole unpushed range — so files
  inherited from that range block it. At push time the lane also gets
  `--refuse-unestablished`, closing the UNPROVEN path. `--no-verify` was the only
  bypass, and both `AGENTS.md` and this goal's Boundaries say it revokes the push
  grant.
- **A consumer's attention-state declaration goes red in both directions.** The
  detector now reads a status as a token rather than a substring, so prose-only
  entries stop being detected (`declared ... but no attention state terms are
  detected`) while separator-variant states start being detected (`are not
  declared`). A consuming repo owns its own copy of that file, so this lands
  without any action on their part.
- **The `Phases:` requirement is keyed to goal CREATION date, not upgrade date.**
  A consumer upgrading later inherits the obligation for every goal created since
  the rule date, including finished-but-not-yet-flipped ones — weeks of in-flight
  artifacts rather than one.
- **Commit-generated release notes would not name a single breaking change.** A
  MAJOR justified entirely by three changed refusals, published with notes
  derived from an 89-commit range, reports what was committed rather than what
  changed for a consumer — the same disease this release repairs.
- **Proof surfaces that ship while contradicting themselves.** The awiki manifest
  carried a `host_notes` sentence stating it "does not make awiki a repo gate"
  beside the note that supersedes it, and that file is mirrored to consumers;
  `quality/latest.md`, named by the Contract Map as the current quality posture,
  still denied that the release's headline gate exists.
- **Acceptance numbers measured against a stale document count.** The docs-graph
  acceptance was recorded at 41 documents before slice 3 added a page.

## Counterweight Pass

Real blockers, all now resolved:

- The push refusal was real and mechanical. It was fixed by SATISFYING the gate,
  not by bypassing it: the blocking set was 11 lines across 6 files plus one
  module with no standing test at all. The pre-push battery now runs green
  (`87 passed, 0 failed`) with `CHARNESS_PRE_PUSH=1`.
- The two self-contradicting proof surfaces were corrected before publish.
- The stale acceptance count was re-measured: 42 documents, `orphans=0
  islands=0 largest_component_ratio=1.0000`.

Raised and NOT folded, deliberately:

- **Rewriting the inherited files' behaviour.** The six blocking files were
  covered with tests for their refusal branches; none of their logic changed. A
  release is not the place to alter code the release is not about.
- **Making `docs-graph` a consumer gate.** The reviewer confirmed by search that
  the lane appears nowhere in the shipped consumer quality contract, which is the
  operator's internal-only decision holding. Left alone.
- **Retro-fitting the `Phases:` rule date to the upgrade date.** That would make
  the floor depend on when a consumer happened to install, which is less
  predictable than a fixed date, not more. Documented in the release notes
  instead.

Over-worry, checked and dismissed with evidence:

- "The new lane breaks consumers without awiki." It does not: the missing binary
  path returns UNESTABLISHED, the label is in `UNESTABLISHED_CAPABLE_LABELS`, and
  the run exits 0 with a named UNPROVEN line.
- "The deleted `--invocation-text` breaks a caller." No hook, preset, profile,
  adapter, or eval passes it; the only caller is an agent reading `SKILL.md`,
  which was updated in the same slice.
- "Slice 6's constant changed behaviour." `MIN_EMPTY_QUEUE_REASON = 21` builds
  `\S.{20,}`, byte-identical to the hand-typed pattern it replaced.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: .githooks/pre-push | action: fix | note: the pre-push battery refused the push on inherited changed-line coverage; satisfied by covering 11 refusal branches plus one unanalyzed module, now green
- F2 | bin: act-before-ship | evidence: strong | ref: integrations/tools/awiki.json | action: fix | note: a host_notes sentence denying awiki is a repo gate shipped beside the note superseding it
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/quality/latest.md | action: fix | note: the current-posture artifact denied the existence of this release's headline gate
- F4 | bin: act-before-ship | evidence: moderate | ref: docs/handoff.md | action: fix | note: documented `publish_release_cli.py --part`, a module with no __main__ guard; the real entrypoint is publish_release.py
- F5 | bin: bundle-anyway | evidence: strong | ref: scripts/validate_attention_state_visibility.py | action: document | note: a consumer's own declaration file goes red in both directions on upgrade; release notes carry the one-command migration
- F6 | bin: bundle-anyway | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_phase_routing.py | action: document | note: the Phases rule is keyed to goal creation date, so a later upgrade inherits it retroactively for in-flight goals
- F7 | bin: over-worry | evidence: strong | ref: scripts/check_docs_graph.py | action: defer | note: consumers run their own run-quality.sh and the lane is absent from the shipped contract; the exported copy degrades to UNPROVEN

## Boundary Ownership

- Producer: the four repaired proof surfaces and the new docs-graph lane — each
  emits a verdict (or a routing decision) that something downstream acts on.
- Consumer: `check_goal_artifact` at the complete flip, `run-quality.sh`'s
  summary, the pre-commit battery, and the agent reading a run plan; plus every
  consuming repo, which inherits all of it through `plugins/charness/`.
- Owning surface: each rule now lives in the module that ENFORCES it, and the
  restatements were moved there rather than re-typed. The two backticked-ref
  remedies and the bare-internal-ref / missing-command remedies became constants
  in `check_doc_links.py`, which raises them; the empty-queue reason floor became
  `MIN_EMPTY_QUEUE_REASON` in `goal_artifact_operator_queue.py`, which matches on
  it, with its own regex built from the constant; and `describe_goal_closeout_shape`
  now renders every number from those owners instead of holding a second copy.
- Verdict: moved-to-owner

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer, the repo's typed read-only reviewer agent.
- Requested spawn fields: subagent_type bounded-reviewer, unnamed one-shot spawn, run synchronously.
- Host exposure state: applied
- Application state: host-confirmed: the spawn returned findings inline and reported `envelope-unbound` does not apply, naming Bash/Edit/Write/Agent as absent from its toolset.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated
