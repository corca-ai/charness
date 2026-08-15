# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1 — the premise check over the next slice's scoped
  items — and only then invoke `impl`. S1-S6c and S6b-2 are committed, both review
  rounds run. **The classification ledger is next**, then S7.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the owner-approved wide scope,
  its sequence, `## Owner Rulings`, each slice's review record, and the findings carried rather than fixed.
- [S6b-2 retro](../charness-artifacts/retro/2026-08-16-s6b-2-cost-as-a-proof-surface.md) — what the
  changed-line proof found, the false quantity a reviewer refuted, and the carrier the Engelbart lens names.
- [Cost dominance](../skills/public/quality/references/cost-dominance.md) — the registry schema, the
  two blocking surfaces authoring it arms, and the exemption granularity that differs by seam.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique floor,
  the write-capable isolation rule, and the Claim Fidelity clause S6 skipped.

## Current State

- **S6b-2 is committed** — SC14, 15, 16, 17, 19 and S6b-1's sampler remainder. One owner
  (`command_dominance_lib`) states its blind class before the detector; the document seam
  lives in the handoff validator, the queued/spawned seam in a new blocking gate.
  Re-prove: `python3 scripts/check_command_dominance.py --repo-root .`.
- **Both review rounds are RUN and the two-round cap is reached.** Round 1 returned six
  blockers and nine majors; round 2, reading the repairs, refuted three of six attacked
  claims and found seven more defects IN them — including a quote-blind splitter that made
  a dominated command invisible to a blocking gate. Every finding and repair is in the
  [release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md)'s
  S6b-2 entry. **Round-2 repairs ship accepted-unreviewed at the cap**, per
  [operating contract](./conventions/operating-contract.md) Critique Discipline.
- **Two owner rulings landed 2026-08-16** — the exported inventory READS budgets rather
  than narrowing the claim, and the gate ships blocking with disclosure. Both are written
  out in the [release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md)
  S6b-2 entry, and the consumer-facing disclosure — which names both blocking surfaces —
  is [cost-dominance](../skills/public/quality/references/cost-dominance.md) in the quality skill.
- **S6b-2's changed-line proof is OBTAINED and clean.** It found unproven changed lines
  across every touched pool file before the commit was final; the count and the closures are
  in the contract's S6b-2 entry. Re-run:
  `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha 0037dbcfd --head-sha HEAD --test-command "python3 scripts/run_standing_pytest.py --repo-root ." --write-fresh-marker`.
- **[#634](https://github.com/corca-ai/charness/issues/634) STAYS OPEN and is commented**
  with the honest score: 2 of ~16 enumerated items.
- Re-prove the suite with `python3 scripts/run_standing_pytest.py` — xdist-parallel,
  budgeted, blocking. Run `python3 scripts/sync_root_plugin_manifests.py` FIRST: the
  generated mirror is a repair surface, and a run begun before its re-sync burns a cycle.
- Ruff is clean only cache-free: `ruff check --no-cache .`, never `ruff check .`.
- The release is still PREPARED: no bump, tag, or publish. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`.
- [cosmic-ray.toml](../cosmic-ray.toml) still holds its bare-pytest `test-command` on
  purpose; it is now EXEMPT with a measured reason and stays in the dominance report.
- Still no checked-in classification ledger; the closeout floor requires one before the
  prepared release record. Check with
  `python3 scripts/check_closeout_classification_parity.py --repo-root .`.

Non-claims: no push, tag, version bump, publish, hosted CI, installed-consumer readback,
or issue closure. S7 has not started. Round-2 repairs are unreviewed by construction. The
exported budget reading and the blocking-gate disclosure are proven locally only — no
consuming repo has run either, and an adversarial reviewer measured that SC19's consumer
half is structurally narrower than its criterion text.

## Next Session

1. **Before each slice, confirm its scoped items still reproduce on the current tree**
   (`gh issue view <id>`, then run the reproduction). In S6b-2 this caught that SC14's
   named first subject had already been repaired, so its clause was green on arrival.
2. **Write the classification ledger**, which the closeout floor requires BEFORE the
   prepared release record. Check the current state with
   `python3 scripts/check_closeout_classification_parity.py --repo-root .`.
3. Then **S7** publishes and closes [#608](https://github.com/corca-ai/charness/issues/608) and
   [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627);
   the classification ledger commits BEFORE the prepared release record, and S7's
   release-note obligations are listed in the contract's S7 entry — including the new
   blocking gate a consumer arms by authoring a registry.

## Discuss

- **The blind class still has no carrier, and this slice proved it twice.** Writing it
  first worked; the paragraph still shipped missing its whole false-POSITIVE direction,
  which a reviewer found. `validate_inference_interpretation.py` already gates a four-field
  declaration including `blind_spots` — but only for modules that DECLARE one, so a verdict
  module with no declaration is invisible to it. Extending it is the capability two retros
  have asked for and nothing has built.
- **A correction claiming completeness needs the same proof as the original claim.** The
  "13 of 14 wrapped" figure was labelled Measured, never counted, and its round-1 repair
  missed one surface while recording "Corrected everywhere". Both round-2 reviewers found
  the survivor. The repair that holds is the assertion, not the corrected number.
- **Nothing checks whether an authored descriptor is TRUE.** The gate only checks a line
  is not bare. Future delegated authoring owes a verification step; no surface enforces one.

## References

- [Design north star](./design-north-star.md) — P4, the different-observer rule that earned
  every blocker this session.
- [Parallel execution](./conventions/parallel-execution.md) — the disjoint-writer rule the
  reviewer fan-out ran under, and the proof floor a fan-out still owes.
- [Implementation discipline](./conventions/implementation-discipline.md) — the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
