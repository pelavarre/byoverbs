#!/usr/bin/env python3

"""
usage: lazy_import.py [ARG [ARG ...]

try out some Python without making you type out its "import"s

examples:
  python3 -i demos/lazy_import.py
    dt
    dir(os.path)
    xml.__file__
    urllib.parse.quote
"""

import importlib
import os
import sys
import urllib.parse
from decimal import Decimal as D


_ = D  # todo: lazy-import X.Y as Z, not just lazy-import X as Z
_ = urllib.parse  # todo: lazy-import X.Y, not just lazy-import X


print(">>> import ...", file=sys.stderr)
print(">>> ", file=sys.stderr)


QUICK_LAZY_IMPORT_NAMES = """


    # hard-to-discover basics

    __main__

    itertools time


    # from ".so" Shared Object Libraries

    array audioop binascii cmath fcntl grp
    math mmap nis pyexpat readline resource select syslog termios unicodedata zlib


    # from Py Files

    abc aifc antigravity argparse ast asynchat asyncore  base64 bdb bisect bz2
    cProfile calendar cgi cgitb chunk cmd code codecs codeop colorsys
        compileall configparser contextlib contextvars copy copyreg crypt csv
    dataclasses datetime decimal difflib dis doctest  enum
    filecmp fileinput fnmatch fractions ftplib functools
    genericpath getopt getpass gettext glob graphlib gzip
    hashlib heapq hmac  imaplib imghdr imp inspect io ipaddress  keyword
    linecache locale lzma

    mailbox mailcap mimetypes modulefinder
    netrc nntplib ntpath nturl2path numbers  opcode operator optparse os
    pathlib pdb pickle pickletools pipes pkgutil platform plistlib poplib posixpath
        pprint profile pstats pty py_compile pyclbr pydoc
    queue quopri  random reprlib rlcompleter runpy
    sched secrets selectors shelve shlex shutil signal site smtpd smtplib sndhdr socket
        socketserver sre_compile sre_constants sre_parse ssl stat statistics string
        stringprep struct subprocess sunau symtable sysconfig
    tabnanny tarfile telnetlib tempfile textwrap this threading timeit token tokenize
        trace traceback tracemalloc tty turtle types typing
    uu uuid warnings  wave weakref webbrowser  xdrlib  zipapp zipfile zipimport


    # from Dirs containing an "_init__.py" File

    asyncio  collections concurrent ctypes curses  dbm distutils
    email encodings ensurepip  html http  idlelib importlib  json  lib2to3 logging

    multiprocessing  pydoc_data  re  sqlite3  test tkinter tomllib turtledemo
    unittest urllib  venv  wsgiref  xml xmlrpc  zoneinfo


    # from VEnv Pip Install

    requests


""".splitlines()

QUICK_LAZY_IMPORT_NAMES = list(_.partition("#")[0] for _ in QUICK_LAZY_IMPORT_NAMES)
QUICK_LAZY_IMPORT_NAMES = list(_.strip() for _ in QUICK_LAZY_IMPORT_NAMES)
QUICK_LAZY_IMPORT_NAMES = " ".join(QUICK_LAZY_IMPORT_NAMES).split()


class LazyImport:
    """Defer the work of "import X as Y" till first Y.Z fetched"""

    def __init__(self, import_, as_=None):
        self.import_ = import_
        self.as_ = import_ if (as_ is None) else as_

    def __getattribute__(self, name):
        if name in "as_ import_".split():
            return super().__getattribute__(name)
        module = importlib.import_module(self.import_)
        globals()[self.as_] = module
        return module.__getattribute__(name)

    def __repr__(self):
        module = importlib.import_module(self.import_)
        globals()[self.as_] = module
        return module.__repr__()


def def_some_lazy_imports():
    """Define some Global Names now, to import later"""

    g = globals()
    for name in QUICK_LAZY_IMPORT_NAMES:
        if name not in g.keys():
            g[name] = LazyImport(name)

    if "dt" not in g.keys():
        dt = LazyImport(import_="datetime", as_="dt")
        g["dt"] = dt

    if "et" not in g.keys():
        et = LazyImport(import_="xml.etree.ElementTree", as_="et")
        g["et"] = et


def discover_more_lazy_imports():
    """Search out Module Names to Import"""

    pynames = list()
    dirnames = list()

    top = os.path.dirname(os.__file__)
    for find in sorted(os.listdir(top)):
        (name, ext) = os.path.splitext(find)
        if not name.startswith("_"):
            if ext == ".py":
                pynames.append(name)
            elif os.path.exists(os.path.join(top, name, "__init__.py")):
                dirnames.append(name)

    print()
    print(" ".join(pynames))

    print()
    print(" ".join(dirnames))


# help("modules")  # ~500..5000 ms, plus 0..N lines of Stderr

# discover_more_lazy_imports()  # ~500 ms

def_some_lazy_imports()  # ~0.75 ms


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/lazy_import.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
