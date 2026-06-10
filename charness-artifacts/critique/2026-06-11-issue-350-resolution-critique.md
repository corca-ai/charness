# Issue #350 resolution critique (create-skill at-cap propagation guards)
Date: 2026-06-11

## Decision Under Review

Resolving corca-ai/charness#350 with the issue's own two suggested guards,
both additive (no trim of any frozen reviewed surface):

1. One checklist line in `skills/public/create-skill/SKILL.md` Guardrails,
   directly after the propagation bullet, naming the at-cap outcome: trim
   deliberately or file an issue — never silently drop the reciprocal line
   (+1 line; 189/200 total, core 156/160 = exactly the ratchet buffer, ok).
2. A non-blocking near-cap warning in
   `scripts/check_skill_surface_preflight.py` `--path` mode:
   `NEAR_CAP_WARN_LINES = 195`, new `warnings` list in `build_report`
   (id `near_cap`), `WARN` line in `format_human`; status/exit unchanged.

Plugin mirrors byte-synced; 3 new tests pin 195 (fires, non-blocking), 194
(absent), and at-ceiling coexistence with `blocked`. Carrier `Closes #350`
staged on the slice commit; the close lands on the goal's final push lane.

## Failure Angles

- The new warning could change exit codes or JSON shape under a consumer
  (`staged_commit_gate_plan`, `slice_closeout_advisories`,
  `check_artifact_surface_preflight`, `skill_issue_anchor_scan`).
- The checklist line could need more headroom than the at-buffer core has.
- The issue's intent could require the warning in commit-boundary mode too.
- The threshold could silently drift without a pinned boundary test.

## Counterweight Pass

- Slice reviewer (bounded fresh-eye, read-only): **SHIP**, no blockers.
  Verified both guards match #350's ask near-verbatim with nothing dropped;
  non-blocking invariant held in code and live probe (hitl 196/200 prints
  `WARN near_cap`, exit 0); no consumer parses the `--path` JSON shape
  (exit-code/command-string consumers only; no closed key-set test); both
  threshold edges and blocked-coexistence pinned by tests; mirrors `cmp`
  clean; ratchet "4 left (buffer 4, was 5) [ok]".
- Recurrence handling: this fix IS the recurrence guard pair that #349's
  resolution critique proposed (F2+F5 there); the class now fails loud at
  pre-edit preflight AND is named in the authoring checklist. The rejected
  semantic reciprocity validator stays rejected (high-cost/low-precision).
- Nits recorded, not folded: unwrapped ~150-char SKILL.md line (file has
  precedent; MD013 off); "surface preflight" names the tool generically
  (portable-skill ergonomics keeps repo script paths out of public cores);
  warning keys off `current` not `after_preview` (a 190 + preview-10 edit
  lands at 200 unwarned — outside #350's stated >=195-current ask; the next
  preflight on that skill warns).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_skill_surface_preflight.py | action: fix | note: guards implemented additively with consumer suites green (136+10+21 tests) and broad gate 73/0; committed with the `Closes #350` carrier, mirror, and goal slice log in one scoped commit.
- F2 | bin: over-worry | evidence: strong | ref: scripts/staged_commit_gate_plan.py | action: document | note: commit-boundary `--changed-skill-md` mode deliberately unchanged — the issue's named surface is pre-edit (`before prose is written`); warning there would be post-hoc noise.
- F3 | bin: valid-but-defer | evidence: weak | ref: scripts/check_skill_surface_preflight.py | action: defer | note: preview-aware near-cap (warn on `after_preview` >= floor) is a possible refinement outside #350's stated current-lines ask; next preflight on the grown skill warns anyway.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: one bounded fresh-eye subagent reviewer (repo-contract
  pre-approved scope), read-only in the shared parent worktree.
- Requested spawn fields: subagent_type=general-purpose; prompt carried the
  full slice packet (intent, staged diff pointer, invariants, proof,
  non-claims, out-of-scope, five reviewer questions).
- Host exposure state: applied
- Application state: host-confirmed: Agent tool returned a structured
  verdict (SHIP, 9 findings, 24 tool uses, 186s) with independently
  verified repo facts (live warn probe, consumer grep, mirror cmp, test
  boundary pins).

## Fresh-Eye Satisfaction

Issue #350 resolution: the bounded review returned no blockers (verdict
SHIP; nits recorded above as F2/F3 dispositions). Both guards land exactly
as the issue asked; the recurrence class now surfaces pre-edit and at
authoring time. Critique #350 binding artifact: this file.
