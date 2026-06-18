# Issue draft — Autonomous code-layer quality pass (capabilities over features)

Status: **FILED 2026-06-18 as corca-ai/charness#390**
(<https://github.com/corca-ai/charness/issues/390>, label `enhancement`, OPEN),
via the `issue` skill after a bounded fresh-eye critique (B1 doc-side scope guard,
B2 one-pass closeability — both folded before filing).
Audience: an autonomous runner (ceal) that can make valuable, independent
progress **before** the north-star overhaul completes.

## Re-scope (2026-06-19) — overhaul now COMPLETE

The north-star overhaul this issue ran *alongside* completed 2026-06-18 (S1–S6;
`charness-artifacts/goals/2026-06-18-north-star-overhaul.md`). That moots the
original "before / while the overhaul is in flight" rationale and the
**concurrent-edit** basis of the hard collision guard below. The pass is now a
**standalone post-overhaul code-layer quality pass**, with one reframing and no
scope expansion:

- **Scope unchanged — still code-layer only** (`scripts/`, `skills/**/scripts/`,
  gate/validator code). Cut duplication + latent defects, test-first, **one
  pass**, file the rest as sub-issues.
- **The collision guard is now lane discipline, not collision avoidance.** Prose
  surfaces (`AGENTS.md`, `CLAUDE.md`, `docs/design-north-star.md`, skill
  **bodies**, closeout / gate-framing prose) stay out of scope because they
  belong to the **prose tracks** — chiefly the still-pending capped-skill-body
  SRP sweep (handoff "Primary spin-out"), which owns skill-body edits. If a code
  change forces a prose change, **file a sub-issue** (unchanged).
- **Net:** same files in / out of scope; only the *reason* for the prose
  boundary changes from "don't collide with an active editor" to "that's another
  track's lane." This session runs the pass interactively (not via ceal), at the
  operator's direction.

---

## Title

Autonomous code-layer quality pass: cut non-orthogonal duplication + latent defects (capabilities over features)

## Observed problem

charness's diagnosed bloat (the "just add an Nth gate" reflex; ≈34.7K lines of
gate scripts, validators near or at length caps) is the *feature-addition*
anti-pattern at the **code layer** — duplicated, non-orthogonal scripts and
latent defects that lower capability reliability without adding capability. The
[*capabilities over features*](../gather/2026-06-18-capabilities-over-features.md)
philosophy (minimum, orthogonal, composable, learnable surface; "less but
better") and `docs/design-north-star.md` both point at reducing this, but the
in-flight north-star overhaul deliberately owns only the **skill-prose / gate
framing** layer (`charness-artifacts/goals/2026-06-18-north-star-overhaul.md`).
The **code/script layer** is left unattended and is safe to improve in parallel.

## Evidence

- Length-headroom advisories already fire on gated scripts near their caps
  (`run_slice_closeout.py`); several validators have been split before under
  length pressure (see prior `*-module-split` goals under
  `charness-artifacts/goals/`).
- The repo already uses `nose` for duplication/refactor discovery (prior
  `nose-duplicate-refactoring`, `nose-issues-*` goals), so the tooling exists.
- Doc↔code drift is a recurring class (the repo ships generated surfaces such as
  `docs/generated/cli-reference.md` that can lag actual CLI behavior).

## Cost

Left alone, the code layer keeps accreting non-orthogonal duplication and
latent defects: each new script is harder to learn, more places to fix a bug,
and more "which helper do I call?" overhead — the exact learnability tax the
philosophy warns about. Doing it *during* the overhaul would collide with the
overhaul's prose edits; doing it *never* lets the debt compound.

## Useful outcome

One **closeable autonomous pass** over the code/script layer that measurably
reduces duplication and latent defects, lands the safe fixes test-first, and
files the rest as tracked sub-issues — with **zero edits** to the surfaces the
north-star overhaul owns.

---

## Autonomous execution contract (for the runner)

### In scope
- Python script / validator / test layer: `scripts/`, `skills/**/scripts/`, gate
  and validator code.
- **Script-level** doc↔code consistency only: generated references
  (`docs/generated/cli-reference.md`) and helper `--help`/behavior — **code/script
  behavior fixes only**. If the *doc* is wrong (not the code), **file a sub-issue
  rather than editing it**; never edit `docs/` prose directly (it may be
  overhaul-owned).

### Out of scope (collision guard — hard)
- Skill-prose **closeout / gate framing** sections and the always-on docs
  (`AGENTS.md`, `CLAUDE.md`, `docs/design-north-star.md`, skill bodies) — these
  are owned by the active overhaul goal
  (`charness-artifacts/goals/2026-06-18-north-star-overhaul.md`). **Do not edit
  them.** If a code change *forces* a prose/doc change on an overhaul-owned
  surface, **file a sub-issue** describing the needed change instead of editing
  it.

### The pass (one closeable iteration)
1. **Duplication / orthogonality (nose + `quality`).** Run `nose` over in-scope
   code for duplication/refactor candidates. Land the **safest top cluster**
   test-first: for any uncovered code you touch, write the test *first*; if it is
   not readily testable, do the safe testability refactor first, then test.
   Reduce non-orthogonal helpers toward "one obvious way." File the remaining
   clusters as sub-issues.
2. **Latent-defect sweep (`debug`).** Systematically read the validator/gate
   scripts for latent bugs (off-by-one, silent except, unhandled path, fail-open
   where fail-closed is meant). Fix with a regression test, or file.
3. **Script-level doc↔code consistency.** Reconcile by fixing **code/script
   behavior** only. If the *doc* is wrong (not the code), **file a sub-issue —
   never edit `docs/` prose directly**. When it is unclear which is wrong, file.

### Done (closeable — bounded to ONE pass)
This issue closes when **one `nose` duplication run + one systematic `debug`
sweep + one script-level doc↔code check over the in-scope file set** are
complete: the safest top cluster landed (test-first) or filed, and every finding
*surfaced in that pass* is either committed or filed as a sub-issue. The runner
**stops after one pass** — not after exhausting all conceivable findings (that
never closes and is the repo's standing-directive smell). The loop continues via
the filed sub-issues, so closing this issue compounds progress rather than
stopping it.

### Discipline (non-negotiable)
- **Test-first** for any uncovered code touched.
- Route through **charness's own skills** — `quality`, `debug`, `nose`,
  `critique`, `issue` (charness has no `bug-hunt` / `better-ut` skill; do not
  assume them).
- Honor `mutate → sync → verify → publish`; sync generated/mirror surfaces
  before validators.
- Fresh-eye `critique` at slice-intent boundaries; the gate suite must stay
  green (no regression).
- **No push / external publish without operator approval** (or strictly within
  ceal's preauthorized apply/restart policy). Precondition: ensure the `nose`
  CLI is current before relying on its output.

### Acceptance (operator-verifiable)
Read the filed sub-issues + the landed commits: measurably less duplication /
fewer latent defects in the in-scope layer, the gate suite green, and **no edits
to overhaul-owned surfaces**.
