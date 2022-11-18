#!/usr/bin/env python3

"""
usage: sed.py [--h] ...

copy input to output but edit it along the way

options:
  --help  show this help message and exit

quirks:
  macOs Sh defines PbPaste & PbCopy, life is harder elsewhere

examples:

  sed.py  # show these examples and exit
  sed.py --h  # show help lines and exit (more reliable than -h)
  sed.py --  # prefix each line with "-- " and suffix each line with " --"

  pbpaste |awk '{print $NF}' |sed 's,^,-- ,' |sed 's,$, --,' |pbcopy
"""

import byotools as byo


ttyline = "pbpaste |awk '{print $NF}' |sed 's,^,-- ,' |sed 's,$, --,' |pbcopy"
shline = "bash -c {!r}".format(ttyline)

byo.sys_exit_if(shline, ttyline=ttyline)
