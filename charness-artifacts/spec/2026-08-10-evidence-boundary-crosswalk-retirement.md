# Retirement record: the #514/#515/#518 evidence-boundary crosswalk instance

Date: 2026-08-10
Retires: `charness-artifacts/spec/2026-08-07-evidence-boundary-crosswalk.json`
Retains: `scripts/evidence_boundary_crosswalk.py`, its validator, and the
`skills/public/issue` authorization ingress — unchanged, and exported as before.

## What is retired, precisely

The **instance**, not the capability. This repo's checked-in crosswalk artifact is
deleted, so `authorize_closeout` now returns `applies: false, authorized: true,
crosswalk_status: <load refusal code>` for every target in this repo — the same
reported-absence state every consuming repo has always been in. No ingress is
removed, no ingress call site changes, and a consumer that checks in its own
crosswalk gets exactly the behavior it had yesterday.

## Why

**The coordinated repair the instance served no longer exists.** The crosswalk's
global `matrix_state` — one state for three issues — came from
`charness-artifacts/goals/2026-08-07-repair-evidence-boundary-close-514-515.md`,
which treats #514/#515/#518 as *one* coordinated repair. That goal is marked
`Activation: SUPERSEDED`. The single latch is the shape of a dead plan, not a
property of the issues: #514 is a `Future Work` operations enhancement whose own
body calls its solution direction non-binding, while #515/#518 are consumer-repo
bug reports substantially repaired by `892d6b95`.

**The gate demanded COMPLETED-shaped evidence for every close, including a
won't-do.** `authorize_closeout` takes no close reason and branches on none; its
refusal text says the *acceptance matrix that would evidence closing* the issue
does not exist. An acceptance matrix — `producer` / `invocation` / `expected` /
`artifact_path` / `final_reader_route` per criterion — evidences the claim "this is
fixed". A `NOT_PLANNED` close claims "we decided not to do this", whose evidence is
a decision and its reasoning. No acceptance matrix can be written for a decision not
to build, so the only reachable state for these three was refusal, indefinitely.

**Both of the gate's states were terminal, which the north star's P5 forbids.**
`bootstrap` is a terminal red and `complete` a terminal green; neither forces a
question. Reaching `complete` required dispositioning every frozen clause —
measured at 35 (#514) + 24 (#515) + 32 (#518) = 91 — with the row-set floor
refusing partial promotion, so the two substantially-repaired issues were held by
the untouched one.

## Who decided this

The prior session did not merely hold the opposite view; it routed this exact
question to the operator and declined to answer it. From
`charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md`
`## Operator Decision Queue`:

> Decision: whether `#514` / `#515` / `#518` should stay permanently unclosable, or
> whether building the evidence-boundary acceptance matrix is worth scheduling. This
> run did NOT route around the `matrix_incomplete` refusal and does not propose to;
> … **Operator-only because it trades a real protection against three issues that
> cannot otherwise move.**

`docs/handoff.md` carried it forward as `## Discuss`.

**The operator ruled in session on 2026-08-10: full retirement of the instance.** The
ruling was given after being shown the measured cost of the alternative (91 frozen
clauses to disposition, with the row-set floor refusing partial promotion), the
option of adding close-reason awareness instead of retiring, and the option of
dropping #514 from the protected set. The operator's stated reason for choosing full
retirement over a partial one was that a half-retired verdict surface is worse than
either end. This record exists so the ruling is not inferred from the deletion.

## The prior session decided the opposite, and this reverses it deliberately

`charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md`
(`Status: complete`) records the contrary decision twice, in its own words:

> `#514` REFUSED and stays open — the evidence-boundary crosswalk reported
> `matrix_incomplete`, which **is a real protection on `#514`/`#515`/`#518`, not an
> obstacle to route around**

> REJECTED — closing `#518`/`#515` on the static evidence that `892d6b95` repaired
> most of what they report: both carry an explicit re-read obligation demanding a
> live re-run against the consuming repo, and both are protected by the
> evidence-boundary crosswalk in `bootstrap` state.

Quoting it because reversing a recorded decision without reading it is this repo's
named defect class, and doing it silently would be the same failure wearing the
opposite mask. Two responses, and one concession:

**On "the protection is real":** it was real, and it fired correctly on a
`COMPLETED`-shaped close attempt. Nothing here disputes that refusal. What the prior
record does not separate is that the gate cannot distinguish that attempt from a
won't-do close, because `authorize_closeout` reads no close reason — so "the
protection is real" and "the protection can only ever say no" are both true, and only
the first was recorded.

**On the re-read obligation:** stated precisely, because an earlier draft of this
record overstated it as circular reasoning and that was unfair to what the goal
actually says. The goal gives two independent reasons — the per-issue re-read
obligation and the crosswalk — and it never argues "keep the crosswalk because the
issues are held"; it routes that trade to the operator instead. What remains true is
narrower: the crosswalk is one of the two reasons, so retiring it removes one of
them, and the other is disputed on its own terms. The obligation is disputed by the
repo's own handoff,
which records the completed goal's Non-Goals section saying those consumer repos
"have been read repeatedly across sessions and their findings already sit in the
issue bodies. Measurement is not the bottleneck," against a Verification Plan saying
the opposite. This retirement does not adjudicate that. It removes the gate's claim
to adjudicate it, and returns the question to the closeout floor and a human.

**Correction, because an earlier draft of this record over-conceded the point and the
closeout review caught it.** The blanket claim that "the live consumer-repo re-run
these issues ask for has still not been taken" is false as stated, and so is the
handoff's premise that each issue body carries a `Re-read obligation`. Against the
frozen source, only **#518** carries one; #514 and #515 carry none, so #515 is not
externally sourced by the schema and the obligation question does not arise for it.
And #518's obligation — "re-run the five repro commands against a TypeScript consumer
repo before resolving or closing" — was **discharged**:
`charness-artifacts/debug/2026-08-07-issue-518-quality-declaration-reconciliation-debug.md`
records all five run against a read-only archive of the consuming repo at the exact
commit the obligation names, with per-command results.

What genuinely remains un-run is narrower, and each close comment states that instead:
the five commands have not been re-run from a consumer's perspective against the
**post-`892d6b95`** tree. That does not hold #518 open, because the residual it is
closed on — the preset-lineage diff, re-filed as its own issue — is establishable
statically from this tree and does not depend on the measurement.

## Protections that lapse with the instance, named

`bootstrap` was not the only teeth in the artifact. Each of the following is now
inert in this repo, and each is a downgrade to the ordinary baseline every other
issue already has. They are listed because a retirement record that names only
`matrix_incomplete` understates what stops being true.

The first five fired only once a protected key was in play:

- `carrier_out_of_scope` — `release`, `release-resume`, `release-resume-closeout`,
  `publish-execute`, and `pr-body` could not close these three. They now can.
- `foreign_repository` — a qualified near-miss such as `fork/charness#514` no longer
  refuses.
- `not_singleton` — a carrier closing #518 together with an unrelated number no
  longer refuses.
- The mandatory `--manual-target-declaration` cross-check on `close-with-comment`.
  `issue_close.py` returns early on `applies: false`, before
  `parse_manual_declaration`, so for these three the CLI `--number` is again its own
  sole authority.
- `missing_invoked_target` — the companion of the bullet above, and the one that
  stopped a commit-body close keyword or a staged artifact from closing a protected
  issue with no declaration anywhere.

One lapse is NOT protected-key-scoped, and is recorded separately because the
sentence above would otherwise misdescribe it: `normalize_target`'s
`unparsable_target` refusals ran on every target in every carrier whenever a
crosswalk loaded at all. `authorize_closeout` now returns before any normalization,
so in this repo they run on none. Nothing downstream depended on them for a verdict —
they refused malformed input rather than authorizing anything — but the reach change
is repo-wide rather than scoped to three issues.

## What carries the boundary now

Closing a GitHub issue stays in the north star's irreversible set, and nothing here
relaxes that. The three former targets are governed by the same floor every other
issue in this repo passes:

- the `issue` closeout floor (`issue_verify_closeout`, `issue_validate_closeout_draft`,
  and the `close-with-comment` carrier requirements), and
- the required fresh-eye review at the closeout boundary (P4: distinct evidence
  channel, distinct observer).

That floor closed eleven issues in the 2026-08-10 goal, nine of them `NOT_PLANNED`
through consolidation readback.

**The second carrier is classification-dependent, and that dependency is load-bearing
rather than incidental.** `issue_resolution_critique` fires only for
`CRITIQUE_REQUIRED_CLASSIFICATIONS = ("bug", "feature", "deferred-work")`, and the
`consolidated` classification explicitly skips the behavioral-verdict, HOTL,
AI-provenance, and resolution-critique floors — with only an advisory, which does not
block. So the fresh-eye carrier is real only for the classifications that trigger it, and
this record does not claim it uniformly:

- **#515 and #518 close as `bug`**, where `check_resolution_critique` runs. It
  requires a `Critique: <path>` resolving to an artifact that binds the issue number
  and carries a typed `Fresh-eye satisfaction:` line — a cited artifact without that
  line resolves `absent`, which refuses the close. Both closes ran that.
- **#514 closes as `consolidated` into umbrella #582**, where the resolution-critique
  floor does NOT fire. That is not a dodge and not an exception granted here: #582 was
  filed naming #514 as a member, and its own correction records that it absorbed three
  of four because this one was refused by the crosswalk. Executing the consolidation
  the retirement unblocks is the honest disposition; inventing a fresh `deferred-work`
  close for it would be the relabelling that picks a classification for the floor it
  triggers rather than for what the close claims. What carries #514's boundary instead
  is the consolidation readback — four facts checked against the live tracker before
  mutation — which is the floor built for exactly this disposition.

An earlier draft of this section said #514 would close as `deferred-work`. That was
written before the umbrella membership was checked, and it is corrected rather than
quietly dropped.

## What is NOT retired

- `scripts/evidence_boundary_crosswalk.py` and
  `scripts/validate_evidence_boundary_crosswalk.py`: portable capability. A consuming
  repo that needs stricter handling for specific targets checks in its own crosswalk.
- The `issue-source-freeze-bundle` surface's capture / owner-inspection /
  freeze-receipt artifacts and their validator line: the frozen source record of the
  three issues stays as history. Only the crosswalk path and its validator command
  leave the bundle.
- `rebind_crosswalk` already treats an absent crosswalk as a no-op, so `refreeze`
  keeps working against the remaining bundle.

## Non-claims

This record does not assert that #514, #515, or #518 is fixed. It asserts only that
the authorization instance protecting them is retired and that their closes now run
the repo's ordinary closeout floor. It does not claim any consumer repo was
inspected, and it does not change the behavior of any repo that checks in its own
crosswalk.

AI-provenance: authored by an agent session.
