# Testing Strategy

## Testability Principle

Any behavior that matters should be testable without attached hardware.

## Test Types

- domain unit tests for event normalization, capabilities, and mapping rules
- application tests using virtual devices and replay sources
- plugin contract tests with fake SDK/device backends
- replay regression tests from known event recordings
- platform integration tests for Linux and Windows adapters
- manual hardware validation for device-specific behavior

## Replay Fixtures

Replay fixtures should be small, curated, and documented. They should represent behavior such as:

- simple button press
- 6DOF motion
- jitter around dead zone
- device disconnect
- reconnect with changed capabilities
- high-rate input burst

## Hardware Tests

Hardware tests should be separated from normal CI. They require explicit opt-in and should report attached device metadata without assuming a specific user's setup.
