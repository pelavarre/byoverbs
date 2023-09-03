#!/usr/bin/env python3

"""
usage: apt.py [--h] [list [--installed]]

show, install, and remove add-on packages for Linux

options:
  --help       show this help message and exit
  --installed  show just the installed packages (default: unknown)

examples:
  apy.py  # show these examples and exit
  apt.py --h  # show help and exit (more reliable than -h)
  apt.py --  # run the last paragraph of examples

  apt  # show help for Apt and exit

  apt list --installed 2>&1 |wc -l
  sudo apt install shellcheck
  apt list --installed 2>&1 |wc -l

  apt list --installed 2>&1 |wc -l
"""


import byohelper

... == byohelper


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/apt.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
