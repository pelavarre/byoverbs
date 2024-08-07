#!/usr/bin/env python3

"""
usage: vi.py [--help] [-u VIMRC]

todo

options:
  -h, --help  show this help message and exit
  -u VIMRC    edit after running a file (default '~/.vimrc')

quirks:
  classic Vi rudely runs ahead and creates a new Scratchpad, when given no Parms
  classic Vi rudely declines to quit when asked to ':n' past the last File

examples:

  vi.py  # show these examples and exit
  vi.py --h  # show help lines and exit (more available than -h)
  vi.py --  # do what's popular now

  vim ~/.vimrc  # visit and run
  vim -u /dev/null ~/.vimrc  # visit, don't run

  vi +$ Makefile  # open up at end of file, not start of file
  vi +':set background=light' Makefile  # choose Light Mode, when they didn't
  vi +':set background=dark' Makefile  # choose Dark Mode, when they didn't
"""

# todo: vim options akin to less -FIRX


import byotools as byo


byo.sys_exit()


# demo +123
# demo +startinsert
# vim.py to take:  triage/scraps/jv_sad_builds.py:775

# solve
#
#    % bash -c vi </dev/null
#    Vim: Warning: Input is not from a terminal
#    :q%
#    %
#


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/vim.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
