# Next-session plan: close the release, then convert the remaining lists to properties

> Written at the end of the 2026-08-30 session, after Step 1 of
> `2026-08-30-next-session-plan.md` landed in full and four unplanned structural
> repairs landed with it.
> Supersedes `2026-08-30-next-session-plan.md`. Its Step 1 is DONE; Steps 2–5
> survive and are re-scoped below.
> Inputs: `charness-artifacts/spec/repograph-tool-control-plane.md`,
> `charness-artifacts/retro/session-retro-2.md`,
> `charness-artifacts/retro/2026-08-30-a-class-discharged-as-a-list.md`,
> `issue-753/2026-08-28-jtbd-audit-quality-gates.md`.

## Operator decisions and execution order (recorded 2026-08-29)

Taken with the operator at plan review, after measuring the tree. These settle
the open decisions below; where a decision contradicts the prose further down,
this section wins and the prose is the reasoning that led to it.

Measured state at review, which differs from what the prose below assumes:

- `origin/main` is `533f24dad`, the abandoned v8.0.0 prepare commit, and local
  `main` is **99** commits ahead (not ~96). Latest tag is `v7.0.0`.
- The ratio gate has **no headroom, not "exactly at the cap"**:
  `source_lines: 144799`, `test_lines: 144800`, `ratio: 1.0`,
  `status: within-max`. Test code is already one line ahead and passes only on
  rounding. A handful of added test lines trips it.
- `release-changed-line-coverage` takes its base from
  `merge-base(origin/main, HEAD)` (`scripts/release_changed_line_coverage.py:118,272`),
  which is `533f24dad`. So the 11-file block IS the unpushed 99 commits, and
  pushing would empty the range and clear the gate without paying anything. It
  is a blocking gate in release order (`tests/quality_gates/support.py:376`).

Decisions:

1. **Version stays 8.0.0**, deliberately and not by inheritance. The retirement
   is a large removal with no consumer-visible artifact loss.
2. **Pay all 11 changed-line-coverage files BEFORE the release.** The push-empties-
   the-range shortcut is refused: the range would clear by erasing the
   measurement, not by covering the lines.
3. **Ratio relief comes from the production side, starting with the release
   machinery** (52 scripts / 12,599 lines; `_publish_and_finalize` at
   `publish_release_execute.py:225` is unreachable in production with three
   test-only callers). Not from the `#753` trim list, and NOT by raising the cap.
   **The reduction is not limited to dead code.** The operator explicitly
   accepted that this may shake the keystone: live release paths may be
   restructured before the release runs, not only after. Deleting a reachable
   path is in scope when the path does not earn its lines. The release run then
   doubles as the proof — a wrong cut shows up as a failed release gate in the
   same session, which is why the reduction goes first rather than last.
4. **Session scope is Step 1 + Step 2.** Steps 3–5 only if they fit.
5. **Push the 99 commits** — the remote is idle on the abandoned prepare and
   nobody is building on it. Fast-forward.
6. **Codex lanes carry both review and separable implementation**
   (`charness task run`, `--effort xhigh`; review as two lanes with materially
   different perspectives). Serial execution is fine when the work only yields
   one lane — do not manufacture a second lane for the shape of it. The parent
   keeps design, integration, final verification, and the release body itself.
7. **A blocked release gets its gate fixed and pushed through**, not abandoned.
   No second abandonment record.
8. **Step 2 builds no new gate registry.** Reuse the existing gate list at
   `tests/quality_gates/support.py:376` and the quality-runner manifest as the
   single source. The prose below suggests "the honest first move may be to
   build one"; that is now conditional — a registry may be authored ONLY after
   demonstrating, concretely, that the existing sources cannot enumerate the
   gates the property must range over. Deleting a stale surface beats adding a
   parallel one.

**Amendment (same session, after measurement).** Decisions 3 and 4 above did not
survive their own evidence, and the operator replaced them:

- Removing production lines alone RAISES `test/source`. Headroom is
  `(deleted test lines) - (deleted production lines) - 1`, so dead-code removal
  costs headroom. Deleting `_publish_and_finalize` (82 lines) would have put the
  ratio at 1.00057 and broken the gate it was meant to relieve.
- Its three tests cannot be deleted either. `_publish_and_finalize` and the live
  `resume_publish` both call `common.run_release_closeout_tail`
  (`publish_release_execute.py:295`, `publish_release_resume_publish.py:218`), and
  the resume tests STUB that tail (`test_release_resume_edge_coverage.py:147`). So
  `test_release_distinct_channel.py:410-467` is the only execution coverage of the
  irreversible issue-close ordering, reached through a dead driver. Repoint, do not
  delete. STILL OPEN.
- A ten-subsystem JTBD audit of the release machinery found no defensible cut:
  nine verdicts of `earns-its-lines`, and the single `oversized` verdict
  (adapter/backend) was refuted with live consumers the assessor missed. Caveat on
  method: the refutation pass ran only against cut proposals, so the `keep`
  verdicts are NOT adversarially verified.
- The real defect was the cap's enforcement posture, not the code it measures.
  `2026-06-19-gate-buy-vs-build-triage.md:36-38` ranked the hard cap the repo's
  strongest DROP candidate; #420 demoted it to advisory on 2026-07-08 and its
  critique warned at `:28` that nothing pinned the flag;
  `issue-753/lane-A-ratio-surface-brief.md:37` said the posture was a LATER #753
  decision; `4122f6cd0` promoted it to blocking the next day at ratio 0.993.
- **Resolution: `--advisory` restored at `run-quality.sh:1171`, and the posture is
  now pinned by `test_ratio_gate_stays_advisory_in_the_runner` with a negative
  control.** The tree is now measurably OVER the cap (144826/144799 = 1.0002) and
  says so as a visible WARN. Adding that pin test is itself what tipped it, which
  is the hazard the gate's own `--advisory` docstring names.

Revised order: cap posture (DONE) → cover the 11 files → release 8.0.0 → Step 2.
No release-machinery reduction is required or justified.

Original order, which is NOT the section order below — decisions 2 and 3 chain:
release-machinery reduction (relief, live paths included) → cover the 11 files →
release 8.0.0 → Step 2. Step 2 is the first thing to drop if the reduction
yields less than the coverage work consumes.

The reduction going first is deliberate and load-bearing three ways: it is the
only sanctioned source of ratio headroom, the release run is what proves the
cuts, and a cut made after the release would ship unverified. The cost of the
ordering is that a bad cut surfaces as a failed release gate — which decision 7
says to fix and push through, not to retreat from.

## Read this first

Read `charness-artifacts/retro/recent-lessons.md` BEFORE planning. `AGENTS.md`
now routes to it as the first "Start here" item, because until 2026-08-30
nothing did: eight modules produced, validated, ranked, deduped, and scored that
digest and it reached no session. The 2026-08-30 session spent a day
rediscovering a lesson that was already sitting in it with three sources.

Then the two operating lessons that session paid for:

> **A verification failure is investigated by suspecting the verifier first.**
> Carried over from the 2026-08-30 plan, and it paid again: "21 files need
> changed-line coverage" was really "the instrument measured nothing", a
> one-line fix instead of 21 files of work.

> **Discharging a class by repairing its known instances leaves the class
> intact.** Ask what property the instances violate and check that instead, over
> the whole corpus, with a negative control proving the check can fire. This is
> `docs/design-north-star.md` P3 stated operationally; the repo was on the wrong
> side of it in at least four places.

And the mechanical one, because it cost 30 minutes:

> Run tests through `python3 scripts/run_standing_pytest.py --repo-root .`
> (add `--pytest-target <path>` for focused runs). A bare `python3 -m pytest` is
> now REFUSED for a broad selection by `tests/conftest.py`; that guard exists
> because nothing else made the cost visible.

## What landed on 2026-08-30

Five commits, `a21bba5a1`..`5d71f3380`:

1. **The native-core distribution layer is retired.** 4,200 lines out, 1,163 in.
   `repograph` is `integrations/tools/repograph.json` (`doctor_policy: required`,
   built with `cargo install --path .` from the crate in the checkout).
   `scripts/native_gate_lib.py` is the single resolver: override → dev-tree →
   installed, building and announcing when the crate is unbuilt or stale.
2. **`tests/conftest.py` refuses a broad serial pytest run** that bypasses the
   canonical runner.
3. **`tests/quality_gates/test_a_manifest_field_is_not_what_the_control_plane_derives.py`**
   checks what the control plane DERIVES from every manifest, with negative
   controls.
4. **`AGENTS.md` routes to the lessons digest.**
5. **The changed-line coverage gate actually measures pytest now.**
   `_COVERAGE_ENV_KEYS` was missing `COVERAGE_FILE`, so nothing inside pytest or
   its xdist workers was measured at all. Blocked set 21 → 12.

## Step 1 — Ship the release (the keystone, and it is now unblocked)

Everything that blocked it is gone. `packaging/charness.json` carries no
`native_core` declaration, `plugin.schema.json` carries no `nativeCore`
definitions, and the release adapter's `real_host_checklist` item 1 is a
`repograph` tool-doctor item instead of a native-artifact readback.

State to confirm before starting: `origin/main` is ~96 commits behind local
`main`, there is no `v8.0.0` tag and no GitHub release, and
`charness-artifacts/release/latest.md` is an ABANDONMENT record carrying
`- target version: 8.0.0` with no prepared marker, so a fresh run is unblocked.

Open decisions for the operator, early:

1. Does 8.0.0 remain the version, given the release it was prepared for was
   halted and its headline feature was then deleted? The retirement is a large
   removal with no consumer-visible artifact loss (nothing was ever published),
   so 8.0.0 is defensible; say so deliberately rather than by inheritance.
2. `origin/main` is ~96 commits behind. Confirm that pushing that range is
   intended and that no one else is building on the remote.

## Step 2 — Convert the remaining enumerated refusals to properties

The highest-value carry-over from the 2026-08-30 pattern analysis, and the
`Sibling Search` follow-up `deferred sweep-rows-to-properties`.

Three gates pin the rows a 2026-08-01 sweep contained rather than the property
those rows violate:

- `tests/quality_gates/test_empty_scope_refusals.py` — states the rule outright
  (*"a gate that compared nothing must say so, and must not exit 0"*) and pins
  four observed gates.
- `tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py` —
  sweep rows S9, S10.
- `tests/quality_gates/test_a_refused_verdict_states_its_refusal.py` — sweep
  rows S23, S2.

The 2026-08-30 defects were all new instances of this class, authored after the
sweep. Convert at least the first: a property over every gate script that can
report a scope, not over the four that were caught. Expect this to be harder
than the manifest case — "every gate" has no single registry, and the honest
first move may be to build one. Do not over-tighten: the sweep artifact records
a deliberate asymmetry (a *discovered* empty set is a real answer and stays a
cheap no-op), and a property that erases that asymmetry makes every commit pay
for every artifact family.

Also carry `deferred env-subset-reexport-audit`: `_with_coverage_env` builds a
full env and forwards a hand-listed subset. That shape is not gated anywhere and
it is what silenced a blocking gate.

## Step 3 — #748 slice 2: `match_surfaces` → native projection

Unchanged in substance from the 2026-08-30 plan; the release gate it was waiting
on is Step 1 here. The three deferred audit obligations were verified at line
level on 2026-08-29 and still hold:

- `staged_commit_gate_plan.py:230-235` catches `SurfaceError` and returns `[]`,
  a silent pre-commit disarm. Binary-unavailability must raise a type **not**
  derived from `SurfaceError`.
- `boundary_probe_lib.py:132` calls `match_surfaces` with no handler and
  deliberately propagates.
- `path_matches_patterns` survives at `surfaces_lib.py:105,109` inside
  `_validate_surface`'s generated-markdown validation — manifest
  self-consistency, a different job. Slice 2 cannot claim single-matcher
  ownership; record it.

## Step 4 — `repo_file_listing.py` decision

Unchanged; the investigation is complete and the answer is evidence-backed.
`CHARNESS_SUPPORT_DIR` has one production read site (`scripts/repo_layout.py:17`)
and one live operator-facing doc; no adapter, hook, CI step, skill script, or
`run-quality.sh` path ever sets it. When set, `skills/support/` patterns are
globbed against the external tree with no git filter
(`repo_file_listing.py:123-128`). Choose: absorb the splice into the native
owner, keep Python with the reason recorded, or deprecate it.

## Step 5 — #753 closeout, with a correction to the audit

The JTBD artifact's candidate list is **partially executed and does not say so**:
`test_prescribed_path_self_test_guidance.py` and `test_retro_skill.py` were
already deleted by an earlier session, and `test_issue_audit_brief.py` was
deleted on 2026-08-30 to restore the test-production ratio. Remaining:

- convert-pin (2): `test_narrative_adapter.py`,
  `test_quality_tool_recommendations.py`
- trim-partial (8): `test_critique_skill.py`,
  `test_issue_closeout_discipline.py`, `test_narrative_scenario_blocks.py`,
  `test_quality_bootstrap.py`, `test_quality_skill_docs.py`,
  `test_retro_memory.py`, `test_skill_docs_contracts.py`,
  `test_source_bound_records_guidance.py`

Cite the artifact's per-file line ranges; do not paraphrase them. **And record
execution state in the artifact as rows are done** — a list whose done-ness is
untracked is the same defect one level up, and it cost a wrong assumption on
2026-08-30.

**Two blocking gates now pull in opposite directions, and the tree sits exactly
on the boundary.** `release-changed-line-coverage` demands tests for changed
lines; `check-test-production-ratio` caps total test code at 1.00× production.
Observed on 2026-08-30, in this order: retirement removed more production than
test code → 1.0002 over-max → deleted a self-disclaiming test → 0.9996 → covered
this session's own changed lines (five tests, `native_gate_lib.py` 89% → 100%)
→ 1.0002 over-max again → executed two documented #753 rows → **1.0000, exactly
at the cap**.

That is not a comfortable place to start a session. The next test file added
tips a blocking gate, and the only currently-sanctioned relief is the #753
trim list, which is finite. Before adding tests, either trim a documented row
first or raise the question with the operator — but do NOT raise the cap to make
room, which is the treadmill `2026-05-20-quality-treadmill-vs-root-cause.md`
already named. The real relief is production-side: `charness` is 6,081 lines and
the release machinery is 12,599, so the denominator has more slack in it than
the numerator does.

## Accumulated follow-ups

- **`charness` is 6,081 lines and `build_recommendation` maps it to 123 test
  files even after the 2026-08-30 narrowing** (it was ~400). Any "focused" or
  "changed-line" claim that touches the CLI still degrades toward "most of the
  suite". This is a topology problem, not a gate problem, and it is the largest
  remaining structural item. `check-changed-line-mutation-coverage` is a 289s
  unbudgeted hotspot because of it.
- **`release-changed-line-coverage` blocks on 11 files** against base
  `533f24dad` (the v8.0.0 prepare), now that the coverage instrument works. This
  is real debt from ~93 commits, not an artifact: the pre-repair list of 21 was
  mostly instrumentation, and `scripts/native_gate_lib.py` left the list once
  its own changed lines were covered (89% → 100%).

  Intersected against `git diff --name-only a21bba5a1~1..HEAD`, exactly ONE of
  the 11 is from the 2026-08-30 session — `charness`, five lines (994, 4530,
  4531, 4533, 4534), the deliberately-kept uninstall residue cleanup and one
  release-probe default. The other ten (`task_run_*.py` ×7,
  `check_standalone_imports.py`, `check_test_production_ratio.py`,
  `validate_inference_interpretation.py`, `check_real_host_proof.py`) predate
  it.

  Those five were left uncovered ON PURPOSE, and the reasoning is the ratio
  tension above: adding a test for them trips `check-test-production-ratio`,
  which then costs another documented #753 trim row, and clearing 1 of 11 does
  not unblock the gate anyway. Clear this as one deliberate slice with the
  ratio in view, not opportunistically.
- **In-process bounded-reviewer delegation has failed five times across two
  sessions**, once with the explicit `opus` override. `.agents/claude-host.md`
  now records that an unreturned review is an unrun review. Either find a
  channel that delivers (the dynamic workflow channel is untested for this in
  the last two sessions) or stop budgeting reviewer spawns as proof.
- `follow-up: release-machinery-jtbd-audit` — `_publish_and_finalize`
  (`publish_release_execute.py:225`) is unreachable in production with three
  test-only callers; 52 release scripts / 12,599 lines plus 36 test files /
  15,336 lines to bump a version, tag, push, create a release.
- `follow-up: seam-fake-real-argv-audit` — every repo fake standing in for an
  external binary (`gh`, `repograph`, `nose`).
- **`charness task run` receipts do not carry the lane's final message** (#754
  family).
- `publish_release_helpers.py` sits near its hard cap;
  `test_release_resume_edge_coverage.py` at 798/800.
- The retro persistence helper names artifacts without the date prefix the
  scaffold suggests (`session-retro-2.md`, not `2026-08-29-session-retro-2.md`).
  The validator accepts it; the two surfaces disagree about naming.

## Working shape

The 2026-08-30 session ran parent-only with design-critique subagents, and the
subagents delivered nothing three times. What actually found every defect was
the parent running a disconfirming probe against the real repository:
`json.load` on the gate's own output, `coverage report` on one file, an
instrumented hook, `cargo --version` in two directories. Budget for that, not
for a second opinion.

Commit before running the battery. Two full cycles on 2026-08-30 were spent on
the parent's own uncommitted state: `tests/repo_copy.py:63` copies the WORKING
TREE, and `git ls-files` still lists worktree-deleted files, so a dirty tree
fails ~16 tests for reasons that have nothing to do with the change.

Regenerate derived surfaces AFTER the last source edit, not before:
`python3 scripts/sync_root_plugin_manifests.py --repo-root .` and
`./charness catalog refresh --repo-root .`. Adding a retro artifact also
requires `python3 scripts/build_retro_lesson_selection_index.py --repo-root .
--write` followed by `python3 skills/public/retro/scripts/refresh_recent_lessons.py
--repo-root .` — a two-step chain whose first refusal names only the first step.
