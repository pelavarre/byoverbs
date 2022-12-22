# deffed in many packages  # missing from:  https://pypi.org

"""
usage: import byotools as byo  # define Func's

competently welcome you into Sh Terminal work, batteries included

examples:
  byo.sys_exit_if()  # prints examples or help or args and exits, else returns
  byo.subprocess_exit_run_if(shline)  # prints and exits, else calls $SHELL and returns
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


def sys_exit_if_argdoc_ne(parser):
    """Print Diff and exit nonzero, unless Arg Doc equals Parser Format_Help"""

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

    # https://github.com/python/cpython/issues/53903  <= options: / optional arguments:
    # https://bugs.python.org/issue38438  <= usage: [WORD ... ] / [WORD [WORD ...]]


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
# Add some Def's to Type List
#


def list_rindex(items, item):
    """Find the last copy of Item, else raise IndexError"""

    indexed = list(reversed(items))
    index = indexed.index(item)

    rindex = len(items) - index

    return rindex


def list_strip(items):
    """Drop the leading and trailing Falsey Items"""

    strip = list(items)
    while strip and not strip[0]:
        strip = strip[1:]

    while strip and not strip[-1]:
        strip = strip[:-1]

    return strip

    # todo: coin a name for "\n".join(items).strip().splitlines()


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


def str_ldent(chars):  # kin to 'str.lstrip'
    """Pick out the Spaces etc, at left of some Chars"""

    lstrip = chars.lstrip()
    length = len(chars) - len(lstrip)
    dent = chars[:length] if lstrip else ""

    return dent


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


def str_ripgraf(graf):
    """Pick the lines below the head line of a paragraph, and dedent them"""

    grafdoc = "\n".join(graf)
    if graf and not graf[0].startswith(" "):
        grafdoc = "\n".join(graf[1:])

    dedent = textwrap.dedent(grafdoc)
    strip = dedent.strip()
    graf = strip.splitlines()

    return graf


def str_splitgrafs(doc, keepends=False):  # todo: keepends=True
    """Form List of Lists of Stripped Lines, from Doc of Grafs between Empty Lines"""

    assert not keepends  # 'keepends=True' like for caller to find Sections of Grafs

    grafs = list()  # collects Grafs

    graf = list()  # begins Empty, opens up to collect Lines, then begins again
    for line in doc.splitlines():

        # Add each Empty Line found before the next Same or Less Dented Line

        if not line:
            if graf:

                graf.append(line)

        # Add each More Dented Line

        elif graf and (len(str_ldent(line)) > len(str_ldent(graf[0]))):

            graf.append(line)

        # Strip and close the Open Graf, before starting again with a Less Dented Line

        else:
            strip = list_strip(graf)
            if strip:

                grafs.append(strip)

            # Begin again with an Empty Graf, not yet opened by its First Line

            graf = list()
            graf.append(line)

    # Strip and close the Last Open Graf, if need be

    strip = list_strip(graf)
    if strip:

        grafs.append(strip)

    return grafs  # -> Grid = List[List[Str]]


#
# Add some Def's to Import SubProcess
#


def subprocess_exit_run_if(stdin=subprocess.PIPE):
    """Print and exit, else run the last Graf of ShLines in the Main Doc"""

    doc = __main__.__doc__
    doc_grafs = str_splitgrafs(doc)
    testdoc_graf = str_ripgraf(doc_grafs[-1])

    rindex = list_rindex(testdoc_graf, "")
    graf = testdoc_graf[rindex:]

    for ttyline in graf:
        subprocess_exit_run_if_ttyline(ttyline)  # in effect, shell=True


def subprocess_exit_run_if_shline(shline, stdin=subprocess.PIPE):
    """Print and exit, else run the ShLine and return after it exits zero"""

    sys_exit_if()  # prints examples or help or args and exits, else returns

    sys_stderr_print("+ {}".format(shline))
    argv = shlex.split(shline)
    run = subprocess.run(argv, stdin=stdin)  # in effect, shell=False

    if run.returncode:
        sys_stderr_print("+ exit {}".format(run.returncode))

        sys.exit(run.returncode)

    return run

    # note: Python SubProcess-Run Shell-False does Not demand AbsPath in the ShVerb


def subprocess_exit_run_if_ttyline(ttyline, stdin=subprocess.PIPE):
    """Print and exit, else run the TtyLine in $SHELL and return after it exits zero"""

    sys_exit_if()  # prints examples or help or args and exits, else returns

    env_shell = os.environ["SHELL"]
    shline = "{} -c {!r}".format(env_shell, ttyline)

    sys_stderr_print("+ {}".format(ttyline))
    argv = shlex.split(shline)
    run = subprocess.run(argv, stdin=subprocess.PIPE)  # in effect, shell=True

    if run.returncode:
        sys_stderr_print("+ exit {}".format(run.returncode))

        sys.exit(run.returncode)

    return run


def subprocess_run_oneline(shline):
    """Take 1 Line of Output from SubProcess Run Shell=False Check=True"""

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

    sys_exit_if()  # prints examples or help or args and exits, else returns

    raise NotImplementedError(sys.argv[1:])


def sys_exit_if():
    """Print examples or help or args and exit, else return"""

    sys_exit_if_testdoc()  # prints examples & exits if no args

    sys_exit_if_argdoc()  # prints help lines & exits if "--h" arg, but ignores "-h"

    sys_exit_if_not_implemented()  # raises unhandled exception if arg isn't just:  --


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
