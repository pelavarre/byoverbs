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
  : Sep/2018 Mojave macOS X 10.14  # yearly major release date, miscoded as minor
  : Oct/2019 Catalina macOS X 10.15  # yearly major release date, miscoded as minor
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
    "sw_vers", stdin=subprocess.PIPE, stdout=subprocess.PIPE, check=True
)
stdout = run.stdout.decode()
lines = stdout.splitlines()

vxk = dict(_.replace(":", "").split("\t") for _ in lines)
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

    print(got)


# posted into:  https://github.com/pelavarre/byoverb/blob/main/bin/sw_vers.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
