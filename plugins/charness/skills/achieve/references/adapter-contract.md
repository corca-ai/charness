# Achieve Adapter Contract

The optional achieve adapter configures planning inputs. A missing adapter uses
the portable defaults. A present but invalid adapter is a typed planning error;
it is never silently replaced with a partial configuration.

## Location

The canonical location is:

```text
.agents/achieve-adapter.yaml
```

Resolve it with:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

## Fields

```yaml
version: 1
repo: charness
language: en
artifact_dir: charness-artifacts/goals
discussion_deploy_vocab:
  - rollout
  - hotfix
interview:
  max_questions: 15
  allow_provisional_local_fallback: false
```

`interview.max_questions` is the maximum number of operator questions in one
planning interview. It defaults to 15 and accepts any positive integer. The
ceiling is not a target: unresolved consequential decisions at the ceiling
return `interview-cap-reached` and no Goal Binding is created.

`interview.allow_provisional_local_fallback` defaults to `false`. It permits a
consumer to continue planning without a provider parent when explicitly true;
it does not create a provider identity or authorize provider mutation.

`discussion_deploy_vocab` optionally replaces the portable deploy vocabulary
used to surface consequential planning decisions. Neutral concepts such as
production, live proof, and irreversible side effects remain triggers.

Unknown fields invalidate the adapter. Execution state is not an adapter field.

## Host boundary

The host goal slot is a host primitive. Achieve coordinates planning and hands
execution to the provider-backed Goal Run; it does not recreate local status or
progress state in the adapter.
