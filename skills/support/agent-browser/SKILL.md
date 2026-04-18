---
name: agent-browser
description: "Use agent-browser CLI for browser automation, JS-rendered pages, and interactive browser debugging. Prefer this when a direct URL needs real browser execution or when you must inspect live DOM state."
---

# Agent Browser

Use this skill when plain HTTP fetch is not enough.

- JS-rendered pages
- interactive browser debugging
- DOM inspection
- click/fill/wait workflows
- screenshots or browser evidence

When the caller is `gather`, treat this as a browser runtime seam rather than a
public workflow concept:

- prefer official API/export paths before browser fallback
- use this runtime when a private SaaS URL or stable UI path still needs real
  browser execution
- preserve which auth/bootstrap mode made the acquisition possible
- stop cleanly when browser auth/bootstrap is still missing

## Runtime

This skill depends on the `agent-browser` CLI and a local Chromium executable.

The runtime installs Chromium via skill-owned `apk-packages.txt`.

If the browser still is not ready yet, run:

```bash
AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/chromium-browser agent-browser open https://example.com
```

For private SaaS gather flows, read `references/auth-bootstrap.md` before
assuming local profile reuse, saved state, or headed bootstrap mean the same
thing on every host.

## Core Workflow

1. Open the page.
2. Wait for the page to settle.
3. Inspect with snapshot or extract with `get` / `eval`.
4. Re-snapshot after DOM changes.
5. Close the browser session when done.

Example:

```bash
AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/chromium-browser agent-browser open https://example.com
AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/chromium-browser agent-browser wait --load networkidle
AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/chromium-browser agent-browser snapshot -i
AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/chromium-browser agent-browser eval "document.body.innerText"
AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/chromium-browser agent-browser close
```

## Notes

- Prefer `web-fetch` for ordinary public URL reading.
- Use this skill when `web-fetch` returns thin content, or when the page clearly needs a real browser.
- For debugging a failing page fetch, capture a screenshot and inspect the live DOM.
- For `gather`, use this only after stronger official acquisition paths were
  checked first.
- Do not treat a local desktop Chrome profile as equivalent to a remote
  headless runner; some flows need one-time manual or headed bootstrap before
  later headless reuse is honest.

## References

- `references/runtime.md`
- `references/auth-bootstrap.md`
