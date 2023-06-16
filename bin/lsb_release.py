#!/usr/bin/env python3

r"""
usage: lsb-release.py [--h] [-a] ...

show Linux Standard Base Version, and mark it with its Month/Year

options:
  --help  show this help message and exit
  -a      say more than 'No LSB modules are available'

quirks:
  presumes you know LSB = Linux Standard Base, and LTS = Long-Term Stable
  classic Lsb_Release dumps Key-Value Pairs, when given no Parms
  goes well with:  Linux Lsb_Release A, Mac Sw_Vers, UName

examples:

  lsb_release.py  # show these examples and exit
  lsb_release.py --h  # show help lines and exit
  lsb_release.py --  # add standard calendar Month/Year to their report of Version

  lsb_release -a
  echo $(lsb_release -a 2>/dev/null |awk '{print $NF}')  # Ubuntu LTS 22.04 jammy
  lsb_release -a 2>&1 |grep ^Desc |cut -d$'\t' -f2  # Ubuntu 22.04.1 LTS

  :
  : Apr/2016 Xenial Ubuntu Linux 16.04 LTS  # major release date
  : Apr/2018 Bionic Ubuntu Linux 18.04 LTS  # major release date
  : Apr/2020 Focal Ubuntu Linux 20.04 LTS  # major release date
  : Apr/2022 Jammy Ubuntu Linux 22.04 LTS  # major release date
  :
"""

import __main__
import subprocess
import sys

import byotools as byo


byo.sys_exit_if()  # prints examples or help and exits, else returns args

run = subprocess.run(
    "lsb_release -a".split(),
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=True,
)
stdout = run.stdout.decode()
lines = stdout.splitlines()

vxk = dict(_.replace(":", "").split("\t") for _ in lines)
description = vxk["Description"]
major = description.split("Ubuntu ")[1].split()[0]

doc = __main__.__doc__
chars = "Ubuntu Linux {} ".format(major)
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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/lsb_release.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
