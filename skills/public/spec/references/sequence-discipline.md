# Sequence Discipline

This reference captures the sequence-discipline moves that matter to `spec`.

## Core Moves

- commit the upstream decision that most changes the rest
- keep downstream detail as a probe or defer until the seam around it is clear
- preserve later options unless an earlier commitment materially reduces churn
- keep the contract ordered by dependency, not by document convenience

## Translation For Spec

- put `Fixed Decisions` ahead of the probes they enable
- make `Probe Questions` answer one uncertainty cleanly instead of mixing
  several downstream choices together
- defer choices that would only be honest after the first implementation slice
