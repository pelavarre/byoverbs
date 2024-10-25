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
import code
import random
import sys
import textwrap


#
# List examples from CspBook.pdf, spoken as Dict, List, and Str
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

    U1 = ["coin", STOP]  # 1.1.1 X1
    U2 = ["coin", ["choc", ["coin", ["choc", STOP]]]]  # 1.1.1 X2
    CTR = ["right", "up", "right", "right", STOP]  # # 1.1.1 X3

    #
    # Cyclic Flows on an Alphabet of 1 Event
    #

    CLOCK0: list | str
    CLOCK0 = "CLOCK0"
    CLOCK0 = ["tick", CLOCK0]  # first 'CLOCK =' of CspBook Pdf

    CLOCK1: list | str
    CLOCK1 = "CLOCK1"
    CLOCK1 = ["tick", CLOCK1]  # missing from CspBook Pdf

    X = "X"
    CLOCK = {"X": ["tick", X]}  # 1.1.2 X1

    #
    # Cyclic Flows on an Alphabet of a Few Events
    #

    CLOCK3 = {"X": ["tick", "tock", "boom", X]}  # missing from CspBook Pdf

    VMS_0: list | str
    VMS_0 = "VMS_0"
    VMS_0 = ["coin", "choc", VMS_0]  # first 'VMS =' of CspBook Pdf

    VMS = {"X": ["coin", "choc", X]}  # 1.1.2 X2

    CH5A = ["in5p", "out2p", "out1p", "out2p", "CH5A"]  # 1.1.2 X3
    CH5B = ["in5p", "out1p", "out1p", "out1p", "out2p", "CH5B"]  # 1.1.2 X4

    #
    # Acyclic Choices and Cyclic Choices
    #

    U3 = {"up": STOP, "right": ["right", "up", STOP]}  # 1.1.3 X1

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

    COPYBIT = {"X": {"in_0": ["out_0", X], "in_1": ["out_1", X]}}  # 1.1.3 X7

    #
    # Mutually Recursive Process Definition
    #

    DD: dict | str
    OO: dict | str
    LL: dict | str
    DD = "DD"
    OO = "OO"
    LL = "OO"

    DD = {"setorange": OO, "setlemon": LL}  # 1.1.4 X1
    OO = {"setlemon": LL, "orange": OO, "setorange": OO}
    LL = {"setorange": OO, "lemon": LL, "setlemon": LL}

    # 'OO =' & 'LL =' ducks Flake8 E741 Ambiguous Variable Name, but mutates CspBook 'O =' & 'L ='
    # Ending 'X =' with the : "X" Choices untangles the loops, but mutates CspBook O L O, L O L


#
# Infinite Sets of Processes Definition
#


def CT(n: int) -> dict:  # 1.1.4 X2  # Cyclic CT(7) called out by 1.8.3 X5

    print(f"Forming CTN({n})")

    p: dict

    if n == 0:
        p = {"up": lambda: CT(1), "around": lambda: CT(0)}
        return p

    p = {"up": lambda: CT(n + 1), "down": CT(n - 1)}
    return p

    # todo: make 'def CT(n)' work


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


def to_process_if(o: Process | dict | list | str) -> Process:
    """Return no change, else a Process in place of Dict | List | Str"""

    # Accept a Process as is

    if isinstance(o, Process):
        return o  # todo: 'better copied than aliased' at .to_process_if

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
# Run well from the Sh Command Line
#


def main() -> None:
    """Run well from the Sh Command Line"""

    parse_csp_py_args_else()  # often prints help & exits

    main_try()


def parse_csp_py_args_else() -> None:
    """Take Words in from the Sh Command Line"""

    doc = __main__.__doc__
    assert doc, (doc,)

    parser = doc_to_parser(doc, add_help=True, epilog_at="examples:")

    yolo_help = "do what's popular now"
    parser.add_argument("--yolo", action="count", help=yolo_help)

    parse_args_else(parser)


def doc_to_parser(doc: str, add_help: bool, epilog_at: str) -> argparse.ArgumentParser:
    """Form an ArgParse ArgumentParser"""

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
# Run some Self-Test's
#


def main_try() -> None:
    """Run some Self-Test's"""

    # Compile each Example Process,
    # from (Dict | List | Str) to a Global Variable with the same Name

    compile_scope = dict(vars(CspBookExamples))
    compile_scope = dict(_ for _ in compile_scope.items() if _[0].upper() == _[0])

    scope_compile_processes(scope=compile_scope)

    # Run one Interactive Console, till exit

    run_scope = scope_to_next_scope(scope=globals(), casefolds=["csp", "dir", "step"])

    print()
    print(">>> dir()")
    print(repr(list(run_scope.keys())))

    code.interact(banner="", local=run_scope, exitmsg="")  # not 'locals='

    print("bye")

    # 'code.interact' adds '__builtins__' into the Scope


def scope_to_next_scope(scope: dict[str, object], casefolds: list[str]) -> dict[str, object]:
    """Form a Scope of Names to work with"""

    alt_scope = dict(scope)  # 'better copied than aliased'

    assert "csp" not in alt_scope.keys()
    alt_scope["csp"] = __main__  # else unimported by default

    def scope_unsorted_dir(*args, **kwargs) -> list[str]:
        """List the Names in Scope, else in Args"""
        if args:
            names = __builtins__.dir(*args, **kwargs)
            return names
        names = list(alt_scope.keys())
        return names

    assert "dir" not in alt_scope.keys()
    alt_scope["dir"] = scope_unsorted_dir  # __builtins__["dir"]() is sorted :-(

    assert "step" not in alt_scope.keys()
    alt_scope["step"] = process_step

    # Drop the casefolded Names from this Scope, except don't drop our celebrated Casefolds

    items = list(alt_scope.items())
    for k, v in items:
        if k.startswith("_"):
            del alt_scope[k]
        elif k == k.casefold():
            if k not in casefolds:
                del alt_scope[k]
        elif k.upper() == k:
            pass
        else:
            del alt_scope[k]

    # Succeed

    return alt_scope


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

        # Skip simple Indefinite Loops

        pv = p.value
        assert pv is not p, (pv, p)
        if isinstance(pv, Pseudonym):
            assert pv.value is not pv, (pv.value, pv)

            if pv.value is p:
                print("# indefinite loop #")
                continue

        assert k != "X", (k,)

        # Print each Flow through the Process

        afters = process_to_afters(p)
        afters_print(afters)


#
# Print the Afters of each Example Process, and its Name
#


def afters_print(afters: list[list[str]]) -> None:

    alt = dict()
    alt["."] = "."  # not "'.'"
    alt["..."] = "..."  # not "'...'"

    for after in afters:
        join = ", ".join((alt[word] if (word in alt) else word) for word in after)
        print(f"[{join}]")


def process_to_afters(p: Process | dict | list | str, after: list[str] = list()) -> list[list[str]]:
    """Walk the Traces of a Process"""

    afters = list()

    pairs: list[tuple[Process | dict | list | str, list[str]]]
    pairs = list()

    p_after = after
    p_pair = (p, p_after)
    pairs.append(p_pair)

    processes = list()

    main_loop = str(".")
    etc = str("...")
    bleep = str("BLEEP")  # todo: Bleep is the Event that is not an Event, but ...

    r1 = None
    while pairs:
        (q, q_after) = pairs.pop(0)
        # print(f"{q_after=}  # process_to_afters")

        #

        r = to_process_if(q)
        r = r.abs_process()

        assert r is not None
        if r1 is None:
            r1 = r

        if r in processes:
            afters.append(q_after + [etc])
            continue

        #

        choices = r.menu_choices()
        if choices:
            # print("processes.append", repr(r))
            processes.append(r)
            if len(processes) > 25:
                print("Quitting after tracing 25 Processes")
                break

        #

        if not choices:
            afters.append(q_after + [bleep])
            continue

        for choice in choices:
            s_after = q_after + [choice]
            s = r.after_process_of(choice)
            s = s.abs_process()
            if s is r1:
                afters.append(s_after + [main_loop])
            else:
                s_pair = (s, s_after)
                pairs.append(s_pair)

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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/csp.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
