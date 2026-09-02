#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")




_scripts_operator_acceptance_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.gates_support.operator_acceptance_lib")
synthesize_operator_acceptance = _scripts_operator_acceptance_lib_module.synthesize_operator_acceptance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose operator-acceptance doc should be synthesized")
    parser.add_argument("--output", type=Path, default=Path("docs/operator-acceptance.md"), help="Output path for the generated doc")
    parser.add_argument("--write", action="store_true", help="Write the doc to disk instead of stdout")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output file")
    args = parser.parse_args()

    payload = synthesize_operator_acceptance(
        repo_root=args.repo_root.resolve(),
        output_path=args.output,
        write=args.write,
        force=args.force,
    )
    # Unconditional YAML. The generated document is not lost by this: it rides in
    # the payload as `markdown`, and `--write` remains the way to put it on disk.
    # Raw markdown on stdout was the other half of the removed format flag, not a
    # separate product.
    yaml_output.emit_yaml(payload)


if __name__ == "__main__":
    main()
