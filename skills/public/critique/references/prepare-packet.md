# Critique Prepare Packet

The **critique prepare packet** is a deterministic, adapter-driven payload
that fresh-eye worker runs consume *before* broad repo sampling. It exists
to keep critique focused on judgment instead of repeatedly rediscovering
enumerable inventory (changed surfaces, adapter subscriptions, doc-link
graphs, role classifications, deferred concerns).

The packet shape is portable. Charness owns the envelope and the worker runner;
each consumer repo's `<repo-root>/.agents/critique-adapter.yaml` decides which
sections apply and how each section's content is produced. Envelope identity and
section schema are owned by `prepare_packet.py` and the reviewed-input identity
modules — copy the emitted `verify_command`, do not restate the schema here.

## When This Fires

The prepare runner fires when:

- the user (or a parent skill) asks `critique` to prepare a packet for
  the next critique pass
- the adapter declares ≥1 `packet_sections` entry (this is the opt-in
  signal — repos with no critique adapter or no declared sections see
  no behavior change)
- the runner is invoked explicitly via
  `python3 "$SKILL_DIR/scripts/prepare_packet.py" --repo-root .`

The `critique` bootstrap runs the runner before starting reviewers when the
adapter declares sections. Parent workflows may still prepare a packet earlier,
but they must pass the packet path/body through and record the consumed path
rather than silently relying on stale context.

## One-Command Operator Path

For a normal file-backed review, use the semantic wrapper instead of assembling
the packet and worker arguments by hand:

```bash
python3 "$SKILL_DIR/scripts/run_review.py" \
  --repo-root . \
  --scope "<bounded scope>" \
  --lens "<review lens>" \
  --goal-lineage-file <lineage.json> \
  --dry-run
```

Remove `--dry-run` only when the derived carrier is ready to start the review.
The wrapper owns packet verification, packet/input identities, canonical schema
materialization, the default read-only capability envelope, artifact paths,
boundary mode, Goal Run lineage, and lifecycle output. Repeatable `--hold-out
<path>` hides a named in-progress artifact from the reviewer tree for the live
run and restores it afterwards. An existing packet can be supplied
with `--packet-file <repo-relative-path>`; its current binding is verified
before a reviewer starts. The low-level `run_reviewer_worker.py` interface
remains available for compatibility and diagnostics, not as the normal manual
operator path.

## Preparing A Packet

The packet is emitted as JSON plus a markdown render under the adapter
`output_dir` (default `charness-artifacts/critique`). For committed-diff
critique, invoke the runner with `--changed-ref`:

```bash
python3 "$SKILL_DIR/scripts/prepare_packet.py" \
  --repo-root . \
  --prepared-for "HEAD" \
  --changed-ref HEAD^..HEAD
```

For the common one-commit or endpoint-range cases, use the aliases:

```bash
python3 "$SKILL_DIR/scripts/prepare_packet.py" --repo-root . --commit HEAD
python3 "$SKILL_DIR/scripts/prepare_packet.py" --repo-root . --range main..HEAD
```

Use repeatable `--reviewed-path <repo-relative-path>` arguments when the review
scope is narrower or more explicit than the changed-path default. The producer
sorts this declaration canonically and scopes fingerprints to those paths, so an
unrelated working-tree change does not invalidate the review. An explicit
`--reviewed-path` is never silently removed; if it names the packet's own
output path, the runner rejects the collision.

In committed-ref mode, the exactness check remains a hard boundary. If the
default sweep excluded a committed review artifact, preparation refuses with
the missing and unexpected paths instead of silently adding or dropping them;
use `run_review.py --reviewed-paths-file <manifest>` to declare the exact
changed-ref set.

`--commit` and `--range` are stored as pinned object ids, not the symbolic
text. `A..B` ranges are endpoint diffs: the packet records files present in the
net diff between the two endpoints, not every file touched and reverted inside
the range.

After writing the JSON, the runner returns `reviewed_input_binding` with
`packet_path`, `packet_sha256`, and `identity_sha256`, plus one exact
executable `verify_command`. **Copy the emitted `verify_command`** into the
durable critique record and run it before treating the packet as current:

```markdown
## Reviewed Input Identity

- Packet path: charness-artifacts/critique/<slug>-packet.json
- Packet SHA256: <exact packet byte digest>
- Identity SHA256: <reviewed input identity digest>
```

The Markdown packet repeats the same `verify_command`. Raw sha256sum is not
the contract: the command owns domain-separated identity reconstruction.

## Consumer Contract (Critique Skill)

When `critique` runs and the repo's adapter declares ≥1 packet section:

1. The bootstrap produces a packet when the adapter declares sections, or the
   parent passes an already-produced packet path/body through. The fresh-eye
   reviewer subagents receive the markdown render before broad repo sampling.
   For a guard, reference, claim, or verdict-surface change, they also apply the
   [semantic reviewer question](../../../shared/references/reviewer-packet-semantic-question.md):
   name the semantic fact or invariant, owning boundary, recorded instance, and
   an axis-varying counterexample before judging the selected control.
2. The critique closeout records `Packet Consumed: <path>` plus reviewer-tier
   evidence and reviewed-input binding evidence. Enforcement lives in the
   *caller skill's* closeout validator when the adapter declares packet
   sections, not in a global packet-consumed scanner.
3. If a parent produced the packet earlier for a specific changed ref, critique
   consumes that packet instead of regenerating a weaker working-tree packet.
   Otherwise critique runs the helper once for the current review target.

When the adapter declares no `packet_sections`, this contract is dormant
and critique behavior is unchanged.

## Producer Script Contract

A `script` section's producer command must:

- run from the repo root
- exit 0 when the section produced honest content (even if empty)
- exit non-zero only when the producer itself failed
- write the rendered section body to stdout
- emit structured payloads as YAML on stdout with no output-format flag
  (`--json` was retired repo-wide on 2026-08-14; see
  `<authoring-repo>/charness-artifacts/spec/cli-command-flag-conventions.md`)

The runner is intentionally thin: read adapter, run command, capture
stdout/stderr, fold into envelope. No retry, no caching, no merging
across runs. If a section needs caching, that lives in the producer.

Adapter validation is wired into the shared `validate_adapters.py` via
`<plugin-dir>/scripts/review/critique_adapter_lib.py`. The producer
(`critique_packet_lib.build_packet`) owns the emitted envelope shape.

## Out Of Scope For This Contract

- Charness does not classify section roles (`source` / `derived` /
  `audit-only` / `rewrite`). Roles are consumer-specific and live in
  the producer's section content.
- Charness does not enforce content correctness. The contract verifies
  packet *shape* and *presence*, not whether a scanner found the right
  things.
- The retro skill does not consume this packet today. A retro-side
  counterpart (`retro_packet_sections`) may follow as a separate slice
  once one or more repos have proven the critique-side contract.
