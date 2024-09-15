#!/usr/bin/env python3

r"""
usage: hashbang.py [-h]

glance over File has Ext vs not, and starts with Hashbang vs not

options:
  -h, --help   show this help message and exit
"""

# code reviewed by People, Black, Flake8, & MyPy


import os
import pathlib
import sys


def main() -> None:

    assert sys.argv[1].startswith("--"), sys.argv[1:]

    pathnames_by_key: dict[tuple[bool, bool, bool], list[str]]
    pathnames_by_key = dict()

    for root, dirs, files in os.walk(top="."):
        dirs[::] = sorted(dirs)

        if root == ".":
            if ".git" in dirs:
                dirs.remove(".git")

        for file in files:
            pathname = os.path.join(root, file)
            pathname = pathname.removeprefix("./")

            #

            (name, ext) = os.path.splitext(pathname)
            has_ext = bool(ext)

            path = pathlib.Path(pathname)
            is_xecutable = bool(path.stat().st_mode & 0o111)

            lines = path.read_text().splitlines()
            has_hashbang = bool(lines and lines[0].startswith("#!"))

            #

            key = (has_ext, is_xecutable, has_hashbang)

            if key not in pathnames_by_key.keys():
                pathnames_by_key[key] = list()
            pathnames_by_key[key].append(pathname)

    d = dict()
    for i in range(8):
        (has_ext, is_xecutable, has_hashbang) = list(bool(int(_)) for _ in f"{i:03b}")
        rep = "#"
        rep += " Ext" if has_ext else ""
        rep += " Xecutable" if is_xecutable else ""
        rep += " Hashbang" if has_hashbang else ""
        d[(has_ext, is_xecutable, has_hashbang)] = rep

    for key, pathnames in sorted(pathnames_by_key.items()):
        print()
        print(d[key])
        print(" ".join(pathnames))


main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/hashbang.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
