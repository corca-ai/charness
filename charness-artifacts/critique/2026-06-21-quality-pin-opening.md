# Quality pin-opening (first pin deletion) — critique

Date: 2026-06-21

## Decision Under Review

The first real "pin-opening": deleting gate-pinned skill contracts (not just
unpinned duplication) under the operator-agreed disciplined test — a gate pin
earns deletion only when it (a) freezes wording rather than proving behavior, or
(b) the behavior is owned canonically elsewhere. Operator-confirmed CONSERVATIVE
scope for `quality`:

- **Opened (criterion a):** two CORE pins in `scripts/check_skill_contracts.py`
  — `implementing that gate in the same turn` + `when the automatable move is
  already clear and repo-owned, implement it in` — deleted with the doubled
  SKILL.md wording they froze. The step-7 `## Workflow` paragraph stated the
  same-turn-implement rule twice; collapsed to one statement. quality CORE pins
  7 → 5.
- **Kept (teeth where a wrong answer escapes):** the inline cautilus guard (CORE
  pins 6–7) — load-bearing point-of-use safety at a destructive boundary, even
  though `CLAUDE.md` + `cautilus-on-demand.md` also own it.
- **Not done:** the 49-entry reference list — `validate_skills.py` locks it to
  the `references/` directory (every file must be listed), so reducing it is a
  file-deletion effort, not a list trim. Deferred.

This is the pilot that licenses a harness-wide pin sweep, so a wrong call here
propagates.

## Failure Angles

- **Behavior loss masquerading as wording-freeze:** the two deleted pins encoded
  a distinct behavioral nuance (the `unless review-only` exception, the
  `repo-owned` qualifier) that the surviving pins + collapsed prose do not carry.
- **Orphaned consumer:** a test, gate, or artifact other than
  `check_skill_contracts.py` depended on the deleted phrases.
- **Pin wrap-split / silent downgrade:** a surviving pin (esp. the cautilus
  guard) wraps across a line break and silently fails its `in` test, or the
  cautilus guard gets weakened.
- **Overclaim:** the dogfood entry calls this criterion (a) when it is really a
  behavior deletion.

## Counterweight Pass

One bounded fresh-eye reviewer (read-only, shared parent worktree, `git show
HEAD:<path>`) was tasked to REFUTE "disciplined, lossless pin-deletion." Verdict:
`DISCIPLINED-PIN-DELETION`. It performed a clause-level HEAD-vs-working-tree
diff: the two HEAD clauses were two phrasings of one rule; the collapse RETAINS
the `unless review-only was requested` exception (which lived only in the
deleted clause 2) and firms the soft `prefer implementing` into `implement it`
— strengthening, not weakening. It grepped both deleted phrases repo-wide: the
only live hits are the deleted pin rows + the descriptive dogfood entry; a
frozen `charness-artifacts/spec/2026-06-20-skill-body-measured-input.json`
records the old 7-pin list but no `.py` gate consumes it (historical snapshot,
not a live dependency). It confirmed 5 surviving pins present/unbroken (cautilus
guards at lines 76/79, point-of-use), both deleted phrases absent, mirrors
byte-identical, the contract gate green (13 core / 8 package), and 22 quality
docs tests passing.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: over-worry | evidence: strong | ref: charness-artifacts/spec/2026-06-20-skill-body-measured-input.json | action: document | note: this frozen 2026-06-20 measurement snapshot records the then-7-pin `core_pins` list for quality. The reviewer flagged it as the only other place the deleted phrases appear, but it is a point-in-time measurement artifact consumed by no `.py` gate/test — updating it would falsify the historical record. Left intentionally untouched.
- F2 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/SKILL.md | action: defer | note: the 49-entry reference list is the remaining quality bloat, but `validate_skills.py:332-342` requires every `references/*` file to be listed (`unlisted reference file(s)` is a hard error). So reducing it is a per-file deletion audit (prove each ref is uncited anywhere, incl. `inventory-dispatch.md` routing) — a separate careful pass, not a list trim. The `references/index.md` affordance (already used by `achieve`) would only RELOCATE the list, which the operator rejected as not-the-point. Deferred.
- F3 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_skill_contracts.py | action: defer | note: the pilot validates the pin-deletion discipline; the licensed next step is promoting it to a durable convention and running the harness-wide sweep over all CORE/PACKAGE pins (delete every pin that freezes wording or is owned elsewhere; keep destructive-boundary guards like cautilus). Deferred to a deliberate sweep.
- F4 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/quality/dup-ratchet-baseline.json | action: fix | note: the pre-push `dup-ratchet` gate hard-blocked because editing `check_skill_contracts.py` re-partitioned nose's GLOBAL clone grouping: the pre-existing structural validators (`validate_core_contract`/`validate_package_contract`/`validate_forbidden_snippets`, lines 233–258) got 2 new content-hash family ids. The delta was COUNT-NEUTRAL (526→526; 2 ids added, 2 removed) — zero new duplication, just a re-hash from the line shift. Resolved by `check_dup_ratchet.py --write-baseline` (reviewed batch accept; delta 4 « threshold, no `--confirm-baseline-delta`). IMPORTANT for the sweep: every `check_skill_contracts.py` pin edit will trip this and need the same count-neutral re-baseline — anticipate it (or extract the 3 near-identical validators to stabilize the file, a separate cleanup).

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage-adjacent (one bounded reviewer; first pin DELETION — higher stakes than unpinned-dup passes because it licenses a harness-wide sweep).
- Requested spawn fields: model=default (Claude Code host resolution; single bounded reviewer).
- Host exposure state: requested_fields_sent
- Application state: 1 bounded reviewer spawned via the Agent tool in the shared parent worktree, read-only (`git show HEAD:<path>` for prior versions, no index/worktree-mutating git ops); the host does not echo resolved spawn fields, so application is unverified-by-carrier (not claimed host-confirmed).

## Fresh-Eye Satisfaction

parent-delegated. The bounded reviewer returned `DISCIPLINED-PIN-DELETION` after
a clause-level diff proving criterion (a), a repo-wide orphan grep, a
surviving-pin + cautilus-guard integrity check, mirror byte-equality, and dogfood
honesty verification. Deterministic backstop: `check_skill_contracts` green (13
core / 8 package, quality now 5 CORE pins); `validate_skills` 24 packages;
`test_quality_skill_docs` 22 passed; verification-lock closeout exit 0 (packaging,
doc-links, markdown, secrets, cautilus-proof, skills, ergonomics, public-skill
validation + dogfood, integrations, broad standing pytest, gitignore-scan-hygiene,
agent-browser orphan guard all PASS); cautilus planner `next_action: none`
(Cautilus correctly NOT run; scenario review recorded in the dogfood ledger).

## Deliberately Not Doing

- **Update the frozen pin-count spec snapshot (F1).** It is a dated measurement
  record consumed by no gate; rewriting it would falsify history. Left as-is.
- **Trim the 49-ref list this pass (F2).** Validator-locked to the directory;
  reduction is a file-deletion audit, and relocation-to-`index.md` is the
  not-the-point move the operator rejected. Deferred.
- **Run the harness-wide pin sweep now (F3).** The pilot licenses it; the sweep
  is a deliberate next step under the now-proven discipline, not a bundled
  follow-on.
- **Run Cautilus.** Planner `next_action: none`; no behavior/routing change.
  Ask-before-run honored.
