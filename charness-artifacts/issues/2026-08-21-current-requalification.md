# Current Requalification Packet: Issues #681–#687

Captured: 2026-08-21T19:22:28+09:00; release-boundary refresh: 2026-08-21
Source candidate: semantic `502c8a8adbbe77781f1714cb6c4383a85d6e3683`,
integrated proof HEAD `26f31a8729ca5b804931b62d1edaef8b1311b1d0`
Source of issue truth: the durable current GitHub reads in
`charness-artifacts/issues/reads/{681,682,683,685,686,687}.raw.yaml`; all six
reads returned `comments_read: true` (the closed #684 read is retained
separately). This packet records current behavior only. It does not
close a GitHub issue, replace the activation ledger, or claim publication.

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
The matrix below still records candidate package/install/host proof as
pending; this source join does not claim those boundaries. The earlier
`7676ec51aeed99e215106dd8490332e57db80d07` and
`1e81fb31bc8017e09f58f905b8c7b41e8545ad00` pointers are historical.

Integrated release-boundary evidence now includes `98 passed, 0 failed` from
`./scripts/run-quality.sh --release`, a clean broad changed-line proof across
53 mapped files, and 5/5 fresh-checkout probes. The generated SLOC refresh is
the only change after the semantic candidate; package/install/host readback,
publication, and tracker closure remain pending.

## First Reader Outcome

The release train repairs one operator-facing failure class: a successful
process, source mirror, clean fingerprint, or old installed cache must never be
read as proof that behavior was delivered. Current status is pre-version and
not release-ready. Before publication, the maintainer can install/update the
exact candidate in a clean home and read back `charness version`,
`charness doctor --detail`, and semantic `#685/#686` behavior. After
publication, the operator path is `charness update` followed by the same
readback; rollback means reinstalling the previous published version and
repeating that readback.

## Disposition Matrix

| Issue | Source | Checked-in export | Installed/public | Host | Release status |
| --- | --- | --- | --- | --- | --- |
| #681 | Checker returns `ok: true`, `cadence_owner.applies: true`, and no findings. | No source/export change required by requalification. | Installed/tracker readback pending. | Not applicable. | `already-satisfied` source; not tracker-closed. |
| #682 | Explicit committed-range basis evaluates; bare empty basis remains `not-established`. | Prove/planner committed-basis carrier present; exact candidate package proof pending. | Old installed copy not used as candidate proof. | Not applicable. | Release exception retained until candidate proof. |
| #683 | Snapshot emits exact `verify --before` continuation; supported replay is clean. | Handoff/fingerprint carrier present; exact candidate package proof pending. | No candidate installed readback. | Not applicable. | Release exception retained; clean fingerprint is not approval. |
| #685 | Source normalizes stem to `.md` without warning. | Checked-in source/export repair present; target-bound export/package proof pending. | Installed 6.2.0 still warns and exits 0; candidate readback pending. | Host install not run for candidate. | Release exception retained. |
| #686 | Source planner emits `$SKILL_DIR/scripts/check_auto_trigger.py`, flattened path, and `available: true`. | Checked-in source/export repair present; target-bound export/package proof pending. | Installed 6.2.0 emits source-layout unavailable path while `ok: true`; candidate readback pending. | Host install not run for candidate. | Release exception retained. |
| #687 | Typed interruption/timeout/channel-loss/recovery states are present. | Charness child is exportable; host event is not a Charness source fact. | Candidate install/readback pending. | Host terminal event remains explicitly unproven. | Charness prevention may ship; host resolution is not claimed. |

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

## Maintainer Candidate Proof Boundary

Before publication, install or update the exact candidate in a clean managed
home, then read back `charness version`, `charness doctor --detail`, and the
installed `#682/#683/#685/#686` semantic probes. Bind the typed outputs to the
candidate SHA. A successful process without those readbacks is not candidate
proof.

## Operator Upgrade Boundary

After publication, the first-reader path is `charness update`, then
`charness version` and `charness doctor --detail`; the release record must bind
the installed semantic probes. Rollback means reinstalling the previous
published version and repeating version/doctor readback. Public rollback is
not available before publication, and a successful process without those
readbacks is not a completed upgrade.
