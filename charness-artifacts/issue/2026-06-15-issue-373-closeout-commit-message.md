fix(achieve): enforce scaffold before goal validation

Close #373.

Classification: bug.
Issue closeout carrier: direct-commit.
Issue: #373 Audit template-producing skills for validator-before-scaffold
regressions.

JTBD: agents following public skill bootstrap instructions must scaffold or
produce templated artifacts before running validators/readiness checks that
expect those artifacts to exist or be shaped.

Root Cause: `achieve` documented `check_goal_artifact.py` before
`upsert_goal.py` in its Bootstrap block, and the repo had no deterministic gate
over public skill bootstrap producer/check ordering. Shape tests proved produced
goal artifacts, but did not inspect the operator-facing command sequence.

Debug Artifact:
`charness-artifacts/debug/2026-06-15-issue-373-producer-before-validator.md`.

Siblings: audited public artifact-producing bootstrap surfaces for achieve,
debug, quality, ideation, critique, handoff, retro, and hitl. Decision: fix the
observed achieve inversion and add an executable ordering gate for all known
producer/validator pairs. Proof: focused test coverage includes achieve and the
fresh-eye-found `hitl` same-script mode pair (`sync_review_artifact.py` versus
`sync_review_artifact.py --check`). Deferred: auto-deriving the pair table from
an owning registry such as `scripts/check_artifact_surface_preflight.py`.

Implementation: changed `skills/public/achieve/SKILL.md` so `upsert_goal.py`
runs before `check_goal_artifact.py`, described the checker as a post-scaffold
gate, synced `plugins/charness/skills/achieve/SKILL.md`, added
`tests/quality_gates/test_artifact_producer_order.py`, and recorded the debug
and resolution-critique artifacts.

Prevention: the new quality-gate test scans known public artifact
producer/validator bootstrap examples and fails when a validator/check token
appears before its producer/scaffold token, including same-script mode pairs.

Tests: focused producer-order and goal-producer tests passed; skill,
packaging, markdown/docs/secrets, deterministic prompt-proof, public-skill
policy/dogfood, debug artifact/index, critique artifact, integration, ruff,
Python length, attention visibility, test-repo-copy, and boundary-bypass gates
passed locally. Broad non-release pytest is deferred to the final bundle proof
per the active goal's slice policy.

Critique: charness-artifacts/critique/2026-06-15-issue-373-producer-before-validator-resolution.md
