#!/usr/bin/env python3

r"""
usage: vi.py [-h] [-q]

copy Bytes to Screen from Keyboard, till told to quit

options:
  -h, --help   show this help message and exit
  -q, --quiet  say less

quirks:
  quits when told ⌃C ⇧Z ⇧Q or ⌃C : Q ! Return
  logs Keystrokes, Paste, and Milliseconds Delays when told: ⇧Z ⇧K
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

        if not args.quiet:
            self.greet()

        return self

    def __exit__(self, *exc_info):
        """Undo the Configure Terminal at entry, or not"""

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

    def runlines(self):
        """Run the Code that defines a Line, else ring the Terminal Bell"""

        bot_by_lines = self.bot_by_lines
        lines = self.lines

        bot = self.write_bel
        if lines in bot_by_lines.keys():
            bot = bot_by_lines[lines]

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
        assert LowerLeftForm == b"\x1B[{y}H"

        if not args.quiet:
            bt.print("Press ⌃C to stop logging Keystrokes and Paste")

        while True:
            line = self.readline()
            self.logline()

            if line == b"\x03":
                break

        if not args.quiet:
            size = shutil.get_terminal_size()
            bt.write("\x1B[{y}H".format(y=size.lines).encode())
            bt.print()
            bt.print("Press ⌃C ⇧Z ⇧Q or ⌃C : Q ! Return to quit")

    def try_screen(self):  # ⇧Z ⇧S
        """Copy Keystrokes and Paste to Screen, till told to quit"""

        args = main.args
        bt = self.bt

        assert control(b"C") == b"\x03"
        assert LowerLeftForm == b"\x1B[{y}H"

        if not args.quiet:
            bt.print("Press ⌃C to stop copying Keystrokes and Paste to Screen")

        while True:
            line = self.readline()
            bt.write(line)

            if line == b"\x03":
                break

        if not args.quiet:
            size = shutil.get_terminal_size()
            bt.write("\x1B[{y}H".format(y=size.lines).encode())
            bt.print()
            bt.print("Press ⌃C ⇧Z ⇧Q or ⌃C : Q ! Return to quit")

    #
    # Define enough Keystrokes to bootstrap Vi - enough for ⇧Z ⇧K and ⇧Z ⇧S
    #

    def form_bot_by_lines(self):
        """Say which Code runs in reply to which Key Sequences"""

        bot_by_lines = dict()

        # Define some Keystroke Sequences

        bot_by_lines[b"\x03"] = self.read_more
        bot_by_lines[b"ZK"] = self.try_keyboard
        bot_by_lines[b"ZS"] = self.try_screen
        bot_by_lines[b"ZQ"] = self.quit_bang
        bot_by_lines[b":q!\r"] = self.quit_bang

        # Mark some Keystroke Sequences as incomplete

        bot_by_lines[b":"] = self.read_more
        bot_by_lines[b":q!"] = self.read_more
        bot_by_lines[b":q"] = self.read_more
        bot_by_lines[b"Z"] = self.read_more

        # Succeed

        return bot_by_lines

    def quit_bang(self):  # ⇧Z ⇧Q  # : Q !
        """Quit when told"""

        sys.exit()

    def write_bel(self):
        """Freak over almost any tupo"""

        self.bt.write(b"\x07")

    def read_more(self):
        """Take another Byte before choosing a reply"""

        line = self.readline()

        if self.lines == b"\x03":
            if line == b"\x03":
                self.write_bel()
            self.lines = b""

        self.lines += line
        self.runlines()

    #
    # Define enough Keystrokes to bootstrap Vi - enough for ⇧Z ⇧K and ⇧Z ⇧S
    #


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

    # Take Esc plus a Byte

    assert Esc == b"\x1B"
    assert CSI == b"\x1B["

    stroke = line
    if line.startswith(b"\x1B"):  # Esc
        stroke = b""
        if len(line) >= 2:
            stroke = line

            # Take CSI plus Unsigned Ints split or marked by ";" and "?"

            if line.startswith(b"\x1B["):  # CSI
                stroke = b""
                for index in range(2, len(line)):
                    end = line[index:][:1]
                    if end not in b"012345679;?":  # solves many Ps of Pm, but not Pt
                        stroke = line[: (index + 1)]
                        break

    # Split out the leading Stroke

    stroke = bytes(stroke)
    lookahead = line[len(stroke) :]

    assert (stroke + lookahead) == line, (stroke, lookahead, line)

    # Succeed

    return (stroke, lookahead)


#
# Name some Python Idioms
#


#
# Name Cheat Codes of the Vi Easter Egg buried inside a Layer of the Terminal
#


Esc = b"\x1B"  # also known as rb"\e"

CSI = b"\x1B["  # Control Sequence Introducer

CursorPositionForm = b"\x1B[{y};{x}H"  # CSI Ps ; Ps H  # CursorPosition CUP Y X

UpperLeft = b"\x1BH"  # the 4 variations on CPR of (), (y), (y,x), (x)
LowerLeftForm = b"\x1B[{y}H"
LowerRightForm = b"\x1B[{y};{x}H"
UpperRightForm = b"\x1B[;{x}H"


_ = r"""  # todo

C0_C1_INTS = list(range(0x00, 0x20)) + [0x7F] + list(range(0x80, 0xA0))
C0_C1_BYTES = list(struct.pack("B", _) for _ in C0_C1_INTS)

BracketedPasteEnter = b"\x1B[?2004h"  # CSI ? Pm h  # Ps = 2 0 0 4
BracketedPasteExit = b"\x1B[?2004l"  # CSI ? Pm l  # Ps = 2 0 0 4

DeviceStatusReport = b"\x1B[6n"  # CSI Ps n  # call for CPR

CursorPositionReport = rb"\x1B\[([0-9]+);([0-9+)R"  # CSI Ps ; Ps R  # CPR Y X

"""


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
# Cite Docs
#
#   https://en.wikipedia.org/wiki/ANSI_escape_code
#   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
#


#
# Sketch future work
#


# todo


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/ttypaint.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
