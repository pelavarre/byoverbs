#!/usr/bin/env python3

r"""
usage: vi.py [-h] [--play LOG] DEV

view & change bytes of screen, memory, pipe, or file, in reply to keyboard chords

positional arguments:
  DEV         always only the '/dev/tty' terminal today, more variety in future

options:
  -h, --help  show this help message and exit
  --play LOG  file of bytes to write to screen

quirks:
  quits without saving input when told ⌃C ⇧Z ⇧Q, or ⌃C ⌃L : Q ! Return
  accepts ⇧Q V I Return without action or complaint
  saves input to ./dev.tty when quit by ⇧Z ⇧Z

keystrokes:
  ⌃C ⌃D ⌃G ⌃H ⌃J ⌃L Return ⌃N ⌃P ⌃\ ↑ ↓ → ←
  Space $ + - 0 1 2 3 4 5 6 7 8 9 ⇧H ⇧M ⇧L H J K L |
  ⇧C ⇧D ⇧G ⇧I ⇧O ⇧R ⇧S ⇧X ^ _ C$ CC D$ DD A I O R S X

escape sequences:
  ⎋[1m bold, ⎋[3m italic, ⎋[4m underline, ⎋[m plain
  ⎋[31m red  ⎋[32m green  ⎋[34m blue  ⎋[38;5;130m orange  ⎋[m plain
  ⎋[T scroll-up  ⎋[S scroll-down

docs:
  https://unicode.org/charts/PDF/U0000.pdf
  https://unicode.org/charts/PDF/U0080.pdf
  https://en.wikipedia.org/wiki/ANSI_escape_code
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
  https://www.ecma-international.org/publications-and-standards/standards/ecma-48
    /wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf

examples:
  vim -u /dev/null ~/.vimrc  # edit custom configuration with default configuration

  screen -L  # log bytes written to Screen into ./screenlog.0
  script -t0  # log bytes written to Mac Screen into ./typescript
  script -f  # log bytes written to Linux Screen into ./typescript before SIGUSR1

  vi.py /dev/tty  # ⌃C ⌃L ⇧Z ⇧Q to quit
  vi.py --play typescript /dev/tty  # ⌃C ⌃L ⇧Z ⇧Q to quit

  vi +$ Makefile  # open up at end of file, not start of file

  vi +':set background=light' Makefile  # choose Light Mode, when they didn't
  vi +':set background=dark' Makefile  # choose Dark Mode, when they didn't

  ls -1 |vi -  # edit from Pipe to File
  ls -1 |vi - +':set t_ti= t_te='  # edit without clearing & switching Screens
  pbpaste |vi -  # edit the Mac Os Copy/Paste Buffer
"""

# "⌃" == "\u2303" == "\N{Up Arrowhead}" for the Control Key
# "⌥" == "\u2325" == "\N{Option Key}" for the Option Key
# "⇧" == "\u21E7" == "\N{Upwards White Arrow}" for the Shift Key
# "⌘" == "\u2318" == "\N{Place of Interest Sign}" for the Command Key


# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import difflib
import os
import pathlib
import re
import select
import signal
import string
import struct
import sys
import termios
import textwrap
import time
import tty
import typing

... == time  # 'time.sleep' often unused  # type: ignore


#
# Run from the Sh Command Line
#


def main() -> None:
    """Run from the Sh Command Line"""

    parse_vi_py_args()

    stdio = sys.__stderr__
    with ViTerminal(stdio) as vt:
        vt.run_till_quit()

    # Sh Pipes nudge us to read Stdin, write Stdout, find Tty at Stderr
    # Py ShUtil Get_Terminal_Size nudges us to lose Tty when not found at Stdout


def parse_vi_py_args() -> argparse.Namespace:
    """Parse the Args from the Sh Command Line"""

    parser = byoargparse.ArgumentParser()

    dev_help = "always only the '/dev/tty' terminal today, more variety in future"
    play_help = "file of bytes to write to screen"

    parser.add_argument("dev", metavar="DEV", help=dev_help)
    parser.add_argument("--play", metavar="LOG", dest="plays", action="append", help=play_help)

    args = parser.parse_args_else()  # often prints help & exits zero
    if args.dev != "/dev/tty":
        sys.stderr.write("vi.py: error: DEV must be:  /dev/tty\n")
        sys.exit(2)

    fd = sys.stdout.fileno()
    if False and args.plays:  # play inside Terminal, and drop the inputs
        for play in args.plays:
            path = pathlib.Path(play)
            bytes_ = path.read_bytes()
            os.write(fd, bytes_)  # FIXME: consume the resulting Stdin

        assert CUP_Y_X1 == "\x1B[{}H"
        size = os.get_terminal_size()
        y = size.lines

        print()
        os.write(fd, "\x1B[{}H".format(y).encode())

        sys.exit(3)

    return args


#
# Loop Terminal Input back as Terminal Output
#


class ViTerminal:
    r"""Loop Terminal Input back as Terminal Output"""

    char_holds: list[str]
    digit_holds: list[str]

    chars_key: str | None
    chars_key_list: list[str]

    def __init__(self, stdio) -> None:
        self.ct = ChordsTerminal(stdio)

        self.bytes_key = bytearray()  # the Bytes held, till next Char
        self.char_holds = list()  # the Words of Chars held, till next Func
        self.digit_holds = list()  # the Digits held, till next Func

        self.chars_key = None  # the Name of the last Func Read
        self.chars_key_list = list()  # the Names of Func's Read
        self.func_by_chords = self.form_func_by_chords_main()  # the Func's by Name

    def __enter__(self) -> "ViTerminal":
        ct = self.ct

        ct.__enter__()

        # FIXME: DSR CPR to find Status Row

        return self

    def __exit__(self, *exc_info) -> bool | None:
        ct = self.ct
        bt = ct.bt

        assert CUP_Y_X1 == "\x1B[{}H"

        y = bt.get_terminal_rows()

        ct.write(b"\r\n")
        ct.write("\x1B[{}H".format(y).encode())

        exit_ = ct.__exit__()

        return exit_

        # ct.write(b"\x1B[J") implied by Mac Process exit  # todo: test Linux

    def pid_suspend(self) -> None:  # Vi ⌃Z F G Return  # FIXME: revive
        """Release the Screen & Keyboard, pause this Process Pid, re-acquire"""

        ct = self.ct
        bt = ct.bt

        assert CUP_Y_X1 == "\x1B[{}H"
        assert ED == b"\x1B[J"

        # Suspend as if 5 L ⌃Z
        # to make room for:  "", "zsh: suspended...", "% fg", "[1]...cont...", ""

        y = bt.get_terminal_rows()
        alt_y = max(y - 4, 1)

        ct.write(b"\r\n")
        ct.write("\x1B[{}H".format(alt_y).encode())

        ct.write(b"\x1B[J")

        # Suspend and resume this Process Pid

        pid = os.getpid()
        signal_ = signal.SIGTSTP

        ct.__exit__(*sys.exc_info())
        os.kill(pid, signal_)
        ct.__enter__()

        # todo: this hangs inside its 'os.kill' if i call Vi Py from Py or Zsh or Bash

    #
    # Launch and Quit
    #

    def run_till_quit(self) -> None:
        """Loop Terminal Input back as Terminal Output"""

        assert CUU == b"\x1B[A"

        # Read enough Chords to choose a Func, and then run that Func

        while True:
            self.read_chords_run_func()  # may raise SystemExit

    def read_chords_run_func(self, stale_chords=None) -> None:
        """Read Chords till they name a Func, then run that Func"""

        bytes_key = self.bytes_key
        ct = self.ct
        char_holds = self.char_holds
        digit_holds = self.digit_holds

        assert not digit_holds, digit_holds
        assert not char_holds, char_holds

        # Cope if the Caller didn't read some Chords ahead

        fresh_chords = stale_chords
        if stale_chords is None:
            fresh_chords = ct.read_chords()

        # Set up Funcs to say try again with more Char Chords

        while True:
            chords = fresh_chords
            if isinstance(fresh_chords, str):
                if char_holds:
                    chords = "".join(char_holds) + fresh_chords
                    char_holds.clear()

            # Run the Func of Bytes, or the closing Func of Chars

            chords_text = self.chords_format(chords)
            text = "{};{}  {}".format(ct.row, ct.column, chords_text)
            self.text_info_print(text)  # FIXME: add Func Name, add route to Quit
            # FIXME: update inside of ⇧I R etc

            func = self.find_func_by_chords(chords)
            func()  # may raise SystemExit

            if isinstance(fresh_chords, str):
                bytes_key.clear()

            # Quit after running the Funcs of Bytes, and the closing Func of Chars

            if isinstance(fresh_chords, str):
                if not digit_holds:
                    if not char_holds:
                        break

            # Else read more Chords

            fresh_chords = ct.read_chords()

    def text_info_print(self, text) -> None:
        """Print the next Log Line"""

        ct = self.ct
        bt = ct.bt
        rows = bt.get_terminal_rows()  # FIXME: Status @ ct.get_scrolling_rows() + 1

        # FIXME: trunc text with 2+3+2 Chars of "  ...  " in the middle, when needed

        #

        assert DecCursorPush == b"\x1B7"
        assert DecCsiCursorHide == b"\x1B[?25l"

        assert CUP_Y_X1 == "\x1B[{}H"
        assert EL == b"\x1B[K"

        assert XtSgrPush == b"\x1B#{"

        assert SgrOff == b"\x1B[m"

        y = rows
        text_bytes = text.encode()

        assert XtSgrPop == b"\x1B#}"
        assert DecCursorPop == b"\x1B8"
        assert DecCsiCursorShow == b"\x1B[?25h"

        #

        ct.write(b"\x1B7")  # DecCursorPush
        ct.write(b"\x1B[?25l")  # DecCsiCursorHide

        ct.write("\x1B[{}H".format(y).encode())  # CUP_Y_X1

        ct.write(b"\x1B[K")  # EL

        ct.write(b"\x1B#{")  # XtSgrPush  # emulated above BytesTerminal at Mac
        ct.write(b"\x1B[m")  # SgrOff

        ct.write(text_bytes)

        ct.write(b"\x1B#}")  # XtSgrPop  # emulated above BytesTerminal at Mac

        ct.write(b"\x1B8")  # DecCursorPop
        ct.write(b"\x1B[?25h")  # DecCsiCursorShow

        # FIXME teach ChordsTerminal to index Cursors - 0 Main, 1 Status, etc
        # FIXME but aggressively Cursor Pop Show to keep the Cursor Shown

        # FIXME think more about leaving ⇧Z ⇧Q on Screen after Quit

    def chords_format(self, chords) -> str:
        """Show the collected Bytes or the collected Words of Chars"""

        bytes_key = self.bytes_key
        digit_holds = self.digit_holds

        # Form a Python Repr to echo Bytes

        if isinstance(chords, bytes):
            bytes_key.extend(chords)
            text_bytes = bytes(bytes_key)
            text = repr(text_bytes)

        # Form Digits followed by Words of Chars, to echo those

        else:
            assert isinstance(chords, str), chords

            chars = chords
            digits = "".join(digit_holds)
            if digits:
                if chords in "0123456789":
                    chars = digits + chords
                else:
                    chars = digits + " " + chords

            text = self.chords_chars_format(chars)

        return text

    def chords_chars_format(self, chars) -> str:
        """Say how to echo Chords Chars as Status"""

        status = ""
        for ch in chars:
            code = ch.encode()
            if code in C0_BYTES:
                if code == ESC:
                    status += EscChord
                else:
                    status += Control + chr(ord(ch) ^ 0x40)
            else:
                status += ch

        return status

    def find_func_by_chords(self, chords) -> typing.Callable:
        """Find the Func most closely named by Bytes and Words of Chars"""

        func_by_chords = self.func_by_chords
        chars_key_list = self.chars_key_list

        assert ESC == b"\x1B"

        if isinstance(chords, str):
            chars_key = chords
            chars_key_list.append(chars_key)

            self.chars_key = chars_key

        func_key = chords
        if isinstance(chords, str):
            chord = chords.split()[-1]
            if chord in ("⌃H", "Delete"):
                func_key = chord

        if func_key in func_by_chords.keys():
            func = func_by_chords[func_key]
        else:
            if isinstance(chords, bytes):
                func = self.shrug  # Vi Bytes
            elif func_key.startswith("\x1B"):
                func = self.write_bytes_key  # Vi C0 Esc Sequence
            else:
                func = self.slap_back_chars  # Vi Func Not Found

        return func

    def form_func_by_chords_main(self) -> dict[str, typing.Callable]:
        """Map Words of Chars to Funcs"""

        func_by_chords = dict()

        # Map Words of Chars to Funcs

        #
        # Map Funcs at Words of ⌃ @ABCDEFGHIJKLMNO PQRSTUVWXYZ[\]^_
        #

        # ["⌃@"]
        # ["⌃A"]
        # ["⌃B"] = self.screen_retreat
        func_by_chords["⌃C"] = self.help_quit_if
        func_by_chords["⌃D"] = self.help_quit_if  # self.screen_half_advance
        # ["⌃E"]
        # ["⌃F"] = self.screen_advance
        func_by_chords["⌃G"] = self.disclose
        func_by_chords["⌃H"] = self.cancel_if  # alias of Mac Delete at PC Backspace
        # ["Tab"] = self.visit_minus_n
        func_by_chords["⌃J"] = self.row_plus_n  # alias of Vi J at Vi ⌃J
        # ["⌃K"]
        func_by_chords["⌃L"] = self.redraw
        func_by_chords["Return"] = self.line_n_plus_start
        func_by_chords["⌃N"] = self.row_plus_n  # alias of Vi J at Emacs ⌃N
        # ["⌃O"] = self.visit_plus_n
        func_by_chords["⌃P"] = self.row_minus_n  # alias of Vi K at Emacs ⌃P
        # ["⌃Q"]  # collides with:  stty ixon
        # ["⌃R"]
        # ["⌃S"]  # collides with:  stty ixoff
        # ["⌃T"]
        # ["⌃U"] = self.screen_half_retreat
        # ["⌃V"]
        # ["⌃W"]
        # ["⌃X"]
        # ["⌃Y"]
        func_by_chords["⌃Z"] = self.pid_suspend

        # ["ESC"]  # collides with 'self.write_bytes_key' C0 Esc Sequence's
        func_by_chords["⌃\\"] = self.help_quit_if
        # ["⌃]"]
        # ["⌃^"]
        # ["⌃_"]

        #
        # Map Funcs at Words of Space !"#$%&'()*+,-./ 0123456789:;<=>?
        #

        func_by_chords["Space"] = self.char_plus_n  # inverse of Vi Delete at Vi Space
        # ["!"]
        # ['"']
        # ["#"]
        func_by_chords["$"] = self.line_n_plus_end  # like Vi _, but Line End
        # ["%"]
        # ["&"]
        # ["'"]
        # ["("]
        # [")"]
        # ["*"]
        func_by_chords["+"] = self.line_n_plus_start
        # [","]
        func_by_chords["-"] = self.line_n_minus_start
        # ["."]
        # ["/"]

        func_by_chords["0"] = self.column_first_if
        func_by_chords["1"] = self.hold_digit
        func_by_chords["2"] = self.hold_digit
        func_by_chords["3"] = self.hold_digit
        func_by_chords["4"] = self.hold_digit
        func_by_chords["5"] = self.hold_digit
        func_by_chords["6"] = self.hold_digit
        func_by_chords["7"] = self.hold_digit
        func_by_chords["8"] = self.hold_digit
        func_by_chords["9"] = self.hold_digit

        # [": !"] = self.system
        # [";"]
        func_by_chords["< <"] = self.row_n_dedent
        # ["="]
        func_by_chords["> >"] = self.row_n_indent
        # ["?"]

        func_by_chords[": Q ! Return"] = self.force_quit

        #
        # Map Funcs at Words of @ABCDEFGHIJKLMNO PQRSTUVWXYZ[\]^_
        #

        # ["@"] = self.replay_x

        # ["⇧A"] = self.row_end_insert_n_till  # "A"ppend
        # ["⇧B"] = self.word_minus_n
        func_by_chords["⇧C"] = self.row_n_tail_cut_insert  # "C"change
        func_by_chords["⇧D"] = self.row_n_tail_cut_column_minus  # "D"elete
        # ["⇧E"] = self.word_end_n
        # ["⇧F"] = self.find_x_minus
        func_by_chords["⇧G"] = self.line_n_start
        func_by_chords["⇧H"] = self.row_high_n_line_start  # "H"igh
        func_by_chords["⇧I"] = self.row_start_insert_n_till  # "Insert"
        # ["⇧J"] = self.line_n_join
        # ["⇧K"]
        func_by_chords["⇧L"] = self.row_low_n_line_start  # "L"ow
        func_by_chords["⇧M"] = self.row_middle_line_start_once  # "M"iddle
        # ["⇧N"] = self.match_minus
        func_by_chords["⇧O"] = self.row_end_return_insert_n_till  # "O"pen

        func_by_chords["⇧Q V I Return"] = self.shrug

        func_by_chords["⇧R"] = self.replace_n_till  # "R"eplace
        func_by_chords["⇧S"] = self.row_n_cut_split_insert  # "S"ubstitute
        # ["⇧T"] = self.upto_x_minus
        # ["⇧U"]
        # ["⇧V"]
        # ["⇧W"] = self.word_plus_n
        func_by_chords["⇧X"] = self.column_minus_n_cut  # e"X"cise
        # ["⇧Y"] = self.row_tail_copy
        func_by_chords["⇧Z ⇧Q"] = self.force_quit

        # ["["]
        # ["\\"]
        # ["]"]
        func_by_chords["^"] = self.line_start_once  # rhymes with 're.search(r"^ *",'
        func_by_chords["_"] = self.line_n1_plus_start  # like Vi $, but Start

        #
        # Map Funcs at Words of `abcdefghijklmno pqrstuvwxyz{|}~
        #

        # ["`"]

        func_by_chords["A"] = self.column_plus_insert_n_till  # "a"ppend
        # ["B"]
        func_by_chords["C $"] = self.row_n_tail_cut_insert
        func_by_chords["C C"] = self.row_n_cut_split_insert  # "c"hange
        func_by_chords["D $"] = self.row_n_tail_cut_column_minus
        func_by_chords["D D"] = self.row_n_cut  # "d"elete
        # ["E"]
        # ["F"] = self.find_x_plus
        # ["G"]
        func_by_chords["H"] = self.column_minus_n
        func_by_chords["I"] = self.insert_n_till  # "i"nsert
        func_by_chords["J"] = self.row_plus_n
        func_by_chords["K"] = self.row_minus_n
        func_by_chords["L"] = self.column_plus_n
        # ["M"]
        # ["N"] = self.match_plus
        func_by_chords["O"] = self.row_below_return_insert_n_till  # "o"pen
        # ["P"]
        # ["Q"]
        func_by_chords["R"] = self.replace_once  # "r"eplace
        func_by_chords["S"] = self.column_plus_n_cut_insert  # "s"ubstitute
        # ["T"] = self.upto_x_plus
        # ["U"]
        # ["V"]
        func_by_chords["X"] = self.column_plus_n_cut  # e"x"cise
        # ["W"]
        # ["X"]
        # ["Y"]
        # ["Z"]

        # ["{"]
        func_by_chords["|"] = self.column_n
        # ["}"]
        # ["~"]

        #
        # Map Funcs at Words from outside the US Ascii Text Characters
        #

        func_by_chords["Delete"] = self.cancel_if

        func_by_chords["↑"] = self.row_minus_n
        func_by_chords["↓"] = self.row_plus_n
        func_by_chords["→"] = self.column_plus_n
        func_by_chords["←"] = self.column_minus_n

        func_by_chords["Fn⇧←"] = self.write_bytes_key  # ⎋[H
        func_by_chords["Fn⇧→"] = self.write_bytes_key  # ⎋[F

        #
        # Map fewer Words of Chars to Funcs
        #

        keys = list(func_by_chords.keys())
        for key in keys:
            if isinstance(key, str):
                splits = key.split()
                for index in range(len(splits)):
                    alt_key = " ".join(splits[:index])

                    if alt_key not in keys:
                        func_by_chords[alt_key] = self.hold_chars

        # Succeed

        return func_by_chords

    def shrug(self) -> None:  # Vi Bytes
        """Consciously make no reply"""

        pass

    def disclose(self) -> None:  # Vi ⌃G
        """Show some of the ChordsTerminal Cache of BytesTerminal"""

        ct = self.ct
        ct.print("  {},{}  ".format(ct.row, ct.column), end="")

        # todo: Place the Status Row outside the Scrolling Rows

    def redraw(self) -> None:  # Vi ⌃L
        """Call for Refresh of the ChordsTerminal Cache of BytesTerminal"""

        ct = self.ct
        ct.redraw()

        # no Refresh happens till after Read of CPR

    def hold_digit(self) -> None:  # Vi 1 2 3 4 5 6 7 8 9, and Vi 0 too thereafter
        """Hold Digits till Digits complete"""

        digit_holds = self.digit_holds
        chars_key = self.chars_key
        chars_key_list = self.chars_key_list

        assert chars_key, repr(chars_key)
        assert chars_key in "0123456789", repr(chars_key)
        if not digit_holds:
            assert chars_key != "0", repr(chars_key)

        digit_holds.extend(chars_key)

        assert chars_key_list[-1:] == [chars_key], (chars_key_list[-1:], chars_key)
        chars_key_list[::] = chars_key_list[:-1]

    def pull_digits_int(self, default) -> int:
        """Read then clear the Digits, and return the Int of them, else the Default"""

        digits = self.pull_digits_chars()
        int_else = int(digits) if digits else default

        return int_else

    def pull_digits_chars(self) -> str:
        """Read then clear the Digits, and return them as zero or more Chars"""

        digit_holds = self.digit_holds

        digits = "".join(digit_holds)
        digit_holds.clear()

        return digits

    def write_form_digits(self, form) -> None:
        """Write a Csi Pn F Byte Sequence with zero or more Held Digits inside"""

        ct = self.ct
        digits = self.pull_digits_chars()  # may be empty

        assert form.count("{}") == 1, repr(form)
        chars = form.format(digits)
        write = chars.encode()
        ct.write(write)

    def write_form_n(self, form, n) -> None:
        """Write a Csi Pn F Byte Sequence, but with the Digits of an Int inside"""

        ct = self.ct

        assert isinstance(n, int), repr(n)
        assert n > 0, n

        assert form.count("{}") == 1, repr(form)
        chars = form.format(n)
        write = chars.encode()
        ct.write(write)

    def write_bytes_key(self) -> None:
        """Write a Csi Pn F Byte Sequence given as Keyboard Input"""

        ct = self.ct
        bytes_key = self.bytes_key
        chars_key = self.chars_key

        assert bytes_key, (bytes_key, chars_key)
        assert chars_key, (chars_key, bytes_key)

        assert b"\x1B" == ESC
        encode = chars_key.encode()
        if encode.startswith(b"\x1B"):
            alt_encode = b"\x0F" + encode  # ⌃O
            assert bytes_key in (encode, alt_encode), (bytes_key, encode, alt_encode)

        ct.write(bytes_key)

    def hold_chars(self) -> None:  # Vi ⇧Z etc
        """Hold Char Chords till Chars complete"""

        char_holds = self.char_holds
        chars_key = self.chars_key

        assert isinstance(chars_key, str), repr(chars_key)

        char_holds.extend(chars_key)
        char_holds.extend(" ")

    def cancel_if(self) -> None:  # Vi Delete  # Vi ⌃H
        """Cancel a Word and its Digits, else go to start of N Chars before here"""

        char_holds = self.char_holds
        digit_holds = self.digit_holds

        if char_holds:
            char_holds.clear()
            digit_holds.clear()
            return

        self.char_minus_n()

    def help_quit_if(self) -> None:  # Vi ⌃C ⌃D ⌃\ etc
        """Help more if shoved more"""

        chars_key = self.chars_key
        chars_key_list = self.chars_key_list
        digit_holds = self.digit_holds

        if chars_key == "⌃C":
            digit_holds.clear()

        force = 0
        if digit_holds:
            force += 1
        if chars_key != "⌃C":
            force += 1
        if chars_key_list[-2:] == [chars_key, chars_key]:
            force += 1
        if chars_key_list[-3:] == [chars_key, chars_key, chars_key]:
            force += 1

        if force >= 2:
            self.slap_back_chars()  # repeated Vi ⌃C ⌃D ⌃\ etc
        elif force >= 1:
            self.help_quit()

    def help_quit(self) -> None:  # Vi ⌃C ⌃D ⌃\ etc
        """Help quit Vi"""

        ct = self.ct

        assert CR == b"\r"
        assert EL == b"\x1B[K"

        status = "Press ⇧Z ⇧Q to quit, or ⌃C ⇧Z ⇧Q "  # trailing Space included
        write = status.encode()

        ct.print()
        ct.write(b"\r")
        ct.write(b"\x1B[K")
        ct.write(write)

    def slap_back_once(self) -> None:
        """Slap back if starting out wrong, but don't slap back repeats"""

        chars_key = self.chars_key
        chars_key_list = self.chars_key_list
        if chars_key_list[-2:] == [chars_key, chars_key]:
            return  # inside Vi Py of ⌃H ⌃J Return ⌃N ⌃P Delete ↑ ↓ → ← $ + - H J K L _

        self.slap_back_chars()

    def slap_back_chars(self) -> None:  # i'm afraid i can't do that, Dave.
        """Say don't do that"""

        ct = self.ct
        # ct.bt.breakpoint()  # jitter Sat 10/Jun

        chars_key = self.chars_key
        assert chars_key, (chars_key,)

        chars_key_list = self.chars_key_list
        digit_holds = self.digit_holds

        chars_key_list.extend(["Bel", "⌃C"])

        assert BEL == b"\a"

        chords = chars_key + " " + "Bel"
        text = self.chords_format(chords)
        self.text_info_print(text)

        digit_holds.clear()

        ct.write(b"\a")

    def force_quit(self) -> None:  # ⇧Z ⇧Q
        """Force quit Vi, despite dirty Cache, etc"""

        ct = self.ct
        assert CR == b"\r"
        ct.write(b"\r")

        sys.exit()

    #
    # Move the Cursor relative to itself
    #

    def column_minus_n(self) -> None:  # Vi H  # Vi ←
        """Go left"""

        ct = self.ct
        column = ct.column
        if column == 1:
            self.slap_back_once()
            return

        assert CUB_N == "\x1B[{}D"
        self.write_form_digits("\x1B[{}D")

    def column_plus_n(self) -> None:  # Vi L  # Vi →
        """Go right"""

        ct = self.ct
        column = ct.column
        columns = ct.get_scrolling_columns()
        if column == columns:
            self.slap_back_once()
            return

        assert CUF_N == "\x1B[{}C"
        self.write_form_digits("\x1B[{}C")

    def row_minus_n(self) -> None:  # Vi K  # Vi ⌃P  # Vi ↑
        """Go up"""

        ct = self.ct
        row = ct.row
        if row == 1:
            self.slap_back_once()
            return

        assert CUU_N == "\x1B[{}A"
        self.write_form_digits("\x1B[{}A")

    def row_plus_n(self) -> None:  # Vi J  # Vi ⌃J  # Vi ⌃N  # Vi ↓
        """Go down"""

        ct = self.ct
        row = ct.row
        rows = ct.get_scrolling_rows()
        if row == rows:
            self.slap_back_once()
            return

        assert CUD_N == "\x1B[{}B"

        self.write_form_digits("\x1B[{}B")

    #
    # Move the Cursor relative to the Screen
    #

    def column_first_if(self) -> None:  # Vi 0 when not-preceded by 1 2 3 4 5 6 7 8 9
        """Go to First Column of Row"""

        ct = self.ct
        digit_holds = self.digit_holds

        if digit_holds:
            self.hold_digit()
            return

        assert CR == b"\r"
        ct.write(b"\r")

    def column_n(self) -> None:  # Vi |  # Vi ⇧\
        """Go from Left of Row"""

        assert CHA_X == "\x1B[{}G"

        self.write_form_digits("\x1B[{}G")

    def line_n_start(self) -> None:  # Vi ⇧G
        """Go down from Top of File, to the Nth Line Start"""

        ct = self.ct
        rows = ct.get_scrolling_rows()
        n = self.pull_digits_int(default=rows)

        assert VPA_Y == "\x1B[{}d"

        self.write_form_n("\x1B[{}d", n)
        self.line_start()

    def row_high_n_line_start(self) -> None:  # Vi ⇧H
        """Go down from Top of Screen, to the Nth Line Start"""

        assert VPA_Y == "\x1B[{}d"

        self.write_form_digits("\x1B[{}d")
        self.line_start()

    def row_middle_line_start_once(self) -> None:  # Vi ⇧M
        """Go to Middle Row of Screen, to its Line Start, only without Digits"""

        ct = self.ct
        rows = ct.get_scrolling_rows()

        if self.pull_digits_chars():
            self.slap_back_chars()  # Vi ⇧M with Digits Arg
            return

        assert VPA_Y == "\x1B[{}d"

        assert rows
        n = (rows + 1) // 2  # Row 2 of 1 2 3 4, Row 3 of 1 2 3 4 5, etc
        self.write_form_n("\x1B[{}d", n=n)
        self.line_start()

        # classic Vi ⇧M drops Digits without Beep

    def row_low_n_line_start(self) -> None:  # Vi ⇧L
        """Go up from Bottom of Screen, to the -Nth Line Start"""

        ct = self.ct
        rows = ct.get_scrolling_rows()
        n = self.pull_digits_int(default=1)

        assert VPA_Y == "\x1B[{}d"

        alt_n = (rows + 1 - n) if (n < rows) else 1
        self.write_form_n("\x1B[{}d", n=alt_n)
        self.line_start()

    #
    # Move the Cursor relative to the Chars
    #

    def char_minus_n(self) -> None:  # Vi Delete  # Vi ⌃H  # when no Chars Held
        """Go to start of N Chars before here"""

        ct = self.ct
        column = ct.column
        columns = ct.get_scrolling_columns()
        row = ct.row
        n = self.pull_digits_int(default=1)

        assert CUB_N == "\x1B[{}D"
        assert CUU_N == "\x1B[{}A"
        assert CUF_N == "\x1B[{}C"

        # Move indefinitely far left, and not at all up, if Column unknown

        if column is None:
            self.write_form_n("\x1B[{}D", n)
            return

        # Slap back moving left from first Char

        if (row, column) == (1, 1):
            self.slap_back_once()
            return

        # Plan the moves

        alt_n = n
        if row is not None:
            max_n = ((row - 1) * columns) + (column - 1)
            alt_n = min(max_n, n)

        steps = alt_n // columns
        slips = alt_n % columns

        if slips < column:
            x = column - slips
            ups = steps
            lefts = slips
            rights = 0
        else:
            x = (columns + 1) - (slips - (column - 1))
            ups = steps + 1
            lefts = 0
            rights = x - column

        # Make the moves

        slips = 0
        if lefts:
            self.write_form_n("\x1B[{}D", n=lefts)
            slips += lefts
        if ups:
            self.write_form_n("\x1B[{}A", n=ups)
            slips += ups * columns
        if rights:
            self.write_form_n("\x1B[{}C", n=rights)
            slips -= rights

        assert ct.column == x, (ct.column, x, slips, alt_n, lefts, ups, rights)
        assert slips == alt_n, (slips, alt_n, lefts, ups, rights)

    def char_plus_n(self) -> None:  # Vi Space
        """Go to end of N Chars before here"""

        ct = self.ct
        column = ct.column
        columns = ct.get_scrolling_columns()
        row = ct.row
        rows = ct.get_scrolling_rows()
        n = self.pull_digits_int(default=1)

        assert CUF_N == "\x1B[{}C"
        assert CUD_N == "\x1B[{}B"
        assert CUB_N == "\x1B[{}D"

        # Move indefinitely far right, and not at all down, if Column unknown

        if column is None:
            self.write_form_n("\x1B[{}C", n)
            return

        # Slap back moving right from last Char

        if (row, column) == (rows, columns):
            self.slap_back_once()
            return

        # Plan the moves

        alt_n = n
        if row is not None:
            max_n = ((rows - row) * columns) + (columns - column)
            alt_n = min(max_n, n)

        steps = alt_n // columns
        slips = alt_n % columns

        if slips <= (columns - column):
            x = column + slips
            downs = steps
            rights = slips
            lefts = 0
        else:
            x = (column + slips) - columns
            downs = steps + 1
            rights = 0
            lefts = column - x

        # Make the moves

        slips = 0
        if rights:
            self.write_form_n("\x1B[{}C", n=rights)
            slips += rights
        if downs:
            self.write_form_n("\x1B[{}B", n=downs)
            slips += downs * columns
        if lefts:
            self.write_form_n("\x1B[{}D", n=lefts)
            slips -= lefts

        assert ct.column == x, (ct.column, x, slips, alt_n, rights, downs, lefts)
        assert slips == alt_n, (slips, alt_n, rights, downs, lefts)

    def line_n_minus_start(self) -> None:  # Vi -
        """Go to the top-left of N Lines above here"""

        ct = self.ct
        row = ct.row
        if row == 1:
            self.slap_back_once()
            return

        assert CUU_N == "\x1B[{}A"

        self.write_form_digits("\x1B[{}A")
        self.line_start()

    def line_n1_plus_start(self) -> None:  # Vi _  # Vi ⇧-
        """Go to the bottom-left of N Lines here"""

        ct = self.ct
        row = ct.row
        rows = ct.get_scrolling_rows()
        if row == rows:
            self.slap_back_once()
            return

        n = self.pull_digits_int(default=1)

        assert CUD_N == "\x1B[{}B"

        n1 = n - 1
        if n1:
            self.write_form_n("\x1B[{}B", n=n1)
        self.line_start()

    def line_n_plus_start(self) -> None:  # Vi +  # Vi ⇧=  # Vi Return
        """Go to the bottom-left of N Lines below here"""

        ct = self.ct
        row = ct.row
        rows = ct.get_scrolling_rows()
        if row == rows:
            self.slap_back_once()
            return

        assert CUD_N == "\x1B[{}B"

        self.write_form_digits("\x1B[{}B")
        self.line_start()

    def line_start_once(self) -> None:  # Vi ^  # Vi ⇧6
        """Go to Line Start, only without Digits"""

        if self.pull_digits_chars():
            self.slap_back_chars()  # Vi ^ with Digits Arg
            return

        self.line_start()

        # classic Vi ^ drops Digits without Beep

    def line_start(self) -> None:
        """Go to Line Start"""

        if self.pull_digits_chars():
            self.slap_back_chars()  # Vi ^ with Digits Arg
            return

        ct = self.ct
        assert CR == b"\r"
        ct.write(b"\r")

        # classic Vi goes to first non-Space Char

    def line_n_plus_end(self) -> None:  # Vi $  # Vi ⇧4
        """Go to the bottom-right of N Lines here"""

        n = self.pull_digits_int(default=1)

        if n > 1:
            ct = self.ct
            row = ct.row
            rows = ct.get_scrolling_rows()
            if row == rows:
                self.slap_back_once()
                return

        assert CUD_N == "\x1B[{}B"

        n1 = n - 1
        if n1:
            self.write_form_n("\x1B[{}B", n=n1)
        self.line_end()

    def line_end(self) -> None:
        """Go to Line End"""

        ct = self.ct
        columns = ct.get_scrolling_columns()
        assert CHA_X == "\x1B[{}G"
        self.write_form_n("\x1B[{}G", n=columns)

        # classic Vi goes to last non-Space Char

    #
    # Cut Chars or Rows
    #

    def column_plus_n_cut(self) -> None:  # Vi X
        """Cut N Chars here and to the right, from this Row"""

        assert DCH_N == "\x1B[{}P"
        self.write_form_digits("\x1B[{}P")

    def column_minus_n_cut(self) -> None:  # Vi ⇧X
        """Cut N Chars to the left, from this Row"""

        ct = self.ct
        column = ct.column
        n = self.pull_digits_int(default=1)

        assert BS == b"\b"
        assert DCH_N == "\x1B[{}P"

        alt_n = n if (column is None) else min(column - 1, n)
        if alt_n:
            ct.write(alt_n * b"\b")
            self.write_form_n("\x1B[{}P", n=alt_n)

    def row_n_cut(self) -> None:  # Vi D D
        """Cut N Rows here and below, and go to Line Start"""

        assert DL_N == "\x1B[{}M"
        self.write_form_digits("\x1B[{}M")
        self.line_start()

        # classic Vi D D beeps vs Digits in the last Row

    def row_n_dedent(self) -> None:  # Vi < <
        """Dedent N Rows here"""

        ct = self.ct
        n = self.pull_digits_int(default=1)

        row = ct.row
        rows = ct.get_scrolling_rows()

        assert CR == b"\r"
        assert CUD == b"\x1B[B"
        assert DCH_N == "\x1B[{}P"
        assert CUU_N == "\x1B[{}A"

        alt_n = n
        if row is not None:
            alt_n = min(n, rows + 1 - row)

        for i in range(alt_n):
            ct.write(b"\r")
            if i:
                ct.write(b"\x1B[B")
            self.write_form_n("\x1B[{}P", n=4)

        if alt_n > 1:
            alt_n1 = alt_n - 1
            self.write_form_n("\x1B[{}A", n=alt_n1)

        self.line_start()

        # Vi < < doesn't delete non-Space Chars at Left Margin

    def row_n_tail_cut_column_minus(self) -> None:  # Vi ⇧D
        """Cut N - 1 Rows below, then Tail of Row here, then go left"""

        ct = self.ct
        self.row_n_tail_cut()
        ct.write(b"\b")

        # classic Vi ⇧D beeps vs Digits in the last Row

    def row_n_tail_cut(self) -> None:
        """Cut N - 1 Rows below, then Tail of Row here"""

        ct = self.ct
        n = self.pull_digits_int(default=1)

        assert CUD == b"\x1B[B"
        assert DL_N == "\x1B[{}M"
        assert CUU == b"\x1B[A"
        assert EL == b"\x1B[K"

        n1 = n - 1
        if n1:
            ct.write(b"\x1B[B")
            self.write_form_n("\x1B[{}M", n=n1)
            ct.write(b"\x1B[A")

        ct.write(b"\x1B[K")

    #
    # Work a bit and then Insert
    #

    def column_plus_n_cut_insert(self) -> None:  # Vi S
        """Cut N Chars here, and then insert, as if Vi X I"""

        self.column_plus_n_cut()
        self.insert_n_till()

    def row_n_indent(self) -> None:  # Vi > >
        """Indent N Rows here"""

        ct = self.ct
        n = self.pull_digits_int(default=1)

        row = ct.row
        rows = ct.get_scrolling_rows()

        alt_n = n
        if row is not None:
            alt_n = min(n, rows + 1 - row)

        assert SM_IRM == b"\x1B[4h"  # Insert without CS_6_BAR
        assert RM_IRM == b"\x1B[4l"  # Replace without CS_NONE

        assert CR == b"\r"
        assert CUD == b"\x1B[B"
        assert CUU_N == "\x1B[{}A"

        # Insert 4 Spaces

        with_inserting = ct.write_before_if(b"\x1B[4h", after=b"\x1B[4l")

        for i in range(alt_n):
            ct.write(b"\r")
            if i:
                ct.write(b"\x1B[B")
            ct.write(4 * b" ")

        if alt_n > 1:
            alt_n1 = alt_n - 1
            self.write_form_n("\x1B[{}A", n=alt_n1)
        self.line_start()

        ct.write_after_if(with_inserting)

        # Vi > > doesn't delete non-Space Chars at Right Margin
        # Vi can indent by Tabs, and by more or less than 4 Spaces

    def row_n_tail_cut_insert(self) -> None:  # Vi ⇧C
        """Cut N - 1 Rows below, then Tail of Row, and then insert, as if Vi ⇧D I"""

        self.row_n_tail_cut()
        self.insert_n_till()

        # classic Vi ⇧C beeps vs Digits in the last Row

    def row_n_cut_split_insert(self) -> None:  # Vi ⇧S  # Vi C C
        """Cut N Rows but then start a new Row here, as if D D ⇧O"""

        ct = self.ct

        assert CR == b"\r"
        assert DL_N == "\x1B[{}M"
        assert IL == b"\x1B[L"

        ct.write(b"\r")
        self.write_form_digits("\x1B[{}M")
        ct.write(b"\x1B[L")

        self.insert_n_till()

        # classic Vi ⇧S beeps vs Digits in the last Row, ditto Vi C C

    def column_plus_insert_n_till(self) -> None:  # Vi A
        """Go right and then insert, as if Vi 1 L I"""

        ct = self.ct

        if self.pull_digits_chars():
            self.slap_back_chars()  # todo: Vi A with Digits Args
            return

        assert CUF == b"\x1B[C"

        ct.write(b"\x1B[C")

        self.insert_n_till()

    def row_start_insert_n_till(self) -> None:  # Vi ⇧I
        """Go to Line Start and then insert, as if Vi ^ I"""

        self.line_start()
        self.insert_n_till()

    def row_end_return_insert_n_till(self) -> None:  # Vi ⇧O
        """Insert a new Row above this Row, as if Vi 0 I Return ↑"""

        ct = self.ct

        assert IL == b"\x1B[L"
        assert CR == b"\r"

        ct.write(b"\x1B[L")
        ct.write(b"\r")

        self.insert_n_till()

    def row_below_return_insert_n_till(self) -> None:  # Vi O
        """Insert a new Row below this Row, as if Vi $ A Return"""

        ct = self.ct

        assert CUD == b"\x1B[B"
        assert IL == b"\x1B[L"
        assert CR == b"\r"

        ct.write(b"\x1B[B")
        ct.write(b"\x1B[L")
        ct.write(b"\r")

        self.insert_n_till()

    #
    # Insert
    #

    def insert_n_till(self) -> None:  # Vi I
        """Insert Text Sequences till ⌃C, except for ⌃O and Control Sequences"""

        ct = self.ct

        if self.pull_digits_chars():
            self.slap_back_chars()  # todo: Vi I with Digits Args
            return

        assert SM_IRM == b"\x1B[4h"
        assert RM_IRM == b"\x1B[4l"

        assert CS_NONE == b"\x1B[ q"
        assert CS_6_BAR == b"\x1B[6 q"

        # Enter Insert Mode

        with_inserting = ct.write_before_if(b"\x1B[4h", after=b"\x1B[4l")
        with_cs_6_bar = ct.write_before_if(b"\x1B[6 q", after=b"\x1B[ q")

        # Insert Text Sequences till ⌃C, except for ⌃O and Control Sequences

        func_by_chords = self.form_func_by_chords_insert()
        self.run_text_sequence(func_by_chords)

        # Exit Insert Mode

        ct.write_after_if(with_cs_6_bar)
        ct.write_after_if(with_inserting)

    def insert_delete(self) -> None:
        """Go left, then Shift Left the Tail of this Row"""

        ct = self.ct
        assert DCH_N == "\x1B[{}P"
        ct.write(b"\b\x1B[P")

        # todo: Vi I Delete in first Column deletes Line-Break

    def insert_return(self) -> None:
        """Insert new Row above this Row"""

        ct = self.ct

        assert CUD == b"\x1B[B"
        assert IL == b"\x1B[L"

        ct.write(b"\x1B[B")
        ct.write(b"\x1B[L")
        self.line_start()

        # todo: Vi I Return splits Row

    def form_func_by_chords_insert(self) -> dict[str, typing.Callable]:
        """Map Single Words of Control Chars to Funcs while Inserting Text"""

        func_by_chords = dict()
        func_by_chords["Delete"] = self.insert_delete
        func_by_chords["Return"] = self.insert_return

        return func_by_chords

    #
    # Replace
    #

    def replace_once(self) -> None:  # Vi R
        """Replace once"""

        if self.pull_digits_chars():
            self.slap_back_chars()  # todo: Vi R with Digits Args
            return

        self.replace_n_till(limit=1)

        # Vi R ⌃V ⌃O and our R ⌃V ⌃O work the same
        # Vi R ⌃O works like Vi ⇧R ⌃V ⌃O ⌃C, vs our R ⌃O works like Vi ⇧R ⌃O

    def replace_n_till(self, limit=None) -> None:  # Vi ⇧R
        """Replace Text Sequences till ⌃C, except for ⌃O and Control Sequences"""

        ct = self.ct

        if self.pull_digits_chars():
            self.slap_back_chars()  # todo: Vi ⇧R with Digits Arg
            return

        assert SM_IRM == b"\x1B[4h"
        assert RM_IRM == b"\x1B[4l"

        assert CS_NONE == b"\x1B[ q"
        assert CS_4_SKID == b"\x1B[4 q"

        # Enter Replace Mode

        with_replacing = ct.write_before_if(b"\x1B[4l", after=b"\x1B[4h")
        with_cs_4_skid = ct.write_before_if(b"\x1B[4 q", after=b"\x1B[ q")

        # Replace Text Sequences till ⌃C, except for ⌃O and Control Sequences

        func_by_chords = self.form_func_by_chords_replace()
        self.run_text_sequence(func_by_chords, limit=limit)

        # Exit Replace Mode

        ct.write_after_if(with_cs_4_skid)
        ct.write_after_if(with_replacing)

    def replace_delete(self) -> None:
        """Go left to Replace with Space"""

        ct = self.ct
        ct.write(b"\b \b")

        # todo: Vi ⇧R Delete undoes Replace's but then just moves backwards

    def replace_return(self) -> None:
        """Insert new Row below this Row"""

        ct = self.ct

        assert CUD == b"\x1B[B"
        assert IL == b"\x1B[L"

        ct.write(b"\x1B[B")
        ct.write(b"\x1B[L")
        self.line_start()

        # todo: Vi ⇧R Return matches Vi I Return, but records replacements

    def form_func_by_chords_replace(self) -> dict[str, typing.Callable]:
        """Map Single Words of Control Chars to Funcs while Replacing Text"""

        func_by_chords = dict()
        func_by_chords["Delete"] = self.replace_delete
        func_by_chords["Return"] = self.replace_return

        return func_by_chords

    #
    # Insert or Replace
    #

    def run_text_sequence(self, func_by_chords, limit=None) -> None:
        """Insert/ Replace Text till ⌃C, except for ⌃O and Control Sequences"""

        bytes_key = self.bytes_key
        ct = self.ct

        text_set = set(chr(_) for _ in range(0x20, 0x7F))

        # Read Chords

        byte_holds = bytearray()
        while True:
            chords = ct.read_chords()
            if isinstance(chords, bytes):
                byte_holds.extend(chords)

                continue

            bytes_key[::] = bytes(byte_holds)
            byte_holds.clear()

            # Close up

            if chords == "⌃C":
                break

            # Delete, Return, etc

            if chords in func_by_chords.keys():
                func = func_by_chords[chords]
                func()

                continue

            # Temporarily close up by explicit request

            if chords == "⌃O":
                self.read_chords_run_func()

                continue

            # Temporarily close up by implicit request

            chars_write_set = set(bytes_key.decode())
            diff_set = chars_write_set - text_set
            if diff_set:
                self.read_chords_run_func(stale_chords=chords)

                continue

            # Write the Text Sequence to the Terminal

            ct.write(bytes_key)

            # Close up after limit

            if limit:
                break

            # todo: take ⌃V as quoting non-text chars


#
# Write Output as Mock Moves, read Input as Chars, above a BytesTerminal
#
#   "ESC", "Space", "Tab", and "Return" for b"\x1B", b" ", b"\t", and b"\r"
#   "⇧Tab", "⌥Space", b"⇧←" for b"\x1B[Z", b"\xC2\xA0", b"\x1B[1;2C"
#   "⌥3", "⇧F12" for b"\xC2\xA3", b"\x1B[\x33\x34\x7E"
#   "⌥E E" for b"\xC2\xB4"
#   etc
#


class ChordsTerminal:
    """Write Output as Mock Moves, read Input as Chars, above a BytesTerminal"""

    enter_writes: list[bytes]
    exit_writes: list[bytes]

    row: int | None
    column: int | None
    pushed_row_column: tuple[int | None, int | None]

    mocked_sgr_seqs: list[bytes]
    pushed_sgr_seqs: list[bytes]

    def __init__(self, stdio) -> None:
        self.bt = BytesTerminal(stdio)

        self.holds = bytearray()  # the Bytes taken from the BytesTerminal Keyboard
        self.peeks = bytearray()  # the Bytes already taken of an incomplete Sequence

        self.enter_writes = list()  # the Byte Sequences written at entry
        self.exit_writes = list()  # the Byte Sequences to write at exit

        self.row = None  # the Y of the Cursor, else None
        self.column = None  # the X of the Cursor, else None
        self.pushed_row_column = (None, None)  # the pushed Cursor Y X

        self.mocked_sgr_seqs = list()  # the written Sgr Contexts
        self.pushed_sgr_seqs = list()  # the pushed Sgr Contexts

    def __enter__(self) -> "ChordsTerminal":
        bt = self.bt
        enter_writes = self.enter_writes

        bt.__enter__()
        for write in enter_writes:
            self.write(write)

        self.try_me()

        return self

    def try_me(self) -> None:
        """Run a quick thorough self-test"""

        bt = self.bt

        assert bt.tcgetattr is not None  # requires called between Bt Enter & Exit

        bt.write(b"")  # tests 'os.write'
        self.kbhit(0)  # tests 'select.select'

    def __exit__(self, *exc_info) -> bool | None:
        bt = self.bt
        exit_writes = self.exit_writes

        for write in exit_writes:
            self.write(write)
        exit_ = bt.__exit__()

        self.row = None
        self.column = None

        return exit_

        # FIXME: sgr xtpush & clear at exit, restore enter - testable at G Shells

    def get_scrolling_columns(self) -> int:
        """Count Columns on Screen"""

        bt = self.bt
        columns = bt.get_terminal_columns()  # presumes no cache needed

        return columns

    def get_scrolling_rows(self) -> int:
        """Count Rows on Screen"""

        bt = self.bt
        lines = bt.get_terminal_rows()  # presumes no cache needed

        rows = lines  # todo: split off 1 or 2 Rows of Status below Scrolling

        return rows

    def write_before_if(self, before, after) -> tuple[bytes, bytes] | None:
        """Write if not written already and return the pair, else return None"""
        # FIXME: explain lots better

        enter_writes = self.enter_writes
        exit_writes = self.exit_writes

        assert SM_IRM == b"\x1B[4h"
        assert RM_IRM == b"\x1B[4l"

        assert CS_NONE == b"\x1B[ q"

        if before in enter_writes:
            return None

        #

        alt_before = before
        alt_after = after

        if before == b"\x1B[4l":  # remains in RM_IRM after exit
            if before not in exit_writes:
                alt_before = b""
                alt_after = b""

        self.write(before)  # may be in Exit Writes

        if after == b"\x1B[ q":  # exits to enclosing Enter Write
            if after in exit_writes:
                index = exit_writes.index(after)
                alt_after = enter_writes[-1 - index]

        enter_writes.append(alt_before)
        exit_writes.insert(0, alt_after)

        return (alt_before, alt_after)

    def write_after_if(self, before_after) -> None:  # FIXME: explain lots better
        """Write the After if wrote the Before"""

        enter_writes = self.enter_writes
        exit_writes = self.exit_writes

        if not before_after:
            return

        #

        (before, after) = before_after

        self.write(after)

        assert before in enter_writes, before
        assert after in exit_writes, after

        enter_writes.remove(before)
        exit_writes.remove(after)

    def redraw(self) -> None:  # Vi ⌃L
        """Call for Refresh of the ChordsTerminal Cache of BytesTerminal"""

        assert DSR_FOR_CPR == b"\x1B[6n"

        self.row = None
        self.column = None

        self.write(b"\x1B[6n")

        # no Refresh happens till after Read of CPR

    #
    # Write Output as Mock Moves above a BytesTerminal
    #

    def print(self, *args, **kwargs) -> None:
        """Print Output as Bytes and also as Mock Moves, above a BytesTerminal"""

        keys = sorted(set(kwargs.keys()) - set("end sep".split()))
        assert not keys, keys  # rejects 'file=' & 'flush=', till we test those

        assert CRLF == b"\r\n"

        sep = " "
        if ("sep" in kwargs) and (kwargs["sep"] is not None):
            sep = kwargs["sep"]

        end = "\r\n"
        if ("end" in kwargs) and (kwargs["end"] is not None):
            end = kwargs["end"]

        chars = sep.join(str(_) for _ in args) + end
        bytes_ = chars.encode()

        self.write(bytes_)

    def write(self, bytes_) -> None:
        """Write Output as Bytes and also as Mock Moves, above a BytesTerminal"""

        writes = bytearray(bytes_)
        while writes:
            seq = bytes_take_seq(writes)
            assert seq, seq  # FIXME: fails at:  ⎋ [ ⌃C
            writes[::] = writes[len(seq) :]

            self.write_seq(seq)

    def write_seq(self, seq) -> None:
        """Write one whole Byte Sequence"""

        assert seq, seq

        if seq[:1] not in C0_BYTES:
            self.write_text_seq(seq)
            return

        csi_match = re.match(rb"^" + CsiPattern + rb"$", string=seq)
        if csi_match:
            self.write_csi_seq(seq)
            return

        if seq[:1] == ESC:
            self.write_esc_seq(seq)
            return

        assert len(seq) == 1, (len(seq), seq)

        self.write_c0_seq(seq)

    def write_text_seq(self, seq) -> None:
        """Write one whole Text Sequence"""

        bt = self.bt

        assert seq, seq

        for index in range(len(seq)):
            assert seq[index:][:1] not in C0_BYTES, seq[index:][:1]

        bt.write(seq)
        self.mock_jump_by_columns(columns=len(seq))

        pass  # misreads undefined Chars  # no count, no log

    def write_c0_seq(self, seq) -> None:
        """Write one C0 Byte that isn't ESC"""

        bt = self.bt

        assert seq, seq
        assert seq != ESC, seq

        bt.write(seq)

        if seq == b"\b":
            self.mock_jump_by_columns(columns=-1)
            return

        if seq == b"\n":
            self.mock_jump_by_rows(rows=1)
            return

        if seq == b"\r":
            self.column = 1
            return

        pass  # drops undefined Mock Writes  # no count, no log

    def write_esc_seq(self, seq) -> None:
        """Write one whole Byte Sequence that starts with ESC"""

        bt = self.bt

        assert ESC == b"\x1B"
        assert CSI == b"\x1B["

        assert seq, seq
        assert seq.startswith(ESC), seq
        assert not seq.startswith(CSI)

        assert DecCursorPush == b"\x1B7"
        assert DecCursorPop == b"\x1B8"

        bt.write(seq)

        if seq == b"\x1B7":
            self.pushed_row_column = (self.row, self.column)
            return

        if seq == b"\x1B8":
            (self.row, self.column) = self.pushed_row_column
            return

        pass  # drops undefined Mock Writes  # no count, no log

    def write_csi_seq(self, seq) -> None:
        """Write one whole Byte Sequence that starts with CSI"""

        bt = self.bt
        mocked_sgr_seqs = self.mocked_sgr_seqs

        assert CSI == b"\x1B["

        assert seq, seq
        assert seq.startswith(CSI), seq

        csi_match = re.match(rb"^" + CsiPattern + rb"$", string=seq)
        assert csi_match, seq

        assert CUU == b"\x1B[A"  # implicit N=1
        assert CUD == b"\x1B[B"
        assert CUF == b"\x1B[C"
        assert CUB == b"\x1B[D"

        assert CUP_Y1_X1 == b"\x1B[H"

        assert XtSgrPush == b"\x1B#{"
        assert XtSgrPop == b"\x1B#}"

        f = bytes(seq[-1:])
        ff = bytes(seq[-2:])

        form_n_match = re.match(b"^\x1B\\[([0-9]*)[A-Za-z]$", string=seq)
        # form_y_x_match = re.match(b"^\x1B\\[([0-9]*);([0-9]*)[A-Za-z]$", string=seq)
        if form_n_match:
            assert csi_match, seq

            digits = form_n_match.group(1)  # drops leading Zeroes
            n = int(digits) if digits else 1

            bt.write(seq)
            self.mock_write_csi_n_seq(f, n=n)

            return

        if f == b"m":
            bt.write(seq)
            if seq == b"\x1B[m":
                mocked_sgr_seqs.clear()
            else:
                mocked_sgr_seqs.append(seq)
            return

        if ff == "#{":
            self.write_xt_sgr_push()
            return

        if ff == "#}":
            self.write_xt_sgr_pop()
            return

        bt.write(seq)

        pass  # drops undefined Mock Writes  # no count, no log

    def mock_write_csi_n_seq(self, f, n) -> None:
        """Write CSI Pn $F Output into a Mirror/ Shadow/ Mock Terminal"""

        assert CUU_N == "\x1B[{}A"
        assert CUD_N == "\x1B[{}B"
        assert CUF_N == "\x1B[{}C"
        assert CUB_N == "\x1B[{}D"
        assert CHA_X == "\x1B[{}G"

        assert VPA_Y == "\x1B[{}d"

        assert CUP_Y_X1 == "\x1B[{}H"

        # Take some Uppercase Ascii Letters

        if f == b"A":
            self.mock_jump_by_rows(-n)
            return

        if f == b"B":
            self.mock_jump_by_rows(n)
            return

        if f == b"C":
            self.mock_jump_by_columns(-n)
            return

        if f == b"D":
            self.mock_jump_by_columns(n)
            return

        if f == b"G":
            self.mock_jump_to_column(n)
            return

        if f == b"H":
            self.mock_jump_to_row(n)
            self.mock_jump_to_column(1)
            return

        # Take some Lowercase Ascii Letters

        if f == b"d":
            self.mock_jump_to_row(n)
            return

    def mock_jump_to_row(self, row) -> None:
        """Mock moving the Cursor up or down to a chosen Row"""

        rows = self.get_scrolling_rows()
        capped_row = min(max(row, 1), rows)

        self.row = capped_row

    def mock_jump_by_rows(self, rows) -> None:
        """Mock moving the Cursor up or down by a count of Rows"""

        row = self.row
        if row is not None:
            self.mock_jump_to_row(row + rows)

    def mock_jump_to_column(self, column) -> None:
        """Mock moving the Cursor left or right to a chosen Column"""

        columns = self.get_scrolling_columns()
        capped_column = min(max(column, 1), columns)

        self.column = capped_column

    def mock_jump_by_columns(self, columns) -> None:
        """Mock moving the Cursor left or right by a count of Columns"""

        column = self.column
        if column is not None:
            self.mock_jump_to_column(column + columns)

    def write_xt_sgr_pop(self) -> None:
        """Restore the Select Graphic Rendition (SGR) Choices"""

        mocked_sgr_seqs = self.mocked_sgr_seqs
        pushed_sgr_seqs = self.pushed_sgr_seqs

        if mocked_sgr_seqs:
            self.write(b"\x1B[m")

        assert not mocked_sgr_seqs, mocked_sgr_seqs

        self.write(b"".join(pushed_sgr_seqs))

        assert mocked_sgr_seqs == pushed_sgr_seqs, (mocked_sgr_seqs, pushed_sgr_seqs)

        # solves here, doesn't call on BytesTerminal to help, because Mac didn't

    def write_xt_sgr_push(self) -> None:
        """Save the Select Graphic Rendition (SGR) Choices"""

        mocked_sgr_seqs = self.mocked_sgr_seqs
        pushed_sgr_seqs = self.pushed_sgr_seqs

        pushed_sgr_seqs[::] = mocked_sgr_seqs

        # solves here, doesn't call on BytesTerminal to help, because Mac didn't

    #
    # Read Input as Chars in from the Keyboard of a BytesTerminal
    #

    def read_chords(self) -> bytes | str:
        """Read each Byte, and then a whole Word of Chars"""

        bt = self.bt

        holds = self.holds
        peeks = self.peeks

        # Read the last Bytes of a whole Sequence, else Bytes of the next Sequence

        index = 0
        while True:
            (seq, plus) = self.bytes_splitseq(holds)

            enough_holds = holds[: len(seq)] if seq else holds
            if enough_holds and (len(peeks) < len(enough_holds)):
                old_peeks_bytearray = enough_holds[len(peeks) :]
                old_peeks = bytes(old_peeks_bytearray)
                # to do: more carefully place bytearray/ bytes boundary above

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

            # Read more Bytes, just once

            index += 1
            assert index <= 1

            read = bt.read()
            assert read, read
            holds.extend(read)

        # like each of b'\x1B', b'[', b'A', but then "↑", in turn

    def kbhit(self, timeout) -> bool:
        """Peek a piece of a Sequence, or a whole Sequence, or zero Bytes"""

        bt = self.bt

        holds = self.holds
        peeks = self.peeks

        # Read the last Bytes of a whole Sequence, else Bytes of the next Sequence

        (seq, plus) = self.bytes_splitseq(holds)

        enough_holds = holds[: len(seq)] if seq else holds
        if enough_holds and (len(peeks) < len(enough_holds)):
            available = True
            return True

        # Read the Sequence as Chars of Words

        if seq:
            available = True
            return True

        # Wait to read more Bytes

        available = bt.kbhit(timeout=timeout)  # False | True

        return available

    def bytes_splitseq(self, bytes_) -> tuple[bytes, bytes]:
        """Split out one whole Byte Sequence, else zero Bytes"""

        seq = bytes_take_seq(bytes_)
        seq = bytes(seq)  # returns Bytes even when Bytes_ is a ByteArray

        m = re.match(rb"^" + CprPatternYX + rb"$", seq)
        if m:
            self.row = int(m.group(1))
            self.column = int(m.group(2))

        plus = bytes_[len(seq) :]
        assert (seq + plus) == bytes_, (seq, plus, bytes_)

        return (seq, plus)


#
# Name Screen Output Bytes and Keyboard Input Bytes
#


CUU_N = "\x1B[{}A"  # CSI 04/01 Cursor Up (CUU) of ΔY
CUU = b"\x1B[A"
CUD_N = "\x1B[{}B"  # CSI 04/02 Cursor Down (CUD) of ΔY
CUD = b"\x1B[B"
CUF_N = "\x1B[{}C"  # CSI 04/03 Cursor Right (CUF) of ΔX
CUF = b"\x1B[C"
CUB_N = "\x1B[{}D"  # CSI 04/04 Cursor Left (CUB) of ΔX
CUB = b"\x1B[D"

CHA_X = "\x1B[{}G"  # CSI 04/07 Cursor Character Absolute (CHA) of Y

CUP_Y_X = "\x1B[{};{}H"  # CSI 04/08 Cursor Position (CUP) of Y X
CUP_Y_X1 = "\x1B[{}H"  # CSI of X=1 at Y
CUP_Y1_X1 = b"\x1B[H"  # CSI of Y=1 X=1

ED = b"\x1B[J"  # CSI 04/10 Erase in Page (ED) of no Ps
EL = b"\x1B[K"  # CSI 04/11 Erase In Line (EL) of no Ps
IL = b"\x1B[L"  # CSI 04/12 Insert Line (IL)
DL_N = "\x1B[{}M"  # CSI 04/13 Delete Line (DL) of N
DCH_N = "\x1B[{}P"  # CSI 05/00 Delete Character (DCH) of N

VPA_Y = "\x1B[{}d"  # CSI 06/04 Line Position Absolute (VPA) of Y

SM_IRM = b"\x1B[4h"  # CSI 06/08 Set Mode (SM)  # 4 Insertion Replacement Mode (IRM)
RM_IRM = b"\x1B[4l"  # CSI 06/12 Reset Mode (RM)  # 4 Insertion Replacement Mode (IRM)

DecCsiCursorShow = b"\x1B[?25h"  # CSI 06/08 Cursor Show  # DECSET.DECTCEM
DecCsiCursorHide = b"\x1B[?25l"  # CSI 06/12 Cursor Hide  # DECRST.DECTCEM
# aka Set/Reset Mode (SM/RM)  # 25 Private Mode TwentyFive

SgrOff = b"\x1B[m"  # CSI 06/13 Select Graphic Rendition (SGR) of no Ps


# ⎋[1m ⎋[31m Bold Dim Red runs as ⎋[1m ⎋[91m Bold Bright Red in my G Shells


DSR_FOR_CPR = b"\x1B[6n"  # CSI 06/14 Device Status Report (DSR) call for CPR

CprPatternYX = rb"\x1B[\\[]([0-9]+);([0-9]+)R"
# CSI 04/18 Cursor Position Report (CPR) of Y X


CS_NONE = b"\x1B[ q"  # CSI 02/00 07/01  # Cursor of no Style
CS_4_SKID = b"\x1B[4 q"  # CSI 02/00 07/01  # Cursor Style 4 Skid
CS_6_BAR = b"\x1B[6 q"  # CSI 02/00 07/01  # Cursor Style 6 Bar
# CSI 07/00..07/14 Private or Experimental Use

XtSgrPush = b"\x1B#{"  # CSI 02/03 07/11  # XTPUSHSGR
XtSgrPop = b"\x1B#}"  # CSI 02/03 07/13  # XTPOPSGR


DecCursorPush = b"\x1B7"  # 01/11 03/07  # Cursor Save  # DECSC
DecCursorPop = b"\x1B8"  # 01/11 03/08  # Cursor Restore  # DECRC


#
# Map Keyboard Input Bytes to Keyboard Chords or Text Chars
#


Control = "\N{Up Arrowhead}"  # ⌃
Option = "\N{Option Key}"  # ⌥
Shift = "\N{Upwards White Arrow}"  # ⇧
Command = "\N{Place of Interest Sign}"  # ⌘

EscChord = "\N{Broken Circle With Northwest Arrow}"  # ⎋


C0_BYTES = b"".join(chr(_).encode() for _ in range(0, 0x20)) + b"\x7F"
# the Text Bytes of the first 0x80 (128) Bytes are the Bytes not-in the C0_BYTES

# C1_BYTES = b"".join(chr(_).encode() for _ in range(0x80, 0xA0))  # not U+00A0, U+00AD
# yea no that Code for C1_BYTES is way way wrong


def bytes_to_chords_else(bytes_, default) -> str:
    """Find the Keyboard Bytes as Str Words of Keyboard Chords, else return Default"""

    if bytes_ in CHORDS_BY_BYTES.keys():
        chords = CHORDS_BY_BYTES[bytes_]
        return chords  # '⌥E E', etc

    return default


def chords_to_bytes(chords) -> bytes:
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
CHORDS_BY_BYTES[b"\x1B"] = EscChord  # Esc ⌥Esc ⌥⇧Esc etc
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

CHORDS_BY_BYTES[b"\x1BOA"] = "↑"
CHORDS_BY_BYTES[b"\x1BOB"] = "↓"
CHORDS_BY_BYTES[b"\x1BOC"] = "→"
CHORDS_BY_BYTES[b"\x1BOD"] = "←"
# ⎋O replaces ⎋[ for ↑↓→← for b"\x1b[1?h" Application-Cursor-Keys till b"\x1b[1?l"


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

CHORDS_BY_BYTES.update(  # the Fn Delete and Fn Arrows
    {
        b"\x1B[3~": "FnDelete",
        b"\x1B[3;2~": "Fn⇧Delete",
        b"\x1B[5~": "Fn⇧↑",
        b"\x1B[6~": "Fn⇧↓",
        b"\x1B[H": "Fn⇧←",  # collides w 04/08 Cursor Position (CUP)
        b"\x1BOH": "Fn←",
        b"\x1BOF": "Fn→",
        b"\x1B[F": "Fn⇧→",  # collides w 04/06 Cursor Preceding Line (CPL)
    }
)
# usual Tty codes Fn⇧↑ as Fn⇧↑, and Fn⇧↓ as Fn⇧↓, but gives Fn Arrows to macOS Terminal
# some Tty codes Fn↑ as Fn⇧↑, and Fn↓ as Fn⇧↓, but gives Fn⇧ Arrows to macOS Terminal
# todo: find where this change is, in transcripts of macOS Vim

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


def add_us_ascii_into_chords_by_bytes() -> None:
    """Add a US Ascii Keyboard into Chars by Bytes"""

    chords_by_bytes = CHORDS_BY_BYTES

    # Decode the Control Chords not yet decoded

    assert Control == "\N{Up Arrowhead}"  # ⌃

    for ord_ in C0_BYTES:
        char = chr(ord_)
        bytes_ = char.encode()
        if bytes_ in chords_by_bytes.keys():
            assert bytes_ in b"\x00\x09\x0D\x1B\x7F", bytes_
        else:
            chords_by_bytes[bytes_] = Control + chr(ord_ ^ 0x40)

    # Decode the Shift'ed and un-Shift'ed US Ascii Letters

    assert Shift == "\N{Upwards White Arrow}"  # ⇧

    for char in string.ascii_uppercase:  # "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        bytes_ = char.encode()
        assert bytes_ not in chords_by_bytes.keys(), bytes_
        chords_by_bytes[bytes_] = Shift + char

    for char in string.ascii_lowercase:  # "abcdefghijklmnopqrstuvwxyz"
        bytes_ = char.encode()
        assert bytes_ not in chords_by_bytes.keys(), bytes_
        chords_by_bytes[bytes_] = char.upper()

    # Decode the US Ascii Bytes not yet decoded

    for ord_ in range(0x80):
        char = chr(ord_)
        bytes_ = char.encode()
        if bytes_ in chords_by_bytes.keys():
            pass
        elif bytes_ in string.digits.encode():  # b"0123456789"
            chords_by_bytes[bytes_] = char
        else:
            assert bytes_ in rb""" !"#$%&'()*+,-./ :;<=>?  @ [\]^_ ` {|}~ """, bytes_
            chords_by_bytes[bytes_] = char


add_us_ascii_into_chords_by_bytes()


#
# Define whole & partial Control Byte and Text Byte Sequences
#


BEL = b"\a"  # 00/07 Bell
BS = b"\b"  # 00/08 Backspace
CR = b"\r"  # 00/13 Carriage Return
CRLF = b"\r\n"  # 00/13 00/10 Carriage Return + Line Feed
LF = b"\n"  # 00/10 Line Feed
ESC = b"\x1B"  # 01/11 Escape

CSI = b"\x1B["  # 01/11 05/11 Control Sequence Introducer  # till rb"[\x30-\x7E]"
OSC = b"\x1B]"  # 01/11 05/13 Operating System Command  # till BEL, CR, Esc \ ST, etc
SS3 = b"\x1BO"  # 01/11 04/15 Single Shift Three


CsiStartPattern = b"\x1B\\[" rb"[\x30-\x3F]*[\x20-\x2F]*"  # leading Zeroes allowed
CsiEndPattern = rb"[\x40-\x7E]"
CsiPattern = CsiStartPattern + CsiEndPattern
# Csi Patterns define many Pm, Pn, and Ps, but not the Pt of Esc ] OSC Ps ; Pt BEL
# in 5.4 Control Sequences of ECMA-48_5th 1991


MouseSixByteReportPattern = b"\x1B\\[" rb"M..."  # MPR X Y


def control(bytes_) -> bytes:
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


def bytes_take_seq(bytes_) -> bytes:
    """Take one whole Byte Sequence, else zero Bytes"""

    seq = b""
    if bytes_:
        seq = bytes_take_mouse_six_byte_report(bytes_)
        if not seq:
            seq = bytes_take_control_sequence(bytes_)  # would misread Mouse Six Byte
            if not seq:
                seq = bytes_take_text_sequence(bytes_)  # would misread C0 Sequence

    return seq  # may be empty


def bytes_take_text_sequence(bytes_) -> bytes:
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


def bytes_take_control_sequence(bytes_) -> bytes:
    """Take 1 whole C0 Control Sequence that starts these Bytes, else 0 Bytes"""

    # Take nothing when given nothing

    if bytes_ == b"":
        return b""

    # Take nothing when not given a C0 Control Byte to start with

    head = bytes_[:1]
    if head not in C0_BYTES:
        return b""

    # Take a C0 Control Byte by itself

    if head != b"\x1B":
        return head

    # Take 1 whole C0 Esc Sequence that starts these Bytes, else 0 Bytes

    seq = bytes_take_esc_sequence(bytes_)

    return seq  # may be empty

    # in Output Bytes, people look for CR LF after CR, else take CR LF, else take CR


def bytes_take_esc_sequence(bytes_) -> bytes:
    """Take 1 whole C0 Esc Sequence that starts these Bytes, else 0 Bytes"""

    assert ESC == b"\x1B"
    assert CsiStartPattern == b"\x1B\\[" rb"[\x30-\x3F]*[\x20-\x2F]*"
    assert CsiEndPattern == rb"[\x40-\x7E]"

    assert bytes_.startswith(ESC), bytes_

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

    assert ESC == b"\x1B"
    assert CSI == b"\x1B["

    assert bytes_.startswith(CSI), bytes_

    m0 = re.match(rb"^" + CsiStartPattern + rb"$", string=bytes_)
    if m0:
        return b""

    # Take one whole Esc [ Sequence, or settle for Esc [ begun but cut short

    m1 = re.match(rb"^" + CsiStartPattern, string=bytes_)
    assert m1, (m1, bytes_)

    start_seq = m1.string[m1.start() : m1.end()]
    end_seq = m1.string[m1.end() :][:1]
    seq = start_seq + end_seq

    mn = re.match(rb"^" + CsiEndPattern + rb"$", string=end_seq)
    if not mn:
        return start_seq

    return seq


def bytes_take_mouse_six_byte_report(bytes_) -> bytes:
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

    tcgetattr: list[int | list[bytes | int]] | None = None

    def __init__(self, stdio) -> None:
        self.stdio = stdio
        self.fd = stdio.fileno()
        self.tcgetattr = None

    def __enter__(self) -> "BytesTerminal":
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

    def __exit__(self, *exc_info) -> bool | None:
        r"""Start line-buffering Input and start replacing \n Output with \r\n"""

        fd = self.fd

        tcgetattr = self.tcgetattr
        if tcgetattr is not None:
            self.tcgetattr = None

            when = termios.TCSADRAIN
            termios.tcsetattr(fd, when, tcgetattr)

            # self.flush()

        return None

    def breakpoint(self) -> None:
        """Exit, breakpoint, and try to enter again"""

        self.__exit__(*sys.exc_info())
        breakpoint()
        self.__enter__()

    def get_terminal_columns(self) -> int:
        """Count Columns on Screen"""

        fd = self.fd
        size = os.get_terminal_size(fd)  # often < 50 us
        columns = size.columns

        return columns

    def get_terminal_rows(self) -> int:
        """Count Rows on Screen"""

        fd = self.fd
        size = os.get_terminal_size(fd)  # often < 50 us
        rows = size.lines

        return rows

        # 'shutil.get_terminal_size' often runs < 100 us

    def print(self, *args, **kwargs) -> None:
        """Work like Print, but end with '\r\n', not with '\n'"""

        assert CRLF == b"\r\n"

        alt_kwargs = dict(kwargs)
        if ("end" not in kwargs) or (kwargs["end"] is None):
            alt_kwargs["end"] = "\r\n"

        print(*args, **alt_kwargs)

        # 'bt.print' not much tested by ChordsTerminal

    def write(self, bytes_) -> None:
        """Write some Bytes without encoding them, & without ending the Line"""

        fd = self.fd
        os.write(fd, bytes_)

    def flush(self) -> None:
        """Flush the Output Buffer without waiting for the Line to end"""

        stdio = self.stdio
        stdio.flush()

        # 'bt.flush' not much tested by ChordsTerminal

    def read(self) -> bytes:
        """Read one or more Bytes"""

        fd = self.fd

        length = 1022  # large Paste came as 1022 Bytes per 100ms  # macOS 2023-03
        read = os.read(fd, length)
        assert read, read  # todo: test when 'os.read' does return b""

        return read

        # ⌘V ⌘V Paste Strokes sometimes arrived together in one read  # macOS 2023-03

    def kbhit(self, timeout=None) -> bool:  # 'timeout' in seconds
        """Wait till next Input Byte, else till Timeout, else till forever"""

        stdio = self.stdio

        rlist: list[typing.IO]
        wlist: list[typing.IO]
        xlist: list[typing.IO]

        rlist = [stdio]
        wlist = list()
        xlist = list()

        (alt_rlist, _, _) = select.select(rlist, wlist, xlist, timeout)
        available = bool(alt_rlist)

        return available

    def try_me(self) -> None:
        """Run a quick thorough self-test"""

        self.write(b"")  # tests 'os.write'
        self.kbhit(0)  # tests 'select.select'


#
# Add some Def's to Import ArgParse
#


byoargparse = sys.modules[__name__]


class ArgumentParser(argparse.ArgumentParser):
    """Amp up Class ArgumentParser of Import ArgParse"""

    def __init__(self, add_help=True) -> None:
        main_doc = __main__.__doc__
        assert main_doc

        # Compile much of the Arg Doc to Args of 'argparse.ArgumentParser'

        doc_lines = main_doc.strip().splitlines()
        prog = doc_lines[0].split()[1]  # first word of first line

        doc_firstlines = list(_ for _ in doc_lines if _ and (_ == _.lstrip()))
        alt_description = doc_firstlines[1]  # first line of second paragraph

        # Say when Doc Lines stand plainly outside of the Epilog

        def skippable(line) -> bool:
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

        super().__init__(
            prog=prog,
            description=description,
            add_help=add_help,
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=epilog,
        )

        # 'add_help=False' for 'cal -h', 'df -h', 'ls -h', etc

    #
    # def parse_args(self, args=None) -> argparse.Namespace:
    #     argspace = super().parse_args(args)
    #     return argspace
    #
    # yea no, MyPy would then explode with a deeply inscrutable
    #
    #   Signature of "parse_args" incompatible with supertype "ArgumentParser"
    #   [override]
    #

    def parse_args_else(self, args=None) -> argparse.Namespace:
        """Parse the Sh Args, even when no Sh Args coded as the one Sh Arg '--'"""

        # Print Diffs & exit nonzero, when Arg Doc wrong

        diffs = self.diff_doc_vs_format_help()
        if diffs:
            print("\n".join(diffs))

            sys.exit(2)

        # Print examples & exit zero, if no Sh Args

        testdoc = self.scrape_testdoc_from_epilog()
        if not sys.argv[1:]:
            print()
            print(testdoc)
            print()

            sys.exit(0)

        # Accept the "--" Sh Args Separator when present with or without Positional Args

        shargs = sys.argv[1:] if (args is None) else args
        if shargs == ["--"]:  # ArgParse chokes if Sep present without Pos Args
            shargs = ""

        # Print help lines & exit zero, else return Parsed Args

        argspace = self.parse_args(shargs)

        return argspace

        # often prints help & exits

    def diff_doc_vs_format_help(self) -> list[str]:
        """Form Diffs from Main Arg Doc to Parser Format_Help"""

        # Fetch the Main Doc, and note where from

        main_doc = __main__.__doc__
        assert main_doc

        main_filename = os.path.split(__file__)[-1]
        got_filename = "./{} --help".format(main_filename)

        # Fetch the Parser Doc from a fitting virtual Terminal
        # Fetch from a Black Terminal of 89 columns, not current Terminal width
        # Fetch from later Python of "options:", not earlier Python of "optional arguments:"

        with_columns = os.getenv("COLUMNS")
        os.environ["COLUMNS"] = str(89)
        try:
            parser_doc = self.format_help()

        finally:
            if with_columns is None:
                os.environ.pop("COLUMNS")
            else:
                os.environ["COLUMNS"] = with_columns

        parser_doc = parser_doc.replace("optional arguments:", "options:")

        parser_filename = "ArgumentParser(...)"
        want_filename = parser_filename

        # Print the Diff to Parser Doc from Main Doc and exit, if Diff exists

        got_doc = main_doc.strip()
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

        return diffs

    def scrape_testdoc_from_epilog(self) -> str:
        """Pick out the last Heading of the Epilog of an Arg Doc, and drop its Title"""

        epilog = "" if (self.epilog is None) else self.epilog

        lines = epilog.splitlines()

        indices = list(_ for _ in range(len(lines)) if lines[_])  # no empties
        indices = list(_ for _ in indices if not lines[_].startswith(" "))  # headings

        testdoc = "\n".join(lines[indices[-1] + 1 :])  # last heading, minus its title
        testdoc = textwrap.dedent(testdoc)
        testdoc = testdoc.strip()

        return testdoc


#
# Sketch practically-never work
#


... == """

Terminal Windows smaller than the MacOS min of 5 Rows x 20 Columns

"""  # type: ignore


#
# Sketch future work
#


... == r"""  # up towards demo of reduce Python to Color Python

--

vi.py /dev/tty  # ⇧Z⇧Z to save to 'dev.tty'

revive messaging of Press ⌃C ⇧Z ⇧Q to quit

Save Cursor/ Restore to go to Status and back

tell us at hit X of Y

--

underline the row of the Cursor to show Insert/ Replace

status row for the ChordsScreenTest
move self-tests into 2 ⇧M or 2 ^ as less occupied that ⇧Z Q

status row for ⌃G
status row for tracing writes to ChordsTerminal
variably many status rows

:! could be an input line outside of scrolling
/ could be an input line outside of scrolling

--

mm '' 'm marks of Cursor Position

⇧Y should be Y $ not Y Y
as per Vim Help at:  help Y

--

persist qq @q as played ["@q"] = b"..."

save sparse as played into TypeScript
save sparse as scanned as TypeScript
save full as pseudotty scanned as TypeScript
save with delays into Py
save as punctuation implied from Color into Py

--

. and U redo and undo, though our Undo's will be partial

--

digits Arg for ⇧A ⇧R A I R

let the digits be 0x etc, uppercase if 0x
⌃V and \x and \u and \U and \a character insert

track Bold and Color

take Cursor Row for Status Row
⎋[y;xH ⎋[K update Status Row

trace what people do to grow the sparse Area of known Screen
notice when they move the Status Row

save it as a 'vi.typescript' File of Color etc,
with no movement except as needed to leap over sparse gaps

help people bold the un-sparse, like to know when they've traced over it all

--

test \n \r \r\n bytes inside macOS Paste Buffer

less pain here from tides forcing auto-wrapped searches and auto-cancelled searches

jump to color

--

copy in older Vi dreams from:  demos/vi1.py, futures.md, etc

add patch on the side to test random match to real Vi

"""  # type: ignore


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/demos/vi3.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
