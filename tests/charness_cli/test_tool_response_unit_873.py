from __future__ import annotations

import scripts.cli.tool_response as tool_response


def test_tool_result_map_rejects_non_list_and_skips_non_dicts() -> None:
    assert tool_response.tool_result_map({"a": 1}) == {}
    assert tool_response.tool_result_map(None) == {}
    mapped = tool_response.tool_result_map(["nope", {"tool_id": 42}, {"tool_id": "alpha", "v": 1}])
    assert mapped == {"alpha": {"tool_id": "alpha", "v": 1}}


def test_tool_release_result_returns_first_release_dict() -> None:
    release = {"status": "ok", "latest_tag": "v1"}
    assert tool_response._tool_release_result({"x": 1}, {"release": release}) == release
    assert tool_response._tool_release_result({"x": 1}, None) is None
    assert tool_response._tool_release_result() is None


def test_print_tool_result_block_full_shapes(capsys) -> None:
    result = {
        "repair": {"status": "fixed", "execute": True},
        "install": {
            "status": "ok",
            "mode": "script",
            "provenance": {"install_method": "script", "package_name": "pkg"},
            "release": {"status": "ok", "latest_tag": "v9"},
        },
        "update": {
            "status": "updated",
            "mode": "package_manager",
            "package_manager": "brew",
            "package_name": "tool",
            "healthcheck": {"status": "ok"},
        },
        "support": {"status": "ok"},
        "doctor": {
            "doctor_status": "healthy",
            "support_state": "ready",
            "provenance": {"install_method": "brew", "binary_path": "/usr/bin/t"},
        },
        "next_step": "run again",
    }
    tool_response._print_tool_result_block("alpha", result)
    out = capsys.readouterr().out
    assert "alpha:" in out
    assert "REPAIR: fixed (execute)" in out
    assert "INSTALL: ok (script)" in out
    assert "INSTALL_PROVENANCE: script pkg" in out
    assert "UPDATE: updated (package_manager)" in out
    assert "UPDATE_ROUTE: brew tool" in out
    assert "SUPPORT: ok" in out
    assert "DOCTOR: healthy (ready)" in out
    assert "PROVENANCE: brew /usr/bin/t" in out
    assert "RELEASE: ok v9" in out
    assert "NEXT: run again" in out


def test_print_tool_result_block_minimal_and_preview_repair(capsys) -> None:
    tool_response._print_tool_result_block("beta", {"repair": {"status": "x"}})
    out = capsys.readouterr().out
    assert "beta:" in out
    assert "REPAIR: x (preview)" in out
    tool_response._print_tool_result_block("gamma", {})
    assert "gamma:" in capsys.readouterr().out


def test_compact_tool_action_empty_compact_branch() -> None:
    assert tool_response._compact_tool_action("repair", {"unrelated": 1}) is None
    assert tool_response._compact_tool_action("repair", None) is None
    compact = tool_response._compact_tool_action("repair", {"status": "ok", "execute": False})
    assert compact == {"status": "ok", "execute": False}


def test_tool_result_status_doctor_and_none_branches() -> None:
    assert tool_response._tool_result_status({"doctor": {"doctor_status": "healthy"}}) == "healthy"
    assert tool_response._tool_result_status({"update": {"status": "updated"}}) == "updated"
    assert tool_response._tool_result_status({}) is None
    assert tool_response._tool_result_status({"doctor": {"doctor_status": 42}}) is None
