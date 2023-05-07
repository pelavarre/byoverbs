#!/usr/bin/env python3

"""
usage: script.py [-h]

record, replay, & auto-correct the bytes streaming to screen from keyboard

options:
  -h, --help  show this help message and exit

quirks:
  sets you up to bold or color your Sh Input Lines
    like type ⎋[1m to bold your input, ⎋[m to stop
    like type ⎋[34m to turn your input blue, ⎋[31m red, etc, ⎋[m to stop
  exports COLUMNS & LINES if opening a Python Pty changes Os Get_Terminal_Size,
    even while ⎋[18t will still type out ⎋[8;$LINES;${COLUMNS}t

docs:
  https://en.wikipedia.org/wiki/ANSI_escape_code
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html

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
                while True:
                    read_some = os.read(fd, 0x400)
                    keylog.write(read_some)
                    keylog.flush()

                    alt_read_some = take_in(read_some)
                    if alt_read_some:
                        return alt_read_some

            def screen_recorder(fd):
                read_some = os.read(fd, 0x400)
                screenlog.write(read_some)
                screenlog.flush()
                return read_some

            pty.spawn(shargv, master_read=screen_recorder, stdin_read=key_logger)

    # compare with 'def read' at https://docs.python.org/3/library/pty.html


def take_in(read_some):
    states = take_in.states
    state = states[0] if states else None

    func_by_state = dict(
        {
            None: state_none,
            1: state_1,
            2: state_2,
            3: state_3,
            4: state_4,
            5: state_5,
        }
    )

    func = func_by_state[state]
    alt_read_some = func(read_some)

    return alt_read_some


take_in.states = list()
take_in.screen_bytes = b""


def state_none(key_bytes):
    states = take_in.states
    if key_bytes == b"\x1B":
        states[::] = [1]
        take_in.screen_bytes = b""
        take_in.screen_bytes += key_bytes
        sys.stdout.write("⎋")
        sys.stdout.flush()
        return b""
    return key_bytes


def state_1(key_bytes):
    states = take_in.states
    if key_bytes == b"[":
        states[::] = [2]
        take_in.screen_bytes = b"\x1B["
        sys.stdout.write("[")
        sys.stdout.flush()
        return b""
    states[::] = list()
    sys.stdout.write(len(take_in.screen_bytes) * "\b \b")
    sys.stdout.flush()
    return key_bytes


def state_2(key_bytes):
    states = take_in.states
    if (len(key_bytes) == 1) and (key_bytes in b"0123456789"):
        states[::] = [3]
        take_in.screen_bytes += key_bytes
        sys.stdout.write(key_bytes.decode())
        sys.stdout.flush()
        return b""
    if key_bytes == b"m":
        states[::] = [5]
        take_in.screen_bytes += key_bytes
        sys.stdout.write("m")
        sys.stdout.flush()
        return b""
    states[::] = list()
    sys.stdout.write(len(take_in.screen_bytes) * "\b \b")
    sys.stdout.flush()
    return key_bytes


def state_3(key_bytes):
    states = take_in.states
    if (len(key_bytes) == 1) and (key_bytes in b"0123456789"):
        states[::] = [4]
        take_in.screen_bytes += key_bytes
        sys.stdout.write(key_bytes.decode())
        sys.stdout.flush()
        return b""
    if key_bytes == b"m":
        states[::] = [5]
        take_in.screen_bytes += key_bytes
        sys.stdout.write("m")
        sys.stdout.flush()
        return b""
    states[::] = list()
    sys.stdout.write(len(take_in.screen_bytes) * "\b \b")
    sys.stdout.flush()
    return key_bytes


def state_4(key_bytes):
    states = take_in.states
    if key_bytes == b"m":
        states[::] = [5]
        take_in.screen_bytes += key_bytes
        sys.stdout.write("m")
        sys.stdout.flush()
        return b""
    states[::] = list()
    sys.stdout.write(len(take_in.screen_bytes) * "\b \b")
    sys.stdout.flush()
    return key_bytes


def state_5(key_bytes):
    states = take_in.states
    states[::] = list()
    sys.stdout.write(len(take_in.screen_bytes) * "\b \b")
    sys.stdout.write(take_in.screen_bytes.decode())
    sys.stdout.flush()
    return key_bytes


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/script.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
