# craken-agents absorption — pass 1 (2026-06-20)

Read-only mining of `../craken-agents` for patterns charness should absorb, scoped by the
north-star overhaul (`docs/north-star-overhaul-roadmap.md`). Baseline discipline applied
(the lychee lesson): only genuine gaps vs charness's existing surface count.

## Framing correction

`craken-agents` is NOT a skills/harness repo — it is a TS/Cloudflare-Workers agent product
("Orca"). Its "skills" are (a) repo-local Codex maintainer skills (`.codex/skills/`:
`make-pr`, `kill-mutants`) and (b) runtime product skills (`src/skills/builtin/`: `chat`,
`literature-search`, `experiment-protocol`, ...). The operator's anchor `bug-hunt` is NOT
in this repo — it is an external `$bug-hunt` / `$better-*` Codex skill referenced in
`docs/self-healing.md`, installed elsewhere. Its stated intent (reproduce before fixing)
is already enforced by charness `debug`.

## Strong external validation

craken and charness independently converged on the same thesis ("the metric/floor is a
forcing function, not the goal; non-terminal disposition over terminal-green"). So most
craken value is better phrasings / worked examples of doctrine charness already holds, not
new capability.

## Genuine absorptions (feed the overhaul)

- **A1 (HIGH) — survivor/exclusion equivalence reasoning.** `docs/testing-mutation.md`
  gives every surviving mutant + excluded file a written verdict (kill /
  equivalent-because-X / defer-because-Y), never a tautological kill or silent tolerate.
  Cleanest external embodiment of the north star's P5. -> doctrine line + a reference
  addition in `skills/public/quality/references/mutation-testing.md`.
- **A2 (MED-HIGH) — exception ledger with Review Rule + re-audit-by-removal.**
  `docs/quality-exceptions.md` carries `Last audited:` and proves each exception still
  earns its place by REMOVING it and counting real clones, then deletes obsolete ones. ->
  charness exemption discipline gains a `last_audited` + remove-and-count revisit.
- **A4 (MED) — claim-granularity anti-regression.** evidence-DEPTH labeling (don't
  collapse confidence levels), "carry citations across rewrites — never silently drop
  prior links," and numeric stop/go thresholds (`experiment-protocol`). -> doctrine for
  `spec`/`quality` + a rewrite-preservation rule candidate for `handoff`/`narrative`.

## Where charness is already equal-or-better (do NOT absorb)

- `debug` (falsifiable-hypothesis + durable artifact + RCA ledger) > craken's external
  bug-hunt.
- `create-skill` (portability/classification/manifests/proof-ladder/dogfood) >
  `skill-creator` (craken wins only on terseness — borrow the "Do not use for ..."
  second-sentence convention).
- `critique` (3 angles + counterweight + bounded subagent) — no craken equivalent.

## Next-pass veins

1. Locate `$bug-hunt` / `$better-*` bodies (operator's anchor; verify per-surface vs
   `debug`/`quality`/`code-review` before absorbing).
2. Extract `testing-mutation.md` survivor-disposition pattern as a concrete P5 example (A1).
3. `docs/code-quality.md` "Retrospective" — inline-in-standard lessons vs charness's
   separate `retro`/`recent-lessons.md`.
