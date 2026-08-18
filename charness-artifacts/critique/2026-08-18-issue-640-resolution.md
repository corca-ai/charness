# issue-640-resolution
Date: 2026-08-18

## Decision Under Review

Making the artifact line ceiling a consuming repo's adapter setting (#640) across
debug, quality and handoff, plus the shared `optional_int` primitive whose absence
is why the ceiling was a module constant at all.

## Failure Angles

- Completeness of reach: the ceiling is enforced in a validator and forecast in a
  scaffold/planner. A surface missed by the override renders a verdict against a
  number the gate no longer enforces, which is worse than no override.
- Refactor blast radius: `apply_optional_fields` replaced four hand-copied typed-field
  loops and `artifact_violation_report` was split out of `artifact_validator`. Either
  could change error ordering, key ordering, or monkeypatch identity silently.
- Consuming-repo contract: this ships as a vendored package. A new module that does not
  ship, or a field the canonical field enumeration never names, is a defect that only
  appears downstream.
- Repair-carries-its-own-class: the round-1 repairs touched verdict logic on a proof
  surface, so they owe their own read.

## Counterweight Pass

- Real blockers, all repaired: two author-facing forecast surfaces
  (`check_doc_authoring_preflight`, `doc_authoring_rules`) still read the shipped
  default while the handoff planner emitted both commands, so one run computed the
  resolved ceiling and then instructed the author to run a command contradicting it;
  and an unguarded `LINE_BUDGET_FIELD` attribute read turned a stale vendored resolver
  into an AttributeError at import — a traceback and no verdict on a proof surface.
- Real but smaller, repaired: the round-1 fix's own `except Exception` returned the
  default silently while the doc shipped beside it claimed that could never happen.
- Over-worry, closed by reading the parent rather than by argument: field application
  order was string -> list -> int at `c34155a48` in all three callers, identical to
  `apply_optional_fields`, so no `errors` or `validated` ordering changed. `__all__`
  did not list the moved names at the parent either.
- Deliberately not done: no upper bound on the override. Clamping would reintroduce a
  charness-chosen number by the back door, which is the defect being fixed; the repo
  already owns `output_dir` and `artifact_class` on the same adapter.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_doc_authoring_preflight.py | action: fix | note: rendered `status: blocked` against the shipped default; repaired via `resolver_attr` + `surface_cap`
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/validate_debug_artifact.py | action: fix | note: bare `LINE_BUDGET_FIELD` read crashed at import under resolver skew; now `getattr` with the literal default
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/debug/scripts/scaffold_debug_artifact.py | action: fix | note: round-1 guard degraded silently; `size_budget.source` now names the degradation
- F4 | bin: act-before-ship | evidence: moderate | ref: skills/public/debug/references/adapter-contract.md | action: fix | note: canonical field enumeration omitted the new field; added to all three contracts
- F5 | bin: act-before-ship | evidence: moderate | ref: tests/test_doc_authoring_preflight.py | action: fix | note: cap-drift test passed only because this repo declares no ceiling; now patches the resolver
- F6 | bin: over-worry | evidence: strong | ref: scripts/adapter_field_application.py | action: defer | note: field-order change was hypothesized, then refuted by reading the parent — order was already string/list/int
- F7 | bin: valid-but-defer | evidence: moderate | ref: skills/public/handoff/SKILL.md | action: defer | note: literal `78` pinned by a literal-vs-literal test; re-basing that guard is a quality-contract change outside this issue's boundary

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` typed subagent (read-only: Read/Grep/Glob), four spawns across two rounds.
- Requested spawn fields: subagent_type plus a scope-bounded prompt per angle; no host addressing name, per the repo's unnamed-spawn rule.
- Host exposure state: host-defaulted
- Application state: all four spawns returned findings inline; each reviewer independently reported its envelope bound with no write, exec, or spawn tool exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewed input was the commit
range itself (c34155a48..53ea10d5a), named per angle in each spawn prompt. -->

## Boundary Ownership

- Producer: the consuming repo's `.agents/<skill>-adapter.yaml`, via each skill's `resolve_adapter.py`.
- Consumer: the artifact validators (the gate) and the scaffolds/planner/doc-authoring preflight (the forecast).
- Owning surface: the skill adapter contract, with `scripts/adapter_lib.optional_int` as the shared vocabulary the fields are expressed in.
- Verdict: owned-correctly
