"""
usage: main.py

draw a Checkers Board and move its Pieces

examples:
  clear
  python3 main.py
"""

import dataclasses
import re
import sys
import textwrap

#
#
# Place Tubes of Cells on the Board
#

FEATURE_STAGING = True  # jitter Fri 15/Mar
FEATURE_STAGING = False

TubeCount7 = 7  # total printed
TubeCount2 = 2  # often empty

BallCount4 = 4

Board = """

    ... .x. ... .x. ... .x. ... .x.

    .x. ... .x. ... .x. ... .x. ...

    ... .x. ... .x. ... .x. ... .x.

    .x. ... .x. ... .x. ... .x. ...

    ... .x. ... .x. ... .x. ... .x.

    .x. ... .x. ... .x. ... .x. ...

    ... .x. ... .x. ... .x. ... .x.

    .x. ... .x. ... .x. ... .x. ...

"""

Board = textwrap.dedent(Board).strip()

BoardLines = Board.splitlines()

Y1Below = 3 + len(BoardLines)

White = "\N{Medium White Circle}"
Black = "\N{Medium Black Circle}"  # 'Medium' Black better than 'Large', but why?
Red = "\N{Large Red Circle}"
Blue = "\N{Large Blue Circle}"
Orange = "\N{Large Orange Circle}"
Yellow = "\N{Large Yellow Circle}"
Green = "\N{Large Green Circle}"
Purple = "\N{Large Purple Circle}"
Brown = "\N{Large Brown Circle}"

... == White, Black, Red, Blue, Orange, Yellow, Green, Purple, Brown


@dataclasses.dataclass
class Cell:
    """Give a Place to 0 or 1 Pieces"""

    y1: int
    x1: int

    color: str  # one of White, Black, Blue, Red, or Orange

    y: int
    x: int


Cells = list()
for y3, line in enumerate(BoardLines):
    y1 = 3 + y3
    for m in re.finditer(r"x", string=line):
        x1 = 1 + 4 + m.start()

        c = Cell(y1=y1, x1=x1, color=White, y=-1, x=-1)
        Cells.append(c)

assert len(Cells) == 8 * 4, len(Cells)

yy = sorted(set(_.y1 for _ in Cells))
xx = sorted(set(_.x1 for _ in Cells))
assert yy == list(range(3, 19, 2)), (yy, )
assert xx == list(range(6, 36, 4)), (xx, )

cell_by_yx = dict()
for y in range(8):
    for x in range(4):
        yx = (y, x)
        assert yx not in cell_by_yx.keys(), (yx, )

        y1 = Y1Below - 1 - (y * 2)

        if (y % 2) == 0:
            x1 = 6 + (x * 8)
        else:
            x1 = 10 + (x * 8)

        cc = list(_ for _ in Cells if (_.y1, _.x1) == (y1, x1))
        assert len(cc) == 1, (cc, (y1, x1), yx)

        c = cc[-1]
        cell_by_yx[yx] = c

        assert c.y == -1, (c, yx)
        assert c.x == -1, (c, yx)

        c.y = y
        c.x = x

#
#
# Fill all but the middle two Rows
#

for y in range(3):
    for x in range(4):
        yx = (y, x)
        cell = cell_by_yx[yx]
        assert cell.color == White, (cell.color, yx)

        cell.color = Red

for y in range(5, 8):
    for x in range(4):
        yx = (y, x)
        cell = cell_by_yx[yx]
        assert cell.color == White, (cell.color, yx)

        cell.color = Black

#
#
# Model, paint, and judge a Game
#


class Main:
    """Name a workspace for the Code of this Py File"""

    turn: int  # count Turns of Sorting or Scrambling


def board_paint() -> None:
    """Paint over the Board on Screen"""

    for c in Cells:
        y1 = c.y1
        x1 = c.x1

        print(f"\x1B[{y1};{x1}H" + c.color, end="")

    print(f"\x1B[{Y1Below}H", end="")

    print()
    print()

    print("\x1B[J", end="")

    Main.turn = Main.turn + 1
    dent = 8 * " "
    print(f"{dent}Playing Checkers - Turn {Main.turn}")

    sys.stdout.flush()

    # Mar/2024 ReplIt·Com didn't accept EL = "\x1B[2K"  # Erase In Line


def board_judge() -> None:
    """Pick apart the Cells"""


#
#
# Play thyself forever
#


def main() -> None:
    """Launch this Process"""

    print("\x1B[H" + "\x1B[2J" + "\x1B[3J")  # a la Sh 'clear'

    print("\x1B[?25l")  # DecCsiCursorHide
    try:
        try_main()
    finally:
        print("\x1B[?25h")  # DecCsiCursorShow
        print(f"\x1B[{Y1Below}H")
        print()
        print()
        print()


def try_main() -> None:
    """Play the Game, over and over and over"""

    Main.turn = 0

    board_paint()


main()
