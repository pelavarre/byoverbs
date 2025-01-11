<!-- omit in toc -->
# Turtling in the Python Terminal

Contents

- [Welcome](#welcome)
  - [Working separately or not](#working-separately-or-not)
  - [Starting over expertly](#starting-over-expertly)
  - [Please expect we've gone wrong](#please-expect-weve-gone-wrong)
- [You can just try things](#you-can-just-try-things)
  - [Move the Turtle](#move-the-turtle)
  - [Draw a Triangle](#draw-a-triangle)
    - [Relaunch](#relaunch)
    - [Symmetry](#symmetry)
    - [Terminal Window Shape, Size, Darkmode, Lightmode, \& Fonts](#terminal-window-shape-size-darkmode-lightmode--fonts)
  - [Draw a Huge Square](#draw-a-huge-square)
  - [Draw Animals](#draw-animals)
    - [Natalia's Snake](#natalias-snake)
    - [Tina's Giraffe](#tinas-giraffe)
  - [Draw Circles and parts of Circles](#draw-circles-and-parts-of-circles)
  - [Explore More Colors](#explore-more-colors)
    - [Explore 24-Bit Color in the Cloud](#explore-24-bit-color-in-the-cloud)
    - [Explore 8-Bit Color at macOS](#explore-8-bit-color-at-macos)
  - [Glance through the Help Texts](#glance-through-the-help-texts)
  - [Draw famous Figures](#draw-famous-figures)
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

Four Steps =>

1

**You start inside a macOS or Linux**

If you don't already have a Linux,
you can go run the 4+ GB Linux that your gMail gives you free at

> https://shell.cloud.google.com/?show=terminal

I wish we could recommend the replIt Startup service over the gShell Corporate service,
but your free gMail gCloud gShell runs much faster than the free tier of replIt.
And of course getting a hold of a macOS Terminal like mine
would cost you hundreds or thousands of US Dollars

2

**You download the Source Code**

    curl -Ss https://raw.githubusercontent.com/pelavarre/byoverbs/refs/heads/main/bin/turtling.py >turtling.py

    wc -l turtling.py  # thousands of lines

You can just run the Code.
I wish we could find someone to judge for you how much trust you should give to this Code.
This Code is published, formatted for review, at
GitHub > [Turtling·Py](https://github.com/pelavarre/byoverbs/blob/main/bin/turtling.py)

3

**You open one Terminal Window or Tab**, and
you tell it to move Turtles around to draw things on the Terminal Screen

    python3 turtling.py --yolo

4

**You open another Terminal Window or Tab**, and
you tell it to chat with you,
giving you your chance to type out Logo Instructions for your Turtles

    python3 turtling.py -i

Our Code takes the brief Logo Instructions you type,
fills them out to form Python Instructions carefully spelled and punctuated,
and then forwards the Python into the Turtles in the other Windows or Tabs,
so that those Turtles then run the Python to move around and draw things for you

This Md File walks you through tests of such Turtle Logo Instructions

### Working separately or not

I really like running my Turtles and my Chat in separate Windows, not just separate Tabs.
You can run separate Windows at replIt·Com, and at macOS,
but not at gMail gCloud gShell.
That gShell will let you split a single Terminal Tab,
which can be as good.
But if you want the Font for your Turtles to be lots smaller
than the Font for your Chat,
then you have to run macOS or replIt·Com or something other than gShell

### Starting over expertly

Next time you start over,
if you want just one thing to remember,
it turns out you can start both Terminal Windows or Tabs in the same way.
They both work if you always start each Tab or Window with:&nbsp; python3 turtling.py --yolo

### Please expect we've gone wrong

You're meeting with us here in our early days.
If you quit reading before we stop talking at you, then we've gone wrong.
That's when you know you've tested our Doc and our Doc failed you.
We'd love to have you tell us exactly how far you got, please


## You can just try things


### Move the Turtle

Try

    fd

We guess you meant 't.forward(100)', so we type that out for you, as you can see.
You can type 'forward' to mean the same thing

    forward

Over inside your Turtle's Tab or Window,
you can see it drew a Line of 11 Squares for you.

Why 11 and not 10?
Well, I'm not sure about that.
You're meeting with us here in our early days.
We're still figuring out what Turtling Well means

You can type out the full Python yourself if you want:

    import turtling
    t = turtling.Turtle()
    t.forward(100)

Note: We define 'import turtling'. The people at Python·Org define only 'import turtle'


### Draw a Triangle

Try

    relaunch
    fd 100 rt 120  fd 100 rt 120  fd 100 rt 120

You'll see your Turtle drew a Triangle. Something like

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
We're still figuring out our small Triangles,
inside our [arrow-keys.logo](../demos/arrow-keys.logo) Demo.
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
even when clashing with the Darkmode's of replIt or macOS.
(And it often declines to run altogether at gShell.)

You choose your default Terminal Font.
Presently we guess the Pixel you want is a Square pair of U+2588 Full-Block █ █ Characters.
Lotsa of Terminal Fonts disagree over how to draw a U+2588 Full-Block █ Character.
Many Fonts agree Full-Block means paint the full horizontal width,
but lots of Terminal Fonts disagree over how much of the vertical height to paint over.
I've not yet found a Font that says Full-Block should paint the full vertical height,
but that works that way by default at replIt·Com

As for me, as you can see in my screenshots,
lately mostly I test Screens of
101 Columns and 42 Rows of Andale Mono 18
in the Lightmode Basic Profile of the macOS Terminal App in Oct/2024 Sequoia macOS 15

I think most of you are working inside your gMail gCloud gShell.
I've also seen the free tier of replIt work.
I haven't tested macOS Ghostty, nor macOS iTerm2 either

I'd love to see screenshots or video of how well the Turtle Logos work for you,
on the Terminals you choose to test.
I've posted mine into LinkedIn, Mastodon, and Twitter.
I can send you copies. We can trade


### Draw a Huge Square

Try

    relaunch
    setxy -180 180  setxy 180 180  setxy 0 0
    setxy 180 180  setxy 180 -180  setxy 0 0
    setxy 180 -180  setxy -180 -180  setxy 0 0
    setxy -180 -180  setxy -180 180  setxy 0 0

Don't forget to press Return after the end of the last Line of your Input here

Turtle Logo's disagree over how large this Square is.
UCB Turtle Logo makes a Square from -250 -250 to 250 250 as large as their Square Window

Presently we fit a Square from -180 -180 to 180 180
into a Terminal Window of 101 Columns x 42 Rows


### Draw Animals

#### Natalia's Snake

Draw Natalia's Snake, first drawn by Natalia of Bucharest

    relaunch
    rt 180  fd 30
    lt 90  fd 10  rt 90  fd 10  bk 10
    lt 90  fd 10  lt 90  fd 30  bk 30
    write '█'  fd 30
    rt 90  fd 10  lt 90  fd 10  bk 10
    rt 90  fd 10  lt 90  bk 30  fd 30
    rt 90  fd 10  lt 90  fd
    rt 90  bk 10  write ' '  fd 20  write '  █'
    tada

<!--

clear; pbpaste
printf '\e[H''\e[13L''\e[39H'  # 39 of 42
bin/turtling.py --yolo
⎋[28'⇧}

-->

#### Tina's Giraffe

Draw Tina's Giraffe, first drawn by Tina of Monterey

    relaunch
    penup home pendown
    rt 270  fd  lt 90  fd
    penup home pendown  write '█'
    bk 100
    penup home pendown  write '█'
    rt 45  fd 100
    seth  rt 90  fd 30
    penup home
    fd 10  write '   █'
    tada

<!-- FIXME: Fully Relaunch after Write '   █' without '█' -->

### Draw Circles and parts of Circles

To draw three-quarters of a Circle, try

    relaunch
    arc arc arc

To draw a couple of Overlapping Circles, try

    relaunch
    arc 360
    penup  setxy -50 30  pendown
    arc 360

To draw a Latin Capital Letter P in five colors, try

    relaunch
    setpencolor red  arc
    setpencolor green  arc
    setpencolor blue  arc
    setpencolor yellow  arc
    setpencolor none
    bk 150

To draw something like the two Curves and a Line of the Atari ™ Logo, try

    relaunch
    left 90  arc  fd 10 bk 10
    penup  lt 90  fd 20  pendown
    seth  fd 10 bk 10  bk 50  fd 50
    penup  lt 90  fd 20  pendown
    seth  fd 10 bk 10  rt 180  arc

To draw a tall thin Ellipse, try

    relaunch
    penup setx -100 pendown
    setxyzoom 0.20 1.00
    arc arc arc arc

To draw a Plain Diamond inside a Blue Circle inside a Green Square,
at the Center of the Screen

    relaunch
    penup  lt 90  fd 50  rt 90  pendown
    setpencolor  green  bk 50  rep 4  fd 50
    setpencolor blue  arc arc arc arc
    setpencolor  none  rt 45  rep 4 360 70.7  lt 45
    round(100 * math.sqrt(2) / 2, 1)  # 70.7

To draw a Large Arc as a Repeat of Forward Right

    relaunch
    repeat 25 90 10


### Explore More Colors

The most classic most basic 8 Colors of a Sh Terminal are

    setpc white
    setpc magenta
    setpc blue
    setpc cyan
    setpc green
    setpc yellow
    setpc red
    setpc black

You can call for these Colors like that, or
you can cast more arcane, fiddly, intricate Terminal Spells such as

    write '\e[37m'  # White
    write '\e[35m'  # Magenta
    write '\e[34m'  # Blue
    write '\e[36m'  # Cyan
    write '\e[32m'  # Green
    write '\e[33m'  # Yellow
    write '\e[31m'  # Red
    write '\e[30m'  # Black

If you dig down into the deep magic like that,
then you can swap in deeper magic.
For example

    write '\e[38;5;130m'  # Orange

#### Explore 24-Bit Color in the Cloud

There's a world of Colors out there, and I don't yet know it well.
One of the websites talking of Sh Terminal Colors is

Wikipedia > [ANSI escape code](https://en.wikipedia.org/wiki/ANSI_escape_code)

Searching with ⌘F 31 will show you
Wikipedia People talking of ESC[31m, as we did above

Searching instead with ⌘F 38; will show you
Wikipedia People talking of "Select RGB foreground color"
from a choice of more than 16 million "24-bit" Colors

For example, inside of a gMail gCloud gShell, try

    write '\x1B[38;2;255;0;0m Red'
    write '\x1B[38;2;0;255;0m Green'
    write '\x1B[38;2;0;0;255m Blue'

<!-- FIXME: Work when given \e at replIt·Com, not only when given \x1B -->

This works inside a replIt·Com Terminal Sh likewise

This does Not work inside a macOS Terminal Sh.
Perplexity·Ai tells me that limitation is famous.
That limitation drives people to swap in other Terminals for macOS.
Such as macOS Ghostty or macOS iTerm2



#### Explore 8-Bit Color at macOS

There's a world of Colors out there, and I don't yet know it well.
One of the websites talking of Sh Terminal Colors is

Wikipedia > [ANSI escape code](https://en.wikipedia.org/wiki/ANSI_escape_code)

Searching with ⌘F 31 will show you Wikipedia People talking of ESC[31m, as we did above

My experiments tell me that macOS Terminals only do the "8-bit" Color of "256-color lookup tables". For example, this experiment works

    relaunch
    write '\e[38;5;4m'
    fd 50  bk 50  rt 30  # Darker Purple
    write '\e[38;5;5m'
    fd 50  bk 50  rt 30  # Darker Pink
    write '\e[38;5;12m'
    fd 50  bk 50  rt 30  # Purple
    write '\e[38;5;13m'
    fd 50  bk 50  rt 30  # Lighter Pink
    write '\e[38;5;40m'
    fd 50  bk 50  rt 30  # Darker Green
    write '\e[38;5;80m'
    fd 50  bk 50  rt 30  # Lighter Blue Green
    write '\e[38;5;120m'
    fd 50  bk 50  rt 30  # Lighter Green
    write '\e[38;5;160m'
    fd 50  bk 50  rt 30  # Red
    write '\e[38;5;200m'
    fd 50  bk 50  rt 30  # Much the Same Pink
    write '\e[38;5;241m'
    fd 50  bk 50  rt 30  # Darker Gray
    write '\e[38;5;249m'
    fd 50  bk 50  rt 30  # Lighter Gray
    setpc none  penup  home
    tada

Wikipedia People tell us these '38;5' Color Numbers carry a meaning like so

    0-  7:  standard colors (as in ESC [ 30–37 m)
    8- 15:  high intensity colors (as in ESC [ 90–97 m)
    16-231:  6 × 6 × 6 cube (216 colors): 16 + 36 × r + 6 × g + b (0 ≤ r, g, b ≤ 5)
    232-255:  grayscale from dark to light in 24 steps

Some tests of replIt·Com choked unless we type our \e notation,
extended from merely standard Python,
as \x1B instead. I dunno why yet

    write '\x1B[m'
    # Plain Text, Uncolored

<!-- FIXME: work despite trailing # commentary -->
<!-- FIXME: w for write -->
<!-- FIXME: no quotes needed for \e without Spaces -->


### Glance through the Help Texts

To see all our Turtle Verbs listed, try

    help(t)

The Help appears in the Tab or Window of the Turtles,
not the Tab or Window where you typed out 'help(t)' to ask for it.
When you're done reading the Help, press Q to see your Drawings again.
Press Spacebar before Q if you want to see more Screenfuls of the Help

You'll see our Help suggests you play around, saying please try
Arc, Backward, Beep, Bye,
ClearScreen,
Forward,
HideTurtle, Home,
IncX, IncY, IsDown, IsVisible,
Label, Left,
PenDown, PenUp,
Relaunch, Repeat, Restart, Right,
SetHeading, SetHertz, SetPenColor, SetPenPunch, SetX, SetXY, SetXYZoom, SetY,
ShowTurtle, Sierpiński, Sleep,
Tada,
and Write.
Help is not in this list,
because Help is a thing of Python itself,
not just a thing of our kind of Logo Turtle.
When you try this yourself,
you'll also see talk of Breakpoint and Exec,
but those take more knowledge to speak well

<!-- FIXME: Can we hide t.breakpoint, t.exec, t.mode? -->

It then tells you to press Q to quit.
It means that you press the Q Key once, to start serving drawings again

Try

    help(t.forward)

You'll see Python telling you that our Forward Verb takes a Keyword Argument named:  distance

A quicker way to see all our Turtle Verbs mentioned even more briefly is

    dir(t)


### Draw famous Figures

Draw Sierpiński's Triangles inside Triangles,
first well explained by Sierpiński in Warsaw, also known as Sierpiński's Sieve or Gasket

    relaunch
    pu  setxy 170 -170  lt 90  pd
    sierpiński 400

To pack more Pixels into the same macOS Terminal Window, you can press

    ⌘- View > Smaller

You can press that again and again to make the Pixels smaller.
And you can drag the lower-right Corner of the Window to make the Window larger again.

To undo what you've done, you can press ⇧⌘+ View > Bigger again and again,
or even choose to press ⌘0 Default Font Size

While you've got lots more Pixels to draw with,
such as 387 X 133 Y,
you can draw more Triangles inside Triangles,
such as

    relaunch
    pu  setxy 510 -510  lt 90  pd
    sierpiński 1200

**Links**

Wiki > [Sierpiński triangle](https://en.wikipedia.org/wiki/Sierpi%C5%84ski_triangle)<br>


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
So we round off the 'lt.a = 90' that you say to become 'left_angle = 90'
and we tell our 't.left' to watch for you having said that

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

These works of Dir and Del and Locals and so on
are standard, arcane, intricate Python ways of speaking.
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
> [demos/rainbow.logo](../demos/rainbow.logo)<br>
> [demos/xyplotter.logo](../demos/xyplotter.logo)<br>

Our "arrow-keys" draws the four Arrow keys of a macBook Keyboard.
Our "bkboxbox" and "fdboxbox" draw two boxes, one inside the other,
one clockwise, the other anticlockwise.
Our "headings" draws Lines of 30°, 45°, 60°, and 90° in each of the four Quadrants.
draws something a lot like concentric circles,
somewhat miscalculated by hand, with charm.
Our "rainbow.logo"
draws concentric circles, calculated by machine.
Our "xyplotter.logo" draws a Parabola, twice,
accelerating as it goes right, decelerating as it goes left

To try each of these in turn,
you can open them up, one at a time, and paste them into your chat with the Turtles

At macOS, we know how to work with the Os-Copy/Paste-Clipboard.
At macOS, you can open up a third Terminal Window to work with the Sh,
and push them into the Clipboard together, one at a time

    for F in demos/*.logo; do echo; (set -xe; cat $F |pbcopy); read; done

That macOS Sh Script does the ⌘C Copy into your Os-Copy/Paste-Clipboard for you,
over and over again, when it calls '|pbcopy'.
But you have to do the ⌘V Paste part yourself,
back into your second Terminal Window,
where you've left the "🐢?" Turtle Chat going.
And then you have to come back to your Sh Window
and press Return to get the next one going

Your macOS Sh Window can also try them all together, one after another

    cat demos/*.logo |sed 's,tada,ht sleep 1 st,' |pq



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

You hit the edges of the Screen and distort the drawing, when you make it too large.
Like when you're drawing on the 101x42 Columns and Rows of my Terminal,
it'll be too large if you choose a Repeat_Count of 8 or more,
or if you choose a Forward_Distance larger than 100

Some Turtle Logos will wrap the Cursor at the edges,
rather than insisting that you always center your drawings yourself.
As an example of more centering a drawing yourself,
you can click into the Server Window and press Return after Relaunch,
but before the Count = and For,
then you can draw Count as large as 10 in my Terminal today.
If you watch for it, you can see
our Client prints "Snap" Messages when your drawing grows too large,
such that we clip and distort it

For such Messages coming back from the Turtle to make the most sense,
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
Or we could figure out how to show the Turtle
even after you split a gMail gCloud gShell Tab
with ⌃B ⇧" and then moved the Turtle between Splits with ⌃B ↑ and  ⌃B ↓.
replIt·Com has this same disappear-the-Turtle bug
if you run the Turtle and the Chat in separate Browser Windows.
gMail gCloud gShell can't do separate Browser Windows.

And so on and on and on.
Choices and choices and choices, each with intricate and unpredictable consequences.
We stop calling it Technology after it works, just plain works.
This world is still new enough that lots of bits of it don't quite work.
You have to pay enough attention to figure out how to cope, all the same.

You've joined us in our early days.
We don't have more than a few of us gathered here yet, dreaming out what's the most fun.
Tell us what change you want next, and odds on we'll deliver it sooner


## Dig in technically, deep into the Python

You could review the whole Code? Read every line of the Python? No one has before you.
Or you could pick out just one aspect of the Code to drill down into?

Our Turtle Logo App here is thousands of lines large.
It's large enough that it gives
its own kind of a tour of the Standard Python Library.

It mixes together 27 Python Imports

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

Mit·Edu [Scratch](https://scratch.mit.edu) Programming Language - Draw Logo-Like Programs that draw Logo-Like Turtle Graphics

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

Please speak your thoughts out loud as words to someone.
To us, if possible

+ LinkedIn > [pelavarre](https://www.linkedin.com/in/pelavarre)<br>
+ Mastodon > [pelavarre](https://social.vivaldi.net/@pelavarre)<br>
+ Twitter > [pelavarre](https://twitter.com/intent/tweet?text=/@PELaVarre)<br>

Please also thank our people for their efforts, if you catch the chance

**January, 2025**

Georgiana of Bucharest!
She put the Terminal Tabs of the gMail gCloud gShell
forward as the most available Linux Hosts

Natalia of Bucharest!
She drew our first Animal, her Snake

Tina of Monterey!
She drew our first Giraffe


<!-- omit in toc -->
## Copied from

Posted as:  https://github.com/pelavarre/byoverbs/blob/main/docs/turtling-in-the-python-terminal.md<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git<br>
