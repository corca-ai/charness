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

That refusal is what the probe can see. It is **not** the only thing holding:
`consolidated` is also outside all three floors' own classification gates, so they
would skip the line even with the repair-claim rule removed. Round 2 caught the first
declaration presenting the visible half as the whole design. For behavioral-verdict
and resolution-critique the underlying skip has a sound reason (a consolidation
implements nothing). For HOTL it does not — which is the finding below.

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

Corroborating: `issue_verify_closeout_body.py:116` says a `question` close "silently
bypasses two of the three floor checks", and its advisory names only the
behavioral-verdict and resolution-critique floors. The matrix declares **five**
non-firing floors for `question` on the five body carriers — the module's own advisory
undercounts, and two of the five have no justification at all.

Filed as [`#591`](https://github.com/corca-ai/charness/issues/591) and declared as 24
`undispositioned` cells (two more point at `#592`, below). The gate refuses an inert
cell carrying neither a reason nor a finding, so this cannot go quiet again.

**The HOTL half of this finding came from round-1 bounded review, not from the first
reading of the measurement.** The first declaration labelled those twelve cells
`skipped-by-design` with a reason — "no live HOTL loop to dispose" — that the probe's
own fixture falsifies, because the fixture presents an entry.

### A second live asymmetry, on the release lane

The release lane force-applies the behavioral-verdict floor to every classification
and leaves the resolution-critique floor exempt, in the same call. Its own stated
reason for the first — a released close is a shipped-item claim regardless of issue
type — applies to the second. Filed as
[`#592`](https://github.com/corca-ai/charness/issues/592); two cells declared
`undispositioned` against it.

Round 2 found those two cells carrying the generic light-close reason, refuted by the
`behavioral_verdict` cell one row above them in the same pair.

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
