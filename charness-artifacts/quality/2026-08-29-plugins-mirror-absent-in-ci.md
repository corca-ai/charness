# Quality Review
Date: 2026-08-29

Title: The untracked plugin mirror — one loud break, three silent ones

## Scope

Target boundary: why `main` is red for anyone who clones it (Step 0 of the
2026-08-29 plugins-mirror design study). Measured on real fresh clones of
`030aa8262`, because every maintainer machine has run `charness init/update`,
which writes `plugins/` and hides the fault.

Ambient repo findings: two detectors and one hook prefix that `6e05e026e`
disarmed silently, plus a symlink refusal found while filing this record.

## Surface Contract Review

- semantic coverage: observed — three fresh clones, a full standing suite in
  each, the five plugin-touching gates, both `plugins/**` detector scopes.
- surface: what a checkout without `plugins/` proves versus what it reports.
- owner: `scripts/sync_root_plugin_manifests.py`; both CI workflows consume the
  mirror and neither ran it.
- projections: gate exit codes, gate stdout, suite counts, detector scope size.
- state scope: `030aa8262`, clean clones, no local state.
- transitions: two workflows gained a provisioning step; one doc was corrected.
- proof boundary: the table below; each cell is a run, not a read.
- unexamined axes: the mutation run itself (it never reached a mutant).

## Current Gates

`git ls-files plugins/` returns 0; the tree is 1,045 generated files.

| surface | mirror ABSENT | mirror REGENERATED |
| --- | --- | --- |
| standing suite | **94 failed, 16 errors** | 8,468 passed, 0 failed |
| `check_doc_links.py` | **exit 1** | exit 0 |
| `check_plugin_doc_links.py` | exit 0, "Validated … skipped: none" | **byte-identical** |
| `check_plugin_asset_command_carriers.py` | exit 0, "Validated 0 … asset(s)" | **identical** |

The 94 reproduce `#758` exactly. `check_doc_links.py` fails *before* pytest in
`quality-core.yml`, so Quality Core never reached the suite — `#758` is the
mutation half of one fault, not the whole of it.

**The per-test question, answered at once.** Regenerating takes all 94 to green,
so every one asks a real question about a GENERATED surface; none is a source
fact asserted against a mirror that happened to be there. Their names say why:
`test_the_exported_mirror_enumerates_its_own_modules`,
`test_plugin_copy_renders_the_workflow_into_a_fresh_repo`. An export test exists
because the transform can break. The plan's open question about a fifth test is
closed: both `test_check_doc_links.py` tests fail on a true fresh clone; the
earlier `mv plugins /tmp/` probe ran four named node IDs and could not see it.

**Three silent breaks, worse than the red ones because they print `Validated`.**

1. `check_plugin_doc_links.py` scopes through `iter_matching_repo_files`, which
   reads the GIT LISTING. With the mirror fully present — 229 markdown files —
   its scope is **0 documents**. Dead since `6e05e026e` everywhere: locally, in
   CI, on a fresh clone. Output is byte-identical over 229 files and over none,
   because it counts what it SKIPPED and never what it EXAMINED. Its own
   docstring names this failure and cites #479. `quality-core.yml` calls the step
   "the layer that catches that case on a push."
2. `check_plugin_asset_command_carriers.py` — same shape, 0 of 58 assets. More
   honest: it prints the zero, so the vacuity is at least legible.
3. `UNCONDITIONAL_FULL_GATE_PREFIXES` leads with `plugins/`, which `.githooks/pre-push`
   uses to force the full gate. An untracked path never appears in a push diff,
   so that entry cannot fire. Its tracked siblings still work.

Both detectors were ruled SANCTIONED in the previous session's
[empty-scope disposition](2026-08-29-empty-scope-disposition.md) on the premise
that zero plugin docs is "a legitimate discovered-empty family". That premise was
already false: the mirror is a REQUIRED generated surface. The disposition was
reached by source reading; one with/without run refutes it.

**A false claim in the consumer-facing doc.** `docs/host-packaging.md` called the
tree "checked-in" in eight places, including a section title, and linked into it
three times. All eight became false at `6e05e026e` and all three links broke
there. That commit DID sweep docs — 34 backticked refs converted across nine of
them — but it swept the docs whose BACKTICK classification changed and missed the
one doc whose existing LINKS it invalidated. Sweeping by the rule that just
started firing is not sweeping by what the change broke.

**Filing this record exposed a second instance of the plan's Step 1 class.** The
documented flow — write the record, run `refresh_current_pointer.py --execute` —
made `test_charness_packet_carries_the_semantic_reviewer_question` fail:
`reviewed path 'charness-artifacts/quality/latest.md' is a symlink`. Isolated by
restore/reapply. Step 1 records that a range containing DELETIONS cannot be
declared as bounded-review input; a range containing a POINTER REFRESH cannot
either — that is every session filing a quality record. It clears at commit,
which is why it went unseen: it bites only in the window where a reviewer would
read the record. Step 1's repair should key on the reviewed path's KIND.

## Runtime Signals

- runtime source: timing capture is missing; no structured metrics collected.
  Wall-clock only: the standing suite ran ~75–86s per clone.
- runtime hot spots: none introduced; the new step is a 1,045-file copy.
- coverage gate: no changed-line or mutation verdict is claimed.
- evaluator depth: deterministic local runs; no delegated review requested.

## Healthy

The producer reconstitutes all 1,045 files from a bare clone in one call, which
is why regeneration beats re-tracking. `6e05e026e`'s cost case (11 MB, 37% of
commits as churn) stands; nothing here argues for reverting it.
`test_both_trees_are_present_so_this_test_can_mean_anything` is the one surface
that already refuses rather than passes when its subject is missing.

## Weak

This gives the gates their subject; it does not give `check_plugin_doc_links.py`
the ability to notice it has none. The doc keeps its three links: the doc-link
contract has no vocabulary for a deliberately-generated path, and backticking
them raises `missing-artifact`.

## Missing

No test asserts that CI materializes the mirror. Drop either step and this class
returns silently, its first symptom again a 94-failure baseline.

## Deferred

- A doc-link placeholder vocabulary for generated-and-untracked repo paths.
- Folding the symlink refusal into Step 1's repair, as one class not two.

## Advisory

- `gh run view --log-failed 33252724811` reports `Status: UNMEASURED`: no mutant
  has run since `030aa8262`, so the next run is a first measurement.

## Delegated Review

- status: not_applicable — no delegated review was requested for this diagnosis.

## Commands Run

`git clone --no-hardlinks . /tmp/charness-fc{1,2,3}` at `030aa8262`;
`run_standing_pytest.py` in each; `sync_root_plugin_manifests.py`; the five
plugin-touching gates per clone; scope probes over `iter_matching_repo_files`
for both detectors; `gh run view --log-failed 33248180425`.

## Recommended Next Quality Moves

- active land the two workflow steps and the doc correction; they close the
  consumer-facing break and nothing else depends on them.
- passive because arming is its own decision with its own evidence: treat the two
  dead detectors as one repair, since a single scope rule fixes both.

## History

- [2026-07-14 quality review](history/2026-07-14-open-issue-resolution-proof.md)
