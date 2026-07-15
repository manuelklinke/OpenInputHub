# Event Bus

## Purpose

The event bus decouples event producers from consumers. It is the central runtime path for live devices, virtual devices, recorders, replayers, processors, and output plugins.

## Design Constraints

- deterministic enough for replay-driven tests
- observable enough for diagnostics
- bounded enough to avoid unbounded memory growth
- explicit about ordering guarantees
- suitable for high-frequency sensor data

## Event Streams

The architecture should distinguish:

- raw diagnostic stream: adapter-specific, optional, not part of stable replay
- normalized input stream: stable domain events
- processed stream: mapped or transformed domain events
- output command stream: target-specific commands

The normalized input stream is the primary record/replay boundary.

## Backpressure

High-rate devices can produce more events than slow consumers can process. The event bus should support per-consumer policies such as:

- block producer
- drop oldest
- drop newest
- coalesce values
- mark data loss

The policy must be explicit per route or subscriber.
