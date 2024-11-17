#!/usr/bin/env python3

"""
usage: vim.py [--help] [-u VIMRC]

todo

options:
  -h, --help  show this help message and exit
  -u VIMRC    edit after running a file (default '~/.vimrc')

quirks:
  classic Vim rudely runs ahead and creates a new Scratchpad, when given no Parms
  classic Vim rudely declines to quit when asked to ':n' past the last File

examples:

  vim.py  # show these examples and exit
  vim.py --h  # show help lines and exit (more available than -h)
  vim.py --  # do what's popular now

  vim ~/.vimrc  # visit and run
  vim -u /dev/null ~/.vimrc  # visit, don't run

  vim +$ Makefile  # open up at end of file, not start of file
  vim +':set background=light' Makefile  # choose Light Mode, when they didn't
  vim +':set background=dark' Makefile  # choose Dark Mode, when they didn't
"""

# todo: vim options akin to less -FIRX


import byotools as byo


byo.sys_exit()


# :helpgrep
# :helpgrep CTRL-U
# :cnext

# demo +123
# demo +startinsert
# vim.py to take:  pathname:123
# vim.py to take:  pathname:123:4

# solve
#
#    % bash -c vim </dev/null
#    Vim: Warning: Input is not from a terminal
#    :q%
#    %
#


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/vim.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
