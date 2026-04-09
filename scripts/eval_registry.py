from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    description: str


SCENARIOS = (
    Scenario("skill-valid", "fixture repo with one valid public skill passes package validation"),
    Scenario("profile-valid", "fixture repo with one valid profile passes artifact validation"),
    Scenario("packaging-valid", "shared host-packaging manifest stays aligned with repo artifacts"),
    Scenario("packaging-export", "shared packaging metadata materializes usable Claude and Codex plugin layouts"),
    Scenario("doc-links-valid", "fixture docs with valid internal links pass markdown link validation"),
    Scenario("quality-adapter-bootstrap", "quality init/resolve scripts bootstrap a clean repo"),
    Scenario("quality-adapter-checked-in", "checked-in quality adapter resolves to the declared repo contract"),
    Scenario("handoff-adapter-bootstrap", "handoff adapter helpers bootstrap the durable handoff artifact path"),
    Scenario("gather-adapter-bootstrap", "gather adapter helpers bootstrap the durable gather artifact path"),
    Scenario("handoff-absolute-links", "repo-local absolute markdown links remain valid in handoff-style docs"),
    Scenario("find-skills-local-first", "find-skills keeps local-first discovery while exposing configured official roots"),
    Scenario("representative-skill-contracts", "representative public skills retain their required contract markers"),
)


def scenario_ids() -> set[str]:
    return {scenario.scenario_id for scenario in SCENARIOS}
