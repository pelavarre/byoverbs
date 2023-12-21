#!/usr/bin/env python3

r"""
usage: pq [-h] [-b | -c | -w | -l | -g | -f] [VERB ...]

tell Python to edit the Os Copy/Paste Clipboard Buffer, else other Stdin/ Stdout

positional arguments:
  VERB             verb of the Pq Programming Language:  dedent, join, len, max, ...

options:
  -h, --help       show this help message and exit
  -b, --bytearray  work with Bytes, such as 'len'
  -c, --str        work with Chars, such as 'dedent' or 'split' or 'upper'
  -w, --words      work with Words of Chars, such as 'join'
  -l, --lines      work with Lines of Chars, such as 'dent' and 'undent'
  -g, --grafs      work with Grafs of Lines of Chars, such as 'gather' and 'spread'
  -f, --text       work with File of Lines of Chars, such as 'reversed'

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

examples with Bytes:
  pq -b  # no changes
  pq -b len  # counts Bytes  # |wc -c
  pq decode  # decodes Py Repr of Bytes as Chars, such as "b'\xC3\x9F'" to 'ß'
  echo 'b"\xC0\x80"' |pq decode  # raises UnicodeDecodeError
  echo 'b"\xC0\x80"' |pq decode.errors=replace replace.\uFFFD.?  # '?' for trouble

examples with Chars:
  pq -c  # no changes, else raises UnicodeDecodeError if not Utf-8
  pq -c len  # counts Chars  # |wc -m
  pq -c strip  # drops the Chars of the leading & trailing blank Lines
  pq casefold  # case-fold's the Chars, such as 'ß' to 'ss'
  pq dedent  # removes blank Columns at left
  pq encode  # encodes Chars as Py Repr of Bytes, such as 'ß' to "b'\xC3\x9F'"
  pq lower  # lowers the Chars, such as 'ß' to itself  # |tr '[A-Z]' '[a-z]'
  pq split  # guesses you mean 'pq -c split', same as 'pq -w'  # |xargs -n 1
  pq translate..._  # drop the Spaces  # |tr -d ' '
  pq translate.abc123.123abc  # swap some Chars  # |tr abc123 123abc
  pq upper  # uppers the Chars , such as 'ß' to 'SS'  # unlike |tr '[a-z]' '[A-Z]'

examples with Words of Chars:
  pq -w  # splits to 1 Word per Line  # |xargs -n 1
  pq -w len  # counts Words  # |wc -w
  pq join  # guesses you mean 'pq -w join'  # |xargs

examples with Lines of Chars:
  pq -l  # closes each Line with b"\n", and closes last Line if not closed
  pq -l len  # counts Chars per Line
  pq -l len max  # counts max Chars per Line
  pq dent  # adds four Spaces to left of each Line  # |sed 's,^,    ,'
  pq if.findplus.frag  # forward each Line containing a Fragment  # |grep frag
  pq if.match.^...$  # forward each Line of 3 Characters  # |grep ^...$
  pq if.search.pattern  # forward each Line containing a Reg Ex Match  # |grep pattern
  pq lstrip  # drops Spaces etc from left of each Line  # |sed 's,^ *,,''
  pq replace..prefix.1  # inserts Prefix to left of each Line  # |sed 's,^,prefix,'
  pq replace.o  # deletes each 'o' Char  # |tr -d o
  pq replace.old.new  # finds and replaces each
  pq replace.old.new.1  # finds and replaces once
  pq rstrip  # drops Spaces etc from right of each Line  # |sed 's, *$,,''
  pq split len max  # counts max Words per Line
  pq strip  # drops Spaces etc from left and right of each Line
  pq sub.old.new  # calls Python 're.sub' to replace each  # |sed 's,o,n,g'
  pq sub.old.new.1  # calls Python 're.sub' to replace once  # |sed 's,o,n,'
  pq sub.$.suffix  # appends a Suffix if not RegEx  # |sed 's,$,suffix,'
  pq undent  # deletes 4 Spaces if present from left of each Line  # |sed 's,^    ,,'
  pq removeprefix.____  # same as 'undent'
  pq 'removeprefix("    ")'  # same as 'undent'

examples with Grafs of Lines of Chars:
  pq -g  # drops leading, trailing, & duplicate Blank Lines; also closes Last Line
  pq -g len  # counts Lines per Graf
  git grep -Hn '^def ' |pq -g |cat -  # print one Graf of Hits per File
  git grep -Hn '^def ' |pq --grafs |cat -  # say '-g' as '--grafs'
  git grep -Hn '^def ' |pq gather |cat -  # say '-g' as 'gather'
  git grep -Hn '^def ' |pq gather spread |cat -  # undo Gather with Spread

examples with File of Lines of Chars:
  pq -f  # no changes, else raises UnicodeDecodeError if not Utf-8, same as 'pq -c'
  pq -f len  # counts Lines, but doesn't need its '-f' mark  # |wc -l
  pq Counter items  # counts Duplicates of Lines, but doesn't reorder the Lines
  pq dict keys  # drops Duplicate Lines but doesn't reorder the Lines
  pq reversed  # forwards Lines in reverse order  # Linux |tac  # Mac |tail -r
  pq set  # drops Duplicate Lines and sorts the rest  # sort |uniq
  pq sorted  # forwards Lines in sorted order
  pq sorted Counter items  # sorts and counts Duplicates  # sort |uniq -c |expand
  pq sorted.reverse  # forwards Lines in reversed sorted order
  pq enumerate  # number each line, up from 0  # |nl -v0 |expand
  pq enumerate.start.1  # number each line, up from 1  # |cat -n |expand
  pq count  # guesses you mean:  pq Counter items
  pq enum  # guesses you mean:  pq enumerate
  pq sort  # guesses you mean:  pq sorted
  pq reverse  # guesses you mean:  pq reversed
  pq -f '[:3],"...",[-2:]'  # first 3 & last 2 Lines, with Ellipsis in between

examples:
  echo abc |pq upper |cat -  # edit the Chars streaming through a Sh Pipe
  echo abc |pq upper  # fill the Os Copy/Paste Clipboard Buffer
  pq lower |cat -  # dump the Os Copy/Paste Clipboard Buffer, but edit the dump
  pq lower  # edit the Chars inside the Os Copy/Paste Clipboard Buffer
  pq --  # closes each Line with b"\n", and closes last Line if not closed
"""

# todo: count Screens, given Width & Height of Screens, infinite Width for No Wrap

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import builtins
import dataclasses
import itertools
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import textwrap
import types
import typing

assert builtins is __builtins__


#
# Declare PyDef's as the Pq Pipe Filters
#


@dataclasses.dataclass
class PyDef:
    """Declare the Args, KwArgs, Defaults, and Result Type of a Python Callable"""

    func: typing.Callable  # callable

    arg_types: list[type]
    kwarg_types: dict[str, type]
    arg_defaults: dict[int, object]
    kwarg_defaults: dict[str, object]
    result_type: type | types.UnionType


#
# Run well from the Sh Command Line
#


@dataclasses.dataclass
class PqPyArgs:
    """Name the Command-Line Arguments of Pq Py"""

    stdin_isatty: bool
    stdout_isatty: bool

    b: int  # -b, --bytearray
    c: int  # -c, --str
    w: int  # -w, --words
    l: int  # -l, --lines
    g: int  # -g, --grafs
    f: int  # -f, --text

    pydefs: list[PyDef]

    @property
    def typehints(self) -> dict[str, bool]:
        """List the Type Hints parsed as Args of Pq Py"""
        d = dict((k, bool(v)) for (k, v) in vars(self).items() if k in "bcwlgf")
        return d


@dataclasses.dataclass
class Main:
    """Open up a shared workspace for the Code of this Py File"""

    args: PqPyArgs


def main() -> None:
    """Run well from the Sh Command Line"""

    args = parse_pq_py_args()  # often prints help & exits zero
    Main.args = args

    pydefs = args.pydefs

    ibytes = pull_ibytes()
    olist = ibytes_decode(ibytes)

    for pydef in pydefs:
        func = pydef.func

        ilist = olist
        if func is len:
            olist = list(len(_) for _ in ilist)
        elif func is list_join:
            olist = [list_join(ilist, sep=" ")]
        elif func is min:
            olist = [min(ilist)]
        elif func is max:
            olist = [max(ilist)]
        else:
            assert func is textwrap.dedent, func
            olist = list(textwrap.dedent(_) for _ in ilist)

    ilist = olist

    obytes = ilist_encode(ilist)
    obytes_push(obytes)


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
    w_help = "work with Words of Chars, such as 'join'"
    l_help = "work with Lines of Chars, such as 'dent' and 'undent'"
    g_help = "work with Grafs of Lines of Chars, such as 'gather' and 'spread'"
    f_help = "work with File of Lines of Chars, such as 'reversed'"

    sub.add_argument("-b", "--bytearray", action="count", help=b_help)
    sub.add_argument("-c", "--str", action="count", help=c_help)
    sub.add_argument("-w", "--words", action="count", help=w_help)
    sub.add_argument("-l", "--lines", action="count", help=l_help)
    sub.add_argument("-g", "--grafs", action="count", help=g_help)
    sub.add_argument("-f", "--text", action="count", help=f_help)

    verb_help = "verb of the Pq Programming Language:  dedent, join len, max, ..."
    parser.add_argument("pqverbs", metavar="VERB", nargs="*", help=verb_help)

    # Run the Parser

    ns = parser.parse_args()  # often prints help & exits zero

    pydefs = find_pydefs(ns.pqverbs)

    args = PqPyArgs(
        stdin_isatty=sys.stdin.isatty(),
        stdout_isatty=sys.stdout.isatty(),
        b=ns.bytearray,
        c=ns.str,
        w=ns.words,
        l=ns.lines,
        g=ns.grafs,
        f=ns.text,
        pydefs=pydefs,
    )

    args_guess_datatypes(args)  # patches in an Input Datatype, if need be

    typehints = args.typehints
    assert sum(_ for _ in typehints.values()) == 1, (typehints, pydefs)

    # Fall back to print the last Paragraph of Epilog in a frame of 2 Blank Lines

    if sys.argv[1:]:
        return args

    doc = __main__.__doc__
    testdoc = doc[doc.rindex("\n\n") :].strip()
    testdoc = testdoc[testdoc.index("\n") :]
    testdoc = textwrap.dedent(testdoc).strip()

    print()
    print(testdoc)
    print()

    sys.exit(0)

    # often prints help & exits zero


def args_guess_datatypes(args: PqPyArgs) -> None:
    """Work backwords from the Code to guess Input DataType"""

    pydefs = args.pydefs
    typehints = args.typehints

    # Accept explicit Choices unchanged

    if sum(_ for _ in typehints.values()):
        return

    # Define 'bin/pq.py --' to work with Lines of Chars

    if not pydefs:
        vars(args)["l"] = True
        return

        # ducks Flake8:  args.l = True  # E741 ambiguous variable name 'l'

    # Fit to Input DataType

    pydef_0 = pydefs[0]

    arg_types = pydef_0.arg_types
    arg_type = arg_types[0]

    if arg_type is str:
        args.c = True
    elif pydef_0.func.__qualname__ == "list_join":
        args.w = True  # todo: distinguish Words from List[Line]
    else:
        assert arg_type is list, (arg_type, pydef_0)
        vars(args)["l"] = True


#
# Pick an Input Source and read it
#


def pull_ibytes() -> bytes:
    """Read Bytes of Input"""

    stdin_isatty = Main.args.stdin_isatty

    assert stat.S_IRWXU == (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)  # chmod u=rwx
    assert stat.S_IRWXG == (stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)  # chmod g=rwx
    assert stat.S_IRWXO == (stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)  # chmod o=rwx

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


#
# Pick an Output Sink and write it
#


def obytes_push(obytes) -> None:
    """Write Bytes of Output"""

    stdout_isatty = Main.args.stdout_isatty

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


#
# Auto-correct Datatype Conflicts
#


def ibytes_decode(ibytes: bytes) -> list:
    """Choose which Datatype of Input to take"""

    args = Main.args

    typehints = args.typehints
    assert sum(_ for _ in typehints.values()) == 1, (typehints, args.pydefs)

    #

    olist: list

    if args.b:  # takes Input as 1 Instance of Bytes
        olist = [ibytes]
        return olist  # -> list[bytes]

    ichars = ibytes.decode()  # may raise UnicodeDecodeError

    if args.c:  # takes Input as 1 Instance of Chars
        olist = [ichars]
        return olist  # -> list[str]

    if args.w:  # takes Input as N Words
        iwords = ichars.split()
        olist = iwords
        return olist  # -> list[Word]

    if args.g:  # takes Input as N Grafs
        igrafs = str_splitgrafs(ichars)  # includes '.splitlines()'
        olist = igrafs
        return olist  # -> list[Graf]

    ilines = ichars.splitlines()

    if args.l:  # takes Input as N Lines
        olist = ilines  # takes Input as Each Line of Chars
        return olist  # -> list[Line]

    if args.f:  # takes Input as 1 Instance of List of N Lines, as if 1 Graf
        olist = [ilines]  # drops Line-Break encodings at 'keepends=False'
        return olist  # -> list[list[Line]]

    #

    assert False, (args,)  # unreached


def ilist_encode(ilist: list) -> bytes:
    """Join what has split, before writing it out, if need be"""

    assert isinstance(ilist, list), [type(ilist)]

    # Forward Empty List as Zero Bytes

    if not ilist:
        obytes = b""
        return obytes

    # Forwards List of Bytes as Byte Lines

    ilist_0 = ilist[0]

    if isinstance(ilist_0, bytes):
        obytes = b"\n".join(ilist) + b"\n"
        return obytes

    # Forwards List of Chars as Char Lines, encoded as Utf-8 Bytes

    if isinstance(ilist_0, str):
        ochars = "\n".join(ilist) + "\n"
        obytes = ochars.encode()  # may raise UnicodeEncodeError
        return obytes

    # Forwards List of Objects as List of Repr of Objects

    rstuff = list(repr(_) for _ in ilist)  # int's, float's, dt.datetime's, etc

    ochars = "\n".join(rstuff) + "\n"
    obytes = ochars.encode()

    return obytes


#
# Amp up Import BuiltIns List
#


def list_join(self: list, /, sep: str = " ") -> str:
    """Catenate the Items of the List, but insert a Sep before each next Item"""

    join = sep.join(self)

    return join

    # may raise TypeError: sequence item ~: expected str instance, ~ found


#
# Amp up Import BuiltIns Str
#


def str_splitgrafs(self: str) -> list[list[str]]:
    """Form List of Lists of Lines, from Wider Lines separated by Empty Lines"""

    lines = self.splitlines()
    grafs = list(list(v) for (k, v) in itertools.groupby(lines, key=bool) if k)

    return grafs


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


def textwrap_dedent_graflines(self: str) -> list[str]:
    """Drop the Blank Lines and the Leftmost Blank Columns"""

    dedent = textwrap.dedent(self)
    strip = dedent.strip()
    splitlines = strip.splitlines()

    return splitlines


#
# Declare the Input Types of many Pq Words
#


def find_pydefs(pqverbs) -> list[PyDef]:
    """Choose between Words of the Pq Programming Language"""

    builtins_defs_names = list(_.split()[1].split("(")[0] for _ in BUILTINS_DEFS_LINES)
    str_defs_names = list(_.split()[1].split("(")[0] for _ in STR_DEFS_LINES)
    words_defs_names = list(_.split()[1].split("(")[0] for _ in WORDS_DEFS_LINES)

    pydefs = list()
    for pqverb in pqverbs:
        if pqverb in builtins_defs_names:
            if pqverb == "len":
                pydef = PyDef(
                    func=builtins.len,
                    arg_types=[list],
                    kwarg_types={},
                    arg_defaults={},
                    kwarg_defaults={},
                    result_type=int,
                )
            elif pqverb == "max":
                pydef = PyDef(
                    func=builtins.max,
                    arg_types=[list],
                    kwarg_types={},
                    arg_defaults={},
                    kwarg_defaults={},
                    result_type=object | None,
                )
            else:
                assert pqverb == "min", (pqverb,)
                pydef = PyDef(
                    func=builtins.min,
                    arg_types=[list],
                    kwarg_types={},
                    arg_defaults={},
                    kwarg_defaults={},
                    result_type=object | None,
                )
        elif pqverb in str_defs_names:
            assert pqverb == "dedent", (pqverb,)
            pydef = PyDef(
                func=textwrap.dedent,
                arg_types=[str],
                kwarg_types={},
                arg_defaults={},
                kwarg_defaults={},
                result_type=str,
            )
        else:
            assert pqverb in words_defs_names, (pqverb,)
            assert pqverb == "join", (pqverb,)
            pydef = PyDef(
                func=list_join,
                arg_types=[list],
                kwarg_types=dict(sep=str),
                arg_defaults={},
                kwarg_defaults=dict(sep=" "),
                result_type=str,
            )

        pydefs.append(pydef)

    return pydefs


BUILTINS_DEFS_CHARS = """
    def len(self: list, /) -> int  # 'builtins.len'
    def max(self: list, /) -> object | None  # 'builtins.max'
    def min(self: list, /) -> object | None  # 'builtins.min'
"""

BUILTINS_DEFS_LINES = list(_ for _ in textwrap_dedent_graflines(BUILTINS_DEFS_CHARS))


STR_DEFS_CHARS = """
    def dedent(self: str, /) -> str
"""

STR_DEFS_LINES = list(_ for _ in textwrap_dedent_graflines(STR_DEFS_CHARS))


WORDS_DEFS_CHARS = """
    def list_join(self: list, /, sep: str = " ") -> str  # 'str.join'
"""

WORDS_DEFS_LINES = list(_ for _ in textwrap_dedent_graflines(WORDS_DEFS_CHARS))


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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
