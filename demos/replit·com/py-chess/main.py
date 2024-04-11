#!/usr/bin/env python3

"""
usage: main.py

draw a Chess Board and move its Pieces

examples:
  python3 main.py --
"""


# code reviewed by people, and by Black & Flake8 & MyPy

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

... == dict[str, int] | None  # new since Oct/2021 Python 3.10


#
# Name some Chess conventions
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


Pawns = (BlackChessPawn, WhiteChessPawn)
Rooks = (BlackChessRook, WhiteChessRook)
Knights = (BlackChessKnight, WhiteChessKnight)
Bishops = (BlackChessBishop, WhiteChessBishop)
Queens = (BlackChessQueen, WhiteChessQueen)
Kings = (BlackChessKing, WhiteChessKing)


Axials = [(-1, 0), (0, -1), (0, +1), (+1, 0)]
Diagonals = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
Royals = sorted(Axials + Diagonals)

Nobles = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]


#
# Call on a Printer to show a Player working a Board of Cells to please a Judge
#


def main() -> None:
    """Run well, inside a Sh Terminal or Replit Console"""

    fd = sys.stderr.fileno()  # Py Idle raises io.UnsupportedOperation here
    (columns, rows) = os.get_terminal_size(fd)
    if (columns < 50) or (rows < 36):
        print("Try a larger Terminal, such as 50 Rows x 36 Columns", file=sys.stderr)
        sys.exit(1)

    print("\x1B[?25l", end="")  # DecCsiCursorHide  # 06/12 l
    try:
        player.run_awhile()
    finally:
        print("\x1B[?25h", end="")  # DecCsiCursorShow  # 06/12 l
        print(f"\x1B[{board.y1_below}H", end="")
        sys.stdout.flush()
        for _ in range(19):
            print()

    # CUP = "\x1B[H"  # Cursor Position  # 04/08 H
    # CUP_Y1 = "\x1B[{}H"  # Cursor Position  # 04/08 H
    # ED2 = "\x1B[2J"  # 04/10 J  # Erase Screen
    # ED3 = "\x1B[3J"  # 04/10 J  # Erase Scrollback


@dataclasses.dataclass(order=True)
class Player:
    """Play the Game against your Self"""

    stale_boards: list["Board"]

    def __init__(self) -> None:
        self.stale_boards = list()

    def run_awhile(self) -> None:
        """Run well, inside a Sh Terminal or Replit Console"""

        if not printer.at_upper_left():
            ... == board.forward_speed
            board.forward_speed = 100
            # wrong in Upper Left of Shell, but that's rarely tested

        while True:
            print("\x1B[H" + "\x1B[2J" + "\x1B[3J", end="")  # a la Sh 'clear'
            player.play_once()

            print()
            print("Press Return to roll back the Game")
            sys.stdin.readline()

            print("\x1B[H" + "\x1B[2J" + "\x1B[3J", end="")  # a la Sh 'clear'
            player.roll_back()

            print()
            print("Press Return to play again")
            sys.stdin.readline()

    def play_once(self) -> None:
        """Play the Game through, once"""

        cell_by_yx = board.cell_by_yx
        stale_boards = self.stale_boards

        board_cells = list(cell_by_yx.values())

        while True:
            board.turn += 1
            board.paint_cells()

            judge.work_it_out()

            copied = copy.deepcopy(board)
            stale_boards.append(copied)

            time.sleep(1.000 / board.forward_speed)

            kings = list(_ for _ in board_cells if _.piece_if in Kings)
            if len(kings) < 2:
                break
            if not judge.move_list:
                break

            board.make_one_move()

    def roll_back(self) -> None:
        """Roll back the Game"""

        stale_boards = self.stale_boards
        cell_by_yx = board.cell_by_yx

        while stale_boards:
            stale_board = stale_boards.pop()

            for yx, cell in cell_by_yx.items():
                stale_cell = stale_board.cell_by_yx[yx]
                assert stale_cell is not cell, (stale_cell, cell)

                stale_cell.stale_if = ""

                # todo: '= cell.stale_if' doesn't work??
                # todo: not just because clearing all cells before roll back

            stale_board.paint_cells()

            if stale_boards:
                time.sleep(1.000 / board.reverse_speed)

        board.clear()


@dataclasses.dataclass(order=True)
class Printer:
    """Print well, into a Sh Terminal or Replit Console"""

    Plain = "\x1B[m"  # Select Graphic Rendition (SGR)  # 06/13 m

    def __init__(self) -> None:
        default_eq_None = None

        BlackBack = "\x1B[40m"  # SGR 06/13 m  # 40 Black Background
        GrayBack = "\x1B[47m"  # SGR 06/13 m  # 47 White Background
        if os.getenv("REPLIT_ENVIRONMENT", default_eq_None):
            (BlackBack, GrayBack) = (GrayBack, BlackBack)
            # 24/Mar/2024 Replit·Com got these backwards

        self.BlackBack = BlackBack
        self.GrayBack = GrayBack

    def at_upper_left(self) -> bool:
        """Guess if Stderr is to a Replit Console (not Shell)"""

        fd = sys.stderr.fileno()
        y1x1 = self.fd_fetch_cursor_position_report(fd)

        result = y1x1 == (1, 1)
        return result

    def fd_fetch_cursor_position_report(self, fd) -> tuple[int, int]:
        """Silently drop any pending Tty Input, and report Cursor Y1 X1"""

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

    def color_sequence_str(self, color) -> str:
        r"""Convert Color Name to an Unprintable Str such as '\x1B[m'"""

        if color == "Light":
            return self.Plain
        elif color == "Dark":
            return self.GrayBack

        assert False, (color,)  # no need for BlackBack yet

    ... == """

        lots of docs:
          https://unicode.org/charts/PDF/U0000.pdf
          https://unicode.org/charts/PDF/U0080.pdf
          https://en.wikipedia.org/wiki/ANSI_escape_code
          https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
          https://www.ecma-international.org/publications-and-standards/standards/ecma-48
            /wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf

    """


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


@dataclasses.dataclass(order=True)
class Board:
    """Track the State of Play"""

    game_name: str  # name of the Game, which is its Random Seed
    turn: int  # count Turns of Sorting or Scrambling

    cell_by_yx: dict[tuple[int, int], Cell]
    outs: list[str]  # Pieces taken off the Board

    forward_speed = 5
    reverse_speed = 10

    y1_below: int  # Y1 of the first Sh Terminal Line beneath this Board

    def __init__(self) -> None:
        self.clear()

    def clear(self) -> None:
        """Start a new Game"""

        game_name = self.new_game_name()
        # game_name = str(0.000)  # jitter Tue 26/Mar
        self.game_name = game_name

        seed = float(game_name)
        random.seed(seed)

        self.turn = 0
        self.cell_by_yx = dict()
        self.outs = list()

        self.place_empty_cells()
        self.add_eight_pieces_twice()
        self.add_pawns()

    def new_game_name(self) -> str:
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

    def place_empty_cells(self) -> None:
        """Fill this Board with Empty Cells, placed & indexed correctly"""

        cell_by_yx = self.cell_by_yx

        for y in range(8):
            y1 = 1 + 3 + ((7 - y) * 2)
            for x in range(8):
                x1 = 1 + 4 + 2 + (5 * x)

                color = "Light" if ((y + x) % 2) else "Dark"
                cell = Cell(y1=y1, x1=x1, color=color)

                yx = (y, x)
                cell_by_yx[yx] = cell

        assert len(cell_by_yx) == (8 * 8)

        max_y1 = max(_.y1 for _ in cell_by_yx.values())
        self.y1_below = max_y1 + 2

    def add_eight_pieces_twice(self) -> None:
        """Fill the Top Row and Bottom Row with 8 Pieces each"""

        cell_by_yx = self.cell_by_yx

        whos = "Rook Knight Bishop Queen King Bishop Knight Rook".split()

        for y, color in [(7, "Black"), (0, "White")]:
            for x, who in enumerate(whos):
                yx = (y, x)
                cell = cell_by_yx[yx]

                piece = unicodedata.lookup(f"{color} Chess {who}")
                if piece == BlackChessQueen:  # "Queen on her Color"
                    assert cell.color == "Dark", (cell.color, cell)
                elif piece == WhiteChessQueen:
                    assert cell.color == "Light", (cell.color, cell)

                cell.piece_if = piece

    def add_pawns(self) -> None:
        """Fill the 2nd-to-Top Row and 2nd-toBottom Row with 8 Pawns each"""

        cell_by_yx = self.cell_by_yx

        for y, color in [(7 - 1, "Black"), (0 + 1, "White")]:
            for x in range(8):
                yx = (y, x)

                piece = unicodedata.lookup(f"{color} Chess Pawn")
                cell_by_yx[yx].piece_if = piece

    def make_one_move(self) -> None:
        """Move one Piece once"""

        move_list = judge.move_list
        outs = self.outs

        assert move_list, (move_list,)
        move = random.choice(move_list)

        end_piece_if = move[-1].piece_if
        if end_piece_if != Space:
            outs.append(end_piece_if)

        piece = move[0].piece_if
        move[-1].piece_if = piece
        move[0].piece_if = Space

    def paint_cells(self) -> None:
        """Paint over the Board on Screen"""

        cell_by_yx = self.cell_by_yx
        game_name = self.game_name
        outs = self.outs
        turn = self.turn
        y1_below = self.y1_below

        #

        sys.stdout.flush()

        for yx, cell in cell_by_yx.items():
            y1 = cell.y1
            x1 = cell.x1

            (y, x) = yx
            assert y1 == 1 + 3 + ((7 - y) * 2), (y1, yx, cell)
            assert x1 == 1 + 4 + 2 + (5 * x), (x1, yx, cell)

            if cell.stale_if != cell.piece_if:
                cell.stale_if = cell.piece_if

                print(f"\x1B[{y1};{x1 - 2}H", end="")  # CUP_Y1_X1
                if cell.color != "Light":
                    print(printer.color_sequence_str(cell.color), end="")

                print("  " + cell.piece_if + "  ", end="")

                if cell.color != "Light":
                    print(printer.Plain, end="")

                sys.stdout.flush()

        #

        print(f"\x1B[{y1_below}H", end="")  # CUP_Y1
        sys.stdout.flush()

        print()
        print()

        dent = 4 * " "  # trailing Dent needed to roll back
        print(f"{2 * dent}Playing Chess - Turn {turn}{dent}")

        game_name = game_name
        print(f"{3 * dent}Game {game_name}")

        print()
        if not outs:
            print("\x1B[K", end="")  # EL  # needed to roll back
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

                print("\x1B[K", end="")  # EL
                print()

        print("\x1B[K", end="")  # EL
        print()
        sys.stdout.flush()

        print("\x1B[J", end="")  # ED
        sys.stdout.flush()

        # CUP_Y1 = "\x1B[{}H"  # Cursor Position  # 04/08 H
        # CUP_Y1_X1 = "\x1B[{};{}H"  # Cursor Position  # 04/08 H
        # ED = "\x1B[J"  # Erase in Page  # 04/10 J
        # EL = "\x1B[K"  # Erase In Line  # 04/11 K


@dataclasses.dataclass(order=True)
class Judge:
    """Judge the State of Play"""

    move_list: list[list[Cell]]

    def __init__(self) -> None:
        self.move_list = list()

    def work_it_out(self) -> None:
        """Judge the Board"""

        move_list = self.move_list
        move_list.clear()

        self.moves_add_pawns(move_list)

        self.moves_add_bishops(move_list)
        self.moves_add_rooks(move_list)
        self.moves_add_queens(move_list)

        self.moves_add_kings(move_list)
        self.moves_add_knights(move_list)

    def moves_add_bishops(self, move_list) -> None:
        """Move Bishops across Empty Cells into Empty Cells"""

        self._moves_add_thataway_if_(move_list, pieces=Bishops, dy_dx_vectors=Diagonals)

    def moves_add_kings(self, move_list) -> None:
        """Move Kings across Empty Cells into Empty Cells"""

        self._moves_add_thataway_if_(move_list, pieces=Kings, dy_dx_vectors=Royals)

    def moves_add_knights(self, move_list) -> None:
        """Move Knights across Empty Cells into Empty Cells"""

        self._moves_add_thataway_if_(move_list, pieces=Knights, dy_dx_vectors=Nobles)

    def moves_add_pawns(self, move_list) -> None:
        """Move Pawns across Empty Cells into Empty Cells"""

        cell_by_yx = board.cell_by_yx

        for yx, cell in cell_by_yx.items():
            (y, x) = yx

            # Move only Pawns, only ahead

            if cell.piece_if == BlackChessPawn:
                first_y = 7 - 1
                dy = -1
            elif cell.piece_if == WhiteChessPawn:
                first_y = 0 + 1
                dy = +1
            else:
                continue

            self.moves_add_one_pawn(move_list, yx=yx, first_y=first_y, dy=dy)

    def moves_add_one_pawn(self, move_list, yx, first_y, dy) -> None:
        """Move this 1 Pawn across Empty Cells into Empty Cells"""

        cell_by_yx = board.cell_by_yx

        cell = cell_by_yx[yx]
        (y, x) = yx

        # Move to the Cell ahead, or leap to the Cell after that

        step_yx = (y + dy, x)
        if step_yx in cell_by_yx.keys():
            step_cell = cell_by_yx[step_yx]
            if step_cell.piece_if == Space:
                move = [cell, step_cell]
                move_list.append(move)

                if y == first_y:  # leaps only from start
                    leap_yx = (y + 2 * dy, x)
                    leap_cell = cell_by_yx[leap_yx]
                    if leap_cell.piece_if == Space:
                        move = [cell, leap_cell]
                        move_list.append(move)

        # Take the Cell ahead to the left or to the right

        for step_yx in [(y + dy, x - 1), (y + dy, x + 1)]:
            if step_yx in cell_by_yx.keys():
                step_cell = cell_by_yx[step_yx]
                if step_cell.piece_if != Space:
                    move = [cell, step_cell]
                    move_list.append(move)

    def moves_add_queens(self, move_list) -> None:
        """Move Queens across Empty Cells into Empty Cells"""

        self._moves_add_thataway_if_(move_list, pieces=Queens, dy_dx_vectors=Royals)

    def moves_add_rooks(self, move_list) -> None:
        """Move Rooks across Empty Cells into Empty Cells"""

        self._moves_add_thataway_if_(move_list, pieces=Rooks, dy_dx_vectors=Axials)

    def _moves_add_thataway_if_(self, move_list, pieces, dy_dx_vectors) -> None:
        """Move Pieces in a straight Line across Empty Cells into Empty Cells"""

        cell_by_yx = board.cell_by_yx

        SingleSteppers = sorted(Kings + Knights)
        for yx, cell in cell_by_yx.items():
            (y, x) = yx
            piece_if = cell.piece_if

            if piece_if not in pieces:
                continue

            title = unicodedata.name(piece_if).title()
            color = title.split()[0]

            for dy, dx in dy_dx_vectors:
                move = [cell]
                (my, mx) = (y, x)

                while True:
                    step_yx = (my + dy, mx + dx)
                    if step_yx in cell_by_yx.keys():
                        step_cell = cell_by_yx[step_yx]
                        far_piece_if = step_cell.piece_if

                        if far_piece_if == Space:
                            move.append(step_cell)
                            move_list.append(list(move))

                            if cell.piece_if in SingleSteppers:
                                break

                            (my, mx) = step_yx
                            continue

                        far_title = unicodedata.name(far_piece_if).title()
                        far_color = far_title.split()[0]

                        if color != far_color:
                            move.append(step_cell)
                            move_list.append(list(move))
                            break

                    break

        # limits Kings / Knights to move only once, not again and again


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

        # print(f"{len(dir(__builtins__))}")

    # print(mar)
    # print(nov)

    assert ((24 - 8) * 3600) == 57600
    tz = dt.timezone(dt.timedelta(days=-1, seconds=57600))  # Winter
    if (naive >= mar) or (naive < nov):
        tz = dt.timezone(dt.timedelta(days=-1, seconds=61200))  # Summer

    return tz


#
# Create 1 Instance of each Singleton Class,
#   rather than marking every Def as @staticmethod
#


player = Player()
printer = Printer()
board = Board()
judge = Judge()


main()


# todo: number the '8 7 6' Rows top down, and 'a b c' Columns left to right
# todo: print the last move, in long figurine algebraic notation

# todo: accept smaller Screens
# todo: accept Dark Mode Terminals

# todo: left and right arrow to step back and forth through the Game
# todo: Option + Arrow to step faster
# todo: Shift + Arrow to go to either end

# todo: play the Loser's Chess of must choose a take when takes open

# todo: Castling, En Passant, Check, Checkmate, Stalemate, Promotion


# posted into:  https://github.com/pelavarre/byoverbs/tree/main/demos/replit·com
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
