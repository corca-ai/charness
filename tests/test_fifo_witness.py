"""The FIFO witness proves a child's life without a clock; prove the witness itself."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.fifo_witness import FifoWitness, holder_snippet, shell_holder_snippet

pytestmark = pytest.mark.boundary_contract(
    reason="these tests spawn real children and block on their descriptors"
)


def test_wait_line_blocks_until_the_child_reaches_the_line_and_eof_until_it_dies(tmp_path: Path) -> None:
    with FifoWitness(tmp_path / "witness") as witness:
        assert not witness.has_line(), "no writer has connected yet"
        child = subprocess.Popen(
            [
                sys.executable,
                "-c",
                holder_snippet(witness.path, "reached")
                # Block on stdin, not on a clock: the test decides when the child dies.
                + "import sys\nsys.stdin.read()\n",
            ],
            stdin=subprocess.PIPE,
        )
        try:
            assert witness.wait_line() == "reached"
            assert child.poll() is None, "the line arrived from a live child"
            child.stdin.close()
            child.wait(timeout=30)
            assert witness.wait_eof() == b""
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=10)


def test_eof_waits_for_the_grandchild_that_inherited_the_descriptor(tmp_path: Path) -> None:
    """A dead child is not a dead tree: EOF arrives only when the LAST holder is gone."""
    with FifoWitness(tmp_path / "witness") as witness:
        # bash forks a background grandchild that inherits fd 3, then the shell exits.
        # Both stdin reads use the SAME pipe: the grandchild lives until the test
        # closes it, and by then its parent shell has long since exited.
        child = subprocess.Popen(
            [
                "/bin/bash",
                "-c",
                shell_holder_snippet(witness.path, "tree-up") + "; (read -r _line) & exit 0",
            ],
            stdin=subprocess.PIPE,
        )
        try:
            assert witness.wait_line() == "tree-up"
            child.wait(timeout=30)
            assert child.returncode == 0, "the direct child exited on its own"
            assert not witness.has_line()
            child.stdin.close()
            assert witness.wait_eof() == b""
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=10)


def test_wait_line_names_an_abort_descriptor_instead_of_hanging(tmp_path: Path) -> None:
    with FifoWitness(tmp_path / "witness") as witness:
        child = subprocess.Popen([sys.executable, "-c", "raise SystemExit(0)"], stdout=subprocess.PIPE)
        try:
            with pytest.raises(AssertionError, match="became readable before the witness line"):
                witness.wait_line(abort_fds=(child.stdout.fileno(),))
        finally:
            child.wait(timeout=30)


def test_a_writer_that_closes_without_a_line_is_a_named_failure(tmp_path: Path) -> None:
    with FifoWitness(tmp_path / "witness") as witness:
        writer = os.open(witness.path, os.O_WRONLY)
        os.write(writer, b"half")
        os.close(writer)
        with pytest.raises(AssertionError, match="every writer closed before a whole line"):
            witness.wait_line()
