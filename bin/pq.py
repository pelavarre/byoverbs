#!/usr/bin/env python3

r"""
usage: pq.py [-h] [WORD ...]

edit the Os Copy/Paste Buffer else other Stdin/ Stdout

positional arguments:
  WORD        word of the Pq Programming Language

options:
  -h, --help  show this help message and exit

quirks:
  always closes the last Line of Chars in output
  often does the same work as ' |jq'

vocabulary:
  _ dent casefold expandtabs lower lstrip rstrip strip upper  # to Lines from Lines
  encode len repr # to Lit Bytes/ Int/ Str from Line
  decode eval # to Line from Lit Line
  dedent enumerate sorted  # to Files of Lines from Files of Lines
  keys values  # to Lit File from Lit File

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

  ls -1 |pq enumerate |cat -  # numbered up from '0 '
  ls -1 |cat -n |pq repr |cat -  # numbered up from '1\t'
  ls -1 |cat -n |pq expandtabs |pq repr |cat -  # numbered up from '1  '

  ls -1 -F -rt
  ls -1 -F -rt |pq sorted && pbpaste  # show Sorted
  ls -1 -F -rt |pq sorted && pq enumerate && pbpaste  # show Numbered and Sorted

  ls -1 -F -rt |pq so && pq nu && pbpaste  # ok if 'so' 'nu' is only Sort & Enumerate

  pq help  # fails, but dumps vocabulary
"""


import argparse
import ast
import io
import pprint
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

    with PyQueryVm() as pqv:
        main.pqv = pqv

        func()


def parse_pq_args():
    """Take Words from the Sh Command Line into Pq Py"""

    assert argparse.ZERO_OR_MORE == "*"

    parser = byo.ArgumentParser()
    words_help = "word of the Pq Programming Language"
    parser.add_argument("words", metavar="WORD", nargs="*", help=words_help)
    args = parser.parse_args()  # often prints help & exits zero

    return args


#
# Define the Runtime Context of the Pq Programming Language
#


class PyQueryVm:
    """Define the Runtime Context of the Pq Programming Language"""

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

        stdout = self.stdout

        # Revert to Sys Stdin Stdout, for debug etc

        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__

        # Read what we wrote

        offset_0 = 0
        whence_set = io.SEEK_SET
        stdout.seek(offset_0, whence_set)

        # Forward what we wrote

        ochars = stdout.read()
        if ochars:
            assert ochars.endswith("\n"), repr(ochars[-9:])

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


def line_skid():
    """Close the last Line if not closed"""

    byo.sys_stderr_print(">>> _")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(line)


#
# Work with Lines of Files
#


def line_casefold():
    """Casefold each Line"""

    byo.sys_stderr_print(">>> _.casefold()")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(line.casefold())


def line_dent():
    """Insert 4 Spaces into every Line of the Chars"""

    byo.sys_stderr_print('>>> "    {}".format(_)')

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print("    {}".format(line))


def line_encode_lit():
    """Encode each Line as a Py Literal of Bytes"""

    byo.sys_stderr_print('>>> _.encode(errors="surrogatescape")')

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(line.encode())


def line_expandtabs():
    """Replace "\t" U+0009 Tab's with 1 to 8 Spaces"""

    byo.sys_stderr_print(">>> _.expandtabs()")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(line.expandtabs())


def line_len_lit():
    """Count Chars in each Line"""

    byo.sys_stderr_print(">>> len(_)")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(len(line))


def line_lower():
    """Lower each Line"""

    byo.sys_stderr_print(">>> _.lower()")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(line.lower())


def line_lstrip():
    """LStrip each Line"""

    byo.sys_stderr_print(">>> _.lstrip()")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(line.lstrip())


def line_repr_lit():
    """RepR each Line"""

    byo.sys_stderr_print(">>> repr(_)")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(repr(line))


def line_rstrip():
    """RStrip each Line"""

    byo.sys_stderr_print(">>> _.rstrip()")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(line.rstrip())


def line_strip():
    """Strip each Line"""

    byo.sys_stderr_print(">>> _.strip()")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(line.strip())


def line_upper():
    """Upper each Line"""

    byo.sys_stderr_print(">>> _.upper()")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        print(line.upper())


#
# Work with Chars of Lines of Files
#


def file_dedent():
    """Strip the Spaces common across every Line of the Chars"""

    byo.sys_stderr_print(">>> textwrap.dedent(_)")

    ichars = sys.stdin.read()

    ochars = ichars
    ochars = textwrap.dedent(ochars)

    sys.stdout.write(ochars)


def file_enumerate():
    """Count off every Line of the Chars, from 0 up"""

    byo.sys_stderr_print(">>> enumerate(_)")

    ichars = sys.stdin.read()
    for index, line in enumerate(ichars.splitlines()):
        print("{} {}".format(index, line))


def file_sorted():
    """Sort the Lines of the Chars"""

    byo.sys_stderr_print(">>> sorted(_)")

    ichars = sys.stdin.read()
    ilines = ichars.splitlines()

    olines = sorted(ilines)
    ochars = ""
    if olines:
        ochars = "\n".join(olines) + "\n"

    sys.stdout.write(ochars)


#
# Work with Ast Literal Evals of Chars of Lines of Files
#


def lit_file_keys():
    """Pick out the Keys of each Value, else the Index up from Zero for it"""

    # main.pqv.breakpoint()  # jitter Sat 17/Jun

    byo.sys_stderr_print(">>> _.keys()")

    ichars = sys.stdin.read()
    e = ast.literal_eval(ichars)

    if hasattr(e, "index"):
        ilist = e
        olist = list(range(len(ilist)))
    else:
        idict = e
        olist = list(idict.keys())

    ochars = pprint.pprint(olist)
    sys.stdout.write(ochars)


def lit_file_values():
    """Pick out the Keys of each Value, else the Index up from Zero for it"""

    byo.sys_stderr_print(">>> _.values()")

    ichars = sys.stdin.read()
    e = ast.literal_eval(ichars)

    if hasattr(e, "index"):
        ilist = e
        olist = list(ilist)
    else:
        idict = e
        olist = list(idict.values())

    ochars = pprint.pprint(olist)
    sys.stdout.write(ochars)


def lit_line_decode_line():
    """Decode each Line as a Py Literal of Bytes"""

    byo.sys_stderr_print('>>> _.decode(errors="surrogatescape")')

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        eval_ = ast.literal_eval(line)
        print(eval_.decode(errors="surrogatescape"))


def lit_line_eval_line():
    """Eval each Line as a Py Literal of Bytes"""

    byo.sys_stderr_print(">>> ast.literal_eval(_)")

    ichars = sys.stdin.read()
    for line in ichars.splitlines():
        eval_ = ast.literal_eval(line)
        print(eval_)


#
# Map Pq Words to Pq Py Funcs run on Lines and Files
#


FUNC_BY_WORD = dict()

FUNC_BY_WORD["_"] = line_skid
FUNC_BY_WORD["casefold"] = line_casefold
FUNC_BY_WORD["decode"] = lit_line_decode_line
FUNC_BY_WORD["eval"] = lit_line_eval_line
FUNC_BY_WORD["dedent"] = file_dedent
FUNC_BY_WORD["dent"] = line_dent
FUNC_BY_WORD["encode"] = line_encode_lit
FUNC_BY_WORD["enumerate"] = file_enumerate
FUNC_BY_WORD["expandtabs"] = line_expandtabs
FUNC_BY_WORD["keys"] = lit_file_keys
FUNC_BY_WORD["len"] = line_len_lit
FUNC_BY_WORD["lower"] = line_lower
FUNC_BY_WORD["lstrip"] = line_lstrip
FUNC_BY_WORD["repr"] = line_repr_lit
FUNC_BY_WORD["rstrip"] = line_rstrip
FUNC_BY_WORD["sorted"] = file_sorted
FUNC_BY_WORD["strip"] = line_strip
FUNC_BY_WORD["upper"] = line_upper
FUNC_BY_WORD["values"] = lit_file_values


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
  echo -n |pq lstrip |hexdump -C
  echo -n |pq rstrip |hexdump -C
  echo -n |pq sort |hexdump -C
  echo -n |pq strip |hexdump -C

  echo |pq _ |hexdump -C
  echo |pq dedent |hexdump -C
  echo |pq dent |hexdump -C
  echo |pq enumerate |hexdump -C
  echo |pq expandtabs |hexdump -C
  echo |pq lstrip |hexdump -C
  echo |pq rstrip |hexdump -C
  echo |pq sort |hexdump -C
  echo |pq strip |hexdump -C

  echo -n abc |pq _ |hexdump -C
  echo -n abc |pq dedent |hexdump -C
  echo -n abc |pq dent |hexdump -C
  echo -n abc |pq enumerate |hexdump -C
  echo -n abc |pq expandtabs |hexdump -C
  echo -n abc |pq lstrip |hexdump -C
  echo -n abc |pq rstrip |hexdump -C
  echo -n abc |pq sort |hexdump -C
  echo -n abc |pq strip |hexdump -C

  echo abc |pq _ |hexdump -C
  echo abc |pq dedent |hexdump -C
  echo abc |pq dent |hexdump -C
  echo abc |pq enumerate |hexdump -C
  echo abc |pq expandtabs |hexdump -C
  echo abc |pq lstrip |hexdump -C
  echo abc |pq rstrip |hexdump -C
  echo abc |pq sort |hexdump -C
  echo abc |pq strip |hexdump -C

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
  pq str splitlines for str join  # _

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
  pq str splitlines sorted join  # sorted
  pq str eval dict values list str  # values, but only for dict str, not for list str

  echo '{"a": 11, "c": 33, "b": 22}' |pq keys sorted  # as List Lit, but closed
  echo '{"a": 11, "c": 33, "b": 22}' |pq keys sorted join  # as Lines, and closed

"""


#
# Run from the Sh Command Line
#

if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/pq.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
