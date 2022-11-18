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
  goes well with Cp, Ls, Mv, Rm, RmDir, Touch
  classic Ls dumps all the Items, with no Scroll limit, when given no Parms

examples:

  ls.py  # show these examples and exit
  ls.py --h  # show help lines and exit (more reliable than -h)
  ls.py --  # count off the '%m%djqd' backup copies of Dirs and Files in the Stack

  ls -1rt |grep $(date +%m%djqd) |cat -n |expand
"""

import byotools as byo


jqd = byo.subprocess_run_oneline("git config user.initials")
jqd = jqd if jqd else "jqd"

ttyline = "ls -1rt |grep $(date +%m%d{jqd}) |cat -n |expand".format(jqd=jqd)
shline = "bash -c {!r}".format(ttyline)

byo.sys_exit_if(shline, ttyline=ttyline)
