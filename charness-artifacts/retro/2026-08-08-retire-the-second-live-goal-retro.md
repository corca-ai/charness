# Retro: Retire the second live goal, then close the four filed issues that reach a verdict

Goal: charness-artifacts/goals/2026-08-08-retire-the-second-live-goal-then-close-four-filed-issues.md

## What Happened

Five planned slices, five reached — the first goal in this family to finish its
plan. All five claimed issues are `CLOSED` and verified through the adapter
(`#536`, `#558`, `#557`, `#559`, `#556`), and the second live goal artifact
reached `complete`, so the repo has ONE unfinished goal instead of two.

- **Slice 1 (`#536`)** — closed a probe-drift message built by the predecessor.
  The closeout's own two rounds found seven blockers, all in repairs.
- **Slice 2 (`#558`)** — `(repo, number)` is now enforced at all three surfaces
  that read an issue's state back, with a declared `repo_scoped: owner/repo`
  waiver and an answer-side check.
- **Slice 3 (`#557`, `#559`)** — the fourth copy of the backend rule removed; the
  fifth kept with a reason that is executable rather than prose.
- **Slice 4 (`#556`)** — a check that could only fire for one directory name now
  fires for a consumer-shaped repo, proven at both ends.
- **Slice 5** — bundle proof and this closeout.

## What Created Waste

- **Every review round this run landed its blockers on REPAIRS, not on the
  original analysis.** Eighteen blockers across ten rounds, and not one was in the
  first diagnosis of a defect. The premise checks were right about the defects
  every time; the fixes were where the cost was. That is not waste to remove — it
  is where the budget correctly went — but it means any plan budgeting one round
  per verdict-logic slice is under-budgeted by roughly half.
- **A consolidation was built and reverted.** Slice 3's delegation of the release
  backend was written, smoke-tested, found to double the binary for every existing
  release adapter, and reverted. Cheap because one command caught it; expensive if
  the premise check's word had been taken.
- **The same line moved in opposite directions across two rounds in slice 4**, and
  both moves were defects: too wide (measuring absent tiers) then too narrow
  (measuring only a literal pair). Two rounds to find one invariant.
- **Three length-cap and dup-ratchet blocks** interrupted commits. Each was right
  and each named a real second owner or a real module boundary, so the interruption
  bought structure — but running them EARLY rather than at the commit boundary
  would have avoided re-running the aggregate three times.

## Decisions That Mattered

- **Ordering by leverage rather than by issue number.** Slice 1 retired an entire
  goal artifact, which was the acceptance criterion most at risk of being left
  last and dropped.
- **Reverting the release delegation instead of shipping it.** The premise check
  had refuted the issue's stated blocker and was right; the blocker that actually
  holds was found only by executing the replacement. Shipping on the premise
  check's authority would have changed what command runs during a release.
- **Keeping the fifth copy with an executable reason.** This goal's acceptance
  allowed either one owner OR a measured reason per copy. A differential test that
  demonstrates the binary doubling is a stronger artifact than a consolidation
  that breaks consumers.
- **Refusing to weaken tests to make a build pass.** Two pre-existing tests in
  slice 2 pinned the exact behaviour `#558` reports as the defect. They were
  RETARGETED to the case they were really about (`{limit}`, not `{repo}`) rather
  than loosened, and the reason is recorded in their docstrings.

## Repeat Traps

- **Opening the file is necessary and NOT sufficient.** The sharpest form of this
  family's central lesson, and it is new. At `#536`'s closeout I printed a probe's
  whole `_provenance` block, read three keys quoting counts, and then wrote
  "transcribes no figures at all" two steps later. Write the claim from what the
  read RETURNED, not from the shape the sentence wants.
- **A repair inherits HALVES.** Slice 3's round 2 found three findings with one
  theme: half a layout (source tree but not installed), half an exception contract
  (a typed refusal swallowed by the caller's broad `except`), and half an owner
  (delegating to `resolve_op` while passing `required` empty, one slice after
  building that floor). Ask what a repair did not inherit.
- **A test that re-implements its subject is another copy of the rule.** Shipped
  one inside the slice about copies of rules; it rebuilt a loader's candidate list
  and asserted on its own copy, so it would have passed with the loader deleted.
  Call the function.
- **Pin the SOURCE, not the generated mirror.** A mutant against the source
  survived a pin that read the mirror, because the mirror lags until the next sync.
- **The set a check MEASURES must match the set its predicate ITERATES.** When
  those live in different places they drift invisibly from either site — slice 4's
  adoption iterated every tier while measurement used a hardcoded pair.
- **A comment written to be honest can still be false.** Slice 4's prose about a
  token's writers was written from memory and refuted by opening one reference.

## Next-Time Checklist

1. Budget TWO rounds per verdict-logic slice; the second has never been wasted.
2. Verify the reviewer boundary the moment a reviewer returns, before repairing.
3. Run the dup ratchet and length headroom EARLY, not at the commit boundary.
4. Smoke-test a consolidation before believing a premise check about it.
5. For any claim about where a fact lives, quote the read back into the claim.

## North Star Alignment

`docs/design-north-star.md` governs where this goal's teeth belong, and this run
tracks it more closely than its predecessors did.

Held, **P4 at the irreversible boundary**: all five closes paired a `CLOSED`
adapter readback with a behavioural verdict from a distinct channel — a live
pytest reproduction against a constructed corpus write, constructed stub backends,
module-level probes, and constructed repo shapes. `#558`'s own readback ran
through the close path that same slice hardened, which is the strongest instance:
the fix verified its own closeout.

Held, **teeth where a wrong answer escapes**: the three surfaces `#558` touched
are all state readbacks feeding irreversible decisions, and the waiver that keeps
them affordable is opt-in per call site precisely so a staleness reader's risk
budget cannot be applied to a closeout verifier's.

Held, **a gate that cries wolf costs more than the defect**: slice 4 refused to
widen adoption to "any declared model", refused to measure undeclared tiers, and
`#556`'s acceptance was proven at BOTH ends — fires for a consumer, silent for a
repo that never opted in.

Mis-applied: the family's own **failure signature, a proof surface asserting what
it did not establish**, appeared eighteen times in this run's own repairs. The
signature is not something this repo is drifting toward; it is the thing it
reliably does, and the two-round rule is the only measure that has ever caught it.

## Sibling Search

- axis: same layer | location: `skills/public/release/scripts/publish_release_helpers.py::backend_command` — the fifth implementation of the command-resolution rule | decision: intentional plain-text or non-rendering boundary | proof: runtime/provider roundtrip not needed; executed locally — release templates INCLUDE the binary and the function never reads `release_backend.binary`, while the owner prepends it, so delegating doubles the binary for every existing release adapter. Pinned by a differential test that fails if the pair drifts again | follow-up: none — resolved as a deliberate boundary, with `#559` closed on that measurement
- axis: abstraction up | location: `skills/public/setup/references/default-surfaces.md:83` versus the setup renderer's own gate | decision: valid follow-up outside the slice | proof: static scan only — the renderer is gated against baking a model id into the contract while this reference instructs an agent to write exactly that profile, so an agent following the reference produces an AGENTS.md the same inspector flags | follow-up: deferred-handoff-anchor — recorded in `scripts/setup_critique_adapter_inspection.py` where the predicate reads it; a setup-contract decision with its own owner
- axis: specialization down | location: `skills/public/issue/scripts/issue_verify_closeout.py` at 351/360 code lines | decision: valid follow-up outside the slice | proof: local payload proof — measured by the length gate after the repository check landed; extracting the mismatch record bought back the overflow, and the next addition should split the module rather than squeeze | follow-up: deferred-handoff-anchor — the successor's structural slot
- axis: mental-model siblings | location: `charness-artifacts/probe/2026-08-01-inventory-marker-rule.json` and its sibling floor probe — equality-pinned measurements over a corpus ordinary work mutates | decision: valid follow-up outside the slice | proof: local payload proof — a third probe pins the INVARIANT (`min_residual >= floor`) and has never needed a refresh, so the recurring tax is a property of the pin STYLE rather than of the measurement | follow-up: issue #561

## Next Improvements

- workflow: applied — the successor goal budgets TWO delegated rounds per
  verdict-logic slice as a plan-level cost rather than a rule to remember, on this
  run's measurement that eighteen of eighteen blockers were in repairs.
- workflow: applied — the successor's verification plan runs the dup ratchet and
  length headroom EARLY in each slice, after this run hit three commit-boundary
  blocks that each named a real second owner or module boundary.
- capability: issue #561 — Structural pattern: a pinned measurement asserting
  EQUALITY against a corpus ordinary work mutates converts every routine write into
  a hand re-record indistinguishable from laundering a rule regression. Triggering
  instance(s): the two inventory probes refreshed three times in seven days versus
  a third pinning `>= floor` and never refreshed. Destination: issue #561 (recurs:
  measured across three probes and five re-stamps).
- capability: issue #562 — Structural pattern: an owner-inspection locator pin
  cannot distinguish "the file I reasoned about changed meaningfully" from "someone
  edited it elsewhere", so its remediation is one mechanical command recording no
  basis. Triggering instance(s): 6 of 20 locators changed in a day, five re-stamps,
  0/5 true positives. Destination: issue #562 (recurs: five measured instances).
- memory: applied — this artifact, plus the successor's `## Active Operating
  Frame`, which carries the four traps this run measured that no gate holds:
  opening a file is not sufficient, a repair inherits halves, a test that
  re-implements its subject is a copy of the rule, and a pin must read the source
  rather than the generated mirror.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md
