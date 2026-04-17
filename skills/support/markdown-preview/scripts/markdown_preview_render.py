from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_markdown_preview_lib() -> Any:
    module_path = Path(__file__).resolve().with_name("markdown_preview_lib.py")
    spec = importlib.util.spec_from_file_location("markdown_preview_lib", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("markdown_preview_lib", module)
    spec.loader.exec_module(module)
    return module


_LIB = _load_markdown_preview_lib()
PreviewConfig = _LIB.PreviewConfig
artifact_stem = _LIB.artifact_stem


def _backend_version(backend: str) -> str | None:
    completed = subprocess.run([backend, "--version"], check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or completed.stderr.strip() or None


def _git_head(repo_root: Path) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, check=False, capture_output=True, text=True
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def _render_with_glow(path: Path, width: int) -> tuple[str | None, str | None]:
    completed = subprocess.run(
        ["glow", "-w", str(width), str(path)], check=False, capture_output=True, text=True
    )
    if completed.returncode == 0:
        return completed.stdout, None
    error = completed.stderr.strip() or completed.stdout.strip() or "glow failed without output"
    return None, error


def _degraded_text(path: Path, *, backend: str, reason: str, repo_root: Path) -> str:
    return "\n".join(
        [
            "MARKDOWN PREVIEW DEGRADED",
            f"backend: {backend}",
            f"reason: {reason}",
            f"source: {path.relative_to(repo_root).as_posix()}",
            "",
            "The text below is raw Markdown source copied only as a reference aid.",
            "It is not equivalent to a rendered readability review.",
            "",
            "---",
            "",
            path.read_text(encoding="utf-8"),
            "",
        ]
    )


def _write_artifact(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def render_targets(repo_root: Path, config: PreviewConfig, targets: list[Path]) -> dict[str, Any]:
    artifact_dir = (repo_root / config.artifact_dir).resolve()
    backend_available = shutil.which(config.backend) is not None if config.backend == "glow" else False
    warnings: list[str] = []
    previews: list[dict[str, Any]] = []
    overall_status = "success"
    for target in targets:
        relative = target.relative_to(repo_root).as_posix()
        source_sha256 = hashlib.sha256(target.read_bytes()).hexdigest()
        for width in config.widths:
            artifact_path = artifact_dir / f"{artifact_stem(repo_root, target)}.w{width}.txt"
            item: dict[str, Any] = {
                "source_path": relative,
                "width": width,
                "artifact_path": str(artifact_path.relative_to(repo_root)),
                "backend": config.backend,
                "source_sha256": source_sha256,
            }
            rendered, reason = (None, f"{config.backend} not found on PATH")
            if backend_available:
                rendered, reason = _render_with_glow(target, width)
            if rendered is None:
                _write_artifact(
                    artifact_path,
                    _degraded_text(
                        target,
                        backend=config.backend,
                        reason=reason or "backend error",
                        repo_root=repo_root,
                    ),
                )
                item["status"] = "degraded" if not backend_available else "backend-error"
                item["reason"] = reason or "backend error"
                overall_status = "degraded" if not backend_available and overall_status == "success" else "partial"
                if backend_available:
                    warnings.append(f"{relative} @ width {width}: {item['reason']}")
            else:
                _write_artifact(artifact_path, rendered)
                item["status"] = "rendered"
            previews.append(item)
    payload = {
        "status": overall_status if targets else "no-targets",
        "repo_root": str(repo_root),
        "backend": config.backend,
        "backend_available": backend_available,
        "backend_version": _backend_version(config.backend) if backend_available else None,
        "config_path": config.config_path,
        "artifact_dir": str(artifact_dir.relative_to(repo_root)),
        "git_head": _git_head(repo_root),
        "widths": list(config.widths),
        "target_count": len(targets),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "previews": previews,
        "warnings": warnings,
    }
    _write_artifact(artifact_dir / "manifest.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return payload
