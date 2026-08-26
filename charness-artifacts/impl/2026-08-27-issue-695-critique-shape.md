# Implementation contract — #695 critique execution shape

Date: 2026-08-27 Asia/Seoul

## Decision

Make `scripts/critique_reviewer_evidence.py` the executable owner of the
reviewer-tier execution-mode field and its two valid values. Critique scaffold
output, prepare-packet JSON/Markdown, and the typed issue closeout observer use
that owner. Existing legacy artifacts may omit the new field; new producer
output must include a valid value, and typed-subagent closeout remains
fail-closed.

The source of truth remains `skills/public/`; the checked-in
`plugins/charness/` tree is synchronized by export. No consumer repository,
installed host, hosted enforcement, conditional trigger execution, or release
surface is claimed by this slice.

## Owned surface

- `scripts/critique_reviewer_evidence.py` and its plugin mirror
- `scripts/critique_packet_lib.py`, `skills/public/critique/scripts/scaffold_critique_artifact.py`,
  and their plugin mirrors
- `skills/public/issue/scripts/issue_resolution_observer.py` and its plugin mirror
- critique references and focused producer/consumer tests
- evidence-led debug artifact and this implementation contract

The standalone issue observer also owns its repository-root import-path setup
when it loads the canonical shape module. The implementation does not mass
rewrite historical critique artifacts or add a universal changed-line gate.

## Acceptance checks

- Every new scaffold and prepare-packet producer emits `Execution mode` with a
  valid `file-backed-worker` or `typed-subagent` value.
- Typed-subagent closeout refuses missing, placeholder, malformed, or
  non-typed execution-mode evidence.
- Malformed packet runner input defaults deterministically without producing an
  invalid shape.
- Direct standalone issue-shape execution remains importable.
- Source and exported plugin mirrors remain identical.

## Verification receipt

- Base SHA: `7bfab87ee7348ce9662dcc01016791cfa0dc7d4a`
- Target SHA: `5941475b4c724257b4aa5b6c9115fd9e7485931e`
- Target commits: `01bc266e0`, `974c654b9`, `5941475b4`
- Proof branch: `proof/issue-695-critique-shape-coverage-20260827`
- Proof path: `/tmp/charness-695-proof3-20260827`
- Proof path scope: the owned source/plugin files above, the two critique
  reference files, `tests/test_critique_scaffold.py`,
  `tests/test_critique_prepare_packet.py`, and
  `tests/quality_gates/test_changed_line_reviewer_consumer_gaps.py`.
- Clean named proof-worktree preflight and post-status: pass; branch was not
  detached; `worktree doctor --require-isolation`: pass.
- Focused standing command over scaffold, packet, consumer-gap, issue-observer,
  and enforcement-scope tests: 137 passed.
- Issue-mandated standing target
  `tests/quality_gates/test_describe_goal_closeout_shape.py`: 19 passed.
- Narrow changed-line proof for the verdict/proof surface: 4 mapped files,
  every changed line covered, `blocking_targets: {}`, producer exit 0.
- Mapped producer initially found a standalone-import regression; the base
  three-test control passed, the repair passed the same three tests, and the
  final mapped producer passed. This repair is included in the target above.
- Export to a temporary host layout, source/plugin parity, ruff, `py_compile`,
  Python-length validation, debug-artifact validation, and `git diff --check`:
  pass. The length validator reports its existing 479-line advisory warn band
  but no hard failure.
- Python caches were kept outside the proof tree; proof-tree pre/post cache
  inventory: none.

## Critique and non-claims

`Critique: blocked` for a forced fresh-eye review: the explicit operator
direction for this goal omits that workflow, and this host exposes no
Agent/subagent capability. This is not fresh-eye approval. No claim is made
about host-attested process distinctness, installed-plugin behavior, consumer
repository adoption, hosted/remote CI, push, release, tag, or issue closure.
No handoff update or micro-slice record is introduced.
