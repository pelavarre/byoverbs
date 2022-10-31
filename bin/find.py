#!/usr/bin/env python3

"""
usage: find.py [TOP]

list the Dirs and Files of some Dirs of Dirs of Files

positional arguments:
  TOP        where to start (default: $PWD)

options:
  --help     show this help message and exit

quirks:
  Mac Find doesn't guess the TOP for you

examples:

  find.py  # show these examples and exit
  find.py --h  # show this help message and exit
  find.py --  # find .

  find.py .  # find .
  find.py $PWD  # raise NotImplementedError
"""

import sys

import byotools as byo


if sys.argv[1:] != ["."]:

    byo.sys_exit_if()

shline = "find ."
byo.sys_stderr_print("+ {}".format(shline))
byo.subprocess_run("find .")
