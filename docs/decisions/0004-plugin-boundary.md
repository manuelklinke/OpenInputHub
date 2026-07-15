# 0004: Start with In-Process Plugins

Date: 2026-07-01

## Status

Accepted

## Context

OpenInputHub needs extensibility, but premature process isolation can add complexity around IPC, deployment, versioning, and debugging.

## Decision

The initial architecture will assume in-process plugins with a deliberately small boundary. The design should not prevent later out-of-process plugins.

## Consequences

- Early development remains simpler.
- Plugin crashes can affect the main process.
- Binary compatibility must be treated carefully.
- A future C ABI or IPC-based plugin interface may be needed before broad third-party plugin distribution.
