from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_nose_clones.py"

# nose 0.13.3 removed `nose scan`; the advisory now runs `nose query <path> all
# top=N sort=K --format json` per scope root (one path per call) and merges the
# families, deduped by `id`. These end-to-end tests drive a fake `nose` that speaks
# the query contract. Multi-root scanning means the fake is invoked once per root
# (scripts / skills/public / skills/support), so families carry an `id` to dedupe.


def _make_nose(bin_dir: Path, body: str) -> None:
    """Write a fake `nose` that answers `--version` and runs the given `query` body.

    The advisory may stamp the version via `nose --version` when a report omits it,
    so the stub handles that call; `query` bodies emit a versioned JSON report.
    """
    bin_dir.mkdir(parents=True, exist_ok=True)
    nose = bin_dir / "nose"
    nose.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "args = sys.argv[1:]\n"
        "if args[:1] == ['--version']:\n"
        "    print('nose 0.13.3'); sys.exit(0)\n"
        + textwrap.dedent(body),
        encoding="utf-8",
    )
    nose.chmod(0o755)


def _run(script_args: list[str], bin_dir: Path | None) -> subprocess.CompletedProcess:
    if bin_dir is None:
        env = {**os.environ, "PATH": "/nonexistent-empty-bin", "NOSE_BIN": ""}
    else:
        env = {**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}", "NOSE_BIN": ""}
    return subprocess.run(
        [sys.executable, str(SCRIPT), *script_args],
        cwd=ROOT, check=True, capture_output=True, text=True, env=env,
    )


def test_nose_advisory_reports_missing_without_failing(tmp_path: Path) -> None:
    result = _run(["--repo-root", str(tmp_path)], bin_dir=None)
    assert result.returncode == 0
    assert "ADVISORY: nose missing" in result.stdout


def test_nose_advisory_missing_json_preserves_scope_filters(tmp_path: Path) -> None:
    result = _run(
        ["--repo-root", str(tmp_path), "--exclude", "**/resolve_adapter.py",
         "--ignore-file", "nose.ignore.json", "--json"],
        bin_dir=None,
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "missing"
    assert payload["excludes"] == ["**/resolve_adapter.py"]
    assert payload["ignore_file"] == "nose.ignore.json"
    assert payload["scope"] == {}
    assert payload["ranking"] == {}


def test_nose_advisory_uses_installed_binary(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    _make_nose(
        bin_dir,
        """
        assert args[0] == "query"
        assert args[args.index("--min-size") + 1] == "24"
        for legacy in ("--threshold", "--min-lines", "--min-tokens"):
            assert legacy not in args
        print(json.dumps({"schema_version": 3, "tool_version": "0.13.3", "families": [
            {"id": "fam1", "value": 10.0, "members": 2, "params": 1, "shared": 10,
             "locations": [
                {"file": "scripts/a.py", "start": 1, "end": 6, "name": "a", "lang": "python"},
                {"file": "scripts/b.py", "start": 1, "end": 6, "name": "b", "lang": "python"}
             ]}
        ]}))
        """,
    )
    payload = json.loads(_run(["--repo-root", str(tmp_path), "--json"], bin_dir).stdout)
    assert payload["status"] == "findings"
    assert payload["family_count"] == 1  # same id across 3 roots -> deduped
    assert payload["total_dup_lines"] == 12  # two 6-line spans, derived
    assert payload["tool_version"] == "0.13.3"
    assert payload["families"][0]["sample_locations"][0]["file"] == "scripts/a.py"
    interpretation = payload["interpretation"]
    assert set(interpretation) == {"measures", "proxy_for", "blind_spots", "interpretation_question"}
    assert all(interpretation[field].strip() for field in interpretation)


def test_nose_advisory_propagates_family_id(tmp_path: Path) -> None:
    # query's `id` is the stable per-family content hash; the dup-review ratchet
    # (item 5) keys the reviewed-fixable classification on it, normalized to
    # family_id, so the summary must carry it through.
    bin_dir = tmp_path / "bin"
    _make_nose(
        bin_dir,
        """
        assert args[0] == "query"
        print(json.dumps({"schema_version": 3, "tool_version": "0.13.3", "families": [
            {"id": "ff1fc93f63fabbc0", "members": 2, "locations": []}
        ]}))
        """,
    )
    payload = json.loads(_run(["--repo-root", str(tmp_path), "--json"], bin_dir).stdout)
    assert payload["status"] == "findings"
    assert payload["families"][0]["family_id"] == "ff1fc93f63fabbc0"


def test_nose_advisory_passes_exclude_filters_to_nose(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    _make_nose(
        bin_dir,
        """
        assert args[0] == "query"
        assert args[args.index("--min-size") + 1] == "24"
        assert args.count("--exclude") == 2
        excludes = [args[index + 1] for index, value in enumerate(args) if value == "--exclude"]
        assert excludes == ["**/resolve_adapter.py", "plugins/**"]
        assert args[args.index("--ignore-file") + 1] == "nose.ignore.json"
        for legacy in ("--threshold", "--min-lines", "--min-tokens"):
            assert legacy not in args
        print(json.dumps({"schema_version": 3, "tool_version": "0.13.3", "families": []}))
        """,
    )
    payload = json.loads(
        _run(
            ["--repo-root", str(tmp_path), "--exclude", "**/resolve_adapter.py",
             "--exclude", "plugins/**", "--ignore-file", "nose.ignore.json", "--json"],
            bin_dir,
        ).stdout
    )
    assert payload["status"] == "clean"
    assert payload["excludes"] == ["**/resolve_adapter.py", "plugins/**"]
    assert payload["ignore_file"] == "nose.ignore.json"


def test_nose_advisory_human_output_discloses_filtered_scope(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    _make_nose(
        bin_dir,
        """
        assert args[0] == "query"
        print(json.dumps({"schema_version": 3, "tool_version": "0.13.3", "families": []}))
        """,
    )
    result = _run(
        ["--repo-root", str(tmp_path), "--exclude", "**/resolve_adapter.py",
         "--ignore-file", "nose.ignore.json"],
        bin_dir,
    )
    assert "SCOPE: filtered scan" in result.stdout
    assert "excludes=**/resolve_adapter.py" in result.stdout
    assert "ignore_file=nose.ignore.json" in result.stdout
    assert "Excluded findings are not resolved" in result.stdout


def test_nose_advisory_human_output_discloses_top_n_ranking(tmp_path: Path) -> None:
    # nose 0.14.0 runs ONE `--root` multi-root query; the advisory discloses its
    # top-N ranking straight from that single response (no per-root aggregation).
    bin_dir = tmp_path / "bin"
    _make_nose(
        bin_dir,
        """
        assert args[0] == "query"
        assert "--root" in args  # multi-root invocation, not a positional single root
        fams = [{"id": "f%d" % i, "members": 2, "locations": []} for i in range(20)]
        summary = {"families": 526, "shown": 20}
        print(json.dumps({"schema_version": 4, "tool_version": "0.14.0", "families": fams, "summary": summary}))
        """,
    )
    result = _run(["--repo-root", str(tmp_path)], bin_dir)
    assert "RANKING: showing 20 of 526 ranked families" in result.stdout


def test_nose_advisory_emits_interpretation_self_declaration(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    _make_nose(
        bin_dir,
        """
        assert args[0] == "query"
        assert args[args.index("--min-size") + 1] == "24"
        print(json.dumps({"schema_version": 3, "tool_version": "0.13.3", "families": [
            {"id": "fam1", "members": 2, "params": 1, "shared": 10,
             "locations": [
                {"file": "scripts/a.py", "start": 1, "end": 10, "name": "a", "lang": "python"},
                {"file": "scripts/b.py", "start": 1, "end": 10, "name": "b", "lang": "python"}
             ]}
        ]}))
        """,
    )
    result = _run(["--repo-root", str(tmp_path)], bin_dir)
    assert result.returncode == 0
    assert "INTERPRETATION" in result.stdout
    assert "Consumer must answer first" in result.stdout
    assert "intentional" in result.stdout  # the load-bearing blind spot


def test_nose_advisory_id_baseline_filters_drift_without_nose_baseline_flag(tmp_path: Path) -> None:
    # The advisory keeps its own id-set drift baseline (nose's native --baseline is
    # unusable across multi-root query: it clobbers and keys on the churn-prone
    # cluster key), so accepted families are filtered in Python and `nose` is NOT
    # passed --baseline.
    baseline = tmp_path / "charness-artifacts" / "quality" / "nose-baseline.json"
    baseline.parent.mkdir(parents=True)
    baseline.write_text(
        json.dumps({"schemaVersion": "charness.quality.nose_baseline.v2", "code_family_ids": ["accepted1"]}),
        encoding="utf-8",
    )
    bin_dir = tmp_path / "bin"
    _make_nose(
        bin_dir,
        """
        assert args[0] == "query"
        assert "--baseline" not in args
        assert "--write-baseline" not in args
        print(json.dumps({"schema_version": 3, "tool_version": "0.13.3", "families": [
            {"id": "accepted1", "members": 2, "locations": []},
            {"id": "drift1", "members": 2, "locations": []}
        ]}))
        """,
    )
    payload = json.loads(_run(["--repo-root", str(tmp_path), "--json"], bin_dir).stdout)
    assert payload["family_count"] == 1
    assert payload["families"][0]["family_id"] == "drift1"
    assert payload["baseline"] == "charness-artifacts/quality/nose-baseline.json"


def test_nose_advisory_defaults_baseline_when_present(tmp_path: Path) -> None:
    # When the canonical id-set baseline exists, the standing advisory reads it by
    # default — no flag needed — so de-noising "sticks".
    baseline = tmp_path / "charness-artifacts" / "quality" / "nose-baseline.json"
    baseline.parent.mkdir(parents=True)
    baseline.write_text(
        json.dumps({"schemaVersion": "charness.quality.nose_baseline.v2", "code_family_ids": []}),
        encoding="utf-8",
    )
    bin_dir = tmp_path / "bin"
    _make_nose(
        bin_dir,
        """
        assert args[0] == "query"
        print(json.dumps({"schema_version": 3, "tool_version": "0.13.3", "families": []}))
        """,
    )
    payload = json.loads(_run(["--repo-root", str(tmp_path), "--json"], bin_dir).stdout)
    assert payload["baseline"] == "charness-artifacts/quality/nose-baseline.json"


def test_nose_advisory_write_baseline_writes_id_set(tmp_path: Path) -> None:
    # Migration: --write-baseline records EVERY scanned family_id as an id-set in
    # Python (no `nose --write-baseline`, which clobbers per single-path run).
    bin_dir = tmp_path / "bin"
    _make_nose(
        bin_dir,
        """
        assert args[0] == "query"
        assert "--write-baseline" not in args
        print(json.dumps({"schema_version": 3, "tool_version": "0.13.3", "families": [
            {"id": "fid2", "locations": []}, {"id": "fid1", "locations": []}
        ]}))
        """,
    )
    payload = json.loads(_run(["--repo-root", str(tmp_path), "--write-baseline", "--json"], bin_dir).stdout)
    assert payload["status"] == "baseline-written"
    assert payload["baseline"] == "charness-artifacts/quality/nose-baseline.json"
    assert payload["code_family_count"] == 2
    written = json.loads((tmp_path / "charness-artifacts" / "quality" / "nose-baseline.json").read_text(encoding="utf-8"))
    assert written["code_family_ids"] == ["fid1", "fid2"]


def test_nose_advisory_parses_query_schema_v3(tmp_path: Path) -> None:
    # nose 0.13.3 `query` emits schema_version 3 with `families` (under the `all`
    # term); identity `id`, `shared` (not `shared_lines`), location `start`/`end`,
    # no `dup_lines` (derived). Reading the wrong shape silently reports zero.
    bin_dir = tmp_path / "bin"
    _make_nose(
        bin_dir,
        """
        assert args[0] == "query"
        assert args[args.index("--min-size") + 1] == "24"
        for legacy in ("--threshold", "--min-lines", "--min-tokens"):
            assert legacy not in args
        print(json.dumps({"schema_version": 3, "tool_version": "0.13.3", "families": [
            {"id": "qfam", "value": 10.0, "members": 2, "params": 1, "shared": 10,
             "locations": [
                {"file": "scripts/a.py", "start": 1, "end": 6, "name": "a", "lang": "python"},
                {"file": "scripts/b.py", "start": 1, "end": 6, "name": "b", "lang": "python"}
             ]}
        ]}))
        """,
    )
    payload = json.loads(_run(["--repo-root", str(tmp_path), "--json"], bin_dir).stdout)
    assert payload["status"] == "findings"
    assert payload["family_count"] == 1
    assert payload["tool_version"] == "0.13.3"
    assert payload["total_dup_lines"] == 12
    assert payload["families"][0]["family_id"] == "qfam"
    assert payload["families"][0]["shared_lines"] == 10
    assert "paths" in payload["scope"]
    assert payload["families"][0]["sample_locations"][0]["file"] == "scripts/a.py"
