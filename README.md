# byoverbs
Your Sh Terminal runs lots of mostly abandoned C Code from like 1972

We work here to fix it cheaply, by rewriting that C Code as Python now

## Vi

### Vi Bel

Vi Py doesn't slap you with the Bel so much
1. no slap while you're repeating the movement that brought you to an edge
2. no slap when you press ⌃C just once to know where you're starting

### Vi C0 Escape Sequences

Vi Py lets you type C0 Escape Sequences straight into the Screen, you don't have to find the Vi Key Chord sequence to compose them

    vi.py --

You might like

    ⎋[d line-position-absolute  ⎋[G cursor-character-absolute
    ⎋[1m bold  ⎋[31m red  ⎋[32m green  ⎋[34m blue  ⎋[38;5;130m orange  ⎋[m plain
    ⎋[4h insertion-mode  ⎋[6 q bar  ⎋[4l replacement-mode  ⎋[4 q skid  ⎋[ q unstyled
    ⎋[M delete-line  ⎋[L insert-line  ⎋[P delete-character  ⎋[@ insert-character
    ⎋[T scroll-up  ⎋[S scroll-down

### Vi Colored Text Files

Vi Py lets you edit colored Text Files, not just uncolored Text Files

    vi.py screenlog.0  # from Sh:  screen -L
    vi.py typescript  # from Sh:  script

### Vi the Pty Stream

Vi Py lets you shell out and edit what happens there, because there you do give Vi Py the privilege of reading what Characters those are

### Vi the Sh Pipe

Vi Py lets you edit the Sh Pipe you put it inside of

    pbpaste |vi.py - |pbcopy

### Vi the Sh Terminal Screen

Vi Py lets you edit what you already printed onto your Sh Terminal Screen, even though you keep Vi Py blocked from reading what Characters those were

## macOS

### Ls Full-Time

macOS cuts you off from:  ls --full-time

fixable at Ls Py

### Sh Screen > Vi > Py Color > Def

draw the Py "def" Keyword

    vi p.py  # spec: 256-Color Orange
    screen vi p.py  # bug: 16-Color Yellow
    screen bash -c "TERM=$TERM vi p.py"  # bug: 8-Color Red

fixable at Screen Py, because Vi ok inside Demos PseudoTty
fixable at Vi Py, because Sh PrintF Orange ok inside Demos PseudoTty

## Python
### Import Pty > Stty Size

count the Columns x Rows of the Sh Terminal Screen

    stty size  # bug: (0, 0) inside Import Tty

fixable at Vi Py, because Csi 07/04 Private reports Column x Rows anyhow

    printf '\e[18t' && python3 -c 'import sys; print(repr(sys.stdin.read()))'

## Sh

### Man Pages

Our Py Files can give you the Missing Examples from the Missing Manuals of Linux & co

Call us with no Arguments, because Examples for new people matter more than default actions for the rest of us

    ls.py
    screen.py
    vi.py

### Screen Ls

Classic Sh 'screen -ls' could suggest one 'screen -r' Sh Command Line for each detached Screen, but doesn't

Screen Py fixes this, for macOS & for Linux

## Come back tomorrow

As yet, we're more working to show off what you can afford to fix, not so much working to come fix it for you

If you need something fixed, come talk to us enough and we might fix it - Many many fixes are easy to write in Python

We don't have all our own Code and Docs here all synched up lately - Come talk to us enough and we'll fix the bugs that bother you

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/README.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
