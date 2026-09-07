# Literal-reference consumer trace excerpts

Consumer target f914edbcdc1dca0defc093bd431cfb2b842e6b94. Line numbers refer to the original log whose hash is in the adjacent JSON. External package and worktree roots below use logical labels. Long command output was already truncated by the carrier; no missing content is reconstructed.

## Original lines 52-55

```text

/usr/bin/zsh -lc "printf '%s\\n' '--- spec skill ---' && sed -n '1,320p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/SKILL.md" && printf '"'%s\\n' '--- impl references ---' && for p in \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/adapter-contract.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/contract-consumption.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/design-lenses.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/sequence-discipline.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/external-api-contract.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/shared/references/prescribed-path-self-test.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/shared/references/source-bound-records.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/prove/SKILL.md"; do printf '"'\\n--- %s ---\\n' \""'$p"; sed -n '"'1,280p' \""'$p"; done' in <consumer-worktree>
 succeeded in 0ms:
--- spec skill ---
---
```

## Original lines 492-505

```text

--- <export-root>/shared/references/prescribed-path-self-test.md ---
# Prescribed Path Self-Test

Use this when a skill package claims that a self-test, smoke test, schedule,
event trigger, or external lookup proves the skill is ready for another agent
to run later.

## Rule

A passing self-test is evidence only when it exercises the path the next agent
will actually have:

- start from the checked or installed `SKILL.md`, not the author's private
  memory of what worked
```

## Original lines 551-565

```text

--- <export-root>/shared/references/source-bound-records.md ---
# Source-Bound Records

Use this pattern when all of these are true:

- the workflow handles multiple source items
- source identity or principal binding matters
- the workflow performs external, irreversible, expensive, or hard-to-dedupe
  side effects

Do not apply it to read-only summaries or ordinary multi-document synthesis.

## Pattern

1. Deterministic code collects `SourceRecord`s with immutable `itemId`, source
```

## Original lines 986-989

```text

/usr/bin/zsh -lc "printf '%s\\n' '--- hidden repo surfaces ---' && find . -maxdepth 3 -type f -print | sort && printf '%s\\n' '--- spec-skill references ---' && for p in \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/shared/references/bootstrap-resolution.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/ideation/references/spec-boundary.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/shared/references/binary-preflight.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/shared/scripts/plan_risk_interrupt.py" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/references/public-executable-contracts.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/references/design-lenses.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/shared/references/generative-sequence.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/shared/references/source-bound-records.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/references/evidence-durability.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/references/taxonomy-axis-checkpoint.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/references/fixed-probe-defer.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/references/success-criteria.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/references/acceptance-checks.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/references/executable-spec-cost.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/shared/references/agent-assessment-invariant.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/shared/references/success-criteria-review.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/shared/references/fresh-eye-subagent-review.md"; do printf '"'\\n--- %s ---\\n' \""'$p"; if test -f "$p"; then sed -n '"'1,260p' \""'$p"; else echo '"'(missing)'; fi; done && printf '%s\\n' '--- adapter ---' && if test -f .agents/impl-adapter.yaml; then sed -n '1,240p' .agents/impl-adapter.yaml; else echo '(absent)'; fi" in <consumer-worktree>
 succeeded in 23ms:
# Fixed, Probe, Defer

```

## Original lines 1855-1875

```text

+            {"books": ["novel"]},
+            aliases=[("reading", "books")],
+        )
+
+        with self.assertRaises(KeyError):
+            catalog.resolve("missing")
+

 if __name__ == "__main__":
     unittest.main()

codex
The implementation now validates aliases in input order with the specified precedence and stores only canonical targets; lookup checks canonical keys first and otherwise follows the validated alias map. I also added the full unit coverage from the contract, including empty aliases, two successful aliases, canonical preservation, all rejection families, first-error ordering, and the `KeyError` lookup boundary.
exec
/usr/bin/zsh -lc "git diff -- src/catalog.py tests/test_catalog.py && printf '%s\\n' '--- tests ---' && python3 -m unittest discover -s tests -v && printf '%s\\n' '--- status ---' && git status --short" in <consumer-worktree>
 succeeded in 67ms:
test_canonical_lookup_remains_available_with_aliases (test_catalog.CatalogTests) ... ok
test_empty_alias_list_preserves_canonical_behavior (test_catalog.CatalogTests) ... ok
test_rejects_alias_colliding_with_canonical_key (test_catalog.CatalogTests) ... ok
test_rejects_alias_with_unknown_target (test_catalog.CatalogTests) ... ok
test_rejects_duplicate_alias_with_different_target (test_catalog.CatalogTests) ... ok
```
