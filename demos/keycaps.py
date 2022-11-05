#!/usr/bin/env python3

"""
usage: keycaps.py [-h] [--loopback]

fire key caps bright when struck, fade to black, then grey, then gone

options:
  -h, --help  show this help message and exit
  --loopback  show one line per keystroke

quirks:
  reacts complexly to
  + CapsLock, Control, Fn, ⌥ Option Alt, & ⌘ Command keys for shifting keys
  + Option Grave and Option E I N U keys for prefixing other keys
  + Terminal > Preferences > Profiles > Keyboard > Use Option As Meta
  + pressing ⌃ ⌥ Space to change System Preferences > Keyboard > Input Sources
  + pressing Key Caps that work outside, such as ⇧ by itself, or F11 in place of ⌥ F6

examples:
  git clone https://github.com/pelavarre/byobash.git
  tui/keycaps.py  # show these examples
  tui/keycaps.py --  # show a fireplace of key caps bright when struck, then fading
  tui/keycaps.py --loopback  # show only the mechanics inside
"""

# code reviewed by people, and by Black and Flake8
# developed by:  F=demos/keycaps.py && black $F && flake8 $F && $F --


import __main__
import argparse
import collections
import datetime as dt
import difflib
import os
import pdb
import re
import select
import string
import sys
import termios
import textwrap
import tty
import unicodedata

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace


DEFAULT_NONE = None

MILLIS_PER_COLOR = 500  # milliseconds of Key Cap life per color


#
# Run from the Sh command line
#


def main(sys_argv=None):
    """Run from the Sh command line"""

    args = parse_keycaps_args(sys_argv)  # exits if no args, etc

    require_tty()

    if args.loopback:
        run_loopback()

        return

    run_fireplace()


def require_tty():
    """Fail-fast when not run from a Terminal"""

    try:
        with stdtty_open(sys.stderr):
            pass
    except Exception as exc:
        sys_stderr_print("Traceback (most recent call last):")
        sys_stderr_print("  ...")
        sys_stderr_print("{}: {}".format(type(exc).__name__, exc))

        sys_stderr_print()
        sys_stderr_print("Run this code inside a Terminal, such as a Windows Dos Box")

        sys.exit(1)


def run_loopback():
    """Show one line per keystroke"""

    # Greet people

    print()
    print("Beware of F11 moving your Terminal Windows, try ⌥ F6 instead")
    print("Beware of ⌃ ⌥ Space or ⌃ ⌥ ⇧ Space changing your Keyboard Input Source")
    print("Beware of CapsLock changing your Keyboard Input Byte Codes")

    print()
    print("Type faster or slower to see more colors:", COLORS)

    print()
    print("Press the same Keystroke 3 times to quit")

    # React to each Stroke as it comes, don't wait for more

    with stdtty_open(sys.stderr) as chatting:
        strokes = list()
        while True:

            (millis, t1, stroke) = chatting.read_millis_stroke()
            _ = t1

            # Work up details on the Stroke

            str_int_millis = "{:6}".format(int(millis))

            keycaps = KEYCAP_LISTS_BY_STROKE.get(stroke, DEFAULT_NONE)
            hexxed = bytes_hex_repr(stroke)
            vimmed = vim_c0_repr(stroke.decode())

            # Print the details

            print(str_int_millis, hexxed, keycaps, vimmed, end="\r\n")

            # Quit after the 3rd Copy of any 1 Stroke

            strokes.append(stroke)
            if strokes[-3:] == (3 * [stroke]):

                break


def run_fireplace():
    """Fire key caps bright when struck, fade to black, then grey, then gone"""

    DENT = "    "

    # Greet people

    print()
    print("Beware of F11 moving your Terminal Windows, try ⌥ F6 instead")
    print("Beware of ⌃ ⌥ Space or ⌃ ⌥ ⇧ Space changing your Keyboard Input Source")
    print("Beware of CapsLock changing your Keyboard Input Byte Codes")

    print()
    print("Type faster or slower to see more colors:", COLORS)

    print()

    # Form a Board of Keycaps to print

    plottable = textwrap.dedent(MACBOOK_KEYCAP_CHARS).strip()
    plottable = "\n".join(_ for _ in plottable.splitlines() if _)

    indexable = "\n".join((DENT + _ + DENT) for _ in plottable.splitlines())

    plotted = "\n".join((len(_) * " ") for _ in indexable.splitlines())

    # Run with keystrokes forwarded when they occur, don't wait for more

    t_by_keycap = dict()
    with stdtty_open(sys.stderr) as chatting:
        strokes = list()
        sep = None
        while True:

            # Prompt and read the next Stroke

            if not sep:
                print(end="\r\n")

            prompt = "    -- Press the same Keystroke 3 times to quit --"
            print(prompt, end="\r")

            (millis, t1, stroke) = chatting.read_millis_stroke()
            _ = millis

            print(len(prompt) * " ", end="\r")

            rep_stroke = chars_encode_repr(stroke.decode()).replace(r"\x1B", r"\e")

            default_list = list()
            keycaps = KEYCAP_LISTS_BY_STROKE.get(stroke, default_list)

            # Separate one Trace of Key Caps from the next

            if not sep:
                sep = True

                print(end="\r\n")

            # Trace the Stroke itself

            print(keycaps, rep_stroke, end="\r\n")

            # Trace nothing more, when the Stroke sent no Key Caps

            if not keycaps:

                continue

            sep = None

            # Keep the Time Last Struck for each Key Cap

            for keycap_list in keycaps:
                for keycap in keycap_list.split():
                    t_by_keycap[keycap] = t1

            # Plot the Keyboard of Key Caps

            print(end="\r\n")
            print(end="\r\n")

            (plotted, lines) = plotted_plot_keycaps(
                plotted, indexable=indexable, t_by_keycap=t_by_keycap, keycaps=keycaps
            )

            print("\r\n".join(lines), end="\r\n")

            # Quit after the 3rd Copy of any 1 Stroke

            strokes.append(stroke)
            if strokes[-3:] == (3 * [stroke]):

                break


def plotted_plot_keycaps(plotted, indexable, t_by_keycap, keycaps):
    """Plot the Keyboard of Key Caps"""

    # Form a new Board

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

    # Print the details

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
                emit = colorize(keycap, t=t_by_keycap[keycap], now=now)
            emits.append(emit)

        emitting = "".join(emits).rstrip()

        lines.append(emitting)

    # Drop the blank lines above and below the visible Key Caps

    while lines and not lines[0]:
        lines.pop(0)

    while lines and not lines[-1]:
        lines.pop(-1)

    #

    return (plotted, lines)


COLOR_BY_AGE = [36, 32, 33, 35, 31, 34, 30, 37]
COLORS = ", ".join("\x1B[{}m#{}\x1B[0m".format(_, _) for _ in COLOR_BY_AGE)


def colorize(keycap, t, now):
    """Choose a Color for the Key Cap, else replace it with Spaces"""

    # Find Teal, Green, Gold, Pink, Red, Blue, Black, Grey in the Ascii Colors

    no_color = 0  # todo: might should only switch to No Color at the end?
    colors_by_age = [36, 32, 33, 35, 31, 34, 30, 37]

    # Measure the age of the last Stroke of this Key Cap

    nowt = now - t
    timeout = MILLIS_PER_COLOR / 1e3  # often 500e-3
    age = int(nowt.total_seconds() / timeout)

    # Replace with Spaces after awhile

    if age not in range(len(COLOR_BY_AGE)):
        emit = len(keycap) * " "

        return emit

    # Fire bright when struck, fade to black, then grey, then gone

    color = colors_by_age[age]
    emit = "\x1B[{}m{}\x1B[{}m".format(color, keycap, no_color)

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

MACBOOK_SHIFT_KEYCAPS = "⇧ ↑ Fn ⌃ ⌥ ⌘ ← ↓ →".split()


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

CHORDS = [
    "",
    "⌃",
    "⌥",
    "⇧",
    "⌃ ⌥",
    "⌃ ⇧",
    "⌥ ⇧",
    "⌃ ⌥ ⇧",
]

_8_DELETES = list("{} Delete".format(_).strip() for _ in CHORDS)

_12_ESCAPES = ["⌃ [", "⌃ ⌥ [", "⌃ ⌥ [", "⌃ ⌥ ⇧ ["]
_12_ESCAPES += list("{} Esc".format(_).strip() for _ in CHORDS)

_11_TABS = ["⌃ I", "⌃ ⌥ I", "⌃ ⌥ ⇧ I"]
_11_TABS += list("{} Tab".format(_).strip() for _ in CHORDS)

_11_RETURNS = ["⌃ M", "⌃ ⌥ M", "⌃ ⌥ ⇧ M"]
_11_RETURNS += list("{} Return".format(_).strip() for _ in CHORDS)

KEYCAP_LISTS_BY_STROKE.update(  # the rest of Printable Ascii and Control C0 Ascii
    {
        b"\x00": ["⌃ Space", "⌃ ⇧ Space", "⌃ ⇧ 2", "⌃ ⌥ ⇧ 2"],  # near to ⇧2 for @
        b"\x09": _11_TABS,  # drawn as ⇥
        b"\x0D": _11_RETURNS,  # drawn as ↩
        b"\x1B": _12_ESCAPES,  # drawn as ⎋
        b"\x1B\x5B\x5A": ["⇧ Tab", "⌃ ⇧ Tab", "⌥ ⇧ Tab", "⌃ ⌥ ⇧ Tab"],  # drawn as ⇥
        b"\x1C": ["⌃ \\", "⌃ ⌥ \\", "⌃ ⌥ \\", "⌃ ⌥ ⇧ \\"],
        b"\x1D": ["⌃ ]", "⌃ ⌥ ]", "⌃ ⌥ ]", "⌃ ⌥ ⇧ ]"],
        b"\x1E": ["⌃ ⇧ 6", "⌃ ⌥ ⇧ 6"],  # near to ⇧6 for ^
        b"\x1F": ["⌃ -", "⌃ ⌥ -", "⌃ ⌥ -", "⌃ ⌥ ⇧ -"],  # near to ⇧- for _
        b"\x20": ["Space", "⇧ Space"],
        b"\x5C": ["\\", "⌥ Y"],  # ⌥ Y is \ in place of ¥, when inside Terminal
        b"\x7F": _8_DELETES,  # or drawn as ⌫ and ⌦
        b"\xC2\xA0": ["⌥ Space", "⌥ ⇧ Space"],
    }
)

for _N in range(0x80):  # require all the b"\x00"..b"\x7F" Ascii found by Strokes
    assert chr(_N).encode() in KEYCAP_LISTS_BY_STROKE.keys(), _N

assert (0x40 ^ ord("@")) == 0x00

assert (0x40 ^ ord("\\")) == 0x1C
assert (0x40 ^ ord("]")) == 0x1D
assert (0x40 ^ ord("^")) == 0x1E
assert (0x40 ^ ord("_")) == 0x1F
assert (0x40 ^ ord("?")) == 0x7F

KEYCAP_LISTS_BY_STROKE.update(  # the Arrow Key Caps
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

KEYCAP_LISTS_BY_STROKE.update(  # the Fn Key Caps
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

KEYCAP_LISTS_BY_STROKE.update(  # the Option Digit strokes
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

KEYCAP_LISTS_BY_STROKE.update(  # the Option Letter strokes that don't set up accents
    {
        b"\xC3\xA5": ["⌥ A"],
        b"\xE2\x88\xAB": ["⌥ B"],
        b"\xC3\xA7": ["⌥ C"],
        b"\xE2\x88\x82": ["⌥ D"],  # not followed by ⌥ E
        b"\xC6\x92": ["⌥ F"],
        b"\xC2\xA9": ["⌥ G"],
        b"\xCB\x99": ["⌥ H"],  # not followed by ⌥ I
        b"\xE2\x88\x86": ["⌥ J"],
        b"\xCB\x9A": ["⌥ K"],
        b"\xC2\xAC": ["⌥ L"],
        b"\xC2\xB5": ["⌥ M"],  # not followed by ⌥ N
        b"\xC3\xB8": ["⌥ O"],
        b"\xCF\x80": ["⌥ P"],
        b"\xC5\x93": ["⌥ Q"],
        b"\xC2\xAE": ["⌥ R"],
        b"\xC3\x9F": ["⌥ S"],
        b"\xE2\x80\xA0": ["⌥ T"],  # not followed by ⌥ U
        b"\xE2\x88\x9A": ["⌥ V"],
        b"\xE2\x88\x91": ["⌥ W"],
        b"\xE2\x89\x88": ["⌥ X"],
        b"\xCE\xA9": ["⌥ Z"],
        b"\xC3\x85": ["⌥ ⇧ A"],
        b"\xC4\xB1": ["⌥ ⇧ B"],
        b"\xC3\x87": ["⌥ ⇧ C"],
        b"\xC3\x8E": ["⌥ ⇧ D"],
        b"\xC2\xB4": ["⌥ ⇧ E"],
        b"\xC3\x8F": ["⌥ ⇧ F"],
        b"\xCB\x9D": ["⌥ ⇧ G"],
        b"\xC3\x93": ["⌥ ⇧ H"],
        b"\xCB\x86": ["⌥ ⇧ I"],
        b"\xC3\x94": ["⌥ ⇧ J"],
        b"\xEF\xA3\xBF": ["⌥ ⇧ K"],
        b"\xC3\x92": ["⌥ ⇧ L"],
        b"\xC3\x82": ["⌥ ⇧ M"],
        b"\xCB\x9C": ["⌥ ⇧ N"],
        b"\xC3\x98": ["⌥ ⇧ O"],
        b"\xE2\x88\x8F": ["⌥ ⇧ P"],
        b"\xC5\x92": ["⌥ ⇧ Q"],
        b"\xE2\x80\xB0": ["⌥ ⇧ R"],
        b"\xC3\x8D": ["⌥ ⇧ S"],
        b"\xCB\x87": ["⌥ ⇧ T"],
        b"\xC2\xA8": ["⌥ ⇧ U"],
        b"\xE2\x97\x8A": ["⌥ ⇧ V"],
        b"\xE2\x80\x9E": ["⌥ ⇧ W"],
        b"\xCB\x9B": ["⌥ ⇧ X"],
        b"\xC3\x81": ["⌥ ⇧ Y"],
        b"\xC2\xB8": ["⌥ ⇧ Z"],
    }
)

KEYCAP_LISTS_BY_STROKE.update(  # the Option Punctuation-Mark strokes
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

for _KC in MACBOOK_SHIFT_KEYCAPS:
    _KB = _KC.encode()
    assert _KB not in KEYCAP_LISTS_BY_STROKE.keys(), _KB
    KEYCAP_LISTS_BY_STROKE[_KB] = [_KC]


def require_keycap_lists_sorted():
    """Require Chords in each KeyCap List sorted by '', '⌃', '⌥', '⇧', '⌃ ⌥', etc"""

    for (stroke, keycap_list) in KEYCAP_LISTS_BY_STROKE.items():
        assert isinstance(keycap_list, list), repr(keycap_list)

        chord_by_cap = collections.defaultdict(list)
        for keycap in keycap_list:
            assert isinstance(keycap, str), repr(keycap)

            splits = keycap.split()
            chord = " ".join(splits[:-1])
            cap = splits[-1]

            chord_by_cap[cap].append(chord)

        for (cap, chords) in chord_by_cap.items():
            indices = list(CHORDS.index(_) for _ in chords)
            assert indices == sorted(indices), (keycap_list, indices)

            # print(stroke, chords, cap, indices)


require_keycap_lists_sorted()


#
# Take Words from the Sh Command Line into KeyCaps Py
#


def parse_keycaps_args(sys_argv):
    """Take Words from the Sh Command Line into KeyCaps Py"""

    as_sys_argv = sys_argv if sys_argv else [None, "--"]

    # Drop the '--' Separator if present, even while declaring no Pos Args

    sys_parms = as_sys_argv[1:]
    if sys_parms == ["--"]:
        sys_parms = list()

    # Parse the Sh Command Line, or show Help

    parser = compile_keycaps_argdoc()
    args = parser.parse_args(sys_parms)  # exits if "-h", "--h", "--he", ... "--help"
    if not as_sys_argv[1:]:
        doc = __main__.__doc__

        exit_via_testdoc(doc, epi="examples")  # exits because no args

    # Succeed

    return args


def compile_keycaps_argdoc():
    """Form an ArgumentParser for KeyCaps Py"""

    doc = __main__.__doc__

    parser = compile_argdoc(doc, epi="quirks")
    parser.add_argument(
        "--loopback", action="count", help="show one line per keystroke"
    )

    try:

        exit_unless_doc_eq(doc, parser)

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


def exit_unless_doc_eq(doc, parser):
    """Exit nonzero, unless Doc equals Parser Format_Help"""

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

    # Fetch the Main Doc

    file_filename = os.path.split(__file__)[-1]

    main_doc_strip = doc.strip()

    got = main_doc_strip
    got_filename = "{} --help".format(file_filename)
    want = parser_doc
    want_filename = "argparse.ArgumentParser(..."

    # Print the Diff to Parser Doc from Main Doc and exit, if Diff exists

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

        sys.exit(1)  # trust caller to log SystemExit exceptions well


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


def bytes_hex_repr(xxs):
    r"""Repr of the Bytes, but as only uppercase Hex, no \t \n \r nor printable Ascii"""

    hexxes = xxs.hex().upper()
    escapes = "".join(
        r"\x{}{}".format(a, b) for (a, b) in zip(hexxes[::2], hexxes[1::2])
    )
    rep = r"b'{}'".format(escapes)

    return rep  # such as b'\x09\x0A\x0D\x20' for b'\t\n\r '


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


def vim_c0_repr(chars):
    """Encode Chars as themselves, except Space and C0 Ascii as their Xor 0x40"""

    rep = ""
    for ch in chars:
        n = ord(ch)
        if (n < 0x21) or (n == 0x7F):
            rep += "^" + chr(0x40 ^ n)
        else:
            rep += ch

    return rep


#
# Layer over Import Termios and Import Tty
#


def stdtty_open(stdtty):
    """Accept such usage as 'with stdtty_open(sys.stderr):'"""

    obj = StdTtyOpenerCloser(stdtty)

    return obj


class StdTtyOpenerCloser:  # FIXME work in Windows too, not just in Mac and Linux
    r"""
    Emulate a glass teletype at Stdio, such as the 1978 DEC VT100 Video Terminal

    Apply Terminal Input Magic to read ⌃@ ⌃C ⌃D ⌃J ⌃M ⌃Q ⌃S ⌃T ⌃Z ⌃\ etc as themselves,
    not as NUL SIGINT EOF LF CR SIGCONT SIGSTOP SIGINFO SIGTSTP SIGQUIT etc

    Compare Bash 'stty -a' and 'bind -p', Zsh 'bindkey', Unicode.Org Pdf U+0000
    """

    # stty -a |tr -d ' \t' |tr ';' '\n' |grep '=^' |sort

    def __init__(self, stdtty):
        """Work at Sys Stderr, or elsewhere"""

        fd = stdtty.fileno()

        self.fd = fd
        self.getattr_ = None
        self.stdtty = stdtty

    def __enter__(self):
        """Flush, then start taking Keystrokes literally & writing Lf as itself"""

        fd = self.fd
        getattr_ = self.getattr_
        stdtty = self.stdtty

        stdtty.flush()

        if stdtty.isatty() and (getattr_ is None):
            getattr_ = termios.tcgetattr(fd)
            assert getattr_ is not None

            self.getattr_ = getattr_

            tty.setraw(fd, when=termios.TCSADRAIN)  # not TCSAFLUSH

        chatting = self

        return chatting

    def __exit__(self, *exc_info):
        """Flush, then stop taking Keystrokes literally & start writing Lf as Cr Lf"""

        _ = exc_info

        fd = self.fd
        getattr_ = self.getattr_
        stdtty = self.stdtty

        stdtty.flush()

        if getattr_ is not None:
            self.getattr_ = None  # mutate

            when = termios.TCSADRAIN
            termios.tcsetattr(fd, when, getattr_)

    def read_millis_stroke(self):
        """Read one Keystroke, but also measure how long it took to arrive"""

        t0 = dt.datetime.now()
        stroke = self.read_stroke()
        t1 = dt.datetime.now()

        millis = (t1 - t0).total_seconds() * 1000

        return (millis, t1, stroke)

    def read_stroke(self):
        """Block enough to read one Keystroke"""

        fd = self.fd

        # Read one Byte, or a burst of Bytes begun by b"\x1B" Esc

        encodings = os.read(fd, 1)
        if encodings == b"\x1B":
            while self.select_select_rlist(timeout=0):
                encodings += os.read(fd, 1)

        # Read more Bytes to complete a partial trailing Unicode Encoding

        while True:
            try:
                _ = encodings.decode()
            except UnicodeDecodeError:
                encodings += os.read(fd, 1)

                continue

            break

        # Read more Bytes to keep small bursts of Paste together

        while self.select_select_rlist(timeout=0):
            encodings += os.read(fd, 1)

        # Require UTF-8 input

        try:
            encodings.decode()
        except UnicodeDecodeError:
            print("UnicodeDecodeError: {}".format(encodings))

            raise

        # Succeed

        stroke = encodings

        return stroke

        # passes when tested by Keystrokes

        # b'\x1B[Z' for ⇧ Tab  # same bytes as CSI Z, aka Emacs BackTab
        # b'b'\x1b[1;2C' for ⇧ ←  # same bytes as Left(m=1, n=2), so doubled in row
        # b'b'\x1b[1;2D' ⇧ →  # same bytes as Right(m=1, n=2), so doubled in row
        # b'\x1B[Z' aka CSI Z for ⇧ Tab

        # b'\x1Bb' aka ⌥ B for ⌥ ←  # same bytes as Meta B, aka Emacs Backward-Word
        # b'\x1Bf' aka ⌥ F for ⌥ →  # same bytes as Meta F, aka Emacs Forward-Word

        # doubles of Option E I N U Grave send themselves and still mark a vowel
        # Option E I N U before consonants send the marks themselves
        # Option Grave before consonants drops itself

        # FIXME: fails to bundle as much Paste as 3 rapid ⌘ V Paste's of this File

    def select_select_rlist(self, timeout):
        """Wait till next Byte of Keystroke, next burst of Paste pasted, or Timeout"""

        rlist = [self.stdtty]
        wlist = list()
        xlist = list()

        selected = select.select(rlist, wlist, xlist, timeout)

        (rlist2, _, _) = selected
        if rlist2 != rlist:
            assert rlist2 == [], rlist2

        return rlist2


#
# Layer over Import UnicodeData
#


# List the short Uppercase names from Unicode Org U000 Pdf to C0 Control Chars

C0_NAMES_MINUS = """
    NUL SOH STX ETX EOT ENQ ACK BEL BS HT LF VT FF CR SO SI
    DLE DC1 DC2 DC3 DC4 NAK SYN ETB CAN EM SUB ESC FS GS RS US
""".split()  # "\x00".."\x1F" apart from "\x7F" DEL

# b"\x00" NUL at ⌃ Space and ⌃ ⇧ Space
# b"\x00" NUL at ⌃ ⇧ 2 and not at ⌃ 2
# b"\x09" HT at ⌃ I and Tab and not at ⌃ ⇧ I
# b"\x0D" CR at ⌃ J and Return and not at ⌃ ⇧ J
# b"\x19" EOM at ⌃ Y in Python, despite "EM" in Unicode Org U000 Pdf
# b"\x1B" ESC at ⌃ [ and ⌃ ⇧ [ and Esc
# b"\x1E" RS at ⌃ ⇧ 6 and not at ⌃ 6
# b"\x1F" US at ⌃ ⇧ - and at ⌃ -

# b"\x7F" DEL at Delete and not at ⌃ ?


# List the short Uppercase names from Unicode Org U000 Pdf to C1 Control Chars

C1_NAMES_PLUS = """
    . . BPH NBH IND NEL SSA ESA HTS HTJ VTS PLD PLU RI SS2 SS3
    DCS PU1 PU2 STS CCH MW SPA EPA SOS . SCI CSI ST OSC PM APC
""".split()  # "\x80..\x9F" except not "\x80\x81\x99"

# "\x9B" is 1 Char CSI encoded by UTF-8 as b"\xC2\x9B"
# "\x1B\x5B" is 2 Char CSI encoded by UTF-8 as b"\x1B\x5B" == b"\x1B["

# "\xA0" aka "\N{NBSP}" is the first Char just past the C1 Chars, at ⌥ Space
# "\xAD" aka "\N{Soft Hyphen}", not far past the C1 Chars, looks lots like "\u002D" "-"


# Index C0 & C1 Control Chars by their short Uppercase names from Unicode Org U000 Pdf

CC_NAME_BY_CH = dict()

CC_NAME_BY_CH.update({chr(i): k for (i, k) in enumerate(C0_NAMES_MINUS)})
CC_NAME_BY_CH[chr(0x7F)] = "DEL"

CC_NAME_BY_CH.update(
    {chr(0x80 + i): k for (i, k) in enumerate(C1_NAMES_PLUS) if k != "."}
)

# Index C0 & C1 short Uppercase names by Control Chars from Unicode Org U000 Pdf

CC_CH_BY_NAME = {v: k for (k, v) in CC_NAME_BY_CH.items()}

assert len(CC_NAME_BY_CH) == len(CC_CH_BY_NAME)


# Show "\x19" also has "EOM" short name in Python, vs only "EM" short name in Unicode

EM = unicodedata.lookup("EOM")
assert "\x19" == "\N{EOM}" == EM


def unicodedata_lookup(name):
    r"""Char of a \N{name}"""

    try:
        ch = unicodedata.lookup(name)
    except KeyError:
        if name == "EM":  # recover from mystic KeyError at:  unicodedata.lookup("EM")
            ch = CC_CH_BY_NAME[name]
        else:

            raise

    return ch


assert unicodedata.name("\u00A0") == "NO-BREAK SPACE"
assert "\u00A0" == "\N{NBSP}" == "\N{No-Break Space}"


def unicodedata_name(ch):
    r"""One of the \N{name}s of a Char"""

    if ch == "\u00A0":

        return "NBSP"  # choose "NBSP" a la Html '&nbsp;' over "No-Break Space"

    try:
        name = unicodedata.name(ch).title()
    except ValueError:  # recover from ValueError's across C0 & C1 of Category 'Cc'
        name = CC_NAME_BY_CH.get(ch, DEFAULT_NONE)
        if name is None:

            raise

    return name


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main(sys.argv)


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/keycaps.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
