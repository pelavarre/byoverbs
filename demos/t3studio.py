r"""
usage: t3studio.py

drop the 3x3 Tic-tac-toe Game into a Python REPL

search keys:
  Xs and Os, Noughts and crosses, Tic-tac-toe

examples:
  black demos && flake8 demos && python3.bash demos/t3studio.py --
"""


import code
import collections
import datetime as dt
import string

import tictactoe


#
# Say how to flip, spin, and turn the Board
#


CELLS = """

    a b c
    d e f
    g h i

""".split()

CENTER_E = "e"
CORNER_ACGI = "acgi"
OUTSIDE_BDFH = "bdfh"

OPPOSITES_AI_CG_GC_IA = "ai cg gc ia".split()


FLIP_UP_DOWN = """

    g h i
    d e f
    a b c

""".split()

SPIN_LEFT_RIGHT = """

    c b a
    f e d
    i h g

""".split()

TURN_LEFT = """

    c f i
    b e h
    a d g

""".split()

TURN_RIGHT = """

    g d a
    h e b
    i f c

""".split()


#
# Say how to win a game
#


STREAKS = """

    a b c
    d e f
    g h i

    a d g
    b e h
    c f i

    a e i
    c e g

"""

STREAKS = list(_ for _ in STREAKS.splitlines() if _)


#
# Collect 8 Ways to flip, spin and turn
#


RENDERERS = list()  # 8 ways to flip, spin, and turn


BOARDS = list()  # reachable before or at first Win

X_BOARDS = list()  # reachable, no Wins, X moves next
O_BOARDS = list()  # reachable, no Wins, O moves next

X_WINS = list()  # reachable, one or more Wins by X
O_WINS = list()  # reachable, one or more Wins by O

NO_WINS = list()  # reachable, no Wins, no move next


RENDERS_BY_MAX_RENDER = collections.defaultdict()


#
# Run from the Sh Command Line
#


def main():
    """Run from the Sh Command Line"""

    walk_renders()
    walk_boards()
    walk_wins()

    index_boards()

    wikipedia_flip_spin_turn()
    wikipedia_v_wikipedia()

    diff_2023_v_2022()
    play_2023_v_2022()


def walk_renders():
    """Count out the 8 Ways to flip or rotate a Board"""

    print()
    print("walk_renders")

    # Render as is

    render = tuple(CELLS)
    RENDERERS.append(render)

    # Turn left one or two or three times

    turner = tuple(render)
    for step in range(3):
        turner = tuple(turner[CELLS.index(_)] for _ in TURN_LEFT)
        RENDERERS.append(turner)

    # Flip each of those up over down

    for render in list(RENDERERS):
        flipper = tuple(render[CELLS.index(_)] for _ in FLIP_UP_DOWN)
        RENDERERS.append(flipper)

    # Show no duplicates yet, but only duplicates in more turning or flipping

    assert len(set(RENDERERS)) == len(RENDERERS) == 8

    for render in list(RENDERERS):

        left_turner = tuple(render[CELLS.index(_)] for _ in TURN_LEFT)
        right_turner = tuple(render[CELLS.index(_)] for _ in TURN_RIGHT)
        spinner = tuple(render[CELLS.index(_)] for _ in SPIN_LEFT_RIGHT)

        assert left_turner in RENDERERS
        assert right_turner in RENDERERS
        assert spinner in RENDERERS


def walk_boards():
    """Visit each Boards reached by playing till first Win"""

    print()
    print("walk_boards")

    t0 = dt.datetime.now()

    board = tuple(9 * "_")

    x_board = tuple(board)
    more_x_boards = list()
    X_BOARDS.append(x_board)
    more_x_boards.append(x_board)

    for step in range(5):

        tx = dt.datetime.now()
        tx = tx - t0
        print(tx, "{}th move by X".format(step))

        more_o_boards = form_x_moves(more_x_boards, step=step)

        if step < 4:

            to = dt.datetime.now()
            to = to - t0
            print(to, "{}th move by O".format(step))

            more_x_boards = form_o_moves(more_o_boards)

    X_BOARDS[::] = sorted(set(X_BOARDS))
    O_BOARDS[::] = sorted(set(O_BOARDS))

    X_WINS[::] = sorted(set(X_WINS))
    O_WINS[::] = sorted(set(O_WINS))
    NO_WINS[::] = sorted(set(NO_WINS))

    BOARDS.clear()
    BOARDS.extend(X_BOARDS)
    BOARDS.extend(O_BOARDS)
    BOARDS.extend(X_WINS)
    BOARDS.extend(O_WINS)
    BOARDS.extend(NO_WINS)

    BOARDS.sort()
    assert BOARDS == sorted(set(BOARDS))

    wins = X_WINS + O_WINS + NO_WINS

    wins.sort()
    assert wins == sorted(set(wins))

    t1 = dt.datetime.now()

    print(t1 - t0)  # < 10s

    print("{:_} boards".format(len(BOARDS)))
    print(
        "{:_} ({:_}+{:_}+{:_} X O _) won + {:_} {:_} X O moves next".format(
            len(wins),
            len(X_WINS),
            len(O_WINS),
            len(NO_WINS),
            len(X_BOARDS),
            len(O_BOARDS),
        )
    )

    # 2_270_494 boards
    # 495_648 X won + 109_872 O win + 519_697 X moves next + 1_145_277 O moves next


def form_x_moves(more_x_boards, step):
    """Form an X Win or a next O Board out of each X Board"""

    more_o_boards = list()
    for x_board in more_x_boards:
        for x in range(9):
            if x_board[x] == "_":

                board = list(x_board)
                board[x] = "x"
                board = tuple(board)

                if board_pick_wins(board):
                    X_WINS.append(board)
                elif step < 4:
                    assert "_" in board, (step, board)
                    more_o_boards.append(board)
                    O_BOARDS.append(board)
                else:
                    assert "_" not in board, (step, board)
                    NO_WINS.append(board)

    return more_o_boards


def form_o_moves(more_o_boards):
    """Form an O Win or a next X Board out of each O Board"""

    more_x_boards = list()
    for o_board in more_o_boards:
        for o in range(9):
            if o_board[o] == "_":

                board = list(o_board)
                board[o] = "o"
                board = tuple(board)

                if board_pick_wins(board):
                    O_WINS.append(board)
                else:
                    assert "_" in board, board
                    more_x_boards.append(board)
                    X_BOARDS.append(board)

    return more_x_boards


def board_pick_wins(board):
    """Return 'x' or 'o' or 'xx' to say X won once, O won once, X won twice, etc"""

    picks = list()

    for streak in STREAKS:
        cells = list(board[CELLS.index(_)] for _ in streak.split())

        if len(set(cells)) == 1:
            _ox = cells[-1]
            assert _ox in "_ox", (_ox,)

            if _ox in "xo":
                picks.append(_ox)

    picks = "".join(picks)

    return picks


def walk_wins():
    """Count how many Boards win by how much - max 2 X Wins, max 1 O Win"""

    print()
    print("walk_wins")

    boards_by_picks = collections.defaultdict(list)
    for board in X_WINS + O_WINS:
        picks = board_pick_wins(board)
        boards_by_picks[picks].append(board)

    for picks in sorted(boards_by_picks.keys()):
        print("{!r} {:_}".format(picks, len(boards_by_picks[picks])))


def index_boards():
    """Index Boards by Max Render"""

    print()
    print("index_boards")

    board_set = set(BOARDS)

    while board_set:
        board = board_set.pop()

        renders = board_find_renders(board)

        for render in set(renders):
            if render != board:
                board_set.remove(render)

        max_render = max(renders)

        assert max_render not in RENDERS_BY_MAX_RENDER.keys(), max_render
        RENDERS_BY_MAX_RENDER[max_render] = tuple(sorted(renders))

    boards_ = list(RENDERS_BY_MAX_RENDER.keys())

    o_boards = sorted(set(max(board_find_renders(_)) for _ in O_BOARDS))
    x_boards = sorted(set(max(board_find_renders(_)) for _ in X_BOARDS))

    no_wins = sorted(set(max(board_find_renders(_)) for _ in NO_WINS))
    o_wins = sorted(set(max(board_find_renders(_)) for _ in O_WINS))
    x_wins = sorted(set(max(board_find_renders(_)) for _ in X_WINS))

    wins = sorted(no_wins + o_wins + x_wins)

    assert wins == sorted(set(wins))

    print("{:_} groups of equal boards".format(len(boards_)))
    print(
        "{:_} ({:_}+{:_}+{:_} X O _) won + {:_} {:_} X O moves next".format(
            len(wins),
            len(x_wins),
            len(o_wins),
            len(no_wins),
            len(x_boards),
            len(o_boards),
        )
    )


def board_find_renders(board):

    renders = list()

    for renderer in RENDERERS:
        render = tuple(board[CELLS.index(_)] for _ in renderer)
        renders.append(render)

    renders.sort()
    renders = tuple(renders)

    return renders


#
# Work with Boards
#


def board_mover(board):
    """Choose to move 'x' or 'o' or not"""

    _ = board.count("_")
    o = board.count("o")
    x = board.count("x")

    won = board_pick_wins(board)

    if won or (not _):
        _ox = "_"
    elif x > o:
        _ox = "o"
    else:
        _ox = "x"

    return _ox


def board_alt_if(board, i, ox):
    """Fill 1 Cell if Cell empty"""

    assert ox != "_", (ox,)

    if board[i] != "_":

        return None

    alt_board = list(board)
    alt_board[i] = ox
    alt_board = tuple(alt_board)

    return alt_board


def board_print(board):
    """Print 1 Board"""

    print(" ".join(board[:3]))
    print(" ".join(board[3:-3]))
    print(" ".join(board[-3:]))


def board_breakpoint_if(board, moves):
    """Print Mover and Moves and Board if any Moves chosen"""

    if moves:
        _ox = board_mover(board)

        print(_ox, moves)
        board_print(board)

        breakpoint()


def board_breakpoint(board):
    """Print Mover and Board"""

    _ox = board_mover(board)

    print(_ox)
    board_print(board)

    breakpoint()


#
#
#


def play_2023_v_2022():
    """Play a 2023-03 read of Wikipedia of Newell & Simon 1972, vs 2022-11"""

    for players in ("ox", "xo"):

        print()
        print("play_2023_v_2022", players)

        board = tuple(9 * "_")
        boards = [board]

        for step in range(5):
            for board in boards:
                _ox = board_mover(board)
                if _ox != "_":
                    ox = _ox

                    if ox == players[0]:
                        moves = tictactoe.board_moves(board, ox=ox)
                    else:
                        moves = board_wikipedia_moves(board)

                    for move in moves:
                        alt_board = board_alt_if(board, i=move, ox=ox)
                        boards.append(alt_board)

            for board in boards:
                wins = board_pick_wins(alt_board)
                if wins:

                    print()
                    board_print(board)


def diff_2023_v_2022():
    """Contrast a 2023-03 read of Wikipedia of Newell & Simon 1972, vs 2022-11"""

    print()
    print("diff_2023_v_2022")

    for board in BOARDS:
        _ox = board_mover(board)
        if _ox != "_":
            ox = _ox

            if False:
                if board == ("_", "_", "_", "_", "_", "o", "x", "_", "x"):

                    tictactoe.FEATURE_STEPPING = True

            moves_2022 = tictactoe.board_moves(board, ox=ox)
            moves_2023 = board_wikipedia_moves(board)

            if moves_2023 != moves_2022:
                if board == ("_", "_", "_", "_", "_", "_", "_", "_", "_"):
                    assert moves_2022 == (0, 2, 6, 8)
                    assert moves_2023 == (4,)
                elif not (set(moves_2022) - set(moves_2023)):
                    pass
                elif False:
                    print()
                    print(ox)
                    board_print(board)
                    print("if board == {}:".format(board))
                    print("assert moves_2022 == {}".format(moves_2022))
                    print("assert moves_2023 == {}".format(moves_2023))


#
# Move to win, as per Wikipedia of Newell & Simon 1972
#


def wikipedia_v_wikipedia():
    """Show that Wikipedia against itself never wins nor loses"""

    print()
    print("wikipedia_v_wikipedia")

    once_boards = set()
    stopped_boards = set()

    board = tuple(9 * "_")
    boards = [board]

    while boards:
        board = boards.pop()
        if board not in once_boards:
            once_boards.add(board)

            print()
            board_print(board)

            _ox = board_mover(board)
            if _ox == "_":
                stopped_boards.add(board)
            else:
                ox = _ox

                moves = board_wikipedia_moves(board)
                for move in moves:

                    alt_board = board_alt_if(board, i=move, ox=ox)
                    assert alt_board

                    wins = board_pick_wins(alt_board)
                    assert not wins, (alt_board, ox, board)

                    max_alt_board = max(board_find_renders(alt_board))
                    boards.append(max_alt_board)

    print("played {:_} boards".format(len(once_boards)))
    print("stopped {:_} boards".format(len(stopped_boards)))
    print("won 0 games")


def wikipedia_flip_spin_turn():
    """Show that Flip, Spin, and Turn don't change Wikipedia Moves to Win"""

    print()
    print("wikipedia_flip_spin_turn")

    for from_renders in RENDERS_BY_MAX_RENDER.values():

        _oxs = list()
        list_maxxes = list()

        for from_render in from_renders:
            board = from_render

            _ox = board_mover(board)
            _oxs.append(_ox)
            moves = board_wikipedia_moves(board)

            if _ox == "_":
                assert not moves, (moves, _ox, board)
            else:
                assert moves, (moves, _ox, board)

            maxxes = list()
            for move in moves:
                assert _ox in "ox"
                ox = _ox

                to_render = board_alt_if(board, i=move, ox=ox)
                assert to_render, (to_render, board, move, ox)

                max_to_render = max(board_find_renders(board=to_render))
                maxxes.append(max_to_render)

            maxxes = tuple(sorted(maxxes))
            list_maxxes.append(maxxes)

        assert len(set(_oxs)) == 1, (_oxs, from_renders[0])

        converged = set(list_maxxes)
        if len(converged) > 1:
            breakpoint()
        assert len(converged) <= 1, (len(converged), from_renders[0], list_maxxes)


def board_wikipedia_moves(board):
    """Move to win, as per Wikipedia of Newell & Simon 1972"""

    _ox = board_mover(board)
    if _ox == "_":
        moves = list()

        return moves

    ox = _ox
    assert ox in "ox", (ox,)

    moves = board_win_moves(board, ox=ox)
    if not moves:
        moves = board_block_win_moves(board, ox=ox)

    if not moves:
        moves = board_fork_moves(board, ox=ox)
    if not moves:
        moves = board_block_fork_moves(board, ox=ox)

    if not moves:
        moves = board_center_moves(board, ox=ox)
    if not moves:
        moves = board_opposite_moves(board, ox=ox)
    if not moves:
        moves = board_corner_moves(board, ox=ox)
    if not moves:
        moves = board_outside_moves(board, ox=ox)

    assert moves, board
    assert moves == sorted(moves), board

    moves = tuple(moves)

    return moves


def board_win_moves(board, ox):
    """Wikipedia says play the third Cell in a Row"""

    assert ox in "ox", (ox,)

    moves = list()
    for streak in STREAKS:
        indices = list(CELLS.index(_) for _ in streak.split())
        cells = list(board[_] for _ in indices)

        if sorted(cells) == ["_", ox, ox]:
            i = indices[cells.index("_")]

            moves.append(i)

    moves.sort()

    return moves


def board_block_win_moves(board, ox):
    """Wikipedia says play the third Cell in a Row to block the Enemy"""

    assert ox in "ox", (ox,)

    xo = "o" if (ox == "x") else "x"
    xo_wins = board_win_moves(board, ox=xo)
    moves = xo_wins

    assert moves == sorted(moves), (moves, board, ox)

    return moves


def board_fork_moves(board, ox):
    """Wikipedia says open up multiple Ways to Win"""

    assert ox in "ox", (ox,)

    moves = list()
    for i in range(9):
        if board[i] == "_":

            alt_board = list(board)
            alt_board[i] = ox
            alt_board = tuple(alt_board)

            alt_moves = board_win_moves(alt_board, ox=ox)
            if len(alt_moves) > 1:
                assert len(alt_moves) <= 3, (alt_moves, alt_board, board, i)

                moves.append(i)

    moves.sort()

    return moves

    # todo: assert max Fork for each Board is 2


def board_block_fork_moves(board, ox):
    """Wikipedia says block only Fork, else block with 2nd, else play 2nd against"""

    assert ox in "ox", (ox,)

    xo = "o" if (ox == "x") else "x"
    xo_forks = board_fork_moves(board, ox=xo)

    # Wikipedia says make two in a Row to threaten a Win, except don't force a Fork

    forkless_threats = board_forkless_threads(board, ox=ox, xo_forks=xo_forks)

    # Wikipedia says block The Only Fork

    moves = list()
    if xo_forks:
        if len(xo_forks) == 1:
            moves = xo_forks
        else:

            # Look to block All The Forks

            blocks = list()
            forkless_threat_blocks = list()

            for i in range(9):
                alt_board = board_alt_if(board, i=i, ox=ox)
                if alt_board:
                    alt_xo_forks = board_fork_moves(alt_board, ox=xo)
                    if not alt_xo_forks:

                        blocks.append(i)
                        if i in forkless_threats:
                            forkless_threat_blocks.append(i)

            # Wikipedia says go for Forkless Threat Blocks

            if forkless_threat_blocks:
                moves = forkless_threat_blocks

            # Wikipedia says else go for Forkless Threats

            elif forkless_threats:
                moves = forkless_threats

            # Fall back to block All The Forks, although Wikipedia doesn't say so

            elif blocks:
                moves = blocks

            # Fall back to block Any Fork, although Wikipedia doesn't say so

            else:
                moves = xo_forks  # todo: block the strongest Forks

                # board_breakpoint(board)  # jitter Fri 31/Mar

    assert moves == sorted(moves), (moves, board, ox)

    return moves


def board_forkless_threads(board, ox, xo_forks):
    """Wikipedia says make two in a Row to threaten a Win, except don't force a Fork"""

    pairs = board_threat_win_pairs(board, ox=ox)

    forkless_threats = list()
    for (threat, win) in pairs:
        if win not in xo_forks:
            forkless_threats.append(threat)

    return forkless_threats


def board_threat_win_pairs(board, ox):
    """Wikipedia says make two in a Row to threaten a Win"""

    pairs = list()

    for streak in STREAKS:
        indices = list(CELLS.index(_) for _ in streak.split())
        cells = list(board[_] for _ in indices)

        if sorted(cells) == ["_", "_", ox]:
            moves = list(_ for _ in indices if board[_] == "_")
            assert len(moves) == 2, (len(moves), moves, board)

            pairs.append(tuple(moves))
            pairs.append(tuple(reversed(moves)))

    pairs = sorted(set(pairs))

    return pairs


def board_center_moves(board, ox):
    """Wikipedia says play the Center"""

    assert CENTER_E == "e"

    moves = list()

    i = CELLS.index("e")
    if board[i] == "_":

        moves.append(i)

    return moves


def board_opposite_moves(board, ox):
    """Wikipedia says play the Opposite Corner"""

    moves = list()

    assert ox in "ox", (ox,)

    xo = "o" if (ox == "x") else "x"

    assert OPPOSITES_AI_CG_GC_IA == "ai cg gc ia".split()

    for opposites in OPPOSITES_AI_CG_GC_IA:
        i = CELLS.index(opposites[0])
        j = CELLS.index(opposites[-1])

        if (board[i] == "_") and (board[j] == xo):

            moves.append(i)

    return moves


def board_corner_moves(board, ox):
    """Wikipedia says play a Corner"""

    moves = list()

    assert CORNER_ACGI == "acgi"

    for corner in CORNER_ACGI:
        i = CELLS.index(corner)
        if board[i] == "_":

            moves.append(i)

    return moves


def board_outside_moves(board, ox):
    """Wikipedia says play the Middle of an Outside Row or Column"""

    moves = list()

    assert OUTSIDE_BDFH == "bdfh"

    for outside in OUTSIDE_BDFH:
        i = CELLS.index(outside)
        if board[i] == "_":

            moves.append(i)

    return moves


#
# Run from the Sh Command Line
#

if __name__ == "__main__":

    main()

    print()
    print("Press ⌃D TTY EOF to exit")

    print()
    print(">>> ")

    print(">>> list(_ for _ in dir() if _[0] in string.ascii_uppercase)")
    o = list(_ for _ in dir() if _[0] in string.ascii_uppercase)
    print(repr(o))
    print(">>> ")

    del o

    code.interact(banner="", local=globals())


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/t3studio.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
