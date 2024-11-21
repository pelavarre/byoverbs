#!/usr/bin/env python3

r"""
usage: csp.py [-h] [-c CSP] [-i]

work with Communicating Sequential Processes (CSP) notations

options:
  -h, --help  show this message and exit
  -c CSP      compile & run a line of CSP notation (may be empty)
  -i          run the Python Repl to inspect interactively

docs:
  https://en.wikipedia.org/wiki/Communicating_sequential_processes
  http://www.usingcsp.com/cspbook.pdf (Dec/2022)

examples:
  csp.py --h  # shows this message and quits
  csp.py  # shows these examples and quits
  csp.py -i  # opens the Python Repl to work with many CspBook·Pdf examples
  csp.py -i -c ''  # opens the Python Repl to work without much
"""

# code reviewed by People, Black, Flake8, MyPy, & PyLance-Standard


import __main__
import argparse
import bdb
import code
import functools
import pdb
import random
import re
import sys
import textwrap
import traceback
import typing


#
# 1.1 Introduction
#
# List examples from CspBook·Pdf, but spoken as Dict, List, and Str
#
#   + Step across a List[Str] to reach 1 (Dict | List | Str)
#   + Take a List[ItemsOrItem] as saying (ItemsOrItem) in place of ItemsOrItem
#
#   + Branch across >= 2 Keys of a Dict[Str, Dict | List | Str]
#   + Learn your own Name on the way into a Dict[Str, Dict | List | Str] of 1 Key
#
#   + Accept a Str as an uppercase Process Name not yet defined
#   + Or accept a Str as a lowercase Event Name
#

#
# 'We shall often omit explicit mention of the Alphabet A',
#   'in the case of  μ X : A • F(X)'
#


PLENTY_DEPTH_5 = 5  # chooses how deep to trace an infinite Set of Processes


class CspBookExamples:

    #
    # 1.1.1 Prefix = Finite Flows (of Prefix And Then Process)
    #

    STOP: list
    STOP = list()

    U1 = "STOP"  # unmentioned by CspBook·Pdf
    U2 = [STOP]  # unmentioned by CspBook·Pdf

    # 1.1.1 X1  # unnamed in CspBook·Pdf
    U111X1 = ["coin", STOP]

    # 1.1.1 X2  # unnamed in CspBook·Pdf
    U111X2 = [["coin", [["choc", [["coin", [["choc", STOP]]]]]]]]
    U111X2B = ["coin", "choc", "coin", "choc", STOP]  # only described, not shown, by CspBook·Pdf

    # 1.1.1 X3
    CTR = ["right", "up", "right", "right", STOP]

    U113X3B = ["x", ["y", STOP]]

    #
    # 1.1.2 Recursion = Cyclic Flows on an Alphabet of 1 Event
    #

    CLOCK1A: list | str
    CLOCK1A = "CLOCK1A"  # CspBook·Pdf takes the lazy eval of CLOCK1 for granted
    CLOCK1A = ["tick", CLOCK1A]  # 1st of 2 'CLOCK =' of CspBook·Pdf

    # like to saying 'x = x*x + x - 2' to define x = math.sqrt(2)

    CLOCK1B: list | str
    CLOCK1B = "CLOCK1B"
    CLOCK1B = ["tick", ["tick", ["tick", CLOCK1B]]]

    # like to saying math.sqrt(2) = 1.414...

    X = "X"
    CLOCK1C = {"X": ["tick", X]}  # 1.1.2 X1  # 2nd of 2 'CLOCK =' of CspBook·Pdf

    CLOCK = "CLOCK1C"

    #
    # 1.1.3 Choice = Cyclic Flows on an Alphabet of a Few Events
    #

    CLOCK2 = {"X": ["tick", "tock", "boom", X]}  # CLOCK2 missing from CspBook·Pdf

    VMS1A: list | str
    VMS1A = "VMS1A"
    VMS1A = ["coin", ["choc", VMS1A]]  # 1st of 2 'VMS =' of CspBook·Pdf

    VMS1B = {"X": ["coin", ["choc", X]]}  # 1.1.2 X2  # 2nd of 2 'VMS =' of CspBook·Pdf

    VMS = "VMS1B"

    CH5A = ["in5p", "out2p", "out1p", "out2p", "CH5A"]  # 1.1.2 X3
    CH5B = ["in5p", "out1p", "out1p", "out1p", "out2p", "CH5B"]  # 1.1.2 X4

    #
    # Acyclic Choices and Cyclic Choices (of 2-Or-More Distinct Events)
    #

    # 1.1.3 X1  # unnamed in CspBook·Pdf
    U113X1 = {"up": STOP, "right": ["right", "up", STOP]}  # acyclic

    CH5C = [  # 1.1.3 X2  # cyclic
        "in5p",
        {
            "out1p": ["out1p", "out1p", "out2p", "CH5C"],
            "out2p": ["out1p", "out2p", "CH5C"],
        },
    ]

    VMCT = {"X": ["coin", {"choc": X, "toffee": X}]}  # 1.1.3 X3  # cyclic

    VMC: dict | str
    VMC = "VMC"
    VMC = {  # 1.1.3 X4  # acyclic
        "in2p": {"large": VMC, "small": ["out1p", VMC]},
        "in1p": {
            "small": VMC,
            "in1p": {"large": VMC, "in1p": STOP},
        },  # acyclic
    }

    VMC2: dict | str  # VMC2 missing from CspBook
    VMC2 = "VMC2"
    VMC2 = {  # 1.1.3 X4  # cyclic
        "in2p": {"large": VMC2, "small": ["out1p", VMC2]},
        "in1p": {
            "small": VMC2,
            "in1p": {"large": VMC2, "in1p": ["out1p", "out1p", "out1p", VMC2]},
        },
    }

    # todo: lean deeper into Don't-Repeat-Yourself
    # todo: [{"large": [], "small": ["out1p"]}, VMC2]  # No-Op & Single-Event Processes?
    # todo: (Y): {"large": Y, "small": ["out1p", Y]}  # Function on Process Y?

    VMCRED = {"X": {"coin": ["choc", X], "choc": ["coin", X]}}  # 1.1.3 X5  # cyclic
    VMS2 = ["coin", {"X": {"coin": ["choc", X], "choc": ["coin", X]}}]  # 1.1.3 X6  # acyclic
    # 'VMS2 =' is explicit in CspBook·Pdf, distinct from 'VMS ='

    COPYBIT = {"X": {"in_0": ["out_0", X], "in_1": ["out_1", X]}}  # 1.1.3 X7  # cyclic

    RUNA = {"R": {"a": "R", "b": "R", "c": "R"}}  # 1.1.3 X8  # cyclic

    #
    # 1.1.4 Mutural Recursion
    #

    DD: dict | str
    O: dict | str
    L: dict | str

    DD = "DD"
    O = "O"  # noqa: E741 Ambiguous Variable Name 'O'
    L = "L"

    DD = {"setorange": O, "setlemon": L}  # 1.1.4 X1  # acyclic
    O1 = {"orange": O, "setorange": O, "setlemon": L}
    L1 = {"lemon": L, "setlemon": L, "setorange": O}

    O = "O1"  # noqa: E741 Ambiguous Variable Name 'O'
    L = "L1"

    # We say  = O O L and = L L O
    # so as to show the finite past clearly before getting into the infinite futures,
    # despite CspBook·Pdf saying these shuffled, as = O L O and as = L O L

    #
    # 1.2 Pictures
    # 1.3 Laws
    #
    #   (nothing here yet)
    #


#
# Add the "CT =" example from CspBook·Pdf of an Infinite Set of Processes
#
#   We say 0: around | up, and n: down | up,
#   so as to show the finite past clearly before getting into the infinite futures,
#   despite CspBook·Pdf saying the reverse, as 0: up | around, and n: up | down
#


class ProcessFactory:

    func: typing.Callable
    str_self: str

    def __init__(self, func, chars) -> None:
        self.func = func
        self.str_self = textwrap.dedent(chars).strip()

    def __call__(self, *args, **kwargs) -> "Process":
        func = self.func
        return func(*args, **kwargs)

    def __str__(self) -> str:
        s = self.str_self
        return s


str_ct = """

    {
      0: around → CT(0) | up → CT(1)
      n: down → CT(n - 1) | up → CT(n + 1)
    }

"""


@functools.lru_cache(maxsize=None)  # make cyclic detectable by compiling each Int only once
def def_ct(n: int) -> "Process":
    d = ct_n_to_dict(n)
    p = to_process_if(d)
    return p


ct = ProcessFactory(func=def_ct, chars=str_ct)


def ct_n_to_dict(n: int) -> dict:  # 1.1.4 X2  # Cyclic CT(7) called out by 1.8.3 X5

    p: dict

    if n == 0:
        p = {"around": lambda: ct(0), "up": lambda: ct(1)}

        assert p["around"].__name__ == "<lambda>", p["around"].__name__
        assert p["up"].__name__ == "<lambda>", p["up"].__name__

        p["around"].__name__ = "CT(0)"
        p["up"].__name__ = "CT(1)"

        return p

    p = {"down": lambda: ct(n - 1), "up": lambda: ct(n + 1)}

    assert p["down"].__name__ == "<lambda>", p["down"].__name__
    assert p["up"].__name__ == "<lambda>", p["up"].__name__

    p["down"].__name__ = f"CT({n - 1})"
    p["up"].__name__ = f"CT({n + 1})"

    return p

    # todo: compare with Lisp Label's

    # todo: think about about the .__name__ connection into Class Hope


CspBookCornerTexts = [
    #
    "x → P",  # Limits on Prefix →
    "P ; Q  # Sequential Composition not yet Implemented",
    "P → Q  # P is not an Event",  # from the postscript of 1.1.1 X3 in CspBook·Pdf
    "x → y  # 'y' is not an Process",
    #
    "x → P | y → Q | z → R",  # Limits on Choice |
    "x → P | x → Q | z → R  # 'choc' can be chosen at most once",  # until Non-Determinism
    "x → P | x → Q | z → z  # 'z' is not an Process",
    "x → P | (y → Q | z → R)  # Process is not an Event to choose",
    #
]


#
# Run well from the Sh Command Line
#


main_args = argparse.Namespace()


def main() -> None:
    """Run well from the Sh Command Line"""

    ns = parse_csp_py_args_else()  # often prints help & exits
    vars(main_args).update(vars(ns))

    # Run some self-test's, then emulate:  python3 -i csp.py

    try_func_else_pdb_pm(func=main_try)


def try_func_else_pdb_pm(func) -> None:
    """Call a Py Func, but post-mortem debug an unhandled Exc"""

    try:
        func()
    except bdb.BdbQuit:
        raise
    except Exception as exc:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        assert exc is exc_value

        if not hasattr(sys, "last_exc"):
            sys.last_exc = exc_value

        traceback.print_exc(file=sys.stderr)

        print("\n", file=sys.stderr)
        print("\n", file=sys.stderr)
        print("\n", file=sys.stderr)

        print(">>> sys.last_traceback = sys.exc_info()[-1]", file=sys.stderr)
        sys.last_traceback = exc_traceback

        print(">>> pdb.pm()", file=sys.stderr)
        pdb.pm()

        raise


def parse_csp_py_args_else() -> argparse.Namespace:
    """Take Words in from the Sh Command Line"""

    doc = __main__.__doc__
    assert doc, (doc,)

    parser = doc_to_parser(doc, add_help=True, epilog_at="examples:")

    c_help = "compile & run a line of CSP notation (may be empty)"
    i_help = "run the Python Repl to inspect interactively"

    parser.add_argument("-c", metavar="CSP", help=c_help)
    parser.add_argument("-i", action="count", help=i_help)

    ns = parse_args_else(parser)
    return ns

    # works much like:  python3 -i -c ''
    # works much like:  python3 -c ''
    # works much like:  python3 --


def doc_to_parser(doc: str, add_help: bool, epilog_at: str) -> argparse.ArgumentParser:
    """Form an ArgParse ArgumentParser out of the Doc, often the Main Doc"""

    assert doc
    strip = doc.strip()
    lines = strip.splitlines()

    usage = lines[0]
    prog = usage.split()[1]
    description = lines[2]

    epilog = strip[strip.index(epilog_at) :]

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=True,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    return parser


def parse_args_else(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Take Words in from the Sh Command Line, else Print Help and Exit"""

    epilog = parser.epilog
    assert epilog, (epilog,)

    shargs = sys.argv[1:]
    if sys.argv[1:] == ["--"]:  # ArgParse chokes if Sep present without Pos Args
        shargs = list()

    testdoc = textwrap.dedent("\n".join(epilog.splitlines()[1:]))
    if not sys.argv[1:]:
        print()
        print(testdoc)
        print()

        sys.exit(0)  # exits 0 after printing help

    ns = parser.parse_args(shargs)
    return ns

    # often prints help & exits


#
# 1.4 Implementation of processes
#
# Deserialize a Csp Process out of a Dict | List | Str | Callable
# Deserialize a Dict | List | Str eagerly now, deserialize a Callable later when run
#


CODE_SCOPE: dict[str, object]
CODE_SCOPE = dict()


EventName = str
ProcessName = str


def str_is_event_name(chars) -> bool:
    if chars == chars.lower():  # todo: think over .lower vs .casefold @ .is_event_name
        assert chars != chars.upper(), (chars,)
        return True
    return False

    # todo: explain why Event Name required


def str_is_process_name(chars) -> bool:
    if chars == chars.upper():
        assert chars != chars.lower(), (chars,)
        return True
    return False

    # todo: explain why Process Name required


class Process:  # SuperClass  # in itself, an Empty List of no Events  # []
    """List the Def's of every Process"""

    def __abs__(self) -> "Process":
        """FIXME: find words to explain def __abs__"""
        return self

    def __call__(self, *args, **kwargs) -> typing.Union["Process", str, None]:
        """Step interactively if no Args, else return After-Process-Of, else Raise Exception"""

        if (not args) and (not kwargs):
            process_step(self)
            return None

        def func(choice) -> typing.Union["Process", str]:
            choices = self.menu_choices()
            if choice in choices:
                p = self.after_process_of(choice)
                return p

            return "BLEEP"

        if (len(args) == 1) and (not kwargs):
            choice = args[-1]
            result = func(choice)
            return result

        if (not args) and (list(kwargs.keys()) == ["choice"]):
            choice = kwargs["choice"]
            result = func(choice)
            return result

        p = self.after_process_of(*args, **kwargs)  # raises TypeError
        return p

    def menu_choices(self) -> list[str]:
        """Offer no Menu Choices, like a Stop Process"""

        return list()

        # CspBook·Pdf 'def menu' offers only Event Choices from a given Alphabet

    def after_process_of(self, choice: str) -> "Process":
        """Take no Menu Choices"""

        raise NotImplementedError("after_process_of")

    # works like the StopProcessMention, till overriden
    # except its __str__ is the default object.__str__, doesn't say "STOP"

    # todo: toggle off '==' equality, to test clients only take 'is' equality


SerializedProcess = Process | dict | list | ProcessName | typing.Callable
SerializedEventOrProcess = EventName | SerializedProcess


def to_process_if(o: Process | SerializedProcess) -> Process:
    """Return a Process unchanged, else a deserialized Process"""

    # Accept a Process as is

    if isinstance(o, Process):
        return o  # todo: 'better copied than aliased' vs .to_process_if

    # Accept a Callable to hold for now, to run later

    if callable(o):
        if o.__name__ in hope_by_name.keys():
            hope = hope_by_name[o.__name__]
            return hope

        hope = Hope(o)  # todo: why not add this Hope into .hope_by_name here?
        return hope

    # Form a Choice from a large Dict, or a Cloak from a Dict of 1 Item

    if isinstance(o, dict):
        items = list(o.items())
        if len(items) >= 2:
            choice = Choice(d=o)
            return choice

        item = items[-1]

        key = item[0]
        value = item[-1]

        cloak = Cloak(key, value=value)
        return cloak

    # Form a Stop or Box or Flow from a List  # todo: or like Sequence P ; Q ; R

    if isinstance(o, list):
        if not o:
            o = StopProcessMention
            return o

        if len(o) == 1:
            box = Box(o[-1])
            return box

        assert len(o) >= 2, (len(o), o)

        flow = Flow(cells=o)
        return flow

    # Find the Process in the Run-Time Scope by Name later

    assert isinstance(o, str), (type(o), o)
    assert str_is_process_name(o), (o,)

    nym = Mention(o, value=StopProcess)
    return nym


class Flow(Process):  # List of Events then Process  # ["tick", "tock", "boom", X]
    """Take one or more Events, then run a Process"""

    guard: str
    after: Process

    def __init__(self, cells: list[SerializedEventOrProcess]) -> None:

        assert len(cells) >= 2, (len(cells), cells)

        if not isinstance(cells[-1], list):
            after = to_process_if(cells[-1])
        else:
            p = to_process_if(cells[-1])
            if not isinstance(p, Flow):
                after = p
            else:
                after = Box(p)

        for index in reversed(range(1, len(cells) - 1)):
            guard = cells[index]
            assert isinstance(guard, str), (type(guard), guard, cells)
            assert str_is_event_name(guard), (guard,)

            pair: list[SerializedEventOrProcess]
            pair = [guard, after]

            after = Flow(pair)

        guard = cells[0]
        assert isinstance(guard, str), (type(guard), guard, cells)
        assert str_is_event_name(guard), (guard,)

        self.guard = guard
        self.after = after

    def __str__(self) -> str:
        """Speak of this Flow Process as (x → P)"""

        guard = self.guard
        after = self.after

        g = guard
        a = str(after)
        if isinstance(after, Flow):
            a = a.removeprefix("(").removesuffix(")")

        s = f"{g} → {a}"
        s = f"({s})"  # '(x → y → P)'

        return s

    def menu_choices(self) -> list[str]:
        """Offer 1 Menu Choice"""

        guard = self.guard
        choices = [guard]  # one choice only
        return choices

    def after_process_of(self, choice: str) -> Process:
        """Step through the 1 Menu Choice"""

        guard = self.guard
        after = self.after
        assert choice == guard, (choice, guard, self)
        return after


class Choice(Process):  # Dict of 2 or more Process by Event  # {"choc": X, "toffee": X}
    """Take one Event as a choice of which Process to run"""

    by_choice: dict[str, Process]

    def __init__(self, d: dict[EventName, SerializedProcess]) -> None:

        assert len(d.keys()) >= 2, (d.keys(),)

        by_choice = dict()
        for k, v in d.items():
            assert isinstance(k, str), (k,)

            choice = k
            after = to_process_if(v)

            by_choice[choice] = after

        self.by_choice = by_choice

    def __str__(self) -> str:
        """Speak of this Choice Process as (x → P | y → Q | ...)"""

        by_choice = self.by_choice

        s = " | ".join(f"{k} → {v}" for (k, v) in by_choice.items())
        s = f"({s})"

        return s

    def menu_choices(self) -> list[str]:
        """Offer 2 or more Menu Choices"""

        by_choice = self.by_choice
        choices = list(by_choice.keys())
        return choices

    def after_process_of(self, choice: str) -> Process:
        """Step through 1 particular Menu Choice"""

        by_choice = self.by_choice
        choices = self.menu_choices()

        assert choice in choices, (choice, choices)
        after = by_choice[choice]

        return after


class Box(Process):  # List of 1 Process  # [STOP]
    """Run a Process inside a Context"""

    value: Process

    def __init__(self, value: SerializedProcess) -> None:
        super().__init__()

        self.value = to_process_if(value)

    def __abs__(self) -> Process:
        """Unbox the first Process boxed here (unless overriden)"""

        value = self.value
        return value

    def __str__(self) -> str:
        """Speak of the Value as inside Parentheses"""

        value = self.__abs__()

        s = value.__str__()
        if not (s.startswith("(") and s.endswith(")")):
            s = "(" + s + ")"

        return s

    def menu_choices(self) -> list[str]:
        """Offer the Menu Choices of the Value"""

        value = self.__abs__()
        if value is self:
            no_choices: list[str]
            no_choices = list()
            return no_choices

        choices = value.menu_choices()
        return choices

    def after_process_of(self, choice: str) -> "Process":
        """Forward a Menu Choice into the Value"""

        value = self.__abs__()

        p = value.after_process_of(choice)
        return p


class Cloak(Box):  # Dict {"X": ["tick", X]}
    """Run a Process with a Name, and an awareness of its own Name"""

    key: str

    def __init__(self, key: str, value: SerializedProcess) -> None:
        super().__init__(value=value)

        assert key, (key,)
        self.key = key

        eq_push(key, value=self)
        self.value = to_process_if(value)  # replaces
        eq_pop(key, value=self)

    def __str__(self) -> str:
        """Speak of the Value as self-aware:  μ X • [... X ... X ...]"""

        key = self.key
        value = self.value
        s = f"μ {key} • {value}"  # 'μ X • ["tick", X]'
        return s


class Mention(Box):  # Str "X"
    """Run a Process with a Name, but without an awareness of its own Name"""

    key: str

    cloak: Cloak | None

    def __init__(self, key: str, value: SerializedProcess) -> None:
        super().__init__(value)

        g = CODE_SCOPE

        assert key, (key,)
        self.key = key

        self.cloak = None
        if key in g.keys():
            v = g[key]
            if isinstance(v, Cloak):
                self.cloak = v

    def __abs__(self) -> Process:
        """Unbox the present Value of the Key in the Scope"""

        g = CODE_SCOPE

        cloak = self.cloak
        key = self.key

        if cloak:
            return cloak

        if key not in g.keys():
            return StopProcess

        value = g[key]
        assert isinstance(value, Process), (type(value), key)
        return value

    def __str__(self) -> str:
        """Speak of the Value by Name"""

        key = self.key
        s = key
        return s


class Hope(Process):  # Callable
    """Run a Process defined later, by calling a Func when needed"""

    func: typing.Callable
    process: Process | None

    def __init__(self, func: typing.Callable) -> None:
        super().__init__()

        self.func = func
        self.process = None

        assert func.__name__ not in hope_by_name.keys(), (func.__name__,)
        hope_by_name[func.__name__] = self

    def __abs__(self) -> Process:
        """Unbox the first Value of the Func"""

        p = self.process
        func = self.func

        if not p:
            p = to_process_if(func())
            assert p, (p, func)

            self.process = p

        return p

    def __str__(self) -> str:
        """Speak of X marks the spot"""

        func = self.func
        s = func.__name__
        return s


#
# FIXME Find words to say what this is about
#


StopProcess = Process()  # akin to Lisp Nil and Python None  # as if a Flow of no Events

StopProcessMention = Mention(key="STOP", value=StopProcess)


eq_pushes: list[tuple[str, object | None]]
eq_pushes = list()

hope_by_name: dict[str, Hope]
hope_by_name = dict()


def eq_push(key: str, value: object) -> None:
    """Define the Key as a Variable until .eq_pop"""

    g = CODE_SCOPE

    assert key, (key,)
    assert value is not None, (value,)

    if key not in g.keys():
        v = None
    else:
        v = g[key]
        assert v is not None, (key, v)

    eq_push = (key, v)
    eq_pushes.append(eq_push)

    g[key] = value

    # todo: more robust Scoping, beyond .eq_push Shadowing


def eq_pop(key: str, value: object | None) -> None:
    """Undo the .eq_push now"""

    g = CODE_SCOPE

    assert key in g.keys(), (key,)
    assert g[key] is value, (g[key], value)

    eq_push = eq_pushes.pop()
    (k, v) = eq_push
    assert k == key, (k, key, value)

    if v is None:
        del g[k]
    else:
        g[k] = v

    # todo: more robust Scoping, beyond .eq_pop Shadowing


#
# 1.5 Traces
#

# ["x", "y"]  # Csp ⟨x,y⟩
# ["x"]  # Csp ⟨x⟩
# []  # Csp ⟨⟩

# ["coin", "choc", "coin", "choc"]  # 1.5 X1
# ["coin", "choc", "coin"]  # 1.5 X2
# []  # 1.5 X3

# []  # 1.5 X4
# ["in2p"], ["in1p"]
# ["in2p", "large"], ["in2p", "small"], ["in1p", "in1p"], ["in1p", "small"]  # at CspBook·Pdf
# ["in2p", "large"], ["in1p", "small"], ["in2p", "small"], ["in1p", "in1p"]  # at 'csp.sketch(VMC)'

# ["in1p", "in1p", "in1p"]  # 1.5 X5


#
# 1.6 Operations on Traces
#


# 1.6.1 Catenation

# s⌢t  # Py (s + t)

# ["coin", "choc"] + ["coin", "toffee"] = ["coin", "choc", "coin", "toffee"]
# ["in1p"] + ["in1p"] = ["in1p", "in1p"]
# ["in1p", "in1p"] + [] = ["in1p", "in1p"]

# (s + []) == ([] + s) == s  # 1.6.1 L1
# (s + (t + u)) == ((s + t) + u)  # 1.6.1 L2

# (s + t) == (s + u)  iff  (t = u)  # 1.6.1 L3
# (s + t) == (u + t)  iff  (s = u)  # 1.6.1 L4
# (s + t) == []  iff  ((s == []) and (t == []))  # 1.6.1 L5

# 0 * t == []  # 1.6.1 L6
# (n + 1) * t == (t + (n * t))  # 1.6.1 L7

# (n + 1) * t == ((n * t) + t)  # 1.6.1 L8
# (n + 1) * (s + t) == (s + (n * (t + s)) + t))  # 1.6.1 L9


# 1.6.2 Restriction  # Csp (t ↾ A)

assert list(_ for _ in ["around", "up", "down", "around"] if _ in ["up", "down"]) == ["up", "down"]


# 1.6.3 Head and tail  # Csp Subscript 0  # Csp '
# 1.6.4 Star  # Csp Superscript *
# 1.6.5 Ordering  # Csp s ≤ t  # s is a prefix of t
# 1.6.6 Length  # Csp Len #t  # Csp Count #(t ↾ A)


#
# 1.7 Implementation of Traces ('in the obvious way by lists of atoms')
#
# 1.8 Traces of a Process
# 1.8.1 Laws
# 1.8.2 Implementation
# 1.8.3 After  # Csp P / s
#


#
# Run some Self-Test's, and then emulate:  python3 -i csp.py
#


def main_try() -> None:
    """Run some Self-Test's, and then emulate:  python3 -i csp.py"""

    if main_args.c:
        raise NotImplementedError(main_args.c)

    # Form 1 Scope

    code_scope = CODE_SCOPE
    g = code_scope

    assert not code_scope

    code_scope["__annotations__"] = dict()
    code_scope["__builtins__"] = __builtins__  # 'code.interact' adds '__builtins__', if missing
    code_scope["__doc__"] = None
    code_scope["__name__"] = "__console__"

    csp = argparse.Namespace(  # todo: redefine 'import csp' to be something like this small
        csp=sys.modules[__name__],
        exec_=exec_,
        eval_=eval_,
        sketch=sketch,
    )

    code_scope["csp"] = csp  # not '["csp"] = __main__', and not 'import csp'
    code_scope["dir"] = lambda *args, **kwargs: scope_unsorted_dir(code_scope, *args, **kwargs)

    if main_args.c is None:

        # Compile each Example Process,
        # from (Dict | List | Str), to a Process Variable with the same Name

        from_scope = dict(vars(CspBookExamples))
        from_scope = dict(_ for _ in from_scope.items() if _[0].upper() == _[0])

        csp_texts = scope_compile_processes(code_scope, from_scope=from_scope)

        assert g["U1"] is g["STOP"], (g["U1"], g["STOP"])
        assert g["CLOCK"] is g["CLOCK1C"], (g["CLOCK"], g["CLOCK1C"])
        assert g["VMS"] is g["VMS1B"], (g["VMS"], g["VMS1B"])

        code_scope["CT"] = ct

        for csp_text in csp_texts:
            cp = Parser(csp_text)
            ok = cp.take_exec()

            assert ok, (csp_text, cp.takes)
            # todo: add failing test of:  lemon

            assert len(cp.takes) == 1, (len(cp.takes), cp.takes)
            assert len(cp.takes[-1]) == 1, (len(cp.takes[-1]), cp.takes[-1])

        # Sketch the infinity of Processes defined by 'def CT'

        iprint()
        iprint("CT(n) =", code_scope["CT"])

        assert PLENTY_DEPTH_5 == 5

        limit = 5
        afters = process_to_afters(ct(0), limit=limit)
        iprint("\n".join(", ".join(_) for _ in afters))
        iprint(f"# quit tracing infinite depth, after {limit} Processes #")

        assert code_scope["CT"] is ct, (code_scope["CT"], ct)

        iprint()
        iprint("CT(4) =", ct(4))
        iprint("# not tracing CT(4) #")

        # Require some Compile-Time Errors

        iprint()
        for text in CspBookCornerTexts:
            iprint(text)
            (head, sep, tail) = text.partition("#")

            evallable = head.rstrip()
            if not tail:
                eval_(evallable)
                continue

            try:
                eval_(evallable)
            except Exception:
                continue

            assert False, text

    # Run one Interactive Console, till exit, much as if:  python3 -i csp.py

    if main_args.i:

        iprint()
        iprint(">>> dir()")
        iprint(repr(list(code_scope.keys())))
        iprint(">>> ")

        code.interact(banner="", local=code_scope, exitmsg="")  # not 'locals='

    # Succeed

    print("bye")


def sketch(process) -> None:

    assert PLENTY_DEPTH_5 == 5

    limit = 5
    afters = process_to_afters(process, limit=limit)
    print("\n".join(", ".join(_) for _ in afters))

    # todo: mention when the depth limit of .sketch matters
    # todo: vary the depth of .sketch
    # todo: visit the Process'es, don't just print them


def scope_unsorted_dir(scope, *args, **kwargs) -> list[str]:
    """List the Names in Scope in order, else an alphabetical sort of the Names in Args"""

    if args or kwargs:
        names = __builtins__.dir(*args, **kwargs)
        return names

    names = list(scope.keys())

    return names


def scope_compile_processes(to_scope, from_scope) -> list[str]:
    """Compile each named (Dict | List | Str) into a Process Variable with the same Name"""

    # Abbreviate some names

    t = to_scope
    f = from_scope

    # Create each Process Mention

    for k, v in f.items():
        assert isinstance(v, (dict | list | str)), (type(v), v, k)
        assert k not in t.keys(), (k,)

        p = Mention(k, value=StopProcess)
        t[k] = p

    # Compile each Process into its own Mention, in order

    str_by_alias = dict()

    for k, v in f.items():
        p = t[k]
        assert p.value is StopProcess, (p.value,)

        q = to_process_if(v)
        assert q is not StopProcess, (q,)

        if isinstance(q, Mention):  # collapses Mentions', but not Box'es nor Cloak's
            str_by_alias[k] = q.key
            q = q.__abs__()

        p.value = q
        t[k] = q  # mutates t[k]

    # Print each Process

    csp_texts = list()
    for k in f.keys():
        p = t[k]

        s = str(p)
        if k in str_by_alias.keys():
            s = str_by_alias[k]

        csp_text = f"{k} = {s}"
        csp_texts.append(csp_text)

        iprint()
        iprint(csp_text)

        # Print each Flow through the Process

        if (k != "STOP") and (k in str_by_alias.keys()):
            if k == s:
                iprint("# infinite loop #")  # todo: think more about STOP = STOP vs X = X
        else:
            # print(f"{k=}  # scope_compile_processes")
            afters = process_to_afters(p)
            iprint("\n".join(", ".join(_) for _ in afters))

    return csp_texts


def iprint(*args, **kwargs) -> None:
    """Form a Line of Text, but only print it if running on into our -i Repl"""

    itext = " ".join(str(_) for _ in args)
    if main_args.i:
        print(itext, **kwargs)


#
# Spell out the Event Traces of each Example Process, and its Name
# CspBook·Pdf doesn't discuss this, doesn't upvote its breadth-first bias
#


empty_list: list
empty_list = list()


def process_to_afters(p: Process, limit=None, *, after: list[str] = empty_list) -> list[list[str]]:
    """Walk the Traces of a Process"""

    q = p.__abs__()
    q_after = after

    # Choose how to speak of empty and infinite futures

    bleep = "BLEEP"
    etc = "..."
    top = "."

    # Work on while work remains
    # Start a new Trace as often as we step back to the same Process

    afters = list()

    processes: list[Process]
    processes = list()

    pairs: list[tuple[Process, list[str]]]
    pairs = list()

    q_pair = (q, q_after)
    pairs.append(q_pair)

    q1 = q  # aliases
    while pairs:
        (q, q_after) = pairs.pop(0)

        # Stop work after running out of Choices

        choices = q.menu_choices()
        if not choices:
            afters.append(q_after + [bleep])
            continue

        # Visit each Choice in parallel, breadth-first

        for choice in choices:
            r = q.after_process_of(choice)
            s = r.__abs__()

            s_after = q_after + [choice]

            # Stop work after looping to reach the first compiled process

            if (r is p) or (r is q1) or (s is p) or (s is q1):  # todo: test all four?
                afters.append(s_after + [top])
                continue

            # Don't revisit the already visited

            if (r in processes) or (s in processes):
                afters.append(s_after + [etc])
                continue

            if s.menu_choices():
                processes.append(r)  # todo: track max Processes compiled
                processes.append(s)

                if limit is not None:
                    if len(processes) > (2 * limit):  # count 'r', count 's'
                        return afters

            # Else work on

            s_pair = (s, s_after)
            pairs.append(s_pair)

    # Succeed

    return afters


#
# Step and chat through a Trace of a Process
#


def process_step(p: Process) -> None:
    """Step and chat through a Trace of a Process"""

    # Start a new Trace as often as we step back to the same Process

    print("#", p)
    print()

    q = p
    q1 = q  # aliases
    while True:
        if q is q1:
            print()

        # Offer 0 or more Choices

        choices = q.menu_choices()
        print(choices)

        sys.stdout.flush()
        line = process_step_stdin_readline(choices)
        if not line:
            return

        choice = process_step_choose_and_reprint(choices, line=line)
        assert choice, (choice, line, choices)

        r = q.after_process_of(choice)

        q = r  # replaces

    # todo: DD() prints '(setorange → O | setlemon → L)' without explaining 'O' and 'L'


def process_step_stdin_readline(choices) -> str:
    """Return "" to quit, else a non-empty Line of Input"""

    # Quit on request

    try:
        line = sys.stdin.readline()
    except KeyboardInterrupt:  # same across sys.platform in ["darwin", "linux"] nowadays
        print(" KeyboardInterrupt")  # --> ⌃C KeyboardInterrupt
        return ""

    if not line:
        print("⌃D EOFError")  # as if 'except EOFError' for 'input()'
        return ""

    if line.strip() == "END":  # CspBook·Pdf reserves Bleep/ Stop/ End
        return ""

    # Quit when there are no Choices for stepping forward

    if not choices:
        print("BLEEP")
        return ""

    return line


def process_step_choose_and_reprint(choices, line) -> str:
    """Pick a next Step, and leave it echoed on Screen"""

    strip = line.strip()

    # Run ahead with the only Choice, when there is only one

    if len(choices) == 1:
        choice = choices[-1]
        if strip != str(choice):
            print("\x1B[A", end="")
            print(choice)

        return choice

        # CUU_Y = "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up

    # Run ahead with the first whole match

    if strip in choices:
        choice = strip

        return choice

    # Else erase the input and run ahead with a random Choice

    choice = random.choice(choices)
    print("\x1B[A", end="")
    print(choice)

    return choice

    # CspBook·Pdf says beep audibly and hang while wrong choices


#
# Parse Lines of CSP Instructions, by way of this Grammar =>
#
#   Text = Instruction End
#   Instruction = Assignment | Process
#   Assignment = Named "=" Process
#
#   Process = Wrapped | Unwrapped
#   Wrapped = "(" Process ")"
#   Unwrapped = Choice | Chosen

#   Choice = Event "→" Chosen "|" Event "→" Chosen { "|" Event "→" Chosen }
#   Chosen = Wrapped | Flow | Cloak | Named
#   Flow = Event "→" { Event "→" } Process
#   Cloak = "μ" Named "•" Process
#
#   Named = Word
#   Event = Word
#


def eval_(csp_text: str) -> Process:
    """Compile and run 1 Csp Evallable Instruction"""

    cp = Parser(csp_text)
    ok = cp.take_eval()
    assert ok, (csp_text,)  # todo: explain why Parse failed

    assert len(cp.takes) == 1, (len(cp.takes), cp.takes)
    assert len(cp.takes[-1]) == 1, (len(cp.takes[-1]), cp.takes[-1])

    evallable = cp.takes[-1][-1]

    p = to_process_if(evallable)

    process_to_afters(p)  # raises Exception if broken, now, before returning

    return p


def exec_(csp_text: str) -> None:
    """Compile and run 1 Csp Execcable Instruction"""

    g = CODE_SCOPE

    cp = Parser(csp_text)
    ok = cp.take_exec()
    assert ok, (csp_text,)  # todo: explain why Parse failed

    assert len(cp.takes) == 1, (len(cp.takes), cp.takes)
    assert len(cp.takes[-1]) == 1, (len(cp.takes[-1]), cp.takes[-1])

    execcable = cp.takes[-1][-1]

    # Accept an Assignment

    if isinstance(execcable, list):
        assert execcable, (execcable,)

        item_0 = execcable[0]
        if isinstance(item_0, str) and str_is_process_name(item_0):
            assert len(execcable) == 2, (len(execcable), execcable)

            (name, process) = execcable
            # print(f"execcable = {execcable}")  # todo: log this Parser Result
            p = to_process_if(process)

            g[name] = p

            process_to_afters(p)  # raises Exception if broken, now, before returning

            return

    # Else accept an anonymous Process

    p = to_process_if(execcable)

    process_to_afters(p)  # raises Exception if broken, now, before returning


class Parser:

    text: str  # the Source Chars to consume
    index: int  # the Count of Source Chars consumed

    starts: list[int]  # the index'es to backtrack to
    takes: list[dict | list | str]  # the parsed Instruction

    def __init__(self, text) -> None:

        start = 0
        starts = list()
        starts.append(start)

        takes: list[dict | list | str]
        take: list

        takes = list()
        take = list()
        takes.append(take)

        self.text = text
        self.index = start
        self.starts = starts
        self.takes = takes

        # todo: make self.text[self.index:] more available
        # point out "(" found when ")" missing, and "{" found when "}" missing

    #
    # Take 1 Instruction
    #

    def take_exec(self) -> bool:
        """Exec = Execcable End"""

        self.open_take()
        ok = self.take_execcable() and self.take_end()
        ok = self.close_take(ok)

        return ok

    def take_execcable(self) -> bool:
        """Execcable = Assignment | Process"""

        self.open_take()
        ok = self.take_assignment() or self.take_process()
        ok = self.close_take(ok)

        return ok

    def take_assignment(self) -> bool:
        """Assignment = Named "=" Process"""

        self.open_take()
        ok = self.take_named() and self.take_mark("=") and self.take_process()
        ok = self.close_take(ok)

        return ok

    def take_eval(self) -> bool:
        """Eval = Process End"""

        self.open_take()
        ok = self.take_process() and self.take_end()
        ok = self.close_take(ok)

        return ok

    #
    # Wrap Processes in Round Brackets (aka, Parentheses)
    #

    def take_process(self) -> bool:
        """Process = Wrapped | Unwrapped"""

        self.open_take()
        ok = self.take_wrapped() or self.take_unwrapped()
        ok = self.close_take(ok)

        return ok

    def take_wrapped(self) -> bool:
        """Wrapped = "(" Process ")" """

        self.open_take()
        ok = self.take_mark("(") and self.take_process() and self.take_mark(")")
        ok = self.close_take(ok)

        return ok

    def take_unwrapped(self) -> bool:
        """Unwrapped = Choice | Chosen"""

        self.open_take()
        ok = self.take_choice() or self.take_chosen()
        ok = self.close_take(ok)

        return ok

    #
    # Pick apart Choice and Flow and Cloak
    #

    def take_choice(self) -> bool:
        """Choice = Event "→" Chosen "|" Event "→" Chosen { "|" Event "→" Chosen }"""

        self.open_take()
        ok = self.take_event() and self.take_mark("→") and self.take_chosen()
        ok = ok and self.take_mark("|")
        ok = ok and self.take_event() and self.take_mark("→") and self.take_chosen()

        self.open_take()
        more_ok = ok
        while more_ok:
            more_ok = self.take_mark("|")
            more_ok = more_ok and self.take_event() and self.take_mark("→") and self.take_process()
            self.close_accept_one_take(more_ok)
            self.open_take()
        self.close_accept_one_take(False)

        ok = self.close_take(ok)

        if ok:
            deepest_take = self.takes[-1]
            assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
            take = deepest_take[-1]
            assert isinstance(take, list), (type(take), take)

            assert len(take) >= 4, (len(take), take)
            assert (len(take) % 2) == 0, (len(take), take)

            d = dict()
            events = take[::2]
            for event, process in zip(take[::2], take[1::2]):
                d[event] = process

            keys = list(d.keys())
            assert keys == events, (keys, events)  # todo: explain Event Choices must be distinct

            deepest_take[-1] = d

        return ok

    def take_chosen(self) -> bool:
        """Chosen = Wrapped | Flow | Cloak | Named"""

        self.open_take()
        ok = self.take_wrapped() or self.take_flow() or self.take_cloak() or self.take_named()
        ok = self.close_take(ok)

        return ok

    def take_flow(self) -> bool:
        """Flow = Event "→" { Event "→" } Process"""

        self.open_take()
        ok = self.take_event() and self.take_mark("→")

        self.open_take()
        more_ok = ok
        while more_ok:
            more_ok = self.take_event() and self.take_mark("→")
            self.close_accept_one_take(more_ok)
            self.open_take()
        self.close_accept_one_take(False)

        ok = ok and self.take_process()

        ok = self.close_take(ok)

        return ok

    def take_cloak(self) -> bool:
        """Cloak = "μ" Named "•" Process"""

        self.open_take()
        ok = (
            self.take_mark("μ") and self.take_named() and self.take_mark("•") and self.take_process()
        )
        ok = self.close_take(ok)

        if ok:
            deepest_take = self.takes[-1]
            assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
            take = deepest_take[-1]
            assert isinstance(take, list), (type(take), take)

            assert len(take) == 2, (len(take), take)
            (name, process) = take

            d = dict()
            d[name] = process
            deepest_take[-1] = d

        return ok

    #
    # Accept a Process or Event Name
    #

    def take_named(self) -> bool:
        """Named = Word"""

        self.open_take()
        ok = self.take_word()  # todo: require Uppercase for Process Names
        ok = self.close_take(ok)

        return ok

    def take_event(self) -> bool:
        """Event = Word"""

        self.open_take()
        ok = self.take_word()  # todo: require Lowercase for Event Names
        ok = self.close_take(ok)

        return ok

    #
    # Accept one Grammar
    #

    def take_end(self) -> bool:
        """Take the End of the Text"""

        self.drop_blanks()

        assert 0 <= self.index <= len(self.text)
        ok = self.index == len(self.text)

        return ok

    def drop_blanks(self) -> None:
        """Drop one or more Blanks, if present there"""

        index = self.index
        text = self.text

        text1 = text[index:]
        lstrip = text1.lstrip()
        length = len(text1) - len(lstrip)

        self.index = index + length

    def take_word(self) -> bool:
        """Take any one Name"""

        self.drop_blanks()

        index = self.index
        takes = self.takes
        text = self.text

        # Fail now if Name not found

        text1 = text[index:]  # todo: more than r"[a-zA-Z_]" as Letters in Names
        m = re.match(r"^[a-zA-Z_][a-zA-Z_0-9]*", string=text1)
        if not m:
            return False

        name = m.group()

        # Take the Name

        take = name

        self.index += len(name)

        deepest_take = takes[-1]
        assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
        deepest_take.append(take)

        # Succeed

        return True

    def take_mark(self, mark) -> bool:
        """Take a matching Mark"""

        self.drop_blanks()

        index = self.index
        text = self.text

        # Fail now if Mark not found

        text1 = text[index:]
        if not text1.startswith(mark):
            return False

        # Take the Mark

        self.index += len(mark)

        # Succeed

        return True

    #
    #
    #

    def open_take(self) -> None:
        """Open up a List of Takes"""

        index = self.index
        starts = self.starts
        takes = self.takes

        starts.append(index)

        take: list
        take = list()

        takes.append(take)

    def close_take(self, ok) -> bool:
        """Commit and close a List of Takes, else backtrack"""

        starts = self.starts
        takes = self.takes

        start = starts.pop()
        take = takes.pop()
        while isinstance(take, list) and (len(take) == 1):
            take = take[-1]

        if not ok:
            self.index = start
            return False

        deepest_take = takes[-1]
        assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
        deepest_take.append(take)

        return True

    def close_accept_one_take(self, ok) -> bool:
        """Commit and close and merge a List of Takes, else backtrack"""

        starts = self.starts
        takes = self.takes

        start = starts.pop()
        take = takes.pop()
        while isinstance(take, list) and (len(take) == 1):
            take = take[-1]

        if not ok:
            self.index = start
            return False

        deepest_take = takes[-1]
        assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
        if not isinstance(take, list):
            deepest_take.append(take)
        else:
            deepest_take.extend(take)

        return True

        # todo: I once wrote 'todo: say this is better'. Ugh. Better than what??


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: Pull 'nope's and 'compilation failure's from 'bin/csp6.py', then retire it
# todo: Code for showing Cyclicity, showing Acyclity, giving up after a limit?
# todo: Command-Line Input History


# todo: pass more interactive tests

TESTS = """

    P1 = csp.eval_("lime → P2")
    P2 = csp.eval_("fig → STOP")
    csp.sketch(P1)  # should be: lime, fig, BLEEP

    P9 = csp.eval_('(coin → STOP)')
    print(P9("coin"))  # could know it is STOP

"""


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/csp.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
