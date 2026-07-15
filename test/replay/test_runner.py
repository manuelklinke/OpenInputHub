from pathlib import Path

from openinputhub.protocol.constants import Selector
from openinputhub.protocol.frame import Frame, encode_frame
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
from openinputhub.replay.capture import (
    CaptureChunk,
    CaptureHeader,
    UartCapture,
    read_capture,
)
from openinputhub.replay.runner import replay_capture


def capture_from_chunks(chunks: list[tuple[int, bytes]]) -> UartCapture:
    return UartCapture(
        header=CaptureHeader(
            format="openinputhub-uart-capture",
            version=1,
            device="SpaceController",
            baud=38400,
        ),
        chunks=tuple(
            CaptureChunk(offset_ns=offset_ns, data=data)
            for offset_ns, data in chunks
        ),
    )


def test_immediate_replay_uses_real_incremental_parser() -> None:
    frames = [
        Frame(Selector.WHEEL, 1, b"\x01"),
        Frame(Selector.WHEEL, 2, b"\xff"),
    ]
    capture = capture_from_chunks(
        [
            (0, encode_frame(frames[0])[:3]),
            (10_000_000, encode_frame(frames[0])[3:] + encode_frame(frames[1])),
        ]
    )
    parser = FrameParser()
    replayed = replay_capture(capture, parser, speed=0)
    assert [item.frame for item in replayed] == frames
    assert [item.offset_ns for item in replayed] == [10_000_000, 10_000_000]
    assert parser.stats.crc_errors == 0


def test_replay_scales_inter_chunk_delays() -> None:
    calls: list[float] = []
    capture = capture_from_chunks(
        [(0, b""), (20_000_000, b""), (50_000_000, b"")]
    )
    replay_capture(capture, FrameParser(), delay=calls.append, speed=2.0)
    assert calls == [0.01, 0.015]


def test_speed_zero_never_delays() -> None:
    calls: list[float] = []
    capture = capture_from_chunks([(0, b""), (1_000_000, b"")])
    replay_capture(capture, FrameParser(), delay=calls.append, speed=0)
    assert calls == []


def test_negative_speed_is_rejected() -> None:
    capture = capture_from_chunks([])
    try:
        replay_capture(capture, FrameParser(), speed=-1)
    except ValueError as error:
        assert "speed" in str(error)
    else:
        raise AssertionError("negative replay speed was accepted")


def test_corruption_does_not_prevent_next_chunk() -> None:
    expected = Frame(Selector.WHEEL, 9, b"\x01")
    bad = bytearray(encode_frame(Frame(Selector.WHEEL, 8, b"\x00")))
    bad[-2] ^= 1
    capture = capture_from_chunks([(0, bytes(bad)), (1, encode_frame(expected))])
    parser = FrameParser()
    replayed = replay_capture(capture, parser)
    assert [item.frame for item in replayed] == [expected]
    assert parser.stats.crc_errors == 1


def test_committed_fixture_decodes_expected_session() -> None:
    capture = read_capture(
        Path("test/fixtures/spacecontroller/session_v1.jsonl")
    )
    replayed = replay_capture(capture, FrameParser())
    messages = [decode_message(item.frame) for item in replayed]
    assert sum(isinstance(message, Identity) for message in messages) == 1
    assert sum(isinstance(message, Capabilities) for message in messages) == 1
    assert sum(isinstance(message, MotionSample) for message in messages) == 3
    assert sum(isinstance(message, ButtonSnapshot) for message in messages) == 3
    assert sum(isinstance(message, WheelDelta) for message in messages) == 3
    assert sum(isinstance(message, Diagnostics) for message in messages) == 1
