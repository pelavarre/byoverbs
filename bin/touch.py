#!/usr/bin/env python3

"""
touch -d 1970-01-01T00:00:00.000Z t.touch  # make UTC stamp
touch -d 1999-12-31T23:59:59.999 t.touch  # make local stamp
touch -r t1.touch t2.touch  # copy last-modified stamp
"""

import byotools as byo


byo.sys_exit()
