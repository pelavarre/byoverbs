#!/usr/bin/env python3

r"""
usage: keycaps.py [-h]

fire key caps bright when struck, fade to black, then grey, then gone

options:
  -h, --help  show this help message and exit

quirks:
  reacts complexly to
  + CapsLock, Control, Fn, ⌥ Option Alt, & ⌘ Command keys for shifting keys
  + Option Grave and Option E I N U keys for prefixing other keys
  + Terminal > Preferences > Profiles > Keyboard > Use Option As Meta
  + pressing ⌃ ⌥ Space to change System Preferences > Keyboard > Input Sources
  + pressing Key Caps that work outside, such as ⇧ by itself, or F11 in place of ⌥ F6

examples:
  open https://shell.cloud.google.com/?show=terminal  # if you need another Linux
  git clone https://github.com/pelavarre/byoverbs.git
  demos/keycaps.py  # show these examples
  demos/keycaps.py --  # show a fireplace of key caps bright when struck, then fading
  for C in 36 32 33 35 31 34 30 37; do printf "\e[${C}m""color""\e[0m\n"; done
  # colors text as:  color color color color color color color color
"""  # note: COLOR_AS mutates this __main__.__doc__ far below

# code reviewed by people, and by Black and Flake8
# developed by:  F=demos/keycaps.py && black $F && flake8 $F && $F --


import __main__
import argparse
import collections
import datetime as dt
import difflib
import hashlib
import os
import pdb
import random
import re
import select  # defined in Windows only for Sockets, not also for Keyboards
import string
import sys
import textwrap
import time
import types

termios: types.ModuleType | None
tty: types.ModuleType | None

try:
    import termios
    import tty
except ImportError:
    termios = None
    tty = None

    import msvcrt

_ = time

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace  # needed till Jun/2018 Python 3.7


__version__ = "2025.2.17"  # Monday


#
# Name many Spells of the Terminal Output Magic: the spells tested here, and more
#
#   https://en.wikipedia.org/wiki/ANSI_escape_code
#   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
#


CSI = "\x1b["  # macOS Terminal takes "\x1B[" as CSI, doesn't take "\N{CSI}" == "\x9B"

CUP_Y_X = "\x1b[{};{}H"  # Cursor Position (CUP)  # from upper left "\x1B[1;1H"

DECTCEM_CURSOR_HIDE = "\x1b[?25l"  # Hide away the one Cursor on Screen
DECTCEM_CURSOR_SHOW = "\x1b[?25h"  # Show the one Cursor on Screen

HOME_AND_WIPE = "\x1b[H" "\x1b[2J"  # Wipe Screen with Spaces, warp Cursor into Top Left
CLEAR = "\x1b[H" "\x1b[2J" "\x1b[3J"  # Like Home and Wipe, but also clear Scrollback
# doc'ed as "Erase in Display", "Clear Entire Screen"
# some Terminals don't need the "\x1B[H" before "\x1B[2J"
# some Linux Clear's echo $'\x1B[H\x1B[3J\x1B[2J', which doesn't always clear Scrollback

OS_PUT_TERMINAL_SIZE_Y_X = "\x1b[8;{};{}t"  # "CSI 8 t" to Resize Chars per Window
# such as "\x1B[8;50;89t" for a Black-styled Python Terminal


MAC_PASTE_CHUNK_1022 = 1022
MAC_PASTE_125MS = 125e-3


NO_COLOR = 0

COLOR_CHARS_FORMAT = "\x1b[{}m{}\x1b[0m"  # .format(color, chars)
# todo: might should color "\x20" Spaces

_36_CYAN = 36
_32_GREEN = 32
_33_YELLOW = 33
_35_MAGENTA = 35  # a Pink, if you ask me
_31_RED = 31
_34_BLUE = 34
_30_BLACK = 30
_37_WHITE = 37  # a White so Off that you might should call it Grey

COLOR_BY_AGE = (36, 32, 33, 35, 31, 34, 30, 37)
# Ansi Colors = Cyan, Green, Yellow, Magenta, Red, Blue, Black, White
# but their Yellow, Magenta, White come to me as Gold, Pink, Grey

COLORS = list(COLOR_BY_AGE)
STR_COLORS = ", ".join("\x1b[{}m#{}\x1b[0m".format(_, _) for _ in COLOR_BY_AGE)

COLOR_500MS = 500e-3  # milliseconds of Key Cap life per color

assert len(COLOR_BY_AGE) == 8, len(COLOR_BY_AGE)
COLOR_AS = " ".join("\x1b[{}m{}\x1b[0m".format(_, "color") for _ in COLOR_BY_AGE)
assert __main__.__doc__, (__main__.__doc__,)
__main__.__doc__ = __main__.__doc__.replace(8 * " color", " " + COLOR_AS)

BRIGHT_COLORS = (37, 36, 32, 33, 35, 31, 34, 30)
BRIGHT_THEME_COLOR_BY_AGE = tuple(_ for _ in COLOR_BY_AGE if _ not in BRIGHT_COLORS)

DARK_COLORS = (30, 35, 34, 31, 36, 32, 33, 37)  # esp Magenta in Browsers
DARK_THEME_COLOR_BY_AGE = tuple(_ for _ in COLOR_BY_AGE if _ not in DARK_COLORS)


#
# Run from the Sh command line
#


def main():
    """Run from the Sh command line"""

    parse_keycaps_py_args_else()  # prints helps and exits, else returns args
    stdio_has_tui_else(sys.stderr)

    keycaps_plot.t_by_keycap = dict()
    keycaps_plot.plotted = str()

    run_fireplace()


def run_fireplace():
    """Fire key caps bright when struck, fade to black, then grey, then gone"""

    # Greet people

    print()
    print("Beware of CapsLock changing your Keyboard Input Byte Codes")
    print("Beware of ⌃ ⌥ Space or ⌃ ⌥ ⇧ Space changing your Keyboard Input Source")
    print("Beware of F11's toggle moving your Terminal Windows, try ⌥ F6 instead")

    print()
    print("Type faster or slower to see more of {} colors:  {}".format(len(COLORS), STR_COLORS))

    print()

    # Run with keystrokes forwarded when they occur, don't wait for more

    t1 = dt.datetime.now()

    with tui_open(sys.stderr) as tui:
        quit_strokes = list()
        while True:
            prompt = "    -- Press the same Keystroke 3 times to quit --"

            # Prompt and read the next one or two Strokes

            t2 = t1

            t0 = dt.datetime.now()
            stroke = tui.readline(prompt)
            t1 = dt.datetime.now()

            quit_strokes.append(stroke)

            # Pick out which Key Caps might have been struck to form the Stroke

            default_empty = list()
            keycaps = KEYCAP_LISTS_BY_STROKE.get(stroke, default_empty)

            # Print the Stroke, and print the Board of Key Caps if Key Caps found

            if keycaps:
                tui.print()

            tui_stroke_print(tui, stroke=stroke, t0=t0, t1=t1, t2=t2, keycaps=keycaps)

            if keycaps:
                tui.print()
                keycaps_plot(keycaps, t1=t1)
                tui_keycaps_print(tui, keycaps=keycaps, stroke=stroke, t1=t1)
                tui.print()

            # Quit after the 3rd Copy of any 1 Stroke coming slowly from fingers

            t1t0 = (t1 - t0).total_seconds() * 1000
            if t1t0 < 100:  # Don't quit while holding down a Key Cap to repeat
                quit_strokes.clear()

            if quit_strokes[-3:] == (3 * [stroke]):
                break


def tui_stroke_print(tui, stroke, t0, t1, t2, keycaps):
    """Print the Stroke itself"""

    # Measure time

    t0t2 = (t0 - t2).total_seconds() * 1000  # time from last block to this block
    t1t0 = (t1 - t0).total_seconds() * 1000  # time lost in this block

    # Choose a hex representation of Bytes

    def hexlify(encoded):
        decoded = encoded.hex().upper()
        decoded = "x " + " ".join(
            "{}{}".format(_[0], _[-1]) for _ in zip(decoded[0::2], decoded[1::2])
        )

        return decoded

    # Trace the Stroke itself

    stroke_chars = stroke.decode(errors="SurrogateEscape")
    stroke_rep = chars_encode_repr(stroke_chars).replace(r"\x1B", r"\e")

    hexxed = hexlify(stroke)

    str_t1t0 = "{:,}".format(int(t1t0)).replace(",", "_")
    str_t0t2 = "{:,}".format(int(t0t2)).replace(",", "_")

    assert MAX_LEN_KEY_CAPS_STROKE_6 == 6 < 10
    if len(stroke) <= 10:
        tui.print(
            "{}  {} {} ({})  {} {} ms".format(
                keycaps,
                len(stroke),
                stroke_rep,
                hexxed,
                str_t0t2,
                str_t1t0,
            )
        )

        return

    hasher = hashlib.md5()
    hasher.update(stroke)
    encoded = hasher.digest()

    alt_rep = encoded[:3].hex().upper()

    hexxed_0 = hexlify(stroke[:3])
    hexxed_1 = hexlify(stroke[-3:])
    alt_hexxed = "{} ... {}".format(hexxed_0, hexxed_1)

    tui.print(
        "{}  {} {} ({})  {} {} ms".format(
            keycaps, len(stroke), alt_rep, alt_hexxed, str_t0t2, str_t1t0
        )
    )


def keycaps_plot(keycaps, t1):
    """Plot the Keyboard of Key Caps"""

    DENT = "    "

    t_by_keycap = keycaps_plot.t_by_keycap

    # Keep the Time Last Struck for each single Key Cap

    for keycap_list in keycaps:
        for keycap in keycap_list.split():
            t_by_keycap[keycap] = t1

    # Form a Board of Keycaps to print

    was_plotted = keycaps_plot.plotted

    plottable = textwrap.dedent(MACBOOK_KEYCAP_CHARS).strip()
    plottable = "\n".join(_ for _ in plottable.splitlines() if _)

    indexable = "\n".join((DENT + _ + DENT) for _ in plottable.splitlines())

    # Add the fresh Key Caps

    plotted = "\n".join((len(_) * " ") for _ in indexable.splitlines())
    if was_plotted:
        plotted = was_plotted

    for keycap_list in keycaps:
        for keycap in keycap_list.split():
            whole = " " + keycap + " "

            start = 0
            while True:
                find = indexable.find(whole, start)
                if find < 0:
                    break

                start = find + len(whole)
                plotted = plotted[:find] + whole + plotted[start:]

    # Succeed

    keycaps_plot.plotted = plotted


def tui_keycaps_print(tui, keycaps, stroke, t1):
    """Plot the Keyboard of Key Caps"""

    plotted = keycaps_plot.plotted
    t_by_keycap = keycaps_plot.t_by_keycap

    # Mutate and color the Board

    now = dt.datetime.now()
    lines = list()
    for line in plotted.splitlines():
        chars = line.rstrip()

        emits = list()
        splits = re.split(r"([ ]+)", string=chars)
        for split in splits:
            emit = split
            if split.strip():
                keycap = split
                t = t_by_keycap[keycap]
                emit = colorize(keycap, t=t, now=now)
            emits.append(emit)

        emitting = "".join(emits).rstrip()

        lines.append(emitting)

    # Drop the blank Lines above and below the colored Key Caps

    while lines and not lines[0]:
        lines.pop(0)

    while lines and not lines[-1]:
        lines.pop(-1)

    # Print the Lines of colored Key Caps

    for line in lines:
        tui.print(line)


def colorize(keycap, t, now):
    """Choose a Color for the Key Cap, else replace it with Spaces"""

    assert tuple(COLOR_BY_AGE) == (36, 32, 33, 35, 31, 34, 30, 37)
    assert COLOR_500MS == 500e-3

    # Measure the age of the last Stroke of this Key Cap

    nowt = now - t
    timeout = COLOR_500MS
    age = int(nowt.total_seconds() / timeout)

    # Replace with Spaces after awhile

    if age not in range(len(COLOR_BY_AGE)):
        emit = len(keycap) * " "

        return emit

    # Fire bright when struck, fade to black, then grey, then gone

    assert NO_COLOR == 0
    assert COLOR_CHARS_FORMAT == "\x1b[{}m{}\x1b[0m"

    color = COLOR_BY_AGE[age]
    emit = COLOR_CHARS_FORMAT.format(color, keycap)

    return emit


#
# Sketch the Keyboard of a MacBook Pro (Retina, 15-inch, Mid 2015)
#


# Draw the Keyboard as 6.5 Rows of 49 Columns of Chars

MACBOOK_KEYCAP_CHARS = r"""

    Esc F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12

    `    1  2  3  4  5  6  7  8  9  0   -   =  Delete

    Tab   Q  W  E  R  T  Y  U  I  O  P  [  ]  \

           A  S  D  F  G  H  J  K  L  ;  '  Return

    ⇧       Z  X  C  V  B  N  M  ,  .  /         ⇧
    Fn  ⌃  ⌥  ⌘                  ⌘   ⌥      ↑
                  Space                   ← ↓ →

"""

MACBOOK_PASTE_KEYCAPS = "⇧ ↑ Fn ⌃ ⌥ ⌘ ← ↓ →".split()

MAC_ACCENTUATORS = b"\x60 \xc2\xb4 \xcb\x86 \xcb\x9c \xc2\xa8".split()  # E I N U Grave


# List the Punctuation Marks found by Chords of Shift plus a Key Cap

_KEYCAPS_0 = "`1234567890-=" "[]\\" ";'" ",./"  # unshifted
_KEYCAPS_1 = "~!@#$%^&*()_+" "{}|" ':"' "<>?"  # shifted


# List all the Key Caps

KEYCAPS = sorted(MACBOOK_KEYCAP_CHARS.split())


# List the Lists of Chords of Key Caps found as Byte Strings,
# but speak in terms of ⌃ ⌥ ⇧ ⌘ also known as Control Alt-Option Shift Command,
# and speak in terms of F also known as Fn

KEYCAP_LISTS_BY_STROKE = dict()

assert string.ascii_uppercase == "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

for CH_ in string.ascii_uppercase:  # Control, or Control Option, of English Letter
    S_ = chr(ord(CH_) ^ 0x40).encode()
    KEYCAP_LISTS_BY_STROKE[S_] = ["⌃ {}".format(CH_), "⌃ ⌥ {}".format(CH_)]
    if CH_ not in "BF":
        KEYCAP_LISTS_BY_STROKE[S_] += ["⌃ ⌥ ⇧ {}".format(CH_)]

for _KC1 in _KEYCAPS_1:  # Shift of Key Cap for the Key Caps that aren't English Letters
    _KC0 = _KEYCAPS_0[_KEYCAPS_1.index(_KC1)]
    KEYCAP_LISTS_BY_STROKE[_KC1.encode()] = ["⇧ {}".format(_KC0)]

for _KC in KEYCAPS:  # Key Caps of the Keyboard that aren't Multiletter Words
    _XXS = _KC.lower().encode()
    if len(_XXS) == 1:
        KEYCAP_LISTS_BY_STROKE[_XXS] = [_KC]

        if _KC.upper() != _KC.lower():  # Shift of English Letter
            KEYCAP_LISTS_BY_STROKE[_KC.encode()] = ["⇧ {}".format(_KC)]

CHORDS = ["", "⌃", "⌥", "⇧", "⌃ ⌥", "⌃ ⇧", "⌥ ⇧", "⌃ ⌥ ⇧"]

_8_DELETES = list("{} Delete".format(_).strip() for _ in CHORDS)

_11_ESCAPES = ["⌃ [", "⌃ ⌥ [", "⌃ ⌥ ⇧ ["]
_11_ESCAPES += list("{} Esc".format(_).strip() for _ in CHORDS)

_7_TABS = ["⌃ I", "⌃ ⌥ I", "⌃ ⌥ ⇧ I"]
_7_TABS += list("{} Tab".format(_).strip() for _ in ["", "⌃", "⌥", "⌃ ⌥"])

_11_RETURNS = ["⌃ M", "⌃ ⌥ M", "⌃ ⌥ ⇧ M"]
_11_RETURNS += list("{} Return".format(_).strip() for _ in CHORDS)

KEYCAP_LISTS_BY_STROKE.update(  # more Printable Ascii
    {
        b"\x20": ["Space", "⇧ Space"],
        b"\x5c": ["\\", "⌥ Y"],  # ⌥ Y is \ in place of ¥, when inside Terminal
        b"\x60": ["`", "⌥ `", "⌥ ⇧ `", "⌥ ` Space"],  # Backtick, ⌥ Grave, etc
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # more Control C0 Ascii at Mac
    {
        b"\x00": [
            "⌃ Space",
            "⌃ ⌥ Space",
            "⌃ ⇧ Space",
            "⌃ ⌥ ⇧ Space",
            "⌃ ⇧ 2",
            "⌃ ⌥ ⇧ 2",
        ],  # near to ⇧2 for @
        b"\x09": _7_TABS,  # drawn as ⇥
        b"\x0d": _11_RETURNS,  # drawn as ↩
        b"\x1b": _11_ESCAPES,  # drawn as ⎋
        b"\x1b\x5b\x5a": ["⇧ Tab", "⌃ ⇧ Tab", "⌥ ⇧ Tab", "⌃ ⌥ ⇧ Tab"],  # drawn as ⇥
        b"\x1c": ["⌃ \\", "⌃ ⌥ \\", "⌃ ⌥ ⇧ \\"],
        b"\x1d": ["⌃ ]", "⌃ ⌥ ]", "⌃ ⌥ ⇧ ]"],
        b"\x1e": ["⌃ ⇧ 6", "⌃ ⌥ ⇧ 6"],  # near to ⇧6 for ^
        b"\x1f": ["⌃ -", "⌃ ⌥ -", "⌃ ⇧ -", "⌃ ⌥ ⇧ -"],  # near to ⇧- for _
        b"\x7f": _8_DELETES,  # or drawn as ⌫ and ⌦
        b"\xc2\xa0": ["⌥ Space", "⌥ ⇧ Space"],
    }
)
# todo: b"\x0A" is ⌃ Enter at Windows
# todo: b"\x7F" is ⌃ Backspace at Windows

for _N in range(0x80):  # require all the b"\x00"..b"\x7F" Ascii found by Strokes
    assert chr(_N).encode() in KEYCAP_LISTS_BY_STROKE.keys(), _N

assert (0x40 ^ ord("@")) == 0x00

assert (0x40 ^ ord("\\")) == 0x1C
assert (0x40 ^ ord("]")) == 0x1D
assert (0x40 ^ ord("^")) == 0x1E
assert (0x40 ^ ord("_")) == 0x1F
assert (0x40 ^ ord("?")) == 0x7F

KEYCAP_LISTS_BY_STROKE.update(  # the Arrow Key Caps at Mac
    {
        b"\x1b\x5b\x31\x3b\x32\x43": ["⇧ →"],
        b"\x1b\x5b\x31\x3b\x32\x44": ["⇧ ←"],
        b"\x1b\x5b\x41": [
            "↑",
            "⌥ ↑",
            "⇧ ↑",
            "⌃ ⌥ ↑",
            "⌃ ⇧ ↑",
            "⌥ ⇧ ↑",
            "⌃ ⌥ ⇧ ↑",
        ],  # drawn as ▲
        b"\x1b\x5b\x42": [
            "↓",
            "⌥ ↓",
            "⇧ ↓",
            "⌃ ⌥ ↓",
            "⌃ ⇧ ↓",
            "⌥ ⇧ ↓",
            "⌃ ⌥ ⇧ ↓",
        ],  # drawn as ▼
        b"\x1b\x5b\x43": ["→", "⌃ ⌥ →", "⌃ ⇧ →", "⌥ ⇧ →", "⌃ ⌥ ⇧ →"],  # drawn as ▶
        b"\x1b\x5b\x44": ["←", "⌃ ⌥ ←", "⌃ ⇧ ←", "⌥ ⇧ ←", "⌃ ⌥ ⇧ ←"],  # drawn as ◀
        b"\x1b\x62": ["⌥ ←"],
        b"\x1b\x66": ["⌥ →"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # the Fn Key Caps at Mac
    {
        b"\x1b\x4f\x50": ["F1"],  # drawn as:  fn F1
        b"\x1b\x4f\x51": ["F2"],
        b"\x1b\x4f\x52": ["F3"],
        b"\x1b\x4f\x53": ["F4"],
        b"\x1b\x5b\x31\x35\x7e": ["F5"],
        b"\x1b\x5b\x31\x37\x7e": ["F6", "⌥ F1"],
        b"\x1b\x5b\x31\x38\x7e": ["F7", "⌥ F2"],
        b"\x1b\x5b\x31\x39\x7e": ["F8", "⌥ F3"],
        b"\x1b\x5b\x32\x30\x7e": ["F9", "⌥ F4"],
        b"\x1b\x5b\x32\x31\x7e": ["F10", "⌥ F5"],
        b"\x1b\x5b\x32\x33\x7e": ["F11", "⌥ F6"],
        b"\x1b\x5b\x32\x34\x7e": ["F12", "⌥ F7"],
        b"\x1b\x5b\x32\x35\x7e": ["⌥ F8", "⇧ F5"],
        b"\x1b\x5b\x32\x36\x7e": ["⌥ F9", "⇧ F6"],
        b"\x1b\x5b\x32\x38\x7e": ["⌥ F10", "⇧ F7"],
        b"\x1b\x5b\x32\x39\x7e": ["⌥ F11", "⇧ F8"],
        b"\x1b\x5b\x33\x31\x7e": ["⌥ F12", "⇧ F9"],
        b"\x1b\x5b\x33\x32\x7e": ["⇧ F10"],
        b"\x1b\x5b\x33\x33\x7e": ["⇧ F11"],
        b"\x1b\x5b\x33\x34\x7e": ["⇧ F12"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # the Option Digit strokes at Mac
    {
        b"\xc2\xba": ["⌥ 0"],
        b"\xc2\xa1": ["⌥ 1"],
        b"\xe2\x84\xa2": ["⌥ 2"],
        b"\xc2\xa3": ["⌥ 3"],
        b"\xc2\xa2": ["⌥ 4"],
        b"\xe2\x88\x9e": ["⌥ 5"],
        b"\xc2\xa7": ["⌥ 6"],
        b"\xc2\xb6": ["⌥ 7"],
        b"\xe2\x80\xa2": ["⌥ 8"],
        b"\xc2\xaa": ["⌥ 9"],
        b"\xe2\x80\x9a": ["⌥ ⇧ 0"],
        b"\xe2\x81\x84": ["⌥ ⇧ 1"],
        b"\xe2\x82\xac": ["⌥ ⇧ 2"],
        b"\xe2\x80\xb9": ["⌥ ⇧ 3"],
        b"\xe2\x80\xba": ["⌥ ⇧ 4"],
        b"\xef\xac\x81": ["⌥ ⇧ 5"],
        b"\xef\xac\x82": ["⌥ ⇧ 6"],
        b"\xe2\x80\xa1": ["⌥ ⇧ 7"],
        b"\xc2\xb0": ["⌥ ⇧ 8"],
        b"\xc2\xb7": ["⌥ ⇧ 9"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # the Option Letter strokes at Mac
    {
        b"\xc3\xa5": ["⌥ A"],
        b"\xe2\x88\xab": ["⌥ B"],
        b"\xc3\xa7": ["⌥ C"],
        b"\xe2\x88\x82": ["⌥ D"],  # not followed by ⌥ E
        b"\xc3\xa1": ["⌥ E A"],
        b"\xc3\xa9": ["⌥ E E"],
        b"\xc3\xad": ["⌥ E I"],
        b"\x6a\xcc\x81": ["⌥ E J"],
        b"\xc3\xb3": ["⌥ E O"],
        b"\xc3\xba": ["⌥ E U"],
        b"\xc6\x92": ["⌥ F"],
        b"\xc2\xa9": ["⌥ G"],
        b"\xcb\x99": ["⌥ H"],  # not followed by ⌥ I
        b"\xc3\xa2": ["⌥ I A"],
        b"\xc3\xaa": ["⌥ I E"],
        b"\xc3\xae": ["⌥ I I"],
        b"\xc3\xb4": ["⌥ I O"],
        b"\xc3\xbb": ["⌥ I U"],
        b"\xe2\x88\x86": ["⌥ J"],
        b"\xcb\x9a": ["⌥ K"],
        b"\xc2\xac": ["⌥ L"],
        b"\xc2\xb5": ["⌥ M"],  # not followed by ⌥ N
        b"\xc3\xa3": ["⌥ N A"],
        b"\xc3\xb1": ["⌥ N N"],
        b"\xc3\xb5": ["⌥ N O"],
        b"\xc3\xb8": ["⌥ O"],
        b"\xcf\x80": ["⌥ P"],
        b"\xc5\x93": ["⌥ Q"],
        b"\xc2\xae": ["⌥ R"],
        b"\xc3\x9f": ["⌥ S"],
        b"\xe2\x80\xa0": ["⌥ T"],  # not followed by ⌥ U
        b"\xc3\xa4": ["⌥ U A"],
        b"\xc3\xab": ["⌥ U E"],
        b"\xc3\xaf": ["⌥ U I"],
        b"\xc3\xb6": ["⌥ U O"],
        b"\xc3\xbc": ["⌥ U U"],
        b"\xc3\xbf": ["⌥ U Y"],
        b"\xe2\x88\x9a": ["⌥ V"],
        b"\xe2\x88\x91": ["⌥ W"],
        b"\xe2\x89\x88": ["⌥ X"],
        b"\xce\xa9": ["⌥ Z"],
        b"\xc3\x85": ["⌥ ⇧ A"],
        b"\xc4\xb1": ["⌥ ⇧ B"],
        b"\xc3\x87": ["⌥ ⇧ C"],
        b"\xc3\x8e": ["⌥ ⇧ D"],
        b"\xc2\xb4": ["⌥ E", "⌥ ⇧ E", "⌥ ⇧ E Space"],
        b"\xc3\x8f": ["⌥ ⇧ F"],
        b"\xcb\x9d": ["⌥ ⇧ G"],
        b"\xc3\x93": ["⌥ ⇧ H"],
        b"\xcb\x86": ["⌥ I", "⌥ ⇧ I", "⌥ ⇧ I Space"],
        b"\xc3\x94": ["⌥ ⇧ J"],
        b"\xef\xa3\xbf": ["⌥ ⇧ K"],
        b"\xc3\x92": ["⌥ ⇧ L"],
        b"\xc3\x82": ["⌥ ⇧ M"],
        b"\xcb\x9c": ["⌥ N", "⌥ ⇧ N", "⌥ ⇧ N Space"],
        b"\xc3\x98": ["⌥ ⇧ O"],
        b"\xe2\x88\x8f": ["⌥ ⇧ P"],
        b"\xc5\x92": ["⌥ ⇧ Q"],
        b"\xe2\x80\xb0": ["⌥ ⇧ R"],
        b"\xc3\x8d": ["⌥ ⇧ S"],
        b"\xcb\x87": ["⌥ ⇧ T"],
        b"\xc2\xa8": ["⌥ U", "⌥ ⇧ U", "⌥ ⇧ U Space"],
        b"\xe2\x97\x8a": ["⌥ ⇧ V"],
        b"\xe2\x80\x9e": ["⌥ ⇧ W"],
        b"\xcb\x9b": ["⌥ ⇧ X"],
        b"\xc3\x81": ["⌥ ⇧ Y"],
        b"\xc2\xb8": ["⌥ ⇧ Z"],
        b"\xc3\xa0": ["⌥ ` A"],
        b"\xc3\xa8": ["⌥ ` E"],
        b"\xc3\xac": ["⌥ ` I"],
        b"\xc3\xb2": ["⌥ ` O"],
        b"\xc3\xb9": ["⌥ ` U"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # the Option Punctuation-Mark strokes at Mac
    {
        b"\xe2\x80\x93": ["⌥ -"],
        b"\xe2\x89\xa0": ["⌥ ="],
        b"\xe2\x80\x9c": ["⌥ ["],
        b"\xe2\x80\x98": ["⌥ ]"],
        b"\xc2\xab": ["⌥ \\"],
        b"\xe2\x80\xa6": ["⌥ ;"],
        b"\xc3\xa6": ["⌥ '"],
        b"\xe2\x89\xa4": ["⌥ ,"],
        b"\xe2\x89\xa5": ["⌥ ."],
        b"\xc3\xb7": ["⌥ /"],
        b"\xe2\x80\x94": ["⌥ ⇧ -"],
        b"\xc2\xb1": ["⌥ ⇧ ="],
        b"\xe2\x80\x9d": ["⌥ ⇧ ["],
        b"\xe2\x80\x99": ["⌥ ⇧ ]"],
        b"\xc2\xbb": ["⌥ ⇧ \\"],
        b"\xc3\x9a": ["⌥ ⇧ ;"],
        b"\xc3\x86": ["⌥ ⇧ '"],
        b"\xc2\xaf": ["⌥ ⇧ ,"],
        b"\xcb\x98": ["⌥ ⇧ ."],
        b"\xc2\xbf": ["⌥ ⇧ /"],
    }
)


def require_keycap_lists_sorted():
    """Require Chords in each KeyCap List sorted by '', '⌃', '⌥', '⇧', '⌃ ⌥', etc"""

    stroke_by_keycap_tuple = dict()

    for stroke, keycap_list in KEYCAP_LISTS_BY_STROKE.items():
        assert isinstance(keycap_list, list), repr(keycap_list)

        # Require Chords sorted by '', '⌃', '⌥', '⇧', '⌃ ⌥', etc - per Apple Standard

        chord_by_cap = collections.defaultdict(list)
        for keycap in keycap_list:
            assert isinstance(keycap, str), repr(keycap)

            splits = keycap.split()
            chord = " ".join(splits[:-1])
            cap = splits[-1]

            if chord not in CHORDS:
                assert splits[0] == "⌥", splits

                continue  # shrug off "⌥ ` Space", "⌥ E E", etc

            chord_by_cap[cap].append(chord)

        for cap, chords in chord_by_cap.items():
            indices = list(CHORDS.index(_) for _ in chords)
            assert indices == sorted(indices), (keycap_list, indices)

        # Require no Alt Encodings till later

        for keycap in keycap_list:
            splits = keycap.split()

            keycap_tuple = tuple(splits)
            assert keycap_tuple not in stroke_by_keycap_tuple.keys(), repr(keycap)
            stroke_by_keycap_tuple[keycap_tuple] = stroke


require_keycap_lists_sorted()


KEYCAP_LISTS_BY_STROKE.update(  # Control C0 Ascii at Windows
    {
        b"\x00\x03": ["⌃ ⇧ 2"],
        b"\x00\x94": ["⌃ Tab"],
        b"\x00\x95": ["⌃ /"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # the Arrow Key Caps at Windows
    {
        b"\xe0\x48": ["↑"],  # drawn as ▲
        b"\xe0\x4b": ["←"],  # drawn as ◀
        b"\xe0\x4d": ["→"],  # drawn as ▶
        b"\xe0\x50": ["↓"],  # drawn as ▼
        b"\xe0\x73": ["⌃ ←"],
        b"\xe0\x74": ["⌃ →"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # some of the Extra Key Caps at Windows
    {
        b"\x00\x76": ["⌃ PgDn"],
        b"\x00\x84": ["⌃ PgUp"],
        b"\xe0\x47": ["Home"],
        b"\xe0\x49": ["PgUp"],
        b"\xe0\x4f": ["End"],
        b"\xe0\x51": ["PgDn"],
        b"\xe0\x76": ["⌃ PgDn"],
        b"\xe0\x86": ["⌃ PgUp"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # more of the Extra Key Caps at Windows
    {
        b"\xe0\x52": ["Ins"],
        b"\xe0\x53": ["Del"],
        b"\xe0\x92": ["⌃ Ins"],
        b"\xe0\x93": ["⌃ Del"],
    }
)

# todo: KeyboardInterrupt can be Fn B at Windows?


for _KC in MACBOOK_PASTE_KEYCAPS:
    _KB = _KC.encode()
    assert _KB not in KEYCAP_LISTS_BY_STROKE.keys(), _KB
    KEYCAP_LISTS_BY_STROKE[_KB] = [_KC]  # adds Alt Encodings of ↑ ← ↓ →

MAX_LEN_KEY_CAPS_STROKE_6 = max(len(_) for _ in KEYCAP_LISTS_BY_STROKE.keys())
assert MAX_LEN_KEY_CAPS_STROKE_6 == 6, MAX_LEN_KEY_CAPS_STROKE_6


#
# Take Words from the Sh Command Line into KeyCaps Py
#


def parse_keycaps_py_args_else():
    """Print helps for Keycaps Py and exit zero or nonzero, else return args"""

    # Drop the '--' Separator if present, even while declaring no Pos Args

    sys_parms = sys.argv[1:]
    if sys_parms == ["--"]:
        sys_parms = list()

    # Parse the Sh Command Line, or show Help

    parser = compile_keycaps_argdoc_else()
    args = parser.parse_args(sys_parms)  # prints helps and exits, else returns args
    if not sys.argv[1:]:
        doc = __main__.__doc__

        exit_via_testdoc(doc, epi="examples")  # exits because no args

    # Succeed

    return args


def compile_keycaps_argdoc_else():
    """Form an ArgumentParser for KeyCaps Py"""

    doc = __main__.__doc__
    parser = compile_argdoc(doc, epi="quirks")
    try:
        sys_exit_if_argdoc_ne(doc, parser=parser)
    except SystemExit:
        sys_stderr_print("keycaps.py: ERROR: main doc and argparse parser disagree")

        raise

    return parser


#
# Layer over Import ArgParse
#


def compile_argdoc(doc, epi):
    """Form an ArgumentParser, without defining Positional Args and Options"""

    doc_lines = doc.strip().splitlines()
    prog = doc_lines[0].split()[1]  # second word of first line

    doc_firstlines = list(_ for _ in doc_lines if _ and (_ == _.lstrip()))
    description = doc_firstlines[1]  # first line of second paragraph

    epilog_at = doc.index(epi)
    epilog = doc[epilog_at:]

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=True,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    return parser


def sys_exit_if_argdoc_ne(doc, parser):
    """Complain and exit nonzero, unless Arg Doc equals Parser Format_Help"""

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

    got = main_doc
    want = parser_doc

    diff_lines = list(
        difflib.unified_diff(
            a=got.splitlines(),
            b=want.splitlines(),
            fromfile=got_filename,
            tofile=want_filename,
        )
    )

    if diff_lines:
        sys_stderr_print("\n".join(diff_lines))

        sys.exit(2)  # trust caller to log SystemExit exceptions well


def exit_via_testdoc(doc, epi):
    """Print the last Paragraph of the Main Arg Doc"""

    testdoc = doc
    testdoc = testdoc[testdoc.index(epi) :]
    testdoc = "\n".join(testdoc.splitlines()[1:])
    testdoc = textwrap.dedent(testdoc)
    testdoc = testdoc.strip()

    print()
    print(testdoc)
    print()

    sys.exit(0)


def sys_stderr_print(*args, **kwargs):
    """Work like Print, but write Sys Stderr in place of Sys Stdout"""

    kwargs_ = dict(kwargs)
    if "file" not in kwargs.keys():
        kwargs_["file"] = sys.stderr

    sys.stdout.flush()

    print(*args, **kwargs_)

    if "file" not in kwargs.keys():
        sys.stderr.flush()


#
# Layer over Class Bytes and Class Str
#


def chars_encode_repr(chars):
    r"""Repr of the Encode of Chars, except \a \b \e \f for those"""

    if chars == "'":
        rep = '"{}"'.format(chars)  # the three chars " ' "

        return rep

    rep = "".join(ch_encode_repr(_) for _ in chars)
    rep = "b'{}'".format(rep)

    return rep


def ch_encode_repr(ch):
    r"""Repr of the Encode of Ch, except \a \b \e \f for those"""

    #

    c0c1s = list(range(0x00, 0x20)) + [0x7F] + list(range(0x80, 0xA0))
    c0c1s += [0xA0, 0xDA]
    c0c1_set = set(c0c1s)

    encodables = r"\abeftrn"
    encoded = b"\\\a\b\x1b\f\t\r\n"

    assert len(encodables) == len(encoded), (len(encodables), len(encoded))

    #

    assert len(ch) == 1, repr(ch)

    ord_ch = ord(ch)
    xxs = ch.encode()

    index = encoded.find(xxs)

    if index >= 0:
        rep = r"\{}".format(encodables[index])
    elif ord_ch in c0c1_set:
        rep = r"\x{:02X}".format(ord_ch)
    else:
        rep = ch

    return rep


#
# Layer over Import Termios and Import Tty
#


def stdio_has_tui_else(stdio):
    """Fail-fast when not run from a Text User Interface (TUI) Terminal"""

    try:
        with tui_open(stdio):
            pass
    except Exception as exc:
        sys_stderr_print("Traceback (most recent call last):")
        sys_stderr_print("  ...")
        sys_stderr_print("{}: {}".format(type(exc).__name__, exc))

        sys_stderr_print()
        sys_stderr_print("Run this code inside a Terminal, such as a Windows Dos Box")

        sys.exit(1)


def tui_open(stdio):
    """Accept such usage as 'with tui_open(sys.stderr):'"""

    tui = TextUserInterface(stdio)

    return tui


class TextUserInterface:  # FIXME work in Windows too, not just in Mac and Linux
    r"""
    Emulate a Glass Teletype at Stdio, such as the 1978 DEC VT100 Video Terminal

    Apply Terminal Input Magic to read ⌃@ ⌃C ⌃D ⌃J ⌃M ⌃Q ⌃S ⌃T ⌃Z ⌃\ etc as themselves,
    not as NUL SIGINT EOF LF CR SIGCONT SIGSTOP SIGINFO SIGTSTP SIGQUIT etc

    Compare Bash 'stty -a' and 'bind -p', Zsh 'bindkey', Unicode.Org Pdf U+0000
    """

    # stty -a |tr -d ' \t' |tr ';' '\n' |grep '=^' |sort

    def __init__(self, stdio):
        """Work at Sys Stderr, or elsewhere"""

        self.fd = stdio.fileno()  # File Descriptor of Keyboard, for Os Read
        self.stdio = stdio  # File Stream of Keyboard, for IsATty and Flush
        self.tcgetattr = None  # Configuration of Terminal at Entry

        self.line = None  # the 2nd Keystroke that came in with a 1st Keystroke

        self.entries = 0  # count calls of 'def __enter__'

    def __enter__(self):
        """Flush, then start taking Keystrokes literally & writing Lf as itself"""

        self.entries += 1

        fd = self.fd
        tcgetattr = self.tcgetattr
        stdio = self.stdio

        # Flush output before changing buffering

        stdio.flush()

        # Stop line-buffering input, or leave it stopped

        if termios:
            if stdio.isatty() and (tcgetattr is None):
                tcgetattr = termios.tcgetattr(fd)
                assert tcgetattr is not None

                self.tcgetattr = tcgetattr

                tty.setraw(fd, when=termios.TCSADRAIN)  # not TCSAFLUSH

                # todo: show that queued input survives

        # Succeed

        tui = self

        return tui

    def __exit__(self, *exc_info):
        """Flush, then stop taking Keystrokes literally & start writing Lf as Cr Lf"""

        _ = exc_info

        fd = self.fd
        tcgetattr = self.tcgetattr
        stdio = self.stdio

        # Flush output before changing buffering

        stdio.flush()

        # Compile-time option to flush input too

        assert MAC_PASTE_CHUNK_1022 == 1022

        if True:  # last jittered Sat 12/Nov/2022
            if not termios:
                while msvcrt.kbhit():
                    strokes = msvcrt.getch()
                    if strokes in (b"\x00", b"\xe0"):
                        strokes += msvcrt.getch()

            if termios:
                length = MAC_PASTE_CHUNK_1022
                while self.kbhit(timeout=0):
                    _ = os.read(fd, length)

        # Start line-buffering input, or leave it started

        if termios:
            if tcgetattr is not None:
                self.tcgetattr = None  # mutate

                when = termios.TCSADRAIN
                # when = termios.TCSAFLUSH  # todo: find a test that cares
                termios.tcsetattr(fd, when, tcgetattr)

    def print(self, *args, **kwargs):
        """Like Print, but default End to "\r\n" of Tui, not "\n" of Terminal"""

        kwargs_ = dict(kwargs)
        if "end" not in kwargs.keys():
            kwargs_["end"] = "\r\n"

        print(*args, **kwargs_)  # FIXME: write & flush Stderr, not Stdout?

    def cap_from_stroke(self, stroke):  # todo: test with Paste?
        """Pick the main Keycap out of 1 Keystroke"""

        default_empty = list()
        keycap_joins = KEYCAP_LISTS_BY_STROKE.get(stroke, default_empty)

        main_cap = None
        if keycap_joins:
            keycap_join = keycap_joins[0]  # such as '←' from ('←', '⌃ ⌥ ←', '⌃ ⇧ ←')
            main_cap = keycap_join.split()[-1]  # such as 'H' from '⌃ ⌥ ⇧ H'

        for keycap_join in keycap_joins:
            words = list(_ for _ in keycap_join.split() if len(_) > 1)
            if words:
                main_cap = words[0]  # such as 'Return' past '⌃ M'

                break

        return main_cap

    def readline(self, prompt=""):
        """Read the Byte Encoding of 1 Keystroke, or Paste"""

        # Immediately return a 2nd Keystroke that came in with a 1st Keystroke

        line = self.line
        if self.line:  # tested by Mac ⌥ E E ⌥ E Q, etc
            self.line = None

            return line

        # Read one Byte or a burst of Bytes = 1 or 2 Keystrokes, or Paste

        if termios:
            strokes = self.kbread_with_termios(prompt)
        else:
            strokes = self.kbread_with_msvcrt(prompt)

        chars = strokes.decode()

        # Return the 1st Keystroke that came as a pair of Accentuator plus 2nd Keystroke

        if termios:
            mac_accentuators = b"\x60 \xc2\xb4 \xcb\x86 \xcb\x9c \xc2\xa8".split()
            assert MAC_ACCENTUATORS == mac_accentuators  # Option E I N U Grave

            if len(chars) <= 2:
                for accentuator in MAC_ACCENTUATORS:
                    if strokes.startswith(accentuator):
                        line = strokes[len(accentuator) :]
                        self.line = line

                        splits = list()
                        splits.append(accentuator)
                        if line:
                            splits.append(line)

                        if prompt:
                            self.print("Os Read returned", splits)

                        return accentuator

        # Return 1 Keystroke, or Paste

        stroke = strokes

        return stroke

    def kbread_with_msvcrt(self, prompt):
        """Read one Byte or a burst of Bytes = 1 or 2 Keystrokes, or Paste"""

        assert not termios

        # Print a prompt to clear before returning

        self.kbprompt_write(prompt)
        prompted = prompt

        # Take 1 or Keystroke coming in

        strokes = msvcrt.getch()
        if strokes in (b"\x00", b"\xe0"):
            strokes += msvcrt.getch()

        # Clear the prompt

        self.kbprompt_erase(prompted)

        # Succeed

        return strokes

    def kbread_with_termios(self, prompt):
        """Read one Byte or a burst of Bytes = 1 or 2 Keystrokes, or Paste"""

        assert termios

        fd = self.fd

        assert MAC_PASTE_CHUNK_1022 == 1022
        assert MAC_PASTE_125MS == 125e-3

        # Print a prompt to clear before returning

        self.kbprompt_write(prompt)
        prompted = prompt

        # Take 1 or 2 Keystrokes coming in

        strokes = b""
        length = MAC_PASTE_CHUNK_1022
        while True:
            more = os.read(fd, length)
            assert more

            strokes += more

            # Maybe emulate 'os.read' raising an exception

            if False:  # last jittered Sat 12/Nov/2022
                assert random.randint(0, 1)

            # Spike Latency of precisely largest Paste, to catch a chance of more

            if len(more) == length:
                if self.kbhit(timeout=MAC_PASTE_125MS):
                    if len(more) == len(strokes):
                        # Clear the prompt early, to make room for Log Lines

                        self.kbprompt_erase(prompted)
                        prompted = ""

                    # Log each Fragment of Paste, before the last Fragment

                    if prompt:
                        str_count = "{:,}".format(len(more)).replace(",", "_")
                        logline = "{} bytes of Paste".format(str_count)
                        self.print(logline)

                    continue

            break

            # todo: test splitting or joining multiple strokes of ⌘ V Paste

        # Log the last Fragment of Paste

        if len(strokes) > length:
            if prompt:
                str_count = "{:,}".format(len(more) % length).replace(",", "_")
                logline = "{} bytes of Paste".format(str_count)
                self.print(logline)

        # Clear the prompt

        self.kbprompt_erase(prompted)

        # Succeed

        return strokes

        # b'\x1B[Z' for ⇧ Tab  # same bytes as CSI Z, aka Emacs BackTab
        # b'b'\x1b[1;2C' for ⇧ ←  # same bytes as Left(m=1, n=2), so doubled in row
        # b'b'\x1b[1;2D' ⇧ →  # same bytes as Right(m=1, n=2), so doubled in row
        # b'\x1B[Z' aka CSI Z for ⇧ Tab

        # b'\x1Bb' aka ⌥ B for ⌥ ←  # same bytes as Meta B, aka Emacs Backward-Word
        # b'\x1Bf' aka ⌥ F for ⌥ →  # same bytes as Meta F, aka Emacs Forward-Word

        # doubles of Option E I N U Grave send themselves and still mark a vowel
        # Option E I N U Grave before consonants send the marks themselves
        # sometimes as a pair of Keystrokes, sometimes as one and then the next

    def kbprompt_write(self, prompt):
        """Print a prompt in the Line, but leave the Cursor at the left of it"""

        if prompt:
            self.print(prompt, end="")
            sys.stdout.flush()

    def kbprompt_erase(self, prompt):
        """Erase a prompt in the Line, and leave the Cursor at the left of it"""

        if prompt:
            self.print("", end="\r")
            self.print(len(prompt) * " ", end="\r")
            sys.stdout.flush()

    def kbhit(self, timeout):  # 'timeout' in seconds
        """Wait till next Byte of Keystroke, next burst of Paste pasted, or Timeout"""

        rs_0 = [self.stdio]
        ws_0 = list()
        xs_0 = list()

        (rs_1, _, _) = select.select(rs_0, ws_0, xs_0, timeout)

        if rs_1 != rs_0:
            assert rs_1 == [], rs_1

        return rs_1

    def screen_wipe_below(self):
        """Scroll away history without dropping all of it, and print a blank screen"""

        size = self.shutil_get_terminal_size()
        for _ in range(size.lines):
            self.print()

        assert HOME_AND_WIPE == "\x1b[H" "\x1b[2J"
        self.print(HOME_AND_WIPE, end="")

        sys.stdout.flush()

    def shutil_get_terminal_size(self):
        """Run much like 'shutil.get_terminal_size', but on our File Descriptor"""

        def int_else(i, key, default):
            if i > 0:
                return i  # from 'os.get_terminal_size'

            if key in os.environ.keys():
                value = os.environ[key]
                try:
                    return int(value)  # from '123', '1_123.456', '0x80', etc

                except Exception:
                    pass

            return default

        try:
            size = os.get_terminal_size(self.fd)
        except Exception:
            size = os.terminal_size(columns=0, lines=0)

            # such as OSError: [Errno 19] Operation not supported by device

        columns = int_else(size.columns, key="COLUMNS", default=80)
        lines = int_else(size.lines, key="LINES", default=24)

        t = (columns, lines)
        size = os.terminal_size(t)

        assert size.columns == columns, (t, size)
        assert size.lines == lines, (t, size)

        return size

        # note: Python's ShUtil jumped to Not IsATty when just Stdout redirected

        _ = """

COLUMNS=1_123.456 LINES=0x80 python3 -c '''

import os, shutil, sys
sys.stderr.write(str(shutil.get_terminal_size()) + "\n")

''' >/dev/null

        """  # os.terminal_size(columns=1123, lines=128)


def try_put_terminal_size(stdio, size):
    """Write "CSI 8 t" to Resize Window in Monospace Chars"""

    flat_up = os.terminal_size(size)

    size_1 = os.get_terminal_size(stdio.fileno())
    if size_1 == flat_up:
        stdio.flush()
    else:
        print(
            OS_PUT_TERMINAL_SIZE_Y_X.format(flat_up.lines, flat_up.columns),
            end="",
            file=stdio,
        )

        stdio.flush()

        size_2 = os.get_terminal_size(stdio.fileno())
        while size_2 != flat_up:  # FIXME: time out if resize takes forever
            size_2 = os.get_terminal_size(stdio.fileno())


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# todo: rewrite the declarations of Global Variables to conform to PyLance Standard


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/demos/keycaps.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
