# Session Retro
Date: 2026-09-05

## Context

The 8.4.2 class-fix session: a tracked public claim whose only on-disk proof
lived in hidden runtime (#764 sampler baseline) and the #797 keep_worktree
sibling. Same class, named before the patch: a durable record named ephemeral
local bytes as the only copy. Shipped as patch 8.4.2; #797 closed; #764 left
open until a scheduled mutation run is green. Claim strength: the class
diagnosis and the local tests are `strong`; hosted mutation remaining green is
`unproven`.

## Window

From the Five Whys / spec
(`charness-artifacts/debug/2026-09-05-tracked-claim-ephemeral-carrier.md`)
through `v8.4.2` published, #797 `CLOSED`, and the closeout commit `5af9028c2`.
Not the 8.4.1 claims commits that sit in `v8.4.1..HEAD`.

## Evidence Summary

- 12 commits on `main` from `d01d3f2a1` (class fix) through `5af9028c2`
  (8.4.2 closeout). Packet `v8.4.1..HEAD` also lists the 8.4.1 verification
  commits; those are out of this window.
- Debug/spec: `charness-artifacts/debug/2026-09-05-tracked-claim-ephemeral-carrier.md`,
  `charness-artifacts/debug/2026-09-05-worktree-only-candidate-deleted.md`,
  `charness-artifacts/spec/2026-09-05-tracked-claim-ephemeral-carrier.md`.
- Critique: `charness-artifacts/critique/2026-09-05-tracked-claim-and-worktree-only.md`.
- Release-lane wall (measured, helper/run-quality): ~190s fail (seam-index +
  python-lengths), 335s fail (changed-line), 351s pass, 320s prepare, 327s fail
  (changed-line after claims HEAD), 333s pass then publish. Six `--release
  --read-only` runs; the adapter budget for that label is 110s and is advisory
  exceeded (`gate-baseline runtime`).
- GitHub: #797 CLOSED, #764 OPEN; public tag page 200; `charness version`
  8.4.2.
- Retro packet: `charness-artifacts/retro/2026-09-05-000930-packet.md`. Rework
  issues since 2026-08-06 name `achieve` (2), `issue` (1), `retro` (1); none
  names `impl`, `debug`, `release`, or `critique`.
- Last retro: `charness-artifacts/retro/2026-09-04-session-retro.md` tagged
  `gate-failures-patched-serially` and asked this retro whether it fired.
- No metrics_commands configured; efficiency claims here are measured lane
  times plus narrative. Host-log token/tool counts: unavailable.

## Waste

- **`gate-failures-patched-serially` fired again.** Yesterday's improvement was
  "run `--release --read-only` before the publish helper." This session did
  that once, then committed more (docs recopy, length split, coverage tests,
  claims review) and let the next expensive lane name the next miss: docs-length
  1251>1233, stale seam-index, `task_run.py`/`run_review_support.py` over
  tokei caps, changed-line (git-commit fail + promotion escape), eviction-form
  on raw `sys.modules` delitem, then changed-line again after the claims-review
  HEAD shrank the mapped test subset. The class is not "forgot the release
  lane exists." It is "the cheap owner of the files just edited was not run
  before Slice-reopen." (recurrence-class: gate-failures-patched-serially)
- **Executable policy recopied into `docs/artifact-policy.md`.** The extra
  worker-delivered bullet grew a recorded 1233-word page. Documentation
  principles already prefer links over copied policy; the validator already
  holds the path. (recurrence-class: docs-recopy-grows-length-record)
- **A claims-review HEAD is a new tree.** Coverage is incremental from mapped
  tests. After the claims JSON landed, only the promotion test file was mapped,
  so `return module` on an already-loaded support copy went uncovered and
  forced a rebase of the prepared SHA. Direction of error is documented in
  `release_changed_line_coverage.py`: a subset can call a covered line
  uncovered. (recurrence-class: coverage-subset-false-uncover)
- **Gate-baseline runtime.** Six release lanes at ~5.5 minutes each is about
  half an hour of `--release --read-only` wall, against a 110s advisory
  budget. Cadence was eventually right; the cost is still debt. Routed below,
  not absorbed as "necessary safety."

## Critical Decisions

- Name the class (tracked on-disk proof must be visible knowledge) in debug +
  spec before the patch, and treat #797 as the same class rather than a
  second bug. Alternative skipped: retarget the two 2026-09-04 cites only.
  Constrained the slice to refuse hidden cited carriers, promote
  approval-eligible reports, persist dirty candidates, honor `keep_worktree`.
- Close #797 only; leave #764 open until a scheduled mutation run's sampler
  is green. Alternative skipped: close both on the live-corpus green.
  Constrained closeout to the recovery-observer rule.
- Revert the artifact-policy recopy rather than raise the docs-length record.
  Alternative skipped: compress elsewhere to keep the bullet. Constrained
  the page to the recorded 1233 words.
- Rebase the unpublished prepared commit to insert the coverage test *before*
  claims evidence, rather than commit on top of claims (resume would refuse)
  or amend claims (change-set would no longer be claims-only). Constrained
  claims JSON to the new prepared SHA `132c28f46`.

## North Star Alignment

Read `docs/design-north-star.md` for this work.

- **P3 held** on the class fix: one invariant (a tracked producer that names
  an on-disk carrier must name a clean-clone path) plus the two instances,
  instead of a cite-by-cite path list. The live-corpus `--all` stay-strict
  decision is that principle applied to detection.
- **P2 was inverted, then corrected.** `run_review_support.py` and
  `task_run.py` were already in the warn band; promotion and persist were
  appended until tokei refused. `--headroom --paths` existed and was not
  asked before the write. The split into `run_review_promotion.py` and
  `_checkout_own_dir` in `task_run_git.py` is the P2 move the gate forced.
- **P4 held at the close boundary and was mis-applied on HEAD.** #797 close
  used a distinct observer (bounded reviewers + claims reviewer) and a
  distinct channel (HTTPS fetch, `charness version`). The mis-apply: one
  green `--release` on eviction HEAD was treated as covering the later
  claims-review HEAD. Same proxy, new tree.
- **P1 held** for the artifact-policy recopy: shrinking the page was
  reversible judgment; raising the recorded baseline would have been the
  ratchet the length gate exists to prevent.
- **Named signature: terminal trust at a proxy.** A passing release lane on
  commit N is not a passing release lane on commit N+k. The Diagnosis
  section's failure is a green treated as proof; this was a green of a
  different tree.

## Trends vs Last Retro

- Last retro asked whether `gate-failures-patched-serially` fired. It did.
  The 8.2.0 form was "narrow check, commit, next lane surprises." The 8.4.2
  form is "run the expensive lane once, then Slice-reopen more commits." Same
  class, later in the pipeline.
- Last retro was workflow-first after two user corrections. This one is the
  same workflow class plus a product class (hidden cited carriers) that the
  debug/spec path actually caught before code — that half is progress.
- Rework-issue packet still names `achieve`/`issue`/`retro`, not this slice's
  skills.
- Active lesson: yesterday's "run `--release` before publish" is necessary
  and not sufficient; the cheap owners of the just-edited files have to run
  *per commit*, not once per session.

## Expert Counterfactuals

- **Engelbart (system-improving-itself, briefed):** LAM was designed (the
  invariant, the refuse/promote/persist trio, the live-corpus stay-strict).
  T was not designed alongside it: `--headroom` before appending to a
  warn-band file, `check_docs_length` before editing a recorded page,
  seam-index `--write` after a new debug artifact, changed-line after a HEAD
  that is not the HEAD you measured. The system-improving move is to make
  those four cheap commands the T that the Slice-reopen habit requires,
  instead of paying the 5.5-minute release lane to discover each one.
- **John Ousterhout (module depth / one job):** `run_review_support.py` was
  already a grab-bag near 360 lines. Promotion of a durable worker report is
  a different job from hold-out and runner IO. Asking "what is this file's
  one job?" before the first extra function would have created
  `run_review_promotion.py` on the class-fix commit, not after the length
  gate. Same for `_checkout_own_dir` living with git helpers.

## Sibling Search

- Mental model: a green from a verifier that did not judge *this* HEAD, or a
  durable page/file grown without asking the cheap owner that already
  records its size.
- same layer: docs-length recopy, tokei over-cap, stale seam-index,
  eviction-form, changed-line twice | decision: same waste, fix now | proof:
  last `--release` on claims HEAD passed after the cheap fixes landed
- abstraction up: Slice-reopen as a named skip of the commit-msg release
  receipt | decision: intentional boundary | proof: the hook's job is to
  admit unfinished slices; the waste is not the skip, it is skipping the
  cheap owners too
- specialization down: claims-review HEAD shrinking the mapped coverage
  subset | decision: same waste, fix now | proof:
  `tests/test_run_review_declared_path_resolution.py::test_promotion_reuses_an_already_loaded_support_module`
  plus rebase of unpublished prepared SHA
- mental-model siblings: `check_code_lengths.py --headroom` exists and was
  unused before the append | decision: same waste, fix now | proof: the
  8.4.2 length split ran `--headroom` only after the gate was red
- transferable waste item destination: none — habit + the publish helper
  already re-runs `--release` on resume; a new gate that blocked Slice-reopen
  without those four cheap checks would raise the wrong cost. Revisit if the
  class fires a third time.

## Next Improvements

- workflow: before a Slice-reopen commit that touches `docs/`, `scripts/`,
  `skills/`, or `charness-artifacts/debug/`, run the cheap owners of those
  files (`check_docs_length.py`, `check_code_lengths.py --headroom --paths`,
  `build_debug_seam_risk_index.py --check`, focused standing pytest), not
  only the full `--release` once per session. After a claims-review commit,
  re-run changed-line coverage on that HEAD before `--resume --execute`.
  Structural pattern: a skip-the-expensive-lane habit that also skips the
  cheap lane which would have judged the edit. Triggering instance(s):
  artifact-policy 1251>1233; tokei over-cap; seam-index stale; claims-HEAD
  changed-line fail at 327s. Destination: repo-local. Filed only if this
  class fires a third time. (recurrence-class: gate-failures-patched-serially)
- capability: none this run — `--headroom`, docs-length, seam-index
  `--check`, and the publish helper's pre-push `--release` already exist.
  The miss was sequence, not missing T.
- memory: this record, so `gate-failures-patched-serially` accrues a second
  observation and `docs-recopy-grows-length-record` /
  `coverage-subset-false-uncover` enter the working set.
  (recurrence-class: docs-recopy-grows-length-record)
  (recurrence-class: coverage-subset-false-uncover)

## Persisted

Persisted: yes: charness-artifacts/retro/2026-09-05-session-retro.md
Seeding: 2 class(es) seeded

## Packet Consumed

Packet Consumed: charness-artifacts/retro/2026-09-05-000930-packet.md
