<!-- omit in toc -->
# Turtling in the Python Terminal

Contents

- [Welcome](#welcome)
- [Move the Turtle](#move-the-turtle)
- [Draw a Small Triangle](#draw-a-small-triangle)
  - [Relaunch](#relaunch)
  - [Symmetry](#symmetry)
  - [Shape of Window, Darkmode, Lightmode, and Fonts](#shape-of-window-darkmode-lightmode-and-fonts)
- [Draw a Large Square](#draw-a-large-square)
- [Play around](#play-around)
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
You might prefer the look of it at VsCode ⇧⌘V Markdown Open Preview


## Welcome

Welcome to our game

You download the Source Code

    mkdir bin
    curl -Ss https://github.com/pelavarre/byoverbs/raw/refs/heads/main/bin/turtling.py >bin/turtling.py

You open one Terminal Window at right, and
you tell it to invite Turtles to move around and draw on it

    python3 bin/turtling.py --yolo

You open another Terminal Window at left, and
you tell it to invite you to type Turtle Logo Instructions into it

    python3 bin/turtling.py -i

We take the Turtle Logo Instructions you type into the left Window,
auto-complete them to form Python,
and run the Python in the right Window,
to tell the Turtle how to move and what to draw

This Md File walks you through tests of Turtle Logo Instructions


## Move the Turtle

Try

    fd

We guess you meant 't.forward(100)', so we type that out for you, as you can see.
You can type 'forward' to mean the same thing.
You can even type out the full Python yourself if you want:

    import turtling
    t = turtling.Turtle()
    t.forward(100)

Note: We define 'import turtling'. They define 'import turtle'


## Draw a Small Triangle

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


### Relaunch

Turtle Logo's disagree over how to speak the idea of Relaunch the Game.
We have you say Relaunch.
Python Import Turtle would have you say Reset,
so long as you're working with only 1 Turtle,
but gets messier when working with more Turtles


### Symmetry

Turtle Logo's disagree over how symmetric a small Triangle should be.
We're still developing our small Triangles,
inside our [demos/arrow-keys.logo](./demos/arrow-keys.logo)
Our smallest Triangles are not yet as symmetric as this.
and our Triangles pointing up and down don't yet exactly match
our Triangles pointing left and right


### Shape of Window, Darkmode, Lightmode, and Fonts

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

Font's disagree over what U+2588 Full-Block █ means.
Lots of Fonts agree it means paint the full horizontal width,
but they still disagree over how much of the vertical height to paint over.
I've not yet found a Font that says Full-Block should paint the full vertical height.
Andale Mono 18 is working well enough for me at my macOS Terminal,
inside Oct/2023 Sonoma macOS 14,
<!-- Only Oct/2024 Sequoia macOS 15 since Jan/2025 -->
as you can see in my screenshots online.
I haven't tested Ghostty and iTerm at macOS.


## Draw a Large Square

Try

    relaunch
    setxy -250 250  setxy 250 250  setxy 0 0
    setxy 250 250  setxy 250 -250  setxy 0 0
    setxy 250 -250  setxy -250 -250  setxy 0 0
    setxy -250 -250  setxy -250 250  setxy 0 0

Turtle Logo's disagree over how large this Square is.
UCB Turtle Logo makes this Square as large as the Window


## Play around

Plainly, we should tell you more, but what?

You're visiting here in our earliest days,
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


## Breakpoints


### Breakpoint the Server

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


### Breakpoint the Client

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

You could go ask them to learn to auto-complete your Input as strongly as we do.
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

Wiki > [Domain-specific language]([./demos/arrow-keys.logo](https://en.wikipedia.org/wiki/Domain-specific_language))
Wiki > [Greenspun's tenth rule](https://en.wikipedia.org/wiki/Greenspun%27s_tenth_rule)


### Does it work at your desk?

Our Turtle Logo runs inside more Terminals.
Their Turtle Logo runs inside a macOS Terminal, and inside ReplIt·Com.
In other places, our Turtle Logo still works,
whereas their Turtle Logo tells you things like

    ModuleNotFoundError: No module named 'tkinter'

    _tkinter.TclError: no display name and no $DISPLAY environment variable


### What kind of drawings does it make?

Our Turtle Logo draws with Character Graphics inside the Terminal.
You can copy-paste our drawings into a Google Doc, and
edit them inside the Google Doc

Their Turtle Logo draws on a Bitmap Canvas in a separate Window that's not a Terminal Window.
You can take screenshots of their drawings,
and share and edit the screenshots


## Help us please

You know you've got thoughts.
Please do speak them out loud as words

+ LinkedIn > [pelavarre](https://www.linkedin.com/in/pelavarre)<br>
+ Mastodon > [pelavarre](https://social.vivaldi.net/@pelavarre)<br>
+ Twitter > [pelavarre](https://twitter.com/intent/tweet?text=/@PELaVarre)<br>


<!-- omit in toc -->
## Copied from

Posted as:  https://github.com/pelavarre/byoverbs/blob/main/docs/turtling-in-the-python-terminal.md<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git<br>
