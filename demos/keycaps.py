#!/usr/bin/env python3

"""
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
  git clone https://github.com/pelavarre/byobash.git
  tui/keycaps.py  # show these examples
  tui/keycaps.py --  # show a fireplace of key caps bright when struck, then fading
"""

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
import select
import string
import sys
import termios
import textwrap
import time
import tty

_ = time

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace


MAC_PASTE_CHUNK_1022 = 1022
MAC_PASTE_125MS = 125e-3


NO_COLOR = 0
COLOR_BY_AGE = 36, 32, 33, 35, 31, 34, 30, 37
# Ansi Colors = Cyan, Green, Yellow, Magenta, Red, Blue, Black, White
# but their Yellow, Magenta, White come to me as Gold, Pink, Grey

COLORS = ", ".join("\x1B[{}m#{}\x1B[0m".format(_, _) for _ in COLOR_BY_AGE)

COLOR_500MS = 500e-3  # milliseconds of Key Cap life per color


#
# Run from the Sh command line
#


def main(sys_argv=None):
    """Run from the Sh command line"""

    stroke_print.t0 = None
    stroke_print.t1 = dt.datetime.now()
    stroke_print.t2 = None

    parse_keycaps_args(sys_argv)  # exits if no args, etc

    require_tty()

    keycaps_plot.t_by_keycap = dict()
    keycaps_plot.plotted = str()

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


_ = '''  # retain these Sourcelines while Git Diff goes wrong to care

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

'''


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
            len(COLORS), COLORS
        )
    )

    print()

    # Run with keystrokes forwarded when they occur, don't wait for more

    with stdtty_open(sys.stderr) as chatting:
        strokes = list()
        while True:
            prompt = "    -- Press the same Keystroke 3 times to quit --"

            # Prompt and read the next Stroke

            main.prompt = prompt

            print(prompt, end="\r")
            (stroke, millis, t1) = chatting.read_stroke_millis_t1()
            print(len(prompt) * " ", end="\r")

            # Pick out which Key Caps might have been struck to form the Stroke

            default_empty = list()
            keycaps = KEYCAP_LISTS_BY_STROKE.get(stroke, default_empty)

            # Print the Stroke, and print the Board of Key Caps if Key Caps found

            if keycaps:
                print(end="\r\n")

            stroke_print(stroke, millis=millis, t1=t1, keycaps=keycaps)

            if keycaps:
                print(end="\r\n")
                keycaps_plot(keycaps, t1=t1)
                keycaps_print(keycaps, stroke=stroke, t1=t1)
                print(end="\r\n")

            # Quit after the 3rd Copy of any 1 Stroke coming slowly from fingers

            strokes.append(stroke)
            if millis < 100:  # Don't quit while holding down a Key Cap to repeat
                strokes.clear()
            if strokes[-3:] == (3 * [stroke]):

                break


def stroke_print(stroke, millis, t1, keycaps):
    """Print the Stroke itself"""

    # Measure the time from last input to next block for input

    t0t2 = (stroke_print.t0 - stroke_print.t2).total_seconds() * 1000

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

    str_t1t0 = "{:,}".format(int(millis)).replace(",", "_")
    str_t0t2 = "{:,}".format(int(t0t2)).replace(",", "_")

    assert MAX_LEN_KEY_CAPS_STROKE_6 == 6 < 10
    if len(stroke) <= 10:

        print(
            "{} {} {} ({}) {} {} ms".format(
                keycaps,
                len(stroke),
                stroke_rep,
                hexxed,
                str_t0t2,
                str_t1t0,
            ),
            end="\r\n",
        )

        return

    hasher = hashlib.md5()
    hasher.update(stroke)
    encoded = hasher.digest()

    alt_rep = encoded[:3].hex().upper()

    hexxed_0 = hexlify(stroke[:3])
    hexxed_1 = hexlify(stroke[-3:])
    alt_hexxed = "x {} ... {}".format(hexxed_0, hexxed_1)

    print(
        "{} {} {} ({}) {} {} ms".format(
            keycaps, len(stroke), alt_rep, alt_hexxed, str_t0t2, str_t1t0
        ),
        end="\r\n",
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


def keycaps_print(keycaps, stroke, t1):
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

    print("\r\n".join(lines), end="\r\n")


def colorize(keycap, t, now):
    """Choose a Color for the Key Cap, else replace it with Spaces"""

    assert NO_COLOR == 0
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

    color = COLOR_BY_AGE[age]
    emit = "\x1B[{}m{}\x1B[{}m".format(color, keycap, NO_COLOR)
    # todo: might should only switch to No Color at the end?

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

for _KC in MACBOOK_PASTE_KEYCAPS:
    _KB = _KC.encode()
    assert _KB not in KEYCAP_LISTS_BY_STROKE.keys(), _KB
    KEYCAP_LISTS_BY_STROKE[_KB] = [_KC]

MAX_LEN_KEY_CAPS_STROKE_6 = max(len(_) for _ in KEYCAP_LISTS_BY_STROKE.keys())
assert MAX_LEN_KEY_CAPS_STROKE_6 == 6, MAX_LEN_KEY_CAPS_STROKE_6


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

        # Flush output before changing buffering

        stdtty.flush()

        # Stop line-buffering input, or leave it stopped

        if stdtty.isatty() and (getattr_ is None):
            getattr_ = termios.tcgetattr(fd)
            assert getattr_ is not None

            self.getattr_ = getattr_

            tty.setraw(fd, when=termios.TCSADRAIN)  # not TCSAFLUSH

            # todo: show that queued input survives

        # Succeed

        chatting = self

        return chatting

    def __exit__(self, *exc_info):
        """Flush, then stop taking Keystrokes literally & start writing Lf as Cr Lf"""

        _ = exc_info

        fd = self.fd
        getattr_ = self.getattr_
        stdtty = self.stdtty

        # Flush output before changing buffering

        stdtty.flush()

        # Compile-time option to flush input too

        assert MAC_PASTE_CHUNK_1022 == 1022

        if True:  # last jittered Sat 12/Nov/2022
            length = MAC_PASTE_CHUNK_1022
            while self.kbhit(timeout=0):
                _ = os.read(fd, length)

        # Start line-buffering input, or leave it started

        if getattr_ is not None:
            self.getattr_ = None  # mutate

            when = termios.TCSADRAIN
            # when = termios.TCSAFLUSH  # todo: find a test that cares
            termios.tcsetattr(fd, when, getattr_)

    def read_stroke_millis_t1(self):
        """Read one Keystroke, but also measure how long it took to arrive"""

        stroke_print.t2 = stroke_print.t1

        t0 = dt.datetime.now()
        stroke = self.read_stroke()
        t1 = dt.datetime.now()

        stroke_print.t0 = t0
        stroke_print.t1 = t1

        millis = (t1 - t0).total_seconds() * 1000

        return (stroke, millis, t1)

    def read_stroke(self):
        """Read 1 Byte, or b"\x1B" Esc leading a burst of Bytes, or a Paste of Bytes"""

        fd = self.fd

        prompt = main.prompt

        assert MAC_PASTE_CHUNK_1022 == 1022
        assert MAC_PASTE_125MS == 125e-3

        stroke = b""
        while True:
            length = MAC_PASTE_CHUNK_1022
            more = os.read(fd, length)

            if False:  # last jittered Sat 12/Nov/2022
                assert random.randint(0, 1)

            stroke += more

            if len(more) == length:
                if self.kbhit(timeout=MAC_PASTE_125MS):
                    # todo: solve separating multiple strokes of ⌘ V Paste

                    if len(stroke) == len(more):
                        print(len(prompt) * " ", end="\r")

                    str_count = "{:,}".format(len(stroke)).replace(",", "_")
                    print(
                        "Taking more than",
                        str_count,
                        "bytes of Paste",
                        end="\r\n",
                    )

                    continue

            break

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

    def kbhit(self, timeout):
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
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main(sys.argv)


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/keycaps.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
