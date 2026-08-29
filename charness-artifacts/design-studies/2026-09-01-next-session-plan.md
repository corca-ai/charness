# Next-session plan: one defect class across the consumer surface, and the Rust migration redesigned around what measurement said

> Written at the close of the 2026-08-29 session, with the operator.
> Supersedes `2026-08-31-next-session-plan.md`, whose Step 1 (the release) is
> still open and deliberately deprioritised: the operator's direction is
> "릴리즈가 당장 중요한 건 아니고 전체 이슈에서 중요한 건 다 잡고 가고 싶다".
> Inputs: `charness-artifacts/retro/2026-08-29-detector-blind-class.md`,
> the ten open issues, and the measurements recorded below.

## Read this first

Read `charness-artifacts/retro/recent-lessons.md` before planning.

The two lessons this plan is built on, both paid for on 2026-08-29:

> **When a plan's value rests on a quantity, measure the quantity before writing
> the plan.** Two long stretches last session were built on unmeasured premises —
> "reducing the release machinery buys ratio headroom" (the arithmetic runs the
> other way) and "the Rust transition is the speed fix" (native `match-surfaces`
> measured 1.4x SLOWER). Each was one command from being avoided.

> **Do not name an issue a blocker from its text.** The ledger carries this at
> score -2 across two sessions. Every severity claim below was checked against
> THIS repo's code, and the check changed two of them.

## The finding that shapes this plan

Three open issues are not three consumer bugs. They are one class, and it is the
same class the 2026-08-29 retro named:

**A mechanism renders a verdict about a question it never asked.**

- **#751** — `prepare_packet.py` emits a packet with `section_count: 0` when the
  adapter declares no `packet_sections`, and `run_review.py` tells the worker
  that packet is the authoritative review input. Verified live: `grep` for a
  `section_count == 0` refusal across `skills/public/critique/scripts/` returns
  NOTHING. This repo does not hit it only because its own
  `.agents/critique-adapter.yaml` happens to declare sections (`section_count: 3`
  when run today). In Ceal it produced two reviewers deferring on "no content" and
  zero semantic critique.
- **#752** — `scripts/worktree_doctor_lib.py:83,304`: `skip_if_doctor_passes`
  defaults to `True`, and `skills/public/setup/scripts/templates/worktree_adapter.yaml.txt:16`
  ships it `true`. A doctor that says nothing about dependency readiness still
  gates every declared `prepare.commands`. Ceal's two lockfile roots were both
  absent while the doctor reported PASS.
- **#709** — a published number whose only test asserts `0`. The projection can
  return zero for every input and the suite stays green. The issue body says it
  plainly: *"This is the sibling that was found and left."*

The repo already owns the property that answers all three. It is
`tests/quality_gates/test_empty_scope_refusals.py`: *a gate that compared nothing
must say so, and must not exit 0.* It was applied to gates and to nothing else —
not to review packets, not to doctors, not to projections. **The 2026-08-31 plan's
Step 2 was "convert enumerated refusals to properties"; the scope of this property
was itself an enumeration.**

## Step 1 — Extend the empty-scope property past gates, with #751 as the flagship

Order matters: repair the instance that has no consumer workaround first, then
generalise, then sweep.

1. **#751.** Refuse a packet that carries no semantic content, at the point where
   the worker prompt claims the packet IS the review input. A DISCOVERED empty
   set is a real answer elsewhere in this repo, so the refusal must distinguish
   "this adapter declares no sections" (a configuration the operator must resolve)
   from "sections were declared and produced nothing" (a producer failure). Both
   must be loud; neither may reach a worker as an authoritative-but-empty packet.
2. **#752.** The gate is not "did the doctor pass" but "does the doctor's coverage
   INTERSECT what prepare would do". A doctor with no dependency check cannot
   license skipping `npm ci`. Do not delete `skip_if_doctor_passes`; make the skip
   conditional on established coverage rather than on a verdict about something
   else.
3. **#709.** The named instance, then the property: a projection whose only
   assertion is its zero value is untested. Expect the property to be expressible
   over the test corpus.
4. Only then, the sweep. Where else does a mechanism report a verdict about a
   question it did not ask? Candidates already visible: `run_release_closeout_tail`
   (below), any `--advisory` posture, any doctor.

**Non-claim.** Do not add a meta-gate that checks gates. The retro's Engelbart
counterfactual is explicit that the deliverable is an INVENTORY — per detector,
what it cannot see — read for gaps. Whether any gate follows is a later question.
A meta-gate is the treadmill `2026-05-20-quality-treadmill-vs-root-cause.md` names.

## Step 2 — #748 redesigned around what measurement said

Slice 2 as written is dead. It was measured and refused on 2026-08-29:

- Python `load_surfaces` + `match_surfaces` is **3.01 ms in-process**; the native
  subprocess is **4.31 ms**. In-memory pattern matching over a loaded manifest has
  no traversal for Rust to win.
- The matcher survives either way. `path_matches_patterns` has two live Python
  consumers: `surfaces_lib.py:105,109` (manifest self-consistency, a different job)
  and **`boundary_probe_lib.py:112`**, which the 2026-08-31 plan did not record.
  So the switch would move the composition wrapper and leave the duplicated
  primitive — the exact shape #748 exists to remove.

What measurement DOES support:

- `repo_file_listing.iter_repo_files` is **89.2 ms**: git 27.1 + `Path`
  construction and sort 24.9 + `is_file()` 13.0 + decode/rebuild. 27 production
  consumers. Native ownership alone is ~1.4x because the `list[Path]` return keeps
  7,739 object constructions in Python. **Native inventory PLUS a string-first API
  is ~2.8x**, with git as the floor. That is the honest slice: it is #748's FIRST
  acceptance bullet (*"Inventory ... consume the native graph rather than
  rebuilding file sets"*), and `native/repograph/src/inventory.rs` already has the
  `FileInventory` — it is simply not exposed as a command.
- The parity harness is repaired and runs (`difference_count: 0`). Use it before
  any ownership switch, per the issue's own weak direction.

Sequence: expose `repograph inventory` → parity against the Python listing →
switch `repo_file_listing.py` internals → only then consider the API shape change
that unlocks the rest of the win.

**#749** follows from this slice, not before it: its own text says the decision
should use observed ownership results rather than a language preference.

## Step 3 — Finish what 2026-08-29 left, analysis already done

- **`_publish_and_finalize` repointing.** STILL the one real hole on an
  irreversible path. Mechanics, established: `_publish_and_finalize`
  (`publish_release_execute.py:295`) and the live `resume_publish`
  (`publish_release_resume_publish.py:218`) both call
  `common.run_release_closeout_tail`; the resume tests STUB it
  (`test_release_resume_edge_coverage.py:147`); so
  `test_release_distinct_channel.py:410-467` is the ONLY execution coverage of the
  carrier → issue-state-readback → final-artifact ordering and the rung-1 floor,
  and it reaches them through a dead driver. The repair merges two existing
  harnesses: drive `resume_publish` with the `_base_cli` from
  `test_release_distinct_channel.py` and let the real tail run. `resume_publish`
  takes 11 injected parameters; the resume tests already construct them. Sized at
  1–2 hours. Do this BEFORE the release, not after.
- **Fixture consolidation.** `test_python_and_security_gates.py`'s three markdown
  tests clone the whole checkout; a sweep agent built the minimal fixture and
  confirmed all three pass on it. The honest repair is to promote
  `_charness_shaped_repo` (`test_shell_gate_root_resolution.py:67`) into
  `tests/quality_gates/support.py` first — it is a THIRD hand-built repo-shaped
  factory, and importing a private helper across test modules is not the fix.
- **Rust changed-line coverage.** `cargo-llvm-cov` is installed; baseline 78.46% of
  8,010 lines. A whole-repo percentage gate is deliberately NOT the answer — that
  is the count-is-a-metric shape this repo already rejected for the ratio cap. The
  parity with Python is a changed-line floor.
- **`scripts/check_python_lengths.py` is misnamed** now that it measures `.rs`.
  73 references; a rename is its own change.

## Deliberately not in this session

- **The release.** 8.0.0 is prepared (`packaging/charness.json` already carries it,
  `--publish-current` is the right mode, the changed-line gate is clear, 99 commits
  are unpushed and operator-approved). It is deprioritised, not blocked. Do not
  start it without finishing Step 3's first item.
- **#750 and #731.** #750 is a configuration surface that cannot express "off"
  (`resolve_adapter.py:62` fills the default unconditionally) and #731 is review
  ceremony cost. Both are real, both have consumer workarounds, and neither belongs
  to Step 1's class. Group them into their own session rather than diluting this one.

## Working shape

- **Ceal-facing repairs go to codex lanes.** Each issue carries its own repro and
  evidence, and the surfaces (critique runner, worktree doctor, retro adapter) do
  not touch `scripts/` internals, so they run concurrently with Step 2 without
  conflict. That disjointness is the reason 2 and 3 combine at all.
- **The Rust redesign stays with the parent.** Last session's single best call was
  refusing slice 2 after measuring it, and that judgement is not delegable.
- **Measure before proposing.** Any proposal in this session containing "faster /
  smaller / cheaper" carries its measurement in the same message.
- Commit before running the battery. Regenerate derived surfaces AFTER the last
  source edit: `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and
  `./charness catalog refresh --repo-root .`. Note that `plugins/` is now
  UNTRACKED, so mirror drift no longer shows in `git status` — the pre-push sync is
  what keeps it honest.
