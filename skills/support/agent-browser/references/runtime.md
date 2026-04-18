# Runtime Notes

The checked-in runtime hints for this support skill are:

- `runtime/npm-global-packages.txt` for the CLI package name
- `runtime/apk-packages.txt` for the Chromium package expected in minimal Linux environments

If the host already has a working browser runtime, prefer that over re-installing packages ad hoc.

For `gather`-driven private SaaS acquisition, this runtime is the browser
execution boundary only. The public decision ladder stays in `gather`; this
support seam should not silently replace official API/export paths.
