# Retro — dup-ratchet hardening goal (v0.52.6)

Goal: `issue-393-harden-the-dup-ratchet-gate-scope-paths-empty-warning-write`
(achieve goal lifecycle, slices 1–4: F/C/I hardening → in-process coverage →
push → release v0.52.6).

## Efficiency signals (measured vs proxy)

Host logs are exposed (Claude host; `token_count` available, duration/tool/turn
derivable) — see the bound host-log probe
`charness-artifacts/retro/issue-393-harden-the-dup-ratchet-gate-host-log-probe.json`.
A precise provider metrics window was not requested for this goal; the qualitative
read below is proxy, not a fabricated token/time figure.

- **Net waste: one wasted publish cycle.** The first `publish_release --execute`
  ran the full `run-quality --release`, then aborted at a single failing
  managed-install test (~70s + bump/sync/retro work discarded). Avoidable if the
  pre-push proof had exercised release-mode tests.
- **Diagnosis was cheap and correct:** the failing assertion pointed straight at
  `nose doctor version-mismatch`; root-caused to a stale `make_fake_nose` fixture
  (0.6.0 < shipped floor 0.13.3) in two probes, fixed in one line.
- **Slices 1–3 were efficient:** no rework; the bundle proof + two fresh-eye
  critiques (code push-safe, release-surface release-safe) found no blockers.

## What worked

- Folding the B1/B2 plan-critique fixes during shaping meant Slice 1 reused the
  existing evaluate path / `dup-ratchet` phase — no new phase, no false starts.
- Treating the dup-ratchet gate's own hard-block (2 new families) honestly:
  inspected members, proved id-churn of unchanged code, re-baselined with a small
  delta that dogfooded the new C guardrail.
- The release-mode gate caught a real defect the read-only proof missed — the gate
  did its job at the irreversible boundary; not bypassed.

## Findings (transferable)

1. **family_id churn on same-file edits.** Editing a scanned member file rotates
   the nose `family_id` of clusters that include it, forcing a re-baseline even
   with zero new duplication (here 2 ids rotated from unchanged `if x is None:
   return None` + `main()` boilerplate). The `dup_ratchet_lib` docstring claims the
   content-hash id is stable across *sibling* churn, but same-file edits also
   rotate. Transferable to every consumer repo that adopts the gate — directly
   relevant to the consumer-portability goal.
2. **Pre-push proof ≠ release-mode proof.** The read-only bundle proof and CI
   Quality Core skip the managed-install release-mode tests, so a stale fixture
   from the nose migration shipped to `main` (e97a2884) undetected until
   `run-quality --release` at the release boundary.

## Dispositions

- **applied:** `tests/charness_cli/tool_fakes.py` fake nose `0.6.0 → 0.13.3`
  (committed this run) — unblocked the release and fixed the stale fixture.
- **Finding 1 (family_id churn):** operator chose to file → tracked as
  [#395](https://github.com/corca-ai/charness/issues/395) (bug+documentation). Not
  promoted to a blocking gate (Floor-Addition Restraint).
- **Finding 2 (proof divergence):** operator confirmed **intended design** — the
  release-mode tests are deliberately heavier and run at the release boundary
  (layered proof), so the divergence is the intended posture, not waste. No action.
