#!/usr/bin/env python3

r"""
usage: byoverbs.py [-h]

run as if the shell had thought ahead to say:  export PYTHONPATH=$PWD/../byoverbs/..

options:
  -h, --help  show this help message and exit

example:
  unset PYTHONPATH

  cd byoverbs/
  realpath $PWD/../byoverbs
  ls -1d $PWD/../byoverbs  # shows if SymLink into Dir without ByoVerbs
  ls __init__.py  # shows if Python will import Dir

  python3 demos/byoverbs.py  # prints help lines, exit zero

  python3 -i demos/byoverbs.py --
    sys.modules["byoverbs"]  # shows it works, when it works

  python3 -i demos/byoverbs.py --
    pdb.pm()  # shows why it doesn't work, when it doesn't work
"""

# code reviewed by people, and by Black and Flake8


import os
import pdb
import sys

... == pdb  # unneeded till like:  pdb.pm()


# Run from the Sh Command Line


def main():
    """Run from the Sh Command Line"""

    import byoverbs.bin.byotools as byo

    parser = byo.ArgumentParser()
    parser.parse_args_else()  # often prints help & exits


# Run from the Sh Command Line, only when imported

if __name__ == "__main__":
    main()

    sys.exit()


# Find our Dir in the Sys Path

DIR_ENDSWITH = "/demos"

DIR = os.path.abspath(os.path.dirname(__file__))
assert DIR.endswith(DIR_ENDSWITH), DIR
DEPTH = len(DIR_ENDSWITH.split("/"))

ABS_DIRS = list(os.path.abspath(_) for _ in sys.path)
DIR_INDEX = ABS_DIRS.index(DIR)  # often first

# print()
# print("imported byoverbs from", DIR_INDEX, ABS_DIRS)

if ABS_DIRS[1:]:  # never last of two or more, to block indefinite recursion
    # assert False  # injects failure, while uncommented
    assert DIR_INDEX != (len(ABS_DIRS) - 1), (DIR_INDEX, DIR, len(sys.path), sys.path)


# Find the Dir containing the Abs Name of our Git Root Dir, aka our Package Dir

FAR_ABOVE_DIR = os.path.abspath(os.path.join(DIR, *(DEPTH * [os.pardir])))
# such as a Dir containing a Sym Link to our:  git rev-parse --show-toplevel


# Redefine Imports as from Sys Path minus our Dir, else near its Abs Name, else us again

sys.path.remove(sys.path[DIR_INDEX])
sys.path.append(FAR_ABOVE_DIR)
sys.path.append(DIR)


# Retry the Import of ByoVerbs once, and maybe recurse to work harder, else quit

del sys.modules[__name__]

if True:  # ducks Flake8 E402 module.level.import.not.at.top.of.file
    # print()
    # print("importing byoverbs from", sys.path)
    import byoverbs

    _ = byoverbs


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/demos/byoverbs.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
