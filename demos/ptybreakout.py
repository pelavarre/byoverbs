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
import dataclasses
import datetime as dt
import os
import pty
import random
import re
import select
import shlex
import sys
import textwrap
import typing


... == dict[str, int]  # new Syntax since Oct/2020 Python 3.9
# ... == bytes | None  # new Syntax since Oct/2021 Python 3.10


default_sh = "sh"
ENV_SHELL = os.getenv("SHELL", default_sh)


PATCH_DOC = """
    Supported escape sequences:
    ~?  - this message
    ~~  - send the escape character by typing it twice
    ~+  - start changing the look of the screen
    ~-  - restore the look of the screen
    (Note that escapes are only recognized immediately after newline.)
"""

# classic Ssh defines ~? to print these Chars of Help, and more


class Main:
    """Open up a shared workspace for the Code of this Py File"""

    terminal_shadow: "TerminalShadow"
    tprint_when: dt.datetime

    tprint_when = dt.datetime.now()


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
    # shline = "/bin/bash"  # jitter Sat 3/Feb
    argv = shlex.split(shline)

    pty_spawn_argv(argv)


def pty_spawn_argv(argv) -> None:  # noqa C901
    """Wrap the I/O of a Sh Terminal"""

    patch_doc = textwrap.dedent(PATCH_DOC).strip()

    sprites: list[TerminalSprite]
    sprites = list()

    holds = bytearray()
    # holds = bytearray(b"lsa\r")  # jitter Sat 3/Feb

    ij = [ord("."), ord("\r")]
    ts = TerminalShadow()

    Main.terminal_shadow = ts

    def fd_patch_output(fd) -> bytes:
        """Take the chance to patch Output, or don't"""

        iprint("blocking  # fd_patch_output os.read fd")
        obytes = os.read(fd, 0x400)
        iprint("unblocking  # fd_patch_output os.read fd")

        ts.write_bytes(data=obytes)

        return obytes

        # todo: give Cpu to Sprites while 'def fd_patch_input' is blocked

    def fd_patch_input(fd) -> bytes:
        """Take the chance to patch Input, or don't"""

        # Run Sprites while waiting for Input

        spritely = False
        while True:
            while not sys_stdio_kbhit(fd, timeout=0.100):
                for i, sprite in enumerate(sprites):
                    spritely = True
                    sprite.step_ahead()

                    ssk = sys_stdio_kbhit(fd, timeout=0.100)
                    iprint(f"{i=} {ssk=}")

            # Pull Bytes

            if not holds:
                iprint("blocking  # fd_patch_input os.read fd")
                ibytes = os.read(fd, 0x400)
                iprint("unblocking  # fd_patch_input os.read fd")
            else:
                ibytes = bytes(holds)
                holds.clear()

            # Judge 3 Bytes at a time

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
                        xprint("~?", end="\r\n")
                        xprint("\r\n".join(patch_doc.splitlines()), end="\r\n")
                        continue

                    # Take the 3 Bytes b"\r~+" to mean add a Breakout Ball

                    if (i, j, k) == (ord("\r"), ord("~"), ord("+")):
                        xprint("~+", end="")
                        if not sprites:
                            sprite_a = TerminalSprite(ts, index=len(sprites))
                            xprint(end="\r\n")
                            sprites.append(sprite_a)

                            sprite_b = TerminalSprite(ts, index=len(sprites))
                            sprites.append(sprite_b)

                        continue

                    # Take the 3 Bytes b"\r~-" to mean remove a Breakout Ball

                    if (i, j, k) == (ord("\r"), ord("~"), ord("-")):
                        xprint("~-", end="\r\n")
                        if sprites:
                            sprite = sprites.clear()
                        ts.rows_restore()

                        continue

                    # Else forward the b"~" of b"\r~" with the next Byte

                    pbytes.append(j)
                    pbytes.append(k)
                    continue

                # Else forward the Byte immediately

                pbytes.append(k)

            # Take a lil more Cpu, when forwarding Bytes might deny us Cpu

            if pbytes:
                if not spritely:
                    for sprite in sprites:
                        sprite.step_ahead()

                # Return Bytes to forward them

                return pbytes

    fd = sys.stderr.fileno()
    size = os.get_terminal_size(fd)
    if not False:  # evades Terminal Size Discovery Bug in 'pty.spawn'
        os.putenv("LINES", str(size.lines))
        os.putenv("COLUMNS", str(size.columns))

    assert ts.end == "\r\n", (repr(ts.end),)
    pty.spawn(argv, master_read=fd_patch_output, stdin_read=fd_patch_input)
    ts.end = "\n"

    if sprites:
        ts.rows_restore()
        print(f"{len(sprites)} Sprites walked {list(_.steps for _ in sprites)} Steps")

    # compare 'def read' patching output for https://docs.python.org/3/library/pty.html


#
# Keep up a guess of what the Sh Terminal looks like
#


class TerminalShadow:
    """Keep up a guess of what one Sh Terminal looks like"""

    holds = bytearray()  # partial Packet of Output Bytes

    end = "\r\n"  # Encoding of Line-Break

    rows: list[str]  # Rows of Output Text Characters, from 0 to N-1
    rows = list()

    x = 0  # Cursor Column, counted from 0 Leftmost to N-1 Rightmost
    y = 0  # Cursor Row, counted from 0 Topmost to N-1 Bottommost

    inks: list[bytes]  # Chosen Inks   # []  # [b"\x1B[7m"]
    inks = list()

    bitrows: list[list[int]]  # Reverse-Video Bit per Character
    bitrows = list()  # [[1, 0], [0, 1, 0]]

    def rows_restore(self) -> None:
        """Rewrite the Rows of Text"""

        assert CUU_N == "\x1B[{}A"  # Up
        assert EL == "\x1B[K"  # Erase in Line (EL)  # 04/11

        rows = list(self.rows)
        # bitrows = list(self.bitrows)
        y = self.y

        if y:
            cuu = "\x1B[{}A".format(y)
            xprint(cuu, end="")

        xprint("\r", end="")

        el = "\x1B[K"
        for i, row in enumerate(rows):
            xprint(el + row, end=self.end)

    def write_text(self, text) -> None:
        """Keep up a guess of what one Sh Terminal looks like"""

        lines = text.split("\n")  # todo: "\r" and "\r\n" Line-Break's too
        data = b"\r\n".join(_.encode() for _ in lines)

        self.write_bytes(data)

    def write_bytes(self, data) -> None:  # noqa C901
        """Keep up a guess of what one Sh Terminal looks like"""

        fd = sys.stderr.fileno()

        holds = self.holds
        rows = self.rows
        bitrows = self.bitrows

        # Split the Output Bytes into Packets

        holds.extend(data)
        while holds:
            held_bytes = bytes(holds)
            seq = bytes_take_startswith_else(held_bytes)
            if not seq:
                break

            holds[::] = holds[len(seq) :]

            yx = (self.y, self.x)

            # Take C0_CONTROLS as moving the (Y, X) Cursor

            assert "\b" == "\N{Backspace}"
            assert "\r" == "\N{Carriage Return}"
            assert "\n" == "\N{Line Feed}"

            assert "\x1B[m" == Sgr.Plain  # 06/13
            assert "\x1B[7m" == Sgr.ReverseVideo  # 06/13

            if seq[:1] in C0_BYTES:
                if seq == b"\b":
                    iprint(f"{yx=} {seq=}")
                    self.x = max(0, self.x - 1)
                elif seq == b"\r":
                    iprint(f"{yx=} {seq=}")
                    self.x = 0
                elif seq == b"\n":
                    iprint(f"{yx=} {seq=}")
                    self.y += 1

                elif re.match(CsiPattern, string=seq):
                    self.write_csi_seq(seq)

                else:
                    iprint(f"skipping {yx=} {seq=}  # write_bytes")

                continue

            # Find the Row, and overlay or grow the Row, and maybe fall off the End

            iprint(f"{yx=} {seq=}")

            while self.y >= len(rows):
                rows.append("")
                bitrows.append(list())

            row = rows[self.y]
            bitrow = bitrows[self.y]

            decode = seq.decode()
            for ch in decode:
                size = os.get_terminal_size(fd)

                if self.x >= size.columns:
                    assert self.x == size.columns, (self.x, size.columns)

                    rows[self.y] = row
                    assert bitrows[self.y] is bitrow

                    self.y += 1
                    self.x = 0

                    while self.y >= len(rows):
                        rows.append("")
                        bitrows.append(list())

                    row = rows[self.y]
                    bitrow = bitrows[self.y]

                while self.x >= len(row):
                    row += " "  # todo: fill with Flyover Blanks, not Spaces
                    bitrow += [0]
                assert len(bitrow) == len(row), (len(bitrow), len(row))

                row = row[: self.x] + ch + row[self.x + 1 :]
                if self.inks:
                    iprint(f"{self.y=} {self.x=} bit 1")
                    bitrow[self.x] = 1
                else:
                    bitrow[self.x] = 0

                self.x += 1

            rows[self.y] = row
            assert bitrows[self.y] is bitrow

    def write_csi_seq(self, seq) -> None:  # noqa C901
        """Guess how a CSI Seq changes the look of a Sh Terminal"""

        y = self.y
        x = self.x
        yx = (y, x)

        assert CSI == b"\x1B["

        head = b"\x1B["  # "Control Sequence Inducer (CSI)"
        body = seq[len(b"\x1B[") : -1]  # "Parameter Bytes"
        tail = seq[-1:]  # "Final Byte"

        assert (head + body + tail) == seq, (head, body, tail, seq)

        # Choose Reverse-Video or Plain

        assert "\x1B[m" == Sgr.Plain  # 06/13
        assert "\x1B[7m" == Sgr.ReverseVideo  # 06/13

        if seq == b"\x1B[m":  # 06/13
            iprint(f"{yx=} {seq=}")
            self.inks.clear()
            return

        if seq == b"\x1B[0m":  # 06/13
            iprint(f"{yx=} {seq=}")
            self.inks.clear()
            return

        if seq == b"\x1B[7m":  # 06/13
            iprint(f"{yx=} {seq=}")
            self.inks.append(seq)
            return

        # Move the Terminal Cursor by Relative Y and X Distances

        assert CUU_N == "\x1B[{}A"  # Up
        assert CUD_N == "\x1B[{}B"  # Down
        assert CUF_N == "\x1B[{}C"  # Forwards Right
        assert CUB_N == "\x1B[{}D"  # Backwards Left

        if tail in b"ABCD":
            iprint(f"{yx=} {seq=}")

            assert re.match(b"^[0-9]*$", string=body), (body,)
            body_int = int(body) if body else 1

            if tail == b"A":
                self.y -= body_int  # Up
            elif tail == b"B":
                self.y += body_int  # Down
            elif tail == b"C":
                self.x += body_int  # Right
            elif tail == b"D":
                self.x -= body_int  # Left

            return

        # Truncate the Row, or the Rows, on Demand

        assert ED == "\x1B[J"  # Erase in Display  # 04/12
        assert EL == "\x1B[K"  # Erase in Line (EL)  # 04/11

        if tail == b"J":
            if not body:
                iprint(f"{yx=} {seq=}")

                self.y_x_end_one_row(self.y, x=self.x)
                self.y_end_the_rows(self.y + 1)
                return

            # todo: "\x1B[{}J", especially "\x1B[0J"

        if tail == b"K":
            if not body:
                iprint(f"{yx=} {seq=}")

                self.y_x_end_one_row(self.y, x=self.x)
                return

            # todo: "\x1B[{}K", especially "\x1B[0K"

        # Log the Instructions we shrug off

        iprint(f"skipping {yx=} {seq=}  # write_csi_seq")

    def y_x_end_one_row(self, y, x) -> None:
        """Truncate one Row on Demand"""

        rows = self.rows
        bitrows = self.bitrows
        assert len(rows) == len(bitrows), (len(rows), len(bitrows))

        if y < len(rows):
            rows[y] = rows[y][:x]
            bitrows[y] = bitrows[y][:x]

    def y_end_the_rows(self, y) -> None:
        """Truncate Rows on Demand"""

        rows = self.rows
        bitrows = self.bitrows

        rows[::] = rows[:y]
        bitrows[::] = bitrows[:y]


def sys_stdio_kbhit(stdio, timeout) -> list[int]:  # 'timeout' in seconds
    """Wait till next Input Byte, else till Timeout, else till forever"""

    rlist: list[int] = [stdio]
    wlist: list[int] = list()
    xlist: list[int] = list()

    (alt_rlist, _, _) = select.select(rlist, wlist, xlist, timeout)

    return alt_rlist

    # works and returns [stdio] even when 'stdio is sys.stderr', not its .fileno()


#
# Name some of the C0 Control Bytes
#


NUL = b"\0"  # 00/00 "\N{Nul}"
BEL = b"\a"  # 00/07 "\N{Bel}"  # not "\N{Bell}""
BS = b"\b"  # 00/08 "\N{Backspace}"
CR = b"\r"  # 00/13 "\N{Carriage Return}"
CRLF = b"\r\n"  # 00/13 00/10 "\N{Carriage Return}" "\N{Line Feed}"
LF = b"\n"  # 00/10 "\N{Line Feed}"


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


def _bytes_take_mouse_six_else(data) -> typing.Union[bytes, None]:  # bytes | None:
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


def _bytes_take_c0_plus_else(data) -> typing.Union[bytes, None]:  # bytes | None:
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


def _bytes_take_much_utf8_else(data) -> typing.Union[bytes, None]:  # bytes | None:
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

ED = "\x1B[J"  # CSI 04/12 Erase in Display (ED)
EL = "\x1B[K"  # CSI 04/11 Erase in Line (EL)


class Sgr:
    """CSI 06/13 Select Graphic Rendition (SGR)"""

    Plain = "\x1B[m"
    ReverseVideo = "\x1B[7m"  # aka InverseVideo


@dataclasses.dataclass
class TerminalSprite:
    """Work in parallel with Sh Terminal I/O"""

    steps: int

    terminal_shadow: TerminalShadow

    goal: int  # 0 to paint Plain, 1 to paint Reverse-Video

    y: int
    x: int

    dy: int
    dx: int

    def __init__(self, ts, index) -> None:
        """Form Self"""

        self.steps = 0
        self.terminal_shadow = ts
        self.goal = 0 if (index % 2) else 1
        self.yx_init()
        self.dydx_init()

        iprint(f"{self=}  # __init__")

    def step_ahead(self) -> None:
        """Work in parallel with Sh Terminal I/O"""

        self.steps += 1

        ts = self.terminal_shadow
        assert ts.rows, (ts.rows,)

        dydx = (self.dy, self.dx)

        yx_0 = (self.y, self.x)
        yx_1 = self.yx_glide()
        yx_2 = self.yx_fit()

        if yx_2 != yx_1:
            if self.y_x_flying_else(*yx_1) is None:  # if not flying beyond Text
                iprint(f"{yx_0=} {yx_1=} {yx_2=} {dydx=}  # bouncing off a Wall")
                self.dydx_bounce()  # bouncing off a Wall
            else:
                iprint(f"{yx_0=} {yx_1=} {yx_2=} {dydx=}  # flying beyond Text")

        elif self.y_x_flying_else(*yx_1):  # coasting over no Text
            assert yx_2 != yx_0, (yx_2, yx_0)
            self.y_x_visit(*yx_1, bit=not self.goal)
            if not self.y_x_flying_else(*yx_0):
                iprint(f"{yx_0=} {yx_1=} {yx_2=} {dydx=}  # coasting after on Text")
                self.y_x_bitput(*yx_0, bit=self.goal)
            else:
                iprint(f"{yx_0=} {yx_1=} {yx_2=} {dydx=}  # coasting after flying")

        else:  # moving over Text
            assert yx_2 != yx_0, (yx_2, yx_0)

            got = self.y_x_bitget(*yx_2)
            coasting = got == self.goal
            self.y_x_bitput(*yx_2, bit=not self.goal)

            if not self.y_x_flying_else(*yx_0):
                iprint(f"{yx_0=} {yx_1=} {yx_2=} {dydx=}  # moving after on Text")
                self.y_x_bitput(*yx_0, bit=self.goal)
            else:
                iprint(f"{yx_0=} {yx_1=} {yx_2=} {dydx=}  # moving after flying")

            if not coasting:  # bouncing because took a spot
                iprint(f"{got=} {self.goal=} {coasting=}  # bouncing after take")
                self.dydx_bounce()
            else:
                iprint(f"{got=} {self.goal=} {coasting=}  # not bouncing, no take")

    def yx_init(self) -> tuple[int, int]:
        """Land somewhere on the Text"""

        ts = self.terminal_shadow
        rows = ts.rows

        assert rows
        y = len(rows) - 1
        row = rows[y]

        x = len(row)

        self.y_x_warp(y, x)
        yx_2 = self.yx_fit()

        return yx_2

    def y_x_warp(self, y, x) -> tuple[int, int]:
        """Go to a place on the Text, or outside"""

        self.y = y
        self.x = x

        yx = (y, x)

        return yx

    def dydx_init(self) -> tuple[int, int]:
        """Pick a Direction and Speed"""

        while True:
            dy = random.choice([-1, 0, 1])
            dx = random.choice([-1, 0, 1])

            if (dy, dx) == (0, 0):
                continue

            break

        self.dy = dy
        self.dx = dx

        dydx = (dy, dx)

        return dydx

    def yx_glide(self) -> tuple[int, int]:
        """Move the Ball"""

        y = self.y + self.dy
        x = self.x + self.dx

        return self.y_x_warp(y, x)

    def dydx_bounce(self) -> tuple[int, int]:
        """Reverse and tweak the Glide Vector"""

        while True:
            dy = random.choice([-1, 0, 1])
            dx = random.choice([-1, 0, 1])

            if (dy, dx) == (0, 0):
                continue
            if (dy, dx) == (-self.dy, -self.dx):
                continue

            break

        self.dy = dy
        self.dx = dx

        dydx = (dy, dx)

        return dydx

    def yx_fit(self) -> tuple[int, int]:
        """Come back in to land on the Text, or over the first Column beyond it"""

        ts = self.terminal_shadow

        y = self.y
        x = self.x

        assert ts.rows, (ts.rows,)
        if y < 0:
            y = 0
        elif y >= len(ts.rows):
            y = len(ts.rows) - 1

        row = ts.rows[y]
        last_x = len(row)

        if x < 0:
            x = 0
        elif x > last_x:
            x = last_x

        self.y = y
        self.x = x

        yx = (y, x)

        return yx

    def y_x_flying_else(self, y, x) -> typing.Union[bool, None]:  # bool | None:
        """Say if flying over the Columns beyond the Text"""

        ts = self.terminal_shadow

        if 0 <= y < len(ts.rows):
            row = ts.rows[y]
            last_x = len(row)

            if 0 <= x < last_x:
                return False

            if x == last_x:
                return True

        return None

    def y_x_bitget(self, y, x) -> int:
        """Get the Bit at (Y, X)"""

        ts = self.terminal_shadow
        bitrows = ts.bitrows
        assert 0 <= y < len(bitrows), (y, len(bitrows))
        bitrow = bitrows[y]
        assert 0 <= x < len(bitrow), (x, len(bitrow))
        bit = bitrow[x]

        return bit

    def y_x_bitput(self, y, x, bit) -> None:
        """Put the Bit at (Y, X)"""

        ts = self.terminal_shadow

        row = ts.rows[y]
        ch = row[x]

        self.y_x_bitput_ch(y, x=x, ch_if=ch, bit=bit)

    def y_x_bitput_ch(self, y, x, ch_if, bit) -> None:
        """Put the Bit on the Ch at (Y, X)"""

        fd = sys.stderr.fileno()
        ts = self.terminal_shadow

        # Work out how to flip it

        assert Sgr.Plain == "\x1B[m"  # 06/13
        assert Sgr.ReverseVideo == "\x1B[7m"  # 06/13

        polarity = ""
        plain = ""
        if bit:
            polarity = "\x1B[7m"  # Reverse-Video
            plain = "\x1B[m"  # Plain

        bs = "\b"

        # Work out where to flip it

        assert CUU_N == "\x1B[{}A"  # Up
        assert CUD_N == "\x1B[{}B"  # Down
        assert CUF_N == "\x1B[{}C"  # Forwards Right
        assert CUB_N == "\x1B[{}D"  # Backwards Left

        yto = yfrom = ""
        if y < ts.y:
            yto = "\x1B[{}A".format(ts.y - y)
            yfrom = "\x1B[{}B".format(ts.y - y)
        elif ts.y < y:
            yto = "\x1B[{}B".format(y - ts.y)
            yfrom = "\x1B[{}A".format(y - ts.y)

        xto = xfrom = ""
        if x < ts.x:
            xto = "\x1B[{}D".format(ts.x - x)
            xfrom = "\x1B[{}C".format(ts.x - x)
        elif ts.x < x:
            xto = "\x1B[{}C".format(x - ts.x)
            xfrom = "\x1B[{}D".format(x - ts.x)

        # Flip it

        writable = yto + xto + polarity
        if ch_if:
            writable += ch_if + bs
        writable += yfrom + xfrom + plain

        data = writable.encode()
        ts.write_bytes(data)
        os.write(fd, data)

    def y_x_visit(self, y, x, bit) -> None:
        """Move the Cursor to (Y, X) and back, as if putting a Bit there"""

        self.y_x_bitput_ch(y, x=x, ch_if="", bit=bit)


#
# Define variations on Print
#


# Choose a Log File

TextIO = open(os.devnull, "w")
TextIO = open("o.out", "w")  # jitter Sat 3/Feb


def xprint(*args, **kwargs) -> None:
    """Print to Stdout, but also to TerminalShadow"""

    ts = Main.terminal_shadow

    sep = kwargs.get("sep", " ")
    printing = sep.join(str(_) for _ in args)

    print(printing, **kwargs)

    end = kwargs.get("end", "\n")
    ts.write_text(printing + end)


def iprint(*args, **kwargs) -> None:
    """Print with Stamp to Log File not Stdout, but first compress if compressible"""

    sep = kwargs.get("sep", " ")
    printing = sep.join(str(_) for _ in args)

    # Compress =b'...' notation

    find = printing.find("=b'")
    rfind = printing.rfind("'")
    if (find >= 0) and (rfind >= 0):
        start = find + len("=b'")
        stop = rfind

        reps = printing[start:stop]
        if reps:
            ch = reps[-1]
            n = len(reps)

            if reps and (reps == (n * ch)):
                alt = printing[:find] + f"={n} * b'" + ch + printing[rfind:]
                if len(alt) < (len(printing) - 5):
                    tprint(alt, **kwargs)

                    return

    # Else print like normal, but to our TextIO Log File, and flush

    tprint(printing, **kwargs)


def tprint(*args, **kwargs) -> None:
    """Add elapsed Milliseconds Stamp, and print to Log File not Stdout"""

    text_io = TextIO

    sep = kwargs.get("sep", " ")
    printing = sep.join(str(_) for _ in args)

    # Count milliseconds between Print's

    now = dt.datetime.now()
    ms_int = int((now - Main.tprint_when).total_seconds() * 1000)
    ms = f"{ms_int}ms"

    Main.tprint_when = now

    # Add loud elapsed Milliseconds Stamp only if nonzero

    if ms == "0ms":
        print(printing, **kwargs, file=text_io)
    else:
        print("\n" + ms + "\n" + printing, **kwargs, file=text_io)

    text_io.flush()


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# feature: b"\x09" Hard Tabs incorrectly occupy 1 Column, not 1..8 Columns?
# feature: should take ASDF and HJKL impulses
# feature: should take --input=FILE option


# bug: 'noqa C901' marks on 4 Def's

# bug: Balls don't fly over the Columns beyond the Text

# bug: exiting Sprites doesn't restore Reverse/Plain Video
# bug: exiting Sprites doesn't restore Sgr Colors

# bug: 'pty.spawn' calls for patches only when unpatched I/O available
# bug: 'pty.spawn' wrongly flushes Input Paste, in TcsAFlush style, not TcsADrain
# bug: our 'def fd_patch_output' gives no Cpu to Sprites while 'fd_patch_input' blocked


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/ptybreakout.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
