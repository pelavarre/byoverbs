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
    ~+  - start changing the look of the screen
    ~-  - restore the look of the screen
    (Note that escapes are only recognized immediately after newline.)
"""

# classic Ssh defines ~? to print these Chars of Help, and more


class Main:
    """Open up a shared workspace for the Code of this Py File"""

    terminal_shadow: "TerminalShadow"


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

    sprites: list[TerminalSprite]
    sprites = list()

    holds = bytearray()
    # holds = bytearray(b"lsa\r")  # jitter Sat 3/Feb

    ij = [ord("."), ord("\r")]
    ts = TerminalShadow()

    Main.terminal_shadow = ts

    def fd_patch_output(fd) -> bytes:
        """Take the chance to patch Output, or don't"""

        obytes = os.read(fd, 0x400)
        ts.write_bytes(data=obytes)

        return obytes

    def fd_patch_input(fd) -> bytes:
        """Take the chance to patch Input, or don't"""

        # Pull Bytes till some Bytes found to forward

        while True:
            for sprite in sprites:
                while not sys_stdio_kbhit(sys.stderr.fileno(), timeout=0.100):
                    sprite.step_ahead()

            # Pull Bytes

            if not holds:
                ibytes = os.read(fd, 0x400)
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
                        if not sprites:
                            xprint("~+", end="\r\n")
                            sprite = TerminalSprite(ts, index=len(sprites))
                            sprites.append(sprite)
                        continue

                    # Take the 3 Bytes b"\r~-" to mean remove a Breakout Ball

                    if (i, j, k) == (ord("\r"), ord("~"), ord("-")):
                        if sprites:
                            xprint("~-", end="\r\n")
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

    print(f"{len(sprites)} Sprites walked {list(_.steps for _ in sprites)} Steps")

    # compare 'def read' patching output for https://docs.python.org/3/library/pty.html


#
# Keep up a guess of what the Sh Terminal looks like
#


class TerminalShadow:
    """Keep up a guess of what one Sh Terminal looks like"""

    holds = bytearray()  # partial Packet of Output Bytes

    rows: list[str]  # Rows of Output Text Characters, from 0 to N-1
    rows = list()

    x = 0  # Cursor Column, counted from 0 Leftmost to N-1 Rightmost
    y = 0  # Cursor Row, counted from 0 Topmost to N-1 Bottommost

    pens: list[bytes]  # Chosen Pen   # []  # [b"\x1B[7m"]
    pens = list()

    bitrows: list[list[int]]  # Reverse-Video Bit per Character
    bitrows = list()  # [[1, 0], [0, 1, 0]]

    def write_text(self, text) -> None:
        """Keep up a guess of what one Sh Terminal looks like"""

        lines = text.split("\n")  # todo: "\r" and "\r\n" Line-Break's too
        data = b"\r\n".join(_.encode() for _ in lines)

        self.write_bytes(data)

    def write_bytes(self, data) -> None:  # noqa C901
        """Keep up a guess of what one Sh Terminal looks like"""

        holds = self.holds
        rows = self.rows
        bitrows = self.bitrows

        iprint(f"{data=}  # write_bytes")

        # Split the Output Bytes into Packets

        holds.extend(data)
        while holds:
            held_bytes = bytes(holds)
            seq = bytes_take_startswith_else(held_bytes)
            if not seq:
                break

            holds[::] = holds[len(seq) :]

            yx = (self.y, self.x)
            iprint(f"{yx=} {seq=}")

            # Take C0_CONTROLS as moving the (Y, X) Cursor

            assert "\b" == "\N{Backspace}"
            assert "\r" == "\N{Carriage Return}"
            assert "\n" == "\N{Line Feed}"

            assert "\x1B[m" == Sgr.Plain
            assert "\x1B[7m" == Sgr.ReverseVideo

            if seq[:1] in C0_BYTES:
                if seq == b"\b":
                    self.x = max(0, self.x - 1)
                elif seq == b"\r":
                    self.x = 0
                elif seq == b"\n":
                    self.y += 1

                elif re.match(CsiPattern, string=seq):
                    self.write_csi_seq(seq)

                else:
                    iprint(f"{seq=} skipped  # write_bytes")

                continue

            # Find the Row

            while self.y >= len(rows):
                rows.append("")
                bitrows.append(list())

            # Overlay or grow the Row

            row = rows[self.y]
            bitrow = bitrows[self.y]

            decode = seq.decode()
            for ch in decode:
                while self.x >= len(row):
                    row += " "
                    bitrow += [0]
                assert len(bitrow) == len(row), (len(bitrow), len(row))

                row = row[: self.x] + ch + row[self.x + 1 :]
                if self.pens:
                    bitrow[self.x] = 1
                else:
                    bitrow[self.x] = 0

                self.x += 1

            rows[self.y] = row
            assert bitrows[self.y] is bitrow

    def write_csi_seq(self, seq) -> None:
        """Guess how a CSI Seq changes the look of a Sh Terminal"""

        assert CSI == b"\x1B["

        assert CUU_N == "\x1B[{}A"  # Up
        assert CUD_N == "\x1B[{}B"  # Down
        assert CUF_N == "\x1B[{}C"  # Forward Right
        assert CUB_N == "\x1B[{}D"  # Backwards Left

        head = b"\x1B["  # "Control Sequence Inducer (CSI)"
        body = seq[len(b"\x1B[") : -1]  # "Parameter Bytes"
        tail = seq[-1:]  # "Final Byte"

        assert (head + body + tail) == seq, (head, body, tail, seq)

        if seq == b"\x1B[m":
            self.pens.clear()
            return

        if seq == b"\x1B[7m":
            self.pens.append(seq)
            return

        if tail in b"ABCD":
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

        iprint(f"{seq=} skipped  # write_csi_seq")


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


class Sgr:
    """CSI 06/13 Select Graphic Rendition (SGR)"""

    Plain = "\x1B[m"
    ReverseVideo = "\x1B[7m"  # aka InverseVideo


@dataclasses.dataclass
class TerminalSprite:
    """Work in parallel with Sh Terminal I/O"""

    steps: int

    terminal_shadow: TerminalShadow

    goal: bool  # False to paint Plain, True to paint Reverse-Video

    y: int
    x: int

    dy: int
    dx: int

    def __init__(self, ts, index) -> None:
        """Form Self"""

        self.steps = 0
        self.terminal_shadow = ts
        self.goal = not bool(index % 2)
        self.yx_init()
        self.dydx_init()

        iprint(f"{self=}  # __init__")

    def step_ahead(self) -> None:
        """Work in parallel with Sh Terminal I/O"""

        self.steps += 1

        ts = self.terminal_shadow
        assert ts.rows, (ts.rows,)

        yx_0 = (self.y, self.x)
        yx_1 = self.yx_glide()
        yx_2 = self.yx_fit()

        iprint(f"{yx_0=} {yx_1=} {yx_2=}  # step_ahead")

        if yx_2 != yx_1:  # bouncing because hit a wall
            self.dydx_bounce()
        elif self.y_x_flying(*yx_1):  # coasting over no Text
            self.y_x_visit(*yx_1, bit=not self.goal)
            if not self.y_x_flying(*yx_0):
                self.y_x_bitput(*yx_0, bit=self.goal)
        else:  # moving over Text
            coasting = self.y_x_bitget(*yx_1) == self.goal
            self.y_x_bitput(*yx_1, bit=not self.goal)
            if not self.y_x_flying(*yx_0):
                self.y_x_bitput(*yx_0, bit=self.goal)
            if not coasting:  # bouncing because took a spot
                self.dydx_bounce()

    def yx_init(self) -> tuple[int, int]:
        """Land somewhere on the Text"""

        ts = self.terminal_shadow

        if ts.rows:
            y = random.randrange(len(ts.rows))
            row = ts.rows[y]
            if row:
                x = random.randrange(len(row))

        if True:  # jitter Sat 3/Feb
            y = 3
            y = len(ts.rows) - 1
            x = 0

        return self.y_x_warp(y, x)

    def y_x_warp(self, y, x) -> tuple[int, int]:
        """Go to a place on the Text, or outside"""

        self.y = y
        self.x = x

        yx = (y, x)

        return yx

    def dydx_init(self) -> tuple[int, int]:
        """Pick a Direction and Speed"""

        dy = dx = 0
        while (not dy) and (not dx):  # todo: interminable
            dy = random.choice([-1, 0, 1])
            dx = random.choice([-1, 0, 1])

        if True:  # jitter Sat 3/Feb
            dy = -1
            dx = 0

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

        dy = -self.dy
        dx = -self.dx

        if random.random() >= 0.5:
            if random.random() >= 0.5:
                dy = random.choice([-1, 0, 1])
            else:
                dx = random.choice([-1, 0, 1])

            while (not dy) and (not dx):  # todo: interminable
                dy = random.choice([-1, 0, 1])
                dx = random.choice([-1, 0, 1])

        if True:  # jitter Sat 3/Feb
            dy = -self.dy
            dx = -self.dx

        self.dy = dy
        self.dx = dx

        dydx = (dy, dx)

        return dydx

    def yx_fit(self) -> tuple[int, int]:
        """Come back in to land on the Text, or over the first Column beyond it"""

        ts = self.terminal_shadow
        assert ts.rows, (ts.rows,)

        y = self.y
        x = self.x

        if y < 0:
            y = 0
        elif y >= len(ts.rows):
            y = len(ts.rows) - 1

        row = ts.rows[y]
        last_x = len(row)

        if x < 0:
            x = 0
        elif x > last_x:
            x = last_x - 1

        self.y = y
        self.x = x

        yx = (y, x)

        return yx

    def y_x_flying(self, y, x) -> bool:
        """Say if flying over the first Column beyond the Text"""

        ts = self.terminal_shadow

        row = ts.rows[y]
        last_x = len(row)

        flying = x >= last_x

        return flying

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

        assert Sgr.Plain == "\x1B[m"
        assert Sgr.ReverseVideo == "\x1B[7m"

        polarity = ""
        plain = ""
        if bit:
            polarity = "\x1B[7m"  # Reverse-Video
            plain = "\x1B[m"  # Plain

        bs = "\b"

        # Work out where to flip it

        assert CUU_N == "\x1B[{}A"
        assert CUD_N == "\x1B[{}B"
        assert CUF_N == "\x1B[{}C"
        assert CUB_N == "\x1B[{}D"

        yto = yfrom = ""
        if y != ts.y:
            cuu = "\x1B[{}A".format(ts.y - y)
            cud = "\x1B[{}B".format(ts.y - y)
            (yto, yfrom) = (cuu, cud) if (y < ts.y) else (cud, cuu)

        xto = xfrom = ""
        if x != ts.x:
            cub = "\x1B[{}D".format(ts.x - x)
            cuf = "\x1B[{}C".format(ts.x - x)
            (xto, xfrom) = (cub, cuf) if (y < ts.y) else (cuf, cub)

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


TextIO = open(os.devnull, "w")
TextIO = open("o.out", "w")  # jitter Sun 28/Jan


def xprint(*args, **kwargs) -> None:
    """Print to Stdout, but also to TerminalShadow"""

    ts = Main.terminal_shadow

    sep = kwargs.get("sep", " ")
    printing = sep.join(str(_) for _ in args)

    print(printing, **kwargs)
    ts.write_text(printing + "\n")


def iprint(*args, **kwargs) -> None:
    """Print to Log File, not to Stdout"""

    text_io = TextIO

    # Compress =b'...' notation

    sep = kwargs.get("sep", " ")
    printing = sep.join(str(_) for _ in args)

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
                    print(alt, **kwargs, file=text_io)
                    text_io.flush()

                    return

    # Else print like normal, but to our TextIO Log File, and flush

    print(printing, **kwargs, file=text_io)
    text_io.flush()


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# feature: b"\x09" Hard Tabs incorrectly occupy 1 Column, not 1..8 Columns?
# feature: should take ASDF and HJKL impulses
# feature: should take --input=FILE option

# bug: often trips up in leftmost column
# bug: sometimes warps from one angled line to another
# bug: sometimes lays characters back down several columns to the right of where taken
# bug: sometimes moves the Terminal Cursor to the right
# bug: sometimes crashes after moving the Terminal Cursor to the right off Screen

# bug: Sprites stop stepping at first Input after added? Till next Return ~
# bug: Prints from 'def fd_patch_input' bypass the TerminalShadow?

# bug: Py 'pty.spawn' wrongly flushes Input Paste, in TcsAFlush style, not TcsADrain


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/ptybreakout.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
