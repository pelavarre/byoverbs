# deffed in many packages  # missing from:  https://pypi.org

"""
usage: import byotools as byo  # define Func's

competently welcome you into Sh Terminal work, batteries included

examples:
  byo.sys_exit_if()  # prints examples or help and exits, else returns args
  byo.subprocess_exit_run_if(shline)  # prints and exits, else calls $SHELL and returns
"""

# code reviewed by people, and by Black and Flake8


import __main__
import argparse
import datetime as dt
import difflib
import os
import pdb
import shlex
import signal
import string
import subprocess
import sys
import textwrap

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace  # needed till Jun/2018 Python 3.7


_ = subprocess.run  # new since Sep/2015 Python 3.5
_ = dt.datetime.now().astimezone()  # new since Dec/2016 Python 3.6
_ = "{:_}".format(12345)  # new since Dec/2016 Python 3.6
# _ = breakpoint  # new since Jun/2018 Python 3.7
# _ = importlib.import_module("dataclasses")  # new since Jun/2018 Python 3.7
# _ = f"{sys.version_info[:3]=}"  # new since Oct/2019 Python 3.8
# _ = shlex.join  # new since Oct/2019 Python 3.8
# _ = str.removesuffix  # new since Oct/2020 Python 3.9
# _  = list(zip([], [], strict=True))  # since Oct/2021 Python 3.10


#
# Add some Def's to Import ArgParse
#


def compile_argdoc(drop_help=None):
    """Form an ArgumentParser from the ArgDoc, without Positional Args and Options"""

    argdoc = __main__.__doc__

    # Compile much of the Arg Doc to Args of 'argparse.ArgumentParser'

    doc_lines = argdoc.strip().splitlines()
    prog = doc_lines[0].split()[1]  # first word of first line

    doc_firstlines = list(_ for _ in doc_lines if _ and (_ == _.lstrip()))
    alt_description = doc_firstlines[1]  # first line of second paragraph

    add_help = not drop_help

    # Say when Doc Lines stand plainly outside of the Epilog

    def skippable(line):
        strip = line.rstrip()

        skip = not strip
        skip = skip or strip.startswith(" ")
        skip = skip or strip.startswith("usage")
        skip = skip or strip.startswith("positional arguments")
        skip = skip or strip.startswith("options")

        return skip

    default = "just do it"
    description = default if skippable(alt_description) else alt_description

    # Pick the Epilog out of the Doc

    epilog = None
    for index, line in enumerate(doc_lines):
        if skippable(line) or (line == description):
            continue

        epilog = "\n".join(doc_lines[index:])

        break

    # Form an ArgumentParser, without Positional Args and Options

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=add_help,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    return parser


def parser_parse_args(parser):
    """Parse the Sh Args, even when no Sh Args coded as the one Sh Arg '--'"""

    sys_exit_if_argdoc_ne(parser)  # prints diff and exits nonzero, when Arg Doc wrong
    sys_exit_if_testdoc()  # prints examples & exits if no args

    sh_args = sys.argv[1:]
    if sh_args == ["--"]:  # helps ArgParse as needed when no Positional Args
        sh_args = ""

    args = parser.parse_args(sh_args)  # prints helps and exits, else returns args

    return args


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

    diffs = list(
        difflib.unified_diff(
            a=got_doc.splitlines(),
            b=want_doc.splitlines(),
            fromfile=got_filename,
            tofile=want_filename,
            lineterm="",  # else the '---' '+++' '@@' Diff Control Lines end with '\n'
        )
    )

    if diffs:
        print("\n".join(diffs))

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
    for index, line in enumerate(main_lines):
        if line and not line.startswith(" "):
            start = index

    doc = "\n".join(main_lines[start:][1:])
    doc = textwrap.dedent(doc).strip()

    # Take the Main Doc as the Test Doc if it doesn't start with Usage, else as Arg Doc

    word = main_lines[0].split()[0]
    if word != "usage:":
        return main_doc

    return doc


def ast_func_to_py(func):
    """Convert to Py Source Chars from Func"""

    funcname = func.__name__
    def_tag = "def {}".format(funcname)

    modulename = func.__module__
    module = sys.modules[modulename]
    pyfile = module.__file__

    with open(pyfile) as reading:
        pyfile_chars = reading.read()

    py = None

    grafs = str_splitgrafs(pyfile_chars)
    for graf in reversed(grafs):
        if graf[0].startswith(def_tag):
            ripgraf = str_ripgraf(graf)
            py = str_joingrafs([ripgraf])

            break

    assert py, (funcname, pyfile)

    return py


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


SHLEX_COLD_CHARS = (
    "%+,-./"
    + string.digits
    + ":=@"
    + string.ascii_uppercase
    + "_"
    + string.ascii_lowercase
)

SHLEX_COLD_CHARS = "".join(sorted(SHLEX_COLD_CHARS))  # already sorted


SHLEX_HOT_CHARS = " !#$&()*;<>?[]^`{|}~" + '"' + "'" + "\\"
SHLEX_HOT_CHARS = "".join(sorted(SHLEX_HOT_CHARS))


SHLEX_QUOTABLE_CHARS = SHLEX_COLD_CHARS + " !#&()*;<>?[]^{|}~"
SHLEX_QUOTABLE_CHARS = "".join(sorted(SHLEX_QUOTABLE_CHARS))  # omits " $ ' \ `


def shlex_parms_dash_h_etc(parms):
    """Return Truthy if '--help' or '--hel' or ... '--h' before '--'"""

    for parm in parms:
        if parm == "--":  # ignores '--help' etc after '--'
            break

        if parm.startswith("--h") and "--help".startswith(parm):
            return True


def shlex_parms_one_posarg():
    """Accept one Arg without "-" Dash Options, preceded by a "--" Sep or not"""

    sh_args = sys.argv[1:]
    if sys.argv[1:][:1] == ["--"]:
        sh_args = sys.argv[2:]

    parm = None
    if len(sh_args) == 1:
        parm = sh_args[-1]
        if parm.startswith("-"):
            parm = None

    return parm


def shlex_quote_if(chars):
    """Resort to ShLex Quote, only when not plainly cold chars"""

    shchars = chars

    hots = sorted(set(chars) - set(SHLEX_COLD_CHARS))
    if hots:
        shchars = shlex.quote(chars)  # missing from Python till Oct/2019 Python 3.8

    return shchars


#
# Add some Def's to Type Str
#


def str_joingrafs(grafs):
    """Form a Doc of Grafs separated by Empty Lines, from a List of Lists of Lines"""

    chars = ""
    for graf in grafs:
        if chars:
            chars += "\n\n"
        chars += "\n".join(graf)

    return chars


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
        subprocess_ttyline_exit_if(ttyline)  # in effect, shell=True


def subprocess_shline_exit_if(shline, stdin=subprocess.PIPE):
    """Print and exit, else run the ShLine and return after it exits zero"""

    sys_exit_if()  # prints examples or help and exits, else returns args

    sys_stderr_print("+ {}".format(shline))
    argv = shlex.split(shline)
    run = subprocess.run(argv, stdin=stdin)  # in effect, shell=False

    if run.returncode:
        sys_stderr_print("+ exit {}".format(run.returncode))

        sys.exit(run.returncode)

    return run

    # note: Python SubProcess-Run Shell-False does Not demand AbsPath in the ShVerb


def subprocess_ttyline_exit_if(ttyline, stdin=subprocess.PIPE):
    """Print and exit, else run the TtyLine in $SHELL and return after it exits zero"""

    sys_exit_if()  # prints examples or help and exits, else returns args

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
    """Print help lines and exit, if -h, --h, --he, --hel, --help"""

    doc = ast_fetch_argdoc()

    sh_args = sys.argv[1:]
    if shlex_parms_dash_h_etc(sh_args):
        print(doc)

        sys.exit()


def sys_exit_if_not_implemented():
    """Exit by raising unhandled NotImplementedError() if given options or args"""

    sh_args = sys.argv[1:]
    if sh_args != ["--"]:
        raise NotImplementedError(sys.argv[1:])


def sys_exit_if_testdoc():
    """Print examples and exit, if no Sh Args"""

    testdoc = ast_fetch_testdoc()

    sh_args = sys.argv[1:]
    if not sh_args:
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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/byotools.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
