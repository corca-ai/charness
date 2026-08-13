# Session Retro
Date: 2026-08-14

## Context

This session turned three user corrections into one current-contract cleanup:
retired migration and compatibility surfaces should be deleted rather than
maintained, opened lesson content must survive compaction as readable bytes, and
long-running runners must not hide their lifecycle merely because diagnostic
bodies are isolated.

The resulting slice removes one-shot migrators and legacy aliases as owner
cohorts, makes lesson sessions exact-bundle current contracts, and changes the
standing quality runner from a silent parallel batch into an observable control
plane. It does not claim that every compatibility cohort or every long-running
runner in the repository is already converted.

## Window

The working unit is the current-contract cleanup commit plus its closeout repairs
and artifacts. Publication, issue closure, and installed-host proof remain
outside this retro.

## Evidence Summary

- `charness-artifacts/debug/2026-08-14-lesson-presentation-lost-across-compaction.md`
  proves why a digest without readable content was insufficient; #617 now has a
  deterministic Markdown bundle bound by the receipt's existing byte count and
  digest.
- `charness-artifacts/critique/2026-08-14-current-contract-cleanup-review.md`
  records two bounded review rounds. Round 2 passed 23 focused tests; later
  closeout repairs are explicitly accepted-unreviewed at the two-round cap.
- The first full quality run passed 88 checks and exposed five closeout defects:
  ShellCheck spelling, one stale evidence marker, two strict-algorithm fixture
  omissions, changed-line mutation collateral, and a rotated duplicate family.
  A later post-commit run passed 92 checks and isolated one remaining changed-line
  coverage failure. Five owner tests now cover those refusal/output branches; the
  targeted gate reports every mapped changed file covered while leaving three
  unmapped files explicitly unproven. The final full rerun remains the closeout stop.
- A source scan found 230 output-capture/redirect markers across 147 production
  files. Only 17 capture files declare a timeout of at least 60 seconds, and
  inspection located the high-risk orchestration owners rather than treating
  every captured `git` or JSON query as a runner defect.
- PLR2004 diagnostic inventory found 990 numeric-literal findings: 181 in
  production and 809 in tests. That is evidence for a classified production
  pilot, not a sound global blocking floor.
- Closeout telemetry read 1,704 local records and repeated the already-known
  slow-pytest and over-slice classes. Occurrence is a cost signal, not permission
  to weaken proof or a claim about other repositories.

## Waste

The largest avoidable waste was forcing conversational memory to own exact
lesson content that the producer had already rendered. After compaction the user
had to correct a false `presentation-unproven` claim, and host logs were briefly
considered as the normal recovery path. Saving the producer-owned bytes is both
smaller and more reliable.

The compatibility inventory also showed why keyword-first deletion is noisy.
Strict rejection, immutable historical evidence, and live migration branches all
contain the same words but have opposite dispositions. Deleting producer, tests,
docs, and generated mirrors as one owner cohort reduced rework; line-count or
keyword targets would have damaged capability.

Review identity paid another bookkeeping cycle because broad proof after round 2
found mechanical repairs. The two-round cap was honored honestly, but the better
sequence is to run the broadest affordable deterministic proof before minting the
final binding packet.

The operator then hid the newly visible quality lifecycle again by wrapping the
whole runner in `> /tmp/... 2>&1`. That protected against host-output truncation,
but it also erased the exact start and heartbeat channel the runner had just
added. An observable runner cannot defend itself from a silent outer caller;
archival belongs in its owned failure logs and receipt, or in a stream-preserving
wrapper.

## Critical Decisions

1. **Current-only means one reader, not permissive parsing.** Retired schemas and
   aliases were removed with their migration-only tests; strict rejection of an
   old form remains current safety, not compatibility support.
2. **Persist content at its producer.** The lesson opener writes one exact byte
   sequence to the Markdown bundle and stdout, then writes the subordinate
   receipt. Session logs remain forensic evidence only.
3. **Separate body isolation from lifecycle visibility.** Child diagnostic
   bodies may stay buffered to prevent interleaving; runner start, child start,
   actual completion order, elapsed time, bounded heartbeat, and final receipt
   stream immediately. Callers must not recapture that control-plane stream.
4. **Make the principle broad, the implementation selective.** The repository
   convention and public quality lens now own the default. Conversion targets
   are long-running orchestrators; short atomic probes remain quiet captures.
5. **Do not promote PLR2004 from an untriaged corpus.** Production-only
   classification and a no-increase experiment must precede any blocking floor.

## Trends vs Last Retro

The previous session's “guard adjacent to action” lesson improved materially:
lesson recovery now lives beside the opener rather than in a later transcript
search. The review-binding lesson partly held through explicit packet identities
and a truthful capped-round record, but broad proof still arrived after the
review packet and caused another binding cycle. The historical over-slice signal
also remains active; this large cleanup should not become the template for every
follow-up.

## North Star Alignment

**P2/P3 and the taste precondition held.** Removal proceeded only after checking
that current capability was equal: migration producers had no live callers and
checked-in state was current. The result deletes whole concepts rather than
shaving files or adding another compatibility rulebook.

**P4/P5 held at the proof boundary.** Two independent readers inspected the
runner and current-contract verdict surfaces. Post-round-2 mechanical repairs
are named accepted-unreviewed instead of being laundered into the review verdict.

**A failure signature was avoided.** Neither 990 lint findings nor 147 capture
files became a count-based mandate. Capability and blast radius, not corpus size,
selected the next move.

## Expert Counterfactuals

**Douglas Engelbart — Tool, Language, and Method as one unit.** The durable
change is not a paragraph saying “show progress.” The language names two modes
(`atomic_capture`, `monitored_phase`), the method classifies by duration/fan-out,
and one shared tool should implement lifecycle streaming. Designing those three
together prevents each runner from inventing a new heartbeat dialect.

**John Ousterhout — narrow the interface before adding checks.** A global lint
over `capture_output=True` would create exceptions and suppressions. Two explicit
execution paths with a small monitored primitive make the right behavior easier
to choose and leave short value-returning probes unsurprising.

## Sibling Search

- same layer: release publish helpers, fresh-checkout probes, and requested-review
  commands | decision: valid follow-up outside the slice | proof: captured child
  commands may run for 300–1,800 seconds and can swallow `run-quality` lifecycle
  output | follow-up: deferred docs/handoff.md#next-session
- specialization down: skill A/B, JS mutation, mutant restore, eval fan-out,
  worktree prepare, and skill-surface preflight | decision: valid follow-up
  outside the slice | proof: 60–1,200 second children or completion-order hiding
  were observed in their owners | follow-up: deferred docs/handoff.md#next-session
- abstraction up: every subprocess capture | decision: intentional boundary |
  proof: git/JSON/help probes need exact atomic stdout and have no demonstrated
  long-running control-plane role.
- current owners: `run-quality` and slice closeout | decision: same waste, fix
  now | proof: both now emit structured lifecycle while preserving isolated
  diagnostic bodies and terminal verdicts.

## Portable Candidate

Not a new skill. The cross-repo principle already belongs in the public
`quality` operability lens: long-running orchestrators stream lifecycle while
isolating bodies. The reusable monitored subprocess primitive remains a
repo-owned implementation choice until a second codebase demonstrates the same
API need.

## Lesson Evaluation

Lesson evaluation: {"reason":"missing-start","score_event_count":0,"session_id":"none","status":"not-evaluated"}

This current-contract slice did not open a new declared lesson session. The
earlier #614 presentation is not backfilled from this later retro.

## Next Improvements

- **workflow**: delete compatibility and migration debt by owner cohort only
  after proving current-state capability equality; strict old-form refusal is
  not debt. (recurrence-class: premise-not-checked-against-source)
- **capability**: give long-running child execution one reusable
  `monitored_phase` path and reserve `atomic_capture` for short value-returning
  probes; start with release runners and skill A/B.
  (recurrence-class: closeout-diagnostic-visibility)
- **memory**: treat buffered diagnostic bodies and buffered lifecycle status as
  independent choices; non-interleaving must not create an unobservable control
  plane. (recurrence-class: closeout-diagnostic-visibility)
- **workflow**: do not wrap an observable gate in a silent outer redirection;
  retain evidence through the runner's owned logs/receipt or a stream-preserving
  wrapper. (recurrence-class: closeout-diagnostic-visibility)
- **workflow**: run the broad deterministic gate before minting the final review
  binding whenever the cost is already required for closeout.
  (recurrence-class: proof-surface-review-binding)
- **capability**: classify production PLR2004 findings and trial a no-increase
  baseline before considering a blocking rule.
  (recurrence-class: conservative-static-verdicts)

## Packet Consumed

Packet Consumed: `charness-artifacts/retro/2026-08-14-current-contract-cleanup-packet.md`

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-14-session-retro.md
