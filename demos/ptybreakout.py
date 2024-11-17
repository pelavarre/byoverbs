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


#
# Configure Staging
#

FIXME = False
# FIXME = True  # jitter Sun 4/Feb


# Choose a Log File

TextIOElse: typing.Union[typing.TextIO, None]

TextIOElse = None  # for 'vvprint', 'vprint'
if FIXME:
    TextIOElse = open("o.out", "w")  # jitter Sat 3/Feb


#
# Configure Production
#

default_sh = "sh"
ENV_SHELL = os.getenv("SHELL", default_sh)


# classic Ssh defines the \r ~ ? to print Help Lines

PATCH_DOC = """
    Return ~ ?  show this help message
    Return ~ ~  send the escape character by typing it twice
    Return ~ +  start changing the look of the screen
      ⇧Z⇧Q       quit & restore screen
      ⇧Z⇧Z       quit but don't restore screen
      H J K L    poke the Plain-Video Ball with ← ↓ ↑ →
      A S D F    poke the Reverse-Video Ball with ← ↓ ↑ →
      other key  ring the Terminal Bell
"""

# Space  pause/ resume the Balls

# 0123456789  pile up digits
# G g  move 1 Ball to the Last Gameboard Row, or to a chosen Row
# | \  move 1 Ball to the First Gameboard Column, or to a chosen Column

# also quits when given Vi :q!\r :wq\r, Emacs ⌃X⌃C ⌃X⌃S, or Ssh \r~-


class Main:
    """Open up a shared workspace for the Code of this Py File"""

    terminal_shadow: "TerminalShadow"

    digits = bytearray()

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

    fd = sys.stderr.fileno()
    size = os.get_terminal_size(fd)
    if size == (0, 0):
        print(f"{size=}", file=sys.stderr)
        sys.exit(1)

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

    abc = list(b"..\r")

    ts_fd = sys.stderr.fileno()
    ts = TerminalShadow(ts_fd)

    Main.terminal_shadow = ts

    def fd_patch_output(fd) -> bytes:
        """Take the chance to patch Output, or don't"""

        if TextIOElse:
            TextIOElse.flush()

        vvprint("blocking  # fd_patch_output os.read fd")
        obytes = os.read(fd, 0x400)
        vvprint("unblocking  # fd_patch_output os.read fd")

        ts.write_bytes(data=obytes)

        return obytes

        # todo: give Cpu to Sprites while 'def fd_patch_input' is blocked

    def fd_patch_input(fd) -> bytes:
        """Take the chance to patch Input, or don't"""

        digits = Main.digits

        # Run Sprites while waiting for Input

        spritely = False
        while True:
            while not sys_stdio_kbhit(ts.fd, timeout=0.100):
                for i, sprite in enumerate(sprites):
                    spritely = True
                    sprite.step_ahead()

            # Pull Bytes

            if TextIOElse:
                TextIOElse.flush()

            if not holds:
                vvprint("blocking  # fd_patch_input os.read fd")
                ibytes = os.read(fd, 0x400)
                vvprint("unblocking  # fd_patch_input os.read fd")
            else:
                ibytes = bytes(holds)
                holds.clear()

            # Look back over 4 Input Bytes

            pbytes = bytearray()
            for d in ibytes:
                (a, b, c) = abc
                abc[::] = [b, c, d]

                abcd = bytes([a, b, c, d])

                # Play the Game

                if sprites:
                    verb = sprites_take_abcd(sprites, abcd=abcd)
                    if verb == "save_n_quit":
                        digits.clear()
                        ts.rows_commit()
                        sprites.clear()
                    elif verb == "quit_wout_save":
                        digits.clear()
                        ts.rows_rollback()
                        sprites.clear()
                    else:
                        assert not verb, (verb, abcd)

                    continue

                # Take the 2 Bytes b"\r~" to mean hold the b"~" till next Byte

                if abcd.endswith(b"\r~"):
                    continue

                # Take the 3 Bytes b"\r~~" to mean forward the 2 Bytes b"\r~"

                if (b, c) == (ord("\r"), ord("~")):
                    if abcd.endswith(b"\r~~"):
                        pbytes.append(d)
                        continue

                    # Take the 3 Bytes b"\r~?" to mean explain thyself

                    if abcd.endswith(b"\r~?"):
                        xprint("~?", end="\r\n")
                        xprint("\r\n".join(patch_doc.splitlines()), end="\r\n")
                        continue

                    # Take the 3 Bytes b"\r~+" to mean add a Breakout Ball

                    if abcd.endswith(b"\r~+"):
                        xprint("~+", end="")
                        if not sprites:
                            ts.rows_checkpoint()

                            sprite_a = TerminalSprite(ts, index=len(sprites))
                            xprint(end="\r\n")
                            sprites.append(sprite_a)

                            sprite_b = TerminalSprite(ts, index=len(sprites))
                            sprites.append(sprite_b)

                        continue

                    # Else forward the b"~" of b"\r~" with the next Byte

                    pbytes.append(c)
                    pbytes.append(d)
                    continue

                # Else forward the Byte immediately

                pbytes.append(d)

            # Take a lil more Cpu, when forwarding Bytes might deny us Cpu

            if pbytes:
                if not spritely:
                    for sprite in sprites:
                        sprite.step_ahead()

                # Return Bytes to forward them

                return pbytes

    size = os.get_terminal_size(ts.fd)
    if not False:  # evades Terminal Size Discovery Bug in 'pty.spawn'
        os.putenv("LINES", str(size.lines))
        os.putenv("COLUMNS", str(size.columns))

    assert ts.end == "\r\n", (repr(ts.end),)
    pty.spawn(argv, master_read=fd_patch_output, stdin_read=fd_patch_input)
    ts.end = "\n"

    if sprites:
        ts.rows_rollback()
        print(f"{len(sprites)} Sprites walked {list(_.steps for _ in sprites)} Steps")
        sprites.clear()  # unneeded

    # compare 'def read' patching output for https://docs.python.org/3/library/pty.html


def sprites_take_abcd(sprites, abcd) -> str:  # noqa C901
    r"""React to last 4 Bytes of Input, after our abc = "..\r" start"""

    ts = Main.terminal_shadow
    digits = Main.digits

    dbyte = abcd[-1:]

    vprint(f"{abcd=}  # fd_patch_input while Sprites")

    # Pile up Decimal Digits

    if (dbyte in b"123456789") or (digits and (dbyte == b"0")):
        digits.extend(dbyte)
        return ""

    size = os.get_terminal_size(ts.fd)

    digits_int = 1
    if digits:
        digits_int = int(digits)  # todo: test many Digits
        assert digits_int >= 1, (digits_int, digits)

    if dbyte in b"gG":
        assert ts.cloned_rows, (ts.cloned_rows,)
        if not digits:
            digits_int = len(ts.cloned_rows)
        index = dbyte == b"G"
        sprite = sprites[index]
        sprite.y = digits_int - 1
        assert 0 <= sprite.y < len(ts.cloned_rows), (sprite.y, len(ts.cloned_rows))
        return ""

    if dbyte in rb"\|":
        index = dbyte == b"|"
        sprite = sprites[index]
        if digits_int >= size.columns:
            digits_int = size.columns
        sprite.x = digits_int - 1
        assert 0 <= sprite.x < size.columns, (sprite.x, size.columns)
        return ""

    digits.clear()

    # Save and Quit, or Quit without Saving, or wait for more Input Bytes

    assert (ord("C") ^ 0x40) == 0x03
    assert (ord("S") ^ 0x40) == 0x13
    assert (ord("X") ^ 0x40) == 0x18

    save_n_quits = (b":wq\r", b"ZZ", b"\x18\x13")
    quits_wout_save = (b":q!\r", b"ZQ", b"\x18\x03", b"\r~-")

    if any(abcd.endswith(_) for _ in save_n_quits):  # :wq\r ⇧Z⇧Z ⌃X⌃S
        return "save_n_quit"

    if any(abcd.endswith(_) for _ in quits_wout_save):  # :q!\r ⇧Z⇧Q ⌃X⌃C
        return "quit_wout_save"

    if any((dbyte in _) for _ in (save_n_quits + quits_wout_save)):
        return ""

    # Poke one Sprite to step Left/ Down/ Up/ Right

    dy_by_byte = dict(zip(b"asdf" b"hjkl", 2 * (0, +1, -1, 0)))
    dx_by_byte = dict(zip(b"asdf" b"hjkl", 2 * (-1, 0, 0, +1)))
    if dbyte in b"asdf" b"hjkl":
        (dy, dx) = (dy_by_byte[ord(dbyte)], dx_by_byte[ord(dbyte)])

        index = dbyte in b"hjkl"  # not in b"asdf"

        sprite = sprites[index]
        sprite.dy = dy
        sprite.dx = dx

        vprint(f"{dbyte=} {sprite.goal=} {sprite.dy=} {sprite.dx=}")

        sprite.step_ahead()

        return ""

    # Rewrite the Screen to match our Shadow of it

    assert (ord("L") ^ 0x40) == 0x0C

    if dbyte == b"\x0C":  # ⌃L
        ts.rows_rewrite(ts.rows, bitrows=ts.bitrows)

        return ""

    # Pause/ resume the Sprites

    if dbyte == b" ":  # Space
        for sprite in sprites:
            sprite.singly = not sprite.singly

        return ""

    # Shove back sharp & loud against meaningless Input

    vprint(f"{dbyte=} Bel")
    sys.stderr.write("\a")  # Terminal Bell
    sys.stderr.flush()

    return ""


#
# Keep up a guess of what the Sh Terminal looks like
#


class TerminalShadow:
    """Keep up a guess of what one Sh Terminal looks like"""

    fd: int
    holds = bytearray()  # partial Packet of Output Bytes
    end = "\r\n"  # Encoding of Line-Break

    rows: list[str]  # Rows of Output Text Characters, from 0 to N-1
    bitrows: list[list[int]]  # Reverse-Video Bit per Character
    cloned_rows: list[str]
    cloned_bitrows: list[list[int]]

    rows = list()  # ["jqdoe@MacBook ~ % "]
    bitrows = list()  # [[1, 0], [0, 1, 0]]
    cloned_rows = list()
    cloned_bitrows = list()

    x = 0  # Cursor Column, counted from 0 Leftmost to N-1 Rightmost
    y = 0  # Cursor Row, counted from 0 Topmost to N-1 Bottommost

    inks: list[bytes]  # Chosen Inks   # []  # [b"\x1B[7m"]
    inks = list()

    def __init__(self, fd) -> None:
        """Form Self"""

        self.fd = fd  # sys.stderr.fileno()

    def rows_checkpoint(self) -> None:
        """Clone the Rows of Text, before inviting the Sprites to overwrite them"""

        assert len(self.rows) == len(self.bitrows), (len(self.rows), len(self.bitrows))
        for row, bitrow in zip(self.rows, self.bitrows):
            assert len(row) == len(bitrow), (len(row), len(bitrow))

        assert not self.cloned_rows, (self.cloned_rows,)
        assert not self.cloned_bitrows, (self.cloned_bitrows,)

        self.cloned_rows.extend(self.rows)  # need deep copy of 'bitrows'
        self.cloned_bitrows.extend(list(list(_) for _ in self.bitrows))

    def rows_rollback(self) -> None:
        """Rewrite the Rows of Text"""

        cloned_rows = self.cloned_rows
        cloned_bitrows = self.cloned_bitrows
        self.rows_rewrite(cloned_rows, bitrows=cloned_bitrows)
        self.rows_commit()

    def rows_rewrite(self, rows, bitrows) -> None:
        """Rewrite the Rows of Text"""

        assert CUU_N == "\x1B[{}A"  # Up
        assert EL == "\x1B[K"  # Erase in Line (EL)  # 04/11

        alt_rows = list(rows)
        alt_bitrows = list(bitrows)
        assert len(alt_rows) == len(alt_bitrows), (len(alt_rows), len(alt_bitrows))
        n = len(alt_rows)

        y = self.y

        if y:
            cuu = "\x1B[{}A".format(y)
            xprint(cuu, end="")

        xprint("\r", end="")

        el = "\x1B[K"
        for i, pair in enumerate(zip(alt_rows, alt_bitrows)):
            (row, bitrow) = pair
            assert len(row) == len(bitrow), (len(row), len(bitrow), i, n)

            compressed = ""
            for x, ch in enumerate(row):
                bit = bitrow[x]
                polarity = "\x1B[7m" if bit else "\x1B[m"  # todo: don't write unneeded
                if ch != "\t":  # prints all but Tabs
                    compressed += polarity + ch
                elif not compressed.endswith("\t"):  # prints first Tab
                    compressed += polarity + ch
                elif not (x % 8):  # prints another Tab at each Tab Stop
                    compressed += polarity + ch
                else:  # skips filler Tabs extending the first Tab
                    pass

            xprint(el + compressed, end=self.end)

        assert len(self.rows) == len(self.bitrows), (len(self.rows), len(self.bitrows))
        for row, bitrow in zip(self.rows, self.bitrows):
            assert len(row) == len(bitrow), (len(row), len(bitrow))

    def rows_commit(self) -> None:
        """Forget about rewriting the Rows of Text"""

        self.cloned_rows.clear()
        self.cloned_bitrows.clear()

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

        assert self.x >= 0, (self.y, self.x)  # not (self.x, self.y)
        assert self.y >= 0, (self.y, self.x)

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

            if seq == b"\t":
                pass
            elif seq[:1] in C0_BYTES:
                if seq == b"\b":
                    vvprint(f"{yx=} {seq=}")  # b"\b"
                    self.x = max(0, self.x - 1)
                elif seq == b"\r":
                    vvprint(f"{yx=} {seq=}")  # b"\r"
                    self.x = 0
                elif seq == b"\n":
                    vvprint(f"{yx=} {seq=}")  # b"\n"
                    self.y += 1

                elif re.match(CsiPattern, string=seq):
                    self.write_csi_seq(seq)

                else:
                    vprint(f"skipping {yx=} {seq=}  # write_bytes")

                continue

            # Find or make the first Row to write

            vvprint(f"{yx=} {seq=}")  # writing Text or Tab, not other C0_CONTROLS

            while self.y >= len(rows):
                rows.append("")
                bitrows.append(list())

            row = rows[self.y]
            bitrow = bitrows[self.y]

            # Overwrite or add the Column

            decode = seq.decode()
            for ch in decode:
                size = os.get_terminal_size(self.fd)

                # Wrap beyond Screen into the next Row, only when not Tabbing,
                # with late roundoff of \x1B[{};{}H CUP_Y1_X1, \x1B{}C CUF_N

                if self.x >= size.columns:
                    self.x = size.columns

                if (ch != "\t") and (self.x >= size.columns):
                    assert self.x == size.columns, (self.x, size.columns)

                    rows[self.y] = row  # unneeded when equal already
                    assert bitrows[self.y] is bitrow

                    self.y += 1
                    self.x = 0

                    while self.y >= len(rows):
                        rows.append("")
                        bitrows.append(list())

                    row = rows[self.y]
                    bitrow = bitrows[self.y]

                # Grow the Row

                while True:
                    while self.x >= len(row):
                        row += " "
                        bitrow += [0]

                    assert len(bitrow) == len(row), (len(bitrow), len(row))
                    assert len(row) <= size.columns, (len(row), size.columns)

                    # Overwrite the Column

                    y = self.y
                    x = self.x

                    assert 0 <= x < len(row), (x, len(row), y)
                    assert 0 <= x < len(bitrow), (x, len(bitrow), y)

                    row = row[:x] + ch + row[x + 1 :]

                    if not self.inks:
                        vvprint(f"{y=} {x=} bit 0")
                        bitrow[x] = 0
                    else:
                        vvprint(f"{y=} {x=} bit 1")
                        bitrow[x] = 1

                    assert len(bitrow) == len(row), (len(bitrow), len(row))

                    # Move the Cursor past the Column Written, even off Screen

                    self.x += 1

                    if ch != "\t":
                        break

                    if self.x >= size.columns:
                        assert self.x == size.columns, (self.x, size.columns)
                        break
                    if not (self.x % 8):
                        break

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
            vvprint(f"{yx=} {seq=}")  # b"\x1B[m"
            self.inks.clear()
            return

        if seq == b"\x1B[0m":  # 06/13
            vvprint(f"{yx=} {seq=}")  # b"\x1B[0m"
            self.inks.clear()
            return

        if seq == b"\x1B[7m":  # 06/13
            vvprint(f"{yx=} {seq=}")  # b"\x1B[7m"
            self.inks.append(seq)
            return

        # Move the Terminal Cursor by Relative Y and X Distances

        assert CUU_N == "\x1B[{}A"  # Up
        assert CUD_N == "\x1B[{}B"  # Down
        assert CUF_N == "\x1B[{}C"  # Forwards Right
        assert CUB_N == "\x1B[{}D"  # Backwards Left

        if tail in b"ABCD":
            vvprint(f"{yx=} {seq=}")  # \x1B[{}A but for A or B or C or D

            size = os.get_terminal_size(self.fd)

            assert 0 <= self.y, (self.y, self.x)
            assert 0 <= self.x, (self.y, self.x)  # not (x, y)

            if self.y >= size.lines:
                self.y = size.lines - 1
            if self.x >= size.columns:
                self.x = size.columns - 1

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
                vvprint(f"{yx=} {seq=}")  # b"\x1B[J"

                self.y_x_end_one_row(self.y, x=self.x)
                self.y_end_the_rows(self.y + 1)
                return

            # todo: "\x1B[{}J", especially "\x1B[0J"

        if tail == b"K":
            if not body:
                vvprint(f"{yx=} {seq=}")  # b"\x1B[K"

                self.y_x_end_one_row(self.y, x=self.x)
                return

            # todo: "\x1B[{}K", especially "\x1B[0K"

        # Log the Instructions we shrug off

        vprint(f"skipping {yx=} {seq=}  # write_csi_seq")

    def y_x_end_one_row(self, y, x) -> None:
        """Truncate one Row on Demand"""

        rows = self.rows
        bitrows = self.bitrows
        assert len(rows) == len(bitrows), (len(rows), len(bitrows))

        if y < len(rows):
            rows[y] = rows[y][:x]
            bitrows[y] = bitrows[y][:x]

            assert len(rows[y]) == len(bitrows[y]), (len(rows[y]), len(bitrows[y]))

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
    assert alt_rlist in (list(), rlist), (alt_rlist, rlist)

    return alt_rlist

    # returns [0] when Stdin available, if called with sys.stdin.fileno() == 0

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
            if find < 0:  # todo: ugh, unbounded delay till b"\x07" does arrive
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
    singly: bool

    terminal_shadow: TerminalShadow

    goal: int  # 0 to paint Plain, 1 to paint Reverse-Video

    y: int
    x: int

    dy: int
    dx: int

    def __init__(self, ts, index) -> None:
        """Form Self"""

        self.steps = 0
        self.singly = False

        self.terminal_shadow = ts
        self.goal = 0 if (index % 2) else 1
        self.yx_init()
        self.dydx_init()

    def step_ahead(self) -> None:
        """Work in parallel with Sh Terminal I/O"""

        if FIXME:
            if self.goal != 0:
                return

        self.steps += 1

        ts = self.terminal_shadow
        assert ts.rows, (ts.rows,)

        #

        yx_0 = (self.y, self.x)
        yx_1 = self.yx_glide()
        yx_2 = self.yx_fit()

        yx_3 = yx_2
        if yx_2 != yx_1:
            self.y_x_warp(*yx_0)
            yx_3 = yx_0

        vprint(f"{yx_0=} {yx_1=} {yx_2=} {yx_3=}  # step_ahead")

        #

        self.y_x_bitput(*yx_0, bit=self.goal)

        below = self.y_x_bitget(*yx_3)
        ballish = not self.goal
        vprint(f"{below=} {ballish=}  # step_ahead")

        if below != ballish:
            self.y_x_bitput(*yx_3, bit=ballish)

        if (yx_2 != yx_1) or (below == ballish):
            self.dydx_bounce()

        if self.singly:
            vprint("singly read  # step_ahead")
            if TextIOElse:
                TextIOElse.flush()
            while not sys_stdio_kbhit(ts.fd, timeout=123):
                pass

    def yx_init(self) -> tuple[int, int]:
        """Land somewhere on the Text"""

        ts = self.terminal_shadow
        rows = ts.rows

        assert rows
        y = len(rows) - 1  # the last Row

        row = rows[y]
        size = os.get_terminal_size(ts.fd)
        if len(row) < size.columns:
            x = len(row)  # the first Column past the Text
        else:
            x = size.columns - 1  # the last Column of the Text

        if FIXME:
            self.singly = True
            y = 1
            x = 85

        yx = self.y_x_warp(y, x)

        return yx

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

        if FIXME:
            dy = 0
            dx = +1

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

        cloned_rows = ts.cloned_rows  # not ts.rows

        assert cloned_rows, (cloned_rows,)
        if y < 0:
            y = 0
        elif y >= len(cloned_rows):
            y = len(cloned_rows) - 1

        c_row = ts.cloned_rows[y]
        beyond_x = len(c_row)  # the first Column beyond the Text

        if x < 0:
            x = 0
        elif x > beyond_x:
            x = beyond_x

        size = os.get_terminal_size(ts.fd)
        if x > (size.columns - 1):
            x = size.columns - 1

        self.y = y
        self.x = x

        yx = (y, x)

        return yx

    def y_x_bitget(self, y, x) -> int:
        """Get the Bit at (Y, X)"""

        ts = self.terminal_shadow

        bitrows = ts.bitrows
        assert 0 <= y < len(bitrows), (y, len(bitrows))
        bitrow = bitrows[y]

        bit = 0  # pads beyond Row with Plain-Video, not Reverse-Video
        if 0 <= x < len(bitrow):
            bit = bitrow[x]

        return bit

    def y_x_bitput(self, y, x, bit) -> None:
        """Put the Bit at (Y, X)"""

        ts = self.terminal_shadow

        c_row = ts.cloned_rows[y]
        ch = c_row[x] if x < len(c_row) else " "  # pads beyond Row with Space's

        self.y_x_bitput_ch(y, x=x, ch_if=ch, bit=bit)

    def y_x_bitput_ch(self, y, x, ch_if, bit) -> None:
        """Put the Bit on the Ch at (Y, X)"""

        ts = self.terminal_shadow

        vprint(f"{y=} {x=} {ch_if=} {bit=} @ {ts.y=} {ts.x=} # y_x_bitput_ch")

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

        size = os.get_terminal_size(ts.fd)

        writable = yto + xto + polarity

        if ch_if:
            if x < (size.columns - 1):
                writable += ch_if + bs
            else:
                assert x == (size.columns - 1), (x, size.columns)
                writable += ch_if

                # todo: \x1B{}H CUP_Y1_X1 in place of BS for Terminals who wrap

        writable += yfrom + xfrom + plain

        data = writable.encode()
        ts.write_bytes(data)
        os.write(ts.fd, data)


#
# Amp up Print for the TerminalShadow
#


def xprint(*args, **kwargs) -> None:
    """Print to Stdout, but also to TerminalShadow"""

    ts = Main.terminal_shadow

    sep = kwargs.get("sep", " ")
    printing = sep.join(str(_) for _ in args)

    print(printing, **kwargs)

    end = kwargs.get("end", "\n")
    ts.write_text(printing + end)


#
# Amp up Print for Logging
#


def vprint(*args, **kwargs) -> None:
    ctprint(*args, **kwargs)
    return


def vvprint(*args, **kwargs) -> None:
    return
    ctprint(*args, **kwargs)
    return


def ctprint(*args, **kwargs) -> None:
    """Print with Stamp to Log File not Stdout, but first compress if compressible"""

    if not TextIOElse:
        return  # run fast by leaving each Arg Str uncalled, when not logging

    sep = kwargs.get("sep", " ")
    printing = sep.join(str(_) for _ in args)

    # Compress =b'...' notation if found

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

    # Else print to our TextIO Log File

    tprint(printing, **kwargs)


def tprint(*args, **kwargs) -> None:
    """Add elapsed Milliseconds Stamp, and print to Log File not Stdout"""

    if not TextIOElse:
        return  # run fast by leaving each Arg Str uncalled, when not logging

    text_io = TextIOElse

    sep = kwargs.get("sep", " ")
    printing = sep.join(str(_) for _ in args)

    # Count milliseconds between Print's

    now = dt.datetime.now()
    ms_int = int((now - Main.tprint_when).total_seconds() * 1000)
    ms = f"{ms_int}ms"

    Main.tprint_when = now

    # Add loud elapsed Milliseconds Stamp only if nonzero

    if ms in ("0ms", "1ms"):
        print(printing, **kwargs, file=text_io)
    else:
        print("\n" + ms + "\n" + printing, **kwargs, file=text_io)


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# bug: refactor os.get_terminal_size into TerminalShadow
# bug: 'noqa C901' marks on 5 Def's

# bug: exiting Sprites doesn't restore Reverse/Plain Video
# bug: exiting Sprites doesn't restore Sgr Colors

# bug: add -vvv depth to wake up logging without recompiling

# bug: 'pty.spawn' calls for patches only when unpatched I/O available
# bug: 'pty.spawn' wrongly flushes Input Paste, in TcsAFlush style, not TcsADrain
# bug: our 'def fd_patch_output' gives no Cpu to Sprites while 'fd_patch_input' blocked


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/demos/ptybreakout.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
