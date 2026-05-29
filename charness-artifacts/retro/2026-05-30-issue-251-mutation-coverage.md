# Session Retro — #251 mutation-gate regression fix

Mode: session

## Context

One achieve goal end-to-end: handoff chunker pickup → `/achieve` shaping (with a
bounded plan critique) → `/goal` activation → 4-slice fix of the #251 mutation
gate regression (subsumes #219). Reviewing what created or avoided waste so the
next mutation-gate fix is cheaper. Goal artifact:
`charness-artifacts/goals/2026-05-30-issue-251-251-mutation-test-regression-on-main.md`.

## Evidence Summary

- The goal artifact (slice log + plan critique findings).
- Commit `86ea3ea` (7 files, +864/-2) and the full-suite result (1784 passed).
- `probe_host_logs.py`: claude host detected — token_count available;
  duration/tool_call/turn_count derivable (not hand-counted here).
- The faithful gate reproduction (`run_test_coverage` + `classify_changed_line_scope_gap`)
  and the manual 8/8 mutation-kill harness.

## Waste

- **One self-inflicted measurement detour.** The first coverage read showed
  `parse_handoff_entries.py` at 0% (whole file uncovered) and I nearly treated
  that as the gap. The cause: a *naive* `coverage run` does not capture
  subprocess-invoked scripts, but the gate uses `parallel=True` +
  `COVERAGE_PROCESS_START` (subprocess capture). Re-running through the gate's own
  `run_test_coverage` corrected it to 86.4% with only the `--with-issues` branch
  uncovered. Cost: ~one extra repro cycle.
- **A 1GB+ full-suite coverage run kicked off then abandoned.** I started the
  faithful repro against the full test command before realizing a test-scoped
  command reproduces the same trio coverage far faster, then killed it (and the
  `pkill` pattern also caught my replacement run — a second restart). Cost:
  ~minutes + a stale large artifact.
- Not waste: the broad exploration in Slice 1 was triage-phase scoping (locating
  the exact predicate), and the plan critique caught a real proof-model error (B1).

## Critical Decisions

- **Reproduce the gate predicate faithfully instead of trusting the naive
  number.** Running the actual `classify_changed_line_scope_gap` over the failing
  base..head turned a guess into an exact line set, and later proved 0-blocking.
- **Plan critique before activation.** It caught B1 (`workflow_dispatch` computes
  no `base_sha`, so it can never prove the blocking-trio fix — only the score
  path), B2 (wrong local tool), B3 (the `indent=2` mutant is `json.loads`-proof).
  Folding these reshaped the whole verification story away from a false
  "dispatch green == gate fixed" claim.
- **Manual mutation harness over a full cosmic-ray run.** Applying each of the 8
  mutations + running its killing test + git-restoring gave deterministic 8/8
  proof in seconds instead of a multi-minute runner dance — and showed the `*,`
  keyword-only markers are killable (not equivalent) via keyword-only enforcement.

## Expert Counterfactuals

- **Michael Feathers (characterization tests):** would have anchored on "what
  observable behavior does each survived mutant change?" first. Applied to the
  `==`→`<=` and `*,`→`/` mutants, this is exactly what made them killable rather
  than dismissed as equivalent — the lens that paid off; worth making the default
  first question for any survived-mutant slice.
- **Don Reinertsen (batch size / queue cost):** would have flagged the 1GB
  full-suite coverage run as an oversized batch for a 3-file question. The
  cheaper test-scoped repro was the right batch; reach for the minimal faithful
  reproduction before the full one.

## Next Improvements

- **workflow:** For any mutation-gate "uncovered changed lines" fix, reproduce
  via the gate's own `run_test_coverage` (subprocess-capturing) scoped to the
  files' test surface — never a naive `coverage run` (misses subprocess scripts)
  and never the full-suite batch first.
- **capability:** A tiny repo helper that, given base/head + a file list, prints
  changed-line coverage + the blocking verdict (wrapping the libs I chained by
  hand) would remove the bespoke repro script each time. Candidate follow-up
  issue.
- **memory:** The two durable traps — (1) gate coverage is subprocess-capturing,
  naive coverage isn't; (2) `workflow_dispatch` has no `base_sha` so it only
  proves the score path, not the changed-line blocker — belong in the
  mutation-testing reference so the next fixer inherits them.

## Sibling Search

Transferable pattern: "a test asserts on a parsed/normalized form
(`json.loads`), so a formatting/indent mutant survives." Scanned for siblings
across other CLI `--json` emitters with NumberReplacer-vulnerable literals.

- Axis 1 (same operator, other files): other `json.dumps(..., indent=N)` print
  sites in `scripts/*.py` whose only tests do `json.loads` round-trips are
  candidate survivors — not audited this session.
- Axis 2 (same test smell): parsed-form assertions over raw-format guarantees.
- Decision: **follow-up** — worth a bounded audit but out of #251's scope; the
  raw-format assertion pattern (critique B3) is the fix template. Not filed as an
  issue this session; noted here as the durable pointer.
