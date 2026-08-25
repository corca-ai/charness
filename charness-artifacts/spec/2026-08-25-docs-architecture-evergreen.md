# Evergreen Documentation Architecture Contract

Date: 2026-08-25

## Problem

Charness already has a useful documentation graph, but its canonical index is
`docs/README.md` while the new setup profile promises `docs/index.md`. The
graph gate proves reachability, not currentness, ownership, or truth. Root
`AGENTS.md` also routes readers to many pages without stating the documentation
principles that keep those pages evergreen. A long-running goal or a dated
roadmap can therefore become the accidental source of truth.

## Architecture Contract

- `README.md` is first-touch orientation and points to the canonical docs index.
- `docs/index.md` is the one flat-wiki entry point. Evergreen topic pages live
  directly under `docs/`; the former nested `conventions/` and `generated/`
  directories were flattened in this migration.
- An evergreen `docs/` page states its status (`current`, `conditional`, or
  `generated`), owns one question, names its source of truth, and records the
  last verification date when that fact can change. It describes current
  behavior, not an append-only session history.
- Proposals, dated plans, superseded decisions, raw evidence, and retros live
  under `charness-artifacts/` (primarily `spec/`, `goals/`, `retro/`, and
  `quality/`). They may explain why a rule exists but do not silently override
  current docs.
- Generated pages are regenerated from their producer; they are not edited by
  hand. Every relative link is checked, and docs graph/awiki checks remain
  distinct evidence channels.
- A move or retirement is a planned, linked transition: classify the page,
  update all consumers, preserve a compatibility pointer when needed, then
  delete only after the graph and source-of-truth checks pass.

## Current Audit Findings

- `docs/README.md` is now a small compatibility pointer; `docs/index.md` is the
  only maintained index.
- `docs/operator-acceptance.md` is useful but contains a guarded reference to a
  missing `docs/roadmap.md`; its status and source-of-truth relationship need
  to be explicit rather than silently relying on a missing optional page.
- `docs/handoff.md` is intentionally live session state and must not be treated
  as evergreen architecture; its release facts need refresh at release.
- `docs/north-star-overhaul-roadmap.md` is a dated active plan, not evergreen
  architecture. Keep it only while it remains the explicit plan of record;
  otherwise move it to `charness-artifacts/spec/` with a pointer from the
  current docs index.
- The existing docs graph is healthy (`orphans=0`, `largest_component_ratio=1`)
  but does not judge page accuracy or freshness. This is a known non-claim.

## Observed Architecture Snapshot

The repository currently has four cooperating layers:

```text
consumer/operator
        │
        ├─ README.md ──> docs/index.md ──> docs/*.md
        │                              └─ flat pages (policy and generated output)
        │
        ├─ AGENTS.md ──> skill routing, safety, review, and docs principles
        │       └─ CLAUDE.md -> AGENTS.md
        │
        └─ charness CLI / host adapters
                ├─ skills/public/*       (portable source skills)
                ├─ plugins/charness/*     (generated install mirror)
                ├─ scripts/*              (control plane and validators)
                ├─ integrations/tools/*  (declared external capabilities)
                └─ tests/ + evals/        (deterministic and evaluator proof)

operational memory and evidence
        └─ charness-artifacts/
             ├─ goals/ + specs/   (long-run control panel and phase contracts)
             ├─ quality/          (current pointer plus dated reviews)
             ├─ debug/critique/   (failure and adversarial evidence)
             └─ retro/issue/...   (history, decisions, and external closeout)
```

Measured on 2026-08-25: `docs/` contains 44 Markdown pages; the composite docs
gate passes its syntax, reference, graph, and link components; the graph reports
`orphans=0`, `islands=0`, and
`largest_component_ratio=1.0`. The capability inventory reports 20 public
skills, 2 support skills, and 12 integrations, with the consumer-validator
catalog at `status: pass` (14 consumer-facing validators). Source/plugin
mirrors were regenerated and compared after the setup and achieve changes.

This is structurally healthy but not fully prose-freshness-proven. The topology,
ownership boundaries, generated mirror, and required status/source metadata are
green. The gates do not claim that every sentence remains freshly re-researched;
dated plans and working records stay under `charness-artifacts/` when they stop
being current.

## Migration Slice

1. Add `docs/index.md` as the canonical index and make `docs/README.md` a
   compatibility pointer. **Done 2026-08-25.**
2. Update root README, docs-graph guidance, and the awiki integration fact to
   name `docs/index.md`. **Done 2026-08-25.**
3. Add documentation principles to root `AGENTS.md` and the setup profile.
   **Done 2026-08-25.**
4. Flatten the former convention/generated pages and add status/source metadata
   to current docs. **Done 2026-08-25.**

## Acceptance

- `docs/index.md` is the only canonical index named by README, AGENTS, setup,
  docs-graph guidance, and integration metadata.
- `docs/README.md` remains reachable as a compatibility pointer and is not a
  second independently maintained index.
- The root AGENTS policy distinguishes evergreen docs, generated docs, live
  handoff state, and artifact history, and names the doc-as-code gates.
- `check_doc_links.py`, `check_docs_graph.py`, `validate_skills.py`, and the
  relevant quality suite pass; no page is claimed current merely because it is
  reachable.
- No stale roadmap or historical artifact is deleted or moved without a
  source-of-truth classification and updated inbound links.

## Non-Claims

This slice does not claim that every sentence is freshly re-researched or that
active roadmaps are product truth. It does claim the repository's current docs
surface is flat, linked, and governed by the composite docs receipt; history
and superseded concepts remain clearly classified under `charness-artifacts/`.
