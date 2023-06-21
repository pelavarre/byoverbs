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
  : Dec/2016 CPython 3.6  # minor release date  # Dict Keys ordered by Insertion
  : Jun/2018 Python 3.7  # minor release date  # Dict Keys ordered by Insertion
  : : Mar/2019 Python 3.7.3  # micro release date
  : : Dec/2019 Python 3.7.6  # micro release date
  : Oct/2019 Python 3.8  # minor release date  # <- Ubuntu 2020
  : : Feb/2020 Python 3.8.2  # micro release date
  : : May/2021 Python 3.8.10  # micro release date
  : Oct/2020 Python 3.9  # minor release date  # <- G Cloud Shell 2023
  : : Dec/2020 Python 3.9.1  # micro release date
  : : Feb/2021 Python 3.9.2  # micro release date
  : : Apr/2021 Python 3.9.4  # micro release date
  : : May/2021 Python 3.9.5  # micro release date
  : : Jun/2021 Python 3.9.6  # micro release date
  : Oct/2021 Python 3.10  # minor release date  # <- Ubuntu 2022
  : : Mar/2022 Python 3.10.4  # micro release date
  : : Jun/2022 Python 3.10.5  # micro release date
  : : Aug/2022 Python 3.10.6  # micro release date
  : Oct/2022 Python 3.11  # minor release date
  : : Apr/2023  Python 3.11.3  # micro release date
"""

# https://packages.ubuntu.com/ > Long Term Stable (LTS)
# https://packages.ubuntu.com/bionic/python/ Ubuntu Apr/2018  => Jul/2019 Python 3.6.9
# https://packages.ubuntu.com/focal/python/ Ubuntu Apr/2020  => May/2021 Python 3.8.10
# https://packages.ubuntu.com/jammy/python/ Ubuntu Apr/2022  => Mar/2022 Python 3.10.4


import byotools as byo


byo.subprocess_exit_run_if()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/python3.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
