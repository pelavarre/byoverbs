#!/usr/bin/env python3

r"""
usage: argparseyolo.py [-h]

options:
  -h, --help  show this help message and exit
  --yolo      run ahead with our freshest default choices, do damage as needed

examples:
  ./demos/argparseyolo.py  # show these examples
  ./demos/argparseyolo.py --help  # show these help lines
  ./demos/argparseyolo.py --yolo  # do whatever
"""

import __main__
import argparse
import sys
import textwrap

doc = __main__.__doc__
epilog = doc[doc.index("examples:") :].strip()

parser = argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)

help_yolo = "run ahead with our freshest default choices, do damage as needed"
parser.add_argument("--yolo", action="count", help=help_yolo)

shargs = sys.argv[1:]
shargs = shargs[1:] if (shargs[:1] == ["--"]) else shargs

args = parser.parse_args(shargs)
if not sys.argv[1:]:
    examples = textwrap.dedent("\n".join(epilog.splitlines()[1:]))
    print()
    print(examples)
    print()
    sys.exit(0)

print("hurrah, let's do whatever")


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/argparseyolo.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
