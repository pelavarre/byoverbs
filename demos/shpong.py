#!/usr/bin/env python3

r"""
usage: shpong.py [-h]

bounce a U+25A0 $B Ping-Pong Ball back & forth between 2 Paddles

options:
  -h, --help  show this help message and exit

quirks:
  hold down the Spacebar to keep the Ball moving
  press W and S (or A and D) to move the Left Paddle up and down
  press K and J (or H and L) to move the Right Paddle up and down
  press $L $U $D $R shove on the Ball to go more left, up, down, or right
  press other letters if you want, but only Q ends the game if pressed 3 times
  other keys, such as Esc, do also end the game if pressed 3 times, same as Q does

examples:
  git clone https://github.com/pelavarre/byoverbs.git
  ./demos/shpong.py  # show these examples
  ./demos/shpong.py --  # bounce a \u25A0 Ping-Pong Ball back & forth between 2 Paddles
"""
# $B $D $L $R $U initted far below

# code reviewed by people, and by Black and Flake8
# developed by:  F=demos/shpong.py && black $F && flake8 $F && $F --


import __main__
import argparse
import difflib
import os
import pdb
import random
import string
import sys
import textwrap


import keycaps


if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace  # needed till Jun/2018 Python 3.7


#
# Auto-complete the Help Lines
#


DOC = __main__.__doc__

DOC = DOC.replace("$B", "\N{Black Square}")  # ■ U+25A0
DOC = DOC.replace("$D", "\N{Downwards Arrow}")  # ↓ U+2193
DOC = DOC.replace("$L", "\N{Leftwards Arrow}")  # ← U+2190
DOC = DOC.replace("$R", "\N{Rightwards Arrow}")  # → U+2192
DOC = DOC.replace("$U", "\N{Upwards Arrow}")  # ↑ U+2191

__main__.__doc__ = DOC


#
# Name some Commands of the Terminal Output Magic
#
#   https://en.wikipedia.org/wiki/ANSI_escape_code
#   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
#


CSI = "\x1B["  # macOS Terminal takes "\x1B[" as CSI, doesn't take "\N{CSI}" == "\x9B"

CUP_Y_X = "\x1B[{};{}H"  # Cursor Position (CUP)  # from upper left "\x1B[1;1H"

HOME_AND_WIPE = "\x1B[H" "\x1B[2J"

DECTCEM_CURSOR_HIDE = "\x1B[?25l"  # Hide away the one Cursor on Screen
DECTCEM_CURSOR_SHOW = "\x1B[?25h"  # Show the one Cursor on Screen

OS_PUT_TERMINAL_SIZE = "\x1B[8;{};{}t"  # "CSI 8 t" to Resize Window in Monospace Chars
# such as "\x1B[8;50;89t" for a Black-styled Python Terminal


#
# Spell out some Words of the Terminal Input Magic
#


Space = "Space"

Down = "\N{Downwards Arrow}"
Left = "\N{Leftwards Arrow}"
Right = "\N{Rightwards Arrow}"
Up = "\N{Upwards Arrow}"


#
# Draw decimal digits in the style of
#
#   LED & LCD Seven-Segment Displays, circa 1975
#   https://en.wikipedia.org/wiki/Seven-segment_display
#


#
#   12345   12345   12345   12345   12345   12345   12345   12345   12345   12345
#   1234567_1234567_1234567_1234567_1234567_1234567_1234567_1234567_1234567_12345
#

DIGITS_CHARS = """

    ■ ■ ■       ■   ■ ■ ■   ■ ■ ■   ■   ■   ■ ■ ■   ■       ■ ■ ■   ■ ■ ■   ■ ■ ■
    ■   ■       ■       ■       ■   ■   ■   ■       ■           ■   ■   ■   ■   ■
    ■   ■       ■    ■ ■    ■ ■ ■   ■ ■ ■    ■ ■    ■ ■ ■       ■   ■ ■ ■   ■ ■ ■
    ■   ■       ■   ■           ■       ■       ■   ■   ■       ■   ■   ■       ■
    ■ ■ ■       ■   ■ ■ ■   ■ ■ ■       ■   ■ ■ ■   ■ ■ ■       ■   ■ ■ ■   ■ ■ ■

"""
# "\N{Black Square}"  # ■ U+25A0

DIGITS_CHARS = textwrap.dedent(DIGITS_CHARS).strip()


BALL = "\N{Black Square}"  # ■  # Black in Light Mode, White in Dark Mode


def form_chars_by_digit():
    """Pick each Decimal Digit out of DIGITS_CHARS as 5 Lines of 5 Chars each"""

    chars_by_digit = dict()

    lines = DIGITS_CHARS.splitlines()
    for digit in range(10):

        chars = ""
        for line in lines:
            if chars:
                chars += "\n"

            chars += line[(digit * 8) :][:5]

        chars_by_digit[digit] = chars

    return chars_by_digit


CHARS_BY_DIGIT = form_chars_by_digit()


#
# Bind some Letter Keycaps to Code
#
#   . . ↑ . .    . W . .
#   . ← ↓ → .   . A S D .   H J K L
#
#


ARROW_BY_CAP = dict()

ARROW_BY_CAP["A"] = "\N{Leftwards Arrow}"
ARROW_BY_CAP["W"] = "\N{Upwards Arrow}"
ARROW_BY_CAP["S"] = "\N{Downwards Arrow}"
ARROW_BY_CAP["D"] = "\N{Rightwards Arrow}"

ARROW_BY_CAP["H"] = "\N{Leftwards Arrow}"
ARROW_BY_CAP["K"] = "\N{Upwards Arrow}"
ARROW_BY_CAP["J"] = "\N{Downwards Arrow}"
ARROW_BY_CAP["L"] = "\N{Rightwards Arrow}"

Q_CAP = "Q"

ESC_CAP = "Esc"  # tested by default, not explicitly


#
# Run from the Sh command line
#


def main():
    """Run from the Sh command line"""

    parse_shpong_py_args_else()  # prints helps and exits, else returns args
    keycaps.stdio_has_tui_else(sys.stderr)  # prints helps and exits if no Tui found

    run_shpong()


def run_shpong():
    """Start and stop emulating a Glass Teletype at Stdio"""

    stdio = sys.stderr

    if False:
        flat_up = os.terminal_size(SCREEN_ROWS, SCREEN_COLUMNS)
        keycaps.try_put_terminal_size(stdio, size=flat_up)

    with keycaps.tui_open(stdio) as tui:
        tui.print(DECTCEM_CURSOR_HIDE)
        try:
            tui.screen_wipe_below()
            try_shpong(tui)
        finally:
            tui.print(DECTCEM_CURSOR_SHOW)


def try_shpong(tui):  # FIXME  # noqa C901 too complex (14
    """Bounce a Ball back & forth between 2 Paddles"""

    inertia_y_x = [0, 0]
    inertia_y_x[0] = random.randint(-3, 3)  # FIXME
    inertia_y_x[0] = 0
    inertia_y_x[-1] = +1

    quit_strokes = list()
    while True:

        # Draw one Ball

        (y, x) = BALL_Y_X
        tui.print(CUP_Y_X.format(1 + y, x) + BALL, end="")

        # Draw two Paddles

        for paddle_y_x in (PADDLE_LEFT_Y_X, PADDLE_RIGHT_Y_X):
            (y, x) = paddle_y_x
            for row in range(PADDLE_ROWS):
                tui.print(CUP_Y_X.format(1 + y + row, x) + BALL, end="")

        # Draw two single digit Scores

        for (x, score) in zip(SCORE_XS, SCORES):
            chars = CHARS_BY_DIGIT[score]
            for (index, line) in enumerate(chars.splitlines()):
                tui.print(CUP_Y_X.format(2 + index, x) + line, end="")

        tui.print(CUP_Y_X.format(4, MID_BOARD_X) + BALL, end="")
        tui.print(CUP_Y_X.format(5, MID_BOARD_X) + BALL, end="")

        # Block till Keystroke

        sys.stdout.flush()

        if (SCORES[0] >= 9) or (SCORES[-1] >= 9):

            break

        stroke = tui.readline()

        quit_strokes.append(stroke)  # leaks
        if quit_strokes[-3:] == (3 * [stroke]):

            break

        # Convert to Keycap

        default_empty = list()
        caps = keycaps.KEYCAP_LISTS_BY_STROKE.get(stroke, default_empty)

        cap = None
        if caps:
            cap = caps[0]  # such as '←' from ('←', '⌃ ⌥ ←', '⌃ ⇧ ←')
            cap = cap.split()[-1]  # such as 'H' from '⌃ ⌥ ⇧ H'

        alt_cap = cap
        if cap in ARROW_BY_CAP.keys():
            alt_cap = ARROW_BY_CAP[cap]

        # Clear two Paddles

        for paddle_y_x in (PADDLE_LEFT_Y_X, PADDLE_RIGHT_Y_X):
            (y, x) = paddle_y_x
            for row in range(PADDLE_ROWS):
                tui.print(CUP_Y_X.format(1 + y + row, x) + " ", end="")

        # Clear one Ball

        (y, x) = BALL_Y_X
        tui.print(CUP_Y_X.format(1 + y, x) + " ", end="")

        # Pick which Paddle the shared Arrow Keys would move

        paddle_index = inertia_y_x[-1] > 0
        if cap in "AWSD":
            paddle_index = False
        elif cap in "HJKL":
            paddle_index = True

        if not paddle_index:
            paddle = PADDLE_LEFT_Y_X
        else:
            paddle = PADDLE_RIGHT_Y_X

        # Interpret the Keycap

        if cap in "AWSD" "HJKL":

            if alt_cap in (Up, Left):
                quit_strokes.clear()
                if paddle[0] > 1:
                    paddle[0] -= 1

            elif alt_cap in (Down, Right):
                quit_strokes.clear()
                if paddle[0] < (BOARD_ROWS + 1 - PADDLE_ROWS):
                    paddle[0] += 1

        else:

            if alt_cap == Down:
                quit_strokes.clear()
                inertia_y_x[0] += 1

            elif alt_cap == Left:
                quit_strokes.clear()
                inertia_y_x[-1] -= 1

            elif alt_cap == Right:
                quit_strokes.clear()
                inertia_y_x[-1] += 1

            elif alt_cap == Up:
                quit_strokes.clear()
                inertia_y_x[0] -= 1

            elif alt_cap == Q_CAP:

                continue

            elif alt_cap == Space:
                quit_strokes.clear()

            elif alt_cap in string.ascii_uppercase:
                quit_strokes.clear()

        # Limit Inertia

        inertia_y_x[0] = min(max(inertia_y_x[0], -2), +2)
        inertia_y_x[-1] = min(max(inertia_y_x[-1], -3), +3)

        # Step forward in Time

        for tries in range(3):
            assert tries < 2, (tries, BALL_Y_X, inertia_y_x)

            (y, x) = BALL_Y_X

            (y_min, y_max) = (1, 1 + BOARD_ROWS - 1)
            (x_min, x_max) = (4, 4 + BOARD_COLUMNS - 2)

            y += inertia_y_x[0]
            x += inertia_y_x[-1]

            y = min(max(y, y_min), y_max)
            x = min(max(x, x_min), x_max)

            if (y, x) != tuple(BALL_Y_X):

                break

            if inertia_y_x == [0, 0]:

                break

            score_index = inertia_y_x[-1] > 0
            SCORES[score_index] += 1

            score = SCORES[score_index]
            assert score in CHARS_BY_DIGIT.keys(), score

            inertia_y_x[-1] = -inertia_y_x[-1]

        if False:
            y = random.randint(y_min, y_max)
            x = random.randint(x_min, x_max)

        BALL_Y_X[::] = (y, x)

    #

    tui.print(CUP_Y_X.format(SCREEN_ROWS - 1, 1), end="")


SCREEN_ROWS = 24
SCREEN_COLUMNS = 80

BOARD_ROWS = SCREEN_ROWS - 2
BOARD_COLUMNS = SCREEN_COLUMNS - 6

PADDLE_ROWS = 5

PADDLE_Y = (BOARD_ROWS - PADDLE_ROWS) // 2

PADDLE_LEFT_Y_X = [PADDLE_Y, 1 + 1]
PADDLE_RIGHT_Y_X = [PADDLE_Y, SCREEN_COLUMNS - 2]

MID_BOARD_X = 1 + (BOARD_COLUMNS // 2)

BALL_Y_X = [(BOARD_ROWS // 2) - 1, 1 + (BOARD_COLUMNS // 2)]


SCORE_LEFT_X = BALL_Y_X[-1] - 3 - 5
SCORE_RIGHT_X = BALL_Y_X[-1] + 3 + 1
SCORE_XS = [SCORE_LEFT_X, SCORE_RIGHT_X]

SCORES = [0, 0]


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


# record and replay the game, at 1X or some other X speed
# take Return as Return, not as ⌃ M
# score a point only if Paddle not present - when Ball hits the left edge or top edge
# bounce, don't crash - when Ball hits the top edge or bottom edge
# bounce more convincingly off each Paddle
# bounce differently at each pixel of each Paddle
# timeout Keycaps struck to keep the Ball moving even while no Keycaps struck


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/keycaps.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
