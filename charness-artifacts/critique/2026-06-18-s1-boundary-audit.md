# S1 — Irreversible-Boundary Audit (North-Star Overhaul, Track 1a)

Status: **complete (read-only).** Produced by slice S1 of
`charness-artifacts/goals/2026-06-18-north-star-overhaul.md`.
Date: 2026-06-18.

## What this audit does

Classify **every irreversible boundary** in the harness as one of:

- **mandates-per-unit-verdict** — the closeout prose obliges a (fresh/distinct)
  observer to render a **per-unit *behavioral* verdict** ("did *this* unit's
  user-facing behavior actually happen?") through an **evidence channel distinct
  from** the proxy (gate-green / `CLOSED` / carrier-verified / ledger-recorded).
- **rubber-stamps-proxy** — the closeout disposition rests on an aggregate proxy
  (a passing gate, a `CLOSED` state, a carrier verified, "a critique ran", a
  state distinguished local/tag/public) **without** mandating a per-unit
  behavioral verdict through a distinct channel.

The discriminator is the **north-star contract** (`docs/design-north-star.md`
P4/P5) and the **Step-0 resolved finding**: the lever that flips catch 0.00 →
1.00 is a *per-unit behavioral-verdict mandate at the boundary*; the
distinct-channel demand is its automatic consequence.

### The trap this audit must not fall into

A boundary that already has heavy deterministic machinery
(`verify-closeout --expect-state CLOSED`, `publish_release.py --execute`'s
critique gate, slug-drift checkers) is **still rubber-stamps-proxy** if the
disposition rests on that machinery. The machinery confirms **FORM/STATE** —
which *is* the proxy. "There is already a gate here" is not "this boundary is
covered." Per north-star P5, a gate may *force a question*; it may not *declare
the behavior proven*. Only a per-unit behavioral verdict through a distinct
channel does that.

## The irreversible set (north-star "blast radius of a wrong pass")

Per `design-north-star.md`: **GitHub issue/PR close · release publish ·
external state writes (Slack/Notion/provider/apply-to-prod) · deletions.**
Audited by family below.

---

## Family 1 — GitHub issue / PR close

### COVERED (the model / #386 seed)

- **Achieve issue-bundle disposition review** —
  `skills/public/achieve/references/lifecycle.md` L666–687 (Rung-2).
  > "For **each** closed issue, the reviewer must confirm the issue's
  > user-facing behavior through an evidence channel **distinct from** the
  > bundle-level deployment readback and `CLOSED` state … **or** record an
  > explicit non-`verified` disposition. … Re-reading the readback or the
  > closeout evidence is not confirmation."
  - **Classification: mandates-per-unit-verdict.** ✅ This is the seed Track 1a
    generalizes. Cites P4 explicitly; forbids same-proxy re-read.
  - **Scope caveat (the reason a gap exists):** this mandate fires **only**
    "when the goal closes a tracked GitHub issue bundle that **touches
    HOTL/live behavior**" **and only inside an `achieve` goal.** Issue/PR
    closes outside `achieve`, and `achieve` bundles that do not touch live
    behavior, inherit nothing.

### GAP carriers (rubber-stamps-proxy) — same boundary, outside the seed's scope

- **(1a) Standalone `issue resolve` close** —
  `skills/public/issue/references/closeout-discipline.md` L52–104,
  `references/resolve-flow.md` L53–69, `issue/SKILL.md`.
  Disposition rests on `issue_tool.py verify-closeout --expect-state CLOSED`
  (re-reads GitHub **state** → the `CLOSED` proxy) + a `Critique: <path>`
  carrier header (a **presence/binding** gate proving a *recurrence-focused*
  critique ran). Neither is a per-issue **behavioral** verdict — "did each
  closed issue's user-facing behavior actually work, confirmed through a
  channel distinct from `CLOSED`?" is never mandated.
  - **Classification: rubber-stamps-proxy.** ⚠️ GAP. This is the literal #386
    shape one step outside `achieve` — and the primary issue-close path.

- **(1b) PR merge → shared history** —
  `issue/SKILL.md` L124–127, `resolve-flow.md` L53–60.
  > "before merge, preserve the keywords if the repository uses squash, rebase,
  > or edited merge commits … verify the final merge body still contains the
  > close keywords before treating the issue as closable."
  The merge propagates to **shared history others build on** (north-star:
  "enters shared history" = irreversible; "Reopenable ≠ reversible"). Yet the
  merge boundary is guarded only by **keyword-survival** (carrier proxy) +
  post-merge `CLOSED` (state proxy). No behavioral verdict at
  merge-to-shared-history.
  - **Classification: rubber-stamps-proxy.** ⚠️ GAP. The plan-critique B1
    blocker that elevated PR merge as under-scoped. **Trigger =
    merge-to-shared-history, not the tracker flip.** (Note: in this repo's
    dogfood the common carrier is direct-to-default commit, not PR merge; the
    boundary is the same and the gap is identical for both carriers.)

- **(1c) Release-linked issue close** —
  `release/SKILL.md` L120–121, L152–153.
  `--close-issue <number>` → preflight `gh issue view`, write keywords, verify
  GitHub state after push + public release, manual fallback. Confirms per-issue
  **`CLOSED` state** (proxy); no per-issue behavioral verdict through a distinct
  channel.
  - **Classification: rubber-stamps-proxy.** ⚠️ GAP. Same shape as (1a), via
    the release carrier. Explicit Track 1a target ("release-linked issue
    close").

---

## Family 2 — release publish

- **Release publish** — `release/SKILL.md` L75–119,
  `references/closeout-critique-gate.md` L10–27.
  Disposition rests on: `publish_release.py --execute` refusing without
  `--critique-artifact` / `--critique-blocked` (a critique-**ran** presence
  gate) + local-surface verify (version agreement, gates pass) + "distinguish
  `local/tag` vs `workflow` vs `public release surface verified`" (**STATE**
  distinction = proxy) + `check_real_host_proof.py` (may carry a release-time
  proof **checklist**, adapter-conditional) + `audit_public_release_narrative`.
  The release critique is framed as **aggregate release hygiene/readiness**
  ("`Critique: short`" for hygiene, "`Critique: full`" for compat/install/
  visibility) — **not** "for each shipped capability/change, confirm its
  behavior in the published surface through a distinct channel."
  - **Classification: rubber-stamps-proxy (with partial mitigation).** ⚠️ GAP.
    `check_real_host_proof.py`'s checklist is the closest existing partial
    cover, but it is an adapter-conditional **aggregate checklist**, not a
    **mandate** to render a per-unit behavioral verdict. Most-machinery,
    still-proxy — the canonical trap above.

---

## Family 3 — external state writes (Slack / Notion / provider / apply-to-prod)

### COVERED (sibling model)

- **HOTL ledger + proof-rules** —
  `skills/public/hotl/references/ledger-and-dispositions.md` L24–105,
  `references/proof-rules.md` L22–32.
  > "`verified` requires … `proof_artifact` … `proving_surface_refs` … provider
  > refs. … Deployment readback and a closed tracker state are not this audit …
  > a `verified` entry must cite the behavior channel that observed it, not the
  > bundle readback or `CLOSED` state it rode in on. An entry confirmed only by
  > re-reading that same proxy is not `verified` — that is the re-examination
  > failure that *P4* names." + "External mutation proof needs before/after
  > readback." Completion audit **blocks** unresolved entries.
  - **Classification: mandates-per-unit-verdict.** ✅ Per-entry behavioral
    verdict via provider readback; cites P4; already defers to the achieve
    disposition reviewer for issue-bundle closes. The second already-correct
    boundary.

### MOSTLY-COVERED (nuance, not a primary gap)

- **Announcement delivery (Slack/chat posts)** — `announcement/SKILL.md`
  L148–158. `preflight_sources.py` (unverified in-progress source → user
  confirm) + a **verified delivery ledger** (channel / thread / permalink /
  recorded head, read from the *actual delivery response* — a per-output,
  distinct-channel readback). For a one-way human-facing post the irreversible
  act *is* the post, and "posted to channel X / thread Y / permalink Z" is a
  reasonable behavioral readback.
  - **Classification: borderline → leans mandates (per-post delivery readback).**
    Residual nuance: it confirms **delivery occurred**, not that the post is
    correct or reaches the intended human (cf. proof-rules' "bot-authored smoke
    is not human-ingress proof"). **Low priority; not a primary gap.** A
    one-line sharpen *could* name the per-post verdict explicitly, but the
    existing delivery ledger is close to adequate.

---

## Family 4 — deletions

- **Rename/deletion critique** —
  `skills/public/critique/references/rename-critique.md` (whole file).
  Fresh-eye multi-angle critique (Raskin first-reader, Minto slug agreement,
  Gawande checklist) + four-bin triage (**Act Before Ship holds the PR**) +
  deterministic **slug-drift check** (`check_title_slug_drift.py`, advisory) +
  cite-validator allowlist + a **first-reader probe**.
  - **Classification: partial → leans rubber-stamps on the *behavioral* axis.**
    ⚠️ GAP (weakest). Strong machinery and a real fresh-eye review, but framed
    as **aggregate coherence** ("does *a* first reader hit a coherent model")
    + a checklist — not an explicit **per-deleted-unit** behavioral verdict
    ("for each removed concept / each dangling cite site, the downstream still
    behaves, confirmed through a distinct channel"). Mitigation: the
    slug-drift + cite-validator arguably *are* the distinct behavioral channel
    for deletion (a dangling cite *is* the behavioral failure). Existing
    machinery is closest-to-adequate of all the gaps.

---

## Gap list (ranked by leverage = blast-radius × current-coverage-deficit)

| # | Boundary | Family | Current disposition rests on | Why a gap |
| --- | --- | --- | --- | --- |
| G1 | **`issue resolve` / PR close (outside achieve)** | issue/PR close | `verify-closeout CLOSED` + recurrence critique | Literal #386 shape, primary close path; no per-issue behavioral verdict |
| G2 | **PR merge → shared history** | issue/PR close | keyword-survival + `CLOSED` | Highest blast radius (shared history); plan-B1 under-scoped; no behavioral verdict |
| G3 | **release publish** | release | critique-ran + state-distinguished + (adapter) host-proof checklist | Most machinery, still proxy; aggregate critique not per-unit verdict |
| G4 | **release-linked issue close** | issue/PR close | preflight + post-release `CLOSED` per issue | Same as G1 via release carrier |
| G5 | **deletions** | deletions | fresh-eye critique + slug-drift (aggregate coherence) | No explicit per-deleted-unit behavioral verdict; slug-drift partially covers |
| — | announcement delivery | external write | per-post delivery readback | **Not a primary gap** — delivery ledger ≈ distinct channel; nuance only |
| — | HOTL live behavior | external write | per-entry `verified` via provider readback | **Covered (model)** |
| — | achieve issue-bundle (HOTL-touching) | issue/PR close | per-issue distinct-channel confirmation | **Covered (seed/model)** |

### Recommended S2 target (the "single worst gap")

**G1 + G2 as one boundary** — *the GitHub issue/PR-close boundary in every
carrier outside the achieve seed* (standalone `issue resolve`, whether the
carrier is direct-to-default commit or PR merge-to-shared-history). Rationale:

- It is the **literal #386 mechanism** (aggregate sign-off after all-green +
  `CLOSED`) reproduced one step outside the seed's `achieve`-only scope.
- It is the **highest-frequency** irreversible close in this repo's dogfood
  **and** (via PR merge) the **highest blast radius** in the north-star's own
  "enters shared history" sense.
- The goal's named set leads with "PR **merge**/close"; folding G1+G2 matches
  how the goal frames the boundary ("PR merge/close" together) and lets one
  in-place sharpen cover both carriers of the same boundary.

S2 closes this one gap in-place (sharpen the issue-close closeout prose →
per-issue behavioral verdict through a channel distinct from `CLOSED`, cite
P4), then a bound fresh-eye critique confirms framing-not-gate. S3 sweeps G3
(release publish), G4 (release-linked close), and G5 (deletions) with the
validated pattern. (S2 target is **confirmable/overturnable** by the S2
fresh-eye reviewer; G2-PR-merge could be split out if the in-place sharpen
would duplicate the same paragraph across the two carriers — the goal's
≥3-boundary-duplication overturn guard.)

## Guardrail carried into S2/S3 (the B2 blocker — do not relapse to terminal green)

For **every** closed gap, the sharpened prose must **MANDATE the per-unit
question**, never **DECLARE a completion condition.** A formulation like
"confirm each unit via a distinct channel; **when all units are confirmed,
close**" re-creates the exact "all-green + `CLOSED` = behavior proven"
equivalence #386 named as root cause (the second clause is the relapse). The
per-boundary reviewer question for S2/S3, verbatim from the goal's
High-Confidence checks:

> Does the sharpened prose **DECLARE a completion condition** (BLOCKER) or only
> **MANDATE the per-unit behavioral question** (pass)?

No new gate, no new script, no new verdict token is added at any gap — these are
framing/task-structure prose changes at the decision point (north-star P5; the
#386 commit's "why no gate"). Adding an 8th deterministic floor over the agent's
own self-classification would re-grant the terminal green this overhaul exists to
remove.

## Non-claims

- **Not behaviorally re-validated.** This audit classifies by reasoning against
  the north-star contract + the Step-0 resolved finding; it did not re-run the
  C3b/C3c subagent harness at the new boundaries (optional, non-blocking per the
  goal's External-Or-Live Proof section). Δ≈0.9 makes the lever's transfer
  high-confidence, but the transfer to each new boundary is reviewer-confirmed,
  not behaviorally proven here.
- **Single read pass.** Surfaces were mapped by one fan-out sweep + direct reads
  of the eight operative files; a surface that closes an irreversible boundary
  through a path none of those touched would be missed. The four north-star
  families were each reached.
- **PR-merge carrier frequency.** This repo's dogfood closes mostly
  direct-to-default; the PR-merge carrier (G2) is real per the north-star but
  fires rarely here. The gap is identical across carriers, so this does not
  change the classification — only the dogfood exposure.
