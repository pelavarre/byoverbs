#!/usr/bin/env python3

"""
usage: pseudotty.py --

trace the I/O of a Pseudo-Terminal, in the way of a Sh 'script typescript'

docs:
  https://en.wikipedia.org/wiki/ANSI_escape_code
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html

examples:
  rm -fr keylogger.bytes typescript  # clear cache
  demos/pseudotty.py --  # call once to record
  demos/pseudotty.py --  # call again to replay
  ls -1 |vi -u /dev/null +':set mouse=a' -  # setup a mouse-click/ touch-tap demo
"""

# code reviewed by people and by Black, Flake8, & Flake8-Import-Order


import __main__
import os
import pathlib
import pty
import re
import struct
import sys
import time


C0_C1_INTS = list(range(0x00, 0x20)) + [0x7F] + list(range(0x80, 0xA0))
C0_C1 = list(struct.pack("B", _) for _ in C0_C1_INTS)

ESC_INT = 0x1B
ESC = b"\x1B"


TOLD_BY_PACKET = dict()

TOLD_BY_PACKET[b"\x04"] = "\N{Up Arrowhead}D Tty Eof"  # ⌃D
TOLD_BY_PACKET[b"\r"] = "\N{Return Symbol} Return"  # ⏎
TOLD_BY_PACKET[b"\n"] = "\N{Symbol For Newline} Line Break"  # ␤

TOLD_BY_PACKET[b"\r\n"] = "\N{Symbol For Carriage Return}\N{Symbol For Line Feed} CrLf"
# ␍␊

TOLD_BY_PACKET[b"\x1B" b"="] = "Application Keypad (DECKPAM)"  # VT100
TOLD_BY_PACKET[b"\x1B" b">"] = "Normal Keypad (DECKPNM)"  # VT100
TOLD_BY_PACKET[b"\x1B" b"OB"] = "\N{Downwards Arrow} Mouse Down"  # ↓
TOLD_BY_PACKET[b"\x1B" b"OC"] = "\N{Rightwards Arrow} Mouse Right"  # →

TOLD_BY_PACKET[b"\x1B[" b"2J"] = "Erase In Display (ED) Above Below"

TOLD_BY_PACKET[b"\x1B[" b"K"] = "Erase In Line (EL) To Right"

TOLD_BY_PACKET[b"\x1B[" b"?1h"] = "Application Cursor Keys (DECCKM)"  # VT100
TOLD_BY_PACKET[b"\x1B[" b"?12h"] = "Blink Cursor"
TOLD_BY_PACKET[b"\x1B[" b"?25h"] = "Show Cursor"  # DECTCEM VT220, 1st of 2
TOLD_BY_PACKET[b"\x1B[" b"?1034h"] = "Join Meta"
TOLD_BY_PACKET[b"\x1B[" b"?1049h"] = "Alt Screen"
TOLD_BY_PACKET[b"\x1B[" b"?2004h"] = "Alt Paste"

TOLD_BY_PACKET[b"\x1B[" b"?1l"] = "Normal Cursor Keys (DECCKM)"  # VT100
TOLD_BY_PACKET[b"\x1B[" b"?12l"] = "Steady Cursor"
TOLD_BY_PACKET[b"\x1B[" b"?25l"] = "Hide Cursor"  # DECTCEM VT220, 2nd of 2
# TOLD_BY_PACKET[b"\x1B[" b"?1034l"] = "Split Meta"  # (not seen in traces lately)
TOLD_BY_PACKET[b"\x1B[" b"?1049l"] = "Main Screen"
TOLD_BY_PACKET[b"\x1B[" b"?2004l"] = "Main Paste"

TOLD_BY_PACKET[b"\x1B[" b"27m"] = "Positive SGR"
TOLD_BY_PACKET[b"\x1B[" b"29m"] = "Uncrossed SGR"
TOLD_BY_PACKET[b"\x1B[" b"94m"] = "Bright Blue SGR"
TOLD_BY_PACKET[b"\x1B[" b"m"] = "Exit SGR"

TOLD_BY_PACKET[b"\x1B[" b">4;2m"] = "Enter XTQMODKEYS"
TOLD_BY_PACKET[b"\x1B[" b">4;m"] = "Exit XTQMODKEYS"
TOLD_BY_PACKET[b"\x1B[" b"?4m"] = "Query XTQMODKEYS"

TOLD_BY_PACKET[b"\x1B[" b"22;1t"] = "Push Icon Title"
TOLD_BY_PACKET[b"\x1B[" b"22;2t"] = "Push Window Title"
TOLD_BY_PACKET[b"\x1B[" b"23;1t"] = "Pop Icon Title"
TOLD_BY_PACKET[b"\x1B[" b"23;2t"] = "Pop Window Title"

TOLD_BY_PACKET_KEYS_MINUS = list(TOLD_BY_PACKET.keys())

TOLD_BY_PACKET[b"\x1B"] = "\N{Broken Circle With Northwest Arrow} Esc"  # ⎋


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

    # Split out 1 Escape Sequence begun by the Control Sequence Introducer (CSI)

    if bytes_[:2] == b"\x1B[":
        pattern = b"\x1B\\[([0-9;]*)[^0-9;]"
        m = re.match(pattern, string=bytes_)
        if m:
            packet = m.group(0)

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

    print('with open("{}", "wb") as writing:'.format(path_name))
    for group in groups:
        (repeats, packet) = group

        tail = ""
        told = pty_packet_told(packet)
        if told:
            tail = "  # {}".format(told)
            if "(CUP)" in told:
                tail = "  # {}".format(told.lower())

        if repeats == 1:
            print(dent + r"writing.write({!r}){}".format(packet, tail))
        else:
            print(dent + r"writing.write({} * {!r}){}".format(repeats, packet, tail))


def pty_packet_told(packet):
    """Pick out what the Packet means, else return None"""

    told = None

    if packet in TOLD_BY_PACKET.keys():
        told = TOLD_BY_PACKET[packet]

    elif packet.startswith(b"\x1B["):  # Control Sequence Introducer (CSI)
        if packet.endswith(b"H"):
            told = "Cursor Position (CUP) Y X"
        elif packet.endswith(b"r"):
            told = "Set Scrolling Region (DECSTBM) Y1 Y2"

    return told


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()
