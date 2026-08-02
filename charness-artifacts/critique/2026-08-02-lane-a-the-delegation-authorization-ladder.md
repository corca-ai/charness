# Lane A the delegation authorization ladder
Date: 2026-08-02

## Decision Under Review

Issue #475: bounded fresh-eye review is MANDATED by several skills and was INERT
in any repo that never ran `setup`, because the authorization rule named exactly
one source of the standing delegation request (`<repo-root>/AGENTS.md`). The
repair is the operator-chosen three-rung ladder — `AGENTS.md`, else a structured
`.agents/subagent-delegation.json` record, else ask the user once and persist —
with no silent self-grant, propagated to the surfaces a consuming repo reads.

## Failure Angles

- **Verdict-logic fail-open.** The resolver decides whether an agent may spend
  tokens spawning agents. Any malformed, hostile, or partial record that reads
  as `granted` lets the plugin authorize its own spawns in every repo that
  installs it.
- **Propagation across seams (#458's shape).** A fix that lands only in the
  authoring repo's prose while the shipped code that ACTS on the doctrine keeps
  reading one source.
- **Does the fix reproduce the class it fixes?** A repair that itself cannot
  fire where it was written is this goal's own thesis pointed at the repair.
- **Blast radius of widened verdict surfaces.** Two adoption detectors and two
  blocked-signal floors changed what they accept or refuse.

## Counterweight Pass

- Round 1 (two lenses: verdict logic, propagation) and round 2 (two lenses:
  does-the-fix-reproduce-its-class, blast radius) all delivered findings.
  Round 2 was owed because this slice changes verdict logic on proof surfaces.
- **Round 2 confirmed the class reproduced itself**, twice: the `delegation
  signal` widening added in round 1 could not fire on the one-line record the
  contract prescribes (the floor matched the heading only at line start), and
  `blocked_kind` was computed while the operator-facing advisory still called a
  user's decline a host incapacity. Both are repaired.
- Over-worry raised and NOT folded: a scope-aware rung 1. Rung 1 reads prose, so
  a repo that hand-narrowed its `AGENTS.md` block cannot be detected; the
  resolver now states that limitation in its payload rather than pretending to
  enforce it. Building a prose scope parser would re-create the fragility rung 2
  exists to remove.
- Over-worry raised and NOT folded: proving human authorship of a rung-2 grant.
  No file-based mechanism can. The repair buys auditability instead — provenance
  echoed at the point of use, `--note` required for a grant, a warning when a
  grant carries none — and the contract says plainly that the record is
  testimony, not proof.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/shared/scripts/resolve_subagent_delegation.py | action: fix | note: rung 1 silently overrode a recorded decline, a state `setup` itself manufactures by writing the block; now a conflict resolving to ask
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/validate_critique_artifacts.py | action: fix | note: the prescribed decline record was refused by its own floor and laundered as a host incapacity by the issue observer; delegation signal heading plus blocked_kind
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/validate_critique_artifacts.py | action: fix | note: round 2 found the delegation signal widening could not fire on the prescribed one-line record because the floor matched the heading only at line start
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_critique_observer.py | action: fix | note: two shipped adoption detectors read only AGENTS.md, going inert in the exact repo class the ladder serves, and ignored the conflict and narrowed-scope states
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_resolution_critique.py | action: fix | note: blocked_kind had zero production consumers so the operator advisory still said confirm the host genuinely could not spawn for a user decline
- F6 | bin: act-before-ship | evidence: moderate | ref: skills/shared/scripts/subagent_delegation_record.py | action: fix | note: an empty or malformed scopes key widened the grant to all five scopes exactly when the author had tried to narrow it
- F7 | bin: act-before-ship | evidence: moderate | ref: skills/public/setup/SKILL.md | action: fix | note: the ladder command used $SKILL_DIR above the line that resolves it, so the first command a fresh repo runs would expand to an empty path
- F8 | bin: valid-but-defer | evidence: moderate | ref: scripts/templates/agents_subagent_delegation.txt | action: file-issue | note: the shipped compact template does not contain the second delegation marker, so a setup-created repo may read as never adopted - a pre-existing instance of this same class, verified by measurement and filed | follow-up: https://github.com/corca-ai/charness/issues/476
- F9 | bin: over-worry | evidence: weak | ref: skills/shared/scripts/resolve_subagent_delegation.py | action: defer | note: rung 1 cannot enforce a hand-narrowed scope list because it reads prose; the limitation is stated in the payload rather than parsed
- F10 | bin: over-worry | evidence: contested | ref: skills/shared/scripts/subagent_delegation_record.py | action: document | note: a rung-2 record cannot prove human authorship; auditability and a required note replace a proof that no file-based mechanism can give

## Reviewer Tier Evidence

- Requested tier: high-leverage (proof-surface authoring; verdict logic about whether spawning is authorized).
- Requested spawn fields: typed `bounded-reviewer`, session-model inheritance (per-host contract; the Codex model/effort request does not apply on a Claude Code host).
- Host exposure state: host-defaulted
- Application state: n/a — this host exposes no per-subagent model/effort confirmation signal.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — four bounded reviewers across two rounds, all findings received in the parent context. Round 1 (window `lane-a-round-1`): verdict-logic lens and propagation lens. Round 2 (window `lane-a-round-2`, reading the repaired surface): does-the-fix-reproduce-its-class lens and blast-radius lens. Both rounds' `reviewer_boundary_fingerprint.py verify` returned exit 0 with `{"ok": true, "verdict": "clean", "drift": []}` and nothing parent-declared.

Fresh-eye pass: skills/shared/scripts/resolve_subagent_delegation.py — round 1 found a silent decline override, fail-open scope widening, no repo-root validation, a silent clobber and a TOCTOU double parse; round 2 found the rung-1 provenance leak and the scope check's inertness at rung 1. All repaired or stated as a limitation.
Fresh-eye pass: skills/shared/scripts/subagent_delegation_record.py — round 2 found scope comparison was case-sensitive so a record written `["Critique"]` would silently downgrade a real grant; repaired.
Fresh-eye pass: scripts/validate_critique_artifacts.py — round 2 found the `delegation signal` widening could not fire on the prescribed one-line record, and that the refusal message still instructed the false `host signal:` line; both repaired.
Fresh-eye pass: skills/public/issue/scripts/issue_critique_observer.py — round 2 found the decline regex false-fired on genuine host signals ("delegation declined by the workspace policy") and that the reader ignored the conflict and narrowed-scope states; both repaired.
Fresh-eye pass: skills/public/issue/scripts/issue_resolution_critique.py — round 2 found `blocked_kind` had zero production consumers; wired into the operator-facing advisory.
Fresh-eye pass: tests/quality_gates/test_subagent_delegation_ladder.py — round 2 found a tautological assertion, a fixture that spelled the decline record the way the matcher wanted rather than the way the contract prescribes, and a parity fixture set that omitted exactly the states the ladder invented; all repaired.

Round-2 repairs are recorded as accepted-unreviewed per the two-round cap.

## Reviewed Input Identity

<!-- No prepare packet was consumed; reviewers received inline bounded packets naming intent, changed files, invariants, non-claims, and out-of-scope lines. -->

## Boundary Ownership

- Producer: the repo owner, who grants the standing bounded-review delegation request.
- Consumer: every skill that mandates a bounded fresh-eye review and must decide whether it may spawn.
- Owning surface: skills/shared/references/fresh-eye-subagent-review.md, with the deterministic half in skills/shared/scripts/.
- Verdict: owned-correctly
