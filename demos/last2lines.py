#!/usr/bin/env python3

r"""
usage: last2lines.py [-h] DIR [DIR ...]

autocorrect the last 4 Lines of every Py File in the Dir

positional arguments:
  DIR         files to edit

options:
  -h, --help  show this help message and exit

examples:
  demos/last2lines.py bin/
"""

import __main__
import os
import pathlib
import sys


FIND = os.path.abspath(sys.argv[0])
assert FIND.endswith("/demos/last2lines.py"), (FIND,)

DIR = os.path.dirname(FIND)
sys.path[1:1] = [os.path.join(DIR, os.pardir, "bin")]

try:  # says 'try/except/raise' to get Flake8 to accept Import from edited Sys Path
    import byotools as byo
except Exception:
    raise


def main() -> None:
    """Run from the Sh Command Line"""

    # Parse the Sh Command Line

    parser = byo.ArgumentParser()
    parser.add_argument("dirnames", metavar="DIR", nargs="+", help="files to edit")
    args = parser.parse_args_else()  # often prints help & exits zero

    # Pick out the Last 4 Lines from this Source File

    main_name = __main__.__file__
    main_path = pathlib.Path(main_name)
    main_text = main_path.read_text()
    main_tail = "\n".join(main_text.splitlines()[-4:]) + "\n"

    main.tail = main_tail

    # Visit each File of the Dir

    edits = list()
    loud_pyfinds = list()
    pyfinds = list()

    main.edits = edits
    main.loud_pyfinds = loud_pyfinds
    main.pyfinds = pyfinds

    dirnames = args.dirnames
    for dirname in dirnames:
        items = sorted(os.listdir(dirname))

        for item in items:
            find = os.path.join(dirname, item)
            assert "//" not in find, (find,)

            # Fetch each Py File, and edit zero or more of them

            ext = os.path.splitext(find)[-1]
            if ext == ".py":
                visit_py_find(find)

    # Say what happened

    join = " ".join(loud_pyfinds)
    if loud_pyfinds:
        print()
        print(r"vi {} +'/# posted into\|# copied from'".format(join))

    print()
    print(
        "last2lines.py: edited {} of {} Py Files found in {} Dirs".format(
            len(edits), len(pyfinds), len(dirnames)
        )
    )


def visit_py_find(find) -> None:
    """Fetch this Py File, review it, and auto-correct it if need be"""

    edits = main.edits
    loud_pyfinds = main.loud_pyfinds
    pyfinds = main.pyfinds
    main_tail = main.tail

    pyfinds.append(find)

    path = pathlib.Path(find)
    text = path.read_text()
    tail = "\n".join(text.splitlines()[-4:]) + "\n"

    # Add the Autocorrection of 4 new Autostyled Lines if not present already

    repl = main_tail.replace("demos/last2lines.py", find)

    alt_text = text
    if tail != repl:
        if text:
            edits.append(find)
            alt_text = text + repl
            with open(find, "a") as appending:
                appending.write(repl)

    # Surface more than 1 'posted into' or 'copied from' mark

    lines = alt_text.splitlines()

    loud_pairs = list()
    for index, line in enumerate(lines):
        line_number = 1 + index

        if line.startswith("# posted into:"):
            loud_pairs.append([line_number, line])
        if line.startswith("# copied from:"):
            loud_pairs.append([line_number, line])

    if text:
        if len(loud_pairs) != 2:
            loud_pyfinds.append(find)


# Run from the Sh Command Line, if not imported

if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/last2lines.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
