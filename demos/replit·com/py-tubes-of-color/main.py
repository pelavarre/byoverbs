"""
usage: main.py

sort balls by colour

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

FEATURE_STAGING = True  # jitter Fri 15/Mar
FEATURE_STAGING = False

TubeCount7 = 7  # total printed
TubeCount2 = 2  # often empty

BallCount4 = 4

Board = """

    d   d   d   d
    c   c   c   c
    b   b   b   b
    a   a   a   a

      d   d   d
      c   c   c
      b   b   b
      a   a   a

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

Colors = (Red, Blue, Orange, Green, Purple)
Empty = White


@dataclasses.dataclass
class Tube:
    """Pile up some Colored Balls into a vertical Tube"""

    name: str

    y1: int
    x1: int

    balls: list[str]


Tubes = list()


def board_init() -> None:
    """Fill up the Tubes"""

    # Stand each Tube at & above the Ball at 'a' in the Board

    for y3, line in enumerate(BoardLines):
        y1 = 3 + y3
        for m in re.finditer(r"a", string=line):
            x1 = 1 + m.start()

            index = len(Tubes)
            name = str(index)

            t = Tube(name=name, y1=y1, x1=x1, balls=list())
            Tubes.append(t)

    assert len(Tubes) == TubeCount7, len(Tubes)

    # Fill up the Tubes with Balls, except not the last two Tubes

    balls = list()
    for color in Colors:
        balls.extend(4 * [color])

    random.shuffle(balls)

    assert TubeCount2 == 2
    assert BallCount4 == 4

    while balls:
        ball = balls.pop(0)

        some_tubes = list(_ for _ in Tubes[:-2] if len(_.balls) < 4)
        t = random.choice(some_tubes)

        t.balls.append(ball)


board_init()

#
#
# Test one particular Game, when called
#


def balls_patch_up_for_staging() -> None:
    """Start a particular game"""

    Tubes[0].balls[::] = [Orange, Orange, Blue, Green]
    Tubes[1].balls[::] = [Red, Red, Red, Red]
    Tubes[2].balls[::] = [Orange, Orange, Green, Blue]
    Tubes[3].balls[::] = [Blue, Green, Purple, Blue]
    Tubes[4].balls[::] = []
    Tubes[5].balls[::] = []
    Tubes[6].balls[::] = [Purple, Purple, Purple, Green]

    Main.draining_tubes = [Tubes[4], Tubes[5]]


#
#
# Model, paint, and judge a Game
#


class Main:
    """Name a workspace for the Code of this Py File"""

    turn: int  # count Turns of Sorting or Scrambling

    draining_tubes: list[Tube]  # a goal of Scrambling

    empty_tubes: list[Tube]  # the Tubes that can't give Balls
    giving_tubes: list[Tube]  # the Tubes that can give Balls
    taking_tubes: list[Tube]  # the Tubes that can take Balls
    full_tubes: list[Tube]  # the Tubes that can't take Balls

    full_sorted_tubes: list[Tube]  # the Tubes full of matching Balls


Main.draining_tubes = list()


def board_paint() -> None:
    """Paint over the Board on Screen"""

    for t in Tubes:
        y1 = t.y1
        x1 = t.x1
        balls = t.balls

        assert not any((_ == Empty) for _ in balls)
        four_glyphs = (balls + (4 * [Empty]))[:4]

        y = y1
        for glyph in four_glyphs:
            print(f"\x1B[{y};{x1}H" + glyph, end="")
            y -= 1

    print(f"\x1B[{Y1Below}H", end="")

    print()
    print()

    print("\x1B[J", end="")

    if Main.turn < 0:
        print(f"Turn {-Main.turn} - SCRAMBLING")
    else:
        print(f"Sorting Balls - Turn {Main.turn}")

    sys.stdout.flush()

    # Mar/2024 ReplIt·Com didn't accept EL = "\x1B[2K"  # Erase In Line


def board_judge() -> None:
    """Pick apart the Tubes"""

    assert BallCount4 == 4

    empty_tubes = list(_ for _ in Tubes if not _.balls)
    giving_tubes = list(_ for _ in Tubes if _.balls)
    taking_tubes = list(_ for _ in Tubes if len(_.balls) < 4)
    full_tubes = list(_ for _ in Tubes if len(_.balls) >= 4)

    full_sorted_tubes = list()
    for t in full_tubes:
        if len(set(t.balls)) == 1:
            full_sorted_tubes.append(t)

    Main.empty_tubes = empty_tubes
    Main.giving_tubes = giving_tubes
    Main.taking_tubes = taking_tubes
    Main.full_tubes = full_tubes

    Main.full_sorted_tubes = full_sorted_tubes


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


def try_main() -> None:
    """Play the Game, over and over and over"""

    print(f"\x1B[{Y1Below}H", end="")

    if FEATURE_STAGING:
        balls_patch_up_for_staging()
        balls_scramble()

    while True:
        balls_sort()
        balls_scramble()


def balls_sort() -> None:  # noqa C901 too complex
    """Move Balls to a Tube topped by a matching Ball, or to an Empty Tube"""

    Main.turn = 0

    while True:
        Main.turn = Main.turn + 1

        board_paint()
        board_judge()

        time.sleep(0.9)

        # List available Moves

        pairs = list()
        for g in Main.giving_tubes:
            giving = g.balls[-1]

            for t in Main.taking_tubes:
                if t is not g:
                    taking = t.balls[-1] if t.balls else giving
                    if taking == giving:
                        pair = (g, t)
                        pairs.append(pair)

        # Stop playing after a Loss

        if not pairs:
            break

        # Stop playing after all Tubes full and sorted, except for two Tubes empty

        assert TubeCount7 == 7
        assert TubeCount2 == 2

        if len(Main.empty_tubes + Main.full_sorted_tubes) >= 7:
            if len(Main.empty_tubes) >= 2:
                break

        # Choose a move, and make it

        moved = 0

        pair = random.choice(pairs)
        (g, t) = pair
        while g.balls and (len(t.balls) < BallCount4):
            giving = g.balls[-1]
            taking = t.balls[-1] if t.balls else giving
            if taking != giving:
                break

            moving = g.balls.pop()
            assert moving == taking == giving, (moving, taking, giving)
            t.balls.append(moving)

            moved += 1

        assert moved

    time.sleep(0.9)

    chosen_draining_tubes = list(Tubes)
    random.shuffle(chosen_draining_tubes)
    Main.draining_tubes[::] = chosen_draining_tubes[:2]


def balls_scramble() -> None:  # noqa C901 too complex
    """Move Balls back out at random, till two or more Tubes empty"""

    Main.turn = 0

    while True:
        Main.turn = Main.turn - 1

        board_paint()
        board_judge()

        time.sleep(0.3)

        # Stop playing after no Tube full and sorted, and two Tubes empty

        assert TubeCount2 == 2

        if not Main.full_sorted_tubes:
            if len(Main.empty_tubes) >= 2:
                break

        # Give from the Draining Tubes, if available, after no Tube full and sorted

        chosen_giving_tubes = list()
        if not Main.full_sorted_tubes:
            for t in Main.draining_tubes:
                if t in Main.giving_tubes:
                    chosen_giving_tubes.append(t)
        if not chosen_giving_tubes:
            chosen_giving_tubes = list(Main.giving_tubes)

        # Don't take into the Draining Tubes, after no Tube full and sorted

        chosen_taking_tubes = list(Main.taking_tubes)
        if not Main.full_sorted_tubes:
            for t in Main.draining_tubes:
                if t in Main.taking_tubes:
                    chosen_taking_tubes.remove(t)

        # Choose a move, and make it

        pairs = list()
        for g in Main.giving_tubes:
            for t in chosen_taking_tubes:
                if t is not g:
                    pair = (g, t)
                    pairs.append(pair)

        assert pairs

        pair = random.choice(pairs)

        (g, t) = pair
        moving = g.balls.pop()
        t.balls.append(moving)

    time.sleep(0.9)

    Main.draining_tubes[::] = list()


main()
