#!/usr/bin/env python3

r"""
usage: echo.py [--h] [ARG ...]

number and print a list of strings of chars

positional arguments:
  ARG     a string of chars

options:
  --help  show this help message and exit
  -n      print without closing the line, a la Bash PrintF
  -E      don't escape the \ backslant
  -e      do escape the \ backslant with any of \ abfnrtv 0 x, and also with \e and \c

quirks:
  classic Echo never numbers its args
  goes well with Clear, Cp, Echo, Mv, PrintF, Reset, TPut

examples:
  echo.py -- a 'b c'  # numbers and prints its own args

  echo "+ exit $?"  # reads-and-clears last process returncode exit status
  echo -n '⌃ ⌥ ⇧ ⌘ ← → ↓ ↑ ⎋' |hexdump -C
  echo $'\x1B[34mBlue \x1B[31mRed \x1B[33mYellow \x1B[32mGreen \x1B[36mTeal \x1B[30m'

  python3 -c 'print("'"$(echo '\N{Large '{Red,Green,Blue}' Circle} ')"'")'
  # {Blue,Brown,Green,Orange,Purple,Red,Yellow}

  touch t.txt
  F=t.txt && echo mv -i $F{,~$(date -r $F +%m%d$(qjd)%H%M)~} |tee /dev/tty |bash
  F=t.txt && echo cp -ip $F{,~$(date -r $F +%m%d$(qjd)%H%M)~} |tee /dev/tty |bash

  printf '\e[8;%s;89t' "$(stty size |cut -d' ' -f2)"  # echoes inside 89 Columns
  printf '\e[8;50;%st' "$(stty size |cut -d' ' -f2)"  # echoes inside 50 Lines
  printf '\e[H\e[2J\e[3J'  # clears Scrollback and Screen of Echoes
"""

import sys

import byotools as byo


if sys.argv[1:][:1] != ["--"]:

    byo.sys_exit()

for (index, arg) in enumerate(sys.argv):
    print("{}:  {!r}".format(index, arg))
print(len(sys.argv))
