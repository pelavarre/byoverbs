#!/usr/bin/env python3

r"""
usage: pq [-h] [-b | -c | -w | -l | -g | -f] [VERB ...]

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
  -f, --for-line  work with each Line of Chars, such as 'dent', 'strip', and 'undent'

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
  pq decode  # decodes Py Repr of Bytes as Chars, such as "b'\xC3\x9F'" to 'ß'
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
  pq encode  # encodes Chars as Py Repr of Bytes, such as 'ß' to "b'\xC3\x9F'"
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
  pq splitlines split for len max  # same as '-f split len max', but without '-f'
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

    defname: str  # the '.func.__name__', not the '.func.__qualname__'

    aname_by_int: dict[int, str]
    type_by_int: dict[int, type]
    type_by_kw: dict[str, type]

    default_by_int: dict[int, object]
    default_by_kw: dict[str, object]

    result_type: type | types.UnionType

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
    funcs: list[typing.Callable]

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
    funcs = args.funcs

    ibytes = pull_ibytes()
    olist = ibytes_decode(ibytes)

    for pydef, func in zip(pydefs, funcs):
        defname = pydef.defname

        want = pydef.type_by_int[0].__name__
        got = type(olist[0]).__name__
        sys.stderr.write(f"{defname=} want=list[{want}] got=list[{got}]\n")

        ilist = olist
        olist = list(func(_) for _ in ilist)
        if len(olist) != 1:
            olist = [olist]

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
    w_help = "work with Words of Chars, such as 'join' or 'split set'"
    l_help = "work with Lines of Chars, such as 'max' and 'reversed'"
    g_help = "work with Grafs of Lines, such as 'gather' and 'spread'"
    f_help = "work with each Line of Chars, such as 'dent', 'strip', and 'undent'"

    sub.add_argument("-b", "--bytes", action="count", help=b_help)
    sub.add_argument("-c", "--chars", action="count", help=c_help)
    sub.add_argument("-w", "--words", action="count", help=w_help)
    sub.add_argument("-l", "--lines", action="count", help=l_help)
    sub.add_argument("-g", "--grafs", action="count", help=g_help)
    sub.add_argument("-f", "--for-line", action="count", help=f_help)

    verb_help = "verb of the Pq Programming Language:  dedent, join len, max, ..."
    parser.add_argument("pqverbs", metavar="VERB", nargs="*", help=verb_help)

    # Run the Parser

    ns = parser.parse_args()  # often prints help & exits zero

    pydefs = pqverbs_find_pydefs(ns.pqverbs)
    funcs = pydefs_find_funcs(pydefs)

    args = PqPyArgs(
        stdin_isatty=sys.stdin.isatty(),
        stdout_isatty=sys.stdout.isatty(),
        b=ns.bytes,
        c=ns.chars,
        w=ns.words,
        l=ns.lines,
        g=ns.grafs,
        f=ns.for_line,
        pydefs=pydefs,
        funcs=funcs,
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

    type_by_int = pydef_0.type_by_int
    arg_type = type_by_int[0]

    if arg_type is str:
        args.c = True
    elif pydef_0.defname == "join":
        args.w = True  # todo: distinguish Words from List[Line]
    else:
        assert arg_type is typing.Iterable, (arg_type, pydef_0)
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

    if args.b:  # takes Input as Bytes
        olist = [ibytes]
        return olist  # -> list[bytes]

    ichars = ibytes.decode()  # may raise UnicodeDecodeError

    if args.c:  # takes Input as Chars
        olist = [ichars]
        return olist  # -> list[str]

    if args.w:  # takes Input as Words
        iwords = ichars.split()
        olist = [iwords]
        return olist  # -> list[list[WordStr]]

    if args.g:  # takes Input as Grafs
        igrafs = str_splitgrafs(ichars)  # includes '.splitlines()'
        olist = [igrafs]
        return olist  # -> list[list[Graf]]

    ilines = ichars.splitlines()  # drops Line-Break encodings at 'keepends=False'

    if args.l:  # takes Input as Lines
        olist = [ilines]
        return olist  # -> list[list[Line]]

    if args.f:  # takes Input as For Each Line
        olist = ilines
        return olist  # -> list[Line]

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

    # List each Positional Argument or KeyWord Option, and its Default if present

    # type_by_int: dict[int, type]

    type_by_int: dict[int, type]

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
    )

    # Succeed

    remade = pydef.defline + hash_ + comment
    assert remade == defline, (remade, defline)

    return pydef


def ast_type_eval(typename):
    """Look up a Python Type Name"""

    assert typename in TYPE_BY_NAME.keys(), (typename,)

    type_ = TYPE_BY_NAME[typename]

    return type_


TYPE_BY_NAME = {
    "int": int,
    "list[str]": list[str],
    "object | None": object | None,
    "str": str,
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


def pqverbs_find_pydefs(pqverbs) -> list[PyDef]:
    """Choose between Words of the Pq Programming Language"""

    pqverb_pydef_by_defname = PQVERB_PYDEF_BY_DEFNAME

    pydefs = list()
    for pqverb in pqverbs:
        assert pqverb in pqverb_pydef_by_defname, (pqverb,)
        pydef = pqverb_pydef_by_defname[pqverb]
        pydefs.append(pydef)

    return pydefs


def pydefs_find_funcs(pydefs) -> list[typing.Callable]:
    """Link each PyDef to its corresponding Py Callable"""

    funcs = list()
    for pydef in pydefs:
        defname = pydef.defname

        func: typing.Callable
        if defname == "dedent":
            func = textwrap.dedent
        elif defname == "len":
            func = len
        elif defname == "max":
            func = max
        else:
            assert defname == "join", (defname,)
            func = list_join

        funcs.append(func)

    return funcs


def form_pqverb_pydef_by_defname() -> dict[str, PyDef]:
    """Compile the PyDef's of many Pq Words"""

    iterables_pydefs = list(ast_defline_to_pydef(_) for _ in _ITERABLES_DEFS_LINES)
    chars_pydefs = list(ast_defline_to_pydef(_) for _ in _CHARS_DEFS_LINES)
    words_pydefs = list(ast_defline_to_pydef(_) for _ in _WORDS_DEFS_LINES)

    pydefs = list()
    pydefs.extend(iterables_pydefs)
    pydefs.extend(chars_pydefs)
    pydefs.extend(words_pydefs)

    pydef_by_defname = dict()
    for pydef in pydefs:
        defname = pydef.defname
        pydef_by_defname[defname] = pydef

    return pydef_by_defname


_CHARS_DEFS_CHARS = """
    def dedent(self: str, /) -> str  # 'textwrap.dedent'
"""

_CHARS_DEFS_LINES = list(_ for _ in textwrap_dedent_graflines(_CHARS_DEFS_CHARS))


_ITERABLES_DEFS_CHARS = """
    def len(self: typing.Iterable, /) -> int  # 'builtins.len'
    def max(self: typing.Iterable, /) -> object | None  # 'builtins.max'
    def min(self: typing.Iterable, /) -> object | None  # 'builtins.min'
"""

_ITERABLES_DEFS_LINES = list(
    _ for _ in textwrap_dedent_graflines(_ITERABLES_DEFS_CHARS)
)


_WORDS_DEFS_CHARS = """
    def join(self: list[str], /, sep: str = " ") -> str  # 'str.join'
"""

_WORDS_DEFS_LINES = list(_ for _ in textwrap_dedent_graflines(_WORDS_DEFS_CHARS))


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
