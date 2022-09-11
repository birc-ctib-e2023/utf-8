# This directory will be checked with pytest. It will examine
# all files that start with test_*.py and run all functions with
# names that start with test_

from utf8 import encode, decode


def test_reversible() -> None:
    """Test that encoding and then decoding gives us the same string."""
    print('enc:', encode('€'))
    print('dec:', decode(encode('€')))
    assert decode(encode('15€')) == '15€'
    assert decode(encode('Skåne')) == 'Skåne'
    assert decode(encode('你好, 世界')) == '你好, 世界'
    assert decode(encode('🎃🥳🤪')) == '🎃🥳🤪'
