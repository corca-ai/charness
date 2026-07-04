# Gate Reclassification Audit (2026-07-04)

One-time classification pass over the gate-script mass named in
[docs/design-north-star.md](../../docs/design-north-star.md): the mass grew
~51.5K -> ~54.9K lines (259 -> 270 files) in the two weeks *after* the
2026-06-20 diagnosis, and the standing floor-addition-restraint detector did
not see new gate **files** (only new blocking sites inside files already
tracked) — see `scripts/slice_closeout_advisories.py`
`new_gate_script_findings`, extended in this same PR to close that gap.

A second governing input, alongside the north star, was added mid-audit by
operator directive:
[charness-artifacts/gather/2026-07-04-enforcing-quality-of-ai-generated-code.md](../gather/2026-07-04-enforcing-quality-of-ai-generated-code.md)
(operator-mandated gather record, "Enforcing the quality of AI-generated
code"). It records an endorsed combination of deterministic quality floors
specifically against AI-authored-code failure modes — file/function length
caps, cognitive-complexity limits, code duplication as an error, test-coverage
floors, dead-code detection, test-to-production ratio caps, and
scheduled/ratcheted mutation testing — and the claim that these tools must be
**combined** because each counterbalances another's evasion mode (coverage
without a ratio cap -> unbounded test count; dedup pressure without complexity
limits -> unbounded logic complexity). See `## Operator Overrides` below for
the concrete consequences for this audit's dispositions.

**Scope.** Only gate phases *actually wired* in
[scripts/run-quality.sh](../../scripts/run-quality.sh) (the broad `A` path) and
[scripts/staged_commit_gate_plan.py](../../scripts/staged_commit_gate_plan.py)
(the commit-boundary `B` path, including its
`staged_commit_gate_plan_helpers.py` and the pulled timing-layer / leak-scan
subsets) are enumerated — not all 270 `scripts/*.py` files. A gate present in
both is marked `A+B`; `B`-only entries are new commit-boundary-only structural
gates `A` never runs standalone.

**Tags.**

- `boundary`: `irreversible` (a wrong PASS propagates outside this session's
  editable state — a consumer repo installs a broken export, a secret leaks, a
  vulnerable dependency ships, a GitHub issue closes), `reversible` (a wrong
  pass stays inside locally-fixable working state), or `form` (cheap
  structural well-formedness — P5-licensed teeth even though the boundary
  itself is not irreversible).
- `current-teeth`: `blocking` (a non-zero exit fails the phase / commit) or
  `advisory` (the command is designed to exit 0 and only print
  `WARN`/`ADVISORY`), verified per gate against its actual invocation flags and
  script exit-code logic, not assumed from the label.
- `disposition`: `keep` / `demote` / `delete` / `already-handled-this-PR` /
  `review-needed` (used, per instruction, wherever I could not verify enough
  to be confident — an honest gap beats an invented one).

## Seed Dispositions — Verified

Four dispositions were seeded as seams other slices in this PR/branch
(`north-star-p123`) were expected to have already executed. Verified against
the current worktree rather than trusted on the seed alone:

| Seed claim | Verification | Disposition |
|---|---|---|
| `check_markdown_inline_code` -> demote | `scripts/check-markdown.sh:64-71` catches its non-zero exit and prints `WARN: ... (advisory; rendered output is correct, not blocking)` instead of failing the phase — confirmed demoted. The *rest* of `check-markdown` (`markdownlint-cli2`) is unaffected and still hard-fails. | **already-handled-this-PR** (inline-code sub-check only) |
| `check_python_lengths` hard arm -> demote | **Superseded by operator override** (see below) before this could settle as `already-handled-this-PR`. Original verification (module-length arm demoted at both wiring sites) is preserved as history in `## Operator Overrides`. | see `## Operator Overrides` |
| `check_premortem_rename` / `check_init_repo_rename` -> delete | Both `.py` files (and their allowlists) no longer exist under `scripts/` (only stale `__pycache__` entries and the as-yet-unsynced `plugins/charness/scripts/` mirror remain — mirror re-sync is a separate `mutate -> sync` phase, not this slice's job). No reference to either in `run-quality.sh` or `staged_commit_gate_plan.py`. | **already-handled-this-PR** (source deleted, un-wired) |
| `check_test_production_ratio` -> delete | **Superseded by operator override** — the operator affirmed its value; it is back and wired, see below. | see `## Operator Overrides` |
| `check_skill_cut_safety` -> wire+keep | **Confirmed, landed.** `scripts/skill_cut_safety_advisory.py` (new file) wraps `check_skill_cut_safety.deleted_skill_surfaces` and is composed into `run_slice_closeout.py`'s `_predict_commit_advisories` at `run_slice_closeout.py:416-422` (`_rca_link_advisory.provider(...) + _skill_cut_safety_advisory.provider(...)`), which feeds `staged_commit_gate_plan.py`'s `run_predict_commit(..., advisory_provider=...)`. It is wired as a non-blocking **REVIEW** advisory (exit 0 always; prints "REVIEW: staged deletion of a skill contract surface..." per `skill_cut_safety_advisory.py:30-46`), not a blocking `GateCommand` — the file's own module docstring and a `# floor-addition-restraint:` comment (`skill_cut_safety_advisory.py:26-29`) explicitly justify keeping it advisory rather than a hard block, so an intentional/justified skill-surface deletion is never hard-blocked. | **wired+keep (this PR)** — confirmed present with file:line evidence above. |

## Operator Overrides (2026-07-04, post-initial-pass)

Two operator directives arrived after the first pass above and change two of
the seeded dispositions. Both were re-verified against the (shared, actively
being edited) worktree rather than recorded on the operator's word alone.

1. **`check_test_production_ratio` -> KEEP, not delete.** Operator: "exists to
   prevent AI-generated test code from bloating relative to production code."
   Verified: `scripts/check_test_production_ratio.py` exists again (it had
   been deleted, then restored — presumably by a sibling wave reacting to the
   same operator input) and is wired at `run-quality.sh:480`:
   `check-test-production-ratio ... --require-git-file-listing --advisory`.
   The script's own `--advisory` flag (confirmed at `check_test_production_ratio.py:146-181`)
   demotes a ratio-cap breach (`DEFAULT_MAX_RATIO = 1.0`, i.e. 100%, in the
   100-120% band the gathered article names) to a `WARN:` line instead of
   raising `RatioError`. Recorded: **boundary=reversible, current-teeth=advisory,
   disposition=keep, reason="operator-affirmed guard against test-code bloat
   (2026-07-04)."**
2. **`check_python_lengths` hard arm -> KEEP-blocking, not demote** (supersedes
   the original seed and my first-pass `already-handled-this-PR` call). Per
   the gathered article, file/function-length caps are one of the
   operator-endorsed combination classes and are **not** P1-demote candidates
   by default even though they act on reversible work — demoting one now
   requires operator sign-off, which the original seed did not have.
   **Confirmed blocking at BOTH wiring sites, corrected from an earlier stale
   observation.** A fresh-eye review (`git diff HEAD -- scripts/staged_commit_gate_plan.py`
   is empty — byte-identical to HEAD — and `git log --oneline -S 'check-python-lengths (staged)'`
   shows that gate line was only ever touched by one commit, #266, never with
   `--advisory`) caught that I had recorded a **live inconsistency with more
   confidence than the evidence supported**: `run-quality.sh:418`
   (`check-python-lengths`, the broad `A` path) is blocking, and
   `staged_commit_gate_plan.py`'s `check-python-lengths (staged)` gate (the
   commit-boundary `B` path, currently at lines 263-274) is **also** blocking
   — it takes no `--advisory` flag in the current file or in any commit. What
   I actually saw was real: a sibling wave had **temporarily** added
   `--advisory` plus a north-star-P1-style comment to the `B`-side gate in the
   uncommitted working tree while a demotion was in flight, then fully
   reverted it before anything was committed. I observed that transient state
   honestly at the time, but the artifact then carried it forward as a
   settled, high-confidence "current state" claim after the ground had moved
   — exactly the single-channel-claim failure this audit exists to prevent.
   Recorded: **boundary=reversible, current-teeth=blocking (at both A and B),
   disposition=keep-blocking (operator override, 2026-07-04)**.

Per the operator's broader principle, every gate in the endorsed combination
classes named in the gather record (length/complexity caps, duplication,
coverage floors, dead-code detection, test/prod ratio, mutation testing) is
tagged `boundary=reversible, disposition=keep` below with a reason citing the
combination, not the default P1 reversible-work posture — see rows for
`ruff` (mccabe `C90`/`PLR0915`), `dup-ratchet`, `check-coverage`,
`check-changed-line-mutation-coverage`, and `check-test-production-ratio`.

## A. Gates wired in `run-quality.sh` (grouped by concern)

| Gate(s) | Wired in | Boundary | Current teeth | Disposition | Reason |
|---|---|---|---|---|---|
| `validate-skills`, `validate-skill-ergonomics`, `check-skill-contracts`, `check-skill-bootstrap-vars`, `check-bootstrap-shim-consistency`, `check-cli-skill-surface` | A+B (ergonomics/contracts/bootstrap-vars/bootstrap-shim also pulled to commit time) | form | blocking | keep | Cheap structural/contract checks; already the #332 fail-fast structural-sweep class, not a churn source. |
| `check_skill_cut_safety` (wired as an advisory, not a `GateCommand`) | wired via `run_slice_closeout.py --predict-commit`'s advisory-provider chain (`scripts/skill_cut_safety_advisory.py`, not `staged_commit_gate_plan.py` directly — see Seed Verification for exact file:line) | form | **advisory** (exit 0 always; REVIEW-severity nudge on staged skill-contract-surface deletions) | keep (wired+keep, this PR) | Deliberately kept advisory rather than a blocking floor (own `# floor-addition-restraint:` comment) — an intentional, justified skill deletion must never hard-block; matches P5's forces-a-question-not-completion posture. |
| `check-doc-links`, `check-markdown` (markdownlint-cli2 half), `check-command-docs`, `check-public-doc-coupling`, `check-references-link-inventory`, `check-title-slug-drift` | A+B (doc-links/markdown/title-slug also pulled to commit time) | form | blocking, except `check-title-slug-drift` = **advisory** (explicit north-star P1 WARN posture, `staged_commit_gate_plan.py:85-88`) | keep | Cheap, deterministic doc-shape checks; title-slug already correctly demoted. |
| `check_markdown_inline_code` (sub-check inside `check-markdown`) | A+B | form | **advisory** (see Seed Verification) | already-handled-this-PR | — |
| `validate-cautilus-scenarios`, `validate-cautilus-proof`, `validate-cautilus-diagnostics`, `validate-cautilus-call-provenance`, `validate-public-skill-validation`, `validate-public-skill-dogfood`, `validate-claim-fidelity-specs` | A | form | blocking | keep | Deterministic policy-alignment floors, distinct from the Cautilus *run* itself (correctly ask-before-run/advisory per repo policy); matches `closeout-floors.md` §B precedent. |
| `validate-surfaces`, `validate-profiles`, `validate-presets`, `validate-adapters`, `validate-integrations` | A+B | form | blocking | keep | Cheap manifest-shape validators, distinct surfaces, low false-fire. |
| `validate-packaging`, `validate-packaging-committed`, `staged-plugin-mirror-drift` (B only), `check-plugin-import-smoke`, `check-export-safe-imports` | A (+B for mirror-drift) | **irreversible** | blocking | keep | Seeded: a broken export/mirror reaches consumer repos outside this session's control before it can be corrected (#257). |
| `validate-handoff-artifact`, `validate-debug-artifact`, `validate-debug-seam-index`, `validate-retro-lesson-index`, `validate-quality-artifact`, `validate-attention-state-visibility`, `validate-quality-closeout-contract`, `validate-critique-artifacts`, `validate-ideation-artifact`, `validate-retro-artifact`, `validate-current-pointer-freshness`, `check-current-pointer-writes`, `inventory-quality-handoff`, `check-artifact-shape (staged)` | A (+B for attention-state/current-pointer-freshness/artifact-shape) | form | blocking | keep | Closeout-artifact shape floors; `closeout-floors.md` §A already found this class absorb-shaped/low-churn, and the actual gate stays the enforcement. |
| `validate-usage-episodes`, `report-usage-episodes` | A | form | blocking (both have live `return 1` paths, verified) | keep | Deterministic usage-episode shape checks; despite the "report-" name, `report_usage_episodes.py` genuinely blocks on malformed input. |
| `validate-inventory-consumption`, `validate-inventory-consumption-declaration`, `check-inventory-declaration-coverage`, `validate-maintainer-setup` | A (+B for inventory-declaration-coverage) | form | blocking | keep | Cheap declaration/consumption-parity checks. |
| `check-python-lengths` (module-length hard arm) | A+B | reversible (operator-endorsed combination class, not default P1) | **blocking at both A and B** (confirmed via clean `git diff` + `git log -S`; see `## Operator Overrides` for the corrected observation history) | keep-blocking (operator override, 2026-07-04) | Length caps are an operator-endorsed AI-code-quality floor (gather record). |
| `check-test-production-ratio` | A | reversible (operator-endorsed combination class) | advisory (`--advisory` passed; script demotes a ratio-cap breach to `WARN:`) | keep | Operator-affirmed guard against test-code bloat (2026-07-04). |
| `check-python-filenames`, `check-python-runtime-inheritance`, `py-compile`, `ruff` | A+B (filenames/py-compile/ruff staged variants) | form for filenames/runtime-inheritance/py-compile; reversible (operator-endorsed combination class) for `ruff`'s complexity rules | blocking | keep | Cheap, deterministic Python hygiene. `ruff`'s `mccabe` (`C90`, max-complexity 15) and `PLR0915` (function statement-count cap) are exactly the cognitive-complexity / max-function-length controls the gather record's endorsed combination calls for — not a demote candidate (supersedes this row's earlier framing). |
| `validate-inference-interpretation`, `check-timing-layer-completeness`, `validate-quality-reference-catalog` | A+B | form | blocking | keep | The deliberate #332/#368 shift-left class — already fail-fast-first by design, not a churn source. |
| `check-spec-evidence-durability`, `check-seed-fixture-budget` | A | form | blocking | keep | Cheap, deterministic. |
| `check-secrets`, `check-supply-chain`, `check-supply-chain-online`, `check-github-actions` | A | **irreversible** | blocking | keep | Seeded: a leaked secret, a shipped vulnerable dependency, or a malicious/misconfigured CI workflow is not correctable after the fact. |
| `check-shell` | A | form | blocking (assumed; not individually re-verified beyond convention) | keep | Cheap shellcheck-class lint. |
| `check-links-internal` | A | form | blocking | keep | Cheap, repo-local. |
| `check-links-external` | A | form | blocking (assumed) | review-needed | Hits the network; a flaky external site can false-fire a commit-blocking gate on a surface this repo does not control — not independently re-verified whether it retries/degrades. |
| `pytest`, `check-test-completeness`, `check-boundary-bypass-ratchet`, `specdown`, `run-evals`, `doc-duplicates` (`--require-nose`, blocks only on tool-missing/stale, not on findings) | A (+B for run-evals) | form | blocking | keep | The final-bundle correctness-proof class; `closeout-floors.md` §B already blessed this as cadence-restrained, not a churn source. |
| `check-coverage`, `check-changed-line-mutation-coverage` (**advisory** by construction, non-blocking unless fresh coverage exists) | A | reversible (operator-endorsed combination class: coverage floors + scheduled/ratcheted mutation testing) | blocking (check-coverage) / advisory (mutation, by construction) | keep | Coverage and mutation-score gates are named explicitly in the gather record's endorsed combination — coverage without a ratio cap is one of the named evasion modes, so this pairs with `check-test-production-ratio` above, not a standalone P1 target. |
| `dup-ratchet` | A | reversible (operator-endorsed combination class: code duplication as an error) | **advisory** by design (comment: "advisory (never blocks) when the overlay/baseline/nose are missing"; blocks only the no-increase ratchet itself) | keep | Duplication-as-error is a named combination class (jscpd/nose analogue); correctly non-blocking only on missing tooling, not on found duplication. |
| `inventory-ci-local-gate-parity` (`--require-empty-parity-issues`) | A+B (B adds `--require-canonical-gate-match`, stricter) | form | blocking | keep | Cheap CI/local parity check; the B-side extra strictness only fires on workflow-file/timing-doc edits. |
| `inventory-gitignore-scan-hygiene` (`--require-empty`) | A | form | blocking (degrades to a skip-message print when the script is absent) | keep | Cheap, deterministic when present. |
| `inventory-sloc`, `inventory-cli-ergonomics`, `inventory-nose-clones` | A | reversible | **advisory** (verified: no `return 1`/`sys.exit(1)` path found) | keep | Genuinely informational; naming and behavior agree. |
| `inventory-ubiquitous-language` | A | reversible | **blocking** (verified: `return 1 if report["findings"] else 0`, unconditional — no opt-in flag) | review-needed | Naming/behavior mismatch: reads as an "inventory" (informational) gate but actually hard-blocks on any deprecated-terminology finding with no advisory posture. Not confidently keep or demote without knowing whether that was deliberate; flagged for maintainer judgment. |
| `measure-startup-probes`, `check-runtime-budget` | A | reversible | blocking (both verified `return 1` on failure) | keep | Dev-loop hygiene; low false-fire, cheap. |
| `agent-browser-runtime-baseline`, `agent-browser-runtime-hygiene` | A | reversible | blocking | keep | Opt-in only (env var or explicit `--labels` selection) — already the correct low-false-fire default-off posture. |

## B. Commit-boundary-only additions in `staged_commit_gate_plan.py`

Gates with no `run-quality.sh` equivalent — new structural checks that exist
*only* at the literal git pre-commit boundary.

| Gate(s) | Boundary | Current teeth | Disposition | Reason |
|---|---|---|---|---|
| `check-staged-reversion` | form | blocking | keep | Cheap staged-state sentinel; matches `closeout-floors.md`'s "Boundary/repo-copy ratchets" precedent. |
| `staged-worktree-consistency` (conditional on the script existing) | form | blocking | keep | Same family; degrades to no-op when the script is absent (portable). |
| `check-skill-core-headroom (staged)`, `check-artifact-shape (staged)` | form | blocking | keep | Relocates changed-surface shape verdicts to commit time — the describe-first-preflight pattern, not a new churn source. |

## Related gate outside the audited scope (seeded, noted for completeness)

`check_issue_closeout_commit_msg.py` (the "issue-closeout commit-msg" gate) is
wired in `.githooks/commit-msg`, **not** in either audited file — out of this
audit's stated scope, but seeded as `keep` and worth recording: boundary =
**irreversible** (governs the actual `Close #N` GitHub issue-close action),
current-teeth = blocking. Disposition **keep** stands; not re-litigated here
since the file itself was not in scope.

## Follow-ups

Demote/delete candidates, incomplete reversions, and missing tool classes
surfaced above but **not executed** in this PR:

- **Missing tool class: dead-code detection (combination gap, not a demote
  candidate).** The gather record names `knip`-style dead-code detection as
  part of the endorsed combination ("agents rarely delete code"). `pyproject.toml`
  already has a `[tool.vulture]` config section (`paths`, `min_confidence = 80`,
  `sort_by_size = true`) but `vulture` is **not wired into `run-quality.sh` or
  `staged_commit_gate_plan.py`** (confirmed: zero matches in either file or any
  githook) — configured but never actually run as a gate. This is the one
  concrete gap in the endorsed combination this repo's gate set does not yet
  close.
- **Cognitive-complexity limits: already satisfied, no gap.** The gather
  record names this as a combination class; `ruff`'s `mccabe` (`C90`,
  `max-complexity = 15`) and `PLR0915` already cover it (see the
  `check-python-lengths`/`ruff` row above) — no follow-up needed here.
- `inventory-ubiquitous-language` blocks unconditionally despite its
  "inventory-" naming convention (every sibling `inventory-*` gate in this
  audit is advisory). Worth a maintainer decision: rename for honesty, add an
  opt-in `--require-empty`-style flag to match its siblings, or confirm the
  blocking posture is deliberate.
- `check-links-external` hits the network at commit-time-adjacent broad-gate
  boundary with no independently-verified retry/degrade behavior; a flaky
  external site could false-fire a blocking gate on a surface outside this
  repo's control. Not reclassified here for lack of verification, per the
  review-needed policy above.
- The `plugins/charness/scripts/` mirror still carries the deleted
  `check_premortem_rename.py` / `check_init_repo_rename.py` and an unsynced
  `run-quality.sh`. This is expected drift under the
  `mutate -> sync -> verify -> publish` phase barrier (sync is a later,
  batched phase in this same PR), not a fresh finding requiring action here.
