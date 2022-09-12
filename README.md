# Encoding and decoding UTF-8

Here is a slightly more complicated encoding/decoding problem: encoding unicode text as UTF-8.

[Unicode](https://en.wikipedia.org/wiki/Unicode) is a standard that assigns to every character, used in real or imagined languages, a unique integer code, called a *code point*. You can encode every such code point in a 32-bit integer, but this is wasteful of memory since most text do not use all possible unicode characters. Instead, it makes sense to use less memory for characters you use often, and more memory for those characters you rarely use.

For western languages, the encoding choice is typically [UTF-8](https://en.wikipedia.org/wiki/UTF-8). There, all the letters from the Latin alphabet plus most common punctuation characters can be encoded in one byte (8 bits), while characters from, say, the Cyrillic alphabet requires two bytes, Chinese characters three bytes, and emoticons require four.

How many bytes you need to represent a unicode code point depends on how many significant bits the integer of the code point has. If you have a number that uses less than eight bits, so the most significant bit is at position seven or less, then you can use the number as it is.

```
   0b0xxxxxxx -> 0b0xxxxxxx
```

(read this as the binary number (`0b`) starts with a zero and the seven bits that follows are copied as they are).

If you use up to 11 bits, you need to encode it in two bytes. The first byte should start with the bits `0b110` and the second with `0b10` and you split the original bits like this:

```
    0b0yyyyyxxxxxx -> 0b110yyyyy 0b10xxxxxx
```

that is, your first byte starts with `0b110` and then the first five bits of the code point, and the second byte starts with `0b10` and then the remaining six bits from the code point.

If you have between 11 and 16 bits in the code point, you split the bits as this:

```
    0b0zzzzyyyyyyxxxxxx -> 0b1110zzzz 0b10yyyyyy 0b10xxxxxx
```

Finally, if you are using more bits (and you can only use up to 21 for a code point) then you split them like this:

```
    0b0wwwzzzzzzyyyyyyxxxxxx -> 0b11110www 0b10zzzzzz 0b10yyyyyy 0b10xxxxxx
```

To transate a code point integer into integers that only take up eight bits, you need code to manipulate individual bits. For that, I have written a class `bits` that you can use. If you have an integer `x`, then `b = bits(x)` translates it into this class, and in the class you can extract bits: `b[i:j]` gives you bit `i` to `j`, you can assign to bits, `b[i:j] = v` sets the bits `i` to `j` to `v`, and you can add a mask (set the topmost bits, assuming we only use eight) with `b.mask(0b1110)`. When you are done, you can get an integer back using `int(b)`.

You can check how many significant bits you have in a number using `x.bit_length()`.

You need to implement the following functions:

```python
def code_points(x: str) -> list[int]:
    ...
```

It should translate a string into a list of code points. That is easy in Python, since it just means calling `ord` on each character in the string.

```python
def encode_codepoint(codepoint: int) -> str
    ...
```

should translate a code point (integer) into one to four bytes using the rules mentioned above. We encode the bytes as a string of hex numbers with two characters per byte. This isn't, of course, how we normally do with strings on our computers, since it uses twice as much memory as UTF-8 should, but working with strings rather than binary data is slightly easier.

If `b` is a byte (as an integer), then `f"{b:>2x}"` will give you a hex value in two characters.

```python
def get_bytes(x: str) -> list[int]:
    ...
```

should split a UTF-8 string into individual bytes and return them as a list. This means taking a string of hex-encoded UTF-8 strings, extracting the characters pairwise, and then transating the byte-strings into integers.

```python
def decode_bytes(x: list[int]) -> list[int]:
    ...
```

Takes a list of bytes (as returned by `get_bytes()`) and translate those into a list of code points. Here, you need to check the first bits of the first byte, figure out how many are used for a code point based on the initial bits, then get those bytes and reassemle them by running the split in reverse. Then you continue with the next byte after those you have already used.

If you implement these functions, then the `encode()` and `decode()` functions should handle the rest.

