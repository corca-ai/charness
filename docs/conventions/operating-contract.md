# Operating Contract

This document owns Charness repo conventions that do not need to be repeated in
the root instruction file. [AGENTS.md](../../AGENTS.md) stays as the session
entry and link index.

## Guiding Principles

These expand in [README.md Core Concepts](../../README.md#core-concepts):

1. Less Is More: strong defaults over menus; progressive disclosure.
2. Agents Are First-Class Users: CLIs, scripts, artifacts, docs are agent-facing.
3. Reveal Intent, Hide Detail: public surface names intent; tool detail sits underneath.
4. Human-Code-AI Symbiosis: humans judge, code verifies, AI drafts.
5. Long-Running Agents Need Quality Software: quality as trust surface.
6. Tacit Knowledge Becomes Workflow: expert moves become reusable skills.
7. The System Should Get Smarter With Use: retros and adapters learn.
8. Context Must Keep Flowing: handoff, review, release, and narrative are core work.

## Commit Discipline

- After each meaningful unit of work, create a git commit before moving on.
- Do not leave task-completing repo work in a dirty tree unless the user
  explicitly asked to pause before commit or an unresolved blocker is named.
- Prefer commit subjects that state user-facing purpose, not only mechanism.
- After any `git push`, confirm the branch is clean and the remote update succeeded.
- When a Charness workflow creates or updates durable artifacts under
  [charness-artifacts/](../../charness-artifacts/), include meaningful artifact
  changes in the same commit as the work they support.
- Cite proof from checked-in durable evidence in spec, quality, release,
  dogfood, debug, premortem, and design-study artifacts. Paths matching
  [.gitignore](../../.gitignore) are reproduction sources only and must
  carry a citation-bullet-scoped `<!-- reproduction-source -->` marker; otherwise check in a
  selected proof artifact with the cited fields. See
  [skills/public/spec/references/evidence-durability.md](../../skills/public/spec/references/evidence-durability.md).

## Pointer-Write Discipline

- Skill `latest.*` artifacts are read-mostly current pointers. When a skill
  refreshes the pointer to a new canonical record, never overwrite or unlink
  the prior canonical record by writing through a stale symlink target. The
  trap (issue #138, gather): `latest.md -> 2026-01-01.md` symlink combined
  with a writer that opens `latest.md` for writing rewrites the prior dated
  record in place. The fix shape is `lstat` the pointer first, write a fresh
  canonical record under its dated filename, then atomically swap the pointer
  via `unlink + symlink_to` (acceptable small-window race for read-mostly
  pointers).
- The reference implementation lives in
  [skills/public/gather/scripts/write_record.py](../../skills/public/gather/scripts/write_record.py)
  and [`gather_writer_lib`](../../skills/public/gather/scripts/gather_writer_lib.py).
  Other skills that publish a `latest.*` rolling pointer
  (quality/release/cautilus/debug/hitl/narrative/retro/critique)
  inherit the same hazard and should reuse this writer once promoted to a
  shared helper, not reimplement open-and-overwrite.

## Critique Discipline

- Every task-completing repo change runs critique before closeout. Scale the
  pass, not the obligation; the review unit is the risk boundary or meaningful
  slice, not every commit.
- Small local-risk slices may use a short scoped critique artifact that names
  the decision, the likely misread, counterweight triage, and the next move.
- Non-trivial design, deletion, rename, release, workflow, compatibility,
  install/update, host-proof, prompt-surface, public-skill, validator, or export
  decisions use the standalone `critique` skill once per substantial slice or
  bundle, and rerun it only when later edits introduce a new risk boundary.
- Slice fresh-eye review consumes a bounded packet: intent, changed files and
  owning/generated surfaces, expected invariants, tests/proof, non-claims,
  out-of-scope lines, and reviewer questions. **The packet's NON-CLAIMS are
  claims** and need the same premise check as a plan's remedies: on 2026-08-02 a
  packet asserted "no skill files, so no `plugins/` mirror is involved" when the
  whole `scripts/` tree is mirrored, and that unchecked sentence was the round's
  only blocker — the export would have shipped the un-repaired gate plus a
  `ModuleNotFoundError`.
- **Task-completing work runs a CLOSEOUT-CLAIMS review by a distinct observer
  before the completion flip** — a bounded reviewer whose subject is what the
  ARTIFACT ASSERTS, not whether the code is correct. Give it the acceptance bar
  and ask it to re-derive each figure, check each disposition reason against the
  text it cites, and name anything claimed as proven that was only reasoned
  about. It is a different question from the code rounds, so it is not satisfied
  by running more of them.
  - **Measured 2026-08-02, and this is why it is standing rather than
    advisory.** Three code-reading rounds passed over: a verification step the
    plan required (an adversarial pass over every disposition) that had never
    run and would have shipped recorded as satisfied; a Slice Log that
    contradicted its own retro in the flattering direction; an unreconciled
    headline count (13 vs 14) that WAS the acceptance bar; and a disposition
    whose stated reason was false at every site it cited. The claims round found
    all four in one pass, and its own single reading refuted a disposition the
    code rounds had approved.
  - The failure mode it catches is structural, not sloppiness: a code reviewer
    is asked "is this right?", so it reads the diff. Nobody reading the diff is
    asked "does the artifact's own summary survive contact with it?" — and the
    author, who wrote both, is the last one who can tell.
  - Scale it to the work: one bounded reviewer, given the acceptance criteria
    and the closeout sections. When the host blocks subagent spawning, record
    the concrete signal and leave the review unproven — never substitute a
    same-agent reread, which is precisely the observer this floor exists to
    exclude.
  - **Surfaces: goal closeout AND release closeout** (2026-08-02). A release
    publishes a record — notes, a version claim, an announcement — to readers
    outside the session, with less context and the least chance of correction
    after the fact. `release`'s own
    [critique-boundary](../../skills/public/release/references/critique-boundary.md)
    *Claims Review* owns the release form. Not per-commit: the unit is a
    closeout RECORD, not a diff, and firing it per-diff is how a floor becomes
    ceremony.
- **Run the reviewer boundary command**
  `reviewer_boundary_fingerprint.py verify --before <snapshot-path> --window-id <id>`
  the moment the reviewer returns, BEFORE any parent write.
  A verify run after the parent has
  started folding findings reports `boundary-drift` and can only be resolved by
  declaring the parent's own paths — which downgrades the attestation from "the
  tree did not move" to "the parent says it moved these files". Measured
  2026-08-02: two of three windows were verified late and both needed
  `--parent-path` declarations. The tool cannot detect this; only the ordering
  prevents it.
- **A slice that changes VERDICT LOGIC on a proof surface runs a SECOND bounded
  review reading the repaired surface** — notwithstanding the once-per-slice
  clause above, which this class overrides on the REVIEW count only: the repairs
  are exactly the "later edits" that clause would otherwise wave through. It is
  still ONE critique artifact per slice, recording both rounds (the worked
  example is
  [this critique](../../charness-artifacts/critique/2026-07-28-four-unestablished-scope-readers-in-the-quality-dup-nose-subsystem.md),
  whose Fresh-Eye Satisfaction names five reviewers across two rounds). One round
  is not enough here and the repo has the count to say so: every measured slice
  shipped a fix carrying the class it fixed, and on 2026-07-28 round 1 found six
  such instances inside the fix while round 2, reading the repaired state, found
  four more — two of them blockers that one round would have shipped.
  - **Trigger is verdict logic, not the file.** A proof surface is a gate,
    validator, or any code rendering a verdict about other code or artifacts,
    but ~60-163 such files are touched per week against a population of ~135
    (measured in [new_proof_surface_advisory.py](../../scripts/new_proof_surface_advisory.py)),
    so a touched-the-file trigger is unaffordable and would be ignored. Changing
    what a surface decides, or when it refuses, fires the rule; a rename,
    comment, docstring, or import-only edit does not.
  - **Two cases that look out of scope and are not**, because both are recorded
    escapes: (1) **weakening a test assertion** that pins a verdict — a loosened
    or flipped assertion stops discriminating, which is the same class in test
    form, so it fires (merely ADDING a case does not); (2) **changing a status,
    reason, or value that another surface keys on** — the producer still decides
    the same thing, and the escape lives in an untouched reader, so round 2's
    packet is the subsystem's READERS of that value, not the edited file.
  - **Relationship to the birth advisory.** That advisory argues an
    edit-triggered check over proof-surface FILES is useless, and it is right:
    the risk is at a verdict's birth. This rule does not contradict it — new
    verdict logic inside an existing file, and the repairs themselves, ARE
    births. The advisory owns newly added surface FILES and its
    `Fresh-eye pass: <path>` marker; that marker is matched only against
    newly-added paths, so for a changed existing surface nothing mechanically
    records this rule and the critique artifact is the record.
  - **Round 2 reads the repaired surface, not the repair hunks**, and asks the
    same question of it: does this fix reproduce the class it fixes? A hunk-only
    packet cannot see a guard that is dead, negative, or bypassed elsewhere.
  - **A first round that produced no repairs discharges the obligation** — record
    that it found nothing rather than spawning a second reviewer over an
    unchanged tree. Scale the pass, not the obligation.
  - **The cap is two rounds, and round-2 repairs ship unreviewed by that same
    argument.** This is a deliberate stopping rule, not an oversight: iterating
    until a round comes back clean is unaffordable, and the marginal round is
    worth less each time (round 1 found six, round 2 four). Record round-2
    repairs as accepted-unreviewed in the critique artifact so the residual is
    visible instead of implied; escalate to a third round only when a round-2
    finding was itself a blocker in verdict logic.
  - Both rounds run BEFORE the locked `--produce-mutation-coverage` producer run
    (see [implementation-discipline.md](./implementation-discipline.md)); a
    round-2 repair after the producer invalidates the coverage fingerprint.
  - A docs, artifact, or ordinary-code slice keeps the single-round obligation
    above.
- **A multi-slice goal runs a bounded GOAL-CLAIMS review at its midpoint, not only
  at closeout.** The slice rule above puts a fresh eye on every repair; nothing
  put one on the goal's own claims until the end, and a goal artifact is a verdict
  surface too — it asserts what each row now is, and downstream sessions plan
  against those assertions rather than against the code.
  - **Trigger:** a goal with three or more slices. Two-slice goals keep the
    closeout review alone; the midpoint round is not worth its cost there.
  - **What the reviewer reads:** the goal artifact's per-row claims against the
    OWNING records and the commits, not the code. The question is "does the Slice
    Log claim match what the record says and what the commit did", which is a
    different question from "is this repair correct" and is answered by a
    different packet.
  - **Why the midpoint and not only closeout.** Measured on the 2026-08-01
    stragglers goal: the closeout review found two blockers — an acceptance
    criterion (one critique artifact per slice) that had gone unmet for all five
    slices, and a row marked `FIXED` whose own record's prose still said the
    opposite. Both were cheap to fix at the midpoint and expensive at the end,
    because by then five slices of claims had been written against the same
    unnoticed gap. Catching a claims defect once costs one round; catching it at
    closeout costs re-writing every artifact the defect touched.
  - The closeout disposition review still runs. The midpoint round does not
    replace it, and a goal that stops early runs only the closeout one.
- **Claim fidelity: the assertion is a surface too.** Measured on the 2026-08-01
  three-unarmed-refusals goal: THREE of five bounded rounds found a defect in
  something the author asserted rather than in code — a comment claiming a branch
  was live beside a probe recording zero, a units swap that made two different
  numbers read as agreement, and a "repair" that never applied. That class is the
  residue left once the shallower defects are gone, and it is cheap to refuse
  mechanically. Three checks, none of which needs a reviewer:
  - After a non-interactive string edit (a scripted replace, a sed), assert the
    SUPERSEDED text is absent. A replace that does not match fails SILENTLY, so
    "I fixed it" and "the wrong text still ships" are indistinguishable without
    the check. This is how a corrected number stayed in the gate comment that
    exists to defend the threshold.
  - When a number replaces a number in a durable record, grep the repo for the
    OLD value before closing. Superseded figures linger in sibling docstrings,
    generated mirrors, and dogfood records that no reader will cross-check.
  - State the UNIT before the value when comparing measurements. `5 reviews` and
    `5 citations across 4 artifacts` are not the same claim, and a measurement
    that lands near an expected number invites narrating agreement that the units
    do not support.
- `Critique: not-applicable <reason>` is reserved for inspect-only, status-only,
  or routing-only requests that do not complete repo work.
- If the required bounded-review path is blocked by the host, stop and record
  `Critique: blocked <host-signal>` instead of substituting same-agent review.

## Regenerable-Fact Discipline

**A number in forward-looking prose is banned by default. Carry the command, not
its output.** A transcribed version, sha, or count is true on the day it is
written and misleading every day after, and the next reader acts on it instead of
checking. This is a stance, not a style note: it had teeth on one file and now covers every
surface this repo's quality adapter names under `regenerable_facts.surfaces` —
the agent prompt files, the repo README, the docs tree, and shipped skill prose.
Widening that list is an adapter edit, and a surface absent from it is NOT
covered: the gate reports what it scanned so the scope is legible rather than
assumed.

The seam that decides whether a surface is in scope:

- **Dated, append-only RECORDS** — retros, critiques, audits, goal slice logs,
  commit messages. A number there describes one moment that will never be true
  again, and that is exactly what it is for. Permanently OUT OF SCOPE, by nature
  rather than by grandfather.
- **Rolling, FORWARD-LOOKING surfaces** — agent prompt files, conventions, docs,
  skill prose. A reader treats these as today's answer. IN SCOPE.

Two ways to satisfy it, and the difference is what the command COSTS:

- A **cheap** command (`git describe`, `gh issue list`, a grep): carry the command
  alone. The reader runs it and gets today's answer for nothing.
- An **expensive** command (a multi-minute suite, a fan-out census, a full-corpus
  sweep): carry the command AND link the checked-in artifact holding its output.
  Telling a reader to re-run an expensive gate to learn one number is not a fix —
  it moves the cost onto every future reader, forever. The artifact is the
  provenance: it records what was run, when, and against what, so the prose links
  it rather than copying numbers out of it. **An expensive measurement that exists
  only in a chat reply has not been recorded.**

Three narrow exceptions, and each owes a stated reason in the adapter rather than
a silent pass: historical context (the figures a decision was TAKEN on, which
rewriting to today's numbers would falsify), a pinned tool version a documented
behaviour was observed against, and provenance for a past decision such as the
commit that moved a gate between timing layers.

Enforced by [check_regenerable_facts.py](../../skills/public/quality/scripts/check_regenerable_facts.py), which
ships to consuming repos through `quality`. Surfaces and exemptions come from each
repo's own quality adapter under `regenerable_facts`, so nothing here is bound to
this tree's layout — and an exemption with no recorded reason is REFUSED, because
an unexplained escape hatch is the same unfalsifiable claim the rule removes.

## Skill And Metadata Discipline

- Treat `skills/public/<skill-id>/SKILL.md` as the trigger contract and
  decision skeleton; keep long rationale, examples, schemas, and edge cases in
  `references/`.
- Sparse real-person anchors in `SKILL.md` core are intentional retrieval aids
  when they improve reasoning; keep them factual, behavior-linked, and
  supported by `references/`.
- Keep frontmatter YAML-safe. Quote descriptions when punctuation would make
  plain scalars fragile.

## Dogfood Discipline

- Loaded skills may come from a host-managed checkout or plugin cache rather
  than this working tree. For Claude managed-checkout dogfood, that path is
  usually `~/.agents/src/charness/`.
- Editing `skills/public/<id>/SKILL.md` does not reach the next Claude/Codex
  session in this repo until the relevant install or update path picks it up.
- Keep detailed dogfood procedures in [docs/development.md](../development.md),
  not in AGENTS.md.
- After a release or dogfood cycle, `charness update` with no flags restores
  the managed-checkout flow.

## Local Enforcement Policy

- `./scripts/run-quality.sh --read-only` is enforced locally via `.githooks/pre-push`. Every push runs current-pointer freshness, plugin manifest sync, and the artifact-mutation guard. The read-only gate runs in two shapes per push, selected by [`classify_push_diff_lib.py`](../../scripts/classify_push_diff_lib.py):
  - **Full gate**: every push that touches `plugins/`, `.claude-plugin/`, `.agents/plugins/`, `scripts/`, `skills/`, `tests/`, `integrations/`, `profiles/`, `presets/`, `packaging/`, `evals/`, the `charness` CLI, packaging manifest, `Makefile`, any top-level dotfile/dir, or any non-allowlisted path. The first three are the slice-7 stop-condition prefixes and are unconditional.
  - **Docs-only subset**: every push whose entire diff is on the allowlist (`docs/`, `charness-artifacts/`, plus the root README/AGENTS/CLAUDE entry-point files). Runs ~13 doc/artifact phases (check-doc-links, check-markdown, check-links-internal, check-references-link-inventory, check-spec-evidence-durability, validate-{handoff,debug,quality,retro,ideation,critique-artifacts}-artifact, inventory-quality-handoff, validate-current-pointer-freshness) in ~13s instead of ~100-120s. The `doc-duplicates` nose advisory is intentionally broad-only (its full-tree scan is too slow for the fast docs subset); pre-push doc-dup coverage is deferred to the item-5 ratchet design.
  - Operator override: `CHARNESS_FORCE_FULL_GATE=1 git push ...` forces the full gate regardless of the classifier's decision.
  - New ref creation, ref deletion, and unresolvable upstream all force the full gate (no upstream-sha to diff against).
- Two workflows are checked in, and both are intentionally exempt from CI/local gate parity by [`inventory_ci_local_gate_parity.py`](../../skills/public/quality/scripts/inventory_ci_local_gate_parity.py): [`mutation-tests.yml`](../../.github/workflows/mutation-tests.yml) marked `# charness:gate-policy scheduled-deeper-check`, and [`quality-core.yml`](../../.github/workflows/quality-core.yml) marked `local-gate-subset-mirror`. Ask the tool, not this bullet: `inventory_ci_local_gate_parity.py` reports the current parity verdict.
- PR CI runs a **subset** mirror, not the full read-only quality gate. This is the intended posture under the current single-maintainer push model: the pre-push hook owns standing enforcement, and no recurring external PR contribution path exists yet. The absence of a FULL PR-CI gate is intended, not missing.
- Reopen trigger: when external PR contribution becomes a recurring path (more than one outside contributor PR per release cycle), add a conditional PR CI workflow that mirrors `./scripts/run-quality.sh --read-only` for `pull_request.head.repo.full_name != github.repository`.

## Session Discipline

- Update [docs/handoff.md](../handoff.md) when the next session's first move changed.
- **Handoff timing is closeout-only.** Read the baton at pickup; write it at
  closeout. A pickup's durable output is the derived goal skeleton (the chunker's
  forward artifact), never a mid-session rewrite of the handoff doc — the
  session's own work moves the state again, so a pickup-time rewrite is churn. A stale
  handoff item discovered at pickup is carried in the conversation and folded
  into the single closeout write.
- **`## Next Session` is a curation/sequencing memo, not a synced task queue.**
  The issue tracker is the source of truth for what is open; the handoff chunker
  unions the live backlog at pickup (`parse_handoff_entries.py --with-issues`,
  #249). So `## Next Session` carries only the cross-issue judgment the tracker
  cannot express — coupling, sequencing rationale, the recommended first move —
  not a complete, frequently-stale list that duplicates the tracker.
- **Closeout pointer reconciliation is a contract, not reviewer-only cleanup.**
  After writing a dated quality, retro, probe, or goal-bound record, the
  closeout owner refreshes every affected current pointer and runs
  `python3 scripts/validate_current_pointer_freshness.py --repo-root .` before
  the final disposition review. A stale-pointer finding remains a closeout
  blocker until the canonical record, pointer, and handoff/goal references
  agree; the closeout evidence names this validator. The validator detects
  pointer drift but does not assert the semantic truth of the records.
- **Wire retro improvements at closeout, do not just record them.** When a
  session ran a retro, the closeout handoff write must reflect its
  `Next Improvements` in `## Next Session` (or apply the cheap ones, or file an
  issue/owner for the rest). A lesson that lives only in `recent-lessons` rots —
  this is a repeat trap caught by the user more than once. At handoff refresh,
  explicitly check the latest `charness-artifacts/retro/*` `Next Improvements`
  against the new `## Next Session`.
- If the user correctly points out a missed issue, broken assumption, or
  missing gate that should likely have been caught, run a brief retro before
  continuing and say whether that retro was persisted.
- If the operator expresses the "agent got dumber" / context-tax symptom
  mid-session, append one line to
  [symptom-ledger.md](../../charness-artifacts/reference-compaction/symptom-ledger.md)
  (a pointer, not a gate; contract in
  [context-tax-measurement-design.md](../../charness-artifacts/reference-compaction/context-tax-measurement-design.md)).
