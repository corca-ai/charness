# Achieve Goal: #405 — add Verification-channel fitness + Guard-propagation-across-seams to quality-lenses.md, and a distinct-named-lens delegation note to fresh-eye-subagent-review.md

Status: complete
Created: 2026-06-28
Activation: `/goal @charness-artifacts/goals/2026-06-28-issue-405-405-add-verification-channel-fitness-guard-propagation-acros.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 1 — add `Verification-channel fitness` + `Guard-propagation
  across seams` bullets to the `quality-lenses.md` Behavior lens, and a
  distinct-named-lens delegation note to `fresh-eye-subagent-review.md`. One
  coherent reference-prose slice (single risk class: skill-reference prose).
- Mode: implementation-continuation. The operator activated via `/goal` with an
  active Stop hook; the directive is to pursue, not draft-and-stop. Shaping runs
  now in this `/achieve` pass; execution follows in the same session.
- Next action: COMPLETE. Edits + mirror landed, slice closeout green, two
  distinct-named-lens fresh-eye reviews clean, retro + host-log probe + rung-2
  disposition review written, status flipped to `complete`, closeout committed
  with `Close #405` + ledger. Carrier is staged, not pushed — the maintainer's
  push closes #405.
- Verification cadence: cheap deterministic gates at the commit boundary via
  `run_slice_closeout.py` (structural sweep, ruff, lengths, markdown,
  mirror-drift, `validate_skills`, `check_doc_links`); fresh-eye critique at the
  slice boundary. No broad pytest (docs-only; no Python or test change) and no
  external/live proof.
- Slice review packet: slice intent; the two source diffs + their regenerated
  `plugins/` mirrors; expected invariant (provider-neutral wording — no host- or
  tool-brand name); mirror-sync requirement; out-of-scope lines (no new
  top-level lens; no files beyond the two named; the Guard-propagation lens text
  must not itself license scope creep beyond the two files).
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

#405 — add Verification-channel fitness + Guard-propagation-across-seams to quality-lenses.md, and a distinct-named-lens delegation note to fresh-eye-subagent-review.md

**Source handoff entry #2: #405: quality/critique lenses miss two failure modes: verification-channel fitness & guard-propagation across seams**

> ## Context
>
> A `quality`/critique fresh-eye pass on a downstream repo (a SvelteKit static blog) shipped two bugs that the lenses, as written, don't prompt for. Both survived a bounded fresh-eye review.
>
> 1. **Charset omitted on a prerendered `.txt` asset** → non-ASCII (Korean) text rendered as mojibake in browsers. It was "runtime-verified" via terminal `curl` — but a UTF-8 terminal *structurally cannot exhibit* a charset bug (it decodes UTF-8 regardless of the HTTP `charset`). The fresh-eye reviewer looked right at the `content-type: text/plain` line and explicitly marked it a NICE non-issue.
> 2. **Bracket-bearing titles broke markdown link text** in a machine-read index file (`[…]` category prefixes closing the link text early on lenient parsers). The author had applied the *analogous* escaping at a **sibling** injection point (JSON-LD `<`→`<`) the same turn, but did not propagate it.
>
> ## Pattern
>
> Errors cluster at **seams** — where two systems with different rules meet (corpus text → markdown / JSON-LD / HTML; endpoint `Response` → deployed static-asset header). The recurring shape:
> - a known guard applied at the **salient** crossing and **not propagated** to sibling crossings of the same hazard class; and
> - a runtime "proof" collected in a **channel that cannot exhibit** the failure under review.
>
> The current `quality-lenses.md` Behavior lens has "behavior-facing assertions / failure-path confidence / low-signal or gameable checks," and the "Runtime proof over presence" idea is widely used — but neither names *channel fitness* or *guard propagation*, so both misses passed.
>
> ## Proposed changes
>
> 1. **`plugins/charness/skills/quality/references/quality-lenses.md`** — Behavior lens, add:
>    - **Verification-channel fitness**: a runtime proof must be collected in a channel that can actually *exhibit* the failure mode under review (charset/encoding/rendering bugs are invisible to a UTF-8 terminal — fetch in a charset-respecting client / render as a user would). Read each response field — status / content-type / **charset** / cache — against the spec; don't pattern-match "looks right."
>    - **Guard-propagation across seams**: when a fix escapes/guards/converts/sets-a-header at one boundary crossing, enumerate *every* sibling crossing of that hazard class in the same diff and apply it as an invariant, not a local patch.
> 2. **`plugins/charness/shared/references/fresh-eye-subagent-review.md`** (or the `quality` workflow that assigns reviewer scopes) — add a delegation-design note: assign reviewers **distinct, explicitly-named lenses** (e.g. encoding/i18n vs injection/escaping) rather than N generic reviewers. Empirically, the generic reviewer here shared the author's framing blind spot — it caught the bracket bug but missed the charset bug. Lens diversity catches failure modes redundancy can't (this mirrors the existing "perspective-diverse verify" idea, applied to review lens assignment).
>
> ## Provenance
>
> Incident in a downstream private repo; the same lesson was also encoded there as a local standing review lens. Happy to provide the exact before/after diffs if useful.

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not absorb adjacent handoff entries beyond the selected chunk.

## Boundaries

- In scope: `charset/encoding/`, `escapes/guards/converts/`, `plugins/charness/shared/references/fresh-eye-subagent-review.md`, `plugins/charness/skills/quality/references/quality-lenses.md`
- Portable per implementation-discipline: no host-specific assumption.
- Stop conditions: name on first discovery; do not guess.

## User Acceptance

What the user can do to verify completion directly:

- Open `skills/public/quality/references/quality-lenses.md`, find the Behavior
  lens, and read two new named bullets — **Verification-channel fitness** and
  **Guard-propagation across seams** — each capturing the failure mode the issue
  describes (a runtime proof collected in a channel that cannot exhibit the bug;
  a guard applied at the salient crossing but not propagated to sibling
  crossings of the same hazard class).
- Open `skills/shared/references/fresh-eye-subagent-review.md` and read a new
  delegation-design note prescribing **distinct, explicitly-named reviewer
  lenses** (e.g. encoding/i18n vs injection/escaping) instead of N generic
  reviewers, with the lens-diversity rationale.
- Confirm both `plugins/` mirrors match their sources:
  `diff skills/public/quality/references/quality-lenses.md plugins/charness/skills/quality/references/quality-lenses.md`
  and the `fresh-eye-subagent-review.md` pair are byte-clean.
- Confirm the wording is provider-neutral: no host name, no tool brand
  (`curl`/browser product), no model name in the new prose.
- On the maintainer side, `gh issue view 405` shows the closing commit
  referencing `Close #405` once the carrier is pushed (staged at `achieve`
  closeout; the issue is still OPEN until the maintainer pushes).

## Agent Verification Plan

### Low-Cost Checks

- Read back the edited Behavior-lens bullets and the new delegation note.
- `diff` source vs `plugins/` mirror clean for both files after
  `sync_root_plugin_manifests.py`.
- Grep the new prose for banned-by-portability tokens (tool brands, model
  names, host names) to enforce provider-neutral wording.

### High-Confidence Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  green: structural sweep, ruff, `check_python_lengths`, markdown gates,
  `check_staged_mirror_drift`, `validate_skills`, `check_doc_links`.
- Bounded fresh-eye slice critique on the slice packet (risk class:
  prompt/skill-surface reference prose). Per the new Guard-propagation lens, the
  reviewer also checks the change was propagated to the mirror sibling and that
  no other in-scope sibling crossing was silently skipped.

### External Or Live Proof

- None. The originating incident lives in a downstream private repo (a SvelteKit
  static blog); its charset/bracket bugs cannot and will not be reproduced here.
  Recorded as an explicit non-claim — this goal proves the *doctrine edits land
  and pass repo gates*, not that they would have caught that specific downstream
  incident.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Add `Verification-channel fitness` + `Guard-propagation across seams` to the `quality-lenses.md` Behavior lens (2 bullets) and a distinct-named-lens delegation note to `fresh-eye-subagent-review.md` (1 note); regenerate + stage the `plugins/` mirror | Sole deliverable of #405; both edits share one risk class (skill-reference prose), so one critique boundary covers them | Both source files edited; mirror byte-clean; `run_slice_closeout.py --skip-broad-pytest` green; bounded fresh-eye critique pass | planned |
| 2 | Closeout: fresh-eye disposition review, retro, host-log probe, commit with `Close #405`, handoff refresh | Required closeout for task-completing repo work that resolves a tracked issue | `check_goal_artifact.py` passes; commit carries closeout ledger + `Close #405` | planned |

## Operator Decision Queue

- none — the only external action is the maintainer's push of the `Close #405`
  carrier to the default branch, a routine publication surface (not a queued
  operator decision); `achieve` does not push.

## Coordination Cues

Routing for each phase is deferred to `find-skills`' recommendation engine, not
an inline map. Evidence lines are filled at closeout (presence-only floors).

- Routing: find-skills → impl for the two reference-file edits (the only implementation work this run).
- Routing: find-skills → quality owns the lens content plus the public-skill scenario/validation review for this slice.
- Routing: find-skills → issue stages the #405 closeout carrier on the commit body.
- Gather: n/a — Context Sources name only the in-repo handoff entry and issue
  #405; no external `http(s)://` URL was used as a source.
- Release: n/a — docs-only reference change; no version bump, no install
  manifest or `marketplace.json` edit.
- Issue closeout: `Close #405` staged via `issue` on the closeout commit body
  with the resolution ledger; the maintainer's push to default branch closes the
  issue (still OPEN at `achieve` closeout).

Discuss before activation: resolved — the operator activated via `/goal` this
session and directed immediate pursuit. The surfaced consequential triggers are
benign for a docs-only reference change: (1) issue #405 close is *staged*
(`Close #405` on the closeout commit), never pushed or closed by this run — the
maintainer's push closes it; (2) the only non-claim is that the downstream
private-repo incident (a SvelteKit static blog) cannot be reproduced here, which
does not weaken the deliverable's local proof (the doctrine edits land and pass
repo gates); (3) no production/live proof, no broad bundled scope, and no
irreversible side effect are performed by this run. Several triggers fired on
prose that *describes* these as not-applicable; none names a real
operator-blocking decision.

## Slice Log

### Slice 1: Add the three lens entries + sync mirror

- Objective: Add verification-channel-fitness + guard-propagation-across-seams bullets to the quality-lenses.md Behavior lens, and a Distinct Named Lenses delegation note to fresh-eye-subagent-review.md; regenerate + stage the plugins mirror
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: run_slice_closeout.py --skip-broad-pytest structural-sweep PASS; mirror diffs byte-clean; provider-neutral grep clean (no tool/host/model token). Public-skill validation review (scenario_review, quality hitl-recommended): routed via plan_cautilus_proof (next_action=none -> cautilus NOT run, deterministic gates own closeout) + suggest_public_skill_dogfood; decision: quality consumer contract in docs/public-skill-dogfood.json is unchanged (additive doctrine, no routing/artifact/tier/acceptance-evidence delta). Scenario-review substance done via TWO distinct-named-lens fresh-eye reviewers (portability/house-style/scope + doctrine-fidelity), both verdict=clean, parent-delegated.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

- Source: handoff entry #2 (#405: quality/critique lenses miss two failure modes: verification-channel fitness & guard-propagation across seams) — see [docs/handoff.md](../../docs/handoff.md).
- Cited path: `charset/encoding/`
- Cited path: `escapes/guards/converts/`
- Cited path: `plugins/charness/shared/references/fresh-eye-subagent-review.md`
- Cited path: `plugins/charness/skills/quality/references/quality-lenses.md`
- Cited issue: #405

## Interview Decisions

No live user interview was run: the operator activated via `/goal` with an active
Stop hook directing immediate pursuit ("do not pause to ask"). Decisions below
are the assumed defaults, each with an anti-anchoring record.

- Mode (artifact-only vs implementation-continuation): chose
  **implementation-continuation**. The `/goal` activation + active Stop hook is
  the operator's explicit pursue action. single-point: this is the operator's
  expressed action this session, not a system axis.
- Slice granularity (one slice vs one-per-file): chose **one coherent slice**.
  Both edits are the same risk class (skill-reference prose), so one fresh-eye
  critique boundary covers them; per-file slices would double critique for no new
  risk class. single-point: granularity follows risk class, not a varying axis.
- Lens placement in `quality-lenses.md` (new top-level lens vs Behavior-lens
  bullets): chose **Behavior-lens bullets**. The issue explicitly says "Behavior
  lens, add"; the existing lens already owns "behavior-facing assertions /
  failure-path confidence / low-signal or gameable checks," which is the right
  neighbor. single-point: dictated by the issue, not an axis.
- Delegation-note placement in `fresh-eye-subagent-review.md` (nested subsection
  vs peer section vs inline in Reviewer Tier): landed as a **new peer `##
  Distinct Named Lenses` section immediately after Delegation Context** (lens
  assignment is a delegation-design concern; a peer section reads cleaner than a
  nested `###`, confirmed by the fidelity fresh-eye reviewer). single-point.
- Wording portability: the lens text must be **provider/host/tool-neutral** —
  "a charset-respecting client / render as a user would," never `curl` or a
  browser brand. axis: portability (the repo varies on host/provider); the
  doctrine itself is uniform across hosts, so it is written host-neutral rather
  than pinned to one host's tool.

## Plan Critique Findings

Lightweight self plan-critique at shaping; the substantive review is the
mandatory bounded fresh-eye slice critique at the slice boundary (prompt/skill
-surface risk class).

- Blocker folded → Verification cadence + Slice Plan: the `plugins/` mirror must
  be regenerated (`sync_root_plugin_manifests.py`) and staged; otherwise
  `check_staged_mirror_drift` blocks the commit. Made an explicit step.
- Blocker folded → Boundaries (portability): the new prose must stay
  provider-neutral. A naive draft would write "fetch with `curl --…`" — the exact
  channel-fitness trap the lens warns against, and a host-anchoring violation.
- Blocker folded → Boundaries (scope discipline): the Guard-propagation lens text
  ("enumerate *every* sibling crossing") could tempt this very edit to sprawl
  into other skill files. Boundaries cap scope to the two named files; any other
  sibling surface that genuinely needs the lens is filed as an off-goal finding,
  not silently expanded (stop condition: name on first discovery, do not guess).
- Over-worry raised, not folded: whether the two additions warrant a structural
  restructure of the Behavior lens. Rejected — the issue scopes them as two
  bullets in the existing list; restructuring is out of scope.
- Reviewer provenance: self at shaping (this section). Fresh-eye reviewer assigned
  at the slice boundary; per the lens-diversity note being added, that reviewer is
  given an explicitly-named lens (skill-surface portability + guard-propagation),
  dogfooding the change.

Activation discussion: resolved above — see the `Discuss before activation:`
summary placed before `## Slice Log` (the consequential triggers are benign for
a docs-only change; nothing names a real operator-blocking decision).

## Off-Goal Findings

- Pre-existing uncommitted churn in `charness-artifacts/find-skills/latest.json`
  and `latest.md` (a prior session's inventory refresh: date 2026-06-25 →
  2026-06-27, support-skills count 7 → 4). Out of scope for #405 and deliberately
  left unstaged so the #405 closeout commit stays scoped. Operator follow-up:
  commit it as a separate inventory-refresh change or re-run `find-skills`
  `--write-artifact`. Not filed as a tracked issue (routine current-pointer
  drift, not a defect).

## Final Verification

Self-verification against the goal: both deliverables landed.
`skills/public/quality/references/quality-lenses.md` Behavior lens now carries
`verification-channel fitness` and `guard-propagation across seams`;
`skills/shared/references/fresh-eye-subagent-review.md` carries the new
`## Distinct Named Lenses` delegation note. Both `plugins/` mirrors are byte-clean
against source. Wording is tool/host/model-neutral (grep clean).

Final quality gate: `run_slice_closeout.py --skip-broad-pytest
--ack-cautilus-skill-review` → `status: completed`; all verify gates PASS
(packaging, packaging-committed, doc links, command docs, markdown, secrets,
cautilus-proof + diagnostics, `validate_skills`, py_compile, skill-ownership,
skill-ergonomics, public-skill validation, public-skill dogfood, agent-browser
guard). No broad pytest: the change is reference-prose only — no Python or test
file changed, so the unit suite covers nothing new (recorded non-claim, not a
skipped obligation).

High-confidence / external proof: none run, and none applicable. The originating
incident is in a downstream private repo and is not reproducible here (recorded
non-claim). The deliverable is doctrine prose, fully verified by local file
inspection + deterministic gates + two distinct-named-lens fresh-eye reviews.

Public-skill validation review: Cautilus `next_action: none` (ask-before-run; not
invoked — deterministic gates own closeout). Scenario-review substance: two
parent-delegated bounded fresh-eye reviewers with distinct named lenses
(portability/house-style/scope + doctrine-fidelity), both `verdict: clean`. The
`quality` consumer contract in `docs/public-skill-dogfood.json` is unchanged
(additive doctrine; no routing/artifact/tier/acceptance-evidence delta).

Closeout state (standalone goal): reached `impl-local` (edits + all deterministic
gates green) and `carrier` (closeout commit staged with `Close #405` + resolution
ledger). NOT reached and recorded as explicit non-claims: `pushed-ci` (no push —
`achieve` does not push), `instance-synced` / `live` (n/a — docs change, no
runtime), `issue-closed` (#405 is still OPEN; the maintainer's push of the carrier
closes it). The rung-2 review classified #405 `local-only-by-contract` — a
docs/reference deliverable with no provider/connector behavior owed.

Retro: charness-artifacts/retro/2026-06-28-issue-405-405-quality-lens-guard-propagation-retro.md
Host log probe: charness-artifacts/probe/2026-06-28-issue-405-405-add-verification-channel-fitness-guard-propagation-acros.json
Disposition review: charness-artifacts/critique/2026-06-28-issue-405-405-disposition-review.md

## User Verification Instructions

- Read `skills/public/quality/references/quality-lenses.md` → `## Behavior`:
  confirm the `verification-channel fitness` and `guard-propagation across seams`
  bullets read faithfully and stay tool/host-neutral.
- Read `skills/shared/references/fresh-eye-subagent-review.md` →
  `## Distinct Named Lenses`: confirm the distinct-named-lens delegation guidance
  and its lens-diversity rationale.
- Run `diff skills/public/quality/references/quality-lenses.md plugins/charness/skills/quality/references/quality-lenses.md`
  and the `fresh-eye-subagent-review.md` pair — both must be byte-clean.
- After the maintainer pushes the carrier, `gh issue view 405` should show #405
  CLOSED with the commit referencing `Close #405`.

## Auto-Retro

Retro: charness-artifacts/retro/2026-06-28-issue-405-405-quality-lens-guard-propagation-retro.md

Per-improvement dispositions, mirroring the cited retro's `## Next Improvements`:

- Retro dispositions: out-of-scope: a Before-phase describe-first preflight is
  separate achieve-tooling larger than this docs goal, and `--pursue-ready`
  already names the exact gap, so the friction is one self-correcting cycle, not
  a recurrence warranting a new tool in this run.
- Retro dispositions: applied: the two Behavior-lens entries plus the
  `## Distinct Named Lenses` note landed in the public `quality` skill reference
  and the shared fresh-eye reference (mirrored to `plugins/`), so
  charness-consuming repos inherit the doctrine, not just charness.
- Structural follow-up: none — the `check_staged_mirror_drift` pre-commit gate
  already guards the mirror sibling crossing the retro's Sibling Search names;
  this run applied that standing guard and adds no new floor.
