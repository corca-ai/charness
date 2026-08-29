# Quality Review

Date: 2026-08-29

Title: The untracked plugin mirror — one loud break, three silent ones

## Scope

Step 0 of `charness-artifacts/design-studies/2026-08-29-plugins-mirror-red-and-unreviewed-removal.md`:
why `main` is red for anyone who clones it. Measured on real fresh clones of
`030aa8262` rather than on this checkout, because every maintainer machine has
run `charness init/update`, which materializes `plugins/` and hides the fault.

Scope grew during measurement. The plan framed this as failing tests. The tests
are the loud half; `6e05e026e` (`untrack the generated plugin export`) also
disarmed two gates and one hook prefix that still report success.

## Surface Contract Review

- semantic coverage: observed — three fresh clones, full standing suite in each,
  the five plugin-touching gates, and the scope of both `plugins/**` detectors.
- surface: what a checkout without `plugins/` proves versus what it reports.
- owner: `scripts/sync_root_plugin_manifests.py` produces the mirror; both CI
  workflows consume it and neither ran it.
- projections: gate exit codes, gate stdout, standing-suite counts, gate scope size.
- state scope: `030aa8262` (the commit CI reported), clean clones, no local state.
- transitions: two workflows gained a provisioning step; one doc was corrected.
- proof boundary: the with/without comparison below; each verdict is a run, not a read.
- unexamined axes: the mutation run itself (never reached a mutant), and whether
  any of the 94 tests should be re-aimed at source rather than the mirror.

## Current Gates

`git ls-files plugins/` returns 0; the tree is 1,045 generated files. A fresh
clone has none of it. Measured on `030aa8262`:

| surface | mirror ABSENT | mirror REGENERATED |
| --- | --- | --- |
| standing suite | **94 failed, 16 errors** | 0 failed, 8,467 passed |
| `check_doc_links.py` | **exit 1**, `docs/host-packaging.md` | exit 0 |
| `validate_packaging.py` | exit 0, "Validated 1 packaging manifest(s)." | identical |
| `check_plugin_doc_links.py` | exit 0, "Validated … skipped: none" | **byte-identical** |
| `check_plugin_asset_command_carriers.py` | exit 0, "Validated 0 shipped … asset(s)" | **identical** |

The 94 failures reproduce the list in `#758` exactly. `check_doc_links.py` fails
*before* pytest in `quality-core.yml`, so Quality Core never reached the suite —
`#758` is the mutation half of one fault, not the whole of it.

### The loud break, and its disposition

The plan asks, per test, whether it questions a GENERATED surface (CI must
regenerate) or a source fact (it is asserting against a mirror that happened to
be there). Measurement answers it for all 94 at once: regenerating the mirror
takes the suite to zero failures. Not one of them needs re-aiming. Their names
say why — `test_the_exported_mirror_enumerates_its_own_modules`,
`test_installed_cli_catalog_list_loads_backend_from_managed_checkout`,
`test_plugin_copy_renders_the_workflow_into_a_fresh_repo`. Answering those from
source would answer a weaker question: an export test exists because the
transform can break.

The plan's open question about a fifth test is closed: BOTH
`test_check_doc_links.py` tests fail on a true fresh clone. The earlier
`mv plugins /tmp/` probe ran four named node IDs, so it could not have seen it.

### The silent breaks, which no one is watching

These are worse than the red tests, because red is loud and these print
"Validated".

1. **`check_plugin_doc_links.py` scans nothing, and says so in no way.** Its
   scope is `iter_matching_repo_files(root, ("plugins/**/*.md",))`, which
   resolves against the *git listing*. With the mirror fully present on disk —
   229 markdown files — the scope is **0 documents**. It has been dead since
   `6e05e026e` everywhere: locally, in CI, on a fresh clone. Its output is
   byte-identical over 229 files and over none, so nothing distinguishes a full
   pass from a vacuous one. Its own docstring names this failure: "a gate that
   skips silently and then prints 'Validated' reads as full coverage … the exact
   failure this gate was built to close (#479)". It counts what it *skipped* and
   never what it *examined*, so an empty scope reports "skipped: none".
   `quality-core.yml` calls this step "the layer that catches that case on a push."
2. **`check_plugin_asset_command_carriers.py` is dead the same way** — 0 in scope
   against 58 matching files on disk. It is the more honest of the two: it prints
   "Validated 0 shipped JSON/YAML asset(s)", so the vacuity is at least legible.
3. **`UNCONDITIONAL_FULL_GATE_PREFIXES` contains a dead entry.** `plugins/` is
   first in the list `.githooks/pre-push` uses to force the full broad gate. An
   untracked path never appears in a push diff, so that entry can no longer fire.
   Its siblings `.claude-plugin/` and `.agents/plugins/` are still tracked and
   still work.

Both detectors were reviewed in the previous session, in
`charness-artifacts/quality/2026-08-29-empty-scope-disposition.md` and both were
ruled SANCTIONED, on the premise that zero plugin docs/assets is "a legitimate
discovered-empty family". That premise was already false when it was written:
the mirror is a *required generated surface*, not an optional family, and
`6e05e026e` had removed it from the listing the detectors read. The disposition
was reached by source reading; a with/without run would have caught it. This is
the ledger's own `green-test-is-not-covered-line` shape, one layer up.

### A false claim in the consumer-facing doc

`docs/host-packaging.md` asserted the plugin tree is "checked-in" in eight
places, including a section titled `## Checked-In Install Surface`. All eight
became false at `6e05e026e`, and its three links into `plugins/charness/` became
broken at the same commit. That is what Quality Core actually failed on.

The miss has a precise shape. `6e05e026e` DID sweep the docs — it converted 34
backticked references into links across nine of them, because untracking made
those basenames unique and armed a rule that had never fired. It swept the docs
whose *backtick classification* the untracking changed, and missed the one doc
whose *existing links* the untracking invalidated. `docs/host-packaging.md` is
not in that commit's diff at all; its three links pre-date it and were correct
while the tree was tracked. Sweeping by the rule that just started firing is not
the same as sweeping by what the change broke.

### An unrelated defect this record's own filing exposed

Writing this record surfaced a second instance of the plan's Step 1 class, found
by accident rather than by looking. The documented flow is: write the dated
record, then run `refresh_current_pointer.py --execute`, which the resolver
itself instructs (`update_current_pointer_after_write: true`). Doing exactly that
made `tests/test_critique_prepare_packet.py::test_charness_packet_carries_the_semantic_reviewer_question`
fail:

```
ValueError: reviewed path `charness-artifacts/quality/latest.md` is a symlink;
declare the target file explicitly
```

Isolated by restoring the symlink (test passes) and reapplying the refresh (test
fails). `reviewed_input_identity._checked_path` refuses symlinks, and the
refreshed pointer is a modified symlink in the change set, so `build_packet`
cannot build an identity over it.

Step 1 records that a change range containing DELETIONS cannot be declared as
bounded-review input. This is the same wall with a different shape: a change
range containing a POINTER REFRESH cannot be either — which is every session that
files a quality record and follows the documented flow. The failure is transient
(it clears at commit, since the path leaves the change set), which is precisely
why it has not been noticed: it only bites in the window where a reviewer would
be asked to review the record. Step 1's repair should be scoped to the reviewed
path's *kind*, not to deletions alone.

## Runtime Signals

- runtime source: three clean clones; standing suite ~80s each under the repo runner.
- runtime hot spots: none introduced. The new step is a file copy (1,045 files, sub-second).
- coverage gate: no changed-line or mutation verdict is claimed; mutation has not
  run on any commit since `030aa8262`.
- evaluator depth: deterministic local runs only; no delegated review requested.

## Healthy

The producer is complete and cheap: `sync_root_plugin_manifests.py` reconstitutes
all 1,045 files from a bare clone in one call, which is what makes regeneration
the right repair rather than re-tracking. `6e05e026e`'s cost analysis (11 MB, 37%
of commits as regenerated churn) stands; nothing here argues for reverting it.

`test_parents_index_layout_invariant.py::test_both_trees_are_present_so_this_test_can_mean_anything`
is the one surface that already did the right thing — it refuses rather than
passes when its subject is missing, and its name says so.

## Weak

The repair makes CI green by giving the gates their subject. It does not give
`check_plugin_doc_links.py` the ability to notice it has no subject — that gate
stays vacuous after this change, because its scope reads the git listing and the
mirror is still untracked. Arming it is a separate decision with its own evidence.

The doc keeps its three links into the generated tree, because the doc-link
contract has no vocabulary for "repo-shaped path that is deliberately generated":
backticking them raises `missing-artifact`, and `plugins/` is in
`REPO_REFERENCE_PREFIXES`. So a reader on a bare clone still gets three dead
links; the prose now warns them, which is honesty, not a fix.

## Missing

No test asserts that CI materializes the mirror. If either workflow's step is
dropped, this whole class returns silently and the first symptom is again a
94-failure baseline. That guard is not written.

## Deferred

- Re-arming `check_plugin_doc_links.py` and `check_plugin_asset_command_carriers.py`
  over the on-disk mirror, and correcting their SANCTIONED rows in the
  2026-08-29 empty-scope disposition.
- Removing or replacing the dead `plugins/` prefix in `UNCONDITIONAL_FULL_GATE_PREFIXES`.
- A doc-link placeholder vocabulary for generated-and-untracked repo paths.
- Folding the symlink refusal above into Step 1's reviewed-input-identity repair,
  so deletions and pointer refreshes are fixed as one class rather than two.

## Advisory

- The mutation workflow has produced no verdict since `030aa8262`. Its next run
  is the first real measurement, not a re-confirmation.

## Delegated Review

- status: not_applicable — no delegated review was requested for this diagnosis.

## Commands Run

`python3 scripts/render_lesson_selection_preview.py --repo-root . --seed step0-plugins-mirror`;
`git clone --no-hardlinks . /tmp/charness-fc{1,2,3}` at `030aa8262`;
`python3 scripts/run_standing_pytest.py --repo-root .` in each;
`python3 scripts/sync_root_plugin_manifests.py --repo-root .`;
the five plugin-touching gates in each clone; scope probes over
`iter_matching_repo_files` for both `plugins/**` detectors;
`./scripts/check-markdown.sh`; `gh run view --log-failed 33248180425`.

## Recommended Next Quality Moves

- active: land the two workflow steps and the doc correction; they close the
  consumer-facing break and nothing else depends on them.
- passive: treat the two dead detectors as one arming decision, not two repairs —
  they fail identically and a single scope rule fixes both.

## History

- [2026-08-29 empty-scope disposition](2026-08-29-empty-scope-disposition.md)
- [2026-08-25 quality review](2026-08-25-quality-review.md)
