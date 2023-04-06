#!/usr/bin/env python3

r"""
usage: glass1000.py [-h]

move the Cursor to each Mouse Click

options:
  -h, --help  show this help message and exit

quirks:
  quits after you repeat any three input characters, such as Q Q Q
  hangs for 250ms before quitting, if you ran with '--init'

examples:
  ./demos/glass1000.py --  # loop back like a Glass Terminal with no Remote Host
"""

# code reviewed by people, and by Black and Flake8


import datetime as dt
import os
import re
import select
import sys
import termios
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
CPR_REGEX = rb"\x1B[\\[]([0-9]+);([0-9]+)R"
# macOS & Gmail Terminals ignored the "\x1B[?6n" DSR variation in Jan/2023


MAC_PASTE_125MS = 125e-3
MAC_PASTE_CHUNK_1022 = 1022


DECSCUSR_N = "\x1B[{} q"  # Set Cursor Style  # such as "\x1B[2 q"
DECSCUSR = "\x1B[ q"  # Clear Cursor Style (but doc'ed poorly)


Up = "\x1B[A"
Down = "\x1B[B"
Right = "\x1B[C"
Left = "\x1B[D"

UpCodes = Up.encode()
DownCodes = Down.encode()
RightCodes = Right.encode()
LeftCodes = Left.encode()


#
# Run from the Sh command line
#


def main():
    """Run from the Sh command line"""

    parser = byo.compile_argdoc()
    byo.parser_parse_args(parser)  # prints helps and exits, else returns args

    logfile = open("logfile.log", "w")

    with TextUserInterface(sys.stderr) as tui:
        os.write(sys.stdout.fileno(), b"\x1B[" b"?1000h")  # Mouse Enter
        try:
            while True:
                sys.stderr.flush()
                sys.stdout.flush()

                ibytes = b""
                for _ in range(6):
                    ibyte = tui.kbreadbyte()
                    print("0x{:02X}".format(ibyte[0]), file=logfile)
                    ibytes += ibyte
                    if ibytes == b"\x1B":
                        continue
                    elif ibytes[:2] == b"\x1B[":
                        continue
                    elif ibytes[:3] == b"\x1B[M":
                        continue
                    else:
                        sys.exit()

                (cb, cx, cy) = (ibytes[-3], ibytes[-2], ibytes[-1])

                (cx_, cy_) = (cx, cy)
                if cb & 0x20:
                    (cx_, cy_) = (cx - 0x20, cy - 0x20)

                os.write(sys.stdout.fileno(), "\x1B[{};{}H".format(cy_, cx_).encode())

        finally:
            os.write(sys.stdout.fileno(), b"\x1B[" b"?1000l")  # Mouse Exit

            (columns, lines) = tui.terminal_size()
            sys.stdout.write(CUP_Y_X.format(lines, 1))


class TextUserInterface:  # todo: port to Windows
    def __init__(self, stdio):
        """Work at Sys Stderr, or elsewhere"""

        self.fd = stdio.fileno()  # File Descriptor of Keyboard, for Os Read
        self.stdio = stdio  # File Stream of Keyboard, for IsATty and Flush
        self.tcgetattr = None  # Configuration of Terminal at Entry

        self.kblines = list()  # Bursts of Bytes fetched but not yet returned
        self.kblogs = list()  # Log Lines formed but not yet written

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
                # when = termios.TCSAFLUSH  # todo: test for Drain v Flush
                termios.tcsetattr(fd, when, tcgetattr)

    def kbreadbyte(self):
        """Read 1 Byte"""

        if not self.kblines:
            self.kblog()
            self.kblog(21, dt.datetime.now())
            self.kbfill()
            self.kblog(22, dt.datetime.now())
            self.kblogflush()

        kblines = self.kblines
        peek_kbline = kblines[0]

        head = peek_kbline[:1]
        tail = peek_kbline[1:]

        if tail:
            kblines[0] = tail
        else:
            kblines.pop(0)

        return head

        # may be taken from:  re.match(rb"^" + CPR_REGEX + rb"$", string=peek_kbline)

    def kbfill(self):
        """Block till 1 or more Bytes arrive"""

        kblines = self.kblines

        # Block till more Input Bytes from Keyboard

        first_kbline = self.kbreadline()
        assert first_kbline

        if False:  # jitter Sat 15/Jan
            kblines.append(first_kbline)

            return

        # Succeed now, if not led by LeftCodes and RightCodes that can mean Up or Down

        if first_kbline.startswith(LeftCodes):
            pass
        elif first_kbline.startswith(RightCodes):
            pass
        else:
            kblines.append(first_kbline)

            return

        # Succeed now, if given more already

        if self.kbhit(timeout=0):
            kblines.append(first_kbline)

            return

        # Succeed now, if given UpCodes or DownCodes already

        if (UpCodes in first_kbline) or (DownCodes in first_kbline):
            kblines.append(first_kbline)

            return

        self.kbfill_with_dsr_cpr(first_kbline)

        #
        # 5x20 macOS Terminal Jan/2023 delays, splits, catenates, stutters mouse clicks
        #
        #   1 2023-01-15 10:32:39.639331
        #       b'\x1b[C' + 16*b'\x1b[C' + b'\x1b[C\x1b[C\x1b[C' + b'\x1b[5;1R'
        #
        #   1 2023-01-15 10:32:39.639331
        #       10*b'\x1b[D'+b'\x1b[B' + 16*b'\x1b[C' + b'\x1b[B'+4*b'\x1b[C'
        #
        #   1 2023-01-15 10:42:01.589099 21*b'\x1b[C'
        #
        #   1 2023-01-15 10:53:33.193613
        #       19*b'\x1b[C'+b'\x1b[B' + 20*b'\x1b[C'+b'\x1b[B'
        #

        #
        # 89x50 macOS Terminal Jan/2023 delays and splits mouse clicks
        #
        #   1 2023-01-15 11:51:44.386793 b'\x1b[A'
        #   1 2023-01-15 11:51:44.388258 14*b'\x1b[A'
        #   1 2023-01-15 11:51:44.389170 8*b'\x1b[A'
        #   1 2023-01-15 11:51:44.392431 b'\x1b[A'
        #   1 2023-01-15 11:51:44.393010 25*b'\x1b[A'
        #

    def kbfill_with_dsr_cpr(self, first_kbline):
        """Block till 1 or more Bytes arrive"""

        kblines = self.kblines

        # Block till leading Left/ Right Codes defined,
        # because needed at Gmail Terminal Jan/2023 for Tap+Hold and Option+Click

        fill_kblines = list()
        fill_kblines.append(first_kbline)

        self.stdio.write(DSR)
        self.stdio.flush()

        size = self.terminal_size()
        str_size = "{}x{}".format(size.lines, size.columns)
        assert size.columns and size.lines, str_size

        t0 = dt.datetime.now()
        while True:
            cpr_kbline = self.kbreadline()
            fill_kblines.append(cpr_kbline)

            hit = re.search(CPR_REGEX + rb"$", string=cpr_kbline)
            if hit:
                break

            t1 = dt.datetime.now()
            if (t1 - t0).total_seconds() >= 1:
                self.kblog(10.9, dt.datetime.now(), b"".join(fill_kblines), str_size)
                kblines.extend(fill_kblines)

                return

        y = int(hit.group(1), 10)
        x = int(hit.group(2), 10)

        alt_x = size.columns if (x == (size.columns + 1)) else x

        assert 1 <= alt_x <= size.columns, (x, alt_x, hit.groups(), str_size)
        assert 1 <= y <= size.lines, (y, hit.groups(), str_size)

        # Succeed now, if given more during DSR to CPR

        kbhit = self.kbhit(timeout=0)

        self.kblog(11, dt.datetime.now(), b"".join(fill_kblines), str_size, x, y)

        if kbhit or fill_kblines[2:]:
            kblines.extend(fill_kblines)

            return

        # Succeed now, if given UpCodes or DownCodes during DPR to CPR

        join = b"".join(fill_kblines)
        if (UpCodes in join) or (DownCodes in join):
            kblines.extend(fill_kblines)

            return

        # Succeed now, if didn't receive Left-Wrap nor Right-Wrap

        left_wrap = alt_x * LeftCodes
        right_wrap = (size.columns + 1 - alt_x) * RightCodes

        if join.startswith(left_wrap):
            alt_kbline = self.take_gcp_left_wraps(join, size=size, x=alt_x, y=y)
        elif join.startswith(right_wrap):
            alt_kbline = self.take_gcp_right_wraps(join, size=size, x=alt_x, y=y)
        else:
            kblines.extend(fill_kblines)

            return

        # Succeed now, if can't correct Codes by adding in Columns, Lines, X, and Y

        if alt_kbline == join:
            kblines.extend(fill_kblines)

            return

        # Commit to corrected Codes

        kblines.append(alt_kbline)

        self.kblog(12, dt.datetime.now(), alt_kbline)
        self.kblogflush()

        # Gmail Terminal reports X = Columns + 1 after printing into Last Column

    def take_gcp_left_wraps(self, kbline, size, x, y):
        """Take Left past First Column as Up, or Up & Left, or Up & Right"""

        str_size = "{}x{}".format(size.lines, size.columns)
        left_wrap = x * LeftCodes
        left_up = size.columns * LeftCodes

        found = b""
        repl = b""

        # Take Left-Up's as Up's

        ups = 0
        while kbline.startswith(found + left_up):
            found += left_up
            ups += 1

        should = ups < y
        if not self.kblog_should(11.1, kbline, should, ups, str_size, x, y):
            return kbline

        repl += ups * UpCodes

        # Take Left-Wrap-Left's as Up-Right's

        if kbline.startswith(found + left_wrap):
            lefts = 0
            while kbline.startswith(found + LeftCodes):
                found += LeftCodes
                lefts += 1

            rights = size.columns - lefts

            should = 1 < y
            if not self.kblog_should(11.1, kbline, should, 1, str_size, x, y):
                return kbline

            should = lefts < size.columns
            if not self.kblog_should(11.2, kbline, should, lefts, str_size, x, y):
                return kbline

            should = rights <= (size.columns - x)
            if not self.kblog_should(11.3, kbline, should, rights, str_size, x, y):
                return kbline

            repl += UpCodes
            repl += rights * RightCodes

        # Change Codes, or not, as planned above

        alt_kbline = repl + kbline[len(found) :]

        return alt_kbline

        # 115x40 Gmail Terminal gave (25 * 115 + 15) Left's at '\x1b[24;1R' in Jan/2023

    def kblog_should(self, tag, kbline, should, count, str_size, x, y):
        """Return a truthy Should, else log details and return a falsey None"""

        if should:
            return should

        self.kblog(tag, dt.datetime.now(), kbline, should, count, str_size, x, y)

        self.stdio.write("\a")
        self.stdio.flush()

    def take_gcp_right_wraps(self, kbline, size, x, y):
        """Take Right past Last Column as Down, or Down & Right, or Down & Left"""

        str_size = "{}x{}".format(size.lines, size.columns)
        right_wrap = (size.columns + 1 - x) * RightCodes
        right_down = size.columns * RightCodes

        found = b""
        repl = b""

        # Take Right-Down's as Down's

        downs = 0
        while kbline.startswith(found + right_down):
            found += right_down
            downs += 1

        should = downs <= (size.lines - y)
        if not self.kblog_should(11.6, kbline, should, downs, str_size, x, y):
            return kbline

        repl += downs * DownCodes

        # Take Right-Wrap-Right's as Down-Left's

        if kbline.startswith(found + right_wrap):
            rights = 0
            while kbline.startswith(found + RightCodes):
                found += RightCodes
                rights += 1

            lefts = size.columns - rights

            should = y < size.lines
            if not self.kblog_should(11.7, kbline, should, 1, str_size, x, y):
                return kbline

            should = rights < size.columns
            if not self.kblog_should(11.8, kbline, should, rights, str_size, x, y):
                return kbline

            should = lefts < x
            if not self.kblog_should(11.9, kbline, should, lefts, str_size, x, y):
                return kbline

            repl += DownCodes
            repl += lefts * LeftCodes

        # Correct the Codes or leave them unchanged

        alt_kbline = repl + kbline[len(found) :]

        return alt_kbline

    def kbreadline(self):
        """Read 1 or more Bytes of Keystroke, of Keystroke Sequence, or of Paste"""

        fd = self.fd

        # Block till first burst of Input Bytes

        line = b""

        length = MAC_PASTE_CHUNK_1022
        while True:
            more = os.read(fd, length)
            assert more
            self.kblog(1, dt.datetime.now(), more)

            line += more

            if len(more) == length:
                if self.kbhit(timeout=MAC_PASTE_125MS):
                    continue  # needed at macOS Jan/2023 for Large Paste

            break

        self.kblogflush()  # todo: try flushing more frequently, maybe that works

        return line

    def kblog(self, *args):
        """Quickly form another Log Line"""

        kblogs = self.kblogs

        kblogs.append(args)

    def kblogflush(self):
        """Slowly flush Log Lines to File"""

        kblogs = self.kblogs

        if kblogs:
            with open("glass.log", "a") as a:
                while kblogs:
                    args = kblogs.pop(0)

                    args_ = self.kblog_compress_args(args)

                    line = " ".join(str(_) for _ in args_)
                    a.write("{}\n".format(line))

    def kblog_compress_args(self, args):
        """Compress Log Args of bursts of Arrow Codes, or any other Triple Byte Code"""

        # Succeed now if not compressible

        kbline = None
        if args[2:] and isinstance(args[2], bytes):
            args_2 = args[2]

            if len(args_2) >= (4 * 3):
                if b"'" not in args_2:
                    kbline = args_2

        if kbline is None:
            return args

        # Split Bytes into Runs of Bytes

        verbose_runs = list()
        runs = None

        index = 0
        while index < len(kbline):
            triple = kbline[index:][:3]

            found = 1
            while kbline[index:].startswith((found * triple) + triple):
                found += 1

            run = (found, triple)
            verbose_runs.append(run)

            index += 3 * found

            if found >= 4:
                runs = list(verbose_runs)

        if not runs:
            return args

        alt_args = self.kblog_compress_args_2(args, kbline=kbline, runs=runs)

        return alt_args

    def kblog_compress_args_2(self, args, kbline, runs):
        # Require correct Split

        alt_runs = list(runs)

        join = b""
        for run in runs:
            join += run[0] * run[-1]

        assert kbline.startswith(join)

        if kbline != join:
            alt_run = (1, kbline[len(join) :])

            alt_runs.append(alt_run)

        # Don't compress if not much compressible

        rep_kbline = self.kblog_compress_runs(kbline, runs=alt_runs)
        if rep_kbline == str(kbline):
            return args

        # Compress

        alt_args = list(args)
        alt_args[2] = rep_kbline

        return alt_args

    def kblog_compress_runs(self, kbline, runs):
        """Compress bursts of Multi-Byte Codes"""

        # Succeed now if not much compressible

        founds = list(found for (found, _) in runs)
        if max(founds) < 4:
            rep = str(kbline)

            return rep

        # Compress

        reps = list()
        for run in runs:
            (found, codes) = run

            if found < 4:
                rep = str(codes)
            else:
                rep = "{}*{}".format(found, codes)

            reps.append(rep)

        join = " + ".join(reps)

        return join

    def kbhit(self, timeout):  # 'timeout' in seconds
        """Wait till next Byte of Keystroke, next burst of Paste pasted, or Timeout"""

        rs_0 = [self.stdio]
        ws_0 = list()
        xs_0 = list()

        (rs_1, _, _) = select.select(rs_0, ws_0, xs_0, timeout)

        if rs_1 != rs_0:
            assert rs_1 == [], rs_1

        return rs_1

    def terminal_size(self):
        """Work like 'shutil.get_terminal_size', but on 'self.fd'"""

        size = shutil_get_terminal_size_fd(self.fd)

        return size


#
# Extend Import ShUtil
#


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


def shutil_get_terminal_size_fd(fd, fallback=(80, 24)):
    """Work like 'shutil.get_terminal_size', but on a chosen File Descriptor"""

    # Show that Columns come before Lines

    fallback_size = os.terminal_size(fallback)

    assert fallback_size.columns == fallback[0], (fallback_size, fallback)
    assert fallback_size.lines == fallback[-1], (fallback_size, fallback)

    # Try Os Get_Terminal_Size

    try:
        size = os.get_terminal_size(fd)

    # Fall back to Os Environ, else to our Fallback Arg

    except Exception:
        # such as OSError: [Errno 19] Operation not supported by device

        columns = fallback_size.columns
        if "COLUMNS" in os.environ.keys():
            columns = int_else(os.environ["COLUMNS"], default=columns)

        lines = fallback_size.lines
        if "LINES" in os.environ.keys():
            lines = int_else(os.environ["LINES"], default=lines)

        tupled = (columns, lines)
        size = os.terminal_size(tupled)

    return size  # such as:  os.terminal_size(columns=80, lines=24)

    # note: Python's ShUtil jumped to Not IsATty when just Stdout redirected

    _ = """

COLUMNS=1_123.456 LINES=0x80 \
python3 -c '''

import os, shutil, sys
sys.stderr.write(str(shutil.get_terminal_size()) + "\n")

''' >/dev/null

    """


# os.terminal_size(columns=80, lines=24)  # without the COLUMNS LINES
# os.terminal_size(columns=1123, lines=128)  # with the COLUMNS LINES


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/glass1000.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
