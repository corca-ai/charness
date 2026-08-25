# Quality Review
Date: 2026-08-25

Title: Telemetry retirement, flat current-SOT docs, and task-envelope hardening

## Scope

This review covers the active usage/t-events retirement, flat `docs/` migration,
composite documentation receipt, lychee manifest, and the repo-local task
envelope. Historical artifacts remain outside the current-doc lint population.

## Surface Contract Review

- semantic coverage: partial — source/plugin behavior, docs topology, and task
  transitions were exercised; external URL reachability and real Windows
  execution were not observed here.
- surface: current docs and task state
- owner: Charness source plus generated plugin mirror
- projections: source tree, generated plugin tree, current docs, and task JSON
- state scope: tracked repository files plus gitignored local task state
- transitions: retired telemetry, docs-path migration, task claim/submit/review
- proof boundary: deterministic tests, composite docs receipt, packaging parity,
  and bounded fresh-eye reviews
- unexamined axes: live consumer adoption, online external links, Windows host
  process behavior

## Current Gates

- `./scripts/check-docs.sh`: pass; 44 current docs, zero orphans/islands,
  command-contract check pass, internal lychee 758/758 resolved, external links
  discovered but not fetched offline. Markdown reports 22 advisory wrapped
  inline-code spans; `MD013` remains disabled, so no 80-column gate exists.
- Focused task/docs/packaging proof: 49 tests pass after source/plugin sync;
  the final task-envelope and YAML branch run is 20/20.
- Selected quality receipt: 7 checks pass, including ruff, current-pointer
  freshness, export self-sufficiency, boundary-bypass ratchet, command docs,
  docs receipt, and duplicate ratchet. Duplicate families are explicitly
  classified only where review found portability or ownership boundaries.
- The earlier broad standing run reached 11,178 passed; its seven failures were
  checked-in plugin drift caused by a later source edit. Export + manifest sync
  followed by the focused 49-test rerun is the current proof for that class.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  plus the run-quality receipt and pytest output.
- runtime hot spots: the prior standing suite is the dominant cost; docs/dup
  checks stayed under ten seconds.
- coverage gate: changed-line mutation coverage was not rerun in this closeout,
  so no mutation verdict is claimed.
- evaluator depth: deterministic gates only; no Cautilus run was requested.

The selected quality receipt passed in 8.4s for its seven checks. The prior
standing run reached 11,178 passes before seven source/plugin-drift failures;
after export and manifest sync, the focused 49-test mirror/task rerun passed.

## Healthy

Usage-episode and t-event active producers, schemas, adapters, and tests are
removed. RCA and lesson-ledger records remain. Current docs carry status/source
metadata, use a flat topology, and route one operator receipt through Markdown,
graph, reference, command-contract, and link checks. Task transitions now use
atomic writes, CAS, POSIX locks or a bounded Windows lock-directory fallback,
opaque execution refs, one result carrier, and parent-owned review.

## Weak

The duplicate scanner still emits advisory lineage warnings for legacy baseline
members. External lychee is discovery-only offline. Historical artifacts may
contain old vocabulary or links; the specifically affected migration records
were marked historical/superseded or repaired in this slice.

## Missing

No real Windows process race or live consumer-repo roundtrip was run. No online
external-link proof or Cautilus evaluation is claimed.

## Deferred

- Windows concurrent-writer proof remains deferred until a Windows runner is
  available.
- Online external-link validation remains deferred until a network-enabled CI
  channel is granted.

## Advisory

- Duplicate-ratchet legacy lineage warnings remain advisory because `command:
  python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root .`
  reports no new fixable family while the old baseline lacks member paths.
- External lychee was discovery-only because `command: ./scripts/check-docs.sh`
  ran offline; 78 URLs were found and not presented as online-validated.

## Delegated Review

- status: executed — runtime fresh-eye review: first round found CAS, atomic-claim, recovery-command,
  and execution-ref gaps; repairs were re-read and the remaining Windows/fallback
  and stale-verdict issues were repaired.
- status: executed — artifact fresh-eye review found stale flat-doc links and deleted lifecycle
  capture claims; those links and dogfood entries were removed or marked
  historical, and the current pointer was refreshed. Three older spec links
  were subsequently classified as historical or redirected to current owners.
- status: executed — counterweight review required review metadata clearing on resubmit and
  executable, repo-root-qualified `next_step` commands; both are now tested.
- status: executed — final runtime review required malformed stale Windows leases
  to be recoverable, lock timeout to emit a structured rejection, and review
  recovery to include a copy/paste command; all three are now covered.

## Commands Run

`./scripts/check-docs.sh`; selected `run-quality.sh --read-only`; focused task,
docs, packaging, and plugin-preamble tests; `python3 scripts/export_plugin.py`
for Claude/Codex; `sync_root_plugin_manifests.py`; `ruff`; `git diff --check`.

## Recommended Next Quality Moves

- passive because this host is Linux-only — capability_needed=Windows host; next_center=task lock roundtrip;
  transformation=run a concurrent writer test on Windows; proof_boundary=CAS
  and stale-lock recovery; enforcement_posture=no-gate because this host cannot
  observe it until a Windows runner is available.
- passive because this run was offline — capability_needed=network; next_center=external link validation;
  transformation=run lychee online in CI; proof_boundary=distinct hosted
  readback; enforcement_posture=no-gate because offline discovery is honest until
  a network-enabled validation channel is granted.

## History

- [2026-08-18 quality review](history/2026-08-18-quality-review.md)
