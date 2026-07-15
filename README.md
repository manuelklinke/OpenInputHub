# OpenInputHub

OpenInputHub is an experimental, portable input middleware project. It aims to
turn physical, virtual, replayed, and network input sources into a shared event
model and expose those events through standard output backends.

The SpaceControl Blackline is the first hardware reference, but the architecture
is intentionally not tied to one device or vendor.

## Why This Project Exists

The immediate motivation is a valuable SpaceController whose main controller no
longer operates correctly. The mechanics, sensors, buttons, display, and circuit
boards are too useful to throw away merely because the original controller or
software stack has failed.

OpenInputHub explores whether such hardware can be understood, repaired, and
given a useful second life with an open host service and, if necessary,
replacement firmware.

A second explicit goal is to test how effectively ChatGPT/Codex can assist with
a long-running project that combines hardware diagnosis, firmware reverse
engineering, protocol design, and software development. AI assistance is part
of the experiment, not evidence that a conclusion or implementation is
correct.

## Project Goals

- Preserve and reuse capable hardware that would otherwise become electronic
  waste.
- Build device-independent input middleware for Linux workstations and a
  Raspberry Pi 4.
- Support normalized six-degree-of-freedom motion, buttons, wheels, keyboard,
  mouse, and configurable output profiles.
- Let a Raspberry Pi present standard composite USB input devices to a
  restricted computer without requiring software installation on that host.
- Keep profiles and configuration available locally on the Pi, with optional
  browser-based network configuration.
- Make simulation, recording, replay, and hardware-free tests first-class
  development tools.
- Document which conclusions are measured, reconstructed, probable, or still
  unknown.

## Current Status

Milestone 1, the hardware-independent SpaceController protocol foundation, is
implemented and tested. It currently provides:

- a versioned, 7-bit-safe UART frame codec with CRC-7/MMC;
- incremental parsing and recovery after malformed input;
- typed SpaceController wire messages;
- normalized, versioned input-event models;
- a deterministic SpaceController simulator;
- versioned JSON Lines UART captures and deterministic replay;
- the `openinputhub-replay` command-line tool.

The current implementation does **not** yet open a serial device, create Linux
`uinput` devices, provide the mapping/profile engine or web interface, configure
a Raspberry Pi USB gadget, or replace the AVR maincontroller firmware.

## Planned Deployment

The same Python service is intended to run in two primary environments:

### Linux workstation

The SpaceController connects directly to a Linux system. OpenInputHub reads the
device, applies calibration and profiles, and will emit standard Linux input
events through `uinput`.

### Raspberry Pi 4

Input devices connect to the Pi. The Pi will keep profiles locally and present
keyboard, mouse, and multi-axis HID reports as a composite USB gadget to another
computer. A private Linux workstation may configure and monitor the service over
the network, but the active profile must continue working without that network
connection.

Generic multi-axis HID is the first planned USB personality. A separately
selectable 3Dconnexion-compatible mode may follow after its behavior has been
measured and tested.

## Quick Start

Python 3.12 or newer is required. The current milestone can be developed and
tested without attached hardware.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest
```

Replay the committed deterministic capture as normalized JSON events:

```bash
.venv/bin/openinputhub-replay \
  test/fixtures/spacecontroller/session_v1.jsonl --speed 0
```

Inspect decoded UART frames instead:

```bash
.venv/bin/openinputhub-replay \
  test/fixtures/spacecontroller/session_v1.jsonl --raw-frames
```

Additional replay options include `--session-id`, `--timestamp-origin-ns`, and
`--speed`. Exit status `0` means a clean replay, `1` means one or more frames or
messages were rejected, and `2` means the arguments or capture file were
invalid.

## Documentation

- [Project charter](docs/project-charter.md)
- [Architecture overview](docs/architecture/overview.md)
- [SpaceController UART protocol v1](docs/protocol/spacecontroller-uart-v1.md)
- [Architecture decisions](docs/decisions/README.md)
- [Testing strategy](docs/testing/testing-strategy.md)

## AI-Assisted Development

ChatGPT/Codex has been used to help organize evidence, inspect firmware and host
software, propose experiments, write documentation, design protocols, and
implement tested code. This is deliberately visible because evaluating that
collaboration is one of the project's goals.

AI-generated output can be incomplete or wrong. In particular:

- hardware pin assignments must be checked against the physical board and the
  correct component datasheet;
- protocol and firmware claims must be checked against captures, disassembly,
  tests, or measurements;
- generated code must pass review and automated tests;
- voltage, reset, ISP, fuse, and flashing instructions require independent
  human verification before touching hardware.

## Safety and Project Independence

This is an unofficial community research project. It is not affiliated with,
authorized by, or endorsed by SpaceControl, 3Dconnexion, or any other referenced
manufacturer. Product and company names are used only to identify hardware and
describe interoperability research. All trademarks remain the property of
their respective owners.

Hardware probing, ISP operations, fuse changes, and firmware flashing can
permanently damage a device or destroy its original software. Treat all such
procedures as experimental, verify connections independently, use current
limiting where appropriate, and preserve recoverable information before making
destructive changes.

The software is provided without warranty under the terms of the GNU General
Public License; see [LICENSE](LICENSE), particularly sections 15 and 16.

## Licensing

Unless an individual file states otherwise, original OpenInputHub software and
original project documentation are licensed under the GNU General Public
License version 3 only (`GPL-3.0-only`). See [LICENSE](LICENSE).

The project GPL grant does **not** apply automatically to locally retained
firmware dumps, address-faithful reconstructions, firmware-derived pseudocode,
reverse-engineering evidence, or manufacturer firmware, SDKs, libraries,
documentation, hardware designs, trademarks, and other third-party material.
These materials are excluded from the public repository and may be subject to
separate copyright, contract, trademark, or other restrictions. Review their
provenance and applicable law before copying or redistributing them. This
repository policy is not legal advice.

## Contributing

Bug reports, reproducible captures, tests, protocol corrections, and portable
device adapters are welcome. Contributions should clearly distinguish measured
facts from inference and must not include proprietary SDKs, vendor firmware,
credentials, private serial numbers, or other material the contributor is not
authorized to publish.

By submitting original code or documentation to this repository, contributors
agree that their contribution may be distributed under `GPL-3.0-only`.
