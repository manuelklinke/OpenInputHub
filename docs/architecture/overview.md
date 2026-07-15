# Architecture Overview

## System Shape

OpenInputHub is organized around a small, stable core and replaceable edges.

```text
Input Adapter Plugin
        |
        v
Device Session -> InputEvent -> EventBus -> Processing Pipeline -> Output Plugin
        |              |             |              |                  |
        |              |             |              |                  v
        |              |             |              |           USB HID / Network /
        |              |             |              |           Macro / Clipboard
        |              |             |
        |              |             v
        |              |       Recorder / Monitor
        |              |
        v              v
 Capability Model   Replay Store
```

## Layers

### Domain

Owns concepts that are true regardless of hardware:

- input events
- capabilities
- device identity metadata
- logical controls
- timestamps
- routing intent
- replay records

The domain layer must not depend on vendor SDKs, OS APIs, USB stacks, or plugin loading.

### Application Core

Coordinates runtime behavior:

- plugin lifecycle
- device sessions
- event bus
- routing
- recording and replay
- diagnostics
- configuration loading

The application core depends on domain abstractions, not concrete devices.

### Infrastructure

Contains adapters to outside systems:

- vendor SDK integrations
- Linux device APIs
- Windows APIs
- USB HID backends
- network transports
- logging sinks
- file formats

Infrastructure code is replaceable and should be easy to exclude per platform.

### Plugins

Plugins add input sources, output targets, transforms, profiles, or diagnostics. Plugins may depend on platform APIs or vendor SDKs, but the core must only see their declared interfaces and capabilities.

## Data Flow

1. An input plugin discovers a device or virtual source.
2. It creates a device session with static and dynamic capabilities.
3. Raw device data is translated into `InputEvent` records at the adapter boundary.
4. Events are published to the event bus.
5. Processing components may map, filter, combine, or enrich events.
6. Output plugins consume normalized events and emit target-specific output.
7. Recorder components may persist the same normalized event stream.
8. Replay components may later inject recorded events through the same bus.

## Architectural Rule

The closer code is to the core, the less it may know about hardware. The closer code is to a plugin, the more concrete and device-specific it may be.
