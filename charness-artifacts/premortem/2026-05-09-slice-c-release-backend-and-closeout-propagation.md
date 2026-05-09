# Premortem — Slice C: Release Backend + Closeout-Discipline Propagation

Date: 2026-05-09
Decisions under review:

- **Item 10.1 (release backend adapter)** — `release_backend` field added
  to release adapter (default `{id: gh, binary: gh, commands: null}`),
  mirrors the `issue_backend` shape from #122. New `backend_command` helper
  in `publish_release_helpers.py` resolves `auth_check`/`release_view`/
  `release_create` ops with `{tag}`/`{title}` substitution for both
  adapter-supplied templates and the default `gh` shape. Three previously
  hardcoded `gh` calls now route through the backend.
- **Item 10.2 (cross-skill closeout-discipline)** — new shared reference
  `skills/shared/references/closeout-discipline.md` lifts the three
  `issue/references/closeout-discipline.md` patterns (Verified Ledger,
  Target Durability, External-Source Identity) into a skill-agnostic home.
  The issue-specific file cites the shared abstract while keeping its
  concrete `gh issue view` examples.
- **Item 10.3 (external-source identity propagation)** — `announcement`/
  `narrative`/`handoff` SKILL.md gain a workflow-step anchor citing the
  External-Source Identity section plus a References-list cite.
- **Item 10.5 (durable target propagation)** — `release`/`gather`/
  `announcement` SKILL.md gain a workflow-step anchor citing Verified
  Ledger + Target Durability sections plus a References-list cite.

## Success Criteria

- Existing release publish flow stays byte-compatible with default backend
  (verified: 8 `test_release_publish.py` tests still pass with the same
  fake-gh fixture).
- Custom `release_backend` parses, validates, and resolves command
  templates with substitution.
- 5 consumer skills cite the shared closeout-discipline ref via References
  + workflow-step anchor.
- Plugin manifests stay synced; full test sweep stays green.

## Out of Scope

- CI / pre-push wiring of a new `release_backend`-required gate. Default
  shape preserves byte-compatibility; no gate change required.
- Creating standalone shared refs per pattern. Three sections in one shared
  ref is the right shape for narrative/handoff (which only use
  External-Source Identity) plus release/gather/announcement (which use
  Verified Ledger + Target Durability).
- Refactoring default templates into named constants. Defaults live at
  call sites; revisit when a fourth backend op lands.

## Angles + Counterweight

Bounded angle subagent + counterweight delegated under repo
`Subagent Delegation` clause. Triage:

- **Act Before Ship**: none.
- **Bundle Anyway** (both pulled in):
  1. `backend_command` only calls `.format(**subs)` on parts containing
     `{`, so a future caller with a literal brace in a non-substituted
     default no longer crashes with `KeyError`.
  2. `adapter-contract.md` placeholder list now names the current set
     (`{tag}`, `{title}`) and notes that adding a placeholder requires
     updating call-site kwargs and a regression test, matching
     `issue-backend.md` style.
- **Over-Worry**: shared-ref scope creep (lifting three patterns is
  right-sized; per-skill 3-4 line anchors are concrete enough to shape
  behavior); plugin manifest sync (verified by `validate_packaging_committed`
  via `plugin_preamble.py:root_install_surface.ok`).
- **Valid but Defer**: citation-chain test brittleness on literal substring
  assertions (intentional — that is the gate); default template
  duplication between helper and CLI (revisit when fourth op lands).

## Recurrence Prevention

- 8 release-backend tests + 7 propagation tests anchor the contract.
- Existing 8 release publish tests stay green via byte-compatible default.
- Plugin sync gate caught the `adapter-contract.md` mirror drift before
  the slice closed; verified after `sync_root_plugin_manifests.py` run.
- The `.format` brace guard removes a latent KeyError class for any
  future non-substituted default arg.
