#!/usr/bin/env python3

"""
usage: sed.py [--h] ...

copy input to output but edit it along the way

options:
  --help  show this help message and exit

quirks:
  macOs Sh defines PbPaste & PbCopy, life is harder elsewhere

examples:

  sed.py  # show these examples and exit
  sed.py --  # prefix each line with "-- " and suffix each line with " --"

  pbpaste |sed 's,^,-- ,' |sed 's,$, --,' |pbcopy
"""

import byotools as byo


def main():
    """Run as a Sh Verb"""

    # Require one Arg, preceded by a "--" Sep or not

    parm = byo.shlex_parms_one_posarg()

    # Choose a Sh Line, else quit

    if not parm:
        byo.sys_exit_if()  # prints examples or help lines and exits, else returns

    ttyline = "pbpaste |sed 's,^,-- ,' |sed 's,$, --,' |pbcopy"
    shline = "bash -c {!r}".format(ttyline)

    # Run the chosen Sh Line, and return

    byo.sys_stderr_print("+ {}".format(ttyline))
    byo.subprocess_run(shline)


main()
