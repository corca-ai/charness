# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1. The prepared major release IS PUBLISHED and the
  cohort's ten issues are closed, so the release question that governed the last two
  handoffs is settled. Read the tag with `git describe --tags --abbrev=0`.

## Continuation Capability

- [S9 critique](../charness-artifacts/critique/2026-08-16-s9-close-keyword-prepush-guard.md) — both
  rounds, F1-F15, and the two blockers round 2 found inside round 1's repairs.
- [S8 critique](../charness-artifacts/critique/2026-08-16-s8-handoff-five-and-coverage-debt.md) — the
  previous range's findings and which forced a reversion rather than a patch.
- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the
  owner-approved scope and its sequence.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.

## Current State

- **The prepared major release is PUBLISHED**, not a draft or prerelease. Read the tag
  with `git describe --tags --abbrev=0`, then re-prove the published state with
  `gh release view "$(git describe --tags --abbrev=0)" --repo corca-ai/charness`.
- **The ten cohort issues are closed, one close per issue, each body about only itself.**
  #618-#625 and #627 were closed by `close-with-comment`; #626 was already closed by
  accident and received its missing body as a comment under the owner's do-not-reopen
  ruling. The posted bodies are checked in as `charness-artifacts/issue/2026-08-16-issue-*.md`.
- **The close-keyword pre-push guard blocks**, which is why this range's pushes could not
  close anything by accident. Re-prove with the guard
  [prepush_close_keyword_guard.py](../scripts/prepush_close_keyword_guard.py) over the
  commit that closed #626 (find it with `git log --grep='S7 closes' -i origin/main`).
- **A gate's cleanup can no longer restate its verdict.** `set -e` inside an EXIT trap let
  a failed `rm` rewrite a gate's exit code; swept across the shell gates and pinned by the
  regression file [test_quality_runner_exit_status.py](../tests/quality_gates/test_quality_runner_exit_status.py).
- Re-prove the suite with `python3 scripts/run_standing_pytest.py --include-release-only`
  after `python3 scripts/sync_root_plugin_manifests.py`; ruff needs `--no-cache`.

Non-claims: the release's real-host checklist has NOT been run — no `charness update`, no
installed-vs-repo readback, no `nose` tool-doctor pass. Two should-fix findings in the
published notes ship unrepaired and are named in the release-review artifact. No consuming
repo has run this tree.

## Next Session

1. **Run the release's real-host checklist.** It is the one proof the release shipped
   without:
   `charness update` on this machine, then `charness doctor` and a cited-check == repo
   spot check, so the installed plugin is not skewed from the repo. The full list is in
   the published record [latest.md](../charness-artifacts/release/latest.md).
2. **Two should-fix claims ship unrepaired in the published notes**, recorded rather than
   quietly fixed. Both are named in
   the [prepared claims review](../charness-artifacts/release-review/2026-08-16-v6.0.0-prepared-claims-review.md):
   a sentence pointing at "module docstrings" for a caveat that lives in a function
   docstring, and an undisclosed exit-0-judged-nothing path on malformed pre-push stdin.
   Fix both in the tree; the notes are published and are not where to start.
3. **[#634](https://github.com/corca-ai/charness/issues/634) residual.** Only the
   shell-gate half landed. The cwd-relative instruction sites are UNREPAIRED and the
   detector for them was reverted: it pushed a documentation placeholder into four
   EXECUTED command fields and refused correct consumer prose. Any retry must first
   separate fields that are READ from fields that are RUN.
4. **[#546](https://github.com/corca-ai/charness/issues/546) residual.** The count is
   first-class now; separating "legitimately conditional" from "abandoned behind an
   opt-in" still needs an adapter-declared expectation, and a sample-history repair for
   it was already built, measured defective and reverted.
5. **The unshipped-path arm in [export_self_sufficiency_lib.py](../scripts/export_self_sufficiency_lib.py)**
   counts AST literal nodes, so a subpath written as one literal escapes it.
6. **The canonical close-keyword scanner still misses `GH-N` and issue-URL forms.** The new
   guard widened DETECTION for itself only; every other consumer of the shared scanner
   function [iter_close_keyword_refs](../skills/public/issue/scripts/issue_verify_closeout_body.py)
   still cannot see them. Widening the shared one touches many surfaces.
7. **Residuals disclosed inside the closed issues, now unowned**: #623's consuming repos
   still read a literal `<authoring-repo>` placeholder; #625's seeder is not re-prompted
   after a cold start and its file mode differs from its sibling's; #626's graduated
   lessons stay `active` against the budget. Each is stated in that issue's close comment.

## Discuss

- **Every review round this session found a defect in the previous round's repair.** At
  five boundaries: the guard, the gate runner, the release notes, the closeout bodies, and
  twice inside one sentence. The two-round cap is a floor, and the class it catches is the
  fix that carries what it fixed.
- **A reviewer caught an edit I reported making and had not made.** A `replace()` with no
  assert silently did nothing and I described the result as repaired. Scripted edits to a
  claim surface should assert their anchor and read back.
- **Splitting the aggregate close body did not split the habit.** The first per-issue draft
  still inherited a cross-issue uniqueness sentence verbatim from the ledger it replaced,
  plus a comparative that was factually wrong about a sibling issue.
- **The gates refused three pushes and four release attempts, and every refusal was real**:
  a docs ratchet, a runtime budget, a false claim in prose, and ungrounded quantities.
- **Editing this file can turn SC14 red**: it substitutes into the real handoff and needs
  the bare backticked `python3 scripts/run_standing_pytest.py` as its anchor.

## References

- [Design north star](./design-north-star.md) — P4, the different-observer rule that earned
  every blocker this session.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique floor
  and the write-capable isolation rule.
- [Implementation discipline](./conventions/implementation-discipline.md) — the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
