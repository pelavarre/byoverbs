# bugs/DotTabReturn.md

Dot Tab Return starts looking up your notes on Sh Verbs for you,
when you add the Folder ~/Public/byoverbs/bin/ into your Sh Path

    export PATH=$PATH:$HOME/Public/byoverbs/bin

It finds your notes, your examples, your preferences,
whatever you put in the Py File to remind you of your friendship with the Sh Verb

## Try it

Like if you type out the 5 Chars 'which' and then press Dot and then press Tab,
then Sh will spell out for you all of

    which.py

Press Return, and it will list out for you the half-a-dozen places
where we go to hide the definitions of your Sh Verbs,
as examples of searching for the definitions of your Sh Verbs

## You know what I mean

Sh by design is glitchy

1 If you have Spaces in your Sh Path or Sh Home,
then instead you must say

    export PATH="$PATH:$HOME/Public/byoverbs/bin"

2 If you didn't already have a Sh Path set,
and you don't want the "" Empty Path that means "$PWD" added into your Sh Path,
then you must say one of:

    export PATH="$HOME/Public/byoverbs/bin"

    export PATH="${PATH:+$PATH:}$HOME/Public/byoverbs/bin"

3 If the Sh Verb you're looking up also already exists as a Python Module,
then you'll see two Dots in place of 1

    pwd..py
    time..py

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/bugs/DotTabReturn.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
