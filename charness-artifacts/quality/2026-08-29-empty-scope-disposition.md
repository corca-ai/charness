# Quality Review
Date: 2026-08-29

Title: Empty-scope detector disposition

## Scope

Source-code judgment of the 13 detectors classified by `inventory_empty_scope_honesty.py` as `positive-verdict-over-zero`; the bucket is evidence, not an automatic defect verdict. No detector, test, gate, or current pointer changed.

## Surface Contract Review

- semantic coverage: observed — all 13 detector sources, the refusal test, and both staged-state examples were read.
- surface: empty-scope discovery, named-scope refusal, and read-failure behavior of the 13 detectors.
- owner: detector source, with `tests/quality_gates/test_empty_scope_refusals.py` owning the asymmetry.
- projections: scope calls, empty/read-failure states, exit codes, and operator output.
- state scope: empty-repository probe plus source; no repairs executed.
- transitions: none; this record does not arm or alter a gate.
- proof boundary: line-referenced source evidence and reproduced inventory count.
- unexamined axes: the other 117 detectors, implemented repairs, and independent live-host behavior.

## Current Gates

The probe reproduced 130 detectors and 13 bucket findings. The disposition follows.

| detector path | verdict | evidence | repair (DEFECT only) |
| --- | --- | --- | --- |
| `scripts/check_code_lengths.py` | SANCTIONED | `iter_python_targets` calls `iter_matching_repo_files` (212-214); default discovery uses it (313-315). Named-empty paths raise `ValidationError` (376-395), and tokei/listing failures raise rather than fabricate counts (125-166). Empty default is the discovered-empty code-family pass. | — |
| `scripts/check_current_pointer_writes.py` | SANCTIONED | Scope is `iter_matching_repo_files(... require_git=require_git)` (95-96), consumed by `scan_repo` (390-400). The CLI forwards strict listing (412-416), so that failure is not clean; an empty returned set means no Python family. | — |
| `scripts/check_doc_links.py` | SANCTIONED | `main` establishes `docs` and `late_docs` with `iter_matching_repo_files` (510-515), then reads each doc directly (516-518); strict listing is available (506-510), and read failure is uncaught. Zero Markdown docs is a real no-link family. | — |
| `scripts/check_markdown_inline_code.py` | DEFECT | Discovery calls `iter_matching_repo_files` (107-109), but named `--path` targets skip existence validation (127-135); nonexistent targets are continued, then `Validated ... len(targets)` prints (155-159). | In `main` or a named-target helper, reject nonexistent/unreadable named paths with `unestablished` and exit 1. Test: missing `--path` is nonzero, names the path, and emits no validated verdict. |
| `scripts/check_plugin_asset_command_carriers.py` | ~~SANCTIONED~~ → **DEFECT** (corrected 2026-08-30, see below) | `scan_assets` returns `(len(assets), findings)` (95-103); parse errors become findings (99-102), and strict listing is forwarded (106-118). ~~Zero shipped assets is a legitimate discovered-empty family.~~ Measured: 0 in scope against 58 assets on disk. | Scope the generated mirror from disk, not the git listing; refuse `unestablished` when it is absent. |
| `scripts/check_plugin_doc_links.py` | ~~SANCTIONED~~ → **DEFECT** (corrected 2026-08-30, see below) | The scope loop is `iter_matching_repo_files` (143-144); skipped cases are counted (145-155), and strict listing is forwarded (177-185). Read failures are not collapsed. ~~No plugin Markdown docs is an absent family.~~ Measured: 0 in scope against 229 docs on disk, with byte-identical output either way. | Scope the generated mirror from disk, not the git listing; refuse `unestablished` when it is absent; report the EXAMINED count. |
| `scripts/check_prose_pin.py` | DEFECT | `_git` returns `None` for failed git (43-51); `changed_status` turns that into `[]` (67-73), and `build_report` calls empty findings clean (194-206). No `HEAD` or failed diff is therefore green like no change. | Make `_git`/`changed_status` raise or return `unestablished`; `main` reports it and exits nonzero. Test: failed `git diff ... HEAD` yields nonzero `status: unestablished`, not `clean`. |
| `scripts/check_public_doc_coupling.py` | DEFECT | `_line_findings` calls `iter_matching_repo_files` (62-72), but catches read `OSError`/`UnicodeDecodeError` and continues (72-75). An unreadable file therefore yields the clean payload (123-138). | In `_line_findings`, raise/report `unestablished` for read failures; CLI exits nonzero with file and cause. Test: unreadable matched file gives `status: unestablished` and nonzero. |
| `scripts/check_python_runtime_inheritance.py` | SANCTIONED | `_iter_scan_paths` gets Python files from `iter_matching_repo_files` (73-79). `check_file` turns syntax failure into a failure row (89-113); strict listing is forwarded (116-132). Empty Python population is a discovered-empty pass. | — |
| `scripts/check_skill_cut_safety.py` | DEFECT | `build_report` gets changed paths from `changed_skill_md` (213-220), which delegates to `check_prose_pin.changed_status` (82-85). That returns `[]` on diff failure (43-73 of `check_prose_pin.py`), and no skills becomes `clean` (241-260). | Make the diff owner propagate `unestablished`; `build_report`/`main` report it and exit 1. Test: failed diff discovery yields nonzero `status: unestablished`, not clean. |
| `scripts/check_skill_ownership_overlap.py` | SANCTIONED | `scan` checks `skills/public` (261-266) and returns `_unwalked_payload`; zero readable files take the explicit branch (314-315), recording `scanned_files: 0` and `stale_allowlist: []` (187-196). `iterdir`/`read_text` failures are not swallowed. This says no skill family was read. | — |
| `scripts/check_spec_evidence_durability.py` | SANCTIONED | `main` explicitly skips “no git work tree” (368-378); otherwise it establishes both populations with `iter_matching_repo_files` (379-382). `git check-ignore` failures raise (139-150), while an empty artifact family reaches the counted validated line (407-412). | — |
| `scripts/check_staged_reversion.py` | SANCTIONED | `_staged_paths` is the whole scope: successful git enumeration returns paths, including `[]` (84-106), but OSError or nonzero git raises `RuntimeError` (95-105). `main` emits `state: unestablished` and exits nonzero on that exception (284-309); only an established empty staged set reaches `state: clean` (311-332). | — |

### Correction, 2026-08-30

Two rows above were wrong and are struck through rather than rewritten, because the reasoning that produced them is the finding.

Both plugin detectors were ruled SANCTIONED on the premise that zero plugin docs or assets is "a legitimate discovered-empty family". That premise was already false when this record was written. `6e05e026e` had gitignored `/plugins/`, and `iter_matching_repo_files` scopes through `git ls-files --others --exclude-standard`, which honors `.gitignore` — so both detectors saw ZERO of a complete on-disk mirror (229 docs, 58 assets) and still printed `Validated`. `check_plugin_doc_links.py`'s output was byte-identical over the full mirror and over nothing at all.

The mirror is a REQUIRED generated surface with an unconditional producer, so its absence is never a discovered-empty family; it means nobody ran the producer.

What this row's method missed: every verdict here was reached by READING the detector against its scope helper, and the defect lived in the helper's interaction with `.gitignore` — invisible at that layer. One with/without run refutes both rows in seconds. Source reading cannot establish that a scope is non-empty; only running it against a known-populated subject can.

Re-armed in the same change: both now scope the mirror from disk, refuse with `status: unestablished` and exit 1 when it is absent, and report what they EXAMINED. The doc-links gate found two real consumer-facing defects on its first armed run — `presets/{python,typescript}-quality.md` linked into the pre-flattening export layout — which it had been blind to for the whole period it reported success. Evidence: [plugins-mirror record](2026-08-29-plugins-mirror-absent-in-ci.md).

### Decision closure

Undecided: none. Every row has source evidence sufficient to distinguish a sanctioned discovered-empty answer from a green result over failed or silently dropped scope.

That closure statement did not hold for the two corrected rows, and the correction above says why.

## Runtime Signals

- runtime source: no samples; evidence is the structured YAML inventory and the cited detector source.
- runtime hot spots: the inventory’s detector subprocess probe and the required source reads; no timing claim is made.
- coverage gate: no changed-line, mutation, or full-suite verdict is claimed.
- evaluator depth: deterministic source judgment only; no external evaluator or delegated review was requested.

## Healthy

Nine detectors preserve a legitimate discovered-empty pass, and the staged-reversion detector is a complete worked example of separating successful empty enumeration from unestablished git state. The four defects have concrete, test-observable repairs without changing this record’s scope.

## Weak

The inventory itself probes only the default discovered-empty arm; named-scope behavior and failure branches were established by source reading, not a new fixture sweep.

## Missing

No repair was implemented or tested. This record does not claim the four defects are closed, nor that the other 117 detectors are honest.

## Deferred

- Implementation of the four repairs is deferred to a separately scoped change with focused negative controls.

## Advisory

- `inventory_empty_scope_honesty.py --repo-root . --detail` is an unarmed inventory, not a gate; its 13-row bucket required this disposition rather than automatic arming.

## Delegated Review

- status: not_applicable — this focused source judgment did not request a delegated review.

## Commands Run

`python3 scripts/render_lesson_selection_preview.py --repo-root . --seed 2026-08-29-empty-scope-disposition`; `PYTHONDONTWRITEBYTECODE=1 python3 skills/public/quality/scripts/inventory_empty_scope_honesty.py --repo-root . --detail`; resolver for the requested record path; focused source reads; `git status --short --untracked-files=all`.

## Recommended Next Quality Moves

- passive because implementation is outside this disposition’s exact scope — preserve the four repairs as named follow-up work and do not arm the inventory from this record alone.

## History

- [2026-07-14 quality review](history/2026-07-14-open-issue-resolution-proof.md)
