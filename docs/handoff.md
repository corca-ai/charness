# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1. Item 1 of the previous handoff is DONE and its
  three commits are unpushed; the release decision is still the open question.

## Continuation Capability

- [S9 critique](../charness-artifacts/critique/2026-08-16-s9-close-keyword-prepush-guard.md) — both
  rounds, F1-F15, and the two blockers round 2 found inside round 1's repairs.
- [S8 critique](../charness-artifacts/critique/2026-08-16-s8-handoff-five-and-coverage-debt.md) — the
  previous range's findings and which forced a reversion rather than a patch.
- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the
  owner-approved scope and its sequence.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.

## Current State

- **The close-keyword pre-push guard exists and blocks.**
  [prepush_close_keyword_guard.py](../scripts/prepush_close_keyword_guard.py) applies the
  commit-msg closeout floor to every close keyword in a push range, reading STORED
  messages. Re-prove over the commit that closed #626 (find it with
  `git log --format='%H %s' --grep='S7 closes' -i origin/main`): the guard refuses it,
  and the other 19 close-keyword commits in the last 400 pass.
- **The root cause of the #626 close is repaired.** The carrier stripped `^\s*#` lines as
  git comments — right for an editor message, wrong for the `-m`/`-F` message actually
  stored — so it scanned text the repo never held. See
  [check_issue_closeout_commit_msg.py](../scripts/check_issue_closeout_commit_msg.py)
  `_close_keyword_scan_text`.
- **The changed-line proof is CLEAN for this range**, not `partial`: run
  [prepush_focused_changed_line_coverage.py](../scripts/prepush_focused_changed_line_coverage.py).
- Re-prove the suite with `python3 scripts/run_standing_pytest.py --include-release-only`
  after `python3 scripts/sync_root_plugin_manifests.py`; ruff needs `--no-cache`.

Non-claims: the release is still PREPARED, not published — no push, tag, bump, publish,
hosted CI, installed-consumer readback, or issue closure has run. This range's three
commits are LOCAL. Round-2 repairs and the coverage tests after them ship at the
two-round cap, unreviewed. NO consuming repo has run this tree.

## Next Session

1. **Do not run a fourth claims round on the same body.** The publish is STOPPED at
   `unproven`. The stop, its three rounds, and what each round CONFIRMED are recorded in
   [the claims review](../charness-artifacts/release-review/2026-08-16-v6.0.0-claims-review.md), which
   is worth reading before deciding anything about the release. Each round found
   a NEW real defect, including one INTRODUCED by the previous round's repair, so the
   finding is about the body rather than the reviewers. Two exits, in order of
   preference: split the close into batches so no aggregate count sentence exists, or
   derive the per-issue claims from the critique's structured `F` findings, which
   already carry the issue number the prose keeps mis-attributing.
2. **Close the issues this range resolves**, through whichever exit item 1 picks.
   #632, #528 and #618 are resolved; #634 and #546 are NARROWED and must not be
   closed. #626 needs its missing closeout body added as a COMMENT — owner ruled do
   NOT reopen. Map each requested outcome to executed proof before claiming closable.
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
6. **The canonical close-keyword scanner still misses `GH-N` and issue-URL forms.**
   The new guard widened DETECTION for itself only; every other consumer of
   [iter_close_keyword_refs](../skills/public/issue/scripts/issue_verify_closeout_body.py)
   still cannot see them. Widening the shared one touches many surfaces.

## Discuss

- **Round 2 earned its cost for the third slice running, and this time inside my own
  repair.** The new maintainer arming check counted a MENTION as an invocation and
  tested `|| true` against the wrong line of a two-line command — verbatim the class the
  SIBLING arming check's own round 2 had already removed. Re-deriving a judgment instead
  of calling the module's existing parser re-created it.
- **The gate that would have caught #626 already existed and reported `not_applicable`.**
  Replaying it on the stored body is what found the cause. A floor that MODELS what
  another tool will do is a floor that can be silently wrong about it.
- **Editing this file can turn SC14 red**: it substitutes into the real handoff and
  needs the bare backticked `python3 scripts/run_standing_pytest.py` as its anchor.
- **`keyword-in-prose-is-a-directive` recurred as its own repair.** It was SEEDED but
  not presented at S8 close; this session consumed it from this file alone.
- **I piped a gate through `tail` and it masked a ruff failure** until the commit hook
  caught it — the rule is in CLAUDE.md and I broke it inside the session that added a gate.

## References

- [Design north star](./design-north-star.md) — P4, the different-observer rule that earned
  every blocker this session.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique floor
  and the write-capable isolation rule.
- [Implementation discipline](./conventions/implementation-discipline.md) — the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
