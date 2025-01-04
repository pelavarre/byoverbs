<!-- omit in toc -->
# Turtling in the Python Terminal

Contents

- [Welcome](#welcome)
- [You can just try things](#you-can-just-try-things)
  - [Move the Turtle](#move-the-turtle)
  - [Draw a Small Triangle](#draw-a-small-triangle)
    - [Relaunch](#relaunch)
    - [Symmetry](#symmetry)
    - [Terminal Window Shape, Size, Darkmode, Lightmode, \& Fonts](#terminal-window-shape-size-darkmode-lightmode--fonts)
  - [Draw a Large Square](#draw-a-large-square)
  - [Glance through the Help Texts](#glance-through-the-help-texts)
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

If you're seeing this Md File inside GitHub, it should look ok already.
But on a MacBook you might prefer to read this Md File
at VsCode ⇧⌘V Markdown Open Preview


## Welcome

Welcome to our game

You download the Source Code

    mkdir bin

    curl -Ss https://raw.githubusercontent.com/pelavarre/byoverbs/refs/heads/main/bin/turtling.py >bin/turtling.py

    wc -l bin/turtling.py  # thousands of lines

You open one Terminal Window to run the Server at right, and
you tell it to invite Turtles to move around and draw on the Terminal Screen

    python3 bin/turtling.py --yolo

You open another Terminal Window to run the Client at left, and
you tell it to invite you to type out Turtle Logo Instructions to run through

    python3 bin/turtling.py -i

We take the Turtle Logo Instructions you type in the left Window,
auto-complete them to form Python Instruction,
and run through the Python Instructions in the right Window,
telling Turtles how to move and what to draw

This Md File walks you through tests of such Turtle Logo Instructions

You've met with us here in our early days.
If you quit before we stop talking at you, then we've gone wrong.
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

You'll see a Triangle drawn. Something like

    ██
    ██████
    ██    ████
    ██        ████
    ██            ████
    ██                ██
    ██            ████
    ██        ████
    ██    ████
    ██████
    ██


#### Relaunch

Turtle Logo's disagree over how to speak the idea of Relaunch the Game.
Above you see we have you say Relaunch.
We'll also accept you saying just Restart when you do mostly want to start over,
but you don't want to clear the Screen.
Python Import Turtle would have you say Reset,
so long as you're working with only 1 Turtle,
but Python Import Turtle gets messier when working with more Turtles


#### Symmetry

Turtle Logo's disagree over how symmetric a small Triangle should be.
We're still developing our small Triangles,
inside our [demos/arrow-keys.logo](../demos/arrow-keys.logo)
Our Triangles pointing up and down don't yet exactly match
our Triangles pointing left and right


#### Terminal Window Shape, Size, Darkmode, Lightmode, & Fonts

We rely on you to make your own Terminal Windows,
so you make several choices for us

You chose your Shape of Window for us.
Turtle Logo's disagree over whether
to draw in a Landscape, Portrait, or Square Window

You choose your Size of Window for us.
Turtle Logo's disagree over how large to make the Window

You choose Lightmode or Darkmode.
Turtle Logo's disagree over whether
to draw Dark Pixels on a Lightmode Canvas, or
to draw Light Pixels on a Darkmode Canvas.
In particular, the 2024 Python Import Turtle forces Lightmode,
even when clashing with the Darkmode's of macOS or ReplIt·Com

You choose your default Terminal Font.
Presently we guess the Pixel you want is a Square pair of U+2588 Full-Block █ █ Characters.
Lotsa of Terminal Font's disagree over how to draw a U+2588 Full-Block █ Character.
Many Fonts agree Full-Block means paint the full horizontal width,
but lots disagree over how much of the vertical height to paint over.
I've not yet found a Font that says Full-Block should paint the full vertical height.

As for me, as you can see in my screenshots,
lately mostly I test Screens of
101 Columns and 42 Rows of Andale Mono 18
in the Lightmode Basic Profile of the macOS Terminal App in Oct/2023 Sonoma macOS 14
<!-- Oct/2024 Sequoia macOS 15 since Jan/2025 -->

I haven't tested Ghostty, nor iTerm either

I'd love to see screenshots or video of how well the Turtle Logos work for you,
on the Terminals you choose to test


### Draw a Large Square

Try

    relaunch
    setxy -180 180  setxy 180 180  setxy 0 0
    setxy 180 180  setxy 180 -180  setxy 0 0
    setxy 180 -180  setxy -180 -180  setxy 0 0
    setxy -180 -180  setxy -180 180  setxy 0 0

Turtle Logo's disagree over how large this Square is.
UCB Turtle Logo makes a Square from -250 -250 to 250 250 as large as their Square Window

Presently we fit a Square from -180 -180 to 180 180
into a Terminal Window of 101 Columns x 42 Rows


### Glance through the Help Texts

To see all our Turtle Verbs listed, try

    help(t)

You'll see our Help suggests you play around, saying
Backward, Beep, Breakpoint, Bye,
ClearScreen,
Forward,
HideTurtle, Home,
IsDown, IsVisible,
Label, Left,
PenDown, PenUp,
Relaunch, Repeat, Restart, Right,
SetHeading, SetHertz, SetPenColor, SetPenPunch, SetX, SetXY, SetY, ShowTurtle, Sleep,
Tada,
and Write

It then tells you to press Q to quit.
It means that you press the Q Key once, to start serving drawings again

Try

    help(t.forward)

You'll see Python telling you that our Forward Verb takes a Keyword Argument named:  distance


### Choose your own Defaults, when you dislike ours

Try

    relaunch
    rt fd rt fd
    lt bk lt bk

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
    rt fd rt fd
    lt bk lt bk

There you've told us to make this different Shape

We don't make you type out the Verb and Argument Names in full.
For the same result, you can type just

    relaunch
    d = 100
    lt.a = 90
    rt fd rt fd
    lt bk lt bk

Python itself objects if you explicitly try to say 't.left.angle = 90'.
It will sayAttributeError: 'method' object has no ...
So we round off what you're saying to become 'left_angle = 90'
and we tell our 't.left' to watch for you to say that

Presently, to see all that we abbreviate for you, you can try

    TurtlingDefaults
    KwByGrunt
    PythonSpeaker().verb_by_grunt

This is an act of peeking deep into the guts.
Odds on, we'll soon dream up some better way to disclose these secrets,
and this exact spelling of a deep peek into the guts will stop working

To remember what defaults you've chosen, you can look at things like

    dir()

    locals()

    distance
    left_angle

To undo what you've said, you can try

    del distance
    del left_angle
    dir()

These works of Dir and Del and Locals and so on are standard Python ways of speaking.
They work without us pouring any special effort into making them work


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
> [demos/xyplotter.logo](../demos/xyplotter.logo)<br>

If you open up a third Terminal Window, then you can ask to try them one-at-a-time like so =>

    for F in demos/*.logo; do echo; (set -xe; cat $F |pbcopy); read; done

That Sh Script does the ⌘C Copy into your Os-Copy/Paste-Clipboard for you,
where it calls for '|pbcopy'.
But you have to do the ⌘V Paste part yourself,
back into your second Terminal Window,
where you've left the "🐢?" Turtle Chat going


### Play around

Plainly, we should tell you more, but what?

You've joined us in our early days,
while we're still rapidly rewriting what's here,
to make it more friendly

Presently, you can draw an Pentagon like this

    relaunch
    rep 5

Traditionally, talk of Turtle Logo
makes the first lesson in '🐢? repeat' be exactly this:
the parts of a polygon
drawn by repeating a Forward Move and a Right Turn

You can redraw this same Pentagon by more spelling out the steps

    relaunch
    fd rt 72  fd rt 72  fd rt 72  fd rt 72  fd rt 72

We let you say 'fd' in place of 'fd 100' or 'forward 100'
Most other Turtle Logos hold to the 1960's Lisp convention
of requiring you to give the same number of arguments every time you try something,
unless you explicitly enclose them inside '()' parentheses.
We depart from that convention intentionally.
We let you type out more or less arguments as you please

You can also type out the raw Python to draw this same Pentagon

    relaunch
    count = 5
    for _ in range(count): t.forward(100); t.right(360 / count)

<!--  pu  setxy -260 -10  pd  -->

You hit the edges and distort the drawing,
when you choose a Repeat_Count of 8 or more,
or if you choose a Forward_Distance larger than 100,
when you're drawing on the 101x42 Columns and Rows of my Terminal,
Some Turtle Logos will wrap the Cursor at the edges,
rather than insisting that you always center your drawings yourself.
Like if you click into the Server Window and press Return after Relaunch,
but before the Count = and For,
then you can draw Count as large as 10 in my Terminal today.
If you watch for it, you can see
our Client prints "Snap" Messages when your drawing grows too large,
such that we clip and distort it

For such Notes coming back from the Turtle to make the most sense,
you'll want to see them in real-time.
If you try 'sleep 0' after you press Return, before the Count = and For,
then you'll see the Note on you having pressed Return pops up then.
You can try just 's' to clear the Note too.
That works a little less directly,
by sleeping as long as the last 🐢 SetHertz said to sleep


### Help sort our Wish List

Have you found a deal-breaker that's shutting you out somehow,
stopping you from playing this game some more?

Tell us what it is?

Like we could give this game a more game-like feel,
if we completed a full Python Command every time you pressed a Key at the Server.
Or we could rewrite our Arrow Keys Demo to have 4 Turtles draw it, not just 1.
And so on and on and on

You've joined us in our early days.
We don't have more than a few of us gathered here yet, dreaming out what's the most fun.
Tell us what change you want next, and odds on we'll deliver it sooner


## Dig in technically, deep into the Python

You could review the whole Code? Read every line of the Python? No one has before you

Or you could pick out just one aspect of the Code to drill down into?

Our Turtle Logo App here is thousands of lines large.
It's large enough that it gives
its own kind of a tour of the Standard Python Library.

It mixes together 27 Imports

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
