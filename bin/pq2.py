#!/usr/bin/env python3

r"""
usage: pq [VERB ...]

tell Python to edit the Os Copy/Paste Clipboard Buffer, else other Stdin/ Stdout

positional arguments:
  VERB        verb of the Pq Programming Language:  dedent, dent, join, len, max, ...

options:
  -h, --help  show this help message and exit

quirks:
  takes Names of Python Funcs and Types as the Words of a Pq Programming Language
  defaults like Awk to 'bytes decode splitlines Iterable', unless you say different
  ducks the Shift key and Quotes by taking '.' for '(' or ',', taking '_' for ' ', etc
  replaces:  awk, cut, head, grep, sed, sort, tail, tr, uniq, wc -l, xargs, xargs -n 1
  copied from:  git clone https://github.com/pelavarre/byoverbs.git

examples easier to spell out with Python than with Sh:
  pq dent  # adds four Spaces to left of each Line  # |sed 's,^,    ,'
  pq help  # shows more examples, specs more quirks
  pq len  # counts Chars per Line  # |jq --raw-input length
  pq list join replace._  # tr -d ' \n'
  pq list set  # drops Duplicate Lines but doesn't reorder Lines  # unique_everseen
  pq list shuffled  # shuffles Lines, via 'random.shuffle'
  pq str casefold  # case-fold's the Chars, such as 'ß' to 'ss'  # |pq casefold
  pq str dedent  # removes blank Columns at left, via 'textwrap.dedent'
  pq str dedent strip  # drops lead Blank Columns, & trail/ lead Blank Lines
  pq str lower  # lowers the Chars, such as 'ß' to itself  # |tr '[A-Z]' '[a-z]'
  pq str strip  # removes blank Rows above and below
  pq strip  # drops Spaces etc from left and right of each Line
  pq undent  # deletes 4 Spaces if present from left of each Line  # |sed 's,^    ,,'

examples:
  echo abc |pq upper |cat -  # edit the Chars streaming through a Sh Pipe
  echo abc |pq upper  # fill the Os Copy/Paste Clipboard Buffer
  pq lower |cat -  # dump the Os Copy/Paste Clipboard Buffer, but edit the dump
  pq lower  # edit the Chars inside the Os Copy/Paste Clipboard Buffer
  pq --  # closes each Paste Line with "\n", even closes last Line if not closed
"""

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import ast
import builtins
import dataclasses
import difflib
import itertools
import json
import pathlib
import random
import re
import shutil
import stat
import subprocess
import sys
import textwrap
import types
import typing

if type(__builtins__) is not dict:  # todo: test inside:  python3 -m pdb bin/pq.py
    assert builtins is __builtins__


#
# Run well from the Sh Command Line
#


def main() -> None:
    """Run well from the Sh Command Line"""

    args = parse_pq_py_args()  # often prints help & exits zero
    Main.args = args

    sponge = PySponge(args.pysteps)
    sponge.run_pysteps()


#
# Git-track the Man Page
#


MAIN_DOC = __main__.__doc__  # not stripped
assert MAIN_DOC

LIL_DOC = MAIN_DOC  # todo: each LIL_DOC Line consistent with BIG_DOC?
LIL_DOC = LIL_DOC[LIL_DOC.rindex("\n\n") :].strip()
LIL_DOC = LIL_DOC[LIL_DOC.index("\n") :]
LIL_DOC = textwrap.dedent(LIL_DOC).strip()
LIL_DOC = "\n" + LIL_DOC + "\n"  # todo: last Graf is all Examples of Lil Doc?


BIG_DOC = r"""
usage: pq [VERB ...]

tell Python to edit the Os Copy/Paste Clipboard Buffer, else other Stdin/ Stdout

positional arguments:
  VERB        verb of the Pq Programming Language:  dedent, dent, join, len, max, ...

options:
  -h, --help  show this help message and exit

quirks:
  takes Names of Python Funcs and Types as the Words of a Pq Programming Language
  defaults like Awk to 'bytes decode splitlines Iterable', unless you say different
  ducks the Shift key and Quotes by taking '.' for '(' or ',', taking '_' for ' ', etc
  doesn't itself update the Os Copy/Paste Clipboard Buffer from the middle of a Sh Pipe
  substitutes the File '~/.ssh/pbpaste', when 'pbpaste' or 'pbcopy' undefined
  takes Regular Expression Patterns as in Python, not as as in:  awk, grep, sed, tr
  work its own 'pq' examples correctly, but not yet its own '##' examples  <= todo
  replaces:  awk, cut, head, grep, sed, sort, tail, tr, uniq, wc -l, xargs, xargs -n 1
  copied from:  git clone https://github.com/pelavarre/byoverbs.git

related works:
  https://clig.dev - Command Line Interface Guidelines, via Julia Evans (@b0rk)
  https://joeyh.name/code/moreutils/ - including 'sponge' up Stdin & dump it
  https://jqlang.github.io/jq - a fast Json Processor, lightweight & flexible
  https://pypi.org/project/pawk - a Python Line Processor, a la Awk
  https://redis.io/ - Key-Value Pairs in Memory, but with a friendly Cli

examples of running Python for each Line:
  pq dent  # adds four Spaces to left of each Line  # |sed 's,^,    ,'
  ## if.findplus.frag  # forwards each Line containing a Fragment  # |grep frag
  ## if.match.^...$  # forwards each Line of 3 Characters  # |grep ^...$
  ## if.search.pattern  # forwards each Line containing a Reg Ex Match  # |grep pattern
  pq len  # counts Chars per Line  # |jq --raw-input length
  pq lstrip  # drops Spaces etc from left of each Line  # |sed 's,^ *,,''
  pq replace..prefix:.1  # inserts Prefix to left of each Line  # |sed 's,^,prefix:,'
  pq replace.o  # deletes each 'o' Char  # |tr -d o
  pq replace.old.new  # finds and replaces each
  pq replace.old.new.1  # finds and replaces once
  pq rstrip  # drops Spaces etc from right of each Line  # |sed 's, *$,,''
  pq set join.  # drops Duplicate Chars but doesn't reorder Chars  # unique_everseen
  pq strip  # drops Spaces etc from left and right of each Line
  ## sub.old.new  # calls Python 're.sub' to replace each  # |sed 's,o,n,g'
  ## sub.old.new.1  # calls Python 're.sub' to replace once  # |sed 's,o,n,'
  ## sub.$.suffix  # appends a Suffix if not RegEx  # |sed 's,$,suffix,'
  pq undent  # deletes 4 Spaces if present from left of each Line  # |sed 's,^    ,,'
  ## removeprefix.____  # more explicit 'undent'

examples of running Python for Lines of Chars:
  pq list len  # counts Lines, else UnicodeDecodeError  # |wc -l
  ## list Counter items  # counts Duplicates of Lines, but doesn't reorder the Lines
  pq list set  # drops Duplicate Lines but doesn't reorder Lines  # unique_everseen
  pq list reversed  # forwards Lines in reverse order  # Linux |tac  # Mac |tail -r
  pq list shuffled  # shuffles Lines, via 'random.shuffle'
  pq list sorted  # forwards Lines in sorted order
  ## list sorted Counter items  # sorts and counts Duplicates  # sort |uniq -c |expand
  ## list sorted set  # sorts Lines and drops Duplicates  # sort |uniq
  ## list sorted.reverse  # forwards Lines in reversed sorted order
  pq list enumerate  # numbers each line, up from 0  # |nl -v0 |expand
  ## list enumerate.start.1  # numbers each line, up from 1  # |cat -n |expand

examples of running Python for Words of Chars:
  pq str split  # splits to 1 Word per Line, else UnicodeDecodeError  # |xargs -n 1
  pq str split len  # counts Words, else UnicodeDecodeError  # |wc -w
  pq str split join  # remake into one Line of Words, via 'str.join(list)'  # |xargs
  pq str split join replace._   # drop Spaces and drop Line-Breaks  # |tr -d ' \n'

examples of running Python for Chars decoded from Bytes:
  pq str len  # counts Chars, else UnicodeDecodeError  # |wc -m
  pq str dedent  # removes blank Columns at left, via 'textwrap.dedent'
  pq str dedent strip  # drops leading Blank Columns, and trailing/ leading Blank Lines
  pq str set join.  # drops Duplicate Chars but doesn't reorder Chars  # unique_everseen
  ## str set.key=casefold join.  # drops Duplicate Chars ignoring Case, doesn't reorder
  pq str encode  # encodes Chars as Bytes, such as 'ß' to "b'\xC3\x9F'"
  pq str fromhex  # encodes Hex to Bytes, via 'bytes.fromhex', such as 'C39F' to 'ß'
  pq str strip  # drops the Chars of the leading & trailing blank Lines

examples of running Python slightly faster for Chars, vs running for Lines:
  pq str casefold  # case-fold's the Chars, such as 'ß' to 'ss'
  pq str lower  # lowers the Chars, such as 'ß' to itself  # |tr '[A-Z]' '[a-z]'
  pq str replace._  # drop the Spaces  # |tr -d ' '
  pq str replace.0 replace.1  # drop 0 or 1  # |tr -d 0 |tr -d 1
  ## str translate...01  # drop 0 or 1  # |tr -d '01'
  ## str translate.abc123.123abc  # swap some Chars  # |tr abc123 123abc
  pq str upper  # uppers the Chars , such as 'ß' to 'SS'  # unlike |tr '[a-z]' '[A-Z]'

examples of running Python for Bytes:
  pq bytes len  # counts Bytes  # |wc -c  # such as 2 Bytes at b'\xC3\x9F' of 'ß'
  ## bytes decode.errors=replace replace.\uFFFD.?  # '?' in place of UnicodeDecodeError
  pq bytes hex upper  # decodes Bytes as Hex Chars, such as "b'\xC3\x9F'" to 'C39F'

examples of popular abbreviations:
  ## list count  # guesses 'pq Counter items' not 'pq list count._'
  ## list enum  # an alt syntax for:  pq list enumerate
  ## list sort  # an alt syntax for:  pq list sorted
  ## list reverse  # an alt syntax for:  pq list reversed

examples:
  echo abc |pq upper |cat -  # edit the Chars streaming through a Sh Pipe
  echo abc |pq upper  # fill the Os Copy/Paste Clipboard Buffer
  pq lower |cat -  # dump the Os Copy/Paste Clipboard Buffer, but edit the dump
  pq lower  # edit the Chars inside the Os Copy/Paste Clipboard Buffer

  pq  # shows briefest help message and exits
  pq --  # closes each Paste Line with "\n", even closes last Line if not closed
  pq -h  # show this help message and exits  # pq --help
  pq -hhh  # shows longest help message and exits  # pq help
  pq --help  # shows this help message and exits  # pq -h
  pq help  # shows more examples, specs more quirks  # pq -hhh
"""

# todo: bold for Big Doc to Stdout


#
# Define the Classes of a PySponge Virtual Machine, bottom-up
#


@dataclasses.dataclass
class PyCall:
    """Split a Python Callable Mention into Name, Arg, & KwArg Typed Values"""

    defname: str  # the '.func.__name__', not the '.func.__qualname__'
    arg_by_int: dict[int, object | None]
    kwarg_by_key: dict[str, object | None]

    @property
    def call_word(self) -> str:
        """Form the Call Word, without its Parentheses"""

        defname = self.defname
        arg_by_int = self.arg_by_int
        kwarg_by_key = self.kwarg_by_key

        s = f"{defname}"

        for i, v in arg_by_int.items():
            s += "."
            s += str(v)

        for k, v in kwarg_by_key.items():
            str_v = str(v)
            s += "."
            s += f"{k}={str_v}"

        return s

        # inverts 'ast_word_to_pycall'

        # str.replace._
        # str.translate..._


@dataclasses.dataclass
class PyDef:
    """Split a Python Callable into Name, Arg, KwArg, & Result Types plus Defaults"""

    defname: str  # the '.func.__name__', not the '.func.__qualname__'

    aname_by_int: dict[int, str]
    type_by_int: dict[int, type | types.UnionType]
    type_by_kw: dict[str, type | types.UnionType]

    default_by_int: dict[int, object]  # present or absent, per int
    default_by_kw: dict[str, object]

    result_type: type | types.UnionType
    result_list_type_else: type | types.UnionType | None

    @property
    def def_line(self) -> str:
        """Form the Def Sourceline, without its Colon, without a Body"""

        defname = self.defname
        aname_by_int = self.aname_by_int
        type_by_int = self.type_by_int
        type_by_kw = self.type_by_kw
        default_by_int = self.default_by_int
        default_by_kw = self.default_by_kw
        result_type = self.result_type

        arg_indices = list(range(len(aname_by_int)))
        arg_triples = list(
            zip(arg_indices, aname_by_int.values(), type_by_int.values())
        )

        #

        s = ""

        if arg_triples:
            for arg_index, arg_name, arg_type in arg_triples:
                if s:
                    s += ", "

                qualtname = ast_type_repr(arg_type)
                s += f"{arg_name}: {qualtname}"
                if arg_index in default_by_int.keys():
                    arg_default = default_by_int[arg_index]
                    s += f" = {ast_black_repr(arg_default)}"
            s += ", "
            s += "/"

        if arg_triples or type_by_kw:
            for kwarg_name, kwarg_type in type_by_kw.items():
                assert s, (s,)
                s += ", "

                qualtname = ast_type_repr(kwarg_type)
                s += f"{kwarg_name}: {qualtname}"
                if kwarg_name in default_by_kw.keys():
                    kwarg_default = default_by_kw[kwarg_name]
                    s += f" = {ast_black_repr(kwarg_default)}"

        result_tname = ast_type_repr(result_type)

        #

        s = f"def {defname}({s}) -> {result_tname}"

        return s

    # inverts 'ast_def_line_to_pydef'
    # inverts 'PyDef.def_line'


@dataclasses.dataclass
class PyFunc:
    """Speak of a Python Callable as itself plus its Py Def"""

    pycall: PyCall
    func: typing.Callable
    pydef: PyDef

    def call_on_item(self, obj) -> object | None:
        """Call the Func with the Obj, and return the Result"""

        func = self.func
        pycall = self.pycall

        args = list()
        args.append(obj)
        args.extend(pycall.arg_by_int.values())

        kwargs = pycall.kwarg_by_key

        result = func(*args, **kwargs)

        return result

    def call_on_iterable(self, obj) -> typing.Iterable:
        """Call the Func with the Obj, and return the Result"""

        func = self.func
        pycall = self.pycall

        args = list()
        args.append(obj)
        args.extend(pycall.arg_by_int.values())

        kwargs = pycall.kwarg_by_key

        result = func(*args, **kwargs)

        return result

    # todo: why MyPy requires 2 Bodies for call_on_item/ call_on_iterable


@dataclasses.dataclass
class PyStep:
    """Clone the Sponge, change its Datatype, and/or call a PyFunc to edit it"""

    pyverb: str  # "str", "dent"
    pytype_else: type | types.UnionType | None
    pyfunc_else: PyFunc | None


@dataclasses.dataclass
class PqPyArgs:
    """Name the Command-Line Arguments of Pq Py"""

    ns_pyverbs: list[str]
    pysteps: list[PyStep]


def parse_pq_py_args() -> PqPyArgs:
    """Parse the Command-Line Arguments of Pq Py"""

    main_doc = __main__.__doc__
    assert main_doc

    lil_doc = LIL_DOC
    big_doc = BIG_DOC

    assert main_doc == MAIN_DOC
    assert argparse.ZERO_OR_MORE == "*"

    # Form the Parser

    prog = "pq"
    description = "edit the Os Copy/Paste Clipboard Buffer, else other Stdin/ Stdout"
    epilog = main_doc[main_doc.index("quirks:") :]  # todo: first Graf of Epilog?

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    help_help = "show this help message and exit"
    parser.add_argument("-h", "--help", action="count", help=help_help)

    verb_help = "verb of the Pq Programming Language:  dedent, join len, max, ..."
    parser.add_argument("pyverbs", metavar="VERB", nargs="*", help=verb_help)

    # Parse the Args, else print help & exit zero

    ns = parser.parse_args()  # often prints help & exits zero

    doc_else = None
    if ns.help:
        if ns.help < 3:
            doc_else = main_doc.strip()
        else:
            doc_else = big_doc
    elif "help" in ns.pyverbs:
        doc_else = big_doc
    elif not sys.argv[1:]:
        doc_else = lil_doc

    if doc_else:
        print(doc_else)

        sys.exit(0)

    # Forward instructions on into the main PySponge

    opt_pyverbs = ns_choose_pyverbs(ns)
    opt_pysteps = list(pyverb_find_pystep(_) for _ in opt_pyverbs)
    pos_pysteps = list(pyverb_find_pystep(_) for _ in ns.pyverbs)

    pysteps = opt_pysteps + pos_pysteps
    if pysteps:
        pystep_n = pysteps[-1]
        if pystep_n.pyverb != "bytes":
            bytes_pystep = pyverb_find_pystep("bytes")
            pysteps.append(bytes_pystep)

    args = PqPyArgs(
        ns_pyverbs=ns.pyverbs,
        pysteps=pysteps,
    )

    return args

    # often prints help & exits zero


@dataclasses.dataclass
class Main:
    """Open up a shared workspace for the Code of this Py File"""

    args: PqPyArgs


@dataclasses.dataclass
class PySponge:
    """Read a List of Items in, mess with the List, write the List back out"""

    iterable: typing.Iterable
    iterable_type: type | types.UnionType
    pysteps: list[PyStep]

    stdin_isatty: bool
    stdout_isatty: bool

    def __init__(self, pysteps: list[PyStep]) -> None:
        self.iterable = b""
        self.iterable_type = bytes
        self.pysteps = pysteps

        self.stdin_isatty = sys.stdin.isatty()
        self.stdout_isatty = sys.stdout.isatty()

    def read_bytes(self) -> bytes:
        """Pick an Input Source and read it"""

        stdin_isatty = self.stdin_isatty

        assert stat.S_IRWXU == (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)  # u=rwx
        assert stat.S_IRWXG == (stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)  # g=rwx
        assert stat.S_IRWXO == (stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)  # o=rwx

        u_rwx = stat.S_IRWXU
        u_rw = stat.S_IRUSR | stat.S_IWUSR

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

        # Create the 'chmod go-rwx ~/.ssh/.' Dir, if absent

        ssh_path = pathlib.Path.home() / ".ssh"
        if not ssh_path.is_dir():
            ssh_path.mkdir(u_rwx)

        # Create the Copy-Paste Clipboard Buffer, if absent

        pbpaste_path = ssh_path.joinpath("0.pbpaste")
        if not pbpaste_path.exists():
            pbpaste_path.touch(mode=u_rw, exist_ok=True)

        # Read the Copy-Paste Clipboard Buffer

        ibytes = pbpaste_path.read_bytes()

        return ibytes

    def write_obytes(self, obytes: bytes) -> None:
        """Pick an Output Sink and write it"""

        stdout_isatty = self.stdout_isatty

        # Write the Sh Pipe Out and done, if present

        if not stdout_isatty:
            opath = pathlib.Path("/dev/stdout")
            try:
                opath.write_bytes(obytes)
            except BrokenPipeError as exc:  # todo: how much output written?
                line = f"BrokenPipeError: {exc}"
                sys.stderr.write(f"{line}\n")
                # sys.exit(1)  # nope, don't raise BrokenPipeError as Nonzero Exit

            return

        # Write the Os Copy-Paste Clipboard Buffer, if present

        pbcopy_else = shutil.which("pbcopy")
        if pbcopy_else is not None:
            argv = [pbcopy_else]
            subprocess.run(argv, input=obytes, check=True)

            return

        # Write the Copy-Paste Clipboard Buffer

        ssh_path = pathlib.Path.home() / ".ssh"
        pbpaste_path = ssh_path.joinpath("0.pbpaste")

        pbpaste_path.write_bytes(obytes)

    def as_pytype(self, pytype, eaching_else) -> typing.Iterable:
        """Clone the Iterable as Bytes, as List[Bytes], as Str, or as List[Str]"""

        iterable = self.iterable
        iterable_type = self.iterable_type

        if pytype is set:
            setlike = self._as_pytype_setlike(eaching_else)
            return setlike

        # Form the Bytes

        if isinstance(iterable, bytes):  # todo: runtime cost of speculative cloning?
            byte_iterable = bytes(iterable)
        else:
            byte_iterable = self.as_bytes()

        # Take the Iterable as Bytes or as List[Bytes]

        if pytype is bytes:
            return byte_iterable

        if pytype == list[bytes]:
            byteline_iterable = byte_iterable.splitlines()
            return byteline_iterable

        # Take the Iterable as Str or as List[Str]

        char_iterable = byte_iterable.decode()  # may UnicodeDecodeError

        if pytype is str:
            return char_iterable

        charline_iterable = char_iterable.splitlines()

        if pytype == list[str]:
            return charline_iterable

        # Take the Iterable as List[Bool] or List[Int]

        if pytype == list[bool]:
            bool_iterable = list(bool(_) for _ in charline_iterable)
            return bool_iterable

        if pytype == list[int]:
            int_iterable = list(int(_) for _ in charline_iterable)
            return int_iterable

        if pytype == list[float]:
            float_iterable = list(float(_) for _ in charline_iterable)
            return float_iterable

        # Else freak

        assert False, (pytype, iterable_type)  # unreached

    def _as_pytype_setlike(self, eaching_else) -> typing.Iterable:
        """Drop Duplicate Items but do Not reorder Items"""

        iterable = self.iterable

        by_k: dict[object, None]  # todo: Value could be alias of Yielded

        if not eaching_else:
            by_k = dict()
            for k in iterable:
                if k not in by_k.keys():
                    by_k[k] = None
            keys = list(by_k.keys())
            return keys

        items = list()
        for item in iterable:
            by_k = dict()
            for k in item:
                if k not in by_k.keys():
                    by_k[k] = None
            keys = list(by_k.keys())
            items.append(keys)

        return items

        # could guess:  items = b"".join(keys)
        # could guess:  items = "".join(keys)

        # compare 'unique_everseen' of https://docs.python.org/3/library/itertools.html

    def as_bytes(self) -> bytes:
        """Take the Iterable as a Clone of Bytes"""

        iterable = self.iterable

        # Write Bytes as such

        if isinstance(iterable, bytes):
            obytes = bytes(iterable)
            return obytes

        # Write Chars as 1 or more Closed Char Lines, else raise Exception

        if isinstance(iterable, str):
            ochars = str(iterable)
            if ochars and (ochars[-1:] != "\n"):
                ochars += "\n"
            obytes = ochars.encode()  # may UnicodeEncodeError
            return obytes

        # Write 1 Bool or 1 Int or 1 Float as Bytes of 1 Closed Str Line

        _3_json_scalar_types = (bool, int, float)
        if any(isinstance(iterable, _) for _ in _3_json_scalar_types):
            ochars = "\n".join(str(iterable)) + "\n"
            obytes = ochars.encode()  # practically never UnicodeEncodeError
            return obytes

        # Write anything else as a List

        items = list(iterable)

        # Write an Empty List as Zero Bytes

        if not items:
            obytes = b""
            return obytes

        # Write List[Bytes] as Closed Byte Lines
        # Write List[Str] as Bytes of Closed Str Lines, else Exception
        # Write Bools or Ints or Floats as Bytes of Closed Str Lines

        obytes_else = self.iterable_as_bytes_else(iterable=items)
        if obytes_else is not None:
            obytes = obytes_else
            return obytes

        # Write whatever Else as approximately equal Json Chars  # todo: close enough?

        ochars = json.dumps(iterable, indent=2) + "\n"  # may TypeError for Set, etc
        # todo: emulate jq --compact-output

        loads = json.loads(ochars)
        if loads != iterable:  # because Tuple, etc - not None, Bool, Int, Float, Str
            raise ValueError(type(loads), type(iterable))  # todo: more detail

        obytes = ochars.encode()  # may UnicodeEncodeError

        return obytes

    def iterable_as_bytes_else(self, iterable) -> bytes | None:
        """Write the Iterable as Closed Byte Lines, else None"""

        # Write List[Bytes] as Closed Byte Lines

        if isinstance(iterable[0], bytes):
            obytes = b"\n".join(iterable)
            if obytes and (obytes[-1:] != b"\n"):
                obytes += b"\n"
            return obytes

        # Write List[Str] as Bytes of Closed Str Lines, else raise Exception

        if isinstance(iterable[0], str):
            ochars = "\n".join(iterable)
            if ochars and (ochars[-1:] != b"\n"):
                ochars += "\n"
            obytes = ochars.encode()  # may UnicodeEncodeError
            return obytes

            # todo: Str as Str may collide with Str of Scalar Types

        # Write Bools or Ints or Floats as Bytes of Closed Str Lines

        json_scalar_types = (bool, int, float, str)
        if any(isinstance(iterable[0], _) for _ in json_scalar_types):
            ochars = "\n".join(str(_) for _ in iterable) + "\n"
            obytes = ochars.encode()  # practically never UnicodeEncodeError
            return obytes

        # Else give up, quit, pass the work back to the Caller

        return None

    def run_pysteps(self) -> None:
        """Launch a run of our Virtual Machine, have it take steps till it quits"""

        pysteps = self.pysteps

        self.trace_pysteps_if(pysteps)

        # Start up

        ibytes = self.read_bytes()

        # Walk the Steps and then quit

        self.iterable = ibytes
        self.iterable_type = bytes

        eaching_else = None
        for pystep in pysteps:
            iterable = self.iterable

            # print(pystep)

            # Remake the Iterable as Bytes, as List[Bytes], as Str, or as List[Str]

            if pystep.pytype_else:
                pytype = pystep.pytype_else
                eaching_else = self.pystep_pytype_convert_to(
                    pystep, pytype=pytype, eaching_else=eaching_else
                )

            # Work on the Iterable

            if pystep.pyfunc_else:
                pyfunc = pystep.pyfunc_else
                pydef = pyfunc.pydef

                if not eaching_else:  # once over all
                    result = pyfunc.call_on_iterable(iterable)  # once
                    self.iterable = result
                    self.iterable_type = pydef.result_type
                else:  # once per item
                    results = list(pyfunc.call_on_item(_) for _ in iterable)
                    self.iterable = results
                    assert pydef.result_list_type_else, (pydef,)
                    result_list_type = pydef.result_list_type_else
                    self.iterable_type = result_list_type

        # Shut down

        assert self.iterable_type is bytes, (self.iterable_type, type(self.iterable))

        obytes = typing.cast(bytes, self.iterable)
        self.write_obytes(obytes)

    def trace_pysteps_if(self, pysteps) -> None:
        """Trace intent, sketched as mechanism"""

        ns_pyverbs = Main.args.ns_pyverbs

        stdin_isatty = self.stdin_isatty
        stdout_isatty = self.stdout_isatty

        opt_pos_pyverbs = list(_.pyverb for _ in pysteps)

        line = "+ "
        if stdin_isatty:
            line += "pbpaste |"
        line += "pq "
        line += " ".join(opt_pos_pyverbs)
        if stdout_isatty:
            line += " |pbcopy"

        if stdin_isatty or stdout_isatty or (opt_pos_pyverbs != ns_pyverbs):
            print(line, file=sys.stderr)

        # todo: trace 'pq str encode' as itself, no '|pq bytes' needed

    def pystep_pytype_convert_to(self, pystep, pytype, eaching_else) -> bool:
        """Remake the Iterable as Bytes, as List[Bytes], as Str, or as List[Str]"""

        iterable_type = self.iterable_type

        #

        if pystep.pytype_else is list:
            # if iterable_type in (bool, list[bool]):  # FIXME
            #    pytype = list[bool]
            if iterable_type in (bytes, list[bytes]):
                pytype = list[bytes]
            elif iterable_type in (int, list[int]):
                pytype = list[int]
            else:
                assert iterable_type in (str, list[str]), (iterable_type,)
                pytype = list[str]

        #

        if pystep.pytype_else is typing.Iterable:
            eaching_else = True
            return eaching_else

        self.iterable = self.as_pytype(pytype=pytype, eaching_else=eaching_else)
        self.iterable_type = pytype  # bytes, list[bytes], str, list[str]

        if eaching_else:
            if pystep.pytype_else is not set:
                eaching_else = False

        #

        return eaching_else


#
# Amp up Import Ast
#


def ast_black_repr(obj) -> str:
    """Form a Py Repr of an Object, but as styled by PyPi·Black"""

    s = repr(obj)
    if s.startswith("'") and s.endswith("'"):
        if '"' not in s:
            s = s.replace("'", '"')

    return s


def ast_word_to_pycall(word) -> PyCall:
    """Form a PyCall by parsing 1 Word, without Spaces, Commas, or Parentheses"""

    pyverb_pydef_by_defname = PYVERB_PYDEF_BY_DEFNAME

    splits = word.split(".")
    assert word and splits, (word, splits)

    defname = splits[0]
    arg_by_int = dict()
    kwarg_by_key = dict()

    pyverb_exit_if(pyverb=defname)

    min_len_args = 0
    if defname in pyverb_pydef_by_defname.keys():
        pydef = pyverb_pydef_by_defname[defname]
        # keys = list(pydef.type_by_kw.keys())  # todo: fail fast wrong keys

        min_len_args = len(pydef.type_by_int.keys())
        while min_len_args and ((min_len_args - 1) in pydef.default_by_int.keys()):
            min_len_args -= 1

        assert min_len_args >= 1, (min_len_args, pydef)
        min_len_args -= 1  # don't count the placeholder for Self

    index = 0
    for split in splits[1:]:
        if "=" not in split:
            arg_by_int[index] = ast_str_to_typed_value(split)
            index += 1

    kwarg_splits = splits[1 + index :]

    while index < min_len_args:  # todo: could error, not default to =""
        arg_by_int[index] = ""
        index += 1

    for split in kwarg_splits:
        (k, eq, v0) = split.partition("=")
        kwarg_by_key[k] = ast_str_to_typed_value(v0)

    pycall = PyCall(defname=defname, arg_by_int=arg_by_int, kwarg_by_key=kwarg_by_key)

    return pycall

    # inverts 'PyDef.call_word'

    # replace._ -> replace(" ", "")
    # replace._..1 -> replace(" ", "", 1)


def ast_str_to_typed_value(self) -> object | None:
    """Eval an Arg Value or KwArg Value Fragment of a Word"""

    v0 = self

    v1 = v0.replace("_", " ")

    try:
        v2 = ast.literal_eval(v1)
    except Exception:
        v2 = v1  # instance of Str

    return v2


def ast_def_line_to_pydef(def_line) -> PyDef:
    """Form a PyDef by parsing a Py Def Sourceline, without its Colon"""

    # Pick apart the Def Name, Args Line, Result Type Name, and Comment

    s = def_line
    (s, hash_, comment) = s.partition("  #")
    s = s.removeprefix("def ")

    (defname, _opener, s) = s.partition("(")
    (argsline, _closer, s) = s.partition(")")
    result_tname = s.removeprefix(" -> ")

    result_type = ast_type_eval(result_tname)
    result_list_type_else = ast_type_eval_else("list[{}]".format(result_tname))

    # List each Positional Argument or KeyWord Option, and its Default if present

    type_by_int: dict[int, type | types.UnionType]

    aname_by_int = dict()
    type_by_int = dict()
    type_by_kw = dict()
    default_by_int = dict()
    default_by_kw = dict()

    splits = argsline.split(", ") if argsline else list()
    group = 0
    for split in splits:
        (key, _colon, keyed) = split.partition(": ")
        (tname, _eq, default_py) = keyed.partition(" = ")

        if key == "/":
            group = -1
            continue

        assert tname, (tname, key, keyed, split, splits, def_line)
        arg_type = ast_type_eval(tname)
        default_else = ast.literal_eval(default_py) if default_py else None

        if group == 0:
            arg_index = len(type_by_int)
            aname_by_int[arg_index] = key
            type_by_int[arg_index] = arg_type
            if default_py:
                default = default_else
                default_by_int[arg_index] = default
        else:
            type_by_kw[key] = arg_type
            if default_py:
                default = default_else
                default_by_kw[key] = default

    # Form one PyDef

    pydef = PyDef(
        defname=defname,
        aname_by_int=aname_by_int,
        type_by_int=type_by_int,
        type_by_kw=type_by_kw,
        default_by_int=default_by_int,
        default_by_kw=default_by_kw,
        result_type=result_type,
        result_list_type_else=result_list_type_else,
    )

    # Succeed

    remade = pydef.def_line + hash_ + comment
    assert remade == def_line, (remade, def_line)

    return pydef


def ast_type_eval(typename) -> type | types.UnionType:
    """Look up a Python Type Name"""

    assert typename in TYPE_BY_NAME.keys(), (typename,)

    evalled = TYPE_BY_NAME[typename]

    return evalled


def ast_type_eval_else(typename) -> type | types.UnionType | None:
    """Look up a Python Type Name, else None if not found"""

    if typename not in TYPE_BY_NAME.keys():
        return None

    evalled = TYPE_BY_NAME[typename]

    return evalled


TYPE_BY_NAME: dict[str, type | types.UnionType]

TYPE_BY_NAME = {
    "bool": bool,
    "bytes": bytes,
    "float": float,
    "int": int,
    "list": list,
    "list[bool]": list[bool],
    "list[bytes]": list[bytes],
    "list[float]": list[float],
    "list[int]": list[int],
    "list[list]": list[list],
    "list[list[bytes]]": list[list[bytes]],
    "list[list[str]]": list[list[str]],
    "list[None]": list[None],
    "list[object]": list[object],
    "list[object | None]": list[object | None],
    "list[set]": list[set],
    "list[str]": list[str],
    "None": type(None),
    "object": object,
    "object | None": object | None,
    "set": set,  # todo: meaning a 'set_list' like 'builtins.set' but ordered
    "str": str,
    "typing.Generator": typing.Generator,
    "typing.Iterable": typing.Iterable,
}  # todo: think more about what 'not in TYPE_BY_NAME.keys()' should mean


def ast_type_repr(type_) -> str:
    """Form an eval'lable Python Type Name"""

    if type_ is type(None):
        typename = "None"
    else:
        typename = repr(type_)  # 'list[str]', 'object | None', 'typing.Iterable'
        if typename.startswith("<class "):
            typename = type_.__name__  # 'int', 'str'

    assert typename in TYPE_BY_NAME.keys(), (typename,)

    return typename


#
# Amp up Import BuiltIns for Types Iterable
#


def iterable_join(self: typing.Iterable, /, sep: str = " ") -> str:
    """Catenate the Items of the List, but insert a Sep before each next Item"""

    join = sep.join(self)

    return join

    # may TypeError: sequence item ~: expected str instance, ~ found
    # may TypeError: sequence item 0: expected a bytes-like object, ~ found

    # may return List[type(sep)] for empty Lists of any type


def iterable_shuffled(self: typing.Iterable) -> list:
    """Shuffle the Items of the List, in place"""

    items = list(self)
    random.shuffle(items)

    return items


#
# Amp up Import BuiltIns Str
#


def str_dent(self: str) -> str:
    """Insert 4 Blank Columns into the Left of 1 Line"""

    dented = "    " + self

    return dented


def str_splitgrafs(self: str) -> list[list[str]]:
    """Form List of Lists of Lines, from Wider Lines separated by Empty Lines"""

    lines = self.splitlines()
    grafs = list(list(v) for (k, v) in itertools.groupby(lines, key=bool) if k)

    return grafs


def str_undent(self: str) -> str:
    """Drop 4 Blank Columns from the Left of 1 Line, if present"""

    undented = self.removeprefix(4 * " ")

    return undented


def str_unexpandtabs(self: str) -> str:
    """Compress the Chars by replacing Spaces with Tabs, at left or elsewhere"""

    echars = self.expandtabs()

    ochars = ""
    for m in re.finditer(r"([ ]+)|([^ ]+)", string=echars):
        g1 = m.group(1)

        spaces = len(g1) if g1 else 0
        if spaces > 1:
            start = m.start()
            elastic = 8 - (start % 8)  # width of the first Tab

            if elastic <= spaces:
                tabbed = elastic + (((spaces - elastic) // 8) * 8)
                assert tabbed <= spaces, (tabbed, spaces, start)

                tabs = (tabbed + 8 - 1) // 8
                if tabs < spaces:
                    ochars += tabs * "\t"
                    if tabbed < spaces:
                        ochars += (spaces - tabbed) * " "

                    continue

        ochars += m.group(0)

    assert ochars.expandtabs() == echars, (ochars, echars)  # requires correct Print

    return ochars

    # inverts 'str.expandtabs'


def _test_str_unexpandtabs() -> None:
    """Call 'str_unexpandtabs' across a spread of corner cases"""

    def test(i, want) -> None:
        o = str_unexpandtabs(i)
        assert o == want, (o, want, i)  # requires accepted Conventions

    # 0123456 0123456 0123456 0123456 0123456 0123456 0123456 0123456 0123456 0123456

    test("abcdefg i", want="abcdefg i")
    test("ab def  i", want="ab def\ti")
    test("ab def         H", want="ab def\t       H")
    test("ab def          I", want="ab def\t\tI")
    test("ab defg         I", want="ab defg\t\tI")  # some say "ab defg \tI"
    test("ab defg          J", want="ab defg\t\t J")

    # 0123456 0123456 0123456 0123456 0123456 0123456 0123456 0123456 0123456 0123456


#
# Amp up Import BuiltIns TextWrap
#


def textwrap_dedent_lines(self: str) -> list[str]:
    """Drop the Blank Lines and the Leftmost Blank Columns"""

    dedent = textwrap.dedent(self)
    strip = dedent.strip()
    splitlines = strip.splitlines()

    return splitlines


#
# Declare the Input Types of many Pq Words
#


def ns_choose_pyverbs(ns) -> list[str]:
    """Choose For-Each or not, and between Bytes, Chars, Words, Lines, Grafs"""

    opt_pyverbs = list()

    if not ns.pyverbs:
        opt_pyverbs.append("str")
    else:
        pyverb_0 = ns.pyverbs[0]
        if pyverb_0 == "bytes":
            pass
        else:
            opt_pyverbs.append("str")
            if pyverb_0 == "str":
                pass
            elif pyverb_0 == "list":
                pass
            else:
                opt_pyverbs.append("list")
                opt_pyverbs.append("Iterable")

    # Succeed

    return opt_pyverbs


def pyverb_find_pystep(pyverb) -> PyStep:
    """Pick 1 PyDef to run for 1 Pq Verb"""

    pyverb_pydef_by_defname = PYVERB_PYDEF_BY_DEFNAME
    pytype_by_pyverb = PYTYPE_BY_PYVERB

    # Pick apart the mention of the Func from mention of its Args & KwArgs

    pycall = ast_word_to_pycall(pyverb)

    # Pick 1 PyType to run

    defname = pycall.defname
    if defname in pytype_by_pyverb.keys():
        pytype = pytype_by_pyverb[defname]

        pystep = PyStep(
            pyverb=defname,
            pytype_else=pytype,
            pyfunc_else=None,
        )

        return pystep

    # Pick 1 PyFunc to run

    assert defname in pyverb_pydef_by_defname.keys(), (defname,)
    pydef = pyverb_pydef_by_defname[defname]

    func = pydef_find_func(pydef)

    pyfunc = PyFunc(
        pycall=pycall,
        func=func,
        pydef=pydef,
    )

    call_word = pycall.call_word
    pystep = PyStep(
        pyverb=call_word,
        pytype_else=None,
        pyfunc_else=pyfunc,
    )

    return pystep


def pyverb_exit_if(pyverb) -> None:
    """Quit if PyVerb not found, but first tell Stderr why"""

    defined_pyverbs = DEFINED_PYVERBS

    v0 = defined_pyverbs[0]
    vn = defined_pyverbs[-1]

    if pyverb not in defined_pyverbs:
        alts = difflib.get_close_matches(pyverb, possibilities=defined_pyverbs, n=1)
        if not alts:
            line = f"NameError: name {pyverb!r} not found in {v0!r} .. {vn!r}"
        else:
            alt = alts[0]
            line = f"NameError: name {pyverb!r} is not defined. Did you mean: {alt!r}?"

        sys.stderr.write(f"{line}\n")
        sys.exit(1)


def pydef_find_func(pydef) -> typing.Callable:
    """Pick 1 Func to run for 1 PyDef"""

    defname = pydef.defname

    pyplus_func_by_name: dict[str, typing.Callable]
    pyplus_func_by_name = {
        "dent": str_dent,
        "dedent": textwrap.dedent,
        "join": iterable_join,
        "shuffled": iterable_shuffled,
        "splitgrafs": str_splitgrafs,
        "undent": str_undent,
    }

    func: typing.Callable
    if defname in pyplus_func_by_name.keys():
        func = pyplus_func_by_name[defname]

    elif hasattr(str, defname):
        func = getattr(str, defname)  # casefold, dedent, encode, split, strip
    elif hasattr(bytes, defname):
        func = getattr(bytes, defname)  # decode, hex

    else:
        assert hasattr(builtins, defname), (defname,)
        func = getattr(builtins, defname)  # len, max, min

    return func


def form_defined_pyverbs() -> list[str]:
    """List our Defined PyVerb's"""

    pyverb_pydef_by_defname = PYVERB_PYDEF_BY_DEFNAME
    pytype_by_pyverb = PYTYPE_BY_PYVERB

    defined_pyverbs: list[str]

    defined_pyverbs = list()
    defined_pyverbs.extend(pyverb_pydef_by_defname.keys())
    defined_pyverbs.extend(pytype_by_pyverb.keys())
    defined_pyverbs.sort()

    assert sorted(set(defined_pyverbs)) == defined_pyverbs, (defined_pyverbs,)

    return defined_pyverbs


def form_pyverb_pydef_by_defname() -> dict[str, PyDef]:
    """Compile the PyDef's of many Pq Words"""

    bytes_pydefs = list(ast_def_line_to_pydef(_) for _ in _BYTES_DEFS_LINES)
    chars_pydefs = list(ast_def_line_to_pydef(_) for _ in _CHARS_DEFS_LINES)
    words_pydefs = list(ast_def_line_to_pydef(_) for _ in _WORDS_DEFS_LINES)
    # void_pydefs = list(ast_def_line_to_pydef(_) for _ in _VOID_DEFS_LINES)

    outer_pydefs = list(ast_def_line_to_pydef(_) for _ in _OUTER_DEFS_LINES)
    inner_pydefs = list(ast_def_line_to_pydef(_) for _ in _INNER_DEFS_LINES)

    pydefs = list()
    pydefs.extend(bytes_pydefs)
    pydefs.extend(chars_pydefs)
    pydefs.extend(words_pydefs)
    # pydefs.extend(void_pydefs)
    pydefs.extend(outer_pydefs)
    pydefs.extend(inner_pydefs)

    pydef_by_defname = dict()
    for pydef in pydefs:
        defname = pydef.defname
        pydef_by_defname[defname] = pydef

        pydef_find_func(pydef)  # quits unless 1 Py Callable found

    return pydef_by_defname


PYTYPE_BY_PYVERB = {
    "Iterable": typing.Iterable,  # todo: map, for, each
    "bytes": bytes,
    "list": list,
    "list[bytes]": list[bytes],
    "list[str]": list[str],
    "set": set,
    "str": str,
}  # todo: case-insensitive Py Types


# Pq Filters of Bytes, of Chars, of Words, of one Iterable, of each Line

_BYTES_DEFS_CHARS = """
    def decode(self: bytes, /) -> str  # bytes.decode
    def hex(self: bytes, /) -> str  # bytes.hex
"""

_CHARS_DEFS_CHARS = """
    def casefold(self: str, /) -> str  # str.casefold
    def dedent(self: str, /) -> str  # textwrap.dedent
    def encode(self: str, /) -> bytes  # str.encode
    def fromhex(self: str, /) -> bytes  # bytes.fromhex
    def lower(self: str, /) -> str  # str.lower
    def split(self: str, /) -> list[str]  # str.split
    def splitgrafs(self: str, /) -> list[list[str]]  # "splitgrafs" not in dir(str)
    def splitlines(self: str, /) -> list[str]  # str.splitlines
    def title(self: str, /) -> str  # str.title
    def upper(self: str, /) -> str  # str.upper
    def translate(self: str, from: str, to: str, drop: str = "", /) -> str  # str.translate'ish
"""
# todo: >88 Columns inside Triple Quote of 'def translate'

# _VOID_DEFS_CHARS = """
#     def help() -> None  # close kin with 'builtins.help'
# """

_WORDS_DEFS_CHARS = """
    def join(self: list[str], /, sep: str = " ") -> str  # str.join, but KwArg Sep
"""

_OUTER_DEFS_CHARS = """
    def enumerate(self: typing.Iterable, /, start: int = 0) -> typing.Generator
    def len(self: typing.Iterable, /) -> int  # builtins.len
    def max(self: typing.Iterable, /) -> object | None  # builtins.max
    def min(self: typing.Iterable, /) -> object | None  # builtins.min
    def reversed(self: typing.Iterable, /) -> typing.Generator
    def shuffled(self: typing.Iterable, /) -> list  # random.shuffle
    def sorted(self: typing.Iterable, /, reverse: bool = False) -> list
    def sum(self: typing.Iterable, /, start: object = 0) -> object | None  # builtins.sum
"""
# todo: >88 Columns inside Triple Quote of 'def sum'

_INNER_DEFS_CHARS = """
    def bool(self: object, /) -> bool  # builtins.bool
    def dent(self: str, /) -> str  # "dent" not in dir(str)
    def float(self: object, /) -> float  # builtins.float
    def int(self: object, /) -> int  # builtins.int
    def lstrip(self: str, /) -> str  # str.lstrip
    def replace(self: str, old: str, new: str, count: int = 0, /) -> str  # str.replace
    def strip(self: str, /) -> str  # str.strip
    def rstrip(self: str, /) -> str  # str.rstrip
    def undent(self: str, /) -> str  # "undent" not in dir(str)
"""

# todo: try 'ast' parse of 'def ... -> type: return type()' falsey result


_BYTES_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_BYTES_DEFS_CHARS))
_CHARS_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_CHARS_DEFS_CHARS))
_WORDS_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_WORDS_DEFS_CHARS))
# _VOID_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_VOID_DEFS_CHARS))

_OUTER_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_OUTER_DEFS_CHARS))
_INNER_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_INNER_DEFS_CHARS))

PYVERB_PYDEF_BY_DEFNAME = form_pyverb_pydef_by_defname()

DEFINED_PYVERBS = form_defined_pyverbs()


# todo: collections.Counter vs str.count vs. list.count (and vs bytes.count)

# todo: str.format vs builtins.format
# todo: str.index vs list.index (and vs bytes.index)
# todo: str.split vs re.split vs builtins.split (and vs bytes.split)
# todo: re.compile vs builtins.compile
# todo: bytes.hex vs builtins.hex


#
# Git-Track some more Doc in progress
#


# todo: pq aliases
#
# trace as casefolded Alias when supplied in pieces
# trace as mixed Self when supplied as 1 verb
# enter/ exit to reconstruct from Bytes/ Chars/ ... Grafs
# trace enter, don't trace exit
#
# Bytes = bytes
# Chars = encode/ decode
# Words = str split/ join
# Lines = str splitlines/ join._n
# Grafs = str splitgrafs/ "\n\n".join("\n".join(_) for _ in grafs))
#
# Byte = bytes map
# Char = str map
# Word = str split map
# Line = str splitlines map
# Graf = str splitgrafs map
#


# ls -l |cv && bin/pq str strip splitlines for upper && cv

... == """

more intricate examples:
  pq decode splitlines [len]  # a more explicit syntax to say 'pq len'
  pq list [len] max  # counts max Chars per Line  # pq len| pq list max
  pq list [split len] max  # counts max Words per Line  # pq split len  # |pq list max
  pq list '[split len]' max  # an alt syntax for when Zsh dislikes ' ' inside '[]'
  pq list [split] [len] max  # another alt syntax for when Zsh dislikes ' ' inside '[]'
  pq list '_[:3]+["..."]+_[-2:]'  # first 3 & last 2 Lines, with Ellipsis in between
  pq 'removeprefix("    ")'  # same as 'pq undent' or 'pq removeprefix.____'

examples of Python for Grafs of Lines:
  pq splitgrafs  # drops leading, trailing, & duplicate Blank Lines; closes Last Line
  pq splitgrafs len  # counts Grafs
  pq splitgrafs [len]  # counts Lines per Graf
  git grep -Hn '^def ' |pq splitgrafs gather |cat -  # print one Graf of Hits per File
  git grep -Hn '^def ' |pq splitgrafs gather spread |cat -  # undo Gather with Spread

"""  # type: ignore

# todo: dig back into bytes byte str char words word lines line grafs graf
# todo: trace + pbpaste |split |pbcopy also as:  + aka:  pbpaste |xargs -n 1 |pbcopy
# todo: dumps, loads, from 'import json'
# todo: trace the pick-it-apart, don't also trace the put-it-back-together

# todo: still give us a way to say put-it-back-together differently

# todo: find a way to guess '|pq str set' should run as '|pq str set join.'
# todo: trace '|pq str set' as '|pq str set' not as '|pq str str set bytes'
# todo: trace '|pq set' as '|pq line set' not as '|pq str list Iterable set join. bytes'

# todo: more compare/ contrast 'pq' vs 'builtins.map' and 'functools.reduce'
# todo: more compare/ contrast 'pq' vs jq --raw-input
# todo: more concise errors

# todo: --no-input to run headless, never hang or nor pause for Tty
# todo: --plain, --json, --csv, --tsv
# todo: -d, --debug, -q, --quiet, -v, --version

# todo: color Stdout/ Stderr Tty, vs --no-color, --color=never|always|auto, TERM=dumb
# todo: bold, emojis
# todo: auto pager

# todo: pbcopy, pbpaste, as PyVerbs - and drop trace if explicit
# todo: str unicodedata.name, .lookup
# todo: deslack, and other contributions from bin/pq1.py

# todo: pq ls -> list[dict], in the way of lsa = ls -dhlAF -rt
# todo: pq - for writing/reading to Stdout while Tty

# todo: count Screens, given Width & Height of Screens, infinite Width for No Wrap
# todo: help not alias @ suggest 'OrderedSet' and 'set' in place of 'unique_everseen'
# todo: solve 'unique_justseen' and the other 'import itertools' 'recipes'
# todo: pq tee upper  # backs up original before editing, into './pq.tee'
# todo: pq tee.o upper tee.n os.devnull  # writes 3 Streams and no Stdout


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq2.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
