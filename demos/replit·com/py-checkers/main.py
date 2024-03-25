#!/usr/bin/env python3
"""
usage: main.py

draw a Checkers Board and move its Pieces

examples:
  python3 main.py --
"""

import calendar
import copy
import dataclasses
import datetime as dt
import os
import random
import re
import sys
import termios
import textwrap
import time
import tty

#
#
# Run differently at Replit·Com Console, vs Replit·Com Shell
#


def replit_is_a_console() -> bool:
    "Guess if Sys Stderr is to a Replit Console (not Shell)"

    y1x1 = tty_kbwhere()
    isacons = y1x1 == (1, 1)

    return isacons

    # wrong in the Upper Left of Shell, but that's rarely tested


def tty_kbwhere() -> tuple[int, int]:
    """Silently drop any pending Tty Input, and report Cursor Y1 X1"""

    fd = sys.stderr.fileno()
    tcgetattr = termios.tcgetattr(fd)
    tty.setraw(fd, when=termios.TCSADRAIN)

    sys.stderr.write("\x1B[6n")  # Device Status Report (DSR) 06/14 n
    sys.stderr.flush()

    ibytes = os.read(fd, 100)

    when = termios.TCSADRAIN
    termios.tcsetattr(fd, when, tcgetattr)

    CPR_BYTES_REGEX = rb"^\x1B\[([0-9]+);([0-9]+)R$"
    m = re.match(CPR_BYTES_REGEX, string=ibytes)
    assert m, (ibytes,)  # Cursor Position Report (CPR) 05/02 R

    y1 = int(m.group(1))
    x1 = int(m.group(2))
    y1x1 = (y1, x1)

    return y1x1


ISACONS = replit_is_a_console()

# print(os.get_terminal_size())

#
#
# Place Tubes of Cells on the Board
#

#

SPEEDUP = 750
SPEEDUP = 100
SPEEDUP = 50
SPEEDUP = 10
SPEEDUP = 5
SPEEDUP = 1
# last sticks

if not ISACONS:
    SPEEDUP = 750

MAX_TURN = -1

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

Emptyish = (White, Yellow, Green, Purple, Brown)

Reddish = (Red, Orange)
Blackish = (Black, Blue)

Pawnish = (Red, Black)
Queenish = (Orange, Blue)


@dataclasses.dataclass(order=True)
class Cell:
    """Give a Place on the Board to 1 Queen, 1 Pawn, or No One"""

    y1: int  # where to paint the Cell
    x1: int

    color: str  # one of White, Black, Blue, Red, or Orange
    stale_if: str  # may be empty ""

    y: int  # index the Cells of the Board by Y Up and X Right
    x: int

    yx: tuple[int, int]

    def __init__(self, y1, x1, color, y, x) -> None:
        assert color, (color,)

        self.y1 = y1
        self.x1 = x1
        self.color = color
        self.stale_if = ""
        self.y = y
        self.x = x
        self.yx = (y, x)


Cells: list[Cell]
cell_by_yx: dict[tuple[int, int], Cell]
yx_list: list[tuple[int, int]]

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

    game_name: str  # name of the Game, which is its Random Seed
    turn: int  # count Turns of Sorting or Scrambling

    outs: list[str]  # Colors of Queens or Pawns taken off the Board

    future_trails: list[list[Cell]]  # the Moves found

    reddish_trails: list[list[Cell]]  # of Red Queen/ Orange Pawn
    blackish_trails: list[list[Cell]]  # of Blue Queen/ Black Pawn
    pawnish_trails: list[list[Cell]]  # of Orange Pawn/ Black Pawn
    queenish_trails: list[list[Cell]]  # of Red Queen/ Blue Queen

    our_colors: tuple[str, str]  # our Red & Orange, else Black & Blue
    our_trails: list[list[Cell]]  # the Moves of our Colors
    our_steps: list[list[Cell]]  # our Moves from Cell into Empty Neighbor
    our_jumps: list[list[Cell]]  # our Moves from Cell over Enemy

    their_colors: tuple[str, str]  # their Red & Orange, else Black & Blue
    their_trails: list[list[Cell]]  # the Moves of their Colors
    their_steps: list[list[Cell]]  # their Moves from Cell into Empty Neighbor
    their_jumps: list[list[Cell]]  # their Moves from Cell over Enemy


Main.outs = list()
Main.future_trails = list()


def board_paint() -> None:
    """Paint over the Board on Screen"""

    cells = list(Cells)  # unneeded cloning
    outs = list(Main.outs)  # unneeded cloning

    sys.stdout.flush()

    for c in cells:
        y1 = c.y1
        x1 = c.x1

        if c.stale_if != c.color:
            print(f"\x1B[{y1};{x1}H", end="")
            sys.stdout.flush()
            print(c.color, end="")
            c.stale_if = c.color
            sys.stdout.flush()

    print(f"\x1B[{Y1Below}H", end="")
    sys.stdout.flush()

    print()
    print()

    dent = 4 * " "  # trailing Dent needed to roll back
    print(f"{2 * dent}Playing Checkers - Turn {Main.turn}{dent}")

    game_name = Main.game_name
    print(f"{3 * dent}Game {game_name}")

    print()
    if not outs:
        print("\x1B[K", end="")  # needed to roll back
    else:
        print("Outs")
        print()
        for index in range(0, len(outs), 8):
            some_outs = outs[index:][:8]

            sys.stdout.flush()
            for index, color in enumerate(some_outs):
                if index:
                    print(" ", end="")
                    sys.stdout.flush()
                print(color, end="")
                sys.stdout.flush()

            print("\x1B[K", end="")
            print()

    print("\x1B[K", end="")
    print()
    sys.stdout.flush()

    print("\x1B[J", end="")
    sys.stdout.flush()

    # CUP_Y1 = b"\x1B[{}H"  # Cursor Position  # 04/08 H
    # CUP_Y1_X1 = b"\x1B[{};{}H"  # Cursor Position  # 04/08 H
    # ED = b"\x1B[J"  # Erase in Page  # 04/10 J
    # EL = "\x1B[K"  # Erase In Line  # 04/11 K


def board_judge() -> None:  # noqa C901
    """Look for Moves"""

    # List the Moves

    futures: list[list[Cell]]

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

    Main.reddish_trails = reddish_trails
    Main.blackish_trails = blackish_trails
    Main.pawnish_trails = pawnish_trails
    Main.queenish_trails = queenish_trails

    our_colors = Reddish if (Main.turn % 2) else Blackish
    our_trails = list(_ for _ in futures if _[0].color in our_colors)
    our_steps = list(_ for _ in our_trails if len(_) == 2)
    our_jumps = list(_ for _ in our_trails if len(_) == 3)

    their_colors = Blackish if (Main.turn % 2) else Reddish
    their_trails = list(_ for _ in futures if _[0].color in their_colors)
    their_steps = list(_ for _ in their_trails if len(_) == 2)
    their_jumps = list(_ for _ in their_trails if len(_) == 3)

    our_lengths = sorted(set(len(_) for _ in our_trails))
    their_lengths = sorted(set(len(_) for _ in their_trails))
    if our_lengths:
        assert our_lengths in ([2], [2, 3], [3]), (our_lengths,)
    if their_lengths:
        assert their_lengths in ([2], [2, 3], [3]), (their_lengths,)

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
        sys.stdout.flush()
        for _ in range(19):
            print()


past_turns: list[int]
past_cell_lists: list[list[Cell]]
past_outs_lists: list[list[str]]

past_turns = list()
past_cell_lists = list()
past_outs_lists = list()


def try_main() -> None:
    """Play the Game over and over"""

    while True:
        play_once()

        print("Press Return to roll back the Game")
        sys.stdin.readline()

        tco_list = list(zip(past_turns, past_cell_lists, past_outs_lists))
        for t, c, o in reversed(tco_list):
            Main.turn = t
            for index, cell in enumerate(c):
                Cells[index].color = cell.color
            Main.outs[::] = o

            board_paint()

            rollback_speedup = 10
            time.sleep(0.9 / rollback_speedup)

        past_turns.clear()
        past_cell_lists.clear()
        past_outs_lists.clear()

        print()
        print("Press Return to play again")
        sys.stdin.readline()


def play_once() -> None:  # noqa C901
    """Play the Game through, once"""

    Main.turn = 0

    game_name = "194604.0322"  # mostly tied, but Black Pawn become Blue Queen wins
    game_name = "195448.0322"  # often displays wrong when run at Speedup 750
    game_name = new_game_name()  # '194604.0322'
    # last sticks

    Main.game_name = game_name

    seed = float(game_name)
    random.seed(seed)

    #

    inc = 1
    inc_yx = (-1, -1)

    while True:
        if (MAX_TURN >= 0) and (Main.turn >= MAX_TURN):
            sys.exit(3)

        Main.turn += inc

        board_paint()
        board_judge()
        time.sleep(0.9 / SPEEDUP)

        past_turns.append(Main.turn)
        past_cell_lists.append(copy.deepcopy(Cells))
        past_outs_lists.append(copy.deepcopy(Main.outs))

        # Fade all the Purple to White

        if inc or (not Main.our_trails):
            for yx in yx_list:
                cell = cell_by_yx[yx]
                if cell.color in Emptyish:
                    if cell.color != White:
                        cell.color = White

        # List Moves, but move Reddish first

        if not Main.our_trails:  # no Tie Game at no Pawnish_Trails, Queens keep moving
            board_paint()
            board_judge()  # unneeded unless Emptyish vs White matters

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

        if inc:  # any move to start with
            assert Main.our_trails, (Main.our_trails, inc, Main.turn)
            trail = random.choice(Main.our_trails)
        else:  # else only a next move from where the last jump landed
            oj = Main.our_jumps
            our_jumps_here = list(_ for _ in oj if _[0].yx == inc_yx)
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

            Main.outs.append(middle_cell.color)
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
            oj = Main.our_jumps
            our_jumps_here = list(_ for _ in oj if _[0].yx == inc_yx)
            if our_jumps_here:
                if random.random() >= 0.667:
                    inc = 0


def new_game_name() -> str:
    """Say what MDd.HhMmSs is in California now"""

    naive = dt.datetime.now()
    pacific = pacific_timezone(naive)
    t = naive.astimezone(pacific)

    # print(t)

    md = (t.month, t.day)
    hms = (t.hour, t.minute, t.second)
    str_md = "".join("{:02d}".format(_) for _ in md)
    str_hms = "".join("{:02d}".format(_) for _ in hms)

    md_dot_hms = f"{str_hms}.{str_md}".removeprefix("0")

    return md_dot_hms

    # '191041.0322'


def pacific_timezone(t=None) -> dt.timezone:
    """Guess when Winter and Summer is, in California"""

    naive = t if t else dt.datetime.now()
    year = naive.year

    mar = dt.datetime(year, 3, 1, 2 + 8, 0, 0)
    nov = dt.datetime(year, 11, 1, 2 + 7, 0, 0)

    for nth in range(2):
        while mar.weekday() != calendar.SUNDAY:  # 2nd Sunday in March
            mar += dt.timedelta(days=1)
        if nth < (2 - 1):
            mar += dt.timedelta(days=1)

    while nov.weekday() != calendar.SUNDAY:  # 1st Sunday in November
        nov += dt.timedelta(days=1)

    # print(mar)
    # print(nov)

    assert ((24 - 8) * 3600) == 57600
    tz = dt.timezone(dt.timedelta(days=-1, seconds=57600))  # Winter
    if (naive >= mar) or (naive < nov):
        tz = dt.timezone(dt.timedelta(days=-1, seconds=61200))  # Summer

    return tz


main()
