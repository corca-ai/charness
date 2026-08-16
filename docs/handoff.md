# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1. The release IS PUBLISHED, its two should-fix claims
  are repaired in the tree, and the real-host checklist is still the one unrun proof.
  Read the tag with `git describe --tags --abbrev=0`.

## Continuation Capability

- [S9 critique](../charness-artifacts/critique/2026-08-16-s9-close-keyword-prepush-guard.md) — both
  rounds, F1-F15, and the two blockers round 2 found inside round 1's repairs.
- [Prepared claims review](../charness-artifacts/release-review/2026-08-16-v6.0.0-prepared-claims-review.md) —
  the two should-fix findings, now marked repaired in the tree with the notes unchanged.
- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the
  owner-approved scope and its sequence.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.

## Current State

- **The prepared major release is PUBLISHED**, not a draft or prerelease. Read the tag
  with `git describe --tags --abbrev=0`, then re-prove the published state with
  `gh release view "$(git describe --tags --abbrev=0)" --repo corca-ai/charness`.
- **The published notes' two should-fix claims are repaired in the TREE**, notes bytes and
  tag unchanged. Status is recorded in the
  [prepared claims review](../charness-artifacts/release-review/2026-08-16-v6.0.0-prepared-claims-review.md).
- **The shared close-keyword scanner now sees `GH-N` and issue URLs**, case-insensitively,
  so every consumer of
  [iter_close_keyword_refs](../skills/public/issue/scripts/issue_verify_closeout_body.py)
  sees what only the pre-push guard saw. Re-prove with
  `python3 -m pytest tests/quality_gates/test_prepush_close_keyword_guard.py -q`.
- **`sync_command` and `quality_command` are the release adapter's only EXECUTED fields**,
  checked rather than rewritten;
  [bump_version.py](../skills/public/release/scripts/bump_version.py) refuses a missing
  target before it writes the version.
- Re-prove the suite with `python3 scripts/run_standing_pytest.py --include-release-only`
  after `python3 scripts/sync_root_plugin_manifests.py`; ruff needs `--no-cache`.

Non-claims: the release's real-host checklist has NOT been run — no `charness update`, no
installed-vs-repo readback, no `nose` tool-doctor pass. Nothing in this range is pushed.
Items 4-7 below carry review rounds whose repairs are accepted-unreviewed at the cap.

## Next Session

1. **Run the release's real-host checklist.** It is the one proof the release shipped
   without: `charness update` on this machine, then `charness doctor` and a cited-check ==
   repo spot check, so the installed plugin is not skewed from the repo. The full list is
   in the published record [latest.md](../charness-artifacts/release/latest.md).
2. **Two latent traps the scanner widening opens, with no live instance today.** Re-sweep
   stored messages with
   `git log --format=%B origin/main | grep -inE '(close[sd]?|fix(e[sd])?|resolve[sd]?)[[:space:]:]+(GH-[0-9]+|https?://)'`.
   First, the
   closeout-artifact reader in
   [check_issue_closeout_commit_msg.py](../scripts/check_issue_closeout_commit_msg.py)
   derives an artifact's numbers from the same scanner, so unqualified prose naming an
   issue URL would demand a close keyword for an unrelated issue — and the remedy closes
   it. Second, a consolidated closeout takes the FIRST number in document order as its
   own, so a URL ref above the real keyword line changes which issue it thinks it is.
3. **[#634](https://github.com/corca-ai/charness/issues/634) residual, now HALF done.** The
   two adapter `command:` values that persist into consumer config are checked. The ~20
   remaining cwd-relative `python3 scripts/<x>.py` sites in exported docs and references
   are UNREPAIRED, and no detector exists: the reverted one pushed a documentation
   placeholder into EXECUTED fields. Re-measure with
   `rg -n 'python3 scripts/[a-zA-Z_0-9-]+\.(py|sh)' plugins/charness/skills`.
4. **[#546](https://github.com/corca-ai/charness/issues/546) residual.** Untouched. The
   count is first-class; separating "legitimately conditional" from "abandoned behind an
   opt-in" still needs an adapter-declared expectation, and a sample-history repair for it
   was already built, measured defective and reverted.
5. **Residuals still unowned inside closed issues**: #625's seeder is not re-prompted after
   a cold start and its file mode differs from its sibling's; #626's graduated lessons stay
   `active` against the budget. #623's `<authoring-repo>` placeholder is CLOSED — both the
   retro scaffold and the retro validator's refusal now resolve per repo.
6. **The pre-push guard has three disclosed exit-0 coverage holes**, named in its own
   [exit-code block](../scripts/prepush_close_keyword_guard.py): the creation cap, a stale
   remote-tracking exclusion reported nowhere, and `status: no-refs`, which cannot be told
   apart from a wrapper that drained the hook's stdin. Disclosed, not closed.

## Discuss

- **Every review round this range found a defect in the previous round's repair, again.**
  The adapter recognizer took two rounds to stop being a false-refusal source: a blacklist
  written to stop quoted/tilde/glob guesses missed `;`, `|`, `&&` and glob classes because
  `split()` breaks on whitespace only. The shape that ended it was inverting to an
  allowlist — a rule that cannot go stale.
- **A fix landing only in the CLI is a fix that does not ship.** The stdin fail-closed sat
  in `main` while `evaluate` — the exported function a consumer shim calls — kept
  returning `ok: true`. Put the decision where the fact is.
- **The commit-msg floor refused this range's own commit message**, because a draft spelled
  its failing examples as close verbs directly before a ref. That is the widening working,
  and it is the first evidence item 2's channel is reachable from ordinary prose.
- **Editing this file can turn SC14 red**: it substitutes into the real handoff and needs
  the bare backticked `python3 scripts/run_standing_pytest.py` as its anchor.

## References

- [Design north star](./design-north-star.md) — P4, the different-observer rule that earned
  every blocker this session.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique floor
  and the write-capable isolation rule.
- [Implementation discipline](./conventions/implementation-discipline.md) — the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
