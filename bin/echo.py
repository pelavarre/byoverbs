#!/usr/bin/env python3

r"""
usage: echo.py [--h] [ARG ...]

number and print a list of strings of chars

positional arguments:
  ARG     a string of chars

options:
  --help  show this help message and exit
  -n      print without closing the line
  -E      don't escape the \ backslant
  -e      do escape the \ backslant with any of \ abfnrtv 0 x, and also with \e and \c

quirks:
  goes well with Clear, Echo, PrintF, Reset, TPut
  classic Echo never numbers its args

examples:

  echo.py  # show these examples and exit
  echo.py --h  # show help lines and exit (more reliable than -h)
  echo.py -- a 'b c'  # number and print these args

  echo "+ exit $?"  # read-and-clear last process returncode exit status
  echo -n '⌃ ⌥ ⇧ ⌘ ← → ↓ ↑ ⎋' |hexdump -C
  echo $'\x1B[34mBlue \x1B[31mRed \x1B[33mYellow \x1B[32mGreen \x1B[36mTeal \x1B[30m'

  printf '\e[8;%s;89t' "$(stty size |cut -d' ' -f2)"  # 89 Columns
  printf '\e[8;50;%st' "$(stty size |cut -d' ' -f2)"  # 50 Lines
  printf '\e[H\e[2J\e[3J'  # Clear Scrollback and Screen
"""

import sys

import byotools as byo


if sys.argv[1:][:1] != ["--"]:

    byo.sys_exit()

for (index, arg) in enumerate(sys.argv):
    print("{}:  {!r}".format(index, arg))
print(len(sys.argv))
