---
type: spec
workdir: .
---

# On-Demand Review Viewer

This page makes optional reviewer or consumer-owned behavioral evidence visible
in the same report a product reader uses to understand the current contract.
It is a viewer over the chosen evidence, not another evaluator or standing
gate. Local deterministic checks remain the default proof layer.

## `critique` Stays On-Demand

`critique` is a judgment-heavy, canonical-subagent workflow. The standing repo
bar should keep seam checks for the contract itself, while the real behavioral
question stays on-demand through explicit reviewed HITL proof or a
consumer-owned evaluator.
Per #161, `critique` now ships an opt-in `.agents/critique-adapter.yaml`
contract for the prepare-packet runner, so it lives in the `required`
adapter bucket alongside other adapter-shipping public skills; the gate
still fires only when the adapter declares `packet_sections`.

```run:shell
python3 -c "import json; from pathlib import Path; policy = json.loads(Path('docs/public-skill-validation.json').read_text(encoding='utf-8')); assert 'critique' in policy['tiers']['hitl-recommended']; assert 'critique' in policy['adapter_requirements']['required']; skill = ' '.join(Path('skills/public/critique/SKILL.md').read_text(encoding='utf-8').split()); assert 'two bounded fresh-eye reviewers run in parallel' in skill; assert 'parent-owned counterweight pass' in skill"
```
