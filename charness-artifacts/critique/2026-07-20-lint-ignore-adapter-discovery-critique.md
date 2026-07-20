# Critique Review
Date: 2026-07-20

## Decision Under Review

Making lint-ignore discovery adapter-owned — the sibling the hardcoded-discovery
gate surfaced. The lint-ignore inventory scanned only py/js/ts suppression syntax
(`# noqa`, `# ruff: noqa`, `# pylint: disable`, `eslint-disable`), so a repo
linting Go (`//nolint`) or Ruby (`# rubocop:disable`) was silently undercounted —
the same measurement-contract class as the `.mjs` test-discovery bug. New adapter
field `lint_ignore_discovery.directives` lets a consumer declare `{tool,
suffixes, pattern (regex, ideally with a (?P<codes>...) group), scope}`; each
directive's suffixes join the discovery set and its regex is applied line by
line. Inert when omitted (only the built-in matchers run).

One bounded high-leverage fresh-eye reviewer ran (correctness + robustness/safety
+ honesty/fit, with an in-lens counterweight); rail-1 reviewer-boundary
fingerprint verified clean around the pass.

## Failure Angles

- Correctness: does an adapter directive on a new suffix actually get scanned
  given the built-in short-circuit, and is scope/codes parsing right?
- Robustness/safety: regex trust posture, runtime compile drift, degrade-not-crash.
- Honesty & fit: marker/INTERPRETATION accuracy, validator shape-gate completeness.

## Counterweight Pass (four-bin triage)

- K1 | act/bundle (fixed): the validator checked unknown keys per directive but
  had **no top-level unknown-key loop** (unlike its sibling `test_file_discovery`).
  A mistyped `directves:` would yield zero matchers with no error and a valid
  adapter — the exact silent undercount this feature removes, reintroduced at the
  outermost key. Added the top-level warning loop (a new `LINT_IGNORE_DISCOVERY_
  KNOWN_KEYS`), refactored the per-directive checks into `_validate_lint_directive`
  to stay under the complexity cap, and added a regression test asserting the
  typo warns while the adapter stays valid.
- K2 | over-worry (confirmed, no change): the reviewer verified the adapter scan
  runs BEFORE the built-in `has_*_marker` short-circuit, so a `.go` file records
  its findings then falls through harmlessly; codes parse correctly for
  no-group / unmatched-group / empty-match (all blanket); `_directive_scope`
  leading-logic is correct; a runtime `re.error` skips the directive rather than
  crashing; an invalid adapter degrades (permissive load, built-in scan still
  runs). Double-counting needs a consumer to declare a py/js/ts directive
  overlapping built-in syntax — a different `tool` label on trusted repo-owned
  config, not a defect.
- K3 | bundle (fixed): a muddled doc line ("regex runs against repo-owned config
  as trusted input") now states the pattern is the trusted config and is applied
  to file content, and names the top-level unknown-key warning.
- K4 | valid-but-defer: ReDoS from an adapter pattern is bounded by the
  repo-owned-config trust boundary (stated, consistent with `test_file_discovery`'s
  shell command) and per-line `finditer`; no action.

## Recurrence Verdict

The lint-ignore surface now consumes the repo's declared linter syntax instead of
guessing it, closing the same divergence class as the `.mjs` fix for a second
inventory. Its own limit — a consumer must declare the directive syntax, not just
an extension — is honest (suppression syntax genuinely is language-specific) and
documented in the marker and adapter contract.

## Boundary Ownership

- Verdict: owned-correctly

The fix touches the shared quality adapter contract. The portable body owns the
built-in py/js/ts matchers and the discovery mechanism; the consuming repo owns
its non-default linter directive syntax via the adapter. No producer/consumer
inversion — the same layering as `test_file_discovery`.

## Reviewer Tier Evidence

<!-- allowed Host exposure state enums only -->
- Requested tier: high-leverage
- Requested spawn fields: none — Claude Code host, typed `bounded-reviewer` (Read/Grep/Glob) with session-model inheritance per the repo per-host subagent contract; no Codex model requested on this host, so the omission is contract-conformant, not a degradation.
- Host exposure state: host-defaulted
- Application state: the host spawned the typed `bounded-reviewer` agent by name; the read-only envelope bound and the rail-1 reviewer-boundary fingerprint verified clean (no index/worktree drift) after the reviewer returned, so approvals are valid and the reviewer ran on the parent's session-inherited model.

## Fresh-Eye Satisfaction

parent-delegated — one high-leverage resolution reviewer with an in-lens
counterweight; rail-1 reviewer-boundary fingerprint verified clean.
