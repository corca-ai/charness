docs: make hook failures self-describing when output is truncated

Closes #513

JTBD: Make a commit or push hook's final visible failure signal name the
blocking gate and a usable next evidence path when output is filtered or
truncated.

Boundary: This deferred-work resolution owns portable setup guidance for
consumer Lefthook configurations, the generated plugin mirror, worktree-doc
clarification, and deterministic contract/parity proof. It does not change a
consumer's actual hook file, Charness runtime hooks, gate thresholds, or
Husky/simple-git-hooks syntax.

Resolution brief: inline (no pause) — route only detected Lefthook
configurations to a contract requiring actionable `fail_text`; retain
diagnostic stdout/stderr in a pre-provisioned stable log; use a self-contained
fallback when a short command has no log; and make final output ordering a
consumer acceptance check.

Implementation: Added `skills/public/setup/references/hook-failure-visibility.md`,
routed the public setup skill and bootstrap seams to it, mirrored the setup
surfaces under `plugins/charness`, clarified `docs/worktree-prepare.md`, and
added `tests/quality_gates/test_setup_hook_failure_guidance.py`.

Prevention: Every covered Lefthook `pre-commit`/`pre-push` command now has a
documented `fail_text` requirement; diagnostic gates capture both streams to a
pre-provisioned stage-specific log; filter pipelines are explicitly rejected;
source/plugin routing and ownership parity are regression-tested.

Critique #513: charness-artifacts/critique/2026-08-06-issue-513-hook-failure-visibility-resolution-critique.md
Behavior #513: local-only-by-contract — focused setup/worktree tests (27 passed)
verified the Lefthook guidance, fallback wording, source/plugin mirrors, and
prepare.commands ownership boundary; Charness has no consumer Lefthook runner,
so an intentional failing-hook final-order roundtrip remains unproven and is
explicitly deferred to the adopting consumer.

Fresh-Eye Satisfaction: parent-delegated; three initial named angle reviews
returned findings, their later drifted fingerprints were quarantined, and a
repaired-surface reviewer plus separate final counterweight returned
findings-received with clean boundary fingerprints.
AI-provenance: Agent-authored direct-commit carrier; the resolution brief,
implementation, focused tests, source/plugin sync, final critique, and
non-claims are recorded in the listed artifacts.
