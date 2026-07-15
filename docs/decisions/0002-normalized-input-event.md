# 0002: Normalized InputEvent as Core Data Model

Date: 2026-07-01

## Status

Accepted

## Context

Input devices expose data in different formats, units, coordinate systems, and APIs. Output targets should not need to understand every input device.

## Decision

All input adapters translate device data into a shared normalized `InputEvent` model at the boundary between adapter and core.

## Consequences

- The event bus, recorder, replay system, and output plugins can share a stable model.
- Raw hardware data can still be retained for diagnostics, but it is not the primary core contract.
- Normalization rules must be documented per adapter to avoid hidden behavior.
