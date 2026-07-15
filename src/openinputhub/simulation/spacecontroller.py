"""Deterministic protocol-level SpaceController simulator."""

from dataclasses import dataclass

from openinputhub.protocol.frame import Frame, encode_frame
from openinputhub.protocol.messages import (
    ButtonSnapshot,
    Capabilities,
    Diagnostics,
    Identity,
    MotionSample,
    WheelDelta,
    WireMessage,
    encode_message,
)


@dataclass(frozen=True, slots=True)
class SimulatorConfig:
    model: str = "SpaceControl Blackline"
    serial: str = "SIM0001"
    firmware: tuple[int, int, int] = (1, 0, 0)
    start_timestamp_ns: int = 0
    sample_period_ns: int = 10_000_000

    def __post_init__(self) -> None:
        if self.start_timestamp_ns < 0:
            raise ValueError("start_timestamp_ns must not be negative")
        if self.sample_period_ns <= 0:
            raise ValueError("sample_period_ns must be positive")


class SpaceControllerSimulator:
    def __init__(self, config: SimulatorConfig) -> None:
        self.config = config
        self._sequence = 0
        self._step_index = 0

    def startup_frames(self) -> tuple[Frame, ...]:
        return (
            self._frame(
                Identity(
                    model=self.config.model,
                    serial=self.config.serial,
                    firmware=self.config.firmware,
                )
            ),
            self._frame(Capabilities(6, 17, True, True, True)),
        )

    def step(self) -> tuple[Frame, ...]:
        index = self._step_index
        axes = tuple(
            ((index * (axis + 3) * 257) % 4095) - 2047
            for axis in range(6)
        )
        messages: list[WireMessage] = [
            MotionSample(axes),
            ButtonSnapshot(1 << (index % 17)),
            WheelDelta((0, 1, 0, -1)[index % 4]),
        ]
        if index % 10 == 0:
            messages.append(
                Diagnostics(
                    uptime_ms=(index * self.config.sample_period_ns // 1_000_000)
                    & 0xFFFFFFFF,
                    reset_cause=0,
                    uart_rx_errors=0,
                    sensor_timeouts=0,
                    display_timeouts=0,
                    watchdog_resets=0,
                )
            )
        self._step_index += 1
        return tuple(self._frame(message) for message in messages)

    def step_bytes(self) -> bytes:
        return b"".join(encode_frame(frame) for frame in self.step())

    def _frame(self, message: WireMessage) -> Frame:
        frame = encode_message(message, self._sequence)
        self._sequence = (self._sequence + 1) & 0x7F
        return frame
