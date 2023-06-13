#!/usr/bin/env python3

# sed -iEXT FILE

"""
usage: sed.py [--h] ...

copy input to buffer to output, while running Sed Code to edit the buffer

options:
  --help  show this help message and exit

quirks:
  macOs Sh defines PbPaste & PbCopy, life is harder elsewhere
  abbreviates Stream Editor as S E D

examples:

  sed.py  # show these examples and exit
  sed.py --h  # show help lines and exit (more reliable than -h)
  sed.py --  # prefix each line with "-- " and suffix each line with " --"

  pbpaste |awk '{print $NF}' |sed 's,^,-- ,' |sed 's,$, --,' |pbcopy
"""

import byotools as byo


byo.subprocess_exit_run_if()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/sed.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
