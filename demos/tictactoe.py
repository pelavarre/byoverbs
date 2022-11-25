#!/usr/bin/env python3

"""
usage: tictactoe.py [-h]

draw a Tic-Tac-Toe Board more vividly than we do by hand

options:
  -h, --help  show this help message and exit

quirks:
  plots X or O or . in your A B C choice of column and 1 2 3 choice of row
  chooses X after O, or O after X for you, but lets you choose X or O or . if you like
  undoes your last Move, when you press the ← Leftwards Arrow key
  redoes your last Undone Move, when you press the → Rightwards Arrow key
  steps the Game forward by trying to win, when you press the ↑ Upwards Arrow key
  steps the Game forward by one random Move, when you press the ↓ Downwards Arrow key
  mutates some random Cell randomly, when you press the ! Bang key (the ⇧1 chord)
  clears the Board when you press Tab or the - Dash key
  quits the Game when you press Q or Esc

examples:
  git clone https://github.com/pelavarre/byoverb.git
  demos/tictactoe.py  # show these examples
  demos/tictactoe.py --  # draw a Tic-Tac-Toe Board more vividly than we do by hand
  # colors X O . moves into Cells as:   color color color color color
"""


# code reviewed by people, and by Black and Flake8
# developed by:  cls && F=demos/tictactoe.py && black $F && flake8 $F && $F --


import __main__
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
ESC_STROKES.append("\x1B[A")  # alt encoding of "\N{Upwards Arrow}" ↑
ESC_STROKES.append("\x1B[B")  # alt encoding of "\N{Downwards Arrow}" ↓
ESC_STROKES.append("\x1B[C")  # alt encoding of "\N{Upwards Arrow}" ↓
ESC_STROKES.append("\x1B[D")  # alt encoding of "\N{Leftwards Arrow}" ←

TURNS = "XO."


COLOR_CHARS_FORMAT = "\x1B[{}m{}\x1B[0m"
assert keycaps.COLOR_CHARS_FORMAT == COLOR_CHARS_FORMAT

TOO_BRIGHT_COLORS = keycaps.BRIGHT_COLORS[:1]
TOO_DARK_COLORS = keycaps.DARK_COLORS[:2]

COLOR_BY_MOVE = list(reversed(keycaps.COLOR_BY_AGE))
COLOR_BY_MOVE = list(_ for _ in COLOR_BY_MOVE if _ not in TOO_BRIGHT_COLORS)
COLOR_BY_MOVE = list(_ for _ in COLOR_BY_MOVE if _ not in TOO_DARK_COLORS)

N = 3
assert len(COLOR_BY_MOVE) >= ((N * N + 1) // 2), (len(COLOR_BY_MOVE), N)

assert len(COLOR_BY_MOVE) == 5, len(COLOR_BY_MOVE)
COLOR_AS = " ".join(COLOR_CHARS_FORMAT.format(_, "color") for _ in COLOR_BY_MOVE)
__main__.__doc__ = __main__.__doc__.replace(5 * " color", " " + COLOR_AS)


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

        self.keyhelp = ".XO ABC 123 ! ←↑↓→ - Tab # Return ? / Q Esc"  # AWSD HKJL
        self.chords = list()
        self.helps = list()

        self.restart_game()

    def restart_game(self):  # FIXME: fuzzy thinking near suspend/ resume/ clear
        """Start over"""

        board = self.board
        n = self.n

        if not board:
            self.board = Board(n)
        else:
            board.restart_board(n)

        self.key = None
        self.func_by_key = self.form_func_by_key()

        self.turn = "X"
        self.x = None
        self.y = None

        self.chords_helps_clear()

    def chords_helps_clear(self):
        """Restart collecting input, like after each Move"""

        self.chords.clear()
        self.helps.clear()

    def form_func_by_key(self):
        """Choose which Keystroke calls for what action"""

        func_by_key = dict()

        func_by_key.update(
            {
                "\x03": self.quit_game,  # ⌃C SIGINT KeyboardInterrupt
                "\x1C": self.quit_game,  # ⌃\ SIGQUIT
                "\x08": self.moves_undo_one,  # Backspace ⌃H
                "\x0A": self.move_onto_empty,  # Enter ⌃J
                "\x0D": self.move_onto_empty,  # Return ⌃M
                "\t": self.game_board_clear,  # Tab ⌃I
                "\x1B": self.quit_game,  # Esc ⌃[
                "!": self.move_onto_random,
                "Q": self.quit_game,
                "\x7F": self.moves_undo_one,  # Delete  # classic ⌃? but not at Mac
                "\x1B[A": self.move_to_win,  # UpwardsArrow ↑
                "\x1B[B": self.move_onto_empty,  # DownwardsArrow ↓
                "\x1B[C": self.moves_redo_one,  # RightwardsArrow →
                "\x1B[D": self.moves_undo_one,  # LeftwardsArrow ←
                "\N{Downwards Arrow}": self.move_onto_empty,  # ↓
                "\N{Leftwards Arrow}": self.moves_undo_one,  # ←
                "\N{Rightwards Arrow}": self.moves_undo_one,  # →
                "\N{Upwards Arrow}": self.move_to_win,  # ↑
            }
        )

        func_by_key["-"] = func_by_key["\t"]
        func_by_key["Q"] = func_by_key["\x1B"]

        func_by_key["H"] = func_by_key["\N{Leftwards Arrow}"]  # H mutated by 8x8 games
        func_by_key["K"] = func_by_key["\N{Upwards Arrow}"]
        func_by_key["J"] = func_by_key["\N{Downwards Arrow}"]
        func_by_key["L"] = func_by_key["\N{Rightwards Arrow}"]

        func_by_key["A"] = func_by_key["\N{Leftwards Arrow}"]  # A mutated below
        func_by_key["W"] = func_by_key["\N{Upwards Arrow}"]
        func_by_key["S"] = func_by_key["\N{Downwards Arrow}"]
        func_by_key["D"] = func_by_key["\N{Rightwards Arrow}"]  # D mutated by 4x4 games

        func_by_key.update(
            {
                ".": self.choose_turn,
                "O": self.choose_turn,
                "X": self.choose_turn,
            }
        )

        func_by_key.update(
            {
                "A": self.choose_x,  # mutates ["A"] above
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

        return func_by_key

    def run_till_quit(self):
        """Run till Quit"""

        board = self.board
        helps = self.helps
        tui = self.tui

        color_chars_format = "\x1B[{}m{}\x1B[0m"
        assert keycaps.COLOR_CHARS_FORMAT == color_chars_format

        str_moves = list()
        for (index, move) in enumerate("XC3 OB2 XA1 OC1 XB1 OC2 XA2 OA3".split()):
            color = COLOR_BY_MOVE[index // 2]
            str_move = color_chars_format.format(color, move)
            str_moves.append(str_move)

        tui.print()
        tui.print(DENT + "An O Win By Fork is:  " + " ".join(str_moves))

        tui.print()
        self.tui_print_keyhelp()
        tui.print()

        board.tui_print_cells(tui)
        tui.print()

        shunting = False
        while True:

            choices = [self.turn, self.x, self.y]
            choices = list(_ for _ in choices if _)

            template = "Got {} so next press ABC or Tab or Q or ? or some other key"
            if self.x:
                template = "Got {} so next press 123 or Tab or Q or ? or some other key"

            prompt = DENT + template.format(" ".join(choices)) + " "
            (keys, chord) = self.tui_read_keys(prompt)

            for key in keys:

                if key == "#":
                    shunting = True
                elif shunting and (key in ("\r", "\n")):
                    shunting = False
                elif not shunting:

                    if key in ("/", "?"):  # '/' because '?' at ⇧ /
                        if not helps:
                            self.help_game(keys, key=key, chord=chord)
                            helps.append(1)
                    else:
                        self.run_one_key(keys, key=key, chord=chord)

    def run_one_key(self, keys, key, chord):
        """Run one Key"""

        chords = self.chords
        func_by_key = self.func_by_key

        alt_key = key.upper()
        if alt_key not in func_by_key.keys():

            return

        if chord and (len(keys) == 1):
            chords.append(chord)
        else:
            chords.append(alt_key)

        func = func_by_key[alt_key]

        self.key = alt_key
        func()

        self.key = None

    def tui_read_keys(self, prompt):
        """Block till next Keystroke, or till next Paste of Keystrokes"""

        tui = self.tui

        tui.kbprompt_write(prompt)
        stroke = tui.readline()
        tui.kbprompt_erase(prompt)

        chars = stroke.decode()

        default_empty = []
        keycap_lists = keycaps.KEYCAP_LISTS_BY_STROKE.get(stroke, default_empty)

        chord = None
        if keycap_lists:

            chord = "".join(keycap_lists[0].split())
            if chord == "⇧1":
                chord = "!"
            elif chord == "⇧/":
                chord = "?"
            elif chord == "\N{Up Arrowhead}" "[":  # "⌃["
                chord = "Esc"
            elif chord == "\N{Up Arrowhead}" "I":  # "⌃I"
                chord = "Tab"
            elif chord == "\N{Up Arrowhead}" "J":  # "⌃J"
                chord = "Enter"
            elif chord == "\N{Up Arrowhead}" "M":  # "⌃M"
                chord = "Return"

        keys = [chars]
        if not chars.startswith("\x1B"):
            keys = list(chars)

        return (keys, chord)

        # <= FIXME: excessive coupling with 'import keycaps'

    def help_game(self, keys, key, chord):  # ? /
        """Help the Game"""

        tui = self.tui

        echo = key
        if chord and (len(keys) == 1):
            echo = chord

        tui.print(DENT + "input " + echo)
        tui.print()

        self.tui_print_keyhelp()
        tui.print()

    def tui_print_keyhelp(self):
        """Print the Key Help at Launch, Restart, Quit or on demand"""

        keyhelp = self.keyhelp
        tui = self.tui

        tui.print(DENT + "Press one of", keyhelp)

    def quit_game(self):  # Q Esc
        """Quit the Game"""

        chords = self.chords
        tui = self.tui

        tui.print(DENT + " ".join(chords))
        tui.print()

        self.chords_helps_clear()

        WAR_GAMES_QUOTE = "A strange game"  # from "War Games" 1983
        WAR_GAMES_QUOTE += ". The only winning move is not to play"
        WAR_GAMES_QUOTE += ". How about a nice game of chess?"

        tui.print(WAR_GAMES_QUOTE)
        tui.print()

        sys.exit()

    def choose_x(self):  # A B C
        """Choose a Column of the Board to move onto"""

        key = self.key
        turn = self.turn

        self.x = key
        if self.y:
            self.move_onto_x_y(after=turn)  # changes no Cell when repeating a Move

    def choose_y(self):  # 1 2 3
        """Choose a Row of the Board to move onto"""

        key = self.key
        turn = self.turn

        self.y = key
        if self.x:
            self.move_onto_x_y(after=turn)  # changes no Cell when repeating a Move

    def choose_turn(self):  # . O X
        """Choose who moves next"""

        key = self.key

        assert (not self.x) or (not self.y), (self.x, self.y)

        self.turn = key

    def move_to_win(self):  # K ↑ UpwardsArrow
        """Choose a Column of the Board to move onto"""

        board = self.board
        turn = self.turn

        if turn == ".":

            self.game_board_clear()

            return

        move = board.choose_shove_in(turn)
        if move:
            (move_turn, x, y) = move

            assert move_turn == turn

            self.x = x
            self.y = y

            self.move_onto_x_y(after=turn)  # always changes 1 Cell

    def move_onto_x_y(self, after):  # called by A B C 1 2 3, but also by# ! ↑ ↓
        """Mutate the chosen Cell, print the Board, pick next Player"""

        board = self.board
        chords = self.chords
        tui = self.tui

        # Sample the choice of Turn and X and Y

        turn = self.turn
        x = self.x
        y = self.y

        assert x and y, (x, y)

        # Restart the choice of X and Y, while trusting the caller to choose next Turn

        self.x = None
        self.y = None

        # Move, pick the next mark, and print the resulting Board, else don't

        move = board.add_move(turn, x=x, y=y)
        if move:
            self.turn = self.choose_next_turn(after=after)

            board.tui_turn_chords_print(tui, turn=self.turn, chords=chords)
            self.chords_helps_clear()

        return move

    def choose_next_turn(self, after):  # . X O
        """Pick the next Mark in alternation, else X to above O, else O up to X"""

        board = self.board
        turn = self.turn

        cells = board.cells
        streaks_by_winner = board.streaks_by_winner

        x_cells = list(_ for _ in cells if _.upper() == "X")
        o_cells = list(_ for _ in cells if _.upper() == "O")

        if after == "X":
            turn = "O"
        elif after == "O":
            turn = "X"
        else:
            assert after == ".", after
            turn = "X" if (len(x_cells) <= len(o_cells)) else "O"

        move = board.choose_random_empty_else()
        if streaks_by_winner or not move:
            turn = "."

        return turn

    def move_onto_empty(self):  # J ↓ DownwardsArrow
        """Move on to a random choice of empty Cell, if any exist"""

        board = self.board
        turn = self.turn
        streaks_by_winner = board.streaks_by_winner

        move = board.choose_random_empty_else()
        if streaks_by_winner or not move:

            self.game_board_clear()

            return

        (before, x, y) = move

        assert before == "."

        self.x = x
        self.y = y
        self.move_onto_x_y(after=turn)  # changes no Cell when Turn of "."

    def move_onto_random(self):  # !
        """Mutate one Cell chosen at random, print the Board, pick next Player"""

        board = self.board

        move = board.choose_random_mutate()
        (turn, x, y) = move
        self.turn = turn

        self.x = x
        self.y = y
        self.move_onto_x_y(after=".")  # always changes 1 Cell

    def moves_undo_one(self):  # Backspace H Delete ← LeftwardsArrow
        """Undo the Last Move"""

        board = self.board
        chords = self.chords
        tui = self.tui

        move = board.moves_undo_one()

        if not move:
            self.turn = "X"
        else:
            (turn, x, y) = move
            self.turn = turn

            board.tui_turn_chords_print(tui, turn=self.turn, chords=chords)
            self.chords_helps_clear()

    def moves_redo_one(self):  # L → RightwardsArrow
        """Redo the Last Undone"""

        board = self.board
        chords = self.chords
        tui = self.tui

        move = board.moves_redo_one()

        if move:
            (turn, x, y) = move
            self.turn = turn

            board.tui_turn_chords_print(tui, turn=self.turn, chords=chords)
            self.chords_helps_clear()

    def game_board_clear(self):  # - Tab
        """Clear the Board"""

        board = self.board
        chords = self.chords
        tui = self.tui

        tui.print(DENT + "input " + " ".join(chords))
        tui.print()
        tui.print()
        self.tui_print_keyhelp()
        self.restart_game()
        board.tui_turn_chords_print(tui, turn=self.turn, chords=chords)
        self.chords_helps_clear()


class Board:
    """Lay out Cells in a square NxN Grid of '.', 'O', and 'X'"""

    def __init__(self, n):

        self.restart_board(n)

    def restart_board(self, n):
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

        self.center_xys = self.form_center_xys()
        self.corner_xys = self.form_corner_xys()
        self.side_xys = self.form_side_xys()

        # Publish the Mutables

        self.cells = cells
        self.moves = list()
        self.undos = list()
        self.streaks_by_winner = dict()

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

    def form_center_xys(self):
        """List the Center Cell as a List of 1 Cell"""

        xs = self.xs
        ys = self.ys

        x = xs[len(xs) // 2]
        y = ys[len(ys) // 2]

        xy = (x, y)
        center_xys = [xy]

        return center_xys

    def form_corner_xys(self):
        """List the Corner Cells"""

        xs = self.xs
        ys = self.ys

        corner_xys = list()
        for x in (xs[0], xs[-1]):
            for y in (ys[0], ys[-1]):
                xy = (x, y)

                corner_xys.append(xy)

        return corner_xys

    def form_side_xys(self):
        """List the Side Cells"""

        xs = self.xs
        ys = self.ys

        side_xys = list()

        x = xs[len(xs) // 2]
        for y in (ys[0], ys[-1]):
            xy = (x, y)

            side_xys.append(xy)

        y = ys[len(ys) // 2]
        for x in (xs[0], xs[-1]):
            xy = (x, y)

            side_xys.append(xy)

        return side_xys

    def moves_undo_one(self):
        """Undo the Last Move"""

        moves = self.moves
        undos = self.undos

        if not moves:

            return None

        move = moves.pop()
        undos.append(move)

        self._moves_replay()

        return move

    def moves_redo_one(self):
        """Redo the Last Undone"""

        moves = self.moves
        undos = self.undos

        if not undos:

            return None

        move = undos.pop()
        moves.append(move)

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
        streaks_by_winner = self.streaks_by_winner

        streaks_by_winner.clear()

        for xy in xys:
            index = xys.index(xy)
            cells[index] = cells[index].lower()

        for streak in streaks:
            streak_set = set(cells[xys.index(xy)].upper() for xy in streak)
            if len(streak_set) == 1:
                cell = list(streak_set)[-1]
                if cell != ".":
                    if cell not in streaks_by_winner.keys():
                        streaks_by_winner[cell] = list()

                    streaks_by_winner[cell].append(streak)

                    for xy in streak:
                        index = xys.index(xy)
                        cells[index] = cells[index].upper()

    def choose_random_empty_else(self):
        """Choose one empty Cell at random"""

        empty_xys = self.find_empty_xys()
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

    def choose_shove_in(self, turn):
        """Say how to max chance of winning"""

        moves = self.moves
        xys = self.xys

        # Stop moving after moving into the last Cell

        empty_xys = self.find_empty_xys()
        if not empty_xys:

            return None

        # Rank goals, much in the way of Newell & Simon 1972
        # as paraphrased by:  https://en.wikipedia.org/wiki/Tic-tac-toe

        voters = list()
        voters.append(self.side_xys)  # 0x1
        voters.append(self.corner_xys)  # 0x2
        voters.append(self.center_xys)  # 0x4
        voters.append(self.find_opposite_corner_xys)  # 0x8
        voters.append(self.find_block_fork_xys)  # 0x10
        voters.append(self.find_threaten_win_xys)  # 0x20
        voters.append(self.find_fork_xys)  # 0x40
        voters.append(self.find_block_win_xys)  # 0x80
        voters.append(self.find_win_xys)  # 0x100

        if not moves:
            voters = [self.corner_xys]

        # Trade off the goals

        weight_by_xy = dict((_, 0) for _ in xys)

        for xy in empty_xys:
            weight = 0
            for (index, voter) in enumerate(voters):
                voter_xys = voter
                if not isinstance(voter, list):
                    voter_xys = voter(turn)
                if xy in voter_xys:
                    weight |= 1 << index
            weight_by_xy[xy] |= weight

        max_weight = max(weight_by_xy.values())

        # Choose a move

        shoves = list(_ for _ in empty_xys if weight_by_xy[_] == max_weight)
        xy = random.choice(shoves)

        (x, y) = xy
        move = "{}{}{}".format(turn, x, y)

        return move

    def find_empty_xys(self):
        """Find the Empty Cells"""

        cells = self.cells
        xys = self.xys

        empty_xys = list(_ for _ in xys if cells[xys.index(_)] == ".")

        return empty_xys

    def find_opposite_corner_xys(self, turn):
        """Find the Corners opposite the Corners taken by Them"""

        assert turn in "OX", repr(turn)

        cells = self.cells
        corner_xys = self.corner_xys
        xs = self.xs
        ys = self.ys
        xys = self.xys

        oturn = "X" if (turn != "X") else "O"

        #

        opposite_xys = list()

        for xy in corner_xys:
            (x, y) = xy

            ox = xs[len(xs) - 1 - xs.index(x)]
            oy = ys[len(ys) - 1 - ys.index(y)]
            oxoy = (ox, oy)

            oxoy_cell = cells[xys.index(oxoy)]
            if oxoy_cell == oturn:

                opposite_xys.append(xy)

        return opposite_xys

    def find_threaten_win_xys(self, turn):
        """Find the Empty Cells to take to bring a Streak within 1 Cell of Us Winning"""

        cells = self.cells
        streaks = self.streaks
        xys = self.xys

        ofork_xys = self.find_block_fork_xys(turn)

        threat_xys_set = set()

        empty_xys = self.find_empty_xys()
        for xy in empty_xys:
            (x, y) = xy

            for streak in streaks:
                if xy in streak:
                    n_cells = list(cells[xys.index(xy)].upper() for xy in streak)

                    free_cells = list(_ for _ in n_cells if _ == ".")
                    if len(free_cells) == 2:
                        taken_set = set(_ for _ in n_cells if _ != ".")
                        if len(taken_set) == 1:
                            taker = list(taken_set)[-1]

                            if taker == turn:

                                next_xys = list(
                                    nxy
                                    for nxy in streak
                                    if cells[xys.index(nxy)] == "."
                                )
                                next_xys = list(nxy for nxy in next_xys if nxy != xy)

                                assert len(next_xys) == 1, next_xys

                                next_xy = next_xys[-1]
                                if next_xy in ofork_xys:

                                    continue  # such as O in diagonals after XA1 OB2 XC3

                                threat_xys_set.add(xy)

        threat_xys = sorted(threat_xys_set)

        return threat_xys

    def find_block_fork_xys(self, turn):
        """Find the Empty Cells to take to Fork for Them"""

        (_, ofork_xys) = self._find_fork_ofork_xys(turn)

        return ofork_xys

    def find_fork_xys(self, turn):
        """Find the Empty Cells to take to Fork for Us"""

        (fork_xys, _) = self._find_fork_ofork_xys(turn)

        return fork_xys

    def _find_fork_ofork_xys(self, turn):
        """List the Empty Cells to Take to Form or Block Forks"""

        # List all the Empty Cells that do Form or Block Forks

        (forks_by_xy, oforks_by_oxoy) = self._find_fork_ofork_by_xy(turn)

        # Drop the Empty Cells that don't create the most Winning Moves

        most = max(len(_) for _ in forks_by_xy.values()) if forks_by_xy else 0
        omost = max(len(_) for _ in oforks_by_oxoy.values()) if oforks_by_oxoy else 0

        forks = list()
        if most > 1:
            for (xy, streaks_of_xy) in forks_by_xy.items():
                if len(streaks_of_xy) >= most:

                    forks.append(xy)

        oforks = list()
        if omost > 1:
            for (oxoy, streaks_of_oxoy) in oforks_by_oxoy.items():
                if len(streaks_of_oxoy) >= omost:

                    oforks.append(oxoy)

        # Succeed

        return (forks, oforks)

    def _find_fork_ofork_by_xy(self, turn):
        """List all the Empty Cells that do Form or Block Forks"""

        cells = self.cells
        streaks = self.streaks
        xys = self.xys

        # Visit each Empty Cell

        empty_xys = self.find_empty_xys()

        forks_by_xy = collections.defaultdict(list)
        oforks_by_oxoy = collections.defaultdict(list)

        for xy in empty_xys:

            # Visit each Streak across the Empty Cell

            xy_streaks = list(_ for _ in streaks if xy in _)

            for streak in xy_streaks:
                n_cells = list(cells[xys.index(xy)].upper() for xy in streak)

                # Pick out when taking this Empty Cell creates a Winning Move

                free_cells = list(_ for _ in n_cells if _ == ".")
                if len(free_cells) == 2:  # if taking 1 means taking next wins
                    taken_set = set(_ for _ in n_cells if _ != ".")
                    if len(taken_set) == 1:  # if n=3 or otherwise no interference
                        taker = list(taken_set)[-1]

                        # Collect as a Fork of ours, else as a Fork of theirs

                        if taker == turn:
                            forks_by_xy[xy].append(streak)
                        else:
                            oforks_by_oxoy[xy].append(streak)

        forks_by_xy = dict(forks_by_xy)
        oforks_by_oxoy = dict(oforks_by_oxoy)

        return (forks_by_xy, oforks_by_oxoy)

    def find_block_win_xys(self, turn):
        """Find the Empty Cells to take to Win for Them"""

        (_, blocker_xys) = self._find_winner_blocker_xys(turn)

        return blocker_xys

    def find_win_xys(self, turn):
        """Find the Empty Cells to take to Win for Us"""

        (winner_xys, _) = self._find_winner_blocker_xys(turn)

        return winner_xys

    def _find_winner_blocker_xys(self, turn):
        """Find the Empty Cells to take to Win for Us"""

        assert turn in "OX", repr(turn)

        cells = self.cells
        xys = self.xys
        streaks = self.streaks

        # Visit each Streak left with just 1 Empty Cell in it

        winner_xys = list()
        blocker_xys = list()

        for streak in streaks:
            n_cells = list(cells[xys.index(xy)].upper() for xy in streak)

            free_cells = list(_ for _ in n_cells if _ == ".")
            if len(free_cells) == 1:
                taken_set = set(_ for _ in n_cells if _ != ".")
                if len(taken_set) == 1:
                    taker = list(taken_set)[-1]

                    # Find the 1 Empty Cell

                    free_xys = list(xy for xy in streak if cells[xys.index(xy)] == ".")
                    assert len(free_xys) == 1, (free_xys, streak)

                    free_xy = free_xys[-1]

                    # Collect as a winning Move, or as blocking Move

                    if taker == turn:
                        winner_xys.append(free_xy)
                    else:
                        blocker_xys.append(free_xy)

        # Succeed

        return (winner_xys, blocker_xys)

    def _choose_center_else(self, turn):
        """Say to move to Center"""

        cells = self.cells
        xs = self.xs
        ys = self.ys
        xys = self.xys

        x = xs[len(xs) // 2]
        y = ys[len(ys) // 2]
        xy = (x, y)

        move = "{}{}{}".format(turn, x, y)

        cell = cells[xys.index(xy)]
        if cell != ".":

            return None

        return move

    def _choose_opposite_else(self, turn):
        """Say to move to an Opposite Corner"""

        assert turn in "OX", repr(turn)

        cells = self.cells
        corner_xys = self.corner_xys
        xs = self.xs
        ys = self.ys
        xys = self.xys

        oturn = "X" if (turn != "X") else "O"

        # List the Empty Opposite Corner Cells

        empty_opposite_xys = list()

        for xy in corner_xys:
            (x, y) = xy

            ox = xs[len(xs) - 1 - xs.index(x)]
            oy = ys[len(ys) - 1 - ys.index(y)]
            oxoy = (ox, oy)

            xy_cell = cells[xys.index(xy)]
            oxoy_cell = cells[xys.index(oxoy)]

            if (xy_cell == ".") and (oxoy_cell == oturn):

                empty_opposite_xys.append(xy)

        # Choose 1 Empty Oppposite Corner Cell to move onto

        if not empty_opposite_xys:

            return None

        xy = random.choice(empty_opposite_xys)
        (x, y) = xy

        move = "{}{}{}".format(turn, x, y)

        return move

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

    def tui_turn_chords_print(self, tui, turn, chords):
        """Print the Chords, the Handicaps, the Moves, and the Cells"""

        assert "←" == "\N{Leftwards Arrow}"
        assert "↑" == "\N{Upwards Arrow}"
        assert "↓" == "\N{Downwards Arrow}"
        assert "→" == "\N{Rightwards Arrow}"

        # Format the Chords

        str_chords_plus = " ".join(chords) + " "
        if len(chords) == 1:
            chord = chords[-1]
            if chord in "AWSD" "HKJL":
                arrow = "←↑↓→←↑↓→"["AWSDHKJL".index(chord)]
                str_chords_plus = "{} like {}".format(chord, arrow)

        # Print the Chords, the Handicaps, and the Moves

        (handicaps, xo_moves) = self._moves_split()

        if chords:
            tui.print(DENT + "input " + str_chords_plus)
        if handicaps:
            tui.print(DENT + "handicaps " + " ".join(handicaps))
        if xo_moves:
            tui.print(DENT + "gameboard " + " ".join(xo_moves))

        # Print the Cells

        tui.print()
        self.tui_print_cells(tui)
        tui.print()

        # Print the News of a Win or Draw

        self.tui_print_winners(tui, turn=turn)

    def tui_print_winners(self, tui, turn):
        """Print the News of a Win or Draw"""

        streaks_by_winner = self.streaks_by_winner

        # Print the News of a Win

        winners = list(streaks_by_winner.keys())
        if winners:
            if len(set(winners)) == 1:
                winner = winners[-1]
                news = "{} won".format(winner)

                streaks = streaks_by_winner[winner]
                if len(streaks) != 1:
                    news = "{} won {} times".format(winner, len(streaks))

            else:

                news = "{} won {} times, {} won {} times".format(
                    "X", len(streaks_by_winner["X"]), "O", len(streaks_by_winner["O"])
                )

            tui.print(DENT + news)
            tui.print()

            return

        # Print the News of a Draw

        empty_xys = self.find_empty_xys()
        if not empty_xys:
            tui.print(DENT + "Game over, nobody won")
            tui.print()

            return

        # Print a Forecast of who could win

        if False:  # len(empty_xys) <= 9:  # FIXME: run fast

            (x, o, z) = self.forecast_x_o_wins(tui, turn=turn)

            str_x = "{:,}".format(x).replace(",", "_")
            str_o = "{:,}".format(o).replace(",", "_")
            str_z = "{:,}".format(z).replace(",", "_")

            news = "{} ways for X to win".format(str_x)
            news += ", {} ways for O to win".format(str_o)
            news += ", {} ways for Nobody to win".format(str_z)

            if x == o == 0:
                news = "Game nearly over, nobody wins"

            tui.print(DENT + news)
            tui.print()

    def tui_print_cells(self, tui):
        """Print the Cells"""

        cells = self.cells

        n = self.n
        xs = self.xs
        ys = self.ys
        xys = self.xys

        dminus = DENT[:-1]

        color_chars_format = "\x1B[{}m{}\x1B[0m"
        assert keycaps.COLOR_CHARS_FORMAT == color_chars_format

        assert len(COLOR_BY_MOVE) >= ((n * n + 1) // 2), (len(COLOR_BY_MOVE), n)

        #

        (handicaps, xo_moves) = self._moves_split()

        tui.print(dminus, "", "", "", " ".join(self.xs))
        tui.print()
        for y in ys:
            tui.print(dminus, y, "", end=" ")

            for x in xs:
                xy = (x, y)
                cell = cells[xys.index(xy)]
                move = "{}{}{}".format(cell.upper(), x, y)

                if cell == ".":
                    tui.print(cell, end=" ")
                elif move in handicaps:
                    assert move not in xo_moves, move
                    tui.print(cell, end=" ")
                else:
                    assert move not in handicaps, move

                    index = xo_moves.index(move)
                    # rindex = len(xo_moves) - 1 - index

                    color = COLOR_BY_MOVE[index // 2]
                    chars = color_chars_format.format(color, cell)
                    tui.print(chars, end=" ")

            tui.print()

    def forecast_x_o_wins(self, tui, turn):

        cells = self.cells

        # Forecast for X Next or O Next

        if turn == ".":
            (xx, xo) = self.forecast("X")
            (ox, oo) = self.forecast("O")

            x_ = xx + ox
            o_ = xo + oo

            return (x_, o_)

        # Collect Boards of Cells to score

        scoreables = list()

        scoreable = (turn, cells)
        scoreables.append(scoreable)

        x_ = 0
        o_ = 0
        z_ = 0
        while scoreables:
            scoreable = scoreables.pop(0)
            (turn_, cells_) = scoreable

            turn__ = "X" if (turn_ != "X") else "O"

            (x, o, z) = self.score_x_o_wins(tui, cells=cells_)

            if z and ("." in cells_):

                for (index, cell_) in enumerate(cells_):
                    if cell_ == ".":
                        cells__ = list(cells_)
                        cells__[index] = turn_

                        scoreable__ = (turn__, cells__)
                        # tui.print(scoreable__)
                        scoreables.append(scoreable__)

            else:

                (x, o, z) = self.score_x_o_wins(tui, cells=cells_)
                x_ += x
                o_ += o
                z_ += z

        return (x_, o_, z_)

    def score_x_o_wins(self, tui, cells):

        xys = self.xys
        streaks = self.streaks

        streaks_by_winner = dict()

        for streak in streaks:
            streak_set = set(cells[xys.index(xy)].upper() for xy in streak)
            if len(streak_set) == 1:
                cell = list(streak_set)[-1]
                if cell != ".":
                    if cell not in streaks_by_winner.keys():
                        streaks_by_winner[cell] = list()

                    streaks_by_winner[cell].append(streak)

        len_x = len(streaks_by_winner["X"]) if ("X" in streaks_by_winner.keys()) else 0
        len_o = len(streaks_by_winner["O"]) if ("O" in streaks_by_winner.keys()) else 0

        x = 1 if (len_x > len_o) else 0
        o = 1 if (len_o > len_x) else 0
        z = 0 if (x or o) else 1

        # str_cells = "{}{}{} {}{}{} {}{}{}".format(*cells)
        # if str_cells == "XoX xoo xOx":
        #     breakpoint()
        # tui.print("Z" if z else ("X" if x else "O"), str_cells)

        return (x, o, z)


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

    # o fork win
    - XC3 OB2 XA1 OC1 XB1 OC2 XA2 OA3

    # quit
    Q

"""


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main(sys.argv)


# todo: sort uniq to reduce flips and rotations, print what remains


# todo: Y for analysis - advise the moves without taking them: win, block win, etc

# todo: stop with the Got Choices, instead trace the Chords
# todo: Press ABC or ? or some other key, to choose Row for X
# todo: Press 123 or ? or some other key, to choose Column in Row A for X

# todo: = X gives you O after your every X, = O gives you X after O, = . is default
# todo: > auto plays to end of game in the ↑ ↓ → style only (or end of → input)
# todo: < auto plays to star of game in the ← style only

# todo: input > taken as ↑
# todo: input > taken as 2 ↑
# todo: input B 2 taken as X B 2
# todo: input B 2 taken as X B 2, then also O ↑, thus O C 3

# todo: take digits 0..9 as multiplier before ! ←↑↓→
# todo: take ⌃C as cancelling input preceding it
# todo: empty the keyboard when not keeping up

# todo: echo all input, have most of it work like ? /
# todo: say input: !, taken as X B 3
# todo: allow 3 of ? / etc before limiting
# todo: quit at 2 of Q Esc ⌃C ⌃\ vs Windows Chrome Linux ⌃C ⌃V

# todo: export/ import Game & Board into __pycache__/tictactoe.json


# todo: 2 doesn't say what fraction of the moves you chose yourself
# todo: 3 doesn't forecast to say when a Draw or Win is inevitable
# todo: sketch how many X wins vs O wins still possible
# todo: 4 doesn't undo clearing the Board - could resist Undo of Clear, not refuse it

# todo: draw counters not yet placed to fill the empty cells

# todo: lean more into always doing something in reply to input
# todo: could make the meanings of ! ←↑↓→ - Return more visible
# todo: could echo each char of each # ... Return comment
# todo: could toggle start with X vs O
# todo: could mark the Board somehow for next X or next O
# todo: could resist Tab after Tab

# todo: 'def run_till_quit' prompts for n != 3


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/tictactoe.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
