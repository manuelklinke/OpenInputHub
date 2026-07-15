"""Typed raw payloads for SpaceController UART v1."""

from dataclasses import dataclass
import struct
from typing import TypeAlias

from .constants import ControlOpcode, Selector
from .frame import Frame


class MessageDecodeError(ValueError):
    """A valid frame contained an invalid selector-specific payload."""


def _require_unsigned(name: str, value: int, maximum: int) -> None:
    if not 0 <= value <= maximum:
        raise ValueError(f"{name} must be between 0 and {maximum}")


def _require_signed_16(name: str, value: int) -> None:
    if not -32768 <= value <= 32767:
        raise ValueError(f"{name} must fit signed 16-bit")


@dataclass(frozen=True, slots=True)
class Hello:
    kind: int
    min_major: int
    min_minor: int
    max_major: int
    max_minor: int
    nonce: int

    def __post_init__(self) -> None:
        if self.kind not in (0, 1):
            raise ValueError("hello kind must be 0 or 1")
        for name in ("min_major", "min_minor", "max_major", "max_minor"):
            _require_unsigned(name, getattr(self, name), 0xFF)
        _require_unsigned("nonce", self.nonce, 0xFFFFFFFF)


@dataclass(frozen=True, slots=True)
class Identity:
    model: str
    serial: str
    firmware: tuple[int, int, int]

    def __post_init__(self) -> None:
        if len(self.firmware) != 3:
            raise ValueError("firmware must contain major, minor, and patch")
        for part in self.firmware:
            _require_unsigned("firmware part", part, 0xFF)
        for name in ("model", "serial"):
            value = getattr(self, name)
            try:
                encoded = value.encode("utf-8")
            except UnicodeEncodeError as error:
                raise ValueError(f"{name} must be valid UTF-8") from error
            if not encoded or len(encoded) > 24:
                raise ValueError(f"{name} must contain 1..24 UTF-8 bytes")


@dataclass(frozen=True, slots=True)
class Capabilities:
    axis_count: int
    button_count: int
    has_wheel: bool
    has_leds: bool
    has_display: bool

    def __post_init__(self) -> None:
        if self.axis_count != 6:
            raise ValueError("protocol v1 requires six axes")
        if self.button_count != 17:
            raise ValueError("protocol v1 requires 17 buttons")


@dataclass(frozen=True, slots=True)
class MotionSample:
    axes: tuple[int, int, int, int, int, int]

    def __post_init__(self) -> None:
        if len(self.axes) != 6:
            raise ValueError("motion sample must contain six axes")
        for value in self.axes:
            _require_signed_16("axis value", value)


@dataclass(frozen=True, slots=True)
class ButtonSnapshot:
    mask: int

    def __post_init__(self) -> None:
        if not 0 <= self.mask <= 0x1FFFF:
            raise ValueError("button mask must contain only 17 buttons")


@dataclass(frozen=True, slots=True)
class WheelDelta:
    delta: int

    def __post_init__(self) -> None:
        _require_signed_16("wheel delta", self.delta)


@dataclass(frozen=True, slots=True)
class Diagnostics:
    uptime_ms: int
    reset_cause: int
    uart_rx_errors: int
    sensor_timeouts: int
    display_timeouts: int
    watchdog_resets: int

    def __post_init__(self) -> None:
        _require_unsigned("uptime_ms", self.uptime_ms, 0xFFFFFFFF)
        _require_unsigned("reset_cause", self.reset_cause, 0xFF)
        for name in (
            "uart_rx_errors",
            "sensor_timeouts",
            "display_timeouts",
            "watchdog_resets",
        ):
            _require_unsigned(name, getattr(self, name), 0xFFFF)


@dataclass(frozen=True, slots=True)
class ControlMessage:
    opcode: ControlOpcode | int
    request_id: int
    body: bytes

    def __post_init__(self) -> None:
        opcode_value = int(self.opcode)
        _require_unsigned("opcode", opcode_value, 0xFF)
        try:
            opcode: ControlOpcode | int = ControlOpcode(opcode_value)
        except ValueError:
            opcode = opcode_value
        object.__setattr__(self, "opcode", opcode)
        _require_unsigned("request_id", self.request_id, 0xFF)

        if opcode == ControlOpcode.SET_LEDS and len(self.body) != 5:
            raise ValueError("SET_LEDS body must contain mask and brightness")
        if opcode == ControlOpcode.SET_DISPLAY:
            if not self.body:
                raise ValueError("SET_DISPLAY body must contain a length")
            declared_length = self.body[0]
            if declared_length > 64:
                raise ValueError("SET_DISPLAY accepts at most 64 display bytes")
            if declared_length != len(self.body) - 1:
                raise ValueError("declared display length does not match body")
        if opcode == ControlOpcode.CLEAR_DISPLAY and self.body:
            raise ValueError("CLEAR_DISPLAY body must be empty")
        if opcode == ControlOpcode.ACK and len(self.body) != 1:
            raise ValueError("ACK body must contain the acknowledged opcode")
        if opcode == ControlOpcode.ERROR:
            if len(self.body) != 2:
                raise ValueError("ERROR body must contain opcode and error code")
            if self.body[1] not in range(1, 6):
                raise ValueError("ERROR code must be between 1 and 5")
        if not isinstance(opcode, ControlOpcode) and len(self.body) > 65:
            raise ValueError("unknown control body exceeds 65 bytes")


WireMessage: TypeAlias = (
    Hello
    | Identity
    | Capabilities
    | MotionSample
    | ButtonSnapshot
    | WheelDelta
    | Diagnostics
    | ControlMessage
)

_HELLO = struct.Struct("<BBBBBI")
_MOTION = struct.Struct("<6h")
_BUTTONS = struct.Struct("<I")
_WHEEL = struct.Struct("<h")
_DIAGNOSTICS = struct.Struct("<IBHHHH")


def encode_message(message: WireMessage, sequence: int) -> Frame:
    if isinstance(message, Hello):
        payload = _HELLO.pack(
            message.kind,
            message.min_major,
            message.min_minor,
            message.max_major,
            message.max_minor,
            message.nonce,
        )
        selector = Selector.LINK
    elif isinstance(message, Identity):
        model = message.model.encode("utf-8")
        serial = message.serial.encode("utf-8")
        payload = bytes(message.firmware) + bytes([len(model)]) + model
        payload += bytes([len(serial)]) + serial
        selector = Selector.IDENTITY
    elif isinstance(message, Capabilities):
        flags = (
            int(message.has_wheel)
            | (int(message.has_leds) << 1)
            | (int(message.has_display) << 2)
        )
        payload = bytes([message.axis_count, message.button_count, flags])
        selector = Selector.CAPABILITIES
    elif isinstance(message, MotionSample):
        payload = _MOTION.pack(*message.axes)
        selector = Selector.MOTION
    elif isinstance(message, ButtonSnapshot):
        payload = _BUTTONS.pack(message.mask)
        selector = Selector.BUTTONS
    elif isinstance(message, WheelDelta):
        payload = _WHEEL.pack(message.delta)
        selector = Selector.WHEEL
    elif isinstance(message, Diagnostics):
        payload = _DIAGNOSTICS.pack(
            message.uptime_ms,
            message.reset_cause,
            message.uart_rx_errors,
            message.sensor_timeouts,
            message.display_timeouts,
            message.watchdog_resets,
        )
        selector = Selector.DIAGNOSTICS
    elif isinstance(message, ControlMessage):
        payload = bytes([int(message.opcode), message.request_id]) + message.body
        selector = Selector.CONTROL
    else:
        raise TypeError(f"unsupported wire message: {type(message)!r}")
    return Frame(selector=selector, sequence=sequence, payload=payload)


def decode_message(frame: Frame) -> WireMessage:
    try:
        if frame.selector == Selector.LINK:
            _require_length(frame, _HELLO.size)
            return Hello(*_HELLO.unpack(frame.payload))
        if frame.selector == Selector.IDENTITY:
            return _decode_identity(frame.payload)
        if frame.selector == Selector.CAPABILITIES:
            _require_length(frame, 3)
            axis_count, button_count, flags = frame.payload
            if flags & ~0x07:
                raise ValueError("reserved capability flags are set")
            return Capabilities(
                axis_count,
                button_count,
                bool(flags & 1),
                bool(flags & 2),
                bool(flags & 4),
            )
        if frame.selector == Selector.MOTION:
            _require_length(frame, _MOTION.size)
            return MotionSample(_MOTION.unpack(frame.payload))
        if frame.selector == Selector.BUTTONS:
            _require_length(frame, _BUTTONS.size)
            return ButtonSnapshot(_BUTTONS.unpack(frame.payload)[0])
        if frame.selector == Selector.WHEEL:
            _require_length(frame, _WHEEL.size)
            return WheelDelta(_WHEEL.unpack(frame.payload)[0])
        if frame.selector == Selector.DIAGNOSTICS:
            _require_length(frame, _DIAGNOSTICS.size)
            return Diagnostics(*_DIAGNOSTICS.unpack(frame.payload))
        if frame.selector == Selector.CONTROL:
            if len(frame.payload) < 2:
                raise ValueError("CONTROL payload must contain opcode and request id")
            return ControlMessage(frame.payload[0], frame.payload[1], frame.payload[2:])
    except MessageDecodeError:
        raise
    except (ValueError, struct.error) as error:
        raise MessageDecodeError(f"{frame.selector.name} payload: {error}") from error
    raise MessageDecodeError(f"unsupported selector 0x{frame.selector.value:02x}")


def _require_length(frame: Frame, expected: int) -> None:
    if len(frame.payload) != expected:
        raise ValueError(
            f"{frame.selector.name} payload must contain {expected} bytes, "
            f"got {len(frame.payload)}"
        )


def _decode_identity(payload: bytes) -> Identity:
    if len(payload) < 5:
        raise MessageDecodeError("IDENTITY payload is too short")
    firmware = (payload[0], payload[1], payload[2])
    model_length = payload[3]
    model_end = 4 + model_length
    if model_end >= len(payload):
        raise MessageDecodeError("IDENTITY payload has invalid model length")
    serial_length = payload[model_end]
    serial_start = model_end + 1
    serial_end = serial_start + serial_length
    if serial_end != len(payload):
        raise MessageDecodeError("IDENTITY payload has invalid serial length")
    try:
        model = payload[4:model_end].decode("utf-8")
        serial = payload[serial_start:serial_end].decode("utf-8")
    except UnicodeDecodeError as error:
        raise MessageDecodeError("IDENTITY UTF-8 is invalid") from error
    try:
        return Identity(model=model, serial=serial, firmware=firmware)
    except ValueError as error:
        raise MessageDecodeError(f"IDENTITY payload: {error}") from error
