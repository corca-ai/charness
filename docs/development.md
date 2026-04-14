# charness Development Paths

This document collects development-only and proof-only `charness` flows.

These paths are useful when you are changing this repo itself, validating a
packaging change before push, or exercising a host-specific edge case without
mutating the installed CLI source of truth.

They are not the operator install contract. For supported installation and
refresh guidance, use [INSTALL.md](../INSTALL.md).

## Repo-Local Dogfood

If you changed this checkout locally and want the installed host surface to
exercise those unpushed edits, update from this repo without pulling:

```bash
charness update --repo-root . --no-pull --skip-cli-install
```

Use this when the managed checkout already contains the exact source you want
to dogfood and an implicit `git pull --ff-only` would be wrong. This is a
proof-only path: it updates the host-visible plugin surface from the working
tree, but keeps the installed CLI pinned to the managed checkout.

If you need to refresh the installed CLI itself, run the managed checkout
entrypoint directly:

```bash
~/.agents/src/charness/charness update
```

After a release or normal operator cycle, go back to the default managed flow:

```bash
charness update
```

## Proof-Only Non-Managed Checkout

If you deliberately want to prove install behavior from a non-managed checkout,
keep it explicitly read-only with respect to the installed CLI source:

```bash
./charness init --repo-root /absolute/path/to/charness --skip-cli-install
```

This is for development or packaging proof only. The installed CLI should still
resolve back to `~/.agents/src/charness`.

## Host-Specific Proof Paths

- Claude fallback proof may still use `claude --plugin-dir /absolute/path/to/charness/plugins/charness`,
  but that is not the primary install path once `charness init` manages the
  host install.
- Codex local development may point the checked-in marketplace file at
  `./plugins/charness` when proving packaging behavior inside this repo.

Keep any proof-only host route out of operator docs unless it becomes a
maintained, first-class install contract.
