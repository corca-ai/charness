# Duplicate Ratchet Closeout Critique
Date: 2026-07-09
Fresh-eye satisfaction: parent-delegated

## Decision Under Review

Resolve the remaining prompt-mutation goal duplicate-ratchet hard block by
extracting the prompt-mutant skill file discovery helpers into
`scripts/prompt_mutant_files_lib.py` and classifying the seven remaining
low-value clone families as intentional in
`charness-artifacts/quality/dup-review.json`.

## Failure Angles

- Classification laundering: marking genuinely extractable duplication as
  intentional would silence the hard arm without improving the code.
- Coupling risk: extracting tiny CLI/path/hash/status idioms across unrelated
  scripts could create a shared abstraction with more maintenance cost than the
  duplicate spans.
- Mirror drift: changing a root script requires the plugin mirror to stay synced
  before validation.

## Counterweight Pass

- One same-file duplicated loop had a clear shared concept and was extracted
  into `_pair_public_skill_files`; the surrounding skill path/discovery helpers
  now live in `scripts/prompt_mutant_files_lib.py` so
  `scripts/prompt_mutant_lib.py` keeps mutation logic under the line-length
  guard.
- The remaining seven families are tiny standalone CLI, path, hash, status-label,
  or string-assignment shapes whose notes name why shared helpers would couple
  unrelated modules or collapse distinct concepts.
- `check_dup_ratchet.py --repo-root . --json` now reports `status: clean`,
  `ok: true`, `new_code_families: []`, and `fixable_ceiling=0`.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/prompt_mutant_files_lib.py` | action: fix | note: Extracted the repeated plugin/public sibling pairing loop and related file-discovery helpers instead of classifying them away.
- F2 | bin: bundle-anyway | evidence: strong | ref: `charness-artifacts/quality/dup-review.json` | action: document | note: Seven remaining low-value duplicate families are classified as intentional with per-family coupling rationale.
- F3 | bin: act-before-ship | evidence: strong | ref: `plugins/charness/scripts/prompt_mutant_files_lib.py` | action: fix | note: Plugin mirror was regenerated with `sync_root_plugin_manifests.py`.
- F4 | bin: bundle-anyway | evidence: moderate | ref: `scripts/witness_coverage.py` | action: fix | note: Follow-up reviewer found stale docstrings naming `prompt_mutant_lib` as the discovery owner; comments were updated to name `prompt_mutant_files_lib` for file discovery and `prompt_mutant_lib` for unit splitting.

## Reviewer Tier Evidence

- Requested tier: bounded duplicate-ratchet closeout.
- Requested spawn fields: model=gpt-5.4-mini, reasoning_effort=medium; service_tier inherited.
- Host exposure state: requested_fields_sent
- Application state: host returned reviewer agent id and completion payload with `PASS`.

## Fresh-Eye Satisfaction

parent-delegated — one bounded read-only reviewer completed through
`multi_agent_v1.spawn_agent` and returned `PASS`; a follow-up fresh-eye review
after the final module split also returned `PASS` and its only non-blocking
stale-docstring finding was fixed.

## Boundary Ownership

- Producer: duplicate-ratchet scanner and `dup-review.json` overlay produce the hard-arm classification.
- Consumer: final quality/closeout gates consume the clean ratchet verdict.
- Owning surface: quality duplicate-ratchet artifacts plus prompt-mutant helper code.
- Verdict: owned-correctly
