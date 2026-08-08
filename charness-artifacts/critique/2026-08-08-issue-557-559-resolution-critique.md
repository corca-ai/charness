# Issue #557 and #559 Resolution Critique
Date: 2026-08-08

## Decision Under Review

Resolving `#557` by consolidating the capture lane's adapter-template branch onto
`issue_backend.resolve_op` (leaving its non-template GraphQL default local), and
resolving `#559` by NOT consolidating the release copy — repairing its measured
drift instead and shipping an executable reason for the split.

Two delegated bounded rounds ran before the close call. Both are recorded here.

## Failure Angles

- **Bundling two issues that share a face and not a remedy.** This goal's own
  Plan Critique named the risk, and the predecessor measured it twice.
- **Taking each issue's stated blocker on trust.** Both are durable records
  naming a remedy, which is exactly where this repo's Change Discipline fires.
- **A consolidation that changes what command actually runs**, on a release
  surface.
- **Inheriting an owner's code without its protections.**
- **A copy of a rule reappearing as a copy of a rule inside a test.**

## Counterweight Pass

The premise check paid three times, and the third payment was the largest.

It refuted the BUNDLING (`#557` is a shape problem in one branch under the
owner's own adapter key; `#559` is an ownership problem across two skills), and
it refuted BOTH issues' stated blockers. `#557` had concluded from one branch
that the whole function was unconsolidatable. `#559` had framed its blocker as a
contract decision about unifying adapter keys, which is not a thing that needed
deciding: `resolve_op` reads only `binary`, `id` and `commands`, and the only
coupling to `issue_backend` lived in three error strings.

Then the delegation was attempted, and a smoke test found the blocker that
actually holds and that neither the issue nor the premise check had seen: the two
adapter contracts disagree about where the BINARY lives. Release templates carry
it and `backend_command` never reads `release_backend.binary`; the owner prepends
it. Delegating doubles the binary for every existing release adapter. That is a
consumer-facing contract change on the least reversible surface in this repo, and
it would have shipped on the strength of a premise check that was right about the
adapter keys and silent about the argv shape.

The honest conclusion is not "the premise check failed" — it corrected two wrong
remedies. It is that a premise check verifies the CLAIM it was pointed at, and
the thing that caught this was executing the replacement and reading its output.
Both are needed.

Over-worry, checked and dismissed: whether keeping the fifth copy is a failure of
the slice. It is not — this goal's acceptance is "one owner, OR every remaining
copy carries a measured reason", and the reason is now executable rather than
prose, which is strictly stronger than the deferral it replaces.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/issue_source_capture_lib.py:88 | action: fix | note: round 1 — the new owner loader knew only the source-tree layout; in the exported mirror the owner sits at `skills/issue/...`. `spec_from_file_location` returns a spec WITH a loader for a nonexistent path, so the shape guard could not fire and `exec_module` raised an untyped `FileNotFoundError` into a typed-refusal lane — and it ran BEFORE the GraphQL default returned, so every installed capture would have died, not only templated ones
- F2 | bin: act-before-ship | evidence: strong | ref: tests/test_tracker_backend_single_owner.py:14 | action: fix | note: round 1 — the debt ledger's module docstring still said the capture copy was NOT removed while its set entry was gone. The guard iterates the set, so the rot landed in the half nothing checks
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/issue_source_capture_lib.py:163 | action: fix | note: round 2 — `CaptureRefusal` subclasses `RuntimeError`, so the loader's own new typed code was caught by the caller's broad translation and re-raised as `invalid_capture_command`, routing an operator to the adapter file for a broken INSTALL. The code F1's repair added could never be observed
- F4 | bin: act-before-ship | evidence: strong | ref: tests/test_issue_source_capture_backend_delegation.py:41 | action: fix | note: round 2 — the test written to prove F1's repair RE-IMPLEMENTED the loader's candidate list and asserted on its own copy. It would have passed with the loader deleted, with the wrong package root, or with the refusal misspelled: a second copy of the rule under test, inside the slice about copies of a rule. It calls the loader now
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/issue_source_capture_lib.py:208 | action: fix | note: round 2 — a brace-bearing template still escaped untyped: `PLACEHOLDER_RE` matches only `{lower_snake}`, so a JSON part clears the allowlist and then raises inside `str.format`. A `source_capture` template is GraphQL/JSON-shaped by nature, so that is the EXPECTED case here rather than the exotic one, and the release copy already guarded it
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/issue_source_capture_lib.py:200 | action: fix | note: round 2 — the delegation passed `required=frozenset()`, discarding the issue-identity floor built one slice earlier, in the slice that consolidates onto that very owner. A template naming no repository is refused now, in either spelling (`{repo}`, or `{owner}`+`{name}`), checked in the lane because the owner's flat `required` cannot express a disjunction
- F7 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_helpers.py:160 | action: fix | note: found by the parent's own smoke test during the build, and it reversed the slice's shape — release templates INCLUDE the binary while the owner prepends it, so the attempted delegation doubled it for every existing release adapter. Reverted to a drift repair plus an executable reason
- F8 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_release_backend_agrees_with_the_owner.py:112 | action: fix | note: round 1 advisories taken as fixes — the differential covered only one op, so a divergence reachable through `release_create`/`release_view_body`/`auth_check` was untested; and it pinned the owner's RAW exception type, which would fail on a later improvement for a non-drift reason
- F9 | bin: act-before-ship | evidence: moderate | ref: scripts/issue_source_capture_lib.py:57 | action: fix | note: round 1 advisory taken as a fix — the placeholder allowlist was hand-restated beside the `subs` dict it must match. Two declarations of one set: a missing entry silently refuses a previously-valid template, an extra one re-opens the hole. Derived from a single `capture_subs()` now
- F10 | bin: act-before-ship | evidence: moderate | ref: skills/public/release/references/adapter-contract.md:192 | action: fix | note: round 1 advisory taken as a fix — the reference said `release_backend` mirrors the `issue_backend` shape, which the new test measures to be false in exactly the binary position. Host authors read the doc, not the test. Brace escaping was undocumented too
- F11 | bin: valid-but-defer | evidence: strong | ref: skills/public/release/scripts/publish_release_helpers.py:154 | action: document | note: the fifth copy STAYS, and this is the disposition rather than a deferral of the analysis. The blocker is measured, executable, and recorded in three places that agree: `_KNOWN_UNCONSOLIDATED`, the `dup-review.json` classification, and the differential test that fails if the pair drifts again
- F12 | bin: over-worry | evidence: strong | ref: tests/test_issue_source_capture.py | action: document | note: feared that splitting the test file on the length cap would scatter the subject; the split is cohesive — everything moved answers one question (does the lane delegate?) while the parent file is about capture completeness

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded reviewer (`bounded-reviewer` typed agent), two spawns — a review of the implementation, then a second round reading that review's repairs.
- Requested spawn fields: subagent_type `bounded-reviewer`, no host addressing name, read-only toolset (Read/Grep/Glob).
- Host exposure state: host-defaulted
- Application state: host-confirmed: both spawns returned findings inline and each reported the read-only envelope bound, with no Bash, Edit, Write, or Agent tool visible.
- Delivery state: findings-received

Per-host note: Claude Code host, so the repo's Codex-only `gpt-5.6-terra`/`medium`
request does not apply; typed `bounded-reviewer` agents were used instead.

## Fresh-Eye Satisfaction

`parent-delegated`. Two bounded reviewers in distinct contexts, each
boundary-fingerprinted with `reviewer_boundary_fingerprint.py` snapshot/verify —
windows `w-20260808T063211Z-3901148` and `w-20260808T063920Z-3915653`, both
verifying `clean` with empty drift, and both verified the moment the reviewer
returned, before any repair.

Six blockers, all in repairs. Round 2's set is the sharper one and its theme is
worth stating: three of its four findings were about a repair inheriting only
half of something — half a layout, half an exception contract, half an owner's
protections. Twelve mutants were killed across the build and both repair sets,
and one SURVIVED first: a pin asserting on the generated mirror passed over a
broken source, because the mirror lags until the next sync.

The cap is two rounds, so round 2's repairs (F3-F6 and the pins over them) are
recorded as accepted-unreviewed.

## Reviewed Input Identity

<!-- No packet consumed: this critique binds to both issue bodies, the working tree at review time, the two reviewer reports cited inline, and the constructed probes executed before and after each repair. -->

## Boundary Ownership

- Producer: `skills/public/issue/scripts/issue_backend.py` — `resolve_op` for rendering, `backend_binary` for the binary rule.
- Consumer: `scripts/issue_source_capture_lib.py::build_page_argv` (now delegating) and `skills/public/release/scripts/publish_release_helpers.py::backend_command` (deliberately not, with an executable reason).
- Owning surface: the `issue` skill for tracker access; the `release` skill for release publication. The two adapter keys stay separate, and the binary-position difference is what makes that a contract fact rather than a preference.
- Verdict: owned-correctly
