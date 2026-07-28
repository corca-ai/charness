# Evidence-Surface Bug Hunt — Verdicts Over Unestablished Scope
Date: 2026-07-27
Status: 30 defects reproduced by execution. A4, A7, C5 fixed and E2 partially
fixed on 2026-07-27 as the empty-scope family; A1, A2 fixed and A9 partially
fixed on 2026-07-27 as the containment family
([spec Decision 2](../spec/2026-07-27-foreign-copy-write-enforcement.md)); A3
fixed the same day, on its own; B3 fixed, B2 fixed-narrowed and B1 partially
fixed on 2026-07-27 as the issue-close carrier family; D1, D3, D5 fixed and D2
partially fixed on 2026-07-27 as the publish-gate family; D2, D6, D8 fixed and
D4 partially fixed on 2026-07-28 as the distinct-channel family; D7, D9, D10, E5
fixed on 2026-07-28 as the empty-scope family remainder.

**Remaining: 11 OPEN + 6 PARTIAL.** Count fully-open rows and partial rows
separately; a PARTIAL is not a landed row, and rolling them into a single
"N remain" figure is the same class of claim this file exists to hunt.
This file is the tracking record — update the Status column as items land.

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
`PARTIAL` — one half fixed, the remainder scoped in the row. `WONTFIX` —
deliberate, with the reason recorded.

---

## Cluster A — provenance and repo-integrity guards

| id | Status | Defect | file:line |
| --- | --- | --- | --- |
| A1 | FIXED | The in-repo install source (the checked-in plugin tree) is exempt from the provenance guard as `same-tree` | `scripts/helper_provenance_lib.py` (`inspect_helper_provenance`) |
| A2 | FIXED | A non-empty drift list (and a version mismatch) is discarded when the invoked entry script is absent from the target | `scripts/helper_provenance_lib.py` (`inspect_helper_provenance`) |
| A3 | PARTIAL | A deletion-only or rename-only staged commit schedules zero commit-boundary gates — scheduling fixed; what the scheduled gates then *inspect* is the residual (see below) | `scripts/staged_commit_gate_plan_helpers.py` (`collect_staged_scope_paths`), `scripts/staged_commit_gate_plan.py` (`staged_commit_gate_plan`, `run_predict_commit`) |
| A4 | FIXED | `validate_packaging` exits 0 on an empty manifest set, and it is the whole engine of the mirror-drift gate | `scripts/validate_packaging.py:425` |
| A5 | OPEN | `check_staged_reversion` prints a positive clean verdict whenever git fails | `scripts/check_staged_reversion.py:76` |
| A6 | OPEN | `check_staged_worktree_consistency` misses staged-then-deleted, and `CHARNESS_ALLOW_PARTIAL_STAGE=0` enables the bypass | `scripts/check_staged_worktree_consistency.py:41,52` |
| A7 | FIXED | Zero-file scans report a pass (`export-safe imports`, `bootstrap-shim consistency`) | `scripts/check_export_safe_imports.py:209`, `scripts/check_bootstrap_shim_consistency.py:94` |
| A8 | OPEN | Anchor-guard install/status keyed on a command basename; the matcher is never read back | `scripts/host_hook_install_lib.py:192,449` |
| A9 | PARTIAL | `own-root-unknown` is a silent pass (OPEN); the anchors scan omitted `support/` and `shared/` siblings (fixed with A1/A2 in `_tracked_files` / `counterpart_path`) | `scripts/helper_provenance_lib.py` (`inspect_helper_provenance`, `_tracked_files`) |
| A10 | OPEN | `post_edit_skill_anchor_guard` fail-opens when the rule library is missing entirely | `scripts/post_edit_skill_anchor_guard.py:72` |

**A1 is NOT the 2026-07-27 incident's mechanism — it is a second, live escape in
the same guard.** That incident's cause was the guard being *absent* from the
copy that ran, verified by `git cat-file`; its copy lived outside the target root
so the containment branch was never reached. A1 is the branch itself: the guard
returns `same-tree` for any copy *contained in* the target root, and this repo's
packaging manifest declares the checked-in plugin tree — a full second charness
tree inside the repo — as an install source. So an install from that source is
structurally exempt during every `mutate -> sync` window. Same failure mode,
different caller. The RCA listed this as candidate cause 4 and refuted it for
that incident; the refutation has now been scoped in place so it does not read as
"fixed". Class (e).

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

**A3 — what landed, and what did not (2026-07-27).** Scheduling is fixed both
ways: a deletion and a detected rename now plan the same gates a modification
does (measured 0 -> 6 for a `plugins/**` deletion, 0 -> 6 for a rename, control
modification unchanged), and the per-file list is now *derived* from that scope by
`is_file()` rather than queried with `ACM`, so a renamed-and-edited file finally
gets `py_compile`/`ruff`/lengths — before the fix a rename with a syntax error in
the destination planned none of the three. Three residuals are NOT closed and the
row stays `PARTIAL` because of them:

1. **Scheduled is not judged.** Of the gates a deletion schedules, only
   `check_staged_mirror_drift` reads the *index*; `check_doc_links` and friends
   walk the worktree, and `check_staged_reversion` passes a genuine deletion by
   design. So `git rm --cached docs/x.md` schedules the doc gates and they see the
   file still on disk. The hook now prints gate names and `ok` over a deletion most
   of those gates did not inspect — legible assurance where there used to be
   silence, which is class (d) in a more trusted form.
2. **`git revert` and auto-merge never reach this hook at all.** Probed: with
   `core.hooksPath` set, `git revert HEAD` ran no pre-commit hook. Reverting a sync
   commit can still land a mismatched mirror with nothing having run. Pre-push
   remains the floor for that shape.
3. **A5 and A6 sit inside the new floor.** The index-hygiene trio a deletion now
   always schedules is `check_staged_reversion` (A5: prints a clean verdict when
   git fails), `check_git_identity`, and `check_staged_worktree_consistency` (A6:
   blind to the staged-then-deleted case). Fixing those raises what this floor is
   worth.

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
| B1 | PARTIAL | `N/A` passes every rung-1 ledger floor; the placeholder entry is unreachable dead code — the entry is reachable now, but B5 still absorbs a bare placeholder into the following line (see below) | `skills/public/issue/scripts/issue_verify_closeout_body.py:45,114` |
| B2 | FIXED (narrowed) | `Critique: blocked <17 chars>` skips the fresh-eye critique; the caller manufactures the allowed skip head — the length cliff and the silent-skip legibility are closed; the vacuous enum check is unfixable at rung-1 and stays scoped below | `skills/public/issue/scripts/issue_resolution_critique.py:64` |
| B3 | FIXED | The word `Answer:` in a staged artifact infers the fully-exempt `question` classification | `scripts/check_issue_closeout_commit_msg.py:118` |
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

**B1/B2/B3 — what landed, and what did not (2026-07-27).** All three repros are
closed with controls; three bounded reviewers then found four things the fixes
themselves got wrong or left silent, each repaired inside this slice.

1. **B1 is PARTIAL because B5 outlives it.** The declared `n/a` placeholder is
   reachable now (`N/A` behaves exactly as `TBD` always did), but `_body_fields`
   appends any non-field line to the *preceding* field, so `Prevention: N/A`
   followed by a `Behavior #42:` line still normalizes to a substantive value.
   Measured: the all-`N/A` ledger reports 5 missing fields when nothing follows
   it, and 3 when a `Behavior` line does. Bare-`N/A` refusal therefore holds only
   for a field with no continuation line. That is B5, still `OPEN`.
2. **B1 moved one floor toward PASS, deliberately and pinned.**
   `evaluate_source_preservation` uses the same predicate as a gate-*opener*, so
   `Source origin: N/A` flipped from refused to exempt. That reading is right — a
   bare `N/A` origin asserts no external source, as omitting the field does, and
   the old behavior demanded a preservation form for a source that does not
   exist — but it is a floor loosening inside a tightening fix, so it carries its
   own test rather than living as a side effect.
3. **B2's real tooth is legibility, not length.** The enum head is manufactured
   by the caller on this carrier, so the enum check validates a constant and
   cannot be fixed at rung-1. The length floor now measures only author-written
   text (`MIN_SKIP_DETAIL_LENGTH = 20`; the head's 23 characters no longer pay
   it), which closes the confirmed 17-character cliff. It is set at 20 and not at
   the 40-char total, because the repo's own genuine host signals run 24-39
   characters — a 40-char detail floor sits above honest usage and buys padding.
   **A fluent 40-character excuse still passes, and no length floor can refuse
   one.** What changed is that a skipped critique is no longer byte-identical to
   an executed one: every issue carrier now emits a non-blocking `REVIEW: … was
   SKIPPED` line. The class-(b) verdict here is narrowed, not closed.
4. **B3's first fix was a regression.** Removing the loose `question` inference
   is right, but the same edit dropped the `root cause:`/`debug artifact:` →
   `bug` branch as "redundant with the `bug` fallback". It is not: it precedes
   the `feature` branch, and a real bug closeout carries both `Root cause:` and
   `Implementation:`. Measured — such a body classified `feature`, whose ledger
   demands neither `debug_artifact` nor the `siblings` decision-and-proof check,
   so the fix silently dropped two bug-only floors before the branch was
   restored. This is the fourth slice in a row where the review defect was inside
   the fix.
5. **B3 had a sibling escape on the other carrier.** The bare close-keyword path
   reads the commit body with fences deliberately unstripped (GitHub auto-closes
   on a fenced `Fixes #123`), and reused that raw text to read the
   classification — so `Classification: question` inside a *pasted code fence*
   asserted the exemption. Close keywords now read raw; the classification reads
   stripped.

Leads opened by the reviewers and **not** fixed here (out of B1-B3 scope, none
parent-reproduced except where noted): `publish_release_preflight.py:251` is the
same manufactured-head carrier at the publish boundary and got the floor but no
advisory; `docs/prescribed-skill-closeout-contract.md` described a placeholder
check the helper never had (fixed); `_CLASSIFICATION_RE` rejects the trailing
period in `Classification: bug.`, which is the dominant checked-in convention, so
those artifacts reach the floors by inference rather than declaration (harmless
now that the `root cause:` branch is restored, live if it is removed again);
`release_issue_closeout_message.py:9` lacks the bold `**Classification**:` form
the hook has; and `check_resolution_critique` judges only `checks[0]` on the
single-issue path, so a valid critique line followed by an invalid one reports
`ok: True`. `none` is still not a placeholder value, and is a likelier
hand-written empty than `N/A` was.

**B4** — `_token_matches` treats any digit cluster with non-alphanumeric
neighbours as a match, so `Date: 2026-07-27` binds #27 and #2026, `v0.42.1`
binds #42, `14:32:05` binds #32. Confirmed: a critique whose body says `Issue: #999` binds a #27 closeout, and
deleting only its `Date:` line flips the verdict to a binding failure. Class (b).

---

## Cluster C — critique record evidence floors

| id | Status | Defect | file:line |
| --- | --- | --- | --- |
| C1 | FIXED | The unedited scaffold's tier block validates green beside a `parent-delegated` claim it contradicts | `scripts/critique_reviewer_evidence.py:87,138` |
| C2 | FIXED | A body `Date:` back-dates a new artifact past all four date-gated floors; nothing cross-checks the filename | `scripts/validate_critique_artifacts.py:174` |
| C3 | FIXED (narrowed) | `- Packet consumed:` (bullet form) does not match the binding trigger, so the binding floor never runs | `scripts/critique_reviewed_input_binding.py:14` |
| C4 | FIXED (narrowed) | `--all` — the surface's own declared verify command — disables tier evidence, delivery state, and binding currency | `scripts/validate_critique_artifacts.py:549` |
| C5 | FIXED (narrowed) | `--paths <nonexistent>` reports `Validated 0 critique artifact(s).` and exits 0 | `scripts/validate_critique_artifacts.py:130`, `scripts/artifact_validator.py:458` |
| C6 | PARTIAL | The cross-surface probe reads the committed range only, and is silently off when `merge-base origin/main HEAD` fails | `scripts/validate_critique_artifacts.py:514`, `scripts/run-quality.sh:511` |

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

**C1/C2/C3/C4/C6 — what landed, and what did not (2026-07-28).** The critique
evidence floor, taken as ONE subsystem rather than five patches: every floor here
is conditional — on a date, a selection mode, a probe config, or a trigger line
the artifact itself supplies — and each condition was independently satisfiable
in silence. The enforcement-scope concept now lives in
`scripts/critique_enforcement_scope.py` and the run prints what it did NOT
establish. All five reproduced with controls before the fix; the whole 650-artifact
corpus stays green after it.

Three bounded reviewers then found **eleven** defects in the fixes, every one
reproduced by execution before repair. **This is the seventh consecutive slice
where the review defect was inside the fix**, and the sharpest one is again the
class under repair:

1. **The scope record reproduced the class it was added to close.** `on_complete`
   runs unconditionally, but the probe is resolved inside `validate_factory`,
   which the shared runner calls only when artifacts exist. So a run that passed a
   perfectly good `--changed-ref` and simply found no critique artifact printed
   `cross-surface-probe=not-established (… no --changed-ref/--changed-path
   resolved …)` — asserting a resolution that never ran, on the common
   `run-quality.sh` path. Now `not-resolved`, its own state.
2. **C4's fix handed C4 back through `observed_date is None`.** The new
   date-keyed requirement read `is not None and >= RULE_DATE`, so an undatable
   artifact was fully exempt under `--all` — through the one input this module's
   own docstring names as never fail-open, while every sibling floor obeys that
   rule. Becoming undatable is easy and often accidental (`**Date:**`, or an
   undated filename, both already in the corpus).
3. **C1a was defeated by three characters of markup.** `_section_field_map`
   strips only backticks, and the stub check tested the raw value, so `**TODO**`
   passed while `TODO` was refused — in the one function the slice added, whose
   two siblings in the same file already normalize leading markup.
4. **C1b's trigger was shadowable and fence-blind.** `fresh_eye_satisfaction_status`
   returned the FIRST line containing the phrase, so an earlier sentence — or a
   fenced quotation of the canonical form, which a critique *of this validator*
   is very likely to contain — became the artifact's asserted claim. Fenced text
   is shown, not asserted: this repo's own standing lesson, live again.
5. **C1b covered only half its own claim set.** `nested-delegated` asserts a
   completed delegation too and got the consistency check for free.
6. **C3's widening created the over-block twin of the hole it closed.**
   `- Packet Consumed: n/a (no adapter sections)` — the corpus's own way of
   writing "no packet" — became a trigger demanding three SHA256 fields for a
   packet the artifact had just said does not exist. A refusal with no possible
   remediation, which is the release-notes over-block class inverted. The trigger
   now reads the declared VALUE, not just the line.
7. **C3 still missed the corpus's only genuine bullet declaration**, which wraps
   the path onto the next line. Wrapped and bold forms are handled now.
8. **The scaffold pre-loaded three failures it never disclosed.** Its fresh-eye
   and boundary placeholders say "replace with"; the tier block read as a
   descriptive hint, so an author filled the two marked surfaces, submitted, and
   was refused on a third — one guaranteed extra validator round-trip per
   critique, forever. The scaffold now names the rule and the `n/a` escape.
9. **One fix was a floor addition smuggled in as a repair.** Routing the
   tier-evidence trigger through the completed-delegation set would have demanded
   a whole tier section for `nested-delegated`, whose absent evidence link this
   module records as a known, accepted boundary. Caught by the existing suite;
   narrowed back to `parent-delegated`.
10. `binding-currency=evaluated` reported the run MODE, not evaluation — the same
    overclaim the bare artifact count makes. Now `binding-currency-check=enabled|
    disabled`. And an unrecognized probe state rendered as `evaluated`, the one
    value that asserts the probe ran.
11. The scope record was invisible on failing runs, which is exactly where the
    silently-skipped floors stay silent. It now prints on both paths.

**C3, C4 and C6 are narrowed or partial, not closed:**

- **C3** still does not match the `## Packet Consumed` heading form (~20 checked-in
  release critiques) or a mid-line mention. Both need a different parse than a
  line trigger, and every widening of a CONTENT trigger also fires on an artifact
  that merely discusses this surface.
- **C4** closes the tier-evidence and delivery-state halves in every mode.
  Binding CURRENCY stays off under `--all` deliberately — a full sweep re-reads
  historical bindings that are stale by design — and is now named rather than
  silent.
- **C6** distinguishes `not-configured` / `not-established` / `not-resolved` /
  `evaluated (match|no match)`, which closes the "off is indistinguishable from
  clean" half. It does NOT close the other half: the probe still reads the
  COMMITTED range, so the slice under critique — which is in the worktree at
  validation time, because verify precedes commit — is invisible to it. Closing
  that needs the probe to read the working tree, which is a contract change.
- **C2's residual, stated:** when only one date channel parses, that channel
  decides alone. Corroboration is unavailable, not achieved.

Two findings outside this slice's scope, recorded rather than folded in:
`scripts/validate_retro_artifact.py:136` still uses the body-first `or` fallback
that C2 replaced, so the retro floors remain back-dateable; and
`LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS` names two prepare packets that
`candidate_paths` excludes by content kind, so both entries are dead allowlist
rows that read as live grandfather decisions.

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
| D1 | FIXED | A `## Release State` heading with any suffix disables the entire five-entry ledger check; audit still reports `passed` | `skills/public/release/scripts/audit_public_release_narrative.py:44,66` |
| D2 | FIXED | The mutable-tag notes audit blocks the *pinned* pointer and passes `main`/raw pointers | same file, `:80` |
| D3 | FIXED | The same-proxy guard is a positional prefix match: flag order, wrappers, and absolute paths defeat it | `skills/public/release/scripts/publish_release_post_create.py:124` |
| D4 | PARTIAL | The HTTP distinct-channel probe confirms on any 200 with ≥1 body byte; content is never checked — content is checked now, but the channel still cannot tell a released tag from a pushed one (measured) | same file, `:99` |
| D5 | FIXED | `validate_release_version_claim` silently no-ops when the claim is absent or reformatted, and a decoy first match shadows the real claim | `scripts/validate_current_pointer_freshness.py:160` |
| D6 | FIXED | The installed readback records `observed` on exit code alone; the version read back is never compared | `skills/public/release/scripts/release_observer.py:60` |
| D7 | FIXED | `check_real_host_proof` returns `not-required` for an empty scope, for a clean tree, and for an unconfigured repo, all indistinguishably | `skills/public/release/scripts/check_real_host_proof.py:124,146` |
| D8 | FIXED | The artifact asserts "a channel distinct from `gh release view`" even on the `same-proxy-flagged` and `skipped` records | `skills/public/release/scripts/publish_release_artifact_sections.py:171` |
| D9 | FIXED | `check_current_pointer_writes` reports clean over a scope excluding `skills/shared/` and any name-computed pointer path | `scripts/check_current_pointer_writes.py:16,54` |
| D10 | FIXED | Two more silent early-returns in the freshness validator (missing integrations dir, non-dict inventory) | `scripts/validate_current_pointer_freshness.py:222,226` |

**D1** — heading *presence* is a substring test, block *location* is an
exact-line test, and the disagreement fails open (`state_block is None` returns
early). Confirmed:

```text
## Release State (ledger)  -> status: passed  | blockers: []      # empty ledger
## Release State           -> status: blocked | blockers: 5       # same file
```

Class (d). This gates publish through `publish_release_cli.run_narrative_audit`.

**D1/D2/D3/D5 — what landed (2026-07-27).** All four repros closed with
both-direction controls. Two bounded reviewers then found **ten** further defects
in the fixes themselves, every one confirmed by execution before repair — the
same pattern as the B1-B3 slice, now five slices running.

The one that mattered most: **the D1 fix reproduced D1.** `_release_state_block`
takes the FIRST matching heading and was fence-blind, so an artifact documenting
the ledger format in a code fence satisfied all five entry checks while its real
`## Release State` section below was empty — a false PASS at the publish
boundary, D1's own escape class surviving the D1 fix. Both audits now read
`strip_display_code(...)`: content rendered as code is shown to the reader, not
asserted by the author.

The rest, grouped:

- **D2 over-reach.** Dropping the repo-specific path literal made the rule fire
  on any source-tree link, including third-party ones whose remediation ("pin to
  the release tag `v2.11.3`") is impossible. Fence-stripping resolves the real
  case (install one-liners are fenced). `_IMMUTABLE_REF_RE` also over-blocked
  short shas, `v1.0`, and the `refs/tags/` raw form, while missing `tree/main`
  with no path. All fixed; a branch NAMED like a version is still accepted, which
  is not decidable from a ref string and is now stated rather than implied.
- **D3 left four bypasses and added one over-flag.** An unparseable command
  failed OPEN, so one apostrophe in a `#` comment ran the identical query under
  bash while the guard reported "distinct". Only the first token was
  basename-normalized, so `sudo /usr/bin/gh ...` escaped though each half alone
  was caught. Omitting the tag escaped — and `gh release view` with no tag
  resolves to the LATEST release, which moments after publish is the one being
  confirmed. The unwrap budget could be exhausted silently. And a degenerate
  `release_view` template made the guard refuse `gh api` or pass everything; it
  now declines to render a verdict it cannot establish and records
  `same_proxy_guard: inconclusive-...` instead of leaving absence to read as a
  passed check.
- **D5 turned correct pointers stale.** The three claim renderings nest, and the
  capture kept the residue: `**`2.11.3`**` compared backticks-and-all. A trailing
  period did the same. `target version: TBD` was compared as a version, reporting
  "manifest is X, pointer claims TBD" — the wrong diagnosis for the condition the
  absent-claim branch correctly calls unestablished. Fenced captured tool output
  is no longer scanned for claims.

**D2 stays PARTIAL:** the notes audit still never runs on the `--generate-notes`
path (`notes_file is None`), which is the default publish path. Auto-generated
notes are commit messages and PR text — a prime carrier of `blob/main` links.
Closing that needs a post-create readback of the published body, which belongs
with D4/D6/D8.

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

**D2/D4/D6/D8 — what landed (2026-07-28).** All three repros closed plus D2's
`--generate-notes` residual. One bounded reviewer found **four blockers** in the
fixes, each then confirmed by execution:

1. **The D2-residual audit never ran.** It was wired `run=cli.run_shell`, which
   uses `shell=True`, where a LIST makes `args[0]` the command and drops the rest
   into `$0,$1,...`. Measured: `run_shell(["git","status","--short"])` executes
   bare `git` and exits 1, while `run(...)` returns short-format output. Every
   publish would have recorded `unavailable` — **closed-looking, not closed.**
2. **A non-`gh` backend would have stranded the publish.** `backend_command`
   raises `SystemExit` for an undeclared op, `SystemExit` does not derive from
   `Exception`, and this call sits after `create_release` and outside the
   rollback wrapper. Confirmed escaping. It now catches `BaseException` and
   records `not-configured`; `release_view_body` is documented in the adapter
   contract as the one op a backend may safely omit.
3. **An empty published body recorded `clean`** — a PASS over a scope never
   established, class (a) reintroduced by the fix for class (d). Now
   `unestablished`.
4. **The D8 fix branched on the wrong field.** Distinctness is a property of the
   same-proxy GUARD, not the status: a probe of literally `gh release view v1`
   reaches `confirmed` when the caller omits `backend`/`backend_command`, and an
   `inconclusive-degenerate-template` guard coexists with `confirmed`. Confirmed
   rendering "(a channel distinct from `gh release view`)" over a
   `gh release view` probe — D8's exact failure mode surviving the D8 fix. The
   guard's own verdict is rendered now.

Also folded in: the D6 comparison used a substring, so `2.11.3` matched
`2.11.30` and — worse — matched the trailer in `charness 2.11.1 (latest 2.11.3
available)`, reporting a match while the wrong version was installed. The
reported version is now the first version-shaped token and must EQUAL the
expected one. And `published_notes_audit` reached nobody: it lived only in the
publish run's stdout JSON, so it is now rendered into the release artifact.

**D4 stays PARTIAL, and this is the important part.** The content check closes
the "any 200 with any body" hole. It does NOT make the probe proof that a
release exists. Measured on the live repo: `releases/tag/v0.1.1` — a pushed tag
with **no** GitHub release — returns HTTP 200 with the tag present 23 times, and
both that page and a real release page title themselves `Release <tag>`. The
publish flow pushes the tag before creating the release, so this channel cannot
distinguish "the release exists" from "the tag was pushed". The unauthenticated
REST API, which does distinguish, answered 403 (rate-limited) and is not a
dependable default. The record therefore carries `establishes` and
`does_not_establish`, and the artifact renders both, rather than letting
`confirmed` be read as the stronger claim. Closing this needs a release-specific
channel that does not depend on unauthenticated API quota.

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

**D7/D9/D10/E5 — what landed (2026-07-28).** The empty-scope family remainder.
Each surface now names the scope its verdict covers instead of returning one
value for several different worlds. D9 and D10 were unreproduced leads; both were
parent-reproduced first.

- **D7** returned `required: False` identically for an unconfigured repo, a
  configured repo handed an EMPTY changed scope, and a configured repo whose
  triggers genuinely did not match — four worlds, one sentence. Now
  `evaluation_scope: evaluated | empty | not-configured | not-established`.
- **D9** omitted `skills/shared` from `SCAN_ROOTS` (an identical violation was
  caught under `scripts/` and `skills/public/` and invisible under
  `skills/shared/`), and matched string constants only, so a computed
  `f"latest.{ext}"` was unseeable — and the prefilter required the literal
  filename, so such a file never reached the AST scan at all.
- **D10** had two silent early-returns: with a genuinely stale claim in place,
  deleting the integrations directory or corrupting the inventory shape flipped
  BLOCK to PASS.
- **E5** reported `coverage: 1.0` over zero observations, and the sub-30-statement
  per-file exemption silently dropped files — a 0%-covered 29-statement file
  vanished while the same file at 30 statements was a violation.

A bounded reviewer then found **two blockers and four findings**, all reproduced
by execution:

1. **E5's own fix hard-broke the gate.** `coverage: None` reached
   `summary["coverage"] < args.min_coverage`; confirmed `TypeError: '<' not
   supported between instances of 'NoneType' and 'float'` — a traceback instead
   of this gate's own error. It now refuses legibly. The headline E5 change had
   **no test at all**, which is why it shipped.
2. **D7's scope never reached the reader.** `real_host_lines` branched on
   `required` alone, so the release artifact still said "No configured
   release-time real-host proof trigger matched this slice" over a record whose
   scope was `empty` — a sentence asserting an evaluation that never happened,
   at the publish boundary. D8's failure mode inside the D7 fix.
3. D9's computed detector missed the **dominant idiom** — `target = out /
   f"latest.{ext}"` then `target.write_text(...)`, whose literal twin the gate
   already handled — and its `BinOp` branch read only the left operand, so in
   `str(out) + "/latest." + ext` the pointer-ish literal (always a RIGHT operand
   under left-associative parsing) was never inspected.
4. D10 misdiagnosed unreadable JSON as a shape error, and had no
   `schema_version` gate — a future schema would be reported as "regenerate the
   catalog" rather than "this validator does not read schema N".
5. E5's unmeasured files were filed under the small-file exemption with
   `coverage: 1.0`, so being at the floor kept them OUT of `exempt_below_floor`,
   the list documented as the hidden population. The fix for a silent exemption
   would have reintroduced one a layer down.
6. A key collision: D7's bare `scope` landed on the same dict `plan_release_run`
   stamps `evidence_scope` onto. Renamed `evaluation_scope`.

The reviewer's angle-1 hypothesis — that D9's widened prefilter would produce
live false positives — was checked and **refuted**: the prefilter emits no
findings, and a whole-tree scan of every `latest`-bearing f-string and
concatenation under the four scan roots produced none. Recorded as a negative
result rather than dropped.

---

## Cluster E — mutation and coverage proof

| id | Status | Defect | file:line |
| --- | --- | --- | --- |
| E1 | OPEN | The mutation score is a global ratio sold as proof about the change; a changed file whose mutants all survive still PASSes | `scripts/check_mutation_score.py:160` |
| E2 | PARTIAL | score claim with no facts returned `provable: true` — FIXED; the manifest path still cannot establish the run was green, now reported as `conclusion_established: false` rather than refused | `scripts/check_mutation_run_proof.py:86,109` |
| E3 | OPEN | `--reuse-coverage --write-fresh-marker` stamps the freshness proof onto arbitrary coverage without running any probe | `scripts/check_changed_line_mutation_coverage.py:180` |
| E4 | OPEN | The freshness fingerprint is blind to `tests/` and to the test command, and degenerates to a per-base constant on an empty pool diff | `scripts/mutation_changed_files_lib.py:235` |
| E5 | FIXED | `check_coverage` reports 100% when it collected zero observations; files under 30 statements are exempt from the per-file floor | `scripts/check_coverage.py:356,366` |
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

- Fixes have landed for the rows whose Status column says so (A4, A7, C5, E2
  partial on the empty-scope slice; A1, A2, A9 partial on the containment
  slice; A3 partially, on its own; B3, B2 narrowed and B1 partial on the
  issue-close carrier slice). Every other id above is `OPEN`. The Status column
  is the current truth; this section is not a second status register.
- B2 is `FIXED (narrowed)`, not closed: the length cliff and the silent-skip
  legibility are fixed, and a fluent excuse of sufficient length still passes.
  B1 is `PARTIAL`: bare-`N/A` refusal is real but B5 absorbs a placeholder into
  the following line, so an all-`N/A` ledger is not uniformly refused.
- A5, A7, D7, E5 and the empty-input cases are reproduced against synthetic
  roots; they are real behaviors of the code, not observed production incidents.
- A8, A10, B5, C6, D8, D9, D10, E7 were reported by reviewers and are
  **not** parent-reproduced (everything else in this file is). They carry the
  reviewers' file:line and reasoning; treat them as leads until run.
- A9 was in that lead set. Its *anchors-scan-omits-`support`/`shared`* half was
  reproduced on the live tree before it was fixed — a `tree` scan of
  `plugins/charness` resolved no counterpart for exactly 4 of 605 modules
  (`shared/scripts/*.py`) and 0 of 605 after the remap, and the sibling-glob
  half has a regression test that fails against the pre-fix module. Its
  *`own-root-unknown` is a silent pass* half remains an unreproduced lead.
- The reviewers had no shell. Confirmation is the parent's execution, and every
  confirmed item above was run with a control variant that behaves correctly, so
  a passing control rules out "the harness was broken".

## Suggested order for the fix sessions

1. **A1 + A2** — the live incident mechanism, and the guard that would otherwise
   still be bypassable after A1 is fixed. (Landed.)
2. **A3 + A4 + A5** — the commit boundary. A3 meant an entire class of commit was
   ungated; A4 landed and A3 landed partially (scheduling fixed, inspection
   residuals recorded above). A5 remains, and it is now inside A3's floor.
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
