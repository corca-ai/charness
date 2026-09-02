"""Quality-adapter scope for critique artifact consumers."""

from __future__ import annotations

import re
from pathlib import Path

from runtime_bootstrap import import_repo_module

_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _artifact_validator.ValidationError
_critique_adapter = import_repo_module(__file__, "scripts.review.critique_adapter_lib")
load_critique_adapter = _critique_adapter.load_adapter
_quality_adapter = import_repo_module(__file__, "scripts.adapters.quality_adapter_lib")
load_quality_adapter = _quality_adapter.load_quality_adapter
_quality_universes = import_repo_module(__file__, "scripts.adapters.quality_universes_lib")
_critique_paths = import_repo_module(__file__, "scripts.review.critique_artifact_paths")
_prepare_packet = import_repo_module(__file__, "scripts.gates_support.prepare_packet_markdown_kind")
file_is_prepare_packet_markdown_kind = _prepare_packet.file_is_prepare_packet_markdown_kind
CRITIQUE_ARTIFACT_PREFIX = _critique_paths.CRITIQUE_ARTIFACT_PREFIX
STRUCTURED_FINDINGS_HEADING = import_repo_module(
    __file__, "scripts.review.critique_structured_findings"
).STRUCTURED_FINDINGS_HEADING
DEFAULT_ARTIFACT_ROOTS = _quality_universes.DEFAULT_ARTIFACT_ROOTS
matching_files = _quality_universes.matching_files
refuse_if_declared_and_empty = _quality_universes.refuse_if_declared_and_empty
resolve_universe = _quality_universes.resolve_universe
CRITIQUE_PREPARE_PACKET_KIND = "charness.critique_prepare_packet"
CRITIQUE_PREPARE_PACKET_TITLE_RE = re.compile(r"^# Critique Prepare Packet(?:\s+—\s+\S.*)?$")


def default_root(repo_root: Path) -> str:
    data = load_critique_adapter(repo_root).get("data") or {}
    output_dir = data.get("output_dir")
    return (
        output_dir
        if isinstance(output_dir, str) and output_dir
        else DEFAULT_ARTIFACT_ROOTS["critique"]
    )


def prefix(repo_root: Path) -> str:
    return f"{default_root(repo_root).rstrip('/')}/"


def resolve_scope(repo_root: Path):
    universe = resolve_universe(
        load_quality_adapter(repo_root),
        "artifact_roots.critique",
        default=default_root(repo_root),
    )
    files = [path for path in matching_files(repo_root, universe) if path.suffix.lower() == ".md"]
    refusal = refuse_if_declared_and_empty(universe, files, "validate-critique-artifacts")
    if refusal:
        raise ValidationError(refusal)
    return universe, files


def candidate_paths(repo_root: Path, paths: list[str], *, all_artifacts: bool) -> list[Path]:
    universe_files = None
    if all_artifacts:
        _universe, universe_files = resolve_scope(repo_root)
        if not universe_files:
            print(
                "Discovered empty critique artifact universe: no Markdown artifacts "
                "matched the configured scope."
            )
    return _critique_paths.candidate_paths(
        repo_root,
        paths,
        all_artifacts=all_artifacts,
        artifact_prefix=prefix(repo_root),
        universe_files=universe_files,
        packet_checker=lambda path: _prepare_packet.file_is_prepare_packet_markdown_kind(
            path,
            expected_kind=CRITIQUE_PREPARE_PACKET_KIND,
            expected_title_re=CRITIQUE_PREPARE_PACKET_TITLE_RE,
        ),
    )
