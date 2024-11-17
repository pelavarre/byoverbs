# xargs

#
# % echo a  b c |xargs -n 1
# a
# b
# c
# %
# % echo "'singly-quoted yah'" |xargs -n 1
# singly-quoted yah
# %
# % echo '"doubly-quoted ooh"' |xargs -n 1
# doubly-quoted ooh
# %
#
# % echo "'singly-quoted" |xargs -n 1
# xargs: unterminated quote
# %
#
# % echo '"doubly-quoted' |xargs -n 1
# xargs: unterminated quote
# %
#


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/xargs.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
