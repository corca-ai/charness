# Boundary Ownership Checkpoint — Implementation Contract

Living build contract for the portable concept-boundary checkpoint requested by
issues [#416](https://github.com/corca-ai/charness/issues/416) (drift symptom),
[#414](https://github.com/corca-ai/charness/issues/414) (missing seam), and
[#408](https://github.com/corca-ai/charness/issues/408) (sharpest instance +
acceptance test). Design was agreed in a design-conversation-first session on
2026-07-05; this document crystallizes that agreement. No code has been written
yet — this spec IS the "agreed" boundary the handoff `## Next Session` #4 gated on.

## Problem

Charness portable lifecycle skills have no reliable, adapter-owned place to ask
"does this change respect the repo's producer/consumer ownership boundaries?"
When a consumer repo (Ceal) carries an ownership taxonomy
(`core/runtime/connector/workflow/instance`), the discipline either:

- leaks the consumer's taxonomy into portable skill prose (breaks portability —
  #416), or
- forces the consumer to overstuff always-loaded instructions/local prose so the
  discipline fires (bloat — #414), or
- is silently skipped, so a symptom-driven fix lands workflow-specific logic in a
  generic core reducer and a passing unit test looks like success (#408).

The three issues are one problem: the lifecycle lacks a portable **carrier** for
a boundary-ownership question whose **taxonomy** stays repo-owned.

## Capability Contract

- Actor: an agent doing task-completing repo work through `critique` / `impl`
  (and, for the authoring guard, `create-skill` / `quality`).
- Capability delta: the agent is briefed with a taxonomy-free producer/consumer
  question at review time, and closeout carries a typed boundary-ownership
  disposition whose *presence* is enforced and whose *severity* a repo-owned
  cross-surface probe can upgrade.
- Acceptance boundary: a `critique` run over a change that moves producer-owned
  behavior into a generic surface records a boundary disposition, and — when the
  repo's cross-surface probe fires — a bare `single-surface` verdict is rejected,
  even if the change's unit test passes (#408 acceptance).

## Portability Invariant (governs every decision below)

> **Charness owns the question, the disposition schema, and the carrier. The
> consumer repo owns the taxonomy, the labels, the cross-surface probe, and the
> completion statuses — supplied through its adapter, never through portable
> skill prose.**

This is the same split already shipped by `critique` `packet_sections`
(`.agents/critique-adapter.yaml`): the adapter declares section content; Charness
validates shape only and explicitly disclaims role semantics
(`Charness does not classify section roles ... Roles stay consumer-defined`).

## Current Slice

First slice = **critique + impl + a #416 authoring-lens brief**, on one shared
seam designed to extend later to `issue` / `quality` / `spec` / `achieve`
(the wider #414 list).

- **critique** is the **validated-teeth carrier** — it already has a durable
  artifact + `scaffold_critique_artifact.py` + `validate_critique_artifacts.py`
  with a date-gated presence-floor pattern (`_check_fresh_eye_typed_presence`,
  enforce-from `2026-07-05`). The boundary presence-floor mirrors that pattern.
- **impl** carries the **always-brief + an emitted `Boundary Ownership` closeout
  token**; its teeth come from the step-6 fresh-eye `critique` it already runs
  (`skills/public/impl/SKILL.md` step 6), not a new impl-only validator. impl
  deliberately has no durable artifact / scaffold / validator, and this slice
  keeps it that way.
- **#416 authoring-lens brief** — `create-skill` authoring lens and `quality`
  adapter-gate-review each gain one judgment question ("is repo taxonomy leaking
  into portable prose?"). Brief, not a gate.

## Fixed Decisions

1. **Portability invariant** as stated above. Ceal's owner nouns
   (`core/runtime/connector/workflow/instance`) enter Charness in zero places.
2. **Judge-brief, not a deterministic detector.** Detecting "workflow logic in a
   generic reducer" generically needs the taxonomy (leak) and still misses the
   general smell. The checkpoint briefs the fresh-eye reviewer; it does not try
   to mechanically classify the code as a violation.
3. **Always-brief, taxonomy-free.** The 4 producer/consumer questions live in ONE
   portable shared reference (new, e.g.
   `skills/shared/references/boundary-ownership-brief.md`); impl's existing
   `references/review-gate.md:12` "boundary honesty and ownership" lens links it,
   and the relevant critique target references (`references/code-critique.md`,
   `references/spec-critique.md` — the files that actually shape the reviewer's
   angle brief; there is NO `critique/references/review-gate.md`) surface it as an
   angle. The brief fires with no adapter configured. Adapter `packet_sections`
   enrichment adds the repo's concrete layers/labels/smells.
4. **Closeout presence-floor with always-record.** Every standalone `critique`
   closeout records a boundary-ownership disposition. The validator checks
   presence + value-in-enum, never correctness (D34 announcement posture). The
   value MAY be `single-surface`, but it MUST be present — so the disposition is
   un-omittable *within any standalone critique*.
5. **Repo-owned cross-surface probe = the objective override, at TWO enforcement
   points.** When the repo's adapter declares a cross-surface trigger
   (surfaces.json IDs or raw globs) and it matches the changed paths:
   - (a) **impl stop gate** — a hit FORCES escalation to a standalone `critique`
     (cadence rung 3), producing the durable artifact the floor needs, EVEN WHEN
     the agent self-judged the change a small local slice (`Critique: short`,
     cadence rung 2). This is the #408 override: an objective path-match beats the
     agent's own rung self-judgment.
   - (b) **critique validator** — a hit REJECTS a bare `single-surface` verdict;
     the reviewer must record `owned-correctly` / `moved-to-owner` /
     `escalated-to-issue-spec`.
   The same repo-owned probe drives both points. Without a configured probe,
   neither override exists (see Fixed Decision 6).
6. **#408 closure is CONDITIONAL on a configured probe — stated honestly.** With a
   repo probe, the impl-gate override (5a) closes the exact rung-2 silent-skip the
   #408 incident took, because the objective path-match escalates the change into
   the durable-critique path where the floor bites. WITHOUT a probe, a rung-2
   self-judged close is caught only by the taxonomy-free brief (judgment), not by
   teeth — a named residual (DBD-4). **This slice ships charness's own probe OFF
   (opt-in empty):** choosing charness's cross-surface glob set is a separate
   design task (DBD-4), so the override is proven here by the AC2/AC3/AC7 unit
   fixtures, NOT by charness's live CI — charness itself is currently a probe-less
   consumer relying on the always-brief + presence-floor + authoring-lens. The
   design does NOT claim the silent skip is closed for probe-less consumers,
   charness included, until a probe is configured.
7. **Disposition schema (one axis).** Fields: `producer`, `consumer`,
   `owning-surface` (repo-defined free label), `verdict`. `verdict` enum =
   `{single-surface, owned-correctly, moved-to-owner, escalated-to-issue-spec}`.
   `single-surface` means "no cross-surface concern found"; without a configured
   probe it is self-asserted, so it is only as strong as the reviewer's judgment
   (cross-ref DBD-4). Taxonomy-axis checkpoint result: all four values sit on one
   axis — the *terminal boundary-ownership disposition of this change* —
   isomorphic to announcement's `status ∈ {confirmed, not-confirmed,
   blocked-needs-capability, skipped}`. The enum is honest (different values imply
   materially different follow-up: `escalated-to-issue-spec` implies an issue/spec
   must exist; `moved-to-owner` implies the relocation is in the diff), so it
   stays a typed value rather than being split into `cross_surface: bool` +
   `resolution`.
8. **impl has no new validator.** impl's teeth = the escalation-forced (5a) or
   already-run step-6 `critique`. The impl `Boundary Ownership` emitted token is
   **emit-only / eval-judged, not validator-matched** — do not add an impl
   validator by reflex, and do not read the token as a deterministic floor.

## Probe Questions (resolved through the first implementation slice)

- **P1 — cross-surface probe form.** Support BOTH a `boundary_cross_surface_surfaces`
  ID list (validated against `.agents/surfaces.json` via
  `surfaces_lib.resolve_trigger_surfaces`) and a `boundary_cross_surface_globs`
  raw-glob list (`surfaces_lib.match_surfaces` / fnmatch), copying the retro
  `check_auto_trigger.py` shape. Confirm during impl whether a probe *command*
  variant (reusing `critique_packet_lib._run_command`) is also needed or is
  YAGNI for the first consumer.
- **P2 — grandfather date.** The boundary presence-floor needs its own
  `enforce-from` date constant so pre-existing critique artifacts do not
  retroactively fail (mirror `FRESH_EYE_PRESENCE_RULE_DATE`). Pick the date at
  impl time (>= first-landing date).
- **P3 — where the probe hit is computed.** Most likely the critique validator
  gains an optional `--changed-ref` mode (mirroring `check_cli_skill_surface.py`
  `--changed-path`) and computes the hit itself via
  `surfaces_lib.collect_changed_paths*`. Confirm this vs. a separate gate during
  impl.
- **P4 — impl brief placement.** Confirm the `Boundary Ownership` token slots
  into impl `## Output Shape` between `Truth Surface Sync` and `Critique`, with
  its enum in `## Closeout Vocabulary`, anchored to workflow step 5/6.

## Deferred Decisions

- **DBD-1 — deterministic taxonomy-leak guard for #416.** A checker that flags
  repo-specific nouns in portable skill prose is a content classifier; the repo's
  deterministic-floor philosophy (cf. D29) avoids that until an observed gaming
  instance shapes a narrow checkable form. The first slice ships only the
  judgment brief. Reopen trigger: an observed instance of consumer taxonomy
  leaking into portable prose that the authoring-lens brief did not catch.
- **DBD-2 — extend the checkpoint to `issue` / `quality` / `spec` / `achieve`.**
  The #414 list beyond critique+impl. The shared seam is designed to extend, but
  each stage's carrier (does it have a durable artifact? an emitted token?) needs
  the same critique-vs-impl analysis done here. Reopen trigger: the critique+impl
  slice lands and a second lifecycle stage needs the discipline.
- **DBD-3 — probe command variant (P1 tail).** If no first consumer needs a
  cross-surface *command* probe, ship globs/IDs only and defer the command
  executor wiring.
- **DBD-4 — probe-less consumer relies on brief judgment for rung-2 closes.** The
  honest residual of Fixed Decision 6: a consumer that configures no cross-surface
  probe gets the always-brief + presence-floor (inside any standalone critique)
  but NOT the impl-gate objective override, so a rung-2 self-judged cross-surface
  close is caught only by reviewer judgment. This is deliberate — a portable
  deterministic override would need the taxonomy (leak). Reopen trigger: a
  probe-less consumer reproduces the #408 failure mode often enough to justify a
  stronger portable default (e.g. shipping a conservative default cross-surface
  glob set that consumers narrow, rather than opt-in). Concrete follow-up:
  charness ships probe-off in this slice; adopting charness's own cross-surface
  glob set — plus wiring the escalated critique's `--changed-ref` validation into
  run-quality so the 5b tooth fires in charness CI — is the next boundary-checkpoint
  slice, gated on choosing globs that do not false-positive on every commit.
  - **Resolution (2026-07-05) — charness ADOPTS a narrow probe (DBD-4 closed).**
    The self-adoption slice was implemented after a corrected measurement. (A first
    measurement pass claimed broad globs were ~100% false-positive; that was a
    methodology bug — `git log -n 60 -- <path>` returns the 60 most-recent commits
    *touching* the path, capped at 60, not a rate. A fresh-eye resolution critique
    caught it.) Corrected hit-rate over the actual last 60 commits, using the probe's
    own matcher: `scripts/*_lib.py` = 5%, `skills/shared/**` = 5% (union 8%),
    `skills/public/**` = 33%, `scripts/*.py` = 13%. So a NARROW set is viable, not
    a false-positive machine. It also matters because charness's own loop had NO
    deterministic #408-class coverage: the content-scanning guards
    (`skill_issue_anchor_scan.py`, `post_edit_skill_anchor_guard.py`) catch prose
    issue-anchors and non-portable path/command cites — NOT caller-specific *code*
    landing in a shared library (#408's actual class), and NOT the taxonomy nouns
    (those are judgment-only per DBD-1). Decision (operator, 2026-07-05): adopt
    `boundary_cross_surface_globs: [scripts/*_lib.py, skills/shared/**]` (8% hit) and
    wire `--changed-ref` into `run-quality.sh` so the 5b tooth fires in charness CI.
    Verified end-to-end: the configured probe rejects a bare `single-surface` verdict
    when the changed set touches a glob path and passes otherwise. #408's mechanism
    acceptance (fixtures) is now backed by charness's own live dogfood.

## Non-Goals

- A Charness-side ownership taxonomy or any enumeration of surface kinds.
- A deterministic detector of ownership-boundary violations in code.
- Blocking on the *correctness* of a recorded disposition (only its presence /
  typed value / cross-surface consistency is enforced).
- New durable-artifact/scaffold/validator machinery for `impl`.

## Deliberately Not Doing

- **Not** giving impl a net-new durable closeout artifact + validator (rejected
  in the design conversation: it is scope creep against impl's intentional
  "emit status, no durable file" identity; teeth route through the critique impl
  already runs).
- **Not** making the presence-floor fire only when the reviewer self-declares
  cross-surface (rejected: reintroduces the exact #408 silent-skip).
- **Not** attempting a deterministic cross-surface *content* gate (rejected:
  needs taxonomy = leak, and conflicts with the north-star judgment-first stance).

## Constraints

- Reuse existing seams; add minimal new surface:
  - packet render: `skills/public/critique/scripts/prepare_packet.py` +
    `scripts/critique_packet_lib.py` (`content_kind: script|static`) — content-agnostic already.
  - scaffold: `skills/public/critique/scripts/scaffold_critique_artifact.py`.
  - validator: `scripts/validate_critique_artifacts.py` (append a check to the
    `checks` tuple; mirror `_check_fresh_eye_typed_presence`).
  - probe machinery: `scripts/surfaces_lib.py`
    (`collect_changed_paths` / `match_surfaces` / `resolve_trigger_surfaces`);
    copy-target `skills/public/retro/scripts/check_auto_trigger.py`. The SAME
    probe has two consumers: the critique validator (severity upgrade) and a new
    small impl stop-gate hook (escalation-force). The impl hook is a
    cadence-escalation signal, not a durable-artifact validator — it does not
    violate Fixed Decision 8.
  - presence+enum posture: `scripts/announcement_verification_lib.py`
    (`evaluate_delivery_verification`, `DELIVERY_VERIFICATION_STATUSES`) — no
    generic "present + in-enum" helper exists; reimplement the ~4-line pattern.
- Installed `charness` CLI stays stdlib-only and runnable from a managed checkout.
- Scaffold↔validator enum legends must stay pinned (existing drift test).
- Sync the checked-in plugin export mirror before validators (mutate→sync→verify).

## Success Criteria

- SC1 — With no adapter config, a `critique` run surfaces the taxonomy-free
  producer/consumer brief to the fresh-eye reviewer, and the reviewer records a
  typed boundary disposition at closeout.
- SC2 — The critique validator FAILS a post-enforce-date critique artifact whose
  `## Boundary Ownership` disposition is missing or whose `verdict` is not in the
  enum; it PASSES a `single-surface` disposition when no cross-surface probe is
  configured.
- SC3 — With a repo-owned cross-surface probe declared and the changed paths
  matching it, the validator REJECTS a `single-surface` verdict and PASSES
  `owned-correctly` / `moved-to-owner` / `escalated-to-issue-spec`.
- SC4 — The #408 scenario: a critique over a sample patch that adds
  workflow-specific logic to a generic reducer records a boundary disposition and
  (probe firing) cannot close as `single-surface`, even though the sample's unit
  test passes.
- SC5 — impl's closeout emits a `Boundary Ownership` token; impl's step-6
  critique is the artifact that carries the validated disposition. No impl-only
  validator is added.
- SC6 — `create-skill` and `quality` adapter-gate-review each surface the
  "is repo taxonomy leaking into portable prose?" question. Zero Ceal nouns
  appear anywhere in portable skill/reference prose (grep-clean).
- SC7 (the #408 override) — With a repo cross-surface probe configured, an impl
  slice whose changed paths match the probe is FORCED to escalate to a standalone
  `critique` (producing the durable artifact the floor bites), even when the agent
  self-judged it a small local slice. Without a probe configured, no escalation is
  forced (DBD-4).

## Acceptance Checks

- AC1 (`unit`) — validator test: missing `## Boundary Ownership` section OR
  out-of-enum `verdict` on a post-enforce-date artifact → non-zero;
  `single-surface` with no probe → zero. Anchors SC2.
- AC2 (`unit`) — validator test: probe-configured + changed paths match +
  `verdict: single-surface` → non-zero; same with `moved-to-owner` → zero.
  Anchors SC3.
- AC3 (`unit`) — probe-resolution test: `boundary_cross_surface_surfaces` (valid
  + invalid ID) and `boundary_cross_surface_globs` against a synthetic
  changed-path set resolve via `surfaces_lib` helpers. Anchors SC3/P1.
- AC4 (`integration`) — scaffold→validator round-trip: a freshly scaffolded
  critique artifact passes the new check; the enum-legend drift test stays green.
  Anchors SC2.
- AC5 (`eval`) — the #408 sample-patch scenario as a fixture: a critique packet +
  reviewer brief over the reducer-regex sample produces a disposition and blocks
  a `single-surface` close. Anchors SC4. (Cautilus eval-only, ask-before-run per
  repo contract.)
- AC6 (`manual`) — grep the portable `skills/public/**` + `skills/shared/**`
  prose for Ceal owner nouns after the slice; expect zero. Anchors SC6.
- AC7 (`unit`) — impl stop-gate hook test: probe configured + changed paths match
  → escalation signal is TRUE (force standalone critique); probe configured + no
  match → FALSE; no probe configured → FALSE (no forced escalation). Anchors SC7 —
  this is the deterministic proof of the #408 override, independent of AC5's eval.
- AC8 (`unit`) — brief-reachability test: assert the portable
  `boundary-ownership-brief.md` is linked from impl `review-gate.md` AND surfaced
  by the critique target references (`code-critique.md` / `spec-critique.md`), so
  SC1's "surface the brief to the reviewer" half is deterministically proven, not
  left to AC5. Anchors SC1 (surfacing half).
- AC9 (`unit`) — impl-token grep test: impl `## Output Shape` and
  `## Closeout Vocabulary` contain the `Boundary Ownership` token. Cheap anchor
  for SC5 that does not lean on the eval-only channel.

## Critique

- **Taxonomy-axis checkpoint (run):** the `verdict` enum was tested against
  `references/taxonomy-axis-checkpoint.md`. Result: one axis (terminal
  boundary-ownership disposition), honest enum (values imply materially different
  follow-up), kept as a single typed field rather than split. Recorded here so a
  future maintainer does not re-litigate the axis.
- **Risk-interrupt planner:** `plan_risk_interrupt.py` = `not-applicable` (no
  forced debug interrupt to consume).
- **Likely implementer misread #1:** treating "critique + impl" as symmetric.
  They are NOT — critique carries validated teeth; impl carries only brief+token
  and leans on its step-6 critique. The spec states this explicitly (Fixed
  Decision 7) so impl does not grow a validator by reflex.
- **Likely implementer misread #2:** putting the 4 brief questions only in the
  adapter `packet_sections`. That would make the brief non-portable (fires only
  when an adapter declares it). The portable questions MUST live in the portable
  reference; the adapter section is enrichment only (Fixed Decision 3).
- **Overstated-acceptance guard:** SC4/AC5 is the load-bearing acceptance. It is
  an `eval`-class check (Cautilus, ask-before-run), so the deterministic teeth
  (AC1–AC4 `unit`/`integration`) must independently prove the presence-floor and
  probe-upgrade without waiting on the eval.
- **Hidden sequencing:** the cross-surface probe (SC3) depends on the presence
  floor (SC2) existing first; land SC2's validator check before wiring SC3's
  probe-aware upgrade, so the enforce-from grandfather (P2) is exercised once.
- **Fresh-eye satisfaction:** a bounded fresh-eye reviewer (read-only, shared
  worktree) reviewed this contract on 2026-07-05. Verdict REVISE. It confirmed
  portability holds across every proposed surface (zero Ceal nouns) and that the
  deterministic AC1–AC4 prove the floor+upgrade without the eval. It caught three
  real issues, now incorporated: (F1) the floor/probe only ran on durable critique
  artifacts, so the exact #408 rung-2 self-judged close bypassed them → added the
  impl stop-gate probe override (FD5a, FD6, SC7, AC7) and made the #408 closure
  claim conditional on a configured probe (DBD-4); (F2) `review-gate.md` was
  misattributed — the lens lives in impl, critique has no such file — corrected in
  FD3 + First Slice #1, with the real surfacing home specified; (F3) SC1's
  surfacing half and SC5 lacked deterministic checks → added AC8/AC9. Two nits
  (F4 enum self-assertion, F5 emit-only token framing) folded into FD7/FD8. The
  reviewer named the enum-split framing and further portability hunting as
  over-worry; not over-corrected.

## Canonical Artifact

- This document during implementation of the first slice.
- On landing, the three issues (#416/#414/#408) get the agreed direction
  reflected as comments (external write — operator-confirmed before posting).

## First Implementation Slice

1. Create ONE portable, taxonomy-free brief at
   `skills/shared/references/boundary-ownership-brief.md` (the 4 producer/consumer
   questions). Link it from impl's existing `references/review-gate.md:12`
   "boundary honesty and ownership" lens, and surface it as an angle in the
   critique target references `references/code-critique.md` /
   `references/spec-critique.md` (there is no `critique/references/review-gate.md`;
   do not create one). Land AC8 (reachability). Portable, taxonomy-free.
2. Add `## Boundary Ownership` to `scaffold_critique_artifact.py` and a
   `_check_boundary_ownership_typed_presence` (own enforce-from date, P2) to
   `scripts/validate_critique_artifacts.py`; append to its `checks` tuple. Land
   AC1/AC4 first (presence floor before probe).
3. Wire the repo-owned cross-surface probe: adapter keys
   `boundary_cross_surface_surfaces` / `boundary_cross_surface_globs`. Two
   consumers: (a) critique validator `--changed-ref` mode reusing `surfaces_lib`
   (land AC2/AC3, severity upgrade); (b) a new small impl stop-gate hook that,
   on a probe hit, emits an escalation signal forcing a standalone critique
   (land AC7, the #408 override). Sequencing: land the presence floor (step 2)
   before this probe-aware layer so the enforce-from grandfather is exercised once.
4. Add the impl `Boundary Ownership` emitted token to `skills/public/impl/SKILL.md`
   `## Output Shape` + `## Closeout Vocabulary` (P4), flagged emit-only /
   eval-judged (not validator-matched). No impl validator. Land AC9.
5. Add the #416 authoring-lens question to `create-skill` and `quality`
   adapter-gate-review references; AC6 grep-clean.
6. Sync the checked-in plugin export mirror, run repo validators, then the AC5
   eval fixture (ask-before-run). Bounded fresh-eye critique before finalizing.
