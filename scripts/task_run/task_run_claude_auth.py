"""Ephemeral parent-side Anthropic auth; real credentials never enter a lane."""

from __future__ import annotations

import contextlib
import http.client
import http.server
import secrets
import threading
from typing import Iterator

from scripts.task_run.task_run_contract import TaskRunError


@contextlib.contextmanager
def claude_auth_proxy(env: dict[str, str]) -> Iterator[dict[str, str]]:
    """Keep real auth outside the agent's PID namespace, files and environment.

    Only a fixed Anthropic HTTPS upstream is reachable through this proxy. It
    never logs request/response bodies or headers. Claude receives a disposable
    placeholder; arbitrary tools and /proc reads cannot recover the real token.
    """
    child_env = dict(env)
    auth = next(((name, child_env.get(name)) for name in
                 ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
                 if child_env.get(name)), None)
    for name in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        child_env.pop(name, None)
    if auth is None:
        raise TaskRunError("Claude executor requires local API or OAuth authentication")
    name, token = auth
    placeholder = secrets.token_urlsafe(32)
    child_env[name] = placeholder
    header = "x-api-key" if name == "ANTHROPIC_API_KEY" else "Authorization"
    value = token if header == "x-api-key" else f"Bearer {token}"
    expected = placeholder if header == "x-api-key" else f"Bearer {placeholder}"
    handler = _auth_proxy_handler(header, value, expected)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    child_env["ANTHROPIC_BASE_URL"] = f"http://127.0.0.1:{server.server_port}"
    try:
        yield child_env
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


def _auth_proxy_handler(auth_header: str, auth_value: str, expected: str) -> type[http.server.BaseHTTPRequestHandler]:
    class AuthProxyHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, _format: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            self._forward()

        def do_POST(self) -> None:
            self._forward()

        def _forward(self) -> None:
            if not secrets.compare_digest(self.headers.get(auth_header, ""), expected):
                self.send_error(403, "Invocation authentication required")
                return
            if not self.path.startswith("/") or self.path.startswith("//"):
                self.send_error(400, "Invalid API path")
                return
            headers = {key: value for key, value in self.headers.items()
                       if key.lower() not in ("host", "authorization", "x-api-key", "connection", "transfer-encoding")}
            headers[auth_header] = auth_value
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            upstream = http.client.HTTPSConnection("api.anthropic.com", timeout=300)
            try:
                upstream.request(self.command, self.path, body=body, headers=headers)
                response = upstream.getresponse()
                self.send_response(response.status)
                for key, value in response.getheaders():
                    if key.lower() not in ("connection", "transfer-encoding", "authorization", "x-api-key", "proxy-authenticate", "www-authenticate", "set-cookie"):
                        self.send_header(key, value)
                self.send_header("Connection", "close")
                self.end_headers()
                while chunk := response.read1(65536):
                    self.wfile.write(chunk)
                    self.wfile.flush()
            except (OSError, http.client.HTTPException):
                # Never expose exception text: request headers can contain auth.
                self.close_connection = True
            finally:
                upstream.close()
    return AuthProxyHandler
