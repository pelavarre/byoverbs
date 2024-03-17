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

SPEEDUP = 50
SPEEDUP = 10
SPEEDUP = 5
SPEEDUP = 1
# last wins

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
cell_by_yx = dict()
yx_list = list()


def board_init() -> None:  # noqa C901
    """Fill out the Cells"""

    # Place 1 Cell at each X in the BoardLines

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

    # Index the Cells as Y from Bottom to Top, and as X from Left to Right

    for y in range(8):
        for x in range(4):
            yx = (y, x)

            yx_list.append(yx)

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

    # Fill all but the middle two Rows

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


board_init()

#
#
# Model, paint, and judge a Game
#


class Main:
    """Name a workspace for the Code of this Py File"""

    turn: int  # count Turns of Sorting or Scrambling

    future_trails: list[list[Cell]]
    outs: list[str]  # Colors


Main.outs = list()


def board_paint() -> None:
    """Paint over the Board on Screen"""

    for c in Cells:
        y1 = c.y1
        x1 = c.x1

        print(f"\x1B[{y1};{x1}H" + c.color, end="")

    print(f"\x1B[{Y1Below}H", end="")

    print()
    print()

    dent = 4 * " "
    print(f"{dent}{dent}Playing Checkers - Turn {Main.turn}")

    print()
    if Main.outs:
        print("Outs")
        print()
        for index in range(0, len(Main.outs), 8):
            some_outs = Main.outs[index:][:8]
            print(" ".join(some_outs))
            print()

    print()

    print("\x1B[J", end="")

    sys.stdout.flush()

    # Mar/2024 ReplIt·Com didn't accept EL = "\x1B[2K"  # Erase In Line


Main.future_trails = list()


def board_judge() -> None:  # noqa C901
    """Look for Moves"""

    future_trails = Main.future_trails
    future_trails.clear()

    for yx in yx_list:
        (y, x) = yx

        cell = cell_by_yx[yx]
        if cell.color == White:
            continue

        # Look every which way the Cell can move

        yx_plus_funcs = list()
        if (cell.color == Red) or (cell.color in Queenish):
            yx_plus_funcs.append(yx_plus_north_plus_east)
            yx_plus_funcs.append(yx_plus_north_plus_west)
        if (cell.color == Black) or (cell.color in Queenish):
            yx_plus_funcs.append(yx_plus_south_plus_east)
            yx_plus_funcs.append(yx_plus_south_plus_west)

        if cell.color in Reddish:
            them_colors = Blackish
        else:
            them_colors = Reddish

        # Step into an adjacent Empty Cell

        for yx_plus_func in yx_plus_funcs:
            ahead_yx = yx_plus_func(yx)
            if ahead_yx in yx_list:
                ahead_cell = cell_by_yx[ahead_yx]

                if ahead_cell.color == White:
                    future_trail = [cell, ahead_cell]
                    future_trails.append(future_trail)

                # Jump over an Enemy into an Empty Cell

                if ahead_cell.color in them_colors:
                    far_ahead_yx = yx_plus_func(ahead_yx)
                    if far_ahead_yx in yx_list:
                        far_cell = cell_by_yx[far_ahead_yx]

                        if far_cell.color == White:
                            future_trail = [cell, ahead_cell, far_cell]
                            future_trails.append(future_trail)


def yx_plus_north_plus_east(yx) -> tuple[int, int]:
    (y, x) = yx
    yx_plus = (y + 1, x) if (y % 2) else (y + 1, x - 1)
    return yx_plus


def yx_plus_north_plus_west(yx) -> tuple[int, int]:
    (y, x) = yx
    yx_plus = (y + 1, x + 1) if (y % 2) else (y + 1, x)
    return yx_plus


def yx_plus_south_plus_east(yx) -> tuple[int, int]:
    (y, x) = yx
    yx_plus = (y - 1, x) if (y % 2) else (y - 1, x - 1)
    return yx_plus


def yx_plus_south_plus_west(yx) -> tuple[int, int]:
    (y, x) = yx
    yx_plus = (y - 1, x + 1) if (y % 2) else (y - 1, x)
    return yx_plus


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

    Main.turn = 0

    # todo: pile up past Boards to undo after end of Game
    while True:
        Main.turn += 1

        board_paint()
        board_judge()
        time.sleep(0.9 / SPEEDUP)

        # List Moves, but move Reddish first

        futures = Main.future_trails

        reddish_trails = list(_ for _ in futures if _[0].color in Reddish)
        blackish_trails = list(_ for _ in futures if _[0].color in Blackish)
        pawnish_trails = list(_ for _ in futures if _[0].color in Pawnish)
        ... == pawnish_trails

        our_colors = Reddish if (Main.turn % 2) else Blackish
        our_trails = list(_ for _ in futures if _[0].color in our_colors)

        their_colors = Blackish if (Main.turn % 2) else Reddish

        if not our_trails:  # no Tie Game at no Pawnish_Trails, Queens keep moving
            print()
            if reddish_trails:
                print("Red won")
            elif blackish_trails:
                print("Black won")
            else:
                print("Game tied")

            print()

            sys.stdout.flush()

            time.sleep(0.9 / SPEEDUP)

            break

        # Choose which Move to make

        trail = random.choice(our_trails)
        assert len(trail) in (2, 3), (len(trail), trail)

        cell = trail[0]
        last_cell = trail[-1]

        assert cell.color in our_colors, (cell.color, our_colors, cell, trail)
        assert last_cell.color == White, (last_cell.color, last_cell, trail)

        # Take out the Queens or Pawns jumped over

        if len(trail) == 3:
            middle_cell = trail[1]

            o = (middle_cell.color, their_colors, middle_cell, trail)
            assert middle_cell.color in their_colors, o

            Main.outs.append(middle_cell.color)
            middle_cell.color = White

        # Make Queens out of Pawns

        cell_color = cell.color

        if cell.color == Red:
            if last_cell.y == 7:
                cell_color = Orange
        elif cell.color == Black:
            if last_cell.y == 0:
                cell_color = Blue

        # Make the Move

        last_cell.color = cell_color
        cell.color = White


main()
