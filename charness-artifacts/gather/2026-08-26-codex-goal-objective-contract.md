# Gathered Source: Codex Goal Objective Contract

Source: https://learn.chatgpt.com/docs/developer-commands?surface=cli
Retrieved: 2026-08-26
Source type: official OpenAI documentation

## Relevant Contract

- `/goal <objective>` stores a non-empty objective for the active chat.
- The objective is arbitrary text up to the documented length limit.
- For longer instructions, the official guidance says to put details in a file
  and point the goal objective at that file.

## Design Consequence For This Goal

Codex does not need a new host-level binding-file parser. The goal objective can
be the ordinary text `#724`. Charness defines `/goal #<issue-number>` to mean the
parent issue in the current repository: `achieve` uses the adapter-resolved
`issue` backend to read that parent, then follows and validates the parent-owned
Goal Draft and Goal Binding pointers. The host owns persistence of the objective,
not interpretation of Charness's issue shorthand or Goal Binding schema.

## Non-Claims

- This source does not define Charness's binding schema or provider readback.
- It does not define `#<issue-number>` as an issue reference; that is a Charness
  convention layered on arbitrary objective text.
- It does not prove other hosts expose the same `/goal` command shape.
- Charness must not claim to implement or configure the host goal runtime.
