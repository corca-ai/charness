# Existing-script to CLI consumer packet

This packet is a small, dependency-free consumer repository for the Goal 798
create-cli journey. The `seed/` directory is the unchanged starting repo;
the prompts describe the CLI contract and its implementation handoff.

The seed contains two useful existing scripts and their standard-library
tests. It intentionally contains no `repoctl` candidate or candidate result.
The parent's observer owns acceptance and comparative results.

Run the seed from its root with:

```text
python3 -m unittest discover -s tests -v
```

An isolated task lane may be invoked with `task run --skip-prepare`. The seed
uses only the Python standard library and does not copy Charness skills into
the consumer repository.

Packet contents:

- `seed/` — baseline consumer files and tests.
- `prompts/create-cli.md` — the installed `create-cli` handoff.
- `prompts/impl.md` — the installed `impl` handoff.
