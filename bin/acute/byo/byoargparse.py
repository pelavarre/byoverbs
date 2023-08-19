#!/usr/bin/env python3

r"""
usage: byoargparse.py [-h]

compile an ArgParser Parser of the Sh Command Line from the Main Doc, and run it

options:
  -h, --help  show this help message and exit

examples:
  python3 -i bin/acute/ --
    from byo import byoargparse  # forms Parser from __main__.__doc__
    parser = byoargparse.ArgumentParser()
    aa = parser.parse_args()
    print(aa)  # Namespace()
"""

# code reviewed by people, and by Black and Flake8


import __main__
import argparse
import difflib
import os
import pdb
import sys
import textwrap

_ = breakpoint, pdb  # requires Python >= Jun/2018 Python 3.7


def ArgumentParser():
    """Work like Class ArgumentParser of Import ArgParse"""

    parser = compile_argdoc()

    proxy = ArgumentParserProxy(parser)
    parser.parse_args = proxy.parse_args

    return parser


class ArgumentParserProxy:
    def __init__(self, parser):
        self.parser = parser

    def parse_args(self, args=None):
        """Parse the Sh Args, even when no Sh Args coded as the one Sh Arg '--'"""

        parser = self.parser

        # Persuade ArgParse to ignore the "--" Sh Args Separator when no Positional Args

        sh_args = sys.argv[1:] if (args is None) else args
        if sh_args == ["--"]:
            sh_args = ""

        # Print Diffs & exit nonzero, when Arg Doc wrong

        diffs = parser_to_diffs(parser)
        if diffs:
            print("\n".join(diffs))

            sys.exit(2)

        # Print examples & exit zero, if no Sh Args

        testdoc = epilog_to_testdoc(parser.epilog)
        if not sys.argv[1:]:
            print()
            print(testdoc)
            print()

            sys.exit(0)

        # Print help lines & exit zero, else return Parsed Args

        args = type(parser).parse_args(parser, sh_args)

        return args


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


def epilog_to_testdoc(epilog):
    """Pick out the last Heading of the Epilog of an Arg Doc, and drop its Title"""

    lines = epilog.splitlines()
    indices = list(_ for _ in range(len(lines)) if lines[_])  # drops empties
    indices = list(_ for _ in indices if not lines[_].startswith(" "))  # takes headings
    testdoc = "\n".join(lines[indices[-1] + 1 :])  # takes last heading, drops its title
    testdoc = textwrap.dedent(testdoc)

    return testdoc


def parser_to_diffs(parser):
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

    return diffs


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    assert sys.argv[1:], sys.argv


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/acute/byo/
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
