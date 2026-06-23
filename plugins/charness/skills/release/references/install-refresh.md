# Install Refresh

Release work should tell operators how to refresh installed state without
guessing host-specific steps.

## Operator Update Instructions

When the adapter declares `update_instructions`, treat them as the canonical
operator-facing refresh path for already published installs.

Keep update instructions user-meaningful. Avoid host-internal compatibility
detail unless operators need it to complete the update.

## Maintainer Dev-Machine Refresh

When the adapter declares `post_publish_install_refresh`, treat that adapter
value as the maintainer-machine refresh command. The public skill does not know
the command name; the repo adapter owns it.

```yaml
post_publish_install_refresh: <repo-owned update command>
```

After public release verification, `publish_release.py` auto-runs this command
on the maintainer machine and records the result under `install_refresh`.

The command is opt-in per repo, non-blocking after publication, timeout bounded,
and recorded as `refreshed`, `failed`, or `not_configured`. A failed refresh is
an open risk, not a reason to pretend the already-published release did not
happen.

## Why It Exists

The maintainer's installed plugin can otherwise lag the repo and cause scaffolds
or validators to cite an older installed copy. Keeping the installed surface
aligned after release closes that version-skew class.
