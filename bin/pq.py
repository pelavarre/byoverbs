#!/usr/bin/env python3

r"""
usage: pq.py [-h] [WORD ...]

edit the Terminal Screen

positional arguments:
  WORD        word of the Pq Programming Language:  dedent, dent, ...

options:
  -h, --help  show this help message and exit

quirks:
  respects color and ignores case
  doesn't clear screen at launch, nor at quit either
  looks to reject Bytes that don't decode as UTF-8
  looks to end every line with U+000A Line-Feed
  works well with:  ⌘C pbcopy, ⌘V pbpaste, less -IRX

examples:
  pq.py  # show these examples and exit
  pq.py --help  # show this help message and exit
  pq.py --  # dump the Os Copy/Paste Clipboard Buffer on Screen, then edit the Screen
"""

# todo: --py  show the code without running it

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import dataclasses
import difflib
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import textwrap
import urllib

... == dict[str, int]  # new since Oct/2020 Python 3.9


#
# Run well from the Sh Command Line
#


@dataclasses.dataclass
class PqPyArgs:
    """Name the Sh Command-Line Arguments of Pq Py"""

    words: list[str]


def main() -> None:
    """Run well from the Sh Command Line"""

    args = parse_pq_py_args()

    words = args.words
    assert words in ([], ["dedent"], ["dent"]), (words,)

    sponge = ShPipeSponge()
    ibytes = sponge.read_bytes()

    if not words:
        obytes = ibytes_edit(ibytes)
    elif words == ["dedent"]:
        obytes = ibytes_dedent(ibytes)
    elif words == ["dent"]:
        obytes = ibytes_dent(ibytes)
    else:
        assert False, (words,)

    sponge.write_bytes(data=obytes)


def parse_pq_py_args() -> PqPyArgs:
    """Parse the Sh Command-Line Arguments of Pq Py"""

    parser = ArgumentParser()

    assert argparse.ZERO_OR_MORE == "*"
    words_help = "word of the Pq Programming Language:  dedent, dent, ..."
    parser.add_argument("words", metavar="WORD", nargs="*", help=words_help)

    # py_help = "show the code without running it"
    # parser.add_argument("--py", action="count", help=py_help)

    # Parse the Sh Args, else print help & exit zero

    ns = parser.parse_args_else()

    # Collect up the Parsed Args

    args = PqPyArgs(
        words=ns.words,
    )

    # Succeed

    return args

    # often prints help & exits zero


#
# Pipe Text through Python
#


def ibytes_dedent(ibytes) -> bytes:
    """Dedent Text Lines"""

    itext = ibytes.decode()
    otext = textwrap.dedent(itext)
    otext = "\n".join(otext.splitlines()) + "\n"
    obytes = otext.encode()

    return obytes


def ibytes_dent(ibytes) -> bytes:
    """Dedent Text Lines"""

    itext = ibytes.decode()
    ilines = itext.splitlines()

    dent = 4 * " "
    olines = list((dent + _) for _ in ilines)

    otext = "\n".join(olines) + "\n"
    obytes = otext.encode()

    return obytes


#
# Edit
#


def ibytes_edit(ibytes) -> bytes:
    """Edit"""

    fd = sys.stderr.fileno()
    size = os.get_terminal_size(fd)  # raises OSError when not a Terminal

    assert size.columns >= 20  # vs Mac Sh Terminal Columns >= 20
    assert size.lines >= 5  # vs Mac Sh Terminal Lines >= 5

    # todo: print the input that fits, to screen - even to last column & row
    # todo: shadow the print, then edit it
    # todo: output the shadow, at quit

    #

    try:
        obytes = ibytes_try_guess_obytes(ibytes)
        return obytes
    except Exception:
        pass

    #

    itext = ibytes.decode()
    otext = textwrap.dedent(itext)
    otext = "\n".join(otext.splitlines()) + "\n"
    obytes = otext.encode()

    #

    return obytes

    # OSError: [Errno 19] Operation not supported by device
    # OSError: [Errno 25] Inappropriate ioctl for device


def ibytes_try_guess_obytes(ibytes) -> bytes:
    """Guess what Byte change we want, else raise an Exception"""

    itext = ibytes.decode()
    ilines = itext.splitlines()

    assert len(ilines) == 1, (len(ilines),)
    iline = ilines[-1]

    oline = iline_try_guess_oline(iline)

    otext = oline + "\n"
    obytes = otext.encode()

    return obytes


def iline_try_guess_oline(iline) -> str:
    """Guess what Char change we want in 1 Line, else raise an Exception"""

    try:
        oline = iline_google_to_share_address(iline)
        return oline
    except Exception:
        pass

    try:
        oline = iline_codereviews_to_diff_address(iline)
        return oline
    except Exception:
        pass

    try:
        oline = iline_hot_to_cold_address(iline)
        return oline
    except Exception:
        pass

    try:
        oline = iline_cold_to_hot_address(iline)
        return oline
    except Exception:
        pass

    assert False


def iline_google_to_share_address(iline) -> str:
    """Convert to Google Drive without Edit Path and without Query"""

    isplits = urllib.parse.urlsplit(iline)

    scheme = isplits.scheme
    netloc = isplits.netloc
    path = isplits.path

    assert scheme in ("https", "http"), (scheme,)
    assert netloc == "docs.google.com", (netloc,)

    alt_path = path.removesuffix("/edit")

    osplits = urllib.parse.SplitResult(
        scheme=scheme, netloc=netloc, path=alt_path, query="", fragment=""
    )

    address = osplits.geturl()

    return address

    # 'https://docs.google.com/document/d/$HASH'
    # from 'https://docs.google.com/document/d/$HASH/edit?usp=sharing'
    # or from 'https://docs.google.com/document/d/$HASH/edit#gid=0'


def iline_codereviews_to_diff_address(iline) -> str:
    """Convert to Http CodeReviews Diff without Fragment"""

    isplits = urllib.parse.urlsplit(iline)

    scheme = isplits.scheme
    netloc = isplits.netloc
    path = isplits.path

    assert scheme in ("https", "http"), (scheme,)

    sub_0 = netloc.split(".")[0]
    assert sub_0 == "codereviews", (sub_0,)

    m = re.match(r"^/r/([0-9]+)", string=path)
    assert m, (m, path)

    r = int(m.group(1))

    http_not_s = "http"
    osplits = urllib.parse.SplitResult(
        scheme=http_not_s, netloc=sub_0, path=f"/r/{r}/diff", query="", fragment=""
    )

    address = osplits.geturl()

    return address

    # 'https://codereviews/r/186738/diff'
    # from 'https://codereviews.example.co.uk/r/186738/diff/1/#index_header'


def iline_hot_to_cold_address(iline) -> str:
    """Convert to like cold 'https :// twitter . com /pelavarre/status/123456789'"""

    assert " " not in iline, (iline,)

    isplits = urllib.parse.urlsplit(iline)
    assert isplits.scheme in ("https", "http"), (isplits.scheme,)

    iwords = iline.split("/")

    owords = list(iwords)
    owords[0] = owords[0].replace(":", " :")
    owords[2] = " " + owords[2].replace(".", " . ") + " "

    oline = "/".join(owords)

    return oline

    # 'https :// twitter . com /pelavarre/status/1647691634329686016'
    # from 'https://twitter.com/pelavarre/status/1647691634329686016'


def iline_cold_to_hot_address(iline) -> str:
    """Convert from like cold 'https :// twitter . com /pelavarre/status/123456789'"""

    iwords = iline.split()
    iwords_0 = iwords[0]
    assert iwords_0 in ("https", "http"), (iwords_0,)

    oline = "".join(iwords)
    return oline

    # 'https://twitter.com/pelavarre/status/1647691634329686016'
    # from 'https :// twitter . com /pelavarre/status/1647691634329686016'


#
# Amp up Import ArgParse
#


class ArgumentParser(argparse.ArgumentParser):
    """Amp up Class ArgumentParser of Import ArgParse"""

    def __init__(self, add_help=True) -> None:
        argdoc = __main__.__doc__

        # Compile much of the Arg Doc to Args of 'argparse.ArgumentParser'

        doc_lines = argdoc.strip().splitlines()
        prog = doc_lines[0].split()[1]  # second word of first line

        doc_firstlines = list(_ for _ in doc_lines if _ and (_ == _.lstrip()))
        alt_description = doc_firstlines[1]  # first line of second paragraph

        # Say when Doc Lines stand plainly outside of the Epilog

        def skippable(line) -> bool:
            strip = line.rstrip()

            skip = not strip
            skip = skip or strip.startswith(" ")  # includes .startswith("  ")
            skip = skip or strip.startswith("usage")
            skip = skip or strip.startswith("positional arguments")
            skip = skip or strip.startswith("options")  # excludes "optional arguments"

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

    def parse_args_else(self, args=None) -> argparse.Namespace:
        """Parse the Sh Args, even when no Sh Args coded as the one Sh Arg '--'"""

        # Drop the "--" Sh Args Separator, if present,
        # because 'ArgumentParser.parse_args()' without Pos Args wrongly rejects it

        shargs = sys.argv[1:] if (args is None) else args
        if sys.argv[1:] == ["--"]:  # ArgParse chokes if Sep present without Pos Args
            shargs = list()

        # Print Diffs & exit nonzero, when Arg Doc wrong

        diffs = self.diff_doc_vs_format_help()
        if diffs:
            print("\n".join(diffs))

            sys.exit(2)  # exit 2, same as for bad Sh Args

        # Print examples & exit zero, if no Sh Args

        testdoc = self.scrape_testdoc_from_epilog()
        if not sys.argv[1:]:
            print()
            print(testdoc)
            print()

            sys.exit(0)

        # Print help lines & exit zero, else return Parsed Args

        argspace = self.parse_args(shargs)

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

        # Return the Diff to Parser Doc from Main Doc, may be empty

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
# Amp up Import Io
#


@dataclasses.dataclass
class ShPipeSponge:
    """Read/ write the Sh Pipes, else the Os Clipboard Buffer, else our File"""

    stdin_isatty: bool
    stdout_isatty: bool

    def __init__(self) -> None:
        self.stdin_isatty = sys.stdin.isatty()
        self.stdout_isatty = sys.stdout.isatty()

    def read_bytes(self) -> bytes:
        """Pick an Input Source and read it"""

        stdin_isatty = self.stdin_isatty

        # Read the Sh Pipe In and done, if present

        if not stdin_isatty:
            ipath = pathlib.Path("/dev/stdin")
            ibytes = ipath.read_bytes()

            return ibytes

        # Read the Os Copy-Paste Clipboard Buffer, if present

        pbpaste_else = shutil.which("pbpaste")
        if pbpaste_else is not None:
            argv = [pbpaste_else]
            run = subprocess.run(argv, stdout=subprocess.PIPE, check=True)
            ibytes = run.stdout

            return ibytes

        # Read our Copy-Paste Clipboard Buffer File

        dirpath = pathlib.Path.home() / ".ssh"
        filepath = dirpath.joinpath("pbpaste.bin")

        if not dirpath.is_dir():  # chmod u=rwx,go= ~/.ssh
            dirpath.mkdir(stat.S_IRWXU, exist_ok=True)
        if not filepath.exists():  # chmod u=rw,go= ~/.ssh/pbpaste.bin
            filepath.touch(mode=(stat.S_IRUSR | stat.S_IWUSR), exist_ok=True)

        ibytes = filepath.read_bytes()

        return ibytes

    def write_bytes(self, data: bytes) -> None:
        """Pick an Output Sink and write it"""

        stdout_isatty = self.stdout_isatty

        # Write the Sh Pipe Out and done, if present

        if not stdout_isatty:
            opath = pathlib.Path("/dev/stdout")
            try:
                opath.write_bytes(data)
            except BrokenPipeError as exc:  # todo: how much output written?
                line = f"BrokenPipeError: {exc}"
                sys.stderr.write(f"{line}\n")
                # sys.exit(1)  # nope, don't raise BrokenPipeError as Nonzero Exit

            return

        # Write the Os Copy-Paste Clipboard Buffer, if present

        pbcopy_else = shutil.which("pbcopy")
        if pbcopy_else is not None:
            argv = [pbcopy_else]
            subprocess.run(argv, input=data, check=True)

            return

        # Write our Copy-Paste Clipboard Buffer File

        dirpath = pathlib.Path.home() / ".ssh"
        filepath = dirpath.joinpath("pbpaste.bin")

        if not dirpath.is_dir():  # chmod u=rwx,go= ~/.ssh
            dirpath.mkdir(stat.S_IRWXU, exist_ok=True)
        if not filepath.exists():  # chmod u=rw,go= ~/.ssh/pbpaste.bin
            filepath.touch(mode=(stat.S_IRUSR | stat.S_IWUSR), exist_ok=True)

        filepath.write_bytes(data)


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
