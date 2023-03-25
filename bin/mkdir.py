#!/usr/bin/env python3

"""
usage: mkdir.py [-h]

form a new empty dir

options:
  -h, --help  show this help message and exit

quirks:
  moves the 'git status --ignored --short' trash into a new dir ~%m%d$(qjd)%H%M~
  naturally doesn't move the empty dirs not listed by 'git status --ignored --short'
  goes well with Cp, MkDir, Mv, Ls, Rm, RmDir, Touch

examples:
  mkdir.py  # show examples
  mkdir.py --h  # show help and examples
  mkdir.py --  # moves untracked files into a new dir

  mkdir ~$(date +%m%d$(qjd)%H%M)~
  mv -i $(git status --ignored --short |cut -c 4-) ~$(date +%m%d$(qjd)%H%M)~/.
"""

# code reviewed by people, and by Black and Flake8


import datetime as dt
import os
import shlex
import shutil
import subprocess
import sys

import byotools as byo


def main():
    """Run as a Sh Verb"""

    parser = byo.compile_argdoc()
    byo.parser_parse_args(parser)  # prints helps and exits, else returns args

    # Say who's calling

    jqd = byo.subprocess_run_oneline("git config user.initials")
    jqd = jqd if jqd else "jqd"

    # Name a new Trash Can

    now = dt.datetime.now()
    dirname = now.strftime("%m%d{}%H%M%S".format(jqd))

    # Look for Dirs and Files to archive

    qsis_shline = "git status --ignored --short"

    qsis_argv = shlex.split(qsis_shline)

    qsis_run = subprocess.run(
        qsis_argv,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    assert not qsis_run.stderr, qsis_run.stderr

    stdout = qsis_run.stdout.decode()
    lines = stdout.splitlines()

    # Require no Dirs and Files in play at Git, except for the trash to archive

    glitches = list(_ for _ in lines if not _.startswith("?? "))
    if glitches:

        byo.sys_stderr_print(
            "mkdir.py: {} lines not tagged as '?? ' in:  {}".format(
                len(glitches), qsis_shline
            )
        )

        sys.exit(1)

    # Move the Dirs and Files

    assert not glitches

    fromnames = list(_[len("?? ") :].rstrip("/") for _ in lines)
    for fromname in fromnames:
        toname = "{}/{}".format(dirname, fromname)

        todirname = os.path.dirname(toname)
        if not os.path.exists(todirname):
            byo.sys_stderr_print("+ mkdir -p {}".format(todirname))
            os.makedirs(todirname)

        byo.sys_stderr_print("+ mv -i {} {}/.".format(fromname, todirname))
        shutil.move(fromname, dst=toname)  # like 'mv -i'

        # may raise:  shutil.Error: Destination path '...' already exists
        # may raise:  NotADirectoryError: [Errno 20] Not a directory: '...'


main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/mkdir.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
