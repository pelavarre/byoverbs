#!/usr/bin/env python3

"""
usage: glass.py [-h] [-X]

print the bytes of keystrokes to the screen, when they arrive, as they arrive

options:
  -h, --help     show this help message and exit
  -X, --no-init  run in the main screen, not in the alt screen, a la:  less -X

quirks:
  hangs for 1s then quits after you repeat any three input characters, such as Q Q Q
  just quits without hanging, if you run with '--no-init'

examples:
  ./demos/glass.py --h  # show help and examples
  ./demos/glass.py  # show examples
  ./demos/glass.py --  # loop back like a Glass Terminal with no Remote Host
"""

# code reviewed by people, and by Black and Flake8


import datetime as dt
import os
import select
import sys
import termios
import time
import tty


DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path[1:1] = [os.path.join(DIR, os.pardir, "bin")]

try:
    import byotools as byo
except Exception:  # auth edit of Sys Path for Flake8 with this Try Except Block

    raise


#
# Configure Text User Interface
#
#   https://en.wikipedia.org/wiki/ANSI_escape_code
#   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
#


ESC = "\x1B"  # Esc
CSI = ESC + "["  # Control Sequence Introducer (CSI)


ED_2 = "\x1B[2J"  # Erase in Display (ED)  # 2 = Whole Screen
CUP_Y_X = "\x1B[{};{}H"  # Cursor Position (CUP)  # such as "\x1B[1;1H"
CUP_1_1 = "\x1B[H"  # Cursor Position (CUP)  # (1, 1) = Upper Left

DECSC = ESC + "7"  # DEC Save Cursor
DECRC = ESC + "8"  # DEC Restore Cursor

_XTERM_ALT_ = "\x1B[?1049h"  # show Alt Screen
_XTERM_MAIN_ = "\x1B[?1049l"  # show Main Screen

SMCUP = DECSC + _XTERM_ALT_  # Set-Mode Cursor-Positioning
RMCUP = ED_2 + _XTERM_MAIN_ + DECRC  # Reset-Mode Cursor-Positioning

_CURSES_INITSCR_ = SMCUP + ED_2 + CUP_1_1
_CURSES_ENDWIN_ = RMCUP


DSR = "\x1B[6n"  # Device Status Report, answered by CPR_Y_X
CPR_Y_X = "\x1B[{};{}R"  # Cursor Position Report, called for by DSR
# Wikipedia mentions the "\x1B[?6n" variation  # Gmail Terminal ignored it Jan/2023


DECSCUSR_N = "\x1B[{} q"  # Set Cursor Style  # such as "\x1B[2 q"
DECSCUSR = "\x1B[ q"  # Clear Cursor Style (but doc'ed poorly)


MAC_PASTE_125MS = 125e-3
MAC_PASTE_CHUNK_1022 = 1022


#
# Run from the Sh command line
#


def main():
    """Run from the Sh command line"""

    parser = byo.compile_argdoc()

    X_help = "run in the main screen, not in the alt screen, a la:  less -X"
    parser.add_argument("-X", "--no-init", action="count", help=X_help)

    args = byo.parser_parse_args(parser)  # prints helps and exits, else returns args

    #

    with open("glass.log", "w"):
        pass

    if not args.no_init:
        sys.stdout.write(_CURSES_INITSCR_)

    try:
        ibytes = b""
        with TextUserInterface(sys.stderr) as tui:
            if not args.no_init:
                print()
                print(tui.shutil_get_terminal_size(), end="\r\n")
                print()
                print("Press Q Q Q to quit, or other keys")
                print()

            if False:
                sys.stdout.write("\x1B[6n")
                sys.stdout.flush()

            while True:
                sys.stdout.flush()

                ibyte = tui.kbreadbyte()
                os.write(sys.stdout.fileno(), ibyte)
                ibytes += ibyte

                if ibytes[2:]:
                    if len(set(ibytes[-3:])) == 1:

                        break

            (columns, lines) = tui.shutil_get_terminal_size()
            sys.stdout.write(CUP_Y_X.format(lines, 1))
            sys.stdout.flush()

    finally:

        if not args.no_init:
            print("... sleeping briefly ...  ", end="")
            sys.stdout.flush()

            time.sleep(1)
            sys.stdout.write(_CURSES_ENDWIN_)


class TextUserInterface:  # todo: port to Windows
    def __init__(self, stdio):
        """Work at Sys Stderr, or elsewhere"""

        self.fd = stdio.fileno()  # File Descriptor of Keyboard, for Os Read
        self.stdio = stdio  # File Stream of Keyboard, for IsATty and Flush
        self.tcgetattr = None  # Configuration of Terminal at Entry

        self.kblogs = list()  # Ops completed but not yet logged
        self.kbpops = list()  # Bytes fetched but not yet returned

    def __enter__(self):
        """Flush, then start taking Keystrokes literally & writing Lf as itself"""

        fd = self.fd
        tcgetattr = self.tcgetattr
        stdio = self.stdio

        # Flush output before changing buffering

        stdio.flush()

        # Stop line-buffering input, or leave it stopped

        if termios:
            if stdio.isatty() and (tcgetattr is None):
                tcgetattr = termios.tcgetattr(fd)
                assert tcgetattr is not None

                self.tcgetattr = tcgetattr

                tty.setraw(fd, when=termios.TCSADRAIN)  # not TCSAFLUSH

                # todo: show that queued input survives

        # Succeed

        tui = self

        return tui

    def __exit__(self, *exc_info):
        """Flush, then stop taking Keystrokes literally & start writing Lf as Cr Lf"""

        _ = exc_info

        fd = self.fd
        tcgetattr = self.tcgetattr
        stdio = self.stdio

        # Flush output before changing buffering

        stdio.flush()

        # Flush input  # todo: apps that don't want Flush Input at Exit

        if termios:
            length = MAC_PASTE_CHUNK_1022
            while self.kbhit(timeout=0):
                _ = os.read(fd, length)

        # Start line-buffering input, or leave it started

        if termios:
            if tcgetattr is not None:
                self.tcgetattr = None  # mutate

                when = termios.TCSADRAIN
                # when = termios.TCSAFLUSH  # todo: find a tebst that cares
                termios.tcsetattr(fd, when, tcgetattr)

    def kbreadbyte(self):
        """Read 1 Byte"""

        kbpops = self.kbpops

        #

        if not kbpops:

            # FIXME: ask to sample cursor position if not kbhit

            #

            kbline = self.kbreadline()
            assert kbline

            # Search for miscodings in Paste or in bursts of Keystrokes

            alt_kbline = kbline
            if len(kbline) > 3:

                (columns, _) = self.shutil_get_terminal_size()

                Up = b"\x1B[A"
                Down = b"\x1B[B"
                Right = b"\x1B[C"
                Left = b"\x1B[D"

                # FIXME: detect more Left or Right than fits vs CPR Cursor Position

                # Liberally accept miscoding Up as a Left in every Column

                LeftLine = columns * Left
                alt_kbline = alt_kbline.replace(LeftLine, Up)

                # Liberally accept miscoding Down as a Right in every Column

                RightLine = columns * Right
                alt_kbline = alt_kbline.replace(RightLine, Down)

                if kbline != alt_kbline:
                    self.kblog(2, dt.datetime.now(), columns, alt_kbline)

                # liberal Up/ Down needed at Gmail Terminal Jan/2023 for Option+Click

            #

            kbpops.extend(list(alt_kbline[_:][:1] for _ in range(len(alt_kbline))))

        pop = kbpops.pop(0)

        return pop

        # Gmail Terminal Mobile Tap+Hold worked like Laptop Option+Click

    def kbwritedsr(self, more):

        Up = b"\x1B[A"
        Down = b"\x1B[B"
        Right = b"\x1B[C"
        Left = b"\x1B[D"

        assert len(Up) == len(Down) == len(Right) == len(Left)

        for arrow in (Up, Down, Right, Left):
            if more == ((len(more) // len(Up)) * arrow):
                self.kblog(0, dt.datetime.now(), len(more), DSR.encode())
                self.stdio.write(DSR)
                self.stdio.write("\a")
                self.stdio.flush()

                self.kbwritedsr = lambda _: None

                return

    def kbreadline(self):
        """Read 1 or more Bytes arriving as 1 Keystroke, or a Keystroke Sequence, or Paste"""

        fd = self.fd

        #

        line = b""

        length = MAC_PASTE_CHUNK_1022
        while True:
            more = os.read(fd, length)
            assert more

            self.kbwritedsr(more)

            self.kblog(1, dt.datetime.now(), more)

            # FIXME: snoop reports of cursor position

            #

            line += more

            if self.kbhit(timeout=0):

                continue  # needed at Gmail Terminal Jan/2023 for Option+Click

            if len(more) == length:
                if self.kbhit(timeout=MAC_PASTE_125MS):

                    continue  # needed at macOS Jan/2023 for large paste

            break

        self.kblogflush()

        return line

    def kblog(self, *args):

        kblogs = self.kblogs

        kblogs.append(args)

    def kblogflush(self):

        kblogs = self.kblogs

        if kblogs:
            with open("glass.log", "a") as a:
                while kblogs:
                    args = kblogs.pop(0)
                    line = " ".join(str(_) for _ in args)
                    a.write("{}\n".format(line))

    def kbhit(self, timeout):  # 'timeout' in seconds
        """Wait till next Byte of Keystroke, next burst of Paste pasted, or Timeout"""

        rs_0 = [self.stdio]
        ws_0 = list()
        xs_0 = list()

        (rs_1, _, _) = select.select(rs_0, ws_0, xs_0, timeout)

        if rs_1 != rs_0:
            assert rs_1 == [], rs_1

        return rs_1

    def shutil_get_terminal_size(self):
        """Run much like 'shutil.get_terminal_size', but on our File Descriptor"""

        def int_else(i, key, default):

            if i > 0:

                return i  # from 'os.get_terminal_size'

            if key in os.environ.keys():
                value = os.environ[key]
                try:

                    return int(value)  # from '123', '1_123.456', '0x80', etc

                except Exception:

                    pass

            return default

        try:
            size = os.get_terminal_size(self.fd)
        except Exception:
            size = os.terminal_size(columns=0, lines=0)

            # such as OSError: [Errno 19] Operation not supported by device

        columns = int_else(size.columns, key="COLUMNS", default=80)
        lines = int_else(size.lines, key="LINES", default=24)

        t = (columns, lines)
        size = os.terminal_size(t)

        assert size.columns == columns, (t, size)
        assert size.lines == lines, (t, size)

        return size

        # note: Python's ShUtil jumped to Not IsATty when just Stdout redirected

        _ = """

COLUMNS=1_123.456 LINES=0x80 python3 -c '''

import os, shutil, sys
sys.stderr.write(str(shutil.get_terminal_size()) + "\n")

''' >/dev/null

        """  # os.terminal_size(columns=1123, lines=128)


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/glass.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
