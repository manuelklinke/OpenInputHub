# Project Map

## Repository Areas

- `vendor/`: read-only SDK and vendor reference material
- `docs/`: canonical human-readable project documentation
- `docs/architecture/`: architecture model and boundaries
- `docs/decisions/`: Architecture Decision Records
- `.ai/`: AI-facing knowledge base and work guidance
- `src/`: OpenInputHub production code
- `test/`: automated tests and replay fixtures

## Current Initialization State

This repository currently contains architecture and documentation for OpenInputHub itself. `vendor/sc_treiber/` contains read-only SpaceControl reference material and sample code that belongs to the vendor SDK, not to OpenInputHub implementation.

## Important Cross-References

- Capability model: ../../docs/architecture/capability-system.md
- Repository structure: ../../docs/architecture/repository-structure.md
- Event model: ../../docs/architecture/domain-model.md
- Plugin model: ../../docs/architecture/plugin-architecture.md
- Replay model: ../../docs/architecture/recording-replay.md
