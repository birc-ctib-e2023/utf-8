"""
Decodes a string in UTF-8 (but encoded in hex).
"""

import argparse


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
    if byte >> 7 == 0b0:
        return 0
    if byte >> 5 == 0b110:
        return 1
    if byte >> 4 == 0b1110:
        return 2
    if byte >> 3 == 0b11110:
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


def main() -> None:
    """Decode an argument string."""
    argparser = argparse.ArgumentParser(description="Encode a string as UTF-8")
    argparser.add_argument("string", type=str)
    args = argparser.parse_args()
    seq = get_bytes(args.string)
    print("".join(chr(i) for i in decode(seq)))


if __name__ == '__main__':
    main()
