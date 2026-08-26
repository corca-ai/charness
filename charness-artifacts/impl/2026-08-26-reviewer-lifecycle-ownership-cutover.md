# Reviewer Lifecycle Ownership Cutover

Date: 2026-08-26 Asia/Seoul
Status: implemented-uncommitted

## Goal

Fold the #728, #729, and #731 friction cluster into one ownership boundary:
the repository-owned critique command accepts semantic review input once,
derives the provenance and runtime paths, and returns a typed lifecycle carrier.
The parent runner owns timeout/interruption cleanup. The old low-level runner
remains a compatibility implementation detail, not the normal operator path.

This is the next large cutover in the active Goal Run amendment after the
risk-adaptive prove/critique cutover. It does not add another child-graph ritual
or a fresh-eye review for this execution.

## Fixed implementation contract

- The command accepts a packet (or packet-generation inputs), review scope, lens,
  and optional reviewed-path manifest. It derives packet identity and reviewed
  input identity from the packet and current repository bytes.
- The command materializes a byte-identical canonical result schema and a
  read-only capability envelope under one ignored run directory. Callers do not
  enter hashes, schema paths, capability paths, ledger paths, receipt paths,
  report paths, or boundary fingerprints.
- Dry-run performs the same path, packet, schema, capability, and boundary
  preflight but never starts a reviewer. A stale packet, schema drift, invalid
  path, or invalid capability is a typed preflight refusal.
- A final lifecycle carrier distinguishes `preflight-blocked` from a started
  run, timed-out/interrupted delivery, and a delivered `pass`/`block` verdict.
  A runner/process failure never becomes a reviewer verdict or approval. The
  carrier also records a `runner_stream` comparison and refuses approval when
  stdout disagrees with the canonical report file.
- The parent boundary starts the canonical runner in its own process group and
  terminates the group on timeout or interruption. Partial ledger/output files
  remain available as non-approval evidence.
- Existing receipt, ledger, schema, packet/input identity, capability, and
  result validation remain authoritative. This cutover only derives their
  inputs and joins their observable result.
- Source and checked-in plugin mirrors stay synchronized. No issue close,
  push, release, tag, installed-host mutation, remote CI, or handoff update is
  part of this cutover.

## Acceptance checks

- A successful dry-run needs no manually supplied hash or generated-artifact
  path and reports all derived identities and paths.
- A positive-control run with a fake backend returns one lifecycle carrier and
  keeps the result approval rule intact.
- Negative controls cover stale packet/input, schema drift, capability refusal,
  runner preflight refusal, started timeout, and delivered `block`.
- Source/plugin command and shared lifecycle surfaces are byte-identical.
- Focused tests, skill contract checks, syntax/lint checks, and docs checks are
  executed and recorded below.

## Closeout evidence

Implementation: complete in the working tree. `run_review.py` is the semantic
CLI; packet/input derivation, capability/schema/path ownership, lifecycle
projection, runner-stream comparison, and process-group signal cleanup are in
the source/plugin mirrors. The low-level runner now keeps the worker receipt
off the public stdout stream, leaving one canonical report carrier.

Verification:

- `pytest -q tests/quality_gates/test_semantic_review_command.py` — 5 passed,
  including dry-run, delivered pass/block, worker timeout, stale packet, and
  parent interruption with a descendant cleanup assertion.
- `pytest -q tests/quality_gates/test_semantic_review_command.py tests/quality_gates/test_reviewer_runner.py tests/quality_gates/test_reviewer_worker.py tests/quality_gates/test_reviewer_worker_report.py tests/quality_gates/test_critique_skill.py` — 57 passed.
- `python3 scripts/check_skill_contracts.py --repo-root .` — pass.
- `ruff check` on changed Python surfaces — pass; `py_compile` — pass.
- `check_python_lengths.py` on changed source/test surfaces — pass; the
  pre-existing shared runner remains an advisory 358/360 code-line warning.
- `scripts/check-docs.sh` — pass (markdown, links, graph, command contracts).
- Source/plugin SHA-256 parity — pass for the semantic CLI, packet/support
  helpers, lifecycle, process, runner, and updated critique docs.

Known verification boundary: `git diff --check` still reports a pre-existing
extra blank line at EOF in `charness-artifacts/gather/latest.md`; it is outside
this cutover and was not edited. The normal commit gate is also not yet closed:
the pre-existing boundary-bypass ratchet reports candidate count `53` versus
baseline `52`, with the new key attributed to the unrelated unstaged
`tests/quality_gates/test_python_length_gates.py` / `scripts/check_python_lengths.py`
work. No `--no-verify` bypass is claimed.

Critique: not-run operator-directed exception; the current execution explicitly
omits forced fresh-eye, handoff, and micro-slice work.

Non-claims: no external issue mutation, issue closure, push, release, tag,
installed-host, remote-CI, or fresh-eye result is claimed here.
