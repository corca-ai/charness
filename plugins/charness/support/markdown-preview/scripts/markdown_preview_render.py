from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
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
    try:
        completed = subprocess.run([backend, "--version"], check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or completed.stderr.strip() or None


def _git_head(repo_root: Path) -> str | None:
    git = shutil.which("git") or next(
        (str(candidate) for candidate in (Path("/usr/bin/git"), Path("/opt/homebrew/bin/git")) if candidate.is_file()),
        None,
    )
    if git is None:
        return None
    try:
        completed = subprocess.run(
            [git, "rev-parse", "HEAD"], cwd=repo_root, check=False, capture_output=True, text=True
        )
    except FileNotFoundError:
        return None
    return completed.stdout.strip() if completed.returncode == 0 else None


def _run_glow(path: Path, width: int, *, stdout_path: Path | None = None) -> subprocess.CompletedProcess[str]:
    stdout = subprocess.PIPE
    stdout_handle = None
    if stdout_path is not None:
        stdout_handle = stdout_path.open("w", encoding="utf-8")
        stdout = stdout_handle
    try:
        return subprocess.run(["glow", "-w", str(width), str(path)], check=False, stdout=stdout, stderr=subprocess.PIPE, text=True)
    finally:
        if stdout_handle is not None:
            stdout_handle.close()


def _render_with_glow(path: Path, width: int) -> tuple[str | None, str | None]:
    completed = subprocess.run(
        ["glow", "-w", str(width), str(path)], check=False, capture_output=True, text=True
    )
    source_non_empty = bool(path.read_text(encoding="utf-8").strip())
    if completed.returncode == 0 and (completed.stdout.strip() or not source_non_empty):
        return completed.stdout, None
    if completed.returncode == 0 and source_non_empty:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "glow-output.txt"
            retry = _run_glow(path, width, stdout_path=output_path)
            rendered = output_path.read_text(encoding="utf-8") if output_path.is_file() else ""
            if retry.returncode == 0 and rendered.strip():
                return rendered, None
            retry_error = retry.stderr.strip() or rendered.strip()
        return None, retry_error or "glow produced blank output for non-empty Markdown"
    error = completed.stderr.strip() or completed.stdout.strip() or "glow failed without output"
    return None, error


def check_backend(backend: str) -> dict[str, str | bool]:
    if backend != "glow":
        return {"available": False, "status": "backend-error", "reason": f"unsupported backend `{backend}`"}
    if shutil.which(backend) is None:
        return {"available": False, "status": "missing", "reason": f"{backend} not found on PATH"}
    with tempfile.TemporaryDirectory() as tmp_dir:
        sample = Path(tmp_dir) / "sample.md"
        sample.write_text("# Preview Check\n\nBody\n", encoding="utf-8")
        rendered, reason = _render_with_glow(sample, 80)
    if rendered is not None and rendered.strip():
        return {"available": True, "status": "healthy", "reason": ""}
    return {"available": True, "status": "backend-error", "reason": reason or "backend produced unusable output"}


def _fallback_text(path: Path, *, backend: str, reason: str, repo_root: Path, status: str) -> str:
    title = "MARKDOWN PREVIEW BACKEND ERROR" if status == "backend-error" else "MARKDOWN PREVIEW DEGRADED"
    return "\n".join(
        [
            title,
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


def _repo_relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def render_targets(repo_root: Path, config: PreviewConfig, targets: list[Path]) -> dict[str, Any]:
    artifact_dir = (repo_root / config.artifact_dir).resolve()
    backend_probe = check_backend(config.backend)
    backend_available = bool(backend_probe["available"])
    backend_status = str(backend_probe["status"])
    warnings: list[str] = []
    previews: list[dict[str, Any]] = []
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
            rendered, reason = (None, str(backend_probe["reason"]))
            if backend_status == "healthy":
                rendered, reason = _render_with_glow(target, width)
            if rendered is None:
                status = "degraded" if backend_status == "missing" else "backend-error"
                _write_artifact(
                    artifact_path,
                    _fallback_text(
                        target,
                        backend=config.backend,
                        reason=reason or "backend error",
                        repo_root=repo_root,
                        status=status,
                    ),
                )
                item["status"] = status
                item["reason"] = reason or "backend error"
                if status == "backend-error":
                    warnings.append(f"{relative} @ width {width}: {item['reason']}")
            else:
                _write_artifact(artifact_path, rendered)
                item["status"] = "rendered"
            previews.append(item)
    statuses = {str(item["status"]) for item in previews}
    if not targets:
        overall_status = "no-targets"
    elif statuses == {"rendered"}:
        overall_status = "success"
    elif statuses == {"degraded"}:
        overall_status = "degraded"
    elif statuses == {"backend-error"}:
        overall_status = "backend-error"
    else:
        overall_status = "partial"
    payload = {
        "status": overall_status,
        "repo": repo_root.name,
        "backend": config.backend,
        "backend_available": backend_available,
        "backend_status": backend_status,
        "backend_healthcheck": backend_probe,
        "backend_version": _backend_version(config.backend) if backend_available else None,
        "config_path": config.config_path,
        "artifact_dir": _repo_relative(repo_root, artifact_dir),
        "git_head": _git_head(repo_root),
        "widths": list(config.widths),
        "target_count": len(targets),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "previews": previews,
        "warnings": warnings,
    }
    _write_artifact(artifact_dir / "manifest.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return payload
