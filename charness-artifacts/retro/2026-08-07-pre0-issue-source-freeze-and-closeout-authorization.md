# Retro — pre-0: issue-source freeze and closeout authorization surface

Date: 2026-08-07

## Context

Reviews the pre-0 bootstrap slice of the unified goal covering issues 514, 515,
and 518 (commit `8bc8e0e4`). The slice built an operating surface, not a repair:
a paginated issue-source capture adapter, a freeze/receipt chain, and a closeout
authorization gate wired into every carrier that can close an issue.

The question that matters next is not whether the surface works — 109 new tests
and two bounded review rounds say it does. It is why a slice whose entire subject
is *identity binding and refusal design* reproduced the repo's own named
identity-churn trap in a brand-new surface, and shipped two refusals that had to be
withdrawn.

## Window

Single session, 2026-08-07: goal activation through pre-0 closeout and commit
`8bc8e0e4`. No push, release, tag, PR, or Cautilus run.

## Evidence Summary

- Commit `8bc8e0e4`: 64 files, +9262/−29. 2867 added lines under `scripts/` and
  `skills/` (root, excluding generated `plugins/` mirrors); 2063 under `tests/`.
- Full suite: 7490 passed, 34 failed in 697s. All 34 reproduce with the slice
  stashed (`publish_state_ledger` ×26, `inventory_marker_rule_measurement` ×2,
  `closeout_bundle` ×2, `final_bundle_preflight` ×3,
  `a_declaration_is_not_its_own_corroboration` ×1). Zero regressions.
- Measured host signals (claude session scope, thread-wide — not a per-goal
  total): 298 function calls, 108 patch applications, 3 subagent spawns, 0 context
  compactions.
- Live capture cross-checked through a second channel: `gh issue view` body
  lengths 4538/3806/7254 and comment counts 0/1/0 matched the adapter capture
  exactly.
- Three delegated bounded reviews (2 round-1, 1 round-2), all `parent-delegated`,
  all envelope-bound read-only.
- `mine_closeout_telemetry.py --detail`: 1448 records examined; the recurring
  `gate_runtime` finding (16 occurrences, peak 475s against a 120s budget) sits in
  a 2026-06-13..15 window. Historical; it does not establish current-owner defect,
  same disposition the prior retro reached.
- Packet Consumed: `charness-artifacts/retro/2026-08-07-003059-packet.md` (clean
  working tree at generation time, post-commit — the changed-surfaces section is
  therefore empty and carried no signal for this retro).

## Waste

Ordered by cost, and separated from the safety work that only *looks* like waste.

1. **A documented repeat trap recurred, in a surface I was building at the time.**
   The recent-lessons checklist says: *"freeze quality artifacts and host probes
   before broad verification so the proof record and the implementation surface
   share one identity."* I started an 11.5-minute full suite and re-froze the
   source artifacts while it ran. The run reported 35 failures, 3 of which were
   my own artifact-binding tests failing against artifacts I was mutating
   mid-flight. The whole run had to be re-read and partly redone. This is the
   single largest recoverable loss in the session and it was written down in
   advance.

2. **The re-bind ritual I built was a three-step manual sequence with a
   hand-written Python step in the middle.** Every re-freeze needed
   `stamp-inspection` → `freeze` → an ad-hoc `python3 - <<EOF` heredoc to copy
   four identity fields from the freeze receipt into the crosswalk. I executed
   that sequence **six times**. The heredoc is not a tool, is not tested, and is
   not discoverable by the next session — a direct violation of this repo's own
   "prefer validators and scripts over prose rituals" rule, committed by the slice
   that was building the validator.

3. **Three length-cap splits were discovered after writing, not before.**
   `resolve_adapter.py` (365/360), `release_issue_closeout.py` (370/360), and
   `check_issue_closeout_commit_msg.py` (492/480) each blocked at verification and
   forced a mid-slice module extraction. `check_python_lengths.py --headroom`
   exists precisely to make the new-module-vs-append call *before* writing; I ran
   it once at the start and then stopped.

4. **The dup ratchet hard-blocked twice, and the second block was pure
   bookkeeping.** First block: 19 new families — legitimate, and consolidating the
   error classes and CLI refusal blocks was a real improvement the gate earned.
   Second block: splitting a module rotated 4 already-classified families to new
   IDs, re-blocking on duplication that had already been reviewed and accepted.
   The gate has `--accept-rotation` for membership *shrink* but nothing for
   split-induced rotation.

5. **One commit attempt was refused by the gate the commit was adding.** My
   message contained a close keyword before a comma-separated list of two
   protected issues, which the comma-list scanner correctly read as one carrier
   closing both. Cost: one full pre-commit gate cycle. Cheap to have avoided —
   the hook is runnable against a draft message file directly.

**Not waste, stated explicitly:** the two bounded review rounds, the round-2 pass
over repaired surfaces, and the re-verification after each repair. Those found
defects that would otherwise have shipped, including two HIGH-severity escapes.
Broad exploration during the capture-adapter design was phase-appropriate for a
surface with no prior art in this repo.

## Critical Decisions

- **Scoped the capture-capability refusal to the capture operation rather than
  adapter load.** Requiring `issue_source_capture` at adapter-load time made every
  non-`gh` adapter invalid and broke four unrelated close/verify tests. The
  refusal belongs where the unprovable claim is made, not on the whole issue lane.
- **Made `verify-closeout` report authorization without gating on it.** By
  readback time the close already happened; refusing there would suppress the only
  channel confirming whether the irreversible act landed, in exchange for a
  protection with nothing left to protect. Recorded in-code as
  `gating: reported-only`.
- **Kept the crosswalk in `bootstrap` so the slice that built the gate cannot walk
  through it.** This is why nothing can close the three protected issues yet, and
  it is a feature.
- **Withdrew two refusals I had added.** The `UnterminatedFence` raise and the
  indented-code splitting rule were both removed on second thought — see North
  Star Alignment.

## Trends vs Last Retro

The prior retro (`2026-08-07-session-retro.md`) named `release-proof-identity-churn`
as a recurrence class: *"evidence identity was frozen after a reviewed ledger
change, causing packet regeneration and an extra bookkeeping cycle."*

This session **reproduced that exact shape in a new surface**. The owner inspection
binds working-tree digests of files the slice itself edits, so every code change
correctly staled the freeze — six times. The prior retro's higher-order diagnosis
("invariants bound at the terminal closeout boundary instead of at evidence
production") is confirmed and extended: the new failure mode is not *late* binding
but *unautomated re-binding*. The trap was known, the class was named, and the new
surface inherited it anyway because nothing in the workflow checks a new
identity-binding surface for a one-command refresh path.

## North Star Alignment

The North Star's rule is: brief a capable judge, and **keep teeth only where a
wrong answer escapes**.

**Where it held.** The irreversible boundary was defended properly. The capture was
confirmed by a different observer *and* a different channel (`gh issue view`, not
the adapter's own exit code). Every ingress refusal is proven to land before the
first side effect, and the refusal tests assert *order* — zero backend calls, no
temp file, no bump — rather than a boolean that could pass with the check placed
after the mutation. The gate refusing my own commit is the standard working as
designed.

**Where I violated it, twice, in the same function.** Both were teeth added where
no wrong answer could escape:

- `UnterminatedFence` raised on a body whose fence is never closed. That made a
  common typo *in someone else's GitHub comment* a hard failure of this repo's
  capture — and, worse, it would have split text into "criteria" that no human
  reading the issue can see as criteria. A refusal that fires on a non-escape and
  contradicts the source of truth is pure friction.
- The indented-code splitting rule, added to stop pasted evidence minting
  criterion-shaped clauses, instead swallowed every nested bullet — including
  regressing the 4-to-7-space band that previously worked.

The second is the sharper North Star lesson because of *how* it was caught: not by
either bounded review, but by my own five-line probe of the actual function. **Two
independent reviewers read the diff and neither found it**; a direct execution of
the code found it in seconds. Reading a refusal cannot tell you what it refuses.

**The unresolved tension.** The freeze's staleness teeth are correct in principle
and noisy in practice: they fire on every slice that edits an inspected owner,
which is every slice. Teeth that fire mostly on non-escapes train the operator to
discharge them reflexively — `stamp-inspection` re-stamps digests with no evidence
anything was re-read, so the refusal is satisfiable at zero cost. That is a
North Star smell the round-2 reviewer named and I have not yet resolved.

## Expert Counterfactuals

**Engelbart — treat (H + LAM + T) as one unit; design T alongside LAM.**
I built the tool (LAM) and left the process (T) as a heredoc I retyped six times.
Engelbart's test is sharp and I failed it: *the moment you find yourself
hand-executing a step of the tool you just built, the tool is unfinished.* The
counterfactual action is concrete — when `freeze` was first written, its very next
commit should have been `refreeze` (stamp + freeze + rebind, one command, tested),
because the second manual repetition was already the signal. That single change
would have removed waste items 1 and 2 together: with a one-command refresh there
is no reason to interleave re-freezing with a broad verification run.

**Ousterhout — define errors out of existence.**
A slice whose entire subject is designing refusals should be the *most* suspicious
of adding one. Ousterhout's rule is that many error conditions are best fixed by
redefining semantics so the condition is not an error. Applied to the unterminated
fence: GitHub renders it as code to end of body, so the correct move was never
"refuse" — it was "match the source of truth and emit one clause," which is what
the second pass did. The counterfactual is a standing question for this class of
work: **for each refusal, name the escape it prevents; if the answer is "someone
else's malformed input that changes no verdict," define it away instead.** Both
withdrawn refusals fail that test in one sentence.

The two lenses converge on the same discipline from opposite ends: Engelbart says
finish the mechanism, Ousterhout says add fewer mechanisms. The slice needed both.

## Sibling Search

Transferable pattern: **a new identity-binding surface ships without a
one-command re-bind path, so operators discharge staleness by hand.**

- same layer: `scripts/critique_packet_lib.py` / `scripts/critique_reviewed_input_binding.py` | decision: `valid follow-up outside the slice` | proof: grepped for `rebind|regenerate|refresh` in the binding module — no match; the packet is rebuilt via `build_packet`/`write_packet` with no single refresh entrypoint, which is the surface the prior retro's `release-proof-identity-churn` was observed on. follow-up: deferred `docs/handoff.md` § Next Session
- abstraction up: `scripts/reviewed_input_identity.py` (the shared sha256-v2 identity owner) | decision: `intentional boundary` | proof: it is a pure identity computer with no artifact of its own to re-bind; the churn lives in its consumers, not here.
- specialization down: `scripts/issue_source_freeze_lib.py` + `scripts/validate_issue_source_freeze.py` (this slice) | decision: `same waste, fix now` | proof: executed the three-step sequence six times this session; a `refreeze` subcommand is the named improvement below.
- mental-model siblings: `scripts/final_bundle_preflight_lib.py` | decision: `diagnostic-only` | proof: it is the one surface in the grep that already exposes a refresh-shaped path (`--restamp`-style handling), so it is evidence the pattern is solvable here, not evidence of the same waste.

## Next Improvements

- **workflow** — Run `check_python_lengths.py --repo-root . --headroom --paths <files>`
  before adding more than ~30 lines to an existing gated file, not after
  verification refuses. Three forced splits this session; the tool exists for
  exactly this call.
- **workflow** — Never start a broad verification run while artifacts are still
  being re-bound. Freeze first, then verify. This is a re-statement of a lesson
  already in the digest, which is why it belongs as a workflow change and not just
  a note.
- **workflow** — Run the commit-msg hook against the draft message file before
  `git commit` when the message references protected issue numbers.
- **capability** — `applied: scripts/validate_issue_source_freeze.py refreeze` —
  stamp-inspection → freeze → crosswalk `source_identity` rebind → validate, in one
  command, covered by two tests (`test_refreeze_restamps_refreezes_and_rebinds_the_crosswalk_in_one_command`,
  `test_refreeze_is_usable_before_a_crosswalk_exists`). Removes the untested heredoc
  from the loop; the direct Engelbart repair.
- **capability** — `applied: issue #534 filed` —
  https://github.com/corca-ai/charness/issues/534. Structural pattern: *a
  content-addressed baseline treats a refactor as new debt.* Triggering instances:
  four families rotated by three length-cap-forced module splits in commit
  `8bc8e0e4`. Destination: repo-local gate
  (`skills/public/quality/scripts/check_dup_ratchet.py`).
- **capability** — `applied: issue #535 filed` —
  https://github.com/corca-ai/charness/issues/535, carrying the critique-packet
  sibling gap and the proposed "every content-digest artifact names its re-bind
  command" rule. Structural pattern: *a new identity-binding surface ships without a
  one-command re-bind, so staleness is discharged by hand.* Triggering instances: the
  prior retro's `release-proof-identity-churn` on the critique packet, and six manual
  re-bind cycles on the freeze surface in commit `8bc8e0e4`.
- **memory** — This artifact, plus the digest refresh, so the
  `release-proof-identity-churn` class carries its *second* instance and the
  "new identity surface needs a re-bind command" rule is inherited rather than
  rediscovered.
- **memory (claim discipline)** — Two docstrings in this slice overstated their
  guarantees (freeze "unforgeability"; clause-digest rewrap tolerance) and were
  corrected only because a reviewer read them adversarially. For proof surfaces,
  the docstring is part of the verdict logic and deserves the same review as the
  code.

## Portable Candidate

- Abstract pattern: any repo that binds a reviewed/frozen artifact to content
  digests of files the work itself edits will generate routine staleness, and
  needs a single tested refresh command or operators will discharge it by hand.
- Triggering evidence: six manual stamp→freeze→rebind cycles this session; the
  same class named as `release-proof-identity-churn` in the prior retro on a
  different surface.
- Intended consumer shape: repos with a freeze/lock/packet-identity discipline.
- Destination: `not portable — insufficient corpus`. Two instances in one repo is
  a repo-local rule, not yet a public skill contract. Revisit if a third distinct
  surface shows the same shape.
- First-prompt acceptance claim (if it later becomes portable): *"every artifact
  that binds a content digest names the one command that re-binds it."*

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-07-pre0-issue-source-freeze-and-closeout-authorization.md
