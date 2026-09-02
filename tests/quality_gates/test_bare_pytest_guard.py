"""The bare-run guard in `tests/conftest.py`.

The guard's job is to stop a broad selection from running single-process when
`scripts/gates_support/run_standing_pytest.py` would have supplied xdist. Measured on this
repo: 8400 tests take ~110s through the runner and over half an hour without it,
and nothing in pytest's own output says the fast path was skipped.

These tests drive `bare_pytest_refusal` -- the decision -- rather than the hook
that acts on it. The hook calls `pytest.exit`, which a worker interprets as "the
session is over" and reports as a crashed worker, so the decision has to be
separable to be testable at all. The end-to-end refusal is proven by
`test_the_hook_stops_the_session_on_a_refusal` spawning a real pytest.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from tests import conftest

ROOT = Path(__file__).resolve().parents[2]


def _config(numprocesses: object) -> SimpleNamespace:
    return SimpleNamespace(option=SimpleNamespace(numprocesses=numprocesses))


def _items(count: int) -> list[object]:
    return [object()] * count


def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        conftest.CANONICAL_RUNNER_ENV,
        conftest.BARE_PYTEST_ESCAPE_ENV,
        conftest.NESTED_PYTEST_ENV,
        "PYTEST_XDIST_WORKER",
    ):
        monkeypatch.delenv(name, raising=False)


def test_a_broad_serial_selection_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)

    message = conftest.bare_pytest_refusal(
        _config(None), _items(conftest.BARE_PYTEST_ITEM_FLOOR)
    )

    assert message is not None
    assert "run_standing_pytest.py" in message
    assert conftest.BARE_PYTEST_ESCAPE_ENV in message


def test_xdist_in_use_is_the_primary_exemption(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keyed on whether the fast path is actually in use, not on who launched it.

    The runner always passes `-n`, so this exemption covers it without the guard
    having to trust an environment variable.
    """
    _clear_env(monkeypatch)

    assert conftest.bare_pytest_refusal(_config(8), _items(10_000)) is None


def test_the_runner_marker_exempts_its_serial_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv(conftest.CANONICAL_RUNNER_ENV, "1")

    assert conftest.bare_pytest_refusal(_config(None), _items(10_000)) is None


def test_a_deliberate_bare_run_declares_itself(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv(conftest.BARE_PYTEST_ESCAPE_ENV, "1")

    assert conftest.bare_pytest_refusal(_config(None), _items(10_000)) is None


def test_a_focused_selection_is_never_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """xdist startup can make a small check slower, so the floor is not decoration."""
    _clear_env(monkeypatch)

    assert conftest.bare_pytest_refusal(
        _config(None), _items(conftest.BARE_PYTEST_ITEM_FLOOR - 1)
    ) is None


def test_an_xdist_worker_is_not_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw3")

    assert conftest.bare_pytest_refusal(_config(None), _items(10_000)) is None


def test_the_runner_actually_sets_the_marker_the_guard_reads() -> None:
    """Both halves of the contract in one assertion.

    A guard keyed on a name the runner never sets would refuse the runner's own
    serial fallback, and nothing else in the suite pairs the two spellings.
    """
    source = (ROOT / "scripts" / "gates_support" / "run_standing_pytest.py").read_text(encoding="utf-8")
    assert f'env["{conftest.CANONICAL_RUNNER_ENV}"] = "1"' in source


def test_the_marker_is_not_an_ambient_pytest_variable() -> None:
    """`PYTEST_DEBUG_TEMPROOT` cannot serve as the marker.

    It survives in any shell descended from a run that exported it, so it reports
    "the canonical runner owns this session" for a hand-typed command in the same
    terminal. That was observed on the authoring machine while building this
    guard, and it is the ambient-runner-state class `_scrub_ambient_runner_state`
    already exists for.
    """
    assert not conftest.CANONICAL_RUNNER_ENV.startswith("PYTEST_")


def test_cosmic_ray_declares_its_deliberate_serial_run() -> None:
    """The mutation harness runs one bare serial pytest per mutant, by design.

    If it stopped declaring that, the guard would refuse every mutant and the
    mutation baseline would read as a suite-wide failure.
    """
    # Read as text, not parsed: `tomllib` is 3.11+ and this suite runs on 3.10.
    text = (ROOT / "cosmic-ray.toml").read_text(encoding="utf-8")
    command = next(
        line for line in text.splitlines() if line.startswith("test-command")
    )
    assert f"{conftest.BARE_PYTEST_ESCAPE_ENV}=1" in command
    assert "python3 -m pytest" in command


def test_the_hook_stops_the_session_rather_than_raising(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pins the bug this guard was first written with.

    The first draft did `raise pytest.UsageError(...)`. pytest's hook caller
    ABSORBS an exception raised inside `pytest_collection_modifyitems`: the hook
    entered, raised, and 5935 tests were still reported as collected -- a guard
    that believed it had refused while the expensive run proceeded. Only
    `pytest.exit` stops the session, so the hook must call it.

    Not spawned as a real subprocess on purpose. A nested pytest over this repo
    would need `PYTEST_XDIST_WORKER` cleared to reach the guard, and clearing it
    also re-arms the `pytest_sessionfinish` orphan reaper against the real repo --
    the hazard that hook's own comment documents.
    """
    _clear_env(monkeypatch)
    calls: list[dict[str, object]] = []
    monkeypatch.setattr(
        pytest, "exit", lambda msg, returncode=0: calls.append({"msg": msg, "rc": returncode})
    )

    conftest.pytest_collection_modifyitems(
        _config(None), _items(conftest.BARE_PYTEST_ITEM_FLOOR)
    )

    assert len(calls) == 1
    assert calls[0]["rc"] == 4
    assert "run_standing_pytest.py" in str(calls[0]["msg"])


def test_the_hook_does_not_stop_an_exempt_session(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setattr(
        pytest, "exit", lambda *_a, **_k: pytest.fail("an exempt session must not be stopped")
    )

    conftest.pytest_collection_modifyitems(_config(8), _items(10_000))
