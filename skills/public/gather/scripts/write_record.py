#!/usr/bin/env python3

"""Symlink-safe writer for gather dated records and the current pointer.

Resolves the gather adapter, writes a fresh dated canonical record under
`<output_dir>/<YYYY-MM-DD>-<slug>.md`, then safely refreshes the current
pointer (`latest.md`) via the lstat-aware helper in `gather_writer_lib`
so a writer that hits a symlinked pointer never silently follows the
link and clobbers an unrelated dated record. The refresh is
unlink-then-write rather than strictly POSIX-atomic; gather's read-mostly
workload tolerates the small window.

Idempotent on the dated path: if a dated record with the same slug+date
already exists, the script refuses to overwrite. Use a different slug or
update the prior record manually with the same lstat-aware care.
"""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
# Command output is unconditionally YAML since the 2026-08-14 --json removal. These three
# sites used `json.dump(payload, sys.stdout, ...)`, a spelling the sweep's scanners did not
# match -- and `gather_public_url._run_json` reads this stdout with `yaml.safe_load`, which
# accepted the JSON silently. The mismatch was invisible precisely because JSON is YAML.
emit_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output").emit_yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gather_writer_lib as wlib  # noqa: E402
import resolve_adapter as gather_adapter  # noqa: E402

_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapters.adapter_version_verdict"
)


def _resolve_output_dir(repo_root: Path) -> Path:
    payload = gather_adapter.load_adapter(repo_root)
    # A version this reader cannot speak leaves `output_dir` at the shipped default, so
    # the dated record AND the `latest.md` pointer would be written under a directory
    # the repo never named -- the repo's real pointer left stale while a shadow one
    # appears elsewhere, reported as `status: updated`, exit 0. Refuse instead: this
    # writes a durable knowledge asset, and writing it to the wrong place is worse than
    # not writing it.
    #
    # ROUND 2 OF THE SLICE-5 REVIEW WIDENED THIS PREDICATE. It asked `version_refused`,
    # which is one door into that state; a parser refusal is the other, and reaches the
    # same `infer_defaults(...)` payload. Measured on the real CLI: `version: !!int 9`
    # beside a declared `output_dir: docs/gathered` wrote BOTH the dated record and
    # `latest.md` under `charness-artifacts/gather`, `status: updated`, exit 0 -- while
    # `version: 9` in the same repo refused. The narrow predicate was the escape.
    errors = payload.get("errors")
    if _version_verdict.declarations_unhonored(errors):
        raise wlib.WriteError(
            f"gather adapter {_version_verdict.unhonored_cause(errors)} "
            f"({'; '.join(errors or [])}); nothing it declares is honored, "
            "so `output_dir` would be the charness default rather than this repo's. "
            + _version_verdict.unhonored_remedy(errors, "gather-adapter.yaml")
        )
    data = payload.get("data") or {}
    output_dir = data.get("output_dir")
    if not isinstance(output_dir, str):
        raise wlib.WriteError("gather adapter did not declare output_dir")
    return (repo_root / output_dir).resolve()


def _read_content(path: Path | None) -> str:
    """The record body. Empty or whitespace-only content is REFUSED, not written.

    A gather record is a durable knowledge asset, and this helper writes two things:
    the dated record and the `latest.md` current pointer that other sessions read as
    "the gathered source". Empty stdin — a fetch that produced nothing, a pipe that
    failed, a `--content-file` of a truncated download — wrote a 0-byte record AND
    overwrote the pointer with 0 bytes, reporting `{"status": "updated",
    "wrote_record": true}` and exit 0. The destructive half is the pointer: a
    previously good asset is replaced by nothing, and the report says it worked.

    Refused HERE rather than at the write, so `--dry-run` (which reads content to
    report `content_bytes`) refuses on the same input the executing run would.
    """
    content = sys.stdin.read() if path is None else None
    if content is None:
        if not path.is_file():
            raise wlib.WriteError(f"--content-file {path} does not exist or is not a file")
        content = path.read_text(encoding="utf-8")
    if not content.strip():
        source = "stdin" if path is None else f"--content-file {path}"
        raise wlib.WriteError(
            f"refusing to write an empty gather record: {source} produced "
            f"{len(content.encode('utf-8'))} byte(s) of content, none of it non-whitespace. "
            "A 0-byte record would also overwrite the `latest.md` current pointer, replacing a "
            "real gathered asset with nothing while reporting success. Check that the fetch or "
            "pipe upstream of this command actually produced the source text."
        )
    return content


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="repo root where the gather record should be written")
    parser.add_argument("--slug", required=True, help="lowercase slug for the dated record")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (default: today UTC)")
    parser.add_argument(
        "--content-file",
        type=Path,
        default=None,
        help="path to the record content (defaults to stdin)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="write the dated record and refresh the pointer (otherwise dry-run)",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    root = args.repo_root.resolve()
    wlib.validate_slug(args.slug)
    date = args.date or wlib.today_iso()
    wlib.validate_date(date)
    output_dir = _resolve_output_dir(root)
    record_path = wlib.compute_record_path(output_dir, date, args.slug)
    payload: dict[str, Any] = {
        "repo_root": str(root),
        "slug": args.slug,
        "date": date,
        "output_dir": str(output_dir),
        "record_artifact_path": str(record_path),
        "current_pointer_path": str(output_dir / "latest.md"),
        "execute": args.execute,
        "would_write": True,
    }
    if record_path.exists():
        payload["status"] = "blocked"
        payload["reason"] = "dated record already exists; choose a different slug or date"
        emit_yaml(dict(sorted(payload.items())))
        return 1
    content = _read_content(args.content_file)
    if not args.execute:
        payload["status"] = "planned"
        payload["content_bytes"] = len(content.encode("utf-8"))
        emit_yaml(dict(sorted(payload.items())))
        return 0
    output_dir.mkdir(parents=True, exist_ok=True)
    record_path.write_text(content, encoding="utf-8")
    payload["wrote_record"] = True
    pointer_path = output_dir / "latest.md"
    refresh = wlib.refresh_current_pointer(
        pointer_path, record_path, output_dir, execute=True
    )
    payload["pointer_refresh"] = refresh
    payload["status"] = "updated" if refresh.get("status") in {"updated", "noop"} else "partial"
    emit_yaml(dict(sorted(payload.items())))
    return 0 if payload["status"] != "partial" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except wlib.WriteError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
