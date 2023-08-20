#!/usr/bin/env python3

r"""
Amp up Import ArgParse

Form an ArgParser ArgumentParser of the Sh Command Line by compiling the Main Doc

Trust the caller to add Arguments as needed to match the Usage Line of the Main Doc

Define '.parse_args' to

    a ) print examples & exit zero, when no Sh Args sipplied
    b ) print help & exit zero, same as original ArgParse, for '-h' and '--help'
    c ) print diffs & exit nonzero, when Arg Doc wrong
    d ) accept the "--" Sh Args Separator when present with or without Positional Args

Pick the Examples of how to test this Code out of the last Paragraph of the Epilog

Don't yet solve SubParser's
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


_SELF_TEST_DOC = """
usage: p.py [-h]

test self

options:
  -h, --help  show this help message and exit

examples:
  ./p.py  # shows these examples and exits
  ./p.py --h  # shows these examples as part of a larger help message and exits
  ./p.py --  # runs this self-test
"""


def self_test_main_doc(filename):
    """Form a Main Doc for a Self-Test"""

    doc = _SELF_TEST_DOC.replace("p.py", filename)

    return doc


def ArgumentParser(add_help=True):
    """Work like Class ArgumentParser of Import ArgParse"""

    parser = compile_argdoc(drop_help=not add_help)

    proxy = ArgumentParserProxy(parser)
    parser.parse_args = proxy.parse_args

    return parser

    # 'add_help=False' for 'cal -h', 'df -h', 'ls -h', etc


class ArgumentParserProxy:
    def __init__(self, parser):
        self.parser = parser

    def parse_args(self, args=None):  # often prints help & exits
        """Parse the Sh Args, even when no Sh Args coded as the one Sh Arg '--'"""

        parser = self.parser

        # Accept the "--" Sh Args Separator when present with or without Positional Args

        sh_args = sys.argv[1:] if (args is None) else args
        if sh_args == ["--"]:  # ArgParse chokes if Sep present without Pos Args
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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/acute/byo/
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
