#!/usr/bin/env python3

"""
usage: tictactoe.py [-h]

draw a Tic-Tac-Toe Board more vividly than we do by hand

options:
  -h, --help  show this help message and exit

quirks:
  plots X or O or . in your A B C choice of column and 1 2 3 choice of row
  chooses X after O, or O after X for you, but lets you choose X or O or . if you like
  steps the Game forward by one random Move, when you press the ↓ Downwards Arrow key
  mutates some random Cell randomly, when you press the ! Bang key (the ⇧1 chord)
  clears the Board when you press Tab or the - Dash key
  quits the Game when you press Q or Esc

examples:
  git clone https://github.com/pelavarre/byoverb.git
  demos/tictactoe.py  # show these examples
  demos/tictactoe.py --  # draw a Tic-Tac-Toe Board more vividly than we do by hand
"""

# code reviewed by people, and by Black and Flake8
# developed by:  cls && F=demos/tictactoe.py && black $F && flake8 $F && $F --


import collections
import pdb
import random
import sys

import keycaps

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace  # needed till Jun/2018 Python 3.7


DENT = 4 * " "

ESC_STROKES = list()
ESC_STROKES.append("\x1B")  # Esc
ESC_STROKES.append("\x1B[B")  # alt encoding of "\N{Downwards Arrow}" ↓

TURNS = "XO."


#
# Run from the Sh command line
#


def main(sys_argv=None):
    """Run from the Sh command line"""

    keycaps.parse_keycaps_args(sys_argv)  # exits if no args, etc
    keycaps.require_tui()
    with keycaps.tui_open(sys.stderr) as tui:
        g = Game(tui, n=3)

        g.run_once()


class Game:
    """Interpret Keystrokes"""

    def __init__(self, tui, n):

        self.tui = tui
        self.n = n

        self.start()

    def start(self):
        """Start over"""

        n = self.n

        self.board = Board(n)
        self.turn = "X"
        self.x = None
        self.y = None

    def run_once(self):
        """Run once"""

        board = self.board
        tui = self.tui

        keymap = "123 ABC .XO ↓ ! - Tab Q Esc"

        tui.print()
        tui.print("Press the '#' or Return key, else one of:  {}".format(keymap))
        tui.print("such as:  XC3 OB2 XA1 OC1 XB1 OC2 XA2 OA3  # is an O Win by Fork")

        tui.print()
        board.tui_print(tui)
        tui.print()

        shunting = None
        while True:

            choices = [self.turn, self.x, self.y]
            choices = list(_ for _ in choices if _)

            template = "Press Q or Esc to quit, else some other key, after:  {}"
            prompt = DENT + template.format("".join(choices))

            tui.kbprompt_write(prompt)
            stroke = tui.readline()
            tui.kbprompt_erase(prompt)

            chars = stroke.decode()

            str_list = [chars]
            if not chars.startswith("\x1B"):
                str_list = list(chars)
            str_list = list((_.upper() if (len(_) == 1) else _) for _ in str_list)

            for chars in str_list:  # like for when multiple Chars pasted together

                if chars == "#":
                    shunting = True
                elif chars in ("\r", "\n"):
                    shunting = False

                if not shunting:
                    self.take_chars(chars)

    def take_chars(self, chars):
        """Choose a Column, or mutate and print the Tic-Tac-Toe Board"""

        tui = self.tui

        assert TURNS == "XO."

        # Choose a Column or Row of Cells

        if chars in ("A", "B", "C"):
            self.x = chars
            self.move_onto_x_y()

            return

        if chars in ("1", "2", "3"):
            self.y = chars
            self.move_onto_x_y()

            return

        # Change the Player

        if chars in ("X", "O", "."):
            self.turn = chars
            self.move_onto_x_y()

            return

        # Move next at a random Cell

        if chars in ("\x1B[B", "\N{Downwards Arrow}"):
            self.move_onto_empty()

            return

        # Inject a random mutation

        if chars in ("!",):
            self.mutate_one_cell()

            return

        # Clear the Board

        if chars in ("\t", "-"):  # Tab Dash
            self.board_clear()

            return

        # Quit the Game

        if chars in ("\x1B", "Q"):  # Esc Q

            tui.print(DENT + "Q")
            tui.print()

            sys.exit()

    def move_onto_x_y(self):
        """Mutate the chosen Cell, print the Board, pick next Player"""

        board = self.board
        tui = self.tui
        turn = self.turn
        x = self.x
        y = self.y

        # Return early if no Row or no Column chosen

        if not (x and y):

            return

        # Mutate the chosen Cell, else leave it unchanged and return early

        before = list(board.cells)
        board.x_y_mutate(x, y, turn)

        if board.cells == before:

            return

        # Print the mutated Board as zero or more Handicaps, plus X O moves in turn

        move = "{}{}{}".format(turn, x, y)
        (handicaps, xo_moves) = board.add_move(move)

        if handicaps:
            tui.print(DENT + " ".join(handicaps))
        if xo_moves:
            tui.print(DENT + " ".join(xo_moves))
        if not (handicaps or xo_moves):
            tui.print(DENT + "Tab")

        # Print the mutated Board

        tui.print()
        board.tui_print(tui)
        tui.print()

        # Mutate the Turn too

        self.turn = self.choose_next_turn()
        self.x = None
        self.y = None

    def choose_next_turn(self):
        """Pick the next Mark in alternation, else X to above O, else O up to X"""

        board = self.board
        turn = self.turn

        cells = board.cells

        counter = collections.Counter(cells)

        if turn == "X":
            turn = "O"
        elif turn == "O":
            turn = "X"
        else:
            turn = "X" if (counter["X"] <= counter["O"]) else "O"

        return turn

    def move_onto_empty(self):  # ↓
        """Move on to a random choice of empty Cell, if any exist"""

        board = self.board

        move = board.choose_random_empty_else_none()
        if board.wins or not move:

            self.board_clear()

        else:

            (empty, x, y) = move

            assert empty == "."
            assert self.turn == self.turn

            self.x = x
            self.y = y

            self.move_onto_x_y()

    def mutate_one_cell(self):  # !
        """Mutate one Cell chosen at random, print the Board, pick next Player"""

        board = self.board

        move = board.choose_random_mutate()
        (turn, x, y) = move

        self.turn = turn
        self.x = x
        self.y = y

        self.move_onto_x_y()

    def board_clear(self):
        """Clear the Board"""

        tui = self.tui

        tui.print(DENT + "Tab")

        self.start()

        tui.print()
        self.board.tui_print(tui)
        tui.print()


class Board:
    """Lay out Cells in a square NxN Grid of '.', 'O', and 'X'"""

    def __init__(self, n):

        # Form the Cells

        assert 1 <= n <= 9

        cells = (n * n) * ["."]

        # Index the Cells

        xs = list("ABCDEFGHI"[:n])
        ys = list("12345679"[:n])

        rxs = list(reversed(xs))
        rys = list(reversed(ys))

        xys = list((x, y) for y in ys for x in xs)

        # Publish the Indices and the Cells

        self.n = n
        self.cells = cells

        self.xs = xs
        self.ys = ys
        self.rxs = rxs
        self.rys = rys
        self.xys = xys

        self.streaks = self.form_streaks()

        self.moves = list()
        self.wins = list()

    def form_streaks(self):
        """List the ways to win"""

        xs = self.xs
        ys = self.ys
        rys = self.rys

        streaks = list()

        for y in ys:  # rows
            streak = list((x, y) for x in xs)
            streaks.append(streak)

        for x in xs:  # columns
            streak = list((x, y) for y in ys)
            streaks.append(streak)

        streak = list((x, y) for (x, y) in zip(xs, ys))
        streaks.append(streak)  # diagonal - upper left to lower right

        streak = list((x, y) for (x, y) in zip(xs, rys))
        streaks.append(streak)  # diagonal - upper right to lower left

        return streaks

    def x_y_mutate(self, x, y, turn):
        """Mutate the one Cell at X, Y"""

        cells = self.cells
        xys = self.xys

        xy = (x, y)
        index = xys.index(xy)
        cells[index] = turn.lower()

        self.mark_wins_and_losses()

    def mark_wins_and_losses(self):
        """Mark Streaks in upper case, the other cells in lower case"""

        cells = self.cells
        xys = self.xys
        streaks = self.streaks
        wins = self.wins

        wins.clear()

        for xy in xys:
            index = xys.index(xy)
            cells[index] = cells[index].lower()

        for streak in streaks:
            streak_set = set(cells[xys.index(xy)] for xy in streak)
            if len(streak_set) == 1:
                cell = list(streak_set)[-1]
                if cell != ".":

                    wins.append(streak)

                    for xy in streak:
                        index = xys.index(xy)
                        cells[index] = cells[index].upper()

    def choose_random_empty_else_none(self):
        """Choose one empty Cell at random"""

        cells = self.cells
        xys = self.xys

        empty_xys = list(_ for _ in xys if cells[xys.index(_)] == ".")
        if not empty_xys:

            return None

        xy = random.choice(empty_xys)

        turn = "."
        (x, y) = xy

        move = "{}{}{}".format(turn, x, y)

        return move

    def choose_random_mutate(self):
        """Choose one Cell at random and also choose randomly how to mutate it"""

        cells = self.cells
        xys = self.xys

        xy = random.choice(xys)
        index = xys.index(xy)
        turn_before = cells[index].upper()

        turns = list(TURNS)
        turns.remove(turn_before)

        turn = random.choice(turns)
        (x, y) = xy

        move = "{}{}{}".format(turn, x, y)

        return move

    def add_move(self, move):
        """Add a Move, but then separate the Handicaps from X O Moves in turn"""

        moves = self.moves

        # Add the one Move, but drop any Move it cancels

        moves.append(move)

        self._moves_drop_cancelled()

        # Split the Handicaps out of the X O Moves in turn

        handicaps = list(moves)
        xo_moves = list()

        turn = "X"
        while handicaps:
            fitting_moves = list(_ for _ in handicaps if _.startswith(turn))
            if fitting_moves:
                move = fitting_moves[0]
                handicaps.remove(move)
                xo_moves.append(move)

                turn = "X" if (turn != "X") else "O"

                continue

            break

        return (handicaps, xo_moves)

    def _moves_drop_cancelled(self):
        """Drop the earlier moves cancelled by later moves"""

        moves = self.moves

        uniques = list()

        xys_set = set()
        for move in reversed(moves):
            assert len(move) == len("Oxy")

            (turn, x, y) = move
            xy = (x, y)

            if xy not in xys_set:
                xys_set.add(xy)
                if turn != ".":
                    uniques.append(move)

        uniques = list(reversed(uniques))
        moves[::] = uniques

    def tui_print(self, tui):
        """Print the Cells"""

        cells = self.cells

        xs = self.xs
        ys = self.ys
        xys = self.xys

        dminus = DENT[:-1]

        tui.print(dminus, "", "", "", " ".join(self.xs))
        tui.print()
        for y in ys:
            tui.print(dminus, y, "", end=" ")
            for x in xs:
                xy = (x, y)
                index = xys.index(xy)
                cell = cells[index]
                tui.print(cell, end=" ")
            tui.print()


#
# Git-Track some Test Input
#


_ = """

    # diagonals
    - XA1 XB2 XC3
    - XC1 XB2 XA3
    - OA1 OB2 OC3
    - OC1 OB2 OA3

    # rows
    - OA1 OB1 OC1
    - OA2 OB2 OC2
    - OA3 OB3 OC3

    # columns
    - OA1 OA2 OA3 - OB1 OB2 OB3 - OC1 OC2 OC3

    # draw
    - XB2 OA1 XC3 OC1 XB1 OB3 XC2 OA2 XA3

    # x fork win
    - XB2 OB1 XA1 OC3 XA2 OC2 XA3

    # quit
    Q

"""


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main(sys.argv)


# todo: keep a rewind/ ff history on the left right arrows and backspace delete
# todo: up arrow auto strong move

# todo: draw counters not yet placed to fill the blank cells

# todo: sort uniq to reduce flips and rotations, print what remains
# todo: index center cell, corner cells, mid cells
# todo: colour X O pairs of bursts of moves by age
# todo: colour handicap X O

# todo: count the wins
# todo: count the handicaps
# todo: sketch how many X wins vs O wins still possible

# todo: lean into always doing something in reply to input
# todo: could toggle start with X vs O
# todo: could mark the Board somehow for next X or next O

# todo: 'def run_once' prompts for n != 3


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/tictactoe.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
