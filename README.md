# byoverbs
Competently welcome you into Sh Terminal work

Three moves =>

i ) Break you free to Bring-Your-Own (BYO) Verbs into Sh Terminal work, on the cheap

ii ) Invite you to copy-edit and fork what meets you here

ii ) Help you write enough and not too much Code as simple small Sh Scripts,
  so you can switch into Python to read, keep up, and write less simple Code

## Examples, Explanations, Guesses, Options, Args, and Code

Odds on your Sh Terminal has been inviting you to press Dot Tab Return,
  in place of just Return, as often as you type out the first Word of a Command Line

For example, when you drop both 'echo' and 'echo.py' into your Sh Path,
  then typing out E C H O and pressing Dot Tab will fill out the Dot P Y part for you

That obscure move of yours then gives you all the choices of what happens next

Our conventions here help you remember what you've learned of the Sh Verb involved

We give you your own **examples** first,
  but we'll give you your longer **explanations**
    if you type Space Dash Dash H before you press Return, and
  we jump up to flat **guess** what you want
    if you type out all of Space Dash Dash before you press Return

    echo.py  # show these examples and exit
    echo.py --h  # show help lines and exit (more reliable than -h)
    echo.py -- a 'b c'  # number and print these args

You pressing Space Dash Dash Return authorizes the guess,
  and then this guess of what you meant come out astonishingly correct,
  merely because you chose it, you put this guess exactly here,
  you planted this Easter Egg to come work with you as needed

The Sh and Python and Linux conventions spell out how you type these Dot P Y Dash Dash H marks,
  but don't so very much nail down what they mean - technically speaking,
  pressing Return means no argument,
  the Space Dash Dash H Return is short
    for a '--help' option calling for help lines, and
  the Space Double Dash Return is a way for you to type more than you must type
    just to more explicitly say you chose no argument

You choosing to type more than you know you must is a convenient address to plant an Easter Egg at

Over time, your process of having written out your own Examples and Explanations
  will build a feel in you for what you want the guesses of what you mean to be

Your mere choice to work with
  your own Notes of Examples and Explanations - your own Lab Notebook -
will give you the feel
  for what missing **Options** and **Args** you can bring in to work with you,
by changing and growing the **Code** in the Py File

Linux mostly ships only Sh Verbs that don't end in Dot P Y, don't end in Dot Anything,
  so you showing up to add the first Dot P Y variation
    **hijacks Autocomplete to give you a separate Lab Notebook for each Sh Verb**,
      an indexed Py File you can easily search out that comes to record
  your own Examples and Explanations, and
  your preferred Guesses of what you want for when you're not bothering to spell it out

## Placing Files into your Sh Path

How you drop Files into your Sh Path can vary wildly

A quick test is to drop a copy of our Files onto the back of your Sh Path,
  where they're more mostly harmless,
  because out there they don't redefine any Sh Verb you already have installed

    git clone https://github.com/pelavarre/byoverbs.git
    cd byoverbs/bin/
    export PATH="${PATH:+$PATH:}$PWD"

Me, I reconfigure my Sh to do this for me always

    mkdir -p ~/bin
    export PATH=$PATH:$HOME/bin

    git clone https://github.com/pelavarre/byoverbs.git
    cp -p byoverbs/bin/* ~/bin/.

## Inviting You to Fish, not Shoving Fish on You

Nearly all our Sh Scripts show you what they're doing as they do it,
  to help you learn how to do the same work without them

For example, our 'n' Script
  inside 'ls |n' will show you its '|cat -n -' and its '|expand'

Our most destructive scripts go so far as to halt after showing you what they will do,
  waiting for your authorization to proceed,
    such as our 'qcl' abbreviation of 'git clean -ffxdq'

Our one Sh Script that's hard to trace is our 'cls' Sh Script that clears all output,
  including whatever trace it makes of its one work, whoops

To trace that work, you have to look at the source, or capture its output

    cat bin/cls
    cls |hexdump -C

## Dirs of Dirs of Files

5 Dirs of Dirs of 14 Files, and then also the 94 Files in our Bin Dir

> Makefile - define what 'make' means here
<br> README.md - this file
<br> futures.md - what i might should make next for us

> bin/ - 94 Sh Verbs you could add
<br> demos/ - mostly Games to invite people into G Cloud Linux Sh Terminals
<br> dotfiles/ - 6 ways i configure my Terminal Sh
<br> pwnme/ - compress the instructions for download & trust & run the Demos

### 3 Files in our Demos Dir

> keycaps.py - bring your own Text User Interface (TUI) onto Python 3 with no Pip Installs
<br> maskup.py - generate Loren Ipsum placeholder text from your input
<br> tictactoe.py - make a clay out of a Tic-Tac-Toe game board

### 6 Files in our DotFiles Dir

> dotfiles/dot.emacs
<br> dotfiles/dot.gitconfig
<br> dotfiles/dot.hushlogin - empty the top of a new macOS Terminal window
<br> dotfiles/dot.vimrc
<br> dotfiles/dot.zprofile - grow the Path, choose the first Pwd, and suggest Scp
<br> dotfiles/dot.zshrc - empty the Zsh Ps1, until you launch Zsh inside Zsh

### 1 File in our PwnMe Dir

> tictactoe.bash

### 22 Files in Bin Dir, mostly to abbreviate Sh Pipes

18 of these exist to fit well into Sh Pipes, the other 4 are our E P V session launchers and our Q from Git

> bin/a
<br> bin/c
<br> bin/cv
<br> bin/d
<br> bin/e - take E to mean launch a new Emacs Session
<br> bin/f
<br> bin/g
<br> bin/gi
<br> bin/giv
<br> bin/gv
<br> bin/h
<br> bin/mo
<br> bin/n
<br> bin/p - take P to mean launch a new Python session
<br> bin/q - Q for Git since G is Grep, but it's discussed separately, far far below
<br> bin/s
<br> bin/t
<br> bin/u
<br> bin/v - take V to mean launch a new Vim Session
<br> bin/x
<br> bin/xd
<br> bin/xn1

### 9 Sh Verbs in Bin Dir

> bin/:h - max horizontal width of Sh Terminal
<br> bin/:v - max vertical height of Sh Terminal
<br> bin/black - find and run the Black auto-styling app for Python
<br> bin/cls - clear the visible Screen Rows and the Scrollback too
<br> bin/flake8 - find and run the Flake8 linting app for Python
<br> bin/md5sum - patch Linux 'md5sum' idea into macOS
<br> bin/pwnme - download & trust & update from GitHub to LocalHost ByoVerbs
<br> bin/tac - patch Linux 'tac' idea into macOS
<br> bin/whence - patch Zsh 'whence' idea into Bash

> bin/byotools.py - competently welcome you into Sh Terminal work, batteries included
<br> bin/touch.py - mark a file as modified, or create a new empty file

### 9 Py Scripts in Bin Dir

our Examples, Notes, and Guesses compiled into Sh Dot Tab Return as Dot P Y

this is the Big Idea here, but i haven't yet explored it much here,
  my other various abandoned GitHUb Repos are where i explored it lots more,
    before figuring out how to say it well here

> bin/apt.py
<br> bin/byotools.py
<br> bin/echo.py
<br> bin/git.py
<br> bin/ls.py
<br> bin/mv.py
<br> bin/sed.py
<br> bin/sw_vers.py
<br> bin/touch.py

### 4 Sh Scripts in Bin Dir

> bin/python3.bash
<br> bin/screen.bash
<br> bin/shellcheck.bash
<br> bin/tac.bash

### 5 Sh Source Scripts in Bin Dir

> bin/zprofile - abbreviations that need the privileges of being 'source'd into Sh
<br> bin/bh.source
<br> bin/zh.source
<br> bin/qp.source
<br> bin/qcd.source

### 42 Abbreviations of Git Sh Lines in Bin Dir

7 related files, but see also 'bin/zprofile', 'bin/qp.source', 'bin/qcd.source'

> bin/eqgl
<br> bin/eqno
<br> bin/vqgl
<br> bin/vqno

42 abbreviations

> bin/q - short for Git Checkout with no argument (which is short for Git Status)
<br> bin/qa - short for Git Add
<br> bin/qb
<br> bin/qb0
<br> bin/qc
<br> bin/qca
<br> bin/qcaa - short for Git Commit All Amend
<br> bin/qcaf
<br> bin/qcam
<br> bin/qcf
<br> bin/qcl - short for Git Clean F F X D Q
<br> bin/qco
<br> bin/qcp
<br> bin/qd - short for Git Diff
<br> bin/qdh
<br> bin/qdno - short for Git Diff Name-Only
<br> bin/qfcorb
<br> bin/qg
<br> bin/qgi
<br> bin/qgil
<br> bin/qgl
<br> bin/ql - short for Git Log
<br> bin/ql1 - short for Git Log -1
<br> bin/qlf - short for Git Ls-Files
<br> bin/qlq - short for Git Log No-Decorate -10
<br> bin/qls
<br> bin/qlv - short for Git Log Decorate -10
<br> bin/qno
<br> bin/qo
<br> bin/qof
<br> bin/qoi
<br> bin/qoil
<br> bin/qol
<br> bin/qpfwl
<br> bin/qrh
<br> bin/qrh1
<br> bin/qri
<br> bin/qrv
<br> bin/qs - short for Git Show
<br> bin/qsis - short for Git Status Ignored Short
<br> bin/qsp
<br> bin/qspno - short for Git Show Pretty Name-Only

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
