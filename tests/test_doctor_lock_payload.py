from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTOR_PATH = ROOT / "scripts" / "doctor.py"


def load_doctor_module():
    spec = importlib.util.spec_from_file_location("doctor", DOCTOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lock_safe_doctor_payload_truncates_volatile_command_output() -> None:
    doctor = load_doctor_module()
    long_stdout = "x" * (doctor.LOCK_OUTPUT_LIMIT + 250)
    payload = {
        "install_route": {"mode": "npm"},
        "support_discovery": {"paths": ["support/agent-browser"]},
        "previous_lock_present": True,
        "release": {"latest": "1.2.3"},
        "provenance": {"install_method": "npm"},
        "next_steps": ["cleanup"],
        "support_sync": {"status": "ok", "expected_paths": [], "missing_paths": [], "extra": "drop"},
        "detect": {"ok": True, "results": [], "failure_details": []},
        "healthcheck": {
            "ok": False,
            "results": [{"command": "demo", "exit_code": 1, "stdout": long_stdout, "stderr": long_stdout}],
            "failure_details": [long_stdout],
            "failure_hint": "Run cleanup.",
        },
    }

    safe = doctor.lock_safe_doctor_payload(payload)

    assert "install_route" not in safe
    assert "release" not in safe
    assert safe["support_sync"] == {"status": "ok", "expected_paths": [], "missing_paths": []}
    result = safe["healthcheck"]["results"][0]
    assert len(result["stdout"]) < len(long_stdout)
    assert "truncated 250 chars" in result["stdout"]
    assert "truncated 250 chars" in safe["healthcheck"]["failure_details"][0]
