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
  ls.py --  # count off the '%m%djqd' backup copies of Dirs and Files in the Stack

  ls -1rt |grep $(date +%m%djqd) |cat -n |expand
"""

import byotools as byo


def main():
    """Run as a Sh Verb"""

    # Require one Arg, preceded by a "--" Sep or not

    parm = byo.shlex_parms_one_posarg()

    # Say who's calling

    jqd = byo.subprocess_run_oneline("git config user.initials")
    jqd = jqd if jqd else "jqd"

    # Choose a Sh Line, else quit

    if not parm:
        byo.sys_exit_if()  # prints examples or help lines and exits, else returns

    ttyline = "ls -1rt |grep $(date +%m%d{jqd}) |cat -n |expand".format(jqd=jqd)
    shline = "bash -c {!r}".format(ttyline)

    # Run the chosen Sh Line, and return

    byo.sys_stderr_print("+ {}".format(ttyline))
    byo.subprocess_run(shline)


main()
