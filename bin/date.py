#!/usr/bin/env python3

"""
usage: date.py [--h] [-r FILE] [-u] ...

format date/time stamps

options:
  --help   show this help message and exit
  -r FILE  work with last-modified stamp of file, in place of now
  -u       speak of the UTC GMT Zulu time zone

quirks:
  local to you is remote to me

examples:

  date.py  # show these examples and exit
  date.py --h  # show help lines and exit (more reliable than -h)
  date.py --  # run the examples below

  date -u

  TZ=Asia/Calcutta date
  TZ=Europe/Kyiv date
  TZ=America/Los_Angeles date
"""


import byotools as byo


byo.subprocess_exit_run_if()
