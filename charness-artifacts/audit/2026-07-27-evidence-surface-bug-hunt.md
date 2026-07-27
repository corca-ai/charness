# Evidence-Surface Bug Hunt — Verdicts Over Unestablished Scope
Date: 2026-07-27
Status: 30 defects reproduced by execution; none fixed yet. This file is the
tracking record — update the Status column as items land.

## Why this exists

Closing issues #460/#461/#463 produced six defects that a 5728-test suite never
saw, and three of them shared one shape: **a check that reports a verdict over a
scope it did not establish.** This hunt asked whether that class has siblings in
the repo's other proof surfaces. It does — thirty of them, across five clusters.

Five bounded read-only reviewers hunted; the parent reproduced each finding by
execution, with a discriminating control alongside (a variant that behaves
correctly), so "confirmed" here means the defective behavior was observed AND
isolated, not inferred from reading.

## The class, generalized

A proof surface is suspect when it:

- **(a)** accepts a degenerate or empty input and still returns PASS;
- **(b)** keys its verdict on a field that is constant or coarse where it must
  discriminate;
- **(c)** has a backstop suppressed by a condition the normal case satisfies;
- **(d)** reports PASS for a check that silently did not run;
- **(e)** lives only in the copy the caller chose, so an older caller carries no
  check at all;
- **(f)** computes a ratio whose denominator can empty or be silently narrowed.

## Status legend

`OPEN` — reproduced, not fixed. `FIXED` — fixed with a regression test.
`WONTFIX` — deliberate, with the reason recorded.

---

## Cluster A — provenance and repo-integrity guards

| id | Status | Defect | file:line |
| --- | --- | --- | --- |
| A1 | OPEN | The in-repo install source (the checked-in plugin tree) is exempt from the provenance guard as `same-tree` | `scripts/helper_provenance_lib.py:239` |
| A2 | OPEN | A non-empty drift list is discarded when the invoked entry script is absent from the target | `scripts/helper_provenance_lib.py:275` |
| A3 | OPEN | A deletion-only or rename-only staged commit schedules zero commit-boundary gates | `scripts/staged_commit_gate_plan_helpers.py:22`, `scripts/staged_commit_gate_plan.py:244,484` |
| A4 | OPEN | `validate_packaging` exits 0 on an empty manifest set, and it is the whole engine of the mirror-drift gate | `scripts/validate_packaging.py:425` |
| A5 | OPEN | `check_staged_reversion` prints a positive clean verdict whenever git fails | `scripts/check_staged_reversion.py:76` |
| A6 | OPEN | `check_staged_worktree_consistency` misses staged-then-deleted, and `CHARNESS_ALLOW_PARTIAL_STAGE=0` enables the bypass | `scripts/check_staged_worktree_consistency.py:41,52` |
| A7 | OPEN | Zero-file scans report a pass (`export-safe imports`, `bootstrap-shim consistency`) | `scripts/check_export_safe_imports.py:209`, `scripts/check_bootstrap_shim_consistency.py:94` |
| A8 | OPEN | Anchor-guard install/status keyed on a command basename; the matcher is never read back | `scripts/host_hook_install_lib.py:192,449` |
| A9 | OPEN | `own-root-unknown` is a silent pass; the anchors scan omits `support/` and `shared/` siblings | `scripts/helper_provenance_lib.py:237,156` |
| A10 | OPEN | `post_edit_skill_anchor_guard` fail-opens when the rule library is missing entirely | `scripts/post_edit_skill_anchor_guard.py:72` |

**A1 is the mechanism behind the 2026-07-27 foreign-copy incident.** The guard
returns `same-tree` when the running copy is *contained in* the target root, and
the packaging manifest declares the in-repo plugin tree — a full second
charness tree inside the repo — as the install source. So the copy that is stale
during every `mutate -> sync` window is structurally exempt. The RCA
(`charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md:57`) lists
this as candidate cause 4, refutes it *for that incident*, and never names the
in-repo install-source instance. Class (e).

Confirmed:

```text
status: same-tree | compared: None | drifted: None      # nothing compared
# after making the mirror's schema_version stale:
python3 plugins/charness/scripts/build_retro_lesson_selection_index.py --repo-root . --write
  -> "Wrote charness-artifacts/retro/lesson-selection-index.json."  exit 0, no refusal
  -> index now carries "schema_version": 0
python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check   -> fails
```

**A2** compounds it: `inspect_helper_provenance` computes `drifted` and then
returns `consuming-repo` — allowing the write — whenever the *entry script's*
filename is absent from the target. Confirmed: the verdict carries a non-empty
`drifted` list and `version_mismatch: True` while reporting `consuming-repo`.
Class (b): a coarse existence key overrides a discriminating list the function
already computed.

**A3** — `collect_staged_paths` uses `--diff-filter=ACM`, so `D` and `R` are
invisible. `git rm plugins/charness/skills/retro/SKILL.md` gives `ACM paths: 0`
→ `scheduled gates: 0` → the pre-commit hook exits 0 printing nothing, while
running the suppressed gate directly reports that the checked-in plugin public
skills do not match the source public skills. Class (c)+(d). Fix must separate the
*gate-scheduling* path list (needs D/R) from the *per-file validator* list
(needs existing files only).

**A4** — running `validate_packaging.py` against an empty root prints
`No packaging manifests found.` and exits 0. Since `check_staged_mirror_drift` inspects
only that returncode, an index with the packaging manifest staged for deletion
gets a green `staged plugin mirror matches staged sources` verdict. Class (a).

**A5** — `python3 scripts/check_staged_reversion.py --repo-root /tmp/not-a-repo`
→ `{"state": "clean", "findings": []}` exit 0. Its two siblings at the same
boundary raise instead. `git` exits 128 for a dubious-ownership repo, a common
container/CI state. Class (a)+(d).

**A6** — staged-then-deleted-on-disk: exit 0 (should flag; `--diff-filter=ACM` on
the unstaged side excludes `D`, and a deleted file is exactly the case
worktree-walking validators skip entirely). And `CHARNESS_ALLOW_PARTIAL_STAGE=0`
— the spelling an operator uses to turn the bypass *off* — turns it on
(control: no env var → exit 1, `=0` → exit 0).

---

## Cluster B — GitHub-issue closeout ledger (irreversible boundary)

| id | Status | Defect | file:line |
| --- | --- | --- | --- |
| B1 | OPEN | `N/A` passes every rung-1 ledger floor; the placeholder entry is unreachable dead code | `skills/public/issue/scripts/issue_verify_closeout_body.py:45,114` |
| B2 | OPEN | `Critique: blocked <17 chars>` skips the fresh-eye critique; the caller manufactures the allowed skip head | `skills/public/issue/scripts/issue_resolution_critique.py:64` |
| B3 | OPEN | The word `Answer:` in a staged artifact infers the fully-exempt `question` classification | `scripts/check_issue_closeout_commit_msg.py:118` |
| B4 | OPEN | The critique-to-issue binding accepts any standalone digit run, so a `Date:` line binds an unrelated critique | `skills/public/issue/scripts/issue_resolution_critique.py:91`, `scripts/check_prescribed_skill_executed_lib.py:43` |
| B5 | OPEN | An empty ledger field absorbs the following `Behavior #N:` line as its value | `skills/public/issue/scripts/issue_verify_closeout_body.py:139` |

**B1** — `_normalize_field_name` maps every non-`[a-z0-9]` run to a space
*before* the placeholder-set test, so the set's own `"n/a"` entry can never be
produced. Confirmed with the control that isolates it:

```text
all-N/A ledger  -> ok: True  | missing: []
same body, TBD  -> ok: False | missing: ['jtbd','root_cause','debug_artifact','prevention']
```

`_has_substantive_value` is the single predicate behind every ledger field,
behavioral verdict, AI provenance, HOTL disposition, and source-preservation
floor on all carriers. Class (b).

**B2** — the caller prepends `"host-blocked-subagent: "` itself, so the enum
check in `check_prescribed_skill_executed_lib` validates a constant the caller
supplied. Only `MIN_SKIP_LENGTH = 40` survives, and the manufactured prefix is
already 23 chars. Confirmed cliff:

```text
len=16 ok=False status=failed
len=17 ok=True  status=carrier_verified  skipped=[{'reason': 'host-blocked-subagent: xxxxxxxxxxxxxxxxx'}]
len=39 ok=True  status=carrier_verified  skipped=[... 'i did not feel like spawning a reviewer']
```

The top-level result is byte-identical to a real critique. Class (b)+(d).

**B3** — `_bare_classification` was hardened against exactly this and the
hardening was not applied to its sibling `_infer_classification`. Confirmed: the
same commit message exits 0 when the staged artifact merely contains `Answer:`
(classification `question`, so behavioral verdict / AI provenance / resolution
critique all report `applies: False`), and exits 1 when the artifact declares
`Classification: bug`. A non-blocking `REVIEW:` advisory does print — the only
mitigation. Class (b).

**B4** — `_token_matches` treats any digit cluster with non-alphanumeric
neighbours as a match, so `Date: 2026-07-27` binds #27 and #2026, `v0.42.1`
binds #42, `14:32:05` binds #32. Confirmed: a critique whose body says `Issue: #999` binds a #27 closeout, and
deleting only its `Date:` line flips the verdict to a binding failure. Class (b).

---

## Cluster C — critique record evidence floors

| id | Status | Defect | file:line |
| --- | --- | --- | --- |
| C1 | OPEN | The unedited scaffold's tier block validates green beside a `parent-delegated` claim it contradicts | `scripts/critique_reviewer_evidence.py:87,138` |
| C2 | OPEN | A body `Date:` back-dates a new artifact past all four date-gated floors; nothing cross-checks the filename | `scripts/validate_critique_artifacts.py:174` |
| C3 | OPEN | `- Packet consumed:` (bullet form) does not match the binding trigger, so the binding floor never runs | `scripts/critique_reviewed_input_binding.py:14` |
| C4 | OPEN | `--all` — the surface's own declared verify command — disables tier evidence, delivery state, and binding currency | `scripts/validate_critique_artifacts.py:549` |
| C5 | OPEN | `--paths <nonexistent>` reports `Validated 0 critique artifact(s).` and exits 0 | `scripts/validate_critique_artifacts.py:130`, `scripts/artifact_validator.py:458` |
| C6 | OPEN | The cross-surface probe reads the committed range only, and is silently off when `merge-base origin/main HEAD` fails | `scripts/validate_critique_artifacts.py:514`, `scripts/run-quality.sh:511` |

**C1** — `Requested tier: TODO ...` is truthy, and `pending-parent-spawn` is a
full typed value with an empty remainder, so the scaffold's own defaults satisfy
both floors permanently. Worse, nothing compares them to the
`Fresh-eye satisfaction` claim: an artifact can assert `parent-delegated` (a *completed*
delegation) while its own record says no reviewer was ever spawned and no
findings arrived. Confirmed: exit 0. `tests/test_critique_scaffold.py:92` pins
this as intended. Class (b).

**C2** — `_date_from_body(text) or _date_from_filename(path)`, with no agreement
check. The observed date gates the fresh-eye presence floor, the boundary
ownership floor, the delivery-state floor, and the reviewed-input binding floor.
Confirmed: the identical file named `2026-07-27-f2.md` exits 1 when its body
reads `Date: 2026-07-27` and exits 0 when it reads `Date: 2026-07-01`. Class (b).

**C3** — `PACKET_CONSUMED_RE` allows leading whitespace but not a list marker.
Confirmed: flush form exits 1 (`packet-bound critique must declare fields`),
bullet form exits 0. Two checked-in artifacts already use the bullet form, and
`scaffold_critique_artifact.py` never emits the line at all — the floor's own
producer does not emit its trigger. Class (d).

**C4** — under `--all`, `selected_paths` is empty so `require_tier_evidence` is
False for every artifact, and `check_current_binding` is False. Confirmed: a
`parent-delegated` artifact with no reviewer record exits 1 under `--paths` and
0 under `--all`. `.agents/surfaces.json:542` declares `--all` as this
validator's verify command. Combined with `changed_paths` being
working-tree-vs-HEAD, a committed artifact is only ever seen again by the weak
mode. Class (c).

---

## Cluster D — release claims (irreversible boundary)

| id | Status | Defect | file:line |
| --- | --- | --- | --- |
| D1 | OPEN | A `## Release State` heading with any suffix disables the entire five-entry ledger check; audit still reports `passed` | `skills/public/release/scripts/audit_public_release_narrative.py:44,66` |
| D2 | OPEN | The mutable-tag notes audit blocks the *pinned* pointer and passes `main`/raw pointers | same file, `:80` |
| D3 | OPEN | The same-proxy guard is a positional prefix match: flag order, wrappers, and absolute paths defeat it | `skills/public/release/scripts/publish_release_post_create.py:124` |
| D4 | OPEN | The HTTP distinct-channel probe confirms on any 200 with ≥1 body byte; content is never checked | same file, `:99` |
| D5 | OPEN | `validate_release_version_claim` silently no-ops when the claim is absent or reformatted, and a decoy first match shadows the real claim | `scripts/validate_current_pointer_freshness.py:160` |
| D6 | OPEN | The installed readback records `observed` on exit code alone; the version read back is never compared | `skills/public/release/scripts/release_observer.py:60` |
| D7 | OPEN | `check_real_host_proof` returns `not-required` for an empty scope, for a clean tree, and for an unconfigured repo, all indistinguishably | `skills/public/release/scripts/check_real_host_proof.py:124,146` |
| D8 | OPEN | The artifact asserts "a channel distinct from `gh release view`" even on the `same-proxy-flagged` and `skipped` records | `skills/public/release/scripts/publish_release_artifact_sections.py:171` |
| D9 | OPEN | `check_current_pointer_writes` reports clean over a scope excluding `skills/shared/` and any name-computed pointer path | `scripts/check_current_pointer_writes.py:16,54` |
| D10 | OPEN | Two more silent early-returns in the freshness validator (missing integrations dir, non-dict inventory) | `scripts/validate_current_pointer_freshness.py:222,226` |

**D1** — heading *presence* is a substring test, block *location* is an
exact-line test, and the disagreement fails open (`state_block is None` returns
early). Confirmed:

```text
## Release State (ledger)  -> status: passed  | blockers: []      # empty ledger
## Release State           -> status: blocked | blockers: 5       # same file
```

Class (d). This gates publish through `publish_release_cli.run_narrative_audit`.

**D2** — the blocker fires only when the ref equals the release tag, so the
immutable pointer is blocked and the pointer that changes on every commit passes.
Confirmed: three mutable pointers — a `blob/main/` link, a
`raw.githubusercontent.com` link, and a source-tree doc link — all yield
`passed` with an empty `notes_blockers` list;
re-pinning one to the tag → `blocked`. Class (b), with the discriminator
inverted. Also: the regex only examines `charness-artifacts/` paths (a
repo-specific literal inside a portable public skill), never matches
`raw.githubusercontent.com`, and the whole notes audit is skipped when
`notes_file is None`, which is the `--generate-notes` path.

**D3** — confirmed matrix (`flagged` = correctly refused as same-proxy):

```text
True   gh release view v2.11.2
True   gh   release  view   v2.11.2   --json url
False  gh release view --json url v2.11.2      # same command, flag moved
False  sh -c "gh release view v2.11.2"
False  env gh release view v2.11.2
False  /usr/bin/gh release view v2.11.2
```

D35 in [deferred decisions](../../docs/deferred-decisions.md) suspects
whitespace and trailing args —
**both are already caught**; D35 should be re-scoped to flag ordering and
wrappers, not closed as handled.

**D4** — confirmed against a local server returning a page that mentions no tag:
`{'status': 'confirmed', 'http_status': 200, 'evidence_len': 46}`. `urllib`
follows redirects silently, and `body` is used only for its length.

**D5** — confirmed: with three manifests that disagree with each other and with
the artifact, `- target version: **2.11.2**` (bold instead of backticks) →
`Validated rolling current-pointer freshness claims.` exit 0. And with a decoy
line earlier in the file matching the manifests, a genuinely stale claim below it
is never compared → exit 0. `re.search` takes the first match. Class (a)+(d).

**D6** — confirmed: target `2.11.2`, readback `charness 2.11.1`, disposition
`observed`. The value is stored in the durable JSON and never compared.

---

## Cluster E — mutation and coverage proof

| id | Status | Defect | file:line |
| --- | --- | --- | --- |
| E1 | OPEN | The mutation score is a global ratio sold as proof about the change; a changed file whose mutants all survive still PASSes | `scripts/check_mutation_score.py:160` |
| E2 | OPEN | `check_mutation_run_proof --claim score` returns `provable: true` with no facts at all; manifest mode never establishes the run was green | `scripts/check_mutation_run_proof.py:97,143` |
| E3 | OPEN | `--reuse-coverage --write-fresh-marker` stamps the freshness proof onto arbitrary coverage without running any probe | `scripts/check_changed_line_mutation_coverage.py:180` |
| E4 | OPEN | The freshness fingerprint is blind to `tests/` and to the test command, and degenerates to a per-base constant on an empty pool diff | `scripts/mutation_changed_files_lib.py:235` |
| E5 | OPEN | `check_coverage` reports 100% when it collected zero observations; files under 30 statements are exempt from the per-file floor | `scripts/check_coverage.py:356,366` |
| E6 | OPEN | A sampled file whose mutants were all filtered vanishes from every denominator and raises no signal | `scripts/check_mutation_score.py:229` |
| E7 | OPEN | The dirty-pool contamination detector fails open when git errors | `scripts/check_changed_line_mutation_coverage.py:190` |

**E1** — confirmed: 25 killed mutants in a fill file plus 5 survived mutants in
the changed file → `score=83.3 status=PASS passed=True blocking=[]`. Every
exclusion route (uncovered-line filter, 85% coverage filter, selection budget,
workload budget) is recorded under advisory keys that by construction never enter
the blocking set, so a change can be "100%-proven" by excluding everything hard.
Class (f).

**E2** — confirmed: `python3 scripts/check_mutation_run_proof.py --claim score`
→ `{"base_sha": null, "event": null, "provable": true}` exit 0. No argument
identifies a run. Class (a).

**E3** — confirmed end to end: a hand-written coverage JSON dated 2020-01-01 was
stamped fresh in **0.28s** (no probe ran), and the consumer then returned
`ok: True` with an empty `blocking` list. Class (d).

**E4** — confirmed: appending a line to a test file leaves the fingerprint
byte-identical (`d431916b…` before and after), and on a clean tree the digest
equals the hand-computed constant `sha256(marker + base_sha)` for the fixed
`charness-changed-pool-fingerprint-v1` marker — a digest of nothing. Class (a)+(b).

**E5** — confirmed: `coverage= 1.0 covered= 0 total= 0 violations= []`. Zero
denominator fails open to 1.0. Class (f).

**E6** — confirmed: a changed file whose five mutants were all filtered as a
trivial entry guard yields `scope_gap=0`, `per_file_ok=True`, an empty
incomplete list, and `score=100.0 PASS`. Only the "Filtered uncovered mutation line" reason counts as a scope gap.
Class (f).

---

## What is NOT claimed here

- No fix has landed. Every id above is `OPEN`.
- A5, A7, D7, E5 and the empty-input cases are reproduced against synthetic
  roots; they are real behaviors of the code, not observed production incidents.
- A8, A9, A10, B5, C6, D8, D9, D10, E7 were reported by reviewers and are
  **not** parent-reproduced (everything else in this file is). They carry the
  reviewers' file:line and reasoning; treat them as leads until run.
- The reviewers had no shell. Confirmation is the parent's execution, and every
  confirmed item above was run with a control variant that behaves correctly, so
  a passing control rules out "the harness was broken".

## Suggested order for the fix sessions

1. **A1 + A2** — the live incident mechanism, and the guard that would otherwise
   still be bypassable after A1 is fixed.
2. **A3 + A4 + A5** — the commit boundary. A3 in particular means an entire class
   of commit is ungated today.
3. **B1 + B2 + B3** — the issue-close carrier, where a false PASS closes a real
   issue on GitHub.
4. **D1 + D5** — the publish gate and the only standing release-version
   cross-check.
5. **C1 + C2 + C3 + C4** — the critique evidence floors, which every other
   closeout leans on.
6. **E1 + E2 + E3 + E6** — test-strength claims. Bigger design questions:
   per-changed-file discrimination is a contract change, not a patch.

A cheaper cross-cutting move worth deciding first: several of these are one
predicate — "an empty or unestablished scope must not return PASS". A shared
helper that forces every gate to emit `scope: evaluated | empty | not-configured`
alongside its verdict would close A4, A7, C5, D7, E2, E5 as a family rather than
one at a time.
