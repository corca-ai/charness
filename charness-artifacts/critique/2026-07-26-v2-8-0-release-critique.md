# v2.8.0 release critique
Date: 2026-07-26

## Decision Under Review

Publishing v2.8.0 as a `minor` bump over four commits: documented-command
resolution in [check_doc_links.py](../../scripts/check_doc_links.py) plus the new
shared walk [markdown_doc_scan.py](../../scripts/markdown_doc_scan.py); the
optional `## Continuation Capability` handoff section; the regenerable-fact rule
in [validate_handoff_artifact.py](../../scripts/validate_handoff_artifact.py);
and the runtime-budget/speed work from the
[quality review](../quality/2026-07-25-quality-review.md).

## Failure Angles

- Is `minor` honest when two BLOCKING gates got stricter and ship to consumers?
- What existing consumer document newly fails, and is there any escape?
- Does the new portable rule contradict another portable skill's contract?
- Is a budget invented for a label with zero samples a bar or a decoration?
- Does the new shared module break a partial install at import time?

## Counterweight Pass

The reviewer built the strongest `major` case it could — both stricter gates are
commit-time-pulled, so a consumer upgrades and gets a red pre-commit on a file
they did not touch — and then argued itself down: the Major bullets are about
invocation shape (renamed skills, removed surfaces, changed CLI contracts), none
of which moved. It landed on `minor` WITH a condition rather than a bare verdict.

It also cleared three angles honestly instead of inflating them: the
`getattr(..., "OPTIONAL_SECTIONS", ())` fallback degrades correctly against an
older consumer validator (the planner's diagnosis matches the gate that would
actually fire); the plugin mirror is byte-identical for all four surfaces; and
the import-time hard failure of the new shared module is the pre-existing pattern
for `repo_file_listing` and `artifact_validator`, so the release adds no new
failure mode — only a wider blast radius for one missing file.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/references/state-selection.md | action: document | note: BLOCKER as found — `release`'s post-publish baton reconcile orders the operator to make the handoff name the just-published version, while the new `Regenerable Facts` rule calls itself "unconditional" and a commit-time gate rejects it; two portable public skills gave opposing instructions about the same lines of the same file, and this release's own closeout would have hit it. Both contracts were already satisfiable — `observed_versions` scans raw markdown so a backticked version counts as a claim, and the rule scrubs inline code — but nothing said so. The carve-out is now stated in both references and pinned by a test so closing it later cannot silently re-create the contradiction
- F2 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml | action: fix | note: `pytest-release: 125000` was 1.4x the max of the whole `run-quality-full-release` bundle that CONTAINS that gate, so no possible run could trip it — a freshly authored instance of the exact "a budget that can no longer fail" anti-pattern the same commit's comment names as the bug, and the identical value to the aggregate label betrays that it was copied rather than derived. Resized to 87000 from the only evidence that exists (the conflated window's 62483ms max at the same 1.4x)
- F3 | bin: act-before-ship | evidence: moderate | ref: .agents/quality-adapter.yaml | action: document | note: the deferral of the `pytest: 90000` retune rested on "the slack advisory will report it once the split window fills", but `BUDGET_SLACK_FACTOR` is 3.0 and 90000/41826 is 2.15 — the advisory will stay silent and the promised self-correction would never have fired. Recorded as a deliberate owed revisit instead of an automatic one
- F4 | bin: act-before-ship | evidence: moderate | ref: scripts/validate_handoff_artifact.py | action: document | note: the repo's RULE_DATE convention is "new floor gets a landing-day grandfather plus a closed legacy allowlist, never fail-open", and this floor has none; the reason is real (the handoff is a single rolling document, so there is no dated history to protect and the next rewrite IS the migration) but was unwritten, which is how a deliberate omission reads as a forgotten one
- F5 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/2026-07-26-v2.8.0-notes.md | action: document | note: `version-policy.md` requires a debatable bump to say why; two blocking gates got stricter with no grandfather, so the notes carry a stricter-gates section naming both rules, the escapes, and the third gate whose behavior moved (`check_spec_evidence_durability` now skips fully-commented single lines — verified clean across all 350 in-scope docs)
- F6 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_doc_links.py | action: defer | note: a doc documenting a cwd-relative invocation ("from the skill directory, run ...") resolves only against repo root or the skill package root, so it can fail while being correct as written; no live instance exists in this repo and the `<...>` placeholder escape covers it, so widening resolution is speculative surface until a consumer reports it
- F7 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_handoff_artifact.py | action: defer | note: the count rule cannot distinguish an as-of measurement from a forward-looking plan, so "add 4 tests to cover the fallback" is rejected as a count; narrowing needs a tense/state cue rather than another literal, and the backtick escape gives the author an immediate out
- F8 | bin: over-worry | evidence: weak | ref: scripts/markdown_doc_scan.py | action: defer | note: three blocking gates now share one hard import, but `import_repo_module` already fails identically for `repo_file_listing` and `artifact_validator` in the same files; the mirror is byte-identical and no new failure mode ships
- F9 | bin: over-worry | evidence: weak | ref: skills/public/handoff/scripts/plan_handoff_run.py | action: defer | note: the `OPTIONAL_SECTIONS` fallback was inspected against an older consumer validator and is honest — the section lands in `extra_h2_sections` exactly when the consumer's own gate would reject it

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage (irreversible publish boundary over four commits touching two portable public skills).
- Requested spawn fields: none sent — per the repo's per-host subagent split, Claude Code hosts use the host's own typed-agent controls (`bounded-reviewer`) with session-model inheritance, and no host addressing `name` was passed.
- Host exposure state: host-defaulted
- Application state: reviewer ran on the session-inherited model; no host tier-application signal exposed.
<!-- allowed Delivery state: findings-received | findings-recovered-from-transcript | spawn-accepted-no-delivery | pending-parent-spawn. Boundary cleanliness is a separate claim and does not imply delivery. -->
- Delivery state: findings-received — the reviewer returned its findings inline under the unnamed spawn shape.

## Fresh-Eye Satisfaction

`parent-delegated`. One bounded reviewer spawned as `bounded-reviewer` with no
host addressing `name`; findings returned inline and it self-reported the
read-only envelope bound. Rail-1 boundary snapshot taken before the spawn and
verified `{"ok": true, "drift": []}` on return, before any fix was applied.

Its recommendation was HOLD-then-ship-as-minor. Both hold conditions (F1, F2)
were fixed before the tag, and F1 was verified independently by the parent
against `publish_release_baton.py` and `publication-boundary.md` rather than
taken on the reviewer's word.

Non-claim: the reviewer had no git access, so its release-readiness pass read
working-tree state rather than the four commit diffs, and it explicitly asked the
parent to supply the direction of the third gate's behavior change. The parent
answered that from its own earlier reading and corpus run — same-agent evidence,
not fresh-eye, and recorded as such.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: `handoff` owns what the baton may state; `release` owns what a publish requires the baton to state.
- Consumer: the operator writing the baton at release closeout, and the commit-time gate that judges it.
- Owning surface: `state-selection.md` for the rule and its carve-out, `publication-boundary.md` for the reconcile obligation that consumes it.
- Verdict: owned-correctly — the two skills legitimately own different halves, and the defect was an undocumented seam between them rather than a misplaced rule. Neither rule moved; the shared boundary is now stated on both sides and pinned by a test.
