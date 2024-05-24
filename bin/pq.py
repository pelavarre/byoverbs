#!/usr/bin/env python3

r"""
usage: pq.py [-h] [--py] [WORD ...]

edit the Os Copy/Paste Clipboard Buffer

positional arguments:
  WORD        word of the Pq Programming Language:  dedented, dented, ...

options:
  -h, --help  show this help message and exit
  --py        test and show the Python Code, except don't write the Clipboard Buffer

words:
  dedented, dented, reversed, sorted

guesses:
  reduces to http://codereviews/r/$R/diff from r/$R or from r/$R/diff/9?...#...
  reduces to https://docs.google.com/document/d/$HASH from ...$=/$HASH/edit?...#...
  toggles between http://...jenkins.../... and http://...jenkins/...
  toggles between PROJ-12345 and http://jira.../browse/PROJ-12345
  toggles between http://example.com and h t t p : / / e x a m p l e . c o m

quirks:
  respects color and ignores case
  doesn't clear screen at launch, nor at quit either
  looks to end the last Line, and every Line, with U+000A Line-Feed
  works well with:  ⌘C pbcopy, ⌘V pbpaste, less -IRX

examples:
  pq.py  # show these examples and exit
  pq.py --help  # show this help message and exit
  pq.py --  # parse the Paste to guess what to do with it
  pq.py dent  # insert 4 Spaces at the left of each Line
  pq.py dedent  # remove the leading Blank Columns from the Lines
"""

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import dataclasses
import difflib
import os
import pathlib
import re
import shutil
import socket
import stat
import subprocess
import sys
import textwrap
import urllib.parse

... == dict[str, int]  # new since Oct/2020 Python 3.9  # type: ignore


#
# Run well from the Sh Command Line
#


@dataclasses.dataclass
class PqPyArgs:
    """Name the Sh Command-Line Arguments of Pq Py"""

    py: bool
    words: list[str]


@dataclasses.dataclass
class Main:
    """Open up a shared workspace for the Code of this Py File"""

    args: PqPyArgs


def main() -> None:
    """Run well from the Sh Command Line"""

    args = parse_pq_py_args()
    Main.args = args

    sponge = ShPipeSponge()
    ibytes = sponge.read_bytes()
    obytes = ibytes_take_words_else(ibytes)  # often prints Py Lines & exits zero
    sponge.write_bytes(data=obytes)


def parse_pq_py_args() -> PqPyArgs:
    """Parse the Sh Command-Line Arguments of Pq Py"""

    parser = ArgumentParser()

    assert argparse.ZERO_OR_MORE == "*"
    words_help = "word of the Pq Programming Language:  dedented, dented, ..."
    parser.add_argument("words", metavar="WORD", nargs="*", help=words_help)

    py_help = "test and show the Python Code, except don't write the Clipboard Buffer"
    parser.add_argument("--py", action="count", help=py_help)

    # Parse the Sh Args, else print help & exit zero

    ns = parser.parse_args_else()

    # Collect up the Parsed Args

    args = PqPyArgs(
        py=bool(ns.py),
        words=ns.words,
    )

    # Succeed

    return args

    # often prints help & exits zero


#
# Pipe Bytes of Lines of Text through Python
#


def ibytes_take_words_else(data) -> bytes:
    """Take Sh Words as hints, else guess without any"""

    ibytes = data

    args = Main.args
    words = args.words

    if not words:
        obytes = ibytes_take_or_edit_else(ibytes)
    elif words in (["dedent"], ["dedented"]):
        obytes = ibytes_dedented_else(ibytes)
    elif words in (["dent"], ["dented"]):
        obytes = ibytes_dented_else(ibytes)
    elif words in (["reverse"], ["reversed"]):
        obytes = ibytes_reversed_else(ibytes)
    elif words in (["sort"], ["sorted"]):  # Py Sort, not Mac, not Linux
        obytes = ibytes_sorted_else(ibytes)
    else:
        assert False, (words,)

    return obytes


def ibytes_dedented_else(ibytes) -> bytes:
    """Dedent Text Lines"""

    itext = ibytes.decode()

    ... == textwrap  # type: ignore
    alt_locals = dict(itext=itext)

    py = """
        text = textwrap.dedent(itext)
        olines = text.splitlines()
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    olines = alt_locals["olines"]

    otext = "\n".join(olines) + "\n"
    obytes = otext.encode()

    py_trace_else(py)

    return obytes

    # often prints Py & exits zero


def ibytes_dented_else(ibytes) -> bytes:
    """Dent Text Lines"""

    itext = ibytes.decode()
    ilines = itext.splitlines()

    alt_globals = dict(globals())
    alt_globals["dent"] = 4 * " "
    alt_locals = dict(ilines=ilines)

    py = """
        dent = 4 * " "
        olines = list((dent + _) for _ in ilines)
    """
    py = textwrap.dedent(py).strip()

    exec(py, alt_globals, alt_locals)
    assert alt_globals["dent"] == alt_locals["dent"], (alt_locals["dent"],)
    olines = alt_locals["olines"]

    otext = "\n".join(olines) + "\n"
    obytes = otext.encode()

    py_trace_else(py)

    return obytes

    # often prints Py & exits zero


def ibytes_reversed_else(ibytes) -> bytes:
    """Reverse the Order of Text Lines"""

    itext = ibytes.decode()
    ilines = itext.splitlines()

    alt_locals = dict(ilines=ilines)

    py = """
        olines = reversed(ilines)
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    olines = alt_locals["olines"]

    otext = "\n".join(olines) + "\n"
    obytes = otext.encode()

    py_trace_else(py)

    return obytes

    # often prints Py & exits zero


def ibytes_sorted_else(ibytes) -> bytes:
    """Sort Text Lines"""

    itext = ibytes.decode()
    ilines = itext.splitlines()

    alt_locals = dict(ilines=ilines)

    py = """
        olines = sorted(ilines)
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    olines = alt_locals["olines"]

    otext = "\n".join(olines) + "\n"
    obytes = otext.encode()

    py_trace_else(py)

    return obytes

    # often prints Py & exits zero


def ibytes_endlines_else(ibytes) -> bytes:
    """End the last Line, and every Line, with U+000A Line-Feed"""

    itext = ibytes.decode()
    ilines = itext.splitlines()

    alt_locals = dict(ilines=ilines)

    py = """
        olines = ilines
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    olines = alt_locals["olines"]

    otext = "\n".join(olines) + "\n"
    obytes = otext.encode()

    py_trace_else(py)

    return obytes

    # often prints Py & exits zero


#
# Edit
#


def ibytes_take_or_edit_else(ibytes) -> bytes:
    """Guess what to do, else print some to Screen and edit it there"""

    # Guess what to do

    try:
        obytes = ibytes_take_else(ibytes)
        return obytes
    except Exception:
        pass

    # Else print some to Screen and edit it there

    fd = sys.stderr.fileno()
    size = os.get_terminal_size(fd)  # raises OSError when not a Terminal

    assert size.columns >= 20  # vs Mac Sh Terminal Columns >= 20
    assert size.lines >= 5  # vs Mac Sh Terminal Lines >= 5

    # todo: print the input that fits, to screen - even to last column & row
    # todo: shadow the print, then edit it
    # todo: output the shadow, at quit

    # End the last Line, and every Line, with U+000A Line-Feed

    obytes = ibytes_endlines_else(ibytes)

    return obytes

    # OSError: [Errno 19] Operation not supported by device
    # OSError: [Errno 25] Inappropriate ioctl for device

    # often prints Py & exits zero


def ibytes_take_else(ibytes) -> bytes:
    """Guess what Bytes Change we want, else raise an Exception"""

    itext = ibytes.decode()
    ilines = itext.splitlines()

    assert len(ilines) == 1, (len(ilines),)
    iline = ilines[-1]

    oline = iline_take_else(iline)
    olines = [oline]

    otext = "\n".join(olines) + "\n"
    obytes = otext.encode()

    return obytes

    # often prints Py & exits zero


#
# Pipe Bytes of 1 Line of Text through Python
#


def iline_take_else(iline) -> str:
    """Guess what Line Change we want, else raise an Exception"""

    funcs = [
        iline_gdrive_to_share_else,
        iline_codereviews_to_diff_else,
        iline_jenkins_toggle_else,
        iline_jira_toggle_else,
        iline_address_toggle_else,
    ]

    for func in funcs:
        try:
            oline = func(iline)
            return oline
        except Exception:
            pass

    assert False

    # often prints Py & exits zero


def iline_gdrive_to_share_else(iline) -> str:
    """Convert to Google Drive without Edit Path and without Query"""

    isplits = urllib.parse.urlsplit(iline)
    assert isplits.scheme in ("https", "http"), (isplits.scheme,)
    assert isplits.netloc.endswith(".google.com"), (isplits.netloc,)

    alt_locals = dict(iline=iline)

    py = """
        isplits = urllib.parse.urlsplit(iline)
        ipath = isplits.path

        opath = ipath
        opath = opath.removesuffix("/edit")
        opath = opath.removesuffix("/view")

        osplits = urllib.parse.SplitResult(
            scheme=isplits.scheme,
            netloc=isplits.netloc,
            path=opath,
            query="",
            fragment="",
        )
        oline = osplits.geturl()
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    oline = alt_locals["oline"]

    py_trace_else(py)

    return oline

    # 'https://docs.google.com/document/d/$HASH'
    # from 'https://docs.google.com/document/d/$HASH/edit?usp=sharing'
    # or from 'https://docs.google.com/document/d/$HASH/edit#gid=0'

    # often prints Py & exits zero


def iline_codereviews_to_diff_else(iline) -> str:
    """Convert to Http CodeReviews Diff without Fragment"""

    isplits = urllib.parse.urlsplit(iline)
    assert isplits.scheme in ("https", "http"), (isplits.scheme,)
    assert isplits.netloc.split(".")[0] == "codereviews", (isplits.netloc,)

    m = re.match(r"^/r/([0-9]+)", string=isplits.path)
    assert m, (isplits.path,)
    ... == int(m.group(1))  # type: ignore

    alt_locals = dict(iline=iline)

    py = """
        isplits = urllib.parse.urlsplit(iline)
        m = re.match(r"^/r/([0-9]+)", string=isplits.path)  # discards end of path
        r = int(m.group(1))
        osplits = urllib.parse.SplitResult(
            scheme="http",  # not "https"
            netloc=isplits.netloc.split(".")[0],  # "codereviews"
            path=f"/r/{r}/diff",
            query="",
            fragment="",
        )
        oline = osplits.geturl()
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    oline = alt_locals["oline"]

    return oline

    # 'https://codereviews/r/186738/diff'
    # from 'https://codereviews.example.co.uk/r/186738/diff/1/#index_header'

    # often prints Py & exits zero


def iline_jenkins_toggle_else(iline) -> str:
    """Toggle between wide HttpS and thin Http Jenkins Web Addresses"""

    try:
        oline = iline_jenkins_thin_else(iline)
        return oline
    except Exception:
        pass

    try:
        oline = iline_jenkins_widen_else(iline)
        return oline
    except Exception:
        pass

    assert False

    # often prints Py & exits zero


def iline_jenkins_thin_else(iline) -> str:
    """Convert to Thin Http-Not-S Jenkins Web Address"""

    isplits = urllib.parse.urlsplit(iline)

    assert isplits.scheme == "https"
    sub = isplits.netloc.split(".")[0]
    assert sub.casefold().endswith("jenkins"), (isplits.netloc,)
    assert "." in isplits.netloc, (isplits.netloc,)  # as if endswith f".{dn}"

    alt_locals = dict(iline=iline)

    py = """
        isplits = urllib.parse.urlsplit(iline)
        sub = isplits.netloc.split(".")[0]
        osplits = urllib.parse.SplitResult(
            scheme="http",
            netloc=sub.casefold().replace("jenkins", "Jenkins"),
            path=isplits.path,
            query=isplits.query,
            fragment=isplits.fragment,
        )
        oline = osplits.geturl()
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    oline = alt_locals["oline"]

    py_trace_else(py)

    return oline

    # often prints Py & exits zero


def iline_jenkins_widen_else(iline) -> str:
    """Convert to Wide HttpS Jenkins Web Address"""

    isplits = urllib.parse.urlsplit(iline)

    assert isplits.scheme == "http"
    sub = isplits.netloc.split(".")[0]
    assert sub.casefold().endswith("jenkins"), (isplits.netloc,)
    assert "." not in isplits.netloc, (isplits.netloc,)  # as if not endswith f".{dn}"

    ... == socket  # type: ignore
    alt_locals = dict(iline=iline)

    py = """
        isplits = urllib.parse.urlsplit(iline)
        fqdn = socket.getfqdn()
        dn = fqdn.partition(".")[-1]
        osplits = urllib.parse.SplitResult(
            scheme="https",
            netloc=f"{isplits.netloc}.dev.{dn}".casefold(),
            path=isplits.path.removesuffix("/"),
            query=isplits.query,
            fragment=isplits.fragment,
        )
        oline = osplits.geturl()
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    oline = alt_locals["oline"]

    py_trace_else(py)

    return oline

    # often prints Py & exits zero


def iline_jira_toggle_else(iline) -> str:
    """Toggle between thin Jira Path and wide Jira Web Address"""

    try:
        oline = iline_jira_thin_else(iline)
        return oline
    except Exception:
        pass

    try:
        oline = iline_jira_widen_else(iline)
        return oline
    except Exception:
        pass

    assert False

    # often prints Py & exits zero


def iline_jira_thin_else(iline) -> str:
    """Convert to Thin Http-Not-S jira Web Address"""

    isplits = urllib.parse.urlsplit(iline)

    assert isplits.scheme == "https"
    assert isplits.netloc.split(".")[0] == "jira", (isplits.netloc,)
    assert "." in isplits.netloc, (isplits.netloc,)  # as if endswith f".{dn}"

    alt_locals = dict(iline=iline)

    py = """
        isplits = urllib.parse.urlsplit(iline)
        oline = isplits.path.removeprefix("/browse/")  # 'PROJ-12345'
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    oline = alt_locals["oline"]

    py_trace_else(py)

    return oline

    # often prints Py & exits zero


def iline_jira_widen_else(iline) -> str:
    """Convert to Wide HttpS Jenkins Web Address"""

    assert re.match(r"[A-Z]+[-][0-9]+", iline)

    ... == socket  # type: ignore
    alt_locals = dict(iline=iline)

    py = """
        isplits = urllib.parse.urlsplit(iline)
        fqdn = socket.getfqdn()
        dn = fqdn.partition(".")[-1]
        osplits = urllib.parse.SplitResult(
            scheme="https",
            netloc=f"jira.{dn}",
            path=f"/browse/{iline}",
            query="",
            fragment="",
        )
        oline = osplits.geturl()
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    oline = alt_locals["oline"]

    py_trace_else(py)

    return oline

    # often prints Py & exits zero


def iline_address_toggle_else(iline) -> str:
    """Chill a Web Address else warm a Web Address else raise an Exception"""

    try:
        oline = iline_address_chill_else(iline)
        return oline
    except Exception:
        pass

    try:
        oline = iline_address_warm_else(iline)
        return oline
    except Exception:
        pass

    assert False

    # often prints Py & exits zero


def iline_address_chill_else(iline) -> str:
    """Convert like to cold 'https :// twitter . com /pelavarre/status/123456789'"""

    assert " " not in iline, (iline,)

    isplits = urllib.parse.urlsplit(iline)
    assert isplits.scheme in ("https", "http"), (isplits.scheme,)
    isplits = iline.split("/")
    osplits = list(isplits)
    osplits[0] = osplits[0].replace(":", " :")  # https ://

    alt_locals = dict(iline=iline)

    py = """
        isplits = iline.split("/")
        osplits = list(isplits)
        osplits[0] = osplits[0].replace(":", " :")  # https ://
        osplits[2] = " " + osplits[2].replace(".", " . ") + " "  # :// sub . domain
        oline = "/".join(osplits)
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    oline = alt_locals["oline"]

    py_trace_else(py)

    return oline

    # 'https :// twitter . com /pelavarre/status/1647691634329686016'
    # from 'https://twitter.com/pelavarre/status/1647691634329686016'

    # often prints Py & exits zero


def iline_address_warm_else(iline) -> str:
    """Convert like from cold 'https :// twitter . com /pelavarre/status/123456789'"""

    iwords = iline.split()
    iwords_0 = iwords[0]
    assert iwords_0 in ("https", "http"), (iwords_0,)

    alt_locals = dict(iwords=iwords)

    py = """
        oline = "".join(iwords)
    """
    py = textwrap.dedent(py).strip()

    exec(py, globals(), alt_locals)
    oline = alt_locals["oline"]

    py_trace_else(py)

    return oline

    # 'https://twitter.com/pelavarre/status/1647691634329686016'
    # from 'https :// twitter . com /pelavarre/status/1647691634329686016'

    # often prints Py & exits zero


#
# Amp up Import ArgParse
#


class ArgumentParser(argparse.ArgumentParser):
    """Amp up Class ArgumentParser of Import ArgParse"""

    def __init__(self, add_help=True) -> None:
        main_doc = __main__.__doc__
        assert main_doc

        # Compile much of the Arg Doc to Args of 'argparse.ArgumentParser'

        doc_lines = main_doc.strip().splitlines()
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

            sys.exit(0)  # exit 0, same as for --help

        # Print help lines & exit zero, else return Parsed Args

        argspace = self.parse_args(shargs)

        return argspace

        # often prints help & exits

    def diff_doc_vs_format_help(self) -> list[str]:
        """Form Diffs from Main Arg Doc to Parser Format_Help"""

        # Fetch the Main Doc, and note where from

        main_doc = __main__.__doc__
        assert main_doc

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

        got_doc = main_doc.strip()
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
# Edit
#


def py_trace_else(py) -> None:
    """Print the Py Lines, framed in two Blank Rows, just before running them"""

    args = Main.args

    if not args.py:
        return

    sys.stderr.write("\n")
    sys.stderr.write(py + "\n")
    sys.stderr.write("\n")

    sys.exit(0)

    # often prints Py & exits zero


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: remember that 'collections.Counter' does the 'unique_everseen' work nowadays


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
