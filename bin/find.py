# find .  # isn't implied by 'find' without Sh Args at Mac
# find / -mount 2>/dev/null |grep ...

# find -size +1001k 2>/dev/null
# ls -hlAF -rt -rS $(find . -size +1001k 2>/dev/null)


# cd bin/ && find bin/find.py should work sometimes


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/find.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
