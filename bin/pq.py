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
KCDEBUG = False  # Debug 'FUNC_BY_KCAP_STR'


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

        lotsa_shargs = list()
        for index, sharg in enumerate(shargs):
            if sharg == "--":  # accepts explicit "--" Sh Arg
                lotsa_shargs.extend(shargs[index:])
                break

            if not sharg.startswith("-"):  # inserts implicit "--" Sh Arg
                lotsa_shargs.append("--")
                lotsa_shargs.extend(shargs[index:])
                break

            lotsa_shargs.append(sharg)

        # Parse the Sh Args

        try:
            ns = parser.parse_args_else(lotsa_shargs)  # often prints help & exits zero
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
    olines = lt.verbs_wrangle(ilines, kmap="Emacs")

    return olines


def visual_ex(ilines) -> list[str]:
    """Edit in the way of Ex Vi"""

    lt = LineTerminal()
    olines = lt.verbs_wrangle(ilines, kmap="Vi")

    return olines


ESC = b"\x1B"


@dataclasses.dataclass
class BytesLogger:
    """Log Bytes arriving over time, for a time-accurate replay or analysis later"""

    tag: str  # 'k'  # 's'
    exists: bool  # True if the Log File already existed
    logfile: typing.TextIO  # '.pqinfo/keylog.py'
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

        logfile = path.open("a")
        self.logfile = logfile

        if not exists:
            self.write_prolog()

        self.logged = dt.datetime.now()

    def write_prolog(self) -> None:
        """Write the Code before the Log"""

        logfile = self.logfile
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

        logfile.write(py + "\n" "\n")

        # todo: duck away from PyPi·Org Black 'E501 line too long (... > 999 characters'

    def log_bytes_io(self, sbytes) -> None:
        """Log some Keyboard Input Bytes, Screen Output Bytes, etc"""

        logfile = self.logfile
        logged = self.logged

        now = dt.datetime.now()
        total_seconds = (now - logged).total_seconds()
        self.logged = now

        rep = black_repr(sbytes)

        print(f"    time.sleep({total_seconds})", file=logfile)
        print(f"    yield {rep}", file=logfile)


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

        self.before = before  # todo: test Tcsa Flush, not only Tcsa Drain
        self.tcgetattr_else = None
        self.kinterrupts = 0
        self.after = after

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
            if False:  # jitter 3/Aug  # ⌃C prints Py Traceback
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

            s0 = "\x1B" "[" "4l"  # CSI 06/12 Replace
            s1 = "\x1B" "[" " q"  # CSI 02/00 07/01  # No-Style Cursor
            self.btwrite((s0 + s1).encode())

            #

            tcgetattr = tcgetattr_else
            self.tcgetattr_else = None

            assert after in (termios.TCSADRAIN, termios.TCSAFLUSH), (after,)
            when = after
            termios.tcsetattr(fd, when, tcgetattr)

        return None

        # CSI 02/00 07/01  # 4 Skid Cursor  # 6 Bar Cursor  # No-Style Cursor
        # CSI 06/08 Set Mode (SM)  # 4 Insertion Replacement Mode (IRM)
        # CSI 06/12 Reset Mode (RM)  # 4 Insertion Replacement Mode (IRM)

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

            if read_1 in (b"O", b"["):
                while True:  # todo: what ends an Esc [ or Esc O Sequence?
                    read_2 = self.read_kchar_bytes_if()
                    kchord_bytes += read_2

                    if len(read_2) == 1:
                        ord_2 = read_2[-1]
                        if 0x20 <= ord_2 < 0x40:
                            continue

                    break

                    # "\x1B" "O" Sequences often then stop short, 3 Bytes in total

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

        stdio = self.stdio
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

        if False:  # jitter 3/Aug
            os.write(fd, b"??")

        stdio.flush()

        self.kbyteslogger.logfile.flush()  # plus ~0.050 ms, ugh
        self.sbyteslogger.logfile.flush()  # plus another ~0.050 ms, ugh

        kbytes = os.read(fd, 1)  # 1 or more Bytes, begun as 1 Byte
        kbyteslogger.log_bytes_io(kbytes)  # logs In after Read

        if kbytes != b"\x03":  # ⌃C
            self.kinterrupts = 0
        else:
            self.kinterrupts += 1
            if self.kinterrupts >= 3:
                if False:  # jitter 3/Aug  # ⌃C prints Py Traceback
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


KCAP_SEP = " "  # 1 Space separates one KCHORD_STR from the next in a KCAP_STR

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
    "\x1B" "[" "1;2C": "⇧→",  # CSI 04/03 Cursor Forward (CUF) Y=1 X=2
    "\x1B" "[" "1;2D": "⇧←",  # CSI 04/04 Cursor Backward (CUB) Y=1 X=2
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
    "\x1B" "[" "C": "→",  # CSI 04/03 Cursor Forward (CUF)
    "\x1B" "[" "D": "←",  # CSI 04/04 Cursor Backward (CUB)
    "\x1B" "[" "F": "⇧Fn→",  # CSI 04/06 Cursor Preceding Line (CPL)
    "\x1B" "[" "H": "⇧Fn←",  # CSI 04/08 Cursor Position (CUP)
    "\x1B" "[" "Z": "⇧Tab",  # ⇤  # CSI 05/10 Cursor Backward Tabulation (CBT)
    "\x1B" "b": "⎋←",  # ⌥← ⎋B  # ⎋←  # Emacs M-b Backword-Word
    "\x1B" "f": "⎋→",  # ⌥→ ⎋F  # ⎋→  # Emacs M-f Forward-Word
    "\x20": "Spacebar",  # ' ' ␠ ␣ ␢
    "\x7F": "Delete",  # ␡ ⌫ ⌦
    "\xA0": "⌥Spacebar",  # '\N{No-Break Space}'
}

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

    bt: BytesTerminal  # wrapped by us, here

    def __init__(self, bt) -> None:
        self.bt = bt

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

        assert KCAP_SEP == " "
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

        elif (o < 0x20) or (o == 0x7F):
            s = "⌃" + chr(o ^ 0x40)  # '⌃@'
        elif "A" <= ch <= "Z":
            s = "⇧" + chr(o)  # '⇧A'
        elif "a" <= ch <= "z":
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


@dataclasses.dataclass
class LineTerminal:
    """React to Sequences of Key Chords by laying Chars of Lines over the Screen"""

    st: StrTerminal  # wrapped by us here

    olines: list[str]  # the Lines to sketch

    kstr_holds: list[str]  # list("")  # list("-45")  # list("⎋", "[")
    kbytes: bytes  # the Bytes of the last Keyboard Chord
    kcap_str: str  # the Str of the KeyCap Words of the last Keyboard Chord

    kmap: str  # ''  # 'Emacs'  # 'Vi'
    vmodes: list[str]  # ''  # 'Insert'  # 'Replace'

    def __init__(self) -> None:

        bt = BytesTerminal()
        st = StrTerminal(bt)

        self.st = st

        self.olines = list()

        self.kstr_holds = list()
        self.kbytes = b""
        self.kcap_str = ""

        self.kmap = ""
        self.vmodes = [""]

        # lots of empty happens only until first Keyboard Input

    def vmode_enter(self, vmode) -> None:
        """Take Input as Insert Text or Replace Text, till Exit"""

        vmodes = self.vmodes

        assert vmode in ("", "Insert", "Replace"), vmode
        vmodes.append(vmode)

        self.vmode_stwrite(vmode)

    def vmode_stwrite(self, vmode) -> None:
        """Redefine Write as Insert or Replace, and choose a Cursor Style"""

        st = self.st

        assert vmode in ("", "Insert", "Replace"), vmode
        if KCDEBUG:
            st.stprint(f"{vmode=}  # vmode_stwrite")

        if not vmode:
            st.stwrite("\x1B" "[" "4l")  # CSI 06/12 Replace
            st.stwrite("\x1B" "[" " q")  # CSI 02/00 07/01  # No-Style Cursor
        elif vmode in "Insert":
            st.stwrite("\x1B" "[" "4h")  # CSI 06/08 Insert
            st.stwrite("\x1B" "[" "6 q")  # CSI 02/00 07/01  # 6 Bar Cursor
        else:
            assert vmode == "Replace", (vmode,)
            st.stwrite("\x1B" "[" "4l")  # CSI 06/12 Replace
            st.stwrite("\x1B" "[" "4 q")  # CSI 02/00 07/01  # 4 Skid Cursor

        # CSI 06/08 Set Mode (SM)  # 4 Insertion Replacement Mode (IRM)
        # CSI 06/12 Reset Mode (RM)  # 4 Insertion Replacement Mode (IRM)

        # CSI 02/00 07/01  # 4 Skid Cursor  # 6 Bar Cursor  # No-Style Cursor

    def vmode_exit(self) -> None:
        """Undo 'def vmode_enter'"""

        vmodes = self.vmodes

        vmodes.pop()
        vmode = vmodes[-1]

        self.vmode_stwrite(vmode)

    def texts_wrangle(self) -> None:
        """Take Input as Insert Text or Replace Text, till ⌃C or ⎋"""

        st = self.st

        vmode = self.vmodes[-1]
        assert vmode, (vmode,)

        while True:
            self.screen_print()

            if self.kstr_holds:
                self.verb_read(vmode="")  # Texts_Wrangle KStr_Holds
                self.verb_eval(vmode="")  # Texts_Wrangle KStr_Holds
                continue

            self.verb_read(vmode=vmode)  # Texts_Wrangle Replace/ Insert

            kbytes = self.kbytes
            kchars = kbytes.decode()  # may raise UnicodeDecodeError
            kcap_str = self.kcap_str

            if kcap_str in ("⌃C", "⎋"):
                break

            unprintable_keys = ["⌥[", "⎋["]
            if kcap_str in unprintable_keys:
                self.verb_eval(vmode="")  # Texts_Wrangle Unprintable-Keys
            elif kchars.isprintable():
                st.stwrite(kchars)
            else:
                self.verb_eval(vmode="")  # Texts_Wrangle Replace/ Insert

        # assert False  # jitter 4/Aug

    def verbs_wrangle(self, ilines, kmap) -> list[str]:
        """Launch, and run till SystemExit"""

        olines = self.olines
        olines.extend(ilines)

        self.kmap = kmap

        # Wrap around a StrTerminal wrapped around a ByteTerminal

        klog_exists = self.st.bt.kbyteslogger.exists
        slog_exists = self.st.bt.sbyteslogger.exists

        with BytesTerminal() as bt:
            st = StrTerminal(bt)
            self.st = st

            # Tell the StrTerminal what to say at first

            olines = self.olines
            for oline in olines:
                st.stprint(oline)

            if (not klog_exists) or (not slog_exists):
                st.stprint()
                if not klog_exists:
                    st.stprint(
                        "Logging Keyboard Chord Bytes into:  cat",
                        bt.kbyteslogger.logfile.name,
                    )
                if not slog_exists:
                    st.stprint(
                        "Logging Screen Bytes into:  cat", bt.sbyteslogger.logfile.name
                    )

            self.help_quit()

            # Read & Eval & Print in a loop till SystemExit

            vmode = self.vmodes[-1]
            assert not vmode, (vmode,)

            while True:
                try:
                    self.screen_print()
                    self.verb_read(vmode="")  # Verbs_Wrangle
                    self.verb_eval(vmode="")  # Verbs_Wrangle
                except SystemExit as exc:
                    if exc.code:
                        raise

                    olines.clear()

                    return olines

    def screen_print(self) -> None:
        """Speak after taking Keyboard Chord Sequences as Commands or Text"""

        pass  # todo: do more inside 'def screen_print'

    def verb_read(self, vmode) -> None:
        """Read one Keyboard Chord Sequence from the Keyboard, as Bytes and as Str"""

        verbs = list(FUNC_BY_KCAP_STR.keys())
        deffed_kcap_strs = list(verbs)  # copied better than aliased

        st = self.st

        # Read one Keyboard Chord, and then zero or more to say which Verb to run

        (kbytes, kcap_str) = st.read_one_kchord_bytes_str()

        sep = " "  # '⇧Tab'  # '⇧T a b'  # '⎋⇧Fn X'  # '⎋⇧FnX'
        if not vmode:
            while any(_.startswith(kcap_str + " ") for _ in deffed_kcap_strs):
                (kchord_bytes, kchord_str) = st.read_one_kchord_bytes_str()

                kbytes += kchord_bytes
                kcap_str += sep + kchord_str

                # 1 'D' is a complete Sequence, because 2 'D ' doesn't start 6 'Delete'

        # Succeed

        if KCDEBUG:
            st.stprint(f"{kbytes=} {kcap_str=}  # verb_read")

        self.kbytes = kbytes
        self.kcap_str = kcap_str

        # '⌃L'  # '⇧Z ⇧Z'

    def verb_eval(self, vmode) -> None:
        """Take 1 Keyboard Chord Sequence as a Command to execute"""

        st = self.st

        kstr_holds = self.kstr_holds
        kcap_str = self.kcap_str

        # Take the Str of 1 Keyboard Chord Sequence as a call of 1 Python Def

        kstr_holds_before = list(kstr_holds)

        func = LineTerminal.kdo_text_write_n
        if (not vmode) or (not kcap_str.isprintable()):
            if kcap_str in FUNC_BY_KCAP_STR.keys():
                func = FUNC_BY_KCAP_STR[kcap_str]

        assert func.__name__.startswith("kdo_"), (func.__name__, kcap_str)

        if KDEBUG:
            if func is not LineTerminal.kdo_force_quit:
                self.kstr_holds.clear()
                return

        if KCDEBUG:
            st.stprint(f"func={func.__name__} {kstr_holds=}  # verb_eval")
            sys.stderr.flush()

        func(self)  # always one of 'def kdo_'...

        if kstr_holds == kstr_holds_before:
            self.kstr_holds.clear()  # for when Func is not .kdo_hold_kstr, etc

    def kdo_text_write_n(self) -> None:
        """Take the Str of 1 Keyboard Chord Sequence as Chars to write to Screen"""

        st = self.st
        kcap_str = self.kcap_str

        kint = self.pull_kint(default=1)
        if not kint:
            return  # without alarm
        if kint < 0:
            self.alarm_ring()
            return

        st.stwrite(kint * kcap_str)  # distinct printable echo better than beep

        # Return, Spacebar, Tab, and printable US-Ascii or Unicode

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

        st.stwrite(schars)

    #
    # Quit & Quote & Repeat
    #

    def kdo_force_quit(self) -> None:
        """Revert changes to the O Lines, and quit this Linux Process"""

        _ = self.pull_kint(default=0)  # todo: 'returncode = ' here

        sys.exit()  # ignore the K Int

        # Emacs ⌃X ⌃S ⌃X ⌃C save-buffer save-buffers-kill-terminal

        # Vim ⌃L ⌃C : Q ! Return quit-no-save
        # Vim ⇧Z ⇧Q quit-no-save
        # Vim ⇧Z ⇧Z save-quit

    def kdo_quote_kchars(self) -> None:
        """Block till the next K Chord, but then take it as Text, not as Command"""

        st = self.st

        kint = self.pull_kint(default=1)
        if kint < 0:
            self.alarm_ring()
            return

        (kbytes, kchord_str) = st.read_one_kchord_bytes_str()

        kchars = kbytes.decode()  # may raise UnicodeEncodeError
        st.stwrite(kint * kchars)  # b'\x1B'  # b'['  # b'A'

        # Emacs ⌃Q quoted-insert/ replace
        # Vi ⌃V

    def kdo_quote_csi_kstrs_n(self) -> None:
        """Block till CSI Sequence complete, then take it as Text"""

        st = self.st
        kcap_str_holds = self.kstr_holds
        kcap_str = self.kcap_str
        # no .pull_int here

        # Run as [ only after ⎋, else reject the .kcap_str [ as if entirely unbound

        if kcap_str == "[":
            if (not kcap_str_holds) or (kcap_str_holds[-1] != "⎋"):
                self.kdo_text_write_n()
                return

        # Block till CSI Sequence complete

        kbytes = b"\x1B" b"["
        kcap_str = "⎋ ["

        while True:  # todo: what ends an Esc [ or Esc O Sequence?
            (kchord_bytes, kchord_str) = st.read_one_kchord_bytes_str()

            kbytes += kchord_bytes

            sep = " "  # '⇧Tab'  # '⇧T a b'  # '⎋⇧Fn X'  # '⎋⇧FnX'
            kcap_str += sep + kchord_str

            if KDEBUG or KCDEBUG:
                st.stprint(f"{kbytes=} {kcap_str=}  # kdo_quote_csi_kstrs_n")

            read_2 = kchord_bytes
            if len(read_2) == 1:
                ord_2 = read_2[-1]
                if 0x20 <= ord_2 < 0x40:
                    continue

            break

        self.kbytes = kbytes
        self.kcap_str = kcap_str

        # Write as if via 'self.kdo_text_write_n()'  # ⎋[m, ⎋[1m, ⎋[31m, ...

        kint = self.pull_kint(default=1)
        kchars = kbytes.decode()  # may raise UnicodeDecodeError
        st.stwrite(kint * kchars)

        # Pq [ quote.csi.kstrs
        # missing from Emacs, Vi, VsCode
        # unlike Vi [ Key Map

    def kdo_kminus(self) -> None:
        """Jump back by one or more Lines, but land past the Dent"""

        kstr_holds = self.kstr_holds
        # no .pull_int here

        if kstr_holds and (kstr_holds == ["⌃U"]):

            if kstr_holds == ["⌃U", "-"]:
                self.kstr_holds = ["⌃U"]
                return

            self.kdo_hold_kstr()  # kdo_ calls kdo_
            return

        self.kdo_dent_minus_n()  # kdo_ calls kdo_  # K Int live

        # Emacs ⌃U - universal-argument negative

    def kdo_kzero(self) -> None:
        """Hold another Digit, else jump to First Column"""

        kstr_holds = self.kstr_holds
        # no .pull_int here

        # Help quit Vi, or just drop some Extras out of the Key-Cap Str Holds

        self.help_quit_if()

        # Hold 0 as another Digit, if after 1 2 3 4 5 6 7 8 9, or if after Emacs ⌃U

        if kstr_holds and (kstr_holds[0] in "0123456789"):  # never '0' here
            self.kdo_hold_kstr()  # kdo_ calls kdo_
            return

        if kstr_holds and (kstr_holds[0] == "⌃U"):
            self.kdo_hold_kstr()  # kdo_ calls kdo_
            return

        # Else jump to First Column

        self.kdo_column_1()  # kdo_ calls kdo_

        # Emacs ⌃U 0 digit
        # Vi 0 after 1 2 3 4 5 6 7 8 9
        # Vi 0 otherwise

    def kdo_hold_kstr(self) -> None:
        """Hold Key-Cap Str's till Line-Terminal Key-Cap Sequence complete"""

        kstr_holds = self.kstr_holds
        kcap_str = self.kcap_str

        # Help quit Vi, or just drop some Extras out of the Key-Cap Str Holds

        self.help_quit_if()

        # Hold this Key-Cap for now

        kstr_holds.append(kcap_str)

        # Emacs '-', and Emacs 0 1 1 2 3 4 5 6 7 8 9, after Emacs ⌃U
        # Pq Em/Vi Csi Sequences:  ⎋[m, ⎋[1m, ⎋[31m, ...
        # Vi 1 2 3 4 5 6 7 8 9, and Vi 0 thereafter

    def help_quit_if(self) -> None:
        """Help quit Vi, or just drop some Extras out of the Key-Cap Str Holds"""

        kstr_holds = self.kstr_holds
        kcap_str = self.kcap_str

        assert DONT_QUIT_KCAP_STRS == ("⌃C", "⌃D", "⌃G", "⎋", "⌃\\")
        dont_quit_kcap_strs = DONT_QUIT_KCAP_STRS

        for quitting_kcap_str in dont_quit_kcap_strs:
            if kstr_holds[-1:] == [quitting_kcap_str]:
                kstr_holds.clear()

                if kcap_str == quitting_kcap_str:
                    self.help_quit()
                    return

    def kdo_help_quit(self) -> None:

        self.help_quit()  # no .pull_kint here

    def help_quit(self) -> None:
        """Say how to quit Vi"""

        st = self.st
        # no .pull_int here

        quit_kcap_strs = list()
        for kcap_str, func in FUNC_BY_KCAP_STR.items():
            if func is LineTerminal.kdo_force_quit:
                quit_kcap_strs.append(kcap_str)

        st.stprint()

        quits = " or ".join("".join(_.split()) for _ in quit_kcap_strs)
        st.stprint(f"Press {quits} to quit")

        # 'Press ⌃L⌃C:Q!Return or ⌃X⌃C or ⌃X⌃S⌃X⌃C or ⇧Z⇧Q or ⇧Z⇧Z to quit'
        # todo: many Emacs don't bind '⌃C R' to (revert-buffer 'ignoreAuto 'noConfirm)
        # todo: and Emacs still freaks if you delete the ⌃X⌃S File before calling ⌃X⌃S

        # Emacs/ Vi famously leave how-to-quit too often unmentioned

    def push_kint(self, kint) -> None:
        """Fill the cleared Key-Cap Str Holds, as if Emacs ⌃U ..."""

        kstr_holds = self.kstr_holds
        assert not kstr_holds, (kstr_holds,)

        kstr_holds.extend(["⌃U"] + list(str(kint)))

    def pull_kint(self, default) -> int:
        """Fetch & clear the Key-Cap Str Holds"""

        kstr_holds = self.kstr_holds

        # Drop some Extras out of the Key-Cap Str Holds

        assert DONT_QUIT_KCAP_STRS == ("⌃C", "⌃D", "⌃G", "⎋", "⌃\\")
        dont_quit_kcap_strs = DONT_QUIT_KCAP_STRS

        for quitting_kcap_str in dont_quit_kcap_strs:
            if kstr_holds[-1:] == [quitting_kcap_str]:
                kstr_holds.clear()

        # Make sense of Emacs corners of ⌃U ⌃U, ⌃U - -, ⌃U without digits

        if kstr_holds and (kstr_holds[0] == "⌃U"):
            kstr_holds.pop(0)
            if kstr_holds == ["-"]:  # todo: Emacs says ⌃U !- = ⌃U 0 ?
                kstr_holds.pop(0)
            if not kstr_holds:  # todo: Emacs says ⌃U != ⌃U 0 ?
                kstr_holds.append("0")
                assert kstr_holds == ["0"], (kstr_holds,)

        # Take Int Literal, else Default

        kint = default
        if kstr_holds:
            kint = int("".join(kstr_holds))  # may raise ValueError
            kstr_holds.clear()

        # Succeed

        return kint  # positive kint for the Vi .kmap

        # raises ValueError if ever '.kstr_holds' not an Int Literal

    #
    # Move the Screen Cursor to a Column, relatively or absolutely
    #

    def kdo_char_minus_n(self) -> None:
        """Step back by one or more Chars"""

        self.kdo_column_minus_n()  # Classic Vi wraps left

        # Emacs ← left-char
        # Vi Delete
        # Vi ^H

    def kdo_char_plus_n(self) -> None:
        """Step ahead by one or more Chars"""

        self.kdo_column_plus_n()  # Classic Vi wraps right

        # Emacs → right-char
        # Vi Spacebar

    def kdo_column_0n(self) -> None:
        """Jump to a zero-based numbered Column for Pedantic Emacs"""

        #

        kint = self.pull_kint(default=0)
        if kint < 0:  # todo: negative Column Numbers for Emacs
            self.alarm_ring()
            return

        kint_plus = kint + 1

        #

        self.write_form_kint("\x1B[{}G", kint=kint_plus)

        # CSI 04/07 Cursor Character Absolute (CHA)
        # "\r" (aka "\0x0D") and "\x1B[G" and "\x1B[1G" all go to Column 1

        # Emacs ⎋ G Tab move-to-column

    def kdo_column_1(self) -> None:
        """Jump to Left of Line"""

        st = self.st
        st.stwrite("\r")  # 00/13  # "\x0D"  # "\x1B[G"  # "\x1B[1G"

        # 00/13 Carriage Return (CR) \r ⌃M
        # CSI 04/07 Cursor Character Absolute (CHA)
        # "\r" (aka "\0x0D") and "\x1B[G" and "\x1B[1G" all go to Column 1

        # part of Vi 0
        # much like Vi ^ kdo_column_dent_beyond

    def kdo_column_minus_n(self) -> None:
        """Jump back by one or more Columns"""

        #

        kint = self.pull_kint(default=1)

        if not kint:
            return

        if kint < 0:
            self.push_kint(-kint)
            self.kdo_column_plus_n()
            return

        #

        self.write_form_kint("\x1B[{}D", kint=kint)

        # 00/08 Backspace (BS) \b ⌃H
        # 07/15 Delete (DEL) \x7F ⌃? 'Eliminated Control Function'

        # CSI 04/04 Cursor Backward (CUB)

        # Vi ←
        # Vi H

    def kdo_column_dent_beyond(self) -> None:
        """Jump to the first Column beyond the Dent"""

        # no .pull_int here

        self.kdo_column_1()  # Classic Vi past Dent

        # Vi ^

    def kdo_column_n(self) -> None:
        """Jump to a numbered Column"""

        #

        kint = self.pull_kint(default=1)
        if not kint:  # todo: zero Column Numbers for Vi  # middle?
            self.alarm_ring()
            return
        if kint < 0:  # todo: negative Column Numbers for Vi
            self.alarm_ring()
            return

        #

        self.write_form_kint("\x1B[{}G", kint=kint)

        # CSI 04/07 Cursor Character Absolute (CHA)
        # "\r" (aka "\0x0D") and "\x1B[G" and "\x1B[1G" all go to Column 1

        # Vi |
        # VsCode ⌃G {line}:{column}

    def kdo_column_plus_n(self) -> None:
        """Jump ahead by one or more Columns"""

        #

        kint = self.pull_kint(default=1)

        if not kint:
            return

        if kint < 0:
            self.push_kint(-kint)
            self.kdo_column_minus_n()
            return

        #

        self.write_form_kint("\x1B[{}C", kint=kint)

        # CSI 04/03 Cursor Forward (CUF)

        # Vi →
        # Vi L

    def kdo_tab_minus_n(self) -> None:
        """Jump back by one or more Column Tabs"""

        #

        kint = self.pull_kint(default=1)

        if not kint:
            return

        if kint < 0:
            self.push_kint(-kint)
            self.kdo_tab_plus_n()
            return

        #

        kint_8x = 8 * kint
        self.write_form_kint("\x1B[{}D", kint=kint_8x)

        # CSI 05/10 Cursor Backward Tabulation (CBT)
        # CSI 04/04 Cursor Backward (CUB)

        # Pq ⇧Tab tab.minus.n
        # missing from Emacs, Vi, VsCode

    def kdo_tab_plus_n(self) -> None:
        """Jump ahead by one or more Column Tabs"""

        st = self.st

        #

        kint = self.pull_kint(default=1)

        if not kint:
            return

        if kint < 0:
            self.push_kint(-kint)
            self.kdo_tab_minus_n()
            return

        #

        st.stwrite(kint * "\t")  # 00/08

        # 00/08 Character Tabulation (HT)  # \t Tab

        # Pq Tab tab.plus.n
        # missing from Emacs, Vi, VsCode

    #
    # Move the Screen Cursor to a Row, relatively or absolutely
    #

    def kdo_dent_line_n(self) -> None:
        """Jump to a numbered Line, but land past the Dent"""

        st = self.st

        #

        kint = self.pull_kint(default=32100)  # todo: more Rows on Screen
        if not kint:  # todo: zero Line Numbers
            self.alarm_ring()
            return
        if kint < 0:  # todo: negative Line Numbers
            self.alarm_ring()
            return

        #

        self.write_form_kint("\x1B[{}d", kint=kint)

        st.stwrite("\r")  # 00/13  # "\x1B[G"  # "\x1B[1G"  # Classic Vi past Dent

        # CSI 06/04 Line Position Absolute (VPA)

        # 00/13 Carriage Return (CR) \r ⌃M
        # CSI 04/07 Cursor Character Absolute (CHA)
        # "\r" (aka "\0x0D") and "\x1B[G" and "\x1B[1G" all go to Column 1

        # Vi G

    def kdo_dent_minus_n(self) -> None:
        """Jump back by one or more Lines, but land past the Dent"""

        self.kdo_line_minus_n()  # Classic Vi past Dent
        self.kdo_column_1()  # Classic Vi past Dent

        # Vi -

    def kdo_dent_plus_n(self) -> None:
        """Jump ahead by one or more Lines, but land past the Dent"""

        self.kdo_line_plus_n()  # Classic Vi past Dent
        self.kdo_column_1()  # Classic Vi past Dent

        # Vi +

    def kdo_dent_plus_n1(self) -> None:
        """Jump ahead by zero or more Lines, but land past the Dent"""

        #

        kint = self.pull_kint(default=1)

        if not kint:  # todo: zero Vi _
            self.alarm_ring()
            return
        if kint < 0:  # todo: negative Vi _ could be Vi -
            self.alarm_ring()
            return

        #

        if kint > 1:
            kint_minus = kint - 1
            self.write_form_kint("\x1B[{}B", kint=kint_minus)

        self.kdo_column_1()  # Classic Vi past Dent

        # CSI 04/02 Cursor Down (CUD)

        # Vi _

    def kdo_end_plus_n1(self) -> None:
        """Jump ahead by zero or more Lines, and land at End of Line"""

        #

        kint = self.pull_kint(default=1)

        if not kint:  # todo: zero Vi $
            self.alarm_ring()
            return
        if kint < 0:  # todo: negative Vi $ could be Vi ⌃E
            self.alarm_ring()
            return

        #

        if kint > 1:
            kint_minus = kint - 1
            self.write_form_kint("\x1B[{}B", kint=kint_minus)

        self.write_form_kint("\x1B[{}C", kint=32100)  # todo: more Columns on Screen

        # CSI 04/02 Cursor Down (CUD)
        # CSI 04/03 Cursor Forward (CUF)

        # Emacs ⌃E move-end-of-line
        # Vi $

    def kdo_dent_n(self) -> None:
        """Jump to a numbered Line, but land past the Dent"""

        st = self.st

        #

        kint = self.pull_kint(default=32100)  # todo: more Rows on Screen

        if not kint:  # todo: zero Row Number  # middle?
            self.alarm_ring()
            return
        if kint < 0:  # todo: negative Row Numbers
            self.alarm_ring()
            return

        #

        self.write_form_kint("\x1B[{}d", kint=kint)  # Classic Vi past Dent
        st.stwrite("\r")  # 00/13  # "\x1B[G"  # "\x1B[1G"

        # CSI 06/04 Line Position Absolute (VPA)

        # 00/13 Carriage Return (CR) \r ⌃M
        # CSI 04/07 Cursor Character Absolute (CHA)
        # "\r" (aka "\0x0D") and "\x1B[G" and "\x1B[1G" all go to Column 1

        # Emacs ⎋G G goto-line
        # Emacs ⎋G ⎋G goto-line

    def kdo_home_plus_n1(self) -> None:
        """Jump ahead by zero or more Lines, and land at Left of Line"""

        #

        kint = self.pull_kint(default=1)

        if not kint:  # todo: zero Emacs ⌃A
            self.alarm_ring()
            return
        if kint < 0:  # todo: negative Emacs ⌃A
            self.alarm_ring()
            return

        #

        if kint > 1:
            kint_minus = kint - 1
            self.write_form_kint("\x1B[{}B", kint=kint_minus)

        self.kdo_column_1()  # kdo_ calls kdo_

        # CSI 04/02 Cursor Down (CUD)

        # Emacs ⌃A move-beginning-of-line

    def kdo_line_minus_n(self) -> None:
        """Jump back by one or more Lines"""

        #

        kint = self.pull_kint(default=1)

        if not kint:
            return

        if kint < 0:
            self.push_kint(-kint)
            self.kdo_line_plus_n()
            return

        #

        self.write_form_kint("\x1B[{}A", kint=kint)

        # CSI 04/01 Cursor Up (CUU)

        # Emacs ⌃P previous-line
        # Vi K

    def kdo_line_plus_n(self) -> None:
        """Jump ahead by one or more Lines"""

        #

        kint = self.pull_kint(default=1)

        if not kint:
            return

        if kint < 0:
            self.push_kint(-kint)
            self.kdo_line_minus_n()
            return

        #

        self.write_form_kint("\x1B[{}B", kint=kint)

        # CSI 04/02 Cursor Down (CUD)

        # Emacs ⌃N next-line
        # Vi ⌃J
        # Vi J

    def kdo_row_n_down(self) -> None:
        """Jump to Top of Screen, but ahead by zero or more Lines"""

        #

        kint = self.pull_kint(default=1)

        if not kint:  # todo: zero Emacs ⎋ R
            self.alarm_ring()
            return
        if kint < 0:  # todo: negative Emacs ⎋ R
            self.alarm_ring()
            return

        #

        self.write_form_kint("\x1B[{}d", kint=1)
        if kint > 1:
            kint_minus = kint - 1
            self.write_form_kint("\x1B[{}B", kint=kint_minus)

        # CSI 06/04 Line Position Absolute (VPA)
        # CSI 04/02 Cursor Down (CUD)

        # Emacs ⎋ R move-to-window-line-top-bottom, with Zero-Based Positive K-Int
        # Vi ⇧H

    def kdo_row_n_up(self) -> None:
        """Jump to Bottom of Screen, but back behind by zero or more Lines"""

        #

        kint = self.pull_kint(default=1)

        if not kint:  # todo: zero Emacs ⎋ R
            self.alarm_ring()
            return
        if kint < 0:  # todo: negative Emacs ⎋ R
            self.alarm_ring()
            return

        #

        self.write_form_kint("\x1B[{}d", kint=32100)  # todo: more Rows on Screen
        if kint > 1:
            kint_minus = kint - 1
            self.write_form_kint("\x1B[{}A", kint=kint_minus)

        # CSI 06/04 Line Position Absolute (VPA)
        # CSI 04/01 Cursor Up (CUU)

        # Emacs ⎋ R move-to-window-line-top-bottom, with Negative K-Int
        # Vi ⇧L

    #
    # Dedent or Dent the Lines at and below the Screen Cursor
    #

    def kdo_lines_dedent_n(self) -> None:
        """Remove Blank Space from the Left of one or more Lines"""

        st = self.st

        #

        kint = self.pull_kint(default=1)

        if not kint:
            return

        if kint < 0:
            self.push_kint(-kint)
            self.kdo_lines_dent_n()
            return

        #

        self.verb_read("")  # after "<"
        kcap_str = self.kcap_str
        if kcap_str != "<":
            self.alarm_ring()
            return

        #

        st.stwrite("\r")  # 00/13  # "\x1B[G"  # "\x1B[1G"

        for i in range(kint):
            st.stwrite("\x1B" "[" "4" "P")  # CSI 05/00
            if i < (kint - 1):
                # st.stwrite("\x1B" "[" "B")  # CSI 04/02
                st.stwrite("\n")  # 00/10  # "\x1B[E"  # "\x1B[1E"

        for i in range(kint - 1):
            st.stwrite("\x1B" "[" "A")  # CSI 04/01

        # CSI 05/00 Delete Character (DCH)

        # 00/10 Line Feed (LF) \n ^J
        # 00/13 Carriage Return (CR) \r ⌃M
        # ESC 04/05 Next Line (NEL)
        # CSI 04/02 Cursor Down (CUD)
        # CSI 04/05 Cursor Next Line (CNL)
        # "\r" (aka "\0x0D") and "\x1B[G" and "\x1B[1G" all go to Column 1

        # CSU 04/01 Cursor Up (CUU)

        # FIXME: << to land past Dent

    def kdo_lines_dent_n(self) -> None:
        """Insert 1 Dent of Blank Space into the Left of one or more Lines"""

        st = self.st

        #

        kint = self.pull_kint(default=1)

        if not kint:
            return

        if kint < 0:
            self.push_kint(-kint)
            self.kdo_lines_dedent_n()
            return

        #

        self.verb_read("")  # after ">"
        kcap_str = self.kcap_str
        if kcap_str != ">":
            self.alarm_ring()
            return

        #

        st.stwrite("\x1B" "[" "4h")  # CSI 06/08 Insert

        for i in range(kint):
            st.stwrite("\r")  # 00/13  # "\x1B[G"  # "\x1B[1G"
            st.stwrite(4 * " ")
            if i < (kint - 1):
                # st.stwrite("\x1B" "[" "B")  # CSI 04/02
                st.stwrite("\n")  # 00/10  # "\x1B[E"  # "\x1B[1E"

        for i in range(kint - 1):
            st.stwrite("\x1B" "[" "A")  # CSI 04/01

        st.stwrite("\r")  # 00/13  # "\x1B[G"  # "\x1B[1G"

        st.stwrite("\x1B" "[" "4l")  # CSI 06/12 Replace

        # FIXME: >> to land past Dent

        # CSI 06/08 Set Mode (SM)  # 4 Insertion Replacement Mode (IRM)
        # CSI 06/12 Reset Mode (RM)  # 4 Insertion Replacement Mode (IRM)

        # 00/10 Line Feed (LF) \n ^J
        # 00/13 Carriage Return (CR) \r ⌃M
        # ESC 04/05 Next Line (NEL)
        # CSI 04/02 Cursor Down (CUD)
        # CSI 04/05 Cursor Next Line (CNL)
        # "\r" (aka "\0x0D") and "\x1B[G" and "\x1B[1G" all go to Column 1

    #
    # Delete the Lines at and below the Screen Cursor
    #

    def kdo_dents_cut_n(self) -> None:
        """Cut N Lines here and below, and land past Dent"""

        st = self.st

        #

        kint = self.pull_kint(default=1)

        if not kint:
            return

        if kint < 0:  # todo: negative Emacs ⎋ R
            self.alarm_ring()
            return

        #

        self.verb_read("")  # after D
        kcap_str = self.kcap_str
        if kcap_str != "D":
            self.alarm_ring()
            return

        #

        st.stwrite("\r")  # 00/13  # "\x1B[G"  # "\x1B[1G"
        st.stwrite(("\x1B" "[" "{}" "M").format(kint))  # CSI 04/13

        # CSI 04/13 Delete Line (DL)

        # Vi D D

    #
    # Switch between Insert Mode, Replace Mode, and View Mode
    #

    def kdo_insert_n_till(self) -> None:
        """Insert Text Sequences till ⌃C, except for ⌃O and Control Sequences"""

        #

        kint = self.pull_kint(default=1)
        if kint != 1:  # todo: Vi I with Digits Args
            self.alarm_ring()
            return

        #

        self.vmode_enter("Insert")
        self.texts_wrangle()
        self.vmode_exit()

        # Vi I

    def kdo_replace_n_till(self) -> None:
        """Replace Text Sequences till ⌃C, except for ⌃O and Control Sequences"""

        #

        kint = self.pull_kint(default=1)
        if kint != 1:  # todo: Vi ⇧R with Digits Args
            self.alarm_ring()
            return

        #

        self.vmode_enter("Replace")
        self.texts_wrangle()
        self.vmode_exit()

        # Vi ⇧R

    #
    #
    #

    # Emacs Delete delete-backward-char


#
# presently:
#
#   Option Mouse click moves Cursor via ← ↑ → ↓
#
#   ⎋GG ⎋G⎋G ⎋[
#   ⌃A ⌃E ⌃H Tab ⇧Tab ⌃J ⌃N ⌃P ⌃Q ⌃U ⌃V Return ← ↑ → ↓
#   Spacebar $ + - 0 1 2 3 4 5 6 7 8 9 ⇧G ^ _ H J K L | Delete
#   << >> DD
#   I ⇧R ⌃C ⎋
#   ⌥GG ⌥G⌥G
#
#   ⎋ ⌃C ⌃D ⌃G ⌃\ ⇧QVIReturn
#   ⌃L⌃C:Q!Return ⌃X⌃C ⌃X⌃S⌃X⌃C ⇧Z⇧Q ⇧Z⇧Z
#

#
# todo:
#
#   ⌃K ⇧A C ⇧D ⇧I ⇧O ⇧R ⇧S ⇧X A C$ CC D$ DD I O R S X ⌃C ⎋
#   Emacs ⌃O vs Vim ⌃O ⌃I
#
#   ⌃H⌃A ⌃H⌃K
#   ^Z and ways to send ^C ^\ Assert-False
#
#   [ Vi ⌃B Vi ⌃F Scroller CSI Sequences ]
#   Emacs ⌃V ⌥V vs Vim ⌃V
#   [ < > C D to movement ⇧G etc ]
#   ⇧M
#
#   ⌃L [ of Shadow Screen, of File larger than Screen ]
#   Emacs ⌃T
#   Emacs ⌃W ⌃Y
#
#   Emacs ⌃R ⌃S
#

DONT_QUIT_KCAP_STRS = ("⌃C", "⌃D", "⌃G", "⎋", "⌃\\")  # ..., b'\x1B, b'\x1C'

FUNC_BY_KCAP_STR = {
    "⎋": LineTerminal.kdo_hold_kstr,
    "⎋⎋": LineTerminal.kdo_help_quit,  # Meta Esc
    "⎋G G": LineTerminal.kdo_dent_n,
    "⎋G ⎋G": LineTerminal.kdo_dent_n,
    "⎋G Tab": LineTerminal.kdo_column_0n,
    # "⎋ R": LineTerminal.kdo_row_middle_up_down,
    "⎋[": LineTerminal.kdo_quote_csi_kstrs_n,  # b'\x1B\x5B'  # Option [
    #
    "⌃A": LineTerminal.kdo_home_plus_n1,  # b'\x01'
    "⌃C": LineTerminal.kdo_hold_kstr,  # b'\x03'
    "⌃D": LineTerminal.kdo_hold_kstr,  # b'\x04'
    "⌃E": LineTerminal.kdo_end_plus_n1,  # b'\x05'
    "Tab": LineTerminal.kdo_tab_plus_n,  # b'\x09'  # b'\t'
    "⌃J": LineTerminal.kdo_line_plus_n,  # b'\x0A'  # b'\n'
    "⌃L ⌃C : Q ! Return": LineTerminal.kdo_force_quit,  # b'\x0C...
    "Return": LineTerminal.kdo_dent_plus_n,  # b'\x0D'  # b'\r'
    "⌃N": LineTerminal.kdo_line_plus_n,  # b'\x0E'
    "⌃P": LineTerminal.kdo_line_minus_n,  # b'\x10'
    "⌃Q": LineTerminal.kdo_quote_kchars,  # b'\x11'
    "⌃U": LineTerminal.kdo_hold_kstr,  # b'\x15'
    "⌃V": LineTerminal.kdo_quote_kchars,  # b'\x16'
    "⌃X ⌃C": LineTerminal.kdo_force_quit,  # b'\x18...
    "⌃X ⌃S ⌃X ⌃C": LineTerminal.kdo_force_quit,  # b'\x18...
    # "⌃X 8 Return": LineTerminal.unicodedata_lookup,  # Emacs insert-char
    "↑": LineTerminal.kdo_line_minus_n,  # b'\x1B[A'
    "↓": LineTerminal.kdo_line_plus_n,  # b'\x1B[B'
    "→": LineTerminal.kdo_column_plus_n,  # b'\x1B[C'
    "←": LineTerminal.kdo_column_minus_n,  # b'\x1B[D'
    "⇧Tab": LineTerminal.kdo_tab_minus_n,  # b'\x1B[Z'
    "⌃\\": LineTerminal.kdo_hold_kstr,  # ⌃\  # b'\x1C'
    #
    "Spacebar": LineTerminal.kdo_char_plus_n,  # b'\x20'
    "$": LineTerminal.kdo_end_plus_n1,  # b'\x24'
    "+": LineTerminal.kdo_dent_plus_n,  # b'\x2B'
    "-": LineTerminal.kdo_kminus,  # b'\x2D'
    "0": LineTerminal.kdo_kzero,  # b'0'
    "1": LineTerminal.kdo_hold_kstr,
    "2": LineTerminal.kdo_hold_kstr,
    "3": LineTerminal.kdo_hold_kstr,
    "4": LineTerminal.kdo_hold_kstr,
    "5": LineTerminal.kdo_hold_kstr,
    "6": LineTerminal.kdo_hold_kstr,
    "7": LineTerminal.kdo_hold_kstr,
    "8": LineTerminal.kdo_hold_kstr,
    "9": LineTerminal.kdo_hold_kstr,
    "<": LineTerminal.kdo_lines_dedent_n,
    ">": LineTerminal.kdo_lines_dent_n,
    #
    "⇧G": LineTerminal.kdo_dent_line_n,  # b'G'
    "⇧H": LineTerminal.kdo_row_n_down,  # b'H'
    "⇧L": LineTerminal.kdo_row_n_up,  # b'L'
    "⇧Q V I Return": LineTerminal.kdo_help_quit,  # b'Qvi\r'
    "⇧R": LineTerminal.kdo_replace_n_till,  # b'R'
    "⇧Z ⇧Q": LineTerminal.kdo_force_quit,  # b'ZQ'
    "⇧Z ⇧Z": LineTerminal.kdo_force_quit,  # b'ZZ'
    "[": LineTerminal.kdo_quote_csi_kstrs_n,  # b'\x5B'
    "^": LineTerminal.kdo_column_dent_beyond,  # b'\x5E'
    "_": LineTerminal.kdo_dent_plus_n1,  # b'\x5F'
    #
    "D": LineTerminal.kdo_dents_cut_n,  # b'd'
    "H": LineTerminal.kdo_column_minus_n,  # b'h'
    "I": LineTerminal.kdo_insert_n_till,  # b'i'
    "J": LineTerminal.kdo_line_plus_n,  # b'j'
    "K": LineTerminal.kdo_line_minus_n,  # b'k'
    "L": LineTerminal.kdo_column_plus_n,  # b'l'
    "|": LineTerminal.kdo_column_n,  # b'\x7C'
    "Delete": LineTerminal.kdo_char_minus_n,  # b'\x7F'
    #
    "⌥⎋": LineTerminal.kdo_help_quit,  # Option Esc
    "⌥G G": LineTerminal.kdo_dent_n,
    "⌥G ⌥G": LineTerminal.kdo_dent_n,
    "⌥G Tab": LineTerminal.kdo_column_0n,
    # "⌥ R": LineTerminal.kdo_row_middle_up_down,
    "⌥[": LineTerminal.kdo_quote_csi_kstrs_n,  # b'\xE2\x80\x9C'  # Option [
}

# hand-sorted by ⎋ ⌃ ⌥ ⇧ ⌘ Fn order

# todo: Emacs ⌃U - for non-positive K-Int

# todo: assert Keys of FUNC_BY_KCAP_STR reachable by StrTerminal
#   such as ⎋' isn't reachable while '⎋ G Tab' defined
#       because 'deffed_kcap_strs'


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
