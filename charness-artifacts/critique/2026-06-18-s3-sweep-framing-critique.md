# S3 — Fresh-Eye Critique: Track 1a sweep (release publish, release-linked close, deletion)

Status: **PASS (no blockers, no folds).** Bound by slice S3 of
`charness-artifacts/goals/2026-06-18-north-star-overhaul.md`. Date: 2026-06-18.

Reviewer provenance: one bounded fresh-eye subagent (read-only, shared parent
worktree; prior versions via `git show HEAD:<path>`, no index/worktree mutation),
per the CLAUDE.md subagent-delegation contract.

## Slice review packet

- **Intent:** generalize the S2-validated per-unit behavioral-verdict framing to
  the remaining S1 gaps — **G3** release publish, **G4** release-linked issue
  close, **G5** deletion. Framing/prose only; no new gate/script/token (P5).
- **Changed surfaces:**
  - `skills/public/release/SKILL.md` — step 7: consolidated three redundant
    state-distinction bullets into one P4-framed per-surface behavioral-verdict
    bullet (G3); guardrail: added the per-issue behavioral-verdict pointer to
    `issue/references/closeout-discipline.md` (G4). Net +2 lines; landed 199/200.
  - `skills/public/critique/references/rename-critique.md` — new
    "## Per-Removed-Concept Verdict (deletion is an irreversible boundary)"
    section (G5).
  - `plugins/charness/...` mirror (synced, byte-match).
  - `docs/public-skill-dogfood.json` — scenario-review freeze for `critique` and
    `release` (hitl-recommended tier; planner `next_action: none` → no Cautilus
    eval; acked).
- **Design decision under review:** kept **in-place** per-boundary instantiation
  (not a shared-ref hoist), the operator's resolved method — to be tested against
  the ≥3-boundary-duplication overturn rule.

## Reviewer verdict (summary)

**Overall: PASS, no folds.** Per-question:

- **Q1 declares-vs-mandates — PASS (G3, G4, G5).** Each surface mandates the
  per-unit *verdict-or-disposition* and explicitly denies the aggregate
  terminal-green: G3 "tag push or helper success alone is never completion"; G4
  "`status: verified` is the CLOSED state, not behavior proof"; G5 "a per-concept
  question to render, never a 'cites look updated, ship it' aggregate sign-off".
- **Q2 smuggled gate / new token — PASS.** Purely framing; pre-existing checks
  (`publish_release.py` critique gate, `verify-closeout`,
  `check_title_slug_drift.py`) referenced in their existing roles, never
  repurposed as the behavioral proof. G5 even guards "a slug-drift run … you do
  not actually read back is not this verdict".
- **Q3 safeguard preserved + not a cap-dodge — PASS.** All three consolidated
  concepts survive; the strongest (four-state non-interchangeability) is intact
  and unchanged in guardrails L158-159. The consolidation is **net +2 lines** at
  the site — it *consumed* headroom, so it is concept-merge (P2-sanctioned), not
  a line-shave-to-dodge-the-cap (P2 violation).
- **Q4 distinct channel + observer (P4) — PASS.** G3 names fresh-checkout /
  real-host smoke / install-refresh readback distinct from tag/version state
  (verified present in step 6); G5 names slug-drift output / validator allowlist /
  first-reader probe distinct from the editor's own pass. P4 citations accurate.
- **Q5 orthogonality / duplication — IN-PLACE JUSTIFIED (do not hoist).** Each
  instantiation differs on every filled axis — unit, proxy, distinct channel,
  disposition vocabulary, observer (the reviewer tabulated all five). The shared
  *pattern* repeats but the *paragraphs* do not, so the goal's ≥3-boundary
  "same paragraph" overturn rule is **not** triggered. Hoisting would force a
  generic template + re-localization, losing the at-point-of-use concreteness P3
  prefers.

## Over-worries (raised, not folded)

- release/SKILL.md at 199/200 is tight, but S3 net-added here rather than shaving;
  pre-existing pressure, **a Track-2 (S5) slim candidate**, not an S3 violation.
- G3's distinct *observer* leans on the pre-existing release critique gate rather
  than naming a new observer in the bullet — consistent with framing-only and the
  S1 gap being channel-distinctness for release; not a fold.
- Optional future refinement (defer): a one-line cross-link in the shared
  `closeout-discipline.md` naming the pattern + pointing to the per-boundary
  instantiations, if a 4th–5th boundary lands. Recorded as a Track-2 candidate.

## Relocation + re-verification (post-critique)

After the PASS above, the `check-skill-core-headroom` ratchet gate (a `>=4`-line
core-headroom buffer that blocks a *regressing* change) forced the G3 release
detail out of the capped `release/SKILL.md` body. The detail was **relocated** to
the release-owned reference `references/install-surface.md` "Publication Closure
Boundary" (which already owned the three-state distinction and names the
channels), with a **terse salient in-body pointer** kept at SKILL.md step 7 (the
operative directive "render `public release surface verified` as a per-surface
behavioral verdict, not tag/version state" stays in-body; the reference holds the
channels + disposition vocabulary). A redundant step-6 line ("distinguish
local/tag success from later workflow or public verification") was removed as a
third copy of the same concept. release/SKILL.md core dropped 199 → 193 (headroom
3 → 7).

**Re-verified by the same fresh-eye reviewer (read-only) — PASS, no folds:**
- Q1 declares-vs-mandates: PASS, *strengthened* — the relocated text makes the
  per-surface iteration explicit ("for each operator-facing surface the release
  touched") and still denies the aggregate ("never a 'tag pushed, ship it'
  aggregate sign-off to declare"; "Re-reading the tag/version state is not this
  verdict").
- Q3 safeguard preserved: PASS — the three-state distinction survives in
  `install-surface.md` L70-74 *and* guardrail L152-153 (verbatim, unchanged); the
  removed step-6 line was a redundant third copy; the channel set is intact and
  better co-located. A legitimate P2 concept-relocation that *created* headroom,
  not a cap-dodge.
- Salience: PASS — the operative directive is in-body at the close step; the
  pointer is named (file + section); reinforced by guardrail L152-153 and the
  `Public Release Verification` Output Shape field.

## Disposition

PASS with no folds (including the relocation re-verification). Track 1a is
complete: every irreversible boundary in the S1
audit now demands a per-unit behavioral verdict through a distinct channel
(issue/PR close S2; release publish, release-linked close, deletion S3; achieve
issue-bundle + HOTL pre-existing), as prose at the decision point, with no gate,
token, or lost safeguard. The in-place method is validated as orthogonal
(boundary-specific instantiation of P4), with the shared-ref hoist recorded as an
optional Track-2 consolidation candidate.
