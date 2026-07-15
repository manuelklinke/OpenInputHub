"""Reversible 8-bit to 7-bit payload packing."""


def pack_7bit(raw: bytes) -> bytes:
    encoded = bytearray()
    for offset in range(0, len(raw), 7):
        group = raw[offset : offset + 7]
        header = 0
        low_bytes = bytearray()
        for index, byte in enumerate(group):
            header |= ((byte >> 7) & 1) << index
            low_bytes.append(byte & 0x7F)
        encoded.append(header)
        encoded.extend(low_bytes)
    return bytes(encoded)


def unpack_7bit(encoded: bytes) -> bytes:
    if any(byte >= 0x80 for byte in encoded):
        raise ValueError("encoded payload contains a non-7-bit byte")

    raw = bytearray()
    offset = 0
    while offset < len(encoded):
        remaining = len(encoded) - offset
        group_size = min(8, remaining)
        if group_size == 1:
            raise ValueError("7-bit group is missing group data")

        header = encoded[offset]
        data_count = group_size - 1
        if header >> data_count:
            raise ValueError("7-bit group has unused header bits set")

        for index, low_byte in enumerate(encoded[offset + 1 : offset + group_size]):
            raw.append(low_byte | (((header >> index) & 1) << 7))
        offset += group_size

    return bytes(raw)
