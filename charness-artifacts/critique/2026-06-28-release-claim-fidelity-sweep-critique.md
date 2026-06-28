# Release Critique — charness per-skill claim-fidelity calibration sweep + shipping fixes

Date: 2026-06-28
Reviewer: bounded fresh-eye subagent (standalone, read-only), per release `critique-boundary`
Range: `origin/main..HEAD` (36 commits atop v0.56.9; 111 files, +3206/-249)

## Scope

These 36 commits ship one dominant internal workstream plus a small set of operator-visible
fixes. The internal bulk is a per-skill Cautilus claim-fidelity calibration sweep across all
20 public skills: 25 static fixture specs under `evals/cautilus/*-claim-fidelity/spec.json`, a
new validator (`scripts/claim_fidelity_lib.py` + `scripts/validate_claim_fidelity_specs.py`), a
registry (`evals/cautilus/claim-fidelity-registry.json`), a methodology spec under
`charness-artifacts/spec/`, and rolling `docs/handoff.md` updates. Riding alongside and actually
shipping to installed users: SKILL.md point-of-need routing refinements (`ideation` step 1 →
`concept-architecture.md`, `narrative` step 6 → `brief-shape.md`, `find-skills` step 4/5 routing
note), three behaviour bug fixes (handoff namespaced-bare `/charness:handoff` chunker bypass,
gather provider-host redirect doc, find-skills `next_step` recommendation field), a CEAL→`acme`
portability de-leak across ~49 files, and a "Quality round five" test/script-speed pass.

## Readiness Verdict

**ready-with-notes.** The body is coherent and internally consistent; no half-applied work, WIP,
or debug leftovers were found. The plugin mirror is fully in sync, version state is uniform at
0.56.9 (pre-bump), and the no-live-capture status is honestly carried in the handoff, registry,
and every spec `_comment`. The only notes are (a) the bump level is a genuine judgment call and
(b) the calibration is explicitly unproven (static) — a documented non-claim, not a defect.

## Bump Recommendation

**patch.** Under `references/version-policy.md`, the operator-visible deltas are all patch-class —
three runtime/behaviour bug fixes that preserve the same public shape (handoff chunker regex,
gather doc, find-skills `next_step` additive field) and wording/metadata routing refinements that
propagate to installed users (`ideation`/`narrative`/`find-skills` SKILL.md point-of-need
pointers). The eval calibration, validator, registry, and methodology spec are internal quality
scaffolding not shipped to the operator runtime. Why it is debatable: the find-skills `next_step`
field is a small *additive* surface, which the policy lists under `minor`. It lands on **patch**
because `next_step` is a non-breaking enrichment of an existing recommendation payload (no new
command, skill, or install surface; existing callers unaffected; it is stripped from the canonical
inventory), making it a runtime correction rather than an adoptable new capability. If the
maintainer reads `next_step` as a meaningfully new behaviour worth advertising, **minor** is
defensible — stated explicitly rather than defaulted.

## Findings

- **Coherence / no leftovers:** secret-scan and WIP/debug-marker scan over the full diff returned
  only legitimate hits (the `check-secrets` gate name, "token review" prose, policy-describing
  rationale strings). No `TODO/FIXME/breakpoint/console.log` introduced. Largest commit
  (`247084fe`, +1923) is the bulk fixture add — expected. No empty commits.
- **Plugin mirror sync — clean:** byte-identical between `skills/`+`scripts/` and
  `plugins/charness/` for every changed surface spot-checked (`ideation`/`narrative`/`find-skills`/
  `issue` SKILL.md, `claim_fidelity_lib.py`, `gather_plan.py`, `chunked_routing_lib.py`).
- **find-skills `next_step` correctly scoped:** emitted only when a ranking exists; stripped by
  `inventory_artifact.py:_canonical_inventory` so a no-ranking run yields an identical canonical
  artifact (current-pointer no-op preserved).
- **handoff chunker fix sound:** the negative lookahead lets `/charness:handoff` fall through to
  chunked routing; covered by the 3 intent-keyed scenario split.
- **CEAL de-leak intentional and bounded:** the remaining `ceal` tokens are the documented
  protected set (adapter examples, frozen dogfood log, domain-blindness guard, in-flight WS-3a/3b
  narration). Test rename `test_ceal_lesson_propagation` → `test_skill_lesson_durability` is clean.
- **New gate wired:** `validate-claim-fidelity-specs` is queued in `scripts/run-quality.sh` (and
  the plugin mirror) and backed by `tests/quality_gates/test_claim_fidelity_specs.py`.
- **User-visible surface — no false claim:** README makes no version/skill-count assertion this
  release would falsify. Version strings are uniform at 0.56.9 across `plugin.json` (claude/codex),
  `packaging/charness.json`, and `.claude-plugin/marketplace.json`; the bump is the only
  version-state change the release still needs.
- **Real-host scope:** the diff touches NONE of the adapter's `real_host_required_path_globs`
  (README.md, docs/host-packaging.md, integrations/tools/**, scripts/doctor*, install/sync/update
  scripts), so the real-host checklist is not triggered by this slice — record real-host-proof as
  not-applicable for this release.

## Irreversible-Boundary Risks

- **None found** in the content. No secrets, no unintended/oversized/empty files, no newly leaked
  private host identifiers (the de-leak *reduces* leakage). Nothing here is costly to walk back.
- Standard release-time reminder (process, not content): the tag/push/GitHub-release publish is the
  irreversible boundary. Per the north star, confirm the published release through a different
  observer/channel (read back the published GitHub release + installed manifest version) rather
  than treating a green tag push as proof. The 4 manifest version strings must bump together.

## Non-Claims

- **NO live Cautilus captures were run.** The entire 20-skill claim-fidelity calibration is
  **static** — reasoning + per-skill fresh-eye critique only. Carried honestly in the handoff
  (`No live captures run yet`), the registry description, and every spec `_comment`.
- **All fixture `thresholds` are intentionally unset.** A documented, deliberate non-claim;
  empirical validation via live `/charness:<skill>` captures is the pinned next phase
  (ask-before-run, one at a time, per the Cautilus eval-only contract).
- `debug` is a deliberate lens-5 capture-context non-claim (its fixture is not faithfully runnable
  against a clean repo by design). This release ships the calibration *methodology and static
  specs*, not validated runtime claim-fidelity numbers.
