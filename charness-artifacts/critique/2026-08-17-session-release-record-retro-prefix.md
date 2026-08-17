# Session Critique — release record and retro prefix slices
Date: 2026-08-17

## Decision Under Review

Three slices taken from the handoff: give the release record a bump-rationale field,
bind two of its unconditional sentences to executed checks, and resolve the retro
validator's owned prefix from the adapter. Three review rounds ran over them.

## Failure Angles

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

- The resume-lane gate was defensible in isolation and wrong in context: the surface
  check itself is sound, and the recorded decision against it was about WHERE.
- The retro prefix defect was real and reported by a consumer; the fix was not the
  problem, its blast radius was. Scope reduction rather than reversal was correct.
- Quoting operator prose closes the line-anchored class in one move and was upheld under
  attack in all three rounds. The over-wide raw-HTML refusal built on top of it was not:
  it refused ordinary English for true positives a blockquote already bounds.
- Two mutants were run against the predictions of round 3. One prediction was wrong (the
  plugin-root fallback IS pinned, by a test the reviewer had not read); one was right.
  Both are recorded rather than only the confirming one.

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

## Reviewer Tier Evidence

- Requested tier: n/a — this host exposes no per-subagent tier control to the parent
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name
- Host exposure state: unsupported
- Application state: n/a — no host signal is exposed for reviewer model or effort
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. Nine bounded reviewers across three rounds, spawned unnamed as
`bounded-reviewer`. Rounds 1 and 2 are the operating contract's floor; round 3 was
requested directly by the repo owner and exceeds it.

Delegation was blocked for the first three commits: a session-level instruction
prohibited spawning until the owner requested review. Those commits shipped unreviewed
and are named in the round-1 findings.

Reviewer boundary: round 1 verified `drift: []` with no parent writes in the window.
Round 2 verified `verdict: parent-attributed`, `drift: []` with every changed path
declared — the parent wrote the repairs after the reviewers finished. Round 3's window
is open at the time of writing and its repairs are parent writes in the same shape.

## Reviewed Input Identity

<!-- No packet consumed: reviewers were briefed on commit ranges and file lists
inline, not through a prepare_packet.py packet. The binding floor is therefore off,
and the reviewed input is identified by the commit shas named in each round's brief. -->

## Boundary Ownership

- Producer: the retro adapter's `output_dir`, and the release helper's payload keys
- Consumer: the retro validator's candidate filter, the retro scaffold's write path, and
  the release record an outside reader gets
- Owning surface: the adapter for the directory; the record renderers for what the record
  claims; the lesson-ledger subsystem for its own literal, until it moves as one
- Verdict: moved-to-owner
