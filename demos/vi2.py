#!/usr/bin/env python3

r"""
usage: vi2.py [-h] [-q]

edit the Screen in reply to Keyboard Chord Sequences

options:
  -h, --help   show this help message and exit
  -q, --quiet  say less

quirks:
  quits when told ⌃C ⇧Z ⇧Q, or ⌃C : Q ! Return, or ⌃Q ⇧N Return
  restores replacement-mode at exit, unless run as -q

keystrokes:
  ⌃C ⌃G ⌃M ⌃N ⌃P Return Space
  $ + 0 ⇧G ⇧H ⇧K ⇧N ^ H J K L |

escape-sequences:
  ⎋[d line-position-absolute ⎋[G cursor-character-absolute
  ⎋[1m bold ⎋[31m red ⎋[32m green ⎋[34m blue ⎋[38;5;130m orange ⎋[m plain
  ⎋[4h insertion-mode ⎋[ 6q bar ⎋[4l replacement-mode ⎋[4 q skid ⎋[ q unstyled
  ⎋[L delete-line ⎋[M insert-line ⎋[P delete-character ⎋[@ insert-character
  ⎋[T scroll-up ⎋[S scroll-down

self-tests:
  ⇧Z ⇧T, 1 ⇧Z ⇧T, 2 ⇧Z ⇧T, etc

docs:
  https://unicode.org/charts/PDF/U0000.pdf
  https://unicode.org/charts/PDF/U0080.pdf
  https://en.wikipedia.org/wiki/ANSI_escape_code
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
  https://www.ecma-international.org/publications-and-standards/standards/ecma-48
    /wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf

large inputs:
  git show && ./demos/vi2.py --
  make p.py && vi +':set t_ti= t_te=' p.py && ./demos/vi2.py --
  git grep --color=always def |less -FIRX && ./demos/vi2.py --
  cat ./demos/vi2.py |dd bs=1 count=10123 |tr '[ -~]' '.' |pbcopy && ./demos/vi2.py --

examples:
  ./demos/vi2.py --
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
import string
import struct
import sys
import termios
import textwrap
import time
import tty

_ = time


#
# Run from the Sh Command Line
#


def main():
    """Run from the Sh Command Line"""

    args = parse_vi2_py_args()
    main.args = args

    stdio = sys.__stdout__  # '__stdout__' as per 'shutil.get_terminal_size'
    with BytesTerminal(stdio) as bt:
        ct = ChordsTerminal(bt)
        vt = ViTerminal(ct)

        try:
            vt.run_till_quit()
        finally:
            if not main.args.quiet:
                bt.write(b"\x1B[4l")  # CSI Ps 06/12  # 4 replacement-mode
                bt.write(b"\x1B[ q")  # CSI Ps SP 07/01  # unstyled cursor-style


def parse_vi2_py_args():
    """Parse the Args from the Sh Command Line"""

    parser = compile_argdoc()
    parser.add_argument("-q", "--quiet", dest="q", action="count", help="say less")

    args = parser_parse_args(parser)  # prints help and exits zero, when asked
    args.quiet = args.q if args.q else 0

    return args


#
# Loop Terminal Input back as Terminal Output
#


class ViTerminal:
    r"""Loop Terminal Input back as Terminal Output"""

    def __init__(self, ct):
        bt = ct.bt

        self.ct = ct
        self.bt = bt

    def run_till_quit(self):  # noqa  # C901 too complex  # todo
        """TODO"""

        ct = self.ct
        bt = self.bt

        old = None
        read = None

        prompted = None
        while True:
            if not prompted:
                prompted = True
                self.bt_write_if(b"\x1B[K")
                self.bt_print_if("Press ⇧Z⇧Q to quit, or ⇧Z⇧S, or ⇧Z⇧K, or ⌃C")

            bt.flush()

            if read and not isinstance(read, bytes):
                old = read

            read = ct.read()

            if (old, read) == ("⇧Z", "⇧K"):
                self.bt_print_if("⇧K")

                prompted = False
                self.bt_print_if("Press ⌃C to stop logging Millisecond Input Bytes")

                ckt = ChordsKeyboardTest(ct)
                ckt.run_till_quit()

                self.bt_print_if()  # todo: prompt to Quit at each Screen of Input?

                continue

            if (old, read) == ("⇧Z", "⇧Q"):
                self.bt_print_if("⇧Q")
                break

            if (old, read) == ("⇧Z", "⇧S"):
                self.bt_print_if("⇧S")

                prompted = False
                self.bt_print_if("Press ⌃C to stop looping Keyboard into Screen")

                cst = ChordsScreenTest(ct)
                cst.run_till_quit()

                size = os.get_terminal_size()
                if size.lines > 2:
                    y = size.lines - 2
                    self.bt_write_if("\x1B[{y}H".format(y=y).encode())

                self.bt_print_if()

                continue

            if old == "⇧Z":
                self.bt_print_if(read)
                bt.print("\a")
                read = None

                continue

            if read == "⇧Z":
                self.bt_print_if("⇧Z", end="")

                continue

            if read == "⌃C":
                self.bt_print_if("⌃C")

                continue

            self.bt_print_if(repr(read))
            bt.write(b"\a")

    def bt_print_if(self, *args, **kwargs):
        """Print Chars, if not running '--quiet'ly"""

        bt = self.bt
        if not main.args.quiet:
            bt.print(*args, **kwargs)

    def bt_write_if(self, bytes_):
        """Write Bytes, if not running '--quiet'ly"""

        bt = self.bt
        if not main.args.quiet:
            bt.write(bytes_)


#
# Loopback Keyboard Chords into the Screen
#


class ChordsScreenTest:
    """Loopback Keyboard Chords into the Screen"""

    def __init__(self, ct):
        self.ct = ct

        bt = ct.bt

        self.bt = bt

    def run_till_quit(self):  # noqa  # C901 too complex
        """Loopback Keyboard Chords into the Screen"""

        args_quiet = main.args.quiet

        bt = self.bt
        ct = self.ct

        assert DSR == b"\x1B[6n"
        assert CprPatternYX == rb"\x1B[\\[]([0-9]+);([0-9]+)R"

        writes = bytearray()
        yx_by_frame = 2 * [None]

        # Read Bytes|Str

        frame = None
        while True:
            read = ct.read()

            # Warp the Cursor to the Frame of Bytes|Str

            old_frame = frame
            frame = int(isinstance(read, bytes))

            if not args_quiet:
                if old_frame != frame:
                    yx = yx_by_frame[frame]
                    if yx is not None:
                        cup = CUP_Y_X.format(*yx)
                        cup = cup.encode()
                        bt.write(cup)

            # Capture and trace the Bytes, else write the Bytes in place of Str

            if isinstance(read, bytes):
                writes.extend(read)
                rep = bytes(writes)
                rep = repr(rep).encode()
                if not args_quiet:
                    bt.write(b"\r" + b"\x1B[K" + rep)
            else:
                bt.write(writes)
                writes.clear()

                # Quit after Control+C

                if read == (Control + "C"):
                    break

            # Find the Cursor

            if not args_quiet:
                bt.write(DSR)

                cpr_else = bt.read()
                m = re.match(rb"^" + CprPatternYX + rb"$", string=cpr_else)
                assert m, cpr_else  # todo: let my people type this fast

                (y, x) = (m.group(1), m.group(2))
                (y, x) = (y.decode(), x.decode())
                yx_by_frame[frame] = (y, x)

                # Warp the Cursor to the Frame of Str, if need be

                old_frame = frame
                frame = int(isinstance("", bytes))

                if old_frame != frame:
                    yx = yx_by_frame[frame]
                    if yx is not None:
                        cup = CUP_Y_X.format(*yx)
                        cup = cup.encode()
                        bt.write(cup)


#
# Test the ChordsTerminal Read Until till ⌃C
#


class ChordsKeyboardTest:
    """Test the ChordsTerminal Read Until till ⌃C"""

    def __init__(self, ct):
        self.ct = ct

        bt = ct.bt
        t0 = dt.datetime.now()

        self.bt = bt
        self.t0 = t0
        self.t1 = t0
        self.old_ms = None
        self.clocking = False

    def run_till_quit(self):
        """Test the ChordsTerminal Read Until till ⌃C"""

        ct = self.ct

        while True:
            if ct.kbhit(timeout=0):
                read = self.read_verbosely()
                if read == (Control + "C"):
                    break

            self.log_clock()

            self.sleep_till()

    def read_verbosely(self):
        """Timestamp Chars from the Terminal, and the Bytes inside them"""

        bt = self.bt
        ct = self.ct

        # Fetch one Byte or some Words of Chars

        read = ct.read()

        # Timestamp

        self.t1 = dt.datetime.now()
        t1t0 = self.t1 - self.t0
        self.t0 = self.t1

        # Close the Clock Line if open

        if self.clocking:
            self.clocking = False
            bt.print()

        # Log the whole Keystroke as Words of Chars, or a Byte of it

        ms = int(t1t0.total_seconds() * 1000)
        if not ms:
            bt.print("    {}, {!r}".format(ms, read))
        else:
            if self.old_ms == 0:
                bt.print()
            bt.print("{}, {!r}".format(ms, read))

        self.old_ms = ms

        # Succeed

        return read

    def log_clock(self):
        """Timestamp no Chars and no Bytes from the Terminal"""

        bt = self.bt

        # Limit the rate of logging

        t2 = dt.datetime.now()
        t2t1 = t2 - self.t1
        if t2t1 >= dt.timedelta(seconds=3):
            self.t1 += dt.timedelta(seconds=1)

            # Print a Separator and open the Clock Line

            if not self.clocking:
                self.clocking = True
                bt.print()

            # Refresh the Clock

            hms = t2.strftime("%H:%M:%S")
            bt.write(b"\r" + hms.encode())

    def sleep_till(self):
        """Yield Cpu while no Keyboard Input"""

        ct = self.ct

        next_clock = self.t1 + dt.timedelta(seconds=3)
        t3 = dt.datetime.now()
        if t3 > next_clock:
            timeout = next_clock - t3
            timeout = timeout.total_seconds()
            if timeout > 0:
                ct.kbhit(timeout=timeout)


#
# Read Terminal Input as Chars formed from Bytes of Terminal Input
#
#   "Esc", "Space", "Tab", and "Return" for b"\x1B", b" ", b"\t", and b"\r"
#   "⇧Tab", "⌥Space", b"⇧←" for b"\x1B[Z", b"\xC2\xA0", b"\x1B[1;2C"
#   "⌥3", "⇧F12" for b"\xC2\xA3", b"\x1B[\x33\x34\x7E"
#   "⌥E E" for b"\xC2\xB4"
#   etc
#


class ChordsTerminal:
    """Read Input as Chars, from a ByteTerminal"""

    def __init__(self, bt):
        self.bt = bt

        self.holds = bytearray()
        self.peeks = bytearray()

        assert bt.tcgetattr is not None
        self.try_me()

    def try_me(self):
        """Run a quick self-test"""

        bt = self.bt

        bt.write(b"")  # tests 'os.write'
        self.kbhit(0)  # tests 'select.select'

    def read(self):
        """Read a piece of a Sequence, or a whole Sequence, or zero Bytes"""

        bt = self.bt

        holds = self.holds
        peeks = self.peeks

        # Read the last Bytes of a whole Sequence, else Bytes of the next Sequence

        index = 0
        while True:
            (seq, plus) = self.bytes_splitseq(holds)

            enough_holds = holds[: len(seq)] if seq else holds
            if enough_holds and (len(peeks) < len(enough_holds)):
                old_peeks = enough_holds[len(peeks) :]
                old_peeks = bytes(old_peeks)

                peeks.extend(old_peeks)
                assert old_peeks and isinstance(old_peeks, bytes), repr(old_peeks)

                return old_peeks

            # Read the Sequence as Chars of Words

            if seq:
                seq_peeks = bytes(peeks)
                assert seq_peeks == seq, (seq_peeks, seq)

                peeks.clear()
                holds[::] = plus

                seq_decode = seq.decode()
                chords = bytes_to_chords_else(seq, default=seq_decode)
                assert chords and not isinstance(chords, bytes), repr(chords)

                return chords

            # Wait to read more Bytes

            kbhit = bt.kbhit(timeout=None)
            assert kbhit, kbhit

            index += 1
            assert index <= 1

            read = bt.read()
            assert read, read
            holds.extend(read)

    def kbhit(self, timeout):
        """Peek a piece of a Sequence, or a whole Sequence, or zero Bytes"""

        bt = self.bt
        stdio = bt.stdio

        holds = self.holds
        peeks = self.peeks

        # Read the last Bytes of a whole Sequence, else Bytes of the next Sequence

        (seq, plus) = self.bytes_splitseq(holds)

        enough_holds = holds[: len(seq)] if seq else holds
        if enough_holds and (len(peeks) < len(enough_holds)):
            return [stdio]

        # Read the Sequence as Chars of Words

        if seq:
            return [stdio]

        # Wait to read more Bytes

        kbhit = bt.kbhit(timeout=timeout)

        return kbhit

    def bytes_splitseq(self, bytes_):
        """Split out one whole Byte Sequence, else zero Bytes"""

        seq = bytes_take_seq(bytes_)
        seq = bytes(seq)  # returns Bytes even when Bytes_ is a ByteArray

        plus = bytes_[len(seq) :]
        assert (seq + plus) == bytes_, (seq, plus, bytes_)

        return (seq, plus)


#
# Name Screen Output Bytes and Keyboard Input Bytes
#


CUP_Y_X = "\x1B[{};{}H"  # Cursor Position (CUP) of (Y, X)

DSR = b"\x1B[6n"  # Device Status Report (DSR) call for CPR

CprPatternYX = rb"\x1B[\\[]([0-9]+);([0-9]+)R"  # Cursor Position Report (CPR) of (Y, X)


#
# Map Keyboard Input Bytes to Keyboard Chords or Text Chars
#


def bytes_to_chords_else(bytes_, default):
    """Find the Keyboard Bytes as Str Words of Keyboard Chords, else return unchanged"""

    if bytes_ in CHORDS_BY_BYTES.keys():
        chords = CHORDS_BY_BYTES[bytes_]
        return chords  # '⌥E E', etc

    return default


def chords_to_bytes(chords):
    """Find the Keyboard Bytes of the some Str Words of Keyboard Chords"""

    matches = list(_[0] for _ in CHORDS_BY_BYTES.items() if _[-1] == chords)
    assert len(matches) <= 1, (len(matches), repr(chords))

    if len(matches) == 1:
        match = matches[-1]
        return match

    encode = chords.encode()
    return encode


CHORDS_BY_BYTES = dict()


CHORDS_BY_BYTES[b"\0"] = "⌃Space"  # ⌃Space ⌃⌥Space ⌃⇧Space ⌃⇧2 ⌃⌥⇧2
CHORDS_BY_BYTES[b"\t"] = "Tab"  # ⌃I ⌃⌥I ⌃⌥⇧I Tab ⌃Tab ⌥Tab ⌃⌥Tab
CHORDS_BY_BYTES[b"\r"] = "Return"  # ⌃M ⌃⌥M ⌃⌥⇧M Return etc
CHORDS_BY_BYTES[b"\x1B"] = "Esc"  # Esc ⌥Esc ⌥⇧Esc etc
CHORDS_BY_BYTES[b" "] = "Space"  # Space ⇧Space
CHORDS_BY_BYTES[b"\x7F"] = "Delete"  # Delete ⌥Delete ⌥⇧Delete etc

# b"\r" is also Return ⌃Return ⌥Return ⇧Return ⌃⌥Return ⌃⇧Return ⌥⇧Return ⌃⌥⇧Return
# b"\x1B" is also Esc ⌃Esc ⌥Esc ⇧Esc ⌃⌥Esc ⌃⇧Esc ⌥⇧Esc ⌃⌥⇧Esc
# b"\x7F" is also Delete ⌃Delete ⌥Delete ⇧Delete ⌃⌥Delete ⌃⇧Delete ⌥⇧Delete ⌃⌥⇧Delete


CHORDS_BY_BYTES[b"\x1B[Z"] = "⇧Tab"  # ⇧Tab ⌃⇧Tab ⌥⇧Tab ⌃⌥⇧Tab
CHORDS_BY_BYTES[b"\xC2\xA0"] = "⌥Space"  # ⌥Space ⌥⇧Space

assert b"\xC2\xA0".decode() == "\u00A0" == "\N{No-Break Space}"

CHORDS_BY_BYTES[b"\x1B[A"] = "↑"  # ↑ ⌥↑ ⇧↑ ⌃⌥↑ ⌃⇧↑ ⌥⇧↑ ⌃⌥⇧↑  # macOS takes ⌃↑
CHORDS_BY_BYTES[b"\x1B[B"] = "↓"  # ↓ ⌥↓ ⇧↓ ⌃⌥↓ ⌃⇧↓ ⌥⇧↓ ⌃⌥⇧↓  # macOS takes ⌃↓
CHORDS_BY_BYTES[b"\x1B[C"] = "→"  # → ⌃⌥→ ⌃⇧→ ⌥⇧→ ⌃⌥⇧→  # macOS takes ⌃→
CHORDS_BY_BYTES[b"\x1Bf"] = "⌥→"
CHORDS_BY_BYTES[b"\x1B[1;2C"] = "⇧→"
CHORDS_BY_BYTES[b"\x1B[D"] = "←"  # ← ⌃⌥← ⌃⇧← ⌥⇧← ⌃⌥⇧←  # macOS takes ⌃←
CHORDS_BY_BYTES[b"\x1Bb"] = "⌥←"
CHORDS_BY_BYTES[b"\x1B[1;2D"] = "⇧←"


def add_us_ascii_into_chords_by_bytes():
    """Add a US Ascii Keyboard into Chars by Bytes"""

    chords_by_bytes = CHORDS_BY_BYTES

    # Decode Control Chords

    assert Control == "\N{Up Arrowhead}"  # ⌃

    for ord_ in C0_BYTES:
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


CHORDS_BY_BYTES.update(  # the Fn Key Caps at Mac
    {
        b"\x1BOP": "F1",
        b"\x1BOQ": "F2",
        b"\x1BOR": "F3",
        b"\x1BOS": "F4",
        b"\x1B[15~": "F5",
        b"\x1B[17~": "F6",  # F6  # ⌥F1
        b"\x1B[18~": "F7",  # F7  # ⌥F2
        b"\x1B[19~": "F8",  # F8  # ⌥F3
        b"\x1B[20~": "F9",  # F9  # ⌥F4
        b"\x1B[21~": "F10",  # F10  # ⌥F5
        b"\x1B[23~": "⌥F6",  # F11  # ⌥F6  # macOS takes F11
        b"\x1B[24~": "F12",  # F12  # ⌥F7
        b"\x1B[25~": "⇧F5",  # ⌥F8  # ⇧F5
        b"\x1B[26~": "⇧F6",  # ⌥F9  # ⇧F6
        b"\x1B[28~": "⇧F7",  # ⌥F10  # ⇧F7
        b"\x1B[29~": "⇧F8",  # ⌥F11  # ⇧F8
        b"\x1B[31~": "⇧F9",  # ⌥F12  # ⇧F9
        b"\x1B[32~": "⇧F10",
        b"\x1B[33~": "⇧F11",
        b"\x1B[34~": "⇧F12",
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
# Define whole & partial Control Byte and Text Byte Sequences
#


BS = b"\b"  # Backspace
CR = b"\r"  # Carriage Return
LF = b"\n"  # Line Feed
Esc = b"\x1B"  # Escape

CSI = b"\x1B["  # Control Sequence Introducer  # ended by rb"[\x30-\x7E]"
OSC = b"\x1B]"  # Operating System Command  # ended by BEL, CR, Esc \ ST, etc
SS3 = b"\x1BO"  # Single Shift Three

C0_BYTES = b"".join(chr(_).encode() for _ in range(0, 0x20)) + b"\x7F"
C1_BYTES = b"".join(chr(_).encode() for _ in range(0x80, 0xA0))  # not U+00A0, U+00AD


Control = "\N{Up Arrowhead}"  # ⌃
Option = "\N{Option Key}"  # ⌥
Shift = "\N{Upwards White Arrow}"  # ⇧
Command = "\N{Place of Interest Sign}"  # ⌘


CsiStartPattern = b"\x1B\\[" rb"[\x30-\x3F]*[\x20-\x2F]*"  # leading Zeroes allowed
CsiEndPattern = rb"[\x40-\x7E]"
# as per 1991 ECMA-48_5th 5.4 Control Sequences
# Csi Patterns solve many Pm, Pn, and Ps, but not the Pt of Esc ] OSC Ps ; Pt BEL


MouseSixByteReportPattern = b"\x1B\\[" rb"M..."  # MPR X Y


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


def bytes_take_seq(bytes_):
    """Take one whole Byte Sequence, else zero Bytes"""

    seq = b""
    if bytes_:
        seq = bytes_take_mouse_six_byte_report(bytes_)
        if not seq:
            seq = bytes_take_control_sequence(bytes_)  # would misread Mouse Six Byte
            if not seq:
                seq = bytes_take_text_sequence(bytes_)  # would misread C0 Sequence

    return seq  # may be empty


def bytes_take_text_sequence(bytes_):
    """Take one or more whole UTF-8 Encodings of Text Chars"""

    seq = b""
    for index in range(len(bytes_)):
        length = index + 1

        try_seq = bytes_[:length]
        try:
            _ = try_seq.decode()
        except UnicodeDecodeError:
            continue

        if try_seq[-1:] in C0_BYTES:
            break

        seq = try_seq

    return seq


def bytes_take_control_sequence(bytes_):
    """Take 1 whole C0 Control Sequence that starts these Bytes, else 0 Bytes"""

    # Take nothing when given nothing

    if bytes_ == b"":
        return b""

    # Take nothing when not given a C0 Control Byte to start with

    head = bytes_[:1]
    if head not in C0_BYTES:
        return b""

    # Take a C0 Control Byte by itself

    if head not in b"\r" b"\x1B":
        return head

    # Look for CR LF after CR, else take CR LF, else take CR

    if head == b"\r":
        cr_plus = bytes_[:2]
        if not cr_plus[1:]:
            return b""
        if cr_plus == b"\r\n":
            return cr_plus
        return head

    # Take 1 whole C0 Esc Sequence that starts these Bytes, else 0 Bytes

    seq = bytes_take_esc_sequence(bytes_)

    return seq  # may be empty


def bytes_take_esc_sequence(bytes_):
    """Take 1 whole C0 Esc Sequence that starts these Bytes, else 0 Bytes"""

    assert Esc == b"\x1B"
    assert CsiStartPattern == b"\x1B\\[" rb"[\x30-\x3F]*[\x20-\x2F]*"
    assert CsiEndPattern == rb"[\x40-\x7E]"

    assert bytes_.startswith(Esc), bytes_

    # Look for Esc and a Byte

    if not bytes_[1:]:
        return b""

    esc_plus = bytes_[:2]

    # Look for Esc [ O and a Byte, like as the Single Shift Three (SS3) of F1 F2 F3 F4

    assert SS3 == b"\x1BO"

    if esc_plus == b"\x1BO":
        if not bytes_[2:]:
            return b""

        ss3_plus = bytes_[:3]
        return ss3_plus

    # Look for Text Byte after Esc, else take it with Esc, else take Esc alone

    if esc_plus != b"\x1B[":  # CSI
        if (esc_plus[-1:] in C0_BYTES) or (esc_plus[-1] >= 0x80):
            return esc_plus[:1]

        return esc_plus

    # Look for more Bytes while Esc [ Sequence incomplete

    assert Esc == b"\x1B"
    assert CSI == b"\x1B["

    assert bytes_.startswith(CSI), bytes_

    m0 = re.match(rb"^" + CsiStartPattern + rb"$", string=bytes_)
    if m0:
        return b""

    # Take one whole Esc [ Sequence, or settle for Esc [ begun but cut short

    m1 = re.match(rb"^" + CsiStartPattern, string=bytes_)

    start_seq = m1.string[m1.start() : m1.end()]
    end_seq = m1.string[m1.end() :][:1]
    seq = start_seq + end_seq

    mn = re.match(rb"^" + CsiEndPattern + rb"$", string=end_seq)
    if not mn:
        return start_seq

    return seq


def bytes_take_mouse_six_byte_report(bytes_):
    """Take 1 whole Mouse Six Byte Report that starts these Bytes, else 0 Bytes"""

    assert MouseSixByteReportPattern == b"\x1B\\[" rb"M..."  # MPR X Y
    assert len(MouseSixByteReportPattern) == 7

    m = re.match(rb"^" + MouseSixByteReportPattern + rb"$", string=bytes_)
    if not m:
        return b""

    report = m.string[m.start() : m.end()]
    assert len(report) == 6

    return report


#
# Read Terminal Input without line-buffering, & write \n Output as itself, not as \r\n
#


class BytesTerminal:
    r"""Read Input without line-buffering, & write \r Output as itself, not as \r\n"""

    def __init__(self, stdio):
        self.stdio = stdio
        self.fd = stdio.fileno()
        self.tcgetattr = None

    def __enter__(self):
        r"""Stop line-buffering Input and stop replacing \n Output with \r\n"""

        fd = self.fd
        tcgetattr = self.tcgetattr

        if tcgetattr is None:
            tcgetattr = termios.tcgetattr(fd)

            self.tcgetattr = tcgetattr

            tty.setraw(fd, when=termios.TCSADRAIN)  # Drain flushes Output, then changes
            # termios.TCSAFLUSH  # Flush destroys Input, flushes Output, then changes

        self.try_me()

        return self

    def try_me(self):
        """Run a quick self-test"""

        self.write(b"")  # tests 'os.write'
        self.kbhit(0)  # tests 'select.select'

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
        """Write some Bytes without encoding them, & without ending the Line"""

        fd = self.fd
        os.write(fd, line)

    def flush(self):
        """Flush the Output Buffer without waiting for the Line to end"""

        sys.stdout.flush()

    def read(self):
        """Read one or more Bytes"""

        fd = self.fd

        length = 1022  # large Paste came as 1022 Bytes per 100ms  # macOS 2023-03
        read = os.read(fd, length)
        assert read, read  # todo: test when 'os.read' does return b""

        return read

        # ⌘V ⌘V Paste Strokes sometimes arrived together in one read  # macOS 2023-03

    def kbhit(self, timeout=None):  # 'timeout' in seconds
        """Wait till next Input Byte, else till Timeout, else till forever"""

        stdio = self.stdio

        rlist = [stdio]
        wlist = list()
        xlist = list()

        (alt_rlist, _, _) = select.select(rlist, wlist, xlist, timeout)

        return alt_rlist


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
    indices = list(_ for _ in indices if not lines[_].startswith(" "))
    testdoc = "\n".join(lines[indices[-1] + 1 :])
    testdoc = textwrap.dedent(testdoc)

    print()
    print(testdoc)
    print()

    sys.exit(0)


#
# Complete the CHORDS_BY_BYTES
#


add_us_ascii_into_chords_by_bytes()


#
# Sketch future work
#


# todo: copy in dreams from:  demos/vi1.py, futures.md, etc

_ = r"""

solve the Esc [ 1 d echoed without quoting

solve the typing too fast slips the CPR of DSR

move the ⇧Z ⇧K, ⇧Z ⇧S, etc into ⇧Z ⇧T, 1 ⇧Z ⇧T, 2 ⇧Z ⇧T, etc
still have a -q ⇧Z ⇧S that doesn't echo the Keystrokes

\x and \u and \U and \r character insert, in ChordsScreenTest, such as \r undelayed

test \n \r \r\n bytes inside macOS Paste Buffer

⌃C ⌃D ⌃\ should help you quit

Esc should explain you owe us more input

echoed as digits
then as ⎋ [ digits ; digits ;

less pain here from tides forcing auto-wrapped searches and auto-cancelled searches

jump to color

"""


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/vi2.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
