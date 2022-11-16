#!/usr/bin/env python3

"""
usage: tictactoe.py [-h]

draw Tic-Tac-Toe vividly

options:
  -h, --help  show this help message and exit

quirks:
  accepts coordinates as input:  A 1, A 2, A 3, B 1, B 2, etc
  quits when you input characters outside of printable Ascii

examples:
  git clone https://github.com/pelavarre/byobash.git
  demos/tictactoe.py  # show these examples
  demos/tictactoe.py --  # draw a Tic-Tac-Toe board more vividly than we do by hand
"""

# code reviewed by people, and by Black and Flake8
# developed by:  cls && F=demos/tictactoe.py && black $F && flake8 $F && $F --


import collections
import datetime as dt
import pdb
import sys

import keycaps

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace


#
# Run from the Sh command line
#


def main(sys_argv=None):
    """Run from the Sh command line"""

    keycaps.stroke_print.t0 = None
    keycaps.stroke_print.t1 = dt.datetime.now()
    keycaps.stroke_print.t2 = None

    keycaps.parse_keycaps_args(sys_argv)  # exits if no args, etc
    keycaps.require_tty()

    run_game()


def run_game():
    """Draw a Tic-Tac-Toe board more vividly than we do by hand"""

    cell_by_y = {"1": ".", "2": ".", "3": "."}
    cell_by_x_y = dict(A=dict(cell_by_y), B=dict(cell_by_y), C=dict(cell_by_y))

    run_game.cell_by_x_y = cell_by_x_y
    run_game.turn = "X"
    run_game.x = None
    run_game.y = None

    # Run with keystrokes forwarded when they occur, don't wait for more

    print_board()

    shunting = None
    with keycaps.stdtty_open(sys.stderr) as chatting:
        while True:
            dent = "    "
            keymap = "Press Esc to quit, or one of . - 1 2 3 A B C X O Tab Q"

            choices = [run_game.x, run_game.y, run_game.turn]
            choices = list(_ for _ in choices if _)
            if not choices:
                prompt = dent + "-- {} --".format(keymap)
            else:
                prompt = dent + "-- {} with {} --".format(keymap, " ".join(choices))

            (strokes, millis, t1) = chatting.read_strokes_millis_t1(prompt)

            for (index, stroke) in enumerate(keycaps.strokes_split(strokes)):
                chars = stroke.decode()
                for ch in chars:  # like for when multiple Chars pasted together

                    if ch == "#":
                        shunting = True
                    elif ch in "\r\n":
                        shunting = False

                    if not shunting:
                        take_ch(ch=ch.upper())


def take_ch(ch):
    """Choose a Column, or mutate and print the Tic-Tac-Toe Board"""

    # Choose a Column or Row of Cells

    if ch in "ABC":
        run_game.x = ch
        if run_game.x and run_game.y:
            add_move()

        return

    if ch in "123":
        run_game.y = ch
        if run_game.x and run_game.y:
            add_move()

        return

    # Change the Player

    if ch in "XO.":
        run_game.turn = ch

        return

    # Clear the Board

    if ch in "\b\t-\x7F":  # Backspace Tab Dash Delete
        clear_board()

        return

    # Quit the Game

    if ch in "\x1BQ":  # Esc

        sys.exit()


def clear_board():
    """Clear the Cells, print the Board, pick next Player"""

    cell_by_x_y = run_game.cell_by_x_y

    # Mutate zero or many or all Cells

    before_cells = list_cells()

    for cell_by_y in cell_by_x_y.values():
        for (y, v) in cell_by_y.items():
            cell_by_y[y] = "."

    after_cells = list_cells()

    # Return if no mutation

    if before_cells == after_cells:
        if run_game.x is run_game.y is None:
            if run_game.turn == "X":

                return

    # Trace the Instruction

    print("Tab")

    # Print the mutated Board

    print_board()

    # Start over with X moves first

    run_game.x = None
    run_game.y = None
    run_game.turn = "X"


def add_move():
    """Mutate the Cell, print the Board, pick next Player"""

    cell_by_x_y = run_game.cell_by_x_y

    # Clone the Instruction

    x = run_game.x
    y = run_game.y
    turn = run_game.turn

    # Mutate one Cell, or zero Cells

    before_cells = list_cells()

    cell_by_x_y[x][y] = turn.lower()

    mark_the_wins()
    after_cells = list_cells()

    # Return if no mutation

    if before_cells == after_cells:

        return

    # Trace the Instruction

    dent = "    "

    print(end="\r\n")
    print(dent + "{}{} = {}".format(x, y, turn), end="\r\n")

    # Consume the Instruction

    run_game.x = None
    run_game.y = None
    run_game.turn = None

    # Print the mutated Board

    print_board()

    # Pick the next Player in alternation, else X to above O, else O up to X

    counter = collections.Counter(after_cells)

    if turn == "X":
        turn = "O"
    elif turn == "O":
        turn = "X"
    else:
        turn = "X" if (counter["X"] <= counter["O"]) else "O"

    run_game.turn = turn


def mark_the_wins():  # noqa  # FIXME C901 'mark_the_wins' is too complex (20
    """Uppercase each run of 3 X and each run of 3 O"""

    cell_by_x_y = run_game.cell_by_x_y

    # Transpose the Board

    cell_by_y_x = dict()

    for (x, cell_by_y) in cell_by_x_y.items():
        for (y, cell) in cell_by_y.items():
            if y in cell_by_y_x:
                assert x not in cell_by_y_x[y].keys()
            else:
                cell_by_y_x[y] = dict()

            cell_by_y_x[y][x] = cell

    # List the X and list the Y

    xs = list(cell_by_x_y.keys())
    ys = list(cell_by_y_x.keys())

    # Walk by X to win Columns

    for x in xs:
        x_set = set(cell_by_y_x[y][x] for y in ys)
        if len(x_set) == 1:
            cell = list(x_set)[-1]
            if cell != ".":

                for y in ys:
                    cell_by_x_y[x][y] = cell_by_x_y[x][y].upper()

    # Walk by Y to win Rows

    for y in ys:
        y_set = set(cell_by_x_y[x][y] for x in xs)
        if len(y_set) == 1:
            cell = list(y_set)[-1]
            if cell != ".":

                for x in xs:
                    cell_by_x_y[x][y] = cell_by_x_y[x][y].upper()

    # Walk by X Y and by Y X to win Diagonals

    up_x_set = set()
    for (y, x) in zip(cell_by_y_x.keys(), cell_by_x_y.keys()):
        cell = cell_by_y_x[y][x]
        up_x_set.add(cell)

    if len(up_x_set) == 1:
        cell = list(up_x_set)[-1]
        if cell != ".":
            for (y, x) in zip(cell_by_y_x.keys(), cell_by_x_y.keys()):

                cell_by_x_y[x][y] = cell_by_x_y[x][y].upper()

    down_x_set = set()
    for (y, x) in zip(cell_by_y_x.keys(), reversed(cell_by_x_y.keys())):
        cell = cell_by_y_x[y][x]
        down_x_set.add(cell)

    if len(down_x_set) == 1:
        cell = list(down_x_set)[-1]
        if cell != ".":
            for (y, x) in zip(cell_by_y_x.keys(), reversed(cell_by_x_y.keys())):

                cell_by_x_y[x][y] = cell_by_x_y[x][y].upper()


def list_cells():
    """List the Cells across every Row"""

    cell_by_x_y = run_game.cell_by_x_y

    cells = list(
        cell for cell_by_y in cell_by_x_y.values() for cell in cell_by_y.values()
    )

    return cells


def print_board():
    """Print the Tic-Tac-Toe Board"""

    cell_by_x_y = run_game.cell_by_x_y

    dent = "    "
    dminus = dent[:-1]

    print(end="\r\n")
    print(end="\r\n")
    print(dminus, "", "  A B C", end="\r\n")
    print(end="\r\n")
    for y in "123":
        print(dminus, y, "", end=" ")
        for x in "ABC":
            cell = cell_by_x_y[x][y]
            print(cell, end=" ")
        print(end="\r\n")

    print(end="\r\n")


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


# todo: count the wins
# todo: count the excess of X or O plus Turn - by the rules game is even or +X

# todo: search the rotations, print each distinct
# todo: search the flips of each rotation, assert no distinct found


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/tictactoe.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
