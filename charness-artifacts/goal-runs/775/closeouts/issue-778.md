hooks: run the release lane on every code push, and document the clean-clone push (#778)

Closes #778

The pre-push hook ran ./scripts/run-quality.sh --full --read-only, and the
standing pytest lane deselects release_only and slow_corpus, so a release-only
regression that landed in code crossed the push boundary unseen: #768 carried
three for four days until #772 ran --release by hand. The hook's full branch
now runs --full --read-only --release. A docs-artifact-only push keeps its
subset: the release lane is indivisible and cannot narrow to a label list, and
a docs diff cannot change what a release_only test measures. docs/development.md
gains a Pushing section naming the hook lane, the cadence, the measured
runtime, and the clean-clone shape the Goal Run closeouts use.

Classification: feature
Jtbd: a maintainer cannot push a release-only regression from a clean tree without the hook refusing it first.
Boundary: .githooks/pre-push (the full branch only), tests/quality_gates/test_prepush_runtime_regime.py, docs/development.md. The standing lane's marker selection, the docs-only subset, the close-keyword guard, and the release receipt path are unchanged. No hosted observer.
Resolution Brief: charness-artifacts/goals/2026-09-03-verification-shape-alignment.md slice 3 and the #778 Work Item body.
Implementation: one line in the hook plus its comment; the regime tests assert --release on the code branch and its absence on the docs-only branch.
Prevention: test_prepush_runtime_regime.py pins the hook's argv on both branches through the real hook script; the clean-clone proof below is recorded in charness-artifacts/goal-runs/775/2026-09-03-session-record.md.
Behavior: verified — clean clone of the #777 tree with the hook installed: a seeded release_only failure pushed to a local bare remote was refused (rc 1, 123 s, FAIL pytest-release, release pytest failed; stopping before later release checks); the seed removed plus a code change passed (rc 0, 257 s, 85 passed, 0 failed, PASS pytest-release 100.7s); both runs recorded in charness-artifacts/goal-runs/775/778-clean-clone-proof.md; tests/quality_gates/test_prepush_runtime_regime.py 4 passed; ./scripts/check-docs.sh PASS.
Review disposition: critique not required; a one-line cadence change decided with the operator on 2026-09-03 and proven by a seeded refusal in a clean clone.
AI-provenance: implemented, probed, and verified by an AI agent (Claude Code) in the Goal Run #775 session.
Goal lineage: Goal Run corca-ai/charness#775; draft sha256 6f2f63ecd8264a4502f7feeb9884a2e2cbb5e3f288be22536fd93a2eed010898; binding sha256 ea389dd26293eb3deff01bf502073c6d242dd84bb3a1df42b245fcac729d46b0; Work Item release-lane-standing-evidence (#778).
