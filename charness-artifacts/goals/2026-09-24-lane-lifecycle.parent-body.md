## Situation

`charness task run` lanes are fire-and-forget: once a lane starts, the integrator cannot steer it, amend its scope, or read a typed verdict. Every Ceal multi-lane session therefore pays the same taxes: stale-plan relaunches, crash vs needs-review conflation, late P1s found after integration, and private orchestration scripts each repo re-invents.

## Experience

Over the last two weeks, sixteen lane issues (#814, #815, #816, #822, #823, #826, #827, #828, #829, #830, #831, #832, #833, #834, #835, #836) each fixed one carrier boundary with one more flag or field. Seven open issues continue the pattern from complementary angles: #837 (steer a running lane), #838 (executor availability probe), #839 (fresh-eye self-review), #840 (one exit code per result kind), #841 (generic merge train), #842 (lessons-ledger injection). Umbrella #843 adds eighteen orchestration practices (brief critique, premise checks, DAG queue, report economy, landing reviews, metrics, test cache, friction log) that currently live only in private session scripts.

## Impact

Implemented separately, these are twelve more mechanisms on the same carrier: the status/flag combinations explode while orchestration stays tribal. The next six issues will look the same.

## Weak solution direction (optional)

Own the whole loop in charness instead: typed result kinds with one exit code each, a mid-run steer channel, repo-declared verify/integrate profiles split from a generic core, and the before/during/after-landing orchestration (#843) as owned mechanics. Planning record: `charness-artifacts/goals/2026-09-24-lane-lifecycle.md` (achieve Goal Run; binding freezes the exact bytes).
