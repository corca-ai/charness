# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1. The handoff's five blocking items are closed or
  narrowed, and the release lane is green for the first time in this range.

## Continuation Capability

- [S8 critique](../charness-artifacts/critique/2026-08-16-s8-handoff-five-and-coverage-debt.md) — both
  rounds, F1-F12, and which findings forced a reversion rather than a patch.
- [S8 retro](../charness-artifacts/retro/2026-08-16-s8-the-handoff-five-and-the-aggregate-coverage-debt.md) — the
  executed-vs-read-field class, and the two round-1 repairs that were worse than what they replaced.
- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the
  owner-approved scope and its sequence.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.

## Current State

- **The release lane is GREEN**: `95 passed, 0 failed`. Re-prove with
  [run-quality.sh](../scripts/run-quality.sh) `--release`.
- **The aggregate changed-line proof is OBTAINED for the first time** — 244 uncovered
  lines over `merge-base origin/main HEAD` are now zero. The focused proof lives in
  [prepush_focused_changed_line_coverage.py](../scripts/prepush_focused_changed_line_coverage.py) and
  reports `partial`, not `pass`, because 19 changed files map to no standing test.
- **Four consumer-facing defects are repaired**, and six runtime bars drawn at ~1.0x of
  observed were relevelled as a class; both are F1-F12 of the
  [S8 critique](../charness-artifacts/critique/2026-08-16-s8-handoff-five-and-coverage-debt.md), which
  also records which findings forced a reversion rather than a patch.
- Re-prove the suite with `python3 scripts/run_standing_pytest.py --include-release-only`
  after `python3 scripts/sync_root_plugin_manifests.py`; ruff needs `--no-cache`.

Non-claims: the release is still PREPARED, not published — no tag, bump, publish,
hosted CI, installed-consumer readback, or issue closure has run. Round-2 repairs ship
at the two-round cap. Every consumer-facing judgement is from reading the export's
layout against the instruction text; NO consuming repo has run this tree.

## Next Session

1. **Build the close-keyword pre-push guard.** Pushing this range closed #626: an
   earlier commit message carried the prose "S7 closes\n#626/#627/#631" describing a
   future release, and the host read `closes #626` as a directive. Only #626 bound —
   the `/` separator stops the link — and a scan of all sixty messages found no other.
   **Owner ruling: do NOT reopen**; the state was the intended one and only the
   closeout body is missing, so add that body as a comment instead. The existing guard
   inspects a staged `charness-artifacts/issue/*.md` for `Closes #N` and cannot see a
   keyword inside a sentence; the new one scans the push range for the host's own
   keyword grammar. Smallest item here, and the only one that prevents a repeat of an
   irreversible act.
2. **Do not run a fourth claims round on the same body.** The publish is STOPPED at
   `unproven`. The stop, its three rounds, and what each round CONFIRMED are recorded in
   [the claims review](../charness-artifacts/release-review/2026-08-16-v6.0.0-claims-review.md), which
   is worth reading before deciding anything about the release. Each round found
   a NEW real defect, including one INTRODUCED by the previous round's repair, so the
   finding is about the body rather than the reviewers. Two exits, in order of
   preference: split the close into batches so no aggregate count sentence exists, or
   derive the per-issue claims from the critique's structured `F` findings, which
   already carry the issue number the prose keeps mis-attributing.
3. **Close the issues this range resolves**, through whichever exit item 2 picks.
   #632, #528 and #618 are resolved here; #634 and #546 are NARROWED and must not be
   closed. Map each requested outcome to executed proof before claiming closable.
4. **[#634](https://github.com/corca-ai/charness/issues/634) residual.** Only the
   shell-gate half landed. The cwd-relative instruction sites are UNREPAIRED and the
   detector for them was reverted: it pushed a documentation placeholder into four
   EXECUTED command fields and refused correct consumer prose. Any retry must first
   separate fields that are READ from fields that are RUN.
5. **[#546](https://github.com/corca-ai/charness/issues/546) residual.** The count is
   first-class now; separating "legitimately conditional" from "abandoned behind an
   opt-in" still needs an adapter-declared expectation, and a sample-history repair for
   it was already built, measured defective and reverted.
6. **The unshipped-path arm in [export_self_sufficiency_lib.py](../scripts/export_self_sufficiency_lib.py)**
   counts AST literal nodes, so a subpath written as one literal escapes it.

## Discuss

- **Round 2 earned its cost twice over.** Six defects in round 1's repairs, two of them
  worse than what they replaced — a root-level gate silently dropped out of DISCOVERY,
  and a pointer added to remove a duplicated list dangled in the one payload a reviewer
  reads. One round would have shipped both.
- **Editing this file can turn SC14 red**: it substitutes into the real handoff and
  needs the bare backticked `python3 scripts/run_standing_pytest.py` as its anchor.
- **Four of five scored lessons were `read-but-not-applied`.** The counted-limit trap and
  the changed-line-proof ordering both recurred with the lesson naming them presented at
  session open, which is a carrier problem rather than an authoring one.
- **This session's two most expensive lessons are SEEDED but not PRESENTED.**
  `prose-claim-without-a-reader` and `keyword-in-prose-is-a-directive` sit in the
  selection index at weight 1.0 and lost their digest slots to recurring classes, so
  this file is their only carrier until they recur. Between them they cost an
  irreversible issue close and three refused publish attempts.
- **Five false claims in artifacts, every one found by a reviewer and none by me**,
  with the gates green throughout: gates check the tree, not what prose says about it.

## References

- [Design north star](./design-north-star.md) — P4, the different-observer rule that earned
  every blocker this session.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique floor
  and the write-capable isolation rule.
- [Implementation discipline](./conventions/implementation-discipline.md) — the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
