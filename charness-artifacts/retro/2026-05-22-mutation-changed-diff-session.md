# Session Retro: Mutation Changed Diff Fail-Closed
Date: 2026-05-22
Mode: session

## Context

This session hardened mutation sampling so a configured base/head changed-file
diff failure exits before publishing sample manifests, workflow outputs, or
Cosmic Ray config rewrites. The slice also updated exported plugin surfaces,
quality dogfood evidence, handoff state, and debug memory.

## Evidence Summary

- Focused mutation sampling tests passed with 25 tests.
- Fresh-eye review found no ship blockers and identified one implicit
  empty-diff compatibility behavior, which was then pinned.
- Slice closeout passed after correcting doc-link and durability findings.
- `./scripts/run-quality.sh --read-only` passed after restoring the
  `recent-lessons.md` handoff token and keeping the handoff at 70 lines.

## Waste

- The first closeout run caught gitignored reproduction paths in the new debug
  artifact because the reproduction-source marker was added after the artifact,
  not during writing.
- Handoff trimming removed `recent-lessons.md`, causing a later standing-gate
  failure that a targeted memory invariant check exposed.

## Critical Decisions

- Treating failed changed-file discovery as unknown state, not empty state, made
  the sampler fail closed without disturbing no-base or successful empty-diff
  behavior.
- Adding the reviewer-suggested empty successful diff test converted a
  compatibility assumption into a regression pin before closeout.

## Expert Counterfactuals

- Gary Klein lens: run a quick premortem on new durable artifacts before broad
  closeout; it would have named gitignored reproduction outputs as likely
  validator risks.
- Daniel Kahneman lens: after trimming a compact state file, check literal
  invariant tests before rerunning the broad gate; concise edits can remove
  required trigger tokens.

## Next Improvements

- workflow: when a debug artifact cites ignored generated outputs, mark those
  lines `<!-- reproduction-source -->` while writing the artifact.
- workflow: after handoff compaction, run `validate_handoff_artifact.py` plus
  the small invariant test touching the changed token before the full gate.
- memory: keep the next suppression sibling explicit as read-only quality
  changed-path discovery swallowing git failures.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-22-mutation-changed-diff-session.md`
