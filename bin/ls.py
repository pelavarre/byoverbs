#!/usr/bin/env python3

"""
usage: ls.py [--h] [TOP ...]

show the files and dirs inside a dir

positional arguments:
  TOP     the name of a dir or file to show

options:
  --help  show this help message and exit
  -1      show as one column of one file or dir per line
  -C      show as multiple columns
  -l      show as many columns of one file or dir per line
  -lh     like -l but round off byte counts to k M G T P E Z Y R Q etc
  -m      show as comma separated names

quirks:
  goes well with Cp, MkDir, Ls, Mv, Rm, RmDir, Touch
  classic Ls dumps all the Items, with no Scroll limit, when given no Parms

examples:
  ls.py --  # count off the '%m%d$(qjd)' revisions, else the '$(qjd)' revisions
  find ./* -prune  # like 'ls', but with different corruption of File and Dir Names
  ls -1rt |grep $(date +%m%d$(qjd)) |cat -n |expand
"""

# code reviewed by people, and by Black and Flake8


import os
import shlex
import subprocess
import sys

import byotools as byo


def main():
    """Run from the Sh Command Line"""

    # Plan to count off the '%m%d$(qjd)' backup copies of Dirs and Files in the Stack

    jqd = byo.subprocess_run_oneline("git config user.initials")
    shjqd = byo.shlex_quote_if(jqd)

    ttyline_0 = "ls -1rt |grep $(date +%m%d{jqd}) |cat -n |expand".format(jqd=shjqd)
    shline_0 = "bash -c {!r}".format(ttyline_0)

    ttyline_1 = "ls -1rt |grep {jqd} |cat -n |expand".format(jqd=shjqd)
    shline_1 = "bash -c {!r}".format(ttyline_1)

    # Maybe choose to do other things

    byo.sys_exit_if_testdoc()  # prints examples & exits if no args

    byo.sys_exit_if_argdoc()  # prints help lines & exits if "--h" arg, but ignores "-h"

    # Search up the '%m%d$(qjd)' revisions

    byo.sys_stderr_print("+ {}".format(ttyline_0))
    argv_0 = shlex.split(shline_0)
    run_0 = subprocess.run(
        argv_0,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    os.write(sys.stdout.fileno(), run_0.stdout)
    os.write(sys.stderr.fileno(), run_0.stderr)

    # Else fail over to also search up the '$(qjd)' revisions

    if not run_0.stdout:

        byo.sys_stderr_print("+ {}".format(ttyline_1))
        argv_1 = shlex.split(shline_1)
        _ = subprocess.run(argv_1, stdin=subprocess.PIPE, check=True)


main()
