# Reference reading and release coverage cost

Date: 2026-09-08 (KST). Source: `a9c6ae451cfa4ccb13f7f05135b6aab650e1a5af`.
Disposition: not-goal-bound; dated observations, not a new operating contract.

The prompt candidate is rejected. It reduced unnecessary reading and reported
worker tokens, but violated the frozen path criterion. Release coverage reuse
is unproven; the existing preparation and final gates remain unchanged.

## Frozen reading comparison

Four fresh consumers ran sequentially in A1–B1–B2–A2 order, with the same seed,
exported package, oracle, Luna/xhigh settings, and task carrier. A used the
current impl prompt. B added one paragraph distinguishing path resolution from
body reading and retaining every required step and applicability condition.
No prompt tuning, retries, replacements, or parent rescue occurred. Coverage
execution began only after all four consumers finished.

The seed asks for reference resolution; it does not literally demand reading
every body. Prior descriptions of blanket-reading pressure were interpretations,
not a quotation of a mandatory read-all instruction. This experiment tests a
fixture instruction clarification, not a public-skill change.

| Cell | Unnecessary body reads | Unique bodies | Reported tokens | Carrier seconds | Path result |
| --- | ---: | ---: | ---: | ---: | --- |
| A1 | ≥26 | ≥21 | 64,106 | 147.351 | Pass |
| B1 | 1 | 1 | 50,715 | 102.749 | Fail: four invented paths |
| B2 | 1 | 1 | 39,258 | 123.521 | Pass after command rework |
| A2 | ≥28 | ≥17 | 68,288 | 126.341 | Incomplete literal-resolution evidence |

The same classifier counts spec-driven content without a contract change and
conditional impl/Prove content without an applicability trigger. It excludes
inventories, existence checks, `wc`, manifests, and required/applicable impl
reads. Truncated compound-command output makes A counts lower bounds.

All four outputs passed the 11-test consumer suite and unchanged four-test
external oracle. All preserved the spec and original test method ASTs, changed
only `src/catalog.py` and `tests/test_catalog.py`, consumed the exact exported
impl skill/version, and avoided host/source substitution.

B1 used unavailable `realpath` nine times and guessed four nonexistent spec
references (`contract-consumption`, `decision-record`, `ideation-handoff`, and
`sequence-discipline`). It later resolved all eight actual impl references,
but recovery does not erase the frozen no-invented-path violation. B2 recovered
from assigning zsh's special `path` variable and an unquoted `<repo-root>` shell
pattern. A2 did not demonstrate every impl literal resolution, so this is not a
fully compliant four-cell path comparison. B1 independently suffices to reject.

The observed token reductions were 20.89% and 42.51%; time reductions were
30.27% and 2.23%. Two pairs do not establish general speedup, and the second
pair's 2.820-second difference is small. No source prompt or public skill was
changed on the strength of these observations.

## Release evidence identity

The archived preparation and final producers used the same base
`af7c1b784cf9893aff10f6138c49c1bca2288059`, the same 29 changed pool files,
and the same command selecting 354 test files. Replaying each historical selector
with its own source produced identical command/test-list digests.

Preparation actually ran at HEAD `8b6ce9635e84c4891b60a71fe0b3c6292cc0cc34`
with uncommitted version changes; the prepared commit was created afterward.
Final ran at `d8d05d57e312fa5206007256f0fc182ebc9c39a2`. Git/index state,
release/claims files and seed-cache namespaces differed. Equal pool bytes and
selected tests therefore do not establish equal executed dependencies. Prior
broad-suite file tracing is not evidence attributing dependencies to these 354
selected test files. Cross-stage coverage reuse remains unproven.

The current producer already limits JSON export to mapped paths. Deferring
preparation coverage would change the documented prepare contract, receipt and
claims-review wording, and when failures are discovered. It could waste a
prepared commit and claims review when final coverage fails. This investigation
does not adopt that scheduling change.

Historical changed-line times were 145.050s at preparation and 151.820s at final:
296.870s of the combined 566.585s quality-lane time (52.4%). This is historical
arithmetic, not a measured saving or a prediction for a future release.

## One fresh producer timing

A clean historical-final checkout was measured with the explicit historical
base and a call-through timer around the unchanged producer. The selected
command and mapped population were asserted equal to the replay before pytest.

| Stage | Wall seconds |
| --- | ---: |
| Test-file selection | 9.394 |
| Coverage preparation | 0.002 |
| Instrumented standing runner | 137.570 |
| Coverage combine | 1.805 |
| Coverage JSON | 1.162 |
| Fingerprint | 0.234 |
| Changed-line consumer | 2.313 |
| Total | 152.536 |

The runner passed 5,780 tests; the changed-line consumer returned clean for all
29 mapped files. Source status remained clean. The instrumented runner includes
its preamble and subprocess overhead; pytest itself reported 129.83s. Combine
and JSON are shown separately; their 2.968s enclosing timer is not added again.
The JSON was 161,850 bytes. The timer's selection and runtime paths belong to a
new checkout/environment, so this is one fresh observation, not an exact replay
of the historical wall time. Raw stdout had an `ok` prefix before the clean
YAML body; it is retained, and is not claimed as a directly parseable receipt.

The first attempt stopped before pytest because the ignored plugin export was
missing (11.433s, exit 2, no verdict). The historical repo-owned exporter then
materialized it without tracked changes. The second attempt above completed.
Both attempts and the preparation mistake remain in the evidence/cost record.

Test execution consumed about 90.2% of the completed run. Combine/JSON consumed
about 1.9%; the existing mapped-only export already avoids broad serialization.
No safe cache reuse, gate deletion, or useful small producer optimization was
demonstrated. A scheduling change or better test selection needs a separate
contract and dependency argument; neither is smuggled in as a measured saving.

## End-to-end cost and verification

The observed interval started at 22:04:56 UTC. Through evidence assembly at
2026-09-07T22:23:22Z, elapsed wall time was 1106.7s (18.44 minutes),
including parent preparation, investigation, reviews, waits, failed setup, and
synthesis. This timestamp precedes the final artifact commit/response; it is
not a claim that closure cost was zero.

Preparation before the first consumer took 281s. Four consumer carriers totaled
499.962s and reported 222,367 tokens. Design, investigation and review intervals
are retained separately and overlap; they must not be added to total wall time.
Parent and host reviewer token totals were not exposed. No total monetary/model
cost or end-to-end speedup is claimed. The investigation spent time to reject
one candidate and resolve the coverage bottleneck, without a production change.

The reading audit and coverage timing interpretation were independently reviewed.
Focused consumer checks and historical producer proof are scoped above; no fresh
broad authoring suite was run for these two dated evidence files. Artifact JSON,
portable paths, measurement arithmetic, source identity and whitespace were
checked before the local evidence commit.

[Structured observations](./2026-09-08-reading-coverage-cost.json) retain the
frozen prompts and identities, all four outcomes, trace excerpts and hashes,
selector command/digests, both coverage attempts, call-through timer, and costs.
Runtime paths are logical labels; raw hashes bind the original local captures.
