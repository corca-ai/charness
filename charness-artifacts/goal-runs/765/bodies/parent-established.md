## Situation

Charness exists to reduce rework in the repositories that consume it and to make agentic development there fast. A read-only audit of this checkout on 2026-09-02 found that the repository's own structure no longer reflects that purpose: the shipped `quality` skill carries this repository's entire gate machine, `scripts/` is a flat tree of 397 files with no boundary between consumer-facing code and repo-only tooling, subprocess use is pervasive in both production and tests despite an in-process idiom, and `docs/` mixes current contracts with completed project records.

## Experience

A new session reads `docs/index.md`, finds `north-star-overhaul-roadmap.md` labelled "active roadmap", and plans work that closed on 2026-06-20. A consumer installs the plugin and receives 199 quality scripts, most of which police this repository's release lane rather than their own repo's health. A maintainer wants to add a subdirectory under `scripts/` and cannot, because about 50 single-star globs would silently drop it from every gate. A test author wants to import a script in-process and finds a forward-only ratchet that grandfathers 193 files forever.

## Evidence

| Surface | Measured 2026-09-02 |
| --- | --- |
| `docs/` | 43 pages; 40 lack `Last verified`; 1 retired roadmap called active in 2 places; 6 self-described working records; `readme-proof.md` cites README sections that no longer exist; 3 dead script citations |
| AGENTS.md / README | AGENTS.md lacks the docs-as-code principles; README omits hosts, prerequisites, install effects, undo, and the skill list; `docs/index.md` does not link README |
| Production subprocess | 205 sites; 19 re-spawn this repo's own Python (14 pure habit); 7 hardcoded `python3`; 189 of 205 bypass `scripts/subprocess_guard.py` |
| Test subprocess | 289 of 565 files use subprocess; 193 spawn `python3` on a repo script; 91 use the in-process loaders; ratchet policy `no_increase` |
| `quality` skill | 199 scripts referenced vs ~118 for the other 19 public skills; `run-quality.sh` 1341 lines, 97 gates, exempt from the length gate because `.sh` is not covered |
| `scripts/` | 385 `.py` + 12 `.sh`, flat; 299 of 397 reachable from both a shipped skill and the quality lane; 32 quality-lane-only; 12 tests-only; 2 unreferenced; no file-level dead-code gate (knip absent, vulture advisory default-off) |
| Rework signal | usage-episode instrumentation removed as unmeasurable; no current instrument |

Planning record: `charness-artifacts/goals/2026-09-02-north-star-realignment.md`.

## Impact

Machinery that does not prevent consumer rework is cost, by the north star's own definition. Today the cost lands on every new session (stale planning surfaces), every consumer install (repo-only gates shipped), and every maintainer change to `scripts/` or `tests/` (flat layout, non-converging ratchets). Refactoring further inside the current boundaries makes the same machine tidier without changing who it serves.

## Desired outcome

- `docs/` holds only current contracts and every page carries a verified date; AGENTS.md states the docs-as-code principles; README is a user guide linked from the index.
- Every production spawn goes through `subprocess_guard`; no repo script re-spawns repo Python; tests import in-process unless a declared boundary is the claim.
- The `quality` skill exports only what checks a consumer repo's health via gates and intelligence; repo-only gates live in a root `tools/` tree that is not exported.
- `scripts/` is organised into concept packages whose gates cover subdirectories and shell files; unreferenced scripts are detected.
- Consumer rework is observed through the operator's own issue filing and read by retro.

Success is a wrong answer's escape path closed and a concept made clearer, never a line, gate, or file count.

## Ownership contract

- Goal Draft owns approved intent, boundaries, and slice design. Goal Binding owns the frozen identity. This parent owns the current-child cursor. Work Item issues own routine implementation state and behavioural proof.
- Per-surface migration, never bulk deletion: each moved gate, doc, or test names the failure mode it catches and proves the replacement on a seeded instance.
- Gate-scope repair precedes any subdirectory under `scripts/`.
- The export boundary is a proof surface: distinct-observer review and a clean-export probe before that child closes.
- AGENTS.md changes only under the operator's explicit approval, given 2026-09-02 for the four docs-as-code principles.

## Work sequence

1. docs-as-code
2. gate-scope-repair
3. subprocess-retroactive-removal
4. quality-boundary-and-run-quality
5. scripts-packaging
6. rework-instrument
7. integrated-closeout

## Completion criteria

- Every child provider-closed with behavioural evidence.
- Clean consumer install proof recorded from a throwaway repository.
- Release lane green on the integrated tree with the skip list read.
- Parent closed only through the guarded Goal Run close path after exact readback.

## Non-claims

- Test reallocation toward `spec`, `impl`, `prove`, and `create-cli` is a follow-up goal, not this run.
- No skill behaviour is redesigned; no git porcelain is replaced by a library.
- Push, tag, release publish, and installed-host mutation remain separately authorised.

## Membership digest rule

`current_membership_sha256` and `progress.membership_sha256` are the SHA-256 of the canonical JSON array of the parent's sub-issue numbers, sorted ascending, no whitespace, no trailing newline.

AI provenance: drafted and filed by an AI agent from the operator-approved Goal Draft and direct activation approval.
<!-- charness-goal-run:v1
{
  "binding_path": "charness-artifacts/goals/2026-09-02-north-star-realignment.binding.json",
  "binding_schema": "charness.goal-binding/v1",
  "binding_sha256": "20fdaf7e9a3e1489a308b11041555a9249b2e826d93d951f294a565b24d161cf",
  "bootstrap_verification": "verified-target-roundtrip",
  "current_membership_sha256": "06e46354f95d0ca5949f7816f641b083f1d19ac135e959dfb973730fac9819e1",
  "draft_path": "charness-artifacts/goals/2026-09-02-north-star-realignment.md",
  "draft_sha256": "129f065a28ce2c6a6a7fd7dc5f6ff2b63349b75ddf1ab62411ea4879ff8d2501",
  "initial_graph_sha256": "2473a6d41daf1b9c2b6ae24040670850f1ad1a0544cd7fa97fef056ca8ad8b62",
  "parent_identity": {
    "number": 765,
    "repo": "corca-ai/charness",
    "url": "https://github.com/corca-ai/charness/issues/765"
  },
  "progress": {
    "completed": 0,
    "membership_sha256": "06e46354f95d0ca5949f7816f641b083f1d19ac135e959dfb973730fac9819e1",
    "next": {
      "key": "docs-as-code",
      "number": 766,
      "repo": "corca-ai/charness",
      "state": "OPEN",
      "url": "https://github.com/corca-ai/charness/issues/766"
    },
    "open": 7,
    "revision": 1,
    "schema": "charness.goal-progress/v1",
    "total": 7
  }
}
-->
