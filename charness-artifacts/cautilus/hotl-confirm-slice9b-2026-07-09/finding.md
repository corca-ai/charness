# hotl confirming capture after the ledger INLINE-token lift (#410 Slice 9b)

## What ran

**2026-07-09, ask-before-run capture, operator-authorized** (`justification.md`).
Skill change under test committed at `8bdf9fda` (SKILL.md step 5 lifted the
census-INLINE tokens out of `references/ledger-and-dispositions.md`: the
`verified_against.*` dotted sub-fields, the `disposition.*` dotted fields, and
the Operator-Decision-Queue five-field template). Captured via
`capture-skill-run.sh --ref HEAD` with the standing hotl spec prompt.

## Outcome — floor CONFIRMED after the lift

- **Grade vs the unchanged spec: `passed`.** Coverage 2/2 DEPTH references;
  `ledger-and-dispositions.md` genuinely opened (a real shell `cat` of the
  reference while updating the ledger — not a name-mention), exactly the
  post-lift question this capture existed to answer: the doc-open floor is
  still load-bearing because the completion-audit anti-proxy / P4 judgment
  rule and the full disposition semantics stay reference-only.
- The run performed a faithful HOTL loop: separated the edit-time hook (already
  verified in a prior loop) from the commit-time backstop this prompt names,
  classified the proof local-only (proof rule 6), ran the 72-test suite green,
  surfaced the capture harness's own hooks-neutralization
  (`GIT_CONFIG_* core.hooksPath` injection) as a pre-roundtrip constraint it
  had to design around, and committed a ledger closeout inside the worktree.
- Run weight recorded honestly: 18,379,520 total tokens (117,970 output),
  835,853 ms wall, 108 tool calls, 6 waste smells (duplicate_read,
  repeated_edit, repeated_bash) — hotl's proof loop is the heaviest
  representative run in the fleet; threshold-setting for this spec should use
  this baseline, not the pre-lift one.

## Non-Claims

The MIXED split stands as designed: INLINE tokens now in core, anti-proxy DEPTH
reference-only, RCF `[ledger-and-dispositions.md]` unchanged. No matcher or
spec change rode this capture (confirmation only).

Raw capture (worktree/config/stream/credentials) scrubbed — not committed.
