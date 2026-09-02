from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import os
import sys
import textwrap
from pathlib import Path

import yaml

from tests.quality_gates.repo_shapes import install_committed_repo

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "run_dead_code_advisory.py"
EVIDENCE_SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "dynamic_entrypoint_evidence.py"


def _run_dead_code_advisory_stdout(monkeypatch, bin_dir: Path, *args: str) -> str:
    spec = importlib.util.spec_from_file_location("run_dead_code_advisory_cli_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    buffer = io.StringIO()
    monkeypatch.setattr(sys, "argv", ["run_dead_code_advisory.py", *args])
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ.get('PATH', '')}")
    with contextlib.redirect_stdout(buffer):
        assert module.main() == 0
    return buffer.getvalue()


def _run_dead_code_advisory(monkeypatch, bin_dir: Path, *args: str) -> dict:
    return yaml.safe_load(_run_dead_code_advisory_stdout(monkeypatch, bin_dir, *args))


def _seed_fake_vulture(bin_dir: Path, *, sweep_finding: str | None) -> None:
    """Write a fake `vulture` that emits ``sweep_finding`` (exit 3) at confidence
    <= 60 and is clean (exit 0) otherwise, or is always clean when ``sweep_finding``
    is None."""
    lines = [
        "#!/usr/bin/env python3",
        "import sys",
        "confidence = int(sys.argv[sys.argv.index('--min-confidence') + 1])",
    ]
    if sweep_finding is not None:
        lines += ["if confidence <= 60:", f"    print({sweep_finding!r})", "    raise SystemExit(3)"]
    lines.append("raise SystemExit(0)")
    fake = bin_dir / "vulture"
    fake.write_text("\n".join(lines) + "\n", encoding="utf-8")
    fake.chmod(0o755)


def test_dead_code_advisory_reports_primary_and_sweep(tmp_path: Path, monkeypatch) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_vulture = bin_dir / "vulture"
    fake_vulture.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            confidence = int(sys.argv[sys.argv.index("--min-confidence") + 1])
            if confidence <= 60:
                print("scripts/example.py:3: unused function 'old_helper' (60% confidence, 2 lines)")
                raise SystemExit(3)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    fake_vulture.chmod(0o755)
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "scripts").mkdir()
    (repo / "scripts" / "example.py").write_text("def old_helper():\n    pass\n", encoding="utf-8")

    payload = _run_dead_code_advisory(monkeypatch, bin_dir, "--repo-root", str(repo), "--detail")

    assert payload["primary"]["status"] == "clean"
    assert payload["sweep"]["status"] == "findings"
    assert payload["sweep"]["findings"] == [
        {
            "path": "scripts/example.py",
            "line": 3,
            "message": "unused function 'old_helper'",
            "confidence": 60,
            "size": 2,
            "classification": "review_candidate",
        }
    ]


def test_dead_code_advisory_reports_not_applicable_for_typescript_only_repo(
    tmp_path: Path, monkeypatch
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _seed_fake_vulture(bin_dir, sweep_finding=None)
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            "src/app.ts": "export const app = true;\n",
            "package.json": '{"scripts":{"test":"vitest"}}\n',
        },
    )

    payload = _run_dead_code_advisory(
        monkeypatch, bin_dir, "--repo-root", str(repo), "--detail"
    )
    human = _run_dead_code_advisory_stdout(
        monkeypatch, bin_dir, "--repo-root", str(repo)
    )

    assert payload["applicability"] == "not-applicable-no-python-paths"
    assert payload["primary"]["status"] == "not-applicable"
    assert payload["sweep"]["status"] == "not-applicable"
    assert "NOT APPLICABLE:" in human
    assert "clean" not in human


def test_dead_code_advisory_reports_partial_for_mixed_language_repo(
    tmp_path: Path, monkeypatch
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _seed_fake_vulture(bin_dir, sweep_finding=None)
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            "scripts/helper.py": "KEEP = True\n",
            "src/app.ts": "export const app = true;\n",
        },
    )

    payload = _run_dead_code_advisory(
        monkeypatch, bin_dir, "--repo-root", str(repo), "--detail"
    )
    human = _run_dead_code_advisory_stdout(
        monkeypatch, bin_dir, "--repo-root", str(repo)
    )

    assert payload["applicability"] == "partial-python-only"
    assert payload["git_visible_python_file_count"] == 1
    assert payload["git_visible_non_python_source_count"] == 1
    assert payload["non_python_source_sample"] == ["src/app.ts"]
    assert human.splitlines()[0].startswith("PARTIAL:")
    assert "no repo-wide dead-code verdict" in human


def test_dead_code_advisory_explicit_path_scopes_non_python_census(
    tmp_path: Path, monkeypatch
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _seed_fake_vulture(bin_dir, sweep_finding=None)
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            "scripts/helper.py": "KEEP = True\n",
            "src/app.ts": "export const app = true;\n",
        },
    )

    payload = _run_dead_code_advisory(
        monkeypatch,
        bin_dir,
        "--repo-root",
        str(repo),
        "--path",
        "scripts",
        "--detail",
    )

    assert payload["applicability"] == "applicable-python-scope"
    assert payload["non_python_scope"] == "requested-roots"
    assert payload["git_visible_non_python_source_count"] == 0


def test_dead_code_advisory_summary_omits_full_command_and_findings(tmp_path: Path, monkeypatch) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_vulture = bin_dir / "vulture"
    fake_vulture.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            confidence = int(sys.argv[sys.argv.index("--min-confidence") + 1])
            if confidence <= 60:
                print("scripts/example.py:3: unused function 'old_helper' (60% confidence, 2 lines)")
                print("tests/conftest.py:1: unused variable 'pytest_plugins' (60% confidence, 1 line)")
                raise SystemExit(3)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    fake_vulture.chmod(0o755)
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "scripts").mkdir()
    (repo / "scripts" / "example.py").write_text("def old_helper():\n    pass\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "conftest.py").write_text("pytest_plugins = []\n", encoding="utf-8")

    payload = _run_dead_code_advisory(
        monkeypatch,
        bin_dir,
        "--repo-root",
        str(repo),
        "--summary",
    )

    assert payload["summary_note"].startswith("summary is triage output")
    assert "command" not in payload["sweep"]
    assert "findings" not in payload["sweep"]
    assert payload["sweep"]["finding_count"] == 2
    assert payload["sweep"]["classification_counts"] == {
        "likely_framework_convention": 1,
        "review_candidate": 1,
    }
    assert payload["sweep"]["review_candidate_sample"] == [
        {
            "path": "scripts/example.py",
            "line": 3,
            "message": "unused function 'old_helper'",
            "confidence": 60,
            "size": 2,
            "classification": "review_candidate",
        }
    ]


def test_dead_code_advisory_human_output_surfaces_advisory_for_review_candidate(
    tmp_path: Path, monkeypatch
) -> None:
    # A review_candidate finding must produce a first-line `ADVISORY:` marker so
    # run-quality.sh's attention filter surfaces the opt-in gate without --verbose.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _seed_fake_vulture(bin_dir, sweep_finding="scripts/example.py:3: unused function 'old_helper' (60% confidence, 2 lines)")
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "example.py").write_text("def old_helper():\n    pass\n", encoding="utf-8")

    output = _run_dead_code_advisory_stdout(monkeypatch, bin_dir, "--repo-root", str(repo))

    first_line = output.splitlines()[0]
    assert first_line.startswith("ADVISORY:")
    assert "review_candidate" in first_line
    assert "never blocks" in first_line


def test_dead_code_advisory_human_output_omits_advisory_when_no_review_candidate(
    tmp_path: Path, monkeypatch
) -> None:
    # A clean sweep must emit no ADVISORY line, so the gate stays silent when there
    # is nothing to triage.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _seed_fake_vulture(bin_dir, sweep_finding=None)
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "example.py").write_text("KEEP = True\n", encoding="utf-8")

    output = _run_dead_code_advisory_stdout(monkeypatch, bin_dir, "--repo-root", str(repo))

    assert "ADVISORY:" not in output


def test_dead_code_advisory_human_output_survives_missing_vulture(tmp_path: Path, monkeypatch) -> None:
    # Regression: with vulture absent, run_vulture() returns a "missing" dict that has
    # no `classification_counts` key. The human output path must NOT crash on it — an
    # opted-in advisory gate has to stay exit-0 even when the tool is not installed,
    # otherwise it turns the quality run red (a blocker the fresh-eye review caught).
    spec = importlib.util.spec_from_file_location("run_dead_code_advisory_missing_vulture", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module.shutil, "which", lambda _name: None)
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "example.py").write_text("KEEP = True\n", encoding="utf-8")
    buffer = io.StringIO()
    monkeypatch.setattr(sys, "argv", ["run_dead_code_advisory.py", "--repo-root", str(repo)])
    with contextlib.redirect_stdout(buffer):
        assert module.main() == 0
    out = buffer.getvalue()
    assert "missing" in out
    assert "ADVISORY:" not in out


def test_dead_code_advisory_scans_untracked_nonignored_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            ".gitignore": "ignored.py\n",
            "tracked.py": "TRACKED = True\n",
        },
    )
    (repo / "untracked.py").write_text("UNTRACKED = True\n", encoding="utf-8")
    (repo / "ignored.py").write_text("IGNORED = True\n", encoding="utf-8")

    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.git_visible_python_paths(repo, ("tracked.py", "untracked.py", "ignored.py")) == [
        "tracked.py",
        "untracked.py",
    ]


def test_dead_code_advisory_non_python_census_unreadable_population_is_empty(
    tmp_path: Path,
) -> None:
    spec = importlib.util.spec_from_file_location(
        "run_dead_code_advisory_non_python_unreadable", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.git_visible_non_python_sources(tmp_path) == []


def test_dead_code_advisory_skips_deleted_tracked_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(repo, {"tracked.py": "TRACKED = True\n"})
    (repo / "tracked.py").unlink()

    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.git_visible_python_paths(repo, ("tracked.py",)) == []


def test_dead_code_advisory_marks_pytest_conventions() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.parse_findings(
        "tests/conftest.py:1: unused variable 'pytest_plugins' (60% confidence, 1 line)\n"
    )

    assert findings[0]["classification"] == "likely_framework_convention"


def test_dead_code_advisory_marks_pytest_fixture_candidates() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.parse_findings("tests/conftest.py:12: unused function 'driver' (60% confidence, 5 lines)\n")

    assert findings[0]["classification"] == "likely_pytest_fixture"


def test_dead_code_advisory_recognizes_decorated_fixture_outside_conftest(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    repo = tmp_path / "repo"
    source = repo / "tests" / "test_example.py"
    source.parent.mkdir(parents=True)
    source.write_text(
        "import pytest\n\n@pytest.fixture(autouse=True)\ndef clear_state():\n    yield\n",
        encoding="utf-8",
    )

    findings = module.parse_findings(
        "tests/test_example.py:3: unused function 'clear_state' (60% confidence, 2 lines)\n"
        "tests/test_example.py:4: unused function 'clear_state' (60% confidence, 2 lines)\n",
        repo_root=repo,
    )

    assert [finding["classification"] for finding in findings] == [
        "likely_pytest_fixture",
        "likely_pytest_fixture",
    ]


def test_dead_code_advisory_does_not_treat_unrelated_fixture_decorator_as_pytest(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    repo = tmp_path / "repo"
    source = repo / "scripts" / "example.py"
    source.parent.mkdir(parents=True)
    source.write_text(
        "import local_framework\n\n@local_framework.fixture\ndef abandoned():\n    pass\n",
        encoding="utf-8",
    )

    findings = module.parse_findings(
        "scripts/example.py:3: unused function 'abandoned' (60% confidence, 2 lines)\n",
        repo_root=repo,
    )

    assert findings[0]["classification"] == "review_candidate"


def test_dead_code_advisory_recognizes_node_visitor_dispatch(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    repo = tmp_path / "repo"
    source = repo / "scripts" / "visitor.py"
    source.parent.mkdir(parents=True)
    source.write_text(
        "import ast\n\nclass Visitor(ast.NodeVisitor):\n    def visit_Name(self, node):\n        pass\n",
        encoding="utf-8",
    )

    findings = module.parse_findings(
        "scripts/visitor.py:4: unused method 'visit_Name' (60% confidence, 2 lines)\n",
        repo_root=repo,
    )

    assert findings[0]["classification"] == "likely_framework_convention"


def test_dead_code_advisory_does_not_treat_unrelated_node_visitor_as_ast(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    repo = tmp_path / "repo"
    source = repo / "scripts" / "visitor.py"
    source.parent.mkdir(parents=True)
    source.write_text(
        "class NodeVisitor:\n    pass\n\nclass Visitor(NodeVisitor):\n    def visit_Name(self, node):\n        pass\n",
        encoding="utf-8",
    )

    findings = module.parse_findings(
        "scripts/visitor.py:5: unused method 'visit_Name' (60% confidence, 2 lines)\n",
        repo_root=repo,
    )

    assert findings[0]["classification"] == "review_candidate"


def test_dead_code_advisory_recognizes_direct_import_aliases(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    repo = tmp_path / "repo"
    source = repo / "tests" / "test_aliases.py"
    source.parent.mkdir(parents=True)
    source.write_text(
        "from ast import NodeVisitor as VisitorBase\n"
        "from pytest import fixture as fixture_alias\n\n"
        "@fixture_alias\n"
        "def clear_state():\n    yield\n\n"
        "class Visitor(VisitorBase):\n"
        "    def visit_Name(self, node):\n        pass\n",
        encoding="utf-8",
    )

    findings = module.parse_findings(
        "tests/test_aliases.py:4: unused function 'clear_state' (60% confidence, 2 lines)\n"
        "tests/test_aliases.py:9: unused method 'visit_Name' (60% confidence, 2 lines)\n",
        repo_root=repo,
    )

    assert [finding["classification"] for finding in findings] == [
        "likely_pytest_fixture",
        "likely_framework_convention",
    ]


def test_dead_code_advisory_recognizes_runpy_registered_entrypoint(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    repo = tmp_path / "repo"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "loader.py").write_text("def load_sibling():\n    pass\n", encoding="utf-8")
    (scripts / "consumer.py").write_text(
        'import runpy\nfrom pathlib import Path\nrunpy.run_path(str(Path(__file__).with_name("loader.py")))["load_sibling"]()\n',
        encoding="utf-8",
    )

    finding = module.parse_findings(
        "scripts/loader.py:1: unused function 'load_sibling' (60% confidence, 2 lines)\n",
        repo_root=repo,
        scan_paths=["scripts/loader.py", "scripts/consumer.py"],
    )[0]

    assert finding["classification"] == "registered_dynamic_entrypoint"
    (scripts / "consumer.py").write_text(
        'import runpy\nrunpy.run_path("/other/loader.py")["load_sibling"]()\n',
        encoding="utf-8",
    )
    finding = module.parse_findings(
        "scripts/loader.py:1: unused function 'load_sibling' (60% confidence, 2 lines)\n",
        repo_root=repo,
        scan_paths=["scripts/loader.py", "scripts/consumer.py"],
    )[0]
    assert finding["classification"] == "review_candidate"
    (scripts / "consumer.py").write_text(
        'import runpy\nfrom pathlib import Path\nrunpy.run_path(str(Path(__file__).with_name("loader.py") / "not_target"))["load_sibling"]()\n',
        encoding="utf-8",
    )
    finding = module.parse_findings(
        "scripts/loader.py:1: unused function 'load_sibling' (60% confidence, 2 lines)\n",
        repo_root=repo,
        scan_paths=["scripts/loader.py", "scripts/consumer.py"],
    )[0]
    assert finding["classification"] == "review_candidate"
    (scripts / "consumer.py").write_text(
        'import runpy\nfrom pathlib import Path\nrunpy.run_path(str(Path(__file__).parent / "other" / "loader.py"))["load_sibling"]()\n',
        encoding="utf-8",
    )
    finding = module.parse_findings(
        "scripts/loader.py:1: unused function 'load_sibling' (60% confidence, 2 lines)\n",
        repo_root=repo,
        scan_paths=["scripts/loader.py", "scripts/consumer.py"],
    )[0]
    assert finding["classification"] == "review_candidate"


def test_dead_code_advisory_requires_registry_dispatch_for_entrypoint(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    repo = tmp_path / "repo"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "hook.py").write_text("def reconcile_hook():\n    pass\n", encoding="utf-8")
    registry = scripts / "registry.py"
    declaration = (
        'HOOK_INTENTS = (SiblingHookIntent(module="hook", reconcile_function="reconcile_hook"),)\n'
    )
    dispatch = (
        "def reconcile(intents=HOOK_INTENTS):\n"
        "    for intent in intents:\n"
        "        module = import_module(intent.module)\n"
        "        getattr(module, intent.reconcile_function)()\n"
    )
    registry.write_text(declaration + dispatch, encoding="utf-8")

    def classify() -> str:
        return module.parse_findings(
            "scripts/hook.py:1: unused function 'reconcile_hook' (60% confidence, 2 lines)\n",
            repo_root=repo,
            scan_paths=["scripts/hook.py", "scripts/registry.py"],
        )[0]["classification"]

    assert classify() == "registered_dynamic_entrypoint"
    registry.write_text(
        declaration
        + "def reconcile(intents=HOOK_INTENTS):\n"
        + "    for intent in intents:\n"
        + "        module = unrelated_loader(intent.module)\n"
        + "        getattr(module, intent.reconcile_function)()\n",
        encoding="utf-8",
    )
    assert classify() == "review_candidate"
    registry.write_text(
        declaration
        + "def reconcile(intents=HOOK_INTENTS):\n"
        + "    for intent in intents:\n"
        + "        module = import_module(intent.module)\n"
        + "        getattr(unrelated_module, intent.reconcile_function)()\n",
        encoding="utf-8",
    )
    assert classify() == "review_candidate"
    registry.write_text(
        declaration
        + "def reconcile():\n"
        + "    for intent in ():\n"
        + "        module = import_module(intent.module)\n"
        + "        getattr(module, intent.reconcile_function)()\n",
        encoding="utf-8",
    )
    assert classify() == "review_candidate"


def test_dead_code_advisory_does_not_exempt_contract_name_in_other_file() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.parse_findings(
        "scripts/reporter.py:3: unused variable 'ATTENTION_STATES' (60% confidence, 1 line)\n"
    )

    assert findings[0]["classification"] == "review_candidate"


def test_dead_code_advisory_marks_mock_and_test_protocol_noise() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.parse_findings(
        "\n".join(
            [
                "tests/test_driver.py:8: unused attribute 'side_effect' (60% confidence, 1 line)",
                "tests/test_driver.py:20: unused method 'connect' (60% confidence, 3 lines)",
            ]
        )
        + "\n"
    )

    assert [finding["classification"] for finding in findings] == [
        "likely_mock_protocol",
        "likely_test_protocol",
    ]
    assert module.classification_counts(findings) == {
        "likely_mock_protocol": 1,
        "likely_test_protocol": 1,
    }


def test_dead_code_advisory_marks_structured_output_fields() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.parse_findings(
        "scripts/evidence/agent_browser_runtime_guard.py:44: "
        "unused variable 'rss_kib' (60% confidence, 1 line)\n"
    )

    assert findings[0]["classification"] == "structured_output_field"


def test_dead_code_advisory_reclassifies_dataclass_annotated_fields(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    repo = tmp_path / "repo"
    source_path = repo / "scripts" / "payloads.py"
    source_path.parent.mkdir(parents=True)
    source_path.write_text(
        textwrap.dedent(
            """\
            from dataclasses import dataclass
            import dataclasses

            @dataclass
            class Payload:
                schema_value: str

            class Outer:
                @dataclasses.dataclass(frozen=True)
                class Nested:
                    nested_value: str

            class Ordinary:
                schema_value: str

            module_value: str
            """
        ),
        encoding="utf-8",
    )

    findings = module.parse_findings(
        "\n".join(
            [
                "scripts/payloads.py:6: unused variable 'schema_value' (60% confidence, 1 line)",
                "scripts/payloads.py:11: unused variable 'nested_value' (60% confidence, 1 line)",
                "scripts/payloads.py:14: unused variable 'schema_value' (60% confidence, 1 line)",
                "scripts/payloads.py:16: unused variable 'module_value' (60% confidence, 1 line)",
            ]
        ),
        repo_root=repo,
    )

    assert [finding["classification"] for finding in findings] == [
        "structured_output_field",
        "structured_output_field",
        "review_candidate",
        "review_candidate",
    ]


def test_dead_code_advisory_ignores_unreadable_dataclass_source(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory_unreadable_source", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    invalid_syntax = tmp_path / "invalid_syntax.py"
    invalid_syntax.write_text("def broken(:\n", encoding="utf-8")
    invalid_utf8 = tmp_path / "invalid_utf8.py"
    invalid_utf8.write_bytes(b"\xff")

    # Reads `source_role_locations`, which is where production reaches this data
    # (run_dead_code_advisory.py:163). Two pass-through aliases used to stand between this
    # assertion and that function, each with no caller but this one; repointing at the first
    # alias would only have moved the same defect down a module.
    #
    # Asserting the whole dict, not just `dataclass_fields`: the fail-closed branch returns all
    # three keys empty, so checking one of them lets a mutation that leaks into the other two
    # survive every input below.
    empty = {"dataclass_fields": set(), "pytest_fixtures": set(), "visitor_methods": set()}
    assert module._source_roles.source_role_locations(tmp_path / "missing.py") == empty
    assert module._source_roles.source_role_locations(invalid_syntax) == empty
    assert module._source_roles.source_role_locations(invalid_utf8) == empty


def test_dynamic_entrypoint_evidence_covers_fail_closed_ast_branches(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("dynamic_entrypoint_evidence", EVIDENCE_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module._caller_path(ast.parse("Path(__file__).resolve()", mode="eval").body)
    assert not module._caller_path(ast.parse("somewhere_else", mode="eval").body)

    tree = ast.parse(
        "REGISTRY = ()\n"
        "def positional(items=REGISTRY):\n    pass\n"
        "def keyword_only(*, items=REGISTRY):\n    pass\n"
        "for item in REGISTRY:\n    pass\n"
        "for item in unrelated:\n    pass\n"
    )
    aliases = module._function_default_registries(tree, {"REGISTRY"})
    assert {tuple(mapping.items()) for mapping in aliases.values()} == {
        (("items", "REGISTRY"),),
    }
    direct_loop, unrelated_loop = [node for node in ast.walk(tree) if isinstance(node, ast.For)]
    assert module._loop_registry(tree, direct_loop, {"REGISTRY"}, aliases) == "REGISTRY"
    assert module._loop_registry(tree, unrelated_loop, {"REGISTRY"}, aliases) is None

    lookup = ast.parse(
        'runpy.run_path(str(Path(__file__).with_name("loader.py")))["load_sibling"]()'
    )
    assert not module._runpy_lookup_matches(
        lookup,
        producer=tmp_path / "scripts" / "loader.py",
        symbol="load_sibling",
        consumer=tmp_path / "other" / "consumer.py",
    )


def test_dynamic_entrypoint_evidence_rejects_non_registry_rows(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("dynamic_entrypoint_evidence", EVIDENCE_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    tree = ast.parse(
        'REGISTRY = (Factory(module="hook", reconcile_function="dead"), '
        'SiblingHookIntent(module="other", reconcile_function="dead"))\n'
    )

    assert not module._registry_lookup_matches(tree, producer=tmp_path / "hook.py", symbol="dead")


def test_dynamic_entrypoint_evidence_skips_unreadable_irrelevant_and_invalid_consumers(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("dynamic_entrypoint_evidence", EVIDENCE_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "irrelevant.py").write_text("KEEP = True\n", encoding="utf-8")
    (scripts / "invalid.py").write_text("dead = (\n", encoding="utf-8")

    assert module.find_registered_dynamic_entrypoints(
        tmp_path,
        {("scripts/producer.py", "dead")},
        ["scripts/missing.py", "scripts/irrelevant.py", "scripts/invalid.py"],
    ) == set()
