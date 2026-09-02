# Goal Run #765 Parent Terminal Obligation

The parent is the Goal Run for `charness-artifacts/goals/2026-09-02-north-star-realignment.md`
(frozen draft sha256 `129f065a28ce2c6a6a7fd7dc5f6ff2b63349b75ddf1ab62411ea4879ff8d2501`,
binding sha256 `20fdaf7e9a3e1489a308b11041555a9249b2e826d93d951f294a565b24d161cf`).
It receives no child cursor of its own and closes only through
`issue_tool.py goal-run-close` after exact readback.

Before the parent closes, all of the following hold and are cited in the
final proof:

1. Every one of the nine linked children (766, 767, 768, 769, 770, 771, 772,
   773, 774) is provider `CLOSED`, carries an issue-owned closeout comment
   whose URL is the evidence identity in the close proof, and has a
   `verify-closeout` = `verified` readback against its closeout commit.
2. The exact expected graph (`expected-final-graph.json`: the seven
   operator-approved initial children plus the two approved amendments 773
   and 774) equals the live graph read by `goal-run-read`.
3. The clean consumer install proof exists, names the export commit, and shows
   `charness doctor`, `charness update`, and a quality run completing from the
   installed export without executing any authoring-repo `tools/` gate.
4. The release lane (`./scripts/run-quality.sh --release`) is green on the
   integrated tree with its skip list read and recorded.
5. The distinct-observer review of the export boundary and gate classification
   is recorded (`charness-artifacts/critique/2026-09-02-769-export-boundary.md`).

Push, tag, release publish, and installed-host mutation on operator machines
stay separately authorised and are not claimed by the close.
