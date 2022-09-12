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

    def __getitem__(self, idx: int | slice) -> bits:
        """
        Extract specific bits.

        Indexing with a single integer, like x[i], gives you the bit
        at index i, and indexing with a slice, like x[i:j], gives you
        bits from i up to (but not including) j.

        >>> x = bits(0b110011)
        >>> x[0]
        bits(0b1)
        >>> x[2]
        bits(0b0)
        >>> x[1:5]
        bits(0b1001)
        """
        match idx:
            case slice(start=i, stop=j):
                i = i if i is not None else 0
                mask = (1 << j) - 1 if j is not None else ~0
                return bits((self._x & mask) >> i)
            case i:
                return bits((self._x >> i) & 1)

    def __setitem__(self, idx: int | slice, val: int | bits) -> bits:
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
        val = val._x if isinstance(val, bits) else val
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

    def __eq__(self, other: bits | int) -> bool:
        """Compare with another bits or an int."""
        other = other._x if isinstance(other, bits) else other
        return self._x == other

    def mask(self, mask: int) -> bits:
        """
        Add mask to the top mask.bit_length() bits.

        This method assumes that self is a single byte.

        >>> bits(0b00001111).mask(0b11)
        bits(0b11001111)
        """
        self._x |= mask << (8 - mask.bit_length())
        return self


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
    ...


def encode_codepoint(codepoint: int) -> str:
    """
    Encode a code point as one to four bytes, representing them in
    hex with two digits per byte.

    >>> encode_codepoint(ord('h'))
    '68'

    >>> encode_codepoint(ord('в'))
    'd0b2'

    >>> encode_codepoint(ord('世'))
    'e4b896'

    >>> encode_codepoint(ord("🎃"))
    'f09f8e83'
    """
    ...


def encode(x: str) -> str:
    """
    Encode a string as UTF-8 (written in hex).

    >>> encode('15€')
    '3135e282ac'

    >>> encode('你好, 世界')
    'e4bda0e5a5bd2c20e4b896e7958c'
    """
    return ''.join(
        encode_codepoint(cp) for cp in code_points(x)
    )


# Decoding

def get_bytes(x: str) -> list[int]:
    """
    Extract the individual bytes in the string x.

    >>> get_bytes('E282AC')
    [226, 130, 172]
    """
    ...


def decode_bytes(x: list[int]) -> list[int]:
    """
    Translate a UTF-8 encoded sequence into a list of code points.
    """
    ...


def decode(x: str) -> str:
    """
    Translate a UTF-8 encoded sequence into a list of code points.

    >>> decode('3135e282ac')
    '15€'

    >>> decode('e4bda0e5a5bd2c20e4b896e7958c')
    '你好, 世界'
    """
    return ''.join(
        chr(cp) for cp in decode_bytes(get_bytes(x))
    )
