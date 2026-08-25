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
- `docs/index.md` is the one flat-wiki entry point. New evergreen topic pages
  live directly under `docs/`; an existing nested tree is preserved until an
  explicit migration proves links and ownership.
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

- `docs/README.md` is a substantial, coherent index, but it is named contrary
  to the setup contract and several machine-readable messages still call it
  canonical.
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
        │                              ├─ conventions/ (policy)
        │                              └─ generated/   (producer-owned output)
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

Measured on 2026-08-25: `docs/` contains 44 Markdown pages; the link gate and
graph gate both pass; the graph reports `orphans=0`, `islands=0`, and
`largest_component_ratio=1.0`. The capability inventory reports 20 public
skills, 2 support skills, and 12 integrations, with the consumer-validator
catalog at `status: pass` (14 consumer-facing validators). Source/plugin
mirrors were regenerated and compared after the setup and achieve changes.

This is structurally healthy but not fully freshness-healthy. The topology,
ownership boundaries, and generated mirror are green. The existing gates do not
yet prove that every one of the 44 pages carries current status/source-of-truth
metadata or that its prose remains factually current. Several pages are active
contracts; dated plans and working records (notably the north-star roadmap and
older initiative notes) still need a page-by-page narrative classification
before they can be safely moved or deleted.

## Migration Slice

1. Add `docs/index.md` as the canonical copy of the current index and make
   `docs/README.md` a compatibility pointer.
2. Update root README, docs-graph guidance, and the awiki integration fact to
   name `docs/index.md`; preserve fixture references that intentionally test a
   missing path.
3. Add the documentation principles to root `AGENTS.md` and the setup profile
   so consumer repos inherit the same evergreen/source-of-truth policy.
4. Add status/source-of-truth metadata to the canonical index and the two live
   exceptions (handoff and operator acceptance); classify the roadmap before
   moving or deleting it.

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

This slice does not claim that every existing page is factually current, that
the roadmap is obsolete, or that a consumer's nested docs can be flattened
without an explicit migration. A later quality/narrative pass must classify
remaining pages and choose any moves.
