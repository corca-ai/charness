"""One owner for "is this gate's env bypass switched on?".

Every gate with an escape hatch has to answer the same question about the same
kind of value, and the answer is not `bool(os.environ.get(NAME))`. Bare
truthiness reads every non-empty spelling as "on", so `NAME=0`, `NAME=false`,
`NAME=no` and `NAME=off` -- the spellings an operator reaches for to say "keep
the gate running" -- switch the gate OFF instead. The escape hatch fires in the
exact moment someone tried to nail it shut.

That inversion has shipped in this repo twice, in two separate copies of this
three-line predicate, and was repaired twice (`check_staged_worktree_consistency`
first, then `helper_provenance_lib`). It was live in a third copy
(`check_staged_reversion`) with no test able to see it, because the contract was
restated per gate instead of imported: a repair to one copy cannot reach the
others, and no test of one copy constrains another.

So the spelling table lives here once and is pinned once. A gate that also has a
CLI flag keeps that disjunction local -- the flag is per-gate, the truthiness
rule is not.
"""
from __future__ import annotations

import os

#: The only spellings that switch a bypass ON, compared after `strip().lower()`.
#: Everything else -- including "0", "false", "no", "off", "" and unset -- leaves
#: the gate running. Keep this an allowlist: an "is it falsy" denylist has to
#: enumerate every way to say no, and whatever it misses disarms a gate.
TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def env_bypass_enabled(name: str) -> bool:
    """True only for an explicit truthy spelling of the ``name`` env var."""
    return os.environ.get(name, "").strip().lower() in TRUE_VALUES
