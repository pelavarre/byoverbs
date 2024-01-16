#!/usr/bin/env python3

r"""
usage: pq [-h] [-q] [--py] [WORD ...]

tell Python to edit the Os Copy/Paste Clipboard Buffer, else other Stdin/ Stdout

positional arguments:
  WORD         word of the Pq Programming Language:  dedent, dent, join, len, max, ...

options:
  -h, --help   show this help message and exit
  -q, --quiet  show less
  --py         show the code without running it

quirks:
  takes Names of Python Funcs and Types as the Words of a Pq Programming Language
  defaults like Awk to 'bytes decode splitlines', unless you say different
  ducks the Shift key and Quotes by taking '.' for '(' or ',', taking '_' for ' ', etc
  replaces:  awk, cut, head, grep, sed, sort, tail, tr, uniq, wc -l, xargs, xargs -n 1
  copied from:  git clone https://github.com/pelavarre/byoverbs.git

examples easier to spell out with Python than with Sh:
  pq  # closes last Line if not closed  # |awk '{print}'
  pq dent  # adds four Spaces to left of each Line  # |sed 's,^,    ,'
  pq help  # shows more examples, specs more quirks  # pq -hhh
  pq len  # counts Chars per Line  # |jq --raw-input length
  pq list join  # tr '\n' ' '
  pq list join replace._  # tr -d ' \n'
  pq list set  # drops Duplicate Lines but doesn't reorder Lines  # unique_everseen
  pq list set list len  # counts Distinct Lines  # |sort -u |wc -l
  pq list shuffled  # shuffles Lines, via 'random.shuffle'
  pq str casefold  # case-fold's the Chars, such as 'ß' to 'ss'  # |pq casefold
  pq str dedent  # removes blank Columns at left, via 'textwrap.dedent'
  pq str dedent strip splitlines strip  # drops Top/ Left/ Right/ Bottom margins
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
import dataclasses
import sys
import textwrap


#
# Git-track the Man Page
#


BIG_DOC = r"""
usage: pq [-h] [-q] [--py] [WORD ...]

tell Python to edit the Os Copy/Paste Clipboard Buffer, else other Stdin/ Stdout

positional arguments:
  WORD         word of the Pq Programming Language:  dedent, dent, join, len, max, ...

options:
  -h, --help   show this help message and exit
  -q, --quiet  show less
  --py         show the code without running it

quirks:
  takes Names of Python Funcs and Types as the Words of a Pq Programming Language
  defaults like Awk to 'bytes decode splitlines', unless you say different
  ducks the Shift key and Quotes by taking '.' for '(' or ',', taking '_' for ' ', etc
  replaces:  awk, cut, head, grep, sed, sort, tail, tr, uniq, wc -l, xargs, xargs -n 1
  copied from:  git clone https://github.com/pelavarre/byoverbs.git

more quirks:
  substitutes the File '~/.ssh/pbpaste', when 'pbpaste' or 'pbcopy' undefined
  doesn't itself update the Os Copy/Paste Clipboard Buffer from the middle of a Sh Pipe
  takes Regular Expression Patterns as in Python, not as as in:  awk, grep, sed, tr
  work its own 'pq' examples correctly, but not yet its own '##' examples  <= todo

related works:
  https://clig.dev - Command Line Interface Guidelines, via Julia Evans (@b0rk)
  https://joeyh.name/code/moreutils/ - including 'sponge' up Stdin & dump it
  https://jqlang.github.io/jq - a fast Json Processor, lightweight & flexible
  https://pypi.org/project/pawk - a Python Line Processor, a la Awk
  https://redis.io/ - Key-Value Pairs in Memory, but with a friendly Cli

examples of running Python for each Line:
  pq  # closes last Line if not closed  # |awk '{print}'
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
  pq list join  # tr '\n' ' '
  pq list join replace._  # tr -d ' \n'
  pq list reversed  # forwards Lines in reverse order  # Linux |tac  # Mac |tail -r
  pq list set  # drops Duplicate Lines but doesn't reorder Lines  # unique_everseen
  pq list set list len  # counts Distinct Lines  # |sort -u |wc -l
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
  pq str dedent strip splitlines strip  # drops Top/ Left/ Right/ Bottom margins
  pq str set join.  # drops Duplicate Chars but doesn't reorder Chars  # unique_everseen
  ## str set.key=casefold join.  # drops Duplicate Chars ignoring Case, doesn't reorder
  pq str encode  # encodes Chars as Bytes, such as 'ß' to "b'\xC3\x9F'"
  pq str fromhex  # encodes Hex to Bytes, via 'bytes.fromhex', such as 'C39F' to 'ß'
  pq str strip  # removes blank Rows above and below

examples of running Python slightly faster for Chars, vs running for Lines:
  pq str casefold  # case-fold's the Chars, such as 'ß' to 'ss'  # |pq casefold
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

ALT_BIG_DOC = r"""
examples easier to spell out with Python than with Sh:
"""  # accept these Lines found in '__main__.__doc__' but not in BIG_DOC

# todo: bold for Big Doc to Stdout


#
# Run well from the Sh Command Line
#


@dataclasses.dataclass
class PqPyArgs:
    """Name the Command-Line Arguments of Pq Py"""

    quiet: int | None
    py: bool | None

    hints: list[str]  # given as Pq Words on the Sh Line

    steps: list[str]  # auto-completed from the Hints


@dataclasses.dataclass
class Main:
    """Open up a shared workspace for the Code of this Py File"""

    args: PqPyArgs


#
# Run well from the Sh Command Line
#


def main() -> None:
    """Run well from the Sh Command Line"""

    args = parse_pq_py_args()  # often prints help & exits zero
    Main.args = args

    py = steps_to_py(args.steps)
    if args.py:
        print(py)
    else:
        exec(py)


def parse_pq_py_args() -> PqPyArgs:
    """Parse the Command-Line Arguments of Pq Py"""

    (main_doc, lil_doc, big_doc) = fetch_pq_py_docs()

    # Form the Arg Parser

    prog = "pq"
    description = "edit the Os Copy/Paste Clipboard Buffer, else other Stdin/ Stdout"
    epilog = main_doc[main_doc.index("quirks:") :]  # takes Quirks as 1st Line of Epilog

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=False,  # undefines '--help' at '.parse_args'
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    help_help = "show this help message and exit"
    quiet_help = "show less"
    py_help = "show the code without running it"

    parser.add_argument("-h", "--help", action="count", help=help_help)
    parser.add_argument("-q", "--quiet", action="count", help=quiet_help)
    parser.add_argument("--py", action="count", help=py_help)

    assert argparse.ZERO_OR_MORE == "*"
    pqwords_help = "word of the Pq Programming Language:  dedent, join len, max, ..."
    parser.add_argument("pqwords", metavar="WORD", nargs="*", help=pqwords_help)

    # Parse the Args, else print help & exit zero

    ns = parser.parse_args()  # often prints help & exits zero or nonzero

    # Often print help & exit zero

    doc_else = None
    if not sys.argv[1:]:
        doc_else = lil_doc
    elif ns.help:
        if ns.help < 3:
            parser.print_help()
            sys.exit(0)
        doc_else = big_doc
    elif "help" in ns.pqwords:
        doc_else = big_doc

    if doc_else:
        print(doc_else)
        sys.exit(0)

    # Auto-complete the given List of Pq Words

    hints = ns.pqwords
    steps = hints_auto_complete(hints)

    if steps != hints:  # rarely False
        join = " ".join(steps)
        if not ns.quiet:
            print(f"+ pq {join}", file=sys.stderr)

    # Collect up the Parsed Args

    args = PqPyArgs(
        quiet=ns.quiet,
        py=ns.py,
        hints=hints,
        steps=steps,
    )

    # Succeed

    return args

    # often prints help & exits zero


def fetch_pq_py_docs() -> tuple[str, str, str]:
    """Fetch the Main, the Lil, and the Big Docs of Pq Py"""

    # Define '-hhh' as print the bigger DocString from middle of this File

    big_doc = BIG_DOC
    alt_big_doc = ALT_BIG_DOC

    # Define '--help' as print the DocString from top of Main Py File

    main_doc = __main__.__doc__
    main_doc = main_doc.strip()

    big_lines = big_doc.splitlines()
    alt_big_lines = alt_big_doc.splitlines()
    for main_line in main_doc.splitlines():
        if main_line not in alt_big_lines:
            assert main_line in big_lines, (main_line, len(big_lines))

    # Define no Sh Args as print the last Graf of the Main Doc, but framed

    lil_doc = main_doc  # todo: each LIL_DOC Line consistent with BIG_DOC?
    lil_doc = lil_doc[lil_doc.rindex("\n\n") :].strip()  # splitgrafs [-1]
    assert lil_doc[0] != " "  # requires not-dented
    lil_doc = lil_doc[lil_doc.index("\n") :]  # drops first Line
    lil_doc = textwrap.dedent(lil_doc).strip()
    lil_doc = "\n" + lil_doc + "\n"  # frames inside two Blank Lines

    # Succeed

    return (main_doc, lil_doc, big_doc)


#
# Auto-complete a given List of Pq Words
#


def hints_auto_complete(hints: list[str]) -> list[str]:
    """Auto-complete a given List of Pq Words"""

    picks = list(hints)

    source = picks_pop_0_source(picks)
    heads = picks_pop_0_heads(picks)

    sink = picks_pop_sink(picks)
    tails = picks_pop_tails(picks)

    steps = [source] + heads + [":"]
    steps += picks
    steps += [":"] + tails + [sink]

    return steps


def picks_pop_0_source(picks: list[str]) -> str:
    """Pop one or zero Picks from the front, return a Source of Bytes"""

    stdin_isatty = sys.stdin.isatty()

    if picks and (picks[0] in "pbpaste stdin".split()):
        source = picks.pop(0)
    elif not stdin_isatty:
        source = "stdin"
    else:
        source = "pbpaste"

    return source


def picks_pop_0_heads(picks: list[str]) -> list[str]:
    """Pop one or zero Picks from the front, return a Decoder of Bytes"""

    if not picks:
        heads = "decode splitlines".split()
    else:
        pick = picks[0]
        if pick in ": bytes".split():
            picks.pop(0)
            heads = list()
        elif pick in "decode str".split():
            picks.pop(0)
            heads = "decode".split()
        elif pick in "list list[str]".split():
            picks.pop(0)
            heads = "decode splitlines list".split()
        elif pick in "loads".split():
            picks.pop(0)
            heads = "decode loads".split()
        elif pick in "split".split():
            picks.pop(0)
            heads = "decode split".split()
        elif pick in "splitlines".split():
            picks.pop(0)
            heads = "decode splitlines".split()
        else:
            heads = "decode splitlines".split()

    return heads


def picks_pop_sink(picks: list[str]) -> str:
    """Pull one or zero Picks from the back, return a Sink of Bytes"""

    stdout_isatty = sys.stdout.isatty()

    if picks and (picks[-1] in "pbcopy stdin".split()):
        sink = picks.pop()
    elif not stdout_isatty:
        sink = "stdout"
    else:
        sink = "pbcopy"

    return sink


def picks_pop_tails(picks: list[str]) -> list[str]:
    """Pull one or zero Picks from the back, return an Encoder of Bytes"""

    tails = list()

    if not picks:
        tails.extend("textify encode".split())
    else:
        pick = picks[-1]
        if pick in ": bytes".split():
            picks.pop()
        elif pick in "encode".split():
            picks.pop()
            tails.extend("encode".split())
        elif pick in "textify str".split():
            picks.pop()
            tails.extend("textify encode".split())
        elif pick in "list list[str]".split():
            pass  # don't 'picks.pop()'
            tails.extend("dumps textify encode".split())
        elif pick in "dumps".split():
            picks.pop()
            tails.extend("dumps textify encode".split())
        elif pick in "join".split():
            picks.pop()
            tails.extend("join textify encode".split())
        elif pick in "textify".split():
            picks.pop()
            tails.extend("textify encode".split())
        else:
            tails.extend("textify encode".split())

    return tails


#
# Compose a Python Program to work Bytes through Steps
#


def steps_to_py(steps) -> str:
    """Compose a Python Program to work Bytes through Steps"""

    # Define the Python Program

    py0 = r"""

        import subprocess

        a_run = subprocess.run("pbpaste", input=b"", stdout=subprocess.PIPE, check=True)
        a = a_run.stdout

        b = a.decode()

        c = b.splitlines()

        #

        #

        d = "\n".join(c) + "\n"
        e = d.encode()
        subprocess.run("pbcopy", input=e, check=True)

    """

    py = textwrap.dedent(py0).strip()

    return py


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
