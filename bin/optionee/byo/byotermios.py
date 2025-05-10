r"""
usage: byotermios.py [-h]

encode Terminal Keyboard Input & Paste as Chords of Words of Chars, not as Bytes

options:
  -h, --help  show this help message and exit

note 1:
  takes single Bytes as ⌃@ ⌃A ... Space ! ... @ ⇧A ⇧B ... A B ...
  takes other single Bytes as Tab, Return, Delete, and ⎋ ...
  takes multiple Bytes as ← ↑ → ↓ ...
  takes multiple Bytes as ⌥Q and F1 and FnDelete, and as ⌥⇧A and ⌥E E, and so on and on

note 2:
  doesn't demand Doc for encoding Chords, just encodes them as shown in our own tests,
  except does take the first 128 Byte Encodings from the most standard place of
    https://unicode.org/charts/PDF/U0000.pdf

note 3:
  tries to run well on macOS, Linux, & Windows - but runs mostly at macOS as yet

usage examples:
  PYTHONPATH=bin/optionee python3 bin/optionee/byo/byotermios.py --
"""

# code reviewed by People, Black, Flake8, & MyPy


import collections
import datetime as dt
import string
import sys

import byo
from byo import byoargparse
from byo import byotty

... == dict[str, int]  # new since Oct/2020 Python 3.9  # type: ignore
... == byo  # ducks Flake8 F401 imported.but.unused  # type: ignore


#
# Run from the Sh Command Line
#


def main() -> None:
    """Run from the Sh Command Line"""

    chords_by_bytes = CHORDS_BY_BYTES

    parser = byoargparse.ArgumentParser()
    parser.parse_args_else()  # often prints help & exits zero

    # Copy Bytes of Keyboard or Paste to Screen,
    # as Chords of Words of Chars and themselves, else as themselves alone

    with byotty.BytesTerminal(sys.stderr) as bt:
        quits = ("⌃C", "⌃D", "⌃Z", r"⌃\ ".rstrip(), "⇧Q")
        bt.print(r"Press ⇧Z ⇧Q to quit, or any one of ⌃C ⌃D ⌃Z ⌃\ ".rstrip())
        bt.print()  # doesn't accept classic Vi : Q ! Return

        t0 = dt.datetime.now()
        while True:
            data = bt.read_chord_bytes()  # blocks till Paste or Chords

            # Time the arrivals, log the details

            t1 = dt.datetime.now()
            if data not in chords_by_bytes.keys():
                bt.print(t1 - t0, data)
            else:
                chords = chords_by_bytes[data]
                bt.print(t1 - t0, data, chords)
                if chords in quits:
                    break

            t0 = dt.datetime.now()

        # yes the Tty at Stderr, not a Tty at the Stdout of ShUtil Get_Terminal_Size


#
# Often speak in terms of Shift Keys
#


Control = "\N{UP ARROWHEAD}"  # ⌃
Option = "\N{OPTION KEY}"  # ⌥
Shift = "\N{UPWARDS WHITE ARROW}"  # ⇧

Command = "\N{PLACE OF INTEREST SIGN}"  # ⌘

# Fn = ...


#
# Sometimes speak in terms of Prefix Keys
#


Escape = "\N{BROKEN CIRCLE WITH NORTHWEST ARROW}"  # ⎋  # Emacs Meta Prefix Key


#
# Form Chords of Words of Chars from the Chars of US Ascii and a few more
#

CHORDS_BY_BYTES = dict()


# Tests of Escape can run slow, such as delayed till next Key Chord

CHORDS_BY_BYTES[b"\0"] = "⌃@"  # ⌃Space ⌃⌥Space ⌃⇧Space ⌃⌥⇧Space ⌃⇧2 ⌃⌥⇧2

assert (ord("@") ^ ord("@")) == 0  # and so we speak of b"\0" as "^@"

CHORDS_BY_BYTES[b"\t"] = "Tab"  # ⌃I ⌃⌥I ⌃⌥⇧I Tab ⌃Tab ⌥Tab ⌃⌥Tab
CHORDS_BY_BYTES[b"\r"] = "Return"  # ⌃M ⌃⌥M ⌃⌥⇧M Return ⌃⌥Return ⌃⌥⇧⌥Return etc
CHORDS_BY_BYTES[b"\x1b"] = "Escape"  # ⌃[ ⌃⌥[ ⌃⌥⇧[ Escape etc
CHORDS_BY_BYTES[b" "] = "Space"  # Space ⇧Space
CHORDS_BY_BYTES[b"\x7f"] = "Delete"  # Delete ⌥Delete ⌥⇧Delete etc

CHORDS_BY_BYTES[b"\x1b[Z"] = "⇧Tab"  # ⇧Tab ⌃⇧Tab ⌥⇧Tab ⌃⌥⇧Tab
CHORDS_BY_BYTES[b"\xc2\xa0"] = "⌥Space"  # ⌥Space ⌥⇧Space

assert b"\xc2\xa0".decode() == "\u00a0" == "\N{NO-BREAK SPACE}"

# b"\r" is also Return ⌃Return ⌥Return ⇧Return ⌃⌥Return ⌃⇧Return ⌥⇧Return ⌃⌥⇧Return
# b"\x1B" is also Escape ⌃Escape ⌥Escape ⇧Escape ⌃⌥Escape ⌃⇧Escape ⌥⇧Escape ⌃⌥⇧Escape
# b"\x7F" is also Delete ⌃Delete ⌥Delete ⇧Delete ⌃⌥Delete ⌃⇧Delete ⌥⇧Delete ⌃⌥⇧Delete

# CSI Z writes as 05/10 Cursor Backward Tabulation (CBT)

CHORDS_BY_BYTES[b"\x1b[3~"] = "FnDelete"
CHORDS_BY_BYTES[b"\x1b[3;2~"] = "Fn⇧Delete"
CHORDS_BY_BYTES[b"\x1b[3;5~"] = "Fn⌃Delete"  # also ends Fn⌃⌥Delete

# b"\x1B\x1B[3;5~" is Fn⌃⌥Delete and also Escape Fn⌃Delete

# macOS takes Fn with many Keys, such as Fn Q for Notes, Fn E for Emoji, etc
# macOS mostly (entirely?) ignores Fn with Tab, Return, Escape, Space


CHORDS_BY_BYTES[b"\x1b[A"] = "↑"  # ↑ ⌥↑ ⇧↑ ⌃⌥↑ ⌃⇧↑ ⌥⇧↑ ⌃⌥⇧↑  # macOS takes ⌃↑
CHORDS_BY_BYTES[b"\x1b[B"] = "↓"  # ↓ ⌥↓ ⇧↓ ⌃⌥↓ ⌃⇧↓ ⌥⇧↓ ⌃⌥⇧↓  # macOS takes ⌃↓
CHORDS_BY_BYTES[b"\x1b[C"] = "→"  # → ⌃⌥→ ⌃⇧→ ⌥⇧→ ⌃⌥⇧→  # macOS takes ⌃→
CHORDS_BY_BYTES[b"\x1bf"] = "⌥→"  # encoded as if Esc F for Emacs M-f
CHORDS_BY_BYTES[b"\x1b[1;2C"] = "⇧→"  # encoded as if explicit Y=1 with X=2 in CSI C
CHORDS_BY_BYTES[b"\x1b[D"] = "←"  # ← ⌃⌥← ⌃⇧← ⌥⇧← ⌃⌥⇧←  # macOS takes ⌃←
CHORDS_BY_BYTES[b"\x1bb"] = "⌥←"  # encoded as if Esc B for Emacs M-b
CHORDS_BY_BYTES[b"\x1b[1;2D"] = "⇧←"

CHORDS_BY_BYTES[b"\x1bOA"] = "↑"  # encoded as if CSI Pn 0 alias of CSI Pn 1
CHORDS_BY_BYTES[b"\x1bOB"] = "↓"
CHORDS_BY_BYTES[b"\x1bOC"] = "→"
CHORDS_BY_BYTES[b"\x1bOD"] = "←"

# b"\x1BO" replaces b"\x1B[" for ↑ ↓ → ←
# after b"\x1b[1?h" Application-Cursor-Keys until b"\x1b[1?l"

# CSI A B C D writes as 04/01 /02 /03 /04 Cursor Up Down Right Left


CHORDS_BY_BYTES.update(  # the Fn Key Caps at Mac
    {
        b"\x1bOP": "F1",
        b"\x1bOQ": "F2",
        b"\x1bOR": "F3",
        b"\x1bOS": "F4",
        b"\x1b[15~": "F5",
        b"\x1b[17~": "F6",  # F6  # ⌥F1
        b"\x1b[18~": "F7",  # F7  # ⌥F2
        b"\x1b[19~": "F8",  # F8  # ⌥F3
        b"\x1b[20~": "F9",  # F9  # ⌥F4
        b"\x1b[21~": "F10",  # F10  # ⌥F5
        b"\x1b[23~": "F11",  # F11  # ⌥F6  # macOS takes F11
        b"\x1b[24~": "F12",  # F12  # ⌥F7
        b"\x1b[25~": "⇧F5",  # ⇧F5  # ⌥F8
        b"\x1b[26~": "⇧F6",  # ⇧F6  # ⌥F9
        b"\x1b[28~": "⇧F7",  # ⇧F7  # ⌥F10
        b"\x1b[29~": "⇧F8",  # ⇧F8  # ⌥F11
        b"\x1b[31~": "⇧F9",  # ⇧F9  # ⌥F12
        b"\x1b[32~": "⇧F10",
        b"\x1b[33~": "⇧F11",
        b"\x1b[34~": "⇧F12",
    }
)

# macOS takes ⇧F1 ⇧F2 ⇧F3 ⇧F4


CHORDS_BY_BYTES.update(  # the Fn Arrows
    {
        b"\x1bOH": "Fn←",
        b"\x1bOF": "Fn→",
        b"\x1b[5~": "Fn⇧↑",  # macOS Terminal takes Fn↑
        b"\x1b[6~": "Fn⇧↓",  # macOS Terminal takes Fn↓
        b"\x1b[H": "Fn⇧←",  # writes as 04/08 Cursor Position (CUP)
        b"\x1b[F": "Fn⇧→",  # writes as 04/06 Cursor Preceding Line (CPL)
    }
)

# todo: more test of Fn↑ and Fn↓ and Fn⇧↑ and Fn⇧↓
# because macOS Terminal Vi Insert ⌃V
# codes Fn↑ Fn↓ as Fn⇧↑ Fn⇧↓ and gives Fn↑ Fn↓ to macOS Terminal


CHORDS_BY_BYTES.update(  # the Option Digit Chords at Mac
    {
        b"\xc2\xba": "⌥0",  # 'Masculine Ordinal Indicator'
        b"\xc2\xa1": "⌥1",  # 'Inverted Exclamation Mark'
        b"\xe2\x84\xa2": "⌥2",  # 'Trade Mark Sign'
        b"\xc2\xa3": "⌥3",  # 'Pound Sign'
        b"\xc2\xa2": "⌥4",  # 'Cent Sign'
        b"\xe2\x88\x9e": "⌥5",  # 'Infinity'
        b"\xc2\xa7": "⌥6",  # 'Section Sign'
        b"\xc2\xb6": "⌥7",  # 'Pilcrow Sign'
        b"\xe2\x80\xa2": "⌥8",  # 'Bullet'
        b"\xc2\xaa": "⌥9",  # 'Feminine Ordinal Indicator'
        b"\xe2\x80\x9a": "⌥⇧0",  # 'Single Low-9 Quotation Mark'
        b"\xe2\x81\x84": "⌥⇧1",  # 'Fraction Slash'
        b"\xe2\x82\xac": "⌥⇧2",  # 'Euro Sign'
        b"\xe2\x80\xb9": "⌥⇧3",  # 'Single Left-Pointing Angle Quotation Mark'
        b"\xe2\x80\xba": "⌥⇧4",  # 'Single Right-Pointing Angle Quotation Mark'
        b"\xef\xac\x81": "⌥⇧5",  # 'Latin Small Ligature FI'
        b"\xef\xac\x82": "⌥⇧6",  # 'Latin Small Ligature FL'
        b"\xe2\x80\xa1": "⌥⇧7",  # 'Double Dagger'
        b"\xc2\xb0": "⌥⇧8",  # 'Degree Sign'
        b"\xc2\xb7": "⌥⇧9",  # 'Middle Dot'
    }
)


CHORDS_BY_BYTES.update(  # the Option Letter & Option Accent Chords at Mac
    {
        # ⌥` does not come before ⌥A
        b"\xc3\xa5": "⌥A",
        b"\xe2\x88\xab": "⌥B",
        b"\xc3\xa7": "⌥C",
        b"\xe2\x88\x82": "⌥D",
        # ⌥E does not come after ⌥D
        b"\xc3\xa1": "⌥E A",
        b"\xc3\xa9": "⌥E E",
        b"\xc3\xad": "⌥E I",
        b"\x6a\xcc\x81": "⌥E J",
        b"\xc3\xb3": "⌥E O",
        b"\xc3\xba": "⌥E U",
        b"\xc6\x92": "⌥F",
        b"\xc2\xa9": "⌥G",
        b"\xcb\x99": "⌥H",
        # ⌥I does not come after ⌥H
        b"\xc3\xa2": "⌥I A",
        b"\xc3\xaa": "⌥I E",
        b"\xc3\xae": "⌥I I",
        b"\xc3\xb4": "⌥I O",
        b"\xc3\xbb": "⌥I U",
        b"\xe2\x88\x86": "⌥J",
        b"\xcb\x9a": "⌥K",
        b"\xc2\xac": "⌥L",
        b"\xc2\xb5": "⌥M",
        # ⌥N does not come after ⌥M
        b"\xc3\xa3": "⌥N A",
        b"\xc3\xb1": "⌥N N",
        b"\xc3\xb5": "⌥N O",
        b"\xc3\xb8": "⌥O",
        b"\xcf\x80": "⌥P",
        b"\xc5\x93": "⌥Q",
        b"\xc2\xae": "⌥R",
        b"\xc3\x9f": "⌥S",
        b"\xe2\x80\xa0": "⌥T",
        # ⌥U does not come after ⌥T
        b"\xc3\xa4": "⌥U A",
        b"\xc3\xab": "⌥U E",
        b"\xc3\xaf": "⌥U I",
        b"\xc3\xb6": "⌥U O",
        b"\xc3\xbc": "⌥U U",
        b"\xc3\xbf": "⌥U Y",
        b"\xe2\x88\x9a": "⌥V",
        b"\xe2\x88\x91": "⌥W",
        b"\xe2\x89\x88": "⌥X",
        b"\xce\xa9": "⌥Z",
        b"\xc3\x85": "⌥⇧A",
        b"\xc4\xb1": "⌥⇧B",
        b"\xc3\x87": "⌥⇧C",
        b"\xc3\x8e": "⌥⇧D",
        b"\xc2\xb4": "⌥⇧E",  # ⌥E ⌥E  # ⌥⇧E  # ⌥E Space
        b"\xc3\x8f": "⌥⇧F",
        b"\xcb\x9d": "⌥⇧G",
        b"\xc3\x93": "⌥⇧H",
        b"\xcb\x86": "⌥⇧I",  # ⌥I ⌥I  # ⌥⇧I  # ⌥I Space
        b"\xc3\x94": "⌥⇧J",
        b"\xef\xa3\xbf": "⌥⇧K",
        b"\xc3\x92": "⌥⇧L",
        b"\xc3\x82": "⌥⇧M",
        b"\xcb\x9c": "⌥⇧N",  # ⌥N ⌥N  # ⌥⇧N  # ⌥N Space
        b"\xc3\x98": "⌥⇧O",
        b"\xe2\x88\x8f": "⌥⇧P",
        b"\xc5\x92": "⌥⇧Q",
        b"\xe2\x80\xb0": "⌥⇧R",
        b"\xc3\x8d": "⌥⇧S",
        b"\xcb\x87": "⌥⇧T",
        b"\xc2\xa8": "⌥⇧U",  # ⌥U ⌥U  # ⌥⇧U  # ⌥U Space
        b"\xe2\x97\x8a": "⌥⇧V",
        b"\xe2\x80\x9e": "⌥⇧W",
        b"\xcb\x9b": "⌥⇧X",
        b"\xc3\x81": "⌥⇧Y",
        b"\xc2\xb8": "⌥⇧Z",
        # b"\x60"  # ⌥` ⌥`  # ⌥⇧`  # ⌥` Space
        b"\xc3\xa0": "⌥`A",
        b"\xc3\xa8": "⌥`E",
        b"\xc3\xac": "⌥`I",
        b"\xc3\xb2": "⌥`O",
        b"\xc3\xb9": "⌥`U",
    }
)


CHORDS_BY_BYTES.update(  # the Option Punctuation-Mark Chords at Mac
    {
        b"\xe2\x80\x93": "⌥-",  # 'En Dash'
        b"\xe2\x89\xa0": "⌥=",  # 'Not Equal To'
        b"\xe2\x80\x9c": "⌥[",  # 'Left Double Quotation Mark'
        b"\xe2\x80\x98": "⌥]",  # 'Left Single Quotation Mark'
        b"\xc2\xab": "⌥\\",  # 'Left-Pointing Double Angle Quotation Mark'
        b"\xe2\x80\xa6": "⌥;",  # 'Horizontal Ellipsis'
        b"\xc3\xa6": "⌥'",  # 'Latin Small Letter AE'
        b"\xe2\x89\xa4": "⌥,",  # 'Less-Than Or Equal To'
        b"\xe2\x89\xa5": "⌥.",  # 'Greater-Than Or Equal To'
        b"\xc3\xb7": "⌥/",  # 'Division Sign'
        b"\xe2\x80\x94": "⌥_",  # 'Em Dash'
        b"\xc2\xb1": "⌥⇧=",  # 'Plus-Minus Sign'
        b"\xe2\x80\x9d": "⌥⇧[",  # 'Right Double Quotation Mark'
        b"\xe2\x80\x99": "⌥⇧]",  # 'Right Single Quotation Mark'
        b"\xc2\xbb": "⌥⇧\\",  # 'Right-Pointing Double Angle Quotation Mark'
        b"\xc3\x9a": "⌥⇧;",  # 'Latin Capital Letter U With Acute'
        b"\xc3\x86": "⌥⇧'",  # 'Latin Capital Letter AE'
        b"\xc2\xaf": "⌥⇧,",  # 'Macron'
        b"\xcb\x98": "⌥⇧.",  # 'Breve'
        b"\xc2\xbf": "⌥⇧/",  # 'Inverted Question Mark'
    }
)

# macOS takes ⌃⇧F ⌃⌥⇧F


def add_us_ascii_into_chords_by_bytes() -> None:
    """Add a US Ascii Keyboard into Chars by Bytes"""

    chords_by_bytes = CHORDS_BY_BYTES

    c0_bytes = bytes(_ for _ in range(0, 0x20)) + b"\x7f"
    assert len(c0_bytes) == 0x21 == 33 == (128 - 95)

    # Decode the Control Chords not yet decoded

    assert Control == "\N{UP ARROWHEAD}"  # ⌃

    assert (ord("@") ^ ord("@")) == 0
    assert (ord("@") ^ ord("A")) == 1
    assert (ord("@") ^ ord("Z")) == 26

    for ord_ in c0_bytes:
        char = chr(ord_)
        bytes_ = char.encode()
        if bytes_ in chords_by_bytes.keys():  # Space Tab Return Escape Delete
            assert bytes_ in b"\x00\x09\x0d\x1b\x7f", bytes_
        else:
            chords_by_bytes[bytes_] = Control + chr(ord_ ^ 0x40)

    # Decode the Shift'ed and un-Shift'ed US Ascii Letters

    assert Shift == "\N{UPWARDS WHITE ARROW}"  # ⇧

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
# Require each List of Chords stands for exactly one List of Bytes,
# except when life isn't quite so simple
#


def assert_one_bytes_per_chord():
    """Require each List of Chords stands for exactly one List of Bytes"""

    alt_chords_by_bytes = dict(CHORDS_BY_BYTES)

    del alt_chords_by_bytes[b"\x1bOA"]  # "↑"
    del alt_chords_by_bytes[b"\x1bOB"]  # "↓"
    del alt_chords_by_bytes[b"\x1bOC"]  # "→"
    del alt_chords_by_bytes[b"\x1bOD"]  # "←"

    counter = collections.Counter(alt_chords_by_bytes.values())
    for chords, count in sorted(counter.items()):
        if count != 1:
            print(chords, count)

    for chords, count in sorted(counter.items()):
        assert count == 1, (chords, count)


assert_one_bytes_per_chord()


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()

    # todo: solve bugs in macOS ⌥E Q arriving as b'\xC2\xB4', b'q' together or apart
    # todo: solve bugs like macOS ⌥E Q across the ⌥` ⌥E ⌥I ⌥U ⌥N

    # todo: more test of Option and Command and Fn


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/optionee/byo/
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
