import pytest

from openinputhub.protocol.constants import Selector
from openinputhub.protocol.crc import crc7_mmc
from openinputhub.protocol.frame import Frame, encode_frame


def test_crc7_mmc_check_vector() -> None:
    assert crc7_mmc(b"123456789") == 0x75


def test_frame_golden_vector() -> None:
    frame = Frame(selector=Selector.WHEEL, sequence=3, payload=b"\xff")
    assert encode_frame(frame) == bytes.fromhex("f5 03 02 01 7f 2b 8d")


@pytest.mark.parametrize("sequence", [-1, 128])
def test_frame_rejects_invalid_sequence(sequence: int) -> None:
    with pytest.raises(ValueError, match="sequence"):
        Frame(Selector.WHEEL, sequence, b"")


def test_frame_rejects_oversized_payload() -> None:
    with pytest.raises(ValueError, match="payload"):
        Frame(Selector.CONTROL, 0, bytes(106))


def test_maximum_payload_encodes_to_protocol_limit() -> None:
    encoded = encode_frame(Frame(Selector.CONTROL, 127, bytes(range(105))))
    assert encoded[2] == 120
    assert len(encoded) == 125
