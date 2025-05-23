#!/usr/bin/env python3

r"""
usage: shpong.py [-h]

bounce a U+25A0 $B Ping-Pong Ball back & forth between 2 Paddles

options:
  -h, --help  show this help message and exit

quirks:
  press W and S (or A and D) to move the Left Paddle up and down
  press K and J (or H and L) to move the Right Paddle up and down
  press $L $U $D $R shove on the Ball to speed it up or slow it down
  press Q three times in a row, to end the Game before scoring 9 points
  press Keys while the other Player needs to press Keys, just to delay those Keys

examples:
  open https://shell.cloud.google.com/?show=terminal  # if you need another Linux
  git clone https://github.com/pelavarre/byoverbs.git
  printf '\e[8;24;80t'  # play in a conventional 24x80 Terminal Window
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


__version__ = "2025.2.17"  # Monday


#
# Auto-complete the Help Lines
#


DOC = __main__.__doc__
assert DOC, (DOC,)

DOC = DOC.replace("$B", "\N{BLACK SQUARE}")  # ■ U+25A0
DOC = DOC.replace("$D", "\N{DOWNWARDS ARROW}")  # ↓ U+2193
DOC = DOC.replace("$L", "\N{LEFTWARDS ARROW}")  # ← U+2190
DOC = DOC.replace("$R", "\N{RIGHTWARDS ARROW}")  # → U+2192
DOC = DOC.replace("$U", "\N{UPWARDS ARROW}")  # ↑ U+2191

__main__.__doc__ = DOC


#
# Name some Commands of the Terminal Output Magic
#
#   https://en.wikipedia.org/wiki/ANSI_escape_code
#   https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
#


CSI = "\x1b["  # macOS Terminal takes "\x1B[" as CSI, doesn't take "\N{CSI}" == "\x9B"

CUP_Y_X = "\x1b[{};{}H"  # Cursor Position (CUP)  # from upper left "\x1B[1;1H"

DECTCEM_CURSOR_HIDE = "\x1b[?25l"  # Hide away the one Cursor on Screen
DECTCEM_CURSOR_SHOW = "\x1b[?25h"  # Show the one Cursor on Screen


#
# Spell out some Words of the Terminal Input Magic
#


Space = "Space"

Down = "\N{DOWNWARDS ARROW}"
Left = "\N{LEFTWARDS ARROW}"
Right = "\N{RIGHTWARDS ARROW}"
Up = "\N{UPWARDS ARROW}"


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


BALL = "\N{BLACK SQUARE}"  # ■ U+25A0  # Black in Light Mode, White in Dark Mode


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


SCORE_CAPS = list("-0123456789=")  # '=' for '=' itself, and for '+' at '⇧ ='
SCORE_CAPS.sort()

HOT_CAPS = list("← ↑ ↓ → W A S D H J K L . Space".split())
HOT_CAPS += SCORE_CAPS
HOT_CAPS.sort()


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

    if False:
        flat_up = os.terminal_size((80, 24))
        keycaps.try_put_terminal_size(stdio, size=flat_up)

    with keycaps.tui_open(stdio) as tui:
        game = ShPongGame(tui)

        tui.print(DECTCEM_CURSOR_HIDE)
        try:
            tui.screen_wipe_below()
            game.run_till_quit()
        finally:
            tui.print(DECTCEM_CURSOR_SHOW)  # todo:  grow 'tui.__exit__'


class ShPongGame:

    selves: list["ShPongGame"]
    selves = list()

    def __init__(self, tui):
        ShPongGame.selves.append(self)
        self.tui = tui

        self.reinit()

    def reinit(self):
        self.caps = list()  # keylogger  # trace of 'tui.cap_from_stroke' of 'tui.readline'

        self.ball_vector_yx = (0, +1)
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

        ball_y_mid = 1 + (board_rows // 2)
        ball_x_mid = 1 + (board_columns // 2)  # todo: why 1 extra column on right ??

        ball_yx = (ball_y_mid, ball_x_mid)

        ball_y_min = 2
        ball_y_max = ball_y_min + board_rows - 1
        ball_x_min = 2
        ball_x_max = ball_x_min + board_columns - 1

        # Place two Paddles

        paddle_y_mid = (board_rows // 2) - (PADDLE_ROWS // 2) + 1
        paddle_ys = [paddle_y_mid, paddle_y_mid]
        paddle_xs = [2, columns - 1]

        paddle_y_min = 2
        paddle_y_max = (paddle_y_min + board_rows - 1) - (PADDLE_ROWS - 1)

        # Place two single-digit decimal Scores

        colon_y = 4
        colon_x = ball_x_mid

        score_left_x = ball_x_mid - 3 - DIGIT_WIDTH_5  # 3 columns left of middle
        score_right_x = ball_x_mid + 3 + 1  # 3 columns right of middle
        score_xs = [score_left_x, score_right_x]

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

        self.paddle_y_min = paddle_y_min
        self.paddle_y_mid = paddle_y_mid
        self.paddle_y_max = paddle_y_max
        self.paddle_ys = paddle_ys
        self.paddle_xs = paddle_xs

        self.colon_y = colon_y
        self.colon_x = colon_x

        self.score_xs = score_xs

        self.status_y = status_y
        self.status_x = status_x
        self.status_width = columns - 1

    def run_till_quit(self):  # noqa # too complex (11  # FIXME
        tui = self.tui

        caps = self.caps
        scores = self.scores

        paused = False
        while True:
            # Draw one Ball, two Paddles, one Colon, two Scores

            self.board_draw()
            if (scores[0] >= 9) or (scores[-1] >= 9):
                break

            # Read the next Keystroke

            sys.stdout.flush()

            stroke = None
            if not tui.kbhit(timeout=0.100):
                cap = Space  # mmm, not really the Spacebar, rather the absence of a Key
            else:
                stroke = tui.readline()

                cap = tui.cap_from_stroke(stroke)
                if stroke == b"@":
                    cap = "@"  # FIXME: excessive coupling with 'import keycaps'

                caps.append(cap)
                if caps[-3:] == (3 * [cap]):
                    if cap not in HOT_CAPS:  # todo: kind of drastic?
                        break

                if cap == Space:
                    paused = not paused

            # Change the Score on request

            if cap in SCORE_CAPS:
                self.score_cap_stroke(cap, stroke)

            # Erase one moving Ball and two moving Paddles

            self.board_erase()

            # Move the Paddles on demand

            if cap in PADDLE_VECTOR_BY_CAP.keys():
                self.paddle_move(cap)

            # Speed up the Ball, slow it down, or hold it still

            if cap in VECTOR_YX_BY_CAP.keys():
                self.ball_shove(cap)

            # Start the game again

            if cap == "@":
                self.reinit()

            # Step the Ball along, unless Paused

            if not paused:
                self.ball_step()

        status = "".center(self.status_width)
        tui.print(CUP_Y_X.format(self.status_y, self.status_x) + status, end="")

        tui.print(CUP_Y_X.format(self.rows - 2, 1))

    def board_draw(self):
        """Draw one Ball, two Paddles, one Colon, two Scores - and update Status"""

        caps = self.caps
        tui = self.tui

        # Draw one Ball

        (ball_y, ball_x) = self.ball_yx
        tui.print(CUP_Y_X.format(ball_y, ball_x) + BALL, end="")

        # Draw two Paddles

        for paddle_yx in zip(self.paddle_ys, self.paddle_xs):
            (paddle_y, paddle_x) = paddle_yx
            for row in range(PADDLE_ROWS):
                tui.print(CUP_Y_X.format(paddle_y + row, paddle_x) + BALL, end="")

        # Draw the two Dots of one Colon

        tui.print(CUP_Y_X.format(self.colon_y + 0, self.colon_x) + BALL, end="")
        tui.print(CUP_Y_X.format(self.colon_y + 1, self.colon_x) + BALL, end="")

        # Draw two single digit Scores

        for score_x, score in zip(self.score_xs, self.scores):
            chars = CHARS_BY_DIGIT[score]
            for index, line in enumerate(chars.splitlines()):
                tui.print(CUP_Y_X.format(2 + index, score_x) + line, end="")

        # Draw an echo of unwanted input, if any arrived lately

        status = "(press one of "
        status += "A W S D, H K J L, ← ↑ ↓ →, + - =, 0 1 2 3 4 5 6 7 8 9 @ Q)"

        if caps:
            last_cap = caps[-1]
            if last_cap not in HOT_CAPS:
                echo_caps = (3 * [" "]) + caps[-3:]
                echo_caps = echo_caps[-3:]

                echo = " ".join(str(_) for _ in echo_caps)
                status = echo

        status_chars = status.center(self.status_width)[: self.status_width]
        tui.print(CUP_Y_X.format(self.status_y, self.status_x) + status_chars, end="")

    def board_erase(self):
        """Erase one moving Ball and two moving Paddles"""

        tui = self.tui

        # Erase two Paddles

        for paddle_yx in zip(self.paddle_ys, self.paddle_xs):
            (paddle_y, paddle_x) = paddle_yx
            for row in range(PADDLE_ROWS):
                tui.print(CUP_Y_X.format(paddle_y + row, paddle_x) + " ", end="")

        # Erase one Ball

        (ball_y, ball_x) = self.ball_yx
        tui.print(CUP_Y_X.format(ball_y, ball_x) + " ", end="")

    def paddle_find_yx(self, yx):
        """Return distance in Paddle above/ below center, else None"""

        y_center = PADDLE_ROWS // 2

        for paddle_yx in zip(self.paddle_ys, self.paddle_xs):
            (paddle_y, paddle_x) = paddle_yx
            for row in range(PADDLE_ROWS):
                if yx == (paddle_y + row, paddle_x):
                    y_minus_center = row - y_center

                    occasion = (-y_center, y_minus_center, y_center)
                    assert -y_center <= y_minus_center <= y_center, occasion

                    return y_minus_center

    def score_cap_stroke(self, cap, stroke):
        """Edit the Scores"""

        ball_x_mid = self.ball_x_mid
        scores = self.scores

        (_, x) = self.ball_yx
        (_, vector_x) = self.ball_vector_yx

        index = 1 - int(x >= ball_x_mid)
        if vector_x:
            index = int(vector_x < 0)

        score = scores[index]

        if cap == "=":
            if stroke == b"=":
                scores[0] = scores[1] = max(scores)

                return

        if cap == "=":  # take '⇧ =' as '+'
            alt_score = score + 1
        elif cap == "-":
            alt_score = score - 1
        elif cap in "0123456789":
            alt_score = int(cap)
        else:
            assert False, (SCORE_CAPS, cap)

        next_score = min(max(alt_score, 0), 9)
        if next_score != alt_score:
            if next_score == 0:
                next_score = 1
            elif next_score == 9:
                next_score = 8

        scores[index] = next_score

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

        # Score and Serve, or Bounce off of Paddle, at far Left or far Right

        y_minus_center = self.paddle_find_yx(self.ball_yx)

        if vector_x != vector_x_next:
            if y_minus_center is None:
                self.ball_score_and_serve()
            else:
                self.ball_bounce_off_paddle(y_minus_center)

    def ball_score_and_serve(self):
        """Score and Serve, at far Left or far Right"""

        (_, ball_x) = self.ball_yx
        (_, vector_x) = self.ball_vector_yx

        index = None
        if ball_x == self.ball_x_min:
            index = -1
        elif ball_x == self.ball_x_max:
            index = 0

        assert index is not None, (self.ball_x_min, ball_x, self.ball_x_max)

        # Score

        self.scores[index] += 1
        assert self.scores[index] <= 9, self.scores[index]

        # Serve fast or slow, but not still

        y_next = self.ball_y_mid
        x_next = self.ball_x_max if index else self.ball_x_min

        vector_y_next = 0
        if self.paddle_ys[index] < self.paddle_y_mid:
            vector_y_next = +1
        elif self.paddle_ys[index] > self.paddle_y_mid:
            vector_y_next = -1

        vector_x_next = -1 if index else +1
        if vector_x:
            vector_x_next = -abs(vector_x) if index else abs(vector_x)

        # Mutate Self

        self.paddle_ys[index] = self.paddle_y_mid

        self.ball_yx = (y_next, x_next)
        self.ball_vector_yx = (vector_y_next, vector_x_next)

    def ball_bounce_off_paddle(self, y_minus_center):
        """Bounce off of Paddle, at far Left or far Right"""

        for _ in range(abs(y_minus_center)):
            if y_minus_center < 0:
                self.ball_shove("↓")
            else:
                self.ball_shove("↑")


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
        sys_exit_if_argdoc_ne(doc, parser=parser)
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


def sys_exit_if_argdoc_ne(doc, parser):
    """Complain and exit nonzero, unless Arg Doc equals Parser Format_Help"""

    # Fetch the Main Doc, and note where from

    assert __main__.__doc__, (__main__.__doc__,)

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


# todo:  adjust to resized Terminal Window Pane without quitting & relaunching the Game

# todo:  explain/change how Spacebar toggles Pause
# todo:  explain/change how holding down Dot . temporarily speeds up the Ball
# todo:  explain/change how pressing any undefined Key 3 times quits the Game


# todo:  accept Tab in place of W Up, accept Return in place of K Up
# todo:  accept Letters near the Hot Letters in their place
# todo:  Bell for rejected Letters

# todo:  heat up the Paddle Colors with each Bounced Ball between Points

# todo:  bounce the Ball into Angles and Speeds that aren't whole Int's

# todo:  record and replay the game, at 1X or some other X speed


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/demos/shpong.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
