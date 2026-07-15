# Project Charter

## Mission

OpenInputHub provides a stable middleware layer between heterogeneous input devices and heterogeneous output targets. It normalizes device-specific input into a common event model, routes those events through a core pipeline, and exposes them through output plugins.

## Non-Goals

- OpenInputHub is not a vendor SDK wrapper.
- OpenInputHub is not a single-device driver.
- OpenInputHub is not initially responsible for replacing operating-system input stacks.
- OpenInputHub must not require the SpaceControl SDK to define the internal architecture.

## Architectural Values

- Long-term maintainability over short-term code generation.
- Explicit boundaries between domain, hardware integration, transport, and output.
- Testability without attached hardware.
- Extensibility through capabilities and plugins.
- Conservative use of abstraction: abstractions must protect real variation, not decorate the codebase.

## Initial Assumptions

- The repository contains SpaceControl reference material under `vendor/sc_treiber/`.
- The SDK is deep enough that shallow scans may miss relevant files; analysis should use targeted paths and `rg`.
- A first header-level inspection is captured in [SpaceControl SDK Inventory](analysis/spacecontrol-sdk-inventory.md).
- The current SpaceControl Blackline diagnosis is captured in [SpaceControl Blackline Current State](analysis/spacecontrol-blackline-current-state.md).
- Fedora Linux is the reference development platform.
- Windows support should be designed early but implemented later.
- Embedded targets are output/device endpoint candidates, not necessarily hosts for the full middleware.

## Key Constraints

- `vendor/` is read-only.
- No architecture decision may require modifying vendor SDK files.
- The core must not branch on device names such as `SpaceControl` or `SpaceMouse`.
- Device-specific behavior must be represented as capabilities, profile metadata, mapping configuration, or adapter code.
