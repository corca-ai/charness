# Achieve Goal: Stop a surface from returning success its own evidence contradicts

Status: active
Created: 2026-08-06
Activation: `/goal @charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: A — repair this artifact, and close the pursue-ready scope gap
  it exposed.
- Current slice intent: this artifact was activated in a materially damaged
  state (9 sections absent — 7 of the 11 required plus 2 of the 3 portability
  headings, per the full check quoted in `## Goal`) and `--pursue-ready` still said
  `safe to pursue`. Slice A restores the artifact and makes the activation
  verdict state the scope it measured. Once active, this names the
  reviewable-intent unit in progress and the commits it spans; critique and
  broad proof do not re-fire within one unchanged intent — update it when the
  intent changes, not per commit (meaningful-slice-cadence).
- Next action: reconstruct-and-commit the artifact repair, then fix
  `pursue_readiness` so its verdict names what it did not check.
- **Non-claim carried from the first minute — what is rebuilt and what survived.**
  **RECONSTRUCTED** (written 2026-08-06 from the three issues, the shaping commit
  message `db20ccfc`, and `docs/handoff.md`; the original text never reached disk
  and is not recoverable): `## Goal`, `## Non-Goals`, `## Boundaries`,
  `## User Acceptance`, `## Agent Verification Plan`, `## Slice Plan`,
  `## Context Sources`, and `## Slice Log` (empty — the goal had not run).
  **SURVIVED VERBATIM** at `db20ccfc` and was copied byte-for-byte, with only its
  swallowed H2 heading line restored above it: the BODY of
  `## Interview Decisions` (decisions 1 and 2) and of
  `## Operator Decision Queue`. Verify with
  `git show db20ccfc:charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md`
  — that text is present there, headingless, spliced into the middle of the
  frame's last bullet. Interview Decision **3** is new, written by this session,
  and says so in its own text. Treat the reconstructed sections as this session's
  shaping, not the prior session's.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`, and
  `## Auto-Retro`.

## Goal

*(Reconstructed 2026-08-06 — see the non-claim in the frame.)*

**Three surfaces bit live during the #481 goal, and each returned a success its
own evidence contradicts.**

1. [#488](https://github.com/corca-ai/charness/issues/488) — the changed-line
   mutation lane printed `this run analyzed only 6 of 7 changed mutation-pool
   file(s). A clean verdict says NOTHING about the rest`, set `"blocking": []`,
   and exited the same code it exits with no blind spot. The push landed;
   remote CI then blocked on the 7th file.
2. [#489](https://github.com/corca-ai/charness/issues/489) — a partially-deleted
   `coverage_floor_policy:` block is refilled from the preset by
   `merge_coverage_floor_policy`, and the report calls the field `preserved`.
   The status line asserts the opposite of what the merge did.
3. [#487](https://github.com/corca-ai/charness/issues/487) — `achieve`'s
   slice-log helpers take free prose through `argv`, so a shell expands
   backtick-quoted identifiers before the process starts. The helper exits 0 and
   reports `"action": "appended"` over a record with holes in it.

**The class, and the deliberate exception.** #488 and #489 are one mechanism: a
surface COMPUTES a scope-limiting fact and then DISCARDS it at the moment it
would change the answer. #488 computes `unanalyzed_changed_pool_files` and does
not let it reach the exit code; #489 computes which sub-keys the merge refilled
and does not let it reach the status. #487 shares the symptom and NOT the
mechanism — the loss happens before the helper's `argv` exists, so there is
nothing inside the process to discard. It is carried for cost and repaired
differently, on the recorded axis that *three symptoms in one session are
evidence of a class only if the MECHANISMS match*.

**A fourth instance, found by activating this goal (2026-08-06).**
`check_goal_artifact.py --pursue-ready` reported `pursue_ready: true`,
`"shaped: no Before-phase placeholders remain; safe to pursue via /goal"`, exit
0 — on this artifact, while the sibling full check on the same bytes reported
`ok: false`, exit 1, `missing sections: Goal, Non-Goals, Boundaries, User
Acceptance, Agent Verification Plan, Slice Plan, Slice Log` plus
`missing portability sections: Context Sources, Interview Decisions`. The
`--pursue-ready` mode measures placeholder markers only, by design, and then
renders a verdict phrased over the whole artifact. `/goal` activation consults
only that mode. Same class as #488, in `achieve`'s own activation gate, and
folded into scope because it fired on this goal's first command.

The outcome is that a proof surface which could not cover its whole scope says
so **in the answer**, not only in prose beside it.

## Non-Goals

*(Reconstructed 2026-08-06.)*

- **Not the dotted sub-key vocabulary for `deliberately_absent`.** Decided by
  the operator 2026-08-05: #489 gets an honest STATUS first. The dotted
  vocabulary is deferred as a larger verification and ambiguity surface, not
  rejected as wrong.
- **Not a full local mutation runner.** #488 is about the verdict the existing
  changed-line lane returns, not about widening what it analyzes.
- **Not the unreachable-file cluster** (#482/#483/#484). Rejected at shaping as
  a second, heterogeneous family that would put the timebox at risk.
- **Not the E-cluster, not D41–D50, not #480/#468/#475.**
- **Not re-litigating `mask_fences`' fail-open.** Adjacent, already reasoned
  through in `goal_artifact_markdown.py`, out of scope.

## Boundaries

*(Reconstructed 2026-08-06.)*

- **External side-effect scope.** Issue CREATION is standing per `AGENTS.md`.
  `git push` is standing CONDITIONAL ON THE GATES — a refusing gate withdraws
  it, and nothing gets weakened to reach a green push. Closing #487/#488/#489 is
  standing CONDITIONAL ON THE CLOSEOUT FLOOR. PR, release, tag, version bump,
  and `cautilus evaluate` are NOT covered and are not requested.
- **This goal edits a gate that guards pushes.** Its own pushes may be refused
  by the rule it installs. That is the rule working, not a reason to relax it.
- In scope: `scripts/check_changed_line_mutation_coverage.py` and its pre-push
  wiring; `scripts/quality_bootstrap_lib.py`'s `merge_coverage_floor_policy` and
  `_add_adapter_policy_fields`, plus `scripts/quality_bootstrap_absence.py`'s
  refill claim; `skills/public/achieve/scripts/append_slice_log.py` /
  `upsert_goal.py` input channel; `goal_artifact_lib.pursue_readiness`; and the
  `plugins/` mirror of anything touched.
- Stop conditions:
  1. **If the #488 repair makes the lane refuse constantly**, stop — a gate that
     blocks every push is not a repair, and shipping one in place of the current
     false green trades one wrong answer for another.
  2. **If #489's honest status turns out to need the dotted vocabulary after
     all**, STOP and re-ask; the operator scoped that out on purpose, so
     discovering it is unavoidable is a design change, not an implementation
     detail.
  3. **If #487's repair requires changing every skill helper's documented call
     shape**, stop at the `achieve` helpers and record the sweep rather than
     performing it.
- **Cut order if short: #487, then #489.** #488 is the one that let a defect
  reach `main`.

## User Acceptance

*(Reconstructed 2026-08-06.)*

- **The #488 lane cannot return a bare pass over a changed set it did not fully
  analyze**, proven by reproducing the live condition (a changed pool file that
  maps to no standing test) and showing the exit code changes.
- **The #489 report does not say `preserved` about a block whose sub-keys the
  merge refilled**, proven by the reproduction pasted on #489 verbatim: the
  status is honest AND the refilled sub-keys are named.
- **The #487 helpers cannot silently receive truncated prose**, proven by
  driving the real lossy channel (a backtick-bearing string through a shell) and
  showing the content arrives whole or the call fails loudly.
- **The activation gate's verdict states its scope**, proven by re-running
  `--pursue-ready` on a deliberately gutted artifact and getting an answer a
  reader cannot mistake for "this artifact is complete".
- **Every new or changed rule is proven to BITE** by reintroducing the real
  defect, not by asserting the new branch exists.
- **Every figure carries `<value> — <source>`**, with its denominator and date.
- **Non-claim in writing**: name which channel reached which tree, and never let
  a local green stand in for remote CI.

## Agent Verification Plan

*(Reconstructed 2026-08-06.)*

### Low-Cost Checks

- **Reproduce each issue before designing its fix.** All three carry a concrete
  reproduction; a fix designed before the observation is a fix for the report.
- **Check whether the fact is already computed.** For #488 and #489 the
  scope-limiting fact is believed to exist already (`unanalyzed_changed_pool_files`;
  the merge's own refill set) — verify that before adding a new computation.
- Sync `plugins/` mirrors before validators; obey the dup-ratchet edit advisory.
- `run_slice_closeout.py --skip-broad-pytest` at pre-lock slice boundaries.

### High-Confidence Checks

- **TWO bounded rounds for any slice that changes VERDICT LOGIC**, round 2
  reading the repairs. #488, #489, and the pursue-ready fix are all verdict
  surfaces, so all three owe it. Measured eight times; the round that reads the
  repairs is where the class comes back.
- `reviewer_boundary_fingerprint.py snapshot` around each review, `verify` the
  moment the reviewer returns, before any parent write.
- A closeout-claims review by a distinct observer before the completion flip.

### External Or Live Proof

- `git push` to `main` and its CI — standing, conditional on the gates. Remote
  CI confirmed by a different observer AND a different channel than the push
  exit code; the combined-status API reads `pending`/`total_count: 0` here
  because this repo publishes check-runs, which is not a real pending.
- #488's own remote-CI block on `scripts/markdown_preview_bootstrap_lib.py` is
  the live evidence the repaired lane must be measured against.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Repair this artifact, and make `--pursue-ready` state the scope it measured | The goal's own memory surface was activated gutted, and the activation gate called it shaped | The full check green on this artifact; a gutted-artifact fixture where `--pursue-ready` no longer reads as "complete" | in progress |
| B | #488 — the changed-line mutation lane stops returning a bare pass over an unanalyzed changed set | This is the one that let a defect reach `main` and be chased backwards from CI | The live 6-of-7 condition reproduced, and the exit code / verdict changes; the gate still passes on a fully-analyzed changed set | pending |
| C | #489 — an honest status for a partially-refilled block | It is the residue the #486 fix left, and it is worse-reported than #481 was | #489's pasted reproduction run verbatim: status is not `preserved`, and the refilled sub-keys are named | pending |
| D | #487 — close the prose-through-argv channel for the `achieve` helpers | The loss is silent, and the surface is the record a resumed session reads | A backtick-bearing slice-log entry arrives whole, or the call fails loudly; proven through a real shell | pending |
| E | Closeout: bundle gate, claims review by a distinct observer, retro, issue closeout floors, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest number; `check_goal_artifact.py` green; each issue closed through its floor or explicitly deferred | pending |

## Operator Decision Queue

Both shaping decisions were RESOLVED by the operator on 2026-08-05 and are folded
into `## Interview Decisions`. Nothing is currently queued for the operator.

- Queued: none — the two shaping decisions are resolved and folded; no new
  operator-only decision has surfaced.

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from
  installed metadata/model judgment, and record the route. At completion,
  recorded implementation / debug / quality / issue work needs this `Routing:`
  evidence or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at
  the gathered asset, or write `Gather: n/a — <reason>`.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof.

- Routing: achieve — selected from installed skill metadata to operate this goal's lifecycle (slice sequencing, slice log, closeout floors); it delegates implementation to the repo's own impl/quality surfaces, issue to the three tracked issues, critique to the bounded rounds each verdict surface owes, and retro to the after-action review.

## Discuss Before Activation

- Discuss before activation: RESOLVED at design time. No release surface, no
  live/prod proof, no broad scope. The two consequential calls are recorded as
  Interview Decisions 1 (scope is all three issues) and 2 (#489 reports an
  honest status rather than growing a dotted vocabulary). Push is standing
  conditional on the gates; issue close is standing conditional on the closeout
  floor.
- **This goal is ready to run.**

## Slice Log

### Slice 1: A - Repair the artifact, and make the activation verdict state its scope

- Objective: Restore the 9 sections this goal artifact was activated without (7 required + 2 portability), and stop `check_goal_artifact.py --pursue-ready` from calling a gutted artifact `safe to pursue`.
- Why this approach: The artifact is the goal's memory surface, so a slice cannot be planned from it while it is empty; and the gate that let it through is the same class the goal is about (a verdict phrased over a scope it did not measure), found on this goal's first command rather than looked for.
- Commits: one commit, subject "Make the only gate in front of /goal state the scope it measured". Named by SUBJECT rather than SHA on purpose: this artifact ships INSIDE that commit, so writing the SHA in requires an amend, and the amend changes the SHA the line just recorded. The SHA is recorded once in `## Final Verification` at closeout, when it is no longer self-invalidating.
- What changed: NEW skills/public/achieve/scripts/goal_artifact_pursue.py holds the readiness concept (goal_artifact_lib.py was 374/360 code lines after the change); the section floor + `scope_not_checked` + multi-clause `reason` + an unbalanced-fence refusal live there; goal_artifact_lib.pursue_readiness is now a wrapper injecting REQUIRED_SECTIONS+PORTABILITY_SECTIONS, status, mask_fences, fences_balanced, discussion_readiness, draft_frame_disposition. Dead `_UNSHAPED_MARKER` deleted from lib rather than copied. SKILL.md + references/lifecycle-before.md document the second unshaped form. NEW tests/quality_gates/test_goal_artifact_pursue.py (source test file was 821/800). Goal artifact reconstructed and labelled.
- Alternatives rejected: Report-only (add `missing_sections` to the payload and keep `pursue_ready: true`) was rejected: the false green would survive, and `/goal` consults only the exit code. Making `shape_ready` itself mean completeness was rejected: it would overload an established signal, so completeness is a separate dimension. Re-running the whole Before phase and re-interviewing the operator was rejected because decisions 1 and 2 survived verbatim in the damaged file.
- Targeted verification: python3 -m pytest tests/ -q -k 'goal or achieve' -> 452 passed after the round-1 repairs (449 before them, 2026-08-06). Live: gutted 5-line artifact -> exit 1 naming 14 absent headings; repaired real artifact -> exit 0; all-headings-inside-one-unclosed-fence -> exit 1 `unreadable:`. check_python_lengths -> exit 0. check_dup_ratchet -> status clean, 0 new families. reviewer_boundary_fingerprint verify -> clean.
- Test duplication pressure: check_dup_ratchet --summary reports 0 new code and 0 new doc fixable-eligible families after the extraction; the first attempt DID add 2 (the `_load_sibling` boilerplate), which is why the new module takes injected callables instead of loading its own siblings.
- Critique: Bounded fresh-eye round 1 (delegated, read-only) returned 2 blockers, both folded. B1: pursue_readiness never consulted `fences_balanced`, and `mask_fences` fails open on odd parity - so 14 headings inside one unclosed fence read `sections_complete: true` and `pursue_ready: true`, the exact two-verdicts-on-one-bytes shape this slice closes, one command from the gate it repaired. B2: the artifact's reconstruction label omitted `## Interview Decisions` and `## Slice Log`, so operator decisions 1-2 read as established rather than as recovered text. Also folded: the PASS sentence named only the marker fact while standing in for a four-dimension verdict; and the CLI `_write_discussion_goal` fixture was over-determined by the new section floor. Round 2 (delegated, read-only, reading the REPAIRS) returned NO blocker and one HIGH: R1 removed `fence balance` from `scope_not_checked` in code but left the shipped reference `lifecycle-before.md` still listing it as not-established, and the new `unreadable:` refusal undocumented - a verdict-scope surface disagreeing with the verdict, one file from the gate this slice repaired. Folded, both copies. Also folded: two wrong figures in this artifact (9 was the TOTAL, not the required count; the test count was pre-repair), and two comment/docstring staleness nits. Round 2 confirmed clean: `fences_balanced` and `mask_fences` share one predicate so they cannot disagree about parity; the rule was injected, not re-derived; no caller matches the pass string; `_REMAINING_SECTIONS` covers exactly 13 of 14 with no doubled `## Non-Goals`. It also noted the balanced-fence CONTROL test is non-discriminating by design (it would pass pre-repair too) - it is a false-refusal guard, not bite proof; the refusal test is what bites. Cap: two rounds; no round-3 repairs were made.
- Off-goal findings: Issue #490 filed (the pursue-ready scope gap), plus a correction comment on it — the body miscounted 9 total sections as 9 required. Nothing else off-goal yet.
- Fresh-eye pass: skills/public/achieve/scripts/goal_artifact_pursue.py — the new proof surface this slice was born with. Read by BOTH bounded rounds by a different agent context: round 1 refused it over the fail-open fence reading, round 2 re-derived `fences_balanced`/`mask_fences` parity agreement line by line and cleared the repair. Classified: it IS a verdict surface (it renders `pursue_ready`, the only gate in front of `/goal`), which is why it took two rounds rather than the advisory's one.
- Lessons carried forward: The goal's own activation command produced a fourth instance of the class the goal was shaped around, before any planned slice ran. And the round-1 repair for it carried the class it fixed: the section floor was rendered over a fail-open reading nobody established. That is the ninth measured time the repairs are where the class comes back.
- Metrics: 1 goal artifact, 9 sections restored - 7 of 11 required + 2 of 3 portability, 2026-08-06. 14 headings absent on the 5-line reproduction. goal_artifact_lib.py 374 -> under the 360 cap after extraction; test_goal_artifact_lib.py 821/800 -> under the cap after the pursue tests moved out.

## Context Sources

*(Reconstructed 2026-08-06.)* Durable references this goal was shaped from. A
fresh session can reconstruct the originating context by following them in order.

1. [issue #488](https://github.com/corca-ai/charness/issues/488) — the live
   local-pass / remote-block transcript. Read this first; it is the instance
   that reached `main`.
2. [issue #489](https://github.com/corca-ai/charness/issues/489) — carries a
   copy-pasteable reproduction and the three candidate directions, of which the
   third is the chosen one.
3. [issue #487](https://github.com/corca-ai/charness/issues/487) — the
   prose-through-argv channel, with the observed `command not found` transcript
   and the reason the helper cannot fix it from inside.
4. [design-north-star.md](../../docs/design-north-star.md) — P4 governs all
   three: a proof surface's success is provisional, and a terminal green is not
   a verdict.
5. [the completed #481 goal](2026-08-05-make-deliberate-absence-representable.md)
   and [its resolution critique](../critique/2026-08-05-issue-485-486-resolution-critique.md)
   — where all three issues were found, and the round-2 discipline they owe.
6. [recent-lessons.md](../retro/recent-lessons.md) — repeat traps that should
   change the next move.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

*Decisions 1 and 2 SURVIVED VERBATIM at `db20ccfc` — only this heading line was
lost, and the text below it is a byte-for-byte copy of what was there. Decision 3
was written by this session on 2026-08-06.*

1. **What is the unit of the goal?** Family considered: {#487+#488 only, as the
   operator first said; add #489; add the unreachable-file cluster}. **Chosen by
   the operator 2026-08-05: #488 + #489 + #487.** #488 and #489 are genuinely the
   same class and share a ruler, so splitting them would stand the same reviewer
   up twice; and leaving #489 out strands the residue the previous goal's own fix
   created. The unreachable-file cluster was rejected as a second, heterogeneous
   family that would put the timebox at risk. Anti-anchoring: `axis: three
   symptoms in one session is evidence of a class only if the MECHANISMS match —
   check before unifying`. That check is why #487 is carried but explicitly not
   folded into the class.
2. **#489's direction.** Family considered: {let `deliberately_absent` name dotted
   sub-keys; report an honest status; decide after replaying the merge}. **Chosen
   by the operator 2026-08-05: report an honest status first** — `augmented` plus
   the refilled sub-keys, instead of `preserved`. The false statement is the part
   that misleads a reader, and removing it needs no schema change and breaks
   nothing. The dotted vocabulary was rejected FOR NOW as a larger verification and
   ambiguity surface, not as wrong. Anti-anchoring: `axis: the smallest honest
   change is the one that stops the surface from asserting something untrue, not
   the one that makes the feature complete`.
3. **What to do about the gutted artifact found at activation (decided by this
   session, 2026-08-06).** Family considered: {activate as-is and shape as we go;
   re-run the Before phase from scratch and re-interview the operator;
   reconstruct from the recoverable record and label it}. **Chosen: reconstruct
   and label.** The two operator decisions survived verbatim in the damaged file
   itself — headingless, but byte-for-byte — and again in `db20ccfc`'s message, so
   a re-interview would re-ask questions already
   answered; but presenting a reconstruction as the prior session's shaping would
   be exactly the class this goal is about. So every reconstructed section is
   marked as one. Anti-anchoring: `axis: a record you rebuilt is evidence about
   what you could recover, not about what was originally written`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
