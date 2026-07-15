# Recording and Replay

## Goal

Recording and replay are first-class architecture features. They are required for reproducible tests, hardware-free development, bug reports, and virtual devices.

## Recording Boundary

The default recording boundary is the normalized `InputEvent` stream. This avoids binding replay files to a vendor SDK or operating-system API.

Raw hardware reports may be captured as diagnostic attachments, but they should not be required for normal replay.

## Replay Requirements

Replay must preserve:

- event ordering
- source session identity or an equivalent remapping
- timestamps or relative timing
- capability snapshots
- configuration references
- software version metadata

Replay should support:

- real-time playback
- accelerated playback
- step-by-step playback
- deterministic test injection

## Virtual Devices

A replay source is a virtual input device. It should enter the runtime through the same device/session/capability model as a physical device.

This keeps tests honest: output plugins and mapping logic should not be able to tell whether events came from hardware or replay unless they explicitly ask for provenance metadata.
