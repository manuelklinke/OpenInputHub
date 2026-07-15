"""Replay a captured SpaceController UART stream as JSON Lines."""

import argparse
from collections.abc import Sequence
from dataclasses import fields
import json
from pathlib import Path
import sys

from openinputhub.domain.conversion import EventContext, message_to_event
from openinputhub.protocol.messages import MessageDecodeError, decode_message
from openinputhub.protocol.parser import FrameParser, ParserStats
from openinputhub.replay.capture import CaptureFormatError, read_capture
from openinputhub.replay.runner import replay_capture


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _argument_parser().parse_args(argv)
    capture_path = Path(arguments.capture)
    session_id = arguments.session_id or f"replay:{capture_path.stem}"

    try:
        if arguments.timestamp_origin_ns < 0:
            raise ValueError("timestamp origin must not be negative")
        capture = read_capture(capture_path)
        parser = FrameParser()
        before = _stats_snapshot(parser.stats)
        replayed = replay_capture(capture, parser, speed=arguments.speed)
    except (CaptureFormatError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2

    had_error = False
    for item in replayed:
        if arguments.raw_frames:
            print(
                json.dumps(
                    {
                        "selector": f"{item.frame.selector.value:02x}",
                        "sequence": item.frame.sequence,
                        "payload_hex": item.frame.payload.hex(" "),
                        "offset_ns": item.offset_ns,
                    },
                    separators=(",", ":"),
                )
            )
            continue
        try:
            message = decode_message(item.frame)
            event = message_to_event(
                message,
                item.frame.sequence,
                EventContext(
                    source_session_id=session_id,
                    timestamp_ns=arguments.timestamp_origin_ns + item.offset_ns,
                ),
            )
        except (MessageDecodeError, ValueError, TypeError) as error:
            print(
                f"selector {item.frame.selector.name} sequence "
                f"{item.frame.sequence}: {error}",
                file=sys.stderr,
            )
            had_error = True
            continue
        if event is not None:
            print(event.model_dump_json())

    after = _stats_snapshot(parser.stats)
    if after != before:
        changes = [
            f"{name}={new - old}"
            for name, old, new in zip(_stats_names(), before, after, strict=True)
            if new != old
        ]
        print("replay parser discarded or rejected data: " + ", ".join(changes), file=sys.stderr)
        had_error = True
    return 1 if had_error else 0


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture")
    parser.add_argument(
        "--speed", type=float, default=0.0, help="0 disables replay delays"
    )
    parser.add_argument("--session-id")
    parser.add_argument("--timestamp-origin-ns", type=int, default=0)
    parser.add_argument("--raw-frames", action="store_true")
    return parser


def _stats_names() -> tuple[str, ...]:
    return tuple(field.name for field in fields(ParserStats))


def _stats_snapshot(stats: ParserStats) -> tuple[int, ...]:
    return tuple(getattr(stats, name) for name in _stats_names())


if __name__ == "__main__":
    raise SystemExit(main())
