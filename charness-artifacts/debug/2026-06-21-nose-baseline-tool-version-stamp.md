# nose Baseline tool_version Stamp Debug
Date: 2026-06-21

## Problem

The nose clone scanner writes two checked-in id-set baselines — the non-blocking
clone advisory (`nose-baseline.json`) and the BLOCKING dup-ratchet gate
(`dup-ratchet-baseline.json`) — each a sorted `code_family_ids` list. The contract
says "re-baseline per scanner version" everywhere, but neither baseline recorded the
producing nose version. A future nose bump silently changes how `family_id` is
computed, so every stored id is stale: the advisory floods with false drift and the
blocking gate FALSE-HARD-BLOCKS a wall of "new" families that are pure version
rotation, with no signal telling the operator "this is a scanner skew — re-baseline"
versus "real new duplication — remove it" (#391, surfaced by the 0.52.5 release critique).

## Correct Behavior

Given the gate/advisory key newness on a scanner-version-scoped `family_id` set,
when the live scanner version differs from the version that produced the baseline,
then the surface must surface an actionable "re-baseline" signal rather than read the
stale id-set as new duplication — and the BLOCKING gate must keep blocking (never
silently degrade, which would let real new duplication through) while explaining that
the block is probably version rotation.

## Observed Facts

- `nose_report_lib.resolve_tool_version` already detects `nose --version`, and
  `collect_families` already returns `tool_version` in its payload — the detection
  primitive existed; the writers discarded it.
- `build_baseline` / `build_gate_baseline` serialized only `schemaVersion`/`note`/
  `code_family_ids`; no version axis reached either baseline file.
- The `--write-baseline` large-delta guard (`check_dup_ratchet.py`) catches a >50
  mass-rotation, but only on the maintenance WRITE, never on the blocking `evaluate`
  READ — so the false-hard-block ships first; the guard is downstream of an already
  confused operator.
- nose bumped 0.13.x → 0.14.0 THIS session (chunk-2), rotating the whole baseline —
  the exact trigger, materialized, not hypothetical.

## Reproduction

Dogfood on this repo's own baselines:

- Re-baseline both via `--write-baseline` → each now stamps `tool_version: 0.14.0`
  from the same scan that minted the ids; gate clean, `version_skew: null`.
- Injected drive: a gate baseline stamped `0.13.0` against a live (injected) scan
  stamped `0.14.0` with all ids rotated → the gate STILL returns `status: hard-block`
  AND a `version_skew` message naming both versions
  (`test_inproc_version_skew_warns_without_degrading_block`).
- A legacy unstamped baseline against a `0.14.0` scan → `version_skew: null`, no false
  warning (`test_inproc_no_version_skew_on_legacy_unstamped_baseline`).

## Candidate Causes

- Both baseline writers serialize ids only; the available `tool_version` is dropped
  at the build step — confirmed (`build_baseline`/`build_gate_baseline`).
- No read-time version comparison existed on either consumer — confirmed.
- (Rejected) the detection primitive was missing — disproven: `resolve_tool_version`
  + `collect_families.tool_version` already existed; only stamp+compare were absent.

## Hypothesis

If a derived id-set baseline is a cache keyed by the scanner's id algorithm, and the
algorithm version is unrecorded, then a scanner bump makes every key stale
indistinguishably from real drift. Stamping the producing version on write and
comparing it on read (warn, never degrade; a missing stamp = "unknown", not a
mismatch) closes the gap without breaking legacy baselines.

## Verification

- Re-baselined both id-sets lockstep → both stamped `tool_version: 0.14.0`, identical
  526-id sets, gate `status: clean`, `version_skew: null` (live matches stamp).
- Targeted suites green: 98 (nose + dup-ratchet) + 33 (advisory + boundary-bypass +
  doc-duplicates). Every changed/new line driven in-process (the #393/#394
  changed-line-coverage class).
- Three bounded fresh-eye reviewers (correctness, behavior/scope, counterweight) →
  unanimous SHIP; warn-not-degrade and the additive-no-schema-bump choices confirmed.

## Root Cause

The mistaken model: "a checked-in derived id set is self-describing data, so the
baseline only needs to store the ids — the tool that minted them is an environmental
constant." Reality: a hash-keyed baseline is a cache keyed by an UNRECORDED function
(the scanner's normalize+hash). When that function changes (version bump, scope-model
swap), every stored key is stale, but nothing records which function-version produced
them, so skew is indistinguishable from real drift.

## Detection Gap

- writer drop | both writers had `tool_version` in hand and serialized ids only |
  stamp it on `--write-baseline` from the producing scan (done).
- read blindness | neither consumer compared the live version to the baseline's |
  compare on read and surface a skew WARNING; in-process skew tests lock it (done).
- guard placement | the only version-aware check (delta guard) fires on write, not
  on the blocking read | the read-time warn now fires where the false-block lands.

## Sibling Search

Mental-model: "checked-in derived/cached surface whose validity silently depends on a
producer-tool version it does not record." Repo-wide scan of derived surfaces:

- same layer: `doc-nose-baseline.json` (doc `path#heading` signatures) | decision:
  same class, lower stakes, DEFERRED | proof: local scan — advisory-only,
  position-independent signatures, already floor-guarded at `nose >= 0.13.0`; its
  stamp is a deferred same-class sibling, recorded in `references/dup-ratchet.md`.
- safe sibling: `scripts/boundary-bypass-baseline.json` | decision: no gap (the
  pattern to mirror) | proof: records `inventory_schemaVersion` and actively flags
  `schema_mismatch` — pins its producer contract.
- safe sibling: `charness-artifacts/quality/sloc-inventory/latest.json` | decision:
  no gap | proof: stamps `tokei_version` AND is a fresh full inventory (no stored
  keys to go stale).
- safe sibling: Cosmic Ray mutation session | decision: no gap | proof: regenerated
  wholesale each run (`baseline`+`init`), not a checked-in accepted-id set.
- cross-file: skills/public/quality/scripts/dup_ratchet_lib.py

## Seam Risk

- Interrupt ID: nose-baseline-tool-version-stamp
- Risk Class: operator-visible-recovery
- Seam: nose scanner version (id algorithm) -> unrecorded in id-set baseline -> stale-id false hard-block with no skew signal
- Disproving Observation: a baseline stamped 0.13.0 against a 0.14.0 scan still hard-blocks but now names the skew and prescribes re-baseline (test green); a legacy unstamped baseline does not false-warn.
- What Local Reasoning Cannot Prove: whether a future nose version will keep `--version` parseable by `_VERSION_RE`, or change the id algorithm without changing the version string.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Both code id-set baselines stamp the producing nose `tool_version` (from the same
scan that minted the ids, never a fresh probe); the gate and advisory compare it
against the live version and surface a skew WARNING that explains a block rather than
suppressing one. A missing stamp is treated as "unknown" (no false warning on legacy
baselines). The field is additive — no `schemaVersion` bump — so existing unstamped
baselines still validate and degrade-repo-wide is avoided. `references/dup-ratchet.md`
documents the skew-detection behavior and records the doc-signature baseline as a
deferred same-class sibling.

## Related Prior Incidents

- #395 (dup-ratchet `family_id` rotation): same two baselines, the offset/path-folding
  half of "family_id is scanner-version- AND edit-scoped"; this slice adds the
  version-axis detection that #395's re-baseline discipline assumed but never enforced.
- nose 0.14.0 compat pass: re-seeded both id-sets for the scanner bump by hand — the
  exact maintenance this stamp now makes self-detecting.
