#!/usr/bin/env python3

"""
usage: ls.py [--help] [-a] [-d] [-1 | -C | -m | -l | -lh | --full-time] [--py]
             [TOP ...]

show the files and dirs inside of dirs

positional arguments:
  TOP          the name of a dir or file to show

options:
  --help       show this help message and exit
  -a           show '.*' hidden files and dirs too
  -d           show the top dirs as items of a higher dir, not their insides
  -1           show as one column of file or dir names (default for Stdout Pipe)
  -C           show as columns of names (default for Stdout Tty)
  -m           show as lines of comma separated names
  -l           show as many columns of one file or dir per line
  -lh          like -l but round off byte (B) counts to k M G T P E Z Y R Q etc
  --full-time  like -l but detail date/time as "%Y-%m-%d %H:%M:%S.%f %z"
  --py         show the code without running it

quirks:
  goes well with Cp, MkDir, Ls, Mv, Rm, RmDir, Touch
  toggles between Decimal and Binary SI Units at '-lh', at '-lh -lh', etc
  doesn't tweak the numbers to speak the alt Binary SI Units of Mac/ Linux '-lh'
  doesn't guess you want '-a' when you say '--full-time', although Linux Ls does
  classic Ls dumps all the Items, with no Scroll limit, when given no ShArgs

docs:
  https://physics.nist.gov/cuu/Units/binary.html

examples:

  ls.py --  # ls -alF -rt
  ls.py /tmp  # ls -alF -rt /tmp
  ls.py /tmp/*  # ls -adlF -rt /tmp/*

  ls.py |cat -  # runs the Code for:  ls -1
  ls.py --py |cat -  # shows the Code for:  ls -1
  ls.py -C --py  # shows the Code for Ls C, which is the Code for:  ls

  ls.py -1 --py >p.py  # name the Code
  python3 p.py  # run the named Code
  cat p.py |cat -n |expand  # show the numbered Sourcelines of the named Code

  python3 -c "$(ls.py -1 --py)"  # runs the Code as shown

  find ./* -prune  # like 'ls', but with different corruption of File and Dir Names
  ls -1rt |tail -1  # the File or Dir most recently touched, if any
"""

# code reviewed by people, and by Black and Flake8


import argparse
import datetime as dt
import os
import shlex
import stat
import subprocess
import sys
import traceback

import byotools as byo


def main():
    """Run from the Sh Command Line"""

    args = parse_ls_py_args()  # prints help & exits zero for:  -h, --help
    main.args = args

    # Compile Sh Args to Python and run it, if any Dash or Dash-Dash Options in Sh Args

    options = dict(vars(args))
    del options["tops"]

    if any(options.values()):
        run_ls_args(args)

        sys.exit()

    # Else run our default ShLine

    shargv = shlex.split("ls -alF -rt") + args.tops
    if args.tops[1:]:
        shargv = shlex.split("ls -adlF -rt") + args.tops

    shline = " ".join(byo.shlex_quote_if(_) for _ in shargv)  # todo: unglob '*' etc

    byo.sys_stderr_print("+ {}".format(shline))

    run = subprocess.run(
        shargv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    os.write(sys.stdout.fileno(), run.stdout)
    os.write(sys.stderr.fileno(), run.stderr)  # deferred past all Stdout

    sys.exit(run.returncode)


def parse_ls_py_args():
    """Parse the Args of the Sh Command Line"""

    # Collect Help Lines

    help_top = "the name of a dir or file to show"

    help_help = "show this help message and exit"
    help_a = "show '.*' hidden files and dirs too"
    help_d = "show the top dirs as items of a higher dir, not their insides"

    help_one = "show as one column of file or dir names (default for Stdout Pipe)"
    help_cee = "show as columns of names (default for Stdout Tty)"
    help_ell = "show as many columns of one file or dir per line"

    help_lh = "like -l but round off byte (B) counts to k M G T P E Z Y R Q etc"
    help_m = "show as lines of comma separated names"

    help_full_time = 'like -l but detail date/time as "%%Y-%%m-%%d %%H:%%M:%%S.%%f %%z"'
    help_py = "show the code without running it"

    # Form Parser

    parser = byo.compile_argdoc(drop_help=True)

    assert argparse.ZERO_OR_MORE == "*"
    parser.add_argument("tops", metavar="TOP", nargs="*", help=help_top)

    parser.add_argument("--help", action="count", help=help_help)  # not at "-h"
    parser.add_argument("-a", action="count", help=help_a)
    parser.add_argument("-d", action="count", help=help_d)

    sub = parser.add_mutually_exclusive_group()
    sub.add_argument("-1", dest="alt_one", action="count", help=help_one)
    sub.add_argument("-C", dest="alt_cee", action="count", help=help_cee)
    sub.add_argument("-m", action="count", help=help_m)
    sub.add_argument("-l", dest="alt_ell", action="count", help=help_ell)
    sub.add_argument("-lh", action="count", help=help_lh)
    sub.add_argument("--full-time", action="count", help=help_full_time)

    parser.add_argument("--py", action="count", help=help_py)

    # Run Parser

    args = byo.parser_parse_args(parser)  # prints help & exits, when need be
    if args.help:
        parser.print_help()

        sys.exit(0)

    # Gather context for choosing a default Style

    styles = [args.alt_one, args.alt_cee, args.alt_ell, args.lh, args.m, args.full_time]
    styles = list(bool(_) for _ in styles)

    sum_styles = sum(styles)
    assert sum_styles <= 1, (sum_styles, styles)  # because 'mutually_exclusive_group'

    stdout_isatty = sys.stdout.isatty()

    # Succeed

    args.one = args.alt_one or ((not sum_styles) and (not stdout_isatty))
    args.cee = args.alt_cee or ((not sum_styles) and stdout_isatty)
    args.ell = args.alt_ell or args.full_time or args.lh

    return args


def run_ls_args(args):
    """Interpret the Parsed Args"""

    # Default to 'ls -1', despite Sh Ls defaulting to 'ls -C'

    tops = args.tops

    explicit_styles = (args.one, args.cee, args.ell, args.lh, args.m)
    args_one = args.one if any(bool(_) for _ in explicit_styles) else True

    # Pick the Code to show or run

    if args_one:
        (opt, func, kwargs) = parse_ls_one_args(args)
    elif args.ell:
        (opt, func, kwargs) = parse_ls_ell_args(args)
    elif args.cee:
        opt = "-C"  # show as columns of names
        func = ls_by_ljust
        kwargs = dict(tops=tops)
    elif args.m:
        opt = "-m"  # show as lines of comma separated names
        func = ls_by_comma_space
        kwargs = dict(tops=tops)
    else:
        assert False, args  # unreached

    # Form the Code, then show it or run it

    title_py = opt_form_title_py(opt, tops=tops, func=func)
    opt_show_or_exec_py(opt, kwargs=kwargs, func=func, title_py=title_py)


def parse_ls_one_args(args):
    """Pick out the '-1' Option, its 1 Func, and its KwArgs"""

    opt = "-1"  # show as one column of file or dir names

    tops = args.tops
    top_else = tops[0] if tops else None

    stat_by_top = fetch_os_stat_by_top(tops)  # always called, sometimes needed

    isdirs = list(
        (stat.S_ISDIR(s.st_mode) and not stat.S_ISLNK(s.st_mode))
        for s in stat_by_top.values()
    )

    if not tops:  # if no Tops
        func = ls_here_by_name
        kwargs = dict()

    elif not tops[1:]:  # if one Top
        if all(isdirs):
            func = ls_dir_by_name
            kwargs = dict(top=top_else)
        else:
            func = ls_file_by_name
            kwargs = dict(file_=top_else)

    else:  # else many Tops
        if all(isdirs):
            func = ls_top_dirs_by_name
            kwargs = dict(tops=tops)
        elif not any(isdirs):
            func = ls_files_by_name
            kwargs = dict(files=tops)
        else:
            func = ls_tops_by_name
            kwargs = dict(tops=tops)

    return (opt, func, kwargs)


def parse_ls_ell_args(args):
    """Pick out the '-l' or '-lh' or '--full-time' Option, its 1 Func, and its KwArgs"""

    assert args.ell, args
    if args.full_time:
        opt = "--full-time"  # like -l but detail date/time as "%Y-%m-%d %H:%M:%S.%f %z"
    elif args.lh:
        opt = "-lh"  # like -l but round off byte counts to k M G T P E Z Y R Q etc
    else:
        opt = "-1"  # show as many columns of one file or dir per line

    tops = args.tops
    top_else = tops[0] if tops else None

    stat_by_top = fetch_os_stat_by_top(tops)  # always called, sometimes needed

    isdirs = list(
        (stat.S_ISDIR(s.st_mode) and not stat.S_ISLNK(s.st_mode))
        for s in stat_by_top.values()
    )

    if not tops:  # if no Tops
        func = ls_here_by_stat
        kwargs = dict()

    elif not tops[1:]:  # if one Top
        if all(isdirs):
            func = ls_dir_by_stat
            kwargs = dict(top=top_else)
        else:
            func = ls_file_by_stat
            kwargs = dict(file_=top_else)

    else:  # else many Tops
        if all(isdirs):
            func = ls_top_dirs_by_stat
            kwargs = dict(tops=tops)
        elif not any(isdirs):
            func = ls_files_by_stat
            kwargs = dict(files=tops)
        else:
            func = ls_tops_by_stat
            kwargs = dict(tops=tops)

    return (opt, func, kwargs)

    # todo: merge 'parse_ls_ell_args' with 'parse_ls_one_args'


def fetch_os_stat_by_top(tops):
    """Call Os Stat for each Top"""

    alt_tops = tops if tops else [os.curdir]

    stat_by_top = dict()
    for top in alt_tops:
        if top not in stat_by_top.keys():
            stat_ = os.lstat(top)
            stat_by_top[top] = stat_

    return stat_by_top


def opt_form_title_py(opt, tops, func):
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

    title_py = "# {}".format(shline)
    if func in (ls_tops_by_name, ls_tops_by_stat):
        title_py = '"""{}"""'.format(shline)

    return title_py


def opt_show_or_exec_py(opt, kwargs, func, title_py):
    """Form the Code, then show it or run it"""

    # Fetch the Code

    func_py = byo.ast_func_to_py(func)

    # Sculpt the Code

    lines = func_py.splitlines()

    lines_forward_kwargs_etc(lines, kwargs=kwargs)
    lines_apply_dash_a(lines)
    lines_infer_boilerplates(lines, func=func, title_py=title_py)

    lines[::] = list(_ for _ in lines if _ is not None)  # deletes dropped Sourcelines

    # Show the Code or run it

    py = "\n".join(lines)

    py_exec_or_show(py)


def lines_forward_kwargs_etc(lines, kwargs):
    """Forward the KwArgs, after dropping the Func's DocString"""

    assert lines[0].startswith('"""')
    lines[0] = None

    for k, v in reversed(kwargs.items()):
        kv_py = "{} = {!r}".format(k, v)
        lines[1:1] = [kv_py]


def lines_apply_dash_a(lines):
    """Correct the Code to run for Ls with or without '-a'"""

    args = main.args

    DENT_4 = 4 * " "

    # Drop the Os CurDir and ParDir from what Os ListDir finds, when not:  ls -a

    lines[::] = list(_ for _ in lines if _ is not None)  # deletes dropped Sourcelines

    startswith_dot_ok = args.a
    if not args.a:
        chars = "\n".join(lines)

        old = '[".", ".."] + '
        if old in chars:
            startswith_dot_ok = True
            new = ""
            chars = chars.replace(old, new)

        lines[::] = chars.splitlines()

    # Stop caring if Item Starts With Dot, when yes:  ls -a

    if startswith_dot_ok:
        dropped_if = None
        dent_if = None
        for i, line in enumerate(lines):
            if line.strip() == 'if not item.startswith("."):':
                lines[i] = None

                assert dropped_if is None, (i, line)
                dropped_if = i
                dent_if = (len(line) - len(line.lstrip())) * " "

            if dropped_if is not None:
                if i > dropped_if:
                    if line:
                        if not line.startswith(dent_if):
                            dropped_if = len(lines)
                        else:
                            lines[i] = line[len(DENT_4) :]


def lines_infer_boilerplates(lines, func, title_py):
    """Choose Hash Bang, DocString, Imports, and sometimes drop all the Blank Lines"""

    # Pull in the Imports apparently mentioned, 3rd of all

    lines[::] = list(_ for _ in lines if _ is not None)  # deletes dropped Sourcelines

    chars = "\n".join(lines)
    if "os." in chars:
        lines[0:0] = ["import os", "", ""]

    # Insert the DocString to Echo Bash, 2nd of all

    lines[0:0] = ["", title_py, ""]

    # Mark these Sourcelines as Py Sourcelines, 1st of all, when printing lots

    if func in (ls_tops_by_name, ls_tops_by_stat):
        lines[0:0] = ["#!/usr/bin/env python3"]

    # Drop the blank Sourcelines when not printing lots of Sourcelines

    if func not in (ls_tops_by_name, ls_tops_by_stat):
        for i, line in enumerate(lines):
            if not line:
                lines[i] = None


def py_exec_or_show(py):
    """Show the Code or run it"""

    args = main.args

    if args.py:
        print(py)
    else:
        try:
            exec(py)
        except Exception as exc:
            traceback.print_exception(exc)
            # traceback.print_exception(exc, limit=0)

            sys.exit(1)


#
# Find & print Columns of Names, in the ways of:  ls -1
#


def ls_here_by_name():
    """Show the Working Dir as one Column of File or Dir Names"""

    items = sorted([".", ".."] + os.listdir())
    for item in items:
        if not item.startswith("."):
            print(item)


def ls_dir_by_name(top):
    """Show a Dir as one Column of File or Dir Names"""

    items = sorted([".", ".."] + os.listdir(top))
    for item in items:
        if not item.startswith("."):
            print(item)


def ls_file_by_name(file_):
    """Show one File Name"""

    _ = os.lstat(file_)
    print(file_)


def ls_top_dirs_by_name(tops):
    """Show some Dirs, each as the Label of a Column of File or Dir Names"""

    sep = None
    for top in sorted(tops):
        if sep:
            print()
        sep = "\n"

        print(top + ":")

        for item in sorted([".", ".."] + os.listdir(top)):
            if not item.startswith("."):
                print(item)


def ls_files_by_name(files):
    """Show some Files as a Column of File Names"""

    for file_ in sorted(files):
        _ = os.lstat(file_)

        print(file_)


def ls_tops_by_name(tops):
    """Show the Files, one per Line, and then the Dirs, each as Label of a Column"""

    sep = None

    topdirs = list()
    for top in sorted(tops):
        if os.path.isdir(top):
            topdirs.append(top)
        else:
            _ = os.lstat(top)
            print(top)
            sep = "\n"

    for topdir in sorted(topdirs):
        if sep:
            print()
        sep = "\n"

        print(topdir + ":")

        for item in sorted([".", ".."] + os.listdir(topdir)):
            if not item.startswith("."):
                print(item)


#
# Find & print Rows of Columns, in the ways of:  ls -l, ls -lh, ls --full-time
#


def ls_here_by_stat():
    """Show the Working Dir as many Columns of one File or Dir per Line"""

    rows = list()
    items = sorted([".", ".."] + os.listdir())
    for item in items:
        if not item.startswith("."):
            row = find_form_cells(find=item, item=item)
            rows.append(row)

    chars = byo.textwrap_lists_tabled(lists=rows, sep="  ")
    print(chars)


def ls_dir_by_stat(top):
    """Show a Dir as many Columns of one File or Dir per Line"""

    rows = list()
    items = sorted([".", ".."] + os.listdir(top))
    for item in items:
        if not item.startswith("."):
            find = os.path.join(top, item)
            row = find_form_cells(find, item=item)
            rows.append(row)

    chars = byo.textwrap_lists_tabled(lists=rows, sep="  ")
    print(chars)


def ls_file_by_stat(file_):
    """Show the Name of one File"""

    row = find_form_cells(find=file_, item=file_)
    rows = [row]
    chars = byo.textwrap_lists_tabled(lists=rows, sep="  ")
    print(chars)


def ls_top_dirs_by_stat(tops):
    """Show some Dirs, each as the Label of many Columns of one File or Dir per Line"""

    sep = None
    for top in sorted(tops):
        if sep:
            print()
        sep = "\n"

        print(top + ":")

        rows = list()
        for item in sorted([".", ".."] + os.listdir(top)):
            if not item.startswith("."):
                find = os.path.join(top, item)
                row = find_form_cells(find, item=item)
                rows.append(row)

        chars = byo.textwrap_lists_tabled(lists=rows, sep="  ")
        print(chars)


def ls_files_by_stat(files):
    """Show some Files as many Columns of one File per Line"""

    rows = list()
    for file_ in sorted(files):
        row = find_form_cells(find=file_, item=file_)
        rows.append(row)

    chars = byo.textwrap_lists_tabled(lists=rows, sep="  ")
    print(chars)


def ls_tops_by_stat(tops):
    """Show the Files, one per Line, and then the Dirs, each as Label of many Columns"""

    rows = list()

    sep = None
    topdirs = list()
    for top in sorted(tops):
        if os.path.isdir(top):
            topdirs.append(top)
        else:
            sep = "\n"

            row = find_form_cells(find=top, item=top)
            rows.append(row)

    chars = byo.textwrap_lists_tabled(lists=rows, sep="  ")
    print(chars)

    for topdir in sorted(topdirs):
        if sep:
            print()
        sep = "\n"

        print(topdir + ":")
        ls_dir_by_stat(top=topdir)


def find_form_cells(find, item):
    """Show one File or Dir as many Columns"""

    s = os.lstat(find)

    chmods = stat.filemode(s.st_mode)

    size = s.st_size
    if not stat.S_ISDIR(s.st_mode):
        if not stat.S_ISLNK(s.st_mode):
            if main.args.lh:
                size = st_size_str(s.st_size)

    stamp = st_mtime_ns_brief(s.st_mtime_ns)
    if main.args.full_time:
        stamp = st_mtime_ns_precise(s.st_mtime_ns)

    quoted_item = byo.shlex_quote_if(item)
    assert not quoted_item.startswith(" ")  # not marked as right-justified or centered
    assert not quoted_item.endswith(" ")  # not marked as left-justified or centered

    quoted = quoted_item
    if stat.S_ISLNK(s.st_mode):
        there = os.readlink(find)
        quoted = "{} -> {}".format(quoted_item, there)

    cells = (chmods, s.st_nlink, s.st_uid, s.st_gid, size, stamp, quoted)

    return cells


def st_mtime_ns_precise(st_mtime_ns):
    """Style Date/Time Stamp of a File or Dir"""

    ts = st_mtime_ns / 10**9
    ns = st_mtime_ns % 10**9

    naive = dt.datetime.fromtimestamp(ts)
    t = naive.astimezone()

    form = "%Y-%m-%d %H:%M:%S.{:09} %z".format(ns)
    chars = t.strftime(form)

    return chars


def st_mtime_ns_brief(st_mtime_ns):
    """Pack Date/Time Stamp of a File or Dir into like 12 Columns"""

    ts_int = int(st_mtime_ns / 10**9)
    t = dt.datetime.fromtimestamp(ts_int)

    now = dt.datetime.now()
    now = now.replace(microsecond=0)  # rounds down to an int timestamp

    (early_year, early_month) = (now.year, now.month)
    early_month -= 6
    if early_month < 1:
        early_month += 12
        early_year -= 1
    early = now.replace(year=early_year, month=early_month)

    (late_year, late_month) = (now.year, now.month)
    late_month += 6
    if late_month > 12:
        late_month -= 12
        late_year += 1
    late = now.replace(year=late_year, month=late_month)

    form = "%b {:2} %H:%M".format(t.day)
    if (t < early) or (t > late):
        form = "%b {:2}  %Y".format(t.day)

    chars = t.strftime(form)

    return chars


def st_size_str(st_size):
    """Right-justify Byte Size in SI Units"""

    # List the Decimal Units, else the Binary Units

    step = 10**3
    marks = list("kMGTPEZYRQ")
    if (main.args.lh % 2) == 0:
        step = 2**10
        marks = list("{}i".format(_.upper()) for _ in marks)

    # Pick a Unit less than or equal to the Size, else the Unit 1 for a 0 Size

    mark = ""
    scale_plus = step
    while st_size >= scale_plus:
        mark = marks.pop(0)  # raises IndexError when File Size >= 1024 QiB
        scale_plus *= step

    scale = scale_plus // step

    # Round down or up  # todo: when to prefer 'Rounding half to even', 'to odd', etc

    size = st_size // scale
    if (st_size % scale) >= (step // 2):
        size += 1

    assert size in range(step + 1)  # may be 1000 up from 999.5, or 1024 up from 1023.5

    chars = " {}{}B".format(size, mark)  # mark with Space at left for right-justifying

    return chars


#
# Find & print Names, but pack in more than one per Terminal Row, in the way of:  ls -m
#


def ls_by_comma_space(top):
    """Show as Lines of Comma separated Names"""

    raise NotImplementedError("def ls_by_comma_space")


#
# Find & print Names, but pack in more than one per Terminal Row, in the way of:  ls -C
#


def ls_by_ljust(top):
    """Show as Columns of Names"""

    raise NotImplementedError("def ls_by_ljust")


#
# Remember some Tests
#


PY_SH_TESTS = """

    bind 'set enable-bracketed-paste off' 2>/dev/null; unset zle_bracketed_paste
    setopt interactive_comments

    make bin

    ls -1
    ls.py -1
    ls.py -1 --py
    ls.py --py |cat -  # -1 style because Stdout IsAtty False

    ls.py --py >p.py
    python3 p.py
    cat p.py |cat -n |expand

    python3 -c "$(ls.py -1 --py)"

    ls -1a
    ls.py -1a
    ls.py -1a --py

    ls
    ls.py -C --py
    ls.py --py  # -C style because Stdout IsATty True

    ls -1 Makefile
    ls.py -1 Makefile
    ls.py -1 Makefile --py

    ls /dev/null/supercali  # exits 1 because 'Not a directory'
    echo + exit $?
    ls.py -1 /dev/null/supercali  # exits 1 because NotADirectoryError
    echo + exit $?
    ls.py -1 /dev/null/supercali --py  # exits 1 because NotADirectoryError
    echo + exit $?

    ls -1 docs/
    ls.py -1 docs/
    ls.py -1 docs/ --py

    ls -1 futures.md Makefile
    ls.py -1 futures.md Makefile
    ls.py -1 futures.md Makefile --py

    ls -1 docs/ futures.md Makefile
    ls.py -1 docs/ futures.md Makefile
    ls.py -1 docs/ futures.md Makefile --py

    ls -l
    ls.py -l
    ls.py -l --py

    ls --full-time  # often unavailable at Mac  # forces '-a' at Linux
    ls.py --full-time
    ls.py --full-time --py

    ls -lh  # different at Linux, different at Mac, legacies of last century
    ls.py -lh  # International System of Units (SI) Decimal
    ls.py -lh -lh  # Binary Dec/1998 https://physics.nist.gov/cuu/Units/binary.html
    ls.py -lh --py
    ls.py -lh -lh --py

"""


#
# Run from the Sh Command Line now, unless imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/ls.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
