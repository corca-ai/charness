# Achieve Goal: Harden the dup-ratchet gate (scope_paths-empty warning, --write-baseline delta/confirm guardrail, validate_gate_baseline wired into a run-quality/validate phase), then add in-process coverage for check_dup_ratchet.py, and land both with the rest of the unpushed stack in a single push so consumer repos first see the hardened gate.

Status: draft
Created: 2026-06-19
Activation: `/goal @charness-artifacts/goals/2026-06-19-issue-393-harden-the-dup-ratchet-gate-scope-paths-empty-warning-write.md`
Discuss before activation: RESOLVED. Consequential decisions surfaced and settled with the operator during shaping (see Interview Decisions): (1) irreversible side effects + live proof + broad bundle scope — this goal crosses two external/irreversible boundaries, a push to `origin/main` and a release publish; operator APPROVED the push-through-release path, with push at the slice-3 bundle boundary under explicit per-instance approval (NOT auto-on-green) and the release via the `release` skill verified on a different evidence channel (install/update fetches the hardened gate; CI green on the pushed SHA), per the north-star irreversible-boundary rule. (2) issue close/split — none in scope: #393 is a coverage-attribution class (not closed by this goal) and the open issues #391/#387/#392/#371 are explicitly out-of-scope chunk-4. Never auto-push or auto-publish without the operator's go at each boundary.

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: shaped draft awaiting activation.
- Current disposition: real draft/backlog awaiting activation — shaped this session (4 interview decisions folded). Reshape before activating only if the dup-ratchet hardening scope (F/C/I) or the push→release external boundary changed.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-19-issue-393-harden-the-dup-ratchet-gate-scope-paths-empty-warning-write.md` after confirming the push→release approval still holds.
- Verification cadence: cheap deterministic checks (targeted unit tests, pre-commit hooks) at commit boundaries; `run-quality.sh --read-only` focused phases + the in-repo misconfig fixture + a bounded fresh-eye critique at slice boundaries; full run-quality + packaging/managed-install + operator-approved push + post-release different-observer verification at the bundle/closeout boundary.
- Slice review packet: intent (advisory-only gate hardening + test coverage, no new content floor); changed files (`check_dup_ratchet.py`, dup_ratchet policy lib, run-quality/validate wiring, `references/dup-ratchet.md`, `adapter.example.yaml`, dup-ratchet tests, release surface); expected invariants (F/I are advisory non-blocking; no false-block; baseline-integrity warning only); tests/proof; non-claims; out-of-scope (chunk-2/4/5); reviewer questions.
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

Harden the dup-ratchet gate so consumer repos first see a hardened, self-checking version: add the F (scope_paths-empty warning, advisory — surfaces the silent-`DEFAULT_PATHS`-fallback risk, does not block), C (`--write-baseline` warn + named-flag confirm on large delta, never a hard-fail), and I (fold `validate_gate_baseline` advisory into the existing `check_dup_ratchet` evaluate path, surfaced via `degraded_reasons` in the existing `dup-ratchet` run-quality phase — no new phase) critique deferrals; add in-process coverage for `check_dup_ratchet.py`; then land both with the rest of the unpushed stack in a single operator-approved push and cut a release so the hardened gate is the version external repos receive.

**Source handoff entry #3: dup-ratchet hardening slice**

> (slice-2 critique deferrals): `--write-baseline`
>   delta/confirm guardrail; wire `validate_gate_baseline` into a run-quality/validate
>   phase; warn when `enabled` but `scope_paths` empty. See spec `### Slice 2 Critique`.

---

**Source handoff entry #1: Before pushing the unpushed stack:**

> add in-process coverage for
>   `check_dup_ratchet.py` (the slice-2 CLI is subprocess-tested → 0% *attributed*,
>   the #393 class). It is a TEST addition; the changed-line gate skips non-blocking
>   today, but the scheduled mutation run will flag it. Then decide on push.

## Non-Goals

- Not adding any new blocking content floor — F and I land advisory/non-blocking (Floor-Addition Restraint; promote to a floor only on recorded recurrence).
- Not doing chunk-2 (changed-line gate `--reuse-coverage` graceful-degrade), chunk-4 (the remaining-tracks basket), or chunk-5 (external-repo dry-run); those stay separate tracks.
- Not changing the dup-ratchet content thresholds or the boy-scout escalation arm's inert-at-ceiling-0 posture.
- Not closing #393 (it is a coverage-attribution *class*, not an open tracked issue) or any of the open issues #391/#387/#392/#371.

## Boundaries

- In scope (confirm exact paths on first discovery): `skills/public/quality/scripts/check_dup_ratchet.py` and its policy lib (`dup_ratchet_lib.py`); the I wiring — fold `validate_gate_baseline` into the existing `check_dup_ratchet` evaluate path, surfaced as a `degraded_reasons` advisory through the **existing** `dup-ratchet` run-quality phase (there is no generic "validate" phase — do not invent one); `skills/public/quality/references/dup-ratchet.md`; `adapter.example.yaml`; the dup-ratchet test surface; and the release surface (plugin version + generated install manifest + operator update doc) via the `release` skill.
- Mirror obligation (mutate→sync→verify barrier): the dup-ratchet scripts and `quality_dup_ratchet_policy.py` are mirrored under `plugins/charness/...`; run `sync_root_plugin_manifests.py` before validators/critique/commit at each slice. A late edit missing the sync was a slice-2/3 BLOCKER twice (recent-lessons) — treat it as load-bearing, not optional.
- C scoping: C **warns and requires an explicit named flag** (e.g. `--confirm-baseline-delta`/`--force`) only past a large-delta threshold, and never hard-fails; a deliberate nose-version re-baseline (e.g. slice-3's 571→487 id swing) is the legitimate large-delta case the message must accommodate, not obstruct.
- Point-in-time values: baseline id counts and the nose version floor (`>=0.13.3`) are version-scoped and rot; do not assert a specific count in tests or the misconfig fixture — assert behavior (warn emitted, FD8 whole-gate degrade, never a false block, never a silent clean pass).
- Portable per implementation-discipline: F/C/I stay adapter-driven; no host-specific assumption.
- External boundaries: push to `origin/main` (bundle-approval) and release publish (irreversible — different-observer/different-channel verification per north-star).
- Stop conditions: name exact paths on first discovery, do not guess; stop and re-discuss if any hardening item turns out to require a new content floor; stop at the push and release boundaries for explicit operator approval.

## User Acceptance

What the user can do to verify completion directly:

- Set `dup_ratchet.enabled: true` with empty `scope_paths` in a config and run the gate → see the **F** warning surfaced (not a silent fall-through to nose `DEFAULT_PATHS`).
- Run `--write-baseline` that would shift the committed baseline by a large delta → see the **C** guardrail warn and refuse without the named confirm flag, instead of a silent overwrite; supplying the flag (a deliberate version re-baseline) still succeeds.
- Point `run-quality` at a malformed/corrupt dup-ratchet baseline → see the **I** advisory warning (non-blocking) that the hard arm is at risk; run-quality still passes.
- Confirm `check_dup_ratchet.py` now shows attributed in-process coverage (the #393 subprocess-only-attribution class is closed for this file).
- After release: install/update charness and confirm the hardened gate is the version consumers receive; CI is green on the pushed SHA.

## Agent Verification Plan

### Low-Cost Checks

- Targeted unit tests for F, C, and I, plus the new in-process `check_dup_ratchet.py` coverage test.
- `sync_root_plugin_manifests.py` run before validators/critique/commit at each slice (mutate→sync→verify); the dup-ratchet scripts + `quality_dup_ratchet_policy.py` mirror under `plugins/charness/...`.
- Pre-commit hooks (staged-reversion, doc-links, markdown, title-slug, skill-ergonomics).
- Cautilus stays eval-only/ask-before-run: consult `python3 scripts/run_cautilus_proof.py --repo-root . --json` only if a named failing-log path exists; otherwise do not invoke.

### High-Confidence Checks

- `run-quality.sh --read-only` focused phases (dup-ratchet + the new validate phase) green.
- In-repo misconfig fixture proving the F warning + FD8 whole-gate degrade (never a false block, never a silent clean pass).
- Changed-line coverage now attributes `check_dup_ratchet.py`.
- Bounded fresh-eye slice critique (different agent context) before lock.

### External Or Live Proof

- Full `run-quality.sh` green at the bundle boundary; packaging + managed-install green.
- Operator-approved push to `origin/main` (bundle-boundary, not auto-on-green).
- Release via the `release` skill: plugin version bump + generated install manifest + operator update instructions.
- Post-release verification on a different evidence channel: install/update fetches the hardened gate; CI green on the pushed SHA. Never substitute a terminal green for this.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | dup-ratchet hardening: F (scope_paths-empty advisory warn) + C (`--write-baseline` warn + named-flag confirm on large delta, never hard-fail) + I (fold `validate_gate_baseline` advisory into the existing `check_dup_ratchet` evaluate path / `dup-ratchet` phase via `degraded_reasons` — no new phase) | onboarding correctness + surface the silent-disarm risk (advisory; promote to a block only on recorded recurrence) before the gate spreads to consumer repos (priming) | unit tests for F/C/I green; misconfig fixture shows warn+degrade (behavior, not literal ids); `dup-ratchet` phase prints the advisory; no new blocking floor; mirror synced | planned |
| 2 | in-process coverage for `check_dup_ratchet.py` (the #393 subprocess-only-attribution class) | the only stated blocker to pushing the stack; the scheduled mutation run will otherwise flag 0% attributed | changed-line/mutation coverage attributes `check_dup_ratchet.py`; focused tests green | planned |
| 3 | bundle proof + push | both slices landed; convert built→shipped | full run-quality + packaging/managed-install green; fresh-eye critique; operator-approved push to `origin/main` | planned |
| 4 | release | consumer repos first see the hardened gate (priming terminal state) | release skill: version bump + install manifest + operator update; post-release different-observer verification; CI green on pushed SHA | planned |

## Operator Decision Queue

- Decision: approve the push to `origin/main` at the slice-3 bundle boundary.
  - Owner: operator
  - Why deferred: slices 1–2 and local proof proceed safely first.
  - Unblock action: explicit "push" approval after slice-3 bundle proof passes.
  - Revisit trigger: slice-3 bundle boundary reached with green proof.
- Decision: approve the release publish (and confirm the version number).
  - Owner: operator / maintainer
  - Why deferred: release follows a green push.
  - Unblock action: approve the release cut + version bump.
  - Revisit trigger: slice-4 after a green push.

## Coordination Cues

- Phase routing defers to `find-skills` (no inline phase→skill map baked here).
- Expected closeout floors: `Release:` triggered (release skill, slice 4); `Routing:` triggered (impl/quality/critique/release phases recorded); `Gather:` n/a — no external sources consumed; `Issue closeout:` n/a — #393 is a coverage-attribution class, not an open tracked issue, and the open issues #391/#387/#392/#371 are out-of-scope chunk-4.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Source: handoff entry #3 (dup-ratchet hardening slice) — see [docs/handoff.md](../../docs/handoff.md).
- Source: handoff entry #1 (Before pushing the unpushed stack:) — see [docs/handoff.md](../../docs/handoff.md).
- Spec `### Slice 2 Critique` (defines C/I/F precisely) — see [charness-artifacts/spec/boy-scout-dup-ratchet.md](../spec/boy-scout-dup-ratchet.md).
- Dup-ratchet reference — see [skills/public/quality/references/dup-ratchet.md](../../skills/public/quality/references/dup-ratchet.md).
- Recent lessons (Floor-Addition Restraint, the #393 coverage follow-up, the --reuse-coverage degrade) — see [charness-artifacts/retro/recent-lessons.md](../retro/recent-lessons.md).
- Nose-migration + self-diagnosis retro — see [charness-artifacts/retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md](../retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md).
- Cited class: #393 (subprocess-only coverage attribution).

## Interview Decisions

- **Push scope.** Family: {push-ready + bundle approval, auto-push on green, defer push out of goal}. Chosen: push-ready + per-instance bundle approval, extended through a release. Rejected: auto-push-on-green (no per-instance approval at an irreversible boundary, violates north-star); defer-out-of-goal (operator wants the goal to carry through push and release — "1 이후 푸시 릴리즈까지").
- **External dry-run / verification scope.** Family: {in-repo + misconfig fixture, fold external-repo dry-run into verification}. Chosen: in-repo verification + a synthetic misconfig fixture for the F warning. Rejected: folding chunk-5's external-repo dry-run in (keeps the goal bounded, respects the 3→1 selection; chunk-5 becomes a separate follow-up goal).
- **validate_gate_baseline posture.** Family: {advisory warn (non-blocking), block on integrity failure only, defer I}. Chosen: advisory warn, non-blocking. Rejected: block-on-integrity (Floor-Addition Restraint — advisory first, promote on recorded recurrence); defer-I (the silent-disarm risk is worth an advisory signal now, cheaply).
- **Timebox.** Family: {none / open-ended, set a fixed budget}. Chosen: no timebox (slice-paced). Rejected: a timebox (no fixed work budget was given; timebox fields intentionally omitted).

## Plan Critique Findings

Bounded fresh-eye plan critique (separate agent context, read-only; 5 angles + counterweight). Verdict: **pursue-ready after fixes** — all corrections were artifact wording/scope, no plan reversal.

Blockers folded:

- **B1 — "validate phase" did not exist.** `validate_gate_baseline` is defined+tested in `dup_ratchet_lib.py` but called by nothing; `run-quality.sh` has no generic "validate" phase. Folded: I now reuses the existing `check_dup_ratchet` evaluate path + `dup-ratchet` run-quality phase via `degraded_reasons` (Goal, Boundaries, Slice 1) — which also keeps it honestly advisory.
- **B2 — plugin-mirror sync was missing from scope.** The dup-ratchet scripts + `quality_dup_ratchet_policy.py` mirror under `plugins/charness/...`; a missed sync was a slice-2/3 BLOCKER twice. Folded: mirror obligation added to Boundaries + Low-Cost Checks (mutate→sync→verify).

Should-fix folded:

- **C guardrail could block a legitimate re-baseline.** Pinned to warn + named-flag confirm past a large-delta threshold, never hard-fail; the slice-3 571→487 version re-baseline named as the legitimate large-delta case (Goal, Boundaries, User Acceptance).
- **Over-literalization.** Added the point-in-time note (id counts + nose floor rot; fixture asserts behavior, not literal ids) to Boundaries + Slice 1.
- **F oversold "close the silent-disarm risk."** Softened to "surface (advisory); promote to block only on recorded recurrence" (Goal, Slice 1) — matching Interview Decision 3.

Over-worry raised, not folded (recorded so they are not relitigated):

- Slice 1 / slice 2 are genuinely independent — 3→1 ordering is a mild efficiency, not a dependency.
- The push→release north-star handling (different observer + different evidence channel, no terminal-green substitute) is adequate; naming the exact install/update readback command is execution-time detail.
- In-process coverage attributing the CLI is mechanically achievable (the test file already loads the lib in-process via `importlib`).

Reviewer provenance: general-purpose fresh-eye subagent, bounded plan-critique packet, ran read-only against the artifact + spec Slice 2 Critique + dup-ratchet reference + recent-lessons + `check_dup_ratchet.py` + north-star.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro
