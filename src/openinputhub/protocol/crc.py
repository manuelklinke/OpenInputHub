"""CRC used by SpaceController UART v1."""


def crc7_mmc(data: bytes) -> int:
    crc = 0
    for byte in data:
        for bit_index in range(8):
            incoming = (byte >> (7 - bit_index)) & 1
            feedback = ((crc >> 6) & 1) ^ incoming
            crc = (crc << 1) & 0x7F
            if feedback:
                crc ^= 0x09
    return crc
