# Domain Model

## InputEvent

`InputEvent` is the common representation for all input activity. It is a domain concept, not a transport packet and not a hardware report.

Expected event categories:

- axis motion
- relative motion
- absolute position
- button state
- gesture
- sensor sample
- battery state
- device lifecycle
- text/input command
- custom extension event

## Event Requirements

Every event should carry enough metadata to support routing, logging, recording, replay, and tests:

- stable source session id
- logical control id
- event category
- normalized value
- original value when useful for diagnostics
- timestamp from a defined clock domain
- sequence number within a session
- capability reference
- quality/status flags

## Device

A device is an input or output participant known to the runtime. It may be physical, virtual, replayed, or network-backed.

The domain model should distinguish:

- device identity: stable facts and discovery metadata
- device session: a runtime connection instance
- device capabilities: what the session can do
- logical controls: axes, buttons, sensors, displays, LEDs, and force sensors

## Logical Controls

Logical controls describe what can produce or consume values. They are not tied to vendor names.

Examples:

- `translation_x`
- `rotation_z`
- `button_primary`
- `battery_level`
- `force_sensor_front_left`
- `led_status`

Control naming should be stable enough for configuration files and replay data.

## Normalization

Normalization converts hardware-specific ranges, units, and states into common domain values. The original value can still be preserved for diagnostics and device-specific calibration.

Normalization must be explicit. Silent assumptions about axis ranges, dead zones, coordinate handedness, or units will make replay and cross-device mapping unreliable.
