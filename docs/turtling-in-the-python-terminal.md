<!-- omit in toc -->
# Turtling in the Python Terminal

Contents

- [Welcome](#welcome)
  - [Step 1: You start inside a Shell inside a Terminal](#step-1-you-start-inside-a-shell-inside-a-terminal)
    - [Windows](#windows)
    - [macOS](#macos)
    - [Linux](#linux)
      - [gCloud Browser Linux, or Sh TMux](#gcloud-browser-linux-or-sh-tmux)
      - [replIt Browser Linux](#replit-browser-linux)
      - [Sh Screen](#sh-screen)
  - [Step 2: You download \& run the Source Code](#step-2-you-download--run-the-source-code)
  - [Step 3: You open one Terminal Window Tab Pane for Drawing](#step-3-you-open-one-terminal-window-tab-pane-for-drawing)
  - [Step 4: You open another Terminal Window Tab Pane for Chat](#step-4-you-open-another-terminal-window-tab-pane-for-chat)
  - [You can start over expertly](#you-can-start-over-expertly)
  - [You can quit for now and start back up again later](#you-can-quit-for-now-and-start-back-up-again-later)
  - [Please believe we've gone wrong](#please-believe-weve-gone-wrong)
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
  - [Light up the Turtle](#light-up-the-turtle)
  - [Draw Circles and parts of Circles](#draw-circles-and-parts-of-circles)
  - [Draw famous Figures](#draw-famous-figures)
  - [Color by Number or Color by Words](#color-by-number-or-color-by-words)
    - [Terminal Shell Colors at gCloud Terminal Shell](#terminal-shell-colors-at-gcloud-terminal-shell)
    - [Terminal Shell Colors at replIt](#terminal-shell-colors-at-replit)
    - [Terminal Shell Colors at macOS](#terminal-shell-colors-at-macos)
  - [Edit your Drawings](#edit-your-drawings)
- [We can just try things together](#we-can-just-try-things-together)
  - [Glance through the Help Texts](#glance-through-the-help-texts)
  - [Blame me, not you, when this English is difficult to read](#blame-me-not-you-when-this-english-is-difficult-to-read)
  - [Choose your own Defaults, when you dislike ours](#choose-your-own-defaults-when-you-dislike-ours)
  - [Paste whole Files of Input](#paste-whole-files-of-input)
    - [Pasting many Whole Files more automagically, at macOS](#pasting-many-whole-files-more-automagically-at-macos)
  - [Play around](#play-around)
  - [Help sort our Wish List](#help-sort-our-wish-list)
- [Dig in technically, deep into the Python](#dig-in-technically-deep-into-the-python)
  - [25 Cross-Platform Python Imports](#25-cross-platform-python-imports)
  - [3 Linux/ macOS Imports](#3-linux-macos-imports)
  - [0 Windows Imports](#0-windows-imports)
  - [Breakpoints](#breakpoints)
    - [Breakpoint the Drawing Window](#breakpoint-the-drawing-window)
    - [Breakpoint the Chat](#breakpoint-the-chat)
- [Near Future Work](#near-future-work)
  - [Difficult Bugs](#difficult-bugs)
    - [🐢 Pong begun, but bounces poorly](#-pong-begun-but-bounces-poorly)
    - [Future Pucks](#future-pucks)
    - [Future Paddles](#future-paddles)
    - [Paste arrives slowly](#paste-arrives-slowly)
    - [Isosceles found, where Equilateral expected](#isosceles-found-where-equilateral-expected)
    - [11x11 found where 10x10 Pixels expected](#11x11-found-where-10x10-pixels-expected)
  - [Easy Bugs](#easy-bugs)
    - [🐢 Press begun, but nothing like finished](#-press-begun-but-nothing-like-finished)
    - [🐢 Write guesses wrong where the Turtle will land](#-write-guesses-wrong-where-the-turtle-will-land)
  - [Solutions for the free-of-charge tier at replIt·Com](#solutions-for-the-free-of-charge-tier-at-replitcom)
- [Try out some other Terminal Games, free of charge](#try-out-some-other-terminal-games-free-of-charge)
  - [Wump and more](#wump-and-more)
  - [Other Turtle Logos](#other-turtle-logos)
    - [Does their Turtle Logo work at your desk?](#does-their-turtle-logo-work-at-your-desk)
    - [What kind of drawings does their Turtle Logo make?](#what-kind-of-drawings-does-their-turtle-logo-make)
- [Help us please](#help-us-please)

<!-- I wish VsCode ToC would number its headings -->

<!--

Try VsCode ⇧⌘V Markdown Open Preview
to show you this Md File rendered without these words

-->


## Welcome

Welcome to our Game

**Four Steps** =>


### Step 1: You start inside a Shell inside a Terminal

You'll choose to work with
two Terminal Window Tab Panes,
or two Terminal Window Tabs, or two Terminal Windows.
You need one for Turtles to draw things, and one for you to chat with the Turtles.
We'll talk of your two Panes,
and you'll know if you find two Panes in one Tab, or in two Tabs, or in two Windows


#### Windows


If you have a Windows Terminal Shell, then please do test our Code.
Microsoft Licensing locks us out of learning to work with their Code,
same as they lock out most people.
But your Windows could soon start working too,
if you talk with us about how it's going


#### macOS

If you have a macOS Terminal, then you're already running our Code like we do.
But you'll have to upgrade to a 2021 Python 3.10 or newer,
else ask us to backport our Code farther into the past.
Apple's Licenses run sharper than Microsoft's, but I've got one for me


#### Linux

If you feel you don't have a Linux Terminal with a modern Python inside, actually you do


##### gCloud Browser Linux, or Sh TMux

You can run the 4+ GB Terminal gCloud Linux Terminal Shell
that your gMail gives you free-of-charge at

> https://shell.cloud.google.com/?show=terminal

Google gives out one Linux Terminal Shell Window per Browser.
And they keep it current, like giving you 2023 Python 3.12 in 2025

Many gCloud Shell people soon learn the Keyboard Shortcuts
for splitting one Terminal Window into Panes

| Key Chord Sequence | Meaning |
|--------------------|---------|
| ⌃B ⇧% | Add Pane > Insert Right |
| ⌃B ⇧" | Add Pane > Insert Down |
| ⌃D | Close Pane |

After you add a Pane, then
⌃B ← and ⌃B ↑ and ⌃B  → and ⌃B ↓ is how you move your Cursor between Panes.

These Keyboard Shortcuts first appeared inside the TMux Add-On for Linux Terminals,
but the gCloud Linux Terminal Shell installs these Keyboard Shortcuts by default.
Like you have to press ⌃B ⌃B twice to get Vi to know you want to page back

Apple speaks of Modifier Key Caps with the ⎋ ⌃ ⌥ ⇧ ⌘ notation

| Modifier Key | Name |
|-----|------|
| ⎋ | esc |
| ⌃ | control |
| ⌥ | option |
| ⇧ | shift |
| ⌘ | command |

When searching texts, you have to struggle.
You have to distinguish
U+005E ^ Circumflex-Accent from U+2303 ⌃ Up-Arrowhead.
People differ over which punctuation mark to speak
to mean the Modifier Key labeled as "Control" or "Ctrl" and so on
And Gnu·Org pushes a tradition that speaks of ⇧S as 'S' and S as 's'.
This push from last century still causes confusion today.
As a reader, you can't know if the writer meant
the ⇧S two-Key Chord or the S single Keystroke, when they say 'S'.


##### replIt Browser Linux

The replIt·Com Startup will lend you a Linux Terminal,
if you give them an email address.
And they keep it current, like lending you 2022 Python 3.11 in 2025.

But they soon stop you playing.
They pop suddenly, and demand you pay like US$180/year.
They trip you up like this after you leave a Terminal of theirs open for like 10 Hours

They calm down and let you back in again after like a month, people tell me.
Specifically, what Perplexity·Ai told me this in February, 2025, when I asked:
How quickly does replIt·Com hit you with "You've used up all your Development time"?
I haven't tested this claim.
The replIt people don't make it reasonably easy to keep track of what deal they're offering

The replIt people don't accurately measure if you're around or not.
Maybe you're typing on the Keyboard and moving and clicking the Mouse, maybe you're not.
Even when not,
if you have one accident of leaving a Process running then you're done for the month

The replIt people also radically change how their Panes work, from time to time.
Presently, in February of 2025,
they more push "Shell - Move existing tab here" at you.
When you need to work with two Panes,
you have to search farther to find
"Shell - Directly access your App through a command line interface (CLI)"


##### Sh Screen

If you have Sh Screen and a Linux Terminal Window,
then you can add a Vertical Split much as you do in gCloud Shell or Sh TMux,
just with different Keyboard Shortcuts

| Key Chord Sequence | Meaning |
|--------------------|---------|
| ⌃A ⇧| | Add Pane > Insert Right |
| ⌃A ⇧S | Add Pane > Insert Down |
| ⌃A Tab | Move Cursor into Next Pane |
| ⌃A C | Launch a Shell in New Pane |
| ⌃A ⇧X | Close Pane |


### Step 2: You download & run the Source Code

    curl -Ss https://raw.githubusercontent.com/pelavarre/byoverbs/refs/heads/main/bin/turtling.py >turtling.py

    wc -l turtling.py  # thousands of lines

Some security setups will block you from downloading our Code this way.
You can look for options to download our Code out where we keep it published for review:&nbsp;
GitHub > [Turtling·Py](https://github.com/pelavarre/byoverbs/blob/main/bin/turtling.py)

We've seen ⌘S work there, as meaning … > Raw File Content > Download.
Their UI misleadingly tells us ⌘⇧S works for them, but it's ⌘S that works for us, without the ⇧ Shift Modified Key

Another Shell way of Downloading is

    git clone https://github.com/pelavarre/byoverbs.git

Sadly, Raw File Content is too powerful to trust.
Even when you get it from someone you know,
still someone else could have turned it against you both, without your knowledge.
We'd be curious to hear how you chose to try our Game, all the same


### Step 3: You open one Terminal Window Tab Pane for Drawing

Inside of one Pane,
you tell our Code to move Turtles around and draw things on the Terminal Screen

    python3 turtling.py --yolo

First up, it'll tell you something like
> Drawing until you press ⌃\ here<br>


### Step 4: You open another Terminal Window Tab Pane for Chat

Inside of a second Pane,
you tell our Code to find the Turtles in your Drawing Pane and chat with you about them

    python3 turtling.py -i

First up, our Code will tell you something like
> BYO Turtling·Py 2025.2.15<br>
> Chatting with you, till you say:  bye<br>

You type out Logo or Python Instructions for your Turtles.
Or you copy-paste Instructions in from somewhere else.

Our Code takes any brief Logo Instructions you type,
and fills them out ("auto-completes" them)
to form Python Instructions, all carefully spelled and punctuated

Our Code then has only Python Instructions to deal with.
It forwards the Python into the Turtles of the Pane you opened for Drawing.
The Turtles there then follow your Instructions.
They move around and draw things and beep at you

This Doc walks you through fun tests of such Turtle Instructions


### You can start over expertly

If you want just one step to remember, you can
tell the Shells in both of your Terminal Window Tab Panes
to start up in the same way.
You always just say:&nbsp; `./turtling.py --yolo`

The second Pane figures out it arrived in second place
and runs as a Chat Pane, not as a Drawing Pane

For our Game to work, you have to start both Panes inside the same Folder.
You can tell the Shell to tell you which Folder you chose with:&nbsp; `pwd`

If you do try to run our Game from a different Folder, you'll see it say something like
> ... can't open file ... [Errno 2] No such file or directory


### You can quit for now and start back up again later

When you're done playing, you can always just shut the Windows

If you just shut Browser Windows, then that works fine.
But if you just shut Terminal Windows,
then sometimes your Terminal
will refuse to play our Game again until after your next Restart of your Op Sys.
Expert Shell people can work out
combinations of 'pwd' and 'cd' and 'ps aux |grep -i Turtl' and 'kill -9'
that will let you play again without restarting your Op Sys

### Please believe we've gone wrong

You're meeting with us here in our early days.
If you quit reading before we stop talking at you, then we've gone wrong,
for our Doc has failed you.
We'd love to have you tell us exactly how far you got before we went wrong, please


## You can just try things


### Move the Turtle

Try telling the Chat to

    fd

Our Code will guess
you typed that Logo Instruction to mean the Python Instructon 't.forward(100)'.
So we type out that Python Instruction for you,
carefully spelled and punctuated, as you can see.
You can type 'forward' to mean the same thing

    forward

Over inside your Turtle's Tab or Window,
you can see it drew a Line of 11 Squares for you.

Why 11 and not 10?
Well, I'm not sure about that.
You're meeting with us here in our early days.
We're still figuring out what it means to turtle well

You can type out the full Python yourself if you want:

    import turtling
    t = turtling.Turtle()
    t.forward(100)

Note: We define 'import turtling'.
The people at Python·Org and at PyPi·Org define only 'import turtle'

Note: We say Turtle. Some people say Sprite. Many people say Terminal Cursor


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

You might want to prepare your Instructions in some other Window and paste them in,
because our Input Line Editing doesn't work very well yet.
For now, as you type instructions, to edit what you've typed, you can try

| Key Chord | Name | Meaning |
|-----------|------------|---------|
| ⌃C | row-delete | Delete the Input Line and say KeyboardInterrupt |
| ⌃W | word-delete | Delete 1 Word at the Left of the Turtle |
| ⌃U | row-delete | Delete the Input Line |
| Delete | char-delete-left | Delete 1 Character at the Left of the Turtle |


#### Relaunch

Turtle Logo's disagree over how to speak the idea of Relaunch the Game.
Above you see we have you say Relaunch.
We'll also accept you saying just Restart when you only mostly want to start over,
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

We rely on you to make your own Terminal Windows, Tabs, & Panes.
So you make many choices for us

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
even when clashing with the Darkmode's of replIt or macOS
And it often declines to run altogether at the gCloud Terminal Shell

You choose your default Terminal Font.
Presently we guess the Pixel you want is a Square pair of U+2588 Full-Block █ █ Characters.
Lotsa of Terminal Fonts disagree over how to draw a U+2588 Full-Block █ Character.
Many Fonts agree Full-Block means paint the full horizontal width,
but lots of Terminal Fonts disagree over how much of the vertical height to paint over.
I've not yet found a Font that always says Full-Block should paint the full vertical height.
Except the default Font at replIt does paint the full vertical height

Lately I mostly test Screens of
101 Columns and 42 Rows of Andale Mono 18
in the Lightmode Basic Profile of the macOS Terminal App in Oct/2024 Sequoia macOS 15.
I've also sent out some Screenshots from the Darkmode Homebrew Profile

I'd guess most of you are working inside a free gCloud Terminal Shell.
I've also seen replIt Terminal Shells work.
I haven't tested macOS Ghostty, nor macOS iTerm2 either,
nor any of the Terminal Apps of Linux and Windows

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
    restart tada

Don't forget to press Return after the end of the last Line of your Input here

Turtle Logo's disagree over how large this Square is.
UCB Turtle Logo makes a Square from -250 -250 to 250 250 as large as their Square Window

Presently we fit a Square from -200 -200 to 200 200
plus one extra Row
into a Terminal Window of 101 Columns x 42 Rows


### Draw Animals

#### Natalia's Snake

Draw Natalia's Snake, first drawn by Natalia of Bucharest

    relaunch
    rt 180  fd 30
    lt 90  fd 10  rt 90  fd 10  bk 10
    lt 90  fd 10  lt 90  fd 30  bk 30
    rt 90  fd 5  lt 90  fd 30
    rt 90  fd 10  lt 90  fd 10  bk 10
    rt 90  fd 10  lt 90  bk 30  fd 30
    rt 90  fd 10  lt 90  fd
    rt 90  bk 15  penerase  fd 10  pd  fd 20  penerase  fd 10
    pd  fd 5  penerase  fd 5
    restart tada

<!--

Shell Commands to paste Natalia's Snake but then shift it down and right

clear
pbpaste
printf '\e[H''\e[13L''\e[39H'  # 39 of 42
bin/turtling.py --yolo  # todo: some way to say run to draw & edit, never to chat
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
    seth 0  rt 90  fd 30
    penup home
    fd 10  write '   █'
    restart tada


### Light up the Turtle

Our Turtle is too easy to lose

Sometimes it's the same Color as the Background of the Screen,
or the same Color as your Drawing in the Foreground,
or you turned it off with HideTurtle or Tada,
or you turned it off with gCloud Terminal Shell TMux ⌃B and a ← ↑ → ↓ Arrow Key,
or you didn't turn it back on with ShowTurtle

To get the Turtle to blink on and off,
you can intentionally damage and repair your Drawing.
You can tell the Turtle to draw just 1 Square Pixel underneath it without moving away, in one Color and then another Color

Like try each of these, but just one at a time. First

    Restart  PenDown  SetPenColor Red  Forward 0  Tada

And then

    Restart  PenDown  SetPenColor None  Forward 0  Tada

And then

    Restart  PenDown  SetPenColor None  Write '..'  Tada

When you try these one at a time, then you can see the changes

Myself, I'll often draft a Drawing in PenColor None,
and end by drawing just 1 Pixel in Red,
just so I can see where I left the Turtle standing


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

To draw something like the two Curves and a Line of the 1972 Atari ™ Logo, try

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

Wikipedia > [Sierpiński triangle](https://en.wikipedia.org/wiki/Sierpi%C5%84ski_triangle)<br>


### Color by Number or Color by Words

People made & sold Terminals in the 1970's and 1980's without much forethought.
They competed so fiercely, in such a rush, that they ended up
handing down Five Ways to speak of Terminal Color, down through the years to us
> 3-Bit, 4-Bit, 4.6-Bit, 8-Bit, and 24-Bit

FIVE Ways.
That's too many ways of speaking to learn well quickly,
but you can search till you find the Color Palette you need.

<!-- FIXME: Put their Color Tables/Wheels up as demos/*.logo Files -->

Try running our Color Test

    Relaunch

    Restart  Right 0    SetPenColor Red  Forward  # 3-Bit Color
    Restart  Right 15   SetPenColor Red 4  Forward  # 4-Bit Color
    Restart  Right 30   SetPenColor "FF0000" 8  Forward  # 8-Bit Color
    Restart  Right 45   SetPenColor "FF0000" 24  Forward  # 24-Bit Color

    Restart  Right 60   SetPenColor Green  Forward  # 3-Bit Color
    Restart  Right 75   SetPenColor Green 4  Forward  # 4-Bit Color
    Restart  Right 90   SetPenColor "00FF00" 8  Forward  # 8-Bit Color
    Restart  Right 105  SetPenColor "00FF00" 24  Forward  # 24-Bit Color

    Restart  Right 120  SetPenColor Blue  Forward  # 3-Bit Color
    Restart  Right 135  SetPenColor Blue 4  Forward  # 4-Bit Color
    Restart  Right 150  SetPenColor "0000FF" 8  Forward  # 8-Bit Color
    Restart  Right 165  SetPenColor "0000FF" 24  Forward  # 24-Bit Color

    Restart  Right 180  SetPenColor 0 4.6  Forward  # 25-Step Grayscale
    Restart  Right 195  SetPenColor 8 4.6  Forward
    Restart  Right 210  SetPenColor 16 4.6  Forward

    Restart  Right 90
    SetPenColor 24 4.6  Arc 45  SetPenColor "802B00" 8  Arc  45
    SetPenColor 24 4.6  Arc 45  SetPenColor "802B00" 8  Arc  45

    Restart Tada

Our Color Test here tries out all Five Ways of speaking of Terminal Color

<!--

There are also many more,
less concrete, more abstract, non-specific Ways of speaking of Terminal Color,
beyond the five specific concrete Ways of speaking of Terminal Color,

-->

<!--

SetPenColor 1 4 and SetPenColor 9 4 are the Red's of 4-Bit Color

We choose the same Control Escape Sequence for 9 4 as for 1 3,
as you can see if you try those.
So every test of SetPenColor 9 4 gives the same results as for SetPenColor 1 3,
so we don't test SetPenColor 9 4 here

Ironically, our first shipping revision of SetPenColor 9 4 got this wrong.
But we fixed it a week later.  : -)

-->

This drawing comes out differently on different Terminals.
Because the people who make the Terminals have been arguing for fifty years,
without talking well enough
to come into full agreement about which Color Code means which Color.
Let's hope the younger people can do better

> You can search till you find the Color Palette you need.

Please do tell us how easy or hard your search for a Color Palette was?
We'd like to dream up stronger ways of helping you,
like we could draw out examples of Terminal Color Palettes
that look like the Wikipedia ANSI Escape Codes,
or the Hue/ Saturation/ Brightness Sliders of MIT Scratch Logo


#### Terminal Shell Colors at gCloud Terminal Shell

When you run our Color Test in a gCloud Terminal Shell,
they give you 1 Red, 2 Green's, and 2'Blue's.
Who knows why

All the same, you can search through their 8-Bit Colors,
or through their 24-Bit Colors,
till you find the Color Palette you need


#### Terminal Shell Colors at replIt

When you run our Color Test in a replIt Terminal,
they give you 3 Red's, 3 Green's, and 3 Blue's.
In this way, they make it easy to guess
which 8-Bit Colors are the same as which 24-Bit Colors

You can search through their 8-Bit Colors,
or through their 24-Bit Colors,
till you find the Color Palette you need


#### Terminal Shell Colors at macOS

When you run our Color Test in an Apple macOS Terminal,
they give you 2 different Reds, 2 different Greens, and 2 different Blues.
Their 2 different Blues really are different, but it's hard to see their difference,
they are almost the same.

macOS gives you no 24-Bit Colors.
macOS gives you a slap across the face when you ask for 24-Bit Colors

Specifically,
macOS runs ahead to mistake any 24-Bit Color as calling for Uncolored Plain Text.
This comes out as Black on a Lightmode Basic Profile,
as bright Green on a Darkmode Homebrew Profile,
and so on.
Consequently,
you cannot draw the same Drawing outside of macOS and inside of macOS,
not unless you think ahead to give up on 24-Bit Colors

To help you with this,
we'll round off a 24-Bit Html Color to a 8-Bit macOS Color, if you ask

    Relaunch

    Restart  Right 30   SetPenColor "FF0000" 8  Forward
    Restart  Right 90   SetPenColor "00FF00" 8  Forward
    Restart  Right 150  SetPenColor "0000FF" 8  Forward

    Restart Tada

We'll also let you ask for the closest Color to a 24-Bit Color.
At the gCloud or replit Linux Terminal Shells, you'll get the 24-Bit Color you asked for.
At macOS, you'll settle for the closest 8-Bit Color

    Relaunch

    Restart  Right 30   SetPenColor "FF0000" 8  Forward
    Restart  Right 40   SetPenColor "C04000"    Forward  # settle for closest
    Restart  Right 90   SetPenColor "00FF00" 8  Forward
    Restart  Right 100  SetPenColor "00C040"    Forward  # settle for closest
    Restart  Right 150  SetPenColor "0000FF" 8  Forward
    Restart  Right 160  SetPenColor "4000C0"    Forward  # settle for closest

    Restart Tada

<!--

Our work to round off 24-Bit Colors to 8-Bit Colors
is simple-mind'ed Python: 'int(hh * 6 / 0x100)'.
It'd be good if we could find Color People to tell us how wrong or correct we are.

-->


<!--

### Explore More Colors

#### 3-Bit Color

The most classic most basic Colors of a Sh Terminal
are the eight Named and Numbered Colors of the 3-Bit Tradition

    setpc white  # 7
    setpc magenta  # 5
    setpc blue  # 4
    setpc cyan  # 6
    setpc green  # 2
    setpc yellow  # 3
    setpc red  # 1
    setpc black  # 0

The 3-Bit Tradition doesn't number these Colors like a Rainbow,
to fit with the traditions of Physicists and Electronic Engineers.
The 3-Bit Tradition more numbers these Colors like Business People in the West speak of colors.
Black is most basic. Red is lots of alarm. Yellow is less alarm. Green is good.
Cyan and Blue and Magenta are variations. White is bright

These eight Named Colors look something like
the most extreme Red/ Green/ Blue mixes of the Html 24-Bit Colors

    Relaunch

    Restart  Right 0    SetPenColor 'FFffFF'  Forward  # White = Red + Green + Blue
    Restart  Right 15    SetPenColor 'FF80FF'  Forward
    Restart  Right 30   SetPenColor 'FF00FF'  Forward  # Magenta = Red + Blue
    Restart  Right 45   SetPenColor '8000FF'  Forward
    Restart  Right 60   SetPenColor '0000FF'  Forward  # Blue
    Restart  Right 75   SetPenColor '0080FF'  Forward
    Restart  Right 90   SetPenColor '00FFFF'  Forward  # Cyan = Green + Blue
    Restart  Right 105  SetPenColor '00FF80'  Forward

    Restart  Right 120  SetPenColor '00FF00'  Forward  # Green
    Restart  Right 135  SetPenColor '80FF00'  Forward
    Restart  Right 150  SetPenColor 'FFFF00'  Forward  # Yellow = Red + Green
    Restart  Right 165  SetPenColor 'FF8000'  Forward
    Restart  Right 180  SetPenColor 'FF0000'  Forward  # Red
    Restart  Right 195  SetPenColor '800000'  Forward
    Restart  Right 210  SetPenColor '000000'  Forward  # Black
    Restart  Right 225s  SetPenColor '808080'  Forward

Presently, Commands like these don't work if you mix
a ) the conventional Html '#' Hash Mark inside the two ' Quote Marks
b ) a trailing # Comment on the Command

Tell us that Bug of ours bothers you, and we'll fix it sooner

When you don't explicitly spell out your choice of Accent to speak with Color,
you get our default, often 8 or 24.
If you dislike our default, please tell us.
We're trying to guess what Accent works best for you in your Terminal


#### Explore 3-Bit, 4-Bit, and 8-Bit Color by Number

You can call for Terminal Colors as above, or
you can cast more arcane, fiddly, intricate Color Spells such as

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

    write '\e[38;5;130m'  # Orange  # SetPenColor "802B00" 8

#### Explore 24-Bit Color in the Cloud

Searching with ⌘F 31 will show you
Wikipedia People talking of ESC[31m, as we did above

Searching instead with ⌘F 38; will show you
Wikipedia People talking of "Select RGB foreground color"
from a choice of more than 16 million "24-bit" Colors

For example, inside of a gCloud Terminal Shell, try

    write '\e[38;5;196m Red \e[38;2;255;0;0m Red \e[m'
    write '\e[38;5;46m Green \e[38;2;0;255;0m Green \e[m'
    write '\e[38;5;21m Blue \e[38;2;0;0;255m Blue \e[m'

These 24-bit Colors work at gCloud and at replIt.
They do Not work inside a macOS Shell.
Apple rudely mistakes the 38;2 ask for 24-bit Color as canceling the 38;5 ask for 8-bit Color.
You can't ask for 8-bit and ask for 24-bit and settle for what you get, not with Apple around.
You have to discover what to ask for

Perplexity·Ai tells me this limitation is famous.
This limitation drives people to swap in other Terminals for the default macOS Terminal App from Apple.
Such as macOS Ghostty or macOS iTerm2


#### Explore 8-Bit Color at macOS

There's a world of Colors out there, and I don't yet know it well.
One of the websites talking of Sh Terminal Colors is

Wikipedia > [ANSI escape code](https://en.wikipedia.org/wiki/ANSI_escape_code)

Searching with ⌘F 31 will show you Wikipedia People talking of ESC[31m, as we did above

My experiments tell me that macOS Terminals only do the "8-bit" Color of "256-color lookup tables". For example, this experiment works

    relaunch
    write '\e[38;5;4m'  # Darker Purple
    fd 50  bk 50  rt 30
    write '\e[38;5;5m'  # Darker Pink
    fd 50  bk 50  rt 30
    write '\e[38;5;12m'  # Purple
    fd 50  bk 50  rt 30
    write '\e[38;5;13m'  # Lighter Pink
    fd 50  bk 50  rt 30
    write '\e[38;5;40m'  # Darker Green
    fd 50  bk 50  rt 30
    write '\e[38;5;80m'  # Lighter Blue Green
    fd 50  bk 50  rt 30
    write '\e[38;5;120m'  # Lighter Green
    fd 50  bk 50  rt 30
    write '\e[38;5;160m'  # Red
    fd 50  bk 50  rt 30
    write '\e[38;5;200m'  # Much the Same Pink
    fd 50  bk 50  rt 30
    write '\e[38;5;241m'  # Darker Gray
    fd 50  bk 50  rt 30
    write '\e[38;5;249m'  # Lighter Gray
    fd 50  bk 50  rt 30
    setpc none  penup  home
    tada

Wikipedia People tell us these '38;5' Color Numbers carry a meaning like so

    0-  7:  standard colors (as in ESC [ 30–37 m)
    8- 15:  high intensity colors (as in ESC [ 90–97 m)
    16-231:  6 × 6 × 6 cube (216 colors): 16 + 36 × r + 6 × g + b (0 ≤ r, g, b ≤ 5)
    232-255:  grayscale from dark to light in 24 steps

And the Undo for \\e m Settings of the Terminal is

    write '\e[m'  # Plain Text, Uncolored

-->

<!-- FIXME: no quotes needed for \e without Spaces -->


### Edit your Drawings

You can edit your Drawings with the Keyboard Shortcuts that the Terminal itself understands

Odds on your ⎋ ⌃ ⌥ ⇧ ⌘ Keys have letters printed on them: esc, control, option, shift, command

Forwarding what the Keyboard says straight into the Terminal Screen can work.
These Keyboard Shortcuts work like that

| Key Chord | Name | Meaning |
|-----------|------------|---------|
| ← | column-go-left | Move Left by one Column |
| ↑ | row-go-up | Move Up by 1 Row |
| ↓ | row-go-down | Move Down by 1 Row |
| → | column-go-right | Move Right by one Column |
| Tab | tab-go-right | Move far Right, to next Tab Stop |
| ⇧Tab | tab-go-left | Move far Left, to next Tab Stop |

When you learn to type the ⎋ Esc Key, then
you can try feeding more of the Keyboard into the Screen.
These can work, but they're more difficult to make work.
For these to work,
you have to type each Key in less than 1 Second after the previous Key

| Key Chord | Name | Meaning |
|-----------|------------|---------|
| ⎋8 | cursor-revert | Jump to far Upper Left, or to last ⎋7 |
| ⎋7 | cursor-checkpoint | Tell ⎋8 where to go |
| ⎋[⇧P | chars-delete | Delete the 1 Character beneath the Turtle |
| ⎋[⇧@ | chars-insert | Slide the Characters past the Turtle to the right by 1 Column |
| ⎋[⇧M | rows-delete | Lift the Rows below the Turtle up by 1 Row |
| ⎋[⇧L | rows-insert | Push the Rows below the Turtle down by 1 Row |
| ⎋['⇧~ | cols-delete | Slide the Columns past the Turtle to the left by 1 Column |
| ⎋['⇧} | cols-insert | Slide the Columns past the Turtle to the right by 1 Column |

You can also learn to type decimal Digits in the middle of these Escape Control Sequences,
immediately after the [ Left-Square-Bracket.
That change makes these Instructions lots more powerful

| Key Chord | Name | Meaning |
|-----------|------------|---------|
| ⎋[321⇧D | ← Left Arrow | Move the Turtle to the left by 321 Columns, but stop at left edge of Screen |
| ⎋[321⇧A | ↑ Up Arrow | Move the Turtle up by 321 Rows, but stop at top edge of Screen |
| ⎋[321⇧C | → Right Arrow | Move the Turtle to the right by 321 Columns, but stop at right edge of Screen |
| ⎋[321⇧B | ↓ Down Arrow | Move the Turtle down by 321 Rows, but stop at bottom edge of Screen |

You can also learn to type the macOS Keyboard Shortcuts.
These came into Linux as Emacs Keyboard Shortcuts, so they do mostly work there too.
However, gCloud Terminal Shell takes ⌃B as a TMux Keyboard Shortcut, so out there
you have to press ← or press ⌃B ⌃B twice
to mean you're asking to move the Turtle left by 1 Column

| Key Chord | Name | Meaning |
|-----------|------------|---------|
| ⌃A | column-go-leftmost | Go to the leftmost Column of Row |
| ⌃B | column-go-left | Go to the Column at Left of the Turtle |
| ⌃F | column-go-right | Go to the Character at Right of the Turtle |
| ⌃G | alarm-ring | Ring the Terminal Bell |
| ⌃N | row-go-down | Move as if you pressed the ↓ Down Arrow |
| ⌃P | row-go-up | Move as if you pressed the ↑ Up Arrow |

Editing your Drawings like this today
doesn't write the Logo Code that would make the same edits.
We could come fix that. Just ask us


<!--

We need to write down for us how much works where.
Here we tell you what we've seen work somewhere,
but we've lost track of was it working in macOS or gCloud or replIt or what

-->


<!--

Some of the editing Keys of the Keyboard will mostly work as you expect

| Delete | char-delete-left | Delete 1 Character at the Left of the Turtle |
| Return | row-insert-go-below | Insert a Row below this Row and move into it |

with some of the same Keyboard Shortcuts
that a macOS Note or Terminal Emacs understands

The most ordinary editing macOS/ Emacs Key Chords will mostly work too

| Key Chord | Name | Meaning |
|-----------|------|---------|
| ⌃D | char-delete-right | Delete 1 Character at Right (like a Windows Delete) |
| ⌃H | char-delete-left | Delete 1 Character at Left (same as if pressing Delete) |
| ⌃K | row-tail-delete | Delete all the Characters at or to the Right of the Turtle |
| ⌃O | row-insert-below | Insert a Row below this Row |
| ⌃Y | chars-undelete | Paste back in the chars you deleted with ⌃K |

Presently, a few of these Key Chords don't work as well as you might expect

Mainly, because our Turtles don't know what's on Screen.
The Security Design of the Terminal blocks the Turtles
from knowing what came on Screen before they were born.
And the Turtles we have today forget even the Characters they drew themselves,
and then they don't know anything

So our ⌃K today only erases the Characters at and to the Right.
It only deletes the Row when you press it twice in the leftmost Column,
because only then can it know that there are no more Characters to the Right.
And ⌃Y can't give you back what ⌃K erased, because it doesn't know what it erased

Similarly, ⌃O moves you to the leftmost Column when you hit it somewhere else.
Only when you try ⌃O in the leftmost Column do you see it insert a new Row.
And same deal with Return as with ⌃O.

I also fear we can't make the ⌃B work reliably.
gCloud Shell grabs that Key Chord to operate a TMux Split of the Tab
for ⌃B ⇧%, ⌃B ⇧", ⌃B ↓, ⌃B ↑, ⌃B X. etc.
We could grab that Key Chord to operate a TMux Split of the Tab someday too,
just to make our Turtle Logo look & feel alike in more places

-->


## We can just try things together

Could our Game ever earn a place alongside /usr/games/wump in Linux?
Could our Game Engine become the standard Engine to fall back on,
when complexities of TkInter blocks 'import turtle' from working?

Those would be fun stunts. Want to help us get there?


### Glance through the Help Texts

Asking for help can damage your Drawing on Screen,
so don't ask until you're ok with that limitation

To see all our Turtle Verbs listed, try

    help(t)

The Help appears in the Pane where the Turtles draw things,
not the Pane where you typed out 'help(t)' to ask for the Help.
When you're done reading the Help, press Q to see your Drawings again.
Press Spacebar before Q if you want to see more Screenfuls of the Help

You'll see our Help suggests you play around

It suggest you try speaking the Command Verbs it knows:
Arc, Backward, Beep, Breakout, Bye,
ClearScreen, Defaults,
Forward,
H, HideTurtle, Home,
IncX, IncY, IsDown, IsVisible,
Label, Left,
PenDown, PenErase, PenUp, Pong, Press,
Relaunch, Repaint, Repeat, Restart, Right,
SetHeading, SetHertz, SetPenColor, SetPenPunch, SetX, SetXY, SetXYZoom, SetY,
ShowTurtle, Sierpiński, Sleep,
Tada,
and Write

It suggest you try speaking the Nouns it knows:
glass_teletype, heading, hiding,
namespace, penmark, penscapes, rest, warping, xfloat, xscale, yfloat, yscale.
These kind of do work if you mark them up with a 't.' in front

    t.xfloat, t.yfloat

These Nouns let you peek at the internal details of the Turtle.
How they work might change a lot, as we keep developing our idea of how to turtle well

A quicker way to see all this suggested more briefly is

    dir(t)

Try

    help(t.forward)

You'll see Python telling you that our Forward Verb takes a Keyword Argument named:  distance

<!-- FIXME: help(t) also lists the Fields of t -->
<!-- FIXME: Help doesn't cite itself as a choice -->
<!-- FIXME: Can we hide t._breakpoint_, t._exec_, t._mode_ from dir(t)? -->



### Blame me, not you, when this English is difficult to read

You may believe this Doc is written in the English of Computer Engineers

You're not completely wrong.
But my English is famously difficult to read.
People often struggle to get my meaning from my first writing

Let's make it better?
Tell me some piece of this English doesn't just make sense, and then
Claude·Ai & I will go work on rewriting it.
We can make its meaning come across
more clearly and accurately, while still brief

Meanwhile, me, I delight in my own failures to understand your English, first try.
Like so =>

> Part of the value of being oblique, done properly, is that you
> challenge the reader to piece together the meaning themselves.
> This is vastly superior to them taking an answer at face-value, with no depth or nuance,
> in a way that can be worse than having no answer at all
>
> ~ Twitter > Visakan Veerasamy (@visakanv),

And before him

> Tell all the truth but tell it slant —<br>
> Success in Circuit lies<br>
> Too bright for our infirm Delight<br>
> The Truth's superb surprise<br>
> As Lightning to the Children eased<br>
> With explanation kind<br>
> The Truth must dazzle gradually<br>
> Or every man be blind —<br>
>
> ~ Emily Dickinson 1830..1886

<!-- todo: Code those two — more plainly as U+2014 Em-Dash-->


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

Python itself objects if you explicitly try to say:&nbsp; t.left.angle = 90

It will sayAttributeError: 'method' object has no ...
So we round off the 'lt.a = 90' that you say to become 'left_angle = 90'
and we tell our 't.left' to watch for you having said that

Presently, to see all that we abbreviate for you, you can try

    h
    defaults

To remember what defaults you've chosen yourself, you can look at things like

    dir()

    locals()

    distance
    left_angle

To undo your choices of alt defaults, you can try

    del distance
    del left_angle
    dir()

These works of Dir and Del and Locals and so on
are standard, arcane, intricate Python ways of speaking.
They work without us pouring any special effort into making them work

I'd guess I'll soon make lots of the defaults cyclic.
Like when you ask for SetPenColor None then we'll give you back how we started,
but every time you ask for SetPenColor without picking a Color,
then we give you the next Color of the Rainbow


### Paste whole Files of Input

You can paste larger Turtle Logo Programs
into the '🐢? ' Prompt of the Chat Window.
We've not yet worked up a great way to make them more available to you,
but they are posted out there

You can paste one or all of

| File Name | Purpose |
| --------- | ------- |
| [demos/arrow-keys.logo](../demos/headings.logo) | Draw the four Arrow keys of a MacBook Keyboard |
| [demos/bkboxbox.logo](../demos/bkboxbox.logo) | Draw two boxes, one inside the other, anti-clockwise |
| [demos/fdboxbox.logo](../demos/fdboxbox.logo) | Draw two boxes, one inside the other clockwise |
| [demos/headings.logo](../demos/headings.logo) | Draw Lines of 30°, 45°, 60°, and 90° in each of the four Quadrants |
| [demos/like-a-rainbow.logo](../demos/like-a-rainbow.logo) | Draw something like concentric circles, but with personal flair |
| [demos/mtm-titlecard.logo](../demos/mtm-titlecard.logo) | Draw something like the "Mary Tyler Moore" Title Card, from Sep/1970 |
| [demos/rainbow.logo](../demos/rainbow.logo) | Draw concentric circles, plotted by machine |
| [demos/wikipedia-colors.logo](../demos/wikipedia-colors.logo) | Draw a chart like the Wikipedia Ansi Escape Codes Color Chart |
| [demos/xyplotter.logo](../demos/xyplotter.logo) | Draw a Parabola, twice, accelerating as it goes right, decelerating as it goes left |

To try each of these in turn,
you can open them up, one at a time, and paste them into your chat with the Turtles

Our 'wikipedia-colors.logo' doesn't work beautifully well yet,
but at least it does show you each of the 8-Bit Color Codes separately.
You can quickly pick through them by eye
to copy out the Color Codes you need to gather, to form the Color Palette you need


#### Pasting many Whole Files more automagically, at macOS

At macOS, we know how to write Python to work with the Os-Copy/Paste-Clipboard.
At macOS, you can open up a third Terminal Window to work with the Sh,
and push them into the Clipboard together, one at a time

    for F in demos/*.logo; do echo; (set -xe; cat $F |pbcopy); read; done

That macOS Sh Script does the ⌘C Copy into your Os-Copy/Paste-Clipboard for you,
over and over again, when it calls '|pbcopy'.
But you have to do the ⌘V Paste part yourself,
back into your second Terminal Window,
where you've left the "🐢?" Turtle Chat going.
And then you have to come back to your Sh Window
and press Return to get the next one going.
Or you press ⌃C if you want to stop before trying them all

Your macOS Sh Window can also try them all together, one after another

    cat demos/*.logo |sed 's,tada,ht sleep 1 st,' |pq

**Links**

Wikipedia > [ANSI escape code](https://en.wikipedia.org/wiki/ANSI_escape_code)<br>


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

<!--  pu  setxy -250 -10  pd  -->

You hit the edges of the Screen and distort the drawing, when you make it too large.
Like when you're drawing on the 101x42 Columns and Rows of my Terminal,
it'll be too large if you choose a Repeat_Count of 8 or more,
or if you choose a Forward_Distance of 153 or more

    relaunch  rep 8

    relaunch  rep 5 360 160

Turtle Logo's disagree over how to move and draw across the edges of the Screen

Some Turtle Logos will wrap the Turtle at the edges,
rather than insisting that you always center your drawings yourself.
As an example of more centering a drawing yourself,
you can Relaunch, but then go into the Drawing Window and press Return,
before the Count = and For.
That way, you can draw Count as large as 10 in my Terminal today

    rep 10

If you watch for it, you can see
our Chat Window prints "Snap" Messages when your drawing grows too large,
such that we clip and distort it

    rep 11

For such Messages coming back from the Turtle to make the most sense,
you'll want to see them in real-time.
If you try 'sleep 0' after you press Return, before the Count = and For,
then you'll see the Note on you having pressed Return pops up then.
To do this more easily and quickly, you can press S and Return to try a very short sleep.
That works a little less directly,
by sleeping as long as the last 🐢 SetHertz said to sleep


### Help sort our Wish List

Have you found a deal-breaker that's shutting you out somehow,
stopping you from playing this Game some more?

Tell us what it is?

Like we could give this Game a more game-like feel,
if we completed a full Python Command every time you pressed a Key inside the Drawing Window.
Or we could rewrite our Arrow Keys Demo to have 4 Turtles draw it, not just 1.
Or we could figure out how to show the Turtle
even after you split a gCloud Shell Tab
with ⌃B ⇧" and then moved the Turtle between Splits with ⌃B ↑ and  ⌃B ↓.
The replIt Shell has much the same disappear-the-Turtle bug,
if you do run the replIt Turtle and the Chat in separate Browser Windows.
gCloud Shell can't do separate Windows inside the same Browser

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

It mixes together 28 Python Imports

### 25 Cross-Platform Python Imports

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
> import platform<br>
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


#### Breakpoint the Drawing Window

To halt the Drawing and open it up inside the Pdb Python Debugger, try

    🐢? breakpoint

We'll run that as

    >>> t.breakpoint()

And then it works, over in the Pane where the Turtles draw things

To quit a Pdb Debugging Session, you press C and then Return.
To get help with the Pdb language, you press H and then Return.
I'd vote you learn the P command early,
that being their quick way for you to say Print Repr
that even works with single-letter variable names

If you shove hard enough,
then you can instead test '🐢? breakpoint(); pass'
which is '>>> breakpoint(); pass'
which is a less helpful thing,
because it runs inside 'tty.setraw'
which is practically never what you want


#### Breakpoint the Chat

Caution: Hey, this doesn't work. Too many people want ⌃C to mean ⌘C Edit > Copy.
We need to think about this some.
Please feel free to mention it to us

To halt the Chatting and open it up inside the Pdb Python Debugger, press

    ⌃C

By the default choices of Python itself, that works only once per Process Launch.
But we've patched it up so it'll work even as you test it again and again

If you have a habit of pressing ⌃C to mean ⌃U Discard Input Line,
that habit won't work here,
but ⌃U will work


## Near Future Work


### Difficult Bugs


#### 🐢 Pong begun, but bounces poorly

Lately I told my Shell

    cat demos/arrow-keys.logo |pbcopy

Then I pasted those Logo instructions into our Turtle App.
Then I added some more Logo instructions

    penup  fd 30  rt 90  fd 100  pendown
    setpc blue
    seth  right 45

    pong

This experiment draws the Key Caps of the ← ↑ ↓ → Arrow Keys with no Color,
and then bounces a blue Pong Puck around for a short while

I feel like this experiment pretty much works now?

1

Maybe next up is tweaking up the physics.
Like stop bouncing always only exactly 180° onto your backtrail.
And leave the Puck moving for longer, but slow it down with friction.
And teach the Arrow Keys to push and turn the Pong Puck

2

The logic isn't quite right.
Calling Pong like this sends us back some "Note: Snap" complaints.
So something somewhere isn't predicting the Turtle movement perfectly

3

And we could come make this experiment easier to run.
To get it going, we could let you say something like

    demos.arrow_keys

Presently, that doesn't work. It says:  NameError: name 'demos' is not defined

4

The free ReplIt Tier runs this Pong Puck so slowly that you can see it blink.
Maybe that's fun, or maybe so slow is no fun?
I'd be curious to hear if the paid ReplIt Tiers run this Puck better?


#### Future Pucks

What we've got started on there is that
we might next figure out how to add Pong and Breakout Pucks

When you add a Pong Puck,
it slides around,
in between the things you have told Turtles to draw.
It bounces off of them

The Breakout Puck looks much the same,
but it erases the parts of the drawing that it bumps into.
Leave it running for long enough, and it'll erase all of your drawing

You can add more than one Puck


#### Future Paddles

We might next figure out how to add Pong and Breakout Paddles

While you add no Paddle,
you can press the ← ↑ → ↓ Keys to push the Puck in a different direction

When you add more than one Paddle,
then pressing A S D F moves the Left Paddle,
whereas pressing H J K L moves the Right Paddle




#### Paste arrives slowly

In the Drawing Pane,
typing on the Keyboard goes lots faster than pasting the same Characters.
I must have written some silly Code somewhere, I wish I knew where


#### Isosceles found, where Equilateral expected

Can we make our Arrow Keys Demo
come out with triangles that are enough more equilateral?
Presently we get 10.5 X by 11 Y for Left and Right,
vs 13 X by 11 Y for Up or Down.


#### 11x11 found where 10x10 Pixels expected

These instructions

    relaunch
    fd 100
    restart setpc red  rt 90  fd 100
    setpc blue

paint 11x11 Pixels, not 10x10 Pixels

    0  ██
    9  ██
    8  ██
    7  ██
    6  ██
    5  ██
    4  ██
    3  ██
    2  ██
    1  ██
    0  ██████████████████████

       0 1 2 3 4 5 6 7 8 9 0

I feel surprised, I feel disconcerted, by 11 != 10

FD 90 in place oF FD 100 gives us 10x10.
Is this all as it should be, or should we go mess with it?

FD 0 shows the Pixel where you started.
FD 100 shows the Pixel where you ended, and all the Pixels in between.
That's how you end up with 11, not just 10, Pixels altogether

You can choose SetXYZoom 0.909 0.909
as a way of getting FD RT FD RT FD RT FD RT
to mean a Square of 10 Pixels per Side


### Easy Bugs


#### 🐢 Press begun, but nothing like finished

Presently ...

You can speak Logo to tell the Chat to press Keyboard Chord Sequences in the Drawing Pane

    relaunch
    press "⎋8"  # cursor-revert
    rt 90  label '12345678901234567890'
    restart

But you can only send Printable Ascii as itself or preceded by the "⎋" Esc Key.
Lots of Keyboard Chord Sequences don't work

    press "Tab"
    press "⇧Tab"
    press "←"

You have to fall back to encoding the Bytes yourself

    write "\t"  # Tab
    write "\e[Z"  # ⇧Tab
    write "\e[D"  # ←


#### 🐢 Write guesses wrong where the Turtle will land

Presently ...

Control Sequences like "\\r" and "\\n" and so on
do move the Turtle conventionally,
but our Code for 🐢 Write
always guesses the Turtle won't move,
which is laughably wrong


### Solutions for the free-of-charge tier at replIt·Com

The merciless copy-restriction locks at replit·Com
often do slow you down and kick you out without explanation

Well, we can pour time into reverse-engineering what it is that they want

Like maybe they don't run so slow if we retune the timeouts on our 'select.select' calls

Like maybe they don't randomly kick you out for a month if we figure out
how to never run more than two Processes accidentally,
or how to limit the run time of our every Process

Like maybe they'll let you back in if you register a series of email addresses
> jqdoe@gmail.com+1<br>
> jqdoe@gmail.com+2<br>
> jqdoe@gmail.com+3<br>

We'll see


## Try out some other Terminal Games, free of charge

### Wump and more

Before Linux, there was Unix, and people published Games for the Terminal as Open-Source

At gCloud Shell you can try

    sudo apt-get update && sudo apt-get install -y bsdgames
    ls /usr/games
    /usr/games/wump

At replIt Shell you can try

    nix-shell -p bsdgames --run wump

At gCloud Shell, you'll see they suggest you try all of
> adventure atc battlestar caesar cfscores dab gomoku hangman primes<br>
> rot13 snake teachgammon trek wtf arithmetic backgammon bsdgames-adventure<br>
> canfield cribbage go-fish hack pom robots sail snscore tetris-bsd<br>
> worm wump<br>

Tell us what you like?

### Other Turtle Logos

You can try these same tests inside other Turtle Logo Apps

In particular, adding Python into macOS lets you try

    python3 -i -c ''

    import turtle
    turtle.mode("Logo")

    t = turtle.Turtle()

    t.forward(100)
    t.right(45)

This Import Turtle demo runs just as well for me in Window Tab Panes of ReplIt,
but they force those Terminals to run stunningly slow,
and even turn them off for a month,
unless you pay money

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
I can only hope we'll scrub more bugs out of it, and even make it as fast as Python

**Links**

Docs·Python·Org > Import [turtle — Turtle Graphics](https://docs.python.org/3/library/turtle.html)<br>

Mit·Edu [Scratch](https://scratch.mit.edu) Programming Language - Draw Logo-Like Programs that draw Logo-Like Turtle Graphics, if you Add Extension > Pen = Draw with your sprites

Wikipedia > [Domain-specific language]([./demos/arrow-keys.logo](https://en.wikipedia.org/wiki/Domain-specific_language))<br>
Wikipedia > [Greenspun's tenth rule](https://en.wikipedia.org/wiki/Greenspun%27s_tenth_rule)<br>


#### Does their Turtle Logo work at your desk?

Our Turtle Logo runs inside more Terminals
> gMail gCloud Shell @ https://shell.cloud.google.com/?show=terminal<br>
> macOS Terminal Shell<br>
> replIt Shell @ https://replit.com<br>

Their Turtle Logo runs inside a macOS Terminal, and inside a ReplIt Shell

In other places, such as gCloud Shell, our Turtle Logo still works,
whereas their Turtle Logo gives you problems to solve, like
> ModuleNotFoundError: No module named 'tkinter'<br>
> _tkinter.TclError: no display name and no $DISPLAY environment variable<br>


#### What kind of drawings does their Turtle Logo make?

Their Turtle Logo draws on a Bitmap Canvas in a separate Window that's not a Terminal Window.
You can take screenshots of their drawings,
and share and edit the screenshots

Our Turtle Logo draws with Character Graphics inside the Terminal.
You can copy-paste our drawings into a Google Doc (gDoc), and
edit them inside the Google Doc.
At a macOS Terminal, you can copy Characters,
such as a Square pair of U+2588 Full-Block █ █ Characters.
But your Font choice
will say how much of the vertical height the Full-Block should paint over.
I've not yet found a Font that always says Full-Block should paint the full vertical height

Copying from a Landscape Terminal into gDoc
works better if you choose gDoc > File > Page Setup > Orientation = Landscape,
to replace their default choice of Portrait Orientation

Copying Foreground and Background Color
into gDoc from macOS Terminal mostly works.
Copying from gCloud Shell or replIt copies the Characters well, but loses all the Color.
Copying Reverse Color even from macOS Terminal loses that part of the Color

To save our Drawings entirely inside the Terminal,
you can record and replay our Drawings
with the Shell 'screen' command.
But that kind of recording loses variations in Speed,
it redraws the Drawings at near infinite speed,
so you lose the animation effects

Our pixels look large and square by default,
but you can mess with that,
by changing the size of your Terminal Window Pane and its Font


## Help us please

Please speak your thoughts out loud as words to someone.
To us, if possible

+ LinkedIn > [pelavarre](https://www.linkedin.com/in/pelavarre)<br>
+ Mastodon > [pelavarre](https://social.vivaldi.net/@pelavarre)<br>
+ Twitter > [pelavarre](https://twitter.com/intent/tweet?text=/@PELaVarre)<br>

Please also thank our people for their efforts, if you catch the chance

**Thank-you's from us, in January, 2025**

Georgiana of Bucharest!
She put the Terminal Window Tab Panes of gCloud Shell
forward as the most available Linux Hosts

Natalia of Bucharest!
She drew our first Animal, her Snake.
She was first to draw with Half-Pixel's,
and the first to erase Half-Pixel's and Whole-Pixel's

Tina of Monterey!
She drew our first Giraffe


<!-- omit in toc -->
## Copied from

Posted as:  https://github.com/pelavarre/byoverbs/blob/main/docs/turtling-in-the-python-terminal.md<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git<br>
