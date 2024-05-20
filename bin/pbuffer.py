#!/usr/bin/env python3

r"""
usage: pbuffer.py [-h] [SHVERB]

emulate macOS PBCopy & PBPaste at ~/cv

positional arguments:
  SHVERB      'pbpaste' to read ~/cv, 'pbpaste' to write ~/cv

options:
  -h, --help  show this help message and exit

quirks:
  not yet tested with:  chmod go-rwx ~/cv
  not yet tested with:  rm -fr ~/cv && ln -s ... ~/cv
  defaults to 'pbpaste' copy to Stdout, if Stdin is Tty,
  else defaults to 'pbcopy' copy from Stdin, if Stdout is Tty,
  else defaults to 'tee >(pbcopy)' forward and capture Stdin

examples:
  bin/pbcopy  # copies Stdin to ~/cv
  bin/pbpaste  # copies ~/cv to Stdout
"""

# code reviewed by People, Black, Flake8, & MyPy

import argparse
import dataclasses
import os
import pathlib
import shlex
import shutil
import subprocess
import sys

import byotools as byo

... == dict[str, int]  # new since Oct/2020 Python 3.9  # type: ignore
... == byo  # type: ignore


#
# Run well when called from Sh by people
#


@dataclasses.dataclass
class PBufferArgs:
    """Name the Command-Line Arguments of PBuffer Py"""

    shverb: str | None
    pbverb: str


def main() -> None:
    """Run well when called from Sh by people"""

    args = parse_pbuffer_py_args()

    # 1 ) Look for 'pbpaste' and 'pbcopy' in the Sh Path, but outside our Dir

    argv_0_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    which_pbcopy_else = shutil.which("pbcopy")
    which_pbpaste_else = shutil.which("pbpaste")

    pbcopy_else = which_pbcopy_else
    if which_pbcopy_else:
        pbcopy_dir = os.path.dirname(os.path.realpath(which_pbcopy_else))
        if pbcopy_dir == argv_0_dir:
            pbcopy_else = None

    pbpaste_else = which_pbpaste_else
    if which_pbpaste_else:
        pbpaste_dir = os.path.dirname(os.path.realpath(which_pbpaste_else))
        if pbpaste_dir == argv_0_dir:
            pbpaste_else = None

    # 2 ) Copy Stdin to ~/cv, or ~/cv to Stdout, or Stdin to Stdout and to ~/cv

    pbverb = args.pbverb
    if pbverb == "pbpaste":
        do_pbpaste(pbpaste_else)
    elif pbverb == "pbcopy":
        do_pbcopy(pbcopy_else)
    else:
        assert pbverb == "tee >(pbcopy)", (pbverb, args)
        do_tee_pbcopy(pbcopy_else)


def parse_pbuffer_py_args() -> PBufferArgs:
    """Take Words from the Sh Command Line into PBuffer Py"""

    assert argparse.OPTIONAL == "?"

    # Choose defaults for running as head, tail, and middle of Sh Pipe

    if sys.stdin.isatty():
        tty_shverb = "pbpaste"  # pbuffer.py outside of Sh Pipe, or:  pbuffer.py |...
    elif sys.stdout.isatty():
        tty_shverb = "pbcopy"  # ... |pbuffer.py
    else:
        tty_shverb = "tee >(pbcopy)"  # ... |pbuffer.py |...

    # Doc the Sh Args & take them in

    parser = byo.ArgumentParser()
    shverb_help = "'pbpaste' to read ~/cv, 'pbpaste' to write ~/cv"
    parser.add_argument("shverb", metavar="SHVERB", nargs="?", help=shverb_help)

    ns = parser.parse_args_else()  # often prints help & exits zero

    # Auto-correct the Sh Args

    shverb = ns.shverb
    if shverb in ("pbpaste", "pbcopy"):
        pbverb = shverb
    else:
        pbverb = tty_shverb

    # Succeed

    args = PBufferArgs(**vars(ns), pbverb=pbverb)

    return args


#
# Work well with an Os Copy-Paste Buffer of Bytes, or with some emulation thereof
#


def do_pbpaste(pbpaste_else) -> None:
    """Copy ~/cv to Stdout"""

    # Fall back to the Os Copy-Paste Buffer of Bytes

    argv = [pbpaste_else]
    if pbpaste_else:
        print("+ pbpaste", file=sys.stderr)
        subprocess.run(argv, check=True)
        return

    # Substitute Emulation of Dump Buffer to Stdout

    ofd = sys.stdout.fileno()

    cv_path = pathlib.Path.home() / "cv"
    if not cv_path.exists():
        cv_path.write_bytes(b"")

    cv_bytes = cv_path.read_bytes()  # sponges
    os.write(ofd, cv_bytes)


def do_pbcopy(pbcopy_else) -> None:
    """Copy Stdin to ~/cv"""

    # Fall back to the Os Copy-Paste Buffer of Bytes

    argv = [pbcopy_else]
    if pbcopy_else:
        print("+ pbcopy", file=sys.stderr)
        subprocess.run(argv, check=True)
        return

    # Substitute Emulation of Load Buffer from Stdin

    cv_path = pathlib.Path.home() / "cv"
    if not cv_path.exists():
        cv_path.write_bytes(b"")

    ipath = pathlib.Path("/dev/stdin")
    ibytes = ipath.read_bytes()  # sponges

    cv_path.write_bytes(ibytes)


def do_tee_pbcopy(pbcopy_else) -> None:
    """Copy Stdin to Stdout and to ~/cv"""

    # Fall back to the Os Copy-Paste Buffer of Bytes

    argv = shlex.split("bash -c 'tee >(pbcopy)'")  # Bash'ism
    if pbcopy_else:
        print("+ tee >(pbcopy)", file=sys.stderr)
        subprocess.run(argv, check=True)
        return

    # Substitute Emulation of Load Buffer from Stdin, and then dump to Stdout

    ofd = sys.stdout.fileno()

    cv_path = pathlib.Path.home() / "cv"
    if not cv_path.exists():
        cv_path.write_bytes(b"")

    ipath = pathlib.Path("/dev/stdin")
    ibytes = ipath.read_bytes()  # sponges

    cv_path.write_bytes(ibytes)  # todo: consider Stdout before Cv_Path
    os.write(ofd, ibytes)


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pbuffer.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
