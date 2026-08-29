# Session Retro

Date: 2026-08-29

## Context

The 2026-09-01 plan's Step 1 (the empty-scope defect class) and Step 3, all four
deferred handoffs the 2026-08-29 detector-blind-class retro left open, and the
release-only lane. Reviewed against the north-star **Purpose** this session added:
charness exists to reduce rework in the repositories that CONSUME it and to make
agentic development there fast. That clause did not exist when the session began,
and adding it changed how several of these items read.

## Window

`ecb91c135..1c9e76ddd` — 14 commits, 65 files, +2382/−534. Three Codex lanes
(#751, #752, #754), all integrated by the parent. Full standing lane green
throughout; the release-only lane went from 17 failed + 21 errors to 0.

## Evidence Summary

- Commits and their gate runs; the standing lane at 8551 passing including
  `release_only`.
- `charness-artifacts/retro/2026-08-29-detector-blind-class.md` — the prior
  retro, and the document this session should have opened first.
- Live probes, not text: `git check-ignore --no-index`, a fresh `git init` +
  `git add .` reproduction, `npm ls --depth=0` on both arms, `cargo llvm-cov
  --lcov`, and a throwaway detector probe over 129 scripts.
- Mutation probes on three of the changes (dup-ratchet projection, the verdict
  template, the empty-scope classifier) to establish the new tests can fail.
- No `metrics_commands` are configured; efficiency claims here are event-based,
  not token-measured.

## Waste

- **I re-derived a prior session's work because I read the plan and not the
  inputs the plan cited.** The plan's header names
  `2026-08-29-detector-blind-class.md` as an input. I never opened it. Inside it,
  already recorded: the strings-first Python listing measured at 53.9 ms with
  *"the dominant cost is API shape, not language"*; the decision NOT to take #748
  slice 2; the fixture-consolidation finding down to the file, the line number,
  and the confirmation that a sweep agent had already proven the minimal fixture.
  I re-measured all of it and presented it as discovery. Cost: the single largest
  block of this session.
- **I optimised before asking what the thing was for — again.** I measured clone
  cost (0.63s / 0.51s / 0.42s) before asking what the cloning tests need. The
  prior retro records the operator making the identical intervention one session
  earlier ("이 테스트 자체 jtbd가 뭐지?"). The answer both times was that the
  clone was not load-bearing for the tests that could drop it.
- **Two of three lane scopes were wrong.** #751 and #752 both returned
  `status: invalid` solely because `--scope` missed a test file. I built each
  scope from `ls tests/ | grep`, which does not look in subdirectories. Both
  candidates were sound and were integrated by hand. `.agents/claude-host.md`
  already carries this lesson.
- **I chased a dependency closure four levels deep before asking whether the
  test needed the real helper.** `check_markdown_inline_code.py` → `runtime_bootstrap`
  → `scripts/runtime_bootstrap.py` → `scripts.repo_file_listing`. The answer was
  that the detector's own test file already owns its message, so the composition
  test should stub it exactly as it stubs the external tool. The machinery I had
  built to install real helpers was reverted.
- **I did not run the length gate after a commit that changed a test file**, and
  pushed it 24 lines over its cap. Found later, by accident, while renaming that
  gate.
- NOT waste: three full-lane runs that each caught something focused runs did not
  (a cross-module private import, a polyglot constant, a skill-ownership overlap).

## Critical Decisions

- ✓ **Refused #748's consumer migration on measurement, then found the stronger
  reason.** Native ownership measured 0.94x — slower than the Python it replaces.
  The prior session had already refused the same slice for a consumer-contract
  reason that outranks the measurement. Reporting rather than executing the plan
  was right; reaching it by re-measurement rather than by reading was not.
- ✓ **Anchored `plugins/` in `.gitignore` after reproducing the failure.** The
  unanchored rule matched a tracked file at another depth. This checkout hid it
  because the file predated the rule; every fresh `git init` + `git add .` did
  not — which is how `charness init` bootstraps a managed checkout. 36 of 38
  release-lane failures resolved. This is the session's clearest instance of the
  Purpose clause: every gate here was green while the consumer path was broken.
- ✓ **Deleted the dead publish driver instead of testing it.** The only execution
  coverage of an irreversible ordering ran through a function whose own docstring
  said it was unreachable in production. Repointed the tests at the owner the live
  path calls, then deleted 82 lines.
- ✓ **Kept the detector inventory unarmed.** The prior retro asked for a reading
  surface and said explicitly that whether a gate follows is a later question.
  Shipping it armed would have been the treadmill this repo has already named.
- ⚠ **Wrote the north-star Purpose section as narrative first.** It cited an issue
  number, two dates, and two incidents. Corrected to principle-only after the
  operator caught it; the same pass removed pre-existing violations of the same
  rule elsewhere on the page.

## Trends vs Last Retro

Against `2026-08-29-detector-blind-class.md`: its two named traps both recurred.
*"When a plan's value rests on a quantity, measure the quantity before writing
the plan"* held — every proposal this session carried its measurement. But its
sibling, *optimise before asking what the thing is for*, recurred within one
session, and its four deferred handoffs sat unread until the operator asked why
work was being redone. The prior retro's improvements were written down and not
routed into anything a session opens.

The standing suite grew 8422 → 8551 while the release-only lane went from broken
to green; three of that lane's failures had been red since the prior session and
nobody was looking.

## North Star Alignment

The **Purpose** clause added this session is the finding, not a decoration. The
document stated a method and a standard and never named the goal, so *"serve the
goal first"* in Operating stance had no referent — and a session could optimise
the harness against itself and pass all five facets. Several items here would
have read differently against it: the `.gitignore` defect is a Purpose violation
of the first order (consumer bootstrap broken, every local gate green), while the
listing micro-optimisation was harness-facing work that no consumer would have
felt.

**P3 (principle over rulebook) failed inside the gate that enforces prose
honesty.** `check_regenerable_facts` is configured for `docs/**`, does not exempt
the north star, ran clean — and missed every number on the page, because its
detector is *digit + space + an enumerated noun*. Spelled-out numerals, unit
suffixes, hyphenated compounds, and nouns outside the list all pass. The document
that says an enumerated list *"rots and still misses the case it never listed"*
was unguarded by an enumerated list.

**P5 held on the one irreversible surface touched**: the release closeout tail
now runs under test through the path a release actually takes, and the Rust floor
was built unarmed rather than promoted to blocking the day it was written.

## Expert Counterfactuals

- **Douglas Engelbart — treat (H + LAM + T) as one unit.** The tool that failed
  this session is the SESSION-START PATH. Improvements were produced correctly
  (retro written, handoffs named, lessons ranked) and then not consumed: the plan
  cited its inputs in prose, and prose citation is not a mechanism. Engelbart's
  move is not "write a better lesson" — it is to make the next session's opening
  read what the last one produced, by making the plan's `Inputs:` a thing the
  session opens rather than a thing it mentions. The deferred handoffs are the
  same shape one level down: four of them sat in a retro's Sibling Search with
  nothing that surfaces them at planning time.
- **Don Norman — the error is in the affordance, not the operator.** Three
  separate defects this session share one shape: a rule whose enforcement is
  scoped narrower than the rule. `skip_if_doctor_passes` licensed skipping work a
  doctor never checked; the empty-scope rule was enforced over a hand-written 14
  of 129 detectors; the prose-honesty rule was enforced over an enumerated noun
  list. Norman would not add a fourth rule — he would ask, for each existing one,
  *what does this mechanism actually see*, which is precisely the inventory this
  session shipped. The inventory should therefore be READ next session, not
  extended.

## Next Improvements

- workflow — **a plan's cited inputs are opened before the plan is executed.**
  Structural pattern: an artifact that names its sources in prose is trusted to
  have absorbed them, and the next session inherits the summary instead of the
  source. Triggering instance: this session re-derived a prior session's
  measurements, decisions, and a fully-diagnosed follow-up. Destination: the
  next-session prompt (below) and `docs/handoff-and-session-start.md` if one
  exists. `recurs:` — the prior retro's improvements were also written and not
  routed.
- capability — **make the prose-honesty gate advisory-with-judgment rather than a
  wider regex.** Operator-specified design: the detector is heuristic, so accept
  false negatives, surface it as a pre-commit ADVISORY on changes to `AGENTS.md`,
  `README.md`, `docs/**/*.md`, and let an agent judge the flagged text against the
  warning's own stated rule rather than widening the pattern. `novel:`
- capability — **the detector inventory is a reading surface with no reader.**
  It reports 13 detectors asserting success over an unestablished scope and 48
  whose honesty is prose only. Next session reads it and dispositions the 13.
  Leaving it unread makes it exactly the cost the Purpose clause names. `novel:`
- memory — the four deferred handoffs from the prior retro are now closed;
  this artifact and the next-session prompt carry what replaced them.

## Sibling Search

Transferable pattern: **a rule enforced over a hand-enumerated subset of the
population it names.**

- same layer: other quality gates keyed on literal lists —
  `check_test_repo_copy_invariants` (five identifiers, made transitive last
  session), `check_skill_ownership_overlap` (an allowlist), `dup_ratchet`
  (`scope_paths`) | decision: diagnostic-only | proof: each already publishes its
  own scope in its payload (`scope_coverage`, `did_not_judge`, `unscoped_paths`),
  so the enumeration is visible to a reader rather than silent.
- abstraction up: the empty-scope rule itself | decision: same waste, fixed this
  session | proof: `inventory_empty_scope_honesty.py` replaces the discovery half
  with a glob and observation; 129 detectors against the list's 14.
- specialization down: `check_regenerable_facts`'s noun list | decision: valid
  follow-up outside the slice | proof: measured against five real phrasings from
  the north star, one hit and four misses | follow-up: the advisory-with-judgment
  improvement above.
- mental-model siblings: adapter defaults that license an action from an
  unrelated verdict (`skip_if_doctor_passes`) | decision: same waste, fixed this
  session | proof: the skip now requires a declared coverage intersection.

## Portable Candidate

- Abstract pattern: **probe every detector in a repo against an empty scope and
  bucket what it says**, separating "refused", "passed and said it established
  nothing", and "asserted success over nothing".
- Triggering evidence: 129 detectors here, 13 asserting success over an
  unestablished scope, 2 carrying a machine-readable marker against 48 whose
  honesty is prose only.
- Intended consumer shape: any repo with a gate suite it did not write in one
  sitting.
- Destination: `not portable yet — the bucket markers are this repo's own
  vocabulary`. The method transfers; the marker list does not. Revisit once the
  typed empty-scope field exists as a contract rather than a phrase list.
- First-prompt acceptance claim: *"tell me which of my gates pass over a scope
  they never established"* returns a bucketed list with per-detector evidence.

## Packet Consumed

n/a (adapter declares `packet_sections`, but this retro was written from the
live session thread and direct probes rather than a prepared packet)

## Persisted

Persisted: yes: charness-artifacts/retro/purpose-and-the-unread-input.md
