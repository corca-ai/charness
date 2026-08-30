## Parent

#744

## Depends on

The typed topology core and a proven runtime/distribution path from the preceding #744 children.

## Situation

Charness repository-boundary behavior is spread across shared helpers and specialized Python scripts. The representative family includes:

- `scripts/repo_file_listing.py`;
- `scripts/what_reads_this.py` and `scripts/what_reads_this_fallback.py`;
- `scripts/check_plugin_dir_references.py`;
- `scripts/check_export_safe_imports.py`;
- derivable path and topology logic in `scripts/surfaces_lib.py`;
- static target-selection work surrounding `scripts/check_standalone_imports.py`.

These files are also projected into the checked-in plugin export. Adding a Rust gate without deleting or narrowing these owners would create another policy implementation and preserve the script count that motivated the native core.

Issue #743 is a concrete consumer-facing instance: release host-proof triggers need a production source set without treating adjacent test files as production or copying a file-by-file catalog.

## Experience

Maintainers currently need to know which helper owns Git inventory, which matcher interprets a glob, which script recognizes a command carrier, which generated copy is editable, and whether a passing static import check says anything about runtime imports. A one-file repair often leaves sibling implementations untouched because each script appears to own a distinct command.

## Impact

The repository keeps paying for repeated traversal, path matching, fixtures, and generated copies. More importantly, two implementations can disagree while both pass their own tests. Tombstone checks that merely prohibit deleted filenames would preserve the symptom rather than establish one current owner.

## Migration unit

Move one complete repository-boundary family, including inventory, graph construction, selection, verdict projection, tests, quality-lane wiring, plugin export consequences, and documentation. Do not migrate isolated files merely to increase a Rust line count.

## Acceptance

- Inventory, reverse-dependency explanation, generated-mirror relationships, package production/test classification, and export-safe static boundaries consume the native graph rather than rebuilding file sets.
- `what reads this` output preserves literal/glob/command evidence and adds typed root/edge explanations where the old command could only classify a match.
- The standalone-import runtime probe receives a statically selected set but still launches Python for behavior that only Python can establish. Full runtime smoke may remain at a broad release boundary if its distinct claim is documented.
- #743 is resolved through native package/source topology so a consumer can declare “this production package requires host proof” without enumerating all production files. If a generic exclusion contract remains useful for a distinct non-package case, it must not become the owner of package membership.
- Every absorbed Python algorithm is deleted in the same migration slice. A surviving wrapper contains only argument compatibility, subprocess invocation, and output/exit projection.
- Checked-in plugin copies disappear through the canonical exporter when their source owner is deleted; generated files are not hand-edited into a divergent state.
- Tests move from implementation/file-name tombstones to behavioral fixtures over nodes, edges, roots, verdicts, and failure completeness.
- `.agents/surfaces.json` or its successor no longer repeats derivable package/source/generated membership. Every remaining raw path declaration names the semantic or exceptional policy it alone owns.
- Quality and commit-time selection invoke one canonical command for this family. No test-only script is the sole consumer of a production-looking wrapper.
- Whole-repository parity and a consuming-repository fixture prove changed files, new production files, adjacent test files, deletions, renames, generated mirrors, unresolved imports, and external analyzer absence.
- Remove obsolete Python dependencies and bootstrap requirements made unreachable by the migration.

## Non-claims

- Static reachability is not runtime Python-import proof.
- Deleting one validator family does not claim the remaining Python inventory is already well structured or typed.
- The migration does not preserve old internal module paths without a current external consumer.
- No “must not exist” test is added solely to guard retired filenames; recurrence is prevented by making the native contract the only reachable owner.

## Weak direction

Switch one coarse family after parity, then delete its Python implementation immediately. Avoid a long-running shadow mode; comparison belongs before the ownership switch, not as a permanent second gate.

---

<!-- charness-work-item-key: issue-748-native-owner-migration -->
# Work Item #748 — Close the proven native capability slice

## Purpose and premise

Close the generic capability slice already published on provider main. Charness now exposes typed native inventory, classification, component, reverse-reader, standalone-target, and plugin-reference commands; do not force the two deferred Python helpers across an unproven consumer artifact boundary.

## Acceptance and proof

At the exact provider SHA, capture native `repograph inventory --repo-root . --regular-files-only` JSON readback and bind the already-published parity/owner-removal evidence. Close as `completed` for that composable capability scope.

## Non-claims

No claim that `repo_file_listing.py` or `surfaces_lib.match_surfaces` was fully migrated; no plugin-artifact, consumer-export, Git/submodule/topology, repository-wide migration, release, or language-preference claim.
