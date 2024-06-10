#!/usr/bin/env python3

r"""
usage: pq.py [-h] [--py] [--yolo] [WORD ...]

edit the Os Copy/Paste Clipboard Buffer

positional arguments:
  WORD        word of the Pq Programming Language:  dedented, dented, ...

options:
  -h, --help  show this help message and exit
  --py        test and show the Python Code, except don't write the Clipboard Buffer
  --yolo      run ahead with our freshest default choices, do damage as needed

words of the Pq Programming Language = words indexing popular Grafs of Py Code:
  casefold, lower, lstrip, rstrip, strip, title, upper,
  closed, dedented, dented, ended, reversed, shuffled, sorted, undented,
  len bytes, len text, len words, len lines, wcc, wcm, wcw, wcl, wc c, wc m, wc w, wc l,
  a, dumps, json, join, loads, s, split, tac, u, x, xn1,
  ...

guesses by data:
  reduces to http://codereviews/r/$R/diff from r/$R or from r/$R/diff/9?...#...
  reduces to https://docs.google.com/document/d/$HASH from ...$=/$HASH/edit?...#...
  toggles between http://...jenkins.../... and http://...jenkins/...
  toggles between PROJ-12345 and http://jira.../browse/PROJ-12345
  toggles between http://example.com and h t t p : / / e x a m p l e . c o m

quirks:
  looks to end the last Line, and every Line, with U+000A Line-Feed
  works well with:  ⌘C pbcopy, ⌘V pbpaste, less -FIRX

examples:
  pq.py  # show these examples and exit
  pq.py --help  # show this help message and exit
  pq.py --yolo  # parse the Paste to guess what to do to it
  pq.py dent  # insert 4 Spaces at the left of each Line
  pq.py dedent  # remove the leading Blank Columns from the Lines
  pq.py len lines  # count Lines
  pq.py --py len lines  # show how to count Lines
  echo '[0, 11, 22]' |pq.py json |cat -  # format Json consistently
"""

# quirks to come inside 'pq vi':
#   respects color and ignores case
#   doesn't clear screen at launch, nor at quit either

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import collections
import dataclasses
import difflib
import itertools
import json
import os
import pathlib
import random
import re
import shutil
import socket
import stat
import subprocess
import sys
import textwrap
import urllib.parse

... == dict[str, int]  # new since Oct/2020 Python 3.9  # type: ignore
... == json, random  # often unused  # type: ignore


#
# List Grafs of Py Code to Abbreviate Intensely
#


PY_LINES_TEXT = r"""

    oline = " ".join(ilines)  # |tr '\n' ' '  # |xargs  # x x
    oline = (4 * " ") + iline  # as if textwrap.dented  # dent
    oline = iline.lstrip()  # lstripped  # |sed 's,^ *,,'
    oline = iline.removeprefix(4 * " ")  # as if textwrap.undented  # undent
    oline = iline.rstrip()  # rstripped  # |sed 's, *$,,'
    oline = iline.strip()  # stripped  # |sed 's,^ *,,' |sed 's, *$,,'
    oline = str(len(ibytes))  # bytes len  # |wc -c  # wc c  # wcc
    oline = str(len(itext))  # text characters len  # |wc -m  # wc m  # wcm
    oline = str(len(itext.split()))  # words len  # |wc -w  # wc w  # wcw
    oline = str(len(itext.splitlines()))  # lines len  # |wc -l  # wc l  # wcl

    olines = ilines  # ended  # end  # ends every line with "\n"
    olines = itext.split()  # |xargs -n 1  # |xn1  # split
    olines = list(ilines); random.shuffle(olines)  # shuffled
    olines = reversed(ilines)  # reverse  # |tail -r  # tail r  # |tac  # tac
    olines = sorted(ilines)  # sort  # s s

    otext = itext.casefold()  # casefolded  # folded
    otext = itext.lower()  # lowercased  # |tr '[A-Z]' '[a-z]'
    otext = itext.title()  # titled
    otext = itext.upper()  # uppercased  # |tr '[a-z]' '[A-Z]'
    otext = json.dumps(json.loads(itext), indent=2) + "\n"  # |jq .  # jq
    otext = textwrap.dedent(itext) + "\n"  # dedented

"""

# todo: assert rstripped and sorted


PY_GRAFS_TEXT = r"""

    # |awk '{print $NF}'  # a a
    ilinewords = iline.split()
    oline = ilinewords[-1] if ilinewords else ""

    # frame  # framed
    olines = list()
    olines.extend(2 * [""])  # top margin
    for iline in ilines:
        oline = (4 * " ") + iline  # left margin
        olines.append(oline)
    olines.extend(2 * [""])  # bottom margin

    # set, uniq, uniq_everseen, unsorted
    olines = list(dict((_, _) for _ in ilines).keys())

    # closed # close  # ends last line with "\n"
    otext = itext if itext.endswith("\n") else (itext + "\n")

"""

# todo: assert rstripped and sorted


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

    words_help = "word of the Pq Programming Language:  dedented, dented, ..."
    py_help = "test and show the Python Code, except don't write the Clipboard Buffer"
    yolo_help = "run ahead with our freshest default choices, do damage as needed"

    assert argparse.ZERO_OR_MORE == "*"
    parser.add_argument("words", metavar="WORD", nargs="*", help=words_help)

    parser.add_argument("--py", action="count", help=py_help)
    parser.add_argument("--yolo", action="count", help=yolo_help)  # --yolo, --y, --

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


def ibytes_take_words_else(data) -> bytes:  # noqa C901 complex
    """Take Sh Words as hints, else guess without any"""

    ibytes = data

    args = Main.args
    words = args.words

    # Guess how to edit when given no Sh Words

    if not words:
        obytes = ibytes_take_or_edit_else(ibytes)
        return obytes

    # Pick out the Py Graf most closely matching the Sh Words

    keys = words
    py_grafs = keys_to_py_grafs(keys)

    if not py_grafs:
        print(f"pq.py: No Py Grafs matched by {keys}", file=sys.stderr)

        sys.exit(2)  # exit 2 for wrong args

    n = len(py_grafs)
    if n != 1:
        print(
            f"pq.py: {n} Py Grafs matched, not just 1, by {keys}",
            file=sys.stderr,
        )

        for graf in py_grafs:
            print(file=sys.stderr)
            print(graf, file=sys.stderr)

        sys.exit(2)  # exit 2 for wrong args

    hit_py_graf = py_grafs[-1]

    py_graf = py_graf_complete(py_graf=hit_py_graf)
    py_text = "\n".join(py_graf)

    # Trace the chosen Py Graf before testing it, on request

    if False:  # jitter Sat 9/Jun
        py_trace_else(py_text)

    # Run the chosen Py Graf

    alt_locals = dict(ibytes=ibytes)

    if False:  # jitter Fri 7/Jun
        print("<<<", file=sys.stderr)
        print(py_text, file=sys.stderr)
        print(">>>", file=sys.stderr)
        breakpoint()

    exec(py_text, globals(), alt_locals)  # ibytes_take_words_else
    obytes = alt_locals["obytes"]

    # Print Py and exit zero, without writing the OBytes, when running to show --py

    py_trace_else(py_text)

    # Succeed

    return obytes


def py_graf_complete(py_graf) -> list[str]:
    """Auto-complete one Py Graf"""  # todo: more competently

    py_words_text = "\n".join(py_graf)
    py_words = py_text_split(py_words_text)

    # Guess how to set up

    before_py_graf = list()
    if ("itext" in py_words) or ("ilines" in py_words) or ("iline" in py_words):
        before_py_graf.append(r"itext = ibytes.decode()")

    if ("ilines" in py_words) or ("iline" in py_words):
        before_py_graf.append(r"ilines = itext.splitlines()")

    # Guess if and how much to dent

    middle_py_graf = list(py_graf)
    if "iline" in py_words:
        if "olines" not in py_words:
            before_py_graf.append(r"olines = list()")
            before_py_graf.append(r"for iline in ilines:")

            dent = 4 * " "
            middle_py_graf[::] = list((dent + _) for _ in middle_py_graf)
            middle_py_graf.append(dent + r"olines.append(oline)")

    # Guess how to tear down

    after_py_graf = list()
    if ("iline" not in py_words) and ("oline" in py_words):
        if "olines" not in py_words:
            after_py_graf.append(r"olines = [oline]")

    if ("olines" in py_words) or ("oline" in py_words):
        if "otext" not in py_words:
            after_py_graf.append(r'otext = "\n".join(olines) + "\n"')

    after_py_graf.append(r"obytes = otext.encode()")

    # Frame the Seed in the Middle with blank Lines, if lotsa Set Up or Tear Down

    py_graf = before_py_graf + middle_py_graf + after_py_graf
    if len(py_graf) > 3:
        py_graf = before_py_graf + [""] + middle_py_graf + [""] + after_py_graf
        py_graf = graf_strip(py_graf)

    # Succeed

    return py_graf


def graf_strip(graf) -> list[str]:
    """Drop the leading Empty Lines and the trailing Empty Lines"""

    alt_graf = list(graf)

    while alt_graf[0] == "":
        alt_graf.pop(0)
    while alt_graf[-1] == "":
        alt_graf.pop(-1)

    return alt_graf


#
# Edit the Bytes
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

    with open("/dev/tty", "rb") as ttyin:
        fd = ttyin.fileno()
        size = os.get_terminal_size(fd)

    assert size.columns >= 20  # vs Mac Sh Terminal Columns >= 20
    assert size.lines >= 5  # vs Mac Sh Terminal Lines >= 5

    # todo: print the input that fits, to screen - even to last column & row
    # todo: shadow the print, then edit it
    # todo: output the shadow, at quit

    # End the last Line, and every Line, with U+000A Line-Feed

    obytes = ibytes_ended_else(ibytes)

    return obytes

    # OSError: [Errno 19] Operation not supported by device
    # OSError: [Errno 25] Inappropriate ioctl for device

    # often prints Py & exits zero


def ibytes_ended_else(ibytes) -> bytes:
    """End the last Line, and every Line, with U+000A Line-Feed"""

    itext = ibytes.decode()
    ilines = itext.splitlines()

    alt_locals = dict(ilines=ilines)

    py_text = """
        olines = ilines
    """
    py_text = textwrap.dedent(py_text).strip()

    exec(py_text, globals(), alt_locals)  # ibytes_ended_else
    olines = alt_locals["olines"]

    otext = "\n".join(olines) + "\n"
    obytes = otext.encode()

    py_trace_else(py_text)

    return obytes

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

    py_text = """
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
    py_text = textwrap.dedent(py_text).strip()

    exec(py_text, globals(), alt_locals)  # iline_gdrive_to_share_else
    oline = alt_locals["oline"]

    py_trace_else(py_text)

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

    py_text = """
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
    py_text = textwrap.dedent(py_text).strip()

    exec(py_text, globals(), alt_locals)  # iline_codereviews_to_diff_else
    oline = alt_locals["oline"]

    py_trace_else(py_text)

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

    py_text = """
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
    py_text = textwrap.dedent(py_text).strip()

    exec(py_text, globals(), alt_locals)  # iline_jenkins_thin_else
    oline = alt_locals["oline"]

    py_trace_else(py_text)

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

    py_text = """
        isplits = urllib.parse.urlsplit(iline)
        fqdn = socket.getfqdn()
        dn = fqdn.partition(".")[-1]  # Domain Name of HostName
        osplits = urllib.parse.SplitResult(
            scheme="https",
            netloc=f"{isplits.netloc}.dev.{dn}".casefold(),
            path=isplits.path.removesuffix("/"),
            query=isplits.query,
            fragment=isplits.fragment,
        )
        oline = osplits.geturl()
    """
    py_text = textwrap.dedent(py_text).strip()

    exec(py_text, globals(), alt_locals)  # iline_jenkins_widen_else
    oline = alt_locals["oline"]

    py_trace_else(py_text)

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

    py_text = """
        isplits = urllib.parse.urlsplit(iline)
        oline = isplits.path.removeprefix("/browse/")  # 'PROJ-12345'
    """
    py_text = textwrap.dedent(py_text).strip()

    exec(py_text, globals(), alt_locals)  # iline_jira_thin_else
    oline = alt_locals["oline"]

    py_trace_else(py_text)

    return oline

    # often prints Py & exits zero


def iline_jira_widen_else(iline) -> str:
    """Convert to Wide HttpS Jenkins Web Address"""

    assert re.match(r"[A-Z]+[-][0-9]+", iline)

    ... == socket  # type: ignore
    alt_locals = dict(iline=iline)

    py_text = """
        isplits = urllib.parse.urlsplit(iline)
        fqdn = socket.getfqdn()
        dn = fqdn.partition(".")[-1]  # Domain Name of HostName
        osplits = urllib.parse.SplitResult(
            scheme="https",
            netloc=f"jira.{dn}",
            path=f"/browse/{iline}",
            query="",
            fragment="",
        )
        oline = osplits.geturl()
    """
    py_text = textwrap.dedent(py_text).strip()

    exec(py_text, globals(), alt_locals)  # iline_jira_widen_else
    oline = alt_locals["oline"]

    py_trace_else(py_text)

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

    py_text = """
        isplits = iline.split("/")
        osplits = list(isplits)
        osplits[0] = osplits[0].replace(":", " :")  # https ://
        osplits[2] = " " + osplits[2].replace(".", " . ") + " "  # :// sub . domain
        oline = "/".join(osplits).strip()
    """
    py_text = textwrap.dedent(py_text).strip()

    exec(py_text, globals(), alt_locals)  # iline_address_chill_else
    oline = alt_locals["oline"]

    py_trace_else(py_text)

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

    py_text = """
        oline = "".join(iwords)
    """
    py_text = textwrap.dedent(py_text).strip()

    exec(py_text, globals(), alt_locals)  # iline_address_warm_else
    oline = alt_locals["oline"]

    py_trace_else(py_text)

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
        alt_description = doc_firstlines[1]  # first Line of second Graf

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


def py_trace_else(py_text) -> None:
    """Print the Py Lines, framed in two Blank Rows, just before running them"""

    args = Main.args

    if not args.py:
        return

    sys.stderr.write("\n")
    sys.stderr.write(py_text + "\n")
    sys.stderr.write("\n")

    sys.exit(0)

    # often prints Py & exits zero


#
# Search popular Py Grafs
#


def keys_to_py_grafs(keys) -> list[list[str]]:
    """Search popular Py Grafs"""

    # Fetch the multi-line Py Graf, and add in the single-line Py Grafs

    mtext = textwrap.dedent(PY_GRAFS_TEXT)
    mlines = mtext.splitlines()
    mlines = list(mlines)
    mgrafs = list(list(v) for k, v in itertools.groupby(mlines, key=bool) if k)

    stext = textwrap.dedent(PY_LINES_TEXT)
    slines = stext.splitlines()
    slines = list(_ for _ in slines if _)
    sgrafs = list([_] for _ in slines)

    grafs = mgrafs + sgrafs

    # Score each Py Graf

    score_by_graf_text = dict()
    for graf in grafs:
        score = keys_graf_score(keys, graf)

        graf_text = "\n".join(graf)
        score_by_graf_text[graf_text] = score

    scores = list(score_by_graf_text.values())

    # Pick out all the equally strong Matches

    most = max(scores)
    if not most:
        return list()

    py_grafs = list()
    for graf in grafs:
        graf_text = "\n".join(graf)
        score = score_by_graf_text[graf_text]
        if score == most:
            py_grafs.append(graf)

    # Succeed

    return py_grafs


def keys_graf_score(keys, graf) -> int:  # noqa C901 complex
    """Pick out which popular Py Grafs match the Keys most closely"""

    # Count up the Matches, when searching with one kind of Fuzz or another

    score_by_key: dict
    score_by_key = collections.defaultdict(int)

    for line in graf:  # found
        for key in keys:
            score_by_key[key] += line.count(key)

    for line in graf:  # found in Str Word
        words = line.split()
        for key in keys:
            score_by_key[key] += words.count(key)

            for word in words:  # starts Str Word
                if word.startswith(key):
                    score_by_key[key] += 1

    for line in graf:  # found in Py Words
        words = py_text_split(py_text=line)
        for key in keys:
            score_by_key[key] += words.count(key)

            for word in words:  # starts Py Word
                if word.startswith(key):
                    score_by_key[key] += 1

    # Count up the Matches, when searching with one kind of Fuzz or another

    for key in keys:
        key_score = score_by_key[key]
        if not key_score:
            return 0

    score = sum(score_by_key.values())

    # Succeed

    if False:  # jitter Sat 8/Jun
        graf_text = "\n".join(graf)
        if "wc -m" in graf_text:
            breakpoint()
            pass

    return score


def py_text_split(py_text) -> list[str]:
    """Split a Line into Words to search up"""

    words = list(
        _.group(0)
        for _ in re.finditer(r"[a-zA-Z][a-zA-Z0-9_]*|[-.+0-9Ee]|.", string=py_text)
    )

    return words

    # todo: split more by the Py Rules, or even totally exactly like Py Rules
    # except don't drop Comments


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: remember that 'collections.Counter' does the 'unique_everseen' work nowadays


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
