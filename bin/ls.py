#!/usr/bin/env python3

"""
usage: ls.py [--help] [-1 | -C | -m | -l | -lh] [--py] [TOP ...]

show the files and dirs inside a dir

positional arguments:
  TOP     the name of a dir or file to show

options:
  --help  show this help message and exit
  -1      show as one column of one file or dir per line
  -C      show as multiple columns
  -m      show as comma separated names
  -l      show as many columns of one file or dir per line
  -lh     like -l but round off byte counts to k M G T P E Z Y R Q etc
  --py    show the code without running it

quirks:
  goes well with Cp, MkDir, Ls, Mv, Rm, RmDir, Touch
  classic Ls dumps all the Items, with no Scroll limit, when given no Parms

examples of write the Python for you:

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
  ls.py -1 /dev/null/supercali  &&: exits 1 because NotADirectoryError
  ls.py -1 /dev/null/supercali --py

  ls -1 demos/
  ls.py -1 demos/
  ls.py -1 demos/ --py

  ls -1 demos/ futures.md
  ls.py -1 demos/ futures.md
  ls.py -1 demos/ futures.md --py

  python3 -c "$(ls.py --py)"

examples:

  ls.py --  # count off the '%m%d$(qjd)' revisions, else the '$(qjd)' revisions
  ls.py --py  # show the code for:  ls -1
  ls.py -C --py  # show the code for:  ls

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

    sub = parser.add_mutually_exclusive_group()
    sub.add_argument("-1", dest="one", action="count", help=_1_help)
    sub.add_argument("-C", action="count", help=C_help)
    sub.add_argument("-m", action="count", help=m_help)
    sub.add_argument("-l", action="count", help=l_help)
    sub.add_argument("-lh", action="count", help=lh_help)

    parser.add_argument("--py", action="count", help=py_help)

    # Run Parser

    args = byo.parser_parse_args(parser)  # prints help & exits, when need be

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

    run_ls_opt_kwargs_func_tops(
        opt, kwargs=kwargs, func=func, tops=tops, args_py=args.py
    )


def run_ls_opt_kwargs_func_tops(opt, kwargs, func, tops, args_py):
    """Form the Code, then show it or run it"""

    # Echo the Sh Line into a Py Comment, minus '.py' '--py' details

    shtops = []
    if tops:
        for top in tops:
            shtop = byo.shlex_quote_if(top)
            shtops.append(shtop)

    shline = "ls {} {}".format(opt, " ".join(shtops)).rstrip()
    comment_py = "# {}".format(shline)

    # Fetch the Code

    func_py = byo.ast_func_to_py(func)

    # Put the Sh Line Comment in place of the Func's DocString

    lines = func_py.splitlines()
    assert lines[0].startswith('"""')
    lines[0] = comment_py

    # Forward the KwArgs

    for (k, v) in reversed(kwargs.items()):
        kv_py = "{} = {!r}".format(k, v)
        lines[1:1] = [kv_py]

    # Pull in the Imports mentioned

    if "os." in func_py:
        lines[1:1] = ["import os"]

    # Drop the blank lines  # deviates from Black Python Style, for tiny Programs

    lines = list(_ for _ in lines if _)

    # Show it or run it

    py = "\n".join(lines)

    if args_py:
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

    for item in sorted(os.listdir()):  # calmly empty when no Dir
        if not item.startswith("."):
            print(item)


def ls_file_etc_by_line(item):
    """Show the Item Name of one File, as one Line"""

    _ = os.stat(item)  # raises Exception if no File
    print(item)  # no matter if item.startswith(".")


def ls_dir_by_line(top):
    """Show the the Item Names of one Dir, one per Line"""

    for item in sorted(os.listdir(top)):  # raises Exception if File or if no Dir
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

    for (index, topdir) in enumerate(topdirs):
        if sep:
            print()
        print(topdir + ":")
        sep = "\n"

        for item in sorted(os.listdir(topdir)):
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
# Run from the Sh Command Line now, unless imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/ls.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
