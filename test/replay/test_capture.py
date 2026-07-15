from pathlib import Path

import pytest
from pydantic import ValidationError

from openinputhub.replay.capture import (
    CaptureChunk,
    CaptureFormatError,
    CaptureHeader,
    UartCapture,
    read_capture,
    write_capture,
)


def make_capture() -> UartCapture:
    return UartCapture(
        header=CaptureHeader(
            format="openinputhub-uart-capture",
            version=1,
            device="SpaceController",
            baud=38400,
        ),
        chunks=(
            CaptureChunk(offset_ns=0, data=b"\xf5\x03"),
            CaptureChunk(offset_ns=10_000_000, data=b"\x02\x01\x7f\x2b\x8d"),
        ),
    )


def test_capture_round_trip_is_stable(tmp_path: Path) -> None:
    path = tmp_path / "capture.jsonl"
    capture = make_capture()
    write_capture(path, capture)
    assert read_capture(path) == capture
    text = path.read_text(encoding="utf-8")
    assert '"data_hex":"f5 03"' in text
    assert text.endswith("\n")


def test_offsets_must_be_monotonic() -> None:
    with pytest.raises(ValidationError, match="monotonically"):
        UartCapture(
            header=make_capture().header,
            chunks=(
                CaptureChunk(offset_ns=2, data=b""),
                CaptureChunk(offset_ns=1, data=b""),
            ),
        )


def test_chunk_rejects_negative_offset() -> None:
    with pytest.raises(ValidationError):
        CaptureChunk(offset_ns=-1, data=b"")


@pytest.mark.parametrize("data_hex", ["0", "zz", "00 1"])
def test_reader_rejects_invalid_hex_with_line_number(
    tmp_path: Path, data_hex: str
) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text(
        '{"format":"openinputhub-uart-capture","version":1,'
        '"device":"SpaceController","baud":38400}\n'
        f'{{"offset_ns":0,"data_hex":"{data_hex}"}}\n',
        encoding="utf-8",
    )
    with pytest.raises(CaptureFormatError, match=r"bad\.jsonl:2"):
        read_capture(path)


def test_reader_accepts_hex_whitespace(tmp_path: Path) -> None:
    path = tmp_path / "spaces.jsonl"
    path.write_text(
        '{"format":"openinputhub-uart-capture","version":1,'
        '"device":"SpaceController","baud":38400}\n'
        '{"offset_ns":0,"data_hex":"f5  03\\n02"}\n',
        encoding="utf-8",
    )
    assert read_capture(path).chunks[0].data == bytes.fromhex("f5 03 02")


def test_reader_rejects_unknown_property(tmp_path: Path) -> None:
    path = tmp_path / "extra.jsonl"
    path.write_text(
        '{"format":"openinputhub-uart-capture","version":1,'
        '"device":"SpaceController","baud":38400,"extra":true}\n',
        encoding="utf-8",
    )
    with pytest.raises(CaptureFormatError, match=r"extra\.jsonl:1"):
        read_capture(path)


def test_empty_capture_is_valid_but_missing_header_is_not(tmp_path: Path) -> None:
    capture = UartCapture(header=make_capture().header, chunks=())
    path = tmp_path / "empty.jsonl"
    write_capture(path, capture)
    assert read_capture(path) == capture

    missing = tmp_path / "missing.jsonl"
    missing.write_text("", encoding="utf-8")
    with pytest.raises(CaptureFormatError, match="missing capture header"):
        read_capture(missing)


def test_header_is_frozen_and_versioned() -> None:
    header = make_capture().header
    with pytest.raises(ValidationError):
        header.baud = 9600
    with pytest.raises(ValidationError):
        CaptureHeader(
            format="openinputhub-uart-capture",
            version=2,
            device="SpaceController",
            baud=38400,
        )
