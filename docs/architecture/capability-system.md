# Capability System

## Decision

OpenInputHub treats capabilities as the primary way to understand devices. Device names are descriptive metadata only.

## Examples

- `Has6DOF`
- `HasButtons`
- `HasGyro`
- `HasBattery`
- `HasBluetooth`
- `HasDisplay`
- `HasLED`
- `HasForceSensors`
- `CanOutputHID`
- `CanReplay`
- `CanRecord`

## Capability Records

A capability should describe behavior and constraints:

- capability type
- version or schema
- logical controls exposed by the capability
- units and ranges
- update rate expectations
- calibration requirements
- optional feature flags
- platform restrictions

## Static and Dynamic Capabilities

Some capabilities are known at discovery time. Others can change during a session, such as battery availability, optional extension modules, Bluetooth state, or profile-driven virtual outputs.

The runtime should support capability change events instead of assuming a fixed device shape.

## Compatibility Rules

Mappings and output routes should request capabilities, not devices.

Example:

```text
Any source with Has6DOF + HasButtons can feed a virtual SpaceMouse output profile.
```

This keeps the core open for future devices without adding device-specific branches.
