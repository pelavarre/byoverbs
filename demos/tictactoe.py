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


import pdb
import random
import sys

import keycaps

if not hasattr(__builtins__, "breakpoint"):
    breakpoint = pdb.set_trace  # needed till Jun/2018 Python 3.7


DENT = 4 * " "

ESC_STROKES = list()
ESC_STROKES.append("\x1B")  # Esc
ESC_STROKES.append("\x1B[A")  # alt encoding of "\N{Upwards Arrow}" ↑
ESC_STROKES.append("\x1B[B")  # alt encoding of "\N{Downwards Arrow}" ↓
ESC_STROKES.append("\x1B[D")  # alt encoding of "\N{Leftwards Arrow}" ←

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

        g.run_till_quit()


class Game:
    """Interpret Keystrokes"""

    def __init__(self, tui, n):

        self.tui = tui
        self.n = n
        self.board = None

        self.restart()

    def restart(self):
        """Start over"""

        board = self.board
        n = self.n

        if not board:
            self.board = Board(n)
        else:
            board.restart(n)

        self.key = None
        self.func_by_key = self.form_func_by_key()

        self.turn = "X"
        self.x = None
        self.y = None

    def form_func_by_key(self):
        """Choose which Keystroke calls for what action"""

        func_by_key = dict()

        func_by_key.update(
            {
                ".": self.choose_turn,
                "O": self.choose_turn,
                "X": self.choose_turn,
            }
        )

        func_by_key.update(
            {
                "A": self.choose_x,
                "B": self.choose_x,
                "C": self.choose_x,
            }
        )

        func_by_key.update(
            {
                "1": self.choose_y,
                "2": self.choose_y,
                "3": self.choose_y,
            }
        )

        func_by_key.update(
            {
                "\t": self.board_clear,  # Tab
                "\x1B": self.quit_game,  # Esc
                "!": self.move_onto_random,
                "-": self.board_clear,
                "\x08": self.moves_undo_one,  # Backspace  # Control+H
                "H": self.moves_undo_one,
                "J": self.move_onto_empty,
                # "K": self.move_well,
                "Q": self.quit_game,
                "\x7F": self.moves_undo_one,  # Delete  # Control+?
                # "\x1B[A": self.move_well,  # UpwardsArrow ↑
                "\x1B[B": self.move_onto_empty,  # DownwardsArrow ↓
                "\x1B[D": self.moves_undo_one,  # LeftwardsArrow ←
                "\N{Downwards Arrow}": self.move_onto_empty,  # ↓
                "\N{Leftwards Arrow}": self.moves_undo_one,  # ←
                # "\N{Upwards Arrow}": self.move_well,  # ↑
            }
        )

        return func_by_key

    def run_till_quit(self):
        """Run till Quit"""

        board = self.board
        func_by_key = self.func_by_key
        tui = self.tui

        keymap = "123 ABC .XO HJ←↓ ! - Tab Q Esc"

        tui.print()
        tui.print("Press the '#' or Return key, else one of:  {}".format(keymap))
        tui.print("such as:  XC3 OB2 XA1 OC1 XB1 OC2 XA2 OA3  # is an O Win by Fork")

        tui.print()
        board.tui_print_cells(tui)
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

            for key in str_list:  # like for when multiple Chars pasted together

                if key == "#":
                    shunting = True
                elif key in ("\r", "\n"):
                    shunting = False

                if not shunting:
                    if key in func_by_key.keys():

                        func = func_by_key[key]

                        self.key = key
                        func()

                        self.key = None

    def quit_game(self):  # Q Esc
        """Quit the Game"""

        tui = self.tui

        tui.print(DENT + "Q")
        tui.print()

        WAR_GAMES_QUOTE = "A strange game"  # from "War Games" 1983
        WAR_GAMES_QUOTE += ". The only winning move is not to play"
        WAR_GAMES_QUOTE += ". How about a nice game of chess?"

        tui.print(WAR_GAMES_QUOTE)
        tui.print()

        sys.exit()

    def choose_x(self):  # A B C
        """Choose a Column of the Board to move onto"""

        key = self.key

        self.x = key
        if self.y:
            if self.move_onto_x_y():  # changes no Cell when repeating a Move
                self.turn = self.choose_next_turn(after=self.turn)

    def choose_y(self):  # 1 2 3
        """Choose a Row of the Board to move onto"""

        key = self.key

        self.y = key
        if self.x:
            if self.move_onto_x_y():  # changes no Cell when repeating a Move
                self.turn = self.choose_next_turn(after=self.turn)

    def choose_turn(self):  # . O X
        """Choose who moves next"""

        key = self.key

        assert (not self.x) or (not self.y), (self.x, self.y)

        self.turn = key

    def move_onto_x_y(self):  # A B C 1 2 3
        """Mutate the chosen Cell, print the Board, pick next Player"""

        board = self.board
        tui = self.tui

        # Sample the choice of Turn and X and Y

        turn = self.turn
        x = self.x
        y = self.y

        assert x and y, (x, y)

        # Restart the choice of X and Y, while trusting the caller to choose next Turn

        self.x = None
        self.y = None

        # Move and print the resulting Board, else don't

        move = board.add_move(turn, x=x, y=y)
        if move:
            board.tui_print(tui)

        return move

    def choose_next_turn(self, after):  # . X O
        """Pick the next Mark in alternation, else X to above O, else O up to X"""

        board = self.board
        turn = self.turn

        cells = board.cells
        wins = board.wins

        x_cells = list(_ for _ in cells if _.upper() == "X")
        o_cells = list(_ for _ in cells if _.upper() == "O")

        if after == "X":
            turn = "O"
        elif after == "O":
            turn = "X"
        else:
            assert after == ".", after
            turn = "X" if (len(x_cells) <= len(o_cells)) else "O"

        move = board.choose_random_empty_else_none()
        if wins or not move:
            turn = "."

        return turn

    def move_onto_empty(self):  # ↓ DownwardsArrow
        """Move on to a random choice of empty Cell, if any exist"""

        board = self.board
        wins = board.wins

        move = board.choose_random_empty_else_none()
        if wins or not move:

            self.board_clear()

            return

        (empty, x, y) = move

        assert empty == "."
        assert self.turn == self.turn

        self.x = x
        self.y = y
        _ = self.move_onto_x_y()  # changes no Cell when Turn of "."

        self.turn = self.choose_next_turn(after=self.turn)

    def move_onto_random(self):  # !
        """Mutate one Cell chosen at random, print the Board, pick next Player"""

        board = self.board

        move = board.choose_random_mutate()
        (turn, x, y) = move
        self.turn = turn

        self.x = x
        self.y = y
        if not self.move_onto_x_y():
            assert False  # always changes 1 Cell, never returns None
        self.turn = self.choose_next_turn(after=".")

    def moves_undo_one(self):  # Backspace H Delete ← LeftwardsArrow
        """Undo the Last Move"""

        board = self.board
        tui = self.tui

        move = board.moves_undo_one()

        turn = "X"
        if move:
            (turn, x, y) = move
        self.turn = turn

        board.tui_print(tui)

    def board_clear(self):  # - Tab
        """Clear the Board"""

        board = self.board
        tui = self.tui

        self.restart()

        board.tui_print(tui)


class Board:
    """Lay out Cells in a square NxN Grid of '.', 'O', and 'X'"""

    def __init__(self, n):

        self.restart(n)

    def restart(self, n):
        """Start over"""

        # Form the Cells

        assert 1 <= n <= 9

        cells = (n * n) * ["."]

        # Index the Cells

        xs = list("ABCDEFGHI"[:n])
        ys = list("12345679"[:n])

        rxs = list(reversed(xs))
        rys = list(reversed(ys))

        xys = list((x, y) for y in ys for x in xs)

        # Publish the Immutables

        self.n = n

        self.xs = xs
        self.ys = ys
        self.rxs = rxs
        self.rys = rys
        self.xys = xys

        self.streaks = self.form_streaks()

        # Publish the Mutables

        self.cells = cells
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

    def moves_undo_one(self):
        """Undo the Last Move"""

        moves = self.moves
        if not moves:

            return None

        move = moves.pop()
        self._moves_replay()

        return move

    def _moves_replay(self):
        """Wipe the Cells and replay the Moves"""

        cells = self.cells
        moves = self.moves

        cells[::] = list(len(cells) * ["."])
        for after_move in moves:
            (turn, x, y) = after_move
            self.x_y_mutate(x, y, turn)

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
            streak_set = set(cells[xys.index(xy)].upper() for xy in streak)
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

    # FIXME: def choose_well(self):
    # Newell & Simon 1972
    # win, block, fork, block fork, center, opposite corner, empty corner, empty side

    def add_move(self, turn, x, y):
        """Add a Move and return it, else decline the Move and return None"""

        cells = self.cells
        moves = self.moves

        # Try the Move, but decline the Move if it changes no Cells

        before = list(cells)
        self.x_y_mutate(x, y, turn)
        if cells == before:

            return None

        # Add the Move

        move = "{}{}{}".format(turn, x, y)
        moves.append(move)

        # Replay all the Moves, to test the incremental Mutation

        after = list(cells)
        self._moves_replay()
        replayed = list(cells)

        assert after == replayed, (after, replayed)

        # Succeed

        return move

    def _moves_split(self):
        """Split the Handicaps out of the X O Moves in turn"""

        uniques = self._moves_drop_cancelled()

        handicaps = list(uniques)
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

        return uniques

    def tui_print(self, tui):
        """Print the Handicaps, the Moves, and the Cells"""

        # Print the Handicaps and Moves

        (handicaps, xo_moves) = self._moves_split()

        if handicaps:
            tui.print(DENT + " ".join(handicaps))
        if xo_moves:
            tui.print(DENT + " ".join(xo_moves))
        if not (handicaps or xo_moves):
            tui.print(DENT + "Tab")

        # Print the Cells

        tui.print()
        self.tui_print_cells(tui)
        tui.print()

    def tui_print_cells(self, tui):
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


# todo: color the Board as (0 or more X or O Handicaps, X O Move Pairs, X Move)
# todo: keep the Moves as a List
# todo: on adding a Move, work up an incremental prediction, then affirm it
# todo: on deleting a Move, just redraw the Board
# todo: color the Pairs from bright to dim, with no color for Handicaps

# todo: keep a rewind/ ff history on the left right arrows and backspace delete
# todo: up arrow auto strong move

# todo: draw counters not yet placed to fill the blank cells

# todo: sort uniq to reduce flips and rotations, print what remains
# todo: index center cell, corner cells, mid cells

# todo: count the wins
# todo: count the handicaps
# todo: sketch how many X wins vs O wins still possible

# todo: lean more into always doing something in reply to input
# todo: could toggle start with X vs O
# todo: could mark the Board somehow for next X or next O

# todo: 'def run_till_quit' prompts for n != 3


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/tictactoe.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
