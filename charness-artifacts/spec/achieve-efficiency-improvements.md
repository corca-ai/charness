# Spec: Achieve Efficiency Improvements (close the waste-pattern loop)

Source: 2026-06-13 operator discussion of `achieve` waste observed running in
`../ceal`; cross-read of the ceal retro corpus
(`ceal/charness-artifacts/retro/`) and this repo's retro corpus
(`charness-artifacts/retro/`); closed issues
[#356](https://github.com/corca-ai/charness/issues/356) /
[#357](https://github.com/corca-ai/charness/issues/357) (prose-only resolution
that did not stick).

Baseline docs:
- [skills/public/achieve/references/lifecycle.md](../../skills/public/achieve/references/lifecycle.md)
- [skills/shared/references/meaningful-slice-cadence.md](../../skills/shared/references/meaningful-slice-cadence.md)
- [skills/public/retro/references/phase-aware-efficiency.md](../../skills/public/retro/references/phase-aware-efficiency.md)
- [skills/public/retro/references/section-guide.md](../../skills/public/retro/references/section-guide.md)
- [skills/public/critique/references/cadence.md](../../skills/public/critique/references/cadence.md)

## Problem

Operating `achieve` in consumer repos (notably ceal) produced recurring waste the
operator named in three buckets, plus a version-skew context finding. They are
three symptoms of **one meta-pattern**: the system's reflex to every observed
waste is "add one more deterministic floor (teeth)." That reflex is asymmetric —
it over-applies teeth where they create churn, and under-applies them where prose
silently decays.

1. **Validator post-hoc churn (named #1).** Closeout/issue-verify validators
   reject the artifact because a required field/form was not known up front; the
   agent then discovers the shape by *failing the gate and fixing one rejection
   at a time*. Dominant repeating pattern in the ceal corpus (7 retros, e.g.
   `2026-06-08-identity-legacy-cleanup-disposition-review.md`:
   "read the validator output and template/parser contract before editing
   instead of inferring the missing shape from repeated trial runs";
   `2026-06-03-closeout-apply-handoff-hardening-waste-retro.md`: "run complete-goal
   validation before any final push"). The irony: `lifecycle.md:304-313` already
   teaches the *aggregate, don't fix-one-at-a-time* principle for **commit**
   gates, but `achieve` never applies it to its **own** closeout-evidence gate.
   Root cause (verified): `describe_goal_closeout_shape.py` /
   `scripts/check_artifact_surface_preflight.py` — tooling built *precisely* for
   "closeout-evidence forms an author otherwise discovers by failing the flip
   several times" (its own docstring) — exists but is **referenced nowhere** in
   `achieve` SKILL.md or references. The agent meets `check_goal_artifact.py`
   only as a reactive end-gate, so closeout is `draft → fail → fix → fail`, not
   `describe → fill → verify(1)`.

2. **Over-slicing → per-commit premortem (named #2).** Small/frequent commits
   where each tiny diff is treated as a slice, triggering the full per-slice
   ritual (context reload, tests, lint, fresh-eye critique, handoff refresh,
   commit closeout). ceal `2026-05-26-codex-goal-efficiency.md`: 184 commits,
   "per-slice ritual duplication", no max-commit/slice/wall budget. The contract
   *already says the right thing* (`meaningful-slice-cadence.md`: "a slice is a
   reviewable intent unit, not commit count"; critique "review unit, not every
   commit"). Root cause (verified): that rule has **no teeth** — there is no
   commit-count / min-slice / over-slice signal anywhere in `achieve` scripts,
   while almost everything else got a deterministic floor. Prose decays under
   context pressure (the exact lesson `achieve`'s own disposition loop records).
   #356/#357 were closed by commit `f9271594` "Add meaningful-slice cadence and
   quality-signal scorecard contracts" — i.e. resolved with prose only; the
   operator's continued pain is the evidence the prose did not stick. A second
   driver: the 2026-04-27 *mandatory premortem per task-completing change* rule
   collides with *critique is slice-level*; when the agent reads commit ≈
   task-completing change, mandatory premortem fires per commit.

3. **Slow-but-passing gate invisible to the waste retro (named #3).** Pre-push
   runs ~270–296s in ceal; e.g.
   `2026-06-03-instance-access-events-company-info-closeout.md` logs 296.1s in
   Evidence but never elevates it to `## Waste`. Root cause (verified, two-part):
   (a) the retro waste taxonomy splits cost into "necessary safety cost vs
   reducible waste" (framing lives in `lifecycle.md`); a *passing* gate lands in
   "necessary safety cost" and is never flagged. (b) `phase-aware-efficiency.md`
   frames pre-push/broad gates as "final-bundle proof by default", so running it
   once at the end is *correct cadence* — the retro lens only sees cadence misuse
   (too early/often), never a gate that is **slow by design**. `section-guide.md`
   `## Waste` has "slow approval loops" but no "gate baseline runtime" item. A
   slow passing gate is real code-quality debt with no home in any retro lens.
   **Critique-corrected scope (C1):** in this repo the ~296s gate is the **host
   pre-push hook** (`.githooks/pre-push` → `./scripts/run-quality.sh --read-only`),
   which runs as its **own process** and does **not** pass through
   `run_slice_closeout.py`. So the runtime data `achieve` already captures covers
   only the gates `run_slice_closeout` itself runs (broad-pytest, sync/verify),
   not the pre-push hook the operator felt. C must be honest about which timing it
   can see, and pair the retro lens with a pointer to the gate-implementation
   owner (`run-quality.sh` phase cost: coverage / jscpd), because retro prose can
   *flag* a slow gate but cannot *fix* its implementation.

4. **Meta — teeth asymmetry / memory-only dispositions (not named, but in the
   evidence).** charness retros self-report the "misleading-green" family at 4
   recurrences with "memory-only dispositions have not stopped it recurring";
   verification-lock is still memory-only. So the system both over-adds floors
   (feeding #1) and leaves real recurrences teeth-less (feeding #2/#3).

**Version-skew context (scopes the fix, not fixed here).** ceal's installed
`achieve` is an older era: `lifecycle.md` 520 lines vs 752 here; 16 scripts vs
24; missing Structural-follow-up / recurrence-lineage / Closeout-Delegation /
`describe_goal_closeout_shape`. The ceal pain occurred on a *lighter* closeout
contract. The current charness contract is *heavier*, so naive propagation would
make #1 **worse** unless A lands first. This is the central design constraint.

## Current Slice

Sequence by risk, dependency, and the critique's anti-decay correction:

- **Slice 1 = A1 + C + the advisory-module split** (low-risk wiring + the
  net-new runtime advisory surface). The advisory module is split out of
  `run_slice_closeout.py` (already near its length cap per the #332 retro) so
  both C and B build on it — this pre-empts the C7 module coupling.
- **Slice 2 = B-core**, landed **enabled by default** (not deferred behind a
  probe — see Fixed Decision B / C3 correction). Only the advisory's threshold
  is probe-tuned.
- **Slice 3 = D** (restraint rule + floor audit).

This spec is the canonical contract for all four; only Slice 1 locks now.

## Fixed Decisions

- **A1 (wire describe-first).** Add an explicit *first* step to the `achieve`
  After-phase (in `lifecycle.md` and the SKILL.md After bullet): **before
  drafting** the closeout sections (`## Auto-Retro`, `## Final Verification`,
  `## Coordination Cues` evidence), run the artifact-surface preflight for
  `--type goal-closeout` (`scripts/check_artifact_surface_preflight.py`, which
  reads `describe_goal_closeout_shape.py`) **and** a dry `check_goal_artifact.py`
  pass to get the required-line list *at once*, fill once, then verify once. Add
  the *aggregate, don't fix-one-rejection-at-a-time* principle to the closeout
  gate explicitly, mirroring the commit-gate wording already at
  `lifecycle.md:304-313`. **C4 correction:** the current preflight renders a
  *static catalog* of forms (no `--goal-path`); the dry `check_goal_artifact.py`
  pass is what supplies the *goal-conditional* missing-line set, so A1's value
  comes from running **both** at closeout start, not the static catalog alone.
- **C (gate-baseline-runtime waste lens).** Add a new waste category to
  `section-guide.md` `## Waste` and a carve-out to `phase-aware-efficiency.md`:
  a gate that **passes but is slow by design** is *gate-baseline / code-quality
  debt*, distinct from both cadence waste and "necessary safety cost". Two honest
  mechanism parts: (1) **net-new advisory code** (not free reuse — C2) that
  aggregates `run_slice_closeout.py`'s per-gate `elapsed_seconds` (line 136),
  compares to an adapter-overridable budget, and emits a non-blocking advisory
  into the **durable closeout JSON payload** (today the number only prints to
  stderr and dies); (2) the retro lens that classifies an over-budget passing
  gate as gate-baseline waste. Scope is honest: this surfaces gates **run through
  `run_slice_closeout`**; the host pre-push hook's own runtime is a separate
  capture problem (see Probe).
- **B (operational slice teeth, NOT a blocking gate).** Two operational moves,
  no new blocking floor: (1) add a `Current slice intent:` line to
  `## Active Operating Frame` naming the reviewable-intent unit and the commits
  it spans, and state that within one unchanged slice intent, critique and broad
  proof do **not** re-fire; (2) add a **non-blocking advisory** (on the split
  advisory module) that ships **enabled by default with a falsifiable detection
  rule** — *N consecutive artifact-only commits, or the Nth commit in one slice
  intent with no risk-boundary change* — and says critique re-fire is
  unnecessary. C3 correction: the advisory is **Fixed and enabled**, not a
  deferred probe; only its threshold `N` is probe-tuned, so B cannot decay into
  prose the way #356/#357 did. Resolve the premortem↔cadence collision in one
  sentence shared by `critique/references/cadence.md` and `achieve`: *premortem
  fires once per slice-intent boundary; further commits in the same intent
  re-fire only when the risk boundary moves.* Reuse #357's
  `meaningful-slice-cadence.md` definition; do not re-define it.
- **D (restraint rule + closeout-floor audit).** Add a "before adding a new
  deterministic floor" restraint checklist to
  `docs/conventions/implementation-discipline.md`: (1) does this raise
  closeout-contract weight (Problem-1 cost)? (2) is advisory/prose enough? (3)
  can an existing describe-first preflight absorb it? Prefer advisory unless
  prose has a recorded recurrence count. Produce an **audit** of existing
  closeout floors at `charness-artifacts/audit/closeout-floors.md` (C6: path
  named) listing each floor with an `absorb` / `merge` / `keep` decision — audit
  output only; no floor is removed in this spec's slices.
- **Teeth philosophy (D applied to ourselves).** Prefer advisory / operational-
  frame teeth over new blocking floors throughout this spec. The only new
  *blocking* behavior considered is rejected (see Deliberately Not Doing).
- **Portability.** All host-specific values (gate runtime budgets, which gates
  count as "broad", the advisory threshold `N`) stay adapter/preset-owned, not
  hardcoded in the skill body.

## Probe Questions

- **A2 (goal-conditional describe).** `describe_goal_closeout_shape.required_shape()`
  renders forms from constants with no `--goal-path` — a static catalog, not
  "the floors *this* goal triggers". Should A2 make the **preflight** goal-aware
  (read the goal artifact; emit only triggered floors + which are satisfied),
  folding the dry-check role into one call? Answer written back to this spec's
  Probe section and the A2 acceptance check. A1's value (one aggregated list via
  preflight + dry-check) does **not** depend on it, so A2 is a refinement, not a
  blocker.
- **C budget source / threshold.** Adapter-overridable default budget per gate;
  probe the default value against the recent goal corpus' recorded timings.
  Written back to the `achieve`/retro adapter contract.
- **C host-hook timing (raised by C1).** Capturing the host pre-push hook's own
  runtime is **out of `run_slice_closeout`'s reach** (separate process). Probe
  whether a portable capture exists (hook self-timing emitted to a known path, or
  `run-quality.sh` phase timing) or whether this stays an explicit non-claim.
  Answer written back to this spec + the C carve-out.
- **B threshold `N` only.** The advisory *fires by default*; the probe tunes the
  threshold `N` (consecutive artifact-only commits / commits-per-intent) against
  the recent goal corpus so it does not false-fire on a legitimate multi-commit
  slice. Written back to the adapter and the B acceptance test.

## Deferred Decisions

- **Cautilus improve-proof** of the prompt-surface change (eval-only per
  CLAUDE.md; consult `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
  before any `cautilus evaluate ...`). Not auto-run; left as a visible proof path.
  Reopen trigger: operator requests behavioral proof, or a failing-log path
  exists for the planner to consume.
- **ceal propagation / version-skew remediation** — a release/update concern, out
  of this spec's scope. Reopen trigger: A lands here and a ceal sync is cut.
- **Global autonomous budgets** (max wall/commit/slice) from ceal
  `2026-05-26-codex-goal-efficiency.md`. Reopen trigger: B's advisory proves
  insufficient to curb over-slicing in a real run.
- **Git-helper OSError hardening** (Slice 2 impl critique, Valid-but-Defer).
  `_recent_commit_path_lists` and the sibling `_added_vs_base` both guard only
  `returncode != 0`; a missing `git` binary would raise `FileNotFoundError`.
  Unreachable in a git-repo closeout context, and fixing one site but not the
  other would be worse (inconsistent). Reopen trigger: a gitless closeout path
  becomes real — then harden BOTH helpers with `except OSError -> []` in one
  change.
- **Float-cast guard in `evaluate_gate_runtime_budget`** (impl critique,
  Valid-but-Defer). `float(elapsed)` would raise if a future producer ever stored
  a non-numeric `elapsed_seconds`. Deliberately NOT guarded now: every current
  producer writes a float, and the counterweight noted a try/except would *mask* a
  future producer contract violation rather than surface it. Reopen trigger: a
  non-float `elapsed_seconds` producer is added.

## Non-Goals

- Re-defining "meaningful slice" — #357's `meaningful-slice-cadence.md` owns the
  definition; B only gives it operational teeth.
- Fixing ceal's installed version, or fixing the *implementation* cost of any
  consumer repo's gate (C flags, it does not optimize coverage/jscpd).
- Building a new run-loop or execution engine in `achieve`.

## Deliberately Not Doing

- **No new *blocking* closeout gate** for slice size or gate runtime. A blocking
  over-slice or runtime gate would (a) feed Problem #1's churn and (b) risk
  false-positives that train token-theater — the exact anti-pattern D names.
  Both B and C stay advisory / operational-frame.
- **Not deleting existing closeout floors** in these slices. D *audits*; removal
  is a separate, critiqued change.
- **Not making `describe_goal_closeout_shape` a hard precondition** that blocks
  the flip — it is an authoring affordance the lifecycle instructs, not a gate.
- **Not adding `Current slice intent:` to `REQUIRED_SECTIONS`** (C5). The frame
  field stays presence-surfaced and non-blocking; a goal without it must still
  pass the complete flip, guarding against a future hand silently converting the
  advisory into a blocker.

## Constraints

- `mutate → sync → verify → publish`: sync generated/plugin/export mirrors before
  validators (skill edits have `plugins/` mirrors; mirror-drift gate is hard).
- Keep existing drift/producer tests green: `test_goal_artifact_producers.py`,
  the disposition/structural-follow-up form drift pins, and `validate_skills`.
- Prompt-surface claim split: closeout **correctness** guarantees are `preserve`;
  authoring **efficiency** is `improve`. Leave the Cautilus proof path visible.
- `run_slice_closeout.py` is near its length cap (#332 retro) — Slice 1 **splits
  the advisory into its own module** before C/B append to it (C7).
- Advisory output must be non-blocking and quiet on the common case (no false
  fire on a legitimately multi-commit slice).

## Success Criteria

- **A:** A fresh agent running `achieve` closeout receives the full required-
  evidence list (static forms **plus** the goal-conditional missing-line set from
  the dry `check_goal_artifact.py` pass) *before* drafting, and the normal
  closeout path is `describe → fill → verify(1)` with **zero** "fix one gate
  rejection, re-run" rounds **on the floors the preflight + dry-check surface**.
  (The residual goal-conditional gap the *static catalog alone* cannot name is
  A2's scope and is explicitly out of this criterion.)
- **C:** A gate **run through `run_slice_closeout`** that passes but exceeds its
  budget is automatically surfaced in the durable closeout payload and is
  classifiable as gate-baseline waste in the retro — it can no longer sit
  silently in the Evidence section. The host pre-push hook's own runtime is named
  as an explicit capture non-claim (Probe), not silently implied as covered.
- **B:** An over-sliced run (N+ consecutive artifact-only commits, or many tiny
  commits inside one unchanged intent) is flagged by a non-blocking advisory that
  is **on by default**, and the `Current slice intent:` frame makes "what is a
  slice" legible at runtime so critique/broad-proof do not re-fire per commit.
  The premortem↔cadence collision has one authoritative resolution sentence.
- **D:** A maintainer adding a new floor encounters the restraint checklist; the
  closeout-floor audit exists at the named path with a per-floor decision.

## Acceptance Checks

- **A1:** `achieve` SKILL.md/lifecycle.md reference
  `check_artifact_surface_preflight.py` (`--type goal-closeout`) **and** the dry
  `check_goal_artifact.py` pass as the pre-draft closeout step (deterministic:
  grep the wiring). The aggregate principle text is present at the closeout gate.
  `validate_skills` + skill length gates pass. Negative: a fixture goal closeout
  drafted from the preflight + dry-check output passes `check_goal_artifact.py`
  on the **first** flip attempt — the fixture must include at least one
  goal-conditional floor so the test exercises the dry-check path, not only the
  static catalog.
- **A2 (if pursued):** `describe_goal_closeout_shape.py --goal-path <fixture>`
  emits only the floors that fixture triggers; unit test over a multi-floor and a
  bare fixture.
- **C:** `section-guide.md` `## Waste` lists the gate-baseline-runtime category;
  `phase-aware-efficiency.md` carves it out of "necessary safety cost". Unit test:
  the closeout payload carries a per-gate `elapsed_seconds` + budget verdict
  field (not just stderr), and a gate over budget yields a non-blocking advisory
  naming the gate + seconds; an under-budget gate emits nothing. The
  pre-push-hook-not-covered non-claim is present in the C carve-out (grep).
- **B:** `goal-artifact.md` template seeds a `Current slice intent:` line in
  `## Active Operating Frame`. The over-slice advisory fires on a synthetic
  N-consecutive-artifact-only-commits input and stays silent on a single
  legitimate multi-commit slice (unit test, both polarities). **Non-blocking
  negative test (C5):** a goal with **no** `Current slice intent:` line still
  passes `check_goal_artifact.py --status complete`. `critique/references/cadence.md`
  and `achieve` carry the single premortem↔cadence resolution sentence (grep).
- **D:** `implementation-discipline.md` carries the restraint checklist (grep);
  `charness-artifacts/audit/closeout-floors.md` exists listing each floor with an
  `absorb`/`merge`/`keep` decision.
- **Cross-cutting (bundle boundary):** full `run_slice_closeout.py
  --verification-lock` (broad gates) green; `plugins/` mirror synced; goal
  producers test green.

## Critique

Bounded fresh-eye spec critique ran before lock (target: `spec-critique.md`).

- **Execution:** parent-delegated (5 bounded subagents: 4 angle + 1 separate
  counterweight). **Fresh-Eye Satisfaction:** parent-delegated.
- **Packet Consumed:** `charness-artifacts/critique/2026-06-13-083603-packet.md`.
- **Reviewer-tier note:** `.agents/critique-adapter.yaml` requests
  `reviewer_tiers.high-leverage` = `gpt-5.5`; this host could not spawn that
  model, so reviewers ran on the default model. Recorded as a tier limitation,
  not a substituted outcome.
- **Angles:** Jackson (problem framing) · Gawande (operational/checklist) ·
  Weinberg (diagnostic/coupling) · Minto (structure/coherence) + counterweight.

**Four-bin triage (counterweight-confirmed, 0 Over-Worry):**

- **Act Before Ship — folded above:**
  - *C1* — C named "pre-push" but `run_slice_closeout` cannot see the host
    pre-push hook (separate process: `.githooks/pre-push` → `run-quality.sh`).
    Folded: C scoped to gates run through `run_slice_closeout`; host-hook timing
    moved to an explicit Probe + non-claim.
  - *C3* — B (the most painful problem) had the weakest, probe-deferred teeth.
    Folded: B's advisory is now **Fixed and enabled by default** with a
    falsifiable rule; only threshold `N` is probed; B promoted to Slice 2.
  - *C4* — SC-A "zero serial rejection" overstated vs the static catalog. Folded:
    SC-A scoped to "floors the preflight + dry-check surface"; A1 now explicitly
    runs the dry `check_goal_artifact.py` for the goal-conditional set; residual
    is A2.
- **Bundle Anyway — folded above:**
  - *C2* — C is net-new advisory code, not free reuse. Folded into the C Fixed
    Decision (durable JSON payload, honest "net-new").
  - *C5* — B drift guard. Folded: `Current slice intent:` explicitly **not** in
    `REQUIRED_SECTIONS` (Deliberately Not Doing) + a non-blocking negative test.
  - *C7* — A/B share modules near cap. Folded: Slice 1 splits the advisory module
    first.
- **Valid but Defer:** *C6* — D's audit path. Folded early (cheap): path named
  `charness-artifacts/audit/closeout-floors.md`.

**Fixed/Probe/Defer coherence after fold:** SC-A no longer over-claims past the
Fixed mechanism; B is Fixed-enabled (no Fixed-leaning-on-Defer); D's deliverable
has a path; all Deferred items name reopen triggers.

## Implementation Notes (Slice 1 folds)

Facts implementation surfaced that revise the contract (kept alive per
spec/impl discipline):

- **C7 dissolved.** The advisory module already exists
  (`scripts/slice_closeout_advisories.py`); the gate-runtime advisory was *added*
  to it, so no `run_slice_closeout.py` module split was needed. The runtime
  advisory runs **post-execution** (it needs `elapsed_seconds`), unlike the
  existing pre-execution advisories, and attaches a `gate_runtime_advisory`
  verdict to the durable JSON payload (satisfies C2).
- **A portability correction.** The pre-draft step references the **skill-local**
  `describe_goal_closeout_shape.py` (resolves via `$SKILL_DIR`), **not** the
  authoring-repo-internal `scripts/check_artifact_surface_preflight.py`
  dispatcher — caught by `validate_skill_ergonomics`
  (`portable_package_host_surface_reference`). A consumer repo (ceal) has the
  skill-local script via the installed plugin but not the repo-root dispatcher,
  so referencing the dispatcher would have made A non-portable — the exact
  version-skew failure class this spec guards against.
- **Cautilus stance for this slice (planner-consulted).**
  `plan_cautilus_proof.py`: `required=False`, `next_action=none`, `run_mode=ask`,
  with advisory skill-validation recommendations for `achieve`/`retro`. Decision:
  the deterministic `validate_skills` / `validate_public_skill_dogfood` gates
  cover this slice; live scenario/cautilus eval stays deferred (no `cautilus
  evaluate` call, per the `next_action: none` contract).

## Implementation Notes (Slice 2 folds — B)

- **Over-slice detection is the artifact-only-commit run.** The enabled,
  non-blocking advisory fires on ≥N consecutive `charness-artifacts/`-only commits
  (default N=3, `CHARNESS_OVERSLICE_ARTIFACT_RUN`) — a cheap, deterministic,
  both-polarity-testable churn signal read from `git log`. The alternative
  "≥M commits in one slice intent" was **not** made a deterministic gate: it needs
  goal-artifact intent-history attribution that is fragile to detect, so that
  dimension is carried by the `Current slice intent:` frame field plus the cadence
  prose, not a gate. Honest split: deterministic teeth where cheap, operational
  frame where detection would be fragile.
- **C5 satisfied structurally.** `Current slice intent:` is a bullet in
  `## Active Operating Frame`, which is not in `REQUIRED_SECTIONS`, so a goal
  without it still passes the complete flip — asserted directly by a test, not
  only relied on by construction.
- **Premortem↔cadence single source.** The resolution sentence lives once in
  `meaningful-slice-cadence.md` *Review Cadence*; `critique/references/cadence.md`
  and the `achieve` lifecycle defer to it (no duplicated copy that could drift).

## Canonical Artifact

`charness-artifacts/spec/achieve-efficiency-improvements.md` (this file) is the
canonical build contract during implementation. The `achieve`/`retro`/`critique`
skill surfaces and `implementation-discipline.md` are the edit targets; this spec
is updated if implementation discovers a scope/acceptance change.

## First Implementation Slice

**Slice 1 — A1 + C + advisory-module split (close-the-loop bundle):**
1. Split the runtime/over-slice **advisory into its own module** out of
   `run_slice_closeout.py` (pre-empts the length cap; gives C and B a shared
   surface).
2. Wire `check_artifact_surface_preflight.py --type goal-closeout` + the dry
   `check_goal_artifact.py` pass as the pre-draft closeout step in `lifecycle.md`
   After-phase and the SKILL.md After bullet; add the aggregate principle to the
   closeout-gate paragraph.
3. Add the gate-baseline-runtime waste category to `section-guide.md` and the
   carve-out (with the host-pre-push-hook non-claim) to
   `phase-aware-efficiency.md`; add the non-blocking advisory that aggregates
   per-gate `elapsed_seconds` into the durable closeout payload against an
   adapter-overridable budget.
4. Sync `plugins/` mirrors; run `run_slice_closeout.py` (cheap structural sweep +
   targeted tests), then the bundle broad gate; record the slice per the
   operating contract.

**Slice 2 — B-core** (frame field + enabled advisory + premortem↔cadence
sentence) on the split advisory module. **Slice 3 — D** (restraint checklist +
floor audit artifact).
