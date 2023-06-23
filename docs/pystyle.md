# docs/pystyle.md

The Python Code you write comes across more clearly
when you can keep it brief and to-the-point

Tell us how we can do better here?
Tell us if our example inspires you to work in new ways yourself?

## Say what's going on, out loud in words

You'll see some consistency in the style of Python pushed here

You'll get more consistency if we publish our rules for ourselves,
and then we'll both come out happier

## Let Black & Flake8 & Flake8-Import-Order do what work they can for us

Mostly I accept the Py Style kept up by the work of PyPi Black & PyPi Flake8

I do hate the 2023 new thing
of ripping out the blank Sourcelines that follow a ":" Colon

## Avoid abbreviating or corrupting the words we hold in common

PEP 8 correctly tells us
"If a function argument’s name clashes with a reserved keyword,
it is generally better to append a single trailing underscore
rather than use an abbreviation or spelling corruption.
Thus class_ is better than clss.
Perhaps better is to avoid such clashes by using a synonym.)"

## Avoid abbreviating words of less than 8 Letters

I worked somewhere once that made a point of
"Avoid abbreviating words of less than 8 Letters"

I like that rule, for shoving Writers of Code
to stop demanding that Readers of Code learn so very many new Words

## Short Names

If you've got a meaningful Name for a thing, then you speak it, life is good

But for the rest of the time, naming the thing after its data type can keep you moving

bytes_: Bytes<br>
ch: Str of Len 1, not 0, not more<br>
i, j, k: Index | Int<br>
chars: Str with or without trailing Line-End<br>
line: Str with or without trailing Line-End, when spoken of as 1 Line of 0..N Lines<br>
lines: [Line]<br>
pairs: Dict Items<br>
sep: Str working as a Separator<br>
text: Str without trailing Line-End<br>
vxk: Dict, in the sense of Value-by-Key<br>
words: [Str], when each Str contains no Sep<br>

{v}\_by\_{k}:  Dict[k,v]<br>
{v}_list: [v] in the cases when {v}s doesn't work as a Name<br>
{v}_set: Set[v]<br>

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/docs/pystyle.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
