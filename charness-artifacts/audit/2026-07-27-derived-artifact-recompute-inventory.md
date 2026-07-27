# Derived-Artifact Recompute Inventory — Foreign-Writable Artifact Dirs
Date: 2026-07-27
Status: inventory complete; the actionable subset is empty, and the shape-only
contract is now explicit (no enforcement added by this pass)

## Why this exists

The 2026-07-27 foreign-copy incident failed closed because the drift happened to
land in the one artifact validated by "recompute with this repo's own code and
compare bytes" — the retro lesson-selection index. Issue #463 asked the separate,
cause-independent question: of the artifacts a foreign or stale copy can write
into `charness-artifacts/{critique,probe,release,retro}/`, **which are purely
derived, and of those, which lack a recompute gate?** Only that subset is
actionable; the rest need an explicit "shape-only is the contract here" instead.

This file is the answer, so the question is not re-derived. It changed no
enforcement.

## Headline

**The actionable subset is empty.** Both purely derived artifacts in those four
directories already have a byte-compare gate. One family is covered by nothing at
all — `probe/*.md` — but it is agent prose, so the answer there is shape, not
recompute. Everything else is structurally
non-recomputable: its bytes embed agent prose, wall-clock timestamps, subprocess
output, live release URLs, or absolute host paths, so "recompute and compare"
has no defined meaning for it. Shape-only is therefore the contract for those
families by construction, not by omission.

## Inventory

| Artifact | Writer | Class | Current check |
| --- | --- | --- | --- |
| `retro/lesson-selection-index.json` | `scripts/recent_lessons_lib.py:460` `write_lesson_selection_index` | purely derived | **recompute-and-compare** (`recent_lessons_lib.py:484`) |
| `retro/recent-lessons.md` | rendered by `recent_lessons_lib.py:543`; written by `skills/public/retro/scripts/refresh_recent_lessons.py:55` and `scripts/retro_persistence_lib.py:119` | purely derived (see caveat below) | **recompute-and-compare** (`recent_lessons_lib.py:510`) |
| `critique/<slug>-packet.json` / `.md` | `scripts/critique_packet_lib.py:281-282` `write_packet` (built at `:122`) | partly derived | none over the packet as a whole; a conditional partial recompute of `reviewed_input_identity` + packet byte digest runs when a critique record declares the binding (`scripts/critique_reviewed_input_binding.py:29`) |
| `retro/<slug>-packet.json` / `.md` | same builder via [the retro prepare-packet runner](../../skills/public/retro/scripts/prepare_packet.py) | partly derived | JSON-parse only ([surfaces](../../.agents/surfaces.json), `retro-lesson-selection-index`) |
| `probe/*.json` host-log probes | no repo writer: `skills/public/retro/scripts/probe_host_logs.py:82` prints the payload built at `scripts/host_log_probe_lib.py:441` and the operator redirects it to a file | not derived from repo state | JSON-parse only (`probe-artifacts` surface) |
| `probe/*-release-observer.json` | `skills/public/release/scripts/release_observer.py:121` | not derived (run/host data) | write-time shape check (`release_observer.py:17`, invoked at `:114`) |
| `probe/*.md` host-log narratives | agent authored | not derived | **none**: the `probe-artifacts` surface globs `*.json` only |
| `release/latest.md` | `skills/public/release/scripts/publish_release_artifact.py:34` `write_release_artifact` | partly derived | shape + one claim: required headings and state-ledger labels (`audit_public_release_narrative.py:55-77`, reached via `:117`), and `- target version:` cross-checked against three manifests (`scripts/validate_current_pointer_freshness.py:160`) |
| `release/*-notes.md`, `*-real-host-proof.md` | agent/human authored | not derived | mutable-tag audit only (`audit_public_release_narrative.py:85`) |
| `critique/<date>-*.md`, `retro/<date>-*.md` | agent prose; retro records land through `scripts/retro_persistence_lib.py:82` `persist_retro_artifact` — the same path the foreign copy wrote through | not derived | shape validators (`validate_critique_artifacts.py`, `validate_retro_artifact.py`) |

Outside the four directories, one more purely derived artifact exists and is
already gated the same way: [the debug seam-risk index](../debug/seam-risk-index.json)
(`build_debug_seam_risk_index.py --check`). Families outside these directories
were not surveyed; `capability-catalog` is byte-stable by design
(`scripts/capability_catalog_artifact.py:56` reuses the existing `generated_at`
when content is unchanged), so a repo-wide version of this question has a
different answer and is not claimed here.

Caveat on `recent-lessons.md`: a third writer,
`skills/public/setup/scripts/seed_retro_memory.py:68`, writes hand-written stub
bytes the byte-compare gate would reject. It is write-if-missing and setup-only,
so the gate holds in this repo, but "purely derived" is a statement about the
steady state, not about every writer.

The machine-visible surface entries do not yet say any of this. `critique-artifacts`
and `probe-artifacts` record what the artifacts are for, not that shape-only is a
decision; `charness-artifacts/release/**` has no entry; and `retro/*.md` — which
matches `recent-lessons.md` — is listed as a *source* path while only the index
sits in `derived_paths`. Closing that gap is a follow-up, not a claim of this pass.

## Why the partly-derived families are not actionable as recompute gates

The packet families (`critique/`, `retro/` `*-packet.*`) have a fully derived
envelope — `kind`, `version`, `repo`, `section_count`, and each section's
`id`/`title`/`content_kind`/`producer` come from the checked-in adapter — but
their bytes also carry `generated_at` (`critique_packet_lib.py:152`) and the
stdout/stderr/exit code of adapter-declared producer subprocesses
(`critique_packet_lib.py:35-66`). A byte comparison over that is not a drift
detector; it fires on every re-run. A partial recompute limited to the
adapter-derived envelope is conceivable, but it would prove only that the
adapter was read correctly, which is not the failure mode the foreign-copy
incident exposed — that incident was a schema-version mismatch in a *fully*
derived artifact, and the gate that caught it exists precisely because such an
artifact can be reproduced exactly.

`release/latest.md` embeds today's date, the published release URL, host-proof
payloads, and runtime timings. Its one machine-checkable claim (the target
version) is already cross-checked against the three manifests, on top of the
required-headings and state-ledger-label checks in
`audit_public_release_narrative.py:55-77`. Note that
`charness-artifacts/release/**` has no [surfaces](../../.agents/surfaces.json)
entry at all, so neither check is wired into a declared surface; recorded here as
a visible fact rather than silently widened into a new gate by this inventory
pass.

The probe families read `~/.claude` / `~/.codex` and embed absolute `home` and
`repo_root` paths (`host_log_probe_lib.py:451-452`), so no other machine can
reproduce their bytes even in principle.

## What would change this answer

A new artifact under these directories that is a pure function of repo state.
The rule to apply then: if this repo's own code can reproduce the bytes, it gets
a recompute-and-compare gate at write time and a `--check` verify command on its
surface, following `build_retro_lesson_selection_index.py --check`. If it cannot,
the surface entry records shape-only as the deliberate contract.
