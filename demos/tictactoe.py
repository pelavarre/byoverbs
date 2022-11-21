#!/usr/bin/env python3

"""
usage: tictactoe.py [-h]

draw a Tic-Tac-Toe Board more vividly than we do by hand

options:
  -h, --help  show this help message and exit

quirks:
  plots X or O or . in your A B C choice of column and 1 2 3 choice of row
  choose X after O, or O after X for you, but lets you choose X or O or . if you like
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
import sys

import keycaps

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace  # needed till Jun/2018 Python 3.7


DENT = 4 * " "


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
        self.moves = list()
        self.turn = "X"
        self.x = None
        self.y = None

    def run_once(self):
        """Run once"""

        board = self.board
        moves = self.moves
        tui = self.tui

        tui.print()
        tui.print("Press the '#' or Return key, else one of:  123 ABC .XO - Tab Q Esc")
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

            for ch in chars:  # like for when multiple Chars pasted together

                if ch == "#":
                    shunting = True
                elif ch in "\r\n":
                    shunting = False

                if not shunting:
                    self.take_ch(ch=ch.upper())

    def take_ch(self, ch):
        """Choose a Column, or mutate and print the Tic-Tac-Toe Board"""

        tui = self.tui

        # Choose a Column or Row of Cells

        if ch in "ABC":
            self.x = ch
            self.move_once()

            return

        if ch in "123":
            self.y = ch
            self.move_once()

            return

        # Change the Player

        if ch in "XO.":
            self.turn = ch

            return

        # Clear the Board

        if ch in "\t-":  # Tab Dash
            tui.print(DENT + "Tab")

            self.start()

            tui.print()
            self.board.tui_print(tui)
            tui.print()

            return

        # Quit the Game

        if ch in "\x1BQ":  # Esc
            tui.print(DENT + "Q")
            tui.print()

            sys.exit()

    def move_once(self):
        """Mutate the Cell, print the Board, pick next Player"""

        board = self.board
        moves = self.moves
        tui = self.tui
        turn = self.turn
        x = self.x
        y = self.y

        # Return early if no Row or no Column chosen

        if not (x and y):

            return

        # Mutate one Cell, else return early

        before = list(board.cells)
        board.x_y_mutate(x, y, turn)

        if board.cells == before:

            return

        # Trace the instruction

        move = "{}{}{}".format(turn, x, y)
        moves.append(move)

        tui.print(DENT + " ".join(moves))

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

        for xy in xys:
            index = xys.index(xy)
            cells[index] = cells[index].lower()

        for streak in streaks:
            streak_set = set(cells[xys.index(xy)] for xy in streak)
            if len(streak_set) == 1:
                cell = list(streak_set)[-1]
                if cell != ".":

                    for xy in streak:
                        index = xys.index(xy)
                        cells[index] = cells[index].upper()

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

# todo: up arrow auto move
# todo: down arrow random move
# todo: bang random mutate
# todo: keep a rewind/ ff history on the left right arrows and backspace delete

# todo: draw counters not yet placed to fill the blank cells

# todo: sort uniq to reduce flips and rotations, print what remains
# todo: index center cell, corner cells, mid cells
# todo: colour X O pairs of bursts of moves by age

# todo: count the streaks
# todo: count the excess of X or O plus Turn
# todo: sketch how many X wins vs O wins still possible

# todo: lean into always doing something in reply to input
# todo: could toggle start with X vs O
# todo: could mark the Board somehow for next X or next O

# todo: 'def run_once' prompts for n != 3


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/tictactoe.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
