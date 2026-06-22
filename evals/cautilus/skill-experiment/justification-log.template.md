# Skill-experiment behavior source

The cautilus skill-experiment scoring below is motivated by real headless-run
transcripts, not a synthetic sentinel. Fill the refs in before the run.

- source-kind: transcript
- source-ref: `RUNS/baseline/transcript.jsonl`
- source-ref: `RUNS/variant/transcript.jsonl`
- note: the deterministic scorer reads the extracted
  `skill_clone_experiment_input.v1`; these transcripts satisfy the wrapper's
  `source-kind: transcript` gate and are the evidence of which source files each
  arm actually read.
