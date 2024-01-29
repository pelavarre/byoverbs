#!/usr/bin/env python3

r"""
usage: ptyspawn.py [-h]

wrap a Sh Terminal to delay \r ~ and redefine \r ~ ~ and \r ~ ?

options:
  -h, --help  show this help message and exit

examples:

  demos/ptyspawn.py --help  # show help and exit zero
  demos/ptyspawn.py  # show examples and exit zero
  demos/ptyspawn.py --  # wrap a Sh Terminal to mess with \r ~

    \r ~  work like \r ~, but delay the ~ till the next Char after
    \r ~ ~  work like \r ~
    \r ~ ?  show help
"""

# code reviewed by people and by Black, Flake8, & Flake8-Import-Order


import __main__
import os
import pty
import shlex
import sys
import textwrap


default_sh = "sh"
ENV_SHELL = os.getenv("SHELL", default_sh)


PATCH_DOC = """
    Supported escape sequences:
    ~?  - this message
    ~~  - send the escape character by typing it twice
    (Note that escapes are only recognized immediately after newline.)
"""

# Classic Ssh defines ~? to print these Chars of Help, and more


def main() -> None:
    """Run from the Sh Command Line"""

    # Print help & exit, except at:  demos/ptyspawn.py --

    doc = __main__.__doc__.strip()
    testdoc = textwrap.dedent(doc.partition("examples:\n")[-1]).strip()

    shargs = sys.argv[1:]
    if not shargs:
        print("\n" + testdoc + "\n")
        sys.exit(0)
    if shargs != "--".split():
        print(doc)
        sys.exit(0)

    # Wrap the I/O of a Sh Terminal

    shline = ENV_SHELL
    argv = shlex.split(shline)

    pty_spawn_argv(argv)


def pty_spawn_argv(argv) -> None:
    """Wrap the I/O of a Sh Terminal"""

    patch_doc = textwrap.dedent(PATCH_DOC).strip()

    ij = [ord("."), ord("\r")]

    def fd_patch_output(fd):
        """Take the chance to patch Output, or don't"""

        obytes = os.read(fd, 0x400)

        return obytes

    def fd_patch_input(fd):
        """Take the chance to patch Input, or don't"""

        # Pull Bytes till some Bytes found to forward

        while True:
            ibytes = os.read(fd, 0x400)

            # Consider 3 Bytes at a time

            pbytes = bytearray()
            for k in ibytes:
                (i, j) = ij
                ij[::] = [j, k]

                # Take the 2 Bytes b"\r~" to mean hold the b"~" till next Byte

                if (j, k) == (ord("\r"), ord("~")):
                    continue

                # Take the 3 Bytes b"\r~~" to mean forward the 2 Bytes b"\r~"

                if (i, j) == (ord("\r"), ord("~")):
                    if (i, j, k) == (ord("\r"), ord("~"), ord("~")):
                        pbytes.append(k)
                        continue

                    # Take the 3 Bytes b"\r~?" to mean explain thyself

                    if (i, j, k) == (ord("\r"), ord("~"), ord("?")):
                        print("~?", end="\r\n")
                        print("\r\n".join(patch_doc.splitlines()), end="\r\n")
                        continue

                    # Else forward the b"~" of b"\r~" with the next Byte

                    pbytes.append(j)
                    pbytes.append(k)
                    continue

                # Else forward the Byte immediately

                pbytes.append(k)

            # Return Bytes to forward them

            if pbytes:
                return pbytes

    pty.spawn(argv, master_read=fd_patch_output, stdin_read=fd_patch_input)

    # compare 'def read' patching output for https://docs.python.org/3/library/pty.html


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/ptyspawn.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
