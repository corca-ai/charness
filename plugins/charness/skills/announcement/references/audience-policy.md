# Audience Policy

Audience tags are optional and adapter-driven.

Good portable tags are things like:

- `user`
- `operator`
- `developer`

The resolver should distinguish:

- `unset`
- `explicit-empty`
- `configured`

When tags are `unset`, propose likely candidates with evidence.

When tags are explicitly empty, do not keep re-proposing them.
