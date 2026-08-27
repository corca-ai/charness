<!-- charness-goal-run:v1
{
  "binding_path": "charness-artifacts/goals/2026-08-28-friction-generative-sequence-p0-p1.binding.json",
  "binding_schema": "charness.goal-binding/v1",
  "binding_sha256": "e564d1f1c57cdce7f9efecc9a2416e71add70caf578774aa24f63835f476cedd",
  "bootstrap_verification": "verified-target-roundtrip",
  "current_membership_sha256": "31db53a1068dbbd0e6ea9e4509c28eca1c998fac4725c23b9576ef0f5b64e789",
  "draft_path": "charness-artifacts/goals/2026-08-28-friction-generative-sequence-p0-p1.md",
  "draft_sha256": "1a9a38f26cb8dd0d5735a543126603bd7cf86e179874757d899ae52093c61ac5",
  "initial_graph_sha256": "2c9758d0b3f85777c190ea08a6fea9ff7c2980db9c28fa68d959c806c093e01e",
  "parent_identity": {
    "number": 736,
    "repo": "corca-ai/charness",
    "url": "https://github.com/corca-ai/charness/issues/736"
  },
  "progress": {
    "completed": 0,
    "membership_sha256": "31db53a1068dbbd0e6ea9e4509c28eca1c998fac4725c23b9576ef0f5b64e789",
    "next": {
      "key": "remote-truth-reconciliation",
      "number": 737,
      "repo": "corca-ai/charness",
      "state": "OPEN",
      "url": "https://github.com/corca-ai/charness/issues/737"
    },
    "open": 10,
    "revision": 1,
    "schema": "charness.goal-progress/v1",
    "total": 10
  }
}
-->

# Situation

Charness must make correct development in consuming repositories faster and
reduce rework. Duplicate execution, progress, validation, review, artifact,
and documentation ownership currently turns safety mechanisms into recurring
friction.

# Goal

Remove the structures that regenerate that friction, resolve the complete
P0/P1 set in dependency order, and dogfood the simplified Achieve, Issue,
Task, Setup, Impl, Prove, and Quality contracts while doing it.

# Approved boundary

- Frozen Goal Draft: `charness-artifacts/goals/2026-08-28-friction-generative-sequence-p0-p1.md`
- Immutable Goal Binding: `charness-artifacts/goals/2026-08-28-friction-generative-sequence-p0-p1.binding.json`
- Initial graph: ten approved Work Items, all provider-linked and exactly read back
- Current child: #737 `remote-truth-reconciliation`
- Independent P2 backlog: #731 and #709, outside this parent

The bounded interview had zero unresolved consequential ambiguities. Fifteen is
the configured question ceiling, not a quota. The operator explicitly approved
the frozen Draft and listed GitHub mutations.

# Execution order

1. Reconcile remote truth and close absorbed/obsolete issue state.
2. Make the task lane reliable enough for isolated parallel writers.
3. Run Goal Draft, retired-workflow, verification-cost, reviewer-status, and
   adapter-first-use slices as one disjoint parallel generation.
4. Stabilize export ownership, then correct release claim precision.
5. Run one integrated dogfood proof and the dedicated guarded parent close.

# Completion

- Every linked P0/P1 Work Item is closed with behavioral evidence.
- Remote state no longer counts absorbed or obsolete issues as implementation.
- Fresh `/goal #736` pickup reads this parent and one current child only.
- Final provider readback agrees with the frozen Draft, Binding, membership,
  cursor, and child states.
- Push, tag, release, remote CI, and installed-host mutation remain separately
  authorized boundaries.

AI provenance: drafted and filed by an AI agent from the operator-approved Goal
Draft and direct activation approval.
