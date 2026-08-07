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

WHAT IS ARMED, AND WHAT DELIBERATELY IS NOT. This paragraph used to say the opposite --
"this module must not be wired to anything that refuses or warns an operator" -- because
resolution was KEY-scoped rather than (FILE, KEY)-scoped, so a key declared in adapter A
could resolve to a module that only ever loads adapter B. That gap is closed:
`resolve_declared_keys` takes `adapter_relative`, `associated_modules` scopes the parse
list to modules that actually read the file, and `survey` passes it. The prohibition
outlived its reason and was itself a false claim on the instrument built to find them.

`unknown` IS armed: `unreconciled_keys` below feeds `scripts/validate_adapters.py`, which
warns an operator by name. It is the sound state -- no module in `scripts/` or `skills/`
parses the name ANYWHERE -- and `find_readers`' bias (see its KNOWN LIMIT) is toward
calling a key owned, so `unknown` under-reports gaps and cannot invent one.

`reader-elsewhere` is NOT armed, and the number is why. Of its 23 instances measured
across this repo's 37 adapters, 20 are genuine (`.agents/cautilus-adapters/chatbot-*.yaml`,
which `scripts/cautilus_adapter_lib.py` never reads -- it pins `ADAPTER_PATH` to the
SINGULAR `.agents/cautilus-adapter.yaml`), but 3 are association residue that a warning
would report as defects: `chunk_policy` in `skills/public/handoff/adapter.example.yaml` is
genuinely read by `chunked_routing_agentic_policy.py`, and `session_routing` /
`skill_anchor_edit_guard` in `.agents/usage-episodes-adapter.yaml` are genuinely read
through `host_hook_registry.py`'s `getattr` dispatch. All three are invisible to a literal
scan. A 13% false-positive rate is a wolf-crier, and one of the three ships to consumers
inside a shipped example -- so arming it would greet every new consumer with a wrong
warning. Widening `associated_modules` to absorb them is refused separately: that is how
`#553` happened, and how a verdict stops meaning anything. They stay reported by `survey`
and unwarned.

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
SHARED_CORE_OWNER = "scripts/adapter_lib.py"
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

    `state` is one of: `shared-core`, `reader`, `reader-elsewhere`, `text-asserted`,
    `extension`, `retired`, `unknown`. `readers` is the evidence for `reader`/`shared-core`/`text-asserted`, and
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


def _module_name(relative: str) -> str:
    """`scripts/setup_inspect_lib.py` -> `scripts.setup_inspect_lib`, the form this repo's
    dynamic loaders name modules by."""
    return relative.removesuffix(".py").replace("/", ".")


def _import_names(path: Path) -> frozenset[str]:
    """Dotted names this module imports, so association follows real edges."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return frozenset()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return frozenset(names)


def _convention_owners(repo_root: Path, adapter_relative: str) -> set[str]:
    """Owners that name no path because they BUILD it.

    Most skill resolvers never contain their adapter's path: the shared helper composes
    it from the skill id (`.agents/{skill_id}-adapter.yaml`), so `find_adapter(repo_root,
    "release")` owns `.agents/release-adapter.yaml` without the literal appearing
    anywhere. Seeding on exact literals alone therefore reported nine correct
    `release-adapter.yaml` declarations as unread -- the inverted bias this module is
    written to avoid, caught by measuring before shipping rather than by review.

    So the repo's own naming contract seeds ownership too, and like every other entry
    here it is VERIFIED rather than asserted: a candidate counts only if the file exists.
    """
    parts = Path(adapter_relative).parts
    name = Path(adapter_relative).name
    if name.endswith("-adapter.yaml"):
        # `.agents/<skill>-adapter.yaml`
        skill = name.removesuffix("-adapter.yaml")
    elif name == "adapter.example.yaml" and len(parts) >= 2:
        # A shipped example lives beside the resolver that reads its real counterpart:
        # `skills/public/<skill>/adapter.example.yaml`, `integrations/<id>/...`. Without
        # this every example key read as unreconciled, which is the population the
        # operator's warn-vs-refuse decision depends on -- so the miss would have been
        # invisible in this repo's own adapters and decisive in the number that matters.
        skill = parts[-2]
    else:
        return set()
    candidates = (
        f"skills/public/{skill}/scripts/resolve_adapter.py",
        f"scripts/{skill.replace('-', '_')}_adapter_lib.py",
        f"skills/public/{skill}/scripts/{skill.replace('-', '_')}_adapter_policy.py",
    )
    # Existence is not association. A candidate counts only if it also names the skill --
    # `find_adapter(repo_root, "release")` / `skill_id="release"` -- so the convention is
    # RECONCILED against the code rather than asserted, the same discipline
    # `audit_registry` already applies to the registry's own entries. Without this a stub
    # or repurposed resolver at the conventional path would fabricate an owner.
    edges = _reference_edges(repo_root)
    return {
        candidate
        for candidate in candidates
        if (repo_root / candidate).is_file() and skill in edges.get(candidate, (frozenset(), frozenset()))[0]
    }


def _exemplified_owners(repo_root: Path, adapter_relative: str) -> set[str]:
    """A shipped example inherits the association of the adapter it exemplifies.

    `skills/public/setup/adapter.example.yaml` is a template for
    `.agents/setup-adapter.yaml`; by construction the modules that read one read the
    other. Without this the SAME key resolved differently in the two files -- `surfaces`
    was `reader` in the real adapter and `reader-elsewhere` in its own example -- which
    is a verdict that contradicts itself on identical evidence, and would have inflated
    the example-adapter gap count the operator's decision depends on.
    """
    parts = Path(adapter_relative).parts
    if Path(adapter_relative).name != "adapter.example.yaml" or len(parts) < 2:
        return set()
    real = f".agents/{parts[-2]}-adapter.yaml"
    return set(associated_modules(repo_root, real)) if (repo_root / real).is_file() else set()


_EDGES_CACHE: dict[Path, dict[str, tuple[frozenset[str], frozenset[str]]]] = {}
_ASSOCIATED_CACHE: dict[tuple[Path, str], frozenset[str]] = {}


def _reference_edges(repo_root: Path) -> dict[str, tuple[frozenset[str], frozenset[str]]]:
    """`relative -> (string literals, imported dotted names)`, built once per tree.

    Rebuilding this per adapter re-parsed every module ~18 times and made the check cost
    ~24s. Same reasoning as the literal cache: a check that gets expensive gets moved out
    of the fast gates, and then it stops running.
    """
    if repo_root not in _EDGES_CACHE:
        _EDGES_CACHE[repo_root] = {
            relative: (literals, _import_names(repo_root / relative))
            for relative, literals in _reader_literals(repo_root, None)
        }
    return _EDGES_CACHE[repo_root]


def associated_modules(repo_root: Path, adapter_relative: str) -> frozenset[str]:
    """Modules that read the adapter at ``adapter_relative``, directly or transitively.

    Seeded by OWNERS -- modules naming the adapter's exact path, plus the resolver the
    repo's naming convention points at -- then closed over module references until it
    stops growing. The closure is what keeps injected and dynamically
    loaded readers in scope; see this module's docstring for why dropping it would invert
    the bias into false typo reports.
    """
    cache_key = (repo_root, adapter_relative)
    if cache_key in _ASSOCIATED_CACHE:
        return _ASSOCIATED_CACHE[cache_key]
    edges = _reference_edges(repo_root)
    owners = {relative for relative, (literals, _) in edges.items() if adapter_relative in literals}
    owners |= _convention_owners(repo_root, adapter_relative)
    owners |= _exemplified_owners(repo_root, adapter_relative)
    if not owners:
        _ASSOCIATED_CACHE[cache_key] = frozenset()
        return _ASSOCIATED_CACHE[cache_key]
    associated = set(owners)
    frontier = set(owners)
    while frontier:
        # Dotted module names and repo-relative paths only. The bare BASENAME was the
        # whole collision surface and re-created `#553` one level up: this repo has 16
        # files named `resolve_adapter.py`, one per skill, and `_convention_owners` seeds
        # exactly that name -- so a tail match associated every module mentioning
        # "resolve_adapter" with EVERY skill adapter. Association by module-name collision
        # is the same defect as the verdict by key-name collision this module exists to
        # remove, which is why the branch is gone rather than narrowed.
        wanted = {_module_name(member) for member in frontier} | set(frontier)
        found = {
            relative
            for relative, (literals, imports) in edges.items()
            if relative not in associated
            and (literals & wanted or any(name in wanted for name in imports)
                 or any(name.rsplit(".", 1)[0] in wanted for name in imports))
        }
        associated |= found
        frontier = found
    _ASSOCIATED_CACHE[cache_key] = frozenset(associated)
    return _ASSOCIATED_CACHE[cache_key]


def resolve_key(
    repo_root: Path, key: str, *, files: list[Path] | None = None, associated: frozenset[str] | None = None
) -> KeyResolution:
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
    scoped = tuple(module for module in parsing if module in associated) if associated is not None else parsing
    if key in SHARED_CORE_KEYS:
        # Named owner, not a scan result. Returning the unscoped parse list here claimed
        # arbitrary modules as readers, and scoping it returned an EMPTY reader list for a
        # state whose whole meaning is "this one is owned" -- a verdict with no named
        # reader, which is the thing this module refuses to emit. The shared core is owned
        # by the shared loader by construction, so it is named directly.
        return KeyResolution(
            key, "shared-core", (SHARED_CORE_OWNER,), f"shared adapter core, owned by {SHARED_CORE_OWNER}"
        )
    if scoped:
        return KeyResolution(key, "reader", scoped, f"parsed by {len(scoped)} module(s) that read this adapter")
    if parsing:
        return KeyResolution(
            key,
            "reader-elsewhere",
            parsing,
            "a module parses a key of this name, but nothing that reads THIS adapter file "
            "does; the declaration is unreconciled here even though the name is live",
        )
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


def resolve_declared_keys(
    repo_root: Path, declared: dict[str, Any], *, adapter_relative: str | None = None
) -> list[KeyResolution]:
    """Classify every top-level key of one parsed adapter.

    ``adapter_relative`` is what makes the answer about THIS adapter. Omitting it falls
    back to repo-wide resolution, which is weaker and is why `#553` existed; callers that
    know the file should always pass it.
    """
    associated = associated_modules(repo_root, adapter_relative) if adapter_relative else None
    return [resolve_key(repo_root, key, associated=associated) for key in declared if isinstance(key, str)]


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


ADAPTER_GLOBS = (
    ".agents/*-adapter.yaml",
    ".agents/cautilus-adapters/*.yaml",
    "skills/public/*/adapter.example.yaml",
    "integrations/*/adapter.example.yaml",
)
GAP_STATES = ("unknown", "reader-elsewhere", "text-asserted")


def _load_yaml_file(path: Path) -> Any:
    """Import the shared loader lazily and layout-independently.

    A module-level `from scripts.adapter_lib import ...` works when this file is imported
    as part of the package but not when it is executed directly, which is exactly how the
    survey CLI runs. The repo's own direct-execution bootstrap handles both layouts.
    """
    from runtime_bootstrap import import_repo_module

    return import_repo_module(__file__, "scripts.adapter_lib").load_yaml_file(path)


def survey(repo_root: Path) -> dict[str, Any]:
    """Every declared key in every adapter this repo owns or ships, typed.

    Reports rather than refuses. The warn-vs-refuse tier is an operator decision, and
    arming one from a repo-local zero is precisely what `docs/deferred-decisions.md` D46
    argues against: the population that matters is consumer adapters this repo has never
    seen. This produces the number that decision needs; it does not make the decision.
    """
    counts: dict[str, int] = {}
    gaps: list[dict[str, Any]] = []
    files = sorted({path for glob in ADAPTER_GLOBS for path in repo_root.glob(glob)})
    for path in files:
        relative = str(path.relative_to(repo_root))
        # No `isinstance(declared, dict)` guard: this repo's loader always returns a
        # mapping, so the guard was unreachable and read as though a real hazard were
        # handled.
        declared = _load_yaml_file(path)
        for resolution in resolve_declared_keys(repo_root, declared, adapter_relative=relative):
            counts[resolution.state] = counts.get(resolution.state, 0) + 1
            if resolution.state in GAP_STATES:
                gaps.append(
                    {
                        "adapter": relative,
                        "key": resolution.key,
                        "state": resolution.state,
                        "detail": resolution.detail,
                    }
                )
    return {
        "adapters": len(files),
        "keys": sum(counts.values()),
        "counts": counts,
        "gaps": gaps,
        "registry_problems": audit_registry(repo_root),
    }


WARN_STATES = ("unknown",)


def unreconciled_keys(repo_root: Path, paths: list[Path]) -> list[dict[str, str]]:
    """Declared keys that reach an ARMED state, for the operator-visible warn tier.

    Only `WARN_STATES` -- `unknown` -- is returned. The module docstring owns why
    `reader-elsewhere` is excluded (measured 13% association residue, one instance inside
    a shipped example); this function is where that decision is executable rather than
    prose, so widening the tier means editing `WARN_STATES` and re-measuring, not quietly
    adding a state at a call site.

    NO `associated` ARGUMENT, AND THAT IS NOT A WEAKENING. `resolve_key` reaches `unknown`
    only when `parsing` is empty, and `scoped` is a subset of `parsing` -- so the scoped
    and unscoped verdicts are identical for exactly this state, and only for it. Skipping
    it also skips `associated_modules`/`_reference_edges`, the whole import-graph closure,
    which is the expensive half: 4.6s to 3.1s over this repo's 445 declared keys. That
    matters because `validate_adapters.py` runs at commit time, and a gate that gets slow
    is a gate that gets moved somewhere it stops running. The equivalence is pinned by
    test, not left to this comment: a future state added to `WARN_STATES` would NOT
    inherit it.
    """
    findings: list[dict[str, str]] = []
    for path in paths:
        # No `relative_to` fallback and no `isinstance(key, str)` guard. Both were written,
        # both SURVIVED the mutation check, and reading why killed them instead: the only
        # caller passes paths `iter_matching_repo_files` globbed from `repo_root`, so the
        # ValueError branch is unreachable, and this repo's minimal loader coerces every
        # key to `str` (`1:` parses to `"1"`), so the type guard is unreachable too. A
        # branch that cannot run still reads as though a real hazard were handled -- the
        # same false claim this tier exists to warn about, one layer down.
        relative = str(path.relative_to(repo_root))
        declared = _load_yaml_file(path)
        for key in declared:
            resolution = resolve_key(repo_root, key)
            if resolution.state in WARN_STATES:
                findings.append(
                    {"adapter": relative, "key": key, "state": resolution.state, "detail": resolution.detail}
                )
    return findings


def main() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    print(json.dumps(survey(args.repo_root.resolve()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
