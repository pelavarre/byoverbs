#!/usr/bin/env python3

"""
usage: date.py [--h] ...

format date/time stamps

options:
  --help  show this help message and exit

quirks:
  local to you is remote to me

examples:

  date.py  # show these examples and exit
  date.py --h  # show help lines and exit (more reliable than -h)
  date.py --  # run the examples below

  TZ=Asia/Calcutta date
  TZ=Europe/Kyiv date
  TZ=America/Los_Angeles date
"""


import byotools as byo


byo.subprocess_exit_run_if()