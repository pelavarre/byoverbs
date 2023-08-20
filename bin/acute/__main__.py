#!/usr/bin/env python3

r"""
usage: acute [-h] [--keylog K] [--screenlog S] [WHAT]

reply to keyboard with edits of os copy-paste buffer, dir, file, pipe, or screen

positional arguments:
  WHAT           what dir or file to edit, if not os copy-paste buffer or pipes

options:
  -h, --help     show this help message and exit
  --keylog K     program to replay bytes logged at keyboard
  --screenlog S  program to replay bytes logged at screen

quirks:
  defaults to edit os copy-paste buffer, but accepts pipes in or out or both
  reads keyboard and writes screen at /dev/stderr
  logs keyboard to ~/.ssh/keylog.py, logs screen to ~/.ssh/screenlog.py

examples:
  é  # shows these examples and exits
  é --h  # shows these examples as part of a larger help message and exits
  é --  # edits Os Copy-Paste Buffer
  echo abc def |xargs -n 1 |é -- |cat -etv  # edits Pipe
"""

# code reviewed by people, and by Black and Flake8


import argparse
import os
import pathlib
import shlex
import stat
import subprocess
import sys

import byo
from byo import byoargparse
from byo import byotty

_ = byo, byotty  # auths separate test of unused imports despite Flake8


#
# Run well when called from Sh by people
#


def main():
    """Run well when called from Sh by people"""

    args = parse_acute_py_args()
    main.args = args

    # Record and/or replay our work

    home_dot_ssh_find_else()

    with open(os.path.expanduser("~/.ssh/keylog.py"), "w") as klogger:
        with open(os.path.expanduser("~/.ssh/screenlog.py"), "w") as slogger:
            main.klogger = klogger
            main.slogger = slogger

            # Open, slurp, edit, flush, close

            ibytes = pull_in()
            main.ibytes = ibytes

            main.obytes = b""
            mess_about()

            obytes = main.obytes
            push_out(obytes)

    # todo: empty and/recreate the Log Py as executable hashbang Py, then append


def parse_acute_py_args():
    """Take Words from the Sh Command Line into Acute Py"""

    assert argparse.OPTIONAL == "?"

    parser = byoargparse.ArgumentParser()

    what_help = "what dir or file to edit, if not os copy-paste buffer or pipes"
    keylog_help = "program to replay bytes logged at keyboard"
    screenlog_help = "program to replay bytes logged at screen"

    parser.add_argument("what", metavar="WHAT", nargs="?", help=what_help)
    parser.add_argument("--keylog", metavar="K", help=keylog_help)
    parser.add_argument("--screenlog", metavar="S", help=screenlog_help)

    args = parser.parse_args()  # often prints help & exits zero

    what = args.what

    args.key_argv = None
    if args.keylog:
        args.key_argv = shlex.split(args.keylog)

    args.screen_argv = None
    if args.screenlog:
        args.screen_argv = shlex.split(args.screenlog)

    args.ifile = what
    args.ofile = what
    if args.what is None:
        args.ifile = "/usr/bin/pbpaste" if sys.stdin.isatty() else "/dev/stdin"
        args.ofile = "/usr/bin/pbcopy" if sys.stdout.isatty() else "/dev/stdout"

    return args


def home_dot_ssh_find_else():
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


def pull_in():
    """Copy lotsa Bytes in"""

    args = main.args

    # Read from the Os Copy-Paste Buffer

    if args.ifile == "/usr/bin/pbpaste":  # 'pbpaste' first found at macOS
        ibytes = subprocess_run_stdout(argv=shlex.split(args.ifile))
        return ibytes

    # Read from Dir

    ipath = pathlib.Path(args.ifile)
    if ipath.is_dir():
        raise NotImplementedError("Read from Dir")

    # Read from File or Device

    ibytes = ipath.read_bytes()

    return ibytes


def subprocess_run_stdout(argv):
    """Run the ArgV and capture its Stdout"""

    run = subprocess.run(
        argv, stdin=None, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )

    assert run.returncode == 0, (run.returncode,)
    stdout = run.stdout
    assert not run.stderr, (run.stderr,)

    return stdout


def push_out(obytes):
    """Copy lotsa Bytes out"""

    args = main.args

    # Write to the Os Copy-Paste Buffer

    if args.ofile == "/usr/bin/pbcopy":  # 'pbcopy' first found at macOS
        argv = shlex.split("/usr/bin/pbcopy")
        run = subprocess.run(
            argv, input=obytes, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )

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


def mess_about():
    """Work up the Bytes to go out, from the Bytes that came in"""

    args = main.args
    ibytes = main.ibytes

    # Replay Bytes logged at Screen

    if args.screen_argv:
        screen_bytes = subprocess_run_stdout(args.screen_argv)
        print(screen_bytes, file=sys.stderr)

    # Replay Bytes logged at Keyboard

    if args.key_argv:
        key_bytes = subprocess_run_stdout(args.key_argv)
        print(key_bytes, file=sys.stderr)

    # Reply to Keyboard till Quit

    ichars = ibytes.decode(errors="surrogateescape")
    ochars = ichars.upper()
    obytes = ochars.encode(errors="surrogateescape")

    main.obytes = obytes

    # todo: Replay bytes logged at keyboard slowly over time


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    # byotty.main()  # jitter Sat 19/Aug
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/acute
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
