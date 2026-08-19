# Probe Record: announcement-version-refusal

Debt rows 24-25 of slice 5, and `preflight_sources` is the sharpest publish-boundary
reading in the slice: the gate exists to STOP a delivery that would claim an in-progress
source is finished, and an unhonored declaration does not degrade it — it inverts it.

Claim: `preflight_sources` and `record_announcement` refuse when the adapter declares a
  `version` this reader cannot speak, instead of clearing a delivery the repo's own
  declaration blocks
Claim kind: change
Observable: the `delivery_blocked` / `ok` / `surfaces` the preflight prints and its exit
  code; the `adapter_resolved` field the recorder writes into its record log
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `adapter["data"]` is the reader's inferred defaults rather than what the repo wrote
Base ref: 254fa5c44
Head ref: working tree at 254fa5c44
Base arm: base-observed
Call sites unproven: none — each file holds ONE adapter read and the guard sits above it.
  `record_announcement`'s guard sits above its own `except Exception` fallback rather than
  replacing it; the arm that fallback still covers is measured and recorded below

## Source text

Verbatim from the manifest at the pinned revision.

```
    "skills/public/announcement/scripts/preflight_sources.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "Lines 38-46 call load_announcement_adapter() and pass adapter_data straight into preflight_sources() with no check of adapter['valid']/adapter['errors']; announcement_preflight_lib.py:66-72 short-circuits to {ok: True, delivery_blocked: False, surfaces: []} whenever sources is empty."
```

The source names the unguarded read AND the short-circuit that makes the flip total: the
preflight lib returns `ok: True, delivery_blocked: False, surfaces: []` the moment
`in_progress_sources` is empty, so an unhonored declaration is indistinguishable there
from a repo that declared none. The measurement below is that mechanism at runtime.

## Stimulus

A temp repo declaring one in-progress source. The entry is a MAPPING with a `kind` —
`_validate_in_progress_sources` rejects a bare string, and an earlier stimulus in this
slice used one, which sent the list back to empty and made the control unable to fail.

```
mkdir -p $D/.agents
cat > $D/.agents/announcement-adapter.yaml <<'YAML'
version: 9
repo: demo
delivery_kind: release-notes
release_notes_path: docs/mine-notes.md
in_progress_sources:
  - kind: path
    path: docs/pending-migration.md
    summary: a migration the announcement must not claim finished
YAML
python3 skills/public/announcement/scripts/preflight_sources.py --repo-root $D
python3 skills/public/announcement/scripts/record_announcement.py --repo-root $D \
    --head-commit deadbeef --delivery-kind release-notes
```

## Base observable

```
preflight_sources     delivery_blocked: false
                      ok: true
                      surfaces: []
                      exit 0

record_announcement   .charness/announcement/announcements.jsonl
                      exit 0
```

Clear to announce, over a repo that declared a source it must not claim finished.

## Head observable

```
`.agents/announcement-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

Measured on both.

## Polarity controls

- speakable version (`version: 1`), same declaration → `delivery_blocked: true`,
  `ok: false`, the declared `docs/pending-migration.md` listed in `surfaces`, **exit 2**.
  This is the control that carries the claim: a control asserting only exit 0 would be
  satisfied by a preflight that blocks nothing, which IS the base behavior.
- no adapter file at all → `delivery_blocked: false`, exit 0. A repo that declared no
  in-progress sources is genuinely clear to deliver; that answer was wrong only over a
  repo that declared some.
- ordinary-invalid (`preset_version: 3` beside a speakable version) → still
  `delivery_blocked: true`, exit 2. Both halves asserted.

## Non-claims

- **THE "ASYMMETRY IS CORRECT" CLAIM THIS RECORD FIRST CARRIED WAS REFUTED, and the
  refutation is kept rather than the claim quietly replaced.** It argued that a refused
  parse should be absorbed by `record_announcement`'s `except Exception` and recorded as
  `adapter_resolved: false`, "a typed, visible signal". A bounded review showed it wrong
  twice over. The harm it named —
  `requires_delivery_kind_agreement` comparing the recorded kind against a charness
  default — fires only for `delivery_kind: human-backend`, and this record's stimulus
  declares `release-notes`, so the published control could not exercise the harm it cited
  (Fixed Decision 2's disagreeing-observable rule, violated). And with the harm in play
  (`human-backend`, `--delivery-kind none`) the measurement was: `version: 1` raises
  `fail_delivery_kind_mismatch`; `version: !!int 9` exits 0 and appends a DURABLE RECORD.
  One token turned a hard refusal on the self-attestation bypass into a written record.
  "Typed and visible" was not enforcement either: no production surface reads
  `adapter_resolved` — only tests and one prose line.

  Both are now CLOSED, and the closure is a resolver repair rather than a consumer guard —
  see the next bullet.
- **TWO LIVE EXIT-0 BYPASSES OF THIS PUBLISH GATE were found by that review and closed,
  neither needing a version to be touched.** (1) `announcement_adapter_lib` called
  `adapter_lib.load_yaml_file` bare, discarding the uninterpreted-line sink, so an
  over-indented `in_progress_sources:` block left `errors: []`, `valid: true`, no warning,
  and `delivery_blocked: false / ok: true` at exit 0 — two of the guard's three doors were
  structurally dead for this adapter. Repaired by arming the sink, AHEAD of
  [#673](https://github.com/corca-ai/charness/issues/673), because the bypass is a publish
  boundary rather than a message shape; that also makes the parse door reachable and
  closes the delivery-kind bypass above. (2) `_validate_in_progress_sources` uses
  `continue` on every rejected entry, so ONE bad entry empties the list and the empty list
  takes the same short-circuit — `kind: Path`, one capital letter, cleared the gate.
  Repaired by reading `field_state`, which already carried "the repo wrote this key",
  against the validated result. **This slice had already documented that second input, as
  a probe-authoring mistake, without noticing it was a live bypass of the gate it was
  repairing.**
- **The two doors now land the SAME way on `record_announcement`.** `version: 9` resolves cleanly to a payload carrying a
  `delivery_kind` the repo never wrote, so the guard refuses —
  `requires_delivery_kind_agreement` would otherwise compare the recorded kind against a
  charness default. `version: !!int 9` makes announcement's resolver RAISE (one of the six
  in [#673](https://github.com/corca-ai/charness/issues/673)); the guard swallows that,
  answers `None`, and the module's own `except Exception` arm records
  `adapter_resolved: false`. That was VERIFIED by reading the written record, not assumed,
  and it is exactly the case that fallback was written for. Forcing symmetry would replace
  a legible fallback with a stop on the one input where the fallback is right.
- The preflight's parse door refuses with a raw traceback for the same reason, which is
  the same named residual, not a new one.
- This record establishes TWO files. Recount the rest with
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .`.
- The claim is about the delivery verdict and the recorded resolution state. Nothing here
  asserts either command is correct in any other respect.
