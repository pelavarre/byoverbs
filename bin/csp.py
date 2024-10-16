#!/usr/bin/env python3

r"""
usage: import csp

work with Communicating Sequential Processes (CSP)

docs:
  https://en.wikipedia.org/wiki/Communicating_sequential_processes
  http://www.usingcsp.com/cspbook.pdf (4/Dec/2022)

grammar:

  Instruction = ( Assignment | ClosedProcess | Name ) End
  Assignment = Name "=" ( MarkedProcess | Alphabet | Name )
  Process = MarkedProcess | Name
  MarkedProcess = RecursiveProcess | ChoiceProcess | GuardedProcess | ClosedProcess
  RecursiveProcess = "μ" Name [ ":" Alphabet ] "•" Process
  ChoiceProcess = GuardedProcess "|" GuardedProcess { "|" GuardedProcess }
  GuardedProcess = "(" OpenGuardedProcess ")" | OpenGuardedProcess
  OpenGuardedProcess = Event "→" { Event "→" } Process
  ClosedProcess = "(" MarkedProcess | Name ")"
  Alphabet = "{" Event { "," Event } "}"
  Event = Name

examples:

  U1 = (coin → STOP)
  U2 = (coin → (choc → (coin → (choc → STOP))))
  CTR = (right → up → right → right → STOP)
  CLOCK_0 = (tick → CLOCK_0)
  CLOCK = μ X:{tick} • (tick → X)
  VMS = (coin → choc → VMS)
  CH5A = (in5p → out2p → out1p → out2p → CH5A)
  CH5B = (in5p → out1p → out1p → out1p → out2p → CH5B)
  U3 = (up → STOP | right → right → up → STOP)
  CH5C = in5p → (out1p → out1p → out1p → out2p → CH5C | out2p → out1p → out2p → CH5C)
  VMCT = μ X • coin → choc → X | toffee → X
  VMC = (in2p → (large → VMC | small → out1p → VMC)
    | in1p → (small → VMC | in1p → (large → VMC | in1p → STOP)))
  VMCRED = μ X • (coin → choc → X | choc → coin → X)
  VMS2 = (coin → μ X • (coin → choc → X | choc → coin → X))
  COPYBIT = μ X • (in_0 → out_0 → X | in_1 → out_1 → X)
  DD = (setorange → DD_O | setlemon → DD_L)
  DD_O = (orange → DD_O | setlemon → DD_L | setorange → DD_O)
  DD_L = (lemon → DD_L | setorange → DD_O | setlemon → DD_L)

"""

# code reviewed by People, Black, Flake8, & MyPy


import code
import collections
import dataclasses
import json
import random
import re
import string
import sys

# import typing


@dataclasses.dataclass(order=True)  # , frozen=True)  # todo: why not frozen
class Any:
    """A thing that can be"""

    doc: str | None

    def __str__(self) -> str:
        doc = self.doc
        str_doc = str(doc)  # 'None'  # 'alef'
        return str_doc


#
# 1.1 Introduction
#


A: set  # [implied much later in the text, like in the digression past X7 of 1.1.3 Choice]
B: set


@dataclasses.dataclass(order=True, frozen=True)
class Event:  # todo: why not a Subclass of a Frozen Any ?
    """A thing that happens, especially one of importance"""

    doc: str

    def __repr__(self) -> str:
        doc = self.doc
        assert doc
        return doc

    # we don't ask 'whether one event occurs simultaneously with another'


NO_EVENTS: list[Event]
NO_EVENTS = list()


coin = Event("coin")  # the insertion of a coin in the slot of a vending machine
choc = Event("choc")  # the extraction of a chocolate from the dispenser of the machine

in1p = Event("in1p")  # the insertion of one penny
in2p = Event("in2p")  # the insertion of a two penny coin
small = Event("small")  # the extraction of a small biscuit or cookie
large = Event("large")  # the extraction of a large biscuit or cookie
out1p = Event("out1p")  # the extraction of one penny in change

x: Event
y: Event
z: Event


@dataclasses.dataclass(order=True)  # , frozen=True)  # todo: why not frozen
class Process(Any):
    """A pattern of behaviour"""

    def __call__(self) -> None:
        process_walk(self)

    def menu_choices(self) -> list[Event]:

        no_events: list[Event]
        no_events = list()

        return no_events

    def form_event_process(self, event: Event) -> "Process":

        raise NotImplementedError(event)


VMS_0 = Process("VMS_0")  # the simple vending machine
# todo: cope with reassignments, to allow 'VMS =' both as an early example and also later

VMC_0 = Process("VMC_0")  # the complex vending machine
# todo: cope with reassignments, to allow 'VMC =' both as an early example and also later

P: Process  # an arbitrary process
Q: Process
R: Process

STOP = Process("STOP")  # a process that takes no more events

X: Process  # an alias of a process
Y: Process


@dataclasses.dataclass(order=True)  # , frozen=True)  # todo: why not frozen
class Alphabet(Any):
    events: list[Event]  # zero or more Events

    def __init__(self, events: list[Event] = NO_EVENTS, doc: str | None = None) -> None:
        super().__init__(doc)

        self.events = list(events)  # 'copied better than aliased'

    def __str__(self) -> str:
        rep = "{" + ", ".join(str(_) for _ in self.events) + "}"
        return rep


αVMS = Alphabet([coin, choc])
αVMC = Alphabet([in1p, in2p, small, large, out1p])

STOPαVMS = STOP  # todo: associate with αVMS
STOPαVMC = STOP  # todo: associate with αVMC


#
# FIXME: Think up how to code Dynamic Scope
#


PROCESSES_BY_VNAME: dict[str, list[Process]]
PROCESSES_BY_VNAME = collections.defaultdict(list)


def vname_push(vname, process) -> None:
    PROCESSES_BY_VNAME[vname].append(process)


def vname_peek(vname) -> Process:

    m = re.match(r"^CTN[(]([0-9]+)[)]$", string=vname)  # FIXME: ugly, brittle, adequate for now
    if m:
        n = int(m.group(1))
        print(f"Forming CTN({n})")
        return CTN(n)

    processes = PROCESSES_BY_VNAME[vname]
    assert processes, (vname, processes)
    process = processes[-1]

    return process


def vname_pop(vname, process) -> None:
    peek = vname_peek(vname)
    assert peek is process, (peek, process)
    PROCESSES_BY_VNAME[vname].pop()


# 1.1.1 Prefix


@dataclasses.dataclass(order=True)  # , frozen=True)  # todo: why not frozen
class GuardedProcess(Process):
    """Block till Event x, then run through Process P"""

    # α(x → P) = αP when x ∈ αP

    start: str
    events: list[Event | str] | Event  # a sequence of Events, or one Event
    then: str
    process: Process | str
    end: str

    def __init__(  # ) -> None:
        self,
        start: str,
        events: list[Event | str] | Event,
        then: str,
        process: Process | str,  # an actual Process, or the name of a Process
        end: str,
        doc: str | None = None,
    ) -> None:
        super().__init__(doc)

        assert events, (events,)  # not an Empty List

        self.start = start
        self.events = events
        self.then = then
        self.process = process
        self.end = end

        guards = self.guards()
        assert len(guards) >= 1, (len(guards), guards)

    def __str__(self) -> str:

        rep = ""

        rep += self.start
        if isinstance(self.events, Event):
            event = self.events
            rep += str(event)
        else:
            rep += "".join(str(_) for _ in self.events)
        rep += self.then
        rep += str(self.process)
        rep += self.end

        return rep

    def guards(self) -> list[Event]:
        """List the Guarding Events of the Process, from first to last"""

        if isinstance(self.events, Event):
            event = self.events
            guards = [event]
        else:
            guards = list(_ for _ in self.events if isinstance(_, Event))

        return guards

    def menu_choices(self) -> list[Event]:
        """Form a List of the one Event which is the first Guard of the Process"""

        event = self.only_menu_choice()
        events = [event]

        return events

    def only_menu_choice(self) -> Event:
        """Say which Event is the first Guard of the Process"""

        guards = self.guards()
        only_menu_choice = guards[0]

        return only_menu_choice

    def form_event_process(self, event: Event) -> "Process":

        only_menu_choice = self.only_menu_choice()
        assert event == only_menu_choice, (event, only_menu_choice)

        #

        guards = self.guards()
        if len(guards) == 1:

            proc = self.process
            if not isinstance(proc, Process):
                vname = self.process
                proc = vname_peek(vname)

            return proc

        #

        events = self.events
        assert isinstance(events, list), (type(events), events)

        less_events = list(events)

        assert less_events[0] == only_menu_choice, (less_events[0], only_menu_choice)
        less_events.pop(0)

        assert isinstance(less_events[0], str), (type(less_events[0]), less_events[0])
        less_events.pop(0)

        proc = GuardedProcess(self.start, less_events, self.then, self.process, self.end)

        return proc


# we say (x → (y → STOP)), we don't say (x → y)'

# x = coin
# y = choc
# _ = GuardedProcess("(", x, " → ", y, ")")  # mypy nope, 'y' is not Process | str

# todo: test this nope more often


# we say (x → P), we say (x → Q), and we don't say (P → Q)'

# P = VMS
# Q = VMC
# _ = GuardedProcess("(", P, " → ", Q, ")")  # mypy nope, 'P' is not list[Event | str] | Event

# todo: test this nope more often


# X1
# (coin → STOPαVMS)
U1 = GuardedProcess("(", coin, " → ", STOPαVMS, ")")


# X2
# (coin → (choc → (coin → (choc → STOPαVMS))))
U2 = GuardedProcess(
    "(",
    coin,
    " → ",
    GuardedProcess(
        "(",
        choc,
        " → ",
        GuardedProcess("(", coin, " → ", GuardedProcess("(", choc, " → ", STOPαVMS, ")"), ")"),
        ")",
    ),
    ")",
)


# X3
# CTR = (right → (up → (right → (right → STOPαCTR))))

up = Event("up")
right = Event("right")

αCTR = Alphabet([up, right])
STOPαCTR = STOP  # todo: associate with αCTR

CTR = GuardedProcess("(", [right, " → ", up, " → ", right, " → ", right], " → ", STOPαCTR, ")")


#
# 1.1.2 Recursion
#


# CLOCK = (tick → CLOCK)  # tick → tick → tick → ...
# (an alt CLOCK = comes later)

tick = Event("tick")
αCLOCK = Alphabet([tick])

CLOCK_0 = GuardedProcess("(", tick, " → ", "CLOCK_0", ")", doc="a perpetual clock")
vname_push("CLOCK_0", process=CLOCK_0)

# todo: cope with reassignments, to allow 'CLOCK =' both as an early example and also later


@dataclasses.dataclass(order=True)  # , frozen=True)  # todo: why not frozen
class RecursiveProcessWithAlphabet(Process):
    """The process X with alphabet A such that X = F(X)"""

    # μ X:A • F(X)

    vmark: str  # 'μ '
    vname: str
    amark: str  # ':'
    alphabet: Alphabet
    pmark: str  # '•'
    process: Process

    def __init__(  # ) -> None:
        self,
        vmark: str,
        vname: str,
        amark: str,
        alphabet: Alphabet,
        pmark: str,
        process: Process,
        doc: str | None = None,
    ) -> None:
        super().__init__(doc)

        self.vmark = vmark
        self.vname = vname
        self.amark = amark
        self.alphabet = alphabet
        self.pmark = pmark
        self.process = process

    def __str__(self) -> str:

        rep = ""

        rep += self.vmark
        rep += self.vname
        rep += self.amark
        rep += str(self.alphabet)
        rep += self.pmark
        rep += str(self.process)

        return rep

    def menu_choices(self) -> list[Event]:
        proc = self.process
        events = proc.menu_choices()
        return events

    def form_event_process(self, event: Event) -> Process:
        proc = self.process

        vname_push(self.vname, process=self)
        event_proc = proc.form_event_process(event)
        # vname_pop(self.vname, process=self)  # todo: make vname_pop's work

        return event_proc


@dataclasses.dataclass(order=True)  # , frozen=True)  # todo: why not frozen
class RecursiveProcess(RecursiveProcessWithAlphabet):
    """The process X such that X = F(X)"""

    # μ X • F(X)

    vmark: str  # 'μ '
    vname: str
    pmark: str  # '•'
    process: Process

    def __init__(  # ) -> None:
        self,
        vmark: str,
        vname: str,
        pmark: str,
        process: Process,
        doc: str | None = None,
    ) -> None:
        super().__init__(
            vmark=vmark,
            vname=vname,
            amark="",
            alphabet=Alphabet(),
            pmark=pmark,
            process=process,
            doc=doc,
        )

    def __str__(self) -> str:

        rep = ""

        rep += self.vmark
        rep += self.vname
        rep += self.pmark
        rep += str(self.process)

        return rep


# X1

CLOCK = RecursiveProcessWithAlphabet(
    "μ ",
    "X",
    ":",
    Alphabet([tick]),
    " • ",
    GuardedProcess("(", tick, " → ", "X", ")", doc="a perpetual clock"),
)


# X2

# a simple vending machine which serves as many chocs as required

# VMS = (coin → (choc → VMS))
# VMS = μ X : {coin, choc} • (coin → (choc → X ))

VMS = GuardedProcess(  # (replaces earlier less complete definition)
    "(",
    [coin, " → ", choc],
    " → ",
    "VMS",
    ")",
    doc="the simple vending machine",
)

vname_push("VMS", process=VMS)


# X3

# CH5A = (in5p → out2p → out1p → out2p → CH5A)

in5p = Event("in5p")  # the insertion of a five penny coin
out2p = Event("out2p")  # the extraction of two pennies in change
αCH5A = Alphabet([in5p, out2p, out1p])

CH5A = GuardedProcess(
    "(",
    [in5p, " → ", out2p, " → ", out1p, " → ", out2p],
    " → ",
    "CH5A",
    ")",
    doc="a machine that gives change for 5p repeatedly",
)

vname_push("CH5A", process=CH5A)


# X4

# CH5B = (in5p → out1p → out1p → out1p → out2p → CH5B)

CH5B = GuardedProcess(
    "(",
    [in5p, " → ", out1p, " → ", out1p, " → ", out1p, " → ", out2p],
    " → ",
    "CH5B",
    ")",
    doc="a different change-giving machine with the same alphabet",
)

vname_push("CH5B", process=CH5B)


#
# 1.1.3 Choice
#


@dataclasses.dataclass(order=True)  # , frozen=True)  # todo: why not frozen
class ChoiceProcess(Process):
    """Event x then P, choice Event y then Q ”"""

    # α(x → P | y → Q) = αP when {x, y} ∈ αP and αP = αQ

    start: str
    choices: list[GuardedProcess | str]  # two or more Guards
    end: str

    def __init__(  # ) -> None:
        self,
        start: str,
        choices: list[GuardedProcess | str],
        end: str,
        doc: str | None = None,
    ) -> None:
        super().__init__(doc)

        self.start = start
        self.choices = choices
        self.end = end

        menu_choices = self.menu_choices()
        assert len(menu_choices) >= 2, (len(menu_choices), menu_choices)

        count_by_guard = collections.Counter(menu_choices)
        for guard, count in count_by_guard.items():
            if count != 1:
                breakpoint()
            assert count == 1, (guard, count)

    def __str__(self) -> str:

        rep = ""
        rep += self.start
        rep += "".join(str(_) for _ in self.choices)
        rep += self.end

        return rep

    def menu_choices(self) -> list[Event]:
        procs = self.menu_procs()
        events = list(_.only_menu_choice() for _ in procs)
        return events

    def menu_procs(self) -> list[GuardedProcess]:
        choices = self.choices
        procs = list(_ for _ in choices if isinstance(_, GuardedProcess))
        return procs

    def form_event_process(self, event: Event) -> Process:

        menu_procs = self.menu_procs()
        menu_choices = self.menu_choices()

        assert event in menu_choices, (event, menu_choices)

        for menu_proc in menu_procs:
            only_menu_choice = menu_proc.only_menu_choice()
            if event == only_menu_choice:
                return menu_proc.form_event_process(event)

        assert False, (event, menu_choices)


# (one example of compilation failure, from the digression past X7 of 1.1.3 Choice)

# we say (x →  P | y → Q | z → R), we don't say (x →  P | (y → Q | z → R))

# toffee = Event("toffee")

# x = coin
# y = choc
# z = toffee

# P = VMS
# Q = VMC
# R = CTR

# _ = ChoiceProcess(
#     "(",
#     [
#         GuardedProcess("(", x, " → ", P, ")"),
#         " | ",
#         ChoiceProcess(
#             "(",
#             [
#                 GuardedProcess("(", y, " → ", Q, ")"),
#                 " | ",
#                 GuardedProcess("(", z, " → ", R, ")"),
#             ],
#             ")",
#         ),
#     ],
#     ")",
# )

# mypy nope, ChoiceProcess of ChoiceProcess is not defined

# todo: test this nope more often


# (my own example of compilation failure)

# toffee = Event("toffee")

# x = coin
# y = choc
# z = toffee

# P = VMS
# Q = VMC

# _ = (
#     ChoiceProcess(
#         "(",
#         [
#             GuardedProcess("(", [x, " → ", y], " → ", P, ")"),
#             " | ",
#             GuardedProcess("(", [x, " → ", z], " → ", Q, ")"),
#         ],
#         ")",
#     ),
# )

# compile-time nope, ChoiceProcess requires a Menu of multiple distinct Choices

# todo: test this nope more often


# X1

# (up → STOP | right → right → up → STOP)

U3 = ChoiceProcess(
    "(",
    [
        GuardedProcess("", up, " → ", STOP, ""),
        " | ",
        GuardedProcess("", [right, " → ", right, " → ", up], " → ", STOP, ""),
    ],
    ")",
)


# X2

# CH5C = in5p → (out1p → out1p → out1p → out2p → CH5C
#               | out2p → out1p → out2p → CH5C)

CH5C = GuardedProcess(
    "",
    in5p,
    " → ",
    ChoiceProcess(
        "(",
        [
            GuardedProcess("", [out1p, " → ", out1p, " → ", out1p, " → ", out2p], " → ", "CH5C", ""),
            " | ",
            GuardedProcess("", [out2p, " → ", out1p, " → ", out2p], " → ", "CH5C", ""),
        ],
        ")",
    ),
    "",
)

vname_push("CH5C", process=CH5C)


# X3

# VMCT = μ X • coin → (choc → X | toffee → X )

toffee = Event("toffee")

VMCT = RecursiveProcess(
    "μ ",
    "X",
    " • ",
    GuardedProcess(
        "",
        coin,
        " → ",
        ChoiceProcess(
            "",
            [
                GuardedProcess("", choc, " → ", "X", ""),
                " | ",
                GuardedProcess("", toffee, " → ", "X", ""),
            ],
            "",
        ),
        "",
    ),
)


# X4

# a more complicated vending machine,
# which offers a choice of coins and a choice of goods and change

# VMC = (in2p → (large → VMC
#       | small → out1p → VMC)
#   | in1p → (small → VMC
#       | in1p → (large → VMC
#           | in1p → STOP )))

# VMC = (
#   in2p → (
#       large → VMC | small → out1p → VMC
#   ) | in1p → (
#       small → VMC
#       | in1p → (large → VMC | in1p → STOP)
#   )
# )

VMC = ChoiceProcess(
    "(",
    [
        GuardedProcess(
            "",
            in2p,
            " → ",
            ChoiceProcess(
                "(",
                [
                    GuardedProcess("", large, " → ", "VMC", ""),
                    " | ",
                    GuardedProcess("", [small, " → ", out1p], " → ", "VMC", ""),
                ],
                ")",
            ),
            "",
        ),
        " | ",
        GuardedProcess(
            "",
            in1p,
            " → ",
            ChoiceProcess(
                "(",
                [
                    GuardedProcess("", small, " → ", "VMC", ""),
                    " | ",
                    GuardedProcess(
                        "",
                        in1p,
                        " → ",
                        ChoiceProcess(
                            "(",
                            [
                                GuardedProcess("", large, " → ", "VMC", ""),
                                " | ",
                                GuardedProcess("", in1p, " → ", STOP, ""),
                            ],
                            ")",
                        ),
                        "",
                    ),
                ],
                ")",
            ),
            "",
        ),
    ],
    ")",
)

vname_push("VMC", process=VMC)


# X5

# VMCRED = μ X • (coin → choc → X | choc → coin → X )

VMCRED = RecursiveProcess(
    "μ ",
    "X",
    " • ",
    ChoiceProcess(
        "(",
        [
            GuardedProcess("", [coin, " → ", choc], " → ", "X", ""),
            " | ",
            GuardedProcess("", [choc, " → ", coin], " → ", "X", ""),
        ],
        ")",
    ),
)


# X6

# VMS2 = (coin → VMCRED)

VMS2 = GuardedProcess("(", coin, " → ", VMCRED, ")")


# X7

in_0 = Event("in_0")  # input of zero on its input channel")  # they choose inpu
in_1 = Event("in_1")  # input of one on its input channel

out_0 = Event("out_0")  # output of zero on its output channel")  # it chooses outpu
out_1 = Event("out_1")  # output of one on its output channel

COPYBIT = RecursiveProcess(  # [exact same structure as VMCRED]
    "μ ",
    "X",
    " • ",
    ChoiceProcess(
        "(",
        [
            GuardedProcess("", [in_0, " → ", out_0], " → ", "X", ""),
            " | ",
            GuardedProcess("", [in_1, " → ", out_1], " → ", "X", ""),
        ],
        ")",
    ),
)


# (x:B → P(x))  # Event x from Alphabet B, then Process P of Event x


# X8

# αRUNA = A
# RUNA = (x:A → RUNA)


# General Choice Notation

# (x :{e} → P(x)) = (e → P(e))  # the special case of Prefixing

# (y :{} → Q(y)) = STOP  # the special case of Stopping

# (a → P | b → Q ) = (x:B → R(x))  # the special case of Choice
# where B = {a,b}
# and R(x) = if x = a then P else Q


#
# 1.1.4 Mutual recursion
#


# X1

# original text speaks of DD, O, and L
# but to speak of 'O =' clashes w Flake8 E741 'ambiguous variable name' ban against 'O ='

setorange = Event("setorange")
setlemon = Event("setlemon")
orange = Event("orange")
lemon = Event("lemon")

αDD = αDD_O = αDD_L = Alphabet([setorange, setlemon, orange, lemon])

DD = ChoiceProcess(
    "(",
    [
        GuardedProcess("", setorange, " → ", "DD_O", ""),
        " | ",
        GuardedProcess("", setlemon, " → ", "DD_L", ""),
    ],
    ")",
)

DD_O = ChoiceProcess(
    "(",
    [
        GuardedProcess("", orange, " → ", "DD_O", ""),
        " | ",
        GuardedProcess("", setlemon, " → ", "DD_L", ""),
        " | ",
        GuardedProcess("", setorange, " → ", "DD_O", ""),
    ],
    ")",
)

DD_L = ChoiceProcess(
    "(",
    [
        GuardedProcess("", lemon, " → ", "DD_L", ""),
        " | ",
        GuardedProcess("", setorange, " → ", "DD_O", ""),
        " | ",
        GuardedProcess("", setlemon, " → ", "DD_L", ""),
    ],
    ")",
)

vname_push("DD_L", process=DD_L)
vname_push("DD_O", process=DD_O)


# X2 Events

around = Event("around")
down = Event("down")


# X2 Process


# todo: teach CTN(n) to detect when walking again into CTN(n)
def CTN(n: int) -> Process:

    if n == 0:
        P = ChoiceProcess(
            "(",
            [
                GuardedProcess("", up, " → ", f"CTN({1})", ""),
                " | ",
                GuardedProcess("", around, " → ", f"CTN({0})", ""),
            ],
            ")",
        )
        return P

    P = ChoiceProcess(
        "(",
        [
            GuardedProcess("", up, " → ", f"CTN({n + 1})", ""),
            " | ",
            GuardedProcess("", down, " → ", f"CTN({n - 1})", ""),
        ],
        ")",
    )

    return P


#
# 1.2 Pictures (nothing here yet)
#


#
# 1.3 Laws (nothing here yet)
#


#
# 1.4 Implementation of processes
#


def process_walk(P: Process) -> None:

    print("#", P)
    print()

    Q = P
    while True:
        if Q is P:
            print()

        events = Q.menu_choices()
        event_strs = list(str(_) for _ in events)

        # bit = True
        while True:
            # bit = not bit

            print(event_strs)
            # if bit:
            #     print(" ", end="")

            sys.stdout.flush()
            line = sys.stdin.readline()

            if not line:
                print("⌃D TTY EOF")
                return

            strip = line.strip()

            if not events:
                print("BLEEP")
                return

            if len(events) == 1:
                event = events[0]
                if strip != str(event):
                    print("\x1B[A", end="")
                    print(event)
                break

            if strip in event_strs:
                event = events[event_strs.index(strip)]
                break

            event = random.choice(events)
            print("\x1B[A", end="")
            print(event)
            break

            # print("\x1B[A" "\x1B[A" "\x1B[J", end="")

        Q = Q.form_event_process(event)

        # CUU_Y = "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
        # ED_P = "\x1B" "[" "{}J"  # CSI 04/10 Erase in Display  # 0 Tail


#
# 1.5 Traces
#

#
# FIXME: Run well from the Sh Command Line
#


def main() -> None:

    assert sys.argv[1:] == ["--yolo"], (sys.argv[1:],)

    #

    globals_dict = globals()
    items = list(globals_dict.items())  # = sorted(globals_dict.items())

    locals_dict = dict((k, v) for (k, v) in items if not (set(k) & set(string.ascii_lowercase)))

    del locals_dict["NO_EVENTS"]
    del locals_dict["PROCESSES_BY_VNAME"]

    #

    print()

    for pname, process in locals_dict.items():
        if isinstance(process, Process):
            if pname in ["VMS_0", "VMC_0", "STOP"]:
                continue
            if pname in ["STOPαVMS", "STOPαVMC", "STOPαCTR"]:
                continue

            print(pname, "=", process)

    print()

    #

    code.interact(banner="", local=locals_dict, exitmsg="")

    print("bye")

    # 'code.interact' adds '__builtins__' into the dir()


#
# todo: React well when called from Pq
#


def csprocess(ilines) -> list[str]:

    dumps = json.dumps(dict(), indent=2)

    olines = dumps.splitlines()
    return olines


#
# Parse CSP Instructions
#


@dataclasses.dataclass(order=True)  # , frozen=True)
class Parser:

    text: str
    index: int
    starts: list[int]
    takes: list[list | str]

    def __init__(self, text) -> None:

        start = 0
        starts = list()
        starts.append(start)

        takes: list[list | str]
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

    def take_end(self) -> bool:
        """FIXME"""

        assert 0 <= self.index <= len(self.text)
        ok = self.index == len(self.text)

        return ok

    def take_instruction(self) -> bool:
        """Instruction = ( Assignment | ClosedProcess | Name ) End"""

        self.open_take("Instruction")
        ok = self.take_assignment() or self.take_closed_process() or self.take_name()
        ok = self.close_take(ok and self.take_end())

        return ok

    def take_assignment(self) -> bool:
        """Assignment = Name "=" ( MarkedProcess | Alphabet | Name )"""

        self.open_take("Assignment")
        ok = self.close_take(
            self.take_name()
            and self.take_mark("=")
            and (self.take_marked_process() or self.take_alphabet() or self.take_name())
        )

        return ok

    def take_process(self) -> bool:
        """Process = MarkedProcess | Name"""

        self.open_take("Process")
        ok = self.close_take(self.take_marked_process() or self.take_name())

        return ok

    def take_marked_process(self) -> bool:
        """MarkedProcess = RecursiveProcess | ChoiceProcess | GuardedProcess | ClosedProcess"""

        self.open_take("MarkedProcess")
        ok = self.close_take(
            self.take_recursive_process()
            or self.take_choice_process()
            or self.take_guarded_process()
            or self.take_closed_process()
        )

        return ok

    def take_recursive_process(self) -> bool:
        """RecursiveProcess = "μ" Name [ ":" Alphabet ] "•" Process"""

        self.open_take("RecursiveProcess")
        ok = self.take_mark("μ") and self.take_name()

        if ok:
            self.open_take("AcceptOneTake")
            self.close_accept_one_take(self.take_mark(":") and self.take_alphabet())

        ok = self.close_take(ok and self.take_mark("•") and self.take_process())

        return ok

    def take_choice_process(self) -> bool:
        """ChoiceProcess = GuardedProcess "|" GuardedProcess { "|" GuardedProcess }"""

        self.open_take("ChoiceProcess")
        ok = self.take_guarded_process() and self.take_mark("|") and self.take_guarded_process()

        self.open_take("AcceptOneTake")
        try_more = ok
        while try_more:
            try_more = self.take_mark("|") and self.take_guarded_process()
            self.close_accept_one_take(try_more)
            self.open_take("AcceptOneTake")
        self.close_accept_one_take(False)

        ok = self.close_take(ok)

        return ok

    def take_guarded_process(self) -> bool:
        """GuardedProcess = "(" OpenGuardedProcess ")" | OpenGuardedProcess"""

        self.open_take("GuardedProcess")
        ok = self.close_take(
            (self.take_mark("(") and self.take_open_guarded_process() and self.take_mark(")"))
            or self.take_open_guarded_process()
        )

        return ok

    def take_open_guarded_process(self) -> bool:
        """OpenGuardedProcess = Event "→" { Event "→" } Process"""

        self.open_take("OpenGuardedProcess")
        ok = self.take_event() and self.take_mark("→")

        self.open_take("AcceptOneTake")
        try_more = ok
        while try_more:
            try_more = self.take_event() and self.take_mark("→")
            self.close_accept_one_take(try_more)
            self.open_take("AcceptOneTake")
        self.close_accept_one_take(False)

        ok = self.close_take(ok and self.take_process())

        return ok

    def take_closed_process(self) -> bool:
        """ClosedProcess = "(" MarkedProcess | Name ")" """

        self.open_take("ClosedProcess")
        ok = self.close_take(
            self.take_mark("(")
            and (self.take_marked_process() or self.take_name())
            and self.take_mark(")")
        )

        return ok

    def take_alphabet(self) -> bool:
        """Alphabet = "{" Event { "," Event } "}" """

        self.open_take("Alphabet")
        ok = self.take_mark("{") and self.take_event()

        self.open_take("AcceptOneTake")
        try_more = ok
        while try_more:
            try_more = self.take_mark(",") and self.take_event()
            self.close_accept_one_take(try_more)
            self.open_take("AcceptOneTake")
        self.close_accept_one_take(False)

        ok = self.close_take(ok and self.take_mark("}"))

        return ok

    def take_event(self) -> bool:
        """Event = Name"""

        self.open_take("Event")
        ok = self.close_take(self.take_name())

        return ok

    #
    #
    #

    def take_name(self) -> bool:
        """FIXME"""

        index = self.index
        takes = self.takes
        text = self.text

        text0 = text[index:]
        m = re.match(r"^[a-zA-Z_][a-zA-Z_0-9]*", string=text0)
        if not m:
            return False

        name = m.group()

        take: list[str]
        take = ["Name", name]

        self.index += len(name)

        deepest_take = takes[-1]
        assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
        deepest_take.append(take)

        return True

    def take_mark(self, mark) -> bool:
        """FIXME"""

        index = self.index
        takes = self.takes
        text = self.text

        text0 = text[index:]

        text1 = text0.lstrip()
        if not text1.startswith(mark):
            return False

        text2 = text1.removeprefix(mark)
        text3 = text2.lstrip()

        len_taken_text = len(text0) - len(text3)
        taken_text = text0[:len_taken_text]

        take: list[str]
        take = [mark, taken_text]

        self.index += len(taken_text)

        deepest_take = takes[-1]
        assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
        deepest_take.append(take)

        return True

    #
    #
    #

    def open_take(self, name) -> None:
        """FIXME"""

        index = self.index
        starts = self.starts
        takes = self.takes

        starts.append(index)

        take = [name]
        takes.append(take)

    def close_take(self, ok) -> bool:
        """FIXME"""

        starts = self.starts
        takes = self.takes

        start = starts.pop()
        take = takes.pop()

        if not ok:
            self.index = start
            return False

        deepest_take = takes[-1]
        assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
        deepest_take.append(take)

        return True

    def close_accept_one_take(self, ok) -> bool:
        """FIXME"""

        starts = self.starts
        takes = self.takes

        start = starts.pop()
        take = takes.pop()
        assert take[0] == "AcceptOneTake", (take[0], take)

        took = ok and (len(take) > 1)

        if not took:
            self.index = start
            return False

        deepest_take = takes[-1]
        assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
        deepest_take.extend(take)

        return True


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/csp.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
