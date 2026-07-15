"""Incremental, resynchronizing SpaceController frame parser."""

from dataclasses import dataclass

from .constants import FRAME_TERMINATOR, MAX_ENCODED_PAYLOAD, Selector
from .crc import crc7_mmc
from .frame import Frame
from .sevenbit import unpack_7bit

_SELECTOR_VALUES = {selector.value for selector in Selector}


@dataclass(slots=True)
class ParserStats:
    bytes_discarded: int = 0
    format_errors: int = 0
    length_errors: int = 0
    crc_errors: int = 0
    terminator_errors: int = 0
    packing_errors: int = 0


class FrameParser:
    def __init__(self) -> None:
        self._buffer = bytearray()
        self.stats = ParserStats()

    def feed(self, chunk: bytes) -> list[Frame]:
        self._buffer.extend(chunk)
        frames: list[Frame] = []

        while self._buffer:
            if self._buffer[0] not in _SELECTOR_VALUES:
                self._discard_one()
                continue

            if len(self._buffer) < 3:
                break

            sequence = self._buffer[1]
            encoded_length = self._buffer[2]
            if sequence > 0x7F or encoded_length > 0x7F:
                self.stats.format_errors += 1
                self._discard_one()
                continue
            if encoded_length > MAX_ENCODED_PAYLOAD:
                self.stats.length_errors += 1
                self._discard_one()
                continue

            frame_length = encoded_length + 5
            if len(self._buffer) < frame_length:
                if self._has_early_boundary(start=3):
                    self.stats.format_errors += 1
                    self._discard_one()
                    continue
                break

            if any(byte >= 0x80 for byte in self._buffer[3 : frame_length - 1]):
                self.stats.format_errors += 1
                self._discard_one()
                continue

            if self._buffer[frame_length - 1] != FRAME_TERMINATOR:
                self.stats.terminator_errors += 1
                self._discard_one()
                continue

            body = bytes(self._buffer[: frame_length - 2])
            expected_crc = self._buffer[frame_length - 2]
            if crc7_mmc(body) != expected_crc:
                self.stats.crc_errors += 1
                self._discard_one()
                continue

            encoded_payload = bytes(self._buffer[3 : frame_length - 2])
            try:
                payload = unpack_7bit(encoded_payload)
            except ValueError:
                self.stats.packing_errors += 1
                self._discard_one()
                continue

            frames.append(
                Frame(
                    selector=Selector(self._buffer[0]),
                    sequence=sequence,
                    payload=payload,
                )
            )
            del self._buffer[:frame_length]

        return frames

    def _has_early_boundary(self, start: int) -> bool:
        return any(
            byte == FRAME_TERMINATOR or byte in _SELECTOR_VALUES
            for byte in self._buffer[start:]
        )

    def _discard_one(self) -> None:
        del self._buffer[0]
        self.stats.bytes_discarded += 1
