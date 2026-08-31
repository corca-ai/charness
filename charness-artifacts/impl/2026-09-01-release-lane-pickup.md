# Next session: finish the v8.0.2 release lane

Status: pickup prompt. Written 2026-09-01. Base `f084bf7e1`, 96 commits ahead of
`origin/main` (`f8b9cd8af`, v8.0.1). Nothing pushed, no tag, version still 8.0.1,
worktree clean.

## The finding that matters most

**The release lane had been red for a long time and nobody ran it.** Prior
sessions reported "standing suite 8423 green"; the standing lane runs
`-m 'not release_only'` and skips the release queue entirely, so seven separate
gate failures were invisible to it. This is the ledger's own
`skipped-is-not-passed` lesson, realised at repo scale.

Six of the seven are now fixed and committed. One remains.

## What is left: `release-changed-line-coverage`

Current release queue result: **82 passed, 1 failed**.

```
37 changed files carry 154 uncovered changed lines
  this session   :  9 files,  26 lines  (17%)
  prior sessions : 28 files, 128 lines  (83%)
```

The gate's base is `origin/main`, so it measures all 96 commits, not just recent
work. Reproduce with:

```bash
./scripts/run-quality.sh --release --read-only
# log: <runtime>/quality-failure-logs/release-changed-line-coverage.log
# the payload is YAML nested inside `consumer_stdout`; parse it, do not eyeball it
```

Two things about this gate before acting on it:

- It also WARNS that one changed pool file mapped to no standing test and was not
  analysed at all (`skills/public/release/scripts/generate_release_notes.py`). A
  clean verdict says nothing about it.
- An advisory names `scripts/prepush_quality_receipt.py` as possibly LOSING its
  measurement (a test copies the script by name). That is file-granularity only;
  read the copy's destination before concluding those lines are untested.

### Uncovered lines, attributed

| file | origin | lines | line numbers |
|---|---|---|---|
| `scripts/reviewed_input_identity.py` | this session | 7 | 91, 92, 93, 108, 109, 447, 508 |
| `scripts/reviewed_input_nonblob.py` | this session | 4 | 47, 345, 432, 433 |
| `scripts/task_run_state.py` | this session | 4 | 41, 64, 88, 104 |
| `scripts/reviewed_input_worktree.py` | this session | 3 | 45, 49, 112 |
| `scripts/check_staged_worktree_consistency.py` | this session | 2 | 117, 118 |
| `scripts/helper_provenance_lib.py` | this session | 2 | 44, 45 |
| `scripts/task_run.py` | this session | 2 | 91, 92 |
| `scripts/check_current_pointer_writes.py` | this session | 1 | 18 |
| `scripts/sibling_module_loader.py` | this session | 1 | 51 |
| `scripts/git_checkout.py` | prior | 28 | 32, 33, 39, 59, 60, 62, 76, 77, 91, 98, 118, 119, 125, 126, 134, 137, 138, 140, 146, 157, 158, 164, 165, 168, 175, 178, 179, 183 |
| `scripts/premise_git_snapshot.py` | prior | 15 | 99, 131, 134, 142, 143, 144, 145, 146, 147, 148, 149, 153, 189, 199, 200 |
| `skills/public/quality/scripts/test_discovery_lib.py` | prior | 10 | 26, 84, 85, 86, 87, 88, 89, 90, 91, 92 |
| `scripts/prepush_quality_receipt.py` | prior | 7 | 34, 35, 36, 37, 38, 110, 191 |
| `scripts/classify_t_signal.py` | prior | 6 | 63, 66, 122, 326, 327, 328 |
| `skills/public/release/scripts/publish_release_runtime.py` | prior | 6 | 112, 119, 120, 121, 122, 137 |
| `skills/public/release/scripts/scaffold_claims_review.py` | prior | 6 | 174, 177, 178, 179, 180, 181 |
| `scripts/worktree_doctor_checks.py` | prior | 5 | 73, 74, 91, 97, 98 |
| `scripts/git_status_snapshot.py` | prior | 4 | 124, 125, 225, 226 |
| `scripts/lesson_ledger_lib.py` | prior | 4 | 198, 204, 205, 206 |
| `scripts/task_run_git.py` | prior | 4 | 49, 69, 149, 193 |
| `skills/public/quality/scripts/structural_waste_lib.py` | prior | 4 | 49, 50, 55, 56 |
| `scripts/checkout_view.py` | prior | 3 | 117, 123, 124 |
| `scripts/surfaces_lib.py` | prior | 3 | 311, 312, 406 |
| `skills/public/quality/scripts/dup_ratchet_git.py` | prior | 3 | 30, 117, 118 |
| `scripts/dup_ratchet_edit_advisory.py` | prior | 2 | 40, 41 |
| `scripts/mutation_changed_files_lib.py` | prior | 2 | 324, 325 |
| `scripts/premise_tree_observation.py` | prior | 2 | 45, 46 |
| `scripts/setup_inspect_quality_lib.py` | prior | 2 | 105, 106 |
| `scripts/worktree_cleanup_lib.py` | prior | 2 | 44, 45 |
| `skills/public/issue/scripts/issue_critique_observer_support.py` | prior | 2 | 42, 43 |
| `skills/public/release/scripts/release_delta.py` | prior | 2 | 46, 71 |
| `scripts/changed_line_run_trust.py` | prior | 1 | 221 |
| `scripts/check_prose_pin.py` | prior | 1 | 111 |
| `scripts/check_symbol_residue.py` | prior | 1 | 17 |
| `scripts/premise_preflight_lib.py` | prior | 1 | 257 |
| `skills/public/quality/scripts/inventory_entrypoint_docs_ergonomics.py` | prior | 1 | 21 |
| `skills/support/markdown-preview/scripts/markdown_preview_lib.py` | prior | 1 | 181 |

The nine "this session" files are mostly a refactor artefact: splitting four
files over their length cap moved existing lines, and moved lines register as
changed. Four of them are genuinely hard to cover in process, and deliberately
so — `helper_provenance_lib.py:44-45` and `reviewed_input_identity.py:108-109`
are `except ModuleNotFoundError` fallbacks that fire only when `scripts` is NOT
importable, which is the case they exist to serve. Cover them the way
`test_index_hygiene_gates_import_through_their_scheduled_argv` covers its
subject: cross a real process boundary with a `boundary_contract` marker naming
why.

## The six already fixed, and why each was invisible

| gate | root cause |
|---|---|
| `pytest-release` | count pin (12/8) went stale when the seed catalog moved the work to a cached copy; the pin only ever saw one module's `subprocess` |
| `ruff` | three unused imports plus one `C901`; split cohesively rather than `noqa`'d |
| `inventory-gitignore-scan-hygiene` | the marker list omitted `RepoFileSnapshot`, the repo's OWN listing owner, so three correct call sites read as ungoverned |
| `check-boundary-bypass-ratchet` | **9 of 18 exemptions had silently expired** — they are keyed by call-site CONTENT, so editing a covered file voids its adjudication |
| `check-python-lengths` | four files crossed the cap inside this range; the gate passes at `origin/main` |
| `validate-debug-seam-index` | derived index never rebuilt after a debug artifact landed |

The ratchet one generalises and is worth a slice of its own: **a
content-fingerprint exemption expires whenever its file is touched**, re-arming a
gate against a decision a maintainer already made, with no signal. The file
header calls the fingerprint "path-invariant", which is true and beside the point.

## Do not repeat these

- Do not run a file-mutating harness against the working tree. One did here, left
  four gate scripts `ast.unparse`d mid-run, and a premature "completed"
  notification made it read as corruption. Use an isolated copy.
- Do not accept "no findings" from an instrument without asking whether it RAN.
  Three separate instruments in this session reported empty because they had
  errored, not because the thing was clean.
- Do not compare failure COUNTS when the claim is about failure SETS. Equal
  counts hid one test dying and another flipping green; the conclusion survived,
  the reasoning did not.
- Do not re-baseline a ratchet before reading its delta. Here the delta was one
  genuinely new file, and it turned out to spawn nothing at all.

## Not done, deliberately

- The two remaining `_load_sibling` copies (`prepush_close_keyword_guard.py`,
  `check_issue_closeout_commit_msg.py`) still restate the loader that now has an
  owner in `scripts/sibling_module_loader.py`. They run inside git hooks; a
  load-order change is not something to ship beside a release.
- Making the dead-code advisory blocking or non-opt-in. It already reports what a
  proposed new gate would have; it just never blocks.
- `check_current_pointer_writes` cannot see a pointer name built from a variable
  stem. The reported defect was one layer off — the SCANNER lacks constant
  propagation; widening the prefilter changes nothing and that attempt was
  reverted rather than shipped as cosmetic.

## Release inputs already prepared

- notes: `charness-artifacts/release/v8.0.2-notes.md` (derived, `--check` clean)
- critique: `charness-artifacts/critique/release-8-0-2-critique.md` (validates)
- bump: patch. No `feat:` commits; `git diff --name-status origin/main..HEAD --
  skills/public packaging .agents` adds no file.

Resume with the repo's OWN helper, not the installed copy — the provenance guard
refuses the latter and names the right command:

```bash
python3 skills/public/release/scripts/publish_release.py --repo-root . --part patch --execute \
  --notes-file charness-artifacts/release/v8.0.2-notes.md \
  --critique-artifact charness-artifacts/critique/release-8-0-2-critique.md \
  --bump-rationale "<why patch>"
```

## Moved aside, not deleted

22 untracked files from earlier sessions blocked the publish helper's clean-tree
requirement. They are preserved at
`~/.cache/charness-preexisting-untracked-20260831/`. One of them was NOT junk and
is now committed: `charness-artifacts/retro/2026-08-31-123034-packet.md`, which a
committed retro cites and the lesson-selection index counts.
