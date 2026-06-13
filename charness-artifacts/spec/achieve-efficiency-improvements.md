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

5. **The self-improvement loop never observes its own operational waste (the
   meta-gap the operator surfaced).** Despite repeated "autonomously choose the
   next work" runs, none of #1–#3 surfaced on their own — a human had to name
   them. Verified why: (a) autonomous next-work selection is the **handoff
   chunker**, which reasons over the **issue backlog + handoff doc only** (no
   usage-episode input) — so it can only pick up waste already *filed* as an
   issue; (b) **usage episodes** accumulate at
   `.charness/usage-episodes/usage_episode.jsonl` (gitignored, per-repo,
   adapter-resolvable) but capture a **product-success** signal
   (`outcome_status: delivered`, `t_status`) for the #184 conversion metric —
   they have **no field** for gate runtime, commit churn, validator-rejection
   rounds, or slice size, and the work-selection loop never reads them; (c)
   waste-detection therefore lives only in the **agent-authored retro**, with the
   #1–#3 blind spots above. Two compounding facts: cross-repo episodes are
   gitignored local (charness *structurally cannot* see ceal's), and even
   same-repo episodes record no waste fields and are not mined. Net: operational
   waste surfaces only when a human notices — exactly what happened.

**Version-skew context (scopes the fix, not fixed here).** ceal's installed
`achieve` is an older era: `lifecycle.md` 520 lines vs 752 here; 16 scripts vs
24; missing Structural-follow-up / recurrence-lineage / Closeout-Delegation /
`describe_goal_closeout_shape`. The ceal pain occurred on a *lighter* closeout
contract. The current charness contract is *heavier*, so naive propagation would
make #1 **worse** unless A lands first. This is the central design constraint.

## Current Slice / Sequence

Status (live):

- **Slice 1 = A1 + C** — **DONE** (commit `55631fe8`). Describe-first closeout
  wiring + gate-baseline-runtime waste lens + advisory; broad pytest green, C
  dogfooded live (231s gate fired the advisory).
- **Slice 2 = B** — **DONE** (commit `01104241`). `Current slice intent:` frame
  field + enabled over-slice advisory + premortem↔cadence single-source sentence.
- **Slice 3 = E (E1 + E2a)** — **DONE** (this session, post-compaction). E1 emits a
  sibling `closeout-telemetry` stream (`scripts/slice_closeout_telemetry.py`,
  wired into `run_slice_closeout.py`) reusing C's `gate_runtime_advisory` + B's
  `over_slice_run` (no recompute drift) plus a new `slice_churn` signal; E2a mines
  it (`skills/public/retro/scripts/mine_closeout_telemetry.py` + `weekly-trends.md`)
  and routes recurring (`recurs:`) waste to a **filed issue**, never the decaying
  digest. 15 new tests green; targeted proof per cadence (bundle boundary owns the
  broad re-confirm). See *Implementation Notes (Slice 3 folds — E)*.
- **Slice 4 = D** — **DONE** (this session). Floor-Addition Restraint checklist
  added to `docs/conventions/implementation-discipline.md`; closeout-floor audit
  produced at `charness-artifacts/audit/closeout-floors.md` (complete live set:
  absorb 7 / merge 4 / keep 6 in surface A + keep-all in surface B; no floor
  removed). Load-bearing finding (narrowed after critique): the Problem-1 churn was
  the *absorb-class* floors (already fixed by A1 visibility) + cadence (B/C); the
  *conditional `keep`* floors carry a residual reactive-rejection risk A2 closes.
  D's net new contribution is the restraint checklist (honestly framed as prose
  with an advisory-nudge follow-up), not remediation of existing floors.
- **Bundle boundary** — **NEXT / FINAL.** A single `run_slice_closeout.py
  --verification-lock` broad-pytest re-confirmation over the whole effort before it
  is declared complete (Slices 2/3/4 used targeted proof per the meaningful-slice
  cadence). New mutation-pool modules this effort added
  (`slice_closeout_telemetry.py`, `mine_closeout_telemetry.py`) mean the bundle
  closeout should add `--produce-mutation-coverage`.

This spec is the canonical contract for all five directions and the canonical
**resumption surface** after compaction.

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
- **E (close the loop on objective operational-waste telemetry) — PRIORITIZED
  above D (operator call).** The self-improvement loop today *captures*
  (episodes) and *surfaces* (retro digest) but never *observes* operational waste
  objectively or feeds it into work selection (Problem 5). E closes that. Two
  parts:
  - **E1 — record objective waste signals.** Persist the operational-waste
    signals the closeout already computes into a durable, accumulating telemetry
    record, reusing the usage-episode accumulation pattern (jsonl, adapter-
    resolved path, rotation) but as a **sibling `closeout-telemetry` stream**,
    *not* the product-success episode — so the #184 product-review consumers stay
    clean (separation of product-success vs operational-waste concerns). Seed the
    fields from what already exists after Slices 1–2: `gate_runtime` (C's
    `gate_runtime_advisory` verdict) and `over_slice` (B's trailing artifact-only
    run). Add `slice_churn` (commit count / artifact-only ratio over the slice).
  - **E2a — mine the stream in the weekly retro.** `retro` weekly mode already
    mines usage episodes for trends (`weekly-trends.md`); add a waste-trends
    aggregation over the `closeout-telemetry` stream that surfaces recurring
    over-budget gates / over-slice runs. **Teeth — must force the filed-issue
    branch, not the digest (critique R1b).** A recurring (`recurs:`) waste item
    must disposition to a **filed `issue`** (tracked work the chunker reasons
    over), NOT to the `recent-lessons.md` digest — the digest has a 14-day
    half-life and would decay the item back out, re-entering the exact
    Problem-4 prose-decay trap this spec criticizes. "dispositioned" alone is not
    enough; recurring waste → issue.
  - **Honest non-claim (Fixed).** Telemetry is gitignored per-repo, so mining
    surfaces *this* repo's waste only; ceal's waste needs the loop running *in*
    ceal (with patched skills) over ceal's local stream. E does not — and must
    not pretend to — give charness cross-repo visibility.
  - **Scope honesty on closure (critique R1a).** E1+E2a **instrument and surface**
    the loop; they do not by themselves close Problem 5's *autonomous-loop* gap —
    the operator's pain was per-run, and E2a mines weekly. **E2b** (deferred —
    chunker ingests recurring waste as candidate work) is what actually closes the
    autonomous loop. Do not describe E1+E2a as "closing" Problem 5.
  - **Authoring-repo thinness (critique R1, defer-with-note).** charness's own
    stream is mostly release auto-retros, not heavy autonomous-goal churn, so
    E2b's reopen trigger ("E2a proves the stream surfaces real waste") may not
    trip in charness — it likely needs a **ceal** run to demonstrate value. Record
    this so the deferred trigger is not silently dead.
- **D (restraint rule + closeout-floor audit) — now AFTER E.** Add a "before
  adding a new deterministic floor" restraint checklist to
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
- **E stream shape — sibling vs episode-schema. RESOLVED (Slice 3): sibling.**
  `closeout-telemetry.jsonl` is a sibling file in the already-gitignored
  `.charness/usage-episodes/` tree, with its own `event_type:
  "closeout_telemetry"` — NOT a `waste_signals` block on the usage-episode schema.
  This keeps the #184 product-success consumers (and the episode schema) untouched
  and lets the stream be **on by default** (the usage episode is opt-in via an
  adapter because it carries a product metric; operational-waste counters are safe
  to always accumulate locally — and must, or Problem 5 recurs). The miner filters
  by `event_type`, so the two streams could even share a file safely; separate
  files are cleaner.
- **E `fix_after_fail_rounds` capture (Problem-1 analog) — still DEFERRED.** E1
  ships `gate_runtime` + `over_slice` + `slice_churn` (all reusing or cheaply
  derived from existing closeout signals). Counting validator-rejection rounds
  objectively still needs closeout self-tracking across re-runs or a
  "describe-first preflight consulted?" proxy; carried as a follow-on probe, not a
  launch blocker. Reopen trigger: A1's describe-first wiring lands a consulted/not
  signal the closeout can record.

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
- **E2b — chunker waste-source.** Make the autonomous next-work loop (handoff
  chunker) ingest the top recurring waste from the `closeout-telemetry` stream as
  candidate work, alongside issues + handoff. Higher-leverage but higher-risk (it
  changes autonomous work selection). Reopen trigger: E2a (weekly-retro mining)
  proves the telemetry stream surfaces real, actionable recurring waste.
- **`follow-up:floor-addition-restraint-nudge`** (Slice 4 D critique). The
  Floor-Addition Restraint checklist is prose with no firing mechanism; a
  deterministic **non-blocking** advisory that flags a new blocking floor landing
  without a recorded restraint call (mirroring
  `follow-up:portability-classification-tripwire`) is the teeth. Deferred — a
  *blocking* enforcement gate is rejected (it is the reflex D names). Reopen
  trigger: a new blocking floor lands without a recorded restraint call, or an
  operator requests the nudge.
- **A2 closes the conditional-floor residual** (Slice 4 D critique sharpened the
  scope). The `keep` goal-closeout floors (rungs 1a/1b/1e, section-placeholder,
  closeout-delegation, timebox) are runtime-conditional, so the static describe-first
  catalog cannot surface them up front — they keep a residual reactive-rejection
  risk. Already tracked as the A2 probe; the D audit names the exact floor set A2
  would absorb. Reopen trigger: A2 is picked up (preflight reads the goal artifact).
- **Coordination-Cues floor merge** (Slice 4 D audit). The four
  `## Coordination Cues` floors (routing/gather/release/issue-closeout) share a
  section + opt-out grammar and could fold into one routing-presence check.
  Audit-only here; removal/merge is a separate critiqued change. Reopen trigger:
  operator request, or the floors observed to double-fire.
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
- `run_slice_closeout.py` is near its length cap (#332 retro) — keep new logic in
  `scripts/slice_closeout_advisories.py` (the advisory module already exists; the
  C7 "split" dissolved — see Implementation Notes). E1's telemetry-writer should
  follow the same module-not-entrypoint placement.
- Advisory output must be non-blocking and quiet on the common case (no false
  fire on a legitimately multi-commit slice). E1's telemetry write must likewise
  never block or fail closeout (degrade silently like the usage-episode emitter).

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
- **E (instrument + surface; E2b closes).** Operational waste the closeout
  already computes (gate runtime over budget, over-slice run) is recorded into a
  durable accumulating stream, and the weekly retro surfaces recurring instances
  and routes them to **filed issues** (not the decaying digest) — so recurring
  waste becomes tracked work the chunker reasons over. This **instruments and
  surfaces** the Problem-5 loop (scoped to this repo's stream); fully *closing*
  the autonomous-loop gap is **E2b** (deferred), where the next-work loop ingests
  the recurring waste directly.

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
- **E1:** a `run_slice_closeout.py` run appends a durable `closeout-telemetry`
  record carrying `gate_runtime` + `over_slice` (+ `slice_churn`) for the slice;
  unit test asserts the record and fields exist and reuse C's `gate_runtime_advisory`
  + B's over-slice run (no recomputation drift). Negative: a fast under-budget,
  non-churning slice records the fields as empty/zero, not absent.
- **E2a:** the weekly `retro` over a seeded `closeout-telemetry` stream (a gate
  repeatedly over budget across N records) surfaces that gate and dispositions it
  to a **filed `issue`** (recurring `recurs:` waste → tracked work), **not** a
  `recent-lessons.md` digest line; fixture test asserts the recurring waste is
  named AND the disposition is the issue branch (the digest-only branch fails the
  test, per R1b). The cross-repo non-claim is stated in the weekly output (mines
  this repo's stream only).
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

### Direction E design critique (added later, design-only)

Bounded fresh-eye spec critique on the E design (packet
`charness-artifacts/critique/2026-06-13-105232-packet.md`; 2 angle reviewers +
counterweight; parent-delegated). Coherence + acceptance coverage: PASS. Three
Act-Before-Ship, all folded:

- *R1b (must-fix)* — E2a's "dispositioned Next Improvement" could route to the
  `recent-lessons.md` digest, which decays (14-day half-life) and re-enters the
  Problem-4 prose-decay trap. Folded: E2a now **forces the filed-issue branch**
  for recurring (`recurs:`) waste, with the acceptance check asserting it.
- *R1a* — E's Success Criterion over-claimed "closes Problem 5". Folded: E1+E2a
  **instrument + surface**; **E2b** (deferred) closes the autonomous-loop gap.
- *R2* — a stale bottom-of-file "First Implementation Slice" block would mis-route
  a post-compaction reader (D before E). Folded: superseded by Current Slice /
  Sequence + Resumption.
- *Valid-but-Defer (noted, not solved)* — E's authoring-repo value is thin
  (mostly release auto-retros), so E2b's reopen trigger likely needs a ceal run.

### Direction D critique (Slice 4)

Bounded fresh-eye critique on the D deliverables (2 angle reviewers —
efficacy/self-consistency + factual-accuracy — + counterweight; parent-delegated).
The counterweight returned "ship, zero Act-Before-Ship"; both angle reviewers
returned real Act-Before-Ship findings. **Parent adjudication: the counterweight
correctly killed the over-reactions (no *blocking* tripwire now, no floor removal
now), but the honesty/accuracy findings were valid and folded:**

- *Accuracy (Act-Before-Ship, folded):* the audit's Section A inventoried ~7 of
  the live goal-closeout floors and **mis-attributed #359** to rung 1a. #359 in
  fact shipped the section-placeholder floor. Folded: Section A now lists the
  complete live set — added rungs 1e (structural-follow-up) + 1f (residual-ledger),
  the `## Coordination Cues` gather/release/issue-closeout floors (the strongest
  `merge` candidates, alongside routing), the section-placeholder floor (#359,
  correctly attributed), and the closeout-delegation/timebox/early-close-report
  floors. The tally was corrected (absorb 7 / merge 4 / keep 6).
- *Efficacy (Act-Before-Ship, folded):* D's checklist is prose, and the spec/audit
  over-claimed it "stops the next floor" — re-entering the prose-decay trap the
  spec criticizes. Folded: an honest non-claim now states the checklist shares the
  decay risk; a deterministic **non-blocking** nudge is the deferred teeth
  (`follow-up:floor-addition-restraint-nudge`); a *blocking* gate is rejected as
  self-contradictory. Checklist Q3 was scoped to static/form floors only (a
  goal-conditional floor needs A2, deferred), matching the audit's `keep` rungs.
- *Narrowing (Bundle, folded):* the audit's "no floor is a Problem-1 churn source
  today" was narrowed to "no *absorb-class* floor; the conditional `keep` floors
  carry a residual A2 closes."
- *Over-Worry (rejected, per counterweight):* "add a blocking enforcement tripwire
  NOW" (self-defeating); "remove the merge family NOW" (out of scope); "enumerate
  every gate exhaustively in surface B" (grouping is appropriate there).

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

### Direction E implementation critique (Slice 3, post-compaction)

Bounded fresh-eye code critique on the E implementation diff (impl stop gate;
parent-delegated, 3 angle reviewers — correctness/robustness, boundary-honesty,
portability/consistency — + 1 separate counterweight). **Verdict: ship; zero
Act-Before-Ship across all four.** Record:

- **Correctness/robustness:** the never-block contract holds — every git/import/
  JSON path is inside the emitter's `try`; `CHARNESS_QUALITY_MODE` suppression is
  first; emit fires exactly once per executed run with honest `status`; no-drift
  verified live (advisory and telemetry both report the same `over_slice_run`).
- **Boundary-honesty:** R1b teeth are enforced in *code*, not just prose —
  `file-issue`/`watch` are the only disposition values; the digest is not a
  reachable branch. Cross-repo non-claim emitted unconditionally. No source claims
  E "closes" Problem 5. `disabled` state genuinely visible in the terminal payload
  as declared.
- **Portability:** two path literals (emitter repo-root + miner skill-local) are
  the portable-correct choice (a shared constant would force the plugin to import
  a repo-root module a consumer lacks — the version-skew failure class); miner is
  pure stdlib and degrades gracefully on a stream-less repo; `weekly-trends.md`
  invokes it via `$SKILL_DIR`.
- **Folded (cheap):** a clarifying comment on `_slice_churn` documenting the
  deliberate unbounded-window difference vs the bounded `over_slice` field.
- **Confirmed-deferred (no action this slice):** `slice_churn` issues N+1 git
  subprocesses (acceptable at closeout cadence; revisit only on latency);
  git-OSError + float-cast hardening (already deferred with reopen triggers);
  E2a labels the `file-issue` disposition but does not auto-open a `gh` issue —
  automated chunker ingestion is **E2b** (deferred). Keep closeout language honest:
  E1+E2a instrument + surface; E2b closes.

## Implementation Notes (Slice 3 folds — E)

Facts the E implementation surfaced (kept alive per spec/impl discipline):

- **Telemetry is on by default; usage episodes stay opt-in.** The usage-episode
  emitter requires an adapter + `enabled: true` because it carries the #184
  product metric. Closeout-telemetry deliberately does NOT — gating operational
  waste behind an opt-in adapter the operator forgets to set would reproduce
  Problem 5 exactly (waste accumulates only when a human first notices). It is on
  by default, writes only under the gitignored `.charness/` tree, and is escapable
  via `CHARNESS_CLOSEOUT_TELEMETRY=off` (+ `CHARNESS_CLOSEOUT_TELEMETRY_MAX_MB`
  rotation). The `disabled` state is declared in `attention-state-visibility.json`
  so it stays visible in the terminal payload, not a silent clean state.
- **`CHARNESS_QUALITY_MODE` suppression is mandatory, not optional.** Mirrors the
  usage-episode emitter: a closeout spawned inside a quality/verification run (the
  broad pytest exports `CHARNESS_QUALITY_MODE` to its whole tree) must NOT write
  telemetry, or it races the suite (the #194 state-bleed class). Without this the
  E1 emitter would fire during its own broad-pytest gate.
- **No-drift achieved by one shared computation, not a cached value.** B's
  `advise_over_slicing` was refactored to call a new `over_slice_run(repo_root)`;
  E1's record calls the same function, so the telemetry number and the advisory
  number cannot diverge. `gate_runtime` is the literal `gate_runtime_advisory`
  object off the payload (asserted `is`-identical in the test).
- **Emit on both success and stop paths.** Telemetry attaches right after
  `attach_gate_runtime_advisory`, so a FAILED closeout (slow gate, churn) still
  records its waste with an honest `status`, not only clean completions.
- **E2a wiring lives in `weekly-trends.md`, not SKILL.md core.** The retro
  SKILL.md core was at 160/160 nonempty (zero headroom); adding the miner pointer
  to the core would have failed the length gate. The canonical weekly reference is
  the correct layer anyway (detailed routing belongs in references). A clarifying
  note resolves the apparent `What Not To Copy: telemetry` contradiction — weekly
  *reads* an existing local stream, it does not *write* hidden telemetry.
- **E2b reopen trigger unchanged.** E1+E2a instrument + surface; the autonomous
  loop (handoff chunker ingesting recurring waste) is still E2b (deferred), and its
  reopen still likely needs a ceal run to demonstrate value (charness's own stream
  is mostly release auto-retros).

## Canonical Artifact

`charness-artifacts/spec/achieve-efficiency-improvements.md` (this file) is the
canonical build contract during implementation. The `achieve`/`retro`/`critique`
skill surfaces and `implementation-discipline.md` are the edit targets; this spec
is updated if implementation discovers a scope/acceptance change.

## Resumption (post-compaction pickup)

Implementation of E (and D) is deliberately deferred to a fresh session after
compaction. To resume:

1. This spec is canonical. Slices 1 (A1+C, `55631fe8`) and 2 (B, `01104241`) are
   landed; read the `## Implementation Notes` folds before touching their code.
2. **Slice 3 = E is DONE.** E1 = `scripts/slice_closeout_telemetry.py` (wired into
   `run_slice_closeout.py`); E2a = `skills/public/retro/scripts/mine_closeout_telemetry.py`
   + `weekly-trends.md`. Read `## Implementation Notes (Slice 3 folds — E)` before
   touching their code. The sibling-vs-schema probe is resolved (sibling);
   `fix_after_fail_rounds` stays deferred.
3. **Start at Slice 4 = D.** Add the "before adding a new deterministic floor"
   restraint checklist to `docs/conventions/implementation-discipline.md`, and
   produce the closeout-floor audit at `charness-artifacts/audit/closeout-floors.md`
   (per-floor `absorb`/`merge`/`keep`; audit output only, no floor removed). Run a
   fresh bounded critique on the D diff (impl stop gate).
4. Then the **bundle-boundary** `run_slice_closeout.py --verification-lock`
   broad-pytest re-confirmation before declaring done (Slices 2/3 used targeted
   proof per the meaningful-slice cadence).
5. Honest scope reminder: telemetry is gitignored per-repo — E surfaces this
   repo's waste only; ceal needs the patched skills + its own loop run.

## First Implementation Slice

**Superseded by `## Current Slice / Sequence` and `## Resumption` above** — those
are the live plan. Historical record only: Slice 1 (A1+C, landed `55631fe8` —
note the planned "advisory-module split" *dissolved*, the module already existed)
and Slice 2 (B, landed `01104241`) are done. The next implementation slice is
**E** (post-compaction), then **D**, then the bundle-boundary broad-pytest
re-confirmation.
