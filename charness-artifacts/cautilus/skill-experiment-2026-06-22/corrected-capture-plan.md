# Corrected-capture plan (execute after compact)

Root cause of the first run's zero-delta `discard`: the capture task NAMED the
obligation concepts, whose names equal the reference filenames, so the agent
reached refs by filename in BOTH arms and the pointer mechanism was bypassed.
Fix = a generic quality-review task with NO concept/file names + Read-only tools,
so the only path to a routed ref is the variant's SKILL.md pointer (matches the
prior session's proven blind-A/B / reach-via-pointer method).

Obligations themselves (the 7 routed refs) STAY — enumerating what SHOULD be
reachable in the spec is correct; the bug was leaking those names into the agent's
task. Keep spec obligations; degeneralize only the task wording + the capture
prompt.

------------------------------------------------------------------------
## FILE 1 (EDIT): evals/cautilus/skill-experiment/spec.json

Change ONLY `taskPacket.summary` (remove the concept enumeration). Everything
else — experimentId, the 7 sourceCoverageObligations, rubricPhrases, isolation,
skillId, baseline/variant.skillPath — is unchanged.

BEFORE:
  "summary": "Using the quality skill in this repo, identify and read the
   reference files needed to review a repo's quality gates across operability, the
   quality lenses, executable-spec economics, lint-ignore discipline,
   dual-implementation parity, and adapter gate review; report which references you
   consulted."

AFTER:
  "summary": "Using the quality skill in this repo, perform a thorough quality
   review of this repo's gates and skills, following the skill's own routing to
   whatever guidance applies; report which reference files you consulted."

(Also refresh the `_comment` to say the discriminating signal is pointer-routed
coverage gain under a NO-name-hint task; the obligation names are never shown to
the agent.)

Note: the JS test `tests/agent-runtime/extract-skill-experiment-input.test.mjs`
reads spec.json but asserts experimentId / obligations length / isolation / a
routed ref — NOT the summary text. So this edit does not break it.

------------------------------------------------------------------------
## FILE 2 (NEW): evals/cautilus/skill-experiment/capture-prompt.md

The exact, version-controlled prompt piped to `claude -p` for BOTH arms (replaces
the ephemeral /tmp prompt; makes the capture auditable). VERBATIM content:

---8<--- capture-prompt.md ---8<---
You are performing a quality review of THIS repository checkout. Use the repo's
own quality skill as your only guide.

Procedure:
1. Read skills/public/quality/SKILL.md.
2. Follow the skill's own routing from the point of need: open each guidance or
   reference file that SKILL.md (or a file it routes you to) explicitly points you
   to, in order to decide what a thorough quality review of this repo's gates and
   skills should check.

Hard rules:
- Do NOT guess, construct, browse, or glob for files by name. Open a reference
  file ONLY because a file you already read explicitly wrote its path.
- Do not target any specific topic from memory; let the skill's routing decide
  what is relevant.

Finish by listing the exact repo-relative paths of the files you opened and, in
one line each, what that file told you to check. Do not modify any files.
---8<--- end ---8<---

Rationale: keeping "read skills/public/quality/SKILL.md" is NOT a leak — it names
the skill *under test* (entry point), not the reference files. Read-only tools
(below) + "don't guess filenames" force the variant's pointers to be the only
route to a routed ref; baseline (no pointers) reaches fewer → real delta.

------------------------------------------------------------------------
## FILE 3 (EDIT, small): evals/cautilus/skill-experiment/README.md

Under the "Capture" step, add one line: the capture prompt is
`capture-prompt.md`, and it MUST NOT name any reference file or concept (a
name-hinted task lets a capable agent reach refs by filename and defeats the
pointer mechanism — the first 2026-06-22 run's zero-delta failure mode).

------------------------------------------------------------------------
## COMMANDS (runtime; not files)

Worktrees (read-only, isolated; never the install clone):
  git worktree add --detach /tmp/cw-baseline b01cee6b
  git worktree add --detach /tmp/cw-variant  5ded9f3a
  mkdir -p /tmp/se2/baseline /tmp/se2/variant

Capture each arm — SAME model (haiku), SAME prompt, Read-only tools (no Glob/Grep
so the agent cannot scan for filenames), cwd=worktree:
  cd /tmp/cw-<arm> && CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
    CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 DISABLE_TELEMETRY=1 DISABLE_AUTOUPDATER=1 \
    DISABLE_ERROR_REPORTING=1 timeout 600 claude -p --no-session-persistence \
    --output-format stream-json --verbose --exclude-dynamic-system-prompt-sections \
    --model claude-haiku-4-5-20251001 --allowedTools "Read" \
    < /home/hwidong/codes/charness/evals/cautilus/skill-experiment/capture-prompt.md \
    > /tmp/se2/<arm>/transcript.jsonl 2> /tmp/se2/<arm>/stderr.log
  # require result.is_error == false on BOTH; retry / fall to a less-loaded tier on 529.

Extract (cwd-relativized; uses the same spec):
  node scripts/agent-runtime/extract-skill-experiment-input.mjs \
    --spec evals/cautilus/skill-experiment/spec.json \
    --baseline-transcript /tmp/se2/baseline/transcript.jsonl \
    --variant-transcript  /tmp/se2/variant/transcript.jsonl \
    --output /tmp/se2/input.v1.json

Inspect the delta FIRST (this is the whole point):
  # compare baseline vs variant output.sourceRefs ∩ obligations → gained should be non-empty if the fix works

------------------------------------------------------------------------
## GATE — your decision (operator)

- Path 1 (default if unspecified): RE-CAPTURE ONLY. Show the sourceRefs delta from
  the two new transcripts. No cautilus scorer run. Nothing gated.
- Path 2: RE-CAPTURE + SECOND SCORER RUN. The second `cautilus evaluate
  skill-experiment` is the operator-gated "one run" budget — needs explicit GO.
  Then write the new run bundle to
  charness-artifacts/cautilus/skill-experiment-2026-06-22b/ and update latest.md.

------------------------------------------------------------------------
## CLOSEOUT NOTES (execution time)

- The goal artifact is already Status: complete. This correction is a follow-up;
  decide at execution whether to (a) record it as an addendum slice + re-flip, or
  (b) keep it as a standalone corrected-proof note. Do not silently leave the
  closed goal's `discard` as the last word if the corrected run changes it.
- spec.json is a committed surface (prompt-behavior-proof) → run
  sync/closeout after the edit; capture-prompt.md + README live under the same
  already-declared surface glob (evals/cautilus/skill-experiment/**).
- Worktrees: `git worktree remove --force` both; confirm install clone still
  d2cf1b75.
