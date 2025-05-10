def main() -> None:

    for u in range(0x80, 0x110000):  # 4s slow, at my MacBook lately

        try:
            encode = chr(u).encode()
        except UnicodeEncodeError:
            continue

        assert len(encode) >= 2, (encode, u)
        for i in range(1, len(encode)):
            head = encode[:i]

            try:
                head.decode()
                assert False, (head, encode, u)
            except UnicodeDecodeError:
                pass

            if some_decodable_startswith(head):
                continue

            print(head, f"0x{u:X}", encode)
            assert False, (head, encode, u)


def some_decodable_startswith(bytes_) -> bool:
    """Say if these Bytes start 1 or more UTF-8 Encodings of Chars"""

    suffixes = (b"\x80", b"\xbf", b"\x80\x80", b"\xbf\xbf", b"\x80\x80\x80", b"\xbf\xbf\xbf")

    for suffix in suffixes:
        suffixed = bytes_ + suffix
        try:
            decode = suffixed.decode()
            assert len(decode) == 1, (decode,)
            return True
        except UnicodeDecodeError:
            continue

    return False


main()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/demos/unicoders.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
