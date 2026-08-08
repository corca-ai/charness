# Issue #562 Resolution Critique
Date: 2026-08-09

## Decision Under Review

Closing `#562` on the retirement built at `e6a4d67c` — the owner-inspection
locator content pin removed from `scripts/issue_source_freeze_lib.py`, replaced
by existence + containment + set-and-prose binding, with the freeze's
source-snapshot half untouched.

`#562` measured the pin at 0 of 5 true positives: 6 of 20 locators changed in
roughly one day across 8 commits, five re-stamps, every refusal incidental to the
issues' scope. Its second-order complaint is sharper than the noise — the remedy
is one mechanical command, so the gate had trained the see-`stale_inspection`-run-
`refreeze` reflex that would fire on the day a locator's semantics genuinely
changed.

The build already had TWO delegated bounded rounds (12 findings). This critique is
the third delegated reviewer and the one the closeout floor requires before the
close call. Its subject is not the code but the CLOSEOUT: is `#562` genuinely
resolved, is the ledger about to over-claim, and will the class recur.

## Failure Angles

- **Ledger over-claim.** The field most likely to be wrong is `Siblings:` — a
  sibling search that asserts a population of one, or a "proof" that is an
  assertion.
- **The remedy carrying the class it fixes.** `#562` is about a gate that trains
  its own bypass. Binding the artifact's PROSE into `inspection_identity` creates
  a new refusal on a new surface; does it recreate the treadmill?
- **A repair inheriting halves**, this run's measured theme: the round-2 blocker
  was a claim in an unbound region, so ask which claim regions are still unbound.
- **Channel distinctness.** Is the behaviour channel actually distinct from the
  one that produced the fix, or the same pytest loop renamed?
- **A deferral believed rather than verified.** One round-2 finding was deferred
  on a stated reason; the reason itself is a claim to re-open.

## Counterweight Pass

The angle that paid was ledger over-claim, and it paid twice on the same field.

**`Siblings:` was wrong in both directions.** It asserted that `#547`'s subject
was deleted by this change. Only its literal spelling was: `#547` is "refreeze
re-stamps every locator digest silently, so a one-file re-bind can launder
unreviewed drift in the other 18". The digests are gone, so the sentence no longer
parses — but `stamp_inspection` still returns only `{ok, stamped,
inspection_identity}` and reports nothing about what MOVED, while
`rebind_crosswalk` right beside it does return `changed_fields`. And because this
change pulled the locator set AND the artifact's prose inside the identity,
`refreeze` now silently re-stamps strictly MORE than it did when `#547` was filed,
including the very `purpose` field that was round 1's blocker. The generalized
defect is not discharged; it was widened. Recorded as such in the ledger and — after
this critique's own disposition review caught the queue item still describing only the
deletion half — in the operator decision queue too, rather than claimed as resolved.

The same field UNDERSTATED the sibling population by one, and the missing entry
was measured in this same goal. `#561`'s two probe pins are the identical class —
an equality pin against a surface ordinary work mutates, whose remedy is one
mechanical command — measured at 3 reds across 2 files for one ordinary markdown
write, 3 recorded refreshes, remediation spanning 9 surfaces. A sibling search for
`#562` that does not name it asserts a population of one against a record in the
same artifact saying otherwise.

**The prose bind is SOUND, and the argument first written for it was false.** The
docstring said ordinary work edits inspected files constantly and this artifact's
prose "almost never" — and the commit asserting it edited that prose seven times.
The conclusion survives on a different premise: what made the file pin a
wolf-crier was INCIDENCE, not frequency. A third party editing `run-quality.sh`
for unrelated reasons reddened a gate about an artifact they had never opened, so
the refusal was always someone else's problem and `refreeze` was always the
answer. Prose can only move if someone edits THIS artifact, and anyone editing it
is already in the refreeze lane. Docstring corrected to the premise that survives
contact with its own commit.

**The one refusal a legitimate prose edit will hit was the only one with no
remedy.** `inspection_identity_mismatch` said "the declared inspection identity is
not its content's" — no cause, no remedy, no `refreeze` — while
`retired_locator_pin` and `load_inspection` both name their migration. And the
artifact's own `purpose` disclosed only that the locator SET was bound. An owner
fixing a typo in a note would meet an unexplained refusal and conclude the gate is
broken; their second move is `refreeze` until green. That is the reflex,
reconstituted at the one refusal given no explanation. Both fixed in this commit:
the refusal names what it covers and the remedy, and `purpose` discloses the prose
bind.

**Still unbound, and filed rather than fixed.** Every locator carries
`"issue": 514|515|518`, and the artifact makes it a claim — "listing a locator
under an issue asserts the surface was inspected while scoping that issue". The
identity binds `path`, `role`, `note` and NOT `issue`; nothing reads it and the
freeze receipt's `inspected_locators` is paths-only. Flipping a locator's issue
attribution leaves every identity unchanged and `validate` exits 0. This is the
round-2 blocker's own shape half-repaired: the prose was pulled inside the
identity and the structured claim beside it was left outside. The two-round cap is
reached and `#562` did not ask for it, so it is filed; `Prevention:` is worded
narrowly so it cannot be read as "the artifact has no unbound claim regions".

**The deferral was verified, not accepted.** `inspection_identity` does hash
`schema`, `verify_inspection` recomputes the declared identity before the receipt
bind is checked, and `load_inspection` refuses any non-v2 schema outright — so a
v1 artifact cannot reach the receipt bind at all. One honest narrowing the
deferral's reason did not state: transitive binding buys DETECTION, not
LEGIBILITY. A reader holding only the receipt still cannot say which generation it
bound. Residual loss is negligible because the artifact is checked in beside the
receipt with its `schema` in plain sight. Deferral kept, reason sharpened.

**The behaviour channel is genuinely distinct**, checked rather than assumed: no
test in either freeze module invokes the CLI — both call `preflight`,
`stamp_inspection`, `run_refreeze`, and `run_validate` as Python functions, so
nothing reaches `main()`, argparse, exit codes, or `RefusalError` rendering. The
nuance folded into the ledger: `#562`'s behaviour is an ACCEPTANCE, and an exit 0
is also what a short-circuited validator returns, so the field names both
directions — the acceptance AND the refusals that still fire through the same CLI.

Over-worry raised and not folded: a request to prove "the source half is
untouched" by diff rather than by construction. Run anyway, because it was cheap:
`git diff e6a4d67c^..e6a4d67c -- scripts/issue_source_freeze_lib.py` returns five
hunks, all confined to the module docstring, the schema constant,
`load_json`/`require_file`, the `verify_locators` insertion, and
`verify_inspection`. `_rederive_issue`, `verify_capture`, and `_require_contained`
are outside every hunk. The claim is now proven rather than inferred.

## Verdict

`#562` is CLOSABLE. Nothing the issue asked for is undone, the direction is the
operator's own, the Not-in-scope boundary held (`source_snapshot_sha256` is
`9eb2d417e03a` across every re-stamp and a tampered snapshot is still refused),
and the resolution does not reintroduce the class it removed.

Four ledger fields were reworded before the close on this critique's findings:
`Siblings:` (both directions), `Prevention:` (narrowed), `Behavior #562:` (both
directions plus the concrete invocation), and `Debug Artifact:` (the sanctioned
`cite-only` form rather than `none`, since the measurement and its re-confirmation
both have paths). `Jtbd:` and `Root Cause:` were found sound as drafted.

## Non-Claims

- Remote CI is not claimed by this critique.
- The DIRECTION (drop versus narrow the pin) was not re-litigated; the operator
  decided it at filing time.
- `#547` is NOT closed by this work. Its literal subject is discharged and its
  generalized form survives and widened; the decision is the operator's and is
  recorded in the goal's `## Operator Decision Queue`.
- The unbound per-locator `issue` attribution is filed, not fixed.
- Consumer-repo product behaviour remains a standing non-claim.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded reviewer (`bounded-reviewer` typed agent), THREE spawns on this issue — a review of the deletion, a second round reading that round's repairs, and this resolution critique before the close call.
- Requested spawn fields: subagent_type `bounded-reviewer`, no host addressing name, read-only toolset (Read/Grep/Glob).
- Host exposure state: host-defaulted
- Application state: host-confirmed: all three spawns returned findings inline, and each reported the read-only envelope bound with no Bash, Edit, Write, or Agent tool visible.
- Delivery state: findings-received

No host model or effort flag was requested per spawn; the repo's per-host subagent
request does not apply, and typed `bounded-reviewer` agents were used instead.

## Fresh-Eye Satisfaction

`parent-delegated`. Three bounded reviewers in distinct contexts. Each was
boundary-fingerprinted with `reviewer_boundary_fingerprint.py` snapshot/verify —
windows `w-20260808T080751Z-45979` (round 1), `w-20260808T081659Z-66276`
(round 2, reading the repairs), and `w-20260808T090259Z-192061` for the slice-3
sibling round — every verify returning `clean` with empty drift, and every one run
the moment the reviewer returned, BEFORE any repair was made. This resolution
critique is the third delegated reader on `#562` and the one the closeout floor
requires; its four ledger rewordings were applied before the close call rather
than after it.

## Boundary Ownership

- Producer: the agent scoping an issue, which declares which surfaces it read as the owner inspection.
- Consumer: the closeout authorization path, which reads the freeze receipt and the evidence-boundary crosswalk.
- Owning surface: `scripts/issue_source_freeze_lib.py` for the inspection half's rules and identity. The source-snapshot half belongs to `#514`/`#515`/`#518` and was held out of scope rather than adjusted alongside.
- Verdict: owned-correctly

The freeze is a producer/consumer pair and the change lands on the right side of
it. The PRODUCER of the owner inspection is the agent scoping an issue; the
CONSUMER is the closeout authorization path that reads the freeze receipt and the
crosswalk. `#562`'s defect was that the producer's claim was pinned to a surface
neither side owns — the working-tree bytes of files any third party edits — so the
refusal landed on whoever happened to touch an inspected file rather than on either
party to the claim.

The repair moves the binding onto what the producer actually controls: which files
it names, in what role, with what note, and the prose it wrote about them. The
consumer side is unchanged and still reads the same four identity fields through
`rebind_crosswalk`. No claim moved to a different owner and nothing was escalated
to a spec, because the surface that needed narrowing was one module's own.

`#514`/`#515`/`#518` own the receipt this touches, which is why the source-snapshot
half was held out of scope entirely rather than adjusted alongside — that half is
theirs and it is sound.
