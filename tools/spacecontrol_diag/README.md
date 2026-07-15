# SpaceControl Diagnostic Tool

Small read-only diagnostic program for the vendor SpaceControl SDK.

The tool talks to `sc_daemon` through the public SDK library. It does not send
firmware, reset, bootloader, LCD write, LED write, or settings write commands.

## Build

```sh
make -C tools/spacecontrol_diag
```

The build uses the SDK headers and Linux shared library from:

```text
vendor/sc_treiber/SpaceControl/sdk/
```

## Run

Start the vendor daemon first, using the same user account as this program.
Then run:

```sh
tools/spacecontrol_diag/spacecontrol_diag
```

For trace correlation, run one SDK call at a time with wall-clock timestamps:

```sh
tools/spacecontrol_diag/spacecontrol_diag --timestamps --single devinfo
tools/spacecontrol_diag/spacecontrol_diag --timestamps --single basic
tools/spacecontrol_diag/spacecontrol_diag --timestamps --single advanced
tools/spacecontrol_diag/spacecontrol_diag --timestamps --single fmwstate
tools/spacecontrol_diag/spacecontrol_diag --timestamps --single raw
tools/spacecontrol_diag/spacecontrol_diag --timestamps --single lcd
tools/spacecontrol_diag/spacecontrol_diag --timestamps --single leds
tools/spacecontrol_diag/spacecontrol_diag --timestamps --single msg
tools/spacecontrol_diag/spacecontrol_diag --timestamps --single std --poll-count 1
```

If the library cannot be found at runtime, run:

```sh
LD_LIBRARY_PATH=vendor/sc_treiber/SpaceControl/sdk tools/spacecontrol_diag/spacecontrol_diag
```

## What It Checks

- SDK connection to `sc_daemon`
- daemon version/path
- device count and index range
- device info for valid device indexes
- daemon baud parameter
- firmware update state
- basic/advanced settings reads
- raw data reads
- standard data polling with full status reporting
- optional message read
- LCD and LED read calls only

## Options

- `--timestamps`: prints wall-clock markers before selected SDK calls.
- `--single <call>`: runs one read-only device call after connecting. Supported calls are `devinfo`, `basic`, `advanced`, `fmwstate`, `raw`, `lcd`, `leds`, `msg`, and `std`.
- `--dev <idx>`: selects the device index for `--single`; default is `0`.
- `--poll-count <n>`: sets the number of `std` polling iterations.
