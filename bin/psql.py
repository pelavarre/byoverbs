#!/usr/bin/env python3

r"""
usage: psql.py [--h]  ...

take commands spoke in the PostgreSQL languages

options:
  --help  show this help message and exit
  --yolo  do what's popular now

examples:

  psql.py  # show these examples and exit
  psql.py --h  # show this help message and exit
  psql.py --yolo  # do what's popular now

  sudo -u postgres psql  # launch Psql with default 'peer' Auth
  psql --username=postgres  # launch Psql with 'trust' Auth
    \! date  -- to say when you did what
    \timing on  -- to report elapsed time per query
    \x on  -- to transpose Tables to show each Row as multiple Lines

  cd /etc/postgresql/*/main/  # /etc/postgresql/14/main
  sudo cat pg_hba.conf |grep peer   # local all postgres peer  # <= sudo su - postgres
  sudo cat pg_hba.conf |grep trust  # local all postgres trust  # : no sudo needed :

  F=pg_hba.conf && echo cp -ip $F{,~$(date -r $F +%m%djqd%H%M)~} |tee /dev/tty |bash

  : Oct/2019 PostgreSQL 12 # major release date  # Ubuntu 2020?
  : Sep/2020 PostgreSQL 13 # major release date
  : Sep/2021 PostgreSQL 14 # major release date  # Ubuntu 2022?
  : Oct/2022 PostgreSQL 15 # major release date
  : Sep/2023 PostgreSQL 16 # major release date

"""

# https://packages.ubuntu.com/ > Long Term Stable (LTS)
# todo: which have which PostgreSQL


import sys


import byotools as byo


if sys.argv[1:]:
    sys.stderr.write("psql.py: did you mean:  psql ...\n")
    sys.exit(2)


byo.subprocess_exit_run_if()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/psql.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
