"""Focused proof for adapter value readers, refusal sites, and retired keys."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.adapter_key_registry import (  # noqa: E402
    RETIRED_KEYS,
    audit_registry,
    find_readers,
    resolve_key,
)


def test_retired_keys_are_registered_and_not_reported_as_readers() -> None:
    assert set(RETIRED_KEYS) == {"max_content_lines", "max_artifact_lines"}

    for key in RETIRED_KEYS:
        resolution = resolve_key(ROOT, key)
        assert resolution.state == "retired"
        assert resolution.readers == ()
        assert find_readers(ROOT, key)[0] == ()


def test_value_reader_and_literal_refusal_are_structurally_distinct(tmp_path: Path) -> None:
    module = tmp_path / "scripts" / "adapter.py"
    module.parent.mkdir()
    module.write_text(
        """
RETIRED_FIELD = "old_key"
TEXT_ASSERTION = "text_only:"

def validate(data):
    if RETIRED_FIELD in data:
        return False
    return data.get("live_key")

REQUIRED = (TEXT_ASSERTION,)
""",
        encoding="utf-8",
    )

    assert find_readers(tmp_path, "old_key", files=[module]) == ((), ())
    assert find_readers(tmp_path, "live_key", files=[module]) == (("scripts/adapter.py",), ())
    assert find_readers(tmp_path, "text_only", files=[module]) == ((), ("scripts/adapter.py",))


def test_a_module_that_refuses_and_then_reads_a_key_remains_a_reader(tmp_path: Path) -> None:
    module = tmp_path / "scripts" / "adapter.py"
    module.parent.mkdir()
    module.write_text(
        'KEY = "shared_key"\n\n'
        'def validate(data):\n'
        '    if KEY in data:\n'
        '        return data[KEY]\n',
        encoding="utf-8",
    )

    assert find_readers(tmp_path, "shared_key", files=[module]) == (("scripts/adapter.py",), ())


def test_intent_reader_default_section_is_a_value_reader(tmp_path: Path) -> None:
    module = tmp_path / "scripts" / "intent_reader.py"
    module.parent.mkdir()
    module.write_text(
        'def _intent_for(adapter, section="some_declared_key"):\n'
        "    return adapter.lookup(section)\n",
        encoding="utf-8",
    )

    assert find_readers(tmp_path, "some_declared_key", files=[module]) == (
        ("scripts/intent_reader.py",),
        (),
    )


def test_write_only_subscript_is_not_a_value_reader(tmp_path: Path) -> None:
    module = tmp_path / "scripts" / "writer.py"
    module.parent.mkdir()
    module.write_text(
        'def emit(data):\n'
        '    data["target"] = 3\n',
        encoding="utf-8",
    )

    assert find_readers(tmp_path, "target", files=[module]) == ((), ())


def test_field_presence_validation_is_not_value_consumption(tmp_path: Path) -> None:
    module = tmp_path / "scripts" / "presence.py"
    module.parent.mkdir()
    module.write_text(
        'FIELDS = ("target",)\n'
        '\n'
        'def validate(data):\n'
        '    return any(field in data for field in FIELDS)\n',
        encoding="utf-8",
    )

    assert find_readers(tmp_path, "target", files=[module]) == ((), ())


def test_rebound_string_alias_is_not_a_static_value_reader(tmp_path: Path) -> None:
    module = tmp_path / "scripts" / "dynamic_alias.py"
    module.parent.mkdir()
    module.write_text(
        'KEY = "target"\n'
        'KEY = runtime_key()\n'
        '\n'
        'def read(data):\n'
        '    return data[KEY]\n',
        encoding="utf-8",
    )

    assert find_readers(tmp_path, "target", files=[module]) == ((), ())


def test_retired_registry_entries_are_consistent_with_the_tree() -> None:
    assert audit_registry(ROOT) == []
