# Evidence Durability

When a spec, contract, or proof artifact cites a file as evidence for a current
claim, the cited path must be checkoutable on a fresh clone. Generated or
ignored outputs are reproduction sources, not durable evidence.

## Two Citation Roles

- **Durable evidence link**: a checked-in path that another reader can open
  from a clean checkout to verify the claim. Spec proof, acceptance checks,
  release ledgers, and `Critique` evidence belong here.
- **Reproduction source path**: a generated, gitignored, or runtime-only path
  that explains *how to regenerate* the evidence locally. Useful in
  troubleshooting and dogfood notes; not a substitute for the durable link.

Treat them as different roles even when the same human ran the command and
saw the same output. The first survives a fresh checkout, CI, or another
operator. The second only survives the machine that produced it.

## When Generated Output Is the Source of Truth

When a proof's source of truth is a generated artifact (eval summary, runtime
inventory, profile dump, screenshot), pick one of:

- **Selected proof artifact (preferred)**: copy the fields the spec actually
  cites into a checked-in artifact under `charness-artifacts/<scope>/`,
  including a `Source` line naming the reproduction path and a `SHA-256` of
  the source bytes when integrity matters. The spec links to the checked-in
  artifact, not the generated path.
- **Reproduction-only declaration**: when copying the artifact is not honest
  (e.g., shape-of-output is the claim and no field selection makes sense),
  state that the proof is reproduction-only and name the exact command or
  script. Do not link the generated path as if it were durable evidence.

A generated path becomes durable only when it is committed. A path that
matches a `.gitignore` rule is, by definition, not durable.

## Selected Evidence Shape

A `charness-artifacts/<scope>/<topic>-proof.md` (or peer) artifact should
usually carry:

- `Claim`: the spec claim this evidence supports.
- `Source`: the reproduction path or command (e.g.,
  `artifacts/self-dogfood/.../latest/eval-summary.json`).
- `SHA-256`: hash of the source bytes when integrity matters; omit when the
  claim is shape-only.
- `Selected fields`: the rows, keys, or excerpts cited by the spec, copied
  verbatim. Do not rewrite or summarize past the claim's granularity.
- `Captured`: ISO date the operator captured the snapshot.

The spec then links to the checked-in artifact path. Future readers can
re-derive the source via `Source`; they do not depend on the original machine
to read the evidence itself.

## Marker for Intentional Reproduction-Source Citations

Inline reproduction-source paths are allowed when the surrounding prose
explains the role and the citation bullet carries an HTML-comment marker so
deterministic checks can skip it without inferring intent:

```markdown
Run `make eval-self-dogfood` to refresh `artifacts/self-dogfood/latest/eval-summary.json` <!-- reproduction-source -->.
```

The marker is scoped to one citation bullet. Put it on the citation line or on
that bullet's immediately following two- or three-space-indented plain-text
continuation. A nested list item, block quote, heading, or fenced block is a
different semantic block and does not exempt the parent citation. Use the marker
only for prose that honestly describes reproduction, not for sneaking durable
claims past a checker. The keyword is matched case-insensitively, but the HTML
comment delimiters are required so it stays invisible when rendered.

## Frozen Records Are Counted, Not Rewritten

Two kinds of artifact are exempt from enforcement and reported as a count
instead. Artifacts in the later-added families whose filename dates them
before the enforcement anchor are history. A Goal Draft whose exact bytes a
sibling `<stem>.binding.json` hashes under `draft.sha256` is frozen by the
Goal Run it identifies: rewriting it to satisfy this check would break that
run's identity, which is the same inversion the anchor refuses. The binding
exemption holds only while the bytes on disk still hash to what the binding
froze; a draft edited after binding is enforced again. Neither exemption is
an allowlist or an author-written date.

## Failure Mode This Closes

Without this contract, a syntactic link checker can be satisfied by stripping
Markdown link syntax around an ignored path, leaving the spec appearing
evidence-backed while the cited evidence is absent on any fresh clone or CI
run. Link-check success is shape-only; evidence durability is the semantic
invariant on top of it.

When in doubt, prefer the selected proof artifact. It costs one short file and
makes the proof legible from a clean checkout, which is the contract every
charness spec is trying to keep.
