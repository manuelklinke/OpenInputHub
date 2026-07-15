"""Conversion from typed SpaceController messages to normalized events."""

from dataclasses import dataclass

from openinputhub.protocol.messages import (
    ButtonSnapshot,
    Capabilities,
    ControlMessage,
    Diagnostics,
    Hello,
    Identity,
    MotionSample,
    WheelDelta,
    WireMessage,
)

from .events import (
    ButtonStateEvent,
    CapabilitiesEvent,
    DeviceHealthEvent,
    IdentityEvent,
    InputEvent,
    MotionEvent,
    WheelEvent,
)


@dataclass(frozen=True, slots=True)
class EventContext:
    source_session_id: str
    timestamp_ns: int

    def __post_init__(self) -> None:
        if not self.source_session_id:
            raise ValueError("source_session_id must not be empty")
        if self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must not be negative")


def message_to_event(
    message: WireMessage, sequence: int, context: EventContext
) -> InputEvent | None:
    common = {
        "source_session_id": context.source_session_id,
        "timestamp_ns": context.timestamp_ns,
        "sequence": sequence,
    }
    if isinstance(message, MotionSample):
        return MotionEvent(
            **common,
            axes=tuple(_normalize_axis(value) for value in message.axes),
            raw_axes=message.axes,
        )
    if isinstance(message, ButtonSnapshot):
        return ButtonStateEvent(
            **common,
            buttons=tuple(bool(message.mask & (1 << index)) for index in range(17)),
            raw_mask=message.mask,
        )
    if isinstance(message, WheelDelta):
        return WheelEvent(**common, delta=message.delta)
    if isinstance(message, Diagnostics):
        return DeviceHealthEvent(
            **common,
            uptime_ms=message.uptime_ms,
            reset_cause=message.reset_cause,
            uart_rx_errors=message.uart_rx_errors,
            sensor_timeouts=message.sensor_timeouts,
            display_timeouts=message.display_timeouts,
            watchdog_resets=message.watchdog_resets,
        )
    if isinstance(message, Identity):
        return IdentityEvent(
            **common,
            model=message.model,
            serial=message.serial,
            firmware=message.firmware,
        )
    if isinstance(message, Capabilities):
        return CapabilitiesEvent(
            **common,
            axis_count=message.axis_count,
            button_count=message.button_count,
            has_wheel=message.has_wheel,
            has_leds=message.has_leds,
            has_display=message.has_display,
        )
    if isinstance(message, (Hello, ControlMessage)):
        return None
    raise TypeError(f"unsupported wire message: {type(message)!r}")


def _normalize_axis(value: int) -> float:
    return value / (32768 if value < 0 else 32767)
