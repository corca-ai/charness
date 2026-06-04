# Coordination With Existing Skills

`achieve` is a goal lifecycle operator, not a task execution engine and not a
replacement for the workflow skills. It coordinates them around one goal
artifact. Each coordinated skill must still be useful standalone; do not add
`achieve`-only branches to them.

| Skill | Role inside an achieve goal |
| --- | --- |
| `ideation` | clarify the user's intent and upstream decisions before the goal is shaped |
| `spec` | turn the goal into a living implementation contract when the target is complex enough |
| `impl` | execute slices; treat an active goal artifact as the slice memory surface |
| `debug` | for a bug-class goal, drive a falsifiable root-cause *before* the fix slice; record the hypothesis or debug-artifact path in the Slice Plan |
| `quality` | design verification up front, run cheap checks during, broad gates near final |
| `issue` | record off-goal findings (reference + reason only); **and**, when the goal resolves a tracked issue, close it through `issue` at closeout (see *Resolving A Tracked Issue*) |
| `critique` | review the goal plan before activation, substantial slices, and final proof |
| `retro` | produce the automatic after-action review focused on time/token/waste |

## Resolving A Tracked Issue

When the goal's outcome is resolving a tracked GitHub issue (its title or
`Context Sources` name `#N`), coordinate two existing skills the goal's own
slices would otherwise bypass, and record both in the goal artifact so the run
does not improvise them:

- **`debug` for bug-class.** If the issue is bug-class (real behavior diverges
  from a documented or implied contract), drive a falsifiable root-cause through
  `debug` *before* the fix slice, and record the hypothesis (or debug-artifact
  path) in the Slice Plan. This mirrors the causal-review discipline the
  `issue resolve` flow mandates for bug-class issues — an `achieve` goal that
  fixes the bug with its own `impl` slices does not inherit it automatically.
- **`issue` to close at closeout.** Stage the originating issue's close through
  `issue`, not by hand: put the close keyword `Close #N` in the body of the
  commit (or PR) that lands the fix **on the default branch**, so the
  maintainer's push auto-closes the issue. Preserve the keyword through squash /
  rebase / edited-merge bodies (the `issue` skill's closeout-discipline owns this
  failure mode). At `achieve` closeout the issue is still **OPEN** — it is
  *staged* to auto-close, not closed; `achieve` does **not** push or run an
  out-of-band close (push timing stays the maintainer's call). Without the
  keyword a goal can resolve an issue yet leave it open after push; that gap is
  what this coordination closes.
- **Record the close-intended ledger.** In `## Coordination Cues`, add
  `Issue closeout:` with the issue numbers, chosen carrier, close-keyword state,
  classification/critique evidence, and the exact `validate-closeout-draft` or
  `verify-closeout` proof. Bundled carriers are allowed, but each issue's
  critique evidence must be bound through `Critique #N:` or an explicit bundle
  line owned by the `issue` verifier.

This coordination is **operator-side**: `achieve` (the goal operator) plans the
two steps into the goal artifact — the `debug` step in the Slice Plan, the close
keyword at closeout — and invokes `debug` and `issue` **as-is**. Neither skill
gets an `achieve`-only branch, and each stays useful standalone.

The closeout publication default and issue-closeout carrier are adapter-owned.
Resolve `references/adapter-contract.md` before final closeout when a goal names
tracked issues or publication: missing adapters are safe `audit-only`; a repo
adapter may choose `handoff-only` or a publish-capable carrier and may require
the `issue` skill's direct-commit draft validator before push.

## Coordination Cues (find-skills routing + closeout floors)

The role table above is the standalone-skill reference, not the run-time router.
During an active run the goal artifact's `## Coordination Cues` section is where
phase-appropriate routing actually happens, and it **defers which skill answers a
boundary to `find-skills`** (`--recommend-for-task` /
`--recommendation-role --next-skill-id`) — `achieve` never bakes a phase→skill
map into the template or this reference. Seeding the cue in the artifact (read
mid-run), not only in a table read once at shaping, is deliberate: a read-once
table is inert exactly when the cue would fire.

Three boundaries also earn presence-only closeout floors, because a prose cue
alone gets skipped under context pressure and the miss is silent and costly:

- **gather** — when `## Context Sources` names an external source (URL / Slack /
  Notion / Docs / Drive), the run records a `Gather:` step (or
  `Gather: n/a — <reason>`). Mandated by `CLAUDE.md`'s external-source routing.
- **release** — when the run touches a release surface (version bump / install
  manifest), the run records a `Release:` step (or `Release: n/a — <reason>`).
- **issue closeout** — when `## Context Sources` names a tracked/GitHub issue or
  recorded work sections (`## Slice Log` / `## Final Verification`) carry a
  close keyword, the run records an `Issue closeout:` step (or
  `Issue closeout: n/a — <reason>`).

All are enforced by `goal_artifact_coordination_floors.py` at the `complete`
flip, grandfathered by `Created` date, presence/binding-only (never
prose-quality classification). Gather/release apply to goals Created ≥
the gather/release rule landing date; issue closeout applies to goals Created
on or after its landing date. They are
operator-side cues `achieve` plans into the artifact — `gather`, `release`, and
`issue` stay useful standalone, with no `achieve`-only branch. See
`references/lifecycle.md` After-phase for the full contract.

## Activation

The user activates a saved goal explicitly:

```text
/goal @charness-artifacts/goals/<file>.md
```

`/goal` is the host's autonomous-run entrypoint, not a command `charness` ships.
Reference it where the host provides it (Codex backs it with a goals store; the
user confirmed it on their Claude Code). `achieve` prepares and audits the goal
artifact; it does not implement the run loop itself.

## Boundary With `handoff`

Do not make `handoff` the default mid-goal state surface. While a goal is active,
the goal artifact owns running context. `handoff` is still the right surface when:

- the session is stopping outside an active goal
- a blocked goal needs the next session to resume with explicit context
- the user asks for a handoff artifact

## Off-Goal Findings

If a finding is not required for the current goal, file or defer it through
`issue` and append only the reference and reason to the goal artifact's
`Off-Goal Findings` section. Do not silently expand the active goal just because
a local fix is possible.
