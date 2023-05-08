#!/usr/bin/env python3

"""
usage: script.py [-h]

record, replay, & auto-correct the bytes streaming to screen from keyboard

options:
  -h, --help  show this help message and exit

quirks:
  visibly echoes ⌃? Delete, ⌃H Backspace, ⌃I Tab, ⌃M Return, ⎋ Escape, etc
    often pressing ^@ will authorize an Echo without adding another Echo
  sets you up to bold or color your Sh Input Lines
    like type ⎋[1m to bold your input, ⎋[m to stop
    like type ⎋[34m to turn your input blue, ⎋[31m red, etc, ⎋[m to stop
  exports COLUMNS & LINES if opening a Python Pty changes Os Get_Terminal_Size,
    even while ⎋[18t will still type out ⎋[8;$LINES;${COLUMNS}t
  works well with Bash and Zsh calls to redraw the Screen or Screen Row
    bind C-l:clear-screen
    bind C-g:redraw-current-line
    bindkey "^L" clear-screen  && : :
    bindkey "^G" redisplay  && : :

docs:
  https://en.wikipedia.org/wiki/ANSI_escape_code
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
  https://unicode.org/charts/PDF/U0000.pdf
  https://unicode.org/charts/PDF/U0080.pdf

examples:
  ./demos/script.py --
    exit
"""

# code reviewed by people and by Black, Flake8, & Flake8-Import-Order


import ast
import os
import pathlib
import pty
import shlex
import sys

import byoverbs.bin.byotools as byo


OS_ENV_VARS = "COLUMNS LINES SHELL".split()


def main():
    """Run from the Sh Command Line"""

    parser = byo.ArgumentParser()
    parser.parse_args()  # often prints help & exits

    #

    to_path = os_find_not_exists("typescript")  # classic Unix defaults to replace
    from_path = os_find_not_exists("keylog")  # classic Unix defaults to omit

    os_putenv_terminal_size_if()

    print("Script started, keylog is {}, screenlog is {}".format(from_path, to_path))

    copy_until(to_path, from_path=from_path)

    print()  # macOS 'script' inserts this blank line, Linux 'script' doesn't
    print("Script done, keylog is {}, screenlog is {}".format(from_path, to_path))


def os_find_not_exists(pathname):
    """Search out the next Output File that does not yet exist"""

    find = pathlib.Path(pathname)

    index = 1
    while find.exists():
        alt_pathname = "{}.{}".format(index, pathname)
        find = pathlib.Path(alt_pathname)
        index += 1

    return find


def os_putenv_terminal_size_if():
    """Fall back to Put Env COLUMNS & LINES, if Python Pty zeroes Get_Terminal_Size"""

    assert "COLUMNS" in OS_ENV_VARS
    assert "LINES" in OS_ENV_VARS

    # Sample Terminal-Size inside a Python Pty Pseudo-Terminal

    py = "import os; print(tuple(os.get_terminal_size()))"
    shline = "python3 -c {!r}".format(py)
    shargv = shlex.split(shline)

    read = bytearray()

    def os_read_some(fd):
        read_some = os.read(fd, 0x400)
        read.extend(read_some)
        return b""

    pty.spawn(shargv, master_read=os_read_some)

    read_chars = read.decode()
    pty_size = ast.literal_eval(read_chars)

    # Fall back to Put Env COLUMNS & LINES, if Python Pty zeroes Get_Terminal_Size

    size = os.get_terminal_size()

    if pty_size != size:
        assert pty_size == (0, 0), pty_size  # ordinary in May/2023

        os.putenv("COLUMNS", str(size.columns))
        os.putenv("LINES", str(size.lines))

    # Window Resize may revive 'stty size' after:  stty rows 0 && stty cols 0
    # Terminal Scroll may fail after:  stty rows 0 && seq 987 && vi +:q!
    # Zsh Echo may fail inside Python Pty after:  unset COLUMNS LINES && zsh

    # todo: take IsATtty from Stdout/ Stderr/ Stdin


def copy_until(to_path, from_path):
    """Stream Bytes to Screen from Keyboard till Sh SubProcess Quits"""

    assert "SHELL" in OS_ENV_VARS

    default_sh = "sh"
    shverb = os.environ.get("SHELL", default_sh)
    shargv = [shverb]

    with open(from_path, "wb") as keylog:
        with open(to_path, "wb") as screenlog:

            def key_logger(fd):
                """Log and copy Bytes in from the Keyboard"""

                while True:
                    reads = os.read(fd, 0x400)
                    keylog.write(reads)
                    keylog.flush()

                    alt_reads = take_in(takes=reads)
                    if alt_reads:
                        return alt_reads

            def screen_recorder(fd):
                """Log and copy Bytes out to the Screen"""

                reads = os.read(fd, 0x400)
                screenlog.write(reads)
                screenlog.flush()

                return reads

            pty.spawn(shargv, master_read=screen_recorder, stdin_read=key_logger)

    # compare with 'def read' at https://docs.python.org/3/library/pty.html


def take_in(takes):
    """Echo slow Control Sequences visibly, before forwarding them"""

    deferrals = take_in.deferrals
    echoes = take_in.echoes

    fd = sys.__stdout__.fileno()

    # Take one Byte at a time

    forwardables = bytearray()

    pops = bytearray(takes)
    while pops:
        assert bool(echoes) == bool(deferrals), (bool(echoes), bool(deferrals))

        # Defer and echo each Byte of a Control Sequence

        if deferrals or takes_is_controlling(pops):
            while pops:
                (some, more) = takes_split(deferrals)
                if some:
                    break

                pop = pops.pop(0)
                deferrals.append(pop)

                pop_echoes = take_form_echoes(pop)
                os.write(fd, pop_echoes.encode())
                echoes.extend(pop_echoes)

        # Erase the Echoes of the Control Sequence, when more Bytes arrive

        (some, more) = takes_split(deferrals)
        assert (not some) or (not more), (deferrals, some, more)

        if some:
            assert takes_is_controlling(some)
            if pops:
                erasures = len(echoes) * b"\b \b"
                echoes.clear()
                os.write(fd, erasures)

                # Also write or forward the Control Sequence

                deferrals.clear()
                if not takes_is_forwardable(some):
                    os.write(fd, some)
                    continue

                forwardables.extend(some)

        # Forward all the Bytes arriving that don't start with a Control Sequence

        if pops:
            assert not deferrals, deferrals
            forwardables.extend(pops)
            pops.clear()

    # Succeed

    alt_takes = bytes(forwardables)

    return alt_takes

    # todo: echo the Pt of CSI Pt correctly, especially for Chars outside of US-Ascii


take_in.deferrals = bytearray()
take_in.echoes = list()


def take_form_echoes(take):
    """Choose Chars to echo in place of Bytes from Keyboard"""

    assert take in range(0x100), take

    esc_echo = "\N{Broken Circle With Northwest Arrow}"  # ⎋
    control_echo = "\N{Up Arrowhead}"  # ⌃

    if take > 0x80:
        echo = "\\x{:02X}".format(take)
    else:
        if take in range(0x00, 0x20) or (take == 0x7F):
            echo = control_echo + chr(take ^ 0x40)  # b"\0" as "⌃@", Delete as "⌃?", etc
            if take == 0x1B:
                echo = esc_echo  # Esc as "⎋"
        else:
            echo = chr(take)  # b" 0@P`p" etc as " 0@P`p" printable US-Ascii

    return echo


def takes_is_controlling(takes):
    """Say if Bytes to Screen starts with a Control Sequence"""

    if takes:
        ord_ = takes[0]
        if (ord_ in range(0x00, 0x20)) or (ord_ in range(0x7F, 0xA0)):
            return True


def takes_is_forwardable(takes):
    """Say if some Bytes from Keyboard should flow on into the Python Pty"""

    if takes[:1] != b"\x1B":
        return True

    if bytes(takes) in CHORDS_BY_TAKES.keys():
        return True


def takes_split(takes):
    """Split out a Control Sequence starting some Bytes, else before next Sequence"""

    # Take one or more Bytes that don't start a Control Sequence

    starts = bytearray()

    pops = bytearray(takes)
    while pops:
        pop = pops.pop(0)
        controlling = (pop in range(0x00, 0x20)) or (pop in range(0x7F, 0xA0))
        if controlling:
            pops.insert(0, pop)
            break
        starts.append(pop)

    # Take a single Control Byte

    if not starts:
        starts = bytearray(takes[:1])

        # Take one Esc Byte and then one more Byte

        if takes[:1] == b"\x1B":
            starts = bytearray()
            if takes[1:]:
                starts = bytearray(takes[:2])

                # Take Esc [ and then indefinitely many of b"0123456789:;<=>?"

                if takes[:2] == b"\x1B[":
                    starts = bytearray()

                    esc = pops.pop(0)
                    left_square_bracket = pops.pop(0)
                    assert esc == 0x1B
                    assert left_square_bracket == ord("[")

                    csi = bytearray(b"\x1B[")
                    while pops:
                        pop = pops.pop(0)
                        csi.append(pop)
                        if pop not in range(0x30, 0x40):  # todo: is this CSI Spec?
                            starts.extend(csi)
                            break

    some = bytes(starts)
    more = takes[len(starts) :]

    return (some, more)


CHORDS_BY_TAKES = dict()

CHORDS_BY_TAKES[b"\x1Bb"] = "⌥←"
CHORDS_BY_TAKES[b"\x1Bf"] = "⌥→"
CHORDS_BY_TAKES[b"\x1B[A"] = "↑"
CHORDS_BY_TAKES[b"\x1B[B"] = "↓"
CHORDS_BY_TAKES[b"\x1B[C"] = "→"
CHORDS_BY_TAKES[b"\x1B[D"] = "←"
CHORDS_BY_TAKES[b"\x1B[1;2C"] = "⇧→"
CHORDS_BY_TAKES[b"\x1B[1;2D"] = "⇧←"


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/script.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
