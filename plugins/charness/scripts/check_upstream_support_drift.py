#!/usr/bin/env python3

"""Online preflight: confirm every `support_skill_source.path` in
`integrations/tools/*.json` still exists at its pinned `ref` in the declared
`upstream_repo`. This is the root-cause prevention for corca-ai/cautilus#32:
the v0.14.2 pin masks the symptom, but a maintainer who bumps `ref` to a
sibling release where the path moved would silently regress support sync.

This is not a standing local gate. Run it from a CI nightly workflow or
`charness update doctor`-style flow that already requires network access.
Probe-blocked outcomes (no `gh` on PATH, no token, network error) report as
`skipped` and exit 0 — actual path-missing drift is the only fail signal.

For test isolation, set `CHARNESS_UPSTREAM_SUPPORT_PROBE_FIXTURES=<path>` to a
JSON mapping `"<owner>/<repo>:<ref>:<path>"` to one of `"exists"`, `"missing"`,
or `"error:<reason>"`.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
GITHUB_CONTENTS_TEMPLATE = "https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
PROBE_TIMEOUT_SECONDS = 10


def _fixture_lookup(repo: str, ref: str, path: str) -> str | None:
    fixture_path = os.environ.get("CHARNESS_UPSTREAM_SUPPORT_PROBE_FIXTURES")
    if not fixture_path:
        return None
    data = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    key = f"{repo}:{ref}:{path}"
    value = data.get(key)
    return value if isinstance(value, str) else None


def _gh_probe(repo: str, ref: str, path: str) -> dict[str, Any] | None:
    if os.environ.get("CHARNESS_UPSTREAM_SUPPORT_PROBE_NO_GH") == "1":
        return None
    if shutil.which("gh") is None:
        return None
    api_path = f"/repos/{repo}/contents/{urllib.parse.quote(path)}?ref={urllib.parse.quote(ref)}"
    try:
        # subprocess.run inherits the parent env so gh's own keyring auth
        # (`gh auth status`) and GH_TOKEN/GITHUB_TOKEN both flow through.
        completed = subprocess.run(
            ["gh", "api", api_path],
            check=False,
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return {"status": "error", "reason": "gh-timeout", "error": str(exc)}
    if completed.returncode == 0:
        return {"status": "exists"}
    # gh 2.x emits stderr like `gh: Not Found (HTTP 404)` for missing paths and
    # `gh: HTTP 403: ...` for rate-limit or auth issues. If the stderr shape
    # changes upstream, the script downgrades drift to `gh-failed` — bump the
    # matcher when bumping the gh version contract.
    stderr = completed.stderr or ""
    if "404" in stderr or "Not Found" in stderr:
        return {"status": "missing"}
    if "403" in stderr or "Forbidden" in stderr:
        return {"status": "error", "reason": "gh-forbidden", "error": stderr.strip()}
    return {"status": "error", "reason": "gh-failed", "error": stderr.strip()}


def _urllib_probe(repo: str, ref: str, path: str) -> dict[str, Any]:
    url = GITHUB_CONTENTS_TEMPLATE.format(
        repo=repo,
        path=urllib.parse.quote(path),
        ref=urllib.parse.quote(ref),
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "charness-upstream-support-probe",
    }
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=PROBE_TIMEOUT_SECONDS) as response:
            response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"status": "missing"}
        if exc.code == 403:
            return {"status": "error", "reason": "github-forbidden", "error": f"http {exc.code}"}
        return {"status": "error", "reason": f"github-http-{exc.code}", "error": f"http {exc.code}"}
    except (TimeoutError, urllib.error.URLError) as exc:
        return {"status": "error", "reason": "github-network-error", "error": str(exc)}
    return {"status": "exists"}


def probe_path(repo: str, ref: str, path: str) -> dict[str, Any]:
    fixture = _fixture_lookup(repo, ref, path)
    if fixture is not None:
        if fixture == "exists":
            return {"status": "exists"}
        if fixture == "missing":
            return {"status": "missing"}
        if fixture.startswith("error:"):
            return {"status": "error", "reason": fixture.split(":", 1)[1] or "fixture-error", "error": fixture}
        return {"status": "error", "reason": "fixture-unknown", "error": fixture}
    gh_result = _gh_probe(repo, ref, path)
    if gh_result is not None:
        return gh_result
    return _urllib_probe(repo, ref, path)


def collect_targets(repo_root: Path) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for manifest_path in sorted((repo_root / "integrations" / "tools").glob("*.json")):
        if manifest_path.name in {"manifest.schema.json", "dependencies.json", "dependencies.schema.json"}:
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        source = manifest.get("support_skill_source")
        if not isinstance(source, dict):
            continue
        if source.get("source_type") != "upstream_repo":
            continue
        upstream = manifest.get("upstream_repo")
        path = source.get("path")
        ref = source.get("ref")
        # manifest.schema.json only enforces upstream_repo as a non-empty string,
        # so reject anything that is not exactly `owner/repo`. Without this guard
        # `a/b/c` would 404 and surface as a false-positive drift.
        if not isinstance(upstream, str) or upstream.count("/") != 1:
            continue
        if not isinstance(path, str) or not path:
            continue
        if not isinstance(ref, str) or not ref:
            continue
        targets.append(
            {
                "tool_id": manifest.get("tool_id"),
                "manifest_path": manifest_path.relative_to(repo_root).as_posix(),
                "upstream_repo": upstream,
                "ref": ref,
                "path": path,
            }
        )
    return targets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable JSON report.")
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    targets = collect_targets(repo_root)
    results: list[dict[str, Any]] = []
    drift_count = 0
    for target in targets:
        probe = probe_path(target["upstream_repo"], target["ref"], target["path"])
        record = {**target, **probe}
        results.append(record)
        if probe["status"] == "missing":
            drift_count += 1
    payload = {
        "schema_version": 1,
        "checked": results,
        "drift_count": drift_count,
        "target_count": len(targets),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for record in results:
            status = record["status"]
            label = {
                "exists": "ok",
                "missing": "DRIFT",
                "error": f"skipped ({record.get('reason', 'unknown')})",
            }.get(status, status)
            print(
                f"{label}: {record['tool_id']} -> {record['upstream_repo']}@{record['ref']}:{record['path']}"
            )
        print(f"{drift_count} drift / {len(targets)} checked")
    return 1 if drift_count else 0


if __name__ == "__main__":
    sys.exit(main())
