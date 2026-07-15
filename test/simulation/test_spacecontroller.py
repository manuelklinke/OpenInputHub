from openinputhub.protocol.frame import encode_frame
from openinputhub.protocol.messages import (
    ButtonSnapshot,
    Capabilities,
    Diagnostics,
    Identity,
    MotionSample,
    WheelDelta,
    decode_message,
)
from openinputhub.protocol.parser import FrameParser
from openinputhub.simulation.spacecontroller import (
    SimulatorConfig,
    SpaceControllerSimulator,
)


def test_simulator_startup_announces_identity_and_capabilities() -> None:
    simulator = SpaceControllerSimulator(SimulatorConfig(serial="SIM0001"))
    messages = [decode_message(frame) for frame in simulator.startup_frames()]
    assert isinstance(messages[0], Identity)
    assert messages[0].serial == "SIM0001"
    assert messages[1] == Capabilities(6, 17, True, True, True)


def test_simulator_is_deterministic_and_sequences_wrap() -> None:
    left = SpaceControllerSimulator(SimulatorConfig(serial="SIM0001"))
    right = SpaceControllerSimulator(SimulatorConfig(serial="SIM0001"))
    assert [left.step_bytes() for _ in range(140)] == [
        right.step_bytes() for _ in range(140)
    ]

    sequence_source = SpaceControllerSimulator(SimulatorConfig())
    parser = FrameParser()
    frames = parser.feed(
        b"".join(sequence_source.step_bytes() for _ in range(140))
    )
    assert {frame.sequence for frame in frames} == set(range(128))
    assert parser.stats.crc_errors == 0
    assert parser.stats.bytes_discarded == 0


def test_each_step_contains_motion_buttons_and_wheel() -> None:
    simulator = SpaceControllerSimulator(SimulatorConfig())
    messages = [decode_message(frame) for frame in simulator.step()]
    assert [type(message) for message in messages[:3]] == [
        MotionSample,
        ButtonSnapshot,
        WheelDelta,
    ]


def test_diagnostics_are_emitted_every_tenth_step() -> None:
    simulator = SpaceControllerSimulator(SimulatorConfig(sample_period_ns=10_000_000))
    diagnostics: list[Diagnostics] = []
    for _ in range(21):
        diagnostics.extend(
            message
            for message in map(decode_message, simulator.step())
            if isinstance(message, Diagnostics)
        )
    assert [message.uptime_ms for message in diagnostics] == [0, 100, 200]


def test_all_button_positions_and_wheel_pattern_are_generated() -> None:
    simulator = SpaceControllerSimulator(SimulatorConfig())
    masks: list[int] = []
    wheel: list[int] = []
    for _ in range(17):
        for message in map(decode_message, simulator.step()):
            if isinstance(message, ButtonSnapshot):
                masks.append(message.mask)
            elif isinstance(message, WheelDelta):
                wheel.append(message.delta)
    assert masks == [1 << index for index in range(17)]
    assert wheel[:8] == [0, 1, 0, -1, 0, 1, 0, -1]


def test_step_bytes_equals_encoding_step_frames() -> None:
    left = SpaceControllerSimulator(SimulatorConfig())
    right = SpaceControllerSimulator(SimulatorConfig())
    assert left.step_bytes() == b"".join(encode_frame(frame) for frame in right.step())
