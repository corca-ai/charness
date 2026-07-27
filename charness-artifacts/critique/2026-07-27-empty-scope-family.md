# Empty-scope refusal family (A4/A7/C5/E2) and the RCA cause-4 scoping
Date: 2026-07-27

## Decision Under Review

Four of the thirty defects in the
[bug hunt record](../audit/2026-07-27-evidence-surface-bug-hunt.md) share one
predicate, so they were fixed as a family under one decision: **a gate that
compared nothing must say so and must not exit 0**, with a deliberate asymmetry
— a *discovered* empty set stays a cheap pass, because collapsing that would make
every commit pay for every artifact family.

Landed: `validate_packaging` (zero manifests now refuses, and it is the whole
engine of the staged mirror-drift gate), `check_export_safe_imports` and
`check_bootstrap_shim_consistency` (zero-file scans refuse; the latter gains a
typed `empty-scope` status), `artifact_validator` (a named path this validator
owns that resolves to nothing refuses), and `check_mutation_run_proof` (the score
claim refuses without an identified run; a new `conclusion_established` field
separates "known green" from "nobody established it").

Also: the RCA for the foreign-copy incident now scopes its "causes 1-4 refuted"
line, because cause 4 is refuted as *that incident's mechanism* while remaining a
live escape (audit id A1).

The additions pushed `artifact_validator.py` past its length cap, so it split
along the seam the change exposed: `artifact_run_scope.py` owns WHICH artifacts a
run covers, the original owns what a valid artifact looks like.

Out of scope: D7 and E5, which have legitimate empty cases and need design; E2's
manifest-conclusion half; and the debug validator's named-path ownership, which
has no static prefix at its call site.

## Failure Angles

- **Did the fix break a legitimate caller?** A gate that newly fails in a normal
  flow is worse than the defect it closes.
- **Is the discovered-vs-named asymmetry correct and complete?**
- **Is the run-proof asymmetry (score refuses, changed-line does not) coherent?**
- **Does the RCA edit overclaim, or disturb the verified root cause?**

## Counterweight Pass

The review's first finding was not a quibble — it was a regression I had shipped
into the working tree, and the counterweight cuts against my own fix rather than
against the reviewer. `--paths` reads like an author asserting a scope, and it
is not: the surface preflight and the closeout sweep are its main callers, and
they pass a slice of the changed set. Two rounds of narrowing followed, each
caught by a case I had not considered. What I rejected: widening the refusal to
cover "an existing file this validator does not own" (the `docs/handoff.md`
shape). That is an ownership question, not an empty-scope question, and folding
it in is how the first regression happened.

The honest read of this slice is that the cross-cutting framing in the original
record — "one shared helper closes six" — was wrong twice: the gates do not share
an output shape, and two of the six have legitimate empty cases. What they share
is a decision, and the durable form of a decision here is a test file, not a
helper.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/artifact_validator.py:386-410 | action: fix | note: the first version failed any commit that staged a generated packet or deleted an artifact — the validator's own content filter drops packets, and a deleted path is not a typo; narrowed to "absent from disk AND not a deletion git knows about", reproduced before and after
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/artifact_validator.py:405-407 | action: fix | note: second regression from the same fix — a tool passing a changed path from another family (`--paths scripts/unrelated.py`) was refused, which is the common case and was already pinned by tests/test_degradation_branch_coverage.py:228; ownership (`owned_prefix`) is now part of the discriminator
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/artifact_validator.py:449-451 | action: fix | note: the `artifacts is None` early return bypassed the named-path check entirely, so the debug family kept the hole while the record claimed the family was closed; the check now runs before that return
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/check_mutation_run_proof.py:86-88 | action: fix | note: `conclusion_established` was set after the non-success early return, so a known-RED run carried no field at all and a consumer defaulting to False would read it as "unknown" — the exact collapse the field exists to prevent; hoisted above the refusal
- F5 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md:276 | action: fix | note: the E2 row cited lines that were neither the fix nor the new field; re-derived against the current file
- F6 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md:82 | action: fix | note: the cause-4 note named the weaker of two reasons the branch was unreachable, faintly implying the guard ran and took the other branch; now says the guard was absent AND the copy sat outside the target root
- F7 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_empty_scope_refusals.py:47-60 | action: fix | note: every refusal test asserted only `returncode != 0`, so an implementation that exits 1 unconditionally passed the whole file; positive controls against the real repo added
- F8 | bin: valid-but-defer | evidence: strong | ref: scripts/validate_debug_artifact.py:428 | action: defer | note: the debug validator resolves its output dir from an adapter at runtime, so no static `owned_prefix` exists at the call site; `owned_prefix=None` preserves the old behavior rather than guessing, and the audit records the family as still OPEN for debug
- F9 | bin: valid-but-defer | evidence: strong | ref: scripts/check_mutation_run_proof.py:86 | action: defer | note: `conclusion_established` is read by nothing in the repo except its own tests, so the exit code remains the whole signal for a manifest-judged run — a field no gate reads is the same class as the defect being fixed, and whether it should become a refusal is a contract question
- F10 | bin: valid-but-defer | evidence: moderate | ref: scripts/artifact_validator.py:441 | action: defer | note: `--paths` with zero values is `not None`, so it takes the named branch; the repo has a written convention that an empty `--paths` means an explicit empty changeset, and this slice takes no position on it
- F11 | bin: over-worry | evidence: strong | ref: scripts/validate_packaging.py:425 | action: document | note: every real caller runs against a charness root that carries `packaging/charness.json`, and the two library callers use `validate_packaging_manifest()` directly, so the new exit path is unreachable for them
- F14 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_empty_scope_refusals.py:24-46 | action: fix | note: also found at the commit gate — the new tests drove each gate through a subprocess, adding three entries to the boundary-bypass ratchet this repo is tightening because 43% of test files are subprocess-bound; converted to in-process `run_loaded_script_main`. Note the detector keys on the NAME `run_script`, so an in-process wrapper carrying that name still counts: the local helper is named `run_gate`
- F12 | bin: over-worry | evidence: strong | ref: scripts/staged_commit_gate_plan.py:214 | action: document | note: the shim gate at the commit boundary is dropped by `timing_pull_gate` when the target repo does not own the script, so a seeded tmp repo never reaches the new `empty-scope` exit
- F13 | bin: act-before-ship | evidence: strong | ref: scripts/artifact_validator.py:17-24 | action: fix | note: found after review, at the commit gate — the additions pushed the file past its 480-line cap, and the split's first form used a bare `from artifact_run_scope import ...`, which binds only when `scripts/` is on sys.path; the exported plugin layout then failed to import the validator and a consumer's scaffold silently lost its `size_budget`, caught by tests/test_quality_scaffold.py:204. Now resolved through `import_repo_module` like every other sibling import in this repo

## Reviewer Tier Evidence

- Requested tier: `high-leverage` (adapter `reviewer_tiers.high-leverage`), realized as the host's typed `bounded-reviewer` agent with session-model inheritance.
- Requested spawn fields: `subagent_type: bounded-reviewer`, no host addressing/team `name`, one scope per spawn. The adapter's Codex-host fields do not apply on this Claude Code host per the CLAUDE.md per-host split; their omission is contract-conformant.
- Host exposure state: host-defaulted
- Application state: host exposed a typed read-only agent; the reviewer self-reported Read/Grep/Glob only with no Bash/Edit/Write/Agent.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. One bounded reviewer ran in a separate agent context over the
whole family and returned findings directly to the parent. Its three requested
verification commands were run by the parent, since the reviewer had no shell,
and all three confirmed the reported behavior before any fix was applied.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-27-empty-scope-family-packet.json
- Packet SHA256: e202e94806f9d0ff118fd7bbc139e8c3cd6c0c1746416b1c6d7f83d0e04be06b
- Identity SHA256: aa03827375b8dd007f4e4496131f96205c07d96599802cfd4e8623e1a553a29d

**Rebind non-claim.** The reviewer consumed the pre-fix state (packet identity
`eb54c440cc9480a71673225c9d996eeb7f42c1146ba08260f4e79706cc910b6a`). F1 through
F7 are fixes derived from its findings and were not re-reviewed by it. F1 and F2
in particular changed the same predicate twice after review, so the shipped
discriminator has been proven by execution and regression tests, not by a second
fresh-eye pass.

**Boundary fingerprint non-claim.** Snapshot taken under window
`empty-scope-family` before the spawn; verify was run after applying fixes, so it
is parent-attributed, not clean — recorded with declarations rather than quoted
as a clean run.

## Boundary Ownership

- Producer: the four gates, each of which now decides what an empty scope means for its own inputs.
- Consumer: the pre-commit plan and `run-quality.sh`, which read exit codes only.
- Owning surface: the shared `artifact_validator` runner owns the named-vs-discovered asymmetry for the artifact family; each scanner owns its own empty-scope answer, because what "empty" means differs per input.
- Verdict: owned-correctly

## Deliberately Not Doing

- No shared "scope status" helper: these gates do not share an output shape, and a helper cannot force adoption. The rule's durable form is the test file.
- No refusal for D7 or E5: both have legitimate empty cases (a documented clean-tree invocation; a per-file floor exemption entangled with the zero denominator), so a blanket fail would break a documented flow or move live verdicts.
- No ownership check for an existing file outside the validator's directory: that is a different question from empty scope, and folding it in caused this slice's first regression.
