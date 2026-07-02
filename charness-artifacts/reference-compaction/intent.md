# Operator Intent — why this effort exists + how to judge it

Governs `contract.md`, `census.json`, the claim-fidelity specs, and the capture
sweep. If any of those conflict with this intent, THIS wins and the conflicting
surface is what gets fixed. Captured 2026-07-02 from the operator's own reasoning;
key formulations kept verbatim so nuance is not lost in paraphrase.

## The symptom that started it

> "charness를 썼더니 에이전트가 더 멍청해진 것 같다."

The north is **the agent gets SMARTER, not dumber.** Proof (claim-fidelity,
cautilus) is a **means**, never the end. Fidelity, surface size, floor count,
capture coverage are NOT the goal — agent effectiveness is.

## The operator's diagnosis flow (verbatim spine)

1. "정말 내 스킬들이 잘 설계된 거 맞나?"
2. "일단 스킬들 자체의 의도는 genuine하다. 스킬들은 그대로 둘 가치가 있다" — the
   skills stay; their intent is real.
3. "그러나 게이트가 너무 많고 레퍼런스들이 너무 많다. 지능이 제대로 쓰이고 있나?" —
   the suspected drain is gate/reference OVERHEAD drowning the agent's intelligence.
4. "게이트가 정말 유의미한가? 레퍼런스가 정말 스킬의 의도(capability)에 맞게
   유의미하게 쓰이고 있나? 아니라면 삭제하거나 줄이자."
5. "템플릿과 게이트 stdout을 이용하면 지능을 더 잘 쓰게 할 수 있을 것이다." — turn
   gates from teeth into a BRIEF; use templates to channel intelligence, not cage it.
6. "이걸 상상만 하는 게 아니라 정말인지 검증하기 위해 코틸러스 돌려보자" — cautilus is
   the empirical instrument: real tool-calls / reasoning / results / cost / time in
   the logs, judged partly deterministically and partly by an agent re-reading them.

## The governing philosophy (leverage hierarchy — verbatim)

- 할 수 있는 일의 양(capabilities)이 동일하다면 기능(features)이 적을수록 좋다.
  (참고: 기능보다는 가능성 — possibilities over features)
- 기능이 동일하다면 코드의 양이 적을수록 좋다.
- 코드의 양이 동일하다면 오픈 소스의 비중이 높을수록 좋다.
- 코드의 양이 동일하다면 절차적 코드보다 선언적 코드가 좋다.

## The ONLY test (do not replace it with a proxy)

> "그게 정말 최선인가?" — is this really the best?

- **No proxy metric.** Surface reduction, gate count, proof coverage are all
  Goodhart traps — the moment one becomes a target it stops measuring the point.
- **Gate/feature/code addition is NOT evil.** A gate is good when it is genuinely
  the best shape (e.g. the substance-floor-only change ADDED validator code and was
  right — it removed an artificial constraint that forced dishonest floors). Bad =
  an *unjustified* gate, not a gate.
- The hierarchy above is **tie-breakers when capability is equal**, not an
  optimization target.

## Method that is already sufficient (do not over-build)

The question "does this reference meaningfully help this capability, or do the
SKILL.md body / script / template already cover it (so it is redundant)?" is
answered by the **current per-skill approach**: `census.json` (is the content
INLINE/DUP, i.e. already covered) + a real capture (did a faithful run even need
it). A run that does the task well WITHOUT opening ref X already IS the "without X"
arm — the evidence is in the single capture; no separate A/B is needed to prove
redundancy. Two honesty conditions:

- **Per genuinely-distinct condition** — "not opened in the representative run" is
  not "never useful" (missing-scenario trap; gather private-saas really opens
  browser-mediated-private-sources.md).
- **Honest coverage** — "opened" is not "helped" (#415: a prompt name-mention must
  not count as a genuine Read).

A with/without A/B earns its cost ONLY for the narrow case "the ref WAS opened —
did it actually help, or would the body alone have done as well?" Do NOT pre-build
an A/B apparatus; that apparatus is itself the overhead disease we are curing.

## Held open (not yet solved, do not silently drop)

Single-run capture cannot see the **systemic** dumbing the symptom describes —
the context tax a skill's overhead levies on unrelated reasoning across a whole
session, and the ritual-following it may train. Pruning gates/refs reduces this
indirectly, but measuring it directly is an open question, kept separate from the
per-ref redundancy question.

## Stance

Fundamental challenge is welcome — this whole framing may be a local optimum, so
re-derivation from first principles is always in-bounds. But whatever is decided,
it must serve the symptom (smarter agent) and pass the one test (그게 정말 최선인가?).
