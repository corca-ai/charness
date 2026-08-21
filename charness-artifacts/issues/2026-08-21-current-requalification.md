# Current Requalification Packet: Issues #681–#687

Captured: 2026-08-21T08:40:35Z
Tree: `331c4a23032821436b47b3104fb2b80452c12266`
Source of issue truth: the durable current GitHub reads in
`charness-artifacts/issues/reads/{681,682,683,685,686,687}.raw.yaml`; all six
reads returned `comments_read: true` (the closed #684 read is retained
separately). This packet records current behavior only. It does not
close a GitHub issue, replace the activation ledger, or claim publication.

## Disposition Matrix

| Issue | Current observation | Current disposition | Remaining boundary |
| --- | --- | --- | --- |
| #681 | Current goal checker returns `ok: true`, `cadence_owner.applies: true`, and the detected cadence line in one coherent payload. | `already-satisfied` requalified | Consumer installed-version readback and issue closeout remain. |
| #682 | Bare post-commit trigger check returns `state: not-established`, exit 3, and no `triggered`; explicit `HEAD^..HEAD` evaluation returns exit 0 with `state: evaluated`. Current prove/retro guidance and planner emit the explicit committed basis. | Charness-side repair present; retain historical blocker evidence until carrier is integrated into the release candidate. | The empty-basis command must remain visibly non-verdict; final candidate closeout must read the planner packet, not a bare invocation. |
| #683 | Snapshot emits `verify_before` and exact `verify_args`; `verify --before <custom-path>` succeeds for a fresh isolated window. The guessed `--snapshot` flag is rejected, as it should be. | Charness-side handoff repair present; retain historical blocker evidence until candidate proof. | Boundary drift and findings delivery remain separate; no approval follows from a clean fingerprint. |
| #685 | Current source normalizes a stem to `.md` without the contradictory warning. Installed Charness 6.2.0 still emits the warning, exit 0. | Source repair present; installed/public proof pending. | Fresh managed install/update readback must show the repaired behavior. |
| #686 | Current source planner emits `python3 "$SKILL_DIR/scripts/check_auto_trigger.py"`, `path: scripts/check_auto_trigger.py`, `available: true`, and `ok: true`. Installed Charness 6.2.0 still emits the source-layout path as unavailable while returning `ok: true`. | Source/export repair present; installed/public proof pending. | Fresh managed install/update readback must show flattened-path resolution and fail-closed readiness. |
| #687 | Charness delivery state machine has typed terminal states for interruption, timeout, channel loss, and transcript recovery; no host event trace proves the observed Codex episode's terminal state. | `partial-child-shipped` / host non-claim | A host-side terminal event channel is still external to Charness and cannot be claimed from source tests. |

## Exact Current Checks

### #681

```text
python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md
exit: 0
ok: true
cadence_owner.applies: true
cadence_owner.ok: true
findings: []
```

### #682

```text
python3 skills/public/retro/scripts/check_auto_trigger.py --repo-root .
exit: 3
state: not-established
input.mode: working_tree_diff
changed_paths: []
```

This is intentionally not a `no retro owed` answer. The committed-basis
positive control was:

```text
python3 skills/public/retro/scripts/check_auto_trigger.py --repo-root . --base-ref HEAD^ --head-ref HEAD
exit: 0
state: evaluated
input.mode: commit_range
changed_paths: [charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md, charness-artifacts/quality/2026-08-21-fresh-eye-retro-basis-changed-line.md, docs/handoff.md]
triggered: false
```

The current consumer contract in `skills/public/prove/SKILL.md` explicitly
requires `--base-ref <slice-base> --head-ref <slice-head>` after commit, and
the planner's `auto-session-trigger` packet carries the same range.

### #683

An isolated snapshot invocation returned `verify_before` and the exact
continuation argv. Replaying that argv with `--before` returned `ok: true`,
`verdict: clean`, and `drift: []` for the same fresh window. A verification
without the explicit `--before` path read the repository's older default
snapshot and returned a window mismatch; that is a stale/default-input signal,
not a delivery verdict.

The copied `--snapshot` form exits 2 with an argparse error. This wrong flag is
preserved as command-boundary evidence; the supported continuation is
machine-emitted by `snapshot` itself.

### #685

Current source, isolated temporary repo:

```text
python3 skills/public/retro/scripts/persist_retro_artifact.py --repo-root <tmp> --artifact-name requalify-685 --markdown-file <tmp>/input.md --force-empty-summary
exit: 0
artifact_name_normalized: true
artifact_path: charness-artifacts/retro/requalify-685.md
stderr: empty
```

Installed 6.2.0, same isolated fixture and stem:

```text
exit: 0
stderr: persist_retro_artifact: --artifact-name 'requalify-685' lacks .md; writing 'requalify-685.md' so the lesson-selection-index can read it.
```

The installed warning is the remaining public-surface failure; the successful
exit does not make the warning truthful.

### #686

Current source planner:

```text
auto-session-trigger.command: python3 "$SKILL_DIR/scripts/check_auto_trigger.py" --repo-root . --paths scripts/example.ts
path: scripts/check_auto_trigger.py
available: true
ok: true
```

Installed 6.2.0 planner:

```text
auto-session-trigger.command: python3 skills/public/retro/scripts/check_auto_trigger.py --repo-root .
path: skills/public/retro/scripts/check_auto_trigger.py
available: false
ok: true
```

This is a source-versus-installed-layout distinction, not permission to claim
the installed old copy repaired.

### #687

The current Charness tests and delivery schema prove typed non-delivery states
and forbid late findings from resurrecting an interrupted attempt. The adjacent
Codex source remains a pinned host hypothesis, not a runtime trace of this
episode. No fresh-eye PASS or BLOCK approval is inferred from this packet.

## Candidate Gate

The source repairs may be carried into the next semantic candidate, but this
packet does not discharge the installed/public boundary. The historical
post-lock exception reproductions remain retained in the release ledger until
the candidate's source/export proof and the distinct installed readback are
bound. Version mutation, publication, issue closeout, and host-side #687
resolution remain unclaimed.
