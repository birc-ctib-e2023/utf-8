"""
Decodes a string in UTF-8 (but encoded in hex).
"""
from __future__ import annotations


def get_bytes(x: str) -> list[int]:
    """
    Extract the individual bytes in the string x.

    >>> get_bytes('E282AC')
    [226, 130, 172]
    """
    return [int(x[i:i+2], base=16) for i in range(0, len(x), 2)]


def code_class(byte: int) -> int:
    """
    Get the code class for an encoding that starts with byte.

    >>> code_class(226)
    2
    """
    b = bits(byte)
    if b[7:] == 0b0:
        return 0
    if b[5:] == 0b110:
        return 1
    if b[4:] == 0b1110:
        return 2
    if b[3:] == 0b11110:
        return 3
    assert False, "Shouldn't happen"


# Masks for removing top bits
REMOVE_MASK_2 = 0b00111111
REMOVE_MASK_3 = 0b00011111
REMOVE_MASK_4 = 0b00001111


def decode(seq: list[int]) -> list[int]:
    """
    Translate a UTF-8 encoded sequence into a list of code points.
    """
    itr = iter(seq)
    res = []
    try:
        while True:
            byte1 = next(itr)
            match code_class(byte1):
                case 0:
                    res.append(byte1)
                case 1:
                    byte2 = next(itr)
                    res.append(
                        (REMOVE_MASK_3 & byte1) << 6 |
                        (REMOVE_MASK_2 & byte2)
                    )
                case 2:
                    byte2 = next(itr)
                    byte3 = next(itr)
                    res.append(
                        (REMOVE_MASK_3 & byte1) << 12 |
                        (REMOVE_MASK_2 & byte2) << 6 |
                        (REMOVE_MASK_2 & byte3)
                    )
                case 3:
                    byte2 = next(itr)
                    byte3 = next(itr)
                    byte4 = next(itr)
                    res.append(
                        (REMOVE_MASK_3 & byte1) << 18 |
                        (REMOVE_MASK_2 & byte2) << 12 |
                        (REMOVE_MASK_2 & byte3) << 6 |
                        (REMOVE_MASK_2 & byte4)
                    )
    except StopIteration:
        pass  # We are done

    return res


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
                j = j if j is not None else self._x.bit_length() + 1
                assert val.bit_length() <= j - i, "Value has too many bits."
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
