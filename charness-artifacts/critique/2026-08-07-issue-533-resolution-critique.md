# Issue 533 resolution critique
Date: 2026-08-07

## Decision Under Review

Resolving issue #533 by moving the ruff invocation behind one repo-owned entrypoint
(`scripts/check-python-lint.sh`) that CI and the local gate both call, deleting the three
stale retyped copies, and pinning the surviving links with tests — rather than editing the
CI path list to match the local one.

## Failure Angles

- **Patching the symptom.** Adding `skills/shared/scripts` to the CI line would make today
  green and leave four hand-maintained copies of one command, which is what produced the
  drift in the first place.
- **Breaking the seeded runner harness.** `run-quality.sh` gates are exercised against a
  fake repo that copies only a few real scripts and stubs the rest. A gate that changes
  from an inline command to a repo-relative script disappears from that tree.
- **Deleting a regression pin while "moving" it.** `test_shared_script_gate_scope.py`
  existed as the pin for exactly this scope gap. Its assertion looks for
  `skills/shared/scripts` on the runner's ruff line; once the path moves into the script
  that assertion fails, and the cheap repair is to delete it — losing the pin for the bug
  being fixed.
- **Over-claiming prevention.** The parity validator that should have caught this
  evaluates zero jobs for this workflow, so "prevents recurrence" would be false.
- **Hard-failing on absent ruff** where the sibling shell gate skips, possibly regressing
  a consumer or fresh checkout.

## Counterweight Pass

- The hard-fail is not a behavior change and not a risk. The prior invocation ran `ruff`
  directly, so an absent binary already produced exit 127 and failed the same label. The
  change replaces an inscrutable 127 with a named remediation. The opportunistic
  pre-commit lane keeps its soft posture independently (`staged_commit_gate_plan.py`
  skips when `shutil.which` misses), so the split is coherent: opportunistic lanes
  degrade, declared gates do not.
- The label stayed `ruff` deliberately. `docs/conventions/validator-timing-layers.md`
  carries it in a gate-label table and adapter budgets key on it; renaming would have
  cost a doc edit and a budget change for no benefit.
- Widening `skill-packages`' py_compile glob is safe: the added path was already compiled
  by `run-quality.sh`, `py_compile` is idempotent, and it writes only gitignored bytecode.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/support.py:282 | action: fix | note: the seeded runner harness had no stub for the new shell gate, so the one runner test that queues the full graph exited 127; reproduced, then fixed by seeding `("ruff", "check-python-lint.sh")`
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_runner.py:650 | action: fix | note: the drift guard that exists to catch exactly F1 matched only `scripts/*.py`, so a `.sh` gate walked past a guard whose stated scope was wider than its pattern — the same defect class as the bug being fixed, one level up; widened to shell gates and proven to flag a removed stub
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_shared_script_gate_scope.py:37 | action: fix | note: the regression pin had to MOVE, not relax — the obligation is now split into "runner invokes the entrypoint" and "entrypoint covers the shared scripts", so deleting either half restores the gap
- F4 | bin: act-before-ship | evidence: strong | ref: .agents/surfaces.json:273 | action: fix | note: a second instance of the same defect that the issue does not name — `skill-packages` py_compile omitted `skills/shared/scripts/*.py` while that surface's own `source_paths` include `skills/shared/**`, so editing a shared script selected a surface whose verifier excluded it
- F5 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-08-07-issue-533-resolution-critique.md | action: document | note: the prevention claim was over-stated and is downgraded to "instance removed, single-sourced, and pinned; class prevention remains D45/S31"
- F6 | bin: valid-but-defer | evidence: strong | ref: .github/workflows/quality-core.yml:175 | action: document | note: the changed-line mutation step DOES call a repo-owned entrypoint but with a flag set the local lane does not use — argument drift on a shared entrypoint, the same class one level up, and explicitly NOT closed by this fix
- F7 | bin: valid-but-defer | evidence: moderate | ref: scripts/check-python-lint.sh:33 | action: defer | note: two hand-maintained path lists survive — ruff's and `run-quality.sh`'s `python_files` — and they already differ deliberately (py_compile covers vendored files, ruff does not); a superset pin would close it and is not built here
- F8 | bin: over-worry | evidence: strong | ref: scripts/check-python-lint.sh:29 | action: document | note: the hard-fail-vs-skip divergence from `check-shell.sh` reads like an inconsistency but restores no prior soft pass and regresses no consumer

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (repo-typed read-only reviewer, `.claude/agents/bounded-reviewer.md`).
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name, session-model inheritance per the per-host split for Claude Code hosts.
- Host exposure state: applied
- Application state: host-confirmed: both reviewers reported the read-only envelope (Read/Grep/Glob only, no Bash/Edit/Write/Agent) and returned findings inline.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. Two delegated reviewers ran: a causal review before the fix was
designed (which found the fifth copy, the `skill-packages` second instance, and the D45/S31
root cause) and this resolution critique after it was built (which found F1, F2, and the
over-claim). Both ran read-only in the shared parent worktree.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewers were given the changed-file
set inline and read the worktree directly. The binding floor is therefore not turned on
for this artifact. -->

## Boundary Ownership

- Producer: `scripts/check-python-lint.sh`, which now owns the ruff path list.
- Consumer: `scripts/run-quality.sh` and `.github/workflows/quality-core.yml`, plus the two declarative surfaces that name it.
- Owning surface: the repo's quality gate graph.
- Verdict: single-surface

## Non-Claims

- This does NOT prevent the class. The parity validator still evaluates zero jobs for this
  workflow because the file grants itself the exemption, so a CI step whose scope diverges
  from the local gate it claims to mirror remains undetected by construction. D45/S31 is
  the actual prevention and it is open.
- The new pins are string-scoped to `quality-core.yml` and one phrasing. A new workflow
  file, a different tool, or `python -m ruff check ...` would not be caught.
- F6 and F7 are named, not fixed.
