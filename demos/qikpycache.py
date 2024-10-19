r"""
usage: from demos import qikpycache

persist into the './__pycache__/' Dir a Cache of Func Calls and Results

see also:
  functools.lru_cache

examples:
  rm -fr __pycache__/
  python3 demos/qikpycache.py
"""

# code reviewed by people, and by Black and Flake8


import __main__
import atexit
import datetime as dt
import json
import os
import pathlib
import pdb
import sys

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace  # needed till Jun/2018 Python 3.7


MAIN_FIND = os.path.abspath(sys.argv[0])
if hasattr(__main__, "__file__"):
    MAIN_FIND = os.path.abspath(__main__.__file__)

MAIN_NAME = os.path.splitext(os.path.basename(MAIN_FIND))[0]

CACHE_GLOB = "__pycache__/qik-*-calls.json"
CACHE_FIND = CACHE_GLOB.replace("*", MAIN_NAME)


MODULE = sys.modules[__name__]

_CACHE_STAMP = None
_CACHE_DUMP = None
_CACHE_DICT = None


#
# Run from the Sh Command Line
#


def main():
    """Run from the Sh Command Line"""

    tryme(1)
    tryme(2)
    tryme(3)


def tryme(arg):
    """Try cacheing one Call of SubProcess Run"""

    import datetime as dt
    import subprocess

    import qikpycache

    t0 = dt.datetime.now()
    run_dict = qikpycache.try_call(
        subprocess.run,
        "echo hello".split(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        errors="surrogateescape",
    )
    t1 = dt.datetime.now()

    run = subprocess.CompletedProcess(
        args=run_dict["args"],
        returncode=run_dict["returncode"],
        stdout=run_dict["stdout"],
        stderr=run_dict["stderr"],
    )

    print(t1 - t0, run)


def try_call(func, *args, **kwargs):
    """Call and raise Exception, else Call and store Result, else fetch Result"""

    # Form a Key

    module_funcname = "{}.{}".format(func.__module__, func.__name__)
    key = json.dumps([module_funcname, args, kwargs])

    # Call if no Result found

    dump_by_key = load_from_file()
    if key not in dump_by_key.keys():
        result = func(*args, **kwargs)

        try:
            dump = json.dumps(result)
        except TypeError:
            result_dict = vars(result)
            dump = json.dumps(result_dict)

        dump_by_key[key] = dump

    # Fetch the result

    load = dump_by_key[key]
    result_dict = json.loads(load)

    return result_dict


def clear_in_process():
    """Drop all Cache Keys"""

    if _CACHE_DICT is not None:
        _CACHE_DICT.clear()


def stamp_from_file():
    """Say when Cache File last modified before Load, else return None if no File"""

    load_from_file()

    return _CACHE_STAMP


def load_from_file():
    """Load Cache from File"""

    # Load once per Process

    if _CACHE_DICT is not None:
        return _CACHE_DICT

    # Load as empty if no File exist

    MODULE._CACHE_DICT = dict()  # replaces
    atexit.register(dump_changes_to_file)

    path = pathlib.Path(CACHE_FIND)
    if not path.exists():
        return _CACHE_DICT

    # Load from File if File exists

    stat = path.stat()
    dump = path.read_text()
    j = json.loads(dump)

    stamp = dt.datetime.fromtimestamp(stat.st_mtime)

    MODULE._CACHE_DUMP = dump  # replaces
    MODULE._CACHE_STAMP = stamp  # replaces
    MODULE._CACHE_DICT = j  # replaces

    # Promise to load just once per Process

    assert _CACHE_DICT is not None

    # Announce which Key:Value Pairs fetched

    return _CACHE_DICT


def dump_changes_to_file():
    """Dump Cache to File when called, only if it has changed"""

    # Dump only when not empty

    if not _CACHE_DICT.keys():
        return

    # Dump after change

    dump = json.dumps(_CACHE_DICT)
    if dump != _CACHE_DUMP:
        path = pathlib.Path(CACHE_FIND)
        if not path.parent.is_dir():
            path.parent.mkdir()

        path.write_text(dump + "\n")

        # Say when dumped, as if reloaded

        stat = path.stat()
        stamp = dt.datetime.fromtimestamp(stat.st_mtime)
        MODULE._CACHE_STAMP = stamp  # replaces

        # Don't dump again till after more change

        MODULE._CACHE_DUMP = dump  # replaces

    # Announce how many Chars written

    return _CACHE_DUMP


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    assert sys.argv[1:], sys.argv

    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/qikpycache.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
