# Weekly Evidence And Trends

This reference captures what `charness` should and should not borrow from
`gstack`'s heavier weekly retro flow.

## Useful Imports

- name the weekly window explicitly instead of implying "recently"
- state which evidence sources were actually used
- compare against the last durable weekly retro when one exists
- persist a compact snapshot only when the adapter defines an explicit durable path

## Critique

If `weekly` borrows too much from `gstack` without a portability filter, the
likely failure modes are:

- host-specific state leaks into the public skill
- the retro pretends to have metrics it does not really have
- outputs become too long to be used in normal repos
- persistence becomes ambiguous because the skill writes hidden files

## Portable Design Decisions

- `weekly` should prefer durable repo artifacts over live host state.
- `weekly` should name the current window and the evidence set it relied on.
- If a prior weekly retro exists under `output_dir`, compare against it.
- If no prior weekly retro exists, say "First weekly retro recorded" or
  equivalent instead of inventing a trend.
- If `metrics_commands` are missing or weak, the retro may stay narrative-only,
  but it must say so explicitly.
- A machine-readable weekly snapshot is allowed only when the adapter gives an
  explicit `snapshot_path`.

## Closeout Waste Trends

Weekly may mine the local **closeout-telemetry** stream (objective operational
waste the slice closeout already records: gates that pass but run over budget,
and over-slice artifact-only-commit runs — spec achieve-efficiency-improvements,
direction E). Read it with
`$SKILL_DIR/scripts/mine_closeout_telemetry.py --repo-root .`.

- This is **reading** an already-written local stream, not the telemetry/usage
  *logging* the skill must not add (see *What Not To Copy*). Weekly never writes
  the stream; E1's closeout emitter does.
- **Disposition teeth (route recurring waste to a filed issue, not the digest).**
  A waste item the miner marks `recurs:` (seen across multiple runs) must
  disposition to a **filed `issue`** — tracked work the handoff chunker reasons
  over — using `../../../shared/references/retro-issue-destination-split.md`. Do
  **not** park recurring waste in the `recent-lessons.md` digest: it has a
  ~14-day half-life and would decay the item back out (the prose-decay trap this
  direction exists to fix). A one-off (`watch`) waste item needs no issue yet.
- **Cross-repo non-claim.** The miner mines *this* repo's local, gitignored
  stream only. Waste produced while running the skills in another repo (e.g.
  acme) lives in that repo's own stream; charness has no cross-repo telemetry
  visibility. State this in the weekly output rather than implying global reach.

## What Not To Copy

- session-dir or live-state orchestration
- telemetry and usage *logging* (the skill must not write hidden telemetry; it
  may *read* an existing local closeout-telemetry stream — see above)
- host-specific prompt injection or startup hooks
- giant global dashboards that require non-portable infrastructure
