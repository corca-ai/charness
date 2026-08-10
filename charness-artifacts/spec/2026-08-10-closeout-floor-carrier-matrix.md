# Spec: the closeout floor × classification matrix

Date: 2026-08-10
Issue: `#586`
Status: BUILT on 2026-08-10. The declaration is
[`.agents/closeout-floor-matrix.json`](../../.agents/closeout-floor-matrix.json);
the behavioral validator is `scripts/check_closeout_floor_matrix.py`. What the build
learned, and where it departed from this spec, is recorded under
[What the measurement found](#what-the-measurement-found) below. Nothing above that
section was rewritten — the plan is left as it was written so the delta is readable.

## Why this and not a scanner

`#586` ranked three candidate guards. All three mechanizable ones were measured on
2026-08-10 and every one has near-zero current findings:

| candidate | findings today | instances it would cover |
| --- | --- | --- |
| vocabulary parity across classification enumerations | **0** — all six values present in all five carriers | 1, 6 |
| declared-but-unread (name-reference scan) | 9 of 5,493 top-level functions (0.16%); the one read end to end was a superseded helper, not an inert check | 3 |
| fail-open optional guard (a `None`-default parameter gating a refusal, never passed in production) | **0** | 4, 5 |

Building any of them now means validating a guard against its own fixtures, which is
the failure the goal that filed `#586` recorded twice.

The one shape that keeps producing live findings is instance 2's: **a floor that
exists, is correct, and is wired to one carrier but not to the one the disposition
requires.** It recurred on 2026-08-10 at the policy layer, and a bounded review — not
a gate — caught it.

## The live finding this starts from

`evaluate_close_comment_floor` (`skills/public/issue/scripts/issue_close_comment_floor.py:105-115`)
composes six sub-checks: source preservation, behavioral verdict, HOTL dispositions,
AI-provenance, resolution critique, consolidation readback. **Each one's applicability
rule lives in a different module, and no surface states them together.**

The consequence, confirmed while closing `#514`/`#515`/`#518`: the `consolidated`
classification — the disposition built for won't-do closes — skips four of the six.
`issue_resolution_critique.CRITIQUE_REQUIRED_CLASSIFICATIONS` is
`("bug", "feature", "deferred-work")`, and `issue_verify_closeout_body.py:126,137-145`
states the skip in an **advisory that never blocks**. Reading five modules is currently
the only way to learn this.

Whether that skip is right is NOT this spec's question. That it is invisible is.

## What to build

### 1. The declared matrix

One artifact. Rows are floor ids; columns are `(classification, carrier)` pairs. Every
cell carries one of:

- `fires` — the floor contributes to the verdict for this pair;
- `skipped-by-design: <reason>` — deliberately not applied, with the reason that makes
  it deliberate;
- `not-applicable: <reason>` — the floor's own input cannot exist for this pair.

An empty or absent cell is a refusal, not a default.

Floors: `source_preservation`, `behavioral_verdict`, `hotl_dispositions`,
`ai_provenance`, `resolution_critique`, `consolidation_readback`, and the closeout
authorization probe. Classifications: the six in `issue_verify_closeout.CLASSIFICATIONS`.
Carriers: at minimum `commit-msg`, `close-with-comment`, `pr-body`, `direct-commit`,
`manual-fallback`, and the release family.

### 2. The validator, which must be BEHAVIORAL

**Do not grep.** For each `(floor, classification, carrier)`, call the real floor with
a fixture body constructed to fail that floor, and observe whether the failure reaches
the verdict. Compare the observation to the declaration; disagreement in either
direction refuses.

This is the load-bearing constraint of the whole slice. A grep- or import-based matrix
would itself be a check that never fires on the wired path — it would assert what the
code *says* rather than what the caller *gets*, which is the exact class `#586` names.
A matrix built the cheap way makes this issue worse, not better.

### 3. Exhaustiveness

The matrix must be total over `CLASSIFICATIONS × carriers`. A pair with no row refuses.

This is where the cheapest candidate returns as a side effect: adding a value to one
enumeration without adding its matrix rows fails, which is instance 1 and instance 6
without a bespoke parity scanner.

## Slice plan

1. **Declare, from observation.** Run each `(classification, carrier)` pair through the
   real floor with a deliberately-failing body and record which floors bit. Write the
   matrix from what was observed, not from reading the modules — reading is how the
   current five-module scatter stayed invisible.
2. **Build the validator** against that matrix. Expect it to refuse at first; the
   declaration written in step 1 is a measurement, and any disagreement is either a
   fixture bug or a real finding.
3. **Disposition each `skipped-by-design` cell.** The `consolidated` skips need a
   written reason or they need to change. This is where a real repair may fall out, and
   it is a separate decision from the matrix.
4. **Wire the validator into the quality run** and into `.agents/surfaces.json` as an
   owned surface with a real verify command.

## Fresh-eye obligation

This slice changes verdict logic on a proof surface, so it owes **two** bounded review
rounds — the second reading the repairs. Round 2 has caught a blocker on every measured
slice of this class in this repo, including twice on 2026-08-10.

## Non-goals and non-claims

- This does not cover `#586` instances 4 and 5 (a parameter default disarming a check
  on the wired path). Those measure 0 today; if the shape recurs, re-measure before
  building for it. `#586` therefore stays open after this slice.
- The matrix says where a floor RUNS. It says nothing about whether the floor is
  correct, and it must not be read as evidence that a running floor is a sufficient
  one.
- No consumer repo has been inspected. Every number above is from this tree on
  2026-08-10 and the scans behind them are heuristics whose limits are recorded in the
  `#586` comment of that date.

## What the measurement found

Measured 2026-08-10 by running all six carriers against a passing body and a
one-floor-broken body, 36 `(carrier, classification)` pairs.

### The spec's "skips four of six" was imprecise, and the precise version is worse

`consolidated` does not skip four floors uniformly. Three of them —
behavioral-verdict, HOTL, resolution-critique — are **input-refused**: the
disposition's repair-claim rule refuses any carrier that carries those lines, so the
floors' inputs cannot exist on a consolidated body.

That refusal is what the probe can see. As measured, it was **not** the only thing
holding: `consolidated` was also outside all three floors' own classification gates, so
they would have skipped the line even with the repair-claim rule removed. Round 2 caught
the first declaration presenting the visible half as the whole design. For
behavioral-verdict and resolution-critique the underlying skip has a sound reason (a
consolidation implements nothing). For HOTL it did not — which is the finding below,
and which the fix removed: HOTL now has no classification gate at all, so on a
consolidated body the repair-claim rule is the only thing holding. The declaration's
cells say so, and say it differently for HOTL than for its two siblings.

**Two floors are silently skipped where the input is accepted and ignored:
`AI-provenance` and `HOTL`, for `question` and `decision-needed` on all six
carriers.** Both are gated on `BEHAVIORAL_VERDICT_CLASSIFICATIONS`, and neither is a
fact about whether the close changes user-facing behavior. The line may be present —
including an explicitly undispositioned `HOTL:` entry, the exact shape that floor
exists to refuse — and nothing reads it. That includes `close-with-comment`, the only
carrier that writes to GitHub itself, and one of only two a `consolidated` close may
use (`manual-fallback` is the other; the remaining four refuse the disposition
outright). For `consolidated` itself, `AI-provenance` is the silent one; HOTL is
input-refused, with the same untransferred reason underneath.

Corroborating, **as measured on 2026-08-10 before the fix**: `issue_verify_closeout_body.py:116`
said a `question` close "silently bypasses two of the three floor checks", and its
advisory named only the behavioral-verdict and resolution-critique floors. The matrix
declares **five** non-firing floors for `question` on the five body carriers — the
module's own advisory undercounted, and two of the five had no justification at all.
(That file:line no longer exists: the floors moved to
`skills/public/issue/scripts/issue_closeout_rung1_floors.py` and the advisory was
rewritten with the fix below. The citation is preserved as the pre-fix observation it
was.)

Filed as [`#591`](https://github.com/corca-ai/charness/issues/591) and declared as 24
`undispositioned` cells (two more point at `#592`, below). The gate refuses an inert
cell carrying neither a reason nor a finding, so this cannot go quiet again.

**The HOTL half of this finding came from round-1 bounded review, not from the first
reading of the measurement.** The first declaration labelled those twelve cells
`skipped-by-design` with a reason — "no live HOTL loop to dispose" — that the probe's
own fixture falsifies, because the fixture presents an entry.

### The matrix caught its own surface changing

`#591` was then FIXED on operator decision, and the gate's first real test was the
change it was built to catch. Before re-declaring, the validator refused with exactly
26 findings — every `undispositioned` cell, each reading "declared 'undispositioned'
but the carrier observably 'fires' this floor". Nobody told it the floors had moved.

The fix removed both classification gates: `evaluate_hotl_dispositions` now relies on
the presence gate it always had, and `evaluate_ai_provenance` applies to every
classification. Blast radius was measured before building, not asserted: across 84
commit-msg closeout carriers in this repo's history plus the three consolidated closes
on the direct-write carrier, **every** light-classification carrier already carried the
marker voluntarily and **none** presented a HOTL entry — so the widened floors refuse
nothing that previously passed. The matrix now declares 134 `fires`, up from 108.

Two things fell out that only the fix could expose. The commit-msg carrier's pause-brief
path rewrote a floor-exempt classification to `feature` so the provenance check would run
at all — a workaround for exactly this gate, now deleted rather than left to outlive its
cause. And the floor-exemption advisory's pinned sentence, "(only source preservation
still applies)", had become false; byte-stability guards a carrier's output against
accidental drift, not against an advisory that misreports which floors ran.

The rung-1 floors moved to `issue_closeout_rung1_floors.py` when the body reader hit its
length gate. That seam was already named by the repo's own test file: one module answers
how a field is read out of markdown, the other what the body must carry and for which
classification.

Both bounded rounds found blockers again, and both were at the same place: not the
floors, but the surfaces that TELL an author what the floors want.

Round 1, found independently by both reviewers: the closeout-draft shape producer
rendered "AI-provenance (required for classifications: bug, feature, deferred-work)"
from the behavioral tuple, so an author drafting a light close would omit the marker
and be refused by the floor the same surface exists to keep them off. Round 2 then
found the repair had hand-typed the replacement clause in a module whose stated
contract is that it never restates a rule — the same drift, one level up. It now
renders that clause by OBSERVING the floor.

Round 2's own blocker: the commit-msg carrier folds the HOTL floor into its verdict and
rendered nothing for it, so an undispositioned entry blocked `git commit` with no line
naming HOTL or the remedy — on the one carrier that can block a commit, in the file
that already records repairing exactly this for its two sibling floors. Alongside it,
`close-with-comment` refused on `missing_ledger_fields` while printing only its header,
so an author following the new HOTL advice on a consolidated close walked from a
diagnosed refusal into an undiagnosed one. Both render now.

Two pre-existing defects the review surfaced are filed rather than folded in:
[`#593`](https://github.com/corca-ai/charness/issues/593) (the HOTL floor judges quoted
entries for issues the carrier is not closing) and
[`#594`](https://github.com/corca-ai/charness/issues/594) (the draft shape contradicts
the consolidated disposition it renders for). Round-2 repairs are recorded as
accepted-unreviewed per the two-round cap.

### A second live asymmetry, on the release lane

The release lane force-applies the behavioral-verdict floor to every classification
and leaves the resolution-critique floor exempt, in the same call. Its own stated
reason for the first — a released close is a shipped-item claim regardless of issue
type — applies to the second. Filed as
[`#592`](https://github.com/corca-ai/charness/issues/592); two cells declared
`undispositioned` against it.

Round 2 found those two cells carrying the generic light-close reason, refuted by the
`behavioral_verdict` cell one row above them in the same pair.

**DISPOSITIONED 2026-08-10 by operator ruling, and `#592` closed on it.** The two cells
are now `skipped-by-design` with a reason that confronts the neighbouring cell rather
than reusing the light-close reason. The ruling: the two floors differ in whether the
release operator can satisfy them at all. The behavioral floor is a presence check over
an input channel this lane already owns (`--close-issue-behavior`); the critique floor
demands a checked-in artifact bound to the issue and passing `validate_critique_artifacts`,
for classifications whose critique substrate never runs — so force-applying it would
demand evidence of a process that did not happen, and the predictable result is a stub
that satisfies the binding check. Non-claim carried in the cell: this leaves a
`question`/`decision-needed` release close with no fresh-eye review bound to it, which is
a real absence rather than a proven non-need. The durable record is **D55** in
[deferred-decisions.md](../../docs/deferred-decisions.md); the cells point at it, because
round-2 review caught that a ruling living only in a `reason` string the gate explicitly
does not check has no reader. That same round also refuted the reason's first wording:
`issue_resolution_critique.py:363` short-circuits before it looks rather than refusing,
so the artifact is unproduced, not impossible — D55 carries that as a non-claim.

### The matrix caught a live instance-2 defect on the release lane

Round-1 review found the release carrier probed one layer too low.
`preflight_release_issues` runs its **own** behavioral-verdict floor before the
issue-owned draft validation, over a separate input channel
(`--close-issue-behavior`, not the carrier body) and with a **fixed** classification
(`_RELEASE_BEHAVIORAL_CLASSIFICATION = "feature"`). So the release lane does not
exempt `question`/`decision-needed` — it is the one carrier where the light-close
exemption does not hold, and a real release close of either is refused.

Probed from below, those two cells read `skipped-by-design` with the reason "…and it
is the same reason on every carrier". That is `#586`'s instance 2 — a floor wired to
one carrier and not another — asserted **backwards**, inside the artifact built to
expose it. The probe now enters at `preflight_release_issues` and the cells read
`fires`. `tests/test_closeout_floor_matrix.py` pins the asymmetry directly.

Round 2 found the repair had bought a smaller version of the same defect twice more.
First, the probe derived `--close-issue-behavior` from the carrier body, coupling two
channels the lane keeps independent; because a `consolidated` body cannot carry a
`Behavior:` line, that emptied the CLI channel too and the declaration recorded the
probe artifact as a fact about the carrier. Second, the three heavy release cells kept
the classification reason when the release floor fires for every classification. Both
are repaired; the channel is now driven by which floor is being broken.

The move up has a real cost, now declared: the issue-owned behavioral floor is
**structurally shadowed** on this lane. Any input that would break it also empties the
release channel, which refuses first — so unwiring the downstream floor entirely moves
no release cell. That is a property of the lane, and `not_measured` says so.

### Departures from the plan above

- **`closeout_authorization` is not a matrix row.** Its protected-target crosswalk
  instance was RETIRED by operator ruling on the same day, so no probe can make it
  fire without rebuilding the artifact that ruling retired. A row that can never fire
  is the shape `#586` exists to remove. It is named in the artifact's `not_measured`
  instead.
- **Two more cell states were added: `undispositioned` and `input-refused`.** The
  spec's three all assert a judgment, and there was no way to declare "inert, and
  nobody has justified it" — without `undispositioned` the two silent skips would
  have had to be mislabelled `skipped-by-design`, which is the advisory-shaped
  silence the spec objects to. `input-refused` exists because round 1 found
  `not-applicable` admitting two different observations, which made the six cells
  carrying the consolidated finding self-confirming: drop `hotl` from
  `issue_consolidated_closeout._TARGETED_CLAIM_NAMES` and those cells slide
  `input-refused → inert` — a brand-new silent skip on the direct-write carrier —
  with the gate still green and the cells' own "measured, not assumed" reason now
  false. Every state now pins exactly one observation.
- **`fires` means THIS floor refused, not that the carrier refused.** The first
  version attributed any refusal of a one-floor-broken body to that floor, so a floor
  could be unwired entirely and still read `fires` if any other check happened to
  refuse the same body. An unattributable refusal is now `refused-elsewhere`, which no
  declared state accepts.
- **Pair-level refusal is declared separately from cells.** Four carriers refuse
  `consolidated` outright, so no floor there is observable. Declaring per-floor
  `not-applicable` on those pairs would have implied the pair runs.
- **Step 1 did not refuse at first, and could not have.** The declaration was
  GENERATED from the first measurement, so it agreed by construction. Its teeth are
  entirely on the next change; `tests/test_closeout_floor_matrix.py` pins that the
  probe moves when a floor's classification gate moves, in-process and through the
  CLI on a repo copy.
- **`commit-msg` is probed on its bare close-keyword path only.** Its
  staged-artifact and pause-brief paths are named as unmeasured in the artifact.
- **Step 3's "disposition each cell" did not resolve the skips, and should not have.**
  Widening either floor newly refuses close bodies that pass today, at an
  irreversible boundary. The slice files and declares; `#591` decides.
- **One instance-2 case is named as unmeasured rather than declared.**
  `evaluate_close_comment_floor` applies `_missing_ledger_fields` only to
  `consolidated` while `verify_closeout` applies it to every classification — named as
  deliberate restraint in a module docstring nobody reads. It is not a row here, and
  the artifact's `not_measured` says so, because a green gate over 36 pairs must not
  be read as covering it.

AI-provenance: authored by an agent session.
