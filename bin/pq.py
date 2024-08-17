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
  close, dedent, dent, end, reverse, shuffle, sort, spong, undent,
  deframe, dumps, frame, json, join, loads, split,
  expand, md5sum, sha256, tail -r, tac, unexpand,
  a, em, jq ., s, u, wc c, wc m, wc w, wc l,  wc c, wc m, wc w, wc l, vi, x, xn1
  len bytes, len text, len words, len lines, text set,
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
  pq  # end every Line of the Os/Copy Paste Clipboard Buffer
  pq |cat -  # show the Os/Copy Paste Clipboard Buffer
  cat - |pq  # type into the Os/Copy Paste Clipboard Buffer
  pq dent  # insert 4 Spaces at the left of each Line
  pq dedent  # remove the leading Blank Columns from the Lines
  pq len lines  # count Lines
  pq --py len lines  # show how to count Lines
  echo '[0, 11, 22]' |pq json |cat -  # format Json consistently
  pq 'oline = "<< " + iline + " >>"'  # add Prefix and Suffix to each Line
  pq 'olines = ilines[:3] + ["..."] + ilines[-3:]'  # show Head and Tail
  pq vi  # edit the Os/Copy Paste Clipboard Buffer, in the way of Vi or Emacs
"""

# quirks to come when we add 'pq vi':
#   respects color and ignores case
#   doesn't clear screen at launch, nor at quit either

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import bdb
import collections
import dataclasses
import datetime as dt
import difflib
import itertools
import os
import pathlib
import pdb
import re
import select
import shlex
import shutil
import stat
import sys
import termios  # unhappy at Windows
import textwrap
import traceback
import tty  # unhappy at Windows
import typing
import unicodedata

... == dict[str, int]  # new since Oct/2020 Python 3.9  # type: ignore


#
# Configure  # todo: less compile-time choices of modes
#


KDEBUG = False  # Debug 'os.read'


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

        self.pq_words = ns.words or list()
        self.py = ns.py or 0
        self.quiet = min(3, ns.quiet or 0)

        # Parse some Py Code and compose the rest,
        # and maybe sponge up 'self.ibytes_else', and maybe also 'self.itext_else'

        (found_py_graf, complete_py_graf) = self.find_and_form_py_lines()

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
            bindices = list(
                i for i, _ in enumerate(cgrafs_1) if _.startswith("ibytes = ")
            )
            tindices = list(
                i for i, _ in enumerate(cgrafs_1) if _.startswith("itext = ")
            )
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
        exec(py_text, globals(), alt_locals)  # because "i'm feeling lucky"

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
        list_assert_eq(mgrafs0, b=sorted(mgrafs0))  # CUED_PY_GRAFS_TEXT sorted

        mgrafs1 = text_to_grafs(ITEXT_PY_GRAFS_TEXT)  # ordered, not sorted

        mgrafs = mgrafs0 + mgrafs1

        return mgrafs

    def fetch_cued_sgrafs(self) -> list[list[str]]:
        """Fetch the Cued Single-Line Paragraphs"""

        sgrafs = text_to_grafs(CUED_PY_LINES_TEXT)
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
            assert not opushes, (ipulls, opushes)
        elif ipulls == ["print"]:  # pq reverse  # pq sort
            assert not opushes, (ipulls, opushes)
        elif ipulls == ["print", "stdin", "stdout"]:  # pq ts
            assert not opushes, (ipulls, opushes)

        elif (not ipulls) and (opushes == ["olines"]):  # pq ls
            pass
        elif (not ipulls) and (opushes == ["oobject"]):  # pq pi
            pass

        else:
            assert len(ipulls) == 1, (ipulls, opushes)
            assert len(opushes) == 1, (ipulls, opushes)

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

                    if cues not in cues_list:
                        cues_list.append(cues)

                for cues in cues_list:
                    assert cues not in py_graf_by_cues.keys(), (cues,)
                    py_graf_by_cues[cues] = tuple(py_graf)

        return py_graf_by_cues

    #
    # Parse some Py Code and compose the rest       # todo: resolve the noqa C901
    #

    def find_and_form_py_lines(self) -> tuple[list[str], list[str]]:  # noqa C901
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

            # falls back to ending each Text Line, else ending each Byte Line

        if not py_graf:
            if pq_words == ["-"]:  # 'pq -' means 'pbpaste |pbcopy'
                py_graf = ["obytes = ibytes"]

        # Search for one Py Graf matching the Cues (but reject many if found)

        if not py_graf:
            py_graf = self.cues_to_one_py_graf_if(cues=pq_words)  # often exits nonzero

        # Take Cues as fragments of Python, if no match found

        if not py_graf:
            if any((" " in _) for _ in pq_words):
                py_graf = list(pq_words)  # better copied than aliased
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

        complete_py_graf = self.py_graf_complete(
            py_graf, ipulls=ipulls, opushes=opushes
        )

        # Succeed

        return (found_py_graf, complete_py_graf)

        # may sponge up 'self.ibytes_else', and maybe also 'self.itext_else'

    def py_graf_complete(self, py_graf, ipulls, opushes) -> list[str]:
        """Compose the rest of the Py Code"""

        dent = 4 * " "

        # Compose more Py Code to run before and after

        before_py_graf = self.form_before_py_graf(
            py_graf, ipulls=ipulls, opushes=opushes
        )

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
        if len(full_py_graf) > 3:
            full_py_graf = before_py_graf + div + run_py_graf + div + after_py_graf
            full_py_graf = graf_deframe(full_py_graf)

        fuller_py_graf = py_graf_insert_imports(py_graf=full_py_graf)

        # Succeed

        return fuller_py_graf

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

        py_graf = list()

        if "oline" in opushes:
            py_graf.append(dent + "olines.append(oline)")

        py_words = "olines oline".split()
        if any((_ in opushes) for _ in py_words):
            py_graf.append(r'otext = "\n".join(olines) + "\n"')

        if "oobject" in opushes:
            py_graf.append(r'otext = str(oobject) + "\n"')

        if "iolines" in ipulls:
            py_graf.append(r'otext = "\n".join(iolines) + "\n"')
            py_graf.extend(self.form_write_text_py_graf())

        if "stdout" in ipulls:
            if stdout_isatty:
                py_graf.append("otext = stdout.getvalue()")
                py_graf.extend(self.form_write_text_py_graf())

        py_words = "otext olines oline oobject".split()
        if any((_ in opushes) for _ in py_words):
            py_graf.extend(self.form_write_text_py_graf())

        if "obytes" in opushes:
            py_graf.extend(self.form_write_bytes_py_graf())

        #

        return py_graf

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

        """

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

        """

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
        read_py_graf = py_graf_insert_imports(py_graf=core_py_graf)

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
            py_graf = py_graf_insert_imports(py_graf=raw_py_graf)
            py_text = "\n".join(py_graf)

            alt_locals = dict(ilines=ilines)
            try:
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
        size = os.get_terminal_size(fd)

    assert size.columns >= 20  # vs Mac Sh Terminal Columns >= 20
    assert size.lines >= 5  # vs Mac Sh Terminal Lines >= 5

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
    """Form a Py Repr of an Object, but as styled by PyPi·Black"""

    s = repr(obj)

    if (s.startswith("'") or s.startswith("b'")) and s.endswith("'"):
        if '"' not in s:
            s = s.replace("'", '"')

    return s


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
        _.group(0)
        for _ in re.finditer(r"[a-zA-Z][a-zA-Z0-9_]*|[-.+0-9Ee]|.", string=py_text)
    )

    return py_words

    # todo: split more by the Py Rules, or even totally exactly like Py Rules
    # except don't drop Comments


def py_graf_insert_imports(py_graf) -> list[str]:
    """Insert a paragraph of Py Imports up front"""

    #

    importables = list(sys.modules.keys())

    importables.append("dt")
    importables.append("json")
    importables.append("socket")
    importables.append("string")
    importables.append("subprocess")
    importables.append("urllib.parse")

    importables.append("pq")

    #

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

    py_modules.sort()

    fuller_py_graf = list(py_graf)
    if py_modules:
        fuller_py_graf = import_graf + div + py_graf

    return fuller_py_graf


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

    diffs = list(
        difflib.unified_diff(a=strs_a, b=strs_b, fromfile="a", tofile="b", lineterm="")
    )

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
# Amp up Import TermIOs, Tty
#


def ex_macros(ilines) -> list[str]:
    """Edit in the way of Emacs"""

    lt = LineTerminal()
    olines = lt.top_wrangle(ilines, kmap="Emacs")

    return olines


def visual_ex(ilines) -> list[str]:
    """Edit in the way of Ex Vi"""

    lt = LineTerminal()
    olines = lt.top_wrangle(ilines, kmap="Vi")

    return olines


ESC = b"\x1B"


@dataclasses.dataclass
class BytesLogger:
    """Log Bytes arriving over time, for a time-accurate replay or analysis later"""

    tag: str  # 'k'  # 's'
    exists: bool  # True if the Log File already existed
    pylogfile: typing.TextIO  # opened here  # '.pqinfo/keylog.py'
    logged: dt.datetime  # when 'def log_bytes_io' last ran

    def __init__(self, name, tag) -> None:
        """Write the Code before the Log"""

        assert tag in ("k", "s"), (tag,)  # todo: accept more tags?

        self.tag = tag

        dirpath = pathlib.Path(".pqinfo")
        dirpath.mkdir(parents=True, exist_ok=True)  # 'parents=' unneeded at './'

        path = dirpath / name  # '.pqinfo/screenlog.py'
        exists = path.exists()
        self.exists = exists

        # pylogfile = io.StringIO()
        # pylogfile.name = "<io.StringIO>"
        pylogfile = path.open("a")  # last wins

        self.pylogfile = pylogfile

        if not exists:
            self.write_prolog()

        self.logged = dt.datetime.now()

    def write_prolog(self) -> None:
        """Write the Code before the Log"""

        pylogfile = self.pylogfile
        tag = self.tag

        assert tag in ("k", "s"), (tag,)  # todo: accept more tags?

        k_py = f'''
            #!/usr/bin/env python3

            import time
            import typing

            if __name__ == "__main__":
                import keylog

                for kbytes in keylog.kbytes_walk():
                    print(repr(kbytes))


            def {tag}bytes_walk() -> typing.Generator[bytes, None, None]:
                """Yield Bytes slowly over Time, as a replay of this Log"""
        '''

        s_py = f'''
            #!/usr/bin/env python3

            import os
            import sys
            import time
            import typing

            if __name__ == "__main__":
                import screenlog

                fd = sys.stdout.fileno()
                for sbytes in screenlog.sbytes_walk():
                    os.write(fd, sbytes)


            def {tag}bytes_walk() -> typing.Generator[bytes, None, None]:
                """Yield Bytes slowly over Time, as a replay of this Log"""
        '''

        py = k_py if tag == "k" else s_py
        py = textwrap.dedent(py).strip()

        pylogfile.write(py + "\n" "\n")

        # todo: duck away from PyPi·Org Black 'E501 line too long (... > 999 characters'

    def log_bytes_io(self, sbytes) -> None:
        """Log some Keyboard Input Bytes, Screen Output Bytes, etc"""

        pylogfile = self.pylogfile
        logged = self.logged

        now = dt.datetime.now()
        total_seconds = (now - logged).total_seconds()
        self.logged = now

        rep = black_repr(sbytes)

        print(f"    time.sleep({total_seconds})", file=pylogfile)
        print(f"    yield {rep}", file=pylogfile)


#
# escape-sequences:
#
#   ⎋[d line-position-absolute  ⎋[G cursor-character-absolute
#   ⎋[1m bold, ⎋[3m italic, ⎋[4m underline, ⎋[m plain
#
#   ⎋[31m red  ⎋[32m green  ⎋[34m blue  ⎋[38;5;130m orange  ⎋[m plain
#   ⎋[4h insert  ⎋[6 q bar  ⎋[4l replace  ⎋[4 q skid  ⎋[ q unstyled
#   ⎋[M delete-line  ⎋[L insert-line  ⎋[P delete-char  ⎋[@ insert-char
#   ⎋[T scroll-up  ⎋[S scroll-down
#

Y_32100 = 32100  # larger than all Screen Row Heights tested
X_32100 = 32100  # larger than all Screen Column Widths tested

BS = "\b"  # 00/08 Backspace ⌃H
HT = "\t"  # 00/09 Character Tabulation ⌃I
LF = "\n"  # 00/10 Line Feed ⌃J
CR = "\r"  # 00/13 Carriage Return ⌃M

assert ESC == b"\x1B"

SS3 = b"\x1B" b"O"  # 04/15 Single Shift Three

CSI = b"\x1B" b"["  # 05/11 Control Sequence Introducer
CSI_I_P_BYTES = b"".join(bytes([_]) for _ in range(0x20, 0x40))

CUU_Y = "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
CUD_Y = "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down
CUF_X = "\x1B" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right
CUB_X = "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left
CHA = "\x1B" "[" "G"  # CSI 04/07 Cursor Character Absolute 1
CHA_Y = "\x1B" "[" "{}G"  # CSI 04/07 Cursor Character Absolute
CHT_X = "\x1B" "[" "{}I"  # CSI 04/09 Cursor Forward [Horizontal] Tabulation
CBT_X = "\x1B" "[" "{}Z"  # CSI 05/10 Cursor Backward Tabulation
VPA_Y = "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

SU_Y = "\x1B" "[" "{}S"  # CSI 05/03 Scroll Up   # Insert Bottom Lines
SD_Y = "\x1B" "[" "{}T"  # CSI 05/04 Scroll Down  # Insert Top Lines
# SL_X = "\x1B" "[" "{} @"  # CSI 02/00 04/00 Scroll Left  # no-op at macOS Terminal
# SR_X = "\x1B" "[" "{} A"  # CSI 02/00 04/01 Scroll Right  # no-op at macOS Terminal

ICH_X = "\x1B" "[" "{}@"  # CSI 04/00 Insert Character
IL_Y = "\x1B" "[" "{}L"  # CSI 04/12 Insert Line
DL_Y = "\x1B" "[" "{}M"  # CSI 04/13 Delete Line
DCH_X = "\x1B" "[" "{}P"  # CSI 05/00 Delete Character

# ESC 04/05 Next Line (NEL)
# CSI 04/05 Cursor Next Line (CNL)

RM_IRM = "\x1B" "[" "4l"  # CSI 06/12 4 Reset Mode Replace/ Insert
SM_IRM = "\x1B" "[" "4h"  # CSI 06/08 4 Set Mode Insert/ Replace

DECSCUSR = "\x1B" "[" " q"  # CSI 02/00 07/01  # '' No-Style Cursor
DECSCUSR_SKID = "\x1B" "[" "4 q"  # CSI 02/00 07/01  # 4 Skid Cursor
DECSCUSR_BAR = "\x1B" "[" "6 q"  # CSI 02/00 07/01  # 6 Bar Cursor

# quoted Str sorted by the CSI Final Byte:  A, B, C, D, G, Z, d, etc
# the 02/00 ' ' of the CSI ' q' is its only 'Intermediate Byte'


@dataclasses.dataclass
class BytesTerminal:
    """Read/ Write the Bytes at Keyboard/ Screen of a Terminal"""

    #
    # lots of docs:
    #
    #   https://unicode.org/charts/PDF/U0000.pdf
    #   https://unicode.org/charts/PDF/U0080.pdf
    #   https://en.wikipedia.org/wiki/ANSI_escape_code
    #   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
    #
    #   https://www.ecma-international.org/publications-and-standards/standards/ecma-48
    #     /wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf
    #
    #   termios.TCSADRAIN blocks till Queued Output gone, without dropping Queued Input
    #   termios.TCSAFLUSH blocks till Queued Output gone and drops Queued Input
    #

    stdio: typing.TextIO  # sys.stderr
    fd: int  # 2
    kholds: bytearray  # b"" till lookahead reads too fast

    before: int  # termios.TCSADRAIN  # termios.TCSAFLUSH
    tcgetattr_else: list[int | list[bytes | int]] | None
    kinterrupts: int
    after: int  # termios.TCSADRAIN  # termios.TCSAFLUSH

    kbyteslogger: BytesLogger  # logs Keyboard Bytes In
    sbyteslogger: BytesLogger  # logs Screen Bytes Out

    def __init__(self, before=termios.TCSADRAIN, after=termios.TCSADRAIN) -> None:

        stdio = sys.stderr
        fd = stdio.fileno()

        kbyteslogger = BytesLogger("keylog.py", tag="k")
        sbyteslogger = BytesLogger("screenlog.py", tag="s")

        self.stdio = stdio
        self.fd = fd
        self.kholds = bytearray()  # todo: write it sometimes

        self.before = before
        self.tcgetattr_else = None
        self.kinterrupts = 0
        self.after = after  # todo: test Tcsa Flush on large Paste crashing us

        self.kbyteslogger = kbyteslogger
        self.sbyteslogger = sbyteslogger

        # termios.TCSAFLUSH destroys Input, like for when Paste crashes Code

    def __enter__(self) -> "BytesTerminal":  # -> typing.Self:
        r"""Stop line-buffering Input, stop replacing \n Output with \r\n, etc"""

        fd = self.fd
        before = self.before
        tcgetattr_else = self.tcgetattr_else

        if tcgetattr_else is None:
            tcgetattr = termios.tcgetattr(fd)
            assert tcgetattr is not None

            self.tcgetattr_else = tcgetattr

            assert before in (termios.TCSADRAIN, termios.TCSAFLUSH), (before,)
            if False:  # jitter Sat 3/Aug  # ⌃C prints Py Traceback
                tty.setcbreak(fd, when=termios.TCSAFLUSH)  # ⌃C prints Py Traceback
            else:
                tty.setraw(fd, when=before)  # SetRaw defaults to TcsaFlush

        return self

    def __exit__(self, *exc_info) -> None:
        r"""Start line-buffering Input, start replacing \n Output with \r\n, etc"""

        fd = self.fd
        tcgetattr_else = self.tcgetattr_else
        after = self.after

        if tcgetattr_else is not None:

            # Revert Screen Settings to Defaults  # todo: when are our Defaults wrong?

            s0 = "\x1B" "[" "4l"  # CSI 06/12 4 Reset Mode Replace/ Insert
            s1 = "\x1B" "[" " q"  # CSI 02/00 07/01  # '' No-Style Cursor
            self.btwrite((s0 + s1).encode())

            assert RM_IRM == "\x1B" "[" "4l"  # CSI 06/12 Reset Mode Replace/ Insert
            assert DECSCUSR == "\x1B" "[" " q"  # CSI 02/00 07/01  # '' No-Style Cursor

            #

            tcgetattr = tcgetattr_else
            self.tcgetattr_else = None

            assert after in (termios.TCSADRAIN, termios.TCSAFLUSH), (after,)
            when = after
            termios.tcsetattr(fd, when, tcgetattr)

        return None

    def breakpoint(self) -> None:
        r"""Breakpoint with line-buffered Input and \n Output taken to mean \r\n, etc"""

        self.__exit__()
        breakpoint()  # to step up the call stack:  u
        self.__enter__()

        _ = """

        fd = self.fd
        tcgetattr_else = self.tcgetattr_else

        if tcgetattr_else is not None:
            tcgetattr = tcgetattr_else
            when = termios.TCSADRAIN
            termios.tcsetattr(fd, when, tcgetattr)
            stdio.flush()
            tty.setraw(fd, when)

        if False:  # jitter Sat 3/Aug
            os.write(fd, b"??")

        """

    def flush_enough(self) -> None:
        """Repair the damage that Breakpoint does to Entry"""

        stdio = self.stdio
        stdio.flush()

        self.kbyteslogger.pylogfile.flush()  # plus ~0.050 ms, ugh
        self.sbyteslogger.pylogfile.flush()  # plus another ~0.050 ms, ugh

        fd = self.fd
        when = termios.TCSADRAIN
        tty.setraw(fd, when)

    def btwrite(self, sbytes) -> None:
        """Write Bytes to the Screen, but without implicitly also writing a Line-End"""

        self.btprint(sbytes, end=b"")

    def btprint(self, *args, end=b"\r\n") -> None:
        """Write Bytes to the Screen as one or more Ended Lines"""

        fd = self.fd
        assert self.tcgetattr_else
        sbyteslogger = self.sbyteslogger

        sep = b" "
        join = sep.join(args)
        sbytes = join + end

        sbyteslogger.log_bytes_io(sbytes)  # logs Out before Write
        os.write(fd, sbytes)

        # doesn't raise UnicodeEncodeError

    def read_kchord_bytes_if(self) -> bytes:  # noqa C901 complex
        """Read the Bytes of a single Keyboard Chord from the Keyboard"""

        assert ESC == b"\x1B"
        assert CSI == b"\x1B" b"["
        assert SS3 == b"\x1B" b"O"
        assert CSI_I_P_BYTES == b"".join(bytes([_]) for _ in range(0x20, 0x40))

        # Block to fetch at least 1 Byte

        read_0 = self.read_kchar_bytes_if()  # often empties the .kholds
        kchord_bytes = read_0
        if read_0 == b"\x1B":

            # Accept 1 or more ESC Bytes, such as x 1B 1B in ⌥⌃FnDelete

            while True:  # without Timeout would rudely block at ⎋⎋ Meta Esc
                if not self.kbhit(timeout=0):
                    return kchord_bytes

                read_1 = self.read_kchar_bytes_if()
                kchord_bytes += read_1
                if read_1 != b"\x1B":
                    break

            if kchord_bytes == b"\x1B\x5B":  # ⎋[ Meta [
                if not self.kbhit(timeout=0):
                    return kchord_bytes

            # Block or don't, to fetch the rest of the Esc Sequence

            if read_1 == b"O":  # 01/11 04/15 SS3
                read_2 = self.read_kchar_bytes_if()
                kchord_bytes += read_2  # practically never in range(0x20, 0x40)

            elif read_1 == b"[":  # 01/11 05/11 CSI
                while True:
                    read_2 = self.read_kchar_bytes_if()
                    kchord_bytes += read_2

                    if len(read_2) == 1:
                        ord_2 = read_2[-1]
                        if 0x20 <= ord_2 < 0x40:  # !"#$%&'()*+,-./0123456789:;<=>?
                            continue

                    break

        if KDEBUG:
            self.btprint(str(kchord_bytes).encode(), end=b"\r\n")  # todo: logging

        return kchord_bytes

        # cut short by end-of-input, or by undecodable Bytes
        # doesn't raise UnicodeDecodeError

    def read_kchar_bytes_if(self) -> bytes:
        """Read the Bytes of 1 Unicode Char from the Keyboard, if not cut short"""

        def decodable(kbytes: bytes) -> bool:
            try:
                kbytes.decode()  # may raise UnicodeDecodeError
                return True
            except UnicodeDecodeError:
                return False

        kbytes = b""
        while True:  # blocks till KChar Bytes complete
            more = self.readkbyte()
            assert more, (more,)
            kbytes += more

            if not decodable(kbytes):  # todo: invent Unicode Ord > 0x110000
                suffixes = (b"\x80", b"\x80\x80", b"\x80\x80\x80")
                if any(decodable(kbytes + _) for _ in suffixes):
                    continue

            break

        return kbytes

        # cut short by end-of-input, or by undecodable Bytes
        # doesn't raise UnicodeDecodeError

    def readkbyte(self) -> bytes:
        """Read 1 Byte from the Keyboard"""

        fd = self.fd
        assert self.tcgetattr_else
        kbyteslogger = self.kbyteslogger

        # Read 1 Byte from Held Bytes

        kholds = self.kholds
        if kholds:
            kbytes = bytes(kholds[:1])
            kholds.pop()
            return kbytes

        # Else block to read 1 Byte from Keyboard

        self.flush_enough()

        kbytes = os.read(fd, 1)  # 1 or more Bytes, begun as 1 Byte
        kbyteslogger.log_bytes_io(kbytes)  # logs In after Read

        if kbytes != b"\x03":  # ⌃C
            self.kinterrupts = 0
        else:
            self.kinterrupts += 1
            if self.kinterrupts >= 3:
                if False:  # jitter Sat 3/Aug  # ⌃C prints Py Traceback
                    raise KeyboardInterrupt()

        return kbytes

        # ⌥Y often comes through as \ U+005C Reverse-Solidus aka Backslash

    def kbhit(self, timeout) -> list[int]:  # 'timeout' in seconds, None for forever
        """Block till next Input Byte, else till Timeout, else till forever"""

        stdio = self.stdio

        rlist: list[int] = [stdio.fileno()]
        wlist: list[int] = list()
        xlist: list[int] = list()

        (alt_rlist, _, _) = select.select(rlist, wlist, xlist, timeout)

        return alt_rlist


# Shifting Keys other than the Fn Key
# Meta hides inside macOS Terminal > Settings > Keyboard > Use Option as Meta Key

# 'Fn'
Meta = "\N{Broken Circle With Northwest Arrow}"  # ⎋
Control = "\N{Up Arrowhead}"  # ⌃
Option = "\N{Option Key}"  # ⌥
Shift = "\N{Upwards White Arrow}"  # ⇧
Command = "\N{Place of Interest Sign}"  # ⌘  # Super  # Windows


KCAP_SEP = " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc

KCHORD_STR_BY_KCHARS = {
    "\x00": "⌃Spacebar",  # ⌃@  # ⌃⇧2
    "\x09": "Tab",  # '\t' ⇥
    "\x0D": "Return",  # '\r' ⏎
    "\x1B": "⎋",  # Esc  # Meta  # includes ⎋Spacebar ⎋Tab ⎋Return ⎋Delete without ⌥
    "\x1B" "\x01": "⎋⇧Fn←",  # ⌥⇧Fn←   # coded with ⌃A
    "\x1B" "\x03": "⎋FnReturn",  # coded with ⌃C  # not ⌥FnReturn
    "\x1B" "\x04": "⎋⇧Fn→",  # ⌥⇧Fn→   # coded with ⌃D
    "\x1B" "\x0B": "⎋⇧Fn↑",  # ⌥⇧Fn↑   # coded with ⌃K
    "\x1B" "\x0C": "⎋⇧Fn↓",  # ⌥⇧Fn↓  # coded with ⌃L
    "\x1B" "\x10": "⎋⇧Fn",  # ⎋ Meta ⇧ Shift of of F1..F12  # not ⌥⇧Fn  # coded with ⌃P
    "\x1B" "\x1B": "⎋⎋",  # Meta Esc  # not ⌥⎋
    "\x1B" "\x1B" "[" "3;5~": "⎋⌃FnDelete",  # ⌥⌃FnDelete  # LS1R
    "\x1B" "\x1B" "[" "A": "⎋↑",  # CSI 04/01 Cursor Up (CUU)  # not ⌥↑
    "\x1B" "\x1B" "[" "B": "⎋↓",  # CSI 04/02 Cursor Down (CUD)  # not ⌥↓
    "\x1B" "\x1B" "[" "Z": "⎋⇧Tab",  # ⇤  # CSI 05/10 CBT  # not ⌥⇧Tab
    "\x1B" "\x28": "⎋FnDelete",  # not ⌥⎋FnDelete
    "\x1B" "OP": "F1",  # ESC 04/15 Single-Shift Three (SS3)  # SS3 ⇧P
    "\x1B" "OQ": "F2",  # SS3 ⇧Q
    "\x1B" "OR": "F3",  # SS3 ⇧R
    "\x1B" "OS": "F4",  # SS3 ⇧S
    "\x1B" "[" "15~": "F5",  # CSI 07/14 Locking-Shift One Right (LS1R)
    "\x1B" "[" "17~": "F6",  # ⌥F1  # ⎋F1  # LS1R
    "\x1B" "[" "18~": "F7",  # ⌥F2  # ⎋F2  # LS1R
    "\x1B" "[" "19~": "F8",  # ⌥F3  # ⎋F3  # LS1R
    "\x1B" "[" "1;2C": "⇧→",  # CSI 04/03 Cursor [Forward] Right (CUF_YX) Y=1 X=2
    "\x1B" "[" "1;2D": "⇧←",  # CSI 04/04 Cursor [Back] Left (CUB_YX) Y=1 X=2
    "\x1B" "[" "20~": "F9",  # ⌥F4  # ⎋F4  # LS1R
    "\x1B" "[" "21~": "F10",  # ⌥F5  # ⎋F5  # LS1R
    "\x1B" "[" "23~": "F11",  # ⌥F6  # ⎋F6  # LS1R  # macOS takes F11
    "\x1B" "[" "24~": "F12",  # ⌥F7  # ⎋F7  # LS1R
    "\x1B" "[" "25~": "⇧F5",  # ⌥F8  # ⎋F8  # LS1R
    "\x1B" "[" "26~": "⇧F6",  # ⌥F9  # ⎋F9  # LS1R
    "\x1B" "[" "28~": "⇧F7",  # ⌥F10  # ⎋F10  # LS1R
    "\x1B" "[" "29~": "⇧F8",  # ⌥F11  # ⎋F11  # LS1R
    "\x1B" "[" "31~": "⇧F9",  # ⌥F12  # ⎋F12  # LS1R
    "\x1B" "[" "32~": "⇧F10",  # LS1R
    "\x1B" "[" "33~": "⇧F11",  # LS1R
    "\x1B" "[" "34~": "⇧F12",  # LS1R
    "\x1B" "[" "3;2~": "⇧FnDelete",  # LS1R
    "\x1B" "[" "3;5~": "⌃FnDelete",  # LS1R
    "\x1B" "[" "3~": "FnDelete",  # LS1R
    "\x1B" "[" "5~": "⇧Fn↑",
    "\x1B" "[" "6~": "⇧Fn↓",
    "\x1B" "[" "A": "↑",  # CSI 04/01 Cursor Up (CUU)
    "\x1B" "[" "B": "↓",  # CSI 04/02 Cursor Down (CUD)
    "\x1B" "[" "C": "→",  # CSI 04/03 Cursor Right [Forward] (CUF)
    "\x1B" "[" "D": "←",  # CSI 04/04 Cursor [Back] Left (CUB)
    "\x1B" "[" "F": "⇧Fn→",  # CSI 04/06 Cursor Preceding Line (CPL)
    "\x1B" "[" "H": "⇧Fn←",  # CSI 04/08 Cursor Position (CUP)
    "\x1B" "[" "Z": "⇧Tab",  # ⇤  # CSI 05/10 Cursor Backward Tabulation (CBT)
    "\x1B" "b": "⎋←",  # ⌥← ⎋B  # ⎋←  # Emacs M-b Backword-Word
    "\x1B" "f": "⎋→",  # ⌥→ ⎋F  # ⎋→  # Emacs M-f Forward-Word
    "\x20": "Spacebar",  # ' ' ␠ ␣ ␢
    "\x7F": "Delete",  # ␡ ⌫ ⌦
    "\xA0": "⌥Spacebar",  # '\N{No-Break Space}'
}

# the ⌥⇧Fn Key Cap quotes only the Shifting Keys, drops the substantive final Key Cap,
# except that ⎋⇧Fn← ⎋⇧Fn→ ⎋⇧Fn↑ ⎋⇧Fn also exist

assert list(KCHORD_STR_BY_KCHARS.keys()) == sorted(KCHORD_STR_BY_KCHARS.keys())


OPTION_KCHORD_STR_BY_1_KCHAR = {
    "á": "⌥EA",  # E
    "é": "⌥EE",
    "í": "⌥EI",  # without the "j́" here (because Combining Accent comes after)
    "ó": "⌥EO",
    "ú": "⌥EU",
    "´": "⌥ESpacebar",
    "é": "⌥EE",
    "â": "⌥IA",  # I
    "ê": "⌥IE",
    "î": "⌥II",
    "ô": "⌥IO",
    "û": "⌥IU",
    "ˆ": "⌥ISpacebar",
    "ã": "⌥NA",  # N
    "ñ": "⌥NN",
    "õ": "⌥NO",
    "˜": "⌥NSpacebar",
    "ä": "⌥UA",  # U
    "ë": "⌥UE",
    "ï": "⌥UI",
    "ö": "⌥UO",
    "ü": "⌥UU",
    "ÿ": "⌥UY",
    "¨": "⌥USpacebar",
    "à": "⌥`A",  # `
    "è": "⌥`E",
    "ì": "⌥`I",
    "ò": "⌥`O",
    "ù": "⌥`U",
    "`": "⌥`Spacebar",  # comes out as ⌥~
}

# hand-sorted by ⌥E ⌥I ⌥N ⌥U ⌥` order


#
# the Mac US English Terminal Keyboard choice of Option + Printable-US-Ascii
#

#
#  !"#$%&'()*+,-./0123456789:;<=>?
# @ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_
# `abcdefghijklmnopqrstuvwxyz{|}~
#

OPTION_KTEXT = """
     ⁄Æ‹›ﬁ‡æ·‚°±≤–≥÷º¡™£¢∞§¶•ªÚ…¯≠˘¿
    €ÅıÇÎ Ï˝Ó Ô\uF8FFÒÂ Ø∏Œ‰Íˇ ◊„˛Á¸“«‘ﬂ—
     å∫ç∂ ƒ©˙ ∆˚¬µ øπœ®ß† √∑≈¥Ω”»’
"""

# ⌥⇧K is Apple Icon  is \uF8FF is in the U+E000..U+F8FF Private Use Area (PUA)

OPTION_KCHARS = " " + textwrap.dedent(OPTION_KTEXT).strip() + " "
OPTION_KCHARS = OPTION_KCHARS.replace("\n", "")

assert len(OPTION_KCHARS) == (0x7E - 0x20) + 1

OPTION_KCHARS_SPACELESS = OPTION_KCHARS.replace(" ", "")


_KCHARS_LISTS = [
    list(KCHORD_STR_BY_KCHARS.keys()),
    list(OPTION_KCHORD_STR_BY_1_KCHAR.keys()),
    list(OPTION_KCHARS_SPACELESS),
]

_KCHARS_LIST = list(_KCHARS for _KL in _KCHARS_LISTS for _KCHARS in _KL)
for _KCHARS, _COUNT in collections.Counter(_KCHARS_LIST).items():
    assert _COUNT == 1, (_COUNT, _KCHARS)


@dataclasses.dataclass
class StrTerminal:
    """Read/ Write Str Characters at Keyboard/ Screen of a Terminal"""

    bt: BytesTerminal  # wrapped here
    kpushes: list[tuple[bytes, str]]  # cached here

    def __init__(self) -> None:
        self.bt = BytesTerminal()
        self.kpushes = list()

    def __enter__(self) -> "StrTerminal":  # -> typing.Self:
        r"""Stop line-buffering Input, stop replacing \n Output with \r\n, etc"""

        bt = self.bt
        bt.__enter__()

        return self

    def __exit__(self, *exc_info) -> None:
        r"""Start line-buffering Input, start replacing \n Output with \r\n, etc"""

        bt = self.bt
        bt.__exit__(*exc_info)

    def breakpoint(self) -> None:
        r"""Breakpoint with line-buffered Input and \n Output taken to mean \r\n, etc"""

        self.__exit__()
        breakpoint()  # to step up the call stack:  u
        self.__enter__()

    def stwrite(self, schars) -> None:
        """Write Chars to the Screen, but without implicitly also writing a Line-End"""

        self.stprint(schars, end="")

    def stprint(self, *args, end="\r\n") -> None:
        """Write Chars to the Screen as one or more Ended Lines"""

        bt = self.bt

        sep = " "
        join = sep.join(str(_) for _ in args)

        sbytes = join.encode()
        ebytes = end.encode()

        bt.btprint(sbytes, end=ebytes)

    def append_one_kchord_bytes_str(self, kbytes, kstr) -> None:
        """Say to read a Bytes/Str pair again, as if read too far ahead"""

        kpushes = self.kpushes

        kpush = (kbytes, kstr)
        kpushes.append(kpush)

    def pull_one_kchord_bytes_str(self) -> tuple[bytes, str]:
        """Let the caller read again what they read ahead"""

        kpushes = self.kpushes

        if kpushes:
            kpush = kpushes.pop(0)
            return kpush

        kpush = self.read_one_kchord_bytes_str()

        assert kpush[0], (kpush,)  # 1 or more Bytes always
        assert kpush[-1], (kpush,)  # 1 or more Chars always

        return kpush

    def read_one_kchord_bytes_str(self) -> tuple[bytes, str]:
        """Read 1 Keyboard Chord from the Keyboard, as Bytes and Str"""

        bt = self.bt

        kchord_str_by_kchars = KCHORD_STR_BY_KCHARS  # '\e\e[A' for ⎋↑

        # Read the Bytes of 1 Keyboard Chord

        kchord_bytes = bt.read_kchord_bytes_if()  # may contain b' '
        kchars = kchord_bytes.decode()  # may raise UnicodeDecodeError

        # Choose 1 Key Cap to speak of the Bytes of 1 Keyboard Chord

        if kchars in kchord_str_by_kchars.keys():
            kchord_str = kchord_str_by_kchars[kchars]
        else:
            kchord_str = ""
            for kch in kchars:  # often 'len(kchars) == 1'
                s = self.kch_to_kcap(kch)
                kchord_str += s

                # ⌥Y often comes through as \ U+005C Reverse-Solidus aka Backslash

        # Succeed

        assert KCAP_SEP == " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc
        assert " " not in kchord_str, (kchord_str,)

        if KDEBUG:
            self.stprint(kchord_bytes, kchord_str)

        return (kchord_bytes, kchord_str)

        # '⌃L'  # '⇧Z'
        # '⎋A' from ⌥A while macOS Keyboard > Option as Meta Key

    def kch_to_kcap(self, ch) -> str:  # noqa C901
        """Choose a Key Cap to speak of 1 Keyboard Char"""

        o = ord(ch)

        option_kchars = OPTION_KCHARS  # '∂' for ⌥D
        option_kchars_spaceless = OPTION_KCHARS_SPACELESS  # '∂' for ⌥D
        option_kchord_str_by_1_kchar = OPTION_KCHORD_STR_BY_1_KCHAR  # 'é' for ⌥EE
        kchord_str_by_kchars = KCHORD_STR_BY_KCHARS  # '\x7F' for 'Delete'

        # Show more Key Caps than US-Ascii mentions

        if ch in kchord_str_by_kchars.keys():  # Mac US Key Caps for Spacebar, F12, etc
            s = kchord_str_by_kchars[ch]

        elif ch in option_kchord_str_by_1_kchar.keys():  # Mac US Option Accents
            s = option_kchord_str_by_1_kchar[ch]

        elif ch in option_kchars_spaceless:  # Mac US Option Key Caps
            index = option_kchars.index(ch)
            asc = chr(0x20 + index)
            if "A" <= asc <= "Z":
                asc = "⇧" + asc  # '⇧A'
            if "a" <= asc <= "z":
                asc = chr(ord(asc) ^ 0x20)  # 'A'
            s = "⌥" + asc

        # Show the Key Caps of US-Ascii, plus the ⌃ ⇧ Control/ Shift Key Caps

        elif (o < 0x20) or (o == 0x7F):  # C0 Control Bytes, or \x7F Delete (DEL)
            s = "⌃" + chr(o ^ 0x40)  # '⌃@'
        elif "A" <= ch <= "Z":  # printable Upper Case English
            s = "⇧" + chr(o)  # '⇧A'
        elif "a" <= ch <= "z":  # printable Lower Case English
            s = chr(o ^ 0x20)  # 'A'

        # Test that no Keyboard sends the C1 Control Bytes, nor the Quasi-C1 Bytes

        elif o in range(0x80, 0xA0):  # C1 Control Bytes
            assert False, (o, ch)
        elif o == 0xA0:  # 'No-Break Space'
            s = "⌥Spacebar"
            assert False, (o, ch)  # unreached because 'kchord_str_by_kchars'
        elif o == 0xAD:  # 'Soft Hyphen'
            assert False, (o, ch)

        # Show the US-Ascii or Unicode Char as if its own Key Cap

        else:
            assert o < 0x11_0000, (o, ch)
            s = chr(o)  # '!', '¡', etc

        # Succeed, but insist that Blank Space is never a Key Cap

        assert s.isprintable(), (s, o, ch)  # has no \x00..\x1F, \x7F, \xA0, \xAD, etc
        assert " " not in s, (s, o, ch)

        return s

        # '⌃L'  # '⇧Z'


PY_CALL = (
    tuple[typing.Callable]
    | tuple[typing.Callable, tuple]
    | tuple[typing.Callable, tuple, dict]
)


@dataclasses.dataclass
class LineTerminal:
    """React to Sequences of Key Chords by laying Chars of Lines over the Screen"""

    st: StrTerminal  # wrapped here
    logfile: typing.TextIO  # opened here  # '.pqinfo/funclog.log'  # logfmt
    logfile_exists: bool  # created by earlier processes

    olines: list[str]  # the Lines to sketch

    kbytes: bytes  # the Bytes of the last Keyboard Chord
    kcap_str: str  # the Str of the KeyCap Words of the last Keyboard Chord
    kstr_starts: list[str]  # []  # ['⌃U']  # ['⌃U', '-']  # ['⌃U', '⌃U']
    kstr_stops: list[str]  # []  # ['⎋'] for any of ⌃C ⌃D ⌃G ⎋ ⌃\

    kmap: str  # ''  # 'Emacs'  # 'Vi'
    vmodes: list[str]  # ''  # 'Replace'  # 'Insert'

    def __init__(self) -> None:

        dirpath = pathlib.Path(".pqinfo")
        dirpath.mkdir(parents=True, exist_ok=True)  # 'parents=' unneeded at './'

        path = dirpath / "pq.log"  # '.pqinfo/pq.log'
        self.logfile_exists = path.exists()

        # logfile = io.StringIO()
        # logfile.name = "<io.StringIO>"
        logfile = path.open("a")  # last wins

        self.logfile = logfile

        self.st = StrTerminal()
        self.logfile = logfile

        self.olines = list()

        self.kstr_starts = list()
        self.kstr_stops = list()
        self.kbytes = b""
        self.kcap_str = ""

        self.kmap = ""
        self.vmodes = [""]

        # lots of empty happens only until first Keyboard Input

    def breakpoint(self) -> None:
        r"""Breakpoint with line-buffered Input and \n Output taken to mean \r\n, etc"""

        st = self.st

        if False:  # jitter Fri 16/Aug
            breakpoint()  # why does this kind of work, but just in the first Break?
            return

        st.__exit__()
        breakpoint()  # to step up the call stack:  u
        st.__enter__()

    def top_wrangle(self, ilines, kmap) -> list[str]:
        """Launch, and run till SystemExit"""

        olines = self.olines
        olines.extend(ilines)

        self.kmap = kmap

        # Wrap around a StrTerminal wrapped around a ByteTerminal

        klog_exists = self.st.bt.kbyteslogger.exists
        slog_exists = self.st.bt.sbyteslogger.exists
        tlog_exists = self.logfile_exists

        with StrTerminal() as st:
            self.st = st

            # Tell the StrTerminal what to say at first

            olines = self.olines
            for oline in olines:
                st.stprint(oline)

            bt = st.bt
            if (not klog_exists) or (not slog_exists) or (not tlog_exists):
                st.stprint()
                if not klog_exists:
                    st.stprint(
                        "Logging Keyboard Chord Bytes into:  tail -F -n +15",
                        bt.kbyteslogger.pylogfile.name,
                    )
                if not slog_exists:
                    st.stprint(
                        "Logging Screen Bytes into:  tail -F -n +15",
                        bt.sbyteslogger.pylogfile.name,
                    )
                if not tlog_exists:
                    st.stprint(
                        "Logging LogFmt Lines into:  tail -F",
                        self.logfile.name,
                    )

            self.help_quit()  # for .top_wrangle

            try:
                self.texts_vmode_wrangle("Replace")  # as if Vi +:startreplace
                self.verbs_wrangle()  # as if Vi +:stopinsert, not Vi +:startinsert
            except SystemExit as exc:
                if exc.code:
                    raise

            olines.clear()

            return olines

    def verbs_wrangle(self) -> list[str]:
        """Read & Eval & Print in a loop till SystemExit"""

        vmode = self.vmodes[-1]
        assert not vmode, (vmode,)

        while True:
            self.screen_print()
            self.verb_read(vmode="")  # for .verbs_wrangle
            self.verb_eval(vmode="")  # for .verbs_wrangle

    def texts_vmode_wrangle(self, vmode) -> None:
        """Enter Replace/ Insert V-Mode, Wrangle Texts, then exit V-Mode"""

        assert vmode, (vmode,)

        self.vmode_enter(vmode)
        self.texts_wrangle()
        self.vmode_exit()

    def texts_wrangle(self) -> None:  # noqa C901 too complex(11
        """Take Input as Replace Text or Insert Text, till ⌃C or ⎋"""

        kstr_starts = self.kstr_starts
        kstr_stops = self.kstr_stops

        vmode = self.vmodes[-1]
        assert vmode, (vmode,)

        while True:
            self.screen_print()

            # Read one textual/not Keyboard Chord Sequence from the Keyboard
            # may raise UnicodeDecodeError

            (kbytes, kchars, kcap_str) = self.verb_read_for_vmode(vmode)

            textual = self.kchars_are_textual(
                kchars, kcap_str=kcap_str, kstr_starts=kstr_starts
            )

            # Bind Delete and Return differently while Insert

            if vmode == "Insert":
                if kcap_str == "Delete":
                    self.kdo_char_delete_left()
                    continue
                if kcap_str == "Return":
                    self.kdo_insert_return()
                    continue

                # Vim deletes ⌃U Lines and ⌃W Words while Insert
                # Vim leaps over ⌃U Lines and ⌃W Words while Replace

                # Vim does Replace Delete over what's not too old

            # Exit Replace/ Insert Mode on request

            kstr_stops.clear()

            assert STOP_KCAP_STRS == ("⌃C", "⌃D", "⌃G", "⎋", "⌃\\")
            if not textual:
                if kcap_str in ("⌃C", "⌃D", "⌃G", "⎋", "⌃\\"):
                    # self.breakpoint()
                    kstr_stops.append(kcap_str)  # like for ⎋[1m
                    break

            # Take unprintable K Chars as Verbs,
            # and sometimes take - 0 1 2 3 4 5 6 7 8 9 as more K Start's

            if not textual:
                self.verb_eval(vmode="")  # for .texts_wrangle untextuals
                continue

            # Take the KCap_Str as Text Input

            assert textual, (textual,)

            self.kdo_text_write_n()  # for .texts_wrangle textuals

    def kchars_are_textual(self, kchars, kcap_str, kstr_starts) -> bool:
        """Say to take the K Chars as Text, else not"""

        kstarts_sorted_set = sorted(set(kstr_starts))
        kstarts_closed = kstr_starts[1:][-1:] == ["⌃U"]

        # Take the Unprintable K Chars as Verbs, not as Text

        textual = kchars.isprintable()
        if kstr_starts and not kstarts_closed:
            textual = False

        # Take Key Cap Sequences opened by K Starts as Verbs, not as Text
        # Take the K Starts themselves as Verbs, not as Text, if started already

        if kcap_str == "⌃U":
            assert not textual, (textual, kchars)

        if kcap_str == "-":
            if kstarts_sorted_set in (["-"], ["-", "⌃U"], ["⌃U"]):  # not []
                assert not textual, (textual, kchars)

        if kcap_str in list("0123456789"):
            if kstr_starts and not kstarts_closed:
                assert not textual, (textual, kchars)

        if not textual:
            return False

        # Take the K Caps that call for Quoting Input as Verbs, not as Text

        if kcap_str in ["⌥[", "⎋["]:
            return False

        # Else take the K Chars as Text (as the K Chars themselves, not as the K Caps)

        return True

    def vmode_enter(self, vmode) -> None:
        """Take Input as Replace Text or Insert Text, till Exit"""

        vmodes = self.vmodes

        assert vmode in ("", "Insert", "Replace"), vmode
        vmodes.append(vmode)

        self.vmode_stwrite(vmode)

    def vmode_stwrite(self, vmode) -> None:  # for .vmode_exit or .vmode_enter
        """Redefine StrTerminal Write as Replace or Insert, & choose a Cursor Style"""

        st = self.st

        assert vmode in ("", "Insert", "Replace"), vmode
        print(f"{vmode=}", file=self.logfile)

        if not vmode:
            st.stwrite("\x1B" "[" "4l")  # CSI 06/12 Replace
            st.stwrite("\x1B" "[" " q")  # CSI 02/00 07/01  # No-Style Cursor
        elif vmode in "Insert":
            st.stwrite("\x1B" "[" "4h")  # CSI 06/08 4 Set Mode Insert/ Replace
            st.stwrite("\x1B" "[" "6 q")  # CSI 02/00 07/01  # 6 Bar Cursor
        else:
            assert vmode == "Replace", (vmode,)
            st.stwrite("\x1B" "[" "4l")  # CSI 06/12 Replace
            st.stwrite("\x1B" "[" "4 q")  # CSI 02/00 07/01  # 4 Skid Cursor

        assert RM_IRM == "\x1B" "[" "4l"  # CSI 06/12 Reset Mode Replace/ Insert
        assert SM_IRM == "\x1B" "[" "4h"  # CSI 06/08 Set Mode Insert/ Replace

        assert DECSCUSR == "\x1B" "[" " q"  # CSI 02/00 07/01  # '' No-Style Cursor
        assert DECSCUSR_SKID == "\x1B" "[" "4 q"  # CSI 02/00 07/01  # 4 Skid Cursor
        assert DECSCUSR_BAR == "\x1B" "[" "6 q"  # CSI 02/00 07/01  # 6 Bar Cursor

    def vmode_exit(self) -> None:
        """Undo 'def vmode_enter'"""

        vmodes = self.vmodes

        vmodes.pop()
        vmode = vmodes[-1]

        self.vmode_stwrite(vmode)

    def screen_print(self) -> None:
        """Speak after taking Keyboard Chord Sequences as Commands or Text"""

        pass  # todo: do more inside 'def screen_print'

    def verb_read_for_vmode(self, vmode) -> tuple[bytes, str, str]:
        """Read one textual/not Keyboard Chord Sequence from the Keyboard"""

        kstr_starts = self.kstr_starts

        # Read the Head of the Sequence

        if kstr_starts:
            self.verb_read(vmode="")  # for .texts_wrangle while .kstr_starts
        else:
            self.verb_read(vmode=vmode)  # for .texts_wrangle Replace/ Insert

        kbytes = self.kbytes
        kchars = kbytes.decode()  # may raise UnicodeDecodeError
        kcap_str = self.kcap_str

        # Read the Tail of the Sequence when the Head isn't printable

        if not kchars.isprintable():
            self.verb_tail_read(kbytes, kcap_str=kcap_str)

            kbytes = self.kbytes
            kchars = kbytes.decode()  # may raise UnicodeDecodeError
            kcap_str = self.kcap_str

        print(f"{kcap_str=} {kbytes=} {vmode=}", file=self.logfile)

        return (kbytes, kchars, kcap_str)

        # often raises UnicodeDecodeError

    def verb_read(self, vmode) -> None:
        """Read one Keyboard Chord Sequence from the Keyboard, as Bytes, Str, & Str"""

        st = self.st

        # Read the first Keyboard Chord of the Sequence

        self.logfile.flush()
        (kchord_bytes, kchord_str) = st.pull_one_kchord_bytes_str()

        # Take just 1 Chord as a complete Sequence, when taking Chords as Chars

        if vmode:
            print(f"kcap_str={kchord_str!r} kbytes={kchord_bytes!r}", file=self.logfile)
            self.kbytes = kchord_bytes
            self.kcap_str = kchord_str
            return

        # Read zero or more Keyboard Chords to complete the Sequence of a Verb

        self.verb_tail_read(kbytes=kchord_bytes, kcap_str=kchord_str)

        # '⌃L'  # '⇧Z ⇧Z'

    def verb_tail_read(self, kbytes, kcap_str) -> None:
        """Read zero or more Keyboard Chords to complete the Sequence"""

        st = self.st

        assert KCAP_SEP == " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc
        ksep = " "

        b = b""
        s = ""
        eq_choice = (b, s)
        choices = list()

        kb = kbytes
        ks = kcap_str

        while True:
            b += kb
            s += (ksep + ks) if s else ks

            choice = (kb, ks)
            choices.append(choice)

            # Remember the last exact Find

            finds = self.kcap_str_findall(s)
            if s in finds:
                eq_choice = (b, s)

                # Succeed when one Func found

                if len(finds) == 1:
                    assert eq_choice[-1] == s, (eq_choice, s, finds)

                    last_choice = eq_choice
                    break

            # Quit after finding nothing
            # Fall back to last exact Find, else to first Choice

            if not finds:
                last_choice = eq_choice if eq_choice[-1] else choices[0]

                index = choices.index(last_choice)
                for choice in choices[(index + 1) :]:
                    (kb, ks) = choice
                    st.append_one_kchord_bytes_str(kb, kstr=ks)

                break

            self.logfile.flush()
            (kb, ks) = st.pull_one_kchord_bytes_str()

        # Succeed

        (kb, ks) = last_choice

        self.kbytes = kb
        self.kcap_str = ks

    def kcap_str_findall(self, kcap_str) -> list[str]:
        """List every matching LineTerminal Verb"""

        kdo_call_kcap_strs = KDO_CALL_KCAP_STRS

        assert (
            KCAP_SEP == " "
        )  # solves '⇧Tab' vs '⇧T a b'  # solves '⎋⇧FnX' vs '⎋⇧Fn X'
        ksep = " "

        #

        eq_finds = list(_ for _ in kdo_call_kcap_strs if _ == kcap_str)

        p = kcap_str + ksep
        startswith_finds = list(_ for _ in kdo_call_kcap_strs if _.startswith(p))

        #

        finds = eq_finds + startswith_finds

        return finds

    def verb_eval(self, vmode) -> None:
        """Take 1 Keyboard Chord Sequence as a Command to execute"""

        kstr_starts = self.kstr_starts
        kcap_str = self.kcap_str

        kdo_call_by_kcap_str = KDO_CALL_BY_KCAP_STR

        # Choose 1 Python Def to call, on behalf of 1 Keyboard Chord Sequence

        kdo_call: PY_CALL

        kdo_call = (LineTerminal.kdo_kcap_write_n,)  # for outside .kdo_call_by_kcap_str
        if (not vmode) or (not kcap_str.isprintable()):
            if kcap_str in kdo_call_by_kcap_str.keys():
                kdo_call = kdo_call_by_kcap_str[kcap_str]

        if KDEBUG:
            if kdo_call[0] is not LineTerminal.kdo_force_quit:
                kdo_call = (LineTerminal.kdo_kcap_write_n,)  # for KDEBUG

        kdo_func = kdo_call[0]
        assert kdo_func.__name__.startswith("kdo_"), (kdo_call, kcap_str)

        # Call the 1 Python Def

        kstr_starts_before = list(kstr_starts)

        done = False
        if len(kdo_call) == 1:  # takes the Inverse Func when no Args and no KwArgs
            done = self.kdo_inverse_or_nop(kdo_func)
        if not done:
            kint_else = self.kint_peek_else(default=None)
            print(f"kint={kint_else} func={kdo_func.__name__}", file=self.logfile)
            (kdo_func, args, kwargs) = self.py_call_complete(kdo_call)
            kdo_func(self, *args, **kwargs)

        # Forget the K Start's and/or K Stop's when we should

        self.kstarts_kstops_choose_after(kstr_starts_before, kcap_str=kcap_str)

    def py_call_complete(self, call) -> tuple[typing.Callable, tuple, dict]:
        """Complete the Python Call with Args and KwArgs"""

        func = call[0]

        args = ()

        kwargs: dict
        kwargs = dict()

        if len(call) == 1:
            return (func, args, kwargs)

        if len(call) == 2:
            return (func, call[-1], kwargs)

        assert len(call) == 3, (call,)
        return call

    def kstarts_kstops_choose_after(self, kstr_starts_before, kcap_str) -> None:
        """Forget the K Start's and/or add one K Stop's, like when we should"""

        kstr_starts = self.kstr_starts
        kstr_stops = self.kstr_stops

        # Forget the K Start's, unless this last Kdo_Func shrunk or grew or changed them

        if kstr_starts == kstr_starts_before:
            kstr_starts.clear()  # for .kstarts_kstops_forget_if

        # Forget the K Stop's, but then do hold onto the latest K Stop if present

        assert STOP_KCAP_STRS == ("⌃C", "⌃D", "⌃G", "⎋", "⌃\\")

        kstr_stops.clear()
        stopped = self.kcap_str in ("⌃C", "⌃D", "⌃G", "⎋", "⌃\\")
        if stopped:
            kstr_stops.append(self.kcap_str)

        if kcap_str in ("⌃C", "⌃D", "⌃G", "⎋", "⌃\\"):
            assert stopped, (stopped, kcap_str, self.kcap_str)

    def kdo_inverse_or_nop(self, kdo_func) -> bool:
        """Call the Inverse or do nothing, and return True, else return False"""

        # Call for more work when given an un-invertible Func

        kdo_inverse_func_by = VI_KDO_INVERSE_FUNC_DEFAULT_BY_FUNC
        if kdo_func not in kdo_inverse_func_by.keys():
            return False

        (kdo_inverse_func, default) = kdo_inverse_func_by[kdo_func]
        assert default is not None, (default, kdo_func.__name__)

        # Call for more work when given a positive K-Int

        kint = self.kint_peek(default)
        if kint > 0:
            return False

        # Do nothing when given a zero K-Int

        if not kint:
            self.kint_pull(default=0)
            print(f"kint=0 func={kdo_func.__name__}", file=self.logfile)
            return True

        # Call the inverse when given a negative K-Int

        if kint < 0:
            self.kint_pull(default=0)
            self.kint_push(-kint)
            print(f"kint=0 func={kdo_inverse_func.__name__}", file=self.logfile)
            kdo_inverse_func(self)
            self.kint_pull(default=0)
            return True

        # Else call for more work

        return False

    def kdo_text_write_n(self) -> None:
        """Take the Chars of 1 Keyboard Chord Sequence as Text to write to Screen"""

        st = self.st
        kbytes = self.kbytes
        kchars = kbytes.decode()  # may raise UnicodeDecodeError

        kint = self.kint_pull(default=1)
        if not kint:
            return
        if kint < 0:
            self.alarm_ring()  # 'negative repetition arg' for Replace/ Insert
            return

        ktext = kint * kchars
        st.stwrite(ktext)  # for .kdo_text_write_n

        # Spacebar, printable US-Ascii, and printable Unicode

    def kdo_kcap_write_n(self) -> None:
        """Take the Str of 1 Keyboard Chord Sequence as Chars to write to Screen"""

        st = self.st
        kcap_str = self.kcap_str

        kint = self.kint_pull(default=1)
        if not kint:
            return
        if kint < 0:
            self.alarm_ring()  # 'negative repetition arg' for Replace/ Insert
            return

        ktext = kint * kcap_str
        st.stwrite(ktext)  # for .kdo_kcap_write_n

        # distinct printable echo without beep for unbound Keyboard Chord Sequences
        # like calmly kindly tell you what Keys you struck

    def alarm_ring(self) -> None:
        """Ring the Bell"""

        self.st.stprint("\a")

        # 00/07 Bell (BEL)

    #
    # Wrap around the Screen and Keyboard of our StrTerminal
    #

    def write_form_kint(self, form, kint) -> None:
        """Write a CSI Form to the Screen filled out by the Digits of the K Int"""

        assert "{}" in form, (form,)
        assert kint >= 1, (kint,)

        st = self.st

        if kint == 1:
            schars = form.format("")
        else:
            schars = form.format(kint)

        st.stwrite(schars)  # for .write_form_kint

    #
    # Quit
    #

    def kdo_force_quit(self) -> None:
        """Revert changes to the O Lines, and quit this Linux Process"""

        _ = self.kint_pull(default=0)  # todo: 'returncode = ' inside 'kdo_force_quit'

        sys.exit()  # ignore the K Int

        # Emacs ⌃X ⌃S ⌃X ⌃C save-buffer save-buffers-kill-terminal

        # Vi ⌃C ⌃L : Q ! Return quit-no-save
        # Vi ⇧Z ⇧Q quit-no-save
        # Vi ⇧Z ⇧Z save-quit

    def kdo_help_quit(self) -> None:
        """Take a Keyboard Chord Sequence to mean say how to quit Vi"""

        # no .kint_pull here

        self.help_quit()  # for .kdo_help_quit

    def help_quit(self) -> None:
        """Say how to quit Vi"""

        st = self.st
        # no .pull_int here

        quit_kcap_strs = list()
        for kcap_str, call in KDO_CALL_BY_KCAP_STR.items():
            func = call[0]
            if func is LineTerminal.kdo_force_quit:

                quit_kcap_str = kcap_str
                if (kcap_str[:1] != "⌃") or (kcap_str[:2] == "⌃L"):
                    quit_kcap_str = "⌃C " + kcap_str

                quit_kcap_strs.append(quit_kcap_str)

        quit_kcap_strs.sort()

        st.stprint()
        quits = "  ".join("".join(_.split()) for _ in quit_kcap_strs)
        st.stprint(f"To quit, press one of  {quits}")

        # 'Press ⌃L⌃C:Q!Return or ⌃X⌃C or ⌃X⌃S⌃X⌃C or ⇧Z⇧Q or ⇧Z⇧Z to quit'
        # todo: Emacs doesn't bind '⌃C R' to (revert-buffer 'ignoreAuto 'noConfirm)
        # todo: Emacs freaks if you delete the ⌃X⌃S File before calling ⌃X⌃S

        # Emacs/ Vi famously leave how-to-quit nearly never mentioned

    #
    # Quote
    #

    def kdo_quote_kchars(self) -> None:
        """Block till the next K Chord, but then take it as Text, not as Command"""

        st = self.st

        kint = self.kint_pull(default=1)
        if kint < 0:
            self.alarm_ring()  # 'negative repetition arg' for Texts_Wrangle etc
            return

        self.logfile.flush()
        (kbytes, kchord_str) = st.pull_one_kchord_bytes_str()

        kchars = kbytes.decode()  # may raise UnicodeEncodeError
        ktext = kint * kchars
        st.stwrite(ktext)  # for .kdo_quote_kchars

        # Emacs ⌃Q quoted-insert/ replace
        # Vi ⌃V

    def kdo_quote_csi_kstrs_n(self) -> None:
        """Block till CSI Sequence complete, then take it as Text"""

        st = self.st
        kstr_stops = self.kstr_stops
        kcap_str = self.kcap_str
        # no .pull_int here

        assert CSI_I_P_BYTES == b"".join(bytes([_]) for _ in range(0x20, 0x40))

        # Run as [ only after ⎋, else reject the .kcap_str [ as if entirely unbound

        if kcap_str == "[":
            if (not kstr_stops) or (kstr_stops[-1] != "⎋"):
                self.kdo_kcap_write_n()  # for Key Cap [ inside .kdo_quote_csi_kstrs_n
                return

        # Block till CSI Sequence complete

        kbytes = b"\x1B" b"["
        kcap_str = "⎋ ["

        while True:
            self.logfile.flush()
            (kchord_bytes, kchord_str) = st.pull_one_kchord_bytes_str()

            kbytes += kchord_bytes

            sep = " "  # '⇧Tab'  # '⇧T a b'  # '⎋⇧Fn X'  # '⎋⇧FnX'
            kcap_str += sep + kchord_str

            if KDEBUG:
                st.stprint(f"{kbytes=} {kcap_str=}  # kdo_quote_csi_kstrs_n")

            read_2 = kchord_bytes
            if len(read_2) == 1:
                ord_2 = read_2[-1]
                if 0x20 <= ord_2 < 0x40:  # !"#$%&'()*+,-./0123456789:;<=>?
                    continue

            break

        self.kbytes = kbytes
        self.kcap_str = kcap_str

        # Write as if via 'self.kdo_text_write_n()'  # ⎋[m, ⎋[1m, ⎋[31m, ...

        kint = self.kint_pull(default=1)
        kchars = kbytes.decode()  # may raise UnicodeDecodeError
        ktext = kint * kchars
        st.stwrite(ktext)  # for .kdo_quote_csi_kstrs_n

        # Pq [ quote.csi.kstrs  # missing from Emacs, Vi, VsCode
        # unlike Vi [ Key Map

    #
    # For context, remember some of the Keyboard Chord Sequences awhile
    #

    def kdo_kminus(self) -> None:
        """Jump back by one or more Lines, but land past the Dent"""

        kstr_starts = self.kstr_starts  # no .pull_int here

        # Hold Key Cap "-" for context, after Emacs ⌃U, but not after Vi 0123456789

        kdigits = list(_ for _ in kstr_starts if _ in list("0123456789"))
        kstarts_closed = kstr_starts[1:][-1:] == ["⌃U"]

        if not kdigits:
            if kstr_starts and not kstarts_closed:
                self.kdo_hold_start_kstr("-")
                return

        kdo_func = LineTerminal.kdo_dent_minus_n  # Vi -
        done = self.kdo_inverse_or_nop(kdo_func)
        if not done:
            kdo_func(self)

        # Emacs Digit - after ⌃U
        # Vi Digit -

    def kdo_kzero(self) -> None:
        """Hold another Digit, else jump to First Column"""

        kstr_starts = self.kstr_starts  # no .pull_int here
        kstarts_closed = kstr_starts[1:][-1:] == ["⌃U"]

        # Hold Key Cap "0" for context, after Emacs ⌃U or after Vi 123456789

        if kstr_starts and not kstarts_closed:
            self.kdo_hold_start_kstr("0")
            return

        # Else jump to First Column

        self.kdo_column_1()  # for Vi 0

        # Emacs Digit 0 after ⌃U
        # Vi Digit 0 after 1 2 3 4 5 6 7 8 9
        # Vi 0

    def kdo_hold_start_kstr(self, kcap_str) -> None:
        """Hold Key-Cap Str's till taken as Arg"""

        kstr_starts = self.kstr_starts  # no .pull_int here

        kstr_starts_before = list(kstr_starts)
        self.try_kdo_hold_start_kstr(kcap_str=kcap_str)

        assert kstr_starts != kstr_starts_before, (kstr_starts, kstr_starts_before)

    def try_kdo_hold_start_kstr(self, kcap_str) -> None:
        """Hold Key-Cap Str's till taken as Arg"""

        kstr_starts = self.kstr_starts  # no .pull_int here
        kcap_str = self.kcap_str

        kcap_split = kcap_str.split()[-1]  # such as '3' from '⌃Q 3'
        assert kcap_split in (["⌃U"] + list("-0123456789")), (kcap_split,)

        # ⌃U+ vs [-]⌃U* vs [-][-]⌃U* vs [0123456789]+⌃U? vs [-][0123456789]+⌃U?

        kdigits = list(_ for _ in kstr_starts if _ in list("0123456789"))

        kstarts_sorted_set = sorted(set(kstr_starts))
        kpithy = kstarts_sorted_set not in ([], ["-"], ["-", "⌃U"], ["⌃U"])
        assert kpithy == bool(kdigits), (kpithy, kdigits, kstr_starts)

        # Take ⌃U after Digits as starting over, else pile them up

        kstarts_closed = kstr_starts[1:][-1:] == ["⌃U"]

        if kcap_split == "⌃U":
            if kdigits and kstarts_closed:
                kstr_starts.clear()  # for .hold_start_kstr ⌃U
            kstr_starts.append("⌃U")
            return

        # Take an odd or even count of Dash, until the first Digit

        if kcap_split == "-":
            if not kdigits:
                if kstr_starts != ["-"]:
                    kstr_starts.clear()  # for .hold_start_kstr -
                kstr_starts.append("-")
                return

            # else fall-thru

        # Hold the first Digit, or more Digits, after one Dash or none

        if kcap_split in list("0123456789"):
            if not kdigits:
                negated = kstr_starts == ["-"]
                kstr_starts.clear()  # for .hold_start_kstr 0123456789
                if negated:
                    kstr_starts.append("-")
                kstr_starts.append(kcap_split)
                return
            elif not kstarts_closed:
                kstr_starts.append(kcap_split)
                return

            # else fall-thru

        # Take this Key-Cap Str as Unbound Verb of 'def verbs_wrangle'

        self.kdo_kcap_write_n()  # for .hold_start_kstr of Key Cap -0123456789

        # Emacs '-', and Emacs 0 1 1 2 3 4 5 6 7 8 9, after Emacs ⌃U
        # Pq Em/Vi Csi Sequences:  ⎋[m, ⎋[1m, ⎋[31m, ...
        # Vi 1 2 3 4 5 6 7 8 9, and Vi 0 thereafter

    def kdo_hold_stop_kstr(self) -> None:
        """Hold Key-Cap Stop Str just long enough to see if struck twice in a row"""

        kstr_stops = self.kstr_stops  # ignores the .kstr_starts
        kcap_str = self.kcap_str

        assert len(kstr_stops) <= 1, (len(kstr_stops), kstr_stops, kcap_str)
        if kstr_stops == [kcap_str]:
            self.help_quit()  # for .kdo_hold_stop_kstr

        # Pq ⎋ ⌃C ⌃D ⌃G ⌃\  # missing from Emacs, Vi, VsCode

    #
    # Boil our memory of Keyboard Chord Sequences down to one Int Value
    #

    def kint_push(self, kint) -> None:
        """Fill the cleared Key-Cap Str Holds, as if Emacs ⌃U ..."""

        kstr_starts = self.kstr_starts
        assert not kstr_starts, (kstr_starts,)

        kstr_starts.extend(["⌃U"] + list(str(kint)) + ["⌃U"])

        # does pushed as wrapped, could push as not-wrapped

    def kint_pull_positive(self, default) -> int:
        """Fetch & clear a Positive Int Literal from out of the Key-Cap Str Holds"""

        kint = self.kint_pull(default=default)
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

        kint_else = self.kint_peek_else(default)
        assert kint_else is not None, (kint_else, default)
        kint = kint_else

        return kint

    def kint_peek_else(self, default) -> int | None:
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

        return kint  # positive kint for the Vi .kmap

        # raises ValueError if ever '.kstr_starts' isn't Cancelled or an Int Literal

    #
    # Move the Screen Cursor to a Column, relatively or absolutely
    #

    def kdo_char_minus_n(self) -> None:
        """Step back by one or more Chars"""

        self.kdo_column_minus_n()  # Vim wraps Delete ^H left  # Emacs wraps ←

        # Emacs ← left-char
        # Vi Delete
        # Vi ^H

    def kdo_char_plus_n(self) -> None:
        """Step ahead by one or more Chars"""

        self.kdo_column_plus_n()  # Vim wraps Spacebar right  # Emacs wraps →

        # Emacs → right-char
        # Vi Spacebar

    def kdo_column_plus(self) -> None:
        """Jump to a zero-based numbered Column for Pedantic Emacs"""

        #

        kint = self.kint_pull(default=0)
        if kint < 0:  # Emacs says 'Wrong type argument: wholenump'
            self.alarm_ring()  # 'negative repetition arg' for Emacs ⎋ G Tab
            return

        kint_plus = kint + 1

        #

        self.write_form_kint("\x1B" "[" "{}G", kint=kint_plus)

        assert CHA_Y == "\x1B" "[" "{}G"  # 04/07 Cursor Character Absolute

        # Emacs ⎋ G Tab move-to-column

    def kdo_column_1(self) -> None:
        """Jump to Left of Line"""

        # no .pull_int here

        st = self.st
        st.stwrite("\r")  # 00/13  # "\x0D"  # "\x1B" "[" "G"

        assert CR == "\r"  # 00/13 Carriage Return (CR) ⌃M
        assert CHA == "\x1B" "[" "G"  # 04/07 Cursor Character Absolute

        # part of .kdo_kzero Vi 0

    def kdo_column_minus_n(self) -> None:
        """Jump back by one or more Columns"""

        kint = self.kint_pull_positive(default=1)
        self.write_form_kint("\x1B" "[" "{}D", kint=kint)

        # 00/08 Backspace (BS) \b ⌃H
        # 07/15 Delete (DEL) \x7F ⌃? 'Eliminated Control Function'

        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left

        # Vi ←
        # Vi H

    def kdo_column_dent_beyond(self) -> None:
        """Jump to the first Column beyond the Dent"""

        # no .pull_int here

        st = self.st
        st.stwrite("\r")  # 00/13  # "\x0D"  # "\x1B" "[" "G"

        assert CR == "\r"  # 00/13 Carriage Return (CR) ⌃M
        assert CHA == "\x1B" "[" "G"  # 04/07 Cursor Character Absolute

        # Vi ^

    def kdo_column_n(self) -> None:
        """Jump to a numbered Column"""

        #

        kint = self.kint_pull(default=1)
        if not kint:
            self.alarm_ring()  # todo: Pq | Zero Column could be Middle
            return
        if kint < 0:
            self.alarm_ring()  # todo: Pq | Negative Column
            self.write_form_kint("\x1B" "[" "{}G", kint=kint)
            return

        #

        self.write_form_kint("\x1B" "[" "{}G", kint=kint)

        assert CHA_Y == "\x1B" "[" "{}G"  # 04/07 Cursor Character Absolute

        # Vi |
        # VsCode ⌃G {line}:{column}

    def kdo_column_plus_n(self) -> None:
        """Jump ahead by one or more Columns"""

        kint = self.kint_pull_positive(default=1)
        self.write_form_kint("\x1B" "[" "{}C", kint=kint)

        assert CUF_X == "\x1B" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right

        # Vi →
        # Vi L

    def kdo_tab_minus_n(self) -> None:
        """Jump back by one or more Column Tabs"""

        kint = self.kint_pull_positive(default=1)
        self.write_form_kint("\x1B" "[" "{}Z", kint=kint)

        assert CBT_X == "\x1B" "[" "{}Z"  # CSI 05/10 Cursor Backward Tabulation
        assert CUB_X == "\x1B" "[" "{}D"  # CSI 04/04 Cursor [Back] Left

        # Pq ⇧Tab tab.minus.n  # missing from Emacs, Vi, VsCode

    def kdo_tab_plus_n(self) -> None:
        """Jump ahead by one or more Column Tabs"""

        kint = self.kint_pull_positive(default=1)
        self.write_form_kint("\x1B" "[" "{}I", kint=kint)
        # st.stwrite(kint * "\t")  # 00/09

        assert CHT_X == "\x1B" "[" "{}I"  # CSI 04/09 Cursor Forward [Horizontal] Tab~
        assert CUF_X == "\x1B" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right
        assert HT == "\t"  # 00/09 Character Tabulation ⌃I

        # Pq Tab tab.plus.n  # missing from Emacs, Vi, VsCode

    #
    # Move the Screen Cursor to a Row, relatively or absolutely
    #

    def kdo_dent_line_n(self) -> None:
        """Jump to a numbered Line, but land past the Dent"""

        assert Y_32100 == 32100  # vs VPA_Y "\x1B" "[" "{}d"

        kint = self.kint_pull(default=32100)  # todo: more Rows
        if not kint:
            self.alarm_ring()  # todo: Pq G Zero Line Number
            return
        if kint < 0:
            self.alarm_ring()  # todo: Pq G Negative Line Number
            return

        #

        self.write_form_kint("\x1B" "[" "{}d", kint=kint)
        self.kdo_column_dent_beyond()  # for Vim G

        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

        assert CR == "\r"  # 00/13 Carriage Return (CR) ⌃M
        assert CHA == "\x1B" "[" "G"  # 04/07 Cursor Character Absolute

        # Vi G

    def kdo_dent_minus_n(self) -> None:
        """Jump back by one or more Lines, but land past the Dent"""

        self.kdo_line_minus_n()
        self.kdo_column_dent_beyond()  # for Vim -

        # Vi -
        # part of Pq -

    def kdo_dent_plus_n(self) -> None:
        """Jump ahead by one or more Lines, but land past the Dent"""

        self.kdo_line_plus_n()
        self.kdo_column_dent_beyond()  # for Vim +

        # Vi +

    def kdo_dent_plus_n1(self) -> None:
        """Jump ahead by zero or more Lines, but land past the Dent"""

        #

        kint = self.kint_pull(default=1)
        if not kint:
            return
        if kint < 0:
            self.alarm_ring()  # todo: Pq _ Negative could be Vi -
            return

        #

        if kint > 1:
            kint_minus = kint - 1
            self.write_form_kint("\x1B" "[" "{}B", kint=kint_minus)

        self.kdo_column_dent_beyond()  # for Vim _

        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down

        # Vi _

    def kdo_end_plus_n1(self) -> None:
        """Jump ahead by zero or more Lines, and land at End of Line"""

        #

        kint = self.kint_pull(default=1)

        if not kint:
            self.alarm_ring()  # todo: Pq $ Zero
            return
        if kint < 0:
            self.alarm_ring()  # todo: Pq $ Negative could be Vi ⌃E
            return

        #

        assert X_32100 == 32100  # vs CUF_X "\x1B" "[" "{}C"

        if kint > 1:
            kint_minus = kint - 1
            self.write_form_kint("\x1B" "[" "{}B", kint=kint_minus)

        self.write_form_kint("\x1B" "[" "{}C", kint=32100)  # todo: more Columns

        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down
        assert CUF_X == "\x1B" "[" "{}C"  # CSI 04/03 Cursor [Forward] Right

        # Emacs ⌃E move-end-of-line
        # Vi $

    def kdo_home_n(self) -> None:
        """Jump to a numbered Line, and land at Left of Line"""

        assert Y_32100 == 32100  # vs VPA_Y "\x1B" "[" "{}d"

        kint = self.kint_pull(default=32100)  # todo: more Rows

        if not kint:
            self.alarm_ring()  # todo: Pq ⎋G G Zero Row Number could be Middle
            return
        if kint < 0:
            self.alarm_ring()  # todo: Pq ⎋G G Negative Row Number
            return

        # Jump to Line and land at Left of Line

        self.write_form_kint("\x1B" "[" "{}d", kint=kint)
        self.kdo_column_1()  # for Emacs ⎋G G Goto-Line

        # Disassemble these StrTerminal Writes

        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute

        assert CR == "\r"  # 00/13 Carriage Return (CR) ⌃M
        assert CHA == "\x1B" "[" "G"  # 04/07 Cursor Character Absolute

        # Emacs ⎋G G goto-line  # also Emacs ⎋G ⎋G goto-line

    def kdo_home_plus_n1(self) -> None:
        """Jump ahead by zero or more Lines, and land at Left of Line"""

        #

        kint = self.kint_pull(default=1)

        if not kint:
            self.alarm_ring()  # todo: zero Emacs ⌃A
            return
        if kint < 0:
            self.alarm_ring()  # todo: negative Emacs ⌃A
            return

        #

        if kint > 1:
            kint_minus = kint - 1
            self.write_form_kint("\x1B" "[" "{}B", kint=kint_minus)

        self.kdo_column_1()  # for Emacs ⌃A Left of Line

        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down

        # Emacs ⌃A move-beginning-of-line

    def kdo_line_minus_n(self) -> None:
        """Jump back by one or more Lines"""

        kint = self.kint_pull_positive(default=1)
        self.write_form_kint("\x1B" "[" "{}A", kint=kint)

        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up

        # Emacs ⌃P previous-line
        # Vi K

    def kdo_line_plus_n(self) -> None:
        """Jump ahead by one or more Lines"""

        kint = self.kint_pull_positive(default=1)
        self.write_form_kint("\x1B" "[" "{}B", kint=kint)

        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down

        # Emacs ⌃N next-line
        # Vi ⌃J
        # Vi J

    def kdo_row_n_down(self) -> None:
        """Jump to Top of Screen, but ahead by zero or more Lines"""

        kint = self.kint_pull_positive(default=1)

        self.write_form_kint("\x1B" "[" "{}d", kint=1)
        if kint > 1:
            kint_minus = kint - 1
            self.write_form_kint("\x1B" "[" "{}B", kint=kint_minus)

        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute
        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down

        # Emacs ⎋ R move-to-window-line-top-bottom, with Zero-Based Positive K-Int
        # Vi ⇧H

    def kdo_row_n_up(self) -> None:
        """Jump to Bottom of Screen, but back behind by zero or more Lines"""

        kint = self.kint_pull_positive(default=1)

        assert Y_32100 == 32100  # vs VPA_Y "\x1B" "[" "{}d"

        self.write_form_kint("\x1B" "[" "{}d", kint=32100)  # todo: more Rows
        if kint > 1:
            kint_minus = kint - 1
            self.write_form_kint("\x1B" "[" "{}A", kint=kint_minus)

        assert VPA_Y == "\x1B" "[" "{}d"  # CSI 06/04 Line Position Absolute
        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up

        # Emacs ⎋ R move-to-window-line-top-bottom, with Negative K-Int
        # Vi ⇧L

    #
    # Dedent or Dent the Lines at and below the Screen Cursor
    #

    def kdo_lines_dedent_n(self) -> None:
        """Remove Blank Space from the Left of one or more Lines"""

        st = self.st
        kint = self.kint_pull_positive(default=1)

        # Delete 4 Columns at Left of Line, then climb back up
        # todo: Vim deletes only Blank Space

        st.stwrite("\r")  # 00/13  # "\x0D"  # "\x1B" "[" "G"

        for i in range(kint):
            st.stwrite("\x1B" "[" "4" "P")  # CSI 05/00
            if i < (kint - 1):
                st.stwrite("\n")  # 00/10  # "\x0A"  # "\x1B" "[" "B"

        for i in range(kint - 1):
            st.stwrite("\x1B" "[" "A")  # CSI 04/01

        self.kdo_column_dent_beyond()  # for Vim < <

        # Disassemble these StrTerminal Writes

        assert CR == "\r"  # 00/13 Carriage Return (CR) ⌃M
        assert DCH_X == "\x1B" "[" "{}P"  # CSI 05/00 Delete Character
        assert LF == "\n"  # 00/10 Line Feed (LF) ⌃J
        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up

    def kdo_lines_dent_n(self) -> None:
        """Insert 1 Dent of Blank Space into the Left of one or more Lines"""

        st = self.st
        kint = self.kint_pull_positive(default=1)

        # Insert 4 Columns at Left of Line, then climb back up

        for i in range(kint):
            st.stwrite("\r")  # 00/13  # "\x0D"  # "\x1B" "[" "G"
            self.write_form_kint("\x1B" "[" "{}@", kint=4)  # CSI 04/00
            if i < (kint - 1):
                st.stwrite("\n")  # 00/10  # "\x0A"  # "\x1B" "[" "B"

        for i in range(kint - 1):
            st.stwrite("\x1B" "[" "A")  # CSI 04/01

        self.kdo_column_dent_beyond()  # for Vim > >

        # Disassemble these StrTerminal Writes

        assert CR == "\r"  # 00/13 Carriage Return (CR) ⌃M
        assert ICH_X == "\x1B" "[" "{}@"  # CSI 04/00 Insert Character
        assert LF == "\n"  # 00/10 Line Feed (LF) ⌃J
        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up

    #
    # Delete the Lines at and below the Screen Cursor
    #

    def kdo_dents_cut_n(self) -> None:
        """Cut N Lines here and below, and land past Dent"""

        st = self.st

        #

        kint = self.kint_pull(default=1)

        if not kint:
            return

        if kint < 0:
            self.alarm_ring()  # todo: negative Vi D
            return

        # Cut N Lines here and below, and land past Dent

        st.stwrite("\r")  # 00/13  # "\x0D"  # "\x1B" "[" "G"
        self.write_form_kint("\x1B" "[" "{}M", kint=kint)

        assert DL_Y == "\x1B" "[" "{}M"  # CSI 04/13 Delete Line

        # Vi D D

    #
    # Switch between Replace Mode, Insert Mode, and View Mode
    #

    def kdo_insert_n_till(self) -> None:
        """Insert Text Sequences till ⌃C, except for ⌃O and Control Sequences"""

        #

        kint = self.kint_pull(default=1)
        if kint != 1:
            self.alarm_ring()  # todo: arg for Vi I
            return

        #

        self.texts_vmode_wrangle("Insert")

        # Vi I

    def kdo_replace_n_till(self) -> None:
        """Replace Text Sequences till ⌃C, except for ⌃O and Control Sequences"""

        #

        kint = self.kint_pull(default=1)
        if kint != 1:
            self.alarm_ring()  # todo: arg for Vi ⇧R
            return

        #

        self.texts_vmode_wrangle("Replace")

        # Vi ⇧R

    def kdo_insert_return(self) -> None:
        """Insert an Empty Line below, and land at Left of Line"""

        st = self.st

        st.stwrite("\r")  # 00/13  # "\x0D"  # "\x1B" "[" "G"
        st.stwrite("\n")  # 00/10  # "\x0A"  # "\x1B" "[" "B"

        st.stwrite("\x1B" "[" "L")  # CSI 04/12 Insert Line

        assert IL_Y == "\x1B" "[" "{}L"  # CSI 04/12 Insert Line

        # Vi ⇧R I Return  # todo: move tail of Line into new inserted Line

    def kdo_char_delete_left(self) -> None:
        """Delete 1 Character to the Left"""

        st = self.st

        st.stwrite("\b")  # 00/08  # "\x08"  # "\x1B" "[" "D
        st.stwrite("\x1B" "[" "P")  # CSI 05/00 Delete Character

        assert BS == "\b"  # 00/08 Backspace ⌃H
        assert DCH_X == "\x1B" "[" "{}P"  # CSI 05/00 Delete Character

        # Vi ⇧R I Delete

    def kdo_add_bottom_row(self) -> None:
        """Insert new Bottom Rows, and move Cursor Up by that much"""

        kint = self.kint_pull_positive(default=1)
        self.write_form_kint("\x1B" "[" "{}S", kint=kint)
        self.write_form_kint("\x1B" "[" "{}A", kint=kint)

        # Disassemble these StrTerminal Writes

        assert SU_Y == "\x1B" "[" "{}S"  # CSI 05/03 Scroll Up   # Add Bottom Rows
        assert CUU_Y == "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up

        # Vi ⌃Y
        # collides with Emacs ⌃Y

    def kdo_add_top_row(self) -> None:
        """Insert new Top Rows, and move Cursor Down by that much"""

        kint = self.kint_pull_positive(default=1)
        self.write_form_kint("\x1B" "[" "{}T", kint=kint)
        self.write_form_kint("\x1B" "[" "{}B", kint=kint)

        # Disassemble these StrTerminal Writes

        assert SD_Y == "\x1B" "[" "{}T"  # CSI 05/04 Scroll Down  # Add Top Rows
        assert CUD_Y == "\x1B" "[" "{}B"  # CSI 04/02 Cursor Down

        # Vi ⌃E
        # collides with Emacs ⌃E


STOP_KCAP_STRS = ("⌃C", "⌃D", "⌃G", "⎋", "⌃\\")  # ..., b'\x1B, b'\x1C'


LT = LineTerminal


EM_KDO_CALL_BY_KCAP_STR: dict[str, PY_CALL]

VI_KDO_CALL_BY_KCAP_STR: dict[str, PY_CALL]

PQ_KDO_CALL_BY_KCAP_STR: dict[str, PY_CALL]

KDO_CALL_BY_KCAP_STR: dict[str, PY_CALL]

EM_KDO_CALL_BY_KCAP_STR = {
    #
    "⎋G G": (LT.kdo_home_n,),
    "⎋G ⎋G": (LT.kdo_home_n,),
    "⎋G Tab": (LT.kdo_column_plus,),
    # "⎋ R": (LT.kdo_row_middle_up_down,),
    "⌃A": (LT.kdo_home_plus_n1,),  # b'\x01'
    "⌃E": (LT.kdo_end_plus_n1,),  # b'\x05'
    "⌃N": (LT.kdo_line_plus_n,),  # b'\x0E'
    "⌃P": (LT.kdo_line_minus_n,),  # b'\x10'
    "⌃Q": (LT.kdo_quote_kchars,),  # b'\x11'
    "⌃U": (LT.kdo_hold_start_kstr, tuple(["⌃U"])),  # b'\x15'
    # "⌃X 8 Return": (LT.unicodedata_lookup,),  # Emacs insert-char
    #
    "⌥G G": (LT.kdo_home_n,),
    "⌥G ⌥G": (LT.kdo_home_n,),
    "⌥G Tab": (LT.kdo_column_plus,),
    # "⌥ R": (LT.kdo_row_middle_up_down,),
}

VI_KDO_CALL_BY_KCAP_STR = {
    #
    "Return": (LT.kdo_dent_plus_n,),  # b'\x0D'  # b'\r'
    "⌃E": (LT.kdo_add_bottom_row,),  # b'\x05'
    "⌃V": (LT.kdo_quote_kchars,),  # b'\x16'
    "⌃Y": (LT.kdo_add_top_row,),  # b'\x19'
    "↑": (LT.kdo_line_minus_n,),  # b'\x1B[A'
    "↓": (LT.kdo_line_plus_n,),  # b'\x1B[B'
    "→": (LT.kdo_column_plus_n,),  # b'\x1B[C'
    "←": (LT.kdo_column_minus_n,),  # b'\x1B[D'
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
    "< <": (LT.kdo_lines_dedent_n,),
    "> >": (LT.kdo_lines_dent_n,),
    #
    "⇧G": (LT.kdo_dent_line_n,),  # b'G'
    "⇧H": (LT.kdo_row_n_down,),  # b'H'
    "⇧L": (LT.kdo_row_n_up,),  # b'L'
    "⇧R": (LT.kdo_replace_n_till,),  # b'R'
    "^": (LT.kdo_column_dent_beyond,),  # b'\x5E'
    "_": (LT.kdo_dent_plus_n1,),  # b'\x5F'
    #
    "D D": (LT.kdo_dents_cut_n,),  # b'd'
    "H": (LT.kdo_column_minus_n,),  # b'h'
    "I": (LT.kdo_insert_n_till,),  # b'i'
    "J": (LT.kdo_line_plus_n,),  # b'j'
    "K": (LT.kdo_line_minus_n,),  # b'k'
    "L": (LT.kdo_column_plus_n,),  # b'l'
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
    "⌃C": (LT.kdo_hold_stop_kstr,),  # b'\x03'
    "⌃D": (LT.kdo_hold_stop_kstr,),  # b'\x04'
    "⌃E": (LT.kdo_end_plus_n1,),  # b'\x05'
    "⌃G": (LT.kdo_hold_stop_kstr,),  # b'\x07'
    "Tab": (LT.kdo_tab_plus_n,),  # b'\x09'  # b'\t'
    "⌃J": (LT.kdo_line_plus_n,),  # b'\x0A'  # b'\n'
    "⌃L : Q ! Return": (LT.kdo_force_quit,),  # b'\x0C...
    "⌃L ⇧Z ⇧Q": (LT.kdo_force_quit,),  # b'\x0C...
    "⌃L ⇧Z ⇧Z": (LT.kdo_force_quit,),  # b'\x0C...
    # "⌃Q ⌃Q": (LT.kdo_quote_kchars,),  # b'\x11...  # no, go with ⌃V ⌃Q
    # "⌃V ⌃V": (LT.kdo_quote_kchars,),  # b'\x16...  # no, go with ⌃Q ⌃V
    "⌃X ⌃C": (LT.kdo_force_quit,),  # b'\x18...
    "⌃X ⌃S ⌃X ⌃C": (LT.kdo_force_quit,),  # b'\x18...
    "⇧Tab": (LT.kdo_tab_minus_n,),  # b'\x1B[Z'
    "⌃\\": (LT.kdo_hold_stop_kstr,),  # ⌃\  # b'\x1C'
    #
    "⇧Q V I Return": (LT.kdo_help_quit,),  # b'Qvi\r'
    "⇧Z ⇧Q": (LT.kdo_force_quit,),  # b'ZQ'
    "⇧Z ⇧Z": (LT.kdo_force_quit,),  # b'ZZ'
    "[": (LT.kdo_quote_csi_kstrs_n,),  # b'\x5B'
    #
    "⌥⎋": (LT.kdo_help_quit,),  # Option Esc
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
KDO_CALL_BY_KCAP_STR.update(EM_KDO_CALL_BY_KCAP_STR)
KDO_CALL_BY_KCAP_STR.update(VI_KDO_CALL_BY_KCAP_STR)
KDO_CALL_BY_KCAP_STR.update(PQ_KDO_CALL_BY_KCAP_STR)

KDO_CALL_KCAP_STRS = sorted(KDO_CALL_BY_KCAP_STR.keys())

# hand-sorted as ⎋, ⌃, 0..9, ⇧A..⇧Z, A..Z order of K Bytes
# not so much by ⎋ ⌃ ⌥ ⇧ ⌘ Fn order

# todo: Emacs ⌃U - for non-positive K-Int

# todo: assert Keys of KDO_CALL_BY_KCAP_STR reachable by StrTerminal
#   such as '⎋' less reachable while '⎋ G Tab' defined
#       because 'kdo_call_kcap_strs'


# Run these K Do Func's as is when called with positive Arg,
#   as paired when called with negative Arg, and as nothing when called with zeroed Arg

VI_KDO_INVERSE_FUNC_DEFAULT_BY_FUNC = {
    LT.kdo_add_bottom_row: (LT.kdo_add_top_row, 1),  # ⌃E
    LT.kdo_add_top_row: (LT.kdo_add_bottom_row, 1),  # ⌃Y
    LT.kdo_column_minus_n: (LT.kdo_column_plus_n, 1),  # ← H
    LT.kdo_column_plus_n: (LT.kdo_column_minus_n, 1),  # → L
    LT.kdo_dent_minus_n: (LT.kdo_dent_plus_n, 1),  # -
    LT.kdo_dent_plus_n: (LT.kdo_dent_minus_n, 1),  # Return +
    LT.kdo_line_minus_n: (LT.kdo_line_plus_n, 1),  # ↓ ⌃J ⌃N J
    LT.kdo_line_plus_n: (LT.kdo_line_minus_n, 1),  # ↑ ⌃P K
    LT.kdo_lines_dedent_n: (LT.kdo_lines_dent_n, 1),  # < <
    LT.kdo_lines_dent_n: (LT.kdo_lines_dedent_n, 1),  # > >
    LT.kdo_row_n_down: (LT.kdo_row_n_up, 1),  # ⇧L
    LT.kdo_row_n_up: (LT.kdo_row_n_down, 1),  # ⇧H
    LT.kdo_tab_minus_n: (LT.kdo_tab_plus_n, 1),  # Tab ⇥
    LT.kdo_tab_plus_n: (LT.kdo_tab_minus_n, 1),  # ⇧Tab ⇤
}


#
# presently
#
#   Emacs  ⎋GG ⎋GTab
#   Emacs  ⌃A ⌃E ⌃N ⌃P ⌃Q ⌃U
#   Emacs  ⌥GG ⌥GTab
#
#   Vi  Return ⌃E ⌃V ⌃Y ← ↓ ↑ →
#   Vi  Spacebar $ + - 0 123456789 << >>
#   Vi  ⇧G ⇧H ⇧L ⇧R ^ _
#   Vi  DD H I J K L | Delete
#
#   Pq  ⎋ ⎋⎋ ⎋[ ⌃C ⌃D ⌃G Tab ⇧Tab ⌃J ⌃L⌃C:Q!Return ⌃X⌃C ⌃X⌃S⌃X⌃C ⌃\
#   Pq  ⇧QVIReturn ⇧Z⇧Q ⇧Z⇧Z [ ⌥⎋ ⌥[
#
#   Option Mouse click moves Cursor via ← ↑ → ↓
#   Keyboard Trace at:  tail -F -n +15 .pqinfo/keylog.py
#

#
# smallish todo's
#
#   bind << >> DD outside of themselves  # verb_read D D < < > >
#
#   ⌃K ⇧A C ⇧D ⇧I ⇧O ⇧R ⇧S ⇧X A C$ CC D$ DD I O R S X ⌃C ⎋
#   Pq ⌃Q escape to Vi ⌃D ⌃E ⌃G ⌃L ⌃U ⌃V ⌃W ^Y etc
#   Pq ⌃V escape to Emacs ⌃B ⌃C ⌃D ⌃F ⌃Q ⌃O ⌃V ⌃Y etc
#

#
# bigger todo's
#
#   Bounce Cursor to Tracer
#       Trace the unicode.name while Replace/ Insert
#       Delete the Message we last wrote, write the new, log Messages & lost Messages
#
#   Size the Screen
#       ⇧M
#       bind C⇧L D⇧L
#
#   ^Z and ways to send ^C ^\ Assert-False
#
#   ⌃H⌃A ⌃H⌃K
#
#   Shadow the Screen
#       Vim ⌃O ⌃I Undo/Redo movements that pierce the Shadow
#       Emacs ⌃T
#       < > C D to movement ⇧G etc
#       Bind Undo Keys to roll back
#

#
# later todo's:
#
#   ⌃L [ of Shadow Screen, of File larger than Screen ]
#   Emacs ⌃W ⌃Y
#   Vi :set ruler
#
#   Emacs ⌃R ⌃S Searches
#


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

    assert unicodedata.name("\xA0").title() == "No-Break Space"
    assert unicodedata.name("\xAD").title() == "Soft Hyphen"

    try:
        name = unicodedata.name(char)
        assert False, (name, hex(ord(char)), ascii(char))
    except ValueError as exc:
        assert str(exc) == "no such name"

    names = UNICODEDATA_NAMES_ANYHOW_BY_CHAR[char]
    for name in names:
        assert unicodedata.lookup(name) == char, (name, hex(ord(char)), ascii(char))

    name_0 = names[0]

    return name_0


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
    "\x0A": ("Line Feed", "LF"),
    "\x0B": ("Line Tabulation", "VT"),  # Vertical Tabulation
    "\x0C": ("Form Feed", "FF"),
    "\x0D": ("Carriage Return", "CR"),
    "\x0E": ("Shift Out", "SO"),
    "\x0F": ("Shift In", "SI"),
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
    "\x1A": ("Substitute", "SUB"),
    "\x1B": ("Escape", "ESC"),
    "\x1C": ("Information Separator Four", "FS"),  # File Separator
    "\x1D": ("Information Separator Three", "GS"),  # Group Separator
    "\x1E": ("Information Separator Two", "RS"),  # Record Separator
    "\x1F": ("Information Separator One", "US"),  # Unit Separator
    "\x7F": ("Delete", "DEL"),
    "\x82": ("Break Permitted Here", "BPH"),  # ! = "Zero Width Space" U+200B ZWSP
    "\x83": ("No Break Here", "NBH"),  # != "Word Joiner" U+2060 WJ
    "\x84": ("Index", "IND"),
    "\x85": ("Next Line", "NEL"),
    "\x86": ("Start of Selected Area", "SSA"),
    "\x87": ("End of Selected Area", "ESA"),
    "\x88": ("Character Tabulation Set", "HTS"),
    "\x89": ("Character Tabulation With Justification", "HTJ"),
    "\x8A": ("Line Tabulation Set", "VTS"),
    "\x8B": ("Partial Line Forward", "PLD"),
    "\x8C": ("Partial Line Backward", "PLU"),
    "\x8D": ("Reverse Line Feed", "RI"),
    "\x8E": ("Single Shift Two", "SS2"),
    "\x8F": ("Single Shift Three", "SS3"),
    "\x90": ("Device Control String", "DCS"),
    "\x91": ("Private Use One", "PU1"),
    "\x92": ("Private Use Two", "PU2"),
    "\x93": ("Set Transmit State", "STS"),
    "\x94": ("Cancel Character", "CCH"),
    "\x95": ("Message Waiting", "MW"),
    "\x96": ("Start of Guarded Area", "SPA"),
    "\x97": ("End of Guarded Area", "EPA"),
    "\x98": ("Start of String", "SOS"),
    "\x9A": ("Single Character Introducer", "SCI"),
    "\x9B": ("Control Sequence Introducer", "CSI"),
    "\x9C": ("String Terminator", "ST"),
    "\x9D": ("Operating System Command", "OSC"),
    "\x9E": ("Privacy Message", "PM"),
    "\x9F": ("Application Program Command", "APC"),
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

    iolines.sort()  # sort  # sorted sorted  # s s s s s s s


    obytes = b"\n".join(ibytes.splitlines()) + b"\n"  # bytes ended

    obytes = ibytes  # sponged  # sponge

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


    olines = ilines  # end  # ended  # chr ended  # ends every line with "\n"

    olines = pq.ex_macros(ilines)  # em em  # ema  # emac  # emacs

    olines = pq.visual_ex(ilines)  # vi  # vim


    oobject = "".join(chr(_) for _ in range(0x100))  # chr range

    oobject = len(ibytes)  # bytes len  # |wc -c  # wc c  # wcc

    oobject = len(itext)  # text characters chars len  # |wc -m  # wc m  # wcm

    oobject = len(itext.split())  # words len  # |wc -w  # wc w  # wcw

    oobject = len(itext.splitlines())  # lines len  # |wc -l  # wc l  # wcl

    oobject = math.e  # e e e e e e e

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

    otext = re.sub(r"(.)", repl=r"\1 ", string=itext).rstrip()  # sub  # repl

    otext = string.capwords(itext)  # capwords

    otext = textwrap.dedent(itext) + "\n"  # dedent  # dedented  # textwrap.dedent


    random.shuffle(iolines) # shuffle  # shuffled


"""


# todo: reject single-line snippets that don't have comments to name them

CUED_PY_GRAFS_TEXT = r"""

    # awk  # |awk '{print $NF}'  # a a a a
    iwords = iline.split()
    oline = iwords[-1] if iwords else ""

    # bytes range
    obytes = ibytes  # todo: say this without ibytes
    obytes = b"".join(bytes([_]) for _ in range(0x100))

    # cat n expand  # |cat -n |expand  # enum 1  # n n n n
    olines = list(f"{n:6d}  {i}" for (n, i) in enumerate(ilines, start=1))

    # closed # close  # ends last line with "\n"
    otext = itext if itext.endswith("\n") else (itext + "\n")

    # collections.Counter.keys  # counter  # set set set  # uniq  # uniq_everseen
    olines = list(dict((_, _) for _ in ilines).keys())  # unsort  # unsorted  # dedupe

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

    # head head  # h h h h h h
    olines = ilines[:10]

    # head tail  # h t  # h t  # h t  # h t  # h t  # ht ht
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

    # tail tail  # t t t t t t t t t
    olines = ilines[-10:]

    # ts  # |ts
    while True:
        readline = stdin.readline()
        if not readline:
            break
        iline = readline.splitlines()[0]
        ts = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S.%f %z")
        print(f"{ts}  {iline}", file=stdout)
        stdout.flush()

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

    # chill
    assert iline.startswith("http")  # "https", "http", etc
    assert " " not in iline
    oline = iline.replace("://", " :// ").replace(".", " . ").rstrip()

    # warm
    assert iline.startswith("http")  # "https", "http", etc
    assert " " in iline
    oline = iline.replace(" ", "")

"""

#
# crthin to:  http://codereviews/r/190588/diff
# crthin from:  https://codereviews.example.com/r/190588/diff/8/#index_header
#
# glink to:  https://docs.google.com/document/d/$HASH
# glink from:  https://docs.google.com/document/d/$HASH/edit?usp=sharing
# glink from:  https://docs.google.com/document/d/$HASH/edit#gid=0'
#
# jkthin to:  http://63xJenkins
# jkwide to:  https://63xjenkins.dev.example.com
#
# jkey to:  PROJ-12345
# jlink to:  https://jira.example.com/browse/PROJ-12345
#
# chill to:  https :// twitter . com /pelavarre/status/1647691634329686016
# warm to:  https://twitter.com/pelavarre/status/1647691634329686016
#


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
