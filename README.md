# byoverbs

## Show, not tell

Try it, you'll like it

    mkdir ~/Public/
    cd ~/Public/

    rm -fr byoverbs/
    git clone https://github.com/pelavarre/byoverbs.git

    export PATH="${PATH:+$PATH:}$HOME/Public/byoverbs/bin"

Please give us words to help more people start to get it?

    open https://twitter.com/intent/tweet?text=.@PELaVarre

## One example

Your happy experiences will include . . .

Choose well with no args

    $ lsa
    + ls -AhlF -rt
    total 0
    drwxr-xr-x  12 jqdoe  staff   384B Oct  4 08:31 byoverbs/
    $

Choose well with 1 arg

    $ lsa *
    + ls -AhlF -rt byoverbs
    total 56
    -rw-r--r--    1 jqdoe  staff   3.7K Oct  4 08:31 Makefile
    -rw-r--r--    1 jqdoe  staff   9.9K Oct  4 08:31 README.md
    drwxr-xr-x  172 jqdoe  staff   5.4K Oct  4 08:31 bin/
    drwxr-xr-x    7 jqdoe  staff   224B Oct  4 08:31 bugs/
    drwxr-xr-x   26 jqdoe  staff   832B Oct  4 08:31 demos/
    drwxr-xr-x    5 jqdoe  staff   160B Oct  4 08:31 docs/
    drwxr-xr-x   10 jqdoe  staff   320B Oct  4 08:31 dotfiles/
    -rw-r--r--    1 jqdoe  staff   9.6K Oct  4 08:31 futures.md
    drwxr-xr-x    3 jqdoe  staff    96B Oct  4 08:31 pwnme/
    drwxr-xr-x   12 jqdoe  staff   384B Oct  4 08:31 .git/
    $

Choose well with 2 args

    $ lsa byoverbs/bugs/ byoverbs/docs/
    + ls -AdhlF -rt ...
    drwxr-xr-x  7 jqdoe  staff   224B Oct  4 08:31 byoverbs/bugs//
    drwxr-xr-x  5 jqdoe  staff   160B Oct  4 08:31 byoverbs/docs//
    $

## Another example

Bring your examples back on Screen, before your notes at `--h` and your defaults at `--`

    $ ls.py


    ls.py -- |cat -  # runs the Code for:  ls -1
    ls.py --py |cat -  # shows the Code for:  ls -1

    ls.py -al  # runs the Code for:  ls -al

    ls.py -1 --py >p.py  # name the Code
    python3 p.py  # run thmake named Code
    cat p.py |cat -n |expand  # show the numbered Sourcelines of the named Code

    python3 -c "$(ls.py -1 --py)"  # runs the Code as shown

    find ./* -prune  # like 'ls', but with different corruption of File and Dir Names
    ls -1rt |tail -1  # the File or Dir most recently touched, if any

    $

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/README.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
