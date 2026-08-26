Closes #669

JTBD: prevent a SIGTERM arriving during `Popen` construction from orphaning
the monitored child process group.

Boundary: Charness owns the shared process guard, its checked-in plugin export,
and the local POSIX child-plus-grandchild proof. Windows, every host kernel,
SIGKILL, hosted enforcement, installed adoption, and consumer rollout remain
outside this resolution.

Resolution brief: record interrupt-like signals across the constructor binding
boundary, restore the caller handler inside the cleanup envelope, kill and drain
the group, then replay the recorded signal.

Implementation: commit `529062620a28fdae8413dc7b961846266412dee6` updates
`scripts/subprocess_guard.py`, the checked-in plugin export, and the deterministic
regression fixture in `tests/test_subprocess_guard.py`.

Prevention: retain the real-Popen-before-return child-plus-grandchild fixture;
run focused and related combined checks from an explicit clean named worktree.

Root cause: cleanup began only after the Popen object was bound, leaving a
fork/exec-to-return interruption window without a process-group owner.
Debug artifact: charness-artifacts/debug/2026-08-27-issue-669-sigterm-popen.md
Siblings: `scripts/standing_pytest_run_record.py` uses the shared guard; decision:
same class, fix now; proof: its caller signal boundary was exercised by the
related combined standing run.

Critique #669: blocked host exposes no subagent/Agent tool in this session; direct operator override
Behavior #669: local-only-by-contract — clean named POSIX process-group fixture and standing runner proof
AI-provenance: authored by an agent session.
Manual fallback reason: operator-directed-manual-close.

Explicit non-claims: no universal changed-line proof, forced fresh-eye review,
handoff update, micro-slice record, every-kernel or Windows guarantee, remote CI,
installed-host behavior, consumer-repository adoption, push, release, or tag is
claimed. The separate release-planner timeout reported in the existing issue
comment was not bundled into this fix and remains a successor candidate.
