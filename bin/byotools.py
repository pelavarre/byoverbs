# deffed in many packages  # missing from:  https://pypi.org

"""
usage: import byotools as byo  # define Func's

competently welcome you into Sh Terminal work, batteries included

examples:
  byo.sys_exit_if()  # prints examples or help lines and exits, else returns
"""

import __main__
import argparse
import datetime as dt
import difflib
import os
import pdb
import shlex
import signal
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
# Add some Def's to Import ArgParse
#


def compile_argdoc(epi, drop_help=None):
    """Construct an ArgumentParser, from ArgDoc, without Positional Args and Options"""

    argdoc = __main__.__doc__  # could be:  argdoc = doc if doc else __main__.__doc__

    doc_lines = argdoc.strip().splitlines()
    prog = doc_lines[0].split()[1]  # first word of first line

    doc_firstlines = list(_ for _ in doc_lines if _ and (_ == _.lstrip()))
    description = doc_firstlines[1]  # first line of second paragraph

    add_help = not drop_help

    epilog_at = argdoc.index(epi)
    epilog = argdoc[epilog_at:]

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=add_help,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    return parser


def exit_unless_doc_eq(parser):
    """Complain and exit nonzero, unless Arg Doc equals Parser Format_Help"""

    # Fetch the Main Doc, and note where from

    main_doc = __main__.__doc__.strip()
    main_filename = os.path.split(__file__)[-1]
    got_filename = "./{} --help".format(main_filename)

    # Fetch the Parser Doc from a fitting virtual Terminal
    # Fetch from a Black Terminal of 89 columns, not current Terminal width
    # Fetch from later Python of "options:", not earlier Python of "optional arguments:"

    with_columns = os.getenv("COLUMNS")
    os.environ["COLUMNS"] = str(89)
    try:

        parser_doc = parser.format_help()

    finally:
        if with_columns is None:
            os.environ.pop("COLUMNS")
        else:
            os.environ["COLUMNS"] = with_columns

    parser_doc = parser_doc.replace("optional arguments:", "options:")

    parser_filename = "ArgumentParser(...)"
    want_filename = parser_filename

    # Print the Diff to Parser Doc from Main Doc and exit, if Diff exists

    got_doc = main_doc
    want_doc = parser_doc

    diff_lines = list(
        difflib.unified_diff(
            a=got_doc.splitlines(),
            b=want_doc.splitlines(),
            fromfile=got_filename,
            tofile=want_filename,
        )
    )

    if diff_lines:
        print("\n".join(diff_lines))

        sys.exit(2)  # trust caller to log SystemExit exceptions well


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
# Add some Def's to Type Str
#


def str_removeprefix(chars, prefix):
    """Remove Prefix from Chars if present, till Oct/2020 Python 3.9 str.removeprefix"""

    result = chars
    if prefix and chars.startswith(prefix):
        result = chars[len(prefix) :]

    return result


def str_removesuffix(chars, suffix):
    """Remove Suffix from Chars if present, till Oct/2020 Python 3.9 str.removesuffix"""

    result = chars
    if suffix and chars.endswith(suffix):
        result = chars[: -len(suffix)]

    return result


#
# Add some Def's to Import SubProcess
#


def subprocess_run_plus(shline):
    """Call SubProcess Run on a ShLine, without Stdin, with Check True"""

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


def sys_exit():
    """Prints examples or help lines or exception, and exits"""

    sys_exit_if()

    raise NotImplementedError(sys.argv[1:])


def sys_exit_if(shline=None, ttyline=None):
    """Print examples & exit, or print help lines & exit, or shell out & return"""

    alt_ttyline = ttyline if ttyline else shline

    # Sometimes print & exit

    sys_exit_if_testdoc()  # prints examples & exits if no args

    sys_exit_if_argdoc()  # prints help lines & exits if "--h" arg, but ignores "-h"

    sys_exit_if_not_implemented()  # raises unhandled exception if arg isn't just:  --

    # Call the ShLine, if any

    if shline:
        sys_stderr_print("+ {}".format(alt_ttyline))
        subprocess_run_plus(shline)

    # Succeed

    pass


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


def sys_stdin_prompt_if():
    """Prompt for TTY EOF before blocking to read more of it"""

    CONTROL_KEYCAP = "\N{Up Arrowhead}"  # ⌃
    if sys.stdin.isatty():
        sys_stderr_print("Press {}D TTY EOF to quit".format(CONTROL_KEYCAP))


def sys_stdin_readline_else():
    """Take a Line from Sys StdIn, else exit zero or nonzero"""

    SIGINT_RETURNCODE_130 = 0x80 | signal.SIGINT
    assert SIGINT_RETURNCODE_130 == 130, SIGINT_RETURNCODE_130

    try:
        line = sys.stdin.readline()
    except KeyboardInterrupt:
        sys.stderr.write("\n")
        sys.stderr.write("KeyboardInterrupt\n")

        sys.exit(SIGINT_RETURNCODE_130)  # exits 130 to say KeyboardInterrupt SIGINT

    if not line:  # already echoed as "^D\n" at Mac, already echoed as "\n" at Linux

        sys.exit()  # exits None to say Stdin Closed

    chars = line.splitlines()[0]  # picks out Chars of Line, apart from Line End

    return chars


def sys_stderr_print(*args, **kwargs):
    """Work like Print, but write Sys Stderr in place of Sys Stdout"""

    kwargs_ = dict(kwargs)
    if "file" not in kwargs.keys():
        kwargs_["file"] = sys.stderr

    sys.stdout.flush()

    print(*args, **kwargs_)

    if "file" not in kwargs.keys():
        sys.stderr.flush()
