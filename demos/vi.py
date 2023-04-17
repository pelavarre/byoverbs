#!/usr/bin/env python3

r"""
usage: vi.py [-h] [-q]

copy Bytes to Screen from Keyboard, till told to quit

options:
  -h, --help   show this help message and exit
  -q, --quiet  say less

quirks:
  quits when told ⌃C ⇧Z ⇧Q or ⌃C : Q ! Return
  loosely emulates Vi ⌃C ⌃G ⌃M ⌃N ⌃P Space Return $ + 0 G H K N ^ ) h j k l |
  logs Keystrokes, Paste, and Milliseconds Delays when told ⇧Z ⇧K, until ⌃C
  copies exactly when told ⇧Z ⇧S, until ⌃C
  edits classic Vi output, when run inside:  vi +':set t_ti= t_te='

examples:
  ./demos/vi.py --  # talks Cheat Codes to the Vi Easter Egg buried in the Terminal
  ./demos/vi.py -q  # doesn't write Escape Sequences at entry/ exit
  ls -CR && ./demos/vi.py --  # fills Screen with Text and then edits it
  cat ./demos/vi.py |dd bs=1 count=10123 |tr '[ -~]' '.' |pbcopy  # makes large Paste
"""

# code reviewed by people, and by Black and Flake8


# "⌃" == "\u2303" == "\N{Up Arrowhead}" of the 'Control+' Modifier
# "⌥" == "\u2325" == "\N{Option Key}" of the 'Option+' Modifier
# "⇧" == "\u21E7" == "\N{Upwards White Arrow}" of the 'Shift+' Modifier
# "⌘" == "\u2318" == "\N{Place of Interest Sign}" of the 'Command+' Modifier


import __main__
import argparse
import datetime as dt
import difflib
import os
import re
import select
import shutil
import struct
import sys
import termios
import textwrap
import tty


#
# Run from the Sh command line
#


def main():
    """Run from the Sh command line"""

    args = parse_vi_py_args()
    main.args = args

    stdio = sys.__stdout__  # '__stdout__' as per 'shutil.get_terminal_size'

    with ByteTerminal(stdio) as bt:
        with CharTerminal(bt) as ct:
            ct.readlines()


def parse_vi_py_args():
    """Parse the Args from the Sh command line"""

    parser = compile_argdoc()
    parser.add_argument("-q", "--quiet", dest="q", action="count", help="say less")

    args = parser_parse_args(parser)  # prints help and exits zero, when asked

    args.quiet = args.q if args.q else 0

    return args


class CharTerminal:
    """Copy Bytes to Screen from Keyboard, till told to quit"""

    def __init__(self, bt):
        self.bt = bt

        t0 = dt.datetime.now()

        self.t0 = t0
        self.t1 = t0
        self.line = b""

        self.lines = b""
        self.bot_by_lines = self.form_bot_by_lines()

    def __enter__(self):
        """Configure the Terminal and greet the Operator, or not"""

        args = main.args

        assert MouseEnter == b"\x1B[?1000h"
        assert MouseSgrUp == b"\x1B[?1006h"
        assert BracketedPasteEnter == b"\x1B[?2004h"

        if not args.quiet:
            self.bt_write(b"\x1B[?1000h")
            self.bt_write(b"\x1B[?1006h")
            self.bt_write(b"\x1B[?2004h")

            self.greet()

        return self

    def __exit__(self, *exc_info):
        """Undo the Configure Terminal at entry, or not"""

        args = main.args

        assert BracketedPasteExit == b"\x1B[?2004l"
        assert LowerLeftForm == b"\x1B[{y}H"  # y=1
        assert MouseExit == b"\x1B[?1000l"
        assert MouseSgrDown == b"\x1B[?1006l"

        if not args.quiet:
            size = shutil.get_terminal_size()

            self.bt_write(b"\x1B[?2004l")
            self.bt_write(b"\x1B[?1006l")
            self.bt_write(b"\x1B[?1000l")

            self.bt_write("\x1B[{y}H".format(y=size.lines).encode())

    def bt_write(self, line):
        """Write Bytes out through 'self.bt' Byte Terminal"""

        bt = self.bt
        bt.write(line)

    def bt_breakpoint(self):
        """Breakpoint outside of Bracketed Paste"""

        bt = self.bt

        assert BracketedPasteEnter == b"\x1B[?2004h"
        assert BracketedPasteExit == b"\x1B[?2004l"

        bt.write(b"\x1B[?1000l")
        bt.breakpoint()
        bt.write(b"\x1B[?1000h")

    def greet(self):
        """Prompt the Operator"""

        bt = self.bt

        bt.print()
        bt.print("Press ⌃C ⇧Z ⇧K to log Keystrokes and Paste, ⌃C to stop")
        bt.print("Press ⌃C ⇧Z ⇧S to copy Bytes to Screen from Keyboard, ⌃C to stop")
        bt.print("Press ⌃C ⇧Z ⇧Q or ⌃C : Q ! Return to quit")

    def readline(self):
        """Read and log the next Keystroke or Paste"""

        bt = self.bt

        # Read and time-stamp the next Keystroke or Paste

        t0 = self.t1
        line = bt.readline()
        t1 = dt.datetime.now()

        self.t0 = t0
        self.t1 = t1
        self.line = line

        # Succeed

        return line

    def logline(self):
        """Log this Keystroke or Paste"""

        bt = self.bt

        t0 = self.t0
        t1 = self.t1
        line = self.line

        t1t0 = int((t1 - t0).total_seconds() * 1000)
        if len(str(line)) <= 75:
            bt.print("{}ms {} {}".format(t1t0, len(line), line))
        else:
            formed = "{}ms {} {} ... {}".format(t1t0, len(line), line[:20], line[-20:])
            bt.print(formed)

        # FIXME: uppercase the hex

    def runlines(self):
        """Run the Code that defines a Line, else ring the Terminal Bell"""

        assert MouseSgrReportPattern == b"\x1B\\[<([0-9]+);([0-9]+);([0-9]+)([Mm])"

        bot_by_lines = self.bot_by_lines
        lines = self.lines

        key = lines
        if key.startswith(b"\x1B[<"):
            key = b"\x1B[<"

        bot = self.write_bel
        if key in bot_by_lines.keys():
            bot = bot_by_lines[key]

        bot()

    #
    # Name some Loops
    #

    def readlines(self):  # ⌃C
        """Copy Bytes to Screen from Keyboard, till told to quit"""

        while True:
            line = self.readline()
            self.lines = line
            self.runlines()

    def try_keyboard(self):  # ⇧Z ⇧K
        """Log Keystrokes, Paste, & Delays from Keyboard, till told to quit"""

        args = main.args
        bt = self.bt

        assert control(b"C") == b"\x03"
        assert LowerLeftForm == b"\x1B[{y}H"  # y=1

        if not args.quiet:
            bt.print("Press ⌃C to stop logging Keystrokes and Paste")

        while True:
            line = self.readline()
            self.logline()

            if line == b"\x03":
                break

        if not args.quiet:
            size = shutil.get_terminal_size()
            self.bt_write("\x1B[{y}H".format(y=size.lines).encode())
            bt.print()
            bt.print("Press ⌃C ⇧Z ⇧Q or ⌃C : Q ! Return to quit")

    def try_screen(self):  # ⇧Z ⇧S
        """Copy Keystrokes and Paste to Screen, till told to quit"""

        args = main.args
        bt = self.bt

        assert control(b"C") == b"\x03"
        assert LowerLeftForm == b"\x1B[{y}H"  # y=1

        if not args.quiet:
            bt.print("Press ⌃C to stop copying Keystrokes and Paste to Screen")

        while True:
            line = self.readline()
            self.bt_write(line)

            if line == b"\x03":
                break

        if not args.quiet:
            size = shutil.get_terminal_size()
            self.bt_write("\x1B[{y}H".format(y=size.lines).encode())
            bt.print()
            bt.print("Press ⌃C ⇧Z ⇧Q or ⌃C : Q ! Return to quit")

    #
    # Define enough Keystrokes to bootstrap Vi - enough for ⇧Z ⇧K and ⇧Z ⇧S
    #

    def form_ZK_ZS_bot_by_lines(self):
        """Say which Code runs in reply to which Key Sequences"""

        bot_by_lines = dict()

        # Define some Keystroke Sequences

        bot_by_lines[b"\x03"] = self.read_more  # Vi ⌃C
        bot_by_lines[b"\x03:q!\r"] = self.quit_bang
        bot_by_lines[b"\x03ZQ"] = self.quit_bang

        bot_by_lines[b":q!\r"] = self.quit_bang  # Vi : Q ! Return

        bot_by_lines[b"ZK"] = self.try_keyboard  # Vi ⇧Z ⇧K
        bot_by_lines[b"ZQ"] = self.quit_bang  # Vi ⇧Z ⇧Q
        bot_by_lines[b"ZS"] = self.try_screen  # Vi ⇧Z ⇧S

        # Mark some Keystroke Sequences as incomplete

        bot_by_lines[b":"] = self.read_more
        bot_by_lines[b":q"] = self.read_more
        bot_by_lines[b":q!"] = self.read_more

        bot_by_lines[b"Z"] = self.read_more

        # Succeed

        return bot_by_lines

    def quit_bang(self):  # ⇧Z ⇧Q  # : Q !
        """Quit when told"""

        sys.exit()

    def write_bel(self):
        """Freak over almost any tupo"""

        self.bt_write(b"\x07")

    def read_more(self):
        """Take another Byte before choosing a reply"""

        assert control(b"C") == b"\x03"

        line = self.readline()

        if self.lines == b"\x03":
            if line == b"\x03":
                self.write_bel()
            self.lines = b""

        self.lines += line
        self.runlines()

    #
    # Define the Keystrokes of a Vi for Files as small as the Screen
    #

    def form_bot_by_lines(self):
        """Say which Code runs in reply to which Key Sequences"""

        bot_by_lines = self.form_ZK_ZS_bot_by_lines()

        assert b"\a" == b"\x07"
        assert b"\r" == b"\x0D"

        assert control(b"N") == b"\x0E"
        assert control(b"P") == b"\x10"

        assert MouseSgrReportPattern == b"\x1B\\[<([0-9]+);([0-9]+);([0-9]+)([Mm])"
        assert PasteOpenPattern == b"\x1B\\[200~"

        # Define some Keystroke Sequences

        bot_by_lines[b"\x07"] = self.send_for_cpr  # Vi ⌃G
        bot_by_lines[b"\x0D"] = self.to_row_down  # Vi ⌃M  # Vi Return
        bot_by_lines[b"\x0E"] = self.to_row_down  # Vi ⌃N
        bot_by_lines[b"\x10"] = self.to_row_up  # Vi ⌃P

        bot_by_lines[b"\x1B[200~"] = self.got_paste_report  # till CSI 201 ~
        bot_by_lines[b"\x1B[<"] = self.got_mouse_report  # CSI < ... M, or ... m

        bot_by_lines[b"\x1B[A"] = self.to_row_up
        bot_by_lines[b"\x1B[B"] = self.to_row_down
        bot_by_lines[b"\x1B[C"] = self.to_column_right
        bot_by_lines[b"\x1B[D"] = self.to_column_left

        bot_by_lines[b" "] = self.to_char_next  # Vi Space
        bot_by_lines[b"$"] = self.to_column_beyond  # Vi ⇧4  # Vi $
        bot_by_lines[b"+"] = self.to_dent_down  # Vi ⇧=  # Vi +
        bot_by_lines[b"-"] = self.to_dent_up  # Vi -

        bot_by_lines[b"0"] = self.to_column_leftmost  # Vi 0

        bot_by_lines[b"G"] = self.to_dent_last  # Vi ⇧G
        bot_by_lines[b"H"] = self.to_dent_first  # Vi ⇧H
        bot_by_lines[b"L"] = self.to_dent_last  # Vi ⇧L
        bot_by_lines[b"M"] = self.to_dent_middle  # Vi ⇧M

        bot_by_lines[b"^"] = self.to_dent_left  # Vi ⇧6  # Vi ^
        bot_by_lines[b"_"] = self.to_dent_here_down  # Vi ⇧- # Vi _

        bot_by_lines[b"h"] = self.to_column_left  # Vi H
        bot_by_lines[b"j"] = self.to_row_down  # Vi J
        bot_by_lines[b"k"] = self.to_row_up  # Vi K
        bot_by_lines[b"l"] = self.to_column_right  # Vi L

        bot_by_lines[b"|"] = self.to_column_chosen  # Vi ⇧\ |

        # Mark some Keystroke Sequences as incomplete

        bot_by_lines[b"\x1B"] = self.read_more
        bot_by_lines[b"\x1B["] = self.read_more

        # Succeed

        return bot_by_lines

    def send_for_cpr(self):  # Vi ⌃G
        """Tell Terminal Keyboard to send Cursor Position Report (CPR)"""

        # Send DSR for CPR

        assert DeviceStatusReport == b"\x1B[6n"
        self.bt_write(b"\x1B[6n")

        if False:  # jitter Sun 16/Apr
            self.try_keyboard()
            self.bt_write(b"\x1B[6n")

        # Receive CPR

        assert CursorPositionForm == b"\x1B[{y};{x}H"  # y=1, x=1
        assert CursorPositionReportPattern == b"\x1B\\[([0-9]+);([0-9]+)R"
        assert EraseInLineForm == b"\x1B[{ps}K"  # ps=0
        assert LowerLeftForm == b"\x1B[{y}H"  # y=1

        line = self.readline()

        m = re.match(b"^\x1B\\[([0-9]+);([0-9]+)R$", string=line)
        if not m:
            size = shutil.get_terminal_size()
            self.bt_write("\x1B[{y}H".format(y=size.lines).encode())
            self.bt_write("\x1B[{ps}K".format(ps="").encode())
            self.bt.print(line)

            self.write_bel()

            return

        y = int(m.group(1))
        x = int(m.group(2))

        size = shutil.get_terminal_size()
        status_chars = '"/dev/tty" [Modified] {} lines {} columns  {},{}'.format(
            size.lines, size.columns, y, x
        )

        self.bt_write("\x1B[{y}H".format(y=size.lines).encode())
        self.bt_write("\x1B[{ps}K".format(ps="").encode())
        self.bt_write(status_chars.encode())

        self.bt_write("\x1B[{y};{x}H".format(y=y, x=x).encode())

    def got_paste_report(self):  # OCPBR
        """React to Paste"""

        assert PasteClosePattern == b"\x1B\\[201~"

        lines = b""
        while True:  # todo: time out to break free without PasteClosePattern
            line = self.readline()
            if line == b"\x1B[201~":
                break
            lines += line

        self.lines = lines
        self.runlines()

    def got_mouse_report(self):  # MPR
        """React to Press or Release of the Terminal Mouse"""

        line = self.line

        assert CursorPositionForm == b"\x1B[{y};{x}H"  # y=1, x=1
        assert MouseSgrReportPattern == b"\x1B\\[<([0-9]+);([0-9]+);([0-9]+)([Mm])"
        assert MouseSgrPress == b"M"
        assert MouseSgrRelease == b"m"

        m = re.match(b"\x1B\\[<([0-9]+);([0-9]+);([0-9]+)([Mm])", string=line)
        if not m:
            self.write_bel()
            return

        pb = int(m.group(1))
        px = int(m.group(2))
        py = int(m.group(3))

        pc = m.group(4)
        assert pc in b"Mm"

        mask = pb
        if pb & 0x10:  # ⌃ Control
            mask = mask & ~0x10
        if pb & 0x8:  # ⌥ Option
            mask = mask & ~0x8
        if pb & 0x4:  # ⇧ Shift
            mask = mask & ~0x4

        self.bt_write("\x1B[{y};{x}H".format(y=py, x=px).encode())

        if mask:
            self.write_bel()
            return

    #
    # Move the Cursor relatively
    #

    def to_char_next(self):  # Vi Space, but past Last Char and stops before next Row
        """Cursor Move Next"""

        assert CursorForwardForm == b"\x1B[{x}C"  # x=1
        self.bt_write("\x1B[{x}C".format(x="").encode())

    def to_column_left(self):  # Vi H
        """Cursor Move Left"""

        assert BS == b"\b"
        assert CursorBackwardForm == b"\x1B[{x}D"  # x=1
        self.bt_write(b"\b")

    def to_column_right(self):  # Vi L, but goes past last Char in Row
        """Cursor Move Right"""

        assert CursorForwardForm == b"\x1B[{x}C"  # x=1
        self.bt_write("\x1B[{x}C".format(x="").encode())

    def to_row_down(self):  # Vi J  # Vi ⌃N
        """Cursor Move Down"""

        assert CursorDownForm == b"\x1B[{y}B"  # y=1
        self.bt_write("\x1B[{y}B".format(y="").encode())

    def to_row_up(self):  # Vi K  # Vi ⌃P
        """Cursor Move Up"""

        assert CursorUpForm == b"\x1B[{y}A"  # y=1
        self.bt_write("\x1B[{y}A".format(y="").encode())

    #
    # Move the Cursor absolutely
    #

    def to_column_leftmost(self):  # Vi 0
        """Cursor Move to first Column of Row"""

        assert CR == b"\r"
        self.bt_write(b"\r")

    def to_column_chosen(self):  # Vi ⇧\  # Vi |
        """Cursor Move to chosen Column of Row"""

        assert CursorCharAbsoluteForm == b"\x1B[{x}G"  # x=1
        self.bt_write("\x1B[{x}G".format(x="").encode())

    def to_column_beyond(self):  # Vi ⇧4  # Vi $  # but past last Char in Row
        """Cursor Move to last Column of Row"""

        assert CursorCharAbsoluteForm == b"\x1B[{x}G"  # x=1

        size = shutil.get_terminal_size()
        reply = "\x1B[{x}G".format(x=size.columns).encode()
        self.bt_write(reply)

    def to_dent_down(self):  # Vi ⇧=  # Vi +  # but left of Dent
        """Cursor Move to first Column of Row and Down"""

        assert CR == b"\r"
        assert CursorDownForm == b"\x1B[{y}B"  # y=1

        self.bt_write(b"\r")
        self.bt_write("\x1B[{y}B".format(y="").encode())

    def to_dent_here_down(self):  # Vi ⇧-  # Vi _  # but left of Dent
        """Cursor Move to first Column of Row"""

        assert CR == b"\r"
        self.bt_write(b"\r")

    def to_dent_first(self):  # Vi ⇧H  # but same Column, not right of Dent
        """Cursor Move to first Row of Screen"""

        assert LinePositionAbsoluteForm == b"\x1B[{y}d"  # y=1
        self.bt_write("\x1B[{y}d".format(y="").encode())

    def to_dent_left(self):  # Vi ⇧6  # Vi ^  # but left of Dent
        """Cursor Move to first Column of Row"""

        assert CR == b"\r"
        self.bt_write(b"\r")

    def to_dent_middle(self):  # Vi ⇧M  # but same Column, not right of Dent
        """Cursor Move to middle Row of Screen"""

        assert LinePositionAbsoluteForm == b"\x1B[{y}d"  # y=1

        size = shutil.get_terminal_size()
        reply = "\x1B[{y}d".format(y=(size.lines // 2)).encode()
        self.bt_write(reply)

    def to_dent_last(self):  # Vi ⇧L  # but same Column, not right of Dent
        """Cursor Move to last Row of Screen"""

        assert LinePositionAbsoluteForm == b"\x1B[{y}d"  # y=1

        size = shutil.get_terminal_size()
        reply = "\x1B[{y}d".format(y=size.lines).encode()
        self.bt_write(reply)

        # Vi ⇧G  # but same Column, not right of Dent, and not below Screen

    def to_dent_up(self):  # Vi -  # but left of Dent
        """Cursor Move Up"""

        assert CursorUpForm == b"\x1B[{y}A"  # y=1
        self.bt_write(b"\x1B[A")


class ByteTerminal:
    r"""Start/ Stop line-buffering Input and replacing \n Output with \r\n"""

    def __init__(self, stdio):
        self.stdio = stdio

        self.fd = stdio.fileno()
        self.line = bytearray()
        self.tcgetattr = None

        self.try_me()

    def try_me(self):
        """Run a quick self-test"""

        self.write(b"")  # tests 'os.write'
        self.kbhit(0)  # tests 'select.select'

    def __enter__(self):
        r"""Stop line-buffering Input and stop replacing \n Output with \r\n"""

        fd = self.fd

        tcgetattr = self.tcgetattr
        if tcgetattr is None:
            tcgetattr = termios.tcgetattr(fd)

            self.tcgetattr = tcgetattr

            tty.setraw(fd, when=termios.TCSADRAIN)  # Drain flushes Output, then changes
            # termios.TCSAFLUSH  # Flush destroys Input, flushes Output, then changes

        return self

    def __exit__(self, *exc_info):
        r"""Start line-buffering Input and start replacing \n Output with \r\n"""

        fd = self.fd

        tcgetattr = self.tcgetattr
        if tcgetattr is not None:
            self.tcgetattr = None

            when = termios.TCSADRAIN
            termios.tcsetattr(fd, when, tcgetattr)

    def print(self, *args, **kwargs):
        """Work like Print, but end with '\r\n', not with '\n'"""

        alt_kwargs = dict(kwargs)
        if ("end" not in kwargs) or (kwargs["end"] is None):
            alt_kwargs["end"] = "\r\n"

        print(*args, **alt_kwargs)

    def write(self, line):
        """Write some Bytes without encoding or ending them"""

        fd = self.fd

        os.write(fd, line)

    def readline(self):
        """Read the next Keystroke or Paste from Keyboard"""

        fd = self.fd
        line = self.line

        # Pop the next Keystroke or Paste

        while True:
            (stroke, lookahead) = bytes_splitstroke(line)
            if stroke:
                line[::] = lookahead
                return stroke

            # Else read more Bytes

            length = 1022  # Paste came as 1022 Bytes per 100ms, at 2023-03 macOS
            read = os.read(fd, length)
            line.extend(read)

        # tests of many ⌘V ⌘V Paste Strokes do sometimes read more than one together

    def kbhit(self, timeout):  # 'timeout' in seconds
        """Wait till next Keyboard Byte struck or pasted, or Timeout"""

        rlist = [self.stdio]
        wlist = list()
        xlist = list()

        (rlist_, _, _) = select.select(rlist, wlist, xlist, timeout)

        return rlist_  # empty after Timeout, else clone of  'rlist'

    def breakpoint(self):
        """Breakpoint with line-buffered Input and "\r\n" Line-End's"""

        self.__exit__(*sys.exc_info())
        breakpoint()
        self.__enter__()


def bytes_splitstroke(line):
    """Split off the first Keystroke or Paste"""

    assert Esc == b"\x1B"
    assert CSI == b"\x1B["
    assert MouseSixByteReportPattern == b"\x1B\\[M..."

    # Take anything but Esc

    if not line.startswith(b"\x1B"):  # Esc
        stroke = line.partition(b"\x1B")[0]
    elif line.startswith(b"\x1B"):  # Esc
        stroke = b""

        # Take a MouseSixByteReportPattern from b"\x1B[M" and more

        if line.startswith(b"\x1B[M"):  # CSI
            m = re.match(MouseSixByteReportPattern, line)  # todo: testme
            if m:
                stroke = line

        # Take CSI plus Unsigned Decimal Ints split or marked by ";", "<", and "?"

        elif line.startswith(b"\x1B["):
            for index in range(2, len(line)):
                end = line[index:][:1]
                csi_middles = b"0123456789;<?"
                if end not in csi_middles:  # solves many Ps of Pm, but not Pt
                    stroke = line[: (index + 1)]  # may contain leading zeroes
                    break

    # Split out the leading Stroke

    stroke = bytes(stroke)
    lookahead = line[len(stroke) :]

    assert (stroke + lookahead) == line, (stroke, lookahead, line)

    # Succeed

    return (stroke, lookahead)


#
# Name Cheat Codes of the Vi Easter Egg buried in the Terminal
#
#   https://en.wikipedia.org/wiki/ANSI_escape_code
#   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
#


BS = b"\b"  # Backspace  # BS
CR = b"\r"  # Carriage Return   # CR
Esc = b"\x1B"  # Escape  # ESC

CSI = b"\x1B["  # Control Sequence Introducer  # CSI

DeviceStatusReport = b"\x1B[6n"  # CSI Ps n  # DSR  # Ps = 6  # Send for CPR

BracketedPasteEnter = b"\x1B[?2004h"  # CSI ? Pm h  # Ps = 2 0 0 4  # DECSET
BracketedPasteExit = b"\x1B[?2004l"  # CSI ? Pm l  # Ps = 2 0 0 4  # DECRST

MouseEnter = b"\x1B[?1000h"  # CSI ? Pm h  # Ps = 1 0 0 0  # DECSET
MouseSgrUp = b"\x1B[?1006h"  # CSI ? Pm h  # Ps = 1 0 0 6  # DECSET
MouseSgrDown = b"\x1B[?1006l"  # CSI ? Pm h  # Ps = 1 0 0 6  # DECRST
MouseExit = b"\x1B[?1000l"  # CSI ? Pm h  # Ps = 1 0 0 0  # DECRST


CursorPositionForm = b"\x1B[{y};{x}H"  # CSI Ps ; Ps H  # CursorPosition CUP  # y=1,x=1

UpperLeft = b"\x1BH"  # the 4 variations on CPR of (), (y), (y,x), (x)
LowerLeftForm = b"\x1B[{y}H"  # y=1
LowerRightForm = b"\x1B[{y};{x}H"  # y=1,x=1
UpperRightForm = b"\x1B[;{x}H"  # x=1

CursorUpForm = b"\x1B[{y}A"  # CSI Ps A  # Cursor Up CUU  # y=1
CursorDownForm = b"\x1B[{y}B"  # CSI Ps B  # Cursor Down CUD  # y=1
CursorForwardForm = b"\x1B[{x}C"  # CSI Ps C  # Cursor Forward CUF  # x=1
CursorBackwardForm = b"\x1B[{x}D"  # CSI Ps D  # Cursor Backward CUB  # x=1

CursorCharAbsoluteForm = b"\x1B[{x}G"  # y=1
LinePositionAbsoluteForm = b"\x1B[{y}d"  # y=1

EraseInLineForm = b"\x1B[{ps}K"  # CSI Ps K  # EL  # Ps = 0  # Erase to Right  # ps=0


CursorPositionReportPattern = b"\x1B\\[([0-9]+);([0-9]+)R"  # CSI r ; c R  # CPR Y X
# CPR rarely indexed as CSI Pm R

PasteOpenPattern = b"\x1B\\[200~"  # Os Copy-Paste Buffer Report  # OCBR
PasteClosePattern = b"\x1B\\[201~"

MouseSixByteReportPattern = b"\x1B\\[M..."  # MPR X Y

MouseSgrPress = b"M"
MouseSgrRelease = b"m"
MouseSgrReportPattern = b"\x1B\\[<([0-9]+);([0-9]+);([0-9]+)([Mm])"  # MPR X Y
# CSI < Pm M  # py ; px ; pb  # MPR X Y  # indexed as:  a final character which is M
# CSI < Pm m  # py ; px ; pb  # MPR X Y  # indexed as:  and m  for


def control(bytes_):
    """Define 'control(b"C") == "\x03"' etc"""

    assert len(bytes_) == 1, bytes_
    assert bytes_[0] in range(0x3F, 0x60), bytes_[0]
    ctrl_bytes = struct.pack("B", bytes_[0] ^ 0x40)

    return ctrl_bytes


#
# Add some Def's to Import ArgParse
#


def compile_argdoc(drop_help=None):
    """Form an ArgumentParser from the Main Doc, without Positional Args and Options"""

    argdoc = __main__.__doc__

    # Compile much of the Arg Doc to Args of 'argparse.ArgumentParser'

    doc_lines = argdoc.strip().splitlines()
    prog = doc_lines[0].split()[1]  # first word of first line

    doc_firstlines = list(_ for _ in doc_lines if _ and (_ == _.lstrip()))
    description = doc_firstlines[1]  # first line of second paragraph

    add_help = not drop_help

    # Pick the Epilog out of the Doc

    epilog = None
    for index, line in enumerate(doc_lines):
        strip = line.rstrip()

        skip = False
        skip = skip or not strip
        skip = skip or strip.startswith(" ")
        skip = skip or strip.startswith("usage")
        skip = skip or strip.startswith(description.rstrip())
        skip = skip or strip.startswith("positional arguments")
        skip = skip or strip.startswith("options")
        if skip:
            continue

        epilog = "\n".join(doc_lines[index:])

        break

    # Form an ArgumentParser, without Positional Args and Options

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=add_help,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    return parser


def parser_parse_args(parser):
    """Parse the Sh Args, even when no Sh Args coded as the one Sh Arg '--'"""

    sys_exit_if_argdoc_ne(parser)  # prints diff and exits nonzero, when Arg Doc wrong

    sh_args = sys.argv[1:]
    if sh_args == ["--"]:  # needed by ArgParse when no Positional Args
        sh_args = ""

    args = parser.parse_args(sh_args)  # prints helps and exits, else returns args

    sys_exit_if_testdoc(parser.epilog)  # prints examples & exits if no args

    return args


def sys_exit_if_argdoc_ne(parser):
    """Print Diff and exit nonzero, unless Arg Doc equals Parser Format_Help"""

    # Fetch the Main Doc, and note where from

    main_doc = __main__.__doc__.strip()
    main_filename = os.path.split(__file__)[-1]
    got_filename = "./{} --help".format(main_filename)

    # Fetch the Parser Doc from a fitting virtual Terminal
    # Fetch from a Black Terminal of 89 columns, not current Terminal width
    # Fetch from later Python of "options:", not earlier Python of "optional arguments:"

    with_columns = os.getenv("COLUMNS")
    os.environ["COLUMNS"] = str(89)
    try:
        parser_doc = parser.format_help()

    finally:
        if with_columns is None:
            os.environ.pop("COLUMNS")
        else:
            os.environ["COLUMNS"] = with_columns

    parser_doc = parser_doc.replace("optional arguments:", "options:")

    parser_filename = "ArgumentParser(...)"
    want_filename = parser_filename

    # Print the Diff to Parser Doc from Main Doc and exit, if Diff exists

    got_doc = main_doc
    want_doc = parser_doc

    diffs = list(
        difflib.unified_diff(
            a=got_doc.splitlines(),
            b=want_doc.splitlines(),
            fromfile=got_filename,
            tofile=want_filename,
            lineterm="",  # else the '---' '+++' '@@' Diff Control Lines end with '\n'
        )
    )

    if diffs:
        print("\n".join(diffs))

        sys.exit(2)  # trust caller to log SystemExit exceptions well

    # https://github.com/python/cpython/issues/53903  <= options: / optional arguments:
    # https://bugs.python.org/issue38438  <= usage: [WORD ... ] / [WORD [WORD ...]]

    # todo: tag the 'a=' 'b=' such that 'git apply -v' fixes the failure


#
# Add some Def's to Import Sys
#


def sys_exit_if_testdoc(epilog):
    """Print examples and exit, if no Sh Args"""

    if sys.argv[1:]:
        return

    lines = epilog.splitlines()
    indices = list(_ for _ in range(len(lines)) if lines[_])
    indices = list(_ for _ in range(len(lines)) if not lines[_].startswith(" "))
    testdoc = "\n".join(lines[indices[-1] + 1 :])
    testdoc = textwrap.dedent(testdoc)

    print()
    print(testdoc)
    print()

    sys.exit(0)


#
# Sketch future work
#


# todo: take Vi 1234567890 Keystrokes as digits of repeat
# todo: take changes from Vi ⇧C ⇧D ⇧I ⇧O ⇧R ⇧S ⇧X  a c d i o r s x
# todo: repeat changes at Vi .


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/vi.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
