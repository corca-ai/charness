# Achieve Goal: Harden the dup-ratchet gate (scope_paths-empty warning, --write-baseline delta/confirm guardrail, validate_gate_baseline wired into a run-quality/validate phase), then add in-process coverage for check_dup_ratchet.py, and land both with the rest of the unpushed stack in a single push so consumer repos first see the hardened gate.

Status: draft
Created: 2026-06-19
Activation: `/goal @charness-artifacts/goals/2026-06-19-issue-393-harden-the-dup-ratchet-gate-scope-paths-empty-warning-write.md`
Discuss before activation: RESOLVED. Consequential decisions surfaced and settled with the operator during shaping (see Interview Decisions): (1) irreversible side effects + live proof + broad bundle scope — this goal crosses two external/irreversible boundaries, a push to `origin/main` and a release publish; operator APPROVED the push-through-release path, with push at the slice-3 bundle boundary under explicit per-instance approval (NOT auto-on-green) and the release via the `release` skill verified on a different evidence channel (install/update fetches the hardened gate; CI green on the pushed SHA), per the north-star irreversible-boundary rule. (2) issue close/split — none in scope: #393 is a coverage-attribution class (not closed by this goal) and the open issues #391/#387/#392/#371 are explicitly out-of-scope chunk-4. Never auto-push or auto-publish without the operator's go at each boundary.

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slices 1+2+3 DONE (pushed to origin/main `e97a2884`, CI Quality Core green on that SHA); Slice 4 (release) in progress.
- Current disposition: ACTIVE — operator activated and pre-approved push+release ("푸시 릴리즈도 사전 승인"). Release (slice 4) gates on the release skill flow + north-star post-release different-channel verification.
- Next action: Slice 4 — release via the `release` skill (version bump + install manifest + operator update); then post-release different-observer verification (install/update fetches the hardened gate; CI green on the release SHA).
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
| 1 | dup-ratchet hardening: F (scope_paths-empty advisory warn) + C (`--write-baseline` warn + named-flag confirm on large delta, never hard-fail) + I (fold `validate_gate_baseline` advisory into the existing `check_dup_ratchet` evaluate path / `dup-ratchet` phase via `degraded_reasons` — no new phase) | onboarding correctness + surface the silent-disarm risk (advisory; promote to a block only on recorded recurrence) before the gate spreads to consumer repos (priming) | unit tests for F/C/I green; misconfig fixture shows warn+degrade (behavior, not literal ids); `dup-ratchet` phase prints the advisory; no new blocking floor; mirror synced | **DONE** — 4 in-process F/C/I tests + 2233 quality_gates green; mirrors synced; live gate re-baselined (2-id churn, delta 4 < 50 dogfooded C's small-delta path) |
| 2 | in-process coverage for `check_dup_ratchet.py` (the #393 subprocess-only-attribution class) | the only stated blocker to pushing the stack; the scheduled mutation run will otherwise flag 0% attributed | **DONE** — in-process attribution 0%→86% (CLI was subprocess-only); 40 focused tests green; the ~25 remaining lines are real-nose/doc-subprocess/git/`__main__` paths covered by the live gate + nose-gated + git-seam tests; none are changed lines | planned |
| 3 | bundle proof + push | both slices landed; convert built→shipped | **DONE** — run-quality 77/0 (dup-ratchet PASS); plugin-import-smoke + packaging-committed green; fresh-eye critique push-safe (no blockers); pushed `90bab0de..e97a2884`; pre-push hook re-ran 77/0; CI Quality Core success on `e97a2884` (different channel) | planned |
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

### Slice 1: Slice 1 — dup-ratchet F/C/I hardening

- Objective: Land the three slice-2 critique deferrals advisory/non-blocking: F (enabled + empty scope_paths -> whole-gate advisory degrade, never a false block or silent pass), C (--write-baseline refuses a large family_id delta without --confirm-baseline-delta; never touches the gate evaluate path), I (fold dup_ratchet_lib.validate_gate_baseline into the existing check_dup_ratchet evaluate path, surfaced via degraded_reasons through the existing dup-ratchet phase — no new phase).
- Why this approach: B1 fix: there is no generic validate phase, so I reused the existing evaluate path + dup-ratchet phase, which also keeps I honestly advisory. C is the maintenance command refusing a silent overwrite (exit-1 to signal refusal), never a gate hard-fail — the never-hard-fail constraint is about the evaluate path. F degrades the whole gate (FD8) so a misconfigured scan cannot read as clean.
- Commits:
- What changed: skills/public/quality/scripts/check_dup_ratchet.py (F in _evaluate_config; I integrity fold; C guardrail + DEFAULT_BASELINE_DELTA_THRESHOLD const + --confirm-baseline-delta/--baseline-delta-threshold flags; docstring); references/dup-ratchet.md (degraded ladder + adoption + review Q); adapter.example.yaml (scope_paths note); tests/quality_gates/test_dup_ratchet.py (in-process loader + 4 F/C/I tests; _consumer_repo scope_paths param); plugin mirrors (sync_root_plugin_manifests.py); charness-artifacts/quality/dup-ratchet-baseline.json (2-id rotation re-baseline).
- Alternatives rejected: Refactor the flagged clones (rejected: the 2 new families are unchanged pre-existing patterns — the if-None idiom and the standalone-CLI main() boilerplate — re-hashed by editing the file, not new duplication; extracting main() contradicts the portable standalone-gate-script design). Classify intentional in dup-review.json (rejected: family_id churns on every edit, so an id-keyed overlay entry is not durable). New blocking floor for F/I (rejected: Floor-Addition Restraint — advisory first).
- Targeted verification: 4 new in-process tests green; full tests/quality_gates 2233 passed (209s); live gate clean after re-baseline (status=clean, 0 new, no degrade); mirror parity diff clean; baseline diff is exactly 2 removed + 2 added.
- Test duplication pressure: 4 new tests share _consumer_repo/_run_inproc/_code_inventory/_doc_inventory helpers (no setup copy-paste); each asserts a distinct behavior (F degrade, I integrity, C-refuse, C-confirm). In-process tests deliberately complement the subprocess SC5 tests (process contract: argv/exit/stdout) rather than duplicate them (branch attribution + new F/C/I logic). Low duplication pressure; tests/ is outside the dup-ratchet scope_paths so the gate does not self-flag them.
- Critique: Deferred to the Slice 3 bundle boundary per the shaped plan (one bounded fresh-eye critique covering slices 1+2 before the irreversible push).
- Off-goal findings: family_id churn: editing a scanned member file rotates the family_ids of clusters that include it (here 2 ids rotated from an unchanged file), forcing a re-baseline even with no new duplication. The reference claims content-hash id is stable across sibling churn but same-file edits still rotate. Candidate retro/issue finding; advisory, out of this slice's scope (Floor-Addition Restraint).
- Lessons carried forward: Re-baseline is legitimate here (reviewed: no new fixable duplication), and the small delta (4) dogfooded that C's guardrail does not obstruct a legitimate small re-baseline.
- Metrics:

### Slice 2: Slice 2 — in-process coverage for check_dup_ratchet.py (#393)

- Objective: Close the #393 subprocess-only-attribution class for check_dup_ratchet.py: the slice-2 CLI was only ever driven via run_script subprocess (0% attributed), which the scheduled mutation run would flag. Drive the CLI in-process so its run()/main()/evaluate/write-baseline branches attribute coverage.
- Why this approach: Slice 1's 4 F/C/I in-process tests already lifted attribution 0%->73%; Slice 2 adds main() (json+text, exit codes), run() inert + adapter-invalid, write-baseline-failed, the _families_from_text error branches, and the overlay/baseline-missing + doc-status degrade branches -> 86%. Remaining ~25 lines are real-nose-scan / doc-inventory-subprocess / git-stagnation / __main__ paths that need real tools; they are exercised by the live gate run, the nose-gated subprocess test, and the SC4 git-seam fixture. In-process tests complement (not duplicate) the subprocess SC5 tests, which still own the real process contract (argv, exit code, stdout).
- Commits:
- What changed: tests/quality_gates/test_dup_ratchet.py: in-process check_dup_ratchet loader (_load + _run_inproc) and 7 in-process branch tests (main json-inert/text-hard-block, run adapter-invalid, write-baseline-failed, _families_from_text bad inputs, missing overlay+baseline degrade, doc-status degrade).
- Alternatives rejected: Mock nose/git to attribute the real-tool paths in-process (rejected: adds harness complexity + near-duplication of the live/nose-gated coverage for marginal attribution; the integration paths are genuinely exercised by the live gate). Replace the subprocess SC5 tests with in-process equivalents (rejected: SC5 is the documented acceptance fixture and owns the real CLI process contract).
- Targeted verification: 40 focused tests green (was 33 after slice 1); coverage --include check_dup_ratchet.py reports 86% in-process (0% before any in-process driving); missing lines confirmed to be real-tool/entry-guard, none of them changed lines.
- Test duplication pressure: 7 new tests reuse _consumer_repo/_run_inproc/_code_inventory/_doc_inventory; each asserts a distinct branch (inert, adapter-invalid, hard-block exit, write-baseline-failed, parse helpers, degrade ladders). No setup copy-paste; tests/ is outside dup-ratchet scope_paths so the gate does not self-flag. Low pressure.
- Critique: Deferred to the Slice 3 bundle boundary (one bounded fresh-eye critique covering slices 1+2).
- Off-goal findings:
- Lessons carried forward: 0%-attribution from subprocess-only CLI testing is closed by adding a thin in-process driver alongside the subprocess contract tests; the real-tool branches stay subprocess/live-gated rather than mocked.
- Metrics:

### Slice 3: Slice 3 — bundle proof + operator-approved push

- Objective: Convert the built slices (1+2) plus the rest of the unpushed stack into shipped state: full quality proof, an independent fresh-eye review, packaging proof, then the operator-approved push to origin/main, with a different-channel CI verification per the north-star irreversible-boundary rule.
- Why this approach: Operator pre-approved push at activation ('푸시 릴리즈도 사전 승인'); still gated push on green bundle proof + an independent observer (fresh-eye critique) + a different evidence channel (remote CI on the pushed SHA), never a local terminal green alone.
- Commits:
- What changed: No code changes in this slice — proof + push only. Pushed 9-commit stack 90bab0de..e97a2884 (the nose-migration stack, find-skills refresh, handoff, goal shaping, and slices 1+2).
- Alternatives rejected:
- Targeted verification: run-quality.sh --read-only: 77 passed / 0 failed (dup-ratchet phase PASS), tree clean; check_plugin_import_smoke.py green (every plugins/charness module imports); validate_packaging_committed.py green; bounded fresh-eye subagent critique returned VERDICT=push-safe with no blockers (independently verified F/I cannot block, C never touches the evaluate path, no new phase/floor, mirror byte-identical, and the 2-id re-baseline honest by inspecting members byte-identical base-vs-HEAD). Pre-push hook re-ran run-quality 77/0. Post-push: CI Quality Core run 27825608075 on e97a2884 = success (Core deterministic gates success; PR-mirror job skipped on direct push).
- Test duplication pressure:
- Critique: Bounded fresh-eye subagent (different agent context, read-only in the shared parent worktree per fresh-eye-subagent-review.md). One should-fix: the dup_ratchet_lib docstring's family_id-stability claim is narrower than reality (same-file edits also rotate ids) — pre-existing, already logged as the slice-1 off-goal finding, correctly deferred under Floor-Addition Restraint.
- Off-goal findings: Scheduled 'Mutation Tests' workflow failed at 01:34 on an OLDER SHA (pre-push) — the exact #393 0%-attribution class Slice 2 addresses. It is schedule-triggered, not push-triggered, so it did not re-run on e97a2884; the next scheduled run should benefit from the 86% in-process attribution. Candidate to confirm at the next scheduled mutation cycle.
- Lessons carried forward: North-star push verification satisfied with three independent signals: fresh-eye observer + packaging channel + remote CI on the pushed SHA — not a single local terminal green.
- Metrics:

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
