# deffed in many packages  # missing from:  https://pypi.org

"""
usage: import byotools as byo  # define Func's

competently welcome you into Sh Terminal work, batteries included

examples:
  byo.sys_exit_if()  # prints examples or help and exits, else returns args
  byo.subprocess_exit_run_if(shline)  # prints and exits, else calls $SHELL and returns
"""

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import dataclasses
import datetime as dt
import difflib
import os
import re
import shlex
import signal
import string
import subprocess
import sys
import textwrap


assert sys.version_info[:2] >= (3, 9), (sys.version_info,)


... == subprocess.run  # new since Sep/2015 Python 3.5

... == dt.datetime.now().astimezone()  # new since Dec/2016 Python 3.6  # Ubuntu 2018
... == "{:_}".format(12345)  # new since Dec/2016 Python 3.6
... == (re.search(r"..", "abcde") or [""])[0]  # new since Dec/2016 Python 3.6

... == breakpoint  # new BuiltIn since Jun/2018 Python 3.7
... == dataclasses  # new Import since Jun/2018 Python 3.7

... == f"{sys.version_info[:3]=}"  # new Syntax since Oct/2019 Python 3.8  # Ubuntu 2020
... == shlex.join  # new since Oct/2019 Python 3.8

... == str.removeprefix, str.removesuffix  # new since Oct/2020 Python 3.9
... == dict[str, int]  # new Syntax since Oct/2020 Python 3.9

# ... == int.bit_count  # new since Oct/2021 Python 3.10  # Ubuntu 2022
# ... == list(zip([], [], strict=True))  # new since Oct/2021 Python 3.10  # Ubuntu 2022

# ... == tomllib  # new since Oct/2022 Python 3.11
# ... == termios.tcgetwinsize(sys.stderr.fileno())  # new since Oct/2022 Python 3.11
# ... == typing.Self  # new since Oct/2022 Python 3.11


#
# Add some Def's to Import ArgParse
#


class ArgumentParser(argparse.ArgumentParser):
    """Amp up Class ArgumentParser of Import ArgParse"""

    def __init__(self, add_help=True) -> None:
        argdoc = __main__.__doc__

        # Compile much of the Arg Doc to Args of 'argparse.ArgumentParser'

        doc_lines = argdoc.strip().splitlines()
        prog = doc_lines[0].split()[1]  # first word of first line

        doc_firstlines = list(_ for _ in doc_lines if _ and (_ == _.lstrip()))
        alt_description = doc_firstlines[1]  # first line of second paragraph

        # Say when Doc Lines stand plainly outside of the Epilog

        def skippable(line) -> bool:
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

        super().__init__(
            prog=prog,
            description=description,
            add_help=add_help,
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=epilog,
        )

        # 'add_help=False' for 'cal -h', 'df -h', 'ls -h', etc

    #
    # def parse_args(self, args=None) -> argparse.Namespace:
    #     argspace = super().parse_args(args)
    #     return argspace
    #
    # yea no, MyPy would then explode with a deeply inscrutable
    #
    #   Signature of "parse_args" incompatible with supertype "ArgumentParser"
    #   [override]
    #

    def parse_args_else(self, args=None) -> argparse.Namespace:
        """Parse the Sh Args, even when no Sh Args coded as the one Sh Arg '--'"""

        # Accept the "--" Sh Args Separator when present with or without Positional Args

        sh_args = sys.argv[1:] if (args is None) else args
        if sh_args == ["--"]:  # ArgParse chokes if Sep present without Pos Args
            sh_args = ""

        # Print Diffs & exit nonzero, when Arg Doc wrong

        diffs = self.diff_doc_vs_format_help()
        if diffs:
            print("\n".join(diffs))

            sys.exit(2)

        # Print examples & exit zero, if no Sh Args

        testdoc = self.scrape_testdoc_from_epilog()
        if not sys.argv[1:]:
            print()
            print(testdoc)
            print()

            sys.exit(0)

        # Print help lines & exit zero, else return Parsed Args

        argspace = self.parse_args(sh_args)

        return argspace

        # often prints help & exits

    def diff_doc_vs_format_help(self) -> list[str]:
        """Form Diffs from Main Arg Doc to Parser Format_Help"""

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
            parser_doc = self.format_help()

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

        return diffs

    def scrape_testdoc_from_epilog(self) -> str:
        """Pick out the last Heading of the Epilog of an Arg Doc, and drop its Title"""

        epilog = "" if (self.epilog is None) else self.epilog

        lines = epilog.splitlines()

        indices = list(_ for _ in range(len(lines)) if lines[_])  # no empties
        indices = list(_ for _ in indices if not lines[_].startswith(" "))  # headings

        testdoc = "\n".join(lines[indices[-1] + 1 :])  # last heading, minus its title
        testdoc = textwrap.dedent(testdoc)
        testdoc = testdoc.strip()

        return testdoc


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


def ast_fetch_argdoc() -> str:
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


def ast_fetch_testdoc() -> str:
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


def ast_func_to_py(func) -> str:
    """Convert to Py Source Chars from Func"""

    funcname = func.__name__
    def_tag = "def {}(".format(funcname)

    modulename = func.__module__
    module = sys.modules[modulename]
    pyfile = module.__file__

    assert pyfile, (module, module.__file__)  # keeps MyPy happy, but maybe never fails
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

    # finds wrong Func or no Func when source isn't Black'ened, such as:  def func ():

    # to do: AttributeError at func=sys.exit, etc
    # to do: TypeError at each Func in dir(google), if those existed


#
# Add some Def's to Type List
#


def list_rindex(items, item) -> int:
    """Find the last copy of Item, else raise IndexError"""

    indexed = list(reversed(items))
    index = indexed.index(item)

    rindex = len(items) - index

    return rindex


def list_strip(items) -> list:
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


def shlex_parms_dash_h_etc(shargs, opts=["-h", "--help"]) -> bool | None:
    """Return Truthy if '--help' or '--hel' or ... '--h' before '--'"""

    for opt in opts:
        single = opt.startswith("-") and not opt.startswith("--")
        double = opt.startswith("--") and not opt.startswith("---")
        assert single or double, repr(opt)

    for sharg in shargs:
        if sharg == "--":  # ignores '--help' etc after '--'
            break

        for opt in opts:
            double = opt.startswith("--") and not opt.startswith("---")
            if sharg == opt:
                return True
            if double and sharg[len("--") :]:
                if opt.startswith(sharg):
                    return True

    return None


def shlex_parms_one_posarg() -> str | None:
    """Accept one Arg without "-" Dash Options, preceded by a "--" Sep or not"""

    shargs = sys.argv[1:]
    if sys.argv[1:][:1] == ["--"]:
        shargs = sys.argv[2:]

    parm = None
    if len(shargs) == 1:
        parm = shargs[-1]
        if parm.startswith("-"):
            parm = None

    return parm


def shlex_quote_if(chars) -> str:
    """Resort to ShLex Quote, only when not plainly cold chars"""

    shchars = chars

    hots = sorted(set(chars) - set(SHLEX_COLD_CHARS))
    if hots:
        shchars = shlex.quote(chars)  # missing from Python till Oct/2019 Python 3.8

    return shchars

    # todo: solve shlex_quote_if(chars="don't")


#
# Add some Def's to Type Str
#


def str_joingrafs(grafs) -> str:
    """Form a Doc of Grafs separated by Empty Lines, from a List of Lists of Lines"""

    chars = ""
    for graf in grafs:
        if chars:
            chars += "\n\n"
        chars += "\n".join(graf)

    return chars


def str_ldent(chars) -> str:
    """Pick out the Spaces etc, at left of some Chars"""

    lstrip = chars.lstrip()
    length = len(chars) - len(lstrip)
    dent = chars[:length] if lstrip else ""

    return dent

    # kin to 'str.lstrip'


def str_removeprefix(chars, prefix) -> str:
    """Remove Prefix from Chars if present, till Oct/2020 Python 3.9 str.removeprefix"""

    result = chars
    if prefix and chars.startswith(prefix):
        result = chars[len(prefix) :]

    return result


def str_removesuffix(chars, suffix) -> str:
    """Remove Suffix from Chars if present, till Oct/2020 Python 3.9 str.removesuffix"""

    result = chars
    if suffix and chars.endswith(suffix):
        result = chars[: -len(suffix)]

    return result


def str_ripgraf(graf) -> list[str]:
    """Pick the lines below the head line of a paragraph, and dedent them"""

    grafdoc = "\n".join(graf)
    if graf and not graf[0].startswith(" "):
        grafdoc = "\n".join(graf[1:])

    dedent = textwrap.dedent(grafdoc)
    strip = dedent.strip()
    graf = strip.splitlines()

    return graf


def str_splitgrafs(doc) -> list[list[str]]:
    """Form List of Lists of Stripped Lines, from Doc of Grafs between Empty Lines"""

    grafs = list()  # collects Grafs

    graf: list[str]
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

    # todo: keepends=True


#
# Add some Def's to Import SubProcess
#


def subprocess_exit_run_if(stdin=subprocess.PIPE) -> None:
    """Print and exit, else run the last Graf of ShLines in the Main Doc"""

    doc = __main__.__doc__
    doc_grafs = str_splitgrafs(doc)
    testdoc_graf = str_ripgraf(doc_grafs[-1])

    rindex = list_rindex(testdoc_graf, "")
    graf = testdoc_graf[rindex:]

    for ttyline in graf:
        subprocess_ttyline_exit_if(ttyline)  # in effect, shell=True


def subprocess_shline_exit_if(  # ) -> subprocess.CompletedProcess:
    shline, stdin=subprocess.PIPE
) -> subprocess.CompletedProcess:
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


def subprocess_ttyline_exit_if(  # ) -> subprocess.CompletedProcess:
    ttyline, stdin=subprocess.PIPE
) -> subprocess.CompletedProcess:
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


def subprocess_run_oneline(shline) -> str:
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

    stdout = run.stdout.decode()  # not errors="surrogateescape"
    lines = stdout.splitlines()

    assert len(lines) == 1, repr(lines[:3])

    line = lines[-1]

    return line


def subprocess_run_stdout_bytes(shline) -> bytes:
    """Take Output from SubProcess Run Shell=False Check=True"""

    argv = shlex.split(shline)

    run = subprocess.run(
        argv,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    stdout = run.stdout
    assert not run.stderr, run.stderr

    return stdout


def subprocess_run_stdout_surrogateescape(shline) -> str:
    """Take Output from SubProcess Run Shell=False Check=True"""

    argv = shlex.split(shline)

    run = subprocess.run(
        argv,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        errors="surrogateescape",
        check=True,
    )

    stdout_chars = run.stdout
    assert not run.stderr, run.stderr

    return stdout_chars


#
# Add some Def's to Import Sys
#


def sys_exit() -> None:
    """Prints examples or help lines or exception, and exits"""

    sys_exit_if()  # prints examples or help or args and exits, else returns

    raise NotImplementedError(sys.argv[1:])


def sys_exit_if() -> None:
    """Print examples or help or args and exit, else return"""

    sys_exit_if_testdoc()  # prints examples & exits if no args

    sys_exit_if_helpdoc()  # prints help & exits zero for:  -h, --help

    sys_exit_if_not_implemented()  # raises unhandled exception if arg isn't just:  --


def sys_exit_if_helpdoc(opts=["-h", "--help"]) -> None:
    """Print help lines and exit, if -h, --h, --he, --hel, --help"""

    doc = ast_fetch_argdoc()

    shargs = sys.argv[1:]
    if shlex_parms_dash_h_etc(shargs, opts=opts):
        print(doc)

        sys.exit()

    # byo.sys_exit_if_helpdoc()  # prints help & exits zero for:  -h, --help
    # byo.sys_exit_if_helpdoc(["--help"])  # ignores "-h", but prints & exits for "--h"


def sys_exit_if_argdoc_ne(parser) -> None:
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

    pattern = r"\[([^ ]*) \[([^ ])* [.][.][.]\]\]\n"  # matches '[WORD [WORD ...]]' etc
    m = re.search(pattern, string=parser_doc)
    if m:
        assert m.group(1) != m.group(2), m.groups()
        repl = "[{} ...]\n".format(m.group(1))  # replaces with '[WORD ...]\n', etc
        parser_doc = re.sub(pattern, repl=repl, string=parser_doc, count=1)

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


def sys_exit_if_not_implemented() -> None:
    """Exit by raising unhandled NotImplementedError() if given options or args"""

    shargs = sys.argv[1:]
    if shargs != ["--"]:
        raise NotImplementedError(sys.argv[1:])


def sys_exit_if_testdoc() -> None:
    """Print examples and exit, if no Sh Args"""

    testdoc = ast_fetch_testdoc()

    shargs = sys.argv[1:]
    if not shargs:
        print()
        print(testdoc)
        print()

        sys.exit()


def sys_stdin_prompt_if() -> None:
    """Prompt for TTY EOF before blocking to read more of it"""

    CONTROL_KEYCAP = "\N{Up Arrowhead}"  # ⌃
    if sys.stdin.isatty():
        sys_stderr_print("Press {}D TTY EOF to quit".format(CONTROL_KEYCAP))


def sys_stdin_readline_else() -> str:
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


def sys_stderr_print(*args, **kwargs) -> None:
    """Work like Print, but write Sys Stderr in place of Sys Stdout"""

    kwargs_ = dict(kwargs)
    if "file" not in kwargs.keys():
        kwargs_["file"] = sys.stderr

    sys.stdout.flush()

    print(*args, **kwargs_)

    if "file" not in kwargs.keys():
        sys.stderr.flush()


#
# Add some Def's to Import TextWrap
#


def textwrap_dicts_tabled(dicts, sep=" | ", divider="-+-") -> str:
    """Format [Dict] as centered Column Keys, then Rows of justified Cells"""

    if not dicts:
        return ""

    labels = list(" {} ".format(_) for _ in dicts[-1].keys())
    lists = [labels] + list(list(_.values()) for _ in dicts)

    chars = textwrap_lists_tabled(lists, sep=sep, divider=divider)

    return chars


def textwrap_frame(chars) -> str:
    """Add top/ bottom/ left/ right margins"""

    dent = 4 * " "

    lines = list()

    lines.append("")  # opens twice
    lines.append("")

    for alt_line in chars.splitlines():
        line = dent + alt_line
        line = line.rstrip()

        lines.append(line)

    lines.append("")  # closes twice
    lines.append("")

    alt_chars = "\n".join(lines)

    return alt_chars


def textwrap_lists_tabled(lists, sep="  ", divider=None) -> str:
    """Format List of List of Cells as centered or justified Str's in Columns"""

    # Count out the Width of each Column

    rows = lists
    widths_rows = list(list(len(str(cell).strip()) for cell in row) for row in rows)
    widths = list(max(_) for _ in zip(*widths_rows))

    div_widths = list(widths)
    div_widths[0] += 1  # adds Left Margin in the Dividing Row
    div_widths[-1] += 1  # adds Right Margin in the Dividing Row

    # Form each Row

    lines = list()
    for i, row in enumerate(rows):
        justs = list()
        for cell, width in zip(row, widths):
            strip = str(cell).strip()

            if not isinstance(cell, str):  # as if starts with & doesn't end with Space
                just = strip.rjust(width)
            elif not cell.startswith(" "):  # maybe ends with Space, maybe doesn't
                just = strip.ljust(width)
            elif not cell.endswith(" "):  # starts with Space & doesn't end with Space
                just = strip.rjust(width)
            else:  # starts with & ends with Space
                just = strip.center(width)

            justs.append(just)

        line = sep.join(justs)
        if divider:
            line = " " + line  # adds Left Margin to all Rows tabled with a Dividing Row
        line = line.rstrip()  # makes the Right Margin implicit, not explicit
        lines.append(line)

        # Insert a Dividing Row between Column Labels and Column Cells

        if divider:
            if i == 0:
                dividing_line = divider.join((_ * divider[-1:]) for _ in div_widths)
                lines.append(dividing_line)

    # Succeed

    join = "\n".join(lines)

    return join


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/byotools.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
