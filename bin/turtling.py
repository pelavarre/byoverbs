#!/usr/bin/env python3

r"""
usage: turtling.py [-h] [--yolo] [-i] [-c COMMAND]

draw inside a Terminal Window with Logo Turtles

options:
  -h, --help  show this message and exit
  --yolo      launch the first server in this folder, else launch a chat client
  -i          launch a chat client
  -c COMMAND  things to do, before quitting or chatting

examples:
  turtling.py --h  # shows more help and quits
  turtling.py  # shows some help and quits
  turtling.py --yolo  # tells the enclosing Terminal to start serving Turtles
  turtling.py -i  # clears screen, adds one Turtle, and chats
  turtling.py -i -c ''  # doesn't clear screen, doesn't add Turtle, but does chat
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
import re  # 're.fullmatch' since Mar/2014 Python 3.4
import select  # Windows sad at 'select.select' of Named Pipes
import shlex
import shutil
import signal
import subprocess
import sys
import termios  # Windows sad
import textwrap
import time
import traceback
import tty  # Windows sad
import typing
import unicodedata

# todo: add 'import mscvrt' at Windows


turtling = __main__


DegreeSign = unicodedata.lookup("Degree Sign")  # ° U+00B0
FullBlock = unicodedata.lookup("Full Block")  # █ U+2588
Turtle_ = unicodedata.lookup("Turtle")  # 🐢 U+01F422


if not __debug__:
    raise NotImplementedError(str((__debug__,)))  # "'python3' better than 'python3 -O'"


#
# Run well from the Sh Command Line
#


def main() -> None:
    """Run well from the Sh Command Line"""

    ns = parse_turtling_py_args_else()  # often prints help & exits

    try:
        main_try(ns)
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


def main_try(ns) -> None:

    if ns.yolo:
        assert (not ns.i) and (not ns.c), (ns.i, ns.c, ns.yolo, ns)
        if turtling_server_attach():
            turtling_client_run("relaunch")
        else:
            turtling_server_run()
        return

    turtling_server_attach()

    if ns.c is not None:
        turtling_client_run(ns.c)
        return

    assert ns.i, (ns.i, ns)
    turtling_client_run("relaunch")
    print("Bye")


def parse_turtling_py_args_else() -> argparse.Namespace:
    """Take Words in from the Sh Command Line"""

    doc = __main__.__doc__
    assert doc, (doc,)

    parser = doc_to_parser(doc, add_help=True, startswith="examples:")

    yolo_help = "launch the first server in this folder, else launch a chat client"
    i_help = "launch a chat client"
    c_help = "things to do, before quitting or chatting"

    parser.add_argument("--yolo", action="count", help=yolo_help)
    parser.add_argument("-i", action="count", help=i_help)
    parser.add_argument("-c", metavar="COMMAND", help=c_help)

    ns = parse_args_else(parser)  # often prints help & exits
    assert ns.yolo or ns.i or (ns.c is not None), (ns,)

    if ns.yolo and (ns.i or ns.c):
        sys.exit(2)  # exits 2 for wrong Sh Args

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
    if sys.argv[1:] == ["--"]:  # ArgParse chokes if Sep present without defining Pos Args
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

DSR_0 = "\x1B" "[" "0n"  # CSI 06/14 [Request] Device Status Report  # Ps 0 because DSR_5
DSR_5 = "\x1B" "[" "5n"  # CSI 06/14 [Request] Device Status Report  # Ps 5 for DSR_0 In
DSR_6 = "\x1B" "[" "6n"  # CSI 06/14 [Request] Device Status Report  # Ps 6 for CPR In

DECSCUSR = "\x1B" "[" " q"  # CSI 02/00 07/01  # '' No-Style Cursor
DECSCUSR_SKID = "\x1B" "[" "4 q"  # CSI 02/00 07/01  # 4 Skid Cursor
DECSCUSR_BAR = "\x1B" "[" "6 q"  # CSI 02/00 07/01  # 6 Bar Cursor
# all three with an Intermediate Byte of 02/00 ' ' Space

XTWINOPS_8 = "\x1B" "[" "8t"  # CSI 07/04 [Response]   # Ps 8 In because XTWINOPS_18 Out
XTWINOPS_18 = "\x1B" "[" "18t"  # CSI 07/04 [Request]   # Ps 18 Out for XTWINOPS_8 In


# the quoted Str above sorted mostly by their CSI Final Byte's:  A, B, C, D, G, Z, m, etc

# to test in Sh, run variations of:  printf '\e[18t' && read


# CSI 05/02 Active [Cursor] Position Report (CPR) In because DSR_6 Out
CPR_Y_X_REGEX = r"\x1B\[([0-9]+);([0-9]+)R"  # CSI 05/02 Active [Cursor] Pos Rep (CPR)


assert CSI_EXTRAS == "".join(chr(_) for _ in range(0x20, 0x40))  # r"[ -?]", no "@"
CSI_PIF_REGEX = r"(\x1B\[)" r"([0-?]*)" r"([ -/]*)" r"(.)"  # Parameter/ Intermediate/ Final Bytes


MACOS_TERMINAL_CSI_SIMPLE_FINAL_BYTES = "@ABCDEGHIJKLMPSTZdhlm"
# omits "R" of CPR_Y_X_REGEX In
# omits "n" of DSR_5 DSR_6 Out, so as to omit "n" of DSR_0 In
# omits "t" of XTWINOPS_18 Out, so as to omit "t" of XTWINOPS_8 In
# omits " q", "'}", "'~" of DECIC_X DECSCUSR and DECDC_X Out


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
    fileno: int  # 2

    before: int  # termios.TCSADRAIN  # termios.TCSAFLUSH  # at Entry
    tcgetattr_else: list[int | list[bytes | int]] | None  # sampled at Entry
    after: int  # termios.TCSADRAIN  # termios.TCSAFLUSH  # at Exit

    kbytes_list: list[bytes]  # Bytes of each Keyboard Chord in  # KeyLogger
    sbytes_list: list[bytes]  # Bytes of each Screen Write out  # ScreenLogger

    #
    # Init, enter, exit, flush, and stop
    #

    def __init__(self, before=termios.TCSADRAIN, after=termios.TCSADRAIN) -> None:

        assert before in (termios.TCSADRAIN, termios.TCSAFLUSH), (before,)
        assert after in (termios.TCSADRAIN, termios.TCSAFLUSH), (after,)

        stdio = sys.stderr
        fileno = stdio.fileno()

        self.stdio = stdio
        self.fileno = fileno

        self.before = before
        self.tcgetattr_else = None  # is None after Exit and before Entry
        self.after = after

        self.kbytes_list = list()
        self.sbytes_list = list()

        # todo: need .after = termios.TCSAFLUSH on large Paste crashing us

    def __enter__(self) -> "BytesTerminal":  # -> typing.Self:
        r"""Stop line-buffering Input, stop replacing \n Output with \r\n, etc"""

        fileno = self.fileno
        before = self.before
        tcgetattr_else = self.tcgetattr_else

        if tcgetattr_else is None:
            tcgetattr = termios.tcgetattr(fileno)
            assert tcgetattr is not None

            self.tcgetattr_else = tcgetattr

            assert before in (termios.TCSADRAIN, termios.TCSAFLUSH), (before,)

            debug = False
            if debug:
                tty.setcbreak(fileno, when=termios.TCSAFLUSH)  # ⌃C prints Py Traceback
            else:
                tty.setraw(fileno, when=before)  # SetRaw defaults to TcsaFlush

        return self

    def __exit__(self, *exc_info) -> None:
        r"""Start line-buffering Input, start replacing \n Output with \r\n, etc"""

        fileno = self.fileno
        tcgetattr_else = self.tcgetattr_else
        after = self.after

        if tcgetattr_else is not None:
            self.sbytes_flush()  # for '__exit__' of .ksbytes_stop etc

            tcgetattr = tcgetattr_else
            self.tcgetattr_else = None

            assert after in (termios.TCSADRAIN, termios.TCSAFLUSH), (after,)
            when = after
            termios.tcsetattr(fileno, when, tcgetattr)

        return None

    def sbytes_flush(self) -> None:
        """Flush Screen Output, like just before blocking to read Keyboard Input"""

        stdio = self.stdio
        stdio.flush()

    def ksbytes_stop(self) -> None:  # todo: learn to do .ksbytes_stop() well
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

    #
    # Write Screen Output Bytes
    #

    def sbytes_write(self, sbytes) -> None:
        """Write Bytes to the Screen, but without implicitly also writing a Line-End afterwards"""

        assert self.tcgetattr_else, (self.tcgetattr_else,)

        fileno = self.fileno
        sbytes_list = self.sbytes_list

        sbytes_list.append(sbytes)
        os.write(fileno, sbytes)

        # doesn't raise UnicodeEncodeError
        # called with end=b"" to write without adding b"\r\n"
        # called with end=b"n" to add b"\n" in place of b"\r\n"

    #
    # Read Key Chords as 1 or more Keyboard Bytes
    #

    def kbytes_pull(self, timeout) -> bytes:
        """Read, and record, the Bytes of 1 Incomplete/ Complete Key Chord"""

        kbytes_list = self.kbytes_list

        kbytes = self.kbytes_read(timeout=timeout)
        kbytes_list.append(kbytes)

        return kbytes

    def kbytes_read(self, timeout) -> bytes:
        """Read the Bytes of 1 Incomplete/ Complete Key Chord, without recording them"""

        assert ESC == "\x1B"
        assert CSI == "\x1B" "["
        assert SS3 == "\x1B" "O"

        # Block to fetch at least 1 Byte

        kbytes1 = self.kchar_bytes_read_if()  # for .kbytes_read

        many_kbytes = kbytes1
        if kbytes1 != b"\x1B":
            return many_kbytes

        # Accept 1 or more Esc Bytes, such as x 1B 1B in ⌥⌃FnDelete

        while True:
            if not self.kbhit(timeout=timeout):
                return many_kbytes

                # 1st loop:  ⎋ Esc that isn't ⎋⎋ Meta Esc
                # 2nd loop:  ⎋⎋ Meta Esc that doesn't come with more Bytes

            kbytes2 = self.kchar_bytes_read_if()  # for .kbytes_read
            many_kbytes += kbytes2
            if kbytes2 != b"\x1B":
                break

        if kbytes2 == b"O":  # 01/11 04/15 SS3
            kbytes3 = self.kchar_bytes_read_if()  # for .kbytes_read
            many_kbytes += kbytes3  # todo: rarely in range(0x20, 0x40) CSI_EXTRAS
            return many_kbytes

        # Accept ⎋[ Meta [ cut short by itself, or longer CSI Escape Sequences

        if kbytes2 == b"[":  # 01/11 ... 05/11 CSI
            assert many_kbytes.endswith(b"\x1B\x5B"), (many_kbytes,)
            if not self.kbhit(timeout=timeout):
                return many_kbytes

                # ⎋[ Meta Esc that doesn't come with more Bytes

            many_kbytes = self.csi_kchord_bytes_read_if(many_kbytes)

        # Succeed

        return many_kbytes

        # cut short by end-of-input, or by undecodable Bytes
        # doesn't raise UnicodeDecodeError

    def csi_kchord_bytes_read_if(self, kbytes) -> bytes:
        """Block to read the rest of 1 CSI Escape Sequence"""

        assert CSI_EXTRAS == "".join(chr(_) for _ in range(0x20, 0x40))

        many_kchord_bytes = kbytes
        while True:
            kbytes_ = self.kchar_bytes_read_if()  # for .kbytes_read via .read_csi_...
            many_kchord_bytes += kbytes_

            if len(kbytes_) == 1:  # as when ord(kbytes_.encode()) < 0x80
                kord = kbytes_[-1]
                if 0x20 <= kord < 0x40:
                    continue

                    # 16 Parameter Bytes in 0123456789:;<=>?
                    # 16 Intermediate Bytes of Space or in !"#$%&'()*+,-./

                    # FIXME: accept Parameter Bytes only before Intermediate Bytes

            break

        return many_kchord_bytes

        # continues indefinitely while next Bytes in CSI_EXTRAS
        # cut short by end-of-input, or by undecodable Bytes
        # doesn't raise UnicodeDecodeError

        # todo: limit the length of the CSI Escape Sequence

    def kchar_bytes_read_if(self) -> bytes:
        """Read the Bytes of 1 Incomplete/ Complete Char from Keyboard"""

        def decodable(kbytes: bytes) -> bool:
            try:
                kbytes.decode()  # may raise UnicodeDecodeError
                return True
            except UnicodeDecodeError:
                return False

        kbytes = b""
        while True:  # till KChar Bytes complete
            kbyte = self.kbyte_read()  # for .kchar_bytes_read_if  # todo: test end-of-input
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

    def kbyte_read(self) -> bytes:
        """Read 1 Keyboard Byte"""

        fileno = self.fileno
        assert self.tcgetattr_else, (self.tcgetattr_else,)

        self.sbytes_flush()  # for 'kbyte_read'
        kbyte = os.read(fileno, 1)  # 1 or more Bytes, begun as 1 Byte

        return kbyte

        # ⌃C comes through as b"\x03" and doesn't raise KeyboardInterrupt
        # ⌥Y often comes through as \ U+005C Reverse-Solidus aka Backslash

    def kbhit(self, timeout) -> bool:  # 'timeout' in seconds - 0 for now, None for forever
        """Block till next Input Byte, else till Timeout, else till forever"""

        fileno = self.fileno
        assert self.tcgetattr_else, self.tcgetattr_else  # todo: kbhit can say readline won't block

        self.sbytes_flush()  # for 'kbhit'  # todo: log how often unneeded

        (r, w, x) = select.select([fileno], [], [], timeout)
        hit = fileno in r

        return hit


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


class StrTerminal:
    """Write/ Read Chars at Screen/ Keyboard of the Terminal, mixed with Inband Signals"""

    bytes_terminal: BytesTerminal
    kchords: list[tuple[bytes, str]]  # Key Chords read ahead after DSR until CPR

    y_rows: int  # -1, then Count of Screen Rows
    x_columns: int  # -1, then Count of Screen Columns

    row_y: int  # -1, then Row of Cursor
    column_x: int  # -1, then Column of Cursor

    #
    # Init, Enter, and Exit
    #

    def __init__(self) -> None:

        bt = BytesTerminal()

        self.bytes_terminal = bt
        self.kchords = list()

        self.y_rows = -1
        self.x_columns = -1
        self.row_y = -1
        self.column_x = -1

    def __enter__(self) -> "StrTerminal":  # -> typing.Self:

        bt = self.bytes_terminal
        bt.__enter__()

        return self

    def __exit__(self, *exc_info) -> None:

        bt = self.bytes_terminal
        kchords = self.kchords

        if kchords:
            self.schars_print()
            while kchords:
                (kbytes, kcaps) = kchords.pop(0)
                self.schars_print(kcaps)

        bt.__exit__()

    #
    # Read Key Chords from Keyboard or Screen
    #

    def kchord_pull(self, timeout) -> tuple[bytes, str]:
        """Read 1 Key Chord, but snoop the Cursor-Position-Report's, if any"""

        bt = self.bytes_terminal
        kchords = self.kchords

        if kchords:
            kchord = kchords.pop(0)
            return kchord

            # todo: log how rarely KChords wait inside a StrTerminal

        kbytes = bt.kbytes_pull(timeout=timeout)  # may contain b' ' near to KCAP_SEP
        kchars = kbytes.decode()  # may raise UnicodeDecodeError
        kchord = self.kbytes_to_kchord(kbytes)

        self.kchars_snoop_kcpr_if(kchars)

        return kchord

    def kchars_snoop_kcpr_if(self, kchars) -> bool:
        """Snoop the Cursor-Position-Report (CPR) out of a Key Chord, if present"""

        assert CPR_Y_X_REGEX == r"\x1B\[([0-9]+);([0-9]+)R"  # CSI 05/02 CPR

        # Never mind, if no CPR present

        m = re.fullmatch(r"\x1B\[([0-9]+);([0-9]+)R", string=kchars)
        if not m:
            return False

        # Interpret the CPR

        row_y = int(m.group(1))
        column_x = int(m.group(2))

        assert row_y >= 1, (row_y,)
        assert column_x >= 1, (column_x,)

        self.row_y = row_y
        self.column_x = column_x

        return True

    def kbytes_to_kchord(self, kbytes) -> tuple[bytes, str]:
        """Choose 1 Key Cap to speak of the Bytes of 1 Key Chord"""

        kchars = kbytes.decode()  # may raise UnicodeDecodeError

        kcap_by_kchars = KCAP_BY_KCHARS  # '\e\e[A' for ⎋↑ etc

        if kchars in kcap_by_kchars.keys():
            kcaps = kcap_by_kchars[kchars]
        else:
            kcaps = ""
            for kch in kchars:  # often 'len(kchars) == 1'
                s = self.kch_to_kcap(kch)
                kcaps += s

                # '⎋[25;80R' Cursor-Position-Report (CPR)
                # '⎋[25;80t' Rows x Column Terminal Size Report
                # '⎋[200~' and '⎋[201~' before/ after Paste to bracket it

            # ⌥Y often comes through as \ U+005C Reverse-Solidus aka Backslash

        # Succeed

        assert KCAP_SEP == " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc
        assert " " not in kcaps, (kcaps,)

        return (kbytes, kcaps)

        # '⌃L'  # '⇧Z'
        # '⎋A' from ⌥A while macOS Keyboard > Option as Meta Key

    def kch_to_kcap(self, ch) -> str:  # noqa C901
        """Choose a Key Cap to speak of 1 Char read from the Keyboard"""

        o = ord(ch)

        option_kchars_spaceless = OPTION_KCHARS_SPACELESS  # '∂' for ⌥D
        option_kstr_by_1_kchar = OPTION_KSTR_BY_1_KCHAR  # 'é' for ⌥EE
        kcap_by_kchars = KCAP_BY_KCHARS  # '\x7F' for 'Delete'

        # Show more Key Caps than US-Ascii mentions

        if ch in kcap_by_kchars.keys():  # Mac US Key Caps for Spacebar, F12, etc
            s = kcap_by_kchars[ch]

        elif ch in option_kstr_by_1_kchar.keys():  # Mac US Option Accents
            s = option_kstr_by_1_kchar[ch]

        elif ch in option_kchars_spaceless:  # Mac US Option Key Caps
            s = self.spaceless_ch_to_option_kstr(ch)

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

    def spaceless_ch_to_option_kstr(self, ch) -> str:
        """Convert to Mac US Option Key Caps from any of OPTION_KCHARS_SPACELESS"""

        option_kchars = OPTION_KCHARS  # '∂' for ⌥D

        index = option_kchars.index(ch)
        asc = chr(0x20 + index)
        if "A" <= asc <= "Z":
            asc = "⇧" + asc  # '⇧A'
        if "a" <= asc <= "z":
            asc = chr(ord(asc) ^ 0x20)  # 'A'
        s = "⌥" + asc  # '⌥⇧P'

        return s

    def row_y_column_x_read(self, timeout) -> tuple[int, int]:
        """Sample Cursor Row & Column"""

        bt = self.bytes_terminal
        kchords = self.kchords

        assert DSR_6 == "\x1B" "[" "6n"  # CSI 06/14 DSR  # Ps 6 for CPR

        self.schars_write("\x1B" "[" "6n")

        while True:
            kbytes = bt.kbytes_pull(timeout=timeout)  # may contain b' ' near to KCAP_SEP
            kchars = kbytes.decode()  # may raise UnicodeDecodeError
            kchord = self.kbytes_to_kchord(kbytes)

            if self.kchars_snoop_kcpr_if(kchars):
                break

            kchords.append(kchord)

            # todo: log how rarely KChords wait inside a StrTerminal

        row_y = self.row_y
        column_x = self.column_x

        return (row_y, column_x)

    def y_rows_x_columns_read(self, timeout) -> tuple[int, int]:
        """Sample Counts of Screen Rows and Columns"""

        bt = self.bytes_terminal

        fileno = bt.fileno
        (columns, lines) = os.get_terminal_size(fileno)
        (x_columns, y_rows) = (columns, lines)

        assert y_rows >= 5, (y_rows,)  # macOS Terminal min 5 Rows
        assert x_columns >= 20, (x_columns,)  # macOS Terminal min 20 Columns

        self.y_rows = y_rows
        self.x_columns = x_columns

        return (y_rows, x_columns)

    #
    # Say if writing these Screen Chars as Bytes would show their meaning clearly
    #

    def schars_to_writable(self, schars) -> bool:
        """Say if writing these Screen Chars as Bytes would show their meaning clearly"""

        assert CSI_PIF_REGEX == r"(\x1B\[)" r"([0-?]*)" r"([ -/]*)" r"(.)"  # 4 Kinds of Bytes

        assert DECIC_X == "\x1B" "[" "{}'}}"  # CSI 02/07 07/13 DECIC_X  # "}}" to mean "}"
        assert DECDC_X == "\x1B" "[" "{}'~"  # CSI 02/07 07/14 DECDC_X

        assert DECSCUSR == "\x1B" "[" " q"  # CSI 02/00 07/01  # '' No-Style Cursor
        assert DECSCUSR_SKID == "\x1B" "[" "4 q"  # CSI 02/00 07/01  # 4 Skid Cursor
        assert DECSCUSR_BAR == "\x1B" "[" "6 q"  # CSI 02/00 07/01  # 6 Bar Cursor

        assert DSR_5 == "\x1B" "[" "5n"  # CSI 06/14 [Request] Device Status Report  # Ps 5 for DSR_0
        assert DSR_6 == "\x1B" "[" "6n"  # CSI 06/14 [Request] Device Status Report  # Ps 6 for CPR
        assert XTWINOPS_18 == "\x1B" "[" "18t"  # CSI 07/04 [Request]   # Ps 18 for XTWINOPS_8

        assert MACOS_TERMINAL_CSI_SIMPLE_FINAL_BYTES == "@ABCDEGHIJKLMPSTZdhlm"

        # Accept Chars that Repr Accepts

        if schars.isprintable():  # "" is printable, etc
            return True

        # Accept the most ordinary Screen Control Chars

        if schars in list(" \a\b\n\t\r"):
            return True

            # definitely True for "\n", else True Enough
            #
            #   \a takes time to land, and may be silenced
            #   \b and \r don't move the Cursor at min Column X
            #   \t doesn't move the Cursor at max Column X
            #

        # Accept the CSI Escape Sequences that a macOS Terminal accepts

        (csi, p, i, f) = self.schars_csi_partition(schars)
        if csi:

            if not i:
                if f in "@ABCDEGHIJKLMPSTZdhlm":  # no "R"
                    return True

            if (i + f) in (" q", "'}", "'~"):
                return True

            if (p + i + f) in ("5n", "6n", "18t"):  # no "0n"  # no "8t"
                return True

            # many of these have corner cases of no visible effect

        # Reject anything else

        return False

        # todo: Unlock arbitrary SChars for Testing

    def schars_csi_partition(self, schars) -> tuple[str, str, str, str]:
        """Split a CSI Escape Sequence into its Prefix, Parameter, Intermediate, and Final Bytes"""

        CsiNotFound = ("", "", "", schars)

        assert CSI_PIF_REGEX == r"(\x1B\[)" r"([0-?]*)" r"([ -/]*)" r"(.)"  # 4 Kinds of Bytes

        m = re.match(r"(\x1B\[)" r"([0-?]*)" r"([ -/]*)" r"(.)", string=schars)
        if not m:
            return CsiNotFound

        csi = m.group(1)
        p = m.group(2)  # Parameter Bytes
        i = m.group(3)
        f = m.group(4)  # Final Byte

        o = (csi, p, i, f, schars)
        assert (csi + p + i + f) == schars, o

        return (csi, p, i, f)

        # returns Falsey Csi when not a CSI Escape Sequence

    #
    # Emulate a more functional Terminal
    #

    def columns_delete_n(self, n) -> None:  # a la VT420 DECDC ⎋['~
        """Delete N Columns (but snap the Cursor back to where it started)"""

        assert DCH_X == "\x1B" "[" "{}P"  # CSI 05/00 Delete Character
        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

        (y_rows, x_columns) = self.y_rows_x_columns_read(timeout=0)
        (y_row, x_column) = self.row_y_column_x_read(timeout=0)

        for y in range(1, y_rows + 1):
            ctext = "\x1B" "[" f"{y}d"
            ctext += "\x1B" "[" f"{n}P"
            self.schars_write(ctext)

        ctext = "\x1B" "[" f"{y_row}d"
        self.schars_write(ctext)

    def columns_insert_n(self, n) -> None:  # a la VT420 DECIC ⎋['}
        """Insert N Columns (but snap the Cursor back to where it started)"""

        assert ICH_X == "\x1B" "[" "{}@"  # CSI 04/00 Insert Character
        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

        (y_rows, x_columns) = self.y_rows_x_columns_read(timeout=0)
        (y_row, x_column) = self.row_y_column_x_read(timeout=0)

        for y in range(1, y_rows + 1):
            ctext = "\x1B" "[" f"{y}d"
            ctext += "\x1B" "[" f"{n}@"
            self.schars_write(ctext)

        ctext = "\x1B" "[" f"{y_row}d"
        self.schars_write(ctext)

    #
    # Print or Write Str's of Chars
    #

    def schars_print(self, *args, end="\n") -> None:
        """Write Chars to the Screen as one or more Ended Lines"""

        sep = " "
        join = sep.join(str(_) for _ in args)
        ended = join + end

        schars = ended.replace("\n", "\r\n")
        self.schars_write(schars)

    def schars_write(self, schars) -> None:
        """Write Chars to the Screen, but without implicitly also writing a Line-End afterwards"""

        bt = self.bytes_terminal

        sbytes = schars.encode()
        bt.sbytes_write(sbytes)


class GlassTeletype:
    """Write/ Read Chars at Screen/ Keyboard of a Monospaced Rectangular Terminal"""

    bytes_terminal: BytesTerminal
    str_terminal: StrTerminal

    # FIXME: Snoop a guess of what Chars in which Columns of which Rows
    # FIXME: Draw the new, undraw the old only where not already replaced

    #
    # Init, enter, exit, breakpoint
    #

    def __init__(self) -> None:

        st = StrTerminal()

        self.bytes_terminal = st.bytes_terminal
        self.str_terminal = st

        glass_teletypes.append(self)

    def __enter__(self) -> "GlassTeletype":  # -> typing.Self:
        st = self.str_terminal
        st.__enter__()
        return self

    def __exit__(self, *exc_info) -> None:
        st = self.str_terminal
        st.__exit__()

    def breakpoint(self) -> None:

        st = self.str_terminal

        st.__exit__()
        getsignal = signal.getsignal(signal.SIGINT)

        breakpoint()  # where, up, down, ...
        pass

        signal.signal(signal.SIGINT, getsignal)
        st.__enter__()

    #
    # Delegate work to the Str Terminal
    #

    def schars_write(self, schars) -> None:
        st = self.str_terminal
        st.schars_write(schars)

    def os_terminal_y_row_x_column(self) -> tuple[int, int]:
        st = self.str_terminal
        (y_row, x_column) = st.row_y_column_x_read(timeout=0)
        return (y_row, x_column)

    def os_terminal_y_rows_x_columns(self) -> tuple[int, int]:
        st = self.str_terminal
        (y_rows, x_columns) = st.y_rows_x_columns_read(timeout=0)
        return (y_rows, x_columns)

    #
    # Loop Keyboard Bytes back onto the Screen
    #

    def kchord_write_kbytes_else_print_kstr(self, kchord) -> None:
        """Write 1 Key Chord, else print its Key Caps"""

        (kbytes, kcaps) = kchord
        sbytes = kbytes
        schars = kbytes.decode()  # may raise UnicodeDecodeError

        bt = self.bytes_terminal
        st = self.str_terminal

        assert DECIC_X == "\x1B" "[" "{}'}}"  # CSI 02/07 07/13 DECIC_X  # "}}" to mean "}"
        assert DECDC_X == "\x1B" "[" "{}'~"  # CSI 02/07 07/14 DECDC_X

        # self.schars_print(kcaps, end="  ")  # jitter Mon 23/Dec

        if not st.schars_to_writable(schars):
            st.schars_print(kcaps)
        else:
            (csi, p, i, f) = st.schars_csi_partition(schars)
            if csi:
                if not p:
                    n = 1
                elif re.fullmatch("[0-9]+", string=p):
                    n = int(p)
                else:
                    n = None

                if n is not None:
                    if (i + f) == "'}":
                        st.columns_insert_n(n)
                        return
                    elif (i + f) == "'~":
                        st.columns_delete_n(n)
                        return

            bt.sbytes_write(sbytes)


glass_teletypes: list[GlassTeletype]
glass_teletypes = list()


#
# Chat with 1 Logo Turtle
#


class Turtle:
    """Chat with 1 Logo Turtle"""

    glass_teletype: GlassTeletype

    float_x: float  # sub-pixel horizontal x-coordinate position
    float_y: float  # sub-pixel vertical y-coordinate position
    heading: float  # stride direction

    penscape: str  # setup written before punching a mark  # '\x1B[m'
    penmark: str  # mark to punch at each step
    warping: bool  # moving without punching, or not
    hiding: bool  # hiding the Turtle, or not

    rest: float  # min time between marks

    # todo: tada_func_else: typing.Callable | None  # runs once before taking next Command

    def __init__(self, glass_teletype=None) -> None:

        if glass_teletype is None:
            self.glass_teletype = glass_teletypes[-1]
        else:
            self.glass_teletype = glass_teletype

        self._reinit_()

    def _reinit_(self) -> None:
        """Clear the Turtle's Settings, but without writing the Screen"""

        self.float_x = 0e0
        self.float_y = 0e0
        self.heading = 360e0  # 360° of North Up Clockwise

        self.penscape = "\x1B[m"  # CSI 06/13 Select Graphic Rendition (SGR)
        self.penmark = FullBlock
        self.warping = False
        self.hiding = False

        self.rest = 1 / 1e3

        # todo: self.tada_func_else = None

        # macOS Terminal Sh Launch/ Quit doesn't clear the Graphic Rendition, Cursor Style, etc

    def clearscreen(self) -> None:
        """Write Spaces over every Character of every Screen Row and Column"""

        text = "\x1B[2J"  # CSI 04/10 Erase in Display  # 0 Tail # 1 Head # 2 Rows # 3 Scrollback
        gt = self.glass_teletype
        gt.schars_write(text)

        # just the Screen, not also its Scrollback

        # Scratch: Erase-All

        # todo: undo/ clear Turtle Trails separately

    def relaunch(self) -> dict:
        """Warp the Turtle to Home, and clear its Settings, and clear the Screen"""

        self.restart()
        self.clearscreen()

        d = self.asdict()
        return d

        # FmsLogo Clean deletes 1 Turtle's trail, without clearing its Settings
        # PyTurtle Clear deletes 1 Turtle's Trail, without clearing its Settings

    def restart(self) -> dict:
        """Warp the Turtle to Home, and clear its Settings, but do Not clear the Screen"""

        self._reinit_()

        self.hideturtle()
        self.penup()
        self.home()
        self.pendown()
        self.setpencolor()
        self.showturtle()

        d = self.asdict()
        return d

        # todo: Terminal Cursor Styles

    def asdict(self) -> dict:
        """Show the Turtle's Settings as a Dict"""

        d = {
            "float_x": self.float_x,
            "float_y": self.float_y,
            "heading": self.heading,
            "penscape": self.penscape,
            "penmark": self.penmark,
            "warping": self.warping,
            "hiding": self.hiding,
            "rest": self.rest,
        }

        return d

    #
    # Define what 1 Turtle can do
    #

    def backward(self, distance=None) -> dict:
        """Move the Turtle backwards along its Heading, tracing a Trail if Pen Down"""

        float_stride = 200e0 if (distance is None) else float(distance)
        self._punch_bresenham_stride_(-float_stride)

        d = dict(float_x=self.float_x, float_y=self.float_y)
        return d

        # Assymetric defaults for 🐢 Backward and 🐢 Forward make their Distance Arg more discoverable

    def beep(self) -> dict:
        """Ring the Terminal Alarm Bell once, remotely inside the Turtle"""

        text = "\a"  # Alarm Bell
        gt = self.glass_teletype
        gt.schars_write(text)

        # time.sleep(2 / 3)  # todo: guess more accurately when the Terminal Bell falls silent

        return dict()

        # 'def beep' not found in PyTurtle

    # todo: def x +=
    # Scratch: Change-X-By-10

    # todo: def y +=
    # Scratch: Change-Y-By-10

    # FIXME: Resort - Label into the L's, and review/ correct the other Def's
    def label(self, *args) -> dict:
        """Write 0 or more Args"""

        gt = self.glass_teletype
        heading = self.heading

        if round(heading) != 90:
            raise NotImplementedError("Printing Labels for Headings other than 90° East")

            # todo: Printing Labels for 180° South Heading
            # todo: Printing Labels for Headings other than 90° East and 180° South

        (y_row, x_column) = gt.os_terminal_y_row_x_column()

        line = " ".join(str(_) for _ in args)
        line += f"\x1B[{y_row};{x_column}H"  # CSI 06/12 Cursor Position  # 0 Tail # 1 Head # 2 Rows # 3 Columns]"
        line += "\n"  # just Line-Feed \n without Carriage-Return \r

        gt.schars_write(line)

        d = dict(float_x=self.float_x, float_y=self.float_y)
        return d

        # PyTurtle: (nope)
        # Scratch: Say

        # todo: most Logo's feel the Turtle should remain unmoved after printing a Label??

    def forward(self, distance=None) -> dict:
        """Move the Turtle forwards along its Heading, tracing a Trail if Pen Down"""

        float_stride = 100e0 if (distance is None) else float(distance)
        self._punch_bresenham_stride_(float_stride)

        d = dict(float_x=self.float_x, float_y=self.float_y)
        return d

        # Assymetric defaults for 🐢 Forward and 🐢 Backward make their Distance Arg more discoverable

        # Scratch Move-10-Steps (with infinite speed)
        # Scratch Glide-1-Secs-To-X-0-Y-0 (locks out parallel work)

    def hideturtle(self) -> dict:
        """Stop showing where the Turtle is"""

        gt = self.glass_teletype

        text = "\x1B[?25l"  # 06/12 Reset Mode (RM) 25 VT220 DECTCEM
        gt.schars_write(text)

        self.hiding = True

        d = dict(hiding=self.hiding)
        return d

    def isdown(self) -> bool:
        """Say if the Turtle will leave a Trail as it moves"""

        down = not self.warping
        return down

        # Lisp'ish Logo's say IsDown as PenDownP and as PenDown?

    def isvisible(self) -> bool:
        """Say if the Turtle is showing where it is"""

        visible = not self.hiding
        return visible

        # Lisp'ish Logo's say IsVisible as ShownP and as Shown?

    def home(self) -> dict:
        """Move the Turtle to its Home and turn it North, tracing a Trail if Pen Down"""

        self.setxy()  # todo: different Homes for different Turtles
        self.setheading()

        d = dict(float_x=self.float_x, float_y=self.float_y, heading=self.heading)
        return d

    def left(self, angle=None) -> dict:
        """Turn the Turtle anticlockwise, by a 45° Right Angle, or some other Angle"""

        float_angle = 45e0 if (angle is None) else float(angle)
        heading = self.heading

        d = self.setheading(heading - float_angle)
        return d

        # Assymetric defaults for 🐢 Left and 🐢 Right make their Angle Arg more discoverable

        # Scratch Turn-CCW-15-Degrees

    def pendown(self) -> dict:
        """Plan to leave a Trail as the Turtle moves"""

        self.warping = False

        d = dict(warping=self.warping)
        return d

        # Scratch Pen-Down

        # todo: calculated boolean args for pd pu ht gt

    def penup(self) -> dict:
        """Plan to Not leave a Trail as the Turtle moves"""

        self.warping = True

        d = dict(warping=self.warping)
        return d

        # Scratch Pen-Up

    def repeat(self, count=None) -> dict:
        """Run some instructions a chosen number of times, often less or more than once"""

        count = 1 if (count is None) else int(count)
        if not count:
            self.forward(0)  # punches the initial pixel without moving on
            self.right(0)  # mostly harmless
        else:
            angle = 360e0 / count
            for _ in range(count):
                self.forward()  # the traditional [fd rt]
                self.right(angle)  # todo: never the countercultural [rt fd]

        d = dict(float_x=self.float_x, float_y=self.float_y, heading=self.heading)
        return d

    def right(self, angle=None) -> dict:
        """Turn the Turtle clockwise, by a 90° Right Angle, or some other Angle"""

        float_angle = 90e0 if (angle is None) else float(angle)
        heading = self.heading  # turning clockwise

        d = self.setheading(heading + float_angle)
        return d

        # 🐢 Right 90° sets up 🐢 Label to print English from left to right
        # Assymetric defaults for 🐢 Right and 🐢 Left make their Angle Arg more discoverable

        # Scratch Turn-CW-15-Degrees

    def setheading(self, angle=None) -> dict:
        """Turn the Turtle to move 0° North, or to some other Heading"""

        float_angle = 0e0 if (angle is None) else float(angle)  # 0° of North Up Clockwise
        heading1 = float_angle % 360e0  # 360° Circle
        heading2 = 360e0 if not heading1 else heading1

        self.heading = heading2

        d = dict(heading=self.heading)
        return d

    def sethertz(self, hertz=None) -> dict:

        rest1 = 0e0
        float_hertz = 1000e0 if (hertz is None) else float(hertz)
        if float_hertz:
            rest1 = 1 / float_hertz

        self.rest = rest1

        d = dict(rest=self.rest)
        return d

        # PyTurtle Speed chooses 1..10 for faster animation, reserving 0 for no animation

    def setpencolor(self, color=None) -> dict:
        """Choose which Color to draw with"""

        gt = self.glass_teletype

        floatish = isinstance(color, float) or isinstance(color, int) or isinstance(color, bool)
        if color is None:
            penmode1 = "\x1B[m"  # CSI 06/13 Select Graphic Rendition (SGR)
        elif floatish or isinstance(color, decimal.Decimal):
            penmode1 = self._rgb_to_penmode_(rgb=int(color))
        elif isinstance(color, str):
            if color.casefold() == "None".casefold():
                penmode1 = "\x1B[m"  # CSI 06/13 Select Graphic Rendition (SGR)
            else:
                penmode1 = self._colorname_to_penmode_(colorname=color)
        else:
            assert False, (type(color), color)

        gt.schars_write(penmode1)

        self.penscape = penmode1

        d = dict(penscape=self.penscape)
        return d

        # todo: Scratch Change-Pen-Color-By-10

    _rgb_by_name_ = {
        "white": 0xFFFFFF,
        "magenta": 0xFF00FF,
        "blue": 0x0000FF,
        "cyan": 0x00FFFF,
        "green": 0x00FF00,
        "yellow": 0xFFFF00,
        "red": 0xFF0000,
        "black": 0x000000,
    }

    _ansi_by_rgb_ = {  # CSI 06/13 Select Graphic Rendition (SGR)  # 30+ Display Foreground Color
        0xFFFFFF: "\x1B[37m",
        0xFF00FF: "\x1B[35m",
        0x0000FF: "\x1B[34m",
        0x00FFFF: "\x1B[36m",
        0x00FF00: "\x1B[32m",
        0xFFFF00: "\x1B[33m",
        0xFF0000: "\x1B[31m",
        0x000000: "\x1B[30m",
    }

    def _colorname_to_penmode_(self, colorname) -> str:

        casefold = colorname.casefold()
        colornames = sorted(_.title() for _ in self._rgb_by_name_.keys())
        if casefold not in self._rgb_by_name_.keys():
            raise KeyError(f"{colorname!r} not in {colornames}")

        rgb = self._rgb_by_name_[casefold]
        penscape = self._ansi_by_rgb_[rgb]
        return penscape

    def _rgb_to_penmode_(self, rgb) -> str:
        penscape = self._ansi_by_rgb_[rgb]
        return penscape

    def setpenpunch(self, ch=None) -> dict:
        """Choose which Character to draw with, or default to '*'"""

        floatish = isinstance(ch, float) or isinstance(ch, int) or isinstance(ch, bool)
        if ch is None:
            penmark1 = FullBlock
        elif floatish or isinstance(ch, decimal.Decimal):
            penmark1 = chr(int(ch))  # not much test of '\0' yet
        elif isinstance(ch, str):
            # assert len(ch) == 1, (len(ch), ch)  # todo: unlock vs require Len 1 after dropping Sgr's
            penmark1 = ch
        else:
            assert False, (type(ch), ch)

        self.penmark = penmark1

        d = dict(penmark=self.penmark)
        return d

        # todo: With SetPenColor Forward 1:  "!" if (penmark == "~") else chr(ord(penmark) + 1)

    # todo: def setx
    # Scratch: Set-X-To-0

    # todo: def sety
    # Scratch: Set-Y-To-0

    # FIXME: Resort after Rename
    def setxy(self, x=None, y=None) -> dict:
        """Move the Turtle to an X Y Point, tracing a Trail if Pen Down"""

        float_x = 0e0 if (x is None) else float(x)
        float_y = 0e0 if (y is None) else float(y)

        (x1, y1) = self.x_y_position()

        x2 = round(float_x / 10)  # / 10 to a screen of a few large pixels
        y2 = round(float_y / 10 / 2)  # / 2 for thin pixels

        self._punch_bresenham_segment_(x1, y1=y1, x2=x2, y2=y2)

        self.float_x = float_x  # not 'float_x_'
        self.float_y = float_y  # not 'float_y_'

        d = dict(float_x=self.float_x, float_y=self.float_y)
        return d

        # FMSLogo SetXY & UBrown SetXY & UCBLogo SetXY alias SetPos
        # PyTurtle Goto aliases SetPos, PyTurtle Teleport is With PenUp SetPos
        # Scratch Point-In-Direction-90
        # Scratch Go-To-X-Y
        # UCBLogo Goto is a Control Flow Goto

        # todo: setx without setxy, sety without setxy

    def showturtle(self) -> dict:
        """Start showing where the Turtle is"""

        gt = self.glass_teletype
        # hiding = self.hiding

        text = "\x1B[?25h"  # 06/08 Set Mode (SMS) 25 VT220 DECTCEM
        gt.schars_write(text)

        self.hiding = False
        # if self.hiding != hiding:
        #     print(f"hiding={self.hiding}  # was {hiding}")

        # Forward 0 leaves a Mark to show Turtle was Here
        # SetXY from Home leaves a Mark to show the X=0 Y=0 Home

        d = dict(hiding=self.hiding)
        return d

    def sleep(self) -> dict:
        """Hold the Turtle still for a moment"""

        rest = self.rest
        time.sleep(rest)  # todo: give credit for delay in work before t.sleep

        d = dict(rest=self.rest)
        return d

        # tested with:  sethertz 5  st s ht s  st s ht s  st s ht s  st

    # todo: def tada(self) -> None:
    #     """Hide the Turtle, but only until next Call"""
    #
    #     gt = self.glass_teletype
    #     text = "\x1B[?25l"  # 06/12 Reset Mode (RM) 25 VT220 DECTCEM
    #     gt.schars_write(text)
    #
    #     def tada_func() -> None:
    #         text = "\x1B[?25h"  # 06/08 Set Mode (SMS) 25 VT220 DECTCEM
    #         gt.schars_write(text)
    #
    #     self.tada_func_else = tada_func

    #
    # Move the Turtle along the Line of its Heading
    #

    def _punch_bresenham_stride_(self, stride) -> None:
        """Step forwards, or backwards, along the Heading"""

        stride_ = float(stride) / 10  # / 10 to a screen of a few large pixels

        heading = self.heading  # 0° North Up Clockwise

        # Choose the Starting Point

        (x1, y1) = self.x_y_position()
        float_x = self.float_x
        float_y = self.float_y
        assert (x1 == round(float_x)) and (y1 == round(float_y)), (x1, float_x, y1, float_y)

        # Choose the Ending Point

        angle = (90 - heading) % 360e0  # converts to 0° East Anticlockwise
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
            # print(f"FUZZ1 {stride_=} {angle=} {x1=} {y1=} {x2=} {y2=} {float_x_} {float_y_} FUZZ1")
            x2 = int(float_x_)
            y2 = int(float_y_)

            # got:  cs  pu home reset pd  rt rt fd  rt fd 400
            # wanted:  cs  reset pd  setpch '.'  pu setxy ~400 ~100  pd rt fd 400 lt fd
            # surfaced by:  demos/headings.logo

        # Draw the Line Segment to X2 Y2 from X1 Y1

        self._punch_bresenham_segment_(x1, y1=y1, x2=x2, y2=y2)
        # print(f"float {float_x} {float_y} {float_x__} {float_y__}")

        # Option to show why keep up Precise X Y Shadows in .float_x .float_y

        fuzz2 = True
        fuzz2 = False
        if fuzz2:  # fail test of:  cs  reset pd  fd rt 72  fd rt 72  fd rt 72  fd rt 72  fd rt 72
            # print(f"FUZZ2 {stride_=} {angle=} {x1=} {y1=} {x2=} {y2=} {float_x__} {float_y__} FUZZ2")
            float_x__ = float(x2)
            float_y__ = float(y2)

            # got Pentagon overshot:  cs  reset pd  fd rt 72  fd rt 72  fd rt 72  fd rt 72  fd rt 72
            # got Octogon overshot:  cs  reset pd  rep 8 [fd rt 45]
            # wanted close like:  cs  reset pd  fd rt 120  fd rt 120  fd rt 120
            # wanted close like:  cs  reset pd  rep 4 [fd rt 90]
            # surfaced by:  walking polygons

        self.float_x = float_x__
        self.float_y = float_y__

    def _punch_bresenham_segment_(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Step forwards, or backwards, through (Row, Column) choices"""

        assert isinstance(x1, int), (type(x1), x1)
        assert isinstance(y1, int), (type(y1), y1)
        assert isinstance(y2, int), (type(y2), y2)
        assert isinstance(x2, int), (type(x2), x2)

        # print(f"{x1=} {y1=} ({2 * y1}e0)  {x2=} {y2=} ({2 * y2}e0)")

        x2x1 = abs(x2 - x1)  # distance
        y2y1 = abs(y2 - y1)

        sx = 1 if (x1 < x2) else -1  # steps towards X2 from X1
        sy = 1 if (y1 < y2) else -1  # steps towards Y2 from y1

        e = x2x1 - y2y1  # Bresenham's Error Measure

        wx = x = x1
        wy = y = y1
        while True:

            self._jump_then_punch_(wx, wy=-wy, x=x, y=-y)
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

    def _jump_then_punch_(self, wx, wy, x, y) -> None:
        """Move the Turtle by 1 Column or 1 Row or both, and punch out a Mark if Pen Down"""

        gt = self.glass_teletype
        hiding = self.hiding
        warping = self.warping
        penmark = self.penmark
        rest = self.rest

        # # print(f"{x} {y}")

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
        if not warping:
            pc_text = penmark + (len(penmark) * "\b")
            text = f"{y_text}{x_text}{pc_text}"

        gt.schars_write(text)

        if not hiding:
            time.sleep(rest)

    def x_y_position(self) -> tuple[int, int]:
        """Sample the X Y Position remotely, inside the Turtle"""

        gt = self.glass_teletype

        float_x = self.float_x
        float_y = self.float_y

        # Find the Cursor

        (y_row, x_column) = gt.os_terminal_y_row_x_column()

        # Find the Center of Screen

        (y_rows, x_columns) = gt.os_terminal_y_rows_x_columns()
        cx = 1 + (x_columns // 2)
        cy = 1 + (y_rows // 2)

        # Say how far away from Center the Cursor is, on a plane of Y is Up and X is Right

        x1 = x_column - cx
        y1 = -(y_row - cy)

        # Snap the Shadow to the Cursor Row-Column, if the Cursor moved

        if (x1 != round(float_x)) or (y1 != round(float_y)):
            float_x_ = float(x1)  # 'explicit is better than implicit'
            float_y_ = float(y1)

            # print(f"snap to {float_x_} {float_y_} from {float_x} {float_y}")
            self.float_x = float_x_
            self.float_y = float_y_

        # Succeed

        return (x1, y1)

        # a la PyTurtle Position
        # a la FMSLogo Pos
        # a la UCBLogo X Y Pos, XCor, YCor


#
# Auto-complete Turtle Logo Sourcelines to run as Python
#


class PythonSpeaker:
    """Auto-complete Turtle Logo Sourcelines to run as Python"""

    def text_to_pycalls(self, text, cls) -> list[str]:
        """Auto-complete Turtle Logo Sourcelines to run as Python"""

        funcnames = self.cls_to_funcnames(cls)

        pycalls = list()

        # Forward Python unchanged

        parseable = text
        parseable = parseable.replace("-", "~")  # refuse '-' as bin op, accept as unary op
        parseable = parseable.replace("+", "~")  # refuse '+' as bin op, accept as unary op

        before_strip = text.partition("#")[0].strip()
        if before_strip not in funcnames:
            try:
                ast.parse(parseable)
                pycalls.append(text)
                return pycalls
            except SyntaxError:  # from Ast Parse
                pass

        # Split the Text into Python Texts

        assert not self.pysplit_to_pylit_if("", funcnames=funcnames)

        call_pysplits: list[str]
        call_pysplits = list()

        text_pysplits = self.splitpy(text) + [""]
        for pysplit in text_pysplits:
            if pysplit.lstrip().startswith("#"):
                continue

            pylit = self.pysplit_to_pylit_if(pysplit, funcnames=funcnames)
            if pylit:

                if not call_pysplits:
                    call_pysplits.append("p")
                call_pysplits.append(pylit)

            else:

                if call_pysplits:
                    pyline = self.pysplits_to_pyline(call_pysplits, funcnames=funcnames)
                    pycall = pyline
                    pycalls.append(pycall)

                call_pysplits.clear()
                call_pysplits.append(pysplit)

        assert call_pysplits == [""], (call_pysplits,)

        return pycalls

    def splitpy(self, text) -> list[str]:
        """Split 1 Text into its widest parseable Py Expressions from the Left"""

        splits = list()

        more = text
        while more:

            if more.lstrip().startswith("#"):
                split = more
                splits.append(split)
                break

            heads = list()
            for index in range(0, len(more)):
                length = index + 1
                head = more[:length]

                parseable = head
                parseable = parseable.replace("-", "~")  # refuse '-' as bin op, accept as unary op
                parseable = parseable.replace("+", "~")  # refuse '+' as bin op, accept as unary op

                try:
                    ast.literal_eval(parseable)
                    heads.append(head)
                except ValueError:
                    heads.append(head)
                except SyntaxError:
                    pass

            if not heads:
                splits.append(more)
                break

            head = heads[-1]
            assert head, (
                head,
                more,
            )

            split = head
            if "#" in head:
                if ('"' not in head) and ("'" not in head):
                    before = split.partition("#")[0]
                    split = before.rstrip()
                    assert split, (
                        split,
                        head,
                        more,
                    )

            splits.append(split)

            more = more[len(split) :]

        assert "".join(splits) == text, (splits, text)

        return splits

    def pysplit_to_pylit_if(self, py, funcnames) -> str:
        """Say if Py Text is a literal Py Expression"""

        strip = py.strip()
        try:

            ast.literal_eval(strip)

        except ValueError:

            pylit = repr(strip)
            if strip in funcnames:
                return ""
            return pylit

        except SyntaxError:

            return ""

        return py

    def pysplits_to_pyline(self, pysplits, funcnames) -> str:
        """Convert some Py Texts into a Py Call with Args"""

        assert pysplits, (pysplits,)

        funcname_by_grunt = self.funcname_by_grunt

        strip_0 = pysplits[0].strip()

        funcname = strip_0
        if strip_0 in funcnames:
            if strip_0 in funcname_by_grunt:
                funcname = "t." + funcname_by_grunt[strip_0]
            else:
                funcname = "t." + strip_0

        args = pysplits[1:]
        join = ", ".join(_.strip() for _ in args)

        pyline = f"{funcname}({join})"

        return pyline

    byo_funcname_by_grunt = {
        "b": "beep",
        "clear": "clearscreen",  # Linux Clear  # macOS ⌘K
        "cls": "clearscreen",  # MsDos Cls
        "rep": "repeat",
        "sethz": "sethertz",
        "setpch": "setpenpunch",
        "s": "sleep",
        "t": "tada",
    }

    py_funcname_by_grunt = {  # for the people of:  import turtle
        "back": "backward",
        "bk": "backward",
        # "down": "pendown",  # nope
        "fd": "forward",
        "goto": "setxy",
        "ht": "hideturtle",
        "lt": "left",
        "pd": "pendown",
        "pu": "penup",
        "reset": "restart",  # without ClearScreen
        "rt": "right",
        "seth": "setheading",
        "setpos": "setxy",
        "setposition": "setxy",
        "st": "showturtle",
        # "up": "penup",  # nope
    }

    ucb_funcname_by_grunt = {  # for the people of:  UCBLogo
        "cs": "clearscreen",
        "setpc": "setpencolor",
    }

    funcname_by_grunt = byo_funcname_by_grunt | py_funcname_by_grunt | ucb_funcname_by_grunt

    grunts = sorted(
        list(byo_funcname_by_grunt.keys())
        + list(py_funcname_by_grunt.keys())
        + list(ucb_funcname_by_grunt.keys())
    )

    assert grunts == sorted(set(grunts)), (grunts,)

    def cls_to_funcnames(self, cls) -> list[str]:
        """Say the Verb Names in a Class"""

        funcname_by_grunt = self.funcname_by_grunt

        names = list(_ for _ in dir(cls) if not _.startswith("_"))
        keys = list(funcname_by_grunt.keys())
        values = list(funcname_by_grunt.values())

        funcnames = sorted(set(names + keys + values))

        return funcnames


#
# Trade Texts across a pair of Named Pipes at macOS or Linux
#


class TurtlingFifoProxy:
    """Create/ find a Named Pipe and write/ read it"""

    basename: str  # 'requests'

    find: str  # '__pycache__/turtling/pid=12345/responses.mkfifo'
    pid: int  # 12345
    fileno: int  # 3
    index: int  # -1

    def __init__(self, basename) -> None:

        assert basename in ("requests", "responses"), (basename,)

        self.basename = basename

        self.find = ""
        self.pid = -1
        self.fileno = -1
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

        if self.fileno < 0:
            self.fd_open_write_once()
            assert self.fileno >= 0, (self.fileno,)

        self.fd_write_text(self.fileno, text=text)

    def fd_open_write_once(self) -> int:
        """Open to write, if not open already. Block till a Reader opens the same Pipe"""

        find = self.find
        fileno = self.fileno
        assert find, (find,)

        if fileno >= 0:
            return fileno

        fileno = os.open(find, os.O_WRONLY)
        assert fileno >= 0

        self.fileno = fileno

        return fileno

    def fd_write_text(self, fileno, text) -> None:
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

        os.write(fileno, encode)  # todo: no need for .fdopen .flush?

    def read_text_else(self) -> str | None:
        """Read Chars in as an indexed Request that starts with its own Length"""

        if self.fileno < 0:
            self.fd_open_read_once()
            assert self.fileno >= 0, (self.fileno,)

        rtext_else = self.fd_read_text_else(self.fileno)
        return rtext_else

    def fd_open_read_once(self) -> int:
        """Open to read, if not open already. Block till a Writer opens the same Pipe"""

        find = self.find
        fileno = self.fileno
        assert find, (find,)

        if fileno >= 0:
            return fileno

        fileno = os.open(find, os.O_RDONLY)
        assert fileno >= 0

        self.fileno = fileno

        return fileno

    def fd_read_text_else(self, fileno) -> str | None:
        """Read Chars in as an indexed Request that starts with its own Length"""

        index = self.index
        self.index = index + 1

        # Read the Bytes of the Chars

        blank_head_encode = f"length=0x{0:019_X}\n".encode()
        len_head_bytes = len(blank_head_encode)

        head_bytes = os.read(fileno, len_head_bytes)
        if not head_bytes:
            return None

        assert len(head_bytes) == len_head_bytes, (len(head_bytes), len_head_bytes)
        head_text = head_bytes.decode()

        str_encode_length = head_text.partition("length=")[-1]
        encode_length = int(str_encode_length, 0x10)
        assert head_text == f"length=0x{encode_length:019_X}\n", (head_text, encode_length)

        tail_bytes_length = encode_length - len(head_bytes)
        tail_bytes = os.read(fileno, tail_bytes_length)
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


#
# Attach to a Turtling Server
#


TurtlingWriter = TurtlingFifoProxy("requests")

TurtlingReader = TurtlingFifoProxy("responses")


def turtling_server_attach() -> bool:
    """Start trading Texts with a Turtling Server"""

    reader = TurtlingReader
    writer = TurtlingWriter

    if not reader.find_mkfifo_once_if(pid="*"):
        return False  # Turtling Server not-found
    assert reader.pid >= 0, (reader.pid,)

    pid = reader.pid

    if not writer.find_mkfifo_once_if(pid):
        writer.create_mkfifo_once(pid)

    writer.write_text("")
    read_text_else = reader.read_text_else()
    if read_text_else != "":
        assert False, (read_text_else,)  # Turtling Server texts index not synch'ed

    assert writer.index == 0, (writer.index, reader.index)
    if reader.index != writer.index:
        assert reader.index > 0, (reader.index,)
        writer.index = reader.index

    return True


#
# Run as a Server drawing with Logo Turtles
#


def turtling_server_run() -> None:
    "Run as a Server drawing with Logo Turtles and return True, else return False"

    with GlassTeletype() as gt:
        ts1 = TurtlingServer(gt)
        ts1.server_run_till()


class TurtlingServer:

    glass_teletype: GlassTeletype
    locals_: dict[str, object]

    def __init__(self, glass_teletype) -> None:

        locals_: dict[str, object]
        locals_ = dict()
        locals_["self"] = self

        self.glass_teletype = glass_teletype
        self.locals_ = locals_

    def server_run_till(self) -> None:
        """Draw with Logo Turtles"""

        gt = self.glass_teletype
        st = gt.str_terminal
        bt = gt.bytes_terminal
        bt_fd = bt.fileno  # todo: .file_descriptor

        pid = os.getpid()

        writer = TurtlingFifoProxy("responses")
        reader = TurtlingFifoProxy("requests")

        # Start up

        writer.pid_create_dir_once(pid)
        writer.create_mkfifo_once(pid)

        st.schars_print(f"At your service as {pid=} till you press ⌃D")

        reader_fd = -1
        while True:
            bt.sbytes_flush()  # todo: skip flush if selects were empty?

            # Block till Input or Timeout

            fds = list()
            fds.append(bt_fd)
            if reader_fd >= 0:
                assert reader_fd == reader.fileno, (reader_fd, reader.fileno)
                fds.append(reader_fd)

            timeout = 0.100
            selects = select.select(fds, [], [], timeout)
            select_ = selects[0]

            # Reply to 1 Keyboard Chord

            if bt_fd in select_:
                kchord = self.keyboard_serve_one_kchord()
                if kchord[-1] == "⌃D":
                    break

            # Reply to 1 Client Text

            if reader_fd in select_:
                self.reader_writer_serve(reader, writer=writer)
                continue

            # Reply to 1 Client Arrival

            if reader_fd < 0:
                if reader.find_mkfifo_once_if(pid):  # 0..10 ms
                    reader_fd = reader.fd_open_read_once()
                    assert reader_fd == reader.fileno, (reader_fd, reader.fileno)

    def keyboard_serve_one_kchord(self) -> tuple[bytes, str]:
        """Reply to 1 Keyboard Chord"""

        gt = self.glass_teletype
        st = gt.str_terminal

        kchord = st.kchord_pull(timeout=1.000)
        gt.kchord_write_kbytes_else_print_kstr(kchord)

        return kchord

    def reader_writer_serve(self, reader, writer) -> None:
        """Read a Python Text in, write back out the Repr of its Eval"""

        reader_fd = reader.fileno

        globals_ = globals()
        locals_ = self.locals_

        gt = self.glass_teletype
        st = gt.str_terminal

        # Read a Python Text In

        rtext_else = reader.fd_read_text_else(reader_fd)
        if rtext_else is None:
            st.schars_print("EOFError")
            writer.index += 1  # as if written
            return

        rtext = rtext_else
        py = rtext

        # Eval the Python Text (except eval "" Empty Str as same)

        wtext = ""

        if py:

            try:  # todo: shrug off PyLance pretending eval/exec 'locals=' doesn't work

                eval_ = eval(py, globals_, locals_)

            except NameError:  # from Py Eval

                eval_ = traceback.format_exc()

                eline = eval_.splitlines()[-1]
                m = re.match(r"NameError: name '([^']*)' is not defined\b", string=eline)
                if m:
                    ename = m.group(1)
                    pyname = py.partition("#")[0].strip()
                    if ename == pyname:
                        eval_ = ename

            except SyntaxError:  # from Py Eval

                eval_ = None
                try:
                    exec(py, globals_, locals_)
                except Exception:
                    eval_ = traceback.format_exc()

            except Exception:

                eval_ = traceback.format_exc()

            wtext = repr(eval_)

        # Write back out the Repr of its Eval (except write back "" Empty Str for same)

        if writer.fileno < 0:
            writer.fd_open_write_once()
            assert writer.fileno >= 0, (writer.fileno,)

        writer.fd_write_text(writer.fileno, text=wtext)


#
# Run as a Client chatting with Logo Turtles
#


def turtling_client_run(text) -> None:
    "Run as a Client chatting with Logo Turtles and return True, else return False"

    tc1 = TurtleClient()
    try:
        tc1.client_run_till(text)
    except BrokenPipeError:
        eprint("BrokenPipeError")


class TurtleClient:
    """Chat with the Logo Turtles of 1 Turtling Server"""

    def breakpoint(self) -> None:
        """Chat through a Python Breakpoint, but without redefining ⌃C SigInt"""

        getsignal = signal.getsignal(signal.SIGINT)

        breakpoint()
        pass

        signal.signal(signal.SIGINT, getsignal)

    def client_run_till(self, text) -> None:
        """Chat with Logo Turtles"""

        Bold = "\x1B[" "1m"  # Sgr Bold  # CSI 06/13 Select Graphic Rendition (SGR)
        Plain = "\x1B[" "m"  # Sgr Plain

        ps1 = f"{Turtle_}? {Bold}"
        postedit = Plain

        # Till quit

        ps = PythonSpeaker()

        started = False

        ilines = text.splitlines()
        if text == "relaunch":
            started = True

            eprint("BYO Turtling·Py 2024-12-29")
            trade_else = self.py_trade_else("t = turtling.Turtle(); t.relaunch()")
            assert trade_else is None, (trade_else,)
            ilines = list()  # replace

        while True:
            while ilines:
                iline = ilines.pop(0)

                # Echo the Line by itself, prefixed by a Prompt

                sys.stdout.flush()
                eprint(ps1 + iline + postedit)
                sys.stderr.flush()

                # Quickly dismiss a flimsy Line

                rstrip = iline.rstrip()
                if not self.text_has_pyweight(rstrip):
                    continue

                if rstrip == "import turtling":
                    started = True
                    print(rstrip)
                    continue

                if rstrip.startswith("t =") or rstrip.startswith("t="):
                    started = True

                # Auto-correct till it's Python
                # Send each Python Call to the Server, trace its Reply

                pycalls = ps.text_to_pycalls(rstrip, cls=Turtle)
                trades = list()
                for pycall in pycalls:
                    if pycalls != [rstrip]:  # if autocompleted
                        eprint(">>>", pycall)

                    trade_else = self.py_trade_else(pycall)
                    if trade_else is None:
                        continue

                    trade = trade_else
                    trades.append(trade)

                    print(trade)

                if trades:
                    print()

            # Prompt & Echo Lines from the Keyboard

            ilines = self.read_some_ilines(ps1, postedit=postedit)  # replace
            if not ilines:
                break

            # Insert start-up profile script if not supplied

            itext = "\n".join(ilines)
            if not started:
                if "import turtling" not in itext:
                    started = True

                    ilines[0:0] = ["import turtling", "t = turtling.Turtle()"]

    def read_some_ilines(self, ps1, postedit) -> list[str]:
        """Prompt & Echo Lines from the Keyboard"""

        sys.stdout.flush()
        eprint(ps1, end="")
        sys.stderr.flush()

        ilines = list()
        while True:
            itext = ""
            try:
                itext += sys.stdin.readline()
                while select.select([sys.stdin], [], [], 0.000)[0]:
                    itext += sys.stdin.readline()
            except KeyboardInterrupt:  # mostly shrugs off ⌃C SigInt
                eprint(" KeyboardInterrupt")
                self.breakpoint()
                continue

            ilines.extend(itext.splitlines())

            if not itext:
                eprint("")  # duck Incomplete ⌘K Clear of Screen
                return ilines

            with BytesTerminal() as bt:
                kbhit = bt.kbhit(timeout=0.000)

            if kbhit:  # when last Line started but not ended
                eprint("", end="\r")  # duck Doubled Echo of Line

            break

        eprint("\x1B[" f"{len(ilines)}A" "\x1B[" "J", end="")

        return ilines

    def text_has_pyweight(self, text) -> bool:
        """Say forward to Server if more than Blanks and Comments found"""

        for line in text.splitlines():
            py = line.partition("#")[0].strip()
            if py:
                return True

        return False

    def py_trade_else(self, py) -> str | None:
        """Send Python to the Server, trace its Reply"""

        globals_ = globals()

        def p(*args):
            text = ", ".join(repr(_) for _ in args)
            eprint(text)

        locals_ = dict(p=p)

        if py.startswith("p("):
            exec(py, globals_, locals_)
            return None

        wtext = py
        rtext_else = self.trade_text_else(wtext)
        if rtext_else is None:
            ptext = "EOFError"
            return ptext

        rtext = rtext_else
        if rtext.startswith("'Traceback (most recent call last):"):
            format_exc = eval(rtext)
            ptext = format_exc.rstrip()
            return ptext

        if rtext == "None":
            return None

        ptext = rtext
        return ptext

    def trade_text_else(self, wtext) -> str | None:
        """Write a Text to the Turtling Server, and read back a Text or None"""

        writer = TurtlingWriter
        reader = TurtlingReader

        writer.write_text(wtext)
        rtext_else = reader.read_text_else()

        return rtext_else


#
# Paint Turtle Character Graphics onto a Terminal Screen
#


r'''

class TurtleClientWas:
    """Run at Keyboard and Screen as a Shell, to command 1 Turtle via two MkFifo"""


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
            "showturtle gt": self.do_showturtle,
            "tada t": self.do_tada,
        }

        return d

    def do_bye(self) -> None:
        """Quit the Turtle Chat"""

        print("bye")  # not from "bye", "end", "exit", "quit", ...
        sys.exit()

    def do_help(self, pattern=None) -> None:
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

    def do_print(self, *args) -> None:
        """Print the Str of each Arg, separated by Spaces, and then 1 Line_Break"""

        print(*args)

'''


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
# todo: solve the thin flats left on screen behind:  reset cs pu  sethertz 10 rep 8
# also differs by Hertz:  reset cs pu  sethertz rep 8
# also:  sethertz cs pu setxy 250 250  sethertz 100 home
# also:  sethertz cs pu setxy 0 210  sethertz 100 home
#
#
# todo: solve why ↓ ↑ Keys too small - rounding trouble?:  demos/arrow-keys.logo
#
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
# todo: z-layers to animate a clock of hours/ minutes/ second hands
# todo: let more than 1 Turtle move onto a z-layer to keep only the latest
# todo: colorful spirography
# todo: marble games
# todo: menus w drop shadow & keyboard & mouse - a la Borland Dos Turbo C++
# todo: vi - emacs - notepad
# todo: 'batteries included better than homemade'
#
# todo: randomly go to corners till all eight connections drawn
# todo: Serpienski's Gasket, near to Koch Curve at F+F--F+F in Lindenmayer System
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
# todo: t.penmark should stay as the Chars only, but we always ⎋[Y;XH to where we were - vs thin grey
#
# todo: thicker X Y Pixels
#
# talk up gDoc for export, also Sh Screen TypeScript
# steganography for delays in TypeScript's
# work up export to gDoc tech for ending color without spacing to right of screen
#
# todo: edge cap cursor position, wrap, bounce, whine, stop
# todo: 500x500 canvas at U Brown of UCBLogo
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
# todo: e Pi Inf -Inf NaN ... sqrt power ... math.tau t.tau ...
# todo: print (p) repr's, cleartext (ct) mention ⌘K
# todo: setcursor [x y], cursor
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
# todo: 🐢 SetY, 🐢 SetX, for one-dimensional movement
#
# todo: 🐢 Pin to drop a pin (in float precision!)
# todo: 🐢 Go to get back to it
# todo: 🐢 Pin that has a name, and list them at 🐢 Go, and delete them if pinned twice in same place
#
# todo: or teach 🐢 Label to take a last arg of "" as an ask for no newline?
#
# todo: rep n [fd fd.d rt rt.angle]
# todo: 'to $name ... end' vs 'def $name [ ... ]'
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
# todo: VsCode for .logo, for .lgo, for .log, ...
#
# todo: reconcile with Python "import turtle" Graphics on TkInter
# todo: .rest vs Python Turtle screen.delay
# todo: .stride vs Logo SetStepSize
# todo: .rest vs Logo SetSpeed, SetVelocity, Wait
#
# todo: random moves, seeded random, random $n for random.randint(0, n)
# todo: cyclic moves in Color, in Pen Down, and help catalog more than 8 Colors
# todo: Pen Colors that mix with the Screen: PenPaint/ PenReverse/ PenErase
#
# todo: circles, ellipses
# todo: arc(angle, radius) with a design for center & end-position
# todo: arcs with more args at https://fmslogo.sourceforge.io/manual/command-ellipsearc.html
# todo: collisions, gravity, friction
#
# todo: context of Color Delay etc Space for Forward & Turn, like into irregular dance beat
# todo: more than 8 foreground colors, such as ⎋[38;5;130m orange
# todo: background colors, such as ⎋[38;5;130m orange
#
# todo: scroll and resize and reposition and iconify/ deiconify the window
#

#
# 🐢 Python Makeovers  # todo
#
#
# todo: factor out Class Turtle, think into running more than one
# todo: factor out 'import turtling'
#
# todo: def efprint1(self, form, **kwargs) at uturtle.Turtle for printing its Fields
# todo: print only first and then changes in the form result
#

#
# 🐢 Turtle Chat References
#
#   https://github.com/pelavarre/byoverbs/tree/main/docs
#       todo: turtling-in-the-python-terminal.md
#           output-at-right/left light/dark cap/bounce/wrap
#
#   FMSLogo for Linux Wine/ Windows (does the Linux Wine work?)
#   https://fmslogo.sourceforge.io
#   https://fmslogo.sourceforge.io/manual/index.html
#
#   Scratch
#   https://scratch.mit.edu
#   https://en.scratch-wiki.info/wiki
#   view-source:https://en.scratch-wiki.info/wiki/Scratch_Wiki:Table_of_Contents/Motion_Blocks
#       ⌘F >move
#
#   UCBLogo for Linux/ macOS/ Windows <- USA > U of California Berkeley (UCB)
#   https://people.eecs.berkeley.edu/~bh/logo.html
#   https://people.eecs.berkeley.edu/~bh/usermanual [.txt]
#   https://cs.brown.edu/courses/bridge/1997/Resources/LogoTutorial.html
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
