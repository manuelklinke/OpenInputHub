# Architecture Roadmap

## Phase 0: Documentation Baseline

- project charter
- architecture overview
- capability model
- plugin model
- replay strategy
- risk register
- ADR baseline

## Phase 1: SDK and Platform Analysis

- inspect SpaceControl SDK
- inspect Linux driver model
- document event semantics
- document legal and redistribution constraints
- define first plugin boundary

## Phase 2: Core Contracts

- define domain event schema
- define capability schema
- define plugin metadata schema
- define recording format
- define logging conventions

## Phase 3: Prototype Without Hardware Dependency

- virtual input source
- recorder/replayer
- event bus prototype
- one simple output backend

## Phase 4: First Hardware Adapter

- SpaceControl adapter as an input plugin
- replay fixtures captured from real hardware
- platform-specific integration tests

## Phase 5: Restricted-PC Deployment

- evaluate HID bridge architecture
- define host-to-bridge protocol
- prototype RP2040 or ESP32-S3 HID endpoint
