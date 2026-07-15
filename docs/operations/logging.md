# Logging Strategy

## Goals

Logging must support development, support requests, replay diagnosis, and long-running deployments without exposing unnecessary sensitive data.

## Requirements

- structured logs
- severity levels
- component names
- device session ids
- plugin ids
- event correlation ids where useful
- configurable sinks
- clear separation between logs and replay records

## Recommended Levels

- `trace`: high-volume event and timing details, disabled by default
- `debug`: plugin lifecycle, mapping decisions, discovery details
- `info`: startup, shutdown, device attach/detach, route activation
- `warning`: degraded behavior, recoverable plugin issues, dropped events
- `error`: failed operations requiring user attention
- `critical`: process-level failure

## Privacy

Input middleware can observe sensitive user actions. Logging must avoid recording typed text, clipboard contents, or high-resolution input streams unless the user explicitly enables diagnostic capture.

Replay files are not logs and should have their own consent and storage policy.
