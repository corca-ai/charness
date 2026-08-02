# Retro: Push the armed gate and close #477 through its carrier

## Context

Goal `2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier`. Two
things were finished and un-shipped: a proven commit sitting unpushed, and
#477's work complete with the issue open. Both were the same shape — local proof
done, external boundary never crossed, because the prior goal's side-effect
approval was scoped to that goal.

What matters next: the class this goal chased is now bounded and gated, but the
`parents[3]` family it surfaced is still live and correct only by coincidence.

## Window

Continuation of the same session as the previous goal. Four slices, five bounded
reviewer contexts, one issue closed, four pushes.

## Evidence Summary

- `inventory_skill_script_references.py --strict` → `all 402 (201 authoring /
  201 shipped) resolve`, exit 0, 2026-08-02. The one surviving
  `<repo-root>/scripts/` reference is `rca-ledger-append.md`, correct as an
  existence predicate the reader evaluates.
- Broad suite: **6752 passed, 0 failed**.
- #477: `verify-closeout` → `CLOSED` via `backend-state-readback`, no state
  mismatches — a different channel from the push exit code.
- Behavioural proof out of tree:
  [the installed-layout probe](../probe/2026-08-02-477-installed-layout-plan-risk-interrupt.md).
- FIVE `bounded-reviewer` contexts, each bracketed by
  `reviewer_boundary_fingerprint.py` snapshot/verify, every one `clean`.
- Host log probe (thread-wide, not per-goal): 476 function calls, 59 patch
  applications, 9 subagent spawns, 0 compactions. Token snapshots are
  point-in-time, so no cumulative total is claimed.

## Waste

- **The fix for "a documented command that cannot run" shipped three new
  documented commands that cannot run.** The three call sites I authored for the
  #478 shims used a bare path — `Run $SKILL_DIR/../../shared/scripts/X.py` —
  while the shims ship mode `100644`. Not executable. `permission denied` for
  any reader who follows the line literally. The two pre-existing Bootstrap
  fences were fine because they already said `python3 "..."`; I copied the
  invocation's SHAPE without noticing the interpreter prefix was load-bearing.
  Round 2 caught it; `git ls-files -s` confirmed it. **This is the single most
  instructive thing in the run**: I had spent the whole session on this exact
  class and still reproduced it inside its own repair.
- **A guard asserted half the thing it quoted.** The swallow check asserted
  `|| true` while its own docstring named `2>/dev/null || true`. Three of the
  four call sites are `references/` prose that the Bootstrap-fence checker never
  reaches, so that half-assertion was their only guard.
- **A test proved a bound existed without pinning it.** The bounded-walk fixture
  buried its outsider at ancestor index 7, so it stayed green for any cap up to
  7 — invisible to exactly the 5→7 loosening the cap exists to prevent. Verified
  by running `locate` at caps 5/7/8 rather than reasoning about it.
- **A comment cited a guard that did not cover the branch.** The lowered
  shipped-layout floor named an authoring-only fixture as "the real guard"; that
  fixture builds no `plugins/` tree, and no fixture anywhere produced a
  shipped-layout `BROKEN` row. The floor and its stated justification were both
  weaker than they read.
- **The closeout-claims round found five blockers in the RECORD, on its own
  first outing.** Every one was about what the artifact asserted, not about the
  code: `Disposition review:` bound to the same file as `Retro:` (one file
  cannot be its own independent review, and the gate would have refused);
  `## Lane C` still reading "NOT APPLIED — awaiting the operator" after the edits
  had shipped; a push line collapsing four pushes into one range with CI
  attribution that named no SHA; every Slice Plan row still `pending` while the
  run was finished; and — sharpest — "four bounded reviewer contexts … all
  clean" written BEFORE the fourth reviewer's `verify` could run. Four
  code-reading rounds this session reported none of these, because none was
  asked whether the summary survives contact with the work.
- **The closeout ledger took six refusals to satisfy** — four from
  `validate-closeout-draft` (field parsing, a `siblings` value lacking the
  decision-AND-proof shape, an unrecognised critique line form, a critique
  artifact with no `Fresh-eye satisfaction:` line) and two from the critique
  artifact's own validator. None were the gates being awkward; each named a
  field that makes the close auditable. Worth recording because
  "validate-closeout-draft passed" reads very differently from what it took.

## Critical Decisions

- **Read the planner before deciding its fate.** I had recommended deleting the
  `plan_risk_interrupt` call on the reasoning that nobody had missed it. The
  operator pushed back; reading it showed it returns `blocked` with a forced
  `external-seam` class on this very repo. Repoint, not delete. The lesson is
  narrow and sharp: I recommended deleting code I had not read.
- **One shim, not a two-candidate probe.** A probe in the fence would have had
  one candidate failing by construction in each layout — indistinguishable from
  a real broken reference to both the link gate and the new checker. Resolving
  the ambiguity once in code with tests beats resolving it twice in prose.
- **A shared module before the second shim, not after.** Three copies of the
  resolution logic would have been a dup-ratchet hard block at closeout; the
  ratchet stayed clean all run because the shared module came first.
- **Rejected `<plugin-dir>/` for #478 despite it being the obvious answer.** It
  has zero usage precedent and no bootstrap variable behind it, so the agent
  would have to resolve the plugin directory itself, and these sites would have
  become the convention's first users. That is a convention launch, not a repair.
- **`runpy` over a per-target error handler.** Two targets keep their error
  handling in `__main__`; running the target AS `__main__` inherits whatever
  entry contract it already has instead of re-implementing one per target.

## Trends vs Last Retro

- **The round-2 class recurred for the fourth measured time, and this instance
  is qualitatively worse than the previous three.** Before, round-1 repairs
  shipped adjacent defects. This time the repair shipped *the exact class it was
  repairing*, in a session entirely devoted to that class. The cadence rule is
  the only reason it did not ship.
- **The claims-review class recurred too**, in a new dress: last goal it was a
  skipped verification step; here it was a comment citing a guard that did not
  cover the branch. Both are "the record says something the code does not".
- **Improvement that held**: the dup ratchet stayed clean for the entire run
  because the shared module preceded the second copy — the previous retro's
  lesson applied before the block rather than after it.

## Expert Counterfactuals

**Engelbart, `system-improving-itself`.** The T-change this goal actually
delivered is not the shims — it is `<authoring-repo>/`, which makes the escape
hatch and the typo *different tokens*. Before it, a human could not tell them
apart either, which is why the class survived three gates and a human review.
After it, the remaining ambiguous set is one line, and it reads as deliberate.
The counterfactual he would push: I made the SPELLING distinguishable but left
the *depth arithmetic* implicit. Ten `parents[3]` sites are correct only because
the exporter's flattening cancels the `plugins/<pkg>` prefix — a coincidence no
reader can see from the call site. The equivalent T-change there is a named
helper (`plugin_or_repo_root(__file__)`) so the invariant is stated rather than
re-derived by arithmetic at each site. I recorded it as a sibling with a revisit
trigger instead of building it; that is the honest deferral, but it is deferral.

**Second lens — the checklist author (Gawande).** The interpreter-prefix miss is
not a knowledge failure; I knew the shims were not executable, having just
created them. It is a *transfer* failure: I copied an invocation's shape from
one context (a Bootstrap fence that already had `python3`) into another
(reference prose) and did not re-derive the precondition. A checklist would not
have helped — I would have read it and still copied the shape. What DID catch it
was an outside reader asking "does this actually run?", and what made that
answerable in seconds was `git ls-files -s`. The generalisable move is to make
the precondition *checkable* rather than memorable: the assertion now in the
test is worth more than any rule I could write about it.

## Next Improvements

- **workflow** — When authoring an invocation, copy the full invocation
  including its interpreter, or assert the file is executable. Now enforced by
  `test_the_call_sites_name_a_path_that_resolves_in_both_layouts`.
- **capability** — A test that pins a BOUND must place its fixture at the
  boundary, not comfortably past it. Verified this one by running the function
  at three caps rather than reasoning about the fixture.
- **memory** — This retro plus the recent-lessons digest.

## Sibling Search

Transferable pattern: **prose that names an invocation which cannot execute as
written** — not just a wrong path, but a missing interpreter, a non-executable
mode bit, or an unquoted variable that word-splits.

Swept: every `$SKILL_DIR/...`-bearing command line in shipped skill prose. All
now carry `python3` and quote the variable, asserted for the four shim call
sites by test. The `references/` prose sites are NOT covered by
`validate_skills`' Bootstrap-fence swallow check, which is why the shim test
carries that assertion instead.

Decision: **closed for the shim call sites, recorded for the general case.** A
repo-wide "every documented invocation is executable as written" check would
subsume both this and the path-resolution gate; it is the natural next step for
`inventory_skill_script_references.py` and is named here rather than built.

## Portable Candidate

- **Abstract pattern**: a documented command can fail three independent ways —
  the path does not resolve, the file is not executable, or the invocation is
  missing its interpreter — and a checker that covers only the first reports
  clean on the other two.
- **Triggering evidence**: this run's own repair for a path-resolution defect
  shipped three commands that resolved perfectly and could not execute.
- **Intended consumer/repo shape**: any repo whose docs are also runbooks.
- **Destination**: `not portable — as a skill` yet. It belongs in this repo's
  path checker first; offering a convention before it has one real
  implementation is what `<plugin-dir>/` already is.
- **First-prompt acceptance claim**: "every documented command in shipped prose
  can be executed exactly as written, or is spelled as a non-executable
  reference on purpose."

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md

## Packet Consumed

n/a (no adapter sections) — the retro adapter declares no `packet_sections`, so
this retro is narrative plus the host-log probe and the gate/suite numbers in
`## Evidence Summary`.
