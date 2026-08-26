Closes #693

JTBD: make critique-round recording prove which delivered worker execution
produced the semantic findings, so a same-context or delivery-only substitute
cannot be recorded as a distinct review result.

Root cause: `record_round_findings.py` accepted arbitrary stdin or a raw findings
file and recorded only the boundary/window and findings digests. It did not
consume the delivered worker report, validate its receipt/ledger/result chain,
or bind the reviewer execution identity to the recorded typed result.

Debug artifact: `charness-artifacts/debug/2026-08-27-issue-693-reviewer-provenance.md`

Siblings: decision: make the delivered worker report and its typed `result.json` the only findings carrier, require explicit attempt/producer/scope and joined packet/input/parent/boundary identities, and retain pass-only approval consumers; proof: the focused and related standing suites exercise accepted block delivery, raw-findings refusal, missing producer identity, snapshot mismatch, plugin export, and final-consumer validation.

Resolution brief: keep the existing file-backed worker delivery chain as the
source of semantic findings, add an explicit reviewer execution identity to the
round record and receipt, and refuse unbound raw findings before writing a round.

Implementation: commit `35ca8bc79a82db7cd7adbd24d85b358dae8c4ee1` updates the
canonical critique recorder, shared worker-carrier validation, checked-in plugin
mirrors, skill contract, and focused tests. Evidence receipt updates are in
`caaea25e5`.

Prevention: raw `--findings-file`/stdin recording is removed; the recorder now
requires a delivered worker report whose receipt, ledger, typed result, and
identity joins validate before the round is written. Block/defer delivery remains
recordable evidence but is not approval.

Boundary #693: owned-correctly — Charness owns the local recorder, delivery-chain
validation, typed result identity, and plugin export parity. The host's ability to
create a genuinely distinct process or typed subagent is not asserted here.

Verification: base `48a69fd6b1117f403dcec2a0e18994fc32ee3cce`, target
`35ca8bc79a82db7cd7adbd24d85b358dae8c4ee1`, branch
`proof/issue-693-reviewer-provenance-20260827`, path
`/tmp/charness-693-proof-20260827`; focused standing test `8 passed`, related
combined standing tests `76 passed`; debug artifact validation, ruff, Python
length, compile, diff check, source/plugin parity, and pre-commit all passed.
The proof worktree was a clean named branch before and after execution, with
pytest and Python caches outside the worktree.

Behavior #693: local-only-by-contract — the checked-in recorder's typed worker
delivery and final-consumer fixtures pass locally; no installed-host, hosted
subagent, or remote provider behavior is claimed.

Probe record #693: local-only-by-contract

Critique #693: blocked explicit operator direction omits forced fresh-eye review and this host exposes no Agent/subagent capability
AI-provenance: authored by an agent session.
Manual close reason: operator-directed-manual-close.
Manual fallback reason: operator-directed-manual-close.

Explicit non-claims: no universal changed-line proof, forced fresh-eye review,
handoff update, micro-slice record, installed-host behavior, hosted/provider
roundtrip, consumer-repository adoption, remote CI, push, release, or tag is
claimed. Parent dirty state and the frozen goal/handoff surfaces were preserved.
