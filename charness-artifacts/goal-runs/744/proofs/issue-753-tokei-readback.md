# Issue #753 Official Test/Production Readback

Date: 2026-08-30

The current official command was:

```text
python3 scripts/check_test_production_ratio.py --repo-root . --engine tokei
```

It reported `engine: tokei`, `source_lines: 148198`, `test_lines: 148239`, `ratio: 1.0003`, `source_file_count: 773`, `test_file_count: 590`, `max_ratio: 1.0`, and `status: over-max`. The ratio remains advisory evidence, not a deletion target.

The existing JTBD audit at `charness-artifacts/design-studies/issue-753/2026-08-28-jtbd-audit-quality-gates.md` found 358 of 371 reviewed quality-gate files to be clean keeps. It records two removals and the bounded trim candidates separately.

This proof does not use `wc`, does not claim mutation non-regression, and does not license deleting comments or tests to move a count.
