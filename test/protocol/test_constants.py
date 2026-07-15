from openinputhub.protocol.constants import (
    FRAME_TERMINATOR,
    MAX_ENCODED_PAYLOAD,
    PROTOCOL_VERSION,
    ControlOpcode,
    Selector,
)


def test_protocol_constants_are_frozen() -> None:
    assert PROTOCOL_VERSION == (1, 0)
    assert FRAME_TERMINATOR == 0x8D
    assert MAX_ENCODED_PAYLOAD == 120
    assert [member.value for member in Selector] == list(range(0xF0, 0xF8))
    assert ControlOpcode.ACK == 0x70
    assert ControlOpcode.ERROR == 0x71
