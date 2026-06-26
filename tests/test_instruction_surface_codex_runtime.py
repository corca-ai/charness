from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_instruction_surface_codex_session_mode_is_configurable() -> None:
    script = """
        import { codexArgs } from './scripts/agent-runtime/run-local-eval-test.mjs';
        const base = { workspace: '/tmp/work', sandbox: 'read-only', codexSessionMode: 'ephemeral' };
        const persistent = { ...base, codexSessionMode: 'persistent' };
        console.log(JSON.stringify({
          defaultArgs: codexArgs(base, '/tmp/schema.json', '/tmp/output.json'),
          persistentArgs: codexArgs(persistent, '/tmp/schema.json', '/tmp/output.json')
        }));
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "--ephemeral" in payload["defaultArgs"]
    assert "--ephemeral" not in payload["persistentArgs"]


def test_instruction_surface_codex_isolated_home_ignores_user_config() -> None:
    script = """
        import { codexArgs } from './scripts/agent-runtime/run-local-eval-test.mjs';
        const args = codexArgs(
          { workspace: '/tmp/work', sandbox: 'read-only', codexHomeMode: 'isolated' },
          '/tmp/schema.json',
          '/tmp/output.json'
        );
        console.log(JSON.stringify(args));
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "--ignore-user-config" in json.loads(result.stdout)


def test_instruction_surface_codex_home_mode_inherit_preserves_host_home() -> None:
    script = """
        import { codexEnvironment } from './scripts/agent-runtime/run-local-eval-test.mjs';
        process.env.CODEX_HOME = '/tmp/inherited-codex-home';
        const runtime = codexEnvironment(
          { repoRoot: '/tmp/repo', codexHomeMode: 'inherit', codexHome: null },
          '/tmp/output'
        );
        console.log(JSON.stringify({
          codeHome: runtime.env.CODEX_HOME,
          telemetry: runtime.telemetry
        }));
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["codeHome"] == "/tmp/inherited-codex-home"
    assert payload["telemetry"] == {
        "codex_home_mode": "inherit",
        "codex_home_isolated": False,
        "codex_home_path": "/tmp/inherited-codex-home",
    }


def test_instruction_surface_codex_home_override_uses_custom_home(tmp_path: Path) -> None:
    custom_home = tmp_path / "custom-codex-home"
    output_dir = tmp_path / "output"
    script = f"""
        import {{ codexEnvironment }} from './scripts/agent-runtime/run-local-eval-test.mjs';
        const runtime = codexEnvironment(
          {{ repoRoot: '/tmp/repo', codexHomeMode: 'isolated', codexHome: {json.dumps(str(custom_home))} }},
          {json.dumps(str(output_dir))}
        );
        console.log(JSON.stringify({{
          codeHome: runtime.env.CODEX_HOME,
          telemetry: runtime.telemetry
        }}));
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["codeHome"] == str(custom_home)
    assert payload["telemetry"] == {
        "codex_home_mode": "custom",
        "codex_home_isolated": True,
        "codex_home_path": str(custom_home),
    }
    assert custom_home.is_dir()


def test_instruction_surface_codex_isolated_home_inherits_only_auth(tmp_path: Path) -> None:
    source_home = tmp_path / "source-codex-home"
    source_home.mkdir()
    (source_home / "auth.json").write_text('{"token":"test"}\n', encoding="utf-8")
    (source_home / "config.toml").write_text("model = 'stale'\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    script = f"""
        import {{ existsSync, readFileSync }} from 'node:fs';
        import {{ join }} from 'node:path';
        import {{ codexEnvironment }} from './scripts/agent-runtime/run-local-eval-test.mjs';
        process.env.CODEX_HOME = {json.dumps(str(source_home))};
        const runtime = codexEnvironment(
          {{ repoRoot: '/tmp/repo', codexHomeMode: 'isolated', codexHome: null, codexAuthMode: 'inherit' }},
          {json.dumps(str(output_dir))}
        );
        const home = runtime.env.CODEX_HOME;
        console.log(JSON.stringify({{
          sourceHome: process.env.CODEX_HOME,
          codeHome: home,
          auth: readFileSync(join(home, 'auth.json'), 'utf-8'),
          hasConfig: existsSync(join(home, 'config.toml')),
          preflightBlocker: runtime.preflightBlocker
        }}));
        runtime.cleanup?.();
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["codeHome"] != payload["sourceHome"]
    assert payload["auth"] == '{"token":"test"}\n'
    assert payload["hasConfig"] is False
    assert payload["preflightBlocker"] is None


def test_instruction_surface_codex_isolated_home_reports_missing_auth(tmp_path: Path) -> None:
    source_home = tmp_path / "source-codex-home"
    source_home.mkdir()
    script = f"""
        import {{ codexEnvironment }} from './scripts/agent-runtime/run-local-eval-test.mjs';
        process.env.CODEX_HOME = {json.dumps(str(source_home))};
        delete process.env.OPENAI_API_KEY;
        const runtime = codexEnvironment(
          {{ repoRoot: '/tmp/repo', codexHomeMode: 'isolated', codexHome: null, codexAuthMode: 'inherit' }},
          '/tmp/output'
        );
        console.log(JSON.stringify(runtime.preflightBlocker));
        runtime.cleanup?.();
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["blockerKind"] == "runner_auth_missing"
    assert "could not inherit" in payload["summary"]


def test_instruction_surface_codex_auth_failure_is_classified() -> None:
    script = """
        import { codexFailureBlockerKind } from './scripts/agent-runtime/run-local-eval-test.mjs';
        console.log(codexFailureBlockerKind('401 Unauthorized: Missing bearer or basic authentication'));
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "runner_auth_missing"


def test_instruction_surface_codex_exec_isolates_codex_home_by_default(tmp_path: Path) -> None:
    stale_codex_home = tmp_path / "stale-codex-home"
    stale_skill = stale_codex_home / "plugins/cache/local/charness/0.5.21/skills/issue/SKILL.md"
    stale_skill.parent.mkdir(parents=True)
    stale_skill.write_text("# stale installed issue skill\n", encoding="utf-8")
    (stale_codex_home / "auth.json").write_text('{"token":"test"}\n', encoding="utf-8")

    workspace_path = tmp_path / "workspace"
    workspace_path.mkdir()
    cases_path = tmp_path / "cases.json"
    cases_path.write_text(
        json.dumps(
            {
                "schemaVersion": "cautilus.evaluation_cases.v1",
                "suiteId": "codex-home-isolation",
                "evaluations": [
                    {
                        "evaluationId": "repo-local-instruction-surface",
                        "prompt": "Route this request.",
                        "instructionSurface": {
                            "surfaceLabel": "repo-local",
                            "files": [
                                {
                                    "path": "AGENTS.md",
                                    "content": "# repo local instructions\n",
                                }
                            ],
                        },
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_codex = fake_bin / "codex"
    fake_codex.write_text(
        """#!/usr/bin/env python3
import json
import os
import sys

output_file = sys.argv[sys.argv.index("-o") + 1]
stale_home = os.environ["STALE_CODEX_HOME"]
codex_home = os.environ.get("CODEX_HOME", "")
loaded = (
    [os.path.join(stale_home, "plugins/cache/local/charness/0.5.21/skills/issue/SKILL.md")]
    if codex_home == stale_home
    else [os.path.join(os.getcwd(), "AGENTS.md")]
)
with open(output_file, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "observationStatus": "observed",
            "blockerKind": "",
            "summary": f"CODEX_HOME={codex_home}",
            "entryFile": os.path.join(os.getcwd(), "AGENTS.md"),
            "loadedInstructionFiles": loaded,
            "loadedSupportingFiles": [],
            "routingDecision": {
                "selectedSkill": "none",
                "bootstrapHelper": "none",
                "workSkill": "none",
                "selectedSupport": "none",
                "firstToolCall": "none",
                "reasonSummary": "fake codex",
            },
        },
        handle,
    )
""",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)

    output_path = tmp_path / "observed.json"
    artifact_dir = tmp_path / "artifacts"
    env = {
        **os.environ,
        "PATH": f"{fake_bin}:{os.environ.get('PATH', '')}",
        "CODEX_HOME": str(stale_codex_home),
        "STALE_CODEX_HOME": str(stale_codex_home),
    }
    result = subprocess.run(
        [
            "node",
            "scripts/agent-runtime/run-local-eval-test.mjs",
            "--repo-root",
            str(ROOT),
            "--workspace",
            str(workspace_path),
            "--cases-file",
            str(cases_path),
            "--output-file",
            str(output_path),
            "--artifact-dir",
            str(artifact_dir),
            "--backend",
            "codex_exec",
        ],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    packet = json.loads(output_path.read_text(encoding="utf-8"))
    evaluation = packet["evaluations"][0]
    assert evaluation["loadedInstructionFiles"] == ["AGENTS.md"]
    assert stale_skill.as_posix() not in json.dumps(evaluation, ensure_ascii=False)
    assert evaluation["telemetry"]["codex_home_mode"] == "isolated"
    assert evaluation["telemetry"]["codex_home_isolated"] is True
    assert evaluation["telemetry"]["codex_home_path"] != str(stale_codex_home)
