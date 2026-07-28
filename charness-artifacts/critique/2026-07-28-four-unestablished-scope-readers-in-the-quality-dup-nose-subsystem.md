# Four unestablished-scope readers in the quality dup/nose subsystem
Date: 2026-07-28

## Decision Under Review

Closing triage-sweep rows S27/S29/S33/S34 by making the quality dup/nose readers
distinguish a producer that DECLARED zero families from one that established nothing —
and, once two review rounds found the fix carrying its own class, extending that same
distinction to six sibling readers and two writers in the same subsystem.

## Failure Angles

- **The fix reproduces the class it fixes.** This repo's measured rate was 9 of 9 slices,
  and it happened twice more here: round 1 found six instances inside the first fix
  (a self-declared count as the only signal, `or set()` erasing an unreadable baseline, a
  summed survivor count, a truncated member set, a guard dead against the real producer),
  round 2 found three more inside the repairs (a status set omitting `degraded`, a survivor
  count that could go negative, an overlay reader weaker than its own sibling).
- **A widened refusal buys a false refusal.** Every new guard here sits on a path that
  either degrades a gate (advisory, cannot false-block) or exits nonzero (`migrate`,
  `seed`, `write-baseline`). The nonzero ones are where a wrong contract assumption becomes
  an operator-blocking bug, and the blank-stdout reading is exactly such an assumption.
- **A dead guard reads as a live decision.** The first fix added a doc-side `family_count`
  mismatch check that could never fire, and it hid the real doc-side hole one line away.
- **Tests that cannot fail.** A flipped assertion can move to match the code rather than to
  pin a contract, and a fixture can reconstruct a payload no producer emits.

## Counterweight Pass

- The blank-stdout contract was the one genuinely contingent risk, so it was PROBED rather
  than argued: a scope root with no supported files still prints
  `{"families":[],...,"summary":{"families":0,...}}` and exits 0, and a nonexistent root
  exits 1 with non-JSON. Blank stdout is therefore not producible by a clean scan, and the
  degrade cannot false-refuse a clone-free repo.
- `write_baseline` over a zero-family scan is a CONFIRMATION gate rather than a refusal for
  the same reason inverted: a genuinely clone-free scope is real, so it must stay reachable
  with `--confirm-baseline-delta`.
- Two reviewer findings were left OPEN rather than folded: the changed-line coverage gate's
  failed-`git diff`-reads-as-no-files (a blocking gate in another subsystem) and the
  dup-ratchet zero-family backstop's `and baseline_ids` (fixing it naively false-refuses a
  clone-free consumer repo). Both are recorded as sweep leads; neither is this slice.
- The dead `family_count` guard was REMOVED rather than kept as harmless: an allowlist-shaped
  guard that cannot fire is worse than none, because the next reader treats it as coverage.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/draft_dup_ratchet_triage.py:146 | action: fix | note: the unevaluated-status set omitted `degraded`, the canonical could-not-judge status and the one every code-arm degrade this slice added now produces; a writer that drafts a permanent accept read it as "no new families". Fixed by keying on status AND non-empty degraded_reasons, and the refusal still lists whatever the payload named.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/migrate_dup_fingerprints.py:220 | action: fix | note: the overlay vanish arm computed survivors as `len(ids) - len(dropped_ids)`, which goes NEGATIVE on a duplicated or id-less overlay entry, and `not -1` is False — the guard disarmed by the shape it was written to catch. Fixed with a set difference; proved by injecting the old arithmetic and watching the new test fail.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/seed_dup_review.py:97 | action: fix | note: the overlay reader refused only unparseable JSON while its sibling in the same repair round required a dict with an `entries` list; a list/scalar/renamed-key overlay still wiped every operator classification through a parse that succeeded.
- F4 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/scripts/draft_dup_ratchet_triage.py:62 | action: fix | note: `_unsampled_member_count` returned 0 for an ABSENT member count, so a record that never said how many members it has was indistinguishable from a fully sampled one and the permissive branch won. Now returns None and refuses.
- F5 | bin: act-before-ship | evidence: strong | ref: tests/test_doc_duplicates_inprocess_coverage.py:94 | action: fix | note: an assertion loosened from `== "boom"` to `"boom" in ...` stopped discriminating, leaving the doc arm's empty-output naming pinned by nothing. Both halves are asserted now, plus the exit-0 case the exit-code branch never covered.
- F6 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/scripts/nose_report_shape_lib.py:93 | action: document | note: the raw-entry-count arm's justification claimed a primary signal, but no nose version is known to emit non-dict family entries. Docstring downgraded to defensive-against-a-future-shape, with the producer-grounded arm named separately.
- F7 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/changed_line_coverage_gate_lib.py:27 | action: defer | follow-up: deferred charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md R8 | note: a failed `git diff` returns `[]`, which a BLOCKING gate renders as "no eligible changed files"; the freshness fingerprint is vacuous in the same breath. Different subsystem, own slice.
- F8 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/check_dup_ratchet.py:138 | action: defer | follow-up: deferred charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md R9 | note: the zero-family backstop is gated on `and baseline_ids`, so an empty baseline disarms it, and there is no doc-arm equivalent. Needs a design that cannot false-refuse a clone-free consumer repo.
- F9 | bin: over-worry | evidence: weak | ref: skills/public/quality/scripts/nose_report_shape_lib.py:75 | action: defer | note: a payload carrying BOTH `families` and `top_candidates` with the keyed one empty would read clean; nose emits one INSTEAD of the other, and preferring the non-empty list would break the reader/guard symmetry that makes the raw-count check trustworthy.
- F10 | bin: over-worry | evidence: weak | ref: skills/public/quality/scripts/dup_ratchet_rebaseline.py:64 | action: document | note: `--confirm-baseline-delta` now answers two questions (a clone-free scope and a large accepted-set delta), so confirming one waives the other. Maintenance-only path that cannot reach the evaluate arm; noted rather than split.

## Reviewer Tier Evidence

- Requested tier: medium
- Requested spawn fields: agent type `bounded-reviewer` (read-only Read/Grep/Glob), no host addressing name, session model inherited per the Claude Code host branch of the per-host subagent contract.
- Host exposure state: host-defaulted
- Application state: host resolved the typed read-only agent and inherited the session model; no per-subagent model/effort control was requested on this host.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — five bounded reviewers across two rounds: round 1 (fix-carries-its-class,
sibling propagation, false-refusal/test-honesty) and round 2 (repairs-carry-the-class,
test-honesty/move-safety). All findings arrived in-band; none was recovered from a transcript.
Reviewer boundary was snapshotted before round 1 and verified after: every drift path was a
parent write from the repair round (the parent made all writes in that window), and the
reviewers hold no write, exec, or spawn capability by construction.

Fresh-eye pass: skills/public/quality/scripts/nose_report_shape_lib.py — the round-2
reviewer walked every branch of this new proof surface against the advisory's own classes,
specifically class (b) (a verdict keyed on a field that is constant or coarse where it must
discriminate): it found the declared-total arm reachable but insufficient alone, the
raw-entry-count arm defensive rather than producer-reproduced (F6, docstring corrected), and
the `families`-before-`top_candidates` key precedence deliberately identical to
`extract_report`'s so the reader and the guard cannot disagree. Its verdict-rendering role is
accepted, not incidental: this module exists to say when a report establishes nothing.

## Public Skill Validation Decision

The `quality` skill's routing/prompt contract and its dogfood acceptance evidence are
UNCHANGED by this slice: it hardens helper-script strictness (a gate that degrades and names
a reason instead of reporting `clean` over an unestablished scan), not the skill's surface or
the artifact it produces. The checked-in consumer case in `docs/public-skill-dogfood.json`
therefore stays frozen as-is and still validates. The scenario worth a maintainer's eye is
the operator-visible behavior change — a dup-ratchet run over a broken or misconfigured
inventory now reports `degraded` with named reasons instead of `clean`, and
`--write-baseline` over a zero-family scan now needs `--confirm-baseline-delta` — which is
documented in the degrade ladder of
[dup-ratchet.md](../../skills/public/quality/references/dup-ratchet.md), the reference an
adopting repo reads. `quality` is `hitl-recommended`, so this is recorded as an explicit
decision rather than treated as an evaluator scenario that must run.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with `- Packet consumed: <packet-path>` plus three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. That `Packet consumed:` line is what turns the binding floor on. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: nose (via `nose_tool_lib.run_json_query`) and the two inventory CLIs, which emit either a report that declares a family list or a payload that establishes none.
- Consumer: the dup-ratchet gate verdict, the migration/rebaseline/seed writers, and the triage packet an operator reads before writing a permanent `intentional` accept.
- Owning surface: the reader that turns a payload into a family set — `nose_report_shape_lib` for report shapes, `dup_ratchet_scan` for injected inventories — not each verdict-rendering consumer.
- Verdict: moved-to-owner
