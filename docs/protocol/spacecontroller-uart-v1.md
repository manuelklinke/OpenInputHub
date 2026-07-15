# SpaceController UART Protocol v1

## Scope

This protocol connects replacement SpaceController maincontroller firmware to
the OpenInputHub host service. It transports raw device state and bounded
feedback commands. Keyboard shortcuts, profiles, mouse behavior, and USB
personality are host concerns and never appear on this link.

The physical link remains 38400 baud, 8N1 until the assembled UART chain proves
a faster rate reliable.

## Evidence Boundary

Internal reverse-engineering records indicate that selectors `f0` through `f7`
are absent from the known vendor selector inventory. The KSM receive ISR is
confirmed to accept any otherwise unhandled selector with bit 7 set into a
secondary, `8d`-terminated 100-byte slot. Forwarding from that slot to the FTDI
return path is only **Probable**. Later hardware-in-the-loop firmware work must
validate that path before relying on it in the assembled device.

## Frame Format

```text
SELECTOR SEQUENCE ENCODED_LENGTH ENCODED_PAYLOAD CRC7 8D
```

| Field | Size | Meaning |
| --- | ---: | --- |
| `SELECTOR` | 1 | One of `f0..f7`. |
| `SEQUENCE` | 1 | `00..7f`, incremented modulo 128 by each sender. |
| `ENCODED_LENGTH` | 1 | Encoded payload length, `00..78` (0..120). |
| `ENCODED_PAYLOAD` | variable | 7-bit-safe representation of 0..105 raw bytes. |
| `CRC7` | 1 | CRC-7/MMC over selector through encoded payload. |
| terminator | 1 | Exactly `8d`. |

All bytes after the selector and before the terminator are `00..7f`.
Multibyte raw fields are little-endian.

### 7-bit payload packing

Raw payload is split into groups of at most seven bytes. Each encoded group
starts with a header byte. Header bit `i` contains the removed high bit of raw
byte `i`; the following bytes contain the corresponding low seven bits. A full
group therefore contains one header and seven data bytes. The last group may
be shorter. Empty input produces an empty encoded payload. Unused header bits
in the final group must be zero.

Example: raw `80 01 ff` becomes `05 00 01 7f`.

### CRC

CRC uses CRC-7/MMC: polynomial `09` (`x^7 + x^3 + 1`), initial value `00`, no
reflection, no final XOR. The check value for ASCII `123456789` is `75`.

### Rejection and recovery

A receiver rejects the complete candidate on invalid sequence, encoded length,
payload packing, CRC, or terminator. It resumes scanning at the next `f0..f7`
byte. Because the frame body is 7-bit safe, another selector or an early `8d`
always proves that the current candidate is truncated. Unknown control opcodes
do not stop frame parsing.

## Selectors and Raw Payloads

| Selector | Name | Raw payload |
| --- | --- | --- |
| `f0` | Link/hello | `kind:u8 min_major:u8 min_minor:u8 max_major:u8 max_minor:u8 nonce:u32` |
| `f1` | Identity | `fw_major:u8 fw_minor:u8 fw_patch:u8 model_len:u8 model:utf8 serial_len:u8 serial:utf8` |
| `f2` | Capabilities | `axis_count:u8 button_count:u8 flags:u8` |
| `f3` | Motion | `tx:i16 ty:i16 tz:i16 rx:i16 ry:i16 rz:i16` |
| `f4` | Buttons | `mask:u32`, only bits 0..16 valid |
| `f5` | Wheel | `delta:i16` |
| `f6` | Diagnostics | `uptime_ms:u32 reset_cause:u8 uart_rx_errors:u16 sensor_timeouts:u16 display_timeouts:u16 watchdog_resets:u16` |
| `f7` | Control | `opcode:u8 request_id:u8 body:0..65 bytes` |

Hello kind `00` is a host request and kind `01` is a device response. Protocol
v1 capabilities require six axes and 17 buttons. Capability flag bit 0 means
wheel, bit 1 LEDs, and bit 2 display. The diagnostics packet also serves as the
heartbeat. Reset cause retains the ATmega MCUSR bit mask.

Button reports are complete 17-bit snapshots, not key chords. Signed wheel
deltas accumulate movement since the previous report.

## Control Messages

| Opcode | Name | Payload after opcode |
| --- | --- | --- |
| `01` | `SET_LEDS` | `request_id:u8 mask:u32 brightness:u8` |
| `02` | `SET_DISPLAY` | `request_id:u8 data_length:u8 data:0..64 bytes` |
| `03` | `CLEAR_DISPLAY` | `request_id:u8` |
| `70` | `ACK` | `request_id:u8 acknowledged_opcode:u8` |
| `71` | `ERROR` | `request_id:u8 failed_opcode:u8 error_code:u8` |

LED brightness ranges from 0 (off) to 255 (full). `SET_DISPLAY` carries one
already validated display-controller frame. Its inner grammar remains a
separate protocol. Every state-changing request receives `ACK` or `ERROR` with
the same request id.

Error codes are:

| Code | Meaning |
| --- | --- |
| `01` | unknown opcode |
| `02` | invalid length |
| `03` | invalid value |
| `04` | peripheral timeout |
| `05` | unsupported capability |

An unknown opcode receives error `01` and does not reset parsing.
