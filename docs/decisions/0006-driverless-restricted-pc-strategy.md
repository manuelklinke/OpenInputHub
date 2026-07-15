# 0006: Driverless Restricted-PC Strategy

Date: 2026-07-01

## Status

Accepted

## Context

A company PC may not allow software installation, administrator rights, or custom drivers. At the same time, OpenInputHub should ideally appear as a standard USB HID device to that PC.

## Decision

The architecture will treat a separate hardware HID bridge as the preferred long-term strategy for restricted PCs. The full middleware can run on Linux and forward output commands to a microcontroller that appears to the restricted PC as standard USB HID.

## Consequences

- Restricted PCs can remain unmodified.
- RP2040 and ESP32-S3 become important output endpoint candidates.
- A host-to-bridge protocol must be designed later.
- Pure software virtual HID remains useful on Linux and some Windows scenarios, but it is not the only deployment model.
