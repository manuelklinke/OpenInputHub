"""Strict JSON Lines format for raw UART captures."""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class CaptureFormatError(ValueError):
    """A capture file is syntactically or semantically invalid."""


class CaptureHeader(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    format: Literal["openinputhub-uart-capture"]
    version: Literal[1]
    device: str = Field(min_length=1)
    baud: Literal[38400]


class CaptureChunk(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    offset_ns: int = Field(ge=0)
    data: bytes


class UartCapture(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    header: CaptureHeader
    chunks: tuple[CaptureChunk, ...]

    @model_validator(mode="after")
    def validate_monotonic_offsets(self) -> "UartCapture":
        offsets = [chunk.offset_ns for chunk in self.chunks]
        if offsets != sorted(offsets):
            raise ValueError("capture offsets must be monotonically non-decreasing")
        return self


def write_capture(path: Path, capture: UartCapture) -> None:
    lines = [
        json.dumps(capture.header.model_dump(), separators=(",", ":"), ensure_ascii=False)
    ]
    for chunk in capture.chunks:
        record = {
            "offset_ns": chunk.offset_ns,
            "data_hex": chunk.data.hex(" "),
        }
        lines.append(json.dumps(record, separators=(",", ":"), ensure_ascii=False))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_capture(path: Path) -> UartCapture:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise CaptureFormatError(f"{path}: {error}") from error
    if not lines:
        raise CaptureFormatError(f"{path}: missing capture header")

    header_record = _read_json_object(path, 1, lines[0])
    try:
        header = CaptureHeader.model_validate(header_record)
    except ValidationError as error:
        raise CaptureFormatError(f"{path}:1: {error}") from error

    chunks: list[CaptureChunk] = []
    for line_number, line in enumerate(lines[1:], start=2):
        record = _read_json_object(path, line_number, line)
        data_hex = record.pop("data_hex", None)
        if not isinstance(data_hex, str):
            raise CaptureFormatError(
                f"{path}:{line_number}: data_hex must be a hexadecimal string"
            )
        try:
            compact = "".join(data_hex.split())
            if len(compact) % 2:
                raise ValueError("odd number of hexadecimal digits")
            data = bytes.fromhex(compact)
        except ValueError as error:
            raise CaptureFormatError(f"{path}:{line_number}: invalid data_hex: {error}") from error
        try:
            chunks.append(CaptureChunk.model_validate({**record, "data": data}))
        except ValidationError as error:
            raise CaptureFormatError(f"{path}:{line_number}: {error}") from error

    try:
        return UartCapture(header=header, chunks=tuple(chunks))
    except ValidationError as error:
        raise CaptureFormatError(f"{path}: {error}") from error


def _read_json_object(path: Path, line_number: int, line: str) -> dict[str, object]:
    try:
        value = json.loads(line)
    except json.JSONDecodeError as error:
        raise CaptureFormatError(f"{path}:{line_number}: {error.msg}") from error
    if not isinstance(value, dict):
        raise CaptureFormatError(f"{path}:{line_number}: expected a JSON object")
    return value
