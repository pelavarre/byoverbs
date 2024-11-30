#!/usr/bin/env python3

r"""
usage: pbuffer.py [-h] [--verbose] [SHVERB]

emulate macOS PBCopy & PBPaste at ~/pbuffer.bin

positional arguments:
  SHVERB      'pbpaste' to read, 'pbpaste' to write ~/pbuffer.bin

options:
  -h, --help  show this help message and exit
  --verbose   say more

quirks:
  not yet tested with:  chmod go-rwx ~/pbuffer.bin
  not yet tested with:  rm -fr ~/pbuffer.bin && ln -s ... ~/pbuffer.bin
  defaults to 'pbpaste' copy to Stdout, if Stdin is Tty,
  else defaults to 'pbcopy' copy from Stdin, if Stdout is Tty,
  else defaults to 'tee >(pbcopy)' forward and capture Stdin

examples:
  bin/pbcopy  # copies Stdin to ~/pbuffer.bin
  bin/pbpaste  # copies ~/pbuffer.bin to Stdout
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


_: object  # '_: object' tells MyPy to accept '_ =' tests across two and more Datatypes


_ = dict[str, int] | None  # new since Oct/2021 Python 3.10


#
# Run well when called from Sh by people
#


@dataclasses.dataclass
class PBufferArgs:
    """Name the Command-Line Arguments of PBuffer Py"""

    shverb: str | None
    pbverb: str

    verbose: int | None


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

    # 2 ) Copy from Stdin, or to Stdout, or from Stdin to Stdout but tee

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

    shverb_help = "'pbpaste' to read, 'pbpaste' to write ~/pbuffer.bin"
    verbose_help = "say more"

    parser.add_argument("shverb", metavar="SHVERB", nargs="?", help=shverb_help)
    parser.add_argument("--verbose", action="count", help=verbose_help)

    ns = parser.parse_args_else()  # often prints help & exits zero

    # Auto-correct the Sh Args

    shverb = os.path.basename(ns.shverb)
    if shverb in ("pbpaste", "pbcopy"):
        pbverb = shverb
    else:
        pbverb = tty_shverb

    # Succeed

    args = PBufferArgs(**vars(ns), pbverb=pbverb)
    if args.verbose:
        print(f"{args=}", file=sys.stderr)

    return args


#
# Work well with an Os Copy-Paste Buffer of Bytes, or with some emulation thereof
#


def do_pbpaste(pbpaste_else) -> None:
    """Copy ~/pbuffer.bin to Stdout"""

    # Fall back to the Os Copy-Paste Buffer of Bytes

    argv = [pbpaste_else]
    if pbpaste_else:
        print("+ pbpaste", file=sys.stderr)
        subprocess.run(argv, check=True)
        return

    # Substitute Emulation of Dump Buffer to Stdout

    ofd = sys.stdout.fileno()

    bin_path = pathlib.Path.home() / "pbuffer.bin"
    if not bin_path.exists():
        bin_path.write_bytes(b"")

    bin_bytes = bin_path.read_bytes()  # sponges
    os.write(ofd, bin_bytes)


def do_pbcopy(pbcopy_else) -> None:
    """Copy Stdin to ~/pbuffer.bin"""

    # Fall back to the Os Copy-Paste Buffer of Bytes

    argv = [pbcopy_else]
    if pbcopy_else:
        print("+ pbcopy", file=sys.stderr)
        subprocess.run(argv, check=True)
        return

    # Substitute Emulation of Load Buffer from Stdin

    bin_path = pathlib.Path.home() / "pbuffer.bin"
    if not bin_path.exists():
        bin_path.write_bytes(b"")

    ipath = pathlib.Path("/dev/stdin")
    ibytes = ipath.read_bytes()  # sponges

    bin_path.write_bytes(ibytes)


def do_tee_pbcopy(pbcopy_else) -> None:
    """Copy Stdin to Stdout and to ~/pbuffer.bin"""

    # Fall back to the Os Copy-Paste Buffer of Bytes

    argv = shlex.split("bash -c 'tee >(pbcopy)'")  # Bash'ism
    if pbcopy_else:
        print("+ tee >(pbcopy)", file=sys.stderr)
        subprocess.run(argv, check=True)
        return

    # Substitute Emulation of Load Buffer from Stdin, and then dump to Stdout

    ofd = sys.stdout.fileno()

    bin_path = pathlib.Path.home() / "pbuffer.bin"
    if not bin_path.exists():
        bin_path.write_bytes(b"")

    ipath = pathlib.Path("/dev/stdin")
    ibytes = ipath.read_bytes()  # sponges

    bin_path.write_bytes(ibytes)  # todo: File before Stdout, or Stdout before File?
    os.write(ofd, ibytes)


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/pbuffer.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
