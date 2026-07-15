from openinputhub.protocol.constants import Selector
from openinputhub.protocol.frame import Frame, encode_frame
from openinputhub.protocol.parser import FrameParser


def test_parser_accepts_fragmented_and_concatenated_frames() -> None:
    first = Frame(Selector.BUTTONS, 1, b"\x01\x00\x01")
    second = Frame(Selector.WHEEL, 2, b"\xff")
    wire = encode_frame(first) + encode_frame(second)
    parser = FrameParser()
    assert parser.feed(wire[:4]) == []
    assert parser.feed(wire[4:9]) == [first]
    assert parser.feed(wire[9:]) == [second]


def test_parser_recovers_after_noise_crc_and_bad_terminator() -> None:
    expected = Frame(Selector.MOTION, 7, bytes(12))
    valid = encode_frame(expected)
    bad_crc = bytearray(valid)
    bad_crc[-2] ^= 1
    bad_end = bytearray(valid)
    bad_end[-1] = 0
    parser = FrameParser()
    assert parser.feed(b"\x00\x8d" + bad_crc + bad_end + valid) == [expected]
    assert parser.stats.crc_errors == 1
    assert parser.stats.terminator_errors == 1
    assert parser.stats.bytes_discarded >= 2


def test_parser_rejects_length_above_protocol_limit_then_recovers() -> None:
    parser = FrameParser()
    expected = Frame(Selector.WHEEL, 4, b"\x01")
    valid = encode_frame(expected)
    assert parser.feed(bytes([Selector.MOTION, 0, 121]) + valid) == [expected]
    assert parser.stats.length_errors == 1


def test_parser_does_not_wait_on_truncated_frame_before_new_selector() -> None:
    parser = FrameParser()
    truncated = bytes([Selector.MOTION, 9, 120, 0, 0])
    expected = Frame(Selector.WHEEL, 4, b"\x01")
    assert parser.feed(truncated + encode_frame(expected)) == [expected]
    assert parser.stats.format_errors == 1


def test_parser_rejects_invalid_packed_payload_then_recovers() -> None:
    # Payload header bit 1 is unused because only one low byte follows it.
    invalid_body = bytes([Selector.WHEEL, 1, 2, 2, 0])
    from openinputhub.protocol.crc import crc7_mmc

    invalid = invalid_body + bytes([crc7_mmc(invalid_body), 0x8D])
    expected = Frame(Selector.WHEEL, 2, b"\x01")
    parser = FrameParser()
    assert parser.feed(invalid + encode_frame(expected)) == [expected]
    assert parser.stats.packing_errors == 1


def test_empty_chunks_are_noop() -> None:
    parser = FrameParser()
    assert parser.feed(b"") == []
    assert parser.stats.bytes_discarded == 0
