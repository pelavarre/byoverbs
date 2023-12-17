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

  seq 20 |awk '!f{f=1;print} {o=$0} END{print o}' |uniq  # copies first & last lines
  seq 20 |awk '!f{f=1;print} {o=$0} END{if (NR > 1) {print "..."; print o}}'
  seq 20 |awk '/^8$/{F=1} /^14$/{F=0} F{print}'  # starts/ stops copying lines
  find * |awk -F/ -vOFS=/ '{$NF=""; print}' |sort |uniq |grep   # dirs not empty/hidden

  A='{if (k!=$1) {print ""; print $1":"; k = $1}; gsub(/^[^:]*:/, ""); print "   ", $0}'
  alias -- --a="awk -F: '$A'"
  unset A
  grep 'seq.*[|]' bin/*.py |--a
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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/awk.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
