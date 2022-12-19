#!/usr/bin/env python3

"""
usage: maskup.py [-h]

copy input to output, but randomize runs of decimal, hex, alphabetics, or alphanumerics

options:
  -h, --help  show this help message and exit

quirks:
  wrongly discloses the more narrow type of a run that could be a wider type
  delays infinitely & looks weird if you paste in an open line prefaced by closed lines

examples:
  open https://shell.cloud.google.com/?show=terminal  # if you need another Linux
  git clone https://github.com/pelavarre/byoverbs.git
  demos/maskup.py  # show these examples
  demos/maskup.py --  # randomize runs of hex, and runs of alphanumerics
"""

# code reviewed by people, and by Black and Flake8
# developed by:  cls && F=demos/maskup.py && black $F && flake8 $F && $F --


import __main__
import random
import re
import string
import sys
import textwrap


def main():
    """Run from the Sh Command Line"""

    exit_if()  # shows examples or help lines and quit

    sys_stderr_print("Press ⌃D to quit")
    sys_stderr_print()

    while True:
        line = sys.stdin.readline()  # copies 1 Line from Input
        if not line:

            break

        oline = line_maskup(line)
        print(oline)  # copies 1 Line to Output


def line_maskup(line):
    """Randomize runs of hex, and runs of alphanumerics"""

    assert re.match(r"^[0-9]+$", string=string.digits)
    assert re.match(r"^[0-9A-Fa-f]+$", string=string.hexdigits)
    assert re.match(r"^([A-Z]+)$", string=string.ascii_uppercase)
    assert re.match(r"^([a-z]+)$", string=string.ascii_lowercase)
    assert re.match(r"^([A-Za-z]+)$", string=string.ascii_letters)
    assert re.match(r"^([0-9A-Za-z]+)$", string=(string.ascii_letters + string.digits))

    splits = re.split(r"([0-9A-Za-z]+)", string=line)
    assert len(splits) % 2, splits

    sep = splits[0]
    maskup = sep
    for (hit, sep) in zip(splits[1::2], splits[2::2]):
        if re.match(r"^[0-9]+$", string=hit):
            maskup += length_maskup(string.digits, len(hit))
        elif re.match(r"^[0-9A-Fa-f]+$", string=hit):
            maskup += length_maskup(string.hexdigits, len(hit))
        elif re.match(r"^([A-Z]+)$", string=hit):
            maskup += length_maskup(string.ascii_uppercase, len(hit))
        elif re.match(r"^([a-z]+)$", string=hit):
            maskup += length_maskup(string.ascii_lowercase, len(hit))
        elif re.match(r"^([A-Za-z]+)$", string=hit):
            maskup += length_maskup(string.ascii_letters, len(hit))
        else:
            maskup += length_maskup(string.ascii_letters + string.digits, len(hit))
        maskup += sep

    return maskup


def length_maskup(choices, length):
    """Catenate shuffled choices as a random enough substitute to show length"""

    items = list(choices)

    random.shuffle(items)

    chars = ""
    while len(chars) < length:
        random.shuffle(items)
        chars += "".join(items)

    maskup = chars[:length]

    return maskup


# deffed in many files  # missing from docs.python.org
def exit_if():
    """Show examples or help lines and quit, else return"""

    doc = __main__.__doc__.strip()

    testdoc = doc
    testdoc = testdoc[testdoc.index("examples") :]
    testdoc = textwrap.dedent("\n".join(testdoc.splitlines()[1:])).strip()

    sys_parms = sys.argv[1:]
    if not sys_parms:
        print(testdoc)

        sys.exit()

    elif sys_parms != ["--"]:
        print(doc)

        sys.exit()


# deffed in many files  # missing from docs.python.org
def sys_stderr_print(*args, **kwargs):
    """Work like Print, but write Sys Stderr in place of Sys Stdout"""

    kwargs_ = dict(kwargs)
    if "file" not in kwargs.keys():
        kwargs_["file"] = sys.stderr

    sys.stdout.flush()

    print(*args, **kwargs_)

    if "file" not in kwargs.keys():
        sys.stderr.flush()


_ = """  # example input

    ’Twas brillig, and the slithy toves
          Did gyre and gimble in the wabe:
    All mimsy were the borogoves,
          And the mome raths outgrabe.

"""

_ = """  # example output

    ’rKHd aykzosl, ekq ncf eklgnx xblfw
          TpO uomd oyi aotsey yd aeu rhmy:
    MtF cmkri tqbc adx rzacqhovf,
          JfM nes jqza lonyk szpqvrwy.

"""


if __name__ == "__main__":
    main()


# todo: 1 doesn't show what kinds of Characters it sees you gave it
# todo: 2 it doesn't invite you to override its choices of what kinds to see


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/tictactoe.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
