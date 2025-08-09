#!/usr/bin/env python3

r"""
usage: turtling.py [-h] [--version] [--yolo] [--stop] [-i] [-c COMMAND]

draw with Logo Python Turtles on a Terminal Window Tab Pane

options:
  -h, --help  show this message and exit
  --version   show version and exit
  --yolo      draw inside this Pane, else chat inside this Pane
  --stop      send Signal·SigKill to every Turtling·Py Process, as if Sh 'kill -9'
  -i          chat inside this Pane
  -c COMMAND  do some things, before quitting if no -i, or before chatting if -i

how to run the freshest Code from the web:
  python3 <(curl -Ss https://raw.githubusercontent.com/pelavarre/byoverbs/refs/heads/main/bin/turtling.py) --yolo

calls for help:
  turtling.py  # shows examples
  turtling.py --  # shorthand for turtling.py --yolo
  turtling.py --help  # shows this message and exits zero

examples:
  turtling.py --yolo  # draws inside this Pane, else chats inside this Pane
  turtling.py -i  # clears Pane, puts down one Turtle, and chats
  turtling.py -i -c ''  # doesn't clear Pane, puts down one Turtle, and chats
"""

# code reviewed by People, Black, Flake8, MyPy, & PyLance-Standard


import __main__
import argparse
import ast
import bdb
import collections
import datetime as dt
import decimal
import glob
import inspect
import math
import os
import pathlib
import pdb
import platform  # platform.system() 'Darwin' often lacks 24-Bit Terminal Color
import random
import re  # 're.fullmatch' since Mar/2014 Python 3.4
import select  # Windows sad at 'select.select' of Named Pipes
import shlex
import shutil
import signal
import string
import subprocess
import sys
import termios  # Windows sad
import textwrap
import time
import traceback
import tty  # Windows sad
import typing
import unicodedata
import warnings

# todo: add 'import mscvrt' at Windows


__version__ = "2025.3.15"  # Saturday

_ = dict[str, int] | None  # new since Oct/2021 Python 3.10


if "turtle" not in globals():
    globals()["turtle"] = sys.modules[__name__]
if "turtling" not in globals():
    globals()["turtling"] = sys.modules[__name__]


DegreeSign = unicodedata.lookup("Degree Sign")  # ° U+00B0
FullBlock = unicodedata.lookup("Full Block")  # █ U+2588
Turtle_ = unicodedata.lookup("Turtle")  # 🐢 U+01F422

Plain = "\x1b[" "m"  # Unstyled, uncolored, ...
Bold = "\x1b[" "1m"


COLOR_ACCENTS = (None, 3, 4, 4.6, 8, 24)  # Bits of Terminal Color (4.6 for 25-Step Grayscale)


if not __debug__:
    raise NotImplementedError(str((__debug__,)))  # "'python3' is better than 'python3 -O'"


#
# Run well from the Sh Command Line
#


def main() -> None:
    """Run well from the Sh Command Line, else launch the Pdb Post-Mortem Debugger"""

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
    """Run well from the Sh Command Line, else raise an Exception"""

    # Take the Stop Option as Auth to signal each Turtling Process

    if ns.stop:
        assert (not ns.i) and (ns.c is None), (ns.i, ns.c, ns.yolo, ns)

        turtling_processes_stop()
        return

    # Take the Yolo Option as Auth to run as a Chat Pane of the first Drawing Pane,
    # else to run as the first Drawing Pane

    if ns.yolo:
        assert (not ns.i) and (ns.c is None), (ns.i, ns.c, ns.yolo, ns)

        if turtling_sketchist_find():
            turtling_run_as_chat_client("relaunch")
        else:
            turtling_run_as_sketchist()

        return

    # Take the I or C or both Options as Auth to run as the Chat Pane of a Drawing Pane

    assert ns.i or (ns.c is not None), (ns,)

    if not turtling_sketchist_find():
        workaround = "Try 'pwd' and 'cd' and 'ps aux |grep -i Turtl' and so on"
        workaround += ", like via:  python3 turtling.py --stop"
        print(f"No Terminal Window Pane found for drawing. {workaround}", file=sys.stderr)
        sys.exit(1)

    command = "relaunch" if (ns.c is None) else ns.c
    turtling_run_as_chat_client(command)

    eprint("Bye bye")


def parse_turtling_py_args_else() -> argparse.Namespace:
    """Take Words in from the Sh Command Line"""

    # Define the Arg Parser

    doc = __main__.__doc__
    assert doc, (doc,)

    parser = doc_to_parser(doc, add_help=True, startswith="how to run")

    version_help = "show version and exit"
    yolo_help = "draw inside this Pane, else chat inside this pane"
    stop_help = "send Signal·SigKill to every Turtling·Py Process, as if Sh 'kill -9'"
    i_help = "chat inside this pane"
    c_help = "do some things, before quitting if no -i, or before chatting if -i"

    parser.add_argument("--version", action="count", help=version_help)
    parser.add_argument("--yolo", action="count", help=yolo_help)
    parser.add_argument("--yolo1", action="count", help=argparse.SUPPRESS)
    parser.add_argument("--yolo2", action="count", help=argparse.SUPPRESS)
    parser.add_argument("--stop", action="count", help=stop_help)
    parser.add_argument("-i", action="count", help=i_help)
    parser.add_argument("-c", metavar="COMMAND", help=c_help)

    # Take in the Words, and react to undoc'ed Options

    ns = parse_args_else(parser)  # often prints help & exits

    if ns.yolo1:
        yolo1()
        sys.exit(0)

    if ns.yolo2:
        yolo2()
        sys.exit(0)

    # React to doc'ed Options

    if ns.version:
        print(f"BYO Turtling·Py {__version__}")
        sys.exit(0)

    if ns.stop and (ns.yolo or ns.i or (ns.c is not None)):
        print("error: don't choose --stop with --yolo or -i or -c", file=sys.stderr)
        sys.exit(2)  # exits 2 for wrong Sh Args

    if ns.yolo and (ns.i or (ns.c is not None)):
        print("error: don't choose --yolo with -i or -c", file=sys.stderr)
        sys.exit(2)  # exits 2 for wrong Sh Args

    if (not ns.yolo) and (not ns.i) and (ns.c is None):
        ns.yolo = 1  # replaces  # at ./turtling.py --

    # Succeed

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
# Sketch out the Byte Sequences to test early & often
#


# Keycap Symbols are ⎋ Esc, ⌃ Control, ⌥ Option/ Alt, ⇧ Shift, ⌘ Command/ Os

#     ⌃G ⌃H ⌃I ⌃J ⌃M mean \a \b \t \n \r, and ⌃[ means \e, also known as ⎋ Esc
#     Tab means ⌃I \t, and Return means ⌃M \r
#
# The famous Esc ⎋ Byte Pairs are ⎋ 7 8 C L ⇧D ⇧E ⇧M
#
#     ⎋7 cursor-checkpoint  ⎋8 cursor-revert (defaults to Y 1 X 1)
#     ⎋C screen-erase  ⎋L row-column-leap
#     ⎋⇧D ↓  ⎋⇧E \r\n else \r  ⎋⇧M ↑
#
# The famous Csi ⎋[ Sequences are ⎋[ ⇧@ ⇧A⇧B⇧C⇧D⇧E⇧G⇧H⇧I⇧J⇧K⇧L⇧M⇧P⇧S⇧T⇧Z and ⎋[ DHLMNQT
#
#     ⎋[⇧A ↑  ⎋[⇧B ↓  ⎋[⇧C →  ⎋[⇧D ←
#     ⎋[I ⌃I  ⎋[⇧Z ⇧Tab
#     ⎋[D row-leap  ⎋[⇧G column-leap  ⎋[⇧H row-column-leap
#
#     ⎋[⇧M rows-delete  ⎋[⇧L rows-insert  ⎋[⇧P chars-delete  ⎋[⇧@ chars-insert
#     ⎋[⇧J after-erase  ⎋[1⇧J before-erase  ⎋[2⇧J screen-erase  ⎋[3⇧J scrollback-erase
#     ⎋[⇧K row-tail-erase  ⎋[1⇧K row-head-erase  ⎋[2⇧K row-erase
#     ⎋[⇧T scrolls-down  ⎋[⇧S scrolls-up
#
#     ⎋[4H insert  ⎋[4L replace  ⎋[6 Q bar  ⎋[4 Q skid  ⎋[ Q unstyled
#
#     ⎋[1M bold  ⎋[4M underline  ⎋[7M reverse/inverse
#     ⎋[31M red  ⎋[32M green  ⎋[34M blue  ⎋[38;5;130M orange
#     ⎋[M plain
#
#     ⎋[5N call for reply ⎋[0N
#     ⎋[6N call for reply ⎋[{y};{x}⇧R  ⎋[18T call for reply ⎋[8;{rows};{columns}T
#
#     ⎋['⇧} cols-insert  ⎋['⇧~ cols-delete


#
#   macOS Keyboard encodes Fn⇧← as ⎋[⇧H row-column-go
#   macOS Mouse answers ⎋[?1006;1000h till ⎋[?1006;1000l with ⎋[<{b};{y};{x}M and ⎋[<{b};{y};{x}m
#
#   Our macOS App Emulation includes
#
#       ⌃A column-leap-leftmost
#       ⌃B ←
#       ⌃D char-delete-right  # FIXME: make it so
#       ⌃F →
#       ⌃G alarm-ring
#       ⌃H char-delete-left  # FIXME: make it so
#       ⌃K row-tail-erase  # FIXME: make it so
#       ⌃N ↓
#       ⌃O row-insert  # FIXME: make it so
#       ⌃P ↑
#       Delete char-delete-right  # FIXME: make it so
#
#   Our Emulation of default Vim/ Emacs includes
#
#       ⌃L scrollback-and-screen-erase  # FIXME: make it so
#           note: ⌘K ⌘K is already plenty destructive at macOS now
#
#       Also Turtle Press "⌘K ⌘K" works  # FIXME: make it so
#


#
# Name Control Bytes and Escape Sequences, like for working with Import Termios, Tty
#


Y_32100 = 32100  # larger than all Screen Row Heights tested
X_32100 = 32100  # larger than all Screen Column Widths tested


BS = "\b"  # 00/08 Backspace ⌃H
HT = "\t"  # 00/09 Character Tabulation ⌃I
LF = "\n"  # 00/10 Line Feed ⌃J  # akin to CSI CUD "\x1B" "[" "B"
CR = "\r"  # 00/13 Carriage Return ⌃M  # akin to CSI CHA "\x1B" "[" "G"

ESC = "\x1b"  # 01/11 Escape ⌃[  # also known as printf '\e'  # but Python doesn't define \e

DECSC = "\x1b" "7"  # ESC 03/07 Save Cursor [Checkpoint] (DECSC)
DECRC = "\x1b" "8"  # ESC 03/08 Restore Cursor [Revert] (DECRC)
SS3 = "\x1b" "O"  # ESC 04/15 Single Shift Three  # in macOS F1 F2 F3 F4

CSI = "\x1b" "["  # 05/11 Control Sequence Introducer
CSI_EXTRAS = "".join(chr(_) for _ in range(0x20, 0x40))  # !"#$%&'()*+,-./0123456789:;<=>?, no @
# Parameter, Intermediate, and Not-Final Bytes of a CSI Escape Sequence


CUU_Y = "\x1b" "[" "{}A"  # CSI 04/01 Cursor Up
CUD_Y = "\x1b" "[" "{}B"  # CSI 04/02 Cursor Down  # \n is Pn 1 except from last Row
CUF_X = "\x1b" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right
CUB_X = "\x1b" "[" "{}D"  # CSI 04/04 Cursor [Back] Left  # \b is Pn 1

CNL_Y = "\x1b" "[" "{}E"  # CSI 04/05 Cursor Next Line (CNL)  # \r\n but never implies ⎋[⇧S

CHA_X = "\x1b" "[" "{}G"  # CSI 04/07 Cursor Character Absolute  # \r is Pn 1
VPA_Y = "\x1b" "[" "{}d"  # CSI 06/04 Line Position Absolute

# CUP_1_1 = "\x1B" "[" "H"  # CSI 04/08 Cursor Position
# CUP_Y_1 = "\x1B" "[" "{}H"  # CSI 04/08 Cursor Position
# CUP_1_X = "\x1B" "[" ";{}H"  # CSI 04/08 Cursor Position
CUP_Y_X = "\x1b" "[" "{};{}H"  # CSI 04/08 Cursor Position

CHT_X = "\x1b" "[" "{}I"  # CSI 04/09 Cursor Forward [Horizontal] Tabulation  # \t is Pn 1
CBT_X = "\x1b" "[" "{}Z"  # CSI 05/10 Cursor Backward Tabulation


ED_P = "\x1b" "[" "{}J"  # CSI 04/10 Erase in Display  # 0 Tail # 1 Head # 2 Rows # 3 Scrollback

ICH_X = "\x1b" "[" "{}@"  # CSI 04/00 Insert Character
IL_Y = "\x1b" "[" "{}L"  # CSI 04/12 Insert Line [Row]
DL_Y = "\x1b" "[" "{}M"  # CSI 04/13 Delete Line [Row]
DCH_X = "\x1b" "[" "{}P"  # CSI 05/00 Delete Character

DECIC_X = "\x1b" "[" "{}'}}"  # CSI 02/07 07/13 DECIC_X  # "}}" to mean "}"
DECDC_X = "\x1b" "[" "{}'~"  # CSI 02/07 07/14 DECDC_X
# both with an Intermediate Byte of 02/07 ' Apostrophe [Tick]
# despite DECDC_X and DECIC_X absent from macOS Terminal

EL_P = "\x1b" "[" "{}K"  # CSI 04/11 Erase in Line  # 0 Tail # 1 Head # 2 Row

SU_Y = "\x1b" "[" "{}S"  # CSI 05/03 Scroll Up   # Insert Bottom Lines
SD_Y = "\x1b" "[" "{}T"  # CSI 05/04 Scroll Down  # Insert Top Lines

SM_IRM = "\x1b" "[" "4h"  # CSI 06/08 4 Set Mode Insert, not Replace
RM_IRM = "\x1b" "[" "4l"  # CSI 06/12 4 Reset Mode Replace, not Insert

# todo = "\x1B" "[" "1000h"  # CSI 06/08 4 Set Mode  # Mouse Reports
# todo = "\x1B" "[" "1005h"  # CSI 06/08 4 Set Mode  # UTF-8 vs VT200 Byte Encoding
# todo = "\x1B" "[" "1006h"  # CSI 06/08 4 Set Mode  # SGR
# todo = "\x1B" "[" "1015h"  # CSI 06/08 4 Set Mode  # URXVT

# todo = "\x1B" "[" "1000l"  # CSI 06/12 4 Reset Mode  # Mouse Reports
# todo = "\x1B" "[" "1005l"  # CSI 06/12 4 Reset Mode  # UTF-8 vs VT200 Byte Encoding
# todo = "\x1B" "[" "1006l"  # CSI 06/12 4 Reset Mode  # SGR
# todo = "\x1B" "[" "1015l"  # CSI 06/08 4 Set Mode  # URXVT

SGR = "\x1b" "[" "{}m"  # CSI 06/13 Select Graphic Rendition

DSR_0 = "\x1b" "[" "0n"  # CSI 06/14 [Request] Device Status Report  # Ps 0 because DSR_5
DSR_5 = "\x1b" "[" "5n"  # CSI 06/14 [Request] Device Status Report  # Ps 5 for DSR_0 In
DSR_6 = "\x1b" "[" "6n"  # CSI 06/14 [Request] Device Status Report  # Ps 6 for CPR In

DECSCUSR = "\x1b" "[" " q"  # CSI 02/00 07/01  # '' No-Style Cursor
DECSCUSR_SKID = "\x1b" "[" "4 q"  # CSI 02/00 07/01  # 4 Skid Cursor
DECSCUSR_BAR = "\x1b" "[" "6 q"  # CSI 02/00 07/01  # 6 Bar Cursor
# all three with an Intermediate Byte of 02/00 ' ' Space

XTWINOPS_8 = "\x1b" "[" "8t"  # CSI 07/04 [Response]   # Ps 8 In because XTWINOPS_18 Out
XTWINOPS_18 = "\x1b" "[" "18t"  # CSI 07/04 [Request]   # Ps 18 Out for XTWINOPS_8 In


# we've sorted the Str Literals above mostly by their CSI Final Byte's:  A, B, C, D, G, Z, m, etc

# to test in Sh, we run variations of:  printf '\e[18t' && read


# CSI 05/02 Active [Cursor] Position Report (CPR) In because DSR_6 Out
CPR_Y_X_REGEX = r"\x1B\[([0-9]+);([0-9]+)R"  # CSI 05/02 Active [Cursor] Pos Rep (CPR)


assert CSI_EXTRAS == "".join(chr(_) for _ in range(0x20, 0x40))  # r"[ -?]", no "@"
CSI_PIF_REGEX = r"(\x1B\[)" r"([0-?]*)" r"([ -/]*)" r"(.)"  # Parameter/ Intermediate/ Final Bytes


MACOS_TERMINAL_CSI_SIMPLE_FINAL_BYTES = "@ABCDEGHIJKLMPSTZdhlm"

#
# omits "R" of CPR_Y_X_REGEX In
# omits "n" of DSR_5 DSR_6 Out, so as to omit "n" of DSR_0 In
# omits "t" of XTWINOPS_18 Out, so as to omit "t" of XTWINOPS_8 In
# omits " q", "'}", "'~" of DECIC_X DECSCUSR and DECDC_X Out
#


#
# Terminal Interventions
#
#   macOS > Terminal > Settings > Profiles > Keyboard > Use Option as Meta Key
#       chooses whether ⌥9 comes through as itself ⌥9, or instead as ⎋9
#
#   bind 'set enable-bracketed-paste off' 2>/dev/null  # for Bash
#   unset zle_bracketed_paste  # for Zsh
#       accepts Line-Break's from Paste
#
#   tput clear && printf '\e[3J'  # clears Screen plus Terminal Scrollback Line Buffer
#
#   echo "POSTEDIT='$POSTEDIT'" |hexdump -C && echo "PS1='$PS1'"  # says if Zsh is bolding Input
#   echo "PS0='$PSO'" && echo "PS1='$PS1'" && trap  # says if Bash is bolding Input
#   ... |sed 's,\x1B\[m,,g'  # drops the Esc[m's that can come out of Bash ... done >...; cat ...|
#


#
# Terminal Docs
#
#   https://unicode.org/charts/PDF/U0000.pdf
#   https://unicode.org/charts/PDF/U0080.pdf
#   https://en.wikipedia.org/wiki/ANSI_escape_code
#
#   https://www.ecma-international.org/publications-and-standards/standards/ecma-48
#     /wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf
#
#   https://github.com/tmux/tmux/blob/master/tools/ansicode.txt  <= close to h/t jvns.ca
#   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
#   https://jvns.ca/blog/2025/03/07/escape-code-standards
#   https://man7.org/linux/man-pages/man4/console_codes.4.html  <= h/t jvns.ca
#   https://sw.kovidgoyal.net/kitty/keyboard-protocol  <= h/t jvns.ca
#   https://vt100.net/docs/vt100-ug/chapter3.html  <= h/t jvns.ca
#
#   https://iterm2.com/feature-reporting  <= h/t jvns.ca
#   https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda  <= h/t jvns.ca
#   https://github.com/Alhadis/OSC8-Adoption?tab=readme-ov-file  <= h/t jvns.ca
#
#   termios.TCSADRAIN doesn't drop Queued Input, but blocks till Queued Output gone
#   termios.TCSAFLUSH drops Queued Input, and blocks till Queued Output gone
#


# FIXME: Try AugmentCode Review of Class TerminalBytePacket

# FIXME: Limit rate of input so that hanging in Google Shell doesn't go so wild
# FIXME: Stop hanging in Google Shell at ⌃⌥↑ etc over ⎋⎋OA

# FIXME: Tweak up Python Logo Turtles to call TerminalBytePacket
# FIXME: like for quick ⎋[M DL_Y etc
# FIXME: like for no crash of ⎋ [ M ⎋[A


class TerminalBytePacket:
    """Hold 1 Control Character, else 1 or more Text Characters, else some Bytes"""

    assert ESC == "\x1b"  # ⎋
    assert CSI == "\x1b" "["  # ⎋[
    assert SS3 == "\x1b" "O"  # ⎋O

    text: str  # 0 or more Chars of Printable Text

    head: bytearray  # 1 Control Byte, else ⎋[, or ⎋O, or 3..6 Bytes starting with ⎋[M
    neck: bytearray  # CSI Parameter Bytes, in 0x30..0x3F
    back: bytearray  # CSI Intermediate Bytes, in 0x20..0x2F
    stash: bytearray  # 1..3 Bytes taken for now, in hope of decoding 2..4 Later
    tail: bytearray  # CSI Final Byte, in 0x40..0x7E

    closed: bool  # closed because completed, or because continuation undefined

    def __init__(self, bytes_=b"") -> None:

        self.text = ""

        self.head = bytearray()
        self.neck = bytearray()
        self.back = bytearray()
        self.stash = bytearray()
        self.tail = bytearray()

        self.closed = False

        laters = self.take_some_if(bytes_)
        if laters:
            raise ValueError(laters)

        self._limit_mutation_()

        # closes ControlSequence(bytes([0x80 | 0x0B]))  # doesn't open as b"\x1B\x5B" CSI ⎋[
        # closes ControlSequence(bytes([0x80 | 0x0F]))  # doesn't open as b"\x1B\x4F" SS3 ⎋O

        # raises ValueError: b'\x80' when asked for ControlSequence(b'\xC0\x80')

    def _limit_mutation_(self) -> None:
        """Raise Exception if a mutation has damaged Self"""

        text = self.text
        head = self.head
        neck = self.neck
        back = self.back
        stash = self.stash
        tail = self.tail
        closed = self.closed  # only via 'def close' if text or stash or not head

        if (not text) and (not head):
            assert (not tail) and (not closed), (tail, closed, stash, self)

        if text:
            assert not head, (head, text, self)
            assert (not neck) and (not back) and (not tail), (neck, back, tail, text, self)

        if head:
            assert not text, (text, head, self)
        if neck or back or tail:
            assert head, (head, neck, back, tail, self)
        if stash:
            assert not tail, (tail, closed, stash, self)
        if tail:
            assert closed, (closed, tail, self)

    def __bool__(self) -> bool:
        truthy = bool(self.text or self.head or self.neck or self.back or self.tail or self.stash)
        return truthy  # no matter if .closed

    def __repr__(self) -> str:

        cname = self.__class__.__name__

        text = self.text
        head_ = bytes(self.head)  # reps bytearray(b'') loosely, as b''
        neck_ = bytes(self.neck)
        back_ = bytes(self.back)
        stash_ = bytes(self.stash)
        tail_ = bytes(self.tail)
        closed = self.closed

        s = f"text={text!r}, "
        s += f"head={head_!r}, neck={neck_!r}, back={back_!r}, stash={stash_!r}, tail={tail_!r}"
        s = f"{cname}({s}, {closed=})"

        return s

        # "TerminalBytePacket(head=b'', back=b'', neck=b'', stash=b'', tail=b'', closed=False)"

    def __str__(self) -> str:

        text = self.text
        head_ = bytes(self.head)  # reps bytearray(b'') loosely, as b''
        neck_ = bytes(self.neck)
        back_ = bytes(self.back)
        stash_ = bytes(self.stash)
        tail_ = bytes(self.tail)

        if text:
            if stash_:
                return text + " " + str(stash_)
            return text

        if not head_:
            if stash_:
                return str(stash_)

        s = str(head_)
        if neck_:  # 'Parameter' Bytes
            s += " " + str(neck_)
        if back_ or stash_ or tail_:  # 'Intermediate' Bytes or Final Byte
            assert (not stash_) or (not tail_), (stash_, tail_)
            s += " " + str(back_ + stash_ + tail_)

        return s  # no matter if .closed

    def to_bytes(self) -> bytes:

        text = self.text
        head_ = bytes(self.head)  # reps bytearray(b'') loosely, as b''
        neck_ = bytes(self.neck)
        back_ = bytes(self.back)
        stash_ = bytes(self.stash)
        tail_ = bytes(self.tail)

        b = text.encode()
        b += head_ + neck_ + back_ + stash_ + tail_

        return b  # no matter if .closed

    def _try_bytes_lists_(self) -> None:  # todo: add Code to call this slow thorough Self-Test
        """Try some Str of Packets open to, or closed against, taking more Bytes"""

        # Try some Sequences left open to taking more Bytes

        tbp = TerminalBytePacket(b"Superb")
        assert str(tbp) == "Superb" and not tbp.closed, (tbp,)

        self._try_open_(b"")  # empty
        self._try_open_(b"\x1b")  # first Byte of Esc Sequence
        self._try_open_(b"\x1b\x1b")  # first Two Bytes of Esc-Esc Sequence
        self._try_open_(b"\x1bO")  # first Two Bytes of Three-Byte SS3 Sequence
        self._try_open_(b"\x1b[", b"6", b" ")  # CSI Head with Neck and Back but no Tail
        self._try_open_(b"\xed\x80")  # Head of >= 3 Byte UTF-8 Encoding
        self._try_open_(b"\xf4\x80\x80")  # Head of >= 4 Byte UTF-8 Encoding
        self._try_open_(b"\x1b[M#\xff")  # Undecodable Head, incomplete CSI Mouse Report
        self._try_open_(b"\x1b[M \xc4\x8a")  # Head only, 6 Byte incomplete CSI Mouse Report

        # Try some Sequences closed against taking more Bytes

        self._try_closed_(b"\n")  # Head only, of 7-bit Control Byte
        self._try_closed_(b"\x1b\x1b[", b"3;5", b"~")  # CSI Head with Neck and Tail, no Back
        self._try_closed_(b"\xc0")  # Head only, of 8-bit Control Byte
        self._try_closed_(b"\xff")  # Head only, of 8-bit Control Byte
        self._try_closed_(b"\xc2\xad")  # Head only, of 2 Byte UTF-8 of U+00AD Soft-Hyphen Control
        self._try_closed_(b"\x1b", b"A")  # Head & Text Tail of a Two-Byte Esc Sequence
        self._try_closed_(b"\x1b", b"\t")  # Head & Control Tail of a Two-Byte Esc Sequence
        self._try_closed_(b"\x1bO", b"P")  # Head & Text Tail of a Three-Byte SS3 Sequence
        self._try_closed_(b"\x1b[", b"3;5", b"H")  # CSI Head with Next and Tail
        self._try_closed_(b"\x1b[", b"6", b" q")  # CSI Head with Neck and Back & Tail

        # FIXME: test each Control Flow Return? test each Control Flow Branch?

    def _try_open_(self, *args) -> None:
        """Raise Exception unless the Eval of the Str of the Packet equals its Bytes"""

        tbp = self._try_bytes_(*args)
        assert not tbp.closed, (tbp,)

    def _try_closed_(self, *args) -> None:
        """Raise Exception unless the Eval of the Str of the Packet equals its Bytes"""

        tbp = self._try_bytes_(*args)
        assert tbp.closed, (tbp,)

    def _try_bytes_(self, *args) -> "TerminalBytePacket":
        """Raise Exception unless the Eval of the Str of the Packet equals its Bytes"""

        bytes_ = b"".join(args)
        join = " ".join(str(_) for _ in args)

        tbp = TerminalBytePacket(bytes_)
        tbp_to_bytes = tbp.to_bytes()
        tbp_to_str = str(tbp)

        assert tbp_to_bytes == bytes_, (tbp_to_bytes, bytes_)
        assert tbp_to_str == join, (bytes_, tbp_to_str, join)

        return tbp

    def close(self) -> None:
        """Close, if not closed already"""

        head = self.head
        stash = self.stash

        head_plus = head + stash  # if closing a 6-Byte Mouse-Report that decodes to < 6 Chars
        if head_plus.startswith(b"\x1b[M"):
            try:
                decode = head_plus.decode()
                if len(decode) < 6:
                    if len(head_plus) == 6:

                        head.extend(stash)
                        stash.clear()

            except UnicodeDecodeError:
                pass

        self.closed = True

        self._limit_mutation_()

    def take_some_if(self, bytes_) -> bytes:
        """Take in the Bytes and return 0, else return the trailing Bytes that don't fit"""

        for index in range(len(bytes_)):
            byte = bytes_[index:][:1]
            after_bytes = bytes_[index:][1:]

            laters = self.take_one_if(byte)
            if laters:
                return laters + after_bytes

        return b""  # maybe .closed, maybe not

    def take_one_if(self, byte) -> bytes:
        """Take in next 1 Byte and return 0 Bytes, else return 1..4 Bytes that don't fit"""

        laters = self._take_one_if_(byte)
        self._limit_mutation_()

        return laters

    def _take_one_if_(self, byte) -> bytes:
        """Take in next 1 Byte and return 0 Bytes, else return 1..4 Bytes that don't fit"""

        text = self.text
        head = self.head
        closed = self.closed

        # Decline Bytes after Closed

        if closed:
            return byte  # declines Byte after Closed

        # Take 1 Byte into Stash, if next Bytes could make it Decodable

        (decode_if, stash_laters) = self._take_one_stashable_if(byte)
        assert len(decode_if) <= 1, (decode_if, stash_laters, byte)
        if not stash_laters:
            return b""  # holds 1..3 possibly Decodable Bytes in Stash

        # Take 1 Byte into Mouse Report, if next Bytes could close as Mouse Report

        mouse_laters = self._take_some_mouse_if_(stash_laters)
        if not mouse_laters:
            return b""  # holds 1..5 Undecodable Bytes, or 1..11 Bytes as 1..5 Chars as Mouse Report

        assert mouse_laters == stash_laters, (mouse_laters, stash_laters)

        # Take 1 Char into Text

        if decode_if:
            printable = decode_if.isprintable()
            if printable and not head:
                self.text += decode_if
                return b""  # takes 1 Printable Char into Text, or as starts Text

        if text:
            return mouse_laters  # declines 1..4 Unprintable Bytes after Text

        # Take 1 Char into 1 Control Sequence

        control_laters = self._take_some_control_if_(decode_if, laters=mouse_laters)
        return control_laters

    def _take_one_stashable_if(self, byte) -> tuple[str, bytes]:
        """Take 1 Byte into Stash, if next Bytes could make it Decodable"""

        stash = self.stash
        stash_plus = stash + byte

        try:
            decode = stash_plus.decode()
            stash.clear()
        except UnicodeDecodeError:
            decodes = self.any_decodes_startswith(stash_plus)
            if decodes:
                stash.extend(byte)
                return ("", b"")  # holds 1..3 possibly Decodable Bytes in Stash

            stash.clear()
            return ("", stash_plus)  # declines 1..4 Undecodable Bytes

        assert not stash, (stash, byte)
        assert len(decode) == 1, (decode, stash, byte)

        return (decode, stash_plus)  # forwards 1..4 Decodable Bytes

    def any_decodes_startswith(self, bytes_) -> str:
        """Return Say if these Bytes start 1 or more UTF-8 Encodings of Chars"""

        suffixes = (b"\x80", b"\xbf", b"\x80\x80", b"\xbf\xbf", b"\x80\x80\x80", b"\xbf\xbf\xbf")

        for suffix in suffixes:
            suffixed = bytes_ + suffix
            try:
                decode = suffixed.decode()
                assert len(decode) >= 1, (decode,)
                return decode
            except UnicodeDecodeError:
                continue

        return ""

        # b"\xC2\x80", b"\xE0\xA0\x80", b"\xF0\x90\x80\x80" .. b"\xF4\x8F\xBF\xBF"
        # todo: invent UTF-8'ish Encoding beyond 1..4 Bytes for Unicode Codes < 0x110000

    def _take_some_mouse_if_(self, laters) -> bytes:
        """Take 1 Byte into Mouse Report, if next Bytes could close as Mouse Report"""

        assert laters, (laters,)

        head = self.head
        neck = self.neck
        back = self.back

        # Do take the 3rd Byte of this kind of CSI here, and don't take the first 2 Bytes here

        if (head == b"\x1b[") and (not neck) and (not back):
            if laters == b"M":
                head.extend(laters)
                return b""  # takes 3rd Byte of CSI Mouse Report here

        if not head.startswith(b"\x1b[M"):  # ⎋[M Mouse Report
            return laters  # doesn't take the first 2 Bytes of Mouse Report here

        # Take 3..15 Bytes into a 3..6 Char Mouse Report

        head_plus = head + laters
        try:
            head_plus_decode_if = head_plus.decode()
        except UnicodeDecodeError:
            head_plus_decode_if = ""

        if head_plus_decode_if:
            assert len(head_plus_decode_if) <= 6, (head_plus_decode_if, laters)
            head.extend(laters)
            if len(head_plus_decode_if) == 6:
                self.closed = True
            return b""  # takes 3..15 Bytes into a 6 Char Mouse Report

        # Take 4..15 Bytes into a 6 Byte Mouse Report

        if len(head_plus) > 6:  # 6..15 Bytes
            return laters  # declines 2..4 Bytes into 5 of 6 Chars or into 5 of 6 Bytes

        head.extend(laters)
        if len(head_plus) == 6:
            self.closed = True
        return b""  # takes 4..14 Bytes into a 6 Byte Mouse Report

    def _take_some_control_if_(self, decode_if, laters) -> bytes:
        """Take 1 Char into Control Sequence, else return 1..4 Bytes that don't fit"""

        assert laters, (laters,)

        head = self.head
        tail = self.tail
        closed = self.closed

        assert not tail, (tail,)
        assert not closed, (closed,)

        # Look only outside of Mouse Reports

        assert not head.startswith(b"\x1b[M"), (head,)  # Mouse Report

        # Look only at Undecodable, Unprintable, or Escaped Bytes

        printable = False
        assert len(decode_if) <= 1, (decode_if, laters)
        if decode_if:
            assert len(decode_if) == 1, (decode_if, laters)
            printable = decode_if.isprintable()
            assert head or not printable, (decode_if, laters, head, printable)

        # Take first 1 or 2 or 3 Bytes into Esc Sequences
        # ⎋ Esc  # ⎋⎋ Esc Esc  # ⎋⎋O Esc SS3  # ⎋O SS3
        # ⎋ CSI  # ⎋ Esc CSI

        head_plus = head + laters
        if head_plus in (b"\x1b", b"\x1b\x1b", b"\x1b\x1bO", b"\x1b\x1b[", b"\x1bO", b"\x1b["):
            head.extend(laters)
            return b""  # takes first 1 or 2 Bytes into Esc Sequences

        # Take & close 1 Unprintable Char or 1..4 Undecodable Bytes, as Head

        if not head:
            if not printable:
                head.extend(laters)
                self.closed = True
                return b""  # takes & closes Unprintable Chars or 1..4 Undecodable Bytes

            # takes \b \t \n \r \x7F etc

        # Take & close 1 Escaped Printable Decoded Char, as Tail
        # ⎋ Esc  # ⎋⎋ Esc Esc  # ⎋⎋O Esc SS3  # ⎋O SS3

        if head in (b"\x1b", b"\x1b\x1b", b"\x1b\x1bO", b"\x1bO"):
            if printable:
                tail.extend(laters)
                self.closed = True
                return b""  # takes & closes 1 Escaped Printable Decoded Char

            # Take & close Unprintable Chars or 1..4 Undecodable Bytes, as Escaped Tail

            tail.extend(laters)  # todo: test of Unprintable/ Undecodable after ⎋O SS3
            self.closed = True
            return b""  # takes & closes Unprintable Chars or 1..4 Undecodable Bytes

            # does take ⎋\x10 ⎋\b ⎋\t ⎋\n ⎋\r ⎋\x7F etc

            # doesn't take bytes([0x80 | 0x0B]) as meaning b"\x1B\x5B" CSI ⎋[
            # doesn't take bytes([0x80 | 0x0F]) as meaning b"\x1B\x4F" SS3 ⎋O

        # Decline 1..4 Undecodable Bytes, when escaped by CSI or Esc CSI

        if not decode_if:
            return laters  # declines 1..4 Undecodable Bytes

        decode = decode_if
        assert len(decode_if) == 1, (decode_if, laters)
        assert laters == decode.encode(), (laters, decode_if)

        # Take or don't take 1 Printable Char into CSI or Esc CSI Sequence

        esc_csi_laters = self._esc_csi_take_one_if_(decode)
        return esc_csi_laters  # maybe empty

    def _esc_csi_take_one_if_(self, decode) -> bytes:
        """Take 1 Char into CSI or Esc CSI Sequence, else return 1..4 Bytes that don't fit"""

        assert len(decode) == 1, decode
        ord_ = ord(decode)
        encode = decode.encode()

        head = self.head
        back = self.back
        neck = self.neck
        tail = self.tail
        closed = self.closed

        # Look only at unclosed CSI or Esc CSI Sequence

        assert CSI == "\x1b" "[", (CSI,)  # ⎋[
        if not head.startswith(b"\x1b\x1b["):  # ⎋⎋[ Esc CSI
            assert head.startswith(b"\x1b["), (head,)  # ⎋[ CSI

        assert not tail, (tail,)
        assert not closed, (closed,)

        # Decline 1..4 Bytes of Unprintable or Multi-Byte Char

        if ord_ > 0x7F:
            return encode  # declines 2..4 Bytes of 1 Unprintable or Multi-Byte Char

        # Accept 1 Byte into Back, into Neck, or as Tail

        byte = chr(ord_).encode()
        assert byte == encode, (byte, encode)

        if not back:
            if 0x30 <= ord_ < 0x40:  # 16 Codes
                neck.extend(byte)
                return b""  # takes 1 of 16 Parameter Byte Codes

        if 0x20 <= ord_ < 0x30:  # 16 Codes
            back.extend(byte)
            return b""  # takes 1 of 16 Intermediate Byte Codes

        if 0x40 <= ord_ < 0x7F:  # 63 Codes
            tail.extend(byte)
            self.closed = True
            return b""  # takes 1 of 63 Final Byte Codes

        # Decline 1 Byte of Unprintable Char

        return byte  # declines 1 Byte <= b"\x7F" of Unprintable Char

        # splits '⎋[200~' and '⎋[201~' away from enclosed Bracketed Paste

        # todo: limit the length of a CSI Escape Sequence

    # todo: limit rate of input so livelocks go less wild, like in Keyboard/ Screen loopback


#
# Amp up Import TermIOs, Tty
#


def yolo2() -> None:
    """Loop Keyboard back to Screen"""

    assert DL_Y == "\x1b" "[" "{}M"  # CSI 04/13 Delete Line [Row]

    with BytesTerminal() as bt:
        print("Loop Keyboard back to Screen", end="\r\n")
        print(r"To quit, press ⌃\ or close this Terminal Window Pane", end="\r\n")

        while True:
            (tbp, laters) = yolo_read_tbp_laters(bt, t=None)
            bytes_ = tbp.to_bytes() + laters

            fd = bt.fileno
            data = bytes_
            os.write(fd, data)

            if bytes_ == b"\x1c":  # ⌃\
                return


def yolo1() -> None:
    """Trace Keyboard"""

    assert DL_Y == "\x1b" "[" "{}M"  # CSI 04/13 Delete Line [Row]

    with BytesTerminal() as bt:
        print("Tracing Keyboard ...", end="\r\n")
        print(r"To quit, press ⌃\ or close this Terminal Window Pane", end="\r\n")

        while True:
            print(end="\r\n")

            t = dt.datetime.now().astimezone()
            while True:
                (tbp, laters) = yolo_read_tbp_laters(bt, t=t)
                if laters:
                    print(laters, end="\r\n")

                bytes_ = tbp.to_bytes() + laters
                if bytes_ == b"\x1c":  # ⌃\
                    return

                if bt.kbhit(timeout=0):  # sometimes catches Release or Press after Press
                    print("kbhit", end="\r\n")
                    continue

                break

                # todo: macOS Control+Click sends Press, Delay, Press, Delay, Release


def yolo_read_tbp_laters(bt, t) -> tuple[TerminalBytePacket, bytes]:
    """Take Bytes while they arrive instantly, or as needed to closed a Packet"""

    stamp = t

    # Take the Bytes that come together, and trace all but the last slow Byte here

    tbp = TerminalBytePacket()
    while True:
        kbyte = bt.kbyte_read()
        laters = tbp.take_one_if(kbyte)

        if tbp.text and laters:  # drops any Text without ever returning it
            assert tbp.text.isprintable(), (tbp.text, laters)
            if t:
                print(repr(tbp.text), end="\r\n")
                print(end="\r\n")

            tbp = TerminalBytePacket()
            laters = tbp.take_some_if(laters)

        if tbp.closed or laters:
            break

        if bt.kbhit(timeout=0.000):
            continue

        if not t:  # takes single Text Characters quickly, while Yolo2
            if tbp.text:
                tbp.close()
                break

        if tbp.head == b"\x1b[M":  # takes ⎋[M DL_Y quickly, when not ⎋[M... Mouse Report
            tbp.close()
            break

        if t:
            print(stamp, tbp.to_bytes(), tbp, repr(tbp), 1, end="\r\n")

        if not bt.kbhit(timeout=1.000):
            if tbp.text:
                continue

            return (tbp, laters)

        stamp = dt.datetime.now().astimezone()

    # Also take the extra Bytes that come immediately

    while (not tbp.closed) and bt.kbhit(timeout=0.000):
        kbyte = bt.kbyte_read()
        if not laters:
            laters = tbp.take_one_if(kbyte)
        else:
            laters += kbyte

    if t:
        print(stamp, tbp.to_bytes(), tbp, repr(tbp), 2, end="\r\n")

    return (tbp, laters)

    # todo: return two Packets when the Laters are a new Packet


class BytesTerminal:
    """Write/ Read Bytes at Screen/ Keyboard of the Terminal"""

    stdio: typing.TextIO  # sys.stderr
    fileno: int  # 2

    before: int  # termios.TCSADRAIN  # termios.TCSAFLUSH  # written at Entry
    tcgetattr_else: list[int | list[bytes | int]] | None  # sampled at Entry
    after: int  # termios.TCSADRAIN  # termios.TCSAFLUSH  # written at Exit

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
                tty.setraw(fileno, when=before)  # Tty SetRaw defaults to TcsaFlush

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
            termios.tcsetattr(fileno, when, tcgetattr)  # .tcsetattr(fd, when, attributes)

        return None

    def sbytes_flush(self) -> None:
        """Flush Screen Output, like just before blocking to read Keyboard Input"""

        stdio = self.stdio
        stdio.flush()

    def ksbytes_stop(self) -> None:  # todo: learn to do .ksbytes_stop() well
        """Suspend and resume this Screen/ Keyboard Terminal Process"""

        pid = os.getpid()

        self.__exit__()

        eprint("Turtling·Py Terminal Stop: ⌃Z F G Return")
        eprint("macOS ⌃C might stop working till you close Window")  # even past:  reset
        eprint("Linux might freak lots more than that")

        os.kill(pid, signal.SIGTSTP)  # a la 'sh kill $pid -STOP' before 'sh kill $pid -CONT'

        self.__enter__()

        assert os.getpid() == pid, (os.getpid(), pid)

        # a la Emacs ⌃Z suspend-frame, Vim ⌃Z

    #
    # Write Screen Output Bytes
    #

    def sbytes_write(self, sbytes) -> None:
        """Write Bytes to the Screen, but without also writing a Line-End afterwards"""

        assert self.tcgetattr_else, (self.tcgetattr_else,)

        fileno = self.fileno
        sbytes_list = self.sbytes_list

        sbytes_list.append(sbytes)
        os.write(fileno, sbytes)

        # doesn't raise UnicodeEncodeError

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
        """Read the 1 or more Bytes of 1 Key Chord, but let it stop short"""

        tbp = TerminalBytePacket()
        while True:
            kbyte = self.kbyte_read()
            laters = tbp.take_one_if(kbyte)
            if tbp.text or tbp.closed or laters:
                break
            if not self.kbhit(timeout=timeout):
                break

        bytes_ = tbp.to_bytes() + laters
        return bytes_

        # often returns the Bytes of a complete Key Chord
        # asks to take one too many Bytes when given an incomplete TerminalBytePacket
        # doesn't raise UnicodeDecodeError

        # todo: tight coupling across StrTerminal.schars_split & BytesTerminal.kbytes_read

    def kbyte_read(self) -> bytes:
        """Read 1 Keyboard Byte"""

        fileno = self.fileno
        assert self.tcgetattr_else, (self.tcgetattr_else,)

        self.sbytes_flush()  # for 'kbyte_read'
        kbyte = os.read(fileno, 1)  # 1 or more Bytes

        return kbyte

        # ⌃C comes through as b"\x03" and doesn't raise KeyboardInterrupt
        # ⌥Y often comes through as \ U+005C Reverse-Solidus aka Backslash  # not ¥ Yen-Sign

    def kbhit(self, timeout) -> bool:
        """Block till next Input Byte, else till Timeout, else till forever"""

        fileno = self.fileno
        assert self.tcgetattr_else, self.tcgetattr_else  # todo: kbhit can say readline won't block

        self.sbytes_flush()  # for 'kbhit'  # todo: log how often unneeded

        (r, w, x) = select.select([fileno], [], [], timeout)
        hit = fileno in r

        return hit

        # 'timeout' is 0 for Now, None for Never, else count of Seconds


# Name the Shifting Keys

Meta = unicodedata.lookup("Broken Circle With Northwest Arrow")  # ⎋
Control = unicodedata.lookup("Up Arrowhead")  # ⌃
Option = unicodedata.lookup("Option Key")  # ⌥
Shift = unicodedata.lookup("Upwards White Arrow")  # ⇧
Command = unicodedata.lookup("Place of Interest Sign")  # ⌘  # Super  # Windows
# 'Fn'

# note: Meta hides inside macOS Terminal > Settings > Keyboard > Use Option as Meta Key


# Define ⌃Q ⌃V and ⌃V ⌃Q
# to strongly abbreviate a few of the KCAP_BY_KCHARS Values

KCAP_QUOTE_BY_STR = {
    "Delete": unicodedata.lookup("Erase To The Left"),  # ⌫
    "Return": unicodedata.lookup("Return Symbol"),  # ⏎
    "Spacebar": unicodedata.lookup("Bottom Square Bracket"),  # ⎵  # not ␣ Open-Box
    "Tab": unicodedata.lookup("Rightwards Arrow To Bar"),  # ⇥
    "⇧Tab": unicodedata.lookup("Leftwards Arrow To Bar"),  # ⇤
}


# Encode each Key Chord as a Str without a " " Space in it

KCAP_SEP = " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc

KCAP_BY_KCHARS = {
    "\x00": "⌃Spacebar",  # ⌃@  # ⌃⇧2
    "\x09": "Tab",  # '\t' ⇥
    "\x0d": "Return",  # '\r' ⏎
    "\x1b": "⎋",  # Esc  # Meta  # includes ⎋Spacebar ⎋Tab ⎋Return ⎋Delete without ⌥
    "\x1b" "\x01": "⌥⇧Fn←",  # ⎋⇧Fn←   # coded with ⌃A
    "\x1b" "\x03": "⎋FnReturn",  # coded with ⌃C  # not ⌥FnReturn
    "\x1b" "\x04": "⌥⇧Fn→",  # ⎋⇧Fn→   # coded with ⌃D
    "\x1b" "\x08": "⎋⌃Delete",  # ⎋⌃Delete  # coded with ⌃H  # aka \b
    "\x1b" "\x0b": "⌥⇧Fn↑",  # ⎋⇧Fn↑   # coded with ⌃K
    "\x1b" "\x0c": "⌥⇧Fn↓",  # ⎋⇧Fn↓  # coded with ⌃L  # aka \f
    "\x1b" "\x10": "⎋⇧Fn",  # ⎋ Meta ⇧ Shift of Fn F1..F12  # not ⌥⇧Fn  # coded with ⌃P
    "\x1b" "\x1b": "⎋⎋",  # Meta Esc  # not ⌥⎋
    "\x1b" "\x1b" "OA": "⌃⌥↑",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧A  # gCloud Shell
    "\x1b" "\x1b" "OB": "⌃⌥↓",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧B  # gCloud Shell
    "\x1b" "\x1b" "OC": "⌃⌥→",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧C  # gCloud Shell
    "\x1b" "\x1b" "OD": "⌃⌥←",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧D  # gCloud Shell
    "\x1b" "\x1b" "[" "3;5~": "⎋⌃FnDelete",  # ⌥⌃FnDelete  # LS1R
    "\x1b" "\x1b" "[" "A": "⎋↑",  # CSI 04/01 Cursor Up (CUU)  # not ⌥↑
    "\x1b" "\x1b" "[" "B": "⎋↓",  # CSI 04/02 Cursor Down (CUD)  # not ⌥↓
    "\x1b" "\x1b" "[" "Z": "⎋⇧Tab",  # ⇤  # CSI 05/10 CBT  # not ⌥⇧Tab
    "\x1b" "\x28": "⎋FnDelete",  # not ⌥FnDelete
    "\x1b" "OP": "F1",  # ESC 04/15 Single-Shift Three (SS3)  # SS3 ⇧P
    "\x1b" "OQ": "F2",  # SS3 ⇧Q
    "\x1b" "OR": "F3",  # SS3 ⇧R
    "\x1b" "OS": "F4",  # SS3 ⇧S
    "\x1b" "[" "15~": "F5",  # CSI 07/14 Locking-Shift One Right (LS1R)
    "\x1b" "[" "17~": "F6",  # ⌥F1  # ⎋F1  # LS1R
    "\x1b" "[" "18~": "F7",  # ⌥F2  # ⎋F2  # LS1R
    "\x1b" "[" "19~": "F8",  # ⌥F3  # ⎋F3  # LS1R
    "\x1b" "[" "1;2C": "⇧→",  # CSI 04/03 Cursor [Forward] Right (CUF_YX) Y=1 X=2
    "\x1b" "[" "1;2D": "⇧←",  # CSI 04/04 Cursor [Back] Left (CUB_YX) Y=1 X=2
    "\x1b" "[" "20~": "F9",  # ⌥F4  # ⎋F4  # LS1R
    "\x1b" "[" "21~": "F10",  # ⌥F5  # ⎋F5  # LS1R
    "\x1b" "[" "23~": "F11",  # ⌥F6  # ⎋F6  # LS1R  # macOS takes F11
    "\x1b" "[" "24~": "F12",  # ⌥F7  # ⎋F7  # LS1R
    "\x1b" "[" "25~": "⇧F5",  # ⌥F8  # ⎋F8  # LS1R
    "\x1b" "[" "26~": "⇧F6",  # ⌥F9  # ⎋F9  # LS1R
    "\x1b" "[" "28~": "⇧F7",  # ⌥F10  # ⎋F10  # LS1R
    "\x1b" "[" "29~": "⇧F8",  # ⌥F11  # ⎋F11  # LS1R
    "\x1b" "[" "31~": "⇧F9",  # ⌥F12  # ⎋F12  # LS1R
    "\x1b" "[" "32~": "⇧F10",  # LS1R
    "\x1b" "[" "33~": "⇧F11",  # LS1R
    "\x1b" "[" "34~": "⇧F12",  # LS1R
    "\x1b" "[" "3;2~": "⇧FnDelete",  # LS1R
    "\x1b" "[" "3;5~": "⌃FnDelete",  # LS1R
    "\x1b" "[" "3~": "FnDelete",  # LS1R
    "\x1b" "[" "5~": "⇧Fn↑",
    "\x1b" "[" "6~": "⇧Fn↓",
    "\x1b" "[" "A": "↑",  # CSI 04/01 Cursor Up (CUU)
    "\x1b" "[" "B": "↓",  # CSI 04/02 Cursor Down (CUD)
    "\x1b" "[" "C": "→",  # CSI 04/03 Cursor Right [Forward] (CUF)
    "\x1b" "[" "D": "←",  # CSI 04/04 Cursor [Back] Left (CUB)
    "\x1b" "[" "F": "⇧Fn→",  # CSI 04/06 Cursor Preceding Line (CPL)
    "\x1b" "[" "H": "⇧Fn←",  # CSI 04/08 Cursor Position (CUP)
    "\x1b" "[" "Z": "⇧Tab",  # ⇤  # CSI 05/10 Cursor Backward Tabulation (CBT)
    "\x1b" "b": "⌥←",  # ⎋B  # ⎋←  # Emacs M-b Backword-Word
    "\x1b" "f": "⌥→",  # ⎋F  # ⎋→  # Emacs M-f Forward-Word
    "\x20": "Spacebar",  # ' ' ␠ ␣ ␢
    "\x7f": "Delete",  # ␡ ⌫ ⌦
    "\xa0": "⌥Spacebar",  # '\N{No-Break Space}'
}

assert list(KCAP_BY_KCHARS.keys()) == sorted(KCAP_BY_KCHARS.keys())

assert KCAP_SEP == " "
for _KCAP in KCAP_BY_KCHARS.values():
    assert " " not in _KCAP, (_KCAP,)

# the ⌥⇧Fn Key Cap quotes only the Shifting Keys, dropping the substantive final Key Cap,
# except that four Shifted Arrows exist at ⎋⇧Fn← ⎋⇧Fn→ ⎋⇧Fn↑ ⎋⇧Fn↓


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
    €ÅıÇÎ Ï˝Ó Ô\uf8ffÒÂ Ø∏Œ‰Íˇ ◊„˛Á¸“«‘ﬂ—
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

    y_count: int  # -1, then Count of Screen Rows
    x_count: int  # -1, then Count of Screen Columns

    row_y: int  # -1, then Row of Cursor
    column_x: int  # -1, then Column of Cursor

    revert_y: int  # -1, then Row of Cursor at ⎋7 DECSC Save-Cursor
    revert_x: int  # -1, then Column of Cursor at ⎋7 DECSC Save-Cursor

    writelog: dict[int, dict[int, str]]  # todo: row major or column major?  # ScreenLogger

    #
    # Init, Enter, and Exit
    #

    def __init__(self) -> None:

        bt = BytesTerminal()

        self.bytes_terminal = bt
        self.kchords = list()

        self.y_count = -1
        self.x_count = -1
        self.row_y = -1
        self.column_x = -1
        self.revert_y = -1
        self.revert_x = -1

        self.writelog = dict()

    def __enter__(self) -> "StrTerminal":  # -> typing.Self:

        bt = self.bytes_terminal
        bt.__enter__()

        return self

    def __exit__(self, *exc_info) -> None:

        bt = self.bytes_terminal
        kchords = self.kchords

        ctext = "\x1b[m"  # 1m Sgr Plain
        ctext += "\x1b[?25h"  # 06/08 Set Mode (SMS) 25 VT220 DECTCEM
        self.schars_write(ctext)  # todo: restore only after disturbing

        if kchords:
            self.schars_print()
            while kchords:
                (kbytes, kstr) = kchords.pop(0)
                self.schars_print(kstr)

        bt.__exit__()

    #
    # Read Key Chords from Keyboard or Screen
    #

    def kcaps_append(self, kcaps) -> None:  # todo: not much tested
        """Add imagined Key Caps to the real Key Caps"""

        kchords = self.kchords

        for kcap in kcaps:
            kchord = (b"", kcap)
            kchords.append(kchord)

        # todo: tight coupling across Turtle Press & StrTerminal KCaps_Append

    def kchord_pull(self, timeout) -> tuple[bytes, str]:
        """Read 1 Key Chord, and snoop the Cursor Position out of it, if present"""

        bt = self.bytes_terminal
        kchords = self.kchords

        if kchords:
            kchord = kchords.pop(0)
            return kchord

            # todo: log how rarely KChords wait inside a StrTerminal

        kbytes = bt.kbytes_pull(timeout=timeout)  # may contain b' ' near to KCAP_SEP
        assert kbytes, (kbytes,)

        [kchars, kcaps] = self.kbytes_to_kchars_kcaps(kbytes)  # may raise UnicodeDecodeError
        kchord = (kbytes, kcaps)

        self.kchars_snoop_kcpr_if(kchars)

        return kchord

        # .kbytes empty inside the .kchord when .kchord from .kcaps_append

    def kchars_snoop_kcpr_if(self, kchars) -> bool:
        """Snoop the Cursor Position out of a Key Chord, if present"""

        assert CPR_Y_X_REGEX == r"\x1B\[([0-9]+);([0-9]+)R"  # CSI 05/02 CPR

        # Never mind, if no Keyboard Cursor-Position-Report (K CPR) present

        m = re.fullmatch(r"\x1B\[([0-9]+);([0-9]+)R", string=kchars)
        if not m:
            return False

        # Interpret the K CPR

        row_y = int(m.group(1))
        column_x = int(m.group(2))

        assert row_y >= 1, (row_y,)
        assert column_x >= 1, (column_x,)

        self.row_y = row_y
        self.column_x = column_x

        return True

    def kbytes_to_kchars_kcaps(self, kbytes) -> tuple[str, str]:
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

            # ⌥Y often comes through as \ U+005C Reverse-Solidus aka Backslash  # not ¥ Yen-Sign

        # Succeed

        assert KCAP_SEP == " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc
        assert " " not in kcaps, (kcaps,)

        return (kchars, kcaps)

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
            s = kcap_by_kchars[ch]  # '⌃Spacebar', 'Return', 'Delete', etc

        elif ch in option_kstr_by_1_kchar.keys():  # Mac US Option Accents
            s = option_kstr_by_1_kchar[ch]

        elif ch in option_kchars_spaceless:  # Mac US Option Key Caps
            s = self.spaceless_ch_to_option_kstr(ch)

        # Show the Key Caps of US-Ascii, plus the ⌃ ⇧ Control/ Shift Key Caps

        elif (o < 0x20) or (o == 0x7F):  # C0 Control Bytes, or \x7F Delete (DEL)
            s = "⌃" + chr(o ^ 0x40)  # '^ 0x40' speaks of ⌃ with one of @ A..Z [\]^_ ?

            # '^ 0x40' speaks of ⌃@ but not ⌃⇧@ and not ⌃⇧2 and not ⌃Spacebar at b"\x00"
            # '^ 0x40' speaks of ⌃M but not Return at b"\x0D"
            # '^ 0x40' speaks of ⌃[ ⌃\ ⌃] ⌃_ but not ⎋ and not ⌃⇧_ and not ⌃⇧{ ⌃⇧| ⌃⇧} ⌃-
            # '^ 0x40' speaks of ⌃? but not Delete at b"\x7F"

            # ^` ^2 ^6 ^⇧~ don't work

            # todo: can we more quickly decide that ⌃[ is only ⎋ by itself not continued?
            # todo: should we push ⌃- above ⌃⇧_

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

        assert DSR_6 == "\x1b" "[" "6n"  # CSI 06/14 DSR  # Ps 6 for CPR

        # Settle for a stale Sample,
        # else call for a fresh Sample and block till it comes

        if bt.sbytes_list[-1:] != [DSR_6.encode()]:  # todo: looser bt/st coupling

            self.schars_write("\x1b" "[" "6n")

            while True:
                kbytes = bt.kbytes_pull(timeout=timeout)  # may contain b' ' near to KCAP_SEP
                [kchars, kcaps] = self.kbytes_to_kchars_kcaps(kbytes)  # may raise UnicodeDecodeError
                kchord = (kbytes, kcaps)

                if self.kchars_snoop_kcpr_if(kchars):
                    break

                kchords.append(kchord)

                # todo: log how rarely KChords wait inside a StrTerminal

        # Pass back the fresh Sample

        row_y = self.row_y
        column_x = self.column_x

        assert row_y >= 1, (row_y,)  # rows counted down from Row 1 at Top
        assert column_x >= 1, (column_x,)  # columns counted up from Column 1 at Left

        return (row_y, column_x)

    def y_count_x_count_read(self, timeout) -> tuple[int, int]:
        """Sample Counts of Screen Rows and Columns"""

        bt = self.bytes_terminal

        fileno = bt.fileno
        (columns, lines) = os.get_terminal_size(fileno)
        (x_count, y_count) = (columns, lines)

        assert y_count >= 5, (y_count,)  # macOS Terminal min 5 Rows
        assert x_count >= 20, (x_count,)  # macOS Terminal min 20 Columns

        self.y_count = y_count
        self.x_count = x_count

        return (y_count, x_count)

        # .timeout unneeded where os.get_terminal_size available

    #
    # Say if writing these Screen Chars as Bytes would show their meaning clearly
    #

    def schars_to_writable(self, schars) -> bool:
        """Say if writing these Screen Chars as Bytes would show their meaning clearly"""

        assert CSI_PIF_REGEX == r"(\x1B\[)" r"([0-?]*)" r"([ -/]*)" r"(.)"  # 4 Kinds of Bytes

        assert DECIC_X == "\x1b" "[" "{}'}}"  # CSI 02/07 07/13 DECIC_X  # "}}" to mean "}"
        assert DECDC_X == "\x1b" "[" "{}'~"  # CSI 02/07 07/14 DECDC_X

        assert DECSCUSR == "\x1b" "[" " q"  # CSI 02/00 07/01  # '' No-Style Cursor
        assert DECSCUSR_SKID == "\x1b" "[" "4 q"  # CSI 02/00 07/01  # 4 Skid Cursor
        assert DECSCUSR_BAR == "\x1b" "[" "6 q"  # CSI 02/00 07/01  # 6 Bar Cursor

        assert DSR_5 == "\x1b" "[" "5n"  # CSI 06/14 [Request] Device Status Report  # Ps 5 for DSR_0
        assert DSR_6 == "\x1b" "[" "6n"  # CSI 06/14 [Request] Device Status Report  # Ps 6 for CPR
        assert XTWINOPS_18 == "\x1b" "[" "18t"  # CSI 07/04 [Request]   # Ps 18 for XTWINOPS_8

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

        # Accept the ⎋7 cursor-checkpoint, and ⎋8 cursor-revert

        if schars in ("\x1b" "7", "\x1b" "8"):
            return True

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

        assert DCH_X == "\x1b" "[" "{}P"  # CSI 05/00 Delete Character
        assert VPA_Y == "\x1b" "[" "{}d"  # CSI 06/04 Line Position Absolute

        (y_count, x_count) = self.y_count_x_count_read(timeout=0)
        (row_y, column_x) = self.row_y_column_x_read(timeout=0)

        for y in range(1, y_count + 1):
            ctext = "\x1b" "[" f"{y}d"
            ctext += "\x1b" "[" f"{n}P"
            self.schars_write(ctext)  # for .columns_delete_n

        ctext = "\x1b" "[" f"{row_y}d"
        self.schars_write(ctext)  # for .columns_delete_n

    def columns_insert_n(self, n) -> None:  # a la VT420 DECIC ⎋['}
        """Insert N Columns (but snap the Cursor back to where it started)"""

        assert ICH_X == "\x1b" "[" "{}@"  # CSI 04/00 Insert Character
        assert VPA_Y == "\x1b" "[" "{}d"  # CSI 06/04 Line Position Absolute

        (y_count, x_count) = self.y_count_x_count_read(timeout=0)
        (row_y, column_x) = self.row_y_column_x_read(timeout=0)

        for y in range(1, y_count + 1):
            ctext = "\x1b" "[" f"{y}d"
            ctext += "\x1b" "[" f"{n}@"
            self.schars_write(ctext)  # for .columns_insert_n

        ctext = "\x1b" "[" f"{row_y}d"
        self.schars_write(ctext)  # for .columns_insert_n

    #
    # Print or Write Str's of Chars
    #

    def write_row_y_column_x(self, row_y, column_x) -> None:
        """Write Cursor Row & Column"""

        assert row_y >= 1, (row_y,)  # rows counted down from Row 1 at Top
        assert column_x >= 1, (column_x,)  # columns counted up from Column 1 at Left

        assert CUP_Y_X == "\x1b" "[" "{};{}H"  # CSI 04/08 Cursor Position (CUP)

        self.schars_write("\x1b" "[" f"{row_y};{column_x}H")

        self.row_y = row_y
        self.column_x = column_x

        # todo: .write_row_y_column_x when out of bounds
        # todo: .write_row_y_column_x when no change to Y and/or to X

    def schars_print(self, *args, end="\n") -> None:
        """Write Chars to the Screen as one or more Ended Lines"""

        sep = " "
        join = sep.join(str(_) for _ in args)
        ended = join + end

        schars = ended.replace("\n", "\r\n")
        self.schars_write(schars)  # for .schars_print

    def schars_write(self, schars) -> None:
        """Write Chars to the Screen, but without implicitly also writing a Line-End afterwards"""

        bt = self.bytes_terminal
        writelog = self.writelog

        assert ED_P == "\x1b" "[" "{}J"  # CSI 04/10 Erase in Display  # 2 Rows, etc

        for split in self.schars_split(schars):
            sbytes = split.encode()

            if split == "\x1b" "[2J":
                bt.sbytes_write(sbytes)
                writelog.clear()
            elif not split.isprintable():
                bt.sbytes_write(sbytes)
                self.control_schars_emulate(schars=split)
            else:
                (row_y, column_x) = self.row_y_column_x_read(timeout=0)
                bt.sbytes_write(sbytes)

                for sch in split:

                    if column_x not in writelog.keys():
                        writelog[column_x] = dict()

                    writelog_x = writelog[column_x]
                    writelog_x[row_y] = sch

                    column_x += 1

                    # todo: .schars_write when out of bounds

                self.column_x = column_x

    def control_schars_emulate(self, schars) -> None:
        """Write Control Chars into .row_y and .column_x"""

        # Emulate 1 Control Char

        assert BS == "\b"  # 00/08 Backspace ⌃H
        assert HT == "\t"  # 00/09 Character Tabulation ⌃I
        assert LF == "\n"  # 00/10 Line Feed ⌃J  # akin to CSI CUD "\x1B" "[" "B"
        assert CR == "\r"  # 00/13 Carriage Return ⌃M  # akin to CSI CHA "\x1B" "[" "G"

        if len(schars) == 1:

            if schars == "\b":
                self.column_x -= 1
            elif schars == "\n":
                self.row_y += 1
            elif schars == "\r":
                self.column_x = 1
            elif schars == "\t":
                tab = 1 + 8 * ((self.column_x - 1) // 8)
                self.column_x = tab + 8

            return

        # Emulate 2 Control Chars

        assert DECSC == "\x1b" "7"  # ESC 03/07 Save Cursor [Checkpoint] (DECSC)
        assert DECRC == "\x1b" "8"  # ESC 03/08 Restore Cursor [Revert] (DECRC)

        if schars == "\x1b" "7":
            self.revert_y = self.row_y
            self.revert_x = self.column_x
            return

        if schars == "\x1b" "8":
            self.row_y = self.revert_y if (self.revert_y >= 1) else 1
            self.column_x = self.revert_x if (self.revert_x >= 1) else 1
            return

        # Emulate 1 CSI Control Sequence, into .row_y and .column_x

        self.csi_control_schars_emulate(schars)

    def csi_control_schars_emulate(self, schars) -> None:
        """Emulate 1 CSI Control Sequence, into .row_y and .column_x"""

        assert CSI_PIF_REGEX == r"(\x1B\[)" r"([0-?]*)" r"([ -/]*)" r"(.)"

        m = re.fullmatch(CSI_PIF_REGEX, string=schars)  # todo: merge with .schars_csi_partition
        if not m:
            return

        csi = m.group(1)
        p = m.group(2) if m.group(2) else ""
        # i = m.group(3) if m.group(3) else ""
        f = m.group(4)

        (py, px) = (p, "")
        if p.count(";") == 1:
            (py, px) = p.split(";")

        p = p if p else "1"  # mutates into default 1 for Final in ABCD E GdH IZ
        py = py if py else "1"
        px = px if px else "1"

        assert CUU_Y == "\x1b" "[" "{}A"  # CSI 04/01 Cursor Up
        assert CUD_Y == "\x1b" "[" "{}B"  # CSI 04/02 Cursor Down
        assert CUF_X == "\x1b" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right
        assert CUB_X == "\x1b" "[" "{}D"  # CSI 04/04 Cursor [Back] Left

        assert CNL_Y == "\x1b" "[" "{}E"  # CSI 04/05 Cursor Next Line (CNL)

        if csi and (f == "A"):
            self.row_y -= int(p)
        elif csi and (f == "B"):
            self.row_y += int(p)
        elif csi and (f == "C"):
            self.column_x += int(p)
        elif csi and (f == "D"):
            self.column_x -= int(p)

        elif csi and (f == "E"):
            self.row_y += int(p)
            self.column_x = 1

        assert CHA_X == "\x1b" "[" "{}G"  # CSI 04/07 Cursor Character Absolute
        assert VPA_Y == "\x1b" "[" "{}d"  # CSI 06/04 Line Position Absolute
        assert CUP_Y_X == "\x1b" "[" "{};{}H"  # CSI 04/08 Cursor Position

        if csi and (f == "G"):
            self.column_x = int(p)
        elif csi and (f == "d"):
            self.row_y = int(p)
        elif csi and (f == "H"):
            self.row_y = int(py)
            self.column_x = int(px)

        assert CHT_X == "\x1b" "[" "{}I"  # CSI 04/09 Cursor Forward [Horizontal] Tabulation
        assert CBT_X == "\x1b" "[" "{}Z"  # CSI 05/10 Cursor Backward Tabulation

        if csi and (f == "I"):
            tab = 1 + 8 * ((self.column_x - 1) // 8)
            self.column_x = tab + 8 * int(p)
        elif csi and (f == "Z"):
            tab = 1 + 8 * ((self.column_x - 1 + 8 - 1) // 8)
            self.column_x = tab - 8 * int(p)

        # todo: shrug off Exception's in 'int(p)', 'p.split', etc

    def schars_split(self, schars) -> list[str]:
        """Split Chars into Text and Controls"""  # todo: should match BytesTerminal.kbytes_read

        assert ESC == "\x1b"
        assert CSI == "\x1b" "["
        assert SS3 == "\x1b" "O"

        splits = list()

        assert CSI_PIF_REGEX == r"(\x1B\[)" r"([0-?]*)" r"([ -/]*)" r"(.)"

        split = ""
        for sch in schars:

            # Split out 1 And More Text Chars

            if not split:
                split = sch
                continue

            if split.isprintable():
                if sch.isprintable():
                    split += sch
                    continue

                splits.append(split)  # 1 And More Text Chars
                split = sch
                continue

            # Split out 1 Control Char, and start over

            if not split.startswith("\x1b"):
                splits.append(split)  # 1 Control Char  # ['\r', '\n']
                split = sch
                continue

            split_plus = split + sch

            # Split out 1 Esc Pair, and start over

            if len(split) == 1:
                split += sch
                if split_plus not in ("\x1b\x1b", "\x1b[", "\x1bO"):  # ESC ESC, CSI, SS3
                    splits.append(split)  # 1 Esc Pair
                    split = ""
                continue

            # Split out 1 SS3 Sequence, or begun plus a Byte

            if split == "\x1b\x1b":
                split += sch
                if split_plus in ("\x1b\x1bO", "\x1b\x1b["):  # ESC SS3, ESC CSI
                    continue

                splits.append(split)
                split = ""
                continue

            if split in ("\x1bO", "\x1b\x1bO"):  # SS3, ESC SS3
                split += sch

                splits.append(split)
                split = ""
                continue

            assert split.startswith("\x1b[") or split.startswith("\x1b\x1b["), (split,)  # CSI

            # Split out 1 CSI Sequence, or begun plus a Byte

            prefix = "\x1b"
            if split.startswith("\x1b\x1b"):
                prefix = "\x1b\x1b"

            csi_tail = split.removeprefix(prefix + "[")
            csi = "\x1b[" + csi_tail + sch
            csi_plus = csi + "."

            m0 = re.fullmatch(CSI_PIF_REGEX, string=csi_plus)
            if m0:
                split += sch
                continue

            m1 = re.fullmatch(CSI_PIF_REGEX, string=csi)
            if m1:
                split += sch

                splits.append(split)
                split = ""
                continue

            assert False, (split, sch)

        if split:
            splits.append(split)
            split = ""  # unneeded

        join = "".join(splits)
        assert join == schars, (join, splits, schars)

        return splits

        # todo: tight coupling across BytesTerminal.kbytes_read & StrTerminal.schars_split

    def schar_read_if(self, row_y, column_x, default) -> str:
        """Read 1 Char from the Screen, if logged before now"""

        writelog = self.writelog

        if column_x in writelog.keys():
            writelog_x = writelog[column_x]
            if row_y in writelog_x.keys():
                sch = writelog_x[row_y]
                return sch

        return default

    def writelog_bleach(self) -> None:
        """Write the Logged Screen back into place, but with present Highlight/ Color/ Style"""

        bt = self.bytes_terminal
        writelog = self.writelog

        row_y_column_x = self.row_y_column_x_read(timeout=0)

        for column_x in writelog.keys():  # insertion order
            writelog_x = writelog[column_x]
            for row_y in writelog_x.keys():  # insertion order
                self.write_row_y_column_x(row_y, column_x=column_x)

                sch = writelog_x[row_y]

                sbytes = sch.encode()
                bt.sbytes_write(sbytes)

        (row_y, column_x) = row_y_column_x
        self.write_row_y_column_x(row_y, column_x=column_x)

    #
    # Imagine the Bytes pulled from the Keyboard as an Encoding of the Key Caps Chord
    #

    def kstr_to_kbytes(self, kstr) -> bytes:  # noqa C901 too complex(17
        """Imagine the Bytes pulled from the Keyboard as an Encoding of the Key Caps Chord"""

        assert CSI_PIF_REGEX == r"(\x1B\[)" r"([0-?]*)" r"([ -/]*)" r"(.)"

        if not kstr:
            raise NotImplementedError(kstr)

        if kstr.isprintable():
            if len(kstr) == 1:  # 'A'  # '9'  # '█'
                if kstr in string.ascii_uppercase:
                    kbytes = kstr.casefold().encode()
                    return kbytes
                if kstr in string.ascii_lowercase:
                    upper = kstr.upper()
                    raise NotImplementedError(f"Did you mean '⇧{upper}' or '{upper}'?")
                kbytes = kstr.encode()
                return kbytes

        if kstr[:1] == "⇧":  # '⇧A'
            if kstr[-1] in string.ascii_uppercase:
                kbytes = kstr[-1].encode()
                return kbytes

        if kstr[:1] == "⌃":  # '⌃A'
            if len(kstr) == 2:
                kcode_n = ord(kstr[-1])
                if kcode_n in range(0x40, 0x60):
                    kbytes = bytes([kcode_n ^ 0x40])
                    return kbytes

        if kstr[:1] == "⎋":  # '⎋7'  # '⎋8'
            if len(kstr) == 2:
                if kstr[-1].isprintable():
                    kbytes = b"\x1b" + kstr[-1].encode()
                    return kbytes

        if kstr.startswith("⎋O"):  # '⎋OQ'  # '⎋OR'
            if len(kstr) == 3:
                if kstr[-1].isprintable():
                    kbytes = b"\x1b" + b"O" + kstr[-1].encode()
                    return kbytes

        if kstr.startswith("⎋⎋O"):  # '⎋⎋OQ'  # '⎋⎋OR'
            if len(kstr) == 4:
                if kstr[-1].isprintable():
                    kbytes = b"\x1b\x1b" + b"O" + kstr[-1].encode()
                    return kbytes

        if re.fullmatch(r"(⎋\[)" r"([0-?]*)" r"([ -/]*)" r"(.)", string=kstr):  # '⎋[2;2H'
            kbytes = b"\x1b" + kstr[1:].encode()
            return kbytes

        raise NotImplementedError(kstr)

        # todo: tight coupling across BytesTerminal.kbytes_read & StrTerminal.kstr_to_kbytes


class GlassTeletype:
    """Write/ Read Chars at Screen/ Keyboard of a Monospaced Rectangular Terminal"""

    bytes_terminal: BytesTerminal
    str_terminal: StrTerminal
    notes: list[str]

    # todo: Snoop a guess of what Chars in which Columns of which Rows
    # todo: Draw the new, undraw the old only where not already replaced

    #
    # Init, enter, exit, breakpoint
    #

    def __init__(self) -> None:

        st = StrTerminal()

        self.bytes_terminal = st.bytes_terminal
        self.str_terminal = st
        self.notes = list()

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

        breakpoint()  # c, where, up, down, p, pp ...
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
        (row_y, column_x) = st.row_y_column_x_read(timeout=0)
        return (row_y, column_x)

    def os_terminal_y_count_x_count(self) -> tuple[int, int]:
        st = self.str_terminal
        (y_count, x_count) = st.y_count_x_count_read(timeout=0)
        return (y_count, x_count)

    def writelog_bleach(self) -> None:
        st = self.str_terminal
        st.writelog_bleach()

    def write_row_y_column_x(self, row_y, column_x) -> None:
        st = self.str_terminal
        st.write_row_y_column_x(row_y, column_x)

    #
    # Loop Keyboard Bytes back onto the Screen
    #

    def keyboard_serve_one_kchord(self, kchord) -> None:
        """Reply to 1 Keyboard Chord"""

        if self.kchord_edit_like_macos(kchord):
            return

        (kbytes, kstr) = kchord

        if kstr == "Return":
            self.schars_write("\r\n")
        elif kstr == "Tab":
            self.schars_write("\t")
        elif kstr == "Spacebar":
            self.schars_write(" ")

        elif kstr == "⇧Tab":
            self.schars_write("\x1b[Z")  # CSI 05/10 Cursor Backward Tabulation (CBT)
        elif kstr == "←":
            self.schars_write("\x1b[D")  # CSI 04/04 Cursor [Backward] Left
        elif kstr == "↑":
            self.schars_write("\x1b[A")  # CSI 04/01 Cursor [Up] Previous
        elif kstr == "→":
            self.schars_write("\x1b[C")  # CSI 04/03 Cursor [Forward] Right
        elif kstr == "↓":
            self.schars_write("\x1b[B")  # CSI 04/02 Cursor [Down] Next

        else:
            self.kchord_write_kbytes_else_print_kstr(kchord)

    def kchord_edit_like_macos(self, kchord) -> bool:
        """Reply to 1 Keyboard Chord that edits the Terminal"""
        # Return True if served, else return False

        (kbytes, kstr) = kchord

        func_by_kstr = {
            "⌃A": self.do_column_go_leftmost,
            "⌃B": self.do_column_go_left,
            # "⌃D": self.do_char_delete_right,
            "⌃F": self.do_column_go_right,
            "⌃G": self.do_alarm_ring,
            # "⌃H": self.do_char_delete_left,
            # "⌃K": self.do_row_tail_delete,
            # "Return": self.do_row_insert_go_below,
            "⌃N": self.do_row_go_down,
            # "⌃O": self.do_row_insert_below,
            "⌃P": self.do_row_go_up,
            # "Delete": self.do_char_delete_left,
        }

        if kstr not in func_by_kstr.keys():
            return False

        func = func_by_kstr[kstr]
        func(kchord)

        return True

    def kchord_write_kbytes_else_print_kstr(self, kchord) -> None:
        """Write 1 Key Chord, else print its Key Caps"""

        st = self.str_terminal

        (kbytes, kstr) = kchord
        if not kbytes:
            kbytes = st.kstr_to_kbytes(kstr)

        schars = kbytes.decode()  # may raise UnicodeDecodeError

        assert DECIC_X == "\x1b" "[" "{}'}}"  # CSI 02/07 07/13 DECIC_X  # "}}" to mean "}"
        assert DECDC_X == "\x1b" "[" "{}'~"  # CSI 02/07 07/14 DECDC_X

        if not st.schars_to_writable(schars):
            st.schars_print(kstr, end=" ")
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

            st.schars_write(schars)

    #
    # Edit the Screen lots like macOS edit a Text Buffer
    #

    def do_alarm_ring(self, kchord) -> None:  # ⌃G
        """Ring the Terminal Bell"""

        self.schars_write("\a")  # Alarm Bell

    def do_char_delete_left(self, kchord) -> None:  # ⌃H  # Delete
        """Delete 1 Character at the Left of the Turtle"""

        self.schars_write("\b\x1b[P")  # CSI 05/00 Delete Character

        # todo: join lines from left edge

    def do_char_delete_right(self, kchord) -> None:  # ⌃D
        """Delete 1 Character at Right (like a Windows Delete)"""

        self.schars_write("\x1b[P")  # CSI 05/00 Delete Character

        # todo: join lines from right edge

    def do_column_go_left(self, kchord) -> None:  # ⌃B
        """Go to the Character at Left of the Turtle"""

        self.schars_write("\x1b[D")  # CSI 04/04 Cursor [Backward] Left  # could be "\b"

        # todo: wrap back across left edge

    def do_column_go_leftmost(self, kchord) -> None:  # ⌃A
        """Go to first Character of Row"""

        self.schars_write("\x1b[G")  # CSI 04/06 Cursor Char Absolute (CHA))  # could be "\r"

    def do_column_go_right(self, kchord) -> None:  # ⌃F
        """Go to the next Character of Row"""

        self.schars_write("\x1b[C")  # CSI 04/03 Cursor [Forward] Right

        # todo: wrap forward across right edge

    def do_row_go_down(self, kchord) -> None:  # ⌃N
        """Move as if you pressed the ↓ Down Arrow"""

        self.schars_write("\x1b[B")  # CSI 04/02 Cursor [Down] Next  # could be "\n"

    def do_row_go_up(self, kchord) -> None:  # ⌃P
        """Move as if you pressed the ↑ Up Arrow"""

        self.schars_write("\x1b[A")  # CSI 04/01 Cursor [Up] Previous

    def do_row_insert_below(self, kchord) -> None:  # ⌃O
        """Insert a Row below this Row"""

        (row_y, column_x) = self.os_terminal_y_row_x_column()
        if column_x != 1:
            self.schars_write("\x1b[G")  # CSI 04/06 Cursor Char Absolute (CHA))  # could be "\r"
        else:
            self.schars_write("\x1b[L")  # CSI 04/12 Insert Line [Row]

        # todo: split differently at left edge, at right edge, at middle

    def do_row_insert_go_below(self, kchord) -> None:  # Return
        """Insert a Row below this Row and move into it"""

        (row_y, column_x) = self.os_terminal_y_row_x_column()
        if column_x != 1:
            self.schars_write("\x1b[G")  # CSI 04/06 Cursor Char Absolute (CHA))  # could be "\r"
        else:
            self.schars_write("\x1b[L")  # CSI 04/12 Insert Line [Row]
            self.schars_write("\x1b[B")  # CSI 04/02 Cursor [Down] Next  # could be "\n"

        # todo: split differently at left edge, at right edge, at middle

    def do_row_tail_delete(self, kchord) -> None:  # ⌃K
        """Delete all the Characters at or to the Right of the Turtle"""

        st = self.str_terminal
        kchords = st.kchords

        self.schars_write("\x1b[K")  # CSI 04/11 Erase in Line  # 0 Tail # 1 Head # 2 Row

        (row_y, column_x) = self.os_terminal_y_row_x_column()
        if column_x == 1:
            kstrs = list(_[-1] for _ in kchords[-2:])
            if kstrs == ["⌃K", "⌃K"]:
                self.schars_write("\x1b[M")  # CSI 04/13 Delete Line [Row]

                kchord = (b"", "")  # takes ⌃K ⌃K ⌃K as ⌃K ⌃K and ⌃K
                kchords.append(kchord)

        # todo: join when run from right edge


glass_teletypes: list[GlassTeletype]
glass_teletypes = list()


#
# Define the Abbreviations of Turtles before defining Turtles themselves
#


CompassesByBearing = {
    45: ("NE", "Northeast"),
    90: ("E", "East"),
    135: ("SE", "Southeast"),
    180: ("S", "South"),
    225: ("SW", "Southwest"),
    270: ("W", "West"),
    315: ("NW", "Northwest"),
    360: ("N", "North"),
}
"""Names for Exact Compass Heading Floats"""


KwByGrunt = {
    "a": "angle",
    "d": "distance",
    "hz": "hertz",
    "n": "count",
    "x": "x",
    "y": "y",
}
"""Abbreviations for Turtle Verb Kw Arg Names"""


def _turtling_defaults_choose_() -> dict:
    """Choose default Values for KwArg Names"""

    angle = 0
    count = 1
    distance = 100
    hertz = 1e3
    mark = 2 * FullBlock  # '██'
    seconds = 1e-3
    x = 0
    xscale = 1
    y = 0
    yscale = 1

    _ = count

    d = dict(
        #
        accent=None,
        setpencolor_accent=None,
        #
        angle=0,
        arc_angle=90,
        circle_angle=360,
        left_angle=45,
        repeat_angle=360,
        right_angle=90,
        setheading_angle=angle,  # 0° North is 360° North
        #
        color="Bold",
        setpenhighlight_color="Plain",  # Uncolored
        setpencolor_color="Bold",
        #
        count=1,
        breakout_count=100,
        circle_count=-1,
        pong_count=100,
        puck_count=100,
        repeat_count=3,
        sierpiński_count=2,
        #
        distance=100,
        arc_distance=100,  # diameter
        backward_distance=200,
        circle_distance=50,  # radius
        forward_distance=distance,
        incx_distance=10,
        incy_distance=10,
        repeat_distance=100,
        sierpiński_distance=200,
        #
        hertz=1e3,  # todo: =1e3 or =1000 for hertz= ?
        sethertz_hertz=hertz,
        #
        mark=(2 * FullBlock),  # '██'
        setpenpunch_mark=mark,
        #
        seconds=1e-3,
        sleep_seconds=seconds,
        #
        x=0,
        xscale=1,
        setx_x=x,
        setxy_x=x,
        setxyzoom_xscale=xscale,
        #
        y=0,
        yscale=1,
        sety_y=y,
        setxy_y=y,
        setxyzoom_yscale=yscale,
        #
    )

    return d

    # Assymetric Defaults make editable Defaults more discoverable, because harder to ignore,
    #
    #   backward_distance != forward_distance
    #   count != repeat_count
    #   left_angle != right_angle
    #

    # 🐢 Right 90° sets up 🐢 Label to print English from left to right


TurtlingDefaults = _turtling_defaults_choose_()
"""Default Values for Turtle Verb Kw Arg Names"""


#
# Chat with 1 Logo Turtle
#


Logo = "Logo"
Trigonometry = "Trigonometry"  # todo: NotImplementedError vs Trigonometry
TunnelVision = "TunnelVision"  # todo: TunnelVision relevant only to Puck?

turtling_modes: list[str]
turtling_modes = list()
turtling_modes.append(Logo)


class Turtle:
    """Chat with 1 Logo Turtle"""

    glass_teletype: GlassTeletype  # where this Turtle draws
    namespace: dict  # variables of this Turtle, sometimes shared with others

    xfloat: float  # sub-pixel horizontal x-coordinate position
    yfloat: float  # sub-pixel vertical y-coordinate position
    xscale: float  # multiply Literal X Int/ Float by Scale
    yscale: float  # multiply Literal Y Int/ Float by Scale

    bearing: float  # stride direction

    backscapes: list[str]  # configuration of penpunch backdrop
    penscapes: list[str]  # configuration of penpunch ink
    penmark: str  # mark to punch at each step
    warping: bool  # moving without punching, else punching while moving
    erasing: bool  # erasing punches while moving
    hiding: bool  # hiding the Turtle, else showing the Turtle

    rest: float  # min time between marks

    def __init__(self) -> None:

        if not glass_teletypes:
            gt = GlassTeletype()
            gt.__enter__()
        gt = glass_teletypes[-1]

        self.backscapes = list()
        self.penscapes = list()

        namespace = dict()
        if turtling_sketchists:
            turtling_sketchist = turtling_sketchists[-1]
            namespace = turtling_sketchist.namespace

        self.glass_teletype = gt
        self.namespace = namespace

        self._reinit_()

        _turtles_list_.append(self)

    def _reinit_(self) -> None:
        """Clear the Turtle's Settings, but without writing the Screen"""

        self.namespace.clear()

        self.xfloat = 0e0
        self.yfloat = 0e0
        self.xscale = 100e-3
        self.yscale = 100e-3

        self.bearing = 360e0  # 360° of North Up Clockwise

        self.backscapes.clear()
        self.penscapes.clear()
        self.penscapes.append(Bold)
        self.penmark = 2 * FullBlock  # ██
        self.warping = False  # todo: imply .isdown more clearly
        self.erasing = False
        self.hiding = False

        self.rest = 1 / 1e3

        # macOS Terminal Sh Launch/ Quit doesn't clear the Graphic Rendition, Cursor Style, etc

    def bleach(self) -> dict:
        """Write the Logged Screen back into place, but with present Highlight/ Color/ Style"""

        gt = self.glass_teletype
        gt.writelog_bleach()

        return dict()

    def _breakpoint_(self) -> None:
        """Chat through a Python Breakpoint, but without redefining ⌃C SigInt"""

        gt = self.glass_teletype

        self._schars_write_("\r\n")
        gt.breakpoint()

    def bye(self) -> None:
        """Exit Sketchist & Client, without clearing the Sketchist Screen (EXIT or QUIT for short)"""

        gt = self.glass_teletype

        (y_count, x_count) = gt.os_terminal_y_count_x_count()
        assert y_count >= 1, (y_count,)

        y = y_count  # todo: remember why we coded this as 'y_count - 3' for awhile
        x = 1
        gt.write_row_y_column_x(row_y=y, column_x=x)

        sys.exit()

        # todo: surface "bye", "exit", "quit", more strongly

    def clearscreen(self) -> dict:
        """Write Spaces over every Character of every Screen Row and Column (CLS or CLEAR or CS for short)"""

        ctext = "\x1b[2J"  # CSI 04/10 Erase in Display  # 0 Tail # 1 Head # 2 Rows # 3 Scrollback
        self._schars_write_(ctext)

        (x_min, x_max, y_min, y_max) = self._xy_min_max_()

        d = dict(
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            clear="clearscreen",
            cls="clearscreen",
            cs="clearscreen",
        )
        return d

        # just the Screen, not also its Scrollback

        # Scratch: Erase-All

        # todo: undo/ clear Turtle Trails separately

    def _xy_min_max_(self) -> tuple[float, float, float, float]:
        """Say the Extent of the Screen, in SetXY Coordinates"""

        gt = self.glass_teletype

        (y_count, x_count) = gt.os_terminal_y_count_x_count()
        center_x = 1 + ((x_count - 1) // 2)  # biased left when odd
        center_y = 1 + ((y_count - 1) // 2)  # biased up when odd

        x_min = (1 - center_x) / 2  # doublewide X

        x_max = (x_count - center_x) / 2  # doublewide X
        x_max -= 1 / 2  # todo: figure out why we need this
        if x_count % 1:
            x_max -= 1 / 2  # todo: draw Half-Pixels at Right of Screen

        y_min = -(y_count - center_y)
        y_max = center_y - 1

        return (x_min, x_max, y_min, y_max)

        # todo: PyTurtle t.screen.screensize() returns just (x_max, y_max)
        # todo: PyTurtle t.screen.screensize() with Args does resize the Screen

    def relaunch(self) -> dict:
        """Warp the Turtle to Home, and clear its Settings, and clear the Screen"""

        turtling_modes.clear()

        self.restart()
        self.clearscreen()

        gt = self.glass_teletype
        gt.notes.clear()  # todo: Count Exception Notes lost per Relaunch

        d = self._asdict_()
        return d

        # FmsLogo Clean deletes 1 Turtle's trail, without clearing its Settings
        # PyTurtle Clear deletes 1 Turtle's Trail, without clearing its Settings

        # todo: more often test the corner of:  Relaunch  Relaunch

    def restart(self) -> dict:
        """Warp the Turtle to Home, and clear its Settings, but do Not clear the Screen (RESET for short)"""

        self.hideturtle()
        self.penup()
        self.home()

        self.pendown()
        self.setpenhighlight(color=None, accent=None)
        self.setpencolor(color=None, accent=None)  # todo: do we want optional 'accent='?

        self._reinit_()

        self.showturtle()

        self.restarting = True  # todo: multiple Listeners, Callbacks, ...

        d = self._asdict_()
        return d

        # todo: explain why .home before ._reinit_, why .showturtle after, etc

        # todo: Terminal Cursor Styles

    def _asdict_(self) -> dict:
        """Show most of the Turtle's Settings as a Dict"""

        d = {
            "xfloat": self.xfloat,
            "yfloat": self.yfloat,
            "bearing": self.bearing,
            "penscapes": self.penscapes,
            "penmark": self.penmark,
            "warping": self.warping,
            "erasing": self.erasing,
            "hiding": self.hiding,
            "rest": self.rest,
        }

        self._dict_insert_compass_if_(d)

        return d

        # omits .glass_teletype, .restarting

    #
    # Define what 1 Turtle can do
    #

    assert TurtlingDefaults["arc_angle"] == 90, (TurtlingDefaults,)
    assert TurtlingDefaults["arc_distance"] == 100, (TurtlingDefaults,)

    def arc(self, angle, distance) -> dict:
        """Draw a Part or All of a Circle, centered at Right Forward"""

        angle_float = float(90 if (angle is None) else angle)
        distance_float = float(100 if (distance is None) else distance)

        diameter = distance_float
        radius = diameter / 2

        bearing = self.bearing
        xscale = self.xscale
        yscale = self.yscale

        a1 = (90e0 - bearing) % 360e0  # converts to 0° East Anticlockwise
        (x1, y1) = self._x_y_position_()  # may change .xfloat .yfloat

        a0 = (a1 - 90e0) % 360e0
        x0 = (x1 / xscale) + (radius * math.cos(math.radians(a0)))
        y0 = (y1 / yscale) + (radius * math.sin(math.radians(a0)))

        marking_center = False
        if marking_center:
            isdown = self.isdown()
            self.penup()
            self.setxy(x0, y=y0)
            self.pendown()
            self.setxy(x0, y=y0)
            self.penup()
            self.setxy(x=x1 / xscale, y=y1 / yscale)
            if isdown:
                self.pendown()

        a1_ = round(a1 + 90e0)
        a2_ = round(a1 + 90e0 - angle_float)
        step = round(math.copysign(1, a2_ - a1_))

        for a in range(a1_, a2_ + step, step):
            x2 = x0 + (radius * math.cos(math.radians(a)))
            y2 = y0 + (radius * math.sin(math.radians(a)))
            self.setxy(x2, y=y2)

            # todo: pick the Angle Step less simply, not always abs(step) == 1

            # todo: Mode Trigonometry to Arc Anticlockwise
            # todo: Negative Arc Diameter to flip Anticlockwise/ Clockwise
            # todo: more similar output between PyTurtle Circle and our Circle via Arc

        self.right(angle_float)

        d = dict(
            xfloat=self.xfloat, yfloat=self.yfloat, bearing=self.bearing, a="angle", d="distance"
        )
        self._dict_insert_compass_if_(d)
        return d

        # todo: Turn the Turtle Heading WHILE we draw the Arc - Unneeded till we have Sprites

        # we have 🐢 Arc $Angle $Diameter, drawn by the Turtle, matched to Forward $Diameter
        # compare: PyTurtle Circle +/-$Radius $Angle

        # ugh: PyTurtle Circle $Radius $Angle $Count is near our 🐢 Repeat $Count $Angle $Distance
        # ugh: PyTurtle Circle anticlockwise for positive Radius despite Mode Logo with Clockwise Headings
        # ugh: UCBLogo Arc $Angle $Radius centers the Circle on the Turtle & keeps the turtle still

    def _dict_insert_compass_if_(self, d) -> None:
        """Insert Compass Direction, if Heading is exact"""

        compasses_by_bearing = CompassesByBearing

        items = list()
        for item in d.items():
            items.append(item)

            (k, v) = item
            if k == "bearing":
                bearing = v
                if bearing in compasses_by_bearing.keys():
                    compasses = compasses_by_bearing[bearing]  # ('NW', 'Northwest')
                    compass = compasses[-1]  # 'Northwest

                    item = ("compass", compass)
                    items.append(item)

        d.clear()
        d.update(items)

    assert TurtlingDefaults["backward_distance"] == 200, (TurtlingDefaults,)

    def backward(self, distance) -> dict:
        """Move the Turtle backwards along its Heading, leaving a Trail if Pen Down (BACK D for short)"""

        distance_float = float(200 if (distance is None) else distance)

        self._punch_bresenham_stride_(-distance_float, xys=None)  # for .backward

        d = dict(
            xfloat=self.xfloat, yfloat=self.yfloat, rest=self.rest, back="backward", bk="backward"
        )
        return d

    def beep(self) -> dict:
        """Ring the Terminal Alarm Bell once, remotely inside the Turtle (B for short)"""

        ctext = "\a"  # Alarm Bell
        self._schars_write_(ctext)

        # time.sleep(2 / 3)  # todo: guess more accurately when the Terminal Bell falls silent

        return dict(b="beep")

        # PyTurtle's work in silence, unless you add sound on the side

    def circle(self, distance, angle, count) -> dict:
        """Draw some or all of a Polygon or Circle, in the style of Python 'import turtle'"""

        angle_float = float(angle)
        angle_float = angle_float % 360e0  # 360° Circle
        angle_float = 360e0 if not angle_float else angle_float

        radius = distance
        if count < 0:
            diameter = 2 * radius
            self.arc(angle, distance=diameter)
        elif count != 1:
            raise NotImplementedError(f"PyTurtle t.circle count {count} != 1")
        else:
            polygon_count = round(360e0 / angle_float)  # todo: int, or round?
            step_distance = (math.tau * radius) / polygon_count
            self.right(angle)
            self.repeat(count=count, angle=angle, distance=step_distance)
            self.left(angle)

            # todo: Mode Trigonometry to Circle Anticlockwise
            # todo: Negative Circle Radius to flip Anticlockwise/ Clockwise
            # todo: more similar output between PyTurtle Circle and our Circle via Arc

        d = dict(
            xfloat=self.xfloat,
            yfloat=self.yfloat,
            bearing=self.bearing,
            d="distance",
            a="angle",
            n="count",
        )
        self._dict_insert_compass_if_(d)
        return d

        # PyTurtle Circle

    def _exec_(self, text) -> None:
        """Exec a Logo Turtle Text"""

        globals_ = globals()
        locals_ = self.namespace

        ps = PythonSpeaker()
        pycodes = ps.text_to_pycodes(text, cls=Turtle)
        for pycode in pycodes:
            exec_strict(pycode, globals_, locals_)

    assert TurtlingDefaults["forward_distance"] == 100, (TurtlingDefaults,)

    def forward(self, distance) -> dict:
        """Move the Turtle forwards along its Heading, leaving a Trail if Pen Down (FD D for short)"""

        distance_float = float(100 if (distance is None) else distance)

        self._punch_bresenham_stride_(distance_float, xys=None)  # for .forward

        d = dict(xfloat=self.xfloat, yfloat=self.yfloat, rest=self.rest, fd="forward", d="distance")
        return d

        # Scratch Move-10-Steps (with infinite speed)
        # Scratch Glide-1-Secs-To-X-0-Y-0 (locks out parallel work)

    def defaults(self) -> dict:
        """Show the Turtle's own Defaults for each Verb KwArg, until overriden by Locals"""

        d = dict(TurtlingDefaults)
        return d

    def h(self) -> dict:
        """Show the Turtle's Most Cryptic Abbreviations"""

        ps = PythonSpeaker()

        d0 = dict(ps.verb_by_grunt)
        d1 = dict(_ for _ in KwByGrunt.items() if _[0] != _[-1])

        d = dict(short_verbs=d0, short_argument_keywords=d1)

        return d

    def hideturtle(self) -> dict:
        """Stop showing where the Turtle is (HT for short)"""

        ctext = "\x1b[?25l"  # 06/12 Reset Mode (RM) 25 VT220 DECTCEM
        self._schars_write_(ctext)

        self.hiding = True

        d = dict(hiding=self.hiding, ht="hideturtle")
        return d

    def home(self) -> dict:
        """Move the Turtle to its Home and turn it North, leaving a Trail if Pen Down"""

        self.setxy(x=0e0, y=0e0)  # todo: different Homes for different Turtles
        self._setbearing_(360e0)

        d = dict(xfloat=self.xfloat, yfloat=self.yfloat, bearing=self.bearing)
        self._dict_insert_compass_if_(d)
        return d

        # todo: good that .home doesn't follow/ change .setxy and .setheading defaults?

    assert TurtlingDefaults["incx_distance"] == 10, (TurtlingDefaults,)

    def incx(self, distance) -> dict:
        """Move the Turtle along the X Axis, keeping Y unchanged, leaving a Trail if Pen Down"""

        distance_float = float(10 if (distance is None) else distance)

        xfloat_ = self.xfloat
        yfloat_ = self.yfloat
        xfloat = xfloat_ / self.xscale
        yfloat = yfloat_ / self.yscale

        xplus = xfloat + distance_float
        self.setxy(x=xplus, y=yfloat)

        d = dict(xfloat=self.xfloat, d="distance")
        return d

        # Scratch: Change-X-By-10

    assert TurtlingDefaults["incy_distance"] == 10, (TurtlingDefaults,)

    def incy(self, distance) -> dict:
        """Move the Turtle along the Y Axis, keeping X unchanged, leaving a Trail if Pen Down"""

        distance_float = float(10 if (distance is None) else distance)

        xfloat_ = self.xfloat
        yfloat_ = self.yfloat
        xfloat = xfloat_ / self.xscale
        yfloat = yfloat_ / self.yscale

        yplus = yfloat + distance_float
        self.setxy(x=xfloat, y=yplus)

        d = dict(yfloat=self.yfloat, d="distance")
        return d

        # Scratch: Change-Y-By-10

    def isdown(self) -> bool:
        """Say if the Turtle will leave a Trail as it moves"""

        down = not self.warping
        return down

        # Lisp'ish Logo's say IsDown as PenDownP and as PenDown?

    def iserasing(self) -> bool:
        """Say if the Turtle will erase a Trail as it moves"""

        erasing = self.erasing
        return erasing

    def isvisible(self) -> bool:
        """Say if the Turtle is showing where it is"""

        visible = not self.hiding
        return visible

        # Lisp'ish Logo's say IsVisible as ShownP and as Shown?

    def label(self, *args) -> dict:
        """Write the Str's of 0 or more Args, separated by Spaces"""

        gt = self.glass_teletype
        bearing = self.bearing

        if round(bearing) != 90:  # 90° East
            raise NotImplementedError("Printing Labels for Headings other than 90° East")

            # todo: Printing Labels for 180° South Heading
            # todo: Printing Labels for -90° West and 0° North
            # todo: Printing Labels for Headings other than 90° East and 180° South

        (row_y, column_x) = gt.os_terminal_y_row_x_column()

        text = " ".join(str(_) for _ in args)
        ctext = f"\x1b[{row_y};{column_x}H"  # CSI 06/12 Cursor Position  # 0 Tail # 1 Head # 2 Rows # 3 Columns]"
        ctext += "\n"  # just Line-Feed \n without Carriage-Return \r

        self._schars_write_(text)  # for .label
        self._schars_write_(ctext)
        self.yfloat -= 1

        hiding = self.hiding
        rest = self.rest
        if not hiding:
            time.sleep(rest)

        d = dict(xfloat=self.xfloat, yfloat=self.yfloat)
        return d

        # Scratch Say

        # todo: most Logo's feel the Turtle should remain unmoved after printing a Label??
        # todo: call gt.write_row_y_column_x ?

    assert TurtlingDefaults["left_angle"] == 45, (TurtlingDefaults,)

    def left(self, angle) -> dict:
        """Turn the Turtle anticlockwise, by a 45° Right Angle, or some other Angle (LT A for short)"""

        angle_float = float(45 if (angle is None) else angle)

        bearing = self.bearing
        self._setbearing_(bearing - angle_float)

        d = dict(bearing=self.bearing, lt="left", a="angle")
        self._dict_insert_compass_if_(d)
        return d

        # Scratch Turn-CCW-15-Degrees

    def _mode_(self, hints) -> dict:
        """Choose a dialect of the Logo Turtle Language"""

        defined_modes = (Logo, Trigonometry, TunnelVision)

        if hints is None:
            return dict()

        for hint in hints.split():
            hint_modes = list(_ for _ in defined_modes if _.casefold().startswith(hint.casefold()))
            if (len(hint_modes) != 1) or (len(hint) < 4):
                raise ValueError(f"Choose Mode from {defined_modes}, not {hint!r}")

                # todo: limit land grab of first 4 Characters of Turtle Mode?

            hint_mode = hint_modes[-1]
            if hint_mode not in turtling_modes:

                if hint_mode == Trigonometry:
                    raise NotImplementedError("🐢 mode Trigonometry")

                turtling_modes.append(hint_mode)
                turtling_modes.sort()

                # todo: implement Trigonometry in Headings and Initial Zero Heading
                # todo: how to undo TunnelVision, short of a full 🐢 Relaunch?

        modes = list(turtling_modes)  # 'copied is better than aliased'
        return dict(modes=modes)

        # todo: Trigonometry Angles start at 90° North and rise to turn Left
        # todo: Logo Angles starts at 0° North and rise to turn Right
        # todo: Locals Tau can be 360° or 2π Radians

    def pe(self) -> dict:
        raise NotImplementedError("Did you mean PenErase?")

    def pendown(self) -> dict:
        """Plan to leave a Trail as the Turtle moves (PD for short)"""

        self.warping = False
        self.erasing = False

        d = dict(warping=self.warping, erasing=self.erasing, pd="pendown")
        return d

        # Scratch Pen-Down

        # todo: calculated boolean args for pd pu ht gt

    def penerase(self) -> dict:
        """Plan to erase a Trail as the Turtle moves"""

        self.warping = False
        self.erasing = True

        d = dict(warping=self.warping, erasing=self.erasing)
        return d

        # Scratch Pen-Down

        # todo: calculated boolean args for pd pu ht gt

    def penup(self) -> dict:
        """Plan to Not leave a Trail as the Turtle moves (PU for short)"""

        self.warping = True
        self.erasing = False

        d = dict(warping=self.warping, erasing=self.erasing, pu="penup")
        return d

        # Scratch Pen-Up

    def press(self, kline) -> dict:
        """Take a Keyboard Chord Sequence from the Chat Pane, as if pressed in the Drawing Pane"""

        gt = self.glass_teletype
        st = gt.str_terminal

        assert KCAP_SEP == " "

        for kstr in kline.split():
            kchord = (b"", kstr)
            gt.keyboard_serve_one_kchord(kchord)

        (row_y, column_x) = (st.row_y, st.column_x)
        self._snap_to_column_x_row_y_(column_x, row_y=row_y)

        return dict(row_y=row_y, column_x=column_x)

        # todo: tight coupling across StrTerminal KCaps_Append & Turtle Press

        # todo: 🐢 Press with multiple Arguments

    assert TurtlingDefaults["repeat_count"] == 3, (TurtlingDefaults,)
    assert TurtlingDefaults["repeat_angle"] == 360, (TurtlingDefaults,)
    assert TurtlingDefaults["repeat_distance"] == 100, (TurtlingDefaults,)

    def repeat(self, count, angle, distance) -> dict:
        """Run some instructions a chosen number of times, often less or more than once (REP N A D for short)"""

        # self.glass_teletype.notes.append(f"repeat {count=} {angle=} {distance=}")

        int_count = int(90 if (count is None) else count)
        angle_float = float(90 if (angle is None) else angle)
        distance_float = float(100 if (distance is None) else distance)

        a = angle_float / int_count
        for _ in range(int_count):  # such as (int_count == 1) at:  circle 50 45 8
            self.forward(distance_float)
            self.right(a)

            # the traditional [fd rt], never the countercultural [rt fd]

        d = dict(
            xfloat=self.xfloat,
            yfloat=self.yfloat,
            bearing=self.bearing,
            rep="repeat",
            n="count",
            a="angle",
            d="distance",
        )
        self._dict_insert_compass_if_(d)

        return d

        # ugh: PyTurtle Circle $Radius $Angle $Count is near our 🐢 Repeat $Count $Angle $Distance

    assert TurtlingDefaults["right_angle"] == 90, (TurtlingDefaults,)

    def right(self, angle) -> dict:
        """Turn the Turtle clockwise, by a 90° Right Angle, or some other Angle (RT A for short)"""

        angle_float = float(90 if (angle is None) else angle)

        bearing = self.bearing  # turning clockwise
        self._setbearing_(bearing + angle_float)

        d = dict(bearing=self.bearing, rt="right", a="angle")
        self._dict_insert_compass_if_(d)
        return d

        # Scratch Turn-CW-15-Degrees

    assert TurtlingDefaults["setheading_angle"] == 0, (TurtlingDefaults,)

    def setheading(self, angle) -> dict:
        """Turn the Turtle to move 0° North, or to some other Heading (SETH A for short)"""

        b = self._bearing_to_float_(angle)
        self._setbearing_(b)

        d = dict(bearing=self.bearing, seth="setheading", a="angle")
        self._dict_insert_compass_if_(d)

        return d

    def _bearing_to_float_(self, bearing) -> float:
        """Take Str Heading as Name of Float, else return Heading unchanged"""

        compasses_by_bearing = CompassesByBearing

        # Tabulate Heading Float by Compass Heading Name

        bearing_by_casefold: dict[str, float]
        bearing_by_casefold = dict()

        for b, cc in compasses_by_bearing.items():
            for c in cc:
                s = c.casefold()
                if s not in bearing_by_casefold.keys():
                    bearing_by_casefold[s] = b  # inits
                else:
                    # bearing_by_casefold[s] = None  # replaces
                    assert False, (s, bearing_by_casefold[s], b)

        # Return Angle cloned, essentially unchanged, when not Str

        if not isinstance(bearing, str):
            float_bearing = float(bearing)
            return float_bearing

        # Convert Compass Heading Str to Float

        casefold = bearing.casefold()
        float_bearing = bearing_by_casefold[casefold]  # raises ValueError when undefined

        return float_bearing

    def _setbearing_(self, angle) -> None:
        """Turn the Turtle to move 0° North, or to some other Heading (SETH A for short)"""

        angle_float = float(0 if (angle is None) else angle)

        bearing1 = angle_float % 360e0  # 360° Circle
        bearing2 = 360e0 if not bearing1 else bearing1

        self.bearing = bearing2

    assert TurtlingDefaults["sethertz_hertz"] == 1e3, (TurtlingDefaults,)

    def sethertz(self, hertz) -> dict:
        """Say how many Characters to draw per Second with the Pen (SETHZ HZ for short)"""

        hertz_float = float(1e3 if (hertz is None) else hertz)

        rest1 = 0e0
        if hertz_float:
            rest1 = 1 / hertz_float

            assert rest1 >= 0e0, (rest1, hertz_float, hertz)  # 0e0 at Inf Hertz

        self.rest = rest1

        d = dict(rest=self.rest, sethz="sethertz", hz="hertz")
        return d

        # PyTurtle Speed chooses 1..10 for faster animation, reserving 0 for no animation
        # PyTurtle Screen Delay Milliseconds runs like an inverse of our SetHertz

    def setpenhighlight(self, color, accent) -> dict:  # as if gDoc Highlight Color
        """Take a number, two numbers, or some words as the Highlight to draw on (SETPH for short)"""

        assert COLOR_ACCENTS == (None, 3, 4, 4.6, 8, 24)
        assert accent in (None, 3, 4, 4.6, 8, 24), (accent,)

        backscapes = self.backscapes
        penscapes = self.penscapes

        # Start over, but defer change until returning without Exception

        backscapes_: list[str]
        backscapes_ = []

        # Take a number, two numbers, or some words

        if color is not None:
            if isinstance(color, str):
                self._scapes_take_words_(
                    backscapes_, color, accent=accent, func=self._backscapes_take_numbers_
                )
            else:
                floatish = (
                    isinstance(color, float) or isinstance(color, int) or isinstance(color, bool)
                )
                if floatish:  # todo: or isinstance(color, decimal.Decimal):
                    self._backscapes_take_numbers_(backscapes_, color, accent=accent)
                else:
                    raise NotImplementedError(type(color), type(accent), color, accent, floatish)

        # Accept the change, and catch up the Terminal

        backscapes[::] = backscapes_
        self._schars_write_("".join([Plain] + backscapes + penscapes))

        d = dict(backscapes=backscapes_, setph="setpenhighlight")
        return d

    def setpencolor(self, color, accent) -> dict:  # as if gDoc Text Color
        """Take a number, two numbers, or some words as the Color to draw with (SETPC for short)"""

        assert COLOR_ACCENTS == (None, 3, 4, 4.6, 8, 24)
        assert accent in (None, 3, 4, 4.6, 8, 24), (accent,)

        backscapes = self.backscapes
        penscapes = self.penscapes

        # Start over, but defer change until returning without Exception

        penscapes_ = [Bold]

        # Take a number, two numbers, or some words

        if color is not None:
            if isinstance(color, str):
                self._scapes_take_words_(
                    penscapes_, color, accent=accent, func=self._penscapes_take_numbers_
                )
            else:
                floatish = (
                    isinstance(color, float) or isinstance(color, int) or isinstance(color, bool)
                )
                if floatish:  # todo: or isinstance(color, decimal.Decimal):
                    self._penscapes_take_numbers_(penscapes_, color, accent=accent)
                else:
                    raise NotImplementedError(type(color), type(accent), color, accent, floatish)

        # Accept the change, and catch up the Terminal

        penscapes[::] = penscapes_
        self._schars_write_("".join([Plain] + backscapes + penscapes))

        d = self._penscapes_disassemble_(penscapes_)
        assert "penscapes" not in d.keys()
        d["penscapes"] = penscapes_
        d["setpc"] = "setpencolor"

        return d

        # todo: don't write through to Terminal when no change to Backscapes/ Penscapes

        # todo: Scratch Change-Pen-Color-By-10

    def _penscapes_disassemble_(self, penscapes) -> dict:
        """Disassemble the R:G:B and Grayscale of 8-bit Terminal Color"""

        d: dict[str, str]
        d = dict()

        for penscape in penscapes:
            part = penscape
            part = part.partition("\x1b[38;5;")[-1]
            part = part.partition("m")[0]
            if f"\x1b[38;5;{part}m" == penscape:
                code = int(part)

                assert (16 + (6 * 6 * 6) + 24) == 0x100

                if (16 + (6 * 6 * 6) - 1) < code < 0x100:
                    gray25 = 24
                    if code >= (16 + (6 * 6 * 6)):
                        gray25 = code - (16 + (6 * 6 * 6))

                    assert "grayscale" not in d.keys()
                    d["grayscale"] = f"{gray25}/24"

                if 16 <= code < (16 + (6 * 6 * 6)):
                    r6g6b6 = code - 16

                    r6 = r6g6b6 // 36
                    g6 = (r6g6b6 // 6) % 6
                    b6 = r6g6b6 % 6

                    r = int(r6 * 0xFF / 5)  # todo: off-by-one in either direction?
                    g = int(g6 * 0xFF / 5)
                    b = int(b6 * 0xFF / 5)

                    assert "rrggbb" not in d.keys()
                    d["rrggbb"] = f"{r:02X}{g:02X}{b:02X}"

        return d

    def _platform_color_accent_(self) -> int:
        """Guess which Color Accent works best in this Terminal"""

        # Find 8-bit macOS Terminal Color at 'Darwin' 'xterm-256color' without $COLORTERM

        if platform.system() == "Darwin":
            if "TERM" in os.environ.keys():
                env_term = os.environ["TERM"]
                if env_term == "xterm-256color":
                    if "COLORTERM" not in os.environ.keys():
                        return 8

                    # Or with empty $COLORTERM

                    env_colorterm = os.environ["COLORTERM"]
                    if not env_colorterm:
                        return 8

        # Else guess 24-bit Html Color

        return 24

        # 8 at macOS TERM=xterm-256color .system='Darwin'
        # 24 at gShell TERM=screen .system='Linux'
        # 24 at replIt TERM=xterm-256color .system='Linux'

        # todo: save how much time by cacheing 'def _platform_color_accent_' per Process?

    _number_by_word_ = dict(
        black=0,
        red=1,
        yellow=3,
        green=2,
        cyan=6,
        blue=4,
        magenta=5,
        white=7,
    )

    def _scapes_take_words_(self, penscapes, color, accent, func) -> None:
        """Choose Color by a Sequence of Words"""

        # Take one Word at a time

        splits = color.split()
        for split in splits:
            casefold = split.casefold()

            # Define words for None/ Plain and Bold

            if casefold in ("None".casefold(), "plain"):
                penscapes.clear()
                continue

            if casefold == "bold":
                penscapes.append("\x1b[1m")  # 1m Sgr Plain
                continue

            # Take any of the 8 smallest Color Words

            if casefold in self._number_by_word_.keys():
                number = self._number_by_word_[casefold]

                assert accent in (None, 3, 4), (accent, split, color)
                if accent != 4:
                    func(penscapes, color=number, accent=3)
                else:
                    func(penscapes, color=number, accent=4)
                continue

            # Take 24-bit Html Hexadecimal 6 or 7 Character Color Strings

            if casefold.strip("#0123456789abcdef") == "":
                if "#" not in casefold:
                    casefold = "#" + casefold

                platform_accent = self._platform_color_accent_()
                accent_ = platform_accent if (accent is None) else accent
                assert accent_ in (8, 24), (accent_,)

                m = re.match(
                    r"#([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])", string=casefold
                )
                assert m, (accent, split, color, "not found in #000000 .. #FFffFF")

                r = int(m.group(1), 0x10)
                g = int(m.group(2), 0x10)
                b = int(m.group(3), 0x10)

                if accent_ == 24:
                    number = (r << 16) + (g << 8) + b
                else:
                    assert accent_ == 8, (accent, split, color)

                    r_ = int(r * 6 / 0x100)
                    g_ = int(g * 6 / 0x100)
                    b_ = int(b * 6 / 0x100)

                    number = 16 + (r_ * 36) + (g_ * 6) + b_

                func(penscapes, color=number, accent=accent_)

                continue

            # Accept Control Character Sequences

            controls = any(unicodedata.category(_).startswith("C") for _ in split)
            assert controls, (accent, split, color)

            penscapes.append(split)
            continue

        # todo: drop dupes?

    def _backscapes_take_numbers_(self, backscapes, color, accent) -> None:
        """Choose background Pen Highlight Escape Control Sequences by Number"""

        color = int(color)

        platform_accent = self._platform_color_accent_()
        accent_ = platform_accent if (accent is None) else accent
        assert COLOR_ACCENTS == (None, 3, 4, 4.6, 8, 24)
        assert accent_ in (3, 4, 4.6, 8, 24), (accent,)

        if accent == 4.6:
            assert 0 <= color < 25, (color, accent_, accent)
        else:
            assert 0 <= color < (1 << accent_), (color, accent_, accent)

        if accent_ == 3:

            backscapes.append(f"\x1b[{40 + color}m")  # 3-Bit Color

        elif accent_ == 4:

            if color < 8:
                backscapes.append(f"\x1b[{100 + color}m")  # second half of 4-Bit Color
            else:
                backscapes.append(f"\x1b[{40 + color - 8}m")  # first half of 4-Bit Color

        elif accent_ == 4.6:

            if color < 24:
                backscapes.append(f"\x1b[48;5;{232 + color}m")
            else:
                assert color == 24, (color, accent, accent_)
                backscapes.append(f"\x1b[48;5;{232 - 1}m")  # 231 8-Bit Color R G B = Max 5 5 5

        elif accent_ == 8:

            backscapes.append(f"\x1b[48;5;{color}m")

        else:
            assert accent_ == 24, (color, accent_, accent)

            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF

            backscapes.append(f"\x1b[48;2;{r};{g};{b}m")  # 24-Bit R:G:B Color

    def _penscapes_take_numbers_(self, penscapes, color, accent) -> None:
        """Choose foreground Pen Color Escape Control Sequences by Number"""

        color = int(color)

        platform_accent = self._platform_color_accent_()
        accent_ = platform_accent if (accent is None) else accent
        assert COLOR_ACCENTS == (None, 3, 4, 4.6, 8, 24)
        assert accent_ in (3, 4, 4.6, 8, 24), (accent,)

        if accent_ == 4.6:
            assert 0 <= color < 25, (color, accent_, accent)
        else:
            assert 0 <= color < (1 << accent_), (color, accent_, accent)

        if accent_ == 3:

            penscapes.append(f"\x1b[{30 + color}m")  # 3-Bit Color

        elif accent_ == 4:

            if color < 8:
                penscapes.append(f"\x1b[{90 + color}m")  # second half of 4-Bit Color
            else:
                penscapes.append(f"\x1b[{30 + color - 8}m")  # first half of 4-Bit Color

        elif accent_ == 4.6:

            if color < 24:
                penscapes.append(f"\x1b[38;5;{232 + color}m")
            else:
                assert color == 24, (color, accent, accent_)
                penscapes.append(f"\x1b[38;5;{232 - 1}m")  # 231 8-Bit Color R G B = Max 5 5 5

        elif accent_ == 8:

            penscapes.append(f"\x1b[38;5;{color}m")

        else:
            assert accent_ == 24, (color, accent_, accent)

            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF

            penscapes.append(f"\x1b[38;2;{r};{g};{b}m")  # 24-Bit R:G:B Color

    assert TurtlingDefaults["setpenpunch_mark"] == "██", (TurtlingDefaults,)

    def setpenpunch(self, mark) -> dict:
        """Choose which Character to draw with, or default to '██' (SETPCH for short)"""

        floatish = isinstance(mark, float) or isinstance(mark, int) or isinstance(mark, bool)
        if mark is None:
            penmark1 = 2 * FullBlock  # '██'
        elif floatish or isinstance(mark, decimal.Decimal):
            penmark1 = chr(int(mark))  # not much test of '\0' yet
        elif isinstance(mark, str):
            penmark1 = mark
        else:
            assert False, (type(mark), mark)

        self.penmark = penmark1

        d = dict(penmark=self.penmark, setpenpunch="setpenpunch", mark="mark")
        return d

        # todo: cyclic US Ascii Penmarks:  "!" if (penmark == "~") else chr(ord(penmark) + 1)
        # todo: Penmark by Ord for more than 1 Ord

    def setx(self, x) -> dict:
        """Move the Turtle to a X Point, keeping Y unchanged, leaving a Trail if Pen Down"""

        yfloat_ = self.yfloat
        yfloat = yfloat_ / self.yscale

        self.setxy(x=x, y=yfloat)  # X may be None

        d = dict(xfloat=self.xfloat)
        return d

    assert TurtlingDefaults["setxy_x"] == 0, (TurtlingDefaults,)
    assert TurtlingDefaults["setxy_y"] == 0, (TurtlingDefaults,)

    def setxy(self, x, y) -> dict:
        """Move the Turtle to an X Y Point, leaving a Trail if Pen Down (GOTO or SETPOS or SETPOSITION for short)"""

        xfloat = float(0 if (x is None) else x)
        yfloat = float(0 if (y is None) else y)

        # Choose the Starting Point

        (x1, y1) = self._x_y_position_()  # may change .xfloat .yfloat

        # Choose the Ending Point

        xfloat_ = xfloat * self.xscale
        yfloat_ = yfloat * self.yscale

        xfloat__ = round(xfloat_, 10)
        yfloat__ = round(yfloat_, 10)

        x2 = round(2 * xfloat_) / 2  # doublewide X
        y2 = round(yfloat_)

        # Draw the Line Segment to X2 Y2 from X1 Y1

        self._punch_bresenham_segment_(x1, y1=y1, x2=x2, y2=y2, xys=None)

        # Catch up the Precise X Y Shadows

        self.xfloat = xfloat__
        self.yfloat = yfloat__

        d = dict(
            xfloat=self.xfloat, yfloat=self.yfloat, setposition="setxy", setpos="setxy", goto="setxy"
        )
        return d

        # todo: Share most of .setxy with ._punch_bresenham_stride_ of .forward/ .backward

        # FMSLogo SetXY & UBrown SetXY & UCBLogo SetXY alias SetPos
        # PyTurtle Goto aliases SetPos, PyTurtle Teleport is a With PenUp SetPos
        # Scratch Point-In-Direction-90
        # Scratch Go-To-X-Y
        # UCBLogo Goto is a Control Flow Goto

    def setxyzoom(self, xscale, yscale) -> dict:
        """Choose an X:Y Ratio of Zoom"""

        assert xscale, (xscale,)
        assert yscale, (yscale,)

        self.xscale = round(xscale * 100e-3, 10)
        self.yscale = round(yscale * 100e-3, 10)

        d = dict(xscale=self.xscale, yscale=self.yscale)
        return d

        # UCBLogo SetScrunch

    def sety(self, y) -> dict:
        """Move the Turtle to a Y Point, keeping X unchanged, leaving a Trail if Pen Down"""

        xfloat_ = self.xfloat
        xfloat = xfloat_ / self.xscale

        self.setxy(x=xfloat, y=y)  # Y may be None

        d = dict(yfloat=self.yfloat)
        return d

    def showturtle(self) -> dict:
        """Start showing where the Turtle is (ST for short)"""

        ctext = "\x1b[?25h"  # 06/08 Set Mode (SMS) 25 VT220 DECTCEM
        self._schars_write_(ctext)

        self.hiding = False

        # Forward 0 leaves a Mark to show Turtle was Here
        # SetXY from Home leaves a Mark to show the X=0 Y=0 Home

        d = dict(hiding=self.hiding, st="showturtle")
        return d

    assert TurtlingDefaults["sleep_seconds"] == 1e-3, (TurtlingDefaults,)

    def sleep(self, seconds) -> dict:
        """Hold the Turtle still for a moment (S for short)"""

        second_float = float(1e-3 if (seconds is None) else seconds)

        time.sleep(second_float)  # may raise ValueError or TypeError

        return dict()  # not the sticky .rest, and not this transient .seconds either

        # todo: give credit for delay in work before t.sleep

        # tested with:  sethertz 5  st s ht s  st s ht s  st s ht s  st

    def tada(self) -> dict:
        """Call HideTurtle immediately, and then ShowTurtle before anything else (T for short)"""

        self.hideturtle()

        d = dict(next_python_codes=["t.showturtle()"])
        return d

    def teleport(self, x, y) -> dict:
        """Move the Turtle to an X Y Point, without leaving a Trail"""

        raise NotImplementedError("Did you mean PenUp Home PenDown?")

        # PyTurtle Teleport = pu home pd, but can't say: pu home seth fd pd

    def write(self, s) -> None:
        """Write one Str to the Screen"""

        gt = self.glass_teletype
        st = gt.str_terminal

        self._schars_write_(s)  # for .write  # arbitrary mix of Controls and Text

        (row_y, column_x) = (st.row_y, st.column_x)
        self._snap_to_column_x_row_y_(column_x, row_y=row_y)

        # PyTurtle Write

    def _snap_to_column_x_row_y_(self, column_x, row_y) -> None:
        """Secretly silently snap to the emulated Cursor Row-Column"""

        gt = self.glass_teletype

        (y_count, x_count) = gt.os_terminal_y_count_x_count()

        center_x = 1 + ((x_count - 1) // 2)  # biased left when odd
        center_y = 1 + ((y_count - 1) // 2)  # biased up when odd

        x1 = (column_x - center_x) / 2  # doublewide X
        y1 = -(row_y - center_y)

        xfloat_ = float(x1)  # 'explicit is better than implicit'
        yfloat_ = float(y1)

        self.xfloat = xfloat_
        self.yfloat = yfloat_

    def _schars_write_(self, s) -> None:
        """Write one Str to the Screen"""

        gt = self.glass_teletype
        gt.schars_write(s)  # for ._schars_write_

    def xcor(self) -> float:
        """Say the Turtle's X Position"""

        xfloat = self.xfloat / self.xscale
        return xfloat

        # FMSLogo XCor, PyTurtle XCor, UCBLogo XCor

    def ycor(self) -> float:
        """Say the Turtle's Y Position"""

        yfloat = self.yfloat / self.yscale
        return yfloat

        # FMSLogo YCor, PyTurtle YCor, UCBLogo YCor

    #
    # Move the Turtle along the Line of its Heading, leaving a Trail if Pen Down
    #

    def _punch_bresenham_stride_(self, stride, xys) -> None:
        """Step forwards, or backwards, along the Heading"""

        xfloat = self.xfloat
        yfloat = self.yfloat

        xstride_ = float(stride) * self.xscale
        ystride_ = float(stride) * self.yscale

        bearing = self.bearing  # 0° North Up Clockwise

        # Limit travel

        (x_min, x_max, y_min, y_max) = self._xy_min_max_()

        # Choose the Starting Point

        if xys is None:
            (x1, y1) = self._x_y_position_()  # may change .xfloat .yfloat
        else:
            x1 = round(2 * xfloat) / 2  # doublewide X
            y1 = round(yfloat)

        xfloat = self.xfloat
        yfloat = self.yfloat

        assert ((2 * x1) == round(2 * xfloat)) and (y1 == round(yfloat)), (x1, xfloat, y1, yfloat)

        # Choose the Ending Point

        angle = (90e0 - bearing) % 360e0  # converts to 0° East Anticlockwise

        xfloat_ = xfloat + (xstride_ * math.cos(math.radians(angle)))
        yfloat_ = yfloat + (ystride_ * math.sin(math.radians(angle)))

        xfloat_ = min(max(xfloat_, x_min), x_max)  # limits X
        yfloat_ = min(max(yfloat_, y_min), y_max)  # limits Y

        xfloat__ = round(xfloat_, 10)  # todo: how round should our Float Maths be?
        yfloat__ = round(yfloat_, 10)  # todo: are we happy with -0.0 and +0.0 flopping arund?

        x2 = round(2 * xfloat__) / 2  # doublewide X
        y2 = round(yfloat__)

        # Option to show why Round over Int at X2 Y2

        fuzz1 = True
        fuzz1 = False
        if fuzz1:
            # eprint(f"FUZZ1 {stride_=} {angle=} {x1=} {y1=} {x2=} {y2=} {xfloat_} {yfloat_} FUZZ1")
            x2 = int(2 * xfloat_) / 2  # doublewide X
            y2 = int(yfloat_)

            # got:  cs  pu home reset pd  rt rt fd  rt fd 400
            # wanted:  cs  reset pd  setpch '.'  pu setxy ~400 ~100  pd rt fd 400 lt fd
            # surfaced by:  demos/bearings.logo

        # Draw the Line Segment to X2 Y2 from X1 Y1

        self._punch_bresenham_segment_(x1, y1=y1, x2=x2, y2=y2, xys=xys)
        # eprint(f"float {xfloat} {yfloat} {xfloat__} {yfloat__}")

        # Option to show why keep up Precise X Y Shadows in .xfloat .yfloat

        fuzz2 = True
        fuzz2 = False
        if fuzz2:  # fail test of:  cs  reset pd  fd rt 72  fd rt 72  fd rt 72  fd rt 72  fd rt 72
            # eprint(f"FUZZ2 {stride_=} {angle=} {x1=} {y1=} {x2=} {y2=} {xfloat__} {yfloat__} FUZZ2")
            xfloat__ = float(x2)
            yfloat__ = float(y2)

            # got Pentagon overshot:  cs  reset pd  fd rt 72  fd rt 72  fd rt 72  fd rt 72  fd rt 72
            # got Octogon overshot:  cs  reset pd  rep 8 [fd rt 45]
            # wanted close like:  cs  reset pd  fd rt 120  fd rt 120  fd rt 120
            # wanted close like:  cs  reset pd  rep 4 [fd rt 90]
            # surfaced by:  walking polygons

        # Catch up the Precise X Y Shadows

        if xys is None:
            self.xfloat = xfloat__
            self.yfloat = yfloat__

    def _punch_bresenham_segment_(self, x1, y1, x2, y2, xys) -> None:  # noqa C901 complex
        """Step forwards, or backwards, through (Row, Column) choices"""

        assert int(x1 * 2) == (x1 * 2), (x1,)
        assert int(y1) == y1, (y1,)
        assert int(x2 * 2) == (x2 * 2), (x2,)
        assert int(y2) == y2, (y2,)

        gt = self.glass_teletype

        # Plan to jump & punch along the Line

        x2x1 = abs(x2 - x1)  # distance
        y2y1 = abs(y2 - y1)

        sx = 1 if (x1 < x2) else -1  # steps towards X2 from X1
        sy = 1 if (y1 < y2) else -1  # steps towards Y2 from y1

        e = x2x1 - y2y1  # Bresenham's Error Measure

        # gt.notes.append(f"{x2x1=} {y2y1=} {sx=} {sy=} {e=}  # {x1=} {y1=} {x2=} {y2=}")

        # Follow the plan

        fresh_xys: list[tuple[float, float]]
        fresh_xys = list()

        wx = x = x1
        wy = y = y1
        while True:
            # gt.notes.append(f"{wx=} {wy=} {x=} {y=}")

            # Take a Jump, and maybe punch (or erase) a Trail

            if xys is None:
                self._jump_punch_rest_if_(wx, wy=-wy, x=x, y=-y)
            else:
                xy = (x, y)
                if xys:
                    assert xys[len(fresh_xys)] == xy, (xy, xys, fresh_xys, gt.notes)

                    self._jump_punch_rest_if_(wx, wy=-wy, x=x, y=-y)
                    self.xfloat = float(x)
                    self.yfloat = float(y)

                fresh_xys.append(xy)
                if len(fresh_xys) > 1:
                    break

            # Calculate the next Jump

            wx = x
            wy = y

            ee = 2 * e
            dx = ee < x2x1
            dy = ee > -y2y1

            if dy:
                e -= y2y1
                x += sx
            if dx:
                e += x2x1
                y += sy

            if (x2, y2) != (x1, y1):
                assert (x, y) != (wx, wy)
                assert dx or dy, (dx, dy, x, y, ee, x2x1, y2y1, x1, y1)

            # Quit if not moving closer to the Target

            ex = abs(x - x2) - abs(wx - x2)
            ey = abs(y - y2) - abs(wy - y2)

            if (ex == 0) and (ey == 0):  # not moving farther nor closer
                x = wx
                y = wy
                break

            if (ex > 0) or (ey > 0):  # moving away
                x = wx
                y = wy
                break

            # # Look into this Iteration of this Loop
            #
            # if False:  # jitter Sat 15/Feb
            #     if len(gt.notes) > 100:
            #         gt.notes.append("... looping indefinitely ...")
            #         break
            #
            #     # todo: <= 100 while sending many Notes can break such as:  arc 45 400

        # Slip Terminal Cursor to min Error in Doublewide X
        # todo: Terminal Cursor Slips for Breakout, for Pong, for Puck

        e_still = abs(x - x2)
        e_left = abs(x - (1 / 2) - x2)  # doublewide X
        e_right = abs(x + (1 / 2) - x2)  # doublewide X
        if e_left < e_still:
            assert e_right >= e_still, (e_still, e_left, e_right, x, x2)
            if xys is None:
                self._schars_write_("\x1b[D")
        elif e_right < e_still:
            assert e_left >= e_still, (e_still, e_left, e_right, x, x2)
            if xys is None:
                self._schars_write_("\x1b[C")

        # Pass back the look ahead, on request

        if xys is not None:
            if not xys:
                xys.extend(fresh_xys)

        # Wikipedia > https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm

        # To: Perplexity·Ai
        #
        #   When I'm drawing a line across a pixellated display,
        #   what's the most ordinary way
        #   to turn my y = a*x + b equation into a list of pixels to turn on?
        #

    def _jump_punch_rest_if_(self, wx, wy, x, y) -> None:
        """Slip into next Column or next Row, and punch, and rest, or some or none"""

        self._next_jump_punch_rest_if_()

        self._jump_if_(wx, wy=wy, x=x, y=y)
        self._punch_or_erase_if_()
        self._rest_if_()

    def _jump_if_(self, wx, wy, x, y) -> None:
        """Slip into next Column or next Row, or don't"""

        # Plan the Jump  # todo: .int or .round ?

        if wx < x:
            pn = int(2 * (x - wx))  # doublewide X
            assert pn >= 1, (pn,)
            x_ctext = f"\x1b[{pn}C"  # CSI 04/03 Cursor [Forward] Right
        elif wx > x:
            pn = int(2 * (wx - x))  # doublewide X
            x_ctext = f"\x1b[{pn}D"  # CSI 04/04 Cursor [Backward] Left
        else:
            x_ctext = ""

        if wy < y:
            pn = int(y - wy)
            assert pn >= 1, (pn,)
            y_ctext = f"\x1b[{pn}B"  # CSI 04/02 Cursor [Down] Next
        elif wy > y:
            pn = int(wy - y)
            assert pn >= 1, (pn,)
            y_ctext = f"\x1b[{pn}A"  # CSI 04/01 Cursor [Up] Previous
        else:
            y_ctext = ""

        # Do the Jump

        ctext = f"{y_ctext}{x_ctext}"
        if ctext:
            if platform.system() == "Darwin":
                ctext = "\x1b[A" + "\x1b[B" + ctext  # else macOS leaves thin 1-pixel base lines

        self._schars_write_(ctext)

    def _punch_or_erase_if_(self) -> None:
        """Punch or Erase, except don't while 🐢 PenUp"""

        warping = self.warping
        erasing = self.erasing
        penmark = self.penmark

        # Plan to write the PenMark, else to erase the Penmark while 🐢 PenErase

        width = 0
        for ch in penmark:
            eaw = unicodedata.east_asian_width(ch)
            width += 1
            if eaw in ("F", "W"):
                width += 1

        punch = (width * " ") if erasing else penmark
        backspaces = width * "\b"

        # Do the Punch or Erase, except don't while 🐢 PenUp

        if not warping:  # todo: .writelog when Controls mixed into Text
            self._schars_write_(punch)  # for ._jump_punch_rest_if_
            self._schars_write_(backspaces)

    def _rest_if_(self) -> None:
        """Do rest awhile, except don't while 🐢 HideTurtle"""

        hiding = self.hiding
        rest = self.rest

        if not hiding:
            time.sleep(rest)

    #
    # Rotate Settings, if setup for that
    #

    def _next_jump_punch_rest_if_(self) -> None:
        """Rotate the Jump/ Punch/ Rest Settings, or don't"""

        self._next_setpencolor_()

        # todo: Rotate .highlights

    def _next_setpencolor_(self) -> None:
        """Rotate the Color and Accent at SetPenColor"""

        namespace = self.namespace

        # Peek at Color and Accent

        rotations = list()

        if "setpencolor_color" in namespace.keys():
            color = namespace["setpencolor_color"]
        elif "color" in namespace.keys():
            color = namespace["color"]
        else:
            if "setpencolor_colors" in namespace.keys():
                setpencolor_colors = namespace["setpencolor_colors"]
                color = setpencolor_colors[0]
                rotations.append("setpencolor_colors")
            else:
                color = TurtlingDefaults["setpencolor_color"]

        if "setpencolor_accent" in namespace.keys():
            accent = namespace["setpencolor_accent"]
        elif "accent" in namespace.keys():
            accent = namespace["accent"]
        else:
            if "setpencolor_accents" in namespace.keys():
                setpencolor_accents = namespace["setpencolor_accents"]
                accent = setpencolor_accents[0]
                rotations.append("setpencolor_accents")
            else:
                accent = TurtlingDefaults["setpencolor_accent"]

        # Do set & rotate the Color and Accent, or don't

        if rotations:

            self.setpencolor(color, accent=accent)

            for rotation in rotations:
                values = namespace[rotation]
                pop = values.pop(0)
                values.append(pop)

    #
    # Sample the X Y Position remotely, inside the Turtle
    #

    def _x_y_position_(self) -> tuple[float, float]:
        """Sample the Turtle's X Y Position"""

        gt = self.glass_teletype
        xfloat = self.xfloat
        yfloat = self.yfloat

        # Find the Cursor & Center of Screen,
        # on a Plane of Y is Down and X is Right,
        # counted from an Upper Left (1, 1)

        (row_y, column_x) = gt.os_terminal_y_row_x_column()
        (y_count, x_count) = gt.os_terminal_y_count_x_count()

        center_x = 1 + ((x_count - 1) // 2)  # biased left when odd
        center_y = 1 + ((y_count - 1) // 2)  # biased up when odd

        # Say how far away from Center of Screen the Cursor is,
        # on a plane of Y is Up and X is Right,
        # counted from a (0, 0) in the Middle

        x1 = (column_x - center_x) / 2  # doublewide X
        y1 = -(row_y - center_y)

        xfloat_ = float(x1)
        yfloat_ = float(y1)

        # Snap the Shadow to the Cursor Row-Column, if the Cursor moved

        xf = round(2 * xfloat) / 2  # doublewide X
        yf = round(yfloat)
        # gt.notes.append(f"{x1=} {y1=} {xf=} {yf=}")

        if (x1 != xf) or (y1 != yf):

            floats = (xfloat_, yfloat_, xfloat, yfloat)
            (ix_, iy_, ix, iy) = (int(xfloat_), int(yfloat_), int(xfloat), int(yfloat))

            if floats == (ix_, iy_, ix, iy):
                note = f"Snap to X Y {ix_} {iy_} from {ix} {iy} for Y X {row_y} {column_x}"
            else:
                note = f"Snap to X Y {xfloat_} {yfloat_} from {xfloat} {yfloat} for Y X {row_y} {column_x}"

            gt.notes.append(note)  # todo: should all Glass-Terminal Notes be Exceptions?

            self.xfloat = xfloat_
            self.yfloat = yfloat_

            # todo: still snap to Int Y when X is an exact one-half Pixel away from Int X

        # Succeed

        return (xfloat_, yfloat_)

        # a la PyTurtle Position, XCor, YCor
        # a la FMSLogo Pos, XCor, YCor
        # a la UCBLogo Pos, XCor, YCor

    #
    # Draw some famous Figures
    #

    def puckland(self) -> dict:
        """Draw something like a Pac-Man™ Game Board"""

        gt = self.glass_teletype
        bt = gt.bytes_terminal

        hiding = self.hiding
        rest = self.rest
        warping = self.warping
        xscale = self.xscale
        yscale = self.yscale

        # Choose what to draw, copy-edited from https://en.wikipedia.org/wiki/Pac-Man

        git_text = """

            ┌──────────────────────────────────────────────────────┐
            │┌────────────────────────┐  ┌────────────────────────┐│
            ││()()()()()()()()()()()()│  │()()()()()()()()()()()()││
            ││()┌──────┐()┌────────┐()│  │()┌────────┐()┌──────┐()││
            ││@@│      │()│        │()│  │()│        │()│      │@@││
            ││()└──────┘()└────────┘()└──┘()└────────┘()└──────┘()││
            ││()()()()()()()()()()()()()()()()()()()()()()()()()()││
            ││()┌──────┐()┌──┐()┌──────────────┐()┌──┐()┌──────┐()││
            ││()└──────┘()│  │()└─────┐  ┌─────┘()│  │()└──────┘()││
            ││()()()()()()│  │()()()()│  │()()()()│  │()()()()()()││
            │└─────────┐()│  └─────┐  │  │  ┌─────┘  │()┌─────────┘│
            └─────────┐│()│  ┌─────┘  └──┘  └─────┐  │()│┌─────────┘
                      ││()│  │                    │  │()││
            ──────────┘│()│  │  ┌─────----─────┐  │  │()│└──────────
            ───────────┘()└──┘  │┌────----────┐│  └──┘()└───────────
                        ()      ││            ││      ()
            ───────────┐()┌──┐  │└────────────┘│  ┌──┐()┌───────────
            ──────────┐│()│  │  └──────────────┘  │  │()│┌──────────
                      ││()│  │                    │  │()││
            ┌─────────┘│()│  │  ┌──────────────┐  │  │()│└─────────┐
            │┌─────────┘()└──┘  └─────┐  ┌─────┘  └──┘()└─────────┐│
            ││()()()()()()()()()()()()│  │()()()()()()()()()()()()││
            ││()┌──────┐()┌────────┐()│  │()┌────────┐()┌──────┐()││
            ││()└───┐  │()└────────┘()└──┘()└────────┘()│  ┌───┘()││
            ││@@()()│  │()()()()()()()()()()()()()()()()│  │()()@@││
            │└───┐()│  │()┌──┐()┌──────────────┐()┌──┐()│  │()┌───┘│
            │┌───┘()└──┘()│  │()└─────┐  ┌─────┘()│  │()└──┘()└───┐│
            ││()()()()()()│  │()()()()│  │()()()()│  │()()()()()()││
            ││()┌─────────┘  └─────┐()│  │()┌─────┘  └─────────┐()││
            ││()└──────────────────┘()└──┘()└──────────────────┘()││
            ││()()()()()()()()()()()()()()()()()()()()()()()()()()││
            │└────────────────────────────────────────────────────┘│
            └──────────────────────────────────────────────────────┘

        """

        text = textwrap.dedent(git_text).strip()
        lines = text.splitlines()
        lines = ["", ""] + lines + ["", ""]

        assert len(lines) == 37, (len(lines), lines[37:])

        # Place its Upper Left Corner

        if not warping:
            self.penup()

        x1 = -(((2 * 4) + 56) / 2 / 2) / xscale
        y1 = 18 / yscale  # because (2 + 15 + 1 + 17 + 2) == 37
        self.setxy(x=x1, y=y1)  # todo: ⌃C of .setxy while not .warping
        (xa, ya) = self._x_y_position_()  # may change .xfloat .yfloat

        if not warping:
            self.pendown()  # todo: stop calling .penup .pendown .penup sometimes

        # Draw this Game Board

        Blue = "0000FF"
        Yellow = "CCCC00"
        Melon = "CC9999"

        broke = False
        for index, line in enumerate(lines):

            # Write the Line of Colored Chars

            assert len(line) <= 56, (len(line), line)
            writable = (line + (56 * " "))[:56]
            writable = (4 * " ") + writable + (4 * " ")

            # color = ""
            for ch in writable:

                # Quit on demand

                rindex = index - len(lines)
                if rindex < -1:
                    if bt.kbhit(timeout=0.000):
                        broke = True
                        break

                # Write the Colored Char, or an Uncolored Space

                if ch != " ":
                    color = Melon if (ch in "()@") else Blue
                    self.setpencolor(color, accent=8)

                self._schars_write_(ch)

            if broke:
                break

            self._schars_write_(len(writable) * "\b")
            self._schars_write_("\n")

            # if color == Melon:
            #     if not hiding:
            #         time.sleep(rest)
            #         time.sleep(rest)
            #         time.sleep(rest)

            # Slow down on demand

            assert CUU_Y == "\x1b" "[" "{}A"  # CSI 04/01 Cursor Up
            assert CUD_Y == "\x1b" "[" "{}B"  # CSI 04/02 Cursor Down

            if not hiding:
                time.sleep(rest)  # todo: a la ._rest_if_  # todo: break Sleep with KB Hit
                if platform.system() == "Darwin":
                    self._schars_write_("\x1b[A" "\x1b[B")  # else thin 1-pixel base lines

        if not broke:
            self.setpencolor(Yellow, accent=8)

        self.xfloat = xa
        self.yfloat = -ya - 1

        (xb, yb) = self._x_y_position_()  # may change .xfloat .yfloat

        # End over the left Dot beneath Home

        (xc, yc) = (xb, yb)
        if not broke:

            if not warping:
                self.penup()

            self.setxy(-1 / xscale, -8 / yscale)  # (-1, -8), because I measured it : -)
            (xc, yc) = self._x_y_position_()  # may change .xfloat .yfloat

            if not warping:
                self.pendown()

            # Show the Puck

            self.puck(0)
            gt.notes.append("Next try:  puck 1")

        # Succeed, or fall short

        d = dict(xa=xa, ya=ya, xb=xb, yb=yb, xc=xc, yc=yc, broke=broke)

        return d

        # see also 'def puck'

    def sierpiński(self, distance, count) -> dict:  # aka Sierpinski
        """Draw Triangles inside Triangles, in the way of Sierpiński 1882..1969 (also known as Sierpinksi)"""

        assert distance >= 0, (distance,)
        assert count > 0, (count,)

        t = self

        if distance <= 50:
            t.repeat(3, angle=360, distance=distance)
        else:
            for _ in range(3):

                fewer = distance / count
                t.sierpiński(fewer, count=count)

                t.forward(distance)
                t.right(120)

        return dict(sierpinski="sierpiński", d="distance", n="count")

        # todo: cyclic colors for Sierpiński's Triangle/ Sieve/ Gasket

        #
        # tested with
        #
        #   relaunch
        #   pu  setxy 170 -170  lt 90  pd
        #   sierpinski 400
        #

    #
    # Move like a Game Puck
    #

    def breakout(self, count) -> dict:
        """Move like a Breakout Game Puck"""

        count_ = int(count)
        assert count_ >= 0, (count_,)

        if count_ == 0:
            self.forward(0)
        else:
            for _ in range(count_):
                self._puck_step_(kind="Breakout")

        d = dict(xfloat=self.xfloat, yfloat=self.yfloat, bearing=self.bearing)
        self._dict_insert_compass_if_(d)
        return d

    def pong(self, count) -> dict:
        """Move like a Pong Game Puck"""

        count_ = int(count)
        assert count_ >= 0, (count_,)

        if count_ == 0:
            self.forward(0)
        else:
            for _ in range(count_):
                self._puck_step_(kind="Pong")

        d = dict(xfloat=self.xfloat, yfloat=self.yfloat, bearing=self.bearing)
        self._dict_insert_compass_if_(d)
        return d

    def puck(self, count) -> dict:
        """Move like a Pac-Man™ Game Puck"""

        gt = self.glass_teletype
        notes = gt.notes

        count_ = int(count)
        assert count_ >= 0, (count_,)

        if count_ == 0:
            self.forward(0)
        else:
            n = len(notes)
            for _ in range(count_):
                self._puck_step_(kind="Puck")

                if len(notes) > 25:
                    n += len(notes) - 25
                    notes[::] = notes[:8] + [f"... 😰 Too many notes, dropping {n} ..."]

        d = dict(xfloat=self.xfloat, yfloat=self.yfloat, bearing=self.bearing)
        self._dict_insert_compass_if_(d)
        return d

        # see also 'def puckland'

    def _puck_step_(self, kind) -> None:  # noqa C901 Too Complex
        """Move like a Breakout or Pong Game Puck"""

        assert kind in ("Breakout", "Pong", "Puck"), (kind,)

        gt = self.glass_teletype
        st = gt.str_terminal

        # Find the Place of this Turtle on Screen

        (y_count, x_count) = gt.os_terminal_y_count_x_count()
        center_x = 1 + ((x_count - 1) // 2)  # biased left when odd
        center_y = 1 + ((y_count - 1) // 2)  # biased up when odd

        (x1, y1) = self._x_y_position_()  # may change .xfloat .yfloat

        column_x1 = int(center_x + (2 * x1))
        column_x1_plus = int(column_x1 + 1)

        row_y1 = int(center_y - y1)

        xy1a = (column_x1, row_y1)
        xy1b = (column_x1_plus, row_y1)

        # Turn the Puck aside if Food on the side, while None ahead and None behind

        if kind == "Puck":
            if TunnelVision not in turtling_modes:
                self._puck_chase_(column_x1, row_y1=row_y1)

            # todo: option to Chase Food more randomly

        bearing = self.bearing  # sampled only after ._puck_chase_

        # Look ahead down the Bresenham Line

        xys: list[tuple[float, float]]
        xys = list()

        distance_float = 1e5  # todo: calculate how far from .bearing
        self._punch_bresenham_stride_(distance_float, xys=xys)  # for ._puck_step_

        assert len(xys) in (1, 2), (len(xys), xys, gt.notes)  # 1 at Bounds of Screen
        xy = xys[-1]

        if len(xys) != 1:
            assert xy != (x1, y1), (xy, x1, y1)

        # Find the Next Place of this Turtle on Screen

        (x2, y2) = xy

        column_x2 = int(center_x + (2 * x2))
        column_x2_plus = int(column_x2 + 1)
        row_y2 = int(center_y - y2)

        xy2a = (column_x2, row_y2)
        xy2b = (column_x2_plus, row_y2)

        # Look for Collision

        collision = False

        if len(xys) != 2:
            collision = True

        if xy2a not in (xy1a, xy1b):
            schar_2a_if = st.schar_read_if(row_y=row_y2, column_x=column_x2, default="")
            if kind == "Puck":
                for ch in "()@█":
                    schar_2a_if = schar_2a_if.replace(ch, " ")
            if schar_2a_if.strip():
                collision = True

        if xy2b not in (xy1a, xy1b):
            schar_2b_if = st.schar_read_if(row_y=row_y2, column_x=column_x2_plus, default="")
            if kind == "Puck":
                for ch in "()@█":
                    schar_2b_if = schar_2b_if.replace(ch, " ")
            if schar_2b_if.strip():
                collision = True

        if (column_x2 < 1) or (column_x2_plus >= x_count):
            collision = True  # todo: rare now that ._punch_bresenham_stride_ checks bounds

        if (row_y2 < 1) or (row_y2 >= y_count):
            collision = True  # todo: rare now that ._punch_bresenham_stride_ checks bounds

        # Step ahead

        if (not collision) or (kind == "Breakout"):

            self._punch_bresenham_stride_(distance_float, xys=xys)  # for ._puck_step_
            self.xfloat = x2
            self.yfloat = y2

            if collision:
                self._setbearing_(bearing + 180e0)

        else:
            assert collision, (collision,)
            assert kind in ("Pong", "Puck"), (kind,)

            xys2: list[tuple[float, float]]
            xys2 = list()

            if kind == "Pong":
                self._setbearing_(bearing + 180e0)
            else:
                assert kind == "Puck", (kind,)
                self._puck_bounce_(column_x1, row_y1=row_y1)

            self._punch_bresenham_stride_(distance_float, xys=xys2)  # for ._puck_step_
            assert len(xys2) == 2, (len(xys2), xys2, gt.notes)

            xy2 = xys2[-1]
            self._punch_bresenham_stride_(distance_float, xys=xys2)  # for ._puck_step_

            (x2, y2) = xy2  # replaces
            column_x2 = int(center_x + (2 * x2))  # replaces
            row_y2 = int(center_y - y2)  # replaces

        # Blink out after drawing over Here and There

        st.schars_write(f"\x1b[{row_y1};{column_x1}H")
        st.schars_write("  ")

        st.schars_write(f"\x1b[{row_y2};{column_x2}H")  # todo: skip if unmoving

    def _puck_chase_(self, column_x1, row_y1) -> None:
        """Turn aside if Food on the side, while Nne ahead and None behind"""

        bearing = self.bearing

        gt = self.glass_teletype
        st = gt.str_terminal

        # Do nothing if not moving along a Puckland Heading

        if bearing not in (90, 180, 270, 360):
            return

        # Look around

        (ya, xa) = (row_y1 - 1, column_x1)  # Up
        (yb, xb) = (row_y1 + 1, column_x1)  # Down
        (yc, xc) = (row_y1, column_x1 + 2)  # Right
        (yd, xd) = (row_y1, column_x1 - 2)  # Left

        sa0 = st.schar_read_if(row_y=ya, column_x=xa, default="")
        sa1 = st.schar_read_if(row_y=ya, column_x=xa + 1, default="")
        sb0 = st.schar_read_if(row_y=yb, column_x=xb, default="")
        sb1 = st.schar_read_if(row_y=yb, column_x=xb + 1, default="")
        sc0 = st.schar_read_if(row_y=yc, column_x=xc, default="")
        sc1 = st.schar_read_if(row_y=yc, column_x=xc + 1, default="")
        sd0 = st.schar_read_if(row_y=yd, column_x=xd, default="")
        sd1 = st.schar_read_if(row_y=yd, column_x=xd + 1, default="")

        sa = sa0 + sa1
        sb = sb0 + sb1
        sc = sc0 + sc1
        sd = sd0 + sd1

        # Look for Food on the side, while None ahead and None behind

        food_bearings = list()

        if bearing in (180, 360):  # Down, Up
            if sa == sb == "  ":
                if sc in ("()", "@@"):
                    food_bearings.append(90)
                if sd in ("()", "@@"):
                    food_bearings.append(270)
        else:
            assert bearing in (90, 270), (bearing,)  # Right, Left
            if sc == sd == "  ":
                if sa in ("()", "@@"):
                    food_bearings.append(360)
                if sb in ("()", "@@"):
                    food_bearings.append(180)

        # Turn aside if found

        if food_bearings:
            b = random.choice(food_bearings)
            self._setbearing_(b)

    def _puck_bounce_(self, column_x1, row_y1) -> None:
        """Choose a Heading to bounce off of a Collision"""

        bearing = self.bearing

        gt = self.glass_teletype
        st = gt.str_terminal

        siblings = [  # Look right/ down/ left/ up in a Y X Plane of Y Down Double-X Right
            (2, 0, 90),
            (0, 1, 180),
            (-2, 0, 270),
            (0, -1, 360),
        ]

        bearings = list()
        food_bearings = list()
        for sibling in siblings:  # todo: Look outside of the 4 Close Siblings
            (dx, dy, b) = sibling

            x = column_x1 + dx
            x_plus = x + 1
            y = row_y1 + dy

            schar_xya_if = st.schar_read_if(row_y=y, column_x=x, default="")
            schar_xya_if = schar_xya_if.replace("█", "")

            schar_xyb_if = st.schar_read_if(row_y=y, column_x=x_plus, default="")
            schar_xyb_if = schar_xyb_if.replace("█", "")

            schars = schar_xya_if + schar_xyb_if
            if schars in ("  ", "()", "@@"):
                bearings.append(b)
                if schars in ("()", "@@"):
                    food_bearings.append(b)

        if not bearings:
            raise NotImplementedError("Puck boxed in")

        assert bearing not in bearings, (bearing, bearings, column_x1, row_y1)

        if food_bearings:
            b = random.choice(food_bearings)
        else:
            b = random.choice(bearings)

        self._setbearing_(b)

    #
    # Define the same small set of abbreviated Method Names as "import turtle",
    # but without DocString's per Def
    #

    def back(self, distance) -> dict:  # PyTurtle t.back
        return self.backward(distance)

    def bk(self, distance) -> dict:
        return self.backward(distance)

    def down(self) -> dict:
        raise NotImplementedError("Did you mean PenDown?")

    def fd(self, distance) -> dict:
        return self.forward(distance)

    def goto(self, x, y) -> dict:
        return self.goto(x, y)

    def ht(self) -> dict:
        return self.hideturtle()

    def lt(self, angle) -> dict:
        return self.left(angle)

    def rt(self, angle) -> dict:
        return self.right(angle)

    def seth(self, angle) -> dict:
        return self.setheading(angle)

    def setpos(self, x, y) -> dict:
        return self.setxy(x, y)

    def st(self) -> dict:
        return self.showturtle()

    def up(self) -> dict:
        raise NotImplementedError("Did you mean PenUp?")


_turtles_list_: list[Turtle]
_turtles_list_ = list()


#
# Define a similar 'turtling.alef(bet, gimel)' for most Methods of Class Turtle
#
#   note: Sketchist Eval/ Exec of 'alef(bet, gimel)' runs as 'turtling.alef(bet, gimel)'
#
#   todo: solve 'turtling._breakpoint_' and 'turtling._exec_'
#


def getturtle() -> Turtle:
    """Find or form a Turtle to work with"""

    if not glass_teletypes:
        if not turtling_sketchist_find():
            turtling_run_as_sketchist()
            sys.exit()

    if not _turtles_list_:
        Turtle()

    turtle = _turtles_list_[-1]

    return turtle

    # PyTurtle GetTurtle


def arc(angle, distance) -> dict:
    return getturtle().arc(angle, distance=distance)


def back(distance) -> dict:
    return getturtle().backward(distance)


def backward(distance) -> dict:
    return getturtle().backward(distance)


def beep() -> dict:
    return getturtle().beep()


def bk(distance) -> dict:
    return getturtle().backward(distance)


def bleach() -> dict:
    return getturtle().bleach()


def breakout(count) -> dict:
    return getturtle().pong(count)


def bye() -> None:
    return getturtle().bye()


def circle(distance, angle, count) -> dict:
    return getturtle().circle(distance, angle=angle, count=count)


def clearscreen() -> dict:
    return getturtle().clearscreen()


def down() -> dict:  # NotImplementedError("Did you mean PenDown?")
    return getturtle().down()


def fd(distance) -> dict:
    return getturtle().forward(distance)


def forward(distance) -> dict:
    return getturtle().forward(distance)


def goto(x, y) -> dict:
    return getturtle().setxy(x, y)


def hideturtle() -> dict:
    return getturtle().hideturtle()


def home() -> dict:
    return getturtle().home()


def ht() -> dict:
    return getturtle().hideturtle()


def incx(distance) -> dict:
    return getturtle().incx(distance)


def incy(distance) -> dict:
    return getturtle().incy(distance)


def isdown() -> bool:
    return getturtle().isdown()


def iserasing() -> bool:
    return getturtle().iserasing()


def isvisible() -> bool:
    return getturtle().isvisible()


def label(*args) -> dict:
    return getturtle().label(*args)


def left(angle) -> dict:
    return getturtle().left(angle)


def mode(hints) -> dict:
    return getturtle()._mode_(hints)


def pendown() -> dict:
    return getturtle().pendown()


def pe() -> dict:  # NotImplementedError("Did you mean PenErase?")
    return getturtle().pe()


def penerase() -> dict:
    return getturtle().penerase()


def penup() -> dict:
    return getturtle().penup()


def pong(count) -> dict:
    return getturtle().pong(count)


def press(kstr) -> dict:
    return getturtle().press(kstr)


def puckland() -> dict:
    return getturtle().puckland()


def relaunch() -> dict:
    return getturtle().relaunch()


def restart() -> dict:
    return getturtle().restart()


def repeat(count, angle, distance) -> dict:
    return getturtle().repeat(count, angle=angle, distance=distance)


def right(angle) -> dict:
    return getturtle().right(angle)


def seth(angle) -> dict:
    return getturtle().setheading(angle)


def setheading(angle) -> dict:
    return getturtle().setheading(angle)


def sethertz(hertz) -> dict:
    return getturtle().sethertz(hertz)


def setpencolor(color, accent) -> dict:
    return getturtle().setpencolor(color, accent)


def setpenpunch(ch) -> dict:
    return getturtle().setpenpunch(ch)


def setpos(x, y) -> dict:
    return getturtle().setxy(x, y=y)


def setx(x) -> dict:
    return getturtle().setx(x)


def setxy(x, y) -> dict:
    return getturtle().setxy(x, y=y)


def setxyzoom(xscale, yscale) -> dict:
    return getturtle().setxyzoom(xscale, yscale=yscale)


def sety(y) -> dict:
    return getturtle().sety(y)


def showturtle() -> dict:
    return getturtle().showturtle()


def sierpiński(distance, count) -> dict:
    return getturtle().sierpiński(distance, count=count)


def sleep(seconds) -> dict:
    return getturtle().sleep(seconds)


def st() -> dict:
    return getturtle().showturtle()


def tada() -> dict:
    return getturtle().tada()


def teleport(x, y) -> dict:
    return getturtle().teleport(x, y=y)  # NotImplementedError - PenUp Home PenDown


def up() -> dict:
    return getturtle().up()  # NotImplementedError("Did you mean PenUp?")


def write(s) -> None:
    return getturtle().write(s)


def xcor() -> float:
    return getturtle().xcor()


def ycor() -> float:
    return getturtle().ycor()


#
# Auto-complete Turtle Logo Sourcelines to run as Python
#


class PythonSpeaker:
    """Auto-complete Turtle Logo Sourcelines to run as Python"""

    namespace: dict  # Names to take as Names, not auto-complete into Quoted Strings

    verbs: list[str]  # Verbs to call
    kws_by_verb: dict[str, list[str]]  # Kw Args to unabbreviate and find Defaults for
    localname_by_leftside: dict[str, str]  # Variables to hold Default Values

    def __init__(self) -> None:

        verbs = self.cls_to_verbs(cls=Turtle)
        kws_by_verb = self.cls_to_kws_by_verb(cls=Turtle)
        localname_by_leftside = self.to_localname_by_leftside()

        self.namespace = dict()

        self.verbs = verbs
        self.kws_by_verb = kws_by_verb
        self.localname_by_leftside = localname_by_leftside

    #
    # Auto-complete Turtle Logo Sourcelines to run as Python
    #

    def text_to_pycodes(self, text, cls) -> list[str]:
        """Auto-complete Turtle Logo Sourcelines to run as Python"""

        assert cls is Turtle, (cls,)

        verbs = self.verbs
        kws_by_verb = self.kws_by_verb

        pycodes = list()

        # Fetch the Turtle's Verbs and their Kw Args
        # todo: cache these to save ~1ms per Input Line

        # Extend Python to accept 'verb.kw =' or 'v.kw =' as meang 'verb_kw =',

        kw_text_pycodes = self.kw_text_to_pycodes_if(text)

        if kw_text_pycodes:
            pycodes.extend(kw_text_pycodes)
            return pycodes

        # Take 'breakpoint()' as meaning 't._breakpoint_()' not 'breakpoint();pass'

        if re.fullmatch(r"breakpoint *[(] *[)] *", string=text):
            pycodes.append("t._breakpoint_()")
            return pycodes

        # Forward Python unchanged

        dedent = textwrap.dedent(text)
        lede = dedent.partition("#")[0].strip().casefold()

        title = lede.title()
        if title in ("False", "None", "True"):
            pycodes.append(title)
            return pycodes

        if lede not in verbs:

            pyish = dedent
            pyish = pyish.replace("-", "~")  # accepts '-' as unary op, but refuse as binary op
            pyish = pyish.replace("+", "~")  # accepts '+' as unary op, but refuses as binary op

            try:
                ast_parse_strict(pyish)
                pycodes.append(dedent)
                return pycodes
            except SyntaxError:  # from Ast Parse Strict
                pass

            alt_pyish = pyish.replace(r"\e", r"\x1B")

            try:
                ast_parse_strict(alt_pyish)
                pycodes.append(dedent)
                return pycodes
            except SyntaxError:  # from Ast Parse Strict
                pass

            # rejects 'forward -50'
            # accepts 'forward(-50)' Python to become 'turtling.forward(-50)'

        # Split the Text into Python Texts

        assert not self.pysplit_to_pyrepr_if("", verbs=verbs)

        call_pysplits: list[str]
        call_pysplits = list()

        text_pysplits = self.py_split(text) + [""]
        trailing_pysplits = list()
        for pysplit in text_pysplits:
            if pysplit.lstrip().startswith("#"):
                trailing_pysplits.append(pysplit)
                continue

            pyrepr = self.pysplit_to_pyrepr_if(pysplit, verbs=verbs)
            if pyrepr:

                if not call_pysplits:
                    call_pysplits.append("")
                call_pysplits.append(pyrepr)

            else:

                if call_pysplits:
                    pyline = self.pysplits_to_pycode(
                        call_pysplits, verbs=verbs, kws_by_verb=kws_by_verb
                    )
                    pycode = pyline
                    pycodes.append(pycode)

                call_pysplits.clear()
                call_pysplits.append(pysplit)

        assert call_pysplits == [""], (call_pysplits,)

        if trailing_pysplits:
            pycodes[-1] += "  " + "  ".join(trailing_pysplits)

        return pycodes

    def kw_text_to_pycodes_if(self, text) -> list[str]:
        """Extend Python to accept 'verb.kw =' or 'v.kw =' as meaning 'verb_kw ='"""

        localname_by_leftside = self.localname_by_leftside

        # Drop a trailing Comment, but require something more

        head = text.partition("#")[0].strip()
        if not head:
            return list()

        # Split by Semicolon

        pycodes = list()
        for split in head.split(";"):
            if split.count("=") != 1:
                return list()

            (left_, _, right_) = split.partition("=")
            left = left_.strip()
            right = right_.strip()

            # Require Kw or Verb.Kw at left, with either or both abbreviated or not

            casefold = left.casefold()
            if casefold not in localname_by_leftside.keys():
                return list()

            localname = localname_by_leftside[casefold]

            # Require a complete Py Literal at right,
            # justifying our .partition("#") and .split(";") above

            try:
                ast_literal_eval_strict(right)
            except Exception:
                return list()

            # Form an Exec'able Python Statement

            pycode = f"{localname} = {right}"
            pycodes.append(pycode)

        # Succeed

        return pycodes

    def py_split(self, text) -> list[str]:
        """Split 1 Text into its widest parseable Py Expressions from the Left"""

        lines = text.splitlines()
        assert len(lines) <= 1, (len(lines), text)

        # Loop to add Py Splits till all Text matched

        splits = list()

        more = text
        while more:

            # Take the whole Text if '#' Comment found

            if more.lstrip().startswith("#"):
                splits.append(more)
                more = ""
                break

            # Search for the Widest Py Split from the Left

            heads = list()
            for index in range(0, len(more)):
                length = index + 1
                head = more[:length]

                # Accept Leading and Trailing Spaces into the Py Split Syntax

                strip = head.strip()  # ast.literal_eval strip's input since Oct/2021 Python 3.10

                # Split before a '#' Comment, a bit too often

                if "#" in strip:
                    break

                # Accept '-' and '+' as unary op always, but refuse as bin op when not bracketed

                pyish = strip
                if strip and (strip[:1] not in "([{"):
                    pyish = pyish.replace("-", "~")
                    pyish = pyish.replace("+", "~")

                # Accept \e as meaning \x1B . a bit too often

                pyish = pyish.replace(r"\e", r"\x1B")

                # Collect the Py Splits of Good Syntax (although only the last found matters)

                try:
                    ast_literal_eval_strict(pyish)  # todo: send to 'pysplit_to_pyrepr_if'
                    heads.append(head)
                except ValueError:
                    heads.append(head)
                except SyntaxError:  # fron Ast Literal Eval Strict
                    pass

            # Take the whole Text if no Good Syntax found

            if not heads:
                splits.append(more)
                more = ""
                break

            # Take the Widest Py Split

            head = heads[-1]
            assert head, (head, more)

            split = head
            splits.append(split)
            more = more[len(split) :]

        # Promise to drop no Characters

        assert "".join(splits) == text, (splits, text)

        return splits

        # ['Hello, World', '!']
        # ['1 (2 * 3 * 4)']

    def pysplit_to_pyrepr_if(self, py, verbs) -> str:
        """Eval the Py as a Py Literal, else return the Empty Str"""

        strip = py.strip()
        strip = strip.replace(r"\e", r"\x1B")  # replace r'\e' a bit too often

        casefold = strip.casefold()
        title = strip.title()

        if title in ("False", "None", "True"):
            return title

        try:

            ast_literal_eval_strict(strip)  # take from 'py_split'

        except ValueError:

            if casefold in verbs:
                return ""

            pyrepr = self.pyrepr(strip)  # converts to Str Lit from undefined Name
            return pyrepr

            #

        except SyntaxError:  # fron Ast Literal Eval Strict

            return ""

        return py

    def pysplits_to_pycode(self, pysplits, verbs, kws_by_verb) -> str:
        """Stitch together some Py Texts into Py Code for Exec/ Eval"""

        assert pysplits, (pysplits,)
        pystrips = list(_.strip() for _ in pysplits)

        # Guess a 't.' prefix implied by any Verb of the Class

        verb_by_grunt = self.verb_by_grunt

        strip_0 = pystrips[0]
        casefold = strip_0.casefold()

        args = list(_.replace(r"\e", r"\x1B") for _ in pystrips[1:])

        funcname = casefold
        if casefold in verbs:
            verb = casefold
            if casefold in verb_by_grunt:  # unabbreviates the Verb, if need be
                verb = verb_by_grunt[casefold]

            funcname = "t." + verb

            # Fill out the Args for any Verb of the Class, if missing

            assert verb in kws_by_verb, (verb, kws_by_verb)

            kws = kws_by_verb[verb]
            assert kws[0] == "self", (kws, verb)
            args_kws = kws[1:]
            for i in range(len(args), len(args_kws)):
                kw = args_kws[i]

                (chosen, value) = self.kw_to_chosen_arg(kw, verb=verb)
                if not chosen:
                    break

                arg = value

                pyrepr = self.pyrepr(arg)
                argpy = f"{kw}={pyrepr}" if i else pyrepr

                args.append(argpy)

        # Form the Python Code Line

        join = ", ".join(_.strip() for _ in args)
        pyline = f"{funcname}({join})"

        # Succeed

        return pyline

    def kw_to_chosen_arg(self, kw, verb) -> tuple[bool, object | None]:
        """Fetch a default Value for the Kw Arg of the Verb, else return None"""

        # Fetch Values suggested for KwArgs

        turtling_defaults = TurtlingDefaults
        namespace = self.namespace

        # Give the Win to the more explicit Sketchist Locals, else to our more implicit Defaults
        # Give the Win to the more explicit f"{verb}_{kw}", else to the more implicit f"{kw}"

        for space in (namespace, turtling_defaults):
            for k in (f"{verb}_{kw}", f"{kw}"):  # ('backward_distance', 'distance')
                if k in space.keys():
                    arg = space[k]
                    return (True, arg)

        # Else fail

        return (False, None)

    def pyrepr(self, obj) -> str:
        """Work like Repr, but better"""

        s0 = repr(obj)

        # End Float Int Lits with an '' Int mark in place of '.0' Float mark

        if isinstance(obj, float):
            f = obj
            if f == int(f):
                assert s0.endswith(".0"), (s0,)
                assert "e" not in s0, (s0,)

                # s1 = s0.removesuffix(".0") + "e0"
                s1 = s0.removesuffix(".0")

                return s1

        # Quote Bytes & Str Lits with Double Quotes a la PyPi·Org Black

        if isinstance(obj, bytes):  # todo: not much tested yet
            if s0.startswith("b'") and s0.endswith("'"):
                if ('"' not in s0) and ("'" not in s0):
                    s1 = 'b"' + s0[1:-1] + '"'
                    assert ast_literal_eval_strict(s1) == ast_literal_eval_strict(s0), (s1, s0)
                    return s1

        if isinstance(obj, str):
            if s0.startswith("'") and s0.endswith("'"):
                if ('"' not in s0) and ("'" not in s0):
                    s1 = '"' + s0[1:-1] + '"'
                    assert ast_literal_eval_strict(s1) == ast_literal_eval_strict(s0), (s1, s0)
                    return s1

        # Succeed

        return s0

        # 'One char " can show you two ticks'

    #
    # Shadow Changes to Sketchist Locals
    #

    def note_snoop(self, note) -> bool:
        """Consume the Note and return True, else return False"""

        globals_ = globals()
        locals_ = self.namespace

        # Pick out the Py to exec

        if not note.startswith("locals: "):
            return False

        py = note.removeprefix("locals: ")

        # Count Delete of Name as done already, if done already,
        # like after quitting one Client while launching the next Client

        if py.startswith("del "):
            key = py.removeprefix("del ")
            if key not in globals_.keys():
                if key not in locals_.keys():
                    print(f">>> {py}  # already done at Chat Pane")
                    return True

        # Weakly emulate the Remote Sketchist assignment of an Object with a default Repr

        (key, sep, value) = py.partition("=")
        key = key.strip()
        value = value.strip()

        if sep == "=":
            quotable = value[1:-1]
            if value == ("<" + quotable + ">"):
                # eprint("weakly emulate local exec of remote py:", py)
                locals_[key] = AngleQuotedStr(quotable)
                return True

                # <__main__.Turtle object at 0x101486a50>

        # More robustly emulate other the Remote Sketchist add/ mutate/ del at a Key

        # eprint("local exec of remote py:", py)
        exec_strict(py, globals_, locals_)  # in Class PythonSpeaker

        return True

    #
    # Declare the well-known Turtle Verbs and their Abbreviations
    #

    byo_verb_by_grunt = {
        "b": "beep",
        "clear": "clearscreen",  # Linux Clear  # macOS ⌘K
        "cls": "clearscreen",  # MsDos Cls
        "exit": "bye",
        "quit": "bye",
        "rep": "repeat",
        "sethz": "sethertz",
        "setph": "setpenhighlight",  # background vs foreground "setpencolor"
        "setpch": "setpenpunch",
        "s": "sleep",
        # "t": "tada",  # 't()' collides too close to '(t)' and 't.'
        # "w": "write",
    }

    py_verb_by_grunt = {  # for the PyTurtle people of:  import turtle
        "back": "backward",
        "bk": "backward",
        # "down": "pendown",  # ugh: PyTurtle land-grab's Down to mean Pen Down
        "fd": "forward",
        "goto": "setxy",
        "ht": "hideturtle",
        "lt": "left",
        "pd": "pendown",
        # "pe": "penerase",  # nope, too destructive
        "pu": "penup",
        "reset": "restart",  # without ClearScreen
        "rt": "right",
        "seth": "setheading",
        "setpos": "setxy",
        "setposition": "setxy",
        "sierpinski": "sierpiński",
        "st": "showturtle",
        # "up": "penup",  # ugh: PyTurtle land-grab's Up to mean Pen Up
    }

    ucb_verb_by_grunt = {  # for the UCBLogo people
        "cs": "clearscreen",
        "setpc": "setpencolor",  # foreground vs background "setpenhighlight"
    }

    verb_by_grunt = byo_verb_by_grunt | py_verb_by_grunt | ucb_verb_by_grunt

    fgrunts = sorted(  # rejects contradictory grunt definitions
        list(byo_verb_by_grunt.keys())
        + list(py_verb_by_grunt.keys())
        + list(ucb_verb_by_grunt.keys())
    )

    assert fgrunts == sorted(set(fgrunts)), (fgrunts,)

    def cls_to_verbs(self, cls) -> list[str]:
        """Say the Verb Names in a Class"""

        verb_by_grunt = self.verb_by_grunt

        funcnames = list(_ for _ in dir(cls) if not _.startswith("_"))
        grunts = list(verb_by_grunt.keys())
        grunt_verbs = list(verb_by_grunt.values())

        verbs = sorted(set(funcnames + grunts + grunt_verbs))

        for v in verbs:
            assert v == v.casefold(), (v, v.casefold())

        return verbs

    def cls_to_kws_by_verb(self, cls) -> dict[str, list[str]]:
        """List the Verbs defined by a Class and their Args"""

        kws_by_verb = dict()

        funcnames = list(_ for _ in dir(cls) if not _.startswith("_"))
        for funcname in funcnames:
            func = getattr(cls, funcname)

            kws = list()
            sig = inspect.signature(func)  # since Dec/2016 Python 3.6
            for kw, parm in sig.parameters.items():
                kws.append(kw)

            verb = funcname
            kws_by_verb[verb] = kws

            assert verb == verb.casefold(), (verb, verb.casefold())
            for kw in kws:
                assert kw == kw.casefold(), (kw, kw.casefold())

        return kws_by_verb

        # todo: .cls_to_names imprecisely incorrect outside of
        #   parm.kind in inspect.Parameter. POSITIONAL_OR_KEYWORD, KEYWORD_ONLY

    def to_localname_by_leftside(self) -> dict[str, str]:
        """List the Kw Arg Names and their abbreviations"""

        verb_by_grunt = self.verb_by_grunt

        kw_by_grunt = KwByGrunt
        turtling_defaults = TurtlingDefaults

        d: dict[str, str]
        d = dict()

        for key in turtling_defaults.keys():

            # Collect each 'Kw =' as itself

            if "_" not in key:
                assert key not in d.keys(), (key,)
                d[key] = key  # d['angle'] = 'angle'

                # Collect each 'K =' as abbreviating 'Kw ='

                for kwgrunt, kwkw in kw_by_grunt.items():
                    if kwgrunt != kwkw:
                        if kwkw == key:
                            assert kwgrunt not in d.keys(), (kwgrunt,)
                            d[kwgrunt] = key  # d['a'] = 'angle'

            # Collect each 'Func_Kw =' as itself

            else:
                assert key not in d.keys(), (key,)
                d[key] = key  # d['backward_distance'] = 'backward_distance'

                (verb, kw) = key.split("_")  # ('backward', 'distance')

                # Collect each 'Func.Kw =' as abbreviating 'Func_Kw ='

                k = f"{verb}.{kw}"
                assert k not in d.keys(), (k,)
                d[k] = key  # d['backward.distance'] = 'backward_distance'

                # Collect each 'Func.K =' as abbreviating 'Func_Kw ='

                for kwgrunt, kwkw in kw_by_grunt.items():
                    if kwgrunt != kwkw:
                        if kwkw == kw:
                            k = f"{verb}.{kwgrunt}"
                            assert k not in d.keys(), (k,)
                            d[k] = key  # d['backward.d'] = 'backward_distance'

                # Collect each 'F.Kw =' as abbreviating 'Func_Kw ='

                for vgrunt, vverb in verb_by_grunt.items():
                    assert vgrunt != vverb, (vgrunt, vverb)
                    if vverb == verb:

                        k = f"{vgrunt}.{kw}"
                        assert k not in d.keys(), (k,)
                        d[k] = key  # d['bk.distance'] = 'backward_distance'

                        # Collect each 'F.K =' as abbreviating 'Func_Kw ='

                        for kwgrunt, kwkw in kw_by_grunt.items():
                            if kwgrunt != kwkw:
                                if kwkw == kw:
                                    k = f"{vgrunt}.{kwgrunt}"
                                    assert k not in d.keys(), (k,)
                                    d[k] = key  # d['bk.d'] = 'backward_distance'

        for k in d.keys():
            assert k == k.casefold(), (k, k.casefold())

        by_leftside = d
        return by_leftside

        # {a': 'angle', 'arc_angle': 'arc_angle', ...}

    #
    # Print the results of some Auto-Completion's
    #

    @staticmethod
    def try_some() -> None:
        """Try some Auto-Completion's"""

        PythonSpeaker.try_some_logo_files()
        PythonSpeaker.try_some_md_files()

        # python3 -c 'import bin.turtling; bin.turtling.PythonSpeaker.try_some()' >a

    @staticmethod
    def try_some_logo_files() -> None:
        """Try our Auto-Completion of each Line of each Logo File found in our Demos Dir"""

        filenames = os.listdir("demos")
        for filename in filenames:
            if not filename.endswith(".logo"):
                continue

            print()
            print(filename)

            pathname = os.path.join("demos", filename)
            path = pathlib.Path(pathname)
            text = path.read_text()
            lines = text.splitlines()

            for line in lines:
                ps = PythonSpeaker()

                try:
                    pycodes = ps.text_to_pycodes(line, cls=Turtle)
                    printable = repr(pycodes)
                except Exception as exc:
                    printable = str(exc)

                print()
                # print(pathname)
                print(line)
                print(printable)

    @staticmethod
    def try_some_md_files() -> None:
        """Try our Auto-Completion of each Indented Line of our Docs Md File"""

        filename = "turtling-in-the-python-terminal.md"

        print()
        print(filename)

        pathname = os.path.join("docs", filename)
        path = pathlib.Path(pathname)
        text = path.read_text()
        lines = text.splitlines()

        for line in lines:
            if not line.startswith(4 * " "):
                continue

            ps = PythonSpeaker()

            try:
                pycodes = ps.text_to_pycodes(line, cls=Turtle)
                printable = repr(pycodes)
            except Exception as exc:
                printable = str(exc)

            print()
            # print(pathname)
            print(line)
            print(printable)


class AngleQuotedStr(str):
    """Work like a Str, but enclose Repr in '<' '>' Angle Marks"""

    def __repr__(self) -> str:
        s0 = str.__repr__(self)
        s1 = "<" + s0[1:-1] + ">"
        return s1

        # <__main__.Turtle object at 0x101486a50>


#
# Trade Texts across a pair of Named Pipes at macOS or Linux
#


class TurtlingFifoProxy:
    """Create/ find a Named Pipe and write/ read it"""

    basename: str  # 'requests'

    find: str  # '__pycache__/turtling/pid=12345/responses.mkfifo'
    pid: int  # 12345  # Process Id of the Sketchist  # not the Client
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

    def remove_mkfifo(self) -> None:
        """Remove 1 Named Pipe"""

        find = self.find  # '__pycache__/turtling/pid=92877/responses.mkfifo'
        assert find, (find,)

        os.remove(find)

        self.find = ""

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
        tail_bytes = os.read(fileno, tail_bytes_length)  # todo: chokes at large lengths
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
            if text.startswith("'Traceback (most recent call last):"):  # todo: instructions to repro
                format_exc = ast_literal_eval_strict(text)
                eprint(format_exc)
                sys.exit(1)

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
# Attach to a Turtling Sketchist
#


TurtlingWriter = TurtlingFifoProxy("requests")

TurtlingReader = TurtlingFifoProxy("responses")


def turtling_processes_stop() -> None:
    """Send Signal·SigKill to each Turtling Process"""

    # Trace & Scrape one Sh Line

    ps_shline = "ps auwx"
    print("+", ps_shline, "|grep ...")

    run = subprocess.run(shlex.split(ps_shline), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert run.returncode == 0, (run.returncode, run.stderr, ps_shline)
    assert not run.stderr, (run.returncode, run.stderr, ps_shline)

    stdout = run.stdout.decode()
    lines = stdout.splitlines()
    assert lines, (lines, ps_shline)

    # Trace & Scrape the Output Header Line

    words = lines[0].split()  # user pid %cpu %mem vsz rss tty stat start time command
    print(" ".join(words).casefold())
    assert words, (words, lines[0], ps_shline)

    pid_at = words.index("PID")  # commonly 1
    command_at = words.index("COMMAND")  # commonly 11

    # Trace & Scrape the Output Data Lines

    os_getpid = os.getpid()

    pids = list()
    for line in lines[1:]:
        words = line.split()

        if pid_at < len(words):
            pid = int(words[pid_at])
            if (command_at + 1) < len(words):
                command_0 = words[command_at]
                command_1 = words[command_at + 1]

                basename_0 = os.path.basename(command_0)
                basename_1 = os.path.basename(command_1)
                # print(basename_0, basename_1)

                if basename_0.casefold() in ("python", "python2", "python3"):
                    if basename_1 == "turtling.py":
                        if os_getpid != pid:  # todo: could Assert finding Self
                            pids.append(pid)

                            print(line)

    if not pids:
        print("... Found no Turtling·Py Processes, sent no Signals ...")

    for pid in pids:
        print(f"+ kill -{signal.SIGKILL}", pid)
        os.kill(pid, signal.SIGKILL)

    print("+")

    print("")
    print("Closing the Window Terminal Pane of each Signalled Process often helps")
    print("Or you can try to keep running them, like after telling the Shell to:  reset")


def turtling_sketchist_find() -> bool:
    """Start trading Texts with a Turtling Sketchist"""

    reader = TurtlingReader
    writer = TurtlingWriter

    if not reader.find_mkfifo_once_if(pid="*"):
        return False  # Turtling Sketchist not-found
    assert reader.pid >= 0, (reader.pid,)

    os_pid = os.getpid()
    assert reader.pid != os_pid, (reader.pid, os_pid)

    pid = reader.pid

    if not writer.find_mkfifo_once_if(pid):
        writer.create_mkfifo_once(pid)

    writer.write_text("")
    read_text_else = reader.read_text_else()
    if read_text_else != "":
        assert False, (read_text_else,)  # Turtling Sketchist texts index not synch'ed

    assert writer.index == 0, (writer.index, reader.index)
    if reader.index != writer.index:
        assert reader.index > 0, (reader.index,)
        writer.index = reader.index

    return True


#
# Run as a Sketchist, hosting Logo Python Turtles
#


def turtling_run_as_sketchist() -> None:
    "Run as a Sketchist, hosting Logo Python Turtles and return True, else return False"

    with GlassTeletype() as gt:
        ts1 = TurtlingSketchist(gt)
        ts1.sketchist_run_till()


class TurtlingSketchist:

    glass_teletype: GlassTeletype
    namespace: dict[str, object]  # with local Turtle's  # cloned by remote PythonSpeaker
    kchords: list[tuple[bytes, str]]  # Key Chords served  # KeyLogger

    def __init__(self, gt) -> None:

        namespace: dict[str, object]
        namespace = dict()

        self.glass_teletype = gt
        self.namespace = namespace
        self.kchords = list()

        turtling_sketchists.append(self)

    def sketchist_run_till(self) -> None:
        """Draw with Logo Turtles"""

        gt = self.glass_teletype
        st = gt.str_terminal
        bt = gt.bytes_terminal
        bt_fd = bt.fileno  # todo: .file_descriptor

        kchords = self.kchords

        pid = os.getpid()

        writer = TurtlingFifoProxy("responses")
        reader = TurtlingFifoProxy("requests")

        # Start up

        writer.pid_create_dir_once(pid)
        writer.create_mkfifo_once(pid)

        st.schars_print(r"Drawing until you press ⌃\ here")
        st.schars_print("")
        st.schars_print("")  # just enough more Line-Feed's so ⌃\ doesn't erase the Sh Command

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

            if not select_:
                if st.kchords:
                    select_ = [bt_fd]

            # Reply to 1 Keyboard Chord

            assert CUU_Y == "\x1b" "[" "{}A"  # CSI 04/01 Cursor Up

            if bt_fd in select_:
                kchord = st.kchord_pull(timeout=1.000)
                kchords.append(kchord)

                if kchord[-1] in ("⎋⌃\\", "⌃\\"):
                    t = Turtle()
                    try:
                        t.bye()
                    finally:
                        st.schars_print("\x1b[A", end="")
                        st.schars_print("⎋\\", end="\r\n")
                    break

                gt.keyboard_serve_one_kchord(kchord)

            # Reply to 1 Client Text

            if reader_fd in select_:
                self.reader_writer_serve(reader, writer=writer)
                continue

            # Reply to 1 Client Arrival

            if reader_fd < 0:
                if reader.find_mkfifo_once_if(pid):  # 0..10 ms
                    reader_fd = reader.fd_open_read_once()
                    assert reader_fd == reader.fileno, (reader_fd, reader.fileno)

    def reader_writer_serve(self, reader, writer) -> None:
        """Read a Python Text in, write back out the Repr of its Eval"""

        reader_fd = reader.fileno

        namespace = self.namespace
        gt = self.glass_teletype

        # Read a Python Text In, or an "" Empty Str, or fail to read

        rtext_else = reader.fd_read_text_else(reader_fd)
        if rtext_else is None:
            writer.index += 1  # as if written
            return

        rtext = rtext_else
        py = rtext

        # Eval the "" Empty Str or the Python Text,
        # but do insist on keeping >= 1 Turtles in Service

        wtext = ""
        if py:

            if "t" not in namespace.keys():
                t0 = getturtle()
                namespace["t"] = t0

            before = dict(self.namespace)  # sample before

            wvalue = self.py_exec_eval(py)

            if "t" not in namespace.keys():
                t1 = getturtle()
                namespace["t"] = t1

            t = namespace["t"]
            assert isinstance(t, Turtle), (type(t), t)

            after = dict(self.namespace)  # sample after  # 'copied is better than aliased'

            # Watch for Changes in the Terminal Cursor Position or Repr's of Locals

            t._x_y_position_()  # raises a Note if Terminal Cursor moved

            self.note_local_changes(before=before, after=after)

            if gt.notes:

                if wvalue is None:
                    wvalue = dict(notes=list(gt.notes))  # replaces
                    gt.notes.clear()

                elif isinstance(wvalue, dict):
                    assert "notes" not in wvalue.keys(), (py, wvalue.keys())
                    wvalue["notes"] = list(gt.notes)  # mutates
                    gt.notes.clear()

                    # todo: count the cost of varying the .wvalue schema only sometimes

            wtext = repr(wvalue)

        # Write back out the Repr of its Eval (except write back "" Empty Str for same)

        if writer.fileno < 0:
            writer.fd_open_write_once()
            assert writer.fileno >= 0, (writer.fileno,)

        writer.fd_write_text(writer.fileno, text=wtext)

        # trades with TurtleClient.trade_text_else

    def py_exec_eval(self, py) -> object | None:
        """Eval a Python Expression, or exec a Python Statement, or raise an Exception"""

        gt = self.glass_teletype
        bt = gt.bytes_terminal
        fileno = bt.fileno
        tcgetattr_0 = termios.tcgetattr(fileno)

        # Try Eval first

        try_exec = False

        globals_ = globals()
        locals_ = self.namespace

        try:  # todo: shrug off PyLance pretending eval/exec 'locals=' doesn't work

            value = eval_strict(py, globals_, locals_)  # in Class TurtlingSketchist

        except bdb.BdbQuit:  # from Py Eval  # of the Quit of a Pdb Breakpoint

            raise

        except NameError:  # from Py Eval

            value = traceback.format_exc()

            eline = value.splitlines()[-1]
            m = re.match(r"NameError: name '([^']*)' is not defined\b", string=eline)
            if m:
                ename = m.group(1)
                pyname = py.partition("#")[0].strip()
                if ename == pyname:
                    value = ename

        except SyntaxError:  # from Py Eval Strict

            value = None
            try_exec = True

        except Exception:

            value = traceback.format_exc()

        # Try Exec next, only if Eval raised

        if try_exec:
            assert value is None, (value,)
            try:
                exec_strict(py, globals_, locals_)  # in Class TurtlingSketchist
            except bdb.BdbQuit:  # from Py Exec  # of the Quit of a Pdb Breakpoint
                raise
            except Exception:
                value = traceback.format_exc()

        # If need be, then recover from such stress as:  help();

        tcgetattr_1 = termios.tcgetattr(fileno)
        if tcgetattr_1 != tcgetattr_0:
            note = "Snap to Tty SetRaw"  # details at 'difflib.unified_diff' of 'pprint.pformat'
            gt.notes.append(note)

            when = termios.TCSADRAIN
            tty.setraw(fileno, when)  # Tty SetRaw defaults to TcsaFlush

            # todo: tty.setraw, or termios.tcsetattr to .tcgetattr_0 or to bt.tcgetattr_else

        # Succeed

        return value

    def note_local_changes(self, before, after) -> None:
        """Note each Change in the Pairs of Key and Repr Value"""

        gt = self.glass_teletype
        notes = gt.notes

        for ak, av in after.items():
            rav = repr(av)
            if ak not in before.keys():

                note = f"locals: {ak} = {rav}"
                notes.append(note)

        for bk, bv in before.items():
            rbv = repr(bv)
            if bk not in after.keys():

                note = f"locals: del {bk}"
                notes.append(note)

            else:
                ak = bk
                av = after[ak]
                rav = repr(av)
                if rav != rbv:  # todo: contrast 'if av != bv:'

                    note = f"locals: {ak} = {rav}"
                    notes.append(note)


turtling_sketchists: list[TurtlingSketchist]
turtling_sketchists = list()


#
# Run as a Client chatting with Logo Turtles
#


def turtling_run_as_chat_client(text) -> None:
    "Run as a Client chatting with Logo Turtles and return True, else return False"

    tc1 = TurtleClient()
    try:
        tc1.client_run_till(text)
    except BrokenPipeError:
        eprint("BrokenPipeError")


class TurtleClient:
    """Chat with the Logo Turtles of 1 Turtling Sketchist"""

    ps = PythonSpeaker()

    pycodes: list[str]  # Python Calls to send to the Sketchist later
    pycodes = list()

    def breakpoint(self) -> None:
        """Chat through a Python Breakpoint, but without redefining ⌃C SigInt"""

        getsignal = signal.getsignal(signal.SIGINT)

        breakpoint()  # in Class TurtleClient
        pass

        signal.signal(signal.SIGINT, getsignal)

    def client_run_till(self, text) -> None:  # noqa C901 too complex
        """Chat with Logo Turtles"""

        ps = self.ps
        pycodes = self.pycodes

        ps1 = f"{Turtle_}\x1b[2D\x1b[2C? {Bold}"  # gCloud Shell needs the 2D 2C
        postedit = Plain

        # Till quit

        started = False

        ilines = text.splitlines()
        if text == "relaunch":
            started = True
            eprint(f"BYO Turtling·Py {__version__}")
            eprint("Chatting with you, till you say:  bye")

            (trade_else, value_else) = self.py_trade_else("t.relaunch(); pass")
            if trade_else is not None:
                eprint(trade_else)
                assert False, (trade_else, value_else)

            ilines = list()  # replace

        while True:
            while ilines:
                iline = ilines.pop(0)

                # Echo the Line by itself, prefixed by a Prompt

                sys.stdout.flush()
                eprint(ps1 + iline + postedit)
                sys.stderr.flush()

                # Quickly dismiss a flimsy Line

                dedent = textwrap.dedent(iline)
                if not self.text_has_pyweight(dedent):
                    continue

                if dedent == "import turtling":
                    started = True
                    eprint(dedent)
                    continue

                if dedent.startswith("t =") or dedent.startswith("t="):
                    started = True

                # Auto-correct till it's Python
                # Send each Python Call to the Sketchist, trace its Reply

                more_pycodes = ps.text_to_pycodes(iline, cls=Turtle)
                enough_pycodes = pycodes + more_pycodes
                pycodes.clear()

                trades = list()
                for pycode in enough_pycodes:
                    if enough_pycodes != [dedent]:  # if autocompleted
                        eprint(">>>", pycode)

                        # Py itself completes 'forward(50)' to 'turtling.forward(50)'

                    (trade_else, value_else) = self.py_trade_else(pycode)
                    if trade_else is None:
                        continue

                    trade = trade_else
                    trades.append(trade)

                    if not isinstance(value_else, dict):
                        eprint(trade)
                    else:
                        d = value_else
                        items = list(d.items())
                        py = "dict(" + ", ".join(f"{k}={ps.pyrepr(v)}" for (k, v) in items) + ")"
                        eprint(py)

                        if "next_python_codes" in d.keys():
                            next_python_codes = d["next_python_codes"]
                            pycodes.extend(next_python_codes)

                if trades:
                    eprint()

            # Prompt & Echo Lines from the Keyboard

            ilines = self.read_some_ilines(ps1)  # replace
            if not ilines:
                break

            # Insert start-up profile script if not supplied

            itext = "\n".join(ilines)
            if not started:
                if "import turtling" not in itext:
                    started = True

                    ilines[0:0] = ["import turtling", "t = turtling.Turtle()"]

    def read_some_ilines(self, ps1) -> list[str]:  # noqa C901 too complex (17
        """Prompt & Echo Lines from the Keyboard"""

        # Send the Prompt once

        sys.stdout.flush()
        eprint(ps1, end="")
        sys.stderr.flush()

        # Block to read 1 or more Input Lines

        ilines: list[str]
        ilines = list()

        while True:
            itext = ""

            # Poll for Notes from the Sketchist, while no Input available

            while True:
                timeout = 0.100
                if select.select([sys.stdin], [], [], timeout)[0]:
                    break

                # Try taking the Text as a Python Repr

                rtext_else = self.trade_text_else("t.sleep(0)")
                if rtext_else is not None:
                    rtext = rtext_else

                    try:
                        value = ast_literal_eval_strict(rtext)
                    except Exception:
                        continue

                    if isinstance(value, dict):
                        if "notes" in value.keys():
                            notes = value["notes"]
                            if notes:

                                eprint("\r" "\x1b[K", end="")
                                sys.stderr.flush()

                                for note in notes:
                                    self.sketchist_note_eval_as_client(note)

                                sys.stdout.flush()
                                eprint(ps1, end="")
                                sys.stderr.flush()

            # Block to read 1 or more Input Lines

            try:

                itext += sys.stdin.readline()
                timeout = 0.000
                while select.select([sys.stdin], [], [], timeout)[0]:
                    itext += sys.stdin.readline()

            except KeyboardInterrupt:  # ⌃C SigInt

                assert CUU_Y == "\x1b" "[" "{}A"  # CSI 04/01 Cursor Up
                assert ED_P == "\x1b" "[" "{}J"  # CSI 04/10 Erase in Display  # 2 Rows, etc

                if ilines:
                    eprint("\x1b[" f"{len(ilines)}A")
                eprint("\r" "\x1b[" "J", end="")

                eprint(ps1, end="\r\n")
                eprint("KeyboardInterrupt")
                eprint(ps1, end="")
                sys.stderr.flush()

                ilines.clear()

                continue

            if not itext:  # if ⌃D TTY EOF
                eprint("")  # completes the Line that TTY EOF echo doesn't complete

            ilines.extend(itext.splitlines())

            break

        # Clear Auto-Echo of Input, to make room to echo it when taken

        if ilines:
            eprint("\x1b[" f"{len(ilines)}A" "\x1b[" "J", end="")

        # Succeed

        return ilines

        # todo: why doesn't '.kbhit' of Chars work as well as '.select' of Lines here?

    def text_has_pyweight(self, text) -> bool:
        """Say forward to Sketchist if more than Blanks and Comments found"""

        for line in text.splitlines():
            py = line.partition("#")[0].strip()
            if py:
                return True

        return False

    def py_trade_else(self, py) -> tuple[str | None, object | None]:
        """Send Python to the Sketchist, trace its Reply"""

        # Trade with the Sketchist
        # But say EOFError if the Sketchist Quit our Conversation

        wtext = py
        rtext_else = self.trade_text_else(wtext)
        if rtext_else is None:
            if py == "t.bye()":
                sys.exit()

            ptext = "EOFError"
            return (ptext, EOFError())

        rtext = rtext_else

        # Try taking the Text as a Python Repr

        try:
            value = ast_literal_eval_strict(rtext)
        except Exception as exc:
            ptext = rtext
            return (rtext, exc)

        # Take a None as None, such as from Turtle.breakpoint

        if value is None:
            return (None, None)

        # Take a Python Traceback as Quoted Lines to Print

        if rtext.startswith("'Traceback (most recent call last):"):
            assert isinstance(value, str), (value, type(value), rtext)
            ptext = value.rstrip()
            return (ptext, "Traceback")

        # Print the Top-Level Notes on a Dict before returning the Dict

        if isinstance(value, dict):

            if "notes" in value.keys():
                clone = dict(value)

                notes = clone["notes"]
                del clone["notes"]

                for note in notes:
                    self.sketchist_note_eval_as_client(note)

                if not clone:  # lets a Dict carry Notes on behalf of None
                    return (None, None)

                ptext = repr(clone)
                return (ptext, clone)  # .clone is .value, but without its .notes

        # Else fall back to returning the Text without Eval

        ptext = rtext
        return (ptext, value)

    def sketchist_note_eval_as_client(self, note) -> None:
        """Print 1 Sketchist Note, or otherwise consume it"""

        ps = self.ps
        if not ps.note_snoop(note):
            eprint("Note:", note)

    def trade_text_else(self, wtext) -> str | None:
        """Write a Text to the Turtling Sketchist, and read back a Text or None"""

        writer = TurtlingWriter
        reader = TurtlingReader

        writer.write_text(wtext)
        rtext_else = reader.read_text_else()

        return rtext_else

        # trades with TurtlingSketchist.reader_writer_serve


#
# 🐢 My Guesses of Main Causes of loss in Net Promoter Score (NPS) # todo
#
# todo: details still churning for the resulting drawings, such as symmetric small triangles
#


#
# 🐢 Bug Fixes  # todo
#
#
# todo: Stop getting the angle wrong when drawing with the 💙 Blue-Heart in place of █
#
#
# todo: equilateral small triangles of constant Area across ↑ ← ↓ → keys:  demos/arrow-keys.logo
#
#
# todo: vs macOS Terminal thin grey lines, 1-pixel base lines
# todo: solve the thin flats left on screen behind:  reset cs pu  sethertz 10 rep 8
# also differs by Hertz:  reset cs pu  sethertz rep 8
# also:  sethertz cs pu setxy 250 250  sethertz 100 home
# also:  sethertz cs pu setxy 0 210  sethertz 100 home
# seemingly unavoidable in the not-alt-screen while printing raw??
#
#
# todo: test bounds collisions
#   reset cs pd  pu setxy 530 44 pd  lt fd 300
#       skips the column inside the right edge ?!
#
#
# todo: 🐢 SetXY slows to a crawl when given X Y much larger than Screen
# todo: ⌃C interrupt of first Client, but then still attach another, without crashing the Sketchist
#
#
# todo: more limit "setpch" to what presently works
# todo: coin a 🐢 Unlock Verb for less limited experimentation
# todo: adopt Racket Lang progressive feature flags to offer less choices at first
#
#
# todo: default Args in place of Verbose Py Tracebacks, such as:  setpencolor
# todo: when to default to cyclic choices, such as inc color, or spiral fd
#
#
# todo: poll the Sketchist while waiting for next Client Input
# todo: like quick Client reply to Sketchist Mouse/ Arrow
# todo: but sum up the Sketchist Arrow, don't only react to each individually
#
#

#
# 🐢 Turtle Demos  # todo
#
#
# todo: draw a larger Character with the smaller Character, such as the 💙 Blue-Heart
#
#
# todo: 'cs ...' to shuffle the demos and pick the next
# todo: 'import filename' or 'load filename' to fetch & run a particular file
#
# todo: early visual wows of a Twitch video stream
#
# todo: colorful spirography
# todo: marble games
# todo: tic-tac-toe, checkers, chess, & other counters-on-flat-board games
# todo: send keymaps over the wire: bind keyboard keys to turtle moves, to cycle colors
# todo: z-layers to animate a clock of hours/ minutes/ second hands
# todo: let more than 1 Turtle move onto a z-layer to keep only the latest
# todo: menus w drop shadow & keyboard & mouse - a la Borland Dos Turbo C++
# todo: vi - emacs - notepad
#
# todo: randomly go to corners till all eight connections drawn
# todo: Koch Curve at F+F--F+F in Lindenmayer System near to Serpienski Triangles
#
# todo: demo bugs fixed lately - Large Headings.logo for '.round()' vs '.trunc()'
#
# todo: one large single File of many Logo Procs, via:  def <name> [ ... ]
# todo: multiple Procs per File via TO <name>, then dents, optional END
# todo: VsCode for .logo, for .lgo, for .log, ...
#
# todo: abs square:  reset cs pd  setxy 0 100  setxy 100 100  setxy 100 0  setxy 0 0
# todo: blink xy:  sethertz 5  st s ht s  st s ht s  st s ht s  st
# todo: blink bearing:  sethertz 5  pu  st s ht s  bk 10 st s ht s  fd 20 st s ht s  bk 10 st s ht s  st
# todo: a basic smoke test of call the Grunts & Verbs as cited by Hselp
#

#
# 🐢 Turtle Shadow Engine  # todo
#
# todo: fill and clear to collision, with colors, with patterns
# todo: resize what's on Screen, and undo resize without loss
#
# todo: take end-of-Tada in from Vi
# todo: take Heading in from Vi
# todo: compose the Logo Command that sums up the Vi choices
#
# todo: do & redo & undo & clear-all-yours for Turtle work
#
# z layer "█@" for a Turtle with 8 Headings
# todo: z-layers, like one out front with more fun Cursors as Turtle
# todo: thinner X Y Pixels & Pens, especially the 0.5X 1Y of U+2584 Lower, U+2580 Upper
#
# todo: draw on a Canvas larger than the screen
# todo: checkpoint/ commit/ restore the Canvas
# todo: export the Canvas as .typescript, styled & colored
#

#
# 🐢 Turtle Graphics Engine  # todo
#
#
# todo: don't echo the ⌃\ Quit where it hits, echo it far left far below, just above Quit
#
#
# todo: Colors of Bold Italic Underline etc
#
#
# todo: plot Fonts of Characters
#
#
# todo: edge cap cursor position, wrap, bounce, whine, stop
# todo: 500x500 canvas at U Brown of UCBLogo
#
# todo: thicker X Y Pens, beyond the squarish 2X 1Y
#
# todo: write "\e[41m\e[2J" does work, fill screen w background color, do we like that?
# todo: [  write "\e[41m"  clearscreen  ] also works
# todo: more than 8 foreground colors, such as ⎋[38;5;130m orange
# todo: background colors, such as ⎋[38;5;130m orange
#
# todo: thicker X Y Pixels other than the squarish 2X 1Y
#
# steganography to put delays into Sh Script TypeScript Files after all
# todo: 🐢 After ...  # to get past next Float Seconds milestone in Screen .typescript
# work up export to gDoc for ending color without spacing to right of screen
#
# todo: resolve background foreground color collisions, such as [ write "\e[m\e[40m" ]
# todo: like [ write "\r\t\e[40m\e[32m\e[2JHello, Green-on-Black Darkmode" ]
#
# todo: collisions, gravity, friction
#
# todo: more bits of Turtle State on Screen somehow
# todo: more perceptible Screen State, such as the Chars there already
#
# todo: 3D Turtle position & trace
#

#
# 🐢 Turtle Platforms  # todo
#
# Which Backgrounds are Black out of ⎋[40m, ⎋[100m, ⎋[48;5;0m, ⎋[48;5;16m, ⎋[48;5;232m?
#
# Does ⎋[J fill with Color, or does it forget Color before fill?
#
# Does ⎋7 checkpoint Color for ⎋8 to revert?
#

#
# 🐢 Turtle Chat Engine  # todo
#
#
# todo: debug the loose gear surfaced by Tina's Giraffe
# todo: take gShell TERM=screen as reason enough to say '🐢 ?' in place of '🐢?'
# todo: take '>>> ' as request to take the rest of the line as Python without correction
# todo: automagically discover Sketchist Quit, don't wait for BrokenPipeError at next Send
# todo: harness two Turtles in parallel, such as a Darkmode & Lightmode at macOS
#
#
# todo: cut the Comments properly from:  setpc '#FFffFF'  # White = Red + Green + Blue
#
#
# todo: autocomplete 'help' and 'dir' - stop mentioning Instance Fields like '.glass_terminal'
#
#
# todo: Put the Client Breakpoint somewhere (we've taken it away from ⌃C)
# todo: Take ⌃D at either side to quit the Client and Sketchist - or not
# todo: Take ⌃C at the Sketchist to quit the Client and Sketchist - or not
#
#
# todo: 🐢 Poly(*coefficients) to plot it
#
#
# todo: accept multiple Lines of Python with dented Continuation Lines
#
#
# todo: let people say 'locals() distance angle' as one line, not three lines
#
# todo: 🐢 SetHertz Inf, in place of 🐢 SetHertz 0
# todo: publish the 'import maths' e Pi Inf -Inf NaN Tau, in with False None True
#
#
# todo: rep 3 [fd rt]
# todo: work with blocks, such as:  for _ in range(8): t.forward(100e0); t.right(45e0)
# todo: add a rep.d to choose fd.d in 🐢 rep n abbreviation of rep n [fd rep.d rt rep.angle]
#
# todo: Parentheses to eval now, Square brackets to eval later
# todo: rep 5 360 (round  100 * math.sqrt(2) / 2  1)
# todo: rep 5 [fd (round  100 * math.sqrt(2) / 2  1)  rt (360 / 5)]
# todo: rep 5 [fd (_ * 10)  rt 45]
# todo: seth (t.bearing + 90)
#
# todo: 🐢 With to bounce back after a block, such as:  with d [ d=125 fd fd ]
#
#
# todo: do still catenate successive Str Literals, such as for [ write "\e[m" "\e[2J" ]
# todo: stop over-correcting '  del left_angle' to 'de', 'l', 'left_angle'
# todo: kebab-case as an unquoted string becomes "kebab case" rather than (kebab - case)
# todo: like for unicodedata.lookup Full-Block
#
#
# todo: work with random choices
# todo: random moves, seeded random, random $n for random.randint(0, n)
# todo: cyclic moves in Color, in Pen Down, and help catalog more than 8 Colors
# todo: Pen Colors that mix with the Screen: PenPaint/ PenReverse/ PenErase
#
#
# todo: multiple Turtles
#
#
# todo: work with variables somehow - spirals, Sierpiński, etc
# todo: nonliteral (getter) arguments  # 'heading', 'position', 'isvisible', etc
# todo: reconcile more with Lisp Legacy of 'func nary' vs '(func nary and more and more)'
# todo: KwArgs for Funcs, no longer just PosArgs:  [  fd d=100  rt a=90  ]
# todo: context of Color Delay etc Space for Forward & Turn, like into irregular dance beat
#
#
# todo: local tau = for Radians in place of Degrees
# todo: 🐢 Turtling turtle.mode("Trig") for default East counting anticlockwise
# todo: ... sqrt pow ... more discoverable from:  import maths
#
#
# todo: reconcile more with Python "import turtle" Graphics on TkInter
# todo: reconcile with other Logo's
# todo: FMSLogo EllipseArc with more args at https://fmslogo.sourceforge.io/manual/command-ellipsearc.html
# todo: UCBLogo cleartext (ct) mention ⌘K
# todo: UCBLogo setcursor [x y], cursor
# todo: .rest vs Python Turtle screen.delay
# todo: .stride vs Logo SetStepSize
# todo: .rest vs Logo SetSpeed, SetVelocity, Wait
# todo: scroll and resize and reposition and iconify/ deiconify the window
#
# todo: 🐢 Pin to drop a pin (in float precision!)
# todo: 🐢 Go to get back to it
# todo: 🐢 Pin that has a name, and list them at 🐢 Go, and delete them if pinned twice in same place
#
# todo: rep n [fd fd.d rt rt.angle]
# todo: 'to $name ... end' vs 'def $name [ ... ]'
#
# todo: pinned sampling, such as list of variables to watch
# todo: mouse-click (or key chord) to unfold/ fold the values watched
#
# todo: Command Input Line History  # duped 8/Jan/2024
# todo: Command Input Word Tab-Completions
#
# todo: input Sh lines:  !uname  # !ls  # !cat - >/dev/null  # !zsh
#

#
# 🐢 Python Makeovers  # todo
#
#
# todo: correct the self-mentions in .Logo Files too, not just in .Py Files
#
#
# todo: stronger detection of old Sketchist/ Client need 'pkill' or 'kill -9'
#
#
# todo: more solve TurtleClient at:  python3 -i -c ''
#   import turtling; turtling.mode("Logo"); t = turtling.Turtle(); t.forward(100)
#
# todo: Alt Screen for Sketchist t.breakpoint()
#
# todo: declare datatypes of class Turtle args
# todo: subclass Bytes into WholeCSIBytes, CSIBytes, SomeStrBytes, SomeBytes
#

#
# 🐢 Garbled Ideas  # todo
#
# todo: Tada exists
# todo: gShell TMux ⌃B ⇧% vertical split once shifted some Rows right by 1 Column
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
#   Python Import Turtle (PyTurtle)
#   https://docs.python.org/3/library/turtle.html
#   (distinct from the unrelated PyPi·Org Pip Install PyTurtle)
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
# Amp up Import Ast
#


def ast_literal_eval_strict(text) -> object | None:
    """Work like 'ast.literal_eval' but raise the SyntaxWarning's, don't print them"""

    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        value = ast.literal_eval(text)
        return value


def ast_parse_strict(text) -> ast.AST:
    """Work like 'ast.parse' but raise the SyntaxWarning's, don't print them"""

    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        node = ast.parse(text)
        return node


#
# Amp up Import BuiltIns
#


def eprint(*args, **kwargs) -> None:
    """Print to Stderr"""

    print(*args, file=sys.stderr, **kwargs)


def eval_strict(text, globals_, locals_) -> object | None:
    """Work like 'eval' but raise the SyntaxWarning's, don't print them"""

    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        value = eval(text, globals_, locals_)
        return value


def exec_strict(text, globals_: dict, locals_: dict) -> None:
    """Work like 'exec' but raise the SyntaxWarning's, don't print them"""

    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        exec(text, globals_, locals_)


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/turtling.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
