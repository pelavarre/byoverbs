#!/usr/bin/env python3

r"""
usage: byotty.py [-h]

read the Bytes of Terminal Keyboard Input & Paste

options:
  -h, --help  show this help message and exit

notes:
  doesn't delay the Bytes till End-of-Line
  doesn't write \n Line Feed (LF) as \r\n CR LF, write LF as LF
  doesn't take ⌃C ⌃D ⌃\ ⌃Z as Signals of KeyboardInterrupt, EndOfInput, Quit, Suspend

lots of docs:
  https://unicode.org/charts/PDF/U0000.pdf
  https://unicode.org/charts/PDF/U0080.pdf
  https://en.wikipedia.org/wiki/ANSI_escape_code
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
  https://www.ecma-international.org/publications-and-standards/standards/ecma-48
    /wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf

usage examples:
  PYTHONPATH=bin/optionee python3 bin/optionee/byo/byotty.py --
"""

# code reviewed by People, Black, Flake8, & MyPy


import datetime as dt
import os
import re
import select
import sys
import termios  # unhappy at Windows
import tty  # unhappy at Windows

import byo
from byo import byoargparse

... == dict[str, int]  # new since Oct/2020 Python 3.9  # type: ignore
# ... == typing.Self  # new since Oct/2022 Python 3.11  # type: ignore

... == byo  # ducks Flake8 F401 imported.but.unused  # type: ignore


#
# Run from the Sh Command Line
#


def main() -> None:
    """Run from the Sh Command Line"""

    parser = byoargparse.ArgumentParser()
    parser.parse_args_else()  # often prints help & exits zero

    # Copy Bytes of Keyboard or Paste to Screen,
    # as Chords of Words of Chars and themselves, else as themselves alone

    with BytesTerminal(sys.stderr) as bt:
        quits = (b"\x03", b"\x04", b"\x1A", b"\x1C", b"Q")  # ⌃C ⌃D ⌃Z ⌃\ ⇧Q
        bt.print(r"Press ⇧Z ⇧Q to quit, or any one of ⌃C ⌃D ⌃Z ⌃\ ".rstrip())
        bt.print()  # doesn't accept : Q ! Return

        t0 = dt.datetime.now()
        while True:
            data = bt.read_chord_bytes()

            # Time the arrivals, log the details

            t1 = dt.datetime.now()
            bt.print(t1 - t0, data)
            if data == b" ":
                bt.breakpoint()

            t0 = dt.datetime.now()

            # Quit on request

            if data in quits:
                break

        # yes the Tty at Stderr, not a Tty at the Stdout of ShUtil Get_Terminal_Size


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
SS3 = b"\x1BO"  # 01/11 04/15 Single Shift Three

CsiStartPattern = b"\x1B\\[" rb"[\x30-\x3F]*[\x20-\x2F]*"  # leading Zeroes allowed
CsiEndPattern = rb"[\x40-\x7E]"
CsiPattern = CsiStartPattern + CsiEndPattern
# Csi Patterns define many Pm, Pn, and Ps, but not the Pt of Esc ] OSC Ps ; Pt BEL
# in 5.4 Control Sequences of ECMA-48_5th 1991

MouseThreeByteStartPattern = b"\x1B\\[" rb"M"
MouseSixByteEndPattern = b"\x1B\\[" rb"M..."  # MPR X Y


#
# Read the Raw Bytes from a Terminal
#


class BytesTerminal:
    r"""Read the Raw Bytes from a Terminal"""

    tcgetattr_else: list[int | list[bytes | int]] | None

    def __init__(self, stdio) -> None:
        fd = stdio.fileno()

        self.stdio = stdio
        self.fd = fd
        self.tcgetattr_else = None
        self.holds = bytearray()

    def __enter__(self) -> "BytesTerminal":  # -> typing.Self:
        r"""Stop line-buffering Input, stop replacing \n Output with \r\n, etc"""

        fd = self.fd
        tcgetattr_else = self.tcgetattr_else

        if tcgetattr_else is None:
            tcgetattr = termios.tcgetattr(fd)
            assert tcgetattr is not None

            self.tcgetattr_else = tcgetattr

            # choose to enter through
            #   TCSAFLUSH - Flush destroys Input, flushes Output, then changes
            #   TCSADRAIN - Drain flushes Output, then changes

            if False:  # jitter Sat 19/Aug
                tty.setcbreak(fd, when=termios.TCSAFLUSH)  # ⌃C prints Py Traceback
            else:
                tty.setraw(fd, when=termios.TCSADRAIN)  # SetRaw defaults to TcsaFlush

        self.try_me()

        return self

    def __exit__(self, *exc_info) -> None:
        r"""Start line-buffering Input, start replacing \n Output with \r\n, etc"""

        fd = self.fd

        tcgetattr_else = self.tcgetattr_else
        if tcgetattr_else is not None:
            tcgetattr = tcgetattr_else

            self.tcgetattr_else = None

            # choose to exit through
            #   TCSAFLUSH - Flush destroys Input, flushes Output, then changes
            #   TCSADRAIN - Drain flushes Output, then changes

            when = termios.TCSADRAIN
            termios.tcsetattr(fd, when, tcgetattr)

            # todo: test of Drain vs Flush at Exit

        return None

    def breakpoint(self) -> None:
        """Exit and then breakpoint and then re-enter"""

        self.__exit__(*sys.exc_info())
        breakpoint()
        self.__enter__()

    def get_terminal_columns(self) -> int:
        """Count Columns on Screen"""

        fd = self.fd
        size = os.get_terminal_size(fd)  # often < 50 us
        columns = size.columns

        return columns

    def get_terminal_rows(self) -> int:
        """Count Rows on Screen"""

        fd = self.fd
        size = os.get_terminal_size(fd)  # often < 50 us
        rows = size.lines

        return rows

        # 'shutil.get_terminal_size' often runs < 100 us

    def print(self, *args, **kwargs) -> None:
        r"""Work like Print, but end with \r\n, not with \n"""

        assert CRLF == b"\r\n"

        alt_kwargs = dict(kwargs)
        if ("end" not in kwargs) or (kwargs["end"] is None):
            alt_kwargs["end"] = "\r\n"

        print(*args, **alt_kwargs)

    def write(self, data) -> None:
        """Write some Bytes without encoding them, & without ending the Line"""

        fd = self.fd
        os.write(fd, data)

    def read_chord_bytes(self) -> bytes:
        r"""Block till read of Paste or Chords"""

        while True:
            available = self.count_available(func=bytes_take_startswith_else)
            if available:
                break
            self.kbhit()  # blocks till more Bytes arrive

        data = self.read(length=available)

        return data

    def count_available(self, func) -> int:
        """Count the Bytes available to read to satisfy Func, without blocking"""

        holds = self.holds

        while True:
            held_bytes = bytes(holds)
            chord_bytes = func(held_bytes)
            if chord_bytes:
                return len(chord_bytes)

            if not self.kbhit(timeout=0):
                break

            more_held_bytes = self.read()
            holds.extend(more_held_bytes)

        return 0

        # for Func's such as:  bytes_take_startswith_else

    def read(self, length=1022) -> bytes:
        """Block to read one or more Bytes of Paste or Chords"""

        fd = self.fd
        holds = self.holds

        if length <= len(holds):
            held_bytes = bytes(holds[:length])
            del holds[:length]
            return held_bytes

        read = os.read(fd, length)
        assert read, read  # todo: test when 'os.read' does return b""
        assert len(read) <= length, (len(read), length)

        return read

        # large Paste often came as 1022 Bytes per 100ms  # macOS 2023-03
        # ⌘V ⌘V Paste sometimes arrived slung together into one read  # macOS 2023-03

    def kbhit(self, timeout=None) -> list[int]:  # 'timeout' in seconds
        """Wait till next Input Byte, else till Timeout, else till forever"""

        stdio = self.stdio

        rlist: list[int] = [stdio]
        wlist: list[int] = list()
        xlist: list[int] = list()

        (alt_rlist, _, _) = select.select(rlist, wlist, xlist, timeout)

        return alt_rlist

    def try_me(self) -> None:
        """Run a quick thorough self-test"""

        self.write(b"")  # tests 'os.write'
        self.kbhit(0)  # tests 'select.select'


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


def _bytes_take_c0_esc_etc_else(data) -> bytes:
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

    # Take Esc with a Text Byte of 7-Bit US-Ascii as a Byte Pair,
    # and take Esc alone when given before Esc or Control or not 7-bit US-Ascii

    if esc_plus != b"\x1B[":  # CSI
        if (esc_plus[-1:] in C0_BYTES) or (esc_plus[-1] >= 0x80):
            return b"\x1B"

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
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/optionee/byo/
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
