#!/usr/bin/env python3

r"""
usage: ttypaint.py [-h]

copy bytes to screen from keyboard

options:
  -h, --help  show this help message and exit

quirks:
  quits when told to copy ⌃M ⌃M ⌃M

examples:
  ./demos/ttypaint.py --  # loop back like a Glass Terminal with no Remote Host
"""

# code reviewed by people, and by Black and Flake8


import datetime as dt
import os
import select
import shutil
import sys
import termios
import tty

_ = dt


#
# Run from the Sh command line
#


def main():
    assert sys.argv[1:] == ["--"], sys.argv[1:]

    print()
    print("Press Return (or ⌃M) three times to quit")
    print()

    assert CUP_Y_X == b"\x1B[{};{}H"

    _ = shutil.get_terminal_size()

    try:
        stdio_loopback()
    finally:
        (x, y) = shutil.get_terminal_size()
        x_ = 1
        echo = "\x1B[{};{}H".format(y, x_).encode()
        os.write(sys.__stdout__.fileno(), echo)


def stdio_loopback():
    lines = list()

    stdio = sys.__stdout__  # '__stdout__' per 'shutil.get_terminal_size'
    fd = stdio.fileno()

    with GlassTeletype(stdio) as gt:
        while True:
            line = gt.readline()
            lines.append(line)

            echo = bytes_echo(line)

            if False:  # jitter Sat 8/Apr
                with open("l.log", "a") as file_:
                    print(file=file_)
                    print(dt.datetime.now(), file=file_)
                    print(ascii(line), file=file_)
                    print(ascii(echo), file=file_)

            os.write(fd, echo)

            if lines[-3:] == [b"\r", b"\r", b"\r"]:
                break


def bytes_echo(line):
    """Choose how to echo one Keyboard Input struck or pasted"""

    assert CUP_Y_X == b"\x1B[{};{}H"
    assert MouseButton == b"\x1B[" b"M"

    echo = line

    if len(line) == 6:
        if line.startswith(b"\x1B[" b"M"):
            (cb, cx, cy) = (line[-3], line[-2], line[-1])

            _ = cb
            assert cx > 0x20, hex(cx)
            assert cy > 0x20, hex(cy)

            (x, y) = (cx - 0x20, cy - 0x20)

            echo = "\x1B[{};{}H".format(y, x).encode()

    return echo


class GlassTeletype:
    """Read from Keyboard, write to Screen, but don't line-buffer the Keyboard Input"""

    def __init__(self, stdio):
        self.stdio = stdio
        self.fd = stdio.fileno()
        self.line = bytearray()

    def __enter__(self):
        """Stop streaming Lines in from the Keyboard, start streaming Bytes in"""

        fd = self.fd

        assert MouseEnter == b"\x1B[" b"?1000h"
        assert PasteEnter == b"\x1B[" b"?2004h"

        tcgetattr = termios.tcgetattr(fd)
        tty.setraw(fd, when=termios.TCSADRAIN)  # Drain flushes Output, then changes
        # termios.TCSAFLUSH  # Flush destroys Input, flushes Output, then changes

        os.write(fd, b"\x1B[" b"?2004h")
        os.write(fd, b"\x1B[" b"?1000h")

        self.tcgetattr = tcgetattr

        return self

        # also stop adding "\r" before each "\n" of Output

    def __exit__(self, *exc_info):
        """Stop streaming Bytes in from the Keyboard, restart streaming Lines in"""

        fd = self.fd
        tcgetattr = self.tcgetattr

        assert MouseExit == b"\x1B[" b"?1000l"
        assert PasteExit == b"\x1B[" b"?2004l"

        os.write(fd, b"\x1B[" b"?1000l")
        os.write(fd, b"\x1B[" b"?2004l")

        when = termios.TCSADRAIN
        termios.tcsetattr(fd, when, tcgetattr)

        # also restart adding "\r" before each "\n" of Output

    def print(self, *args, **kwargs):
        """Work like Print, but default to end with all of '\r\n', not with just '\n'"""

        alt_kwargs = dict(kwargs)
        if ("end" not in kwargs) or (kwargs["end"] is None):
            alt_kwargs["end"] = "\r\n"

        print(*args, **alt_kwargs)

    def readline(self):
        """Read the next Keyboard Input struck or pasted"""

        fd = self.fd
        line = self.line

        # Return the next whole Chunk of Paste or Key Stroke

        while True:
            (stroke, lookahead) = bytes_splitstroke(line)
            if stroke:
                line[::] = lookahead
                return stroke

            # Else read many Bytes pasted in a rush, or a few, or one

            length = 1500  # 2023-03 macOS yielded 1022 Bytes per call
            timeout = 125e-3

            while True:
                read = os.read(fd, length)
                line.extend(read)

                if len(read) >= 1000:
                    if self.kbhit(timeout):
                        continue
                break

    def kbhit(self, timeout):  # 'timeout' in seconds
        """Wait till next Keyboard Input struck or pasted, or Timeout"""

        rlist = [self.stdio]
        wlist = list()
        xlist = list()

        (rlist_, _, _) = select.select(rlist, wlist, xlist, timeout)

        return rlist_  # emptied after Timeout, else copied 'rlist'


def bytes_splitstroke(line):
    """Pick out the next whole Chunk of Paste or Key Stroke"""

    assert MouseButton == b"\x1B[" b"M"

    stroke = line
    lookahead = b""

    if len(line) >= 6:
        if line.startswith(b"\x1B[" b"M"):
            stroke = line[:6]
            lookahead = line[6:]

    stroke = bytes(stroke)
    lookahead = bytes(lookahead)

    return (stroke, lookahead)


#
# Decipher Terminal Byte Codes, written or read, in the way of
#
#   https://en.wikipedia.org/wiki/ANSI_escape_code
#   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
#

Esc = b"\x1B"

CSI = b"\x1B["


#
# Decipher Keyboard Byte Codes, mostly read and rarely written
#


CPR = b"\x1B[{};{}R"  # Cursor Position Report (CPR) of Row Y Column X in reply to DSR

MouseButton = b"\x1B[" b"M"


#
# Decipher Screen Byte Codes, mostly written and rarely read
#


CUP_Y_X = b"\x1B[{};{}H"  # Cursor Position (CUP) to move Cursor to Row Y Column X

DSR = b"\x1B[" b"6n"  # Device Status Report (DSR) call for CPR

MouseEnter = b"\x1B[" b"?1000h"  # CSI ? Pm h  # Ps = 1 0 0 0  # SET_VT200_MOUSE
MouseExit = b"\x1B[" b"?1000l"  # CSI ? Pm l  # Ps = 1 0 0 0  # SET_VT200_MOUSE

PasteEnter = b"\x1B[" b"?2004h"  # CSI ? Pm h  # Ps = 2 0 0 4
PasteExit = b"\x1B[" b"?2004l"  # CSI ? Pm l  # Ps = 2 0 0 4


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/ttypaint.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
