#!/usr/bin/env python3

"""
usage: pwd.py [-h] [-P]

show an abs path to the current folder (aka, print working directory)

options:
  -h, --help   show this help message and exit
  -P           spell out the abs path more physically, without symbolic links

quirks:
  works well with ReadLink
  i've not yet tested looping symbolic links, deleted symbolic links

examples:

  pwd..py  # shows these examples and exit zero
  pwd..py --h  # shows these help lines and exit zero
  pwd..py --  # runs the last paragraph of examples

  pwd  # shows where you are
  pwd -P  # shows more precisely where you are
  bash -c 'dirs +0 |head -1'  # shows $HOME/ as ~/
  readlink -f "$PWD"  # maybe works better sometimes
"""


import byohelper

... == byohelper


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pwd..py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
