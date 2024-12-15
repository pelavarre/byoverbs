# Python ArgParse - As If People Mattered

## Abstract

why doesn't everybody here code Python CLI like this?

don't they have their own hot take on which Examples we need to surface first? which Notes should show up in the Help Lines? which Defaults work most smoothly with them at their own desk?

don't they agree that the First Impression we give with the Help Lines is the place with lots of leverage over the First Impression we give to people adopting the CLI they coded?

why don't i hear anyone but me talking like this?

## 1 Tell it to wear your look

my requirements for my Python CLI running above whatever are

a ) no args = show my examples

b ) “--” explicit no Sh Args = run my defaults

c ) “-h” = show my notes

d ) whatever else = pass it through with no change or muck with it if i feel like it

## 2 Write it with me

my requirements for Collaborating on a Python CLI we write to run above whatever are

i ) Git Track a copy of the 'parser.print_help' output

ii ) Start the main Source File with a copy of that output

iii ) Print the Diff and exit nonzero when the ArgParse ArgumentParser gets the 'parser.print_help' output wrong

## 3 Brief, clear, lightweight, simple, and small

to cover A B C D and then also I II III, i wrote the lightweight ArgumentParser you can see run as

    import byotools as byo

    parser = byo.ArgumentParser()

    ... call parser.add_argument etc in here if you want ...

    args = parser.parse_args()

    print(args)

## 4 How wrong-headed am i?

are my requirements brief and clear? how persuasive are they? do you feel i should drop or scale back one as unimportant?

## 5 How do we get this done well and quickly for cheap?

how would you recommend i come meet my requirements?

## Transition

bottom line same as top line =>

## Bottom Line Walkaway

why doesn't everybody here code Python CLI like this?

don't they have their own hot take on which Examples we need to surface first? which Notes should show up in the Help Lines? which Defaults work most smoothly with them at their own desk?

don't they agree that the First Impression we give with the Help Lines is the place with lots of leverage over the First Impression we give to people adopting the CLI they coded?

why don't i hear anyone but me talking like this?
