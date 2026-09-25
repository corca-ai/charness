"""Command payloads for the repo-root `charness` entry.

The root entry keeps the parser, the entry-to-tree bridge, and thin
shims; every command body lives here, one module per command group.
Shims lazy-load these modules at command time, after the target tree
is on `sys.path`, so the sibling imports below resolve against it.
"""
