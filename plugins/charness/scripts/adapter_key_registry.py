#!/usr/bin/env python3
"""Resolve a declared adapter key to the reader that owns it, or to a typed gap.

Slice 1 made ONE declared field answerable. This answers the question it could not:
a resolver can now refuse a `version` it does not speak, but nothing can tell a typo'd
key from a deliberate one, so an operator's misspelled declaration reads exactly like a
correct one -- silently defaulted, never mentioned.

WHY THIS IS NOT A KNOWN-KEY SET. The obvious move -- ask the shared loader whether it
knows the key -- was refuted before it was built, and the refutation is measured, not
theoretical. `.agents/setup-adapter.yaml` declares `defaults_version`, `policy_sources`,
`recommendation_sets`, and `surfaces`. The shared `simple_skill` loader knows none of
them; its STRING_FIELDS is six unrelated names. All four are CORRECT, and all four are
parsed by `skills/public/setup/scripts/setup_adapter.py`. A loader-scoped key set would
have called four correct declarations typos on the one surface whose job is to stop a
false signal.

So the unit is the READER, not the key list. `.agents` files have multiple readers, and
"the shared loader has not heard of this" is a fact about one reader, not about the key.

KNOWN DESIGN GAP -- READ THIS BEFORE TRUSTING A `reader` VERDICT. Resolution is
KEY-scoped, not (FILE, KEY)-scoped: it asks "does any module parse this key name",
not "does any module that reads THIS adapter file parse this key". So a key declared in
adapter A can resolve to a module that only ever loads adapter B. Live instance, found
by bounded review and confirmed by measurement: `.agents/cautilus-adapters/
chatbot-benchmark.yaml` has no parsing reader at all -- `scripts/cautilus_adapter_lib.py`
pins `ADAPTER_PATH = .agents/cautilus-adapter.yaml`, the SINGULAR file, and its only
mention of the `cautilus-adapters/*.yaml` glob is inside an unrelated
`DEFAULT_PROMPT_AFFECTING_PATTERNS` list. Yet nine of that file's keys resolve to it,
purely because the names collide with its own field list. `held_out_command_templates`
and `comparison_command_templates` sit in the same declaration with identical epistemic
status and get opposite verdicts for that reason alone.

Consequence: a `reader` verdict is currently a claim about the REPO, not about the
adapter -- "some module parses a key by this name" -- and the count of `reader` states
overstates how much is genuinely reconciled. `unknown` is still sound (no module parses
the name anywhere), and `text-asserted` is sound for the instance it names. The fix is
path association, which is tracked, not done. Until then this module must not be wired
to anything that refuses or warns an operator: it would flag on evidence it does not
have. This is exactly the class the goal targets, found inside the instrument built to
find it, which is why it is written here rather than in a commit message.

WHY THE READER LIST IS DISCOVERED, NOT DECLARED. A checked-in table mapping key ->
reader would be a second declaration nobody reconciles -- this repo's own recurring
defect, rebuilt inside the tool meant to detect it. Readers are found by scanning the
repo's own Python for the key literal, so the answer comes from the code. The registry
below holds only what scanning CANNOT answer: retired keys, and keys whose reader
resolves them dynamically. Every registry entry is itself verified against the tree
(`audit_registry`), so a stale entry is refused rather than believed.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, NamedTuple

# Keys every adapter shares, owned by the shared loader in scripts/adapter_lib.py.
SHARED_CORE_KEYS = ("version", "repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")

# Keys deliberately withdrawn. A retired key is NOT unknown: an operator who still
# declares one deserves "this was removed", not "this looks like a typo". Each entry
# carries the reason, because a bare list rots into a place to hide names.
RETIRED_KEYS: dict[str, str] = {}

# Keys whose reader resolves them dynamically (built name, table lookup) so a literal
# scan cannot see the read. Each names the module that owns it; `audit_registry` checks
# that module still exists, so this cannot quietly outlive its reader.
DYNAMIC_READER_KEYS: dict[str, str] = {}

# Where a reader may live. Scanning the whole repo would count a key's own test fixtures
# as readers, which would make every key look owned.
READER_ROOTS = ("scripts", "skills")

# The instrument is not a reader. Caught by this module's own first run: the docstring
# below quotes `comparison_command_templates` as an example, so the scan matched itself
# and reported the key as owned -- the module manufacturing the evidence it then reports.
# Excluding self is the fix; the general limitation is stated in `find_readers`.
EXCLUDED_READERS = ("scripts/adapter_key_registry.py",)

_EXTENSION_PREFIX = "x-"
_EXTENSION_CONTAINER = "host_extensions"


class KeyResolution(NamedTuple):
    """One declared key's verdict.

    `state` is one of: `shared-core`, `reader`, `text-asserted`, `extension`, `retired`,
    `unknown`. `readers` is the evidence for `reader`/`shared-core`/`text-asserted`, and
    is empty otherwise.
    """

    key: str
    state: str
    readers: tuple[str, ...]
    detail: str


def _is_reader_file(path: Path) -> bool:
    """A candidate reader module.

    The `plugins` clause is belt-and-braces, not the primary mechanism: `READER_ROOTS`
    already keeps the scan inside `scripts/` and `skills/`, so the generated mirror is
    out of reach today. It is kept because adding a root to `READER_ROOTS` is a one-line
    change that would otherwise silently start counting every mirrored module as a second
    reader -- making every single-reader key look shared. Pinned directly in the tests,
    since a mutation proved the property held without it.
    """
    return path.suffix == ".py" and "plugins" not in path.parts and "__pycache__" not in path.parts


def iter_reader_files(repo_root: Path) -> list[Path]:
    """Every module that could own an adapter key.

    `plugins/` is excluded on purpose: it is a generated mirror, so counting it would
    report two readers for every key and make a single-reader key look shared.
    """
    return sorted(
        path
        for root in READER_ROOTS
        for path in (repo_root / root).rglob("*.py")
        if _is_reader_file(path) and str(path.relative_to(repo_root)) not in EXCLUDED_READERS
    )


# Every string constant in a module, collected ONCE per file so each key is answered by a
# set lookup. Scanning per key meant ~230 keys x ~680 files of regex and cost ~40s --
# expensive enough that the check would eventually be moved out of the fast gates, which
# is how a check stops running.
#
# Collected with `ast`, not a quote regex. A regex alternates its quote pairs, so on a
# line like `("alpha", "beta")` it pairs the closing quote of one literal with the
# opening quote of the next and loses both. That UNDER-reports readers, which turns a
# correctly-read key into a reported gap -- an instrument inventing the defect it is
# built to find. Measured while writing this: the regex saw 12 readers for `surfaces`
# where the exact parse sees 13.
_LITERALS_CACHE: dict[Path, list[tuple[str, frozenset[str]]]] = {}


def _literals(path: Path) -> frozenset[str]:
    """Every string constant in ``path``, including docstrings and comments' neighbours.

    A file that will not parse (syntax error, or a template that is not valid Python)
    falls back to an empty set rather than raising: this instrument reports on adapters,
    and it must not turn one unparseable module into a failure to classify every key.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return frozenset()
    return frozenset(
        node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)
    )


def _reader_literals(repo_root: Path, files: list[Path] | None) -> list[tuple[str, frozenset[str]]]:
    """`(relative path, quoted literals)` for every candidate reader, read once per tree."""
    if files is not None:
        return [(str(path.relative_to(repo_root)), _literals(path)) for path in files]
    if repo_root not in _LITERALS_CACHE:
        _LITERALS_CACHE[repo_root] = [
            (str(path.relative_to(repo_root)), _literals(path)) for path in iter_reader_files(repo_root)
        ]
    return _LITERALS_CACHE[repo_root]


def find_readers(
    repo_root: Path, key: str, *, files: list[Path] | None = None
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return ``(parsing readers, text-asserting readers)`` for ``key``.

    The split is the point, and this repo has a live instance of why. A module that reads
    `data["comparison_command_templates"]` USES the value. A module that greps the raw
    adapter text for the snippet `"comparison_command_templates:"` only asserts the line
    is PRESENT -- it never parses it, never runs it, and would pass on a declaration whose
    value is empty, malformed, or nonsense. Counting the second as a reader is the exact
    false green this whole goal exists to remove: presence checked, meaning never
    reconciled.

    Quoted matching specifically: a bare word match would count the key appearing in
    prose or as a substring of a longer identifier, and every key would look owned.

    KNOWN LIMIT, stated rather than implied: any string constant equal to the key counts
    as a parse -- including one in a docstring, an error message, an OUTPUT payload the
    module builds, or an unrelated dict that happens to share the name. Measured: of the
    thirteen modules matching `surfaces`, only three concern the setup adapter's
    `surfaces`; the rest read `.agents/surfaces.json`, the hotl adapter, or merely emit a
    dict with that key. So the bias is toward reporting a key as OWNED, which means this
    UNDER-reports gaps rather than inventing them -- the safe direction for a warn tier,
    and part of why no tier is armed. Found the hard way twice: this module's own
    docstring quotes a key and the first run counted itself as that key's reader, and a
    bounded review found the unrelated-dict case the first write-up had missed.
    """
    prefix = f"{key}:"
    parsing: list[str] = []
    asserting: list[str] = []
    for relative, literals in _reader_literals(repo_root, files):
        if key in literals:
            parsing.append(relative)
        elif any(literal.startswith(prefix) for literal in literals):
            asserting.append(relative)
    return tuple(parsing), tuple(asserting)


def resolve_key(repo_root: Path, key: str, *, files: list[Path] | None = None) -> KeyResolution:
    """Classify ONE declared key. Order matters: the explicit answers come first, so a
    retired key never reports as unknown and an extension key is never scanned for."""
    if key in RETIRED_KEYS:
        return KeyResolution(key, "retired", (), RETIRED_KEYS[key])
    if key.startswith(_EXTENSION_PREFIX) or key == _EXTENSION_CONTAINER:
        return KeyResolution(key, "extension", (), "namespaced extension; readers are host-owned by contract")
    if key in DYNAMIC_READER_KEYS:
        owner = DYNAMIC_READER_KEYS[key]
        return KeyResolution(key, "reader", (owner,), "resolved dynamically by its reader; registered rather than scanned")
    parsing, asserting = find_readers(repo_root, key, files=files)
    if key in SHARED_CORE_KEYS:
        return KeyResolution(key, "shared-core", parsing, "shared adapter core, owned by scripts/adapter_lib.py")
    if parsing:
        return KeyResolution(key, "reader", parsing, f"parsed by {len(parsing)} module(s)")
    if asserting:
        return KeyResolution(
            key,
            "text-asserted",
            asserting,
            "only matched as a raw-text snippet, never parsed: its PRESENCE is checked and "
            "its VALUE is never read, so a malformed or nonsense value passes",
        )
    return KeyResolution(
        key,
        "unknown",
        (),
        "declared but no module in scripts/ or skills/ reads it; a typo and a key whose "
        "reader was deleted look identical from here",
    )


def resolve_declared_keys(repo_root: Path, declared: dict[str, Any]) -> list[KeyResolution]:
    """Classify every top-level key of one parsed adapter."""
    return [resolve_key(repo_root, key) for key in declared if isinstance(key, str)]


def audit_registry(repo_root: Path) -> list[str]:
    """Refuse a registry entry the tree no longer supports.

    This is the anti-rot check, and it is the reason the registry is allowed to exist at
    all. Without it, `DYNAMIC_READER_KEYS` would be exactly the thing this module was
    built to detect: a declaration asserting a reader that nobody verifies.
    """
    problems = [
        f"DYNAMIC_READER_KEYS[{key!r}] names {owner}, which does not exist"
        for key, owner in DYNAMIC_READER_KEYS.items()
        if not (repo_root / owner).is_file()
    ]
    problems += [
        f"DYNAMIC_READER_KEYS[{key!r}] names {owner}, which does not reference the key; "
        "scanning already covers it, or the reader moved"
        for key, owner in DYNAMIC_READER_KEYS.items()
        if (repo_root / owner).is_file() and not any(find_readers(repo_root, key, files=[repo_root / owner]))
    ]
    problems += [
        f"RETIRED_KEYS[{key!r}] is marked retired but {len(readers)} module(s) still read it: {', '.join(readers)}"
        for key, readers in ((key, find_readers(repo_root, key)[0]) for key in RETIRED_KEYS)
        if readers
    ]
    problems += [f"RETIRED_KEYS[{key!r}] carries no reason" for key, reason in RETIRED_KEYS.items() if not reason.strip()]
    return problems
