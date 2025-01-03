<!-- omit in toc -->
# Turtling in the Python Terminal

Contents

- [Welcome](#welcome)
- [You can just try things](#you-can-just-try-things)
  - [Move the Turtle](#move-the-turtle)
  - [Draw a Small Triangle](#draw-a-small-triangle)
    - [Relaunch](#relaunch)
    - [Symmetry](#symmetry)
    - [Shape of Window, Darkmode, Lightmode, and Fonts](#shape-of-window-darkmode-lightmode-and-fonts)
  - [Draw a Large Square](#draw-a-large-square)
  - [Glance through the Help](#glance-through-the-help)
  - [Choose your own Defaults, when you dislike ours](#choose-your-own-defaults-when-you-dislike-ours)
  - [Paste whole Files of Input](#paste-whole-files-of-input)
  - [Play around](#play-around)
  - [Help sort our Wish List](#help-sort-our-wish-list)
- [Dig in technically, deep into the Python](#dig-in-technically-deep-into-the-python)
  - [24 Cross-Platform Python Imports](#24-cross-platform-python-imports)
  - [3 Linux/ macOS Imports](#3-linux-macos-imports)
  - [0 Windows Imports](#0-windows-imports)
  - [Breakpoints](#breakpoints)
    - [Breakpoint the Server](#breakpoint-the-server)
    - [Breakpoint the Client](#breakpoint-the-client)
- [Try out some other Turtle Logo](#try-out-some-other-turtle-logo)
  - [Does it work at your desk?](#does-it-work-at-your-desk)
  - [What kind of drawings does it make?](#what-kind-of-drawings-does-it-make)
- [Help us please](#help-us-please)

<!-- I'd fear people need the headings numbered, if it were just me -->
<!-- VsCode autogenerates this unnumbered Table-of-Contents. Maybe people will cope -->

GitHub posts a rendering of this Md File.
You might prefer to read this Md File there.
Or you might prefer to read this Md File
at VsCode ⇧⌘V Markdown Open Preview


## Welcome

Welcome to our game

You download the Source Code

    mkdir bin

    curl -Ss https://raw.githubusercontent.com/pelavarre/byoverbs/refs/heads/main/bin/turtling.py >bin/turtling.py

    wc -l bin/turtling.py  # thousands of lines

You open one Terminal Window to run the Server at right, and
you tell it to invite Turtles to move around and draw on it

    python3 bin/turtling.py --yolo

You open another Terminal Window to run the Client at left, and
you tell it to invite you to type Turtle Logo Instructions into it

    python3 bin/turtling.py -i

We take the Turtle Logo Instructions you type into the left Window,
auto-complete them to form Python,
and run the Python in the right Window,
to tell the Turtle how to move and what to draw

This Md File walks you through tests of Turtle Logo Instructions

You've joined us in our early days.
If you quit before we stop talking at you, then it's our fault.
You've tested our Doc and our Doc failed you.
We'd love to have you tell us exactly how far you got, please


## You can just try things


### Move the Turtle

Try

    fd

We guess you meant 't.forward(100)', so we type that out for you, as you can see.
You can type 'forward' to mean the same thing

    forward

You can even type out the full Python yourself if you want:

    import turtling
    t = turtling.Turtle()
    t.forward(100)

Note: We define 'import turtling'. They define 'import turtle'


### Draw a Small Triangle

Try

    relaunch
    fd 100 rt 120  fd 100 rt 120  fd 100 rt 120

You'll see a Triangle. Something like

    ██
    █ ███
    █    ███
    █      ███
    █    ███
    █ ███
    ██


#### Relaunch

Turtle Logo's disagree over how to speak the idea of Relaunch the Game.
We have you say Relaunch,
or just Restart when you do mostly want to start over,
but you don't want to clear the Screen.
Python Import Turtle would have you say Reset,
so long as you're working with only 1 Turtle,
but gets messier when working with more Turtles


#### Symmetry

Turtle Logo's disagree over how symmetric a small Triangle should be.
We're still developing our small Triangles,
inside our [demos/arrow-keys.logo](./demos/arrow-keys.logo)
Our smallest Triangles are not yet as symmetric as this.
In fact, our Triangles pointing up and down don't even exactly match
our Triangles pointing left and right


#### Shape of Window, Darkmode, Lightmode, and Fonts

We rely on you to make your own Terminal Windows,
so you make several choices for us

Turtle Logo's disagree over whether
to draw in a Landscape, Portrait, or Square Window.
You chose your Shape of Window for us

Turtle Logo's disagree over whether
to draw Dark Pixels on a Lightmode Canvas, or
to draw Light Pixels on a Darkmode Canvas.
Like 2024 Python Import Turtle forces Lightmode,
even when clashing with the Darkmode's of macOS ior ReplIt·Com.
You chose your Darkmode or Lightmode Terminal for us,
no clash required

Turtle Logo Font's disagree over what U+2588 Full-Block █ means.
Lots of Turtle Logo Fonts agree it means paint the full horizontal width,
but they still disagree over how much of the vertical height to paint over.
I've not yet found a Font that says Full-Block should paint the full vertical height.
Andale Mono 18 is working well enough for me at my macOS Terminal,
inside Oct/2023 Sonoma macOS 14,
<!-- Only Oct/2024 Sequoia macOS 15 since Jan/2025 -->
As you can see in my screenshots,
I haven't tested Ghostty and iTerm at macOS.


### Draw a Large Square

Try

    relaunch
    setxy -250 250  setxy 250 250  setxy 0 0
    setxy 250 250  setxy 250 -250  setxy 0 0
    setxy 250 -250  setxy -250 -250  setxy 0 0
    setxy -250 -250  setxy -250 250  setxy 0 0

Turtle Logo's disagree over how large this Square is.
UCB Turtle Logo makes this Square as large as their Square Window


### Glance through the Help

To see all the Turtle Verbs listed, try

    help(t)

You'll see
Backward, Beep, Breakpoint, Bye,
ClearScreen,
Forward,
HideTurtle, Home,
IsDown, IsVisible,
Label,
PenDown, PenUp,
Relaunch, Repeat, Restart, Right,
SetHeading, SetHertz, SetPenColor, SetX, SetXY, SetY, ShowTurtle, Sleep, Tada, and
Write
suggested

Try

    help(t.forward)

You'll see Python telling you that our Forward Verb takes a Keyword Argument named:  distance

It then tells you to press Q to quit.
It means that you press the Q Key once, to start serving drawings again


### Choose your own Defaults, when you dislike ours

Try

    relaunch
    fd rt fd rt
    bk lt bk lt

Turtle Logo's disagree over what Shape this is.
After all, who's to say?
What is the default Forward Distance? Backward Distance? Right Angle? Left Angle?
And so on and on

You can see our choices, when you try things.
When you come to feel you prefer other choices, you can tell us to change.
Try

    relaunch
    distance = 100
    left.angle = 90
    fd rt fd rt
    bk lt bk lt

There you've told us to make this different Shape

We don't make you type out the Verb and Argument Names in full.
For the same result, you can type just

    relaunch
    d = 100
    lt.a = 90
    fd rt fd rt
    bk lt bk lt

Python itself objects if you explicitly try to say 't.left.angle = 90'.
It will sayAttributeError: 'method' object has no ...
So we round off what you're saying to become 'left_angle = 90'
and we tell 't.left' to watch for that

Presently, to see all that we abbreviate for you, you can try

    TurtlingDefaults
    KwByGrunt
    PythonSpeaker().verb_by_grunt

That's an act of peeking deep into the guts.
Odds on, we'll soon dream up some better way to disclose those secrets

To remember what you've said, you can try

    dir()

To undo what you've said, you can try

    del distance
    del left_angle

These works of Dir and Del are standard Python incantations.
They work without us helping you out


### Paste whole Files of Input

You can paste larger Turtle Logo Programs
in to the '🐢? ' Prompt of the Client Window.
We've not yet worked up a great way to make them more available to you,
but they are posted out there

In particular, presently you can paste one or all of

> [demos/arrow-keys.logo](../demos/headings.logo)<br>
> [demos/bkboxbox.logo](../demos/bkboxbox.logo)<br>
> [demos/fdboxbox.logo](../demos/fdboxbox.logo)<br>
> [demos/headings.logo](../demos/headings.logo)<br>
> [demos/like-a-rainbow.logo](../demos/like-a-rainbow.logo)<br>


### Play around

Plainly, we should tell you more, but what?

You've joined us in our early days,
while we're still rapidly rewriting what's here,
to make it more friendly

Presently, you can draw an Octagon like this

    relaunch
    rep 8

Traditionally, talk of Turtle Logo
makes the first lesson in '🐢? repeat' be exactly this:
the parts of a polygon
drawn by repeating a Forward Move and a Right Turn

You can draw an Octagon by more spelling out the steps

    relaunch
    fd rt 45  fd rt 45  fd rt 45  fd rt 45
    fd rt 45  fd rt 45  fd rt 45  fd rt 45

We let you say 'fd' in place of 'fd 100' or 'forward 100'
Most other Turtle Logos hold to the 1960's Lisp convention
of requiring you to give the same number of arguments every time you try something,
unless you explicitly enclose them inside '()' parentheses.
We depart from that convention inetntionally.
We let you type out more or less arguments as you please

You can also type out the raw Python to draw an Octagon

    relaunch
    n = 8
    for _ in range(n): t.forward(100e0); t.right(360e0 / n)

When drawing on the 101x42 Columns and Rows of my Terminal,
you hit the edges and distort the drawing only when you choose an N of 17 or more.
Some Turtle Logos will wrap the Cursor at the edges,
rather than insisting that you always center your drawings yourself.
Like if you press Return after Relaunch,
but before the N = and For,
then you can draw N as large as 24 in my Terminal today

For the Notes coming back from the Turtle to make sense,
you'll want to see them in real-time.
If you try 'sleep 0' after you press Return, before the N = and For,
then you'll see the Note on you having pressed Return pops up then.
You can try just 's' to clear the Note too.
That works a little less directly,
by sleeping as long as the last 🐢 SetHertz said to sleep


### Help sort our Wish List

Have you found a deal breaker?

Tell us what it is?

Maybe you need us to try making Square Pixels?
Or we could this work a more game-like feel,
if we completed a full Python Command every time you pressed a Key at the Server.
Or we could rewrite our Arrow Keys Demo to have 4 Turtles draw it, not just 1.
And so on and on and on

You've joined us in our early days.
We don't have more than a few of us gathered here yet.
Tell us what change you want next, and odds on we'll deliver it sooner


## Dig in technically, deep into the Python

You could review the whole Code? No one has before you

Or you could pick out just one aspect of the Code to drill down into?

Our Turtle Logo App here is thousands of lines large.
It's large enough that it gives
its own kind of a tour of the Standard Python Library.

### 24 Cross-Platform Python Imports

> import \_\_main\_\_<br>
> import argparse<br>
> import ast<br>
> import bdb<br>
> import collections<br>
> import decimal<br>
> import glob<br>
> import inspect<br>
> import math<br>
> import os<br>
> import pathlib<br>
> import pdb<br>
> import re<br>
> import shlex<br>
> import shutil<br>
> import signal<br>
> import subprocess<br>
> import sys<br>
> import textwrap<br>
> import time<br>
> import traceback<br>
> import typing<br>
> import unicodedata<br>
> import warnings<br>

### 3 Linux/ macOS Imports

> import select<br>
> import termios<br>
> import tty<br>

### 0 Windows Imports

> import mscvrt

We've got nobody testing Microsoft Windows, but you could change that


### Breakpoints


#### Breakpoint the Server

To halt the Server and open it up inside the Pdb Python Debugger, try

    🐢? breakpoint

We'll run that as

    >>> t.breakpoint()

And then it works.

To quit a Pdb Debugging Session, you press C and then Return.
To get help with the Pdb language, you press H and then Return.
I'd vote you learn the P command early,
that being their quick way for you to say Print Repr
that even works with single-letter variable names

If you shove hard enough,
then you can test '🐢? breakpoint(); pass'
which is '>>> breakpoint(); pass'
which is a less helpful thing,
because it runs inside 'tty.setraw'
which is practically never what you want


#### Breakpoint the Client

To halt the Client and open it up inside the Pdb Python Debugger, press

    ⌃C

By the default choices of Python itself, that works only once per Process Launch.
But we've patched it up so it'll work even as you test it again and again

If you have a habit of pressing ⌃C to mean ⌃U Discard Input Line,
that habit won't work here,
but ⌃U will work


## Try out some other Turtle Logo

You can try these same tests inside other Turtle Logo Apps.
In particular, adding Python into macOS lets you try

    python3 -i -c ''

    import turtle
    turtle.mode("Logo")

    t = turtle.Turtle()

    t.forward(100)
    t.right(45)

This Import Turtle demo runs just as well for me in Windows of ReplIt·Com.
But it runs noticeably slower than macOS out there,
at least while I'm only logged in and not paying for the ReplIt·Com service

You could go ask Python·Org people
to learn to auto-complete your Turtle Logo Input as strongly as we do.
They already run with some understanding of abbreviations.
For example, they do understand

    t.fd(100)
    t.rt(45)

Technically, the Turtle Logo language we auto-complete correctly here
is a "Domain-Specific Language (DSL)".
Our DSL here is "ad hoc, informally-specified, bug-ridden, and slow".
I feel it works well, so I like it, I like it lots.
I can only hope we'll scrub more bugs out of it and make it fast too

**Links**

Docs·Python·Org > Import [turtle — Turtle Graphics](https://docs.python.org/3/library/turtle.html)<br>

Wiki > [Domain-specific language]([./demos/arrow-keys.logo](https://en.wikipedia.org/wiki/Domain-specific_language))<br>
Wiki > [Greenspun's tenth rule](https://en.wikipedia.org/wiki/Greenspun%27s_tenth_rule)<br>


### Does it work at your desk?

Our Turtle Logo runs inside more Terminals.
Their Turtle Logo runs inside a macOS Terminal, and inside ReplIt·Com.
In other places, our Turtle Logo still works,
whereas their Turtle Logo tells you things like

    ModuleNotFoundError: No module named 'tkinter'

    _tkinter.TclError: no display name and no $DISPLAY environment variable


### What kind of drawings does it make?

Our Turtle Logo draws with Character Graphics inside the Terminal.
You can copy-paste our drawings into a Google Doc (gDoc), and
edit them inside the Google Doc

To save drawings entirely inside the Terminal,
you can record and replay them (at near infinite speed)
with the Terminal Sh 'screen' command

Their Turtle Logo draws on a Bitmap Canvas in a separate Window that's not a Terminal Window.
You can take screenshots of their drawings,
and share and edit the screenshots


## Help us please

You know you've got thoughts.
Please do speak them out loud as words to someone,
and to us, if possible

+ LinkedIn > [pelavarre](https://www.linkedin.com/in/pelavarre)<br>
+ Mastodon > [pelavarre](https://social.vivaldi.net/@pelavarre)<br>
+ Twitter > [pelavarre](https://twitter.com/intent/tweet?text=/@PELaVarre)<br>


<!-- omit in toc -->
## Copied from

Posted as:  https://github.com/pelavarre/byoverbs/blob/main/docs/turtling-in-the-python-terminal.md<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git<br>
