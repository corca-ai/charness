# Retro → Issue: Generalization And Destination Split

This is the shared contract for turning a retrospective waste finding into one or
more issue proposals. `retro` classifies along the two axes below, `achieve`'s
Auto-Retro dispositions each improvement against them, and `issue` routes the
result to the correct target. Each skill stays usable standalone; this reference
is the single place the axes are defined so the three do not drift.

The failure this prevents: a retro lesson becomes an issue that says "fix the one
thing that happened this run," filed into whichever repo happened to be open.
That couples the fix to the incident and to the wrong surface. Both axes below
decouple it.

## Axis 1 — Generalization (structural, not incident-coupled)

Every issue proposal derived from a retro finding carries two fields:

- `Structural pattern:` — the generalized failure mode or improvement. State it
  so it would read sensibly even if this run had never happened. This is the fix
  scope.
- `Triggering instance(s):` — the specific incident(s) that surfaced the pattern.
  This is *evidence*, not the fix scope.

The split is the whole point: the structural pattern is what gets fixed; the
instance is why we believe it is real. An issue that only restates the instance
("the release helper lost the diff this time") is incident-coupled; the same
finding generalized ("release helpers that commit before evaluating a trigger
lose the trigger's input — any such helper needs the input captured before the
mutating step") is structural.

This is enforced **presence-only** (see Enforcement). The check proves both
fields exist; a human or reviewer judges whether the pattern is actually
general. Do not add a content classifier that scores "structural enough" — that
re-imports the word-list trap the achieve disposition floor explicitly forbids.

## Axis 2 — Destination (where the fix lands)

Classify each actionable improvement by the surface that owns the fix:

- `upstream-harness` — portable charness skill / harness core: skill prose,
  shared references, scripts, validators, adapter *schemas*, presets, profiles.
  A fix here helps every repo that installs charness.
- `repo-local` — the current repo's own operating surface: skill *adapters*
  (`.agents/*.yaml`), repo-local skills, `AGENTS.md` / `CLAUDE.md`, folder
  structure, test fixtures, code quality, repo-specific docs. A fix here helps
  only this repo.
- `both` — a finding that genuinely needs a generalizable upstream fix **and** a
  distinct current-repo adaptation. Only then is a split pair warranted.

Record the chosen value as `Destination:` on the proposal.

### D1 — Over-split rule (single destination by default)

Default to a single destination. Split one finding into an upstream + local pair
only when both are independently true and actionable:

1. there is a portable harness change that other repos would also want, and
2. there is a distinct current-repo change that the upstream fix does not cover.

If the local need is just "adopt the upstream fix here once it lands," that is a
follow-up note on the upstream issue, not a second issue. Never mechanically
fork every finding into two issues — that doubles backlog noise and double-counts
one root cause.

## Upstream Identity (B1) And The Collapse Rule (E1)

"Upstream charness" is resolved from the issue adapter, never guessed:

- `issue` adapter field `harness_upstream: <org/repo>` names the charness
  upstream repository (for charness itself: `corca-ai/charness`).
- Use `resolve_adapter.py resolve-destination --current <org/repo>` (or the
  library `resolve_destination_target`) to get concrete targets.

Three outcomes:

- **Consumer repo** (current repo ≠ `harness_upstream`, pointer set):
  `upstream-harness` → the `harness_upstream` repo; `repo-local` → the current
  repo. A `both` finding files one issue to each.
- **Collapse — current repo *is* charness** (current repo == `harness_upstream`):
  there is only one repo, so the destination axis does not map to two
  repositories. It maps to two *surfaces within this repo*: portable skill/
  harness core vs this repo's own operating surface (its adapters, AGENTS.md,
  fixtures). A `both` finding may still be two issues, but both target this repo
  and are distinguished by label/section, not by destination repo.
- **Unknown — safe fallback** (`harness_upstream` unset and current repo cannot
  be confirmed as the harness): keep the finding `repo-local`, file it to the
  current repo, and state the ambiguity in the issue body. Never file a harness
  issue into a guessed upstream repo.

## Enforcement (C2 — presence-only)

`validate_proposal_fields.py` checks that a proposal block carries non-empty
`Structural pattern:`, `Triggering instance(s):`, and `Destination:` fields, and
that `Destination:` is one of `upstream-harness` / `repo-local` / `both`. It is
presence/value-enum only: a present-but-vague pattern passes; a missing field
fails. It never judges whether the generalization is good — that is the
reviewer's job, exactly as the achieve disposition floor stays presence-only.

## The Structural-Follow-Up Destination (disposition-side, the teeth)

The two axes above shape an issue *once a finding is headed for one*. The prior
question — for a **transferable** waste item (one a retro's `## Sibling Search`
names), where does the structural follow-up go *at all*? — is the
structural-follow-up **destination**. This shared section is the single source of
that vocabulary: `retro` records it per transferable waste item, `achieve`'s
disposition review classifies it, and the achieve disposition gate (rung 1e in
`goal_artifact_disposition.py`) enforces a valid form is present. The inline
four-form list in achieve `lifecycle.md` (rung 1e) is a display copy for the gate
contract, not a second source — it points here. One vocabulary, four forms:

- `applied: <gate/hook/validator/test/contract change>` — teeth landed this run.
- `issue #N (recurs: <lineage> | novel: <reason>)` — filed for later; the issue
  then carries Axis 1 (`Structural pattern:`+`Triggering instance(s):`) and Axis 2
  (`Destination:`) above, which route *which* surface owns it. That per-issue
  `Destination:` is independent of the sibling scan's per-location decisions.
- `repo-local guard: <path>` — a guard-level fix (test, hook, contract) landed now
  in this repo's own local surface (the `repo-local` Axis-2 destination realized as
  applied teeth, distinct from a generic `applied:` change or a filed `issue #N`).
- `none — <reason>` — no structural follow-up; a falsifiable claim the disposition
  review can contradict.

This composes with the per-location decisions in the retro waste-sibling-scan
(`waste-sibling-scan.md`): `same waste, fix now` → `applied:`;
`valid follow-up outside the slice` → `issue #N` / `repo-local guard:`;
`diagnostic-only` / `intentional boundary` → `none — <reason>`. The sibling scan
decides *per location the same waste shape recurs*; the destination is the
*per-waste-item* disposition.

**Presence/form-enum only**, exactly like Axes 1–2: the floor proves a valid
destination form is present; the disposition reviewer (and the human) judge
whether the chosen destination is right, and **reject "recorded in
recent-lessons"** as a destination unless it is paired with one of the four forms
— a bare memory note is capture, not a structural disposition. Never a content
classifier (the achieve guardrail). The code single source of the form grammar is
`disposition_form.py` (`evaluate_destination_form`).

## Worked Examples

- **Single (upstream).** Retro: "the disposition gate let a blank Auto-Retro
  through once." → `Structural pattern:` Auto-Retro completion can be claimed
  without dispositioning surfaced improvements; the gate needs a block-the-blank
  rung. `Triggering instance(s):` goal X on 2026-0x-xx. `Destination:`
  upstream-harness. One issue to `corca-ai/charness`.
- **Single (repo-local).** Retro: "editing handoff broke a test that pins stale
  issue numbers." → `Structural pattern:` repo-local fixtures that hard-pin live
  issue numbers break on unrelated edits; pin via fixture, not live state.
  `Destination:` repo-local. One issue to the current repo.
- **Both (consumer repo).** Retro: "the skill assumed `gh` on PATH; our host
  uses a mediated backend." → upstream: skill prose should never assume a binary
  (`harness`); local: this repo's `<repo-root>/.agents/issue-adapter.yaml` must
  declare the mediated backend (`repo-local`). Two issues, one per target.
