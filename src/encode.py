"""
Encode a string as UTF-8 and write it in hex.
"""

import argparse


def code_points(x: str) -> list[int]:
    """
    Turn a string into the corresponding unicode code points.

    >>> code_points("hello, world!")
    [104, 101, 108, 108, 111, 44, 32, 119, 111, 114, 108, 100, 33]

    >>> code_points("Здравей свят")
    [1047, 1076, 1088, 1072, 1074, 1077, 1081, 32, 1089, 1074, 1103, 1090]

    >>> code_points("你好, 世界")
    [20320, 22909, 44, 32, 19990, 30028]
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


def main() -> None:
    """Encode an argument string."""
    argparser = argparse.ArgumentParser(description="Encode a string as UTF-8")
    argparser.add_argument("string", type=str)
    args = argparser.parse_args()
    cps = code_points(args.string)
    enc = encode_codepoint_seq(cps)
    print(''.join(f"{cp:0>2x}" for cp in enc))


if __name__ == '__main__':
    main()
