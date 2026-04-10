from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "support" / "gather-notion" / "vendor" / "notion-to-md.py"
MODULE_SPEC = importlib.util.spec_from_file_location("notion_to_md", MODULE_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(MODULE)


def test_fetch_page_unwraps_records_and_syncs_missing_children(monkeypatch) -> None:
    page_id = "page-id"
    header_id = "header-id"
    child_id = "child-id"
    calls: list[str] = []

    def fake_api_request(payload: dict, *, api_url: str = MODULE.API_URL) -> dict:
        calls.append(api_url)
        if api_url == MODULE.API_URL:
            return {
                "recordMap": {
                    "block": {
                        page_id: {
                            "value": {
                                "value": {
                                    "id": page_id,
                                    "type": "page",
                                    "properties": {"title": [["Demo Page"]]},
                                    "content": [header_id],
                                }
                            }
                        },
                        header_id: {
                            "value": {
                                "value": {
                                    "id": header_id,
                                    "type": "header",
                                    "properties": {"title": [["Section"]]},
                                    "content": [child_id],
                                }
                            }
                        },
                    }
                },
                "cursor": {},
            }
        assert api_url == MODULE.SYNC_API_URL
        return {
            "recordMap": {
                "block": {
                    child_id: {
                        "value": {
                            "value": {
                                "id": child_id,
                                "type": "text",
                                "properties": {"title": [["Nested body"]]},
                            }
                        }
                    }
                }
            }
        }

    monkeypatch.setattr(MODULE, "_api_request", fake_api_request)
    block_map, page_title = MODULE.fetch_page(page_id)

    assert page_title == "Demo Page"
    assert block_map[page_id]["type"] == "page"
    assert child_id in block_map
    markdown = MODULE.blocks_to_markdown(page_id, block_map)
    assert "# Demo Page" in markdown
    assert "# Section" in markdown
    assert "Nested body" in markdown
    assert calls == [MODULE.API_URL, MODULE.SYNC_API_URL]
