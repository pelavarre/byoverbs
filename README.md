<!-- omit in toc -->
# byoverbs

Contents

- [Welcome](#welcome)
- [Cook up your own Logo Turtles](#cook-up-your-own-logo-turtles)
- [Roll your own Emacs, Less, Sh Screen, Ssh, Vi](#roll-your-own-emacs-less-sh-screen-ssh-vi)
- [Roll your own Sh Pipes](#roll-your-own-sh-pipes)
- [Roll your own Sh Verbs](#roll-your-own-sh-verbs)
- [Smooth out your own Git Command-Line-Interface (CLI)](#smooth-out-your-own-git-command-line-interface-cli)
- [Write your own Cheat Sheets](#write-your-own-cheat-sheets)
- [Write your own Dot Files](#write-your-own-dot-files)
- [Write your own Notes](#write-your-own-notes)
- [Help us please](#help-us-please)

<!-- I'd fear people need the headings numbered, if it were just me -->
<!-- VsCode autogenerates this Table-of-Contents. Maybe people will cope -->

## Welcome

This Repo is my pile of **actions your computer should make easy for you**

I work for fun and for hire on "Direct Manipulation & Live Programming projects".
My thanks to Omar Rizwan for the phrase.

My first puzzle here is how to stop losing new insights.
What works for me is that first, I chat with you a bit here, calmly, up front.
But by the day, I stream insights in real-time into Futures·Md, as they bubble up out of my brain.
Solutions I more drop into Scraps·Txt.
The Code comes to me first, the English Words to speak of it come much later.
Day shift, I work on a MacBook, mostly in Sh Terminals, mostly Ssh'ed into Linuxes,
with my huge Bin Folder of 200+ extra Sh Verbs, added to the far end of my Sh Path.
This File is the ReadMe·Md of the Bring-Your-Own Verbs (BYO Verbs) Git Repository at GitHub.

I love the words people speak well of dreams like mine

+ I'm always looking to fill in my knowledge gaps of the things already up helping me work.
I'm often not really looking to learn from scratch
~~ Julia Evans (@/b0rk)

+ You should feel agency and power, when you work with your thing.
You should feel you can change it.
You should feel we've invited you to improve it
~~ Cristóbal Sciutto (@/tobyshooters)

+ We love the things we think with
~~ Sherry Turkle (@/sturkle)

Scroll on down now to glance over my ongoing Projects at Home
<!-- Click through to see more -->

**Footnotes**<br>
ByoVerbs > [Bin Folder](bin)<br>
ByoVerbs > [Demos Folder](demos)<br>
ByoVerbs > [DotFiles Folder](dotfiles)<br>
ByoVerbs > [Futures·Md File](futures.md)<br>
ByoVerbs > [ReadMe·Md File](readme.md)<br>
ByoVerbs > [Scraps·Txt File](scraps.txt)<br>
Twitter > [Omar Rizwan 2024-Dec-12](https://twitter.com/rsnous/status/1867221875543162944)<br>

## Cook up your own Logo Turtles

A Logo Turtle is a Sh Terminal Cursor, but with a Heading that isn't always only 90° East on a flat plane

Let's solve Python "Batteries Included" for Logo Turtles
+ Run reasonably well in an ordinary Terminal built into macOS. Don't force people to add on Graphics Software
+ Let my people type Commands without Arguments. Don't force people to learn Punctuation early
+ Let my people choose their own Default Arguments. Don't force people to like our Choices

**Footnotes**<br>
Wikipedia > [Batteries Included](https://en.wikipedia.org/wiki/Batteries_Included)<br>
Wikipedia > [Logo Programming Language](https://en.wikipedia.org/wiki/Logo_(programming_language))<br>
Wikipedia > [Turtle Graphics](https://en.wikipedia.org/wiki/Turtle_graphics)<br>


## Roll your own Emacs, Less, Sh Screen, Ssh, Vi

Until you roll your own,
your Keyboard-to-Screen latencies run ridiculously high (10X?),
and your features fall short of modern VsCode,
such as select Blank Space to see it is encoded as Space or Tab and so on

But to roll your own, you need a Terminal Driver.
Well, I've got that here, built for macOS & Linux,
built out from what I remember of 1989,
built on top of Import of "select, signal, termios, tty"

I have kept the Terminal Driver running,
for the Logo Turtles call on it to paint Pixels on Screen.
But presently I don't have the Emacs, Less, Sh Screen, Ssh, and Vi
running above the Terminal Driver

Back at some old Git Hashes,
I can show us delightfully low Less latencies.
I can show us Key Maps for Emacs/ Less/ Vi too.
I can also show us "import pty" mostly does the work of Sh Screen and Ssh,
but there's an unsolved bug in Term Cap negotiations
that rudely cuts back Vi's default choice of Color Palette to like 8 Colors

I've borrowed Windows machines from friends often enough to believe
we could solve Windows on top of a base of Windows "import mscvrt".
But I have no free-of-charge way to test Windows frequently, until you give me one

## Roll your own Sh Pipes

I build my Sh Pipes out of single Letters

+ |a is for Awk
+ |c is for Cat
+ |d is for Diff
+ |e is for Emacs
+ |f is for Find
+ |g is for Grep
+ |h is for Head
+ |n is for |cat -n |expand
+ |p is for Python, but doesn't make me type out "import" statements
+ |q is for Git, because G was taken
+ |s is for Sort
+ |t is for Tail
+ |u is for Uniq
+ |uu is for the kind of Uniq that doesn't first sort the Data
+ |v is for Vi
+ |x is for XArgs

Those are the Sh Pipe Filters that I write most often,
but I practically always only call on them to run composed together with other Sh Verbs

Like it should be easy for you to look back over your own Sh Input Line History,
and drop the Duplicates,
but keep the Last Duplicate, not the First Duplicate

It is easy for me

I build the key fragment of that Sh Pipe out of more than one Letter each

    |tac |uu |tac |


## Roll your own Sh Verbs

Now and again I work on replacing the Sh Verbs with fresh Python
that you could edit to suit you

Maybe the only piece of that I really still have going now is my "cal.py".
I practically never want to look at only 1 Month.
I'm most commonly looking like back 14 Days or ahead 14 Days.
Pretty often I want to see 3 Months.
I've tuned the defaults so I more get what I want,
without me first having to remember the intricate Syntax
that they invented long ago to let you call for a huge pile of things I practically never do want


## Smooth out your own Git Command-Line-Interface (CLI)

My ~70 Git Command Aliases show up as "bin/q*"

I'd push them into a ~/.gitconfig File,
except I don't know how to make that kind of Git Alias
show you in real time on screen at Stderr what you're doing

My Git Aliases spell out for me and for you watching over my shoulder the tricks I've found

    cat - && git clean -dffxq  # destroys the Files not yet git-add'ed
    cat - && git reset --hard @{upstream}  # buries Commits in the Git Reflog, loses the rest
    git show --pretty= --name-only  # so very often all you need to know

And so on


## Write your own Cheat Sheets

It might be that no one can write a Cheat Sheet that's much help to anyone else.
The Cheat Sheet is a record of how you put Syntax into your Brain.
Maybe that's different than how everyone else puts Syntax into their Brains.
Or maybe it's the same.
Let's find out

I'm working on Cheat Sheets for Emacs, Git, Less, Make, Sh itself, Sh Screen, Ssh, & Vi

Let's talk


## Write your own Dot Files

It might be that no one can write a Dot File that's much help to anyone else.
The Dot File is a record of which Configuration Settings you flipped out of Default.
Maybe that's different than what choices everyone else makes.
Or maybe it's the same.
Let's find out

I'm working on Dot Files for Bash, Emacs, Git, HushLogin, Vi, & Zsh

Let's talk


## Write your own Notes

What I want from a Man Page are my examples and my notes of how to run your program

Like say you write some Program and you name it Alfa and you set up "man alfa" or "alfa --help" to give me a copy of your Man Page.
Yea.
That does me almost no good

What does me good is for me to write an "alfa.py" that gives me my examples.
And my "alfa.py --" gives me the most usual way I call you,
though sometimes I spell that out more explicity as "alfa.py --yolo".
And my "alfa.py --help" gives me my notes

My 75+ "bin/*.py" Files are examples, often woefully incomplete.
One of the better examples is my "bin/python3.py".
It reminds me how to spell the more forgettable Python Easter Eggs

    python3 -i -c ''
    python3 -c 'import this' |tail +3 |cat -n |expand

And my "bin/python3.py" also reminds me
when the different 3.2.1 "Major-Minor-Micro" Version Numbers reached me,
like so I can know how old some of your Python Code is,
when measured by a merely standard Calendar


## Help us please

You know you've got thoughts.
Please do speak out

+ LinkedIn > [pelavarre](https://www.linkedin.com/in/pelavarre)<br>
+ Mastodon > [pelavarre](https://social.vivaldi.net/@pelavarre)<br>
+ Twitter > [pelavarre](https://twitter.com/intent/tweet?text=/@PELaVarre)<br>


<!-- omit in toc -->
## Copied from

Posted as:  https://github.com/pelavarre/byoverbs/blob/main/README.md<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git<br>
