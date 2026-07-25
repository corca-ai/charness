# Closeout Telemetry

A retro may mine the local **closeout-telemetry** stream: objective operational
waste the slice closeout already records — gates that pass but run over budget,
and over-slice artifact-only-commit runs. Read it with:

```bash
python3 "$SKILL_DIR/scripts/mine_closeout_telemetry.py" --repo-root .
```

This is **reading** an already-written local stream, not telemetry *logging*.
The skill must never write hidden telemetry; the closeout emitter owns the
stream, the retro only reads it.

## Why it belongs in every retro

Gate-runtime waste is the failure this stream is best at catching, and it is
invisible to a passing gate by construction: a gate that passes at 475s reports
success, so nothing else in the harness ever raises it. Recurrence is the signal,
and recurrence only shows up across runs — which is exactly what the stream
holds and a single session's own observation does not.

## Disposition teeth

Route recurring waste to a **filed issue**, not the digest.

A waste item the miner marks `recurs:` (seen across multiple runs) dispositions
to a filed `issue` — tracked work the handoff chunker reasons over — using
`../../../shared/references/retro-issue-destination-split.md`. Do **not** park
recurring waste in the `recent-lessons.md` digest: it has a ~14-day half-life
and would decay the item back out, which is the prose-decay trap this rule
exists to fix. A one-off (`watch`) item needs no issue yet.

## Non-claims

- **Cross-repo.** The miner mines *this* repo's local, gitignored stream only.
  Waste produced while running the skills in another repo lives in that repo's
  own stream; there is no cross-repo telemetry visibility. State this in the
  output rather than implying global reach.
- **Reading is not proof.** An occurrence count is evidence that a cost recurs,
  not a verdict on whether the cost is worth paying. Answer that question for
  this repo before escalating a number.
