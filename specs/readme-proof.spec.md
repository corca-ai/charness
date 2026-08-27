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
    "Claim Ledger",
    "README-INIT-ROUTE",
    "README-NORMAL-PROMPTS",
    "README-QUALITY",
    "Review Rule",
]
missing = [item for item in required if item not in text]
assert not missing, missing
PY
```

## Proof Owners

Ledger rows must name explicit proof owners instead of implying that generated
docs or an unscoped evaluator prove every claim.

```run:shell
python3 - <<'PY'
from pathlib import Path
from scripts.readme_proof_ledger_lib import LedgerEvidenceError, claim_ledger_rows, validate_ledger_rows

source = Path("docs/readme-proof.md")
text = source.read_text(encoding="utf-8")
for owner in ("deterministic", "HITL/operator", "deferred"):
    assert owner in text, owner

try:
    rows = claim_ledger_rows(text)
except LedgerEvidenceError as exc:
    raise AssertionError(str(exc)) from exc
assert rows, "expected ledger rows"
for cells in rows:
    proof_owner = cells[3]
    assert proof_owner, cells
    assert "claim discover" not in proof_owner.lower(), cells
    assert "proof plan" not in proof_owner.lower(), cells
    assert any(
        marker in proof_owner
        for marker in (
            "Deterministic",
            "HITL/operator",
            "Specdown",
            "delegated review",
            "human-auditable",
        )
    ), cells
assert "not a second test runner" in text
try:
    evidence_rows = validate_ledger_rows(text, source_path=source, repo_root=Path("."))
except LedgerEvidenceError as exc:
    raise AssertionError(str(exc)) from exc
assert len(evidence_rows) == len(rows)
PY
```
