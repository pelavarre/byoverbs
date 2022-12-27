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
  -p         copy, don't fabricate, last-modified date/time stamp and chmod permissions

quirks:
  moves Jpeg, Jpg, Png Files into __jqd-trash__/., for 'git config user.initials'
  moves the last Modified File off the Stack, out to ~%m%djqd%H%M~
  copies last-modified date/time stamp as faithfully as:  touch -r FROM TO
  goes well with Cp, MkDir, Mv, Ls, Rm, RmDir, Touch

examples:
  cp.py  # show these examples and exit
  cp.py --h  # show help lines and exit (more reliable than -h)
  cp.py --  # duplicates last File of Stack

  echo cp -ip "$(ls -1rt |tail -1)"{,~$(date +%m%djqd%H%M)~}
"""

import datetime as dt
import os
import sys

import byotools as byo


def main():
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

    byo.subprocess_exit_run_if_shline(shline)


main()
