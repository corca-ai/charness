# Retro: Repair the commands the skills tell agents to run

## Context

Goal `2026-08-03-repair-the-commands-the-skills-tell-agents-to-run`. Thirteen
shipped skill references said `<repo-root>/scripts/X.py` while `X.py` lived in
the skill's own package, so an agent following the instruction got "No such file
or directory" — here and in any consuming repo. Three lanes: repair the 13,
disposition the references whose file really is a charness repo script, and ship
the resolution check as a non-blocking advisory (operator-decided).

What matters next: #477 and #478 are open operator decisions this run
deliberately did not take.

## Window

Single session, from `/goal` activation at `9f405a28` through closeout. Three
lanes plus closeout, **four bounded reviewer contexts** (Lane A+C round 1, the
round-2 pass over the repaired surface, a closeout-claims audit by a distinct
observer, and an adversarial default-to-refuted pass over the Lane B table), two
issues filed.

## Evidence Summary

- The advisory's own output before/after: broken **13 to 0** in the authoring
  layout, denominator restated as `406 references (203 authoring / 203 shipped)`
  across 47 scanned package roots (~23 distinct packages, counted once per
  layout), 2026-08-02.
- Broad suite: `run_standing_pytest.py --mode read-only` = **6716 passed, 0
  failed, 38.17s** — run because the handoff warns a `completed` gate is not
  broad proof, and last run's gate said `completed` while a test was failing.
- `run_slice_closeout.py --verification-lock --ack-cautilus-skill-review
  --produce-mutation-coverage` = `Closeout status: completed`.
- Four bounded `bounded-reviewer` contexts, each bracketed by
  `reviewer_boundary_fingerprint.py` snapshot/verify, all `clean`, no drift.
- Host log probe (thread-wide, not per-goal): 185 function calls, 44 patch
  applications, 2 subagent spawns, 0 compactions. Token snapshots are
  point-in-time, so no cumulative total is claimed.

## Waste

- **The advisory's first version measured the wrong tree.** It scanned
  `skills/` only — inheriting the goal's own 13/91/9/0 measurement, which was
  taken over the authoring tree. But `plugins/charness/` is what ships, it is a
  *different* tree, and a reference can resolve in one and not the other. Two
  real defects (`plan_risk_interrupt`, now #477) were structurally invisible to
  the measurement the goal handed me. Found only because I checked the mirror by
  hand after the repair. Cost: one rework of the scanner mid-slice; the bigger
  cost would have been shipping a check that says "all resolve" about a tree
  nobody runs.
- **The round-1 repair shipped two gate failures of the class it was fixing.**
  Wiring the advisory into `run-quality.sh` satisfied neither of that surface's
  two registration contracts: `check_timing_layer_completeness.py` (every
  `queue_selected` label needs a verdict row in the timing-layer table) and
  `test_every_queued_repo_script_gate_has_a_seeded_harness_stub`. Round 2 caught
  both; I confirmed both by running them. **Third measured instance** of "the
  round that reads the REPAIRS is where the class comes back".
- **A test asserted a proxy instead of the real thing, and failed on its own
  docstring.** `assert "--strict" not in source` matched the module docstring
  *explaining* that `--strict` is deliberately absent. Replaced with a read of
  the real `argparse` parser's option strings. Same family as the standing
  "build test inputs from the source constant" trap, one level up: not a
  retyped fixture, but a grep standing in for the structure it describes.
- **The dup ratchet fired twice, and only the first was at the edit.** The
  edit-time advisory fired on the first write and I handled it there (an
  improvement on last run's aggregate-time discovery). But the round-2
  restructuring of the same file **rotated the fingerprints**, so a second
  hard-block appeared at the closeout aggregate with three new families. The
  edit-time discipline is necessary and not sufficient: a later refactor of an
  already-classified file re-opens the question.
- **I recorded a promised verification step as done when it had not run.** The
  plan required "adversarial verification defaulting to refuted on every Lane B
  disposition". I dispositioned all ten rows by reading them once and moved on;
  no adversarial pass existed. A closeout-claims reviewer caught the gap — and
  its own single reading had already refuted one row, which is exactly the
  evidence that the pass was load-bearing rather than ceremonial. When the pass
  was then actually run, it refuted a further row and found a third broken token
  (`check-links-internal.sh`) that no count had ever included, because the
  original measurement scanned only `.py`. **This is the worst item in this
  retro**: not a defect that slipped through review, but a verification step the
  artifact would have carried as satisfied.
- **The artifact contradicted its own retro in the flattering direction.** The
  Slice Log said "no new families from the Lane C additions" while the retro
  recorded a second dup-ratchet hard-block with three families. Whichever was
  written second, the one that survived into the goal artifact was the one that
  read better.
- **Four `## Coordination Cues` lines were written inside backticks and the
  floor did not see them.** The template's example line is backticked as an
  illustration of the *form*; copying it verbatim produced non-satisfying
  values. Small, but it is the same "the escape hatch is indistinguishable from
  the real thing" shape this whole goal is about.

## Critical Decisions

- **Two repair forms, not one.** References-list bullets became
  `scripts/X.py`; prose became `$SKILL_DIR/scripts/X.py`. Both are exactly what
  `skill_ergonomics_lib.has_portable_path_ambiguity` whitelists, so the repair
  matched the existing sanctioned convention instead of imposing a new uniform
  one. A reviewer independently confirmed this from the whitelist source.
- **Did not repair `plan_risk_interrupt`.** Repointing would make a command that
  has never run in an installed plugin start running everywhere — a behaviour
  change, which the goal's stop condition (1) routes out of scope. Filed as #477
  and pinned as a ratcheted known exception so the count may shrink, never grow.
  This is the decision I am least certain about and most confident was correct
  procedurally: the fix is one character, and that is exactly what makes it
  tempting to take without a decision.
- **Narrowed the bare `scripts/X.py` scan to `## References` bullets.** The
  broad version would have turned legitimate prose ("point it at your repo's
  `scripts/ci_check.py`") into findings. Manufacturing a defect is the same
  failure as missing one — and a check that cries wolf is how a deterministic
  gate loses its standing.
- **Shipped the advisory with no `--strict` flag at all**, rather than one
  defaulting to off. An escalation flag that exists gets wired into a gate by
  habit; absence is the enforceable version of the operator's restraint call.

## Trends vs Last Retro

- Repeat trap **avoided**: the dup ratchet was run at the first edit, not the
  closeout aggregate — the previous retro's explicit checklist item. It then
  re-fired anyway after a refactor, which is new information rather than a
  repeat of the old miss.
- Repeat trap **recurred, third instance**: the round-2 repair round catching
  what round 1 structurally could not. The handoff predicted this in writing
  ("twice last run a round-1 repair on a proof surface shipped the defect it was
  repairing") and it happened again. This is now the most reliably-recurring
  pattern in the recent-lessons digest, and the cadence rule that catches it is
  earning its cost every single time.
- Repeat trap **recurred in a new dialect**: the "fixture spelled the way the
  matcher wants" family showed up as a source-grep proxy rather than a fixture.
- **New this run, and the one worth carrying forward**: reviewers who audit
  CLAIMS rather than CODE found a different and more embarrassing class than the
  code reviewers did — a dropped verification step, a self-contradiction, an
  unreconciled headline number. Three code-reading rounds passed over all of
  them. The closeout-claims round is not a formality at the end of the ladder;
  it is the only round whose subject is what the artifact asserts.

## Expert Counterfactuals

**Engelbart, `system-improving-itself` (briefed by the planner: treat H + LAM +
T as one unit; design T alongside LAM).** The tooling (T) here is
`check_doc_links.py`, and the sharpest thing this run produced is not the 13
repairs — it is the finding that the 13 were invisible **by construction**.
`<repo-root>/` is a *documented portable placeholder*, the sanctioned escape for
commands that only resolve in a consuming repo, so three separate silences
overlap on exactly that spelling. Engelbart's move would be to stop treating
this as a defect count and start treating it as an **augmentation-system
defect**: the escape hatch and the typo are the same token, so the human cannot
tell them apart either. The counterfactual action: I reached for "measure and
repair" when the higher-leverage change was to make the two *spellings*
distinguishable — a distinct placeholder for "resolves only in a consuming repo"
versus a path that should resolve in the package. That is a T-change that turns
a class which is undiagnosable-by-eye into one that is diagnosable-by-eye, and I
did not propose it. Recorded below as a candidate, not smuggled into this goal.

**Second lens — decision quality under uncertainty (Klein's pre-mortem).** Asked
before Lane C: "it is six months from now and this advisory has been silently
useless — why?" The answer that would have surfaced immediately is the one round
1 found late: *because it scanned the authoring tree while the mirror is what
ships*, and *because it was wired to nothing*. Both are "the check exists but
never fires where it matters" — the identical class the goal was repairing, one
meta-level up. A pre-mortem on the instrument, not just on the defect, would
have caught both before a reviewer did.

## Next Improvements

- **workflow** — When adding a `queue_selected` line to `run-quality.sh`, two
  registrations are owed in the same breath: a verdict row in
  `docs/conventions/validator-timing-layers.md` and a stub in
  `tests/quality_gates/support.py::QUALITY_PYTHON_STUBS`. Both gates exist and
  both fired correctly; they fired at closeout rather than at the edit.
- **workflow** — Re-run the dup ratchet after a *refactor* of an
  already-classified file, not only at its first edit. Fingerprints rotate.
- **capability** — A check whose subject is a shipped surface must resolve
  against the shipped layout, not the authoring one. Applied here; the general
  form is the Portable Candidate below.
- **memory** — This retro plus the recent-lessons digest.

## Sibling Search

Transferable pattern: **a path that is correct in the authoring tree and wrong
in the shipped tree, because the exporter changes the depth from the package to
the root.** Bounded scan over the one axis where source-correct differs from
mirror-correct (everything else in `plugins/` is a byte copy, and mirror drift
already has its own gate):

- `$SKILL_DIR/../../../...` (3 levels — reaches the repo root in the authoring
  tree, overshoots the plugin root in the shipped one): **exactly 2 sites**,
  `impl/SKILL.md:41` and `spec/SKILL.md:26`, both `plan_risk_interrupt.py`, both
  filed as #477.
- `$SKILL_DIR/../...` and `$SKILL_DIR/../../...` (1-2 levels — sibling skill or
  the tier root): 11 prose sites outside `skills/shared` (15 including it; 9 if
  the two `<skill-id>` placeholder sites in `create-skill/SKILL.md` are
  excluded), counted 2026-08-02 by `grep -rnoE '\$SKILL_DIR(/\.\.)+/...'` over
  `skills/**/*.md`. These resolve **identically** in both layouts, because the
  package-to-tier-root depth is the same in each.

Decision: **closed at 2 on the prose axis.** Scope of that claim, narrowed after
a closeout-claims reviewer showed the first wording was broader than the scan:
the scan covered `$SKILL_DIR/...` tokens **in markdown prose**. It did NOT
enumerate the same-axis depth walks inside packaged Python — e.g.
`Path(__file__).resolve().parents[3]` in several `skills/public/*/scripts/plan_*.py`.
The reviewer checked those by hand and they resolve in both layouts
(`parents[3]` is `skills/` authoring and `plugins/charness/` shipped), so the
conclusion survives — but the advisory does **not** detect the `.py` variants,
so "any new instance is detected automatically" is true of prose only. That
gap is the honest residual, not a closed class.

## Portable Candidate

- **Abstract pattern**: when a documentation placeholder for "this path only
  resolves in the consumer's tree" is spelled the same way as an ordinary broken
  path, a link checker cannot distinguish a deliberate escape from a typo, and
  the typos accumulate silently and indefinitely.
- **Triggering evidence**: 13 references accumulated undetected in a repo that
  runs a doc-link gate on every commit, because `<repo-root>/` is that gate's
  own documented escape hatch and is exempt by design.
- **Intended consumer/repo shape**: any repo shipping documentation that is read
  from two different roots — a plugin/package mirror, a monorepo publish step,
  a docs site with rewritten bases.
- **Destination**: `not portable — as a skill`. The insight is a *convention*
  ("give the consumer-only escape its own distinguishable spelling"), not a
  workflow, and it belongs in this repo's authoring conventions before it is
  offered to anyone else. Recorded here so it is not relearned.
- **First-prompt acceptance claim**: "every documented command path either
  resolves in the tree that ships it, or is spelled with a marker reserved
  exclusively for consumer-tree resolution."

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md

## Packet Consumed

n/a (no adapter sections) — the retro adapter declares no `packet_sections` and
no `metrics_commands`, so this retro is narrative plus the host-log probe and
the gate/suite numbers quoted in `## Evidence Summary`.
