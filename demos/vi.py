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
  logs Key Chords, Paste, and Milliseconds Delays when told ⇧Z ⇧K, until ⌃C
  copies exactly when told ⇧Z ⇧S, until ⌃C
  edits classic Vi output, when run inside:  vi +':set t_ti= t_te='

examples:
  ./demos/vi.py --  # talks Cheat Codes to the Vi Easter Egg buried in the Terminal
  ./demos/vi.py -q  # doesn't write Escape Sequences at entry/ exit
  ls -CR && ./demos/vi.py --  # fills Screen with Text and then edits it
  cat ./demos/vi.py |dd bs=1 count=10123 |tr '[ -~]' '.' |pbcopy  # makes large Paste
"""

# "⌃" == "\u2303" == "\N{Up Arrowhead}" for the Control Key
# "⌥" == "\u2325" == "\N{Option Key}" for the Option Key
# "⇧" == "\u21E7" == "\N{Upwards White Arrow}" for the Shift Key
# "⌘" == "\u2318" == "\N{Place of Interest Sign}" for the Command Key


# code reviewed by people, and by Black and Flake8


import __main__
import argparse
import datetime as dt
import difflib
import os
import re
import select
import shutil
import string
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
    with ViTerminal(stdio) as vt:
        vt.try_vi()


def parse_vi_py_args():
    """Parse the Args from the Sh command line"""

    parser = compile_argdoc()
    parser.add_argument("-q", "--quiet", dest="q", action="count", help="say less")
    args = parser_parse_args(parser)  # prints help and exits zero, when asked
    args.quiet = args.q if args.q else 0

    return args


class ViTerminal:
    """Take Bytes from the Keyboard as Commands to edit the Screen"""

    def __init__(self, stdio):
        self.ct = CharTerminal(stdio)

        self.splits = list()
        self.bot_by_chars = self.form_bot_by_chars()

    def __enter__(self):
        """FIXME"""

        args = main.args

        ct = self.ct
        ct.__enter__()

        if not args.quiet:
            self.greet()

        return self

    def __exit__(self, *exc_info):
        """FIXME"""

        ct = self.ct
        if ct.__exit__():
            return True

    def greet(self):
        """Prompt the Operator"""

        bt = self.ct.bt

        bt.print()
        bt.print("Press ⌃C ⇧Z ⇧K to log Key Chords and Paste, ⌃C to stop")
        bt.print("Press ⌃C ⇧Z ⇧S to copy Bytes to Screen from Keyboard, ⌃C to stop")
        bt.print("Press ⌃C ⇧Z ⇧Q or ⌃C : Q ! Return to quit")

        # "⌃" == "\u2303" == "\N{Up Arrowhead}" for the Control Key
        # "⇧" == "\u21E7" == "\N{Upwards White Arrow}" for the Shift Key

    def write_bel(self):
        """Freak over almost any tupo"""

        self.bt_write(b"\x07")

    def bt_write(self, line):
        """Write Bytes out through 'self.bt' Byte Terminal"""

        fd = self.ct.bt.fd
        os.write(fd, line)

    #
    # Name some Loops
    #

    def try_keyboard(self):  # ⇧Z ⇧K
        """Log Key Chords, Paste, & Delays from Keyboard, till told to quit"""

        args = main.args

        ct = self.ct
        bt = self.ct.bt

        assert LowerLeftForm == b"\x1B[{y}H"  # y=1

        ByteTerminal.readline.verbose = True

        if not args.quiet:
            bt.print("Press ⌃C to stop logging Key Chords and Paste")

        while True:
            bt.print()
            line = ct.readline()
            ct.logline()
            bt.print("try_keyboard", repr(line))

            if line == "⌃C":
                break

        ByteTerminal.readline.verbose = False

        if not args.quiet:
            size = shutil.get_terminal_size()
            self.bt_write("\x1B[{y}H".format(y=size.lines).encode())
            bt.print()
            bt.print("Press ⌃C ⇧Z ⇧Q or ⌃C : Q ! Return to quit")

    def try_screen(self):  # ⇧Z ⇧S
        """Copy Key Chords and Paste to Screen, till told to quit"""

        args = main.args

        bt = self.ct.bt

        assert control(b"C") == b"\x03"
        assert LowerLeftForm == b"\x1B[{y}H"  # y=1

        if not args.quiet:
            bt.print("Press ⌃C to stop copying Key Chords and Paste to Screen")

        while True:
            line = bt.readline()
            bt.write(line)

            if line == b"\x03":
                break

        if not args.quiet:
            size = shutil.get_terminal_size()
            self.bt_write("\x1B[{y}H".format(y=size.lines).encode())
            bt.print()
            bt.print("Press ⌃C ⇧Z ⇧Q or ⌃C : Q ! Return to quit")

    def try_vi(self):  # ⌃C
        """Take Bytes from the Keyboard as Commands to edit the Screen"""

        while True:
            bot = self.readbot()
            bot()

    #
    # Define the Key Chords of a Vi for Files as small as the Screen
    #

    def form_bot_by_chars(self):
        """Say which Code runs in reply to which Key Sequences"""

        bot_by_chars = dict()

        bot_by_chars[": Q ! Return"] = self.quit_bang  # Vi : Q ! Return

        bot_by_chars["⇧Z ⇧K"] = self.try_keyboard  # Vi ⇧Z ⇧K
        bot_by_chars["⇧Z ⇧Q"] = self.quit_bang  # Vi ⇧Z ⇧Q
        bot_by_chars["⇧Z ⇧S"] = self.try_screen  # Vi ⇧Z ⇧S

        assert MouseSgrReportPattern == b"\x1B\\[<([0-9]+);([0-9]+);([0-9]+)([Mm])"
        assert PasteOpenPattern == b"\x1B\\[200~"

        # Define some Key Chord Sequences

        bot_by_chars["⌃G"] = self.send_for_cpr  # Vi ⌃G
        bot_by_chars["Return"] = self.to_row_down  # Vi ⌃M  # Vi Return
        bot_by_chars["⌃N"] = self.to_row_down  # Vi ⌃N
        bot_by_chars["⌃P"] = self.to_row_up  # Vi ⌃P

        bot_by_chars["\x1B[200~"] = self.got_paste_report  # till CSI 201 ~
        bot_by_chars["\x1B[<"] = self.got_mouse_report  # CSI < ... M, or ... m

        bot_by_chars["↑"] = self.to_row_up
        bot_by_chars["↓"] = self.to_row_down
        bot_by_chars["→"] = self.to_column_right
        bot_by_chars["←"] = self.to_column_left

        bot_by_chars[" "] = self.to_char_next  # Vi Space
        bot_by_chars["$"] = self.to_column_beyond  # Vi ⇧4  # Vi $
        bot_by_chars["+"] = self.to_dent_down  # Vi ⇧=  # Vi +
        bot_by_chars["-"] = self.to_dent_up  # Vi -

        bot_by_chars["0"] = self.to_column_leftmost  # Vi 0

        bot_by_chars["⇧G"] = self.to_dent_last  # Vi ⇧G
        bot_by_chars["⇧H"] = self.to_dent_first  # Vi ⇧H
        bot_by_chars["⇧L"] = self.to_dent_last  # Vi ⇧L
        bot_by_chars["⇧M"] = self.to_dent_middle  # Vi ⇧M

        bot_by_chars["^"] = self.to_dent_left  # Vi ⇧6  # Vi ^
        bot_by_chars["_"] = self.to_dent_here_down  # Vi ⇧- # Vi _

        bot_by_chars["H"] = self.to_column_left  # Vi H
        bot_by_chars["J"] = self.to_row_down  # Vi J
        bot_by_chars["K"] = self.to_row_up  # Vi K
        bot_by_chars["L"] = self.to_column_right  # Vi L

        bot_by_chars["|"] = self.to_column_chosen  # Vi ⇧\ |

        # Succeed

        return bot_by_chars

    #
    #
    #

    def quit_bang(self):  # ⇧Z ⇧Q  # : Q !
        """Quit when told"""

        sys.exit()

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
    # Move the Cursor to the Left Margin of some nearby Row
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

    #
    #
    #

    def readbot(self):
        """Read the next Bot to run"""

        ct = self.ct
        splits = self.splits

        # Split out the next Key Chords or Paste

        while True:
            (bot, more) = self.splits_splitbot(splits)
            if bot:
                splits[::] = more

                return bot

            # Else read more Bytes

            line = ct.readline()
            splits.extend(line.split())

    def splits_splitbot(self, splits):
        """Split out the Bot of the first Key Chords"""

        bot_by_chars = self.bot_by_chars

        join = " ".join(splits)
        alt_matches = list(
            _ for _ in bot_by_chars.keys() if (_.startswith(join) or join.startswith(_))
        )

        matches = alt_matches
        if len(alt_matches) == 1:
            match = alt_matches[-1]
            if splits != match.split():
                matches = [None, None]

        if not matches:
            bot = self.write_bel
            keys = splits[:1]
        elif len(matches) == 1:
            key = matches[-1]
            bot = bot_by_chars[key]
            keys = [key]
        else:
            bot = None
            keys = list()

        more = splits[len(keys) :]

        return (bot, more)


#
# Bypass the Line Buffer, in speaking with the Screen and Keyboard of the Terminal
#


class CharTerminal:
    r"""Take Bytes from the Keyboard as Chars"""

    def __init__(self, stdio):
        self.bt = ByteTerminal(stdio)

        t0 = dt.datetime.now()

        self.t0 = t0
        self.t1 = t0
        self.line = b""

        self.lines = bytearray()

    def __enter__(self):
        """Start intercepting Mouse Strokes and Paste Strokes"""

        bt = self.bt

        assert BracketedPasteEnter == b"\x1B[?2004h"
        assert MouseEnter == b"\x1B[?1000h"
        assert MouseSgrUp == b"\x1B[?1006h"

        bt.__enter__()

        bt.write(b"\x1B[?1000h")
        bt.write(b"\x1B[?1006h")
        bt.write(b"\x1B[?2004h")

        return self

    def __exit__(self, *exc_info):
        """Stop intercepting Mouse Strokes and Paste Strokes"""

        bt = self.bt

        assert BracketedPasteExit == b"\x1B[?2004l"
        assert MouseExit == b"\x1B[?1000l"
        assert MouseSgrDown == b"\x1B[?1006l"

        assert LowerLeftForm == b"\x1B[{y}H"  # y=1

        if bt.__exit__():
            return True

        size = shutil.get_terminal_size()

        bt.write(b"\x1B[?2004l")
        bt.write(b"\x1B[?1006l")
        bt.write(b"\x1B[?1000l")

        bt.write("\x1B[{y}H".format(y=size.lines).encode())

    def breakpoint(self):
        """Exit, breakpoint, and try to enter again"""

        bt = self.bt

        self.__exit__(*sys.exc_info())
        bt.breakpoint()
        self.__enter__()

    def readline(self):
        """Read the Chars of the next Key Chords or Paste from Keyboard"""

        bt = self.bt
        lines = self.lines

        # Split out the next Key Chords or Paste

        while True:
            (some, more) = self.bytes_splitchord(lines)
            if some:
                lines[::] = more

                return some

            # Else read more Bytes

            line = bt.readline()
            if line:
                self.t0 = self.t1
                self.t1 = dt.datetime.now()
                self.line = line

                # Continue

                lines.extend(line)

    def logline(self):
        """Log this Key Chords or Paste"""

        bt = self.bt

        t0 = self.t0
        t1 = self.t1
        line = self.line

        t1t0 = int((t1 - t0).total_seconds() * 1000)
        if len(str(line)) <= 75:
            formed = "{}ms {} {}".format(t1t0, len(line), line)
        else:
            formed = "{}ms {} {} ... {}".format(t1t0, len(line), line[:20], line[-20:])
        bt.print("logline", formed)

        # FIXME: uppercase the hex

    def bytes_splitchord(self, bytes_):
        """Split out the Chars of the first Key Chord encoded as Bytes"""

        chords_by_bytes = CHORDS_BY_BYTES

        matches = list(
            _
            for _ in chords_by_bytes.keys()
            if (_.startswith(bytes_) or bytes_.startswith(_))
        )

        if not matches:
            chords = bytes_.decode(errors="surrogateescape")
            some = chords[0]
            key = some.encode(errors="surrogateescape")
        elif len(matches) == 1:
            key = matches[-1]
            some = chords_by_bytes[key]
        else:
            some = ""
            key = b""

        more = bytes_[len(key) :]

        return (some, more)


#
# Name some Key Chords
#


Control = "\N{Up Arrowhead}"  # ⌃
Option = "\N{Option Key}"  # ⌥
Shift = "\N{Upwards White Arrow}"  # ⇧
Command = "\N{Place of Interest Sign}"  # ⌘


C0_CONTROLS = b"".join(chr(_).encode() for _ in list(range(0x20)) + [0x7F])

Esc = b"\x1B"  # Escape  # ESC


assert b"\xC2\xA0".decode() == "\u00A0" == "\N{No-Break Space}"


CHORDS_BY_BYTES = dict()

CHORDS_BY_BYTES[b"\0"] = "⌃Space"  # ⌃Space ⌃⌥Space ⌃⇧Space ⌃⇧2 ⌃⌥⇧2
CHORDS_BY_BYTES[b"\t"] = "Tab"  # ⌃I ⌃⌥I ⌃⌥⇧I Tab ⌃Tab ⌥Tab ⌃⌥Tab
CHORDS_BY_BYTES[b"\r"] = "Return"  # ⌃M ⌃⌥M ⌃⌥⇧M Return etc
CHORDS_BY_BYTES[b" "] = "Space"  # Space ⇧Space
CHORDS_BY_BYTES[b"\x1B[Z"] = "⇧Tab"  # ⇧Tab ⌃⇧Tab ⌥⇧Tab ⌃⌥⇧Tab
CHORDS_BY_BYTES[b"\xC2\xA0"] = "⌥Space"  # ⌥Space ⌥⇧Space

CHORDS_BY_BYTES[b"\x1B[A"] = "↑"  # ↑ ⌥↑ ⇧↑ ⌃⌥↑ ⌃⇧↑ ⌥⇧↑ ⌃⌥⇧↑  # macOS takes ⌃↑
CHORDS_BY_BYTES[b"\x1B[B"] = "↓"  # ↓ ⌥↓ ⇧↓ ⌃⌥↓ ⌃⇧↓ ⌥⇧↓ ⌃⌥⇧↓  # macOS takes ⌃↓
CHORDS_BY_BYTES[b"\x1B[C"] = "→"  # → ⌃⌥→ ⌃⇧→ ⌥⇧→ ⌃⌥⇧→  # macOS takes ⌃→
CHORDS_BY_BYTES[b"\x1Bf"] = "⌥→"
CHORDS_BY_BYTES[b"\x1B[1;2C"] = "⇧→"
CHORDS_BY_BYTES[b"\x1B[D"] = "←"  # ← ⌃⌥← ⌃⇧← ⌥⇧← ⌃⌥⇧←  # macOS takes ⌃←
CHORDS_BY_BYTES[b"\x1Bb"] = "⌥←"
CHORDS_BY_BYTES[b"\x1B[1;2D"] = "⇧←"

# ⌃M is also Return ⌃Return ⌥Return ⇧Return ⌃⌥Return ⌃⇧Return ⌥⇧Return ⌃⌥⇧Return


def add_us_ascii_into_chords_by_bytes():
    """Add a US Ascii Keyboard into Chars by Bytes"""

    chords_by_bytes = CHORDS_BY_BYTES

    # Decode Control Chords

    assert Control == "\N{Up Arrowhead}"  # ⌃

    for ord_ in C0_CONTROLS:
        char = chr(ord_)
        bytes_ = char.encode()
        if bytes_ not in chords_by_bytes.keys():
            if bytes_ != Esc:
                chords_by_bytes[bytes_] = Control + chr(ord_ ^ 0x40)

    # Decode Shift'ed and un-Shift'ed US Ascii Letters

    assert Shift == "\N{Upwards White Arrow}"  # ⇧

    for char in string.ascii_uppercase:
        bytes_ = char.encode()
        assert bytes_ not in chords_by_bytes.keys(), bytes_

        chords_by_bytes[bytes_] = Shift + char

    for char in string.ascii_lowercase:
        bytes_ = char.encode()
        assert bytes_ not in chords_by_bytes.keys(), bytes_

        chords_by_bytes[bytes_] = char.upper()

    # Decode all the US Ascii Bytes not decoded above

    for ord_ in range(0x80):
        char = chr(ord_)

        bytes_ = char.encode()
        if bytes_ not in chords_by_bytes.keys():
            if bytes_ != Esc:
                chords_by_bytes[bytes_] = char


add_us_ascii_into_chords_by_bytes()

assert b" " in CHORDS_BY_BYTES.keys()
assert ((" " not in _) for _ in CHORDS_BY_BYTES.values())


CHORDS_BY_BYTES.update(  # the Fn Key Caps at Mac
    {
        b"\x1B\x4F\x50": "F1",
        b"\x1B\x4F\x51": "F2",
        b"\x1B\x4F\x52": "F3",
        b"\x1B\x4F\x53": "F4",
        b"\x1B\x5B\x31\x35\x7E": "F5",
        b"\x1B\x5B\x31\x37\x7E": "F6",  # F6  # ⌥F1
        b"\x1B\x5B\x31\x38\x7E": "F7",  # F7  # ⌥F2
        b"\x1B\x5B\x31\x39\x7E": "F8",  # F8  # ⌥F3
        b"\x1B\x5B\x32\x30\x7E": "F9",  # F9  # ⌥F4
        b"\x1B\x5B\x32\x31\x7E": "F10",  # F10  # ⌥F5
        b"\x1B\x5B\x32\x33\x7E": "⌥F6",  # F11  # ⌥F6  # macOS takes F11
        b"\x1B\x5B\x32\x34\x7E": "F12",  # F12  # ⌥F7
        b"\x1B\x5B\x32\x35\x7E": "⇧F5",  # ⌥F8  # ⇧F5
        b"\x1B\x5B\x32\x36\x7E": "⇧F6",  # ⌥F9  # ⇧F6
        b"\x1B\x5B\x32\x38\x7E": "⇧F7",  # ⌥F10  # ⇧F7
        b"\x1B\x5B\x32\x39\x7E": "⇧F8",  # ⌥F11  # ⇧F8
        b"\x1B\x5B\x33\x31\x7E": "⇧F9",  # ⌥F12  # ⇧F9
        b"\x1B\x5B\x33\x32\x7E": "⇧F10",
        b"\x1B\x5B\x33\x33\x7E": "⇧F11",
        b"\x1B\x5B\x33\x34\x7E": "⇧F12",
    }
)

CHORDS_BY_BYTES.update(  # the Option Digit strokes at Mac
    {
        b"\xC2\xBA": "⌥0",
        b"\xC2\xA1": "⌥1",
        b"\xE2\x84\xA2": "⌥2",
        b"\xC2\xA3": "⌥3",
        b"\xC2\xA2": "⌥4",
        b"\xE2\x88\x9E": "⌥5",
        b"\xC2\xA7": "⌥6",
        b"\xC2\xB6": "⌥7",
        b"\xE2\x80\xA2": "⌥8",
        b"\xC2\xAA": "⌥9",
        b"\xE2\x80\x9A": "⌥⇧0",
        b"\xE2\x81\x84": "⌥⇧1",
        b"\xE2\x82\xAC": "⌥⇧2",
        b"\xE2\x80\xB9": "⌥⇧3",
        b"\xE2\x80\xBA": "⌥⇧4",
        b"\xEF\xAC\x81": "⌥⇧5",
        b"\xEF\xAC\x82": "⌥⇧6",
        b"\xE2\x80\xA1": "⌥⇧7",
        b"\xC2\xB0": "⌥⇧8",
        b"\xC2\xB7": "⌥⇧9",
    }
)

CHORDS_BY_BYTES.update(  # the Option Letter strokes at Mac
    {
        b"\xC3\xA5": "⌥A",
        b"\xE2\x88\xAB": "⌥B",
        b"\xC3\xA7": "⌥C",
        b"\xE2\x88\x82": "⌥D",  # ⌥E does not come after ⌥D
        b"\xC3\xA1": "⌥E A",
        b"\xC3\xA9": "⌥E E",
        b"\xC3\xAD": "⌥E I",
        b"\x6A\xCC\x81": "⌥E J",
        b"\xC3\xB3": "⌥E O",
        b"\xC3\xBA": "⌥E U",
        b"\xC6\x92": "⌥F",
        b"\xC2\xA9": "⌥G",
        b"\xCB\x99": "⌥H",  # ⌥I does not come after ⌥H
        b"\xC3\xA2": "⌥I A",
        b"\xC3\xAA": "⌥I E",
        b"\xC3\xAE": "⌥I I",
        b"\xC3\xB4": "⌥I O",
        b"\xC3\xBB": "⌥I U",
        b"\xE2\x88\x86": "⌥J",
        b"\xCB\x9A": "⌥K",
        b"\xC2\xAC": "⌥L",
        b"\xC2\xB5": "⌥M",  # ⌥N does not come after ⌥M
        b"\xC3\xA3": "⌥N A",
        b"\xC3\xB1": "⌥N N",
        b"\xC3\xB5": "⌥N O",
        b"\xC3\xB8": "⌥O",
        b"\xCF\x80": "⌥P",
        b"\xC5\x93": "⌥Q",
        b"\xC2\xAE": "⌥R",
        b"\xC3\x9F": "⌥S",
        b"\xE2\x80\xA0": "⌥T",  # ⌥U does not come after ⌥T
        b"\xC3\xA4": "⌥U A",
        b"\xC3\xAB": "⌥U E",
        b"\xC3\xAF": "⌥U I",
        b"\xC3\xB6": "⌥U O",
        b"\xC3\xBC": "⌥U U",
        b"\xC3\xBF": "⌥U Y",
        b"\xE2\x88\x9A": "⌥V",
        b"\xE2\x88\x91": "⌥W",
        b"\xE2\x89\x88": "⌥X",
        b"\xCE\xA9": "⌥Z",
        b"\xC3\x85": "⌥⇧A",
        b"\xC4\xB1": "⌥⇧B",
        b"\xC3\x87": "⌥⇧C",
        b"\xC3\x8E": "⌥⇧D",
        b"\xC2\xB4": "⌥⇧E",  # ⌥E  # ⌥⇧E  # ⌥⇧E Space
        b"\xC3\x8F": "⌥⇧F",
        b"\xCB\x9D": "⌥⇧G",
        b"\xC3\x93": "⌥⇧H",
        b"\xCB\x86": "⌥⇧I",  # ⌥I  # ⌥⇧I  # ⌥⇧I Space
        b"\xC3\x94": "⌥⇧J",
        b"\xEF\xA3\xBF": "⌥⇧K",
        b"\xC3\x92": "⌥⇧L",
        b"\xC3\x82": "⌥⇧M",
        b"\xCB\x9C": "⌥⇧N",  # ⌥N  # ⌥⇧N  # ⌥⇧N Space
        b"\xC3\x98": "⌥⇧O",
        b"\xE2\x88\x8F": "⌥⇧P",
        b"\xC5\x92": "⌥⇧Q",
        b"\xE2\x80\xB0": "⌥⇧R",
        b"\xC3\x8D": "⌥⇧S",
        b"\xCB\x87": "⌥⇧T",
        b"\xC2\xA8": "⌥⇧U",  # ⌥U  # ⌥⇧U  # ⌥⇧U Space
        b"\xE2\x97\x8A": "⌥⇧V",
        b"\xE2\x80\x9E": "⌥⇧W",
        b"\xCB\x9B": "⌥⇧X",
        b"\xC3\x81": "⌥⇧Y",
        b"\xC2\xB8": "⌥⇧Z",
        b"\xC3\xA0": "⌥`A",
        b"\xC3\xA8": "⌥`E",
        b"\xC3\xAC": "⌥`I",
        b"\xC3\xB2": "⌥`O",
        b"\xC3\xB9": "⌥`U",
    }
)

CHORDS_BY_BYTES.update(  # the Option Punctuation-Mark strokes at Mac
    {
        b"\xE2\x80\x93": "⌥-",
        b"\xE2\x89\xA0": "⌥=",
        b"\xE2\x80\x9C": "⌥[",
        b"\xE2\x80\x98": "⌥]",
        b"\xC2\xAB": "⌥\\",
        b"\xE2\x80\xA6": "⌥;",
        b"\xC3\xA6": "⌥'",
        b"\xE2\x89\xA4": "⌥,",
        b"\xE2\x89\xA5": "⌥.",
        b"\xC3\xB7": "⌥/",
        b"\xE2\x80\x94": "⌥-",
        b"\xC2\xB1": "⌥⇧=",
        b"\xE2\x80\x9D": "⌥⇧[",
        b"\xE2\x80\x99": "⌥⇧]",
        b"\xC2\xBB": "⌥⇧\\",
        b"\xC3\x9A": "⌥⇧;",
        b"\xC3\x86": "⌥⇧'",
        b"\xC2\xAF": "⌥⇧,",
        b"\xCB\x98": "⌥⇧.",
        b"\xC2\xBF": "⌥⇧/",
    }
)

# no Bytes come from macOS Keyboard at ⇧F1 ⇧F2 ⇧F3 ⇧F4 ⌃⌥F ⌃⇧F ⌥⇧F ⌃⌥⇧F


#
# Bypass the Line Buffer, in speaking with the Screen and Keyboard of the Terminal
#


class ByteTerminal:
    r"""Start/ Stop line-buffering Input and replacing \n Output with \r\n"""

    def __init__(self, stdio):
        self.stdio = stdio

        self.fd = stdio.fileno()
        self.lines = bytearray()
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

    def breakpoint(self):
        """Exit, breakpoint, and try to enter again"""

        self.__exit__(*sys.exc_info())
        breakpoint()
        self.__enter__()

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

    def kbhit(self, timeout):  # 'timeout' in seconds
        """Wait till next Keyboard Byte struck or pasted, or Timeout"""

        rlist = [self.stdio]
        wlist = list()
        xlist = list()

        (rlist_, _, _) = select.select(rlist, wlist, xlist, timeout)

        return rlist_  # empty after Timeout, else clone of  'rlist'

    def readline(self):
        """Read the Bytes of the next Key Chords or Paste from Keyboard"""

        fd = self.fd
        lines = self.lines
        verbose = self.readline.verbose if hasattr(self.readline, "verbose") else None

        # Split out the next Key Chords or Paste

        while True:
            (some, more) = self.bytes_splitbytes(lines)
            if some:
                lines[::] = more
                return some

            # Else read more Bytes

            length = 1022  # Paste came as 1022 Bytes per 100ms, at 2023-03 macOS
            line = os.read(fd, length)
            if verbose:
                self.print("readline", line)

            # Continue

            lines.extend(line)

        # tests of many ⌘V ⌘V Paste Strokes do sometimes read more than one together

    def bytes_splitbytes(self, bytes_):
        """Split out the Bytes of the first Key Chords or Paste"""

        assert Esc == b"\x1B"
        assert CSI == b"\x1B["
        assert MouseSixByteReportPattern == b"\x1B\\[M..."

        # Take anything but Esc

        if not bytes_.startswith(b"\x1B"):  # Esc
            some = bytes_.partition(b"\x1B")[0]
        elif bytes_.startswith(b"\x1B"):  # Esc
            some = b""

            # Take a MouseSixByteReportPattern from b"\x1B[M" and more

            if bytes_.startswith(b"\x1B[M"):  # CSI
                m = re.match(MouseSixByteReportPattern, bytes_)  # todo: testme
                if m:
                    some = bytes_

            # Take CSI plus Unsigned Decimal Ints split or marked by ";", "<", and "?"

            elif bytes_.startswith(b"\x1B["):
                for index in range(2, len(bytes_)):
                    end = bytes_[index:][:1]
                    csi_middles = b"0123456789;<?"
                    if end not in csi_middles:  # solves many Ps of Pm, but not Pt
                        some = bytes_[: (index + 1)]  # may contain leading zeroes
                        break

            # Take Esc plus whatever, even Esc Esc

            elif bytes_[1:]:
                some = bytes_[:2]

        # Split out the Bytes of the first Key Chords or Paste

        some = bytes(some)
        more = bytes_[len(some) :]

        assert (some + more) == bytes_, (some, more, bytes_)

        # Succeed

        return (some, more)


#
# Name Cheat Codes of the Vi Easter Egg buried in the Terminal
#
#   https://en.wikipedia.org/wiki/ANSI_escape_code
#   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
#


BS = b"\b"  # Backspace  # BS
CR = b"\r"  # Carriage Return   # CR
assert Esc == b"\x1B"  # Escape  # ESC

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

    # b"\x7F" == control(b"?"), b"?" == b"\x3F"
    # b"\x00" == control(b"@"), b"@" == b"\x40"
    # b"\x01" == control(b"A"), b"A" == b"\x41"
    # b"\x1A" == control(b"Z"), b"Z" == b"\x5A"
    # b"\x1F" == control(b"_"), b"_" == b"\x5F"


#
# Add some Def's to Import ArgParse
#


def compile_argdoc(drop_help=None):
    """Form an ArgumentParser from the ArgDoc, without Positional Args and Options"""

    argdoc = __main__.__doc__

    # Compile much of the Arg Doc to Args of 'argparse.ArgumentParser'

    doc_lines = argdoc.strip().splitlines()
    prog = doc_lines[0].split()[1]  # first word of first line

    doc_firstlines = list(_ for _ in doc_lines if _ and (_ == _.lstrip()))
    alt_description = doc_firstlines[1]  # first line of second paragraph

    add_help = not drop_help

    # Say when Doc Lines stand plainly outside of the Epilog

    def skippable(line):
        strip = line.rstrip()

        skip = not strip
        skip = skip or strip.startswith(" ")
        skip = skip or strip.startswith("usage")
        skip = skip or strip.startswith("positional arguments")
        skip = skip or strip.startswith("options")

        return skip

    default = "just do it"
    description = default if skippable(alt_description) else alt_description

    # Pick the Epilog out of the Doc

    epilog = None
    for index, line in enumerate(doc_lines):
        if skippable(line) or (line == description):
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


# todo: take Vi 1234567890 Key Chords as digits of repeat
# todo: take changes from Vi ⇧C ⇧D ⇧I ⇧O ⇧R ⇧S ⇧X  a c d i o r s x
# todo: repeat changes at Vi .


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/vi.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
