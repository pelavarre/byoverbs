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


coin = Event("the insertion of a coin in the slot of a vending machine")
choc = Event("the extraction of a chocolate from the dispenser of the machine")

in1p = Event("the insertion of one penny")
in2p = Event("the insertion of a two penny coin")
small = Event("the extraction of a small biscuit or cookie")
large = Event("the extraction of a large biscuit or cookie")
out1p = Event("the extraction of one penny in change")

x: Event
y: Event
z: Event


reassignments: list[tuple[str, object]]  # the aliases we know we've mutated
reassignments = list()


class Process(Any):
    """A pattern of behaviour"""


VMS: Process
VMS = Process("the simple vending machine")

VMC: Process
VMC = Process("the complex vending machine")

P: Process  # an arbitrary process
Q: Process
R: Process

STOP = Process("[a process who produces no more events of any alphabet]")

X: Process  # an alias of a process
Y: Process


NO_EVENTS: list[Event]
NO_EVENTS = list()


class Alphabet(Any):
    events: list[Event]  # zero or more Events

    def __init__(self, events: list[Event] = NO_EVENTS, doc: str | None = None) -> None:
        super().__init__(doc)

        self.events = list(events)  # 'copied better than aliased'


αVMS = Alphabet([coin, choc])
αVMC = Alphabet([in1p, in2p, small, large, out1p])

STOPαVMS = STOP  # todo: associate with αVMS
STOPαVMC = STOP  # todo: associate with αVMC


# 1.1.1 Prefix


class GuardedProcess(Process):
    """Event x, then Process P"""

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
        """List the Guards of the Process"""

        if isinstance(self.events, Event):
            event = self.events
            guards = [event]
        else:
            guards = list(_ for _ in self.events if isinstance(_, Event))

        return guards

    def menu_choice(self) -> Event:
        """Say which Event is the first Guard of the Process"""

        guards = self.guards()
        menu_choice = guards[0]

        return menu_choice


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
GuardedProcess("(", coin, " → ", STOPαVMS, ")")


# X2
# (coin → (choc → (coin → (choc → STOPαVMS))))
GuardedProcess(
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


tick = Event("tick")
αCLOCK = Alphabet([tick])

CLOCK: Process
CLOCK = GuardedProcess("(", tick, " → ", "CLOCK", ")", doc="a perpetual clock")

# CLOCK = (tick → CLOCK)  # tick → tick → tick → ...


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

reassignments.append(("CLOCK", CLOCK))

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

reassignments.append(("VMS", VMS))

VMS = GuardedProcess(  # (replaces earlier less complete definition)
    "(",
    [coin, " → ", choc],
    " → ",
    "VMS",
    ")",
    doc="the simple vending machine",
)


# X3

# CH5A = (in5p → out2p → out1p → out2p → CH5A)

in5p = Event("the insertion of a five penny coin")
out2p = Event("the extraction of two pennies in change")
αCH5A = Alphabet([in5p, out2p, out1p])

CH5A = GuardedProcess(
    "(",
    [in5p, " → ", out2p, " → ", out1p, " → ", out2p],
    " → ",
    "CH5A",
    ")",
    doc="a machine that gives change for 5p repeatedly",
)


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
        events = list(_.menu_choice() for _ in procs)
        return events

    def menu_procs(self) -> list[GuardedProcess]:
        choices = self.choices
        procs = list(_ for _ in choices if isinstance(_, GuardedProcess))
        return procs


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

ChoiceProcess(
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

reassignments.append(("VMC", VMC))

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

in_0 = Event("input of zero on its input channel")  # they choose inputs
in_1 = Event("input of one on its input channel")

out_0 = Event("output of zero on its output channel")  # it chooses outputs
out_1 = Event("output of one on its output channel")

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


#
# As if Import Csp
#


def csprocess(ilines) -> list[str]:

    dumps = json.dumps(dict(), indent=2)

    olines = dumps.splitlines()
    return olines


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/csp.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
