---
type: spec
workdir: .
---

# README Proof Ledger

The README proof ledger is the current claim-to-proof map for reader-facing
README and operator promises. It should stay visible in the Specdown report so a
reader can move from the product story to the evidence owner for each acceptance
criterion.

```run:shell
python3 - <<'PY'
from pathlib import Path

text = Path("docs/readme-proof.md").read_text(encoding="utf-8")
required = [
    "# README Proof Ledger",
    "cautilus claim discover",
    "cautilus.claim_proof_plan.v1",
    "Claim Ledger",
    "README-INIT-ROUTE",
    "README-NORMAL-PROMPTS",
    "README-QUALITY",
    "charness-artifacts/cautilus/latest.md",
]
missing = [item for item in required if item not in text]
assert not missing, missing
PY
```

## Proof Owners

Ledger rows must name explicit proof owners instead of implying that generated
docs or Cautilus discovery alone prove every claim.

```run:shell
python3 - <<'PY'
from pathlib import Path

text = Path("docs/readme-proof.md").read_text(encoding="utf-8")
for owner in ("deterministic", "Cautilus", "HITL/operator", "deferred"):
    assert owner in text, owner

rows = [line for line in text.splitlines() if line.startswith("| README-")]
assert rows, "expected ledger rows"
for row in rows:
    cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
    assert len(cells) == 8, row
    proof_owner = cells[3]
    assert proof_owner, row
    assert "claim discover" not in proof_owner.lower(), row
    assert "proof plan" not in proof_owner.lower(), row
    assert any(
        marker in proof_owner
        for marker in (
            "Deterministic",
            "Cautilus",
            "HITL/operator",
            "Specdown",
            "delegated review",
            "human-auditable",
        )
    ), row
assert "proof plan, not a verdict" in text
PY
```
