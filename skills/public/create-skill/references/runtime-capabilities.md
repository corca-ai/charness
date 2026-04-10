# Runtime Capability Authoring Rule

Portable skills should assume they may run inside isolated agent runtimes.

## Preferred Access Order

When an external capability is needed, design for:

1. runtime grant
2. authenticated local binary
3. env fallback
4. public fallback or degraded mode

## Do Not Put These In Public Skill Bodies

- raw token names as user instructions
- `.env` file handling rituals
- copy-pasted secret bootstrap steps
- adapter fields that imply secret values live in repo config

## Put These In The Right Layer Instead

- public skill: user intent, required capability class, degradation behavior
- support skill: provider-specific usage guidance
- integration manifest: install, detect, healthcheck, access modes, and
  discovery-time capability metadata
- adapter: repo-local artifact paths and explicit non-secret defaults

## Review Questions

- does this skill still read as one user-facing concept after provider logic is removed?
- are private-access assumptions modeled as capability requirements rather than
  secret rituals?
- can an isolated host use this through a grant path without reopening the
  public-skill contract?
