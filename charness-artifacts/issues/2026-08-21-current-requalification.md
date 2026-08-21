# Current Requalification Packet: Issues #681–#687

Captured: 2026-08-21T19:22:28+09:00; release-boundary refresh: 2026-08-21
Source candidate: semantic `502c8a8adbbe77781f1714cb6c4383a85d6e3683`,
integrated proof HEAD `d0df6dc7ac9c761b14bd1d5c5ef8b95bd1f2ec9d`
Source of issue truth: the durable current GitHub reads in
`charness-artifacts/issues/reads/{681,682,683,685,686,687}.raw.yaml`; all six
reads returned `comments_read: true` (the closed #684 read is retained
separately). This packet records current behavior only. It does not
close a GitHub issue, replace the activation ledger, or claim issue closure.

Published release join: version `6.2.1`; tag `v6.2.1` targets
`46169b7ad7491e1d4b1a50b5411ebf5a08f03a68`; post-publish artifact commit and
`origin/main` are `d0df6dc7ac9c761b14bd1d5c5ef8b95bd1f2ec9d`; the GitHub Release
is confirmed by `gh release view v6.2.1`. The managed install was refreshed
with supported `charness update --detail`, then `charness version` matched
`6.2.1` and `charness doctor --detail` reported valid cache/no source-cache
drift. This is package/install/doctor proof, not an issue-specific semantic
probe or host-side #687 proof.

Historical documentation join: the older `331c4a23032821436b47b3104fb2b80452c12266`
to `22ea27d7847d7f44d8258cae19fea7bf0ee5c4d5` range is retained only as
historical no-source-diff evidence. It is not the current candidate and must
not be used as installed or host proof.

Candidate-bound status join: the current source candidate is
`502c8a8adbbe77781f1714cb6c4383a85d6e3683`, the exact semantic candidate
containing the root host-delivery exit/provenance repair, same-version content
readback, scoped recovery, failure-aware init/update output, and boundary
regression coverage. Its exact packet is
`charness-artifacts/critique/2026-08-21-r3-delivery-provenance-repair-current-exact-packet.json`
with packet SHA256
`5a936834bce7fe68db1f894e5e6764de336d9b8dbd4e69fd26f472ab07632ef7` and
reviewed-input identity
`26f29ca25c71bf4d704854285c787734f9a1e99bc7d770a9df8674ee3778dfc2`.
The matrix below records which issue-specific claims remain open after the
general package/install readback; this source join does not claim host-side
#687 resolution. The earlier
`7676ec51aeed99e215106dd8490332e57db80d07` and
`1e81fb31bc8017e09f58f905b8c7b41e8545ad00` pointers are historical.

Integrated release-boundary evidence now includes `98 passed, 0 failed` from
`./scripts/run-quality.sh --release`, a clean broad changed-line proof across
53 mapped files, 5/5 fresh-checkout probes, public release readback, and
managed install/version/doctor readback. Tracker closure was not requested;
host-side #687 remains explicitly unproven.

## First Reader Outcome

The release train repairs one operator-facing failure class: a successful
process, source mirror, clean fingerprint, or old installed cache must never be
read as proof that behavior was delivered. Current status is published and
installed/read back at `6.2.1`. The general operator path was verified with
`charness update`, `charness version`, and `charness doctor --detail`; the
issue-specific semantic probes and tracker closeout remain separately
unclaimed, and host-side #687 resolution is not inferred.

## Disposition Matrix

| Issue | Source | Checked-in export | Installed/public | Host | Release status |
| --- | --- | --- | --- | --- | --- |
| #681 | Checker returns `ok: true`, `cadence_owner.applies: true`, and no findings. | No source/export change required by requalification. | General `6.2.1` install/version/doctor readback verified. | Not applicable. | `already-satisfied` source; tracker closeout not requested. |
| #682 | Explicit committed-range basis evaluates; bare empty basis remains `not-established`. | Prove/planner committed-basis carrier shipped in `6.2.1`. | General release readback verified; issue-specific replay not rerun post-publish. | Not applicable. | Source repair shipped; tracker closeout not requested. |
| #683 | Snapshot emits exact `verify --before` continuation; supported replay is clean. | Handoff/fingerprint carrier shipped in `6.2.1`. | General release readback verified; issue-specific replay not rerun post-publish. | Not applicable. | Source repair shipped; tracker closeout not requested. |
| #685 | Source normalizes stem to `.md` without warning. | Checked-in source/plugin repair shipped in `6.2.1`. | General release readback verified; dedicated persistence probe not rerun post-publish. | Host install is not an issue-specific host proof. | Repair shipped; tracker closeout not requested. |
| #686 | Source planner emits `$SKILL_DIR/scripts/check_auto_trigger.py`, flattened path, and `available: true`. | Checked-in source/plugin repair shipped in `6.2.1`. | General release readback verified; dedicated planner probe not rerun post-publish. | Host install is not an issue-specific host proof. | Repair shipped; tracker closeout not requested. |
| #687 | Typed interruption/timeout/channel-loss/recovery states are present. | Charness child and delivery contract shipped in `6.2.1`. | General install/doctor readback verified. | Host terminal event remains explicitly unproven. | Charness prevention shipped; host resolution and tracker closeout are not claimed. |

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

The source repairs are carried in published `6.2.1`, and the distinct general
installed/public readback is bound above. Historical post-lock reproductions
remain retained for issue-specific follow-up; issue closure and host-side #687
resolution remain unclaimed.

## Maintainer Candidate Proof Boundary

Before publication, the exact candidate was installed/read back in the managed
home. The general typed outputs are bound to the post-publish artifact commit;
issue-specific `#682/#683/#685/#686` probes remain a separate follow-up and are
not implied by version/doctor success.

## Operator Upgrade Boundary

After publication, the first-reader path `charness update` followed by
`charness version` and `charness doctor --detail` was executed successfully.
Rollback still means reinstalling the previous published version and repeating
version/doctor readback; issue tracker closure is intentionally a separate
operation.
