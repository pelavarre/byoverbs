#!/usr/bin/env python3

"""
usage: cal.py [--help] [-h] [-M] [-S] [-H YYYYMMDD] [-m M] [Y]

show what weekday it is, was, or will be, of which year and month

positional arguments:
  Y            the number of the year, such as 1970 (default: today's year)

options:
  --help       show this help message and exit
  -h           don't highlight today
  -M           start the week on a UK Monday, not on a US Sunday (default if Linux)
  -S           start the week on a US Sunday, not on a UK Monday (default if Mac)
  -H YYYYMMDD  center & highlight some chosen day (default: today)
  -m M         show only one chosen month

quirks:
  forwards options into classic Cal usages:  cal, cal -m M, cal -m M Y
  falls over to forward '-h' or '-H' at Linux into:  ncal -b, ncal -b M, ncal -b M Y
  takes months 1..12 as 8 behind, 3 ahead, or this month
  takes years 0..99 as 66 behind, 33 ahead, or this year
  doesn't stop Mac 'cal' from choking over '-M'
  doesn't force you to type the '-' dashes in the YYYY-MM-DD
  doesn't highlight today when Stdin is not a Tty

examples:
  cal.py  # show these examples and exit
  cal.py --h  # show help lines and exit
  cal.py --  # show fourteen days before and after now, as one month or two
  cal.py -- |cat -  # same as 'cal.py --', but without highlighting today
  cal.py -h  # same as 'cal.py --', but without highlighting today
  cal.py -H 19990314  # same as 'cal.py --', but centering & highlighting Pi Day 1999
  cal.py -H 314  # same as 'cal.py --', but center & highlight Pi Day this year
  cal.py -H 628  # same as 'cal.py --', but center & highlight Tau Day this year
  cal.py -m 11  # show the 11th month of some year, and say which one
  cal.py 23  # show twelve months of the 23rd year of some century, and say which one
"""
# Tau Day is in the last 14 Days of the Month, Pi Day is in the first 14 Days

import argparse
import datetime as dt
import os
import re
import shlex
import subprocess
import sys
import time

import byotools as byo


def main() -> None:
    """Run as a Sh Verb"""

    # Take in Words from the Sh Command Line

    args = parse_cal_py_args_else()  # prints helps and exits, else returns args

    # Work up some context

    when = args.when
    early_when = when - dt.timedelta(days=14)
    late_when = when + dt.timedelta(days=14)

    # Form an ArgV

    inner_argv = "cal".split()
    if sys.platform == "linux":
        if args.H or args.M or args.S or args.h:  # Linux Cal lost classic "-h"
            inner_argv = "ncal -b".split()

    shverb = inner_argv[0]
    which_shverb = "/usr/bin/{}".format(inner_argv[0])
    if not os.path.exists(which_shverb):
        byo.sys_stderr_print("Command '{}' not found, but can be installed with:".format(shverb))
        byo.sys_stderr_print("sudo apt install ncal")
        byo.sys_stderr_print("sudo apt install bsdmainutils")

        sys.exit(127)  # exit code 127 for ShVerb not found

        # these Print's emulate how a 2022 Terminal might prompt you through
        #
        #   sudo apt install command-not-found
        #   sudo apt update
        #   ncal
        #   nmap
        #

        # people without 'sudo apt' can resort to:  ../pybashish/bin/cal.py

    # Also run the month before, when centered in the first 14 days of a month

    early_args = argparse.Namespace(**vars(args))
    early_args.h = None
    early_args.H = None
    early_args.Y = str(early_when.year)
    early_args.m = str(early_when.month)

    early_argv = list(inner_argv)
    argv_append_cal_args(early_argv, args=early_args, when=early_when)

    if (not args.Y) and (not args.m):
        if early_when.month != when.month:
            subprocess_run(early_argv)

    # Run the month  # TODO: Run the month before, the month, and the month after

    middle_argv = list(inner_argv)
    argv_append_cal_args(middle_argv, args=args, when=when)

    subprocess_run(middle_argv)

    # Also run the month after, when centered in the last 14 days of a month

    late_args = argparse.Namespace(**vars(args))
    late_args.h = None
    late_args.H = None
    late_args.Y = str(late_when.year)
    late_args.m = str(late_when.month)

    late_argv = list(inner_argv)
    argv_append_cal_args(late_argv, args=late_args, when=late_when)

    if (not args.Y) and (not args.m):
        if late_when.month != when.month:
            subprocess_run(late_argv)


def subprocess_run(argv) -> None:
    """Forward the options and args to a SubProcess"""

    shline = " ".join(argv)

    splits = shlex.split(shline)
    assert splits == argv, (splits, argv)

    byo.sys_stderr_print("+ {}".format(shline))

    _ = subprocess.run(argv, stdin=None)


def argv_append_cal_args(argv, args, when) -> None:
    """Append each option or arg"""

    # Work up some context

    yyyy_mm_dd = when.strftime("%Y-%m-%d")
    Y = str(when.year)
    m = str(when.month)

    # Append each option or arg, in context

    if args.h:
        argv.append("-h")

    if args.M:
        assert not args.S
        argv.append("-M")

    if args.S:
        assert not args.M
        argv.append("-S")

    if args.H:
        argv.extend(["-H", yyyy_mm_dd])
        if not args.m:
            argv.extend(["-m", m])
        if not args.Y:
            argv.append(Y)

    if args.m:
        argv_append_args_m(argv, args=args, when=when)

    if args.Y:
        argv_append_args_Y(argv, args=args, when=when)


def argv_append_args_m(argv, args, when) -> None:
    """Take months 1..12 as 8 behind, 3 ahead, or this month"""

    argv.extend(["-m", args.m])

    year_by_int_m = dict()
    for months in range(-8, 3 + 1):
        month = when.month + months

        year = when.year
        if month < 1:
            year = when.year - 1
            month += 12
        elif month > 12:
            year = when.year + 1
            month -= 12

        assert 1 <= month <= 12, (args.m, when, months, month, year)

        year_by_int_m[month] = year

    if re.match(r"^[0-9]+$", args.m):
        int_args_m = int(args.m)
        if 1 <= int_args_m <= 12:
            assert int_args_m in year_by_int_m.keys(), year_by_int_m

            arg = str(year_by_int_m[int_args_m])

            if not (args.H or args.Y):
                argv.append(arg)


def argv_append_args_Y(argv, args, when) -> None:
    """Takes years 0..99 as 66 behind, 33 ahead, or this year"""

    year_by_int_y = dict()
    for year in range(when.year - 66, when.year + 33 + 1):
        int_y = year % 100
        year_by_int_y[int_y] = year

    arg = args.Y

    if re.match(r"^[0-9]+$", args.Y):
        int_yy = int(args.Y)
        if int_yy < 100:
            assert int_yy in year_by_int_y.keys(), year_by_int_y

            arg = str(year_by_int_y[int_yy])

    argv.append(arg)


def parse_cal_py_args_else() -> argparse.Namespace:
    """Print helps for Cal Py and exit zero or nonzero, else return args"""

    # Take Words

    parser = compile_cal_py_argdoc_else()

    args = parser.parse_args_else()  # often prints help & exits zero
    if args.help:
        parser.print_help()

        sys.exit(0)

    # Reject the -M -S contradiction, and default to -M at Linux

    assert not (args.M and args.S), args

    if not args.S:
        if sys.platform == "linux":
            args.M = True  # -M chokes at Mac

    # Auto-complete the Sh Command Line

    now = parse_cal_now()

    when = now
    if args.H is not None:
        when = parse_cal_when(args.H, now=now)

    args.when = when

    if not sys.stdout.isatty():
        args.h = True  # doesn't highlight today when Stdin is not a Tty

    # Succeed

    return args


def parse_cal_now() -> dt.datetime:
    """Take now as now, or sleep one second and look again"""

    now = dt.datetime.now()
    hms = (now.hour, now.minute, now.second)
    if hms == (23, 59, 59):
        time.sleep(1)

        now = dt.datetime.now()

        hms = (now.hour, now.minute, now.second)
        assert hms != (23, 59, 59)

    return now


def parse_cal_when(str_when, now) -> dt.datetime:
    """Take in MM or MDD or MMDD or YYMMDD or YYYYMMDD"""

    # Don't force people to type the leading zero of an MM month

    alt_str_when = str_when
    if len(str_when) in (len("M"), len("MDD")):
        alt_str_when = "0" + str_when

    # Require exactly 1 Matching Form

    forms = "%m %m%d %m-%d %y%m%d %y-%m-%d %Y%m%d %Y-%m-%d".split()
    examples = list(now.strftime(_) for _ in forms)

    whens = list()
    try:
        for form, example in zip(forms, examples):
            if len(alt_str_when) == len(example):
                if bool("-" in alt_str_when) == bool("-" in example):
                    when = dt.datetime.strptime(alt_str_when, form)
                    if "%y" not in form:
                        when = when.replace(year=now.year)

                    whens.append(when)

        assert len(whens) == 1, (str_when, alt_str_when, whens)

    except Exception:
        byo.sys_stderr_print(
            "cal.py: repair -H {!r} to look like one of: {}".format(str_when, " ".join(examples))
        )

        sys.exit(1)

    when = whens[-1]

    # Succeed

    return when


def compile_cal_py_argdoc_else() -> byo.ArgumentParser:
    """Construct an ArgumentParser from the Main ArgDoc"""

    parser = byo.ArgumentParser(add_help=False)

    parser.add_argument("--help", action="count", help="show this help message and exit")

    parser.add_argument("-h", action="count", help="don't highlight today")

    parser.add_argument(
        "-M",
        action="count",
        help="start the week on a UK Monday, not on a US Sunday (default if Linux)",
    )

    parser.add_argument(
        "-S",
        action="count",
        help="start the week on a US Sunday, not on a UK Monday (default if Mac)",
    )

    parser.add_argument(
        "-H",
        metavar="YYYYMMDD",
        help="center & highlight some chosen day (default: today)",
    )

    parser.add_argument("-m", help="show only one chosen month")

    parser.add_argument(
        "Y",
        nargs="?",
        help="the number of the year, such as 1970 (default: today's year)",
    )

    return parser


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/cal.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
