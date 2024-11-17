#!/usr/bin/env python3

"""
usage: time.py [-h] [WORD ...]

run a line of sh input but then tell stderr how long it took

positional arguments:
  WORD         a word of a Sh Input Line

options:
  -h, --help   show this help message and exit

quirks:
  tells just wall clock, more concisely than Bash or Zsh
  misreads Sh aliases and functions literally
  isn't yet implemented as Py for 1 or more Sh Words

examples:

  time..py  # shows these examples and exit zero
  time..py --h  # shows these help lines and exit zero
  time..py --  # runs the last paragraph of examples

  time sleep 0.1
"""


import byohelper

... == byohelper  # type: ignore


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/time..py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
