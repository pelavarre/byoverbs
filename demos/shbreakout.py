#!/usr/bin/env python3

r"""
usage: shbreakout.py [-h]

bounce a U+25A0 $B Breakout Ball above one Paddle through a ceiling of Layers of Bricks

options:
  -h, --help  show this help message and exit

quirks:
  hold down the Spacebar to keep the Ball moving
  run the Ball into a Brick to explode the Brick and bounce the Ball
  press A and D (or W and S) to move the one Paddle left and right, (or H K ad L J)
  press $L $U $D $R shove on the Ball to speed it up or slow it down
  press Esc three times in a row, to end the Game before exploding all the Bricks

examples:
  open https://shell.cloud.google.com/?show=terminal  # if you need another Linux
  git clone https://github.com/pelavarre/byoverbs.git
  printf '\e[8;24;80t'  # play in a conventional 24x80 Terminal Window
  ./demos/shbreakout.py  # show these examples
  ./demos/shbreakout.py --  # bounce a \u25A0 Breakout Ball above one Paddle
"""
# $B $D $L $R $U initted far below

# code reviewed by people, and by Black and Flake8
# developed by:  F=demos/breakout.py && black $F && flake8 $F && $F --


import __main__
import argparse
import difflib
import os
import pdb
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

DECTCEM_CURSOR_HIDE = "\x1B[?25l"  # Hide away the one Cursor on Screen
DECTCEM_CURSOR_SHOW = "\x1B[?25h"  # Show the one Cursor on Screen


#
# Spell out some Words of the Terminal Input Magic
#


Space = "Space"

Down = "\N{Downwards Arrow}"
Left = "\N{Leftwards Arrow}"
Right = "\N{Rightwards Arrow}"
Up = "\N{Upwards Arrow}"


#
# Spell out some Words of the Terminal Input Magic
#


BALL = "\N{Black Square}"  # ■ U+25A0  # Black in Light Mode, White in Dark Mode

BRICK = BALL

BRICK_ROWS = 5  # how many Layers of Brick

PADDLE_COLUMNS = 5  # how many Pixels per Paddle


#
# Bind some Letter Keycaps to Code
#
#   . . ↑ . .    . W . .
#   . ← ↓ → .   . A S D .   H J K L
#
#


HOT_CAPS_SET = set("← ↑ ↓ → W A S D H J K L Space".split())

QUIT_CAPS_SET = list(string.ascii_letters + string.digits) + "Esc".split()
QUIT_CAPS_SET = set(QUIT_CAPS_SET) - set(HOT_CAPS_SET)


PADDLE_VECTOR_BY_CAP = dict()

PADDLE_VECTOR_BY_CAP["A"] = -1  # Left
PADDLE_VECTOR_BY_CAP["W"] = -1
PADDLE_VECTOR_BY_CAP["S"] = +1
PADDLE_VECTOR_BY_CAP["D"] = +1  # Right

PADDLE_VECTOR_BY_CAP["H"] = -1  # Left
PADDLE_VECTOR_BY_CAP["K"] = -1
PADDLE_VECTOR_BY_CAP["J"] = +1
PADDLE_VECTOR_BY_CAP["L"] = +1  # Right


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

    parse_breakout_py_args_else()  # prints helps and exits, else returns args
    keycaps.stdio_has_tui_else(sys.stderr)  # prints helps and exits if no Tui found

    try:
        run_breakout()
    except Exception as exc:
        sys.stderr.write("{}: {}".format(type(exc).__name__, exc))

        breakpoint()

        raise


def run_breakout():
    """Start and stop emulating a Glass Teletype at Stdio"""

    stdio = sys.stderr

    if False:
        flat_up = os.terminal_size((80, 24))
        keycaps.try_put_terminal_size(stdio, size=flat_up)

    with keycaps.tui_open(stdio) as tui:

        game = BreakoutGame(tui)

        tui.print(DECTCEM_CURSOR_HIDE)
        try:
            game.run_till_quit()
        finally:
            tui.print(DECTCEM_CURSOR_SHOW)  # todo:  grow 'tui.__exit__'


class BreakoutGame:

    selves = list()

    def __init__(self, tui):
        BreakoutGame.selves.append(self)

        self.tui = tui
        self.caps = []  # trace of 'tui.cap_from_stroke' of 'tui.readline'

        self.ball_vector_yx = (-1, 0)
        self.brick_yxs_set = set()

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

        ball_y_mid = 1 + (board_rows // 2)
        ball_x_mid = 1 + (board_columns // 2)  # todo: why 1 extra column on right ??

        ball_yx = (rows - 2, ball_x_mid)

        ball_y_min = 1
        ball_y_max = ball_y_min + board_rows - 1
        ball_x_min = 2
        ball_x_max = ball_x_min + board_columns - 1

        # Place one Paddle

        paddle_x_mid = ball_x_mid - (PADDLE_COLUMNS // 2)

        paddle_y = rows - 2
        paddle_x = paddle_x_mid

        paddle_x_min = 2
        paddle_x_max = (paddle_x_min + board_columns - 1) - (PADDLE_COLUMNS - 1)

        # Place the Bricks

        brick_y = BRICK_ROWS

        # Place Status

        status_y = rows
        status_x = 1

        # Mutate Self

        self.rows = rows
        self.columns = columns

        self.ball_y_min = ball_y_min
        self.ball_y_mid = ball_y_mid
        self.ball_y_max = ball_y_max

        self.ball_x_min = ball_x_min
        self.ball_x_mid = ball_x_mid
        self.ball_x_max = ball_x_max

        self.ball_yx = ball_yx

        self.paddle_x_min = paddle_x_min
        self.paddle_x_mid = paddle_x_mid
        self.paddle_x_max = paddle_x_max
        self.paddle_y = paddle_y
        self.paddle_x = paddle_x

        self.brick_y = brick_y

        self.status_y = status_y
        self.status_x = status_x
        self.status_width = columns - 1

        self.entries = None

    def run_till_quit(self):

        tui = self.tui

        caps = self.caps

        while True:

            # Draw one Ball and one Paddle

            self.board_draw()
            if not self.brick_yxs_set:

                break

            # Read the next Keystroke

            sys.stdout.flush()

            stroke = None
            if False:  # not tui.kbhit(timeout=0.100):  # FIXME
                cap = Space
            else:
                stroke = tui.readline()
                cap = tui.cap_from_stroke(stroke)

                if stroke == b"\x03":
                    tui.print(CUP_Y_X.format(self.rows, self.columns))
                    tui.print()
                    tui.__exit__(*sys.exc_info())

                    breakpoint()

                    tui.__enter__()

                    continue

                caps.append(cap)
                if caps[-3:] == (3 * [cap]):
                    if cap in QUIT_CAPS_SET:

                        break

            # Erase one moving Ball and one moving Paddle

            self.board_erase()

            # Move the Paddle on demand

            if cap in PADDLE_VECTOR_BY_CAP.keys():
                self.paddle_move(cap)

            # Speed up the Ball, slow it down, or hold it still

            if cap in VECTOR_YX_BY_CAP.keys():
                self.ball_shove(cap)

            # Step the Ball along

            self.ball_step()

        status = "".center(self.status_width)
        tui.print(CUP_Y_X.format(self.status_y, self.status_x) + status, end="")

        tui.print(CUP_Y_X.format(self.rows - 2, 1))

    def board_draw(self):
        """Draw one Ball and one Paddle - and update Status"""

        paddle_x = self.paddle_x
        paddle_y = self.paddle_y
        tui = self.tui

        # Scroll away history without dropping all of it, and print a blank screen

        if self.entries != tui.entries:
            tui.screen_wipe_below()

        # Draw one Ball

        ball_yx = self.ball_yx
        (ball_y, ball_x) = ball_yx

        ball = keycaps.COLOR_CHARS_FORMAT.format(keycaps._32_GREEN, BALL)

        tui.print(CUP_Y_X.format(ball_y, ball_x) + ball, end="")

        # Draw one Paddle

        for column in range(PADDLE_COLUMNS):
            print_yx = (paddle_y, paddle_x + column)
            if print_yx != ball_yx:
                tui.print(CUP_Y_X.format(*print_yx) + BALL, end="")

        # Draw the Bricks

        self.board_draw_bricks()

        # Draw an echo of unwanted input, if any arrived lately

        self.board_draw_status()

        # Take credit for drawing a complete Board, not just Diffs

        self.entries = tui.entries

    def board_draw_bricks(self):
        """Draw the Bricks"""

        brick_y = self.brick_y
        brick_yxs_set = self.brick_yxs_set
        columns = self.columns
        tui = self.tui

        # Collect the Layers of Bricks, just once per Game

        if not brick_yxs_set:

            for row in range(BRICK_ROWS):
                bricks = (columns - 2) * BRICK
                for brick_x in range(2, 2 + len(bricks)):
                    brick_yx = (brick_y + row, brick_x)
                    brick_yxs_set.add(brick_yx)

        # Draw the collected Layers of Bricks

        if self.entries != tui.entries:

            for row in range(BRICK_ROWS):
                bricks = (columns - 2) * BRICK
                for brick_x in range(2, 2 + len(bricks)):
                    brick_yx = (brick_y + row, brick_x)
                    if brick_yx in brick_yxs_set:
                        tui.print(CUP_Y_X.format(*brick_yx) + BRICK, end="")

    def board_draw_status(self):
        """Draw an echo of unwanted input, if any arrived lately"""

        caps = self.caps
        tui = self.tui

        status = "(press one of "
        status += "A W S D, H K J L, Space, ← ↑ ↓ →, Q)"

        if caps:
            last_cap = caps[-1]
            if last_cap not in HOT_CAPS_SET:
                echo_caps = (3 * [" "]) + caps[-3:]
                echo_caps = echo_caps[-3:]

                echo = " ".join(echo_caps)
                status = echo

        status_chars = status.center(self.status_width)[: self.status_width]
        tui.print(CUP_Y_X.format(self.status_y, self.status_x) + status_chars, end="")

    def board_erase(self):
        """Erase one moving Ball and two moving Paddles"""

        paddle_x = self.paddle_x
        paddle_y = self.paddle_y
        tui = self.tui

        # Erase one Paddle

        for column in range(PADDLE_COLUMNS):
            tui.print(CUP_Y_X.format(paddle_y, paddle_x + column) + " ", end="")

        # Erase one Ball

        (ball_y, ball_x) = self.ball_yx
        tui.print(CUP_Y_X.format(ball_y, ball_x) + " ", end="")

    def paddle_find_yx(self, yx):
        """Return distance in Paddle above/ below center, else None"""

        paddle_x = self.paddle_x
        paddle_y = self.paddle_y

        x_center = PADDLE_COLUMNS // 2

        for column in range(PADDLE_COLUMNS):
            if yx == (paddle_y, paddle_x + column):
                x_minus_center = column - x_center

                occasion = (-x_center, x_minus_center, x_center)
                assert -x_center <= x_minus_center <= x_center, occasion

                return x_minus_center

    def paddle_move(self, cap):
        """Move one Paddle left or right, inside its limits"""

        vector = PADDLE_VECTOR_BY_CAP[cap]

        x = self.paddle_x

        # Do as told

        x_next = x + vector
        if not (self.paddle_x_min <= x_next <= self.paddle_x_max):

            # Else kick back from Min or Max

            x_next = x - vector
            if not (self.paddle_x_min <= x_next <= self.paddle_x_max):
                assert False, (self.paddle_x_min, x_next, self.paddle_x_max)

        self.paddle_x = x_next

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

    def ball_step(self):
        """Step the Ball along"""

        (y, x) = self.ball_yx

        (vector_y, vector_x) = self.ball_vector_yx
        (vector_y_next, vector_x_next) = (vector_y, vector_x)

        # Move up or down or neither

        y_next = y + vector_y_next
        if not (self.ball_y_min <= y_next <= self.ball_y_max):
            vector_y_next = -vector_y

            y_next = min(max(y_next, self.ball_y_min), self.ball_y_max)
            if not (self.ball_y_min <= y_next <= self.ball_y_max):
                assert False, (self.ball_y_min, y_next, self.ball_y_max)

        # Move left or right or neither

        x_next = x + vector_x_next
        if not (self.ball_x_min <= x_next <= self.ball_x_max):
            vector_x_next = -vector_x

            x_next = min(max(x_next, self.ball_x_min), self.ball_x_max)
            if not (self.ball_x_min <= x_next <= self.ball_x_max):
                assert False, (self.ball_x_min, x_next, self.ball_x_max)

        # Make a first guess at how to Mutate Self

        self.ball_yx = (y_next, x_next)
        self.ball_vector_yx = (vector_y_next, vector_x_next)

        # Collide with a Brick

        x_minus_center = self.paddle_find_yx(self.ball_yx)
        self.ball_bricks_collide(x_minus_center)

        # Score and Serve, or Bounce off of Paddle, at far Left or far Right

        if vector_y != vector_y_next:
            if y_next == self.ball_y_max:
                if x_minus_center is None:
                    self.ball_score_and_serve()
                else:
                    self.ball_bounce_off_paddle(x_minus_center)

    def ball_bricks_collide(self, x_minus_center):

        ball_yx = self.ball_yx
        (vector_y, vector_x) = self.ball_vector_yx

        (y, x) = ball_yx

        tui = self.tui

        #

        if ball_yx in self.brick_yxs_set:
            assert y != self.ball_y_max, (y, self.ball_y_max)
            assert x_minus_center is None, x_minus_center

            self.brick_yxs_set.remove(ball_yx)

            self.ball_vector_yx = (-vector_y, -vector_x)

            #

            left_yx = (y, x - 1)
            if left_yx in self.brick_yxs_set:
                self.brick_yxs_set.remove(left_yx)
                tui.print(CUP_Y_X.format(y, x - 1) + " ", end="")

            right_yx = (y, x + 1)
            if right_yx in self.brick_yxs_set:
                self.brick_yxs_set.remove(right_yx)
                tui.print(CUP_Y_X.format(y, x + 1) + " ", end="")

    def ball_score_and_serve(self):
        """Score and Serve, at Bottom"""

        ball_x_mid = self.ball_x_mid
        rows = self.rows

        # Serve fast or slow, but not still

        vector_y_next = -1
        vector_x_next = 0

        # Mutate Self

        self.paddle_x = self.paddle_x_mid

        self.ball_yx = (rows - 2, ball_x_mid)
        self.ball_vector_yx = (vector_y_next, vector_x_next)

    def ball_bounce_off_paddle(self, x_minus_center):
        """Bounce off of Paddle, at Bottom"""

        for _ in range(abs(x_minus_center)):
            if x_minus_center < 0:
                self.ball_shove("←")
            else:
                self.ball_shove("→")


#
# Take Words from the Sh Command Line into KeyCaps Py
#


def parse_breakout_py_args_else():
    """Print helps for Breakout Py and exit zero or nonzero, else return args"""

    # Drop the '--' Separator if present, even while declaring no Pos Args

    sys_parms = sys.argv[1:]
    if sys_parms == ["--"]:
        sys_parms = list()

    # Parse the Sh Command Line, or show Help

    parser = compile_breakout_argdoc_else()
    args = parser.parse_args(sys_parms)  # prints helps and exits, else returns args
    if not sys.argv[1:]:
        doc = __main__.__doc__

        exit_via_testdoc(doc, epi="examples")  # exits because no args

    # Succeed

    return args


def compile_breakout_argdoc_else():
    """Form an ArgumentParser for Breakout Py"""

    doc = __main__.__doc__
    parser = compile_argdoc(doc, epi="quirks")
    try:
        exit_if_argdoc_ne(doc, parser=parser)
    except SystemExit:
        sys_stderr_print("breakout.py: ERROR: main doc and argparse parser disagree")

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


# todo: need a debug trigger to dump last few states as separate Json to Diff

# todo: yes, a first draft, but no, its Physics can't explode all the Bricks yet


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/keycaps.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
