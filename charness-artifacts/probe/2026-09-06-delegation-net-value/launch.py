"""One-experiment transport and snapshots; no agent planning or recovery logic."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SEED = REPO / "evals/fixtures/consumer-journeys/spec-impl-alias/seed"
SEED_FILES = ("README.md", "src/__init__.py", "src/catalog.py", "tests/test_catalog.py")
MODELS = {"low": "gpt-5.6-luna", "high": "gpt-6-astra"}
INPUT_FILES = ("protocol.md", "initial-task.md", "revised-task.md", "start.md",
               "resume.md", "treatment.md", "oracle.py", "control_catalog.py",
               "controls.py", "launch.py", "launcher_controls.py")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(root):
    result = {}
    for path in sorted(root.rglob("*")):
        key = str(path.relative_to(root))
        if path.is_symlink():
            result[key] = {"kind": "symlink", "target": os.readlink(path)}
        elif path.is_file():
            result[key] = {"kind": "file", "sha256": digest(path),
                           "mode": path.stat().st_mode & 0o777}
    return result


def same_file(path, expected):
    return not path.is_symlink() and path.is_file() and digest(path) == digest(expected)


def protected_inventory(root):
    # Interpreter cache writes are execution overhead, not source implementation.
    return {name: value for name, value in manifest(root).items()
            if name.split("/", 1)[0] in {"src", "tests"}
            and "__pycache__" not in Path(name).parts and not name.endswith(".pyc")}


def escaping_symlinks(root):
    escapes = []
    for path in root.rglob("*"):
        if not path.is_symlink():
            continue
        try:
            path.resolve().relative_to(root.resolve())
        except (ValueError, RuntimeError):
            escapes.append(str(path.relative_to(root)))
    return sorted(escapes)


def phase_checks(work, phase, initial_inventory):
    task_source = HERE / ("initial-task.md" if phase == 1 else "revised-task.md")
    checks = {"baseline_tests_unchanged": same_file(work / "tests/test_catalog.py", SEED / "tests/test_catalog.py"),
              "task_channel_unchanged": same_file(work / ".task/current.md", task_source),
              "escaping_symlinks": escaping_symlinks(work)}
    if phase == 1:
        checks["source_and_test_inventory_unchanged"] = protected_inventory(work) == initial_inventory
    return checks


def inject_task(work, source):
    folder = work / ".task"
    target = folder / "current.md"
    if folder.is_symlink() or target.is_symlink():
        return False
    if folder.exists() and not folder.is_dir():
        return False
    if target.exists() and not target.is_file():
        return False
    folder.mkdir(exist_ok=True)
    shutil.copyfile(source, target)
    return True


def isolated_command(work, package):
    user_root = Path.home()
    codex_root = user_root / ".codex"
    command = ["bwrap", "--die-with-parent", "--unshare-pid", "--ro-bind", "/", "/",
               "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
               "--tmpfs", str(user_root / "codes"), "--tmpfs", str(user_root / ".cache"),
               "--tmpfs", str(codex_root), "--bind", str(work), "/tmp/work"]
    for name in ("auth.json", "models_cache.json"):
        source = codex_root / name
        if source.is_file():
            command += ["--ro-bind", str(source), str(source)]
    if package:
        command += ["--ro-bind", str(package), "/tmp/package"]
    return command + ["--chdir", "/tmp/work"]


def run_process(command, prompt, seconds, output):
    started = time.monotonic()
    with output.open("w") as stream:
        process = subprocess.Popen(command + [prompt], stdout=stream, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        timed_out = False
        try:
            code = process.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                code = process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
    return {"exit_code": code, "timeout": timed_out,
            "wall_seconds": round(time.monotonic() - started, 3)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("preflight", "cell", "freeze"))
    parser.add_argument("--tier", choices=MODELS, default="low")
    parser.add_argument("--root", type=Path, required=True, help="new absolute arm directory under /tmp")
    parser.add_argument("--package", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if root.parent != Path("/tmp") or root.exists():
        parser.error("root must be a new direct child of /tmp")
    package = args.package.resolve() if args.package else None
    if package and (not package.is_dir() or package.parent != Path("/tmp")):
        parser.error("package must be an exported directory directly under /tmp")
    frozen_inputs = {str((HERE / name).relative_to(REPO)): digest(HERE / name)
                     for name in INPUT_FILES}
    frozen_inputs.update({str((SEED / name).relative_to(REPO)): digest(SEED / name)
                          for name in SEED_FILES})
    for name in ("control-observations.json", "launcher-control-observations.json"):
        source = HERE / name
        if source.is_file():
            frozen_inputs[str(source.relative_to(REPO))] = digest(source)
        elif args.mode != "preflight":
            parser.error(f"required frozen control evidence is missing: {name}")
    root.mkdir()
    (root / "inputs.json").write_text(json.dumps(frozen_inputs, indent=2) + "\n")
    if args.mode == "freeze":
        return 0
    if args.mode == "cell":
        frozen = HERE / "frozen-inputs.json"
        if not frozen.is_file() or json.loads(frozen.read_text()) != frozen_inputs:
            parser.error("current inputs differ from the accepted frozen manifest")
        if package:
            candidate = HERE / "candidate-inputs.json"
            if not candidate.is_file():
                parser.error("candidate package identity has not been frozen")
            accepted = json.loads(candidate.read_text())
            if not accepted.get("revision") or accepted.get("manifest") != manifest(package):
                parser.error("candidate package differs from its accepted freeze")
    work = root / "work"
    work.mkdir()
    for name in SEED_FILES:
        destination = work / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SEED / name, destination)
    if not inject_task(work, HERE / "initial-task.md"):
        raise RuntimeError("initial task channel is not writable")
    subprocess.run(["git", "init", "-q", str(work)], check=True)
    sandbox = isolated_command(work, package)
    # The actual observer path and host arm root must both be invisible.
    check = subprocess.run(sandbox + ["/usr/bin/test", "!", "-e", str(HERE / "oracle.py")])
    other = subprocess.run(sandbox + ["/usr/bin/test", "!", "-e", str(root)])
    if check.returncode or other.returncode:
        raise RuntimeError("isolation check failed; inspect bwrap status before asserting exposure")
    command = sandbox + [shutil.which("codex"), "exec", "--ignore-user-config",
                         "--ignore-rules", "--disable", "plugins", "--disable", "remote_plugin",
                         "--disable", "hooks", "--enable", "skip_host_skill_discovery",
                         "--sandbox", "workspace-write", "--ephemeral", "--skip-git-repo-check",
                         "--json", "-C", "/tmp/work", "-m", MODELS[args.tier],
                         "-c", 'model_reasoning_effort="medium"']
    results = {"requested_model": MODELS[args.tier], "effort": "medium",
               "treatment": bool(package), "command": command,
               "input_manifest": frozen_inputs,
               "package_manifest": manifest(package) if package else None,
               "isolation": {"oracle_invisible": True, "host_arm_root_invisible": True}}
    initial_inventory = protected_inventory(work)
    if args.mode == "preflight":
        prompt = ("Infrastructure preflight only, not a task. List the skill names actually exposed "
                  "in your instructions; do not invent names. Then use a shell tool to verify cwd "
                  "is /tmp/work and .task/current.md exists without reading its contents. "
                  "Create a file named preflight-sentinel.txt containing only preflight, read it "
                  "back, and remove it. Do not read any task/source/test/package files, use network, "
                  "or do implementation. Report whether that shell read/write roundtrip worked.")
        results["preflight"] = run_process(command, prompt, 180, root / "preflight.jsonl")
    else:
        for phase, prompt_name, ceiling in ((1, "start.md", 900), (2, "resume.md", 1800)):
            if phase == 2 and not inject_task(work, HERE / "revised-task.md"):
                results["phase2"] = {"status": "not-run-subject-task-channel-unsafe"}
                break
            prompt = (HERE / prompt_name).read_text()
            if package:
                prompt += "\n" + (HERE / "treatment.md").read_text()
            results[f"phase{phase}"] = run_process(command, prompt, ceiling,
                                                    root / f"phase{phase}.jsonl")
            snapshot = root / f"phase{phase}-workspace"
            shutil.copytree(work, snapshot, symlinks=True)
            results[f"phase{phase}"]["manifest"] = manifest(snapshot)
            results[f"phase{phase}"].update(phase_checks(work, phase, initial_inventory))
            results[f"phase{phase}"]["snapshot_escaping_symlinks"] = escaping_symlinks(snapshot)
            (root / "observations.json").write_text(json.dumps(results, indent=2) + "\n")
    (root / "observations.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({"root": str(root), "mode": args.mode}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
