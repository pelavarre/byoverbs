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


Control = "\N{Up Arrowhead}"  # ⌃
Option = "\N{Option Key}"  # ⌥
Shift = "\N{Upwards White Arrow}"  # ⇧

Command = "\N{Place of Interest Sign}"  # ⌘

# Fn = ...


#
# Sometimes speak in terms of Prefix Keys
#


Escape = "\N{Broken Circle With Northwest Arrow}"  # ⎋  # Emacs Meta Prefix Key


#
# Form Chords of Words of Chars from the Chars of US Ascii and a few more
#

CHORDS_BY_BYTES = dict()


# Tests of Escape can run slow, such as delayed till next Key Chord

CHORDS_BY_BYTES[b"\0"] = "⌃@"  # ⌃Space ⌃⌥Space ⌃⇧Space ⌃⌥⇧Space ⌃⇧2 ⌃⌥⇧2

assert (ord("@") ^ ord("@")) == 0  # and so we speak of b"\0" as "^@"

CHORDS_BY_BYTES[b"\t"] = "Tab"  # ⌃I ⌃⌥I ⌃⌥⇧I Tab ⌃Tab ⌥Tab ⌃⌥Tab
CHORDS_BY_BYTES[b"\r"] = "Return"  # ⌃M ⌃⌥M ⌃⌥⇧M Return ⌃⌥Return ⌃⌥⇧⌥Return etc
CHORDS_BY_BYTES[b"\x1B"] = "Escape"  # ⌃[ ⌃⌥[ ⌃⌥⇧[ Escape etc
CHORDS_BY_BYTES[b" "] = "Space"  # Space ⇧Space
CHORDS_BY_BYTES[b"\x7F"] = "Delete"  # Delete ⌥Delete ⌥⇧Delete etc

CHORDS_BY_BYTES[b"\x1B[Z"] = "⇧Tab"  # ⇧Tab ⌃⇧Tab ⌥⇧Tab ⌃⌥⇧Tab
CHORDS_BY_BYTES[b"\xC2\xA0"] = "⌥Space"  # ⌥Space ⌥⇧Space

assert b"\xC2\xA0".decode() == "\u00A0" == "\N{No-Break Space}"

# b"\r" is also Return ⌃Return ⌥Return ⇧Return ⌃⌥Return ⌃⇧Return ⌥⇧Return ⌃⌥⇧Return
# b"\x1B" is also Escape ⌃Escape ⌥Escape ⇧Escape ⌃⌥Escape ⌃⇧Escape ⌥⇧Escape ⌃⌥⇧Escape
# b"\x7F" is also Delete ⌃Delete ⌥Delete ⇧Delete ⌃⌥Delete ⌃⇧Delete ⌥⇧Delete ⌃⌥⇧Delete

# CSI Z writes as 05/10 Cursor Backward Tabulation (CBT)

CHORDS_BY_BYTES[b"\x1B[3~"] = "FnDelete"
CHORDS_BY_BYTES[b"\x1B[3;2~"] = "Fn⇧Delete"
CHORDS_BY_BYTES[b"\x1B[3;5~"] = "Fn⌃Delete"  # also ends Fn⌃⌥Delete

# b"\x1B\x1B[3;5~" is Fn⌃⌥Delete and also Escape Fn⌃Delete

# macOS takes Fn with many Keys, such as Fn Q for Notes, Fn E for Emoji, etc
# macOS mostly (entirely?) ignores Fn with Tab, Return, Escape, Space


CHORDS_BY_BYTES[b"\x1B[A"] = "↑"  # ↑ ⌥↑ ⇧↑ ⌃⌥↑ ⌃⇧↑ ⌥⇧↑ ⌃⌥⇧↑  # macOS takes ⌃↑
CHORDS_BY_BYTES[b"\x1B[B"] = "↓"  # ↓ ⌥↓ ⇧↓ ⌃⌥↓ ⌃⇧↓ ⌥⇧↓ ⌃⌥⇧↓  # macOS takes ⌃↓
CHORDS_BY_BYTES[b"\x1B[C"] = "→"  # → ⌃⌥→ ⌃⇧→ ⌥⇧→ ⌃⌥⇧→  # macOS takes ⌃→
CHORDS_BY_BYTES[b"\x1Bf"] = "⌥→"  # encoded as if Esc F for Emacs M-f
CHORDS_BY_BYTES[b"\x1B[1;2C"] = "⇧→"  # encoded as if explicit Y=1 with X=2 in CSI C
CHORDS_BY_BYTES[b"\x1B[D"] = "←"  # ← ⌃⌥← ⌃⇧← ⌥⇧← ⌃⌥⇧←  # macOS takes ⌃←
CHORDS_BY_BYTES[b"\x1Bb"] = "⌥←"  # encoded as if Esc B for Emacs M-b
CHORDS_BY_BYTES[b"\x1B[1;2D"] = "⇧←"

CHORDS_BY_BYTES[b"\x1BOA"] = "↑"  # encoded as if CSI Pn 0 alias of CSI Pn 1
CHORDS_BY_BYTES[b"\x1BOB"] = "↓"
CHORDS_BY_BYTES[b"\x1BOC"] = "→"
CHORDS_BY_BYTES[b"\x1BOD"] = "←"

# b"\x1BO" replaces b"\x1B[" for ↑ ↓ → ←
# after b"\x1b[1?h" Application-Cursor-Keys until b"\x1b[1?l"

# CSI A B C D writes as 04/01 /02 /03 /04 Cursor Up Down Right Left


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
        b"\x1B[23~": "F11",  # F11  # ⌥F6  # macOS takes F11
        b"\x1B[24~": "F12",  # F12  # ⌥F7
        b"\x1B[25~": "⇧F5",  # ⇧F5  # ⌥F8
        b"\x1B[26~": "⇧F6",  # ⇧F6  # ⌥F9
        b"\x1B[28~": "⇧F7",  # ⇧F7  # ⌥F10
        b"\x1B[29~": "⇧F8",  # ⇧F8  # ⌥F11
        b"\x1B[31~": "⇧F9",  # ⇧F9  # ⌥F12
        b"\x1B[32~": "⇧F10",
        b"\x1B[33~": "⇧F11",
        b"\x1B[34~": "⇧F12",
    }
)

# macOS takes ⇧F1 ⇧F2 ⇧F3 ⇧F4


CHORDS_BY_BYTES.update(  # the Fn Arrows
    {
        b"\x1BOH": "Fn←",
        b"\x1BOF": "Fn→",
        b"\x1B[5~": "Fn⇧↑",  # macOS Terminal takes Fn↑
        b"\x1B[6~": "Fn⇧↓",  # macOS Terminal takes Fn↓
        b"\x1B[H": "Fn⇧←",  # writes as 04/08 Cursor Position (CUP)
        b"\x1B[F": "Fn⇧→",  # writes as 04/06 Cursor Preceding Line (CPL)
    }
)

# todo: more test of Fn↑ and Fn↓ and Fn⇧↑ and Fn⇧↓
# because macOS Terminal Vi Insert ⌃V
# codes Fn↑ Fn↓ as Fn⇧↑ Fn⇧↓ and gives Fn↑ Fn↓ to macOS Terminal


CHORDS_BY_BYTES.update(  # the Option Digit Chords at Mac
    {
        b"\xC2\xBA": "⌥0",  # 'Masculine Ordinal Indicator'
        b"\xC2\xA1": "⌥1",  # 'Inverted Exclamation Mark'
        b"\xE2\x84\xA2": "⌥2",  # 'Trade Mark Sign'
        b"\xC2\xA3": "⌥3",  # 'Pound Sign'
        b"\xC2\xA2": "⌥4",  # 'Cent Sign'
        b"\xE2\x88\x9E": "⌥5",  # 'Infinity'
        b"\xC2\xA7": "⌥6",  # 'Section Sign'
        b"\xC2\xB6": "⌥7",  # 'Pilcrow Sign'
        b"\xE2\x80\xA2": "⌥8",  # 'Bullet'
        b"\xC2\xAA": "⌥9",  # 'Feminine Ordinal Indicator'
        b"\xE2\x80\x9A": "⌥⇧0",  # 'Single Low-9 Quotation Mark'
        b"\xE2\x81\x84": "⌥⇧1",  # 'Fraction Slash'
        b"\xE2\x82\xAC": "⌥⇧2",  # 'Euro Sign'
        b"\xE2\x80\xB9": "⌥⇧3",  # 'Single Left-Pointing Angle Quotation Mark'
        b"\xE2\x80\xBA": "⌥⇧4",  # 'Single Right-Pointing Angle Quotation Mark'
        b"\xEF\xAC\x81": "⌥⇧5",  # 'Latin Small Ligature FI'
        b"\xEF\xAC\x82": "⌥⇧6",  # 'Latin Small Ligature FL'
        b"\xE2\x80\xA1": "⌥⇧7",  # 'Double Dagger'
        b"\xC2\xB0": "⌥⇧8",  # 'Degree Sign'
        b"\xC2\xB7": "⌥⇧9",  # 'Middle Dot'
    }
)


CHORDS_BY_BYTES.update(  # the Option Letter & Option Accent Chords at Mac
    {
        # ⌥` does not come before ⌥A
        b"\xC3\xA5": "⌥A",
        b"\xE2\x88\xAB": "⌥B",
        b"\xC3\xA7": "⌥C",
        b"\xE2\x88\x82": "⌥D",
        # ⌥E does not come after ⌥D
        b"\xC3\xA1": "⌥E A",
        b"\xC3\xA9": "⌥E E",
        b"\xC3\xAD": "⌥E I",
        b"\x6A\xCC\x81": "⌥E J",
        b"\xC3\xB3": "⌥E O",
        b"\xC3\xBA": "⌥E U",
        b"\xC6\x92": "⌥F",
        b"\xC2\xA9": "⌥G",
        b"\xCB\x99": "⌥H",
        # ⌥I does not come after ⌥H
        b"\xC3\xA2": "⌥I A",
        b"\xC3\xAA": "⌥I E",
        b"\xC3\xAE": "⌥I I",
        b"\xC3\xB4": "⌥I O",
        b"\xC3\xBB": "⌥I U",
        b"\xE2\x88\x86": "⌥J",
        b"\xCB\x9A": "⌥K",
        b"\xC2\xAC": "⌥L",
        b"\xC2\xB5": "⌥M",
        # ⌥N does not come after ⌥M
        b"\xC3\xA3": "⌥N A",
        b"\xC3\xB1": "⌥N N",
        b"\xC3\xB5": "⌥N O",
        b"\xC3\xB8": "⌥O",
        b"\xCF\x80": "⌥P",
        b"\xC5\x93": "⌥Q",
        b"\xC2\xAE": "⌥R",
        b"\xC3\x9F": "⌥S",
        b"\xE2\x80\xA0": "⌥T",
        # ⌥U does not come after ⌥T
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
        b"\xC2\xB4": "⌥⇧E",  # ⌥E ⌥E  # ⌥⇧E  # ⌥E Space
        b"\xC3\x8F": "⌥⇧F",
        b"\xCB\x9D": "⌥⇧G",
        b"\xC3\x93": "⌥⇧H",
        b"\xCB\x86": "⌥⇧I",  # ⌥I ⌥I  # ⌥⇧I  # ⌥I Space
        b"\xC3\x94": "⌥⇧J",
        b"\xEF\xA3\xBF": "⌥⇧K",
        b"\xC3\x92": "⌥⇧L",
        b"\xC3\x82": "⌥⇧M",
        b"\xCB\x9C": "⌥⇧N",  # ⌥N ⌥N  # ⌥⇧N  # ⌥N Space
        b"\xC3\x98": "⌥⇧O",
        b"\xE2\x88\x8F": "⌥⇧P",
        b"\xC5\x92": "⌥⇧Q",
        b"\xE2\x80\xB0": "⌥⇧R",
        b"\xC3\x8D": "⌥⇧S",
        b"\xCB\x87": "⌥⇧T",
        b"\xC2\xA8": "⌥⇧U",  # ⌥U ⌥U  # ⌥⇧U  # ⌥U Space
        b"\xE2\x97\x8A": "⌥⇧V",
        b"\xE2\x80\x9E": "⌥⇧W",
        b"\xCB\x9B": "⌥⇧X",
        b"\xC3\x81": "⌥⇧Y",
        b"\xC2\xB8": "⌥⇧Z",
        # b"\x60"  # ⌥` ⌥`  # ⌥⇧`  # ⌥` Space
        b"\xC3\xA0": "⌥`A",
        b"\xC3\xA8": "⌥`E",
        b"\xC3\xAC": "⌥`I",
        b"\xC3\xB2": "⌥`O",
        b"\xC3\xB9": "⌥`U",
    }
)


CHORDS_BY_BYTES.update(  # the Option Punctuation-Mark Chords at Mac
    {
        b"\xE2\x80\x93": "⌥-",  # 'En Dash'
        b"\xE2\x89\xA0": "⌥=",  # 'Not Equal To'
        b"\xE2\x80\x9C": "⌥[",  # 'Left Double Quotation Mark'
        b"\xE2\x80\x98": "⌥]",  # 'Left Single Quotation Mark'
        b"\xC2\xAB": "⌥\\",  # 'Left-Pointing Double Angle Quotation Mark'
        b"\xE2\x80\xA6": "⌥;",  # 'Horizontal Ellipsis'
        b"\xC3\xA6": "⌥'",  # 'Latin Small Letter AE'
        b"\xE2\x89\xA4": "⌥,",  # 'Less-Than Or Equal To'
        b"\xE2\x89\xA5": "⌥.",  # 'Greater-Than Or Equal To'
        b"\xC3\xB7": "⌥/",  # 'Division Sign'
        b"\xE2\x80\x94": "⌥_",  # 'Em Dash'
        b"\xC2\xB1": "⌥⇧=",  # 'Plus-Minus Sign'
        b"\xE2\x80\x9D": "⌥⇧[",  # 'Right Double Quotation Mark'
        b"\xE2\x80\x99": "⌥⇧]",  # 'Right Single Quotation Mark'
        b"\xC2\xBB": "⌥⇧\\",  # 'Right-Pointing Double Angle Quotation Mark'
        b"\xC3\x9A": "⌥⇧;",  # 'Latin Capital Letter U With Acute'
        b"\xC3\x86": "⌥⇧'",  # 'Latin Capital Letter AE'
        b"\xC2\xAF": "⌥⇧,",  # 'Macron'
        b"\xCB\x98": "⌥⇧.",  # 'Breve'
        b"\xC2\xBF": "⌥⇧/",  # 'Inverted Question Mark'
    }
)

# macOS takes ⌃⇧F ⌃⌥⇧F


def add_us_ascii_into_chords_by_bytes() -> None:
    """Add a US Ascii Keyboard into Chars by Bytes"""

    chords_by_bytes = CHORDS_BY_BYTES

    c0_bytes = bytes(_ for _ in range(0, 0x20)) + b"\x7F"
    assert len(c0_bytes) == 0x21 == 33 == (128 - 95)

    # Decode the Control Chords not yet decoded

    assert Control == "\N{Up Arrowhead}"  # ⌃

    assert (ord("@") ^ ord("@")) == 0
    assert (ord("@") ^ ord("A")) == 1
    assert (ord("@") ^ ord("Z")) == 26

    for ord_ in c0_bytes:
        char = chr(ord_)
        bytes_ = char.encode()
        if bytes_ in chords_by_bytes.keys():  # Space Tab Return Escape Delete
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
# Require each List of Chords stands for exactly one List of Bytes,
# except when life isn't quite so simple
#


def assert_one_bytes_per_chord():
    """Require each List of Chords stands for exactly one List of Bytes"""

    alt_chords_by_bytes = dict(CHORDS_BY_BYTES)

    del alt_chords_by_bytes[b"\x1BOA"]  # "↑"
    del alt_chords_by_bytes[b"\x1BOB"]  # "↓"
    del alt_chords_by_bytes[b"\x1BOC"]  # "→"
    del alt_chords_by_bytes[b"\x1BOD"]  # "←"

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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/optionee/byo/
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
