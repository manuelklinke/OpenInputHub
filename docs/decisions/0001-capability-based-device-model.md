# 0001: Capability-Based Device Model

Date: 2026-07-01

## Status

Accepted

## Context

OpenInputHub must support many current and future devices. Branching on device names would force core changes for every new device and would make similar devices harder to reuse.

## Decision

The core will reason about device capabilities instead of device names. Device names may appear in metadata, logs, UI, and plugin-specific diagnostics, but routing and compatibility decisions must use capabilities.

## Consequences

- New devices can be added by plugins without modifying core logic.
- Mappings can target behavior such as `Has6DOF` instead of `SpaceControl`.
- Capability schemas must be designed carefully and versioned.
- Some vendor-specific quirks will still exist, but they belong in adapters or profiles.
