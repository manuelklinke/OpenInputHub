"""Versioned normalized input events."""

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

NormalizedAxis = Annotated[float, Field(ge=-1.0, le=1.0)]
Signed16 = Annotated[int, Field(ge=-32768, le=32767)]
Unsigned8 = Annotated[int, Field(ge=0, le=0xFF)]
Unsigned16 = Annotated[int, Field(ge=0, le=0xFFFF)]


class EventBase(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal[1] = 1
    source_session_id: str = Field(min_length=1)
    timestamp_ns: int = Field(ge=0)
    sequence: int = Field(ge=0, le=127)


class MotionEvent(EventBase):
    event_type: Literal["motion"] = "motion"
    axes: tuple[NormalizedAxis, ...] = Field(min_length=6, max_length=6)
    raw_axes: tuple[Signed16, ...] = Field(min_length=6, max_length=6)


class ButtonStateEvent(EventBase):
    event_type: Literal["buttons"] = "buttons"
    buttons: tuple[bool, ...] = Field(min_length=17, max_length=17)
    raw_mask: int = Field(ge=0, le=0x1FFFF)

    @model_validator(mode="after")
    def validate_buttons_match_mask(self) -> "ButtonStateEvent":
        mask = sum((1 << index) for index, pressed in enumerate(self.buttons) if pressed)
        if mask != self.raw_mask:
            raise ValueError("buttons do not match raw_mask")
        return self


class WheelEvent(EventBase):
    event_type: Literal["wheel"] = "wheel"
    delta: Signed16


class DeviceHealthEvent(EventBase):
    event_type: Literal["health"] = "health"
    uptime_ms: int = Field(ge=0, le=0xFFFFFFFF)
    reset_cause: Unsigned8
    uart_rx_errors: Unsigned16
    sensor_timeouts: Unsigned16
    display_timeouts: Unsigned16
    watchdog_resets: Unsigned16


class IdentityEvent(EventBase):
    event_type: Literal["identity"] = "identity"
    model: str = Field(min_length=1, max_length=24)
    serial: str = Field(min_length=1, max_length=24)
    firmware: tuple[Unsigned8, Unsigned8, Unsigned8]


class CapabilitiesEvent(EventBase):
    event_type: Literal["capabilities"] = "capabilities"
    axis_count: Literal[6]
    button_count: Literal[17]
    has_wheel: bool
    has_leds: bool
    has_display: bool


class DeviceLifecycleEvent(EventBase):
    event_type: Literal["lifecycle"] = "lifecycle"
    state: Literal["connected", "disconnected", "reconnecting"]


InputEvent: TypeAlias = Annotated[
    MotionEvent
    | ButtonStateEvent
    | WheelEvent
    | DeviceHealthEvent
    | IdentityEvent
    | CapabilitiesEvent
    | DeviceLifecycleEvent,
    Field(discriminator="event_type"),
]
