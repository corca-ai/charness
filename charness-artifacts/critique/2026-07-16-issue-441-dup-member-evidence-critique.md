# Critique Review
Date: 2026-07-16

## Decision Under Review

Issue #441 resolution: attach per-fingerprint member evidence (file, span,
in-current-diff status) to the dup-ratchet hard-block JSON payload
(`new_code_family_members`) and human messages, via a 4-tuple span channel
through `dup_ratchet_scan.py` and a `changed_worktree_paths` git seam.

## Failure Angles

- Evidence enrichment silently changing a verdict, exit code, or degrade/block
  classification on any CLI path (degraded, doc-only block, inert,
  write-baseline, scoped-rebaseline).
- `in_current_diff` misattribution (staged-only edits, renames, deleted files,
  non-repo-relative nose paths) recreating the false-attribution the issue
  names.
- The 4-tuple return-shape change breaking an unseen caller or test seam.
- Tests pinning only the happy shape instead of the reporter's job (collateral
  rotation among untouched files recognizable from output alone).
- Charness-specific leakage into a gate consumed by other repos.

## Counterweight Pass

- Real pre-ship items: the regenerated `plugins/` mirror still carried the old
  3-tuple scan signature — a mandatory mutate→sync phase step, fixed in this
  closeout by running the mirror sync before validators; not a logic defect.
- Over-worry: the verdict-flip concern is unfounded — the attach step only
  reads `new_code_families`/`hard_block`, writes one payload key plus
  messages, and no-ops on every non-code-hard-block path; all three in-repo
  callers were updated and `migrate_dup_fingerprints.py` uses the unchanged
  `scan_families`.
- Genuine but deferred: a cosmetic path-base mismatch when `repo_root` is a
  git subdirectory (root-relative vs cwd-relative names) can mislabel a
  member "untouched"; evidence-only, non-blocking, non-standard configuration.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: plugins/charness/skills/quality/scripts/dup_ratchet_scan.py | action: fix | note: plugin mirror carried the pre-change 3-tuple scan; run sync_root_plugin_manifests before validators/commit (done in this closeout)
- F2 | bin: valid-but-defer | evidence: weak | ref: skills/public/quality/scripts/dup_ratchet_git.py:67 | action: defer | note: git-subdir repo_root path-base mismatch can cosmetically mislabel a member untouched; evidence-only and non-standard config
- F3 | bin: over-worry | evidence: strong | ref: skills/public/quality/scripts/check_dup_ratchet.py:302 | action: document | note: attach step proven evidence-only across degraded/doc-only/inert/maintenance paths; exit code unaffected

## Reviewer Tier Evidence

- Requested tier: high-leverage (issue-closeout review class).
- Requested spawn fields: repo standing request `gpt-5.6-terra` + `medium`
  effort is not exposed by this host's Agent tool (model enum is
  sonnet/opus/haiku/fable); spawned typed `bounded-reviewer` with no model
  override.
- Host exposure state: host-defaulted
- Application state: reviewer reported the read-only envelope bound
  (Read/Grep/Glob only; no Bash/Edit/Write/Agent), and the parent-side
  boundary fingerprint verify returned drift: [] after the review.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: `dup_ratchet_scan.py` (member spans from the nose scan) and
  `dup_ratchet_git.py` (worktree diff set).
- Consumer: the agent or human dispositioning a hard block from
  `check_dup_ratchet.py` output.
- Owning surface: quality skill dup-ratchet gate scripts.
- Verdict: owned-correctly
