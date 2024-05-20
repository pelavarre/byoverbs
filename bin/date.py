#!/usr/bin/env python3

"""
usage: date.py [-h] [-u] [-r FILE] [+FORMAT]

format date/time stamps

options:
  -h, --help   show this help message and exit
  -u           speak of the UTC GMT Zulu time zone
  -r FILE      work with last-modified stamp of file, in place of now
  +FORMAT      replace default of:  date +'%a %b %d %H:%M:%S %Z %Y'

quirks:
  local to you is remote to me

examples:

  date.py  # shows these examples and exit
  date.py --h  # shows help lines and exit (more reliable than -h)
  date.py --  # runs the last paragraph of examples

  date -u
  touch t.touch && date -r t.touch +'%a %b %d %H:%M:%S %Z %Y'
  echo mv -i t.touch{,~$(date -r t.touch +%m%dpl%H%M)~}

  TZ=Asia/Kolkata date
  TZ=Europe/Kyiv date
  TZ=America/Los_Angeles date
"""


import byohelper

... == byohelper  # type: ignore


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/date.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
