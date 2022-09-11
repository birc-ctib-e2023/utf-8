"""
Decodes a string in UTF-8 (but encoded in hex).
"""
from __future__ import annotations


# Helper class...

class bits:
    """Wrap an integer to give us easier access to bits."""

    _x: int

    def __init__(self, x: int) -> None:
        """Create a wrapper."""
        self._x = x

    def __getitem__(self, idx: int | slice) -> int:
        """
        Extract specific bits.

        Indexing with a single integer, like x[i], gives you the bit
        at index i, and indexing with a slice, like x[i:j], gives you
        bits from i up to (but not including) j.

        >>> x = bits(0b110011)
        >>> bin(x[0])
        '0b1'
        >>> bin(x[2])
        '0b0'
        >>> bin(x[1:5])
        '0b1001'
        """
        match idx:
            case slice(start=i, stop=j):
                i = i if i is not None else 0
                mask = (1 << j) - 1 if j is not None else ~0
                return (self._x & mask) >> i
            case i:
                return (self._x >> i) & 1

    def __setitem__(self, idx: int | slice, val: int) -> bits:
        """
        Set specific bits.

        Indexing with a single integer, like x[i], gives you the bit
        at index i, and indexing with a slice, like x[i:j], gives you
        bits from i up to (but not including) j.

        >>> x = bits(0)
        >>> x[:3] = 0b101
        >>> x
        bits(0b101)
        >>> x[3:6] = 0b111
        >>> x
        bits(0b111101)
        """
        match idx:
            case slice(start=i, stop=j):
                i = i if i is not None else 0
                j = j if j is not None else 33  # assuming 32-bit ints
                if val.bit_length() > j - i:
                    raise ValueError(f"{bin(val)} has too many bits")
                clear_mask = ~(((1 << j) - 1) ^ ((1 << i) - 1))
                self._x &= clear_mask  # clear the current bits
                self._x |= (val << i)  # and set the new ones
        return self

    def __str__(self) -> str:
        """Give textual representation."""
        return f"{bin(self._x)}"

    def __repr__(self) -> str:
        """Give textual representation."""
        return f"bits({bin(self._x)})"

    def __int__(self) -> int:
        """Translate the bits back to an integer."""
        return self._x


# Encoding

def code_points(x: str) -> list[int]:
    """
    Turn a string into the corresponding unicode code points.

    >>> code_points("hello, world!")
    [104, 101, 108, 108, 111, 44, 32, 119, 111, 114, 108, 100, 33]

    >>> code_points("Здравей свят")
    [1047, 1076, 1088, 1072, 1074, 1077, 1081, 32, 1089, 1074, 1103, 1090]

    >>> code_points("你好, 世界")
    [20320, 22909, 44, 32, 19990, 30028]

    >>> code_points("🎃🥳🤪")
    [127875, 129395, 129322]
    """
    return [ord(c) for c in x]


def code_class(codepoint: int) -> int:
    """
    Return the encoding class (number of bytes) for a code point.

    >>> [code_class(cp) for cp in code_points("hello, world!")]
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    >>> [code_class(cp) for cp in code_points("hej Skåne!")]
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]

    >>> [code_class(cp) for cp in code_points("Здравей свят")]
    [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1]

    >>> [code_class(cp) for cp in code_points("你好, 世界")]
    [2, 2, 0, 0, 2, 2]

    """
    bits = codepoint.bit_length()
    return \
        0 if bits <= 7 else \
        1 if bits <= 11 else \
        2 if bits <= 16 else \
        3


# Bit masks
MASK_10 = 0b10000000
MASK_110 = 0b11000000
MASK_1110 = 0b11100000
MASK_11110 = 0b11110000

# Table of masks and bits
ENCODE_TABLE = [
    ((0, 0, 8), ),  # Class 0, no mask and just the low seven bits
    ((MASK_110, 6, 11), (MASK_10, 0, 6)),
    ((MASK_1110, 12, 16), (MASK_10, 6, 12), (MASK_10, 0, 6)),
    ((MASK_11110, 18, 21), (MASK_10, 12, 18), (MASK_10, 6, 12), (MASK_10, 0, 6))
]


def extract_bits(x: int, i: int, j: int) -> int:
    """
    Get bits from index i to j in word x.

    >>> extract_bits(0b10101100, 0, 0)
    0
    >>> extract_bits(0b10101100, 2, 5)
    3
    >>> extract_bits(0b10101100, 4, 8)
    10

    """
    x &= (1 << j) - 1  # Mask out the low j
    return x >> i      # and shift away the low i


def encode_codepoint(codepoint: int) -> list[int]:
    """
    Encode a code point as one to four bytes.

    >>> encode_codepoint(ord('h'))
    [104]

    >>> encode_codepoint(ord('в'))
    [208, 178]

    >>> encode_codepoint(ord('世'))
    [228, 184, 150]
    """
    return [
        mask | extract_bits(codepoint, i, j)
        for mask, i, j in ENCODE_TABLE[code_class(codepoint)]
    ]


def encode_codepoint_seq(codepoints: list[int]) -> list[int]:
    """
    Encode all code points in a list

    >>> encode_codepoint_seq([ord('h')])
    [104]

    >>> encode_codepoint_seq([ord('в')])
    [208, 178]

    >>> encode_codepoint_seq([ord('世')])
    [228, 184, 150]
    """
    enc = []
    for cp in codepoints:
        enc.extend(encode_codepoint(cp))
    return enc


def encode(x: str) -> str:
    """
    Encode a string as UTF-8 (written in hex).

    >>> encode('€')
    'e282ac'
    """
    return ''.join(
        f"{cp:>2x}" for cp in encode_codepoint_seq(code_points(x))
    )


# Decoding

def get_bytes(x: str) -> list[int]:
    """
    Extract the individual bytes in the string x.

    >>> get_bytes('E282AC')
    [226, 130, 172]
    """
    return [int(x[i:i+2], base=16) for i in range(0, len(x), 2)]


def decode_bytes(x: list[int]) -> list[int]:
    """
    Translate a UTF-8 encoded sequence into a list of code points.
    """
    itr = iter(x)
    res = []
    try:
        while True:
            code_point = bits(0)

            byte = bits(next(itr))
            if byte[7] == 0:
                code_point[:] = byte[:]
            elif byte[5:] == 0b110:
                code_point[6:] = byte[:5]
                code_point[:6] = bits(next(itr))[:6]
            elif byte[4:] == 0b1110:
                code_point[12:] = byte[:4]
                code_point[6:12] = bits(next(itr))[:6]
                code_point[:6] = bits(next(itr))[:6]
            elif byte[3:] == 0b11110:
                code_point[18:] = byte[:3]
                code_point[12:18] = bits(next(itr))[:6]
                code_point[6:12] = bits(next(itr))[:6]
                code_point[:6] = bits(next(itr))[:6]
            else:
                raise ValueError(f"Illegal opcode byte {byte}")

            res.append(int(code_point))

    except StopIteration:
        pass  # We are done

    return res


def decode(x: str) -> str:
    """
    Translate a UTF-8 encoded sequence into a list of code points.
    """
    return ''.join(
        chr(cp) for cp in decode_bytes(get_bytes(x))
    )
