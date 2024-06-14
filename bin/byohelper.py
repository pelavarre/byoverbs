"""
usage: byohelper.py [-h]

compile & run the __main__.__doc__, as an ArgParse Arg Doc

options:
  --help   show this help message and exit

examples:
  byohelper.py  # show these examples and exit
  byohelper.py --h  # show help lines and exit (more reliable than -h)
  byohelper.py --  # run the last paragraph of examples

  echo '1st Hello ByoHelper World!'
  echo '2nd Hello ByoHelper World!'
"""

import byotools as byo


byo.subprocess_exit_run_if()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/byohelper.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
