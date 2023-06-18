#!/usr/bin/env python3

r"""
usage: pq.py [-h] [-n] [WORD ...]

edit the Os Copy/Paste Buffer else other Stdin/ Stdout

positional arguments:
  WORD              word of the Pq Programming Language

options:
  -h, --help        show this help message and exit
  -n, --open-ended  don't close the last output line

quirks:
  often does the same work as ' |jq'

words:
  _ dent casefold expandtabs lower lstrip rstrip strip upper  # [Line] -> [Line]
  encode len repr  # [Line] -> [Lit] -> [Line]
  dedent enumerate join reversed sorted split  # ... -> Line|[IndexedLine|Line|Word]
  decode encode eval len keys repr values  # ... -> [Any|Bytes|Index|Int|Key|Line|Value]

examples:

  bind 'set enable-bracketed-paste off' 2>/dev/null; unset zle_bracketed_paste
  setopt interactive_comments

  echo abcde |pq _ |cat -  # abcdef
  echo abcde |pq dent |pq dent |cat -  # the 14 Chars '        abcde\n'
  echo abcde |pq len |cat -  # 5

  echo bBß |pq upper |cat -  # BBSS
  echo bBß |pq lower |cat -  # bbß
  echo bBß |pq casefold |cat -  # bbss

  echo "'abc' 'de'"
  echo "'abc' 'de'" |pq eval |cat -
  echo "'abc' 'de'" |pq eval |pq repr |cat -
  echo "'abc' 'de'" |pq eval |pq repr |pq eval |cat -

  echo '    abc d e  ' |pq lstrip |pq repr |cat -  # 'abc d e  '
  echo '    abc d e  ' |pq rstrip |pq repr |cat -  # '    abc d e'
  echo '    abc d e  ' |pq strip |pq repr |cat -  # 'abc d e'

  echo '⌃ ⌥ ⇧ ⌘ # £ ← ↑ → ↓ ⎋ ⋮' |pq encode |cat -
  echo '⌃ ⌥ ⇧ ⌘ # £ ← ↑ → ↓ ⎋ ⋮' |pq encode |pq decode |cat -

  echo a b c |pq split |cat -
  ls |pq join |cat -

  ls -1 |pq enumerate |cat -  # numbered up from '0 ', like '|nl -v0 |expand' does
  ls -1 |cat -n |pq repr |cat -  # numbered up from '1\t'
  ls -1 |cat -n |pq expandtabs |pq repr |cat -  # numbered up from '1  '

  ls -1 -F -rt
  ls -1 -F -rt |pq reversed && pbpaste  # show Reversed
  ls -1 -F -rt |pq sorted && pbpaste  # show Sorted
  ls -1 -F -rt |pq sorted && pq enumerate && pbpaste  # show Numbered and Sorted

  ls -1 -F -rt |pq so && pq nu && pbpaste  # ok if 'so' 'nu' is only Sort & Enumerate

  git grep -Hn '^def ' |pq gather |less -FIRX  # print one Paragraph of Hits per File
  git grep -Hn '^def ' |pq gather |pq spread |cat -  # undo Gather with Spread

  pq help  # fails, but dumps vocabulary
"""

# code reviewed by people, and by Black and Flake8

# todo: --strict to reject abbreviated keywords, such as 'sort' for 'sorted'


import argparse
import ast
import io
import json
import subprocess
import sys
import textwrap

import byotools as byo


#
# Edit the Os Copy/Paste Buffer else other Stdin/ Stdout
#


def main():
    """Edit the Os Copy/Paste Buffer else other Stdin/ Stdout"""

    args = parse_pq_args()  # often prints help & exits zero
    words = args.words

    func = pq_compile_to_func(words)

    with PyQueryVm(open_ended=args.open_ended) as pqv:
        main.pqv = pqv

        func()


def parse_pq_args():
    """Take Words from the Sh Command Line into Pq Py"""

    assert argparse.ZERO_OR_MORE == "*"

    parser = byo.ArgumentParser()

    words_help = "word of the Pq Programming Language"
    parser.add_argument("words", metavar="WORD", nargs="*", help=words_help)

    n_help = "don't close the last output line"
    parser.add_argument("-n", "--open-ended", action="count", help=n_help)

    args = parser.parse_args()  # often prints help & exits zero

    return args


#
# Define the Runtime Context of the Pq Programming Language
#


class PyQueryVm:
    """Define the Runtime Context of the Pq Programming Language"""

    def __init__(self, open_ended):
        self.open_ended = open_ended

    def __enter__(self):
        """Sponge up the Stdin of Chars, and open up the Stdout of Chars"""

        # Sponge in the Stdin of Chars

        if not sys.stdin.isatty():
            alt_ichars = sys.stdin.read()
        else:
            alt_ichars = byo.subprocess_run_stdout("pbpaste", errors="surrogateescape")

        ichars = alt_ichars
        if alt_ichars and not alt_ichars.endswith("\n"):
            ichars = alt_ichars + "\n"  # like for:  |pq dedent

        stdin = io.StringIO(ichars)

        sys.stdin = stdin

        # Sponge out the Stdout of Chars

        stdout = io.StringIO()

        self.stdout = stdout
        sys.stdout = stdout

        # Succeed

        return self

    def __exit__(self, *exc_info):
        """Sponge up the Stdin of Chars, and open up the Stdout of Chars"""

        open_ended = self.open_ended
        stdout = self.stdout

        # Revert to Sys Stdin Stdout, for debug etc

        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__

        # Read what we wrote

        offset_0 = 0
        whence_set = io.SEEK_SET
        stdout.seek(offset_0, whence_set)

        # Forward what we wrote

        alt_ochars = stdout.read()

        ochars = alt_ochars
        if alt_ochars:
            assert alt_ochars.endswith("\n"), repr(ochars[-9:])
            if open_ended:
                ochars = alt_ochars[: -len("\n")]

        if not sys.stdout.isatty():
            sys.stdout.write(ochars)
        else:
            subprocess.run("pbcopy", input=ochars, errors="surrogateescape", check=True)

    def breakpoint(self):
        """Reconnect Stdio till Exit from Breakpoint, and breakpoint once"""

        stdin = sys.stdin
        stdout = sys.stdout

        with open("/dev/tty") as dev_tty:
            sys.stdin = dev_tty
            sys.stdout = sys.__stderr__
            try:
                breakpoint()
            finally:
                sys.stdin = stdin
                sys.stdout = stdout


#
# Define the Pq Programming Language
#


def pq_compile_to_func(words):
    """Compile words of Pq down to a single Func to call"""

    # Make sense of a single Pq Word

    assert words, repr(words)
    assert len(words) == 1, (len(words), words)

    word = words[-1]

    # Overload Word Fragments to mean Exact Match, else StartsWith, else In

    keys = [word]
    if word not in FUNC_BY_WORD.keys():
        keys = list(_ for _ in FUNC_BY_WORD.keys() if _.startswith(word))
        if not keys:
            keys = list(_ for _ in FUNC_BY_WORD.keys() if word in _)
            if not keys:
                keys = [word]

    # Quit in the face of an undefined Word

    key = " ".join(keys)
    assert key in FUNC_BY_WORD.keys(), (key, FUNC_BY_WORD.keys())

    # Pick the code to run inside the Runtime Environment

    func = FUNC_BY_WORD[key]

    return func


#
# Change nothing much
#


def line_print():  # |pq _  # [Line] -> [Line]
    """Close the last Line if not closed"""

    byo.sys_stderr_print(">>> _")

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        print(iline)


#
# Work with Lines of Files
#


def line_casefold():  # |pq casefold  # [Line] -> [Line]
    """Casefold the Chars in each Line"""

    byo.sys_stderr_print(">>> _.casefold()")

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        oline = iline.casefold()
        print(oline)


def line_dent():  # |pq dent  # [Line] -> [Line]
    """Insert 4 Spaces into each Line"""

    byo.sys_stderr_print('>>> "    {}".format(_)')

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        oline = "    {}".format(iline)
        print(oline)


def line_lit_encode():  # |pq encode  # [Line] -> [Bytes]
    """Encode each Line as a Py Bytes Literal"""

    byo.sys_stderr_print('>>> _.encode(errors="surrogatescape")')

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        iline = iline.encode(errors="surrogatescape")
        ilit = str(iline)
        print(ilit)


def line_expandtabs():  # |pq expandtabs  # [Line] -> [Line]
    """Replace the "\t" U+0009 Tab's in each Line with 1 to 8 Spaces"""

    byo.sys_stderr_print(">>> _.expandtabs(tabsize=8)")  # some forbid explicit TabSize

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        oline = iline.expandtabs()
        print(oline)


def line_len_lit():  # |pq len  # [Line] -> [Int]
    """Count the Chars in each Line"""

    byo.sys_stderr_print(">>> len(_)")

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        oint = len(iline)
        olit = str(oint)
        print(olit)


def line_lower():  # |pq lower  # [Line] -> [Line]
    """Lower the Chars in each Line"""

    byo.sys_stderr_print(">>> _.lower()")

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        oline = iline.lower()
        print(oline)


def line_lstrip():  # |pq lstrip  # [Line] -> [Line]
    """Drop the Blanks starting each Line, if any"""

    byo.sys_stderr_print(">>> _.lstrip()")

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        oline = iline.lstrip()
        print(oline)


def line_repr_lit():  # |pq repr  # [Line] -> [Lit]
    """Represent each Line as a Py Str Literal"""

    byo.sys_stderr_print(">>> repr(_)")

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        olit = repr(iline)
        oline = str(olit)
        print(oline)


def line_rstrip():  # |pq rstrip  # [Line] -> [Line]
    """Drop the Blanks ending each Line, if any"""

    byo.sys_stderr_print(">>> _.rstrip()")

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        oline = iline.rstrip()
        print(oline)


def line_strip():  # |pq strip  # [Line] -> [Line]
    """Strip each Line"""

    byo.sys_stderr_print(">>> _.strip()")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(line.strip())


def line_upper():  # |pq upper  # [Line] -> [Line]
    """Upper the Chars in each Line"""

    byo.sys_stderr_print(">>> _.upper()")

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        oline = iline.upper()
        print(oline)


#
# Work with Chars of Lines of Files
#


def file_dedent():  # |pq dedent  # [Line] -> Str -> [Line]
    """Strip the Blank Columns that start every Line of Chars"""

    byo.sys_stderr_print(">>> textwrap.dedent(_)")

    ichars = sys.stdin.read()
    ochars = textwrap.dedent(ichars)
    sys.stdout.write(ochars)


def file_enumerate():  # |pq enumerate  # [Line] -> [IndexedLine]
    """Count off every Line of the Chars, up from 0"""

    byo.sys_stderr_print(">>> enumerate(_)")

    ichars = sys.stdin.read()
    ilines = ichars.splitlines()
    for opair in enumerate(ilines):
        print(*opair)


def file_join():  # |pq join  # [Word] -> Line
    r"""Replace each Line-Ending with one Space"""

    byo.sys_stderr_print(r'''>>> " ".join() + "\n"''')

    ichars = sys.stdin.read()
    ilines = ichars.splitlines()

    ochars = ""
    if ilines:
        ochars = " ".join(ilines) + "\n"

    sys.stdout.write(ochars)


def file_para_gather(sep=":"):  # |pq gather  # [TaggedLine] -> [TaggedPara]
    """Print the Non-Blank Dent plus a Colon to start the Para, then Dent with Spaces"""

    byo.sys_stderr_print(""">>> gather(_, sep=":")""")

    dent = 4 * " "

    ichars = sys.stdin.read()
    ilines = ichars.splitlines()

    opart = None
    for iline in ilines:
        if not iline:  # todo:
            if opart is not None:
                print()
            opart = None

            continue

        iparts = iline.partition(sep)

        ipart = iparts[0]
        if opart != ipart:
            opart = ipart  # may be empty, is not None
            print()
            print(opart + sep)

        print(dent + iparts[-1])

    if opart is not None:
        print()


def file_para_spread(sep):  # |pq spread  # [TaggedPara] -> [TaggedLine]
    """Print the 1 Head Line of each Para as a Non-Blank Dent of each Tail Line"""

    assert sep == ":"
    byo.sys_stderr_print(""">>> spread(_, sep=":")""")

    dent = 4 * " "

    ichars = sys.stdin.read()
    ilines = ichars.splitlines()

    opart = None
    tailed = None
    for iline in ilines:
        if not iline:
            continue

        if iline.startswith(dent):
            tailed = dent
            oline = opart + sep + iline[len(dent) :]
            print(oline)
        else:
            if opart is not None:
                if tailed is None:
                    print(opart)

            iparts = iline.partition(sep)
            opart = iparts[0]
            tailed = None

    if opart is not None:
        if tailed is None:
            print(opart)


def file_reversed():  # |pq reversed  # [Line] -> [OppositeLine]
    """Reverse the Lines"""

    byo.sys_stderr_print(">>> reversed(_)")

    ichars = sys.stdin.read()
    ilines = ichars.splitlines()

    olines = list(reversed(ilines))

    ochars = ""
    if olines:
        ochars = "\n".join(olines) + "\n"

    sys.stdout.write(ochars)


def file_sorted():  # |pq sorted  # [Line] -> [SortedLine]
    """Sort the Lines"""

    byo.sys_stderr_print(">>> sorted(_)")

    ichars = sys.stdin.read()
    ilines = ichars.splitlines()

    olines = list(sorted(ilines))

    ochars = ""
    if olines:
        ochars = "\n".join(olines) + "\n"

    sys.stdout.write(ochars)


def file_split():  # |pq split  # [[Word]] -> [Word]
    """Split each Line into Words"""

    byo.sys_stderr_print(">>> _.split()")

    ichars = sys.stdin.read()
    iwords = ichars.split()

    ochars = ""
    if iwords:
        ochars = "\n".join(iwords) + "\n"

    sys.stdout.write(ochars)


#
# Work with Ast Literal Evals of Chars of Lines of Files
#


def file_eval():  # |pq .  # Dict|[Value] -> Dict|[Value]
    """Clone a Dict or List"""

    byo.sys_stderr_print(">>> ast.literal_eval(_)")

    ichars = sys.stdin.read()
    ieval = ast.literal_eval(ichars)

    olit = json.dumps(ieval, indent=2) + "\n"
    sys.stdout.write(olit)


def file_eval_keys():  # |pq keys  # Dict|[Value] -> [Key|Index]
    """Pick out the Keys of a Dict Lit, else the Indices of a List Lit"""

    byo.sys_stderr_print(">>> _.keys()")

    ichars = sys.stdin.read()
    ieval = ast.literal_eval(ichars)

    if hasattr(ieval, "get"):
        idict = ieval
        olist = list(idict.keys())
    else:
        ilist = ieval
        olist = list(range(len(ilist)))

    olit = json.dumps(olist, indent=2) + "\n"
    sys.stdout.write(olit)


def file_eval_values():  # |pq values  # Dict[Key,Value]|[Value] -> [Value]
    """Pick out the Values of a Dict Lit, else clone a List"""

    byo.sys_stderr_print(">>> _.values()")

    ichars = sys.stdin.read()
    ieval = ast.literal_eval(ichars)

    # main.pqv.breakpoint()  # jitter Sat 17/Jun

    if hasattr(ieval, "get"):
        idict = ieval
        olist = list(idict.values())
    else:
        olist = ieval

    olit = json.dumps(olist, indent=2) + "\n"
    sys.stdout.write(olit)


def line_eval_decode():  # |pq decode  # [Bytes] -> [Line]
    """Decode each Line as a Py Literal of Bytes"""

    byo.sys_stderr_print('>>> _.decode(errors="surrogatescape")')

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        ieval = ast.literal_eval(iline)
        oline = ieval.decode(errors="surrogatescape")
        print(oline)


def line_eval_print():  # |pq eval  # [Lit] -> [Any]
    """Eval each Line as a Py Literal of Bytes"""

    byo.sys_stderr_print(">>> ast.literal_eval(_)")

    ichars = sys.stdin.read()
    for iline in ichars.splitlines():
        ieval = ast.literal_eval(iline)
        oline = str(ieval)
        print(oline)


#
# Map Pq Words to Pq Py Funcs run on Lines and Files
#


FUNC_BY_WORD = {
    ".": file_eval,
    "_": line_print,
    "casefold": line_casefold,
    "decode": line_eval_decode,
    "dedent": file_dedent,
    "dent": line_dent,
    "encode": line_lit_encode,
    "enumerate": file_enumerate,
    "eval": line_eval_print,
    "expandtabs": line_expandtabs,
    "gather": file_para_gather,
    "join": file_join,
    "keys": file_eval_keys,
    "len": line_len_lit,
    "lower": line_lower,
    "lstrip": line_lstrip,
    "repr": line_repr_lit,
    "reversed": file_reversed,
    "rstrip": line_rstrip,
    "sorted": file_sorted,
    "split": file_split,
    "spread": file_para_spread,
    "strip": line_strip,
    "upper": line_upper,
    "values": file_eval_values,
}


#
# Git-track some Tests that worked, when last i tried them
#


# Test extremely small Input Files of Chars

_ = """

  bind 'set enable-bracketed-paste off' 2>/dev/null; unset zle_bracketed_paste

  :

  echo -n |pq _ |hexdump -C
  echo -n |pq dedent |hexdump -C
  echo -n |pq dent |hexdump -C
  echo -n |pq enumerate |hexdump -C
  echo -n |pq expandtabs |hexdump -C
  echo -n |pq gather |hexdump -C
  echo -n |pq join |hexdump -C
  echo -n |pq lstrip |hexdump -C
  echo -n |pq reversed |hexdump -C
  echo -n |pq rstrip |hexdump -C
  echo -n |pq sorted |hexdump -C
  echo -n |pq split |hexdump -C
  echo -n |pq spread |hexdump -C
  echo -n |pq strip |hexdump -C

  echo |pq _ |hexdump -C
  echo |pq dedent |hexdump -C
  echo |pq dent |hexdump -C
  echo |pq enumerate |hexdump -C
  echo |pq expandtabs |hexdump -C
  echo |pq gather |hexdump -C
  echo |pq join |hexdump -C
  echo |pq lstrip |hexdump -C
  echo |pq reversed |hexdump -C
  echo |pq rstrip |hexdump -C
  echo |pq sorted |hexdump -C
  echo |pq split |hexdump -C
  echo |pq spread |hexdump -C
  echo |pq strip |hexdump -C

  echo -n abc |pq _ |hexdump -C
  echo -n abc |pq dedent |hexdump -C
  echo -n abc |pq dent |hexdump -C
  echo -n abc |pq enumerate |hexdump -C
  echo -n abc |pq expandtabs |hexdump -C
  echo -n abc |pq gather |hexdump -C
  echo -n abc |pq join |hexdump -C
  echo -n abc |pq lstrip |hexdump -C
  echo -n abc |pq reversed |hexdump -C
  echo -n abc |pq rstrip |hexdump -C
  echo -n abc |pq sorted |hexdump -C
  echo -n abc |pq split |hexdump -C
  echo -n abc |pq spread |hexdump -C
  echo -n abc |pq strip |hexdump -C

  echo abc |pq _ |hexdump -C
  echo abc |pq dedent |hexdump -C
  echo abc |pq dent |hexdump -C
  echo abc |pq enumerate |hexdump -C
  echo abc |pq expandtabs |hexdump -C
  echo abc |pq gather |hexdump -C
  echo abc |pq join |hexdump -C
  echo abc |pq lstrip |hexdump -C
  echo abc |pq reversed |hexdump -C
  echo abc |pq rstrip |hexdump -C
  echo abc |pq sorted |hexdump -C
  echo abc |pq split |hexdump -C
  echo abc |pq spread |hexdump -C
  echo abc |pq strip |hexdump -C

  echo '[0, 11, 22]' |pq . |cat -
  echo '[0, 11, 22]' |pq keys |cat -
  echo '[0, 11, 22]' |pq values |cat -

  echo '{"a":11, "b":22}' |pq . |cat -
  echo '{"a":11, "b":22}' |pq keys |cat -
  echo '{"a":11, "b":22}' |pq values |cat -

"""


#
# Git-track some Tests that might could start working soon
#


# Test explicit ways of speaking 'wc' across '-w, -m, -c, -l'

_ = """

  pq len  # |awk '{ print length($0) }'  # counts Chars per Line
  pq str splitlines for len  # counts Chars per Line

  pq str split len  # |wc -w  # counts Words in File
  pq str len  # |wc -m  # count Chars in File
  pq str encode len  # |wc -c  # counts Bytes in File
  pq str splitlines len  # |wc -l  # counts Lines in File

"""


# Test more explicit statements of our default:  |pq str splitlines for

_ = """

  pq str splitlines for print  # _
  pq str splitlines for str "\n".join(_)+"\n"  # _

  pq str splitlines for str.casefold  # casefold
  pq str splitlines for str.decode str  # decode
  pq str splitlines for str_dent  # dent
  pq str splitlines for ast_literal.eval bytes encode  # encode
  pq str splitlines for ast_literal.eval str  # eval
  pq str splitlines for str.expandtabs  # expandtabs
  pq str splitlines for str.len str  # len
  pq str splitlines for str.lower  # lower
  pq str splitlines for str.lstrip  # lstrip
  pq str splitlines for str.repr
  pq str splitlines for str.rstrip  # rstrip
  pq str splitlines for str.strip  # strip
  pq str splitlines for str.upper  # upper

"""


# Test explicit overrides of our default:  |pq str splitlines for

_ = """

  pq str textwrap.dedent  # dedent
  pq str splitlines enumerate for print  # enumerate
  pq str eval dict keys list str  # keys, but only for dict str, not for list str
  pq str len  # |wc -m
  pq str splitlines sorted "\n".join(_)+"\n"  # sorted
  pq str eval dict values list str  # values, but only for dict str, not for list str

  echo '{"a": 11, "c": 33, "b": 22}' |pq keys sorted  # as List Lit, but closed
  echo '{"a": 11, "c": 33, "b": 22}' |pq keys sorted join  # as Lines, and closed

  pq join
  pq str splitlines " ".join(_)

  pq split
  pq str split

"""


#
# Run from the Sh Command Line
#

if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
