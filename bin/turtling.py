#!/usr/bin/env python3

r"""
usage: turtling.py [-h]

draw inside a Terminal Window with Logo Turtles

options:
  -h, --help  show this message and exit
  --yolo      do what's popular now (draws, else chats)

examples:
  turtling.py --h  # shows more help and quits
  turtling.py  # shows some help and quits
  turtling.py --yolo  # does what's popular now (draws, else chats)
"""

# code reviewed by People, Black, Flake8, MyPy, & PyLance-Standard


import __main__
import argparse
import ast
import bdb
import collections
import decimal
import glob
import math
import os
import pathlib
import pdb
import platform
import re
import select  # Windows sad at 'select.select' of Named Pipes
import shlex
import shutil
import signal
import subprocess
import sys
import termios
import textwrap
import time
import traceback
import tty
import typing
import unicodedata


turtling = sys.modules[__name__]


DegreeSign = unicodedata.lookup("Degree Sign")  # ° U+00B0
FullBlock = unicodedata.lookup("Full Block")  # █ U+2588
Turtle_ = unicodedata.lookup("Turtle")  # 🐢 U+01F422


#
# Run well from the Sh Command Line
#


def main() -> None:
    """Run well from the Sh Command Line"""

    parse_turtling_py_args_else()  # often prints help & exits

    try:
        main_try()
    except bdb.BdbQuit:
        raise
    except Exception as exc:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        assert exc_type is type(exc_value), (exc_type, exc_value)
        assert exc is exc_value, (exc, exc_value)

        if not hasattr(sys, "last_exc"):
            sys.last_exc = exc_value

        traceback.print_exc(file=sys.stderr)

        print("\n", file=sys.stderr)
        print("\n", file=sys.stderr)
        print("\n", file=sys.stderr)

        print(">>> sys.last_traceback = sys.exc_info()[-1]", file=sys.stderr)
        sys.last_traceback = exc_traceback

        print(">>> pdb.pm()", file=sys.stderr)
        pdb.pm()

        raise


def main_try() -> None:

    if not turtling_client_run():
        if not turtling_server_run():
            assert False, "Turtles Server succeeds or quits, never just fails"


def parse_turtling_py_args_else() -> argparse.Namespace:
    """Take Words in from the Sh Command Line"""

    doc = __main__.__doc__
    assert doc, (doc,)

    parser = doc_to_parser(doc, add_help=True, startswith="examples:")

    yolo_help = "do what's popular now (draws, else chats)"
    parser.add_argument("--yolo", action="count", help=yolo_help)

    ns = parse_args_else(parser)  # often prints help & exits

    return ns

    # often prints help & exits


def doc_to_parser(doc: str, add_help: bool, startswith: str) -> argparse.ArgumentParser:
    """Form an ArgParse ArgumentParser out of the Doc, often the Main Doc"""

    assert doc
    strip = doc.strip()
    lines = strip.splitlines()

    usage = lines[0]
    prog = usage.split()[1]
    description = lines[2]

    epilog = strip[strip.index(startswith) :]

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=add_help,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    return parser


def parse_args_else(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Take Words in from the Sh Command Line, else Print Help and Exit"""

    epilog = parser.epilog
    assert epilog, (epilog,)

    shargs = sys.argv[1:]
    if sys.argv[1:] == ["--"]:  # ArgParse chokes if Sep present without Pos Args
        shargs = list()

    testdoc = textwrap.dedent("\n".join(epilog.splitlines()[1:]))
    if not sys.argv[1:]:
        print()
        print(testdoc)
        print()

        sys.exit(0)  # exits 0 after printing help

    ns = parser.parse_args(shargs)  # often prints help & exits
    return ns

    # often prints help & exits


#
# Name Control Bytes and Escape Sequences
#


#
#   ⌃G ⌃H ⌃I ⌃J ⌃M ⌃[   \a \b \t \n \r \e
#
#   and then the @ABCDEGHIJKLMPSTZdhlmnq forms of ⎋[ Csi, without R t } ~, are
#
#   ⎋[A ↑  ⎋[B ↓  ⎋[C →  ⎋[D ←
#   ⎋[I Tab  ⎋[Z ⇧Tab
#   ⎋[d row-go  ⎋[G column-go  ⎋[H row-column-go
#
#   ⎋[M rows-delete  ⎋[L rows-insert  ⎋[P chars-delete  ⎋[@ chars-insert
#   ⎋[J after-erase  ⎋[1J before-erase  ⎋[2J screen-erase  ⎋[3J scrollback-erase
#   ⎋[K tail-erase  ⎋[1K head-erase  ⎋[2K row-erase
#   ⎋[T scrolls-down  ⎋[S scrolls-up
#
#   ⎋[4h insert  ⎋[4l replace  ⎋[6 q bar  ⎋[4 q skid  ⎋[ q unstyled
#
#   ⎋[1m bold, ⎋[3m italic, ⎋[4m underline, ⎋[7m reverse/inverse
#   ⎋[31m red  ⎋[32m green  ⎋[34m blue  ⎋[38;5;130m orange
#   ⎋[m plain
#
#   ⎋[6n call for ⎋[{y};{x}R  ⎋[18t call for ⎋[{rows};{columns}t
#
#   ⎋[E repeat \r\n
#
#   and also VT420 had DECIC ⎋['} col-insert, DECDC ⎋['~ col-delete
#


Y_32100 = 32100  # larger than all Screen Row Heights tested
X_32100 = 32100  # larger than all Screen Column Widths tested


BS = "\b"  # 00/08 Backspace ⌃H
HT = "\t"  # 00/09 Character Tabulation ⌃I
LF = "\n"  # 00/10 Line Feed ⌃J  # akin to CSI CUD "\x1B" "[" "B"
CR = "\r"  # 00/13 Carriage Return ⌃M  # akin to CSI CHA "\x1B" "[" "G"

ESC = "\x1B"  # 01/11 Escape ⌃[

SS3 = "\x1B" "O"  # 04/15 Single Shift Three  # in macOS F1 F2 F3 F4

CSI = "\x1B" "["  # 05/11 Control Sequence Introducer
CSI_EXTRAS = "".join(chr(_) for _ in range(0x20, 0x40))  # !"#$%&'()*+,-./0123456789:;<=>?, no @
# Parameter, Intermediate, and Not-Final Bytes of a CSI Escape Sequence


CUU_Y = "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
CUD_Y = "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down  # "\n" is Pn 1 except from last Row
CUF_X = "\x1B" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right
CUB_X = "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left  # "\b" is Pn 1

# CNL_Y = "\x1B" "[" "{}E"  # CSI 04/05 Cursor Next Line (CNL)  # a la "\r\n" replace, not insert

CHA_Y = "\x1B" "[" "{}G"  # CSI 04/07 Cursor Character Absolute  # "\r" is Pn 1
VPA_Y = "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

# CUP_1_1 = "\x1B" "[" "H"  # CSI 04/08 Cursor Position
# CUP_Y_1 = "\x1B" "[" "{}H"  # CSI 04/08 Cursor Position
# CUP_1_X = "\x1B" "[" ";{}H"  # CSI 04/08 Cursor Position
CUP_Y_X = "\x1B" "[" "{};{}H"  # CSI 04/08 Cursor Position

ED_P = "\x1B" "[" "{}J"  # CSI 04/10 Erase in Display  # 0 Tail # 1 Head # 2 Rows # 3 Scrollback

CHT_X = "\x1B" "[" "{}I"  # CSI 04/09 Cursor Forward [Horizontal] Tabulation  # "\t" is Pn 1
CBT_X = "\x1B" "[" "{}Z"  # CSI 05/10 Cursor Backward Tabulation

ICH_X = "\x1B" "[" "{}@"  # CSI 04/00 Insert Character
IL_Y = "\x1B" "[" "{}L"  # CSI 04/12 Insert Line
DL_Y = "\x1B" "[" "{}M"  # CSI 04/13 Delete Line
DCH_X = "\x1B" "[" "{}P"  # CSI 05/00 Delete Character

DECIC_X = "\x1B" "[" "{}'}}"  # CSI 02/07 07/13 DECIC_X  # "}}" to mean "}"
DECDC_X = "\x1B" "[" "{}'~"  # CSI 02/07 07/14 DECDC_X
# both with an Intermediate Byte of 02/07 ' Apostrophe [Tick]
# despite DECDC_X and DECIC_X absent from macOS Terminal

EL_P = "\x1B" "[" "{}K"  # CSI 04/11 Erase in Line  # 0 Tail # 1 Head # 2 Row

SU_Y = "\x1B" "[" "{}S"  # CSI 05/03 Scroll Up   # Insert Bottom Lines
SD_Y = "\x1B" "[" "{}T"  # CSI 05/04 Scroll Down  # Insert Top Lines

RM_IRM = "\x1B" "[" "4l"  # CSI 06/12 4 Reset Mode Replace/ Insert
SM_IRM = "\x1B" "[" "4h"  # CSI 06/08 4 Set Mode Insert/ Replace

SGR = "\x1B" "[" "{}m"  # CSI 06/13 Select Graphic Rendition

DSR_5 = "\x1B" "[" "5n"  # CSI 06/14 [Request] Device Status Report  # Ps 5 for DSR_0
DSR_6 = "\x1B" "[" "6n"  # CSI 06/14 [Request] Device Status Report  # Ps 6 for CPR

DECSCUSR = "\x1B" "[" " q"  # CSI 02/00 07/01  # '' No-Style Cursor
DECSCUSR_SKID = "\x1B" "[" "4 q"  # CSI 02/00 07/01  # 4 Skid Cursor
DECSCUSR_BAR = "\x1B" "[" "6 q"  # CSI 02/00 07/01  # 6 Bar Cursor
# all three with an Intermediate Byte of 02/00 ' ' Space

XTWINOPS_18 = "\x1B" "[" "18t"  # CSI 07/04 [Request]   # Ps 18 for XTWINOPS_8


# the quoted Str above sorted mostly by their CSI Final Byte's:  A, B, C, D, G, Z, m, etc

# to test in Sh, run variations of:  printf '\e[18t' && read


# CSI 05/02 Active [Cursor] Position Report (CPR)
CPR_Y_X_REGEX = r"^\x1B\[([0-9]+);([0-9]+)R$"  # CSI 05/02 Active [Cursor] Pos Rep (CPR)


assert CSI_EXTRAS == "".join(chr(_) for _ in range(0x20, 0x40))  # r"[ -?]", no "@"
CSI_P_F_REGEX = r"^\x1B\[([ -?])*(.)$"  # CSI Intermediate/ Parameter Bytes and Final Byte

MACOS_TERMINAL_CSI_FINAL_BYTES = "@ABCDEGHIJKLMPSTZdhlmnq"


#
# Terminal Interventions
#
#   tput clear && printf '\e[3J'  # clears Screen plus Terminal Scrollback Line Buffer
#
#   echo "POSTEDIT='$POSTEDIT'" |hexdump -C && echo "PS1='$PS1'"  # says if Zsh is bolding Input
#   echo "PS0='$PSO'" && echo "PS1='$PS1'" && trap  # says if Bash is bolding Input
#
#   macOS > Terminal > Settings > Profiles > Keyboard > Use Option as Meta Key
#       chooses whether ⌥9 comes through as itself ⌥9, or instead as ⎋9
#


#
# Terminal Docs
#
#   https://unicode.org/charts/PDF/U0000.pdf
#   https://unicode.org/charts/PDF/U0080.pdf
#   https://en.wikipedia.org/wiki/ANSI_escape_code
#   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
#
#   https://www.ecma-international.org/publications-and-standards/standards/ecma-48
#     /wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf
#
#   termios.TCSADRAIN doesn't drop Queued Input but blocks till Queued Output gone
#   termios.TCSAFLUSH drops Queued Input and blocks till Queued Output gone
#


#
# Amp up Import TermIOs, Tty
#


class BytesTerminal:
    """Write/ Read Bytes at Screen/ Keyboard of the Terminal"""

    stdio: typing.TextIO  # sys.stderr
    fd: int  # 2

    before: int  # termios.TCSADRAIN  # termios.TCSAFLUSH  # at Entry
    tcgetattr_else: list[int | list[bytes | int]] | None  # sampled at Entry
    after: int  # termios.TCSADRAIN  # termios.TCSAFLUSH  # at Exit

    kbytes_list: list[bytes]  # Bytes of each Keyboard Chord in  # KeyLogger
    sbytes_list: list[bytes]  # Bytes of each Screen Write out  # ScreenLogger

    #
    # Init, enter, exit, breakpoint, flush, stop, and yolo self-test
    #

    def __init__(self, before=termios.TCSADRAIN, after=termios.TCSADRAIN) -> None:

        assert before in (termios.TCSADRAIN, termios.TCSAFLUSH), (before,)
        assert after in (termios.TCSADRAIN, termios.TCSAFLUSH), (after,)

        stdio = sys.stderr
        fd = stdio.fileno()

        self.stdio = stdio
        self.fd = fd

        self.before = before
        self.tcgetattr_else = None  # is None after Exit and before Entry
        self.after = after

        self.kbytes_list = list()
        self.sbytes_list = list()

        # todo: need .after = termios.TCSAFLUSH on large Paste crashing us

    def __enter__(self) -> "BytesTerminal":  # -> typing.Self:
        r"""Stop line-buffering Input, stop replacing \n Output with \r\n, etc"""

        fd = self.fd
        before = self.before
        tcgetattr_else = self.tcgetattr_else

        if tcgetattr_else is None:
            tcgetattr = termios.tcgetattr(fd)
            assert tcgetattr is not None

            self.tcgetattr_else = tcgetattr

            assert before in (termios.TCSADRAIN, termios.TCSAFLUSH), (before,)

            debug = False
            if debug:
                tty.setcbreak(fd, when=termios.TCSAFLUSH)  # ⌃C prints Py Traceback
            else:
                tty.setraw(fd, when=before)  # SetRaw defaults to TcsaFlush

        return self

    def __exit__(self, *exc_info) -> None:
        r"""Start line-buffering Input, start replacing \n Output with \r\n, etc"""

        fd = self.fd
        tcgetattr_else = self.tcgetattr_else
        after = self.after

        if tcgetattr_else is not None:
            self.bytes_flush()  # for '__exit__'

            tcgetattr = tcgetattr_else
            self.tcgetattr_else = None

            assert after in (termios.TCSADRAIN, termios.TCSAFLUSH), (after,)
            when = after
            termios.tcsetattr(fd, when, tcgetattr)

        return None

    def bytes_breakpoint(self) -> None:
        r"""Breakpoint with line-buffered Input and \n Output taken to mean \r\n, etc"""

        self.__exit__()
        breakpoint()  # to step up the call stack:  u
        self.__enter__()

    def bytes_flush(self) -> None:
        """Flush Screen Output, like just before blocking to read Keyboard Input"""

        stdio = self.stdio
        stdio.flush()

    def bytes_stop(self) -> None:  # todo: learn to do .bytes_stop() well
        """Suspend and resume this Screen/ Keyboard Terminal Process"""

        pid = os.getpid()

        self.__exit__()

        print("Pq Terminal Stop: ⌃Z F G Return")
        print("macOS ⌃C might stop working till you close Window")  # even past:  reset
        print("Linux might freak lots more than that")

        os.kill(pid, signal.SIGTSTP)  # a la 'sh kill $pid -STOP' before 'sh kill $pid -CONT'

        self.__enter__()

        assert os.getpid() == pid, (os.getpid(), pid)

        # a la Emacs ⌃Z suspend-frame, Vim ⌃Z

    def bytes_yolo(self) -> None:  # bin/pq.py btyolo
        """Read Bytes from Keyboard, Write Bytes or Repr Bytes to Screen"""

        bt = self
        kbytes_list = self.kbytes_list
        assert self.tcgetattr_else, (self.tcgetattr_else,)

        # Speak the Rules

        bt.str_print("Let's test Class BytesTerminal")
        bt.str_print("Press ⎋ Fn ⌃ ⌥ ⇧ ⌘ and Spacebar Tab Return and ← ↑ → ↓ and so on")
        bt.str_print("Press ⌃C ⇧R to write Bytes, also ⌃C I same, and press ⌃C ⇧Z ⇧Q to quit")

        bt.str_print()
        bt.str_print()

        bt.sbytes_list.clear()

        # Play till Quit

        tmode = "Write"
        while True:
            kbytes = bt.pull_kchord_bytes_if(timeout=0)

            # Loopback the Keyboard Bytes, else describe them

            if tmode == "Write":
                bt.bytes_write(kbytes)
            else:
                assert tmode == "Meta", (tmode,)

                kstr = repr(kbytes)
                bt.str_write(kstr)

            # Take just I and ⇧R and ⌃C from Vim, for switching between Write and Meta Modes

            if kbytes in (b"i", b"R"):  # I  # ⇧R
                tmode = "Write"
            elif kbytes == b"\x03":  # ⌃C
                tmode = "Meta"

            # Switch back into Meta Mode, secretly magically, after CSI Final Byte b"n" or b"t"
            # todo: wow ugly

            # if kbytes_list[:2] == [b"\x1B", b"["]:  # CSI
            # if kbytes_list[-1] in (b"n", b"t"):  # DSR  # Terminal Size Query

            if kbytes_list[-4:] == [b"\x1B", b"[", b"5", b"n"]:  # DSR_5 to DSR_0
                tmode = "Meta"
            elif kbytes_list[-4:] == [b"\x1B", b"[", b"6", b"n"]:  # DSR_6 to CPR
                tmode = "Meta"
            elif kbytes_list[-5:] == [b"\x1B", b"[", b"1", b"8", b"t"]:  # XTWINOPS_18 to XTWINOPS_8
                tmode = "Meta"

            # Quit at ⇧Z ⇧Q

            if tmode == "Meta":
                if kbytes_list[-2:] == [b"Z", b"Q"]:  # ⇧Z ⇧Q
                    break

        bt.bytes_print()

        # bt.str_print(bt.kbytes_list)
        # bt.str_print(bt.sbytes_list)

    #
    # Write Screen Output Bytes
    #

    def str_print(self, *args, end="\r\n") -> None:
        """Write Chars to the Screen as one or more Ended Lines"""

        sep = " "
        join = sep.join(str(_) for _ in args)
        sbytes = join.encode()

        end_bytes = end.encode()

        self.bytes_print(sbytes, end=end_bytes)

    def str_write(self, schars) -> None:
        """Write Chars to the Screen, but without implicitly also writing a Line-End afterwards"""

        sbytes = schars.encode()
        self.bytes_write(sbytes)

    def bytes_print(self, *args, end=b"\r\n") -> None:
        """Write Bytes to the Screen as one or more Ended Lines"""

        sep = b" "
        join = sep.join(args)
        sbytes = join + end

        self.bytes_write(sbytes)

    def bytes_write(self, sbytes) -> None:
        """Write Bytes to the Screen, but without implicitly also writing a Line-End afterwards"""

        assert self.tcgetattr_else, (self.tcgetattr_else,)

        fd = self.fd
        sbytes_list = self.sbytes_list

        sbytes_list.append(sbytes)
        os.write(fd, sbytes)

        # doesn't raise UnicodeEncodeError
        # called with end=b"" to write without adding b"\r\n"
        # called with end=b"n" to add b"\n" in place of b"\r\n"

    #
    # Read Key Chords as 1 or more Keyboard Bytes
    #

    def pull_kchord_bytes_if(self, timeout) -> bytes:
        """Read, and record, the Bytes of 1 Incomplete/ Complete Key Chord"""

        kbytes_list = self.kbytes_list

        kbytes = self.read_kchord_bytes_if(timeout=timeout)
        kbytes_list.append(kbytes)

        return kbytes

    def read_kchord_bytes_if(self, timeout) -> bytes:
        """Read the Bytes of 1 Incomplete/ Complete Key Chord, without recording them"""

        assert ESC == "\x1B"
        assert CSI == "\x1B" "["
        assert SS3 == "\x1B" "O"

        # Block to fetch at least 1 Byte

        kbytes1 = self.read_kchar_bytes_if()  # for .read_kchord_bytes_if

        many_kbytes = kbytes1
        if kbytes1 != b"\x1B":
            return many_kbytes

        # Accept 1 or more Esc Bytes, such as x 1B 1B in ⌥⌃FnDelete

        while True:
            if not self.kbhit(timeout=timeout):
                return many_kbytes

                # 1st loop:  ⎋ Esc that isn't ⎋⎋ Meta Esc
                # 2nd loop:  ⎋⎋ Meta Esc that doesn't come with more Bytes

            kbytes2 = self.read_kchar_bytes_if()  # for .read_kchord_bytes_if
            many_kbytes += kbytes2
            if kbytes2 != b"\x1B":
                break

        if kbytes2 == b"O":  # 01/11 04/15 SS3
            kbytes3 = self.read_kchar_bytes_if()  # for .read_kchord_bytes_if
            many_kbytes += kbytes3  # rarely in range(0x20, 0x40) CSI_EXTRAS
            return many_kbytes

        # Accept ⎋[ Meta [ cut short by itself, or longer CSI Escape Sequences

        if kbytes2 == b"[":  # 01/11 ... 05/11 CSI
            assert many_kbytes.endswith(b"\x1B\x5B"), (many_kbytes,)
            if not self.kbhit(timeout=timeout):
                return many_kbytes

                # ⎋[ Meta Esc that doesn't come with more Bytes

            many_kbytes = self.read_csi_kchord_bytes_if(many_kbytes)

        # Succeed

        return many_kbytes

        # cut short by end-of-input, or by undecodable Bytes
        # doesn't raise UnicodeDecodeError

    def read_csi_kchord_bytes_if(self, kbytes) -> bytes:
        """Block to read the rest of 1 CSI Escape Sequence"""

        assert CSI_EXTRAS == "".join(chr(_) for _ in range(0x20, 0x40))

        many_kchord_bytes = kbytes
        while True:
            kbytes_ = self.read_kchar_bytes_if()  # for .read_kchord_bytes_if via .read_csi_...
            many_kchord_bytes += kbytes_

            if len(kbytes_) == 1:  # as when ord(kbytes_.encode()) < 0x80
                kord = kbytes_[-1]
                if 0x20 <= kord < 0x40:  # !"#$%&'()*+,-./0123456789:;<=>?
                    continue  # Parameter/ Intermediate Bytes in CSI_EXTRAS

            break

        return many_kchord_bytes

        # continues indefinitely while next Bytes in CSI_EXTRAS
        # cut short by end-of-input, or by undecodable Bytes
        # doesn't raise UnicodeDecodeError

        # todo: limit the length of the CSI Escape Sequence

    def read_kchar_bytes_if(self) -> bytes:
        """Read the Bytes of 1 Incomplete/ Complete Char from Keyboard"""

        def decodable(kbytes: bytes) -> bool:
            try:
                kbytes.decode()  # may raise UnicodeDecodeError
                return True
            except UnicodeDecodeError:
                return False

        kbytes = b""
        while True:  # till KChar Bytes complete
            kbyte = self.read_kbyte()  # for .read_kchar_bytes_if  # todo: test end-of-input
            assert kbyte, (kbyte,)
            kbytes += kbyte

            if not decodable(kbytes):  # todo: invent Unicode Ord > 0x110000
                suffixes = (b"\x80", b"\x80\x80", b"\x80\x80\x80")
                if any(decodable(kbytes + _) for _ in suffixes):
                    continue

            break

        assert kbytes  # todo: test end-of-input

        return kbytes

        # cut short by end-of-input, or by undecodable Bytes
        # doesn't raise UnicodeDecodeError

    def read_kbyte(self) -> bytes:
        """Read 1 Keyboard Byte"""

        fd = self.fd
        assert self.tcgetattr_else, (self.tcgetattr_else,)

        self.bytes_flush()  # for 'read_kbyte'
        kbyte = os.read(fd, 1)  # 1 or more Bytes, begun as 1 Byte

        return kbyte

        # ⌃C comes through as b"\x03" and doesn't raise KeyboardInterrupt
        # ⌥Y often comes through as \ U+005C Reverse-Solidus aka Backslash

    def kbhit(self, timeout) -> bool:  # 'timeout' in seconds - 0 for now, None for forever
        """Block till next Input Byte, else till Timeout, else till forever"""

        fd = self.fd
        assert self.tcgetattr_else, (
            self.tcgetattr_else,
        )  # todo: when kbhit says if readline won't block

        (r, w, x) = select.select([fd], [], [], timeout)
        hit = fd in r

        return hit

    #
    # Emulate a more functional Terminal
    #

    def columns_delete_n(self, n) -> None:  # a la VT420 DECDC ⎋['~
        """Delete N Columns (but snap the Cursor back to where it started)"""

        fd = self.fd

        assert DCH_X == "\x1B" "[" "{}P"  # CSI 05/00 Delete Character
        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

        (x_columns, y_rows) = os.get_terminal_size(fd)
        (y_row, x_column) = self.write_dsr_read_kcpr_y_x()

        for y in range(1, y_rows + 1):
            ctext = "\x1B" "[" f"{y}d"
            ctext += "\x1B" "[" f"{n}P"
            self.str_write(ctext)

        ctext = "\x1B" "[" f"{y_row}d"
        self.str_write(ctext)

    def columns_insert_n(self, n) -> None:  # a la VT420 DECIC ⎋['}
        """Insert N Columns (but snap the Cursor back to where it started)"""

        fd = self.fd

        assert ICH_X == "\x1B" "[" "{}@"  # CSI 04/00 Insert Character
        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

        (x_columns, y_rows) = os.get_terminal_size(fd)
        (y_row, x_column) = self.write_dsr_read_kcpr_y_x()

        for y in range(1, y_rows + 1):
            ctext = "\x1B" "[" f"{y}d"
            ctext += "\x1B" "[" f"{n}@"
            self.str_write(ctext)

        ctext = "\x1B" "[" f"{y_row}d"
        self.str_write(ctext)

    def write_dsr_read_kcpr_y_x(self) -> tuple[int, int]:  # todo: mix well with other reader/ writer
        """Write 1 Device-Status-Request (DSR), read 1 Cursor-Position-Report (KCPR)"""

        fd = self.fd

        assert DSR_6 == "\x1B" "[" "6n"  # CSI 06/14 DSR  # Ps 6 for CPR
        self.str_write("\x1B" "[" "6n")

        assert CPR_Y_X_REGEX == r"^\x1B\[([0-9]+);([0-9]+)R$"  # CSI 05/02 CPR

        csi_kbytes = os.read(fd, 2)
        assert csi_kbytes == b"\x1B[", (csi_kbytes,)

        y_kbytes = b""
        while True:
            kbyte = os.read(fd, 1)
            if kbyte not in b"0123456789":
                break
            y_kbytes += kbyte

        assert kbyte == b";"

        x_kbytes = b""
        while True:
            kbyte = os.read(fd, 1)
            if kbyte not in b"0123456789":
                break
            x_kbytes += kbyte

        assert kbyte == b"R"

        row_y = int(y_kbytes)
        column_x = int(x_kbytes)

        return (row_y, column_x)


# Name the Shifting Keys
# Meta hides inside macOS Terminal > Settings > Keyboard > Use Option as Meta Key

Meta = unicodedata.lookup("Broken Circle With Northwest Arrow")  # ⎋
Control = unicodedata.lookup("Up Arrowhead")  # ⌃
Option = unicodedata.lookup("Option Key")  # ⌥
Shift = unicodedata.lookup("Upwards White Arrow")  # ⇧
Command = unicodedata.lookup("Place of Interest Sign")  # ⌘  # Super  # Windows
# 'Fn'


# Define ⌃Q ⌃V and ⌃V ⌃Q
# to strongly abbreviate a few of the KCAP_BY_KCHARS Values

KCAP_QUOTE_BY_STR = {
    "Delete": unicodedata.lookup("Erase To The Left"),  # ⌫
    "Return": unicodedata.lookup("Return Symbol"),  # ⏎
    "Spacebar": unicodedata.lookup("Bottom Square Bracket"),  # ⎵  # ␣ Open Box
    "Tab": unicodedata.lookup("Rightwards Arrow To Bar"),  # ⇥
    "⇧Tab": unicodedata.lookup("Leftwards Arrow To Bar"),  # ⇤
}


# Encode each Key Chord as a Str without a " " Space in it

KCAP_SEP = " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc

KCAP_BY_KCHARS = {
    "\x00": "⌃Spacebar",  # ⌃@  # ⌃⇧2
    "\x09": "Tab",  # '\t' ⇥
    "\x0D": "Return",  # '\r' ⏎
    "\x1B": "⎋",  # Esc  # Meta  # includes ⎋Spacebar ⎋Tab ⎋Return ⎋Delete without ⌥
    "\x1B" "\x01": "⌥⇧Fn←",  # ⎋⇧Fn←   # coded with ⌃A
    "\x1B" "\x03": "⎋FnReturn",  # coded with ⌃C  # not ⌥FnReturn
    "\x1B" "\x04": "⌥⇧Fn→",  # ⎋⇧Fn→   # coded with ⌃D
    "\x1B" "\x0B": "⌥⇧Fn↑",  # ⎋⇧Fn↑   # coded with ⌃K
    "\x1B" "\x0C": "⌥⇧Fn↓",  # ⎋⇧Fn↓  # coded with ⌃L
    "\x1B" "\x10": "⎋⇧Fn",  # ⎋ Meta ⇧ Shift of Fn F1..F12  # not ⌥⇧Fn  # coded with ⌃P
    "\x1B" "\x1B": "⎋⎋",  # Meta Esc  # not ⌥⎋
    "\x1B" "\x1B" "[" "3;5~": "⎋⌃FnDelete",  # ⌥⌃FnDelete  # LS1R
    "\x1B" "\x1B" "[" "A": "⎋↑",  # CSI 04/01 Cursor Up (CUU)  # not ⌥↑
    "\x1B" "\x1B" "[" "B": "⎋↓",  # CSI 04/02 Cursor Down (CUD)  # not ⌥↓
    "\x1B" "\x1B" "[" "Z": "⎋⇧Tab",  # ⇤  # CSI 05/10 CBT  # not ⌥⇧Tab
    "\x1B" "\x28": "⎋FnDelete",  # not ⌥⎋FnDelete
    "\x1B" "OP": "F1",  # ESC 04/15 Single-Shift Three (SS3)  # SS3 ⇧P
    "\x1B" "OQ": "F2",  # SS3 ⇧Q
    "\x1B" "OR": "F3",  # SS3 ⇧R
    "\x1B" "OS": "F4",  # SS3 ⇧S
    "\x1B" "[" "15~": "F5",  # CSI 07/14 Locking-Shift One Right (LS1R)
    "\x1B" "[" "17~": "F6",  # ⌥F1  # ⎋F1  # LS1R
    "\x1B" "[" "18~": "F7",  # ⌥F2  # ⎋F2  # LS1R
    "\x1B" "[" "19~": "F8",  # ⌥F3  # ⎋F3  # LS1R
    "\x1B" "[" "1;2C": "⇧→",  # CSI 04/03 Cursor [Forward] Right (CUF_YX) Y=1 X=2
    "\x1B" "[" "1;2D": "⇧←",  # CSI 04/04 Cursor [Back] Left (CUB_YX) Y=1 X=2
    "\x1B" "[" "20~": "F9",  # ⌥F4  # ⎋F4  # LS1R
    "\x1B" "[" "21~": "F10",  # ⌥F5  # ⎋F5  # LS1R
    "\x1B" "[" "23~": "F11",  # ⌥F6  # ⎋F6  # LS1R  # macOS takes F11
    "\x1B" "[" "24~": "F12",  # ⌥F7  # ⎋F7  # LS1R
    "\x1B" "[" "25~": "⇧F5",  # ⌥F8  # ⎋F8  # LS1R
    "\x1B" "[" "26~": "⇧F6",  # ⌥F9  # ⎋F9  # LS1R
    "\x1B" "[" "28~": "⇧F7",  # ⌥F10  # ⎋F10  # LS1R
    "\x1B" "[" "29~": "⇧F8",  # ⌥F11  # ⎋F11  # LS1R
    "\x1B" "[" "31~": "⇧F9",  # ⌥F12  # ⎋F12  # LS1R
    "\x1B" "[" "32~": "⇧F10",  # LS1R
    "\x1B" "[" "33~": "⇧F11",  # LS1R
    "\x1B" "[" "34~": "⇧F12",  # LS1R
    "\x1B" "[" "3;2~": "⇧FnDelete",  # LS1R
    "\x1B" "[" "3;5~": "⌃FnDelete",  # LS1R
    "\x1B" "[" "3~": "FnDelete",  # LS1R
    "\x1B" "[" "5~": "⇧Fn↑",
    "\x1B" "[" "6~": "⇧Fn↓",
    "\x1B" "[" "A": "↑",  # CSI 04/01 Cursor Up (CUU)
    "\x1B" "[" "B": "↓",  # CSI 04/02 Cursor Down (CUD)
    "\x1B" "[" "C": "→",  # CSI 04/03 Cursor Right [Forward] (CUF)
    "\x1B" "[" "D": "←",  # CSI 04/04 Cursor [Back] Left (CUB)
    "\x1B" "[" "F": "⇧Fn→",  # CSI 04/06 Cursor Preceding Line (CPL)
    "\x1B" "[" "H": "⇧Fn←",  # CSI 04/08 Cursor Position (CUP)
    "\x1B" "[" "Z": "⇧Tab",  # ⇤  # CSI 05/10 Cursor Backward Tabulation (CBT)
    "\x1B" "b": "⌥←",  # ⎋B  # ⎋←  # Emacs M-b Backword-Word
    "\x1B" "f": "⌥→",  # ⎋F  # ⎋→  # Emacs M-f Forward-Word
    "\x20": "Spacebar",  # ' ' ␠ ␣ ␢
    "\x7F": "Delete",  # ␡ ⌫ ⌦
    "\xA0": "⌥Spacebar",  # '\N{No-Break Space}'
}

assert list(KCAP_BY_KCHARS.keys()) == sorted(KCAP_BY_KCHARS.keys())

assert KCAP_SEP == " "
for _KCAP in KCAP_BY_KCHARS.values():
    assert " " not in _KCAP, (_KCAP,)

# the ⌥⇧Fn Key Cap quotes only the Shifting Keys, drops the substantive final Key Cap,
# except that ⎋⇧Fn← ⎋⇧Fn→ ⎋⇧Fn↑ ⎋⇧Fn also exist


OPTION_KSTR_BY_1_KCHAR = {
    "á": "⌥EA",  # E
    "é": "⌥EE",
    "í": "⌥EI",
    # without the "j́" of ⌥EJ here (because its Combining Accent comes after as a 2nd K Char)
    "ó": "⌥EO",
    "ú": "⌥EU",
    "´": "⌥ESpacebar",
    "é": "⌥EE",
    "â": "⌥IA",  # I
    "ê": "⌥IE",
    "î": "⌥II",
    "ô": "⌥IO",
    "û": "⌥IU",
    "ˆ": "⌥ISpacebar",
    "ã": "⌥NA",  # N
    "ñ": "⌥NN",
    "õ": "⌥NO",
    "˜": "⌥NSpacebar",
    "ä": "⌥UA",  # U
    "ë": "⌥UE",
    "ï": "⌥UI",
    "ö": "⌥UO",
    "ü": "⌥UU",
    "ÿ": "⌥UY",
    "¨": "⌥USpacebar",
    "à": "⌥`A",  # `
    "è": "⌥`E",
    "ì": "⌥`I",
    "ò": "⌥`O",
    "ù": "⌥`U",
    "`": "⌥`Spacebar",  # comes out as ⌥~
}

# hand-sorted by ⌥E ⌥I ⌥N ⌥U ⌥` order


#
# the Mac US English Terminal Keyboard choice of Option + Printable-US-Ascii
#


#
#   ! " # $ % & ' ( ) * + , - . / 0 1 2 3 4 5 6 7 8 9 : ; < = > ?
# @ A B C D E F G H I J K L M N O P Q R S T U V W X Y Z [ \ ] ^ _
# ` a b c d e f g h i j k l m n o p q r s t u v w x y z { | } ~
#

#
# ⌥Spacebar ⌥! ⌥" ⌥# ⌥$ ⌥% ⌥& ⌥' ⌥( ⌥) ⌥* ⌥+ ⌥, ⌥- ⌥. ⌥/
# ⌥0 ⌥1 ⌥2 ⌥3 ⌥4 ⌥5 ⌥6 ⌥7 ⌥8 ⌥9 ⌥: ⌥; ⌥< ⌥= ⌥> ⌥?
# ⌥@ ⌥⇧A ⌥⇧B ⌥⇧C ⌥⇧D ⌥⇧E ⌥⇧F ⌥⇧G ⌥⇧H ⌥⇧I ⌥⇧J ⌥⇧K ⌥⇧L ⌥⇧M ⌥⇧N ⌥⇧O
# ⌥⇧P ⌥⇧Q ⌥⇧R ⌥⇧S ⌥⇧T ⌥⇧U ⌥⇧V ⌥⇧W ⌥⇧X ⌥⇧Y ⌥⇧Z ⌥[ ⌥\ ⌥] ⌥^ ⌥_
# ⌥` ⌥A ⌥B ⌥C ⌥D ⌥E ⌥F ⌥G ⌥H ⌥I ⌥J ⌥K ⌥L ⌥M ⌥N ⌥O
# ⌥P ⌥Q ⌥R ⌥S ⌥T ⌥U ⌥V ⌥W ⌥X ⌥Y ⌥Z ⌥{ ⌥| ⌥} ⌥~
#

#
# ⎋Spacebar ⎋! ⎋" ⎋# ⎋$ ⎋% ⎋& ⎋' ⎋( ⎋) ⎋* ⎋+ ⎋, ⎋- ⎋. ⎋/
# ⎋0 ⎋1 ⎋2 ⎋3 ⎋4 ⎋5 ⎋6 ⎋7 ⎋8 ⎋9 ⎋: ⎋; ⎋< ⎋= ⎋> ⎋?
# ⎋@ ⎋⇧A ⎋⇧B ⎋⇧C ⎋⇧D ⎋⇧E ⎋⇧F ⎋⇧G ⎋⇧H ⎋⇧I ⎋⇧J ⎋⇧K ⎋⇧L ⎋⇧M ⎋⇧N ⎋⇧O
# ⎋⇧P ⎋⇧Q ⎋⇧R ⎋⇧S ⎋⇧T ⎋⇧U ⎋⇧V ⎋⇧W ⎋⇧X ⎋⇧Y ⎋⇧Z ⎋[ ⎋\ ⎋] ⎋^ ⎋_
# ⎋` ⎋A ⎋B ⎋C ⎋D ⎋E ⎋F ⎋G ⎋H ⎋I ⎋J ⎋K ⎋L ⎋M ⎋N ⎋O
# ⎋P ⎋Q ⎋R ⎋S ⎋T ⎋U ⎋V ⎋W ⎋X ⎋Y ⎋Z ⎋{ ⎋| ⎋} ⎋~
#


OPTION_KTEXT = """
     ⁄Æ‹›ﬁ‡æ·‚°±≤–≥÷º¡™£¢∞§¶•ªÚ…¯≠˘¿
    €ÅıÇÎ Ï˝Ó Ô\uF8FFÒÂ Ø∏Œ‰Íˇ ◊„˛Á¸“«‘ﬂ—
     å∫ç∂ ƒ©˙ ∆˚¬µ øπœ®ß† √∑≈¥Ω”»’
"""

# ⌥⇧K is Apple Icon  is \uF8FF is in the U+E000..U+F8FF Private Use Area (PUA)

OPTION_KCHARS = " " + textwrap.dedent(OPTION_KTEXT).strip() + " "
OPTION_KCHARS = OPTION_KCHARS.replace("\n", "")

assert len(OPTION_KCHARS) == (0x7E - 0x20) + 1

OPTION_KCHARS_SPACELESS = OPTION_KCHARS.replace(" ", "")


# Give out each Key Cap once, never more than once

_KCHARS_LISTS = [
    list(KCAP_BY_KCHARS.keys()),
    list(OPTION_KSTR_BY_1_KCHAR.keys()),
    list(OPTION_KCHARS_SPACELESS),
]

_KCHARS_LIST = list(_KCHARS for _KL in _KCHARS_LISTS for _KCHARS in _KL)
assert KCAP_SEP == " "
for _KCHARS, _COUNT in collections.Counter(_KCHARS_LIST).items():
    assert _COUNT == 1, (_COUNT, _KCHARS)


class ChordsKeyboard:
    """Read Combinations of Key Caps from a BytesTerminal, mixed with Inband Signals"""

    bt: BytesTerminal

    y_rows: int  # -1, then Count of Screen Rows
    x_columns: int  # -1, then Count of Screen Columns

    row_y: int  # -1, then Row of Cursor
    column_x: int  # -1, then Column of Cursor

    kchords: list[tuple[bytes, str]]  # Key Chords read ahead after DSR until CPR

    #
    # Init, Enter, and Exit
    #

    def __init__(self, bt) -> None:

        self.bt = bt
        self.y_rows = -1
        self.x_columns = -1
        self.row_y = -1
        self.column_x = -1
        self.kchords = list()

    def __enter__(self) -> "ChordsKeyboard":  # -> typing.Self:

        return self

    def __exit__(self, *exc_info) -> None:

        bt = self.bt
        kchords = self.kchords

        if kchords:
            bt.bytes_print()
            while kchords:
                (kbytes, kstr) = kchords.pop(0)
                encode = kstr.encode()
                bt.bytes_print(encode)

    #
    # Read Key Chords from Keyboard or Screen
    #

    def read_kchord(self, timeout) -> tuple[bytes, str]:
        """Read 1 Key Chord, but accept Cursor-Position-Report (KCPR's) if they come first"""

        kchords = self.kchords

        while not self.read_kchord_or(timeout=timeout):
            pass

            # todo: log how rarely CPR's come here

        kchord = kchords.pop(0)

        return kchord

    def read_kchord_or(self, timeout) -> bool:
        """Do read something, and return True if it was a Key Chord"""

        bt = self.bt
        kchords = self.kchords

        assert CPR_Y_X_REGEX == r"^\x1B\[([0-9]+);([0-9]+)R$"  # CSI 05/02 CPR

        # Read something

        kbytes = bt.pull_kchord_bytes_if(timeout=timeout)  # may contain b' ' near to KCAP_SEP
        kchars = kbytes.decode()  # may raise UnicodeDecodeError

        # Return True if it was a Key Chord

        m = re.match(r"^\x1B\[([0-9]+);([0-9]+)R$", string=kchars)
        if not m:
            kchord = self.kbytes_to_kchord(kbytes)
            kchords.append(kchord)
            return True

        # Interpret the KCPR

        row_y = int(m.group(1))
        column_x = int(m.group(2))

        assert row_y >= 1, (row_y,)
        assert column_x >= 1, (column_x,)

        self.row_y_column_x_report(row_y, column_x=column_x)

        # Admit it was not a Key Chord

        return False

    def row_y_column_x_report(self, row_y, column_x) -> None:
        """Say which Row & Column is the Cursor's Row & Column"""

        self.row_y = row_y
        self.column_x = column_x

    def kbytes_to_kchord(self, kbytes) -> tuple[bytes, str]:
        """Choose 1 Key Cap to speak of the Bytes of 1 Key Chord"""

        kchars = kbytes.decode()  # may raise UnicodeDecodeError

        kcap_by_kchars = KCAP_BY_KCHARS  # '\e\e[A' for ⎋↑ etc

        if kchars in kcap_by_kchars.keys():
            kstr = kcap_by_kchars[kchars]
        else:
            kstr = ""
            for kch in kchars:  # often 'len(kchars) == 1'
                s = self.kch_to_kcap(kch)
                kstr += s

                # '⎋[25;80R' Cursor-Position-Report (CPR)
                # '⎋[25;80t' Rows x Column Terminal Size Report
                # '⎋[200~' and '⎋[201~' before/ after Paste to bracket it

            # ⌥Y often comes through as \ U+005C Reverse-Solidus aka Backslash

        # Succeed

        assert KCAP_SEP == " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc
        assert " " not in kstr, (kstr,)

        return (kbytes, kstr)

        # '⌃L'  # '⇧Z'
        # '⎋A' from ⌥A while macOS Keyboard > Option as Meta Key

    def kch_to_kcap(self, ch) -> str:  # noqa C901
        """Choose a Key Cap to speak of 1 Char read from the Keyboard"""

        o = ord(ch)

        option_kchars = OPTION_KCHARS  # '∂' for ⌥D
        option_kchars_spaceless = OPTION_KCHARS_SPACELESS  # '∂' for ⌥D
        option_kstr_by_1_kchar = OPTION_KSTR_BY_1_KCHAR  # 'é' for ⌥EE
        kcap_by_kchars = KCAP_BY_KCHARS  # '\x7F' for 'Delete'

        # Show more Key Caps than US-Ascii mentions

        if ch in kcap_by_kchars.keys():  # Mac US Key Caps for Spacebar, F12, etc
            s = kcap_by_kchars[ch]

        elif ch in option_kstr_by_1_kchar.keys():  # Mac US Option Accents
            s = option_kstr_by_1_kchar[ch]

        elif ch in option_kchars_spaceless:  # Mac US Option Key Caps
            index = option_kchars.index(ch)
            asc = chr(0x20 + index)
            if "A" <= asc <= "Z":
                asc = "⇧" + asc  # '⇧A'
            if "a" <= asc <= "z":
                asc = chr(ord(asc) ^ 0x20)  # 'A'
            s = "⌥" + asc  # '⌥⇧P'

        # Show the Key Caps of US-Ascii, plus the ⌃ ⇧ Control/ Shift Key Caps

        elif (o < 0x20) or (o == 0x7F):  # C0 Control Bytes, or \x7F Delete (DEL)
            s = "⌃" + chr(o ^ 0x40)  # '⌃@' from b'\x00'
        elif "A" <= ch <= "Z":  # printable Upper Case English
            s = "⇧" + chr(o)  # shifted Key Cap '⇧A' from b'A'
        elif "a" <= ch <= "z":  # printable Lower Case English
            s = chr(o ^ 0x20)  # plain Key Cap 'A' from b'a'

        # Test that no Keyboard sends the C1 Control Bytes, nor the Quasi-C1 Bytes

        elif o in range(0x80, 0xA0):  # C1 Control Bytes
            assert False, (o, ch)
        elif o == 0xA0:  # 'No-Break Space'
            s = "⌥Spacebar"
            assert False, (o, ch)  # unreached because 'kcap_by_kchars'
        elif o == 0xAD:  # 'Soft Hyphen'
            assert False, (o, ch)

        # Show the US-Ascii or Unicode Char as if its own Key Cap

        else:
            assert o < 0x11_0000, (o, ch)
            s = chr(o)  # '!', '¡', etc

        # Succeed, but insist that Blank Space is never a Key Cap

        assert s.isprintable(), (s, o, ch)  # has no \x00..\x1F, \x7F, \xA0, \xAD, etc
        assert " " not in s, (s, o, ch)

        return s

        # '⌃L'  # '⇧Z'

    def read_row_y_column_x(self, timeout) -> tuple[int, int]:
        """Sample Cursor Row & Column"""

        bt = self.bt

        assert DSR_6 == "\x1B" "[" "6n"  # CSI 06/14 DSR  # Ps 6 for CPR

        encode = ("\x1B" "[" "6n").encode()
        bt.bytes_write(encode)

        while self.read_kchord_or(timeout=timeout):
            pass

            # todo: log how rarely anything but CPR comes after DSR
            # todo: hangs if CPR never comes, despite DSR

        row_y = self.row_y
        column_x = self.column_x

        assert row_y >= 1, (row_y,)
        assert column_x >= 1, (column_x,)

        return (row_y, column_x)

    def read_y_rows_x_columns(self, timeout) -> tuple[int, int]:
        """Sample Counts of Screen Rows and Columns"""

        bt = self.bt

        fd = bt.fd
        (x_columns, y_rows) = os.get_terminal_size(fd)

        assert y_rows >= 5, (y_rows,)  # macOS Terminal min 5 Rows
        assert x_columns >= 20, (x_columns,)  # macOS Terminal min 20 Columns

        self.y_rows = y_rows
        self.x_columns = x_columns

        return (y_rows, x_columns)


class ShadowsTerminal:
    """Write/ Read Chars at Screen/ Keyboard of a Monospaced Square'ish Terminal"""

    bt: BytesTerminal
    ck: ChordsKeyboard

    #
    # Init, enter, exit
    #

    def __init__(self) -> None:
        bt = BytesTerminal()
        self.bt = bt
        self.ck = ChordsKeyboard(bt)

    def __enter__(self) -> "ShadowsTerminal":  # -> typing.Self:
        self.bt.__enter__()
        self.ck.__enter__()
        return self

    def __exit__(self, *exc_info) -> None:
        self.ck.__exit__()
        self.bt.__exit__()

    def str_print(self, *args, end="\r\n") -> None:
        bt = self.bt
        bt.str_print(*args, end=end)


#
# Trade Texts across a pair of Named Pipes at macOS or Linux
#


class TurtlingFifoProxy:
    """Create/ find a Named Pipe and write/ read it"""

    basename: str  # 'requests'

    find: str  # '__pycache__/turtling/pid=12345/responses.mkfifo'
    pid: int  # 12345
    fd: int  # 3
    index: int  # -1

    def __init__(self, basename) -> None:

        assert basename in ("requests", "responses"), (basename,)

        self.basename = basename

        self.find = ""
        self.pid = -1
        self.fd = -1
        self.index = -1

    def pid_create_dir_once(self, pid) -> None:
        """Create 1 Working Dir"""

        assert self.pid in (-1, pid), (self.pid, pid)

        if not os.path.exists("__pycache__"):
            os.mkdir("__pycache__")
        if not os.path.exists("__pycache__/turtling"):
            os.mkdir("__pycache__/turtling")

        dirfind = f"__pycache__/turtling/pid={pid}"
        if os.path.exists(dirfind):  # wildly rare
            eprint(f"shutil.rmtree {dirfind=}", end="\r\n")
            shutil.rmtree(dirfind)

        os.mkdir(dirfind)

    def create_mkfifo_once(self, pid) -> None:
        """Create 1 Named Pipe, like as a promise to write or read it soon"""

        assert pid >= 0, (pid,)

        basename = self.basename
        find = self.find

        if find:
            return

        self.pid = pid

        # Create 1 Named Pipe once

        find = f"__pycache__/turtling/pid={pid}/{basename}.mkfifo"
        os.mkfifo(find)

        self.find = find

    def find_mkfifo_once_if(self, pid) -> bool:
        """Find 1 Named Pipe served by a Process Pid, else return False"""

        assert pid, (pid,)
        assert isinstance(pid, int) or (pid == "*"), (pid,)

        basename = self.basename
        find = self.find

        # Don't look past the first Pipe found

        if find:
            return True

        assert self.pid == -1, (self.pid,)

        # Say no Pipes found

        pattern = f"__pycache__/turtling/pid={pid}/{basename}.mkfifo"
        unsorted_finds = list(glob.glob(pattern))
        if not unsorted_finds:
            return False

        # Say the last-modified Pipe has no Process at the far end of it

        finds = sorted(unsorted_finds, key=lambda _: pathlib.Path(_).stat().st_mtime)

        find = finds[-1]
        str_pid = find.partition("/pid=")[-1].split("/")[0]
        int_pid = int(str_pid)

        run = subprocess.run(shlex.split(f"kill -0 {int_pid}"), stderr=subprocess.PIPE)
        if run.returncode:  # macOS 'kill -0' can spend 6ms
            return False

        # Remember success

        self.pid = int_pid
        self.find = find

        # Succeed

        return True

    def write_text(self, text) -> None:
        """Write Chars out as an indexed Packet that starts with its own Length"""

        if self.fd < 0:
            self.fd_open_write_once()
            assert self.fd >= 0, (self.fd,)

        self.fd_write_text(self.fd, text=text)

    def fd_open_write_once(self) -> int:
        """Open to write, if not open already. Block till a Reader opens the same Pipe"""

        find = self.find
        fd = self.fd
        assert find, (find,)

        if fd >= 0:
            return fd

        fd = os.open(find, os.O_WRONLY)
        assert fd >= 0

        self.fd = fd

        return fd

    def fd_write_text(self, fd, text) -> None:
        """Write Chars out as an indexed Packet that starts with its own Length"""

        assert text is not None, (text,)

        index = self.index
        self.index = index + 1

        tail = f"index={index}\ntext={text}\n"
        tail_encode = tail.encode()

        blank_head_encode = f"length=0x{0:019_X}\n".encode()
        encode_length = len(blank_head_encode) + len(tail_encode)

        head_encode = f"length=0x{encode_length:019_X}\n".encode()
        encode = head_encode + tail_encode

        os.write(fd, encode)  # todo: no need for .fdopen .flush?

    def read_text_else(self) -> str | None:
        """Read Chars in as an indexed Request that starts with its own Length"""

        if self.fd < 0:
            self.fd_open_read_once()
            assert self.fd >= 0, (self.fd,)

        rtext_else = self.fd_read_text_else(self.fd)
        return rtext_else

    def fd_open_read_once(self) -> int:
        """Open to read, if not open already. Block till a Writer opens the same Pipe"""

        find = self.find
        fd = self.fd
        assert find, (find,)

        if fd >= 0:
            return fd

        fd = os.open(find, os.O_RDONLY)
        assert fd >= 0

        self.fd = fd

        return fd

    def fd_read_text_else(self, fd) -> str | None:
        """Read Chars in as an indexed Request that starts with its own Length"""

        index = self.index
        self.index = index + 1

        # Read the Bytes of the Chars

        blank_head_encode = f"length=0x{0:019_X}\n".encode()
        len_head_bytes = len(blank_head_encode)

        head_bytes = os.read(fd, len_head_bytes)
        if not head_bytes:
            return None

        assert len(head_bytes) == len_head_bytes, (len(head_bytes), len_head_bytes)
        head_text = head_bytes.decode()

        str_encode_length = head_text.partition("length=")[-1]
        encode_length = int(str_encode_length, 0x10)
        assert head_text == f"length=0x{encode_length:019_X}\n", (head_text, encode_length)

        tail_bytes_length = encode_length - len(head_bytes)
        tail_bytes = os.read(fd, tail_bytes_length)
        assert len(tail_bytes) == tail_bytes_length, (len(tail_bytes), tail_bytes_length)

        tail_text = tail_bytes.decode()

        # Pick out the Index

        stop = tail_text.index("\n") + len("\n")
        index_line = tail_text[:stop]

        # Pick out the Chars

        text_eq = tail_text[stop:]
        assert text_eq.startswith("text="), (text_eq,)
        assert text_eq.endswith("\n"), (text_eq,)

        text = text_eq
        text = text.removeprefix("text=")
        text = text.removesuffix("\n")

        # Recover Synch, if lost

        if index_line != f"index={index}\n":
            assert text == "", (text, index_line, index)

            alt_index = int(index_line.removeprefix("index="))
            assert alt_index != index, (index, alt_index)

            if index != -1:
                assert alt_index == -1, (alt_index, index)
            else:
                assert alt_index != -1, (alt_index, index)
                self.index = alt_index + 1

        # Succeed

        return text

        # Named Pipes don't reliably send & receive EOF at close of File


TurtlingWriter = TurtlingFifoProxy("requests")

TurtlingReader = TurtlingFifoProxy("responses")


def turtling_server_attach() -> None:
    """Start trading Texts with a Turtling Server"""

    reader = TurtlingReader
    writer = TurtlingWriter

    if not reader.find_mkfifo_once_if(pid="*"):
        raise FileNotFoundError("No Turtling Server Started")
    assert reader.pid >= 0, (reader.pid,)

    pid = reader.pid

    if not writer.find_mkfifo_once_if(pid):
        writer.create_mkfifo_once(pid)

    writer.write_text("")
    read_text_else = reader.read_text_else()
    if read_text_else != "":
        print(repr(read_text_else))
        breakpoint()
        raise FileNotFoundError("Turtling Server Texts-Index-Synch Failed")

    assert writer.index == 0, (writer.index, reader.index)
    if reader.index != writer.index:
        assert reader.index > 0, (reader.index,)
        writer.index = reader.index


#
# Run as a Server drawing with Logo Turtles
#


def turtling_server_run() -> bool:
    "Run as a Server drawing with Logo Turtles and return True, else return False"

    with ShadowsTerminal() as st:
        ts1 = TurtlingServer(st)
        ts1.server_run_till()

    return True


class TurtlingServer:

    shadows_terminal: ShadowsTerminal
    locals_: dict[str, object]

    def __init__(self, shadows_terminal) -> None:

        locals_: dict[str, object]
        locals_ = dict()
        locals_["self"] = self

        self.shadows_terminal = shadows_terminal
        self.locals_ = locals_

    def server_run_till(self) -> None:
        """Draw with Logo Turtles"""

        st = self.shadows_terminal
        bt = st.bt  # todo: .bytes_terminal
        bt_fd = bt.fd  # todo: .file_descriptor
        ck = st.ck

        pid = os.getpid()

        writer = TurtlingFifoProxy("responses")
        reader = TurtlingFifoProxy("requests")

        # Start up

        writer.pid_create_dir_once(pid)
        writer.create_mkfifo_once(pid)

        st.str_print(f"At your service as {pid=} till you press ⌃D")

        reader_fd = -1
        while True:

            # Block till Input or Timeout

            fds = list()
            fds.append(bt_fd)
            if reader_fd >= 0:
                assert reader_fd == reader.fd, (reader_fd, reader.fd)
                fds.append(reader_fd)

            timeout = 0.100
            selects = select.select(fds, [], [], timeout)
            select_ = selects[0]

            if bt_fd in select_:
                kchord = ck.read_kchord(timeout=1)
                st.str_print(kchord)
                if kchord[-1] == "⌃D":
                    break

            if reader_fd in select_:
                self.reader_writer_serve(reader, writer=writer)
                continue

            if reader_fd < 0:
                if reader.find_mkfifo_once_if(pid):  # 0..10 ms
                    reader_fd = reader.fd_open_read_once()
                    assert reader_fd == reader.fd, (reader_fd, reader.fd)

    def reader_writer_serve(self, reader, writer) -> None:
        """Read a Python Text in, write back out the Repr of its Eval"""

        reader_fd = reader.fd

        globals_ = globals()
        locals_ = self.locals_
        st = self.shadows_terminal

        # Read a Python Text In

        rtext_else = reader.fd_read_text_else(reader_fd)
        if rtext_else is None:
            st.str_print("EOFError")
            writer.index += 1  # as if written
            return

        rtext = rtext_else

        # Eval the Python Text (except eval "" Empty Str as same)

        wtext = ""

        if rtext:
            py = rtext
            try:  # todo: shrug off PyLance pretending eval/exec 'locals=' doesn't work
                eval_ = eval(py, globals_, locals_)
            except SyntaxError:
                eval_ = None
                try:
                    exec(py, globals_, locals_)
                except Exception:
                    eval_ = traceback.format_exc()
            except Exception:
                eval_ = traceback.format_exc()

            wtext = repr(eval_)

        # Write back out the Repr of its Eval (except write back "" Empty Str for same)

        if writer.fd < 0:
            writer.fd_open_write_once()
            assert writer.fd >= 0, (writer.fd,)

        writer.fd_write_text(writer.fd, text=wtext)


#
# Run as a Client chatting with Logo Turtles
#


def turtling_client_run() -> bool:
    "Run as a Client chatting with Logo Turtles and return True, else return False"

    try:
        turtling_server_attach()
    except Exception:
        # eprint("turtling_client_run turtling_server_attach")
        # traceback.print_exc(file=sys.stderr)
        return False

    tc1 = TurtleClient()
    try:
        tc1.client_run_till()
    except BrokenPipeError:
        eprint("BrokenPipeError")

    return True


class Turtle:
    """Chat with 1 Logo Turtle"""

    def trade_text_else(self, wtext) -> str | None:
        """Write a Text to the Turtling Server, and read back a Text or None"""

        writer = TurtlingWriter
        reader = TurtlingReader

        writer.write_text(wtext)
        rtext_else = reader.read_text_else()

        return rtext_else


class TurtleClient:
    """Chat with the Logo Turtles of 1 Turtling Server"""

    def client_run_till(self) -> None:
        """Chat with Logo Turtles"""

        t1 = Turtle()

        while True:
            eprint(f"{Turtle_} ", end="")

            sys.stdout.flush()
            sys.stderr.flush()

            readline = sys.stdin.readline()
            if not readline:
                eprint("Bye")  # politely closing the line makes ⌘K work
                break

            rstrip = readline.rstrip()
            if self.text_is_pylike(rstrip):
                rtext_else = t1.trade_text_else(wtext=rstrip)
                if rtext_else is None:
                    eprint("EOFError")
                    continue

                rtext = rtext_else
                if rtext.startswith("'Traceback (most recent call last):"):
                    format_exc = eval(rtext)
                    eprint(format_exc.rstrip())
                    continue

                if rtext != "None":
                    eprint(rtext)
                    eprint()

    def text_is_pylike(self, text) -> bool:
        """Say forward to Server if more than Blanks and Comments found"""

        for line in text.splitlines():
            py = line.partition("#")[0].strip()
            if py:
                return True

        return False


#
# Paint Turtle Character Graphics onto a Terminal Screen
#


class TurtleClientWas:
    """Run at Keyboard and Screen as a Shell, to command 1 Turtle via two MkFifo"""

    ps1 = f"{Turtle_}? \x1B[1m"  # prompt for Turtle Client Shell  # \e1m Bold Sgr
    after_ps1 = "\x1B[m"  # \em Plain Sgr

    float_x: float  # sub-pixel shadow of horizontal position
    float_y: float  # sub-pixel shadow of vertical position
    heading: float  # stride direction
    stride: float  # stride size

    penmode: str  # last ⎋[m Select Graphic Rendition (SGR) chosen for PenChar
    penchar: str  # mark to print at each step
    pendown: bool  # printing marks, or not
    hiding: bool  # hiding the Turtle, or not
    sleep: float  # time between marks

    tada_func_else: typing.Callable | None  # runs once before taking next Command

    def __init__(self) -> None:

        self.reinit()

    def reinit(self) -> None:

        self.float_x = 0e0
        self.float_y = 0e0
        self.heading = 0e0  # 0° of North Up Clockwise
        self.stride = 100e0

        self.penmode = "\x1B[m"  # CSI 06/13 Select Graphic Rendition (SGR)
        self.penchar = FullBlock
        self.pendown = False
        self.hiding = False

        hertz = 1000e0
        self.sleep = 1 / hertz

        self.tada_func_else = None

        # macOS Terminal Sh launch doesn't clear the Graphic Rendition, Cursor Style, etc

    def do_reset(self) -> None:
        """Warp the Turtle to Home, but do Not clear the Screen"""

        self.reinit()
        self.do_hideturtle()
        self.do_setpencolor()
        self.do_home()
        self.do_showturtle()

        print(  # no matter if changed, or not changed
            f"heading={self.heading}"
            f" stride={self.stride}"
            f" penchar={self.penchar}"
            f" pendown={self.pendown}"
            f" sleep={self.sleep}"
        )

        py = 'self.str_write("\x1B" "[" " q")'  # CSI 02/00 07/01  # No-Style Cursor
        rep = self.py_eval_to_repr(py)
        assert not rep, (rep, py)

    def turtle_client_yolo(self) -> None:  # noqa # too complex (11  # FIXME
        """Read 1 Line, Eval it, Print its result, Loop (REPL Chat)"""

        # Cancel the Vi choice of a Cursor Style
        # Trust Vi to have already chosen ShowTurtle & no SGR

        py = 'self.str_write("\x1B" "[" " q")'  # CSI 02/00 07/01  # No-Style Cursor
        rep = self.py_eval_to_repr(py)
        assert not rep, (rep, py)

        # Prompt & read 1 Line from Keyboard, till ⌃D pressed to quit

        while True:
            print()
            print(self.ps1, end="")
            sys.stdout.flush()
            try:
                readline = sys.stdin.readline()
            except KeyboardInterrupt:  # mostly shrugs off ⌃C SigInt
                print(" KeyboardInterrupt")
                self.breakpoint()
                continue

            print(self.after_ps1, end="")

            print_if(f"{readline=}")

            if not readline:  # accepts ⌃D Tty End
                self.do_bye()
                assert False  # unreached

            # Prompt & read 1 Line from Keyboard, till ⌃D Tty End pressed to quit

            py = self.readline_to_py(readline)
            if py:
                rep = self.py_eval_to_repr(py)
                if rep:
                    if not rep.startswith("'Traceback (most recent call last):"):  # todo: weak
                        print(rep)
                    else:
                        try:
                            print(eval(rep))
                        except Exception:
                            hostname = platform.node()
                            debug = hostname.startswith("plavarre")
                            if debug:
                                traceback.print_exc()  # todo: log the Traceback of Exc
                            print(rep)

    #
    # Eval 1 Line of Input
    #

    def readline_to_py(self, readline) -> str:  # noqa C901 complex  # FIXME
        """Eval 1 Line of Input"""

        func_by_verb = self.to_func_by_verb()
        tada_func_else = self.tada_func_else

        # Drop a mostly blank Line

        strip = readline.strip()
        if not strip:
            return ""

        part = strip.partition("#")[0].strip()
        if not part:
            return ""

        # Split the 1 Line into its widest Py Expressions from the Left

        pys = list()
        tail = part
        while tail:
            prefixes = list()
            for index in range(0, len(tail)):
                length = index + 1

                prefix = tail[:length]

                evallable = prefix
                evallable = evallable.replace("-", "~")  # refuse '-' as bin op, accept as unary op
                evallable = evallable.replace("+", "~")  # refuse '+' as bin op, accept as unary op

                try:
                    ast.literal_eval(evallable)
                    # print(f"{prefix=}  # Literal")
                    prefixes.append(prefix)
                except ValueError:
                    # print(f"{prefix=}  # ValueError")
                    prefixes.append(prefix)
                except SyntaxError:
                    continue

            if not prefixes:
                # print(f"{tail=} {part=}  # no prefixes")
                return part

            py = prefixes[-1]
            pys.append(py)

            tail = tail[len(py) :]

        assert "".join(pys) == part, (pys, part)

        # print(f"{pys=}")
        # breakpoint()

        # Split the 1 Line into a Series of 1 or more Py Calls

        call: list[object | None]
        call = list()

        calls: list[list[object | None]]
        calls = list()

        calculated_call_ids = list()

        for py in pys:

            # Add a Literal Arg,
            # or guess Printing wanted if no Verb before Literal Args

            try:
                arg = ast.literal_eval(py)
                if not call:
                    call.append("print")  # todo: "printrepr" when Args of no Func?
                call.append(arg)
                continue

            # Begin again with each unquoted Verb

            except ValueError:

                word = py.strip()
                iword = word.casefold()
                if iword in func_by_verb.keys():
                    if call:
                        calls.append(call)
                        call = list()  # replace
                    call.append(py.strip())
                    continue

                # Take an eval'able Expression as its own Literal Value

                try:
                    evalled = eval(py)
                    call.append(evalled)
                    calculated_call_ids.append(id(call))
                    continue
                except Exception:
                    pass

                # Take an undefined Name as if it were a Case-Respecting Quoted String

                call.append(word)
                continue

            # Demand that no Syntax Error escaped earlier Guards

            except SyntaxError:
                assert False, (py, pys, strip)

        if call:
            calls.append(call)
            call = list()  # unneeded

        if not calls:
            return ""

        # Exit a Tada Pause between Calls

        if tada_func_else:
            tada_func = tada_func_else

            self.tada_func_else = None

            tada_func()

        # Make each Call in order

        for call in calls:
            verb = call[0]
            args = call[1:]

            if id(call) in calculated_call_ids:
                print(f"{verb}({", ".join(repr(_) for _ in args)})")

            assert verb, (verb, call, calls, readline)
            assert isinstance(verb, str), (type(verb), verb, call, calls, readline)

            iverb = verb.casefold()
            if iverb in func_by_verb:
                func = func_by_verb[iverb]
                try:
                    func(*args)

                except Exception:
                    hostname = platform.node()
                    debug = hostname.startswith("plavarre")
                    if debug:
                        traceback.print_exc()  # todo: log the Traceback of Exc
                        return ""

                    format_exc = traceback.format_exc()
                    line = format_exc.splitlines()[-1]
                    print(line)
                    return ""
            else:
                py = f"{iverb}({', '.join(repr(_) for _ in args)})"
                rep = self.py_eval_to_repr(py)
                if rep:
                    print(rep)

        # Succeed

        return ""

    def to_func_by_verb(self) -> dict[str, typing.Callable]:
        """Say how to spell each Command Verb"""

        keys = list()

        d: dict[str, typing.Callable]
        d = dict()

        func_by_join = self.to_func_by_join()
        for join, func in func_by_join.items():
            func_verbs = join.split()
            keys.extend(func_verbs)
            for verb in func_verbs:
                d[verb] = func

        collisions = list(_ for _ in collections.Counter(keys).items() if _[-1] != 1)
        assert not collisions, (collisions,)

        return d

    def to_func_by_join(self) -> dict[str, typing.Callable]:
        """Choose 1 or more spellings for each 🐢 Command Verb"""

        d: dict[str, typing.Callable]
        d = {
            "backward back bk": self.do_backward,
            "beep b": self.do_beep,
            "bye exit quit": self.do_bye,
            "clearscreen clear cls cs": self.do_clearscreen,
            "forward fd": self.do_forward,
            "help h": self.do_help,
            "home": self.do_home,
            "hideturtle ht": self.do_hideturtle,
            "label lb": self.do_label,
            "left lt": self.do_left,
            "pendown pd": self.do_pendown,
            "penup pu": self.do_penup,
            "print p": self.do_print,
            "repeat rep": self.do_repeat,
            "reset": self.do_reset,
            "right rt": self.do_right,
            "sleep s": self.do_sleep,
            "setheading seth": self.do_setheading,
            "sethertz hz": self.do_sethertz,
            "setpencolor setpc": self.do_setpencolor,
            "setpenpunch setpch": self.do_setpenpunch,
            "setxy xy": self.do_setxy,
            "showturtle st": self.do_showturtle,
            "tada t": self.do_tada,
        }

        return d

    #
    # Mess with 1 Turtle
    #

    def do_backward(self, stride=None) -> None:  # as if do_bk, do_back
        """Move the Turtle backwards along its Heading, tracing a Trail if Pen Down"""

        float_stride = self.stride if (stride is None) else float(stride)
        self.punch_bresenham_stride(-float_stride)

    def do_beep(self) -> None:
        """Ring the Terminal Alarm Bell once, remotely inside the Turtle"""

        text = "\a"  # Alarm Bell
        self.str_write(text)

        # todo: sleep here, do Not return, until after the Bell is done ringing

    def do_label(self, *args) -> None:
        """Write 0 or more Args"""

        heading = self.heading
        if round(heading) != 90:
            print("NotImplementedError: Printing Labels for Headings other than 90° East")
            return

            # todo: Printing Labels for 180° South Heading
            # todo: Printing Labels for Headings other than 90° East and 180° South

        (y_row, x_column) = self.os_terminal_y_row_x_column()

        line = " ".join(str(_) for _ in args)
        line += f"\x1B[{y_row};{x_column}H"  # CSI 06/12 Cursor Position  # 0 Tail # 1 Head # 2 Rows # 3 Columns]"
        line += "\n"  # just Line-Feed \n without Carriage-Return \r

        self.str_write(line)

        # todo: most Logo's feel the Turtle should remain unmoved after printing a Label??

    def do_bye(self) -> None:
        """Quit the Turtle Chat"""

        print("bye")  # not from "bye", "end", "exit", "quit", ...
        sys.exit()

    def do_clearscreen(self) -> None:  # as if do_cs, do_cls do_clear
        """Write Spaces over every Character of every Screen Row and Column"""

        text = "\x1B[2J"  # CSI 04/10 Erase in Display  # 0 Tail # 1 Head # 2 Rows # 3 Scrollback
        self.str_write(text)

        # just the Screen, not also its Scrollback

    def do_forward(self, stride=None) -> None:  # as if do_fd
        """Move the Turtle forwards along its Heading, tracing a Trail if Pen Down"""

        float_stride = self.stride if (stride is None) else float(stride)
        self.punch_bresenham_stride(float_stride)

    def do_help(self, pattern=None) -> None:  # as if do_h
        """List the Command Verbs"""

        (verbs, grunts) = self._sliced_to_verbs_grunts_(pattern)
        if not verbs:
            assert not grunts, (pattern, verbs, grunts)
            print(f"Chars {pattern!r} not found in Turtle Command Verbs")
            return

        if not pattern:
            verbs.remove("bye")  # drops test-ending 'bye' etc from tests of almost-all Verbs
            grunts.remove("exit")
            grunts.remove("quit")

        print("Choose from:", ", ".join(sorted(verbs)))
        print("Or abbreviated as:", ", ".join(sorted(grunts)))

    def _sliced_to_verbs_grunts_(self, pattern) -> tuple[list[str], list[str]]:
        """List the Abbreviations or Verbs that contain the Arg"""  # pattern=None matches All Verbs

        func_by_join = self.to_func_by_join()

        verbs = list()
        grunts = list()
        for join, func in func_by_join.items():
            func_verbs = join.split()
            verbs.append(func_verbs[0])
            grunts.extend(func_verbs[1:])

        if pattern is not None:
            verbs[::] = list(_ for _ in verbs if pattern in _)
            grunts[::] = list(_ for _ in grunts if pattern in _)

        return (verbs, grunts)

    def do_home(self) -> None:
        """Move the Turtle to its Home and turn it North, tracing a Trail if Pen Down"""

        self.do_setxy()  # todo: different Homes for different Turtles
        self.do_setheading()

    def do_hideturtle(self) -> None:  # as if do_ht
        """Stop showing where the Turtle is"""

        hiding = self.hiding

        text = "\x1B[?25l"  # 06/12 Reset Mode (RM) 25 VT220 DECTCEM
        self.str_write(text)

        self.hiding = True
        if self.hiding != hiding:
            print(f"hiding={self.hiding}  # was {hiding}")

    def do_left(self, angle=None) -> None:  # as if do_lt
        """Turn the Turtle anticlockwise, by a 90° Right Angle, or some other Angle"""

        heading = self.heading  # turning anticlockwise

        float_angle = 90e0 if (angle is None) else float(angle)
        self.heading = (heading - float_angle) % 360  # 360° Circle
        if self.heading != heading:
            print(f"heading={self.heading}{DegreeSign}  # was {heading}{DegreeSign}")

    def do_pendown(self) -> None:  # as if do_pd
        """Plan to leave a Trail as the Turtle moves"""

        pendown = self.pendown
        self.pendown = True
        if self.pendown != pendown:
            print(f"pendown={self.pendown}  # was {pendown}")

        # todo: calculated boolean args for pd pu ht st

    def do_penup(self) -> None:  # as if do_pu
        """Plan to Not leave a Trail as the Turtle moves"""

        pendown = self.pendown
        self.pendown = False
        if self.pendown != pendown:
            print(f"pendown={self.pendown}  # was {pendown}")

    def do_print(self, *args) -> None:  # as if do_p
        """Print the Str of each Arg, separated by Spaces, and then 1 Line_Break"""

        print(*args)

    def do_repeat(self, count=None) -> None:  # as if do_rep
        """Run some instructions a chosen number of times, often less or more than once"""

        count = 1 if (count is None) else int(count)
        if not count:
            self.do_forward(0)  # punches the initial pixel without moving on
            self.do_right(0)  # mostly harmless
        else:
            angle = 360 / count
            for _ in range(count):
                self.do_forward()  # the traditional [fd rt]
                self.do_right(angle)  # not the countercultural [rt fd]

    def do_right(self, angle=None) -> None:  # as if do_rt
        """Turn the Turtle clockwise, by a 90° Right Angle, or some other Angle"""

        heading = self.heading  # turning clockwise

        float_angle = 90e0 if (angle is None) else float(angle)
        self.heading = (heading + float_angle) % 360  # 360° Circle
        if self.heading != heading:
            print(f"heading={self.heading}{DegreeSign}  # was {heading}{DegreeSign}")

    def do_setheading(self, angle=None) -> None:  # as if do_seth
        """Turn the Turtle to move 0° North, or to some other Heading"""

        heading = self.heading  # turning North

        float_angle = 0e0 if (angle is None) else float(angle)  # 0° of North Up Clockwise
        self.heading = float_angle % 360  # 360° Circle
        if self.heading != heading:
            print(f"heading={self.heading}{DegreeSign}  # was {heading}{DegreeSign}")

    def do_sethertz(self, hertz=None) -> None:

        sleep = self.sleep

        sleep1 = 0e0
        float_hertz = 1000e0 if (hertz is None) else float(hertz)
        if float_hertz:
            sleep1 = 1 / float_hertz

        self.sleep = sleep1

        if sleep1 != sleep:
            print(f"sleep={sleep1}s  # was {sleep}s")

    def do_setpencolor(self, color=None) -> None:  # as if do_setpcv
        """Choose which Color to draw with"""

        penmode = self.penmode

        floatish = isinstance(color, float) or isinstance(color, int) or isinstance(color, bool)
        if color is None:
            penmode1 = "\x1B[m"  # CSI 06/13 Select Graphic Rendition (SGR)
        elif floatish or isinstance(color, decimal.Decimal):
            penmode1 = self.rgb_to_penmode(rgb=int(color))
        elif isinstance(color, str):
            if color.casefold() == "None".casefold():
                penmode1 = "\x1B[m"  # CSI 06/13 Select Graphic Rendition (SGR)
            else:
                penmode1 = self.colorname_to_penmode(colorname=color)
        else:
            assert False, (type(color), color)

        py = f"self.str_write({penmode1!r})"

        rep = self.py_eval_to_repr(py)
        assert not rep, (rep, py)

        self.penmode = penmode1

        if penmode1 != penmode:
            print(f"penmode={penmode1!r} because {color!r}  # was {penmode!r}")

    rgb_by_name = {
        "white": 0xFFFFFF,
        "magenta": 0xFF00FF,
        "blue": 0x0000FF,
        "cyan": 0x00FFFF,
        "green": 0x00FF00,
        "yellow": 0xFFFF00,
        "red": 0xFF0000,
        "black": 0x000000,
    }

    ansi_by_rgb = {  # CSI 06/13 Select Graphic Rendition (SGR)  # 30+ Display Foreground Color
        0xFFFFFF: "\x1B[37m",
        0xFF00FF: "\x1B[35m",
        0x0000FF: "\x1B[34m",
        0x00FFFF: "\x1B[36m",
        0x00FF00: "\x1B[32m",
        0xFFFF00: "\x1B[33m",
        0xFF0000: "\x1B[31m",
        0x000000: "\x1B[30m",
    }

    def colorname_to_penmode(self, colorname) -> str:

        casefold = colorname.casefold()
        colornames = sorted(_.title() for _ in self.rgb_by_name.keys())
        if casefold not in self.rgb_by_name.keys():
            raise KeyError(f"{colorname!r} not in {colornames}")

        rgb = self.rgb_by_name[casefold]
        penmode = self.ansi_by_rgb[rgb]
        return penmode

    def rgb_to_penmode(self, rgb) -> str:
        penmode = self.ansi_by_rgb[rgb]
        return penmode

    def do_setpenpunch(self, ch=None) -> None:  # as if do_setpch
        """Choose which Character to draw with, or default to '*'"""

        penchar = self.penchar

        floatish = isinstance(ch, float) or isinstance(ch, int) or isinstance(ch, bool)
        if ch is None:
            penchar1 = FullBlock
        elif floatish or isinstance(ch, decimal.Decimal):
            penchar1 = chr(int(ch))  # not much test of '\0' yet
        elif isinstance(ch, str):
            # assert len(ch) == 1, (len(ch), ch)  # todo: unlock vs require Len 1 after dropping Sgr's
            penchar1 = ch
        else:
            assert False, (type(ch), ch)

        self.penchar = penchar1

        if penchar1 != penchar:
            print(f"penchar={penchar1!r}  # was {penchar!r}")

        # todo: With SetPenColor Forward 1:  "!" if (penchar == "~") else chr(ord(penchar) + 1)

    def do_setxy(self, x=None, y=None) -> None:
        """Move the Turtle to an X Y Point, tracing a Trail if Pen Down"""

        float_x = 0e0 if (x is None) else float(x)
        float_y = 0e0 if (y is None) else float(y)

        (x1, y1) = self.os_terminal_x_y()

        x2 = round(float_x / 10)  # / 10 to a screen of a few large pixels
        y2 = round(float_y / 10 / 2)  # / 2 for thin pixels

        self.punch_bresenham_segment(x1, y1=y1, x2=x2, y2=y2)

        self.float_x = float_x  # not 'float_x_'
        self.float_y = float_y  # not 'float_y_'

        # todo: setx without setxy, sety without setxy

    def do_showturtle(self) -> None:
        """Start showing where the Turtle is"""

        hiding = self.hiding

        text = "\x1B[?25h"  # 06/08 Set Mode (SMS) 25 VT220 DECTCEM
        self.str_write(text)

        self.hiding = False
        if self.hiding != hiding:
            print(f"hiding={self.hiding}  # was {hiding}")

        # Forward 0 leaves a Mark to show the Turtle was Here
        # SetXY leaves a Mark to show the X=0 Y=0 Home

    def do_sleep(self) -> None:
        """Hold the Turtle still for a moment"""

        sleep = self.sleep
        print(f"Sleeping {sleep}s because SetHertz")
        time.sleep(sleep)

        # tested with:  sethertz 5  st s ht s  st s ht s  st s ht s  st

    def do_tada(self) -> None:
        """Hide the Turtle, but only until next Call"""

        text = "\x1B[?25l"  # 06/12 Reset Mode (RM) 25 VT220 DECTCEM
        self.str_write(text)

        def tada_func() -> None:
            text = "\x1B[?25h"  # 06/08 Set Mode (SMS) 25 VT220 DECTCEM
            self.str_write(text)

        self.tada_func_else = tada_func

    #
    # Move the Turtle along the Line of its Heading
    #

    def punch_bresenham_stride(self, stride) -> None:
        """Step forwards, or backwards, along the Heading"""

        stride_ = float(stride) / 10  # / 10 to a screen of a few large pixels

        heading = self.heading  # 0° North Up Clockwise

        # Choose the Starting Point

        (x1, y1) = self.os_terminal_x_y()
        float_x = self.float_x
        float_y = self.float_y
        assert (x1 == round(float_x)) and (y1 == round(float_y)), (x1, float_x, y1, float_y)

        # Choose the Ending Point

        angle = (90 - heading) % 360  # converts to 0° East Anticlockwise
        float_x_ = float_x + (stride_ * math.cos(math.radians(angle)))  # destination
        float_x__ = round(float_x_, 10)  # todo: how round should our Float Maths be?
        float_y_ = float_y + (stride_ * math.sin(math.radians(angle)) / 2)  # / 2 for thin pixels
        float_y__ = round(float_y_, 10)  # todo: are we happy with -0.0 and +0.0 flopping arund?

        x2 = round(float_x__)
        y2 = round(float_y__)

        # Option to show why Round over Int at X2 Y2

        fuzz1 = True
        fuzz1 = False
        if fuzz1:
            print(f"FUZZ1 {stride_=} {angle=} {x1=} {y1=} {x2=} {y2=} {float_x_} {float_y_} FUZZ1")
            x2 = int(float_x_)
            y2 = int(float_y_)

            # got:  cs  pu home reset pd  rt rt fd  rt fd 400
            # wanted:  cs  reset pd  setpch '.'  pu setxy ~400 ~100  pd rt fd 400 lt fd
            # surfaced by:  demos/headings.logo

        # Draw the Line Segment to X2 Y2 from X1 Y1

        self.punch_bresenham_segment(x1, y1=y1, x2=x2, y2=y2)
        print(f"float {float_x} {float_y} {float_x__} {float_y__}")

        # Option to show why keep up Precise X Y Shadows in .float_x .float_y

        fuzz2 = True
        fuzz2 = False
        if fuzz2:  # fail test of:  cs  reset pd  fd rt 72  fd rt 72  fd rt 72  fd rt 72  fd rt 72
            print(f"FUZZ2 {stride_=} {angle=} {x1=} {y1=} {x2=} {y2=} {float_x__} {float_y__} FUZZ2")
            float_x__ = float(x2)
            float_y__ = float(y2)

            # got Pentagon overshot:  cs  reset pd  fd rt 72  fd rt 72  fd rt 72  fd rt 72  fd rt 72
            # got Octogon overshot:  cs  reset pd  rep 8 [fd rt 45]
            # wanted close like:  cs  reset pd  fd rt 120  fd rt 120  fd rt 120
            # wanted close like:  cs  reset pd  rep 4 [fd rt 90]
            # surfaced by:  walking polygons

        self.float_x = float_x__
        self.float_y = float_y__

    def punch_bresenham_segment(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Step forwards, or backwards, through (Row, Column) choices"""

        assert isinstance(x1, int), (type(x1), x1)
        assert isinstance(y1, int), (type(y1), y1)
        assert isinstance(y2, int), (type(y2), y2)
        assert isinstance(x2, int), (type(x2), x2)

        print(f"{x1=} {y1=} ({2 * y1}e0)  {x2=} {y2=} ({2 * y2}e0)")

        x2x1 = abs(x2 - x1)  # distance
        y2y1 = abs(y2 - y1)

        sx = 1 if (x1 < x2) else -1  # steps towards X2 from X1
        sy = 1 if (y1 < y2) else -1  # steps towards Y2 from y1

        e = x2x1 - y2y1  # Bresenham's Error Measure

        wx = x = x1
        wy = y = y1
        while True:

            self.jump_then_punch(wx, wy=-wy, x=x, y=-y)
            if (x == x2) and (y == y2):
                break

            wx = x
            wy = y

            ee = 2 * e
            dx = ee < x2x1
            dy = ee > -y2y1
            assert dx or dy, (dx, dy, x, y, ee, x2x1, y2y1, x1, y1)

            if dy:
                e -= y2y1
                x += sx
            if dx:
                e += x2x1
                y += sy

            assert (x, y) != (wx, wy)

        # Wikipedia > https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm

        # To: Perplexity·Ai
        #
        #   When I'm drawing a line across a pixellated display,
        #   what's the most ordinary way
        #   to turn my y = a*x + b equation into a list of pixels to turn on?
        #

    def jump_then_punch(self, wx, wy, x, y) -> None:
        """Move the Turtle by 1 Column or 1 Row or both, and punch out a Mark if Pen Down"""

        hiding = self.hiding
        pendown = self.pendown
        penchar = self.penchar
        sleep = self.sleep

        # print(f"{x} {y}")

        if wx < x:
            x_text = f"\x1B[{x - wx}C"  # CSI 04/03 Cursor [Forward] Right
        elif wx > x:
            x_text = f"\x1B[{wx - x}D"  # CSI 04/04 Cursor [Backward] Left
        else:
            x_text = ""

        if wy < y:
            y_text = f"\x1B[{y - wy}B"  # CSI 04/02 Cursor [Down] Next
        elif wy > y:
            y_text = f"\x1B[{wy - y}A"  # CSI 04/01 Cursor [Up] Previous
        else:
            y_text = ""

        text = f"{y_text}{x_text}"
        if pendown:
            pc_text = penchar + (len(penchar) * "\b")
            text = f"{y_text}{x_text}{pc_text}"

        self.str_write(text)

        if not hiding:
            time.sleep(sleep)

    #
    # Layer thinly over 1 ShadowsTerminal, found at the far side of 2 Named Pipes
    #

    def breakpoint(self) -> None:
        """Chat through a Python Breakpoint, but without redefining ⌃C SigInt"""

        getsignal = signal.getsignal(signal.SIGINT)

        breakpoint()
        pass

        signal.signal(signal.SIGINT, getsignal)

    def str_write(self, text) -> None:
        """Write the Text remotely, at the Turtle"""

        py = f"self.str_write({text!r})"
        rep = self.py_eval_to_repr(py)
        assert not rep, (rep, py)

    def py_eval_to_repr(self, py) -> str:
        """Eval the Python remotely, inside the Turtle, and return the Repr of the Result"""

        # opener1 = ""  # "<client>"
        # closer1 = ""  # "<tneilc>"

        print_if(f"Client Write text={py!r}")
        try:
            # pathlib.Path("stdin.mkfifo").write_text(opener1 + py + closer1)
            pathlib.Path("stdin.mkfifo").write_text(py)
        except BrokenPipeError:
            print("BrokenPipeError", file=sys.stderr)
            sys.exit()  # exits zero to shrug off BrokenPipeError

        # opener2 = ""  # "<server>"
        # closer2 = ""  # "<revres>"

        print_if("Client Read Entry")
        read_text = pathlib.Path("stdout.mkfifo").read_text()
        print_if(f"Client Read Exit text={read_text!r}")

        # assert read_text.startswith(opener2), (opener2, read_text)
        # assert read_text.endswith(closer2), (closer2, read_text)
        # read_core = read_text[len(opener2) : -len(closer2)]

        read_core = read_text

        if read_core == "None":
            return ""  # todo: think more about encodings of None

        if read_core.startswith("'Traceback (most recent call last):\\n"):
            exc_text = ast.literal_eval(read_core)
            print(exc_text, file=sys.stderr)
            return ""

        return read_core

    def os_terminal_x_y(self) -> tuple[int, int]:
        """Sample the X Y Position remotely, inside the Turtle"""

        float_x = self.float_x
        float_y = self.float_y

        # Find the Cursor

        (y_row, x_column) = self.os_terminal_y_row_x_column()

        # Find the Center of Screen

        x_columns, y_lines = self.os_terminal_size()
        cx = 1 + (x_columns // 2)
        cy = 1 + (y_lines // 2)

        # Say how far away from Center the Cursor is, on a plane of Y is Up and X is Right

        x1 = x_column - cx
        y1 = -(y_row - cy)

        # Snap the Shadow to the Cursor Row-Column, if the Cursor moved

        if (x1 != round(float_x)) or (y1 != round(float_y)):
            float_x_ = float(x1)  # 'explicit is better than implicit'
            float_y_ = float(y1)

            print(f"snap to {float_x_} {float_y_} from {float_x} {float_y}")
            self.float_x = float_x_
            self.float_y = float_y_

        # Succeed

        return (x1, y1)

    def os_terminal_y_row_x_column(self) -> tuple[int, int]:
        """Sample the Row-Column Position remotely, inside the Turtle"""

        py = "self.write_dsr_read_kcpr_y_x()"
        rep = self.py_eval_to_repr(py)
        kcpr_y_x = ast.literal_eval(rep)

        (y_row, x_column) = kcpr_y_x
        assert isinstance(y_row, int), (type(y_row), y_row)
        assert isinstance(x_column, int), (type(x_column), x_column)

        return (y_row, x_column)

    def os_terminal_size(self) -> tuple[int, int]:
        """Sample the Terminal Width and Height remotely, inside the Turtle"""

        py = "os.get_terminal_size()"
        rep = self.py_eval_to_repr(py)

        regex = r"os.terminal_size[(]columns=([0-9]+), lines=([0-9]+)[)]"
        m = re.fullmatch(regex, rep)
        assert m, (m, py, rep)
        x_columns, y_lines = m.groups()

        size = os.terminal_size([int(x_columns), int(y_lines)])

        return size


#
# 🐢 My Guesses of Main Causes of loss in Net Promoter Score (NPS) # todo
#
# todo: can't paste the drawing back into the Terminal
# todo: hangs now and again
# todo: details still churning for the resulting drawing
#


#
# 🐢 Bug Fixes  # todo
#
#
# todo: tweak up 'make push' to depend on:  ssh-end-work, ssh-start-home
# but inside call on ssh-end-home, ssh-start-work
#
#
# todo: solve the thin flats left on screen behind:  reset cs pu  sethertz 10 rep 8
# also differs by Hertz:  reset cs pu  sethertz rep 8
# also:  sethertz cs pu setxy 250 250  sethertz 100 home
# also:  sethertz cs pu setxy 0 210  sethertz 100 home
#
# todo: solve why ↓ ↑ Keys too small - rounding trouble?:  demos/arrow-keys.logo
#
#
# todo: solve run 'pq.py' easily outside macOS, like disentangle from Pq PbCopy/ PbPaste
# todo: stop clearing the Os Copy-Paste Buffer as part of quitting normally
#
# todo: test bounds collisions
#   reset cs pd  pu setxy 530 44 pd  lt fd 300
#       skips the column inside the right edge ?!
#
# todo: strip out the Sgr and then limit "setpch" to 1 Char
# todo: unlock Verb for less limited experimentation
#
# todo: repro/ fix remaining occasional hangs in the named-pipe mkfifo of Linux & macOS
# todo: start the 🐢 Chat without waiting to complete the first write to the 🐢 Sketch
#
# todo: solve ⌘K vs Turtle Server - record the input, fix the output, especially wide prompts
#

#
# 🐢 Turtle Demos  # todo
#
#
# todo: Write a Tutorial
#
#
# todo: 'cs ...' to choose a next demo of a shuffle
# todo: 'import filename' or 'load filename' to fetch & run a particular file
#
#
# todo: early visual wows of a twitch stream
# todo: colorful spirography
# todo: 'batteries included better than homemade'
#
# todo: demo bugs fixed lately - Large Headings.logo for '.round()' vs '.trunc()'
#
# todo: one large single File of many Logo Procs, via:  def <name> [ ... ]
# todo: multiple Procs per File via TO <name>, then dents, optional END
#
# todo: abs square:  reset cs pd  setxy 0 100  setxy 100 100  setxy 100 0  setxy 0 0
# todo: blink xy:  sethertz 5  st s ht s  st s ht s  st s ht s  st
# todo: blink heading:  sethertz 5  pu  st s ht s  bk 10 st s ht s  fd 20 st s ht s  bk 10 st s ht s  st
# todo: smoke tests of call the Grunts & Verbs as cited by:  help
#
# garbled to do was: 🐢 Tada exists
#

#
# 🐢 Turtle Shadow Engine  # todo
#
#
# z layer "█@" for a Turtle with 8 Headings
# todo: z-layers, like one out front with more fun Cursors as Turtle
# todo: thinner X Y Pixels & Pens, especially the 0.5X 1Y of U+2584 Lower, U+2580 Upper
#
#
# todo: fill and clear to collision, with colors, with patterns
#
# todo: do & redo & undo for Turtle work
#
# todo: take end-of-Tada in from Vi
# todo: take Heading in from Vi
# todo: compose the Logo Command that sums up the Vi choices
#
# todo: draw on a Canvas larger than the screen
# todo: checkpoint/ commit/ restore the Canvas
# todo: export the Canvas as .typescript, styled & colored
#

#
# 🐢 Turtle Graphics Engine  # todo
#
#
# todo: t.penchars should stay as the Chars only, but we always ⎋[Y;XH to where we were
#
# todo: thicker X Y Pixels
#
# talk up gDoc for export
# work up export to gDoc tech for ending color without spacing to right of screen
#
# todo: edge cap cursor position, wrap, bounce, whine, stop
#
#
# todo: plot Fonts of Characters
#
#
# todo: label "\e[41m" cs - does work, fill screen w background colour, do we like that?
#
# todo: thicker X Y Pens, especially the squarish 2X 1Y
#
# todo: double-wide Chars for the Turtle, such as LargeGreenCircle  # setpch "🟢"
# todo: pasting such as LargeGreenCircle into ⇧R of 'pq turtle', 'pq st yolo', etc
#
# todo: Large Window vs SetScrunch, such as a large Headings.logo
# todo: Ellipse etc via SetScrunch to tweak our fixed '/ 2 for thin pixels'
# todo: Log Scale SetScrunch in Y or X or both
#
# todo: more bits of Turtle State on Screen somehow
# todo: more perceptible Screen State, such as the Chars there already
#
#
# todo: 3D Turtle position & trace
#

#
# 🐢 Turtle Chat Engine  # todo
#
# todo: e Pi Inf -Inf NaN
#
# todo: \e escapes in Str
# todo: kebab-case as a string becomes "kebab case"
# todo: input Sh lines:  !uname  # !ls  # !cat - >/dev/null  # !zsh
# todo: input Py lines:  ;sys.version_info[:3]  # ;breakpoint()
# todo: stop rejecting ; as Eval Syntax Error, route to Exec instead
#
# todo: 🐢 Punch ... "\n"   # to print at Server, vs Print at Client
# todo: 🐢 After ...  # to get past next Float Seconds milestone in Screen .typescript
#
# todo: tweak the fd.d to hold diameter constant in 🐢 rep n abbreviation of rep n [fd fd.d rt rt.angle]
#
# todo: prompts placed correctly in the echo of multiple lines of Input
#
# todo: 🐢 Pin to drop a pin (in float precision!)
# todo: 🐢 Go to get back to it
# todo: 🐢 Pin that has a name, and list them at 🐢 Go, and delete them if pinned twice in same place
#
# todo: or teach 🐢 Label to take a last arg of "" as an ask for no newline?
#
# todo: rep n [fd fd.d rt rt.angle]
# todo: get/set of default args, such as fd.d and rt.angle
# todo: printing diffs only vs say where we are, such as "rt 0" or "sethertz"
# todo: 'setpch' to .punch or pen.char or what?
# todo: nonliteral (getter) arguments  # 'heading', 'position', 'isvisible', etc
# todo: deal with Logo Legacy of 'func nary' vs '(func nary and more and more)'
#
# todo: pinned sampling, such as list of variables to watch
# todo: mouse-click (or key chord) to unfold/ fold the values watched
#
# todo: escape more robustly into Python Exec & Eval, such as explicit func(arg) calls
#
# todo: Command Input Line History
# todo: Command Input Word Tab-Completions
#
# todo: KwArgs for Funcs
# todo: VsCode for .logo, for .lgo, ...
#
# todo: reconcile with Python "import turtle" Graphics on TkInter
# todo: .sleep vs Python Turtle screen.delay
# todo: .stride vs Logo SetStepSize
# todo: .sleep vs Logo SetSpeed, SetVelocity, Wait
#
# todo: random moves, seeded random
# todo: cyclic moves in Color, in Pen Down, and help catalog more than 8 Colors
# todo: Pen Colors that mix with the Screen: PenPaint/ PenReverse/ PenErase
#
# todo: circles, ellipses
# todo: arc(angle, radius) with a design for center & end-position
# todo: arcs with more args at https://fmslogo.sourceforge.io/manual/command-ellipsearc.html
# todo: collisions, gravity, friction
#
# todo: context of Color Delay etc Space for Forward & Turn, like into irregular dance beat
# todo: color less arcanely than via self.str_write "\x1B[36m"
#   as with  ⎋[31m red  ⎋[32m green  ⎋[36m cyan  ⎋[38;5;130m orange
#
# todo: scroll and resize and reposition the window
#

#
# 🐢 Python Makeovers  # todo
#
#
# todo: factor out Class Turtle, think into running more than one
# todo: factor out 'import uturtle' as a copy of 'pq.py' created when needed
# todo: def efprint1(self, form, **kwargs) at uturtle.Turtle for printing its Fields
# todo: print only first and then changes in the form result
#
#
# todo: have the BytesTerminal say when to yield, but yield in the ShadowsTerminal
# todo: move the VT420 DECDC ⎋['~ and DECIC ⎋['} emulations up into the ShadowsTerminal
#

#
# 🐢 Turtle Chat References
#
#   FMSLogo for Linux Wine/ Windows (does the Linux Wine work?)
#   https://fmslogo.sourceforge.io
#   https://fmslogo.sourceforge.io/manual/index.html
#
#   UCBLogo for Linux/ macOS/ Windows <- USA > U of California Berkeley (UCB)
#   https://people.eecs.berkeley.edu/~bh/logo.html
#   https://people.eecs.berkeley.edu/~bh/usermanual [.txt]
#
#   References listed by https://people.eecs.berkeley.edu/~bh/other-logos.html
#   References listed by https://fmslogo.sourceforge.io/manual/where-to-start.html
#


#
# Amp up Import BuiltIns
#


def eprint(*args, **kwargs) -> None:
    """Print to Stderr"""

    print(*args, file=sys.stderr, **kwargs)


w_open_else: typing.TextIO | None
w_open_else = None


def print_if(*args, **kwargs) -> None:
    """Print, if debugging"""

    if w_open_else:
        file_ = w_open_else

        print(*args, **kwargs, end="\r\n", file=file_)
        file_.flush()  # todo: measure when no flush needed by (file_ is sys.stderr)


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/turtling.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
