#!/usr/bin/env python3
"""
usage: main.py

draw a Chess Board and move its Pieces

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
import time
import tty
import unicodedata

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

    sys.stderr.write("\x1B[6n")  # Device Status Report (DSR) 06/14
    sys.stderr.flush()

    ibytes = os.read(fd, 100)

    when = termios.TCSADRAIN
    termios.tcsetattr(fd, when, tcgetattr)

    CPR_BYTES_REGEX = rb"^\x1B\[([0-9]+);([0-9]+)R$"
    m = re.match(CPR_BYTES_REGEX, string=ibytes)
    assert m, (ibytes,)  # Cursor Position Report (CPR) 05/02

    y1 = int(m.group(1))
    x1 = int(m.group(2))
    y1x1 = (y1, x1)

    return y1x1


ISACONS = replit_is_a_console()

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
SPEEDUP = 5
# last sticks

if not ISACONS:
    SPEEDUP = 750

MAX_TURN = -1

#

Space = " "
assert Space == unicodedata.lookup("Space")

BlackChessPawn = unicodedata.lookup("Black Chess Pawn")
BlackChessRook = unicodedata.lookup("Black Chess Rook")
BlackChessKnight = unicodedata.lookup("Black Chess Knight")
BlackChessBishop = unicodedata.lookup("Black Chess Bishop")
BlackChessQueen = unicodedata.lookup("Black Chess Queen")
BlackChessKing = unicodedata.lookup("Black Chess King")

WhiteChessPawn = unicodedata.lookup("White Chess Pawn")
WhiteChessRook = unicodedata.lookup("White Chess Rook")
WhiteChessKnight = unicodedata.lookup("White Chess Knight")
WhiteChessBishop = unicodedata.lookup("White Chess Bishop")
WhiteChessQueen = unicodedata.lookup("White Chess Queen")
WhiteChessKing = unicodedata.lookup("White Chess King")

#

Plain = "\x1B[m"  # 06/13 m  # Default Rendition
Black = "\x1B[40m"  # 40 Black Background # 06/13 m
Gray = "\x1B[47m"  # 47 White Background # 06/13 m

default_eq_None = None
if os.getenv("REPLIT_ENVIRONMENT", default_eq_None):
    (Black, Gray) = (Gray, Black)
    # 24/Mar/2024 Replit·Com got these backwards


@dataclasses.dataclass(order=True)
class Cell:
    """Give a Place on the Board to 1 Piece, or No Piece"""

    y1: int  # where to paint the Cell
    x1: int

    color: str  # Plain or Gray
    piece_if: str  # which Piece to paint, or Space, or Empty
    stale_if: str  # the last Piece, or Space, or Empty

    def __init__(self, y1, x1, color) -> None:
        self.y1 = y1
        self.x1 = x1

        self.color = color
        self.piece_if = Space
        self.stale_if = ""  # != Space


cell_by_yx: dict[tuple[int, int], Cell]
cell_by_yx = dict()


def board_init() -> None:
    """Fill out the Cells"""

    # Empty the Board

    for y in range(8):
        y1 = 2 + (7 - y) * 2
        for x in range(8):
            x1 = 3 + (5 * x)

            color = Plain if ((y + x) % 2) else Gray
            cell = Cell(y1=y1, x1=x1, color=color)

            yx = (y, x)
            cell_by_yx[yx] = cell

    assert len(cell_by_yx) == (8 * 8)

    # Fill the Top 2 Rows and Bottom 2 Rows with 8 Pieces each

    whos = "Rook Knight Bishop Queen King Bishop Knight Rook".split()

    for y, color in [(7, "Black"), (0, "White")]:
        for x, who in enumerate(whos):
            yx = (y, x)

            piece = unicodedata.lookup(f"{color} Chess {who}")
            cell_by_yx[yx].piece_if = piece

    for y, color in [(7 - 1, "Black"), (0 + 1, "White")]:
        for x in range(8):
            yx = (y, x)

            piece = unicodedata.lookup(f"{color} Chess Pawn")
            cell_by_yx[yx].piece_if = piece


board_init()

if False:
    for yx, cell in cell_by_yx.items():
        print(yx, cell)
    sys.exit(2)

MaxY1 = max(_.y1 for _ in cell_by_yx.values())
Y1Below = MaxY1 + 2

#
#
# Model, paint, and judge a Game
#


class Main:
    """Name a workspace for the Code of this Py File"""

    game_name: str  # name of the Game, which is its Random Seed
    turn: int  # count Turns of Sorting or Scrambling

    outs: list[str]  # Pieces taken off the Board
    moves: list[Cell]


Main.outs = list()
Main.moves = list()


def board_paint() -> None:
    """Paint over the Board on Screen"""

    outs = list(Main.outs)  # unneeded cloning

    sys.stdout.flush()

    for yx, cell in cell_by_yx.items():
        y1 = cell.y1
        x1 = cell.x1
        assert x1 >= 3, (x1, yx, cell)

        (y, x) = yx
        assert y1 == 2 + (7 - y) * 2, (y1, yx)
        assert x1 == 3 + (5 * x), (x1, yx)

        if cell.stale_if != cell.piece_if:
            cell.stale_if = cell.piece_if

            print(f"\x1B[{y1};{x1 - 2}H", end="")
            if cell.color != Plain:
                print(cell.color, end="")
            print("  " + cell.piece_if + "  ", end="")
            if cell.color != Plain:
                print(Plain, end="")

            sys.stdout.flush()

    print(f"\x1B[{Y1Below}H", end="")
    sys.stdout.flush()

    print()
    print()

    dent = 4 * " "  # trailing Dent needed to roll back
    print(f"{2 * dent}Playing Chess - Turn {Main.turn}{dent}")

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

    # CUP_Y1 = b"\x1B[{}H"  # Cursor Position  # 04/08
    # CUP_Y1_X1 = b"\x1B[{};{}H"  # Cursor Position  # 04/08
    # ED = b"\x1B[J"  # Erase in Page  # 04/10
    # EL = "\x1B[K"  # Erase In Line  # 04/11


def board_judge() -> None:
    """Look for Moves"""

    moves = list()
    moves_add_pawns(moves)

    Main.moves[::] = moves


def moves_add_pawns(moves) -> None:
    """Move each Pawn"""

    for yx, cell in cell_by_yx.items():
        (y, x) = yx

        if cell.piece_if == BlackChessPawn:
            delta_y = -1
        elif cell.piece_if == WhiteChessPawn:
            delta_y = +1
        else:
            continue

        next_yx = (y + delta_y, x)
        next_cell = cell_by_yx[next_yx]

        if next_cell.piece_if != Space:
            continue

        move = [cell, next_cell]
        moves.append(move)


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
past_cell_dicts: list[dict[tuple[int, int], Cell]]
past_outs_lists: list[list[str]]

past_turns = list()
past_cell_dicts = list()
past_outs_lists = list()


def try_main() -> None:
    """Play the Game over and over"""

    while True:
        play_once()

        print("Press Return to roll back the Game")
        sys.stdin.readline()

        tco_list = list(zip(past_turns, past_cell_dicts, past_outs_lists))
        for t, c, o in reversed(tco_list):
            Main.turn = t
            for yx, cell in c.items():
                cell_by_yx[yx].piece_if = cell.piece_if
            Main.outs[::] = o

            board_paint()

            rollback_speedup = 10
            time.sleep(0.9 / rollback_speedup)

        past_turns.clear()
        past_cell_dicts.clear()
        past_outs_lists.clear()

        print()
        print("Press Return to play again")
        sys.stdin.readline()


def play_once() -> None:  # noqa C901
    """Play the Game through, once"""

    Main.turn = 0

    game_name = new_game_name()  # FIXME '194604.0322'
    # last sticks

    Main.game_name = game_name

    seed = float(game_name)
    random.seed(seed)

    #

    moves = Main.moves
    while True:
        if (MAX_TURN >= 0) and (Main.turn >= MAX_TURN):
            sys.exit(3)

        Main.turn += 1

        board_paint()
        board_judge()
        time.sleep(0.9 / SPEEDUP)

        past_turns.append(Main.turn)
        past_cell_dicts.append(copy.deepcopy(cell_by_yx))
        past_outs_lists.append(copy.deepcopy(Main.outs))

        if not moves:
            break

        move = random.choice(moves)

        piece = move[0].piece_if
        move[-1].piece_if = piece
        move[0].piece_if = Space


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


if False:

    def print(*args, **kwargs) -> None:
        """Work like a Python Print, or don't"""

        default_eq_Space = " "
        sep = kwargs.get("sep", default_eq_Space)

        line = sep.join(str(_) for _ in args)
        line = line.replace("\x1B", r"\x1B")
        line = line.replace(" ", r"_")

        alt_kwargs = dict(kwargs)
        if "end" in alt_kwargs.keys():
            alt_kwargs["end"] = "\n"

        __builtins__.print(line, **alt_kwargs)


main()
