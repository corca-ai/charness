# Quality claim-fidelity behavior source

The cautilus observation scoring below is motivated by a real headless
`/charness:quality` run (isolated CLAUDE_CONFIG_DIR, full tools, hooksPath fixed,
completed ~12.6min / 53 turns on 5a9d6fa8), not a synthetic sentinel.

- source-kind: transcript
- source-ref: `/tmp/qcfg/projects/-tmp-qcap/1b89d34e-f3a4-4185-b922-5f1ca342ce53.jsonl` (parent session log)
- source-ref: `/tmp/qcfg/projects/-tmp-qcap/*/subagents/agent-*.jsonl` (subagent tracks)
- note: the observed packet /tmp/qcap-observed.json was built from this full
  session tree by build-skill-execution-observation.mjs. The run opened 0/39
  declared references (tool profile Bash=77 Read=8 Edit=3 Write=2 Agent=1),
  failing the required-reference-read claim. This packet is the evidence cautilus
  evaluate observation scores.
