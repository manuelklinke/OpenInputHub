import pytest

from openinputhub.protocol.constants import ControlOpcode, Selector
from openinputhub.protocol.frame import Frame
from openinputhub.protocol.messages import (
    ButtonSnapshot,
    Capabilities,
    ControlMessage,
    Diagnostics,
    Hello,
    Identity,
    MessageDecodeError,
    MotionSample,
    WheelDelta,
    WireMessage,
    decode_message,
    encode_message,
)

MESSAGES: list[WireMessage] = [
    Hello(
        kind=0,
        min_major=1,
        min_minor=0,
        max_major=1,
        max_minor=0,
        nonce=0x12345678,
    ),
    Identity(
        model="SpaceControl Blackline", serial="SIM0001", firmware=(1, 0, 0)
    ),
    Capabilities(
        axis_count=6,
        button_count=17,
        has_wheel=True,
        has_leds=True,
        has_display=True,
    ),
    MotionSample(axes=(-32768, -1, 0, 1, 1234, 32767)),
    ButtonSnapshot(mask=0x1FFFF),
    WheelDelta(delta=-3),
    Diagnostics(
        uptime_ms=123456,
        reset_cause=2,
        uart_rx_errors=3,
        sensor_timeouts=4,
        display_timeouts=5,
        watchdog_resets=6,
    ),
    ControlMessage(
        opcode=ControlOpcode.SET_LEDS,
        request_id=9,
        body=b"\x03\x00\x00\x00\x7f",
    ),
    ControlMessage(
        opcode=ControlOpcode.SET_DISPLAY,
        request_id=10,
        body=b"\x03abc",
    ),
    ControlMessage(
        opcode=ControlOpcode.ACK,
        request_id=10,
        body=bytes([ControlOpcode.SET_DISPLAY]),
    ),
]


@pytest.mark.parametrize("message", MESSAGES)
def test_wire_message_round_trip(message: WireMessage) -> None:
    frame = encode_message(message, sequence=11)
    assert frame.sequence == 11
    assert decode_message(frame) == message


def test_selectors_match_message_types() -> None:
    assert [encode_message(message, 0).selector for message in MESSAGES[:8]] == [
        Selector.LINK,
        Selector.IDENTITY,
        Selector.CAPABILITIES,
        Selector.MOTION,
        Selector.BUTTONS,
        Selector.WHEEL,
        Selector.DIAGNOSTICS,
        Selector.CONTROL,
    ]


def test_button_snapshot_rejects_bit_17_and_above() -> None:
    with pytest.raises(ValueError, match="17 buttons"):
        ButtonSnapshot(mask=0x20000)


def test_decode_rejects_wrong_payload_length() -> None:
    with pytest.raises(MessageDecodeError, match="MOTION payload"):
        decode_message(Frame(Selector.MOTION, 0, bytes(11)))


def test_identity_rejects_invalid_utf8() -> None:
    payload = bytes([1, 0, 0, 1, 0xFF, 0])
    with pytest.raises(MessageDecodeError, match="IDENTITY UTF-8"):
        decode_message(Frame(Selector.IDENTITY, 0, payload))


@pytest.mark.parametrize("field", ["model", "serial"])
def test_identity_rejects_text_over_24_utf8_bytes(field: str) -> None:
    values = {"model": "model", "serial": "serial", "firmware": (1, 0, 0)}
    values[field] = "ä" * 13
    with pytest.raises(ValueError, match=field):
        Identity(**values)  # type: ignore[arg-type]


def test_capabilities_require_spacecontroller_v1_shape() -> None:
    with pytest.raises(ValueError, match="six axes"):
        Capabilities(5, 17, True, True, True)
    with pytest.raises(ValueError, match="17 buttons"):
        Capabilities(6, 16, True, True, True)


def test_display_body_accepts_64_data_bytes_and_rejects_65() -> None:
    valid = ControlMessage(ControlOpcode.SET_DISPLAY, 1, bytes([64]) + bytes(64))
    assert decode_message(encode_message(valid, 0)) == valid
    with pytest.raises(ValueError, match="64 display bytes"):
        ControlMessage(ControlOpcode.SET_DISPLAY, 1, bytes([65]) + bytes(65))


def test_display_declared_length_must_match_body() -> None:
    with pytest.raises(ValueError, match="declared display length"):
        ControlMessage(ControlOpcode.SET_DISPLAY, 1, b"\x02x")


def test_unknown_control_opcode_survives_round_trip() -> None:
    message = ControlMessage(opcode=0x22, request_id=1, body=b"future")
    decoded = decode_message(encode_message(message, 7))
    assert decoded == message
    assert decoded.opcode == 0x22


def test_control_opcode_specific_lengths_are_enforced() -> None:
    with pytest.raises(ValueError, match="SET_LEDS"):
        ControlMessage(ControlOpcode.SET_LEDS, 1, bytes(4))
    with pytest.raises(ValueError, match="CLEAR_DISPLAY"):
        ControlMessage(ControlOpcode.CLEAR_DISPLAY, 1, b"x")
    with pytest.raises(ValueError, match="ACK"):
        ControlMessage(ControlOpcode.ACK, 1, b"")
    with pytest.raises(ValueError, match="ERROR"):
        ControlMessage(ControlOpcode.ERROR, 1, b"\x01")


def test_motion_and_wheel_ranges_are_enforced() -> None:
    with pytest.raises(ValueError, match="six axes"):
        MotionSample((0,) * 5)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="signed 16-bit"):
        MotionSample((0, 0, 0, 0, 0, 32768))
    with pytest.raises(ValueError, match="signed 16-bit"):
        WheelDelta(-32769)
