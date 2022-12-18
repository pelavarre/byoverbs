#!/usr/bin/env python3

r"""
usage: shpong.py [-h]

bounce a U+25A0 $BALL Ping-Pong Ball back & forth between 2 Paddles

options:
  -h, --help  show this help message and exit

quirks:
  $UP and $DOWN or W and S move the Left Paddle
  $DOWN and $UP or J and K move the Right Paddle
  other keys, such as Q or Esc, end the game if pressed 3 times

examples:
  git clone https://github.com/pelavarre/byoverbs.git
  ./demos/shpong.py  # show these examples
  ./demos/shpong.py --  # bounce a \u25A0 Ping-Pong Ball back & forth between 2 Paddles
"""

# code reviewed by people, and by Black and Flake8
# developed by:  F=demos/shpong.py && black $F && flake8 $F && $F --


import __main__
import argparse
import difflib
import os
import random
import shutil
import sys
import textwrap

import keycaps

__main__.__doc__ = __main__.__doc__.replace("$UP", "\N{Upwards Arrow}")  # U+2191
__main__.__doc__ = __main__.__doc__.replace("$DOWN", "\N{Downwards Arrow}")  # U+2193
__main__.__doc__ = __main__.__doc__.replace("$BALL", "\N{Black Square}")  # U+25A0


BALL = "\N{Black Square}"

CSI = "\x1B["

CUP_Y_X = "\x1B[{};{}H"  # Cursor Position (CUP)  # such as "\x1B[1;1H"

DECTCEM_HIDE = "\x1B[?25l"  # Hide away the one cursor
DECTCEM_SHOW = "\x1B[?25h"  # Show the one cursor

SCREEN_ROWS = 24
SCREEN_COLUMNS = 80

BOARD_ROWS = SCREEN_ROWS - 2
BOARD_COLUMNS = SCREEN_COLUMNS - 6

PADDLE_ROWS = 5

PADDLE_Y = (BOARD_ROWS - PADDLE_ROWS) // 2

PADDLE_LEFT_Y_X = [PADDLE_Y, 1 + 1]
PADDLE_RIGHT_Y_X = [PADDLE_Y, SCREEN_COLUMNS - 2]

BALL_Y_X = [BOARD_ROWS // 2, 1 + (BOARD_COLUMNS // 2)]


#
# Run from the Sh command line
#


def main():
    """Run from the Sh command line"""

    parse_shpong_py_args_else()  # prints helps and exits, else returns args

    require_tui()

    run_shpong()


def require_tui():
    """Fail-fast when not run from a Text User Interface (TUI) Terminal"""

    try:
        with keycaps.tui_open(sys.stderr):
            pass
    except Exception as exc:
        sys_stderr_print("Traceback (most recent call last):")
        sys_stderr_print("  ...")
        sys_stderr_print("{}: {}".format(type(exc).__name__, exc))

        sys_stderr_print()
        sys_stderr_print("Run this code inside a Terminal, such as a Windows Dos Box")

        sys.exit(1)


def run_shpong():
    """Bounce a \u25A0 Ping-Pong Ball back & forth between 2 Paddles"""

    # Resize the Terminal Window to fit the Board plus margin

    print("\x1B[8;{};{}t".format(SCREEN_ROWS, SCREEN_COLUMNS))

    #

    with keycaps.tui_open(sys.stderr) as tui:
        tui_print_blank_screen(tui)

        tui.print(DECTCEM_HIDE)
        try:
            try_shpong(tui)
        finally:
            tui.print(DECTCEM_SHOW)


def try_shpong(tui):  # FIXME  # noqa C901 too complex (14
    """Bounce a \u25A0 Ping-Pong Ball back & forth between 2 Paddles"""

    #

    Down = "\N{Downwards Arrow}"
    Left = "\N{Leftwards Arrow}"
    Right = "\N{Rightwards Arrow}"
    Space = "Space"
    Up = "\N{Upwards Arrow}"

    arrow_by_cap = dict()

    arrow_by_cap["A"] = "\N{Leftwards Arrow}"
    arrow_by_cap["W"] = "\N{Upwards Arrow}"
    arrow_by_cap["S"] = "\N{Downwards Arrow}"
    arrow_by_cap["D"] = "\N{Rightwards Arrow}"

    arrow_by_cap["H"] = "\N{Leftwards Arrow}"
    arrow_by_cap["J"] = "\N{Downwards Arrow}"
    arrow_by_cap["K"] = "\N{Upwards Arrow}"
    arrow_by_cap["L"] = "\N{Rightwards Arrow}"

    #

    tui_print_blank_screen(tui)

    #

    inertia_y_x = [0, +1]
    quit_strokes = list()

    while True:

        #

        for paddle_y_x in (PADDLE_LEFT_Y_X, PADDLE_RIGHT_Y_X):
            (y, x) = paddle_y_x
            for row in range(PADDLE_ROWS):
                tui.print(CUP_Y_X.format(1 + y + row, x) + BALL, end="")

        (y, x) = BALL_Y_X
        tui.print(CUP_Y_X.format(1 + y, x) + BALL, end="")

        #

        sys.stdout.flush()

        stroke = tui.readline()

        quit_strokes.append(stroke)  # leaks
        if quit_strokes[-3:] == (3 * [stroke]):

            break

        default_empty = list()
        caps = keycaps.KEYCAP_LISTS_BY_STROKE.get(stroke, default_empty)

        cap = None
        if caps:
            cap = caps[0]  # such as '←' from ('←', '⌃ ⌥ ←', '⌃ ⇧ ←')
            cap = cap.split()[-1]  # such as 'H' from '⌃ ⌥ ⇧ H'

        alt_cap = cap
        if cap in arrow_by_cap.keys():
            alt_cap = arrow_by_cap[cap]

        #

        paddle_index = inertia_y_x[-1] > 0
        if cap in "AWSD":
            paddle_index = False
        if cap in "HJKL":
            paddle_index = True

        if not paddle_index:
            paddle = PADDLE_LEFT_Y_X
        else:
            paddle = PADDLE_RIGHT_Y_X

        #

        for paddle_y_x in (PADDLE_LEFT_Y_X, PADDLE_RIGHT_Y_X):
            (y, x) = paddle_y_x
            for row in range(PADDLE_ROWS):
                tui.print(CUP_Y_X.format(1 + y + row, x) + " ", end="")

        (y, x) = BALL_Y_X
        tui.print(CUP_Y_X.format(1 + y, x) + " ", end="")

        #

        if alt_cap == Up:
            quit_strokes.clear()

            if paddle[0] > 1:
                paddle[0] -= 1

        elif alt_cap == Down:
            quit_strokes.clear()

            if paddle[0] < (BOARD_ROWS + 1 - PADDLE_ROWS):
                paddle[0] += 1

        elif alt_cap == Left:
            quit_strokes.clear()

            inertia_y_x[-1] = -1

        elif alt_cap == Right:
            quit_strokes.clear()

            inertia_y_x[-1] = +1

        elif cap == Space:
            quit_strokes.clear()

            pass

        #

        for tries in range(3):
            assert tries < 2, tries

            (y, x) = BALL_Y_X

            (y_min, y_max) = (1, 1 + BOARD_ROWS - 1)
            (x_min, x_max) = (4, 4 + BOARD_COLUMNS - 2)

            y += inertia_y_x[0]
            x += inertia_y_x[-1]

            y = min(max(y_min, y), y_max)
            x = min(max(x_min, x), x_max)

            if (y, x) != tuple(BALL_Y_X):

                break

            inertia_y_x[-1] = -inertia_y_x[-1]

        if False:
            y = random.randint(y_min, y_max)
            x = random.randint(x_min, x_max)

        BALL_Y_X[::] = (y, x)

    #

    tui.print(CUP_Y_X.format(SCREEN_ROWS + 1, 1), end="")


def tui_print_blank_screen(self):
    """Scroll history away and print a blank screen"""

    size = shutil.get_terminal_size()
    for _ in range(size.lines):
        self.print()

    self.print("\x1B[H" "\x1B[2J", end="")

    sys.stdout.flush()


#
# Take Words from the Sh Command Line into KeyCaps Py
#


def parse_shpong_py_args_else():
    """Print helps for ShPong Py and exit zero or nonzero, else return args"""

    # Drop the '--' Separator if present, even while declaring no Pos Args

    sys_parms = sys.argv[1:]
    if sys_parms == ["--"]:
        sys_parms = list()

    # Parse the Sh Command Line, or show Help

    parser = compile_shpong_argdoc_else()
    args = parser.parse_args(sys_parms)  # prints helps and exits, else returns args
    if not sys.argv[1:]:
        doc = __main__.__doc__

        exit_via_testdoc(doc, epi="examples")  # exits because no args

    # Succeed

    return args


def compile_shpong_argdoc_else():
    """Form an ArgumentParser for ShPong Py"""

    doc = __main__.__doc__
    parser = compile_argdoc(doc, epi="quirks")
    try:
        exit_if_argdoc_ne(doc, parser=parser)
    except SystemExit:
        sys_stderr_print("shpong.py: ERROR: main doc and argparse parser disagree")

        raise

    return parser


#
# Layer over Import ArgParse
#


def compile_argdoc(doc, epi):
    """Form an ArgumentParser, without defining Positional Args and Options"""

    doc_lines = doc.strip().splitlines()
    prog = doc_lines[0].split()[1]  # second word of first line

    doc_firstlines = list(_ for _ in doc_lines if _ and (_ == _.lstrip()))
    description = doc_firstlines[1]  # first line of second paragraph

    epilog_at = doc.index(epi)
    epilog = doc[epilog_at:]

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=True,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    return parser


def exit_if_argdoc_ne(doc, parser):
    """Complain and exit nonzero, unless Arg Doc equals Parser Format_Help"""

    # Fetch the Main Doc, and note where from

    main_doc = __main__.__doc__.strip()
    main_filename = os.path.split(__file__)[-1]
    got_filename = "./{} --help".format(main_filename)

    # Fetch the Parser Doc from a fitting virtual Terminal
    # Fetch from a Black Terminal of 89 columns, not current Terminal width
    # Fetch from later Python of "options:", not earlier Python of "optional arguments:"

    with_columns = os.getenv("COLUMNS")
    os.environ["COLUMNS"] = str(89)
    try:

        parser_doc = parser.format_help()

    finally:
        if with_columns is None:
            os.environ.pop("COLUMNS")
        else:
            os.environ["COLUMNS"] = with_columns

    parser_doc = parser_doc.replace("optional arguments:", "options:")

    parser_filename = "ArgumentParser(...)"
    want_filename = parser_filename

    # Print the Diff to Parser Doc from Main Doc and exit, if Diff exists

    got = main_doc
    want = parser_doc

    diff_lines = list(
        difflib.unified_diff(
            a=got.splitlines(),
            b=want.splitlines(),
            fromfile=got_filename,
            tofile=want_filename,
        )
    )

    if diff_lines:
        sys_stderr_print("\n".join(diff_lines))

        sys.exit(2)  # trust caller to log SystemExit exceptions well


def exit_via_testdoc(doc, epi):
    """Print the last Paragraph of the Main Arg Doc"""

    testdoc = doc
    testdoc = testdoc[testdoc.index(epi) :]
    testdoc = "\n".join(testdoc.splitlines()[1:])
    testdoc = textwrap.dedent(testdoc)
    testdoc = testdoc.strip()

    print()
    print(testdoc)
    print()

    sys.exit(0)


def sys_stderr_print(*args, **kwargs):
    """Work like Print, but write Sys Stderr in place of Sys Stdout"""

    kwargs_ = dict(kwargs)
    if "file" not in kwargs.keys():
        kwargs_["file"] = sys.stderr

    sys.stdout.flush()

    print(*args, **kwargs_)

    if "file" not in kwargs.keys():
        sys.stderr.flush()


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/keycaps.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
