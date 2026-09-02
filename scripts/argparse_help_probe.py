"""Cached, batched ``<command> --help`` probes, for the gates that read argparse back.

Two gates ask argparse what it declares rather than trusting a literal:
`check_documented_command_flags.py` (does this script accept this flag) and
`check_documented_subcommands.py` (does this CLI have this subcommand). Both need
the same machinery underneath -- run `--help` at a subparser path, cache it, batch
one round per depth so the walk down the tree costs rounds instead of processes,
and refuse to answer from a probe that did not exit clean.

Keyed on the WHOLE argv tuple, so `("scripts/adapter.py", "resolve")` and
`("charness", "tool", "install")` are the same kind of key. That is what lets one
probe serve both callers: neither owns a notion of "the script" separate from
"the path", they just have different first elements.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

from runtime_bootstrap import import_repo_module

_argparse_surface = import_repo_module(__file__, "scripts.argparse_surface_lib")
_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_processes_in_order = _subprocess_guard.run_processes_in_order

# argparse wraps to the terminal width, and a wrapped line can put an option name
# or a choice list out of reach of a line-oriented scanner.
HELP_COLUMNS = "200"
# Every argparse section title and `usage:` prefix goes through `gettext`.
# `accepted_options` keys on `usage:` and on the option-row shape, so under a
# locale with an argparse catalog installed it reads NOTHING and every documented
# flag reports missing at once -- a repo-wide false red that depends on the
# machine, not on the code. Pinned here beside COLUMNS because both are the same
# kind of fact: the probe owns the rendering its readers parse.
HELP_LOCALE_ENV = {"LC_ALL": "C", "LANGUAGE": ""}
PROBE_TIMEOUT_SECONDS = 120
HelpRunner = Callable[..., list[object]]


class HelpProbe:
    """``--help`` results for a set of argv prefixes, primed in batched rounds."""

    def __init__(
        self,
        root: Path,
        *,
        interpreter: str = "python3",
        runner: HelpRunner | None = None,
    ) -> None:
        self._root = root
        self._interpreter = interpreter
        self._runner = runner or run_processes_in_order
        self._results: dict[tuple[str, ...], object] = {}

    def prime(self, targets: set[tuple[str, ...]]) -> None:
        """Run every not-yet-probed argv prefix, in parallel, in one round."""
        pending = sorted(targets - self._results.keys())
        if not pending:
            return
        env = dict(os.environ, COLUMNS=HELP_COLUMNS, **HELP_LOCALE_ENV)
        commands = [[self._interpreter, *target, "--help"] for target in pending]
        results = self._runner(
            commands,
            cwd=self._root,
            env=env,
            timeout_seconds=PROBE_TIMEOUT_SECONDS,
        )
        self._results.update(zip(pending, results, strict=True))

    def result(self, target: tuple[str, ...]):
        return self._results[target]

    def probed_clean(self, target: tuple[str, ...]) -> bool:
        """Whether this target produced readable help.

        Callers need this because `_clean_text` collapses "not primed yet" and
        "exited non-zero" into the same answer -- correct for a walk that
        descends one level per round, and a false green for a caller that reads
        the resulting empty set as "this parser has no subcommands". A gate that
        cannot tell those apart reports a leaf where the probe actually broke.
        """
        result = self._results.get(target)
        return result is not None and result.returncode == 0

    def clean_count(self) -> int:
        """Probes that produced readable help.

        `count()` includes failures, so a receipt built on it over-claims in the
        same breath as it under-checks.
        """
        return sum(1 for target in self._results if self.probed_clean(target))

    def text(self, target: tuple[str, ...]) -> str:
        result = self.result(target)
        return result.stdout + result.stderr

    def _clean_text(self, target: tuple[str, ...]) -> str | None:
        """Help text, or None when this target has not probed clean.

        An unprobed depth and a non-zero exit are the same answer to every reader
        below: nothing derivable here. That is what makes a walk descend exactly
        one level per round -- the next round primes what this one revealed --
        and it is what keeps a broken parser from having children invented for
        it.
        """
        result = self._results.get(target)
        return None if result is None or result.returncode != 0 else self.text(target)

    def _read(self, target: tuple[str, ...], reader) -> set[str]:
        text = self._clean_text(target)
        return reader(text) if text is not None else set()

    def accepted_options(self, target: tuple[str, ...]) -> set[str]:
        return self._read(target, _argparse_surface.accepted_options)

    def options_with_values(self, target: tuple[str, ...]) -> set[str]:
        return self._read(target, _argparse_surface.options_with_values)

    def subcommand_choices(self, target: tuple[str, ...]) -> set[str]:
        return self._read(target, _argparse_surface.subcommand_choices)

    def count(self) -> int:
        return len(self._results)
