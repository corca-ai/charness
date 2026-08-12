#!/usr/bin/env python3
"""Verify recorded external-tool observations under `charness-artifacts/quality/fixtures/`.

Each fixture pins a command, a tool version/commit, an exit code, and digests of the
captured streams. This checks that the fixture is internally consistent with the streams
it checked in beside itself.

It deliberately does NOT re-run the external tool, and it does NOT claim the repo routes
that tool to a verdict. A fixture whose `final_consumer` is null is recorded evidence with
no executable reader; that gap belongs to the issue that owns the tool, not here.

Refusals, each for an escape that was observed rather than imagined:

- `digest_malformed`: `awiki-0.5.0-docs-lint.json` shipped a 62-character
  `stderr_sha256` -- the empty-stream digest with two characters dropped in
  transcription. A digest that is never compared is also never checked for being a
  digest, so the corruption sat in checked-in evidence unread.
- `digest without path`: a fixture that declares `stdout_sha256` but no readable
  `stdout_path` used to pass vacuously, because the comparison short-circuited on the
  absent key. That is one field away from turning the whole check off.
- `path without digest`: the MIRROR of the above, and the same shape as this slice's
  own root cause -- a rewrite that drops one key. A fixture naming a stream file but no
  digest leaves that file unpinned while the run still prints `Verified`. Found by the
  round-2 bounded review of the repair that closed the first direction.
- `path escapes the fixture directory`: `stdout_path` comes from a file under review, so
  it is untrusted. `repo_root / "/tmp/out"` is `/tmp/out`, and `../` escapes upward --
  either would let a fixture "verify" against a file nobody reviewed.
  `scripts/issue_source_freeze_lib.py` already refuses this for the same reason on the
  same kind of input; this is that idiom, applied here.
- `digest_drift`: the stream file no longer hashes to what the fixture recorded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

FIXTURE_DIR = Path("charness-artifacts/quality/fixtures")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
STREAMS = ("stdout", "stderr")
REQUIRED_RECORD_FIELDS = ("tool", "version", "command", "exit_code", "final_consumer", "non_claim")


def _contained(repo_root: Path, stream_rel: object) -> Path | None:
    """Resolve a fixture-declared stream path, or None if it leaves the fixture directory.

    The path is read out of a file under review, so it is untrusted: `repo_root / "/tmp/x"`
    silently becomes `/tmp/x`, and `../` climbs out. A fixture must verify against the
    stream it checked in beside itself, not against whatever the machine happens to hold.
    """
    if not isinstance(stream_rel, str) or not stream_rel:
        return None
    root = (repo_root / FIXTURE_DIR).resolve()
    candidate = (repo_root / stream_rel).resolve()
    return candidate if candidate == root or root in candidate.parents else None


def _record_problems(payload: dict[str, object], rel: str) -> list[str]:
    problems: list[str] = []
    for field in REQUIRED_RECORD_FIELDS:
        value = payload.get(field)
        if field == "exit_code":
            valid = isinstance(value, int) and not isinstance(value, bool)
        elif field == "final_consumer":
            valid = value is None or (isinstance(value, str) and bool(value.strip()))
        else:
            valid = isinstance(value, str) and bool(value.strip())
        if not valid:
            problems.append(f"{rel}: required observation field {field!r} is missing or invalid")
    return problems


def _problems(repo_root: Path, fixture: Path) -> list[str]:
    found: list[str] = []
    rel = fixture.relative_to(repo_root).as_posix()
    try:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"{rel}: unreadable fixture JSON: {exc}"]
    if not isinstance(payload, dict):
        return [f"{rel}: expected a JSON object"]
    found.extend(_record_problems(payload, rel))

    for stream in STREAMS:
        digest_key = f"{stream}_sha256"
        path_key = f"{stream}_path"
        recorded = payload.get(digest_key)
        stream_rel = payload.get(path_key)
        if recorded is None:
            # A fixture that records no stream is fine. One that names a stream file and
            # no digest leaves that file unpinned, which is the mirror of the vacuous skip.
            if stream_rel:
                found.append(f"{rel}: {path_key} is set but {digest_key} is absent, so nothing pins it")
            continue
        if not isinstance(recorded, str) or SHA256_RE.fullmatch(recorded) is None:
            found.append(
                f"{rel}: {digest_key} is not 64 lowercase hex characters ({recorded!r})"
            )
            continue
        if not stream_rel:
            # An empty stream needs no file, but the digest must then BE the empty digest.
            if recorded != hashlib.sha256(b"").hexdigest():
                found.append(
                    f"{rel}: {digest_key} records content but {path_key} is absent, so nothing proves it"
                )
            continue
        contained = _contained(repo_root, stream_rel)
        if contained is None:
            found.append(f"{rel}: {path_key} {stream_rel} escapes {FIXTURE_DIR}")
            continue
        if not contained.is_file():
            found.append(f"{rel}: {path_key} {stream_rel} does not exist")
            continue
        actual = hashlib.sha256(contained.read_bytes()).hexdigest()
        if actual != recorded:
            found.append(f"{rel}: {digest_key} drift -- recorded {recorded}, {stream_rel} hashes to {actual}")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    fixtures = sorted((repo_root / FIXTURE_DIR).rglob("*.json"))
    if not fixtures:
        print(
            f"FAIL check_quality_tool_fixtures: no fixtures under {FIXTURE_DIR}; "
            "the checked-in evidence contract would otherwise be unproven.",
            file=sys.stderr,
        )
        return 1

    problems = [problem for fixture in fixtures for problem in _problems(repo_root, fixture)]
    for problem in problems:
        print(f"FAIL {problem}", file=sys.stderr)
    if problems:
        print(f"FAIL check_quality_tool_fixtures: {len(problems)} problem(s)", file=sys.stderr)
        return 1
    print(f"Verified {len(fixtures)} quality tool fixture(s) against their captured streams.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
