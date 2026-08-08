# Open-Issue Opinion — the open backlog, grouped by the decision each needs
Date: 2026-08-08

## What this file is, and is not

This is an OPINION file. It is one session's view of the open backlog, written so
the next session can argue with something concrete instead of re-deriving it. It is
not a plan, and it carries no authority — where it says "opinion", the reasoning is
mine and the operator should overrule it freely.

It is grounded in a 7-day value audit run on 2026-08-08 (449 commits, 70 closed
issues, 12 agents). **The audit's headline thesis — that this repo had been
improving itself rather than its users — was mostly REFUTED**, and this file must
not inherit that dead premise. What broke:

- critique growth was dominated by machine-generated packet pairs; the `critique`
  SKILL barely moved
- `skills/public` growth was `achieve`/`issue`, the skills consumer repos use most
- the length floors are `MIN_OPTOUT_REASON` on escape hatches only, never on real
  values
- every new `scripts/` file ships to consumers, a large minority referenced by
  `skills/public`

Re-measure any figure below with the command beside it rather than trusting it.

**What survived is one instruction:** the work drifted after `#516` from consumer
defects to internal proof surfaces, and the next pick should be consumer-facing.
That is a prioritization finding, not a cleanup mandate.

## The reference repo: `../craken-agents`, for awiki and gardening

`../craken-agents` (HEAD `4c49c96d`) is a TypeScript product repo and does **NOT**
install charness (`grep -rl charness ../craken-agents` → 0 outside `node_modules`).
It is a sibling shape comparison, not consumer evidence. The operator named the
specific thing to learn: **its awiki usage and doc gardening.** Three transferable
patterns, read from its own files:

1. **Docs checked as a GRAPH, not a set of files.** `package.json` has
   `"docs:lint": "awiki lint -root docs"`, and `docs/documentation.md` states the
   invariant: it "fails on orphan pages and disconnected components, so a new page
   needs a link from `docs/index.md` and from at least one sibling page in body
   prose." charness has `check_doc_links.py` for link VALIDITY and **no orphan or
   island check at all** — a different question, unasked here.
2. **The doc states that its own check is UNENFORCED, precisely.**
   `docs/documentation.md`: "This check is manual and unenforced: `docs:lint` is not
   part of `quality`, `quality:base`, `quality:fast`, `quality:commit`, or
   `quality:push`, it is absent from the Husky pre-commit and pre-push hooks, and no
   workflow under `.github/workflows/` runs it. Nothing will stop a merge that breaks
   the graph, so run it yourself." Opinion: this is the most valuable thing in the
   repo for us. It is the honest inverse of a false green — instead of arming a gate
   so the question feels answered, it names exactly what is NOT protected and hands
   the reader the job. charness's reflex is to arm; this is worth copying as prose
   discipline, and it is P5 ("a gate may force a question; it may not declare
   completion") expressed without a gate.
3. **Exception tables carry a per-row REMOVAL CONDITION.**
   `docs/quality-exceptions.md` has an `Entry | Kind | Why the check is low-signal |
   Removal condition` table, where `Permanent` is an explicit allowed value and
   others read "Remove if `awiki` becomes a project dependency". charness closed
   `#526` (stale waiver signal) already, so this is a shape refinement rather than a
   gap.

The size comparison stays relevant but is NOT the lesson: craken's `AGENTS.md` is
**1,105 bytes / 20 lines**, and one of those 20 lines is the awiki instruction.

## Consumer repos, measured — this fills the audit's biggest hole

The 7-day audit could not say whether its fixes reached anyone because it inspected
no consumer. Five exist and the operator named them: `../ceal`, `../cmanki`,
`../stdy.blog`, `../journal.stdy.blog`, `../cautilus`. All five install charness and
all five carry `charness-artifacts/`.

**Always-loaded surface, every consumer (`#523`'s real blast radius):**

| repo | `AGENTS.md` |
|---|---|
| ceal | 18,349 bytes / 67 lines |
| journal.stdy.blog | 17,714 / 251 |
| **charness (this repo)** | **15,806 / 129** |
| stdy.blog | 12,121 / 169 |
| cautilus | 12,064 / 160 |
| cmanki | 11,826 / 235 |
| craken-agents (not a consumer) | 1,105 / 20 |

**Every consuming repo sits at 11.8–18.3 KB, and two are LARGER than charness's
own.** So `#523` is not an internal context-budget question — the shape propagates
through `setup`, and my earlier claim that the beneficiary is mostly this repo was
wrong.

**Which skills consumers actually run** (counted by their real write paths, not by
directory name — `achieve` writes `goals/`, `handoff` writes `docs/handoff.md`; my
first count got both wrong):

- 5/5 — `critique`, `quality`, `gather`, `retro`, `debug`, `setup`
- 4/5 — `achieve`, `handoff`, `ideation`, `narrative`
- 3/5 — `issue`, `spec`, `impl`
- 2/5 — `release`, `hotl`
- 1/5 — `hitl`, `announcement`, `create-skill`
- 0/5 — `create-cli`

Two consequences. `critique` at 5/5 is the most-used skill in the product, which is
why criticising its growth was the wrong target. And **`#521`'s implied premise is
weak**: only `create-cli` has no consumer trace, so the prompt surface is not
carrying dead weight and there is essentially nothing to delete on usage grounds.

## Group A — consumer-surface gaps whose premise I verified

These are the ones I would pick from. Each premise was checked this session, not
inferred.

- **`#523` (root always-loaded surface is contract prose, not routing).** My
  strongest recommendation, and my view CHANGED during this session — I had it as
  runner-up. Three independent confirmations now: `AGENTS.md` is 15,806 bytes with
  one section (`## Subagent Delegation`) at ~30% of the file; a repo the operator
  calls good runs on 1,105 bytes, **14× smaller**; and charness's own shipped
  guidance forbids exactly this —
  `skills/public/setup/references/default-surfaces.md:122` tells a consumer not to
  turn `AGENTS.md` into "a second handbook". That is a dogfood violation against a
  contract we ship. It is also a DELETION, so it reverses growth instead of adding
  a surface, and the consumer table above shows the shape propagating to every
  installing repo. Opinion: highest value per line changed of anything open.
  **Scope correction from the operator: `## Subagent Delegation` is LOAD-BEARING and
  is not the target.** It was added deliberately, at known cost, because without it
  the bounded critique subagent does not run — and `critique` is the 5/5
  most-used skill in the product, so that cost buys the most valuable thing here.
  Shrink it further only if it can be done without losing that; cut the REST.
- **`#527` (0 human-facing skill docs, 0 invocation lock).** Verified: 22 public
  skills, `find skills/public -name '*.md' ! -name SKILL.md` is entirely
  `references/` (agent procedure); `grep -ril "working if"` → 0; `grep -ril
  "disable-model-invocation\|allow_implicit_invocation"` → 0, and the only guard
  against publishing a release is one prose line at
  `skills/public/release/SKILL.md:61`. Two halves with different value: the
  invocation lock is small and sits exactly where the north star wants teeth
  (P5, irreversible), and the docs half risks becoming 22 hand-written files —
  i.e. the bloat this audit failed to prove but would then create. Opinion: take
  the lock half; take the docs half only as ONE generated file. The operator has
  already declined the lock half once, so this is a re-raise, not a decision.
- **`#531` (SessionStart hook discards cwd and emits one constant for every repo).**
  Opinion: underrated. It is the first thing every session in every consumer repo
  touches, and it currently cannot say anything repo-specific. Small surface, wide
  blast radius.
- **`#524`, `#525`, `#532`** (proof ladder has no machine-readable registry; external
  claims not bound to evidence; run-plan envelope requires `cost_tier` but has no
  size field for reads). Opinion: all three are real consumer extension-point gaps
  and all three are bigger than they look. Not next.

## Group B — measurement projects, and why the order matters

- **`#519` (skill trigger accuracy never measured), `#520` (no-skill baseline on 1 of
  20).** **Owner correction: skill evaluation is `../cautilus`'s job, not
  charness's.** So these are not a request to build measurement infrastructure here,
  and my earlier framing — first "expensive new infra", then "copy craken's evals" —
  was wrong twice, pointing at two wrong owners. The evaluator exists. The stated
  problem is CADENCE: it is not run often. Note `AGENTS.md` makes Cautilus eval-only
  and ask-before-run, gated behind `scripts/plan_cautilus_proof.py` and
  `scripts/run_cautilus_eval.py`, so a run needs an explicit grant. Opinion: reframe
  both issues as "the evaluator is not being run", which is a cadence and
  authorization question, not a build.
- **`#521` (prompt surface monotonically increasing — open a deletion path?).** A
  decision request, not a defect. Now measured against real usage: only `create-cli`
  has no consumer trace, so a NO-OBSERVED-EFFECT deletion path would find almost
  nothing. Opinion: `#523` is the better first cut at the same concern — it shrinks
  the surface every session pays for without deleting a skill anyone uses.

## Group C — consumer quality-contract defects

`#514`, `#515`, `#518` (closeout evidence assembly; quality surface lost behind a
green code gate; adapter/preset declares gates it never reconciles), plus `#528`,
`#530`, `#546`, `#549`, `#550`, `#542`.

Opinion: `#515`/`#518` are the most consequential in this group because they are
false-green classes, and false greens are what the north star's diagnosis is about.
But they are consumer-owned (`#514`/`#515`/`#518` carry consumer-repo evidence), so
they need that owner in the loop, and repeated goals have declined them for that
reason. `#530` and `#550` are adapter-resolver work that overlaps `#553`'s closed
repair; re-read that before scoping either.

## Group D — waiting on an operator decision, not on work

- **`#561`** — equality-versus-invariant probe pins. Both costs measured in the
  close-the-copies goal's Operator Decision Queue. Belongs to D47's owner.
- **`#560`** — built and PROVEN this session; only its closeout floor was never
  run. Closable, not closed. Cheapest possible close in the tracker.
- **`#547`** — needs a RE-SCOPE, not a close. Its literal subject died with the
  locator digests; its generalized form was WIDENED, because `refreeze` now
  re-stamps the locator set and the artifact's prose while reporting no diff.
- **`#535`** — identity-binding surfaces ship without a one-command re-bind. Opinion:
  worth claiming; it is the same "maintenance ritual is hand-executed" shape that
  `refreeze` was built to remove.
- **`#563`** — needs a decision on 3 non-English titles before the scope widens, or
  it lands red on day one.

## Group E — filed by this session, and honestly small

- **`#566`** was filed by this session and MIS-FRAMED; the correction is in its
  comments. It is not a fresh doc-graph finding — charness had already run awiki,
  captured a fixture, written an awiki contract critique under `#518`, and recorded 7
  orphans. The real gap is that awiki has no integration manifest, so no consumer can
  declare it, and that was an unfilled operator instruction rather than a discovery.
  I also pruned that state out of the handoff as stale in the same session, which was
  wrong; it is restored.
- **`#565`** (a mutation sweep with a broken baseline reports every mutant as
  killed). Re-confirmed LIVE during the audit: the same zsh word-split defect
  recurred in a command verifying an audit charge, an hour after being filed.
  Opinion: real, small, and a cleanup item rather than a goal.
- **`#564`** (a repair pinned only at its own function survives deletion of its call
  site). Opinion: I now think the remedy I proposed — a line in the goal template's
  verification plan — is rulebook growth (P3). Prefer letting `#565`'s tool ask the
  question. Re-scope or close.

## Group F — do not touch as titled

- **`#534`** (dup ratchet re-blocks after a module split). A prior goal built it
  green, REFUTED it, reverted it in full, and posted the refutation to the issue.
  Re-scope from the refutation, never from the title.
- **`#539`, `#545`** — provider/publication safety. Opinion: `#545` (private provider
  media URLs published as GitHub evidence) is the only issue in the backlog with a
  plausible data-exposure consequence. It is not urgent because nothing has been
  pushed, but it should not sit behind ergonomics work indefinitely.
- **`#554`** (`achieve` shapes a goal without reading the tracker). Opinion: partly
  addressed in practice — the close-the-copies goal carried a `## Backlog Recount`
  — but the SKILL still does not require it. Small.

## My ranking, as opinion

1. `#523`, with `## Subagent Delegation` held out — a deletion, a dogfood violation
   against guidance we ship, and measured at 11.8–18.3 KB across all five consumers
2. **`#566`, as CORRECTED in its comments** — not a doc-graph discovery. awiki was
   asked for as a support binary and never installed as one: `integrations/tools/`
   and `integrations/locks/` declare eleven binaries and awiki is in neither, while
   `docs/support-skill-policy.md:37-39` names the integration manifest as its home.
   The orphan count was already measured (7, transcribed, scope unverified), so my
   "open it as a measurement" framing was wrong too. craken's transferable half is
   the DISCLOSURE discipline, not the graph check
3. `#560` — close it; the work is done and proven
4. `#531` — the first surface every session in every consumer touches
5. Re-scope `#519`/`#520` onto Cautilus cadence rather than onto new measurement

## Non-claims

- Consumer repos WERE inspected for the table above (five, named by the operator).
  What is measured is `AGENTS.md` size and which skills left artifacts; no consumer's
  runtime behavior, no operator experience, and no defect rate was observed.
  `craken-agents` does not install charness and is a shape comparison only.
- Artifact presence proves a skill RAN at least once, not that it is used often or
  that it worked. `create-cli` at 0/5 may simply leave no artifact.
- This file's `#566` entry was wrong when first written. Treat every "verified this
  session" claim here as verified against THIS repo's tree at one moment, not against
  the repo's history — the awiki case shows the difference: the code said no
  doc-graph checker exists, and the HISTORY said awiki had already been run against
  it. Grep the artifacts, not only the scripts.
- The 7-day audit's own structural charges were largely refuted; anything in this
  file that reads as "the repo is bloated" is opinion that the evidence did not
  support.
- Nothing here is a proof that a fix is correct or safe; every item still owes its
  own premise check.
- Issue bodies were read; most shipped diffs were not re-read for this file.
