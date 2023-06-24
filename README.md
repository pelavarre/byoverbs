# byoverbs

Your Sh Terminal runs lots of mostly abandoned C Code from like 1972

We work here to make that mostly dead C Code live well again.
We make you feel like someone competent is looking out for you.
We break you free from working inside the Sh Terminal with nothing but rotted-out tools

We keep our Doc ahead of our Tests, we keep our Tests ahead of our Code.
If you see something wrong, say something, please.
Odds on we'll fix it faster if you're up talking it out

## Ls

To report sub-second last-modified Date/Time at Mac without Linux 'ls --full-time', try

    bin/ls.py --full-time

## Missing Man Pages

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

## Pq

To build Sh Pipe Filters out of Python, in place of Awk and Jq, try

    bin/pq.py

## Screen

To spell out which 'screen -r' Sh Command Line will reach each detached Screen, try

    bin/screen.py -ls

To run 'sh screen', but with ⌃B Esc ... Esc to mean move around, try

    bin/screen.py --  # reminds you of the Sh syntax:  screen -e^Bb

To get 256-Color Vi Py while recording your Font and Color experience,
just run Screen Py and Vi Py in place of the buggy Screen and Vi that Apple ships

Left broken by Apple macOS

    bin/vi p.py  # spec: 256-Color Orange for Python 'def' keyword
    bin/screen vi p.py  # bug: 16-Color Yellow
    bin/screen bash -c "TERM=$TERM vi p.py"  # bug: 8-Color Red

    bin/screen.py vi p.py  # bug: stops synching with Terminal Window Resize

    bin/screen.py stty size  # bug: (0, 0) inside Python Import Tty

Working in Python

    bin/vi.py p.py
    bin/screen.py vi.py p.py
    bin/screen.py bash -c "TERM=$TERM vi.py p.py"
    bin/screen.py stty.py size

Size works in Python because Csi 07/04 Private reports Column x Rows anyhow

    bin/screen.py
    printf '\e[18t' && python3 -c 'import sys; print(repr(sys.stdin.read()))'

## Tac

For when you remember 'tac' from Linux and don't find it at Mac, try

    echo a b c |tr ' ' '\n' |bin/tac

For when your Linux Tac chokes while Tmp Dir full, try

    echo a b c |tr ' ' '\n' |bin/tac.bash

For when your Linux Tac inserts a last Line left open into the 2nd-to-last Line, try

    echo -n a b c |tr ' ' '\n' |bin/tac.py

## Tail R

For when you remember 'tail -r' from Mac and don't find it at Linux, try

    echo a b c |tr ' ' '\n' |bin/tail.py -r

For when your Mac Tac inserts a last Line left open into the 2nd-to-last Line, try

    echo -n a b c |tr ' ' '\n' |bin/tail.py -r


## Vi

To run a variation of Vi that you can easily quickly write Python to reprogram, try

    vi.py
    ls -1 |vi.py - >ls1.txt
    pbpaste |vi.py - |pbcopy
    vi.py /dev/tty

Vi Py helps you edit Screen, Memory, Os Copy/Paste Buffer, Pipe, or File -
not just the Memory or File of classic Vi

### Vi Py Mouse

Click your mouse on the Screen, and Classic Vi does nothing, ugh.
Vi Py tells you what sequence of Keyboard Chords to press to go there.
Vi Py teaches you Vim Golf by playing Vim Golf well for you.
Vi Py and Classic Vi move the Cursor to the Mouse if you press Option Click.

### Vi Py Esc Key and ⌃C Key Chord

Vi Py doesn't block you from typing out the C0 Escape Sequences you know.
Vi Py doesn't make you go learn what Vi Py Keyboard Chords will inject them.

You have to learn one new thing:
you press ⌃C to stop Replacing or Inserting, to go back to Moving.
Pressing ⌃C to go back to Moving works in Classic Vi too,
but maybe you didn't know that.
Like bugs in their ':set cursorline' makes this hard to see correctly.

With Vi Py, beyond Classic Vi, you can type out an C0 Escape Sequence

    ⎋[1m Bold, ⎋[3m Italic, ⎋[4m Underline, ⎋[m Plain
    ⎋[31m Red, ⎋[32m Green, ⎋[34m Blue, ⎋[m Colorless

If you forget this difference between Vi Py and Classic Vi,
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

Same story for ⌃D and ⌃U to page just half as far, down and up.

### Vi Py repeating Replace and Insert

Vi Py doesn't block you from including movement in your repeated Replace and Insert

Like you can start with 3 I and mix ← ↑ → ↓ Arrow Keys into your Input ended with ⌃C,
and then V Py does work the same
as if you told Vi Q Q I ⌃C 3 @ Q to record/ replay all your Input.
Vi Py 3 I is lots less intricate than Classic Vi starts with Q Q and ends with ⌃C 3 @ Q

Vi Py 3 I also still works if you stop the Replace or Insert with ⌃C,
unlike Classic Vi that cancels the Repeat 3
unless you end with the Replace or Insert with Esc

Same story for ⇧R, R, and same story for ⇧I, ⇧O, A, I, and O

### Vi Py edits the Lines flowing through the Sh Pipe you have

Vi Py lets you edit the Sh Pipe you put it inside of

    ls -1 |vi.py - >ls1.txt
    pbpaste |vi.py - |pbcopy

By contrast, Classic Vi forces you to name an output File,
and then work separately to pipe that output File to where you need it to go

    ls -1 |vi -
    pbpaste |vi -
    cat t.txt |pbcopy

### Vi Py edits the Screen you have

Your Terminal has a main Screen and an alternate Screen.

Vi Py defaults to work on your main Screen,
same as Classic Less and Classic Vi learned to do intricately and late

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

You can tell Vi Py to record Color and Font for you

    vi --script

You can edit the recording as it happens, just call Vi Py again from inside Vi Py

You can tell Vi Py to edit Text Files that include C0 Escape Sequences
to mark your choices of Color and Font

    vi.py screenlog.0  # from Sh:  screen -L
    vi.py typescript  # from Sh:  script

## Come back tomorrow

As yet, we're more working to show off what you can afford to fix,
not so much working to come fix it for you

If you need something fixed now, come talk to us enough
and we might fix it soon - Many many fixes are easy to write in Python

We don't have all our own Code and Docs here all synched up
lately - Come talk to us enough and we'll fix the bugs that bother you

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/README.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
