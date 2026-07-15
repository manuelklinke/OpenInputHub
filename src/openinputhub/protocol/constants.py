from enum import IntEnum

PROTOCOL_VERSION = (1, 0)
FRAME_TERMINATOR = 0x8D
MAX_ENCODED_PAYLOAD = 120
MAX_RAW_PAYLOAD = 105


class Selector(IntEnum):
    LINK = 0xF0
    IDENTITY = 0xF1
    CAPABILITIES = 0xF2
    MOTION = 0xF3
    BUTTONS = 0xF4
    WHEEL = 0xF5
    DIAGNOSTICS = 0xF6
    CONTROL = 0xF7


class ControlOpcode(IntEnum):
    SET_LEDS = 0x01
    SET_DISPLAY = 0x02
    CLEAR_DISPLAY = 0x03
    ACK = 0x70
    ERROR = 0x71
