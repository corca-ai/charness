"""The public-release narrative audit gate at the publish boundary.

One concept: everything that reads a release NARRATIVE — the durable audit
artifact and the release notes — and refuses publish when what it says is not
supported. Split out of `publish_release_cli.py` (which had reached its length
cap) because these three entrypoints share one question, distinct from the CLI's
job of wiring a run together:

- `run_narrative_audit` — the durable artifact's headings and its five-entry
  release state ledger;
- `run_notes_file_preflight` — mutable source-tree pointers in a notes FILE,
  before publish;
- `audit_notes_text` — the same pointer rule over notes TEXT, so the PUBLISHED
  body can be audited after `--generate-notes`, which composes the notes at
  creation time and leaves no file to inspect beforehand.

The pre-publish pair raise `SystemExit`; the post-publish reader does not, and
must not — the release already exists by then, so its finding is an advisory.
"""
from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_audit_narrative = SKILL_RUNTIME.load_local_skill_module(__file__, "audit_public_release_narrative")

build_narrative_audit_payload = _audit_narrative.build_payload
audit_notes_text = _audit_narrative.audit_notes_text
audit_notes_file = _audit_narrative.audit_notes_file


def run_narrative_audit(
    repo_root: Path,
    *,
    target_tag: str,
    notes_file: Path | None = None,
) -> None:
    audit_payload = build_narrative_audit_payload(
        repo_root,
        target_tag=target_tag,
        notes_file=notes_file,
    )
    if audit_payload["status"] == "blocked":
        raise SystemExit(
            "public release narrative audit blocked publish:\n"
            + "\n".join(f"- {blocker}" for blocker in audit_payload["blockers"])
        )


def run_notes_file_preflight(repo_root: Path, *, target_tag: str, notes_file: Path | None) -> None:
    if notes_file is None:
        return
    notes_blockers = audit_notes_file(notes_file, target_tag=target_tag)
    if notes_blockers:
        raise SystemExit(
            "public release notes preflight blocked publish:\n"
            + "\n".join(f"- {blocker}" for blocker in notes_blockers)
        )
