#!/usr/bin/env python3

"""
usage: vi.py [-h] [-u VIMRC]

view & change bytes of memory or file, in reply to keyboard chords

options:
  -h, --help  show this help message and exit
  -u VIMRC    edit after running a File (default '~/.vimrc')

examples:

  vi +$ Makefile  # open up at end of file, not start of file

  vi +':set background=light' Makefile  # choose Light Mode, when they didn't
  vi +':set background=dark' Makefile  # choose Dark Mode, when they didn't

  vim -u /dev/null ~/.vimrc  # edit custom configuration with default configuration

  ls -1 |vi -  # edit from Pipe to File
  ls -1 |vi - +':set t_ti= t_te='  # edit without clearing & switching Screens
  pbpaste |vi -  # edit the Mac Os Copy/Paste Buffer
"""

# see also: demos/vi2.py


import byotools as byo


byo.sys_exit()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/vi.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
