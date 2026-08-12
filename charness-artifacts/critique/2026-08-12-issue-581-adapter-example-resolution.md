# #581 Issue Adapter Example Resolution Critique

Date: 2026-08-12

## Execution

Three bounded, read-only fresh-eye angle reviews and one independent
counterweight reviewed the #581 repair. A final bound-packet review initially
compared raw file hashes to the typed `sha256-v2` identity, then corrected that
false alarm after the canonical identity verifier returned `current`. All
findings reached the parent; each reviewer boundary fingerprint verified clean
before the next review.

## Fresh-Eye Satisfaction

parent-delegated — causal review, implementation review, three critique angles,
and the counterweight all returned their findings directly.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none; the host used the inherited session defaults.
- Host exposure state: host-defaulted
- Application state: no provider tier-application metadata was returned.
- Delivery state: findings-received

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-104057-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-104057-packet.json
- Packet SHA256: d88a4f1455c3e3518f33e2e0916618c3211721ff0901cc43ea43bd45db5710be
- Identity SHA256: 0ac3433c0994d0ca542f38a2d5319d14b032de31f5cf041064bd935f18913da2

## Boundary Ownership

- Producer: the public issue adapter example declares host command templates.
- Consumer: a repository operator copying that example into an issue adapter.
- Owning surface: `skills/public/issue` example plus its generated plugin projection.
- Verdict: owned-correctly

## Decision Under Review

Remove create's unsupported `{reason}` argument from the shipped example and
prove every declared example command resolves through its operation-owned
placeholder allowlist, without claiming host-provider execution.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/public/issue/adapter.example.yaml:18-68 | action: document | note: retain source-to-plugin synchronization and packaging validation because the source YAML is the tested authority and the plugin is derived.
- F2 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/test_issue_skill.py:51-94 | action: document | note: a new central operation registry would blur call-site-specific required-placeholder semantics; the exact example op-set plus production resolver and module-owned allowlists prevent the reported copy-paste class.
- F3 | bin: valid-but-defer | evidence: moderate | ref: skills/public/issue/scripts/issue_read.py:30-38 | action: defer | note: automatically deriving the union of every future view-call requirement needs a separate contract design if operation metadata becomes centralized.
- F4 | bin: over-worry | evidence: strong | ref: scripts/reviewed_input_identity.py:_worktree_content_sha256 | action: document | note: raw file SHA-256 is not comparable to the packet's typed sha256-v2 content digest; the canonical verifier confirmed the final packet is current.

## Deliberately Not Doing

- Do not validate the hypothetical host `acme` CLI flag grammar or claim a provider roundtrip.
- Do not introduce a generic operation metadata registry solely for this bounded example repair.
- Do not close #581, publish, push, or claim consumer-repository execution.

## Next Move

Run the focused regression, packaging validation, artifact validators, and the
local lint gate; commit the locally proven slice, then continue to #594.
