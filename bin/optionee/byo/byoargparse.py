#!/usr/bin/env python3

r"""
Amp up Import ArgParse

Form an ArgParser ArgumentParser of the Sh Command Line by compiling the Main Doc

Trust the caller to add Arguments as needed to match the Usage Line of the Main Doc

Define 'parser.parse_args_else' to

    a ) print examples & exit zero, when no Sh Args supplied
    b ) print help & exit zero, same as original ArgParse, for '-h' and '--help'
    c ) print diffs & exit nonzero, when Arg Doc wrong
    d ) accept the "--" Sh Args Separator when present with or without Positional Args

Pick the Examples of how to test Main out of the last Paragraph of the Epilog

Don't yet solve SubParser's
"""

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import difflib
import os
import pdb
import sys
import textwrap

... == breakpoint, pdb  # requires Python >= Jun/2018 Python 3.7


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


def self_test_main_doc(filename) -> str:
    """Form a Main Doc for a Self-Test"""

    doc = _SELF_TEST_DOC.replace("p.py", filename)

    return doc


class ArgumentParser(argparse.ArgumentParser):
    """Amp up Class ArgumentParser of Import ArgParse"""

    def __init__(self, add_help=True) -> None:  # ,doc=None  # FIXME
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

    _ = """

    def aspy(self):  # FIXME
        py = aspy(parser=self)
        return py

    def add_subparsers_from_doc(self, doc):  # FIXME
        subparsers = add_subparsers_from_doc(parser=self, doc=doc)
        alt_subparsers = SubParser(subparsers)
        return alt_subparsers

    """


# def aspy(parser):  # FIXME

# def parser_add_subparsers(parser, doc)  # FIXME
# def parser_add_subparser(parser, doc)  # FIXME


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/optionee/byo/
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
