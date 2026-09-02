"""Can the exported plugin RUN on a machine that has only the exported plugin?

The class (#634), stated once: an exported artifact depends on a repo-root file
the export does not ship, so it is broken or silently mis-calibrated for every
consumer while working perfectly here. Three recorded instances before this
module existed -- a docs-graph bar measured on charness's own tree with the
ratchet record unexported, the quality skill's budget apparatus shipped without
the runner it budgets, and `bootstrap_runtime.py` shipped without the dependency
contract it reads. The third was found by a stranded session on another machine.

WHY THE EXISTING GATES CANNOT SEE IT, which is the reason this is a new question
and not a stricter setting on an old one. `validate_packaging_install_surface.py`
re-runs the exporter into a tmpdir and diffs it against the materialized tree, so
its ORACLE IS THE EXPORTER: anything the exporter omits is absent from both sides
and the diff is empty. It is a fixed-point check on the generator, not a
self-sufficiency check on the artifact. The native-backed `check-export-safe-imports`
gate asks the adjacent question -- does a path literal survive the `skills/public/` collapse --
and reasons about the SOURCE tree. This module reads the CHECKED-IN EXPORT, which
is the thing a consumer actually installs.

Two arms, because the recorded instances have two shapes:

1. **Paths.** An exported module builds a repo-root-relative path whose first
   segment the export does not ship. Not every such segment is a defect: a
   consumer OWNS `.agents/`, `charness-artifacts/`, `docs/`, and the rest of
   `CONSUMER_OWNED_ROOTS` -- those are seeded or scanned at runtime, and shipping
   filled copies would overwrite consumer config. So the verdict needs a declared
   classification, and the declaration carries its reason.

2. **Dependencies, asked as AVAILABILITY rather than as declaration.** A
   documented consumer entrypoint -- a script an exported `SKILL.md`, reference,
   or adapter tells a consumer to run -- must not crash on a bare
   `ModuleNotFoundError`. It either guards the import and names what to install,
   or it does not import a third-party package at the top level at all.

   The first build of this arm asked whether the export DECLARED the package
   anywhere, and a round-2 adversarial reviewer refuted it in one move: this
   slice's other repair shipped `packaging/bootstrap-requirements.txt`, which
   declared pyyaml, jsonschema and packaging for the entire export at a stroke,
   so ~36 bare imports across ~29 modules kept raising the exact reported error
   while the gate went green. Declaration is not availability, and a shipped
   requirements file installs nothing.

   Scoped to documented entrypoints on purpose: that is the surface a consumer
   is TOLD to run, it is where the reported failure happened, and it is a set
   small enough that the remedy is a guard rather than a sweep. The rest of the
   export's bare imports are real risk and are reported as an inventory, not as
   a verdict -- said here rather than left to look like coverage.

ONLY THE DOCUMENTED-ENTRYPOINT ARM RENDERS A BLOCKING VERDICT, and the reason is a measured
one rather than a staging preference. Bounded review read the first
build of the path arm and showed it wrong in BOTH directions at once: it excused
`repo_root / "packaging" / f"{name}.json"` the moment this slice shipped two
files into `packaging/`, and it reported `root / "evals" / ...` in maintainer
tools where `root` is the repo the OPERATOR named -- code that is correct. Both
follow from one gap the arm cannot close as written: it cannot tell "reads its
own tree" from "scans whatever tree the caller passed". The export-safe gate
closes it by requiring the chain to be rooted at the module's own `REPO_ROOT`
name, and that discrimination is what this arm still owes.

So the path arm ships as an INVENTORY: it enumerates, it is regenerable, and it
does not refuse. Publishing it as a ratchet with a baseline would have made a
release-blocking gate out of a classification two reviewers independently
falsified, and the escape hatch (`--write-baseline`) would have become the
routine response. Named here rather than left as a quiet severity choice.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module
from tools.export_tools_reference_lib import (  # noqa: E402
    MOVED_TOOL_BASENAMES,
    exported_tools_reference_findings,
)

__all__ = ["MOVED_TOOL_BASENAMES", "exported_tools_reference_findings"]


_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")

#: Repo-root entries a CONSUMER owns, with the reason each is not a shipping gap.
#: A filled copy of any of these would overwrite the consumer's own state, so
#: "not shipped" is the correct behaviour rather than a defect to repair.
CONSUMER_OWNED_ROOTS = {
    ".agents": "adapter config the consumer authors; seeded, never overwritten",
    ".charness": "per-run local state, gitignored by construction",
    ".claude": "host-local settings owned by the consumer's editor/agent host",
    ".git": "the consumer's own repository metadata",
    ".githooks": "hooks the consumer installs into their own repo",
    "AGENTS.md": "the consumer's own agent contract; seeded by setup",
    "CLAUDE.md": "the consumer's own host doc surface; seeded by setup",
    "charness-artifacts": "the consumer's artifact tree, written at runtime",
    "docs": "the consumer's documentation tree, read and written at runtime",
    "node_modules": "installed by the consumer's package manager",
    "package.json": "the consumer's own JS manifest, read when present",
    "pyproject.toml": "the consumer's own Python manifest, read when present",
    "reports": "run output written into the consumer's repo",
    "specdown.json": "consumer-authored config, read when present",
    "specs": "the consumer's own spec tree",
    "tests": "the consumer's own test tree, scanned at runtime",
    "tools": "repository-only quality gates; never exported to consumers",
}


#: Filenames for the repository-only tool surface. An exported document or
#: executable carrier naming one of these files has leaked a command whose
#: implementation the export deliberately omits. Keep this explicit instead
#: of deriving it from the export: the empty export is the case this arm must
#: detect. The two small adapters below are new tools-only carriers, so they
#: are included even though no former ``scripts/`` path exists for them.
#: Literal prefixes this check does NOT own, with the owner named. The plugin
#: export collapses `skills/public/<skill>/` to `skills/<skill>/`, and
#: The native-backed `check-export-safe-imports` gate already renders a verdict on exactly that --
#: including a deliberate exemption for a chain rooted at an operator-supplied
#: `repo_root`, because a maintainer tool legitimately walks `skills/public/` in
#: whatever repo the caller named. Re-reporting those here would be the same
#: finding under a second name, and 60 of them would bury the findings this check
#: is the only one that can see.
COLLAPSE_PREFIXES_OWNED_BY_EXPORT_SAFE_IMPORTS = ("skills/public", "skills/support")


#: Distributions whose import name differs from the name a requirements file
#: spells. Kept explicit: guessing this mapping is how a declared dependency
#: reads as undeclared and a real gap hides in the noise.
IMPORT_NAME_TO_DISTRIBUTION = {
    "yaml": "pyyaml",
    "packaging": "packaging",
    "jsonschema": "jsonschema",
}


#: Repo-relative-or-as-given, from the repo's existing owner rather than a fourth
#: private copy. An absolute path in a reported finding pins one machine's
#: checkout and reads as noise on every other one.
_reported_path = _artifact_validator._artifact_label


def shipped_roots(export_root: Path) -> set[str]:
    """Top-level entries the export actually ships. Read from the CHECKED-IN
    tree, not from the exporter -- using the exporter here would rebuild the
    fixed-point blindness this module exists to escape."""
    return {entry.name for entry in export_root.iterdir()}


def _chain_segments(node: ast.AST) -> tuple[list[str], bool]:
    """The literal PREFIX of a `a / "x" / "y"` chain, leftmost first, plus whether
    the chain was literal all the way to its end.

    A prefix rather than all-or-nothing: `root / "evals" / name` names a
    directory the export either ships or does not, and that verdict does not
    depend on the computed leaf. Bailing on the whole chain hid exactly those
    sites -- measured, when de-duplicating nested chains made them disappear."""
    segments: list[str] = []
    complete = True
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        right = node.right
        if isinstance(right, ast.Constant) and isinstance(right.value, str):
            segments.append(right.value)
        else:
            # Everything to the RIGHT of a computed segment is unknown, so the
            # literal prefix restarts from here leftward.
            segments = []
            complete = False
        node = node.left
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        segments.append(node.value)
    return list(reversed(segments)), complete


def _first_segment(node: ast.AST) -> str | None:
    segments, _complete = _chain_segments(node)
    if not segments:
        return None
    head = segments[0].replace("\\", "/").split("/")[0]
    return head or None


def unshipped_path_findings(
    export_root: Path, *, repo_root_entries: set[str], relative_to: Path | None = None
) -> list[dict[str, object]]:
    """Path literals in exported source naming a repo-root entry the export omits.

    Scoped to segments that name something in the DEV repo's root: a chain
    starting with an arbitrary string is a relative path inside some tree the
    caller named, not a claim about this repo's layout, and reporting those would
    bury the real findings."""
    shipped = shipped_roots(export_root)
    findings: list[dict[str, object]] = []
    for path, tree in _iter_exported_modules(export_root):
        # OUTERMOST chain only. `a / "x" / "y"` is a BinOp whose `.left` is
        # itself a BinOp, so walking every node reports the same site once per
        # segment -- which inflates a count and, worse, makes a two-segment
        # finding look like two findings.
        inner = {
            id(node.left)
            for node in ast.walk(tree)
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
        }
        for node in ast.walk(tree):
            if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
                continue
            if id(node) in inner:
                continue
            segments, complete = _chain_segments(node)
            head = _first_segment(node)
            if head is None or head not in repo_root_entries:
                continue
            if head in CONSUMER_OWNED_ROOTS:
                continue
            relative = "/".join(segment.replace("\\", "/") for segment in segments).strip("/")
            if relative.startswith(COLLAPSE_PREFIXES_OWNED_BY_EXPORT_SAFE_IMPORTS):
                continue
            if head in shipped:
                # PATH depth, not AST-node count. `len(segments)` counts chain links, so
                # the same target escaped or was reported depending only on how it was
                # SPELLED: `root / "packaging" / "bootstrap-python.json"` is two links and
                # was judged, while `root / "packaging/bootstrap-python.json"` is one link
                # naming the same absent file and was skipped -- and the one-link spelling
                # is how the defect that opened this class was actually written.
                #
                # FIRST of the two guards, deliberately. Both `continue`, so the order
                # cannot change a verdict -- but it decides which one is REACHABLE.
                #
                # NOT because the depth guard was dead: `shipped_roots` lists NAMES via
                # `iterdir`, while `.exists()` FOLLOWS symlinks, so a dangling entry is
                # shipped-and-absent and reached the depth guard under either order
                # (measured: `iterdir` yields it, `.exists()` is False). What is true is
                # narrower -- whenever the export tree RESOLVES, a depth-1 `relative`
                # under a shipped head is the head itself and therefore exists, so
                # `.exists()` first swallowed every ordinary input this guard is written
                # for and a test named after the depth rule passed one branch early.
                # Ordering it first makes the bare shipped-directory case exercise the
                # rule that actually decides it, without resting on a dead-code claim
                # that a broken symlink refutes.
                if len([part for part in relative.split("/") if part]) < 2:
                    continue
                # A SHIPPED first segment is not enough. Shipping two files out of
                # `packaging/` makes the directory present while every other path
                # under it is still absent, and a first-segment rule would call
                # that clean -- the same partial-shipping shape as the defect.
                # Only a fully literal chain proves the exact target; a chain with
                # a computed leaf is judged on the literal prefix it does name.
                if (export_root / relative).exists():
                    continue
            findings.append(
                {
                    "kind": "unshipped-path",
                    "path": _reported_path(path, relative_to),
                    "line": node.lineno,
                    "segment": head,
                    "literal": relative,
                }
            )
    return findings


#: How an exported doc/adapter spells a command a consumer should run. The
#: `$SKILL_DIR` form is the export's own 100+-site convention; a script named
#: this way is a surface a consumer is TOLD to execute.
DOCUMENTED_ENTRYPOINT_RE = re.compile(r"(?:\$SKILL_DIR|\$\{SKILL_DIR\})/scripts/([a-z0-9_]+\.py)")
_ENTRYPOINT_DOC_SUFFIXES = (".md", ".yaml", ".yml", ".json")


def documented_entrypoint_names(export_root: Path) -> set[str]:
    """Script filenames an exported doc, reference, or adapter tells a consumer to run."""
    names: set[str] = set()
    for path in export_root.rglob("*"):
        if path.suffix not in _ENTRYPOINT_DOC_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        names.update(DOCUMENTED_ENTRYPOINT_RE.findall(text))
    return names


#: A doc/adapter site spelling a command as `python3 scripts/<name>.py`. On a
#: consumer machine `scripts/` is the CONSUMER's repo root, not the plugin, so
#: the instruction resolves to the wrong tree -- or to nothing -- even though the
#: script ships. `<plugin-dir>/scripts/<name>.py` is the spelling that resolves
#: in both trees (`check_plugin_dir_references.py` owns that placeholder).
REPO_ROOT_SCRIPT_INSTRUCTION_RE = re.compile(r"python3 scripts/([a-z0-9_]+\.(?:py|sh))")

#: A generated file's header names the generator that produced it. That is
#: PROVENANCE for whoever regenerates it in THIS repo -- a maintainer action --
#: not an instruction a consumer follows, and rewriting it would make the header
#: unable to describe its own regeneration. Skipped by field name rather than by
#: per-file exemption, because every generated file in the export carries it.
#:
#: Applied ONLY to files that declare `generated_file: true`. `sync_command` is
#: also a live adapter CONFIG key -- `skills/release/adapter.example.yaml:10` --
#: so matching the field name everywhere silently exempted a real finding and the
#: load-bearing test caught it one edit later.
GENERATED_HEADER_FIELD_RE = re.compile(r"^\s*(?:generator|sync_command):")
GENERATED_FILE_MARKER = "generated_file: true"

#: Sites where `python3 scripts/...` is a CONFIG VALUE, not an instruction to type.
#: Two different reasons live here and the difference matters:
#:
#: 1. CONSUMER-OWNED values a consumer replaces with their own command.
#: 2. EXECUTED values run by the subprocess runner after `shlex.split(command)`.
#: `<plugin-dir>/`
#:    is a DOC placeholder that no runtime substitutes -- `check_plugin_dir_references`
#:    says so in its own docstring -- so applying the remedy to an executed field
#:    converts a working command into `can't open file`. The first build of this arm
#:    did exactly that to five render-critique sites before a reviewer caught it.
#:
#: Each entry carries which reason applies, because an unexplained allowlist is how
#: this class returns. Matched by EXACT relative path, not suffix: `endswith` would
#: silently exempt any future nested path ending in one of these strings.
INSTRUCTION_EXEMPT_PATHS = {
    "skills/critique/references/adapter-contract.md": (
        "EXECUTED: documents the critique adapter's `command:` value, which "
        "critique_packet_lib runs through subprocess; the doc must show the runnable "
        "spelling or a consumer copies a broken one"
    ),
    "skills/critique/references/prepare-packet.md": (
        "EXECUTED: names the producer for that same `command:` field"
    ),
    "skills/retro/references/adapter-contract.md": (
        "EXECUTED: documents the retro adapter's `command:` value, same executor"
    ),
    "skills/release/references/adapter-contract.md": (
        "EXECUTED: documents `sync_command`, which resolve_adapter.EXECUTED_COMMAND_FIELDS "
        "names as one of the release adapter's two RUN fields. Consumer-REPLACEABLE and "
        "executed are independent; this is the executed one"
    ),
    "skills/quality/references/cost-dominance.md": (
        "CONSUMER-OWNED: the `replacement:` key is a value a repo author fills in with "
        "THEIR fast runner. Residual, tracked not banked: a consumer copying the schema "
        "example verbatim reproduces the #634 shape, and the example carries no warning"
    ),
}


def repo_root_instruction_findings(
    export_root: Path, *, apply_exemptions: bool = True
) -> list[dict[str, object]]:
    """Exported docs telling a consumer to run `python3 scripts/<name>.py`.

    The sibling of the path arm, asked about PROSE rather than code. The path arm
    reads Python literals; this reads what a consumer is told to type. Both come
    from #634's class -- an exported artifact naming a repo-root location the
    consumer does not have -- but nothing in the AST arm can see a markdown line.

    Reported only when the named script SHIPS in the export: an unshipped name is
    either the path arm's business or a genuine consumer-owned command, and
    claiming both here would rebuild the falsified classification the path arm
    already paid for.

    Blind class, stated because the first two builds of the sibling arms were
    refuted on exactly this: it matches ONE spelling (`python3 scripts/X`). A doc
    saying `run scripts/X.py`, or building the path across a line break, or using
    `./scripts/X.py`, is invisible to it. It also cannot tell an instruction from
    a config value -- that distinction is carried by INSTRUCTION_EXEMPT_PATHS,
    which is a declaration, not a measurement.
    """
    findings: list[dict[str, object]] = []
    shipped = {path.name for path in (export_root / "scripts").glob("*") if path.is_file()}
    for path in sorted(export_root.rglob("*")):
        if path.suffix not in (*_ENTRYPOINT_DOC_SUFFIXES, ".py") or not path.is_file():
            continue
        relative = path.relative_to(export_root).as_posix()
        if apply_exemptions and relative in INSTRUCTION_EXEMPT_PATHS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        # Header region only: the marker appears mid-file in docs ABOUT generated
        # files, and in this module as a constant value. Whole-file matching let
        # such a file exempt its own real instructions.
        is_generated = GENERATED_FILE_MARKER in "\n".join(text.splitlines()[:10])
        for lineno, line in enumerate(text.splitlines(), start=1):
            if is_generated and GENERATED_HEADER_FIELD_RE.match(line):
                continue
            for name in REPO_ROOT_SCRIPT_INSTRUCTION_RE.findall(line):
                if name not in shipped:
                    continue
                findings.append(
                    {
                        "doc": relative,
                        "line": lineno,
                        "script": name,
                        "site_class": _instruction_site_class(relative),
                        "remedy": f"python3 <plugin-dir>/scripts/{name}",
                    }
                )
    return findings


def _instruction_site_class(relative: str) -> str:
    """`consumer-doc` for PROSE a consumer reads and types; `module-prose` for
    everything else, which is advisory inventory.

    Only `.md` outside a `scripts/` directory is consumer-doc, and the narrowing is
    the whole lesson of this arm's first two builds. A `.yaml`/`.json` file holds
    VALUES, and a value under `command:`, `commands:`, `sync_command:` or
    `quality_command:` is RUN by an executor -- `critique_packet_lib._run_command`
    shells `command:`, `control_plane_lib.run_shell` runs `checks.*.commands`, and
    `resolve_adapter.EXECUTED_COMMAND_FIELDS` names `sync_command`/`quality_command`
    as the release adapter's two RUN fields. `<plugin-dir>/` is a DOC placeholder no
    runtime substitutes, so prescribing it into any of those converts a working
    command into `can't open file`. Build one rewrote five such values; build two
    reverted them but left the classifier able to BLOCK on the next one, with the
    remedy still prescribing the break. Config cannot reach the blocking arm now.

    Blind class: a consumer instruction living in a `.yaml` comment or a JSON
    `description` is real and is under-reported here. That is the deliberate side to
    err on -- a missed advisory entry costs an inventory line, a wrong block costs a
    broken command.
    """
    if relative.endswith(".md") and "/scripts/" not in relative:
        return "consumer-doc"
    return "module-prose"


def _guarded_import_lines(tree: ast.AST) -> set[int]:
    """Line numbers of imports inside a `try`, which is the form that CAN name a
    remedy. A function-level import is NOT included: it only DEFERS the
    ModuleNotFoundError to call time, which is the reported failure one call
    deeper. The first version of this module claimed otherwise in a docstring;
    a round-2 reviewer measured six live counter-instances in the export."""
    guarded: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        for statement in node.body:
            for sub in ast.walk(statement):
                if isinstance(sub, (ast.Import, ast.ImportFrom)):
                    guarded.add(sub.lineno)
    return guarded


def _iter_exported_modules(export_root: Path):
    """`(path, tree)` for every parseable Python file in the export, sorted.

    ONE walker for all three arms. Each asks a different question of the tree,
    but "which files are the export's Python, and what do we do with one that
    will not parse" is the same answer three times, and three copies is how they
    drift apart on the day someone adds an exclusion to one."""
    for path in sorted(export_root.rglob("*.py")):
        try:
            yield path, ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue


def _third_party_imports(tree: ast.AST, local: set[str], *, nodes) -> list[tuple[int, str]]:
    """`(lineno, module)` for each import of a name that is neither stdlib nor
    resolvable inside the export.

    ONE walker for both dependency arms. They ask different questions -- one about
    documented entrypoints anywhere in the file, one about top-level imports
    across the whole export -- but "which of these names is third-party" is the
    same question, and a second copy is how two arms end up disagreeing about
    what `packaging` is."""
    found: list[tuple[int, str]] = []
    for node in nodes:
        if isinstance(node, ast.Import):
            names = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names = [node.module.split(".")[0]]
        else:
            continue
        for name in names:
            if name in sys.stdlib_module_names or name in local:
                continue
            found.append((node.lineno, name))
    return found


def unguarded_entrypoint_import_findings(
    export_root: Path, *, relative_to: Path | None = None
) -> list[dict[str, object]]:
    """A DOCUMENTED consumer entrypoint importing a third-party package unguarded.

    The blocking arm, and the one that maps to the reported failure: a consumer
    followed a SKILL.md, ran the command, and got a bare `ModuleNotFoundError`
    with nothing naming what to install."""
    documented = documented_entrypoint_names(export_root)
    local = _local_module_names(export_root)
    findings: list[dict[str, object]] = []
    for path, tree in _iter_exported_modules(export_root):
        if path.name not in documented:
            continue
        guarded = _guarded_import_lines(tree)
        for lineno, name in _third_party_imports(tree, local, nodes=ast.walk(tree)):
            if lineno in guarded:
                continue
            findings.append(
                {
                    "kind": "unguarded-entrypoint-import",
                    "path": _reported_path(path, relative_to),
                    "line": lineno,
                    "module": name,
                    "entrypoint": path.name,
                }
            )
    return findings


def declared_distributions(export_root: Path) -> set[str]:
    """Third-party distributions the EXPORT declares, from whatever dependency
    contract it ships. Empty when it ships none -- which is the reported defect,
    not a reason to fall back to the repo's own declaration."""
    declared: set[str] = set()
    for requirements in sorted(export_root.rglob("*requirements*.txt")):
        for raw in requirements.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            name = line
            for separator in ("[", "=", ">", "<", "!", "~", ";", " "):
                name = name.split(separator, 1)[0]
            if name:
                declared.add(name.strip().lower())
    return declared


def _local_module_names(export_root: Path) -> set[str]:
    """Names that resolve to something INSIDE the export, so an import of them is
    not a third-party dependency.

    A directory only counts when it CONTAINS Python -- a round-1 reviewer
    measured the alternative: taking every top-level entry name made shipping
    `packaging/bootstrap-*.json` shadow the `packaging` DISTRIBUTION, so
    `from packaging.version import ...` in two exported modules stopped being
    checked at the moment this slice created the directory. The fix for one
    instance blinded the arm to another."""
    names = {path.stem for path in export_root.rglob("*.py")}
    names.update(
        entry.name for entry in export_root.iterdir() if entry.is_dir() and any(entry.rglob("*.py"))
    )
    return names


def undeclared_dependency_findings(
    export_root: Path, *, relative_to: Path | None = None
) -> list[dict[str, object]]:
    """Top-level imports of a third-party package the export declares nowhere.

    TOP-LEVEL only, deliberately: an import inside a `try` or a function is the
    guarded form, and this repo already handles its optional dependencies that
    way (`cosmic_ray`, `tomli`, `curl_cffi`). Reporting those would say the
    correct pattern is the defect."""
    declared = declared_distributions(export_root)
    local = _local_module_names(export_root)
    findings: list[dict[str, object]] = []
    for path, tree in _iter_exported_modules(export_root):
        for lineno, name in _third_party_imports(tree, local, nodes=tree.body):
            distribution = IMPORT_NAME_TO_DISTRIBUTION.get(name, name).lower()
            if distribution in declared:
                continue
            findings.append(
                {
                    "kind": "undeclared-dependency",
                    "path": _reported_path(path, relative_to),
                    "line": lineno,
                    "module": name,
                    "distribution": distribution,
                }
            )
    return findings
