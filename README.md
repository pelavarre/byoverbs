# byoverbs

Your Sh Terminal runs lots of mostly abandoned C Code from like 1972

We work here to make that mostly dead C Code live well again.
We make you feel like someone competent is looking out for you.
We break you free from working inside the Sh Terminal with nothing but rotted-out tools

We keep our Doc ahead of our Tests, we keep our Tests ahead of our Code.
If you see something, say something, please.
Odds on we'll fix broken things faster if you're up talking them out with us

Run our code, read our code, fork it when you please.
You've "brought your own verb" - B Y O - when you install it or fork it

## Ls Py

Classic Ls rounds off last-modified Date/Time to whole local seconds.
To report sub-second time at Mac without Linux 'ls --full-time', try

    bin/ls.py --full-time

Classic Sh shoves on you to run the Code without reading it first.
We give you the Code when you ask for it

    % bin/ls.py -1 --py
    # ls -1
    import os
    for item in sorted(os.listdir()):
        print(item)
    % 

## Man Py

To dump the concrete examples missing from merely official Man Pages,
call our Py Files with no Sh Arguments

    bin/ls.py
    bin/pq.py
    bin/screen.py
    bin/vi.py

    ... and so on ...

We know concrete Examples for new people
matter more than convenient default actions for the rest of us.
We bury the conveniences for us behind an explicit double-dash mark of no Sh Arguments

    bin/ls.py --
    bin/pq.py --
    bin/screen.py --
    bin/vi.py --

    ... and so on ...

## Md5Sum Py

For when you remember 'md5sum' from Linux and don't find it at Mac, try

    bin/md5sum bin/md5sum

Careful, it will hang silently if you give it no Filename, same as at Linux

## Pq Py

To build Sh Pipe Filters out of Python, in place of Awk and Jq, try

    bin/pq.py

## Screen Py

To spell out which 'screen -r' Sh Command Line will reach each detached Screen, try

    bin/screen.py -ls

To run 'sh screen', but with ⌃B Esc ... Esc to mean move around, try

    bin/screen.py --  # reminds you of the Sh syntax:  screen -e^Bb

To get 256-Color Vi Py while recording your Font and Color experience,
just run Screen Py and Vi Py in place of the buggy Screen and Vi that Apple ships

Working in Python

    bin/vi.py p.py
    bin/screen.py vi.py p.py
    bin/screen.py bash -c "TERM=$TERM vi.py p.py"
    bin/screen.py stty.py size

Left broken by Apple macOS

    bin/vi p.py  # spec: 256-Color Orange for Python 'def' keyword
    bin/screen vi p.py  # bug: 16-Color Yellow
    bin/screen bash -c "TERM=$TERM vi p.py"  # bug: 8-Color Red

    bin/screen.py vi p.py  # bug: stops synching with Terminal Window Resize

    bin/screen.py stty size  # bug: (0, 0) inside Python Import Tty

Stty Py Size can work in Python no worries, because Csi 07/04 Private reports Column x Rows anyhow

    bin/screen.py
    printf '\e[18t' && python3 -c 'import sys; print(repr(sys.stdin.read()))'

## Sha256 Py

For when you remember 'md5sum' from Linux and don't find 'sha256' in your Linux or Mac, try

    bin/sha256 bin/sha256

Careful, it will hang silently if you give it no Filename, same as at Linux Md5Sum

## Tac Py

For when you remember 'tac' from Linux and don't find it at Mac, try

    echo a b c |tr ' ' '\n' |bin/tac

For when your Linux Tac chokes while Tmp Dir full, try

    echo a b c |tr ' ' '\n' |bin/tac.bash

For when your Linux Tac inserts a last Line left open into the 2nd-to-last Line, try

    echo -n a b c |tr ' ' '\n' |bin/tac.py

## Tail Py

For when you remember 'tail -r' from Mac and don't find it at Linux, try

    echo a b c |tr ' ' '\n' |bin/tail.py -r

For when your Mac Tac inserts a last Line left open into the 2nd-to-last Line, try

    echo -n a b c |tr ' ' '\n' |bin/tail.py -r

## Vi Py

To run a variation of Vi that you can  quickly write trivial Python to reprogram, try one of

    vi.py  # edit Memory on Screen
    ls -1 |vi.py - >ls1.txt  # edit a Sh Pipe
    pbpaste |vi.py - |pbcopy  # edit the macOS Copy/Paste Buffer
    vi.py /dev/tty  # edit the Screen

Vi Py helps you edit Screen, Memory, Os Copy/Paste Buffer, Pipe, or File -
not just the Memory or File of Classic Vim

### Vi Py Mouse

Click your mouse on the Screen, and Classic Vim does nothing, ugh, sorry, so very misleading.
Vi Py tells you what sequence of Keyboard Chords to press to go there.
Get it? Vi Py works to teach you Vim Golf by playing Vim Golf well for you.
Vi Py and Classic Vim move the Cursor to the Mouse if you press Option Click

### Vi Py Esc Key and ⌃C Key Chord

Vi Py doesn't block you from typing out the C0 Escape Sequences you know.
Vi Py doesn't make you go learn what Vi Py Keyboard Chords will inject the C0 Escape Sequences

You might feel you do have to learn one new thing:
you press ⌃C to stop Replacing or Inserting, to go back to Moving.
Pressing ⌃C to go back to Moving works in Classic Vim too,
but maybe you didn't know that.
Like bugs in their ':set cursorline' makes this truth hard to demo plainly

With Vi Py, beyond Classic Vim, you can type out an C0 Escape Sequence

    ⎋[1m Bold, ⎋[3m Italic, ⎋[4m Underline, ⎋[m Plain
    ⎋[31m Red, ⎋[32m Green, ⎋[34m Blue, ⎋[m Colorless

If you forget this difference between Vi Py and Classic Vim,
you can press Esc twice, and then Replacing or Inserting still stops,
same as if you did press ⌃C

When you save your Text, Vi Py saves the Color you gave it too

Vi Py waits patiently if you press Esc and think awhile about what to press next,
Vi Py doesn't slap you with a Bel a couple of seconds after you press Esc

Vi Py doesn't slap you with a Bel
if you press ⌃C just once to know you've stopped Replacing or Inserting

Vi Py doesn't slap you with the Bel
while you're repeating the movement that brought you to an edge

### Vi Py Control Key while replacing and inserting

Vi Py doesn't so much change what the Control Key means
while you're replacing and inserting

Like you can press ⌃F to page down, ⌃B to page up,
you don't have to press ⌃O ⌃F and ⌃O ⌃B for that effect

Same story for ⌃D and ⌃U to page just half as far, down and up

The D and C inside Vi Py do let you cut to movement, for example you can D ⌃O and you can C ⌃I.
Bizarrely, Classic Vim requires you to move there, set a Mark, and move back,
like by way of } } 2 ⌃O M M 2 ⌃I D ' M.
Vi Py D ⌃O and C ⌃O is lots less intricate than all that

### Vi Py repeating Replace and Insert

Vi Py doesn't block you from including movement in your repeated Replace and Insert

Like you can start with 3 I and mix ← ↑ → ↓ Arrow Keys into your Input ended with ⌃C,
and then V Py does work the same
as if you told Vi Q Q I ⌃C 3 @ Q to record/ replay all your Input.
Vi Py 3 I is lots less intricate than all that

Vi Py 3 I also still works if you stop the Replace or Insert with ⌃C,
unlike Classic Vim that cancels the Repeat 3
unless you end with the Replace or Insert with Esc

Same story for ⇧R, R, and same story for ⇧I, ⇧O, A, I, and O

### Vi Py edits the Lines flowing through the Sh Pipe you have

Vi Py lets you edit the Sh Pipe you put it inside of

    ls -1 |vi.py - >ls1.txt
    pbpaste |vi.py - |pbcopy

By contrast, Classic Vim forces you to name an output File,
and then work separately afterwards,
to pipe that output File to where you need it to go

    ls -1 |vi -
    pbpaste |vi -
    cat t.txt |pbcopy

### Vi Py edits the Screen you have

Your Terminal has a main Screen and an alternate Screen.

Vi Py defaults to work on your main Screen,
same as Classic Less and Classic Vim learned to do intricately and late

    ls -1 |less -FIRX
    ls -1 |vi - +':set t_ti= t_te='

Vi Py will come work on your whole Screen if you tell it to

    vi.py /dev/tty

Vi Py doesn't make you copy the Screen into a File to work on it.
Like Vi Py can take Colored Output from 'git diff' and put a blank Frame around it,
before you screen-shoot it.
However,
so long as your Terminal's Secure Sandbox blocks Vi Py from reading your Screen,
then Vi Py can only save the Texts you told it to replace or insert,
it can't know what you put on Screen before running Vi Py

You can tell the Sh to record Color and Font for you

    script

You can tell us to record Color and Font more accurately for you

    script.py --

You can edit the recording as it happens, by calling Vi Py again from inside Vi Py

    vi.py /dev/tty

You can tell Vi Py to edit Text Files that include C0 Escape Sequences
marking your choices of Color and Font

    vi.py screenlog.0  # from Sh:  screen -L
    vi.py typescript  # from Sh:  script

## Less Available Sh Terminal Work

You can find more things to love in here, if you dig deeper,
but these things are only actually worthwhile for more people,
not obviously worthwhile

### 15 Flavours of Sh Pipe

We lack the patience required to spell out as much of Sh Pipe Filters
as should be at your fingertips.
Our 15 single-letter abbreviations for 15 Classic Sh Pipe Filters show up at

    % ls bin/?
    bin/a	bin/d	bin/f	bin/h	bin/p	bin/s	bin/u	bin/x
    bin/c	bin/e	bin/g	bin/n	bin/q	bin/t	bin/v
    % 

On the side, we worked up 4 more Sh Pipe Filters, arguably Classic

    bin/cv  bin/mo  bin/xd  bin/xn1

Our 'bin/cv' Sh Filter in particular unifies Mac 'pbpaste' and 'pbcopy'.
Place it where you need it in your Sh Pipe and then
it figures out if you meant 'pbpaste' or 'pbcopy',
by whether you left Stdin or Stdout or both or neither as a Dev Tty

    echo abc |cv
    cv
    echo xyz |cv |tr '[a-z]' '[A-Z]'
    cv

### 57 Flavours of Git

We lack the patience required to spell out as much of Git
as should be at your fingertips.
Our 57 single-letter abbreviations for 57 Words of Git show up at

    ls bin/q*

## Come back tomorrow

We keep our Doc ahead of our Tests, we keep our Tests ahead of our Code.
If you see something, say something, please.
Odds on we'll fix broken things faster if you're up talking them out with us

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/README.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
