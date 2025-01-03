#!/usr/bin/env python3

"""
usage: python3.py [--h]  ...

take commands spoke in the Python 3 language

options:
  --help         show this help message and exit
  -V, --version  print Python version (-VV for more force)

quirks:
  goes well with Python3 Bash
  classic 'python3' does 'del __file__', unless you breakpoint before the end

examples:

  python3.py  # show these examples and exit
  python3.py --h  # show this help message and exit
  python3.py --  # run the examples below

  python -i -c ''  # run without first showing a banner welcome message

  python3 -c 'import this' |tail +3 |cat -n |expand
    # 'included is better than homemade'
    # 'copied is better than aliased'
    # 'ordered is better than muddled'
    # 'python3' is better than 'python3 -O'

  : Dec/2008 Python 3  # major release date
  : Jun/2009 Python 3.1  # minor release date
  : Feb/2011 Python 3.2  # minor release date
  : Sep/2012 Python 3.3  # minor release date
  : Mar/2014 Python 3.4  # minor release date
  : : Feb/2015 Python 3.4.3  # micro release date
  : Sep/2015 Python 3.5  # minor release date
  : : Jun/2016 Python 3.5.2  # micro release date
  : Dec/2016 Python 3.6  # minor release date  # <- Ubuntu 2018
  : : Mar/2018 Python 3.6.5  # micro release date
  : : Dec/2018 Python 3.6.8  # micro release date
  : : Jul/2019 Python 3.6.9  # micro release date
  : : Dec/2019 Python 3.6.10  # micro release date
  : : Sep/2021 Python 3.6.15  # micro release date
  : Dec/2016 CPython 3.6  # minor release date  # Dict Keys ordered by Insertion

  : 2011 + Minor-Version = year of Python Minor-Version since 3.7

  : Jun/2018 Python 3.7  # minor release date  # Dict Keys ordered by Insertion
  : : Mar/2019 Python 3.7.3  # micro release date
  : : Dec/2019 Python 3.7.6  # micro release date
  : Oct/2019 Python 3.8  # minor release date  # <- Ubuntu 2020
  : : Feb/2020 Python 3.8.2  # micro release date
  : : May/2021 Python 3.8.10  # micro release date
  : Oct/2020 Python 3.9  # minor release date  # <- G Cloud Shell 2023
  : : Dec/2020 Python 3.9.1  # micro release date
  : : Feb/2021 Python 3.9.2  # micro release date  # <- G Cloud Shell later 2023
  : : Apr/2021 Python 3.9.4  # micro release date
  : : May/2021 Python 3.9.5  # micro release date
  : : Jun/2021 Python 3.9.6  # micro release date  # <- macOS 2021..2023 Monterey Plus
  : Oct/2021 Python 3.10  # minor release date  # <- Ubuntu 2022
  : : Mar/2022 Python 3.10.4  # micro release date
  : : Jun/2022 Python 3.10.5  # micro release date
  : : Aug/2022 Python 3.10.6  # micro release date
  : : Oct/2022 Python 3.10.8  # micro release date  # <- ReplIt-Com Python 2023
  : : Jun/2023 Python 3.10.12  # micro release date
  : Oct/2022 Python 3.11  # minor release date
  : : Apr/2023 Python 3.11.3  # micro release date
  : : Oct/2023 Python 3.11.6  # micro release date
  : Oct/2023 Python 3.12  # minor release date  # <- Ubuntu 2024
  : : Apr/2024 Python 3.12.3  # micro release date
  : : Jun/2024 Python 3.12.4  # micro release date
  : : Aug/2024 Python 3.12.5  # micro release date
  : : Sep/2024 Python 3.12.6  # micro release date
  : Oct/2024 Python 3.13  # minor release date
  : : Dec/2024 Python 3.13.1  # micro release date

"""

# https://packages.ubuntu.com/ > Long Term Stable (LTS)
# https://packages.ubuntu.com/bionic/python/ Ubuntu Apr/2018  => Jul/2019 Python 3.6.9
# https://packages.ubuntu.com/focal/python/ Ubuntu Apr/2020  => May/2021 Python 3.8.10
# https://packages.ubuntu.com/jammy/python/ Ubuntu Apr/2022  => Mar/2022 Python 3.10.4

# Ubuntu 2024 as logged by
#   https://utcc.utoronto.ca/~cks/space/blog/python/Ubuntu2404PythonState
# not yet seen by me (Pat LaVarre)


import sys


import byotools as byo


if sys.argv[1:]:
    sys.stderr.write("python3.py: did you mean:  python3 ...\n")
    sys.exit(2)


byo.subprocess_exit_run_if()


# todo: some good way to remember to say encoding="utf-8" more often than "utf8"


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/python3.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
