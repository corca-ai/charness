"""Verifying a RECORDED reviewed-input identity, as opposed to building one.

Split from `scripts/review/reviewed_input_identity.py`, which owns production: git
enumeration, range resolution, path checking, and content digests. This module
owns the other half — deciding whether a binding that was already written down
still holds, and whether a critique artifact declares one at all.

The split is also why `reviewed_input_identity` can stay a leaf: the shipped
reviewer runtime loads a module BY FILE PATH (`spec_from_file_location`), with no
package context, so anything it loads must resolve its own siblings the same way.
The `_load_identity` fallback below is that resolution, not decoration.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

def _load_identity():
    """The identity module ADJACENT to this file, never one that merely shares its name.

    Order matters and it used to be backwards. Trying `from scripts import
    reviewed_input_identity` first let any already-importable module of that name
    win -- including a consumer repo's own `scripts/review/reviewed_input_identity.py` --
    even though this verifier had itself been loaded by file path precisely
    because there is no trustworthy package context there. A fresh-eye review
    proved the substitution by preloading a synthetic module and watching the
    verifier report the consumer's constants.

    An already-imported module is reused ONLY when it is byte-identically this
    same file. That is not an optimisation: re-executing the file would create a
    second module object, and the owner would stop being authoritative under
    monkeypatch exactly the way an import-time alias did.
    """
    sibling = Path(__file__).resolve().with_name("reviewed_input_identity.py")
    canonical = "scripts.review.reviewed_input_identity"
    loaded = sys.modules.get(canonical)
    loaded_file = getattr(loaded, "__file__", None)
    if loaded_file is not None and Path(loaded_file).resolve() == sibling:
        return loaded
    if sibling.is_file():
        # Import through the canonical name when — and only when — that name
        # already resolves to THIS file. Loading it by path instead would build a
        # second module object, so a later `from scripts import
        # reviewed_input_identity` would hold a different one and patching either
        # would leave the other stale. Which object you get must not depend on
        # who imported first.
        try:
            spec = importlib.util.find_spec(canonical)
        except (ImportError, ValueError):
            spec = None
        if spec is not None and spec.origin and Path(spec.origin).resolve() == sibling:
            return importlib.import_module(canonical)
        spec = importlib.util.spec_from_file_location("charness_reviewed_input_identity", sibling)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    from scripts.review import reviewed_input_identity as module  # noqa: PLC0415

    return module


_identity = _load_identity()

ALGORITHM = _identity.ALGORITHM
SUBSTRATE_MODES = _identity.SUBSTRATE_MODES
SUBSTRATE_COMMITTED_REF = _identity.SUBSTRATE_COMMITTED_REF
SUBSTRATE_WORKING_TREE = _identity.SUBSTRATE_WORKING_TREE
ReviewedInputError = _identity.ReviewedInputError

# NOT aliased. Binding the callable at import time made the owner module
# non-authoritative: patching `reviewed_input_identity.build_reviewed_input_identity`
# left this module still calling the copy it captured. Two names for one function
# that can diverge is the same defect class this module exists to police, so the
# call goes through `_identity` and the owner stays the only definition.
_LEGACY_SUBSTRATE_MODE_ALIASES = _identity._LEGACY_SUBSTRATE_MODE_ALIASES
_SHA256_RE = _identity._SHA256_RE
_sha256 = _identity._sha256

ARTIFACT_HEADING = "## Reviewed Input Identity"
# floor-addition-restraint: keep — this typed form is consumed at release/closeout,
# where silently reusing a stale verdict can escape an irreversible boundary;
# enforcement is limited to packet-bound critiques and grandfathered by date.
ARTIFACT_REQUIRED_FIELDS = ("packet path", "packet sha256", "identity sha256")
ARTIFACT_BINDING_RULE_DATE = date(2026, 7, 20)
LEGACY_UNDATED_ARTIFACTS = frozenset({"release-0-55-1-critique.md"})


def artifact_binding_required(path_name: str, observed_date: date | None, packet_consumed: bool) -> bool:
    if not packet_consumed:
        return False
    if observed_date is not None:
        return observed_date >= ARTIFACT_BINDING_RULE_DATE
    return path_name not in LEGACY_UNDATED_ARTIFACTS
def verify_reviewed_input_identity(repo_root: Path, identity: dict[str, Any]) -> tuple[bool, str]:
    if identity.get("status") != "captured":
        return False, "reviewed input identity was unavailable when the packet was produced"
    if identity.get("algorithm") != ALGORITHM:
        return False, f"reviewed input identity must use `{ALGORITHM}`"
    if "reviewed_paths" not in identity or identity.get("reviewed_paths") is None:
        return False, "declared reviewed inputs cover zero paths"
    if not isinstance(identity.get("reviewed_paths"), list):
        return False, "cannot reconstruct reviewed input identity: reviewed_paths must be a list"
    if not identity.get("reviewed_paths"):
        # An empty path set digests to the same constant in every repo forever, so
        # it would verify as `current` while proving nothing. Reject it as a
        # binding rather than let a zero-input verdict read as a checked one.
        return False, "declared reviewed inputs cover zero paths"
    mode = identity.get("substrate_mode") or identity.get("mode")
    mode = _LEGACY_SUBSTRATE_MODE_ALIASES.get(mode, mode)
    if mode not in SUBSTRATE_MODES or identity.get("mode") != mode:
        return False, "reviewed input identity has an invalid or missing substrate mode"
    if (mode == SUBSTRATE_COMMITTED_REF) != bool(identity.get("changed_ref")):
        return False, "reviewed input identity substrate mode does not match changed_ref"
    try:
        current = _identity.build_reviewed_input_identity(
            repo_root=repo_root,
            reviewed_paths=list(identity["reviewed_paths"]),
            changed_ref=identity.get("changed_ref"),
            substrate_mode=mode,
        )
    except ReviewedInputError as exc:
        return False, f"{exc.code}: {exc}"
    except (KeyError, TypeError, ValueError) as exc:
        return False, f"cannot reconstruct reviewed input identity: {exc}"
    for item in current.get("reviewed_content", []):
        if not isinstance(item, dict) or not _SHA256_RE.fullmatch(str(item.get("content_sha256", ""))):
            return False, "reviewed input identity contains a null or invalid content hash"
    for field in ("reviewed_patch_sha256", "staged_patch_sha256", "unstaged_patch_sha256"):
        if not _SHA256_RE.fullmatch(str(current.get(field, ""))):
            return False, f"reviewed input identity contains a null or invalid {field}"
    if current["identity_sha256"] != identity.get("identity_sha256"):
        return False, "declared reviewed inputs are stale"
    return True, "current"
def packet_file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())
def _canonical_packet_path(repo_root: Path, packet_path: str) -> tuple[Path | None, str | None]:
    raw = Path(packet_path)
    if raw.is_absolute() or ".." in raw.parts:
        return None, "reviewed packet path resolves outside repo root"
    lexical = repo_root / raw
    if lexical.is_symlink():
        return None, "reviewed packet path must not be a symlink"
    candidate = lexical.resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        return None, "reviewed packet path resolves outside repo root"
    return candidate, None
def _reconcile_substrate_modes(
    packet: dict[str, Any], identity: dict[str, Any]
) -> tuple[str | None, str | None, bool, bool]:
    """(packet_mode, identity_mode, identity_declared_one, packet_is_legacy).

    Historical v1 packets carried the mode only inside the reviewed-input
    identity. That immutable evidence is preserved while newly produced packets
    are required to emit the top-level field.
    """
    packet_mode = packet.get("substrate_mode")
    packet_mode = _LEGACY_SUBSTRATE_MODE_ALIASES.get(packet_mode, packet_mode)
    identity_mode = identity.get("substrate_mode") or identity.get("mode")
    identity_has_mode = identity_mode is not None
    identity_mode = _LEGACY_SUBSTRATE_MODE_ALIASES.get(identity_mode, identity_mode)
    legacy_packet = packet_mode is None
    if identity_mode is None:
        identity_mode = SUBSTRATE_COMMITTED_REF if packet.get("changed_ref") else SUBSTRATE_WORKING_TREE
    if packet_mode is None:
        packet_mode = identity_mode
    return packet_mode, identity_mode, identity_has_mode, legacy_packet


def verify_packet_binding(
    *,
    repo_root: Path,
    packet_path: str,
    packet_sha256: str,
    identity_sha256: str,
    expected_kind: str,
    check_current: bool = True,
) -> tuple[bool, str]:
    candidate, path_error = _canonical_packet_path(repo_root, packet_path)
    if path_error is not None or candidate is None:
        return False, path_error or "reviewed packet path is invalid"
    if not candidate.is_file():
        return False, f"reviewed packet does not exist: {packet_path}"
    packet_bytes = candidate.read_bytes()
    if not _SHA256_RE.fullmatch(str(packet_sha256)):
        return False, "packet sha256 is null or invalid"
    if _sha256(packet_bytes) != packet_sha256:
        return False, "reviewed packet bytes are stale or tampered"
    try:
        packet = json.loads(packet_bytes)
    except json.JSONDecodeError:
        return False, "reviewed packet is not valid JSON"
    if packet.get("kind") != expected_kind:
        return False, "reviewed packet has the wrong kind"
    identity = packet.get("reviewed_input_identity")
    if not isinstance(identity, dict):
        return False, "reviewed packet has no reviewed input identity"
    if identity.get("identity_sha256") != identity_sha256:
        return False, "artifact identity does not match the reviewed packet"
    if not _SHA256_RE.fullmatch(str(identity_sha256)):
        return False, "identity sha256 is null or invalid"
    packet_mode, identity_mode, identity_has_mode, legacy_packet = _reconcile_substrate_modes(
        packet, identity
    )
    if packet_mode not in SUBSTRATE_MODES or identity_mode != packet_mode:
        return False, "packet and reviewed input identity substrate modes do not match"
    if packet.get("changed_ref") != identity.get("changed_ref"):
        return False, "packet and reviewed input identity changed_ref values do not match"
    if check_current and identity_has_mode:
        return verify_reviewed_input_identity(repo_root, identity)
    # Zero declared paths is refused even in integrity-only mode. `--all` turns
    # `check_current` off for a real reason -- a corpus sweep re-reads historical
    # bindings that are stale BY DESIGN -- but that switch was taking an
    # unrelated rule down with it. "Covers zero paths" is not a currency
    # question: an empty path set digests to the same constant in every repo
    # forever, so it is vacuous at capture time and stays vacuous, and the sweep
    # registered as the `critique-artifacts` surface command could never catch
    # one. A correctly-disabled check silently disabling a second, independent
    # check is the same intersection shape this module keeps producing.
    declared = identity.get("reviewed_paths")
    if not isinstance(declared, list) or not declared:
        return False, "declared reviewed inputs cover zero paths"
    return True, "legacy-packet-integrity-only" if legacy_packet else "packet-integrity-only"
def verify_artifact_binding(
    artifact_path: Path,
    fields: dict[str, str],
    *,
    expected_kind: str,
    check_current: bool = True,
    repo_root: Path | None = None,
) -> tuple[bool, str]:
    resolved_root = repo_root.resolve() if repo_root is not None else None
    if resolved_root is None:
        # Prefer the known artifact layout before scanning ancestors. A nested
        # test checkout can live below an unrelated `.git` directory (for
        # example a shared temp root); selecting that first makes a valid
        # packet look like a wrong-path/missing-file failure.
        if len(artifact_path.resolve().parents) >= 3:
            layout_root = artifact_path.resolve().parents[2]
            if (layout_root / fields.get("packet path", "")).is_file():
                resolved_root = layout_root
        if resolved_root is None:
            resolved_root = next(
                (parent for parent in artifact_path.resolve().parents if (parent / ".git").exists()),
                None,
            )
        # Artifacts produced under the canonical `charness-artifacts/<kind>/`
        # layout still need a deterministic root when a fixture has no `.git`
        # directory. Keep the layout fallback even when the packet is missing:
        # the caller should receive the typed missing-packet refusal, not a
        # misleading repository-root discovery failure.
        if resolved_root is None and len(artifact_path.resolve().parents) >= 3:
            resolved_root = artifact_path.resolve().parents[2]
    if resolved_root is None:
        return False, "cannot resolve repository root for reviewed input binding"
    return verify_packet_binding(
        repo_root=resolved_root,
        packet_path=fields["packet path"],
        packet_sha256=fields["packet sha256"],
        identity_sha256=fields["identity sha256"],
        expected_kind=expected_kind,
        check_current=check_current,
    )
def verify_declared_binding(
    artifact_path: Path,
    fields: dict[str, str],
    *,
    required: bool,
    required_fields: tuple[str, ...],
    expected_kind: str,
    check_current: bool = True,
    repo_root: Path | None = None,
) -> tuple[bool, str]:
    if not fields:
        if required:
            return False, f"packet-bound critique must declare fields {list(required_fields)}"
        return True, "not-declared"
    missing = [field for field in required_fields if not fields.get(field)]
    if missing:
        return False, f"reviewed input identity missing fields: {missing}"
    return verify_artifact_binding(
        artifact_path,
        fields,
        expected_kind=expected_kind,
        check_current=check_current,
        repo_root=repo_root,
    )
