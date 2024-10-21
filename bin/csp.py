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
# List lots of examples from CspBook.pdf, spoken as Dict, List, and Str
#
#   + Step across List[Str] to reach a (Dict | List | Str)
#   + Branch across 2 Keys or more of Dict[Str, Dict | List | Str] into a (Dict | List | Str)
#   + Learn your own name at a Dict[Str, Dict | List | Str] of 1 Key
#


class CspBookExamples:

    STOP: list  # pacifies MyPy's weird demand for Empty Lists to declare their Datatypes

    STOP = list()

    U1 = ["coin", STOP]  # 1.1.1 X1

    U2 = ["coin", ["choc", ["coin", ["choc", STOP]]]]  # 1.1.1 X2

    CTR = ["right", "up", "right", "right", STOP]  # # 1.1.1 X3

    CLOCK_0 = ["tick", "CLOCK_0"]  # first 'CLOCK =' of CspBook Pdf
    CLOCK_1 = ["tick", "CLOCK_1"]  # missing from CspBook Pdf
    # FIXME: why prints as [tick, tick, ...] with Two Ticks

    X = "X"
    CLOCK = {"X": ["tick", X]}  # 1.1.2 X1

    XCLOCK = {"X": ["tick", "tock", "boom", X]}  # missing from CspBook Pdf

    VMS_0 = ["coin", "choc", "VMS"]  # first 'VMS =' of CspBook Pdf
    VMS = {"X": ["coin", "choc", X]}  # 1.1.2 X2

    CH5A = ["in5p", "out2p", "out1p", "out2p", "CH5A"]  # 1.1.2 X3
    CH5B = ["in5p", "out1p", "out1p", "out1p", "out2p", "CH5B"]  # 1.1.2 X4

    U3 = {"up": STOP, "right": ["right", "up", STOP]}  # 1.1.3 X1

    CH5C = [  # 1.1.3 X2
        "in5p",
        {
            "out1p": ["out1p", "out1p", "out2p", "CH5C"],
            "out2p": ["out1p", "out2p", "CH5C"],
        },
    ]

    VMCT = {"X": ["coin", {"choc": X, "toffee": X}]}  # 1.1.3 X3

    VMC = {  # 1.1.3 X4
        "in2p": ["large", "VMC"],
        "small": ["out1p", "VMC"],
        "in1p": {"small": "VMC", "in1p": {"large": "VMC", "in1p": STOP}},  # acyclic
    }
    # FIXME: why prints as 'in1p, in1p, in1p,' twice

    VMCRED = {"X": {"coin": ["choc", "X"], "choc": ["coin", "X"]}}  # 1.1.3 X5
    VMS2 = ["coin", {"X": {"coin": ["choc", "X"], "choc": ["coin", "X"]}}]  # 1.1.3 X6  # acyclic

    COPYBIT = {"X": {"in_0": ["out_0", "X"], "in_1": ["out_1", "X"]}}  # 1.1.3 X7

    DD = {"setorange": "DD_O", "setlemon": "DD_L"}  # 1.1.4 X1
    DD_O = {"orange": "DD_O", "setlemon": "DD_L", "setorange": "DD_O"}  # in CspBook Pdf as 'O ='
    DD_L = {"lemon": "DD_L", "setorange": "DD_O", "setlemon": "DD_L"}  # in CspBook Pdf as 'L ='
    # Flake8 defaults to reject 'O =' via Flake8 E741 ambiguous variable name 'O'

    @staticmethod
    def CT(n: int) -> dict:  # 1.1.4 X2  # Cyclic CT(7) called out by 1.8.3 X5

        print(f"Forming CTN({n})")

        P: dict

        if n == 0:
            P = {"up": lambda: CT(1), "around": lambda: CT(0)}
            return P

        P = {"up": lambda: CT(n + 1), "down": CT(n - 1)}
        return P

        # todo: make 'def CT' work


CT = CspBookExamples.CT


#
# Form a Process from a Dict or List, like after loading one of those from a Json File
#


class Process:

    process_name: str

    def __init__(self, name="[]") -> None:
        self.process_name = name

    def __str__(self) -> str:
        """Draw Self as a CSP Process"""
        s = self.process_name  # '[]' as the Json Str of the STOP Process
        return s

    def abs_process(self) -> "Process":
        """Search through Aliases and Defs to find the actual Process"""
        return self

    def menu_choices(self) -> list[str]:
        """List the Steps ahead, if any"""
        return list()

    def after_process_of(self, choice: str) -> "Process":
        """Take a particular next Step forward"""
        assert False, (choice, self)

    # works like the STOP Process, unless overriden


cloak_str_recursions = list()


class Cloak(Process):  # FIXME: merge into Base Class Process

    process_else: Process | None

    def __init__(self, name) -> None:
        assert isinstance(name, str), (type(name), name)
        super().__init__(name)
        self.process_else = None

    def __str__(self) -> str:
        process_name = self.process_name
        process_else = self.process_else

        if process_else:
            process = process_else
            if process_name not in cloak_str_recursions:
                cloak_str_recursions.append(process_name)
                s = process.__str__()
                pop = cloak_str_recursions.pop()  # todo: try/ finally
                assert pop == process_name, (pop, process_name)
                return s

        s = super().__str__()
        return s

    def abs_process(self) -> Process:
        if self.process_else:
            process = self.process_else
            P = process.abs_process()
            return P
        P = super().abs_process()
        return P

    def menu_choices(self) -> list[str]:
        if self.process_else:
            process = self.process_else
            choices = process.menu_choices()
            return choices
        choices = super().menu_choices()
        return choices

    def after_process_of(self, choice: str) -> Process:
        if self.process_else:
            process = self.process_else
            P = process.after_process_of(choice)
            return P
        P = super().after_process_of(choice)
        return P


class Flow(Process, list):

    def __init__(self, P: list) -> None:
        Process.__init__(self, "")
        list.__init__(self, P)  # todo: coherent super init's

        assert P, (P,)
        assert len(P) >= 2, (P,)

    def __str__(self) -> str:
        s = " → ".join(str(_) for _ in self)
        s = f"({s})"
        return s

    def abs_process(self) -> Process:
        return self

    def menu_choices(self) -> list[str]:
        assert self, (self,)
        guard = self[0]
        return [guard]

    def after_process_of(self, choice: str) -> Process:
        """Take a particular next Step forward"""

        assert self, (self,)
        guard = self[0]
        assert choice == guard, (choice, guard, self)

        # Step to next Guard

        after_process: Process
        if len(self) >= 3:
            after_process = Flow(self[1:])
            return after_process

        # Step into the Guarded Process

        assert len(self) == 2, (len(self), self)

        V = self[-1]

        if isinstance(V, Process):
            after_process = V
        else:
            after_process = loads_to_process(P=V)

        return after_process


class Choice(Process, dict):

    def __init__(self, P: dict) -> None:
        Process.__init__(self, "")
        dict.__init__(self, P)

        assert P, (P,)
        assert len(P.keys()) >= 2, (P.keys(),)

        items = list(self.items())
        for k, v in items:
            V = to_process(v)
            self[k] = V

    def __str__(self) -> str:
        s = " | ".join(f"{k} → {v}" for k, v in self.items())
        s = f"({s})"
        return s

    def abs_process(self) -> Process:
        return self

    def menu_choices(self) -> list[str]:
        guards = list(self.keys())
        return guards

    def after_process_of(self, choice: str) -> Process:
        """Take a particular next Step forward"""

        assert self, (self,)
        guards = list(self.keys())
        assert len(guards) >= 2, (guards, choice, self)
        assert choice in guards, (choice, guards, self)

        # Step through the Chosen Guard into the Chosen Process

        V = self[choice]

        if isinstance(V, Process):
            after_process = V
        else:
            after_process = loads_to_process(P=V)

        return after_process


def_str_recursions = list()


class Def(Process, dict):

    def __init__(self, P: dict) -> None:
        Process.__init__(self, "")
        dict.__init__(self, P)

        assert P, (P,)
        assert len(P.keys()) == 1, (P.keys(),)

        (k, v) = list(P.items())[-1]

        vv_else = None
        if k in globals().keys():
            vv_else = globals()[k]
            assert vv_else is not None, (vv_else, k)
            del globals()[k]

        globals()[k] = self  # todo: work well with Scopes
        V = to_process(v)

        if vv_else is not None:
            globals()[k] = vv_else

        assert self[k] is v, (self[k], v)
        self[k] = V

    def __str__(self) -> str:
        (k, v) = list(self.items())[-1]

        globals()[k] = self  # todo: work well with Scopes
        V = to_process(v)

        if k in def_str_recursions:
            s = f"{k}"
        else:
            def_str_recursions.append(k)
            s = f"μ {k} • {V}"
            pop = def_str_recursions.pop()  # todo: try/ finally
            assert pop == k, (pop, k)

        return s

    def abs_process(self) -> Process:
        (k, V) = list(self.items())[-1]
        W = to_process(V)
        return W

    def menu_choices(self) -> list[str]:
        (k, v) = list(self.items())[-1]
        assert isinstance(v, Process)
        choices = v.menu_choices()
        return choices

    def after_process_of(self, choice: str) -> Process:
        (v_name, V) = list(self.items())[-1]
        assert isinstance(V, Process)

        # print(f"globals()[{v_name!r}] = {V!r}")
        globals()[v_name] = V  # adds or replaces  # todo: work well with Scopes
        # print(f"setattr({module!r}, {v_name!r}, {V!r})")
        # setattr(module, v_name, V)  # adds or replaces  # todo: work well with Scopes

        after_process = V.after_process_of(choice)
        return after_process


#
# Run well from the Sh Command Line
#


def main() -> None:

    # Early on, take Words in from the Sh Command Line, and give back Help Lines

    assert sys.argv[1:] == ["--yolo"], (sys.argv[1:],)

    # Run one Interactive Console, till exit

    g = globals()
    del g["CT"]

    scope1 = dict(vars(CspBookExamples))
    del scope1["CT"]

    scope2 = scope_to_next_scope(scope1, casefolds=["csp", "dir", "step"])
    scope_compile_processes(scope2, verbose=False)
    scope_print_afters(scope2, verbose=True)

    scope3 = dict(globals())
    scope4 = scope_to_next_scope(scope3, casefolds=["csp", "dir", "step"])

    print()
    print(">>> dir()")
    print(repr(list(scope4.keys())))

    code.interact(banner="", local=scope4, exitmsg="")  # not 'locals='

    print("bye")

    # 'code.interact' adds '__builtins__' into the Scope


def scope_to_next_scope(scope: dict[str, object], casefolds: list[str]) -> dict[str, object]:
    """Form a Scope of Names to work with"""

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
    scope["dir"] = scope_unsorted_dir  # __builtins__["dir"]() is sorted :-(

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
        elif k.upper() == k:
            pass
        else:
            del scope[k]

    # Succeed

    return scope


def scope_compile_processes(scope, verbose) -> None:

    d1_items = list(_ for _ in scope.items() if _[0].upper() == _[0])
    d1_items = list(_ for _ in d1_items if _[0] not in ["CT"])

    g = globals()

    for k, v in d1_items:
        assert isinstance(v, (dict | list | str)), (type(v), v, k)
        assert k not in g.keys(), (k,)
        g[k] = Cloak(k)

    d2 = dict()
    for k, v in d1_items:
        P = to_process(v)
        d2[k] = P

    for k, P in d2.items():
        g[k].process_else = P

    for k, P in d2.items():
        s = str(g[k])
        if verbose:
            print(f"{k} = {s}")


#
# Print the Afters of each Example Process, and its Name
#


def scope_print_afters(scope, verbose) -> None:  # noqa C901 complex

    d1_items = list(_ for _ in scope.items() if _[0].upper() == _[0])
    d1_items = list(_ for _ in d1_items if _[0] not in ["CT"])

    for k, P in d1_items:

        if verbose:
            print()
            print(f"{k} = {P}")

        p_afters = process_to_afters(P)

        alt = dict()
        alt["..."] = "..."  # not "'...'"
        alt["."] = "..."  # not "'.'"

        if verbose:
            for p_after in p_afters:
                join = ", ".join((alt[word] if (word in alt) else word) for word in p_after)
                print(f"[{join}]")


def loads_to_process(P: dict | list | str) -> Process:

    Q: Process

    # Form a Def or Choice from a Dict

    if isinstance(P, dict):
        assert P, (P,)
        if len(P.keys()) == 1:
            Q = Def(P)
            return Q

        Q = Choice(P)
        return Q

    # Form a Flow from a List

    if isinstance(P, list):
        if not P:
            Q = Process()  # acts like the STOP Process
            return Q

        assert len(P) >= 2, (len(P), P)

        Pn = P[-1]
        Qn = to_process(Pn)  # mutually recurses

        Q = Flow(P[:-1] + [Qn])
        return Q

    # Form a Process from a Str

    assert isinstance(P, str), (type(P), P)
    Q = to_process(P)  # mutually recurses

    return Q


to_process_recursions: list[str]
to_process_recursions = list()  # limits recursion


def to_process(P: Process | dict | list | str) -> Process:
    """Return a Process, else form a Process, else find a Process"""

    # Return a Process as a Process

    if isinstance(P, Process):
        return P

    # Form a Process from a Json Dict or Json List

    if isinstance(P, (dict, list)):
        Q = loads_to_process(P)  # mutually recurses
        return Q

    # Return the Process Value of a Str

    assert isinstance(P, str), (type(P), P)

    q_name = P

    if q_name in to_process_recursions:
        print(f"Infinite Recursion:  {q_name} = ... {q_name} ...")
        breakpoint()
        return Process()  # acts like the STOP Process

    if q_name not in globals().keys():
        Q = Cloak(q_name)
        return Q

    Q = globals()[q_name]

    to_process_recursions.append(q_name)
    R = to_process(Q)  # recurses
    pop = to_process_recursions.pop()
    assert pop == q_name, (pop, q_name)  # todo: try/ finally

    assert isinstance(R, (Cloak | Flow | Def | Choice | str)), (type(R), R, P)

    return R


def process_to_afters(P: Process | dict | list | str, after: list[str] = list()) -> list[list[str]]:
    """Walk the Traces of a Process"""

    afters = list()

    pairs: list[tuple[Process | dict | list | str, list[str]]]
    pairs = list()

    p_after = after
    p_pair = (P, p_after)
    pairs.append(p_pair)

    processes = list()

    main_loop = str(".")
    etc = str("...")
    bleep = str("BLEEP")  # todo: Bleep is the Event that is not an Event, but ...

    while pairs:
        (Q, q_after) = pairs.pop(0)
        # print(f"{q_after=}  # afters")

        #

        R = to_process(Q)

        if R in processes:
            afters.append(q_after + [etc])
            continue

        #

        choices = R.menu_choices()

        if choices:
            processes.append(R)
            if len(processes) > 25:
                print("Quitting after tracing 25 Processes")
                break

        #

        if not choices:
            afters.append(q_after + [bleep])
            continue

        for choice in choices:
            s_after = q_after + [choice]
            S = R.after_process_of(choice)
            if S is R:
                afters.append(s_after + [main_loop])
            else:
                s_pair = (S, s_after)
                pairs.append(s_pair)

    return afters


#
# Step and chat through a Trace of a Process
#


def process_step(P: dict | list | str) -> None:
    """Step and chat through a Trace of a Process"""

    # Find the first actual Process, not just its Aliases

    Q: Process
    if isinstance(P, Process):
        Q = P
    else:
        q_else_q_name = loads_to_process(P)
        if isinstance(q_else_q_name, str):
            print("Process Name {!q_name} has no Def")
            return

        Q = q_else_q_name

    R = Q.abs_process()

    R1 = R
    print("#", R1)
    print()

    # Start a new Trace as often as we step back to the same Process

    while True:
        if R is R1:
            print()

        # Offer 0 or more Choices

        choices = R.menu_choices()
        print(choices)

        sys.stdout.flush()
        line = process_step_stdin_readline(choices)
        if not line:
            return

        choice = process_step_choose_and_reprint(choices, line=line)
        assert choice, (choice, line, choices)

        R = R.after_process_of(choice)
        R = R.abs_process()

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
