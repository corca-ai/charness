# Session Retro — debug internalization (Plan A) + reference compression (Plan B) + inherited-red repair

Mode: session

## Context

Executed handoff item 1 "debug: internalize method into structure + compress
reference docs". Three commits: Plan A (ce3caa6c) moved the falsifiable-hypothesis
rule INTO the scaffold structure (`## Reproduction`/`## Hypothesis`/`## Verification`
seeds + a `disconfirmer:` honesty marker on the current `latest.md`); Plan B
(853a5174) compressed reference docs (633->565 lines, 11->10 files: deleted
anti-patterns.md, slimmed sibling-search + detection-gap); handoff (2f05a153) was
pruned, which also repaired a PRE-EXISTING broad-pytest red. The operator then
raised a design question that becomes this retro's headline improvement: should
"are retro lessons actually internalized into the next session's behavior?" be a
Cautilus fixture, and is it an AGENTS.md-level eval?

## Evidence Summary

The three commits; two bounded fresh-eye critiques (Slice 1 found a real blocker —
the new forward-only validator fired on the live `latest.md` pointer; Slice 2
clean); full broad standing pytest (3887 passed, 0 failed); the prior re-capture
finding (the `falsifiable-hypothesis-before-fix` FAIL that is Plan A's basis). A
live Plan-A validation re-capture is IN FLIGHT (background `capture-skill-run.sh`
at HEAD) — its grade is NOT yet in, so no claim is made on Plan A's live effect.

## Waste

- **Inherited broad-pytest red diagnosed late.** The full suite was red on
  `test_handoff_plan.py` from session start (committed by 853fb9fc), but I only saw
  it at the FINAL broad closeout because the focused per-slice tests were green and
  masked it. I then spent a detour proving it was inherited (not mine) before fixing
  it. A broad-pytest baseline at PICKUP would have classified the red as inherited
  instantly. Cost: ~one diagnosis detour.
- **Closeout broad-pytest fingerprint friction.** Ran the `--verification-lock`
  closeout twice on a stale cached proof (different fingerprint, expected post-
  commit) before reaching for `--refresh-broad-pytest-proof`. ~1 wasted closeout
  invocation; the message named the fix and I re-read it rather than acting first.
- **Background launch denied — repeat of a known trap.** First capture launch
  stacked a compound `rm -rf` + multi-statement command with `run_in_background`;
  denied. The clean single command was accepted. SAME lesson already in
  recent-lessons.md — it recurred, so a structural fix beats re-noting it.

## Critical Decisions

- **Proactively extracted `_section_declares_marker`** (shared by the cross-file and
  disconfirmer markers) before closeout. Pre-empted BOTH the dup-ratchet rotation
  and a fresh-eye near-clone finding in one move — cheaper than reacting to either.
- **The honesty marker is NOT an anti-gaming gate** (accepts `disconfirmer: n/a`).
  The OUTCOME assertion stays the substance bar. Floor-Addition Restraint call
  recorded at the validator site (keep: recorded recurrence, modeled on the accepted
  cross-file marker, absorbed by the existing preflight).
- **Did NOT retire any floor doc** (Plan C deferred, n=1). Compressed in place plus
  one justified deletion (anti-patterns, rule already in SKILL.md Guardrails).
- **Brought the live current pointer to the new forward-only contract** rather than
  relaxing the validator — "the gap is the artifact, not the rule." Same instinct as
  Plan B: structure carries the rule, the live state must honor it.
- **Pruned the handoff to FIX the inherited red, not mask it** — root cause over
  workaround, and logged the brittle-test root cause for a deeper follow-up.

## Expert Counterfactuals

- **Lakatos / research-programme lens (the operator's insight, sharpened):** a
  lesson written to `recent-lessons.md` is a *hard-core* claim only if its
  internalization is tested; otherwise it is an unfalsified auxiliary hypothesis
  that quietly decays. "Lesson written = lesson learned" is the SAME doc-opening
  proxy fallacy this whole debug arc exists to kill — applied to the operating
  contract instead of a skill. The fix rhymes exactly: internalize recurring lessons
  into STRUCTURE (validators, advisories, preflights — the repo already does some,
  e.g. `advise_floor_addition_restraint`) and judge the CONSUMER side by substance
  (did the next session repeat the trap?), not by "was recent-lessons.md read."
- **Test-as-contract lens (on the brittle handoff test):** a unit test that reads
  `--repo-root .` live state to assert "the handoff is pickup-ready" is a category
  error — it encodes a global MAINTENANCE invariant as a state-dependent unit test,
  so normal artifact drift reds the suite. That invariant belongs to a maintenance
  gate (or a fixture-driven test), not a live-state read.

## Next Improvements

- **capability (headline, operator-originated) — AGENTS.md / operating-contract
  claim-fidelity fixture.** A NEW Cautilus target class (`agent-context`, distinct
  from the 20 `public_skill` specs): capture a session, then judge whether a named
  prior lesson from `recent-lessons.md` was HONORED or the trap repeated — the
  consumer-side analogue of debug's substance assertions. Highest-value failure to
  catch: "lesson written, next session repeats it." Open design rocks: capture unit
  (session vs skill-run), lesson selection, gaming risk. Headed for an issue.
- **workflow:** at session PICKUP, establish a broad-pytest (or last-commit CI /
  closeout) baseline so an INHERITED red is distinguished from a session-introduced
  red immediately, before slice work masks it with green focused tests.
- **memory:** recent-lessons should carry: (1) a forward-only `latest.md`-only
  validator marker must MIGRATE the live current pointer to the new contract —
  whole-tree validation reds otherwise; the fresh-eye critique is the backstop, the
  pointer migration is the fix; (2) standing tests that read live mutable repo
  artifacts (`--repo-root .` over docs/handoff.md, `*/latest.md`) red the suite on
  normal drift — assert via fixtures, not live state.

## Sibling Search

Transferable patterns surfaced this session (four-axis scan):

- same layer (forward-only `latest.md`-only validator markers across skills):
  debug's new `disconfirmer:` marker broke the live current pointer the same way the
  cross-file marker did when added; retro / hitl / quality / issue-closeout share a
  strict `latest.md` validator + current pointer and inherit the exposure on any new
  forward-only marker. decision: same class, diagnostic-only for this slice | proof:
  the broad closeout (`validate_debug_artifact --report-all` whole-tree) caught the
  debug case and the cross-file precedent already migrates pointers on add — the
  backstop exists; the memory lesson covers recurrence.
- abstraction up (standing tests coupled to live mutable repo state): the general
  shape is a unit test asserting a global maintenance invariant by reading
  `--repo-root .` live artifacts. decision: valid follow-up outside the slice |
  proof: static scan only | follow-up: deferred docs/handoff.md#discuss (audit other
  live-state-coupled standing tests; brittle-test root cause logged in Discuss).
- mental-model sibling (producer-vs-consumer fidelity gap): every "artifact/lesson
  written = behavior changed" assumption is the doc-opening proxy fallacy; the
  consumer side of `recent-lessons.md` is unverified. decision: valid follow-up
  outside the slice | proof: not inspected | follow-up: deferred
  charness-artifacts/retro/recent-lessons.md (the AGENTS.md-level fidelity fixture
  in Next Improvements).
- cross-file: scripts/validate_debug_artifact.py and the cross-skill `latest.md`
  validator class are siblings outside this session's debug-only subject files.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-06-30-debug-internalize-compress-session.md
