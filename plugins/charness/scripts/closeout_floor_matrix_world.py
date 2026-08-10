#!/usr/bin/env python3
"""The hermetic world the closeout floor matrix probes run inside.

Split from `closeout_floor_matrix_lib` on a real seam: this file answers "what does a
closeout carrier run against", while the sibling answers "what did the carrier decide".

Everything here exists to make the probe hermetic and comparable. A throwaway git
repo, because `direct-commit` reads a commit and the commit-msg hook lists a staged
index. A stubbed `gh` reached both by absolute path (adapter-declared backends) and
by PATH shim (the commit-msg carrier hardcodes `gh`), so no probe can reach GitHub.
The repo's own `AGENTS.md`, so the resolution-critique floor's delegation question is
answered the way this repo answers it rather than the way a contract-less repo would.
NOT a claim that the observer REFUSAL arm is exercised: the probe bodies bind their
critique with `Critique: blocked <signal>`, which the shared helper files under
`skipped` rather than as resolved evidence, so `fresh_eye_observer` stays None and the
refusal set is always empty. The artifact's `not_measured` says so.

ONE world for every carrier, deliberately: measuring one carrier in a different world
than the rest would make the cells incomparable, and a floor could read as inert
because its world differed rather than because the carrier skips it.
"""
from __future__ import annotations

import contextlib
import importlib.util
import json
import runpy
import subprocess
from pathlib import Path
from typing import Any

REPO = "corca-ai/charness"
NUMBER = 77
DESTINATION = 900

_GH_VIEW = ("issue", "view", "--repo", "{repo}", "{number}", "--json", "{json_fields}")


_STUB_GH = '''#!/usr/bin/env python3
"""Stub `gh` for the closeout floor matrix probe. Serves `issue view` only."""
import json, sys
from pathlib import Path

argv = sys.argv[1:]
if argv[:2] != ["issue", "view"]:
    sys.stderr.write(f"closeout-floor-matrix stub gh: unsupported argv {argv!r}\\n")
    raise SystemExit(2)
payloads = json.loads((Path(__file__).resolve().parent / "payloads.json").read_text())
number = next(part for part in argv[2:] if part.isdigit())
payload = payloads.get(number)
if payload is None:
    sys.stderr.write(f"closeout-floor-matrix stub gh: no payload for #{number}\\n")
    raise SystemExit(1)
print(json.dumps(payload))
'''


def skill_module(repo_root: Path, skill: str, name: str) -> Any:
    """Load a public-skill script the way its own package does.

    The issue package ships a sibling loader and its modules expect to be loaded
    through it; the release package resolves siblings itself from ``__file__``, so a
    plain spec load is the right entry there.
    """
    scripts = repo_root / "skills" / "public" / skill / "scripts"
    local_import = scripts / "issue_local_import.py"
    if local_import.is_file():
        return runpy.run_path(str(local_import))["sibling_loader"](str(scripts / f"{name}.py"))(name)
    spec = importlib.util.spec_from_file_location(f"cfm_{skill}_{name}", scripts / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProbeWorld:
    """A throwaway git repo plus a stubbed `gh`, shared by every probe.

    One world for all carriers on purpose: `direct-commit` needs a repo it can read a
    commit out of, and measuring one carrier in a different world than the rest would
    make the cells incomparable -- a floor could read as inert because its world
    differed, not because the carrier skips it.
    """

    def __init__(self, source_root: Path, root: Path) -> None:
        self.source_root = source_root
        self.root = root
        self.bin = root / "bin"
        self.bin.mkdir(parents=True, exist_ok=True)
        self.gh = self.bin / "gh"
        self.gh.write_text(_STUB_GH, encoding="utf-8")
        self.gh.chmod(0o755)
        self.set_destination_state("OPEN")
        # The repo CONTRACT travels into the probe world. The resolution-critique
        # floor's observer arm short-circuits on `repo_requires_delegated_observer`,
        # which reads `AGENTS.md`; without it the matrix would report what a caller in
        # a contract-less repo gets rather than what a caller HERE gets, and an
        # applicability change in that arm would be invisible to the gate.
        # `AGENTS.md` only: `repo_requires_delegated_observer` reads that file and
        # `.agents/subagent-delegation.json`, never `CLAUDE.md`, so copying the latter
        # would be inert decoration on a proof surface.
        contract = source_root / "AGENTS.md"
        if contract.is_file():
            (root / "AGENTS.md").write_text(contract.read_text(encoding="utf-8"), encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        for key, value in (("user.email", "probe@example.invalid"), ("user.name", "probe")):
            subprocess.run(["git", "-C", str(root), "config", key, value], check=True)
        # Seeded unconditionally so no carrier depends on another having run first:
        # the commit-msg hook lists `git diff --cached` and previously only had a HEAD
        # because `direct-commit` happened to be probed before it.
        subprocess.run(
            ["git", "-C", str(root), "commit", "-q", "--allow-empty", "-m", "seed probe world"],
            check=True,
        )
        self.verifier = skill_module(source_root, "issue", "issue_verify_closeout")
        self.draft = skill_module(source_root, "issue", "issue_validate_closeout_draft")
        self.closer = skill_module(source_root, "issue", "issue_close")

    @property
    def backend(self) -> dict[str, Any]:
        """An adapter-declared backend whose binary is the stub, using `gh`'s own
        template -- so the stub answers the adapter path and the PATH-shimmed
        hardcoded-`gh` path identically."""
        return {"id": "cfm-stub", "binary": str(self.gh), "commands": {"view": list(_GH_VIEW)}}

    def set_destination_state(self, state: str) -> None:
        (self.bin / "payloads.json").write_text(
            json.dumps(
                {
                    str(NUMBER): {
                        "number": NUMBER,
                        "state": "OPEN",
                        "url": f"https://github.com/{REPO}/issues/{NUMBER}",
                        "body": "The probe's own issue.",
                    },
                    str(DESTINATION): {
                        "number": DESTINATION,
                        "state": state,
                        "url": f"https://github.com/{REPO}/issues/{DESTINATION}",
                        "body": f"Umbrella issue. Absorbs #{NUMBER}.",
                    },
                }
            ),
            encoding="utf-8",
        )

    def run_backend(self, argv: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
        """The `run` callable the release lane threads into its `gh issue view`.

        Routed through the same stub the other carriers use, by absolute path, so no
        probe can reach the real backend even though this lane hardcodes `gh` in its
        argv.
        """
        return subprocess.run(
            [str(self.gh)] + list(argv[1:]), cwd=cwd or self.root,
            check=False, capture_output=True, text=True,
        )

    @contextlib.contextmanager
    def destination_closed(self):
        """Run the block with the consolidation destination CLOSED, then restore OPEN.

        A context manager rather than two `set_destination_state` calls: the restore is
        the invariant every later probe in the sweep depends on, and a manual pair is
        one early return away from leaking a CLOSED destination into unrelated cells.
        """
        self.set_destination_state("CLOSED")
        try:
            yield
        finally:
            self.set_destination_state("OPEN")

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def commit(self, message: str) -> str:
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-q", "--allow-empty", "-m", message],
            check=True,
        )
        return subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()


