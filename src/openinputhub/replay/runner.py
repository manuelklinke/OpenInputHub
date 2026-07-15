"""Feed recorded byte chunks through the production frame parser."""

from collections.abc import Callable
from dataclasses import dataclass
import time

from openinputhub.protocol.frame import Frame
from openinputhub.protocol.parser import FrameParser

from .capture import UartCapture


@dataclass(frozen=True, slots=True)
class ReplayedFrame:
    frame: Frame
    offset_ns: int


def replay_capture(
    capture: UartCapture,
    parser: FrameParser,
    delay: Callable[[float], None] | None = None,
    speed: float = 0,
) -> list[ReplayedFrame]:
    if speed < 0:
        raise ValueError("replay speed must not be negative")

    sleep = delay if delay is not None else time.sleep
    replayed: list[ReplayedFrame] = []
    previous_offset: int | None = None
    for chunk in capture.chunks:
        if speed > 0 and previous_offset is not None:
            interval = (chunk.offset_ns - previous_offset) / 1_000_000_000 / speed
            if interval > 0:
                sleep(interval)
        replayed.extend(
            ReplayedFrame(frame=frame, offset_ns=chunk.offset_ns)
            for frame in parser.feed(chunk.data)
        )
        previous_offset = chunk.offset_ns
    return replayed
