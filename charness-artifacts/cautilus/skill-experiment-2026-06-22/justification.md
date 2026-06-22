# Skill-experiment behavior source — quality-ref disposition (2026-06-22)

The cautilus skill-experiment scoring below is motivated by two real headless
`claude -p` quality-task transcripts captured in isolated read-only worktrees
(baseline `b01cee6b` = pre-disposition; variant `5ded9f3a` = the executed
quality-ref disposition). Both arms ran haiku-4.5 with the same prompt and
read-only tools; neither mutated any shared install clone.

- source-kind: transcript
- source-ref: `charness-artifacts/cautilus/skill-experiment-2026-06-22/baseline.transcript.jsonl`
- source-ref: `charness-artifacts/cautilus/skill-experiment-2026-06-22/variant.transcript.jsonl`
- note: cautilus reads the extracted `input.v1.json`; these transcripts are the
  captured evidence of which quality reference files each arm actually read.
