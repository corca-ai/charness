# Setup And Quality Posture Critique

Date: 2026-05-16
Target: code critique for `50dd2b7 Normalize setup and quality posture`
Fresh-Eye Satisfaction: parent-delegated
Packet Consumed: `charness-artifacts/critique/2026-05-16-021809-packet.md`

## Change

The reviewed change normalized the setup routing surface, repaired quality
bootstrap preservation for `mutation_testing`, restored plugin import smoke,
excluded ignored generated mutation output from standing-test economics, and
recorded setup plus quality artifacts.

## Angles

- Michael Jackson / problem framing: checked whether the diff solved setup and
  quality normalization or bundled adjacent repairs under an unclear frame.
- Gerald Weinberg / diagnostic: checked whether the fixes addressed root causes
  rather than symptoms in adapter bootstrap, generated surfaces, and tests.
- Atul Gawande / operational checklist: checked operator-facing cleanup,
  rollback/audit evidence, and packet/surface closeout behavior.
- Counterweight: separated ship blockers from cheap bundle work and future
  design concerns.

## Findings

- The original prepare packet was inadequate for committed-diff critique because
  it inspected only the clean working tree and reported no changed paths for a
  17-file commit.
- The concrete `mutation_testing` preservation fix is acceptable for this slice;
  generic unknown adapter-field round-tripping remains a future design concern.
- The managed doctor readiness assertion intentionally pins the repo's current
  setup posture and should not block this slice.
- Agent-browser cleanup before/after JSON would improve auditability, but the
  listed cleanup command plus passing doctor result is enough for this slice.

## Scenario Review

- Reviewed public-skill dogfood prompt: "Stress this pending decision before we
  lock it in and separate real blockers from over-worry."
- The current routing still belongs to `critique`; the change only sharpens the
  prepare-packet evidence path for already-committed diffs.
- No maintained Cautilus scenario is needed for this slice. The dogfood contract
  is frozen in `docs/public-skill-dogfood.json`, and deterministic tests cover
  the `--changed-ref` behavior.

## Counterweight Triage

### Act Before Ship

1. Commit-aware critique packet generation.
   - Resolution: implemented.
   - Change: `prepare_packet.py` now accepts `--changed-ref`; script sections
     receive it through `CHARNESS_CRITIQUE_CHANGED_REF`, and the changed-surface
     producer renders committed refs/ranges instead of only current working-tree
     changes.
   - Proof: regenerated `2026-05-16-021809-packet.md` for `HEAD^..HEAD`; it now
     lists the 17 changed files and owning surfaces from `50dd2b7`.

### Bundle Anyway

1. Cleanup proof could include before/after JSON in future quality artifacts.
   This is cheap when the same artifact is already being edited, but not a
   blocker for the committed setup/quality repair.
2. Commit body/title archaeology could be richer, but the quality artifact
   carries the detailed repair ledger.

### Valid But Defer

1. Generic unknown adapter-field preservation remains real but separate. This
   slice preserves the validated `mutation_testing` block that actually failed.

### Over-Worry

1. The managed doctor test's `ready` expectation is acceptable because this repo
   intentionally gates ambient setup drift.

## Next Move

Ship the critique packet fix with the regenerated packet and targeted tests,
then rerun slice closeout before committing.
