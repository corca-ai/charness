# Narrative Adapter Contract

`narrative` stays portable by loading repo-specific truth-surface defaults from
an adapter instead of hardcoding one repo's document set into the public core.

Canonical path for new repos:

- [`.agents/narrative-adapter.yaml`](../../../../.agents/narrative-adapter.yaml)

Fallback lookup order:

1. [`.agents/narrative-adapter.yaml`](../../../../.agents/narrative-adapter.yaml)
2. `.codex/narrative-adapter.yaml`
3. `.claude/narrative-adapter.yaml`
4. `docs/narrative-adapter.yaml`
5. [`narrative-adapter.yaml`](../../../../.agents/narrative-adapter.yaml)

## Fields

- `version`: adapter schema version, currently `1`
- `repo`: repo display name for artifact labeling
- `language`: default durable artifact language
- `output_dir`: durable artifact directory, default `charness-artifacts/narrative`
- `preset_id`, `preset_version`, `customized_from`: provenance metadata only
- `source_documents`: ordered list of truth-surface docs to read first
- `mutable_documents`: ordered list of docs the skill may realign directly
- `brief_template`: ordered section labels for one audience-neutral brief
  skeleton
- `scenario_surfaces`: optional ordered labels for main first-class use cases
  or evaluation archetypes that should stay visible in the durable docs
- `scenario_block_template`: optional ordered slot labels for scenario blocks;
  keep this as a template, not a promise that every scenario must use every
  slot
- `primary_reader_profiles`: ordered list of first-touch readers the rewrite
  should optimize for before structure is chosen
- `preserve_intents`: ordered list of meanings or product truths that must
  survive even if section names and ordering change
- `terms_to_avoid_in_opening`: internal terms to downgrade or define later
  unless the opening has already earned them
- `quick_start_execution_model`: repo-local reminder of who usually executes
  quick-start actions and where the canonical contract lives
- `special_entrypoints`: repo-local labels or paths that should not be buried
  in a flat skill or feature inventory
- `skill_grouping_rules`: grouping reminders that keep maps aligned with repo
  intent rather than with arbitrary category names
- `owner_doc_boundaries`: deeper contracts that should stay in owner docs
  instead of silently expanding README scope
- `landing_danger_checks`: repo-local failure patterns worth checking before
  closeout
- `remote_name`: git remote to compare against when checking freshness

## Adapter Fitness Review

Before a README, landing page, or operator-facing truth rewrite, check whether
the adapter can actually produce the desired reader outcome. A present adapter
is not automatically a good adapter.

Run:

```bash
python3 skills/public/narrative/scripts/review_adapter.py --repo-root .
```

Treat these as repair-before-rewrite findings for first-touch surfaces:

- missing adapter when the target is README, landing copy, or operator docs
- missing files named by `source_documents`, `mutable_documents`, or
  path-like `special_entrypoints`
- `handoff`, `internal`, `archive`, or `archived` paths used as ordinary
  mutable landing docs
- path-like `special_entrypoints` that should shape the README but are absent
  from `source_documents`
- empty `primary_reader_profiles`, `preserve_intents`, `owner_doc_boundaries`,
  or `landing_danger_checks` when first-touch quality matters
- a broad source set that forces the agent to infer which docs are stable
  product truth and which are current implementation detail

Use volatile handoff or internal notes as situational context only when the
task explicitly targets those documents. They should not become the default
source of public README truth.

When the adapter is missing, scaffold it before rewriting in earnest and fill
the smallest useful contract:

- primary readers
- stable source documents
- mutable documents
- meanings that must survive structural cleanup
- owner documents that should keep deeper detail
- landing danger checks that reflect the repo's known failure patterns

## Durable Artifact

The default artifact is:

- [`charness-artifacts/narrative/latest.md`](../../../../charness-artifacts/narrative/latest.md)

Dated narrative records should use `charness-artifacts/narrative/YYYY-MM-DD-<slug>.md`.

Keep the durable alignment artifact separate from any audience-specific brief
when the brief is ephemeral or audience-local.

`brief_template` should stay audience-neutral. It is the repo-specific skeleton
for compressing the aligned story, not the place to encode language, tone,
channel, or one delivery backend.

`scenario_block_template` should stay concrete and first-run oriented. It is a
reader-scaffolding device for products with multiple first-class use cases, not
an invitation to duplicate the whole contract in cards.

`preserve_intents` is the adapter's main protection against structural cleanup
that erases meaning. Prefer short, falsifiable statements over vague slogans.

`quick_start_execution_model`, `owner_doc_boundaries`, and
`landing_danger_checks` are repo-local guidance layers. They should bias the
rewrite without turning the public skill into one repo's fixed README template.
