#!/usr/bin/env python3

r"""
usage: ptybreakout.py [-h]

mix two Breakout Balls into Sh Terminal I/O

options:
  -h, --help  show this help message and exit

lots of docs:
  https://unicode.org/charts/PDF/U0000.pdf
  https://unicode.org/charts/PDF/U0080.pdf
  https://en.wikipedia.org/wiki/ANSI_escape_code
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
  https://www.ecma-international.org/publications-and-standards/standards/ecma-48
    /wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf

examples:

  demos/ptybreakout.py --help  # show help and exit zero
  demos/ptybreakout.py  # show examples and exit zero
  demos/ptybreakout.py --  # mix two Breakout Balls into Sh Terminal I/O
"""

# code reviewed by people and by Black, Flake8, & Flake8-Import-Order


import __main__
import os
import pty
import random
import re
import select
import shlex
import sys
import textwrap


default_sh = "sh"
ENV_SHELL = os.getenv("SHELL", default_sh)


PATCH_DOC = """
    Supported escape sequences:
    ~?  - this message
    ~~  - send the escape character by typing it twice
    (Note that escapes are only recognized immediately after newline.)
"""

# todo: ~+  - add a Breakout Ball
# todo: ~-  - remove a Breakout Ball


# Classic Ssh defines ~? to print these Chars of Help, and more


def main() -> None:
    """Run from the Sh Command Line"""

    # Print help & exit, except at:  demos/ptyspawn.py --

    doc = __main__.__doc__.strip()
    testdoc = textwrap.dedent(doc.partition("examples:\n")[-1]).strip()

    shargs = sys.argv[1:]
    if not shargs:
        print("\n" + testdoc + "\n")
        sys.exit(0)
    if shargs != "--".split():
        print(doc)
        sys.exit(0)

    # Wrap the I/O of a Sh Terminal

    shline = ENV_SHELL
    argv = shlex.split(shline)

    pty_spawn_argv(argv)


def pty_spawn_argv(argv) -> None:  # noqa C901
    """Wrap the I/O of a Sh Terminal"""

    patch_doc = textwrap.dedent(PATCH_DOC).strip()

    ij = [ord("."), ord("\r")]
    ts = TerminalShadow()

    sprites: list[TerminalSprite]
    sprites = list()

    def fd_patch_output(fd):
        """Take the chance to patch Output, or don't"""

        obytes = os.read(fd, 0x400)
        ts.write_bytes(data=obytes)

        return obytes

    def fd_patch_input(fd):
        """Take the chance to patch Input, or don't"""

        # Pull Bytes till some Bytes found to forward

        while True:
            for sprite in sprites:
                while not sys_stdio_kbhit(sys.stderr, timeout=0.100):
                    sprite.step_ahead()

            ibytes = os.read(fd, 0x400)

            # Consider 3 Bytes at a time

            pbytes = bytearray()
            for k in ibytes:
                (i, j) = ij
                ij[::] = [j, k]

                # Take the 2 Bytes b"\r~" to mean hold the b"~" till next Byte

                if (j, k) == (ord("\r"), ord("~")):
                    continue

                # Take the 3 Bytes b"\r~~" to mean forward the 2 Bytes b"\r~"

                if (i, j) == (ord("\r"), ord("~")):
                    if (i, j, k) == (ord("\r"), ord("~"), ord("~")):
                        pbytes.append(k)
                        continue

                    # Take the 3 Bytes b"\r~?" to mean explain thyself

                    if (i, j, k) == (ord("\r"), ord("~"), ord("?")):
                        print("~?", end="\r\n")
                        print("\r\n".join(patch_doc.splitlines()), end="\r\n")
                        continue

                    # Take the 3 Bytes b"\r~+" to mean add a Breakout Ball

                    if (i, j, k) == (ord("\r"), ord("~"), ord("+")):
                        sprite = TerminalSprite(ts)
                        sprites.append(sprite)
                        continue

                    # Take the 3 Bytes b"\r~-" to mean remove a Breakout Ball

                    if (i, j, k) == (ord("\r"), ord("~"), ord("-")):
                        if sprites:
                            sprite = sprites.pop()
                        continue

                    # Else forward the b"~" of b"\r~" with the next Byte

                    pbytes.append(j)
                    pbytes.append(k)
                    continue

                # Else forward the Byte immediately

                pbytes.append(k)

            # Return Bytes to forward them

            if pbytes:
                return pbytes

    pty.spawn(argv, master_read=fd_patch_output, stdin_read=fd_patch_input)

    if False:
        print("==== OUTPUT WAS ====")
        print("\n".join(ts.rows))
        print("====")

    print(f"{len(sprites)} Sprites walked {list(_.steps for _ in sprites)} Steps")

    # compare 'def read' patching output for https://docs.python.org/3/library/pty.html


#
# Keep up a guess of what the Sh Terminal looks like
#


# LOG = open("o.out", "w")  # jitter Sun 28/Jan
LOG = open(os.devnull, "w")

LOG.write("\n")  # once
LOG.write("\n")  # twice
LOG.flush()


class TerminalShadow:
    """Keep up a guess of what one Sh Terminal looks like"""

    rows: list[str]
    rows = list()  # Rows of Output Text Characters

    x = 0  # Cursor Column
    y = 0  # Cursor Row

    holds = bytearray()  # partial Packet of Output Bytes

    def write_bytes(self, data):  # noqa C901
        """Keep up a guess of what one Sh Terminal looks like"""

        log = LOG

        holds = self.holds
        rows = self.rows

        if False:
            log.write("\n")
            log.write("\n")
            log.write("{}\n".format(f"{data=}"))
            log.flush()

        # Split the Output Bytes into Packets

        holds.extend(data)
        while holds:
            held_bytes = bytes(holds)
            seq = bytes_take_startswith_else(held_bytes)
            if not seq:
                break

            holds[::] = holds[len(seq) :]

            log.write("{}\n".format(f"{self.y=} {self.x=} {seq=}"))
            log.flush()

            # Take C0_CONTROLS as moving the (Y, X) Cursor

            if seq[:1] in C0_BYTES:
                if seq == b"\b":
                    self.x = max(0, self.x - 1)
                elif seq == b"\r":
                    self.x = 0
                elif seq == b"\n":
                    self.y += 1
                else:
                    pass

                continue

            # Find the Row

            while self.y >= len(rows):
                rows.append("")

            # Overlay or grow the Row

            row = rows[self.y]

            decode = seq.decode()
            for ch in decode:
                while self.x >= len(row):
                    row += " "
                row = row[: self.x] + ch + row[self.x + 1 :]
                self.x += 1

            rows[self.y] = row


def sys_stdio_kbhit(stdio, timeout=None) -> list[int]:  # 'timeout' in seconds
    """Wait till next Input Byte, else till Timeout, else till forever"""

    rlist: list[int] = [stdio]
    wlist: list[int] = list()
    xlist: list[int] = list()

    (alt_rlist, _, _) = select.select(rlist, wlist, xlist, timeout)

    return alt_rlist


#
# Name some of the C0 Control Bytes
#


NUL = b"\0"  # 00/00 Null
BEL = b"\a"  # 00/07 Bell
BS = b"\b"  # 00/08 Backspace
CR = b"\r"  # 00/13 Carriage Return
CRLF = b"\r\n"  # 00/13 00/10 Carriage Return + Line Feed
LF = b"\n"  # 00/10 Line Feed


#
# Name some Byte Categories outside of the 95 (0x5F) Text 7-bit US-Ascii Bytes
#


C0_BYTES = bytes(_ for _ in range(0, 0x20)) + b"\x7F"
C1_BYTES = bytes(_ for _ in range(0x80, 0xA0))  # not U+00A0, U+00AD
UTF8_START_BYTES = bytes(_ for _ in range(0xC2, 0xF5))

assert len(C0_BYTES) == 0x21 == 33 == (128 - 95)
assert len(C1_BYTES) == 0x20 == 32
assert len(UTF8_START_BYTES) == 0x33 == 51

# todo: test writing C1_BYTES, like into macOS Terminal


#
# Name the Bytes that split Raw Terminal Bytes into Chords
#


ESC = b"\x1B"  # 01/11 Escape

CSI = b"\x1B["  # 01/11 05/11 Control Sequence Introducer  # till rb"[\x30-\x7E]"
OSC = b"\x1B]"  # 01/11 05/13 Operating System Command  # till BEL, CR, Esc \ ST, etc
_DCSG0 = b"\x1B("  # 01/11 02/08 Designate G0 Character Set
SS3 = b"\x1BO"  # 01/11 04/15 Single Shift Three

CsiStartPattern = b"\x1B\\[" rb"[\x30-\x3F]*[\x20-\x2F]*"  # leading Zeroes allowed
CsiEndPattern = rb"[\x40-\x7E]"
CsiPattern = CsiStartPattern + CsiEndPattern
# Csi Patterns define many Pm, Pn, and Ps, but not the Pt of Esc ] OSC Ps ; Pt BEL
# in 5.4 Control Sequences of ECMA-48_5th 1991

MouseThreeByteStartPattern = b"\x1B\\[" rb"M"
MouseSixByteEndPattern = b"\x1B\\[" rb"M..."  # MPR X Y


#
# Take one whole Byte Sequence, else zero Bytes
#


def bytes_take_startswith_else(data: bytes) -> bytes:
    """Take 1 defined whole Terminal Input/Output Byte Sequence, else zero Bytes"""

    assert not isinstance(data, bytearray), (type(data),)

    seq = b""

    if data:
        seq_else = _bytes_take_mouse_six_else(data)
        if seq_else is None:
            seq_else = _bytes_take_c0_plus_else(data)  # would misread Mouse Six
            if seq_else is None:
                seq_else = _bytes_take_much_utf8_else(data)  # would misread C0 Esc
                if seq_else is None:
                    seq = _bytes_take_one(data)  # would misread partial UTF-8

                    assert len(seq) == 1, (seq, data)
                    assert seq[0] >= 0x80, (seq, data)
                    assert seq not in UTF8_START_BYTES, (seq, data)

                    seq_else = seq

                    # thus, an "invalid start byte" of UTF-8

        seq = seq_else

    return seq  # might be empty, might not be UTF-8, is not None

    # does misread Fn⌃⌥Delete b"\x1B\x1B[3;5~" as (b"\x1B", b"\x1B[3;5~")


def _bytes_take_mouse_six_else(data) -> bytes | None:
    """Take 1 whole Mouse Six Byte Report, else zero Bytes while partial, else None"""

    assert data, data  # not empty here

    assert MouseThreeByteStartPattern == b"\x1B\\[" rb"M"
    assert MouseSixByteEndPattern == b"\x1B\\[" rb"M..."  # MPR X Y
    assert len(MouseThreeByteStartPattern) == 4  # pattern of 4 Bytes to take 3 Bytes
    assert len(MouseSixByteEndPattern) == 7  # pattern of 7 Bytes to take 6 Bytes

    # Don't say block for 6 Bytes till given Esc [ M

    m0 = re.match(rb"^" + MouseThreeByteStartPattern + rb"$", string=data)
    if not m0:
        return None

    # Do say block for 6 Bytes when given Esc [ M

    mn = re.match(rb"^" + MouseSixByteEndPattern + rb"$", string=data)
    if not mn:
        return b""  # partial Mouse Six Byte Report

    # Do take 6 Bytes when given 6 Bytes after finding Esc [ M

    seq = mn.string[mn.start() : mn.end()]
    assert len(seq) == 6

    return seq  # not empty


def _bytes_take_c0_plus_else(data) -> bytes | None:
    """Take 1 whole C0 Control Sequence, else zero Bytes while partial, else None"""

    assert data, data  # not empty here

    # Don't say block for Bytes till given a C0 Control Byte

    head = data[:1]
    if head not in C0_BYTES:
        return None

    # Do take a C0 Control Byte by itself, other than Esc

    assert ESC == b"\x1B"

    if head != b"\x1B":
        return head  # doesn't say block for \r\n after \r, like Screen Writers do

    # Take 1 whole C0 Esc Control Sequence, else zero Bytes while partial, else None

    seq = _bytes_take_c0_esc_etc_else(data)

    return seq  # not empty


def _bytes_take_c0_esc_etc_else(data) -> bytes:  # noqa C901
    """Take 1 whole C0 Esc Control Sequence, else zero Bytes while partial, else None"""

    assert data.startswith(b"\x1B"), (data,)  # given Esc already here

    assert ESC == b"\x1B"
    assert CsiStartPattern == b"\x1B\\[" rb"[\x30-\x3F]*[\x20-\x2F]*"
    assert CsiEndPattern == rb"[\x40-\x7E]"

    assert data.startswith(ESC), data

    # Do say block for the Byte after Esc

    if not data[1:]:
        return b""  # partial C0 Esc Control Sequence

    esc_plus = data[:2]
    assert esc_plus[:1] == b"\x1B", (esc_plus,)

    # Do say block for the Byte after Esc O,
    # such as the Single Shift Three (SS3) of F1 F2 F3 F4

    assert SS3 == b"\x1BO"

    if esc_plus == b"\x1BO":
        if not data[2:]:
            return b""  # partial C0 SS3 Control Sequence

        ss3_plus = data[:3]
        return ss3_plus

    # Do say block for the Byte after Esc (,
    # such as the VT100's 01/11 02/08 Designate G0 Character Set

    assert _DCSG0 == b"\x1B("

    if esc_plus == b"\x1B(":
        if not data[2:]:
            return b""  # partial C0 SS3 Control Sequence

        _dcsg0_plus = data[:3]
        return _dcsg0_plus

        # todo: port _DCSG0 into byo/byotty.py

    # Take Esc with a Text Byte of 7-Bit US-Ascii as a Byte Pair,
    # and take Esc alone when given before Esc or Control or not 7-bit US-Ascii

    if esc_plus != b"\x1B[":  # CSI
        if (esc_plus[-1:] in C0_BYTES) or (esc_plus[-1] >= 0x80):
            return b"\x1B"

        if esc_plus == b"\x1B]":  # OSC
            find = data.find(b"\x07")
            if find < 0:  # todo: ugh, unbounded
                return b""

            find_plus = find + len(b"\x07")
            osc_seq = data[:find_plus]

            return osc_seq  # todo: port OSC into byo/byotty.py

        return esc_plus

    # Do say block for the Bytes after Esc [

    assert ESC == b"\x1B"
    assert CSI == b"\x1B["

    assert data.startswith(CSI), data

    m0 = re.match(rb"^" + CsiStartPattern + rb"$", string=data)
    if m0:
        return b""  # partial C0 CSI Control Sequence

    # Take one whole Esc [ Sequence, or settle for Esc [ begun but cut short

    m1 = re.match(rb"^" + CsiStartPattern, string=data)
    assert m1, (m1, data)

    start_seq = m1.string[m1.start() : m1.end()]
    end_seq = m1.string[m1.end() :][:1]
    seq = start_seq + end_seq

    mn = re.match(rb"^" + CsiEndPattern + rb"$", string=end_seq)
    if not mn:
        return start_seq

    return seq  # not empty


def _bytes_take_much_utf8_else(data) -> bytes | None:
    """Take 1 or more whole UTF-8 Encodings of Text Chars"""

    assert data, data  # not empty here
    assert data[0] not in C0_BYTES, (bytes,)  # UTF-8 decodes C0 Bytes as themselves

    seq = None
    for index in range(len(data)):
        length = index + 1

        if data[length - 1] in C0_BYTES:
            break

        try_seq = data[:length]
        try:
            _ = try_seq.decode()
        except UnicodeDecodeError as exc:
            if "invalid start byte" not in str(exc):
                assert "unexpected end of data" in str(exc), str(exc)
                if length < len(data):
                    continue

                return b""  # partial UTF-8 Encoding

            if seq:
                break  # complete UTF-8 Encoding before an Invalid Start Byte

            assert try_seq[0] >= 0x80, (try_seq, data)
            assert try_seq not in UTF8_START_BYTES, (try_seq, data)

            return None  # Invalid Start Byte

        seq = try_seq

    return seq  # not empty


def _bytes_take_one(data) -> bytes:
    """Take 1 Byte"""

    seq = data[:1]
    assert seq, (seq, data)

    return seq  # not empty


#
# Work in parallel with Sh Terminal I/O
#


CUU_N = "\x1B[{}A"  # CSI 04/01 Cursor Up (CUU) of ΔY
CUD_N = "\x1B[{}B"  # CSI 04/02 Cursor Down (CUD) of ΔY
CUF_N = "\x1B[{}C"  # CSI 04/03 Cursor Right (CUF) of ΔX
CUB_N = "\x1B[{}D"  # CSI 04/04 Cursor Left (CUB) of ΔX


class TerminalSprite:
    """Work in parallel with Sh Terminal I/O"""

    steps = 0

    ts: TerminalShadow

    def __init__(self, ts) -> None:
        self.ts = ts

    def step_ahead(self) -> None:
        """Work in parallel with Sh Terminal I/O"""

        self.steps += 1

        fd = sys.stderr.fileno()
        ts = self.ts

        assert CUU_N == "\x1B[{}A"
        assert CUD_N == "\x1B[{}B"
        assert CUF_N == "\x1B[{}C"
        assert CUB_N == "\x1B[{}D"

        # Pick a Y-X-Character we can flip between Inverse Video and Plain

        if ts.rows:
            y = random.randrange(len(ts.rows))
            row = ts.rows[y]
            if row:
                x = random.randrange(len(row))
                ch = row[x]

                # Don't flip the Blank Spaces beyond the Cursor in the Last Row

                if y == len(ts.rows) - 1:
                    if x > ts.x:
                        return

                # Work out how to flip it

                cuu = cud = ""
                if y < ts.y:
                    cuu = "\x1B[{}A".format(ts.y - y)
                    cud = "\x1B[{}B".format(ts.y - y)

                cto = cfrom = ""
                if x != ts.x:
                    if x < ts.x:
                        cto = "\x1B[{}D".format(ts.x - x)
                        cfrom = "\x1B[{}C".format(ts.x - x)
                    else:
                        cto = "\x1B[{}C".format(x - ts.x)
                        cfrom = "\x1B[{}D".format(x - ts.x)

                polarity = ""
                plain = ""
                if random.random() >= 0.5:
                    polarity = "\x1B[7m"  # Inverse Video
                    plain = "\x1B[0m"  # Plain

                bs = "\b"

                writable = cuu + cto + polarity + ch + plain + bs + cfrom + cud

                # Flip it

                data = writable.encode()
                os.write(fd, data)


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/ptybreakout.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
