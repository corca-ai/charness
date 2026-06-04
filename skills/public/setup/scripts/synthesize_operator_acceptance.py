#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)




_scripts_operator_acceptance_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.operator_acceptance_lib")
synthesize_operator_acceptance = _scripts_operator_acceptance_lib_module.synthesize_operator_acceptance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose operator-acceptance doc should be synthesized")
    parser.add_argument("--output", type=Path, default=Path("docs/operator-acceptance.md"), help="Output path for the generated doc")
    parser.add_argument("--write", action="store_true", help="Write the doc to disk instead of stdout")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output file")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload instead of markdown")
    args = parser.parse_args()

    payload = synthesize_operator_acceptance(
        repo_root=args.repo_root.resolve(),
        output_path=args.output,
        write=args.write,
        force=args.force,
    )
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(payload["markdown"])


if __name__ == "__main__":
    main()
