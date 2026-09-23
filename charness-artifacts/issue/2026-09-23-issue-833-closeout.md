Closes #833

Critique #833: charness-artifacts/critique/v8110-critique.md

JTBD: Task-run worktrees whose lanes already integrated must not linger as registered worktrees that audit cannot resolve; operators need integrated-vs-dirty-vs-unintegrated dispositions instead of permanent deferral.
Boundary: Ancestry or patch-equivalence counts as integrated; dirty trees and unintegrated branches are never removed, only reported with age; task end releases only worktrees with no commits beyond the base and a clean tree.
Resolution brief: `git cherry` fallback in cleanup containment; audit prune reclaims integrated-and-clean task worktrees (plus branch); empty lanes release at task end; the divergence error names unique commits and their equivalence.
Implementation: scripts/worktree/{cleanup_lib,audit_lib}.py, scripts/task_run/task_run_retention.py, root launcher divergence detail, docs/worktree-prepare.md, tests test_worktree_reclaim_833.py and managed-install divergence tests.
Prevention: Patch-equivalence, report-only refusals, and empty-lane release pinned by reclaim tests and the changed-line gate; the migrated managed commits' fallout (reference trigger, local-context declarations, timeout contract) covered by existing gates.
Behavior #833: Confirmed via behavior test channel — test_worktree_reclaim_833.py passes on the shipped tree, exercising cherry-picked cleanup acceptance, prune reclaim and report-only refusals, and empty-lane release with stray/commit retention.
AI-provenance: Authored by an agentic coding session (Muse Code) from behavior tests and the v8.11.0 critique; a human operator reviews before publication.
