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
- [What comes next](#what-comes-next)
- [Choose Your Own Turtle Logo](#choose-your-own-turtle-logo)
  - [Does it work at your desk?](#does-it-work-at-your-desk)
  - [What kind of drawings does it make?](#what-kind-of-drawings-does-it-make)
- [Help us please](#help-us-please)

<!-- I'd fear people need the headings numbered, if it were just me -->
<!-- VsCode autogenerates this unnumbered Table-of-Contents. Maybe people will cope -->

GitHub posts a rendering of this Md File.
You might prefer the look of it at VsCode ⇧⌘V Markdown Open Preview



## Welcome

Welcome to our game

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
    fd rt 120  fd rt 120  fd rt 120

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


## What comes next

You're visiting while we're still rapidly rewriting what's here

Another thing that presently works is

    relaunch
    for _ in range(8): t.forward(100e0); t.right(45e0)


## Choose Your Own Turtle Logo

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
