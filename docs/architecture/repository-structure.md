# Repository Structure

## Current Created Structure

```text
.
├── .ai/
│   ├── adr/
│   ├── guides/
│   ├── knowledge/
│   └── research/
├── docs/
│   ├── analysis/
│   ├── architecture/
│   ├── decisions/
│   ├── operations/
│   ├── roadmap/
│   └── testing/
├── src/
├── test/
└── vendor/
```

## Directory Responsibilities

### `.ai/`

Compact AI-facing knowledge base. It should summarize and link to canonical documentation instead of duplicating it.

### `docs/`

Canonical project documentation for architecture, decisions, analysis, testing, operations, and roadmap planning.

### `src/`

Reserved for future OpenInputHub production code. No source files are created during this architecture-only initialization.

### `test/`

Reserved for future OpenInputHub tests. Replay-driven and virtual-device tests should be designed before hardware-dependent tests.

### `vendor/`

Read-only third-party and vendor reference material. The current SpaceControl material lives under `vendor/sc_treiber/`.

## Future Implementation Structure

When implementation begins, prefer a structure that reflects architectural boundaries:

```text
src/
├── domain/
├── core/
├── infrastructure/
├── plugins/
└── tools/

test/
├── domain/
├── core/
├── contract/
├── replay/
└── integration/
```

This is a direction, not an implementation commitment. Final directories should be created only when real code or tests are added.
