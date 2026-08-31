from __future__ import annotations

import hashlib
import multiprocessing
import os
import subprocess
import time
from pathlib import Path

import pytest

from tests import seed_cache


def test_source_hash_reuses_the_controller_value_in_workers(monkeypatch) -> None:
    inherited = "a" * 32
    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", None)
    monkeypatch.setenv(seed_cache._SOURCE_HASH_ENV, inherited)
    monkeypatch.setattr(
        seed_cache,
        "_compute_source_hash",
        lambda _root: (_ for _ in ()).throw(AssertionError("must reuse controller hash")),
    )

    assert seed_cache.source_hash() == inherited


def test_invalid_inherited_source_hash_is_not_trusted(monkeypatch) -> None:
    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", None)
    monkeypatch.setenv(seed_cache._SOURCE_HASH_ENV, "not-a-source-hash")
    monkeypatch.setattr(seed_cache, "_compute_source_hash", lambda _root: "b" * 32)

    assert seed_cache.source_hash() == "b" * 32


def test_a_failed_git_read_refuses_instead_of_naming_a_shared_cache_key(tmp_path) -> None:
    """A directory git cannot read must not digest to a key other checkouts share.

    Discarding the return code fed the empty string into the digest, so EVERY
    source state that failed the same way produced one constant key -- a single
    cache namespace that unrelated checkouts would both write into and read back,
    serving each other's seeds as a hit.
    """
    not_a_repo = tmp_path / "not-a-repo"
    not_a_repo.mkdir()

    with pytest.raises(seed_cache.SourceStateUnreadable):
        seed_cache._compute_source_hash(not_a_repo)


@pytest.mark.boundary_contract(
    reason=(
        "reproduces the PRE-FIX digest, which is defined by what real `git` writes to "
        "stdout when it fails; a fake git would be my own belief about the failure "
        "rather than the failure that shipped"
    )
)
def test_the_discarded_return_code_is_what_collapsed_two_trees_to_one_key(tmp_path) -> None:
    """Pins the PROPERTY (distinct source states never share a key), not the mechanism.

    Asserting `pytest.raises` on a second directory would just be the previous test
    run twice: no mutant can kill one without killing the other. So this reproduces
    the pre-fix digest inline and shows it COLLIDING, which is the fact that makes
    the refusal worth having. A future repair that keeps the suite running by
    minting a distinct per-root key instead of raising still satisfies this test --
    the contract is "no collision", not "raise".
    """
    first = tmp_path / "one"
    second = tmp_path / "two"
    first.mkdir()
    second.mkdir()
    (first / "alpha.txt").write_text("A" * 100, encoding="utf-8")
    (second / "beta.md").write_text("B" * 9000, encoding="utf-8")

    def pre_fix_digest(root) -> str:
        """`subprocess.run(..., check=False)` reading only `.stdout`, as it was."""
        d = hashlib.sha256()
        for args in (
            ["rev-parse", "HEAD"],
            ["diff", "HEAD"],
            ["ls-files", "--others", "--exclude-standard"],
        ):
            d.update(
                subprocess.run(
                    ["git", "-C", str(root), *args],
                    capture_output=True,
                    text=True,
                    check=False,
                ).stdout.encode()
            )
        return d.hexdigest()[:32]

    assert pre_fix_digest(first) == pre_fix_digest(second), (
        "the defect being fixed is gone from the reproduction itself"
    )

    for root in (first, second):
        with pytest.raises(seed_cache.SourceStateUnreadable):
            seed_cache._compute_source_hash(root)


@pytest.mark.boundary_contract(
    reason=(
        "the subject is the key computed over a real checkout: the untracked set comes "
        "from `git ls-files --others`, so the repository IS the input under test"
    )
)
def test_untracked_content_is_length_prefixed_so_names_cannot_absorb_content(
    tmp_path,
) -> None:
    """`name\\0content` concatenated is ambiguous; two different trees digested equal.

    Files `a` (empty) and `b` (b"c") emit `a\\0b\\0c`; a single file `a` holding
    `b"b\\0c"` emits the same bytes.
    """
    def build(root, files: dict[str, bytes]) -> str:
        root.mkdir()
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        # `-c` is a GLOBAL git option: it has to precede the subcommand, not follow it.
        subprocess.run(
            ["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "-q", "--allow-empty", "-m", "seed"],
            check=True, capture_output=True,
        )
        for name, payload in files.items():
            (root / name).write_bytes(payload)
        return seed_cache._compute_source_hash(root)

    split = build(tmp_path / "split", {"a": b"", "b": b"c"})
    joined = build(tmp_path / "joined", {"a": b"b\0c"})

    assert split != joined


def _concurrent_seed_worker(
    cache_root: str,
    counter_path: str,
    start_event,
    result_queue,
) -> None:
    os.environ["CHARNESS_TEST_SEED_CACHE_ROOT"] = cache_root
    seed_cache._SOURCE_HASH = "concurrency-contract"
    start_event.wait(timeout=10)

    def build(destination: Path) -> None:
        with Path(counter_path).open("a", encoding="utf-8") as counter:
            counter.write("build\n")
        # Give the peer time to wait for this outer seed. The cache must release its
        # root lock while waiting so a builder can safely compose another cached seed.
        time.sleep(0.2)
        dependency = seed_cache.get_or_build(
            "dependency",
            lambda nested: (nested / "ready.txt").write_text("ready\n", encoding="utf-8"),
        )
        assert (dependency / "ready.txt").read_text(encoding="utf-8") == "ready\n"
        (destination / "complete.txt").write_text("complete\n", encoding="utf-8")

    result = seed_cache.get_or_build("shared", build)
    result_queue.put((result / "complete.txt").read_text(encoding="utf-8"))


def _cross_hash_seed_worker(
    cache_root: str,
    source_hash: str,
    start_event,
    started_queue,
    release_event,
    result_queue,
) -> None:
    os.environ["CHARNESS_TEST_SEED_CACHE_ROOT"] = cache_root
    os.environ["CHARNESS_TEST_SEED_CACHE_KEEP"] = "1"
    seed_cache._SOURCE_HASH = source_hash
    start_event.wait(timeout=10)

    def build(destination: Path) -> None:
        started_queue.put(source_hash)
        release_event.wait(timeout=10)
        (destination / "complete.txt").write_text("complete\n", encoding="utf-8")

    result = seed_cache.get_or_build("shared", build)
    result_queue.put((source_hash, (result / "complete.txt").read_text(encoding="utf-8")))


@pytest.mark.boundary_contract(
    reason="Cross-process locking is the behavior under test; an in-process fake cannot prove it."
)
def test_seed_cache_builds_once_across_processes(tmp_path: Path) -> None:
    context = multiprocessing.get_context("spawn")
    start_event = context.Event()
    result_queue = context.Queue()
    counter = tmp_path / "build-count.txt"
    workers = [
        context.Process(
            target=_concurrent_seed_worker,
            args=(str(tmp_path / "cache"), str(counter), start_event, result_queue),
        )
        for _ in range(2)
    ]

    for worker in workers:
        worker.start()
    start_event.set()
    for worker in workers:
        worker.join(timeout=15)

    assert [worker.exitcode for worker in workers] == [0, 0]
    assert counter.read_text(encoding="utf-8").splitlines() == ["build"]
    assert sorted(result_queue.get(timeout=2) for _ in workers) == ["complete\n", "complete\n"]


@pytest.mark.boundary_contract(
    reason="Cross-process pruning races are the behavior under test."
)
def test_seed_cache_pruning_does_not_delete_a_different_hash_build(
    tmp_path: Path,
) -> None:
    """Root pruning and per-entry lock acquisition must be one transaction.

    With only the per-entry lock, a second source hash can observe the first hash between
    its prune and lock acquisition and delete the directory before its builder starts.
    """
    context = multiprocessing.get_context("spawn")
    start_event = context.Event()
    release_event = context.Event()
    started_queue = context.Queue()
    result_queue = context.Queue()
    workers = [
        context.Process(
            target=_cross_hash_seed_worker,
            args=(
                str(tmp_path / "cache"),
                source_hash,
                start_event,
                started_queue,
                release_event,
                result_queue,
            ),
        )
        for source_hash in ("a" * 32, "b" * 32)
    ]

    try:
        for worker in workers:
            worker.start()
        start_event.set()
        assert sorted(started_queue.get(timeout=15) for _ in workers) == ["a" * 32, "b" * 32]
        assert (tmp_path / "cache" / ("a" * 32)).is_dir()
        assert (tmp_path / "cache" / ("b" * 32)).is_dir()
    finally:
        release_event.set()
        for worker in workers:
            worker.join(timeout=15)

    assert [worker.exitcode for worker in workers] == [0, 0]
    assert sorted(result_queue.get(timeout=2) for _ in workers) == [
        ("a" * 32, "complete\n"),
        ("b" * 32, "complete\n"),
    ]


def test_seed_cache_rebuilds_stale_ready_marker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHARNESS_TEST_SEED_CACHE_ROOT", str(tmp_path / "cache"))
    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", "stale-ready")
    cache_dir = tmp_path / "cache" / "stale-ready"
    cache_dir.mkdir(parents=True)
    (cache_dir / "demo.ready").write_text("stale", encoding="utf-8")

    result = seed_cache.get_or_build(
        "demo",
        lambda destination: (destination / "complete.txt").write_text(
            "rebuilt", encoding="utf-8"
        ),
    )

    assert (result / "complete.txt").read_text(encoding="utf-8") == "rebuilt"
    assert (cache_dir / "demo.ready").read_text(encoding="utf-8") == "ok"


def test_seed_cache_rebuilds_partial_directory_without_ready_marker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHARNESS_TEST_SEED_CACHE_ROOT", str(tmp_path / "cache"))
    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", "partial-directory")
    partial = tmp_path / "cache" / "partial-directory" / "demo"
    partial.mkdir(parents=True)
    (partial / "partial.txt").write_text("incomplete", encoding="utf-8")

    result = seed_cache.get_or_build(
        "demo",
        lambda destination: (destination / "complete.txt").write_text(
            "rebuilt", encoding="utf-8"
        ),
    )

    assert not (result / "partial.txt").exists()
    assert (result / "complete.txt").read_text(encoding="utf-8") == "rebuilt"


def test_a_content_addressed_seed_survives_a_source_change_and_a_default_one_does_not(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """The whole reason the shape namespace exists, with its own control.

    A shape holds no repo content, so a source change cannot invalidate it -- but that is
    only worth a second namespace if the DEFAULT still rebuilds. Measured on the full
    standing suite before this split, one edit cost the next run 392 fixture `git` calls,
    ~330 of them rebuilding 147 shapes that had depended on nothing that changed.
    """
    monkeypatch.setenv("CHARNESS_TEST_SEED_CACHE_ROOT", str(tmp_path / "cache"))
    builds: list[str] = []

    def build(kind: str):
        def _build(destination: Path) -> None:
            builds.append(kind)
            (destination / "payload.txt").write_text(kind, encoding="utf-8")

        return _build

    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", "a" * 32)
    shape = seed_cache.get_or_build("demo-shape", build("shape"), content_addressed=True)
    seed_cache.get_or_build("demo-default", build("default"))
    assert builds == ["shape", "default"]

    # One edit: a new working tree state, therefore a new source hash.
    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", "b" * 32)
    again = seed_cache.get_or_build("demo-shape", build("shape"), content_addressed=True)
    seed_cache.get_or_build("demo-default", build("default"))

    assert builds == ["shape", "default", "default"], "the shape must not have rebuilt"
    assert again == shape
    assert (again / "payload.txt").read_text(encoding="utf-8") == "shape"
    # And it lives outside every source-hash entry, where no source hash can reach it.
    assert shape.parent == seed_cache.shapes_root()
    assert not seed_cache._HASH_DIR.match(shape.parent.name)


def test_every_shape_key_carries_the_builder_version(monkeypatch) -> None:
    """Leaving the source-hash namespace gives up the rebuild an edited builder used to get
    for free. Each of the three shape families has to buy that back in its own key."""
    from tests.quality_gates import repo_shapes

    def keys() -> tuple[str, str, str]:
        return (
            repo_shapes._file_digest(
                {"f.txt": "v\n"},
                message="m",
                branch="main",
                author_date=None,
                executable=(),
            ),
            repo_shapes._two_commit_digest(
                {"f.txt": "1\n"},
                {"f.txt": "2\n"},
                first_message="a",
                second_message="b",
                branch="main",
            ),
            repo_shapes._submodule_digest(
                {"r.txt": "r\n"},
                {"f.txt": "v\n"},
                message="m",
                submodule_message="s",
                add_message="add",
                submodule_path="sub",
                branch="main",
            ),
        )

    before = keys()
    monkeypatch.setattr(repo_shapes, "_SHAPE_BUILDER_VERSION", "2")
    after = keys()

    assert len(set(before)) == 3, "the three families must not collide"
    for family, old, new in zip(("one-commit", "two-commit", "submodule"), before, after):
        assert old != new, family
