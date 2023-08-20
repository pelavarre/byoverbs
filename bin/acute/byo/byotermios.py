#!/usr/bin/env python3

r"""
Amp up Import TermIo's

Read the Keyboard and Paste from a Terminal as Chords of Words of Chars, not as Bytes

For example, single Bytes as ⌃@ ⌃A ... Space ! ... @ ⇧A ⇧B ... A B ...
but then also Tab, Return, Delete, and ⎋ ← ↑ → ↓ ...
and then also ⌥Q and F1 and FnDelete, and ⌥⇧A and ⌥E E, and so on and on

Name the Byte Encodings here from our own Tests, stop struggling to find them doc'ed
"""

# code reviewed by people, and by Black & Flake8 & MyPy


import __main__
import datetime as dt
import string
import sys

import byo
from byo import byoargparse
from byo import byotty

_ = byo  # ducks Flake8 F401 imported.but.unused


C0_BYTES = b"".join(bytearray([_]) for _ in range(0, 0x20)) + b"\x7F"
assert len(C0_BYTES) == 0x21 == 33 == (128 - 95)
assert C0_BYTES == byotty.C0_BYTES, (C0_BYTES, byotty.C0_BYTES)


#
# Define Self-Test at Sh Usage: cd bin/acute/ && python3 -m pdb __main__.py --
#


def main() -> None:
    """Define Self-Test at Sh Usage: cd bin/acute/ && python3 -m pdb __main__.py --"""

    __main__.__doc__ = byoargparse.self_test_main_doc("byotermios.py")
    parser = byoargparse.ArgumentParser()
    parser.parse_args_else()  # often prints help & exits zero

    with byotty.BytesTerminal(sys.stderr) as bt:
        quits = ("⌃C", "⌃D", "⌃Z", r"⌃\ ".rstrip(), "⇧Q")
        bt.print(r"Press ⇧Z ⇧Q to quit, or any one of ⌃C ⌃D ⌃Z ⌃\ ".rstrip())
        bt.print()  # doesn't accept : Q ! Return

        t0 = dt.datetime.now()
        while True:
            bytes_ = bt.read_chord_bytes()  # blocks till Paste or Chords
            chords = bytes_to_chords_else(bytes_, default=bytes_)

            # Time the arrivals, log the details

            t1 = dt.datetime.now()
            if isinstance(chords, str):
                bt.print(t1 - t0, bytes_, chords)
            else:
                bt.print(t1 - t0, chords)
            t0 = dt.datetime.now()

            # Quit on request

            if chords in quits:
                break

    # todo: make a Sh Usage work without patching __main__.py

    # todo: solve bugs in macOS ⌥E Q arriving as b'\xC2\xB4', b'q' together or apart
    # todo: solve bugs like macOS ⌥E Q across the ⌥` ⌥E ⌥I ⌥U ⌥N


#
# Map the Bytes from the macOS Keyboard to the Chars of 1 more Words of Keyboard Chords,
# while making some effort to guess well at Linux & Windows Keyboards too
#


def bytes_to_chords_else(bytes_, default) -> bytes | str:
    """Find these Keyboard Bytes as Str Words of Keyboard Chords, else default"""

    if bytes_ in CHORDS_BY_BYTES.keys():
        chords = CHORDS_BY_BYTES[bytes_]
        return chords

    return default


Control = "\N{Up Arrowhead}"  # ⌃
Option = "\N{Option Key}"  # ⌥
Shift = "\N{Upwards White Arrow}"  # ⇧
Command = "\N{Place of Interest Sign}"  # ⌘

EscChord = "\N{Broken Circle With Northwest Arrow}"  # ⎋

# todo: more test of Option and Command


CHORDS_BY_BYTES = dict()


CHORDS_BY_BYTES[b"\0"] = "⌃@"  # ⌃Space ⌃⌥Space ⌃⇧Space ⌃⇧2 ⌃⌥⇧2
CHORDS_BY_BYTES[b"\t"] = "Tab"  # ⌃I ⌃⌥I ⌃⌥⇧I Tab ⌃Tab ⌥Tab ⌃⌥Tab
CHORDS_BY_BYTES[b"\r"] = "Return"  # ⌃M ⌃⌥M ⌃⌥⇧M Return etc
CHORDS_BY_BYTES[b"\x1B"] = EscChord  # Esc ⌥Esc ⌥⇧Esc etc
CHORDS_BY_BYTES[b" "] = "Space"  # Space ⇧Space
CHORDS_BY_BYTES[b"\x7F"] = "Delete"  # Delete ⌥Delete ⌥⇧Delete etc

assert (ord("@") ^ ord("@")) == 0  # here is why "⌃@" is the Chord of b"\x00" NUL
assert (ord("@") ^ ord("A")) == 1
assert (ord("@") ^ ord("Z")) == 26  # and so it goes

# b"\r" is also Return ⌃Return ⌥Return ⇧Return ⌃⌥Return ⌃⇧Return ⌥⇧Return ⌃⌥⇧Return
# b"\x1B" is also Esc ⌃Esc ⌥Esc ⇧Esc ⌃⌥Esc ⌃⇧Esc ⌥⇧Esc ⌃⌥⇧Esc
# b"\x7F" is also Delete ⌃Delete ⌥Delete ⇧Delete ⌃⌥Delete ⌃⇧Delete ⌥⇧Delete ⌃⌥⇧Delete


CHORDS_BY_BYTES[b"\x1B[Z"] = "⇧Tab"  # ⇧Tab ⌃⇧Tab ⌥⇧Tab ⌃⌥⇧Tab
CHORDS_BY_BYTES[b"\xC2\xA0"] = "⌥Space"  # ⌥Space ⌥⇧Space

assert b"\xC2\xA0".decode() == "\u00A0" == "\N{No-Break Space}"

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
# ⎋O replaces ⎋[ for ↑↓→← for b"\x1b[1?h" Application-Cursor-Keys till b"\x1b[1?l"

# Writing CSI A B C D to Terminal Screens is 04/01 /02 /02 /04 Cursor Up Down Right Left
# Writing CSI Z is 05/10 Cursor Backward Tabulation (CBT)


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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/acute/byo/
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
