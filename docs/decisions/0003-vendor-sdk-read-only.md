# 0003: Vendor SDK Is Read-Only Reference Material

Date: 2026-07-01

## Status

Accepted

## Context

The SpaceControl SDK is available as a starting point and reference. It includes vendor-provided headers, libraries, examples, wrappers, documentation, and Linux driver material.

## Decision

Files under `vendor/` are read-only reference material. OpenInputHub code and documentation may analyze and reference them, but must not modify them.

## Consequences

- Vendor provenance remains clear.
- Updating SDK material later is easier.
- Required integration code must live outside `vendor/`.
- SDK limitations must be handled through adapters, not vendor file edits.
