r"""
usage: optionee [-h] [--keylog K] [--screenlog S] [WHAT]

reply to keyboard with edits of os copy-paste buffer, dir, file, pipe, or screen

positional arguments:
  WHAT           what dir or file to edit, if not os copy-paste buffer or pipes

options:
  -h, --help     show this help message and exit
  --keylog K     program to replay bytes logged at keyboard
  --screenlog S  program to replay bytes logged at screen

quirks:
  defaults to edit os copy-paste buffer, but accepts pipes in or out or both
  reads keyboard and writes screen at /dev/stderr (unlike 'shutil.get_terminal_size')
  logs keyboard to ~/.ssh/keylog.py, logs screen to ~/.ssh/screenlog.py

related tests:
  PYTHONPATH=bin/optionee python3 bin/optionee/byo/byotty.py --
  PYTHONPATH=bin/optionee python3 bin/optionee/byo/byotermios.py --
  ls -AdhlF -rt ~/.ssh/*log.py

examples:
  é  # shows these examples and exits
  é --h  # shows these examples as part of a larger help message and exits
  optionee --for=cxce WHAT  # edit one Sh Command to run when saved
  echo abc def |xargs -n 1 |é -- |cat -etv  # edits Pipe
  echo abc def |pbcopy
  pbpaste && é --  # edits Os Copy-Paste Buffer
"""

# code reviewed by People, Black, Flake8, & MyPy


import argparse
import dataclasses
import os
import pathlib
import shlex
import stat
import subprocess
import sys
import time
import typing

import byo
from byo import byoargparse
from byo import byotermios
from byo import byotty


... == dict[str, int]  # new since Oct/2020 Python 3.9
... == byo, byotermios, byotty, time  # ducks Flake8 F401 imported.but.unused


#
# Run well when called from Sh by people
#


@dataclasses.dataclass
class OptioneeArgs:
    """Name the Command-Line Arguments of Optionee Dir"""

    what_else: str | None
    keylog_else: str | None
    screenlog_else: str | None

    key_argv_else: list[str] | None
    screen_argv_else: list[str] | None

    ifile: str
    ofile: str


@dataclasses.dataclass
class Main:
    """Open up a shared workspace for the Code of this Py File"""

    args: OptioneeArgs  # parsed Sh Args
    ibytes: bytes  # the Bytes read as Input
    obytes: bytes  # the Bytes to write as Output
    klogger: typing.TextIO  # the Stream to log Keyboard Reads into
    slogger: typing.TextIO  # the Stream to log Screen Writes into


def main() -> None:
    """Run well when called from Sh by people"""

    args = parse_optionee_dir_args()
    Main.args = args

    # Record and/or replay our work

    home_dot_ssh_find_else()

    with open(os.path.expanduser("~/.ssh/keylog.py"), "w") as klogger:
        with open(os.path.expanduser("~/.ssh/screenlog.py"), "w") as slogger:
            Main.klogger = klogger
            Main.slogger = slogger

            # Open, slurp, edit, flush, close

            ibytes = pull_in()
            Main.ibytes = ibytes

            Main.obytes = b""
            mess_about()

            obytes = Main.obytes
            push_out(obytes)

    # todo: empty and/recreate the Log Py as executable hashbang Py, then append


def parse_optionee_dir_args() -> OptioneeArgs:
    """Take Words from the Sh Command Line into Optionee Dir"""

    assert argparse.OPTIONAL == "?"

    parser = byoargparse.ArgumentParser()

    what_help = "what dir or file to edit, if not os copy-paste buffer or pipes"
    keylog_help = "program to replay bytes logged at keyboard"
    screenlog_help = "program to replay bytes logged at screen"

    parser.add_argument("what", metavar="WHAT", nargs="?", help=what_help)
    parser.add_argument("--keylog", metavar="K", help=keylog_help)
    parser.add_argument("--screenlog", metavar="S", help=screenlog_help)

    ns = parser.parse_args_else()  # often prints help & exits zero

    key_argv_else = None
    if ns.keylog:
        key_argv_else = shlex.split(ns.keylog)

    screen_argv_else = None
    if ns.screenlog:
        screen_argv_else = shlex.split(ns.screenlog)

    ifile = ns.what
    ofile = ns.what
    if ns.what is None:
        ifile = "pbpaste" if sys.stdin.isatty() else "/dev/stdin"
        ofile = "pbcopy" if sys.stdout.isatty() else "/dev/stdout"

    # Succeed

    args = OptioneeArgs(
        what_else=ns.what,
        keylog_else=ns.keylog,
        screenlog_else=ns.screenlog,
        key_argv_else=key_argv_else,
        screen_argv_else=screen_argv_else,
        ifile=ifile,
        ofile=ofile,
    )

    return args


def home_dot_ssh_find_else() -> None:
    """Find else make the 'drwx------' ~/.ssh/"""

    dirname = os.path.expanduser("~/.ssh")
    dpath = pathlib.Path(dirname)
    if not dpath.is_dir():
        os.mkdir(dirname)

        stale_stat = os.stat(dirname)
        stale_mode = stale_stat.st_mode

        fresh_mode = stale_mode
        fresh_mode = fresh_mode & ~(stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)
        fresh_mode = fresh_mode & ~(stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)

        os.chmod(dirname, mode=fresh_mode)


def pull_in() -> bytes:
    """Copy lotsa Bytes in"""

    args = Main.args

    # Read from the Os Copy-Paste Buffer

    if args.ifile == "pbpaste":  # 'pbpaste' first found at macOS
        ibytes = subprocess_run_stdout_bytes(argv=shlex.split(args.ifile))
        return ibytes

    # Read from Dir

    ipath = pathlib.Path(args.ifile)
    if ipath.is_dir():
        raise NotImplementedError("Read from Dir")

    # Read from File or Device

    ibytes = ipath.read_bytes()

    return ibytes


def subprocess_run_stdout_bytes(argv) -> bytes:
    """Run the ArgV and capture its Stdout"""

    run = subprocess.run(argv, stdin=None, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    assert run.returncode == 0, (run.returncode,)
    stdout = run.stdout
    assert not run.stderr, (run.stderr,)

    return stdout

    # todo: 'stdin=None' is not 'stdin=subprocess.PIPE', but here now do we care?


def push_out(obytes) -> None:
    """Copy lotsa Bytes out"""

    args = Main.args

    # Write to the Os Copy-Paste Buffer

    if args.ofile == "pbcopy":  # 'pbcopy' first found at macOS
        argv = shlex.split("pbcopy")
        run = subprocess.run(argv, input=obytes, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        assert run.returncode == 0, (run.returncode,)
        assert not run.stdout, (run.stdout,)
        assert not run.stderr, (run.stderr,)

        return

    # Write to Dir

    opath = pathlib.Path(args.ofile)
    if opath.is_dir():
        raise NotImplementedError("Write to Dir")

    # Read to File or Device

    opath = pathlib.Path(args.ofile)
    opath.write_bytes(obytes)


#
# Mess about with Memory, after reading Bytes in, before writing Bytes out
#


def mess_about() -> None:
    """Work up the Bytes to go out, from the Bytes that came in"""

    args = Main.args
    ibytes = Main.ibytes

    # Replay Bytes logged at Screen

    if args.screen_argv_else:
        screen_bytes = subprocess_run_stdout_bytes(args.screen_argv_else)
        print(screen_bytes, file=sys.stderr)

    # Replay Bytes logged at Keyboard

    if args.key_argv_else:
        key_bytes = subprocess_run_stdout_bytes(args.key_argv_else)
        print(key_bytes, file=sys.stderr)

    # Reply to Keyboard till Quit

    ichars = ibytes.decode(errors="surrogateescape")
    if ichars != ichars.casefold():
        ochars = ichars.casefold()
    else:
        ochars = ichars.upper()
    obytes = ochars.encode(errors="surrogateescape")

    Main.obytes = obytes

    # todo: Replay bytes logged at keyboard slowly over time


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    sys.stdout.write("xyz\b\b\b")
    sys.stdout.flush()

    time.sleep(0.3)

    main()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/optionee/
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
