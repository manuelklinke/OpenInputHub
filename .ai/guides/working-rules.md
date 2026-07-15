# Working Rules for AI Agents

## Repository Rules

- Do not write implementation code during architecture-only tasks.
- Do not create source placeholders.
- Do not modify files under `vendor/`.
- Prefer documentation changes under `docs/` and `.ai/`.
- Link to canonical docs instead of duplicating long explanations.

## Architecture Rules

- Core logic must not depend on device names.
- Device-specific behavior belongs in plugins, adapters, or profiles.
- Domain concepts must not depend on SDK headers or platform APIs.
- Recording and replay must be considered in event and configuration decisions.

## When Requirements Are Unclear

Document assumptions in the relevant architecture or analysis file. If an assumption affects public contracts or long-term direction, create or update an ADR.
