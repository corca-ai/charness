#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
_report_mode_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.hitl_report_mode_lib")
load_adapter = _resolve_adapter_module.load_adapter
render_report = _report_mode_lib.render_report
ReportModeError = _report_mode_lib.ReportModeError


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a HITL report packet as a decision queue.")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True, help="Queue/report packet JSON.")
    parser.add_argument("--output-html", type=Path, help="HTML review surface path.")
    parser.add_argument("--output-decisions", type=Path, help="Structured decisions JSON path.")
    parser.add_argument("--review-input", type=Path, help="Optional human-submitted review JSON.")
    args = parser.parse_args()
    try:
        adapter = load_adapter(args.repo_root.resolve())
        payload = render_report(
            repo_root=args.repo_root.resolve(),
            input_path=args.input,
            output_html=args.output_html,
            output_decisions=args.output_decisions,
            review_input_path=args.review_input,
            runtime_dir=adapter["runtime_dir"],
        )
    except (ReportModeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
