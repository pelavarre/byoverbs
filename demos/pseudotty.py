#!/usr/bin/env python3

"""
usage: pseudotty.py --

trace the I/O of a Pseudo-Terminal, in the way of a Sh 'script typescript'

docs:
  https://en.wikipedia.org/wiki/ANSI_escape_code
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html

examples:
  git clean -ffxdq
  rm -fr keylogger.bytes typescript  # clear cache
  demos/pseudotty.py --  # call once to record
  ls -1 |vi -u /dev/null +':set mouse=a' -  # setup a mouse-click/ touch-tap demo
  :q!
  ⌃D
  demos/pseudotty.py --  # call again to replay
"""

# code reviewed by people and by Black, Flake8, & Flake8-Import-Order


import __main__
import ast
import os
import pathlib
import pty
import re
import struct
import sys
import time


C0_C1_INTS = list(range(0x00, 0x20)) + [0x7F] + list(range(0x80, 0xA0))
C0_C1 = list(struct.pack("B", _) for _ in C0_C1_INTS)

CSI_DIGITS = r"0-9;>\?"
CSI_PATTERN = "\x1B\\[[{}]*[^{}]".format(CSI_DIGITS, CSI_DIGITS).encode()
CSI_PATTERN = "\x1B\\[M...|".encode() + CSI_PATTERN

ESC_INT = 0x1B
ESC = b"\x1B"


TOLD_BY_PACKET = dict()

TOLD_BY_PACKET[b"\x04"] = "\N{Up Arrowhead}D Tty Eof"  # ␃⌃D
# [b"\x04"] = "\N{Symbol For End Of Transmission}"  # ␄
TOLD_BY_PACKET[b"\x07"] = "\N{Up Arrowhead}G Tty Bell"  # ⌃G
# [b"\x07"] = "\N{Symbol For Bell}"  # ␇

# [b"\r"] = "\N{Return Symbol} Return"  # ⏎
# [b"\n"] = "\N{Symbol For Newline} Line Break"  # ␤
# [b"\r\n"] = "\N{Symbol For Carriage Return}\N{Symbol For Line Feed} CrLf"
# ␍␊

TOLD_BY_PACKET[b"\x1B" b"="] = "Application Keypad (DECKPAM)"  # VT100
TOLD_BY_PACKET[b"\x1B" b">"] = "Normal Keypad (DECKPNM)"  # VT100
TOLD_BY_PACKET[b"\x1B" b"M"] = "GShell Esc M"  # some GShell Secret
TOLD_BY_PACKET[b"\x1B" b"OB"] = "\N{Downwards Arrow} Mouse Down"  # ↓
TOLD_BY_PACKET[b"\x1B" b"OC"] = "\N{Rightwards Arrow} Mouse Right"  # →

TOLD_BY_PACKET[b"\x1B[" b"J"] = "Erase In Display (ED) Below"
TOLD_BY_PACKET[b"\x1B[" b"2J"] = "Erase In Display (ED) Above Below"
TOLD_BY_PACKET[b"\x1B[" b"K"] = "Erase In Line (EL) To Right"

TOLD_BY_PACKET[b"\x1B[" b"34h"] = "GShell CSI 34 h"  # some GShell Secret

# b"\x1B[" ... "h" = DECSET CSI ? Pm h  # DEC Private Mode Set
TOLD_BY_PACKET[b"\x1B[" b"?1h"] = "Application Cursor Keys (DECCKM)"  # VT100
TOLD_BY_PACKET[b"\x1B[" b"?12h"] = "Blink Cursor"
TOLD_BY_PACKET[b"\x1B[" b"?25h"] = "Show Cursor"  # DECTCEM VT220, 1st of 2
TOLD_BY_PACKET[b"\x1B[" b"?1000h"] = "Take Keystrokes from Mouse Press and Release"
TOLD_BY_PACKET[b"\x1B[" b"?1034h"] = "Join Meta Leak"  # seen without b"?1034l"
TOLD_BY_PACKET[b"\x1B[" b"?1049h"] = "Alt Screen"
TOLD_BY_PACKET[b"\x1B[" b"?2004h"] = "Alt Paste"

# b"\x1B[" ... "h" = DECRST CSI ? Pm h  # DEC Private Mode Reset
TOLD_BY_PACKET[b"\x1B[" b"?1l"] = "Normal Cursor Keys (DECCKM)"  # VT100
TOLD_BY_PACKET[b"\x1B[" b"?12l"] = "Steady Cursor"
TOLD_BY_PACKET[b"\x1B[" b"?25l"] = "Hide Cursor"  # DECTCEM VT220, 2nd of 2
# [b"\x1B[" b"?1034l"] = "Split 7-Bit Meta"  # (not seen in traces lately)
TOLD_BY_PACKET[b"\x1B[" b"?1000l"] = "Take No Keystrokes from Mouse Press and Release"
TOLD_BY_PACKET[b"\x1B[" b"?1049l"] = "Main Screen"
TOLD_BY_PACKET[b"\x1B[" b"?2004l"] = "Main Paste"

TOLD_BY_PACKET[b"\x1B[" b"00m"] = "Exit SGR 00 Variation"
TOLD_BY_PACKET[b"\x1B[" b"0m"] = "Exit SGR 0 Variation"
TOLD_BY_PACKET[b"\x1B[" b"m"] = "Exit SGR"

TOLD_BY_PACKET[b"\x1B[" b"1;34m"] = "Bold SGR with Blue SGR"
TOLD_BY_PACKET[b"\x1B[" b"1m"] = "Bold SGR"
TOLD_BY_PACKET[b"\x1B[" b"3m"] = "Italic SGR"
TOLD_BY_PACKET[b"\x1B[" b"24m"] = "Underlined Exit SGR"
TOLD_BY_PACKET[b"\x1B[" b"34m"] = "Blue SGR"
TOLD_BY_PACKET[b"\x1B[" b"23m"] = "Italic Exit Blackletter Exit SGR"
TOLD_BY_PACKET[b"\x1B[" b"27m"] = "Reversed Exit SGR"  # Positive On SGR
TOLD_BY_PACKET[b"\x1B[" b"29m"] = "Strikethrough Exit SGR"  # Crossed Out Exit
TOLD_BY_PACKET[b"\x1B[" b"94m"] = "Bright Blue SGR"

TOLD_BY_PACKET[b"\x1B[" b">4;2m"] = "Enter XTQMODKEYS"
TOLD_BY_PACKET[b"\x1B[" b">4;m"] = "Exit XTQMODKEYS"
TOLD_BY_PACKET[b"\x1B[" b"?4m"] = "Query XTQMODKEYS"

TOLD_BY_PACKET[b"\x1B[" b"22;0;0t"] = "Enter XTSMTITLE 22 0 0"
TOLD_BY_PACKET[b"\x1B[" b"22;1t"] = "Push Icon Title"
TOLD_BY_PACKET[b"\x1B[" b"22;2t"] = "Push Window Title"

TOLD_BY_PACKET[b"\x1B[" b"23;0;0t"] = "Exit XTSMTITLE 23 0 0"
TOLD_BY_PACKET[b"\x1B[" b"23;1t"] = "Pop Icon Title"
TOLD_BY_PACKET[b"\x1B[" b"23;2t"] = "Pop Window Title"

TOLD_BY_PACKET[b"\x1B[" b"200~"] = "Enter Bracketed Paste"  # for Mode "rb"
TOLD_BY_PACKET[b"\x1B[" b"201~"] = "Exit Bracketed Paste"  # for Mode "rb"

TOLD_BY_PACKET_KEYS_MINUS = list(TOLD_BY_PACKET.keys())

TOLD_BY_PACKET[b"\x1B"] = "\N{Broken Circle With Northwest Arrow} Esc"  # ⎋

#
# i began with my 2023-04 sample of Monterey macOS 12.6.3
#
# next Ubuntu 2020|2022 =>  \x07  \e[23m \e[22;0;0t \e[23;0;0t
#
# next G Shell =>  \eM \e\ \e] \ek  \e[34h \e[J  \[200~ \[201~
# also G Shell =>  \e[00m \e[0m \e[1;34m \e1m \e3m \e24m \e34m
#


def main():
    """Run from the Sh Command Line"""

    # Print Help Lines

    if sys.argv[1:] != "--".split():
        doc = __main__.__doc__
        print(doc.strip())

        sys.exit(0)

    # Else decode 1 or 2 Trace Files of Terminal I/O

    paths = list()

    path_in = pathlib.Path("keylogger.bytes")
    if path_in.exists():
        paths.append(path_in)
        pty_bytes_decode(path_name=path_in.name, mode="rb")

    path_out = pathlib.Path("typescript")
    if path_out.exists():
        paths.append(path_out)
        pty_bytes_decode(path_name=path_out.name, mode="wb")

    # Else trace Terminal Input to './keylogger.bytes' and Output to './typescript'

    if not paths:
        log_tty_till_exit()


def log_tty_till_exit():
    """Log Terminal I/O till Exit"""  # in much the style of Sh Script

    with open("keylogger.bytes", "wb") as coming:
        with open("typescript", "wb") as going:

            def coming_in(fd):
                in_bytes = os.read(fd, 0x400)
                coming.write(in_bytes)
                coming.flush()
                return in_bytes

            def going_out(fd):
                out_bytes = os.read(fd, 0x400)
                going.write(out_bytes)
                going.flush()
                return out_bytes

            print("Script started, file is", going.name)
            going.write(("Script started on %s\n" % time.asctime()).encode())

            pty.spawn("sh", master_read=going_out, stdin_read=coming_in)

            going.write(("Script done on %s\n" % time.asctime()).encode())
            print("Script done, file is", going.name)

    # compare with 'def read' at https://docs.python.org/3/library/pty.html


#
# Decode a Trace File of Terminal Input or Output
#


def pty_bytes_decode(path_name, mode):
    """Decode a Trace File of Terminal Input or Output"""

    assert mode in "rb wb".split(), (mode,)

    path = pathlib.Path(path_name)
    bytes_ = path.read_bytes()

    packets = pty_bytes_split(bytes_, mode=mode)
    groups = pty_packets_split(packets)
    pty_groups_print_repr(groups, path_name=path_name)


def pty_bytes_split(bytes_, mode):
    """Split Bytes into Defined Packets of Bytes"""

    assert mode in "rb wb".split(), (mode,)

    packets = list()

    splitted = 0
    for i in range(len(bytes_)):
        (packet, more) = pty_bytes_split_once(bytes_=bytes_[splitted:], mode=mode)

        splittable = i + 1 - splitted
        if splittable >= len(packet):
            assert splittable == len(packet), (splittable, len(packet), packet)

            packets.append(packet)
            splitted += len(packet)

    assert splitted == len(bytes_), (splitted, len(bytes_))

    return packets


def pty_bytes_split_once(bytes_, mode):  # noqa
    """Split out the leading Packet of the Bytes"""

    assert mode in "rb wb".split(), (mode,)

    # Declare \e[ CSI

    csi_digits = r"0-9;>\?"
    csi_pattern = "\x1B\\[[{}]*[^{}]".format(csi_digits, csi_digits).encode()
    csi_pattern = "\x1B\\[M...|".encode() + csi_pattern

    assert csi_pattern == CSI_PATTERN

    # Declare \e] OSC and \ek Alt OSC

    osc_pattern = "\x1B][^\x07\x1B]*(\x07|\x1B\\\\)".encode()
    alt_osc_pattern = "\x1Bk[^\x1B]*\x1B\\\\".encode()

    # Split out 1 Escape Sequence begun by the Control Sequence Introducer (CSI)

    if bytes_[:2] == b"\x1B[":
        m = re.match(csi_pattern, string=bytes_)
        if m:
            packet = m.group(0)
        else:
            print("CSI Pattern", csi_pattern.decode().replace("\x1B", r"\e"))  # Stderr?
            assert False, (bytes_[:50],)
            packet = bytes_[:2]

    elif bytes_[:2] == b"\x1B]":
        m = re.match(osc_pattern, string=bytes_)
        if m:
            packet = m.group(0)
        else:
            print("OSC Pattern", osc_pattern.decode().replace("\x1B", r"\e"))
            assert False, (bytes_[:50],)
            packet = bytes_[:2]

    elif bytes_[:2] == b"\x1Bk":
        m = re.match(alt_osc_pattern, string=bytes_)
        if m:
            packet = m.group(0)
        else:
            print("Alt OSC Pattern", alt_osc_pattern.decode().replace("\x1B", r"\e"))
            assert False, (bytes_[:50],)
            packet = bytes_[:2]

    # Split out the widest Defined Packet

    else:
        keys = list(_ for _ in TOLD_BY_PACKET_KEYS_MINUS if bytes_.startswith(_))
        keys.sort(key=lambda _: (len(_), _))
        if keys:
            packet = keys[-1]

        # Split out ESC + 1 Byte

        elif (mode == "wb") and (bytes_[:1] == ESC) and bytes_[1:]:
            packet = bytes_[:2]

        # Split out a burst of Text Characters encoded as Bytes

        else:
            text_width = 0
            bytes_plus = bytes_ + b"\0"
            while bytes_plus[text_width:][:1] not in C0_C1:
                text_width += 1

            if bytes_plus[text_width:][:2] == b"\r\n":
                text_width += len(b"\r\n")

            # Split out Text ended by much Blank Space

            much_width = text_width
            if text_width > 1:
                rstrip = bytes_[:text_width].rstrip()
                blank_width = text_width - len(rstrip)
                if 3 < blank_width < text_width:
                    much_width = len(rstrip)

            # Split out just 1 Byte

            width = max(1, much_width)
            packet = bytes_[:width]

    more = bytes_[len(packet) :]

    return (packet, more)


def pty_packets_split(packets):
    """Split Packets into Groups of Repeated Packets"""

    groups = list()

    grouped = 0
    packets_plus = packets + [None]
    for i, packet in enumerate(packets):
        next_packet = packets_plus[i + 1]

        if packet != next_packet:
            repeats = i - grouped + 1
            group = (repeats, packet)

            if (repeats == 1) and (len(packet) > 3):
                if packet == (len(packet) * packet[:1]):
                    repeats_ = len(packet)

                    packet_ = packet[:1]
                    group = (repeats_, packet_)

            groups.append(group)
            grouped += repeats

    return groups


def pty_groups_print_repr(groups, path_name):
    """Print the Python Code to write a clone of the Bytes"""

    dent = 4 * " "
    exotic_ints = list(ord(_) for _ in C0_C1 if _ not in b"\t\r\n")

    print()
    print('with open("{}", "wb") as writing:'.format(path_name))
    for group in groups:
        (repeats, packet) = group

        # Pick out the Meaning of a Packet

        tail = ""
        told = pty_packet_told(packet)
        if all((_ not in exotic_ints) for _ in packet):
            assert not told, (packet, told)
            tail = "  # (plain text)"

        elif told:
            tail = "  # {}".format(told)
            if "(CUP)" in told:
                tail = "  # {}".format(told.lower())

        # Print the Packet with its Meaning

        rep = repr(packet)
        if b'"' not in packet:
            rep = 'b"' + rep[len("b'") : -len("'")] + '"'
            assert ast.literal_eval(rep) == packet, (ast.literal_eval(rep), packet)

            # FIXME FIXME: upper hex for the Rep

        if repeats == 1:
            print(dent + r"writing.write({}){}".format(rep, tail))
        else:
            print(dent + r"writing.write({} * {}){}".format(repeats, rep, tail))


def pty_packet_told(packet):
    """Pick out what the Packet means, else return None"""

    told = None

    if packet in TOLD_BY_PACKET.keys():
        told = TOLD_BY_PACKET[packet]

    elif packet.startswith(b"\x1B]"):  # Operating System Command (OSC)
        told = "Operating-System-Command (OSC)"

    elif packet.startswith(b"\x1Bk"):  # Alt OSC
        told = "GShell Esc k"  # some GShell Secret

    elif packet.startswith(b"\x1B["):  # Control Sequence Introducer (CSI)
        if packet.startswith(b"\x1B[M") and (len(packet) == 6):
            (cb, cx, cy) = (packet[-3], packet[-2], packet[-1])

            (cx_, cy_) = (cx, cy)
            told = "Mouse Button 0x{:02X} at X={} Y={}".format(cb, cx_, cy_)
            if cb & 0x20:
                (cx_, cy_) = (cx - 0x20, cy - 0x20)
                told = "Mouse Button 0x{:02X} at X={} Y={}".format(cb, cx_, cy_)

        elif packet.endswith(b"H"):
            told = "Cursor Position (CUP) Y X"
        elif packet.endswith(b"r"):
            told = "Set Scrolling Region (DECSTBM) Y1 Y2"

    return told


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# FIXME: large Terminals
# FIXME: even Terminals larger than 255 x 255 Columns x Rows


# see also https://github.com/pelavarre/byoverbs/blob/main/demos/ptyspawn.py


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/pseudotty.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
