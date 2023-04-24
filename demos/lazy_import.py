#!/usr/bin/env python3

"""
usage: lazy_import.py [ARG [ARG ...]

examples:
  python3 -i demos/lazy_import.py
    dt
    dir(os.path)
    xml.__file__
    urllib.parse.quote
"""

import importlib
import sys
import urllib.parse
from decimal import Decimal as D


_ = D  # todo: lazy-import X.Y as Z, not just lazy-import X as Z
_ = urllib.parse  # todo: lazy-import X.Y, not just lazy-import X


print(">>> import ...", file=sys.stderr)
print(">>> ", file=sys.stderr)


LAZY_IMPORT_NAMES = """

    __main__

    argparse collections copy decimal difflib functools
    getpass glob hashlib html importlib itertools json
    os pathlib pdb platform pprint random re
    select shlex shutil signal stat string subprocess sys
    termios textwrap time traceback tty unicodedata urllib xml

""".split()


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
    for name in LAZY_IMPORT_NAMES:
        if name not in g.keys():
            g[name] = LazyImport(name)

    if "dt" not in g.keys():
        dt = LazyImport(import_="datetime", as_="dt")
        g["dt"] = dt

    if "et" not in g.keys():
        et = LazyImport(import_="xml.etree.ElementTree", as_="et")
        g["et"] = et


def_some_lazy_imports()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/lazy_import.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
