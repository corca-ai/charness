fix: align focused coverage marker policy

Closes #615
Classification: bug
Carrier: direct-commit; this message is the proposed issue-resolution carrier.

Jtbd: Before a push, maintainers need the focused changed-line coverage lane to
conservatively catch a changed-line blocker without granting `clean` from tests
the broad producer excludes.

Observed problem: Over the same historical base/head, the local focused wrapper
returned `clean` while the broad CI-shaped producer and an independent coverage
read found lines 116, 117, 132, 133, and 134 missing.

Root Cause: `_focused_pytest_command` passed `--include-release-only` to the
standing runner while `cosmic-ray.toml` defines the broad producer with
`-m 'not release_only'`. The focused population was therefore not a subset of
the broad population, and local-only executions could mark broad-missing lines
as covered. Its command-shape test asserted the widening flag instead of the
comparability contract.

Debug Artifact: charness-artifacts/debug/2026-08-13-issue-615-focused-changed-line-false-clean.md

Implementation: Removed the focused release-only override, bound the focused
command to the broad marker expectation, executed a release-only sentinel
through the real standing-runner child command, synchronized the checked-in
plugin export, and retained the exact repaired historical wrapper evidence.

Siblings: decision: same bug, fix now for the checked-in plugin export; proof:
source and plugin wrapper are byte-identical after generated sync. Decision:
intentional plain-text or non-rendering boundary for the broad closeout producer
and full release-quality lane; proof: both own broad populations and make no
focused-subset claim. Decision: same bug, fix now for the command-shape test;
proof: it now reads the broad policy and rejects focused widening, while a real
child-command sentinel proves release-only deselection.

Prevention: Keep target narrowing and marker-policy narrowing as separate
dimensions; compare the broad marker policy explicitly, execute a real marker
control through the focused command, retain transport/final-consumer tests, and
preserve exact historical incident evidence for end-to-end composition.

Boundary: owned-correctly — the focused producer owns its admissible test
population, the shared consumer owns line dispositions, the wrapper owns the
operator-visible verdict, and generated sync owns the installed plugin copy.

Critique #615: charness-artifacts/critique/2026-08-13-issue-615-focused-marker-parity.md

Behavior #615: Confirmed through a distinct isolated historical runtime channel:
with fresh focused coverage at `d315d989` over base `d0c33e6b...`, the repaired
wrapper returned 1/`blocked` and named the exact five reported lines. The 97-test
focused producer, transport, runner, and final-consumer set also passed. This is
local-only evidence; hosted CI, GitHub CLOSED state, and installed-consumer
behavior remain unverified before an authorized push.

Fresh-Eye Satisfaction: parent-delegated; causal readback accepted the diagnosis,
round 1 used two contrasting reviewers plus a counterweight, and round 2 read the
repaired surface and forced plugin export synchronization. Every reviewer window
verified `clean` before parent writes.

AI-provenance: Agent-authored direct-commit carrier; live issue read, causal
debug, historical reproduction, spec, implementation, generated sync, two-round
fresh-eye critique, and deterministic verification are recorded in the linked
artifacts. The issue remains OPEN until this carrier is pushed and GitHub state
is independently read back.
