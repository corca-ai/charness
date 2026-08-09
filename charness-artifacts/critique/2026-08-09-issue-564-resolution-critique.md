# Issue #564 Resolution Critique
Date: 2026-08-09
Fresh-Eye Satisfaction: parent-delegated

## Reviewer Tier Evidence

- requested tier: `bounded-reviewer` typed subagent, read-only by definition
- requested spawn fields: inherited parent model and reasoning settings; no
  per-subagent model or effort override requested; spawned unnamed
- host exposure state: host-defaulted
- envelope note: the reviewer confirmed only Read/Grep/Glob were exposed and
  named the one command it needed the parent to run rather than asserting its
  outcome
- application state: spawn tool accepted the reviewer agent id; reviewer-tier
  application details are host-hidden
- Delivery state: findings-received

## Decision Under Review

Closing `#564` on the work shipped as slice 5 of
`charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md`
(commit `6b386ba4`, pushed in `ec67291e..18a9a439`).

`#564`: a repair's proof calls the repaired function directly instead of through
the caller that should invoke it, so deleting the CALL SITE leaves the suite
green while the repair is dead in production. Three measured instances in one
goal, none visible in the diff.

The issue's own filed remedy — a new line in the goal template — was DECLINED on
P3 grounds by two durable records, which is why this slice makes the question the
sweep runner's behaviour instead. The premise was re-measured and HELD: the
runner enforced baseline, failure evidence, and restore-on-raise, and nothing
about call sites.

## Failure Angles

- **Re-creating the declined "remembered rule" in code.** An opt-in declaration
  fires only when the author already remembered the thing they forget.
- **A signal that silences its own warning.** Any inferred corroboration risks
  turning the finding off.
- **The reporting feature re-opening a restore hole** (`#573`).

## Round 1 — DEFECTIVE, three blockers

1. The design INFERRED a call-site mutant from removed calls and let that
   SUPPRESS the non-claim. Wrong in both directions, both measured: attribute
   calls are keyed by attribute, so `return tuple(sorted(x.elements()))` ->
   `return ()` reports `('elements',)` and a pure body mutant counted as
   caller-side proof; a `super().__init__()` deletion reported nothing.
2. Classification sat OUTSIDE the restoring `finally`, re-opening `#573` through
   a reporting feature, in a module whose docstring promises the restore covers
   the write.
3. `hasattr(builtins, name)` filtered object-protocol dunders, because
   `builtins` is a module object.

## Round 2 — DEFECTIVE, blockers inside the round 1 repairs

1. The non-claim SENTENCE still said "no mutant deleted a call site" while its
   trigger had become "no mutant was DECLARED" — and the suite already held a run
   printing that beside its own `[removes join, str]` line.
2. A declared mutant that was REFUSED still counted, silencing the warning on a
   mutant that produced NO answer.
3. Plus: a declaration reported `false` for plans that declared `true` on an
   early-refused mutant; `bool("false")` read as a declaration; the crash arms
   missed the stdout flush; an empty plan stayed silent.

The builtins filter was DELETED rather than corrected: it was scaffolding for the
inference design and immediately refused an honest declaration whose mutant
deleted a `print(...)` call.

## Resolution Critique — NOT-CLOSABLE on the first draft

A third delegated reviewer read the closeout draft against the tree and refused
it, while accepting the design:

- **The central objection was raised and it FAILED.** "An opt-in declaration
  fires only when the author already remembered" does not survive the default
  path: `call_site_non_claim` is default-ON, printed unless a declaration exists
  AND its edit corroborates it. The forgetting author gets a warning naming the
  exact `#564` failure mode; the declined template line gave silence.
- **Blocker:** `debug_artifact` cited "slice 4"; the `#564` work is `### Slice 5`.
- **Blocker:** the verdict quoted a baseline of 57 against a module with 58
  tests, and presented three self-caught defects and a clean 13/13 as if one run.
- **Blocker:** the teeth check only that the edit removed SOME call, so a
  declaration corroborated by an incidental `str()` removal still silences the
  non-claim. Acceptable as a boundary, dishonest as an unstated one.

Resolved before posting: the self-sweep was RE-RUN against the shipped tree and
reports `13 killed, 0 survived, 0 refused, 3 call-site, over a baseline of 58
passing tests`; the remote was read back independently (`git ls-remote origin
main` = `18a9a439`), confirming the carrier claim; and the self-certification
boundary plus the slice pointer were written into the posted ledger.

## Counterweight Pass

- **Over-worry rejected:** "nothing routes an agent to this runner." The handoff
  does route it, and a durable skill-level route is a larger scope than `#564`
  asked for. Worth filing if the handoff pointer ever falls out; not grounds to
  hold the issue open.
- **Over-worry rejected:** "same tool run a different way is the same channel."
  The self-sweep through the real CLI against real repo source caught three
  defects the pytest channel did not, which is what distinctness means
  operationally.

## Boundary Ownership

- Producer: `scripts/mutate_and_restore.py` — it produces the kill/survive verdict, the removed-call evidence, and the call-site non-claim.
- Consumer: the agent or operator reading a sweep transcript as proof that a repair is reached.
- Owning surface: the sweep runner itself; the goal template was explicitly declined as the owner.
- Verdict: single-surface

The whole change is confined to `scripts/mutate_and_restore.py` and its test
module; no other surface consumes the runner's output (grep for
`mutate_and_restore` finds only the two script copies, the test module, and
prose), so the widened counts line and the new JSON keys reach no other owner.

`#573` (an interrupted sweep leaves the tree mutated when the PROCESS is killed)
is a distinct, still-open hole this change does not close, and it fired again
during this session. Release and push are out of scope here.

## Will The Class Recur

Guarded where it can be. The non-claim is default-ON and survives an empty plan;
inference is refused as a silencer; a REFUSED mutant cannot corroborate. Not
guarded: whether a declared call-site mutant deletes the RIGHT caller, which the
tool cannot establish and the ledger now says out loud.

## Non-Claims

- The runner reports and does not refuse on the ABSENCE of a call-site mutant,
  because it cannot establish whether one was warranted.
- The baseline-count half of the two never-written lines was already shipped by
  `#565`; this change adds only the call-site half.
- This critique reviews the CLOSE decision. The implementation's own two bounded
  rounds are recorded in the goal artifact's Slice Log, `### Slice 5`.
