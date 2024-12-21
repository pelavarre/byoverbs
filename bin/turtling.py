#!/usr/bin/env python3

r"""
usage: turtling.py [-h]

draw inside a Terminal Window with Logo Turtles

options:
  -h, --help  show this message and exit
  --yolo      do what's popular now (draws, else chats)

examples:
  turtling.py --h  # shows more help and quits
  turtling.py  # shows some help and quits
  turtling.py --yolo  # does what's popular now (draws, else chats)
"""

# code reviewed by People, Black, Flake8, MyPy, & PyLance-Standard


import __main__
import argparse
import glob
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import textwrap
import traceback
import unicodedata


turtling = sys.modules[__name__]


Turtle_ = unicodedata.lookup("Turtle")  # 🐢 U+01F422


#
# Run well from the Sh Command Line
#


def main() -> None:
    """Run well from the Sh Command Line"""

    parse_turtling_py_args_else()  # often prints help & exits
    if not turtling_client_run():
        if not turtling_server_run():
            assert False, "Turtles Server succeeds or quits, never just fails"


def parse_turtling_py_args_else() -> argparse.Namespace:
    """Take Words in from the Sh Command Line"""

    doc = __main__.__doc__
    assert doc, (doc,)

    parser = doc_to_parser(doc, add_help=True, startswith="examples:")

    yolo_help = "do what's popular now (draws, else chats)"
    parser.add_argument("--yolo", action="count", help=yolo_help)

    ns = parse_args_else(parser)  # often prints help & exits

    return ns

    # often prints help & exits


def doc_to_parser(doc: str, add_help: bool, startswith: str) -> argparse.ArgumentParser:
    """Form an ArgParse ArgumentParser out of the Doc, often the Main Doc"""

    assert doc
    strip = doc.strip()
    lines = strip.splitlines()

    usage = lines[0]
    prog = usage.split()[1]
    description = lines[2]

    epilog = strip[strip.index(startswith) :]

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=add_help,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    return parser


def parse_args_else(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Take Words in from the Sh Command Line, else Print Help and Exit"""

    epilog = parser.epilog
    assert epilog, (epilog,)

    shargs = sys.argv[1:]
    if sys.argv[1:] == ["--"]:  # ArgParse chokes if Sep present without Pos Args
        shargs = list()

    testdoc = textwrap.dedent("\n".join(epilog.splitlines()[1:]))
    if not sys.argv[1:]:
        print()
        print(testdoc)
        print()

        sys.exit(0)  # exits 0 after printing help

    ns = parser.parse_args(shargs)  # often prints help & exits
    return ns

    # often prints help & exits


#
# Run as a Client chatting with Logo Turtles
#


def turtling_client_run() -> bool:
    "Run as a Client chatting with Logo Turtles and return True, else return False"

    try:
        t1 = turtling.Turtle()
    except Exception:
        traceback.print_exc(file=sys.stderr)
        return False

    tc1 = TurtleClient(t1)
    tc1.client_run_till()

    sys.exit()


class TurtlingFifosClient:
    """Write a Request to the Turtling Server, and read a Response"""

    mkfifos: list[str]  # Requests, Responses
    request_index: int

    mkfifos = list()
    request_index = 0

    def find_mkfifos_once(self) -> None:
        """Find a Pair of MkFifo's for to write Requests and read Responses"""

        mkfifos = self.mkfifos
        if mkfifos:
            return

        p1 = "__pycache__/turtling/pid=*/requests.mkfifo"
        p2 = "__pycache__/turtling/pid=*/responses.mkfifo"
        for pattern in (p1, p2):
            pathnames = sorted(glob.glob(pattern), key=lambda _: pathlib.Path(_).stat().st_mtime)
            pathname = pathnames[-1]
            mkfifos.append(pathname)

        pid1 = mkfifos[0].partition("/pid=")[-1].split("/")[0]
        pid2 = mkfifos[0].partition("/pid=")[-1].split("/")[0]
        assert pid1 == pid2, (pid1, pid2)
        pid = pid2

        subprocess.run(shlex.split(f"kill -0 {pid}"), stderr=subprocess.PIPE, check=True)

    def remote_py_eval_to_repr(self, py) -> str:
        """Write a Python Expression to the Turtling Server, and read a Python Repr"""

        mkfifos = self.mkfifos

        index = self.request_index
        self.request_index = index + 1

        # Write Request

        pathname_index_write_chars(mkfifos[0], index=index, chars=py)
        repr_ = pathname_index_read_chars(mkfifos[1], index=index)

        # Succeed

        return repr_


def pathname_index_write_chars(pathname, index, chars) -> None:
    """Write Chars out as an indexed Packet"""

    blank_length = "0x0000_0000_0000_0000"
    masked_text = f"length={blank_length}\n{index=}\nchars={chars}\n"

    repr_text_length = f"0x{len(masked_text):019_X}"  # 19 = 16 Nybbles + 3 "_" Skids
    text = f"length={repr_text_length}\n{index=}\nchars={chars}\n"

    assert len(text) == len(masked_text), (text, masked_text)

    # eprint(text)
    with open(pathname, "w") as w:
        w.write(text)


def pathname_index_read_chars(pathname, index) -> str:
    """Write Chars in as an indexed Request"""

    with open(pathname, "r") as r_fifo:
        text = r_fifo.read()

    # eprint(text)

    lines = text.splitlines()

    assert len(lines) >= 3, (lines, text)

    repr_text_length = lines[0].partition("length=")[-1]
    text_length = int(repr_text_length, 0x10)
    assert text_length == len(text), (text_length, len(text), text)

    repr_index = lines[1].partition("index=")[-1]
    text_index = int(repr_index, 10)
    assert text_index == index, (text_index, index, text)

    start = text.index("\n") + len("\n")
    start = text.index("\n", start) + len("\n")
    chars_eq = text[start:]

    assert chars_eq.startswith("chars="), (chars_eq,)
    assert chars_eq.endswith("\n"), (chars_eq,)

    chars = chars_eq
    chars = chars.removeprefix("chars=")
    chars = chars.removesuffix("\n")

    return chars


turtling_fifo_clients: list[TurtlingFifosClient]
turtling_fifo_clients = list()


class Turtle:
    """Command 1 Sprite of 1 Turtling Server"""

    tfc: TurtlingFifosClient

    def __init__(self) -> None:

        if not turtling_fifo_clients:
            tfc_0 = TurtlingFifosClient()
            tfc_0.find_mkfifos_once()
            turtling_fifo_clients.append(tfc_0)

        tfc = turtling_fifo_clients[-1]
        self.tfc = tfc


class TurtleClient:
    """Chat with Logo Turtles"""

    def __init__(self, t1: Turtle) -> None:
        self.t1 = t1

    def client_run_till(self) -> None:
        """Chat with Logo Turtles"""

        t1 = self.t1

        while True:
            eprint()
            eprint(f"{Turtle_} ", end="")

            sys.stdout.flush()
            sys.stderr.flush()

            readline = sys.stdin.readline()
            if not readline:
                break

            rstrip = readline.rstrip()

            py = rstrip
            repr_ = t1.tfc.remote_py_eval_to_repr(py)
            eval_ = repr_
            # eval_ = eval(repr_)
            print(eval_)


#
# Run as a Server drawing with Logo Turtles
#


def turtling_server_run() -> bool:
    "Run as a Server drawing with Logo Turtles and return True, else return False"

    ts1 = TurtlingServer()
    ts1.server_run_till()

    sys.exit()


class TurtlingServer:

    mkfifos: list[str]  # Requests, Responses

    mkfifos = list()

    def server_run_till(self) -> None:
        """Draw with Logo Turtles"""

        mkfifos = self.mkfifos

        self.create_mkfifos_once()

        eprint("at your service")

        response_index = 0
        while True:
            index = response_index
            response_index = index + 1

            chars = pathname_index_read_chars(pathname=mkfifos[0], index=index)
            repr_ = chars

            print(chars)

            # py = chars
            # eval_ = eval(py)
            # repr_ = repr(eval_)

            pathname_index_write_chars(pathname=mkfifos[-1], index=index, chars=repr_)

    def create_mkfifos_once(self) -> None:
        """Create a Pair of MkFifo's for to read Requests and write Responses"""

        mkfifos = self.mkfifos
        assert not mkfifos, (mkfifos,)

        pid = os.getpid()

        if not os.path.exists("__pycache__"):
            os.mkdir("__pycache__")
        if not os.path.exists("__pycache__/turtling"):
            os.mkdir("__pycache__/turtling")

        dirpathname = f"__pycache__/turtling/pid={pid}"
        if os.path.exists(dirpathname):  # wildly rare
            shutil.rmtree(dirpathname)

        os.mkdir(dirpathname)

        p1 = f"__pycache__/turtling/pid={pid}/requests.mkfifo"
        os.mkfifo(p1)
        mkfifos.append(p1)

        p2 = f"__pycache__/turtling/pid={pid}/responses.mkfifo"
        os.mkfifo(p2)
        mkfifos.append(p2)


#
# Amp up Import BuiltIns
#


def eprint(*args, **kwargs) -> None:
    """Print to Stderr"""

    print(*args, file=sys.stderr, **kwargs)


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/turtling.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
