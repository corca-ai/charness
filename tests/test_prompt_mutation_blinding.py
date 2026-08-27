from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

blinding = load_script_module(
    "check_prompt_mutation_blinding_under_test", ROOT / "scripts" / "check_prompt_mutation_blinding.py"
)


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


def test_scan_bundle_flags_history_and_ref_probes_from_trace(tmp_path: Path) -> None:
    bundle = tmp_path / "preserved" / "baseline__0"
    _write_jsonl(
        bundle / "trace-digest.jsonl",
        [
            {
                "step": 4,
                "track": "parent",
                "name": "Bash",
                "args": "git log --oneline -12 && git status --short --branch",
            }
        ],
    )

    report = blinding.scan_bundle(bundle)
    assert report["tainted"] is True
    assert report["probe_count"] == 1
    assert report["hits"][0]["source"] == "trace-digest"
    assert report["hits"][0]["risk"] == "identity_probe"
    assert "git log" in report["hits"][0]["command"]


def test_scan_bundle_flags_git_global_option_history_probe(tmp_path: Path) -> None:
    bundle = tmp_path / "preserved" / "baseline__0"
    _write_jsonl(
        bundle / "trace-digest.jsonl",
        [{"step": 1, "track": "parent", "name": "Bash", "args": "git --no-pager show HEAD:docs/index.md"}],
    )

    report = blinding.scan_bundle(bundle)

    assert report["tainted"] is True
    assert report["hits"][0]["risk"] == "identity_probe"
    assert report["hits"][0]["command"].startswith("git --no-pager show")


def test_scan_bundle_uses_stream_fallback_for_full_command_text(tmp_path: Path) -> None:
    bundle = tmp_path / "preserved" / "step7_slim__0"
    _write_jsonl(
        bundle / "trace-digest.jsonl",
        [
            {
                "step": 19,
                "track": "sub",
                "name": "Bash",
                "args": "git show HEAD...",
            }
        ],
    )
    _write_jsonl(
        bundle / "stream.jsonl",
        [
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "t1",
                            "name": "Bash",
                            "input": {"command": "git show HEAD~1:docs/index.md"},
                        }
                    ],
                },
            }
        ],
    )

    report = blinding.scan_bundle(bundle)
    assert report["tainted"] is True
    assert any(hit["source"] == "stream.jsonl" for hit in report["hits"])
    assert any("git show HEAD~1" in hit["command"] for hit in report["hits"])


def test_scan_ab_dir_summarizes_tainted_bundles_and_cli_prints_json(tmp_path: Path, capsys) -> None:
    ab_dir = tmp_path / "ab"
    (ab_dir / "preserved").mkdir(parents=True)
    (ab_dir / "results.json").write_text(
        json.dumps(
            {
                "runs": [
                    {"arm": "baseline", "run": 0},
                    {"arm": "m1", "run": 0},
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_jsonl(
        ab_dir / "preserved" / "baseline__0" / "trace-digest.jsonl",
        [{"step": 1, "track": "parent", "name": "Bash", "args": "git rev-parse HEAD"}],
    )
    _write_jsonl(
        ab_dir / "preserved" / "m1__0" / "trace-digest.jsonl",
        [{"step": 1, "track": "parent", "name": "Bash", "args": "echo clean"}],
    )

    report = blinding.scan_ab_dir(ab_dir)
    assert report["summary"]["runs"] == 2
    assert report["summary"]["tainted_runs"] == 1
    assert report["summary"]["tainted_bundles"] == [str(ab_dir / "preserved" / "baseline__0")]

    rc = blinding.main(["--ab-dir", str(ab_dir)])
    assert rc == 0
    printed = yaml.safe_load(capsys.readouterr().out)
    assert printed["summary"]["tainted_runs"] == 1
