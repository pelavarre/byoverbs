#!/usr/bin/env python3

r"""
usage: vi2.py [-h] [-q]

edit the Screen in reply to Keyboard Chord Sequences

options:
  -h, --help   show this help message and exit
  -q, --quiet  say less

quirks:
  quits when told ⌃C ⇧Z ⇧Q, or ⌃C ⌃L : Q ! Return
  accepts ⇧Q V I Return without action or complaint

keystrokes:
  ⌃C ⌃D ⌃G ⌃H ⌃J ⌃L Return ⌃N ⌃P ⌃\
  Space $ + - 0 1 2 3 4 5 6 7 8 9 ⇧H ⇧M ⇧L H J K L |
  ⇧C ⇧D ⇧G ⇧I ⇧O ⇧R ⇧S ⇧X ^ _ C$ CC D$ DD A I O R S X

self-tests:  # TODO: could be 2 ⇧M or 2 ^
  1 ⇧Z Q test of Keyboard, 2 ⇧Z Q test of Screen, etc

escape-sequences:
  ⎋[d line-position-absolute  ⎋[G cursor-character-absolute
  ⎋[1m bold  ⎋[31m red  ⎋[32m green  ⎋[34m blue  ⎋[38;5;130m orange  ⎋[m plain
  ⎋[4h insertion-mode  ⎋[6 q bar  ⎋[4l replacement-mode  ⎋[4 q skid  ⎋[ q unstyled
  ⎋[M delete-line  ⎋[L insert-line  ⎋[P delete-character  ⎋[@ insert-character
  ⎋[T scroll-up  ⎋[S scroll-down

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
import signal
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

    stdio = sys.__stderr__
    with BytesTerminal(stdio) as bt:
        ct = ChordsTerminal(bt)
        vt = ViTerminal(ct)

        vt.run_till_quit()

    # Sh Pipes nudge us to read Stdin, write Stdout, find Tty at Stderr
    # Py ShUtil Get_Terminal_Size nudges us to lose Tty when not found at Stdout


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
        bytes_key = bytearray()
        char_holds = list()
        digit_holds = list()
        exit_writes = list()

        func_by_chords = self.form_func_by_chords_main()

        #

        self.ct = ct  # ChordsTerminal

        self.bytes_key = bytes_key  # the Bytes held, till next Char
        self.char_holds = char_holds  # the Words of Chars held, till next Func
        self.digit_holds = digit_holds  # the Digits held, till next Func

        self.chars_key_list = list()  # the Names of Func's Read
        self.chars_key = None  # the Name of the last Func Read
        self.func_by_chords = func_by_chords  # the Func's by Name

        self.exit_writes = exit_writes

    def pid_suspend(self):  # Vi ⌃Z F G Return
        """Release the Screen & Keyboard, pause this Process Pid, re-acquire"""

        ct = self.ct
        bt = ct.bt

        # Place the Cursor

        bt.print()
        y = bt.get_terminal_lines()
        alt_y = max(y - 2, 1)
        bt.write("\x1B[{}H".format(alt_y).encode())
        bt.write(b"\x1B[J")

        # Suspend and resume this Process Pid

        pid = os.getpid()
        signal_ = signal.SIGTSTP

        ct.__exit__(*sys.exc_info())
        os.kill(pid, signal_)
        ct.__enter__()

        # todo: this hangs inside its 'os.kill' if i call Vi Py from Py or Zsh or Bash

    def __exit__(self, *exc_info):
        """Cancel"""

        ct = self.ct
        bt = ct.bt
        exit_writes = self.exit_writes

        assert CUP_Y1 == "\x1B[{}H"

        # Exit the Screen Modes entered

        write = b"".join(sorted(set(exit_writes)))
        self.write_if(write)

        # Close out same as 'def try_screen', when not running quietly

        self.print_if()

        y = bt.get_terminal_lines()
        self.write_if("\x1B[{}H".format(y).encode())

    #
    # Launch and Quit
    #

    def run_till_quit(self):
        """Loop Terminal Input back as Terminal Output"""

        ct = self.ct
        args_quiet = main.args.quiet

        assert CUU == b"\x1B[A"

        # Start up noisily, or not

        if not args_quiet:
            ct.write(b"\x1B[A")
            self.help_quit()

        # Read enough Chords to choose a Func, and then run that Func

        try:
            while True:
                self.read_chords_run_func()  # may raise SystemExit

        # Clean up at Exit

        finally:
            exc_info = sys.exc_info()
            self.__exit__(*exc_info)

    def read_chords_run_func(self, stale_chords=None):
        """Read Chords till they name a Func, then run that Func"""

        bytes_key = self.bytes_key
        ct = self.ct
        char_holds = self.char_holds
        digit_holds = self.digit_holds

        assert not digit_holds, digit_holds
        assert not char_holds, char_holds

        # Cope if the Caller read some Chords ahead

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

            # Echo the Bytes and Chars naming Funcs

            self.echo_chords(chords)

            # Run the Func of Bytes, or the closing Func of Chars

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

    def echo_chords(self, chords):
        """Echo the collected Bytes and the collected Words of Chars"""

        ct = self.ct
        bytes_key = self.bytes_key
        digit_holds = self.digit_holds
        args_quiet = main.args.quiet

        # Form a Python Repr to echo Bytes

        if isinstance(chords, bytes):
            bytes_key.extend(chords)
            status = bytes(bytes_key)
            status = repr(status)

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

            status = self.chars_to_status(chars)

        # Rewrite the Status Row  # todo: warp the Cursor there

        if not args_quiet:
            write_chars = " " + status
            if not isinstance(chords, bytes):
                byte_status = bytes(bytes_key)
                byte_status = repr(byte_status)
                byte_write_chars = " " + byte_status
                length = len(byte_write_chars + write_chars)
                write_chars += length * "\b"

            write = write_chars.encode()
            ct.write(write)

    def chars_to_status(self, chars):
        """Say how to echo Chars as Status"""

        status = ""
        for ch in chars:
            if ch.encode() in C0_BYTES:
                status += Control + chr(ord(ch) ^ 0x40)
            else:
                status += ch

        return status

    def find_func_by_chords(self, chords):
        """Find the Func most closely named by Bytes and Words of Chars"""

        func_by_chords = self.func_by_chords
        chars_key_list = self.chars_key_list

        assert Esc == b"\x1B"

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

    def form_func_by_chords_main(self):
        """Map Words of Chars to Funcs"""

        func_by_chords = dict()

        # Map Words of Chars to Funcs

        #
        # Map Funcs at Words of ⌃ @ABCDEFGHIJKLMNO PQRSTUVWXYZ[\]^_
        #

        # ["⌃@"]
        # ["⌃A"]
        # ["⌃B"]
        func_by_chords["⌃C"] = self.help_quit_if
        func_by_chords["⌃D"] = self.help_quit_if
        # ["⌃E"]
        # ["⌃F"]
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
        # ["⌃U"]
        # ["⌃V"]
        # ["⌃W"]
        # ["⌃X"]
        # ["⌃Y"]
        func_by_chords["⌃Z"] = self.pid_suspend

        # ["Esc"]  # collides with C0 Esc Sequences
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

        # [": !"] = self.system  # TODO
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
        func_by_chords["⇧S"] = self.row_n_cut_insert  # "S"ubstitute
        # ["⇧T"] = self.upto_x_minus
        # ["⇧U"]
        # ["⇧V"]
        # ["⇧W"] = self.word_plus_n
        func_by_chords["⇧X"] = self.column_minus_n_cut  # e"X"cise
        # ["⇧Y"] = self.row_tail_copy

        func_by_chords["⇧Z Q"] = self.try_me_n  # could also take 'Z ⇧Q' and 'Z Q'
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
        func_by_chords["C C"] = self.row_n_cut_insert  # "c"hange
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

    def shrug(self):  # Vi Bytes
        """Consciously make no reply"""

        pass

    def disclose(self):  # Vi ⌃G
        """Show some of the ChordsTerminal Cache of BytesTerminal"""

        ct = self.ct
        ct.print("  {},{}  ".format(ct.row, ct.column), end="")

        # todo: print into Status Rows

    def redraw(self):  # Vi ⌃L
        """Call for Refresh of the ChordsTerminal Cache of BytesTerminal"""

        ct = self.ct
        ct.redraw()

        # no Refresh happens till after Read of CPR

    def hold_digit(self):  # Vi 1 2 3 4 5 6 7 8 9, and Vi 0 too thereafter
        """Hold Digits till Digits complete"""

        digit_holds = self.digit_holds
        chars_key = self.chars_key

        assert chars_key in "0123456789", repr(chars_key)
        if not digit_holds:
            assert chars_key != "0", repr(chars_key)

        digit_holds.extend(chars_key)

    def pull_digits_int_else(self, default=None):
        """Clear the Digits, but return what they were, as an Int"""

        digits = self.pull_digits_chars()
        digits_int_else = int(digits) if digits else default

        return digits_int_else

    def pull_digits_chars(self):
        """Clear the Digits, but return what they were, as Chars"""

        digit_holds = self.digit_holds

        digits = "".join(digit_holds)
        digit_holds.clear()

        return digits

    def write_digits(self, form):
        """Write a Csi Pn F Byte Sequence with zero or more Held Digits inside"""

        ct = self.ct
        digits = self.pull_digits_chars()  # may be empty

        assert form.count("{}") == 1, repr(form)
        chars = form.format(digits)
        write = chars.encode()
        ct.write(write)

    def write_form_n(self, form, n):
        """Write a Csi Pn F Byte Sequence, but with the Digits of an Int inside"""

        ct = self.ct

        assert isinstance(n, int), repr(n)
        assert n > 0, n

        assert form.count("{}") == 1, repr(form)
        chars = form.format(n)
        write = chars.encode()
        ct.write(write)

    def write_bytes_key(self):
        """Write a Csi Pn F Byte Sequence given as Keyboard Input"""

        ct = self.ct
        bytes_key = self.bytes_key
        chars_key = self.chars_key

        assert b"\x1B" == Esc
        encode = chars_key.encode()
        if encode.startswith(b"\x1B"):
            assert encode == bytes_key, (encode, bytes_key)

        ct.write(bytes_key)

    def hold_chars(self):  # Vi ⇧Z etc
        """Hold Char Chords till Chars complete"""

        char_holds = self.char_holds
        chars_key = self.chars_key

        assert isinstance(chars_key, str), repr(chars_key)

        char_holds.extend(chars_key)
        char_holds.extend(" ")

    def cancel_if(self):  # Vi Delete  # Vi ⌃H
        """Cancel a Word and its Digits, else go to start of N Chars before here"""

        char_holds = self.char_holds
        digit_holds = self.digit_holds

        if char_holds:
            char_holds.clear()
            digit_holds.clear()
            return

        self.char_minus_n()

    def help_quit_if(self):  # Vi ⌃C ⌃D ⌃\ etc
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

    def help_quit(self):  # Vi ⌃C ⌃D ⌃\ etc
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

    def slap_back_chars(self):  # i'm afraid i can't do that, Dave.
        """Say don't do that"""

        ct = self.ct
        # ct.bt.breakpoint()  # jitter Sat 10/Jun

        chars_key = self.chars_key
        chars_key_list = self.chars_key_list
        digit_holds = self.digit_holds
        args_quiet = main.args.quiet

        chars_key_list.extend(["Bel", "⌃C"])

        assert BEL == b"\a"

        chords = chars_key + " " + "Bel"
        self.echo_chords(chords)

        digit_holds.clear()

        ct.write(b"\a")
        if not args_quiet:
            if ct.kbhit(timeout=0):
                ct.print()  # cancelled Esc, Esc [, Return, etc

    def force_quit(self):  # ⇧Z ⇧Q
        """Force quit Vi, despite dirty Cache, etc"""

        ct = self.ct
        assert CR == b"\r"
        ct.write(b"\r")

        sys.exit()

    #
    # Move the Cursor relative to itself
    #

    def column_minus_n(self):  # Vi H  # Vi ←
        """Go left"""

        assert CUB_N == "\x1B[{}D"
        self.write_digits("\x1B[{}D")

    def column_plus_n(self):  # Vi L  # Vi →
        """Go right"""

        assert CUF_N == "\x1B[{}C"
        self.write_digits("\x1B[{}C")

    def row_plus_n(self):  # Vi J  # Vi ↓
        """Go down"""

        assert CUD_N == "\x1B[{}B"

        self.write_digits("\x1B[{}B")

    def row_minus_n(self):  # Vi K  # Vi ↑
        """Go up"""

        assert CUU_N == "\x1B[{}A"
        self.write_digits("\x1B[{}A")

    #
    # Move the Cursor relative to the Screen
    #

    def column_first_if(self):  # Vi 0 when not-preceded by 1 2 3 4 5 6 7 8 9
        """Go to First Column of Row"""

        ct = self.ct
        digit_holds = self.digit_holds

        if digit_holds:
            self.hold_digit()
            return

        assert CR == b"\r"
        ct.write(b"\r")

    def column_n(self):  # Vi |  # Vi ⇧\
        """Go from Left of Row"""

        assert CHA_X == "\x1B[{}G"

        self.write_digits("\x1B[{}G")

    def line_n_start(self):  # Vi ⇧G
        """Go down from Top of File, to the Nth Line Start"""

        ct = self.ct
        rows = ct.get_scrolling_rows()
        n = self.pull_digits_int_else(default=rows)

        assert VPA_Y == "\x1B[{}d"

        self.write_form_n("\x1B[{}d", n)
        self.line_start()

    def row_high_n_line_start(self):  # Vi ⇧H
        """Go down from Top of Screen, to the Nth Line Start"""

        assert VPA_Y == "\x1B[{}d"

        self.write_digits("\x1B[{}d")
        self.line_start()

    def row_middle_line_start_once(self):  # Vi ⇧M
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

    def row_low_n_line_start(self):  # Vi ⇧L
        """Go up from Bottom of Screen, to the -Nth Line Start"""

        ct = self.ct
        rows = ct.get_scrolling_rows()

        n = self.pull_digits_int_else(default=1)

        assert VPA_Y == "\x1B[{}d"

        alt_n = (rows + 1 - n) if (n < rows) else 1
        self.write_form_n("\x1B[{}d", n=alt_n)
        self.line_start()

    #
    # Move the Cursor relative to the Line
    #

    def char_minus_n(self):  # Vi Delete  # Vi ⌃H  # when no Chars Held
        """Go to start of N Chars before here"""

        ct = self.ct

        assert CUU == b"\x1B[A"
        assert CUB_N == "\x1B[{}D"

        # Move as far as Left of Row, but then give up, if Column unknown

        if ct.column is None:
            self.column_minus_n()
            return

        # Go back as if through Chars, not so simply as by Columns

        n = self.pull_digits_int_else(default=1)

        alt_n = n
        while alt_n:
            assert alt_n > 0, alt_n

            # Go left inside this Row

            column = ct.column
            if column > 1:
                left_n = min(column - 1, alt_n)
                alt_n -= left_n
                self.write_form_n("\x1B[{}D", n=left_n)
                assert ct.column == (column - left_n), (ct.column, column, left_n)

                continue

            # Cope if no Rows above

            row = ct.row
            if row == 1:
                if n == alt_n:
                    self.slap_back_chars()  # Vi Delete or ⌃H at Start of File

                return

            # Go to end of the Row above

            ct.write(b"\x1B[A")
            if ct.row is not None:
                assert ct.row == (row - 1), (ct.row, row)
            self.line_end()
            alt_n -= 1

    def char_plus_n(self):  # Vi Space
        """Go to end of N Chars here"""

        ct = self.ct

        assert CUD == b"\x1B[B"
        assert CUF_N == "\x1B[{}C"
        assert CR == b"\r"

        # Move as far as Right of Row, but then give up, if Column unknown

        if ct.column is None:
            self.column_plus_n()
            return

        # Go ahead as if through Chars, not so simply as by Columns

        n = self.pull_digits_int_else(default=1)

        alt_n = n
        while alt_n:
            assert alt_n > 0, alt_n

            # Go right inside this Row

            column = ct.column
            columns = ct.get_scrolling_columns()
            if column < columns:
                right_n = min(columns - column, alt_n)
                alt_n -= right_n
                self.write_form_n("\x1B[{}C", n=right_n)
                assert ct.column == (column + right_n), (ct.column, column, right_n)

                continue

            # Cope if no Rows belows

            row = ct.row
            rows = ct.get_scrolling_rows()
            if row == rows:
                if n == alt_n:
                    self.slap_back_chars()  # Vi Space at End of File

                return

            # Go to Start of the Row below (not to the indented Start of Line)

            ct.write(b"\x1B[B")
            assert ct.row == (row + 1), (ct.row, row)
            ct.write(b"\r")
            alt_n -= 1

    def line_n_minus_start(self):  # Vi -
        """Go to the top-left of N Lines above here"""

        assert CUU_N == "\x1B[{}A"

        self.write_digits("\x1B[{}A")
        self.line_start()

    def line_n1_plus_start(self):  # Vi _  # Vi ⇧-
        """Go to the bottom-left of N Lines here"""

        n = self.pull_digits_int_else(default=1)

        assert CUD_N == "\x1B[{}B"

        n1 = n - 1
        if n1:
            self.write_form_n("\x1B[{}B", n=n1)
        self.line_start()

    def line_n_plus_start(self):  # Vi +  # Vi ⇧=
        """Go to the bottom-left of N Lines below here"""

        assert CUD_N == "\x1B[{}B"

        self.write_digits("\x1B[{}B")
        self.line_start()

    def line_start_once(self):  # Vi ^
        """Go to Line Start, only without Digits"""

        if self.pull_digits_chars():
            self.slap_back_chars()  # Vi ^ with Digits Arg
            return

        self.line_start()

    def line_start(self):
        """Go to Line Start"""

        if self.pull_digits_chars():
            self.slap_back_chars()  # Vi ^ with Digits Arg
            return

        ct = self.ct
        assert CR == b"\r"
        ct.write(b"\r")

        # classic Vi goes to first non-Space Char

    def line_n_plus_end(self):  # Vi $  # Vi ⇧4
        """Go to the bottom-right of N Lines here"""

        n = self.pull_digits_int_else(default=1)

        assert CUD_N == "\x1B[{}B"

        n1 = n - 1
        if n1:
            self.write_form_n("\x1B[{}B", n=n1)
        self.line_end()

    def line_end(self):
        """Go to Line End"""

        ct = self.ct
        columns = ct.get_scrolling_columns()
        assert CHA_X == "\x1B[{}G"
        self.write_form_n("\x1B[{}G", n=columns)

        # classic Vi goes to last non-Space Char

    #
    # Cut Chars or Rows
    #

    def column_plus_n_cut(self):  # Vi X
        """Cut N Chars here and to the right, from this Row"""

        assert DCH_N == "\x1B[{}P"
        self.write_digits("\x1B[{}P")

    def column_minus_n_cut(self):  # Vi ⇧X
        """Cut N Chars to the left, from this Row"""

        ct = self.ct
        column = ct.column
        n = self.pull_digits_int_else(default=1)

        assert BS == b"\b"
        assert DCH_N == "\x1B[{}P"

        alt_n = n if (column is None) else min(column - 1, n)
        if alt_n:
            ct.write(alt_n * b"\b")
            self.write_form_n("\x1B[{}P", n=alt_n)

    def row_n_cut(self):  # Vi D D
        """Cut N Rows here and below, and go to Line Start"""

        assert DL_N == "\x1B[{}M"
        self.write_digits("\x1B[{}M")
        self.line_start()

    def row_n_dedent(self):  # Vi < <
        """Dedent N Rows here"""

        ct = self.ct
        n = self.pull_digits_int_else(default=1)

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

    def row_n_tail_cut_column_minus(self):  # Vi ⇧D
        """Cut N - 1 Rows below, then Tail of Row here, then go left"""

        ct = self.ct
        self.row_n_tail_cut()
        ct.write(b"\b")

    def row_n_tail_cut(self):
        """Cut N - 1 Rows below, then Tail of Row here"""

        ct = self.ct
        n = self.pull_digits_int_else(default=1)

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

    def column_plus_n_cut_insert(self):  # Vi S
        """Cut N Chars here, and then insert, as if Vi X I"""

        self.column_plus_n_cut()
        self.insert_n_till()

    def row_n_indent(self):  # Vi > >
        """Indent N Rows here"""

        ct = self.ct
        exit_writes = self.exit_writes
        n = self.pull_digits_int_else(default=1)

        row = ct.row
        rows = ct.get_scrolling_rows()

        assert SM_IRM == b"\x1B[4h"
        assert CR == b"\r"
        assert CUD == b"\x1B[B"
        assert CUU_N == "\x1B[{}A"
        assert RM_IRM == b"\x1B[4l"

        ct = self.ct
        exit_writes = self.exit_writes

        alt_n = n
        if row is not None:
            alt_n = min(n, rows + 1 - row)

        assert SM_IRM == b"\x1B[4h"
        assert CR == b"\r"
        assert CUD == b"\x1B[B"
        assert CUU_N == "\x1B[{}A"
        assert RM_IRM == b"\x1B[4l"

        # Enter Insert Mode, if need be

        with_inserting = b"\x1B[4l" not in exit_writes
        if with_inserting:
            exit_writes.append(b"\x1B[4l")
            ct.write(b"\x1B[4h")

        # Insert 4 Spaces  # todo: classic Vi can indent by "\t" too

        for i in range(alt_n):
            ct.write(b"\r")
            if i:
                ct.write(b"\x1B[B")
            ct.write(4 * b" ")

        if alt_n > 1:
            alt_n1 = alt_n - 1
            self.write_form_n("\x1B[{}A", n=alt_n1)
        self.line_start()

        # Exit Insert Mode, if entered

        if with_inserting:
            ct.write(b"\x1B[4l")
            exit_writes.remove(b"\x1B[4l")

        # Vi > > doesn't delete non-Space Chars at Right Margin

    def row_n_tail_cut_insert(self):  # Vi ⇧C
        """Cut N - 1 Rows below, then Tail of Row, and then insert, as if Vi ⇧D I"""

        self.row_n_tail_cut()
        self.insert_n_till()

    def row_n_cut_insert(self):  # Vi ⇧S  # Vi C C
        """Cut N Rows but then start a new Row here, as if D D ⇧O"""

        ct = self.ct

        assert CR == b"\r"
        assert DL_N == "\x1B[{}M"
        assert IL == b"\x1B[L"

        ct.write(b"\r")
        self.write_digits("\x1B[{}M")
        ct.write(b"\x1B[L")

        self.insert_n_till()

    def column_plus_insert_n_till(self):  # Vi A
        """Go right and then insert, as if Vi 1 L I"""

        ct = self.ct

        if self.pull_digits_chars():
            self.slap_back_chars()  # todo: Vi A with Digits Args
            return

        assert CUF == b"\x1B[C"

        ct.write(b"\x1B[C")

        self.insert_n_till()

    def row_start_insert_n_till(self):  # Vi ⇧I
        """Go to Line Start and then insert, as if Vi ^ I"""

        self.line_start()
        self.insert_n_till()

    def row_end_return_insert_n_till(self):  # Vi ⇧O
        """Insert a new Row above this Row, as if Vi 0 I Return ↑"""

        ct = self.ct

        assert IL == b"\x1B[L"
        assert CR == b"\r"

        ct.write(b"\x1B[L")
        ct.write(b"\r")

        self.insert_n_till()

    def row_below_return_insert_n_till(self):  # Vi O
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

    def insert_n_till(self):  # Vi I
        """Insert Text Sequences till ⌃C, except for ⌃O and Control Sequences"""

        ct = self.ct
        exit_writes = self.exit_writes

        if self.pull_digits_chars():
            self.slap_back_chars()  # todo: Vi I with Digits Args
            return

        assert SM_IRM == b"\x1B[4h"
        assert RM_IRM == b"\x1B[4l"

        # Enter Insert Mode

        exit_writes.append(b"\x1B[4l")
        ct.write(b"\x1B[4h")

        exit_writes.append(b"\x1B[ q")
        ct.write(b"\x1B[6 q")

        # Insert Text Sequences till ⌃C, except for ⌃O and Control Sequences

        func_by_chords = self.form_func_by_chords_insert()
        self.run_text_sequence(func_by_chords)

        # Exit Insert Mode gently, not abruptly

        ct.write(b"\x1B[4l")
        exit_writes.remove(b"\x1B[4l")

        ct.write(b"\x1B[ q")
        exit_writes.remove(b"\x1B[ q")

    def insert_delete(self):
        """Go left, then Shift Left the Tail of this Row"""

        ct = self.ct
        assert DCH_N == "\x1B[{}P"
        ct.write(b"\b\x1B[P")

        # todo: Vi I Delete in first Column deletes Line-Break

    def insert_return(self):
        """Insert new Row above this Row"""

        ct = self.ct

        assert CUD == b"\x1B[B"
        assert IL == b"\x1B[L"

        ct.write(b"\x1B[B")
        ct.write(b"\x1B[L")
        self.line_start()

        # todo: Vi I Return splits Row

    def form_func_by_chords_insert(self):
        """Map Single Words of Control Chars to Funcs while Inserting Text"""

        func_by_chords = dict()
        func_by_chords["Delete"] = self.insert_delete
        func_by_chords["Return"] = self.insert_return

        return func_by_chords

    #
    # Replace
    #

    def replace_once(self):  # Vi R
        """Replace once"""

        self.replace_n_till(limit=1)

        # Vi R ⌃V ⌃O and our R ⌃V ⌃O work the same
        # Vi R ⌃O works like Vi ⇧R ⌃V ⌃O ⌃C, vs our R ⌃O works like Vi ⇧R ⌃O

    def replace_n_till(self, limit=None):  # Vi ⇧R
        """Replace Text Sequences till ⌃C, except for ⌃O and Control Sequences"""

        ct = self.ct
        exit_writes = self.exit_writes

        if self.pull_digits_chars():
            self.slap_back_chars()  # todo: Vi ⇧R with Digits Arg
            return

        # Enter Replace Mode

        ct.write(b"\x1B[4l")

        exit_writes.append(b"\x1B[ q")
        ct.write(b"\x1B[4 q")

        # Replace Text Sequences till ⌃C, except for ⌃O and Control Sequences

        func_by_chords = self.form_func_by_chords_replace()
        self.run_text_sequence(func_by_chords, limit=limit)

        # Exit Replace Mode gently, not abruptly

        ct.write(b"\x1B[ q")
        exit_writes.remove(b"\x1B[ q")

    def replace_delete(self):
        """Go left to Replace with Space"""

        ct = self.ct
        ct.write(b"\b \b")

        # todo: Vi ⇧R Delete undoes Replace's but then just moves backwards

    def replace_return(self):
        """Insert new Row below this Row"""

        ct = self.ct

        assert CUD == b"\x1B[B"
        assert IL == b"\x1B[L"

        ct.write(b"\x1B[B")
        ct.write(b"\x1B[L")
        self.line_start()

        # todo: Vi ⇧R Return matches Vi I Return, but records replacements

    def form_func_by_chords_replace(self):
        """Map Single Words of Control Chars to Funcs while Replacing Text"""

        func_by_chords = dict()
        func_by_chords["Delete"] = self.replace_delete
        func_by_chords["Return"] = self.replace_return

        return func_by_chords

    #
    # Insert or Replace
    #

    def run_text_sequence(self, func_by_chords, limit=None):
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
    # Test
    #

    def print_if(self, *args, **kwargs):
        """Print Chars, if not running quietly"""

        ct = self.ct
        if not main.args.quiet:
            ct.print(*args, **kwargs)

    def write_if(self, bytes_):
        """Write Bytes, if not running quietly"""

        ct = self.ct
        if not main.args.quiet:
            ct.write(bytes_)

    def try_me_n(self):
        """Run a quick thorough self-test"""

        digits_int_else = self.pull_digits_int_else()

        funcs_by_int = dict()

        funcs_by_int[None] = self.try_keyboard
        funcs_by_int[None] = self.try_screen  # last wins

        funcs_by_int[1] = self.try_keyboard
        funcs_by_int[2] = self.try_screen

        if digits_int_else not in funcs_by_int.keys():
            self.slap_back_chars()  # Test Func not-found
            return

        int_func = funcs_by_int[digits_int_else]
        int_func()

    def try_keyboard(self):
        """Test the ChordsTerminal Read till ⌃C"""

        ct = self.ct

        self.print_if("Press ⌃C to stop our ChordsKeyboardTest")

        ckt = ChordsKeyboardTest(ct)
        ckt.run_till_quit()

        self.print_if()  # todo: prompt to Quit at each Screen of Input?

    def try_screen(self):
        """Test the BytesTerminal Write at a Chords Terminal, till ⌃C"""

        ct = self.ct

        assert CUP_Y1 == "\x1B[{}H"

        self.print_if("Press ⌃C to stop our ChordsScreenTest")

        cst = ChordsScreenTest(ct)
        cst.run_till_quit()

        self.print_if()

        bt = ct.bt
        y = bt.get_terminal_lines()
        self.write_if("\x1B[{}H".format(y).encode())


#
# Test the BytesTerminal Write at a Chords Terminal, till ⌃C
#


class ChordsScreenTest:
    """Test the BytesTerminal Write at a Chords Terminal, till ⌃C"""

    def __init__(self, ct):
        self.ct = ct

    def run_till_quit(self):  # noqa  # C901 too complex
        """Test the BytesTerminal Write at a Chords Terminal, till ⌃C"""

        ct = self.ct
        bt = ct.bt
        args_quiet = main.args.quiet

        assert CUP_Y_X == "\x1B[{};{}H"
        assert DSR_FOR_CPR == b"\x1B[6n"
        assert CprPatternYX == rb"\x1B[\\[]([0-9]+);([0-9]+)R"

        writes = bytearray()
        yx_by_frame = 2 * [None]

        # Read Chords

        frame = None
        while True:
            chords = ct.read_chords()

            # Warp the Cursor to the Frame of Bytes|Str

            old_frame = frame
            frame = int(isinstance(chords, bytes))

            if not args_quiet:
                if old_frame != frame:
                    yx = yx_by_frame[frame]
                    if yx is not None:
                        cup = "\x1B[{};{}H".format(*yx)
                        cup = cup.encode()
                        ct.write(cup)

            # Capture and trace the Bytes, else write the Bytes in place of Str

            if isinstance(chords, bytes):
                writes.extend(chords)
                rep = bytes(writes)
                rep = repr(rep).encode()
                if not args_quiet:
                    assert CR == b"\r"
                    assert EL == b"\x1B[K"

                    ct.write(b"\r")
                    ct.write(b"\x1B[K")
                    ct.write(rep)
            else:
                ct.write(writes)
                writes.clear()

                # Quit after Control+C

                if chords == (Control + "C"):
                    break

            # Find the Cursor

            if not args_quiet:
                bt.write(DSR_FOR_CPR)  # todo: CPR through 'ct' to snoop '.row, .column'

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
                        cup = "\x1B[{};{}H".format(*yx)
                        cup = cup.encode()
                        ct.write(cup)


#
# Test the ChordsTerminal Read till ⌃C
#


class ChordsKeyboardTest:
    """Test the ChordsTerminal Read till ⌃C"""

    def __init__(self, ct):
        self.ct = ct

        t0 = dt.datetime.now()

        self.t0 = t0
        self.t1 = t0
        self.old_ms = None
        self.clocking = False

    def run_till_quit(self):
        """Test the ChordsTerminal Read till ⌃C"""

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

        ct = self.ct

        # Fetch one Byte or some Words of Chars

        read = ct.read_chords()

        # Timestamp

        self.t1 = dt.datetime.now()
        t1t0 = self.t1 - self.t0
        self.t0 = self.t1

        # Close the Clock Line if open

        if self.clocking:
            self.clocking = False
            ct.print()

        # Log the whole Keystroke as Words of Chars, or a Byte of it

        ms = int(t1t0.total_seconds() * 1000)
        if not ms:
            ct.print("    {}, {!r}".format(ms, read))
        else:
            if self.old_ms == 0:
                ct.print()
            ct.print("{}, {!r}".format(ms, read))

        self.old_ms = ms

        # Succeed

        return read

    def log_clock(self):
        """Timestamp no Chars and no Bytes from the Terminal"""

        ct = self.ct

        # Limit the rate of logging

        t2 = dt.datetime.now()
        t2t1 = t2 - self.t1
        if t2t1 >= dt.timedelta(seconds=3):
            self.t1 += dt.timedelta(seconds=1)

            # Print a Separator and open the Clock Line

            if not self.clocking:
                self.clocking = True
                ct.print()

            # Refresh the Clock

            hms = t2.strftime("%H:%M:%S")
            encode = hms.encode()

            assert CR == b"\r"

            ct.write(b"\r")
            ct.write(encode)

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
# Write Output as Mock Moves, read Input as Chars, above a BytesTerminal
#
#   "Esc", "Space", "Tab", and "Return" for b"\x1B", b" ", b"\t", and b"\r"
#   "⇧Tab", "⌥Space", b"⇧←" for b"\x1B[Z", b"\xC2\xA0", b"\x1B[1;2C"
#   "⌥3", "⇧F12" for b"\xC2\xA3", b"\x1B[\x33\x34\x7E"
#   "⌥E E" for b"\xC2\xB4"
#   etc
#


class ChordsTerminal:
    """Write Output as Mock Moves, read Input as Chars, above a BytesTerminal"""

    def __init__(self, bt):
        self.bt = bt

        self.holds = bytearray()  # the Holds received from the BytesTerminal Keyboard
        self.peeks = bytearray()  # the Holds already returned

        self.try_me()

        self.writes = bytearray()  # Bytes written but not yet parsed
        self.row = None  # the Row of the Cursor, if known
        self.column = None  # the Column of the Cursor, if known

    def __enter__(self):
        bt = self.bt
        bt.__enter__()

    def __exit__(self, *exc_info):
        bt = self.bt

        self.row = None
        self.column = None

        exit_ = bt.__exit__()

        return exit_

    def redraw(self):  # Vi ⌃L
        """Call for Refresh of the ChordsTerminal Cache of BytesTerminal"""

        assert DSR_FOR_CPR == b"\x1B[6n"

        self.row = None
        self.column = None

        self.write(b"\x1B[6n")

        # no Refresh happens till after Read of CPR

    #
    # Write Output as Mock Moves above a BytesTerminal
    #

    def print(self, *args, **kwargs):
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

    def write(self, bytes_):
        """Write Output as Bytes and also as Mock Moves, above a BytesTerminal"""

        bt = self.bt
        writes = self.writes

        bt.write(bytes_)
        writes.extend(bytes_)

        while True:
            seq = bytes_take_seq(writes)
            if not seq:
                break
            writes[::] = writes[len(seq) :]
            self.mock_write_seq(seq)

    def mock_write_seq(self, seq):
        """Write Output as Mock Moves"""

        assert seq, seq

        csi_match = re.match(rb"^" + CsiPattern + rb"$", string=seq)
        form_n_match = re.match(b"^\x1B\\[([0-9]*)[A-Za-z]$", string=seq)
        # form_y_x_match = re.match(b"^\x1B\\[([0-9]*);([0-9]*)[A-Za-z]$", string=seq)

        assert CUU_N == "\x1B[{}A"
        assert CUD_N == "\x1B[{}B"
        assert CUF_N == "\x1B[{}C"
        assert CUB_N == "\x1B[{}D"
        assert CUP_Y1 == "\x1B[{}H"
        assert CHA_X == "\x1B[{}G"
        assert VPA_Y == "\x1B[{}d"

        assert CUU == b"\x1B[A"
        assert CUD == b"\x1B[B"
        assert CUF == b"\x1B[C"
        assert CUB == b"\x1B[D"
        assert CUP == b"\x1B[H"

        if seq[:1] not in C0_BYTES:
            for index in range(len(seq)):
                assert seq[index:][:1] not in C0_BYTES, seq[index:][:1]
            self.jump_by_columns(columns=len(seq))
            return

        if seq == b"\b":
            self.jump_by_columns(columns=-1)
        elif seq == b"\n":
            self.jump_by_rows(rows=1)
        elif seq == b"\r":
            self.column = 1
        elif form_n_match:
            assert csi_match, seq

            f = bytes(seq[-1:])
            digits = form_n_match.group(1)  # drops leading Zeroes
            n = int(digits) if digits else 1

            mocks_by_f = {
                b"A": [(self.jump_by_rows, -n)],
                b"B": [(self.jump_by_rows, n)],
                b"C": [(self.jump_by_columns, n)],
                b"D": [(self.jump_by_columns, -n)],
                b"G": [(self.jump_to_column, n)],
                b"H": [(self.jump_to_row, n), (self.jump_to_column, 1)],
                b"d": [(self.jump_to_row, n)],
            }

            if f in mocks_by_f.keys():
                mocks = mocks_by_f[f]
                for mock in mocks:
                    (func, arg) = mock
                    func(arg)

            # Flake8 feels unrolling this Code is "too complex" in McCabe Complexity
            # Flake8 is wrong, and expensive to turn off - we'd mark this Func as 'noqa'

    def jump_to_row(self, row):
        """Mock moving the Cursor up or down to a chosen Row"""

        rows = self.get_scrolling_rows()
        capped_row = min(max(row, 1), rows)

        self.row = capped_row

        return capped_row

    def jump_by_rows(self, rows):
        """Mock moving the Cursor up or down by a count of Rows"""

        row = self.row
        if row is not None:
            self.jump_to_row(row + rows)

    def jump_to_column(self, column):
        """Mock moving the Cursor left or right to a chosen Column"""

        columns = self.get_scrolling_columns()
        capped_column = min(max(column, 1), columns)

        self.column = capped_column

        return capped_column

    def jump_by_columns(self, columns):
        """Mock moving the Cursor left or right by a count of Columns"""

        column = self.column
        if column is not None:
            self.jump_to_column(column + columns)

    def get_scrolling_columns(self):
        """Count Columns on Screen"""

        bt = self.bt
        columns = bt.get_terminal_columns()  # presumes no cache needed

        return columns

    def get_scrolling_rows(self):
        """Count Rows on Screen"""

        bt = self.bt
        lines = bt.get_terminal_lines()  # presumes no cache needed

        rows = lines  # todo: split off 1 or 2 Rows of Status below Scrolling

        return rows

    #
    # Read Input as Chars in from the Keyboard of a BytesTerminal
    #

    def read_chords(self):  # like return each of b'\x1B', b'[', b'A', and "↑", in turn
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

            # Read more Bytes, just once

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

        m = re.match(rb"^" + CprPatternYX + rb"$", seq)
        if m:
            self.row = int(m.group(1))
            self.column = int(m.group(2))

        plus = bytes_[len(seq) :]
        assert (seq + plus) == bytes_, (seq, plus, bytes_)

        return (seq, plus)

    def try_me(self):
        """Run a quick thorough self-test"""

        bt = self.bt

        assert bt.tcgetattr is not None  # requires called between Bt Enter & Exit

        bt.write(b"")  # tests 'os.write'
        self.kbhit(0)  # tests 'select.select'


#
# Name Screen Output Bytes and Keyboard Input Bytes
#


CUU_N = "\x1B[{}A"  # 04/01 Cursor Up (CUU) of N
CUU = b"\x1B[A"
CUD_N = "\x1B[{}B"  # 04/02 Cursor Down (CUD) of N
CUD = b"\x1B[B"
CUF_N = "\x1B[{}C"  # 04/03 Cursor Right (CUF) of N
CUF = b"\x1B[C"
CUB_N = "\x1B[{}D"  # 04/04 Cursor Left (CUB) of N
CUB = b"\x1B[D"

CHA_X = "\x1B[{}G"  # 04/07 Cursor Character Absolute (CHA)

CUP_Y_X = "\x1B[{};{}H"  # 04/08 Cursor Position (CUP) of Y X
CUP_Y1 = "\x1B[{}H"
CUP = b"\x1B[H"

EL = b"\x1B[K"  # 04/11 Erase In Line (EL) of no Ps
IL = b"\x1B[L"  # 04/12 Insert Line (IL)
DL_N = "\x1B[{}M"  # 04/13 Delete Line (DL) of N
DCH_N = "\x1B[{}P"  # 05/00 Delete Character (DCH)

VPA_Y = "\x1B[{}d"  # 06/04 Line Position Absolute (VPA)
SM_IRM = b"\x1B[4h"  # 06/08 Set Mode (SM)  # 4 Insertion Replacement Mode (IRM)
RM_IRM = b"\x1B[4l"  # 06/12 Reset Mode (RM)  # 4 Insertion Replacement Mode (IRM)

DSR_FOR_CPR = b"\x1B[6n"  # 06/14 Device Status Report (DSR) call for CPR


# 07/00..07/14 Private or Experimental Use

"\x1B[ q"  # 02/00 07/01  # Cursor No Style
"\x1B[4 q"  # 02/00 07/01  # Cursor Style 4 Skid
"\x1B[6 q"  # 02/00 07/01  # Cursor Style 6 Bar


CprPatternYX = rb"\x1B[\\[]([0-9]+);([0-9]+)R"  # 04/18 Cursor Pos~ Report (CPR) of Y X


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

CHORDS_BY_BYTES[b"\x1BOA"] = "↑"
CHORDS_BY_BYTES[b"\x1BOB"] = "↓"
CHORDS_BY_BYTES[b"\x1BOC"] = "→"
CHORDS_BY_BYTES[b"\x1BOD"] = "←"
# ⎋O replaces ⎋[ for ↑↓→← for b"\x1b[1?h" Application-Cursor-Keys till b"\x1b[1?l"


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


#
# Define whole & partial Control Byte and Text Byte Sequences
#


BEL = b"\a"  # 00/07 Bell
BS = b"\b"  # 00/08 Backspace
CR = b"\r"  # 00/13 Carriage Return
CRLF = b"\r\n"  # 00/13 00/10 Carriage Return + Line Feed
LF = b"\n"  # 00/10 Line Feed
Esc = b"\x1B"  # 01/11 Escape

CSI = b"\x1B["  # 01/11 05/11 Control Sequence Introducer  # till rb"[\x30-\x7E]"
OSC = b"\x1B]"  # 01/11 05/13 Operating System Command  # till BEL, CR, Esc \ ST, etc
SS3 = b"\x1BO"  # 01/11 04/15 Single Shift Three

C0_BYTES = b"".join(chr(_).encode() for _ in range(0, 0x20)) + b"\x7F"
C1_BYTES = b"".join(chr(_).encode() for _ in range(0x80, 0xA0))  # not U+00A0, U+00AD
# the Text Bytes of the first 0x80 (128) Bytes are the Bytes not-in the C0_BYTES


Control = "\N{Up Arrowhead}"  # ⌃
Option = "\N{Option Key}"  # ⌥
Shift = "\N{Upwards White Arrow}"  # ⇧
Command = "\N{Place of Interest Sign}"  # ⌘


CsiStartPattern = b"\x1B\\[" rb"[\x30-\x3F]*[\x20-\x2F]*"  # leading Zeroes allowed
CsiEndPattern = rb"[\x40-\x7E]"
CsiPattern = CsiStartPattern + CsiEndPattern
# as per 1991 ECMA-48_5th 5.4 Control Sequences
# Csi Patterns define many Pm, Pn, and Ps, but not the Pt of Esc ] OSC Ps ; Pt BEL


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

    if head != b"\x1B":
        return head

    # Take 1 whole C0 Esc Sequence that starts these Bytes, else 0 Bytes

    seq = bytes_take_esc_sequence(bytes_)

    return seq  # may be empty

    # in Output Bytes, people look for CR LF after CR, else take CR LF, else take CR


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

    def __exit__(self, *exc_info):
        r"""Start line-buffering Input and start replacing \n Output with \r\n"""

        fd = self.fd

        tcgetattr = self.tcgetattr
        if tcgetattr is not None:
            self.tcgetattr = None

            when = termios.TCSADRAIN
            termios.tcsetattr(fd, when, tcgetattr)

            # self.flush()

    def breakpoint(self):
        """Exit, breakpoint, and try to enter again"""

        self.__exit__(*sys.exc_info())
        breakpoint()
        self.__enter__()

    def get_terminal_columns(self):
        """Count Columns on Screen"""

        fd = self.fd
        size = os.get_terminal_size(fd)  # often < 50 us
        columns = size.columns

        return columns

    def get_terminal_lines(self):
        """Count Rows on Screen"""

        fd = self.fd
        size = os.get_terminal_size(fd)  # often < 50 us
        rows = size.lines

        return rows

        # 'shutil.get_terminal_size' often runs < 100 us

    def print(self, *args, **kwargs):  # 'bt.print' not much tested by ChordsTerminal
        """Work like Print, but end with '\r\n', not with '\n'"""

        assert CRLF == b"\r\n"

        alt_kwargs = dict(kwargs)
        if ("end" not in kwargs) or (kwargs["end"] is None):
            alt_kwargs["end"] = "\r\n"

        print(*args, **alt_kwargs)

    def write(self, bytes_):
        """Write some Bytes without encoding them, & without ending the Line"""

        fd = self.fd
        os.write(fd, bytes_)

    def flush(self):  # todo: not much tested
        """Flush the Output Buffer without waiting for the Line to end"""

        stdio = self.stdio
        stdio.flush()

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

    def try_me(self):
        """Run a quick thorough self-test"""

        self.write(b"")  # tests 'os.write'
        self.kbhit(0)  # tests 'select.select'


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


_ = r"""  # up towards demo of reduce Python to Color Python

TODO: success in arrow excuses repeat in that direction from bell

TODO: fail ⇧C ⇧D ⇧S and such at Bottom of Screen

Y should be Y $ not Y Y
as per Vim:  help Y

--

assert b"\x1B[K" etc eq their Ecma names

--

un-BEL when we do know Cursor Position because we moved absolutely

abs row known for ⇧H ⇧M ⇧L
abs column known for | 0 $
abs column known for ⇧S CC DD

rel row/column known for H J K L
rel row/column known for ⇧C ⇧D ⇧R ⇧S ⇧X CC DD A I R S X

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

DSR CPR fetch Cursor
take Cursor Row for Status Row
⎋[y;xH ⎋[K update Status Row

trace what people do to grow the sparse Area of known Screen
notice when they move the Status Row

save it as a 'vi.typescript' File of Color etc,
with no movement except as needed to leap over sparse gaps

help people bold the un-sparse, like to know when they've traced over it all

--

test \n \r \r\n bytes inside macOS Paste Buffer

echoed as digits
then as ⎋ [ digits ; digits ;

less pain here from tides forcing auto-wrapped searches and auto-cancelled searches

jump to color

copy in older Vi dreams from:  demos/vi1.py, futures.md, etc

--

add patch on the side to test random match to real Vi

"""


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/vi2.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
