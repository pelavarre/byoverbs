#!/usr/bin/env python3

r"""
usage: csp.py [-h] [--yolo]

work with Communicating Sequential Processes (CSP)

options:
  -h, --help  show this message and exit
  --yolo      do what's popular now

docs:
  https://en.wikipedia.org/wiki/Communicating_sequential_processes
  http://www.usingcsp.com/cspbook.pdf (4/Dec/2022)

examples:
  csp.py --h  # shows this message and quits
  csp.py  # shows these examples and quits
  csp.py --yolo  # opens the Python Repl, as if:  python3 -i csp.py
"""

# code reviewed by People, Black, Flake8, & MyPy


import code
import importlib
import random
import sys


#
# Name the examples from CspBook.pdf, but compiled as Dicts and Lists of Dicts and Lists
#
#   + Write a sequence of Events as a List[Str]] of zero or more Str
#   + Write a choice of Events as a Dict[Str, List] of two or more Str
#   + Write either when it knows its own name as a Dict[Str, List | Dict] of one Str
#


#

STOP: list  # :-( MyPy requires Datatypes declared for Empty Lists

#

STOP = list()

U1 = ["coin", STOP]

U2 = ["coin", ["choc", ["coin", ["choc", STOP]]]]

CTR = ["right", "up", "right", "right", STOP]

X = "X"

CLOCK_0 = ["tick", "CLOCK_0"]
CLOCK_1 = ["tick", "CLOCK_1"]
CLOCK_2 = {"X": ["tick1", "tick2", "tick3", X]}  # missing from CspBook Pdf
CLOCK = {"X": ["tick", X]}

VMS = ["coin", "choc", "VMS"]
CH5A = ["in5p", "out2p", "out1p", "out2p", "CH5A"]
CH5B = ["in5p", "out1p", "out1p", "out1p", "out2p", "CH5B"]

U3 = {"up": STOP, "right": ["right", "up", STOP]}

CH5C = [
    "in5p",
    {
        "out1p": ["out1p", "out1p", "out2p", "CH5C"],
        "out2p": ["out1p", "out2p", "CH5C"],
    },
]

VMCT = {"X": ["coin", {"choc": X, "toffee": X}]}

VMC = {
    "in2p": ["large", "VMC"],
    "small": ["out1p", "VMC"],
    "in1p": {"small": "VMC", "in1p": {"large": "VMC", "in1p": STOP}},
}

VMCRED = {"X": {"coin": ["choc", "X"], "choc": ["coin", "X"]}}
VMS2 = ["coin", {"X": {"coin": ["choc", "X"], "choc": ["coin", "X"]}}]

COPYBIT = {"X": {"in_0": ["out_0", "X"], "in_1": ["out_1", "X"]}}

DD = {"setorange": "DD_O", "setlemon": "DD_L"}
DD_O = {"orange": "DD_O", "setlemon": "DD_L", "setorange": "DD_O"}
DD_L = {"lemon": "DD_L", "setorange": "DD_O", "setlemon": "DD_L"}


#
# Run well from the Sh Command Line
#


def main() -> None:

    # Early on, take Words in from the Sh Command Line, and give back Help Lines

    assert sys.argv[1:] == ["--yolo"], (sys.argv[1:],)

    # Run one Interactive Console, till exit

    scope = casefolds_to_scope(casefolds=["csp", "dir", "step"])

    print()
    print(">>> dir()")
    print(repr(list(scope.keys())))

    code.interact(banner="", local=scope, exitmsg="")  # not 'locals='

    print("bye")

    # 'code.interact' adds '__builtins__' into the Scope


def casefolds_to_scope(casefolds: list[str]) -> dict[str, object]:
    """Form a Scope of Names to work with"""

    scope = dict(globals())  # ordered, not sorted

    csp = importlib.import_module("csp")
    assert "csp" not in scope.keys()
    scope["csp"] = csp  # else unimported by default

    def scope_unsorted_dir(*args, **kwargs) -> list[str]:
        """List the Names in Scope, else in Args"""
        if args:
            names = __builtins__.dir(*args, **kwargs)
            return names
        names = list(scope.keys())
        return names

    assert "dir" not in scope.keys()
    scope["dir"] = scope_unsorted_dir

    assert "step" not in scope.keys()
    scope["step"] = process_step

    # Drop the casefolded Names from this Scope, except don't drop our celebrated Casefolds

    items = list(scope.items())
    for k, v in items:
        if k.startswith("_"):
            del scope[k]
        elif k == k.casefold():
            if k not in casefolds:
                del scope[k]

    # Succeed

    return scope


#
# Step and chat through a Trace of a Process
#


def process_step(P: dict | list | str) -> None:  # noqa  # FIXME: | str
    """Step and chat through a Trace of a Process"""

    print("#", P)
    print()

    # Find the first actual Process, not just its Aliases

    P1 = process_after_abs(P)

    if isinstance(P1, dict):
        assert len(P1.keys()) != 1, (len(P1.keys()), P1)

    # Start a new Trace as often as we step back to the same Process

    Q = P1
    while True:
        if Q is P1:
            print()

        # Offer 0 or more Choices

        choices = process_menu_choices(Q)

        while True:
            print(choices)

            # Quit on request

            sys.stdout.flush()
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                if sys.platform == "darwin":  # FIXME: test at Linux
                    print(" ", end="")
                print("TTY INT KeyboardInterrupt")
                return

            if not line:
                print("⌃D TTY EOF")
                return

            strip = line.strip()
            # print(f"{strip=} {choices=} SQUIRREL", end="\n\n")  # .end vs the "\x1B[A"

            # Quit when there are no Choices for stepping forward

            if not choices:
                print("BLEEP")
                return

            # Run ahead with the only Choice, when there is only one

            if len(choices) == 1:
                choice = choices[-1]
                if strip != str(choice):
                    print("\x1B[A", end="")
                    print(choice)
                break

            # Run ahead with the first whole match

            if strip in choices:
                choice = strip
                break

            # Run ahead with a random Choice

            choice = random.choice(choices)
            print("\x1B[A", end="")
            print(choice)
            break

        Q = process_choice_after(Q, choice)

        # CUU_Y = "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
        # ED_P = "\x1B" "[" "{}J"  # CSI 04/10 Erase in Display  # 0 Tail


def process_menu_choices(P: dict | list | str) -> list[str]:
    """Pick out the available next Steps forward"""

    Q = P

    n = 0
    while True:
        n += 1
        assert n < 25, (n, P, Q)

        if isinstance(Q, str):
            q_name = Q
            assert q_name in globals().keys(), (q_name,)
            Q = globals()[q_name]

            continue

        break

    assert isinstance(Q, dict) or isinstance(Q, list), (type(Q), Q)

    # Offer no Steps after the last Step

    if not Q:
        return list()

    # Offer the one Step through a first Guard

    if isinstance(Q, list):
        guard = P[0]
        Q = P[1:]

        assert guard, (guard, P)
        assert Q, (Q, P)

        return [guard]

    # Offer the Steps into a Named Process

    if len(Q.items()) == 1:
        values = list(Q.values())
        R = values[-1]  # the Named Process

        choices = process_menu_choices(R)  # recurses

        return choices

    # Else offer the two or more Choices

    choices = list(Q.keys())  # ordered, not sorted
    assert len(choices) >= 2, (choices, Q)  # because not just one Item above

    return choices


def process_choice_after(P: dict | list | str, choice: str) -> dict | list:
    """Take a particular next Step forward"""

    Q = P

    n = 0
    while True:
        n += 1
        assert n < 25, (n, P, Q)

        if isinstance(Q, str):
            q_name = Q
            assert q_name in globals().keys(), (q_name,)
            Q = globals()[q_name]

            continue

        break

    assert isinstance(Q, dict) or isinstance(Q, list), (type(Q), Q)

    #

    assert isinstance(Q, dict) or isinstance(Q, list), (type(Q), Q)

    # Take no Steps after the last Step

    assert Q, (Q,)

    # Step through the first Guard

    R: dict | list

    if isinstance(Q, list):
        guard = Q[0]
        R = Q[1:]

        assert guard, (guard, P)
        assert R, (R, choice, Q)

        # Step past a first Guard on to the next Guard

        if len(R) >= 2:
            return R

        # Step into a Process

        S = R[-1]
        T = process_after_abs(S)
        assert isinstance(T, dict) or isinstance(T, list), (type(T), T, choice, S, R, Q, P)

        return T

    # Step through the chosen Guard

    assert isinstance(Q, dict), (type(Q), Q)

    items = list(Q.items())  # ordered, not sorted
    if len(items) >= 2:

        R = Q[choice]  # maybe be an Empty STOP
        S = process_after_abs(R)
        assert isinstance(S, dict) or isinstance(S, list), (type(S), S, R, Q, choice, P)

        return S

    # Learn your own Name

    R = process_after_abs(Q)
    assert R is not Q, (R, Q, choice, P)

    return R


def process_after_abs(P: dict | list | str) -> dict | list:
    """Learn your own Name now, if named"""

    Q = P

    n = 0
    while True:
        n += 1
        assert n < 25, (n, P, Q)

        if isinstance(Q, str):
            q_name = Q
            assert q_name in globals().keys(), (q_name,)
            Q = globals()[q_name]

            continue

        if isinstance(Q, dict):
            items = list(Q.items())  # ordered, not sorted
            if len(items) == 1:
                item = items[-1]

                (q_name, Q) = item
                # print(f"globals()[{q_name!r}] = {Q!r}")
                globals()[q_name] = Q  # adds or replaces  # todo: close this Scope soon enough
                # print(f"setattr({module!r}, {q_name!r}, {Q!r})")
                # setattr(module, q_name, Q)  # adds or replaces  # todo: close this Scope soon enough

                continue

            break

        break

    return Q

    # todo: think more into opening/ mutating/ closing Scopes


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: Command-Line Input History


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/csp.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
