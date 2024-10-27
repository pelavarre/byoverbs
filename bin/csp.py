#!/usr/bin/env python3

r"""
usage: csp.py [-h] [--yolo]

work with Communicating Sequential Processes (CSP)

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
import sys
import textwrap
import traceback
import typing


#
# List examples from CspBook·Pdf, spoken as Dict, List, and Str
#
#   + Step across a List[Str] to reach 1 (Dict | List | Str)
#   + Don't yet give a Csp meaning to a List of 1 Item
#   + Branch across >= 2 Keys of a Dict[Str, Dict | List | Str]
#   + Learn your own Name on the way into a Dict[Str, Dict | List | Str] of 1 Key
#   + Accept a Str as a Name not yet defined
#


class CspBookExamples:

    #
    # Finite Flows
    #

    STOP: list
    STOP = list()

    U1 = ["coin", STOP]  # 1.1.1 X1  # not named by CspBook·Pdf
    U2 = ["coin", ["choc", ["coin", ["choc", STOP]]]]  # 1.1.1 X2  # not named by CspBook·Pdf
    CTR = ["right", "up", "right", "right", STOP]  # # 1.1.1 X3

    #
    # Cyclic Flows on an Alphabet of 1 Event
    #

    CLOCK1: list | str
    CLOCK1 = "CLOCK1"  # CspBook·Pdf takes lazy eval of ClOCK0 for granted
    CLOCK1 = ["tick", CLOCK1]  # 1st of 2 'CLOCK =' of CspBook·Pdf

    CLOCK2: list | str
    CLOCK2 = "CLOCK2"  # CspBook·Pdf doesn't distinguish CLOCK1, CLOCK2, CLOCK3, CLOCK
    CLOCK2 = ["tick", CLOCK2]  # missing from CspBook·Pdf

    X = "X"
    CLOCK = {"X": ["tick", X]}  # 1.1.2 X1  # 2nd of 2 'CLOCK =' of CspBook·Pdf

    #
    # Cyclic Flows on an Alphabet of a Few Events
    #

    CLOCK3 = {"X": ["tick", "tock", "boom", X]}  # missing from CspBook·Pdf

    VMS1: list | str
    VMS1 = "VMS0"
    VMS1 = ["coin", "choc", VMS1]  # 1st of 2 'VMS =' of CspBook·Pdf

    VMS = {"X": ["coin", "choc", X]}  # 1.1.2 X2  # 2nd of 2 'VMS =' of CspBook·Pdf

    CH5A = ["in5p", "out2p", "out1p", "out2p", "CH5A"]  # 1.1.2 X3
    CH5B = ["in5p", "out1p", "out1p", "out1p", "out2p", "CH5B"]  # 1.1.2 X4

    #
    # Acyclic Choices and Cyclic Choices
    #

    U3 = {"up": STOP, "right": ["right", "up", STOP]}  # 1.1.3 X1  # not named by CspBook·Pdf

    CH5C = [  # 1.1.3 X2
        "in5p",
        {
            "out1p": ["out1p", "out1p", "out2p", "CH5C"],
            "out2p": ["out1p", "out2p", "CH5C"],
        },
    ]

    VMCT = {"X": ["coin", {"choc": X, "toffee": X}]}  # 1.1.3 X3

    VMC: dict | str
    VMC = "VMC"
    VMC = {  # 1.1.3 X4
        "in2p": ["large", VMC],
        "small": ["out1p", VMC],
        "in1p": {"small": VMC, "in1p": {"large": VMC, "in1p": STOP}},  # acyclic
    }

    VMCRED = {"X": {"coin": ["choc", X], "choc": ["coin", X]}}  # 1.1.3 X5
    VMS2 = ["coin", {"X": {"coin": ["choc", X], "choc": ["coin", X]}}]  # 1.1.3 X6  # acyclic
    # 'VMS2 =' is explicit in CspBook·Pdf

    COPYBIT = {"X": {"in_0": ["out_0", X], "in_1": ["out_1", X]}}  # 1.1.3 X7

    #
    # Mutually Recursive Process Definition
    #

    DD: dict | str  # CspBook·Pdf speaks of 'DD =', 'O =', 'L ='
    OO: dict | str  # Flake8 E741 Ambiguous Variable Name rejects 'O ='
    LL: dict | str

    DD = "DD"
    OO = "OO"
    LL = "OO"

    DD = {"setorange": OO, "setlemon": LL}  # 1.1.4 X1
    OO = {"setlemon": LL, "orange": OO, "setorange": OO}
    LL = {"setorange": OO, "lemon": LL, "setlemon": LL}

    # CspBook·Pdf says = O L O and = L O L, where we say = O O L and = L L O for clarity


#
# Infinite Sets of Processes Definition
#


STR_CT = """

    {
      0: up → CT(1) | around → CT(0)
      n: up → CT(n + 1) | down → CT(n - 1)
    }

"""


@functools.lru_cache(maxsize=None)
def CT(n: int) -> "Process":
    d = ct_n_to_dict(n)
    p = to_process_if(d)
    return p


def ct_n_to_dict(n: int) -> dict:  # 1.1.4 X2  # Cyclic CT(7) called out by 1.8.3 X5

    p: dict

    if n == 0:
        p = {"up": lambda: CT(1), "around": lambda: CT(0)}

        assert p["up"].__name__ == "<lambda>", p["up"].__name__
        assert p["around"].__name__ == "<lambda>", p["around"].__name__

        p["up"].__name__ = "CT(1)"
        p["around"].__name__ = "CT(0)"

        return p

    p = {"up": lambda: CT(n + 1), "down": lambda: CT(n - 1)}

    assert p["up"].__name__ == "<lambda>", p["up"].__name__
    assert p["down"].__name__ == "<lambda>", p["down"].__name__

    p["up"].__name__ = f"CT({n + 1})"
    p["down"].__name__ = f"CT({n - 1})"

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

    # works lots like the STOP Process, till overriden
    # but its __str__ is the default object.__str__, doesn't say "STOP"

    # todo: toggle off '==' equality, to test clients only take 'is' equality


StopProcess = Process()  # akin to Lisp Nil and Python None  # as if a Flow of no Events


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
        return value

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


class Pseudonym(Box):  # Str "X"
    """Run a Process with a Name, but without an awareness of its own Name"""

    key: str

    def __init__(self, key: str, value: Process | dict | list | str) -> None:
        super().__init__(value)

        assert key, (key,)
        self.key = key

    def __str__(self) -> str:
        """Speak of X marks the spot"""

        key = self.key
        s = key
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


hope_by_name: dict[str, Hope]
hope_by_name = dict()


class Cloak(Pseudonym):  # Dict {"X": ["tick", X]}
    """Run a Process with a Name, and with an awareness of its own Name"""

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


eq_pushes: list[tuple[str, object | None]]
eq_pushes = list()


def eq_push(key: str, value: object) -> None:
    """Define the Key here for awhile"""

    assert key, (key,)
    assert value is not None, (value,)

    g = globals()
    if key not in g.keys():
        v = None
    else:
        v = g[key]
        assert v is not None, (key, v)

    eq_push = (key, v)
    eq_pushes.append(eq_push)

    g[key] = value

    # todo: more robust Scoping, beyond .eq_push/ .eq_pop Shadowing


def eq_pop(key: str, value: object | None) -> None:
    """Stop defining the Key here"""

    g = globals()
    assert key in g.keys(), (key,)
    assert g[key] is value, (g[key], value)

    eq_push = eq_pushes.pop()
    (k, v) = eq_push
    assert k == key, (k, key, value)

    if v is None:
        del g[k]
    else:
        g[k] = v

    # todo: more robust Scoping, beyond .eq_pop/ .eq_push Shadowing


def to_process_if(o: Process | dict | list | str | typing.Callable) -> Process:
    """Return no change, else a Process in place of Dict | List | Str"""

    # Accept a Process as is

    if isinstance(o, Process):
        return o  # todo: 'better copied than aliased' at .to_process_if

    # Accept a Callable to hold for now, to run later

    if callable(o):
        if o.__name__ in hope_by_name.keys():
            hope = hope_by_name[o.__name__]
            return hope

        hope = Hope(o)
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
            o = PseudonymStopProcess
            return o

        assert len(o) >= 2, (len(o), o)

        flow = Flow(cells=o)
        return flow

    # Find a Process in the Compile-Time Scope by Name now

    assert isinstance(o, str), (type(o), o)

    g = globals()
    if o in g.keys():
        process = g[o]
        assert isinstance(process, Process), (process,)

        nym = Pseudonym(o, value=process)
        return nym

    # Else find the Process in the Run-Time Scope by Name later

    nym = Pseudonym(o, value=StopProcess)
    return nym


PseudonymStopProcess = Pseudonym(key="STOP", value=StopProcess)


#
# Run some Self-Test's
#


def main_try() -> None:
    """Run some Self-Test's, and then emulate:  python3 -i csp.py"""

    # Compile each Example Process,
    # from (Dict | List | Str), to a Global Variable with the same Name

    compile_scope = dict(vars(CspBookExamples))
    compile_scope = dict(_ for _ in compile_scope.items() if _[0].upper() == _[0])

    scope_compile_processes(scope=compile_scope)

    # List the compiled Processes

    run_scope = scope_to_alt_scope(scope=globals())

    print()
    print("CT(n) =", run_scope["CT"])
    limit = 5
    afters = process_to_afters(CT(0), limit=limit)
    print("\n".join(", ".join(_) for _ in afters))
    print(f"# quit tracing infinite depth, after {limit} Processes #")

    print()
    print("CT(4) =", run_scope["CT"](4))
    print("# (not tracing CT(4)) #")

    # Run one Interactive Console, till exit, much as if:  python3 -i csp.py

    print()
    print(">>> dir()")
    print(repr(list(run_scope.keys())))

    code.interact(banner="", local=run_scope, exitmsg="")  # not 'locals='

    print("bye")

    # 'code.interact' adds '__builtins__' into the Scope


def scope_to_alt_scope(scope: dict[str, object]):
    """Cut down a Scope of Names to work with"""

    alt_scope = dict(scope)  # 'better copied than aliased'

    items = list(alt_scope.items())
    for k, v in items:
        if k.startswith("_"):
            del alt_scope[k]
        elif k == k.casefold():
            del alt_scope[k]
        elif k.upper() == k:
            pass
        else:
            del alt_scope[k]

    # Compile the infinite CT(n) Processes more lazily and dynamically

    del alt_scope["STR_CT"]
    del alt_scope["CT"]

    class callable_ct_class:
        def __call__(self, n) -> Process:
            return CT(n)

        def __str__(self) -> str:
            s = textwrap.dedent(STR_CT).strip()
            return s

    alt_scope["CT"] = callable_ct_class()

    # Add on:  csp, dir, step

    alt_scope["csp"] = __main__  # else unimported by default
    alt_scope["dir"] = lambda *args, **kwargs: scope_unsorted_dir(alt_scope, *args, **kwargs)
    alt_scope["step"] = process_step

    # Succeed

    return alt_scope


def scope_unsorted_dir(scope, *args, **kwargs) -> list[str]:
    """List the Names in Scope, else in Args"""
    if args:
        names = __builtins__.dir(*args, **kwargs)
        return names
    names = list(scope.keys())
    return names


def scope_compile_processes(scope) -> None:
    """Compile each named (Dict | List | Str) into a Global Process Variable with the same Name"""

    g = globals()

    # Create each Process Pseudonym

    for k, v in scope.items():
        assert isinstance(v, (dict | list | str)), (type(v), v, k)
        assert k not in g.keys(), (k,)
        p = Pseudonym(k, value=StopProcess)
        g[k] = p

    # Compile each Process into its own Pseudonym, in order

    for k, v in scope.items():
        p = g[k]

        q = to_process_if(v)
        p.value = q

    # Print each Process

    for k in scope.keys():
        p = g[k]
        s = str(p.value)

        print()
        print(f"{k} = {s}")

        # Skip our simplest Infinite Loops

        pv = p.value
        assert pv is not p, (pv, p)
        if isinstance(pv, Pseudonym):
            assert pv.value is not pv, (pv.value, pv)

            if pv.value is p:
                print("# infinite loop #")
                continue

        assert k != "X", (k,)

        # Print each Flow through the Process

        afters = process_to_afters(p)
        print("\n".join(", ".join(_) for _ in afters))


#
# Spell out the Afters of each Example Process, and its Name
# CspBook·Pdf doesn't discuss this, doesn't upvote its breadth-first bias
#


def process_to_afters(p: Process, limit=None, *, after: list[str] = list()) -> list[list[str]]:
    """Walk the Traces of a Process"""

    # Choose what work to start with

    pairs: list[tuple[Process | dict | list | str, list[str]]]
    pairs = list()

    p_after = after
    p_pair = (p, p_after)
    pairs.append(p_pair)

    # Choose how to speak of empty and infinite futures

    bleep = "BLEEP"  # todo: Bleep is the Event that is not an Event, but ...
    etc = "..."
    main_loop = "."

    # Work on while work remains

    afters = list()

    r1 = None
    processes = list()
    while pairs:
        (q, q_after) = pairs.pop(0)

        # Compile the Process and snoop out the first compiled Process
        # Stop work after looping to recompile a process already compiled

        r = to_process_if(q)
        r = r.abs_process()

        assert r is not None
        if r1 is None:
            r1 = r

        if r in processes:
            afters.append(q_after + [etc])
            continue

        # Stop work after compiling enough Processes

        choices = r.menu_choices()
        if choices:
            processes.append(r)

            if limit is not None:
                if len(processes) > limit:
                    # print(f"# quit tracing infinite depth, after {limit} Processes #")
                    break

        # Stop work after running out of Choices

        if not choices:
            afters.append(q_after + [bleep])
            continue

        # Visit each Choice in parallel, breadth-first

        for choice in choices:
            s_after = q_after + [choice]
            s = r.after_process_of(choice)
            s = s.abs_process()

            # Stop work after looping to reach the first compiled process

            if s is r1:
                afters.append(s_after + [main_loop])

            # Else work on

            else:
                s_pair = (s, s_after)
                pairs.append(s_pair)

    # Succeed

    return afters


#
# Step and chat through a Trace of a Process
#


def process_step(p: dict | list | str) -> None:
    """Step and chat through a Trace of a Process"""

    # Find the first actual Process, not just its Aliases

    q: Process
    if isinstance(p, Process):
        q = p
    else:
        q = to_process_if(p)
        if not q:
            print("Process Name {!p} has no Def")  # todo: more test of this
            return

    r = q.abs_process()

    r1 = r
    print("#", r1)
    print()

    # Start a new Trace as often as we step back to the same Process

    while True:
        if r is r1:
            print()

        # Offer 0 or more Choices

        choices = r.menu_choices()
        print(choices)

        sys.stdout.flush()
        line = process_step_stdin_readline(choices)
        if not line:
            return

        choice = process_step_choose_and_reprint(choices, line=line)
        assert choice, (choice, line, choices)

        r = r.after_process_of(choice)
        r = r.abs_process()

        # CUU_Y = "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
        # ED_P = "\x1B" "[" "{}J"  # CSI 04/10 Erase in Display  # 0 Tail


def process_step_stdin_readline(choices) -> str:
    """Return "" to quit, else a non-empty Line of Input"""

    # Quit on request

    try:
        line = sys.stdin.readline()
    except KeyboardInterrupt:  # same across sys.platform in ["darwin", "linux"] nowadays
        print(" TTY INT KeyboardInterrupt")  # -> '⌃C TTY INT ...'
        return ""

    if not line:
        print("⌃D TTY EOF")  # as if 'except EOFError' for 'input()'
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
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: Command-Line Input History
# todo: compile lines of Csp Input


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/csp.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
