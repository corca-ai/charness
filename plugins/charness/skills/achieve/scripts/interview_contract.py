#!/usr/bin/env python3
"""Validate the bounded decision record that precedes goal tracker creation."""

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
POLICY = SKILL_RUNTIME.load_local_skill_module(__file__, "achieve_adapter_policy")
YAML_OUTPUT = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")


def _nonempty(value: Any, field: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")
        return None
    return value.strip()


def _string_list(value: Any, field: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"{field} must be a list of non-empty strings")
        return []
    return [item.strip() for item in value]


def _validate_question(raw: Any, index: int, errors: list[str]) -> dict[str, Any]:  # noqa: C901 -- question validation reports all field errors in one pass
    prefix = f"questions[{index}]"
    if not isinstance(raw, dict):
        errors.append(f"{prefix} must be a mapping")
        return {}
    decision = _nonempty(raw.get("decision"), f"{prefix}.decision", errors)
    raw_options = raw.get("options")
    options: list[dict[str, str]] = []
    option_ids: list[str] = []
    if not isinstance(raw_options, list) or len(raw_options) < 2:
        errors.append(f"{prefix}.options must contain at least two options")
    else:
        for option_index, raw_option in enumerate(raw_options):
            option_prefix = f"{prefix}.options[{option_index}]"
            if not isinstance(raw_option, dict):
                errors.append(f"{option_prefix} must be a mapping")
                continue
            option_id = _nonempty(raw_option.get("id"), f"{option_prefix}.id", errors)
            summary = _nonempty(raw_option.get("summary"), f"{option_prefix}.summary", errors)
            tradeoff = _nonempty(raw_option.get("tradeoff"), f"{option_prefix}.tradeoff", errors)
            if option_id:
                option_ids.append(option_id)
            if option_id and summary and tradeoff:
                options.append({"id": option_id, "summary": summary, "tradeoff": tradeoff})
    if len(set(option_ids)) != len(option_ids):
        errors.append(f"{prefix}.options ids must be unique")

    recommendation = raw.get("recommendation")
    recommendation_out: dict[str, str] = {}
    if not isinstance(recommendation, dict):
        errors.append(f"{prefix}.recommendation must be a mapping")
    else:
        recommended = _nonempty(
            recommendation.get("option"), f"{prefix}.recommendation.option", errors
        )
        reason = _nonempty(
            recommendation.get("reason"), f"{prefix}.recommendation.reason", errors
        )
        if recommended and recommended not in option_ids:
            errors.append(f"{prefix}.recommendation.option must name a declared option")
        if recommended and reason:
            recommendation_out = {"option": recommended, "reason": reason}

    answer = raw.get("answer")
    answer_out: dict[str, str] | None = None
    if answer is not None:
        if not isinstance(answer, dict):
            errors.append(f"{prefix}.answer must be a mapping when present")
        else:
            selected = _nonempty(answer.get("option"), f"{prefix}.answer.option", errors)
            reason = _nonempty(answer.get("reason"), f"{prefix}.answer.reason", errors)
            if selected and selected not in option_ids:
                errors.append(f"{prefix}.answer.option must name a declared option")
            if selected and reason:
                answer_out = {"option": selected, "reason": reason}

    rejected_out: list[dict[str, str]] = []
    raw_rejected = raw.get("rejected_alternatives", [])
    if answer_out is not None:
        if not isinstance(raw_rejected, list):
            errors.append(f"{prefix}.rejected_alternatives must be a list")
        else:
            seen: set[str] = set()
            for rejected_index, raw_rejection in enumerate(raw_rejected):
                rejected_prefix = f"{prefix}.rejected_alternatives[{rejected_index}]"
                if not isinstance(raw_rejection, dict):
                    errors.append(f"{rejected_prefix} must be a mapping")
                    continue
                option = _nonempty(raw_rejection.get("option"), f"{rejected_prefix}.option", errors)
                reason = _nonempty(raw_rejection.get("reason"), f"{rejected_prefix}.reason", errors)
                if option and (option not in option_ids or option == answer_out["option"]):
                    errors.append(f"{rejected_prefix}.option must name a non-selected declared option")
                if option:
                    seen.add(option)
                if option and reason:
                    rejected_out.append({"option": option, "reason": reason})
            expected = set(option_ids) - {answer_out["option"]}
            if seen != expected:
                errors.append(
                    f"{prefix}.rejected_alternatives must explain every non-selected option"
                )

    return {
        "decision": decision,
        "options": options,
        "recommendation": recommendation_out,
        "answer": answer_out,
        "rejected_alternatives": rejected_out,
    }


def validate_record(record: Any, *, max_questions: int) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return {
            "ok": False,
            "status": "invalid",
            "parent_creation_ready": False,
            "max_questions": max_questions,
            "question_count": 0,
            "errors": ["record must be a mapping"],
        }
    if record.get("version") != 1:
        errors.append("version must be 1")
    raw_questions = record.get("questions")
    if not isinstance(raw_questions, list):
        errors.append("questions must be a list")
        raw_questions = []
    questions = [
        _validate_question(raw, index, errors) for index, raw in enumerate(raw_questions)
    ]
    remaining = _string_list(
        record.get("remaining_consequential_decisions", []),
        "remaining_consequential_decisions",
        errors,
    )
    count = len(raw_questions)
    if count > max_questions:
        errors.append(
            f"question count {count} exceeds configured maximum {max_questions}"
        )
    unanswered = [index for index, question in enumerate(questions) if question.get("answer") is None]
    if errors:
        status = "invalid"
    elif remaining and count >= max_questions:
        status = "interview-cap-reached"
    elif remaining or unanswered:
        status = "interview-in-progress"
    else:
        status = "interview-complete"
    return {
        "ok": not errors,
        "status": status,
        "parent_creation_ready": status == "interview-complete",
        "max_questions": max_questions,
        "question_count": count,
        "remaining_consequential_decisions": remaining,
        "unanswered_question_indexes": unanswered,
        "questions": questions,
        "errors": errors,
        "next_action": (
            "raise interview.max_questions or narrow the goal before creating a parent"
            if status == "interview-cap-reached"
            else "create and read back the GitHub parent"
            if status == "interview-complete"
            else "continue the interview"
            if status == "interview-in-progress"
            else "repair the interview record"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a bounded achieve interview before GitHub parent creation."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root used to resolve the achieve adapter")
    parser.add_argument("--record", type=Path, required=True, help="JSON interview record to validate")
    args = parser.parse_args()
    policy = POLICY.interview_policy_report(args.repo_root.resolve())
    if not policy["valid"]:
        YAML_OUTPUT.emit_yaml({"ok": False, "status": "invalid-adapter", "policy": policy})
        return 2
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        YAML_OUTPUT.emit_yaml({"ok": False, "status": "invalid", "errors": [str(exc)]})
        return 2
    result = validate_record(record, max_questions=policy["max_questions"])
    result["policy"] = policy
    YAML_OUTPUT.emit_yaml(result)
    return 0 if result["parent_creation_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
