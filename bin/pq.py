#!/usr/bin/env python3

r"""
usage: pq [-h] [-p | -b | -c | -w | -l] [WORD ...]

edit the Os Copy/Paste Clipboard Buffer, else other Stdin/ Stdout

positional arguments:
  WORD        word of the Pq Programming Language

options:
  -h, --help  show this help message and exit
  -p          take Input as for each Line of Chars (often the default)
  -b          take Input as Bytes
  -c          take Input as Chars
  -l          take Input as Lines of Chars
  -w          take Input as Words of Chars

quirks:
  takes names of Python Funcs to work as the Words of the Pq Programming Language
  chooses for you, often choosing -p, when you don't choose from -b, -c, -w, -l, -p
  works like:  awk, cut, head, grep, sed, sort, tail, tr, uniq, wc, xargs, xargs -n 1
  takes Regular Expression Patterns as in Python, not as as in:  awk, grep, sed, tr
  substitutes the file '~/.ssh/0.pbpaste' File, if 'pbpaste' or 'pbcopy' undefined
  doesn't update the Os Copy/Paste Clipboard Buffer from the middle of a Sh Pipe

related work:
  https://pypi.org/project/pawk
  https://jqlang.github.io/jq

file of bytes:
  pq -b len  # counts Bytes  # | wc -c

file of chars:
  pq -c len  # counts Chars  # | wc -m
  pq -c dedent  # removes blank Columns at left
  pq -c replace.old.new  # show if replacing once runs faster than once per Line
  pq dedent  # guesses you mean:  pq -c dedent
  pq split  # guesses you mean 'pq -c split', same as 'pq -w'  # | xargs -n 1

file of words of chars:
  pq -w  # splits Lines of Words into 1 Word per Line
  pq -w len  # counts Words  # | wc -w
  pq -w join  # joins up one Line of File of Words
  pq join  # guesses you mean 'pq -w join'  # | xargs

file of lines of chars:
  pq -l  # closes last Line if not closed, fails if not Utf-8
  pq -l len  # counts Lines
  pq -l reversed  # forwards Lines in reverse order  # Linux | tac  # Mac | tail -r
  pq -l sorted  # forwards Lines in sorted order
  pq -l sorted.reverse  # forwards Lines in reversed sorted order
  pq -l [:3],"...",[-2:]  # first 3 & last 2 Lines, with Ellipsis in between
  pq -l enumerate expandtabs  # number each line, up from 0  # | nl -v0
  pq -l enumerate.start.1 expandtabs  # number each line, up from 1  # | cat -n |expand
  pq enum  # guesses you mean:  pq -l enumerate.start.0 expandtabs
  pq len  # guesses you mean:  pq -l len  # | wc -l

lines of chars:
  pq len max  # counts max Chars per Line
  pq split len max  # counts max Words per Line
  pq casefold  # case folds Chars in each Line, such as 'ß' to 'ss'
  pq dent  # adds four Spaces to left of each Line  # | sed 's,^,    ,'
  pq if.index.hello  # forward each Line containing a Plain Match
  pq lower  # lowers Chars in each Line, such as 'ß' to itself  # | tr '[A-Z]' '[a-z]'
  pq lstrip  # removes of all Spaces from left of each Line  # | sed 's,^ *,,''
  pq rstrip  # removes of all Spaces from right of each Line  # | sed 's, *$,,''
  pq strip  # removes of all Spaces from left and right of each Line
  pq undent  # removes four Spaces from left of each Line  # | sed 's,^    ,,'
  pq upper  # uppers Chars in each Line, such as 'ß' to 'SS'  # | tr '[a-z]' '[A-Z]'
  pq replace.old.new  # replaces each Plain Match
  pq sub.old.new  # replaces each Reg Ex Match  # | sed 's,o,n,g'
  pq removeprefix.____  # removes four Spaces from left of each Line  # sed 's,^    ,,'

less simple lines of chars:
  pq +._:suffix  # appends a Suffix to right of each Line  # | sed 's,$, :suffix,'
  pq 'if.match.^...$'  # forward each Line of 3 Characters  # | grep '^...$'
  pq replace..prefix:_.1  # inserts Prefix to left of each Line  # | sed 's,^,prefix: ,'
  pq -p dedent  # lets you call Dedent to LStrip each Line, not to Dedent all the Chars

grafs of lines of chars:
  git grep -Hn '^def ' |pq gather |less -FIRX  # print one Graf of Hits per File
  git grep -Hn '^def ' |pq gather spread |less -FIRX  # undo Gather with Spread
  git grep -H '^$' bin/*.py |pq gather |cat -  # Gather nothing when no non-empty Hits

examples:
  echo abc |pq upper |cat -  # edit the Chars streaming through the Sh Pipe
  echo abc |pq upper  # fill the Os Copy/Paste Clipboard Buffer
  pq lower |cat -  # dump an edit of the Os Copy/Paste Clipboard Buffer
  pq lower  # replace the Chars inside the Os Copy/Paste Clipboard Buffer
"""

# todo: gather/spread of Graf's divided by blank lines
# todo: count Screens, given Width & Height of Screens, infinite Width for No Wrap
# todo: hook to eval counts of things, such as Web Search Results

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import argparse
import dataclasses
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import textwrap
import typing


#
# Run well from the Sh Command Line
#


@dataclasses.dataclass
class PqArgs:
    """Name the Command-Line Arguments of Pq Py"""

    stdin_isatty: bool
    stdout_isatty: bool

    p: int
    b: int
    c: int
    w: int
    l: int

    words: list[str]


@dataclasses.dataclass
class Main:
    """Open up a shared workspace for the Code of this Py File"""

    args: PqArgs


def main() -> None:
    """Run well from the Sh Command Line"""

    args = parse_pq_py_args()  # often prints help & exits zero
    Main.args = args

    words = args.words
    funcs = list(word_to_func(_) for _ in words)

    istuff: list[object]
    ostuff: list[object]

    ibytes = pull_ibytes()
    ostuff = ibytes_to_ostuff_by_main_args(ibytes)

    for func in funcs:
        istuff = ostuff
        ostuff = func(istuff)

    istuff = ostuff
    obytes = istuff_to_obytes(istuff)
    obytes_push(obytes)


def parse_pq_py_args() -> PqArgs:
    """Parse the Command-Line Arguments of Pq Py"""

    assert argparse.ZERO_OR_MORE == "*"

    # Form the Parser

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

    sub = parser.add_mutually_exclusive_group()

    p_help = "take Input as for each Line of Chars (often the default)"
    b_help = "take Input as Bytes"
    c_help = "take Input as Chars"
    l_help = "take Input as Lines of Chars"
    w_help = "take Input as Words of Chars"

    sub.add_argument("-p", action="count", help=p_help)
    sub.add_argument("-b", action="count", help=b_help)
    sub.add_argument("-c", action="count", help=c_help)
    sub.add_argument("-w", action="count", help=w_help)
    sub.add_argument("-l", action="count", help=l_help)

    words_help = "word of the Pq Programming Language"
    parser.add_argument("words", metavar="WORD", nargs="*", help=words_help)

    # Run the Parser and return the Parsed Args

    ns = parser.parse_args()  # often prints help & exits zero

    args = PqArgs(
        stdin_isatty=sys.stdin.isatty(),
        stdout_isatty=sys.stdout.isatty(),
        p=ns.b,
        b=ns.b,
        c=ns.c,
        w=ns.w,
        l=ns.l,
        words=ns.words,
    )

    if sys.argv[1:]:
        return args

    # Except default to print the last Paragraph of Epilog in a frame of 2 Blank Lines

    doc = __main__.__doc__
    testdoc = doc[doc.rindex("\n\n") :].strip()
    testdoc = testdoc[testdoc.index("\n") :]
    testdoc = textwrap.dedent(testdoc).strip()

    print()
    print(testdoc)
    print()

    sys.exit(0)

    # often prints help & exits zero


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


def ibytes_to_ostuff_by_main_args(ibytes) -> list[object]:
    """Choose which Datatype of Input to take"""

    args = Main.args

    kinds = [args.b, args.c, args.w, args.l, args.p]
    assert sum(bool(_) for _ in kinds) == 1, (kinds,)

    if args.b:  # takes input as File of Bytes
        ostuff = [ibytes]
        return ostuff

    ichars = ibytes.decode()

    if args.c:  # takes input as File of Chars
        ostuff = [ichars]
        return ostuff

    if args.l:  # takes input as File of Lines of Chars
        ostuff = [ichars.splitlines()]  # go with implicit 'keepends=False'
        return ostuff

    if args.w:  # takes input as File of Words of Chars
        ostuff = ichars.split()
        return ostuff

    ostuff = ichars.splitlines()  # takes input as Each Line of Chars

    return ostuff


def istuff_to_obytes(istuff) -> bytes:
    """Join what has split, before writing it out, if need be"""

    assert isinstance(istuff, list), [type(istuff)]

    # Forward Empty List as Zero Bytes

    if not istuff:
        obytes = b""
        return obytes

    # Forwards List of Bytes as Byte Lines

    istuff_0 = istuff[0]

    if isinstance(istuff_0, bytes):
        obytes = b"\n".join(istuff) + b"\n"
        return obytes

    # Forwards List of Chars as Char Lines, encoded as Utf-8 Bytes

    if isinstance(istuff_0, str):
        ochars = "\n".join(istuff) + "\n"
        obytes = ochars.encode()
        return obytes

    # Forwards List of Objects as List of Repr of Objects

    rstuff = list(repr(_) for _ in istuff)  # int's, float's, dt.datetime's, etc

    ochars = "\n".join(rstuff) + "\n"
    obytes = ochars.encode()

    return obytes


#
# Define the Words of the Pq Programming Language
#


def word_to_func(word) -> typing.Callable:
    """Define the Words of the Pq Programming Language"""

    func_by_word = {
        "dedent": istuff_to_dedent,
        "join": istuff_to_join,
        "len": istuff_to_len,
        "max": istuff_to_max,
        "min": istuff_to_min,
    }

    func = func_by_word[word]

    return func


def istuff_to_dedent(istuff) -> list[str]:
    ostuff = list(textwrap.dedent(_) for _ in istuff)
    return ostuff


def istuff_to_join(istuff) -> list[str]:
    ostuff = [" ".join(istuff)]
    return ostuff


def istuff_to_len(istuff) -> list[int]:
    ostuff = list(len(_) for _ in istuff)
    return ostuff


def istuff_to_max(istuff) -> list[int]:
    ostuff = [max(istuff)]
    return ostuff


def istuff_to_min(istuff) -> list[int]:
    ostuff = [min(istuff)]
    return ostuff


#
# Amp up Import BuiltIns
#


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
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
