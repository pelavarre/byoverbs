#!/usr/bin/env python3

r"""
usage: import csp

work with Communicating Sequential Processes (CSP)

docs:
  https://en.wikipedia.org/wiki/Communicating_sequential_processes
  http://www.usingcsp.com/cspbook.pdf (4/Dec/2022)
"""

# code reviewed by People, Black, Flake8, & MyPy


import collections
import dataclasses
import json
import re
import sys

# import typing


@dataclasses.dataclass(order=True, frozen=True)
class Any:
    """A thing that can be"""

    doc: str | None


#
# 1.1 Introduction
#


A: set  # [implied much later in the text, like in the digression past X7 of 1.1.3 Choice]
B: set


class Event(Any):
    """A thing that happens, especially one of importance"""

    # we don't ask 'whether one event occurs simultaneously with another'

    def __init__(self, doc: str) -> None:
        super().__init__(doc)

    def __repr__(self) -> str:
        doc = self.doc
        assert doc
        return doc


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


class Process(Any):
    """A pattern of behaviour"""

    def menu_choices(self) -> list[Event]:

        no_events: list[Event]
        no_events = list()

        return no_events

    def form_event_process(self, event: Event) -> "Process":

        raise NotImplementedError(event)


VMS: Process
VMS = Process("the simple vending machine")
VMS_0 = VMS  # open up for reassignment

VMC: Process
VMC = Process("the complex vending machine")
VMC_0 = VMC  # open up for reassignment

P: Process  # an arbitrary process
Q: Process
R: Process

STOP = Process("[a process who produces no more events of any alphabet]")

X: Process  # an alias of a process
Y: Process


class Alphabet(Any):
    events: list[Event]  # zero or more Events

    def __init__(self, events: list[Event] = NO_EVENTS, doc: str | None = None) -> None:
        super().__init__(doc)

        self.events = list(events)  # 'copied better than aliased'


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

tick = Event("tick")
αCLOCK = Alphabet([tick])

CLOCK: Process
CLOCK = GuardedProcess("(", tick, " → ", "CLOCK", ")", doc="a perpetual clock")
vname_push("CLOCK", process=CLOCK)

CLOCK_0 = CLOCK  # open up for reassignment


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

    def menu_choices(self) -> list[Event]:
        proc = self.process
        events = proc.menu_choices()
        return events

    def form_event_process(self, event: Event) -> Process:
        proc = self.process

        vname_push(self.vname, process=self)
        event_proc = proc.form_event_process(event)
        # vname_pop(self.vname, process=self)  # todo: make this work

        return event_proc


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
#         "|",
#         ChoiceProcess(
#             "(",
#             [
#                 GuardedProcess("(", y, " → ", Q, ")"),
#                 "|",
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
#             "|",
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
        "|",
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
        "",
        [
            GuardedProcess("", [out1p, " → ", out1p, " → ", out1p, " → ", out2p], " → ", "CH5C", ""),
            "|",
            GuardedProcess("", [out2p, " → ", out1p, " → ", out2p], " → ", "CH5C", ""),
        ],
        "",
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
                "|",
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
                    "|",
                    GuardedProcess("", [small, " → ", out1p], " → ", "VMC", ""),
                ],
                ")",
            ),
            "",
        ),
        "|",
        GuardedProcess(
            "",
            in1p,
            " → ",
            ChoiceProcess(
                "(",
                [
                    GuardedProcess("", small, " → ", "VMC", ""),
                    "|",
                    GuardedProcess(
                        "",
                        in1p,
                        " → ",
                        ChoiceProcess(
                            "(",
                            [
                                GuardedProcess("", large, " → ", "VMC", ""),
                                "|",
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
            "|",
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
            "|",
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
        "|",
        GuardedProcess("", setlemon, " → ", "DD_L", ""),
    ],
    ")",
)

DD_O = ChoiceProcess(
    "(",
    [
        GuardedProcess("", orange, " → ", "DD_O", ""),
        "|",
        GuardedProcess("", setlemon, " → ", "DD_L", ""),
        "|",
        GuardedProcess("", setorange, " → ", "DD_O", ""),
    ],
    ")",
)

DD_L = ChoiceProcess(
    "(",
    [
        GuardedProcess("", lemon, " → ", "DD_L", ""),
        "|",
        GuardedProcess("", setorange, " → ", "DD_O", ""),
        "|",
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


def CTN(n: int) -> Process:

    if n == 0:
        P = ChoiceProcess(
            "(",
            [
                GuardedProcess("", up, " → ", f"CTN({1})", ""),
                "|",
                GuardedProcess("", around, " → ", f"CTN({0})", ""),
            ],
            ")",
        )
        return P

    P = ChoiceProcess(
        "(",
        [
            GuardedProcess("", up, " → ", f"CTN({n + 1})", ""),
            "|",
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

    Q = P
    while True:
        events = Q.menu_choices()
        event_strs = list(str(_) for _ in events)

        while True:
            print(event_strs)

            line = sys.stdin.readline()

            if not events:
                print("BLEEP")
                return

            if len(events) == 1:
                event = events[0]
                break

            strip = line.strip()
            if strip in event_strs:
                event = events[event_strs.index(strip)]
                break

        Q = Q.form_event_process(event)


#
# 1.5 Traces
#

#
# FIXME: Run well from the Sh Command Line
#


def main() -> None:

    assert sys.argv[1:] == ["--yolo"], (sys.argv[1:],)


#
# FIXME: React well when called from Pq
#


def csprocess(ilines) -> list[str]:

    dumps = json.dumps(dict(), indent=2)

    olines = dumps.splitlines()
    return olines


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/csp.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
