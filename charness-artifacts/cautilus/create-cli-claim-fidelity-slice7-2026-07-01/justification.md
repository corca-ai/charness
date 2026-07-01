# Operator Log — create-cli claim-fidelity capture (reference-compaction Slice 7)

- source-kind: operator-log

## Approval

- Operator (bae.hwidong@corca.ai) authorized this Cautilus capture on 2026-07-01
  with the explicit session request: "@docs/handoff.md sweep 시작. 코틸려스 실행
  허용" (start the handoff sweep; allow cautilus execution). This is the
  log-backed behavior-proof request the ask-before-run policy requires:
  `plan_cautilus_proof.py --repo-root . --json` returns `next_action: "none"`,
  `must_ask_before_running: true`, `run_mode: ask` (the working tree carries no
  prompt-affecting create-cli diff — the create-cli SKILL.md is captured
  read-only at HEAD), so this log is the operator-log override that names the
  standing basis below.

## Basis under test (Slice 7 create-cli floor: RCF-doc-open → emitted-verb)

- reference-compaction Slice 7 moves the create-cli claim-fidelity floor off the
  re-read proxy. Currently `requiredCommandFragments` pins four docs including
  `command-conventions.md`, whose load-bearing content — the canonical lifecycle
  verb enum (`init` / `doctor` / `update` / `reset` / `uninstall` / `version`) —
  is ALREADY inlined verbatim in `skills/public/create-cli/SKILL.md` step 2
  (lines 44-46). So opening `command-conventions.md` to satisfy the floor is a
  wasteful re-read of a token the run already has in always-loaded core. The
  claim now under test: does a representative `/charness:create-cli` run on the
  pinned multi-command agent-CLI prompt actually EMIT a canonical lifecycle verb
  it ADDED from the convention (a verb NOT already in the prompt), making an
  emitted-token RSF floor genuinely forced? The RSF token is OBSERVED from THIS
  capture, not assumed (the Slice 5 lesson: the impl plan assumed a token the
  live run never emitted).
- create-cli has NO outcome-assertions.json (no substance judge), so the RSF
  token must be non-hollow on its own: the pinned token must be a verb the run
  emits because it applied the lifecycle-verb convention, not one echoed from the
  prompt (the prompt already names `doctor` and `--json`).

## Honest reading guard

- If the run reaches an honest CLI design WITHOUT emitting any convention-added
  lifecycle verb (only the prompt's own verbs), that is a real skill-shape signal
  that the doc-open floor should be KEPT for create-cli — recorded as a finding,
  never fixed by softening the matcher or pinning a prompt-echoed token.
- This capture is also create-cli's FIRST live claim-fidelity capture (it was a
  HYPOTHESIS floor with thresholds omitted), so it doubles as the correctness
  sweep baseline for create-cli.
