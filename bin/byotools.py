# deffed in many packages  # missing from:  https://pypi.org

"""
usage: import byotools as byo  # define Func's

competently welcome you into Sh Terminal work, batteries included

examples:
  byo.sys_exit_if()  # prints examples or help lines and exits, else returns
"""

import __main__
import datetime as dt
import os
import pdb
import shlex
import subprocess
import sys
import textwrap

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace  # needed till Jun/2018 Python 3.7

_ = subprocess.run  # new since Sep/2015 Python 3.5
_ = dt.datetime.now().astimezone()  # new since Dec/2016 Python 3.6
# _ = breakpoint  # new since Jun/2018 Python 3.7
# _ = importlib.import_module("dataclasses")  # new since Jun/2018 Python 3.7
# _ = f"{sys.version_info[:3]=}"  # new since Oct/2019 Python 3.8
# _ = shlex.join  # new since Oct/2019 Python 3.8
# _ = str.removesuffix  # new since Oct/2020 Python 3.9
# _  = list(zip([], [], strict=True))  # since Oct/2021 Python 3.10


#
# Add some Def's to Import Ast
#


AST_DEFAULT_DOC = """
    usage: $VERB.py [-h] ...

    give examples of:  $VERB

    options:
      -h, --help  show this help message and exit

    examples:
      $VERB.py  # show these examples and exit
      $VERB.py --  # guess what to do, and do it
"""


def ast_fetch_argdoc():
    """Fetch the Sh Terminal help lines for running the main module"""

    # Form an Arg Doc containing the Main Doc as its Test Doc

    main_doc = __main__.__doc__
    main_doc = textwrap.dedent(main_doc).strip()
    main_lines = main_doc.splitlines()

    main_file = __main__.__file__
    prog = os.path.split(main_file)[-1]
    verb = os.path.splitext(prog)[0]

    default_doc = textwrap.dedent(AST_DEFAULT_DOC).strip()
    dented = "\n".join(("  " + _) for _ in main_lines)

    doc = default_doc
    doc = doc.replace("$VERB", verb)
    doc += "\n" + dented

    # Take the Main Doc as the Arg Doc if it starts with Usage, else as Test Doc

    word = main_lines[0].split()[0]
    if word == "usage:":

        return main_doc

    return doc


def ast_fetch_testdoc():
    """Fetch the Sh Terminal examples from the help lines for running the main module"""

    # Pick a Test Doc out of the Main Doc, just past the last Unindented Line

    main_doc = __main__.__doc__
    main_doc = textwrap.dedent(main_doc).strip()
    main_lines = main_doc.splitlines()

    start = 0
    for (index, line) in enumerate(main_lines):
        if line and not line.startswith(" "):
            start = index

    doc = "\n".join(main_lines[start:][1:])
    doc = textwrap.dedent(doc).strip()

    # Take the Main Doc as the Test Doc if it doesn't start with Usage, else as Arg Doc

    word = main_lines[0].split()[0]
    if word != "usage:":

        return main_doc

    return doc


#
# Add some Def's to Import Os
#


#
# Add some Def's to Import ShLex
#


def shlex_parms_dash_dash_h(parms):
    """Return Truthy if '--help' or '--hel' or ... '--h' before '--'"""

    for parm in parms:
        if parm == "--":  # ignores '--help' etc after '--'

            break

        if parm.startswith("--h") and "--help".startswith(parm):

            return True


def shlex_parms_one_posarg():
    """Accept one Arg without "-" Dash Options, preceded by a "--" Sep or not"""

    parms = sys.argv[1:]
    if sys.argv[1:][:1] == ["--"]:
        parms = sys.argv[2:]

    parm = None
    if len(parms) == 1:
        parm = parms[-1]
        if parm.startswith("-"):
            parm = None

    return parm


#
# Add some Def's to Import SubProcess
#


def subprocess_run(shline):
    """Call SubProcess Run on a ShLine, but with Shell None, and without Stdin"""

    argv = shlex.split(shline)

    _ = subprocess.run(argv, stdin=subprocess.PIPE, check=True)


def subprocess_run_oneline(shline):
    """Pull 1 Line from SubProcess Run"""

    argv = shlex.split(shline)

    run = subprocess.run(
        argv,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    assert not run.stderr, run.stderr

    stdout = run.stdout.decode()
    lines = stdout.splitlines()

    assert len(lines) == 1, repr(lines[:3])

    line = lines[-1]

    return line


#
# Add some Def's to Import Sys
#


def sys_exit_if():
    """Print examples and exit, else print help lines and exit, else return"""

    sys_exit_if_testdoc()
    sys_exit_if_argdoc()
    sys_exit_if_not_implemented()


def sys_exit_if_argdoc():
    """Print help lines and exit"""

    doc = ast_fetch_argdoc()

    parms = sys.argv[1:]
    if shlex_parms_dash_dash_h(parms):
        print(doc)

        sys.exit()


def sys_exit_if_not_implemented():
    """Exit by raising unhandled NotImplementedError() if given options or args"""

    parms = sys.argv[1:]
    if parms != ["--"]:

        raise NotImplementedError(sys.argv[1:])


def sys_exit_if_testdoc():
    """Print examples and exit"""

    testdoc = ast_fetch_testdoc()

    parms = sys.argv[1:]
    if not parms:
        print()
        print(testdoc)
        print()

        sys.exit()


def sys_stderr_print(*args, **kwargs):
    """Work like Print, but write Sys Stderr in place of Sys Stdout"""

    kwargs_ = dict(kwargs)
    if "file" not in kwargs.keys():
        kwargs_["file"] = sys.stderr

    sys.stdout.flush()

    print(*args, **kwargs_)

    if "file" not in kwargs.keys():
        sys.stderr.flush()
