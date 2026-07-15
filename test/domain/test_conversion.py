from openinputhub.domain.conversion import EventContext, message_to_event
from openinputhub.domain.events import (
    ButtonStateEvent,
    CapabilitiesEvent,
    DeviceHealthEvent,
    IdentityEvent,
    MotionEvent,
    WheelEvent,
)
from openinputhub.protocol.constants import ControlOpcode
from openinputhub.protocol.messages import (
    ButtonSnapshot,
    Capabilities,
    ControlMessage,
    Diagnostics,
    Hello,
    Identity,
    MotionSample,
    WheelDelta,
)


def test_motion_conversion_uses_asymmetric_signed_normalization() -> None:
    event = message_to_event(
        MotionSample((-32768, -16384, -1, 0, 16384, 32767)),
        sequence=4,
        context=EventContext("sim:001", 500),
    )
    assert isinstance(event, MotionEvent)
    assert event.axes == (-1.0, -0.5, -1 / 32768, 0.0, 16384 / 32767, 1.0)
    assert event.raw_axes == (-32768, -16384, -1, 0, 16384, 32767)


def test_button_mask_becomes_17_boolean_states() -> None:
    event = message_to_event(
        ButtonSnapshot((1 << 0) | (1 << 16)),
        5,
        EventContext("sim:001", 600),
    )
    assert isinstance(event, ButtonStateEvent)
    assert event.buttons[0] is True
    assert event.buttons[16] is True
    assert sum(event.buttons) == 2
    assert event.raw_mask == 0x10001


def test_wheel_identity_and_capabilities_are_preserved() -> None:
    context = EventContext("sim:001", 700)
    wheel = message_to_event(WheelDelta(-3), 6, context)
    identity = message_to_event(Identity("Blackline", "SIM1", (1, 2, 3)), 7, context)
    capabilities = message_to_event(Capabilities(6, 17, True, False, True), 8, context)
    assert isinstance(wheel, WheelEvent) and wheel.delta == -3
    assert isinstance(identity, IdentityEvent) and identity.firmware == (1, 2, 3)
    assert isinstance(capabilities, CapabilitiesEvent)
    assert capabilities.has_leds is False


def test_all_diagnostic_counters_are_preserved() -> None:
    event = message_to_event(
        Diagnostics(1234, 2, 3, 4, 5, 6),
        9,
        EventContext("sim:001", 800),
    )
    assert isinstance(event, DeviceHealthEvent)
    assert event.model_dump() == {
        "schema_version": 1,
        "event_type": "health",
        "source_session_id": "sim:001",
        "timestamp_ns": 800,
        "sequence": 9,
        "uptime_ms": 1234,
        "reset_cause": 2,
        "uart_rx_errors": 3,
        "sensor_timeouts": 4,
        "display_timeouts": 5,
        "watchdog_resets": 6,
    }


def test_link_and_control_messages_are_not_input_events() -> None:
    context = EventContext("sim:001", 0)
    hello = Hello(0, 1, 0, 1, 0, 1)
    ack = ControlMessage(
        ControlOpcode.ACK, 1, bytes([ControlOpcode.SET_LEDS])
    )
    assert message_to_event(hello, 1, context) is None
    assert message_to_event(ack, 2, context) is None
