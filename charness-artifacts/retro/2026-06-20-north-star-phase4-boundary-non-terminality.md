## Mode

session

## Context

Closeout of the north-star **Phase 4** goal
(`charness-artifacts/goals/2026-06-20-north-star-phase4-boundary-non-terminality.md`):
extend the non-terminality doctrine to the remaining irreversible boundaries and
make the one boundary charness does NOT own portable. Five slices, all committed,
each with a bounded fresh-eye critique PASS (no blockers):

- **S0** — concept spec locked by a gating fresh-eye critique (`4e18811b`).
- **WS-1** — release-publish rung-1 presence floor + rung-2 distinct-channel
  observer on BOTH the main and `--resume` paths (`e45f71d2`).
- **WS-2** — Direction-3 refuse-on-undispositioned-HOTL-entry floor on
  `issue verify-closeout` (`cfb1ae9a`).
- **WS-3a** — Tier-1 `ceal-dev` consumer-name portability deleak (`757a8264`).
- **WS-3b** — Tier-2 verb-vocabulary deleak: `applied-restarted` → `instance-synced`
  straight rename + `goal_artifact_discussion` adapter-provided deploy vocab +
  `Post-Apply` → `Post-Checkpoint Commit` heading (`cddcf161`).

Bundle proof: **3520 pytest pass** (3444 default + 76 release_only) over the final
bundled state.

## Waste

- **WS-1 SKILL.md headroom churn — 3 edit cycles on one bullet.** I added a 7-line
  bullet to `release/SKILL.md`, hit `long_core` (161/160), trimmed to 3 lines, hit
  the *staged* `core-headroom` ratchet (157, buffer 4), trimmed to a 1-line pointer
  (155). The mechanism detail belonged in the reference from the start. The
  recent-lessons "headroom discipline" lesson already existed; I did not **measure
  the core buffer before adding**. Notably I then applied the lesson correctly for
  WS-2 (issue SKILL.md was 159/160 → I put the floor doc in the reference, not the
  core) — so the cost was front-loaded into WS-1.
- **Named-subagent spawn round-trips.** S0 and WS-1 critiques used `name:` +
  mailbox; retrieving each verdict needed an idle-notification → `SendMessage`
  round trip (one even returned an idle signal with no content, needing a second
  nudge). The later critiques (WS-2/3a/3b) spawned WITHOUT a name and the final
  message returned directly — cleaner and faster. One named spawn was also
  rejected outright ("teammates cannot spawn teammates"), costing a re-spawn.
- **Minor:** a `docs/public-skill-dogfood.json` Edit anchor used the wrong
  next-case `skill_id` (assumed `narrative`, was `announcement`) → one failed Edit
  + re-read.

## Critical Decisions

- **Concept-first S0 with a gating fresh-eye critique before ANY impl.** This
  front-loaded code-surface verification and caught **two protected sites the plan
  critique missed** — the P4 domain-blindness guard (`test_proof_semantics_adapter.py:244`)
  and the heading pin test (`test_workflow_safety_docs.py:14`). It made every impl
  slice mechanical and prevented WS-3a over-firing. Highest-leverage decision.
- **F2a (the WS-1 non-terminality rule).** Issue-close advances on rung-1
  record-PRESENCE only — a confirmation OR a typed disposition pass equally — never
  an automated `confirmed ⇒ proceed` gate. The gating critique's Blocker 1
  sharpened this; without it I would have wired the HTTP fetch as a second
  automated gate, relocating the #386/P4 anti-pattern to a new channel.
- **Closing BOTH publish paths (WS-1).** The `--resume` path was a parallel escape
  (it lacked even the main path's `release_verified` hard-fail). Wiring only the
  main path would have left a half-closed boundary.
- **WS-3b straight-rename (no alias) + Option A (behavior-preserving default).** S0
  locked both from evidence (token-agnostic gate + membership drift test;
  guard-loss of Option B); the fresh-eye reviewer drove a legacy
  `applied-restarted — verified:` artifact through the gate to PROVE the rename is
  safe. Avoided over-engineering (the alias) and a lost guard (Option B) at once.

## Expert Counterfactuals

- **SRE / observability lens (Charity Majors).** Would push that a `not-confirmed`
  distinct-channel result that still closes issues MUST be loud, or it silently
  ships. The F2a design records it in the artifact + the dogfood, but the *human
  rung-2 audit* at release closeout is the actual stop — the counterfactual sharpens
  that the release closeout should **surface the distinct-channel disposition
  prominently** so the rung-2 reviewer cannot miss a `not-confirmed`. (Next
  Improvement below.)
- **API-design / "don't complect" lens (Rich Hickey).** The WS-3b adapter seam
  REPLACES the English default rather than extending it. Hickey would ask whether a
  consumer who declares one verb silently losing the English set is a surprise. The
  decision is defensible (the neutral concepts always fire; the consumer owns their
  vocabulary) and is documented in the adapter-contract — but replace-vs-extend was
  a real semantic fork worth the explicit doc, which it got.

## Next Improvements

- **workflow:** Before adding prose to a `SKILL.md`, **measure the core buffer**
  (`inventory_skill_ergonomics.py --max-core-lines 160`); at ≥155/160, author new
  content in a reference, not the core. Reinforces the existing headroom-discipline
  lesson with a *pre-edit measure* habit (the 3-cycle churn above).
- **workflow:** For a one-shot fresh-eye critique whose verdict you just want
  returned, spawn the subagent **without a `name`** (direct final-message return);
  reserve named+mailbox for agents you address repeatedly.
- **capability:** none new — the gate suite (attention-state-visibility,
  skill-ergonomics, staged core-headroom, mirror-drift, cautilus-skill-review,
  prose-pin) each caught a real issue this goal. The current bar is the right one.
- **memory:** this retro + the recent-lessons digest.

## Sibling Search

The headroom-churn waste is transferable to any near-cap `SKILL.md`. Four-axis
scan over the surfaces this goal touched: **release** SKILL.md (155 after the fix),
**issue** SKILL.md (159/160 — core untouched, floor doc went to the reference =
lesson already applied mid-goal), **achieve** (references only, core untouched),
**quality** (only a reference JSON touched). No un-applied sibling remains — the
fix is a *habit* (measure-first), already exercised correctly for WS-2.
Destination: `applied: the WS-2 issue-SKILL.md edit already routed to the
reference; the next-improvement workflow habit is the durable guard` — no issue
needed (recurs only as agent discipline, which the recent-lessons digest carries).

## Persisted

(to be set by the persistence helper)
