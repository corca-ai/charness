# Session Retro
Date: 2026-07-10

## Mode

session

## Context

This retro covers the repo-wide quality, bug-fix, speed, and v0.64.0 release
goal at `charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md`.
The work repaired usage-feedback counting and malformed-history handling,
added measured bootstrap and Markdown fast paths, locked the final proof, and
published and refreshed the maintainer installation.

## Evidence Summary

- Release: `https://github.com/corca-ai/charness/releases/tag/v0.64.0`, published
  `2026-07-10T00:39:04Z`; local `main` equals `origin/main` and tag `v0.64.0`
  exists.
- Verification lock: 4,419 coverage-instrumented tests passed; changed-line
  mutation readback reported `blocking: []` for all nine mutation-pool files.
- Distinct-channel public readback: HTTPS fetch of the release URL returned 200.
- Fresh checkout probes passed; `charness update` refreshed the installed
  surface to 0.64.0. Installed `charness version --verbose` reports 0.64.0,
  GIT_HEAD `ad673083`, and `managed-local-cli`.
- Host/tool proof: installed source/cache/Claude surfaces are 0.64.0 and ready;
  `nose` doctor is ready at 0.18.0, dry-run resolves the upstream latest
  installer, `nose --version` is 0.18.0, support sync is skipped because no
  support source is declared, and clone inventory is advisory-only.
- Host log probe: `charness-artifacts/probe/2026-07-10-repo-wide-quality-speed-release.json`.
- Packet Consumed: `charness-artifacts/retro/repo-wide-quality-speed-release-closeout-retro-packet.md`.

## Waste

- Three bounded reviewer runs crossed their read-only boundary: one staged and
  committed reviewed content, a replacement reviewer spawned an unauthorized
  coding child, and the final disposition reviewer mutated `docs/handoff.md`
  and generated the retro packet. The child made no edits; the committed
  content was audited and retained, while all violating approvals were
  discarded. The handoff diff was audited and the packet was canonically
  regenerated with `prepare_packet.py`; the repo-local AGENTS contract already
  states the guard, so no duplicate prose was added.
- Release execution output was lost after its session closed. Release state
  had to be reconstructed from the checked-in release artifact, git/remote
  readbacks, the public HTTPS channel, and installed-machine proof. The
  resulting artifact/state readback was sufficient; no new code change was
  justified.
- After update, injected 0.63.1 skill paths were stale. The stable 0.64.0
  resolver correctly re-resolved them, so no resolver change was needed.

## Critical Decisions

- Rank slices by evidence and preserve correctness gates; do not optimize
  unmeasured paths or broaden the release surface speculatively.
- Keep 16 pytest workers because it was the measured optimum; report speed
  only for directly measured production/operator paths.
- Use the repo-owned release helper and require a distinct HTTPS observer for
  the irreversible publication boundary.

## Expert Counterfactuals

- Engelbart H+LAM+T lens: make the evidence chain (measure, link, verify,
  publish) explicit before changing a path; this kept the speed claims honest
  and made reconstruction possible when a session transcript was unavailable.
- Operational lens: preflight observer ownership and durable state before
  release execution; a release artifact plus independent readback is the
  minimum useful recovery surface for lost runtime output.

## Sibling Search

- reviewer boundary violations | decision: issue #428 | proof: three violations
  recurred in this run despite existing policy; issue is OPEN and body-verified;
  follow-up: issue #428 (recurs: three violations in this run despite existing policy)
- release-session output loss | decision: artifact/state readback sufficient,
  no code change | proof: release artifact, remote/public/install readbacks;
  follow-up: none — no concrete structural gap
- stale injected skill paths after update | decision: resolver worked,
  no change | proof: installed update output and stable 0.64.0 resolver;
  follow-up: none — existing capability is sufficient

## Next Improvements

- applied: evidence-ranked slices, changed-line coverage, release helper,
  distinct-channel verification, and install refresh are now part of this
  goal's durable proof.
- issue #428 (recurs: three reviewer boundary violations in this run despite
  existing policy) owns the structural follow-up; `AGENTS.md` remains the
  existing repo-local guard.
- none — no additional transferable structural gap was found after the
  release/readback reconstruction.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-10-repo-wide-quality-speed-release.md

Packet Consumed: charness-artifacts/retro/repo-wide-quality-speed-release-closeout-retro-packet.md
