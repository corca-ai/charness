# Duplicate-ratchet Backlog Triage — 2026-08-13

## Scope and evidence

The release closeout ran `check_dup_ratchet.py --detail` against the committed
baseline anchor `a52f83e9fd777b59e1e497bd3f826415f02bcf27`. It found 18 new
code-family fingerprints and three membership-reduction rotations. The gate
reported the #608 release implementation in only three families:
`56b292c02680b8e1`, `a9c46f642aadee2a`, and `fb13dedbafbf87d2`; the other 15
are accumulated changes after the anchor. This is a baseline-maintenance
closeout, not evidence that the three #608 changes created all 18 families.

## Disposition

The following are recorded in `dup-review.json` as intentional because their
shared text is direct-execution bootstrap, a tiny idiom, or independently-owned
state/refusal scaffolding: `16031fc80728cd01`, `30d8eb403aa57e12`,
`3dbe01fd711be4f4`, `4ddb93099cc5f8fb`, `56b292c02680b8e1`,
`858dfd6c7ff4dd3c`, `a936c856473995c9`, `a9c46f642aadee2a`, and
`fb13dedbafbf87d2`.

The following nine families are accepted into the gate baseline by an explicit
scoped operation, rather than misclassified as intentional. They remain
independent maintenance candidates: `17b6a4ce734600f7` (same-file quality
loaders), `438a0aed84c8501f` and `bdc05525bd427902` (same-file issue-create
spines), `eddf756a31124767` (same-file output selection), `3ad7e1ff2b43352c`
and `3b82e9ccbfd02e55` (similar but semantically distinct preset/skill parsers),
`8202a3238a3765a0` (direct-script bootstrap), `678309906c040b5b` (quality and
handoff read measurement with different declared bases), and `d66b0caecad32665`
(two dogfood suggestion CLI output contracts).

No family is silently accepted: the scoped command names every accepted family
and each observed membership reduction:
`fc1347ae7049f038=4aa7209224010575`,
`d46cb61704b0ffdc=5a202837839cb1ec`, and
`76ebd5b174802361=64b629c305fd8b01`. The exact command used those three
`--accept-rotation OLD=NEW` options and nine named `--accept-family` options;
its result was `scoped-rebaseline-written` with 686 stored fingerprints. A
subsequent ordinary gate run returned `status: clean` with zero new
fixable-eligible families. A later change that adds or materially changes
duplicate content remains subject to the hard arm.

## Non-claims

This triage does not claim the scoped-accepted families are refactored, nor does
it waive future duplication. It records the historical backlog necessary to
restore a truthful release gate after a succession of otherwise reviewed slices.
