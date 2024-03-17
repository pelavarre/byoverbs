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

Emptyish = (White, Yellow, Green, Purple, Brown)

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

    yx: tuple[int, int]


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

            c = Cell(y1=y1, x1=x1, color=White, y=-1, x=-1, yx=(-1, -1))
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
        c.yx = (y, x)

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
    out_colors: list[str]  # Colors

    future_trails: list[list[Cell]]

    reddish_trails: list[list[Cell]]
    blackish_trails: list[list[Cell]]
    pawnish_trails: list[list[Cell]]
    queenish_trails: list[list[Cell]]

    our_colors: list[str]
    our_trails: list[list[Cell]]
    our_steps: list[list[Cell]]
    our_jumps: list[list[Cell]]

    their_colors: list[str]
    their_trails: list[list[Cell]]
    their_steps: list[list[Cell]]
    their_jumps: list[list[Cell]]


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
    if Main.out_colors:
        print("Outs")
        print()
        for index in range(0, len(Main.out_colors), 8):
            some_out_colors = Main.out_colors[index:][:8]
            print(" ".join(some_out_colors))
            print()

    print()

    print("\x1B[J", end="")

    sys.stdout.flush()

    # Mar/2024 ReplIt·Com didn't accept EL = "\x1B[2K"  # Erase In Line


Main.out_colors = list()
Main.future_trails = list()


def board_judge() -> None:  # noqa C901
    """Look for Moves"""

    # List the Moves

    futures = Main.future_trails
    futures.clear()

    for yx in yx_list:
        (y, x) = yx

        cell = cell_by_yx[yx]
        if cell.color in Emptyish:
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

                if ahead_cell.color in Emptyish:
                    future_trail = [cell, ahead_cell]
                    futures.append(future_trail)

                # Jump over an Enemy into an Empty Cell

                if ahead_cell.color in them_colors:
                    far_ahead_yx = yx_plus_func(ahead_yx)
                    if far_ahead_yx in yx_list:
                        far_cell = cell_by_yx[far_ahead_yx]

                        if far_cell.color in Emptyish:
                            future_trail = [cell, ahead_cell, far_cell]
                            futures.append(future_trail)

    # Pick apart the Moves

    reddish_trails = list(_ for _ in futures if _[0].color in Reddish)
    blackish_trails = list(_ for _ in futures if _[0].color in Blackish)
    pawnish_trails = list(_ for _ in futures if _[0].color in Pawnish)
    queenish_trails = list(_ for _ in futures if _[0].color in Pawnish)

    our_colors = Reddish if (Main.turn % 2) else Blackish
    our_trails = list(_ for _ in futures if _[0].color in our_colors)
    our_steps = list(_ for _ in our_trails if len(_) == 2)
    our_jumps = list(_ for _ in our_trails if len(_) == 3)

    their_colors = Blackish if (Main.turn % 2) else Reddish
    their_trails = list(_ for _ in futures if _[0].color in their_colors)
    their_steps = list(_ for _ in their_trails if len(_) == 2)
    their_jumps = list(_ for _ in their_trails if len(_) == 3)

    our_trail_lengths = sorted(set(len(_) for _ in our_trails))
    their_trail_lengths = sorted(set(len(_) for _ in their_trails))
    if our_trail_lengths:
        assert our_trail_lengths in ([2], [2, 3], [3]), (our_trail_lengths,)
    if their_trail_lengths:
        assert their_trail_lengths in ([2], [2, 3], [3]), (their_trail_lengths,)

    Main.reddish_trails = reddish_trails
    Main.blackish_trails = blackish_trails
    Main.pawnish_trails = pawnish_trails
    Main.queenish_trails = queenish_trails

    Main.our_colors = our_colors
    Main.our_trails = our_trails
    Main.our_steps = our_steps
    Main.our_jumps = our_jumps

    Main.their_colors = their_colors
    Main.their_trails = their_trails
    Main.their_steps = their_steps
    Main.their_jumps = their_jumps


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

    inc = 1
    inc_yx = (-1, -1)

    while True:
        Main.turn += inc

        board_paint()
        board_judge()
        time.sleep(0.9 / SPEEDUP)

        # Fade all the Purple to White

        if inc or (not Main.our_trails):
            for yx in yx_list:
                cell = cell_by_yx[yx]
                if cell.color in Emptyish:
                    if cell.color != White:
                        cell.color = White

        # List Moves, but move Reddish first

        if not Main.our_trails:  # no Tie Game at no Pawnish_Trails, Queens keep moving
            print()
            if Main.reddish_trails:
                print("Red won")
            elif Main.blackish_trails:
                print("Black won")
            else:
                print("Game tied")

            print()

            sys.stdout.flush()

            time.sleep(0.9 / SPEEDUP)

            break

        # Choose which Move to make

        if inc:
            assert Main.our_trails, (Main.our_trails, inc, Main.turn)
            trail = random.choice(Main.our_trails)
        else:
            our_jumps_here = list(_ for _ in Main.our_jumps if _[0].yx == inc_yx)
            assert our_jumps_here, (inc_yx, inc, our_jumps_here, Main.turn)
            trail = random.choice(our_jumps_here)

        assert len(trail) in (2, 3), (len(trail), trail)

        cell = trail[0]
        last_cell = trail[-1]

        o2 = (cell.color, Main.our_colors, cell, trail)
        assert cell.color in Main.our_colors, o2
        assert last_cell.color in Emptyish, (last_cell.color, last_cell, trail)

        # Take out the Queens or Pawns jumped over

        if len(trail) == 3:
            middle_cell = trail[1]

            o3 = (middle_cell.color, Main.their_colors, middle_cell, trail)
            assert middle_cell.color in Main.their_colors, o3

            Main.out_colors.append(middle_cell.color)
            middle_cell.color = Purple

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

        # Sometimes Jump again

        board_judge()  # todo: cache this work while no change to Board

        inc = 1
        if len(trail) == 3:
            inc_yx = trail[-1].yx
            our_jumps_here = list(_ for _ in Main.our_jumps if _[0].yx == inc_yx)
            if our_jumps_here:
                if random.random() >= 0.667:
                    inc = 0


main()
