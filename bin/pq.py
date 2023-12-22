#!/usr/bin/env python3

r"""
usage: pq [-h] [-b | -c | -w | -l | -g] [-f] [VERB ...]

tell Python to edit the Os Copy/Paste Clipboard Buffer, else other Stdin/ Stdout

positional arguments:
  VERB            verb of the Pq Programming Language:  dedent, join, len, max, ...

options:
  -h, --help      show this help message and exit
  -b, --bytes     work with Bytes, such as 'len'
  -c, --chars     work with Chars, such as 'dedent' or 'split' or 'upper'
  -w, --words     work with Words of Chars, such as 'join' or 'split set'
  -l, --lines     work with Lines of Chars, such as 'max' and 'reversed'
  -g, --grafs     work with Grafs of Lines, such as 'gather' and 'spread'
  -f, --for-each  work with each Byte, Char, Word, Line, or Graf, such as 'dent'

quirks:
  takes Names of Python Funcs as the Words of the Pq Programming Language
  chooses for you, often choosing -l or -c, if you don't choose from -b, -c, -w, -l, -f
  ducks the Shift key by taking '.' for '(' or ',', taking '_' for ' ', etc
  works like:  awk, cut, head, grep, sed, sort, tail, tr, uniq, wc, xargs, xargs -n 1
  doesn't itself update the Os Copy/Paste Clipboard Buffer from the middle of a Sh Pipe
  substitutes the File '~/.ssh/pbpaste', when 'pbpaste' or 'pbcopy' undefined
  takes Regular Expression Patterns as in Python, not as as in:  awk, grep, sed, tr

related works:
  https://jqlang.github.io/jq - a Json Processor, lightweight & flexible
  https://pypi.org/project/pawk - a Python Line Processor
  https://redis.io/ - an In-Memory Data Store of Key-Value Pairs, but with a CLI

examples of Python for Bytes:
  pq -b  # no changes
  pq -b len  # counts Bytes  # |wc -c
  pq bytes len  # same as '-b len', but without '-b'
  pq decode  # decodes Bytes as Chars, such as "b'\xC3\x9F'" to 'ß'
  pq hex upper  # decodes Bytes as Hex Chars, such as "b'\xC3\x9F'" to 'C39F'
  echo 'b"\xC0\x80"' |pq decode  # raises UnicodeDecodeError
  echo 'b"\xC0\x80"' |pq decode.errors=replace replace.\uFFFD.?  # '?' for troubles

examples of Python for Chars:
  pq -c  # no changes, else raises UnicodeDecodeError if not Utf-8
  pq -c len  # counts Chars  # |wc -m
  pq -c dict keys  # drops Duplicates but doesn't reorder Chars  # unique_everseen
  pq -c strip  # drops the Chars of the leading & trailing blank Lines
  pq str strip  # same as '-c strip', but without '-c'
  pq casefold  # case-fold's the Chars, such as 'ß' to 'ss'
  pq dedent  # removes blank Columns at left
  pq encode  # encodes Chars as Bytes, such as 'ß' to "b'\xC3\x9F'"
  pq lower  # lowers the Chars, such as 'ß' to itself  # |tr '[A-Z]' '[a-z]'
  pq split  # guesses you mean 'pq -c split', same as 'pq -w'  # |xargs -n 1
  pq translate..._  # drop the Spaces  # |tr -d ' '
  pq translate.abc123.123abc  # swap some Chars  # |tr abc123 123abc
  pq upper  # uppers the Chars , such as 'ß' to 'SS'  # unlike |tr '[a-z]' '[A-Z]'

examples of Python for Words of Chars:
  pq -w  # splits to 1 Word per Line, else UnicodeDecodeError  # |xargs -n 1
  pq -w len  # counts Words  # |wc -w
  pq split len  # same as '-w len', but without '-w'  # |wc -w
  pq join  # guesses you mean 'pq -w join'  # |xargs

examples of Python for Lines of Chars:
  pq -l  # closes every Line with b"\n", else UnicodeDecodeError
  pq -l len  # counts Lines, more explicitly than 'pq len'  # |wc -l
  pq splitlines len  # same as '-l len', but without '-l'  # |wc -l
  pq Counter items  # counts Duplicates of Lines, but doesn't reorder the Lines
  pq dict keys  # drops Duplicate Lines but doesn't reorder the Lines
  pq reversed  # forwards Lines in reverse order  # Linux |tac  # Mac |tail -r
  pq set  # drops Duplicate Lines and sorts the rest  # sort |uniq
  pq sorted  # forwards Lines in sorted order
  pq sorted Counter items  # sorts and counts Duplicates  # sort |uniq -c |expand
  pq sorted.reverse  # forwards Lines in reversed sorted order
  pq enumerate  # number each line, up from 0  # |nl -v0 |expand
  pq enumerate.start.1  # number each line, up from 1  # |cat -n |expand
  pq count  # guesses you mean 'pq Counter items' not 'pq list count._'
  pq enum  # guesses you mean:  pq enumerate
  pq sort  # guesses you mean:  pq sorted
  pq reverse  # guesses you mean:  pq reversed
  pq -l '[:3],"...",[-2:]'  # first 3 & last 2 Lines, with Ellipsis in between

examples of Python for Grafs of Lines:
  pq -g  # drops leading, trailing, & duplicate Blank Lines; and closes Last Line
  pq -g len  # counts Lines per Graf
  pq splitgrafs len  # same as '-g len', but without '-g'
  git grep -Hn '^def ' |pq -g |cat -  # print one Graf of Hits per File
  git grep -Hn '^def ' |pq --grafs |cat -  # say '-g' as '--grafs'
  git grep -Hn '^def ' |pq gather |cat -  # say '-g' as 'gather'
  git grep -Hn '^def ' |pq gather spread |cat -  # undo Gather with Spread

examples of Python for each Line:
  pq -f len  # counts Chars per Line
  pq -f len max  # counts max Chars per Line
  pq -f split len max  # counts max Words per Line
  pq splitlines list split len max  # same as '-f split len max', but without '-f'
  pq dent  # adds four Spaces to left of each Line  # |sed 's,^,    ,'
  pq dict keys  # drops Duplicates but doesn't reorder Lines  # unique_everseen
  pq if.findplus.frag  # forward each Line containing a Fragment  # |grep frag
  pq if.match.^...$  # forward each Line of 3 Characters  # |grep ^...$
  pq if.search.pattern  # forward each Line containing a Reg Ex Match  # |grep pattern
  pq lstrip  # drops Spaces etc from left of each Line  # |sed 's,^ *,,''
  pq replace..prefix.1  # inserts Prefix to left of each Line  # |sed 's,^,prefix,'
  pq replace.o  # deletes each 'o' Char  # |tr -d o
  pq replace.old.new  # finds and replaces each
  pq replace.old.new.1  # finds and replaces once
  pq rstrip  # drops Spaces etc from right of each Line  # |sed 's, *$,,''
  pq strip  # drops Spaces etc from left and right of each Line
  pq sub.old.new  # calls Python 're.sub' to replace each  # |sed 's,o,n,g'
  pq sub.old.new.1  # calls Python 're.sub' to replace once  # |sed 's,o,n,'
  pq sub.$.suffix  # appends a Suffix if not RegEx  # |sed 's,$,suffix,'
  pq undent  # deletes 4 Spaces if present from left of each Line  # |sed 's,^    ,,'
  pq removeprefix.____  # same as 'undent'
  pq 'removeprefix("    ")'  # same as 'undent'

examples:
  echo abc |pq upper |cat -  # edit the Chars streaming through a Sh Pipe
  echo abc |pq upper  # fill the Os Copy/Paste Clipboard Buffer
  pq lower |cat -  # dump the Os Copy/Paste Clipboard Buffer, but edit the dump
  pq lower  # edit the Chars inside the Os Copy/Paste Clipboard Buffer
  pq --  # closes each Line with b"\n", and closes last Line if not closed
"""

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import ast
import builtins
import dataclasses
import itertools
import json
import pathlib
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


@dataclasses.dataclass
class PqPyArgs:
    """Name the Command-Line Arguments of Pq Py"""

    pysteps: list["PyStep"]  # todo: stop needing to quote forward references to Types


@dataclasses.dataclass
class Main:
    """Open up a shared workspace for the Code of this Py File"""

    args: PqPyArgs


def main() -> None:
    """Run well from the Sh Command Line"""

    args = parse_pq_py_args()  # often prints help & exits zero
    Main.args = args

    sponge = PySponge(args.pysteps)
    sponge.run_pysteps()


def parse_pq_py_args() -> PqPyArgs:
    """Parse the Command-Line Arguments of Pq Py"""

    assert argparse.ZERO_OR_MORE == "*"

    # Form the base Parser without Arguments

    doc = __main__.__doc__

    prog = "pq"
    description = "edit the Os Copy/Paste Clipboard Buffer, else other Stdin/ Stdout"
    epilog = doc[doc.index("quirks:") :]  # todo: test if this is first Graf of Epilog

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=True,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    # Add the Arguments

    sub = parser.add_mutually_exclusive_group()

    b_help = "work with Bytes, such as 'len'"
    c_help = "work with Chars, such as 'dedent' or 'split' or 'upper'"
    w_help = "work with Words of Chars, such as 'join' or 'split set'"
    l_help = "work with Lines of Chars, such as 'max' and 'reversed'"
    g_help = "work with Grafs of Lines, such as 'gather' and 'spread'"

    sub.add_argument("-b", "--bytes", action="count", help=b_help)
    sub.add_argument("-c", "--chars", action="count", help=c_help)
    sub.add_argument("-w", "--words", action="count", help=w_help)
    sub.add_argument("-l", "--lines", action="count", help=l_help)
    sub.add_argument("-g", "--grafs", action="count", help=g_help)

    f_help = "work with each Byte, Char, Word, Line, or Graf, such as 'dent'"
    parser.add_argument("-f", "--for-each", action="count", help=f_help)

    verb_help = "verb of the Pq Programming Language:  dedent, join len, max, ..."
    parser.add_argument("pqverbs", metavar="VERB", nargs="*", help=verb_help)

    # Run the Parser

    ns = parser.parse_args()  # often prints help & exits zero

    # Fall back to print the last Paragraph of Epilog in a frame of 2 Blank Lines

    if not sys.argv[1:]:
        doc = __main__.__doc__
        testdoc = doc[doc.rindex("\n\n") :].strip()
        testdoc = testdoc[testdoc.index("\n") :]
        testdoc = textwrap.dedent(testdoc).strip()

        print()
        print(testdoc)
        print()

        sys.exit(0)

    # Forward instructions on into the main PySponge

    opt_pqverbs = ns_choose_pqverbs(ns)
    opt_pysteps = list(pqverb_find_pystep(_) for _ in opt_pqverbs)
    pos_pysteps = list(pqverb_find_pystep(_) for _ in ns.pqverbs)

    pysteps = opt_pysteps + pos_pysteps
    if pysteps:
        pystep_n = pysteps[-1]
        bytes_pystep = pqverb_find_pystep("bytes")

        endswith_bytes = False
        if pystep_n.pytype_else is bytes:
            endswith_bytes = True
        elif pystep_n.pyfunc_else:
            if pystep_n.pyfunc_else.pydef.result_type is bytes:
                endswith_bytes = True

        if not endswith_bytes:
            pysteps.append(bytes_pystep)

    args = PqPyArgs(
        pysteps=pysteps,
    )

    return args

    # often prints help & exits zero


#
# Declare PyDef's as the Pq Pipe Filters
#


@dataclasses.dataclass
class PyDef:
    """Speak of a Python Callable as its Name, Args, KwArgs, Defaults, & Result Type"""

    defname: str  # the '.func.__name__', not the '.func.__qualname__'

    aname_by_int: dict[int, str]
    type_by_int: dict[int, type | types.UnionType]
    type_by_kw: dict[str, type | types.UnionType]

    default_by_int: dict[int, object]
    default_by_kw: dict[str, object]

    result_type: type | types.UnionType
    result_list_type_else: type | types.UnionType | None

    @property
    def defline(self) -> str:
        """Form the Def Sourceline, without its Colon"""

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

        for arg_index, arg_name, arg_type in arg_triples:
            if s:
                s += ", "

            qualtname = ast_type_repr(arg_type)
            s += f"{arg_name}: {qualtname}"
            if arg_index in default_by_int.keys():
                arg_default = default_by_int[arg_index]
                s += f" = {ast_black_repr(arg_default)}"

        if s:
            s += ", "
        s += "/"

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


@dataclasses.dataclass
class PyFunc:
    """Speak of a Python Callable as itself plus its Py Def"""

    func: typing.Callable
    pydef: PyDef


@dataclasses.dataclass
class PyStep:
    """Clone the Sponge, change its Datatype, and/or call a PyFunc to edit it"""

    pytype_else: type | types.UnionType | None
    pyfunc_else: PyFunc | None


class PySponge:
    """Read a List of Items in, mess with the List, write the List back out"""

    stdin_isatty: bool
    iterable: typing.Iterable
    iterable_type: type | types.UnionType
    stdout_isatty: bool
    pysteps: list[PyStep]

    def __init__(self, pysteps: list[PyStep]) -> None:
        self.stdin_isatty = sys.stdin.isatty()
        self.iterable = b""
        self.iterable_type = bytes
        self.stdout_isatty = sys.stdout.isatty()
        self.pysteps = pysteps

    def read_bytes(self) -> bytes:
        """Pick an Input Source and read it"""

        stdin_isatty = self.stdin_isatty

        assert stat.S_IRWXU == (
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
        )  # chmod u=rwx
        assert stat.S_IRWXG == (
            stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
        )  # chmod g=rwx
        assert stat.S_IRWXO == (
            stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH
        )  # chmod o=rwx

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
            sys.stderr.write("+ pbpaste\n")
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
            opath.write_bytes(obytes)

            return

        # Write the Os Copy-Paste Clipboard Buffer, if present

        pbcopy_else = shutil.which("pbcopy")
        if pbcopy_else is not None:
            sys.stderr.write("+ pbcopy\n")
            argv = [pbcopy_else]
            subprocess.run(argv, input=obytes, check=True)

            return

        # Write the Copy-Paste Clipboard Buffer

        ssh_path = pathlib.Path.home() / ".ssh"
        pbpaste_path = ssh_path.joinpath("0.pbpaste")

        pbpaste_path.write_bytes(obytes)

    def as_pytype(self, pytype) -> typing.Iterable:
        """Clone the Iterable as Bytes, as List[Bytes], as Str, or as List[Str]"""

        iterable = self.iterable

        # Take the Iterable as Bytes or as List[Bytes]

        if isinstance(iterable, bytes):
            byte_iterable = iterable
        else:
            byte_iterable = self.as_bytes()

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

        # Else freak

        assert False, (pytype,)  # unreached

    def as_bytes(self) -> bytes:
        """Take the Iterable as Bytes"""

        iterable = self.iterable

        # Take Bytes as such

        if isinstance(iterable, bytes):
            obytes = bytes(iterable)
            return obytes

        # Take Chars as 1 or more Closed Char Lines, else raise Exception

        if isinstance(iterable, str):
            ochars = str(iterable)
            if ochars[-1:] != "\n":
                ochars += "\n"
            obytes = ochars.encode()  # may UnicodeEncodeError
            return obytes

        # Take an Empty List as Zero Bytes

        if not iterable:
            obytes = b""
            return obytes

        # Take List[Bytes] as Closed Byte Lines

        if isinstance(iterable, list):
            if isinstance(iterable[0], bytes):
                obytes = b"\n".join(iterable) + b"\n"
                return obytes

            # Take List[Str] as Closed Str Lines, else raise Exception

            if isinstance(iterable[0], str):
                ochars = "\n".join(iterable) + "\n"
                obytes = ochars.encode()  # may UnicodeEncodeError
                return obytes

                # todo: Str as Str may collide with Str of Scalar Types

            # Take Bools or Ints or Floats as Closed Str Lines

            json_scalar_types = (bool, int, float, str)
            if any(isinstance(iterable[0], _) for _ in json_scalar_types):
                ochars = "\n".join(str(_) for _ in iterable) + "\n"  # not int
                obytes = ochars.encode()  # practically never UnicodeEncodeError
                return obytes

        # Take whatever Else as approximately equal Json Chars

        ochars = json.dumps(iterable, indent=2) + "\n"  # may TypeError for Set, etc
        # todo: emulate jq --compact-output

        loads = json.loads(ochars)
        if loads != iterable:  # because Tuple, etc - not None, Bool, Int, Float, Str
            raise ValueError(type(loads), type(iterable))  # todo: more detail

        obytes = ochars.encode()  # may UnicodeEncodeError

        return obytes

    def run_pysteps(self) -> None:
        """Launch a run of our Virtual Machine, have it take steps till it quits"""

        pysteps = self.pysteps

        # Start up

        ibytes = self.read_bytes()

        # Walk the Steps and then quit

        self.iterable = ibytes
        self.iterable_type = bytes

        eaching_else = None
        for pystep in pysteps:
            iterable = self.iterable
            iterable_type = self.iterable_type

            # Remake the Iterable as Bytes, as List[Bytes], as Str, or as List[Str]

            if pystep.pytype_else:
                pytype = pystep.pytype_else

                #

                if pystep.pytype_else is typing.Iterable:
                    eaching_else = True
                    continue

                if eaching_else:
                    eaching_else = False

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

                self.iterable = self.as_pytype(pytype=pytype)
                self.iterable_type = pytype  # bytes, list[bytes], str, list[str]

            # Work on the Iterable

            if pystep.pyfunc_else:
                pyfunc = pystep.pyfunc_else
                func = pyfunc.func
                pydef = pyfunc.pydef

                if not eaching_else:
                    self.iterable = func(iterable)  # once
                    self.iterable_type = pydef.result_type
                else:
                    self.iterable = list(func(_) for _ in iterable)  # once per item
                    assert pydef.result_list_type_else, (pydef,)
                    result_list_type = pydef.result_list_type_else
                    self.iterable_type = result_list_type

        # Shut down

        assert self.iterable_type is bytes, (self.iterable_type, type(self.iterable))

        obytes = typing.cast(bytes, self.iterable)
        self.write_obytes(obytes)


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


def ast_defline_to_pydef(defline) -> PyDef:
    """Form a PyDef by parsing a Py Def Sourceline, without its Colon"""

    # Pick apart the Def Name, Args Line, Result Type Name, and Comment

    s = defline
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

    splits = argsline.split(", ")
    group = 0
    for split in splits:
        (key, _colon, keyed) = split.partition(": ")
        (tname, _eq, default_py) = keyed.partition(" = ")

        if key == "/":
            group = -1
            continue

        assert tname, (tname, key, keyed, split, splits, defline)
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

    remade = pydef.defline + hash_ + comment
    assert remade == defline, (remade, defline)

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
    "int": int,
    "list": list,
    "list[bool]": list[bool],
    "list[bytes]": list[bytes],
    "list[list[str]]": list[list[str]],
    "list[int]": list[int],
    "list[object | None]": list[object | None],
    "list[str]": list[str],
    "object | None": object | None,
    "str": str,
    "typing.Generator": typing.Generator,
    "typing.Iterable": typing.Iterable,
}


def ast_type_repr(type_) -> str:
    """Form an eval'lable Python Type Name"""

    typename = repr(type_)  # 'list[str]', 'object | None', 'typing.Iterable'
    if typename.startswith("<class "):
        typename = type_.__name__  # 'int', 'str'

    assert typename in TYPE_BY_NAME.keys(), (typename,)

    return typename


#
# Amp up Import BuiltIns List
#


def list_join(self: list, /, sep: str = " ") -> str:
    """Catenate the Items of the List, but insert a Sep before each next Item"""

    join = sep.join(self)

    return join

    # may TypeError: sequence item ~: expected str instance, ~ found


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


def ns_choose_pqverbs(ns) -> list[str]:
    """Choose For-Each or not, and between Bytes, Chars, Words, Lines, Grafs"""

    defnames = list()

    if not ns.bytes:  # -b
        defnames.append("decode")
        if not ns.chars:  # -c
            if ns.words:  # -w
                defnames.append("split")
            elif ns.grafs:  # -g
                defnames.append("splitgrafs")
            else:
                defnames.append("splitlines")
                if not ns.lines:  # -l
                    assert False  # FIXME

    if ns.for_each:  # -f
        defnames.append("each")

    # Succeed

    return defnames


def pqverb_find_pystep(pqverb) -> PyStep:
    """Pick 1 PyDef to run for 1 Pq Verb"""

    pqverb_pydef_by_defname = PQVERB_PYDEF_BY_DEFNAME

    pytype_by_pqverb = {
        "bytes": bytes,
        "each": typing.Iterable,  # todo: 'each' isn't precisely a Py Type
        "list": list,
        "list[bytes]": list[bytes],
        "list[str]": list[str],
        "str": str,
    }

    #

    if pqverb in pytype_by_pqverb.keys():
        pytype = pytype_by_pqverb[pqverb]

        pystep = PyStep(
            pytype_else=pytype,
            pyfunc_else=None,
        )

        return pystep

    #

    assert pqverb in pqverb_pydef_by_defname, (pqverb,)
    pydef = pqverb_pydef_by_defname[pqverb]

    func = pydef_find_func(pydef)

    pyfunc = PyFunc(
        func=func,
        pydef=pydef,
    )

    pystep = PyStep(
        pytype_else=None,
        pyfunc_else=pyfunc,
    )

    return pystep


def pydef_find_func(pydef) -> typing.Callable:
    """Pick 1 Func to run for 1 PyDef"""

    defname = pydef.defname

    pyplus_func_by_name: dict[str, typing.Callable]
    pyplus_func_by_name = {
        "dent": str_dent,
        "dedent": textwrap.dedent,
        "join": list_join,
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


def form_pqverb_pydef_by_defname() -> dict[str, PyDef]:
    """Compile the PyDef's of many Pq Words"""

    bytes_pydefs = list(ast_defline_to_pydef(_) for _ in _BYTES_DEFS_LINES)
    chars_pydefs = list(ast_defline_to_pydef(_) for _ in _CHARS_DEFS_LINES)
    words_pydefs = list(ast_defline_to_pydef(_) for _ in _WORDS_DEFS_LINES)
    iterables_pydefs = list(ast_defline_to_pydef(_) for _ in _ITERABLES_DEFS_LINES)
    line_pydefs = list(ast_defline_to_pydef(_) for _ in _LINE_DEFS_LINES)

    pydefs = list()
    pydefs.extend(bytes_pydefs)
    pydefs.extend(chars_pydefs)
    pydefs.extend(words_pydefs)
    pydefs.extend(iterables_pydefs)
    pydefs.extend(line_pydefs)

    pydef_by_defname = dict()
    for pydef in pydefs:
        defname = pydef.defname
        pydef_by_defname[defname] = pydef

        pydef_find_func(pydef)  # quits unless 1 Py Callable found

    return pydef_by_defname


_BYTES_DEFS_CHARS = """
    def decode(self: bytes, /) -> str  # bytes.decode
    def hex(self: bytes, /) -> str  # bytes.hex
"""

_CHARS_DEFS_CHARS = """
    def casefold(self: str, /) -> str  # str.casefold
    def dedent(self: str, /) -> str  # textwrap.dedent
    def encode(self: str, /) -> bytes  # str.encode
    def lower(self: str, /) -> str  # str.lower
    def split(self: str, /) -> list[str]  # str.split
    def splitgrafs(self: str, /) -> list[list[str]]  # "splitgrafs" not in dir(str)
    def splitlines(self: str, /) -> list[str]  # str.splitlines
    def title(self: str, /) -> str  # str.title
    def upper(self: str, /) -> str  # str.upper
    def translate(self: str, from: str, to: str, drop: str = "", /) -> str  # str.translate'ish
"""

_WORDS_DEFS_CHARS = """
    def join(self: list[str], /, sep: str = " ") -> str  # str.join'ish
"""

_ITERABLES_DEFS_CHARS = """
    def enumerate(self: typing.Iterable, /, start: int = 0) -> typing.Generator
    def len(self: typing.Iterable, /) -> int  # builtins.len
    def max(self: typing.Iterable, /) -> object | None  # builtins.max
    def min(self: typing.Iterable, /) -> object | None  # builtins.min
    def reversed(self: typing.Iterable, /) -> typing.Generator
    def sorted(self: typing.Iterable, /, reverse: bool = False) -> list
"""

_LINE_DEFS_CHARS = """
    def dent(self: str, /) -> str  # "dent" not in dir(str)
    def lstrip(self: str, /) -> str  # str.lstrip
    def strip(self: str, /) -> str  # str.strip
    def rstrip(self: str, /) -> str  # str.rstrip
    def undent(self: str, /) -> str  # "undent" not in dir(str)
"""


_BYTES_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_BYTES_DEFS_CHARS))
_CHARS_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_CHARS_DEFS_CHARS))
_WORDS_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_WORDS_DEFS_CHARS))
_ITERABLES_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_ITERABLES_DEFS_CHARS))
_LINE_DEFS_LINES = list(_ for _ in textwrap_dedent_lines(_LINE_DEFS_CHARS))


PQVERB_PYDEF_BY_DEFNAME = form_pqverb_pydef_by_defname()


# todo: collections.Counter vs str.count vs. list.count (and vs bytes.count)

# todo: str.format vs builtins.format
# todo: str.index vs list.index (and vs bytes.index)
# todo: str.split vs re.split vs builtins.split (and vs bytes.split)
# todo: re.compile vs builtins.compile
# todo: bytes.hex vs builtins.hex


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: count Screens, given Width & Height of Screens, infinite Width for No Wrap
# todo: suggest 'dict keys' in place of 'unique_everseen'
# todo: solve 'unique_justseen' and the other 'import itertools' 'recipes'
# todo: pq tee upper  # backs up original before editing, into './pq.tee'
# todo: pq tee.o upper tee.n os.devnull  # writes 'o.tee', 'n.tee', '/dev/null', no Stdout


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
