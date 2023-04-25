# byoverbs/futures.md

what i might should make next for us soon?

contents
+ Urgencies
+ Demos
+ Mobile Workflow
+ Notes
+ Python Workflow
+ Bash Verbs
+ + Grow Scope
+ + Pwnme
+ + Screen Bash
+ Py Verbs
+ + Cp Py
+ + Dd Py
+ + Emacs & Less & Vim Py
+ + Emacs Py
+ + Git Py
+ + Grep Py
+ + Head Py
+ + Less Py
+ + Ls Py
+ + Open Py
+ + Python Py
+ + Vim Py
+ + Whence Py
+ Read Me
+ Copied from

## Urgencies

bugs in their Code that i can't afford to fix, above nice-to-have features to add

## Demos

demos/buttonfiles/
demos/keycaps.py - add import msvcrt
demos/morse.py - take . - Space/Return as input to show all matches, then less matches
demos/rpn.py

test Paste at Windows
    does it all come through as single Keystrokes in the same millisecond?

list deffed by Py File and not mentioned by that same Py File

import the ByoTools, don't just copy-edit fragments?

## Mobile Workflow

G Cloud shopt -s histverify

## Notes

curl -i, --include Http Response Headers such as Date of Doc
diff -Bbw

## Python Workflow

lint - list deffed by Py File and not mentioned by that same Py File

Vim/Emacs cuts of a whole Def

## Bash Verbs

### Grow Scope

solve numeric v non-numeric args

    a /
    a 1
    qspno 1
    qspno HEAD~1

### Pwnme

also called by:  make pwnme
could more or less volunteer and authorize the destructive prep of:  qc

### Screen Bash

more test and comments

some bug near to

    $ screen.bash
    ++ screen -r 1 Socket in /run/screen/S-pelavarre
    There is no screen to be resumed matching 1.
    $ screen -ls
    There is a screen on:
            2615111.pts-0.ubuntu-pelavarre     (11/09/2022 06:18:56 PM)        (Detached)
    1 Socket in /run/screen/S-pelavarre.
    $ screen.bash 1


## Py Verbs

### Cp Py

kin to Mv Py
accept 0 or 1 args
cp -ipR with 'git config user.initials' and date-time last modified

### Dd Py

dd some large file, to keep it easy to raise free space quickly

### Emacs & Less & Vim Py

solve Bash C-x C-e first, editing inline in the way of Zsh
prompt with how to undo

pattern of search-replace that keeps lit the searches and the replaces
history of what was replaced, what was deleted
edit as bookmark, reached by Undo

### Emacs Py

syntax coloring without coloring trailing spaces past end-of-line

### Git Py

more abbreviation/ promotion of

    git log --no-decorate --pretty=format:'%h%x09%an%x09%cd%x20%x09%s' \
        --author=$(git config user.email) |grep May |grep '2021 -'

    git show :1:FILENAME # base
    git show :2:FILENAME # theirs
    git show :3:FILENAME # ours
    git reflog
    git reset HEAD~1
    git rm -f ...

wrong accident redefine Origin where? how about: git push origin HEAD:origin/feature/foo

### Grep Py

separate runs of hits in one bucket or another more elegantly than extremely ad hoc

    cv |g : |gv '0:00:0[0123]' |g http |column -t \
        |(sleep 0.1 && awk '''
            BEGIN{print ""}
            {o=d; h=0+substr($4, 1, 2); d=(h >= 6) && (h < 18)}
            (o != d){print ""}
            {print}
        ''' && echo)

### Head Py

Mac Tail & Linux Head/Tail
do Not resolve such contradictions as:  -1 -2

### Less Py

run a command piped in
default closer to -FIRX

### Ls Py

ls.py --full-time
but with --ext=.py to show the source

in sorting by version, the version is y.m.d when it's nothing else?

dreams of sharing Sh Terminal space more fairly

    diff -urp <(echo $LESSOPEN) <(echo '| /usr/bin/lesspipe %s')

### Open Py

print the last word by itself, such as 'ABC-12345' from http://jira/browse/ABC-12345
keep the session open till quit
strip trailing slash

### Python Py

give people

    rm -fr sandbox9/
    python3 -m venv --prompt SBOX9 sandbox9
    source sandbox9/bin/activate

### Vim Py

try loud insert mode that expires at arrows, when not fed, etc

solve evolving Vim vs

    :set listchars=tab:\\·,trail:·

solve Multi Buffer Vim, such as

    :nnoremap <space><space> :b <C-d>
    :nnoremap <BS> :b#<CR>
    :nnoremap <S-Tab> :bprevious<CR>
    :nnoremap <Tab> :bnext<CR>

### Whence Py

default to whence -a including Aliases & Funcs of Bash & Zsh

## Read Me

it's got an early index of source code in it, i might should catch that up

## Quickly Now

i gather notes here when they reach me, then later i spread them out above

+ the non-x Py at 'apt find git screen script ssh sudo' should go live
+ + as easily as already at:  bin/touch.py

+ mv.py should toggle itself off?
+ mv.py should stop freaking over trailing '/'
+ cp.py should work like mv.py

+ cal.py should give me 'cal && cal -m 1 2023' on 20/Dec
+ + but did give me 'cal && cal -m 12 2022'

+ mv.py should trace its calls of 'date +' and of 'ls -1rt'

+ tty stdin g should mean qo, else g -R $PWD

+ open.py of a thin decimal number should put that number into a recent web address
+ open.py session should stay open till Tty Eof, and log its work

+ give me a 'time.sleep' that invites me to quit it, like by pressing Return

+ 3 qp should work like qp && qp && qp

+ make remote 'cv' work - like push/pull 'scp.py --' from last Host found by Ssh

+ repeat 'mv.py --' to undo it, not to deepen it
+ loosen up 'ls.py' - look across last few days, and across top few of 'dir -p'

+ bin/md5sum vs bin/md5sum.bash

+ o=$OLDPWD  # for the sake of $o in command lines
+ compositional - o for run it in or on the $OLDPWD

+ cache requests get/post & subprocess run
+ dump & py grep & delete chosen sets of cache keys
+ grep cache keys by key or by value or by date/time stamp
+ grep.py for classic regex vs pygrep.py for py regex

+ keep more Terminal Windows in synch across input histories
+ stop losing timestamps on the first input lines of the morning

+ 'def unicode\_name' should find "EM" in place of "EOM"
+ eqgol qgiol qgol vqgol -> eol qoil vol, but only 'qoil' exists as yet
+ '|t 3' could mean '|tail -3'
+ 'dotfiles/bash\_profile'
+ screen for SyntaxErrors, and auto-repair needs 1 trailing ':' or a few '))'

## More

Git Commit Messages drafted, not pushed

    open.py: Auto-correct Paste Buffer if it's holding 1 over-precise Web Address

    ls.py: Ship usage: ls.py [-F]  # add '/' at 'd', '*' at 'x', '@' at '->', etc

    ls.py: Ship usage: ls.py [-R]  # walk deep down to show dirs in dirs

    .: Link the Tracked Files to Posted-Into/ Copied-From

    find.py: Ship usage: find.py [TOP ...]
    find.py: Ship usage: find.py [TOP ...] [-prune]

    echo.py: Ship usage: bash.py -c 'echo *.md' --py  # show how Sh calls Glob

Transcripts

    % cal.py --
    + cal
         March 2023
    Su Mo Tu We Th Fr Sa
              1  2  3  4
     5  6  7  8  9 10 11
    12 13 14 15 16 17 18
    19 20 21 22 23 24 25
    26 27 28 29 30 31

    no default trace of: cal -m 3
    and also its end-of-line spaces

Cal Py for 2022-10-19, 2022-11-07 looked wrong to me
    cal.py 2022-10-19  # should work, and offer min equivalent 'cal' lines
    cal.py 20221019  # should work, and offer min equivalent 'cal' lines

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/futures.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
