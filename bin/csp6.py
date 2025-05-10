#!/usr/bin/env python3

r"""
usage: import csp

work with Communicating Sequential Processes (CSP)

docs:
  https://en.wikipedia.org/wiki/Communicating_sequential_processes
  http://www.usingcsp.com/cspbook.pdf (4/Dec/2022)

grammar:

  Instruction = ( Assignment | ClosedProcess | Name ) End
  Assignment = Name "=" { Name "=" } ( MarkedProcess | Alphabet | Name )
  Process = MarkedProcess | Name
  MarkedProcess = RecursiveProcess | ChoiceProcess | GuardedProcess | ClosedProcess
  RecursiveProcess = "μ" Name [ ":" Alphabet ] "•" Process
  ChoiceProcess = GuardedProcess "|" GuardedProcess { "|" GuardedProcess }
  GuardedProcess = "(" OpenGuardedProcess ")" | OpenGuardedProcess
  OpenGuardedProcess = Event "→" { Event "→" } Process
  ClosedProcess = "(" MarkedProcess | Name ")"
  Alphabet = EventSet | Name
  EventSet = "{" Event { "," Event } "}"
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
  VMCT = μ X • coin → (choc → X | toffee → X)
  VMC = (in2p → (large → VMC | small → out1p → VMC)
    | in1p → (small → VMC | in1p → (large → VMC | in1p → STOP)))
  VMCRED = μ X • (coin → choc → X | choc → coin → X)
  VMS2 = (coin → μ X • (coin → choc → X | choc → coin → X))
  COPYBIT = μ X • (in_0 → out_0 → X | in_1 → out_1 → X)
  DD = (setorange → DD_O | setlemon → DD_L)
  DD_O = (orange → DD_O | setlemon → DD_L | setorange → DD_O)
  DD_L = (lemon → DD_L | setorange → DD_O | setlemon → DD_L)

  αVMS = {coin, choc}
  αVMC = {in1p, in2p, small, large, out1p}
  αCTR = {up, right}
  αCLOCK = {tick}
  αCH5A = {in5p, out2p, out1p}
  αDD = αDD_O = αDD_L = {setorange, setlemon, orange, lemon}
"""

# code reviewed by People, Black, Flake8, & MyPy


import __main__
import code
import collections
import dataclasses
import functools
import importlib
import json
import random
import re
import string
import sys
import textwrap

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


NO_EVENTS: list[Event | str]
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
        """Step and chat through a Trace of Self, when called"""

        process_step(self)

    def menu_choices(self) -> list[Event]:
        """List the choices for stepping forward with Self"""

        no_events: list[Event]
        no_events = list()

        return no_events

    def form_chosen_process(self, chosen: Event) -> "Process":
        """Form a Process for stepping past a chosen Event"""

        raise NotImplementedError(chosen)

    def print_traces(self) -> None:
        """Print the Traces of Self"""

        p_traces = traces(P=self)
        for p_trace in p_traces:
            print(p_trace)


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
    events: list[Event | str]  # zero or more Events, separated by "," Marks

    def __init__(self, events=NO_EVENTS, doc: str | None = None) -> None:
        super().__init__(doc)

        correcteds: list[Event | str]
        correcteds = list()

        marking = False
        for event_or_str in events:

            if isinstance(event_or_str, Event):
                event = event_or_str
                if marking:
                    correcteds.append(", ")
                correcteds.append(event)
                marking = True

            else:
                assert isinstance(event_or_str, str), (type(event_or_str), event_or_str)
                mark = event_or_str.strip()
                if mark != ",":
                    event_name = event_or_str
                    if marking:
                        correcteds.append(", ")
                    correcteds.append(event_name)
                    marking = True

                else:
                    markplus = event_or_str
                    assert marking, (marking, markplus)
                    correcteds.append(markplus)
                    marking = False

        self.events = correcteds

    def __str__(self) -> str:
        rep = "{" + "".join(str(_) for _ in self.events) + "}"
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
    """Block till Event x, then run through Process P: 'x then P'"""

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

        _ = self.guards()

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
        """Form a List of the Guards of the Process, in order"""

        events = self.events
        if isinstance(events, Event):
            event = events
            guards = [event]
        else:
            guards = list(_ for _ in events if isinstance(_, Event))

        assert guards, (guards,)
        assert len(guards) >= 1, (len(guards), guards)

        return guards

    def menu_choices(self) -> list[Event]:
        """Offer the first Guard as the only Choice"""

        guards = self.guards()
        choice = guards[0]

        choices = [choice]

        return choices

    def form_chosen_process(self, chosen: Event) -> "Process":
        """Find or form a Process for stepping past the only Choice"""

        events = self.events
        choices = self.menu_choices()
        guards = self.guards()

        assert choices == [chosen], (choices, chosen)

        # Step into the Process guarded here, after the last Guard

        if len(guards) == 1:

            proc = self.process
            if not isinstance(proc, Process):
                vname = self.process
                proc = vname_peek(vname)

            return proc

        # Form a new Guarded Process, with the leading chosen Guard removed

        assert isinstance(events, list), (type(events), events)  # not just 1 Event

        less_events = list(events)

        assert less_events[0] == chosen, (less_events[0], chosen)
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


# 1.1.1 X1
# (coin → STOPαVMS)

U1 = GuardedProcess("(", coin, " → ", STOPαVMS, ")")


# 1.1.1 X2
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


# 1.1.1 X3
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

CLOCK_1 = GuardedProcess("(", tick, " → ", "CLOCK_1", ")", doc="a perpetual clock")
vname_push("CLOCK_1", process=CLOCK_1)

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
        """Offer the Choices of the enclosed Process"""

        proc = self.process
        choices = proc.menu_choices()

        return choices

    def form_chosen_process(self, chosen: Event) -> Process:
        """Call on the enclosed Process to step past the chosen Event"""

        proc = self.process

        vname_push(self.vname, process=self)
        event_proc = proc.form_chosen_process(chosen)
        # vname_pop(self.vname, process=self)  # FIXME: make vname_pop's work

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


# 1.1.2 X1

CLOCK = RecursiveProcessWithAlphabet(
    "μ ",
    "X",
    ":",
    Alphabet([tick]),
    " • ",
    GuardedProcess("(", tick, " → ", "X", ")", doc="a perpetual clock"),
)


# 1.1.2 X2

# a simple vending machine which serves as many chocs as required

# VMS = (coin → (choc → VMS))
# todo: cope with reassignments, to allow 'VMS =' both as an early example and also later

VMS_1 = GuardedProcess(
    "(",
    [coin, " → ", choc],
    " → ",
    "VMS_1",
    ")",
    doc="the simple vending machine",
)

vname_push("VMS_1", process=VMS_1)

# VMS = μ X : {coin, choc} • (coin → (choc → X ))    # cyclic

VMS = RecursiveProcessWithAlphabet(
    "μ ",
    "X",
    ":",
    Alphabet([coin, choc]),
    " • ",
    GuardedProcess("(", [coin, " → ", choc], " → ", "X", ")", doc="the simple vending machine"),
)


# 1.1.2 X3

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


# 1.1.2 X4

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

        _ = self.menu_choices()

    def __str__(self) -> str:

        rep = ""
        rep += self.start
        rep += "".join(str(_) for _ in self.choices)
        rep += self.end

        return rep

    def menu_choices(self) -> list[Event]:
        """Offer the first Guard of each Guarded Process as another Choice"""

        choices = list()

        procs = self.menu_procs()
        for proc in procs:
            more_choices = proc.menu_choices()
            assert more_choices, (proc, more_choices)
            assert len(more_choices) == 1, (proc, more_choices)

            choices.extend(more_choices)

        assert len(choices) >= 2, (len(choices), choices)

        count_by_choice = collections.Counter(choices)
        for choice, count in count_by_choice.items():
            assert count == 1, (choice, count)

        return choices

    def menu_procs(self) -> list[GuardedProcess]:
        """Form a List of the Guarded Processes, in order"""

        choices = self.choices
        procs = list(_ for _ in choices if isinstance(_, GuardedProcess))

        return procs

    def form_chosen_process(self, chosen: Event) -> Process:
        """Call on one Guarded Process to step past the chosen Event"""

        menu_choices = self.menu_choices()

        assert chosen in menu_choices, (chosen, menu_choices)

        procs = self.menu_procs()
        for proc in procs:
            more_choices = proc.menu_choices()
            assert more_choices, (proc, more_choices)
            assert len(more_choices) == 1, (proc, more_choices)

            if chosen == more_choices[-1]:
                return proc.form_chosen_process(chosen)

        assert False, (chosen, menu_choices)


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


# 1.1.3 X1

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


# 1.1.3 X2

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


# 1.1.3 X3

# VMCT = μ X • coin → (choc → X | toffee → X )  # cyclic

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
            "(",
            [
                GuardedProcess("", choc, " → ", "X", ""),
                " | ",
                GuardedProcess("", toffee, " → ", "X", ""),
            ],
            ")",
        ),
        "",
    ),
)


# 1.1.3 X4

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


# 1.1.3 X5

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


# 1.1.3 X6

# VMS2 = (coin → VMCRED)

VMS2 = GuardedProcess("(", coin, " → ", VMCRED, ")")


# 1.1.3 X7

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


# 1.1.3 X8

# αRUNA = A
# RUNA = (x:A → RUNA)  # cyclic


# General Choice Notation

# (x :{e} → P(x)) = (e → P(e))  # the special case of Prefixing

# (y :{} → Q(y)) = STOP  # the special case of Stopping

# (a → P | b → Q ) = (x:B → R(x))  # the special case of Choice
# where B = {a,b}
# and R(x) = if x = a then P else Q


#
# 1.1.4 Mutual recursion
#


# 1.1.4 X1

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


# 1.1.4 X2 Events

around = Event("around")
down = Event("down")


# 1.1.4 X2 Process formed by Func  # cyclic, called out in the case of CTN(7) by 1.8.3 X5


@functools.lru_cache(maxsize=None)
def CTN(n: int) -> Process:

    print(f"Forming CTN({n})")

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


def process_step(P: Process) -> None:
    """Step and chat through a Trace of a Process"""

    print("#", P)
    print()

    # Start a new Trace as often as we step back to the same Process

    Q = P
    while True:
        if Q is P:
            print()

        # Offer 0 or more Choices

        choices = Q.menu_choices()
        choice_strs = list(str(_) for _ in choices)

        while True:
            print(choice_strs)

            # Quit on request

            sys.stdout.flush()
            line = sys.stdin.readline()

            if not line:
                print("⌃D TTY EOF")
                return

            strip = line.strip()

            # Quit when there are no Choices for stepping forward

            if not choices:
                print("BLEEP")
                return

            # Run ahead with the only Choice, when there is only one

            if len(choices) == 1:
                chosen = choices[-1]
                if strip != str(chosen):
                    print("\x1b[A", end="")
                    print(chosen)
                break

            # Run ahead with the first whole match

            if strip in choice_strs:
                chosen = choices[choice_strs.index(strip)]
                break

            # Run ahead with a random Choice

            chosen = random.choice(choices)
            print("\x1b[A", end="")
            print(chosen)
            break

        Q = Q.form_chosen_process(chosen)

        # CUU_Y = "\x1B" "[" "{}A"  # CSI 04/01 Cursor Up
        # ED_P = "\x1B" "[" "{}J"  # CSI 04/10 Erase in Display  # 0 Tail


#
# 1.5 Traces
#

#
# 1.6 Operations on Traces
#
# 1.6.1 Catenation
#
# 1.6.2 Restriction
#
# 1.6.3 Head and tail
#
# 1.6.4 Star
#
#   A∗ = { t | t = ⟨⟩ ∨ ( t0 ∈ A ∧ t′ ∈ A∗ ) }
#
# 1.6.5 Ordering
#
# 1.6.6 Length
#

#
# 1.7 Implementation of traces
#

#
# 1.8 Traces of a process
#
# 1.8.1 Laws
#
# 1.8.2 Implementation
#
# 1.8.3 After
#
#   X = (a → (X / ⟨a⟩))  # same as X = X
#
#

#
# 1.9 More operations on traces [skippable]
# 1.9.1 Change of symbol
# 1.9.2 Catenation
# 1.9.3 Interleaving
# 1.9.4 Subscription
# 1.9.5 Reversal
# 1.9.6 Selection
# 1.9.7 Composition
#

#
# 1.10 Specifications
# 1.10.1 Satisfaction
# 1.10.2 Proofs
#


def traces(P: Process, trace: list[Event] = list()) -> list[list[Event]]:
    """Walk the Traces of a Process"""

    traces = list()

    pairs: list[tuple[Process, list[Event]]]
    pairs = list()

    p_trace = trace
    p_pair = (P, p_trace)
    pairs.append(p_pair)

    processes = list()

    main_loop = Event(".")
    etc = Event("...")
    bleep = Event("BLEEP")  # todo: Bleep is the Event that is not an Event, but ...

    while pairs:
        (Q, q_trace) = pairs.pop(0)
        # print(f"{q_trace=}  # traces")

        #

        if Q in processes:
            traces.append(q_trace + [etc])
            continue

        if Q is not STOP:
            processes.append(Q)
            if len(processes) > 25:
                print("Quitting after tracing 25 Processes")
                break

        #

        choices = Q.menu_choices()
        if not choices:
            traces.append(q_trace + [bleep])
            continue

        for chosen in choices:
            r_trace = q_trace + [chosen]
            R = Q.form_chosen_process(chosen)
            if R is P:
                traces.append(r_trace + [main_loop])
            else:
                r_pair = (R, r_trace)
                pairs.append(r_pair)

    return traces


#
# Run well from the Sh Command Line
#


def main() -> None:

    assert sys.argv[1:] == ["--yolo"], (sys.argv[1:],)

    # Run some quick quiet self-test's

    csp_texts = fetch_csp_texts()
    try_parser(csp_texts)
    try_runner(csp_texts)

    # Scrape out a Dict for 'code.interact'

    globals_dict = globals()
    items = list(globals_dict.items())  # = sorted(globals_dict.items())

    locals_dict = dict((k, v) for (k, v) in items if not (set(k) & set(string.ascii_lowercase)))

    del locals_dict["NO_EVENTS"]
    del locals_dict["PROCESSES_BY_VNAME"]

    csp = importlib.import_module("csp")
    assert "csp" not in locals_dict.keys()
    locals_dict["csp"] = csp

    # Print the hand-assembled Process'es and Alphabet's

    print()

    for iname, ivalue in locals_dict.items():
        if isinstance(ivalue, Process):
            if iname in ["VMS_0", "VMC_0", "STOP"]:
                continue
            if iname in ["STOPαVMS", "STOPαVMC", "STOPαCTR"]:
                continue
            print(iname, "=", ivalue)

    print()

    for iname, ivalue in locals_dict.items():
        if isinstance(ivalue, Alphabet):
            print(iname, "=", ivalue)

    print()

    # Run one Interactive Console, till exit

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


def fetch_csp_texts() -> list[str]:

    doc = __main__.__doc__
    assert doc, (doc,)

    tail = doc[doc.index("examples:") :]
    splitlines = tail.splitlines()
    dedent = textwrap.dedent("\n".join(splitlines[1:]))
    strip = dedent.strip()
    ilines = strip.splitlines()

    csp_texts = list()
    for index, iline in enumerate(ilines):
        if not iline.startswith(" "):
            if iline:
                csp_texts.append(iline)
        else:
            assert index >= 1, (index, iline)
            assert ilines[index - 1], (ilines[index - 1], index, iline)
            csp_texts[-1] += "\n" + iline

    return csp_texts


def try_parser(csp_texts) -> None:

    for csp_text in csp_texts:
        p = Parser(csp_text)
        ok = p.take_instruction()
        assert ok, (csp_text,)


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
        """Take the End of the Text"""

        assert 0 <= self.index <= len(self.text)
        ok = self.index == len(self.text)

        return ok

    #
    # Accept one Grammar
    #

    def take_instruction(self) -> bool:
        """Instruction = ( Assignment | ClosedProcess | Name ) End"""

        self.open_take("Instruction")
        ok = self.take_assignment() or self.take_closed_process() or self.take_name()
        ok = self.close_take(ok and self.take_end())

        return ok

    def take_assignment(self) -> bool:
        """Assignment = Name "=" { Name "=" } ( MarkedProcess | Alphabet | Name )"""

        self.open_take("Assignment")

        ok = self.take_name() and self.take_mark("=")

        self.open_take("AcceptOneTake")
        try_more = ok
        while try_more:
            try_more = self.take_name() and self.take_mark("=")
            self.close_accept_one_take(try_more)
            self.open_take("AcceptOneTake")
        self.close_accept_one_take(False)

        ok = self.close_take(self.take_marked_process() or self.take_alphabet() or self.take_name())

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

        # if ok:  # FIXME
        #     breakpoint()
        #     # (Pdb) p self.takes[-1][-1]

        # ['OpenGuardedProcess', ['Event', ['Name', 'coin']], ['→', ' → '], ['Process', ['Name', 'STOP']]]

        #  gg = csp.GuardedProcess("", [csp.coin], " → ", csp.STOP, "")

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
        """Alphabet = EventSet | Name"""

        self.open_take("Alphabet")
        ok = self.close_take(self.take_event_set() or self.take_name())

        return ok

    def take_event_set(self) -> bool:
        """EventSet = "{" Event { "," Event } "}" """

        self.open_take("EventSet")
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
        """Take any one Name"""

        index = self.index
        takes = self.takes
        text = self.text

        # Fail now if Name not found

        text0 = text[index:]  # todo: more than "α" accepted with r"[a-zA-Z_]"
        m = re.match(r"^[a-zA-Z_α][a-zA-Z_0-9]*", string=text0)
        if not m:
            return False

        name = m.group()

        # Take the Name

        take: list[str]
        take = ["Name", name]

        self.index += len(name)

        deepest_take = takes[-1]
        assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
        deepest_take.append(take)

        # Succeed

        return True

    def take_mark(self, mark) -> bool:
        """Take a matching Mark"""

        index = self.index
        takes = self.takes
        text = self.text

        # Capture the Blank Chars before and After the Mark,
        # or fail now because Mark not found

        text0 = text[index:]

        text1 = text0.lstrip()
        if not text1.startswith(mark):
            return False

        text2 = text1.removeprefix(mark)
        text3 = text2.lstrip()

        len_taken_text = len(text0) - len(text3)
        markplus = text0[:len_taken_text]

        # Take the MarkPlus

        take: list[str]
        take = [mark, markplus]

        self.index += len(markplus)

        deepest_take = takes[-1]
        assert isinstance(deepest_take, list), (type(deepest_take), deepest_take)
        deepest_take.append(take)

        # Succeed

        return True

    #
    #
    #

    def open_take(self, name) -> None:
        """Open up a List of Takes"""

        index = self.index
        starts = self.starts
        takes = self.takes

        starts.append(index)

        take = [name]
        takes.append(take)

    def close_take(self, ok) -> bool:
        """Commit and close a List of Takes, else backtrack"""

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
        """Commit and close and merge a List of Takes, else backtrack"""  # todo: say this better

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
        deepest_take.extend(take[1:])

        return True


#
#
#


def try_runner(csp_texts) -> None:

    vm = VirtualMachine()

    for csp_text in csp_texts:
        vm.csp_text_run(csp_text)


@dataclasses.dataclass(order=True)  # , frozen=True)
class VirtualMachine:
    def csp_text_run(self, csp_text) -> None:
        pass


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# FIXME: Print the Source Fragments of a successful Parse

# FIXME: Assemble a successful Parse into a Process, Alphabet, etc

# FIXME: Exhaust the Traces, but then give up on CTR(n)


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/csp6.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
