# Achieve README Route Critique

## Execution

- Target: code critique for the achieve README / workflow-route documentation
  patch.
- Fresh-Eye Satisfaction: parent-delegated.
- Packet Consumed:
  `charness-artifacts/critique/2026-05-31-221042-packet.md`.
- Angle reviewers:
  - `019e8017-2edd-76d2-8802-21178be3d41e`: problem framing / reader
    discoverability.
  - `019e8017-4118-7a12-b7e2-7b18fbf997c6`: operational / generated-surface
    honesty.
  - `019e8019-b058-7462-83b4-ab7b3a73991a`: counterweight.

## Diff Scope

- Add `achieve` to the root README workflow route and public skill map.
- Add a long-running/autonomous goal route section to
  `docs/workflow-routes.md`.
- Add a README proof-ledger row for the achieve long-goal claim.
- Regenerate the checked-in plugin README mirror.

## Counterweight Triage

### Act Before Ship

- Root README and plugin README originally said to activate with `/goal` without
  saying that `/goal` is host-provided, not shipped by Charness.
  - Disposition: addressed in `README.md`; plugin README was regenerated.
- The proof-ledger row originally cited `docs/handoff-chunked-routing.md`, an
  adjacent spec, instead of the direct achieve contract owners.
  - Disposition: addressed by citing `skills/public/achieve/SKILL.md`,
    `skills/public/achieve/references/lifecycle.md`,
    `skills/public/achieve/references/coordination.md`, and the goal artifact
    scripts.

### Bundle Anyway

- The root README pointer to the longer route guide did not mention
  long-running goals even though the new section lives there.
  - Disposition: addressed in `README.md`; plugin README was regenerated.

### Over-Worry

- Expanding the root README with the full achieve lifecycle would overload the
  first-touch surface. The chosen split is better: README carries discovery,
  `docs/workflow-routes.md` carries philosophy and boundaries.
- A Cautilus run is not needed for this docs-only patch; the proof ledger marks
  the new claim as partial.

### Valid But Defer

- Representative long-goal routing/evaluator coverage is still missing.
  - Disposition: recorded in `docs/readme-proof.md` as the next proof gap.

## Verification

- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`
- `python3 scripts/check_doc_links.py --repo-root .`
- `python3 scripts/check_command_docs.py --repo-root .`
- `./scripts/check-markdown.sh`
- `./scripts/check-secrets.sh`
- `bash .githooks/pre-commit`
