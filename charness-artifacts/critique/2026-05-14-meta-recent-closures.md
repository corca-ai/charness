# Critique — Meta-review of 2026-05-14 issue closures (#162 / #163 / #164)

- Execution: full (4 bounded fresh-eye subagents in parallel — 3 angles + 1 counterweight)
- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: `charness-artifacts/critique/2026-05-14-034620-packet.md`
- Target: `references/code-critique.md` (post-merge meta-critique of three landed closures)

## Change

Three issues closed today (2026-05-14 KST). All three already had their own
parent-delegated critique pass at the time of closure. This meta-pass tests
whether any concern slipped through *that* round and now deserves a follow-up.

- #162 announcement fan-out guidance — landed in `b4f99f4` (doc-only:
  `references/large-window-fanout.md` + 2 SKILL.md bullets)
- #163 find-skills bootstrap regression — landed in `df9072f`
  (`CHARNESS_SUPPORT_DIR` env override + `load_support_capability_schema`
  optional `repo_root` arg + 14 SKILL.md "Resolve `SKILL_DIR`" preambles)
- #164 portable delivery-handle chaining — landed in `b4f99f4`
  (`{parent_delivery_handle}` placeholder + JSON-line stdout contract +
  fail-fast + split-on-first-part rule)

## Diff Scope

Documentation + two narrowly-scoped loader changes. No new validators, no new
operator commands, no new tests beyond fixture-seeding.

## Angles

- Jackson (problem framing)
- Weinberg (diagnostic / root-cause layer)
- Gawande (operational checklist / silent failure modes)
- Counterweight (skeptical pushback — speculative consumer / premature lint)

## Findings

### Jackson — Problem framing
- #162: on-target. Reporter asked for "primitive, not hard rule"; got exactly
  that.
- #163: **partial**. Sub-ask (b) (loader accepting explicit path) landed; sub-ask
  (a) (bootstrap commands resolve `SKILL_DIR` themselves, OR a one-line
  preamble snippet, OR a `--skill-dir` flag) was reframed from "actionable
  seam" into operator homework. `skills/public/find-skills/SKILL.md:52-55`
  says *what* to resolve, not *how*.
- #164: on-target. Reporter's both sub-asks (placeholder + thread-reply split)
  landed.

### Weinberg — Diagnostic / root cause
- #163: **partial-cause**. Commit message names the root cause as "self-locating
  constants + unresolved shell vars" pattern. Fix repaired 2 of ~26 listed
  instances. Concrete peers that will recur the same failure class in a split
  monorepo:
  - `scripts/control_plane_lib.py:26` — `MANIFEST_SCHEMA_PATH` is a
    **module-level** constant. Import-time failure, no `repo_root` injection
    point. More severe failure mode than #163's actual case (which was
    lazy-loadable).
  - `scripts/control_plane_lib.py:41` (`load_lock_schema`), `:54`
    (`_plugin_fallback_root`), `:162` (`dependencies_schema_path` call site).
  - `scripts/packaging_lib.py:122-123,155` — `"./skills/support/"` literal
    substring replacement *silently no-ops* in split layouts (worse than
    failing loud).
  - `scripts/cautilus_adapter_lib.py:42-43`, `scripts/plan_cautilus_proof.py:29`,
    `scripts/markdown_preview_bootstrap_lib.py:28` — hardcoded
    `skills/support/...` paths that ignore `CHARNESS_SUPPORT_DIR`.
  - argparse defaults at `scripts/check_python_lengths.py:81`,
    `scripts/check_doc_links.py:350`, `scripts/check_export_safe_imports.py:78`.
  - Positive: all 19 SKILL.md files containing `$SKILL_DIR` did receive the
    preamble (grep for missing-preamble: zero hits).
- #162: **symptom layer** (doc-only, no scaffold/threshold detector). Reporter
  consented to this shape ("primitive, not hard rule").
- #164: **partial-cause**. The JSON-line contract is at the cause layer.
  `rg parent_delivery_handle scripts/` returns zero hits — no validator. Next
  adapter author can re-introduce the bug class and pass `quality`.

### Gawande — Operational checklist
- #163: **silent failure unchanged**. A fresh-shell operator who pastes the
  bootstrap block from `find-skills/SKILL.md:59-65` still hits
  `python3: can't open file '/scripts/list_capabilities.py'` because the
  preamble does not give an executable resolver. The fix renamed the bug from
  "undefined variable" to "operator must invent a resolver"; the bounce-off
  rate is unchanged for the doc-layer ask. This converges with Jackson.
- #164: **new silent failure surface**. No worked `post_command_template`
  example shows JSON emission. Operator who hardcodes
  `{parent_delivery_handle}` in a thread_reply template without making the
  parent script emit JSON gets either fail-fast (if no JSON line at all) or
  a literal placeholder posted (if the seam tolerates absence). No validator
  catches this at adapter-load time.
- #162: **measurement gap**. "Large enough" has no operator-checkable
  threshold (commit count, token budget, source count). A primitive without a
  measurable trigger tends to collapse to "do whatever feels right" → never
  fan out → identical complaint recurs.

### Counterweight — Skeptical pushback
- Most of #163's deferred siblings (5 peer self-locators, 12 hardcoded
  literals, monorepo fixture, lint rule) have no real alt-layout consumer
  yet — sweeping is speculative.
- #164 validator is a single-consumer surface — premature lint until a
  second adapter ships.
- #162 reporter explicitly bounded the ask; expanding scope rewrites their
  intent.
- The "Bundle Anyway 사후 발견" repeat trap fires only when an item belongs
  in the same touched file/function at one-line cost — not when it would
  expand to N call sites or build a new validator.

## Counterweight Triage

### Act Before Ship (1)

1. **#163 doc-layer ask under-shipped — add an executable `SKILL_DIR`
   resolver to the 14 SKILL.md preambles.** Jackson + Gawande converge with
   the *original reporter's own pain*, restated. The current preamble at
   `find-skills/SKILL.md:50-55` is the documentation-of-the-problem the
   reporter complained about, not a fix at the doc layer. Counterweight's
   "no observed pain" rebuttal does not apply: the reporter's pain *is* the
   signal. Smallest viable fix: one-line resolver in each of the 14 files,
   e.g. `SKILL_DIR="${SKILL_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)}"`,
   **or** the lighter form of pointing operators at `--repo-root .` style
   absolute paths the way `scripts/resolve_skill_path.py` already supports.
   Either way, the operator gets an executable line, not a verb.

### Bundle Anyway (1)

1. **#164: worked JSON-line example in `delivery-seams.md` Chaining Outputs**
   (~3 lines, e.g., a `jq -c '{delivery_handle: .ts}'` tail). Bundle into the
   next announcement-adapter slice. Cheap, prevents the silent-placeholder
   regression Gawande named.

### Valid but Defer (3)

1. **`{parent_delivery_handle}` adapter validator** (warns when
   `post_command_template` lacks the placeholder while `outputs` declares a
   `thread_reply`). Add to handoff item 5 — fire when a second adapter
   consumer or first observed misuse appears.
2. **#162 fan-out telemetry / `--fanout-hint` from `collect_commits.py`**
   (e.g., emit `window=N commits, M sources` so the operator can apply the
   primitive intentionally). Defer until first reporter says "fan-out
   guidance exists but wasn't applied".
3. **`MANIFEST_SCHEMA_PATH` module-level import-time risk
   (`control_plane_lib.py:26`).** Distinct from the other deferred peers
   because it's import-time, not lazy. Track separately in handoff item 5
   with the note "split-monorepo import will fail before any env override
   can take effect" — converts to Act Before Ship the moment a split-layout
   consumer is observed.

### Over-Worry (3)

1. **Sweep all 5 peer self-locators + 12 hardcoded `skills/support` literals
   in #163's deferred list.** No alt-layout consumer beyond the one reporter,
   and that reporter's blocker was the support-schema lookup which now has
   an env escape. Expanding scope without signal violates implementation
   discipline.
2. **SKILL.md lint rule rejecting bootstrap blocks with unresolved
   `$SHELL_VAR`.** Single-consumer surface, no drift signal. Premature lint.
3. **Monorepo-layout fixture across every `repo_layout.py` resolver.** Zero
   monorepo consumer in this repo's CI matrix; build when a second consumer
   asks.

## Defect Class Cross-Link

- "Bundle Anyway 항목을 사후에야 발견" (`charness-artifacts/retro/recent-lessons.md`)
  applies to the **Act Before Ship** item above: the executable resolver was
  the natural one-line companion to the "Resolve `SKILL_DIR`" preamble in
  the same 14 files. Per the repeat-trap definition, it belonged in the
  original slice and is being found post-hoc here.

## Capability Gap

None new. The Act-Before-Ship is a doc edit in existing surfaces; the
Bundle-Anyway is a doc edit in an existing reference; deferred validators
would belong in existing `scripts/announcement_adapter_lib.py` /
`scripts/check_skill_contracts.py`.

## Deliberately Not Doing

- Filing a new GitHub issue for the doc-resolver gap — surfacing here as an
  Act-Before-Ship follow-up for the maintainer to land in the next slice,
  not a re-open of #163.
- Expanding #163's fix to the 24 listed peers without a real alt-layout
  consumer signal.
- Adding a fan-out threshold to #162 — reporter explicitly asked for a
  primitive, not a rule. Wait for the dogfood that says "guidance exists
  but wasn't applied".
- Mutating the 14 SKILL.md files in this critique slice — that is the
  next slice's work, not a meta-critique side effect.

## Post-Ship Action

1. **Land** (next slice, ~30min): executable `SKILL_DIR` resolver line in
   the 14 SKILL.md files updated by `df9072f`. Same-file blast radius,
   matches reporter's named ask, closes Jackson + Gawande's convergence.
2. **Record** (handoff item 5 follow-ups for #162/#163/#164):
   - `MANIFEST_SCHEMA_PATH` import-time risk (escalation trigger: split-layout
     consumer observed).
   - `{parent_delivery_handle}` adapter validator (trigger: second adapter
     consumer or first misuse).
   - `collect_commits.py --fanout-hint` (trigger: dogfood "guidance not
     applied").
   - Worked JSON example for delivery-seams Chaining Outputs (bundle into
     next announcement-adapter slice).

## Fresh-Eye Coverage Note

Each reviewer ran in an isolated subagent context. Jackson + Gawande
independently converged on the same #163 doc-layer concern from different
angles, raising confidence that the Act-Before-Ship is real signal, not a
single-reviewer artifact. Counterweight's pushback successfully demoted
the bulk of #163's deferred peer-sweep concerns to Over-Worry.
