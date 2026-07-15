# Plugin Architecture

## Plugin Types

OpenInputHub should support several plugin roles:

- input adapter
- output adapter
- transform processor
- recorder
- replay source
- device profile provider
- diagnostics provider

Plugin roles may be combined only when the combination represents a real deployment unit.

## Plugin Boundary

Plugins are allowed to know about:

- vendor SDKs
- operating-system APIs
- USB details
- network protocols
- hardware quirks

The core is allowed to know only about:

- plugin metadata
- lifecycle hooks
- declared capabilities
- event producers and consumers
- configuration schema
- diagnostics status

## Lifecycle

Expected lifecycle states:

- discovered
- loaded
- configured
- started
- degraded
- stopped
- unloaded

Failures should be explicit and observable. A failed plugin should not bring down unrelated plugins unless it corrupts shared process state.

## In-Process First, Out-of-Process Later

The initial architecture should prefer in-process plugins for simplicity. A future out-of-process plugin boundary should remain possible for crash isolation, license isolation, or language interoperability.

See [ADR 0004](../decisions/0004-plugin-boundary.md).
