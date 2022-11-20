#!/usr/bin/env python3

"""
usage: echo.py [--h] [ARG ...]

number and print a list of strings of chars

positional arguments:
  ARG     a string of chars

options:
  --help  show this help message and exit

quirks:
  goes well with Echo, HexDump
  classic Echo never numbers its args

examples:

  echo.py  # show these examples and exit
  echo.py --h  # show help lines and exit (more reliable than -h)
  echo.py -- a 'b c'  # number and print these args

  ls -1rt |grep $(date +%m%djqd) |cat -n |expand
"""

import sys

import byotools as byo


if sys.argv[1:][:1] != ["--"]:

    byo.sys_exit()

for (index, arg) in enumerate(sys.argv):
    print("{}:  {!r}".format(index, arg))
print(len(sys.argv))
