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
  printf '\e[34mB \e[31mR \e[35mM \e[33mY \e[32mG \e[36mT \e[37mW \e[m\n'  # Plain
  printf '\e[94mB \e[91mR \e[95mM \e[93mY \e[92mG \e[96mT \e[97mW \e[m\n'  # Bright

  python3 -c 'print("'"$(echo '\N{Large '{Red,Green,Blue}' Circle} ')"'")'
  # {Blue,Brown,Green,Orange,Purple,Red,Yellow}

  touch t.txt
  F=t.txt && echo mv -i $F{,~$(date -r $F +%m%d$(qjd)%H%M)~} |tee /dev/tty |bash
  F=t.txt && echo cp -ip $F{,~$(date -r $F +%m%d$(qjd)%H%M)~} |tee /dev/tty |bash

  printf '\e[8;;89t'  # resize Sh Terminal to 89 Cols  # same Rows
  printf '\e[8;;101t'  # resize Sh Terminal to 89 Cols  # same Rows
  printf '\e[8;25;%dt' $(stty size |cut -d' ' -f2)  # resize to 25 Rows  # same Cols
  printf '\e[8;42;%dt' $(stty size |cut -d' ' -f2)  # resize to 42 Rows  # same Cols
  printf '\e[8;42;89t'  # resize Sh Terminal to 89 Cols x 42 Rows
  printf '\e[8;;t'  # resize Sh Terminal to max Rows and Columns
  stty size  # say what Rows and Columns you got

  printf '\e[H\e[2J\e[3J'  # clears Scrollback and Screen of Echoes
"""

import sys

import byotools as byo


if sys.argv[1:][:1] != ["--"]:
    byo.sys_exit()

for index, arg in enumerate(sys.argv):
    print("{}:  {!r}".format(index, arg))
print(len(sys.argv))


# todo:  echo --end='\n' {1,2}.{3,4,5}


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/echo.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
