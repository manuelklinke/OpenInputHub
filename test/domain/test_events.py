import pytest
from pydantic import TypeAdapter, ValidationError

from openinputhub.domain.events import (
    ButtonStateEvent,
    DeviceLifecycleEvent,
    InputEvent,
    MotionEvent,
    WheelEvent,
)


def test_motion_event_is_versioned_frozen_and_json_serializable() -> None:
    event = MotionEvent(
        source_session_id="sim:001",
        timestamp_ns=100,
        sequence=3,
        axes=(-1.0, -0.5, 0.0, 0.5, 1.0, 0.25),
        raw_axes=(-32768, -16384, 0, 16384, 32767, 8192),
    )
    assert event.schema_version == 1
    assert event.event_type == "motion"
    assert event.model_dump(mode="json")["axes"][2] == 0.0
    with pytest.raises(ValidationError):
        event.axes = (0.0,) * 6


def test_event_rejects_invalid_sequence_and_timestamp() -> None:
    with pytest.raises(ValidationError):
        WheelEvent(source_session_id="x", timestamp_ns=-1, sequence=128, delta=1)


def test_motion_requires_six_bounded_axes() -> None:
    with pytest.raises(ValidationError):
        MotionEvent(
            source_session_id="x",
            timestamp_ns=0,
            sequence=0,
            axes=(0.0,) * 5,
            raw_axes=(0,) * 6,
        )
    with pytest.raises(ValidationError):
        MotionEvent(
            source_session_id="x",
            timestamp_ns=0,
            sequence=0,
            axes=(0.0, 0.0, 0.0, 0.0, 0.0, 1.01),
            raw_axes=(0,) * 6,
        )


def test_buttons_require_17_states_matching_mask() -> None:
    with pytest.raises(ValidationError, match="17"):
        ButtonStateEvent(
            source_session_id="x",
            timestamp_ns=0,
            sequence=0,
            buttons=(False,) * 16,
            raw_mask=0,
        )
    with pytest.raises(ValidationError, match="raw_mask"):
        ButtonStateEvent(
            source_session_id="x",
            timestamp_ns=0,
            sequence=0,
            buttons=(False,) * 17,
            raw_mask=1,
        )


@pytest.mark.parametrize("state", ["connected", "disconnected", "reconnecting"])
def test_lifecycle_states_are_part_of_input_event_union(state: str) -> None:
    event = DeviceLifecycleEvent(
        source_session_id="x", timestamp_ns=0, sequence=0, state=state
    )
    decoded = TypeAdapter(InputEvent).validate_python(event.model_dump())
    assert decoded == event
