import pytest
from hypothesis import given, strategies as st

from openinputhub.protocol.sevenbit import pack_7bit, unpack_7bit


def test_known_pack_vector() -> None:
    assert pack_7bit(bytes.fromhex("80 01 ff")) == bytes.fromhex("05 00 01 7f")
    assert unpack_7bit(bytes.fromhex("05 00 01 7f")) == bytes.fromhex("80 01 ff")


@given(st.binary(max_size=105))
def test_pack_round_trip(raw: bytes) -> None:
    encoded = pack_7bit(raw)
    assert unpack_7bit(encoded) == raw
    assert all(byte < 0x80 for byte in encoded)


def test_empty_payload_stays_empty() -> None:
    assert pack_7bit(b"") == b""
    assert unpack_7bit(b"") == b""


def test_unpack_rejects_unused_header_bits() -> None:
    with pytest.raises(ValueError, match="unused header bits"):
        unpack_7bit(bytes.fromhex("02 00"))


def test_unpack_rejects_header_without_data() -> None:
    with pytest.raises(ValueError, match="missing group data"):
        unpack_7bit(b"\x00")


def test_unpack_rejects_non_seven_bit_byte() -> None:
    with pytest.raises(ValueError, match="7-bit"):
        unpack_7bit(b"\x00\x80")
