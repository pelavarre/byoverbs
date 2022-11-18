# byoverbs
Competently welcome you into Sh Terminal work,
  by making three moves in particular here now

i ) Break you free to Bring-Your-Own (BYO) Verbs into Sh Terminal work, on the cheap

ii ) Invite you to copy-edit and fork all of what comes to meet with you here

ii ) Help you write enough and not too much Code as simple small Sh Scripts,
  so you can read, keep up, and write the less simple Code in Python

## Examples, Explanations, Guesses, Options, Args, and Code

Odds on your Sh Terminal has been inviting you to press Dot Tab Return,
  in place of just Return, as often as you type out the first Word of a Command Line

For example, when you place both 'touch' and 'touch.py' in your Sh Path,
  then typing out 'touch' and pressing Dot Tab will fill out the Dot P Y part for you

This move then gives the choice on what happens next to you

Our work here gives you **examples** first,
  but gives you longer **explanations**
    if you type Space Dash Dash H before you press Return, and
  jumps out into **guessing** what you want
    if you type all of Space Dash Dash before you press Return

    touch.py  # show these examples and exit
    touch.py --h  # show help lines and exit (more reliable than -h)
    touch.py --  # create a file named for now, such as 't.touch~1231jqd2359~'

Its guesses are correct, because you chose them

Linux and Python conventions spell out how to send these marks,
  but no so very much what they mean -
  pressing Return means no argument,
  the Space Dash Dash H Return is short
    for a '--help' option calling for help lines, and
  the Space Double Dash Return is a way for you to type more than you have to type
    just to more explicitly say you chose no argument

The walk you walk through the Examples, Explanations, and Guesses,
  will give you the feel for what you want next to go do
    with the **Options** and **Args**
      demoed in the Examples and declared in the Explanations,
and also how you want to change and grow the **Code** in the Py File

Linux mostly ships only Verbs that don't end in Dot P Y,
  so you showing up to add the first Dot P Y variation
    **hijacks Autocomplete to give you a separate Lab Notebook for each Verb**,
      an indexed Py File you can easily search out that comes to record
  your own Examples and Explanations, and
  your preferred Guesses of what you want for when you're not bothering to spell it out

## Placing Files into your Sh Path

How you place Files into your Sh Path can vary wildly

A quick test is

    git clone https://github.com/pelavarre/byoverbs.git
    cd byoverbs/bin/
    export PATH="${PATH:+$PATH:}$PWD"

My technique is

    mkdir -p ~/bin
    export PATH=$PATH:$HOME/bin

    git clone https://github.com/pelavarre/byoverbs.git
    cp -p byoverbs/bin/* ~/bin/.

## Inviting You to Fish, not Shoving Fish on You

Nearly all our Sh Scripts show you what they're doing as they do it,
  to help you learn how to do the same work without them

For example, our 'ls |n' will show you its '|cat -n -' and its '|expand'

Our most destructive scripts even show you what they will do and halt,
  waiting for your permission to proceed,
    such as our 'qcl' abbreviation of 'git clean -ffxdq'

Our one Sh Script that's hard to trace is our 'cls' Sh Script that clears all output,
  including whatever trace it makes of its one work, whoops

To trace that work, you have to look at the source, or capture its output

    cat bin/cls
    cls |hexdump -C

## Dirs of Dirs of Files

3 dirs of 30 files

> Makefile - define what 'make' means here

> README.md - this file

> bin/black - find and run the Black auto-styling app for Python
<br> bin/cls - clear the visible Rows and the Scrollback too
<br> bin/flake8 - find and run the Flake8 linting app for Python
<br> bin/n - take N to mean:  ... |cat -n |expand
<br> bin/p - take P to mean launch a new Python session
<br> bin/v - take V to mean launch a new Vim Session

> bin/byotools.py - competently welcome you into Sh Terminal work, batteries included
<br> bin/touch.py - mark a file as modified, or create a new empty file

> bin/q - short for Git Checkout with no argument (which is short for Git Status)
<br> bin/qa - short for Git Add
<br> bin/qcaa - short for Git Commit All Amend
<br> bin/qcl - short for Git Clean F F X D Q
<br> bin/qd - short for Git Diff
<br> bin/qdno - short for Git Diff Name-Only
<br> bin/ql - short for Git Log
<br> bin/ql1 - short for Git Log -1
<br> bin/qlf - short for Git Ls-Files
<br> bin/qlq - short for Git Log No-Decorate -10
<br> bin/qlv - short for Git Log Decorate -10
<br> bin/qs - short for Git Show
<br> bin/qsis - short for Git Status Ignored Short
<br> bin/qspno - short for Git Show Pretty Name-Only

> dotfiles/dot-hushlogin - empty the top of a new macOS Terminal window
<br> dotfiles/dot-zprofile - grow the Path, choose the first Pwd, and suggest Scp
<br> dotfiles/dot-zshrc - empty the Zsh Ps1, until you launch Zsh inside Zsh

> futures.txt - what i might should make next for us

## Motivations

Three thinkers lit this way for me

1 )
You should feel agency and power, when you work with your thing;
you should feel you can change it;
you should feel we've invited you to improve it
\~\~ Cristóbal Sciutto

2 )
When you like a thing that stopped working,
you can troubleshoot it in an expansive way
\~ D A Norman, via Cory Doctorow

3 )
We think with the objects we love; we love the objects we think with
\~ Sherry Turkle

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/README.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
