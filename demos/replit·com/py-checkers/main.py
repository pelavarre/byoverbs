"""
usage: main.py

draw a Checkers Board and move its Pieces

examples:
  clear
  python3 main.py
"""

import dataclasses
import random
import re
import sys
import textwrap
import time

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

Reddish = (Red, Orange)
Blackish = (Black, Blue)

Pawnish = (Red, Black)
Queenish = (Orange, Blue)


@dataclasses.dataclass(order=True)
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
assert yy == list(range(3, 19, 2)), (yy,)
assert xx == list(range(6, 36, 4)), (xx,)

yx_list = list()
for y in range(8):
    for x in range(4):
        yx = (y, x)

        yx_list.append(yx)

cell_by_yx = dict()
for yx in yx_list:
    (y, x) = yx
    assert yx not in cell_by_yx.keys(), (yx,)

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

    future_trails: list[list[Cell]]


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

    dent = 8 * " "
    print(f"{dent}Playing Checkers - Turn {Main.turn}")

    sys.stdout.flush()

    # Mar/2024 ReplIt·Com didn't accept EL = "\x1B[2K"  # Erase In Line


Main.future_trails = list()


def board_judge() -> None:
    """Look for Moves"""

    future_trails = Main.future_trails
    future_trails.clear()

    for yx in yx_list:
        (y, x) = yx

        cell = cell_by_yx[yx]
        if cell.color == White:
            continue

        if (cell.color in Reddish) or (cell.color == Blue):
            yplus = (y + 1, x)
            if (y % 2) == 0:
                left = (y + 1, x - 1)
                right = yplus
            else:
                left = yplus
                right = (y + 1, x + 1)

            future_add_if(cell, left=left, right=right)

        if (cell.color in Blackish) or (cell.color == Orange):
            yminus = (y - 1, x)
            if (y % 2) == 0:
                left = (y - 1, x - 1)
                right = yminus
            else:
                left = yminus
                right = (y - 1, x + 1)

            future_add_if(cell, left=left, right=right)


def future_add_if(cell, left, right) -> None:
    """Add the Left Move or the Right Move or both or neither, whatever works"""

    future_trails = Main.future_trails

    assert yx in yx_list, (yx,)
    for last_yx in (left, right):
        if last_yx in yx_list:
            last_cell = cell_by_yx[last_yx]
            if last_cell.color == White:
                trail = [cell, last_cell]

                future_trails.append(trail)


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
        print()
        print()
        print()
        print()
        print()
        print()


def try_main() -> None:  # noqa C901
    """Play the Game, over and over and over"""

    breaking = False

    Main.turn = 0

    past_trails = list()
    while True:
        Main.turn += 1

        team = Reddish if (Main.turn % 2) else Blackish  # Reddish first

        board_paint()
        board_judge()
        time.sleep(0.9)
        # time.sleep(0.02)

        # List Moves

        futures = Main.future_trails
        team_trails = list(_ for _ in futures if _[0].color in team)

        reddish_trails = list(_ for _ in futures if _[0].color in Reddish)
        blackish_trails = list(_ for _ in futures if _[0].color in Blackish)
        pawnish_trails = list(_ for _ in futures if _[0].color in Pawnish)

        if (not team_trails) or (not pawnish_trails):
            if breaking:
                board_paint()
                print()
                print()
                print()
                print()
                print()
                breakpoint()
                board_paint()

            print()
            if reddish_trails:
                print("Red won")
            elif blackish_trails:
                print("Black won")
            else:
                print("Game tied")

            print()

            sys.stdout.flush()

            time.sleep(0.9)

            break

        # Choose which Move to make

        trail = random.choice(team_trails)
        (cell, last_cell) = trail

        assert cell.color in team, (cell.color, team, cell, trail)
        assert last_cell.color == White, (last_cell.color, last_cell, trail)

        # Make Queens out of Pawns

        cell_color = cell.color

        if cell.color == Red:
            if last_cell.y == 7:
                cell_color = Orange
                # breaking = True
        elif cell.color == Black:
            if last_cell.y == 0:
                cell_color = Blue
                # breaking = True

        # cell_color = cell.color  # comment out to auth Queens

        # Make the Move

        last_cell.color = cell_color
        cell.color = White

        if breaking:
            board_paint()
            breakpoint()
            board_paint()

        past_trails.append(trail)


main()
