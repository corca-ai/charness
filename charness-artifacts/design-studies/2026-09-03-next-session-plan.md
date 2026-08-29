# Next-session plan: main is red for consumers, and a removal shipped unreviewed

> Written at the close of the 2026-08-29 session, with the operator.
> Supersedes `2026-09-02-next-session-plan.md`, whose Step 0, Step 1, Step 2,
> Step 3 and Step 4 are closed. Step 5 (the release) is DEFERRED by the operator,
> not blocked.

## Read this FIRST, and read the files, not this summary

The previous plan opened with this sentence and it was right. This session still
paid the tax once: I built lane `--scope` lists from a grep that returned 55 files
and then wrote eleven glob patterns that missed nine of them, holding the file
list the whole time.

Required opens, in this order:

1. `charness-artifacts/retro/<this session's retro>` — if one exists. If it does
   not, that absence is itself the first finding: this session ended without one.
2. `docs/design-north-star.md`, `Purpose` section. Every item below is ranked by
   it: **charness exists to reduce rework in the repositories that CONSUME it.**
3. `charness-artifacts/critique/workers/2026-08-29-release-round3/result.json` —
   the round-3 review that DEFERRED. Read its two findings before touching
   Step 2. Rounds 1 and 2 are beside it under the same directory naming; those
   are the two that returned `block`, and their findings are what the repairs in
   this slice answer.
4. Run the ledger preview, as `AGENTS.md` says:
   `python3 scripts/render_lesson_selection_preview.py --repo-root . --seed <id>`

## Standing state, measured

- **10 unpushed commits** (`030aa8262..e3d7aeef0`). Local standing lane 8563
  passing including `release_only`; broad lane 79 passed / 0 failed.
- Release: `packaging/charness.json` is `8.0.0`; latest PUBLISHED is `v7.0.0`
  (2026-08-27). There is no `v8.0.0` tag or release.
  `charness-artifacts/release/latest.md` carries
  `<!-- charness-release-state:abandoned-prepare -->` and states plainly that no
  proof carries forward and the next run establishes its own.
- Closed this session: #755, #750. Committed but unpushed, so still OPEN on
  GitHub until the push lands: #757, #754.
- Filed this session: #756, #759.

## Step 0 — FIRST: main is red for anyone who clones it

Highest priority. It is a live consumer-facing break, and it is the north star's
Purpose clause inverted: every local gate is green while the fresh-clone path
fails.

`#758` reports mutation CI failing on `030aa8262` because five coverage-baseline
tests failed. Four of them reproduce on demand:

```
mv plugins /tmp/ && python3 scripts/run_standing_pytest.py --repo-root . \
  --pytest-target tests/quality_gates/test_export_self_sufficiency.py::test_the_export_ships_the_bootstrap_contract_beside_the_installer \
  --pytest-target tests/quality_gates/test_command_dominance.py::test_sc19_and_sc16_ship_to_consumers_rather_than_living_only_here \
  --pytest-target tests/quality_gates/test_absent_input_is_not_a_matching_input.py::test_s35_this_repo_declares_its_surfaces_and_has_none_absent \
  --pytest-target tests/quality_gates/test_check_doc_links.py::test_the_contradiction_rule_finds_every_live_site_in_the_real_tree
```

Measured: 4 failed with `plugins/` absent, 5 passed with it present.

The cause is structural, not incidental. `git ls-files plugins/` returns **0** —
the mirror was untracked two sessions ago — and these four tests assert facts
ABOUT the exported mirror. A fresh clone and CI have no `plugins/`;
`.github/workflows/quality-core.yml` does not run
`sync_root_plugin_manifests.py` before the suite.

Decide which of these it is, per test, and do not sweep:

- the test asks a real question about a GENERATED surface and CI must regenerate
  it first; or
- the test asks a question that should be answered from source, and it is
  asserting against a mirror because the mirror happened to be there.

The fifth failing test in `#758`
(`test_check_doc_links.py::test_the_live_tree_has_no_unmarked_portable_reference`)
did NOT reproduce in the four-test probe above; establish whether it is a fifth
instance of the same class or something else before bundling it.

Note the shape: the previous session untracked `plugins/` after proving the
regeneration byte-identical, which was correct, and the tests that depended on
its presence were not part of that proof. That is the same gap the `.gitignore`
anchoring incident had, one layer up.

## Step 1 — #759, because it is what stopped this session from finishing

A change range containing DELETIONS cannot be declared as bounded-review input.
Both declarations refuse and they refuse each other:

| declaration | refusal |
| --- | --- |
| `--range` + full `git diff --name-only` (98 paths, deletions included) | `null-content-hash` |
| `--range` + `--diff-filter=d` (92 paths) | `changed-ref-path-mismatch` |
| `--commit <sha>` on a commit with deletions | `null-content-hash` |

Each refusal is individually correct. A deleted path has no content to hash; a
declared set missing part of the range is not the range. Together they leave a
removal slice unreviewable.

This is not theoretical. The real-host proof removal (`e3d7aeef0`, 57 files,
+444/−2968, six deletions) **shipped into the unpushed slice without a fresh-eye
review**, and the workaround used to get a review at all made the evidence worse
rather than weaker — see Step 2.

Read `skills/public/critique/scripts/run_review_packet.py` for where the content
hash is derived. The fix wants deletions to participate in the reviewed-input
identity AS deletions — their pre-image and the fact of removal are both
available from the range — rather than as unhashable content.

`#751` is adjacent and was independently reproduced here: the round-3 packet also
emitted no semantic sections, so the reviewer received routing and non-goals and
no slice. Read them together; they may share one repair.

## Step 2 — the real-host removal is UNREVIEWED, and the record must say so

Round 3 returned `defer`, not `block`, and it did not review the code. It read
the packet, found it could not support a verdict, and said so. Its evidence, worth
reading verbatim in
`charness-artifacts/critique/workers/2026-08-29-release-round3/result.json`:

- `changed_ref: null`, `base_head_role: provenance-only`
- `reviewed_patch_sha256`, `staged_patch_sha256`, `unstaged_patch_sha256` are all
  the SHA-256 of an **empty payload**
- the changed-files section listed two generated critique packets and the
  reviewed-paths manifest — the scaffolding, not the slice
- no deletion entry or absence marker for any removed component, although
  `prepared_for` named the removal explicitly

So the honest ledger for this session's slices is:

| slice | fresh-eye review |
| --- | --- |
| round-1 range | reviewed → `block` → three findings repaired |
| round-2 range | reviewed → `block` → three findings repaired |
| real-host removal + the three commits after it | **not reviewed** |

Do not record "round 3 ran" as "round 3 reviewed". The `--prepared-for`
workaround answers a weaker question than the range form and this session used
it; that is a fact about the evidence, not a detail.

Round 3's second finding stands independently of the packet defect and should be
honored whenever a removal is reviewed: judging the removal of an operator-facing
proof boundary needs a **surface-lock inventory** — which consumer-visible
checks, adapter fields, artifact sections and operator instructions were removed
versus retained, what replacement control exists, and bound focused receipts.
`e3d7aeef0`'s commit message carries that in prose; the packet did not carry it
at all.

## Step 3 — the release, when the operator asks for it

DEFERRED by the operator this session, explicitly. It is not blocked and nothing
below is a prerequisite the operator has to argue with; this section exists so
the next session does not re-derive the state.

- The version surfaces are coherent at `8.0.0` with no drift, so the path is
  `publish-current`, not a bump.
- `fresh_checkout_probes` were RUN this session and passed (3/3, exit 0). That
  verdict is stale the moment anything changes; re-run rather than cite it.
- The claims review has never been run for 8.0.0. `v7.0.0`'s record
  (`charness-artifacts/release-review/2026-08-28-v7.0.0-claims-review.json`) is
  `verdict: unproven` because the host delivered no independent observer. That
  excuse is no longer available: the file-backed reviewer path WORKS now, proven
  three times this session. A claims round audits the release RECORD, not the
  code, and it needs the record to exist first.
- Real-host proof is retired, so it is no longer a publish obligation. The
  critique boundary, the claims review, and the fresh-checkout probes were
  deliberately left untouched.

## Step 4 — the follow-ups this session created and did not take

Each is bounded and each has its evidence already recorded. None is urgent.

- **The four DEFECT detectors from the empty-scope disposition.**
  `charness-artifacts/quality/2026-08-29-empty-scope-disposition.md` names the
  repair and the observable a test would assert for each of
  `check_prose_pin.py`, `check_markdown_inline_code.py`,
  `check_public_doc_coupling.py`, and `check_skill_cut_safety.py`. Two were
  probed at integration and reproduce trivially:
  `check_prose_pin.py` over a directory with no git history prints
  `status: clean` and exits 0; `check_markdown_inline_code.py --path <nonexistent>`
  prints `Validated inline code spans in 1 markdown file(s)` and exits 0.
  Nine detectors were judged SANCTIONED; do not re-litigate those.
- **#756** — split the backend boundary out of `reviewer_worker_runtime.py`
  (357/360 code lines). The extraction needs `WorkerError` to move with it.
- **Arming, still deliberately not done.** `inventory_empty_scope_honesty.py`
  ships with `--require-no-positive-verdict-over-zero` that nothing passes, and
  the restored lesson lifecycle is NOT wired into any quality run. Both are their
  own decisions with their own evidence. The ratio-cap entry in the corpus is
  what happens otherwise.
- **A stale stash from an older session** sits at `stash@{0}`
  (`c7344a1b2ca405e808729bc37cd9fca24d6d40ec`, a 30-line
  `charness-artifacts/retro/lesson-ledger.json` WIP on `0ef5321ad`). It is not
  this session's and was deliberately preserved. Dispose of it or leave it, but
  know it is there before running anything that pops a stash.

## Working shape

- **Do not put `git stash` in the same compound command as a backgrounded
  `charness task run`.** The trailing `git stash pop` runs when the LANE
  finishes, not when the launch returns. This session's pop fired 44 minutes
  later and tried to apply an unrelated session's WIP; only the resulting
  conflict kept it from landing silently.
- **Build `--scope` from the real search AND check the globs against it.** Having
  the file list is not the same as covering it. Diff your glob set against the
  grep output before launching.
- **A lane timeout is not a loss.** This session's removal lane timed out at ~44
  minutes and committed a typed WIP candidate; the worktree's own standing suite
  passed at 8447, and the candidate was salvaged rather than re-run. Salvage
  first, per `.agents/claude-host.md`.
- **`git diff HEAD` on a lane worktree omits UNTRACKED files.** Check
  `git status --porcelain | grep '^??'` before taking a patch. This session
  nearly integrated a restore whose three new files never arrived.
- **Run the disconfirming probe before the confirming suite**, and make the probe
  DISCRIMINATE. One reproduction written this session passed against both the
  fixed and the unfixed code, which proved nothing; the incident's real shape was
  an undated subject key, not a dated one.
- **The reviewer is not automatically right, and neither am I.** Every finding
  from all three rounds was probed before repair. Two round-2 findings landed
  inside repairs this session had already called verified.
- `plugins/` is untracked and regenerated by `sync_root_plugin_manifests.py`;
  after the last source edit, run it and `./charness catalog refresh --repo-root .`.
