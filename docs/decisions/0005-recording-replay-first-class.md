# 0005: Recording and Replay Are First-Class

Date: 2026-07-01

## Status

Accepted

## Context

The project must support reproducible tests and development without attached hardware. Adding replay after implementation would likely force changes to event identity, timestamps, and routing.

## Decision

Recording and replay are part of the initial architecture. The normalized event stream is the primary recording boundary.

## Consequences

- Tests can use virtual devices from the beginning.
- Event schemas must include timing and session metadata.
- Replay files must include capability snapshots.
- Raw device capture is optional diagnostic material, not the main replay format.
