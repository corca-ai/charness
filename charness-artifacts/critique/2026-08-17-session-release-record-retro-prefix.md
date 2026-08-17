# Session Critique — release record and retro prefix slices
Date: 2026-08-17

## Decision Under Review

Three slices taken from the handoff: give the release record a bump-rationale field,
bind two of its unconditional sentences to executed checks, and resolve the retro
validator's owned prefix from the adapter. Four review rounds ran over them.

## Failure Angles

Every angle below was raised by a bounded reviewer, not by the author. The author's own
reading produced none of them, and produced the defects they name. Recorded that way
because an earlier version of this section was written in the author's analytical voice
with no provenance, which silently transferred the credit.

- **A gate added where the repo had already declined one.** The resume lane carried a
  comment naming that gate "a KNOWN GAP, not a decision this slice is entitled to make";
  it was added one function away, which made the comment silently false.
- **A refusal placed in front of a published boundary.** `prepared-claims-review` permits
  `tag_remote` and is not a post-publication phase, so a new refusal there strands a
  release whose only named safe exit is that resume.
- **Operator prose rendered into a machine-parsed document.** The record is read by
  line-anchored parsers, by substring audits, and by a human through GitHub's renderer.
  Three different readers, three different escape shapes.
- **A prefix migrated in one place out of thirty.** The retro output directory is
  answered independently by the validator, the scaffold, the seeder, and the whole
  lesson-ledger subsystem.
- **Tests written to turn a red coverage gate green.** A test that executes a line
  without constraining its behaviour satisfies the gate and proves nothing.

## Counterweight Pass

- The resume-lane gate is not salvageable by re-placing it. An earlier draft of this
  line called it "defensible in isolation and wrong in context"; that softens a finding
  whose entire content is that a gate IS its placement. It could have stranded a
  published release.
- The retro prefix defect was real and consumer-reported, and the fix's blast radius was
  the author's alone. Two attempts, two reverts, and the second was worse than the state
  it repaired.
- Quoting operator prose closes the line-anchored class in one move and survived attack
  in every round. The refusal built on top of it did not survive: it was widened past
  what quoting bounds, then narrowed past what quoting does NOT bound, and only a
  rendered measurement settled where the line is.
- Predictions from reviewers were executed rather than believed. Round 3 predicted two
  surviving mutants: one died (the plugin-root fallback is pinned by a test that reviewer
  had not read, recorded as F10) and one survived (the unasserted absence sentence, fixed
  in the same commit). Round 4 predicted `<script>`/`<style>`/`<textarea>` escape a
  blockquote and flagged its own trace as unmeasured; rendering it confirmed the reviewer
  and refuted the author's narrowing.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume_publish.py | action: fix | note: the added surface gate and focused preflight strand a published prepared stop whose only safe exit is that resume; reverted, with the three reasons recorded at the call site
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_premutation_sections.py | action: fix | note: single-pass heading demotion left `# ## Release State` as a real heading and moved the span the ledger is judged from; demotion deleted entirely because quoting already holds it
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/init_lesson_ledger.py | action: fix | note: adapter-resolving the ledger write flipped a consumer floor from inert to on-and-unsatisfiable while the other lifecycle readers kept the literal; reverted to one literal across the subsystem
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/retro/scripts/resolve_adapter.py | action: fix | note: the validator normalised `output_dir` while the scaffold joined it raw, so one trailing slash reopened the fail-quiet; canonicalisation moved to the single adapter both sides read
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_arg_guards.py | action: fix | note: the raw-HTML refusal matched `<path>` and `<ref>`, blocking a release for ordinary prose, for true positives the blockquote already bounds; narrowed to the one construct that escapes it
- F6 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md | action: fix | note: the handoff asserted resume-lane behaviour the revert removed, and named a script path that does not exist alongside a transcribed count; both corrected
- F7 | bin: bundle-anyway | evidence: strong | ref: skills/public/release/references/version-policy.md | action: document | note: `--bump-rationale` was rejected in a 2026-07-27 critique which priced it at exactly the validator obligation this session then built; the supersession is now recorded where the flag is taught
- F8 | bin: valid-but-defer | evidence: strong | ref: skills/public/release/scripts/publish_release_adapter_preflight.py | action: defer | note: the focused preflight shells out to a bare test-runner binary, so a venv-only install raises where a refusal belongs; deferred to handoff item 6
- F9 | bin: valid-but-defer | evidence: strong | ref: scripts/lesson_evaluation_records_lib.py | action: defer | note: the lesson-ledger directory is answered by ~30 sites on one literal; migrating it is a single slice with its own proof, deferred to handoff item 5
- F10 | bin: over-worry | evidence: contested | ref: scripts/retro_output_dir_lib.py | action: defer | note: a round-3 reviewer predicted the plugin-root fallback was unpinned; the mutant was executed and died, so the prediction is recorded as refuted rather than acted on
- F11 | bin: valid-but-defer | evidence: strong | ref: scripts/critique_enforcement_scope.py | action: defer | note: `PACKET_ABSENT_VALUES` omits `blocked`, the value skills/public/critique/SKILL.md teaches for an honestly skipped packet, so writing the taught value triggers the binding floor and refuses the artifact for SHAs of a packet it declared absent; deferred to handoff

## Reviewer Tier Evidence

Recorded per this repo's own adapter, which prescribes the Claude-host shape. An
earlier version of this artifact wrote `n/a` and `unsupported`, which told a reader
the repo has no tier policy for this host. It has one, in the file the reviewers'
own contract points at.

- Requested tier: `high-leverage` (adapter `reviewer_tiers.high-leverage`)
- Requested spawn fields: typed `bounded-reviewer`, session-model inheritance
  (per-host contract); no host addressing name
- Host exposure state: host-defaulted
- Application state: n/a — this host reports no per-subagent model or effort signal
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. Twelve bounded reviewers across four rounds, spawned unnamed as
`bounded-reviewer`. Rounds 1 and 2 are the operating contract's floor; rounds 3 and 4
were requested directly by the repo owner and exceed it.

Delegation was blocked for the first three commits: a session-level instruction
prohibited spawning until the owner requested review. Those commits shipped unreviewed
and are named in the round-1 findings.

Reviewer boundary: round 1 verified `drift: []` with no parent writes in the window.
Rounds 2 and 3 verified `verdict: parent-attributed`, `drift: []` with every changed
path declared — the parent wrote the repairs after the reviewers finished. Round 4's
window is open at the time of writing.

NON-CLAIM, because this section is the one place the artifact describes its own author's
diligence and nothing in the tree corroborates it. The reviewer runs left no durable
record: no fingerprint snapshot is committed, no per-round findings artifact exists, and
the boundary verdicts above are transcribed rather than cited. A reader can check every
`ref:` in the findings against the code; they cannot check that twelve reviewers ran, or
that any boundary verify returned what this says. That is unfalsifiable testimony and is
labelled as such rather than presented in the same voice as the measured claims.

## Reviewed Input Identity

Packet Consumed: none

`.agents/critique-adapter.yaml` declares `packet_sections`, which opts this repo into
the prepare-packet contract, and the critique skill says to run the prepare runner once
before spawning angle subagents. That step was skipped: reviewers were briefed on commit
ranges and file lists inline. The binding floor is therefore off — not because it does
not apply, but because omitting the declaration is what turns it off. The reviewed input
is identified only by the commit shas named in each round's brief.

The value reads `none` rather than the `blocked <reason>` the critique skill teaches,
because `critique_enforcement_scope.PACKET_ABSENT_VALUES` does not contain `blocked`:
writing the taught value turns the binding floor ON and then refuses the artifact for
three SHA fields describing a packet it just said does not exist. The skill and its
validator disagree about the vocabulary for an honestly skipped packet, which is F11.

Stated in the body rather than in an HTML comment. An earlier version of this section
put the admission inside `<!-- -->`, so a reader saw a heading and nothing under it —
the same hide-the-negative shape this session shipped a release-record guard against on
the same day.

## Boundary Ownership

- Producer: the retro adapter's `output_dir`, and the release helper's payload keys
- Consumer: the retro validator's candidate filter, the retro scaffold's write path, and
  the release record an outside reader gets
- Owning surface: the adapter for the directory; the record renderers for what the record
  claims; the lesson-ledger subsystem for its own literal, until it moves as one
- Verdict: escalated-to-issue-spec

`moved-to-owner` was written first and is wrong: it implies the relocation is in the
diff. Half of it is — the retro directory's canonicalisation moved to the adapter. The
other half was deliberately taken OUT of the diff: the lesson-ledger literal is answered
by every site in that subsystem, and moving one was tried twice and reverted twice. That
half is escalated to a named next-session slice, not relocated.
