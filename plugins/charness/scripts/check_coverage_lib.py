from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from unittest import mock

UNFLOORED_MIN_STATEMENTS = 30
UNFLOORED_FAIL_BELOW = 0.80
UNFLOORED_WARN_BELOW = 0.95


class FakeUrlResponse:
    def __init__(self, payload: dict[str, object] | str) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeUrlResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        if isinstance(self.payload, str):
            return self.payload.encode("utf-8")
        return json.dumps(self.payload).encode("utf-8")


def build_unfloored_file_inventory(files: list[dict[str, object]]) -> dict[str, object]:
    below_fail: list[dict[str, object]] = []
    warn_band: list[dict[str, object]] = []
    for item in files:
        total = int(item["total"])
        coverage = float(item["coverage"])
        if total < UNFLOORED_MIN_STATEMENTS:
            continue
        candidate = {
            "path": item["path"],
            "covered": item["covered"],
            "total": total,
            "coverage": coverage,
        }
        if coverage < UNFLOORED_FAIL_BELOW:
            below_fail.append(candidate)
        elif coverage < UNFLOORED_WARN_BELOW:
            warn_band.append(candidate)
    return {
        "status": "advisory",
        "relationship": "aggregate-floor-only",
        "min_statements_threshold": UNFLOORED_MIN_STATEMENTS,
        "fail_below": UNFLOORED_FAIL_BELOW,
        "warn_below": UNFLOORED_WARN_BELOW,
        "below_fail": below_fail,
        "warn_band": warn_band,
    }


def exercise_upstream_release_scenarios() -> None:
    import scripts.upstream_release_lib as upstream

    def ok_urlopen(_request: urllib.request.Request, *, timeout: int) -> FakeUrlResponse:
        if timeout != 10:
            raise AssertionError("unexpected release probe timeout")
        return FakeUrlResponse({"tag_name": "v9.9.9", "assets": []})

    class FailedGh:
        returncode = 1
        stdout = ""
        stderr = "not authenticated"

    release_env = {
        "CHARNESS_RELEASE_PROBE_FIXTURES": "",
        "CHARNESS_RELEASE_PROBE_NO_GH": "",
        "GH_TOKEN": "",
        "GITHUB_TOKEN": "",
    }
    with mock.patch.dict(os.environ, release_env, clear=False):
        with mock.patch.object(upstream.shutil, "which", return_value=None):
            with mock.patch.object(upstream.urllib.request, "urlopen", ok_urlopen):
                upstream.probe_github_release("example/no-gh")
        with mock.patch.object(upstream.shutil, "which", return_value="/usr/bin/gh"):
            with mock.patch.object(upstream.subprocess, "run", return_value=FailedGh()):
                with mock.patch.object(upstream.urllib.request, "urlopen", ok_urlopen):
                    upstream.probe_github_release("example/failed-gh")
        with mock.patch.object(upstream.shutil, "which", return_value=None):
            for code in (403, 500):

                def http_error_urlopen(
                    request: urllib.request.Request,
                    *,
                    timeout: int,
                    code: int = code,
                ) -> FakeUrlResponse:
                    raise urllib.error.HTTPError(
                        request.full_url,
                        code,
                        "error",
                        hdrs=None,
                        fp=None,
                    )

                with mock.patch.object(upstream.urllib.request, "urlopen", http_error_urlopen):
                    upstream.probe_github_release(f"example/http-{code}")

            def invalid_json_urlopen(
                _request: urllib.request.Request,
                *,
                timeout: int,
            ) -> FakeUrlResponse:
                return FakeUrlResponse("{not-json")

            with mock.patch.object(upstream.urllib.request, "urlopen", invalid_json_urlopen):
                upstream.probe_github_release("example/invalid-json")

            def malformed_urlopen(
                _request: urllib.request.Request,
                *,
                timeout: int,
            ) -> FakeUrlResponse:
                return FakeUrlResponse("[]")

            with mock.patch.object(upstream.urllib.request, "urlopen", malformed_urlopen):
                upstream.probe_github_release("example/malformed")
