# Achieve Goal: Goal-doc coordination cues: route via find-skills + gather/release floors

Status: active
Created: 2026-05-30
Activation: `/goal @charness-artifacts/goals/2026-05-30-coordination-cues-find-skills-routing.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

When achieve shapes a goal, make the goal document carry a coordination cue that routes phase-appropriate skills through find-skills (defer *which* skill to find-skills' recommendation engine — `--recommend-for-task` / `--recommendation-role --next-skill-id` — never a static phase→skill map in achieve), plus exactly two presence-only closeout evidence floors for the cases find-skills routing under-serves: gather (when `## Context Sources` names an external URL/Slack/Notion/Docs) and release (when the run touched a release surface). All scoped to an already-activated /goal run — never auto-invoke at shaping (preserve pursue-only, #247). achieve owns the carrier + the two floors; find-skills owns the recommendation content. Defer the bidirectional issue/debug-read-the-goal surface (critique C9) to its own effort.

## Non-Goals

- **Not** a static phase→skill map inside achieve. That duplicates find-skills' already-shipped recommendation engine (critique C12) as a staler copy and creates O(skills × surfaces) drift (C14). The carrier *defers* to find-skills; it never enumerates skills inline.
- **Not** cueing `setup` / `create-cli` / `create-skill` (critique C6/C7, Over-Worry — speculative breadth; operators reach these deliberately).
- **Not** "when complex enough"-style prose cues that never fire (critique C3 pattern). A cue that matters earns a presence floor, not hope-prose.
- **Not** literal auto-invoke / auto-run of skills — collides with pursue-only (#247); achieve stays a goal operator, not a task runner (critique C11/C13). The cue surfaces an affordance; the agent in the active run chooses whether/when.
- **Not** the bidirectional surface where a standalone `/issue` or `/debug` reads the active goal (critique C9). Real and architecturally serious, but its own O(skills) effort across `active-goal-coordination.md` + the coordinated skills — explicitly deferred; file it separately if pursued.
- **Not** content classification. Floors are **presence/binding-only** (#253 deterministic-floor philosophy); they check that a reference line exists and binds, never whether prose is "good enough".

## Boundaries

- **Ownership split (hard line):** achieve owns the goal lifecycle + the carrier slot + the two evidence floors; find-skills owns "which skill answers this boundary" (its `--recommend-for-task` / `--recommendation-role --next-skill-id` engine). The carrier must defer to find-skills, never inline a skill list.
- **Mechanism — cue at the surface read at that phase:** the routing cue must be seeded where the agent reads it mid-run (a goal-artifact `## Coordination Cues` slot or equivalent), not only in a reference read once at `/achieve` shaping (critique C8 — a role table read once is inert when it would fire).
- **Scope — active run only:** the cue + floors apply inside an already-activated `/goal` run (`Status: active`), never at `/achieve` shaping. Reuse the active-goal presence gate so the pursue-only contract (#247) is preserved.
- **Floors mirror the #253 closeout-evidence shape:** presence-only + clone-safe (in-file content, not mtime), block-the-blank at the `complete` flip, with an explicit opt-out line (`release: n/a — <reason>`, ≥ a min length, like the disposition opt-out). gather floor: `## Context Sources` names an external source (URL/Slack/Notion/Docs) AND no gather reference present → refuse complete. release floor: a release surface changed AND no release reference present → refuse complete (or opt-out).
- **Cheap deterministic detection:** "external source in Context Sources" and "release surface touched" must be cheap, deterministic, clone-safe signals (mirror `goal_artifact_closeout_evidence` binding). Decide the release-surface signal during impl (e.g., changed paths under the release manifest set, or an explicit goal-shaped declaration).
- **Grandfather by `Created` date** like #253, so in-flight goals shaped before the floors existed are not punished.
- **Phase barrier:** `mutate → sync → verify`; sync the `plugins/` mirror before validators (#257 gate).
- **Keep each coordinated skill useful standalone; no achieve-only branches** (critique C13; the coordination.md guardrail).

## User Acceptance

What the user can do to verify completion directly:

1. Shape a goal whose `## Context Sources` names an external URL but carries no gather reference → `check_goal_artifact.py` / the `complete` flip **flags the missing gather step** (or requires an explicit opt-out).
2. A goal that bumped a plugin version / touched an install manifest with no release reference → the `complete` flip is **flagged** (or requires `release: n/a — <reason>`).
3. A normal goal (no external source, no release surface) flips `complete` with **no new friction**.
4. The goal template / shaping output carries a **find-skills routing cue**, and `achieve` has **not** grown a static inline phase→skill list (grep confirms).
5. Full `pytest` green; `plugins/` mirror in sync.

## Agent Verification Plan

Expected proof cost: medium (goal-artifact evidence-gate code + template + tests). Expected test-duplication pressure: moderate — new floor tests sit next to the existing closeout-evidence tests; reuse those fixtures and watch for overlap rather than cloning them.

### Low-Cost Checks

- Targeted `pytest` on the `goal_artifact_*` tests + the new floor tests.
- `check_goal_artifact.py` on crafted fixtures: external-source-without-gather (must flag), release-surface-without-release (must flag), clean goal (must pass), opt-out present (must pass).
- grep: `achieve` carries no inline phase→skill map; the carrier cites find-skills.

### High-Confidence Checks

- Full `pytest` suite.
- The repo's standard quality gate (routed through `quality`).
- A bounded fresh-eye **implementation** critique (this is gate/contract code).

### External Or Live Proof

- **None applies** — deterministic library + template + docs change, no provider/network/live/release surface to exercise. State this explicitly at closeout (not "skipped").

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Carrier + find-skills routing cue (template `## Coordination Cues` slot + Before/During lifecycle instruction to fill it via find-skills; defer which-skill to find-skills) + docs reconciliation | The mechanism that makes any cue reachable mid-run (C8); deferral to find-skills (C12) is the ownership spine | template slot added; lifecycle/coordination.md cue cites find-skills' recommendation engine, no inline skill list; mirror synced; targeted tests | done |
| 2 | gather closeout evidence floor (detect external source in `## Context Sources`; require gather reference or opt-out; scoped to active run; presence-only; Created-grandfathered) + tests | gather is the highest-value uncued gap (C1; CLAUDE.md mandates external-source routing) | floor in `goal_artifact_closeout_evidence`-style code; crafted-fixture tests (flag / pass / opt-out); mirror synced | done |
| 3 | release closeout evidence floor (detect release-surface change; require release reference or `release: n/a — <reason>`) + tests | release lets achieve flip `complete` with unsynced version/manifest (C2) | floor + release-surface signal; tests; mirror synced | done |

## Coordination Cues

Dogfood of the carrier this goal ships. This goal is grandfathered for the
closeout floors (`Created: 2026-05-30` < the `2026-05-31` cutoff), so they are
inert here — the section is recorded as a worked example of the slot.

- **Routing** — `find-skills` routed this session to `achieve` (the work skill;
  task named it verbatim) + `critique` (the bounded fresh-eye review) with the
  `quality` default for validation closeout. No static phase→skill map was
  consulted; the route came from the recommendation engine.
- Gather: n/a — every `## Context Sources` reference is a local repo path or a
  bare issue number; no external URL / Slack / Notion / Docs source to gather.
- Release: n/a — this run edited skill source and synced the `plugins/` mirror
  but cut no version bump or install-manifest, so no release proof applies.

## Slice Log

### Slice 1: Carrier + find-skills routing cue + docs reconciliation

- Objective: Add a goal-template `## Coordination Cues` slot read mid-run that defers WHICH skill to find-skills (recommendation engine), with no inline phase->skill map; reconcile the concept across lifecycle/coordination/SKILL/goal-artifact references + the closeout contract doc.
- Why this approach: The mechanism that makes any cue reachable mid-run (critique C8); deferral to find-skills (C12) is the ownership spine. A read-once role table is inert exactly when the cue would fire.
- Commits:
- What changed: goal_artifact_template.md (+## Coordination Cues seed); references/lifecycle.md (During 'Coordination cues' subsection); references/coordination.md (find-skills routing + floors section); references/goal-artifact.md (shape block); SKILL.md (After bullet, Output Shape, Guardrail); docs/prescribed-skill-closeout-contract.md.
- Alternatives rejected:
- Targeted verification: grep: template cites find-skills, no inline skill enumeration (User Acceptance #4); validate_skills (SKILL.md under 200-line ceiling); template seed inert test.
- Test duplication pressure:
- Critique: Folded into the fresh-eye implementation critique run on the whole change (see slices 2/3).
- Off-goal findings:
- Lessons carried forward: Seed examples must be inside backticks + line-anchored so the carrier text never parses as a real Gather:/Release: line (template self-poisoning guard).
- Metrics:

### Slice 2: gather closeout-evidence floor

- Objective: Presence-only floor: when `## Context Sources` names an external http(s):// source, refuse the complete flip unless `## Coordination Cues` records a Gather: step or a Gather: n/a -- <reason> opt-out (>=30 chars). Grandfathered by Created, clone-safe (artifact text only).
- Why this approach: gather is the highest-value uncued gap (C1); CLAUDE.md mandates routing external sources through gather. Prose-only cues get skipped under context pressure (#233 3x recurrence).
- Commits:
- What changed: NEW goal_artifact_coordination_floors.py (leaf, mirrors goal_artifact_disposition.py); wired via goal_artifact_closeout_evidence.apply_coordination_floors; surfaced in check_goal_artifact.py; refusal note in goal_artifact_lib.py (length-neutral).
- Alternatives rejected: Rejected git-diff detection (not clone-safe); rejected REQUIRED_SECTIONS for Coordination Cues (would break every existing goal).
- Targeted verification: tests/quality_gates/test_goal_coordination_floors.py: trigger on URL, inert on local paths/#N, scoped to Context Sources, fenced-URL ignored, ref/opt-out/short-opt-out parsing, grandfather; CLI smoke on a crafted external-source-no-gather fixture flags it.
- Test duplication pressure: New test file 347/800 lines; sits beside the disposition-floor tests, reuses their goal-construction shape rather than cloning fixtures.
- Critique: Fresh-eye implementation critique (opus subagent a1052f6babb139f00): no blockers; confirmed grandfather/fail-closed/template-inert/report-wiring correct.
- Off-goal findings:
- Lessons carried forward: Reference/opt-out detection scoped to Coordination Cues so a goal that merely describes a step line in prose cannot falsely satisfy (the #253 round-2 B-2 poisoning shape).
- Metrics:

### Slice 3: release closeout-evidence floor

- Objective: Presence-only floor: when the run's recorded work names a release-surface token (bump_version / publish_release / marketplace.json / charness-artifacts/release/), refuse the complete flip unless Coordination Cues records a Release: step or Release: n/a -- <reason>. Coordination Cues span excluded from the token scan.
- Why this approach: release lets achieve flip complete with an unsynced version/manifest (C2). The token set is precise filenames/actions, never the bare word 'release', so a goal that merely references the release skill as context does not self-trip.
- Commits:
- What changed: Same goal_artifact_coordination_floors.py: release_triggered() (token scan minus Coordination Cues span) + the Release: branch of apply_coordination_floors; release ownership allowlist entry in scripts/check_skill_ownership_overlap.allowlist.txt.
- Alternatives rejected: Rejected detecting marketplace.json/plugin.json as version signal alone (regenerated on every mirror sync -> would over-fire on every skill edit); chose version-bump action + release-artifact tokens.
- Targeted verification: test_goal_coordination_floors.py: trigger on bump_version/marketplace.json/release-artifact tokens, inert on bare release-skill mention + plugins/ mirror sync, Coordination-Cues-excluded, fenced-token ignored, ref/opt-out, both-floors-together; check_skill_ownership_overlap green.
- Test duplication pressure:
- Critique: Same fresh-eye critique. Fixed N1 (order-dependent false refusal: _parse_step took the first step line; now prefers the first SATISFYING line) + added a regression test (25 tests total). Over-fire on mere token mention is the accepted determinism cost, cleared by the one-line opt-out.
- Off-goal findings:
- Lessons carried forward: The ownership-overlap gate (check_skill_ownership_overlap) is the sanctioned place to declare an intentional cross-skill reference; the floor's charness-artifacts/release/ token needed an allowlist row, not removal.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- **This session's `critique` run** (the design basis): prepare packet `charness-artifacts/critique/2026-05-30-085915-packet.md`; 3 angle subagents (coverage-gap `a9401f81abf72b596`, mechanism-efficacy `acc7f28300ea26669`, boundary-overlap `aba1fd09ef1dff327`) + counterweight `ab10a490e3ce4cadd`. The triage + net recommendation are narrated in Plan Critique Findings below.
- **find-skills recommendation engine** (the deferral target): `skills/public/find-skills/scripts/list_capabilities_lib.py` (`--recommend-for-task`, `--recommendation-role --next-skill-id`); `skills/public/find-skills/SKILL.md` ("Drive The Routed Workflow"); `skills/public/find-skills/references/session-start-routing.md`.
- **achieve coordination surfaces to extend:** `skills/public/achieve/references/coordination.md` (table + "Resolving A Tracked Issue"), `references/lifecycle.md`, `SKILL.md`, `scripts/goal_artifact_template.md`.
- **The floor pattern to mirror (#253):** `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py` and `goal_artifact_disposition.py` — presence-only floor, binding, `Created`-grandfather, opt-out min-length.
- **Deferred (C9):** `skills/shared/references/active-goal-coordination.md` (currently wires only impl/quality/critique/issue).
- **Target skills + repo rules:** `skills/public/gather/`, `skills/public/release/`; `CLAUDE.md` (external URLs route through `gather`; `mutate → sync → verify → publish`).

## Interview Decisions

- **Route via find-skills vs grow achieve's own map.** Family: {defer to find-skills, static phase→skill map in achieve}. Chosen: **defer to find-skills** (user-confirmed). Rejected the static map — it duplicates a shipped engine, drifts across 4+ surfaces, and risks the "achieve-only branch" guardrail.
- **Pure prose cue vs prose + evidence floor for the named-weak cases.** Chosen: **general prose cue (find-skills routing) + presence-only floors for the two named-weak cases**. Rejected prose-only for the named ones — the repo's #233 recurrence (3×) shows prose-only cues get skipped under context pressure; the user accepted giving the named ones teeth.
- **Which weak cases get floors.** Chosen: **gather + release** (high-frequency, contract-mandated / correctness). Rejected floors for spec / hitl / narrative / announcement / setup / create-* (critique triage: defer or over-worry).
- **Auto-invoke vs cue-within-active-run.** Chosen: **cue within an active `/goal` run only**. Rejected literal auto-invoke (pursue-only #247; achieve is not a task runner).
- **C9 bidirectional surface.** Chosen: **defer**. Rejected bundling it (own O(skills) effort across the shared reference + coordinated skills).

## Plan Critique Findings

The `critique` skill ran this session (premortem target) **before** this goal was shaped — its result is the goal's basis, recorded here so a fresh session does not re-run it.

- **Angles (3) + counterweight (1):** coverage-gap (pro-coordination), mechanism-efficacy, boundary-overlap, then a skeptical counterweight triage. AgentIds in Context Sources.
- **Folded into Boundaries / Slice Plan:** defer-to-find-skills ownership (C12); the cue must be seeded where the agent reads it mid-run, not a read-once role table (C8); presence-only floors for the two named-weak gaps gather/release (C1/C2/C10); scope to an active run to respect pursue-only (C11).
- **Over-worry (raised, not folded):** cue setup/create-cli/create-skill (C6/C7 — speculative breadth); generic drift fears (C13/C14 — they bite only the static-map design this goal rejects).
- **Valid but deferred:** spec cue tuning (C3), hitl (C4), narrative/announcement (C5), and the bidirectional issue/debug-read-the-goal surface (C9 — its own effort).
- **Counterweight's correction of the premise:** the operator's "auto-invoke the right skill by judgment" framing is *partly over-reach* — "auto-invoke" collides with pursue-only (#247) and "by judgment" re-invents find-skills. The honest kernel is "phase-conditioned, find-skills-backed cues surfaced in-artifact, scoped to active runs" — which this goal builds.
- **Standing note:** the critique flagged commit `0d44ca0` (debug + issue-close coordination, shipped this session) as a small instance of the read-once / one-directional pattern. Accepted as standing (it has the concrete `Close #N` evidence anchor); this goal is the better long-term form and should not be extended via more read-once prose.

## Off-Goal Findings

_None yet._

## Final Verification

Self-verification against the original goal (Deming "study" step — measured against the prediction):

- **Carrier (Slice 1):** the template seeds `## Coordination Cues` (read mid-run, after Slice Plan) that defers *which* skill to `find-skills`' recommendation engine; grep confirms no inline phase→skill map in the carrier (User Acceptance #4 met). Concept reconciled across `lifecycle.md`, `coordination.md`, `goal-artifact.md`, `SKILL.md` (still < the 200-line ceiling), and `docs/prescribed-skill-closeout-contract.md`.
- **gather floor (Slice 2):** an external `http(s)://` source in `## Context Sources` refuses the `complete` flip unless `## Coordination Cues` records a `Gather:` step or a `Gather: n/a — <reason>` opt-out (≥30 chars). CLI smoke on a crafted external-source-no-gather fixture flagged it (User Acceptance #1 met).
- **release floor (Slice 3):** a release-surface token in the run's recorded work (`bump_version`/`publish_release`/`marketplace.json`/`charness-artifacts/release/`) refuses the flip unless a `Release:` step / opt-out is present; tokens are precise so a bare release-skill mention or a `plugins/` mirror sync does not self-trip (User Acceptance #2 met).
- **No new friction (User Acceptance #3):** a goal with no external source and no release token is inert — `test_clean_goal_no_floors_no_friction` + the grandfather cutoff confirm it.
- **Tests / parity (User Acceptance #5):** full `pytest tests/` = **1893 passed / 4 skipped / 0 failed** after the mirror re-sync (the single transient failure was mirror drift introduced by the N1 fix, cleared by re-sync — not a logic defect). 25 dedicated floor tests. `validate_skills` / `validate_packaging` / `validate_packaging_committed` / `check_python_lengths` / `check_skill_ownership_overlap` all green; `plugins/` mirror in sync.
- **Fresh-eye implementation critique:** opus subagent (`a1052f6babb139f00`) — no blockers; found and I fixed **N1** (an order-dependent false refusal in `_parse_step` — it took the first step line; now it prefers the first *satisfying* line), with a regression test.

**Residual risk / non-claims:**
- The floors are **presence/binding-only** — they prove a step was *recorded*, never that the gather/release work was *good* (`Gather: pending` satisfies presence, same as every #253-family evidence line). Substance is the operator's / fresh-eye reviewer's call, by design.
- The release floor over-fires on a *mention* of a release token outside Coordination Cues (e.g., a deferred Off-Goal note); the one-line `Release: n/a — <reason>` opt-out is the intended, cheap escape. Accepted determinism cost over the not-clone-safe git-diff alternative.
- **No live / provider / release proof applies** — this is a deterministic library + template + docs change with no network / provider / live / release surface to exercise. Stated explicitly (not "skipped"), per the External-Or-Live plan.
- The bidirectional `/issue`–`/debug`-read-the-goal surface (critique C9) is **deferred** to its own effort, as planned.

## User Verification Instructions

1. **gather floor flags a missing gather step:** craft a goal with `Created: 2026-05-31`, an `https://…` line under `## Context Sources`, and a `## Coordination Cues` carrying no `Gather:` line; run `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path <file>` on a `Status: complete` copy → `ok:false`, the issues name "coordination floors: gather step missing". Add `Gather: n/a — <≥30-char reason>` → passes.
2. **release floor flags a missing release step:** same shape, but put a release token (e.g. `ran bump_version.py`) in the Slice Log and no `Release:` line → flagged; add `Release: n/a — <reason>` → passes.
3. **clean goal, no friction:** a `Created: 2026-05-31` goal with only local Context Sources and no release token flips `complete` with no floor friction.
4. **carrier:** `grep -n find-skills skills/public/achieve/scripts/goal_artifact_template.md` shows the routing cue; the carrier names no specific phase→skill mapping.
5. **suite + parity:** `python3 -m pytest tests/ -q` green; `python3 scripts/sync_root_plugin_manifests.py --repo-root .` then `git diff --stat plugins/ .claude-plugin/ .agents/plugins/` empty.

## Auto-Retro

_Pending: produced by `retro` at closeout next session; substantive findings narrated inline (not collapsed to a path)._
