#!/usr/bin/env python3

r"""
usage: pq [-h] [-q] [--py] [--yolo] [WORD ...]

edit the Os Copy/Paste Clipboard Buffer and the Dev Tty Screen

positional arguments:
  WORD         word of the Pq Programming Language:  dedented, dented, ...

options:
  -h, --help   show this help message and exit
  -q, --quiet  say less and less, when called with -q or -qq or -qqq
  --py         test and show the Python Code, but don't write the Paste Buffer
  --yolo       do what's popular now

words and phrases of the Pq Programming Language:
  ascii, casefold, eval, lower, lstrip, repr, rstrip, strip, title, upper,
  close, dedent, dent, end, reverse, shuffle, sort, sponge, undent,
  deframe, dumps, frame, json, join, loads, split,
  expand, md5sum, sha256, tail -r, tac, unexpand,
  len bytes, len text, len words, len lines, text set

intense cryptic abbreviations:
  xn1
  wc c, wc m, wc w, wc l, wc c, wc m, wc w, wc l
  em, jq, vi
  -, a, c, f, h, n, s, t, u, x
  ...

meanings found when no words chosen:
  toggles between http://example.com and h t t p : / / e x a m p l e . c o m
  toggles between http://...jenkins.../... and http://...jenkins/...
  toggles between https://jira.../browse/PROJ-12345 and PROJ-12345
  shrinks to https://docs.google.com/document/d/$HASH from ...$=/$HASH/edit?...#...
  shrinks to http://codereviews/r/$R/diff from r/$R or from r/$R/diff/9?...#...
  shrinks Py Tracebacks to just 4 Lines

quirks:
  looks to end the last Line, and every Line, with U+000A Line-Feed
  takes no words to mean 'olines = ilines' after running self-tests
  works well with:  ⌘C pbcopy, ⌘V pbpaste, less -FIRX

examples:
  pq.py  # show these examples, run self-tests, and exit
  pq --help  # show this help message and exit
  pq --yolo  # do what's popular now  # like parse the Paste & guess what to do
  pq  # end every Line of the Os Copy/Paste Clipboard Buffer
  pq dent  # insert 4 Spaces at the left of each Line
  pq dedent  # remove the leading Blank Columns from the Lines
  pq len lines  # count Lines
  pq --py len lines  # show how to count Lines
  echo '[0, 11, 22]' |pq json |cat -  # format Json consistently
  pq 'oline = "<< " + iline + " >>"'  # add Prefix and Suffix to each Line
  pq 'olines = ilines[:3] + ["..."] + ilines[-3:]'  # show Head and Tail
  pq vi  # edit the Os Copy/Paste Clipboard Buffer, in the way of Vim or Emacs
"""

# quirks to come when we add 'pq vi':
#   respects color and ignores case
#   doesn't clear screen at launch, nor at quit either

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import ast
import bdb
import collections
import dataclasses
import difflib
import importlib
import itertools
import json
import os
import pathlib
import pdb
import re
import shlex
import shutil
import stat
import sys
import textwrap
import time
import traceback
import unicodedata


# import ast
# import datetime as dt
# import decimal
# import io
# import math
# import platform
# import select
# import signal
# import termios  # sad at Windows
# import tty  # sad at Windows
# import typing


_: object  # '_: object' tells MyPy to accept '_ =' tests across two and more Datatypes

_ = dict[str, int] | None  # new since Oct/2021 Python 3.10
_ = json, time  # r'\bjson[.]' found in str of Py  # r'\btime[.]' for debug as yet

if not __debug__:
    raise NotImplementedError(str((__debug__,)))  # "'python3' is better than 'python3 -O'"


#
# Run well from the Sh Command Line
#


def main() -> None:
    """Run well from the Sh Command Line"""

    def func() -> None:
        peqr = PyExecQueryResult()
        peqr.try_main(shargs=sys.argv[1:])  # often prints help & exits zero

    try_func_else_pdb_pm(func)


def try_func_else_pdb_pm(func) -> None:
    """Call a Py Func, but post-mortem debug an unhandled Exc"""

    try:
        peqr = PyExecQueryResult()
        peqr.try_main(shargs=sys.argv[1:])  # often prints help & exits zero
    except bdb.BdbQuit:
        raise
    except Exception as exc:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        assert exc is exc_value

        if not hasattr(sys, "last_exc"):  # give up when raised inside exec(py, ...)
            raise

        traceback.print_exc(file=sys.stderr)

        print("\n", file=sys.stderr)
        print("\n", file=sys.stderr)
        print("\n", file=sys.stderr)

        print(">>> sys.last_traceback = sys.exc_info()[-1]", file=sys.stderr)
        sys.last_traceback = exc_traceback

        print(">>> pdb.pm()", file=sys.stderr)
        pdb.pm()

        raise


@dataclasses.dataclass
class PyExecQueryResult:
    """Parse, compose, and run fragments of Python Code"""

    cued_py_grafs: list[list[str]]

    pbcopy_else: str | None
    pbpaste_else: str | None

    pq_words: list[str]  # mutable
    py: int  # mutable
    quiet: int  # mutable

    stdin_isatty: bool
    stdout_isatty: bool

    ibytes_else: bytes | None  # mutable
    itext_else: str | None  # mutable

    def __init__(self) -> None:

        mgrafs = self.fetch_cued_mgrafs()
        sgrafs = self.fetch_cued_sgrafs()
        cued_py_grafs = mgrafs + sgrafs  # ordered, not sorted
        self.cued_py_grafs = cued_py_grafs

        self.pbcopy_else = shutil.which("pbcopy")
        self.pbpaste_else = shutil.which("pbpaste")

        self.pq_words = list()
        self.py = 0
        self.quiet = 0

        self.stdin_isatty = sys.stdin.isatty()
        self.stdout_isatty = sys.stdout.isatty()

        self.ibytes_else = None

    #
    # Run well from the Sh Command Line
    #

    def try_main(self, shargs) -> None:
        """Run well from the Sh Command Line"""

        # Mutate Self as per the Sh Args

        assert not self.pq_words, (self.pq_words,)
        assert not self.py, (self.py,)
        assert not self.quiet, (self.quiet,)

        ns = self.parse_pq_args_else(shargs)  # often prints help & exits zero

        pq_words = ns.words or list()
        if ns.words:
            if ns.words[0] == "xeditline":
                pq_words = ["xeditline"]

        self.pq_words = pq_words
        self.py = ns.py or 0
        self.quiet = min(3, ns.quiet or 0)

        # Parse some Py Code and compose the rest,
        # and maybe sponge up 'self.ibytes_else', and maybe also 'self.itext_else'

        (found_py_graf, complete_py_graf, importables) = self.find_and_form_py_lines()

        # Option to trace the Py Code without running it

        self.py_trace_else(  # often prints Py & exits zero
            found_py_graf, complete_py_graf=complete_py_graf
        )

        # Run the Py Code, after patching it to drop Lines already run, if any

        lines = complete_py_graf
        cgrafs = list(list(v) for k, v in itertools.groupby(lines, key=bool) if k)

        alt_locals: dict[str, object | None]
        alt_locals = dict()

        if self.ibytes_else is not None:
            assert len(cgrafs) > 2, (cgrafs, lines)  # Imports, I Bytes/Text, more
            assert all(_.startswith("import ") for _ in cgrafs[0]), (cgrafs[0],)

            cgrafs_1 = cgrafs[1]
            bindices = list(i for i, _ in enumerate(cgrafs_1) if _.startswith("ibytes = "))
            tindices = list(i for i, _ in enumerate(cgrafs_1) if _.startswith("itext = "))
            if tindices:
                assert self.itext_else is not None, (self.itext_else, found_py_graf)
                alt_locals["itext"] = self.itext_else
                cgrafs[1][::] = cgrafs_1[max(tindices) + 1 :]
            elif bindices:
                alt_locals["ibytes"] = self.ibytes_else
                cgrafs[1][::] = cgrafs_1[max(bindices) + 1 :]

        alt_py_graf = list(line for cgraf in cgrafs for line in cgraf)
        py_text = "\n".join(alt_py_graf)

        # alt_locals["dirpath"] = None  # todo: doesn't help
        # globals()["dirpath"] = None  # todo: doesn't help

        try:
            for importable in importables:
                importable_ = "datetime" if importable == "dt" else importable
                importlib.import_module(importable_)
            exec(py_text, globals(), alt_locals)  # because "i'm feeling lucky"
        except Exception:
            print((3 * "\n") + py_text + (2 * "\n"), file=sys.stderr)
            raise

        # sys.stdout.flush()  # todo: to flush the Stdout, or not

    def parse_pq_args_else(self, shargs) -> argparse.Namespace:
        """Parse the Sh Args of Pq"""

        # Declare Positional Arguments and Options

        parser = ArgumentParser()

        words_help = "word of the Pq Programming Language:  dedented, dented, ..."
        quiet_help = "say less and less, when called with -q or -qq or -qqq"
        py_help = "test and show the Python Code, but don't write the Paste Buffer"
        yolo_help = "do what's popular now"

        assert argparse.ZERO_OR_MORE == "*"
        parser.add_argument("words", metavar="WORD", nargs="*", help=words_help)

        parser.add_argument("-q", "--quiet", action="count", help=quiet_help)
        parser.add_argument("--py", action="count", help=py_help)
        parser.add_argument("--yolo", action="count", help=yolo_help)  # --yolo, --y, --

        # Take up Sh Args as if "--" comes before the first Positional Argument

        many_shargs = list()
        for index, sharg in enumerate(shargs):
            if sharg == "--":  # accepts explicit "--" Sh Arg
                many_shargs.extend(shargs[index:])
                break

            if not sharg.startswith("-"):  # inserts implicit "--" Sh Arg
                many_shargs.append("--")
                many_shargs.extend(shargs[index:])
                break

            many_shargs.append(sharg)

        # Parse the Sh Args

        try:
            ns = parser.parse_args_else(many_shargs)  # often prints help & exits zero
        except SystemExit:
            self.assert_lots_ok()  # ~100 ms in Jun/2024
            raise

        # Succeed

        return ns

        # often prints help & exits zero

    def py_trace_else(self, found_py_graf, complete_py_graf) -> None:
        """Print the Py Lines, framed in two Blank Rows, just before running them"""

        found_py_text = "\n".join(found_py_graf)
        complete_py_text = "\n".join(complete_py_graf)

        ipipe = "" if self.stdin_isatty else "|"
        opipe = "" if self.stdout_isatty else "|"

        if not self.py:
            return

        if self.quiet:
            print("\n" + found_py_text + "\n", file=sys.stderr)
        else:
            e = sys.stderr
            print(file=e)
            print(f"{ipipe}python3 -c '''", file=e)
            print("\n" + complete_py_text + "\n", file=e)
            print(f"''' {opipe}".rstrip(), file=e)
            print(file=e)

        sys.exit(0)  # exit 0 after printing Py, as if after printing help

        # often prints Py & exits zero

    def fetch_cued_mgrafs(self) -> list[list[str]]:
        """Fetch the Cued Multi-Line Paragraphs"""

        mgrafs0 = text_to_grafs(CUED_PY_GRAFS_TEXT)
        if mgrafs0 != sorted(mgrafs0):
            try:
                list_assert_eq(mgrafs0, b=sorted(mgrafs0))  # CUED_PY_GRAFS_TEXT sorted
            except Exception:
                sys.exit(1)

        mgrafs1 = text_to_grafs(ITEXT_PY_GRAFS_TEXT)  # ordered, not sorted

        mgrafs = mgrafs0 + mgrafs1

        return mgrafs

    def fetch_cued_sgrafs(self) -> list[list[str]]:
        """Fetch the Cued Single-Line Paragraphs"""

        lit_sgrafs = text_to_grafs(CUED_PY_LINES_TEXT)

        sgrafs = list()
        for lit_sgraf in lit_sgrafs:
            sourcelines = list(_ for _ in lit_sgraf if not _.startswith("#"))
            if sourcelines:
                sgrafs.append(lit_sgraf)

        list_assert_eq(sgrafs, b=sorted(sgrafs))  # CUED_PY_LINES_TEXT sorted

        return sgrafs

    def assert_lots_ok(self) -> None:  # ~100 ms in Jun/2024
        """Run slow Self-Test's and assert they all pass"""

        cued_py_grafs = self.cued_py_grafs

        for cued_py_graf in cued_py_grafs:
            self.py_graf_assert_ipull_to_opush(py_graf=cued_py_graf)

        py_graf_by_cues = self.py_grafs_to_graf_by_cues(cued_py_grafs)
        for cues, py_graf in py_graf_by_cues.items():
            py_grafs = self.cues_to_py_grafs(cues=cues)

            assert py_grafs, (cues, py_graf, py_grafs)
            assert len(py_grafs) == 1, (cues, py_graf, py_grafs)
            assert py_graf == tuple(py_grafs[-1]), (cues, py_graf, py_grafs)

        # often chokes and exits nonzero

    def py_graf_assert_ipull_to_opush(self, py_graf) -> None:
        """Assert this Graf has 1 Input and 1 Output"""

        (ipulls, opushes) = self.py_graf_to_i_pulls_o_pushes(py_graf)

        if ipulls == ["iolines"]:  # pq reverse  # pq sort
            assert not opushes, (ipulls, opushes, py_graf)
        elif ipulls == ["print"]:  # pq reverse  # pq sort
            assert not opushes, (ipulls, opushes, py_graf)
        elif ipulls == ["print", "stdin", "stdout"]:  # pq ts
            assert not opushes, (ipulls, opushes, py_graf)

        elif (not ipulls) and (opushes == ["olines"]):  # pq ls
            pass
        elif (not ipulls) and (opushes == ["oobject"]):  # pq pi
            pass

        elif py_graf == self.PbPastePyGraf:
            pass

        else:
            assert len(ipulls) == 1, (ipulls, opushes, py_graf)
            assert len(opushes) == 1, (ipulls, opushes, py_graf)

    def py_graf_to_i_pulls_o_pushes(self, py_graf) -> tuple[list[str], list[str]]:
        """Pick out the one Sh Pipe Input and one Sh Pipe Output from the Py Graf"""

        iowords = ["iolines", "print", "stdout"]  # mutations, not inits
        iwords = iowords + ["stdin", "ibytes", "itext", "ilines", "iline"]  # mentions
        owords = ["obytes", "otext", "olines", "oline", "oobject", "oobjects"]  # inits

        (ipulls, opushes) = py_graf_to_pulls_pushes(py_graf)

        ipulls = list(_ for _ in ipulls if _ in iwords)
        opushes = list(_ for _ in opushes if _ in owords)

        return (ipulls, opushes)

    def py_grafs_to_graf_by_cues(self, py_grafs) -> dict[tuple[str], tuple[str]]:
        """Index each Py Graf by its own Keys"""

        py_graf_by_cues: dict[tuple, tuple]
        py_graf_by_cues = dict()

        for py_graf in py_grafs:
            for py_line in py_graf:
                (_, _, py_right) = py_line.partition("#")

                cues_py_list = py_right.split("#")
                cues_py_list = list(_.strip() for _ in cues_py_list if _)
                cues_py_list = list(dict((_, _) for _ in cues_py_list).keys())

                cues_list = list()
                for cues_py in cues_py_list:
                    if not re.match(r"^[- .0-9A-Za-z|]+$", string=cues_py):
                        continue

                    cues = tuple(shlex.split(cues_py.replace("|", "")))
                    if cues == (len(cues) * cues[:1]):
                        cues = cues[:1]
                    if not cues:
                        cues = (cues_py,)  # such as ('|',) as the Cues built from '# |'

                    if cues not in cues_list:
                        cues_list.append(cues)

                for cues in cues_list:
                    assert cues not in py_graf_by_cues.keys(), (cues,)
                    py_graf_by_cues[cues] = tuple(py_graf)

        return py_graf_by_cues

    #
    # Parse some Py Code and compose the rest       # todo: resolve the noqa C901
    #

    PbPastePyGraf = ['pathlib.Path("/dev/stdout").write_bytes(ibytes)']

    def find_and_form_py_lines(self) -> tuple[list[str], list[str], list[str]]:  # noqa C901
        """Parse some Py Code and compose the rest"""

        pq_words = self.pq_words
        stdin_isatty = self.stdin_isatty
        stdout_isatty = self.stdout_isatty

        py_graf: list[str]
        py_graf = list()

        # Take whole Input File as Cues, if no Cues given as Sh Args

        if not pq_words:
            if stdin_isatty and not stdout_isatty:  # 'pq| ...' means 'pbpaste| ...'
                py_graf = ["obytes = ibytes"]
                print("+ pbpaste", file=sys.stderr)
            elif (not stdin_isatty) and stdout_isatty:  # '... |pq' means '... |pbcopy'
                py_graf = ["obytes = ibytes"]
                print("+ pbcopy", file=sys.stderr)
            else:  # 'pq' or '... |pq |...' means step the Pipe Data forward
                py_graf = self.read_ibytes_to_one_py_graf(verbose=True)

        # Define the minimal Positional Arg

        assert self.PbPastePyGraf == ['pathlib.Path("/dev/stdout").write_bytes(ibytes)']

        if not py_graf:
            if pq_words == ["-"]:
                if stdin_isatty:
                    if not stdout_isatty:  # pq - |
                        pq_words = "cat -".split()  # mutates .pq_words
                    else:  # pq -
                        py_graf = self.PbPastePyGraf
                        print("+ pbpaste", file=sys.stderr)
                else:
                    if not stdout_isatty:  # |pq - |
                        pq_words = "tee >(pbcopy) | sponge".split()  # mutates .pq_words
                    else:  # |pq -
                        pq_words = "olines = ilines".split()  # mutates .pq_words
                        self.stdout_isatty = False  # mutates  # todo: ick, ugh, yuck

        # Search for one Py Graf matching the Cues (but reject many if found)

        if not py_graf:
            py_graf = self.cues_to_one_py_graf_if(cues=pq_words)  # often exits nonzero

        # Take Cues as fragments of Python, if no match found
        # todo: think more about how we temporarily lost:  pq 'olines = ilines', pq 'otext = itext'

        if not py_graf:
            if any((" " in _) for _ in pq_words):
                py_graf = list(pq_words)  # 'copied is better than aliased'
            elif len(pq_words) == 1:
                pq_word = pq_words[-1]

                if "=" not in pq_word:
                    if "iline" in py_split(pq_word):
                        py_line = f"oline = {pq_word}"  # iline.title()
                        if ("(" not in py_line) and (")" not in py_line):
                            py_line = f"oline = {pq_word}()"  # iline.title
                        py_graf = [py_line]

        # Take Cues as fragments of Rpn, if no match found

        if not py_graf:
            py_graf = self.cues_to_rpn_py_graf_if(cues=pq_words)

        # Require 1 Py Graf found

        if not py_graf:
            print(f"pq.py: No Py Grafs found by {pq_words}", file=sys.stderr)

            sys.exit(2)  # exit 2 for wrong args at No Py Graphs found

        # Compose the rest of the Python

        found_py_graf = py_graf

        (ipulls, opushes) = self.py_graf_to_i_pulls_o_pushes(py_graf)

        (complete_py_graf, importables) = self.py_graf_complete(
            py_graf, ipulls=ipulls, opushes=opushes
        )

        # Succeed

        return (found_py_graf, complete_py_graf, importables)

        # may sponge up 'self.ibytes_else', and maybe also 'self.itext_else'

    def py_graf_complete(self, py_graf, ipulls, opushes) -> tuple[list[str], list[str]]:
        """Compose the rest of the Py Code"""

        dent = 4 * " "

        # Compose more Py Code to run before and after

        before_py_graf = self.form_before_py_graf(py_graf, ipulls=ipulls, opushes=opushes)

        after_py_graf = self.form_after_py_graf(py_graf, ipulls=ipulls, opushes=opushes)

        # Take the parsed Py Code as is, or dent it

        o = (ipulls, opushes, py_graf)
        assert ("iline" in ipulls) == ("oline" in opushes), o

        run_py_graf = list(py_graf)

        if "iline" in ipulls:
            run_py_graf = list((dent + _) for _ in py_graf)

        # Stitch together the composed and the parsed, maybe dented, Py Code

        div = list([""])

        full_py_graf = before_py_graf + run_py_graf + after_py_graf
        full_py_graf = graf_deframe(full_py_graf)
        if len(full_py_graf) >= 3:
            full_py_graf = before_py_graf + div + run_py_graf + div + after_py_graf
            full_py_graf = graf_deframe(full_py_graf)

        (fuller_py_graf, importables) = py_graf_insert_imports(py_graf=full_py_graf)

        # Succeed

        return (fuller_py_graf, importables)

    def form_before_py_graf(self, py_graf, ipulls, opushes) -> list[str]:
        """Say to read Bytes or Text or neither"""

        self.py_graf_assert_ipull_to_opush(py_graf)

        #

        py_graf = list()

        self.py_graf_extend_stdinout(py_graf, ipulls=ipulls, opushes=opushes)

        if "ibytes" in ipulls:
            py_graf.extend(self.form_read_bytes_py_graf())

        py_words = "itext ilines iline iolines".split()
        if any((_ in ipulls) for _ in py_words):
            py_graf.extend(self.form_read_text_py_graf())

        py_words = "ilines iline".split()
        if any((_ in ipulls) for _ in py_words):
            py_graf.append("ilines = itext.splitlines()")

        if "iolines" in ipulls:
            py_graf.append("iolines = itext.splitlines()")

        if "oline" in opushes:
            py_graf.append("olines = list()")

        if "iline" in ipulls:
            py_graf.append("for iline in ilines:")

        #

        return py_graf

    def py_graf_extend_stdinout(self, py_graf, ipulls, opushes) -> None:
        """Say to read Stdin and write Stdout or neither or either"""

        stdin_isatty = self.stdin_isatty
        stdout_isatty = self.stdout_isatty

        if "stdout" in ipulls:
            if not stdout_isatty:
                py_graf.append("stdout = sys.stdout")
            else:
                py_graf.append("stdout = io.StringIO()")  # for |pq ts

        if "stdin" in ipulls:
            if not stdin_isatty:
                py_graf.append("stdin = sys.stdin")
            else:
                py_graf.extend(self.form_read_text_py_graf())
                py_graf.append("stdin = io.StringIO(itext)")

    def form_after_py_graf(self, py_graf, ipulls, opushes) -> list[str]:
        """Say to write Bytes or Text or neither"""

        self.py_graf_assert_ipull_to_opush(py_graf)

        dent = 4 * " "
        stdout_isatty = self.stdout_isatty

        #

        py_graf_ = list()

        if "oline" in opushes:
            py_graf_.append(dent + "olines.append(oline)")

        py_words = "olines oline".split()
        if any((_ in opushes) for _ in py_words):
            py_graf_.append(r'otext = "\n".join(olines) + "\n"')

        if "oobject" in opushes:
            py_graf_.append(r'otext = str(oobject) + "\n"')

        if "iolines" in ipulls:
            py_graf_.append(r'otext = "\n".join(iolines) + "\n"')
            py_graf_.extend(self.form_write_text_py_graf())

        if "stdout" in ipulls:
            if stdout_isatty:
                if py_graf != self.PbPastePyGraf:
                    py_graf_.append("otext = stdout.getvalue()")
                    py_graf_.extend(self.form_write_text_py_graf())

        py_words = "otext olines oline oobject".split()
        if any((_ in opushes) for _ in py_words):
            py_graf_.extend(self.form_write_text_py_graf())

        if "obytes" in opushes:
            py_graf_.extend(self.form_write_bytes_py_graf())

        #

        return py_graf_

    def form_read_bytes_py_graf(self) -> list[str]:
        """Plan to read Bytes before the chosen Py Graf"""

        stdin_isatty = self.stdin_isatty
        pbpaste_else = self.pbpaste_else

        # Number 3 Py Grafs

        bdented = """

            ibytes = pathlib.Path("/dev/stdin").read_bytes()

            irun = subprocess.run(["pbpaste"], stdout=subprocess.PIPE, check=True)
            ibytes = irun.stdout

            ipath = pathlib.Path("~/.ssh/pbpaste.bin")
            ibytes = ipath.read_bytes()

        """

        btext = textwrap.dedent(bdented).strip()
        blines = btext.splitlines()
        bgrafs = list(list(v) for k, v in itertools.groupby(blines, key=bool) if k)
        assert len(bgrafs) == 3, (len(bgrafs), bgrafs)

        # Pick 1 Py Graf

        if not stdin_isatty:
            bgraf = bgrafs[0]
        elif pbpaste_else is not None:
            bgraf = bgrafs[1]  # recklessly allows read Tty at Stdin, write Stderr
        else:
            bgraf = bgrafs[2]
            pathlib_create_pbpaste_bin()  # creates before talking of reading

        # Succeed

        return bgraf

        # chooses 1 of 3 Input Sources

    def form_read_text_py_graf(self) -> list[str]:
        """Plan to read Text before the chosen Py Graf"""

        stdin_isatty = self.stdin_isatty
        pbpaste_else = self.pbpaste_else

        # Number 3 Py Grafs

        bdented = """

            itext = sys.stdin.read()

            irun = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True)
            itext = irun.stdout

            ipath = pathlib.Path("~/.ssh/pbpaste.bin")
            itext = ipath.read_text()

        """

        btext = textwrap.dedent(bdented).strip()
        blines = btext.splitlines()
        bgrafs = list(list(v) for k, v in itertools.groupby(blines, key=bool) if k)
        assert len(bgrafs) == 3, (len(bgrafs), bgrafs)

        # Pick 1 Py Graf

        if not stdin_isatty:
            bgraf = bgrafs[0]
        elif pbpaste_else is not None:
            bgraf = bgrafs[1]  # recklessly allows read Tty at Stdin, write Stderr
        else:
            bgraf = bgrafs[2]
            pathlib_create_pbpaste_bin()  # creates before talking of reading

        # Succeed

        return bgraf

        # chooses 1 of 3 Input Sources

    def form_write_text_py_graf(self) -> list[str]:
        """Plan to write Text after the chosen Py Graf"""

        stdout_isatty = self.stdout_isatty
        pbcopy_else = self.pbcopy_else

        # Number 3 Py Grafs

        bdented = """

            try:
                sys.stdout.write(otext)
            except BrokenPipeError:
                pass

            subprocess.run(["pbcopy"], input=otext, text=True, check=True)

            opath = pathlib.Path("~/.ssh/pbpaste.bin")
            opath.write_text(otext)

        """  # todo: should Text BrokenPipeError sys.exit nonzero?

        btext = textwrap.dedent(bdented).strip()
        blines = btext.splitlines()
        bgrafs = list(list(v) for k, v in itertools.groupby(blines, key=bool) if k)
        assert len(bgrafs) == 3, (len(bgrafs), bgrafs)

        # Pick 1 Py Graf

        if not stdout_isatty:
            bgraf = bgrafs[0]
        elif pbcopy_else is not None:
            bgraf = bgrafs[1]  # recklessly allows write Stdout/ Stderr
        else:
            bgraf = bgrafs[2]
            pathlib_create_pbpaste_bin()  # creates before talking of rewriting

        # Succeed

        return bgraf

        # chooses 1 of 3 Output Sinks

    def form_write_bytes_py_graf(self) -> list[str]:
        """Plan to write Bytes after the chosen Py Graf"""

        stdout_isatty = self.stdout_isatty
        pbcopy_else = self.pbcopy_else

        # Number 3 Py Grafs

        bdented = """

            try:
                pathlib.Path("/dev/stdout").write_bytes(obytes)
            except BrokenPipeError:
                pass

            subprocess.run(["pbcopy"], input=obytes, check=True)

            opath = pathlib.Path("~/.ssh/pbpaste.bin")
            opath.write_bytes(obytes)

        """  # todo: should Bytes BrokenPipeError sys.exit nonzero?

        btext = textwrap.dedent(bdented).strip()
        blines = btext.splitlines()
        bgrafs = list(list(v) for k, v in itertools.groupby(blines, key=bool) if k)
        assert len(bgrafs) == 3, (len(bgrafs), bgrafs)

        # Pick 1 Py Graf

        if not stdout_isatty:
            bgraf = bgrafs[0]
        elif pbcopy_else is not None:
            bgraf = bgrafs[1]  # recklessly allows write Stdout/ Stderr
        else:
            bgraf = bgrafs[2]
            pathlib_create_pbpaste_bin()  # creates before talking of rewriting

        # Succeed

        return bgraf

        # chooses 1 of 3 Output Sinks

    #
    # Pick out the one Py Graf most closely matching the Sh Words
    #

    def cues_to_one_py_graf_if(self, cues) -> list[str]:
        """Pick out the nearest one Py Graf, else zero Py Grafs"""

        py_grafs = self.cues_to_py_grafs(cues=cues)
        if not py_grafs:
            py_grafs = self.emo_cues_to_py_grafs(cues=cues)

        if not py_grafs:
            return list()

        for py_graf in py_grafs:
            assert py_graf, (py_graf, cues)

        if len(py_grafs) != 1:
            print(
                f"pq.py: {len(py_grafs)} Py Grafs found, not just 1, by {cues}",
                file=sys.stderr,
            )

            for graf in py_grafs:
                print(file=sys.stderr)
                print(graf, file=sys.stderr)

            sys.exit(2)  # exit 2 for wrong args at Too Many Py Graphs found

        py_graf = py_grafs[-1]
        assert py_graf, (cues, py_grafs)

        return py_graf

        # often exits nonzero

    def cues_to_py_grafs(self, cues) -> list[list[str]]:
        """Search up popular Py Grafs"""

        cued_py_grafs = self.cued_py_grafs

        less_by_more = self.grafs_to_less_by_more(cued_py_grafs)
        py_grafs = self.dict_cues_to_py_grafs(less_by_more, cues=cues, few=True)

        return py_grafs

    def emo_cues_to_py_grafs(self, cues) -> list[list[str]]:
        """Pick out UnicodeData Lookup Prints by Cues"""

        emo_cues = "emojis emoji emo".split()
        hits = list(_ for _ in cues if _ in emo_cues)
        misses = list(_ for _ in cues if _ not in emo_cues)
        if not hits:
            return list()

        less_by_more = fetch_less_by_more_emoji_py_texts()
        dict_py_grafs = self.dict_cues_to_py_grafs(less_by_more, cues=misses, few=False)

        py_graf = list(line for py_graf in dict_py_grafs for line in py_graf)

        py_grafs = list()
        if py_graf:
            py_grafs = [py_graf]

        return py_grafs

    def dict_cues_to_py_grafs(self, less_by_more, cues, few) -> list[list[str]]:

        py_grafs_by_keepends = self.cues_to_py_grafs_by_keepends(
            cues, less_by_more=less_by_more, few=few
        )

        lesser_py_grafs = py_grafs_by_keepends[False]
        greater_py_grafs = py_grafs_by_keepends[True]

        # Forward the only Pile of Py Grafs, if only one Pile found
        # Forward the smaller Pile of Py Grafs, if two Piles found

        if lesser_py_grafs:
            if not greater_py_grafs:
                return lesser_py_grafs
            if len(lesser_py_grafs) < len(greater_py_grafs):
                return lesser_py_grafs

        if greater_py_grafs:
            if not lesser_py_grafs:
                return greater_py_grafs
            if len(greater_py_grafs) < len(lesser_py_grafs):
                return greater_py_grafs

        # Forward the Py Grafs found with arbitrarily editable Comments,
        # when just as many Py Grafs found with and without searching Comments

        o = (lesser_py_grafs, greater_py_grafs)
        if lesser_py_grafs and greater_py_grafs:
            assert len(lesser_py_grafs) == len(greater_py_grafs), o
            return greater_py_grafs

        # Otherwise say Py Grafs found

        assert not lesser_py_grafs, lesser_py_grafs
        assert not greater_py_grafs, greater_py_grafs

        return list()  # No Py Grafs found

    def grafs_to_less_by_more(self, grafs) -> dict[str, str]:
        """Fetch the Curated Grafs, but as Without-Comments indexed by With-Comments"""

        less_by_more = dict()

        for graf in grafs:
            more_text = "\n".join(graf)

            alt_graf = list(graf)
            alt_graf = list(_.partition("#")[0].rstrip() for _ in alt_graf)
            alt_graf = list(_ for _ in alt_graf if _)

            less_text = "\n".join(alt_graf)

            less_by_more[more_text] = less_text

        return less_by_more

    def cues_to_py_grafs_by_keepends(  # ) -> dict[bool, list[list[str]]]:
        self, cues, less_by_more, few
    ) -> dict[bool, list[list[str]]]:
        """Search up popular Py Grafs, by searching only in Code, or in Comments too"""

        # Try matching without Comments, and only then try again with Comments

        py_grafs_by_keepends = dict()
        for keepends in (False, True):

            # Score each Py Graf

            score_by_more_text = dict()
            for more_text, less_text in less_by_more.items():
                text = more_text if keepends else less_text

                graf = text.splitlines()
                score = self.cues_graf_score(cues, graf)
                if not few:
                    score = min(1, score)

                score_by_more_text[more_text] = score

            scores = list(score_by_more_text.values())

            # Pick out all the equally strong Matches

            py_grafs = list()

            most = max(scores)
            if most:

                for more_text in less_by_more.keys():
                    graf = more_text.splitlines()

                    score = score_by_more_text[more_text]
                    if score == most:
                        py_grafs.append(graf)

            py_grafs_by_keepends[keepends] = py_grafs

        return py_grafs_by_keepends

    def cues_graf_score(self, cues, graf) -> int:
        """Pick out which popular Py Grafs match the Keys most closely"""

        # Count up the Matches, when searching with one kind of Fuzz or another

        score_by_cue: dict[str, int]
        score_by_cue = collections.defaultdict(int)

        d0 = self.cues_graf_score_by_str_split(cues, graf=graf)
        d1 = self.cues_graf_score_by_py_split(cues, graf=graf)
        d2 = self.cues_graf_score_by_str_in(cues, graf=graf)

        for cue in cues:
            score = d0[cue] + d1[cue] + d2[cue]
            score_by_cue[cue] = score

        # Count up the Matches, when searching with one kind of Fuzz or another

        for cue in cues:
            cue_score = score_by_cue[cue]
            if not cue_score:
                return 0

        score = sum(score_by_cue.values())

        # Succeed

        return score

    def cues_graf_score_by_str_in(self, cues, graf) -> dict[str, int]:
        """Count out how often each Cue found in an unsplit Graf Line"""

        score_by_cue: dict[str, int]
        score_by_cue = collections.defaultdict(int)

        for line in graf:  # found
            casefold_line = line.casefold()

            for cue in cues:
                casefold_cue = cue.casefold()

                score_by_cue[cue] += line.count(cue)
                score_by_cue[cue] += casefold_line.count(casefold_cue)

        return score_by_cue

    def cues_graf_score_by_str_split(self, cues, graf) -> dict[str, int]:
        """Count out how often each Cue found as a Str Split in a Graf Line"""

        score_by_cue: dict[str, int]
        score_by_cue = collections.defaultdict(int)

        for line in graf:  # found in Str Word
            casefold_line = line.casefold()

            words = line.split()
            casefold_words = casefold_line.split()

            for cue in cues:
                casefold_cue = cue.casefold()

                score_by_cue[cue] += words.count(cue)
                score_by_cue[cue] += casefold_words.count(casefold_cue)

                for word in words:  # starts Str Word
                    casefold_word = word.casefold()

                    if word.startswith(cue):
                        score_by_cue[cue] += 1
                    if casefold_word.startswith(casefold_cue):
                        score_by_cue[cue] += 1

        return score_by_cue

    def cues_graf_score_by_py_split(self, cues, graf) -> dict[str, int]:
        """Count out how often each Cue found as a Py Split in a Graf Line"""

        score_by_cue: dict[str, int]
        score_by_cue = collections.defaultdict(int)

        for line in graf:  # found in Py Words
            py_words = py_split(py_text=line)
            for cue in cues:
                score_by_cue[cue] += py_words.count(cue)

                for py_word in py_words:  # starts Py Word
                    if py_word.startswith(cue):
                        score_by_cue[cue] += 1

        return score_by_cue

        # no extra points for Py Word matched when casefolded

    #
    # Take whole Input File as Cues, and fall back to ending each Line
    #

    def read_ibytes_to_one_py_graf(self, verbose) -> list[str]:
        """Take the whole Input File as Cues"""

        # Read the Bytes, as if some of the completed Py Graf already ran

        core_py_graf = self.form_read_bytes_py_graf()
        (read_py_graf, imoortables) = py_graf_insert_imports(py_graf=core_py_graf)

        read_py_text = "\n".join(read_py_graf)

        alt_locals = dict(ibytes=b"")
        exec(read_py_text, globals(), alt_locals)
        ibytes = alt_locals["ibytes"]

        self.ibytes_else = ibytes

        # End the Byte Lines and exit zero, if UTF-8 Decoding fails

        try:
            itext = ibytes.decode()
        except UnicodeDecodeError:
            py_graf = ['obytes = b"\n".join(ibytes.splitlines()) + b"\n"']

            assert verbose, (verbose,)
            print("+ pq ended", file=sys.stderr)

            return py_graf

        self.itext_else = itext

        # Take the whole Input File as Cues, if it matches one Python Graf

        py_graf_if = self.itext_to_one_pygraf_if(itext)
        if py_graf_if:

            by_cues = self.py_grafs_to_graf_by_cues([py_graf_if])
            assert by_cues, (by_cues,)
            cues_list = list(by_cues.keys())
            cues = cues_list[0]  # first wins

            assert verbose, (verbose,)
            print("+ pq " + " ".join(cues), file=sys.stderr)

            return py_graf_if

        # Else steal some time to run the Self-Tests more often

        self.assert_lots_ok()  # ~100 ms in Jun/2024

        # Fall back to end the Text Lines and exit zero

        default_py_graf = [
            r"""
                olines = ilines  # end  # ended  # ends every line with "\n"
            """.strip()
        ]

        assert verbose, (verbose,)
        print("+ pq ended", file=sys.stderr)

        return default_py_graf

        # falls back to ending each Text Line, else ending each Byte Line

    def itext_to_one_pygraf_if(self, itext) -> list[str]:
        """Take the first Py Graf that doesn't choke over the Input File"""

        ilines = itext.splitlines()

        dent = 4 * " "
        mgrafs = text_to_grafs(ITEXT_PY_GRAFS_TEXT)  # ordered, not sorted

        for mgraf in mgrafs:
            raw_py_graf = ["for iline in ilines:"] + list((dent + _) for _ in mgraf)
            (py_graf, importables) = py_graf_insert_imports(py_graf=raw_py_graf)
            py_text = "\n".join(py_graf)

            alt_locals = dict(ilines=ilines)
            try:
                for importable in importables:
                    importlib.import_module(importable)
                exec(py_text, globals(), alt_locals)
            except Exception:
                continue

            return mgraf

        return list()  # empty Py Graf

    #
    # Take Cues as fragments of Rpn
    #

    def cues_to_rpn_py_graf_if(self, cues) -> list[str]:
        """Take Cues as fragments of Rpn"""

        if cues == ["math.inf"]:
            return ["oobject = math.inf"]

        return list()  # todo: lots more Rpn


#
# Index some Alt Phrase Books
#


RPN_SCRAPS = '''  # todo: migrate/ delete

def rpn_words_to_one_py_graf(words) -> list[str]:
    """Translate to 1 Py Graf from Reverse Polish Notation (RPN)"""

    try:
        py_phrases = try_rpn_words_to_py_phrases(words)
    except Exception:
        # raise  # jitter Wed 19/Jun
        return list()

    py_graf = list()
    py_graf.append("olines = list()")
    for py_phrase in py_phrases:
        py_graf.append(f"olines.append({py_phrase})")

    return py_graf


def try_rpn_words_to_py_phrases(words) -> list:
    """Translate to 1 Py Graf from Reverse Polish Notation (RPN)"""

    stack: list
    stack = list()

    now = dt.datetime.now()
    midnight = dt.datetime.fromordinal(now.toordinal())

    # Run a Py Forth Vm once at Compile Time

    for word in words:
        m = re.match(r"([0-9]+):([0-9]+)", string=word)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2))
            stamp = midnight.replace(hour=hour, minute=minute)
            stack.append(stamp)
            continue

        if word == "-":
            x = stack.pop()
            y = stack.pop()
            stack.append(y - x)
            continue

        assert False, (word,)

    # Speak a List of Any | None as a List of Evallable Py Phrases

    py_phrases = list()

    for stacked in stack:
        py_phrase = repr(stacked)
        py_phrase = re.sub(r"\bdatetime[.]", repl="dt.", string=py_phrase)
        if not isinstance(stacked, str):
            py_phrase = f"str({py_phrase})"

        py_phrases.append(py_phrase)

    # Succeed

    return py_phrases

'''  # type ignore


VIM_SCRAPS = """  # todo: migrate/ delete

    # Else print some to Screen and edit it there

    with open("/dev/tty", "rb") as ttyin:
        fd = ttyin.fileno()
        (x_columns, y_rows) = os.get_terminal_size(fd)

    assert x_columns >= 20  # vs Mac Sh Terminal Columns >= 20
    assert y_rows >= 5  # vs Mac Sh Terminal Rows >= 5

    # todo: print the input that fits, to screen - even to last column & row
    # todo: shadow the print, then edit it
    # todo: output the shadow, at quit

    # OSError: [Errno 19] Operation not supported by device
    # OSError: [Errno 25] Inappropriate ioctl for device

"""  # type ignore


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
        prog = doc_lines[0].split()[1]  # second Word of first Line

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

        # Print Diffs & exit nonzero, when Arg Doc wrong

        diffs = self.diff_doc_vs_format_help()
        if diffs:
            print("\n".join(diffs))

            sys.exit(2)  # exit 2 for wrong Args in Main Doc

        # Print examples & exit zero, if no Sh Args

        testdoc = self.scrape_testdoc_from_epilog()
        if not sys.argv[1:]:
            print()
            print(testdoc)
            print()

            sys.exit(0)  # exit 0 after printing examples, as if after printing help

        # Drop the "--" Sh Args Separator, if present,
        # because 'ArgumentParser.parse_args()' without Pos Args wrongly rejects it

        shargs = sys.argv[1:] if (args is None) else args
        if sys.argv[1:] == ["--"]:  # ArgParse chokes if Sep present without Pos Args
            shargs = list()

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
# Amp up Import Ast
#


def black_repr(obj) -> str:
    """Form a Py Repr of an Object, but style Str and Bytes a la PyPi·Black"""

    s0 = repr(obj)

    if isinstance(obj, bytes):
        if s0.startswith("b'") and s0.endswith("'"):
            if ('"' not in s0) and ("'" not in s0):
                s1 = 'b"' + s0[1:-1] + '"'
                assert ast.literal_eval(s1) == ast.literal_eval(s0), (s1, s0)
                return s1

    if isinstance(obj, str):
        if s0.startswith("'") and s0.endswith("'"):
            if ('"' not in s0) and ("'" not in s0):
                s1 = '"' + s0[1:-1] + '"'
                assert ast.literal_eval(s1) == ast.literal_eval(s0), (s1, s0)
                return s1

    return s0

    # "can't"
    # 'a "word" spoken'
    # "a ' single quote"


def py_graf_to_pulls_pushes(py_graf) -> tuple[list[str], list[str]]:
    """Pick out Py Names bound, bound and mentioned, or only mentioned"""

    # Split each Py Line by ';' up to '#'

    alt_py_graf: list[str]
    alt_py_graf = list()  # split by ';' surfaces '; {setter} = ...'

    for py_line in py_graf:
        (py_left, _, _) = py_line.partition("#")
        py_left_lines = py_left.split(";")
        alt_py_graf.extend(_.strip() for _ in py_left_lines)

    # Visit each Py Line

    py_getters = list()
    py_setters = list()

    for py_line in alt_py_graf:

        # Work only with Source Chars obviously not in a Py Comment

        py_left = py_line.partition("#")[0]
        py_left_words = py_split(py_left)

        # Pick off each obvious Assignment to a Py Name

        py_words = list()
        for py_word in py_left_words:
            if re.match(r"^([A-Za-z_][A-Za-z0-9_]*)$", string=py_word):
                py_words.append(py_word)

        m1 = re.match(r"^ *for *([A-Za-z_][A-Za-z0-9_]*) in *.*$", string=py_line)
        m2 = re.match(r"^ *([A-Za-z_][A-Za-z0-9_]*) *= *.*$", string=py_line)
        m = m1 or m2  # todo: more test of dented pulls

        if m:
            py_setter = m.group(1)
            py_setters.append(py_setter)

            if m1:
                assert py_words[0] == "for", (py_words,)
                py_words.pop(0)

            assert py_words[0] == py_setter, (py_words,)
            py_words.pop(0)

        # Pick up each mention of a Py Name obviously not in a Py Comment

        py_getters.extend(py_words)

    ipulls = sorted(set(py_getters) - set(py_setters))
    opushes = sorted(set(py_setters) - set(py_getters))

    return (ipulls, opushes)


def py_split(py_text) -> list[str]:
    """Split a Py Text into Py Words to search up"""

    py_words = list(
        _.group(0) for _ in re.finditer(r"[a-zA-Z][a-zA-Z0-9_]*|[-.+0-9Ee]|.", string=py_text)
    )

    return py_words

    # todo: split more by the Py Rules, or even totally exactly like Py Rules
    # except don't drop Comments


def py_graf_insert_imports(py_graf) -> tuple[list[str], list[str]]:
    """Insert a paragraph of Py Imports up front"""

    # Magically know how to import a short list of Modules

    importables = list(sys.modules.keys())

    importables.append("dt")
    importables.append("json")
    importables.append("socket")
    importables.append("string")
    importables.append("subprocess")
    importables.append("urllib")
    importables.append("urllib.parse")

    importables.append("pq")

    # Take any mention of a Module Name as hint enough to import it

    div = list([""])

    py_text = "\n".join(py_graf)
    full_py_words = py_split(py_text)
    py_modules = list(_ for _ in full_py_words if _ in importables)

    import_graf = sorted(set(f"import {module}" for module in py_modules))
    for i, p in enumerate(import_graf):
        if p == "import dt":
            import_graf[i] = "import datetime as dt"
        elif p == "import urllib":
            import_graf[i] = "import urllib.parse"

    # Invite the Caller to run the Imports before Exec, to fail-fast'er and more simply

    inserted_importables = list()
    for import_line in import_graf:
        inserted_importable = import_line.split()[-1]  # 'urllib.parse'
        inserted_importables.append(inserted_importable)

    # Insert the Imports into the Py Graf

    fuller_py_graf = list(py_graf)
    if py_modules:
        fuller_py_graf = import_graf + div + py_graf

    return (fuller_py_graf, inserted_importables)


#
# Amp up Import BuiltIns
#


def list_assert_eq(a, b, occasion=None) -> None:
    """Assert A and B are equal when taken as List[Str]"""

    o = occasion

    list_a = list(a)  # narrow to List, not Tuple/ Iterator/ Dict Keys/ Dict Values/ etc
    list_b = list(b)

    strs_a = list(str(_) for _ in list_a)  # default to Str, not Repr,
    strs_b = list(str(_) for _ in list_b)  # although caller may send us Repr

    diffs = list(difflib.unified_diff(a=strs_a, b=strs_b, fromfile="a", tofile="b", lineterm=""))

    a_set = set(strs_a)
    b_set = set(strs_b)
    ao = sorted(a_set - b_set)
    bo = sorted(b_set - a_set)

    if list_a == list_b:
        return

    print("\n".join(diffs))
    assert diffs, (strs_a, strs_b, list_a, list_b)

    if len(repr(strs_a) + repr(strs_b)) > 500:
        if o is not None:
            assert not diffs, (o, len(a), len(b), len(ao), len(bo), ao, bo)
        assert not diffs, (len(a), len(b), len(ao), len(bo), ao, bo)

    if o is not None:
        assert not diffs, (o, len(a), len(b), len(ao), len(bo), ao, bo, list_a, list_b)
    assert not diffs, (len(a), len(b), len(ao), len(bo), ao, bo, list_a, list_b)

    # todo: prints and raises too much of large Diffs


#
# Amp up Import PathLib
#


def pathlib_create_pbpaste_bin() -> None:
    """Write an empty Copy-Paste Clipboard Buffer File in our usual place"""

    dirpath = pathlib.Path.home() / ".ssh"
    filepath = dirpath.joinpath("pbpaste.bin")

    if not dirpath.is_dir():  # chmod u=rwx,go= ~/.ssh
        dirpath.mkdir(stat.S_IRWXU, exist_ok=True)

    if not filepath.exists():  # chmod u=rw,go= ~/.ssh/pbpaste.bin
        filepath.touch(mode=(stat.S_IRUSR | stat.S_IWUSR), exist_ok=True)


#
# Explore working with a Terminal like Vi, Emacs, Screen, & Ssh do
#


#
# Till we paused work on Class LineTerminal
# Lots worked at:  pq em vi
#
#   Emacs  ⎋< ⎋> ⎋G⎋G ⎋GG ⎋GTab ⎋R
#   Emacs  ⌃A ⌃B ⌃D ⌃E ⌃F ⌃K ⌃N ⌃O ⌃P
#   Emacs  ⎋← ⎋→ ⌥← ⌥→ aka ⎋B ⎋F
#   Emacs  ⌥< ⌥> ⌥G⌥G ⌥GG ⌥GTab ⌥R
#
#   Vim  Return ⌃E ⌃J ⌃Y ← ↓ ↑ →
#   Vim  Spacebar $ + - 0 123456789
#   Vim  ⇧A ⇧B ⇧C ⇧D ⇧E ⇧G ⇧H ⇧I ⇧L ⇧O ⇧R ⇧S ⇧X ⇧W ^ _
#   Vim  A B E H I J K L O S W X | Delete
#   Vim  < > C D as adverbs:  << >> CC DD  C0 D0  C$ D$  <J >J CJ DJ  <K >K CK DK  etc
#
#   Pq  ⎋⎋ ⎋[ Tab ⇧Tab ⌃Q⌃V ⌃V⌃Q [ ⌥⎋ ⌥[
#   Pq  ⎋ ⌃C ⌃D ⌃G ⌃Z ⌃\ ⌃L⌃C:Q!Return ⌃X⌃C ⌃X⌃S⌃X⌃C ⇧QVIReturn ⇧Z⇧Q ⇧Z⇧Z
#   Pq  I⌃D IReturn IDelete I⌃H
#
#   Option Mouse Click moves Cursor via ← ↑ → ↓
#
#   Multiple Parallel Log Files in Sh at:  tail -F .pqinfo/*.log
#

#
# pq-vi Todo's that watch the Screen more closely
#
#   Vim . to repeat Emacs ⌃D ⌃K ⌃O or Vim > < C D
#   Vim . with Arg to repeat more than once
#
#   Work the Mouse
#       Delete/ Change up to the Mouse Click
#       Edit while Mouse-Scrolling, and doc this
#
#   Lines larger than the Screen
#
#    Mark and Select
#       Vim ⌃O ⌃I to walk the List of Marks vs which Verbs make Marks
#           Vim :jumps :clearjumps vs G G, ⇧G, { }
#           Like maybe Mouse Jump should make a Mark
#           Vim M ' makes a Mark, but maybe the other M should likewise
#       Vim M M to create Mark, Vim ' ' to bounce back and forth, Vim ' M to jump to Mark
#       Emacs ⌃W even without ⌃Y Paste Back and without the ⌃W Highlight
#
#   Bounce Cursor to a placed Status Row on Screen
#       Trace the UnicodeData.Name while Replace/ Insert
#       Delete the Message we last wrote, write the new, log Messages & lost Messages
#       Trace Y and X a la Vim :set ruler, cursorline, etc from my ~/.vimrc
#       Collapse repeated Keys into repetition count of Key, like for Turtle Graphics
#       Show the Line Marks
#
#   Relaunch
#       Emacs ⌃X X G 'revert-buffer-quick
#       Vim : E ! Return
#
#   Shadow the Screen
#
#       Insert Return from Columns between Home and End of the Line
#
#       Vim ⌃L Emacs ⌃L of Shadow Screen - mostly to redraw the Screen as shadowed
#       Vim many many jump to Dent, Emacs ⎋M jump to Dent a la Vim ^
#
#       Edit via:  pq xeditline $FILE
#       Emacs ⎋Z for like Vim D F, Vim F T ⇧F ⇧T for jump to, or jump to before
#       Emacs ⎋C ⎋L ⎋U for Title/ Lower/ Upper
#       Emacs ⌃T ⎋T and ⎋T for larger Words such as Last Two Sh Args
#
#       Undo/Redo piercing the Shadow
#       Highlight for Search Found, for Selection, for Whitespace Codes in Selection
#       Pipe through Vim !
#       Vim D A B and such, the Vim Motions that aren't Top Level Vim Motions
#
#   Files smaller than the Screen, with ⎋[m marks in them
#

#
# pq-vi Pq Fixes:
#
#   Our Vi ⇧| should leave the Buffer unchanged when Nonzero Exit Code and No Stdout
#
#   More friction vs quitting without calling ⎋⇧M or ⎋⇧L K etc to keep the lower Rows of the Screen
#
#   Surprise of ⌃X ⌃S moving on already inside ⌃X ⌃E, not waiting for ⌃X ⌃S ⌃X ⌃C
#
#   ⌃X ⌃E Launch irretrievably confused by Zsh placing the Cursor in any Column of Input?
#

#
# pq-vi More Todo's:
#
#   Multiple Screens across Terminals or inside one Terminal
#   Multiple Keyboards across Terminals, even cross Guests
#
#   Emacs ⌃W ⌃Y Copy/Paste Buffer vs Os Copy/Paste Buffer
#
#   Emacs ⌃R ⌃S Searches
#
#   Vim presentations of :set cursorline, etc from my ~/.vimrc
#   More obscure Key Chord Sequences of Vim & Emacs
#   Emacs ideas from my ~/.emacs, Vim ideas from my ~/.vimrc
#   Emacs ⌃C A..Z Name Space, Emacs ⎋N ⎋O ⎋P Name Space, Vim \ A..Z Name Space
#
#   Screens of Files
#

#
# pq-vi Todo's that take Keyboard Input
#
#   Logo Turtle Ascii-Graphics
#
#   Vim Q Q @ Q etc, with repetition of @ Q
#   Vim . could learn to repeat @ Q, and the other @ x, while ⌃Q . more faithful to legacy
#
#   Pq I ⌃Q ⌃O Escape
#   Pq I ⌃Q ⌃O Calls of Insert/ Replace that don't move the Cursor Left
#   Pq I ⌃Q ⌃O ⌃O and Pq I ⌃Q ⌃O ⌃I Cursor Histories
#
#   Pq ⌃Q escape to Vim ⌃D ⌃G ⌃L etc
#   Pq ⌃V escape to Emacs ⌃L ⌃V ⌃W ⌃Y etc
#
#   Emacs insert-char of Py unicodedata.lookup
#
#   Chose ⌃H⌃K inside Texts/ Verbs
#       Refactor Texts_Wrangle & Verb_Eval to form a (KBytes, KCap_Str, Py_Call)
#       Print ⌃H⌃K as all three of (KBytes, KCap_Str, Py_Call)
#
#   Revert to Ex Mode to do ⌃H⌃A
#       Take a line of input as literal ignoring case
#           but "..." or '...' to respect case, except auto-close the " or '
#           and take r"...' or r'...' to do Py RegEx for which to hit
#       Do the reverse-lookup to find (KBytes, KCap_Str, Py_Call)
#           not only Py Func
#

#
# Review these and retire what we've got
#
#   Vim  Return ⌃E ⌃J ⌃Y ← ↓ ↑ →
#   Vim  Spacebar $ + - 0 123456789 << >>
#   Vim  ⇧A ⇧B ⇧C ⇧D ⇧E ⇧G ⇧H ⇧I ⇧L ⇧O ⇧R ⇧S ⇧X ⇧W ^ _
#   Vim  A B C$ CC C⇧G C⇧L D$ DD D⇧G D⇧L E H I J K L O S W X | Delete
#
#   Pq  ⎋⎋ ⎋[ Tab ⇧Tab ⌃Q⌃V ⌃V⌃Q [ ⌥⎋ ⌥[
#   Pq  ⎋ ⌃C ⌃D ⌃G ⌃Z ⌃\ ⌃L⌃C:Q!Return ⌃X⌃C ⌃X⌃S⌃X⌃C ⇧QVIReturn ⇧Z⇧Q ⇧Z⇧Z
#   Pq  I⌃D IReturn IDelete I⌃H
#

#
# pq-vi Python ToDo's
#
#   Refactor to solve the various No-Q-A C901 Too-Complex
#
#   Asserts for Terminal Encoding to top of Def, never ducked by conditional Return
#
#   Define present work in terms of y_line, x_char,
#       no longer only in terms of y_row, x_column,
#           even while today's y_row == y_line, and today's x_column == x_char
#
#   More convergence between 'pq xeditline' and 'pq em vi'
#   More divergence between 'pq vi' and 'pq em'
#
#   Python Callback Hook for entry/ exit into waiting for Keyboard Input
#       Clean up my tangle involving:  kmap_at_ltlaunch_lt_func
#
#   Python Decorators to build Keymap's, guarantee Positive Int Arg, etc
#


r'''

def xeditline() -> list[str]:
    """Edit in the way of Zsh/ Bash Command-Line Editor"""

    assert len(sys.argv) == 3, (len(sys.argv), sys.argv)
    assert sys.argv[1] == "xeditline", (sys.argv[1], sys.argv)

    # Fetch a copy of the Command Line spelled out but not auth'ed

    pathname = sys.argv[2]
    path = pathlib.Path(pathname)
    ilines = path.read_text().splitlines()  # not the 'pbpaste'

    # Guess what $PS1 printed by the Zsh/Bash $EDITOR ⌃X⌃E Api before calling us

    ps1 = "$ " if os.getuid() else "# "
    ps4 = "+ "

    env_shell = os.environ["SHELL"]
    bashing = os.path.basename(env_shell) == "bash"

    def xedit_at_ltlaunch_lt_func(lt) -> None:

        olines = lt.olines
        st = lt.st

        rn_otext = "\r\n".join(olines)

        if bashing:
            st.str_write("\x1B[A" + ps1 + "# " + "\r\n")
            st.str_write(ps1)
        else:
            pn = len(rn_otext)
            st.str_write_form_or_form_pn("\x1B" "[" "{}D", pn=pn)

        st.str_write("\x1B[1m")
        st.str_write(rn_otext)

        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left

    # Print & edit the input

    path.write_text("")

    lt = LineTerminal()
    lt.pqprint(f"{pathname=}")
    olines = lt.run_till_quit(ilines, kmap="Pq", at_ltlaunch_lt_func=xedit_at_ltlaunch_lt_func)

    if olines:
        otext = "\n".join(olines) + "\n"
        path.write_text(otext)

    sys.stdout.write("\x1B[m")
    if bashing:
        if not olines:
            sys.stdout.write("\r" + ps1 + "\x1B[K" + "\r\n")
        else:
            sys.stdout.write("\r\n" + ps4)
    sys.stdout.flush()

    # Succeed

    return olines


def ex_macros(ilines) -> list[str]:
    """Edit in the way of Emacs"""

    print("'pq em' presently doesn't work, we have only:  pq st")

    olines = kmap_lt_run_till_quit(ilines, kmap="Emacs")

    return olines


def visual_ex(ilines) -> list[str]:
    """Edit in the way of Ex Vim"""

    print("'pq vi' presently doesn't work, we have only:  pq st")

    olines = kmap_lt_run_till_quit(ilines, kmap="Vim")

    return olines


def kmap_lt_run_till_quit(ilines, kmap) -> list[str]:
    """Edit in the way of Emacs or Vim"""

    alt_ilines = list(ilines)
    alt_ilines.append("")  # todo: auto-closing the last Line of Input for Emacs

    def kmap_at_ltlaunch_lt_func(lt) -> None:

        olines = lt.olines
        st = lt.st

        st.str_write("\r\n".join(olines))

        st.str_print()
        if kmap == "Emacs":
            st.str_print("Press ⌃G ⌃X ⌃C to quit")
        else:
            st.str_print("Press ⌃C ⇧Z ⇧Q to quit")

    lt = LineTerminal()
    olines = lt.run_till_quit(alt_ilines, kmap=kmap, at_ltlaunch_lt_func=kmap_at_ltlaunch_lt_func)

    if alt_ilines == olines:
        print("save-quit")
    else:
        print("quit-no-save")

    return olines


def bytes_terminal_yolo(ibytes) -> bytes:  # bt yolo
    """Read Bytes from Keyboard, Write Bytes or Repr Bytes to Screen"""

    with BytesTerminal() as bt:
        bt.bytes_yolo()

    return b""


def shadow_terminal_yolo(itext) -> str:  # st yolo
    """Read Bytes from Keyboard, Write Bytes or Repr Bytes to Screen"""

    with ShadowsTerminal() as st:
        st.shadows_yolo(brittle=False)

    return ""


def turtle_yolo(itext) -> str:  # turtle

    module = sys.modules[__name__]
    assert module.w_open_else is None, (w_open_else, module)

    hostname = platform.node()
    debug = hostname.startswith("plavarre")

    turtling = False
    if not os.path.exists("stdin.mkfifo"):
        if debug:
            setattr(module, "w_open_else", open("pq.turtle.client.log", "a"))
        mkfifo_pathnames = ["stdin.mkfifo"]
    elif not os.path.exists("stdout.mkfifo"):
        if debug:
            setattr(module, "w_open_else", open("pq.turtle.server.log", "a"))
        mkfifo_pathnames = ["stdout.mkfifo"]
        turtling = True
    else:
        if debug:
            setattr(module, "w_open_else", open("pq.turtle.client.log", "a"))
        os.remove("stdin.mkfifo")
        os.remove("stdout.mkfifo")
        mkfifo_pathnames = ["stdin.mkfifo"]

    for pathname in mkfifo_pathnames:
        os.mkfifo(pathname)

    try:
        if not turtling:
            tc = TurtleClient()
            tc.turtle_client_yolo()
        else:
            print("\x1B[?25h")  # 06/08 Set Mode (SMS) 25 VT220 DECTCEM
            try:
                with ShadowsTerminal() as st:
                    st.shadows_yolo(brittle=True)
            finally:
                print("\x1B[?25h")  # 06/08 Set Mode (SMS) 25 VT220 DECTCEM
    finally:
        for pathname in mkfifo_pathnames:
            os.remove(pathname)

    return ""
'''


def turtle_yolo(itext) -> str:  # turtle

    text = """

        Find a good way to download:  bin/turtling.py
        Run it twice.  Once in one Terminal Window, once in another
        It should work.  Please tell us if it doesn't work

    """

    text = textwrap.dedent(text).strip() + "\n"

    sys.stderr.write(text)

    return text


r'''
@dataclasses.dataclass
class ShadowsTerminal:
    """Write/ Read Chars at Screen/ Keyboard of a Monospaced Square'ish Terminal"""

    bt: BytesTerminal
    ck: ChordsKeyboard
    tmode: str  # 'Meta'  # 'Replace'  # 'Insert'

    #
    # Init, enter, exit, yolo self-test
    #

    def __init__(self) -> None:

        bt = BytesTerminal()

        self.bt = bt
        self.ck = ChordsKeyboard(bt)
        self.tmode = "Replace"  # technically unknown, often 'Meta'

    def shadows_yolo(self, brittle) -> None:  # noqa C901 too complex  # bin/pq.py styolo
        """Read Bytes from Keyboard, Write Bytes or Repr Bytes to Screen"""

        st = self
        kstr_list = self.ck.kstr_list
        assert self.bt.tcgetattr_else, (self.bt.tcgetattr_else,)

        # Set up this Loop

        if not brittle:

            st.str_print("Let's test Class ShadowsTerminal")
            st.str_print("Press ⎋ Fn ⌃ ⌥ ⇧ ⌘ and Spacebar Tab Return and ← ↑ → ↓ and so on")
            st.str_print("Press ⌃L to count Rows and Columns and say where the Cursor is")
            st.str_print("Press ⌃C ⇧R to replace, ⌃C I to insert, ⌃C ⇧Z ⇧Q to quit")

            st.str_print()
            st.str_print()

        # Run this Loop  # todo: option to start with Meta, would it be:  kchord = (b"", "")

        kchord = (b"R", "⇧R")

        tmode = "Meta"
        while True:
            (kbytes, kstr) = kchord

            if kstr == "⌃L":  # ⌃L Rewrite

                file = io.StringIO()
                st.ck.read_y_rows_x_columns(timeout=1, file=file)
                st.ck.read_row_y_column_x(timeout=1, file=file)
                sys.stderr.write(file.getvalue())

                if tmode == "Replace":
                    st.str_write_tmode_replace()
                    kchord = st.read_past_text_kchords(timeout=1)
                elif tmode == "Insert":
                    st.str_write_tmode_insert()
                    kchord = st.read_past_text_kchords(timeout=1)
                else:
                    kchord = st.ck.read_kchord_despite_kcprs(timeout=1)

            elif kstr == "⇧R":  # ⇧R Replace
                tmode = "Replace"

                st.str_write_tmode_replace()
                kchord = st.read_past_text_kchords(timeout=1)

            elif kstr == "I":  # I Insert
                tmode = "Insert"

                st.str_write_tmode_insert()
                kchord = st.read_past_text_kchords(timeout=1)

            else:
                tmode = "Meta"

                st.str_write_tmode_meta()
                st.str_meta_write(kstr)

                kchord = st.ck.read_kchord_despite_kcprs(timeout=1)

            if brittle:
                if kstr_list[-1:] == ["⌃D"]:
                    (kbytes, kstr) = kchord
                    st.str_meta_write(kstr)
                    break

            if kstr_list[-2:] == ["⇧Z", "⇧Q"]:
                (kbytes, kstr) = kchord
                st.str_meta_write(kstr)
                break

        st.str_print()

        # st.str_print(st.bt.kbytes_list)
        # st.str_print(st.bt.sbytes_list)

    def read_past_text_kchords(self, timeout) -> tuple[bytes, str]:
        """Read Text K Chords and write their Bytes, return the first other K Chord"""

        assert CPR_Y_X_REGEX == r"^\x1B\[([0-9]+);([0-9]+)R$"  # CSI 05/02 CPR

        while True:
            alt_kchord = self.ck.read_kchord_despite_kcprs(timeout=timeout)

            kchord = alt_kchord
            if alt_kchord == (b"\x7F", "Delete"):
                kchord = (b"\x08", "Backspace")

            (kbytes, kstr) = kchord
            schars = kbytes.decode()  # rarely raises UnicodeDecodeError

            if self.str_write_if(schars):
                continue

            writable = self.schars_to_writable(schars)
            if not writable:
                break

            self.str_write(schars)

        return kchord

    def str_write_if(self, schars) -> bool:
        """Say if called BytesTerminal to emulate writing Screen Chars"""

        bt = self.bt

        assert DECIC_X == "\x1B" "[" "{}'}}"  # CSI 02/07 07/13 DECIC_X  # "}}" to mean "}"
        assert DECDC_X == "\x1B" "[" "{}'~"  # CSI 02/07 07/14 DECDC_X

        if not schars.startswith("\x1B["):
            return False

        if schars.endswith("'}"):
            digits = schars[len("\x1B[") : -len("'}")]
            n = int(digits) if digits else 1
            bt.columns_insert_n(n)
            return True

        if schars.endswith("'~"):
            digits = schars[len("\x1B[") : -len("'~")]
            n = int(digits) if digits else 1
            bt.columns_delete_n(n)
            return True

        return False


    #
    # Write Bytes to jump the Cursor
    #

    def x_column_write_if(self, x_column) -> None:
        """Jump the Cursor to a new Column, else nop"""

        assert CHA_Y == "\x1B" "[" "{}G"  # CSI 04/07 Cursor Character Absolute  # "\r" is Pn 1

        column = self.ck.column_x != x_column
        if column:
            self.str_write_form_or_form_pn("\x1B" "[" "{}G", pn=x_column)
            self.ck.column_x_report(x_column)

    def y_row_write_if(self, y_row) -> None:
        """Jump the Cursor to a new Row, else nop"""

        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

        row = self.ck.row_y != y_row
        if row:
            self.str_write_form_or_form_pn("\x1B" "[" "{}d", pn=y_row)
            self.ck.row_y_report(y_row)

    def y_x_row_column_write_if(self, row_y, column_x) -> None:
        """Jump the Cursor to a new Row & Column, else nop"""

        assert CHA_Y == "\x1B" "[" "{}G"  # CSI 04/07 Cursor Character Absolute  # "\r" is Pn 1
        assert CUP_Y_X == "\x1B" "[" "{};{}H"  # CSI 04/08 Cursor Position (CUP)
        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

        row = self.ck.row_y != row_y
        column = self.ck.column_x != column_x

        if row and column:
            form = "\x1B" "[" "{};{}H"
            schars = form.format(row_y, column_x)
            self.str_write(schars)
            self.ck.row_y_column_x_report(row_y, column_x=column_x)
            return

        if row:
            self.str_write_form_or_form_pn("\x1B" "[" "{}d", pn=row_y)
            self.ck.row_y_report(row_y)
            return

        if column:
            self.str_write_form_or_form_pn("\x1B" "[" "{}G", pn=column_x)
            self.ck.column_x_report(column_x)
            return

    #
    # Write Chars or Bytes
    #

    def str_write_form_or_form_pn(self, form, pn, default=1) -> None:
        """Write a CSI Form to the Screen filled out by the Digits of the K Int"""

        assert "{}" in form, (form,)
        if pn != default:
            assert pn >= 1, (pn,)

        if pn == default:
            schars = form.format("")
        else:
            schars = form.format(pn)

        self.str_write(schars)

    def str_write(self, schars) -> None:
        """Write Chars to the Screen, but without implicitly also writing a Line-End"""

        self.str_print(schars, end="")

        # 'st.str_write("\r\n")' and 'st.str_print()' write the same Bytes

    def str_print(self, *args, end="\r\n") -> None:
        """Write Chars to the Screen as one or more Ended Lines"""

        bt = self.bt

        sep = " "
        join = sep.join(str(_) for _ in args)

        sbytes = join.encode()
        ebytes = end.encode()

        bt.bytes_print(sbytes, end=ebytes)

    #
    # Write Bytes to switch between Replace/ Insert/ Meta
    #

    def str_meta_write(self, schars) -> None:
        """Write Chars to the Screen, but don't shadow them, and don't insert them"""

        tmode = self.tmode
        assert tmode in ("Insert", "Meta", "Replace"), (tmode,)

        self.str_tmode_write_if("Meta")  # not "Insert"
        self.str_write(schars)
        self.str_tmode_write_if(tmode)

    def str_tmode_write_if(self, tmode) -> None:
        """Write Bytes to switch between Replace/ Insert/ Meta only if not written already"""

        assert tmode in ("Insert", "Meta", "Replace"), (tmode,)
        assert self.tmode in ("Insert", "Meta", "Replace"), (self.tmode,)

        if self.tmode != tmode:
            self.str_tmode_write(tmode)

    def str_tmode_write(self, tmode) -> None:
        """Write Bytes to switch between Replace/ Insert/ Meta"""

        func_by_tmode = dict(
            Replace=self.str_write_tmode_replace,
            Insert=self.str_write_tmode_insert,
            Meta=self.str_write_tmode_meta,
        )

        func = func_by_tmode[tmode]
        func()

    def str_write_tmode_insert(self) -> None:
        """Shape the Cursor to say Insert in progress"""

        tmode = self.tmode
        assert tmode in ("Insert", "Meta", "Replace"), (tmode,)

        self.tmode = "Insert"

        if tmode != "Insert":
            self.str_write("\x1B" "[" "4h")  # CSI 06/08 4 Set Mode Insert/ Replace
            self.str_write("\x1B" "[" "6 q")  # CSI 02/00 07/01  # 6 Bar Cursor

        assert SM_IRM == "\x1B" "[" "4h"  # CSI 06/08 Set Mode Insert/ Replace
        assert DECSCUSR_BAR == "\x1B" "[" "6 q"  # CSI 02/00 07/01  # 6 Bar Cursor

    def str_write_tmode_meta(self) -> None:
        """Shape the Cursor to say no Replace/ Insert in progress"""

        tmode = self.tmode
        assert tmode in ("Meta", "Insert", "Replace"), (tmode,)

        self.tmode = "Meta"

        if tmode == "Insert":
            self.str_write("\x1B" "[" "4l")  # CSI 06/12 Replace
        if tmode != "Meta":
            self.str_write("\x1B" "[" " q")  # CSI 02/00 07/01  # No-Style Cursor

        assert RM_IRM == "\x1B" "[" "4l"  # CSI 06/12 Reset Mode Replace/ Insert
        assert DECSCUSR == "\x1B" "[" " q"  # CSI 02/00 07/01  # '' No-Style Cursor

    def str_write_tmode_replace(self) -> None:
        """Shape the Cursor to say Replace in progress"""

        tmode = self.tmode
        assert tmode in ("Insert", "Meta", "Replace"), (tmode,)

        self.tmode = "Replace"

        if tmode == "Insert":
            self.str_write("\x1B" "[" "4l")  # CSI 06/12 Replace
        if tmode != "Replace":
            self.str_write("\x1B" "[" "4 q")  # CSI 02/00 07/01  # 4 Skid Cursor

        assert RM_IRM == "\x1B" "[" "4l"  # CSI 06/12 Reset Mode Replace/ Insert
        assert DECSCUSR_SKID == "\x1B" "[" "4 q"  # CSI 02/00 07/01  # 4 Skid Cursor


class LineTerminal:
    def pqprint(self, *args, **kwargs) -> None:
        pass

    def run_till_quit(self, ilines, kmap, at_ltlaunch_lt_func) -> list[str]:
        return list()
'''

r'''

@dataclasses.dataclass
class StrTerminal:
    """Write/ Read Chars at Screen/ Keyboard of the Terminal"""

    bt: BytesTerminal  # wrapped here

    at_stlaunch_func_else: typing.Callable | None  # runs when Terminal Cursor first found

    kpushes: list[tuple[bytes, str]]  # cached here
    kpulls: list[tuple[bytes, str]]  # records Input, as an In-Memory KeyLogger

    def str_breakpoint(self) -> None:
        r"""Breakpoint with line-buffered Input and \n Output taken to mean \r\n, etc"""

        self.__exit__()
        breakpoint()  # to step up the call stack:  u
        self.__enter__()

    def str_flush(self) -> None:
        """Flush Screen Output, like just before blocking to read Keyboard Input"""

        self.bt.bytes_flush()

    def str_stop(self) -> None:
        """Suspend and resume this Screen/ Keyboard Terminal Process"""

        self.bt.bytes_stop()

    #
    # Jump the Cursor to chosen Columns and Rows of the Screen
    #

    def column_x_write_1(self) -> None:
        """Jump to Leftmost Screen Column"""

        self.column_x = 1
        self.str_write("\r")  # 00/13  # "\x0D"

        assert CR == "\r"  # 00/13 Carriage Return (CR) ⌃M

    def column_x_write_dent(self) -> None:
        """Jump to first non-blank Screen Column, else to Leftmost"""

        self.column_x_write_1()  # todo: Vim Shadow lands past Dent

    def column_x_write(self, column_x) -> None:
        """Jump to Screen Column at Left up from 1, else at Right down from -1"""

        assert column_x, (column_x,)

        x = min(column_x, self.x_columns)
        if column_x < 0:
            x = self.x_columns + 1 + column_x  # could code as Rightmost + Left
            x = max(x, 1)

        self.column_x = x
        self.str_write_form_or_form_pn("\x1B" "[" "{}G", pn=x)

        assert CHA_Y == "\x1B" "[" "{}G"  # 04/07 Cursor Character Absolute

    def row_y_write(self, row_y) -> None:
        """Jump to Screen Row at Top down from 1, else at Bottom up from -1"""

        assert row_y, (row_y,)

        y = min(row_y, self.y_rows)
        if row_y < 0:
            y = self.y_rows + 1 + row_y  # could code as Bottom + Up
            y = max(y, 1)

        self.row_y = y
        self.str_write_form_or_form_pn("\x1B" "[" "{}d", pn=y)

        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

    def row_y_column_x_write(self, row_y, column_x) -> None:
        """Jump to Screen Row and Column"""

        assert row_y, (row_y,)
        assert column_x, (column_x,)

        y = min(row_y, self.y_rows)  # todo: test large neg/pos 'row_y'
        if row_y < 0:
            y = self.y_rows + 1 + row_y  # could code as Bottom + Up
            y = max(y, 1)

        x = min(column_x, self.x_columns)  # todo: test large neg/pos 'x_columns'
        if column_x < 0:
            x = self.x_columns + 1 + column_x  # could code as Rightmost + Left
            x = max(x, 1)

        self.y_row = y
        self.x_column = x

        form = "\x1B" "[" "{};{}H"
        schars = form.format(y, x)
        self.str_write(schars)

        assert CUP_Y_X == "\x1B" "[" "{};{}H"  # CSI 04/08 Cursor Position (CUP)

    #
    # Jump the Screen Cursor ahead, or back, across the Chars of Ragged Lines
    #

    def index_yx_plus(self, distance) -> tuple[int, int]:
        """Say which Y X is at the chosen Distance away from present Y X"""

        x_columns = self.x_columns
        y_rows = self.y_rows

        column_x = self.column_x
        row_y = self.row_y
        tmode = self.tmode

        # Measure the width of each Line

        assert x_columns >= 1, (x_columns,)
        x_width = (x_columns - 1) if (tmode == "Meta") else x_columns

        # Find the Terminal Cursor as a Char of Lines

        assert row_y >= 1, (row_y,)
        yx_index = ((row_y - 1) * x_width) + column_x

        # Step the Cursor ahead or back, across Chars of Ragged Lines

        alt_yx_index = yx_index + distance
        alt_yx_index = max(alt_yx_index, 1)

        alt_y = 1 + ((alt_yx_index - 1) // x_width)
        if alt_y <= y_rows:
            alt_x = 1 + ((alt_yx_index - 1) % x_width)
        else:
            alt_y = y_rows
            alt_x = x_width

        # Succeed

        return (alt_y, alt_x)


PY_CALL = (
    tuple[typing.Callable] | tuple[typing.Callable, tuple] | tuple[typing.Callable, tuple, dict]
)


@dataclasses.dataclass
class LineTerminal:
    """React to Sequences of Key Chords by laying Chars of Lines over the Screen"""

    pqlogger: ReprLogger  # wrapped here  # '.pqinfo/pq.log'  # logfmt

    st: StrTerminal  # wrapped here

    olines: list[str]  # the Lines to sketch

    kbytes: bytes  # the Bytes of the last Key Chord
    kcap_str: str  # the Str of the KeyCap Words of the last Key Chord

    kstr_starts: list[str]  # []  # ['⌃U']  # ['⌃U', '-']  # ['⌃U', '⌃U']  # ['1', '2']
    kstr_stops: list[str]  # []  # ['⎋'] for any of ⌃C ⌃G ⎋ ⌃\
    ktext: str

    kmap: str  # ''  # 'Emacs'  # 'Vim'
    vmodes: list[str]  # ''  # 'Replace'  # 'Insert'

    #
    # Init, breakpoint, flush, and run till quit
    #

    def __init__(self) -> None:

        self.pqlogger = ReprLogger(".pqinfo/pq.log")

        self.st = StrTerminal()

        self.olines = list()

        self.kbytes = b""
        self.kcap_str = ""

        self.kstr_starts = list()
        self.kstr_stops = list()
        self.ktext = ""  # .__init__

        self.kmap = "Pq"
        self.vmodes = ["Meta"]

        # lots of empty happens only until first Keyboard Input

    def pqprint(self, *args, **kwargs) -> None:
        """Print to the PQ Logger, and to the Screen"""

        print(*args, **kwargs, file=self.pqlogger.logger)

    def line_breakpoint(self) -> None:
        r"""Breakpoint with line-buffered Input and \n Output taken to mean \r\n, etc"""

        self.line_flush()

        self.st.__exit__()
        breakpoint()  # to step up the call stack:  u
        self.st.__enter__()

    def line_flush(self) -> None:
        """Run just before blocking to read Keyboard Input"""

        self.pqlogger.logger.flush()  # todo: skipped by uncaught Exception's
        self.st.str_flush()

    def run_till_quit(self, ilines, kmap, at_ltlaunch_lt_func) -> list[str]:
        """Run till SystemExit, and then return the edited Lines"""

        st = self.st

        # Register Callback to print Input Text, when Terminal Size & Cursor first found

        assert at_ltlaunch_lt_func is not None
        lt = self

        def lt_at_stlaunch_func() -> None:
            at_ltlaunch_lt_func(lt)

        assert st.at_stlaunch_func_else is None, (st.at_stlaunch_func_else,)
        st.at_stlaunch_func_else = lt_at_stlaunch_func

        # Load up Lines to edit

        assert kmap in ("Emacs", "Pq", "Vim"), (kmap,)
        self.kmap = kmap  # K-Map Hint kept here, but never yet branched on

        olines = self.olines
        olines.extend(ilines)

        # Wrap around a StrTerminal wrapped around a ByteTerminal

        st.__enter__()
        try:
            self.run_while_true()
        except SystemExit:
            pass
        finally:
            st.__exit__()

        return olines

    def run_while_true(self) -> None:
        """Run in a StrTerminal on a BytesTerminal, till SystemExit"""

        try:
            self.texts_vmode_wrangle("Replace", kint=1)  # as if Vim +:startreplace
            self.verbs_wrangle()  # as if Vim +:stopinsert, not Vim +:startinsert
        except SystemExit as exc:
            if exc.code:
                raise

    #
    # Wrangle Text
    #

    def texts_vmode_wrangle(self, vmode, kint) -> str:
        """Enter Replace/ Insert V-Mode, Wrangle Texts, then exit V-Mode"""

        assert vmode in ("Insert", "Meta", "Replace", "Replace1"), (vmode,)
        assert vmode != "Meta", (vmode,)

        st = self.st

        self.vmode_enter(vmode)

        ktext = self.texts_wrangle()
        self.pqprint(f"{ktext=}")

        if kint > 1:
            kint_minus = kint - 1
            st.str_write(kint_minus * ktext)  # for .texts_vmode_wrangle Replace/ Insert

        self.vmode_exit()

        return ktext

        # returns just 1 copy of the .ktext  # not a catenated .kint * .ktext

    def texts_wrangle(self) -> str:
        """Take Input as Replace Text or Insert Text, till ⌃C, or ⎋, etc, or 'Replace1' Mode"""

        kstr_starts = self.kstr_starts
        kstr_stops = self.kstr_stops

        vmode = self.vmodes[-1]
        assert vmode, (vmode,)
        assert vmode in ("Insert", "Meta", "Replace", "Replace1"), (vmode,)
        assert vmode != "Meta", (vmode,)

        # Replace till 'Replace1' Mode

        self.ktext = ""  # entry into .texts_wrangle
        index = 0
        while True:
            index += 1

            if index == 2:
                if vmode == "Replace1":
                    break

            # Replace till till ⎋ or ⌃C

            self.screen_print()

            # Read 1 Short Text, or Whole Control, Key Chord Sequence,
            # or raise UnicodeDecodeError

            (kbytes, kchars, kcap_str) = self.one_else_some_kchords_read(vmode)

            textual = self.kchars_are_textual(kchars, kcap_str=kcap_str, kstr_starts=kstr_starts)

            # Exit Replace/ Insert Mode on request

            kstr_stops.clear()

            assert STOP_KCAP_STRS == ("⌃C", "⌃G", "⌃L", "⎋", "⌃\\")
            if not textual:
                if kcap_str in ("⌃C", "⌃G", "⌃L", "⎋", "⌃\\"):
                    kstr_stops.append(kcap_str)  # like for ⎋[1m
                    break

            # Take unprintable K Chars as Verbs,
            # and sometimes take - 0 1 2 3 4 5 6 7 8 9 as more K Start's

            if not textual:
                self.kchords_eval(vmode)  # for .texts_wrangle untextuals
                continue

            # Take the printable K Chars as Text Input,
            # sometimes amplified with a KInt from ⌃U -? [0-9]+ ⌃U

            assert textual, (textual,)

            ktext = self.kdo_text_write_n()  # for .texts_wrangle textuals
            self.ktext += ktext  # .texts_wrangle of Textual K Chars

        return self.ktext

    def kchars_are_textual(self, kchars, kcap_str, kstr_starts) -> bool:
        """Say to take the K Chars as Text, else not"""

        # Take Unprintable K Chars as a Verb

        if not kchars.isprintable():
            return False

        # Take a next K Start as a Verb continuing already open K Starts

        kstarts_closed = kstr_starts[1:][-1:] == ["⌃U"]
        if kstr_starts and not kstarts_closed:
            if kcap_str in list("-0123456789"):
                return False

        # Take a not-so-textual K Start as a Verb opening or continuing K Starts

        if len(kcap_str) == 2:  # todo: custom overrides of 'str.isprintable'
            if kcap_str.startswith("⎋"):
                if kcap_str[-1] in list("-0123456789"):
                    return False

                    # but don't do this for kcap_str.startswith("⌥")

        # Take the K Cap Seqs that call for Quoting Input as Verbs

        if kcap_str in ["⌥[", "⎋["]:
            return False

        # Else take the K Cap Seq as carrying K Chars as Text

        return True

    def vmode_enter(self, vmode) -> None:
        """Take Input as Replace Text or Insert Text or Meta, till Exit"""

        vmodes = self.vmodes

        assert vmode in ("Insert", "Meta", "Replace", "Replace1"), (vmode,)
        vmodes.append(vmode)

        self.vmode_write(vmode)

    def vmode_exit(self) -> None:
        """Undo 'def vmode_enter'"""

        vmodes = self.vmodes

        vmodes.pop()
        vmode = vmodes[-1]

        self.vmode_write(vmode)

    def vmode_write(self, vmode) -> None:  # for .vmode_exit or .vmode_enter
        """Redefine StrTerminal Write as Replace or Insert, & choose a Cursor Style"""

        st = self.st

        assert vmode in ("Insert", "Meta", "Replace", "Replace1"), (vmode,)
        self.pqprint(f"{vmode=}")

        if vmode == "Replace1":
            st.str_tmode_write("Replace")
        else:
            st.str_tmode_write(tmode=vmode)

    #
    # Wrangle Verbs
    #

    def verbs_wrangle(self) -> list[str]:
        """Read & Eval & Print in a loop till SystemExit"""

        vmode = self.vmodes[-1]
        assert vmode == "Meta", (vmode,)

        while True:
            self.screen_print()
            self.some_kchords_read()  # for .verbs_wrangle
            self.kchords_eval(vmode="Meta")  # for .verbs_wrangle

    def screen_print(self) -> None:
        """Speak after taking Key Chord Sequences as Commands or Text"""

        pass  # todo: do more inside 'def screen_print'

    #
    # Read KChords
    #

    def one_else_some_kchords_read(self, vmode) -> tuple[bytes, str, str]:
        """Read 1 KChord of Text, else a Whole KChord Sequence of 1 or more KChords"""

        kstr_starts = self.kstr_starts
        kstr_stops = self.kstr_stops

        # Read the Head of the Sequence

        if not kstr_starts:
            self.one_kchord_read()  # for .texts_wrangle Replace/ Insert
        else:
            self.some_kchords_read()  # for .texts_wrangle while .kstr_starts

        kbytes = self.kbytes
        kchars = kbytes.decode()  # may raise UnicodeDecodeError
        kcap_str = self.kcap_str

        # Read the Tail of the Sequence when the Head isn't printable

        if not kchars.isprintable():
            self.tail_kchords_read(kbytes, kcap_str=kcap_str)

            kbytes = self.kbytes
            kchars = kbytes.decode()  # may raise UnicodeDecodeError
            kcap_str = self.kcap_str

        self.pqprint(f"{kcap_str=} {kbytes=} {vmode=} {kstr_starts=} {kstr_stops=}")

        return (kbytes, kchars, kcap_str)

        # may raise UnicodeDecodeError

    def one_kchord_read(self) -> None:
        """Read 1 Key Chord, as Bytes and Str"""

        (kbytes, kstr) = self.st_pull_one_kchord()
        self.kbytes = kbytes
        self.kcap_str = kstr

        # '⇧Z'

    def kphrase_read(self) -> None:
        """Read one or some KChords, again and again, till Verb plus Arg complete"""

        kdo_call_by_kcap_str = KDO_CALL_BY_KCAP_STR

        # Pull 1st Arg, read enough KCHords to choose a Verb, pull 2nd Arg

        early_peek_else = self.kint_peek_else()
        early_kint = self.kint_pull(default=-1)

        while True:
            self.some_kchords_read()
            kcap_str = self.kcap_str
            if kcap_str in kdo_call_by_kcap_str.keys():
                kdo_call = kdo_call_by_kcap_str[kcap_str]

                kdo_func = kdo_call[0]
                phrasing = kdo_func == LineTerminal.kdo_hold_start_kstr
                if self.kstr_starts:
                    if kcap_str in ("-", "0"):
                        phrasing = True

                    # todo: more arbitrary Key Maps of '-' '0' Arg Chars

                if phrasing:
                    self.kchords_eval(vmode="Meta")  # for .kphrase_read
                    self.pqprint(f"{self.kstr_starts=} kphrase_read")
                    continue

            break

        # Multiply the Args if both present, else push the one, else push none

        late_peek_else = self.kint_peek_else()

        if early_peek_else is None:
            self.pqprint("kphrase_read")
        else:
            if late_peek_else is None:
                self.pqprint(f"{early_kint=} kphrase_read")
                self.kint_push(early_kint)
            else:
                late_kint = self.kint_pull(default=-1)

                self.pqprint(f"{early_kint=} {late_kint=} kphrase_read")
                self.kint_push(early_kint * late_kint)

    def some_kchords_read(self) -> None:
        """Read 1 Key Chord Sequence, as Bytes and Str"""

        (kbytes, kstr) = self.st_pull_one_kchord()
        self.tail_kchords_read(kbytes=kbytes, kcap_str=kstr)

        # '⌃L'  # '⇧Z ⇧Z'

    def tail_kchords_read(self, kbytes, kcap_str) -> None:
        """Read zero or more Key Chords to complete the Sequence"""

        st = self.st

        assert KCAP_SEP == " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc
        ksep = " "

        # Start up

        b = b""  # piles up Bytes
        s = ""  # piles up Chars as a Str
        eq_choice = (b, s)
        choices = list()

        # For each Key Chord Sequence

        kb = kbytes
        ks = kcap_str
        while True:
            b += kb
            s += (ksep + ks) if s else ks

            choice = (b, s)
            choices.append(choice)

            # Remember the longest Key Sequence matched with a Verb

            finds = self.kcap_str_findall(s)
            if s in finds:
                eq_choice = (b, s)

                # Quit taking more Key Chords when exactly one Func found

                if len(finds) == 1:
                    assert eq_choice[-1] == s, (eq_choice, s, finds)

                    last_choice = eq_choice
                    break

            # Quit after finding nothing
            # Fall back to last exact Find, else to first Choice

            if not finds:
                if not eq_choice[-1]:
                    last_choice = choice
                else:
                    last_choice = eq_choice
                    index = choices.index(last_choice)
                    for choice in choices[(index + 1) :]:
                        (kb, ks) = choice
                        st.append_one_kchord(kb, kstr=ks)
                break

            # Block till next Key Chord

            (kb, ks) = self.st_pull_one_kchord()

        # Succeed

        (b, s) = last_choice

        self.kbytes = b
        self.kcap_str = s

        self.pqprint(f"{b=} {s=}")

    def kcap_str_findall(self, kcap_str) -> list[str]:
        """List every matching LineTerminal Verb"""

        kdo_call_kcap_strs = KDO_CALL_KCAP_STRS

        assert KCAP_SEP == " "  # solves '⇧Tab' vs '⇧T a b' and '⎋⇧FnX' vs '⎋⇧Fn X'
        ksep = " "

        #

        eq_finds = list(_ for _ in kdo_call_kcap_strs if _ == kcap_str)

        p = kcap_str + ksep
        startswith_finds = list(_ for _ in kdo_call_kcap_strs if _.startswith(p))

        #

        finds = eq_finds + startswith_finds

        return finds

    def st_pull_one_kchord(self) -> tuple[bytes, str]:
        """Read 1 Key Chord, as Bytes and Str"""

        self.line_flush()

        kchord = self.st.pull_one_kchord()
        return kchord

    def st_pull_cursor_always_and_keyboard_maybe(self) -> None:

        self.line_flush()

        self.st.pull_cursor_always_and_keyboard_maybe()

    #
    # Eval KChords
    #

    def kchords_eval(self, vmode) -> None:
        """Take 1 Key Chord Sequence as a Verb to eval"""

        assert vmode in ("Insert", "Meta", "Replace", "Replace1"), (vmode,)

        kcap_str = self.kcap_str
        kstr_starts = self.kstr_starts
        ktext = self.ktext

        kdo_call_by_kcap_str = KDO_CALL_BY_KCAP_STR
        insert_pq_kdo_call_by_kcap_str = INSERT_PQ_KDO_CALL_BY_KCAP_STR

        # Choose 1 Python Def to call, on behalf of 1 Key Chord Sequence

        kdo_call: PY_CALL

        kdo_call = (LineTerminal.kdo_kcap_alarm_write_n,)  # def not found for K Cap
        if kcap_str in kdo_call_by_kcap_str.keys():
            kdo_call = kdo_call_by_kcap_str[kcap_str]
        if vmode == "Insert":
            if kcap_str in insert_pq_kdo_call_by_kcap_str.keys():
                kdo_call = insert_pq_kdo_call_by_kcap_str[kcap_str]

        kdo_func = kdo_call[0]
        assert kdo_func.__name__.startswith("kdo_"), (kdo_call, kcap_str)

        # Call the 1 Python Def

        kstr_starts_before = list(kstr_starts)
        peek_else = self.kint_peek_else()
        self.pqprint(f"{kstr_starts=} {peek_else=} {kcap_str=}")

        done = False
        if len(kdo_call) == 1:  # takes the Inverse Func when no Args and no KwArgs
            done = self.verb_eval_explicit_nonpositive_if(kdo_func)
        if not done:
            (alt_kdo_func, args, kwargs) = self.py_call_complete(kdo_call)
            self.pqprint(f"{peek_else=} func={alt_kdo_func.__name__}")
            alt_kdo_func(self, *args, **kwargs)

        # Forget the K Start's, K Stop's, and/or K Text's when we should

        self.kstarts_kstops_choose_after(kstr_starts_before, kcap_str=kcap_str)
        if ktext == self.ktext:
            if ktext:
                self.pqprint(f"{ktext=} cleared")
            self.ktext = ""  # .kchords_eval when .ktext unchanged

    def py_call_complete(self, call) -> tuple[typing.Callable, tuple, dict]:
        """Complete the Python Call with Args and KwArgs"""

        func = call[0]

        args = ()

        kwargs: dict
        kwargs = dict()

        if len(call) == 1:
            return (func, args, kwargs)

        if len(call) == 2:
            args = call[-1]
            return (func, args, kwargs)

        assert len(call) == 3, (call,)

        (func, args, kwargs) = call
        return (func, args, kwargs)

    def kstarts_kstops_choose_after(self, kstr_starts_before, kcap_str) -> None:
        """Forget the K Start's and/or add one K Stop's, like when we should"""

        kstr_starts = self.kstr_starts
        kstr_stops = self.kstr_stops

        # Forget the K Start's, unless this last Kdo_Func shrunk or grew or changed them

        if kstr_starts == kstr_starts_before:
            if kstr_starts:
                self.pqprint(f"{kstr_starts=} cleared")
            kstr_starts.clear()  # for .kstarts_kstops_forget_if

        # Forget the K Stop's, but then do hold onto the latest K Stop if present

        assert STOP_KCAP_STRS == ("⌃C", "⌃G", "⌃L", "⎋", "⌃\\")

        if kstr_stops:
            self.pqprint(f"{kstr_stops=} cleared")
        kstr_stops.clear()

        stopped = self.kcap_str in ("⌃C", "⌃G", "⌃L", "⎋", "⌃\\")
        if stopped:
            kstr_stops.append(self.kcap_str)

    def verb_eval_explicit_nonpositive_if(self, kdo_func) -> bool:
        """Call the Inverse Func for negative K Int, reject as Unbound for zero"""

        kdo_inverse_func_by = KDO_INVERSE_FUNC_BY
        kdo_only_positive_funcs = KDO_ONLY_POSITIVE_FUNCS
        kdo_only_without_arg_funcs = KDO_ONLY_WITHOUT_ARG_FUNCS

        # Quit without derailing a Missing K Int

        peek_else = self.kint_peek_else()
        if peek_else is None:
            return False

        kint = peek_else

        # Reject an explicit K Int, as if Def not found, for some Funcs

        if kdo_func in kdo_only_without_arg_funcs:
            self.kdo_kcap_alarm_write_n()  # as if Def not found, for .kdo_only_without_arg_funcs
            return True

        # Forward a Positive K Int, for some Funcs

        if kint > 0:
            return False

        # Negate the negative K Int and call the Inverse, for some Funcs

        if (kint < 0) and (kdo_func in kdo_inverse_func_by.keys()):
            kdo_inverse_func = kdo_inverse_func_by[kdo_func]
            fname = kdo_inverse_func.__name__

            self.pqprint(f"kint=-{kint} func={fname}")

            self.kint_pull(default=1)  # this Default can't much matter
            self.kint_push_positive(-kint)  # for .verb_eval_explicit_nonpositive_if
            kdo_inverse_func(self)

            return True

        # Reject a zeroed K Int, for some Funcs

        if (kint == 0) and (kdo_func in kdo_inverse_func_by.keys()):
            self.kdo_kcap_alarm_write_n()  # as if Def not found, for .kdo_inverse_func_by
            return True

        # Forward a Negative K Int, for some Funcs

        if kdo_func not in kdo_only_positive_funcs:
            return False

        # Reject a negative K Int, for some Funcs

        self.kdo_kcap_alarm_write_n()  # def not found for explicitly zeroed K Int
        return True

    #
    # Pause or Quit
    #

    def kdo_help_quit(self) -> None:
        """Take a Key Chord Sequence to mean say how to quit Vim"""

        # no .kint_pull here

        self.help_quit()  # for .kdo_help_quit

        # Vim ⎋ ⎋ via Meta Esc
        # Vim ⌃C ⌃L ⇧Q V I Return  # Vim ⇧QVI Return

    def help_quit(self) -> None:
        """Say how to quit Vim"""

        st = self.st
        st.str_print()
        st.str_print(
            "To quit, press one of" " ⌃C⇧Z⇧Q ⌃C⇧Z⇧Z ⌃G⌃X⌃C ⌃C⌃L:Q!Return ⌃G⌃X⌃S⌃X⌃C ⌃C⌃L:WQ!Return"
        )

        # todo: turn off 'self.help_quit' during '.xeditline'

        # todo: Emacs doesn't bind '⌃C R' to (revert-buffer 'ignoreAuto 'noConfirm)
        # todo: Emacs freaks if you delete the ⌃X⌃S File before calling ⌃X⌃S

        # Emacs/ Vim famously leave how-to-quit nearly never mentioned

    def kdo_quit_no_save(self) -> None:
        """Revert changes to the Output Lines, and quit this Linux Process"""

        olines = self.olines

        _ = self.kint_pull(default=0)  # todo: 'returncode = ' inside 'kdo_quit_no_save'

        olines.clear()

        self.line_flush()
        sys.exit()

        # Emacs ⌃X ⌃C save-buffers-kill-terminal  # Emacs ⌃X⌃C
        # Vim ⌃C ⌃L : Q Return quit-no-save  # Vim ⌃C⌃L :Q Return
        # Vim ⌃C ⌃L : Q ! Return quit-no-save  # Vim ⌃C⌃L :Q! Return
        # Vim ⌃C ⌃L ⇧Z ⇧Q quit-no-save  # Vim ⇧Z⇧Q

    def kdo_save_quit(self) -> None:
        """Revert changes to the Output Lines, and quit this Linux Process"""

        _ = self.kint_pull(default=0)  # todo: 'returncode = ' inside 'kdo_quit_no_save'

        self.line_flush()
        sys.exit()

        # Emacs ⌃X ⌃S ⌃X ⌃C save-buffer save-buffers-kill-terminal  # Emacs ⌃X⌃S⌃X⌃C
        # Vim ⌃C ⌃L : W Q Return save-quit  # Vim ⌃C⌃L :WQ Return
        # Vim ⌃C ⌃L : W Q ! Return save-quit  # Vim ⌃C⌃L :WQ! Return
        # Vim ⌃C ⌃L ⇧Z ⇧Z save-quit  # Vim ⇧Z⇧Z

    def kdo_terminal_stop(self) -> None:
        """Suspend and resume this Screen/ Keyboard Terminal"""

        st = self.st
        bt = st.bt

        self.vmode_enter(vmode="Meta")
        bt.bytes_stop()
        self.vmode_exit()

        # Emacs ⌃Z suspend-frame
        # Vim ⌃Z

    #
    # Quote
    #

    def kdo_text_write_n(self) -> str:
        """Take the Chars of 1 Key Chord Sequence as Text to write to Screen"""

        st = self.st
        kbytes = self.kbytes
        kchars = kbytes.decode()  # may raise UnicodeDecodeError

        kint = self.kint_pull(default=1)
        if kint <= 0:
            self.kint_push(kint)  # for .kdo_kcap_alarm_write_n
            self.kdo_kcap_alarm_write_n()
            return ""

        ktext = kint * kchars
        st.str_write(ktext)  # for .kdo_text_write_n

        return ktext

        # Spacebar, printable US-Ascii, and printable Unicode

    def kdo_kcap_alarm_write_n(self) -> None:
        """Take the Str of 1 Key Chord Sequence as Chars to write to Screen"""

        st = self.st
        kcap_str = self.kcap_str

        assert KCAP_SEP == " "

        peek_else = self.kint_peek_else()
        kint = self.kint_pull(default=1)

        self.pqprint(f"peek_else={peek_else} func=kdo_kcap_alarm_write_n")

        if peek_else is not None:
            st.str_meta_write(str(kint))

        ktext = kcap_str.replace(" ", "")
        st.str_meta_write(ktext)

        # Emacs ⌃Q quoted-insert/ replace
        # Vim ⌃V
        # Pq ⌃Q⌃V
        # Pq ⌃V⌃Q

        # Pq for any undefined Key Chord Sequence, printed without an alarming Beep

    def kdo_quote_kchars(self) -> None:
        """Block till the next K Chord, but then take it as Text, not as Verb"""

        st = self.st

        kcap_quote_by_str = KCAP_QUOTE_BY_STR

        #

        kint = self.kint_pull(default=1)
        if kint < 0:
            self.kdo_kcap_alarm_write_n()  # 'negative repetition arg' for Texts_Wrangle etc
            return

        #

        (kbytes, kstr) = self.st_pull_one_kchord()
        if not kint:
            return

        #

        kcap_str = kstr
        if kstr in kcap_quote_by_str.keys():
            kcap_str = kcap_quote_by_str[kstr]

        ktext = kint * kcap_str

        st.str_write(ktext)  # for .kdo_quote_kchars

    def kdo_quote_csi_kstrs_n(self) -> None:
        """Block till CSI Sequence complete, then take it as Text"""

        st = self.st
        kstr_stops = self.kstr_stops
        kcap_str = self.kcap_str
        # no .pull_int here

        assert CSI_EXTRAS == "".join(chr(_) for _ in range(0x20, 0x40))

        # Run as [ only after ⎋, else reject the .kcap_str [ as if entirely unbound

        if kcap_str == "[":
            if (not kstr_stops) or (kstr_stops[-1] != "⎋"):
                self.kdo_kcap_alarm_write_n()  # Key Cap [, but not after ⎋
                return

        # Block till CSI Sequence complete

        many_kbytes = b"\x1B" b"["
        kcap_str = "⎋ ["

        while True:
            (kbytes, kstr) = self.st_pull_one_kchord()

            many_kbytes += kbytes

            sep = " "  # '⇧Tab'  # '⇧T a b'  # '⎋⇧Fn X'  # '⎋⇧FnX'
            kcap_str += sep + kstr

            if len(kbytes) == 1:
                kord = kbytes[-1]
                if 0x20 <= kord < 0x40:  # !"#$%&'()*+,-./0123456789:;<=>?
                    continue

            break

        self.kbytes = many_kbytes
        self.kcap_str = kcap_str

        # Write as if via 'self.kdo_text_write_n()'  # ⎋[m, ⎋[1m, ⎋[31m, ...

        kint = self.kint_pull(default=1)
        kchars = many_kbytes.decode()  # may raise UnicodeDecodeError
        ktext = kint * kchars
        st.str_write(ktext)  # for .kdo_quote_csi_kstrs_n

        # Pq [ quote.csi.kstrs  # missing from Emacs, Vim, VsCode
        # unlike Vim [ Key Map

    def alarm_ring(self) -> None:
        """Ring the Bell"""

        st = self.st
        st.str_write("\a")

        # 00/07 Bell (BEL)

    #
    # For context, remember some of the Key Chord Sequences awhile
    #

    def kdo_kminus(self) -> None:
        """Jump back by one or more Lines, but land past the Dent"""

        kstr_starts = self.kstr_starts  # no .pull_int here

        # Hold Key Cap "-" for context, after Emacs ⌃U, but not after Vim 0123456789

        kdigits = list(_ for _ in kstr_starts if _ in list("0123456789"))
        kstarts_closed = kstr_starts[1:][-1:] == ["⌃U"]

        if not kdigits:
            if kstr_starts and not kstarts_closed:
                self.kdo_hold_start_kstr("-")
                return

        # Else run as Verb, with or without Arg

        kdo_func = LineTerminal.kdo_dent_minus_n  # Vim -
        done = self.verb_eval_explicit_nonpositive_if(kdo_func)
        if not done:
            kdo_func(self)

        # Emacs - after ⌃U
        # Vim -

    def kdo_kzero(self) -> None:
        """Hold another Digit, else jump to First Column"""

        kstr_starts = self.kstr_starts  # no .pull_int here
        st = self.st

        # Hold Key Cap "0" for context, after Emacs ⌃U or after Vim 123456789

        kstarts_closed = kstr_starts[1:][-1:] == ["⌃U"]
        if kstr_starts and not kstarts_closed:
            self.kdo_hold_start_kstr("0")
            return

        # Else jump to First Column

        st.column_x_write_1()  # for Vim 0

        # Emacs Digit 0 after ⌃U
        # Vim Digit 0 after 1 2 3 4 5 6 7 8 9
        # Vim 0

    def kdo_hold_start_kstr(self, argch) -> None:
        """Hold Key-Cap Str's till taken as Arg"""

        assert argch in (["⌃U"] + list("-0123456789")), (argch,)

        kstr_starts = self.kstr_starts  # no .pull_int here

        kstr_starts_before = list(kstr_starts)
        self.try_kdo_hold_start_kstr(argch=argch)

        assert kstr_starts != kstr_starts_before, (kstr_starts, kstr_starts_before)

    def try_kdo_hold_start_kstr(self, argch) -> None:
        """Hold Key-Cap Str's till taken as Arg"""

        assert argch in (["⌃U"] + list("-0123456789")), (argch,)

        kstr_starts = self.kstr_starts

        # ⌃U+ vs [-]⌃U* vs [-][-]⌃U* vs [0123456789]+⌃U? vs [-][0123456789]+⌃U?

        kdigits = list(_ for _ in kstr_starts if _ in list("0123456789"))

        kstarts_sorted_set = sorted(set(kstr_starts))
        kpithy = kstarts_sorted_set not in ([], ["-"], ["-", "⌃U"], ["⌃U"])
        assert kpithy == bool(kdigits), (kpithy, kdigits, kstr_starts)

        # Take ⌃U after Digits as starting over, else pile them up

        kstarts_closed = kstr_starts[1:][-1:] == ["⌃U"]

        if argch == "⌃U":
            if kdigits and kstarts_closed:
                kstr_starts.clear()  # for .hold_start_kstr ⌃U
            kstr_starts.append("⌃U")
            return

            # "" --> "⌃U" --> "⌃U ... ⌃U" --> "⌃U"

        # Take an odd or even count of Dash, until the first Digit

        if argch == "-":
            if not kdigits:
                if kstr_starts != ["-"]:
                    kstr_starts.clear()  # for .hold_start_kstr -
                kstr_starts.append("-")
                return

                # "" --> "-" --> "- -" --> "-"

            # else fall-thru

        # Hold the first Digit, or more Digits, after one Dash or none

        if argch in list("0123456789"):
            if not kdigits:
                negated = kstr_starts == ["-"]
                kstr_starts.clear()  # for .hold_start_kstr 0123456789
                if negated:
                    kstr_starts.append("-")
                kstr_starts.append(argch)
                return

                # "" --> "-..." or "..."

            if not kstarts_closed:
                kstr_starts.append(argch)
                return

                # "..." --> "... ..."

            # else fall-thru

        # Say no Def found for this Key-Cap Str

        self.kdo_kcap_alarm_write_n()  # for .hold_start_kstr of Key Cap -0123456789

        # Emacs '-', and Emacs 0 1 2 3 4 5 6 7 8 9, after Emacs ⌃U
        # Pq Em/Vim Csi Sequences:  ⎋[m, ⎋[1m, ⎋[31m, ...
        # Vim 1 2 3 4 5 6 7 8 9, and Vim 0 thereafter

    def kdo_hold_stop_kstr(self) -> None:
        """Hold Key-Cap Stop Str just long enough to see if struck twice in a row"""

        kstr_stops = self.kstr_stops  # ignores the .kstr_starts
        kcap_str = self.kcap_str

        assert len(kstr_stops) <= 1, (len(kstr_stops), kstr_stops, kcap_str)
        if kstr_stops == [kcap_str]:
            if kcap_str == "⌃\\":
                self.kdo_assert_false()
            else:
                self.help_quit()  # for .kdo_hold_stop_kstr

        # Pq ⎋ ⌃C ⌃G ⌃\  # missing from Emacs, Vim, VsCode

    def kdo_assert_false(self) -> None:
        """Assert False"""

        assert False, (self.kdo_assert_false,)

    #
    # Take a Signed Int Arg from ⌃U+[-][0123456789]*⌃U* Key Chords
    #

    def kint_push_positive(self, kint) -> None:
        """Set up to call another Key Chord Sequence, but only positively"""

        assert kint > 0, (kint,)
        self.kint_push(kint)  # for .kint_push_positive

    def kint_push(self, kint) -> None:
        """Fill the cleared Key-Cap Str Holds, as if Emacs ⌃U ..."""

        kstr_starts = self.kstr_starts
        assert not kstr_starts, (kstr_starts,)

        kstr_starts.extend(["⌃U"] + list(str(kint)) + ["⌃U"])

        # does pushed as wrapped, could push as not-wrapped

    def kint_pull_positive(self) -> int:
        """Fetch & clear a Positive Int from the Key-Cap Str Holds, defaulting to 1"""

        kint = self.kint_pull(default=1)
        assert kint > 0, (kint,)

        return kint

    def kint_pull(self, default) -> int:
        """Fetch & clear an Int Literal from out of the Key-Cap Str Holds"""

        assert default is not None

        kstr_starts = self.kstr_starts

        kint = self.kint_peek(default)
        kstr_starts.clear()  # for .kint_pull

        return kint

    def kint_peek(self, default) -> int:
        """Fetch the Key-Cap Str Holds, without adding or removing them"""

        assert default is not None

        peek_else = self.kint_peek_else(default)
        assert peek_else is not None, (peek_else, default)
        kint = peek_else

        return kint

    def kint_peek_else(self, default=None) -> int | None:
        """Fetch the Key-Cap Str Holds, without adding or removing them"""

        kstr_starts = self.kstr_starts

        # ⌃U+ vs [-]⌃U* vs [-][-]⌃U* vs [0123456789]+⌃U? vs [-][0123456789]+⌃U?

        kdigits = list(_ for _ in kstr_starts if _ in list("0123456789"))
        kliteral = "".join(_ for _ in kstr_starts if _ in list("-0123456789"))

        kstarts_sorted_set = sorted(set(kstr_starts))
        kpithy = kstarts_sorted_set not in ([], ["-"], ["-", "⌃U"], ["⌃U"])
        assert kpithy == bool(kdigits), (kpithy, kdigits, kstr_starts)

        # Take Int Literal, else Default

        kint = default  # may be None
        if kstr_starts:
            if kdigits:
                kint = int(kliteral)  # might never raise ValueError
            elif kstr_starts[:2] == ["-", "-"]:
                assert kstarts_sorted_set in (["-"], ["-", "⌃U"]), (kstarts_sorted_set,)
                kint = 4 ** len(kstr_starts[3:])  # up from 1 at ["-", "-", "⌃U"]
            elif kstr_starts[:1] == ["-"]:
                assert kstarts_sorted_set in (["-"], ["-", "⌃U"]), (kstarts_sorted_set,)
                kint = 4 ** len(kstr_starts[1:])  # down from -1 at ["-"]
                kint *= -1
            else:
                assert kstarts_sorted_set == ["⌃U"], (kstarts_sorted_set,)
                kint = 4 ** len(kstr_starts)  # up from 4 at ["⌃U"]

        # Succeed

        return kint  # positive kint for the Vim .kmap

        # raises ValueError if ever '.kstr_starts' isn't Cancelled or an Int Literal

    #
    # Jump the Screen Cursor ahead, or back, across the Chars of Ragged Lines
    #

    def kdo_char_minus_n(self) -> None:
        """Step back by one or more Chars, into the Lines behind if need be"""

        st = self.st

        kint = self.kint_pull_positive()
        (row_y, column_x) = self.st.index_yx_plus(-kint)
        st.row_y_column_x_write(row_y, column_x=column_x)

        # Emacs ⌃B backward-char
        # Emacs ← left-char
        # Vim ⇧R Delete and Vim R Delete
        # Vim ⌃H and Vim ⇧R ⌃H and Vim R ⌃H
        # macOS ⌃B

    def kdo_char_plus_n(self) -> None:
        """Step ahead by one or more Chars, into the Lines ahead if need be"""

        st = self.st

        kint = self.kint_pull_positive()
        (row_y, column_x) = self.st.index_yx_plus(kint)
        st.row_y_column_x_write(row_y, column_x=column_x)

        # Emacs ⌃F forward-char
        # Emacs → right-char
        # Vim Spacebar
        # macOS ⌃F

    #
    # Jump the Screen Cursor to a Column
    #

    def kdo_column_1(self) -> None:
        """Jump to Left of Line"""

        st = self.st

        # no .pull_int here

        st.column_x_write_1()

        # part of .kdo_kzero Vim 0

    def kdo_column_minus_n(self) -> None:
        """Jump back by one or more Columns"""

        st = self.st

        kint = self.kint_pull_positive()
        st.str_write_form_or_form_pn("\x1B" "[" "{}D", pn=kint)

        # 00/08 Backspace (BS) \b ⌃H
        # 07/15 Delete (DEL) \x7F ⌃? 'Eliminated Control Function'

        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left

        # Vim ←  # Emacs ← is Vim Delete
        # Vim H

    def kdo_column_dent(self) -> None:
        """Jump to the first Column beyond the Dent"""

        st = self.st

        peek_else = self.kint_peek_else()
        assert peek_else is None, (peek_else,)

        st.column_x_write_dent()  # for Vim ^

        # Vim ^

    def kdo_column_n(self) -> None:
        """Jump to Column by number, but without changing the Line of the Cursor"""

        st = self.st

        kint = self.kint_pull(default=self.st.x_columns)  # Vim | defaults to Column 1

        middle_column_x = self.st.x_columns // 2
        if kint == 0:
            st.column_x_write(middle_column_x)
        else:
            st.column_x_write(kint)

        # Vim |
        # VsCode ⌃G {line}:{column}

    def kdo_column_n_plus(self) -> None:
        """Jump to Column by +/- number, but count Columns up from Zero"""

        st = self.st

        middle_column_x = self.st.x_columns // 2

        peek_else = self.kint_peek_else()
        if peek_else is None:
            self.kint_pull(default=0)
            st.column_x_write(middle_column_x)
        else:
            kint = self.kint_pull(default=0)
            st.column_x_write(1 + kint)  # pedantic Zero-Based Emacs ⎋GTab

        # Emacs ⎋GTab ⌥GTab move-to-column

    def kdo_column_plus_n(self) -> None:
        """Jump ahead by one or more Columns"""

        st = self.st
        kint = self.kint_pull_positive()
        st.str_write_form_or_form_pn("\x1B" "[" "{}C", pn=kint)

        assert CUF_X == "\x1B" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right

        # Vim →  # Emacs → is Vim Spacebar
        # Vim L

    def kdo_tab_minus_n(self) -> None:
        """Jump back by one or more Column Tabs"""

        st = self.st

        kint = self.kint_pull_positive()
        st.str_write_form_or_form_pn("\x1B" "[" "{}Z", pn=kint)

        # Disassemble these StrTerminal Writes

        assert CBT_X == "\x1B" "[" "{}Z"  # CSI 05/10 Cursor Backward Tabulation
        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left

        # Pq ⇧Tab tab.minus.n  # missing from Emacs, Vim, VsCode

    def kdo_tab_plus_n(self) -> None:
        """Jump ahead by one or more Column Tabs"""

        st = self.st

        kint = self.kint_pull_positive()
        st.str_write_form_or_form_pn("\x1B" "[" "{}I", pn=kint)

        # Disassemble these StrTerminal Writes

        assert CHT_X == "\x1B" "[" "{}I"  # CSI 04/09 Cursor Forward [Horizontal] Tab~
        assert CUF_X == "\x1B" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right

        # Pq Tab tab.plus.n  # missing from Emacs, Vim, VsCode

    #
    # Move the Screen Cursor to Row, at Left or at Dent, relatively or absolutely
    #

    def kdo_dent_line_n_else_first(self) -> None:
        """Jump to a numbered Line, else First Line, but land past the Dent"""

        peek_else = self.kint_peek_else()
        if peek_else is None:
            self.kint_push_positive(1)

        self.kdo_dent_line_n_else_last()  # for Vim G G

        # Vim G G

    def kdo_dent_line_n_else_last(self) -> None:
        """Jump to a numbered Line, else Last Line, but land past the Dent"""

        st = self.st

        self.kdo_line_n_else_last()  # Vim ⇧G is kin with Vim ⇧H ⇧M ⇧L for Screen
        st.column_x_write_dent()  # for Vim ⇧G

        # Vim ⇧G

    def kdo_dent_minus_n(self) -> None:
        """Jump back by one or more Lines, but land past the Dent"""

        st = self.st

        self.kdo_line_minus_n()
        st.column_x_write_dent()  # for Vim -

        # Vim -
        # part of Pq -

    def kdo_dent_plus_n(self) -> None:
        """Jump ahead by one or more Lines, but land past the Dent"""

        st = self.st

        self.kdo_line_plus_n()
        st.column_x_write_dent()  # for Vim +

        self.ktext += "\r\n"  # Vim ⇧R Return or Vim R Return

        # Vim +
        # Vim Return
        # Vim ⇧R Return and Vim R Return

    def kdo_dent_plus_n1(self) -> None:
        """Jump ahead by zero or more Lines, but land past the Dent"""

        st = self.st

        kint = self.kint_pull_positive()
        if kint > 1:
            kint_minus = kint - 1
            st.str_write_form_or_form_pn("\x1B" "[" "{}B", pn=kint_minus)

        st.column_x_write_dent()  # for Vim _

        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down

        # Vim _

    def kdo_end_plus_n1(self) -> None:
        """Jump ahead by zero or more Lines, and land on End of Line"""

        st = self.st

        vmodes = self.vmodes
        vmode = vmodes[-1]

        assert vmode in ("Insert", "Meta", "Replace", "Replace1"), (vmode,)
        assert X_32100 == 32100  # vs CUF_X "\x1B" "[" "{}C"

        kint = self.kint_pull_positive()  # todo: Emacs ⌃E exact inverse of ⌃A?
        if kint > 1:
            kint_minus = kint - 1
            st.str_write_form_or_form_pn("\x1B" "[" "{}B", pn=kint_minus)

        st.str_write_form_or_form_pn("\x1B" "[" "{}C", pn=32100)  # todo: more Columns
        if vmode == "Meta":
            st.str_write_form_or_form_pn("\x1B" "[" "{}D", pn=1)

        # Disassemble these StrTerminal Writes

        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down
        assert CUF_X == "\x1B" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right
        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left

        # Emacs ⌃E move-end-of-line
        # Vim $
        # macOS ⌃E

    def kdo_home_line_n(self) -> None:
        """Jump to a numbered Line, but land at Left of Line"""

        st = self.st

        self.kdo_line_n_else_last()  # Emacs ⎋G⎋G is kin with Emacs ⎋R
        st.column_x_write_1()  # for Emacs ⎋G⎋G Goto-Line

        # Emacs ⎋G⎋G ⎋GG ⌥G⌥G ⌥GG goto-line  # not zero-based

    def kdo_home_plus_n1(self) -> None:
        """Jump ahead by zero or more Lines, and land at Left of Line"""

        st = self.st

        kint = self.kint_pull_positive()  # todo: Emacs ⌃A exact inverse of ⌃E?
        if kint > 1:
            kint_minus = kint - 1
            st.str_write_form_or_form_pn("\x1B" "[" "{}B", pn=kint_minus)

        st.column_x_write_1()  # for Emacs ⌃A, macOS ⌃A

        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down

        # Emacs ⌃A move-beginning-of-line
        # macOS ⌃A

    def kdo_line_minus_n(self) -> None:
        """Jump back by one or more Lines"""

        st = self.st

        kint = self.kint_pull_positive()
        st.str_write_form_or_form_pn("\x1B" "[" "{}A", pn=kint)

        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up

        # Emacs ⌃P previous-line
        # Vim K

    def kdo_line_n_else_last(self) -> None:
        """Jump to Line by number, but without changing the Column of the Cursor"""

        self.kdo_row_n_else_last()  # todo: more Lines than Rows

        # common to Vim ⇧G and Emacs ⎋G⎋G ⎋GG ⌥G⌥G ⌥GG

    def kdo_line_plus_n(self) -> None:
        """Jump ahead by one or more Lines"""

        st = self.st

        kint = self.kint_pull_positive()
        st.str_write_form_or_form_pn("\x1B" "[" "{}B", pn=kint)

        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down

        # Emacs ⌃N next-line
        # Vim ⌃J
        # Vim J

    def kdo_line_first_tenths_n(self) -> None:
        """Jump to First Line, or to 1...9 Tenths in from Top of File"""

        st = self.st

        kint = self.kint_pull(default=0)

        tenths = 0
        if kint in range(10):  # Emacs ⎋< doesn't doc unusual Args well
            tenths = kint  # Emacs ⌃U ⎋< isn't ⌃U 4 ⎋<

        row_y = 1
        if tenths:
            row_y = int((tenths * st.y_rows) / 10)

        self.kint_push_positive(row_y)
        self.kdo_home_line_n()

        # Emacs ⎋< ⌥< beginning-of-buffer

    def kdo_line_last_tenths_n(self) -> None:
        """Jump to Last Line, or to 1...9 Tenths in from End of File"""

        st = self.st

        kint = self.kint_pull(default=0)

        tenths = 0
        if kint in range(10):  # Emacs ⎋> doesn't doc unusual Args well
            tenths = kint  # Emacs ⌃U ⎋> isn't ⌃U 4 ⎋>

        row_y = st.y_rows - int((tenths * st.y_rows) / 10)

        self.kint_push_positive(row_y)
        self.kdo_home_line_n()

        # Emacs ⎋> ⌥> end-of-buffer

    def kdo_row_middle(self) -> None:
        """Jump to Middle of Screen"""

        st = self.st

        peek_else = self.kint_peek_else()
        assert peek_else is None, (peek_else,)

        middle_row_y = self.st.y_rows // 2
        st.row_y_write(row_y=middle_row_y)
        st.column_x_write_dent()  # for Vim ⇧M

        # Vim ⇧M

    def kdo_row_n_else_last(self) -> None:
        """Jump to Line by number, but without changing the Column of the Cursor"""

        st = self.st

        kint = self.kint_pull(default=st.y_rows)  # Emacs ⎋G⎋G defaults to interact
        if kint == 0:
            st.row_y_write(st.y_rows // 2)
        else:
            st.row_y_write(kint)

        middle_row_y = st.y_rows // 2

        if not kint:  # Emacs ⎋G⎋G shrugs off non-positive Arg
            alt_kint = middle_row_y
        elif kint < 0:  # negative Vim ⇧G Arg could jump to last Line and jump up
            alt_kint = st.y_rows + 1 + kint
        else:
            alt_kint = kint  # Emacs ⎋R counts up from 0, doesn't offer a Middle choice

        y = min(max(1, alt_kint), st.y_rows)

        st.row_y_write(y)

        # common to Emacs ⎋R and Vim ⇧H ⇧M ⇧L

    def kdo_row_n_down(self) -> None:
        """Jump near Top of Screen, but then down ahead by zero or more Lines"""

        st = self.st

        kint = self.kint_pull_positive()
        st.row_y_write(row_y=kint)
        st.column_x_write_dent()  # for Vim ⇧H

        # Vim ⇧H

    def kdo_row_n_else_middle_first_last(self) -> None:
        """Jump to Middle, except Top from Middle, and Bottom from Top"""

        st = self.st
        row_y = st.row_y
        middle_row_y = st.y_rows // 2

        # Jump to Row from Top or Bottom of Screen, if Arg given

        peek_else = self.kint_peek_else()
        if peek_else is not None:
            kint = peek_else

            if kint < 0:
                self.kdo_row_n_else_last()
            else:
                kint = self.kint_pull(default=0)
                self.kint_push_positive(1 + kint)  # pedantic Zero-Based Emacs ⎋R
                self.kdo_row_n_else_last()

            st.column_x_write_1()
            return

        # Jump to Middle, except Top from Middle, and Bottom from Top

        if row_y == 1:
            y = -1
        elif row_y == middle_row_y:
            y = 1
        else:
            y = middle_row_y  # could encode as the 0 Row of Emacs ⎋G⎋G

        st.row_y_write(y)
        st.column_x_write_1()

        # Emacs ⎋R ⌥R move-to-window-line-top-bottom

    def kdo_row_n_up(self) -> None:
        """Jump near Bottom of Screen, but then up behind by zero or more Lines"""

        st = self.st

        kint = self.kint_pull_positive()
        st.row_y_write(row_y=-kint)
        st.column_x_write_dent()  # for Vim ⇧L

        # Vim ⇧L

    #
    # Move the Screen Cursor ahead and back by a couple of sizes of Words
    #

    def kdo_bigword_minus_n(self) -> None:
        """Step back by one or more Bigger Words"""

        self.kdo_tab_minus_n()

        # Emacs ⎋B ⌥B backward-word, inside of superword-mode
        # Vim ⇧B

    def kdo_bigword_plus_n(self) -> None:
        """Step ahead by one or more Bigger Words"""

        self.kdo_tab_plus_n()

        # Emacs ⎋F ⌥F forward-word, inside of superword-mode
        # Vim ⇧W

    def kdo_bigword_plus_n_almost(self) -> None:
        """Step ahead by one or more Bigger Words, but land on end of Word"""

        kint = self.kint_pull_positive()

        self.kint_push_positive(6 * kint)
        self.kdo_char_plus_n()

        # Vim ⇧E

    def kdo_lilword_minus_n(self) -> None:
        """Step back by one or more Little Words"""

        kint = self.kint_pull_positive()

        self.kint_push_positive(4 * kint)
        self.kdo_char_minus_n()

        # Emacs ⎋B ⌥B backward-word, outside of superword-mode
        # Vim B

    def kdo_lilword_plus_n(self) -> None:
        """Step ahead by one or more Little Words"""

        kint = self.kint_pull_positive()

        self.kint_push_positive(4 * kint)
        self.kdo_char_plus_n()

        # Emacs ⎋F ⌥F forward-word, outside of superword-mode
        # Vim W

    def kdo_lilword_plus_n_almost(self) -> None:
        """Step ahead by one or more Little Words, but land on end of Word"""

        kint = self.kint_pull_positive()

        self.kint_push_positive(3 * kint)
        self.kdo_char_plus_n()

        # Vim E

    #
    # Dedent or Dent the Lines at and below the Screen Cursor
    #

    def kdo_lines_dedent_n(self) -> None:
        """Remove Blank Space from the Left of one or more Lines"""

        assert DCH_X == "\x1B" "[" "{}P"  # CSI 05/00 Delete Character

        self.kdo_line_form_to_read_eval("\x1B" "[" "{}P")

        # Vim <
        # Vim < <  # Vim <<

    def kdo_lines_dent_n(self) -> None:
        """Insert 1 Dent of Blank Space into the Left of one or more Lines"""

        assert ICH_X == "\x1B" "[" "{}@"  # CSI 04/00 Insert Character

        self.kdo_line_form_to_read_eval("\x1B" "[" "{}@")

        # Vim >
        # Vim > >  # Vim >>

    def kdo_line_form_to_read_eval(self, form) -> None:
        """Work at the Left of one or more Lines"""

        st = self.st

        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down

        # Decide to do, or not to do

        yxjumps_else = self.read_eval_to_yxjumps_else()
        if yxjumps_else is None:
            return None

        yxjumps = yxjumps_else
        (alt_yjump, xjump) = yxjumps

        yjump = alt_yjump if alt_yjump else -1  # grow mark in Line into mark of Line

        # Start here, or there below, and work up by Line to land in the Top Line

        DENT = 4
        assert DENT == 4  # as if ~/.vimrc said :set softtabstop=4 shiftwidth=4 expandtab

        st.column_x_write_1()  # Vim <<  # Vim >>

        if yjump > 1:
            yjump_minus = yjump - 1
            st.str_write_form_or_form_pn("\x1B" "[" "{}B", pn=yjump_minus)

        for y in range(abs(yjump)):
            if y:
                st.str_write_form_or_form_pn("\x1B" "[" "{}A", pn=1)
            st.str_write_form_or_form_pn(form, pn=4)  # DENT == 4

        # part of Vim >
        # part of Vim >

    #
    # Delete the Lines at and below the Screen Cursor
    #

    def kdo_dents_cut_n(self) -> None:
        """Cut N Lines here and below, and land past Dent"""

        st = self.st

        kint = self.kint_pull_positive()

        st.str_write_form_or_form_pn("\x1B" "[" "{}M", pn=kint)
        st.column_x_write_dent()  # for Vim D D, VsCode ⌘X

        assert DL_Y == "\x1B" "[" "{}M"  # CSI 04/13 Delete Line

        # Vim D D  # Vim DD
        # VsCode ⌘X

    #
    # Visit Replace or Insert to change/ drop/ add Text Chars/ Lines/ Heads/ Tails
    #

    def kdo_ins_n_till(self) -> str:
        """Insert Text Sequences till ⌃C, or ⎋, etc, except for ⌃O and Control Sequences"""

        st = self.st

        kint = self.kint_pull_positive()

        ktext = self.texts_vmode_wrangle("Insert", kint=kint)
        st.str_write_form_or_form_pn("\x1B" "[" "{}D", pn=1)

        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left

        return ktext

        # Vim I
        # Pq I repeats even when ⌃C quits I, not ⌃G ⎋ ⌃\  # Vim I doesn't

    def kdo_replace_n_till(self) -> None:
        """Replace Text Sequences till ⌃C, or ⎋, etc, except for ⌃O and Control Sequences"""

        st = self.st

        kint = self.kint_pull_positive()

        self.texts_vmode_wrangle("Replace", kint=kint)
        st.str_write_form_or_form_pn("\x1B" "[" "{}D", pn=1)

        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left

        # Vim ⇧R
        # Pq ⇧R repeats even when ⌃C quits ⇧R, not ⌃G ⎋ ⌃\  # Vim ⇧R doesn't

    def kdo_replace_n_once(self) -> None:
        """Replace 1 Text Sequence, or pass through ⌃O and Control Sequences"""

        st = self.st

        kint = self.kint_pull_positive()

        self.texts_vmode_wrangle("Replace1", kint=kint)
        st.str_write_form_or_form_pn("\x1B" "[" "{}D", pn=1)

        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left

        # Vim R

    def kdo_char_cut_left_n(self) -> None:
        """Delete N Chars to the Left, but from this Line only"""

        st = self.st

        kint = self.kint_pull_positive()

        behind = (((st.row_y - 1) * st.x_columns) + st.column_x) - 1
        kint_behind = min(behind, kint)

        head = min(kint_behind, st.column_x - 1)
        mid = (kint_behind - head) // st.x_columns
        tail = (kint_behind - head) % st.x_columns

        if head:
            self.kint_push_positive(head)
            self.kdo_column_minus_n()  # Vim wraps I Delete left  # Emacs too

            st.str_write_form_or_form_pn("\x1B" "[" "{}P", pn=head)

        if not tail:
            if head:
                if self.ktext:
                    if not self.ktext.endswith("\r\n"):
                        self.ktext = self.ktext[:-1]  # Vim I Delete

            if mid:
                self.kint_push_positive(mid)
                self.kdo_line_minus_n()

                st.str_write_form_or_form_pn("\x1B" "[" "{}M", pn=mid)

        else:
            self.kint_push_positive(st.x_columns)  # rightmost Column before next Row up
            self.kdo_column_n()

            if mid:
                self.kint_push_positive(mid)
                self.kdo_line_minus_n()

                st.str_write_form_or_form_pn("\x1B" "[" "{}M", pn=mid)

            self.kdo_line_minus_n()

            if tail > 1:
                tail_minus = tail - 1
                self.kint_push_positive(tail_minus)
                self.kdo_column_minus_n()

                st.str_write_form_or_form_pn("\x1B" "[" "{}P", pn=tail_minus)

        # Disassemble these StrTerminal Writes

        assert DL_Y == "\x1B" "[" "{}M"  # CSI 04/13 Delete Line
        assert DCH_X == "\x1B" "[" "{}P"  # CSI 05/00 Delete Character

        # Vim ⇧X

        # Vim I ⌃H into U Undo
        # Vim I Delete into U Undo
        # Vim ⇧R Delete of repetition text  # Pq ⇧R Delete is Vim Delete
        # Emacs Delete into ⌃Y Yank
        # macOS ⌃H into ⌘Z Undo

    def kdo_char_cut_right_n(self) -> None:
        """Delete N Chars to the Right, but from this Line only"""

        st = self.st

        kint = self.kint_pull_positive()
        st.str_write_form_or_form_pn("\x1B" "[" "{}P", pn=kint)
        assert DCH_X == "\x1B" "[" "{}P"  # CSI 05/00 Delete Character

        # Vim X

        # Emacs ⌃D delete-char, or delete-forward-char
        # Vim I ⌃D doesn't work, for no simple reason  # Vim I ⌃O X does work
        # Pq I ⌃D
        # macOS ⌃D into ⌘Z Undo

    def kdo_line_ins_ahead_n(self) -> None:
        """Insert 0 or more Empty Lines ahead, and land at Left before the First"""

        st = self.st

        kint = self.kint_pull(default=1)
        if kint < 0:
            self.kdo_kcap_alarm_write_n()  # def not found for negative Emacs ⌃O
            return

        if kint:
            st.str_write("\n")  # 00/10  # "\x0A"  # "\x1B" "[" "B"
            st.str_write_form_or_form_pn("\x1B" "[" "{}L", pn=kint)  # insert
            st.str_write_form_or_form_pn("\x1B" "[" "{}A", pn=kint)  # up

        self.kdo_end_plus_n1()

        # Disassemble these StrTerminal Writes

        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
        assert IL_Y == "\x1B" "[" "{}L"  # CSI 04/12 Insert Line

        # Emacs ⌃O open-line  # todo: move tail of Line into new inserted Line

    def kdo_line_ins_behind_mostly_n(self) -> None:
        """Insert 1 or more Empty Lines below, and land in Left of Last"""

        st = self.st

        kint = self.kint_pull_positive()

        if st.column_x != 1:
            st.str_write("\r\n")  # 00/13 00/10  # "\x0D\x0A"
        st.str_write_form_or_form_pn("\x1B" "[" "{}L", pn=kint)

        self.ktext += "\r\n"  # Vim I Return

        assert IL_Y == "\x1B" "[" "{}L"  # CSI 04/12 Insert Line

        # Emacs Return
        # Vim I Return  # todo: move tail of Line into new inserted Line
        # Vim ⇧R Return is Vim I Return, but Pq ⇧R Return is Vim Return

    def kdo_tail_head_cut_n(self) -> None:
        """Cut the Tail or Head of the Line, and also Lines Below or Above"""

        st = self.st

        kpulls = st.kpulls

        peek_else = self.kint_peek_else()
        kint = self.kint_pull(default=0)

        ps_0 = 0  # EL_P CSI K writes Spaces ahead for Ps=0

        # Emacs ⌃K, without Arg

        if peek_else is None:

            if st.column_x == 1:
                if len(kpulls) >= 2:
                    if (kpulls[-2][-1], kpulls[-1][-1]) == ("⌃K", "⌃K"):
                        # assert st.kstr_list[-2:] == ["⌃K", "⌃K"], (st.kstr_list[-2:],)
                        st.str_write("\r")  # 00/13  # "\x0D"
                        st.str_write_form_or_form_pn("\x1B" "[" "{}M", pn=1)  # goodbye
                        return

                        # todo: Cope when ⌃K is not .kdo_tail_head_cut_n
                        # todo: Cope when .kdo_tail_head_cut_n is repeated but not ⌃K
                        # todo: Tell each .kdo_ when it's being repeated by whatever Key Chords

            st.str_write_form_or_form_pn("\x1B" "[" "{}K", pn=ps_0, default=ps_0)
            return

        # Emacs ⌃K, with Arg

        if kint > 0:  # Emacs splits, doesn't delete left
            st.str_write("\r")  # 00/13  # "\x0D"
            st.str_write_form_or_form_pn("\x1B" "[" "{}M", pn=kint)  # goodbye
            return

        pn = st.column_x - 1
        if pn:
            st.str_write_form_or_form_pn("\x1B" "[" "{}D", pn=pn)
            st.str_write_form_or_form_pn("\x1B" "[" "{}P", pn=pn)

        if not kint:
            return

        st.str_write_form_or_form_pn("\x1B" "[" "{}A", pn=-kint)  # up
        st.str_write_form_or_form_pn("\x1B" "[" "{}M", pn=-kint)  # goodbye

        # Disassemble these StrTerminal Writes

        assert CR == "\r"  # 00/13 Carriage Return (CR) ⌃M

        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left
        assert DCH_X == "\x1B" "[" "{}P"  # CSI 05/00 Delete Character
        assert EL_P == "\x1B" "[" "{}K"  # CSI 04/11 Erase in Line
        assert DL_Y == "\x1B" "[" "{}M"  # CSI 04/13 Delete Line

        # Emacs ⌃K kill-line
        # macOS ⌃K into ⌘Z Undo

    def kdo_tail_cut_n_column_minus(self) -> None:
        """Cut the Tail of the Line, and also Lines Below"""

        st = self.st

        self.kdo_tail_cut_n()

        st.str_write("\b")  # 00/08 Backspace (BS) \b ⌃H
        assert BS == "\b"  # 00/08 Backspace ⌃H

        # Vim ⇧D  # same effect as Vim D $

    def kdo_tail_cut_n(self) -> None:
        """Cut the Tail of the Line, and also Lines Below"""

        st = self.st

        kint = self.kint_pull(default=1)
        if kint <= 0:
            self.kint_push(kint)
            self.kdo_kcap_alarm_write_n()  # 'negative repetition arg' for Vim ⇧D, Vim ⇧C
            return

        ps_0 = 0  # writes Spaces ahead  # CSI K default Ps = 0
        st.str_write_form_or_form_pn("\x1B" "[" "{}K", pn=ps_0, default=ps_0)

        if kint > 1:
            kint_minus = kint - 1
            st.str_write_form_or_form_pn("\x1B" "[" "{}B", pn=1)  # down
            st.str_write_form_or_form_pn("\x1B" "[" "{}M", pn=kint_minus)  # goodbye
            st.str_write_form_or_form_pn("\x1B" "[" "{}A", pn=1)  # up

        # Disassemble these StrTerminal Writes

        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down
        assert EL_P == "\x1B" "[" "{}K"  # CSI 04/11 Erase in Line
        assert DL_Y == "\x1B" "[" "{}M"  # CSI 04/13 Delete Line

        # common to Vim ⇧C, Vim ⇧D

    #
    # Move before Insert
    #

    def kdo_column_plus_ins_n_till(self) -> None:
        """Step one Column ahead and then visit Insert Mode"""

        st = self.st

        st.str_write_form_or_form_pn("\x1B" "[" "{}C", pn=1)
        self.kdo_ins_n_till()

        assert CUF_X == "\x1B" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right

        # Vim A = Vim I + Vim ⌃O L

    def kdo_column_dent_ins_n_till(self) -> None:
        """Jump to the first Column beyond the Dent, then visit Insert Mode"""

        st = self.st

        st.column_x_write_dent()  # for Vim ⇧I
        self.kdo_ins_n_till()

        # Vim ⇧I = Vim ^ + Vim I

    def kdo_end_plus_ins_n_till(self) -> None:
        """Jump out beyond End of Line, then visit Insert Mode"""

        st = self.st

        st.str_write_form_or_form_pn("\x1B" "[" "{}C", pn=32100)  # todo: more Columns
        self.kdo_ins_n_till()

        assert CUF_X == "\x1B" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right

        # Vim ⇧A = Vim I + Vim ⌃O $

    def kdo_line_ins_above_n(self) -> None:
        """Insert 1 Empty Line above, visit Insert Mode at Left, then repeat Texts"""

        st = self.st

        kint = self.kint_pull_positive()

        st.str_write("\r")  # 00/13  # "\x0D"
        st.str_write_form_or_form_pn("\x1B" "[" "{}L", pn=1)

        ktext = self.kdo_ins_n_till()
        for _ in range(kint - 1):
            st.str_write("\r\n")  # 00/13 00/10  # "\x0D\x0A"

            ktext_kint = len(ktext.splitlines())
            if ktext_kint:
                st.str_write_form_or_form_pn("\x1B" "[" "{}L", pn=ktext_kint)
                st.str_write(ktext)  # for .kdo_line_ins_above_n Insert
                st.str_write_form_or_form_pn("\x1B" "[" "{}D", pn=ktext_kint)

        # Disassemble these StrTerminal Writes

        assert LF == "\n"  # 00/10 Line Feed (LF) ⌃J
        assert CR == "\r"  # 00/13 Carriage Return (CR) ⌃M

        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left
        assert IL_Y == "\x1B" "[" "{}L"  # CSI 04/12 Insert Line

        # Vim ⇧O
        # Pq ⇧O repeats even when ⌃C quits I, not ⌃G ⎋ ⌃\  # Vim ⇧O doesn't

    def kdo_line_ins_below_n(self) -> None:
        """Insert 1 Empty Line ahead, visit Insert Mode at Left, then repeat Texts"""

        st = self.st

        kint = self.kint_pull_positive()

        st.str_write("\r\n")  # 00/13 00/10  # "\x0D\x0A"
        st.str_write_form_or_form_pn("\x1B" "[" "{}L", pn=1)

        ktext = self.kdo_ins_n_till()
        for _ in range(kint - 1):
            st.str_write("\r\n")  # 00/13 00/10  # "\x0D\x0A"

            ktext_kint = len(ktext.splitlines())
            if ktext_kint:
                st.str_write_form_or_form_pn("\x1B" "[" "{}L", pn=ktext_kint)
                st.str_write(ktext)  # for .kdo_line_ins_below_n Insert
                st.str_write_form_or_form_pn("\x1B" "[" "{}D", pn=ktext_kint)

        # Disassemble these StrTerminal Writes

        assert LF == "\n"  # 00/10 Line Feed (LF) ⌃J
        assert CR == "\r"  # 00/13 Carriage Return (CR) ⌃M

        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left
        assert IL_Y == "\x1B" "[" "{}L"  # CSI 04/12 Insert Line

        # Vim O
        # Pq O repeats even when ⌃C quits I, not ⌃G ⎋ ⌃\  # Vim O doesn't

    #
    # Cut before Insert
    #

    def kdo_char_cut_left_n_ins_till(self) -> None:
        """Delete N Chars to the Left, but from this Line only, and then Insert"""

        self.kdo_char_cut_left_n()

        peek_else = self.kint_peek_else()
        assert peek_else is None, (peek_else,)

        self.kdo_ins_n_till()

        # Pq ⌃U - ... S = Vim ⇧X + Vim I

    def kdo_char_cut_right_n_ins_till(self) -> None:
        """Delete N Chars to the Right, but from this Line only, and then Insert"""

        self.kdo_char_cut_right_n()

        peek_else = self.kint_peek_else()
        assert peek_else is None, (peek_else,)

        self.kdo_ins_n_till()

        # Vim S = Vim X + Vim I

    def kdo_dents_cut_n_line_ins_above(self) -> None:
        """Cut N Lines here and below, land past Dent, and then Insert"""

        self.kdo_dents_cut_n()

        peek_else = self.kint_peek_else()
        assert peek_else is None, (peek_else,)

        self.kdo_line_ins_above_n()

        # Vim ⇧S = Vim D D + Vim ⇧O

    def kdo_tail_cut_n_ins_till(self) -> None:
        """Cut N Lines here and below, land past Dent, and then Insert"""

        self.kdo_tail_cut_n()

        peek_else = self.kint_peek_else()
        assert peek_else is None, (peek_else,)

        self.kdo_ins_n_till()

        # Vim ⇧C = Vim ⇧D + Vim I  # same effect as Vim C $

    def kdo_cut_to_read_eval_ins_till(self) -> None:
        """Cut like Vim D would, then Insert 1 Empty Line above, then Insert Till"""

        st = self.st

        assert IL_Y == "\x1B" "[" "{}L"  # CSI 04/12 Insert Line

        #

        yxjumps_else = self.kdo_cut_to_read_eval()
        if yxjumps_else is None:
            return

        yxjumps = yxjumps_else
        (yjump, xjump) = yxjumps

        #

        peek_else = self.kint_peek_else()
        assert peek_else is None, (peek_else,)

        if yjump >= 0:
            if yjump:
                st.str_write_form_or_form_pn("\x1B" "[" "{}L", pn=1)
            self.kdo_ins_n_till()

        # Vim C
        # Vim C C  # Vim CC

    def kdo_cut_to_read_eval(self) -> tuple[int, int] | None:  # noqa C901 too complex
        """Read & eval the next Verb, but cut the Lines or Columns involved"""

        kcap_str = self.kcap_str
        st = self.st

        assert BS == "\b"  # 00/08 Backspace ⌃H
        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up

        # Decide to do, or not to do

        yxjumps_else = self.read_eval_to_yxjumps_else()
        if yxjumps_else is None:
            return None

        yxjumps = yxjumps_else
        (yjump, xjump) = yxjumps

        peek_else = self.kint_peek_else()
        assert peek_else is None, (peek_else,)

        # Patch in the irregular definitions of repeated Vim D $ and Vim C $

        if yjump < -1:
            if self.kcap_str in ("⌃E", "$"):

                if xjump < 0:
                    self.kint_push_positive(-xjump)
                    self.kdo_char_minus_n()
                elif xjump > 0:
                    self.kint_push_positive(xjump)
                    self.kdo_char_plus_n()

                self.kint_push_positive((-yjump) - 1)
                self.kdo_line_minus_n()

                self.kint_push_positive(-yjump)
                self.kdo_tail_cut_n()

                if kcap_str == "D":
                    st.str_write("\b")  # 00/08 Backspace (BS) \b ⌃H

                    # todo: more flexible keymaps of Vim D $ vs Vim C $

                return (yjump, xjump)

            # todo: more flexible keymaps of Pq ⌃E and Vim D $ vs Vim C $

        # Cut zero or more Chars inside one Line

        if yjump == 0:
            if xjump < 0:  # if gone right
                self.kint_push_positive(-xjump)
                self.kdo_char_cut_left_n()
            elif xjump > 0:  # if gone left
                self.kint_push_positive(xjump)
                self.kdo_char_cut_right_n()

            if xjump > 0:
                if self.kcap_str in ("⌃E", "$"):
                    if kcap_str == "D":
                        st.str_write("\b")  # 00/08 Backspace (BS) \b ⌃H

                        # todo: more flexible keymaps of Pq ⌃E and Vim D $ vs Vim C $

            return (yjump, xjump)

        # Else cut one or more Lines

        if yjump < -1:
            yjump_minus = (-yjump) - 1
            st.str_write_form_or_form_pn("\x1B" "[" "{}A", pn=yjump_minus)

        self.kint_push_positive(abs(yjump))
        self.kdo_dents_cut_n()

        return (yjump, xjump)

        # Vim D
        # Vim D D  # Vim DD
        # part of Vim C

    def read_eval_to_yxjumps_else(self) -> tuple[int, int] | None:
        """Read & eval the next Verb, but also count the Lines or Columns involved"""

        kcap_str = self.kcap_str

        st = self.st
        column_x = st.column_x
        row_y = st.row_y

        # Take the next Move from the Keyboard,
        # except when already implied, like by << >> CC DD

        adverbs = ("<", ">", "C", "D")  # todo: more arbitrary Key Maps of Adverbs
        assert kcap_str in adverbs, (kcap_str,)

        self.kphrase_read()  # for .read_eval_to_gaps
        # Vim D and Vim C accept : Q ! Return etc, but reject ⇧Z ⇧Q etc

        xjump = 0
        if self.kcap_str != kcap_str:

            if self.kcap_str in adverbs:
                late_kcap_str = self.kcap_str
                self.kcap_str = kcap_str
                self.kdo_kcap_alarm_write_n()  # Adverb of Adverb   # Vim <, Vim >, Vim C, Vim D
                self.kcap_str = late_kcap_str
                self.kdo_kcap_alarm_write_n()  # Adverb of Adverb   # Vim <, Vim >, Vim C, Vim D
                return None

            self.kchords_eval(vmode="Meta")  # for .kdo_cut_to_read_eval
            self.st_pull_cursor_always_and_keyboard_maybe()  # resamples Cursor, after Eval

            # Mark zero or more Columns within 1 Line

            xjump = column_x - st.column_x
            if st.row_y == row_y:
                self.pqprint(f"yjump=0 {xjump=}")
                return (0, xjump)

            peek_else = self.kint_peek_else()
            assert peek_else is None, (peek_else,)

        # Move up or down, if so asked  # Vim DD  # Vim CC  # Vim <<  # Vim >>

        kint = self.kint_pull(default=1)
        if not kint:
            self.pqprint("yjump=0 xjump=0")
            return (0, 0)

        if kint != 1:
            if kint < 0:
                self.kint_push(-kint)
                self.kdo_line_minus_n()
                self.st_pull_cursor_always_and_keyboard_maybe()  # resamples Cursor, after Eval
            elif kint < 2:
                assert False, (kint,)
            elif kint > 1:
                self.kint_push(kint - 1)
                self.kdo_line_plus_n()
                self.st_pull_cursor_always_and_keyboard_maybe()  # resamples Cursor, after Eval

        # Mark one or more Lines: the first Line, the last Line, and any Lines in between

        if st.row_y < row_y:  # if gone up
            yjump = row_y - st.row_y + 1
        else:  # if gone down, or if not gone up/down
            assert st.row_y >= row_y, (row_y, st.row_y)
            yjump = st.row_y - row_y + 1
            yjump = -yjump

        self.pqprint(f"{yjump=} {xjump=}")
        return (yjump, xjump)

    #
    # Scroll Rows
    #

    def kdo_add_last_row(self) -> None:
        """Insert new Bottom Rows, and move Cursor Up by that much"""

        st = self.st

        kint = self.kint_pull_positive()
        st.str_write_form_or_form_pn("\x1B" "[" "{}S", pn=kint)
        st.str_write_form_or_form_pn("\x1B" "[" "{}A", pn=kint)

        # Disassemble these StrTerminal Writes

        assert SU_Y == "\x1B" "[" "{}S"  # CSI 05/03 Scroll Up   # Add Bottom Rows
        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up

        # Vim ⌃Y
        # collides with Emacs ⌃Y yank

    def kdo_add_top_row(self) -> None:
        """Insert new Top Rows, and move Cursor Down by that much"""

        st = self.st

        kint = self.kint_pull_positive()
        st.str_write_form_or_form_pn("\x1B" "[" "{}T", pn=kint)
        st.str_write_form_or_form_pn("\x1B" "[" "{}B", pn=kint)

        # Disassemble these StrTerminal Writes

        assert SD_Y == "\x1B" "[" "{}T"  # CSI 05/04 Scroll Down  # Add Top Rows
        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down

        # Vim ⌃E
        # collides with Emacs ⌃E move-end-of-line


STOP_KCAP_STRS = ("⌃C", "⌃G", "⌃L", "⎋", "⌃\\")  # ..., b'\x1B, b'\x1C'


LT = LineTerminal


INSERT_PQ_KDO_CALL_BY_KCAP_STR: dict[str, PY_CALL]
EM_KDO_CALL_BY_KCAP_STR: dict[str, PY_CALL]
VI_KDO_CALL_BY_KCAP_STR: dict[str, PY_CALL]
PQ_KDO_CALL_BY_KCAP_STR: dict[str, PY_CALL]

KDO_CALL_BY_KCAP_STR: dict[str, PY_CALL]


INSERT_PQ_KDO_CALL_BY_KCAP_STR = {
    "Return": (LT.kdo_line_ins_behind_mostly_n,),  # b'\x0D'  # b'\r'
    "Delete": (LT.kdo_char_cut_left_n,),  # b'\x7F'
    "⌃H": (LT.kdo_char_cut_left_n,),  # b'\x08'
}
# "⌃W": (LT.kdo_word_cut_left_n,),  # b'\x04'
# "⌃U": (LT.kdo_empty_line_n,),  # b'\x15'

# todo: Vim ⌃W is a delete-last-word


EM_KDO_CALL_BY_KCAP_STR = {
    #
    "⎋-": (LT.kdo_hold_start_kstr, ("-",)),
    "⎋0": (LT.kdo_hold_start_kstr, ("0",)),
    "⎋1": (LT.kdo_hold_start_kstr, ("1",)),
    "⎋2": (LT.kdo_hold_start_kstr, ("2",)),
    "⎋3": (LT.kdo_hold_start_kstr, ("3",)),
    "⎋4": (LT.kdo_hold_start_kstr, ("4",)),
    "⎋5": (LT.kdo_hold_start_kstr, ("5",)),
    "⎋6": (LT.kdo_hold_start_kstr, ("6",)),
    "⎋7": (LT.kdo_hold_start_kstr, ("7",)),
    "⎋8": (LT.kdo_hold_start_kstr, ("8",)),
    "⎋9": (LT.kdo_hold_start_kstr, ("9",)),
    "⎋<": (LT.kdo_line_first_tenths_n,),
    "⎋>": (LT.kdo_line_last_tenths_n,),
    "⎋G G": (LT.kdo_home_line_n,),
    "⎋G ⎋G": (LT.kdo_home_line_n,),
    "⎋G Tab": (LT.kdo_column_n_plus,),
    "⎋R": (LT.kdo_row_n_else_middle_first_last,),
    "⌃A": (LT.kdo_home_plus_n1,),  # b'\x01'
    "⌃B": (LT.kdo_char_minus_n,),  # b'\x02'
    "⌃D": (LT.kdo_char_cut_right_n,),  # b'\x04'
    "⌃E": (LT.kdo_end_plus_n1,),  # b'\x05'
    "⌃F": (LT.kdo_char_plus_n,),  # b'\x06'
    "⌃K": (LT.kdo_tail_head_cut_n,),  # b'\x0B'
    "⌃N": (LT.kdo_line_plus_n,),  # b'\x0E'
    "⌃O": (LT.kdo_line_ins_ahead_n,),  # b'\x0B'
    "⌃P": (LT.kdo_line_minus_n,),  # b'\x10'
    "⌃Q": (LT.kdo_quote_kchars,),  # b'\x11'
    "⌃U": (LT.kdo_hold_start_kstr, ("⌃U",)),  # b'\x15'
    # "⌃X 8 Return": (LT.unicodedata_lookup,),  # Emacs insert-char
    "→": (LT.kdo_char_plus_n,),  # b'\x1B[C'  # Emacs wraps → like ⌃F
    "←": (LT.kdo_char_minus_n,),  # b'\x1B[D'  # Emacs wraps ← like ⌃B
    #
    "⌥←": (LT.kdo_bigword_minus_n,),  # encoded as ⎋B  # can be from ⎋←
    "⌥→": (LT.kdo_bigword_plus_n,),  # encoded as ⎋F  # can be from ⎋→
    # "⌥-": (LT.kdo_hold_start_kstr, ("-",)),  # nope, because – En Dash
    # "⌥0": (LT.kdo_hold_start_kstr, ("0",)),  # nope, because ¡ Inverted Exclamation M~
    # "⌥1": (LT.kdo_hold_start_kstr, ("1",)),  # nope, because ™ Trade Mark Sign
    # "⌥2": (LT.kdo_hold_start_kstr, ("2",)),  # nope, because £ Pound Sign
    # "⌥3": (LT.kdo_hold_start_kstr, ("3",)),  # nope, because ¢ Cent Sign
    # "⌥4": (LT.kdo_hold_start_kstr, ("4",)),  # nope, because ∞ Infinity
    # "⌥5": (LT.kdo_hold_start_kstr, ("5",)),  # nope, because § Section Sign
    # "⌥6": (LT.kdo_hold_start_kstr, ("6",)),  # nope, because ¶ Pilcrow Sign
    # "⌥7": (LT.kdo_hold_start_kstr, ("7",)),  # nope, because • Bullet
    # "⌥8": (LT.kdo_hold_start_kstr, ("8",)),  # nope, because ª Feminine Ordinal I~
    # "⌥9": (LT.kdo_hold_start_kstr, ("9",)),  # nope, because º Masculine Ordinal I~
    "⌥<": (LT.kdo_line_first_tenths_n,),
    "⌥>": (LT.kdo_line_last_tenths_n,),
    "⌥G G": (LT.kdo_home_line_n,),
    "⌥G ⌥G": (LT.kdo_home_line_n,),
    "⌥G Tab": (LT.kdo_column_n_plus,),
    "⌥R": (LT.kdo_row_n_else_middle_first_last,),
    #
}


VI_KDO_CALL_BY_KCAP_STR = {
    #
    "Return": (LT.kdo_dent_plus_n,),  # b'\x0D'  # b'\r'
    "⌃E": (LT.kdo_add_last_row,),  # b'\x05'
    "⌃H": (LT.kdo_char_minus_n,),  # b'\x08'
    "⌃J": (LT.kdo_line_plus_n,),  # b'\x0A'  # b'\n'
    "⌃V": (LT.kdo_quote_kchars,),  # b'\x16'
    "⌃Y": (LT.kdo_add_top_row,),  # b'\x19'
    "↑": (LT.kdo_line_minus_n,),  # b'\x1B[A'
    "↓": (LT.kdo_line_plus_n,),  # b'\x1B[B'
    "→": (LT.kdo_column_plus_n,),  # b'\x1B[C'  # Vim doesn't wrap → like Spacebar
    "←": (LT.kdo_column_minus_n,),  # b'\x1B[D'  # Vim doesn't wrap ← like Delete
    #
    "Spacebar": (LT.kdo_char_plus_n,),  # b'\x20'
    "$": (LT.kdo_end_plus_n1,),  # b'\x24'
    "+": (LT.kdo_dent_plus_n,),  # b'\x2B'
    "-": (LT.kdo_kminus,),  # b'\x2D'
    "0": (LT.kdo_kzero,),  # b'0'
    "1": (LT.kdo_hold_start_kstr, ("1",)),
    "2": (LT.kdo_hold_start_kstr, ("2",)),
    "3": (LT.kdo_hold_start_kstr, ("3",)),
    "4": (LT.kdo_hold_start_kstr, ("4",)),
    "5": (LT.kdo_hold_start_kstr, ("5",)),
    "6": (LT.kdo_hold_start_kstr, ("6",)),
    "7": (LT.kdo_hold_start_kstr, ("7",)),
    "8": (LT.kdo_hold_start_kstr, ("8",)),
    "9": (LT.kdo_hold_start_kstr, ("9",)),
    "<": (LT.kdo_lines_dedent_n,),  # b'<'  # <
    ">": (LT.kdo_lines_dent_n,),  # b'>'  # >
    #
    "⇧A": (LT.kdo_end_plus_ins_n_till,),  # b'A'
    "⇧B": (LT.kdo_bigword_minus_n,),  # b'B'
    "⇧C": (LT.kdo_tail_cut_n_ins_till,),  # b'C'
    "⇧D": (LT.kdo_tail_cut_n_column_minus,),  # b'D'
    "⇧E": (LT.kdo_bigword_plus_n_almost,),  # b'E'
    "⇧G": (LT.kdo_dent_line_n_else_last,),  # b'G'
    "⇧H": (LT.kdo_row_n_down,),  # b'H'
    "⇧I": (LT.kdo_column_dent_ins_n_till,),  # b'I'
    "⇧L": (LT.kdo_row_n_up,),  # b'L'
    "⇧M": (LT.kdo_row_middle,),  # b'M'
    "⇧O": (LT.kdo_line_ins_above_n,),  # b'O'
    "⇧R": (LT.kdo_replace_n_till,),  # b'R'
    "⇧S": (LT.kdo_dents_cut_n_line_ins_above,),  # b'S'
    "⇧W": (LT.kdo_bigword_plus_n,),  # b'W'
    "⇧X": (LT.kdo_char_cut_left_n,),  # b'X'
    "^": (LT.kdo_column_dent,),  # b'\x5E'
    "_": (LT.kdo_dent_plus_n1,),  # b'\x5F'
    #
    "A": (LT.kdo_column_plus_ins_n_till,),  # b'a'
    "B": (LT.kdo_lilword_minus_n,),  # b'b'
    "C": (LT.kdo_cut_to_read_eval_ins_till,),  # b'c'
    "D": (LT.kdo_cut_to_read_eval,),  # b'd' b'd'
    "E": (LT.kdo_lilword_plus_n_almost,),  # b'e'
    "G G": (LT.kdo_dent_line_n_else_first,),  # b'GG'
    "H": (LT.kdo_column_minus_n,),  # b'h'
    "I": (LT.kdo_ins_n_till,),  # b'i'
    "J": (LT.kdo_line_plus_n,),  # b'j'
    "K": (LT.kdo_line_minus_n,),  # b'k'
    "L": (LT.kdo_column_plus_n,),  # b'l'
    # "M M": (LT.kdo_mark_m_place_here,),  # b'mm'
    # "' M": (LT.kdo_mark_m_jump_to,),  # b"'m"
    # "' '": (LT.kdo_marks_swap_ish,),  # b"''"
    "O": (LT.kdo_line_ins_below_n,),  # b'o'
    "R": (LT.kdo_replace_n_once,),  # b'r'
    "S": (LT.kdo_char_cut_right_n_ins_till,),  # b's'
    "W": (LT.kdo_lilword_plus_n,),  # b'w'
    "X": (LT.kdo_char_cut_right_n,),  # b'x'
    "|": (LT.kdo_column_n,),  # b'\x7C'
    "Delete": (LT.kdo_char_minus_n,),  # b'\x7F'
    #
}


PQ_KDO_CALL_BY_KCAP_STR = {
    #
    "⎋": (LT.kdo_hold_stop_kstr,),
    "⎋⎋": (LT.kdo_help_quit,),  # Meta Esc
    "⎋[": (LT.kdo_quote_csi_kstrs_n,),  # b'\x1B\x5B'  # Option [
    #
    "⌃C": (LT.kdo_hold_stop_kstr,),  # b'\x03'  # SIGINT
    "⌃D": (LT.kdo_char_cut_right_n,),  # b'\x04'  # SIGHUP  # Pq like macOS/ Emacs
    "⌃E": (LT.kdo_end_plus_n1,),  # b'\x05'  # Pq like macOS/ Emacs
    "⌃G": (LT.kdo_hold_stop_kstr,),  # b'\x07'
    "⌃H": (LT.kdo_kcap_alarm_write_n,),  # b'\x08'  # till Pq ⌃H Help like Emacs
    "Tab": (LT.kdo_tab_plus_n,),  # b'\x09'  # b'\t'
    "⌃L": (LT.kdo_hold_stop_kstr,),  # b'\x07'
    "⌃L : Q Return": (LT.kdo_quit_no_save,),  # b'\x0C...
    "⌃L : Q ! Return": (LT.kdo_quit_no_save,),  # b'\x0C...
    "⌃L : W Q Return": (LT.kdo_save_quit,),  # b'\x0C...
    "⌃L : W Q ! Return": (LT.kdo_save_quit,),  # b'\x0C...
    "⌃L ⇧Z ⇧Q": (LT.kdo_save_quit,),  # b'\x0C...
    "⌃L ⇧Z ⇧Z": (LT.kdo_save_quit,),  # b'\x0C...
    # "⌃Q ⌃Q": (LT.kdo_quote_kchars,),  # b'\x11...  # no, go with ⌃V ⌃Q
    # "⌃V ⌃V": (LT.kdo_quote_kchars,),  # b'\x16...  # no, go with ⌃Q ⌃V
    "⌃X ⌃C": (LT.kdo_quit_no_save,),  # b'\x18...
    "⌃X ⌃S": (LT.kdo_save_quit,),  # b'\x18...  # "⌃X ⌃S ⌃X ⌃C":
    "⌃Z": (LT.kdo_terminal_stop,),  # b'\x1A'  # SIGTSTP
    "⇧Tab": (LT.kdo_tab_minus_n,),  # b'\x1B[Z'
    "⌃\\": (LT.kdo_hold_stop_kstr,),  # ⌃\  # b'\x1C'
    #
    ": Q Return": (LT.kdo_quit_no_save,),  # b':q\r'
    ": Q ! Return": (LT.kdo_quit_no_save,),  # b':q!\r'
    ": W Q Return": (LT.kdo_save_quit,),  # b':wq\r'
    ": W Q ! Return": (LT.kdo_save_quit,),  # b':wq!\r'
    "⇧Q V I Return": (LT.kdo_help_quit,),  # b'Qvi\r'
    "⇧Z ⇧Q": (LT.kdo_quit_no_save,),  # b'ZQ'
    "⇧Z ⇧Z": (LT.kdo_save_quit,),  # b'ZZ'
    "[": (LT.kdo_quote_csi_kstrs_n,),  # b'\x5B'
    #
    "⌥[": (LT.kdo_quote_csi_kstrs_n,),  # b'\xE2\x80\x9C'  # Option [
    #
}


assert KCAP_SEP == " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc

for _KCS, _CALL in EM_KDO_CALL_BY_KCAP_STR.items():
    _KCAP_STR = "⌃V" + " " + _KCS
    if _KCAP_STR not in PQ_KDO_CALL_BY_KCAP_STR.keys():
        PQ_KDO_CALL_BY_KCAP_STR[_KCAP_STR] = _CALL

for _KCS, _CALL in VI_KDO_CALL_BY_KCAP_STR.items():
    _KCAP_STR = "⌃Q" + " " + _KCS
    if _KCAP_STR not in PQ_KDO_CALL_BY_KCAP_STR.keys():
        PQ_KDO_CALL_BY_KCAP_STR[_KCAP_STR] = _CALL

KDO_CALL_BY_KCAP_STR = dict()
KDO_CALL_BY_KCAP_STR.update(INSERT_PQ_KDO_CALL_BY_KCAP_STR)
KDO_CALL_BY_KCAP_STR.update(EM_KDO_CALL_BY_KCAP_STR)
KDO_CALL_BY_KCAP_STR.update(VI_KDO_CALL_BY_KCAP_STR)
KDO_CALL_BY_KCAP_STR.update(PQ_KDO_CALL_BY_KCAP_STR)

KDO_CALL_KCAP_STRS = sorted(KDO_CALL_BY_KCAP_STR.keys())

# hand-sorted as ⎋, ⌃, 0..9, ⇧A..⇧Z, A..Z order of K Bytes
# not so much by ⎋ ⌃ ⌥ ⇧ ⌘ Fn order

# todo: Emacs ⌃U - for non-positive K-Int

# todo: assert Keys of KDO_CALL_BY_KCAP_STR reachable by StrTerminal
#   such as ⌥ ⎋ never reached as Option Esc, despite ⎋ ⎋ reached as Meta Esc
#   such as '⎋' less reachable while '⎋ G Tab' defined
#       because 'kdo_call_kcap_strs'


# Run these K Do Func's as is when called with positive Arg,
#   as paired when called with negative Arg, and as nothing when called with zeroed Arg

KDO_INVERSE_FUNC_BY = {
    LT.kdo_add_last_row: LT.kdo_add_top_row,  # Vim ⌃E
    LT.kdo_add_top_row: LT.kdo_add_last_row,  # Vim ⌃Y
    LT.kdo_bigword_minus_n: LT.kdo_bigword_plus_n,  # Vim ⇧B  # Emacs ⌥→
    LT.kdo_bigword_plus_n: LT.kdo_bigword_minus_n,  # Vim ⇧W  # Emacs ⌥→
    LT.kdo_char_cut_left_n: LT.kdo_char_cut_right_n,  # Vim I Delete
    LT.kdo_char_cut_right_n: LT.kdo_char_cut_left_n,  # Emas ⌃D
    LT.kdo_char_minus_n: LT.kdo_char_plus_n,  # Vim Delete  # Emacs ⌃B ←
    LT.kdo_char_plus_n: LT.kdo_char_minus_n,  # Vim Spacebar  # Emacs ⌃F →
    LT.kdo_column_minus_n: LT.kdo_column_plus_n,  # Vim ← H
    LT.kdo_column_plus_n: LT.kdo_column_minus_n,  # Vim → L
    LT.kdo_dent_minus_n: LT.kdo_dent_plus_n,  # Vim -
    LT.kdo_dent_plus_n: LT.kdo_dent_minus_n,  # Vim Return +
    LT.kdo_end_plus_n1: LT.kdo_home_plus_n1,  # Emacs ⌃E
    LT.kdo_home_plus_n1: LT.kdo_end_plus_n1,  # Emacs ⌃A
    LT.kdo_lilword_minus_n: LT.kdo_lilword_plus_n,  # Vim B
    LT.kdo_lilword_plus_n: LT.kdo_lilword_minus_n,  # Vim W
    LT.kdo_line_minus_n: LT.kdo_line_plus_n,  # ↓ ⌃J J  # Emacs ⌃N
    LT.kdo_line_plus_n: LT.kdo_line_minus_n,  # ↑ K  # Emacs ⌃P
    LT.kdo_lines_dedent_n: LT.kdo_lines_dent_n,  # Vim <<
    LT.kdo_lines_dent_n: LT.kdo_lines_dedent_n,  # Vim >>
    LT.kdo_row_n_down: LT.kdo_row_n_up,  # Vim ⇧L
    LT.kdo_row_n_up: LT.kdo_row_n_down,  # Vim ⇧H
    LT.kdo_tab_minus_n: LT.kdo_tab_plus_n,  # Pq Tab ⇥
    LT.kdo_tab_plus_n: LT.kdo_tab_minus_n,  # Pq ⇧Tab ⇤
    LT.kdo_char_cut_right_n_ins_till: LT.kdo_char_cut_left_n_ins_till,  # Vim S
    LT.kdo_char_cut_left_n_ins_till: LT.kdo_char_cut_right_n_ins_till,  # (unbound)
}

for _K, _V in KDO_INVERSE_FUNC_BY.items():
    assert _K != _V, (_K, _V)


# Run these K Do Func's with positive Arg, else reject non-positive Arg

KDO_ONLY_POSITIVE_FUNCS = [
    LT.kdo_bigword_plus_n_almost,  # Vim ⇧E
    LT.kdo_column_dent_ins_n_till,  # Vim ⇧I
    LT.kdo_dent_plus_n1,  # Vim _
    LT.kdo_dents_cut_n,  # (not bound lately)
    LT.kdo_ins_n_till,  # Vim I
    LT.kdo_lilword_plus_n_almost,  # Vim E
    LT.kdo_line_ins_above_n,  # Vim ⇧O
    LT.kdo_line_ins_behind_mostly_n,  # Emacs Return, Vim I Return
    LT.kdo_replace_n_once,  # Vim R
    LT.kdo_replace_n_till,  # Vim ⇧R
]

for _K1 in KDO_INVERSE_FUNC_BY.keys():
    assert _K1 not in KDO_ONLY_POSITIVE_FUNCS, (_K1,)

for _K2 in KDO_ONLY_POSITIVE_FUNCS:
    assert _K2 not in KDO_INVERSE_FUNC_BY.keys(), (_K2,)


# Run these K Do Func's with No Arg, else reject Arg

KDO_ONLY_WITHOUT_ARG_FUNCS = [
    LT.kdo_column_dent,  # Vim ^
    LT.kdo_row_middle,  # Vim ⇧M
]


'''


#
# Amp up Import TextWrap
#


def text_to_grafs(text) -> list[list[str]]:
    """Form a List of Paragraphs, each encoded as a List of Lines"""

    dedent = textwrap.dedent(text)
    splitlines = dedent.splitlines()
    grafs = list(list(v) for k, v in itertools.groupby(splitlines, key=bool) if k)

    list_assert_eq(grafs, b=list(graf_deframe(_) for _ in grafs))  # rstripped etc

    return grafs


#
# Amp up Import UnicodeData
#


def unicodedata_name_anyhow(char) -> str:
    """Supply the Unicode Names that UnicodeData mystically omits"""

    assert unicodedata.name("\xa0").title() == "No-Break Space"
    assert unicodedata.name("\xad").title() == "Soft Hyphen"

    try:
        name = unicodedata.name(char)
        assert False, (name, hex(ord(char)), ascii(char))
    except ValueError as exc:
        assert str(exc) == "no such name"

    names = UNICODEDATA_NAMES_ANYHOW_BY_CHAR[char]
    for name in names:
        try:
            _ = unicodedata.lookup(name)
        except KeyError:
            assert name == "EM", (name, sys.version_info)
            continue

            # Tracebacks till some later Python did say:  KeyError: "undefined character name 'EM'"
            # "EM" seen working at Dec/2024 Python 3.13.1 of Oct/2024 Python 3.13
            # "EM" seen broken at Jun/2023 Python 3.10.12 of Oct/2021 Python 3.10

            # unicodedata.lookup("End of Medium") began working before .lookup("EM")

        assert unicodedata.lookup(name) == char, (name, hex(ord(char)), ascii(char))

    name_0 = names[0]

    return name_0

    # pq emojis unicodedata >~/e


UNICODEDATA_NAMES_ANYHOW_BY_CHAR = {  # omitting x 80 81 99 and x A0 AD
    "\x00": ("Null", "NUL"),
    "\x01": ("Start Of Heading", "SOH"),
    "\x02": ("Start Of Text", "STX"),
    "\x03": ("End Of Text", "ETX"),
    "\x04": ("End of Transmission", "EOT"),
    "\x05": ("Enquiry", "ENQ"),
    "\x06": ("Acknowledge", "ACK"),
    "\x07": ("BEL",),  # Bell  # != unicode.lookup("Bell"), U+01F514
    "\x08": ("Backspace", "BS"),
    "\x09": ("Character Tabulation", "HT"),  # Horizontal Tabulation
    "\x0a": ("Line Feed", "LF"),
    "\x0b": ("Line Tabulation", "VT"),  # Vertical Tabulation
    "\x0c": ("Form Feed", "FF"),
    "\x0d": ("Carriage Return", "CR"),
    "\x0e": ("Shift Out", "SO"),
    "\x0f": ("Shift In", "SI"),
    "\x10": ("Data Link Escape", "DLE"),
    "\x11": ("Device Control One", "DC1"),
    "\x12": ("Device Control Two", "DC2"),
    "\x13": ("Device Control Three", "DC3"),
    "\x14": ("Device Control Four", "DC4"),
    "\x15": ("Negative Acknowledge", "NAK"),
    "\x16": ("Synchronous Idle", "SYN"),
    "\x17": ("End Of Transmission Block", "ETB"),
    "\x18": ("Cancel", "CAN"),
    "\x19": ("End Of Medium", "EM"),
    "\x1a": ("Substitute", "SUB"),
    "\x1b": ("Escape", "ESC"),
    "\x1c": ("Information Separator Four", "FS"),  # File Separator
    "\x1d": ("Information Separator Three", "GS"),  # Group Separator
    "\x1e": ("Information Separator Two", "RS"),  # Record Separator
    "\x1f": ("Information Separator One", "US"),  # Unit Separator
    "\x7f": ("Delete", "DEL"),
    "\x82": ("Break Permitted Here", "BPH"),  # ! = "Zero Width Space" U+200B ZWSP
    "\x83": ("No Break Here", "NBH"),  # != "Word Joiner" U+2060 WJ
    "\x84": ("Index", "IND"),
    "\x85": ("Next Line", "NEL"),
    "\x86": ("Start of Selected Area", "SSA"),
    "\x87": ("End of Selected Area", "ESA"),
    "\x88": ("Character Tabulation Set", "HTS"),
    "\x89": ("Character Tabulation With Justification", "HTJ"),
    "\x8a": ("Line Tabulation Set", "VTS"),
    "\x8b": ("Partial Line Forward", "PLD"),
    "\x8c": ("Partial Line Backward", "PLU"),
    "\x8d": ("Reverse Line Feed", "RI"),
    "\x8e": ("Single Shift Two", "SS2"),
    "\x8f": ("Single Shift Three", "SS3"),
    "\x90": ("Device Control String", "DCS"),
    "\x91": ("Private Use One", "PU1"),
    "\x92": ("Private Use Two", "PU2"),
    "\x93": ("Set Transmit State", "STS"),
    "\x94": ("Cancel Character", "CCH"),
    "\x95": ("Message Waiting", "MW"),
    "\x96": ("Start of Guarded Area", "SPA"),
    "\x97": ("End of Guarded Area", "EPA"),
    "\x98": ("Start of String", "SOS"),
    "\x9a": ("Single Character Introducer", "SCI"),
    "\x9b": ("Control Sequence Introducer", "CSI"),
    "\x9c": ("String Terminator", "ST"),
    "\x9d": ("Operating System Command", "OSC"),
    "\x9e": ("Privacy Message", "PM"),
    "\x9f": ("Application Program Command", "APC"),
}


#
# List Grafs of Emoji Py Code to Abbreviate Intensely
#


def fetch_less_by_more_emoji_py_texts() -> dict[str, str]:
    """Auto-complete Py Grafs out of the 'unicodedata.name's"""

    less_by_more = dict()
    for i in range(0x110000):
        char = chr(i)

        if (0x00 <= i <= 0x1F) or (0x7F <= i < 0xA0):
            if i in (0x80, 0x81, 0x99):  # unnamed by ISO/IEC 6429:1992 in U0080.pdf
                continue
            name = unicodedata_name_anyhow(char)
        else:
            try:  # names found for \xA0 \xAD etc
                name = unicodedata.name(char)
            except ValueError as exc:  # at \x0A unicodedata.lookup("Line Feed") etc
                assert str(exc) == "no such name"
                continue

        lit = black_repr(name.title())
        tail = f"  # {char}" if char.isprintable() else ""

        if i == ord("'"):
            more_text = rf"""print('''assert hex(unicodedata.lookup({lit})) == 0x{i:04X}{tail} '''.rstrip())"""
        elif i == ord("\\"):
            more_text = rf"""print('''assert hex(unicodedata.lookup({lit})) == 0x{i:04X}{tail} '''.rstrip())"""
        elif i < 0x10000:
            assert len(f"{i:04X}") <= 4, (i,)
            more_text = rf"""print('''assert hex(unicodedata.lookup({lit})) == 0x{i:04X}{tail}''')"""
        else:
            more_text = rf"""print('''assert hex(unicodedata.lookup({lit})) == 0x{i:06X}{tail}''')"""

        less_text = more_text.partition("#")[0].rstrip()

        less_by_more[more_text] = less_text

    return less_by_more

    # todo: |cv default for:  pq emoji
    # todo: add some form of 'pq emoji .' into 'make slow'


#
# List Grafs of Awkish Py Code to Abbreviate Intensely
#


def graf_deframe(graf) -> list[str]:
    """Drop the top, left, right, and bottom margins"""

    text = "\n".join(graf)
    text = textwrap.dedent(text)
    text = text.strip()

    lines = list(_.rstrip() for _ in text.splitlines())

    return lines


#
# List Grafs of Awkish Py Code to Abbreviate Intensely
#


# todo: reject multiline snippets from the CUED_PY_LINES_TEXT
# todo: reject single-line snippets that don't have comments to name them

CUED_PY_LINES_TEXT = r"""


    iolines.reverse()  # reverse  # reversed  # |tac  # |tail -r  # tail r

    iolines.sort()  # sort  # sorted sorted  # s s s s s s s s s s


    obytes = b"\n".join(ibytes.splitlines()) + b"\n"  # bytes ended

    obytes = ibytes  # sponged  # sponge  # obytes = ibytes

    # obytes = pq.bytes_terminal_yolo(ibytes)  # bt yolo  # btyolo


    oline = (4 * " ") + iline  # dent  # dented  # textwrap.dented

    oline = ascii(iline)  # ascii  # |cat -etv  # cat etv  # shows $'\xA0' Nbsp

    oline = iline.lstrip()  # lstrip  # lstripped  # |sed 's,^ *,,'

    oline = iline.removeprefix(4 * " ")  # undent  # undented  # textwrap.undent

    oline = iline.rstrip()  # rstrip  # rstripped  # |sed 's, *$,,'

    oline = iline.strip()  # strip  # stripped  # |sed 's,^ *,,' |sed 's, *$,,'

    oline = re.sub(r" {8}", repl="\t", string=iline)  # unexpanded  # |unexpand

    oline = repr(iline)  # repr  # undo 'ast.literal_eval'  # |sed "s,.*,'&',"

    oline = repr(iline)[1:0-1]  # |cat -tv  # cat tv  # '"' comes out as \'"\'

    oline = str(ast.literal_eval(iline))  # eval  # undo 'ascii' or 'repr'


    olines = ilines  # olines = ilines  # olines = ilines  # end  # ended  # chr ended  # ends every line with "\n"

    # olines = pq.ex_macros(ilines)  # em em  # ema  # emac  # emacs

    # olines = pq.visual_ex(ilines)  # vi  # vim  # em vi  # em/vi

    # olines = pq.xeditline()  # xeditline


    oobject = "".join(chr(_) for _ in range(0x100))  # chr range

    oobject = len(ibytes)  # bytes len  # |wc -c  # wc c  # wcc

    oobject = len(itext)  # text characters chars len  # |wc -m  # wc m  # wcm

    oobject = len(itext.split())  # words len  # |wc -w  # wc w  # wcw

    oobject = len(itext.splitlines())  # lines len  # |wc -l  # wc l  # wcl

    oobject = math.e  # math.e  # not 'pq e' alone

    oobject = math.pi  # pi

    oobject = math.tau  # tau

    oobject = max(len(_) for _ in ilines)  # max len  # max len  # max

    oobject = max(len(_.split()) for _ in ilines)  # max len split  # max split


    otext = " ".join(itext)  # space

    otext = "".join(dict((_, _) for _ in itext).keys())  # text set  # text set

    otext = "".join(sorted(set(itext)))  # sorted text set

    otext = itext.casefold()  # casefold  # casefolded  # folded

    otext = itext.expandtabs(tabsize=8)  # |expand  # expand expand

    otext = itext.lower()  # lower  # lowered  # lowercased  # |tr '[A-Z]' '[a-z]'

    otext = itext.replace(" ", "")  # despace  # replace replace  # |tr -d ' '

    otext = itext.title()  # title  # titled

    otext = itext.upper()  # upper  # uppered uppercased  # |tr '[a-z]' '[A-Z]'

    otext = json.dumps(json.loads(itext), indent=2) + "\n"  # |jq .  # jq

    # otext = pq.shadow_terminal_yolo(itext)  # st  # st yolo  # styolo

    otext = pq.turtle_yolo(itext)  # turtle yolo

    otext = re.sub(r"(.)", repl=r"\1 ", string=itext).rstrip()  # sub  # repl

    otext = string.capwords(itext)  # capwords

    otext = textwrap.dedent(itext) + "\n"  # dedent  # dedented  # textwrap.dedent


    random.shuffle(iolines) # shuffle  # shuffled


"""


# todo: reject single-line snippets that don't have comments to name them
# todo: test  |pq '#'

CUED_PY_GRAFS_TEXT = r"""

    # !  # "  # $  # %  # &  # '  # (  # )  # *  # + + +  # ,  # - - -  # . . . . . . .  # /
    # 0  # 1 1  # 2 2  # 3 3  # 4  # 5 5  # 6 6  # 7  # 8  # 9  # :  # ;  # <  # =  # >  # ?
    # @
    # b b b
    # d d d d d d d d
    # e e e e e e
    # g g
    # i i i i i i i i i i i
    # j j
    # k
    # l l l l l l l
    # m m m
    # o o o o o o
    # p p p p p p
    # q
    # r r r r r r r r r
    # v v
    # w w w w
    # y y y
    # z
    # {  # | |  # }  # ~
    sys.stderr.write("Pq today defines a, c, f, h, n, s, t, u, x\n")  # and also '-'
    sys.stderr.write("Pq today doesn't define b, d, e, g, i, j, k, l, m, o, p, q, r, v, w, y, z\n")
    olines = ilines[0:0]
    sys.exit(1)

    # awk  # |awk '{print $NF}'  # a a a a
    iwords = iline.split()
    oline = iwords[-1] if iwords else ""

    # bytes range
    obytes = ibytes  # todo: say this without ibytes
    obytes = b"".join(bytes([_]) for _ in range(0x100))

    # c c c c  # cat cat  # cat - >/dev/null
    _ = itext
    sys.stderr.write("Press ⌃C, or Return ⌃D, to quit\n")
    try:
        otext = pathlib.Path("/dev/tty").read_text()
    except KeyboardInterrupt:
        sys.stderr.write("\nKeyboardInterrupt\n")
        otext = ""

    # cat n expand  # |cat -n |expand  # enum 1  # n n n n
    olines = list(f"{n:6d}  {i}" for (n, i) in enumerate(ilines, start=1))

    # closed # close  # ends last line with "\n"
    otext = itext if itext.endswith("\n") else (itext + "\n")

    # counter  # set set set  # uniq  # uniq_everseen  # u  # uu
    olines = collections.Counter(ilines).keys()  # unsort  # unsorted  # dedupe

    # decomment  # |sed 's,#.*,,' |sed 's, *$,,'  # |grep .
    dlines = list()
    for iline in ilines:
        dline = iline.partition("#")[0].rstrip()
        if dline:
            dlines.append(dline)
    olines = dlines

    # deframe  # deframed
    dedent = textwrap.dedent(itext) + "\n"  # no left margin
    dlines = dedent.splitlines()
    olines = list(_.rstrip() for _ in dlines)  # no right margin
    otext = "\n".join(olines).strip() + "\n"  # no top/bottom margins

    # emo  # emoji  # emojis
    sys.stderr.write("did you mean the huge:  pq emojis u" "nicodedata\n")
    sys.exit(2)  # todo: solve this more elegantly
    oobject = "did you mean the huge:  pq emojis u" "nicodedata"

    # find  # find  # find  # find  # f  # just the not-hidden files
    flines = list()
    # dirpath = None  # todo: doesn't help
    for dirpath, dirnames, filenames in os.walk("."):
        # locals()["dirpath"] = dirpath  # todo: doesn't help
        globals()["dirpath"] = dirpath  # todo: does help
        dirnames[::] = list(_ for _ in dirnames if not _.startswith("."))
        dirfiles = list(
            os.path.join(dirpath, _) for _ in filenames if not _.startswith(".")
        )
        flines.extend(sorted(_.removeprefix("./") for _ in dirfiles))
    olines = flines

    # find dirs  # find dirs  # find dirs  # just the not-hidden dirs
    flines = list()
    for dirpath, dirnames, filenames in os.walk("."):
        globals()["dirpath"] = dirpath  # todo: does help
        dirnames[::] = list(_ for _ in dirnames if not _.startswith("."))
        if dirpath != ".":
            flines.append(dirpath.removeprefix("./"))
    olines = flines

    # find dots too  # the dirs and the files, but not the top ".." nor top "."
    flines = list()
    for dirpath, dirnames, filenames in os.walk("."):
        globals()["dirpath"] = dirpath  # todo: does help
        dirfiles = list(os.path.join(dirpath, _) for _ in filenames)
        if dirpath != ".":
            flines.append(dirpath.removeprefix("./"))
        flines.extend(sorted(_.removeprefix("./") for _ in dirfiles))
    olines = flines

    # frame  # framed
    olines = list()
    olines.extend(2 * [""])  # top margin
    for iline in ilines:
        oline = (4 * " ") + iline  # left margin
        olines.append(oline)
    olines.extend(2 * [""])  # bottom margin
    otext = "\n".join(olines) + "\n"

    # head head  # h h h h h h h h h
    olines = ilines[:10]  # could be (Terminal Lines // 3)

    # head tail  # h t  # h t  # h t  # h t  # h t  # h t  # h t  # h t  # ht ht
    ipairs = list(enumerate(ilines, start=1))
    plines = list(f"{_[0]:6}  {_[-1]}" for _ in ipairs[:3])
    plines.append("...")
    plines.extend(f"{_[0]:6}  {_[-1]}" for _ in ipairs[-3:])
    olines = plines

    # join  # joined  # |tr '\n' ' '  # |xargs  # xargs xargs  # x x
    otext = " ".join(ilines) + "\n"

    # ls dots
    olines = sorted(os.listdir())  # still no [os.curdir, os.pardir]

    # ls ls
    olines = sorted(_ for _ in os.listdir() if not _.startswith("."))

    # md5sum
    md5 = hashlib.md5()
    md5.update(ibytes)
    otext = md5.hexdigest() + "\n"

    # nl v0  # |nl -v0 |expand  # enum 0  # enum  # enumerate
    olines = list(f"{n:6d}  {i}" for (n, i) in enumerate(ilines))

    # sha256
    sha256 = hashlib.sha256()
    sha256.update(ibytes)
    otext = sha256.hexdigest() + "\n"

    # split split split  # |sed 's,  *,$,g' |tr '$' '\n'
    # |xargs -n 1  # xargs n 1  # xn1
    olines = itext.split()

    # tail tail  # t t t t t t t t t t t t t t t t t t
    olines = ilines[-10:]  # could be (Terminal Lines // 3)

    # ts  # |ts
    while True:
        readline = stdin.readline()
        if not readline:
            break
        iline = readline.splitlines()[0]
        ts = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S.%f %z")
        print(f"{ts}  {iline}", file=stdout)
        stdout.flush()

    # |tee >(pbcopy) |sponge
    olines = ilines  # todo: also Sponge Ended Bytes? not only Ended Chars?
    input_ = "\n".join(ilines) + "\n"
    subprocess.run(["pbcopy"], input=input_, text=True, check=True)

"""


# The Whole Input File chooses which Python Graf:  the 1st that raises no Exception

ITEXT_PY_GRAFS_TEXT = """

    # crthin
    assert re.match(r"http.*codereviews[./]", string=iline)
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

    # glink
    assert re.match(r"http.*[.]google.com/", string=iline)
    assert ("/edit" in iline) or ("/view" in iline)
    isplits = urllib.parse.urlsplit(iline)
    #
    opath = isplits.path
    opath = opath.removesuffix("/edit")
    opath = opath.removesuffix("/view")
    #
    osplits = urllib.parse.SplitResult(
        scheme=isplits.scheme,
        netloc=isplits.netloc,
        path=opath,
        query="",
        fragment="",
    )
    #
    oline = osplits.geturl()

    # jkthin
    assert re.match(r"^http.*jenkins[0-9]*[.]", string=iline)
    #
    iosplits = urllib.parse.urlsplit(iline)
    iosplits = iosplits._replace(scheme="http")
    iosplits = iosplits._replace(path=iosplits.path.rstrip("/") + "/")
    #
    netloc = iosplits.netloc.split(".")[0]
    netloc = string.capwords(netloc).replace("jenkins", "Jenkins")
    iosplits = iosplits._replace(netloc=netloc)
    #
    oline = iosplits.geturl()

    # jkwide
    assert re.search(r"[jJ]enkins[0-9]*/", string=iline)
    #
    fqdn = socket.getfqdn()
    dn = fqdn.partition(".")[-1]  # 'Domain Name of HostName'
    dn = dn or "example.com"
    #
    iosplits = urllib.parse.urlsplit(iline)
    iosplits = iosplits._replace(scheme="https")
    iosplits = iosplits._replace(path=iosplits.path.rstrip("/"))
    iosplits = iosplits._replace(netloc=f"{iosplits.netloc.casefold()}.dev.{dn}")
    #
    oline = iosplits.geturl()

    # jkey
    assert re.match(r"^http.*jira.*/browse/.*$", string=iline)
    isplits = urllib.parse.urlsplit(iline)
    oline = isplits.path.removeprefix("/browse/")

    # jlink
    assert re.match(r"^[A-Z]+[-][0-9]+$", string=iline)
    #
    fqdn = socket.getfqdn()
    dn = fqdn.partition(".")[-1]  # 'Domain Name of HostName'
    dn = dn or "example.com"
    #
    isplits = urllib.parse.urlsplit(iline)
    osplits = urllib.parse.SplitResult(
        scheme="https",
        netloc=f"jira.{dn}",
        path=f"/browse/{iline}",
        query="",
        fragment="",
    )
    oline = osplits.geturl()

    # wviewpage
    iosplits = urllib.parse.urlsplit(iline)
    assert iosplits.path == "/pages/viewpreviousversions.action"
    iosplits = iosplits._replace(path="/pages/viewpage.action")
    oline = iosplits.geturl()

    # chillx
    assert iline.startswith("http")  # "https", "http", etc
    assert " " not in iline
    ioline = iline
    ioline = ioline.replace("/x.com/", "/twitter.com/")
    count_eq_3 = 3
    ioline = ioline.replace("/", " /", count_eq_3)
    ioline = ioline.replace(".", " . ").rstrip()
    count_eq_1 = 1
    ioline = ioline.replace(": / /", " :// ", count_eq_1).rstrip()
    oline = ioline

    # warm
    assert iline.startswith("http")  # "https", "http", etc
    assert " " in iline
    oline = iline.replace(" ", "")

"""

#
# crthin to:  http://codereviews/r/123456/diff
# crthin from:  https://codereviews.example.com/r/123456/diff/8/#index_header
#
# glink to:  https://docs.google.com/document/d/$HASH
# glink from:  https://docs.google.com/document/d/$HASH/edit?usp=sharing
# glink from:  https://docs.google.com/document/d/$HASH/edit#gid=0'
#
# jkthin to:  http://123Jenkins
# jkwide to:  https://123jenkins.dev.example.com
#
# jkey to:  PROJ-12345
# jlink to:  https://jira.example.com/browse/PROJ-12345
#
# wviewpage to: https://wiki.example.com/pages/viewpage.action?pageId=12345
# wviewpage from: https://wiki.example.com/pages/viewpreviousversions.action?pageId=12345
#
# chillx to:  https :// twitter . com /pelavarre/status/1647691634329686016
# warm to:  https://twitter.com/pelavarre/status/1647691634329686016
#


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: Translate MakeTrans a la Sh |tr '...' '...'
#   |pq 'oline = iline.translate(str.maketrans("HW", "hw"))' |cat -

# todo: Translate MakeTrans a la Sh |tr -d '...'
#   |pq 'oline = iline.translate(str.maketrans("", "", ", !"))' |cat -


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
