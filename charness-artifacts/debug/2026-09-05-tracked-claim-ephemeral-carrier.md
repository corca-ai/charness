# Debug Review: tracked claim, ephemeral carrier
Date: 2026-09-05

## Problem

A tracked `worker-delivered` critique cites a gitignored `.charness/reviewer-round-*/worker-report.yaml`. Local `--all` is green; a clean clone (CI mutation sampler) is red.

## Correct Behavior

Given a tracked artifact that claims `worker-delivered`, when a clean checkout validates it, then the named carrier is itself a tracked, non-hidden path under `charness-artifacts/`, and a gitignored runtime path is refused on the author machine too.

## Observed Facts

- Claim type: absence on CI. Cheapest falsifier: `--all` locally vs after hiding the carrier. Local carrier present; `.gitignore:44` ignores `.charness/reviewer-round-*/`. Result: confirmed class (exist-on-this-disk ≠ portable).
- Two tracked worker-delivered records: `charness-artifacts/critique/2026-09-04-impl-debug-route.md:115` and `...-8-3-0-critique.md:190`.
- `_report_path` (`skills/shared/scripts/reviewer_worker_carrier_support.py:126`) checks `is_file()` only.
- Runtime dir is `.charness/reviewer-round-{attempt}` (`run_review_support.py:294-295`). Durable copies already live under `charness-artifacts/critique/workers/` (2026-08-24/25/30).
- Live corpus (`test_critique_fresh_eye_presence.py:357`) assumes every tracked critique validates on a clean tree.
- Sibling same session: #797 `keep_worktree` vs sweep. Prior: `2026-09-05-worktree-only-candidate-deleted.md`.

## Reproduction

- Cite `.charness/reviewer-round-x/worker-report.yaml` from a tracked worker-delivered artifact; file present locally → validator 0; file absent → 1 with “does not exist inside the repository”.

## Candidate Causes

- CI missing an unrelated pytest (disconfirmed: nodeid is the live-corpus critique test).
- Worker never wrote a report (disconfirmed: hashes join locally).
- Validator equates local existence with a durable carrier (confirmed).

## Hypothesis

- If `_report_path` refuses a `.charness` / `.artifacts` carrier, authoring fails before commit. If `run_review` copies `worker-report.yaml` under `charness-artifacts/critique/workers/<attempt>/`, the parent has a citeable tracked path. | disconfirmer: a fixture with a present gitignored report must now fail.

## Verification

- confirmed — `_report_path:126`; gitignore; two 2026-09-04 cites; workers/ corpus of durable copies.

## Root Cause

Five Whys: sampler UNMEASURED → live-corpus `--all` red → worker-delivered needs a file CI lacks → cite is `.charness/reviewer-round-*` (gitignored 2026-08-21, f7a09d672) → `_report_path` treats “exists here” as “durable” and `run_review` never promotes the report. Bottom: missing invariant that a tracked on-disk proof must itself be tracked/visible, not hidden runtime (`docs/artifact-policy.md` Variable Hidden vs Variable Visible). Not “the author picked the wrong path.”

## Invariant Proof

- Invariant: when a tracked producer emits `worker-delivered` naming a carrier path, a clean-clone consumer must open that path and join hashes; hidden runtime is not that path.
- Producer Proof: `run_review_support.py:294` writes the round dir; 8.3.0 artifacts copy `paths.report`.
- Final-Consumer Proof: CI `--all`; local `--all` is the lying consumer.
- Interface-Shape Sibling Scan: keep_worktree/#797; salvage unreferenced; Worker report lines under accepted-unreviewed.
- Non-Claims: mutation budget after sampler greens; whether every historical `.charness` cite is worker-delivered (three accepted-unreviewed are not).

## Detection Gap

- `_report_path` exist-only | did not fire on author disk | refuse hidden-runtime prefix.
- live-corpus `--all` | fires only on CI | keep strict; do not skip missing carriers.
- Over-reach: the exist check is the gap, not “no test in this corner.”

## Sibling Search

- Mental model: a durable record may name ephemeral local bytes as the only copy; the local consumer sees them, a later consumer does not.
- same layer: `_report_path` exist-only | `same bug, fix now` | local payload proof
- same layer: `new_run_dir` writes only `.charness` | `same bug, fix now` | static scan + 8.3.0 cites
- abstraction up: #797 keep_worktree vs sweep | `same class, diagnostic-only for this slice` | local payload proof — 797 already has its own fix in this worktree
- specialization down: three `.charness` Worker report lines under `accepted-unreviewed` | `intentional plain-text or non-rendering boundary` | static scan — validator does not bind those claims
- mental-model: salvage files beside result.json unnamed | `same class, diagnostic-only for this slice` | executable fixture in #797
- cross-file: `scripts/task_run/task_run_completion.py` keep_worktree vs `skills/shared/scripts/reviewer_worker_carrier_support.py` exist-only

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: author disk vs clean clone
- Disproving Observation: local `--all` green, CI red
- What Local Reasoning Cannot Prove: hosted mutation after sampler greens
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-09-05-tracked-claim-ephemeral-carrier.md

## Prevention

Refuse hidden-runtime worker-delivered paths. Promote `worker-report.yaml` to `charness-artifacts/critique/workers/<attempt>/`. Retarget the two 2026-09-04 records. Leave `--all` strict.
