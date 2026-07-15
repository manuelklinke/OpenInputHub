"""Immutable frames and wire encoding."""

from dataclasses import dataclass

from .constants import (
    FRAME_TERMINATOR,
    MAX_ENCODED_PAYLOAD,
    MAX_RAW_PAYLOAD,
    Selector,
)
from .crc import crc7_mmc
from .sevenbit import pack_7bit


@dataclass(frozen=True, slots=True)
class Frame:
    selector: Selector
    sequence: int
    payload: bytes

    def __post_init__(self) -> None:
        try:
            selector = Selector(self.selector)
        except ValueError as error:
            raise ValueError("selector must be between 0xf0 and 0xf7") from error
        object.__setattr__(self, "selector", selector)

        if not 0 <= self.sequence <= 0x7F:
            raise ValueError("sequence must be between 0 and 127")
        if len(self.payload) > MAX_RAW_PAYLOAD:
            raise ValueError("payload exceeds 105 raw bytes")


def encode_frame(frame: Frame) -> bytes:
    encoded_payload = pack_7bit(frame.payload)
    if len(encoded_payload) > MAX_ENCODED_PAYLOAD:
        raise ValueError("encoded payload exceeds 120 bytes")

    body = bytes(
        [frame.selector.value, frame.sequence, len(encoded_payload)]
    ) + encoded_payload
    return body + bytes([crc7_mmc(body), FRAME_TERMINATOR])
