#!/usr/bin/env python3

r"""
usage: vi2.py [-h]

edit the Screen in reply to Keyboard Chord Sequences

options:
  -h, --help  show this help message and exit

quirks:
  quits when told ⌃C ⇧Z ⇧Q, or ⌃C : Q ! Return, or ⌃Q

keystrokes:
  ⌃C ⌃G ⌃M ⌃N ⌃P Return Space
  $ + 0 ⇧G ⇧H ⇧K ⇧N ^ H J K L |
  ⎋[1m ⎋[31m

docs:
  https://unicode.org/charts/PDF/U0000.pdf
  https://unicode.org/charts/PDF/U0080.pdf
  https://en.wikipedia.org/wiki/ANSI_escape_code
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
  https://www.ecma-international.org/publications-and-standards/standards/ecma-48
    /wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf

large inputs:
  git show && ./demos/vi2.py
  make p.py && vi +':set t_ti= t_te=' p.py && ./demos/vi2.py
  git grep --color=always def |less -FIRX && ./demos/vi2.py
  cat ./demos/vi2.py |dd bs=1 count=10123 |tr '[ -~]' '.' |pbcopy && ./demos/vi2.py

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
import struct
import sys
import termios
import textwrap
import time
import tty

_ = time


#
# Run from the Sh command line
#


def main():
    """Run from the Sh command line"""

    args = parse_vi2_py_args()
    main.args = args

    # Reply to each Keystroke

    t0 = dt.datetime.now()
    t1 = t0
    clocking = False

    stdio = sys.__stdout__  # '__stdout__' as per 'shutil.get_terminal_size'
    with ByteTerminal(stdio) as bt:
        bt.print("Press ⌃C to stop logging Millisecond Delays and Input Bytes")

        line = None
        while True:
            while True:
                read_twice = bt.read_twice(0)
                if not read_twice:
                    break

                old_line = line
                line = read_twice

                t1 = dt.datetime.now()
                t1t0 = t1 - t0
                t0 = t1

                # Print the Input Line

                if clocking:
                    clocking = False
                    bt.print()

                ms = int(t1t0.total_seconds() * 1000)
                bt.print("{}, {}".format(ms, line))

                if line == control(b"C"):
                    if old_line == Esc:  # takes Esc ⌃C without quitting
                        continue
                    break

            if line == control(b"C"):
                break

            # Print a Clock between Input Lines

            t2 = dt.datetime.now()
            t2t1 = t2 - t1
            if t2t1 >= dt.timedelta(seconds=3):
                t1 += dt.timedelta(seconds=1)
                hms = t2.strftime("%H:%M:%S")

                if not clocking:
                    bt.print()

                bt.write(b"\r" + hms.encode())
                clocking = True


def parse_vi2_py_args():
    """Parse the Args from the Sh command line"""

    parser = compile_argdoc()
    args = parser_parse_args(parser)  # prints help and exits zero, when asked

    return args


#
# Bypass the Line Buffer to speak with the Screen and Keyboard of the Terminal
#


class ByteTerminal:
    r"""Start/ Stop line-buffering Input and replacing \n Output with \r\n"""

    def __init__(self, stdio):
        self.stdio = stdio

        self.fd = stdio.fileno()
        self.tcgetattr = None

        self.holds = bytearray()
        self.peeks = bytearray()

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
        """Write some Bytes without encoding or ending them"""

        fd = self.fd

        os.write(fd, line)

    def read_twice(self, timeout):
        """Read each of the next whole Sequence, then the Sequence, else zero Bytes"""

        holds = self.holds
        peeks = self.peeks

        # Promptly read each Byte of a Sequence arriving in parts

        while True:
            (some, more) = self.bytes_splitline(holds)
            assert holds[: len(peeks)] == peeks, (holds, peeks)

            if (not some) or (peeks and (len(peeks) < len(some))):
                peek = holds[len(peeks) :][:1]
                peek = bytes(peek)
                if peek:
                    peeks.extend(peek)
                    return peek

            # Read one whole Sequence

            if some:
                old_peeks = bytes(peeks)

                peeks[::] = list()
                holds[::] = more

                # Return the whole Sequence after each Byte only when multiple Bytes

                if old_peeks and (len(some) == 1):
                    assert old_peeks == some == b"\r", (old_peeks, some)
                    continue

                return some

            # Wait awhile for more Bytes

            if not self.kbhit(timeout):
                break

        return None

    def readline(self):
        """Wait for the next whole Byte Sequence, and read it"""

        fd = self.fd
        holds = self.holds

        length = 1022  # Paste came as 1022 Bytes per 100ms, at 2023-03 macOS
        while not self.kbhit(timeout=0):
            read = os.read(fd, length)
            holds.extend(read)

        (some, more) = self.bytes_splitline(holds)
        assert some, (some, more)

        holds[::] = more

        return some

    def kbhit(self, timeout):  # 'timeout' in seconds
        """Wait for a whole Byte Sequence, else time out, but say if found"""

        fd = self.fd
        holds = self.holds

        length = 1022  # Paste came as 1022 Bytes per 100ms, at 2023-03 macOS

        rlist = [self.stdio]
        wlist = list()
        xlist = list()

        t0 = dt.datetime.now()
        while True:
            (some, more) = self.bytes_splitline(holds)
            if some:
                return rlist  # say found

            t1 = dt.datetime.now()
            t1t0 = (t1 - t0).total_seconds()
            if (not timeout) or (t1t0 < timeout):
                alt_timeout = (timeout - t1t0) if timeout else 0

                (rlist_, _, _) = select.select(rlist, wlist, xlist, alt_timeout)
                if rlist_:
                    read = os.read(fd, length)
                    holds.extend(read)

                    continue

            return list()  # say not found

        # trying many ⌘V ⌘V Paste Strokes bundles more than one together  # macOS 2022

    def bytes_splitline(self, bytes_):
        """Split out a whole Byte Sequence, else split out zero Bytes"""

        some = bytes_take_some(bytes_)
        some = bytes(some)  # returns Bytes even when Bytes_ is a ByteArray

        more = bytes_[len(some) :]
        assert (some + more) == bytes_, (some, more, bytes_)

        return (some, more)


#
# Pick out the next few Bytes to work with
#


def bytes_take_some(bytes_):
    """Pick out the next few Bytes to work with"""

    some = b""
    if bytes_:
        some = bytes_take_mouse_six_byte_report(bytes_)
        if not some:
            some = bytes_take_control_sequence(bytes_)  # would misread Mouse Six Byte
            if not some:
                some = bytes_take_text_sequence(bytes_)  # would misread C0 Sequence

    return some


def bytes_take_text_sequence(bytes_):
    """Take 1 or more complete UTF-8 Encodings of Text Chars"""

    enc = b""
    for index in range(len(bytes_)):
        length = index + 1

        try_enc = bytes_[:length]
        try:
            _ = try_enc.decode()
        except UnicodeDecodeError:
            continue

        if try_enc[-1:] in C0_BYTES:
            break

        enc = try_enc

    return enc


def bytes_take_control_sequence(bytes_):
    """Take 1 whole C0 Control Sequence that starts these Bytes, else 0 Bytes"""

    assert Esc == b"\x1B"
    assert CSI == b"\x1B["
    assert EscSequencePattern == b"\x1B\\[" b"[0123456789;<?]*" b"[^0123456789;<?]"

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

    # Look for Esc paired after Esc, else take Esc paired, else look past Esc [

    assert head == b"\x1B", head  # Esc

    esc_plus = bytes_[:2]
    if not esc_plus[1:]:
        return b""

    if esc_plus != b"\x1B[":  # CSI
        assert esc_plus[-1] not in range(0x80, 0x100), esc_plus[-1]  # todo
        return esc_plus

    # Take nothing while Esc Sequence incomplete

    m = re.match(EscSequencePattern, string=bytes_)
    if not m:
        return b""

    # Take one whole Esc Sequence

    seq = m.string[m.start() : m.end()]
    assert seq[-1] not in range(0x80, 0x100), seq[-1]  # todo

    return seq


def bytes_take_mouse_six_byte_report(bytes_):
    """Take 1 whole Mouse Six Byte Report that starts these Bytes, else 0 Bytes"""

    assert MouseSixByteReportPattern == b"\x1B\\[M..."
    assert len(MouseSixByteReportPattern) == 7

    m = re.match(MouseSixByteReportPattern, string=bytes_)
    if not m:
        return b""

    report = m.string[m.start() : m.end()]
    assert len(report) == 6

    return report


#
# Speak concisely of the C0 Controls
#


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
# Sketch how to split a Stream of Bytes into Text Sequences and Control Sequences
#


C0_BYTES = b"".join(chr(_).encode() for _ in range(0, 0x20)) + b"\x7F"
C1_BYTES = b"".join(chr(_).encode() for _ in range(0x80, 0xA0))  # not U+00A0, U+00AD

BS = b"\b"  # Backspace  # BS
CR = b"\r"  # Carriage Return   # CR
LF = b"\n"  # Line Feed  # LF
Esc = b"\x1B"  # Escape  # ESC

CSI = b"\x1B["  # Control Sequence Introducer  # CSI


EscSequencePattern = b"\x1B\\[" b"[0123456789;<?]*" b"[^0123456789;<?]"
# solves many Ps of Pm, but not Pt
# digits may start with "0"


MouseSixByteReportPattern = b"\x1B\\[M..."  # MPR X Y


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
# Sketch future work
#


# FIXME


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/vi2.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
