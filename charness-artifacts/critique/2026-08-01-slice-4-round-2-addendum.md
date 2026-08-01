# Slice 4 round-2 addendum — the test that asserted a substring

Date: 2026-08-01
Goal: [close-the-sweeps-remaining-high-rows-by-class](../goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md)
Extends: [the slice-4 critique](./2026-08-01-slice-4-a-refused-verdict-states-its-refusal.md),
which recorded round 2 as an open gap. The operator asked for it; this is what it found.

## Reviewer Tier Evidence

- Requested tier: bounded read-only reviewer (`bounded-reviewer` typed agent)
- Requested spawn fields: agent_type=bounded-reviewer, unnamed spawn, session-model
  inheritance. Claude Code host, so the Codex model/effort request does not apply.
- Host exposure state: requested_fields_sent
- Application state: the spawn was accepted and returned findings inline.
- Delivery state: findings-received

## Reviewer Provenance

Fresh-eye satisfaction: parent-delegated

One bounded `bounded-reviewer` subagent, spawned unnamed in the shared parent worktree
with Read/Grep/Glob only, reading the committed surface at `d8318b07`.

Worktree integrity: snapshot opened window `slice4-round2`, and the tree was CLEAN at the
snapshot — the first review window this session to open on a committed tree.
**Non-claim:** the matching `verify` still was not run.

## Findings

Four blockers, and the sharpest is about this slice's own test.

1. **`test_s2_the_release_carrier_also_clears_its_confirmation` asserted a source
   SUBSTRING.** It checked that the string `sync_confirmation_line` appeared in the file
   and that the module imported. It passes if the call is deleted and a comment remains,
   if it sits in an unreachable branch, or if it runs BEFORE the flip it is meant to
   follow. In a file whose stated thesis is "does the thing that SAYS the verdict still
   agree with the thing that DECIDED it", **the test's own verdict had outlived its
   check** — the class, reproduced in the pin. Replaced with a behavior test driving
   `validate_release_closeout_commit_message` with an unexpected `Close #45`, asserting
   `ok is False` and `confirmation["line"] is None`.
2. **The back-compat shim handed the new class to a consumer that labels it with the old
   name.** `check_doc_authoring_preflight.collect_wrapped_inline_code` calls the two-tuple
   shim, which drops the reason, so an unterminated finding rendered as
   `wrapped-inline-code` — the exact operator misdirection the checker had just split a
   message for. The CLI was fixed; its sibling in-repo consumer was not. That consumer
   also applies no `EXCLUDE_PARTS`, so it can be pointed at the very `charness-artifacts/`
   files the measured zero excludes.
3. **The checker's own summary line re-asserted the classification it had just split**
   ("N wrapped inline code span(s) found"), six lines below the fix.
4. **The misdirection is not confined to the new class.** With a stray backtick on its own
   line, the stray pairs with the real opener and a WRAPPED finding is emitted at the
   stray's line, where nothing wraps. The comment and the S2 closure note both claimed the
   problem was confined to the unterminated branch; both now admit otherwise.

Plus: the S23 row's `surface:line` was stale AGAIN — the repair inserted ~25 lines above
it, so a pointer that used to land on the confirmation construction now lands on `ok = (`.
The `is not None` guard on the release carrier was dead code the early raise makes
unreachable. The flip overwrote the draft status vocabulary with the post-publication one.
And `closeout-discipline.md`, the doc that tells handoffs to quote the confirmation line,
never said the field can be null.

## Round 3 — NOT RUN

The cap is two rounds. These repairs ship **accepted-unreviewed**.

## Boundary Ownership

- Verdict: owned-correctly

The reason token belongs with the producer (`find_inline_code_violations`), and both
consumers — the CLI and the preflight — now decide their own rendering from it. The
two-tuple shim stays for callers that do not care, with the reason available to callers
that do. Extracting the preflight's renderer into `_inline_code_lines` was forced by the
complexity gate and is the same boundary: one place decides how each class reads.

## Non-claims

Round 3 did not run. S2 stays NARROWED with the widened residual now on its row. The
changed-line mutation gate reports uncovered changed lines in this goal's two new
measurement scripts; that is the bundle's open item, not this addendum's.
