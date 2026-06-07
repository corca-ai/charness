# Resolution Critique — #325 Provenance-Placement Policy + Portable Check

Binds the bounded fresh-eye critique to the resolution of GitHub issue #325
("Standing/contract docs bake issue numbers + dates into rule prose; define
provenance-placement policy + portable check"). Carrier: the direct commit
staging `Close #325`. Classification: documentation/enhancement (a missing
portable contract + hygiene check, not a behavior defect — `debug: n/a —
policy/portability design`). This bundle also carries the related root-cause
fix (broadening the `implementation-discipline.md` portability-classification
closeout checkpoint to cover improvements/issues/policies).

## Reviewer Provenance

Bounded fresh-eye `critique` subagent (general-purpose, read-only), run this
session in the shared parent worktree against the staged slice (`git diff HEAD`,
empirical `--repo-root` probes on throwaway fixtures). Base (pre-slice) commit:
`git rev-parse HEAD` at staging. The reviewer probed the masking escape-hatch,
two-digit / range / org-repo issue-ref under-fire, portability coupling, the
swept-doc contract semantics, and the policy threshold against the real charness
standing-doc corpus.

## Verdict

**Ship.** No blockers. One real nit (a doc-vs-code exit-code contradiction) was
found and fixed before commit; all five claimed invariants held under probing.

## Blockers

None.

## Nit (found and FIXED before commit)

- **Wrong exit-code claim in the portable docs.** The CLI docstring
  (`check_standing_doc_provenance.py`) and the reference
  (`standing-doc-provenance.md`) said "exit 0 when ... the adapter is invalid",
  but `main()` returns **1** on adapter errors (fail-closed), as the test
  `test_invalid_adapter_block_fails_with_error` and the
  `attention-state-visibility.json` rationale both confirm. Fixed both to "exit 0
  when clean or inert; exit 1 on a flagged line or an invalid adapter (fails
  closed)." Code/test unchanged — they were already correct.

## Over-Worry (raised, probed, ruled non-blocking)

- **Masking as an escape hatch.** A diary date in backticks or a fake link
  target silently escapes. By design: the policy explicitly sanctions inline-code
  examples and record-layer link targets, and there is a visible
  `inline_allow_marker` opt-out. The check targets accidental drift, not an
  adversary; the backtick path is no worse than the documented marker.
- **Two-digit `#42` under-fire.** Bare `#NN` < 3 digits does not flag
  (intentional, avoids list/step-label false positives — the reused
  `ISSUE_ANCHOR_RE` precedent). The only such hit in charness standing docs
  (`Repeat Trap #1`) is correctly not flagged; two-digit `org/repo#42` still
  flags via the org/repo branch; range refs (`#302–#305`) count as 2.
- **Portability coupling.** The entrypoint loads `scripts.quality_adapter_lib`
  via the same `repo_root_from_skill_script` contract the 8 pre-existing quality
  scripts use; the inert-on-empty default + `adapter.example.yaml` shipping
  `standing_docs: []` make it genuinely opt-in and inheritable.
- **Sweep changing contract meaning.** Diffed all four swept docs: grandfather
  cutoff dates are value-identical (only backticked); the dropped `2026-04-10`
  was an illustrative example, not a threshold; the S6 broadening widens the
  checkpoint (one scope → two) without reversing any rule. Both referenced retro
  links resolve.
- **`provenance-allow` self-collision.** The policy doc names the marker literal
  while being scanned, so that line self-skips (also code-masked). Harmless;
  noted for consuming repos that document the marker inside a scanned doc.
- **Policy threshold `≥2 refs OR any date`.** Matches the issue's "dates /
  multiple issue refs"; a single load-bearing `(#NNN)` is preserved; the
  configured check returns 0 findings on charness's 5 standing docs after the
  sweep, so no false-positive class survives the masking on the real corpus.
