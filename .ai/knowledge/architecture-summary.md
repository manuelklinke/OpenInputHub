# Architecture Summary

OpenInputHub is a modular input middleware. The core handles normalized events, capabilities, routing, recording, replay, and plugin lifecycle. Device-specific behavior belongs in plugins and adapters.

The most important rule is that hardware does not define the architecture. Hardware data is translated into `InputEvent` records before entering the core.

## Core Ideas

- capability-based device model
- normalized `InputEvent`
- event bus as runtime backbone
- plugins at hardware and output edges
- replay as a normal input source
- structured logging from the beginning
- SpaceControl SDK isolated behind an adapter

## Do Not Do

- Do not special-case devices by name in the core.
- Do not modify `vendor/`.
- Do not let SpaceControl SDK structs become OpenInputHub domain structs.
- Do not treat replay as a later debug add-on.
- Do not put vendor SDK types into domain models.

See the canonical architecture in ../../docs/architecture/overview.md.
