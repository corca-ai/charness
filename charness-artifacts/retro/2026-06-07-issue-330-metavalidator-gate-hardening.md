# Retro — #330 advisory-interpretation meta-validator + #331 surface-idiom lint

Date: 2026-06-07

## Mode

session

## Context

Activated the shaped achieve goal `2026-06-07-330-metavalidator-gate-hardening`
and ran it end to end: built the #330 meta-validator (enumerate inference-layer
surfaces; assert the 4-field `interpretation` declaration + paired
consumer-must-answer line; fail closed on any unregistered declaration), bundled
the #331-deferred surface-idiom lint, wired both as standing + slice-closeout
gates, and staged `Closes #330`. Routed via `find-skills` (impl + quality;
in-repo, no external source).

## Evidence Summary

- New registry `.agents/inference-interpretation-surfaces.json` (8 surfaces: 7
  python declarations + 1 prose ranking); empirical AST scan confirmed exactly 7
  python declarations exist, so the registry is the complete current set and a
  new/8th declaration fails closed.
- `scripts/validate_inference_interpretation.py` (269/480 lines) + 18 tests;
  `scripts/surfaces_lib.py` idiom lint + 3 tests. 54 targeted tests pass.
- Broad pytest 2394 passed, 4 skipped. Live meta-validator green (8 surfaces);
  `validate_surfaces` clean (29 surfaces). Mirror byte-match; packaging green.
- Bounded fresh-eye review: SHIP-WITH-NITS; all 3 findings folded before ship
  (`charness-artifacts/critique/2026-06-07-issue-330-metavalidator-gate-hardening.md`).

## Waste

- **Doc-anchor line-wrap false-negative (one validator round-trip).** The prose
  anchor `"it is blind to"` did not match gate-classification.md because the text
  wraps as `it is\nblind to` — a substring anchor cannot span a markdown line
  break. Caught on the first live validator run, fixed by choosing single-line
  anchors. Cheap, but avoidable by checking anchor/line geometry up front.
- **Fail-closed gap survived my own authoring; the fresh-eye caught it.** My
  leak scan only walked `ast.Assign`, so the natural annotated form
  `INTERPRETATION: dict = {...}` would have escaped registration — silently
  defeating the gate's entire purpose one surface later. I had even written
  "any nesting" in the docstring, an overclaim. The bounded review found it; I
  folded `AnnAssign` handling + an honest scope boundary before ship.
- **Pipe-exit misread masked a HARD gate as advisory (biggest process waste; a
  repeat-trap recurrence).** I checked `validate_handoff_artifact` with
  `... | tail; echo "rc=$?"`, so `$?` was `tail`'s exit (0), not the validator's.
  The handoff length is a HARD gate (rc=1 at >70 lines), but I read it as a
  non-blocking advisory and trimmed the handoff three times under that false
  belief before running the command bare and seeing the true `rc=1`. This is the
  4th recent instance of the "trusted a misleading green/exit" family
  (`--head-sha HEAD` false-green; boundary-ratchet on an untracked file; `git
  commit | tail` masking a hook abort; now this) — memory-only dispositions have
  not stopped it recurring.

## Critical Decisions

- **Scan + registry hybrid (fail-closed), not a hard-coded list of six.** A
  registry enumerates known surfaces (declaration + consumer pairing); the
  validator ALSO AST-scans the tree so any unregistered declaration fails. This is
  the discovery the plan-critique asked for: the gate fails closed when a new
  declaration appears, rather than trusting a static count.
- **Prose ranking registered as `kind: prose`.** The quality `Recommended Next
  Gates` ranking has no Python dict; registering it as a prose surface with
  anchor-presence checks keeps enumeration faithful to the six #322 surfaces
  without forcing it into the python leak scan.
- **Folded all reviewer NITs rather than deferring.** Each closed a real
  fail-closed hole in the exact guarantee #330 exists for, at a few lines + a test;
  deferring would have shipped a gate weaker than its own claim.

## Expert Counterfactuals

- A **"fail-closed adversary"** lens (the reviewer's stance): the meta-validator's
  only value is that a new declaration cannot escape the contract. Without
  adversarially probing the declaration-form space (AnnAssign, root-level glob),
  the gate would have shipped with a natural escape hatch — the same "a future
  surface leaks the contract" regression class #330 was filed to prevent, recurring
  inside the very tool meant to prevent it. The lesson generalizes: when a gate's
  whole job is to fail closed, the review must attack the closure, not just confirm
  the happy path.

## Sibling Search

- axis: declaration-idiom coverage | location: scripts/validate_inference_interpretation.py find_declaration_dicts | decision: in-scope documented non-claim (not a follow-up) | proof: the scan targets dict literals bound to a name (plain + annotated); non-literal `dict(...)`/dynamic forms are out of structural scope per #330 Non-Goal (no content classifier) and stay owned by per-surface #322 tests; documented in the module docstring and the critique counterweight rather than chased as scope creep.

## Next Improvements

- workflow: when a structural gate asserts a substring anchor against prose,
  choose anchors that live on a single line — markdown wraps text, so a multi-word
  anchor can straddle a `\n` and false-negative. Disposition: memory -> recent-lessons
  digest refreshed this session (source: this retro).
- workflow: when a gate's purpose is to fail closed, the bounded review packet
  should explicitly ask the reviewer to attack the closure (enumerate escape forms),
  not only confirm the registered set passes. The AnnAssign gap proves a happy-path
  review would have missed it. Disposition: memory -> recent-lessons digest refreshed
  this session (source: this retro).
- workflow: never check a gate's pass/fail with `cmd | tail; echo $?` — the pipe
  makes `$?` report `tail`, not the gate. Read the gate's own exit: run it bare, or
  use a `run(){ "$@" >/tmp/o 2>&1; rc=$?; ...; }` true-exit wrapper (which I adopted
  mid-session for the cheap-gate sweep, and which worked). Disposition: memory +
  ESCALATE-IF-RECUR -> recent-lessons refreshed this session; because this is the
  4th recurrence of the misleading-green family, the next instance should not get
  another memory note but a committed gate-runner helper / checklist item that
  captures true exits (source: this retro). NOT filed as an issue now (no new tool
  is warranted yet for a discipline gap I have a working pattern for), but the floor
  is raised: one more recurrence converts this to a tooling/issue disposition.

## Persisted

yes: charness-artifacts/retro/2026-06-07-issue-330-metavalidator-gate-hardening.md
