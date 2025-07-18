#!/usr/bin/env python3

"""
usage: lazy_import.py [ARG [ARG ...]

try out some Python without making you type out its "import"s

docs:
  https://docs.python.org/3/library/builtins.html
  https://docs.python.org/3/library/importlib.html

examples:
  python3 -i demos/lazy_import.py
    type(urllib.parse)
    type(dt)
    now = dt.datetime.now()
    print(now)
    dir(os.path)
    xml.__file__
    print(len(globals().keys()))
    # globals()  # would import ALL of these Modules
"""

import argparse
import builtins
import datetime as dt
import importlib
import os
import sys
import urllib.parse
import zoneinfo
from decimal import Decimal as D


_: object  # '_: object' tells MyPy to accept '_ =' tests across two and more Datatypes

_ = D  # todo: lazy-import X.Y as Z, not just lazy-import X as Z
_ = builtins  # so that CPython:  builtins is __builtins__
_ = urllib.parse  # todo: lazy-import X.Y, not just lazy-import X


# Do speculatively run a few lines of Python in advance

print(">>> import argparse, builtins, importlib, os, sys, urllib.parse, zoneinfo", file=sys.stderr)
print(">>> import ... D ... Pacific ... PacificLaunch ... parser ... dt ... t ...", file=sys.stderr)
print(">>> ", file=sys.stderr)

Pacific = zoneinfo.ZoneInfo("America/Los_Angeles")
PacificLaunch = dt.datetime.now(Pacific)

parser = argparse.ArgumentParser()
t = dt.datetime.now().astimezone(Pacific)


QUICK_LAZY_IMPORT_NAMES = """


    # hard-to-discover basics
    # sorted(_[0] for _  in sys.modules.items() if not hasattr(_[-1], "__file__"))

    __main__

    atexit builtins errno itertools marshal posix pwd sys time


    # from ".so" Shared Object Libraries
    # minus deprecated: audioop nis pyexpat

    array binascii cmath fcntl grp
    math mmap readline resource select syslog termios unicodedata zlib


    # from Py Files
    # minus deprecated: aifc cgi cgitb chunk crypt imghdr
    # minus deprecated: mailcap nntplib pipes sndhdr sunau telnetlib uu uuid xdrlib

    abc antigravity argparse ast asynchat asyncore  base64 bdb bisect bz2
    cProfile calendar cmd code codecs codeop colorsys
        compileall configparser contextlib contextvars copy copyreg csv
    dataclasses datetime decimal difflib dis doctest  enum
    filecmp fileinput fnmatch fractions ftplib functools
    genericpath getopt getpass gettext glob graphlib gzip
    hashlib heapq hmac  imaplib imp inspect io ipaddress  keyword
    linecache locale lzma

    mailbox mimetypes modulefinder
    netrc ntpath nturl2path numbers  opcode operator optparse os
    pathlib pdb pickle pickletools pkgutil platform plistlib poplib posixpath
        pprint profile pstats pty py_compile pyclbr pydoc
    queue quopri  random reprlib rlcompleter runpy
    sched secrets selectors shelve shlex shutil signal site smtpd smtplib socket
        socketserver sre_compile sre_constants sre_parse ssl stat statistics string
        stringprep struct subprocess symtable sysconfig
    tabnanny tarfile tempfile textwrap this threading timeit token tokenize
        trace traceback tracemalloc tty turtle types typing
    warnings  wave weakref webbrowser  zipapp zipfile zipimport


    # from Dirs containing an "_init__.py" File

    asyncio  collections concurrent ctypes curses  dbm distutils
    email encodings ensurepip  html http  idlelib importlib  json  lib2to3 logging

    multiprocessing  pydoc_data  re  sqlite3  test tkinter tomllib turtledemo
    unittest urllib urllib.parse  venv  wsgiref  xml xmlrpc  zoneinfo


    # from VEnv Pip Install

    jira matplotlib numpy pandas psutil psycopg2 redis requests


""".splitlines()

QUICK_LAZY_IMPORT_NAMES = list(_.partition("#")[0] for _ in QUICK_LAZY_IMPORT_NAMES)
QUICK_LAZY_IMPORT_NAMES = list(_.strip() for _ in QUICK_LAZY_IMPORT_NAMES)
QUICK_LAZY_IMPORT_NAMES = " ".join(QUICK_LAZY_IMPORT_NAMES).split()

assert len(QUICK_LAZY_IMPORT_NAMES) == 201, (len(QUICK_LAZY_IMPORT_NAMES), 201)


class LazyImport:
    """Defer the work of "import X as Y" till first Y.Z fetched"""

    def __init__(self, import_, as_=None) -> None:
        self.import_ = import_
        self.as_ = import_ if (as_ is None) else as_

    def __getattribute__(self, name) -> object:
        if name in "as_ import_ beep_".split():
            return super().__getattribute__(name)
        self.beep_()
        module = importlib.import_module(self.import_)
        globals()[self.as_] = module
        return module.__getattribute__(name)

    def __repr__(self) -> str:
        self.beep_()
        module = importlib.import_module(self.import_)
        globals()[self.as_] = module
        return module.__repr__()

    def beep_(self) -> None:
        auto = " # viva lazy automagic"
        if self.import_ == self.as_:
            print(">>> import", self.import_, auto, file=sys.stderr)
        else:
            print(">>> import", self.import_, "as", self.as_, auto, file=sys.stderr)

        # todo: sad when "beep_" runs in the middle of a Row


def def_some_lazy_imports() -> None:
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

    if "np" not in g.keys():
        np = LazyImport(import_="numpy", as_="np")
        g["np"] = np

    if "pd" not in g.keys():
        pd = LazyImport(import_="pandas", as_="pd")
        g["pd"] = pd

    if "plt" not in g.keys():
        plt = LazyImport(import_="matplotlib.pyplot", as_="plt")
        g["plt"] = plt


def discover_more_lazy_imports() -> None:
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


# todo: up line, insert line, print Import, restore cursor - when Import happens


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/demos/lazy_import.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
