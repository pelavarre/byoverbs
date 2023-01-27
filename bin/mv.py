#!/usr/bin/env python3

"""
usage: mv.py [-i] [FROM | FROM... TO]

rename files or dirs

positional arguments:
  FROM       the old name of a file or dir
  TO         the new name of a file or dir

options:
  --help     show this help message and exit
  -i         stop to ask before replacing file or dir

quirks:
  moves Image Files into __jqd-trash__/., for 'git config user.initials'
  moves the last Modified File off the Stack, out to ~%m%djqd%H%M~
  goes well with Cp, MkDir, Mv, Ls, Rm, RmDir, Touch

examples:
  mv.py  # show these examples and exit
  mv.py --h  # show help lines and exit (more reliable than -h)
  mv.py --  # moves Image Files into the Trash, else moves last File off Stack

  echo mv -i "$(ls -1rt |tail -1)"{,~$(date +%m%djqd%H%M)~} __jqd-trash__/.
  echo mv *.jpeg *.jpg *.png *.svg __jqd-trash__/.
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

    # Look for a Trash Can

    trash_reldir = "__{jqd}-trash__".format(jqd=jqd)
    main.trash_reldir = trash_reldir
    trash_isdir_here = os.path.isdir(trash_reldir)

    # Look for File Ext's to archive

    image_exts = ".jpeg .jpg .png .svg".split()

    (_, _, filenames) = next(os.walk("."))

    exts_set = set()
    for filename in filenames:
        ext = os.path.splitext(filename)[-1]
        if ext in image_exts:
            exts_set.add(ext)

    exts = sorted(exts_set)

    patterns = list("*{}".format(_) for _ in exts)
    if not trash_isdir_here:
        patterns = None

    # Peek at top of Stack

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

    # Runs some Sh Lines, else quit

    if patterns and not parm:  # cleans out the trash

        mv_ttyline = "mv -i {} {}/.".format(" ".join(patterns), trash_reldir)
        byo.subprocess_ttyline_exit_if(mv_ttyline)

        ls_shline = "ls"
        byo.subprocess_shline_exit_if(ls_shline)
        byo.sys_stderr_print("+")

    elif fromfile:  # moves one file off the stack

        mv_ttyline = "mv -i {} {}".format(fromfile, tofile)
        mv_shline = mv_ttyline
        byo.subprocess_shline_exit_if(mv_shline)

    else:

        raise NotImplementedError("mv.py: no files found here outside of '.*' and '*~'")


main()
