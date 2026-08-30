# Critique Prepare Packet

The **critique prepare packet** is a deterministic, adapter-driven payload
that fresh-eye worker runs consume *before* broad repo sampling. It exists
to keep critique focused on judgment instead of repeatedly rediscovering
enumerable inventory (changed surfaces, adapter subscriptions, doc-link
graphs, role classifications, deferred concerns).

The packet shape is portable. Charness owns the envelope and the worker runner;
each consumer repo's `<repo-root>/.agents/critique-adapter.yaml` decides which
sections apply and how each section's content is produced.

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
boundary mode, Goal Run lineage, and lifecycle output. An existing packet can be supplied
with `--packet-file <repo-relative-path>`; its current binding is verified
before a reviewer starts. The low-level `run_reviewer_worker.py` interface
remains available for compatibility and diagnostics, not as the normal manual
operator path.

## Envelope

The packet is emitted as two artifacts:

- a JSON payload at
  `<output_dir>/<slug>-packet.json` — machine-readable contract
- a markdown render at
  `<output_dir>/<slug>-packet.md` — human-readable view that worker reviewers
  actually read

Where `<output_dir>` defaults to `charness-artifacts/critique` (override
via adapter `output_dir`) and `<slug>` defaults to a date+sequence
identifier (override via runner `--slug` flag).

For committed-diff critique, invoke the runner with `--changed-ref`:

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
sorts this declaration canonically and scopes staged, unstaged, untracked, and
content fingerprints to those paths, so an unrelated working-tree change does
not invalidate the review. The default sweep already drops the review record —
the critique artifact and any packet under the adapter `output_dir` — and
artifact-writing mode also excludes its own target packet JSON/Markdown paths, so
neither rerunning the same slug nor writing the verdict makes the record part of
the evidence it is trying to identify. The runner reports both the resulting
`reviewed_paths` and the dropped `auto_excluded_paths`.
An explicit `--reviewed-path` is never silently removed; if it names the
packet's own output path, the runner rejects the collision. Lexical traversal
and paths through an out-of-repo symlinked directory are also rejected.

In committed-ref mode, the exactness check remains a hard boundary. If the
default sweep excluded a committed review artifact, preparation refuses with
the missing and unexpected paths instead of silently adding or dropping them;
use `run_review.py --reviewed-paths-file <manifest>` to declare the exact
changed-ref set. The resulting identity is still checked against that set, so
changing the packet declaration or any bound subject path cannot silently move
the review to another subject.

The runner passes that value to script sections as
`CHARNESS_CRITIQUE_CHANGED_REF`. Producers that inspect changed files should
prefer the explicit ref/range over the clean working tree.

`A..B` ranges are endpoint diffs: the packet records files present in the net
diff between the two endpoints, not every file touched and reverted by commits
inside the range.

JSON envelope shape (`charness.critique_prepare_packet.v1`):

```json
{
  "kind": "charness.critique_prepare_packet",
  "version": 1,
  "repo": "<repo-name>",
  "generated_at": "<ISO8601 UTC>",
  "prepared_for": "<short label: commit range, branch, or free text>",
  "substrate_mode": "working-tree | committed-ref",
  "changed_ref": "<git commit or endpoint-diff range, or null>",
  "adapter_path": "<repo-relative path or null>",
  "reviewed_input_identity": {
    "algorithm": "sha256-v2",
    "status": "captured",
    "mode": "working-tree | committed-ref",
    "substrate_mode": "working-tree | committed-ref",
    "changed_ref": "<commit/range or null>",
    "resolved_changed_ref": ["<resolved endpoint(s)>"] ,
    "base_head": "<commit sha>",
    "base_head_role": "provenance-only | target",
    "reviewed_paths": ["<ordered repo-relative path>"],
    "reviewed_content": [{"path": "<path>", "content_sha256": "<non-null sha256>", "disposition": "deleted (present only on paths the ref removed)"}],
    "reviewed_patch_sha256": "<changed-ref patch sha256 or empty-payload sha256>",
    "staged_patch_sha256": "<scope-limited sha256>",
    "unstaged_patch_sha256": "<scope-limited sha256>",
    "declared_untracked": [{"path": "<path>", "content_sha256": "<sha256>"}],
    "auto_excluded_paths": ["<path dropped from the auto sweep>"],
    "identity_sha256": "<canonical component digest>"
  },
  "reviewer_tier_evidence": {
    "requested_tier": "high-leverage",
    "requested_spawn_fields": {"model": "..."},
    "host_exposure_state": "pending-parent-spawn",
    "application_state": "unverified-by-packet",
    "execution_mode": "file-backed-worker",
    "instruction": "<record host state in the review artifact>"
  },
  "sections": [
    {
      "id": "<slug>",
      "title": "<display title>",
      "content_kind": "static" | "script",
      "producer": "<command string or static-config marker>",
      "content": "<rendered string body of the section>",
      "ok": true,
      "errors": []
    }
  ],
  "section_count": 1,
  "ok": true
}
```

Rules:

- `kind` is the literal string `charness.critique_prepare_packet`
- `version` starts at `1`; bump on incompatible envelope changes
- `sections` is a list in declaration order (adapter-declared order
  preserved)
- Each section's `content` is a rendered string the reviewer reads
  directly. JSON-shaped section payloads are pretty-printed inside
  `content` (envelope stays one shape; section payload variety stays
  inside content).
- A failing section sets its own `ok: false` and `errors: [...]`. The
  envelope-level `ok` is `true` only when every section is `ok: true`.
- Envelope-level `ok: false` does not block packet emission; reviewers
  still read what was produced and judge whether the missing section
  changes their next move.
- `reviewer_tier_evidence` records the adapter-requested reviewer tier and
  spawn fields before subagents are spawned. The packet cannot prove host
  application; the parent review artifact records `requested_fields_sent`,
  `metadata-hidden`, `host-defaulted`, `unsupported`, or `applied` only when
  host-confirmed. `execution_mode` is the canonical `file-backed-worker` or
  `typed-subagent` branch selected by the adapter; it is rendered in the
  Markdown evidence block as `Execution mode`.
- `substrate_mode` is explicit in every packet. `working-tree` is the default
  for uncommitted review input and must not carry `changed_ref`; `committed-ref`
  requires a commit or endpoint-diff range. A committed-ref packet's declared
  `reviewed_paths` must exactly equal the paths changed by that ref/range.
- `reviewed_input_identity` records what the reviewer was given. Its patch and
  untracked components are limited to the declared paths. The
  reviewer-boundary fingerprint is a separate whole-worktree proof used only by
  the untyped shared-tree fallback; the default read-only worker does not
  snapshot and verify the parent tree.
- Before launch, the runner re-reads every declared regular file from the bound
  working-tree or committed-ref source, verifies its identity, and writes a
  read-only carrier. It embeds those bytes in the generated prompt, as UTF-8 or
  base64, so backends with and without filesystem tools receive the same
  semantic input. A nonempty consumer-defined section is context, not evidence
  that an unrelated reviewed path reached the worker. Zero reviewed paths,
  unavailable or mismatched bytes, and a combined payload above the bounded
  input limit refuse before the worker starts rather than silently truncating.
  Deleted paths use the same carrier and prompt path with their hash-checked
  pre-image bytes. The packet owns identity and provenance; the carrier owns the
  exact worker bytes.
- A working-tree identity is content-addressed under `sha256-v2`: only the declared
  paths and the bytes at those paths enter `identity_sha256`. `base_head`,
  `staged_patch_sha256`, `unstaged_patch_sha256`, `declared_untracked`, and
  `auto_excluded_paths` are recorded as provenance and excluded from the digest, so
  an unrelated commit, or a plain `git add` of a reviewed path whose bytes did not
  change, does not stale a path-scoped verdict — only an actual edit does. A
  changed-ref identity treats its resolved target and patch as inputs.
- **Symlinks — the rule differs by substrate, deliberately.** In WORKING-TREE
  mode a declared symlink is refused (`declare the target file explicitly`),
  because a live link's target can move underneath the verdict. In COMMITTED-REF
  mode the link is a blob inside an immutable commit, so it is hashed like any
  other path and no refusal applies. Stating this split rather than asserting one
  rule: the contract previously claimed link-payload hashing that had been
  unreachable since the working-tree refusal landed, and then claimed a blanket
  refusal that committed-ref mode does not perform.
- **Current pointers are BOUND, not skipped.** A `latest.md` symlink binds its
  link payload AND the bytes of the record it names, in both the auto sweep and
  an explicit declaration, so a retarget and a rewrite-in-place both stale the
  verdict. A pointer resolving outside the repo root is refused. Refreshing that pointer is the documented step after filing any
  record, so refusing it made every record-filing session unreviewable until it
  committed; excluding it was worse, because `auto_excluded_paths` is provenance
  and never digested, so a retarget could not stale an approved verdict. Binding
  the payload means retargeting the pointer at a different record DOES stale it.
- **Submodules** bind their gitlink commit id, including a removed one, whose
  pre-image comes from the parent tree because `git show <ref>:<path>` cannot
  read a gitlink. A bump changes exactly that value and it is what a reviewer
  judges; neither substrate could declare one before.
- **Deleted paths.** A path the ref removed binds its PRE-IMAGE bytes — from the
  range start for `a..b`, from `c^` for a single commit `c` — and carries
  `disposition: deleted`. The hash answers "what was removed"; the marker is what
  stops it from reading as "this file is present with these bytes". The
  disposition appears ONLY on deletions, so identities captured before this
  contract do not move. Every other declared path and patch component must carry
  a lowercase SHA-256 digest; a missing (`null`) hash is still a typed refusal.
- `verify` accepts only the current `sha256-v2` identity contract. Historical
  packets remain byte-addressed evidence, but are not accepted as current review
  proof under a retired digest rule.
- The auto sweep never returns the review record itself: everything under the adapter
  `output_dir` is dropped and reported in `auto_excluded_paths`, so authoring the
  critique artifact cannot stale the binding that describes it. An explicit
  `--reviewed-path` overrides that exclusion and is never dropped.
- The exact packet byte digest cannot be embedded in the packet without a
  circular hash. After writing the JSON, the runner returns
  `reviewed_input_binding` with `packet_path`, `packet_sha256`, and
  `identity_sha256`, plus one exact executable `verify_command`. Copy the
  binding fields into the durable critique record and run that command before
  treating the packet as current:

  ```markdown
  ## Reviewed Input Identity

  - Packet path: charness-artifacts/critique/<slug>-packet.json
  - Packet SHA256: <exact packet byte digest>
  - Identity SHA256: <reviewed input identity digest>
  ```

  The Markdown packet repeats the same `verify_command`. Raw sha256sum is not
  the contract: the command delegates to `verify_packet_binding`, which owns
  the domain-separated `sha256-v2` identity reconstruction. A raw digest of a
  reviewed file can differ while the packet is current.

  The critique validator checks the packet bytes and recomputes only the
  declared inputs. A declared-input change makes the verdict stale; an
  unrelated-path change does not.

## Section Types

A `packet_sections` entry has:

- `id`: short slug, lowercase-with-hyphens, unique within the packet
- `title`: one-line display title for the markdown render
- `content_kind`: `static` or `script`
- `content` (when `static`, inline string or list of strings) — OR
- `content_path` (when `static`, repo-relative path to a file whose
  contents are inlined verbatim) — OR
- `command` (when `script`, repo-relative shell command the runner
  executes; stdout becomes the section content)

Exactly one of `content`, `content_path`, or `command` must be present
per section, matching the declared `content_kind`.

`static` sections capture stable enumerable data (deferred-decisions
list, non-goals list, doc-link inventory). They are cheap and ideal for
"the things this critique should not relitigate."

`script` sections capture dynamic data (changed-files-and-owning-
surfaces, scanner findings, adapter subscriptions for the changed
paths). They are the place where consumer-specific scanners live; the
runner is content-agnostic.

## Default Sections

Charness ships one default section that runs on the charness repo and
serves as the contract reference example:

- `changed-files-and-owning-surfaces` — for the current
  `git status`/`git diff` working set, or for the runner's `--changed-ref`
  when provided, list each changed path and the surfaces (from
  `<repo-root>/.agents/surfaces.json`) that own or derive from it.
  Producer:
  `python3 scripts/render_critique_section_changed_surfaces.py`.

Consumers add more sections in their own `<repo-root>/.agents/critique-adapter.yaml`.

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
   evidence: requested tier, requested spawn fields, host exposure state, and
   applied-evidence boundary, plus reviewed-input binding evidence. The
   conditional hard-block is workflow-prescriptive: the rule applies
   only when the adapter declares packet sections, and enforcement
   lives in the *caller skill's* closeout validator (e.g., a future
   `validate_quality_closeout_contract.py` extension), not in a
   global `validate_critique_packet_consumed.py`. Critique itself
   writes results into the caller's artifact, so there is no canonical
   critique-output file for a global validator to scan.
3. If a parent produced the packet earlier for a specific changed ref, critique
   consumes that packet instead of regenerating a weaker working-tree packet.
   Otherwise critique runs the helper once for the current review target.

When the adapter declares no `packet_sections`, this contract is dormant
and critique behavior is unchanged.

## Producer Script Contract

A `script` section's producer command must:

- run from the repo root
- exit 0 when the section produced honest content (even if the content
  is empty — for example, "no changed paths detected")
- exit non-zero only when the producer itself failed (missing
  dependency, parse error). Non-zero exit makes the runner record the
  section with `ok: false` and the captured stderr.
- write the rendered section body to stdout
- a producer that also wants to emit a structured payload emits YAML on
  stdout, with no output-format flag (`--json` was retired repo-wide on
  2026-08-14; see
  `<authoring-repo>/charness-artifacts/spec/cli-command-flag-conventions.md`).
  The runner reads only stdout text and stores it as `content`, so the
  payload-shape contract stays producer-side, not envelope-side.

The runner is intentionally thin: read adapter, run command, capture
stdout/stderr, fold into envelope. No retry, no caching, no merging
across runs. If a section needs caching, that lives in the producer.

## Schema Validation

The runner validates each declared section before invoking it:

- exactly one of `content`/`content_path`/`command` per section
- `content_kind` matches the populated field
- `content_path` resolves to a file under the repo root
- `command` is a non-empty string

Adapter validation is wired into the shared `validate_adapters.py`:
`<repo-root>/.agents/critique-adapter.yaml` is parsed by
`<plugin-dir>/scripts/critique_adapter_lib.py`'s `load_adapter` so a malformed adapter
(missing required fields, dual-content fields, kind/field mismatch,
duplicate section ids) fails the standing adapter gate before the
runner ever spawns a producer process. The producer
(`critique_packet_lib.build_packet`) owns the emitted packet's envelope shape
(`section_count`, `ok`), covered directly by its own tests.

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
