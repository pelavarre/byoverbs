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
  git clone https://github.com/pelavarre/byoverb.git
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
import select  # deployed in Windows only for Sockets, not also for Keyboards
import string
import sys
import textwrap
import time

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


MAC_PASTE_CHUNK_1022 = 1022
MAC_PASTE_125MS = 125e-3


NO_COLOR = 0

COLOR_CHARS_FORMAT = "\x1B[{}m{}\x1B[0m"  # .format(color, chars)
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
STR_COLORS = ", ".join("\x1B[{}m#{}\x1B[0m".format(_, _) for _ in COLOR_BY_AGE)

COLOR_500MS = 500e-3  # milliseconds of Key Cap life per color

assert len(COLOR_BY_AGE) == 8, len(COLOR_BY_AGE)
COLOR_AS = " ".join("\x1B[{}m{}\x1B[0m".format(_, "color") for _ in COLOR_BY_AGE)
__main__.__doc__ = __main__.__doc__.replace(8 * " color", " " + COLOR_AS)

BRIGHT_COLORS = (37, 36, 32, 33, 35, 31, 34, 30)
BRIGHT_THEME_COLOR_BY_AGE = tuple(_ for _ in COLOR_BY_AGE if _ not in BRIGHT_COLORS)

DARK_COLORS = (30, 35, 34, 31, 36, 32, 33, 37)  # esp Magenta in Browsers
DARK_THEME_COLOR_BY_AGE = tuple(_ for _ in COLOR_BY_AGE if _ not in DARK_COLORS)


#
# Run from the Sh command line
#


def main(sys_argv=None):
    """Run from the Sh command line"""

    parse_keycaps_py_args_else(sys_argv)  # prints helps and exits, else returns args

    require_tui()

    keycaps_plot.t_by_keycap = dict()
    keycaps_plot.plotted = str()

    run_fireplace()


def require_tui():
    """Fail-fast when not run from a Text User Interface (TUI) Terminal"""

    try:
        with tui_open(sys.stderr):
            pass
    except Exception as exc:
        sys_stderr_print("Traceback (most recent call last):")
        sys_stderr_print("  ...")
        sys_stderr_print("{}: {}".format(type(exc).__name__, exc))

        sys_stderr_print()
        sys_stderr_print("Run this code inside a Terminal, such as a Windows Dos Box")

        sys.exit(1)


def run_fireplace():
    """Fire key caps bright when struck, fade to black, then grey, then gone"""

    # Greet people

    print()
    print("Beware of CapsLock changing your Keyboard Input Byte Codes")
    print("Beware of ⌃ ⌥ Space or ⌃ ⌥ ⇧ Space changing your Keyboard Input Source")
    print("Beware of F11's toggle moving your Terminal Windows, try ⌥ F6 instead")

    print()
    print(
        "Type faster or slower to see more of {} colors:  {}".format(
            len(COLORS), STR_COLORS
        )
    )

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
            "{} {} {} ({}) {} {} ms".format(
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
    alt_hexxed = "x {} ... {}".format(hexxed_0, hexxed_1)

    tui.print(
        "{} {} {} ({}) {} {} ms".format(
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
    assert COLOR_CHARS_FORMAT == "\x1B[{}m{}\x1B[0m"

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

MAC_ACCENTUATORS = b"\x60 \xC2\xB4 \xCB\x86 \xCB\x9C \xC2\xA8".split()  # E I N U Grave


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
        b"\x5C": ["\\", "⌥ Y"],  # ⌥ Y is \ in place of ¥, when inside Terminal
        b"\x60": ["`", "⌥ `", "⌥ ⇧ `", "⌥ ` Space"],  # Backtick, ⌥ Grave, etc
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # more Control C0 Ascii at Mac
    {
        b"\x00": ["⌃ Space", "⌃ ⇧ Space", "⌃ ⇧ 2", "⌃ ⌥ ⇧ 2"],  # near to ⇧2 for @
        b"\x09": _7_TABS,  # drawn as ⇥
        b"\x0D": _11_RETURNS,  # drawn as ↩
        b"\x1B": _11_ESCAPES,  # drawn as ⎋
        b"\x1B\x5B\x5A": ["⇧ Tab", "⌃ ⇧ Tab", "⌥ ⇧ Tab", "⌃ ⌥ ⇧ Tab"],  # drawn as ⇥
        b"\x1C": ["⌃ \\", "⌃ ⌥ \\", "⌃ ⌥ ⇧ \\"],
        b"\x1D": ["⌃ ]", "⌃ ⌥ ]", "⌃ ⌥ ⇧ ]"],
        b"\x1E": ["⌃ ⇧ 6", "⌃ ⌥ ⇧ 6"],  # near to ⇧6 for ^
        b"\x1F": ["⌃ -", "⌃ ⌥ -", "⌃ ⌥ ⇧ -"],  # near to ⇧- for _
        b"\x7F": _8_DELETES,  # or drawn as ⌫ and ⌦
        b"\xC2\xA0": ["⌥ Space", "⌥ ⇧ Space"],
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
        b"\x1B\x5B\x31\x3B\x32\x43": ["⇧ →"],
        b"\x1B\x5B\x31\x3B\x32\x44": ["⇧ ←"],
        b"\x1B\x5B\x41": ["↑", "⌥ ↑", "⇧ ↑", "⌃ ⌥ ↑", "⌃ ⇧ ↑", "⌃ ⌥ ⇧ ↑"],  # drawn as ▲
        b"\x1B\x5B\x42": ["↓", "⌥ ↓", "⇧ ↓", "⌃ ⌥ ↓", "⌃ ⇧ ↓", "⌃ ⌥ ⇧ ↓"],  # drawn as ▼
        b"\x1B\x5B\x43": ["→", "⌃ ⌥ →", "⌃ ⇧ →", "⌥ ⇧ →", "⌃ ⌥ ⇧ →"],  # drawn as ▶
        b"\x1B\x5B\x44": ["←", "⌃ ⌥ ←", "⌃ ⇧ ←", "⌥ ⇧ ←", "⌃ ⌥ ⇧ ←"],  # drawn as ◀
        b"\x1B\x62": ["⌥ ←"],
        b"\x1B\x66": ["⌥ →"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # the Fn Key Caps at Mac
    {
        b"\x1B\x4F\x50": ["F1"],  # drawn as:  fn F1
        b"\x1B\x4F\x51": ["F2"],
        b"\x1B\x4F\x52": ["F3"],
        b"\x1B\x4F\x53": ["F4"],
        b"\x1B\x5B\x31\x35\x7E": ["F5"],
        b"\x1B\x5B\x31\x37\x7E": ["F6", "⌥ F1"],
        b"\x1B\x5B\x31\x38\x7E": ["F7", "⌥ F2"],
        b"\x1B\x5B\x31\x39\x7E": ["F8", "⌥ F3"],
        b"\x1B\x5B\x32\x30\x7E": ["F9", "⌥ F4"],
        b"\x1B\x5B\x32\x31\x7E": ["F10", "⌥ F5"],
        b"\x1B\x5B\x32\x33\x7E": ["F11", "⌥ F6"],
        b"\x1B\x5B\x32\x34\x7E": ["F12", "⌥ F7"],
        b"\x1B\x5B\x32\x35\x7E": ["⌥ F8", "⇧ F5"],
        b"\x1B\x5B\x32\x36\x7E": ["⌥ F9", "⇧ F6"],
        b"\x1B\x5B\x32\x38\x7E": ["⌥ F10", "⇧ F7"],
        b"\x1B\x5B\x32\x39\x7E": ["⌥ F11", "⇧ F8"],
        b"\x1B\x5B\x33\x31\x7E": ["⌥ F12", "⇧ F9"],
        b"\x1B\x5B\x33\x32\x7E": ["⇧ F10"],
        b"\x1B\x5B\x33\x33\x7E": ["⇧ F11"],
        b"\x1B\x5B\x33\x34\x7E": ["⇧ F12"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # the Option Digit strokes at Mac
    {
        b"\xC2\xBA": ["⌥ 0"],
        b"\xC2\xA1": ["⌥ 1"],
        b"\xE2\x84\xA2": ["⌥ 2"],
        b"\xC2\xA3": ["⌥ 3"],
        b"\xC2\xA2": ["⌥ 4"],
        b"\xE2\x88\x9E": ["⌥ 5"],
        b"\xC2\xA7": ["⌥ 6"],
        b"\xC2\xB6": ["⌥ 7"],
        b"\xE2\x80\xA2": ["⌥ 8"],
        b"\xC2\xAA": ["⌥ 9"],
        b"\xE2\x80\x9A": ["⌥ ⇧ 0"],
        b"\xE2\x81\x84": ["⌥ ⇧ 1"],
        b"\xE2\x82\xAC": ["⌥ ⇧ 2"],
        b"\xE2\x80\xB9": ["⌥ ⇧ 3"],
        b"\xE2\x80\xBA": ["⌥ ⇧ 4"],
        b"\xEF\xAC\x81": ["⌥ ⇧ 5"],
        b"\xEF\xAC\x82": ["⌥ ⇧ 6"],
        b"\xE2\x80\xA1": ["⌥ ⇧ 7"],
        b"\xC2\xB0": ["⌥ ⇧ 8"],
        b"\xC2\xB7": ["⌥ ⇧ 9"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # the Option Letter strokes at Mac
    {
        b"\xC3\xA5": ["⌥ A"],
        b"\xE2\x88\xAB": ["⌥ B"],
        b"\xC3\xA7": ["⌥ C"],
        b"\xE2\x88\x82": ["⌥ D"],  # not followed by ⌥ E
        b"\xC3\xA1": ["⌥ E A"],
        b"\xC3\xA9": ["⌥ E E"],
        b"\xC3\xAD": ["⌥ E I"],
        b"\x6A\xCC\x81": ["⌥ E J"],
        b"\xC3\xB3": ["⌥ E O"],
        b"\xC3\xBA": ["⌥ E U"],
        b"\xC6\x92": ["⌥ F"],
        b"\xC2\xA9": ["⌥ G"],
        b"\xCB\x99": ["⌥ H"],  # not followed by ⌥ I
        b"\xC3\xA2": ["⌥ I A"],
        b"\xC3\xAA": ["⌥ I E"],
        b"\xC3\xAE": ["⌥ I I"],
        b"\xC3\xB4": ["⌥ I O"],
        b"\xC3\xBB": ["⌥ I U"],
        b"\xE2\x88\x86": ["⌥ J"],
        b"\xCB\x9A": ["⌥ K"],
        b"\xC2\xAC": ["⌥ L"],
        b"\xC2\xB5": ["⌥ M"],  # not followed by ⌥ N
        b"\xC3\xA3": ["⌥ N A"],
        b"\xC3\xB1": ["⌥ N N"],
        b"\xC3\xB5": ["⌥ N O"],
        b"\xC3\xB8": ["⌥ O"],
        b"\xCF\x80": ["⌥ P"],
        b"\xC5\x93": ["⌥ Q"],
        b"\xC2\xAE": ["⌥ R"],
        b"\xC3\x9F": ["⌥ S"],
        b"\xE2\x80\xA0": ["⌥ T"],  # not followed by ⌥ U
        b"\xC3\xA4": ["⌥ U A"],
        b"\xC3\xAB": ["⌥ U E"],
        b"\xC3\xAF": ["⌥ U I"],
        b"\xC3\xB6": ["⌥ U O"],
        b"\xC3\xBC": ["⌥ U U"],
        b"\xC3\xBF": ["⌥ U Y"],
        b"\xE2\x88\x9A": ["⌥ V"],
        b"\xE2\x88\x91": ["⌥ W"],
        b"\xE2\x89\x88": ["⌥ X"],
        b"\xCE\xA9": ["⌥ Z"],
        b"\xC3\x85": ["⌥ ⇧ A"],
        b"\xC4\xB1": ["⌥ ⇧ B"],
        b"\xC3\x87": ["⌥ ⇧ C"],
        b"\xC3\x8E": ["⌥ ⇧ D"],
        b"\xC2\xB4": ["⌥ E", "⌥ ⇧ E", "⌥ ⇧ E Space"],
        b"\xC3\x8F": ["⌥ ⇧ F"],
        b"\xCB\x9D": ["⌥ ⇧ G"],
        b"\xC3\x93": ["⌥ ⇧ H"],
        b"\xCB\x86": ["⌥ I", "⌥ ⇧ I", "⌥ ⇧ I Space"],
        b"\xC3\x94": ["⌥ ⇧ J"],
        b"\xEF\xA3\xBF": ["⌥ ⇧ K"],
        b"\xC3\x92": ["⌥ ⇧ L"],
        b"\xC3\x82": ["⌥ ⇧ M"],
        b"\xCB\x9C": ["⌥ N", "⌥ ⇧ N", "⌥ ⇧ N Space"],
        b"\xC3\x98": ["⌥ ⇧ O"],
        b"\xE2\x88\x8F": ["⌥ ⇧ P"],
        b"\xC5\x92": ["⌥ ⇧ Q"],
        b"\xE2\x80\xB0": ["⌥ ⇧ R"],
        b"\xC3\x8D": ["⌥ ⇧ S"],
        b"\xCB\x87": ["⌥ ⇧ T"],
        b"\xC2\xA8": ["⌥ U", "⌥ ⇧ U", "⌥ ⇧ U Space"],
        b"\xE2\x97\x8A": ["⌥ ⇧ V"],
        b"\xE2\x80\x9E": ["⌥ ⇧ W"],
        b"\xCB\x9B": ["⌥ ⇧ X"],
        b"\xC3\x81": ["⌥ ⇧ Y"],
        b"\xC2\xB8": ["⌥ ⇧ Z"],
        b"\xC3\xA0": ["⌥ ` A"],
        b"\xC3\xA8": ["⌥ ` E"],
        b"\xC3\xAC": ["⌥ ` I"],
        b"\xC3\xB2": ["⌥ ` O"],
        b"\xC3\xB9": ["⌥ ` U"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # the Option Punctuation-Mark strokes at Mac
    {
        b"\xE2\x80\x93": ["⌥ -"],
        b"\xE2\x89\xA0": ["⌥ ="],
        b"\xE2\x80\x9C": ["⌥ ["],
        b"\xE2\x80\x98": ["⌥ ]"],
        b"\xC2\xAB": ["⌥ \\"],
        b"\xE2\x80\xA6": ["⌥ ;"],
        b"\xC3\xA6": ["⌥ '"],
        b"\xE2\x89\xA4": ["⌥ ,"],
        b"\xE2\x89\xA5": ["⌥ ."],
        b"\xC3\xB7": ["⌥ /"],
        b"\xE2\x80\x94": ["⌥ ⇧ -"],
        b"\xC2\xB1": ["⌥ ⇧ ="],
        b"\xE2\x80\x9D": ["⌥ ⇧ ["],
        b"\xE2\x80\x99": ["⌥ ⇧ ]"],
        b"\xC2\xBB": ["⌥ ⇧ \\"],
        b"\xC3\x9A": ["⌥ ⇧ ;"],
        b"\xC3\x86": ["⌥ ⇧ '"],
        b"\xC2\xAF": ["⌥ ⇧ ,"],
        b"\xCB\x98": ["⌥ ⇧ ."],
        b"\xC2\xBF": ["⌥ ⇧ /"],
    }
)


def require_keycap_lists_sorted():
    """Require Chords in each KeyCap List sorted by '', '⌃', '⌥', '⇧', '⌃ ⌥', etc"""

    stroke_by_keycap_tuple = dict()

    for (stroke, keycap_list) in KEYCAP_LISTS_BY_STROKE.items():
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

        for (cap, chords) in chord_by_cap.items():
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
        b"\xE0\x48": ["↑"],  # drawn as ▲
        b"\xE0\x4B": ["←"],  # drawn as ◀
        b"\xE0\x4D": ["→"],  # drawn as ▶
        b"\xE0\x50": ["↓"],  # drawn as ▼
        b"\xE0\x73": ["⌃ ←"],
        b"\xE0\x74": ["⌃ →"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # some of the Extra Key Caps at Windows
    {
        b"\x00\x76": ["⌃ PgDn"],
        b"\x00\x84": ["⌃ PgUp"],
        b"\xE0\x47": ["Home"],
        b"\xE0\x49": ["PgUp"],
        b"\xE0\x4F": ["End"],
        b"\xE0\x51": ["PgDn"],
        b"\xE0\x76": ["⌃ PgDn"],
        b"\xE0\x86": ["⌃ PgUp"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # more of the Extra Key Caps at Windows
    {
        b"\xE0\x52": ["Ins"],
        b"\xE0\x53": ["Del"],
        b"\xE0\x92": ["⌃ Ins"],
        b"\xE0\x93": ["⌃ Del"],
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


def parse_keycaps_py_args_else(sys_argv):
    """Print helps for Keycaps Py and exit zero or nonzero, else return args"""

    as_sys_argv = sys_argv if sys_argv else [None, "--"]

    # Drop the '--' Separator if present, even while declaring no Pos Args

    sys_parms = as_sys_argv[1:]
    if sys_parms == ["--"]:
        sys_parms = list()

    # Parse the Sh Command Line, or show Help

    parser = compile_keycaps_argdoc_else()
    args = parser.parse_args(sys_parms)  # prints helps and exits, else returns args
    if not as_sys_argv[1:]:
        doc = __main__.__doc__

        exit_via_testdoc(doc, epi="examples")  # exits because no args

    # Succeed

    return args


def compile_keycaps_argdoc_else():
    """Form an ArgumentParser for KeyCaps Py"""

    doc = __main__.__doc__
    parser = compile_argdoc(doc, epi="quirks")
    try:
        exit_if_argdoc_ne(doc, parser=parser)
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


def exit_if_argdoc_ne(doc, parser):
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
    encoded = b"\\\a\b\x1B\f\t\r\n"

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


def tui_open(stdio):
    """Accept such usage as 'with tui_open(sys.stderr):'"""

    tui = GlassTeletype(stdio)

    return tui


class GlassTeletype:  # FIXME work in Windows too, not just in Mac and Linux
    r"""
    Emulate a glass teletype at Stdio, such as the 1978 DEC VT100 Video Terminal

    Apply Terminal Input Magic to read ⌃@ ⌃C ⌃D ⌃J ⌃M ⌃Q ⌃S ⌃T ⌃Z ⌃\ etc as themselves,
    not as NUL SIGINT EOF LF CR SIGCONT SIGSTOP SIGINFO SIGTSTP SIGQUIT etc

    Compare Bash 'stty -a' and 'bind -p', Zsh 'bindkey', Unicode.Org Pdf U+0000
    """

    # stty -a |tr -d ' \t' |tr ';' '\n' |grep '=^' |sort

    def __init__(self, stdio):
        """Work at Sys Stderr, or elsewhere"""

        fd = stdio.fileno()

        self.fd = fd  # File Descriptor of Keyboard, for Os Read
        self.stdio = stdio  # File Stream of Keyboard, for IsATty and Flush
        self.tcgetattr = None  # Configuration of Terminal at Entry

        self.line = None  # the 2nd Keystroke that came in with a 1st Keystroke

    def __enter__(self):
        """Flush, then start taking Keystrokes literally & writing Lf as itself"""

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
                    if strokes in (b"\x00", b"\xE0"):
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

        print(*args, **kwargs_)

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

            mac_accentuators = b"\x60 \xC2\xB4 \xCB\x86 \xCB\x9C \xC2\xA8".split()
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
        if strokes in (b"\x00", b"\xE0"):
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


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main(sys.argv)


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/keycaps.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
