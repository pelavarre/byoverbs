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


BALL = "\N{Black Square}"  # ■ U+25A0  # Black in Light Mode, White in Dark Mode


PADDLE_ROWS = 5  # a vertical line segment of Five "\N{Black Square}"  # ■ U+25A0


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

DIGIT_WIDTH_5 = 5


#
# Bind some Letter Keycaps to Code
#
#   . . ↑ . .    . W . .
#   . ← ↓ → .   . A S D .   H J K L
#
#


HOT_CAPS = "← ↑ ↓ → W A S D H J K L Space".split()


PADDLE_INDEX_BY_CAP = dict()
PADDLE_VECTOR_BY_CAP = dict()

PADDLE_INDEX_BY_CAP["A"] = 0  # Left Paddle
PADDLE_INDEX_BY_CAP["W"] = 0
PADDLE_INDEX_BY_CAP["S"] = 0
PADDLE_INDEX_BY_CAP["D"] = 0

PADDLE_VECTOR_BY_CAP["A"] = -1  # Up
PADDLE_VECTOR_BY_CAP["W"] = -1
PADDLE_VECTOR_BY_CAP["S"] = +1  # Down
PADDLE_VECTOR_BY_CAP["D"] = +1

PADDLE_INDEX_BY_CAP["H"] = -1  # Right Paddle
PADDLE_INDEX_BY_CAP["K"] = -1
PADDLE_INDEX_BY_CAP["J"] = -1
PADDLE_INDEX_BY_CAP["L"] = -1

PADDLE_VECTOR_BY_CAP["H"] = -1  # Up
PADDLE_VECTOR_BY_CAP["K"] = -1
PADDLE_VECTOR_BY_CAP["J"] = +1  # Down
PADDLE_VECTOR_BY_CAP["L"] = +1


VECTOR_YX_BY_CAP = dict()

VECTOR_YX_BY_CAP["←"] = (0, -1)
VECTOR_YX_BY_CAP["↑"] = (-1, 0)
VECTOR_YX_BY_CAP["↓"] = (+1, 0)
VECTOR_YX_BY_CAP["→"] = (0, +1)


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

    if True:
        flat_up = os.terminal_size((80, 24))
        keycaps.try_put_terminal_size(stdio, size=flat_up)

    with keycaps.tui_open(stdio) as tui:

        game = ShPongGame(tui)

        tui.print(DECTCEM_CURSOR_HIDE)
        try:
            tui.screen_wipe_below()
            game.run_till_quit()
        finally:
            tui.print(DECTCEM_CURSOR_SHOW)


class ShPongGame:

    selves = list()

    def __init__(self, tui):
        ShPongGame.selves.append(self)

        self.tui = tui
        self.caps = []  # trace of 'tui.readcap()'

        self.ball_vector_yx = (0, +3)
        self.scores = [0, 0]

        self.mutate_size()

    def mutate_size(self):
        """Resize to fit Terminal now"""

        tui = self.tui

        # Measure the Screen and the Board inside it

        size = tui.shutil_get_terminal_size()
        (columns, rows) = (size.columns, size.lines)

        board_rows = rows - 2  # top margin, bottom margin
        board_columns = columns - 2  # left margin, right margin

        # Place one Ball

        board_mid_y = 1 + (board_rows // 2)
        board_mid_x = 1 + (board_columns // 2)  # todo: why 1 extra column on right ??

        ball_yx = (board_mid_y, board_mid_x)

        ball_y_min = 2
        ball_y_max = ball_y_min + board_rows - 1
        ball_x_min = 2
        ball_x_max = ball_x_min + board_columns - 1

        # Place two Paddles

        paddle_y = (board_rows // 2) - (PADDLE_ROWS // 2) + 1
        paddle_ys = [paddle_y, paddle_y]
        paddle_xs = [2, columns - 1]

        paddle_y_min = 2
        paddle_y_max = (paddle_y_min + board_rows - 1) - (PADDLE_ROWS - 1)

        # Place two single-digit decimal Scores

        colon_y = 4
        colon_x = board_mid_x

        score_left_x = board_mid_x - 3 - DIGIT_WIDTH_5  # 3 columns left of middle
        score_right_x = board_mid_x + 3 + 1  # 3 columns right of middle
        score_xs = [score_left_x, score_right_x]

        # Place Status

        # Mutate Self

        self.rows = rows
        self.columns = columns

        self.ball_y_min = ball_y_min
        self.ball_y_max = ball_y_max
        self.ball_x_min = ball_x_min
        self.ball_x_max = ball_x_max
        self.ball_yx = ball_yx

        self.paddle_y_min = paddle_y_min
        self.paddle_y_max = paddle_y_max
        self.paddle_ys = paddle_ys
        self.paddle_xs = paddle_xs

        self.colon_y = colon_y
        self.colon_x = colon_x

        self.score_xs = score_xs

        self.status_y = rows
        self.status_x = 1
        self.status_width = columns - 1

    def run_till_quit(self):

        tui = self.tui

        caps = self.caps
        scores = self.scores

        while True:

            # Draw one Ball, two Paddles, one Colon, two Scores

            self.board_draw()
            if (scores[0] >= 9) or (scores[-1] >= 9):

                break

            # Read the next Keystroke

            sys.stdout.flush()

            cap = tui.readcap()

            caps.append(cap)
            if caps[-3:] == (3 * [cap]):
                if cap not in HOT_CAPS:

                    break

            # Erase one moving Ball and two moving Paddles

            self.board_erase()

            # Move the Paddles on demand

            if cap in PADDLE_INDEX_BY_CAP.keys():
                self.paddle_move(cap)

            # Speed up the Ball, slow it down, or hold it still

            if cap in VECTOR_YX_BY_CAP.keys():
                self.ball_shove(cap)

            # Step the Ball along

            self.ball_step(cap)

            # Win a point when Ball leaves the Board at left or at right

            self.score_ball(cap)

        status = "".center(self.status_width)
        tui.print(CUP_Y_X.format(self.status_y, self.status_x) + status, end="")

        tui.print(CUP_Y_X.format(self.rows - 2, 1))

    def board_draw(self):
        """Draw one Ball, two Paddles, one Colon, two Scores"""

        caps = self.caps
        tui = self.tui

        # Draw one Ball

        (y, x) = self.ball_yx
        tui.print(CUP_Y_X.format(y, x) + BALL, end="")

        # Draw two Paddles

        for y_x in zip(self.paddle_ys, self.paddle_xs):
            (y, x) = y_x
            for row in range(PADDLE_ROWS):
                tui.print(CUP_Y_X.format(y + row, x) + BALL, end="")

        # Draw the two Dots of one Colon

        tui.print(CUP_Y_X.format(self.colon_y + 0, self.colon_x) + BALL, end="")
        tui.print(CUP_Y_X.format(self.colon_y + 1, self.colon_x) + BALL, end="")

        # Draw two single digit Scores

        for (x, score) in zip(self.score_xs, self.scores):
            chars = CHARS_BY_DIGIT[score]
            for (index, line) in enumerate(chars.splitlines()):
                tui.print(CUP_Y_X.format(2 + index, x) + line, end="")

        # Draw an echo of unwanted input, if any arrived lately

        blank_caps = 3 * [" "]

        echo_caps = blank_caps
        if caps:
            last_cap = caps[-1]
            if last_cap not in HOT_CAPS:
                echo_caps = (3 * [" "]) + caps[-3:]
                echo_caps = echo_caps[-3:]

        echo = " ".join(echo_caps)

        status = echo.center(self.status_width)
        tui.print(CUP_Y_X.format(self.status_y, self.status_x) + status, end="")

    def board_erase(self):
        """Erase one moving Ball and two moving Paddles"""

        tui = self.tui

        # Erase two Paddles

        for paddle_y_x in zip(self.paddle_ys, self.paddle_xs):
            (y, x) = paddle_y_x
            for row in range(PADDLE_ROWS):
                tui.print(CUP_Y_X.format(y + row, x) + " ", end="")

        # Erase one Ball

        (y, x) = self.ball_yx
        tui.print(CUP_Y_X.format(y, x) + " ", end="")

    def paddle_move(self, cap):
        """Move one Paddle up or down, inside its limits"""

        index = PADDLE_INDEX_BY_CAP[cap]
        vector = PADDLE_VECTOR_BY_CAP[cap]

        y = self.paddle_ys[index]

        # Do as told

        y_next = y + vector
        if not (self.paddle_y_min <= y_next <= self.paddle_y_max):

            # Else kick back from Min or Max

            y_next = y - vector
            if not (self.paddle_y_min <= y_next <= self.paddle_y_max):
                assert False, (self.paddle_y_min, y_next, self.paddle_y_max)

        self.paddle_ys[index] = y_next

    def ball_shove(self, cap):
        """Shove the Ball along"""

        vector_yx = VECTOR_YX_BY_CAP[cap]

        (vector_y, vector_x) = self.ball_vector_yx

        vector_y_next = vector_y + vector_yx[0]
        if not (-2 <= vector_y_next <= +2):
            vector_y_next = vector_y - vector_yx[0]
            if not (-2 <= vector_y_next <= +2):
                assert False, (-2, vector_y_next, +2)

        vector_x_next = vector_x + vector_yx[-1]
        if not (-3 <= vector_x_next <= +3):
            vector_x_next = vector_x - vector_yx[-1]
            if not (-3 <= vector_x_next <= +3):
                assert False, (-3, vector_x_next, +3)

        self.ball_vector_yx = (vector_y_next, vector_x_next)

    def ball_step(self, cap):
        """Step the Ball along"""

        (y, x) = self.ball_yx

        (vector_y, vector_x) = self.ball_vector_yx
        (vector_y_next, vector_x_next) = (vector_y, vector_x)

        y_next = y + vector_y_next
        if not (self.ball_y_min <= y_next <= self.ball_y_max):
            vector_y_next = -vector_y

            y_next = min(max(y_next, self.ball_y_min), self.ball_y_max)
            if not (self.ball_y_min <= y_next <= self.ball_y_max):
                assert False, (self.ball_y_min, y_next, self.ball_y_max)

        x_next = x + vector_x_next
        if not (self.ball_x_min <= x_next <= self.ball_x_max):
            vector_x_next = -vector_x

            x_next = min(max(x_next, self.ball_x_min), self.ball_x_max)
            if not (self.ball_x_min <= x_next <= self.ball_x_max):
                assert False, (self.ball_x_min, x_next, self.ball_x_max)

        self.ball_yx = (y_next, x_next)
        self.ball_vector_yx = (vector_y_next, vector_x_next)

    def score_ball(self, cap):
        """Win a point when Ball leaves the Board at left or at right"""

        (_, x) = self.ball_yx

        if x == self.ball_x_min:
            self.scores[-1] += 1
            assert self.scores[-1] <= 9, self.scores[0]
        elif x == self.ball_x_max:
            self.scores[0] += 1
            assert self.scores[0] <= 9, self.scores[0]


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


# todo:  change the score for 1234567890 and - +
# todo:  score a point only if Paddle not present when Ball exits Board left or right
# todo:  recenter the Ball when Ball exits Board left or right
# todo:  bounce differently at each pixel of each Paddle
# todo:  timeout Keycaps struck to keep the Ball moving even while no Keycaps struck
# todo:  record and replay the game, at 1X or some other X speed


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/keycaps.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
