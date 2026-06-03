"""Self-tests for the test DSL (tests/dsl.py).

These exercise every public surface of ``Repo``/``Result`` directly against a
throwaway script, so the DSL is proven independently of any real entrypoint and
every method has at least one caller.
"""

from __future__ import annotations

from pathlib import Path

from tests.dsl import Repo, run_at, run_raw

# A tiny entrypoint: finds --repo-root, writes a JSON file into the repo, echoes
# JSON on stdout, and fails with a marker when asked. Stands in for scripts/*.py.
PROBE = "\n".join(
    [
        "import json, pathlib, sys",
        "i = sys.argv.index('--repo-root')",
        "repo = pathlib.Path(sys.argv[i + 1])",
        "(repo / 'out.json').write_text(json.dumps({'wrote': True}), encoding='utf-8')",
        "if '--boom' in sys.argv:",
        "    sys.stderr.write('boom marker\\n')",
        "    raise SystemExit(3)",
        "print(json.dumps({'ok': True}))",
        "",
    ]
)


def _probe(tmp_path: Path) -> str:
    script = tmp_path / "probe.py"
    script.write_text(PROBE, encoding="utf-8")
    return str(script)


def test_repo_is_lazy_until_build(tmp_path: Path) -> None:
    calls: list[int] = []

    def thunk() -> str:
        calls.append(1)
        return "lazy-body"

    spec = Repo().file("lazy.txt", thunk).adapter("demo", {"k": "v", "items": []})
    assert calls == []  # composing the spec evaluates nothing

    repo = spec.build(tmp_path)
    assert calls == [1]  # build evaluates each thunk exactly once
    assert (repo / "lazy.txt").read_text(encoding="utf-8") == "lazy-body"
    adapter = (repo / ".agents" / "demo-adapter.yaml").read_text(encoding="utf-8")
    assert "k: v" in adapter
    assert "items: []" in adapter


def test_files_and_merge_compose(tmp_path: Path) -> None:
    base = Repo().files({"a.txt": "a", "nested/b.txt": "b"})
    merged = base.merge(Repo().file("a.txt", "override"))

    repo = merged.build(tmp_path, name="merged")
    assert (repo / "nested" / "b.txt").read_text(encoding="utf-8") == "b"
    assert (repo / "a.txt").read_text(encoding="utf-8") == "override"  # later entry wins


def test_run_injects_repo_root_and_reads_back(tmp_path: Path) -> None:
    res = Repo().file("seed.txt", "x").run(tmp_path, _probe(tmp_path)).ok()
    assert res.json == {"ok": True}
    assert res.stdout_has("ok")
    assert res.file_json("out.json") == {"wrote": True}
    assert res.file_text("seed.txt") == "x"


def test_failed_and_stderr_has(tmp_path: Path) -> None:
    repo = Repo().build(tmp_path, name="fail")
    run_at(repo, _probe(tmp_path), "--boom").failed(3).stderr_has("boom marker")


def test_run_raw_skips_injection(tmp_path: Path) -> None:
    repo = Repo().build(tmp_path, name="raw")
    # No --repo-root is injected; pass it ourselves to satisfy the probe.
    run_raw(repo, _probe(tmp_path), "--repo-root", str(repo)).ok().stdout_has("ok")
