# issue-429-430-431-resolution-critique
Date: 2026-07-10

## Decision Under Review

Resolution diff for corca-ai/charness #429 (shared exported scripts into the
ruff/py-compile/length/export-import/runtime-inheritance gate scopes plus a
scope regression test), #430 (bounded-reviewer envelope: frontmatter pin test,
recorded live non-binding probe, non-claim rewording of rail-2 prose), and
#431 (one rail-1 snapshot/verify line at the reviewer-spawn step of the
quality/release/issue/critique SKILL.md files, mirror-synced).

## Failure Angles

- enforcement-integrity / recurrence: gate-scope escapes for the NEXT exported
  script directory, prose-only enforcement decaying like the pre-#428 prose,
  and the mutation pool still excluding `skills/shared/scripts`.
- portability / consuming-repo adoption / boundary ownership: whether the four
  SKILL.md lines and the Enforcement invocation actually work from a portable
  plugin install, and whether each edit landed in the owning surface.
- verification-channel fitness / over-claim honesty: whether the probe JSON,
  the two new regression tests, and the reworded prose claim only what the
  recorded evidence supports (fresh-conversation vs process-restart confound).

## Counterweight Pass

- Real-but-bundled: the rail-2 topic sentence still asserted unconditional
  host denial (falsified on this host today) — fixed with a "where the
  envelope binds" qualifier; the scope test never exercised the git-file-
  listing mode the gate actually runs — fixed with a `require_git=True`
  assertion. Both applied before commit.
- Real-but-deferred: the Enforcement command's `<repo-root>` path idiom does
  not resolve from a portable install (pre-existing, amplified by the new
  SKILL.md pointers; the right portable mechanism needs a design pass, not a
  blind `$SKILL_DIR` swap); glob-set parity across the four gate files; a
  shared-skill mutation pool bucket; deterministic teeth for the four new
  SKILL.md lines; required tool-use-audit artifact for the no-git-trace
  nested-spawn hole.
- Over-worry: brittleness of the run-quality ruff-line test against a future
  multi-line refactor (self-described note-only, speculative).

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/shared/references/fresh-eye-subagent-review.md:163 | action: fix | note: rail-2 topic sentence asserted unconditional host denial; qualified with "where the envelope binds" (applied in this commit)
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_shared_script_gate_scope.py | action: fix | note: scope test only ran require_git=False while the gate uses git file listing; require_git=True assertion added (applied in this commit)
- F3 | bin: valid-but-defer | evidence: strong | ref: skills/shared/references/fresh-eye-subagent-review.md:153 | action: file-issue | follow-up: deferred to the #431 close-comment deferred ledger pending operator triage | note: Enforcement `<repo-root>/skills/shared/scripts/...` invocation is unresolvable from a portable plugin install; the new SKILL.md pointers amplify reliance on it; needs a portable path mechanism decision
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/sample_mutation_files.py:49 | action: defer | note: MUTATION_POOLS has no shared-skill bucket, so skills/shared/scripts (incl. the rail-1 engine) stays outside mutation coverage; outside #429's ruff+length JTBD and touches pool classification plus consumers
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_python_lengths.py:149 | action: defer | note: exported-script glob set stays duplicated across four gate files; next new script dir can escape again; parity mechanism is a design task (cross-language)
- F6 | bin: valid-but-defer | evidence: moderate | ref: skills/public/critique/SKILL.md:112 | action: document | note: the four new SKILL.md rail-1 lines are instruction-following prose; Floor-Addition Restraint says advisory suffices until a recorded decay recurrence
- F7 | bin: valid-but-defer | evidence: moderate | ref: skills/shared/references/fresh-eye-subagent-review.md:171 | action: document | note: undelegated no-git-trace nested spawn has no live enforcement while rail 2 is unbound; dispositioned in prose (parents audit reviewer tool-use events); required audit artifact is a separable follow-up
- F8 | bin: over-worry | evidence: weak | ref: tests/quality_gates/test_shared_script_gate_scope.py:37 | action: defer | note: ruff-line pin could break on a future multi-line refactor of run-quality.sh; speculative, fail-closed, note-only

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority (adapter mapping targets a Codex host; not applicable to this host's spawn surface).
- Host exposure state: host-defaulted
- Application state: host spawned reviewers on the session-default model; adapter spawn fields were not sent because the host exposes no per-spawn model/effort fields for these typed spawns. All four reviewers additionally reported `envelope-unbound` (typed read-only envelope did not bind; tool-use audits confirmed read-only behavior).

## Fresh-Eye Satisfaction

parent-delegated — three angle reviewers (enforcement-recurrence, portability/boundary, proof-honesty) plus one separate counterweight reviewer, each spawned as `bounded-reviewer` with the prepare packet charness-artifacts/critique/2026-07-10-053400-packet.md; rail-1 fingerprint snapshot/verify wrapped both review rounds (verify clean: `{"ok": true, "drift": []}` after the angle round and after the counterweight); reviewer tool-use events audited from transcripts (no writes, no git mutation, no nested spawns).

## Boundary Ownership

- Producer: the shared fresh-eye reference (two-rail policy owner) and each gate script's own scan-scope tuple.
- Consumer: parent sessions spawning shared-tree reviewers (charness and consuming repos) and the repo quality gates consuming the scan scopes.
- Owning surface: skills/shared/references/fresh-eye-subagent-review.md for rail policy and non-claim wording; each gate script (run-quality.sh, check_python_lengths.py, check_export_safe_imports.py, check_python_runtime_inheritance.py) for its own scope; .claude/agents/bounded-reviewer.md for the host envelope; the four SKILL.md files for their own spawn-step routing.
- Verdict: owned-correctly
