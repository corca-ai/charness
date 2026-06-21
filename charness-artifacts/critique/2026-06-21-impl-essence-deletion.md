# Impl essence/deletion redesign — critique

Date: 2026-06-21

## Decision Under Review

Redesign `skills/public/impl/SKILL.md` for essence rather than relocation: delete
unpinned duplication (not move it to a reference) and apply `achieve`'s
name-the-rule-don't-restate guardrail pattern. Guardrails 9 bullets → 2; Workflow
step 4 13 sub-bullets → 4 by deferring to `references/verification-ladder.md`;
worktree-doctor bullet consolidated with `## Worktree Readiness`; prose merges
(194 → 187 lines). This is the worked exemplar for the operator's
"less but better / progressive disclosure / delete what should be deleted" steer;
`debug` and `quality` follow the same discipline next.

## Failure Angles

- **Orphaned rule (lossiness):** a deleted guardrail or step-4 bullet carries a
  load-bearing rule that now has zero home — not in a Workflow step, the
  meta-guardrail's named list, `verification-ladder.md`, or `CLAUDE.md`.
- **Hand-waved deferral:** step 4 "defers" browser/lint/external-API rules to
  `verification-ladder.md`, but the reference does not actually own them, so the
  deferral hides a deletion.
- **Gamed pins / silent contract downgrade:** a gate-pinned phrase is kept only
  as grep-bait in a meaningless spot, or the meta-guardrail silently drops a rule
  while looking like a faithful fold.
- **Less but worse:** a merge produces a denser, harder-to-read bullet — fewer
  lines that degrade the skill rather than clarify it.

## Counterweight Pass

Two bounded fresh-eye reviewers (read-only, shared parent worktree, `git show`
for prior versions) split the angles: an orphan-hunter tasked to REFUTE
"nothing load-bearing was lost," and a contract-honesty + faithfulness reviewer.
Both read `verification-ladder.md` and the prior committed `impl/SKILL.md`
directly. Verdicts: `ESSENCE-PRESERVED` and `CONTRACT-HONEST-AND-FAITHFUL`.
The deferrals were verified real (browser output, lint-gate, external-API, and
completion-report categories genuinely live in `verification-ladder.md`); all 9
old guardrails were traced to a named home; every gate-pin reads naturally at a
sensible section; the meta-guardrail faithfully mirrors `achieve`'s pattern and
the merges were judged "shorter AND clearer." No Act-Before-Ship surfaced.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: over-worry | evidence: moderate | ref: skills/public/impl/SKILL.md:118 | action: document | note: deleted the standalone `disabled`-run-mode cautilus bullet; both reviewers flagged it as the weakest-preserved deletion but NOT an orphan — its three fragments are homed (adapter-decides-proof-policy + keep-deterministic-validation-local + the kept "say explicitly that it did not run"), and its canonical authority is `quality/references/cautilus-on-demand.md` (the CLAUDE.md disabled-surface contract). Restoring it would re-add the duplication this change deletes. Recorded in Deliberately Not Doing.
- F2 | bin: valid-but-defer | evidence: strong | ref: skills/public/debug/SKILL.md | action: defer | note: the same essence/deletion recipe applies to `debug` (the thrice-printed `issue resolve invokes the same substrate` cross-reference; helper-duplicating Bootstrap prose) and `quality` (191-line body but 49 references — the anchor-split relocated instead of deleting). Deferred to the next session per the handoff exemplar-rollout note; out of scope for this single-skill exemplar.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage (two bounded reviewers, distinct angles).
- Requested spawn fields: model=opus (Claude Code host resolution of high-leverage; Codex-host mapping is model=gpt-5.5, reasoning_effort=medium, service_tier=priority).
- Host exposure state: requested_fields_sent
- Application state: 2 bounded reviewers spawned via the Agent tool in the shared parent worktree, read-only (`git show HEAD:<path>` for prior versions, no index/worktree-mutating git ops); the host does not echo resolved spawn fields, so application is unverified-by-carrier (not claimed host-confirmed).

## Fresh-Eye Satisfaction

parent-delegated. Reviewer 1 (orphan-hunter, REFUTE-lossless) returned
`ESSENCE-PRESERVED` with a per-deletion ledger mapping all 10 old guardrail
clauses + every step-4 deferral to a concrete home, after reading
`verification-ladder.md` end-to-end. Reviewer 2 (contract-honesty +
faithfulness) returned `CONTRACT-HONEST-AND-FAITHFUL`, verifying each
CORE/PACKAGE/test pin is present and meaningful (not grep-bait), that the
meta-guardrail faithfully applies `achieve`'s pattern, and that no merge produced
a readability regression. Deterministic backstop: `tests/quality_gates/` 2283
passed, `check_skill_contracts` (13 core / 8 package), `validate_skills`, skill
ergonomics, markdown, and doc links all green; zero edits to gate scripts or
tests.

## Deliberately Not Doing

- **Restore the `disabled`-run-mode cautilus bullet (F1).** Its substance is
  homed across the new step-4 cautilus bullets plus the kept "say explicitly that
  it did not run," and its canonical owner is `cautilus-on-demand.md`. Re-adding
  the inline prose would reinstate exactly the duplication this exemplar exists to
  remove. Left deleted; flagged here for maintainer eyeball.
- **Roll the recipe into `debug`/`quality` this session (F2).** The operator
  scoped this as a single worked exemplar (`impl` first, others follow). Doing
  the rollout now would skip the per-skill clean-split verification each target
  needs. Deferred to the next session via the handoff.
