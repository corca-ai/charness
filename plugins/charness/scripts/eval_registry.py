from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    description: str


SCENARIOS = (
    Scenario("skill-valid", "fixture repo with one valid public skill passes package validation"),
    Scenario("profile-valid", "fixture repo with one valid profile passes artifact validation"),
    Scenario("doc-links-valid", "fixture docs with valid internal links pass markdown link validation"),
    Scenario("impl-adapter-bootstrap", "impl init/resolve scripts bootstrap repo-specific verification preferences"),
    Scenario("debug-adapter-bootstrap", "debug init/resolve scripts bootstrap the repo-local debug artifact contract"),
    Scenario("quality-adapter-bootstrap", "quality init/resolve scripts bootstrap a clean repo"),
    Scenario("quality-adapter-checked-in", "checked-in quality adapter resolves to the declared repo contract"),
    Scenario("quality-bootstrap-posture", "quality bootstrap posture records installed and deferred setup state"),
    Scenario("narrative-adapter-bootstrap", "narrative init/resolve scripts bootstrap the source-of-truth alignment contract"),
    Scenario("release-adapter-bootstrap", "release init/resolve scripts bootstrap the release artifact and adapter contract"),
    Scenario("handoff-adapter-bootstrap", "handoff adapter helpers bootstrap the durable handoff artifact path"),
    Scenario("gather-adapter-bootstrap", "gather adapter helpers bootstrap the durable gather artifact path"),
    Scenario("init-repo-adapter-bootstrap", "init-repo adapter helpers bootstrap the durable normalization artifact path"),
    Scenario("init-repo-inspect-states", "init-repo state inspection distinguishes greenfield bootstrap from partial repo normalization"),
    Scenario("init-repo-compact-skill-routing-discoverability", "init-repo compact routing makes startup find-skills bootstrap explicit without copying a long skill catalog"),
    Scenario("init-repo-operator-acceptance-synthesis", "init-repo can synthesize operator acceptance from functional checks and repo signals"),
    Scenario("handoff-relative-links", "handoff-style docs use relative markdown links"),
    Scenario("find-skills-local-first", "find-skills keeps local-first discovery while exposing configured trusted roots"),
    Scenario("support-sync-contracts", "shipped support-sync contracts stay discoverable without pretending every integration owns a support skill"),
    Scenario("representative-skill-contracts", "representative public skills retain their required contract markers"),
)


def scenario_ids() -> set[str]:
    return {scenario.scenario_id for scenario in SCENARIOS}
