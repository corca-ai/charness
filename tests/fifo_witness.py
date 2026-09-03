"""A FIFO a controlled child holds open, so a test can BLOCK on the child's life.

The wall-clock census (#779) found the same three shapes over and over: a
`time.sleep` standing in for "the child has started by now", a `time.monotonic`
deadline polling for a marker the child could have signalled, and a sleep before
"the grandchild is dead by now". Each passes on the machine that wrote it and
fails on a loaded runner, or passes vacuously when the child never got as far as
the marker. The operator's rule (2026-09-03) is that such a test is rewritten to
an observation the test itself forces, never retried, widened, or deselected.

This is that observation. The test creates a FIFO and opens its read end
non-blocking, so the open returns before any writer exists. The controlled child
opens the write end, writes one line when it has reached the state the test
cares about, and keeps the descriptor open for as long as it lives (its own
children inherit it). Two blocking reads then answer the two questions a sleep
used to guess at:

- `wait_line()` blocks until the child has written a whole line: the child IS
  running and HAS reached that point. A sleep-then-check becomes a read.
- `wait_eof()` blocks until no process holds the write end: every holder has
  exited or closed it. "The grandchild is dead" becomes EOF, which the kernel
  reports exactly when it is true and never earlier.

Neither read takes a timeout. A child that never reaches the line, or a tree
that outlives the kill it was supposed to die from, blocks the test until the
standing runner's own budget ends it -- the runner's budget is the only bound,
and it names the test that hung. That is the trade the operator chose: a hang
with a name over a green that depended on the scheduler.

Linux FIFO semantics this relies on, stated because they are load-bearing: a
reader opened before any writer sees no hang-up until a writer has connected at
least once, so `wait_eof()` before `wait_line()` (or `has_line()`) would block
forever on a child that never opened the FIFO. Call `wait_eof()` only after a
line proved a writer connected. `has_line()` is the non-blocking peek for a
controlled clock: a fake `time.monotonic` that advances past the budget only
once the child has signalled turns a timeout test into a forced observation.
"""

from __future__ import annotations

import os
import select
from pathlib import Path

_CHUNK = 65536


class FifoWitness:
    """One FIFO, opened for non-blocking read before the child exists."""

    def __init__(self, path: Path) -> None:
        self.path = path
        os.mkfifo(path)
        self.fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        self._buffer = b""
        self._eof = False

    def __enter__(self) -> FifoWitness:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1

    # -- observations ---------------------------------------------------------

    def has_line(self) -> bool:
        """Non-blocking: has the child written a whole line yet?"""
        if b"\n" not in self._buffer:
            self._pump(block=False)
        return b"\n" in self._buffer

    def wait_line(self, *, abort_fds: tuple[int, ...] = ()) -> str:
        """Block until one whole line has arrived, and return it without its newline.

        `abort_fds` are descriptors whose readability means the wait can never
        succeed -- typically the child's own stdout pipe, which becomes readable
        at its EOF when the child exits without ever reaching the line. The
        AssertionError names the descriptor so the caller can attach the child's
        output instead of reporting a bare hang.
        """
        while b"\n" not in self._buffer:
            if self._eof:
                raise AssertionError(
                    f"{self.path}: every writer closed before a whole line arrived; "
                    f"received {self._buffer!r}"
                )
            ready, _, _ = select.select([self.fd, *abort_fds], [], [])
            if self.fd not in ready:
                raise AssertionError(
                    f"{self.path}: descriptor(s) {sorted(set(ready))} became readable "
                    "before the witness line arrived"
                )
            self._pump(block=False)
        line, _, self._buffer = self._buffer.partition(b"\n")
        return line.decode("utf-8", errors="replace")

    def wait_eof(self) -> bytes:
        """Block until no process holds the write end; return whatever was left unread.

        Only meaningful after `wait_line()` or a true `has_line()` proved a writer
        connected (see the module docstring for why).
        """
        while not self._eof:
            select.select([self.fd], [], [])
            self._pump(block=False)
        return self._buffer

    # -- plumbing ---------------------------------------------------------------

    def _pump(self, *, block: bool) -> None:
        if block:
            select.select([self.fd], [], [])
        else:
            ready, _, _ = select.select([self.fd], [], [], 0)
            if not ready:
                return
        try:
            chunk = os.read(self.fd, _CHUNK)
        except BlockingIOError:
            return
        if chunk == b"":
            self._eof = True
            return
        self._buffer += chunk


def holder_snippet(witness_path: Path, line: str, *, variable: str = "_witness") -> str:
    """Python source for a controlled child: open the write end, write `line`, keep it open.

    The descriptor is bound to a module-level name so it lives as long as the
    child does and is inherited by anything the child spawns afterwards.
    """
    return (
        f"{variable} = open({str(witness_path)!r}, 'w')\n"
        f"{variable}.write({line + chr(10)!r})\n"
        f"{variable}.flush()\n"
    )


def shell_holder_snippet(witness_path: Path, line: str, *, fd: int = 3) -> str:
    """Shell source for a controlled child: the same three steps for `bash -c` bodies.

    Run it BEFORE forking any background job so the job inherits descriptor `fd`
    and `wait_eof()` covers the whole tree.
    """
    return f"exec {fd}>{witness_path}; printf '%s\\n' '{line}' >&{fd}"
