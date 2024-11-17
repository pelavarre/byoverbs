#!/usr/bin/env python3

r"""
usage: csp.py [-h] [--yolo]

work with Communicating Sequential Processes (CSP) notations

options:
  -h, --help  show this message and exit
  --yolo      do what's popular now

docs:
  https://en.wikipedia.org/wiki/Communicating_sequential_processes
  http://www.usingcsp.com/cspbook.pdf (Dec/2022)

examples:
  csp.py --h  # shows this message and quits
  csp.py  # shows these examples and quits
  csp.py --yolo  # opens the Python Repl, as if:  python3 -i csp.py
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


class CspBookExamples:

    #
    # Finite Flows
    #

    STOP: list
    STOP = list()

    # U1 = STOP  # unmentioned by CspBook·Pdf  # FIXME: make this mean:  U1 is STOP
    # U2 = [STOP]  # unmentioned by CspBook·Pdf  # FIXME: make this mean:  U2 = (STOP)

    # 1.1.1 X1  # unnamed in CspBook·Pdf
    U111X1 = ["coin", STOP]

    # 1.1.1 X2  # unnamed in CspBook·Pdf
    # U111X2 = [["coin", [["choc", [["coin", [["choc", STOP]]]]]]]]  # FIXME: more faithful
    U111X2 = ["coin", ["choc", ["coin", ["choc", STOP]]]]

    # 1.1.1 X3
    CTR = ["right", "up", "right", "right", STOP]

    #
    # Cyclic Flows on an Alphabet of 1 Event
    #

    CLOCK1A: list | str
    CLOCK1A = "CLOCK1A"  # CspBook·Pdf takes the lazy eval of CLOCK1 for granted
    CLOCK1A = ["tick", CLOCK1A]  # 1st of 2 'CLOCK =' of CspBook·Pdf

    X = "X"
    CLOCK1B = {"X": ["tick", X]}  # 1.1.2 X1  # 2nd of 2 'CLOCK =' of CspBook·Pdf

    # CLOCK = CLOCK1B  # FIXME: make this mean:  last CLOCK is CLOCK1B

    #
    # Cyclic Flows on an Alphabet of a Few Events
    #

    CLOCK2 = {"X": ["tick", "tock", "boom", X]}  # CLOCK2 missing from CspBook·Pdf

    VMS1A: list | str
    VMS1A = "VMS1A"
    VMS1A = ["coin", "choc", VMS1A]  # 1st of 2 'VMS =' of CspBook·Pdf

    VMS1B = {"X": ["coin", "choc", X]}  # 1.1.2 X2  # 2nd of 2 'VMS =' of CspBook·Pdf

    # VMS = VMS1B  # FIXME: make this mean:  last VMS is VMS1B

    CH5A = ["in5p", "out2p", "out1p", "out2p", "CH5A"]  # 1.1.2 X3
    CH5B = ["in5p", "out1p", "out1p", "out1p", "out2p", "CH5B"]  # 1.1.2 X4

    #
    # Acyclic Choices and Cyclic Choices
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
    VMC = {  # 1.1.3 X4
        "in2p": {"large": VMC, "small": ["out1p", VMC]},
        "in1p": {"small": VMC, "in1p": {"large": VMC, "in1p": STOP}},  # acyclic
    }

    VMC2: dict | str  # VMC2 missing from CspBook
    VMC2 = "VMC2"
    VMC2 = {  # 1.1.3 X4
        "in2p": {"large": VMC2, "small": ["out1p", VMC2]},
        "in1p": {"small": VMC2, "in1p": {"large": VMC2, "small": ["out1p", VMC2]}},  # cyclic
    }

    # todo: lean deeper into Don't-Repeat-Yourself
    # todo: [{"large": [], "small": ["out1p"]}, VMC2]  # No-Op & Single-Event Processes?
    # todo: (Y): {"large": Y, "small": ["out1p", Y]}  # Function on Process Y?

    VMCRED = {"X": {"coin": ["choc", X], "choc": ["coin", X]}}  # 1.1.3 X5  # cyclic
    VMS2 = ["coin", {"X": {"coin": ["choc", X], "choc": ["coin", X]}}]  # 1.1.3 X6  # acyclic
    # 'VMS2 =' is explicit in CspBook·Pdf, distinct from 'VMS ='

    COPYBIT = {"X": {"in_0": ["out_0", X], "in_1": ["out_1", X]}}  # 1.1.3 X7

    #
    # Mutually Recursive Processes
    #

    OO1 = "OO"  # Flake8 E741 Ambiguous Variable Name rejects 'O ='
    LL1 = "LL"  # CspBook·Pdf speaks of 'DD =', 'O =', 'L ='

    DD = {"setorange": OO1, "setlemon": LL1}  # 1.1.4 X1
    OO = {"orange": OO1, "setorange": OO1, "setlemon": LL1}
    LL = {"lemon": LL1, "setlemon": LL1, "setorange": OO1}

    # CspBook·Pdf says = O L O and = L O L, where we say = O O L and = L L O for clarity


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


#
# Run well from the Sh Command Line
#


def main() -> None:
    """Run well from the Sh Command Line"""

    parse_csp_py_args_else()  # often prints help & exits

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


def parse_csp_py_args_else() -> None:
    """Take Words in from the Sh Command Line"""

    doc = __main__.__doc__
    assert doc, (doc,)

    parser = doc_to_parser(doc, add_help=True, epilog_at="examples:")

    yolo_help = "do what's popular now"
    parser.add_argument("--yolo", action="count", help=yolo_help)

    parse_args_else(parser)


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


def parse_args_else(parser: argparse.ArgumentParser) -> None:
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

    parser.parse_args(shargs)

    # often prints help & exits


#
# Form a Process from a Dict or List, like after loading one of those from a Json File
#


CODE_SCOPE: dict[str, object]
CODE_SCOPE = dict()


class Process:  # List [] of zero Items
    """List the Def's of every Process"""

    def __bool__(self) -> bool:
        """Say a Process with no Menu Choices is Falsey"""

        return False

    def abs_process(self) -> "Process":
        """Default to say a Process is itself, aliasing no one"""

        return self

    def menu_choices(self) -> list[str]:
        """Offer no Menu Choices, like a Stop Process"""

        return list()

    def after_process_of(self, choice: str) -> "Process":
        """Take no Menu Choices"""

        raise NotImplementedError("after_process_of")

    # works like the StopProcessMention, till overriden
    # except its __str__ is the default object.__str__, doesn't say "STOP"

    # todo: toggle off '==' equality, to test clients only take 'is' equality


def to_process_if(o: Process | dict | list | str | typing.Callable) -> Process:
    """Return a Process unchanged, else a Process in place of Dict | List | Str"""

    g = CODE_SCOPE

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

    # Form a Stop or a Flow from a List

    if isinstance(o, list):
        if not o:
            o = StopProcessMention
            return o

        assert len(o) >= 2, (len(o), o)

        flow = Flow(cells=o)
        return flow

    # Find a Process in the Compile-Time Scope by Name now

    assert isinstance(o, str), (type(o), o)

    if o in g.keys():
        process = g[o]
        assert isinstance(process, Process), (process,)

        nym = Mention(o, value=process)
        return nym

    # Else find the Process in the Run-Time Scope by Name later

    nym = Mention(o, value=StopProcess)
    return nym


class Flow(Process):

    guard: str
    after: Process

    def __init__(self, cells: list[Process | dict | list | str]) -> None:

        assert len(cells) >= 2, (len(cells), cells)

        after = to_process_if(cells[-1])

        for index in reversed(range(1, len(cells) - 1)):
            guard = cells[index]
            assert isinstance(guard, str), (type(guard), guard, cells)

            pair: list[Process | dict | list | str]  # MyPy needs | dict | list | mentioned
            pair = [guard, after]

            after = Flow(pair)

        guard = cells[0]
        assert isinstance(guard, str), (type(guard), guard, cells)

        self.guard = guard
        self.after = after

    def __bool__(self) -> bool:
        """Say every Flow Process is Truthy, for it offers 1 Menu Choice"""

        return True

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


class Choice(Process):

    by_choice: dict[str, Process]

    def __init__(self, d: dict[str, Process | dict | list | str]) -> None:

        assert len(d.keys()) >= 2, (d.keys(),)

        by_choice = dict()
        for k, v in d.items():
            assert isinstance(k, str), (k,)

            choice = k
            after = to_process_if(v)

            by_choice[choice] = after

        self.by_choice = by_choice

    def __bool__(self) -> bool:
        """Say every Choice Process is Truthy, for it offers 1 Menu Choice"""

        return True

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


class Box(Process):  # not part of .json()  # close to a List of 1 Item
    """Run a Process inside another Process"""

    value: Process

    def __init__(self, value: Process | dict | list | str) -> None:
        super().__init__()

        self.value = to_process_if(value)

    def __bool__(self) -> bool:
        """Choose Truthy or Falsey by the Value"""

        value = self.value
        b = value.__bool__()
        return b

    def abs_process(self) -> "Process":
        """Uncloak the Value"""

        value = self.value
        p = value.abs_process()

        return p

    def menu_choices(self) -> list[str]:
        """Offer the Menu Choices of the Value"""

        value = self.value
        choices = value.menu_choices()
        return choices

    def after_process_of(self, choice: str) -> "Process":
        """Forward a Menu Choice into the Value"""

        value = self.value
        p = value.after_process_of(choice)
        return p


class Mention(Box):  # Str "X"
    """Run a Process with a Name, but without an awareness of its own Name"""

    key: str

    def __init__(self, key: str, value: Process | dict | list | str) -> None:
        super().__init__(value)

        assert key, (key,)
        self.key = key

    # def __repr__(self) -> str:  # todo: Repr's for Process'es
    #     key = self.key
    #     value = self.value
    #     s = f"Mention({key!r}, {repr(value)}) at 0x{id(self):X}"
    #     return s

    def __str__(self) -> str:
        key = self.key
        s = key
        return s


class Cloak(Mention):  # Dict {"X": ["tick", X]}
    """Run a Process with a Name, and an awareness of its own Name"""

    def __init__(self, key: str, value: Process | dict | list | str) -> None:
        super().__init__(key, value=value)

        eq_push(key, value=self)
        self.value = to_process_if(value)  # replaces
        eq_pop(key, value=self)

    def __str__(self) -> str:
        """Speak of μ X • [... X ... X ...]"""

        key = self.key
        value = self.value
        s = f"μ {key} • {value}"  # 'μ X • ["tick", X]'
        return s


class Hope(Process):  # Callable
    """Run a Process formed later"""

    func: typing.Callable
    process: Process | None

    def __init__(self, func: typing.Callable) -> None:
        super().__init__()

        self.func = func
        self.process = None

        # print(func.__name__, repr(self))
        assert func.__name__ not in hope_by_name.keys(), (func.__name__,)
        hope_by_name[func.__name__] = self

    def __str__(self) -> str:
        """Speak of X marks the spot"""

        func = self.func
        s = func.__name__
        return s

    def __bool__(self) -> bool:
        """Choose Truthy or Falsey by the Value"""

        func = self.func

        p = self.process if self.process else to_process_if(func())
        self.process = p

        b = p.__bool__()
        return b

    def abs_process(self) -> "Process":
        """Uncloak the Value"""

        func = self.func

        p = self.process if self.process else to_process_if(func())
        self.process = p

        q = p.abs_process()
        return q

    def menu_choices(self) -> list[str]:
        """Offer the Menu Choices of the Value"""

        func = self.func

        p = self.process if self.process else to_process_if(func())
        self.process = p

        choices = p.menu_choices()
        return choices

    def after_process_of(self, choice: str) -> "Process":
        """Forward a Menu Choice into the Value"""

        func = self.func

        p = self.process if self.process else to_process_if(func())
        self.process = p

        q = p.after_process_of(choice)
        return q


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
# Run some Self-Test's, and then emulate:  python3 -i csp.py
#


def main_try() -> None:
    """Run some Self-Test's, and then emulate:  python3 -i csp.py"""

    code_scope = CODE_SCOPE

    # Compile each Example Process,
    # from (Dict | List | Str), to a Process Variable with the same Name

    from_scope = dict(vars(CspBookExamples))
    from_scope = dict(_ for _ in from_scope.items() if _[0].upper() == _[0])

    del from_scope["OO1"]
    del from_scope["LL1"]

    if False:  # tests just a few cases, when commented in
        from_scope = dict(
            STOP=from_scope["STOP"],
            # U1=from_scope["U1"],
            U111X1=from_scope["U111X1"],
        )

    csp_texts = scope_compile_processes(code_scope, from_scope=from_scope)

    code_scope["CT"] = ct

    for csp_text in csp_texts:
        cp = Parser(csp_text)
        ok = cp.take_input()
        assert ok, (csp_text, cp.takes)

        assert len(cp.takes) == 1, (len(cp.takes), cp.takes)
        assert len(cp.takes[-1]) == 1, (len(cp.takes[-1]), cp.takes[-1])

    # Sketch the infinity of Processes defined by 'def CT'

    print()
    print("CT(n) =", code_scope["CT"])

    limit = 5
    afters = process_to_afters(ct(0), limit=limit)

    print("\n".join(", ".join(_) for _ in afters))
    print(f"# quit tracing infinite depth, after {limit} Processes #")

    assert code_scope["CT"] is ct, (code_scope["CT"], ct)

    print()
    print("CT(4) =", ct(4))
    print("# (not tracing CT(4)) #")

    # Run one Interactive Console, till exit, much as if:  python3 -i csp.py

    code_scope["add"] = process_add
    code_scope["csp"] = __main__  # else unimported by default
    code_scope["dir"] = lambda *args, **kwargs: scope_unsorted_dir(code_scope, *args, **kwargs)
    code_scope["step"] = process_step

    print()
    print(">>> dir()")
    print(repr(list(code_scope.keys())))

    code.interact(banner="", local=code_scope, exitmsg="")  # not 'locals='

    print("bye")

    # 'code.interact' adds '__builtins__' into the Scope


def scope_unsorted_dir(scope, *args, **kwargs) -> list[str]:
    """List the Names in Scope, else in Args"""

    if args:
        names = __builtins__.dir(*args, **kwargs)
        return names

    names = list(scope.keys())
    if "__builtins__" in names:
        names.remove("__builtins__")

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

    for k, v in f.items():
        p = t[k]
        assert p.value is StopProcess, (p.value,)

        q = to_process_if(v)
        assert q is not StopProcess, (q,)  # FIXME: but it should be, at U1 = STOP

        p.value = q

    # Print each Process

    csp_texts = list()
    for k in f.keys():
        p = t[k]
        s = str(p.value)

        csp_text = f"{k} = {s}"
        csp_texts.append(csp_text)

        print()
        print(csp_text)

        # Skip our simplest Infinite Loops

        pv = p.value
        assert pv is not p, (pv, p, k)
        if isinstance(pv, Mention):
            assert pv.value is not pv, (pv.value, pv, k)

            if pv.value is p:
                print("# infinite loop #")
                continue

        assert k != "X", (k,)

        # Print each Flow through the Process

        afters = process_to_afters(p)
        print("\n".join(", ".join(_) for _ in afters))

    return csp_texts


#
# Spell out the Event Traces of each Example Process, and its Name
# CspBook·Pdf doesn't discuss this, doesn't upvote its breadth-first bias
#


empty_list: list
empty_list = list()


def process_to_afters(p: Process, limit=None, *, after: list[str] = empty_list) -> list[list[str]]:
    """Walk the Traces of a Process"""

    q = p.abs_process()
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
            s_after = q_after + [choice]

            r = q.after_process_of(choice)
            s = r.abs_process()

            # Stop work after looping to reach the first compiled process

            if s is q1:
                afters.append(s_after + [top])
                continue

            # Don't revisit the already visited

            if s in processes:
                afters.append(s_after + [etc])
                continue

            if s.menu_choices():
                processes.append(s)  # todo: track max Processes compiled

                if limit is not None:
                    if len(processes) > limit:
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

    q = p.abs_process()

    print("#", q)
    print()

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
        s = r.abs_process()

        q = s  # replaces

        # CUU_Y = "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
        # ED_P = "\x1B" "[" "{}J"  # CSI 04/10 Erase in Display  # 0 Tail


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

    # Run ahead with the first whole match

    if strip in choices:
        choice = strip
        return choice

    # Else erase the input and run ahead with a random Choice

    choice = random.choice(choices)
    print("\x1B[A", end="")
    print(choice)
    return choice


#
# Parse Lines of CSP Input, by way of this Grammar =>
#
#   Input = Assignment End
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


def process_add(csp_text: str) -> None:  # FIXME: return the compiled process
    """Compile and run 1 Csp Instruction"""

    g = CODE_SCOPE

    cp = Parser(csp_text)
    ok = cp.take_input()
    if not ok:
        print("nope")
        return

    assert len(cp.takes) == 1, (len(cp.takes), cp.takes)
    assert len(cp.takes[-1]) == 1, (len(cp.takes[-1]), cp.takes[-1])

    input_ = cp.takes[-1][-1]
    assert isinstance(input_, list), (type(input_), input_)
    assert len(input_) == 2, (len(input_), input_)

    (name, process) = input_
    p = to_process_if(process)
    g[name] = p

    process_to_afters(p)

    # afters = process_to_afters(p)
    # print("\n".join(", ".join(_) for _ in afters))


class Parser:

    text: str  # the Source Chars to consume
    index: int  # the Count of Source Chars consumed

    starts: list[int]  # the index'es to backtrack to
    takes: list[dict | list | str]  # the parsed Input

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
    # Take a whole Input
    #

    def take_input(self) -> bool:
        """Input = Assignment End"""

        self.open_take()
        ok = self.take_assignment() and self.take_end()
        ok = self.close_take(ok)

        return ok

    def take_assignment(self) -> bool:
        """Assignment = Named "=" Process"""

        self.open_take()
        ok = self.take_named() and self.take_mark("=") and self.take_process()
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
            assert keys == events, (keys, events)

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

        # todo: I once wrote 'todo: say this better'. Ugh. Better than what??


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: Retire bin/csp6.py
# todo: Code for showing Cyclicity, showing Acyclity, giving up after a limit?
# todo: Command-Line Input History


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/csp.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
