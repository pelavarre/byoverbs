#!/usr/bin/env python3

"""
usage: cp.py [-i] [-p] [FROM | FROM... TO]

duplicate files or dirs

positional arguments:
  FROM       the old name of a file or dir
  TO         the new name of a file or dir

options:
  --help     show this help message and exit
  -i         stop to ask before replacing file or dir
  -p         copy, don't lose, last-modified date/time stamp and chmod permissions

quirks:
  copies top File off Stack, but keeps its date/time stamp a la:  touch -r FROM TO
  goes well with Cp, Echo, MkDir, Mv, Ls, Rm, RmDir, Touch

examples:
  cp.py --  # backs up top File of Stack

  touch t.txt
  F=t.txt && echo cp -ip $F{,~$(date -r $F +%m%d$(qjd)%H%M)~} |tee /dev/tty |bash

  echo cp -ip "$(ls -1rt |tail -1)"{,~$(date +%m%d$(qjd)%H%M)~}
"""

# cp.py file.txt copied.txt  # copies like ⌘ D of macOS Finder

# code reviewed by People, Black, Flake8, & MyPy


import datetime as dt
import os
import sys

import byotools as byo


def main() -> None:
    """Run as a Sh Verb"""

    # Require one Arg without "-" Dash Options, preceded by a "--" Sep or not

    parm = byo.shlex_parms_one_posarg()
    if not parm:
        if sys.argv[1:] != ["--"]:
            byo.sys_exit()  # prints examples or help lines or exception, and exits

    # Say who's calling

    jqd = byo.subprocess_run_oneline("git config user.initials")
    jqd = jqd if jqd else "jqd"

    # Peek at top of Stack

    (_, _, filenames) = next(os.walk("."))

    peeks = list(_ for _ in filenames if not (_.startswith(".") or _.endswith("~")))
    peeks.sort(key=lambda _: (os.stat(_).st_mtime, _))
    peek = peeks[-1] if peeks else None

    fromfile = parm if parm else peek

    tofile = None
    if fromfile:
        stat = os.stat(fromfile)
        mtime = dt.datetime.fromtimestamp(stat.st_mtime)
        if fromfile.endswith(os.sep) and (fromfile != os.sep):
            rstrip = fromfile.rstrip(os.sep)
            tofile = rstrip + mtime.strftime("~%m%d{jqd}%H%M~").format(jqd=jqd) + os.sep
        else:
            tofile = fromfile + mtime.strftime("~%m%d{jqd}%H%M~").format(jqd=jqd)

    # Choose a Sh Line, else quit

    shline = None
    if fromfile:  # moves a file off the stack
        ttyline = "cp -ip {} {}".format(fromfile, tofile)
        shline = ttyline
    else:
        raise NotImplementedError("cp.py: no files found here outside of '.*' and '*~'")

    # Run the chosen Sh Line, and return

    byo.subprocess_shline_exit_if(shline)


main()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/cp.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
