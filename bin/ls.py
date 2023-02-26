#!/usr/bin/env python3

"""
usage: ls.py [--help] [-a] [-1 | -C | -m | -l | -lh] [--py] [TOP ...]

show the files and dirs inside a dir

positional arguments:
  TOP     the name of a dir or file to show

options:
  --help  show this help message and exit
  -a      show '.*' hidden files and dirs too
  -1      show as one column of one file or dir per line
  -C      show as multiple columns
  -m      show as comma separated names
  -l      show as many columns of one file or dir per line
  -lh     like -l but round off byte counts to k M G T P E Z Y R Q etc
  --py    show the code without running it

quirks:
  goes well with Cp, MkDir, Ls, Mv, Rm, RmDir, Touch
  classic Ls dumps all the Items, with no Scroll limit, when given no Parms

examples:

  ls.py --  # counts off the '%m%d$(qjd)' Revisions, else the '$(qjd)' Revisions

  ls.py # runs the Code for:  ls -1
  ls.py --py  # shows the Code for:  ls -1
  ls.py -C --py  # shows the Code for Ls C, which is also the code for:  ls

  ls.py --py >.p.py  # name the Code
  python3 .p.py  # run the named Code
  cat -n .p.py |expand  # show the numbered Sourcelines of the named Code

  python3 -c "$(ls.py -1 --py)"  # runs the Code as shown

  find ./* -prune  # like 'ls', but with different corruption of File and Dir Names
  ls -1rt |grep $(date +%m%d$(qjd)) |cat -n |expand
"""

# code reviewed by people, and by Black and Flake8


import argparse
import os
import shlex
import subprocess
import sys
import traceback

import byotools as byo


def main():
    """Run from the Sh Command Line"""

    # Plan to count off the '%m%d$(qjd)' backup copies of Dirs and Files in the Stack

    jqd = byo.subprocess_run_oneline("git config user.initials")
    shjqd = byo.shlex_quote_if(jqd)

    ttyline_0 = "ls -1rt |grep $(date +%m%d{jqd}) |cat -n |expand".format(jqd=shjqd)
    shline_0 = "bash -c {!r}".format(ttyline_0)

    ttyline_1 = "ls -1rt |grep {jqd} |cat -n |expand".format(jqd=shjqd)
    shline_1 = "bash -c {!r}".format(ttyline_1)

    # Maybe choose to do other things

    args = parse_ls_py_args()  # prints help & exits, when need be

    main.args = args

    if any(list(vars(args).values())):
        run_ls_args(args)

        sys.exit()

    # Search up the '%m%d$(qjd)' revisions

    byo.sys_stderr_print("+ {}".format(ttyline_0))
    argv_0 = shlex.split(shline_0)
    run_0 = subprocess.run(
        argv_0,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    os.write(sys.stdout.fileno(), run_0.stdout)
    os.write(sys.stderr.fileno(), run_0.stderr)

    # Else fail over to also search up the '$(qjd)' revisions

    if not run_0.stdout:

        byo.sys_stderr_print("+ {}".format(ttyline_1))
        argv_1 = shlex.split(shline_1)
        _ = subprocess.run(argv_1, stdin=subprocess.PIPE, check=True)


def parse_ls_py_args():
    """Parse the Args of the Sh Command Line"""

    # Collect Help Lines

    top_help = "the name of a dir or file to show"

    help_help = "show this help message and exit"
    a_help = "show '.*' hidden files and dirs too"

    _1_help = "show as one column of one file or dir per line"
    C_help = "show as multiple columns"
    l_help = "show as many columns of one file or dir per line"
    mm = "k M G T P E Z Y R Q"  # Metric Multipliers
    lh_help = "like -l but round off byte counts to " + mm + " etc"
    m_help = "show as comma separated names"

    py_help = "show the code without running it"

    # Form Parser

    parser = byo.compile_argdoc(drop_help=True)

    assert argparse.ZERO_OR_MORE == "*"
    parser.add_argument("tops", metavar="TOP", nargs="*", help=top_help)

    parser.add_argument("--help", action="count", help=help_help)
    parser.add_argument("-a", action="count", help=a_help)

    sub = parser.add_mutually_exclusive_group()
    sub.add_argument("-1", dest="one", action="count", help=_1_help)
    sub.add_argument("-C", action="count", help=C_help)
    sub.add_argument("-m", action="count", help=m_help)
    sub.add_argument("-l", action="count", help=l_help)
    sub.add_argument("-lh", action="count", help=lh_help)

    parser.add_argument("--py", action="count", help=py_help)

    # Run Parser

    args = byo.parser_parse_args(parser)  # prints help & exits, when need be
    if args.help:
        parser.print_help()

        sys.exit(0)

    return args


def run_ls_args(args):
    """Interpret the Parsed Args"""

    # Default to 'ls -1', despite Sh Ls defaulting to 'ls -C'

    explicit_styles = (args.one, args.C, args.l, args.lh, args.m)
    args_one = args.one if any(bool(_) for _ in explicit_styles) else True

    tops = args.tops
    tops_0 = tops[0] if tops else None

    # Pick the Code to show or run

    if args_one:
        opt = "-1"

        if not tops:
            func = ls_here_by_line
            kwargs = dict()
        elif tops[1:]:
            func = ls_tops_by_line
            kwargs = dict(tops=tops)
        else:
            func = ls_file_etc_by_line
            kwargs = dict(item=tops_0)
            if os.path.isdir(tops_0):
                func = ls_dir_by_line
                kwargs = dict(top=tops_0)

    else:

        kwargs = dict(tops=tops)
        if args.C:
            opt = "-C"
            func = ls_by_ljust
        elif args.l:
            opt = "-l"
            func = ls_by_row
        elif args.lh:
            opt = "-lh"
            func = ls_by_row_humane
        elif args.m:
            opt = "-m"
            func = ls_by_comma_space
        else:
            assert False, args  # unreached

    # Form the Code, then show it or run it

    echo_py = echo_ls_func_tops(opt, tops=tops, func=func)
    run_ls_opt_kwargs_func_tops(opt, kwargs=kwargs, func=func, echo_py=echo_py)


def echo_ls_func_tops(opt, tops, func):
    """Echo the Sh Line into a Py Comment, minus '.py' '--py' details"""

    args = main.args

    shtops = []
    if tops:
        for top in tops:
            shtop = byo.shlex_quote_if(top)
            shtops.append(shtop)

    shline = "ls"
    shline += " " + opt
    if args.a:
        shline += "a"
    if shtops:
        shline += " " + " ".join(shtops)

    echo_py = "# {}".format(shline)
    if func is ls_tops_by_line:
        echo_py = '"""{}"""'.format(shline)

    return echo_py


def run_ls_opt_kwargs_func_tops(opt, kwargs, func, echo_py):
    """Form the Code, then show it or run it"""

    # Fetch the Code

    func_py = byo.ast_func_to_py(func)

    # Sculpt the Code

    lines = func_py.splitlines()

    forward_kwargs_etc(lines, kwargs=kwargs)
    apply_dash_a(lines)
    infer_boilerplates(lines, func=func, echo_py=echo_py)

    lines[::] = list(_ for _ in lines if _ is not None)  # deletes dropped Sourcelines

    # Show the Code or run it

    py = "\n".join(lines)

    run_ls_py(py)


def forward_kwargs_etc(lines, kwargs):
    """Forward the KwArgs, after dropping the Func's DocString"""

    assert lines[0].startswith('"""')
    lines[0] = None

    for (k, v) in reversed(kwargs.items()):
        kv_py = "{} = {!r}".format(k, v)
        lines[1:1] = [kv_py]


def apply_dash_a(lines):
    """Correct the Code to run for Ls with or without '-a'"""

    args = main.args

    _4_DENT = 4 * " "

    # Drop the Os CurDir and ParDir from what Os ListDir finds, when not:  ls -a

    lines[::] = list(_ for _ in lines if _ is not None)  # deletes dropped Sourcelines

    if not args.a:

        chars = "\n".join(lines)
        chars = chars.replace('[".", ".."] + ', "")
        lines[::] = chars.splitlines()

    # Stop caring if Item Starts With Dot, when yes:  ls -a

    if args.a:

        for (i, line) in enumerate(lines):
            if line.strip() == 'if not item.startswith("."):':

                lines[i] = None

                assert lines[i + 1].startswith(_4_DENT), repr(lines[i + 1])
                lines[i + 1] = lines[i + 1][len(_4_DENT) :]

                if lines[i + 2 :]:
                    assert not lines[i + 2].startswith(_4_DENT), repr(lines[i + 2])


def infer_boilerplates(lines, func, echo_py):
    """Choose Hash Bang, DocString, Imports, and sometimes drop all the Blank Lines"""

    # Pull in the Imports apparently mentioned, 3rd of all

    lines[::] = list(_ for _ in lines if _ is not None)  # deletes dropped Sourcelines

    chars = "\n".join(lines)
    if "os." in chars:
        lines[0:0] = ["import os", "", ""]

    # Insert the DocString to Echo Bash, 2nd of all

    lines[0:0] = ["", echo_py, ""]

    # Mark these Sourcelines as Py Sourcelines, 1st of all

    if func is ls_tops_by_line:

        lines[0:0] = ["#!/usr/bin/env python3"]

    # Drop the blank Sourcelines when not structuring many Sourcelines

    if func is not ls_tops_by_line:

        for (i, line) in enumerate(lines):
            if not line:
                lines[i] = None


def run_ls_py(py):
    """Show the Code or run it"""

    args = main.args

    if args.py:
        print(py)
    else:
        try:
            exec(py)
        except Exception as exc:
            traceback.print_exception(exc, limit=0)

            sys.exit(1)


#
# Just find and print
#


def ls_here_by_line():
    """Show the Item Names of the Os GetCwd, one per Line"""

    for item in sorted([".", ".."] + os.listdir()):
        if not item.startswith("."):
            print(item)


def ls_file_etc_by_line(item):
    """Show the Item Name of one File, as one Line"""

    _ = os.stat(item)
    print(item)


def ls_dir_by_line(top):
    """Show the the Item Names of one Dir, one per Line"""

    for item in sorted([".", ".."] + os.listdir(top)):
        if not item.startswith("."):
            print(item)


def ls_tops_by_line(tops):
    """Show the Item Names of two or more Files or Dirs,  at one per Line"""

    sep = None

    topdirs = list()
    for top in sorted(tops):
        if os.path.isdir(top):
            topdirs.append(top)
        else:
            print(top)
            sep = "\n"

    for topdir in topdirs:
        if sep:
            print()
        print(topdir + ":")
        sep = "\n"

        for item in sorted([".", ".."] + os.listdir(topdir)):
            if not item.startswith("."):
                print(item)


def ls_by_row(tops):
    """Show the Items in detail, one per Line"""

    raise NotImplementedError("def ls_by_row")


def ls_by_row_humane(tops):
    """Show the Items in detail, one per Line, but round off the Byte Counts"""

    raise NotImplementedError("def ls_by_row_humane")


#
# Find and print, but also pack in more Names per Terminal Row
#


def ls_by_ljust(top):
    """Show the Item Names, a few per Line"""

    raise NotImplementedError("def ls_by_ljust")


def ls_by_comma_space(top):
    """Show the Item Names, separated by ', ' or ', \n' Comma Space Line-Break"""

    raise NotImplementedError("def ls_by_comma_space")


#
# Remember some Tests
#


PY_AUTHOR_TESTS = """

    bind 'set enable-bracketed-paste off' 2>/dev/null; unset zle_bracketed_paste

    ls.py -1a
    ls.py -1a --py
    ls.py -1 --py
    ls
    ls.py -C --py

    ls.py --py

    ls.py --py >.p.py
    python3 .p.py
    cat -n .p.py |expand

    ls -1
    ls.py -1
    ls.py -1 --py

    ls -1 Makefile
    ls.py Makefile
    ls.py Makefile --py

    touch .p.py
    ls -1 .p.py
    ls.py .p.py

    ls /dev/null/supercali  &&: exits 1 because 'Not a directory'
    echo + exit $?
    ls.py -1 /dev/null/supercali  &&: exits 1 because NotADirectoryError
    echo + exit $?
    ls.py -1 /dev/null/supercali --py

    ls -1 demos/
    ls.py -1 demos/
    ls.py -1 demos/ --py

    ls -1 demos/ futures.md Makefile
    ls.py -1 demos/ futures.md Makefile
    ls.py -1 demos/ futures.md Makefile --py

    ls -1a
    ls.py -1a
    ls.py -1a --py

    python3 -c "$(ls.py -1 --py)"

"""


#
# Run from the Sh Command Line now, unless imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/ls.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
