#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
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




_scripts_adapter_init_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_init_lib")
base_adapter_items = _scripts_adapter_init_lib_module.base_adapter_items
run_init_adapter = _scripts_adapter_init_lib_module.run_init_adapter

STABLE_SOURCE_CANDIDATES = (
    "README.md",
    "docs/roadmap.md",
    "docs/decisions.md",
    "docs/operator-acceptance.md",
    "docs/control-plane.md",
    "docs/specs/index.spec.md",
    "docs/specs/current-product.spec.md",
    "docs/consumer-readiness.md",
    "docs/external-consumer-onboarding.md",
)


def existing_stable_docs(repo_root: Path) -> list[str]:
    docs = [path for path in STABLE_SOURCE_CANDIDATES if (repo_root / path).is_file()]
    return docs or ["README.md"]


def build_items(repo_name: str, _args: object) -> list[tuple[str, object]]:
    repo_root = getattr(_args, "repo_root").resolve()
    source_documents = existing_stable_docs(repo_root)
    mutable_documents = [path for path in source_documents if not path.startswith("docs/specs/")]
    mutable_documents = mutable_documents or ["README.md"]
    return [
        *base_adapter_items(repo_name, "charness-artifacts/narrative"),
        ("source_documents", source_documents),
        ("mutable_documents", mutable_documents),
        ("brief_template", ["One-Line Summary", "Current Story", "What Changed", "Open Questions"]),
        ("scenario_surfaces", []),
        (
            "scenario_block_template",
            [
                "What You Bring",
                "Input (CLI)",
                "Input (For Agent)",
                "What Happens",
                "What Comes Back",
                "Next Action",
            ],
        ),
        (
            "primary_reader_profiles",
            [
                "first-time reader deciding whether this repo is relevant",
                "maintainer checking whether durable docs match current repo behavior",
            ],
        ),
        (
            "preserve_intents",
            [
                "Preserve the repo's current product or project promise before changing section order.",
            ],
        ),
        ("terms_to_avoid_in_opening", []),
        ("quick_start_execution_model", ""),
        ("special_entrypoints", []),
        ("skill_grouping_rules", []),
        (
            "owner_doc_boundaries",
            [
                "Keep deep implementation detail in owner docs and link from the landing surface.",
            ],
        ),
        (
            "landing_danger_checks",
            [
                "Do not use handoff, internal, archive, or stale generated notes as public README truth.",
                "Do not rewrite before missing adapter paths are fixed or explicitly removed.",
            ],
        ),
        ("remote_name", "origin"),
    ]


def main() -> None:
    output = run_init_adapter(default_output=Path(".agents/narrative-adapter.yaml"), build_items=build_items)
    sys.stdout.write(f"{output}\n")


if __name__ == "__main__":
    main()
