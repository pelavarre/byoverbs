#!/usr/bin/env python3

"""
usage: sw_vers.py [--h] ...

show macOS Version, and mark it with its Month/Year

options:
  --help  show this help message and exit

quirks:
  classic Sw_Vers dumps Key-Value Pairs, when given no Parms
  goes well with:  Linux Lsb_Release A, Mac Sw_Vers, UName

examples:

  sw_vers.py  # show these examples and exit
  sw_vers.py --h  # show help lines and exit
  sw_vers.py --  # add standard calendar Month/Year to their report of Version

  sw_vers
  echo $(sw_vers |awk '{print $NF}')  # such as:  macOS 12.2.1 21D62
  sw_vers |grep ^ProductVersion: |awk '{print $2}'  # such as:  12.2

  :
  : Classic Mac OS, Mac OS X, OS X, macOS
  :
  : Sep/2016 Sierra macOS 10.12  # major release date
  : Sep/2017 High Sierra macOS 10.13  # major release date
  : Sep/2018 Mojave macOS 10.14  # major release date
  : Oct/2019 Catalina macOS 10.15  # major release date
  :
  : Nov/2020 Big Sur macOS 11  # major release date
  : Oct/2021 Monterey macOS 12  # major release date
  : Oct/2022 Ventura macOS 13  # major release date
  :
"""

import __main__
import subprocess
import sys

import byotools as byo


byo.sys_exit_if()  # prints examples or help and exits, else returns args

run = subprocess.run(
    "sw_vers", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)

assert not run.returncode, run.returncode
assert run.stdout, run.stderr
assert not run.stderr, run.stderr

stdout = run.stdout.decode()
wide_lines = stdout.splitlines()

old_tt = "\t\t"
new_t = "\t"
lines = list(_.replace(old_tt, new_t) for _ in wide_lines)  # needed since 2022 Ventura

pairs = list(_.replace(":", "").split("\t") for _ in lines)
lens = list(len(_) for _ in pairs)
assert set(lens) == set([2]), (lens, pairs, lines)

vxk = dict(pairs)
product_version = vxk["ProductVersion"]
major = product_version.split(".")[0]

doc = __main__.__doc__
chars = "macOS {} ".format(major)
hits = list(_ for _ in doc.splitlines() if chars in _)

if len(hits) != 1:
    sys.stdout.write(stdout)

else:
    hit = hits[-1]

    got = hit
    got = got.split(":")[-1]
    got = got.split("#")[0]
    got = got.strip()

    got_form = "{}, patched up to {}, more detail at:  sw_vers"
    alt_got = got_form.format(got, product_version)

    print(alt_got)


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/sw_vers.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
