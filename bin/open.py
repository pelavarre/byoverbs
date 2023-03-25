#!/usr/bin/env python3

"""
usage: open.py [-h] [ADDRESS]

tell the browser to visit a web address, or just split it into parts

positional arguments:
  ADDRESS     some web address, maybe ending in '/' plus '?' '#' '&' '=' pairs

options:
  -h, --help  show this help message and exit

quirks:
  goes well with Curl
  takes '--' to mean take web addresses from lines of Stdin till Eof

examples:

  open.py  # show these examples and exit
  open.py --h  # show this help message and exit
  open.py --  # take Web Addresses from lines of Stdin till Eof

  open https://docs.google.com/document/d/1YfkPxiJjVJXvf4G1-Ql6-IgxE7J22eEG2JzueNjl2T4

  : for such web addresses as

    http://jira/issues/?jql=text%20~%20%27Hobbit%27
    http://wiki.example.com/display/main/Welcome
    https://docs.google.com/document/d/1YfkPxiJjVJXvf4G1-Ql6-IgxE7J22eEG2JzueNjl2T4
    https://twitter.com/pelavarre/status/1543460479720337409?s=20
    https://www.google.com/search?tbm=isch&q=Carelman+Everyday

"""
# todo: look for '#' over '?' examples of key-value pairs, but found outside the Vpn's


import os
import pdb
import re
import urllib.parse

import byotools as byo

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace  # needed till Jun/2018 Python 3.7


def main():
    """Run from the Sh Command Line"""

    args = parse_open_py_args_else()  # prints helps and exits, else returns args

    if args.address is not None:
        address = args.address

        address_print_nears(address)

    else:

        byo.sys_stdin_prompt_if()
        print()
        while True:
            address = byo.sys_stdin_readline_else()

            address_print_nears(address)


def parse_open_py_args_else():
    """Print helps for Open Py and exit zero or nonzero, else return args"""

    parser = compile_open_py_argdoc_else()

    byo.sys_exit_if_testdoc()  # prints examples & exits if no args

    byo.sys_exit_if_argdoc()  # prints help lines & exits if "--h" arg, but ignores "-h"

    args = parser.parse_args()  # prints helps and exits, else returns

    return args


def compile_open_py_argdoc_else():
    """Print helps for Open Py and exit zero or nonzero, else return args"""

    parser = byo.compile_argdoc()

    parser.add_argument(
        "address",
        metavar="ADDRESS",
        nargs="?",
        help="some web address, maybe ending in '/' plus '?' '#' '&' '=' pairs",
    )

    try:
        byo.sys_exit_if_argdoc_ne(parser)
    except SystemExit:
        print("jvsketch.py: ERROR: Main Doc and ArgParse Parser disagree")

        raise

    return parser


def address_print_nears(address):
    """Print the paragraphs and then the lines near to an address"""

    alt_address = address.strip()

    # Form the Offers

    (paras, lines) = address_form_nears(address=alt_address)

    # Sort the Offers

    def key(chars):
        distinct = (len(chars), chars)
        return distinct

    alt_paras = sorted(set(paras), key=key, reverse=True)
    alt_lines = sorted(set(lines), key=key, reverse=True)

    # Print the Offers

    if alt_paras:
        for para in alt_paras:
            print()
            print(para)

    if alt_lines:
        print()
        for line in alt_lines:
            print(line)

    if alt_address:
        print()


def address_form_nears(address):  # FIXME  # noqa C901 too complex (13
    """Search out paragraphs and lines near to an address"""

    paras = list()
    lines = list()

    # Offer the original address, unchanged

    lines.append(address)

    # Break the Address into Parts

    splits = urllib.parse.urlsplit(address)  # scheme://netloc/path?query...
    scheme = splits.scheme
    netloc = splits.netloc

    # Shrug off Http S, and WWW Dot, and offer that

    alt_splits = urllib.parse.urlsplit(address)
    if scheme == "https":
        alt_splits = alt_splits._replace(scheme="http")
    if netloc.startswith("www."):
        alt_splits = alt_splits._replace(netloc=byo.str_removeprefix(netloc, "www."))

    alt_unsplit = urllib.parse.urlunsplit(alt_splits)
    if alt_unsplit != address:

        lines.append(urllib.parse.urlunsplit(alt_splits))

        # Also chop off all but the first word of a Local NetLoc Domain Name

        alt_vpn_splits = urllib.parse.urlsplit(alt_unsplit)
        if "." in netloc:
            alt_vpn_netloc = alt_vpn_splits.netloc.split(".")[0]
            alt_vpn_splits = alt_vpn_splits._replace(netloc=alt_vpn_netloc)
            alt_vpn_unsplit = urllib.parse.urlunsplit(alt_vpn_splits)

            lines.append(alt_vpn_unsplit)

    # Only chop off all but the first word of a Local NetLoc Domain Name

    vpn_splits = urllib.parse.urlsplit(address)
    if "." in netloc:
        vpn_netloc = vpn_splits.netloc.split(".")[0]
        vpn_splits = vpn_splits._replace(netloc=vpn_netloc)

        vpn_unsplit = urllib.parse.urlunsplit(vpn_splits)
        # may also drop ':$port', i'm not sure when

        lines.append(vpn_unsplit)

    # Try to give up some Escapes

    basename = os.path.basename(splits.path)
    unquoted_basename = urllib.parse.unquote(basename)
    if unquoted_basename != basename:

        lines.append(unquoted_basename)

        # Title the Address to speak of the Service apart from the Address

        titled_basename = unquoted_basename
        titled_basename = titled_basename.replace("+", " ")
        titled_basename = titled_basename.replace(":", " - ")
        titled_basename = re.sub(r" +", repl=" ", string=titled_basename)
        titled_basename = titled_basename.title()

        lines.append(titled_basename)

    # Offer as Paragraph with Line-Break's

    COUNT_1 = 1

    kv_ch = "?"
    kv_address = address
    kv_splits_query = splits.query  # such as from '...?a=1&b=2'
    if not splits.query:

        kv_ch = "#"
        kv_address = address.replace("#", "?", COUNT_1)
        kv_splits = urllib.parse.urlsplit(kv_address)
        kv_splits_query = kv_splits.query  # such as from '...#a=1&b=2'

    if kv_splits_query:
        root = byo.str_removesuffix(kv_address, suffix=kv_splits_query)

        rstrip = root.rstrip("?")

        # Offer without query

        lines.append(rstrip)

        # Offer without query and without basename, when it looks like G Drive

        if rstrip.endswith("/edit"):
            lines.append(byo.str_removesuffix(rstrip, suffix="/edit"))

        # Offer as Paragraph with Line-Break's

        para_lines = list()
        para_lines.append(rstrip + kv_ch)

        kv_sep = "&"  # todo: more 'kv_sep', such as None
        if ("&" not in kv_splits_query) and (";" in kv_splits_query):
            kv_sep = ";"

        pairs = urllib.parse.parse_qsl(kv_splits_query, separator=kv_sep)
        for (index, pair) in enumerate(pairs):
            (name, value) = pair
            qvalue = urllib.parse.quote(value)
            if not index:
                para_lines.append("    {}={}".format(name, qvalue))
            else:
                para_lines.append("    {}{}={}".format(kv_sep, name, qvalue))

        para = "\n".join(para_lines)
        paras.append(para)

        # Offer the Unsplit Query (i used to know what this is??)

        joinable_query = urllib.parse.urlencode(pairs)
        joinable_splits = urllib.parse.urlsplit(kv_address)
        joinable_splits = joinable_splits._replace(query=joinable_query)
        joinable_unsplit = urllib.parse.urlunsplit(joinable_splits)
        joinable_unsplit = joinable_unsplit.replace("?", kv_ch, COUNT_1)

        lines.append(joinable_unsplit)

    # Offer to drop the trailing "/" Slashes

    for line in list(lines):
        alt_line = line.rstrip("/")
        if line != alt_line:
            lines.append(alt_line)

    # Succeed

    return (paras, lines)


if __name__ == "__main__":
    main()


# todo: 'http://example.com?q=a+b' should come out as 'q=a+b' not 'q=a%20b', true??


# posted into:  https://github.com/pelavarre/byobash/blob/main/bin/open.py
# copied from:  git clone https://github.com/pelavarre/byobash.git


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/open.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
