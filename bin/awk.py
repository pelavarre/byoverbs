#!/usr/bin/env python3

"""
usage: awk.py [--h] ...

copy input to buffer to output, while running Awk Code to edit the buffer

options:
  --help  show this help message and exit

quirks:
  macOs Sh defines PbPaste & PbCopy, life is harder elsewhere
  abbreviates Aho, Weinberger, and Kernighan, as A W K

example of line-broken Awk Code:
  {
    if (k != $1) {
      print ""
      print $1":"
      k = $1
    }
    gsub(/^[^:]*:/, "")
    print "   ", $0
  }

examples:

  awk.py  # show these examples and exit
  awk.py --h  # show help lines and exit (more reliable than -h)
  awk.py --  # prefix each line with "-- " and suffix each line with " --"

  A='{if (k != $1) {print ""; print $1":"; k = $1}; gsub(/^[^:]*:/, ""); print "   ", $0}'
  alias -- --a="awk -F: '$A'"
  unset A
"""

import __main__

import byotools as byo


A_AWK = """
  {
    if (k != $1) {
      print "";
      print $1":";
      k = $1
    }
    gsub(/^[^:]*:/, "");
    print "   ", $0
  }
""".strip()

assert A_AWK.replace(";", "") in __main__.__doc__

splits = A_AWK.splitlines()
split_strips = list(_.strip() for _ in splits)
split_strip_join = " ".join(split_strips)

shline = "awk -F: {!r}".format(split_strip_join)
byo.subprocess_shline_exit_if(shline, stdin=None)
