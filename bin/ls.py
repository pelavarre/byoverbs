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
  -m      show as comma separated names

quirks:
  goes well with Cp, MkDir, Ls, Mv, Rm, RmDir, Touch
  classic Ls dumps all the Items, with no Scroll limit, when given no Parms

examples:

  ls.py  # show these examples and exit
  ls.py --h  # show help lines and exit (more reliable than -h)
  ls.py --  # count off the '%m%djqd' backup copies of Dirs and Files in the Stack

  ls -1rt |grep $(date +%m%djqd) |cat -n |expand
"""

import os
import re
import shlex
import subprocess
import sys

import byotools as byo


jqd = byo.subprocess_run_oneline("git config user.initials")
jqd = jqd if jqd else "jqd"

assert re.match(r"^[a-z]+$", string=jqd)  # todo: accept JQD initials outside Ascii

ttyline_0 = "ls -1rt |grep $(date +%m%d{jqd}) |cat -n |expand".format(jqd=jqd)
shline_0 = "bash -c {!r}".format(ttyline_0)

ttyline_1 = "ls -1rt |grep {jqd} |cat -n |expand".format(jqd=jqd)
shline_1 = "bash -c {!r}".format(ttyline_1)

byo.sys_exit_if_testdoc()  # prints examples & exits if no args

byo.sys_exit_if_argdoc()  # prints help lines & exits if "--h" arg, but ignores "-h"

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

if not run_0.stdout:

    byo.sys_stderr_print("+ {}".format(ttyline_1))
    argv_1 = shlex.split(shline_1)
    run_1 = subprocess.run(argv_1, stdin=subprocess.PIPE, check=True)
