# Critique Review
Date: 2026-07-25

## Decision Under Review

Remove stale proof and duplicated prose, on the operator's "less but better"
direction. Five surfaces, net deletions:

1. `docs/conventions/implementation-discipline.md` — the dup-ratchet batching rule
   asserted a `family_id` rotation that D30's 2026-06-27 resolution eliminated,
   cited D30 as still deferred, and recommended `--write-baseline`, the command
   the owning script tells you to avoid.
2. `docs/conventions/operating-contract.md` — "The only checked-in workflow is
   `scheduled-deeper-check`" became false on 2026-06-10 when `quality-core.yml`
   landed, and the bullet told reviewers to dismiss a finding using that fact.
3. `skills/public/quality/references/automation-promotion.md` — pinned a
   "≤200-line core budget (the `check-skill-core-headroom` ratchet)", conflating
   a 200-line total cap with the 160-line core ratchet, and prescribed the
   overflow-displacement P2 forbids. Ships to consumer repos.
4. `scripts/check_python_lengths.py` — the advisory band said "trim before it
   reaches the hard limit" while the same script's hard-limit branch already says
   separate a concept or delete.
5. `skills/public/create-skill/SKILL.md` — nine `## Rules` bullets restated
   references the body never triggered; each owning reference is now cited at the
   Workflow step where it applies. The P2-teaching surface had zero addable core
   headroom (156/160 against a 4-line buffer); it is now 152/160.

## Failure Angles

- Michael Jackson (problem framing): is each "stale" claim actually stale, or is
  the replacement the thing that is wrong?
- Barbara Minto (structure/communication): does a deleted bullet's prescription
  survive at the point of use, or only in a reference nobody is routed to?
- Jef Raskin (humane interface): does a reader hit each rule at the moment the
  decision is in front of them?

## Counterweight Pass

- **Act Before Ship:** two of the nine relocated prescriptions landed in a
  citation list attached to an unrelated step-6 bullet rather than at their real
  decision point — expert-reference hygiene belongs on the named-anchor bullet,
  and WebSearch belongs at step 2's dependency intake, since research does not
  happen while writing helper scripts. That is the "displaced overflow goes
  unread" failure P2 names, committed while removing a different instance of it.
  Both re-sited. The pinned helper-script sentence was also appended after a
  near-identical sentence — duplicated prose added by a de-duplication slice; it
  is now the rule's own blockquote statement, with a provenance comment at the pin.
- **Bundle Anyway:** the "multi-skill propagation rule" pointer sent readers to
  "Named Anchor Rule", which only covers propagating *anchors*; pattern
  propagation lives in the uncited "Cross-Skill Propagation Rule".
  `references/adapter-pattern.md` is an eval-required fragment with no body
  trigger, one parenthetical away from the lines this slice already edited. The
  `create-skill-claim-fidelity` eval rationale still described a Rules section
  that no longer exists in that shape (eval passed; the reviewed prose was stale).
- **Over-Worry:** "this is the fewer-lines failure signature." Rejected on the
  reviewer's accounting: two bullets moved verbatim into the workflow, four were
  superseded by references that carry *more* prescription at the decision point
  than the stub did, one had to go because it told authors to commit the P2
  violation a bullet ten lines below forbids, and two were genuinely damaged and
  have been fixed. The metric held was reachability at point of use, not count.
- **Valid but Defer:** the `retro` weekly-concept duplication (a second concept
  woven through six sections of a 155/160 body, already owned by `mode-guide.md`
  and `weekly-trends.md`) needs planner routing changes and touches two
  `PACKAGE_CONTRACTS` pins — deliberately not rushed at the end of this session.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/create-skill/SKILL.md:117 | action: fix | note: "Expert Reference Hygiene" and "WebSearch Rule" were parked in a step-6 citation list about helper scripts, unreachable from the step where each applies; re-sited to the named-anchor bullet and step 2
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/create-skill/references/portable-authoring.md:282 | action: fix | note: the pinned sentence was grafted after a near-identical sentence — a de-duplication slice adding duplicated prose; merged into the rule as its blockquote statement
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_skill_contracts.py:180 | action: fix | note: the pin had no provenance comment, so the next editor hunting duplicated prose would delete the 22 pinned words and hit an unexplained gate failure; comment added naming its home
- F4 | bin: bundle-anyway | evidence: strong | ref: skills/public/create-skill/SKILL.md:141 | action: fix | note: the multi-skill-propagation pointer named "Named Anchor Rule", which covers anchor propagation only; pattern propagation is the separate "Cross-Skill Propagation Rule", previously cited nowhere in the body
- F5 | bin: bundle-anyway | evidence: strong | ref: evals/cautilus/create-skill-claim-fidelity/spec.json:57 | action: fix | note: the reviewed rationale asserted "Rules section cites three named rules"; after the slice it cites two, with six more moved to their steps — eval passed, reviewed prose was stale
- F6 | bin: bundle-anyway | evidence: moderate | ref: skills/public/create-skill/SKILL.md:81 | action: fix | note: `adapter-pattern.md` is a `requiredCommandFragments` entry with no body trigger; the slice edited the two adjacent lines, so adding the parenthetical was one line away
- F7 | bin: bundle-anyway | evidence: moderate | ref: skills/public/quality/references/automation-promotion.md:151 | action: fix | note: a shipped reference cited a script by bare filename with no consumer-reachable path, unlike its two marked siblings
- F8 | bin: over-worry | evidence: contested | ref: docs/design-north-star.md:97-99 | action: defer | note: "fewer lines cited as success" — the deletions were judged on reachability at point of use; four replaced stubs with richer reference content, and the two that genuinely got worse were fixed rather than reverted
- F9 | bin: valid-but-defer | evidence: strong | ref: skills/public/retro/SKILL.md | action: defer | note: the `weekly` second concept woven through six sections needs `plan_retro_run.py` routing plus two package-contract pins; deferred rather than rushed, recorded in the handoff as the next slice
- F10 | bin: valid-but-defer | evidence: moderate | ref: skills/public/create-skill/SKILL.md:143 | action: document | note: the retained progressive-disclosure bullet meets this slice's own deletion criterion but shapes every edit rather than a conditional one; kept deliberately, recorded here so the criterion is not applied mechanically next time
- F11 | bin: valid-but-defer | evidence: moderate | ref: skills/public/create-skill/references/portable-authoring.md:198 | action: defer | note: the reference says "verify fuzzy or non-obvious paraphrases" where the deleted bullet said "claims"; a fabricated attribution that paraphrases nothing sits outside the narrower wording

## Reviewer Tier Evidence

- Requested tier: high-leverage (deletion-safety review).
- Requested spawn fields: session-model inheritance (Claude Code host; the repo's
  Codex-only model/effort override does not apply on this host).
- Host exposure state: host-defaulted
- Application state: host-confirmed — one `bounded-reviewer` subagent spawned via
  the Agent tool with a Read/Grep/Glob-only envelope. It reported the envelope
  bound and named one evidence gap it could not close (the base blob of the
  edited `SKILL.md`), reconstructing from an older `mutants/` snapshot instead and
  scoping its conclusions accordingly; its trigger-placement and reference-coverage
  findings did not depend on the base. Parent-side worktree+index integrity was
  fingerprinted around the review; verify returned `{"ok": true, "drift": []}`.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

n/a (no adapter `packet_sections` declared; the reviewer was pointed at the live
working tree and the base ref `2116904c`).

## Boundary Ownership

- Producer: `create-skill` owns its SKILL.md and `portable-authoring.md`;
  `quality` owns `automation-promotion.md`; the two `docs/conventions/` files are
  repo-internal contracts; `check_python_lengths.py` is a repo gate with a mirror.
- Consumer: consumer repos read `automation-promotion.md` and the `create-skill`
  package; this repo reads the conventions docs.
- Verdict: owned-correctly

## Non-Claims

- Deletion safety was verified by reading, not by running a consumer repo: no
  consumer-repo install was exercised against the edited `create-skill` package.
- The `create-skill-claim-fidelity` eval's `requiredCommandFragments` still pass,
  but no Cautilus evaluation was run this slice (ask-before-run); the rationale
  edit is prose alignment, not new evaluator evidence.
- The reviewer could not read the base blob of the edited `SKILL.md`; its
  per-bullet "what the deleted text said" reconstruction came from an older
  `mutants/` snapshot, so the word-for-word deletion diff is unverified by the
  distinct observer even though trigger placement and reference coverage are.
