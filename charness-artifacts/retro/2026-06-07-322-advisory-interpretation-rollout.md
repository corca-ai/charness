# Retro — #322 advisory-interpretation contract rollout (session)

Date: 2026-06-07
Mode: session
Goal: `charness-artifacts/goals/2026-06-07-322-advisory-interpretation-rollout.md`

## What happened

Rolled out the advisory-interpretation contract (4-field `interpretation`
self-declaration + paired consumer-must-answer requirement) from the `nose`
pilot to six inference-layer surfaces (S1–S6), recorded the keep-per-surface
schema decision (S7), and staged `Close #322`. Routed the per-surface work to
`impl` per `find-skills`; verification per the goal's plan (targeted per-surface
pytest, broad pytest, bounded fresh-eye critique). Broad pytest 2511 passed, 4
skipped; fresh-eye critique returned no blockers.

## What worked

- **The contract dogfooded itself.** The length warn-band declaration (S4) fired
  on two libs I had just appended to (`standing_test_economics_lib.py`,
  `list_capabilities_lib.py`). Rather than ship into the band, I answered the
  declaration's own interpretation question (cohesive but tight) and resolved it
  by relocating the test-economics declaration to its emitter script and
  compacting the find-skills constant. The length smell working on its own author
  is the strongest signal the rollout is honest.
- **Inference-vs-verified discipline held under pressure.** The two highest-risk
  surfaces (length, find-skills) both have a verified-fact variant adjacent to
  the inference-layer one; gating the declaration (warn-band-only;
  ranking-produced-only) and writing cardinal-error negative-assertion tests kept
  the declaration off the verified facts.

## What created waste / friction

- **Surfacing-prefix near-miss.** The length INTERPRETATION line initially had no
  `ADVISORY:`/`WARN:` prefix, so as a standing `run-quality.sh` gate it would have
  been logged-but-hidden on a passing warn-band run — the exact trap the file's
  own warn-band-constants comment documents. Caught by re-reading the surfacing
  filter before sync, not by a test first. Lesson reused: a declaration added to a
  STANDING gate's passing output must carry a surfaced prefix; on-demand
  inventories (read in full by the consumer) do not.
- **Near-limit append trap (recurring).** Two libs were already ~322/360 before
  the change; appending a 26-line constant pushed them into the warn band. The
  recent-lessons "check headroom before a large addition" applies to constants
  too, not just functions.
- **Boundary-bypass ratchet block — a full test rewrite (the biggest rework
  cycle).** The new `test_python_length_interpretation.py` was first written with
  `run_script(...)` subprocess calls. The pre-commit `check_boundary_bypass_ratchet`
  blocked the commit (`no_increase` policy; one new candidate key) and I rewrote
  the whole file to drive `main()` in-process (importlib + sys.argv +
  redirect_stdout). The sibling per-surface tests I had already read carry an
  explicit "in-process boundary conversion (testability-dsl-initiative)" comment —
  the convention was visible, but I authored a NEW test file against a gated
  surface without checking the constraint first. This is the same #308-class
  authoring-preflight trap already in recent-lessons (author into a gated surface
  before reading the constraint). Existing test files kept subprocess because
  their boundary was already in the baseline; only a NEW file trips the ratchet.
- **Commit-exit misread (minor).** `git commit ... | tail` then `$?` read tail's
  exit (0), masking that the pre-commit hook had aborted the commit. Capture the
  pipeline head's status (or run without a pipe) when a hook can block.

## Improvement dispositions

1. **Meta-validator for the contract (deferred capability).** A gate that
   enumerates the inference-layer surfaces and asserts each emits the 4-field
   declaration AND carries a paired consumer line would prevent a future
   half-contract surface. **Disposition: recorded as a deferred capability**, not
   built — it is a new gate beyond #322's rollout scope and the keep-per-surface
   decision did not require it. Surfaced to the operator; file as a sub-issue only
   if they want it tracked (per the goal's "split if scope grows" frame).
2. **Surfacing-prefix tripwire (deferred).** A cheap check that a declaration/
   advisory line added to a STANDING `run-quality.sh` gate carries a surfaced
   prefix. **Disposition: deferred** — low frequency; the existing warn-band
   comment plus this retro lesson cover it for now.
3. **No new repeat-trap entry needed** beyond the existing near-limit-append and
   authoring-preflight lessons already in `recent-lessons.md`.
4. **In-process-first for new tests of repo scripts.** A NEW test file exercising
   a repo script should drive `main()` in-process (importlib + `sys.argv` +
   `redirect_stdout`), not spawn a subprocess, because `check_boundary_bypass_ratchet`
   blocks a new subprocess candidate key. **Disposition: reinforces the existing
   #308-class authoring-preflight repeat-trap** (read the gated surface's
   constraint before authoring) rather than a new lesson; the boundary-bypass
   ratchet + sibling-test convention already encode it. No new tooling — the gap
   was discipline (I had read the convention), so the durable fix is the
   preflight habit, not another check. Recorded here as the concrete instance.
5. **Commit-exit misread (process nit).** **Disposition: noted, no action** —
   capture the blocking command's own exit status, don't read a piped `tail`'s.
   Too minor for a standing lesson.

## Proof

- Targeted per-surface pytest: 140 passed.
- Broad pytest: 2511 passed, 4 skipped.
- `ruff`, `check_doc_links.py`, `check-links-internal.sh`: clean.
- Bounded fresh-eye critique: no blockers
  (`charness-artifacts/critique/2026-06-07-issue-322-advisory-interpretation-rollout.md`).
