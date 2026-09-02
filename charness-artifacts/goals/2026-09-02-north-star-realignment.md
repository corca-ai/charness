# Achieve Goal: Realign the repo to its north star: consumer-facing skills, repo-only tooling, and docs that are treated like code

Created: 2026-09-02
Planning record: mutable until Goal Binding; the binding freezes these exact bytes.

## Goal
Make the charness checkout serve its stated purpose (consumers develop with less rework, faster) by separating what ships to consumers from what only this repo needs, and by restoring the documentation to a single current-state wiki. Concretely: `docs/` holds only current contracts and every page carries a verified date; AGENTS.md states the docs-as-code principles and README is a user guide linked from the index; every production subprocess spawn goes through `subprocess_guard` and no repo script re-spawns another repo Python script; tests import repo scripts in-process unless a real process or Git boundary is declared; the `quality` skill exports only what checks a consumer repo's health via gates and intelligence, while repo-only gates live in a non-exported tooling tree; `scripts/` is organised into concept packages whose gates cover subdirectories and shell files; and consumer rework is observed through the operator's own issue filing rather than a new gate. Success is a wrong answer's escape path closed and a concept made clearer, never a line or gate count.

## Starting Truth (2026-09-02 audit)

Measured in this session; each number is the reason a slice exists.

| Surface | Observation |
| --- | --- |
| `docs/` | 43 files. `north-star-overhaul-roadmap.md` complete since 2026-06-20 (goal artifacts `Status: complete`) but `docs/index.md:64` calls it "active roadmap" and `docs/operator-acceptance.md:5` "plan of record". Six more self-described working records live in `docs/`. `readme-proof.md` cites README sections "Workflow Routes" and "Core Concepts" that no longer exist. 40 of 43 pages lack `Last verified`. The irreversible-boundary definition is restated in `operating-contract.md` and `impl/SKILL.md` without a link to the north star. Three dead script citations. |
| AGENTS.md / README | AGENTS.md lacks the four docs-as-code principles (dedup, wiki links, README minimal for users, AGENTS.md minimal to `docs/index.md`); operator approved adding them. README claims are all true but omit supported hosts, prerequisites beyond Python, what install does to the machine and how to undo it, and what skills the user gets. `docs/index.md` does not link README. |
| Production subprocess | 205 spawn sites in `scripts/`, `skills/`, `native/`. ~87 git, ~13 cargo/gh/rg/cosmic-ray, 19 self-invocations of this repo's own Python (14 replaceable by `import_repo_module`), 7 hardcoded `"python3"`. Only 16 sites use `scripts/subprocess_guard.py`; 189 bypass its timeout and process-group kill. |
| Test subprocess | 289 of 565 test files use `subprocess`; 193 spawn `python3` on a repo script; 91 use the in-process loaders. `boundary_contract` marker has 11 adopters. Enforcement is staged-lines-only plus a `no_increase` baseline (`scripts/boundary-bypass-baseline.json`), so the 193 never converge. |
| `quality` skill | References 199 scripts; the other 19 public skills reference ~118 combined. `run-quality.sh` is 1341 lines with 97 queued gates and is not length-gated because `check_code_lengths.py` gates `.py` and Rust only. Of 397 `scripts/` files, 299 are reachable from both a shipped skill and the quality lane; 32 are quality-lane-only; 7 surfaces-only; 12 tests-only; 2 unreferenced. Export exclusion is a 3-item tuple `SOURCE_ONLY_PLUGIN_SCRIPTS` in `packaging_lib.py`. |
| `scripts/` layout | 385 `.py` + 12 `.sh`, flat. Name clusters: check_/validate_ ~106, mutation 15, coverage 12, worktree 14, review 14, lessons 14, hooks 10, packaging 7, `_lib` 96. ~50 single-star `scripts/*.py` globs across gates would silently drop a subdirectory from the gated universe (the S40 failure in the 2026-07-28 triage sweep). `import_repo_module` assumes flat names; no `scripts/__init__.py`. No Python file-level dead-code gate: knip is absent, the vulture advisory is default-off and always exits 0. |
| Test allocation | `spec` 8, `impl` 4, `prove` 5, `create-cli` 0 test files; quality/release/mutation/coverage-named tests 150+; tests-about-tests 4231 LOC. |
| Rework signal | usage-episode instrumentation was removed as unmeasurable. No current instrument. |

## Non-Goals

- Rebalancing test coverage toward `spec`, `impl`, `prove`, `create-cli`. Recorded as the follow-up goal this run makes visible; not a slice here.
- Rewriting any skill's behaviour. Slices move, delete, or re-scope; they do not redesign what a skill does.
- Replacing git porcelain calls with a library. The ~105 external-binary spawns stay as spawns, routed through the guard.
- A new gate that measures consumer rework. The instrument is the operator's issue filing plus a retro read.
- A target line count, gate count, or file count. Counting fewer of anything is a north-star failure signature.
- Changing `charness-artifacts/` policy or pruning its 5000 files beyond what a slice moves into it.

## Boundaries

- **Per-surface migration, never bulk deletion.** Before a gate, doc, or test moves or dies, its slice names the failure mode it catches today and shows the replacement catches a seeded instance. One-line rollback ref per surface.
- **AGENTS.md and CLAUDE.md** change only under the operator's explicit approval, given 2026-09-02 for the four docs-as-code principles. Any further AGENTS.md change is a new approval.
- **Gate scope repair precedes any subdirectory.** No file moves under `scripts/` until the single-star globs are recursive and `.sh` is length-gated, so no surface leaves the gated universe silently.
- **Export boundary is a proof surface.** Changing what `packaging_lib.py` exports is authoring a proof surface (north star P5): it needs a distinct-observer review and a clean-export probe before the slice closes.
- **Irreversible provider writes** (issue creation, closeout, release) go through the issue-owned Goal Run and release workflows, never from a slice directly.
- **Historical artifacts are not rewritten.** The 2026-08-07 critique's "scripts/ has no subdirectories" premise is recorded as invalidated by the packaging slice, not edited.
- **Each slice runs the standing lane green before handoff** and reads which checks it skipped; a skipped gate is not a passed gate.

## User Acceptance

- Opening `docs/index.md` shows only current contracts, generated references, and the README; every `docs/` page carries a `Last verified` line that `check-docs.sh` enforces.
- AGENTS.md carries the four docs-as-code principles in a form recognisably derived from the craken-agents guide; README tells a new user which hosts are supported, what install writes and how to undo it, and what skills they get, without duplicating a `docs/` page.
- `grep -rn "subprocess\." scripts skills native` shows spawns only inside `subprocess_guard.py`; no repo script spawns another repo Python script; a form check refuses a new bypass.
- `grep -rln "sys.executable\|\"python3\"" tests` lists only files carrying `boundary_contract`, and `scripts/boundary-bypass-baseline.json` no longer exists.
- A clean export of the `charness` plugin contains no repo-only gate; `run-quality.sh` in the consumer export runs only checks that answer "is this consumer repo healthy".
- `scripts/` has concept packages; `check_code_lengths.py` and every other gate report the same file universe before and after the move, with `.sh` included.
- Two unreferenced and any unjustified tests-only scripts are gone, and a file-level unreferenced-script check runs in the standing lane.
- A retro can read `gh issue list --label rework` and attribute each to a skill; the operator has filed at least one such issue against this goal to prove the path.

## Agent Verification Plan

### Low-Cost Checks

- `scripts/check-docs.sh` green, including the new `Last verified` rule and a seeded page without it failing.
- `python3 -m pytest` standing lane green with skip list read.
- AST count of spawn sites outside `subprocess_guard.py` equals zero after slice 3; seeded bypass refused.
- Reference-graph rerun (same method as the audit) shows zero unreferenced `scripts/` files and reports the per-package universe.

### High-Confidence Checks

- Gate-universe parity: before and after each move, `check_code_lengths.py --list` and every glob-driven gate emit identical sorted file sets (plus `.sh` after slice 2). A moved file that vanishes from any set blocks the slice.
- Seeded-failure proof per relocated gate: one intentionally broken fixture per moved gate still turns red from its new location.
- `pytest --collect-only` count unchanged across the test in-process migration; per-file runtime not worse than the subprocess version.
- Fresh-eye review of the export-boundary change and of the quality-skill scope decision, by a distinct observer, recorded in a critique artifact.

### External or Live Proof

- Clean consumer install from the exported plugin on a throwaway repo: `charness doctor`, `charness update`, and a `quality` run complete without referencing a repo-only gate. Recorded by the operator or a task run, not asserted from the source checkout.
- Release lane (`run-quality.sh --release`) green on the integrated tree before the parent closes.

## Slice Plan

| Slice | Objective | Why Now | Dependencies |
| --- | --- | --- | --- |
| 1 docs-as-code | Add the four principles to AGENTS.md and expand `documentation-principles.md`; retire the roadmap, six records, and `readme-proof.md` to `charness-artifacts/`; fix the two "active" references; add `Last verified` to every page and enforce it in `check-docs.sh`; single-source the irreversible-boundary definition; fix three dead citations; rewrite README as a user guide and link it from `docs/index.md`. | Every later slice and every future session reads these pages first; a stale roadmap plans finished work. Reversible, half a day. | none |
| 2 gate-scope repair | Make every `scripts/*.py` single-star glob recursive; add `.sh` to `check_code_lengths.py` with a cap and a seeded failure; add a standing file-level unreferenced-script check (reference graph over skills, adapters, hooks, scripts, tests); delete the 2 unreferenced scripts; disposition the 12 tests-only scripts. | Subdirectories and a 1341-line shell file must not escape the gated universe; this is the precondition for slices 4 and 5. | 1 |
| 3 subprocess retroactive removal | Replace 14 self-invocations with `import_repo_module`; remove 7 hardcoded `"python3"`; route all remaining production spawns through `subprocess_guard`; add a form check refusing new bypasses. For tests: read each file's recorded reason first (`scripts/boundary-bypass-exemptions.txt` adjudications, `boundary_contract` reasons, test docstrings), keep one spawn where the process boundary is the claim (`__main__` dispatch smoke, exact exit/stderr contract, child-exit-on-parent-death, env-scrubbed export self-sufficiency, targets that themselves spawn git), migrate the rest to the in-process loaders, mark every kept spawn `boundary_contract` with its reason, then delete the ratchet baseline and exemptions file because the marker now carries the adjudication. | Operator decided retroactive removal; a forward-only ratchet never converges. Mechanical, largest file count, best done before files move. | 2 |
| 4 quality boundary and run-quality decomposition | Classify all 97 gates by the question "which consumer rework does this prevent"; move repo-only gates to a non-exported tooling tree with directory-based export exclusion; turn the `run-quality.sh` queue into a declarative gate list with a thin runner; re-scope `quality` SKILL.md and adapter to the consumer definition. Fresh-eye review of the export boundary. | The 75% overlap between shipped and repo-only scripts is the root of the flat layout and the 199-script skill; decide the concept before moving files. | 2, 3 |
| 5 scripts packaging | Move `scripts/` into concept packages (gates, mutation, coverage, worktree, review, lessons, hooks, packaging, core libs) with `scripts/__init__.py` and dotted `import_repo_module` support; parity check per package; record the invalidated "no subdirectories" premise. | Follows the boundary from slice 4 so each file moves once. | 4 |
| 6 rework instrument | Add a `rework` label convention and a causing-skill line to the issue skill's filing template; teach retro to read `gh issue list --label rework` and attribute per skill; operator files one real instance. | Gives slice 4's classification and every future gate debate a consumer-side fact. Small; last so it observes the new layout. | 4 |
| 7 integrated closeout | Clean consumer export and install proof, release lane green, distinct-observer review of the export boundary, parent Goal Run closed through its readback path. | Proves the composition once. | 1–6 |

## Discuss Before Activation

- Discuss before activation: none — the three consequential decisions below were resolved with the operator on 2026-09-02 and are recorded under Interview Decisions.

## Context Sources

- `docs/design-north-star.md` — the governing standard; P1–P5, the boundary definition, taste ladder, failure signatures.
- `docs/documentation-principles.md`, `docs/artifact-policy.md`, `charness-artifacts/spec/2026-08-25-docs-architecture-evergreen.md` — current docs contract and the migration record that already asked for the roadmap's retirement.
- `../craken-agents/AGENTS.md` Documentation Guide — the four principles to adopt.
- `scripts/subprocess_guard.py` — the guard whose docstring records the 30-minute silent hang.
- `pyproject.toml` markers `boundary_contract`, `slow_corpus`, `release_only`; `scripts/boundary-bypass-baseline.json`; `scripts/check_staged_test_boundaries.py`.
- `scripts/check_code_lengths.py` `GATED_GLOBS`; `scripts/packaging_lib.py` `SOURCE_ONLY_PLUGIN_SCRIPTS`; `scripts/check_export_self_sufficiency.py`.
- `scripts/run-quality.sh` — 97 queued gates; the dead-code advisory comment at line 995.
- `charness-artifacts/critique/2026-08-07-issue-492-493-494-resolution-critique.md:81` — the "no subdirectories" premise this goal invalidates.
- `charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md` S40 — zero-file glob pass.
- `charness-artifacts/quality/history/2026-07-03-pytest-suite-test-value-audit.md` — measured redundancy, not allocation.
- `.charness/quality/runtime-signals.json` — standing lane ~119 s, release lane ~298 s; runtime is not the problem.
- Lesson ledger seed `north-star-realignment`: `skipped-is-not-passed`, `goal-closeout-evidence-binding`, `global-probe-for-local-fact`, `bar-recorded-as-prose`.

## Interview Decisions

- 2026-09-02, operator: the craken four principles go into AGENTS.md; explicit approval given.
- 2026-09-02, operator: README stays a public user guide, linked from `docs/index.md`, no duplication with `docs/`.
- 2026-09-02, operator: `subprocess_guard` is kept and applied everywhere if useful, else removed. Agent recommends keep; the guard encodes a measured failure.
- 2026-09-02, operator: subprocess use is removed retroactively as far as possible.
- 2026-09-02, operator: consumer rework is observed via the operator's own issue filing; usage-episode instrumentation was tried and dropped as unmeasurable.
- 2026-09-02, operator: `run-quality.sh` length is abnormal; repo-only gates may be split out of what consumers receive.
- 2026-09-02, operator: consumer `quality` means "check that the repo is healthy and propose, via gates and via intelligence".
- 2026-09-02, operator: the slice order docs → gate scope → subprocess → quality boundary → packaging → rework instrument is accepted.
- 2026-09-02, operator: repo-only tooling lives in a root `tools/` tree excluded from export by directory. Alternatives: `scripts/dev/` with a per-directory exclusion list (rejected: the list drifts); a separate repository (rejected: gates read this repo's code, so version sync cost exceeds the boundary gain). Reason: the export rule becomes "everything under `scripts/` ships" with nothing to maintain.
- 2026-09-02, operator: the test in-process migration happens in slice 3 before packaging, with the condition that each file's recorded reason for spawning is read and honoured, not overridden. Alternative: migrate per package inside slice 5 (rejected: pushes the subprocess removal behind the boundary decision and enlarges the packaging slice). The recorded reasons found today: `__main__` dispatch smoke, exact exit/stderr contract, child-exit-on-parent-death, env-scrubbed export self-sufficiency, targets that spawn git themselves.
- 2026-09-02, operator: test reallocation toward `spec`, `impl`, `prove`, `create-cli` stays a non-goal and becomes a follow-up goal once slice 6 has collected rework instances to justify what to test.

## Plan Critique Findings

- Risk: slice 4's gate classification could be answered "this repo" for gates that actually protect consumers who also run the release lane. Mitigation: each classification names the consumer failure mode or the repo failure mode, and a fresh-eye reviewer reads the list before any move.
- Risk: the in-process test migration erases a boundary that was the claim under test, or silently changes behaviour for scripts that mutate global state or call `sys.exit`. Mitigation: the recorded reason is read per file before migration; a spawn kept for a named reason carries `boundary_contract(reason=...)`; `pytest --collect-only` count and per-file pass parity are the slice's blocking check; an in-process migration that needs `sys.path` filtering to pass is refused (lesson `global-probe-for-local-fact`).
- Risk: recursive globs widen gate universes and surface latent violations in files that were never gated. Mitigation: slice 2 records the delta as a baseline read, fixes or exempts each by name, and never lands a silent widening.
- Risk: moving six records out of `docs/` breaks inbound links from skills. Mitigation: `check-docs.sh` and `check_export_self_sufficiency.py` run per move; links are updated, not left dangling.
