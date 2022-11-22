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

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/futures.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
