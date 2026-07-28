# A second bounded review round for verdict-logic slices
Date: 2026-07-28

## Decision Under Review

Three operator decisions from the S27/S29/S33/S34 closeout, made effective from the next
session: (1) a slice that changes VERDICT LOGIC on a proof surface owes a second bounded
review reading the repaired surface, capped at two rounds; (2) sweep lead R9 is an accepted
residual rather than work; (3) R8 is next session's item 1.

## Failure Angles

- **A new rule that contradicts an old one is worse than no rule.** The pre-existing
  once-per-slice critique clause says to rerun only when later edits introduce a new risk
  boundary — and the repairs ARE those later edits, so a careful reader could use the older,
  more specific-sounding clause to skip the new obligation entirely.
- **An unaffordable trigger is an ignored trigger.** ~60-163 proof-surface files are touched
  per week against a population of ~135, so "changed a proof surface" would fire on nearly
  every slice and be dropped in practice.
- **A rule that ships as prose has not shipped** — the repo's own measured trap, twice.
- **A pinning test can be the same defect in test form**: presence-only substring checks
  pass on a sentence that negates the rule they claim to pin.
- **An accepted residual can read as a hole nobody noticed** unless the record says what
  stays unguarded and why the alternative was rejected.

## Counterweight Pass

- The two-round rule was scoped DOWN rather than up: verdict logic instead of files, with
  renames/comments/import-only edits excluded, because the affordability measurement lives
  in this repo and says a broad trigger cannot be honored.
- The cap at two rounds is a deliberate stopping rule, not an oversight. Iterating until a
  round comes back clean is unaffordable, the marginal round is worth less each time (round
  1 found six, round 2 four), and the honest move is to record round-2 repairs as
  accepted-unreviewed rather than to imply they were reviewed.
- R9's fix was REFUSED in favor of accepting the residual: widening the backstop to fire on
  an empty baseline would false-refuse every genuinely clone-free adopting repo — a real
  refusal traded for a warning nobody can act on. The arrival path was closed instead (R7).
- Round 2 of THIS slice found a fourth copy of the rule in `docs/handoff.md` carrying all
  three defects round 1 had fixed elsewhere — sibling propagation inside the repair, on the
  surface a fresh session reads first. That is the rule justifying itself on its own diff.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md:26 | action: fix | note: round 2 found the handoff carrying a FOURTH copy of the rule with the touched-the-file trigger, the "scoped to the repairs" phrasing, and an unconditional two-round count — every defect round 1 had fixed on the other surfaces, on the surface a pickup reads first. Rewritten to the verdict-logic trigger, the repaired-surface scope, and the discharge clause; the pinning test cannot see this file, which is why it survived round 1.
- F2 | bin: act-before-ship | evidence: strong | ref: docs/conventions/operating-contract.md:71 | action: fix | note: "notwithstanding the once-per-slice clause" overrode an ARTIFACT-count clause when only the REVIEW count was meant, so it read as two critique artifacts and two pointer swaps per slice — contradicting the exemplar it cites two lines later. Now says the override is on the review count and it stays one artifact recording both rounds.
- F3 | bin: act-before-ship | evidence: strong | ref: docs/conventions/operating-contract.md:92 | action: fix | note: three surfaces disagreed on the stopping rule ("a round" that finds nothing vs "a first round" vs an ordering doc that terminates with round-2 repairs unreviewed), leaving both "ship, the cap is two" and "spawn round 3" available. The cap is now stated at two everywhere WITH its cost named: round-2 repairs ship unreviewed and are recorded as such.
- F4 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_closeout_discipline_propagation.py:113 | action: fix | note: the pinning test was presence-only, so a rewrite negating the rule ("does not owe a second bounded review") passed every assertion while keeping every substring. A negation guard was added and proved by rewriting the rule negatively and watching the test fail; two whole-file asserts were also moved onto the rule's own block.
- F5 | bin: act-before-ship | evidence: moderate | ref: docs/conventions/operating-contract.md:88 | action: fix | note: the trigger was undecidable for the two cases that actually escaped — a weakened test assertion (sweep R14) and a new status a downstream reader keys on (R10/R12, where the producer still decides the same thing and the hole lives in an untouched reader). Both are now named in scope, with round 2's packet defined as the subsystem's readers for the second case.
- F6 | bin: act-before-ship | evidence: moderate | ref: docs/conventions/operating-contract.md:85 | action: fix | note: the rule cited `new_proof_surface_advisory.py` for its measurement while that file argues an edit-triggered check is useless, so an agent following the citation met an authority against the rule that sent it there. The reconciliation is now stated (new verdict logic inside an existing file, and the repairs, ARE births), along with the fact that the advisory's marker is matched only against newly-added paths, so for a changed surface the critique artifact is the record.
- F7 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md:8 | action: fix | note: the sweep asserted "every other row is still open" while twelve leads-table rows were REPAIRED and one DISPOSITIONED, and its status vocabulary denied any second done-meaning status existed. The vocabulary block now declares the leads table's three statuses and the absolute claim is scoped to the main findings table.
- F8 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_closeout_discipline_propagation.py:66 | action: fix | note: `_bullet_blocks` dropped markdown lazy continuation and parsed fenced examples as list content, so a legitimate reflow or a doc quoting the rule could fail the test with the rule intact. Fixed in the same pass since the test is the rule's only mechanical tooth.
- F9 | bin: valid-but-defer | evidence: moderate | ref: skills/shared/references/fresh-eye-subagent-review.md:114 | action: defer | follow-up: deferred docs/handoff.md next-session backlog | note: the shared reference's copy is unpinned by any test, so the drift that produced F1 could recur there silently. Deferred rather than bundled: pinning a vendored reference needs a portability decision about what a consuming repo is allowed to change.
- F10 | bin: over-worry | evidence: weak | ref: docs/conventions/operating-contract.md:66 | action: defer | note: the once-per-slice clause's meaning for non-proof-surface slices is untouched — the carve-out bullet states it explicitly — so the "notwithstanding" phrasing does not leak beyond this class.

## Reviewer Tier Evidence

- Requested tier: medium
- Requested spawn fields: agent type `bounded-reviewer` (read-only Read/Grep/Glob), no host addressing name, session model inherited per the Claude Code host branch of the per-host subagent contract.
- Host exposure state: host-defaulted
- Application state: host resolved the typed read-only agent and inherited the session model; no per-subagent model/effort control was requested on this host.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — two bounded rounds on this contract slice, dogfooding the rule it adds.
Round 1 read the original change (misunderstanding/over-literalization lens) and returned
three blockers; round 2 read the REPAIRED surfaces and returned three more blockers plus
seven findings, including the fourth-copy drift in the handoff that round 1 could not see
because that text was written after it. **Round-2 repairs are accepted unreviewed**, which
is the cap this rule sets and the residual it names — recorded here rather than implied.

## Public Skill Validation Decision

This slice changes no skill behavior: it adds a `### Known residual` subsection to the
`quality` skill's dup-ratchet reference (documenting a decision about behavior that shipped
in the previous commit) and a `## Two Rounds For Verdict-Rendering Code` section to the
shared fresh-eye reference. The `quality` routing/prompt contract, its acceptance evidence,
and the artifact it produces are untouched, so the checked-in consumer case in
`docs/public-skill-dogfood.json` stays frozen and still validates. `quality` is
`hitl-recommended`; the scenario worth a maintainer's eye is the residual itself — an
adopting repo that already holds an empty gate baseline gets no zero-family warning — which
is why it is written into the degrade ladder an adopter reads rather than left in a commit
message. The shared fresh-eye reference change ships to consuming repos as guidance only and
explicitly leaves the trigger definition to the adopting repo.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with `- Packet consumed: <packet-path>` plus three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. That `Packet consumed:` line is what turns the binding floor on. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: the operator's approval of the three decisions, plus the 2026-07-28 slice that measured the two-round evidence.
- Consumer: the next session's agent deciding how many review rounds a slice owes, and any adopting repo reading the vendored fresh-eye reference.
- Owning surface: `docs/conventions/operating-contract.md` Critique Discipline owns the rule; `AGENTS.md` and the shared fresh-eye reference carry pointers; `skills/public/quality/references/dup-ratchet.md` owns the R9 residual because that is where an adopting repo reads the degrade ladder.
- Verdict: owned-correctly
