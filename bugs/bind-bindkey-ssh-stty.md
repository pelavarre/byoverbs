# bugs/bind-bindkey-stty.md

Classic Sh hides away from you how wildly it will misread your Keyboard Chords.
Many separate Apps work together to guess what you mean.

## Glitches

Four kinds of messy =>

1

Often, pressing Return to end your current Input Line,
and then starting your next Input Line with the two Chars ~? will tell you things like

    ~?   - this message
    ~/   - type both to see both

When this works, it means you gave Ssh the first chance to decide what you mean.

2

Often your Stty Settings will decide what you mean

    stty -a |grep '\^'

Common Stty Settings include

    susp = ^Z; intr = ^C; quit = ^\;
    erase = ^?; werase = ^W; kill = ^U; eof = ^D
    lnext = ^V; rprnt = ^R
    start = ^Q; stop = ^S

A good place to show these off is inside

    cat - |cat -n |expand

Learning XOff Stop = ^S by experiment can be expensive, because confusing,
but it is XOn Start = ^Q that undoes it.

A start into learning lnext = ^V is to press it twice as ^V^V.
But don't feel surprised if ^V^C works differently in your macOS Zsh vs Linux Bash.

And don't feel too surprised if your experiments in Zsh and Bash
show you ^R meaning search backwards through your own Input Lines,
rather than the 'rprnt' Reprint of your Input Line.

3

The next layer of Code up deciding what your Keyboard Chords mean is Bash

    bind -p |grep C-x |grep C-e  # Bash

or Zsh

    bindkey |grep '...M"'  # Zsh

Zsh and Bash don't both make Bind P and BindKey work, because fragmentation.

Bash forces you to remember the '-p' part of its 'bind -p', i guess for no good reason.

They both don't tell you that that ^S often doesn't undo ^R Search at

    (bind -p || bindkey) |grep -e C-r -e C-s -e '[RS]"'

unless you remember to set up ⌃S to work with

    stty -ixon

4

They mostly don't tell you that the \e in Bash Bind P and the ^[ in Zsh BindKey
are chances for you to make the ⌥ Alt/ Option Key work,
rather than forcing you to press Esc separately
in place of holding down the the ⌥ Alt/ Option Key.

At macOS Terminal, to make the ⌥ Alt/ Option Key work, you turn on

    macOS > Terminal > Settings > Keyboard > Use Option as Meta Key

Otherwise by default you get Apple's œ ∑ é ® † ¥ Keyboard there.

Sure we can mix the Terminal ⌥ Alt/ Option Keyboard with Apple's œ ∑ é ® † ¥ Keyboard,
but I've never seen people make that complex choice.

## Tests

    bind.py
    bindkey.py
    stty.py

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/bugs/bugs/bind-bindkey-ssh-stty.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
