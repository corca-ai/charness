---
type: spec
workdir: .
---

# On-Demand Validation Viewer

This page is a reader-facing viewer for the latest checked on-demand validation
artifacts. The checked artifact remains the source of truth for the run; this
specdown page makes that proof visible in the same report a product reader uses
to understand the current contract.

## Latest `cautilus` Behavioral Proof

The current prompt-behavior proof is checked in at
[`charness-artifacts/cautilus/latest.md`](../charness-artifacts/cautilus/latest.md).
This page should stay a viewer over that artifact, not a second evaluator
implementation.

```run:shell
python3 -c "from pathlib import Path; text = Path('charness-artifacts/cautilus/latest.md').read_text(encoding='utf-8'); assert '## Commands Run' in text; assert '## Outcome' in text; assert 'recommendation:' in text"
```

## `premortem` Stays On-Demand

`premortem` is a judgment-heavy, canonical-subagent workflow. The standing repo
bar should keep seam checks for the contract itself, while the real behavioral
question stays on-demand through `cautilus` or explicit reviewed HITL proof.

```run:shell
python3 -c "import json; from pathlib import Path; policy = json.loads(Path('docs/public-skill-validation.json').read_text(encoding='utf-8')); assert 'premortem' in policy['tiers']['hitl-recommended']; assert 'premortem' in policy['adapter_requirements']['adapter-free']; skill = Path('skills/public/premortem/SKILL.md').read_text(encoding='utf-8'); assert 'use subagents as the canonical path' in skill"
```
