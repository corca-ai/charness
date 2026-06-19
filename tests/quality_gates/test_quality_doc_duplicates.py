from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_doc_duplicates.py"

# Markdown family the fake nose reports. members carry path#heading (the signature
# basis); witness line ranges are deliberately volatile so the baseline test also
# proves the signature is line-number stable.
_FAKE_FAMILY = {
    "tier": "near-high",
    "score": 0.95,
    "files": 2,
    "removable": 12,
    "commonness": 0.1,
    "exact": False,
    "template": False,
    "members": [
        {"path": "./docs/alpha.md", "heading": "Shared", "kind": "section", "start_line": 1, "end_line": 6},
        {"path": "./docs/beta.md", "heading": "Shared", "kind": "section", "start_line": 9, "end_line": 14},
    ],
    "witness": {
        "a_path": "./docs/alpha.md", "a_start": 1, "a_end": 6,
        "b_path": "./docs/beta.md", "b_start": 9, "b_end": 14, "matched_lines": 6,
    },
}


def _write_fake_nose(path: Path, *, version: str) -> None:
    family_json = json.dumps(_FAKE_FAMILY)
    path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "args = sys.argv[1:]",
                "if '--version' in args:",
                f"    print('nose {version}'); sys.exit(0)",
                f"fam = json.loads(r'''{family_json}''')",
                "print(json.dumps({'markdown': [fam], 'schema_version': 2, 'summary': {}}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _run(repo: Path, nose_bin: str | None, *extra: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ}
    if nose_bin is None:
        # Simulate a host with no nose at all: empty PATH + cleared override.
        env["PATH"] = str(repo / "empty-bin")
        env["NOSE_BIN"] = ""
    else:
        # Keep the real PATH so the fake nose's python3 shebang resolves; the
        # NOSE_BIN override still pins discovery to the fake, not the real binary.
        env["NOSE_BIN"] = nose_bin
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json", *extra],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_doc_dup_missing_nose_is_advisory_but_require_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    advisory = _run(repo, None)
    assert advisory.returncode == 0, advisory.stderr
    assert json.loads(advisory.stdout)["status"] == "missing"

    required = _run(repo, None, "--require-nose")
    assert required.returncode == 1
    assert json.loads(required.stdout)["status"] == "missing"


def test_doc_dup_version_too_old_blocks_under_require(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    fake = repo / "nose-old"
    _write_fake_nose(fake, version="0.10.0")

    advisory = _run(repo, str(fake))
    assert advisory.returncode == 0, advisory.stderr
    assert json.loads(advisory.stdout)["status"] == "version-too-old"

    required = _run(repo, str(fake), "--require-nose")
    assert required.returncode == 1


def test_doc_dup_reports_new_family_then_baseline_filters_it(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    fake = repo / "nose-cur"
    _write_fake_nose(fake, version="0.13.0")

    first = _run(repo, str(fake))
    assert first.returncode == 0, first.stderr
    payload = json.loads(first.stdout)
    assert payload["status"] == "ok"
    assert payload["total_family_count"] == 1
    assert payload["family_count"] == 1  # no baseline yet -> reported as new
    assert payload["families"][0]["tier"] == "near-high"

    written = _run(repo, str(fake), "--write-baseline")
    assert written.returncode == 0, written.stderr
    assert (repo / "charness-artifacts" / "quality" / "doc-nose-baseline.json").is_file()

    after = _run(repo, str(fake))
    payload_after = json.loads(after.stdout)
    assert payload_after["total_family_count"] == 1
    assert payload_after["family_count"] == 0  # accepted by baseline (drift posture)
    assert payload_after["accepted_count"] == 1
