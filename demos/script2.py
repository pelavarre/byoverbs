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
import string
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
    """Erase and forward each whole Input, before echoing the next"""

    texts = take_in.texts
    holds = take_in.holds
    controls = take_in.controls

    fd = sys.__stdout__.fileno()

    alt_takes = bytearray()
    for take in takes:
        # Stop deferring the erase & forward of a whole Input

        if not controls:
            erasures = len(texts) * b"\b \b"
            os.write(fd, erasures)
            texts.clear()

            alt_takes.extend(holds)
            holds.clear()

        # FIXME: forward old and complete its output, before echo next

        # Echo the new Byte

        take_echoes = one_take_form_echoes(take)
        os.write(fd, take_echoes.encode())

        # Start deferring the erase & forward of a whole Input,
        # or start completing a sequence of Control Bytes

        controls.append(take)
        (some, more) = takes_split_one(controls)

        if some:
            assert not more, more

            control_echoes = some_takes_form_echoes(takes=controls)
            texts.extend(control_echoes)
            holds.extend(controls)
            controls.clear()

    alt_takes = bytes(alt_takes)

    return alt_takes

    # todo: echo the Pt of CSI Pt correctly, especially for Chars outside of US-Ascii


take_in.texts = list()  # what to erase later
take_in.holds = bytearray()  # what to forward later
take_in.controls = bytearray()  # what to complete, then later erase & forward


def some_takes_form_echoes(takes):
    """Choose Chars to echo in place of some Bytes from Keyboard"""

    echoes = ""
    for take in takes:
        more_echoes = one_take_form_echoes(take)
        echoes += more_echoes

    return echoes


def one_take_form_echoes(take):
    """Choose Chars to echo in place of one Byte from Keyboard"""

    assert take in range(0x100), take
    chr_take = chr(take)

    esc_echo = "\N{Broken Circle With Northwest Arrow}"  # ⎋
    control_echo = "\N{Up Arrowhead}"  # ⌃
    shift_echo = "\N{Upwards White Arrow}"  # ⇧

    if take > 0x80:
        echo = "\\x{:02X}".format(take)
    else:
        if take in range(0x00, 0x20) or (take == 0x7F):
            echo = control_echo + chr(take ^ 0x40)  # b"\0" as "⌃@", Delete as "⌃?", etc
            if take == 0x1B:
                echo = esc_echo  # Esc as "⎋"
        elif chr_take in string.ascii_lowercase:
            echo = chr_take.upper()
        elif chr_take in string.ascii_uppercase:
            echo = shift_echo + chr_take
        else:
            echo = chr_take  # b" 0@P`p" etc as " 0@P`p" printable US-Ascii

    return echo


def takes_is_controlling(takes):  # FIXME: unused?
    """Say if Bytes to Screen starts with a Control Sequence"""

    if takes:
        ord_ = takes[0]
        if (ord_ in range(0x00, 0x20)) or (ord_ in range(0x7F, 0xA0)):
            return True


def takes_is_forwardable(takes):  # FIXME: unused?
    """Say if some Bytes from Keyboard should flow on into the Python Pty"""

    if takes[:1] != b"\x1B":
        return True

    if bytes(takes) in CHORDS_BY_TAKES.keys():
        return True


def takes_split_some(takes):  # FIXME: unused?
    """Split out a List of the Texts or Controls, and then remaining Bytes if any"""

    somes = list()
    more = takes
    while more:
        (some, more) = takes_split_one(more)
        if not some:
            break
        somes.append(some)

    return (somes, more)


def takes_split_one(takes):
    """Split out the Text before the next whole Control, else one whole Control"""

    # Take one or more Text Bytes

    texts = bytearray()
    for take in takes:
        if (take in range(0x00, 0x20)) or (take in range(0x7F, 0xA0)):
            break
        texts.append(take)

    # Else take one or more Control Bytes

    controls = bytearray()
    if takes and not texts:
        controls.append(takes[0])

        # Take one Esc Byte and then one more Byte

        if takes[:1] == b"\x1B":
            controls.clear()
            if takes[1:]:
                controls.extend(takes[:2])

                # Take Esc [ and then indefinitely many of b"0123456789:;<=>?"

                if takes[:2] == b"\x1B[":
                    controls.clear()

                    esc = takes[0]
                    left_square_bracket = takes[1]
                    assert esc == 0x1B
                    assert left_square_bracket == ord("[")

                    csi = bytearray(b"\x1B[")
                    for take in takes[2:]:
                        csi.append(take)
                        if take not in range(0x30, 0x40):  # todo: is this CSI Spec?
                            controls.extend(csi)
                            break

    # Split out zero, one, or more Bytes

    some = bytes(texts or controls)
    more = takes[len(some) :]

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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/script2.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
