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

  echo a b c d e f |tr ' ' '\n' |awk '(NR<=2){print NR":",$0} {o2=o1} {o1=$0} END{print (NR-1)":", o2; print NR":", o1}'
  echo a b c d e f |tr ' ' '\n' |cat -n |expand |tee >(head -2) >(tail -2) >/dev/null  # more cogent, less reliable

  F=log; (cat $F; tail -F $F) |awk '!d[$0]++' |grep -i Error  # don't repeat Lines seen already

  F=bin/awk.py && cat $F |awk '(length($0)>88){print "'$F':"NR":"$0}'

  seq 20 |awk '/^8$/,/^14$/{print}'  # print 8..14
  seq 20 |awk '/^8$/{F=1} /^14$/{F=0} F{print}'  # print 8..13
  seq 20 |awk '!(NR%2){print o, $0} {o=$0}'  # print 1 2, 3 4, ... paired
  seq 20 |awk '!f{f=1;print} {o=$0} END{if (NR > 1) {print "..."; print o}}'  # first, sep, last

  find * |awk -F/ -vOFS=/ '{$NF=""; print}' |sort |uniq  # dirs not empty/hidden

  A='{if (k!=$1) {print ""; print $1":"; k = $1}; gsub(/^[^:]*:/, ""); print "   ", $0}'
  alias -- --a="awk -F: '$A'"
  unset A
  grep 'seq.*[|]' bin/*.py |--a

  echo 'aa  bb  cc' |awk '{$1=$1};1'  # collapse each IFS into one OFS

  awk '{d[$_]++}END{for(k in d){print d[k],k}}' |sort -n  # faster than |uniq -c |expand
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

assert __main__.__doc__
assert A_AWK.replace(";", "") in __main__.__doc__

splits = A_AWK.splitlines()
split_strips = list(_.strip() for _ in splits)
split_strip_join = " ".join(split_strips)

shline = "awk -F: {!r}".format(split_strip_join)
byo.subprocess_shline_exit_if(shline, stdin=None)  # todo: do we mean stdin=subprocess.PIPE ?


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/awk.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
