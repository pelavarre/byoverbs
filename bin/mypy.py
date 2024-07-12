#!/usr/bin/env python3

"""
usage: mypy.py [--h]  ...

say if we believe some Py Type Declarations match the Code

options:
  --help  show this help message and exit
  --yolo  do what's popular now

examples:

  mypy.py  # show these examples and exit
  mypy.py --h  # show this help message and exit
  mypy.py --yolo  # do what's popular now

  : Feb/2023 MyPy 1.0
  : Mar/2023 MyPy 1.1
  : Apr/2023 MyPy 1.2
  : May/2023 MyPy 1.3
  : Jun/2023 MyPy 1.4

  : Aug/2023 MyPy 1.5

  : Oct/2023 MyPy 1.6
  : Nov/2023 MyPy 1.7
  : Dec/2023 MyPy 1.8

  : Mar/2024 MyPy 1.9
  : Apr/2024 MyPy 1.10

  <= https://pypi.org/project/mypy/#history

"""

# https://packages.ubuntu.com/ > Long Term Stable (LTS)
# todo: which have which PostgreSQL


import sys


import byotools as byo


if sys.argv[1:]:
    sys.stderr.write("mypy.py: did you mean:  mypy ...\n")
    sys.exit(2)


byo.subprocess_exit_run_if()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/mypy.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
