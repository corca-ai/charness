## Structural pattern

A published number whose only test asserts the value `0` is pinned on one arm. The
projection that computes it can be broken in a way that returns zero for every input
— a mistyped key, a wrong default — and the whole suite stays green. The report-level
list it is derived from is often well covered, which is exactly what makes the
*projection* look covered when it is not.

This is the defect class the `6.4.0` release repaired twice in other fields
(`count_scanner_exclusions` pinned only at 0; `uncovered_module_count` asserted by an
identity that could not fail). This is the sibling that was found and left.

## Triggering instance(s)

`skills/public/quality/scripts/check_dup_ratchet.py:378,389-390`:

```python
    new_docs = report.get("new_doc_families", [])
    ...
        "new_doc_family_count": len(new_docs) if isinstance(new_docs, list) else 0,
        "new_doc_families_sample": new_docs[:sample_limit] if isinstance(new_docs, list) else [],
```

`summarize()` is the only place the doc list is projected into a count for
`--summary` consumers.

A repo-wide grep finds `new_doc_family_count` asserted in exactly one place:

```
tests/quality_gates/test_dup_ratchet_scope_coverage.py:580:    assert payload["new_doc_family_count"] == 0
```

`new_doc_families_sample` is asserted nowhere.

**Failure scenario.** Mistype the key at line 378 — `report.get("new_doc_familes", [])`
— and every consumer's `--summary` reports **zero new doc families on a run that
hard-blocks on doc drift**, suite green. A new doc family sets `hard_block` exactly
as a code family does, so the summary and the exit code would disagree, and the
summary is what an operator reads first.

The report-level `new_doc_families` list IS well pinned
(`tests/quality_gates/test_dup_ratchet.py:139,405`), which is the reason the
projection reads as covered.

## Note

The code is currently correct. This is a missing proof, not a live wrong number —
hence filed rather than fixed in the release. The fix is a test that drives a
non-zero doc-family block through `summarize()` and asserts the count and the sample
by value, mirroring the `new_code_family_count == 2` assertion two lines above the
existing zero pin.

---

<!-- charness-work-item-key: issue-709-summary-projection -->
# Work Item #709 — Prove the non-zero summary projection

## Purpose and premise

Make `new_doc_family_count` and its sample describe the same observed non-zero family set. Re-read the current projection before editing; a passing current implementation produces a no-code closeout.

## Acceptance and proof

Focused tests cover zero, non-zero, and deliberately stale/wrong projection controls. The issue keeps its own behavior verdict and closeout comment identity.

## Non-claims

No new aggregate summary gate, provider claim, or consumer-specific policy.
