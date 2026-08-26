# Achieve Lifecycle

`achieve` runs one goal as three phases: **before** (research, approval, and
binding), **during** (provider pickup and child execution), and **after**
(issue-owned proof and guarded close). The complete Goal Draft is immutable
planning provenance; the provider-backed Goal Run is execution authority.

Each phase's contract lives in its own file so a run reads only its current
phase instead of the full three-phase document:

- `references/lifecycle-before.md` — research, interview, approval, and binding.
- `references/lifecycle-during.md` — exact pickup, child execution, and retry.
- `references/lifecycle-after.md` — child proof, guarded close, and non-claims.

The current implementation's phase brief is advisory. Read the phase file that
matches the operation and use provider readback as the authority for execution.

## Honest Proof Discipline

Borrow W. Edwards Deming's Plan-Do-Study-Act emphasis on the *study* step:
measure the result against the original prediction before claiming the goal is
met. A run that skips the comparison has done activity, not achievement.

Never claim provider, live, or release proof when only local deterministic
checks ran. If a proof level was skipped, the final report must say so.
