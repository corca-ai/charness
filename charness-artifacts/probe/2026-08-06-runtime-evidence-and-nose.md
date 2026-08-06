# Runtime and Installed-Host `nose` Evidence Packet

Date: 2026-08-06
Goal: [runtime evidence and final boundary](../goals/2026-08-07-runtime-evidence-and-final-boundary.md)

## Scope

This packet binds the existing controlled runtime A/B evidence to the
manifest-supported installed-host `nose` lifecycle. It is host-local and
time-bound. It does not claim a runtime-budget change, cross-host behavior,
provider freshness, live-agent behavior, remote CI, release parity, or issue
state.

## Frozen identities

- Source checkout: `/home/hwidong/codes/charness`, `HEAD`
  `8047a6147ba7ffba7c15ff71ca90f8d559a2f563`.
- Installed managed checkout: `/home/hwidong/.agents/src/charness`, `HEAD`
  `7eed13ec9b819e6d581ea08ea244820579c08935`, version `3.3.0`.
- Target repo reported by the installed CLI: `/home/hwidong/codes/charness`.
- Host: `narnia`, Linux 5.15.0-171-generic, x86_64, 36 CPUs available.
- Probe timestamp: `2026-08-06T10:17:20Z`–`2026-08-06T10:17:31Z` UTC.
- Binary path: `/home/hwidong/.cargo/bin/nose`.

The source and installed checkout SHAs differ; installed-host observations are
therefore evidence about the installed `3.3.0` checkout, not proof that the
uncommitted source worktree is what the host loaded.

## Runtime evidence

Reused packet: [charness-artifacts/quality/2026-08-06-runtime-ab-evidence.md](../quality/2026-08-06-runtime-ab-evidence.md).
Its controlled same-host A/B used the same command, six samples per arm, and
`taskset -c 0-3`:

- isolated, no background workers: `6451, 6503, 6511, 6551, 6567, 6615 ms`,
  median `6531 ms`, return codes `6/6 zero`;
- synthetic contention from four CPU burners on the same affinity:
  `10275, 10428, 10433, 10493, 10576, 10664 ms`, median `10463 ms`, return
  codes `6/6 zero`.

Disposition: retain the `15.500s` budget and classify the result as
contention-sensitive, same-host advisory evidence. It does not establish the
exact repaired runner's causal effect, a cross-host cohort, or a threshold
change.

## Installed-host command receipts

All commands below returned exit code `0` unless stated otherwise.

### Pre-install doctor

Command: `charness tool doctor nose --no-write-locks`

Observed installed checkout: `/home/hwidong/.agents/src/charness`.
Doctor status: `ok`; disposition: `ready`; observed version: `0.20.0`; upstream
latest: `v0.20.0`.

This host did not provide a missing-tool observation, so it does not prove the
missing → installed transition.

### Install dry run

Command: `charness tool install nose --dry-run --detail`

Observed manifest route:

```text
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/corca-ai/nose/releases/latest/download/nose-cli-installer.sh | sh
```

Release API status: `ok`; latest tag: `v0.20.0`; detected version: `0.20.0`;
version constraint `>=0.17.0` matched; support status: `skipped` because the
integration has no support skill source.

### Supported install

Command: `charness tool install nose --detail`

Observed install status: `installed`; mode: `script`; installer exit code: `0`.
Installer stdout reported installation to `/home/hwidong/.cargo/bin` and
`everything's installed!`.
Installer stderr reported `downloading nose-cli 0.20.0 x86_64-unknown-linux-gnu`.

### Version and PATH

Command: `nose --version`

Observed stdout: `nose 0.20.0`; resolved path:
`/home/hwidong/.cargo/bin/nose`.

### Post-install doctor

Command: `charness tool doctor nose --no-write-locks --detail`

Observed at `2026-08-06T10:17:27Z`: detection `ok`, `nose --version` exit
`0`, version `0.20.0`, constraint `>=0.17.0` matched, `doctor_status: ok`,
`doctor_disposition: ready`, `support_state: integration-only`, and
`update_advisory: current`.

### Support synchronization

Command: `charness tool sync-support nose --detail`

Observed at `2026-08-06T10:17:31Z`: support `skipped`, reason integration has no
support skill source; `support_sync.status: not-tracked`; no expected or
materialized support paths.

### Source-checkout clone inventory

Command: `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json`

Observed: `status: findings`, `advisory: true`, exit code `0`, all requested
roots (`scripts`, `skills/public`, `skills/support`) scanned with no missing
paths; tool version `0.20.0`; 9 reported families, 1302 duplicated lines.
The result warns that the committed baseline was written under `nose 0.19.0`.
These are advisory refactoring candidates, not standing quality failures, and
the version-skew warning is not a reason to treat the result as a clean
baseline comparison. No baseline was rewritten in this goal.

## Verification boundary

The packet proves that the installed host can detect, install, execute, doctor,
and synchronize the manifest-declared `nose` integration, and that the source
checkout inventory reaches the advisory scanner with complete declared scope.
It does not prove that the installed checkout contains source `HEAD`, that
the clone baseline is current for `nose 0.20.0`, or that provider, remote-CI,
cross-host, live-agent, release, or issue behavior is healthy.
