#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from scripts import quality_label_universe


class ValidationError(Exception):
    pass


FRESHNESS_LABEL = "validate-current-pointer-freshness"
FRESHNESS_SCRIPT = Path("tools/validate_current_pointer_freshness.py")
FRESHNESS_MODULE = "tools.validate_current_pointer_freshness"
RUN_QUALITY_SCRIPT = Path("scripts/run-quality.sh")
CURRENT_POINTERS = (Path("charness-artifacts/quality/latest.md"),)
QUALITY_POINTER = Path("charness-artifacts/quality/latest.md")
RELEASE_POINTER = Path("charness-artifacts/release/latest.md")
PACKAGING_MANIFEST = Path("packaging/charness.json")
CODEX_PLUGIN_MANIFEST = Path("plugins/charness/.codex-plugin/plugin.json")
CLAUDE_PLUGIN_MANIFEST = Path("plugins/charness/.claude-plugin/plugin.json")
GITIGNORE = Path(".gitignore")
RUNTIME_RECORDER = Path("scripts/gates_support/record_quality_runtime.py")
RUNTIME_BUDGET_CHECKER = Path("skills/public/quality/scripts/check_runtime_budget.py")
RUNTIME_BUDGET_LIB = Path("skills/public/quality/scripts/runtime_budget_lib.py")
RUNTIME_SIGNALS = Path(".charness/quality/runtime-signals.json")
CAPABILITY_CATALOG = Path("charness-artifacts/capability-catalog/latest.json")
INTEGRATIONS_DIR = Path("integrations/tools")
STALE_POINTER_PHRASES = {
    Path("charness-artifacts/quality/latest.md"): (
        "No deterministic freshness check yet",
        "add a narrow freshness check so rolling pointers",
        "extend `validate-current-pointer-freshness` beyond stale validator-existence claims",
    ),
}
COMMAND_RE = re.compile(r"`(python3 [^`]+|\.\/scripts\/[^`]+)`")
# The claim line, in every rendering an author plausibly writes it: backticked
# (canonical), bold, or bare. The old pattern required backticks and a leading
# `- `, so re-rendering the same claim as `- target version: **2.11.2**` made the
# cross-check silently no-op — the one standing check that the release pointer
# agrees with the shipped manifests (D5).
TARGET_VERSION_RE = re.compile(
    r"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?target version(?:\*\*)?[ \t]*:[ \t]*"
    r"(?:`(?P<tick>[^`]+)`|\*\*(?P<bold>[^*]+)\*\*|(?P<bare>[^\s`*]+))[ \t]*$"
)


# Values that are the SHAPE of a claim without being one. They must route to the
# "unestablished" message, not be compared as if they were versions — otherwise
# `target version: TBD` reports "manifest is 2.11.3, pointer claims TBD", which
# diagnoses the wrong problem.
_CLAIM_PLACEHOLDERS = frozenset({"", "tbd", "todo", "n/a", "na", "none", "unknown", "pending", "x"})
# Fenced blocks in the release artifact carry verbatim captured tool output
# (`charness update` tails, changed-path lists). A claim-shaped line appearing
# there is quoted text, not the artifact's own assertion.
_FENCE_RE = re.compile(r"(?ms)^[ \t]*(`{3,}|~{3,}).*?(?:^[ \t]*\1[ \t]*$|\Z)")


def _claimed_versions(release_text: str) -> list[str]:
    """Every target-version claim the artifact ASSERTS, in order.

    ALL of them, not the first: ``re.search`` returned the first match, so a
    decoy line earlier in the file that happened to agree with the manifests
    shadowed a genuinely stale claim below it and the comparison never ran on the
    real one (D5).

    Values are stripped of residual markup, because the three renderings nest:
    ``**`2.11.3`**`` captured the backticks inside the bold group and compared
    them literally, turning a current pointer into a false "stale" verdict.
    Placeholders are dropped so they surface as an unestablished claim instead.
    """
    claims: list[str] = []
    for match in TARGET_VERSION_RE.finditer(_FENCE_RE.sub("", release_text)):
        value = match.group("tick") or match.group("bold") or match.group("bare") or ""
        value = value.strip().strip("`*").strip().rstrip(".").strip()
        if value and value.lower() not in _CLAIM_PLACEHOLDERS:
            claims.append(value)
    return claims


def read_text(repo_root: Path, relative_path: Path) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        raise ValidationError(f"missing current pointer `{relative_path}`")
    return path.read_text(encoding="utf-8")


def validate_gate_is_queued(repo_root: Path) -> None:
    try:
        rows = quality_label_universe.quality_gate_rows(repo_root)
    except quality_label_universe.UniverseError as error:
        raise ValidationError(str(error)) from error
    if rows is not None:
        queued = any(
            row.get("label") == FRESHNESS_LABEL
            and (
                FRESHNESS_MODULE in row.get("command", [])
                or str(FRESHNESS_SCRIPT) in row.get("command", [])
            )
            for row in rows
        )
    else:
        run_quality = read_text(repo_root, RUN_QUALITY_SCRIPT)
        expected_label = f'queue_selected "{FRESHNESS_LABEL}"'
        expected_command = f"python3 -m {FRESHNESS_MODULE}"
        queued = expected_label in run_quality and expected_command in run_quality
        if not queued:
            raise ValidationError(
                f"`scripts/run-quality.sh` must queue `{FRESHNESS_LABEL}` via `{expected_command}`"
            )
        return
    if not queued:
        raise ValidationError(
            f"`{quality_label_universe.QUALITY_GATES_PATH}` must declare "
            f"`{FRESHNESS_LABEL}` via `{FRESHNESS_MODULE}`"
        )


def validate_no_stale_claims(repo_root: Path) -> None:
    stale_hits: list[str] = []
    for relative_path in CURRENT_POINTERS:
        text = read_text(repo_root, relative_path)
        for phrase in STALE_POINTER_PHRASES.get(relative_path, ()):
            if phrase in text:
                stale_hits.append(f"{relative_path}: stale phrase `{phrase}`")
    if stale_hits:
        raise ValidationError(
            "rolling current-pointer freshness claims are stale:\n"
            + "\n".join(f"- {hit}" for hit in stale_hits)
        )


def command_script_path(command: str) -> Path | None:
    parts = command.split()
    if not parts:
        return None
    if parts[0] == "python3" and len(parts) > 1:
        return Path(parts[1])
    if parts[0].startswith("./"):
        return Path(parts[0][2:])
    return None


def validate_quality_command_claims(repo_root: Path) -> None:
    quality = read_text(repo_root, QUALITY_POINTER)
    missing: list[str] = []
    for command in COMMAND_RE.findall(quality):
        script_path = command_script_path(command)
        if script_path is not None and not (repo_root / script_path).is_file():
            missing.append(f"`{command}` references missing `{script_path}`")
    if missing:
        raise ValidationError(
            "quality pointer command claims are stale:\n"
            + "\n".join(f"- {item}" for item in missing)
        )


def validate_runtime_smoothing_claim(repo_root: Path) -> None:
    quality = read_text(repo_root, QUALITY_POINTER)
    if "Runtime EWMA is advisory" not in quality:
        return

    gitignore = read_text(repo_root, GITIGNORE)
    recorder = read_text(repo_root, RUNTIME_RECORDER)
    checker = read_text(repo_root, RUNTIME_BUDGET_CHECKER)
    runtime_budget_sources = checker
    runtime_budget_lib = repo_root / RUNTIME_BUDGET_LIB
    if runtime_budget_lib.is_file():
        runtime_budget_sources += "\n" + runtime_budget_lib.read_text(encoding="utf-8")
    missing: list[str] = []
    required_fragments = (
        (GITIGNORE, gitignore, ".charness/quality/runtime-smoothing.json"),
        (RUNTIME_RECORDER, recorder, 'SMOOTHING_FILENAME = "runtime-smoothing.json"'),
        (RUNTIME_RECORDER, recorder, "SMOOTHING_ALPHA_BASE = 0.35"),
        (RUNTIME_RECORDER, recorder, "SMOOTHING_WARMUP_N = 5"),
        (RUNTIME_RECORDER, recorder, '"advisory": True'),
        (
            RUNTIME_BUDGET_CHECKER,
            runtime_budget_sources,
            'SMOOTHING_PATH = Path(".charness") / "quality" / "runtime-smoothing.json"',
        ),
        (RUNTIME_BUDGET_CHECKER, runtime_budget_sources, "ewma_advisory_elapsed_ms"),
        (
            RUNTIME_BUDGET_CHECKER,
            runtime_budget_sources,
            "ewma {entry['ewma_advisory_elapsed_ms']:.1f}ms advisory",
        ),
    )
    for relative_path, text, fragment in required_fragments:
        if fragment not in text:
            missing.append(f"`{relative_path}` missing `{fragment}`")
    if missing:
        raise ValidationError(
            "quality pointer runtime smoothing claim is stale:\n"
            + "\n".join(f"- {item}" for item in missing)
        )


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _json_version(repo_root: Path, relative_path: Path) -> str | None:
    payload = _load_json(repo_root / relative_path)
    version = payload.get("version")
    return version if isinstance(version, str) else None


def validate_release_version_claim(repo_root: Path) -> None:
    release_path = repo_root / RELEASE_POINTER
    if not release_path.is_file():
        return
    release = release_path.read_text(encoding="utf-8")
    claims = _claimed_versions(release)
    if not claims:
        # An existing release pointer with no parseable claim is an UNESTABLISHED
        # scope, not a satisfied one. Returning silently here is what made a
        # reformatted claim indistinguishable from a verified one (D5).
        raise ValidationError(
            f"`{RELEASE_POINTER}` exists but carries no parseable `target version:` claim, so the "
            "release pointer was never compared against the shipped manifests. Write the claim as "
            "`- target version: `<version>`` (backticks, bold, or bare all parse)."
        )
    distinct = sorted(set(claims))
    if len(distinct) > 1:
        raise ValidationError(
            f"`{RELEASE_POINTER}` carries disagreeing target-version claims "
            + ", ".join(f"`{value}`" for value in distinct)
            + "; a decoy claim shadowing the real one is exactly what made this check pass over a "
            "stale release. Leave one claim."
        )
    claimed_version = distinct[0]
    version_sources = (
        (PACKAGING_MANIFEST, _json_version(repo_root, PACKAGING_MANIFEST)),
        (CODEX_PLUGIN_MANIFEST, _json_version(repo_root, CODEX_PLUGIN_MANIFEST)),
        (CLAUDE_PLUGIN_MANIFEST, _json_version(repo_root, CLAUDE_PLUGIN_MANIFEST)),
    )
    stale = [
        f"`{relative_path}` version is `{version}`, release pointer claims `{claimed_version}`"
        for relative_path, version in version_sources
        if version != claimed_version
    ]
    if stale:
        raise ValidationError(
            "release pointer version claim is stale:\n" + "\n".join(f"- {item}" for item in stale)
        )


def _manifest_default(field: str) -> object:
    return None if field == "recommendation_role" else []


def _load_catalog_sanitizer(repo_root: Path):
    """Load the stable capability catalog sanitizer so the validator can
    apply the same provider-id alias + text sanitization the inventory does.

    Returns ``(alias_path_fn, sanitize_value_fn)``. If the module cannot be
    found (split-install missing the source tree), returns ``(None, None)``
    and the caller falls back to verbatim comparison.
    """
    import importlib.util

    candidate = repo_root / "scripts/adapters/capability_catalog_sources.py"
    if not candidate.is_file():
        return None, None
    repo_root_str = str(repo_root)
    added_path = False
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
        added_path = True
    try:
        spec = importlib.util.spec_from_file_location("_capability_catalog_sources", candidate)
        if spec is None or spec.loader is None:
            return None, None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "_alias_path", None), getattr(module, "_sanitize", None)
    finally:
        if added_path:
            sys.path.remove(repo_root_str)


def validate_capability_catalog_integration_claims(repo_root: Path) -> None:
    inventory_path = repo_root / CAPABILITY_CATALOG
    integrations_dir = repo_root / INTEGRATIONS_DIR
    if not inventory_path.is_file():
        # No catalog pointer to check freshness of. Genuinely not-configured.
        return
    payload = _load_json(inventory_path)
    if not payload:
        # `_load_json` swallows OSError and JSONDecodeError and returns {}, so an
        # unreadable or truncated catalog would otherwise be reported as a SHAPE
        # problem ("inventory is NoneType") — the right refusal with the wrong
        # diagnosis, which costs the reader the actual remedy.
        raise ValidationError(
            f"`{CAPABILITY_CATALOG}` exists but could not be read as JSON (empty, truncated, or "
            "malformed), so its integration claims were never compared against the checked-in "
            "manifests. Regenerate the catalog."
        )
    schema_version = payload.get("schema_version")
    if schema_version != 1:
        # This validator reads the v1 shape. A catalog written by a schema it
        # does not understand must say so, not be reported as malformed v1.
        raise ValidationError(
            f"`{CAPABILITY_CATALOG}` declares schema_version {schema_version!r}, which this "
            "freshness check does not read; its integration claims were never compared. Update "
            "`validate_capability_catalog_integration_claims` for the new schema."
        )
    inventory = payload.get("inventory")
    if not isinstance(inventory, dict):
        # The catalog EXISTS but its inventory is not the shape this check reads.
        # Returning silently made a malformed catalog indistinguishable from a
        # verified-fresh one: with a genuinely stale claim in place, corrupting
        # the shape flipped BLOCK to PASS (D10).
        raise ValidationError(
            f"`{CAPABILITY_CATALOG}` exists but its `inventory` is "
            f"{type(inventory).__name__}, not an object, so its integration claims were never "
            "compared against the checked-in manifests. Regenerate the catalog."
        )
    if not integrations_dir.is_dir():
        # A missing integrations tree is fine ONLY when the catalog claims no
        # integrations. If it claims some, the tree they describe is gone and
        # every claim is stale — which is exactly what returning here hid.
        claimed = [item for item in inventory.get("integrations", []) if isinstance(item, dict)]
        if claimed:
            raise ValidationError(
                f"`{CAPABILITY_CATALOG}` claims {len(claimed)} integration(s), but "
                f"`{INTEGRATIONS_DIR}` does not exist, so none of those claims could be "
                "compared against a manifest. Regenerate the catalog or restore the directory."
            )
        return
    alias_path, sanitize_value = _load_catalog_sanitizer(repo_root)
    artifact_integrations = {
        item.get("path"): item
        for item in inventory.get("integrations", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    stale: list[str] = []
    for manifest_path in sorted(integrations_dir.glob("*.json")):
        if manifest_path.name in {
            "manifest.schema.json",
            "dependencies.json",
            "dependencies.schema.json",
        }:
            continue
        manifest = _load_json(manifest_path)
        relative_path = str(manifest_path.relative_to(repo_root))
        lookup_path = alias_path(relative_path) if alias_path is not None else relative_path
        artifact_entry = artifact_integrations.get(lookup_path)
        if not artifact_entry:
            stale.append(f"`{relative_path}` missing from `{CAPABILITY_CATALOG}`")
            continue
        for field in ("intent_triggers", "supports_public_skills", "recommendation_role"):
            manifest_value = manifest.get(field, _manifest_default(field))
            expected = (
                sanitize_value(manifest_value) if sanitize_value is not None else manifest_value
            )
            if artifact_entry.get(field) != expected:
                stale.append(f"`{relative_path}` `{field}` differs from `{CAPABILITY_CATALOG}`")
    if stale:
        raise ValidationError(
            "capability catalog pointer is stale:\n" + "\n".join(f"- {item}" for item in stale)
        )


def validate_current_pointer_freshness(repo_root: Path) -> None:
    validate_gate_is_queued(repo_root)
    validate_no_stale_claims(repo_root)
    validate_quality_command_claims(repo_root)
    validate_runtime_smoothing_claim(repo_root)
    # `validate_quality_runtime_signal_claims` used to be called here. Its entire
    # body was `_ = repo_root` — a registered check that rendered no verdict, so a
    # reader of this list saw seven checks and believed seven things were checked.
    # Its own comment said why it was empty (runtime samples are written by the
    # same runner that calls this gate, and artifact shape is checked by
    # `validate_quality_artifact`), which makes the emptiness deliberate and the
    # registration the mistake. Deleted rather than kept: a name that claims a
    # verdict it does not render is the fail-open shape this sweep measured.
    validate_release_version_claim(repo_root)
    validate_capability_catalog_integration_claims(repo_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    validate_current_pointer_freshness(repo_root)
    print("Validated rolling current-pointer freshness claims.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
