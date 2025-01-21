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
    - [Light up the Turtle](#light-up-the-turtle)
  - [Draw Circles and parts of Circles](#draw-circles-and-parts-of-circles)
  - [Explore More Colors](#explore-more-colors)
    - [3-Bit Color](#3-bit-color)
    - [Explore 3-Bit, 4-Bit, and 8-Bit Color by Number](#explore-3-bit-4-bit-and-8-bit-color-by-number)
    - [Explore 24-Bit Color in the Cloud](#explore-24-bit-color-in-the-cloud)
    - [Explore 8-Bit Color at macOS](#explore-8-bit-color-at-macos)
  - [Draw famous Figures](#draw-famous-figures)
  - [Edit your Drawings](#edit-your-drawings)
- [We can just try things](#we-can-just-try-things)
  - [Glance through the Help Texts](#glance-through-the-help-texts)
  - [Blame me, not you, when this English is difficult to read](#blame-me-not-you-when-this-english-is-difficult-to-read)
  - [Choose your own Defaults, when you dislike ours](#choose-your-own-defaults-when-you-dislike-ours)
  - [Paste whole Files of Input](#paste-whole-files-of-input)
  - [Play around](#play-around)
  - [Help sort our Wish List](#help-sort-our-wish-list)
- [Dig in technically, deep into the Python](#dig-in-technically-deep-into-the-python)
  - [24 Cross-Platform Python Imports](#24-cross-platform-python-imports)
  - [3 Linux/ macOS Imports](#3-linux-macos-imports)
  - [0 Windows Imports](#0-windows-imports)
  - [Breakpoints](#breakpoints)
    - [Breakpoint the Drawing Window](#breakpoint-the-drawing-window)
    - [Breakpoint the Chat](#breakpoint-the-chat)
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

That's the gShell inside gCloud inside gMail.
I wish we could recommend the replIt·Com Startup service over the gShell Corporate service,
but often your free gShell runs much faster than the free tier of replIt.
And of course getting a hold of a macOS Terminal like mine
will cost you hundreds or thousands of US Dollars

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
That way I can watch my Drawing appear, even while I'm still typing out my Chat

You can run separate Windows at replIt, and at macOS,
but not with gShell.
Your gShell will let you split a single Terminal Tab,
which can be as good.
But if you want the Font for your Turtles to be lots smaller
than the Font for your Chat,
then you have to run macOS or replIt or something other than gShell.
When you open a 2nd Window with the same gShell Login,
then gShell shuts off the 1st Window.
At least, they go wrong like that when both Windows are inside 1 Browser.
Maybe they don't go so wrong if you test 2 Browsers at once with the same gShell Login.
I've not yet tried that

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

You might want to prepare your Instructions in some other Window and paste them in,
because our Input Line Editing doesn't work very well yet.
For now, as you type instructions, to edit what you've typed, you can try

| Key Chord | Short Name | Meaning |
|-----------|------------|---------|
| ⌃C | row-delete | Delete the Input Line |
| ⌃W | word-delete | Delete 1 Word at the Left of the Turtle |
| ⌃U | row-delete | Delete the Input Line |
| Delete | char-delete-left | Delete 1 Character at the Left of the Turtle |


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
except the default Font at replIt does paint the full vertical height

As for me, as you can see in my screenshots,
lately mostly I test Screens of
101 Columns and 42 Rows of Andale Mono 18
in the Lightmode Basic Profile of the macOS Terminal App in Oct/2024 Sequoia macOS 15

I'd guess most of you are working inside a free gShell.
I've also seen free replIt Shells work.
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
    restart tada

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
    seth 0  rt 90  fd 30
    penup home
    fd 10  write '   █'
    restart tada

<!-- FIXME: Fully Relaunch after Write '   █' without '█' -->

#### Light up the Turtle

Our Turtle is too easy to lose

Sometimes it's the same Color as the Background of the Screen,
or the same Color as your Drawing in the Foreground,
or you turned it off with HideTurtle or Tada,
or you didn't turn it back on with ShowTurtle

To get the Turtle to blink on and off,
you can tell the Turtle to draw just 1 Square Pixel underneath it without moving away,
in different Colors

Try each of these, but one at a time. First

    Restart  PenDown  SetPenColor Red  Forward 0  Tada

And then

    Restart  PenDown  SetPenColor None  Forward 0  Tada

And then

    Restart  PenDown  SetPenColor None  Write '..'  Tada

If you try one at a time, then you can see the changes

Like I'll often draft a Drawing in PenColor None,
and end by drawing just 1 Pixel in Red,
just so I can see where I left the Cursor standing


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


### Explore More Colors

Terminal Colors come in too many kinds.
The ways of speaking of Terminal Colors changed rapidly across the 1980s,
and the Colors you actually find in a Terminal today
come out as some mix of Traditions

Our Turtles let you speak into your choice of Tradition,
but we can't know if your Terminal will accept your choice of Color,
until you test it for us.

There's a world of Colors out there, and I don't yet know it well.
One of the websites talking of Sh Terminal Colors is

Wikipedia > [ANSI escape code](https://en.wikipedia.org/wiki/ANSI_escape_code)

By copying those secret spells,
we can figure out how to tell your Terminal to draw Color Charts that look like theirs.
But we've not really finished that work yet.
All the same, here now is a start at trying to do that

    relaunch
    right 90
    penup  setxy -200 200  pendown
    label ''

    label '3-Bit Color'
    label ''
    label '\e[30m 30  \e[31m 31  \e[32m 32  \e[33m 33  \e[34m 34  \e[35m 35  \e[36m 36  \e[37m 37  \e[m'
    label '\e[7m\e[30m 30 \e[m \e[7m\e[31m 31 \e[m \e[7m\e[32m 32 \e[m \e[7m\e[33m 33 \e[m \e[7m\e[34m 34 \e[m \e[7m\e[35m 35 \e[m \e[7m\e[36m 36 \e[m \e[7m\e[37m 37 \e[m \e[m'
    label '\e[40m\e[97m 40 \e[m \e[41m\e[97m 41 \e[m \e[42m\e[97m 42 \e[m \e[43m\e[97m 43 \e[m \e[44m\e[97m 44 \e[m \e[45m\e[97m 45 \e[m \e[46m\e[97m 46 \e[m \e[47m\e[30m 47 \e[m'
    label ''

    label '4-Bit Color'
    label ''
    label '\e[90m  90  \e[91m  91  \e[92m  92  \e[99m  99  \e[94m  94  \e[95m  95  \e[96m  96  \e[97m  97  \e[m'
    label '\e[100m\e[97m 100 \e[m \e[101m\e[97m 101 \e[m \e[102m 102 \e[m \e[103m 103 \e[m \e[104m\e[97m 104 \e[m \e[105m\e[97m 105 \e[m \e[106m 106 \e[m \e[107m 107 \e[m'
    label ''

    label '8-Bit Color'
    label '\e[38;5;0m0 \e[38;5;1m1 \e[38;5;2m2 \e[38;5;3m3 \e[38;5;4m4 \e[38;5;5m5 \e[38;5;6m6 \e[38;5;7m7 \e[m'
    label '\e[38;5;8m8 \e[38;5;9m9 \e[38;5;10m10 \e[38;5;11m11 \e[38;5;12m12 \e[38;5;13m13 \e[38;5;14m14 \e[38;5;15m15 \e[m'
    label '\e[38;5;16m16 \e[38;5;17m17 \e[38;5;18m18 \e[38;5;19m19 \e[38;5;20m20 \e[38;5;21m21 \e[38;5;22m22 \e[38;5;23m23 \e[m'
    label '\e[38;5;24m24 \e[38;5;25m25 \e[38;5;26m26 \e[38;5;27m27 \e[38;5;28m28 \e[38;5;29m29 \e[38;5;30m30 \e[38;5;31m31 \e[m'
    label '\e[38;5;32m32 \e[38;5;33m33 \e[38;5;34m34 \e[38;5;35m35 \e[38;5;36m36 \e[38;5;37m37 \e[38;5;38m38 \e[38;5;39m39 \e[m'
    label '\e[38;5;40m40 \e[38;5;41m41 \e[38;5;42m42 \e[38;5;43m43 \e[38;5;44m44 \e[38;5;45m45 \e[38;5;46m46 \e[38;5;47m47 \e[m'
    label '\e[38;5;48m48 \e[38;5;49m49 \e[38;5;50m50 \e[38;5;51m51 \e[38;5;52m52 \e[38;5;53m53 \e[38;5;54m54 \e[38;5;55m55 \e[m'
    label '\e[38;5;56m56 \e[38;5;57m57 \e[38;5;58m58 \e[38;5;59m59 \e[38;5;60m60 \e[38;5;61m61 \e[38;5;62m62 \e[38;5;63m63 \e[m'
    label '\e[38;5;64m64 \e[38;5;65m65 \e[38;5;66m66 \e[38;5;67m67 \e[38;5;68m68 \e[38;5;69m69 \e[38;5;70m70 \e[38;5;71m71 \e[m'
    label '\e[38;5;72m72 \e[38;5;73m73 \e[38;5;74m74 \e[38;5;75m75 \e[38;5;76m76 \e[38;5;77m77 \e[38;5;78m78 \e[38;5;79m79 \e[m'
    label '\e[38;5;80m80 \e[38;5;81m81 \e[38;5;82m82 \e[38;5;83m83 \e[38;5;84m84 \e[38;5;85m85 \e[38;5;86m86 \e[38;5;87m87 \e[m'
    label '\e[38;5;88m88 \e[38;5;89m89 \e[38;5;90m90 \e[38;5;91m91 \e[38;5;92m92 \e[38;5;93m93 \e[38;5;94m94 \e[38;5;95m95 \e[m'
    label '\e[38;5;96m96 \e[38;5;97m97 \e[38;5;98m98 \e[38;5;99m99 \e[38;5;100m100 \e[38;5;101m101 \e[38;5;102m102 \e[38;5;103m103 \e[m'
    label '\e[38;5;104m104 \e[38;5;105m105 \e[38;5;106m106 \e[38;5;107m107 \e[38;5;108m108 \e[38;5;109m109 \e[38;5;110m110 \e[38;5;111m111 \e[m'
    label '\e[38;5;112m112 \e[38;5;113m113 \e[38;5;114m114 \e[38;5;115m115 \e[38;5;116m116 \e[38;5;117m117 \e[38;5;118m118 \e[38;5;119m119 \e[m'
    label '\e[38;5;120m120 \e[38;5;121m121 \e[38;5;122m122 \e[38;5;123m123 \e[38;5;124m124 \e[38;5;125m125 \e[38;5;126m126 \e[38;5;127m127 \e[m'
    label '\e[38;5;128m128 \e[38;5;129m129 \e[38;5;130m130 \e[38;5;131m131 \e[38;5;132m132 \e[38;5;133m133 \e[38;5;134m134 \e[38;5;135m135 \e[m'
    label '\e[38;5;136m136 \e[38;5;137m137 \e[38;5;138m138 \e[38;5;139m139 \e[38;5;140m140 \e[38;5;141m141 \e[38;5;142m142 \e[38;5;143m143 \e[m'
    label '\e[38;5;144m144 \e[38;5;145m145 \e[38;5;146m146 \e[38;5;147m147 \e[38;5;148m148 \e[38;5;149m149 \e[38;5;150m150 \e[38;5;151m151 \e[m'
    label '\e[38;5;152m152 \e[38;5;153m153 \e[38;5;154m154 \e[38;5;155m155 \e[38;5;156m156 \e[38;5;157m157 \e[38;5;158m158 \e[38;5;159m159 \e[m'
    label '\e[38;5;160m160 \e[38;5;161m161 \e[38;5;162m162 \e[38;5;163m163 \e[38;5;164m164 \e[38;5;165m165 \e[38;5;166m166 \e[38;5;167m167 \e[m'
    label '\e[38;5;168m168 \e[38;5;169m169 \e[38;5;170m170 \e[38;5;171m171 \e[38;5;172m172 \e[38;5;173m173 \e[38;5;174m174 \e[38;5;175m175 \e[m'
    label '\e[38;5;176m176 \e[38;5;177m177 \e[38;5;178m178 \e[38;5;179m179 \e[38;5;180m180 \e[38;5;181m181 \e[38;5;182m182 \e[38;5;183m183 \e[m'
    label '\e[38;5;184m184 \e[38;5;185m185 \e[38;5;186m186 \e[38;5;187m187 \e[38;5;188m188 \e[38;5;189m189 \e[38;5;190m190 \e[38;5;191m191 \e[m'
    label '\e[38;5;192m192 \e[38;5;193m193 \e[38;5;194m194 \e[38;5;195m195 \e[38;5;196m196 \e[38;5;197m197 \e[38;5;198m198 \e[38;5;199m199 \e[m'
    label '\e[38;5;200m200 \e[38;5;201m201 \e[38;5;202m202 \e[38;5;203m203 \e[38;5;204m204 \e[38;5;205m205 \e[38;5;206m206 \e[38;5;207m207 \e[m'
    label '\e[38;5;208m208 \e[38;5;209m209 \e[38;5;210m210 \e[38;5;211m211 \e[38;5;212m212 \e[38;5;213m213 \e[38;5;214m214 \e[38;5;215m215 \e[m'
    label '\e[38;5;216m216 \e[38;5;217m217 \e[38;5;218m218 \e[38;5;219m219 \e[38;5;220m220 \e[38;5;221m221 \e[38;5;222m222 \e[38;5;223m223 \e[m'
    label '\e[38;5;224m224 \e[38;5;225m225 \e[38;5;226m226 \e[38;5;227m227 \e[38;5;228m228 \e[38;5;229m229 \e[38;5;230m230 \e[38;5;231m231 \e[m'
    label '\e[38;5;232m232 \e[38;5;233m233 \e[38;5;234m234 \e[38;5;235m235 \e[38;5;236m236 \e[38;5;237m237 \e[38;5;238m238 \e[38;5;239m239 \e[m'
    label '\e[38;5;240m240 \e[38;5;241m241 \e[38;5;242m242 \e[38;5;243m243 \e[38;5;244m244 \e[38;5;245m245 \e[38;5;246m246 \e[38;5;247m247 \e[m'
    label '\e[38;5;248m248 \e[38;5;249m249 \e[38;5;250m250 \e[38;5;251m251 \e[38;5;252m252 \e[38;5;253m253 \e[38;5;254m254 \e[38;5;255m255 \e[m'

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

    setpc '#FFffFF'  # White = Red + Green + Blue
    setpc '#FF00FF'  # Magenta = Red + Blue
    setpc '#0000FF'  # Blue
    setpc '#00FFFF'  # Cyan = Green + Blue
    setpc '#00FF00'  # Green
    setpc '#FFFF00'  # Yellow = Red + Green
    setpc '#FF0000'  # Red
    setpc '#000000'  # Black

These Commands don't work yet, unless you send them without Comments

    setpc '#FFffFF'
    setpc '#FF00FF'
    setpc '#0000FF'
    setpc '#00FFFF'
    setpc '#00FF00'
    setpc '#FFFF00'
    setpc '#FF0000'
    setpc '#000000'

Tell us that Bug of ours bothers you, and we'll fix it sooner.
The Colors you get when you ask for Html 24-Bit Colors in this way will change.
They're not correct now, they're falling back to substitute the 3-Bit Colors

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

    write '\e[38;5;130m'  # Orange

#### Explore 24-Bit Color in the Cloud

Searching with ⌘F 31 will show you
Wikipedia People talking of ESC[31m, as we did above

Searching instead with ⌘F 38; will show you
Wikipedia People talking of "Select RGB foreground color"
from a choice of more than 16 million "24-bit" Colors

For example, inside of a gShell, try

    write '\e[38;5;196m Red \e[38;2;255;0;0m Red \e[m'
    write '\e[38;5;46m Green \e[38;2;0;255;0m Green \e[m'
    write '\e[38;5;21m Blue \e[38;2;0;0;255m Blue \e[m'

These 24-bit Colors work inside a gShell and also inside a replIt Shell.
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

<!-- FIXME: no quotes needed for \e without Spaces -->


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


### Edit your Drawings

You can edit your Drawings with the Keyboard Shortcuts that the Terminal itself understands

Editing your Drawings like this today
doesn't write the Logo Code that would make the same edits.
We could come fix that. Just ask us

We need to write down for us how much works where.
Here we tell you what we've seen work somewhere,
but we've lost track of was it working in macOS or gShell or replIt or what

Odds on your ⎋ ⌃ ⌥ ⇧ ⌘ Keys have letters printed on them: esc, control, option, shift, command

Forwarding what the Keyboard says straight into the Terminal Screen can work.
These Keyboard Shortcuts work like that

| Key Chord | Short Name | Meaning |
|-----------|------------|---------|
| ← | column-go-left | Move Left by one Column |
| ↑ | row-go-up | Move Up by 1 Row |
| ↓ | row-go-down | Move Down by 1 Row |
| → | column-go-right | Move Right by one Column |
| Tab | tab-go-right | Move far Right, to next Tab Stop |
| ⇧Tab | tab-go-left | Move far Left, to next Tab Stop |

When you learn to type the ⎋ Esc Key, then you can try feeding more of the Keyboard into the Screen

| Key Chord | Short Name | Meaning |
|-----------|------------|---------|
| ⎋8 | cursor-revert | Jump to far Upper Left, or to last ⎋7 |
| ⎋7 | cursor-checkpoint | Tell ⎋8 where to go |
| ⎋[⇧P | chars-delete | Delete the 1 Character beneath the Turtle |
| ⎋[⇧@ | chars-insert | Slide the Characters past the Turtle to the right by 1 Column |
| ⎋[⇧M | rows-delete | Lift the Rows below the Turtle up by 1 Row |
| ⎋[⇧L | rows-insert | Push the Rows below the Turtle down by 1 Row |
| ⎋['⇧~ | cols-delete | Slide the Columns past the Turtle to the left by 1 Column |
| ⎋['⇧} | cols-insert | Slide the Columns past the Turtle to the right by 1 Column |

When you learn to type decimal Digits in the middle of these Escape Control Sequences,
then you can make them more powerful

| Key Chord | Short Name | Meaning |
|-----------|------------|---------|
| ⎋[321⇧D | ← Left Arrow | Move the Turtle to the left by 321 Columns, but stop at right edge of Screen |
| ⎋[321⇧A | ↑ Up Arrow | Move the Turtle up by 321 Rows, but stop at top edge of Screen |
| ⎋[321⇧C | → Right Arrow | Move the Turtle to the right by 321 Columns, but stop at right edge of Screen |
| ⎋[321⇧B | ↓ Down Arrow | Move the Turtle down by 321 Rows, but stop at bottom edge of Screen |

Beware of gShell.
gShell takes ⌃B as a TMux Keyboard Shortcut, so out there
you have to press ← or press ⌃B ⌃B twice to go to the Column at Left of the Turtle

| Key Chord | Short Name | Meaning |
|-----------|------------|---------|
| ⌃A | column-go-leftmost | Go to the leftmost Column of Row |
| ⌃B | column-go-left | Go to the Column at Left of the Turtle |
| ⌃F | column-go-right | Go to the Character at Right of the Turtle |
| ⌃G | alarm-ring | Ring the Terminal Bell |
| ⌃N | row-go-down | Move as if you pressed the ↓ Down Arrow |
| ⌃P | row-go-up | Move as if you pressed the ↑ Up Arrow |

<!--

Some of the editing Keys of the Keyboard will mostly work as you expect

| Delete | char-delete-left | Delete 1 Character at the Left of the Turtle |
| Return | row-insert-go-below | Insert a Row below this Row and move into it |

with some of the same Keyboard Shortcuts
that a macOS Note or Terminal Emacs understands

The most ordinary editing macOS/ Emacs Key Chords will mostly work too

| Key Chord | Short Name | Meaning |
|-----------|------------|---------|
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
gShell grabs that Key Chord to operate a TMux Split of the Tab
for ⌃B ⇧%, ⌃B ⇧", ⌃B ↓, ⌃B ↑, ⌃B X. etc.
We could grab that Key Chord to operate a TMux Split of the Tab someday too,
just to make our Turtle Logo look & feel alike in more places

-->


## We can just try things


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


### Blame me, not you, when this English is difficult to read

You may believe this Md File is written in the English of Computer Engineers

You're not completely wrong.
But my English is famously difficult to read.
People often struggle to get my meaning from my first writing.
Let's make it better?

Tell me some piece of this English doesn't just make sense, and then
Claude·Ai & I will go work on rewriting it.
We can make its meaning come across
more clearly and accurately, while still brief

Myself, I delight in my own failures to understand your English, first try.
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
> Emily Dickinson 1830..1886

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

Python itself objects if you explicitly try to say 't.left.angle = 90'.
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

I'd guess I'll make lots of the defaults cyclic.
Like when you ask for SetPenColor None then give you back how we started,
but every time you ask for SetPenColor without picking a Color,
then we give you the next Color of the Rainbow


### Paste whole Files of Input

You can paste larger Turtle Logo Programs
in to the '🐢? ' Prompt of the Chat Window.
We've not yet worked up a great way to make them more available to you,
but they are posted out there

In particular, presently you can paste one or all of

> [demos/arrow-keys.logo](../demos/headings.logo)<br>
> [demos/bkboxbox.logo](../demos/bkboxbox.logo)<br>
> [demos/fdboxbox.logo](../demos/fdboxbox.logo)<br>
> [demos/headings.logo](../demos/headings.logo)<br>
> [demos/like-a-rainbow.logo](../demos/like-a-rainbow.logo)<br>
> [demos/mtm-titlecard.logo](../demos/mtm-titlecard.logo)<br>
> [demos/rainbow.logo](../demos/rainbow.logo)<br>
> [demos/xyplotter.logo](../demos/xyplotter.logo)<br>

Our "arrow-keys" draws the four Arrow keys of a macBook Keyboard.
Our "bkboxbox" and "fdboxbox" draw two boxes, one inside the other,
one clockwise, the other anticlockwise.
Our "headings" draws Lines of 30°, 45°, 60°, and 90° in each of the four Quadrants.
draws something a lot like concentric circles,
somewhat miscalculated by hand, with charm.
Our "mtm-titlecard" draws the "Mary Tyler Moore" Title Card, from Sep/1970,
which is 11 Lines of differently colored Bold Text on a Black Background.
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
you can click into the Drawing Window and press Return after Relaunch,
but before the Count = and For,
then you can draw Count as large as 10 in my Terminal today.
If you watch for it, you can see
our Chat Window prints "Snap" Messages when your drawing grows too large,
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
if we completed a full Python Command every time you pressed a Key inside the Drawing Window.
Or we could rewrite our Arrow Keys Demo to have 4 Turtles draw it, not just 1.
Or we could figure out how to show the Turtle
even after you split a gShell Tab
with ⌃B ⇧" and then moved the Turtle between Splits with ⌃B ↑ and  ⌃B ↓.
The replIt Shell has much the same disappear-the-Turtle bug,
if you do run the replIt Turtle and the Chat in separate Browser Windows.
gShell can't do separate Windows inside the same Browser

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


#### Breakpoint the Drawing Window

To halt the Drawing and open it up inside the Pdb Python Debugger, try

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


## Try out some other Turtle Logo

You can try these same tests inside other Turtle Logo Apps.
In particular, adding Python into macOS lets you try

    python3 -i -c ''

    import turtle
    turtle.mode("Logo")

    t = turtle.Turtle()

    t.forward(100)
    t.right(45)

This Import Turtle demo runs just as well for me in Windows of ReplIt.
But the free replIt Python runs tremendously slower than macOS Python

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
I can only hope we'll scrub more bugs out of it and make it as fast as Python

**Links**

Docs·Python·Org > Import [turtle — Turtle Graphics](https://docs.python.org/3/library/turtle.html)<br>

Mit·Edu [Scratch](https://scratch.mit.edu) Programming Language - Draw Logo-Like Programs that draw Logo-Like Turtle Graphics

Wiki > [Domain-specific language]([./demos/arrow-keys.logo](https://en.wikipedia.org/wiki/Domain-specific_language))<br>
Wiki > [Greenspun's tenth rule](https://en.wikipedia.org/wiki/Greenspun%27s_tenth_rule)<br>


### Does it work at your desk?

Our Turtle Logo runs inside more Terminals.
Their Turtle Logo runs inside a macOS Terminal, and inside ReplIt.
In other places, such as gShell, our Turtle Logo still works,
whereas their Turtle Logo tells you things like

    ModuleNotFoundError: No module named 'tkinter'

    _tkinter.TclError: no display name and no $DISPLAY environment variable


### What kind of drawings does it make?

Our Turtle Logo draws with Character Graphics inside the Terminal.
You can copy-paste our drawings into a Google Doc (gDoc), and
edit them inside the Google Doc

To save drawings entirely inside the Terminal,
you can record and replay them (at near infinite speed)
with the Shell 'screen' command

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
She put Terminal Tabs of gShell
forward as the most available Linux Hosts

Natalia of Bucharest!
She drew our first Animal, her Snake

Tina of Monterey!
She drew our first Giraffe


<!-- omit in toc -->
## Copied from

Posted as:  https://github.com/pelavarre/byoverbs/blob/main/docs/turtling-in-the-python-terminal.md<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git<br>
