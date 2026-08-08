# Open-Issue Opinion — 29 open, grouped by the decision each needs
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

## The reference repo, and what it actually is

`../craken-agents` (HEAD `4c49c96d`) is a TypeScript product repo. Verified: it does
**NOT install charness** (`grep -rl charness ../craken-agents` → 0 hits outside
`node_modules`). So it is not a consumer whose needs can be read off — it is a
sibling well-run repo, useful as a comparison of OPERATING SHAPE only.

Two measurements from it change my view below, and both are cheap to re-run:

| | craken-agents | charness |
|---|---|---|
| `AGENTS.md` | **1,105 bytes / 20 lines** | 15,806 bytes / 129 lines |
| eval scaffolding | `evals/{baselines,scenarios,evaluation-output.schema.json}` | no baseline corpus per skill |

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
  a surface, and `setup` propagates the pattern to consumer `AGENTS.md`, so the
  benefit is not confined to this repo. Opinion: highest value per line changed of
  anything open.
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
  20).** I previously argued these should wait because they mean building new
  measurement infrastructure — the pattern this audit warned about. **craken-agents
  weakens that objection**: it already has `evals/baselines` + `evals/scenarios` +
  an output schema, so the shape can be copied rather than invented. Opinion: still
  not first, but cheaper than I claimed, and they are the only issues that would
  tell us whether the product WORKS rather than whether it is well-formed.
- **`#521` (prompt surface monotonically increasing — open a deletion path?).** A
  decision request, not a defect. Opinion: my earlier argument that a skill catalog
  is the precondition for this is now weaker, because the bloat premise it rested
  on was refuted. `#523` is the better first cut at the same concern and needs no
  new measurement.

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

1. `#523` — deletion, dogfood violation, 14× comparison, widest reach
2. `#527`'s invocation-lock half — small, and teeth where the north star wants them
3. `#560` — close it; the work is done and proven
4. `#531` — first surface every session touches
5. `#519`/`#520` — the only issues that measure whether the product works

## Non-claims

- No consumer repo was inspected for any claim here. `craken-agents` does not
  install charness, so it is a shape comparison and nothing more.
- The 7-day audit's own structural charges were largely refuted; anything in this
  file that reads as "the repo is bloated" is opinion that the evidence did not
  support.
- Nothing here is a proof that a fix is correct or safe; every item still owes its
  own premise check.
- Issue bodies were read; most shipped diffs were not re-read for this file.
