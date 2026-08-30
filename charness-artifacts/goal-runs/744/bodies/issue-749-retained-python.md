## Parent

#744

## Depends on

At least one complete native-core migration slice, so the decision uses observed ownership and distribution results rather than a language preference.

## Situation

Charness retains a roughly 5,992-line top-level Python `charness` router, hundreds of Python scripts, dynamic source/plugin import paths, and no repository-wide static type checker. Some Python remains appropriate for skill orchestration and actual Python runtime probes, but the current structure does not state that boundary explicitly.

Applying a type checker before native-core consolidation would likely produce a large ignore baseline around dynamic loaders and generated layouts. Moving the entire CLI first would likewise optimize startup that currently measures around 0.22 seconds while leaving the slower analysis fan-out intact.

## Experience

Maintainers cannot tell which Python modules are durable product/orchestration code, which are compatibility projections, which are quality-only commands, and which survive only because a test calls them. Names and placement do not consistently reveal role, and checked-in plugin generation duplicates many scripts regardless of whether installed skills need them.

## Impact

Unclassified Python responsibilities make further migration arbitrary. A broad type-check ignore list would bless the hardest modules as permanently unchecked, while an unconditional CLI rewrite could increase Rust surface without deleting meaningful Python complexity.

## Desired outcome

After the native core has absorbed one complete family, define and enforce a small retained-Python boundary, reduce the top-level router and exported script surface, and add static typing where it can own real cross-module contracts.

## Acceptance

- Inventory every retained canonical Python entrypoint by current consumer and role: bootstrap, skill orchestration, runtime behavior probe, compatibility wrapper, development/quality command, or generated projection.
- Rootless and validation/test-only Python components discovered by the native graph are deleted, merged into a current owner, or explicitly justified by a named consumer and distinct claim.
- Production-looking wrappers whose only consumer is a test or sibling wrapper do not survive merely to preserve a historical command shape.
- The top-level CLI router is decomposed around the native core. Migrate subcommands to Rust only when doing so deletes Python ownership or closes a measured runtime/type boundary; retain Python subcommands when they are thin, stable orchestration.
- Existing human-facing CLI output, structured YAML, exit codes, install/update behavior, and command grammar remain compatible unless an explicit contract change is approved.
- Apply one selected static type checker to the retained importable Python boundary with no broad repository ignore or baseline that makes existing files invisible. Dynamic/plugin seams use narrow typed adapters rather than global suppression.
- Remaining path-based module loading is justified by source/install layout evidence and centralized behind the smallest possible loader API.
- Plugin export includes only scripts required by installed consumers or the declared runtime contract; “copy the entire scripts tree” is no longer an unquestioned default if the native-core migration makes a smaller set derivable.
- Record before/after canonical Python files and lines, dynamic-loader sites, exported Python files, type-check scope, CLI timings, and broad quality timings. Metrics are evidence, not permanent line-count ratchets.
- Documentation names the final ownership boundary and explicit non-claims for behavior that remains Python-owned.

## Non-claims

- This issue does not require eliminating Python or rewriting public skill prose/assets.
- Fewer lines alone do not prove a better boundary.
- A type checker does not replace runtime probes or tests.
- Generated plugin duplication is changed only where install consumers and the exporter contract permit it.

## Weak direction

Treat Python as a thin orchestration and compatibility layer over the typed core, then decide the top-level CLI command-by-command. The desired result is less ownership and stronger contracts, not a language-purity milestone.

---

<!-- charness-work-item-key: issue-749-retained-python -->
# Work Item #749 — Decline an ungrounded retained-Python campaign

## Purpose and premise

Record that the proposed retained-Python/type-check campaign has no current consumer-rework JTBD or approved capability delta. Provider main has no retained-boundary inventory, selected checker, or selective-export proof, and those absences are not implementation success.

## Acceptance and proof

Capture one provider-source boundary audit: no mypy/pyright configuration or executable checker, and packaging still exports the complete scripts tree. Close as `not planned`, without manufacturing an ignore baseline, ownership deletion, or language migration merely to satisfy the tracker.

## Non-claims

No top-level CLI decomposition, repository type-safety, selective-export, Python-ownership deletion, line-reduction, release, or installed-consumer claim.
